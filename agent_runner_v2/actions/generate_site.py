#!/usr/bin/env python3
from __future__ import annotations

"""
actions/generate_site.py - Convert markdown to HTML and optionally PDF.

This action reads the approved markdown content and generates:
- HTML page using markdown conversion and shared styling
- PDF page (if configured and weasyprint is available)
- manifest.json

The output format is determined by the OUTPUT_FORMAT context variable,
which comes from sites.config in the target repo.
"""

import json
from pathlib import Path

import markdown

from ..action_result import ActionResult
from ..constants import AUDIENCE_SITE_WORKFLOWS
from ..runtime_context import resolve_step_meta_rel, write_meta_sidecar
from ..site_styles import COMMON_CSS, page_shell, manifest_json as generate_manifest


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _markdown_to_html(md_content: str) -> str:
    """Convert markdown to HTML using Python markdown library."""
    return markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "codehilite", "toc"],
    )


def _generate_pdf(html_content: str, pdf_path: Path) -> bool:
    """Convert HTML to PDF using weasyprint. Returns True on success."""
    try:
        from weasyprint import HTML
        HTML(string=html_content).write_pdf(str(pdf_path))
        return True
    except ImportError:
        print("[generate_site] weasyprint not installed, skipping PDF generation", flush=True)
        return False
    except Exception as exc:
        print(f"[generate_site] PDF generation failed: {exc}", flush=True)
        return False


def generate_site(*, context: dict[str, str], state: dict, step_cfg: dict, project_root: Path) -> ActionResult:
    """Convert approved markdown to HTML and optionally PDF.

    Reads:
    - Markdown content from the site directory
    - OUTPUT_FORMAT from context (html, pdf, or html+pdf)

    Writes:
    - index.html (if output_format includes html)
    - index.pdf (if output_format includes pdf and weasyprint is available)
    - manifest.json
    """
    template_group = str(state.get("template_group") or "")
    job_id = str(state.get("job_id") or "")
    step = str(state.get("current_step") or "generate_site")
    output_format = str(context.get("OUTPUT_FORMAT") or "html").lower()
    meta_rel = resolve_step_meta_rel(
        context=context,
        state=state,
        context_key="SITE_MANIFEST_METAJSON",
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

    markdown_path = project_root / paths["markdown_rel"]
    html_path = project_root / paths["html_rel"]
    pdf_path = project_root / paths["pdf_rel"]
    manifest_path = project_root / paths["manifest_rel"]

    # Read markdown content
    if not markdown_path.exists():
        result = ActionResult(
            status="REJECTED",
            remark=f"Markdown source not found: {paths['markdown_rel']}",
            artifacts={},
            reject_code="MARKDOWN_NOT_FOUND",
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

    md_content = markdown_path.read_text(encoding="utf-8")

    # Convert markdown to HTML body
    html_body = _markdown_to_html(md_content)

    # Build navigation links
    nav_links = [
        ("../index.html", "Home"),
    ]
    if output_format != "pdf":
        nav_links.append(("index.html", "HTML"))
    if output_format != "html" and pdf_path.exists():
        nav_links.append(("index.pdf", "PDF"))

    # Generate full HTML page
    html_content = page_shell(
        title=paths["title"],
        subtitle=paths["subtitle"],
        workflow=template_group,
        step=step,
        nav_links=nav_links,
        body=html_body,
        site_comment=f"<!-- Generated from {paths['markdown_rel']} -->\n",
    )

    artifacts = {}
    generated_files = []

    # Write HTML if configured
    if output_format in ("html", "html+pdf"):
        _write_text(html_path, html_content)
        artifacts["SITE_INDEX"] = paths["html_rel"]
        generated_files.append(paths["html_rel"])

    # Write PDF if configured
    if output_format in ("pdf", "html+pdf"):
        pdf_success = _generate_pdf(html_content, pdf_path)
        if pdf_success:
            artifacts["SITE_PDF"] = paths["pdf_rel"]
            generated_files.append(paths["pdf_rel"])
        elif output_format == "pdf":
            result = ActionResult(
                status="REJECTED",
                remark="PDF generation failed: weasyprint not available or conversion error",
                artifacts={},
                reject_code="PDF_GENERATION_FAILED",
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

    # Generate manifest
    pages = {}
    if output_format in ("html", "html+pdf"):
        pages[paths["html_rel"]] = paths["title"]
    if output_format in ("pdf", "html+pdf") and pdf_path.exists():
        pages[paths["pdf_rel"]] = f"{paths['title']} (PDF)"
    pages[paths["manifest_rel"]] = "Manifest"

    manifest_content = generate_manifest(
        workflow=template_group,
        step=step,
        pages=pages,
        index_path=paths["html_rel"] if output_format in ("html", "html+pdf") else paths["pdf_rel"],
    )
    _write_text(manifest_path, manifest_content)
    artifacts["SITE_MANIFEST"] = paths["manifest_rel"]
    generated_files.append(paths["manifest_rel"])

    # Write meta sidecar
    if meta_rel:
        write_meta_sidecar(
            meta_rel,
            project_root=project_root,
            status="APPROVED",
            remark=f"Generated {', '.join(generated_files)} from {paths['markdown_rel']}",
            artifacts=artifacts,
        )

    return ActionResult(
        status="APPROVED",
        remark=f"Generated {', '.join(generated_files)} from {paths['markdown_rel']} (output_format={output_format})",
        artifacts=artifacts,
    )
