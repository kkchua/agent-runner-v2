from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[1]
repo_root_str = str(REPO_ROOT)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)

REPO_TEMP_ROOT = REPO_ROOT / ".tmp"
REPO_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("TEMP", str(REPO_TEMP_ROOT))
os.environ.setdefault("TMP", str(REPO_TEMP_ROOT))
os.environ.setdefault("TMPDIR", str(REPO_TEMP_ROOT))
tempfile.tempdir = str(REPO_TEMP_ROOT)


def load_bootstrap_workflow_module() -> ModuleType:
    module_path = REPO_ROOT / "agent_runner_v2" / "bootstrap" / "workflows" / "default" / "template_groups.py"
    spec = importlib.util.spec_from_file_location("tests.bootstrap_template_groups", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load workflow bundle from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
