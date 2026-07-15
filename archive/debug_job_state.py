#!/usr/bin/env python3
"""
Diagnostic script to examine job state and trace routing decisions.

This script will:
1. Load the failed job state
2. Show the retry_history to understand what happened at each step
3. Check if loop_context was active when step 05 completed
4. Examine the actual routing decision that was made
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

JOB_PATH = Path(r"C:\Users\kengk\.ukbe-runner\jobs\00_master_docs_bootstrap_v2\00DOC-20260711-919e2580\job.json")


def analyze_job_state() -> None:
    """Analyze the job state to understand the routing failure."""
    
    print("=" * 80)
    print("JOB STATE ROUTING ANALYSIS")
    print("=" * 80)
    print()
    
    if not JOB_PATH.exists():
        print(f"❌ Job file not found: {JOB_PATH}")
        return
    
    with open(JOB_PATH, 'r', encoding='utf-8') as f:
        job = json.load(f)
    
    print(f"📋 Job Overview:")
    print(f"   Run Code: {job.get('run_code')}")
    print(f"   Workflow: {job.get('workflow_name')}")
    print(f"   Status: {job.get('status')}")
    print(f"   Current Step: {job.get('current_step_name')}")
    print(f"   Error Message: {job.get('error_message')}")
    print()
    
    # Check artifacts
    artifacts = job.get('artifacts', {})
    print(f"📦 Artifacts ({len(artifacts)} total):")
    if 'REVIEW_FILE_SUGGESTED' in artifacts:
        print(f"   ✅ REVIEW_FILE_SUGGESTED: {artifacts['REVIEW_FILE_SUGGESTED']}")
    else:
        print(f"   ❌ REVIEW_FILE_SUGGESTED: NOT FOUND")
    print()
    
    # Check for loop_context (this would indicate an active refine loop)
    loop_context = job.get('loop_context')
    print(f"🔄 Loop Context:")
    if loop_context:
        print(f"   Active: {loop_context.get('active')}")
        print(f"   Loop Step: {loop_context.get('loop_step')}")
        print(f"   Refine Step: {loop_context.get('refine_step')}")
        print(f"   Iteration: {loop_context.get('loop_iteration')}")
        print(f"   Target Artifact: {loop_context.get('loop_target_artifact')}")
    else:
        print(f"   Not present (no active loop)")
    print()
    
    # Check retry_history to see what happened at each step
    retry_history = job.get('retry_history', [])
    print(f"📜 Retry History ({len(retry_history)} entries):")
    print()
    
    for i, entry in enumerate(retry_history, 1):
        step = entry.get('step')
        status = entry.get('result_status')
        remark = entry.get('result_remark', '')[:100]
        reject_code = entry.get('reject_code')
        
        marker = "✅" if status == "APPROVED" else "❌" if status == "FAILED" else "⚠️"
        
        print(f"{i}. {marker} Step: {step}")
        print(f"   Status: {status}")
        if reject_code:
            print(f"   Reject Code: {reject_code}")
        if remark:
            print(f"   Remark: {remark}...")
        print()
    
    # Find step 05 entry specifically
    step_05_entries = [e for e in retry_history if e.get('step') == '05_review_master_system_docs']
    if step_05_entries:
        print("=" * 80)
        print("STEP 05 EXECUTION DETAILS")
        print("=" * 80)
        print()
        
        last_05 = step_05_entries[-1]
        print(f"Status: {last_05.get('result_status')}")
        print(f"Remark: {last_05.get('result_remark', '')[:200]}")
        print(f"Coder Used: {last_05.get('coder_used')}")
        print()
    
    # Check step_coders to see which coder was used for each step
    step_coders = job.get('step_coders', {})
    print(f"👨‍💻 Step Coders:")
    for step_name in ['05_review_master_system_docs', '06_refine_master_system_docs']:
        if step_name in step_coders:
            print(f"   {step_name}: {step_coders[step_name]}")
    print()
    
    # Check completed_steps
    completed_steps = job.get('completed_steps', [])
    print(f"✅ Completed Steps ({len(completed_steps)}):")
    print(f"   {completed_steps}")
    print()
    
    # Check model_approved_steps
    approved_steps = job.get('model_approved_steps', [])
    print(f"✓ Model Approved Steps ({len(approved_steps)}):")
    print(f"   {approved_steps}")
    print()
    
    # Check review_state if present
    review_state = job.get('review_state')
    if review_state:
        print(f"🔍 Review State:")
        for key, value in review_state.items():
            print(f"   {key}: {value}")
        print()
    
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    
    # Provide diagnosis
    print("🎯 DIAGNOSIS:")
    print()
    
    if not loop_context or not loop_context.get('active'):
        print("✅ No active loop context when job failed")
        print("   This means step 05 should have advanced normally via onsuccess")
    else:
        print("❌ Active loop context detected!")
        print(f"   Loop was targeting: {loop_context.get('refine_step')}")
        print("   This would override normal onsuccess routing")
    print()
    
    if 'REVIEW_FILE_SUGGESTED' in artifacts:
        print("✅ REVIEW_FILE_SUGGESTED artifact exists in job state")
        print("   Step 06 should have been able to access it")
    else:
        print("❌ REVIEW_FILE_SUGGESTED artifact MISSING from job state")
        print("   This explains why step 06 failed with 'Missing required input artifact'")
    print()
    
    if step_05_entries and step_05_entries[-1].get('result_status') == 'APPROVED':
        print("✅ Step 05 returned APPROVED status")
        print("   Router should have called advance_step() with onsuccess='07_validate_codebase_baseline'")
    print()


if __name__ == "__main__":
    analyze_job_state()
