from __future__ import annotations

import logging
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from app.config import get_settings
from app.parser import GeminiParser
from app.rendering import DocumentError, render_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Parsing Protocol — Gemini",
    description=(
        "Page-by-page document transcription guided by DPP 0.1. "
        "Output is model-generated and should be validated before downstream use."
    ),
    version="0.1.0",
)


class ParsedPage(BaseModel):
    page_number: int
    markdown: str


class ParseResponse(BaseModel):
    filename: str
    page_count: int
    markdown: str
    pages: list[ParsedPage] | None = None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/parse", response_model=ParseResponse)
async def parse_document(
    file: Annotated[UploadFile, File(description="PDF, PNG, JPEG, or WebP document")],
    include_page_results: Annotated[bool, Query()] = True,
) -> ParseResponse:
    settings = get_settings()

    filename = file.filename or "upload"
    max_bytes = settings.max_upload_mb * 1024 * 1024
    try:
        # Read one byte beyond the limit to reject oversized uploads.
        data = await file.read(max_bytes + 1)
    finally:
        await file.close()

    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.max_upload_mb} MB upload limit.",
        )

    try:
        rendered_pages = render_document(
            data,
            file.content_type,
            dpi=settings.pdf_render_dpi,
            max_pdf_pages=settings.max_pdf_pages,
        )
    except DocumentError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc

    try:
        parser = GeminiParser(settings)
        page_results = await parser.parse_pages(rendered_pages)
    except Exception as exc:
        logger.exception("Document parsing failed for %s", filename)
        # Avoid returning provider internals or uploaded content in the API response.
        raise HTTPException(
            status_code=502,
            detail="Document parsing failed. Check service logs and provider configuration.",
        ) from exc

    combined_markdown = "\n\n---\n\n".join(
        str(page["markdown"]) for page in page_results
    )
    pages = (
        [ParsedPage(**page) for page in page_results]
        if include_page_results
        else None
    )
    return ParseResponse(
        filename=filename,
        page_count=len(page_results),
        markdown=combined_markdown,
        pages=pages,
    )
