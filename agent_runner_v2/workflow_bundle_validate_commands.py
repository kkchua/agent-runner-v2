from __future__ import annotations

import argparse
import json
from pathlib import Path

from .workflow_bundle_validator import (
    DEFAULT_BOOTSTRAP_WORKFLOWS_ROOT,
    validate_named_workflow_bundles,
)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ukbe-run-agent validate-workflow-bundle",
        description="Validate one or more workflow bundles locally before publish or backend sync.",
    )
    p.add_argument(
        "workflow_names",
        nargs="*",
        help="Workflow bundle names to validate. If omitted, validates all bundles under the workflows root.",
    )
    p.add_argument(
        "--workflows-root",
        default=str(DEFAULT_BOOTSTRAP_WORKFLOWS_ROOT),
        help="Root directory containing workflow bundles. Defaults to bootstrap/workflows/default.",
    )
    p.add_argument(
        "--output",
        default="",
        help="Optional JSON report output path.",
    )
    args = p.parse_args(argv)

    workflows_root = Path(args.workflows_root).resolve()
    reports = validate_named_workflow_bundles(
        workflows_root=workflows_root,
        workflow_names=list(args.workflow_names or []),
    )

    payload = {
        "status": "ok" if all(report.valid for report in reports) else "error",
        "workflows_root": str(workflows_root),
        "validated_count": len(reports),
        "invalid_count": sum(1 for report in reports if not report.valid),
        "reports": [report.to_dict() for report in reports],
    }

    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")

    print(rendered)
    return 0 if payload["status"] == "ok" else 1
