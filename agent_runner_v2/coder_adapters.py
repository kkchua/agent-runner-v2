from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .runtime_context import PROJECT_ROOT, RUNNER_ROOT


@dataclass
class CoderInvocationError(Exception):
    message: str
    command: list[str]
    return_code: int
    stdout: str
    stderr: str
    raw_events: list[str]

    def __str__(self) -> str:
        return self.message


@dataclass
class UsageData:
    step: str
    coder_used: str
    usage_source: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    cost: float | None
    duration_ms: int | None
    started_at: str
    finished_at: str


@dataclass
class InvocationManifest:
    step_name: str
    coder_used: str
    command: list[str]
    cwd: str
    prompt_checksum: str
    started_at: str
    finished_at: str
    return_code: int


@dataclass
class InvocationResult:
    return_code: int
    stdout: str
    stderr: str
    parsed_result: dict[str, Any]
    usage: UsageData
    manifest: InvocationManifest
    raw_events: list[str]


DEFAULT_CODER_TIMEOUT_SECONDS = 600
SIDECAR_POLL_INTERVAL_SECONDS = 3.0
SIDECAR_SETTLE_DELAY_SECONDS = 5.0  # Increased from 0.5s to ensure coder finishes writing meta.json
DEFAULT_SIDECAR_POST_COMPLETE_GRACE_SECONDS = 12.0  # Allow final progress updates / cleanup before forced termination
_ACTIVE_CODER_PROCS: set[subprocess.Popen[Any]] = set()
_ACTIVE_CODER_PROCS_LOCK = threading.Lock()


def _load_global_config() -> dict:
    r"""Load the global config.json from %USERPROFILE%\.ukbe-runner\config.json."""
    config_path = Path.home() / ".ukbe-runner" / "config.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _coder_timeout_seconds(override: int | None = None) -> int:
    """Resolve coder timeout with cascading priority:
    
    1. Step-level override (timeout_seconds_override parameter)
    2. Environment variable (AGENT_RUNNER_CODER_TIMEOUT_SECONDS)
    3. Global config.json (coder_timeout_seconds key)
    4. Hardcoded default (DEFAULT_CODER_TIMEOUT_SECONDS = 600)
    """
    # Priority 1: Step-level override
    if isinstance(override, int) and override > 0:
        return override
    
    # Priority 2: Environment variable
    raw = os.environ.get("AGENT_RUNNER_CODER_TIMEOUT_SECONDS", "").strip()
    if raw:
        try:
            value = int(raw)
            return value if value > 0 else DEFAULT_CODER_TIMEOUT_SECONDS
        except ValueError:
            pass
    
    # Priority 3: Global config.json
    cfg = _load_global_config()
    config_timeout = cfg.get("coder_timeout_seconds")
    if isinstance(config_timeout, (int, float)) and config_timeout > 0:
        return int(config_timeout)
    
    # Priority 4: Hardcoded default
    return DEFAULT_CODER_TIMEOUT_SECONDS


def _sidecar_post_complete_grace_seconds() -> float:
    """Resolve post-sidecar grace window priority:

    1. Environment variable: AGENT_RUNNER_SIDECAR_POST_COMPLETE_GRACE_SECONDS
    2. Global config.json: sidecar_post_complete_grace_seconds
    3. Hardcoded default
    """
    raw = os.environ.get("AGENT_RUNNER_SIDECAR_POST_COMPLETE_GRACE_SECONDS", "").strip()
    if raw:
        try:
            value = float(raw)
            if value >= 0:
                return value
        except ValueError:
            pass

    cfg = _load_global_config()
    config_value = cfg.get("sidecar_post_complete_grace_seconds")
    if isinstance(config_value, (int, float)) and config_value >= 0:
        return float(config_value)

    return DEFAULT_SIDECAR_POST_COMPLETE_GRACE_SECONDS


def _coerce_timeout_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def dataclass_dict(value: UsageData | InvocationManifest) -> dict[str, Any]:
    return asdict(value)


