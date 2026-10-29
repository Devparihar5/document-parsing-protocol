import base64
import io
from types import SimpleNamespace
from typing import Any

from PIL import Image
import pytest

import app.parser as parser_module
from app.config import Settings
from app.dpp_prompt import DPP_PAGE_TRANSCRIPTION_PROMPT
from app.parser import OpenAIParser


def test_parser_uses_openai_compatible_chat_completions(monkeypatch):
    image = Image.new("RGB", (20, 10), "white")
    captured: dict[str, Any] = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured["client"] = kwargs
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self.create_completion)
            )

        def create_completion(self, **kwargs):
            captured["request"] = kwargs
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="  Parsed page  ")
                    )
                ]
            )

    monkeypatch.setattr(parser_module, "OpenAI", FakeOpenAI)
    parser = OpenAIParser(
        Settings(
            openai_api_key="test-key",
            openai_base_url="https://models.example/v1",
            openai_model="vision-model",
        )
    )

    assert parser._parse_page_sync(image) == "Parsed page"
    assert captured["client"] == {
        "api_key": "test-key",
        "base_url": "https://models.example/v1",
        "timeout": 300,
    }

    request = captured["request"]
    assert request["model"] == "vision-model"
    assert request["temperature"] == 0
    content = request["messages"][0]["content"]
    assert content[0] == {
        "type": "text",
        "text": DPP_PAGE_TRANSCRIPTION_PROMPT,
    }
    image_data_url = content[1]["image_url"]["url"]
    encoded_image = image_data_url.removeprefix("data:image/png;base64,")
    decoded_image = Image.open(io.BytesIO(base64.b64decode(encoded_image)))
    assert decoded_image.size == image.size


def test_parser_rejects_empty_completion(monkeypatch):
    def create_empty_completion(**kwargs):
        assert kwargs
        return SimpleNamespace(choices=[])

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.options = kwargs
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=create_empty_completion)
            )

    monkeypatch.setattr(parser_module, "OpenAI", FakeOpenAI)
    parser = OpenAIParser(Settings(openai_api_key="test-key"))

    with pytest.raises(
        RuntimeError,
        match="OpenAI-compatible endpoint returned an empty transcription.",
    ):
        parser._parse_page_sync(Image.new("RGB", (1, 1), "white"))
