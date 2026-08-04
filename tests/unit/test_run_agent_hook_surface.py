from __future__ import annotations

from pathlib import Path
import re

from agent_runner_v2 import manual_runtime_deps, run_agent, shared_runtime_deps


def test_runtime_dependency_modules_expose_required_symbols() -> None:
    required_hooks = {
        "shared_runtime_deps": {
            "_ensure_delivery_folders",
            "_load_group",
            "_validate_static_reference_files",
            "_missing_artifacts",
            "_prepare_step_execution",
            "_execute_prepared_step",
            "_resolve_step_coder",
            "_build_group_cfg_from_execution_spec",
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


def test_run_agent_manual_prepare_uses_effective_root_not_undefined_project_root() -> None:
    source = Path("agent_runner_v2/run_agent.py").read_text(encoding="utf-8")

    match = re.search(r"prepared = _prepare_step_execution\((.*?)\n        \)", source, re.DOTALL)
    assert match is not None
    assert "project_root=effective_root" in match.group(1)


def test_manual_runtime_deps_missing_artifacts_matches_direct_workflow_runtime_contract(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_missing_artifacts(keys, state):
        captured["keys"] = keys
        captured["state"] = state
        return ["X"]

    monkeypatch.setattr(manual_runtime_deps._workflow_runtime, "missing_artifacts", fake_missing_artifacts)

    state = {"artifacts": {}}
    result = manual_runtime_deps._missing_artifacts(["X"], state)

    assert result == ["X"]
    assert captured == {"keys": ["X"], "state": state}


def test_manual_runtime_deps_format_job_status_summary_matches_direct_contract(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_format_job_status_summary(state, group_cfg, *, get_job_status):
        captured["state"] = state
        captured["group_cfg"] = group_cfg
        captured["get_job_status"] = get_job_status
        return "summary"

    monkeypatch.setattr(manual_runtime_deps, "format_job_status_summary", fake_format_job_status_summary)

    state = {"job_status": "IN_PROGRESS"}
    group_cfg = {"steps": ["a"]}
    result = manual_runtime_deps._format_job_status_summary(state, group_cfg)

    assert result == "summary"
    assert captured["state"] is state
    assert captured["group_cfg"] is group_cfg
    assert captured["get_job_status"] is manual_runtime_deps.get_job_status


def test_shared_runtime_deps_workflow_runtime_wrappers_match_direct_contract(monkeypatch, tmp_path) -> None:
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def fake_ensure_delivery_folders(target_root):
        calls.append(("ensure_delivery_folders", (target_root,), {}))

    def fake_load_group(group_name, *, workspace_root=None, workflow_root=None):
        calls.append(("load_group", (group_name,), {"workspace_root": workspace_root, "workflow_root": workflow_root}))
        return {"group": group_name}

    def fake_validate_static_reference_files(workspace_root, *, group_cfg=None, template_group=""):
        calls.append(("validate_static_reference_files", (workspace_root,), {"group_cfg": group_cfg, "template_group": template_group}))

    def fake_missing_artifacts(keys, state):
        calls.append(("missing_artifacts", (keys, state), {}))
        return ["Y"]

    monkeypatch.setattr(shared_runtime_deps._workflow_runtime, "ensure_delivery_folders", fake_ensure_delivery_folders)
    monkeypatch.setattr(shared_runtime_deps._workflow_runtime, "load_group", fake_load_group)
    monkeypatch.setattr(shared_runtime_deps._workflow_runtime, "validate_static_reference_files", fake_validate_static_reference_files)
    monkeypatch.setattr(shared_runtime_deps._workflow_runtime, "missing_artifacts", fake_missing_artifacts)

    workspace_root = tmp_path / "workspace"
    workflow_root = tmp_path / "workflow"
    group_cfg = {"steps": []}
    state = {"artifacts": {}}

    shared_runtime_deps._ensure_delivery_folders(workspace_root)
    group = shared_runtime_deps._load_group("demo", workspace_root=workspace_root, workflow_root=workflow_root)
    shared_runtime_deps._validate_static_reference_files(workspace_root, group_cfg=group_cfg, template_group="demo")
    missing = shared_runtime_deps._missing_artifacts(["Y"], state)

    assert group == {"group": "demo"}
    assert missing == ["Y"]
    assert calls == [
        ("ensure_delivery_folders", (workspace_root,), {}),
        ("load_group", ("demo",), {"workspace_root": workspace_root, "workflow_root": workflow_root}),
        ("validate_static_reference_files", (workspace_root,), {"group_cfg": group_cfg, "template_group": "demo"}),
        ("missing_artifacts", (["Y"], state), {}),
    ]


def test_run_agent_workflow_runtime_wrappers_match_direct_contract(monkeypatch, tmp_path) -> None:
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def fake_ensure_delivery_folders(target_root):
        calls.append(("ensure_delivery_folders", (target_root,), {}))

    def fake_load_group(group_name, *, workspace_root=None, workflow_root=None):
        calls.append(("load_group", (group_name,), {"workspace_root": workspace_root, "workflow_root": workflow_root}))
        return {"group": group_name}

    def fake_validate_static_reference_files(workspace_root, *, group_cfg=None, template_group=""):
        calls.append(("validate_static_reference_files", (workspace_root,), {"group_cfg": group_cfg, "template_group": template_group}))

    def fake_missing_artifacts(keys, state):
        calls.append(("missing_artifacts", (keys, state), {}))
        return ["Z"]

    monkeypatch.setattr(run_agent._workflow_runtime, "ensure_delivery_folders", fake_ensure_delivery_folders)
    monkeypatch.setattr(run_agent._workflow_runtime, "load_group", fake_load_group)
    monkeypatch.setattr(run_agent._workflow_runtime, "validate_static_reference_files", fake_validate_static_reference_files)
    monkeypatch.setattr(run_agent._workflow_runtime, "missing_artifacts", fake_missing_artifacts)

    workspace_root = tmp_path / "workspace"
    workflow_root = tmp_path / "workflow"
    group_cfg = {"steps": []}
    state = {"artifacts": {}}

    run_agent._ensure_delivery_folders(workspace_root)
    group = run_agent._load_group("demo", workspace_root=workspace_root, workflow_root=workflow_root)
    run_agent._validate_static_reference_files(workspace_root, group_cfg=group_cfg, template_group="demo")
    missing = run_agent._missing_artifacts(["Z"], state)

    assert group == {"group": "demo"}
    assert missing == ["Z"]
    assert calls == [
        ("ensure_delivery_folders", (workspace_root,), {}),
        ("load_group", ("demo",), {"workspace_root": workspace_root, "workflow_root": workflow_root}),
        ("validate_static_reference_files", (workspace_root,), {"group_cfg": group_cfg, "template_group": "demo"}),
        ("missing_artifacts", (["Z"], state), {}),
    ]


def test_shared_runtime_deps_resolve_step_coder_matches_direct_contract(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_resolve_step_coder(*, group_cfg, state, step, step_cfg, cli_coder):
        captured.update({
            "group_cfg": group_cfg,
            "state": state,
            "step": step,
            "step_cfg": step_cfg,
            "cli_coder": cli_coder,
        })
        return ("claude", None, None, {"model": "x"})

    monkeypatch.setattr(shared_runtime_deps._step_execution_runtime, "resolve_step_coder", fake_resolve_step_coder)

    group_cfg = {"steps": ["a"]}
    state = {"step_coders": {}}
    step_cfg = {"coder": {"default": "claude"}}
    result = shared_runtime_deps._resolve_step_coder(
        group_cfg=group_cfg,
        state=state,
        step="a",
        step_cfg=step_cfg,
        cli_coder=None,
    )

    assert result == ("claude", None, None, {"model": "x"})
    assert captured == {
        "group_cfg": group_cfg,
        "state": state,
        "step": "a",
        "step_cfg": step_cfg,
        "cli_coder": None,
    }


def test_shared_runtime_deps_prepare_and_execute_step_wrappers_keep_adapter_contract(monkeypatch, tmp_path) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_prepare_step_execution(*, template_group, group_cfg, state, step, step_cfg, project_root, workflow_key_override="", cli_coder=None, hooks):
        calls.append(("prepare", {
            "template_group": template_group,
            "group_cfg": group_cfg,
            "state": state,
            "step": step,
            "step_cfg": step_cfg,
            "project_root": project_root,
            "workflow_key_override": workflow_key_override,
            "cli_coder": cli_coder,
            "hooks": hooks,
        }))
        return "prepared"

    def fake_execute_prepared_step(*, prepared, template_group, group_cfg, state, step, step_cfg, effective_root, hooks):
        calls.append(("execute", {
            "prepared": prepared,
            "template_group": template_group,
            "group_cfg": group_cfg,
            "state": state,
            "step": step,
            "step_cfg": step_cfg,
            "effective_root": effective_root,
            "hooks": hooks,
        }))
        return "executed"

    monkeypatch.setattr(shared_runtime_deps._step_execution_runtime, "prepare_step_execution", fake_prepare_step_execution)
    monkeypatch.setattr(shared_runtime_deps._step_execution_runtime, "execute_prepared_step", fake_execute_prepared_step)

    group_cfg = {"steps": ["a"]}
    state = {"job_id": "J"}
    step_cfg = {"produces": ["A"]}
    effective_root = tmp_path / "workspace"

    prepared = shared_runtime_deps._prepare_step_execution(
        template_group="tg",
        group_cfg=group_cfg,
        state=state,
        step="a",
        step_cfg=step_cfg,
        project_root=effective_root,
        workflow_key_override="override",
        cli_coder="claude",
    )
    executed = shared_runtime_deps._execute_prepared_step(
        prepared=prepared,
        template_group="tg",
        group_cfg=group_cfg,
        state=state,
        step="a",
        step_cfg=step_cfg,
        effective_root=effective_root,
    )

    assert prepared == "prepared"
    assert executed == "executed"
    assert calls == [
        ("prepare", {
            "template_group": "tg",
            "group_cfg": group_cfg,
            "state": state,
            "step": "a",
            "step_cfg": step_cfg,
            "project_root": effective_root,
            "workflow_key_override": "override",
            "cli_coder": "claude",
            "hooks": shared_runtime_deps,
        }),
        ("execute", {
            "prepared": "prepared",
            "template_group": "tg",
            "group_cfg": group_cfg,
            "state": state,
            "step": "a",
            "step_cfg": step_cfg,
            "effective_root": effective_root,
            "hooks": shared_runtime_deps,
        }),
    ]


def test_run_agent_step_execution_runtime_wrappers_match_direct_contract(monkeypatch) -> None:
    calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []

    def fake_augment_generated_doc_prompt(template_text, *, template_group, step, step_cfg, state):
        calls.append(("augment_generated_doc_prompt", (template_text,), {
            "template_group": template_group,
            "step": step,
            "step_cfg": step_cfg,
            "state": state,
        }))
        return "augmented"

    def fake_generated_doc_frontmatter_contract(*, template_group, step, step_cfg, state):
        calls.append(("generated_doc_frontmatter_contract", (), {
            "template_group": template_group,
            "step": step,
            "step_cfg": step_cfg,
            "state": state,
        }))
        return "contract"

    def fake_master_bootstrap_frontmatter_rows(*, template_group, step_cfg, state):
        calls.append(("master_bootstrap_frontmatter_rows", (), {
            "template_group": template_group,
            "step_cfg": step_cfg,
            "state": state,
        }))
        return [("docs/a.md", "SYS-1", "system")]

    def fake_resolve_step_coder(*, group_cfg, state, step, step_cfg, cli_coder):
        calls.append(("resolve_step_coder", (), {
            "group_cfg": group_cfg,
            "state": state,
            "step": step,
            "step_cfg": step_cfg,
            "cli_coder": cli_coder,
        }))
        return ("claude", None, None, {"model": "x"})

    monkeypatch.setattr(run_agent._step_execution_runtime, "augment_generated_doc_prompt", fake_augment_generated_doc_prompt)
    monkeypatch.setattr(run_agent._step_execution_runtime, "generated_doc_frontmatter_contract", fake_generated_doc_frontmatter_contract)
    monkeypatch.setattr(run_agent._step_execution_runtime, "master_bootstrap_frontmatter_rows", fake_master_bootstrap_frontmatter_rows)
    monkeypatch.setattr(run_agent._step_execution_runtime, "resolve_step_coder", fake_resolve_step_coder)

    step_cfg = {"produces": ["A"]}
    state = {"job_id": "J"}
    group_cfg = {"steps": ["a"]}

    augmented = run_agent._augment_generated_doc_prompt(
        "base",
        template_group="tg",
        step="a",
        step_cfg=step_cfg,
        state=state,
    )
    contract = run_agent._generated_doc_frontmatter_contract(
        template_group="tg",
        step="a",
        step_cfg=step_cfg,
        state=state,
    )
    rows = run_agent._master_bootstrap_frontmatter_rows(template_group="tg", step_cfg=step_cfg, state=state)
    coder = run_agent._resolve_step_coder(
        group_cfg=group_cfg,
        state=state,
        step="a",
        step_cfg=step_cfg,
        cli_coder=None,
    )

    assert augmented == "augmented"
    assert contract == "contract"
    assert rows == [("docs/a.md", "SYS-1", "system")]
    assert coder == ("claude", None, None, {"model": "x"})
    assert calls == [
        ("augment_generated_doc_prompt", ("base",), {"template_group": "tg", "step": "a", "step_cfg": step_cfg, "state": state}),
        ("generated_doc_frontmatter_contract", (), {"template_group": "tg", "step": "a", "step_cfg": step_cfg, "state": state}),
        ("master_bootstrap_frontmatter_rows", (), {"template_group": "tg", "step_cfg": step_cfg, "state": state}),
        ("resolve_step_coder", (), {"group_cfg": group_cfg, "state": state, "step": "a", "step_cfg": step_cfg, "cli_coder": None}),
    ]


def test_run_agent_prepare_and_execute_step_wrappers_keep_adapter_contract(monkeypatch, tmp_path) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def fake_prepare_step_execution(*, template_group, group_cfg, state, step, step_cfg, project_root, workflow_key_override="", cli_coder=None, hooks):
        calls.append(("prepare", {
            "template_group": template_group,
            "group_cfg": group_cfg,
            "state": state,
            "step": step,
            "step_cfg": step_cfg,
            "project_root": project_root,
            "workflow_key_override": workflow_key_override,
            "cli_coder": cli_coder,
            "hooks": hooks,
        }))
        return "prepared"

    def fake_execute_prepared_step(*, prepared, template_group, group_cfg, state, step, step_cfg, effective_root, hooks):
        calls.append(("execute", {
            "prepared": prepared,
            "template_group": template_group,
            "group_cfg": group_cfg,
            "state": state,
            "step": step,
            "step_cfg": step_cfg,
            "effective_root": effective_root,
            "hooks": hooks,
        }))
        return "executed"

    monkeypatch.setattr(run_agent._step_execution_runtime, "prepare_step_execution", fake_prepare_step_execution)
    monkeypatch.setattr(run_agent._step_execution_runtime, "execute_prepared_step", fake_execute_prepared_step)

    group_cfg = {"steps": ["a"]}
    state = {"job_id": "J"}
    step_cfg = {"produces": ["A"]}
    effective_root = tmp_path / "workspace"

    prepared = run_agent._prepare_step_execution(
        template_group="tg",
        group_cfg=group_cfg,
        state=state,
        step="a",
        step_cfg=step_cfg,
        project_root=effective_root,
        workflow_key_override="override",
        cli_coder="claude",
    )
    executed = run_agent._execute_prepared_step(
        prepared=prepared,
        template_group="tg",
        group_cfg=group_cfg,
        state=state,
        step="a",
        step_cfg=step_cfg,
        effective_root=effective_root,
    )

    assert prepared == "prepared"
    assert executed == "executed"
    assert calls == [
        ("prepare", {
            "template_group": "tg",
            "group_cfg": group_cfg,
            "state": state,
            "step": "a",
            "step_cfg": step_cfg,
            "project_root": effective_root,
            "workflow_key_override": "override",
            "cli_coder": "claude",
            "hooks": run_agent._shared_runtime_deps,
        }),
        ("execute", {
            "prepared": "prepared",
            "template_group": "tg",
            "group_cfg": group_cfg,
            "state": state,
            "step": "a",
            "step_cfg": step_cfg,
            "effective_root": effective_root,
            "hooks": run_agent._shared_runtime_deps,
        }),
    ]