def _is_valid_sidecar_json(path: Path) -> bool:
    """Return True iff path contains a fully valid meta.json matching the step_runner schema.

    Mirrors the validation in _read_and_validate_meta_json() so we never trigger early exit
    on a partially-written sidecar (race condition: coder writes status before recorded_at).
    Required fields: schema_version, coder_result.status, coder_result.artifacts, coder_result.recorded_at.

    Also checks for file write completion to avoid reading partially-written or locked files.
    """
    try:
        # Check 1: File must be readable and not locked by checking if we can get its stat
        try:
            stat1 = path.stat()
            print(f"[_is_valid_sidecar_json] Check 1 PASS: file stat successful, size={stat1.st_size}, mtime={stat1.st_mtime}", flush=True)
        except (OSError, IOError) as e:
            # File is locked or inaccessible
            print(f"[_is_valid_sidecar_json] Check 1 FAIL: file stat failed: {e}", flush=True)
            return False

        # Check 2: Verify file modification is stable (not still being written)
        # Get mtime, wait 100ms, check again - if it changed, file is still being written
        import time as time_module
        mtime1 = stat1.st_mtime
        time_module.sleep(0.1)
        try:
            stat2 = path.stat()
            mtime2 = stat2.st_mtime
        except (OSError, IOError) as e:
            print(f"[_is_valid_sidecar_json] Check 2 FAIL: second stat failed: {e}", flush=True)
            return False

        if mtime1 != mtime2:
            # File is still being modified, not ready yet
            print(f"[_is_valid_sidecar_json] Check 2 FAIL: mtime changed {mtime1} -> {mtime2}, file still being written", flush=True)
            return False

        print(f"[_is_valid_sidecar_json] Check 2 PASS: mtime stable at {mtime1}", flush=True)

        # Check 3: Parse and validate JSON schema
        try:
            text_content = path.read_text(encoding="utf-8-sig")
            data = json.loads(text_content)
            print(f"[_is_valid_sidecar_json] Check 3a PASS: JSON parsed successfully, size={len(text_content)} bytes", flush=True)
        except Exception as e:
            print(f"[_is_valid_sidecar_json] Check 3a FAIL: JSON parse failed: {e}", flush=True)
            return False

        if not isinstance(data, dict):
            print(f"[_is_valid_sidecar_json] Check 3b FAIL: data is not dict, type={type(data)}", flush=True)
            return False
        # Accept v2 schema or legacy artifact_meta_v1
        sv = data.get("schema_version") or data.get("sidecar_version") or ""
        if sv not in ("v2", "artifact_meta_v1"):
            print(f"[_is_valid_sidecar_json] Check 3c FAIL: invalid schema version: {sv!r}", flush=True)
            return False
        cr = data.get("coder_result")
        if not isinstance(cr, dict):
            print(f"[_is_valid_sidecar_json] Check 3d FAIL: coder_result not dict", flush=True)
            return False
        status = str(cr.get("status", "")).upper()
        if status not in ("APPROVED", "REJECTED"):
            print(f"[_is_valid_sidecar_json] Check 3e FAIL: invalid status: {status!r}", flush=True)
            return False
        if not isinstance(cr.get("artifacts"), dict):
            print(f"[_is_valid_sidecar_json] Check 3f FAIL: artifacts not dict", flush=True)
            return False
        if not str(cr.get("recorded_at") or "").strip():
            print(f"[_is_valid_sidecar_json] Check 3g FAIL: missing recorded_at", flush=True)
            return False
        print(f"[_is_valid_sidecar_json] Check 3 PASS: schema valid (version={sv}, status={status})", flush=True)
        return True
    except Exception as e:
        print(f"[_is_valid_sidecar_json] UNEXPECTED EXCEPTION: {e}", flush=True)
        return False


def _save_terminal_settings() -> Any:
    """Save current terminal settings. Returns None if stdin is not a tty."""
    try:
        import termios
        import sys
        fd = sys.stdin.fileno()
        return termios.tcgetattr(fd)
    except Exception:
        return None


def _restore_terminal_settings(saved: Any) -> None:
    """Restore previously saved terminal settings. No-op if saved is None."""
    if saved is None:
        return
    try:
        import termios
        import sys
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, saved)
    except Exception:
        pass


def _terminate_process_tree(proc: subprocess.Popen[Any]) -> None:
    """Terminate a process and its children, using taskkill on Windows."""
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
            )
            return
        except Exception:
            pass


def _register_active_coder_proc(proc: subprocess.Popen[Any]) -> None:
    with _ACTIVE_CODER_PROCS_LOCK:
        _ACTIVE_CODER_PROCS.add(proc)


def _unregister_active_coder_proc(proc: subprocess.Popen[Any]) -> None:
    with _ACTIVE_CODER_PROCS_LOCK:
        _ACTIVE_CODER_PROCS.discard(proc)


