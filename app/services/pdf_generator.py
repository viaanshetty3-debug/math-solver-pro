"""Generate clean, formatted PDF solutions using ReportLab."""

import os
import uuid
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, inch, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.config import GENERATED_DIR


BLUE_PRIMARY = colors.HexColor("#2563eb")
BLUE_LIGHT = colors.HexColor("#eff6ff")
BLUE_DARK = colors.HexColor("#1e40af")
GRAY_DARK = colors.HexColor("#1e293b")
GRAY_MED = colors.HexColor("#475569")
GRAY_LIGHT = colors.HexColor("#f1f5f9")
GREEN = colors.HexColor("#16a34a")
GREEN_LIGHT = colors.HexColor("#f0fdf4")
RED = colors.HexColor("#dc2626")
BORDER_COLOR = colors.HexColor("#e2e8f0")


def get_styles():
    """Get custom paragraph styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="DocTitle",
        parent=styles["Title"],
        fontSize=26,
        leading=32,
        textColor=GRAY_DARK,
        spaceAfter=8,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    ))

    styles.add(ParagraphStyle(
        name="DocSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        textColor=GRAY_MED,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName="Helvetica",
    ))

    styles.add(ParagraphStyle(
        name="QuestionTitle",
        parent=styles["Heading2"],
        fontSize=16,
        leading=22,
        textColor=BLUE_DARK,
        spaceBefore=20,
        spaceAfter=10,
        fontName="Helvetica-Bold",
        borderWidth=0,
        borderPadding=0,
        borderColor=None,
        leftIndent=0,
    ))

    styles.add(ParagraphStyle(
        name="QuestionText",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        textColor=GRAY_DARK,
        spaceBefore=4,
        spaceAfter=12,
        fontName="Helvetica",
        backColor=BLUE_LIGHT,
        borderWidth=1,
        borderColor=BORDER_COLOR,
        borderPadding=10,
        leftIndent=10,
        rightIndent=10,
    ))

    styles.add(ParagraphStyle(
        name="StepTitle",
        parent=styles["Heading3"],
        fontSize=12,
        leading=16,
        textColor=BLUE_PRIMARY,
        spaceBefore=12,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    ))

    styles.add(ParagraphStyle(
        name="StepContent",
        parent=styles["Normal"],
        fontSize=10,
        leading=15,
        textColor=GRAY_DARK,
        spaceAfter=6,
        fontName="Helvetica",
        leftIndent=15,
    ))

    styles.add(ParagraphStyle(
        name="MathResult",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        textColor=GRAY_DARK,
        spaceAfter=8,
        fontName="Courier",
        backColor=GRAY_LIGHT,
        borderWidth=1,
        borderColor=BORDER_COLOR,
        borderPadding=8,
        leftIndent=20,
        rightIndent=20,
    ))

    styles.add(ParagraphStyle(
        name="AnswerBox",
        parent=styles["Normal"],
        fontSize=12,
        leading=18,
        textColor=GREEN,
        spaceBefore=8,
        spaceAfter=12,
        fontName="Helvetica-Bold",
        backColor=GREEN_LIGHT,
        borderWidth=2,
        borderColor=GREEN,
        borderPadding=12,
        leftIndent=10,
        rightIndent=10,
    ))

    styles.add(ParagraphStyle(
        name="Footer",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=GRAY_MED,
        alignment=TA_CENTER,
    ))

    return styles


def _clean_latex(text: str) -> str:
    """Remove LaTeX delimiters for PDF display."""
    text = text.replace("$$", "").replace("$", "")
    text = text.replace("\\left(", "(").replace("\\right)", ")")
    text = text.replace("\\left[", "[").replace("\\right]", "]")
    text = text.replace("\\frac", "frac")
    text = text.replace("\\cdot", "·")
    text = text.replace("\\times", "×")
    text = text.replace("\\pm", "±")
    text = text.replace("\\sqrt", "√")
    text = text.replace("\\pi", "π")
    text = text.replace("\\infty", "∞")
    text = text.replace("\\leq", "≤").replace("\\geq", "≥")
    text = text.replace("\\neq", "≠")
    text = text.replace("\\approx", "≈")
    text = text.replace("\\alpha", "α").replace("\\beta", "β")
    text = text.replace("\\gamma", "γ").replace("\\delta", "δ")
    text = text.replace("\\theta", "θ").replace("\\lambda", "λ")
    text = text.replace("\\sigma", "σ").replace("\\mu", "μ")
    text = text.replace("\\begin{cases}", "").replace("\\end{cases}", "")
    text = text.replace("\\\\", " | ")
    text = text.replace("\\", "")
    # Clean XML/HTML special chars for ReportLab
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return text


def _add_header_footer(canvas, doc):
    """Add header and footer to each page."""
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(BLUE_PRIMARY)
    canvas.setLineWidth(2)
    canvas.line(50, A4[1] - 45, A4[0] - 50, A4[1] - 45)

    # Header text
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(BLUE_PRIMARY)
    canvas.drawString(50, A4[1] - 38, "MathSolver Pro")

    # Footer
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY_MED)
    canvas.drawCentredString(A4[0] / 2, 25, f"Page {doc.page}")
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(50, 40, A4[0] - 50, 40)

    canvas.restoreState()


def generate_solution_pdf(
    title: str,
    solutions: list[dict],
    question_texts: list[str] = None,
    image_paths: list[str] = None,
    filename: str = None,
) -> str:
    """Generate a comprehensive solution PDF."""
    if not filename:
        filename = f"solutions_{uuid.uuid4().hex[:8]}.pdf"
    filepath = GENERATED_DIR / filename

    styles = get_styles()
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        topMargin=55,
        bottomMargin=50,
        leftMargin=50,
        rightMargin=50,
    )

    story = []

    # Title page
    story.append(Spacer(1, 40))
    story.append(Paragraph(title, styles["DocTitle"]))
    story.append(Paragraph("Detailed Step-by-Step Solutions", styles["DocSubtitle"]))

    # Summary table
    summary_data = [
        ["Total Questions", str(len(solutions))],
        ["Solved Successfully", str(sum(1 for s in solutions if s.get("success", False)))],
    ]
    summary_table = Table(summary_data, colWidths=[150, 100])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BLUE_LIGHT),
        ("TEXTCOLOR", (0, 0), (-1, -1), GRAY_DARK),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 30))

    # Solutions
    for i, solution in enumerate(solutions):
        q_num = i + 1
        q_text = ""
        if question_texts and i < len(question_texts):
            q_text = question_texts[i]

        # Question header
        story.append(Paragraph(f"Question {q_num}", styles["QuestionTitle"]))

        if q_text:
            clean_text = _clean_latex(q_text)
            story.append(Paragraph(clean_text, styles["QuestionText"]))

        # Steps
        steps = solution.get("steps", [])
        for step in steps:
            step_title = step.get("step", "")
            explanation = step.get("explanation", "")
            result = step.get("result", "")

            story.append(Paragraph(f"→ {step_title}", styles["StepTitle"]))

            if explanation:
                clean_explanation = _clean_latex(explanation)
                story.append(Paragraph(clean_explanation, styles["StepContent"]))

            if result:
                clean_result = _clean_latex(result)
                story.append(Paragraph(clean_result, styles["MathResult"]))

        # Final answer
        final_answer = solution.get("result", solution.get("simplified", ""))
        sol_list = solution.get("solutions", [])
        if sol_list:
            final_answer = ", ".join([str(s) for s in sol_list])

        if final_answer:
            clean_answer = _clean_latex(str(final_answer))
            story.append(Paragraph(f"Answer: {clean_answer}", styles["AnswerBox"]))

        # Include graph if available
        graph_path = solution.get("graph_path")
        if graph_path and os.path.exists(graph_path):
            try:
                img = Image(graph_path, width=400, height=280)
                story.append(Spacer(1, 10))
                story.append(img)
            except Exception:
                pass

        # Add image paths if provided
        if image_paths:
            for img_path in image_paths:
                if os.path.exists(img_path) and img_path.endswith((".png", ".jpg", ".jpeg")):
                    try:
                        img = Image(img_path, width=350, height=250)
                        story.append(Spacer(1, 10))
                        story.append(img)
                    except Exception:
                        pass

        story.append(Spacer(1, 20))

        # Page break between questions (except the last)
        if i < len(solutions) - 1:
            story.append(PageBreak())

    doc.build(story, onFirstPage=_add_header_footer, onLaterPages=_add_header_footer)
    return str(filepath)
