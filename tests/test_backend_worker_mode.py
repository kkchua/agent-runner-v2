from __future__ import annotations

import json
from unittest.mock import MagicMock

from agent_runner_v2.execution_request import ExecutionRequest
from agent_runner_v2.execution_result import ExecutionFailure, ExecutionResult
from agent_runner_v2 import run_agent as run_agent_module
from agent_runner_v2.step_runner import build_context
from agent_runner_v2.run_agent import (
    _build_execution_state,
    _build_worker_request_payload,
    _execute_step_command,
    _submit_worker_result,
    _worker_command,
)


def test_execution_request_from_dict_requires_minimum_fields():
    request = ExecutionRequest.from_dict(
        {
            'workflow_name': 'initiative_intake_v1',
            'template_group': 'initiative_intake_v1',
            'step_name': 'pre_init',
            'project_root': '/tmp/project',
            'artifacts': {'DRAFT_INIT_FILE': 'docs/draft.md'},
        }
    )

    assert request.workflow_name == 'initiative_intake_v1'
    assert request.template_group == 'initiative_intake_v1'
    assert request.step_name == 'pre_init'
    assert request.input_artifacts['DRAFT_INIT_FILE'] == 'docs/draft.md'


def test_execution_result_to_dict_serializes_failure():
    result = ExecutionResult(
        status='failed',
        outcome='failed',
        step_name='pre_init',
        failure=ExecutionFailure(
            failure_class='FATAL',
            failure_code='META_JSON_MISSING',
            failure_reason='missing sidecar',
            failure_source='runner',
        ),
    )

    payload = result.to_dict()
    assert payload['failure']['failure_code'] == 'META_JSON_MISSING'
    assert payload['status'] == 'failed'


def test_build_worker_request_payload_maps_backend_fields():
    run = {
        'id': 'run-1',
        'workflow_name': 'task_execution_v1',
        'run_code': 'EXEC-001',
        'project_root': '/workspace/project',
        'env_overrides': {'FOO': 'bar'},
        'input_payload': {'TASK_FILE': 'docs/task.md'},
        'context_payload': {'TASK_FILE': 'docs/task.md'},
    }
    step_run = {
        'id': 'step-1',
        'step_name': 'task',
        'coder': 'qwen',
    }

    payload = _build_worker_request_payload(run=run, step_run=step_run)

    assert payload['workflow_run_id'] == 'run-1'
    assert payload['workflow_step_run_id'] == 'step-1'
    assert payload['template_group'] == 'task_execution_v1'
    assert payload['coder_override'] == 'qwen'
    assert payload['input_artifacts']['TASK_FILE'] == 'docs/task.md'


def test_build_execution_state_overrides_ids_and_step():
    request = ExecutionRequest.from_dict(
        {
            'workflow_name': 'initiative_intake_v1',
            'template_group': 'initiative_intake_v1',
            'workflow_run_id': 'run-1',
            'workflow_step_run_id': 'step-1',
            'job_id': 'JOB-123',
            'step_name': 'pre_init',
            'project_root': '/tmp/project',
            'input_artifacts': {'DRAFT_INIT_FILE': 'docs/draft.md'},
            'context_payload': {'x': 1},
        }
    )
    group_cfg = {
        'job_prefix': 'PREINIT',
        'job_init_step': 'pre_init',
        'job_init_inputs': ['DRAFT_INIT_FILE'],
        'default_max_rejects': 2,
        'steps': ['pre_init'],
        'step_configs': {'pre_init': {'prompt_file': 'dummy.txt'}},
    }

    state = _build_execution_state(request=request, group_cfg=group_cfg)

    assert state['job_id'] == 'JOB-123'
    assert state['current_step'] == 'pre_init'
    assert state['workflow_run_id'] == 'run-1'
    assert state['workflow_step_run_id'] == 'step-1'
    assert state['backend_context_payload'] == {'x': 1}
    assert state['backend_step_dir_rel'] == 'backend_runs/run-1/01_pre_init'