def abort_active_coder_processes(*, reason: str = "interrupt") -> int:
    """Terminate all currently tracked coder process trees.

    Returns the number of active processes that were targeted.
    """
    with _ACTIVE_CODER_PROCS_LOCK:
        procs = list(_ACTIVE_CODER_PROCS)

    if procs:
        print(
            f"[coder_adapters] abort_active_coder_processes: terminating {len(procs)} active coder process(es) due to {reason}",
            flush=True,
        )
    for proc in procs:
        _terminate_process_tree(proc)
        _unregister_active_coder_proc(proc)
    return len(procs)
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def _run_with_sidecar_poll(
    cmd: list[str],
    *,
    cwd: Path,
    env: dict | None = None,
    input_text: str | None = None,
    timeout_seconds: int,
    sidecar_path: Path | None = None,
    step: str = "",
) -> tuple[int, str, str]:
    """Launch cmd via Popen, polling for sidecar completion as an early-exit signal.

    If sidecar_path is provided and becomes valid before the process exits, the
    process is terminated and rc=0 is returned — allowing the runner to proceed
    without waiting the full timeout.

    Returns:
        (return_code, stdout, stderr)

    Raises:
        subprocess.TimeoutExpired — if neither the process nor the sidecar is ready
                                    within timeout_seconds.
    """
    import threading

    # Record pre-existing sidecar mtime so we don't mistake a stale sidecar from a
    # previous run as a completion signal for this invocation.
    sidecar_pre_mtime: float | None = None
    if sidecar_path is not None:
        try:
            sidecar_pre_mtime = sidecar_path.stat().st_mtime if sidecar_path.exists() else None
        except OSError:
            sidecar_pre_mtime = None

    # Save terminal settings before launching coder — some CLIs (e.g. claude) put
    # the terminal into raw mode and may not restore it if terminated early.
    saved_terminal = _save_terminal_settings()

    try:
        # Windows: cmd.exe must wrap .cmd/.bat shims since CreateProcess
        # does not resolve PATHEXT (npm-installed CLIs like qwen.cmd).
        if os.name == "nt":
            resolved = shutil.which(cmd[0])
            if resolved and resolved.lower().endswith((".cmd", ".bat")):
                cmd = ["cmd", "/c"] + cmd

        # Inject PYTHONPATH so agent_tools is importable by coder tool commands
        # without sys.path.insert (avoids PowerShell quoting issues on Windows).
        proc_env = dict(env) if env else dict(os.environ)
        _tools_dir = str((Path(__file__).parent / "tools").resolve())
        _existing_pp = proc_env.get("PYTHONPATH", "")
        proc_env["PYTHONPATH"] = _tools_dir + (os.pathsep + _existing_pp if _existing_pp else "")

        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            env=proc_env,
            stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        _register_active_coder_proc(proc)
        if input_text is not None:
            proc.stdin.write(input_text)
            proc.stdin.close()

        chunks_out: list[str] = []
        chunks_err: list[str] = []

        def _drain(pipe: Any, buf: list[str]) -> None:
            for line in pipe:
                buf.append(line)

        t_out = threading.Thread(target=_drain, args=(proc.stdout, chunks_out), daemon=True)
        t_err = threading.Thread(target=_drain, args=(proc.stderr, chunks_err), daemon=True)
        t_out.start()
        t_err.start()

        deadline = time.monotonic() + timeout_seconds
        sidecar_triggered = False
        poll_count = 0
        post_sidecar_grace_seconds = _sidecar_post_complete_grace_seconds()

        # Polling loop: Wait for EITHER condition to be true:
        # 1. Process exits (proc.poll() returns non-None) - normal completion
        # 2. Sidecar (meta.json) becomes valid - coder finished work but didn't exit (common with hanging processes)
        # This OR condition prevents indefinite hangs while respecting the coder's completion signal
        while True:
            poll_count += 1
            # Condition 1: Check if process exited
            poll_result = proc.poll()
            if poll_result is not None:
                print(f"[coder_adapters] poll #{poll_count}: process exited with return_code={poll_result}", flush=True)
                break
            # Check timeout
            time_remaining = deadline - time.monotonic()
            if time_remaining <= 0:
                print(f"[coder_adapters] poll #{poll_count}: TIMEOUT after {timeout_seconds}s, terminating process", flush=True)
                _terminate_process_tree(proc)
                t_out.join(timeout=2)
                t_err.join(timeout=2)
                raise subprocess.TimeoutExpired(cmd, timeout_seconds)

            # Condition 2: Check if sidecar (meta.json) became valid
            # This is the critical early-exit signal for hung processes that complete their work
            if sidecar_path is not None:
                if not sidecar_path.exists():
                    if poll_count % 20 == 1:  # Log every 60 seconds
                        print(f"[coder_adapters] poll #{poll_count}: sidecar not yet created, waiting... ({time_remaining:.1f}s remaining)", flush=True)
                else:
                    try:
                        current_mtime = sidecar_path.stat().st_mtime
                    except OSError:
                        current_mtime = None
                        print(f"[coder_adapters] poll #{poll_count}: sidecar exists but stat failed", flush=True)
                    if current_mtime is not None:
                        is_new_sidecar = (
                            sidecar_pre_mtime is None or current_mtime > sidecar_pre_mtime
                        )
                        if is_new_sidecar:
                            print(f"[coder_adapters] poll #{poll_count}: sidecar is new/updated, validating JSON...", flush=True)
                            if _is_valid_sidecar_json(sidecar_path):
                                # Sidecar is valid: coder finished its work!
                                # Pause briefly to ensure coder finishes all writes to meta.json,
                                # then allow a short grace window for final progress callbacks.
                                print(f"[coder_adapters] poll #{poll_count}: sidecar JSON valid! sleeping {SIDECAR_SETTLE_DELAY_SECONDS}s before grace window", flush=True)
                                time.sleep(SIDECAR_SETTLE_DELAY_SECONDS)
                                sidecar_triggered = True
                                label = f" step={step}" if step else ""
                                grace_deadline = time.monotonic() + post_sidecar_grace_seconds
                                exited_during_grace = False
                                while time.monotonic() < grace_deadline:
                                    poll_result = proc.poll()
                                    if poll_result is not None:
                                        exited_during_grace = True
                                        print(f"[coder_adapters] sidecar detected — process exited naturally during grace window return_code={poll_result}{label}", flush=True)
                                        break
                                    time.sleep(0.1)
                                if not exited_during_grace:
                                    print(f"[coder_adapters] sidecar detected — grace window ({post_sidecar_grace_seconds}s) elapsed, terminating process{label}", flush=True)
                                    _terminate_process_tree(proc)
                                break
                            else:
                                print(f"[coder_adapters] poll #{poll_count}: sidecar exists but JSON validation failed", flush=True)
                        elif poll_count % 20 == 1:
                            print(
                                "[coder_adapters] poll "
                                f"#{poll_count}: sidecar exists but is unchanged since start "
                                f"(mtime={current_mtime}); waiting... ({time_remaining:.1f}s remaining)",
                                flush=True,
                            )
            time.sleep(SIDECAR_POLL_INTERVAL_SECONDS)

        t_out.join(timeout=5)
        t_err.join(timeout=5)
        rc = 0 if sidecar_triggered else (proc.returncode if proc.returncode is not None else 0)
        exit_reason = "sidecar_detected" if sidecar_triggered else f"process_exited_rc={rc}"
        print(f"[coder_adapters] exiting polling loop: {exit_reason}, total_polls={poll_count}, elapsed={(time.monotonic() - (deadline - timeout_seconds)):.1f}s", flush=True)
        return rc, "".join(chunks_out), "".join(chunks_err)
    except BaseException:
        if 'proc' in locals():
            print("[coder_adapters] interrupt/error during coder polling; terminating active process tree", flush=True)
            _terminate_process_tree(proc)
            if 't_out' in locals():
                t_out.join(timeout=2)
            if 't_err' in locals():
                t_err.join(timeout=2)
        raise
    finally:
        if 'proc' in locals():
            _unregister_active_coder_proc(proc)
        _restore_terminal_settings(saved_terminal)


