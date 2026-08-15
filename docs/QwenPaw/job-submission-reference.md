# Job Submission Reference — Agent Runner V2

> **Method of record: Backend API (same call as operator-console-v2).**
> CLI submission (`run_agent --mode manual`, `ukbe-run-agent submit`) and
> pre-built `.bat` submit scripts are **no longer used**. All job submissions
> go through the backend REST API, exactly like the operator-console-v2 frontend.

## Service Status

| Service | How to Check | Expected |
|---------|-------------|----------|
| Backend | `netstat -ano | findstr "8200"` | LISTENING on port 8200 |
| Daemon | `tasklist | findstr /i "daemon"` | python.exe running |
| Database | Docker running | PostgreSQL container active |

**Always ask user to confirm backend/daemon are running before submitting.**

## Submit a Job — Backend API (preferred, same as operator-console-v2)

The operator-console-v2 frontend submits via `POST /api/runs` with a
`SubmitRunRequest` body. Use the exact same call.

### Endpoint

```
POST http://127.0.0.1:8200/api/runs
Content-Type: application/json
Authorization: Bearer <token or API key>
```

> Use `127.0.0.1` not `localhost` (IPv6 resolution issue).

### Request Body (SubmitRunRequest)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `workflow_name` | string | ✅ | e.g. `sdlc_50_implementation_v1` |
| `worker_id` | string | ❌ | **Default: `chua-worker-01`** |
| `project_root` | string | ❌ | **For workflow development: the `agent-runner-v2` repo root** — `D:\MyProjectSpace\01_Workflows\agent-runner-v2` |
| `workspace_path` | string | ❌ | Alternative to project_root |
| `input_payload` | dict | ❌ | Artifact seeds — **filename only**, backend resolves against project_root. Format: `{"ARTIFACT_KEY": "file.md"}` |
| `start_step` | string | ❌ | Resume from a specific step |
| `implementation_name` | string | ❌ | BCS — selected implementation |
| `prompt_selections` | dict | ❌ | BCS — per-slot prompt selections |

### Default Payload for Workflow Development

```json
{
  "workflow_name": "sdlc_50_implementation_v1",
  "worker_id": "chua-worker-01",
  "project_root": "D:\\MyProjectSpace\\01_Workflows\\agent-runner-v2",
  "input_payload": {
    "TASK_FILE": "<TASK_FILE>.md"
  }
}
```

> `<TASK_FILE>.md` = the actual TASK doc filename, e.g. `TASK-20260814-001-01_gen-media-content-scaffolding.md`

### Example (curl)

```bash
curl -X POST http://127.0.0.1:8200/api/runs ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer <token>" ^
  -d "{\"workflow_name\":\"sdlc_50_implementation_v1\",\"worker_id\":\"chua-worker-01\",\"project_root\":\"D:\\MyProjectSpace\\01_Workflows\\agent-runner-v2\",\"input_payload\":{\"TASK_FILE\":\"<TASK_FILE>.md\"}}"
```

### Example (PowerShell)

```powershell
$body = @{
  workflow_name = "sdlc_50_implementation_v1"
  worker_id     = "chua-worker-01"
  project_root  = "D:\MyProjectSpace\01_Workflows\agent-runner-v2"
  input_payload = @{ TASK_FILE = "<TASK_FILE>.md" }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://127.0.0.1:8200/api/runs" `
  -Method Post `
  -ContentType "application/json" `
  -Headers @{ Authorization = "Bearer <token>" } `
  -Body $body
```

### BCS Example (with implementation + prompt selections)

```json
{
  "workflow_name": "agnes_media_gen_v1",
  "worker_id": "chua-worker-01",
  "project_root": "D:\\MyProjectSpace\\01_Workflows\\agnes-AI",
  "input_payload": {
    "INPUT_JSON": "media/xxx_prompts_001.json"
  },
  "implementation_name": "agnes_full",
  "prompt_selections": {
    "extract_desc": "standard",
    "generate_prompts": "standard"
  }
}
```

## Critical Rules

1. **`worker_id`** defaults to **`chua-worker-01`**
2. **`project_root`** for workflow development is always the **`agent-runner-v2` repo root** (`D:\MyProjectSpace\01_Workflows\agent-runner-v2`)
3. **Pass only the filename** in `input_payload` — format `{"ARTIFACT_KEY": "file.md"}` (e.g., `{"TASK_FILE": "<TASK_FILE>.md"}`), not the full path — the backend resolves it relative to `project_root`
4. **Job IDs are auto-assigned by the backend** — never set them manually
5. Use `http://127.0.0.1:8200`, not `localhost:8200` (IPv6 issue)

## Telegram Channel Submission

Send a message to the Telegram bot in the group chat with:
```
/submit <workflow_name> --input-payload {"ARTIFACT_KEY": "relative/path"}
```
(Exact syntax depends on the Telegram bot command handler — verify with user.
Backend API remains the method of record.)

## Job Status Check

### API (same as operator-console-v2)

```
GET http://127.0.0.1:8200/api/runs/{run_id}
```

List runs with optional filters:

```
GET http://127.0.0.1:8200/api/runs?status=active
GET http://127.0.0.1:8200/api/runs?workflow_name=sdlc_50_implementation_v1
GET http://127.0.0.1:8200/api/runs?limit=100&offset=0
```

### Job JSON Location

```
C:\Users\kengk\.ukbe-runner\jobs\YYYYMMDD\<workflow_name>\<job_id>\job.json
```

### Key Job Fields

| Field | Meaning |
|-------|---------|
| `job_status` | Current state (PENDING, RUNNING, COMPLETED, FAILED, WAITING_FOR_HUMAN_INTERVENTION) |
| `current_step` | Step being executed |
| `last_failure_reason` | Error message if failed |
| `artifacts.TASK_FILE` | Seeded artifact path |

## Common Workflows and Required Artifacts

| Workflow | Required Input Artifacts | Output Artifacts |
|----------|-------------------------|------------------|
| `sdlc_50_implementation_v1` | `TASK_FILE` | `IMPL_FILE` |
| `sdlc_60_execution_v1` | `IMPL_FILE` | `EXEC_FILE` |
| `sdlc_10_requirement_v1` | (none) | `REQUIREMENT_DOC` |
| `sdlc_20_planning_v1` | `REQUIREMENT_DOC` | `PLAN_FILE` |
| `sdlc_30_backlog_v1` | `PLAN_FILE` | `BACKLOG_FILE` |
| `sdlc_40_task_v1` | `BACKLOG_FILE` | `TASK_FILE` |
| `sdlc_70_validation_v1` | `IMPL_FILE` or `EXEC_FILE` | `VAL_FILE` |
| `sdlc_80_review_v1` | `IMPL_FILE` or `EXEC_FILE` | `REV_FILE` |

## Troubleshooting

### "Missing required input artifact(s): TASK_FILE"
- The `input_payload` was not passed or the filename is wrong
- Verify the file exists under `project_root`
- Pass **filename only** (no full path, no `docs/...` prefix for seed artifacts unless the workflow expects a relative path)

### Job stuck in WAITING_FOR_HUMAN_INTERVENTION
- Check `last_failure_reason` in job.json
- May need to approve/reject or reset a step via the console UI or the action/reset endpoints

### Daemon not picking up jobs
- Check daemon is running: `tasklist | findstr /i "daemon"`
- Restart daemon if needed
- Check backend is accessible on port 8200
