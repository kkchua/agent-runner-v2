from __future__ import annotations

from typing import Any

from ...backend_client import BackendClient
from ..models import ActiveRunSummary


class BackendRunService:
    def __init__(self, client: BackendClient, *, worker_id: str):
        self.client = client
        self.worker_id = worker_id

    def list_active_runs(self, *, repo_path: str, workflow_name: str | None = None) -> list[ActiveRunSummary]:
        payload = self.client.list_runs(
            repo_path=repo_path,
            workflow_name=workflow_name,
            status_group="non_terminal",
            worker_id=self.worker_id,
        )
        items = payload if isinstance(payload, list) else payload.get("runs") or payload.get("items") or []
        results: list[ActiveRunSummary] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            results.append(_coerce_run(item))
        return results

    def stop_run(self, *, run_id: str, reason: str = "") -> dict[str, Any]:
        return self.client.stop_run(run_id=run_id, reason=reason or None, mode="after_current_step")

    def approve_run(self, *, run_id: str, reject: bool = False, feedback: str = "") -> dict[str, Any]:
        return self.client.approve_run(
            run_id=run_id,
            action="reject" if reject else "approve",
            feedback=feedback or None,
        )

    def get_run_detail(self, *, run_id: str) -> dict[str, Any]:
        return self.client.get_run(run_id=run_id)

    def reset_run_step(self, *, run_id: str, step_name: str) -> dict[str, Any]:
        return self.client.reset_run_step(run_id=run_id, step_name=step_name)


def _coerce_run(item: dict[str, Any]) -> ActiveRunSummary:
    current_step = (
        str(item.get("current_step") or "").strip()
        or str(item.get("current_step_name") or "").strip()
    )
    return ActiveRunSummary(
        run_id=str(item.get("id") or item.get("run_id") or "").strip(),
        run_code=str(item.get("run_code") or item.get("job_id") or "").strip(),
        workflow_name=str(item.get("workflow_name") or item.get("template_group") or "").strip(),
        status=str(item.get("status") or item.get("job_status") or "").strip(),
        current_step=current_step,
        updated_at=str(item.get("updated_at") or item.get("modified_at") or "").strip(),
    )
