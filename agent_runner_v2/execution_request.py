from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ExecutionRequest:
    """Base execution request for running a workflow step.
    
    Used by both manual and daemon modes to specify what step to execute.
    """
    workflow_name: str
    template_group: str
    step_name: str
    project_root: str
    step_spec_source: str = "backend"
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
    step_execution_spec: dict[str, Any] = field(default_factory=dict)

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
            step_spec_source=str(payload.get('step_spec_source') or 'backend'),
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
            step_execution_spec=dict(payload.get('step_execution_spec') or {}),
        )


@dataclass
class WorkerRequest:
    """Machine-mode execution request from daemon/backend claiming.
    
    This is the standardized contract for daemon→run_agent.py communication.
    All fields are validated on construction.
    """
    workflow_name: str
    template_group: str
    job_id: str
    step_name: str
    step_sequence_no: int
    workflow_run_id: int | str  # Can be int (backend ID) or string (run_code)
    workflow_step_run_id: int | str
    project_root: str
    target_project_root: str | None
    input_artifacts: dict[str, str]
    context_payload: dict[str, Any]
    env_overrides: dict[str, str]
    coder_override: str | None
    workflow_key_override: str
    backend_url: str
    state_overrides: dict[str, Any]
    step_execution_spec: dict[str, Any]
    resolved_coder: dict[str, str | None]  # Summary from daemon: coder_alias, coder_used, coder_role, connection, model_id, source
    step_spec_source: str = "backend"  # "global" | "backend" | "hybrid"

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> 'WorkerRequest':
        """Parse and validate worker request from JSON payload.
        
        Args:
            payload: Dictionary from request.json file
            
        Returns:
            Validated WorkerRequest instance
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Required fields with validation
        workflow_name = _require_str(payload, 'workflow_name', 'Workflow name is required')
        template_group = _require_str(payload, 'template_group', 'Template group is required')
        job_id = _require_str(payload, 'job_id', 'Job ID is required')
        step_name = _require_str(payload, 'step_name', 'Step name is required')
        step_sequence_no = _require_int(payload, 'step_sequence_no', 'Step sequence number is required')
        workflow_run_id = payload.get('workflow_run_id')
        if workflow_run_id is None:
            raise ValueError('workflow_run_id is required')
        workflow_step_run_id = payload.get('workflow_step_run_id')
        if workflow_step_run_id is None:
            raise ValueError('workflow_step_run_id is required')
        project_root = _require_str(payload, 'project_root', 'Project root is required')
        
        # Optional fields with defaults
        target_project_root = payload.get('target_project_root')
        input_artifacts = dict(payload.get('input_artifacts') or {})
        context_payload = dict(payload.get('context_payload') or {})
        env_overrides = dict(payload.get('env_overrides') or {})
        coder_override = payload.get('coder_override')
        workflow_key_override = str(payload.get('workflow_key_override') or '')
        backend_url = str(payload.get('backend_url') or '')
        state_overrides = dict(payload.get('state_overrides') or {})
        step_execution_spec = dict(payload.get('step_execution_spec') or {})
        resolved_coder = dict(payload.get('resolved_coder') or {})
        step_spec_source = str(payload.get('step_spec_source') or 'backend')
        
        # Validate step_spec_source
        if step_spec_source not in {'global', 'backend', 'hybrid'}:
            raise ValueError(f'step_spec_source must be global, backend, or hybrid, got: {step_spec_source}')
        
        return cls(
            workflow_name=workflow_name,
            template_group=template_group,
            job_id=job_id,
            step_name=step_name,
            step_sequence_no=step_sequence_no,
            workflow_run_id=workflow_run_id,
            workflow_step_run_id=workflow_step_run_id,
            project_root=project_root,
            target_project_root=target_project_root,
            input_artifacts=input_artifacts,
            context_payload=context_payload,
            env_overrides=env_overrides,
            coder_override=coder_override,
            workflow_key_override=workflow_key_override,
            backend_url=backend_url,
            state_overrides=state_overrides,
            step_execution_spec=step_execution_spec,
            resolved_coder=resolved_coder,
            step_spec_source=step_spec_source,
        )
    
    @classmethod
    def from_file(cls, path: str | Path) -> 'WorkerRequest':
        """Load and validate worker request from JSON file.
        
        Args:
            path: Path to request.json file
            
        Returns:
            Validated WorkerRequest instance
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f'Request file not found: {path}')
        
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            raise ValueError(f'Invalid JSON in request file {path}: {exc}') from exc
        
        return cls.from_dict(payload)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'workflow_name': self.workflow_name,
            'template_group': self.template_group,
            'job_id': self.job_id,
            'step_name': self.step_name,
            'step_sequence_no': self.step_sequence_no,
            'workflow_run_id': self.workflow_run_id,
            'workflow_step_run_id': self.workflow_step_run_id,
            'project_root': self.project_root,
            'target_project_root': self.target_project_root,
            'input_artifacts': self.input_artifacts,
            'context_payload': self.context_payload,
            'env_overrides': self.env_overrides,
            'coder_override': self.coder_override,
            'workflow_key_override': self.workflow_key_override,
            'backend_url': self.backend_url,
            'state_overrides': self.state_overrides,
            'step_execution_spec': self.step_execution_spec,
            'resolved_coder': self.resolved_coder,
            'step_spec_source': self.step_spec_source,
        }


def _require_str(payload: dict[str, Any], key: str, message: str) -> str:
    """Require a string field in payload."""
    value = payload.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError(message)
    return str(value)


def _require_int(payload: dict[str, Any], key: str, message: str) -> int:
    """Require an integer field in payload."""
    value = payload.get(key)
    if value is None:
        raise ValueError(message)
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f'{message}, got non-integer: {value!r}') from None
