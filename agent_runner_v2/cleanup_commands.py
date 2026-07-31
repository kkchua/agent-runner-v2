"""Cleanup command for agent_runner_v2 - remove old job history and runtime files.

This module provides the cleanup functionality for the agent runner,
removing job folders and runtime files older than a configurable number of days.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .config_loader import load_runner_config
from .runtime_context import GLOBAL_RUNNER_HOME, get_jobs_root


@dataclass
class CleanupSummary:
    """Summary of cleanup operation for a single target."""

    target_name: str
    deleted_count: int = 0
    deleted_paths: list[str] = field(default_factory=list)
    kept_count: int = 0
    kept_paths: list[str] = field(default_factory=list)
    bytes_freed: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert summary to dictionary for JSON serialization."""
        return {
            "target_name": self.target_name,
            "deleted_count": self.deleted_count,
            "kept_count": self.kept_count,
            "bytes_freed": self.bytes_freed,
            "deleted_paths": self.deleted_paths,
            "errors": self.errors,
        }


def _get_directory_size(path: Path) -> int:
    """Calculate total size of a directory in bytes."""
    total = 0
    try:
        if path.is_file():
            return path.stat().st_size
        for item in path.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
    except (OSError, PermissionError):
        pass
    return total


def _get_targets_to_cleanup(
    directory: Path, cutoff_time: float
) -> tuple[list[Path], list[Path]]:
    """Scan directory and return paths to delete (older than cutoff) and keep.

    Args:
        directory: Root directory to scan
        cutoff_time: Unix timestamp - files older than this are candidates for deletion

    Returns:
        Tuple of (paths_to_delete, paths_to_keep)
    """
    to_delete: list[Path] = []
    to_keep: list[Path] = []

    if not directory.exists():
        return to_delete, to_keep

    for item in directory.iterdir():
        try:
            mtime = item.stat().st_mtime
            if mtime < cutoff_time:
                to_delete.append(item)
            else:
                to_keep.append(item)
        except (OSError, PermissionError):
            # Skip items we can't stat
            continue

    # Sort by mtime (oldest first for deletion)
    to_delete.sort(key=lambda p: p.stat().st_mtime)
    to_keep.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return to_delete, to_keep


def cleanup_jobs(
    runner_home: Path, keep_days: int, dry_run: bool
) -> CleanupSummary:
    """Clean up job folders older than keep_days.

    Args:
        runner_home: Global runner home path
        keep_days: Number of days to keep
        dry_run: If True, only report what would be deleted

    Returns:
        CleanupSummary with results
    """
    summary = CleanupSummary(target_name="jobs")
    jobs_root = runner_home / "jobs"

    if not jobs_root.exists():
        return summary

    cutoff_time = time.time() - (keep_days * 86400)

    # Iterate through workflow subdirectories
    for workflow_dir in jobs_root.iterdir():
        if not workflow_dir.is_dir():
            continue

        to_delete, to_keep = _get_targets_to_cleanup(workflow_dir, cutoff_time)

        for item in to_keep:
            summary.kept_count += 1
            summary.kept_paths.append(str(item.relative_to(runner_home)))

        for item in to_delete:
            rel_path = str(item.relative_to(runner_home))
            summary.deleted_count += 1
            summary.deleted_paths.append(rel_path)

            if not dry_run:
                try:
                    size = _get_directory_size(item)
                    if item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                    else:
                        item.unlink(missing_ok=True)
                    summary.bytes_freed += size
                except (OSError, PermissionError) as e:
                    summary.errors.append(f"{rel_path}: {e}")

    return summary


def cleanup_runtime(
    runner_home: Path, keep_days: int, dry_run: bool
) -> CleanupSummary:
    """Clean up runtime worker files/folders older than keep_days.

    Args:
        runner_home: Global runner home path
        keep_days: Number of days to keep
        dry_run: If True, only report what would be deleted

    Returns:
        CleanupSummary with results
    """
    summary = CleanupSummary(target_name="runtime")
    runtime_dir = runner_home / "runtime" / "worker"

    if not runtime_dir.exists():
        return summary

    cutoff_time = time.time() - (keep_days * 86400)
    to_delete, to_keep = _get_targets_to_cleanup(runtime_dir, cutoff_time)

    for item in to_keep:
        summary.kept_count += 1
        summary.kept_paths.append(str(item.relative_to(runner_home)))

    for item in to_delete:
        rel_path = str(item.relative_to(runner_home))
        summary.deleted_count += 1
        summary.deleted_paths.append(rel_path)

        if not dry_run:
            try:
                size = _get_directory_size(item)
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)
                summary.bytes_freed += size
            except (OSError, PermissionError) as e:
                summary.errors.append(f"{rel_path}: {e}")

    return summary


def _format_bytes(size: int) -> str:
    """Format byte size to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for cleanup command."""
    parser = argparse.ArgumentParser(
        description="Cleanup old job history and runtime files from agent runner.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Dry-run: show what would be deleted
  %(prog)s --confirm          # Actually delete old files
  %(prog)s --keep-days 3      # Override config, keep 3 days
  %(prog)s --target jobs      # Only clean job folders
        """,
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually delete files (default: dry-run only shows what would be deleted)",
    )
    parser.add_argument(
        "--keep-days",
        type=int,
        default=0,
        help="Override config.json cleanup_keep_days setting",
    )
    parser.add_argument(
        "--target",
        choices=["jobs", "runtime", "all"],
        default="all",
        help="Which areas to clean (default: all)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for cleanup command.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = _parse_args(argv)

    # Load config and resolve keep_days
    config = load_runner_config()
    keep_days = args.keep_days or config.get("cleanup_keep_days", 7)
    if keep_days <= 0:
        keep_days = 7

    runner_home = GLOBAL_RUNNER_HOME
    cutoff_time = time.time() - (keep_days * 86400)
    cutoff_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cutoff_time))

    results: list[CleanupSummary] = []
    has_errors = False

    # Clean up jobs
    if args.target in ("jobs", "all"):
        jobs_summary = cleanup_jobs(runner_home, keep_days, dry_run=not args.confirm)
        results.append(jobs_summary)
        if jobs_summary.errors:
            has_errors = True

    # Clean up runtime
    if args.target in ("runtime", "all"):
        runtime_summary = cleanup_runtime(
            runner_home, keep_days, dry_run=not args.confirm
        )
        results.append(runtime_summary)
        if runtime_summary.errors:
            has_errors = True

    # Build output
    total_deleted = sum(r.deleted_count for r in results)
    total_kept = sum(r.kept_count for r in results)
    total_bytes = sum(r.bytes_freed for r in results)
    all_errors = [e for r in results for e in r.errors]

    output: dict[str, Any] = {
        "status": "success" if not has_errors else "partial_error",
        "dry_run": not args.confirm,
        "runner_home": str(runner_home),
        "keep_days": keep_days,
        "cutoff_date": cutoff_date,
        "summary": {
            "total_deleted": total_deleted,
            "total_kept": total_kept,
            "total_bytes_freed": total_bytes,
            "human_readable_size": _format_bytes(total_bytes),
        },
        "targets": {r.target_name: r.to_dict() for r in results},
    }

    if all_errors:
        output["errors"] = all_errors

    print(json.dumps(output, indent=2, ensure_ascii=False))

    return 1 if has_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
