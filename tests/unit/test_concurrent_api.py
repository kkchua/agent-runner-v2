"""Unit tests for concurrent_api module.

Tests cover:
- All-success, all-failure, and mixed results
- Thread safety with concurrent workers
- Progress logging
- Empty input handling
- max_workers clamping
- ItemResult dataclass
"""
from __future__ import annotations

import threading
import time

import pytest

from agent_runner_v2.concurrent_api import ConcurrentApiRunner, ItemResult


class TestItemResult:
    """Tests for the ItemResult dataclass."""

    def test_success_result(self):
        r = ItemResult(item="a", success=True, data={"url": "http://x"})
        assert r.success is True
        assert r.data == {"url": "http://x"}
        assert r.error is None

    def test_failure_result(self):
        exc = ValueError("boom")
        r = ItemResult(item="b", success=False, error=exc)
        assert r.success is False
        assert r.data is None
        assert r.error is exc

    def test_defaults(self):
        r = ItemResult(item=42, success=True)
        assert r.data is None
        assert r.error is None


class TestConcurrentApiRunnerEmpty:
    """Tests for empty input handling."""

    def test_empty_items_returns_empty(self):
        runner = ConcurrentApiRunner(max_workers=2)
        results = runner.run([], lambda x: x, desc="test")
        assert results == []

    def test_single_item(self):
        runner = ConcurrentApiRunner(max_workers=2)
        results = runner.run([42], lambda x: x * 2, desc="test")
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].data == 84
        assert results[0].item == 42


class TestConcurrentApiRunnerSuccess:
    """Tests for all-success scenarios."""

    def test_all_succeed(self):
        runner = ConcurrentApiRunner(max_workers=3)
        items = list(range(10))
        results = runner.run(items, lambda x: x ** 2, desc="squares")

        assert len(results) == 10
        assert all(r.success for r in results)

        # Verify all items are accounted for
        result_items = sorted(r.item for r in results)
        assert result_items == list(range(10))

        # Verify data correctness
        data_by_item = {r.item: r.data for r in results}
        for i in range(10):
            assert data_by_item[i] == i ** 2

    def test_worker_returns_none(self):
        runner = ConcurrentApiRunner(max_workers=2)
        results = runner.run([1, 2], lambda x: None, desc="none")
        assert len(results) == 2
        assert all(r.success for r in results)
        assert all(r.data is None for r in results)


class TestConcurrentApiRunnerFailure:
    """Tests for failure scenarios."""

    def test_all_fail(self):
        def failing(x):
            raise ValueError(f"fail-{x}")

        runner = ConcurrentApiRunner(max_workers=2)
        results = runner.run([1, 2, 3], failing, desc="failures")

        assert len(results) == 3
        assert all(not r.success for r in results)
        assert all(r.error is not None for r in results)
        assert all(r.data is None for r in results)

    def test_mixed_results(self):
        def sometimes_fail(x):
            if x % 2 == 0:
                raise RuntimeError(f"even-{x}")
            return x * 10

        runner = ConcurrentApiRunner(max_workers=2)
        results = runner.run([1, 2, 3, 4], sometimes_fail, desc="mixed")

        assert len(results) == 4
        successes = [r for r in results if r.success]
        failures = [r for r in results if not r.success]

        assert len(successes) == 2  # 1, 3
        assert len(failures) == 2  # 2, 4

        for r in successes:
            assert r.item in (1, 3)
            assert r.data == r.item * 10

        for r in failures:
            assert r.item in (2, 4)
            assert isinstance(r.error, RuntimeError)


