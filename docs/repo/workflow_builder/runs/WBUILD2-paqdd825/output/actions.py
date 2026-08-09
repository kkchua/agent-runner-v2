"""Custom actions for video_campaign_manuscript -- Composition System.

Provides three domain-specific action implementations:
- scan_components: Discover and parse component markdown files from a
  component library directory, producing a structured inventory.
- validate_components: Validate each discovered component against the
  component schema rules, producing a detailed validation report.
- plan_compositions: Parse composition files, resolve component references,
  validate overrides, inventory placeholders, and produce a resolution plan.

The stepCompletion and promote_workflow_package actions are reused from
the core framework and are NOT duplicated here.
"""
from __future__ import annotations

import logging
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_COMPONENT_TYPES = frozenset({
    "hook", "scene", "voice_style", "visual_direction",
    "audio_mood", "text_style", "transition",
})

# Common properties every component must have
COMMON_REQUIRED_PROPERTIES = frozenset({
    "component_id", "component_type", "name", "version", "description",
})

COMMON_OPTIONAL_PROPERTIES = frozenset({
    "duration_range", "platforms", "tags",
})

# Type-specific required properties per component type
TYPE_SPECIFIC_REQUIRED: dict[str, frozenset[str]] = {
    "hook": frozenset({"hook_style", "hook_script", "visual_cue", "energy_level"}),
    "scene": frozenset({"scene_purpose", "scene_script", "visual_direction", "duration_target"}),
    "voice_style": frozenset({"voice_tone", "pace"}),
    "visual_direction": frozenset({"visual_style", "color_palette", "lighting_mood"}),
    "audio_mood": frozenset({"mood", "tempo"}),
    "text_style": frozenset({"text_treatment", "font_style", "text_animation", "text_color_scheme"}),
    "transition": frozenset({"transition_type", "transition_duration", "transition_energy"}),
}

# Enum value sets per property
ENUM_VALUES: dict[str, frozenset[str]] = {
    "hook_style": frozenset({
        "dramatic_reveal", "question_hook", "statistic_hook",
        "visual_reveal", "challenge_hook",
    }),
    "energy_level": frozenset({"low", "medium", "high"}),
    "scene_purpose": frozenset({
        "problem_setup", "solution_demo", "social_proof",
        "call_to_action", "product_intro", "education", "emotional_appeal",
    }),
    "voice_tone": frozenset({
        "authoritative", "conversational", "enthusiastic",
        "empathetic", "dramatic",
    }),
    "pace": frozenset({"slow", "moderate", "fast", "varied"}),
    "visual_style": frozenset({
        "cinematic", "documentary", "lifestyle", "motion_graphics", "mixed",
    }),
    "lighting_mood": frozenset({"bright", "dramatic", "natural", "neon", "warm"}),
    "aspect_ratio": frozenset({"16:9", "9:16", "1:1", "4:5"}),
    "mood": frozenset({"energetic", "calm", "tense", "uplifting", "mysterious"}),
    "tempo": frozenset({"slow", "moderate", "fast"}),
    "text_treatment": frozenset({
        "kinetic_typography", "lower_thirds", "full_screen", "overlay", "subtitles",
    }),
    "text_animation": frozenset({
        "fade_in", "slide_in", "bounce", "typewriter", "pop", "none",
    }),
    "transition_type": frozenset({
        "cut", "dissolve", "wipe", "zoom", "glitch", "match_cut",
    }),
    "transition_energy": frozenset({"low", "medium", "high"}),
}

# Binding slot to expected component_type mapping
BINDING_TYPE_MAP: dict[str, str] = {
    "opening_hook": "hook",
    "voice_style": "voice_style",
    "visual_direction": "visual_direction",
    "audio_mood": "audio_mood",
    "text_style": "text_style",
    "scenes": "scene",
    "transitions": "transition",
}

# Singleton vs ordered list binding modes
SINGLETON_BINDINGS = frozenset({
    "opening_hook", "voice_style", "visual_direction", "audio_mood", "text_style",
})
ORDERED_LIST_BINDINGS = frozenset({"scenes", "transitions"})

# Required vs optional bindings
REQUIRED_BINDINGS = frozenset({
    "opening_hook", "voice_style", "visual_direction", "scenes",
})
OPTIONAL_BINDINGS = frozenset({"audio_mood", "text_style", "transitions"})

# Placeholder pattern: {placeholder_name}
PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

