from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import error, parse, request


@dataclass
class BackendClient:
    base_url: str
    timeout_seconds: int = 30

    def _url(self, path: str, query: dict[str, str] | None = None) -> str:
        base = self.base_url.rstrip('/')
        url = f"{base}{path}"
        if query:
            url = f"{url}?{parse.urlencode(query)}"
        return url

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None, query: dict[str, str] | None = None) -> dict[str, Any]:
        data = None
        headers = {'Accept': 'application/json'}
        if payload is not None:
            data = json.dumps(payload).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        req = request.Request(self._url(path, query=query), data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as resp:
                body = resp.read().decode('utf-8')
        except error.HTTPError as exc:
            body = exc.read().decode('utf-8', errors='replace')
            raise RuntimeError(f'Backend request failed: {method} {path} status={exc.code} body={body[:500]}') from exc
        except error.URLError as exc:
            raise RuntimeError(f'Backend request failed: {method} {path} error={exc}') from exc
        if not body.strip():
            return {}
        return json.loads(body)

    def submit_run(
        self,
        *,
        workflow_name: str,
        initiative_id: str | None = None,
        target_worker_id: str | None = None,
        assigned_provider: str | None = None,
        coder_override: str | None = None,
        project_root: str | None = None,
        target_project_root: str | None = None,
        workspace_path: str | None = None,
        repo_url: str | None = None,
        repo_ref: str | None = None,
        worker_label: str = "live",
        env_overrides: dict[str, Any] | None = None,
        input_payload: dict[str, Any] | None = None,
        context_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {'workflow_name': workflow_name, 'worker_label': worker_label}
        if initiative_id is not None:
            payload['initiative_id'] = initiative_id
        if target_worker_id is not None:
            payload['target_worker_id'] = target_worker_id
        if assigned_provider is not None:
            payload['assigned_provider'] = assigned_provider
        if coder_override is not None:
            payload['coder_override'] = coder_override
        if project_root is not None:
            payload['project_root'] = project_root
        if target_project_root is not None:
            payload['target_project_root'] = target_project_root
        if workspace_path is not None:
            payload['workspace_path'] = workspace_path
        if repo_url is not None:
            payload['repo_url'] = repo_url
        if repo_ref is not None:
            payload['repo_ref'] = repo_ref
        if env_overrides:
            payload['env_overrides'] = env_overrides
        if input_payload:
            payload['input_payload'] = input_payload
        if context_payload:
            payload['context_payload'] = context_payload
        return self._request('POST', '/api/runs', payload)

    def approve_run(self, *, run_id: str, action: str = "approve", feedback: str | None = None, outcome: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {'action': action}
        if feedback is not None:
            payload['feedback'] = feedback
        if outcome is not None:
            payload['outcome'] = outcome
        return self._request('POST', f'/api/runs/{run_id}/approve', payload)

    def get_run(self, *, run_id: str) -> dict[str, Any]:
        return self._request('GET', f'/api/runs/{run_id}')

    def list_runs(
        self,
        *,
        repo_path: str | None = None,
        workflow_name: str | None = None,
        status_group: str | None = None,
        worker_id: str | None = None,
    ) -> dict[str, Any]:
        query: dict[str, str] = {}
        if repo_path:
            query["repo_path"] = repo_path
        if workflow_name:
            query["workflow_name"] = workflow_name
        if status_group:
            query["status_group"] = status_group
        if worker_id:
            query["worker_id"] = worker_id
        return self._request('GET', '/api/runs', query=query)

    def stop_run(self, *, run_id: str, reason: str | None = None, mode: str = "after_current_step") -> dict[str, Any]:
        payload: dict[str, Any] = {"mode": mode}
        if reason is not None:
            payload["reason"] = reason
        return self._request('POST', f'/api/runs/{run_id}/stop', payload)

    def reset_run_step(self, *, run_id: str, step_name: str) -> dict[str, Any]:
        return self._request('POST', f'/api/runs/{run_id}/reset-step', {"step_name": step_name})

    def register_worker(self, *, worker_id: str, host_name: str | None = None, capabilities: dict[str, Any] | None = None, worker_label: str = "live") -> dict[str, Any]:
        return self._request('POST', '/api/workers/register', {
            'worker_id': worker_id,
            'host_name': host_name,
            'capabilities': capabilities or {},
            'worker_label': worker_label,
        })

    def heartbeat(
        self,
        *,
        worker_id: str,
        status: str | None = None,
        current_step_run_id: str | None = None,
        workflow_run_id: str | None = None,
        workflow_step_run_id: str | None = None,
        run_code: str | None = None,
        pid: int | None = None,
        state: str | None = None,
        log_file: str | None = None,
        watchdog_reason: str | None = None,
        exit_code: int | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {'worker_id': worker_id}
        if status is not None:
            payload['status'] = status
        if current_step_run_id is not None:
            payload['current_step_run_id'] = current_step_run_id
        if workflow_run_id is not None:
            payload['workflow_run_id'] = workflow_run_id
        if workflow_step_run_id is not None:
            payload['workflow_step_run_id'] = workflow_step_run_id
        if run_code is not None:
            payload['run_code'] = run_code
        if pid is not None:
            payload['pid'] = pid
        if state is not None:
            payload['state'] = state
        if log_file is not None:
            payload['log_file'] = log_file
        if watchdog_reason is not None:
            payload['watchdog_reason'] = watchdog_reason
        if exit_code is not None:
            payload['exit_code'] = exit_code
        return self._request('POST', '/api/workers/heartbeat', payload)

    def claim_step(self, *, worker_id: str) -> dict[str, Any]:
        return self._request('POST', '/api/workers/claim', query={'worker_id': worker_id})

    def complete_step_run(self, *, step_run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request('POST', f'/api/step-runs/{step_run_id}/complete', payload)

    def sync_job_state(self, *, step_run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request('POST', f'/api/step-runs/{step_run_id}/job-sync', payload)

    def create_artifact(self, *, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request('POST', f'/api/runs/{run_id}/artifacts', payload)

    def create_event(self, *, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request('POST', f'/api/runs/{run_id}/events', payload)

    def cleanup_execution(self, *, workflow_name: str, dry_run: bool = False) -> dict[str, Any]:
        return self._request('POST', '/api/admin/execution/cleanup', {
            "dry_run": dry_run,
            "include_workers": False,
            "scope": {"workflow_name": workflow_name},
        })