from .runner_logger import log_invocation_result, log_invocation_start
from .coder_registry import get_api_key


def _mask_api_key(key: str) -> str:
    if len(key) <= 8:
        return "****"
    return key[:4] + "****" + key[-4:]


def _log_command_for_step(step: str, command: list[str], cc: dict[str, Any], *, coder_name: str = "qwen") -> None:
    """Print invocation summary to console (not the full command)."""
    model = cc.get("model", "")
    model_id = cc.get("model_id", "")
    connection = cc.get("connection", "")
    auth = cc.get("auth_type", "")
    api_key_env = cc.get("openai_api_key_env", "")
    base_url = cc.get("openai_base_url", "")
    agent = str(cc.get("agent") or "").strip()

    api_key_val = ""
    if api_key_env:
        raw = os.environ.get(api_key_env, "")
        api_key_val = f"key={_mask_api_key(raw)}" if raw else f"key=({api_key_env} not set)"

    parts = [f"coder={coder_name}"]
    if connection:
        parts.append(f"connection={connection}")
    if model_id:
        parts.append(f"model_id={model_id}")
    if model:
        parts.append(f"model={model}")
    if auth:
        parts.append(f"auth={auth}")
    if api_key_val:
        parts.append(api_key_val)
    if base_url:
        parts.append(f"base_url={base_url}")
    if agent:
        parts.append(f"agent={agent}")

    print(f"  [{step}] {' '.join(parts)}", flush=True)


