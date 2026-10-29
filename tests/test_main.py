import httpx
from fastapi.testclient import TestClient
from openai import APITimeoutError
from PIL import Image

import app.main as main_module
from app.config import Settings
from app.rendering import RenderedPage


def test_parse_returns_gateway_timeout_when_provider_times_out(monkeypatch):
    class TimedOutParser:
        def __init__(self, settings):
            assert settings.openai_api_key == "test-key"

        async def parse_pages(self, pages):
            assert len(pages) == 1
            raise APITimeoutError(request=httpx.Request("POST", "https://models.example/v1/chat/completions"))

    monkeypatch.setattr(main_module, "OpenAIParser", TimedOutParser)
    monkeypatch.setattr(
        main_module,
        "render_document",
        lambda *args, **kwargs: [RenderedPage(1, Image.new("RGB", (1, 1)))],
    )
    monkeypatch.setattr(
        main_module, "get_settings", lambda: Settings(openai_api_key="test-key")
    )
    response = TestClient(main_module.app).post(
        "/v1/parse", files={"file": ("page.jpg", b"image", "image/jpeg")}
    )

    assert response.status_code == 504
    assert "Vision provider timed out" in response.json()["detail"]
