# Windows Compatibility for Worker Daemon

## Summary of Changes

The worker daemon (`agent_runner_v2/daemon.py`) has been updated to support running on Windows environments.

## Issues Fixed

### 1. Signal Handling (Lines 268-270)

**Problem**: The daemon registered handlers for both `SIGINT` and `SIGTERM` signals. However, Windows doesn't support Unix-style signals in the same way, and attempting to register a `SIGTERM` handler on Windows can cause issues.

**Solution**: Only register the `SIGTERM` handler on non-Windows systems:

```python
signal.signal(signal.SIGINT, _handle_signal)
if os.name != 'nt':
    signal.signal(signal.SIGTERM, _handle_signal)
```

**Impact**: 
- On Unix/Linux/macOS: Both SIGINT (Ctrl+C) and SIGTERM signals are handled for graceful shutdown
- On Windows: Only SIGINT (Ctrl+C) is handled, which is the standard way to interrupt processes

### 2. Process Termination Logging (Lines 233-247)

**Problem**: The log messages referenced Unix-specific signal names (SIGTERM/SIGKILL) which don't accurately describe Windows behavior. On Windows, both `terminate()` and `kill()` call `TerminateProcess()` which is immediate termination.

**Solution**: Use platform-appropriate log messages:

```python
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
```

**Impact**:
- Log messages are now accurate for each platform
- Easier to debug issues on Windows without confusing Unix signal terminology

## Platform Behavior

### Unix/Linux/macOS
- **SIGINT** (Ctrl+C): Graceful shutdown initiated
- **SIGTERM**: Graceful shutdown initiated
- **Child terminate()**: Sends SIGTERM to child process (allows cleanup)
- **Child kill()**: Sends SIGKILL to child process (immediate termination)

### Windows
- **Ctrl+C**: Graceful shutdown initiated
- **SIGTERM**: Not applicable (not registered)
- **Child terminate()**: Immediate termination via TerminateProcess()
- **Child kill()**: Immediate termination via TerminateProcess()

**Note**: On Windows, there is no graceful shutdown mechanism for child processes. Both `terminate()` and `kill()` result in immediate termination. This is a Windows OS limitation.

## Testing

The existing test suite passes with these changes:
```bash
python -m pytest tests/test_daemon.py -v
```

## Running the Daemon on Windows

The daemon can now be started on Windows using the same command:

```bash
ukbe-run-agent daemon kode-worker-01 --backend-url http://127.0.0.1:8100
```

Or with Python directly:

```bash
python -m agent_runner_v2.run_agent daemon kode-worker-01 --backend-url http://127.0.0.1:8100
```

Press **Ctrl+C** to gracefully shut down the daemon on all platforms.

## Backward Compatibility

These changes are fully backward compatible:
- Unix/Linux/macOS behavior remains unchanged
- No API changes
- No configuration changes required
- Existing deployments continue to work as before
