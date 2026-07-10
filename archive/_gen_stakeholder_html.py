"""Generate the stakeholder site HTML from the approved markdown.

Uses the default theme layout template and weasyprint-compatible CSS.
Includes a custom Compliance Status section sourced from SYSTEM_OVERVIEW.
"""
import re
import json
import os
import markdown
from pathlib import Path
from datetime import datetime

REPO = Path(r"D:\MyProjectSpace\01_Workflows\agent-runner-v2")

# Paths
CONTENT_MD = REPO / "docs" / "site" / "stakeholders" / "content.md"
LAYOUT_TEMPLATE = REPO / "agent_runner_v2" / "bootstrap" / "themes" / "default" / "layout.html"
OUTPUT_HTML = REPO / "docs" / "site" / "stakeholders" / "index.html"
META_DIR = Path(r"C:\Users\kengk\.ukbe-runner\jobs\51_stakeholder_docs_v1\51STAKE-GEN-20260705-009\01_generate_site")


def build_compliance_section() -> str:
    """Build the Compliance Status custom section sourced from SYSTEM_OVERVIEW."""
    return """<section>
<h2 id="compliance-status">Compliance Status</h2>
<p>The platform's compliance posture reflects its current maturity phase and roadmap toward enterprise-grade governance.</p>

<h3>Current Certifications &amp; Posture</h3>
<table>
<thead><tr><th>Area</th><th>Status</th><th>Notes</th></tr></thead>
<tbody>
<tr><td>SOC 2</td><td>Not yet certified</td><td>Execution contract and audit trail design align with SOC 2 Trust Service Criteria; formal audit planned for v1.0</td></tr>
<tr><td>ISO 27001</td><td>Not yet certified</td><td>State persistence, artifact tracking, and role separation provide foundational controls</td></tr>
<tr><td>Internal Audit</td><td>In progress</td><td>Bootstrap workflow generating comprehensive documentation suite for review</td></tr>
</tbody>
</table>

<h3>Audit Status</h3>
<ul>
<li><strong>Documentation Profile</strong>: Currently <code>provisional</code> &mdash; transitioning to <code>explicit</code></li>
<li><strong>Execution Contract</strong>: v2 sidecar-only communication enforced; all results produce verifiable <code>meta.json</code> artifacts</li>
<li><strong>Job State Schema</strong>: Versioned (v2) with migration support; backward compatibility maintained</li>
<li><strong>Review Loop Governance</strong>: Configurable iteration limits; explicit failure classification (retryable vs. fatal)</li>
<li><strong>Artifact Validation</strong>: Declared outputs verified for existence before workflow progression</li>
</ul>

<h3>Compliance Roadmap</h3>
<table>
<thead><tr><th>Phase</th><th>Milestone</th><th>Target</th></tr></thead>
<tbody>
<tr><td>Phase 1 (Current)</td><td>Bootstrap documentation generation; provisional profile</td><td>2026-07-04</td></tr>
<tr><td>Phase 2</td><td>Explicit documentation profile; full governance framework</td><td>Post-bootstrap completion</td></tr>
<tr><td>Phase 3 (v1.0)</td><td>Enterprise compliance features; multi-tenant support; formal audit readiness</td><td>Roadmap</td></tr>
</tbody>
</table>

<p class="muted">Source: SYSTEM_OVERVIEW &mdash; Architecture Profile and Migration Posture sections.</p>
</section>"""


def wrap_sections(html_body: str) -> str:
    """Wrap each h2-headed block in <section> tags for styling."""
    parts = re.split(r'(<h2[^>]*>.*?</h2>)', html_body)
    wrapped = []
    i = 0
    while i < len(parts):
        if re.match(r'<h2', parts[i]):
            heading = parts[i]
            i += 1
            content = ''
            while i < len(parts) and not re.match(r'<h2', parts[i]):
                content += parts[i]
                i += 1
            # If already wrapped in <section>, skip
            if '<section>' not in content[:50]:
                wrapped.append(f'<section>\n{heading}{content}\n</section>')
            else:
                wrapped.append(heading + content)
        else:
            wrapped.append(parts[i])
            i += 1
    return ''.join(wrapped)


