"""V2 outcome queue — file-based handoff between CLI and daemon.

The CLI writes step outcome files to the queue after execution.
The daemon polls the queue and reports outcomes to the backend.

Directory structure::

    ~/.ukbe-runner/queue/{YYYYMMDD}/{workflow_name}/{job_id}/
        {step_run_id}.json      # pending outcome
        archive/                # successfully reported to backend
        failed/                 # failed after max retries

Queue file format::

    {
        "step_run_id": "uuid",
        "run_id": "uuid",
        "run_code": "AMGEN-20260804-001",
        "workflow_name": "...",
        "step_name": "...",
        "job_dir": "/full/path/to/job/folder",
        "outcome": "approved" | "rejected" | "failed",
        "failure_class": null | "AUTO_RETRYABLE" | "HUMAN_RETRY_REQUIRED" | "FATAL",
        "artifacts": {...},
        "review": {...},
        "error_message": null | "...",
        "usage_summary": {...},
        "exit_code": 0,
        "timestamp": "ISO-8601"
    }
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Directory helpers
# ---------------------------------------------------------------------------

def get_queue_dir(
    queue_root: Path,
    workflow_name: str,
    job_id: str,
    *,
    date: str | None = None,
) -> Path:
    """Return the queue directory for a specific job.

    Args:
        queue_root: Queue root path (e.g. ~/.ukbe-runner/queue).
        workflow_name: Workflow name.
        job_id: Job identifier (e.g. AMGEN-20260804-001).
        date: Date prefix (YYYYMMDD). Defaults to today.

    Returns:
        Path to the queue directory for this job.
    """
    date_str = date or dt.datetime.now().strftime("%Y%m%d")
    return queue_root / date_str / workflow_name / job_id


def ensure_queue_dir(queue_dir: Path) -> None:
    """Create the queue directory and its archive/failed subfolders."""
    queue_dir.mkdir(parents=True, exist_ok=True)
    (queue_dir / "archive").mkdir(exist_ok=True)
    (queue_dir / "failed").mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def write_outcome(
    queue_dir: Path,
    step_run_id: str,
    outcome_data: dict[str, Any],
) -> Path:
    """Atomically write an outcome file to the queue directory.

    Writes to a temp file first, then renames to the final path.
    Creates the queue directory and subfolders if they don't exist.

    Args:
        queue_dir: Job's queue directory.
        step_run_id: Step run UUID (used as filename).
        outcome_data: Outcome payload dict.

    Returns:
        Path to the written file.
    """
    ensure_queue_dir(queue_dir)
    final_path = queue_dir / f"{step_run_id}.json"

    # Ensure timestamp is present
    if "timestamp" not in outcome_data:
        outcome_data["timestamp"] = dt.datetime.now(dt.timezone.utc).isoformat()

    # Atomic write: temp file → rename
    fd, tmp_path = tempfile.mkstemp(
        dir=queue_dir, prefix=".tmp_", suffix=".json",
    )
    try:
        with open(fd, "w", encoding="utf-8") as fh:
            json.dump(outcome_data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        Path(tmp_path).replace(final_path)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise

    logger.debug("queue outcome written: %s", final_path)
    return final_path


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def read_outcome(file_path: Path) -> dict[str, Any] | None:
    """Read and parse an outcome file from the queue.

    Returns None if the file doesn't exist or can't be parsed.

    Args:
        file_path: Path to the outcome JSON file.

    Returns:
        Parsed outcome dict, or None on failure.
    """
    if not file_path.exists():
        return None
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            logger.warning("queue file is not a JSON object: %s", file_path)
            return None
        # Validate required fields
        if "step_run_id" not in data or "outcome" not in data:
            logger.warning("queue file missing required fields: %s", file_path)
            return None
        return data
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("failed to read queue file %s: %s", file_path, exc)
        return None


# ---------------------------------------------------------------------------
# Archive / Fail
# ---------------------------------------------------------------------------

def archive_outcome(file_path: Path) -> bool:
    """Move a successfully processed outcome file to the archive subfolder.

    Args:
        file_path: Path to the outcome file.

    Returns:
        True if moved successfully, False otherwise.
    """
    archive_dir = file_path.parent / "archive"
    archive_dir.mkdir(exist_ok=True)
    dest = archive_dir / file_path.name
    try:
        file_path.replace(dest)
        logger.debug("queue outcome archived: %s → %s", file_path, dest)
        return True
    except OSError as exc:
        logger.warning("failed to archive queue file %s: %s", file_path, exc)
        return False


def fail_outcome(file_path: Path) -> bool:
    """Move a failed outcome file to the failed subfolder.

    Args:
        file_path: Path to the outcome file.

    Returns:
        True if moved successfully, False otherwise.
    """
    failed_dir = file_path.parent / "failed"
    failed_dir.mkdir(exist_ok=True)
    dest = failed_dir / file_path.name
    try:
        file_path.replace(dest)
        logger.debug("queue outcome moved to failed: %s → %s", file_path, dest)
        return True
    except OSError as exc:
        logger.warning("failed to move queue file to failed %s: %s", file_path, exc)
        return False


# ---------------------------------------------------------------------------
# List / Scan
# ---------------------------------------------------------------------------

def list_pending_outcomes(queue_root: Path) -> list[Path]:
    """Scan the queue root for all pending outcome files.

    Searches across all date/workflow/job folders for ``*.json`` files
    that are not in archive/ or failed/ subfolders and don't start
    with a dot (temp files).

    Files are returned sorted by modification time (oldest first).

    Args:
        queue_root: Queue root path (e.g. ~/.ukbe-runner/queue).

    Returns:
        List of paths to pending outcome files.
    """
    if not queue_root.exists():
        return []

    pending: list[Path] = []
    for json_file in queue_root.rglob("*.json"):
        # Skip temp files
        if json_file.name.startswith("."):
            continue
        # Skip archive and failed subfolders
        parts = json_file.relative_to(queue_root).parts
        if "archive" in parts or "failed" in parts:
            continue
        pending.append(json_file)

    # Sort by modification time (oldest first)
    pending.sort(key=lambda p: p.stat().st_mtime)
    return pending