def test_build_context_prefers_backend_output_paths(monkeypatch):
    state = {
        'current_step': 'plan',
        'artifacts': {'INIT_FILE': 'docs/init.md'},
        'backend_context_payload': {
            'PLAN_FILE_PATH': 'docs/custom/PLAN-20260606-01_test.md',
            'PLAN_FILE_METAJSON': 'docs/custom/PLAN-20260606-01_test.meta.json',
            'PLAN_ID': 'PLAN-20260606-01',
        },
    }
    step_cfg = {
        'produces': ['PLAN_FILE'],
    }

    def fail_build_plan_file_path(*, state):
        raise AssertionError('legacy plan path builder should not be used when backend supplies path')

    monkeypatch.setattr('agent_runner_v2.step_runner._build_plan_file_path', fail_build_plan_file_path)

    ctx = build_context(state=state, step='plan', step_cfg=step_cfg)

    assert ctx['PLAN_FILE_PATH'] == 'docs/custom/PLAN-20260606-01_test.md'
    assert ctx['PLAN_FILE_METAJSON'] == 'docs/custom/PLAN-20260606-01_test.meta.json'
    assert ctx['PLAN_ID'] == 'PLAN-20260606-01'


def test_submit_worker_result_posts_artifacts_event_and_completion():
    client = MagicMock()
    run = {'id': 'run-1'}
    step_run = {'id': 'step-1'}
    result = {
        'status': 'completed',
        'outcome': 'approved',
        'coder_used': 'claude',
        'remark': 'ok',
        'artifacts': {'PRE_INIT_FILE': 'docs/pre_init.md'},
        'meta_json_path': 'tmp/meta.json',
        'usage': {'total_tokens': 10},
        'review': {'decision': 'approved', 'remark': 'looks good'},
        'diagnostics': {'subprocess_return_code': 0},
        'failure': None,
    }

    _submit_worker_result(client=client, run=run, step_run=step_run, result=result)

    client.create_artifact.assert_called_once()
    artifact_call = client.create_artifact.call_args.kwargs
    assert artifact_call['run_id'] == 'run-1'
    assert artifact_call['payload']['artifact_key'] == 'PRE_INIT_FILE'

    client.complete_step_run.assert_called_once()
    complete_call = client.complete_step_run.call_args.kwargs
    assert complete_call['step_run_id'] == 'step-1'
    assert complete_call['payload']['status'] == 'completed'
    assert complete_call['payload']['review']['decision'] == 'approved'

    client.create_event.assert_called_once()
    event_call = client.create_event.call_args.kwargs
    assert event_call['payload']['event_type'] == 'WORKER_RESULT'


def test_execute_step_command_writes_result_file(monkeypatch, tmp_path):
    request_path = tmp_path / 'request.json'
    result_path = tmp_path / 'result.json'
    request_path.write_text(
        json.dumps(
            {
                'workflow_name': 'initiative_intake_v1',
                'template_group': 'initiative_intake_v1',
                'workflow_run_id': 'run-1',
                'workflow_step_run_id': 'step-1',
                'step_name': 'pre_init',
                'project_root': str(tmp_path),
                'input_artifacts': {'DRAFT_INIT_FILE': 'docs/draft.md'},
            }
        ),
        encoding='utf-8',
    )

    monkeypatch.setattr(run_agent_module, 'load_project_config', lambda workspace_root: {'default_workflow': 'default', 'workflows': {'initiative_intake_v1': {'path': '.'}}})
    monkeypatch.setattr(run_agent_module, 'workflow_root_for', lambda workspace_root, workflow_name: workspace_root)
    monkeypatch.setattr(run_agent_module, 'load_workflow_module', lambda workspace_root, workflow_name, config=None: object())
    monkeypatch.setattr(run_agent_module, 'set_context', lambda **kwargs: None)
    monkeypatch.setattr(run_agent_module, 'set_workflow_module', lambda module: None)
    monkeypatch.setattr(run_agent_module, '_load_group', lambda group_name: {
        'job_prefix': 'PREINIT',
        'job_init_step': 'pre_init',
        'job_init_inputs': ['DRAFT_INIT_FILE'],
        'default_max_rejects': 2,
        'steps': ['pre_init'],
        'step_configs': {'pre_init': {'prompt_file': 'dummy.txt'}},
    })
    monkeypatch.setattr(run_agent_module, '_validate_static_reference_files', lambda *args, **kwargs: None)
    monkeypatch.setattr(
        run_agent_module,
        '_execute_backend_step_request',
        lambda **kwargs: ExecutionResult(
            status='completed',
            outcome='approved',
            step_name='pre_init',
            coder_used='claude',
            remark='ok',
            artifacts={'PRE_INIT_FILE': 'docs/pre_init.md'},
            diagnostics={'workflow_run_id': 'run-1'},
        ),
    )

    exit_code = _execute_step_command(request_path, result_path)

    assert exit_code == 0
    payload = json.loads(result_path.read_text(encoding='utf-8'))
    assert payload['status'] == 'completed'
    assert payload['artifacts']['PRE_INIT_FILE'] == 'docs/pre_init.md'


