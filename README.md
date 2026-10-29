# Document Parsing Protocol (DPP) — Gemini implementation

A Python/FastAPI starter for page-by-page document parsing with Google's Gemini vision models. It aims to produce faithful Markdown transcripts guided by the DPP 0.1 reference, including HTML tables, page boundaries, and printed page numbers.

> **Important:** This is an implementation guided by the DPP reference, not a claim of formal certification or guaranteed protocol compliance. Always validate output against the version of the specification your project adopts.

## Features

- PDF, PNG, JPEG, and WebP uploads
- PDF rendering into ordered page images
- Gemini vision parsing, one page at a time
- Markdown prose and HTML tables
- Configurable Gemini model
- Upload size and page-count limits
- Structured response with per-page output and combined Markdown
- Health endpoint and basic tests

## Requirements

- Python 3.11+
- Google Gemini API key

## Run locally

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
# Set GEMINI_API_KEY in .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

## API

### `GET /health`

Returns service status.

### `POST /v1/parse`

Upload a PDF or image as multipart form field `file`.

Example:

```bash
curl -X POST http://127.0.0.1:8000/v1/parse \
  -F "file=@statement.pdf"
```

Optional query parameters:
- `include_page_results=true` (default): return each page result as well as combined Markdown.

Response shape:

```json
{
  "filename": "statement.pdf",
  "page_count": 2,
  "markdown": "...",
  "pages": [
    {"page_number": 1, "markdown": "..."}
  ]
}
```

## Configuration

See `.env.example`. The default model is configurable with `GEMINI_MODEL`; select a model available to your Google AI project. Do not commit API keys.

## Production considerations

Before exposing this service publicly, add authentication/authorization, rate limiting, request timeouts, malware scanning, private object storage, retention/deletion policies, structured logging, metrics, and a durable queue for long-running documents. Gemini calls are billed and may have provider quotas. For sensitive documents, review your organization's data-processing and retention requirements before sending content to an external model.

Parsing is inherently fallible. Preserve source files when permitted, retain page-level output, and route low-confidence or malformed results for human review. Do not use arithmetic or domain assumptions to silently “correct” values in the source.

## DPP guidance

The parser prompt is maintained in `app/dpp_prompt.py`. Place the exact DPP reference version adopted by your project in `references/` and review the prompt when the specification changes. The prompt is operational guidance, not a substitute for a formal validator.
