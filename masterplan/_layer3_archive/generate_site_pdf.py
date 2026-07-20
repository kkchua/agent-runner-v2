#!/usr/bin/env python3
from __future__ import annotations

"""
actions/generate_site_pdf.py - Convert HTML to PDF using weasyprint.

This action is used as a post_action for LLM_Action steps. After the LLM
generates the HTML, this action converts it to PDF if configured.
"""

import platform
from pathlib import Path

from ..action_result import ActionResult
from ..constants import AUDIENCE_SITE_WORKFLOWS
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar


def _get_install_instructions() -> str:
    """Generate platform-specific installation instructions for weasyprint."""
    system = platform.system()

    instructions = [
        "To enable PDF generation, follow these steps:",
        "",
    ]

    if system == "Windows":
        instructions.extend([
            "1. Install GTK3 Runtime (required for weasyprint on Windows):",
            "   Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases",
            "   Install the latest gtk3-runtime-*.exe",
            "   Restart your terminal/command prompt after installation",
            "",
            "2. Install weasyprint:",
            "   pip install weasyprint",
            "",
            "3. Verify installation:",
            "   python -c \"import weasyprint; print('weasyprint OK')\"",
        ])
    elif system == "Darwin":  # macOS
        instructions.extend([
            "1. Install system dependencies:",
            "   brew install pango libffi",
            "",
            "2. Install weasyprint:",
            "   pip install weasyprint",
            "",
            "3. Verify installation:",
            "   python -c \"import weasyprint; print('weasyprint OK')\"",
        ])
    else:  # Linux and others
        instructions.extend([
            "1. Install system dependencies:",
            "   Ubuntu/Debian: sudo apt-get install libpango1.0-dev libffi-dev",
            "   Fedora: sudo dnf install pango libffi-devel",
            "   Arch: sudo pacman -S pango libffi",
            "",
            "2. Install weasyprint:",
            "   pip install weasyprint",
            "",
            "3. Verify installation:",
            "   python -c \"import weasyprint; print('weasyprint OK')\"",
        ])

    return "\n".join(instructions)


def generate_site_pdf(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    """Convert HTML to PDF using weasyprint.

    This action is called as a post_action after the LLM generates HTML.
    It reads the HTML file and converts it to PDF if configured.

    Reads:
    - HTML file from the site directory
    - OUTPUT_FORMAT from context (only generates PDF if format includes pdf)

    Writes:
    - index.pdf (if output_format includes pdf and weasyprint is available)
    """
    template_group = str(state.get("template_group") or "")
    step = str(state.get("current_step") or "generate_site_pdf")
    output_format = str(context.get("OUTPUT_FORMAT") or "html").lower()
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="SITE_PDF_METAJSON",
        default_step=step,
    )

    # Get audience-specific paths
    paths = AUDIENCE_SITE_WORKFLOWS.get(template_group)
    if not paths:
        result = ActionResult(
            status="REJECTED",
            remark=f"Unknown template group: {template_group}",
            artifacts={},
            reject_code="UNKNOWN_TEMPLATE_GROUP",
        )
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="REJECTED",
                remark=result.remark,
                artifacts={},
            )
        return result

    html_path = project_root / paths["html_rel"]
    pdf_path = project_root / paths["pdf_rel"]

    # Check if PDF generation is needed
    if output_format not in ("pdf", "html+pdf"):
        # PDF not configured, skip
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="APPROVED",
                remark=f"PDF generation skipped (output_format={output_format})",
                artifacts={},
            )
        return ActionResult(
            status="APPROVED",
            remark=f"PDF generation skipped (output_format={output_format})",
            artifacts={},
        )

    # Check if HTML exists
    if not html_path.exists():
        result = ActionResult(
            status="REJECTED",
            remark=f"HTML source not found: {paths['html_rel']}",
            artifacts={},
            reject_code="HTML_NOT_FOUND",
        )
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="REJECTED",
                remark=result.remark,
                artifacts={},
            )
        return result

    # Convert HTML to PDF using weasyprint
    try:
        from weasyprint import HTML
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
    except ImportError:
        # weasyprint not installed - skip with warning, don't fail
        instructions = _get_install_instructions()
        print("[generate_site_pdf] weasyprint not installed, skipping PDF generation", flush=True)
        print("", flush=True)
        print(instructions, flush=True)
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="APPROVED",
                remark="PDF generation skipped: weasyprint not installed. HTML site generated successfully.",
                artifacts={},
            )
        return ActionResult(
            status="APPROVED",
            remark="PDF generation skipped: weasyprint not installed. HTML site generated successfully.",
            artifacts={},
        )
    except Exception as exc:
        # PDF conversion failed - this is a warning, not a failure
        print(f"[generate_site_pdf] PDF conversion failed: {exc}", flush=True)
        print("[generate_site_pdf] HTML site was generated successfully", flush=True)
        if meta_rel:
            write_meta_sidecar(
                meta_rel,
                project_root=project_root,
                status="APPROVED",
                remark=f"PDF generation skipped: {exc}. HTML site generated successfully.",
                artifacts={},
            )
        return ActionResult(
            status="APPROVED",
            remark=f"PDF generation skipped: {exc}. HTML site generated successfully.",
            artifacts={},
        )

    # Write meta sidecar
    artifacts = {"SITE_PDF": paths["pdf_rel"]}
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"Generated {paths['pdf_rel']} from {paths['html_rel']}",
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Generated {paths['pdf_rel']} from {paths['html_rel']}",
        artifacts=artifacts,
    )
