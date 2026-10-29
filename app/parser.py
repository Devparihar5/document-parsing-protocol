from __future__ import annotations

import asyncio
import io
import logging

from google import genai
from google.genai import types
from PIL import Image

from app.config import Settings
from app.dpp_prompt import DPP_PAGE_TRANSCRIPTION_PROMPT
from app.rendering import RenderedPage

logger = logging.getLogger(__name__)


class GeminiParser:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(
                timeout=settings.gemini_timeout_seconds * 1000
            ),
        )

    async def parse_pages(self, pages: list[RenderedPage]) -> list[dict[str, object]]:
        """Parse pages in order, limiting concurrent Gemini requests."""
        semaphore = asyncio.Semaphore(2)

        async def parse_one(page: RenderedPage) -> dict[str, object]:
            async with semaphore:
                markdown = await asyncio.to_thread(self._parse_page_sync, page.image)
                return {"page_number": page.page_number, "markdown": markdown}

        # Gather preserves input order, even when individual calls finish out of order.
        return await asyncio.gather(*(parse_one(page) for page in pages))

    def _parse_page_sync(self, image: Image.Image) -> str:
        image_buffer = io.BytesIO()
        image.save(image_buffer, format="PNG")
        image_part = types.Part.from_bytes(
            data=image_buffer.getvalue(),
            mime_type="image/png",
        )

        response = self._client.models.generate_content(
            model=self._settings.gemini_model,
            contents=[DPP_PAGE_TRANSCRIPTION_PROMPT, image_part],
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="text/plain",
            ),
        )

        text = (response.text or "").strip()
        if not text:
            logger.warning("Gemini returned an empty transcription for a page")
            raise RuntimeError("Gemini returned an empty transcription.")
        return text
