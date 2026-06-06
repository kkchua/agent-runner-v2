from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ExecutionFailure:
    failure_class: str
    failure_code: str
    failure_reason: str
    failure_source: str


@dataclass
class ExecutionResult:
    status: str
    outcome: str
    step_name: str
    coder_used: str | None = None
    remark: str = ''
    artifacts: dict[str, str] = field(default_factory=dict)
    meta_json_path: str | None = None
    review: dict[str, Any] | None = None
    usage: dict[str, Any] = field(default_factory=dict)
    failure: ExecutionFailure | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.failure is None:
            payload['failure'] = None
        return payload