COMPONENT_ID_RE = re.compile(r"^[a-z]+-[a-z][a-z0-9-]*-\d{3}$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_yaml_frontmatter(text: str) -> dict[str, Any] | None:
    """Extract and parse YAML frontmatter from a markdown file.

    Returns the parsed dict, or None if no valid frontmatter found.
    """
    stripped = text.strip()
    if not stripped.startswith("---"):
        return None
    # Find the closing --- delimiter
    end_idx = stripped.find("---", 3)
    if end_idx == -1:
        return None
    yaml_block = stripped[3:end_idx].strip()
    try:
        data = yaml.safe_load(yaml_block)
        if isinstance(data, dict):
            return data
    except yaml.YAMLError:
        return None
    return None


def _find_placeholders(value: Any) -> list[str]:
    """Extract all placeholder names from a value (recursively)."""
    placeholders: list[str] = []
    if isinstance(value, str):
        placeholders.extend(PLACEHOLDER_RE.findall(value))
    elif isinstance(value, dict):
        for v in value.values():
            placeholders.extend(_find_placeholders(v))
    elif isinstance(value, list):
        for item in value:
            placeholders.extend(_find_placeholders(item))
    return placeholders


def _now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Action: scan_components
# ---------------------------------------------------------------------------

@action("scan_components")
def scan_components(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: Path,
) -> ActionResult:
    """Discover component markdown files and build a structured inventory.

    Walks COMPONENT_LIBRARY_DIR for .md files, parses YAML frontmatter,
    extracts component properties, classifies by component_type, and writes
    a structured inventory to COMPONENT_INVENTORY_FILE.
    """
    project_root = Path(project_root)
    artifacts = state.get("artifacts", {})

    library_dir_str = artifacts.get("COMPONENT_LIBRARY_DIR", "")
    inventory_path_str = artifacts.get("COMPONENT_INVENTORY_FILE", "")

    if not library_dir_str:
        return ActionResult(
            status="REJECTED",
            remark="COMPONENT_LIBRARY_DIR artifact not found in state.",
            artifacts={},
            reject_code="MISSING_LIBRARY_DIR",
        )

    library_dir = Path(library_dir_str)
    if not library_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"COMPONENT_LIBRARY_DIR does not exist or is not a directory: {library_dir}",
            artifacts={},
            reject_code="EMPTY_COMPONENT_LIBRARY",
        )

    # Discover all .md files recursively
    md_files = sorted(library_dir.rglob("*.md"))
    if not md_files:
        return ActionResult(
            status="REJECTED",
            remark=f"No .md files found in {library_dir}",
            artifacts={},
            reject_code="NO_COMPONENTS_FOUND",
        )

    # Parse each file
    components: list[dict[str, Any]] = []
    type_counts: dict[str, int] = {}
    parse_errors: list[dict[str, str]] = []

    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception as exc:
            parse_errors.append({
                "file": str(md_file),
                "error": f"Read error: {exc}",
            })
            components.append({
                "file_path": str(md_file),
                "validation_status": "invalid",
                "error": f"Could not read file: {exc}",
            })
            continue

        frontmatter = _parse_yaml_frontmatter(text)
        if frontmatter is None:
            parse_errors.append({
                "file": str(md_file),
                "error": "No valid YAML frontmatter found",
            })
            components.append({
                "file_path": str(md_file),
                "validation_status": "invalid",
                "error": "No valid YAML frontmatter",
            })
            continue

        component_id = frontmatter.get("component_id", "")
        if not component_id:
            parse_errors.append({
                "file": str(md_file),
                "error": "Missing component_id in frontmatter",
            })
            components.append({
                "file_path": str(md_file),
                "validation_status": "invalid",
                "error": "Missing component_id",
            })
            continue

        # Build component entry
        entry: dict[str, Any] = {
            "component_id": component_id,
            "component_type": frontmatter.get("component_type", ""),
            "name": frontmatter.get("name", ""),
            "version": frontmatter.get("version", ""),
            "description": frontmatter.get("description", ""),
            "duration_range": frontmatter.get("duration_range", ""),
            "platforms": frontmatter.get("platforms", []),
            "tags": frontmatter.get("tags", []),
            "file_path": str(md_file),
            "validation_status": "pending",
        }

        # Copy type-specific properties
        comp_type = frontmatter.get("component_type", "")
        if comp_type in TYPE_SPECIFIC_REQUIRED:
            for prop in TYPE_SPECIFIC_REQUIRED[comp_type]:
                entry[prop] = frontmatter.get(prop, "")

        # Also copy any optional type-specific properties present
        for key, value in frontmatter.items():
            if key not in entry and key not in COMMON_REQUIRED_PROPERTIES and key not in COMMON_OPTIONAL_PROPERTIES:
                entry[key] = value

        components.append(entry)

        # Count by type
        if comp_type:
            type_counts[comp_type] = type_counts.get(comp_type, 0) + 1

    if not inventory_path_str:
        return ActionResult(
            status="REJECTED",
            remark="COMPONENT_INVENTORY_FILE artifact path not found in state.",
            artifacts={},
            reject_code="MISSING_OUTPUT_PATH",
        )

    inventory_path = Path(inventory_path_str)
    inventory_path.parent.mkdir(parents=True, exist_ok=True)

    inventory = {
        "scan_timestamp": _now_iso(),
        "source_directory": str(library_dir),
        "total_files_scanned": len(md_files),
        "total_components_discovered": len(components),
        "components_by_type": type_counts,
        "parse_errors": parse_errors,
        "components": components,
    }

    inventory_path.write_text(
        yaml.dump(inventory, default_flow_style=False, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )

    valid_count = sum(1 for c in components if c.get("validation_status") == "pending")
    invalid_count = sum(1 for c in components if c.get("validation_status") == "invalid")

    remark = (
        f"Scanned {len(md_files)} files. "
        f"Discovered {len(components)} components "
        f"({valid_count} parseable, {invalid_count} invalid). "
        f"Type distribution: {type_counts}"
    )
    logger.info("[scan_components] %s", remark)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"COMPONENT_INVENTORY_FILE": str(inventory_path)},
    )


# ---------------------------------------------------------------------------
# Action: validate_components
# ---------------------------------------------------------------------------

