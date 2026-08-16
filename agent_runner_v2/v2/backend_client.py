"""V2 Backend API client for the new state-machine backend.

Architecture reference:
    docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260801-002_platform-v2-architecture-redesign.md

Speaks the V2 API protocol:
- Claim returns work_type (EXECUTE_STEP | PROCESS_ACTION | IDLE)
- Outcome reports are outcome-only (backend computes routing)
- Actions use action_requested field (no __run_control flags)
- Heartbeat returns commands (e.g., ["shutdown"])
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request


@dataclass
class V2BackendClient:
    """HTTP client for the V2 backend API."""

    base_url: str
    timeout_seconds: int = 30
    api_key: str | None = None

    def _url(self, path: str, query: dict[str, str] | None = None) -> str:
        base = self.base_url.rstrip("/")
        url = f"{base}{path}"
        if query:
            url = f"{url}?{parse.urlencode(query)}"
        return url

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        data = None
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = request.Request(
            self._url(path, query=query), data=data, headers=headers, method=method,
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                body = resp.read().decode("utf-8")
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"V2 backend request failed: {method} {path} "
                f"status={exc.code} body={body[:500]}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                f"V2 backend request failed: {method} {path} error={exc}"
            ) from exc
        if not body.strip():
            return {}
        return json.loads(body)

    # ------------------------------------------------------------------
    # Worker endpoints
    # ------------------------------------------------------------------

    def register_worker(
        self,
        *,
        worker_id: str,
        worker_label: str = "live",
        capabilities: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request("POST", "/api/workers/register", {
            "worker_id": worker_id,
            "worker_label": worker_label,
            "capabilities": capabilities or {},
        })

    def get_worker(
        self,
        *,
        worker_id: str,
    ) -> dict[str, Any]:
        """Fetch worker details including status. Returns worker dict or raises if not found."""
        return self._request("GET", f"/api/workers/{worker_id}")

    def heartbeat(
        self,
        *,
        worker_id: str,
        status: str = "idle",
        current_run_id: str | None = None,
        current_step_run_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"status": status}
        if current_run_id:
            payload["current_run_id"] = current_run_id
        if current_step_run_id:
            payload["current_step_run_id"] = current_step_run_id
        return self._request("POST", f"/api/workers/{worker_id}/heartbeat", payload)

    def claim_work(self, *, worker_id: str) -> dict[str, Any]:
        """Claim next available work. Returns work_type + run/step details."""
        return self._request("POST", f"/api/workers/{worker_id}/claim")

    def stop_worker(self, *, worker_id: str) -> dict[str, Any]:
        return self._request("POST", f"/api/workers/{worker_id}/stop")

    # ------------------------------------------------------------------
    # Run endpoints
    # ------------------------------------------------------------------

    def get_run(self, *, run_id: str) -> dict[str, Any]:
        return self._request("GET", f"/api/runs/{run_id}")

    def list_runs(
        self,
        *,
        status: str | None = None,
        worker_id: str | None = None,
    ) -> dict[str, Any]:
        query: dict[str, str] = {}
        if status:
            query["status"] = status
        if worker_id:
            query["worker_id"] = worker_id
        return self._request("GET", "/api/runs", query=query)

    def request_action(
        self,
        *,
        run_id: str,
        action: str,
        feedback: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"action": action, "force": force}
        if feedback:
            payload["feedback"] = feedback
        return self._request("POST", f"/api/runs/{run_id}/action", payload)

    def reset_step(self, *, run_id: str, step_name: str) -> dict[str, Any]:
        return self._request("POST", f"/api/runs/{run_id}/reset-step", {
            "step_name": step_name,
        })

    # ------------------------------------------------------------------
    # Outcome reporting (the key V2 endpoint)
    # ------------------------------------------------------------------

    def report_outcome(
        self,
        *,
        step_run_id: str,
        outcome: str,
        failure_class: str | None = None,
        artifacts: dict[str, str] | None = None,
        review: dict[str, Any] | None = None,
        error_message: str | None = None,
        usage_summary: dict[str, Any] | None = None,
        job_dir: str | None = None,
    ) -> dict[str, Any]:
        """Report step outcome — backend computes next state via state machine."""
        payload: dict[str, Any] = {"outcome": outcome}
        if failure_class:
            payload["failure_class"] = failure_class
        if artifacts:
            payload["artifacts"] = artifacts
        if review:
            payload["review"] = review
        if error_message:
            payload["error_message"] = error_message
        if usage_summary:
            payload["usage_summary"] = usage_summary
        if job_dir:
            payload["job_dir"] = job_dir
        return self._request("POST", f"/api/runs/step-runs/{step_run_id}/outcome", payload)

    # ------------------------------------------------------------------
    # Workflow sync
    # ------------------------------------------------------------------

    def sync_workflow(
        self,
        *,
        workflow_name: str,
        definition: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request("POST", "/api/workflows/sync", {
            "workflow_name": workflow_name,
            "definition": definition,
        })
