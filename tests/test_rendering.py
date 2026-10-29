import io

import pymupdf as fitz
import pytest
from PIL import Image

from app.rendering import DocumentError, render_document


def test_render_png_as_single_page():
    image = Image.new("RGB", (100, 80), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    pages = render_document(
        buffer.getvalue(),
        "image/png",
        dpi=72,
        max_pdf_pages=10,
    )

    assert len(pages) == 1
    assert pages[0].page_number == 1
    assert pages[0].image.size == (100, 80)


def test_render_pdf_pages_in_order():
    pdf = fitz.open()
    pdf.new_page(width=100, height=100)
    pdf.new_page(width=100, height=100)
    data = pdf.tobytes()
    pdf.close()

    pages = render_document(
        data,
        "application/pdf",
        dpi=72,
        max_pdf_pages=10,
    )

    assert [page.page_number for page in pages] == [1, 2]


def test_reject_unsupported_type():
    with pytest.raises(DocumentError):
        render_document(
            b"not a document",
            "text/plain",
            dpi=72,
            max_pdf_pages=10,
        )


def test_enforce_pdf_page_limit():
    pdf = fitz.open()
    pdf.new_page()
    pdf.new_page()
    data = pdf.tobytes()
    pdf.close()

    with pytest.raises(DocumentError, match="limit"):
        render_document(
            data,
            "application/pdf",
            dpi=72,
            max_pdf_pages=1,
        )
