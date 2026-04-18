import os
import re
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import ResearchState
from utils.llm import get_llm

SYSTEM = """You are an expert research writer.
Synthesize the provided research findings into a well-structured, comprehensive report.

Your report MUST follow this exact markdown structure:

# [Title based on the research question]

## Executive Summary
2-3 sentences capturing the key answer.

## Key Findings
Bullet points of the most important facts, statistics, and insights.

## Detailed Analysis
In-depth discussion organized into clear subsections.

## Sources & References
List all sources with their URLs.

## Conclusion
Final summary and any caveats or limitations.

Write in a professional, objective tone. Include specific numbers, dates, and names.
Do NOT add any preamble — start directly with the # Title."""


def markdown_to_html(md: str) -> str:
    """Convert markdown to simple HTML tags for PDF rendering."""
    html = md

    html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.+)$",  r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.+)$",   r"<h1>\1</h1>", html, flags=re.MULTILINE)
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"^\* (.+)$",  r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"^- (.+)$",   r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)

    lines = html.split("\n")
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("<"):
            result.append(line)
        else:
            result.append(f"<p>{line}</p>")

    return "\n".join(result)


def save_pdf(html_body: str, filepath: str) -> bool:
    """Use reportlab only — works on Windows without extra dependencies."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            leftMargin=20*mm, rightMargin=20*mm,
            topMargin=20*mm, bottomMargin=20*mm,
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "T", parent=styles["Title"],
            fontSize=20, textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=14
        )
        h2_style = ParagraphStyle(
            "H2", parent=styles["Heading2"],
            fontSize=14, textColor=colors.HexColor("#16213e"),
            spaceBefore=16, spaceAfter=6
        )
        h3_style = ParagraphStyle(
            "H3", parent=styles["Heading3"],
            fontSize=12, textColor=colors.HexColor("#0f3460"),
            spaceBefore=10, spaceAfter=4
        )
        body_style = ParagraphStyle(
            "B", parent=styles["Normal"],
            fontSize=10, leading=16, spaceAfter=6
        )
        bullet_style = ParagraphStyle(
            "BL", parent=styles["Normal"],
            fontSize=10, leading=15,
            leftIndent=16, spaceAfter=4
        )

        def strip_tags(text):
            return re.sub(r"<[^>]+>", "", text)

        story = []
        for line in html_body.split("\n"):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 4))
            elif line.startswith("<h1>"):
                story.append(Paragraph(strip_tags(line), title_style))
            elif line.startswith("<h2>"):
                story.append(Paragraph(strip_tags(line), h2_style))
            elif line.startswith("<h3>"):
                story.append(Paragraph(strip_tags(line), h3_style))
            elif "<li>" in line:
                clean = strip_tags(line)
                if clean:
                    story.append(Paragraph(f"• {clean}", bullet_style))
            elif line.startswith("<p>") or line.startswith("<a "):
                clean = strip_tags(line)
                if clean:
                    story.append(Paragraph(clean, body_style))

        doc.build(story)
        return True

    except ImportError:
        print("[Writer] reportlab not found — run: pip install reportlab")
        return False


def write_report(state: ResearchState) -> dict:
    print(f"\n[Writer] Generating final report for: {state.query}")

    findings_text = "\n\n".join(state.raw_findings)

    # Deduplicated sources
    seen_urls = set()
    unique_sources = []
    for s in state.sources:
        if s.url not in seen_urls:
            seen_urls.add(s.url)
            unique_sources.append(s)

    sources_text = "\n".join(
        f"- [{s.title}]({s.url})" for s in unique_sources[:20]
    )

    llm = get_llm(temperature=0.4)
    response = llm.invoke([
        SystemMessage(content=SYSTEM),
        HumanMessage(content=(
            f"Research Question: {state.query}\n\n"
            f"Research Plan (sub-questions addressed):\n"
            + "\n".join(f"  - {q}" for q in state.research_plan)
            + f"\n\nResearch Findings:\n{findings_text}\n\n"
            f"Available Sources:\n{sources_text}"
        )),
    ])

    report = response.content.strip()
    print(f"[Writer] Report generated ({len(report)} chars)")

    output_dir = os.getenv("OUTPUT_DIR", "output")
    os.makedirs(output_dir, exist_ok=True)
    safe_name = "".join(
        c if c.isalnum() or c in " _-" else "_"
        for c in state.query[:50]
    )

    # Save Markdown
    md_path = os.path.join(output_dir, f"{safe_name}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[Writer] Markdown saved → {md_path}")

    # Save PDF
    pdf_path = os.path.join(output_dir, f"{safe_name}.pdf")
    html_body = markdown_to_html(report)
    success = save_pdf(html_body, pdf_path)
    if success:
        print(f"[Writer] PDF saved      → {pdf_path}")

    return {"final_report": report}