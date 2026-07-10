# Pushover Notification Integration

## Overview

Agent-runner-v2 now supports Pushover notifications for workflow completion, failure, and human intervention events. Notifications are sent automatically when workflows reach terminal states.

## Features

- **Non-blocking**: Notification failures don't affect workflow execution
- **Configurable**: Message content, priority levels, and enablement controlled via config.json
- **Credential flexibility**: Supports both .env variables and config.json credentials
- **Provider abstraction**: Easy to extend for Slack/Discord in the future
- **Emergency alerts**: FAILED notifications use Pushover emergency priority with retry/expire

## Setup

### 1. Get Pushover Credentials

1. Create a Pushover account at https://pushover.net/
2. Create an application at https://pushover.net/apps
3. Note your **User Key** (from the main page)
4. Note your **Application Token** (from the app page)

### 2. Configure Credentials

**Option A: Environment Variables (Quick Setup)**

Add to your `.env` file:
```bash
PUSHOVER_API_TOKEN=your-pushover-app-token
PUSHOVER_USER_KEY=your-pushover-user-key
```

**Option B: config.json (Persistent)**

The `config.json.example` file is automatically copied to `%USERPROFILE%\.ukbe-runner\` when you run:
```bash
ukbe-run-agent init
```

Copy it to `config.json` and fill in:
```bash
copy %USERPROFILE%\.ukbe-runner\config.json.example %USERPROFILE%\.ukbe-runner\config.json
```

Then edit the notification section:
```json
{
  "notification": {
    "enabled": true,
    "notify_api_url": "https://api.pushover.net/1/messages.json",
    "credentials": {
      "api_token": "your-pushover-app-token",
      "user_key": "your-pushover-user-key"
    }
  }
}
```

**Resolution order**: `.env` → `config.json` → error if neither present

### 3. Enable Notifications

In `%USERPROFILE%\.ukbe-runner\config.json`:
```json
{
  "notification": {
    "enabled": true  // Set to false to disable
  }
}
```

## Configuration Options

Full notification configuration in `config.json`:

```json
{
  "notification": {
    "enabled": true,
    "provider": "pushover",
    "credentials": {
      "api_token": "your-token",
      "user_key": "your-user-key"
    },
    "message_config": {
      "include_job_id": true,
      "include_workflow_name": true,
      "include_template_group": true,
      "include_duration": true,
      "include_failed_step": true,
      "include_retry_counts": false,
      "include_artifacts_summary": false,
      "custom_template": null
    },
    "priority_by_status": {
      "COMPLETED": 0,
      "FAILED": 1,
      "WAITING_FOR_HUMAN_INTERVENTION": 0
    }
  }
}
```

### Message Configuration

| Field | Default | Description |
|-------|---------|-------------|
| `include_job_id` | true | Include job identifier |
| `include_workflow_name` | true | Include workflow name |
| `include_template_group` | true | Include template group |
| `include_duration` | true | Include execution duration |
| `include_failed_step` | true | Include failed step name (FAILED only) |
| `include_retry_counts` | false | Include total retry count |
| `include_artifacts_summary` | false | Include artifact generation summary |
| `custom_template` | null | Custom message template (advanced) |

### Priority Levels

| Status | Default Priority | Behavior |
|--------|------------------|----------|
| COMPLETED | 0 (Normal) | Standard notification |
| FAILED | 1 (Emergency) | Retries every 60s for 1 hour until acknowledged |
| WAITING_FOR_HUMAN_INTERVENTION | 0 (Normal) | Standard notification |

### Custom Templates

For advanced users, you can define custom message templates:

```json
{
  "notification": {
    "message_config": {
      "custom_template": "Workflow: {workflow_name}\nJob: {job_id}\nStatus: {job_status}"
    }
  }
}
```

Template supports `{variable}` substitution from the job state dict. First line becomes title, remaining lines become message body.

## Notification Events

Notifications are sent at these transition points:

### Workflow-Level Notifications (Always On When Enabled)

#### Workflow Completion (COMPLETED)
- All steps completed successfully
- Human approval of final review step
- Auto-completion (e.g., delivery_planning_v1)

#### Workflow Failure (FAILED)
- Fatal errors (non-retryable)
- Max retry attempts exhausted
- Model rejection after loop/replan exhaustion

#### Human Intervention Required (WAITING_FOR_HUMAN_INTERVENTION)
- Planning attempt budget exceeded
- Refinement loop exhausted
- Non-progressing failures (invalid configuration)

### Step-Level Notifications (Configurable Per Step)

You can enable notifications for specific steps by adding `enable_notifications: true` to the step configuration in your workflow template.

**Important:** Step-level notifications are only sent when **both** conditions are met:
1. The step has `enable_notifications: true` configured
2. Global notifications are enabled in `%USERPROFILE%\.ukbe-runner\config.json` (`"enabled": true`)

The system automatically derives the notification status from context:
- Success → `"STEP_COMPLETED"`
- Failure → `"STEP_FAILED"`

This keeps configuration simple while maintaining full control via the global toggle.

**Example:**
```python
"step_configs": {
    "execute_critical_migration": {
        "prompt_file": "...",
        "required_inputs": ["TASK_FILE"],
        "produces": ["MIGRATION_REPORT"],
        "enable_notifications": True,  # Send notifications for this step
    },
}
```

Then control globally via config.json:
```json
{
  "notification": {
    "enabled": true  // Toggle this to enable/disable ALL step notifications
  }
}
```

**Use cases:**
- Monitor critical steps (e.g., deployment, validation)
- Get early warnings before workflow completion
- Track progress on long-running workflows

## Example Notifications

### COMPLETED
```
✅ Workflow COMPLETED