def _load_env_files() -> None:
    """Load .env files from project root and runner root if present."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    # Project root .env
    project_env = PROJECT_ROOT / ".env"
    if project_env.exists():
        load_dotenv(dotenv_path=project_env)
    # Runner root .env (fallback)
    runner_env = RUNNER_ROOT / ".env"
    if runner_env.exists():
        load_dotenv(dotenv_path=runner_env)


_env_loaded = False


def _ensure_env_loaded() -> None:
    global _env_loaded
    if not _env_loaded:
        _load_env_files()
        _env_loaded = True


def invoke_coder(
    *,
    coder: str,
    step: str,
    prompt_text: str,
    cwd: Path,
    prompt_checksum: str,
    now_iso_fn,
    coder_config: dict[str, Any] | None = None,
    sidecar_path: Path | None = None,
    timeout_seconds_override: int | None = None,
) -> InvocationResult:
    _ensure_env_loaded()
    cc = coder_config or {}
    model_name = cc.get("model", "")
    model_id = cc.get("model_id", "")
    connection = cc.get("connection", "")
    auth_type = cc.get("auth_type", "")

    log_invocation_start(
        step,
        coder,
        model=model_name,
        model_id=model_id,
        connection=connection,
        auth_type=auth_type,
    )

    started_at = now_iso_fn()
    started_monotonic = time.monotonic()
    if coder == "codex":
        result = _invoke_codex(step=step, prompt_text=prompt_text, cwd=cwd, sidecar_path=sidecar_path, timeout_seconds_override=timeout_seconds_override)
    elif coder == "claude":
        result = _invoke_claude(step=step, prompt_text=prompt_text, cwd=cwd, sidecar_path=sidecar_path, coder_config=cc, timeout_seconds_override=timeout_seconds_override)
    elif coder == "qwen":
        result = _invoke_qwen(step=step, prompt_text=prompt_text, cwd=cwd, coder_config=cc, sidecar_path=sidecar_path, timeout_seconds_override=timeout_seconds_override)
    elif coder == "opencode":
        result = _invoke_opencode(step=step, prompt_text=prompt_text, cwd=cwd, coder_config=cc, sidecar_path=sidecar_path, timeout_seconds_override=timeout_seconds_override)
    else:
        result = _invoke_plain(coder=coder, step=step, prompt_text=prompt_text, cwd=cwd, sidecar_path=sidecar_path, timeout_seconds_override=timeout_seconds_override)
    finished_at = now_iso_fn()
    duration_ms = int((time.monotonic() - started_monotonic) * 1000)

    return_code = result["return_code"]
    status = "OK" if return_code == 0 else "FAILED"

    usage = result["usage"]
    usage.step = step
    usage.coder_used = coder
    usage.duration_ms = duration_ms
    usage.started_at = started_at
    usage.finished_at = finished_at

    log_invocation_result(
        step, coder, model=model_name, model_id=model_id, connection=connection, auth_type=auth_type,
        return_code=return_code, duration_ms=duration_ms, status=status,
        usage=dataclass_dict(usage),
    )

    manifest = InvocationManifest(
        step_name=step,
        coder_used=coder,
        command=result["command"],
        cwd=str(cwd),
        prompt_checksum=prompt_checksum,
        started_at=started_at,
        finished_at=finished_at,
        return_code=return_code,
    )

    return InvocationResult(
        return_code=return_code,
        stdout=result["stdout"],
        stderr=result["stderr"],
        parsed_result=result["parsed_result"],
        usage=usage,
        manifest=manifest,
        raw_events=result.get("raw_events", []),
    )


def _invoke_plain(*, coder: str, step: str, prompt_text: str, cwd: Path, sidecar_path: Path | None = None, timeout_seconds_override: int | None = None) -> dict[str, Any]:
    command = [coder]
    timeout_seconds = _coder_timeout_seconds(timeout_seconds_override)
    try:
        return_code, stdout, stderr = _run_with_sidecar_poll(
            command,
            cwd=cwd,
            input_text=prompt_text,
            timeout_seconds=timeout_seconds,
            sidecar_path=sidecar_path,
            step=step,
        )
    except subprocess.TimeoutExpired as exc:
        raise CoderInvocationError(
            message=f"Coder subprocess timed out after {timeout_seconds} seconds.",
            command=command,
            return_code=124,
            stdout=_coerce_timeout_output(exc.stdout),
            stderr=_coerce_timeout_output(exc.stderr),
            raw_events=[],
        ) from exc
    parsed_result = _extract_json_object(stdout) if stdout.strip() else {}
    return {
        "command": command,
        "return_code": return_code,
        "stdout": stdout,
        "stderr": stderr,
        "parsed_result": parsed_result,
        "usage": UsageData(
            step=step,
            coder_used=coder,
            usage_source="not_available",
            input_tokens=None,
            output_tokens=None,
            total_tokens=None,
            cost=None,
            duration_ms=None,
            started_at="",
            finished_at="",
        ),
        "raw_events": [],
    }


def _invoke_codex(*, step: str, prompt_text: str, cwd: Path, sidecar_path: Path | None = None, timeout_seconds_override: int | None = None) -> dict[str, Any]:
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", delete=False) as temp_output:
        output_path = Path(temp_output.name)
    command = [
        "codex",
        "exec",
        "--sandbox",
        "danger-full-access",
        "--json",
        "-o",
        str(output_path),
        "-",
    ]
    timeout_seconds = _coder_timeout_seconds(timeout_seconds_override)
    try:
        try:
            return_code, stdout, stderr = _run_with_sidecar_poll(
                command,
                cwd=cwd,
                input_text=prompt_text,
                timeout_seconds=timeout_seconds,
                sidecar_path=sidecar_path,
                step=step,
            )
        except subprocess.TimeoutExpired as exc:
            raise CoderInvocationError(
                message=f"Codex subprocess timed out after {timeout_seconds} seconds.",
                command=command,
                return_code=124,
                stdout=_coerce_timeout_output(exc.stdout),
                stderr=_coerce_timeout_output(exc.stderr),
                raw_events=[],
            ) from exc
        raw_events = [line for line in stdout.splitlines() if line.strip()]
        output_text = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        codex_error = _extract_codex_error_from_events(raw_events)
        if codex_error and not output_text.strip():
            raise CoderInvocationError(
                message=f"Codex returned no structured result. Last codex error: {codex_error}",
                command=command,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                raw_events=raw_events,
            )
        try:
            if output_text.strip():
                parsed_result = _extract_json_object(output_text)
            elif stdout.strip():
                parsed_result = _extract_json_object(stdout)
            else:
                parsed_result = {}  # sidecar-triggered: stdout empty, sidecar is authoritative
        except ValueError as exc:
            raise CoderInvocationError(
                message=f"Failed to extract structured result from codex output: {exc}",
                command=command,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                raw_events=raw_events,
            ) from exc
        usage = _usage_from_json_events(raw_events, step=step, coder="codex")
        return {
            "command": command,
            "return_code": return_code,
            "stdout": stdout,
            "stderr": stderr,
            "parsed_result": parsed_result,
            "usage": usage,
            "raw_events": raw_events,
        }
    finally:
        output_path.unlink(missing_ok=True)


def _extract_codex_error_from_events(lines: list[str]) -> str | None:
    last_error: str | None = None
    for line in lines:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        if data.get("type") == "error" and isinstance(data.get("message"), str):
            last_error = data["message"].strip()
        error_obj = data.get("error")
        if isinstance(error_obj, dict) and isinstance(error_obj.get("message"), str):
            last_error = error_obj["message"].strip()
    return last_error


def _invoke_claude(*, step: str, prompt_text: str, cwd: Path, sidecar_path: Path | None = None, coder_config: dict[str, Any] | None = None, timeout_seconds_override: int | None = None) -> dict[str, Any]:
    cc = coder_config or {}
    command = ["claude"]
    # Inject model flag when provided via resolved coder config
    claude_model = str(cc.get("model_id") or cc.get("model") or "").strip()
    if claude_model:
        command.extend(["--model", claude_model])
    command.extend(["--dangerously-skip-permissions"])
    command.extend(["--print", "--output-format", "json"])
    timeout_seconds = _coder_timeout_seconds(timeout_seconds_override)
    try:
        return_code, stdout, stderr = _run_with_sidecar_poll(
            command,
            cwd=cwd,
            input_text=prompt_text,
            timeout_seconds=timeout_seconds,
            sidecar_path=sidecar_path,
            step=step,
        )
    except subprocess.TimeoutExpired as exc:
        raise CoderInvocationError(
            message=f"Claude subprocess timed out after {timeout_seconds} seconds.",
            command=command,
            return_code=124,
            stdout=_coerce_timeout_output(exc.stdout),
            stderr=_coerce_timeout_output(exc.stderr),
            raw_events=[],
        ) from exc
    payload = _parse_single_json_payload(stdout)
    parsed_result = _extract_result_from_payload(payload) if payload else (
        _extract_json_object(stdout) if stdout.strip() else {}
    )
    usage = _usage_from_payload(payload, step=step, coder="claude")
    return {
        "command": command,
        "return_code": return_code,
        "stdout": stdout,
        "stderr": stderr,
        "parsed_result": parsed_result,
        "usage": usage,
        "raw_events": [json.dumps(payload)] if payload else [],
    }


def _invoke_qwen(*, step: str, prompt_text: str, cwd: Path, coder_config: dict[str, Any] | None = None, sidecar_path: Path | None = None, timeout_seconds_override: int | None = None) -> dict[str, Any]:
    cc = coder_config or {}
    command = ["qwen", "-y"]

    # Inject model-specific CLI flags when a coder_config is provided
    qwen_model = str(cc.get("model_id") or cc.get("model") or "").strip()
    if qwen_model:
        command.extend(["-m", qwen_model])
    if cc.get("auth_type"):
        command.extend(["--auth-type", cc["auth_type"]])
    if cc.get("openai_api_key_env"):
        api_key = get_api_key(cc)
        if api_key:
            command.extend(["--openai-api-key", api_key])
    if cc.get("openai_base_url"):
        command.extend(["--openai-base-url", cc["openai_base_url"]])

    # Enable prompt mode via the long-form flag and keep the actual prompt on
    # stdin. This avoids the short `-p` form that can be mis-handled on Windows.
    command.append("--prompt")

    # Log the actual command for debugging (mask API key)
    _log_command_for_step(step, command, cc, coder_name="qwen")

    timeout_seconds = _coder_timeout_seconds(timeout_seconds_override)
    try:
        return_code, stdout, stderr = _run_with_sidecar_poll(
            command,
            cwd=cwd,
            timeout_seconds=timeout_seconds,
            sidecar_path=sidecar_path,
            step=step,
            input_text=prompt_text,
        )
    except subprocess.TimeoutExpired as exc:
        raise CoderInvocationError(
            message=f"Qwen subprocess timed out after {timeout_seconds} seconds.",
            command=command,
            return_code=124,
            stdout=_coerce_timeout_output(exc.stdout),
            stderr=_coerce_timeout_output(exc.stderr),
            raw_events=[],
        ) from exc

    # FAST FAIL: Detect empty output immediately to provide clear diagnostics
    # (skip when sidecar-triggered — stdout may be empty but sidecar has the result)
    sidecar_valid = bool(
        sidecar_path is not None and sidecar_path.exists() and _is_valid_sidecar_json(sidecar_path)
    )
    print(f"[_invoke_qwen] return_code={return_code}, stdout_len={len(stdout.strip())}, sidecar_path={sidecar_path}", flush=True)
    if not stdout.strip() and not sidecar_valid:
        print(f"[_invoke_qwen] FAIL: no stdout and sidecar not valid", flush=True)
        raise CoderInvocationError(
            message="Qwen completed but produced no output (empty stdout). "
                    "This may indicate a model API error, prompt execution failure, "
                    "or the model exited without returning structured JSON.",
            command=command,
            return_code=return_code,
            stdout="",
            stderr=stderr,
            raw_events=[],
        )
    else:
        print(f"[_invoke_qwen] PASS: has stdout or valid sidecar", flush=True)

    payload = _parse_json_payload(stdout)
    raw_events = _payload_to_raw_events(payload, stdout)
    try:
        if sidecar_valid:
            parsed_result = {}
        elif payload is not None:
            parsed_result = _extract_result_from_qwen_payload(payload)
        elif stdout.strip():
            parsed_result = _extract_json_object(stdout)
        else:
            parsed_result = {}  # sidecar-triggered: stdout empty, sidecar is authoritative
    except ValueError as exc:
        raise CoderInvocationError(
            message=f"Failed to extract structured result from qwen output: {exc}",
            command=command,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            raw_events=raw_events,
        ) from exc
    usage = _usage_from_payload(payload, step=step, coder="qwen")
    return {
        "command": command,
        "return_code": return_code,
        "stdout": stdout,
        "stderr": stderr,
        "parsed_result": parsed_result,
        "usage": usage,
        "raw_events": raw_events,
    }


def _validate_opencode_model(model_name: str) -> str:
    model_value = str(model_name or "").strip()
    if not model_value:
        raise ValueError("OpenCode requires a model in the form '{provider}/{model-id}'.")

    provider, separator, model_id = model_value.partition("/")
    if not separator or not provider.strip() or not model_id.strip():
        raise ValueError(
            f"Invalid OpenCode model {model_value!r}. Expected format '{{provider}}/{{model-id}}'."
        )
    return model_value


def _opencode_model_from_config(coder_config: dict[str, Any]) -> str:
    model_name = str(coder_config.get("model") or "").strip()
    if model_name:
        return _validate_opencode_model(model_name)

    connection_profile = coder_config.get("connection_profile") or {}
    provider_prefix = str(connection_profile.get("provider_prefix") or "").strip()
    model_id = str(coder_config.get("model_id") or "").strip()
    if not provider_prefix or not model_id:
        raise ValueError("OpenCode requires connection_profile.provider_prefix and model_id.")
    return _validate_opencode_model(f"{provider_prefix}/{model_id}")


def _invoke_opencode(*, step: str, prompt_text: str, cwd: Path, coder_config: dict[str, Any] | None = None, sidecar_path: Path | None = None, timeout_seconds_override: int | None = None) -> dict[str, Any]:
    cc = coder_config or {}
    model_name = _opencode_model_from_config(cc)
    command = ["opencode", "run", "--model", model_name]
    agent_name = str(cc.get("agent") or "").strip()
    if agent_name:
        command.extend(["--agent", agent_name])

    _log_command_for_step(step, command, cc, coder_name="opencode")

    timeout_seconds = _coder_timeout_seconds(timeout_seconds_override)
    try:
        return_code, stdout, stderr = _run_with_sidecar_poll(
            command,
            cwd=cwd,
            input_text=prompt_text,
            timeout_seconds=timeout_seconds,
            sidecar_path=sidecar_path,
            step=step,
        )
    except subprocess.TimeoutExpired as exc:
        raise CoderInvocationError(
            message=f"OpenCode subprocess timed out after {timeout_seconds} seconds.",
            command=command,
            return_code=124,
            stdout=_coerce_timeout_output(exc.stdout),
            stderr=_coerce_timeout_output(exc.stderr),
            raw_events=[],
        ) from exc

    sidecar_valid = bool(
        sidecar_path is not None and sidecar_path.exists() and _is_valid_sidecar_json(sidecar_path)
    )
    payload = _parse_json_payload(stdout)
    raw_events = _payload_to_raw_events(payload, stdout)

    if sidecar_valid:
        parsed_result = {}
    elif payload is not None:
        parsed_result = _extract_result_from_qwen_payload(payload)
    elif stdout.strip():
        try:
            parsed_result = _extract_json_object(stdout)
        except ValueError as exc:
            raise CoderInvocationError(
                message=(
                    "OpenCode completed but produced no structured JSON result. "
                    "Ensure it writes the required meta.json sidecar or emits a JSON object."
                ),
                command=command,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                raw_events=raw_events,
            ) from exc
    else:
        raise CoderInvocationError(
            message=(
                "OpenCode completed but produced no output (empty stdout). "
                "Ensure it writes the required meta.json sidecar or emits a JSON object."
            ),
            command=command,
            return_code=return_code,
            stdout="",
            stderr=stderr,
            raw_events=raw_events,
        )

    usage = _usage_from_payload(payload if isinstance(payload, dict) else None, step=step, coder="opencode")
    return {
        "command": command,
        "return_code": return_code,
        "stdout": stdout,
        "stderr": stderr,
        "parsed_result": parsed_result,
        "usage": usage,
        "raw_events": raw_events,
    }


def _parse_single_json_payload(text: str) -> dict[str, Any] | None:
    candidate = text.strip()
    if not candidate:
        return None
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _extract_result_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    direct = payload.get("result")
    if isinstance(direct, dict):
        return direct
    structured = payload.get("structured_output")
    if isinstance(structured, dict):
        return structured
    for key in ("output", "message", "response", "final", "content"):
        value = payload.get(key)
        if isinstance(value, dict) and {"status", "remark"} <= set(value):
            return value
        if isinstance(value, str):
            try:
                return _extract_json_object(value)
            except ValueError:
                continue
    try:
        return _extract_json_object(json.dumps(payload))
    except ValueError as exc:
        raise ValueError("Failed to extract model result from structured payload") from exc


def _parse_json_payload(text: str) -> Any | None:
    candidate = text.strip()
    if not candidate:
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def _payload_to_raw_events(payload: Any, stdout: str) -> list[str]:
    if isinstance(payload, list):
        return [json.dumps(item) for item in payload if isinstance(item, (dict, list))]
    if isinstance(payload, dict):
        return [json.dumps(payload)]
    return [line for line in stdout.splitlines() if line.strip()]


def _extract_result_from_qwen_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        return _extract_result_from_payload(payload)
    if not isinstance(payload, list):
        raise ValueError("Qwen payload is neither an object nor an event list")

    error_messages: list[str] = []
    for event in reversed(payload):
        if not isinstance(event, dict):
            continue
        direct = event.get("result")
        if isinstance(direct, dict):
            return direct
        if isinstance(direct, str):
            try:
                return _extract_json_object(direct)
            except ValueError:
                if _looks_like_qwen_error_text(direct):
                    error_messages.append(direct.strip())
        message = event.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list):
                text_parts: list[str] = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                        text_parts.append(item["text"])
                if text_parts:
                    joined = "\n".join(text_parts)
                    try:
                        return _extract_json_object(joined)
                    except ValueError:
                        if _looks_like_qwen_error_text(joined):
                            error_messages.append(joined.strip())

    if error_messages:
        unique_errors = list(dict.fromkeys(msg for msg in error_messages if msg))
        raise ValueError(f"Qwen returned no structured result. Last agent error: {unique_errors[0]}")
    raise ValueError("No JSON object result found in Qwen event list")


def _looks_like_qwen_error_text(text: str) -> bool:
    candidate = text.strip()
    if not candidate:
        return False
    lowered = candidate.lower()
    return (
        lowered.startswith("[api error:")
        or "connection error" in lowered
        or "fetch failed" in lowered
        or lowered.startswith("error:")
    )


def _usage_from_json_events(lines: list[str], *, step: str, coder: str) -> UsageData:
    payloads: list[dict[str, Any]] = []
    for line in lines:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            payloads.append(data)
    return _usage_from_payload({"events": payloads}, step=step, coder=coder)


def _usage_from_payload(payload: dict[str, Any] | None, *, step: str, coder: str) -> UsageData:
    metrics = _collect_usage_metrics(payload or {})
    usage_source = "cli_reported" if metrics else "not_available"
    input_tokens = _coerce_int(metrics.get("input_tokens"))
    output_tokens = _coerce_int(metrics.get("output_tokens"))
    total_tokens = _coerce_int(metrics.get("total_tokens"))
    if total_tokens is None and input_tokens is not None and output_tokens is not None:
        total_tokens = input_tokens + output_tokens
    cost = _coerce_float(metrics.get("cost"))
    return UsageData(
        step=step,
        coder_used=coder,
        usage_source=usage_source,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cost=cost,
        duration_ms=None,
        started_at="",
        finished_at="",
    )


def _collect_usage_metrics(payload: Any) -> dict[str, Any]:
    metrics: dict[str, Any] = {}

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if "usage" in node and isinstance(node["usage"], dict):
                merge_usage(metrics, node["usage"])
            merge_usage(metrics, node)
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(payload)
    return metrics


def merge_usage(target: dict[str, Any], source: dict[str, Any]) -> None:
    alias_groups = {
        "input_tokens": ("input_tokens", "inputTokens", "prompt_tokens", "promptTokens"),
        "output_tokens": ("output_tokens", "outputTokens", "completion_tokens", "completionTokens"),
        "total_tokens": ("total_tokens", "totalTokens"),
        "cost": ("cost", "total_cost", "totalCost"),
    }
    for canonical, aliases in alias_groups.items():
        if canonical in target and target[canonical] is not None:
            continue
        for alias in aliases:
            if alias in source and source[alias] is not None:
                target[canonical] = source[alias]
                break


def _coerce_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _extract_json_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    if not candidate:
        raise ValueError("Coder output is empty")
    try:
        data = json.loads(candidate)
        if not isinstance(data, dict):
            raise ValueError("Parsed JSON is not an object")
        return data
    except json.JSONDecodeError:
        pass

    fenced = candidate
    if fenced.startswith("```"):
        lines = fenced.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        fenced = "\n".join(lines).strip()
        try:
            data = json.loads(fenced)
            if not isinstance(data, dict):
                raise ValueError("Parsed JSON is not an object")
            return data
        except json.JSONDecodeError:
            pass

    match = None
    depth = 0
    start = -1
    for idx, ch in enumerate(candidate):
        if ch == "{":
            if depth == 0:
                start = idx
            depth += 1
        elif ch == "}":
            if depth:
                depth -= 1
                if depth == 0 and start >= 0:
                    match = candidate[start:idx + 1]
                    break
    if match:
        try:
            data = json.loads(match)
            if not isinstance(data, dict):
                raise ValueError("Parsed JSON is not an object")
            return data
        except json.JSONDecodeError:
            pass

    raise ValueError("Failed to parse JSON object from coder output")
