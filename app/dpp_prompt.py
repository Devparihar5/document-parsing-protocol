"""Load the adopted DPP reference and build the page transcription prompt.

The reference is kept separately under dpp/ so specification updates do not
require editing application code. This remains prompt-level guidance, not a
formal conformance validator.
"""

from functools import lru_cache
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DPP_REFERENCE_PATH = PROJECT_ROOT / "dpp" / "DPP-0.1-starter-reference.md"

DPP_IMPLEMENTATION_INSTRUCTIONS = """
You are transcribing a rendered page from a document into Markdown.
Use the adopted DPP reference below as guidance. The supplied page image is the
source of truth: do not invent, normalize, correct, or infer missing content.
Return only the requested transcription, without commentary.

This application currently parses pages independently. Do not claim to perform
document-wide analysis or emit bounding boxes/sidecar JSON unless the application
implements those capabilities.
""".strip()


@lru_cache(maxsize=1)
def load_dpp_reference() -> str:
    """Read the adopted DPP reference once per process."""
    if not DPP_REFERENCE_PATH.is_file():
        raise FileNotFoundError(
            f"Adopted DPP reference not found: {DPP_REFERENCE_PATH}. "
            "Restore the reference file before starting the parser."
        )

    reference = DPP_REFERENCE_PATH.read_text(encoding="utf-8").strip()
    if not reference:
        raise ValueError(f"Adopted DPP reference is empty: {DPP_REFERENCE_PATH}")
    return reference


def build_page_transcription_prompt() -> str:
    """Combine stable application instructions with the versioned reference."""
    return (
        f"{DPP_IMPLEMENTATION_INSTRUCTIONS}\n\n"
        "# Adopted DPP reference\n\n"
        f"{load_dpp_reference()}"
    )


# Preserve the existing import contract for parser.py.
DPP_PAGE_TRANSCRIPTION_PROMPT = build_page_transcription_prompt()
