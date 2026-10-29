from pathlib import Path

from app.dpp_prompt import (
    DPP_PAGE_TRANSCRIPTION_PROMPT,
    DPP_REFERENCE_PATH,
    build_page_transcription_prompt,
    load_dpp_reference,
)


def test_dpp_reference_file_exists_and_is_not_empty() -> None:
    assert DPP_REFERENCE_PATH.is_file()
    assert load_dpp_reference().strip()


def test_page_prompt_includes_reference_and_implementation_guidance() -> None:
    prompt = build_page_transcription_prompt()

    assert "# Adopted DPP reference" in prompt
    assert "source of truth" in prompt
    assert load_dpp_reference() in prompt
    assert DPP_PAGE_TRANSCRIPTION_PROMPT == prompt