def test_execute_step_command_returns_nonzero_on_failed_result(monkeypatch, tmp_path):
    request_path = tmp_path / 'request.json'
    request_path.write_text(
        json.dumps(
            {
                'workflow_name': 'initiative_intake_v1',
                'template_group': 'initiative_intake_v1',
                'workflow_run_id': 'run-1',
                'workflow_step_run_id': 'step-1',
                'step_name': 'pre_init',
                'project_root': str(tmp_path),
            }
        ),
        encoding='utf-8',
    )

    monkeypatch.setattr(run_agent_module, 'load_project_config', lambda workspace_root: {'default_workflow': 'default', 'workflows': {'initiative_intake_v1': {'path': '.'}}})
    monkeypatch.setattr(run_agent_module, 'workflow_root_for', lambda workspace_root, workflow_name: workspace_root)
    monkeypatch.setattr(run_agent_module, 'load_workflow_module', lambda workspace_root, workflow_name, config=None: object())
    monkeypatch.setattr(run_agent_module, 'set_context', lambda **kwargs: None)
    monkeypatch.setattr(run_agent_module, 'set_workflow_module', lambda module: None)
    monkeypatch.setattr(run_agent_module, '_load_group', lambda group_name: {
        'job_prefix': 'PREINIT',
        'job_init_step': 'pre_init',
        'job_init_inputs': [],
        'default_max_rejects': 2,
        'steps': ['pre_init'],
        'step_configs': {'pre_init': {'prompt_file': 'dummy.txt'}},
    })
    monkeypatch.setattr(run_agent_module, '_validate_static_reference_files', lambda *args, **kwargs: None)
    monkeypatch.setattr(
        run_agent_module,
        '_execute_backend_step_request',
        lambda **kwargs: ExecutionResult(
            status='failed',
            outcome='failed',
            step_name='pre_init',
            failure=ExecutionFailure(
                failure_class='FATAL',
                failure_code='TEST_FAILURE',
                failure_reason='broken',
                failure_source='runner',
            ),
        ),
    )

    exit_code = _execute_step_command(request_path)

    assert exit_code == 1


def test_worker_command_once_processes_one_claim(monkeypatch):
    client = MagicMock()
    client.claim_step.return_value = {
        'run': {
            'id': 'run-1',
            'workflow_name': 'initiative_intake_v1',
            'run_code': 'RUN-1',
            'project_root': '/workspace/project',
            'env_overrides': {},
            'input_payload': {'DRAFT_INIT_FILE': 'docs/draft.md'},
            'context_payload': {'DRAFT_INIT_FILE': 'docs/draft.md'},
        },
        'step_run': {
            'id': 'step-1',
            'step_name': 'pre_init',
            'coder': 'claude',
        },
    }
    monkeypatch.setattr(run_agent_module, 'BackendClient', lambda backend_url: client)
    monkeypatch.setattr(
        run_agent_module,
        '_invoke_execute_step_subprocess',
        lambda request_payload: {
            'status': 'completed',
            'outcome': 'approved',
            'coder_used': 'claude',
            'remark': 'ok',
            'artifacts': {'PRE_INIT_FILE': 'docs/pre_init.md'},
            'meta_json_path': 'tmp/meta.json',
            'usage': {'total_tokens': 12},
            'review': None,
            'diagnostics': {'subprocess_return_code': 0},
            'failure': None,
        },
    )
    submit_calls: list[dict] = []
    monkeypatch.setattr(
        run_agent_module,
        '_submit_worker_result',
        lambda **kwargs: submit_calls.append(kwargs),
    )

    exit_code = _worker_command(
        backend_url='http://127.0.0.1:8100',
        worker_id='worker-1',
        host_name='host-1',
        poll_seconds=1,
        once=True,
    )

    assert exit_code == 0
    client.register_worker.assert_called_once()
    assert client.heartbeat.call_count >= 2
    client.claim_step.assert_called_once_with(worker_id='worker-1')
    assert len(submit_calls) == 1
    assert submit_calls[0]['run']['id'] == 'run-1'
    assert submit_calls[0]['step_run']['id'] == 'step-1'


