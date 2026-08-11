"""Tests for the AGB assemble_package action.

Verifies that assemble_package deterministically builds workflow.toml,
context_extensions.py, and impl.yaml files from an Analysis JSON.
"""
from __future__ import annotations

import ast
import json
import sys
import tomllib
from pathlib import Path
from unittest.mock import MagicMock

import yaml
import pytest

# Add workflows dir to path so we can import the actions module
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2] / "workflows" / "artifact_generator_builder"),
)

from agent_runner_v2.action_result import ActionResult


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


SAMPLE_ANALYSIS = {
    "identity": {
        "name": "text_summarizer_test",
        "job_prefix": "TXTSUM",
        "version": "1.0.0",
        "label": "Text Summarizer Test",
        "description": "Test summarizer workflow",
        "codename": "text_summarizer_test",
    },
    "domain_steps": [
        {
            "name": "parse_input",
            "type": "action",
            "action_name": "parse_input_document",
            "required_inputs": ["SOURCE_DOCUMENT_FILE"],
            "produces": ["PARSED_DOCUMENT"],
        },
        {
            "name": "analyze_structure",
            "type": "prompt",
            "prompt_file": "02_analyze.txt",
            "role_policy": "architect_standard",
            "required_inputs": ["PARSED_DOCUMENT"],
            "produces": ["ANALYSIS_RESULT"],
        },
        {
            "name": "render_output",
            "type": "action",
            "action_name": "render_prose_output",
            "required_inputs": ["ANALYSIS_RESULT"],
            "produces": ["SUMMARY_FILE"],
        },
    ],
    "artifact_keys": {
        "inputs": [
            {"key": "SOURCE_DOCUMENT_FILE", "pattern": "input/{filename}"},
        ],
        "intermediate": [
            {"key": "PARSED_DOCUMENT", "pattern": "intermediate/PARSED_DOCUMENT.json"},
            {"key": "ANALYSIS_RESULT", "pattern": "intermediate/ANALYSIS_RESULT.json"},
        ],
        "outputs": [
            {"key": "SUMMARY_FILE", "pattern": "output/SUMMARY_FILE.md"},
        ],
    },
    "implementations": [
        {
            "name": "key_points",
            "description": "Produces key points list",
            "label": "Key Points",
            "overrides": {
                "render_output": {"action": "render_list_output"},
            },
        },
    ],
}


@pytest.fixture
def out_dir(tmp_path):
    """Create a temporary output directory with a sample Analysis JSON."""
    analysis_path = tmp_path / "output" / "ANALYSIS_JSON-001.json"
    _write(analysis_path, json.dumps(SAMPLE_ANALYSIS, indent=2))
    return tmp_path / "output"


@pytest.fixture
def mock_state(out_dir):
    """Mock job state with artifact paths."""
    return {
        "job_id": "TEST-001",
        "artifacts": {
            "ANALYSIS_JSON_FILE": str(out_dir / "ANALYSIS_JSON-001.json"),
            "WORKFLOW_ACTIONS_FILE": str(out_dir / "actions.py"),
        },
    }


