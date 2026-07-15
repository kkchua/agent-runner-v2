from __future__ import annotations

from pathlib import Path

from agent_runner_v2.workflow_bundle_validator import validate_workflow_bundle_dir


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_validate_workflow_bundle_dir_accepts_core_governance_bundle() -> None:
    bundle_root = Path("workflows/00_layer1_governance_bootstrap_v1").resolve()
    report = validate_workflow_bundle_dir(bundle_root)

    assert report.valid is True
    assert report.findings == ()


def test_validate_workflow_bundle_dir_rejects_invalid_onsuccess_target(tmp_path: Path) -> None:
    bundle_root = tmp_path / "bad_bundle"
    _write(
        bundle_root / "workflow.toml",
        """
[workflow]
name = "bad_bundle"
version = "1"
job_prefix = "BAD"
init_step = "first"

[[step]]
name = "first"
prompt = "prompts/first.txt"
onsuccess = "missing_step"
""".strip(),
    )
    _write(bundle_root / "prompts/first.txt", "hello\n")

    report = validate_workflow_bundle_dir(bundle_root)

    assert report.valid is False
    assert any(item.code == "onsuccess_target_missing" for item in report.findings)


def test_validate_workflow_bundle_dir_rejects_missing_prompt_file(tmp_path: Path) -> None:
    bundle_root = tmp_path / "missing_prompt_bundle"
    _write(
        bundle_root / "workflow.toml",
        """
[workflow]
name = "missing_prompt_bundle"
version = "1"
job_prefix = "MISS"
init_step = "first"

[[step]]
name = "first"
prompt = "prompts/not_here.txt"
""".strip(),
    )

    report = validate_workflow_bundle_dir(bundle_root)

    assert report.valid is False
    assert any(item.code == "missing_prompt_file" for item in report.findings)


def test_validate_workflow_bundle_dir_rejects_unknown_governance_prompt_target(tmp_path: Path) -> None:
    bundle_root = tmp_path / "governed_bundle"
    _write(
        bundle_root / "workflow.toml",
        """
[workflow]
name = "governed_bundle"
version = "1"
job_prefix = "GOV"
init_step = "first"

[[step]]
name = "first"
prompt = "prompts/first.txt"
""".strip(),
    )
    _write(bundle_root / "prompts/first.txt", "hello\n")
    _write(bundle_root / "bundle_governance/core.md", "core\n")
    _write(
        bundle_root / "bundle_governance.toml",
        """
[governance]
canonical_source = "bundle_governance/core.md"
generated_dir = "bundle_governance/generated"
include_in_prompts = true
prompt_targets = ["missing_step"]
""".strip(),
    )

    report = validate_workflow_bundle_dir(bundle_root)

    assert report.valid is False
    assert any(item.code == "unknown_governance_prompt_target" for item in report.findings)


def test_validate_workflow_bundle_dir_rejects_undeclared_governance_artifact_reference(tmp_path: Path) -> None:
    bundle_root = tmp_path / "undeclared_artifact_bundle"
    _write(
        bundle_root / "workflow.toml",
        """
[workflow]
name = "undeclared_artifact_bundle"
version = "1"
job_prefix = "UAR"
init_step = "first"

[[step]]
name = "first"
prompt = "prompts/first.txt"

[step.artifacts]
produces = ["UNDECLARED_ARTIFACT"]
result_meta_key = "UNDECLARED_ARTIFACT"
""".strip(),
    )
    _write(bundle_root / "prompts/first.txt", "hello\n")
    _write(bundle_root / "bundle_governance/core.md", "core\n")
    _write(
        bundle_root / "bundle_governance.toml",
        """
[governance]
canonical_source = "bundle_governance/core.md"
generated_dir = "bundle_governance/generated"

[[artifact]]
key = "SOME_OTHER_ARTIFACT"
path = "docs/out.md"
required = true
""".strip(),
    )

    report = validate_workflow_bundle_dir(bundle_root)

    assert report.valid is False
    assert any(item.code == "undeclared_governance_artifact_reference" for item in report.findings)


def test_validate_workflow_bundle_dir_rejects_unused_governance_artifact_registry_key(tmp_path: Path) -> None:
    bundle_root = tmp_path / "unused_registry_bundle"
    _write(
        bundle_root / "workflow.toml",
        """
[workflow]
name = "unused_registry_bundle"
version = "1"
job_prefix = "URG"
init_step = "first"

[[step]]
name = "first"
prompt = "prompts/first.txt"

[step.artifacts]
produces = ["USED_ARTIFACT"]
result_meta_key = "USED_ARTIFACT"
""".strip(),
    )
    _write(bundle_root / "prompts/first.txt", "hello\n")
    _write(bundle_root / "bundle_governance/core.md", "core\n")
    _write(
        bundle_root / "bundle_governance.toml",
        """
[governance]
canonical_source = "bundle_governance/core.md"
generated_dir = "bundle_governance/generated"

[[artifact]]
key = "USED_ARTIFACT"
path = "docs/used.md"
required = true

[[artifact]]
key = "UNUSED_ARTIFACT"
path = "docs/unused.md"
required = false
""".strip(),
    )

    report = validate_workflow_bundle_dir(bundle_root)

    assert report.valid is False
    assert any(item.code == "unused_governance_artifact_registry_key" for item in report.findings)


def test_validate_workflow_bundle_dir_rejects_prompt_contract_missing_required_literal(tmp_path: Path) -> None:
    bundle_root = tmp_path / "prompt_contract_bundle"
    _write(
        bundle_root / "workflow.toml",
        """
[workflow]
name = "prompt_contract_bundle"
version = "1"
job_prefix = "PCB"
init_step = "first"

[[step]]
name = "first"
prompt = "prompts/first.txt"
""".strip(),
    )
    _write(bundle_root / "prompts/first.txt", "Role:\nTask:\n")
    _write(
        bundle_root / "bundle_governance/prompt_contract.json",
        """
{
  "version": 1,
  "defaults": {
    "ascii_only": true
  },
  "step_requirements": {
    "first": {
      "required_literals": ["Read first:"]
    }
  }
}
""".strip(),
    )

    report = validate_workflow_bundle_dir(bundle_root)

    assert report.valid is False
    assert any(item.code == "prompt_missing_required_literal" for item in report.findings)


def test_validate_workflow_bundle_dir_rejects_prompt_contract_non_ascii_prompt(tmp_path: Path) -> None:
    bundle_root = tmp_path / "non_ascii_prompt_bundle"
    _write(
        bundle_root / "workflow.toml",
        """
[workflow]
name = "non_ascii_prompt_bundle"
version = "1"
job_prefix = "NAP"
init_step = "first"

[[step]]
name = "first"
prompt = "prompts/first.txt"
""".strip(),
    )
    _write(bundle_root / "prompts/first.txt", "Role:\nThis prompt contains an em dash — bad.\n")
    _write(
        bundle_root / "bundle_governance/prompt_contract.json",
        """
{
  "version": 1,
  "defaults": {
    "ascii_only": true
  }
}
""".strip(),
    )

    report = validate_workflow_bundle_dir(bundle_root)

    assert report.valid is False
    assert any(item.code == "prompt_non_ascii" for item in report.findings)
