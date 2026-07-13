from __future__ import annotations

import json
from unittest.mock import MagicMock
import pytest

from agent_runner_v2.execution_request import ExecutionRequest
from agent_runner_v2.execution_result import ExecutionFailure, ExecutionResult
from agent_runner_v2 import run_agent as run_agent_module
from agent_runner_v2 import shared_runtime_deps
from agent_runner_v2.actions.promote_artifact import promote_artifact
from agent_runner_v2.step_runner import build_context
from agent_runner_v2 import runtime_context as runtime_context_module
from agent_runner_v2.run_agent import (
    _finalize_worker_completion,
    _build_execution_state,
    _build_worker_request_payload,
    _execute_step_command,
    _publish_backend_artifacts,
    _submit_worker_result,
    _worker_command,
    _write_backend_job_json,
)
from conftest import load_bootstrap_workflow_module


_BOOTSTRAP_WORKFLOW_MODULE = load_bootstrap_workflow_module()


@pytest.fixture(autouse=True)
def _seed_workflow_module(monkeypatch, tmp_path):
    runner_home = tmp_path / '.ukbe-runner'
    monkeypatch.setattr(runtime_context_module, 'GLOBAL_RUNNER_HOME', runner_home)
    monkeypatch.setattr(
        runtime_context_module,
        '_CTX',
        runtime_context_module.RuntimeContext(
            workspace_root=tmp_path,
            runner_home=runner_home,
            workflow_name='default',
            workflow_root=runner_home / 'workflows' / 'default',
            workflow_module=_BOOTSTRAP_WORKFLOW_MODULE,
            delivery_root=None,
        ),
    )


