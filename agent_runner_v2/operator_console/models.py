from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GlobalSettings:
    backend_url: str
    worker_id: str
    worker_label: str


@dataclass(frozen=True)
class WorkflowEntry:
    name: str
    workflow_name: str
    template_group: str | None = None


@dataclass(frozen=True)
class RepoEntry:
    name: str
    path: str
    worker_id: str = ""
    workflows: tuple[WorkflowEntry, ...] = ()


@dataclass(frozen=True)
class ConsoleConfig:
    repos: tuple[RepoEntry, ...]


@dataclass(frozen=True)
class ActiveRunSummary:
    run_id: str
    run_code: str
    workflow_name: str
    status: str
    current_step: str
    updated_at: str
