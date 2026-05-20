from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as pdfcanvas
import os

# ── Colour palette ──────────────────────────────────────────────────────────
DARK       = colors.HexColor("#1F1E1D")
MUTED      = colors.HexColor("#5F5E5A")
LIGHT_BG   = colors.HexColor("#F1EFE8")
BORDER     = colors.HexColor("#DDDBD2")

PURPLE     = colors.HexColor("#534AB7")
PURPLE_L   = colors.HexColor("#EEEDFЕ".replace("Е","E"))   # fallback
PURPLE_BG  = colors.HexColor("#EEEDFE")

ORANGE     = colors.HexColor("#854F0B")
ORANGE_BG  = colors.HexColor("#FAEEDA")

GREEN      = colors.HexColor("#0F6E56")
GREEN_BG   = colors.HexColor("#E1F5EE")

RED        = colors.HexColor("#A32D2D")
RED_BG     = colors.HexColor("#FCEBEB")

PINK       = colors.HexColor("#993556")
PINK_BG    = colors.HexColor("#FBEAF0")

BLUE       = colors.HexColor("#185FA5")
BLUE_BG    = colors.HexColor("#E6F1FB")

ACCENT     = colors.HexColor("#3B6D11")  # dashboard green

W, H = A4

# ── Custom page template ─────────────────────────────────────────────────────
def on_page(canv, doc):
    canv.saveState()
    # top bar
    canv.setFillColor(DARK)
    canv.rect(0, H - 14*mm, W, 14*mm, fill=1, stroke=0)
    canv.setFillColor(colors.white)
    canv.setFont("Helvetica-Bold", 7)
    canv.drawString(20*mm, H - 9*mm, "GRADEOPS TRIBUNAL — TECHNICAL IMPLEMENTATION GUIDE")
    canv.setFont("Helvetica", 7)
    canv.drawRightString(W - 20*mm, H - 9*mm, f"Page {doc.page}")
    # bottom rule
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.5)
    canv.line(20*mm, 12*mm, W - 20*mm, 12*mm)
    canv.setFillColor(MUTED)
    canv.setFont("Helvetica", 6.5)
    canv.drawString(20*mm, 8*mm, "Confidential — Final Project Documentation")
    canv.restoreState()

# ── Styles ───────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=base[parent], **kw)

styles = {
    "cover_title": S("cover_title", "Title",
        fontSize=32, leading=38, textColor=colors.white,
        fontName="Helvetica-Bold", alignment=TA_LEFT),

    "cover_sub": S("cover_sub", "Normal",
        fontSize=13, leading=18, textColor=colors.HexColor("#C8C5B8"),
        fontName="Helvetica", alignment=TA_LEFT),

    "cover_meta": S("cover_meta", "Normal",
        fontSize=9, textColor=colors.HexColor("#8A8880"),
        fontName="Helvetica"),

    "h1": S("h1", "Heading1",
        fontSize=18, leading=24, textColor=DARK,
        fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6),

    "h2": S("h2", "Heading2",
        fontSize=13, leading=18, textColor=PURPLE,
        fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4),

    "h3": S("h3", "Heading3",
        fontSize=10.5, leading=14, textColor=DARK,
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=3),

    "body": S("body", "Normal",
        fontSize=9.5, leading=15, textColor=DARK,
        fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=6),

    "body_l": S("body_l", "Normal",
        fontSize=9.5, leading=15, textColor=DARK,
        fontName="Helvetica", alignment=TA_LEFT, spaceAfter=4),

    "bullet": S("bullet", "Normal",
        fontSize=9, leading=14, textColor=DARK,
        fontName="Helvetica", leftIndent=14, spaceAfter=3,
        bulletIndent=4),

    "code": S("code", "Code",
        fontSize=8, leading=12, textColor=colors.HexColor("#1A1A2E"),
        fontName="Courier", backColor=colors.HexColor("#F4F3EE"),
        leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=4),

    "caption": S("caption", "Normal",
        fontSize=8, leading=11, textColor=MUTED,
        fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceAfter=8),

    "tag": S("tag", "Normal",
        fontSize=7.5, textColor=colors.white,
        fontName="Helvetica-Bold"),

    "label": S("label", "Normal",
        fontSize=8, textColor=MUTED,
        fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=2),

    "phase_label": S("phase_label", "Normal",
        fontSize=9, textColor=colors.white,
        fontName="Helvetica-Bold"),
}

# ── Helper flowables ─────────────────────────────────────────────────────────

def Rule(color=BORDER, thickness=0.5, vspace=4):
    return [Spacer(1, vspace), HRFlowable(width="100%", thickness=thickness,
            color=color, spaceAfter=vspace)]

def Badge(text, bg, fg=colors.white):
    """Inline pill badge rendered as a 1-cell table."""
    ts = TableStyle([
        ("BACKGROUND",  (0,0), (-1,-1), bg),
        ("TEXTCOLOR",   (0,0), (-1,-1), fg),
        ("FONTNAME",    (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 7.5),
        ("TOPPADDING",  (0,0), (-1,-1), 2),
        ("BOTTOMPADDING",(0,0),(-1,-1), 2),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING",(0,0), (-1,-1), 6),
        ("ROUNDEDCORNERS", [4,4,4,4]),
    ])
    t = Table([[text]], colWidths=None)
    t.setStyle(ts)
    return t

def phase_banner(label, subtitle, bg=PURPLE, fg=colors.white):
    data = [[
        Paragraph(f"<b>{label}</b>", ParagraphStyle("pb", fontName="Helvetica-Bold",
            fontSize=11, textColor=fg)),
        Paragraph(subtitle, ParagraphStyle("ps", fontName="Helvetica",
            fontSize=8.5, textColor=colors.HexColor("#D0CEEA") if bg==PURPLE else colors.white,
            alignment=TA_LEFT)),
    ]]
    ts = TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), bg),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("ROUNDEDCORNERS", [6,6,6,6]),
    ])
    t = Table(data, colWidths=[60*mm, None])
    t.setStyle(ts)
    return t

def info_box(text, bg=LIGHT_BG, border=BORDER, left_bar=None):
    """Shaded info / callout box."""
    p = Paragraph(text, ParagraphStyle("ib", fontName="Helvetica",
        fontSize=9, leading=14, textColor=DARK))
    inner = Table([[p]], colWidths=[W - 60*mm])
    inner.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), bg),
        ("TOPPADDING",   (0,0),(-1,-1), 9),
        ("BOTTOMPADDING",(0,0),(-1,-1), 9),
        ("LEFTPADDING",  (0,0),(-1,-1), 12),
        ("RIGHTPADDING", (0,0),(-1,-1), 12),
        ("BOX",          (0,0),(-1,-1), 0.5, border),
        ("ROUNDEDCORNERS", [4,4,4,4]),
    ]))
    return inner

def agent_card(title, model, role, bg, fg, detail_lines):
    """A coloured agent summary card."""
    header = [
        Paragraph(f"<b>{title}</b>", ParagraphStyle("ah", fontName="Helvetica-Bold",
            fontSize=10, textColor=fg)),
        Paragraph(model, ParagraphStyle("am", fontName="Helvetica",
            fontSize=8, textColor=fg)),
    ]
    rows = [[Paragraph(f"• {d}", ParagraphStyle("ad", fontName="Helvetica",
             fontSize=8.5, leading=13, textColor=DARK))] for d in detail_lines]

    card_data = [[header], [""]] + [[r[0]] for r in rows]

    # simpler: just use a flat table
    cell_content = [
        Paragraph(f"<b>{title}</b>", ParagraphStyle("ah", fontName="Helvetica-Bold",
            fontSize=10.5, textColor=fg)),
        Paragraph(model, ParagraphStyle("am", fontName="Helvetica-Oblique",
            fontSize=8.5, textColor=fg, spaceAfter=6)),
        Paragraph(role, ParagraphStyle("ar", fontName="Helvetica",
            fontSize=8.5, leading=13, textColor=DARK)),
        Spacer(1,4),
    ] + [Paragraph(f"• {d}", ParagraphStyle("ad", fontName="Helvetica",
            fontSize=8.5, leading=13, textColor=DARK)) for d in detail_lines]

    t = Table([[cell_content]], colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), bg),
        ("BOX",          (0,0),(-1,-1), 0.8, fg),
        ("TOPPADDING",   (0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("LEFTPADDING",  (0,0),(-1,-1), 12),
        ("RIGHTPADDING", (0,0),(-1,-1), 12),
        ("ROUNDEDCORNERS", [6,6,6,6]),
    ]))
    return t