@action("validate_components")
def validate_components(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: Path,
) -> ActionResult:
    """Validate each component in the inventory against schema rules.

    Checks common property presence, type enumeration conformance,
    type-specific property conformance, enum values, unique IDs,
    semantic version format, and cross-property rules. Writes a
    detailed report to VALIDATION_REPORT_FILE.
    """
    project_root = Path(project_root)
    artifacts = state.get("artifacts", {})

    inventory_path_str = artifacts.get("COMPONENT_INVENTORY_FILE", "")
    report_path_str = artifacts.get("VALIDATION_REPORT_FILE", "")

    if not inventory_path_str:
        return ActionResult(
            status="REJECTED",
            remark="COMPONENT_INVENTORY_FILE artifact not found in state.",
            artifacts={},
            reject_code="NO_INVENTORY",
        )

    inventory_path = Path(inventory_path_str)
    if not inventory_path.is_file():
        return ActionResult(
            status="REJECTED",
            remark=f"Component inventory file not found: {inventory_path}",
            artifacts={},
            reject_code="NO_INVENTORY",
        )

    try:
        inventory = yaml.safe_load(inventory_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to parse inventory YAML: {exc}",
            artifacts={},
            reject_code="INVALID_INVENTORY",
        )

    if not inventory or not isinstance(inventory, dict):
        return ActionResult(
            status="REJECTED",
            remark="Component inventory is empty or not a valid YAML mapping.",
            artifacts={},
            reject_code="NO_INVENTORY",
        )

    components = inventory.get("components", [])
    if not components:
        return ActionResult(
            status="REJECTED",
            remark="Component inventory contains no components.",
            artifacts={},
            reject_code="NO_INVENTORY",
        )

    # Validate each component
    validation_results: list[dict[str, Any]] = []
    seen_ids: dict[str, int] = {}
    total_valid = 0
    total_invalid = 0

    for comp in components:
        comp_id = comp.get("component_id", "(unknown)")
        errors: list[dict[str, str]] = []
        warnings: list[dict[str, str]] = []

        # Skip already-invalid components (parse failures)
        if comp.get("validation_status") == "invalid":
            validation_results.append({
                "component_id": comp_id,
                "validation_status": "invalid",
                "errors": [{"rule": "PARSE", "message": comp.get("error", "Parse failure")}],
                "warnings": [],
            })
            total_invalid += 1
            continue

        # GLOBAL-VR-001 to GLOBAL-VR-005: Required common properties
        for prop in COMMON_REQUIRED_PROPERTIES:
            val = comp.get(prop, "")
            if not val and val != 0:
                errors.append({
                    "rule": f"GLOBAL-VR-00{list(COMMON_REQUIRED_PROPERTIES).index(prop) + 1}",
                    "message": f"Component is missing required field '{prop}'.",
                })

        # GLOBAL-VR-006: Type enumeration
        comp_type = comp.get("component_type", "")
        if comp_type not in VALID_COMPONENT_TYPES:
            errors.append({
                "rule": "GLOBAL-VR-006",
                "message": f"Unrecognized component_type '{comp_type}'. Must be one of: {', '.join(sorted(VALID_COMPONENT_TYPES))}",
            })

        # GLOBAL-VR-008: component_id format
        if comp_id and comp_id != "(unknown)":
            if not COMPONENT_ID_RE.match(comp_id):
                errors.append({
                    "rule": "GLOBAL-VR-008",
                    "message": f"component_id '{comp_id}' does not follow the naming convention '{{type}}-{{descriptor}}-{{sequence}}'.",
                })

        # GLOBAL-VR-009: Semantic version
        version = comp.get("version", "")
        if version and not SEMVER_RE.match(str(version)):
            errors.append({
                "rule": "GLOBAL-VR-009",
                "message": f"version '{version}' does not follow semantic versioning format (MAJOR.MINOR.PATCH).",
            })

        # GLOBAL-VR-010: Type-specific required properties
        if comp_type in TYPE_SPECIFIC_REQUIRED:
            for prop in TYPE_SPECIFIC_REQUIRED[comp_type]:
                val = comp.get(prop, "")
                if not val and val != 0:
                    errors.append({
                        "rule": "GLOBAL-VR-010",
                        "message": f"Component of type '{comp_type}' is missing required type-specific property '{prop}'.",
                    })

        # GLOBAL-VR-012: Enum value conformance
        for prop, valid_set in ENUM_VALUES.items():
            val = comp.get(prop, "")
            if val and val not in valid_set:
                errors.append({
                    "rule": "GLOBAL-VR-012",
                    "message": f"Property '{prop}' value '{val}' is not in the valid set: {', '.join(sorted(valid_set))}.",
                })

        # GLOBAL-VR-007: Unique ID check (tracked across all components)
        if comp_id in seen_ids:
            errors.append({
                "rule": "GLOBAL-VR-007",
                "message": f"Duplicate component_id '{comp_id}' found. First seen at index {seen_ids[comp_id]}.",
            })
        else:
            seen_ids[comp_id] = len(validation_results)

        # GLOBAL-VR-013: No-override rule
        if comp_type in TYPE_SPECIFIC_REQUIRED:
            for prop in TYPE_SPECIFIC_REQUIRED[comp_type]:
                if prop in COMMON_REQUIRED_PROPERTIES or prop in COMMON_OPTIONAL_PROPERTIES:
                    errors.append({
                        "rule": "GLOBAL-VR-013",
                        "message": f"Type-specific property '{prop}' conflicts with a common property.",
                    })

        # Type-specific cross-property rules
        if comp_type == "hook":
            _validate_hook_cross_props(comp, errors, warnings)
        elif comp_type == "scene":
            _validate_scene_cross_props(comp, errors, warnings)
        elif comp_type == "voice_style":
            _validate_voice_cross_props(comp, errors, warnings)
        elif comp_type == "visual_direction":
            _validate_visdir_cross_props(comp, errors, warnings)
        elif comp_type == "audio_mood":
            _validate_audio_cross_props(comp, errors, warnings)
        elif comp_type == "text_style":
            _validate_text_cross_props(comp, errors, warnings)
        elif comp_type == "transition":
            _validate_transition_cross_props(comp, errors, warnings)

        status = "valid" if not errors else "invalid"
        if status == "valid":
            total_valid += 1
        else:
            total_invalid += 1

        validation_results.append({
            "component_id": comp_id,
            "validation_status": status,
            "errors": errors,
            "warnings": warnings,
        })

    # Write report
    if not report_path_str:
        return ActionResult(
            status="REJECTED",
            remark="VALIDATION_REPORT_FILE artifact path not found in state.",
            artifacts={},
            reject_code="MISSING_OUTPUT_PATH",
        )

    report_path = Path(report_path_str)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    invalid_ids = [
        r["component_id"] for r in validation_results
        if r["validation_status"] == "invalid"
    ]

    report = {
        "validation_timestamp": _now_iso(),
        "total_components_validated": len(components),
        "total_valid": total_valid,
        "total_invalid": total_invalid,
        "invalid_component_ids": invalid_ids,
        "results": validation_results,
    }

    report_path.write_text(
        yaml.dump(report, default_flow_style=False, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )

    remark = (
        f"Validated {len(components)} components: "
        f"{total_valid} valid, {total_invalid} invalid."
    )
    if invalid_ids:
        remark += f" Invalid: {', '.join(invalid_ids[:5])}"

    logger.info("[validate_components] %s", remark)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"VALIDATION_REPORT_FILE": str(report_path)},
    )


