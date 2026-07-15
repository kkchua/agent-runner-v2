from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

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


def test_resolve_subprocess_cwd_falls_back_when_project_root_missing(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    resolved = daemon_module._resolve_subprocess_cwd(
        project_root=str(tmp_path / "missing-project"),
        workspace_root=str(workspace),
    )

    assert resolved == workspace.resolve()


def test_run_supervisor_spawns_child_and_emits_child_heartbeat(monkeypatch, tmp_path):
    heartbeats: list[dict] = []
    sync_calls: list[dict] = []
    claims = [
        {
            'run': {'id': 'run-1', 'run_code': 'RUN-1'},
            'step_run': {'id': 'step-1', 'step_name': 'pre_init'},
            'step_execution_spec': {'template_group': 'initiative_intake_v1'},
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

        def sync_job_state(self, **kwargs):
            sync_calls.append(kwargs)
            return {'ok': True}

    monkeypatch.setattr('agent_runner_v2.backend_client.BackendClient', FakeClient)

    job_root = tmp_path / 'jobs'

    def fake_job_dir(group_name: str, job_id: str):
        return job_root / group_name / job_id

    monkeypatch.setattr('agent_runner_v2.job_state.job_dir', fake_job_dir)

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
        job_path = fake_job_dir('initiative_intake_v1', 'RUN-1')
        job_path.mkdir(parents=True, exist_ok=True)
        (job_path / 'job.json').write_text(json.dumps({
            'job_status': 'COMPLETED',
            'completed_steps': ['pre_init'],
            'project_root': str(tmp_path),
            'artifacts': {'plan': 'docs/plan.md'},
        }), encoding='utf-8')
        return daemon_module.ChildExecution(
            run_id='run-1',
            run_code='RUN-1',
            step_run_id='step-1',
            step_name='pre_init',
            run_payload={'id': 'run-1', 'run_code': 'RUN-1'},
            step_run_payload={'id': 'step-1', 'step_name': 'pre_init'},
            request_payload={'template_group': 'initiative_intake_v1', 'job_id': 'RUN-1'},
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
    assert sync_calls
    assert sync_calls[0]['step_run_id'] == 'step-1'
    assert sync_calls[0]['payload']['run_status'] == 'completed'
    assert sync_calls[0]['payload']['artifacts'] == [
        {'artifact_key': 'plan', 'file_path': str((tmp_path / 'docs' / 'plan.md').resolve()).replace("\\", "/"), 'role': 'output'}
    ]
    child_heartbeats = [item for item in heartbeats if item.get('workflow_step_run_id') == 'step-1']
    assert child_heartbeats
    assert child_heartbeats[0]['worker_id'] == 'worker-1'
    assert child_heartbeats[0]['workflow_run_id'] == 'run-1'
    assert child_heartbeats[0]['state'] in {'running', 'completed'}
    assert (tmp_path / 'worker-daemon.jsonl').exists()


def test_spawn_child_passes_claimed_step_to_run_command(monkeypatch, tmp_path):
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        'agent_runner_v2.run_agent._build_worker_request_payload',
        lambda **kwargs: {
            'project_root': str(tmp_path),
            'job_id': 'RUN-1',
            'template_group': 'initiative_intake_v1',
        },
    )
    monkeypatch.setattr(daemon_module.time, 'monotonic', lambda: 123.0)

    class FakeProc:
        def __init__(self):
            self.pid = 4242

        def poll(self):
            return None

    def fake_popen(args, stdout, stderr, env, cwd):
        captured['args'] = list(args)
        captured['cwd'] = cwd
        return FakeProc()

    monkeypatch.setattr(subprocess, 'Popen', fake_popen)

    logger = SimpleNamespace(log=lambda *args, **kwargs: None)
    child = daemon_module._spawn_child(
        claim={
            'run': {'id': 'run-1', 'run_code': 'RUN-1'},
            'step_run': {'id': 'step-1', 'step_name': 'review_core_governance_docs'},
            'step_execution_spec': {'step_sequence_no': 2},
        },
        runtime_root=tmp_path / 'runtime',
        cli_pythonpath=None,
        logger=logger,
        backend_url='http://127.0.0.1:8100',
        step_spec_source='backend',
    )

    assert child.step_name == 'review_core_governance_docs'
    assert captured['cwd'] == str(tmp_path.resolve())
    assert captured['args'] == [
        sys.executable, '-m', 'agent_runner_v2.run_agent', 'run',
        '--project-root', str(tmp_path),
        '--template-group', 'initiative_intake_v1',
        '--mode', 'daemon',
        '--job-id', '',
        '--job-no', 'RUN-1',
        '--job', 'review_core_governance_docs',
    ]
