from __future__ import annotations

import io
from dataclasses import dataclass

import pymupdf as fitz
from PIL import Image, UnidentifiedImageError


@dataclass(frozen=True)
class RenderedPage:
    page_number: int
    image: Image.Image


class DocumentError(ValueError):
    """Raised when an uploaded document cannot be safely prepared."""


SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}
PDF_MIME_TYPE = "application/pdf"


def render_document(
    data: bytes,
    content_type: str | None,
    *,
    dpi: int,
    max_pdf_pages: int,
) -> list[RenderedPage]:
    """Convert a supported PDF or image into ordered RGB page images."""
    normalized_type = (content_type or "").split(";")[0].strip().lower()

    if normalized_type == PDF_MIME_TYPE or data.startswith(b"%PDF-"):
        return _render_pdf(data, dpi=dpi, max_pdf_pages=max_pdf_pages)

    if normalized_type in SUPPORTED_IMAGE_TYPES or _looks_like_image(data):
        try:
            with Image.open(io.BytesIO(data)) as image:
                image.load()
                # This endpoint intentionally handles a single image page.
                return [RenderedPage(page_number=1, image=image.convert("RGB"))]
        except (UnidentifiedImageError, OSError) as exc:
            raise DocumentError("The uploaded image could not be decoded.") from exc

    raise DocumentError("Unsupported file type. Upload a PDF, PNG, JPEG, or WebP.")


def _looks_like_image(data: bytes) -> bool:
    return (
        data.startswith(b"\x89PNG\r\n\x1a\n")
        or data.startswith(b"\xff\xd8\xff")
        or (len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP")
    )


def _render_pdf(data: bytes, *, dpi: int, max_pdf_pages: int) -> list[RenderedPage]:
    try:
        document = fitz.open(stream=data, filetype="pdf")
    except (fitz.FileDataError, RuntimeError) as exc:
        raise DocumentError("The uploaded PDF is invalid or unreadable.") from exc

    with document:
        if document.is_encrypted:
            raise DocumentError("Password-protected PDFs are not supported.")
        if document.page_count == 0:
            raise DocumentError("The PDF contains no pages.")
        if document.page_count > max_pdf_pages:
            raise DocumentError(
                f"PDF has {document.page_count} pages; limit is {max_pdf_pages}."
            )

        scale = dpi / 72.0
        matrix = fitz.Matrix(scale, scale)
        pages: list[RenderedPage] = []
        for index, page in enumerate(document):
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            pages.append(RenderedPage(page_number=index + 1, image=image))
        return pages