def three_col(c1, c2, c3, gap=4*mm):
    cw = (W - 40*mm - 2*gap) / 3
    t = Table([[c1, c2, c3]], colWidths=[cw, cw, cw],
              hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN",  (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), gap),
        ("TOPPADDING",   (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
    ]))
    return t

def two_col(c1, c2, w1=None, gap=5*mm):
    avail = W - 40*mm - gap
    w1 = w1 or avail*0.5
    w2 = avail - w1
    t = Table([[c1, c2]], colWidths=[w1, w2], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN",  (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), gap),
        ("TOPPADDING",   (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
    ]))
    return t

def mini_card(title, body_lines, bg, border_color):
    content = [
        Paragraph(f"<b>{title}</b>", ParagraphStyle("mct", fontName="Helvetica-Bold",
            fontSize=9, textColor=border_color, spaceAfter=4)),
    ] + [Paragraph(f"• {l}", ParagraphStyle("mcb", fontName="Helvetica",
            fontSize=8.5, leading=13, textColor=DARK)) for l in body_lines]
    t = Table([[content]], colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,-1), bg),
        ("BOX",          (0,0),(-1,-1), 0.5, border_color),
        ("TOPPADDING",   (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING",  (0,0),(-1,-1), 10),
        ("RIGHTPADDING", (0,0),(-1,-1), 10),
        ("ROUNDEDCORNERS", [4,4,4,4]),
    ]))
    return t

def data_flow_row(arrow_label, from_node, to_node, payload):
    data = [
        [Paragraph(from_node, ParagraphStyle("dfn", fontName="Helvetica-Bold",
            fontSize=8.5, textColor=DARK)),
         Paragraph(f"→  {arrow_label}", ParagraphStyle("dfa", fontName="Helvetica-Oblique",
            fontSize=8, textColor=MUTED, alignment=TA_CENTER)),
         Paragraph(to_node, ParagraphStyle("dfn2", fontName="Helvetica-Bold",
            fontSize=8.5, textColor=DARK)),
         Paragraph(payload, ParagraphStyle("dfp", fontName="Courier",
            fontSize=7.5, textColor=GREEN, leading=11)),
        ]
    ]
    cw = (W - 40*mm) / 4
    t = Table(data, colWidths=[cw]*4)
    t.setStyle(TableStyle([
        ("BOX",          (0,0),(-1,-1), 0.4, BORDER),
        ("INNERGRID",    (0,0),(-1,-1), 0.4, BORDER),
        ("BACKGROUND",   (0,0),(-1,-1), LIGHT_BG),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 6),
        ("RIGHTPADDING", (0,0),(-1,-1), 6),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
    ]))
    return t

def tech_table(rows, col_headers=None):
    cw_ratios = [0.22, 0.28, 0.28, 0.22]
    avail = W - 40*mm
    cws = [avail * r for r in cw_ratios]
    header_style = ParagraphStyle("th", fontName="Helvetica-Bold",
        fontSize=8, textColor=colors.white)
    cell_style   = ParagraphStyle("td", fontName="Helvetica",
        fontSize=8, leading=12, textColor=DARK)

    table_data = []
    if col_headers:
        table_data.append([Paragraph(h, header_style) for h in col_headers])
    for row in rows:
        table_data.append([Paragraph(str(c), cell_style) for c in row])

    ts_cmds = [
        ("BACKGROUND",   (0,0),(-1,0),  PURPLE),
        ("BACKGROUND",   (0,1),(-1,-1), LIGHT_BG),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, LIGHT_BG]),
        ("BOX",          (0,0),(-1,-1), 0.5, BORDER),
        ("INNERGRID",    (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 6),
        ("RIGHTPADDING", (0,0),(-1,-1), 6),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
    ]
    t = Table(table_data, colWidths=cws)
    t.setStyle(TableStyle(ts_cmds))
    return t

