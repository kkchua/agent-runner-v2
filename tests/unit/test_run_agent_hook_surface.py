from __future__ import annotations

from pathlib import Path

from agent_runner_v2 import manual_runtime_deps, shared_runtime_deps


def test_runtime_dependency_modules_expose_required_symbols() -> None:
    required_hooks = {
        "shared_runtime_deps": {
            "_ensure_delivery_folders",
            "_load_group",
            "_validate_static_reference_files",
            "_missing_artifacts",
            "load_workflow_package",
            "bundle_to_template_group_dict",
            "known_artifact_paths",
            "legacy_artifact_paths",
            "get_master_docs_output_paths",
            "_prepare_step_execution",
            "_execute_prepared_step",
            "_resolve_step_coder",
            "_build_group_cfg_from_execution_spec",
            "_resolve_worker_engine_root",
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
        "manual_runtime_deps": {
            "_missing_artifacts",
            "_parse_key_value_pairs",
            "_step_progress_label",
            "_format_job_status_summary",
            "_reset_loop_context",
            "_reset_replan_context",
        },
    }

    modules = {
        "shared_runtime_deps": shared_runtime_deps,
        "manual_runtime_deps": manual_runtime_deps,
    }

    missing: dict[str, list[str]] = {}
    for group_name, names in required_hooks.items():
        absent = sorted(name for name in names if not hasattr(modules[group_name], name))
        if absent:
            missing[group_name] = absent

    assert missing == {}


def test_run_agent_no_longer_uses_module_self_hook_injection() -> None:
    source = Path("agent_runner_v2/run_agent.py").read_text(encoding="utf-8")

    assert "sys.modules[__name__]" not in source
