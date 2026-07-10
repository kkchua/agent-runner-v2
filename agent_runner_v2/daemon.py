"""Worker daemon supervisor.

Invoked via: ukbe-run-agent daemon [worker-id]

Claims backend work, spawns one child process per claimed step, monitors child
liveness, writes local logs, and emits child-scoped heartbeats keyed by
workflow_step_run_id."""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .runtime_context import GLOBAL_RUNNER_HOME


def _get_job_step_dir(template_group: str, job_id: str, step_name: str, step_sequence_no: int) -> Path:
    """Compute the job step directory path matching manual mode's structure.
    
    Args:
        template_group: Workflow template group name (e.g., 'delivery_scaffold_v1')
        job_id: Job identifier (run_code from backend)
        step_name: Step name (e.g., 'project_analysis')
        step_sequence_no: Sequential step number for contiguous working dirs
    
    Returns:
        Path to job step directory (e.g., ~/.ukbe-runner/jobs/<template_group>/<job_id>/01_project_analysis)
    """
    from .job_state import job_dir
    return job_dir(template_group, job_id) / f"{step_sequence_no:02d}_{step_name}"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_config() -> dict:
    path = Path.home() / '.ukbe-runner' / 'engine' / 'config.json'
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            pass
    return {}


def _setting(cfg: dict, env_key: str, config_key: str, default: str) -> str:
    return os.environ.get(env_key) or str(cfg.get(config_key) or default)


def _setting_int(cfg: dict, env_key: str, config_key: str, default: int) -> int:
    return int(_setting(cfg, env_key, config_key, str(default)))


def _step_spec_source(cfg: dict, cli_value: str) -> str:
    value = (cli_value or os.environ.get('STEP_SPEC_SOURCE') or str(cfg.get('step_spec_source') or 'backend')).strip().lower()
    if value not in {'global', 'backend', 'hybrid'}:
        return 'backend'
    return value


def _resolve_engine_pythonpath(cfg: dict, log) -> str | None:
    src = os.environ.get('AGENT_RUNNER_V2_SRC', '').strip()
    if src:
        log('info', 'engine_override', message=f'engine live source override ({src})')
        return src

    version = (cfg.get('engine_version') or '').strip()
    if not version or version == 'SNAPSHOT':
        log('info', 'engine_mode', message=f'engine version={version!r} using ambient PYTHONPATH')
        return None

    global_dir = Path.home() / '.ukbe-runner' / 'engine' / 'versions' / version

    if global_dir.exists():
        log('info', 'engine_resolved', message=f'engine {version!r} resolved from global store', details={'path': str(global_dir)})
        return str(global_dir)

    log('error', 'engine_missing', message=f'engine version {version!r} not found', details={'global_path': str(global_dir)})
    return None


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(payload, ensure_ascii=True, sort_keys=True) + '\n')


def _latest_mtime(paths: list[Path], fallback: float) -> float:
    latest = fallback
    for path in paths:
        if path.exists():
            latest = max(latest, path.stat().st_mtime)
    return latest


def _failure_result(*, step_name: str, code: str, reason: str, diagnostics: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        'status': 'failed',
        'outcome': 'failed',
        'step_name': step_name,
        'coder_used': None,
        'remark': reason,
        'artifacts': {},
        'meta_json_path': None,
        'review': None,
        'usage': {},
        'failure': {
            'failure_class': 'FATAL',
            'failure_code': code,
            'failure_reason': reason,
            'failure_source': 'daemon',
        },
        'diagnostics': diagnostics or {},
    }


@dataclass
class ChildExecution:
    run_id: str
    run_code: str
    step_run_id: str
    step_name: str
    run_payload: dict[str, Any]
    step_run_payload: dict[str, Any]
    request_payload: dict[str, Any]
    request_path: Path
    result_path: Path
    combined_log_path: Path
    child_event_log_path: Path
    process: subprocess.Popen[Any]
    started_at_monotonic: float
    started_at_iso: str
    state: str = 'spawned'
    watchdog_reason: str = ''
    exit_code: int | None = None
    term_sent_at: float | None = None
    last_heartbeat_at: float = 0.0
    submission_done: bool = False


