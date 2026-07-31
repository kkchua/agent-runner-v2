"""Show status of daemon and workers.

Invoked via: ukbe-run-agent status

Displays:
  - Daemon status (running/stopped, PID, worker_id)
  - Active workers (PIDs, run codes, steps, durations)
  - Backend connection status

Useful for monitoring the agent-runner system state.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from .config_loader import load_runner_config
from .runtime_context import GLOBAL_RUNNER_HOME


def _load_config() -> dict:
    """Load runner configuration from ~/.ukbe-runner/config.json."""
    return load_runner_config()


def _get_daemon_status() -> dict:
    """Check if daemon is running and return status info."""
    daemon_info = {
        "running": False,
        "pid": None,
        "worker_id": None,
        "started_at": None,
    }

    # Try psutil first
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'cmdline', 'create_time']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'run_agent' in ' '.join(cmdline) and 'daemon' in ' '.join(cmdline):
                    # Found daemon process
                    daemon_info["running"] = True
                    daemon_info["pid"] = proc.info['pid']
                    daemon_info["started_at"] = time.strftime(
                        "%Y-%m-%d %H:%M:%S",
                        time.localtime(proc.info['create_time'])
                    )

                    # Try to extract worker_id from command line
                    cmd_str = ' '.join(cmdline)
                    if '--worker-id' in cmd_str:
                        parts = cmd_str.split('--worker-id')
                        if len(parts) > 1:
                            daemon_info["worker_id"] = parts[1].split()[0].strip()

                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        pass  # psutil not available, use fallback

    # Fallback: Check if mutex exists (Windows)
    if sys.platform == "win32" and not daemon_info["running"]:
        try:
            import ctypes
            mutex = ctypes.windll.kernel32.OpenMutexW(0x100000, False, "Global\\ukbe-runner-daemon")
            if mutex:
                ctypes.windll.kernel32.CloseHandle(mutex)
                daemon_info["running"] = True
                daemon_info["note"] = "Mutex exists but process not found (psutil not installed)"
        except Exception:
            pass

    return daemon_info


def _get_worker_processes() -> list[dict]:
    """Find active worker processes spawned by daemon."""
    workers = []

    # Try psutil first
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'cmdline', 'create_time', 'cpu_percent', 'memory_info']):
            try:
                cmdline = proc.info.get('cmdline', [])
                cmd_str = ' '.join(cmdline)

                # Look for worker processes (run_agent run --mode daemon)
                if ('run_agent' in cmd_str and
                    'run' in cmd_str and
                    '--mode daemon' in cmd_str and
                    'daemon' not in cmd_str):  # Exclude daemon itself

                    worker_info = {
                        "pid": proc.info['pid'],
                        "started_at": time.strftime(
                            "%Y-%m-%d %H:%M:%S",
                            time.localtime(proc.info['create_time'])
                        ),
                        "duration_seconds": int(time.time() - proc.info['create_time']),
                    }

                    # Extract run info from command line
                    if '--template-group' in cmd_str:
                        parts = cmd_str.split('--template-group')
                        if len(parts) > 1:
                            worker_info["template_group"] = parts[1].split()[0].strip()

                    if '--job' in cmd_str:
                        parts = cmd_str.split('--job')
                        if len(parts) > 1:
                            worker_info["step_name"] = parts[1].split()[0].strip()

                    if '--job-no' in cmd_str:
                        parts = cmd_str.split('--job-no')
                        if len(parts) > 1:
                            run_code = parts[1].split()[0].strip()
                            worker_info["run_code"] = run_code

                    workers.append(worker_info)

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except ImportError:
        # psutil not available, return empty list with note
        workers.append({
            "note": "Install psutil for detailed worker process info: pip install psutil",
        })

    return workers


def _get_runtime_dir_info() -> dict:
    """Get info from runtime directory."""
    runtime_dir = GLOBAL_RUNNER_HOME / "runtime" / "worker"

    info = {
        "runtime_dir": str(runtime_dir),
        "active_files": 0,
        "recent_files": [],
    }

    if not runtime_dir.exists():
        return info

    # Count active files in runtime dir
    try:
        files = list(runtime_dir.iterdir())
        info["active_files"] = len(files)

        # Get 5 most recent files
        files_with_mtime = [(f, f.stat().st_mtime) for f in files if f.is_file()]
        files_with_mtime.sort(key=lambda x: x[1], reverse=True)

        for f, mtime in files_with_mtime[:5]:
            info["recent_files"].append({
                "name": f.name,
                "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
            })

    except Exception:
        pass

    return info


def _get_backend_status() -> dict:
    """Check backend connectivity."""
    cfg = _load_config()
    backend_url = str(cfg.get("backend_url") or "").strip() or "http://localhost:8100"

    status = {
        "url": backend_url,
        "reachable": False,
        "error": None,
    }

    try:
        import urllib.request
        req = urllib.request.Request(
            f"{backend_url}/health",
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                status["reachable"] = True
    except Exception as e:
        status["error"] = str(e)

    return status


def main(argv: list[str] | None = None) -> int:
    """Show status of daemon and workers.

    Parameters
    ----------
    argv :
        Command-line arguments (excluding the program name).

    Returns
    -------
    int
        0 on success, 1 on error.
    """
    import argparse

    parser = argparse.ArgumentParser(
        prog="ukbe-run-agent status",
        description="Show status of daemon and workers.",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON (default: human-readable)")
    args = parser.parse_args(argv)

    try:
        daemon_status = _get_daemon_status()
        workers = _get_worker_processes()
        runtime_info = _get_runtime_dir_info()
        backend_status = _get_backend_status()

        status = {
            "daemon": daemon_status,
            "workers": workers,
            "workers_count": len(workers),
            "runtime": runtime_info,
            "backend": backend_status,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if args.json:
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            # Human-readable output
            print("=" * 60)
            print("Agent Runner Status")
            print("=" * 60)
            print()

            # Daemon status
            print(f"Daemon: {'RUNNING' if daemon_status['running'] else 'STOPPED'}")
            if daemon_status['running']:
                print(f"  PID:         {daemon_status['pid']}")
                print(f"  Worker ID:   {daemon_status.get('worker_id', 'unknown')}")
                print(f"  Started:     {daemon_status.get('started_at', 'unknown')}")
            print()

            # Workers
            print(f"Workers: {len(workers)} active")
            for worker in workers:
                if 'note' in worker:
                    print(f"  Note: {worker['note']}")
                else:
                    print(f"  PID {worker.get('pid', 'unknown')}: {worker.get('template_group', 'unknown')}")
                    print(f"    Run:    {worker.get('run_code', 'unknown')}")
                    print(f"    Step:   {worker.get('step_name', 'unknown')}")
                    print(f"    Time:   {worker.get('duration_seconds', 0)}s")
                print()

            # Runtime
            print(f"Runtime: {runtime_info['active_files']} files in worker dir")
            print()

            # Backend
            print(f"Backend: {'CONNECTED' if backend_status['reachable'] else 'UNREACHABLE'}")
            print(f"  URL: {backend_status['url']}")
            if backend_status['error']:
                print(f"  Error: {backend_status['error']}")
            print()

            print("=" * 60)

        return 0

    except Exception as exc:
        error_output = {
            "status": "error",
            "message": str(exc),
        }
        print(json.dumps(error_output, indent=2, ensure_ascii=False), file=sys.stderr)
        return 1
