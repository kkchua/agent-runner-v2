#!/usr/bin/env python3
"""
action_result.py — Return type for non-coder action functions.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ActionResult:
    status: str           # "APPROVED" | "REJECTED"
    remark: str
    artifacts: dict
    reject_code: str | None = None
