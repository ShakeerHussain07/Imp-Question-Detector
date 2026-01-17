import json
import re
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem,
    Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def json_to_pdf_with_images(data, image_base_dir):
    # ---------- Load JSON ----------
    print("loading json data for pdf generation........................")
    subject = data.get("subject", "Unknown Subject")

    # ---------- Clean subject for filename ----------
    safe_subject = re.sub(r"[^\w]+", "_", subject).strip("_")

    # ---------- Output directory ----------
    output_dir = Path(
        r"C:\Users\shiva\OneDrive\Desktop\mini 2.0\results"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    output_pdf = output_dir / f"{safe_subject}.pdf"

    part_a = sorted(
        data.get("PART_A", []),
        key=lambda x: x.get("frequency", 0),
        reverse=True
    )

    part_b = sorted(
        data.get("PART_B", []),
        key=lambda x: x.get("frequency", 0),
        reverse=True
    )

    # ---------- PDF Setup ----------
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    # ---------- Styles ----------
    subject_style = ParagraphStyle(
        "Subject",
        parent=styles["Title"],
        alignment=TA_CENTER
    )
    part_style = ParagraphStyle("Part", parent=styles["Heading2"])
    question_style = ParagraphStyle("Question", parent=styles["Normal"])

    # ---------- Subject ----------
    story.append(Paragraph(subject, subject_style))
    story.append(Spacer(1, 20))

    image_base_dir = Path(image_base_dir).resolve()

    # ---------- Helper ----------
    def add_part(title, questions):
        story.append(Paragraph(title, part_style))
        story.append(Spacer(1, 10))

        items = []

        for q in questions:
            block = []

            q_text = f"{q['question']} <b>(Frequency: {q['frequency']})</b>"
            block.append(Paragraph(q_text, question_style))
            block.append(Spacer(1, 8))

            images = q.get("images")
            if images and isinstance(images, list):
                for img in images:
                    img_path = (image_base_dir / img).resolve()
                    if img_path.exists():
                        block.append(
                            RLImage(
                                str(img_path),
                                width=350,
                                height=220,
                                kind="proportional"
                            )
                        )
                        block.append(Spacer(1, 12))

            items.append(ListItem(block))

        story.append(ListFlowable(items, bulletType="1"))
        story.append(Spacer(1, 20))

    # ---------- Parts ----------
    add_part("PART A", part_a)
    add_part("PART B", part_b)

    # ---------- Build PDF ----------
    final_style = ParagraphStyle(
    "FinalNote",
    parent=styles["Normal"],
    alignment=TA_CENTER,
    spaceBefore=30,
    fontSize=20)

    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>All the best for the exam!</b>", final_style))  
      
    doc.build(story)
    print(f"✅ PDF generated at: {output_pdf}")
    # ✅ RETURN FINAL PDF PATH
    return str(output_pdf.resolve())
