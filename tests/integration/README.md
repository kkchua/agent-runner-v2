# Integration Tests

Integration tests verify components working together with real files, external systems, and subprocesses.

## Running Integration Tests

```bash
# Run all integration tests
python -m pytest tests/integration/ -v

# Run specific integration test
python -m pytest tests/integration/test_daemon.py -xvs

# Skip slow tests
python -m pytest tests/integration/ -v -m "not slow"
```

## Test Files

- `test_architecture_site.py` - Site rendering with actual files
- `test_daemon.py` - Daemon subprocess spawning
- `test_notifications.py` - Notification system (may call APIs)
- `test_pushover.py` - Pushover API directly
- `test_notification_integration.py` - Import wiring
- `test_notification_e2e.py` - End-to-end notification tests
- `test_ukbe_runner_wrapper.py` - Shell wrapper (POSIX only)

## Notes

Some integration tests may require:
- Network access (for API calls)
- Specific environment variables (PUSHOVER_API_TOKEN, etc.)
- POSIX shell (for ukbe_runner_wrapper tests)
