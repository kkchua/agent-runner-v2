"""Launch the operator console."""
from __future__ import annotations


def main(argv: list[str] | None = None) -> int:
    from .operator_console.app import main as app_main

    return app_main(argv)