CSS = """
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
main section {
  background: var(--panel);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow);
}
main h2 { margin-top: 0; font-size: 1.5rem; color: var(--accent); border-bottom: 2px solid var(--line); padding-bottom: 12px; }
main h3 { margin: 24px 0 12px; font-size: 1.2rem; }
main p { margin: 12px 0; }
main table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}
main th, main td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid var(--line);
}
main th {
  background: var(--panel-2);
  font-weight: 600;
  color: var(--accent);
}
main tr:hover { background: var(--panel-2); }
main ul, main ol { margin: 12px 0; padding-left: 24px; }
main li { margin: 8px 0; }
main code {
  background: var(--panel-2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 0.9em;
}
main pre {
  background: var(--panel-2);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
}
main pre code { background: none; padding: 0; }
.muted { color: var(--muted); }
.footer {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.9rem;
  text-align: center;
}
@page {
  size: A4;
  margin: 20mm 15mm;
}
@media print {
  body { background: white; }
  .wrap { max-width: 100%; padding: 0; }
  .hero { box-shadow: none; break-after: avoid; }
  nav { display: none; }
  main section { box-shadow: none; break-inside: avoid; page-break-inside: avoid; }
  h2, h3 { break-after: avoid; page-break-after: avoid; }
  table { break-inside: avoid; page-break-inside: avoid; }
  .footer { break-before: avoid; }
  a { color: var(--text); text-decoration: none; }
}
"""

NAV_LINKS = (
    '<a href="#executive-summary">Executive Summary</a>'
    '<a href="#business-capabilities">Business Capabilities</a>'
    '<a href="#governance-overview">Governance</a>'
    '<a href="#value-proposition">Value Proposition</a>'
    '<a href="#strategic-intent">Strategic Intent</a>'
    '<a href="#compliance-status">Compliance Status</a>'
)

DOWNLOAD_LINK = '<br><a href="index.pdf">Download PDF</a>'


def main():
    # 1. Read markdown content
    md_text = CONTENT_MD.read_text(encoding="utf-8")

    # Strip YAML frontmatter
    md_text = re.sub(r'^---\n.*?\n---\n', '', md_text, count=1, flags=re.DOTALL)

    # 2. Convert markdown to HTML
    body_html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])

    # 3. Insert Compliance Status section before Summary
    summary_idx = body_html.find('<h2 id="summary">')
    if summary_idx == -1:
        summary_idx = body_html.find('<h2>Summary</h2>')
    if summary_idx == -1:
        summary_idx = len(body_html)

    compliance = build_compliance_section()
    body_html = body_html[:summary_idx] + compliance + '\n' + body_html[summary_idx:]

    # 4. Wrap h2-sections in <section> tags
    body_html = wrap_sections(body_html)

    # 5. Read layout template
    template = LAYOUT_TEMPLATE.read_text(encoding="utf-8")

    # 6. Fill template placeholders
    html_out = template
    html_out = html_out.replace('{{TITLE}}', 'Stakeholder Documentation')
    html_out = html_out.replace('{{SUBTITLE}}', 'Business value, capabilities, and governance overview for decision-makers.')
    html_out = html_out.replace('{{WORKFLOW}}', '51_stakeholder_docs_v1')
    html_out = html_out.replace('{{STEP}}', 'generate_site')
    html_out = html_out.replace('{{NAV_LINKS}}', NAV_LINKS)
    html_out = html_out.replace('{{BODY}}', body_html)
    html_out = html_out.replace('{{CSS}}', CSS)
    html_out = html_out.replace('{{THEME_NAME}}', 'default')
    html_out = html_out.replace('{{DOWNLOAD_LINK}}', DOWNLOAD_LINK)

    # 7. Write HTML output
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(html_out, encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML} ({len(html_out)} bytes)")

    # 8. Write meta.json sidecar
    META_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "schema_version": "v2",
        "coder_result": {
            "status": "APPROVED",
            "remark": "Stakeholder HTML site generated with all content sections and custom Compliance Status section. Weasyprint-compatible layout with default theme applied.",
            "artifacts": {
                "STAKEHOLDER_SITE_INDEX": "docs/site/stakeholders/index.html"
            },
            "recorded_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
    }
    meta_path = META_DIR / "meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote {meta_path}")


if __name__ == "__main__":
    main()