class _DaemonLogger:
    def __init__(self, path: Path, worker_id: str):
        self.path = path
        self.worker_id = worker_id

    def log(self, level: str, event: str, *, message: str = '', child: ChildExecution | None = None, details: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {
            'ts': _utcnow_iso(),
            'level': level,
            'event': event,
            'worker_id': self.worker_id,
            'message': message,
            'details': details or {},
        }
        if child is not None:
            payload.update({
                'workflow_run_id': child.run_id,
                'workflow_step_run_id': child.step_run_id,
                'run_code': child.run_code,
                'pid': child.process.pid,
                'state': child.state,
            })
        _append_jsonl(self.path, payload)
        sys.stdout.write(json.dumps(payload, ensure_ascii=True) + '\n')
        sys.stdout.flush()
        if child is not None:
            _append_jsonl(child.child_event_log_path, payload)


def _send_child_heartbeat(client, worker_id: str, child: ChildExecution, *, status: str) -> None:
    client.heartbeat(
        worker_id=worker_id,
        status=status,
        current_step_run_id=None,
        workflow_run_id=child.run_id,
        workflow_step_run_id=child.step_run_id,
        run_code=child.run_code,
        pid=child.process.pid,
        state=child.state,
        log_file=str(child.combined_log_path),
        watchdog_reason=child.watchdog_reason or None,
        exit_code=child.exit_code,
    )


def _spawn_child(*, claim: dict[str, Any], runtime_root: Path, cli_pythonpath: str | None, logger: _DaemonLogger, backend_url: str, step_spec_source: str) -> ChildExecution:
    from .run_agent import _build_worker_request_payload

    run = dict(claim['run'])
    step_run = dict(claim['step_run'])
    step_run_id = str(step_run['id'])
    child_dir = runtime_root / step_run_id
    child_dir.mkdir(parents=True, exist_ok=True)
    request_payload = _build_worker_request_payload(
        run=run,
        step_run=step_run,
        step_execution_spec=claim.get('step_execution_spec'),
        backend_url=backend_url,
        step_spec_source=step_spec_source,
    )
    request_path = child_dir / 'request.json'
    result_path = child_dir / 'result.json'
    combined_log_path = child_dir / 'child.log'
    child_event_log_path = child_dir / 'child-events.jsonl'
    request_path.write_text(json.dumps(request_payload, indent=2), encoding='utf-8')

    env = os.environ.copy()
    if cli_pythonpath:
        env['PYTHONPATH'] = cli_pythonpath + os.pathsep + env.get('PYTHONPATH', '')

    log_handle = combined_log_path.open('ab')
    
    # Set working directory to project_root so subprocess can find .env file
    project_root = request_payload.get("project_root") or request_payload.get("workspace_root")
    subprocess_cwd = Path(project_root).resolve() if project_root else Path.cwd()
    
    logger.log('info', 'subprocess_cwd', message=f'Setting subprocess cwd to {subprocess_cwd}', details={'project_root': project_root, 'subprocess_cwd': str(subprocess_cwd)})
    
    proc = subprocess.Popen(
        [sys.executable, '-m', 'agent_runner_v2.run_agent', 'execute-step', '--request-file', str(request_path), '--result-file', str(result_path)],
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        env=env,
        cwd=str(subprocess_cwd),
    )
    started_monotonic = time.monotonic()
    child = ChildExecution(
        run_id=str(run['id']),
        run_code=str(run.get('run_code') or ''),
        step_run_id=step_run_id,
        step_name=str(step_run.get('step_name') or ''),
        run_payload=run,
        step_run_payload=step_run,
        request_payload=request_payload,
        request_path=request_path,
        result_path=result_path,
        combined_log_path=combined_log_path,
        child_event_log_path=child_event_log_path,
        process=proc,
        started_at_monotonic=started_monotonic,
        started_at_iso=_utcnow_iso(),
        state='running',
        last_heartbeat_at=0.0,
    )
    logger.log('info', 'child_spawned', message='spawned execute-step child', child=child, details={'request_path': str(request_path), 'result_path': str(result_path), 'log_file': str(combined_log_path), 'step_spec_source': step_spec_source, 'coder_override': request_payload.get('coder_override')})
    return child


def _child_result(child: ChildExecution) -> dict[str, Any]:
    diagnostics = {'log_file': str(child.combined_log_path), 'request_path': str(child.request_path), 'result_path': str(child.result_path)}
    if child.result_path.exists():
        payload = json.loads(child.result_path.read_text(encoding='utf-8'))
        payload.setdefault('diagnostics', {}).update(diagnostics)
        if child.exit_code is not None:
            payload['diagnostics']['subprocess_return_code'] = child.exit_code
        return payload
    reason = f'child process exited without result file for step {child.step_name}'
    return _failure_result(step_name=child.step_name, code='CHILD_RESULT_MISSING', reason=reason, diagnostics=diagnostics | {'subprocess_return_code': child.exit_code})


def _terminate_child(child: ChildExecution, logger: _DaemonLogger, sigkill: bool = False) -> None:
    try:
        if sigkill:
            child.process.kill()
            if os.name == 'nt':
                logger.log('error', 'child_killed', message='force terminated child process', child=child)
            else:
                logger.log('error', 'child_killed', message='sent SIGKILL to child', child=child)
        else:
            child.process.terminate()
            if os.name == 'nt':
                logger.log('error', 'child_terminated', message='terminated child process', child=child)
            else:
                logger.log('error', 'child_terminated', message='sent SIGTERM to child', child=child)
    except ProcessLookupError:
        return


def _run_supervisor(*, worker_id: str, worker_label: str, backend_url: str, poll_seconds: int, max_parallel: int, stalled_seconds: int, step_timeout_seconds: int, kill_grace_seconds: int, runtime_dir: Path, log_file: Path, cli_pythonpath: str | None, step_spec_source: str, once: bool = False) -> int:
    from .backend_client import BackendClient
    from .run_agent import _finalize_worker_completion, _submit_worker_result

    logger = _DaemonLogger(log_file, worker_id)
    client = BackendClient(backend_url)
    client.register_worker(worker_id=worker_id, host_name=None, capabilities={'mode': ['execute-step-daemon'], 'max_parallel': max_parallel}, worker_label=worker_label)
    logger.log('info', 'daemon_started', message='worker daemon started', details={'backend_url': backend_url, 'worker_label': worker_label, 'max_parallel': max_parallel, 'runtime_dir': str(runtime_dir), 'step_spec_source': step_spec_source})

    children: dict[str, ChildExecution] = {}
    running = True

    def _handle_signal(_sig, _frame):
        nonlocal running
        running = False
        logger.log('info', 'daemon_shutdown_signal', message='received shutdown signal')

    signal.signal(signal.SIGINT, _handle_signal)
    if os.name != 'nt':
        signal.signal(signal.SIGTERM, _handle_signal)

    while running or children:
        now = time.monotonic()
        active = 0
        for step_run_id in list(children):
            child = children[step_run_id]
            proc_rc = child.process.poll()
            last_activity = _latest_mtime([child.combined_log_path, child.result_path], child.started_at_monotonic)
            if proc_rc is None:
                active += 1
                if child.term_sent_at is not None and now - child.term_sent_at >= kill_grace_seconds:
                    child.state = 'killed'
                    child.watchdog_reason = 'kill_grace_exceeded'
                    _terminate_child(child, logger, sigkill=True)
                elif child.term_sent_at is None and now - child.started_at_monotonic >= step_timeout_seconds:
                    child.state = 'timed_out'
                    child.watchdog_reason = 'step_timeout_exceeded'
                    child.term_sent_at = now
                    logger.log('error', 'child_timeout', message='child exceeded timeout', child=child, details={'timeout_seconds': step_timeout_seconds})
                    _terminate_child(child, logger, sigkill=False)
                elif child.term_sent_at is None and now - last_activity >= stalled_seconds and child.state != 'stalled':
                    child.state = 'stalled'
                    child.watchdog_reason = 'log_inactive'
                    logger.log('warning', 'child_stalled', message='child appears stalled', child=child, details={'stalled_seconds': stalled_seconds})
                elif child.term_sent_at is None and child.state != 'running':
                    child.state = 'running'
                    child.watchdog_reason = ''
                    logger.log('info', 'child_running', message='child is running', child=child)
                if now - child.last_heartbeat_at >= max(5, poll_seconds):
                    _send_child_heartbeat(client, worker_id, child, status='busy')
                    child.last_heartbeat_at = now
                continue

            child.exit_code = proc_rc
            if not child.submission_done:
                result = _child_result(child)
                try:
                    completion = _submit_worker_result(
                        client=client,
                        run=child.run_payload,
                        step_run=child.step_run_payload,
                        result=result,
                    )
                    child.submission_done = True
                    child.state = 'completed' if result.get('status') == 'completed' else 'failed'
                    logger.log('info', 'result_submitted', message='submitted child result', child=child, details={'status': result.get('status'), 'outcome': result.get('outcome'), 'exit_code': proc_rc})
                    try:
                        completion_info = _finalize_worker_completion(
                            client=client,
                            run=child.run_payload,
                            step_run=child.step_run_payload,
                            completion=completion,
                        )
                        logger.log(
                            'info',
                            'completion_finalized',
                            message='finalized backend completion state',
                            child=child,
                            details={
                                'run_status': (completion_info.get('run') or {}).get('status'),
                                'last_event': completion_info.get('last_event'),
                                'next_step_name': ((completion_info.get('next_step_run') or {}).get('step_name')),
                            },
                        )
                    except Exception as finalize_exc:
                        logger.log('warning', 'completion_finalize_failed', message='failed to finalize backend completion state', child=child, details={'error': str(finalize_exc)})
                    
                    # After successful submission, also write result.json to job step directory (matching manual mode)
                    try:
                        template_group = child.request_payload.get("template_group", "")
                        job_id = child.run_code  # run_code is the job_id
                        step_sequence_no = int(child.request_payload.get("step_execution_spec", {}).get("step_sequence_no") or 
                                              child.request_payload.get("step_execution_spec", {}).get("step_order") or 1)
                        
                        step_dir = _get_job_step_dir(
                            template_group=template_group,
                            job_id=job_id,
                            step_name=child.step_name,
                            step_sequence_no=step_sequence_no,
                        )
                        step_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Write result.json with same structure as manual mode
                        result_json_path = step_dir / "result.json"
                        result_json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                        
                        logger.log('info', 'result_json_written', message='wrote result.json to job step directory', child=child, details={'path': str(result_json_path)})
                    except Exception as write_exc:
                        logger.log('warning', 'result_json_write_failed', message='failed to write result.json to job step directory', child=child, details={'error': str(write_exc)})
                except Exception as exc:
                    child.state = 'submit_failed'
                    child.watchdog_reason = str(exc)
                    logger.log('error', 'result_submit_failed', message='failed to submit child result', child=child, details={'error': str(exc)})
                    if not running:
                        logger.log('error', 'result_submit_abandoned', message='shutdown requested; abandoning unsubmitted child result', child=child, details={'error': str(exc)})
                        del children[step_run_id]
                        continue
                    if now - child.last_heartbeat_at >= max(5, poll_seconds):
                        _send_child_heartbeat(client, worker_id, child, status='busy')
                        child.last_heartbeat_at = now
                    active += 1
                    continue
                _send_child_heartbeat(client, worker_id, child, status='busy')
            logger.log('info', 'child_exited', message='child finished', child=child, details={'exit_code': proc_rc})
            del children[step_run_id]

        if running:
            while len(children) < max_parallel:
                client.heartbeat(worker_id=worker_id, status='polling', current_step_run_id=None)
                logger.log('info', 'poll_started', message='polling for work', details={'active_children': len(children)})
                claim = client.claim_step(worker_id=worker_id)
                if not claim.get('step_run') or not claim.get('run'):
                    logger.log('info', 'poll_no_work', message='no work available', details={'active_children': len(children)})
                    break
                child = _spawn_child(claim=claim, runtime_root=runtime_dir, cli_pythonpath=cli_pythonpath, logger=logger, backend_url=backend_url, step_spec_source=step_spec_source)
                children[child.step_run_id] = child
                _send_child_heartbeat(client, worker_id, child, status='busy')
                child.last_heartbeat_at = time.monotonic()
                active = len(children)
                if once:
                    running = False
                    break

        if not children:
            client.heartbeat(worker_id=worker_id, status='idle', current_step_run_id=None)
            if once and not running:
                break
        time.sleep(max(poll_seconds, 1))

    if children:
        for child in children.values():
            _terminate_child(child, logger, sigkill=False)
    client.heartbeat(worker_id=worker_id, status='idle', current_step_run_id=None)
    logger.log('info', 'daemon_shutdown', message='worker daemon stopped')
    return 0


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog='ukbe-run-agent daemon', description='Worker daemon supervisor.')
    p.add_argument('worker_id', nargs='?', default='', help='Worker ID (overrides config and WORKER_ID env var).')
    p.add_argument('--worker-label', default='', help='Queue label override (live or dev).')
    p.add_argument('--backend-url', default='', help='Backend URL override.')
    p.add_argument('--poll-seconds', type=int, default=0, help='Poll interval override.')
    p.add_argument('--log-file', default='', help='Daemon log file path override.')
    p.add_argument('--max-parallel', type=int, default=0, help='Maximum concurrent child executions.')
    p.add_argument('--runtime-dir', default='', help='Runtime directory for child request/result files.')
    p.add_argument('--stalled-seconds', type=int, default=0, help='Seconds without child log/result activity before marking stalled.')
    p.add_argument('--step-timeout-seconds', type=int, default=0, help='Hard timeout for a child execution.')
    p.add_argument('--kill-grace-seconds', type=int, default=0, help='Grace period between SIGTERM and SIGKILL.')
    p.add_argument('--step-spec-source', default='', help='Workflow step spec source: global, backend, or hybrid.')
    args = p.parse_args(argv)

    cfg = _load_config()
    worker_id = args.worker_id or _setting(cfg, 'WORKER_ID', 'worker_id', 'kode-worker-01')
    worker_label = args.worker_label or _setting(cfg, 'WORKER_LABEL', 'worker_label', 'live')
    backend_url = args.backend_url or _setting(cfg, 'AGENT_RUNNER_BACKEND_URL', 'backend_url', 'http://127.0.0.1:8100')
    poll_seconds = args.poll_seconds or _setting_int(cfg, 'WORKER_POLL_SEC', 'poll_seconds', 5)
    max_parallel = args.max_parallel or _setting_int(cfg, 'WORKER_MAX_PARALLEL', 'max_parallel', 1)
    stalled_seconds = args.stalled_seconds or _setting_int(cfg, 'WORKER_STALLED_SEC', 'stalled_seconds', 300)
    step_timeout_seconds = args.step_timeout_seconds or _setting_int(cfg, 'WORKER_STEP_TIMEOUT_SEC', 'step_timeout_seconds', 3600)
    kill_grace_seconds = args.kill_grace_seconds or _setting_int(cfg, 'WORKER_KILL_GRACE_SEC', 'kill_grace_seconds', 30)
    step_spec_source = _step_spec_source(cfg, args.step_spec_source)
    default_log_file = str(GLOBAL_RUNNER_HOME / 'logs' / 'worker-daemon.jsonl')
    default_runtime_dir = str(GLOBAL_RUNNER_HOME / 'runtime' / 'worker')
    log_file = Path(args.log_file or _setting(cfg, 'WORKER_LOG_FILE', 'log_file', default_log_file)).resolve()
    runtime_dir = Path(args.runtime_dir or _setting(cfg, 'WORKER_RUNTIME_DIR', 'runtime_dir', default_runtime_dir)).resolve()

    bootstrap_logger = _DaemonLogger(log_file, worker_id)
    cli_pythonpath = _resolve_engine_pythonpath(cfg, bootstrap_logger.log)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    return _run_supervisor(
        worker_id=worker_id,
        worker_label=worker_label,
        backend_url=backend_url,
        poll_seconds=poll_seconds,
        max_parallel=max_parallel,
        stalled_seconds=stalled_seconds,
        step_timeout_seconds=step_timeout_seconds,
        kill_grace_seconds=kill_grace_seconds,
        runtime_dir=runtime_dir,
        log_file=log_file,
        cli_pythonpath=cli_pythonpath,
        step_spec_source=step_spec_source,
    )
