from __future__ import annotations

import datetime as dt
from typing import Any


def now_iso() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def set_last_failure(
    *,
    state: dict[str, Any],
    failure_class: str,
    failure_code: str,
    failure_reason: str,
    failure_source: str,
    step: str,
) -> None:
    state["last_failure_class"] = failure_class
    state["last_failure_code"] = failure_code
    state["last_failure_reason"] = failure_reason
    state["last_failure_source"] = failure_source
    state["pending_intervention_for"] = step if failure_class == "HUMAN_RETRY_REQUIRED" else None


def clear_last_failure(state: dict[str, Any]) -> None:
    state["last_failure_class"] = None
    state["last_failure_code"] = None
    state["last_failure_reason"] = None
    state["last_failure_source"] = None
    state["pending_intervention_for"] = None


def append_failure_history(
    *,
    state: dict[str, Any],
    step: str,
    failure_class: str,
    failure_code: str,
    failure_source: str,
) -> None:
    state.setdefault("failure_history", []).append(
        {
            "step": step,
            "failure_class": failure_class,
            "failure_code": failure_code,
            "failure_source": failure_source,
            "timestamp": now_iso(),
        }
    )
