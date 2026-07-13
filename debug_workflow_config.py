#!/usr/bin/env python3
"""
Diagnostic script to trace workflow configuration loading at runtime.

This script will:
1. Load the workflow configuration using the same mechanism as run_agent.py
2. Print which source was used (plugin package vs TEMPLATE_GROUPS)
3. Display the step 05 configuration to check for 'onsuccess' field
4. Show the complete step_configs structure for debugging
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add the project root to sys.path so we can import agent_runner_v2 modules
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent_runner_v2.run_agent import _load_group
from agent_runner_v2.bundle_loader import global_workflow_root


def diagnose_workflow_loading(workflow_name: str = "00_master_docs_bootstrap_v2") -> None:
    """Diagnose where workflow config comes from and what it contains."""
    
    print("=" * 80)
    print("WORKFLOW CONFIGURATION DIAGNOSTIC")
    print("=" * 80)
    print()
    
    # Check if plugin workflow exists in global runner home
    from agent_runner_v2.bundle_loader import global_workflows_root
    
    plugin_root = global_workflows_root() / "default" / workflow_name
    plugin_path = plugin_root / "workflow.toml"
    print(f"📁 Checking for plugin workflow at:")
    print(f"   {plugin_path}")
    print(f"   Exists: {plugin_path.exists()}")
    print()
    
    if plugin_path.exists():
        print("✅ Plugin workflow.toml found!")
        print()
        
        # Read and display the relevant section from workflow.toml
        try:
            import tomllib
            raw = plugin_path.read_bytes()
            data = tomllib.loads(raw.decode("utf-8"))
            
            steps = data.get("step", [])
            step_05 = next((s for s in steps if s.get("name") == "05_review_master_system_docs"), None)
            
            if step_05:
                print("📄 Step 05 from workflow.toml:")
                print(f"   onsuccess: {step_05.get('onsuccess', 'NOT DEFINED')}")
                print(f"   Full step config keys: {list(step_05.keys())}")
                print()
        except Exception as e:
            print(f"⚠️  Error reading workflow.toml: {e}")
            print()
    
    print("-" * 80)
    print("Loading workflow configuration via _load_group()...")
    print("-" * 80)
    print()
    
    try:
        # Load using the same mechanism as run_agent.py
        # Provide the global runner home workflows/default as workflow_root
        workflow_root = global_workflows_root() / "default"
        group_cfg = _load_group(workflow_name, workspace_root=PROJECT_ROOT, workflow_root=workflow_root)
        
        print("✅ Workflow configuration loaded successfully!")
        print()
        
        # Check if it came from plugin or TEMPLATE_GROUPS
        has_bundle = "_workflow_bundle" in group_cfg
        source = "PLUGIN PACKAGE" if has_bundle else "TEMPLATE_GROUPS (legacy)"
        print(f"🎯 Configuration source: {source}")
        print()
        
        if has_bundle:
            bundle = group_cfg["_workflow_bundle"]
            print(f"📦 Bundle details:")
            print(f"   Name: {bundle.name}")
            print(f"   Version: {bundle.version}")
            print(f"   Bundle root: {bundle.bundle_root}")
            print(f"   Manifest: {bundle.manifest_path}")
            print()
        
        # Get step configs
        step_configs = group_cfg.get("step_configs", {})
        steps_order = group_cfg.get("steps", [])
        
        print(f"📋 Workflow structure:")
        print(f"   Total steps: {len(steps_order)}")
        print(f"   Steps order: {steps_order}")
        print()
        
        # Find step 05
        step_05_cfg = step_configs.get("05_review_master_system_docs", {})
        
        if step_05_cfg:
            print("=" * 80)
            print("STEP 05 CONFIGURATION ANALYSIS")
            print("=" * 80)
            print()
            
            print(f"🔍 Step 05 keys present: {sorted(step_05_cfg.keys())}")
            print()
            
            # Check for routing fields
            routing_fields = {
                "onsuccess": step_05_cfg.get("onsuccess"),
                "on_reject_refine": bool(step_05_cfg.get("on_reject_refine")),
                "loop_returns_to": step_05_cfg.get("loop_returns_to"),
                "replan_returns_to": step_05_cfg.get("replan_returns_to"),
            }
            
            print("🛤️  Routing configuration:")
            for field, value in routing_fields.items():
                status = "✅ PRESENT" if value else "❌ MISSING"
                print(f"   {field}: {value if isinstance(value, str) else status}")
            print()
            
            if routing_fields["onsuccess"]:
                print(f"✅ SUCCESS: Step 05 has onsuccess = '{routing_fields['onsuccess']}'")
                print(f"   This should route to step: {routing_fields['onsuccess']}")
            else:
                print("❌ PROBLEM: Step 05 is missing 'onsuccess' field!")
                print("   This will cause fallback to automatic step advancement logic.")
            print()
            
            # Show full step config for debugging
            print("📝 Complete step 05 configuration:")
            print(json.dumps(step_05_cfg, indent=2, default=str))
            print()
            
            # Check step 06 as well
            step_06_cfg = step_configs.get("06_refine_master_system_docs", {})
            if step_06_cfg:
                print("-" * 80)
                print("STEP 06 CONFIGURATION (for comparison)")
                print("-" * 80)
                print()
                print(f"🛤️  Step 06 routing:")
                print(f"   loop_returns_to: {step_06_cfg.get('loop_returns_to', 'MISSING')}")
                print(f"   onsuccess: {step_06_cfg.get('onsuccess', 'MISSING')}")
                print()
        
        else:
            print("❌ ERROR: Step 05 not found in step_configs!")
            print()
            print("Available steps:", list(step_configs.keys()))
            print()
        
        # Show all steps with their routing
        print("=" * 80)
        print("ALL STEPS ROUTING SUMMARY")
        print("=" * 80)
        print()
        
        for step_name in steps_order:
            cfg = step_configs.get(step_name, {})
            onsuccess = cfg.get("onsuccess")
            loop = cfg.get("loop_returns_to")
            reject_refine = cfg.get("on_reject_refine", {}).get("step") if cfg.get("on_reject_refine") else None
            
            routing = onsuccess or loop or reject_refine or "NONE"
            marker = "✅" if routing != "NONE" else "❌"
            
            print(f"{marker} {step_name:40s} → {routing}")
        
        print()
        
    except Exception as e:
        print(f"❌ ERROR loading workflow configuration: {e}")
        print()
        import traceback
        traceback.print_exc()
        return
    
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    workflow_name = sys.argv[1] if len(sys.argv) > 1 else "00_master_docs_bootstrap_v2"
    diagnose_workflow_loading(workflow_name)
