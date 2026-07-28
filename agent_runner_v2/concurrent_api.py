"""Concurrent API execution utility for workflow actions.

Provides a reusable wrapper around ``concurrent.futures.ThreadPoolExecutor``
tailored for I/O-bound API calls (image generation, video generation, etc.).
Handles thread-safe result collection, progress logging, and error handling.

Usage::

    from agent_runner_v2.concurrent_api import ConcurrentApiRunner, ItemResult

    def my_worker(item):
        # ... call API, download file, etc.
        return {"output_path": "/path/to/output"}

    runner = ConcurrentApiRunner(max_workers=2)
    results = runner.run(items=[item1, item2, item3], worker_fn=my_worker, desc="generating")

    for r in results:
        if r.success:
            print(f"OK: {r.data}")
        else:
            print(f"FAIL: {r.error}")
"""
from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class ItemResult:
    """Result of processing a single item through a concurrent worker.

    Attributes:
        item: The original input item that was processed.
        success: Whether the worker completed without raising.
        data: Return value from the worker on success, or None on failure.
        error: Exception instance on failure, or None on success.
    """

    item: Any
    success: bool
    data: Any = None
    error: BaseException | None = None


class ConcurrentApiRunner:
    """Thread-pool based runner for parallel I/O-bound API calls.

    Manages a ``ThreadPoolExecutor`` to process items concurrently, with
    thread-safe progress tracking and result collection.

    Args:
        max_workers: Maximum number of concurrent worker threads.
        progress_interval: Log a progress message every N completed items.
            Set to 0 to disable progress logging.
    """

    def __init__(self, max_workers: int = 2, progress_interval: int = 5) -> None:
        self.max_workers = max(1, max_workers)
        self.progress_interval = progress_interval

    def run(
        self,
        items: list[T],
        worker_fn: Callable[[T], Any],
        *,
        desc: str = "processing",
    ) -> list[ItemResult]:
        """Process all items concurrently using the worker function.

        Each item is dispatched to a thread-pool worker.  Results are
        collected as futures complete (not in submission order).

        Args:
            items: List of items to process.
            worker_fn: Callable that takes a single item and returns a result
                dict/value on success, or raises on failure.
            desc: Human-readable description for progress log messages.

        Returns:
            List of :class:`ItemResult` instances — one per input item.
        """
        if not items:
            return []

        total = len(items)
        results: list[ItemResult] = []
        results_lock = threading.Lock()
        completed_count = 0
        count_lock = threading.Lock()

        effective_workers = min(self.max_workers, total)
        logger.info(
            "ConcurrentApiRunner: starting %s — %d item(s), %d worker(s)",
            desc, total, effective_workers,
        )

        def _safe_worker(item: T) -> ItemResult:
            try:
                data = worker_fn(item)
                return ItemResult(item=item, success=True, data=data)
            except Exception as exc:
                return ItemResult(item=item, success=False, error=exc)

        with ThreadPoolExecutor(max_workers=effective_workers) as executor:
            future_to_item = {
                executor.submit(_safe_worker, item): item for item in items
            }

            for future in as_completed(future_to_item):
                result = future.result()
                with results_lock:
                    results.append(result)

                with count_lock:
                    completed_count += 1
                    current = completed_count

                if self.progress_interval > 0 and (
                    current % self.progress_interval == 0 or current == total
                ):
                    successes = sum(1 for r in results if r.success)
                    failures = sum(1 for r in results if not r.success)
                    logger.info(
                        "ConcurrentApiRunner: %s progress — %d/%d "
                        "(%d ok, %d failed)",
                        desc, current, total, successes, failures,
                    )

        final_successes = sum(1 for r in results if r.success)
        final_failures = sum(1 for r in results if not r.success)
        logger.info(
            "ConcurrentApiRunner: %s complete — %d/%d succeeded, %d failed",
            desc, final_successes, total, final_failures,
        )

        return results
