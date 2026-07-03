from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .workflow_specs import build_workflow_step_specs


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent workflow-spec",
        description="Export the authoritative local workflow step specifications.",
    )
    p.add_argument("--project-root", default=".", help="Workspace root used to resolve the workflow bundle.")
    p.add_argument("--workflow-name", default="default", help="Workflow bundle name. Defaults to 'default'.")
    p.add_argument("--template-group", required=True, help="Template group to export, e.g. delivery_scaffold_v1")
    p.add_argument("--output", default="", help="Optional JSON output path. Defaults to stdout.")
    args = p.parse_args(argv)

    workspace_root = Path(args.project_root or ".").resolve()
    specs = build_workflow_step_specs(
        template_group=args.template_group,
        workspace_root=workspace_root,
        workflow_name=args.workflow_name or "default",
    )
    payload = {
        "template_group": args.template_group,
        "workflow_name": args.workflow_name or "default",
        "project_root": str(workspace_root),
        "step_count": len(specs),
        "steps": specs,
    }

    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        print(json.dumps({
            "status": "ok",
            "message": "workflow spec exported",
            "template_group": args.template_group,
            "output": str(output_path),
            "step_count": len(specs),
        }, indent=2))
        return 0

    sys.stdout.write(rendered)
    sys.stdout.write("\n")
    return 0
