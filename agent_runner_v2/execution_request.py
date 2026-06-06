from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionRequest:
    workflow_name: str
    template_group: str
    step_name: str
    project_root: str
    workspace_root: str | None = None
    target_project_root: str | None = None
    workflow_run_id: str | None = None
    workflow_step_run_id: str | None = None
    job_id: str | None = None
    coder_override: str | None = None
    workflow_key_override: str | None = None
    env_overrides: dict[str, str] = field(default_factory=dict)
    input_artifacts: dict[str, str] = field(default_factory=dict)
    context_payload: dict[str, Any] = field(default_factory=dict)
    state_overrides: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> 'ExecutionRequest':
        workflow_name = str(payload.get('workflow_name') or payload.get('workflow') or 'default')
        template_group = str(payload.get('template_group') or payload.get('workflow_name') or '')
        step_name = str(payload.get('step_name') or payload.get('step') or '')
        project_root = str(payload.get('project_root') or payload.get('workspace_root') or '.')
        if not template_group:
            raise ValueError('Execution request requires template_group')
        if not step_name:
            raise ValueError('Execution request requires step_name')
        return cls(
            workflow_name=workflow_name,
            template_group=template_group,
            step_name=step_name,
            project_root=project_root,
            workspace_root=payload.get('workspace_root'),
            target_project_root=payload.get('target_project_root'),
            workflow_run_id=payload.get('workflow_run_id'),
            workflow_step_run_id=payload.get('workflow_step_run_id'),
            job_id=payload.get('job_id'),
            coder_override=payload.get('coder_override'),
            workflow_key_override=payload.get('workflow_key_override'),
            env_overrides=dict(payload.get('env_overrides') or {}),
            input_artifacts=dict(payload.get('input_artifacts') or payload.get('artifacts') or {}),
            context_payload=dict(payload.get('context_payload') or {}),
            state_overrides=dict(payload.get('state_overrides') or {}),
        )