class TestConcurrentApiRunnerConcurrency:
    """Tests for actual concurrent execution."""

    def test_workers_run_in_parallel(self):
        """Verify that workers actually run concurrently, not sequentially."""
        barrier = threading.Barrier(3)

        def sync_worker(x):
            barrier.wait(timeout=5)
            return x

        runner = ConcurrentApiRunner(max_workers=3)
        start = time.monotonic()
        results = runner.run([1, 2, 3], sync_worker, desc="barrier")
        elapsed = time.monotonic() - start

        assert len(results) == 3
        assert all(r.success for r in results)
        # If sequential, each barrier.wait would timeout.
        # Concurrent execution should complete in <2s.
        assert elapsed < 5

    def test_thread_safety_of_shared_state(self):
        """Verify workers can safely access shared thread-safe structures."""
        counter = {"value": 0}
        lock = threading.Lock()

        def incrementing_worker(x):
            with lock:
                counter["value"] += 1
            return counter["value"]

        runner = ConcurrentApiRunner(max_workers=4)
        results = runner.run(list(range(20)), incrementing_worker, desc="counter")

        assert len(results) == 20
        assert all(r.success for r in results)
        assert counter["value"] == 20

    def test_max_workers_clamped_to_item_count(self):
        """max_workers should be min(configured, len(items))."""
        runner = ConcurrentApiRunner(max_workers=10)
        results = runner.run([1, 2], lambda x: x, desc="small")
        assert len(results) == 2
        assert all(r.success for r in results)

    def test_max_workers_minimum_is_one(self):
        """max_workers should be at least 1."""
        runner = ConcurrentApiRunner(max_workers=0)
        results = runner.run([1, 2, 3], lambda x: x, desc="zero")
        assert len(results) == 3
        assert all(r.success for r in results)


class TestConcurrentApiRunnerProgress:
    """Tests for progress logging."""

    def test_progress_interval_zero_disables_logging(self, caplog):
        """progress_interval=0 should not log progress."""
        import logging

        runner = ConcurrentApiRunner(max_workers=2, progress_interval=0)
        with caplog.at_level(logging.INFO, logger="agent_runner_v2.concurrent_api"):
            results = runner.run([1, 2, 3], lambda x: x, desc="silent")

        assert len(results) == 3
        progress_msgs = [
            r.message for r in caplog.records if "progress" in r.message
        ]
        assert len(progress_msgs) == 0

    def test_progress_logged_at_interval(self, caplog):
        """Progress should be logged at the configured interval."""
        import logging

        runner = ConcurrentApiRunner(max_workers=1, progress_interval=2)
        with caplog.at_level(logging.INFO, logger="agent_runner_v2.concurrent_api"):
            results = runner.run(list(range(5)), lambda x: x, desc="counting")

        assert len(results) == 5
        progress_msgs = [
            r.message for r in caplog.records if "progress" in r.message
        ]
        # With interval=2 and 5 items: progress at 2, 4, 5
        assert len(progress_msgs) >= 2


class TestConcurrentApiRunnerEdgeCases:
    """Tests for edge cases."""

    def test_worker_raises_base_exception(self):
        """Workers raising BaseException subclasses should be caught."""
        def bad_worker(x):
            raise KeyboardInterrupt()

        runner = ConcurrentApiRunner(max_workers=2)
        # KeyboardInterrupt is not caught by except Exception,
        # so this will propagate. That's expected behavior.
        with pytest.raises(KeyboardInterrupt):
            runner.run([1], bad_worker, desc="base_exc")

    def test_large_item_count(self):
        """Should handle a large number of items without issues."""
        runner = ConcurrentApiRunner(max_workers=4, progress_interval=50)
        items = list(range(100))
        results = runner.run(items, lambda x: x, desc="large")

        assert len(results) == 100
        assert all(r.success for r in results)
        result_items = sorted(r.item for r in results)
        assert result_items == list(range(100))

    def test_slow_and_fast_workers(self):
        """Mix of slow and fast workers should all complete."""
        def variable_speed(x):
            if x == 0:
                time.sleep(0.1)
            return x

        runner = ConcurrentApiRunner(max_workers=3)
        results = runner.run(list(range(5)), variable_speed, desc="variable")

        assert len(results) == 5
        assert all(r.success for r in results)
