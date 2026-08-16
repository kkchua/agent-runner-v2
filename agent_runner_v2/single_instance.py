"""Cross-platform single-instance enforcement.

Windows: Named mutex via ctypes (kernel-managed, auto-releases on crash)
Linux/WSL: File locking via fcntl (kernel-managed, auto-releases on crash)

Usage:
    from .single_instance import SingleInstanceMutex

    mutex = SingleInstanceMutex("ukbe-runner-daemon")
    if not mutex.acquire():
        print("Already running")
        sys.exit(1)
    # ... do work ...
    mutex.release()  # Optional - auto-released on process exit
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


class SingleInstanceMutex:
    """Cross-platform single-instance mutex.

    Uses Windows named mutex on win32, flock on Unix.
    Both mechanisms are kernel-managed and automatically
    release when the process exits or crashes.

    Args:
        name: Unique name for this mutex (e.g., "ukbe-runner-daemon")
        runtime_dir: Optional directory for lock files (Unix only)
    """

    def __init__(self, name: str, runtime_dir: Path | None = None):
        self.name = name
        self.runtime_dir = runtime_dir
        self._handle: Any = None  # Windows mutex handle
        self._lockfile: Path | None = None
        self._lockfile_fd: Any = None

    def acquire(self) -> bool:
        """Try to acquire the mutex.

        Returns:
            True if acquired, False if another instance is running.
        """
        if sys.platform == "win32":
            return self._acquire_windows()
        else:
            return self._acquire_unix()

    def release(self) -> None:
        """Release the mutex (optional - auto-released on exit)."""
        if sys.platform == "win32":
            self._release_windows()
        else:
            self._release_unix()

    def _acquire_windows(self) -> bool:
        """Windows: Use named mutex via ctypes."""
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32

        # Create named mutex (Global\ prefix for cross-session visibility)
        mutex_name = f"Global\\{self.name}"
        self._handle = kernel32.CreateMutexW(None, False, mutex_name)

        if not self._handle:
            return False

        # ERROR_ALREADY_EXISTS = 183
        already_exists = kernel32.GetLastError() == 183
        if already_exists:
            kernel32.CloseHandle(self._handle)
            self._handle = None
            return False

        return True

    def _release_windows(self) -> None:
        """Windows: Close mutex handle."""
        if self._handle:
            import ctypes

            ctypes.windll.kernel32.CloseHandle(self._handle)
            self._handle = None

    def _acquire_unix(self) -> bool:
        """Unix/Linux: Use flock on lockfile."""
        import fcntl

        # Determine lock directory
        if self.runtime_dir:
            lock_dir = self.runtime_dir
        else:
            lock_dir = Path.home() / ".ukbe-runner" / "locks"

        lock_dir.mkdir(parents=True, exist_ok=True)
        self._lockfile = lock_dir / f"{self.name}.lock"

        # Open lockfile
        self._lockfile_fd = open(self._lockfile, "w")

        try:
            # Try exclusive, non-blocking lock
            fcntl.flock(self._lockfile_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Write PID for debugging
            self._lockfile_fd.write(str(os.getpid()))
            self._lockfile_fd.flush()

            return True
        except (IOError, OSError, BlockingIOError):
            # Already locked by another process
            self._lockfile_fd.close()
            self._lockfile_fd = None
            return False

    def _release_unix(self) -> None:
        """Unix/Linux: Unlock and close lockfile."""
        if self._lockfile_fd:
            import fcntl

            fcntl.flock(self._lockfile_fd, fcntl.LOCK_UN)
            self._lockfile_fd.close()
            self._lockfile_fd = None


def check_single_instance(name: str, error_message: str, runtime_dir: Path | None = None) -> SingleInstanceMutex | None:
    """Check if this is the only instance, exit if not.

    Args:
        name: Mutex name (e.g., "ukbe-runner-daemon")
        error_message: Message to print if already running
        runtime_dir: Optional runtime directory for lock files

    Returns:
        SingleInstanceMutex if acquired, or exits with code 1
    """
    mutex = SingleInstanceMutex(name, runtime_dir)

    if not mutex.acquire():
        print(f"ERROR: {error_message}", file=sys.stderr)
        sys.exit(1)

    return mutex