Workflow: delivery_planning_v1
Template: delivery_planning_v1
Job ID: DELIVERY-INIT-20260706-001
Duration: 15m 42s
Artifacts: 8 generated
```

### FAILED
```
❌ Workflow FAILED

Workflow: task_execution_v1
Template: task_execution_v1
Job ID: TASK-001-20260706-003
Failed at step: execute_implementation
Reason: API timeout error - connection to coder service timed out
Error code: TRANSIENT_API_ERROR
Total retries: 3
```

## Testing

Run the test suite to verify installation:

```bash
python test_notifications.py
python test_notification_integration.py
```

## Troubleshooting

### No notifications received

1. Check `"enabled": true` in config.json
2. Verify credentials are set (either .env or config.json)
3. Check logs for notification errors (non-blocking, logged but don't halt workflow)
4. Test with a simple workflow like `initiative_intake_v1`

### Emergency notifications not working

- Ensure FAILED priority is set to 1 in config.json
- Check that your Pushover account supports emergency notifications
- Verify your device allows emergency notifications (not silenced)

### Credential resolution issues

- `.env` takes precedence over `config.json`
- If using .env, ensure it's loaded before running workflows
- If using config.json, verify it's at `%USERPROFILE%\.ukbe-runner\config.json`

## Implementation Details

### Files Modified

| File | Changes |
|------|---------|
| `agent_runner_v2/notifications.py` | New module - core notification service |
| `agent_runner_v2/job_state.py` | Added send_notification calls on COMPLETED transitions (8 hooks) |
| `agent_runner_v2/workflow_router.py` | Added send_notification calls on FAILED transitions (2 hooks) |
| `agent_runner_v2/run_agent.py` | Added worker-mode notifications for RUN_COMPLETED/RUN_FAILED |
| `.env.example` | Added PUSHOVER_API_TOKEN and PUSHOVER_USER_KEY |
| `config.json.example` | New file - configuration template |

### Hook Points

- `_advance_to_next()` - Workflow natural completion
- `approve_step()` - Human-approved workflow completion (3 locations)
- `force_approve_step()` - Force-approved workflow completion (3 locations)
- `reconcile_job_state()` - Auto-completed workflows (delivery_planning_v1)
- `route_after_failure()` - Fatal/hard failures (2 locations)
- `_route_rejected()` - Model rejection after loop exhaustion
- Worker mode - Backend-driven workflow completion/failure

### Error Handling

All notification calls are wrapped in try/except blocks. Failures are logged via the runner logger but never halt workflow execution. This ensures notifications are purely additive and don't introduce new failure modes.

## Future Enhancements

Potential improvements for future iterations:

- Support for multiple notification providers (Slack, Discord, email)
- Per-workflow notification configuration
- Notification throttling/debouncing
- Rich formatting with artifacts links
- Batch notifications for multiple jobs
- Webhook support for custom integrations
