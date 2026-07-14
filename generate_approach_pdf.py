from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics import renderPDF
import os

OUT = "/home/claude/volopay-intel/Volopay_Task2_Approach_Document.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="H1c", parent=styles["Heading1"], textColor=colors.HexColor("#1e293b"), spaceAfter=10))
styles.add(ParagraphStyle(name="H2c", parent=styles["Heading2"], textColor=colors.HexColor("#3b82f6"), spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle(name="Bodyc", parent=styles["BodyText"], leading=15, spaceAfter=8))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontSize=9, textColor=colors.HexColor("#555555")))
mono = ParagraphStyle(name="Mono", fontName="Courier", fontSize=8.5, leading=11, textColor=colors.HexColor("#1e293b"))

story = []

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
story.append(Paragraph("AI-Powered Customer Intelligence Platform", styles["Title"]))
story.append(Paragraph("Approach Document — Volopay Growth Squad Assessment, Task 2", styles["Small"]))
story.append(Spacer(1, 16))

# ---------------------------------------------------------------------------
# Problem Statement
# ---------------------------------------------------------------------------
story.append(Paragraph("Problem Statement", styles["H2c"]))
story.append(Paragraph(
    "Customer context at a growing company lives in at least five different places: the CRM (contract, plan, "
    "MRR), support tickets (product friction), email threads (explicit customer sentiment), Slack (what the "
    "account team already knows but hasn't escalated), and product usage data (behavior, which is often the "
    "leading indicator everyone reacts to last). Sales, CS, and Partnerships teams end up manually stitching "
    "these together before every important customer conversation, or worse, not stitching them together at all "
    "and missing patterns that only show up when multiple weak signals from different systems line up.",
    styles["Bodyc"]))

# ---------------------------------------------------------------------------
# Solution Approach
# ---------------------------------------------------------------------------
story.append(Paragraph("Solution Approach", styles["H2c"]))
story.append(Paragraph(
    "A single Streamlit application that ingests data from 5 sources, joins it by customer_id, and runs it "
    "through a transparent, rule-based scoring engine to produce a health score, risk list, opportunity list, "
    "and a recommended next best action — each with explicit reasoning traceable back to specific evidence. "
    "An AI layer (Claude) sits on top purely for natural-language summarization, not for scoring. This split was "
    "deliberate: the parts of the tool that drive action (score, risk severity, recommended action) are rule-based "
    "and auditable, so a CSM can see exactly why an account is flagged and trust or override it. The part that "
    "benefits from language generation (a readable summary paragraph) is the only part handed to an LLM, and even "
    "that degrades gracefully to a template summary if no API key is available, so the tool never breaks due to "
    "missing credentials.",
    styles["Bodyc"]))

# ---------------------------------------------------------------------------
# Architecture Diagram
# ---------------------------------------------------------------------------
story.append(Paragraph("Architecture & Workflow", styles["H2c"]))

d = Drawing(480, 400)

def box(x, y, w, h, label, fill="#eff6ff", stroke="#3b82f6", fontsize=8.5):
    d.add(Rect(x, y, w, h, fillColor=colors.HexColor(fill), strokeColor=colors.HexColor(stroke), strokeWidth=1, rx=6, ry=6))
    lines = label.split("\n")
    for i, line in enumerate(lines):
        d.add(String(x + w / 2, y + h / 2 - (len(lines) - 1) * 5 + (len(lines) - 1 - i) * 10 - 3,
                      line, textAnchor="middle", fontSize=fontsize, fontName="Helvetica"))

def arrow(x1, y1, x2, y2):
    d.add(Line(x1, y1, x2, y2, strokeColor=colors.HexColor("#94a3b8"), strokeWidth=1.3))
    d.add(Line(x2, y2, x2 - 4, y2 + 4, strokeColor=colors.HexColor("#94a3b8"), strokeWidth=1.3))
    d.add(Line(x2, y2, x2 - 4, y2 - 4, strokeColor=colors.HexColor("#94a3b8"), strokeWidth=1.3))

# Row 1: 5 source boxes
sources = ["CRM\n(Zoho-style)", "Support\nTickets", "Emails", "Slack\nNotes", "Product\nUsage"]
sx = 10
for s in sources:
    box(sx, 340, 82, 40, s, fill="#f8fafc", stroke="#94a3b8")
    arrow(sx + 41, 340, sx + 41, 305)
    sx += 92

# Row 2: Data loader
box(120, 270, 240, 35, "Data Loader - joins all sources by customer_id", fill="#eff6ff")
arrow(240, 270, 240, 240)

# Row 3: Intelligence engine
box(60, 195, 360, 45, "Intelligence Engine (rule-based, auditable)\nHealth Score . Risks . Opportunities . Next Best Action", fill="#eff6ff")
arrow(240, 195, 145, 165)
arrow(240, 195, 335, 165)

# Row 4: Summary generation branch
box(60, 130, 170, 35, "Template Summary\n(no API key needed)", fill="#f0fdf4", stroke="#12b76a")
box(250, 130, 170, 35, "Claude API\n(if key provided)", fill="#fff7ed", stroke="#f5a623")
arrow(145, 130, 220, 90)
arrow(335, 130, 260, 90)

# Row 5: UI
box(120, 55, 240, 35, "Streamlit UI - profile, score, risks,\nopportunities, timeline, next action", fill="#eef2ff", stroke="#6366f1")

story.append(d)
story.append(Paragraph(
    "Data flow: five JSON sources → joined into one per-customer record by the data loader → rule-based "
    "intelligence engine computes score/risks/opportunities/next action → summary layer generates prose (Claude "
    "if a key is present, otherwise a deterministic template) → Streamlit renders the unified customer view.",
    styles["Small"]))

story.append(PageBreak())

