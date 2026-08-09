"""Custom actions for video_campaign_manuscript workflow.

This module implements the two custom action steps for the composition
system workflow:

- scan_components: Discovers and validates component files in the library.
- plan_compositions: Resolves compositions against the component inventory.

Both actions follow the agent-runner-v2 action module pattern with the
@action decorator and return ActionResult instances.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from agent_runner_v2.action_result import ActionResult
from agent_runner_v2.workflow_packages.actions import action


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_COMPONENT_TYPES = frozenset({
    "hook", "scene", "voice_style", "visual_direction",
    "audio_mood", "text_style", "transition",
})

COMMON_REQUIRED_FIELDS = frozenset({
    "component_id", "component_type", "name", "version", "description",
})

RESERVED_COMMON_NAMES = frozenset({
    "component_id", "component_type", "name", "version",
    "description", "duration_range", "platforms", "tags",
})

VALID_PLATFORMS = frozenset({"tiktok", "reels", "shorts"})

# Type-specific required properties
TYPE_SPECIFIC_REQUIRED: dict[str, list[str]] = {
    "hook": ["hook_style", "hook_script", "visual_cue", "energy_level"],
    "scene": ["scene_purpose", "scene_script", "visual_direction", "duration_target"],
    "voice_style": ["voice_tone", "pace"],
    "visual_direction": ["visual_style", "color_palette", "lighting_mood"],
    "audio_mood": ["mood", "tempo"],
    "text_style": ["text_treatment"],
    "transition": ["transition_type", "transition_duration", "transition_energy"],
}

# Enum validations
ENUM_VALUES: dict[str, set[str]] = {
    "hook_style": {"dramatic_reveal", "question_hook", "statistic_hook", "visual_reveal", "challenge_hook"},
    "energy_level": {"low", "medium", "high"},
    "scene_purpose": {"problem", "solution", "demo", "testimonial", "CTA", "education", "comparison"},
    "voice_tone": {"authoritative", "conversational", "energetic", "empathetic", "playful"},
    "pace": {"slow", "moderate", "fast", "varied"},
    "visual_style": {"cinematic", "minimalist", "vibrant", "documentary", "animated", "mixed_media"},
    "lighting_mood": {"bright", "moody", "natural", "dramatic", "soft"},
    "mood": {"uplifting", "tense", "inspirational", "playful", "calm", "dramatic"},
    "tempo": {"slow", "moderate", "fast", "dynamic"},
    "text_treatment": {"subtitles", "kinetic_typography", "lower_thirds", "title_cards", "callouts"},
    "text_animation": {"none", "fade", "slide", "typewriter", "bounce"},
    "transition_type": {"cut", "fade", "dissolve", "wipe", "zoom", "match_cut", "whip_pan"},
    "transition_energy": {"subtle", "moderate", "dramatic"},
}

# Binding slot -> expected component type
BINDING_TYPE_MAP: dict[str, str] = {
    "opening": "hook",
    "scenes": "scene",
    "voice": "voice_style",
    "visuals": "visual_direction",
    "audio": "audio_mood",
    "text": "text_style",
    "transitions": "transition",
}

REQUIRED_BINDINGS = frozenset({"opening", "scenes", "voice", "visuals", "audio", "transitions"})

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
COMPONENT_ID_RE = re.compile(r"^[a-z]+-[a-z0-9]+-[0-9]{3}$")
DURATION_RE = re.compile(r"^\d+(-\d+)?s$")
PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str] | None:
    """Parse YAML frontmatter from a markdown file.

    Returns a tuple of (frontmatter_dict, body_text) or None if no
    frontmatter is found.
    """
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return None
    # Find the closing ---
    end_idx = stripped.index("---", 3)
    if end_idx < 0:
        return None
    yaml_block = stripped[3:end_idx].strip()
    body = stripped[end_idx + 3:].strip()
    try:
        fm = yaml.safe_load(yaml_block)
    except yaml.YAMLError:
        return None
    if not isinstance(fm, dict):
        return None
    return fm, body


def _validate_component(
    fm: dict[str, Any],
    seen_ids: dict[str, int],
) -> tuple[str, list[str]]:
    """Validate a single component's frontmatter.

    Returns (validation_status, list_of_error_rule_ids).
    """
    errors: list[str] = []

    # GLOBAL-VR-001 through GLOBAL-VR-005: Required fields
    for field in COMMON_REQUIRED_FIELDS:
        if field not in fm or not fm[field]:
            errors.append(f"GLOBAL-VR-001: Missing required field: {field}")

    # GLOBAL-VR-006: component_type validity
    ct = fm.get("component_type", "")
    if ct and ct not in VALID_COMPONENT_TYPES:
        errors.append(f"GLOBAL-VR-006: Invalid component_type '{ct}'")

    # GLOBAL-VR-007: component_id uniqueness
    cid = fm.get("component_id", "")
    if cid:
        if cid in seen_ids:
            errors.append(f"GLOBAL-VR-007: Duplicate component_id '{cid}'")
        seen_ids[cid] = seen_ids.get(cid, 0) + 1

    # GLOBAL-VR-008: component_id naming convention
    if cid and not COMPONENT_ID_RE.match(cid):
        errors.append(f"GLOBAL-VR-008: component_id '{cid}' does not follow naming convention")

    # GLOBAL-VR-012: Semantic version format
    ver = fm.get("version", "")
    if ver and not SEMVER_RE.match(str(ver)):
        errors.append(f"GLOBAL-VR-012: version '{ver}' does not match MAJOR.MINOR.PATCH")
    elif ver:
        parts = str(ver).split(".")
        if any(int(p) < 0 for p in parts):
            errors.append(f"GLOBAL-VR-013: version '{ver}' contains negative components")

    # GLOBAL-VR-014: Duration format
    dur = fm.get("duration_range")
    if dur and not DURATION_RE.match(str(dur)):
        errors.append(f"GLOBAL-VR-014: duration_range '{dur}' does not match required format")

    # Platforms validation
    plats = fm.get("platforms")
    if plats:
        if not isinstance(plats, list) or not plats:
            errors.append("Invalid platforms: must be a non-empty array")
        else:
            for p in plats:
                if p not in VALID_PLATFORMS:
                    errors.append(f"Invalid platform '{p}'")

    # GLOBAL-VR-009: Type-specific required properties
    if ct in TYPE_SPECIFIC_REQUIRED:
        for prop in TYPE_SPECIFIC_REQUIRED[ct]:
            if prop not in fm or fm[prop] is None:
                errors.append(f"GLOBAL-VR-009: Missing required type-specific property '{prop}' for type '{ct}'")

    # GLOBAL-VR-010 / enum validation
    for prop, valid_set in ENUM_VALUES.items():
        val = fm.get(prop)
        if val is not None and str(val) not in valid_set:
            errors.append(f"GLOBAL-VR-010: Property '{prop}' has invalid value '{val}'. Must be one of: {', '.join(sorted(valid_set))}")

    # GLOBAL-VR-011: Property name conflicts
    for key in fm:
        if key not in COMMON_REQUIRED_FIELDS and key != "duration_range" and key != "platforms" and key != "tags":
            if key in RESERVED_COMMON_NAMES:
                errors.append(f"GLOBAL-VR-011: Type-specific property '{key}' conflicts with reserved common property name")

    # Type-specific cross-property validation
    _validate_cross_property(fm, ct, errors)

    # Hook-specific: HOOK-VR-002 word count
    if ct == "hook":
        script = fm.get("hook_script", "")
        if script and len(str(script).split()) > 50:
            errors.append(f"HOOK-VR-002: hook_script exceeds 50 words (found {len(str(script).split())} words)")

    status = "valid" if not errors else "invalid"
    return status, errors


def _validate_cross_property(
    fm: dict[str, Any], ct: str, errors: list[str]
) -> None:
    """Validate cross-property constraints for a component."""
    # HOOK-VR-006: visual_reveal requires visual_cue >= 20 chars
    if ct == "hook" and fm.get("hook_style") == "visual_reveal":
        vc = str(fm.get("visual_cue", ""))
        if len(vc) < 20:
            errors.append("HOOK-VR-006: hook_style=visual_reveal requires visual_cue >= 20 characters")

    # TRANS-VR-005: whip_pan requires moderate or dramatic energy
    if ct == "transition" and fm.get("transition_type") == "whip_pan":
        te = fm.get("transition_energy", "")
        if te == "subtle":
            errors.append("TRANS-VR-005: transition_type=whip_pan requires transition_energy moderate or dramatic")

    # TRANS-VR-006: cut should be 0.1s or less
    if ct == "transition" and fm.get("transition_type") == "cut":
        td = str(fm.get("transition_duration", ""))
        if td:
            # Parse numeric value
            match = re.match(r"^(\d+\.?\d*)s?$", td)
            if match:
                val = float(match.group(1))
                if val > 0.1:
                    errors.append(f"TRANS-VR-006: transition_type=cut with transition_duration='{td}' is contradictory")


def _load_yaml_file(path: Path) -> dict[str, Any] | None:
    """Load and parse a YAML file. Returns None on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            return data
        return None
    except (yaml.YAMLError, OSError):
        return None


