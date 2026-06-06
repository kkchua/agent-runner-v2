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

    def register_worker(self, *, worker_id: str, host_name: str | None = None, capabilities: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request('POST', '/api/workers/register', {
            'worker_id': worker_id,
            'host_name': host_name,
            'capabilities': capabilities or {},
        })

    def heartbeat(self, *, worker_id: str, status: str | None = None, current_step_run_id: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {'worker_id': worker_id}
        if status is not None:
            payload['status'] = status
        if current_step_run_id is not None:
            payload['current_step_run_id'] = current_step_run_id
        return self._request('POST', '/api/workers/heartbeat', payload)

    def claim_step(self, *, worker_id: str) -> dict[str, Any]:
        return self._request('POST', '/api/workers/claim', query={'worker_id': worker_id})

    def complete_step_run(self, *, step_run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request('POST', f'/api/step-runs/{step_run_id}/complete', payload)

    def create_artifact(self, *, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request('POST', f'/api/runs/{run_id}/artifacts', payload)

    def create_event(self, *, run_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request('POST', f'/api/runs/{run_id}/events', payload)