def _use_tmp_runner_home(monkeypatch, tmp_path):
    runner_home = tmp_path / '.ukbe-runner'
    monkeypatch.setattr(runtime_context_module, 'GLOBAL_RUNNER_HOME', runner_home)
    monkeypatch.setattr(
        runtime_context_module,
        '_CTX',
        runtime_context_module.RuntimeContext(
            workspace_root=tmp_path,
            runner_home=runner_home,
            workflow_name='default',
            workflow_root=runner_home / 'workflows' / 'default',
            workflow_module=_BOOTSTRAP_WORKFLOW_MODULE,
            delivery_root=None,
        ),
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

    payload = _build_worker_request_payload(
        run=run,
        step_run=step_run,
        step_execution_spec={
            'template_group': 'task_execution_v1',
            'execution_kind': 'coder',
            'required_inputs': [{'artifact_key': 'TASK_FILE', 'binding_type': 'required_input'}],
            'produces': [{'artifact_key': 'IMPL_FILE', 'binding_type': 'produces'}],
        },
    )

    assert payload['workflow_run_id'] == 'run-1'
    assert payload['workflow_step_run_id'] == 'step-1'
    assert payload['template_group'] == 'task_execution_v1'
    assert payload['coder_override'] == 'qwen'
    assert payload['input_artifacts']['TASK_FILE'] == 'docs/task.md'
    assert payload['step_execution_spec']['execution_kind'] == 'coder'


def test_build_worker_request_payload_merges_required_artifacts_from_context():
    run = {
        'id': 'run-1',
        'workflow_name': 'delivery_scaffold_v1',
        'run_code': 'SCAFFOLD-001',
        'project_root': '/workspace/project',
        'input_payload': {},
        'context_payload': {'PROJECT_ANALYSIS': 'docs/system/00_governance/bootstrap/project_analysis.md'},
    }
    step_run = {'id': 'step-2', 'step_name': 'generate_sop', 'coder': 'qwen'}
    payload = _build_worker_request_payload(
        run=run,
        step_run=step_run,
        step_execution_spec={
            'template_group': 'delivery_scaffold_v1',
            'execution_kind': 'coder',
            'required_inputs': [{'artifact_key': 'PROJECT_ANALYSIS', 'binding_type': 'required_input'}],
            'produces': [{'artifact_key': 'DELIVERY_SOP', 'binding_type': 'produces'}],
        },
    )

    assert payload['input_artifacts']['PROJECT_ANALYSIS'] == 'docs/system/00_governance/bootstrap/project_analysis.md'


def test_build_worker_request_payload_backend_mode_uses_transport_spec_without_local_lookup(monkeypatch):
    run = {
        'id': 'run-1',
        'workflow_name': '00_core_governance_bootstrap_v1',
        'run_code': '00CORE-001',
        'project_root': '/workspace/project',
        'input_payload': {},
        'context_payload': {
            'SYSTEM_DOC_STANDARD': 'docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md',
        },
    }
    step_run = {
        'id': 'step-4',
        'step_name': 'validate_core_governance_docs',
        'sequence_no': 4,
        'coder': 'action',
    }

    def fail_lookup(**_kwargs):
        raise AssertionError('backend mode should not require local workflow lookup')

    monkeypatch.setattr(shared_runtime_deps, 'get_template_group_cfg', fail_lookup)

    payload = _build_worker_request_payload(
        run=run,
        step_run=step_run,
        step_execution_spec={
            'template_group': '00_core_governance_bootstrap_v1',
            'step_sequence_no': 4,
            'required_inputs': [{'artifact_key': 'SYSTEM_DOC_STANDARD'}],
            'produces': [{'artifact_key': 'SYSTEM_DOCS_VALIDATION'}],
        },
        step_spec_source='backend',
    )

    assert payload['input_artifacts']['SYSTEM_DOC_STANDARD'] == 'docs/system/00_governance/bootstrap/DOCUMENTATION_STANDARD.md'
    assert payload['step_execution_spec']['step_sequence_no'] == 4
    assert str(payload['state_overrides']['backend_step_dir_rel']).replace('\\', '/').endswith(
        '00_core_governance_bootstrap_v1/00CORE-001/04_validate_core_governance_docs'
    )


def test_build_context_action_step_without_result_meta_key_does_not_crash():
    state = {
        'template_group': '00_core_governance_bootstrap_v1',
        'job_id': '00CORE-001',
        'backend_step_dir_rel': '.ukbe-runner/jobs/00_core_governance_bootstrap_v1/00CORE-001/06_stepCompletion',
        'artifacts': {},
    }

    ctx = build_context(
        state=state,
        step='stepCompletion',
        step_cfg={'action': 'step_completion'},
    )

    assert 'SYSTEM_DOC_ROOT' in ctx


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
    assert str(state['backend_step_dir_rel']).replace('\\', '/').endswith('initiative_intake_v1/JOB-123/01_pre_init')


def test_build_execution_state_uses_backend_step_sequence_for_runtime_dir():
    request = ExecutionRequest.from_dict(
        {
            'workflow_name': 'delivery_scaffold_v1',
            'template_group': 'delivery_scaffold_v1',
            'workflow_run_id': 'run-1',
            'workflow_step_run_id': 'step-1',
            'job_id': 'JOB-123',
            'step_name': 'generate_templates',
            'project_root': '/tmp/project',
            'step_execution_spec': {
                'step_order': 5,
                'step_sequence_no': 3,
            },
        }
    )
    group_cfg = {
        'job_prefix': 'SCAFFOLD',
        'job_init_step': 'project_analysis',
        'job_init_inputs': [],
        'default_max_rejects': 2,
        'steps': ['project_analysis', 'generate_sop', 'refine_sop', 'replan_sop', 'generate_templates'],
        'step_configs': {'generate_templates': {'prompt_file': 'dummy.txt'}},
    }

    state = _build_execution_state(request=request, group_cfg=group_cfg)

    assert state['backend_step_order'] == 5
    assert state['backend_step_sequence'] == 3
    assert str(state['backend_step_dir_rel']).replace('\\', '/').endswith('delivery_scaffold_v1/JOB-123/03_generate_templates')


def test_build_context_uses_step_execution_spec_artifact_rules_for_produced_paths():
    state = {
        'template_group': 'delivery_scaffold_v1',
        'job_id': 'JOB-123',
        'current_step': 'generate_templates',
        'backend_step_dir_rel': '.ukbe-runner/jobs/delivery_scaffold_v1/JOB-123/05_generate_templates',
        'artifacts': {'PROJECT_ANALYSIS': 'docs/system/00_governance/bootstrap/project_analysis.md'},
        'backend_artifact_rules': {
            'PROJECT_ANALYSIS': {
                'working_path_template': '.ukbe-runner/jobs/{template_group}/{job_id}/{step_dir}/project_analysis.md',
                'final_path_template': 'docs/system/00_governance/bootstrap/project_analysis.md',
                'meta_path_strategy': 'step_shared_meta',
                'publish_mode': 'copy',
                'publish_on_status': 'approved',
            },
            'DELIVERY_TEMPLATE_REGISTRY': {
                'working_path_template': '.ukbe-runner/jobs/{template_group}/{job_id}/{step_dir}/template_registry.md',
                'final_path_template': 'docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md',
                'meta_path_strategy': 'step_shared_meta',
                'publish_mode': 'copy',
                'publish_on_status': 'approved',
            },
        },
    }
    step_cfg = {
        'produces': ['DELIVERY_TEMPLATE_REGISTRY'],
    }

    ctx = build_context(state=state, step='generate_templates', step_cfg=step_cfg)

    assert ctx['PROJECT_ANALYSIS_PATH'] == 'docs/system/00_governance/bootstrap/project_analysis.md'
    assert str(ctx['DELIVERY_TEMPLATE_REGISTRY']).replace('\\', '/').endswith('delivery_scaffold_v1/JOB-123/05_generate_templates/template_registry.md')
    assert str(ctx['DELIVERY_TEMPLATE_REGISTRY_METAJSON']).replace('\\', '/').endswith('delivery_scaffold_v1/JOB-123/05_generate_templates/meta.json')


def test_build_context_action_steps_prefer_step_metajson():
    state = {
        'template_group': 'delivery_planning_v1',
        'job_id': 'PLAN-20260611-38055dbf',
        'backend_step_dir_rel': '.ukbe-runner/jobs/delivery_planning_v1/PLAN-20260611-38055dbf/03_promote_plan',
        'artifacts': {
            'PLAN_FILE': 'docs/delivery/02_plans/PLAN-20260611-01_backend-lineage-metadata-test.md',
        },
    }
    step_cfg = {
        'action': 'promote_artifact',
        'result_meta_key': 'PLAN_FILE',
        'produces': ['PLAN_FILE'],
    }

    ctx = build_context(state=state, step='promote_plan', step_cfg=step_cfg)

    assert str(ctx['PLAN_FILE_METAJSON']).replace('\\', '/').endswith('delivery_planning_v1/PLAN-20260611-38055dbf/03_promote_plan/meta.json')


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


def test_promote_artifact_writes_step_and_artifact_metajson(tmp_path, monkeypatch):
    runner_home = tmp_path / ".ukbe-runner"
    monkeypatch.setattr(runtime_context_module, "GLOBAL_RUNNER_HOME", runner_home)
    runtime_context_module.set_context(workspace_root=tmp_path)

    plan_rel = 'docs/delivery/02_plans/PLAN-20260611-01_backend-lineage-metadata-test.md'
    plan_path = tmp_path / plan_rel
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text('| Status | `draft` |\n', encoding='utf-8')

    context = {
        'PLAN_FILE': plan_rel,
        'PLAN_FILE_METAJSON': '.ukbe-runner/jobs/delivery_planning_v1/PLAN-20260611-38055dbf/03_promote_plan/meta.json',
    }
    result = promote_artifact(
        context=context,
        state={},
        step_cfg={'promotes': 'PLAN_FILE', 'result_meta_key': 'PLAN_FILE'},
        project_root=tmp_path,
    )

    assert result.status == 'APPROVED'
    assert '`Approved`' in plan_path.read_text(encoding='utf-8')

    step_meta = runner_home / 'jobs/delivery_planning_v1/PLAN-20260611-38055dbf/03_promote_plan/meta.json'
    artifact_meta = tmp_path / 'docs/delivery/02_plans/PLAN-20260611-01_backend-lineage-metadata-test.meta.json'
    assert step_meta.exists()
    assert artifact_meta.exists()
    assert json.loads(step_meta.read_text(encoding='utf-8'))['coder_result']['artifacts']['PLAN_FILE'] == plan_rel
    assert json.loads(artifact_meta.read_text(encoding='utf-8'))['coder_result']['artifacts']['PLAN_FILE'] == plan_rel


def test_publish_backend_artifacts_uses_artifact_rules(tmp_path):
    source_dir = tmp_path / '.ukbe-runner/jobs/delivery_scaffold_v1/JOB-123/05_generate_templates'
    source_dir.mkdir(parents=True)
    source_file = source_dir / 'template_registry.md'
    source_file.write_text('registry', encoding='utf-8')
    state = {
        'backend_artifact_rules': {
            'DELIVERY_TEMPLATE_REGISTRY': {
                'final_path_template': 'docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md',
                'publish_mode': 'copy',
                'publish_on_status': 'approved',
            }
        }
    }

    published = _publish_backend_artifacts(
        state=state,
        step='generate_templates',
        artifacts={'DELIVERY_TEMPLATE_REGISTRY': '.ukbe-runner/jobs/delivery_scaffold_v1/JOB-123/05_generate_templates/template_registry.md'},
        project_root=tmp_path,
    )

    assert published['DELIVERY_TEMPLATE_REGISTRY'] == 'docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md'
    assert (tmp_path / 'docs/system/00_governance/bootstrap/templates/delivery/01_delivery_template_registry.md').read_text(encoding='utf-8') == 'registry'


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

    client.complete_step_run.return_value = {
        'run': {'id': 'run-1', 'status': 'pending'},
        'step_run': {'id': 'step-1', 'status': 'completed', 'outcome': 'approved'},
        'next_step_run': {'id': 'step-2', 'step_name': 'review_pre_init'},
    }

    completion = _submit_worker_result(client=client, run=run, step_run=step_run, result=result)

    assert completion['run']['status'] == 'pending'

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


def test_finalize_worker_completion_refreshes_terminal_run_and_sends_completed(monkeypatch):
    client = MagicMock()
    client.get_run.return_value = {
        'id': 'run-1',
        'status': 'completed',
        'workflow_name': 'initiative_intake_v1',
        'run_code': 'RUN-1',
    }
    notifications: list[tuple[str, dict]] = []
    step_notifications: list[tuple[str, dict, str, dict]] = []
    writes: list[dict] = []

    monkeypatch.setattr(
        'agent_runner_v2.notification_manager.send_workflow_notification',
        lambda status, context: notifications.append((status, context)) or True,
    )
    monkeypatch.setattr(
        'agent_runner_v2.notification_manager.send_step_notification',
        lambda status, context, step, step_cfg: step_notifications.append((status, context, step, step_cfg)) or True,
    )
    monkeypatch.setattr(
        shared_runtime_deps,
        '_write_backend_job_json',
        lambda **kwargs: writes.append(kwargs),
    )

    info = _finalize_worker_completion(
        client=client,
        run={'id': 'run-1', 'run_code': 'RUN-1', 'workflow_name': 'initiative_intake_v1'},
        step_run={'id': 'step-1', 'step_name': 'finalize_bootstrap'},
        completion={
            'run': {'id': 'run-1', 'status': 'pending', 'workflow_name': 'initiative_intake_v1', 'run_code': 'RUN-1'},
            'step_run': {'id': 'step-1', 'status': 'completed', 'step_name': 'finalize_bootstrap'},
            'next_step_run': None,
        },
        step_execution_spec={'raw_config': {'enable_notifications': True}},
    )

    client.get_run.assert_called_once_with(run_id='run-1')
    assert info['run']['status'] == 'completed'
    assert notifications == [('COMPLETED', info['run'])]
    assert step_notifications == [('STEP_COMPLETED', info['run'], 'finalize_bootstrap', {'enable_notifications': True})]
    assert writes[0]['last_event'] == 'RUN_COMPLETED'


def test_finalize_worker_completion_enqueued_next_step_sends_only_step_notification(monkeypatch):
    client = MagicMock()
    notifications: list[tuple[str, dict]] = []
    step_notifications: list[tuple[str, dict, str, dict]] = []
    writes: list[dict] = []

    monkeypatch.setattr(
        'agent_runner_v2.notification_manager.send_workflow_notification',
        lambda status, context: notifications.append((status, context)) or True,
    )
    monkeypatch.setattr(
        'agent_runner_v2.notification_manager.send_step_notification',
        lambda status, context, step, step_cfg: step_notifications.append((status, context, step, step_cfg)) or True,
    )
    monkeypatch.setattr(
        shared_runtime_deps,
        '_write_backend_job_json',
        lambda **kwargs: writes.append(kwargs),
    )

    info = _finalize_worker_completion(
        client=client,
        run={'id': 'run-1', 'run_code': 'RUN-1', 'workflow_name': '00_core_governance_bootstrap_v1'},
        step_run={'id': 'step-4', 'step_name': 'validate_core_governance_docs'},
        completion={
            'run': {'id': 'run-1', 'status': 'pending', 'workflow_name': '00_core_governance_bootstrap_v1', 'run_code': 'RUN-1'},
            'step_run': {'id': 'step-4', 'status': 'completed', 'step_name': 'validate_core_governance_docs'},
            'next_step_run': {'id': 'step-5', 'step_name': 'refine_core_governance_docs'},
        },
        step_execution_spec={'raw_config': {'enable_notifications': True, 'on_reject_refine': {'step': 'refine_core_governance_docs'}}},
    )

    client.get_run.assert_not_called()
    assert info['last_event'] == 'STEP_ENQUEUED'
    assert notifications == []
    assert step_notifications == [
        (
            'STEP_COMPLETED',
            info['run'],
            'validate_core_governance_docs',
            {'enable_notifications': True, 'on_reject_refine': {'step': 'refine_core_governance_docs'}},
        )
    ]
    assert writes[0]['last_event'] == 'STEP_ENQUEUED'


def test_finalize_worker_completion_awaiting_human_sends_step_and_workflow_notification(monkeypatch):
    client = MagicMock()
    notifications: list[tuple[str, dict]] = []
    step_notifications: list[tuple[str, dict, str, dict]] = []
    writes: list[dict] = []

    monkeypatch.setattr(
        'agent_runner_v2.notification_manager.send_workflow_notification',
        lambda status, context: notifications.append((status, context)) or True,
    )
    monkeypatch.setattr(
        'agent_runner_v2.notification_manager.send_step_notification',
        lambda status, context, step, step_cfg: step_notifications.append((status, context, step, step_cfg)) or True,
    )
    monkeypatch.setattr(
        shared_runtime_deps,
        '_write_backend_job_json',
        lambda **kwargs: writes.append(kwargs),
    )

    info = _finalize_worker_completion(
        client=client,
        run={'id': 'run-1', 'run_code': 'RUN-1', 'workflow_name': '00_core_governance_bootstrap_v1'},
        step_run={'id': 'step-4', 'step_name': 'validate_core_governance_docs'},
        completion={
            'run': {
                'id': 'run-1',
                'status': 'awaiting_human',
                'workflow_name': '00_core_governance_bootstrap_v1',
                'run_code': 'RUN-1',
                'awaiting_human_step': 'validate_core_governance_docs',
            },
            'step_run': {'id': 'step-4', 'status': 'completed', 'step_name': 'validate_core_governance_docs'},
            'next_step_run': None,
        },
        step_execution_spec={'raw_config': {'enable_notifications': True, 'requires_human_approval_after': True}},
    )

    client.get_run.assert_not_called()
    assert info['last_event'] == 'HUMAN_APPROVAL_REQUIRED'
    assert notifications == [('WAITING_FOR_HUMAN_INTERVENTION', info['run'])]
    assert step_notifications == [
        (
            'STEP_COMPLETED',
            info['run'],
            'validate_core_governance_docs',
            {'enable_notifications': True, 'requires_human_approval_after': True},
        )
    ]
    assert writes[0]['last_event'] == 'HUMAN_APPROVAL_REQUIRED'


def test_finalize_worker_completion_failed_sends_failed_notifications(monkeypatch):
    client = MagicMock()
    notifications: list[tuple[str, dict]] = []
    step_notifications: list[tuple[str, dict, str, dict]] = []
    writes: list[dict] = []

    monkeypatch.setattr(
        'agent_runner_v2.notification_manager.send_workflow_notification',
        lambda status, context: notifications.append((status, context)) or True,
    )
    monkeypatch.setattr(
        'agent_runner_v2.notification_manager.send_step_notification',
        lambda status, context, step, step_cfg: step_notifications.append((status, context, step, step_cfg)) or True,
    )
    monkeypatch.setattr(
        shared_runtime_deps,
        '_write_backend_job_json',
        lambda **kwargs: writes.append(kwargs),
    )

    info = _finalize_worker_completion(
        client=client,
        run={'id': 'run-1', 'run_code': 'RUN-1', 'workflow_name': '00_core_governance_bootstrap_v1'},
        step_run={'id': 'step-4', 'step_name': 'validate_core_governance_docs'},
        completion={
            'run': {
                'id': 'run-1',
                'status': 'failed',
                'workflow_name': '00_core_governance_bootstrap_v1',
                'run_code': 'RUN-1',
            },
            'step_run': {'id': 'step-4', 'status': 'failed', 'step_name': 'validate_core_governance_docs'},
            'next_step_run': None,
        },
        step_execution_spec={'raw_config': {'enable_notifications': True}},
    )

    client.get_run.assert_not_called()
    assert info['last_event'] == 'RUN_FAILED'
    assert notifications == [('FAILED', info['run'])]
    assert step_notifications == [
        (
            'STEP_FAILED',
            info['run'],
            'validate_core_governance_docs',
            {'enable_notifications': True},
        )
    ]
    assert writes[0]['last_event'] == 'RUN_FAILED'


def test_write_backend_job_json_mirrors_run_state(tmp_path, monkeypatch):
    monkeypatch.setattr(shared_runtime_deps, 'JOBS_ROOT', tmp_path / '.ukbe-runner/jobs')

    run = {
        'id': 'run-1',
        'run_code': 'PLAN-20260611-38055dbf',
        'workflow_name': 'delivery_planning_v1',
        'status': 'awaiting_human',
        'current_step_name': 'review_planner',
        'current_step_run_id': 'step-2',
        'awaiting_human_step': 'review_planner',
        'target_worker_id': 'worker-1',
        'claimed_by_worker': 'worker-1',
        'project_root': '/workspace/project',
        'context_payload': {
            'PLAN_FILE': 'docs/delivery/02_plans/PLAN-20260611-01_backend-lineage-metadata-test.md',
            'REVIEW_FILE': 'docs/delivery/05_reviews/REV-260611-03_rplan_P-0611-01_backend-lineage-metadata-test.md',
        },
        'submitted_at': '2026-06-11T07:48:56',
        'started_at': '2026-06-11T07:49:14',
        'completed_at': None,
        'error_message': None,
    }
    step_run = {'id': 'step-2', 'status': 'completed', 'outcome': 'approved', 'coder': 'claude'}
    next_step_run = {'id': 'step-3', 'step_name': 'promote_plan'}

    _write_backend_job_json(run=run, step_run=step_run, next_step_run=next_step_run, last_event='HUMAN_APPROVAL_REQUIRED')

    job_json = tmp_path / '.ukbe-runner/jobs/delivery_planning_v1/PLAN-20260611-38055dbf/job.json'
    assert job_json.exists()
    payload = json.loads(job_json.read_text(encoding='utf-8'))
    assert payload['job_id'] == 'PLAN-20260611-38055dbf'
    assert payload['template_group'] == 'delivery_planning_v1'
    assert payload['job_status'] == 'awaiting_human'
    assert payload['status'] == 'awaiting_human'
    assert payload['current_step'] == 'review_planner'
    assert payload['awaiting_human_step'] == 'review_planner'
    assert payload['context_payload']['PLAN_FILE'] == 'docs/delivery/02_plans/PLAN-20260611-01_backend-lineage-metadata-test.md'
    assert payload['current_step_status'] == 'completed'
    assert payload['next_step_name'] == 'promote_plan'
    assert payload['last_event'] == 'HUMAN_APPROVAL_REQUIRED'


def test_execute_step_command_uses_step_execution_spec_without_load_group(monkeypatch, tmp_path):
    _use_tmp_runner_home(monkeypatch, tmp_path)
    request_path = tmp_path / 'request.json'
    result_path = tmp_path / 'result.json'
    request_path.write_text(
        json.dumps(
            {
                'workflow_name': 'initiative_intake_v1',
                'template_group': 'initiative_intake_v1',
                'workflow_run_id': 'run-1',
                'workflow_step_run_id': 'step-1',
                'job_id': 'JOB-123',
                'step_name': 'pre_init',
                'project_root': str(tmp_path),
                'input_artifacts': {'DRAFT_INIT_FILE': 'docs/draft.md'},
                'step_execution_spec': {
                    'template_group': 'initiative_intake_v1',
                    'prompt_file': 'prompts/20_initiative_intake_v1/01_pre_init.txt',
                    'required_inputs': [{'artifact_key': 'DRAFT_INIT_FILE'}],
                    'raw_config': {},
                },
                'step_execution_spec': {
                    'template_group': 'initiative_intake_v1',
                    'step_name': 'pre_init',
                    'step_order': 1,
                    'step_sequence_no': 1,
                    'execution_kind': 'coder',
                    'prompt_file': 'dummy.txt',
                    'result_meta_key': 'PRE_INIT_FILE',
                    'required_inputs': [{'artifact_key': 'DRAFT_INIT_FILE', 'binding_type': 'required_input'}],
                    'produces': [{'artifact_key': 'PRE_INIT_FILE', 'binding_type': 'produces'}],
                    'coder_policy': {'default_coder': 'claude', 'allowed_coders': ['claude'], 'must_differ_from_previous_step': False},
                    'raw_config': {'prompt_file': 'dummy.txt'},
                },
            }
        ),
        encoding='utf-8',
    )

    monkeypatch.setattr(shared_runtime_deps, 'load_project_config', lambda workspace_root: {'default_workflow': 'default', 'workflows': {'initiative_intake_v1': {'path': '.'}}})
    monkeypatch.setattr(shared_runtime_deps, 'resolve_workflow_root', lambda workspace_root, workflow_name, config=None: runtime_context_module.PACKAGE_ROOT / 'bootstrap' / 'workflows' / 'default')
    monkeypatch.setattr(shared_runtime_deps, 'load_workflow_module', lambda workspace_root, workflow_name, config=None: _BOOTSTRAP_WORKFLOW_MODULE)
    monkeypatch.setattr(shared_runtime_deps, 'set_context', runtime_context_module.set_context)
    monkeypatch.setattr(shared_runtime_deps, 'set_workflow_module', runtime_context_module.set_workflow_module)
    monkeypatch.setattr(shared_runtime_deps, '_load_group', lambda group_name: (_ for _ in ()).throw(AssertionError('_load_group should not be used when step_execution_spec is provided')))
    monkeypatch.setattr(shared_runtime_deps, '_validate_static_reference_files', lambda *args, **kwargs: None)
    monkeypatch.setattr(
        shared_runtime_deps,
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


def test_execute_step_command_writes_result_file(monkeypatch, tmp_path):
    _use_tmp_runner_home(monkeypatch, tmp_path)
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
                'step_execution_spec': {
                    'template_group': 'initiative_intake_v1',
                    'prompt_file': 'prompts/20_initiative_intake_v1/01_pre_init.txt',
                    'required_inputs': [{'artifact_key': 'DRAFT_INIT_FILE'}],
                    'raw_config': {},
                },
            }
        ),
        encoding='utf-8',
    )

    monkeypatch.setattr(shared_runtime_deps, 'load_project_config', lambda workspace_root: {'default_workflow': 'default', 'workflows': {'initiative_intake_v1': {'path': '.'}}})
    monkeypatch.setattr(shared_runtime_deps, 'resolve_workflow_root', lambda workspace_root, workflow_name, config=None: runtime_context_module.PACKAGE_ROOT / 'bootstrap' / 'workflows' / 'default')
    monkeypatch.setattr(shared_runtime_deps, 'load_workflow_module', lambda workspace_root, workflow_name, config=None: _BOOTSTRAP_WORKFLOW_MODULE)
    monkeypatch.setattr(shared_runtime_deps, 'set_context', runtime_context_module.set_context)
    monkeypatch.setattr(shared_runtime_deps, 'set_workflow_module', runtime_context_module.set_workflow_module)
    monkeypatch.setattr(shared_runtime_deps, '_load_group', lambda group_name: {
        'job_prefix': 'PREINIT',
        'job_init_step': 'pre_init',
        'job_init_inputs': ['DRAFT_INIT_FILE'],
        'default_max_rejects': 2,
        'steps': ['pre_init'],
        'step_configs': {'pre_init': {'prompt_file': 'dummy.txt'}},
    })
    monkeypatch.setattr(shared_runtime_deps, '_validate_static_reference_files', lambda *args, **kwargs: None)
    monkeypatch.setattr(
        shared_runtime_deps,
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
    _use_tmp_runner_home(monkeypatch, tmp_path)
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
                'step_execution_spec': {
                    'template_group': 'initiative_intake_v1',
                    'prompt_file': 'prompts/20_initiative_intake_v1/01_pre_init.txt',
                    'required_inputs': [],
                    'raw_config': {},
                },
            }
        ),
        encoding='utf-8',
    )

    monkeypatch.setattr(shared_runtime_deps, 'load_project_config', lambda workspace_root: {'default_workflow': 'default', 'workflows': {'initiative_intake_v1': {'path': '.'}}})
    monkeypatch.setattr(shared_runtime_deps, 'resolve_workflow_root', lambda workspace_root, workflow_name, config=None: runtime_context_module.PACKAGE_ROOT / 'bootstrap' / 'workflows' / 'default')
    monkeypatch.setattr(shared_runtime_deps, 'load_workflow_module', lambda workspace_root, workflow_name, config=None: _BOOTSTRAP_WORKFLOW_MODULE)
    monkeypatch.setattr(shared_runtime_deps, 'set_context', runtime_context_module.set_context)
    monkeypatch.setattr(shared_runtime_deps, 'set_workflow_module', runtime_context_module.set_workflow_module)
    monkeypatch.setattr(shared_runtime_deps, '_load_group', lambda group_name: {
        'job_prefix': 'PREINIT',
        'job_init_step': 'pre_init',
        'job_init_inputs': [],
        'default_max_rejects': 2,
        'steps': ['pre_init'],
        'step_configs': {'pre_init': {'prompt_file': 'dummy.txt'}},
    })
    monkeypatch.setattr(shared_runtime_deps, '_validate_static_reference_files', lambda *args, **kwargs: None)
    monkeypatch.setattr(
        shared_runtime_deps,
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


def test_worker_command_once_processes_one_claim(monkeypatch, tmp_path):
    _use_tmp_runner_home(monkeypatch, tmp_path)
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
    monkeypatch.setattr(shared_runtime_deps, 'BackendClient', lambda backend_url: client)
    monkeypatch.setattr(
        shared_runtime_deps,
        '_invoke_execute_step_subprocess',
        lambda request_payload, engine_root=None: {
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
        shared_runtime_deps,
        '_submit_worker_result',
        lambda **kwargs: submit_calls.append(kwargs),
    )

    monkeypatch.setattr(shared_runtime_deps, '_resolve_worker_engine_root', lambda engine_root: (None, None))

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


def test_worker_command_once_exits_cleanly_when_no_claim(monkeypatch, tmp_path):
    _use_tmp_runner_home(monkeypatch, tmp_path)
    client = MagicMock()
    client.claim_step.return_value = {'step_run': None}
    monkeypatch.setattr(shared_runtime_deps, 'BackendClient', lambda backend_url: client)
    monkeypatch.setattr(shared_runtime_deps, '_resolve_worker_engine_root', lambda engine_root: (None, None))

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


def test_execute_backend_step_request_returns_failed_result_for_missing_meta_json(monkeypatch, tmp_path):
    _use_tmp_runner_home(monkeypatch, tmp_path)
    prompt_path = tmp_path / 'dummy.prompt'
    prompt_path.write_text('prompt body', encoding='utf-8')
    step_dir = tmp_path / 'job' / '01_pre_init'
    step_dir.mkdir(parents=True)

    request = ExecutionRequest.from_dict(
        {
            'workflow_name': 'initiative_intake_v1',
            'template_group': 'initiative_intake_v1',
            'workflow_run_id': 'run-1',
            'workflow_step_run_id': 'step-1',
            'job_id': 'JOB-123',
            'step_name': 'pre_init',
            'project_root': str(tmp_path),
            'input_artifacts': {'DRAFT_INIT_FILE': 'docs/draft.md'},
        }
    )
    group_cfg = {
        'job_prefix': 'PREINIT',
        'job_init_step': 'pre_init',
        'job_init_inputs': ['DRAFT_INIT_FILE'],
        'default_max_rejects': 2,
        'steps': ['pre_init'],
        'step_configs': {'pre_init': {'prompt_file': 'dummy.txt', 'required_inputs': ['DRAFT_INIT_FILE']}},
    }
    step_cfg = group_cfg['step_configs']['pre_init']
    state = _build_execution_state(request=request, group_cfg=group_cfg)

    draft_path = tmp_path / 'docs' / 'draft.md'
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text('draft', encoding='utf-8')

    monkeypatch.setattr(shared_runtime_deps, '_resolve_step_coder', lambda **kwargs: ('qwen', None))
    monkeypatch.setattr(shared_runtime_deps, 'resolve_prompt_path', lambda **kwargs: prompt_path)
    monkeypatch.setattr(shared_runtime_deps, 'build_context', lambda state, step, step_cfg: {})
    monkeypatch.setattr(shared_runtime_deps, 'render_prompt', lambda template_text, context: template_text)
    monkeypatch.setattr(shared_runtime_deps, 'prompt_checksum', lambda prompt_text: 'checksum')
    monkeypatch.setattr(shared_runtime_deps, 'make_step_dir', lambda group_cfg, state, step: step_dir)
    monkeypatch.setattr(shared_runtime_deps, 'check_preflight_artifact_status', lambda **kwargs: None)
    monkeypatch.setattr(shared_runtime_deps, 'ensure_planning_task_queue_integrity', lambda state, step: None)
    monkeypatch.setattr(shared_runtime_deps, 'ensure_execution_task_binding_integrity', lambda state, step: None)
    monkeypatch.setattr(shared_runtime_deps, '_missing_artifacts', lambda keys, state: [])

    def raise_missing_sidecar(**kwargs):
        raise run_agent_module.MetaJsonMissingError('Coder did not write meta.json to expected path: tmp/meta.json')

    monkeypatch.setattr(shared_runtime_deps, 'run_step', raise_missing_sidecar)

    result = run_agent_module._execute_backend_step_request(
        request=request,
        group_cfg=group_cfg,
        step_cfg=step_cfg,
        state=state,
        effective_root=tmp_path,
    )

    assert result.status == 'failed'
    assert result.outcome == 'failed'
    assert result.failure is not None
    assert result.failure.failure_code == 'PRE_RUN_FAILURE'
    assert result.failure.failure_source == 'runner'


def test_resolve_worker_engine_root_uses_global_only(monkeypatch, tmp_path):
    home = tmp_path / "home"
    global_cfg = home / ".ukbe-runner" / "config.json"
    global_ver = home / ".ukbe-runner" / "engine" / "versions" / "1.2.3"
    global_ver.mkdir(parents=True)
    global_cfg.parent.mkdir(parents=True, exist_ok=True)
    global_cfg.write_text('{"engine_version": "1.2.3"}', encoding='utf-8')
    monkeypatch.setattr(run_agent_module.Path, 'home', staticmethod(lambda: home))
    monkeypatch.setattr(shared_runtime_deps.Path, 'home', staticmethod(lambda: home))

    engine_root, version = run_agent_module._resolve_worker_engine_root(None)

    assert version == '1.2.3'
    assert engine_root == str(global_ver)

