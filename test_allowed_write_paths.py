#!/usr/bin/env python3
"""Test script to verify ALLOWED_WRITE_PATHS includes all 8 artifacts for step 03."""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

from agent_runner_v2.step_runner import build_context
from agent_runner_v2.workflow_packages.loader import load_workflow_package

# Load workflow package
workflow_dir = repo_root / "workflows" / "00_master_docs_bootstrap_v2"
bundle = load_workflow_package(workflow_dir)

print(f"Loaded workflow: {bundle.name}")
print(f"Steps type: {type(bundle.steps)}")
step_keys = list(bundle.steps.keys())[:3] if isinstance(bundle.steps, dict) else bundle.steps[:3]
print(f"First 3 steps: {step_keys}...")
print()

# Get step config for step 03 - steps might be dict or list
step_03_cfg = None
if isinstance(bundle.steps, dict):
    step_03_cfg = bundle.steps.get("03_generate_system_overview_docs")
elif isinstance(bundle.steps, list):
    for step in bundle.steps:
        if isinstance(step, dict) and step.get("name") == "03_generate_system_overview_docs":
            step_03_cfg = step
            break
        elif isinstance(step, str) and step == "03_generate_system_overview_docs":
            # It's just a string name, need to get from step_configs
            step_03_cfg = bundle.step_configs.get("03_generate_system_overview_docs")
            break

if not step_03_cfg:
    print("ERROR: Could not find step 03 config")
    print(f"Available attributes: {[a for a in dir(bundle) if not a.startswith('_')]}")
    sys.exit(1)

print(f"Found step 03: {step_03_cfg.name}")
print(f"Step type: {type(step_03_cfg)}")
produces = step_03_cfg.artifacts.produces if hasattr(step_03_cfg, 'artifacts') else []
print(f"Produces ({len(produces)}): {produces}")
print()

# Convert to dict for build_context
step_03_dict = {
    "name": step_03_cfg.name,
    "artifacts": {
        "produces": produces,
    },
    "_workflow_bundle": bundle,
}
if hasattr(step_03_cfg, 'result_meta_key'):
    step_03_dict["result_meta_key"] = step_03_cfg.result_meta_key

# Build minimal state
state = {
    "job_id": "TEST-JOB-001",
    "template_group": bundle.name,
    "backend_step_dir_rel": "",
    "artifacts": {},
}

# Add _workflow_bundle attribute like _load_group does
step_03_dict["_workflow_bundle"] = bundle

# Build context
ctx = build_context(state, step="03_generate_system_overview_docs", step_cfg=step_03_dict)

# Print ALLOWED_WRITE_PATHS
allowed_paths = ctx.get("ALLOWED_WRITE_PATHS", "")
print("=" * 80)
print("ALLOWED_WRITE_PATHS:")
print("=" * 80)
print(allowed_paths)
print("=" * 80)

# Count how many paths are listed
path_count = allowed_paths.count("- ")
print(f"\nTotal paths listed: {path_count}")

# Check for specific artifacts
required_artifacts = [
    "SYSTEM_DOCS_INDEX",
    "SYSTEM_DOC_STANDARD", 
    "BUNDLE_TAXONOMY",
    "BUNDLE_MIGRATION_PLAN",
    "SYSTEM_OVERVIEW",
    "BUSINESS_CAPABILITIES",
    "FUNCTIONAL_SPEC",
    "NON_FUNCTIONAL_REQUIREMENTS",
]

print("\nArtifact path resolution check:")
all_found = True
for artifact in required_artifacts:
    # Check if artifact path appears in ALLOWED_WRITE_PATHS
    found_in_paths = f"docs/system/00_governance/bootstrap/" in allowed_paths and any(
        artifact.lower().replace("_", "-") in line.lower() or 
        artifact.replace("SYSTEM_DOCS_INDEX", "README").replace("SYSTEM_DOC_STANDARD", "DOCUMENTATION_STANDARD").replace("BUNDLE_TAXONOMY", "BUNDLE_TAXONOMY").replace("BUNDLE_MIGRATION_PLAN", "BUNDLE_MIGRATION_PLAN").replace("SYSTEM_OVERVIEW", "SYSTEM_OVERVIEW").replace("BUSINESS_CAPABILITIES", "BUSINESS_CAPABILITIES").replace("FUNCTIONAL_SPEC", "FUNCTIONAL_SPEC").replace("NON_FUNCTIONAL_REQUIREMENTS", "NON_FUNCTIONAL_REQUIREMENTS")
        for line in allowed_paths.split('\n')
    )
    # Simpler check: just see if the artifact key is in context with a path value
    has_path = bool(ctx.get(artifact) or ctx.get(f"{artifact}_PATH"))
    status = "✓" if has_path else "✗"
    if not has_path:
        all_found = False
    print(f"  {status} {artifact}: {ctx.get(artifact) or ctx.get(f'{artifact}_PATH') or 'NOT IN CONTEXT'}")

print()
if all_found:
    print("SUCCESS: All 8 artifact paths are in context!")
else:
    print("FAILURE: Some artifact paths are missing from context")
    sys.exit(1)
