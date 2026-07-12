from __future__ import annotations

from agent_runner_v2 import run_agent as run_agent_module


def test_run_agent_exposes_required_extracted_runtime_hooks() -> None:
    required_hooks = {
        "shared_utils": {
            "_safe_relative_to",
            "_save_text",
            "_save_json",
            "_now_iso",
            "_print_failure",
            "_step_progress_parts",
            "_step_progress_label",
            "_format_job_status_summary",
            "_mark_review_started",
        },
        "workflow_runtime": {
            "_ensure_delivery_folders",
            "_load_group",
            "_validate_static_reference_files",
            "_missing_artifacts",
            "_parse_key_value_pairs",
            "load_workflow_package",
            "bundle_to_template_group_dict",
            "known_artifact_paths",
            "legacy_artifact_paths",
            "get_master_docs_output_paths",
        },
        "step_execution_runtime": {
            "_prepare_step_execution",
            "_augment_generated_doc_prompt",
            "_generated_doc_frontmatter_contract",
            "_master_bootstrap_frontmatter_rows",
            "_execute_prepared_step",
            "_resolve_step_coder",
            "make_step_dir",
        },
        "backend_execution": {
            "_execute_step_command",
            "_build_group_cfg_from_execution_spec",
            "_resolve_worker_engine_root",
            "_worker_command",
            "_build_worker_request_payload",
            "_invoke_execute_step_subprocess",
            "_job_json_path",
            "_write_backend_job_json",
            "_submit_worker_result",
            "_finalize_worker_completion",
            "_build_execution_state",
            "_publish_backend_artifacts",
            "_execute_backend_step_request",
            "_build_worker_crash_result",
        },
    }

    missing: dict[str, list[str]] = {}
    for group_name, names in required_hooks.items():
        absent = sorted(name for name in names if not hasattr(run_agent_module, name))
        if absent:
            missing[group_name] = absent

    assert missing == {}