def test_worker_command_once_exits_cleanly_when_no_claim(monkeypatch):
    client = MagicMock()
    client.claim_step.return_value = {'step_run': None}
    monkeypatch.setattr(run_agent_module, 'BackendClient', lambda backend_url: client)

    exit_code = _worker_command(
        backend_url='http://127.0.0.1:8100',
        worker_id='worker-1',
        host_name=None,
        poll_seconds=1,
        once=True,
    )

    assert exit_code == 0
    client.register_worker.assert_called_once()
    client.claim_step.assert_called_once_with(worker_id='worker-1')


def test_build_execution_state_does_not_call_create_job(monkeypatch):
    called = {'create_job': False}

    def _fail_create_job(*args, **kwargs):
        called['create_job'] = True
        raise AssertionError('create_job should not be called in backend mode')

    monkeypatch.setattr(run_agent_module, 'create_job', _fail_create_job)

    request = ExecutionRequest.from_dict(
        {
            'workflow_name': 'initiative_intake_v1',
            'template_group': 'initiative_intake_v1',
            'workflow_run_id': 'run-1',
            'workflow_step_run_id': 'step-1',
            'step_name': 'pre_init',
            'project_root': '/tmp/project',
        }
    )
    group_cfg = {
        'job_prefix': 'PREINIT',
        'job_init_step': 'pre_init',
        'job_init_inputs': [],
        'default_max_rejects': 2,
        'steps': ['pre_init'],
        'step_configs': {'pre_init': {'prompt_file': 'dummy.txt'}},
    }

    state = _build_execution_state(request=request, group_cfg=group_cfg)

    assert called['create_job'] is False
    assert state['job_id'] == 'run-1'


def test_build_context_prefers_backend_task_payload(monkeypatch):
    monkeypatch.setattr(run_agent_module, 'get_workflow_module', lambda: None)
    state = {
        'template_group': 'task_execution_v1',
        'artifacts': {},
        'loop_context': {},
        'replan_context': {},
        'backend_context_payload': {
            'CURRENT_TASK_NODE_ID': 'TASK-20260606-07',
            'CURRENT_TASK_TITLE': 'Refactor worker mode',
            'TASK_FILE_PATH': 'docs/delivery/03_tasks/TASK-20260606-07_refactor-worker-mode.md',
            'TASK_FILE_METAJSON': 'docs/delivery/03_tasks/TASK-20260606-07_refactor-worker-mode.meta.json',
        },
    }
    step_cfg = {'produces': ['TASK_FILE']}

    ctx = build_context(state, step='task', step_cfg=step_cfg)

    assert ctx['CURRENT_TASK_NODE_ID'] == 'TASK-20260606-07'
    assert ctx['CURRENT_TASK_TITLE'] == 'Refactor worker mode'
    assert ctx['TASK_FILE_PATH'] == 'docs/delivery/03_tasks/TASK-20260606-07_refactor-worker-mode.md'
    assert ctx['TASK_FILE_METAJSON'] == 'docs/delivery/03_tasks/TASK-20260606-07_refactor-worker-mode.meta.json'
