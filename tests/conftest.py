from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from types import ModuleType

import pytest

from agent_runner_v2 import bundle_loader

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


@pytest.fixture
def project_root() -> Path:
    """Return the absolute path to the repository root."""
    return REPO_ROOT


def load_bootstrap_workflow_module() -> ModuleType:
    workflow_root = REPO_ROOT / "agent_runner_v2" / "bootstrap" / "workflows" / "default"
    return bundle_loader._build_workflow_module_from_packages(workflow_root, "bootstrap-tests")