# ---------------------------------------------------------------------------
# Cross-property validation helpers
# ---------------------------------------------------------------------------

def _validate_hook_cross_props(
    comp: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    """Validate hook-specific cross-property rules."""
    hook_script = comp.get("hook_script", "")
    if hook_script:
        word_count = len(hook_script.split())
        if word_count > 50:
            errors.append({
                "rule": "HOOK-VR-002",
                "message": f"hook_script exceeds 50-word limit ({word_count} words found).",
            })

    visual_cue = comp.get("visual_cue", "")
    if visual_cue and len(visual_cue) < 10:
        errors.append({
            "rule": "HOOK-VR-004",
            "message": "visual_cue must be a descriptive string of at least 10 characters.",
        })

    hook_style = comp.get("hook_style", "")
    if hook_style == "visual_reveal" and visual_cue:
        if len(visual_cue) < 20:
            warnings.append({
                "rule": "HOOK-VR-006",
                "message": "When hook_style is 'visual_reveal', visual_cue should describe a specific visual element in detail.",
            })


def _validate_scene_cross_props(
    comp: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    """Validate scene-specific cross-property rules."""
    duration = comp.get("duration_target", 0)
    scene_script = comp.get("scene_script", "")

    if isinstance(duration, (int, float)) and duration > 30:
        word_count = len(scene_script.split()) if scene_script else 0
        if word_count <= 75:
            errors.append({
                "rule": "SCENE-VR-005",
                "message": f"Scenes longer than 30 seconds must have a scene_script exceeding 75 words (current: {word_count}).",
            })

    scene_purpose = comp.get("scene_purpose", "")
    if scene_purpose == "call_to_action" and scene_script:
        imperative_verbs = [
            "get", "try", "shop", "buy", "discover", "learn", "find",
            "visit", "check", "start", "join", "grab", "order", "see",
        ]
        first_word = scene_script.split()[0].lower() if scene_script.split() else ""
        if first_word not in imperative_verbs:
            warnings.append({
                "rule": "SCENE-VR-006",
                "message": "call_to_action scenes should include a clear directive in scene_script.",
            })

    visual_dir = comp.get("visual_direction", "")
    if visual_dir and len(visual_dir) < 15:
        errors.append({
            "rule": "SCENE-VR-003",
            "message": "visual_direction must be a descriptive string of at least 15 characters.",
        })


def _validate_voice_cross_props(
    comp: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    """Validate voice_style-specific cross-property rules."""
    voice_tone = comp.get("voice_tone", "")
    pace = comp.get("pace", "")
    if voice_tone == "dramatic" and pace == "fast":
        warnings.append({
            "rule": "VOICE-VR-003",
            "message": "Warning: dramatic voice_tone paired with fast pace may reduce emotional impact.",
        })


def _validate_visdir_cross_props(
    comp: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    """Validate visual_direction-specific cross-property rules."""
    visual_style = comp.get("visual_style", "")
    lighting_mood = comp.get("lighting_mood", "")
    if visual_style == "cinematic" and lighting_mood not in ("dramatic", "warm", ""):
        warnings.append({
            "rule": "VISDIR-VR-005",
            "message": "Warning: cinematic visual_style pairs best with dramatic or warm lighting_mood.",
        })

    color_palette = comp.get("color_palette", "")
    if color_palette and len(color_palette) < 10:
        errors.append({
            "rule": "VISDIR-VR-002",
            "message": "color_palette must describe the color scheme in at least 10 characters.",
        })


def _validate_audio_cross_props(
    comp: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    """Validate audio_mood-specific cross-property rules."""
    mood_val = comp.get("mood", "")
    tempo_val = comp.get("tempo", "")
    if mood_val == "tense" and tempo_val == "slow":
        warnings.append({
            "rule": "AUDIO-VR-003",
            "message": "Warning: tense mood with slow tempo may feel dull rather than suspenseful.",
        })
    if mood_val == "energetic" and tempo_val == "slow":
        warnings.append({
            "rule": "AUDIO-VR-004",
            "message": "Warning: energetic mood paired with slow tempo creates a mismatch.",
        })


def _validate_text_cross_props(
    comp: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    """Validate text_style-specific cross-property rules."""
    treatment = comp.get("text_treatment", "")
    animation = comp.get("text_animation", "")
    if treatment == "kinetic_typography" and animation == "none":
        errors.append({
            "rule": "TEXT-VR-005",
            "message": "kinetic_typography requires a text_animation value other than none.",
        })


def _validate_transition_cross_props(
    comp: dict[str, Any],
    errors: list[dict[str, str]],
    warnings: list[dict[str, str]],
) -> None:
    """Validate transition-specific cross-property rules."""
    trans_type = comp.get("transition_type", "")
    duration = comp.get("transition_duration", 0)
    energy = comp.get("transition_energy", "")

    if isinstance(duration, (int, float)):
        if duration < 0.1 or duration > 5.0:
            errors.append({
                "rule": "TRANS-VR-002",
                "message": f"transition_duration must be between 0.1 and 5.0 seconds (got {duration}).",
            })
        if trans_type == "cut" and duration > 0.3:
            warnings.append({
                "rule": "TRANS-VR-004",
                "message": f"Warning: cut transitions should have duration under 0.3 seconds (got {duration}).",
            })
        if energy == "high" and duration >= 1.0:
            warnings.append({
                "rule": "TRANS-VR-005",
                "message": "High-energy transitions should be quick (under 1.0s) to maintain momentum.",
            })


# ---------------------------------------------------------------------------
# Action: plan_compositions
# ---------------------------------------------------------------------------

@action("plan_compositions")
def plan_compositions(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: Path,
) -> ActionResult:
    """Parse compositions, resolve references, validate overrides, and plan.

    Reads all composition YAML files from COMPOSITIONS_DIR, resolves every
    component_id against the inventory, validates overrides against the
    component type schema, inventories placeholders, checks binding
    requirements, and writes a resolution plan to RESOLUTION_PLAN_FILE.
    """
    project_root = Path(project_root)
    artifacts = state.get("artifacts", {})

    compositions_dir_str = artifacts.get("COMPOSITIONS_DIR", "")
    inventory_path_str = artifacts.get("COMPONENT_INVENTORY_FILE", "")
    report_path_str = artifacts.get("VALIDATION_REPORT_FILE", "")
    data_source_dir_str = artifacts.get("DATA_SOURCE_DIR", "")
    plan_path_str = artifacts.get("RESOLUTION_PLAN_FILE", "")

    if not compositions_dir_str:
        return ActionResult(
            status="REJECTED",
            remark="COMPOSITIONS_DIR artifact not found in state.",
            artifacts={},
            reject_code="MISSING_COMPOSITIONS_DIR",
        )

    compositions_dir = Path(compositions_dir_str)
    if not compositions_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"COMPOSITIONS_DIR does not exist: {compositions_dir}",
            artifacts={},
            reject_code="NO_COMPOSITIONS",
        )

    yaml_files = sorted(
        list(compositions_dir.glob("*.yaml"))
        + list(compositions_dir.glob("*.yml"))
    )
    if not yaml_files:
        return ActionResult(
            status="REJECTED",
            remark=f"No YAML composition files found in {compositions_dir}",
            artifacts={},
            reject_code="NO_COMPOSITIONS",
        )

    # Load component inventory as lookup dict
    component_lookup: dict[str, dict[str, Any]] = {}
    if inventory_path_str:
        inv_path = Path(inventory_path_str)
        if inv_path.is_file():
            try:
                inv_data = yaml.safe_load(inv_path.read_text(encoding="utf-8"))
                for comp in inv_data.get("components", []):
                    cid = comp.get("component_id", "")
                    if cid:
                        component_lookup[cid] = comp
            except Exception as exc:
                logger.warning("[plan_compositions] Failed to load inventory: %s", exc)

    # Load validation report for invalid component flags
    invalid_ids: set[str] = set()
    if report_path_str:
        rpt_path = Path(report_path_str)
        if rpt_path.is_file():
            try:
                rpt_data = yaml.safe_load(rpt_path.read_text(encoding="utf-8"))
                invalid_ids = set(rpt_data.get("invalid_component_ids", []))
            except Exception as exc:
                logger.warning("[plan_compositions] Failed to load validation report: %s", exc)

    # Load data source field availability
    available_fields: set[str] = set()
    if data_source_dir_str:
        ds_dir = Path(data_source_dir_str)
        if ds_dir.is_dir():
            available_fields = _scan_data_source_fields(ds_dir)

    # Process each composition
    composition_plans: list[dict[str, Any]] = []

    for yaml_file in yaml_files:
        try:
            comp_data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            composition_plans.append({
                "file": str(yaml_file),
                "status": "parse_error",
                "error": f"YAML parse error: {exc}",
            })
            continue

        if not isinstance(comp_data, dict):
            composition_plans.append({
                "file": str(yaml_file),
                "status": "parse_error",
                "error": "Composition file root is not a YAML mapping",
            })
            continue

        comp_id = comp_data.get("composition_id", "(unknown)")
        plan = _plan_single_composition(
            comp_id=comp_id,
            comp_data=comp_data,
            component_lookup=component_lookup,
            invalid_ids=invalid_ids,
            available_fields=available_fields,
            source_file=str(yaml_file),
        )
        composition_plans.append(plan)

    # Write resolution plan
    if not plan_path_str:
        return ActionResult(
            status="REJECTED",
            remark="RESOLUTION_PLAN_FILE artifact path not found in state.",
            artifacts={},
            reject_code="MISSING_OUTPUT_PATH",
        )

    plan_path = Path(plan_path_str)
    plan_path.parent.mkdir(parents=True, exist_ok=True)

    resolution_plan = {
        "plan_timestamp": _now_iso(),
        "total_compositions": len(yaml_files),
        "compositions": composition_plans,
    }

    plan_path.write_text(
        yaml.dump(resolution_plan, default_flow_style=False, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )

    ok_count = sum(1 for p in composition_plans if p.get("status") == "planned")
    err_count = len(composition_plans) - ok_count

    remark = (
        f"Planned {len(yaml_files)} compositions: "
        f"{ok_count} successfully planned, {err_count} with errors."
    )
    logger.info("[plan_compositions] %s", remark)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"RESOLUTION_PLAN_FILE": str(plan_path)},
    )


def _plan_single_composition(
    *,
    comp_id: str,
    comp_data: dict[str, Any],
    component_lookup: dict[str, dict[str, Any]],
    invalid_ids: set[str],
    available_fields: set[str],
    source_file: str,
) -> dict[str, Any]:
    """Plan resolution for a single composition."""
    plan: dict[str, Any] = {
        "composition_id": comp_id,
        "name": comp_data.get("name", ""),
        "source_file": source_file,
        "target_metadata": comp_data.get("target_metadata", {}),
        "status": "planned",
        "bindings": {},
        "reference_integrity": [],
        "override_conformance": [],
        "placeholder_inventory": [],
        "binding_presence": [],
        "ordering_constraints": [],
        "data_source_availability": [],
        "errors": [],
    }

    bindings = comp_data.get("component_bindings", {})
    if not isinstance(bindings, dict):
        plan["errors"].append("component_bindings is not a YAML mapping")
        plan["status"] = "error"
        return plan

    # Check required bindings presence
    for req_binding in REQUIRED_BINDINGS:
        if req_binding in bindings:
            plan["binding_presence"].append({
                "binding": req_binding,
                "status": "present",
            })
        else:
            plan["binding_presence"].append({
                "binding": req_binding,
                "status": "MISSING",
                "severity": "CRITICAL",
            })
            plan["errors"].append(f"Required binding '{req_binding}' is missing")

    for opt_binding in OPTIONAL_BINDINGS:
        if opt_binding in bindings:
            plan["binding_presence"].append({
                "binding": opt_binding,
                "status": "present",
            })
        else:
            plan["binding_presence"].append({
                "binding": opt_binding,
                "status": "omitted",
            })

    all_placeholders: list[dict[str, str]] = []

    # Process each binding
    for binding_name, binding_value in bindings.items():
        expected_type = BINDING_TYPE_MAP.get(binding_name, "")
        is_singleton = binding_name in SINGLETON_BINDINGS
        is_ordered_list = binding_name in ORDERED_LIST_BINDINGS

        if is_singleton:
            _plan_singleton_binding(
                binding_name, binding_value, expected_type,
                component_lookup, invalid_ids, plan, all_placeholders,
            )
        elif is_ordered_list:
            _plan_ordered_list_binding(
                binding_name, binding_value, expected_type,
                component_lookup, invalid_ids, plan, all_placeholders,
            )
        else:
            plan["errors"].append(f"Unknown binding name: '{binding_name}'")

    # Ordering constraints for scenes and transitions
    scenes_binding = bindings.get("scenes", [])
    if isinstance(scenes_binding, list):
        scene_count = len(scenes_binding)
        if scene_count < 3 or scene_count > 8:
            plan["ordering_constraints"].append({
                "constraint": "scene_count",
                "status": "VIOLATION",
                "message": f"Scene count must be 3-8, got {scene_count}",
                "severity": "CRITICAL",
            })
            plan["errors"].append(f"Scene count {scene_count} outside 3-8 range")
        else:
            plan["ordering_constraints"].append({
                "constraint": "scene_count",
                "status": "ok",
                "value": scene_count,
            })

        transitions_binding = bindings.get("transitions", [])
        if isinstance(transitions_binding, list) and transitions_binding:
            expected_transitions = scene_count - 1
            actual_transitions = len(transitions_binding)
            if actual_transitions != expected_transitions:
                plan["ordering_constraints"].append({
                    "constraint": "transition_count",
                    "status": "VIOLATION",
                    "message": (
                        f"Transitions count must be {expected_transitions} "
                        f"(scenes - 1), got {actual_transitions}"
                    ),
                    "severity": "MAJOR",
                })
            else:
                plan["ordering_constraints"].append({
                    "constraint": "transition_count",
                    "status": "ok",
                    "value": actual_transitions,
                })

    # Placeholder resolvability
    for ph in all_placeholders:
        ph_name = ph["placeholder"]
        if ph_name in available_fields:
            ph["resolvability"] = "RESOLVABLE"
        else:
            ph["resolvability"] = "UNRESOLVABLE"
            ph["note"] = f"No data source provides '{ph_name}'"

    plan["placeholder_inventory"] = all_placeholders

    # Data source declarations
    data_sources = comp_data.get("data_sources", {})
    if isinstance(data_sources, dict):
        for ds_name, ds_path in data_sources.items():
            plan["data_source_availability"].append({
                "name": ds_name,
                "declared_path": str(ds_path),
            })

    if plan["errors"]:
        plan["status"] = "error"

    return plan


def _plan_singleton_binding(
    binding_name: str,
    binding_value: Any,
    expected_type: str,
    component_lookup: dict[str, dict[str, Any]],
    invalid_ids: set[str],
    plan: dict[str, Any],
    all_placeholders: list[dict[str, str]],
) -> None:
    """Process a singleton binding entry."""
    if not isinstance(binding_value, dict):
        plan["errors"].append(
            f"Singleton binding '{binding_name}' must be a mapping, "
            f"got {type(binding_value).__name__}"
        )
        return

    ref_id = binding_value.get("component_id", "")
    overrides = binding_value.get("overrides", {})

    # Reference integrity
    if ref_id in component_lookup:
        comp = component_lookup[ref_id]
        actual_type = comp.get("component_type", "")
        if expected_type and actual_type != expected_type:
            plan["reference_integrity"].append({
                "binding": binding_name,
                "component_id": ref_id,
                "status": "TYPE_MISMATCH",
                "expected": expected_type,
                "actual": actual_type,
            })
            plan["errors"].append(
                f"Binding '{binding_name}' expects type '{expected_type}' "
                f"but '{ref_id}' is type '{actual_type}'"
            )
        elif ref_id in invalid_ids:
            plan["reference_integrity"].append({
                "binding": binding_name,
                "component_id": ref_id,
                "status": "REFERENCES_INVALID_COMPONENT",
            })
        else:
            plan["reference_integrity"].append({
                "binding": binding_name,
                "component_id": ref_id,
                "status": "RESOLVED",
            })
    else:
        plan["reference_integrity"].append({
            "binding": binding_name,
            "component_id": ref_id,
            "status": "MISSING",
        })
        plan["errors"].append(
            f"component_id '{ref_id}' not found in component inventory"
        )

    # Override conformance
    if isinstance(overrides, dict) and ref_id in component_lookup:
        comp_type = component_lookup[ref_id].get("component_type", "")
        known_props = set()
        if comp_type in TYPE_SPECIFIC_REQUIRED:
            known_props = set(TYPE_SPECIFIC_REQUIRED[comp_type])
        known_props |= COMMON_REQUIRED_PROPERTIES | COMMON_OPTIONAL_PROPERTIES

        for override_key in overrides:
            if override_key not in known_props:
                plan["override_conformance"].append({
                    "binding": binding_name,
                    "property": override_key,
                    "status": "INVALID_PROPERTY",
                })
            else:
                plan["override_conformance"].append({
                    "binding": binding_name,
                    "property": override_key,
                    "status": "VALID",
                })

    # Collect placeholders from overrides
    if isinstance(overrides, dict):
        for ph_name in _find_placeholders(overrides):
            all_placeholders.append({
                "placeholder": ph_name,
                "location": f"binding:{binding_name}.overrides",
            })

    # Collect placeholders from resolved component values
    if ref_id in component_lookup:
        comp = component_lookup[ref_id]
        for key in ["description", "hook_script", "scene_script", "visual_cue",
                     "visual_direction", "emphasis_pattern", "voice_character",
                     "color_palette", "camera_work", "instrumentation",
                     "volume_balance", "font_style", "text_color_scheme"]:
            val = comp.get(key, "")
            if isinstance(val, str):
                for ph_name in PLACEHOLDER_RE.findall(val):
                    all_placeholders.append({
                        "placeholder": ph_name,
                        "location": f"component:{ref_id}.{key}",
                    })

    plan["bindings"][binding_name] = {
        "mode": "singleton",
        "component_id": ref_id,
        "overrides": overrides if isinstance(overrides, dict) else {},
    }


def _plan_ordered_list_binding(
    binding_name: str,
    binding_value: Any,
    expected_type: str,
    component_lookup: dict[str, dict[str, Any]],
    invalid_ids: set[str],
    plan: dict[str, Any],
    all_placeholders: list[dict[str, str]],
) -> None:
    """Process an ordered list binding entry."""
    if not isinstance(binding_value, list):
        plan["errors"].append(
            f"Ordered list binding '{binding_name}' must be an array, "
            f"got {type(binding_value).__name__}"
        )
        return

    items = []
    for idx, entry in enumerate(binding_value):
        if not isinstance(entry, dict):
            plan["errors"].append(
                f"Binding '{binding_name}[{idx}]' must be a mapping"
            )
            continue

        ref_id = entry.get("component_id", "")
        overrides = entry.get("overrides", {})

        # Reference integrity
        if ref_id in component_lookup:
            comp = component_lookup[ref_id]
            actual_type = comp.get("component_type", "")
            if expected_type and actual_type != expected_type:
                plan["reference_integrity"].append({
                    "binding": f"{binding_name}[{idx}]",
                    "component_id": ref_id,
                    "status": "TYPE_MISMATCH",
                    "expected": expected_type,
                    "actual": actual_type,
                })
            elif ref_id in invalid_ids:
                plan["reference_integrity"].append({
                    "binding": f"{binding_name}[{idx}]",
                    "component_id": ref_id,
                    "status": "REFERENCES_INVALID_COMPONENT",
                })
            else:
                plan["reference_integrity"].append({
                    "binding": f"{binding_name}[{idx}]",
                    "component_id": ref_id,
                    "status": "RESOLVED",
                })
        else:
            plan["reference_integrity"].append({
                "binding": f"{binding_name}[{idx}]",
                "component_id": ref_id,
                "status": "MISSING",
            })

        # Collect placeholders
        if isinstance(overrides, dict):
            for ph_name in _find_placeholders(overrides):
                all_placeholders.append({
                    "placeholder": ph_name,
                    "location": f"binding:{binding_name}[{idx}].overrides",
                })

        items.append({
            "index": idx,
            "component_id": ref_id,
            "overrides": overrides if isinstance(overrides, dict) else {},
        })

    plan["bindings"][binding_name] = {
        "mode": "ordered_list",
        "items": items,
    }


def _scan_data_source_fields(data_source_dir: Path) -> set[str]:
    """Scan data source directory and extract all available field names."""
    fields: set[str] = set()
    for yaml_file in data_source_dir.rglob("*.yaml"):
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                fields.update(data.keys())
        except Exception:
            pass
    for yaml_file in data_source_dir.rglob("*.yml"):
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                fields.update(data.keys())
        except Exception:
            pass
    return fields


# ---------------------------------------------------------------------------
# Action: promote_workflow_package
# ---------------------------------------------------------------------------

@action("promote_workflow_package")
def promote_workflow_package(
    *, context: dict[str, str], state: dict[str, Any],
    step_cfg: dict[str, Any], project_root: Path,
) -> ActionResult:
    """Promote the generated workflow package to the repo workflows directory.

    Copies deployable files from the run output directory to
    workflows/{workflow_name}/. The workflow name is derived from the
    WORKFLOW_MANIFEST_FILE artifact path parent directory structure,
    or from step config slug_source_artifact.
    """
    artifacts = state.get("artifacts", {})
    project_root = Path(project_root)

    manifest_path_str = artifacts.get("WORKFLOW_MANIFEST_FILE", "")
    if not manifest_path_str:
        return ActionResult(
            status="REJECTED",
            remark="WORKFLOW_MANIFEST_FILE artifact not found in state.",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )

    manifest_path = Path(manifest_path_str)
    if not manifest_path.is_file():
        return ActionResult(
            status="REJECTED",
            remark=f"Workflow manifest file not found: {manifest_path}",
            artifacts={},
            reject_code="MISSING_MANIFEST",
        )

    source_dir = manifest_path.parent
    workflow_name = step_cfg.get("workflow_name", "video_campaign_manuscript")
    target_dir = project_root / "workflows" / workflow_name

    # Backup existing target
    if target_dir.exists():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_dir = project_root / "workflows" / f"{workflow_name}_bak_{timestamp}"
        try:
            shutil.copytree(target_dir, backup_dir)
            logger.info("[promote_workflow_package] backed up %s -> %s", target_dir, backup_dir)
        except Exception as exc:
            logger.warning("[promote_workflow_package] backup failed: %s", exc)

    target_dir.mkdir(parents=True, exist_ok=True)

    always_copy = ["workflow.toml", "context_extensions.py", "README.md"]
    conditional_copy = ["actions.py", ".env.sample", "config.json.sample"]
    copy_dirs = ["prompts"]

    copied: list[str] = []

    for filename in always_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            copied.append(filename)

    for filename in conditional_copy:
        src = source_dir / filename
        if src.exists():
            shutil.copy2(src, target_dir / filename)
            copied.append(filename)

    for dirname in copy_dirs:
        src = source_dir / dirname
        if src.is_dir():
            dst = target_dir / dirname
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            copied.append(f"{dirname}/")

    if not copied:
        return ActionResult(
            status="REJECTED",
            remark=f"No files found to promote in {source_dir}",
            artifacts={},
            reject_code="NOTHING_TO_PROMOTE",
        )

    remark = f"Promoted to {target_dir}: {', '.join(copied)}"
    logger.info("[promote_workflow_package] %s", remark)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts={"WORKFLOW_PACKAGE_DIR_FILE": str(target_dir)},
    )