class TestAssemblePackage:
    """Tests for the assemble_package action."""

    def test_generates_workflow_toml(self, out_dir, mock_state):
        """assemble_package produces a valid workflow.toml."""
        from actions import assemble_package

        result = assemble_package(
            context={},
            state=mock_state,
            step_cfg={},
            project_root=out_dir.parent,
        )

        assert result.status == "APPROVED"
        manifest_path = Path(result.artifacts["WORKFLOW_MANIFEST_FILE"])
        assert manifest_path.exists()

        content = manifest_path.read_text(encoding="utf-8")
        assert 'name = "text_summarizer_test"' in content
        assert 'job_prefix = "TXTSUM"' in content
        assert 'init_step = "parse_input"' in content
        assert 'action = "parse_input_document"' in content
        assert 'prompt = "prompts/02_analyze.txt"' in content
        assert 'onsuccess = "step_completion"' in content
        assert 'name = "step_completion"' in content

    def test_generates_context_extensions(self, out_dir, mock_state):
        """assemble_package produces context_extensions.py with correct class."""
        from actions import assemble_package

        result = assemble_package(
            context={},
            state=mock_state,
            step_cfg={},
            project_root=out_dir.parent,
        )

        assert result.status == "APPROVED"
        ext_path = Path(result.artifacts["WORKFLOW_EXTENSIONS_FILE"])
        assert ext_path.exists()

        content = ext_path.read_text(encoding="utf-8")
        assert "class TextSummarizerTestExtensions(WorkflowExtensions):" in content
        assert 'workflow_name = "text_summarizer_test"' in content
        assert '"SOURCE_DOCUMENT_FILE"' in content
        assert '"PARSED_DOCUMENT"' in content
        assert '"SUMMARY_FILE"' in content

    def test_generates_impl_yaml(self, out_dir, mock_state):
        """assemble_package produces impl.yaml for each implementation."""
        from actions import assemble_package

        result = assemble_package(
            context={},
            state=mock_state,
            step_cfg={},
            project_root=out_dir.parent,
        )

        assert result.status == "APPROVED"
        impl_yaml = out_dir / "impls" / "key_points" / "impl.yaml"
        assert impl_yaml.exists()

        content = impl_yaml.read_text(encoding="utf-8")
        assert "name: key_points" in content
        assert "render_output:" in content
        assert 'action: "render_list_output"' in content

    def test_workflow_toml_has_impl_declaration(self, out_dir, mock_state):
        """workflow.toml includes [[workflow.implementation]] declarations."""
        from actions import assemble_package

        result = assemble_package(
            context={},
            state=mock_state,
            step_cfg={},
            project_root=out_dir.parent,
        )

        content = Path(result.artifacts["WORKFLOW_MANIFEST_FILE"]).read_text()
        assert "[[workflow.implementation]]" in content
        assert 'name = "key_points"' in content

    def test_step_chaining(self, out_dir, mock_state):
        """Steps are chained in declared order via onsuccess."""
        from actions import assemble_package

        result = assemble_package(
            context={},
            state=mock_state,
            step_cfg={},
            project_root=out_dir.parent,
        )

        content = Path(result.artifacts["WORKFLOW_MANIFEST_FILE"]).read_text()
        # parse_input → analyze_structure
        assert 'onsuccess = "analyze_structure"' in content
        # analyze_structure → render_output
        assert 'onsuccess = "render_output"' in content
        # render_output → step_completion (last domain step)
        lines = content.split("\n")
        render_idx = next(
            i for i, l in enumerate(lines) if 'name = "render_output"' in l
        )
        # Find onsuccess after render_output
        for line in lines[render_idx:]:
            if "onsuccess" in line:
                assert '"step_completion"' in line
                break

    def test_missing_analysis_json_rejected(self, tmp_path):
        """assemble_package rejects when ANALYSIS_JSON_FILE is missing."""
        from actions import assemble_package

        result = assemble_package(
            context={},
            state={"artifacts": {}},
            step_cfg={},
            project_root=tmp_path,
        )

        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_ANALYSIS_JSON"

    def test_invalid_json_rejected(self, tmp_path):
        """assemble_package rejects when Analysis JSON is malformed."""
        from actions import assemble_package

        bad_json = tmp_path / "bad.json"
        _write(bad_json, "not valid json {{{")

        result = assemble_package(
            context={},
            state={"artifacts": {"ANALYSIS_JSON_FILE": str(bad_json)}},
            step_cfg={},
            project_root=tmp_path,
        )

        assert result.status == "REJECTED"
        assert result.reject_code == "PARSE_ERROR"

    def test_empty_domain_steps_rejected(self, tmp_path):
        """assemble_package rejects when domain_steps is empty."""
        from actions import assemble_package

        analysis = {"identity": {"name": "test"}, "domain_steps": []}
        analysis_path = tmp_path / "empty.json"
        _write(analysis_path, json.dumps(analysis))

        result = assemble_package(
            context={},
            state={"artifacts": {"ANALYSIS_JSON_FILE": str(analysis_path)}},
            step_cfg={},
            project_root=tmp_path,
        )

        assert result.status == "REJECTED"
        assert result.reject_code == "INVALID_ANALYSIS"

    def test_artifact_bindings_in_toml(self, out_dir, mock_state):
        """Step artifact bindings (required_inputs, produces) appear in TOML."""
        from actions import assemble_package

        result = assemble_package(
            context={},
            state=mock_state,
            step_cfg={},
            project_root=out_dir.parent,
        )

        content = Path(result.artifacts["WORKFLOW_MANIFEST_FILE"]).read_text()
        assert '"SOURCE_DOCUMENT_FILE"' in content
        assert '"PARSED_DOCUMENT"' in content
        assert '"SUMMARY_FILE"' in content
        assert "required_inputs" in content
        assert "produces" in content

    def test_coder_role_policy_in_toml(self, out_dir, mock_state):
        """Prompt steps include [step.coder] with role_policy."""
        from actions import assemble_package

        result = assemble_package(
            context={},
            state=mock_state,
            step_cfg={},
            project_root=out_dir.parent,
        )

        content = Path(result.artifacts["WORKFLOW_MANIFEST_FILE"]).read_text()
        assert "[step.coder]" in content
        assert 'role_policy = "architect_standard"' in content

    def test_no_impls_produces_no_impl_dir(self, tmp_path):
        """When no implementations declared, no impls/ directory created."""
        from actions import assemble_package

        analysis = {
            "identity": {
                "name": "simple_workflow",
                "job_prefix": "SIM",
                "version": "1.0.0",
            },
            "domain_steps": [
                {
                    "name": "do_thing",
                    "type": "action",
                    "action_name": "do_thing",
                    "required_inputs": [],
                    "produces": ["OUTPUT"],
                },
            ],
            "artifact_keys": {"inputs": [], "intermediate": [], "outputs": []},
            "implementations": [],
        }
        analysis_path = tmp_path / "simple.json"
        _write(analysis_path, json.dumps(analysis))

        result = assemble_package(
            context={},
            state={"artifacts": {"ANALYSIS_JSON_FILE": str(analysis_path)}},
            step_cfg={},
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        assert not (tmp_path / "impls").exists()


class TestToPascalCase:
    """Tests for the _to_pascal_case helper."""

    def test_snake_case(self):
        from actions import _to_pascal_case
        assert _to_pascal_case("text_summarizer") == "TextSummarizer"

    def test_single_word(self):
        from actions import _to_pascal_case
        assert _to_pascal_case("hello") == "Hello"

    def test_hyphenated(self):
        from actions import _to_pascal_case
        assert _to_pascal_case("my-workflow") == "MyWorkflow"

    def test_mixed(self):
        from actions import _to_pascal_case
        assert _to_pascal_case("my_cool-workflow") == "MyCoolWorkflow"


class TestGeneratedSyntaxValidation:
    """Verify generated files have valid syntax (B1, B2)."""

    def test_generated_toml_parses(self, out_dir, mock_state):
        """Generated workflow.toml is valid TOML."""
        from actions import assemble_package

        result = assemble_package(
            context={}, state=mock_state, step_cfg={}, project_root=out_dir.parent,
        )
        assert result.status == "APPROVED"
        manifest_path = Path(result.artifacts["WORKFLOW_MANIFEST_FILE"])
        content = manifest_path.read_text(encoding="utf-8")
        parsed = tomllib.loads(content)
        assert "workflow" in parsed
        assert "step" in parsed

    def test_generated_python_compiles(self, out_dir, mock_state):
        """Generated context_extensions.py is valid Python."""
        from actions import assemble_package

        result = assemble_package(
            context={}, state=mock_state, step_cfg={}, project_root=out_dir.parent,
        )
        assert result.status == "APPROVED"
        ext_path = Path(result.artifacts["WORKFLOW_EXTENSIONS_FILE"])
        content = ext_path.read_text(encoding="utf-8")
        ast.parse(content)


class TestRolePolicyValidation:
    """Verify prompt steps without role_policy are rejected (A3)."""

    def test_prompt_step_missing_role_policy_rejected(self, tmp_path):
        """Prompt step without role_policy is rejected."""
        from actions import assemble_package

        analysis = {
            "identity": {"name": "test", "job_prefix": "TST", "version": "1.0.0"},
            "domain_steps": [
                {
                    "name": "analyze",
                    "type": "prompt",
                    "prompt_file": "analyze.txt",
                    # missing role_policy
                    "required_inputs": [],
                    "produces": ["RESULT"],
                },
            ],
            "artifact_keys": {"inputs": [], "intermediate": [], "outputs": []},
            "implementations": [],
        }
        analysis_path = tmp_path / "bad_role.json"
        _write(analysis_path, json.dumps(analysis))

        result = assemble_package(
            context={},
            state={"artifacts": {"ANALYSIS_JSON_FILE": str(analysis_path)}},
            step_cfg={},
            project_root=tmp_path,
        )
        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_ROLE_POLICY"


class TestTomlStrEscaping:
    """Verify _toml_str handles special characters (B3)."""

    def test_escapes_newline(self):
        from actions import _toml_str
        assert "\\n" in _toml_str("line1\nline2")

    def test_escapes_carriage_return(self):
        from actions import _toml_str
        assert "\\r" in _toml_str("line1\rline2")

    def test_escapes_tab(self):
        from actions import _toml_str
        assert "\\t" in _toml_str("col1\tcol2")

    def test_escapes_backslash(self):
        from actions import _toml_str
        assert "\\\\" in _toml_str("path\\to\\file")

    def test_escapes_double_quote(self):
        from actions import _toml_str
        assert '\\"' in _toml_str('say "hello"')


class TestGeneratedImplYaml:
    """Verify generated impl.yaml is valid YAML (R3-5)."""

    def test_impl_yaml_parses(self, out_dir, mock_state):
        """Generated impl.yaml is valid YAML."""
        from actions import assemble_package

        result = assemble_package(
            context={}, state=mock_state, step_cfg={}, project_root=out_dir.parent,
        )
        assert result.status == "APPROVED"
        impl_yaml = out_dir / "impls" / "key_points" / "impl.yaml"
        assert impl_yaml.exists()
        content = impl_yaml.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert parsed["name"] == "key_points"
        assert "overrides" in parsed
        assert "render_output" in parsed["overrides"]


class TestGeneratedContextExtensions:
    """Verify generated context_extensions.py includes governance vars (R3-1)."""

    def test_governance_vars_injected(self, out_dir, mock_state):
        """Generated context_extensions.py injects BASE_COMPOSITION_STANDARD etc."""
        from actions import assemble_package

        result = assemble_package(
            context={}, state=mock_state, step_cfg={}, project_root=out_dir.parent,
        )
        assert result.status == "APPROVED"
        ext_path = Path(result.artifacts["WORKFLOW_EXTENSIONS_FILE"])
        content = ext_path.read_text(encoding="utf-8")
        assert "GOVERNANCE_RUNTIME_ROOT" in content
        assert "PLATFORM_RUNTIME_ROOT" in content
        assert "BASE_COMPOSITION_STANDARD" in content
        assert "get_governance_runtime_root" in content


class TestGeneratedWorkflowMetadata:
    """Verify generated workflow.toml includes metadata fields (R3-8)."""

    def test_metadata_fields_present(self, out_dir, mock_state):
        """Generated workflow.toml includes default_max_rejects, visibility, etc."""
        from actions import assemble_package

        result = assemble_package(
            context={}, state=mock_state, step_cfg={}, project_root=out_dir.parent,
        )
        assert result.status == "APPROVED"
        manifest_path = Path(result.artifacts["WORKFLOW_MANIFEST_FILE"])
        content = manifest_path.read_text(encoding="utf-8")
        parsed = tomllib.loads(content)
        wf = parsed["workflow"]
        assert wf.get("default_max_rejects") == 3
        assert wf.get("visibility") == "canonical"
        assert wf.get("layer") == "layer3"
        assert wf.get("platform") == "agent-runner-v2"


class TestExtendMode:
    """Verify extend mode copies existing workflow and adds new implementations."""

    def test_extend_mode_copies_existing_workflow(self, tmp_path):
        """Extend mode copies existing workflow.toml and context_extensions.py."""
        from actions import assemble_package

        # Create existing workflow
        existing_dir = tmp_path / "existing_workflow"
        existing_dir.mkdir()
        _write(existing_dir / "workflow.toml", '[workflow]\nname = "test_workflow"\n')
        _write(existing_dir / "context_extensions.py", "# existing extensions\n")
        _write(existing_dir / "actions.py", "# existing actions\n")

        # Create Analysis JSON with extend_mode
        analysis = {
            "identity": {"name": "test_workflow", "job_prefix": "TST", "version": "1.0.0"},
            "domain_steps": [
                {
                    "name": "do_thing",
                    "type": "action",
                    "action_name": "do_thing",
                    "required_inputs": [],
                    "produces": ["OUTPUT"],
                },
            ],
            "artifact_keys": {"inputs": [], "intermediate": [], "outputs": []},
            "implementations": [
                {
                    "name": "new_impl",
                    "description": "New implementation",
                    "overrides": {"do_thing": {"action": "do_thing_v2"}},
                },
            ],
            "extend_mode": True,
        }
        analysis_path = tmp_path / "extend_analysis.json"
        _write(analysis_path, json.dumps(analysis))

        result = assemble_package(
            context={},
            state={"artifacts": {
                "ANALYSIS_JSON_FILE": str(analysis_path),
                "EXISTING_WORKFLOW_DIR": str(existing_dir),
            }},
            step_cfg={},
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        assert "Extended workflow" in result.remark

        # Verify files were copied
        out_dir = Path(result.artifacts["WORKFLOW_MANIFEST_FILE"]).parent
        assert (out_dir / "workflow.toml").exists()
        assert (out_dir / "context_extensions.py").exists()
        assert (out_dir / "actions.py").exists()

        # Verify new impl declaration was added
        toml_content = (out_dir / "workflow.toml").read_text(encoding="utf-8")
        assert "[[workflow.implementation]]" in toml_content
        assert 'name = "new_impl"' in toml_content

    def test_extend_mode_generates_new_impl_yaml(self, tmp_path):
        """Extend mode generates impl.yaml for new implementations only."""
        from actions import assemble_package

        # Create existing workflow with existing impl
        existing_dir = tmp_path / "existing_workflow"
        existing_dir.mkdir()
        _write(existing_dir / "workflow.toml", '[workflow]\nname = "test_workflow"\n')
        existing_impls = existing_dir / "impls" / "existing_impl"
        existing_impls.mkdir(parents=True)
        _write(existing_impls / "impl.yaml", "name: existing_impl\ndescription: Existing\n")

        # Create Analysis JSON with extend_mode
        analysis = {
            "identity": {"name": "test_workflow", "job_prefix": "TST", "version": "1.0.0"},
            "domain_steps": [
                {
                    "name": "do_thing",
                    "type": "action",
                    "action_name": "do_thing",
                    "required_inputs": [],
                    "produces": ["OUTPUT"],
                },
            ],
            "artifact_keys": {"inputs": [], "intermediate": [], "outputs": []},
            "implementations": [
                {
                    "name": "new_impl",
                    "description": "New implementation",
                    "overrides": {"do_thing": {"action": "do_thing_v2"}},
                },
            ],
            "extend_mode": True,
        }
        analysis_path = tmp_path / "extend_analysis.json"
        _write(analysis_path, json.dumps(analysis))

        result = assemble_package(
            context={},
            state={"artifacts": {
                "ANALYSIS_JSON_FILE": str(analysis_path),
                "EXISTING_WORKFLOW_DIR": str(existing_dir),
            }},
            step_cfg={},
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        out_dir = Path(result.artifacts["WORKFLOW_MANIFEST_FILE"]).parent

        # Verify existing impl was copied
        assert (out_dir / "impls" / "existing_impl" / "impl.yaml").exists()

        # Verify new impl was generated
        new_impl_yaml = out_dir / "impls" / "new_impl" / "impl.yaml"
        assert new_impl_yaml.exists()
        content = new_impl_yaml.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert parsed["name"] == "new_impl"
        assert "do_thing" in parsed["overrides"]

    def test_extend_mode_rejects_without_existing_workflow_dir(self, tmp_path):
        """Extend mode rejects when EXISTING_WORKFLOW_DIR is missing."""
        from actions import assemble_package

        analysis = {
            "identity": {"name": "test", "job_prefix": "TST", "version": "1.0.0"},
            "domain_steps": [
                {
                    "name": "do_thing",
                    "type": "action",
                    "action_name": "do_thing",
                    "required_inputs": [],
                    "produces": ["OUTPUT"],
                },
            ],
            "artifact_keys": {"inputs": [], "intermediate": [], "outputs": []},
            "implementations": [],
            "extend_mode": True,
        }
        analysis_path = tmp_path / "extend_analysis.json"
        _write(analysis_path, json.dumps(analysis))

        result = assemble_package(
            context={},
            state={"artifacts": {"ANALYSIS_JSON_FILE": str(analysis_path)}},
            step_cfg={},
            project_root=tmp_path,
        )

        assert result.status == "REJECTED"
        assert result.reject_code == "MISSING_EXISTING_WORKFLOW"

    def test_extend_mode_rejects_with_nonexistent_dir(self, tmp_path):
        """Extend mode rejects when existing workflow directory doesn't exist."""
        from actions import assemble_package

        analysis = {
            "identity": {"name": "test", "job_prefix": "TST", "version": "1.0.0"},
            "domain_steps": [
                {
                    "name": "do_thing",
                    "type": "action",
                    "action_name": "do_thing",
                    "required_inputs": [],
                    "produces": ["OUTPUT"],
                },
            ],
            "artifact_keys": {"inputs": [], "intermediate": [], "outputs": []},
            "implementations": [],
            "extend_mode": True,
        }
        analysis_path = tmp_path / "extend_analysis.json"
        _write(analysis_path, json.dumps(analysis))

        result = assemble_package(
            context={},
            state={"artifacts": {
                "ANALYSIS_JSON_FILE": str(analysis_path),
                "EXISTING_WORKFLOW_DIR": str(tmp_path / "nonexistent"),
            }},
            step_cfg={},
            project_root=tmp_path,
        )

        assert result.status == "REJECTED"
        assert result.reject_code == "EXISTING_WORKFLOW_NOT_FOUND"
