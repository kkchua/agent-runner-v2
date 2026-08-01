"""[MOVED] V2 sync adapter — moved to v2/sync.py.

→ This file is kept as a redirect. Import from agent_runner_v2.v2.sync instead.
→ Architecture: docs/repo/agent_runner/sdlc/delivery/00_initiatives/INIT-20260801-002_platform-v2-architecture-redesign.md
"""
from .v2.sync import (  # noqa: F401
    build_v2_outcome_payload,
    is_v2_enabled,
    resolve_v2_backend_url,
    sync_outcome_v2,
)
