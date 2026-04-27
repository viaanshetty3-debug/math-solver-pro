"""PDF processing - extract text and questions from uploaded PDFs."""

import re
import uuid
from pathlib import Path

import fitz  # PyMuPDF

from app.config import UPLOAD_DIR


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    doc = fitz.open(file_path)
    full_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        full_text.append(f"--- Page {page_num + 1} ---\n{text}")
    doc.close()
    return "\n\n".join(full_text)


def extract_questions_from_text(text: str) -> list[dict]:
    """Extract individual questions from extracted text."""
    questions = []

    # Common patterns for question numbering
    patterns = [
        r'(?:^|\n)\s*(?:Q(?:uestion)?\.?\s*)?(\d+)\s*[.):\]]\s*(.*?)(?=(?:\n\s*(?:Q(?:uestion)?\.?\s*)?\d+\s*[.):\]]|\Z))',
        r'(?:^|\n)\s*\((\d+)\)\s*(.*?)(?=(?:\n\s*\(\d+\)|\Z))',
        r'(?:^|\n)\s*(?:Problem|Exercise)\s+(\d+)\s*[.):]\s*(.*?)(?=(?:\n\s*(?:Problem|Exercise)\s+\d+|\Z))',
        r'(?:^|\n)\s*([a-z])\s*[.)]\s*(.*?)(?=(?:\n\s*[a-z]\s*[.)]|\Z))',
        r'(?:^|\n)\s*(?:Q(?:uestion)?)\s*(\d+)\s*[.):]*\s*(.*?)(?=(?:\n\s*Q(?:uestion)?\s*\d+|\Z))',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
        if matches and len(matches) >= 1:
            for match in matches:
                q_num = match[0]
                q_text = match[1].strip()
                if q_text and len(q_text) > 5:
                    questions.append({
                        "number": q_num,
                        "text": q_text,
                        "raw": f"{q_num}. {q_text}",
                    })
            if questions:
                break

    if not questions:
        # Fall back: treat each paragraph as a separate question
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip() and len(p.strip()) > 10]
        # Filter out page markers and headers
        paragraphs = [p for p in paragraphs if not p.startswith("--- Page")]
        for i, para in enumerate(paragraphs):
            questions.append({
                "number": str(i + 1),
                "text": para,
                "raw": para,
            })

    return questions


def extract_images_from_pdf(file_path: str) -> list[str]:
    """Extract images from PDF and save them."""
    doc = fitz.open(file_path)
    image_paths = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()

        for img_idx, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data = base_image["image"]
                image_ext = base_image["ext"]

                img_filename = f"extracted_{uuid.uuid4().hex[:8]}.{image_ext}"
                img_path = UPLOAD_DIR / img_filename
                with open(img_path, "wb") as f:
                    f.write(image_data)
                image_paths.append(str(img_path))
            except Exception:
                continue

    doc.close()
    return image_paths


def process_pdf(file_path: str) -> dict:
    """Process an uploaded PDF file - extract text, questions, and images."""
    text = extract_text_from_pdf(file_path)
    questions = extract_questions_from_text(text)
    images = extract_images_from_pdf(file_path)

    return {
        "full_text": text,
        "questions": questions,
        "images": images,
        "num_questions": len(questions),
        "num_images": len(images),
    }
