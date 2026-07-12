from __future__ import annotations

from pathlib import Path

from agent_runner_v2 import task_runtime


def test_build_task_execution_binding_reads_plan_and_task_graph_metadata(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(task_runtime, "PROJECT_ROOT", tmp_path)

    plans_dir = tmp_path / "docs" / "delivery" / "02_plans"
    artifacts_dir = plans_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    plan_path = plans_dir / "PLAN-20260712-01_example.md"
    plan_path.write_text(
        "\n".join(
            [
                "---",
                "title: Example Plan",
                "---",
                "Status: approved",
                "- Plan ID: PLAN-20260712-01",
            ]
        ),
        encoding="utf-8",
    )

    task_graph_path = artifacts_dir / "TASK-GRAPH-20260712-PLAN-20260712-01.md"
    task_graph_path.write_text(
        "\n".join(
            [
                "---",
                "title: Example Task Graph",
                "---",
                "Status: approved",
                "- Task Graph ID: TG-20260712-01",
                "- Plan ID: PLAN-20260712-01",
                "",
                "### `TASK-20260712-01` - First task",
                "body",
                "",
                "### `TASK-20260712-02` - Second task",
                "body",
            ]
        ),
        encoding="utf-8",
    )

    binding = task_runtime.build_task_execution_binding(
        task_graph_file="docs/delivery/02_plans/artifacts/TASK-GRAPH-20260712-PLAN-20260712-01.md",
        task_node_id="TASK-20260712-02",
    )

    assert binding["task_graph_id"] == "TG-20260712-01"
    assert binding["plan_id"] == "PLAN-20260712-01"
    assert str(binding["plan_file"]).replace("\\", "/") == "docs/delivery/02_plans/PLAN-20260712-01_example.md"
    assert binding["task_node_id"] == "TASK-20260712-02"
    assert binding["task_title"] == "Second task"
    assert binding["task_node_snapshot"] == {
        "task_node_id": "TASK-20260712-02",
        "title": "Second task",
        "sequence": 2,
    }
