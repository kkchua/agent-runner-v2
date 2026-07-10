from __future__ import annotations

"""
architecture_site.py - Master index/navigation site generator.

This module generates the master documentation hub index that links to all
audience-specific documentation sites (stakeholders, developers, operators,
testers, users).
"""

from html import escape
from pathlib import Path
from typing import Any

from .constants import ARCHITECTURE_AUDIENCE_SITES
from .doc_paths import docs_site_rel
from .site_styles import page_shell, card, section, manifest_json


# Master site pages
SITE_PAGES = {
    docs_site_rel("index.html"): "Documentation Hub",
}

AUDIENCE_SITES = ARCHITECTURE_AUDIENCE_SITES


def _workflow_name(snapshot: dict[str, Any]) -> str:
    return str(snapshot.get("workflow_name") or snapshot.get("mode") or "architecture_site")


def _site_comment(workflow: str, step: str) -> str:
    return f"<!-- Managed by workflow: {workflow} / step: {step} -->\n"


def render_master_index(snapshot: dict[str, Any], project_root: Path) -> dict[str, str]:
    """Generate the master index/navigation page.

    Args:
        snapshot: Build snapshot (unused for master index, kept for API consistency)
        project_root: Repository root path

    Returns:
        Dict mapping relative paths to HTML content
    """
    workflow = _workflow_name(snapshot)
    project_name = project_root.name or "Repository"
    page_paths: dict[str, str] = {}

    # Build navigation links for the header
    nav_links = [(f"{site['path']}index.html", site["name"].split()[0]) for site in AUDIENCE_SITES]

    # Build audience site cards
    audience_cards = "\n".join(
        card(
            title=site["name"],
            text=f"**For {site['audience']}**: {site['description']}",
            link=f"{site['path']}index.html",
        )
        for site in AUDIENCE_SITES
    )

    # Build overview section
    overview_body = f"""
<section>
  <h2>Documentation Hub</h2>
  <p>Welcome to the {escape(project_name)} documentation hub. This site provides comprehensive documentation tailored to different audiences.</p>
  <p>Select the documentation that matches your role:</p>
  <div class="grid">
    {audience_cards}
  </div>
</section>
<section>
  <h2>Quick Reference</h2>
  <table>
    <thead>
      <tr>
        <th>Audience</th>
        <th>What You'll Find</th>
        <th>Link</th>
      </tr>
    </thead>
    <tbody>
      {''.join(f'''<tr>
        <td><strong>{escape(site['audience'])}</strong></td>
        <td>{', '.join(escape(c) for c in site['content'][:3])}...</td>
        <td><a href="{escape(site['path'])}index.html">View</a></td>
      </tr>''' for site in AUDIENCE_SITES)}
    </tbody>
  </table>
</section>
<section>
  <h2>Documentation Workflows</h2>
  <p>This documentation is generated and maintained by the following workflows:</p>
  <ul>
    <li><code>00_master_docs_bootstrap_v1</code> — Initial documentation bootstrap</li>
    <li><code>40_documentation_sync_v1</code> — Ongoing documentation synchronization</li>
    <li><code>50_architecture_site_v1</code> — This master index</li>
    <li><code>51_stakeholder_docs_v1</code> — Stakeholder documentation site</li>
    <li><code>52_developer_docs_v1</code> — Developer documentation site</li>
    <li><code>53_operator_docs_v1</code> — Operator documentation site</li>
    <li><code>54_tester_docs_v1</code> — Tester documentation site</li>
    <li><code>55_user_docs_v1</code> — User documentation site</li>
  </ul>
</section>
"""

    # Generate the master index page
    index_html = page_shell(
        title=f"{project_name} Documentation Hub",
        subtitle=f"Comprehensive documentation for {project_name} tailored to different audiences.",
        workflow=workflow,
        step=str(snapshot.get("step") or "build_site"),
        nav_links=[("index.html", "Home")] + nav_links,
        body=overview_body,
        site_comment=_site_comment(workflow, str(snapshot.get("step") or "build_site")),
    )

    page_paths[docs_site_rel("index.html")] = index_html

    # Generate manifest
    manifest = manifest_json(
        workflow=workflow,
        step=str(snapshot.get("step") or "build_site"),
        pages=SITE_PAGES,
        index_path=docs_site_rel("index.html"),
    )
    page_paths[docs_site_rel("manifest.json")] = manifest

    return page_paths


def render_architecture_site(snapshot: dict[str, Any], project_root: Path) -> dict[str, str]:
    """Legacy function - now delegates to render_master_index.

    Kept for backward compatibility with existing actions.
    """
    return render_master_index(snapshot, project_root)
