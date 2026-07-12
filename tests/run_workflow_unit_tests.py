from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def _workflow_test_root() -> Path:
    return Path(__file__).resolve().parent / "unit" / "workflows"


def _discover_workflows(root: Path) -> list[str]:
    return sorted(
        child.name
        for child in root.iterdir()
        if child.is_dir() and not child.name.startswith("_") and child.name != "__pycache__"
    )


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    root = _workflow_test_root()
    workflows = _discover_workflows(root)

    if not args or args == ["all"]:
        selected = workflows
    else:
        selected = args
        unknown = [name for name in selected if not (root / name).is_dir()]
        if unknown:
            print(f"Unknown workflow test group(s): {', '.join(unknown)}", file=sys.stderr)
            print(f"Available groups: {', '.join(workflows)}", file=sys.stderr)
            return 2

    pytest_args = [str(root / name) for name in selected]
    basetemp = Path(tempfile.gettempdir()) / "agent-runner-v2-workflow-tests"
    cmd = [sys.executable, "-m", "pytest", f"--basetemp={basetemp}", *pytest_args]
    print("Running:", " ".join(cmd))
    completed = subprocess.run(cmd, cwd=Path(__file__).resolve().parents[1])
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
