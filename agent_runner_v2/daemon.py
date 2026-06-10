"""Worker daemon — dumb cron wrapper.

Invoked via: ukbe-run-agent daemon [worker-id]

Spawns `ukbe-run-agent poll` every N seconds. Zero logic, zero API calls.

Config resolution order (each setting):
  1. CLI arg / env var override  (useful for one-off dev worker)
  2. ~/.ukbe-runner/engine/config.json  (machine-level global config)
  3. Hardcoded default

Engine PYTHONPATH resolution order:
  1. AGENT_RUNNER_V2_SRC env var  → dev override (live source edits)
  2. ~/.ukbe-runner/engines/{version}/  → global engine store
  3. .ukbe-runner/engine/versions/{version}/  → repo-local fallback
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def _load_config() -> dict:
    local_cfg = Path(".ukbe-runner") / "engine" / "config.json"
    global_cfg = Path.home() / ".ukbe-runner" / "engine" / "config.json"
    path = local_cfg if local_cfg.exists() else global_cfg
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _setting(cfg: dict, env_key: str, config_key: str, default: str) -> str:
    return os.environ.get(env_key) or str(cfg.get(config_key) or default)


def _resolve_engine_pythonpath(cfg: dict, log) -> str | None:
    src = os.environ.get("AGENT_RUNNER_V2_SRC", "").strip()
    if src:
        log(f"engine: live source override ({src})")
        return src

    version = (cfg.get("engine_version") or "").strip()
    if not version or version == "SNAPSHOT":
        log(f"engine: version={version!r} — using ambient PYTHONPATH (dev mode)")
        return None

    global_dir = Path.home() / ".ukbe-runner" / "engines" / version
    local_dir = Path(".ukbe-runner") / "engine" / "versions" / version

    if global_dir.exists():
        log(f"engine: {version!r} resolved from global store ({global_dir})")
        return str(global_dir)
    if local_dir.exists():
        log(f"engine: {version!r} resolved from repo-local store ({local_dir})")
        return str(local_dir)

    log(f"engine: version {version!r} not found in global ({global_dir}) or local ({local_dir}) — "
        "run: ukbe-run-agent engine install <version>")
    return None


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent daemon",
        description="Worker daemon — spawns ukbe-run-agent poll on an interval.",
    )
    p.add_argument("worker_id", nargs="?", default="",
                   help="Worker ID (overrides config and WORKER_ID env var).")
    p.add_argument("--worker-label", default="", help="Queue label override (live or dev).")
    p.add_argument("--backend-url", default="", help="Backend URL override.")
    p.add_argument("--poll-seconds", type=int, default=0, help="Poll interval override.")
    p.add_argument("--log-file", default="", help="Log file path override.")
    args = p.parse_args(argv)

    cfg = _load_config()

    worker_id = args.worker_id or _setting(cfg, "WORKER_ID", "worker_id", "kode-worker-01")
    worker_label = args.worker_label or _setting(cfg, "WORKER_LABEL", "worker_label", "live")
    backend_url = args.backend_url or _setting(cfg, "AGENT_RUNNER_BACKEND_URL", "backend_url", "http://127.0.0.1:8100")
    poll_sec = args.poll_seconds or int(_setting(cfg, "WORKER_POLL_SEC", "poll_seconds", "5"))
    log_file = args.log_file or _setting(cfg, "WORKER_LOG_FILE", "log_file", "/tmp/worker-daemon.log")
    cli_cmd = os.environ.get("AGENT_RUNNER_CLI", "ukbe-run-agent").split()

    log_fd = open(log_file, "a")

    def log(msg: str) -> None:
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} [daemon] {msg}\n"
        sys.stdout.write(line)
        sys.stdout.flush()
        log_fd.write(line)
        log_fd.flush()

    engine_pythonpath = _resolve_engine_pythonpath(cfg, log)
    log(f"starting worker={worker_id} label={worker_label} poll={poll_sec}s backend={backend_url}")

    running = True

    def _sig(s, f):
        nonlocal running
        running = False
        log("shutting down")

    signal.signal(signal.SIGTERM, _sig)
    signal.signal(signal.SIGINT, _sig)

    while running:
        env = dict(os.environ)
        if engine_pythonpath:
            env["PYTHONPATH"] = engine_pythonpath + os.pathsep + env.get("PYTHONPATH", "")
        env["AGENT_RUNNER_BACKEND_URL"] = backend_url
        env["AGENT_RUNNER_WORKER_ID"] = worker_id
        env["WORKER_LABEL"] = worker_label
        try:
            result = subprocess.run(
                [*cli_cmd, "poll", "--worker-label", worker_label],
                capture_output=True, text=True, timeout=3600, env=env,
            )
            if result.stdout.strip():
                log(result.stdout.strip()[:500])
            if result.returncode != 0 and result.stderr.strip():
                log(f"exit={result.returncode} err={result.stderr.strip()[:300]}")
        except subprocess.TimeoutExpired:
            log("timeout")
        except Exception as e:
            log(f"error: {e}")
        time.sleep(poll_sec)

    log("stopped")
    return 0