# ── Cover page builder ───────────────────────────────────────────────────────
def draw_cover(c, doc):
    """Draw the cover page directly on the canvas via onFirstPage callback."""
    c.saveState()
    # Dark background
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Accent stripe
    c.setFillColor(PURPLE)
    c.rect(0, H*0.52, W, 4, fill=1, stroke=0)

    # Large ghost text watermark
    c.setFillColor(colors.HexColor("#2A2927"))
    c.setFont("Helvetica-Bold", 110)
    c.drawCentredString(W/2, H*0.12, "TRIBUNAL")

    # Title block
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 34)
    c.drawString(20*mm, H*0.72, "GradeOps Tribunal")
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(PURPLE)
    c.drawString(20*mm, H*0.66, "Multi-Model Adversarial Grading Pipeline")

    c.setFillColor(colors.HexColor("#B0ADA5"))
    c.setFont("Helvetica", 11)
    c.drawString(20*mm, H*0.60,
        "Technical Implementation Guide  ·  Data Flow  ·  Architecture Reference")

    # Divider
    c.setStrokeColor(PURPLE)
    c.setLineWidth(1.5)
    c.line(20*mm, H*0.575, W-20*mm, H*0.575)

    # Phase pills
    phases = [
        (" 1  INGEST ", PURPLE),
        (" 2  EXTRACT ", GREEN),
        (" 3  TRIBUNAL ", colors.HexColor("#993556")),
        (" 4  VERIFY ", ORANGE),
        (" 5  DELIVER ", ACCENT),
    ]
    x = 20*mm
    y = H*0.535
    for label, col in phases:
        c.setFillColor(col)
        tw = c.stringWidth(label, "Helvetica-Bold", 8)
        c.roundRect(x, y, tw+6, 14, 3, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x+3, y+3.5, label)
        x += tw + 12

    # Meta block bottom
    c.setFillColor(colors.HexColor("#3A3835"))
    c.rect(0, 0, W, 38*mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#6A6860"))
    c.setFont("Helvetica", 9)
    c.drawString(20*mm, 28*mm, "Final Project  ·  AI-Assisted Automated Grading System")
    c.setFillColor(colors.HexColor("#4A4845"))
    c.setFont("Helvetica", 8)
    c.drawString(20*mm, 20*mm,
        "Covers: Document Ingestion  ·  Dual Extraction Paths  ·  Adversarial Agent Debate")
    c.drawString(20*mm, 13*mm,
        "RAG-Augmented Consistency  ·  CLIP-Based Plagiarism Detection  ·  TA Dashboard")
    c.setFillColor(colors.HexColor("#6A6860"))
    c.setFont("Helvetica", 8.5)
    c.drawRightString(W-20*mm, 20*mm, "5 Phases")
    c.drawRightString(W-20*mm, 13*mm, "12+ Components")
    c.restoreState()

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD DOCUMENT
# ═══════════════════════════════════════════════════════════════════════════════
def build():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GradeOps_Tribunal_Implementation_Guide.pdf")

    doc = SimpleDocTemplate(
        out,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=22*mm, bottomMargin=18*mm,
        title="GradeOps Tribunal — Technical Implementation Guide",
        author="GradeOps Final Project",
    )

    story = []

    # ── COVER ────────────────────────────────────────────────────────────────
    # Cover is drawn via onFirstPage callback (draw_cover); just need a PageBreak
    story.append(Spacer(1, 1))
    story.append(PageBreak())

    # ── TABLE OF CONTENTS ────────────────────────────────────────────────────
    story.append(Paragraph("Table of Contents", styles["h1"]))
    story.extend(Rule())

    toc_items = [
        ("1.", "System Overview & Design Philosophy", "3"),
        ("2.", "Phase 1 — INGEST: Document Ingestion Pipeline", "4"),
        ("3.", "Phase 2 — EXTRACT: Dual Extraction Paths", "5"),
        ("4.", "Phase 3 — THE TRIBUNAL: Adversarial Agent Debate", "7"),
        ("5.", "Phase 4 — VERIFY: Coordinator & Consensus Loop", "10"),
        ("5b.", "Phase 4B — Parallel Plagiarism Detection (CLIP)", "11"),
        ("6.", "Phase 5 — DELIVER: Persistence & TA Dashboard", "12"),
        ("7.", "Full Data Flow Reference", "13"),
        ("8.", "Technology Stack & Rationale", "14"),
        ("9.", "Implementation Guide & Integration Notes", "15"),
        ("10.", "Deployment Architecture & Scaling Considerations", "17"),
    ]
    toc_data = []
    for num, title, pg in toc_items:
        toc_data.append([
            Paragraph(num, ParagraphStyle("tn", fontName="Helvetica-Bold",
                fontSize=9.5, textColor=PURPLE)),
            Paragraph(title, ParagraphStyle("tt", fontName="Helvetica",
                fontSize=9.5, textColor=DARK)),
            Paragraph(pg, ParagraphStyle("tp", fontName="Helvetica",
                fontSize=9.5, textColor=MUTED, alignment=TA_CENTER)),
        ])
    toc_t = Table(toc_data, colWidths=[12*mm, None, 15*mm])
    toc_t.setStyle(TableStyle([
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",  (0,0),(-1,-1), 4),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.white, LIGHT_BG]),
        ("LINEBELOW",    (0,0),(-1,-1), 0.3, BORDER),
    ]))
    story.append(toc_t)
    story.append(PageBreak())

    # ── SECTION 1: OVERVIEW ──────────────────────────────────────────────────
    story.append(Paragraph("1. System Overview &amp; Design Philosophy", styles["h1"]))
    story.extend(Rule(PURPLE, 1))

    story.append(Paragraph(
        "GradeOps Tribunal is a production-grade, multi-agent AI pipeline designed to automate "
        "the grading of handwritten and typed exam papers at scale. The system coordinates three "
        "specialist AI agents in an adversarial debate loop — a Grader, a Critic, and a RAG "
        "retrieval agent — arbitrated by a lightweight Coordinator. Unlike naive single-model "
        "grading, GradeOps is explicitly designed to surface disagreements, catch partial-credit "
        "errors, and maintain consistency across an entire cohort by anchoring every decision in "
        "semantically similar past grades.",
        styles["body"]))

    story.append(Paragraph(
        "The system simultaneously runs a CLIP-based visual plagiarism detector as a background "
        "job, embedding raw answer images (not just their text transcriptions) to catch diagram "
        "copies and spatially-similar proofs that text-level similarity metrics miss entirely.",
        styles["body"]))

    story.append(Spacer(1, 6))

    # Design principles table
    principles = [
        ["Design Principle", "Technical Mechanism", "Why It Matters"],
        ["Multimodal grounding",
         "Raw image crops fed directly to VLMs alongside OCR text",
         "Eliminates OCR translation loss on diagrams, spatial math, and free-body diagrams"],
        ["Adversarial consistency",
         "Critic agent with devil's-advocate system prompt runs on every graded answer",
         "Forces explicit justification; surfaces partial-credit omissions before persistence"],
        ["RAG-anchored calibration",
         "ChromaDB / pgvector semantic search over historically graded answers",
         "Grading consistency is a retrieval problem — similar answers should get similar scores"],
        ["Bounded retry budget",
         "Coordinator enforces a max-iteration cap on the debate loop",
         "Prevents infinite spin in edge cases; guarantees pipeline forward progress"],
        ["Visual plagiarism",
         "CLIP embeddings + cosine similarity over image vectors",
         "Catches diagram copies and spatial proof reproductions invisible to text diff"],
        ["Human-in-the-loop",
         "TA dashboard with keyboard-driven approve/override/flag workflow",
         "AI provides the first pass; humans retain final authority on contested grades"],
    ]
    p_hdr = ParagraphStyle("ph", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)
    p_cel = ParagraphStyle("pc", fontName="Helvetica", fontSize=8.5, leading=13, textColor=DARK)
    t_data = []
    for i, row in enumerate(principles):
        style = p_hdr if i == 0 else p_cel
        t_data.append([Paragraph(c, style) for c in row])
    avail = W - 40*mm
    pt = Table(t_data, colWidths=[avail*0.22, avail*0.38, avail*0.40])
    pt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  DARK),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, LIGHT_BG]),
        ("BOX",           (0,0),(-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(pt)
    story.append(Spacer(1, 6))

    story.append(info_box(
        "<b>Five-Phase Architecture at a Glance:</b>  "
        "INGEST (document splitting) → EXTRACT (OCR + raw image routing) → "
        "TRIBUNAL (parallel agent debate) → VERIFY (coordinator consensus + plagiarism) → "
        "DELIVER (database persistence + TA dashboard + gradebook export).",
        bg=PURPLE_BG, border=PURPLE))
    story.append(PageBreak())

    # ── SECTION 2: INGEST ────────────────────────────────────────────────────
    story.append(phase_banner("PHASE 1  ·  INGEST",
        "Document Ingestion & Page Splitting", bg=DARK))
    story.append(Spacer(1, 8))
    story.append(Paragraph("2. Phase 1 — INGEST: Document Ingestion Pipeline", styles["h1"]))
    story.extend(Rule(PURPLE, 1))

    story.append(Paragraph(
        "The pipeline accepts two parallel inputs: a bulk-upload exam scan PDF (potentially "
        "containing hundreds of student papers) and a Rubric JSON file that encodes per-question "
        "scoring criteria and point weights. These two inputs converge at the PDF Splitter + "
        "Cropper, which is the first orchestration component.",
        styles["body"]))

    story.append(Paragraph("2.1  Input: Exam Scan PDF", styles["h2"]))
    story.append(Paragraph(
        "Scanned exam PDFs arrive as multi-page, multi-student documents. The ingestion layer "
        "must handle variable scan quality (300 DPI minimum recommended), skewed pages, and "
        "inconsistent answer box boundaries. Each PDF is stored in object storage (e.g., S3 or "
        "GCS) immediately on upload and assigned a batch_id. A task queue (Celery + Redis) "
        "dispatches per-PDF processing jobs.",
        styles["body"]))

    story.append(Paragraph("2.2  Input: Rubric JSON Schema", styles["h2"]))
    story.append(Paragraph(
        "The rubric is the authoritative scoring contract. It is parsed once per batch and "
        "injected into every downstream agent context. A well-structured rubric JSON is critical "
        "— ambiguous rubrics directly degrade Grader output quality.",
        styles["body"]))

    story.append(Paragraph("Rubric JSON schema (recommended):", styles["label"]))
    story.append(Paragraph("""{
  "exam_id": "CS301-Midterm-2025",
  "questions": [
    {
      "q_id": "Q1",
      "max_points": 10,
      "criteria": [
        { "id": "c1", "description": "Correct base case identified", "points": 2 },
        { "id": "c2", "description": "Inductive step is logically sound", "points": 5 },
        { "id": "c3", "description": "Notation is mathematically precise", "points": 3 }
      ],
      "answer_region": { "page": 1, "bbox": [0.05, 0.30, 0.95, 0.75] }
    }
  ]
}""", styles["code"]))

    story.append(Paragraph("2.3  PDF Splitter + Cropper", styles["h2"]))
    story.append(Paragraph(
        "Implemented using PyMuPDF (fitz) or pdfplumber, the splitter performs two operations: "
        "(1) page-level splitting — separating each student's answer sheet — and (2) "
        "question-level cropping — extracting a per-question bounding-box image crop from each "
        "page. The bounding boxes are defined in the rubric's answer_region field as normalized "
        "[x0, y0, x1, y1] coordinates relative to the page dimensions.",
        styles["body"]))

    story.append(Paragraph("Splitter pseudocode:", styles["label"]))
    story.append(Paragraph("""import fitz  # PyMuPDF

def crop_answer_region(pdf_path, page_num, bbox_norm, dpi=150):
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    rect = page.rect
    # Convert normalised bbox → absolute pixel coordinates
    clip = fitz.Rect(
        bbox_norm[0] * rect.width,  bbox_norm[1] * rect.height,
        bbox_norm[2] * rect.width,  bbox_norm[3] * rect.height
    )
    mat = fitz.Matrix(dpi/72, dpi/72)  # render at target DPI
    pix = page.get_pixmap(matrix=mat, clip=clip)
    return pix.tobytes("png")  # → raw PNG bytes for downstream agents""", styles["code"]))

    story.append(Spacer(1, 4))
    story.append(two_col(
        mini_card("Inputs", [
            "Exam scan PDF (bulk, multi-student)",
            "Rubric JSON (per-question criteria + bounding boxes)",
            "batch_id from object storage",
        ], LIGHT_BG, BORDER),
        mini_card("Outputs", [
            "Per-question PNG image crops (raw bytes)",
            "Structured rubric dict (Python object)",
            "student_id × question_id routing map",
            "Metadata: page_num, crop_bbox, dpi",
        ], GREEN_BG, GREEN),
        w1=(W-40*mm)*0.5))
    story.append(PageBreak())

    # ── SECTION 3: EXTRACT ───────────────────────────────────────────────────
    story.append(phase_banner("PHASE 2  ·  EXTRACT",
        "Dual Extraction: OCR Path vs. Raw Image Bypass", bg=GREEN))
    story.append(Spacer(1, 8))
    story.append(Paragraph("3. Phase 2 — EXTRACT: Dual Extraction Paths", styles["h1"]))
    story.extend(Rule(GREEN, 1))

    story.append(Paragraph(
        "The EXTRACT phase is one of the most architecturally distinctive decisions in GradeOps. "
        "Rather than treating OCR as a universal preprocessing step, the system explicitly routes "
        "each answer crop down one of two paths based on content type. This routing is determined "
        "by the rubric's content_type field or by a lightweight content classifier.",
        styles["body"]))

    story.append(Paragraph("3.1  The Routing Decision", styles["h2"]))
    story.append(Paragraph(
        "A fast, lightweight content-type classifier (a fine-tuned ViT or simple heuristic based "
        "on symbol density) examines each crop and assigns it to either the OCR path or the "
        "raw image bypass path. The rubric can also explicitly override this with a "
        "<b>bypass_ocr: true</b> flag per question.",
        styles["body"]))

    route_data = [
        ["Decision Factor", "OCR Path (Nougat / Qwen-VL)", "Raw Image Bypass"],
        ["Content type", "Dense handwritten text, formulae, structured prose",
         "Diagrams, graphs, geometric proofs, spatial math, free-body diagrams"],
        ["Why this path", "OCR converts handwriting to structured text the LLM can reason over precisely",
         "OCR would destroy spatial relationships that are semantically meaningful"],
        ["OCR model used", "Nougat (Meta) for LaTeX-aware math parsing; Qwen-VL as fallback for general handwriting",
         "N/A — raw PNG bytes sent directly to VLM's vision encoder"],
        ["Output format", "Markdown + LaTeX string (e.g., $$\\sum_{i=0}^n i = \\frac{n(n+1)}{2}$$)",
         "Base64-encoded PNG in VLM multimodal message payload"],
        ["Information loss risk", "Low for text; medium for inline diagrams (OCR may skip)",
         "Effectively zero — VLM sees original pixel data"],
    ]
    r_hdr = ParagraphStyle("rh", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)
    r_cel = ParagraphStyle("rc", fontName="Helvetica", fontSize=8.5, leading=13, textColor=DARK)
    r_data = []
    for i, row in enumerate(route_data):
        s = r_hdr if i == 0 else r_cel
        r_data.append([Paragraph(c, s) for c in row])
    avail = W - 40*mm
    rt = Table(r_data, colWidths=[avail*0.20, avail*0.40, avail*0.40])
    rt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  GREEN),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, GREEN_BG]),
        ("BOX",           (0,0),(-1,-1), 0.5, GREEN),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(rt)
    story.append(Spacer(1, 10))

    story.append(Paragraph("3.2  OCR Path: Nougat / Qwen-VL", styles["h2"]))
    story.append(Paragraph(
        "Nougat (Meta, 2023) is a transformer-based document understanding model specifically "
        "pre-trained on academic papers and mathematical notation. It converts page images "
        "directly to Markdown with embedded LaTeX — making it ideal for exam answers that contain "
        "inline equations, summations, integrals, and proof notation. Qwen-VL serves as a "
        "general-purpose fallback for answers with heavy freehand prose or non-standard notation.",
        styles["body"]))

    story.append(Paragraph("Nougat inference call (HuggingFace):", styles["label"]))
    story.append(Paragraph("""from transformers import NougatProcessor, VisionEncoderDecoderModel
from PIL import Image
import io

processor = NougatProcessor.from_pretrained("facebook/nougat-base")
model = VisionEncoderDecoderModel.from_pretrained("facebook/nougat-base")

def ocr_crop(png_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    pixel_values = processor(image, return_tensors="pt").pixel_values
    outputs = model.generate(pixel_values, max_new_tokens=512,
                             bad_words_ids=[[processor.tokenizer.unk_token_id]])
    return processor.batch_decode(outputs, skip_special_tokens=True)[0]
    # Returns: Markdown string with LaTeX formulae""", styles["code"]))

    story.append(Paragraph("3.3  Raw Image Bypass Path", styles["h2"]))
    story.append(Paragraph(
        "For diagrams, circuit schematics, geometric constructions, and spatial math proofs, the "
        "PNG crop is sent directly to the Grader VLM without any OCR intermediary. The image is "
        "Base64-encoded and injected into the VLM's multimodal message payload as an "
        "image_url or image content block. This preserves every pixel of spatial information "
        "that OCR would destroy — relative positions of labels, arrow directions, shaded regions, "
        "and geometric relationships.",
        styles["body"]))

    story.append(Paragraph("3.4  Context Assembler", styles["h2"]))
    story.append(Paragraph(
        "The Context Assembler is the merge node that packages both extraction outputs — OCR "
        "transcript (if available) and raw image crop — along with the rubric JSON for the "
        "specific question into a single structured context object. This context object is what "
        "all three Tribunal agents receive as input.",
        styles["body"]))

    story.append(Paragraph("Assembled context object schema:", styles["label"]))
    story.append(Paragraph("""{
  "student_id": "S042",
  "question_id": "Q3b",
  "rubric": { "max_points": 8, "criteria": [...] },
  "ocr_transcript": "Let A be a set. By definition of power set, P(A) = ...",
  "image_crop_b64": "iVBORw0KGgoAAAANS...",   // null if OCR-only question
  "bypass_ocr": false,
  "rag_examples": []       // populated by RAG Agent before Grader receives context
}""", styles["code"]))
    story.append(PageBreak())

    # ── SECTION 4: TRIBUNAL ──────────────────────────────────────────────────
    story.append(phase_banner("PHASE 3  ·  THE TRIBUNAL",
        "Adversarial 3-Agent Grading Debate", bg=PINK))
    story.append(Spacer(1, 8))
    story.append(Paragraph("4. Phase 3 — THE TRIBUNAL: Adversarial Agent Debate", styles["h1"]))
    story.extend(Rule(PINK, 1))

    story.append(Paragraph(
        "The Tribunal is the architectural centrepiece of GradeOps. Three specialist agents "
        "execute in parallel — each approaching the same answer crop from a distinct adversarial "
        "stance. This multi-agent debate pattern is fundamentally different from ensembling: the "
        "agents are not voting on a score, they are constructing arguments that the Coordinator "
        "must adjudicate. The adversarial tension is deliberate and load-bearing.",
        styles["body"]))

    story.append(Spacer(1, 8))

    # Three agent cards
    grader_card = agent_card(
        "Grader Agent", "GPT-4o Vision  /  Gemini Pro Vision",
        "Primary scoring model. Heavyweight VLM that sees both the raw image crop and the "
        "OCR transcript simultaneously, conditioned on the full rubric.",
        RED_BG, RED,
        [
            "Receives: image_crop_b64 + ocr_transcript + rubric + rag_examples",
            "System prompt: 'You are a fair but rigorous examiner. Score each rubric criterion independently. Output structured JSON only.'",
            "Output schema: { score, max_score, criteria_breakdown: [{id, awarded, justification}], transcribed_snippets: [...] }",
            "Model choice rationale: GPT-4o and Gemini Pro Vision lead on mathematical OCR benchmarks and can reason over handwritten LaTeX in situ",
            "Cost profile: ~$0.01–0.03 per answer depending on image size; budget ~60% of per-answer cost here",
        ])

    critic_card = agent_card(
        "Critic Agent", "Claude Haiku  /  Llama 3-8B",
        "Adversarial auditor. Deliberately cheap, fast, and instruction-tuned to find what "
        "the Grader missed. Runs on the Grader's output — not the raw context.",
        PINK_BG, PINK,
        [
            "Receives: Grader's full JSON output + original rubric + ocr_transcript",
            "System prompt: 'You are a devil's advocate. Your ONLY job is to find errors in this grade. Look for: partial credit missed, rubric criteria misread, steps hallucinated, score inconsistencies.'",
            "Output schema: { agrees: bool, objections: [{criterion_id, issue, suggested_correction}], severity: 'minor'|'major' }",
            "Model choice rationale: Haiku / Llama 3-8B are 10-20x cheaper than GPT-4o; the Critic does NOT need vision — it reasons over text alone",
            "Cost profile: ~$0.0005–0.001 per answer; budget ~10% of per-answer cost",
        ])

    rag_card = agent_card(
        "RAG Agent", "ChromaDB  /  pgvector  +  Embedding Model",
        "Consistency anchor. Retrieves the top-3 semantically similar past graded answers "
        "from the vector store and injects them as few-shot examples into the Grader's context.",
        BLUE_BG, BLUE,
        [
            "Executes BEFORE the Grader so examples are available in context",
            "Embedding model: text-embedding-3-small (OpenAI) or sentence-transformers/all-mpnet-base-v2",
            "Query: embed(ocr_transcript + question_id) → cosine similarity search over ChromaDB collection",
            "Retrieved schema: [{ student_id, ocr_transcript, awarded_score, justification }] × 3",
            "Purpose: transforms 'is this score right?' into 'is this score consistent with similar past answers?'",
            "Cold-start: seed with instructor-graded reference answers before first batch run",
        ])

    story.append(grader_card)
    story.append(Spacer(1, 8))
    story.append(critic_card)
    story.append(Spacer(1, 8))
    story.append(rag_card)
    story.append(Spacer(1, 10))

    story.append(Paragraph("4.1  Grader Agent — Deep Dive", styles["h2"]))
    story.append(Paragraph(
        "The Grader is the only agent in the pipeline that receives the raw image crop. It "
        "constructs a multimodal prompt that interleaves the rubric criteria, the OCR transcript "
        "(as a textual hint, not the ground truth), and the image. The structured JSON output "
        "requirement is enforced via constrained decoding (function calling / tool use in GPT-4o, "
        "or JSON mode in Gemini). This eliminates free-form output parsing entirely.",
        styles["body"]))

    story.append(Paragraph("Grader prompt construction (Python):", styles["label"]))
    story.append(Paragraph("""import base64, json

def build_grader_prompt(ctx: dict) -> list:
    rubric_text = json.dumps(ctx["rubric"], indent=2)
    rag_block = "\\n\\n".join([
        f"PAST EXAMPLE (score {ex['score']}/{ex['max']}):\\n{ex['justification']}"
        for ex in ctx["rag_examples"]
    ])
    messages = [
        {"role": "system", "content":
            "You are a rigorous but fair exam grader. Score each rubric criterion "
            "independently. Output ONLY valid JSON matching the provided schema."},
        {"role": "user", "content": [
            {"type": "text",
             "text": f"RUBRIC:\\n{rubric_text}\\n\\nPAST EXAMPLES:\\n{rag_block}\\n\\n"
                     f"OCR TRANSCRIPT (hint only):\\n{ctx['ocr_transcript']}\\n\\n"
                     "Grade the answer shown in the image below."},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{ctx['image_crop_b64']}"
            }},
        ]}
    ]
    return messages""", styles["code"]))

    story.append(Paragraph("4.2  Critic Agent — Adversarial System Prompt Design", styles["h2"]))
    story.append(Paragraph(
        "The Critic's system prompt is the most deliberately adversarial component in the system. "
        "It is explicitly instruction-tuned to disagree, not to validate. Common failure modes "
        "it is trained to catch include: (a) hallucinated intermediate steps that the Grader "
        "accepted as correct, (b) rubric criteria awarded points that the answer doesn't satisfy, "
        "(c) partial credit that should have been awarded but wasn't, and (d) score arithmetic "
        "errors across criteria.",
        styles["body"]))

    story.append(Paragraph("Critic system prompt (exact):", styles["label"]))
    story.append(Paragraph("""CRITIC_SYSTEM_PROMPT = \"\"\"
You are a devil's advocate reviewing an AI-generated exam grade.
Your ONLY job is to find errors, inconsistencies, and missed partial credit.

For each rubric criterion, ask:
  1. Did the Grader actually verify this criterion against the answer, or assume it?
  2. Are the awarded points consistent with the justification given?
  3. Were any steps or concepts hallucinated (claimed present but not in the answer)?
  4. Was partial credit available that was not awarded?

Output ONLY valid JSON:
{
  "agrees": bool,
  "objections": [
    { "criterion_id": str, "issue": str, "suggested_score": int, "severity": "minor|major" }
  ],
  "overall_severity": "none|minor|major"
}
\"\"\"
""", styles["code"]))

    story.append(Paragraph("4.3  RAG Agent — Vector Retrieval for Consistency", styles["h2"]))
    story.append(Paragraph(
        "The RAG agent transforms grading from a one-shot scoring task into a retrieval-augmented "
        "few-shot task. By injecting the top-3 most semantically similar past answers (with their "
        "awarded scores and justifications), the Grader is implicitly constrained to be "
        "consistent across the cohort. This is the primary mechanism for inter-rater reliability "
        "at scale.",
        styles["body"]))

    story.append(Paragraph("ChromaDB retrieval (Python):", styles["label"]))
    story.append(Paragraph("""import chromadb
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-mpnet-base-v2")
client = chromadb.PersistentClient(path="./gradeops_db")
collection = client.get_or_create_collection("graded_answers")

def retrieve_rag_examples(ocr_transcript: str, question_id: str, k: int = 3):
    query_embedding = embedder.encode(
        f"[Q:{question_id}] {ocr_transcript}"
    ).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        where={"question_id": question_id}   # filter to same question only
    )
    return [
        { "score": m["awarded_score"], "max": m["max_score"],
          "justification": m["justification"], "transcript": doc }
        for doc, m in zip(results["documents"][0], results["metadatas"][0])
    ]""", styles["code"]))
    story.append(PageBreak())

    # ── SECTION 5: VERIFY ────────────────────────────────────────────────────
    story.append(phase_banner("PHASE 4  ·  VERIFY",
        "Coordinator Arbitration & Consensus Loop", bg=colors.HexColor("#854F0B")))
    story.append(Spacer(1, 8))
    story.append(Paragraph("5. Phase 4 — VERIFY: Coordinator &amp; Consensus Loop", styles["h1"]))
    story.extend(Rule(colors.HexColor("#854F0B"), 1))

    story.append(Paragraph(
        "After all three Tribunal agents have produced their outputs, the Coordinator agent "
        "reads both the Grader's scoring JSON and the Critic's objection JSON and makes the "
        "final binding decision. The Coordinator is implemented on the same cheap, fast model "
        "as the Critic (Claude Haiku / Llama 3-8B) because its task is purely textual reasoning "
        "over structured data — it has no need for vision capabilities.",
        styles["body"]))

    story.append(Paragraph("5.1  The Consensus Diamond", styles["h2"]))
    story.append(Paragraph(
        "The consensus decision is a simple binary: did the Grader and Critic agree? Agreement is "
        "defined operationally as: (a) <b>agrees=true</b> from the Critic, OR (b) all objections "
        "have severity='minor' AND the score delta across all criteria is zero. If consensus is "
        "reached, the Grader's output is persisted immediately. If consensus is NOT reached, "
        "the Coordinator enters arbitration.",
        styles["body"]))

    story.append(Paragraph("5.2  Coordinator Arbitration Logic", styles["h2"]))
    story.append(Paragraph(
        "The Coordinator receives the full Grader JSON, the Critic objection JSON, and the "
        "original rubric. It must produce a final_grade JSON that either accepts the Grader's "
        "score, modifies it per the Critic's suggestions, or rejects both and calls for a "
        "human-review flag. The Coordinator is the ONLY component that can emit a requires_human "
        "flag — this escalates directly to the TA dashboard with high priority.",
        styles["body"]))

    story.append(Paragraph("Coordinator decision schema:", styles["label"]))
    story.append(Paragraph("""{
  "final_score": 7,
  "max_score": 10,
  "resolution": "grader_accepted" | "critic_correction_applied" | "requires_human",
  "resolution_rationale": "Critic identified that criterion c2 awarded 5/5 but the "
                          "inductive step contained an unverified base assumption...",
  "criteria_final": [
    { "id": "c1", "awarded": 2, "source": "grader" },
    { "id": "c2", "awarded": 3, "source": "coordinator",
      "override_reason": "Critic objection: hallucinated step in induction" }
  ],
  "iteration": 1,   // incremented on each retry
  "requires_human": false
}""", styles["code"]))

    story.append(Paragraph("5.3  Retry Budget & Loop Termination", styles["h2"]))
    story.append(Paragraph(
        "The consensus loop has a hard maximum iteration count (default: 3). On each failed "
        "consensus check, the Coordinator's latest resolution is fed back into the Critic as "
        "an additional input alongside the original Grader output. If max iterations are "
        "exhausted without consensus, the answer is automatically flagged requires_human=true "
        "and forwarded to the TA dashboard with iteration history attached.",
        styles["body"]))

    story.append(info_box(
        "<b>Loop termination conditions:</b>  "
        "(1) Critic agrees=true on any iteration, "
        "(2) All remaining objections are severity=minor and coordinator accepts them, "
        "(3) max_iterations reached → escalate to human review. "
        "This guarantee ensures the pipeline never stalls on a single answer.",
        bg=ORANGE_BG, border=ORANGE))

    story.append(PageBreak())

    # ── SECTION 5B: PLAGIARISM ───────────────────────────────────────────────
    story.append(phase_banner("PHASE 4B  ·  PARALLEL JOB",
        "CLIP-Based Visual Plagiarism Detection", bg=RED))
    story.append(Spacer(1, 8))
    story.append(Paragraph("5b. Phase 4B — Parallel Plagiarism Detection (CLIP)", styles["h1"]))
    story.extend(Rule(RED, 1))

    story.append(Paragraph(
        "The plagiarism detector runs as an independent background job — fully decoupled from "
        "the Tribunal loop. It receives the raw image crops from the EXTRACT phase and embeds "
        "them using OpenAI CLIP (Contrastive Language-Image Pre-training) into a shared "
        "embedding space. It then computes pairwise cosine similarities across all crops for "
        "the same question_id within a batch.",
        styles["body"]))

    story.append(Paragraph("5b.1  Why CLIP and Not Text Similarity?", styles["h2"]))
    story.append(Paragraph(
        "Text-level similarity (e.g., TF-IDF, BM25, sentence embeddings over OCR output) is "
        "blind to visual structure. A student who copies a diagram, a free-body diagram, a "
        "circuit schematic, or a geometric proof can trivially avoid text-level detection by "
        "relabelling nodes. CLIP embeds the raw pixel content into a semantic vector space where "
        "visually similar images (regardless of label text) cluster together. This closes a "
        "significant loophole that text-only plagiarism detection leaves open.",
        styles["body"]))

    story.append(Paragraph("CLIP embedding + cosine similarity (Python):", styles["label"]))
    story.append(Paragraph("""import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import io

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_proc  = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def embed_crop(png_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    inputs = clip_proc(images=image, return_tensors="pt")
    with torch.no_grad():
        embedding = clip_model.get_image_features(**inputs)
    return embedding[0].numpy() / np.linalg.norm(embedding[0].numpy())  # L2-normalise

def detect_plagiarism(crops: dict, threshold: float = 0.92) -> list:
    \"\"\"crops: { student_id -> png_bytes }\"\"\"
    embeddings = { sid: embed_crop(b) for sid, b in crops.items() }
    flags = []
    ids = list(embeddings.keys())
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            cosine_sim = np.dot(embeddings[ids[i]], embeddings[ids[j]])
            if cosine_sim >= threshold:
                flags.append({ "pair": (ids[i], ids[j]),
                               "similarity": float(cosine_sim),
                               "flag": "VISUAL_PLAGIARISM_SUSPECTED" })
    return flags""", styles["code"]))

    story.append(Paragraph("5b.2  Threshold Calibration", styles["h2"]))
    story.append(Paragraph(
        "The cosine similarity threshold (default 0.92) is a hyperparameter that must be "
        "calibrated per exam type. For diagram-heavy exams (circuit analysis, geometry), a "
        "threshold of 0.88–0.90 is appropriate since legitimate solutions often share structural "
        "similarity. For proof-based exams, 0.93–0.95 reduces false positives. Flags are "
        "soft — they add a plagiarism_suspected field to the database record and surface in "
        "the TA dashboard for human review; no automatic score penalty is applied.",
        styles["body"]))

    story.append(info_box(
        "<b>Implementation note:</b> Run CLIP embedding as a batched GPU job over all crops "
        "for a given question_id simultaneously. The pairwise comparison is O(n²) in the "
        "number of students — for cohorts above 200, use approximate nearest-neighbour "
        "libraries (FAISS or ScaNN) with an index over the embedding vectors.",
        bg=RED_BG, border=RED))
    story.append(PageBreak())

    # ── SECTION 6: DELIVER ───────────────────────────────────────────────────
    story.append(phase_banner("PHASE 5  ·  DELIVER",
        "Database Persistence, TA Dashboard & Gradebook Export", bg=ACCENT))
    story.append(Spacer(1, 8))
    story.append(Paragraph("6. Phase 5 — DELIVER: Persistence &amp; TA Dashboard", styles["h1"]))
    story.extend(Rule(ACCENT, 1))

    story.append(Paragraph("6.1  Database Persistence", styles["h2"]))
    story.append(Paragraph(
        "Every resolved grade — whether consensus was immediate or required coordinator "
        "arbitration — is written to a PostgreSQL or MongoDB instance. The schema is designed "
        "for full auditability: every agent's intermediate output is stored alongside the "
        "final grade. This enables post-hoc analysis of inter-agent agreement rates and "
        "Critic objection patterns.",
        styles["body"]))

    story.append(Paragraph("PostgreSQL grade record schema (DDL):", styles["label"]))
    story.append(Paragraph("""CREATE TABLE grade_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id        TEXT NOT NULL,
    student_id      TEXT NOT NULL,
    question_id     TEXT NOT NULL,

    -- Final verdict
    final_score     SMALLINT NOT NULL,
    max_score       SMALLINT NOT NULL,
    resolution      TEXT CHECK (resolution IN (
                        'grader_accepted', 'critic_correction_applied', 'requires_human')),
    requires_human  BOOLEAN DEFAULT FALSE,
    human_override  BOOLEAN DEFAULT FALSE,

    -- Agent outputs (JSONB for flexible querying)
    grader_output   JSONB,   -- full Grader JSON
    critic_output   JSONB,   -- full Critic JSON
    coordinator_out JSONB,   -- Coordinator final JSON
    rag_examples    JSONB,   -- top-3 retrieved examples

    -- Plagiarism
    plagiarism_flag BOOLEAN DEFAULT FALSE,
    plagiarism_sim  FLOAT,   -- cosine similarity score if flagged

    -- Metadata
    image_crop_path TEXT,    -- S3/GCS URI of the original crop
    iterations      SMALLINT DEFAULT 1,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at     TIMESTAMPTZ,
    reviewed_by     TEXT
);""", styles["code"]))

    story.append(Paragraph("6.2  TA Review Dashboard", styles["h2"]))
    story.append(Paragraph(
        "The dashboard is a keyboard-driven, high-throughput review interface. Each record is "
        "presented as a side-by-side view: the original image crop on the left, the AI-generated "
        "grade breakdown on the right. The TA can approve (mark as final), override (manually "
        "enter a score with a reason), or flag (escalate for second opinion). The interface is "
        "designed for speed: a single keyboard shortcut per action, with the next record "
        "auto-loading on action.",
        styles["body"]))

    dash_items = [
        ["Dashboard Feature", "Implementation"],
        ["Side-by-side view", "Image crop (S3 presigned URL) + Grader/Coordinator JSON rendered as structured card"],
        ["Approve (A key)", "Sets human_override=false, reviewed_by=TA_id, reviewed_at=now()"],
        ["Override (O key)", "Opens score input modal; writes corrected score + reason; sets human_override=true"],
        ["Flag (F key)", "Sets requires_human=true; routes to senior TA queue"],
        ["Priority queue", "requires_human=true records shown first; sorted by plagiarism_flag, then by score delta (Grader vs Critic)"],
        ["Bulk approve", "For records where Critic agreed and similarity to RAG example > 0.85, allow batch approval"],
        ["Audit trail", "Every action logged to grade_audit_log table with timestamp, TA ID, and before/after state"],
    ]
    d_hdr = ParagraphStyle("dh", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)
    d_cel = ParagraphStyle("dc", fontName="Helvetica", fontSize=8.5, leading=13, textColor=DARK)
    d_data = []
    for i, row in enumerate(dash_items):
        s = d_hdr if i == 0 else d_cel
        d_data.append([Paragraph(c, s) for c in row])
    avail = W - 40*mm
    dt = Table(d_data, colWidths=[avail*0.28, avail*0.72])
    dt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  ACCENT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, GREEN_BG]),
        ("BOX",           (0,0),(-1,-1), 0.5, ACCENT),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(dt)
    story.append(Spacer(1, 8))

    story.append(Paragraph("6.3  Final Gradebook Export", styles["h2"]))
    story.append(Paragraph(
        "Once a batch reaches the configured review_threshold (default: 100% of requires_human "
        "records reviewed, plus a random sample of auto-approved records), the gradebook export "
        "is triggered. The export queries the grade_records table, aggregates per-student "
        "totals, and outputs CSV / Excel / LMS-format (Canvas, Blackboard, Moodle) files. "
        "The export includes a per-student grade breakdown, flagged plagiarism pairs, and a "
        "batch-level inter-agent agreement report.",
        styles["body"]))
    story.append(PageBreak())

    # ── SECTION 7: DATA FLOW ─────────────────────────────────────────────────
    story.append(Paragraph("7. Full Data Flow Reference", styles["h1"]))
    story.extend(Rule(PURPLE, 1))

    story.append(Paragraph(
        "The table below documents every significant data handoff in the pipeline, the format "
        "of the payload at each stage, and the consuming component.",
        styles["body"]))
    story.append(Spacer(1, 6))

    flow_header = ParagraphStyle("fh", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)
    flow_cell   = ParagraphStyle("fc", fontName="Helvetica", fontSize=8.5, leading=12, textColor=DARK)
    flow_code   = ParagraphStyle("fco", fontName="Courier", fontSize=7.5, leading=11, textColor=GREEN)
    avail = W - 40*mm

    flow_rows_raw = [
        ["From", "To", "Payload Type", "Key Fields"],
        ["Exam scan PDF\n(object store)", "PDF Splitter", "S3 URI + batch_id",
         "batch_id, student_id, pdf_s3_uri"],
        ["Rubric JSON\n(file upload)", "PDF Splitter\n+ all agents", "JSON object",
         "exam_id, questions[].criteria,\nquestions[].answer_region"],
        ["PDF Splitter", "Content Router", "PNG bytes + metadata",
         "student_id, question_id, png_bytes,\npage_num, crop_bbox_norm"],
        ["Content Router", "Nougat OCR", "PNG bytes", "question_id, png_bytes\n(text-heavy answers)"],
        ["Content Router", "Raw Image Path", "PNG bytes", "question_id, png_bytes\n(diagram/spatial answers)"],
        ["Nougat OCR", "Context Assembler", "Markdown + LaTeX string",
         "ocr_transcript: str\n(may include $...$ LaTeX blocks)"],
        ["Raw Image Path", "Context Assembler", "Base64 PNG string",
         "image_crop_b64: str\nbypass_ocr: true"],
        ["RAG Agent\n(ChromaDB)", "Context Assembler", "List of 3 past grades",
         "rag_examples: [{score, justification,\ntranscript}]"],
        ["Context Assembler", "Grader Agent", "Multimodal context object",
         "rubric, ocr_transcript, image_crop_b64,\nrag_examples, student_id, question_id"],
        ["Grader Agent\n(GPT-4o)", "Critic Agent\n+ Coordinator", "Structured JSON",
         "score, criteria_breakdown,\ntranscribed_snippets, justification"],
        ["Critic Agent\n(Haiku)", "Coordinator", "Objection JSON",
         "agrees: bool, objections: [...],\noverall_severity"],
        ["Coordinator\n(Haiku)", "Consensus check", "Resolution JSON",
         "final_score, resolution, criteria_final,\nrequires_human, iteration"],
        ["Consensus: YES", "PostgreSQL / MongoDB", "Full grade record",
         "All agent JSONs + final_score +\nplagiarism_flag"],
        ["Consensus: NO\n(< max iter)", "Coordinator\n(retry)", "Previous resolution",
         "Prior coordinator JSON appended\nto Critic context"],
        ["Consensus: NO\n(max iter hit)", "TA Dashboard\n(high priority)", "Escalation record",
         "requires_human=true +\nfull iteration history"],
        ["CLIP Detector\n(background)", "PostgreSQL", "Plagiarism flags",
         "pair: (student_id_a, student_id_b),\nsimilarity: float, flag: str"],
        ["PostgreSQL", "TA Dashboard", "Grade records (REST API)",
         "Paginated JSON; priority-sorted by\nrequires_human, plagiarism_flag"],
        ["TA Dashboard", "PostgreSQL", "Review actions",
         "reviewed_by, reviewed_at, human_override,\ncorrected_score, reason"],
        ["PostgreSQL", "Gradebook export", "Aggregated CSV / Excel",
         "student_id, total_score, per_question,\nflags, batch_agreement_rate"],
    ]

    flow_data = []
    for i, row in enumerate(flow_rows_raw):
        if i == 0:
            flow_data.append([Paragraph(c, flow_header) for c in row])
        else:
            styles_row = [flow_cell, flow_cell, flow_cell, flow_code]
            flow_data.append([Paragraph(str(row[j]), styles_row[j]) for j in range(4)])

    ft = Table(flow_data, colWidths=[avail*0.20, avail*0.20, avail*0.22, avail*0.38])
    ft.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  PURPLE),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, LIGHT_BG]),
        ("BOX",           (0,0),(-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(ft)
    story.append(PageBreak())

    # ── SECTION 8: TECH STACK ────────────────────────────────────────────────
    story.append(Paragraph("8. Technology Stack &amp; Rationale", styles["h1"]))
    story.extend(Rule(PURPLE, 1))

    stack_data = [
        ["Component", "Technology / Model", "Why This Choice", "Alternative"],
        ["VLM Grader", "GPT-4o Vision / Gemini Pro Vision",
         "State-of-art on mathematical handwriting OCR benchmarks; native function calling for structured JSON output",
         "Claude 3.5 Sonnet (vision capable; strong on reasoning tasks)"],
        ["Critic + Coordinator", "Claude Haiku / Llama 3-8B",
         "10-20x cheaper than GPT-4o; task is purely textual — no vision required; low latency for fast loop iterations",
         "Mistral-7B, Gemini Flash"],
        ["Handwriting OCR", "Nougat (Meta / facebook/nougat-base)",
         "Specifically trained on scientific documents with LaTeX; outputs structured Markdown+LaTeX directly",
         "Qwen-VL (stronger on general handwriting); Tesseract (traditional, lower accuracy)"],
        ["Vector Store (RAG)", "ChromaDB / pgvector",
         "ChromaDB: zero-config, Python-native; pgvector: reuses existing Postgres, strong for production",
         "Weaviate, Pinecone, Qdrant"],
        ["Embedding Model", "text-embedding-3-small (OpenAI) / all-mpnet-base-v2",
         "OpenAI: high quality, low cost, managed; all-mpnet: fully local, no external dependency",
         "Cohere embed-v3, BGE-large"],
        ["Visual Plagiarism", "CLIP (openai/clip-vit-base-patch32)",
         "Joint vision-language embedding space; visually similar images cluster regardless of text labels",
         "ResNet-50 embeddings, DINOv2"],
        ["ANN Index (large batches)", "FAISS (Facebook AI)",
         "Sub-millisecond approximate nearest-neighbour at scale; GPU-accelerated; battle-tested in production",
         "ScaNN, Hnswlib"],
        ["PDF Processing", "PyMuPDF (fitz)",
         "Fastest Python PDF library; precise bounding-box crop control; handles encrypted/compressed PDFs",
         "pdfplumber, pdf2image + Pillow"],
        ["Task Queue", "Celery + Redis",
         "Mature, battle-tested; supports per-task priority queues needed for requires_human escalation",
         "RQ, Dramatiq, Temporal"],
        ["Database", "PostgreSQL + JSONB",
         "JSONB columns store agent outputs flexibly; relational structure for cohort-level analytics; pgvector extension for vector ops",
         "MongoDB (document-native but weaker relational analytics)"],
        ["API Layer", "FastAPI (Python)",
         "Async-native; OpenAPI docs auto-generated; Pydantic validation matches JSON schemas used throughout pipeline",
         "Django REST Framework, Flask"],
        ["Object Storage", "AWS S3 / GCS",
         "Industry standard; presigned URLs enable secure direct access from TA dashboard browser",
         "MinIO (self-hosted S3-compatible)"],
    ]

    s_hdr = ParagraphStyle("sh", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)
    s_cel = ParagraphStyle("sc", fontName="Helvetica", fontSize=8.5, leading=12, textColor=DARK)
    s_data = []
    for i, row in enumerate(stack_data):
        s = s_hdr if i == 0 else s_cel
        s_data.append([Paragraph(c, s) for c in row])
    avail = W - 40*mm
    st2 = Table(s_data, colWidths=[avail*0.17, avail*0.22, avail*0.38, avail*0.23])
    st2.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  DARK),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, LIGHT_BG]),
        ("BOX",           (0,0),(-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(st2)
    story.append(PageBreak())

    # ── SECTION 9: IMPLEMENTATION ────────────────────────────────────────────
    story.append(Paragraph("9. Implementation Guide &amp; Integration Notes", styles["h1"]))
    story.extend(Rule(PURPLE, 1))

    story.append(Paragraph("9.1  Project Structure", styles["h2"]))
    story.append(Paragraph("""gradeops/
├── ingestion/
│   ├── pdf_splitter.py          # PyMuPDF-based page + question crop
│   ├── rubric_parser.py         # Rubric JSON schema validation (Pydantic)
│   └── content_router.py        # OCR vs. bypass routing logic
├── extraction/
│   ├── nougat_ocr.py            # Nougat / Qwen-VL OCR wrappers
│   ├── raw_image.py             # Base64 encoding for bypass path
│   └── context_assembler.py     # Merge OCR + image + rubric + RAG
├── tribunal/
│   ├── grader_agent.py          # GPT-4o / Gemini Vision API calls
│   ├── critic_agent.py          # Haiku / Llama adversarial critique
│   ├── rag_agent.py             # ChromaDB retrieval + embedding
│   └── coordinator.py           # Consensus check + arbitration loop
├── verify/
│   ├── consensus.py             # Consensus logic + retry budget
│   └── plagiarism/
│       ├── clip_embedder.py     # CLIP embedding pipeline
│       └── similarity.py        # Pairwise cosine + FAISS index
├── delivery/
│   ├── db_writer.py             # PostgreSQL JSONB persistence
│   ├── dashboard_api.py         # FastAPI REST endpoints for TA UI
│   └── export.py                # Gradebook CSV/Excel/LMS export
├── tasks/
│   └── celery_app.py            # Celery task definitions + routing
└── config/
    └── settings.py              # Model endpoints, thresholds, API keys""", styles["code"]))

    story.append(Paragraph("9.2  Environment Configuration", styles["h2"]))
    story.append(Paragraph("""# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...

# Model selection (swap without code changes)
GRADER_MODEL=gpt-4o
CRITIC_MODEL=claude-haiku-4-5-20251001
EMBEDDING_MODEL=text-embedding-3-small

# Thresholds
MAX_DEBATE_ITERATIONS=3
PLAGIARISM_THRESHOLD=0.92
RAG_TOP_K=3

# Infrastructure
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:pass@localhost/gradeops
CHROMA_PERSIST_PATH=./chroma_db
S3_BUCKET=gradeops-crops""", styles["code"]))

    story.append(Paragraph("9.3  Celery Task Chain", styles["h2"]))
    story.append(Paragraph(
        "Each question-level crop is processed as a Celery task chain. The chain enforces "
        "ordering (RAG retrieval → Grader → Critic → Coordinator) while allowing the "
        "plagiarism detection task to execute concurrently as an independent chord.",
        styles["body"]))

    story.append(Paragraph("""from celery import chain, chord, group
from tasks import (retrieve_rag, run_grader, run_critic,
                   run_coordinator, run_plagiarism, save_grade)

def process_question(student_id, question_id, context):
    # Main grading chain (sequential dependencies)
    grading_chain = chain(
        retrieve_rag.s(context),
        run_grader.s(),
        run_critic.s(),
        run_coordinator.s(max_iter=3),
        save_grade.s(student_id, question_id),
    )
    # Plagiarism runs in parallel (independent of grading chain)
    plagiarism_task = run_plagiarism.s(context["image_crop_b64"],
                                        question_id, student_id)
    # Launch both
    grading_chain.delay()
    plagiarism_task.delay()""", styles["code"]))

    story.append(PageBreak())

    # ── SECTION 10: DEPLOYMENT ───────────────────────────────────────────────
    story.append(Paragraph("10. Deployment Architecture &amp; Scaling", styles["h1"]))
    story.extend(Rule(PURPLE, 1))

    story.append(Paragraph("10.1  Per-Answer Cost Breakdown", styles["h2"]))

    cost_data = [
        ["Component", "Model / Service", "Approx. Cost per Answer", "Notes"],
        ["Grader Agent", "GPT-4o Vision", "$0.015–0.030",
         "Depends on image size (token count). Largest cost centre."],
        ["Critic Agent", "Claude Haiku", "$0.0003–0.001",
         "Text-only; very low token count. ~20-50x cheaper than Grader."],
        ["Coordinator", "Claude Haiku", "$0.0002–0.0005",
         "Structured JSON comparison; minimal tokens."],
        ["OCR (Nougat)", "Self-hosted GPU inference", "$0.001–0.003",
         "A100 GPU instance: ~100 crops/min. Amortised over batch."],
        ["CLIP Embedding", "Self-hosted GPU inference", "$0.0001–0.0005",
         "Shared GPU with Nougat; CLIP is very fast (~500 imgs/sec on A100)."],
        ["Embedding (RAG)", "text-embedding-3-small", "$0.00002–0.0001",
         "Very low cost. 512-dim vectors, short inputs."],
        ["Total (no retry)", "—", "~$0.017–0.035", "Roughly $17–35 per 1,000 answers."],
        ["Total (1 retry avg)", "—", "~$0.019–0.040",
         "Critic + Coordinator cost is marginal; retry overhead is small."],
    ]
    c_hdr = ParagraphStyle("ch", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)
    c_cel = ParagraphStyle("cc", fontName="Helvetica", fontSize=8.5, leading=12, textColor=DARK)
    c_num = ParagraphStyle("cn", fontName="Helvetica-Bold", fontSize=8.5, textColor=GREEN,
                           alignment=TA_CENTER)
    c_data = []
    for i, row in enumerate(cost_data):
        if i == 0:
            c_data.append([Paragraph(c, c_hdr) for c in row])
        else:
            c_data.append([
                Paragraph(row[0], c_cel),
                Paragraph(row[1], c_cel),
                Paragraph(row[2], c_num),
                Paragraph(row[3], c_cel),
            ])
    avail = W - 40*mm
    ct = Table(c_data, colWidths=[avail*0.22, avail*0.22, avail*0.18, avail*0.38])
    ct.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  DARK),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, LIGHT_BG]),
        ("BACKGROUND",    (0,-1),(-1,-1), GREEN_BG),
        ("BACKGROUND",    (0,-2),(-1,-2), GREEN_BG),
        ("BOX",           (0,0),(-1,-1), 0.5, BORDER),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(ct)
    story.append(Spacer(1, 10))

    story.append(Paragraph("10.2  Scaling Considerations", styles["h2"]))

    scale_items = [
        ("Horizontal Celery Workers",
         "Each Celery worker can process independent question crops in parallel. Scale worker count "
         "linearly with batch size. At 500 students × 10 questions = 5,000 crop tasks, 20 workers "
         "process a batch in under 30 minutes (assuming 3 min/task including retries)."),
        ("GPU Inference Server",
         "Host Nougat and CLIP on a shared A100/H100 instance behind an internal HTTP endpoint. "
         "Use NVIDIA Triton Inference Server for concurrent model serving and dynamic batching. "
         "For cloud deployment, use Modal, Replicate, or HuggingFace Inference Endpoints."),
        ("Vector Store Sharding",
         "ChromaDB collections should be partitioned by question_id to keep retrieval within "
         "a single question's answer space. For > 50k historical records per question, "
         "migrate to pgvector with HNSW index for sub-10ms retrieval."),
        ("LLM Rate Limits",
         "GPT-4o has tier-based RPM/TPM limits. Implement exponential backoff with jitter on "
         "all LLM API calls. For large batches, use OpenAI Batch API (async, 50% cost reduction) "
         "when real-time latency is not required."),
        ("Database Connection Pooling",
         "Use PgBouncer in transaction-pooling mode in front of PostgreSQL. Celery workers "
         "create many short-lived connections — pooling is essential at scale."),
    ]
    for title, body in scale_items:
        story.append(KeepTogether([
            Paragraph(title, styles["h3"]),
            Paragraph(body, styles["body"]),
        ]))

    story.append(Paragraph("10.3  Monitoring & Observability", styles["h2"]))
    story.append(Paragraph(
        "Instrument every agent call with OpenTelemetry traces. Key metrics to track: "
        "per-question Grader latency (p50/p95), Critic objection rate (objections per 100 answers), "
        "Coordinator override rate (how often the Critic's corrections are applied), "
        "consensus loop iteration distribution, plagiarism flag rate per batch, "
        "and TA review throughput (answers reviewed per TA per hour).",
        styles["body"]))

    story.append(Spacer(1, 6))
    story.append(info_box(
        "<b>Key success metrics for GradeOps Tribunal:</b>  "
        "Inter-agent agreement rate (target &gt;80% first-pass consensus), "
        "Grader-vs-human correlation on sampled answers (target r &gt; 0.92), "
        "Plagiarism false-positive rate (target &lt;2%), "
        "TA override rate (target &lt;5% of auto-approved records), "
        "End-to-end batch latency per 100 students (target &lt;15 min).",
        bg=PURPLE_BG, border=PURPLE))

    story.append(Spacer(1, 12))
    story.extend(Rule(DARK, 1))
    story.append(Paragraph(
        "GradeOps Tribunal — Final Project Technical Documentation  ·  "
        "5 Phases  ·  12+ Components  ·  3 AI Agents  ·  CLIP Plagiarism Detection",
        ParagraphStyle("footer_note", fontName="Helvetica", fontSize=8,
            textColor=MUTED, alignment=TA_CENTER)))

    # BUILD
    doc.build(story, onFirstPage=draw_cover, onLaterPages=on_page)
    print(f"PDF written to: {out}")

build()
