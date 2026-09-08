from pathlib import Path

import pymupdf

from aied.config import PDF_MAX_CHARACTERS


def extract_pdf_text(pdf_path: Path) -> str:
    doc = pymupdf.open(pdf_path)
    chunks: list[str] = []
    current_length = 0

    for page_index, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            chunk = f"\n--- PAGE {page_index + 1} ---\n{text}"
            chunks.append(chunk)
            current_length += len(chunk)

        if current_length >= PDF_MAX_CHARACTERS:
            break

    return "\n".join(chunks)[:PDF_MAX_CHARACTERS]
