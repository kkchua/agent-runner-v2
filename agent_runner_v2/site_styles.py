from __future__ import annotations

"""
site_styles.py - Shared HTML/CSS framework for audience-specific documentation sites.

Provides common styling, page shell, navigation, and helper functions for generating
consistent HTML documentation sites for different audiences (stakeholders, developers,
operators, testers, users).
"""

from html import escape
from pathlib import Path
from typing import Any


# Common CSS for all audience sites
COMMON_CSS = """
:root {
  color-scheme: light;
  --bg: #f8fafc;
  --panel: #ffffff;
  --panel-2: #f1f5f9;
  --text: #1e293b;
  --muted: #64748b;
  --accent: #2563eb;
  --accent-2: #059669;
  --line: rgba(100, 116, 139, 0.2);
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
.wrap { max-width: 1200px; margin: 0 auto; padding: 32px 20px 56px; }
.hero {
  background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
  color: white;
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 32px;
  box-shadow: var(--shadow);
}
.hero h1 { margin: 0 0 12px; font-size: 2.5rem; font-weight: 700; }
.hero .subtitle { font-size: 1.2rem; opacity: 0.9; }
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.75rem;
  font-weight: 600;
  opacity: 0.8;
  margin-bottom: 8px;
}
nav {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 32px;
  padding: 16px;
  background: var(--panel);
  border-radius: 12px;
  box-shadow: var(--shadow);
}
nav a {
  color: var(--text);
  text-decoration: none;
  padding: 10px 16px;
  border-radius: 8px;
  background: var(--panel-2);
  font-weight: 500;
  transition: all 0.2s;
}
nav a:hover {
  background: var(--accent);
  color: white;
}
section {
  background: var(--panel);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow);
}
h2 { margin-top: 0; font-size: 1.5rem; color: var(--accent); border-bottom: 2px solid var(--line); padding-bottom: 12px; }
h3 { margin: 24px 0 12px; font-size: 1.2rem; }
p { margin: 12px 0; }
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 20px 0;
}
.card {
  background: var(--panel-2);
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid var(--accent);
}
.card h3 { margin: 0 0 8px; font-size: 1.1rem; }
.card p { margin: 0; color: var(--muted); }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}
th, td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--line);
}
th {
  background: var(--panel-2);
  font-weight: 600;
  color: var(--accent);
}
tr:hover { background: var(--panel-2); }
ul, ol { margin: 12px 0; padding-left: 24px; }
li { margin: 8px 0; }
code {
  background: var(--panel-2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.9em;
}
pre {
  background: var(--panel-2);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}
pre code { background: none; padding: 0; }
.muted { color: var(--muted); }
.footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.9rem;
  text-align: center;
}
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  background: var(--accent);
  color: white;
}
.badge.secondary { background: var(--accent-2); }

/* Print styles for PDF generation */
@media print {
  body { background: white; }
  .wrap { max-width: 100%; padding: 0; }
  .hero { box-shadow: none; break-after: avoid; }
  nav { display: none; }
  section { box-shadow: none; break-inside: avoid; page-break-inside: avoid; }
  h2, h3 { break-after: avoid; page-break-after: avoid; }
  table { break-inside: avoid; page-break-inside: avoid; }
  .footer { break-before: avoid; }
  a { color: var(--text); text-decoration: none; }
}
"""


def page_shell(
    *,
    title: str,
    subtitle: str,
    workflow: str,
    step: str,
    nav_links: list[tuple[str, str]],
    body: str,
    site_comment: str = "",
) -> str:
    """Generate a complete HTML page with common styling.

    Args:
        title: Page title
        subtitle: Page subtitle/description
        workflow: Workflow name for metadata
        step: Step name for metadata
        nav_links: List of (url, label) tuples for navigation
        body: Main content HTML
        site_comment: Optional HTML comment for the page

    Returns:
        Complete HTML document string
    """
    nav_html = "\n    ".join(
        f'<a href="{escape(url)}">{escape(label)}</a>'
        for url, label in nav_links
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <style>{COMMON_CSS}</style>
</head>
<body>
{site_comment}<div class="wrap">
  <div class="hero">
    <div class="eyebrow">{escape(workflow)}</div>
    <h1>{escape(title)}</h1>
    <p class="subtitle">{escape(subtitle)}</p>
  </div>
  <nav>
    {nav_html}
  </nav>
  <main>
    {body}
  </main>
  <div class="footer">
    Generated by {escape(workflow)} / {escape(step)}. Markdown remains the source of truth.
  </div>
</div>
</body>
</html>
"""


def card(title: str, text: str, link: str | None = None) -> str:
    """Generate a styled card element.

    Args:
        title: Card title
        text: Card description
        link: Optional link URL

    Returns:
        HTML string for the card
    """
    title_html = f'<a href="{escape(link)}" style="color: inherit; text-decoration: none;">{escape(title)}</a>' if link else escape(title)
    return f'<div class="card"><h3>{title_html}</h3><p>{escape(text)}</p></div>'


def table(headers: list[str], rows: list[list[str]]) -> str:
    """Generate a styled HTML table.

    Args:
        headers: Column headers
        rows: Table rows (list of lists)

    Returns:
        HTML string for the table
    """
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body_rows = []
    for row in rows:
        body_rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def section(title: str, content: str) -> str:
    """Generate a styled section element.

    Args:
        title: Section title
        content: Section content HTML

    Returns:
        HTML string for the section
    """
    return f'<section><h2>{escape(title)}</h2>{content}</section>'


def manifest_json(
    *,
    workflow: str,
    step: str,
    pages: dict[str, str],
    index_path: str,
) -> str:
    """Generate manifest.json content for a site.

    Args:
        workflow: Workflow name
        step: Step name
        pages: Dict mapping page paths to titles
        index_path: Path to the index page

    Returns:
        JSON string for the manifest
    """
    import json
    from datetime import datetime

    return json.dumps({
        "workflow": workflow,
        "step": step,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "pages": [{"path": path, "title": title} for path, title in pages.items()],
        "index": index_path,
    }, indent=2)
