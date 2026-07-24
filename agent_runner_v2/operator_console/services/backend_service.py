from __future__ import annotations

from typing import Any

from ...backend_client import BackendClient
from ..models import ActiveRunSummary


def _extract_runs(payload: dict[str, Any] | list[Any]) -> list[ActiveRunSummary]:
    """Extract ActiveRunSummary objects from a backend runs payload.

    Handles both list and dict responses. Dict payloads may contain
    runs under keys like "runs", "items", or "data".
    """
    items = payload if isinstance(payload, list) else payload.get("runs") or payload.get("items") or payload.get("data") or []
    results: list[ActiveRunSummary] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        results.append(_coerce_run(item))
    return results


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
        worker_id=str(item.get("worker_id") or item.get("target_worker_id") or "").strip(),
    )


class BackendRunService:
    def __init__(self, client: BackendClient, *, worker_id: str):
        self.client = client
        self.worker_id = worker_id

    def list_active_runs(self, *, repo_path: str, workflow_name: str | None = None, worker_id: str | None = None) -> list[ActiveRunSummary]:
        """List non-terminal runs for the specified repo and optional workflow."""
        payload = self.client.list_runs(
            repo_path=repo_path,
            workflow_name=workflow_name,
            status_group="non_terminal",
            worker_id=worker_id or self.worker_id,
        )
        return _extract_runs(payload)

    def list_active_runs_for_worker(self, worker_id: str | None = None) -> list[ActiveRunSummary]:
        """List all non-terminal runs for a worker across all repos and workflows."""
        payload = self.client.list_runs(
            status_group="non_terminal",
            worker_id=worker_id or self.worker_id,
        )
        return _extract_runs(payload)

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
