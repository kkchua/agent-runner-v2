# Daemon Runner Scripts

Convenience scripts for managing the `ukbe-run-agent daemon` on Windows and WSL.

## Quick Start

### Windows (ukbe-daemon.bat)

```batch
REM Start the worker daemon
scripts\ukbe-daemon.bat start

REM Or with a custom worker ID
scripts\ukbe-daemon.bat start my-worker-01

REM Check status (uses default worker ID: kode-worker-01)
scripts\ukbe-daemon.bat status

REM Check status of specific worker
scripts\ukbe-daemon.bat status my-worker-01

REM View logs (Ctrl+C to exit)
scripts\ukbe-daemon.bat logs

REM Stop the daemon
scripts\ukbe-daemon.bat stop

REM Restart
scripts\ukbe-daemon.bat restart
```

### WSL/Linux (ukbe-daemon-wsl.sh)

```bash
# Make executable first
chmod +x scripts/ukbe-daemon-wsl.sh

# Start the worker daemon
./scripts/ukbe-daemon-wsl.sh start

# Or with a custom worker ID
./scripts/ukbe-daemon-wsl.sh start my-worker-01

# Check status
./scripts/ukbe-daemon-wsl.sh status

# View logs (Ctrl+C to exit)
./scripts/ukbe-daemon-wsl.sh logs

# Stop the daemon
./scripts/ukbe-daemon-wsl.sh stop

# Restart
./scripts/ukbe-daemon-wsl.sh restart
```

## Worker ID

The worker ID defaults to:
1. The value from `~/.ukbe-runner/engine/config.json` → `worker_id`
2. Falls back to `"kode-worker-01"`

## File Locations

| File | Windows | WSL/Linux |
|------|---------|-----------|
| Config | `%USERPROFILE%\.ukbe-runner\engine\config.json` | `~/.ukbe-runner/engine/config.json` |
| PID files | `%USERPROFILE%\.ukbe-runner\workers\` | `~/.ukbe-runner/workers/` |
| Logs | `%USERPROFILE%\.ukbe-runner\logs\worker-{id}.log` | `~/.ukbe-runner/logs/worker-{id}.log` |

## Environment Variables

Both scripts respect these environment variables:

- `UKBE_CLI` - Override the CLI command (default: `ukbe-run-agent`)
- `WORKER_ID` - Default worker ID (if not in config.json)

## See Also

- `ukbe-runner.sh` - Full-featured bash script with backend and worker management
- These daemon scripts - focused only on worker daemon lifecycle (start/stop/status/logs)
- Full documentation: `docs/worker_supervisor_manual.md`