# ---------------------------------------------------------------------------
# Tools, tech, AI model, prompt engineering
# ---------------------------------------------------------------------------
story.append(Paragraph("Tools, Technologies & AI Model", styles["H2c"]))
tech_table_data = [
    ["Layer", "Choice", "Reasoning"],
    ["UI / App framework", "Streamlit", "Fastest path to a deployable internal tool; no frontend build needed"],
    ["Scoring logic", "Python, rule-based", "Explainable and auditable — CSMs need to trust and override scores"],
    ["AI Model", "Claude (claude-sonnet-4-6) via Anthropic API", "Used only for summarization, not classification/scoring"],
    ["Data layer", "Static JSON (dummy)", "Swappable for live CRM/Slack/email APIs without touching engine logic"],
    ["Deployment", "Streamlit Community Cloud", "Free, public URL, GitHub-based, no infra to manage"],
]
t = Table(tech_table_data, colWidths=[110, 160, 210])
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 8.5),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(Spacer(1, 12))

story.append(Paragraph("Prompt used for AI Summary (when Claude key is provided):", styles["Bodyc"]))
prompt_text = (
    "You are a customer success analyst. Write a concise 3-4 sentence account summary for an internal "
    "CSM/sales dashboard. Be direct and specific, no filler, no marketing tone.<br/><br/>"
    "Company: {company}<br/>Health score: {score}/100 ({label})<br/>"
    "Seat utilization: {active} active of licensed seats<br/>Usage trend (30d): {trend}%<br/><br/>"
    "Risks:<br/>{risk_list}<br/><br/>Opportunities:<br/>{opp_list}<br/><br/>"
    "Write the summary now, plain prose, no headers or bullet points."
)
story.append(Paragraph(prompt_text, mono))
story.append(Paragraph(
    "Design choice: the prompt explicitly bans marketing tone and requires plain prose, because the target "
    "reader is an internal CSM skimming 15 accounts before a pipeline review, not an external audience.",
    styles["Small"]))

# ---------------------------------------------------------------------------
# Dummy data
# ---------------------------------------------------------------------------
story.append(Paragraph("Dummy Dataset", styles["H2c"]))
story.append(Paragraph(
    "6 customer accounts across Logistics, Media, F&B/Retail, Healthcare, and SaaS industries, each with "
    "linked records across all 5 sources: CRM (plan, MRR, seats, contract dates), 10 support tickets, "
    "7 email threads, 6 Slack CSM notes, and product usage snapshots. Data is intentionally varied — some "
    "accounts healthy, some critical, some with pure expansion signals — so the scoring logic can be verified "
    "against ground truth rather than tuned to a single happy-path scenario.",
    styles["Bodyc"]))

# ---------------------------------------------------------------------------
# Sample input/output
# ---------------------------------------------------------------------------
story.append(Paragraph("Sample Input & Output", styles["H2c"]))
story.append(Paragraph("<b>Input</b> (Northwind Logistics, excerpted):", styles["Bodyc"]))
sample_in = (
    "CRM: Scale plan, 60 seats licensed / 34 active, renewal in ~6 months, stage \"Renewal Risk\"<br/>"
    "Support: 1 open High-priority ticket — \"Card decline errors during batch payouts\"<br/>"
    "Email: \"We're evaluating two other vendors before renewal.\"<br/>"
    "Slack (CSM note): \"Renewal is in 6 months and they're already shopping around.\"<br/>"
    "Usage: -18% trend over 30 days"
)
story.append(Paragraph(sample_in, mono))
story.append(Spacer(1, 8))
story.append(Paragraph("<b>Output</b>:", styles["Bodyc"]))
sample_out = (
    "Health Score: 14/100 — Critical<br/>"
    "Risks (3): unresolved high-priority support ticket · negative-sentiment renewal email · "
    "declining usage trend<br/>"
    "Opportunities: none this cycle<br/>"
    "Recommended Next Best Action (Urgent): Escalate to CSM lead + trigger save play — schedule an "
    "executive check-in within 3 business days<br/>"
    "Reasoning: 2+ concurrent high-severity signals (support + relationship + renewal proximity) — "
    "accounts with this pattern historically churn at a materially higher rate if not intercepted within a week."
)
story.append(Paragraph(sample_out, mono))

# ---------------------------------------------------------------------------
# Improvement / Security / Scalability / Error handling
# ---------------------------------------------------------------------------
story.append(Paragraph("One Improvement With More Development Time", styles["H2c"]))
story.append(Paragraph(
    "Add a feedback loop where CSMs mark each recommendation as \"actioned\" or \"not relevant,\" and use that "
    "signal to tune scoring thresholds per industry/segment. Right now a 5-person SaaS account and a 140-seat "
    "enterprise account are graded on the same usage-trend curve, which is the biggest simplification in this "
    "prototype — a -15% usage dip means something very different for those two accounts.",
    styles["Bodyc"]))

story.append(Paragraph("Security, Scalability & Error Handling (see also README)", styles["H2c"]))
story.append(Paragraph(
    "<b>Security:</b> API keys are session-only, never persisted; production version would use OAuth-scoped "
    "read-only tokens and redact PII before any LLM call.<br/>"
    "<b>Scalability:</b> engine logic is decoupled from the data source, so JSON can be swapped for a warehouse "
    "query layer without touching scoring logic; per-account computation is independent and cacheable.<br/>"
    "<b>Error handling:</b> missing/invalid API key falls back to template summary instead of crashing; "
    "division-by-zero guarded in utilization calc; empty states render cleanly for accounts with no tickets/"
    "emails/Slack activity.",
    styles["Bodyc"]))

doc = SimpleDocTemplate(OUT, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                         leftMargin=0.65 * inch, rightMargin=0.65 * inch)
doc.build(story)
print(f"Wrote {OUT}")
