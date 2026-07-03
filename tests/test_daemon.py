from __future__ import annotations

import json
from pathlib import Path

from agent_runner_v2 import daemon as daemon_module


class DummyProc:
    def __init__(self, poll_values: list[int | None], pid: int = 999):
        self._poll_values = list(poll_values)
        self.pid = pid

    def poll(self):
        if len(self._poll_values) > 1:
            return self._poll_values.pop(0)
        return self._poll_values[0]

    def terminate(self):
        self._poll_values = [0]

    def kill(self):
        self._poll_values = [0]


def test_run_supervisor_spawns_child_and_emits_child_heartbeat(monkeypatch, tmp_path):
    heartbeats: list[dict] = []
    submissions: list[dict] = []
    claims = [
        {
            'run': {'id': 'run-1', 'run_code': 'RUN-1'},
            'step_run': {'id': 'step-1', 'step_name': 'pre_init'},
            'step_execution_spec': {},
        },
        {'step_run': None},
    ]

    class FakeClient:
        def __init__(self, base_url: str):
            self.base_url = base_url

        def register_worker(self, **kwargs):
            return {'ok': True}

        def heartbeat(self, **kwargs):
            heartbeats.append(kwargs)
            return {'ok': True}

        def claim_step(self, *, worker_id: str):
            return claims.pop(0)

        def create_artifact(self, **kwargs):
            return {'ok': True}

        def create_event(self, **kwargs):
            return {'ok': True}

        def complete_step_run(self, **kwargs):
            return {'ok': True}

    monkeypatch.setattr('agent_runner_v2.backend_client.BackendClient', FakeClient)
    monkeypatch.setattr('agent_runner_v2.run_agent._submit_worker_result', lambda **kwargs: submissions.append(kwargs))

    def fake_spawn_child(*, claim, runtime_root, cli_pythonpath, logger, backend_url, step_spec_source):
        child_dir = runtime_root / 'step-1'
        child_dir.mkdir(parents=True, exist_ok=True)
        result_path = child_dir / 'result.json'
        result_path.write_text(json.dumps({
            'status': 'completed',
            'outcome': 'approved',
            'step_name': 'pre_init',
            'artifacts': {},
            'diagnostics': {},
            'failure': None,
        }), encoding='utf-8')
        log_path = child_dir / 'child.log'
        log_path.write_text('started\n', encoding='utf-8')
        return daemon_module.ChildExecution(
            run_id='run-1',
            run_code='RUN-1',
            step_run_id='step-1',
            step_name='pre_init',
            request_payload={},
            request_path=child_dir / 'request.json',
            result_path=result_path,
            combined_log_path=log_path,
            child_event_log_path=child_dir / 'child-events.jsonl',
            process=DummyProc([None, 0]),
            started_at_monotonic=0.0,
            started_at_iso='2026-06-11T00:00:00+00:00',
            state='running',
        )

    monkeypatch.setattr(daemon_module, '_spawn_child', fake_spawn_child)

    rc = daemon_module._run_supervisor(
        worker_id='worker-1',
        worker_label='live',
        backend_url='http://127.0.0.1:8100',
        step_spec_source='backend',
        poll_seconds=1,
        max_parallel=1,
        stalled_seconds=30,
        step_timeout_seconds=60,
        kill_grace_seconds=5,
        runtime_dir=tmp_path / 'runtime',
        log_file=tmp_path / 'worker-daemon.jsonl',
        cli_pythonpath=None,
        once=True,
    )

    assert rc == 0
    assert submissions
    child_heartbeats = [item for item in heartbeats if item.get('workflow_step_run_id') == 'step-1']
    assert child_heartbeats
    assert child_heartbeats[0]['worker_id'] == 'worker-1'
    assert child_heartbeats[0]['workflow_run_id'] == 'run-1'
    assert child_heartbeats[0]['state'] in {'running', 'completed'}
    assert (tmp_path / 'worker-daemon.jsonl').exists()
