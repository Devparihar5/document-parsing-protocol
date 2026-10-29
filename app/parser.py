from __future__ import annotations

import asyncio
import base64
import io
import logging

from openai import OpenAI
from PIL import Image

from app.config import Settings
from app.dpp_prompt import DPP_PAGE_TRANSCRIPTION_PROMPT
from app.rendering import RenderedPage

logger = logging.getLogger(__name__)


class OpenAIParser:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=settings.openai_timeout_seconds,
        )

    async def parse_pages(self, pages: list[RenderedPage]) -> list[dict[str, object]]:
        """Parse pages in order, limiting concurrent OpenAI-compatible requests."""
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
        encoded_image = base64.b64encode(image_buffer.getvalue()).decode("ascii")
        image_url = f"data:image/png;base64,{encoded_image}"

        response = self._client.chat.completions.create(
            model=self._settings.openai_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": DPP_PAGE_TRANSCRIPTION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                }
            ],
            temperature=0,
        )

        text = (
            response.choices[0].message.content.strip()
            if response.choices and response.choices[0].message.content
            else ""
        )
        if not text:
            logger.warning("OpenAI-compatible endpoint returned an empty transcription")
            raise RuntimeError("OpenAI-compatible endpoint returned an empty transcription.")
        return text
