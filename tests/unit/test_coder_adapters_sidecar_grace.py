from __future__ import annotations

import os
import sys
from pathlib import Path

from agent_runner_v2 import coder_adapters


def test_run_with_sidecar_poll_allows_post_sidecar_grace(monkeypatch, tmp_path: Path):
    sidecar_path = tmp_path / "meta.json"
    monkeypatch.setattr(coder_adapters, "SIDECAR_POLL_INTERVAL_SECONDS", 0.01)
    monkeypatch.setattr(coder_adapters, "SIDECAR_SETTLE_DELAY_SECONDS", 0.0)
    monkeypatch.setattr(coder_adapters, "SIDECAR_POST_COMPLETE_GRACE_SECONDS", 0.5)

    script = (
        "import json, pathlib, sys, time; "
        "sidecar = pathlib.Path(sys.argv[1]); "
        "sidecar.write_text(json.dumps({'schema_version':'v2','coder_result':"
        "{'status':'APPROVED','remark':'ok','artifacts':{},'recorded_at':'2026-07-10T00:00:00+00:00'}}), encoding='utf-8'); "
        "print('SIDEcar_WRITTEN', flush=True); "
        "time.sleep(0.1); "
        "print('AFTER_SIDECAR', flush=True)"
    )

    rc, stdout, stderr = coder_adapters._run_with_sidecar_poll(
        [sys.executable, "-c", script, str(sidecar_path)],
        cwd=tmp_path,
        env=os.environ.copy(),
        timeout_seconds=5,
        sidecar_path=sidecar_path,
        step="test_step",
    )

    assert rc == 0
    assert "SIDEcar_WRITTEN" in stdout
    assert "AFTER_SIDECAR" in stdout
    assert stderr == ""