# ---------------------------------------------------------------------------
# Action: scan_components
# ---------------------------------------------------------------------------


@action("scan_components")
def scan_components(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Scan the component library directory and validate all components.

    Walks the COMPONENT_LIBRARY_DIR for markdown files with YAML frontmatter.
    Parses each file, extracts component properties, classifies by type,
    and validates against the component schema rules.

    Produces:
    - COMPONENT_INVENTORY_FILE: JSON catalog of all discovered components.
    - VALIDATION_REPORT_FILE: Markdown report with per-component validation findings.
    """
    library_dir_str = context.get("COMPONENT_LIBRARY_DIR", "")
    if not library_dir_str:
        return ActionResult(
            status="REJECTED",
            remark="COMPONENT_LIBRARY_DIR not found in context.",
            artifacts={},
            reject_code="MISSING_CONTEXT",
        )

    library_dir = Path(library_dir_str)
    if not library_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Component library directory not found at {library_dir}",
            artifacts={},
            reject_code="DIR_NOT_FOUND",
        )

    md_files = sorted(library_dir.rglob("*.md"))
    if not md_files:
        return ActionResult(
            status="REJECTED",
            remark=f"No component files found in {library_dir}",
            artifacts={},
            reject_code="NO_COMPONENTS",
        )

    inventory: list[dict[str, Any]] = []
    seen_ids: dict[str, int] = {}

    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8")
        except OSError:
            inventory.append({
                "file_path": str(md_file.relative_to(library_dir)),
                "validation_status": "invalid",
                "validation_errors": ["File could not be read"],
            })
            continue

        parsed = _parse_frontmatter(text)
        if parsed is None:
            inventory.append({
                "file_path": str(md_file.relative_to(library_dir)),
                "validation_status": "invalid",
                "validation_errors": ["No valid YAML frontmatter found"],
            })
            continue

        fm, _body = parsed
        status, errors = _validate_component(fm, seen_ids)

        record: dict[str, Any] = {
            "component_id": fm.get("component_id", ""),
            "component_type": fm.get("component_type", ""),
            "name": fm.get("name", ""),
            "version": fm.get("version", ""),
            "description": fm.get("description", ""),
            "duration_range": fm.get("duration_range", ""),
            "platforms": fm.get("platforms", []),
            "tags": fm.get("tags", []),
            "validation_status": status,
            "validation_errors": [e.split(": ")[0] if ": " in e else e for e in errors],
            "validation_details": errors,
            "file_path": str(md_file.relative_to(library_dir)),
            "properties": {
                k: v for k, v in fm.items()
                if k not in COMMON_REQUIRED_FIELDS and k not in ("duration_range", "platforms", "tags")
            },
        }
        inventory.append(record)

    # Second pass: mark duplicates for GLOBAL-VR-007
    for rec in inventory:
        cid = rec.get("component_id", "")
        if cid and seen_ids.get(cid, 0) > 1:
            if "GLOBAL-VR-007" not in rec["validation_errors"]:
                rec["validation_errors"].append("GLOBAL-VR-007")
                rec["validation_status"] = "invalid"
                rec["validation_details"].append(f"GLOBAL-VR-007: Duplicate component_id '{cid}'")

    # Sort by type then component_id
    inventory.sort(key=lambda r: (r.get("component_type", ""), r.get("component_id", "")))

    # Write inventory JSON
    inv_path = Path(context["COMPONENT_INVENTORY_FILE"])
    inv_path.parent.mkdir(parents=True, exist_ok=True)
    inv_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=True), encoding="utf-8")

    # Build and write validation report
    valid_count = sum(1 for r in inventory if r["validation_status"] == "valid")
    invalid_count = len(inventory) - valid_count
    type_counts: dict[str, int] = {}
    for r in inventory:
        ct = r.get("component_type", "unknown")
        type_counts[ct] = type_counts.get(ct, 0) + 1

    lines: list[str] = []
    lines.append("# Component Validation Report")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Total components scanned: {len(inventory)}")
    lines.append(f"- Valid: {valid_count}")
    lines.append(f"- Invalid: {invalid_count}")
    lines.append("")
    lines.append("## Components by Type")
    for ct in sorted(type_counts):
        lines.append(f"- {ct}: {type_counts[ct]}")
    lines.append("")
    lines.append("## Detailed Findings")
    lines.append("")

    for rec in inventory:
        cid = rec.get("component_id", "(unknown)")
        status = rec["validation_status"]
        lines.append(f"### {cid}")
        lines.append(f"- File: {rec.get('file_path', '')}")
        lines.append(f"- Status: {status}")
        if rec.get("validation_details"):
            for detail in rec["validation_details"]:
                lines.append(f"- Error: {detail}")
        else:
            lines.append("- No errors")
        lines.append("")

    report_path = Path(context["VALIDATION_REPORT_FILE"])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Scanned {len(inventory)} components: {valid_count} valid, {invalid_count} invalid.",
        artifacts={
            "COMPONENT_INVENTORY_FILE": str(inv_path),
            "VALIDATION_REPORT_FILE": str(report_path),
        },
    )


# ---------------------------------------------------------------------------
# Action: plan_compositions
# ---------------------------------------------------------------------------


@action("plan_compositions")
def plan_compositions(
    *,
    context: dict[str, str],
    state: dict[str, Any],
    step_cfg: dict[str, Any],
    project_root: Path,
) -> ActionResult:
    """Resolve compositions against the component inventory.

    Reads all composition YAML files, resolves component_id references,
    validates overrides, checks binding constraints, and inventories
    placeholders for resolvability assessment.

    Produces:
    - RESOLUTION_PLAN_FILE: Markdown document with per-composition resolution details.
    """
    # Load component inventory
    inv_path_str = context.get("COMPONENT_INVENTORY_FILE", "")
    if not inv_path_str:
        return ActionResult(
            status="REJECTED",
            remark="COMPONENT_INVENTORY_FILE not found in context.",
            artifacts={},
            reject_code="MISSING_CONTEXT",
        )

    inv_path = Path(inv_path_str)
    if not inv_path.is_file():
        return ActionResult(
            status="REJECTED",
            remark=f"Component inventory file not found at {inv_path}",
            artifacts={},
            reject_code="FILE_NOT_FOUND",
        )

    try:
        inventory_data = json.loads(inv_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to load component inventory: {exc}",
            artifacts={},
            reject_code="PARSE_ERROR",
        )

    if not inventory_data:
        return ActionResult(
            status="REJECTED",
            remark="Component inventory is empty -- cannot resolve compositions",
            artifacts={},
            reject_code="EMPTY_INVENTORY",
        )

    # Build lookup map: component_id -> record
    comp_map: dict[str, dict[str, Any]] = {}
    for rec in inventory_data:
        cid = rec.get("component_id", "")
        if cid:
            comp_map[cid] = rec

    # Load compositions
    comp_dir_str = context.get("COMPOSITIONS_DIR", "")
    if not comp_dir_str:
        return ActionResult(
            status="REJECTED",
            remark="COMPOSITIONS_DIR not found in context.",
            artifacts={},
            reject_code="MISSING_CONTEXT",
        )

    comp_dir = Path(comp_dir_str)
    if not comp_dir.is_dir():
        return ActionResult(
            status="REJECTED",
            remark=f"Compositions directory not found at {comp_dir}",
            artifacts={},
            reject_code="DIR_NOT_FOUND",
        )

    yaml_files = sorted(
        list(comp_dir.glob("*.yaml")) + list(comp_dir.glob("*.yml"))
    )
    if not yaml_files:
        return ActionResult(
            status="REJECTED",
            remark=f"No composition files found in {comp_dir}",
            artifacts={},
            reject_code="NO_COMPOSITIONS",
        )

    # Data source dir
    ds_dir_str = context.get("DATA_SOURCE_DIR", "")
    ds_dir = Path(ds_dir_str) if ds_dir_str else None

    # Process each composition
    lines: list[str] = []
    lines.append("# Resolution Plan")
    lines.append("")

    for yaml_file in yaml_files:
        comp_data = _load_yaml_file(yaml_file)
        if comp_data is None:
            lines.append(f"## Composition: {yaml_file.stem}")
            lines.append(f"- **Verdict:** UNRESOLVABLE")
            lines.append(f"- **Finding:** YAML parse error in {yaml_file.name}")
            lines.append("")
            continue

        comp_id = comp_data.get("composition_id", yaml_file.stem)
        comp_name = comp_data.get("name", "(unnamed)")
        target_meta = comp_data.get("target_metadata", {})
        data_sources = comp_data.get("data_sources", {})
        bindings = comp_data.get("component_bindings", {})

        lines.append(f"## Composition: {comp_id}")
        lines.append(f"- **Name:** {comp_name}")
        lines.append(f"- **Duration Target:** {target_meta.get('duration_target', 'N/A')}")
        lines.append(f"- **Target Platforms:** {', '.join(target_meta.get('target_platforms', []))}")
        lines.append(f"- **Campaign Type:** {target_meta.get('campaign_type', 'N/A')}")
        lines.append(f"- **Brand:** {target_meta.get('brand', 'N/A')}")
        lines.append("")

        findings: list[tuple[str, str]] = []  # (severity, message)
        resolved_bindings: list[dict[str, Any]] = []
        all_placeholders: dict[str, str] = {}  # placeholder -> status

        # Check required bindings (CF-VAL-006)
        for rb in REQUIRED_BINDINGS:
            if rb not in bindings:
                findings.append(("CRITICAL", f"CF-VAL-006: Missing required binding '{rb}'"))

        # Resolve each binding
        for binding_name, binding_val in bindings.items():
            expected_type = BINDING_TYPE_MAP.get(binding_name)

            if binding_name not in BINDING_TYPE_MAP:
                findings.append(("MAJOR", f"Unrecognized binding name '{binding_name}'"))
                continue

            # Handle singleton vs list
            binding_refs: list[dict[str, Any]] = []
            if isinstance(binding_val, list):
                for item in binding_val:
                    if isinstance(item, dict):
                        binding_refs.append(item)
            elif isinstance(binding_val, dict):
                binding_refs = [binding_val]
            else:
                findings.append(("MAJOR", f"Binding '{binding_name}' has unexpected format"))
                continue

            # Singleton check (CF-VAL-012)
            if expected_type and expected_type not in ("scene", "transition"):
                if len(binding_refs) != 1:
                    findings.append(("CRITICAL", f"CF-VAL-012: Singleton binding '{binding_name}' contains {len(binding_refs)} references"))

            for ref in binding_refs:
                cid = ref.get("component_id", "")
                overrides = ref.get("overrides", {})

                # CF-VAL-001: Reference exists
                if cid not in comp_map:
                    findings.append(("CRITICAL", f"CF-VAL-001: Component '{cid}' not found in inventory"))
                    continue

                comp_rec = comp_map[cid]
                actual_type = comp_rec.get("component_type", "")

                # CF-VAL-002: Type matches binding slot
                if expected_type and actual_type != expected_type:
                    findings.append(("CRITICAL", f"CF-VAL-002: Component '{cid}' is type '{actual_type}', expected '{expected_type}' for binding '{binding_name}'"))

                # CF-VAL-003 / 004 / 005: Override validation
                if overrides:
                    type_props = set(TYPE_SPECIFIC_REQUIRED.get(actual_type, []))
                    # Also include optional type-specific props
                    optional_props = set()
                    for prop_name in ENUM_VALUES:
                        if prop_name not in type_props:
                            optional_props.add(prop_name)
                    all_valid_props = type_props | optional_props
                    # Add commonly optional props
                    optional_props_map: dict[str, set[str]] = {
                        "scene": {"camera_work"},
                        "voice_style": {"emphasis_pattern", "voice_character"},
                        "visual_direction": {"camera_work", "aspect_ratio"},
                        "audio_mood": {"instrumentation", "volume_balance"},
                        "text_style": {"font_style", "text_animation", "text_color_scheme"},
                    }
                    all_valid_props = all_valid_props | optional_props_map.get(actual_type, set())

                    for key, val in overrides.items():
                        if key not in all_valid_props:
                            findings.append(("CRITICAL", f"CF-VAL-003: Override key '{key}' is not valid for type '{actual_type}'"))
                        # Enum check
                        if key in ENUM_VALUES and str(val) not in ENUM_VALUES[key]:
                            findings.append(("CRITICAL", f"CF-VAL-005: Override '{key}' has invalid enum value '{val}'"))

                # Inventory placeholders from overrides
                for key, val in overrides.items():
                    if isinstance(val, str):
                        for ph_match in PLACEHOLDER_RE.finditer(val):
                            ph_name = ph_match.group(1)
                            all_placeholders[ph_name] = "PENDING"

                # Inventory placeholders from component properties
                comp_props = comp_rec.get("properties", {})
                for prop_key, prop_val in comp_props.items():
                    if isinstance(prop_val, str):
                        for ph_match in PLACEHOLDER_RE.finditer(prop_val):
                            ph_name = ph_match.group(1)
                            all_placeholders[ph_name] = "PENDING"

                resolved_bindings.append({
                    "binding": binding_name,
                    "component_id": cid,
                    "component_type": actual_type,
                    "overrides": dict(overrides) if overrides else {},
                })

        # Check ordering constraints
        scene_count = len(bindings.get("scenes", [])) if isinstance(bindings.get("scenes"), list) else 0
        trans_count = len(bindings.get("transitions", [])) if isinstance(bindings.get("transitions"), list) else 0

        # CF-VAL-010: Scene count 3-8
        if scene_count < 3 or scene_count > 8:
            findings.append(("CRITICAL", f"CF-VAL-010: Scene count {scene_count} is outside the 3-8 range"))

        # CF-VAL-011: Transition count = scene count - 1
        if scene_count > 0 and trans_count != scene_count - 1:
            findings.append(("CRITICAL", f"CF-VAL-011: Transition count {trans_count} does not match scenes count {scene_count} - 1"))

        # Resolve placeholders against data sources
        ds_fields: dict[str, str] = {}
        if ds_dir and ds_dir.is_dir():
            for ds_key in ("product_master", "campaign_input", "platform_config"):
                ds_path_rel = data_sources.get(ds_key, "")
                if ds_path_rel:
                    ds_path = Path(ds_path_rel)
                    if not ds_path.is_absolute():
                        ds_path = ds_dir / ds_path_rel
                    if ds_path.is_file():
                        ds_data = _load_yaml_file(ds_path)
                        if ds_data:
                            for k, v in ds_data.items():
                                if isinstance(v, str) and k not in ds_fields:
                                    ds_fields[k] = v
                    else:
                        findings.append(("MAJOR", f"CF-VAL-009: Data source file not found: {ds_path_rel}"))

        # Assess placeholder resolvability
        placeholder_results: list[dict[str, str]] = []
        for ph_name, _status in sorted(all_placeholders.items()):
            source = "not found"
            resolvability = "UNRESOLVABLE"
            if ph_name in ds_fields:
                source = "data source"
                resolvability = "RESOLVABLE"
            placeholder_results.append({
                "placeholder": ph_name,
                "source": source,
                "status": resolvability,
            })

        # Determine verdict
        critical_count = sum(1 for sev, _ in findings if sev == "CRITICAL")
        major_count = sum(1 for sev, _ in findings if sev == "MAJOR")
        if critical_count > 0:
            verdict = "UNRESOLVABLE"
        elif major_count > 0:
            verdict = "RESOLVABLE_WITH_WARNINGS"
        else:
            verdict = "RESOLVABLE"

        lines.append(f"### Verdict: {verdict}")
        lines.append("")

        if findings:
            lines.append("### Findings")
            lines.append("")
            for sev, msg in findings:
                lines.append(f"- [{sev}] {msg}")
            lines.append("")

        lines.append("### Resolved Bindings")
        lines.append("")
        for rb in resolved_bindings:
            ov_str = ""
            if rb["overrides"]:
                ov_str = f", overrides: {list(rb['overrides'].keys())}"
            lines.append(f"- {rb['binding']}: {rb['component_id']} ({rb['component_type']}{ov_str})")
        lines.append("")

        if placeholder_results:
            lines.append("### Placeholder Inventory")
            lines.append("")
            lines.append("| Placeholder | Source | Status |")
            lines.append("|---|---|---|")
            for pr in placeholder_results:
                lines.append(f"| {pr['placeholder']} | {pr['source']} | {pr['status']} |")
            lines.append("")

        lines.append(f"### Constraint Summary")
        lines.append(f"- Scene count: {scene_count}")
        lines.append(f"- Transition count: {trans_count}")
        lines.append(f"- Critical findings: {critical_count}")
        lines.append(f"- Major findings: {major_count}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Write resolution plan
    plan_path = Path(context["RESOLUTION_PLAN_FILE"])
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text("\n".join(lines), encoding="utf-8")

    return ActionResult(
        status="APPROVED",
        remark=f"Resolved {len(yaml_files)} composition(s) against {len(comp_map)} component(s).",
        artifacts={
            "RESOLUTION_PLAN_FILE": str(plan_path),
        },
    )
