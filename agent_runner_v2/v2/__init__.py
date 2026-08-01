"""V2 daemon — backend-authoritative state machine mode.

Architecture reference:
    docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260801-002_platform-v2-architecture-redesign.md

The V2 daemon is a thin claim→spawn→report worker. The backend owns all
state transitions via its two-field model (run_status + action_requested).
The CLI is a pure execution engine.

Modules:
    daemon.py        — V2 supervisor loop and child process spawning
    backend_client.py — HTTP client for the V2 backend API
    sync.py           — Outcome-only sync adapter (CLI → V2 backend)
"""
