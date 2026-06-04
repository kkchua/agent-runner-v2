"""Lightweight migration runner for agent-runner-v2.

Discovers numbered migration modules in agent_runner_v2/db/migrations/,
executes up() or down() entry points in order, and tracks applied migrations
via a _migration_log table.

Related: IMPL-20260602-01
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import List

import psycopg2


MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def _ensure_log_table(conn) -> None:
    """Create the _migration_log table if it doesn't exist.

    Tracks applied migration numbers so the runner knows which migrations
    have already been executed against this database.
    """
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS _migration_log (
                migration_number INTEGER PRIMARY KEY,
                applied_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
    conn.commit()


def get_applied_migrations(conn) -> set[int]:
    """Return the set of migration numbers already applied."""
    _ensure_log_table(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT migration_number FROM _migration_log;")
        return {row[0] for row in cur.fetchall()}


def _discover_migrations() -> list[tuple[int, str]]:
    """Discover numbered migration modules in the migrations directory.

    Returns a list of (number, module_name) tuples sorted by number ascending.
    Module names follow the pattern: NNN_description (e.g., 001_create_agent_runner_jobs).
    """
    migrations: list[tuple[int, str]] = []
    if not MIGRATIONS_DIR.exists():
        raise FileNotFoundError(f"Migrations directory not found: {MIGRATIONS_DIR}")

    for entry in sorted(MIGRATIONS_DIR.iterdir()):
        if entry.is_file() and entry.name.endswith(".py") and entry.name != "__init__.py":
            # Extract the numeric prefix (e.g., "001" from "001_create_agent_runner_jobs.py")
            parts = entry.name.split("_", 1)
            if parts[0].isdigit():
                num = int(parts[0])
                module_name = entry.name[:-3]  # strip .py
                migrations.append((num, module_name))

    migrations.sort(key=lambda x: x[0])
    return migrations


def _load_migration(module_name: str):
    """Dynamically import a migration module by name."""
    full_name = f"agent_runner_v2.db.migrations.{module_name}"
    return importlib.import_module(full_name)


def run_up(conn, target: int | None = None) -> list[int]:
    """Apply all unapplied migrations in ascending order.

    Args:
        conn: psycopg2 connection (will be used within transactions).
        target: Optional migration number to run up to (inclusive). If None, runs all.

    Returns:
        List of migration numbers that were applied in this run.
    """
    applied = get_applied_migrations(conn)
    migrations = _discover_migrations()
    executed: list[int] = []

    for num, module_name in migrations:
        if target is not None and num > target:
            break
        if num in applied:
            continue

        mod = _load_migration(module_name)
        if not hasattr(mod, "up"):
            raise AttributeError(f"Migration {module_name} missing required up() function")

        print(f"Applying migration {num}: {module_name}...")
        mod.up(conn)
        conn.commit()

        # Record in migration log
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO _migration_log (migration_number) VALUES (%s);",
                (num,)
            )
        conn.commit()

        executed.append(num)
        print(f"  Applied migration {num}.")

    if not executed:
        print("No unapplied migrations found.")
    else:
        print(f"Applied {len(executed)} migration(s): {executed}")

    return executed


def run_down(conn, target: int | None = None) -> list[int]:
    """Reverse applied migrations in descending order.

    Args:
        conn: psycopg2 connection.
        target: Optional migration number to roll back to (exclusive).
                If None, rolls back all applied migrations.

    Returns:
        List of migration numbers that were rolled back in this run.
    """
    applied = get_applied_migrations(conn)
    migrations = _discover_migrations()
    # Filter to only applied migrations, sort descending
    to_rollback = [(num, mod) for num, mod in migrations if num in applied]
    to_rollback.sort(key=lambda x: x[0], reverse=True)
    executed: list[int] = []

    for num, module_name in to_rollback:
        if target is not None and num <= target:
            break

        mod = _load_migration(module_name)
        if not hasattr(mod, "down"):
            raise AttributeError(f"Migration {module_name} missing required down() function")

        print(f"Rolling back migration {num}: {module_name}...")
        mod.down(conn)
        conn.commit()

        # Remove from migration log
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM _migration_log WHERE migration_number = %s;",
                (num,)
            )
        conn.commit()

        executed.append(num)
        print(f"  Rolled back migration {num}.")

    if not executed:
        print("No migrations to roll back.")
    else:
        print(f"Rolled back {len(executed)} migration(s): {executed}")

    return executed


def main() -> None:
    """CLI entry point for migration runner.

    Usage:
        python -m agent_runner_v2.db.migrate up [target]
        python -m agent_runner_v2.db.migrate down [target]

    Requires DATABASE_URL environment variable (e.g., postgresql://user:pass@host/dbname).
    """
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]
    if not args or args[0] not in ("up", "down"):
        print("Usage: python -m agent_runner_v2.db.migrate up [target]", file=sys.stderr)
        print("       python -m agent_runner_v2.db.migrate down [target]", file=sys.stderr)
        sys.exit(1)

    command = args[0]
    target = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    conn = psycopg2.connect(database_url)
    try:
        if command == "up":
            run_up(conn, target)
        elif command == "down":
            run_down(conn, target)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
