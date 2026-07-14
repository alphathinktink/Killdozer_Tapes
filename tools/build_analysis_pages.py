from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"

PAGES = [
    {
        "source": "marvin-timeline.md",
        "output": "timeline.html",
        "title": "Steel-Manned Timeline",
        "description": "A best-guess chronological timeline of events according to Marvin Heemeyer's own taped account, intentionally steel-manning his grievance narrative.",
    },
    {
        "source": "marvin-grievances.md",
        "output": "grievances.html",
        "title": "Grievance Map",
        "description": "A structured report of Marvin Heemeyer's grievances as described in the tape transcripts.",
    },
    {
        "source": "marvin-persons-entities.md",
        "output": "persons-entities.html",
        "title": "Persons and Entities",
        "description": "A categorized map of people and entities as Marvin Heemeyer portrays them in the tape transcripts.",
    },
]

REPORT_NOTE = (
    "This is a Codex/ChatGPT-generated analysis report derived from the published tape "
    "transcripts. It is not itself a transcript, not a primary source, and not part of "
    "the archive's core transcript corpus. The timeline intentionally steel-mans Marvin "
    "Heemeyer's grievance narrative where the transcripts leave ordering ambiguity."
)


def inline_markdown(text: str) -> str:
    text = html.escape(text, quote=True)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def split_table_row(line: str) -> list[str]:
    raw = line.strip().strip("|")
    return [cell.strip() for cell in raw.split("|")]


def convert_markdown(markdown: str) -> str:
    lines = markdown.splitlines()
    out: list[str] = []
    i = 0
    paragraph: list[str] = []
    in_list = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            close_list()
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*-+", lines[i + 1].strip()):
            flush_paragraph()
            close_list()
            headers = split_table_row(stripped)
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_table_row(lines[i]))
                i += 1
            out.append('<div class="table-wrap"><table>')
            out.append("<thead><tr>" + "".join(f"<th>{inline_markdown(cell)}</th>" for cell in headers) + "</tr></thead>")
            out.append("<tbody>")
            for row in rows:
                out.append("<tr>" + "".join(f"<td>{inline_markdown(cell)}</td>" for cell in row) + "</tr>")
            out.append("</tbody></table></div>")
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            text = heading.group(2)
            out.append(f"<h{level}>{inline_markdown(text)}</h{level}>")
            i += 1
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline_markdown(stripped[2:])}</li>")
            i += 1
            continue

        paragraph.append(stripped)
        i += 1

    flush_paragraph()
    close_list()
    return "\n".join(out)


def page_template(title: str, description: str, body: str, source_md: str) -> str:
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Report",
        "name": f"Killdozer Tapes Analysis - {title}",
        "description": description,
        "isBasedOn": source_md,
        "creator": "Codex/ChatGPT with alphathinktink",
        "about": "Generated analysis of the Killdozer tape transcripts; not a transcript or primary source.",
    }
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Killdozer Tapes Analysis - {html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="alternate icon" href="../favicon.ico">
  <link rel="stylesheet" href="../styles.css">
  <script type="application/ld+json">{html.escape(json.dumps(json_ld, ensure_ascii=False), quote=False)}</script>
</head>
<body class="transcript-page analysis-page">
  <main class="transcript-document provenance-document analysis-document">
    <nav class="crumbs"><a href="../index.html">Archive index</a> / <a href="index.html">Analysis index</a></nav>
    <aside class="analysis-warning" aria-label="Analysis report notice">
      <strong>Analysis report, not transcript:</strong> {html.escape(REPORT_NOTE)}
    </aside>
    <div class="resource-row analysis-nav" aria-label="Analysis report navigation">
      <a href="index.html">Analysis index</a>
      <a href="timeline.html">Timeline</a>
      <a href="grievances.html">Grievances</a>
      <a href="persons-entities.html">Persons and entities</a>
      <a href="{html.escape(source_md)}">Source Markdown</a>
    </div>
    {body}
  </main>
</body>
</html>
"""


def index_page() -> str:
    json_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Killdozer Tapes Analysis Reports",
        "description": "Separate Codex/ChatGPT-generated analysis reports based on the Killdozer tape transcripts.",
        "creator": "Codex/ChatGPT with alphathinktink",
        "hasPart": [page["output"] for page in PAGES],
    }
    cards = "\n".join(
        f"""<article class="analysis-card">
        <p class="eyebrow">Report</p>
        <h2><a href="{page['output']}">{html.escape(page['title'])}</a></h2>
        <p>{html.escape(page['description'])}</p>
        <p><a href="{page['source']}">Source Markdown</a></p>
      </article>"""
        for page in PAGES
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Killdozer Tapes - Analysis Reports</title>
  <meta name="description" content="Separate Codex/ChatGPT-generated analysis reports based on the Killdozer tape transcripts.">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="alternate icon" href="../favicon.ico">
  <link rel="stylesheet" href="../styles.css">
  <script type="application/ld+json">{html.escape(json.dumps(json_ld, ensure_ascii=False), quote=False)}</script>
</head>
<body class="transcript-page analysis-page">
  <main class="transcript-document provenance-document analysis-document">
    <nav class="crumbs"><a href="../index.html">Archive index</a></nav>
    <header>
      <p class="eyebrow">Separate analysis section</p>
      <h1>Analysis Reports</h1>
      <p class="lede">These pages are generated reports about the transcript content. They are intentionally separated from the tape player, transcript pages, source text files, caption files, and provenance page.</p>
    </header>
    <aside class="analysis-warning" aria-label="Analysis report notice">
      <strong>Analysis report, not transcript:</strong> {html.escape(REPORT_NOTE)}
    </aside>
    <section>
      <h2>Available Reports</h2>
      <div class="analysis-card-grid">
        {cards}
      </div>
    </section>
    <section>
      <h2>Use Note</h2>
      <p>Use these pages as interpretive aids only. When quoting or citing the tapes, return to the transcript pages and preferably verify against the audio. These reports summarize and organize Marvin's account; they do not independently validate the allegations described in that account.</p>
      <p>Generation disclosure: the report Markdown and these web pages were generated with Codex/ChatGPT assistance at the request of alphathinktink.</p>
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    for page in PAGES:
        source = ANALYSIS / page["source"]
        body = convert_markdown(source.read_text(encoding="utf-8"))
        (ANALYSIS / page["output"]).write_text(
            page_template(page["title"], page["description"], body, page["source"]),
            encoding="utf-8",
            newline="\n",
        )
    (ANALYSIS / "index.html").write_text(index_page(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
