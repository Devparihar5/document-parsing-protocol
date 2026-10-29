# Document Parsing Protocol (DPP)

A Python/FastAPI starter for page-by-page document parsing with Google's Gemini vision models. It aims to produce faithful Markdown transcripts guided by the project's DPP reference notes, including HTML tables and preservation of visible page content.

> **Important:** This is an implementation guided by a project-maintained reference, not a claim of formal certification or guaranteed protocol compliance. Validate output against the exact specification version adopted by your project.

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
# Windows PowerShell: .venv\\Scripts\\Activate.ps1

pip install -r requirements-dev.txt
cp .env.example .env
# Set GEMINI_API_KEY in .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

Run tests with `pytest`.

## Run with Docker

```bash
docker build -t dpp-gemini .
docker run --rm -p 8000:8000 --env-file .env dpp-gemini
```

## API

### `GET /health`

Returns service status.

### `POST /v1/parse`

Upload a PDF or image as multipart form field `file`.

Example:

```bash
curl -X POST http://127.0.0.1:8000/v1/parse \\
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

## DPP reference and prompt

The adopted project reference notes are stored in `dpp/DPP-0.1-starter-reference.md`. The prompt loader in `app/dpp_prompt.py` reads this file at startup and combines it with application-specific instructions. Update the reference file to revise guidance without embedding the entire specification in Python source.

The reference file currently contains compact, project-maintained operational notes; it is **not** a verbatim copy of the full protocol source. Use the [Parse Protocol adoption page](https://www.parseprotocol.com/#adopt) to identify the official source and version. If exact rule-by-rule conformance is needed, store the exact adopted specification in `dpp/`, document its version and provenance, and add a formal validator.

The prompt is operational guidance, not a substitute for a formal validator. The current parser processes pages independently and does not implement document-wide pre-analysis, geometric bounding boxes, or sidecar JSON output.

## Production considerations

Before exposing this service publicly, add authentication/authorization, rate limiting, request timeouts, malware scanning, private object storage, retention/deletion policies, structured logging, metrics, and a durable queue for long-running documents. Gemini calls are billed and may have provider quotas. For sensitive documents, review your organization's data-processing and retention requirements before sending content to an external model.

Parsing is inherently fallible. Preserve source files when permitted, retain page-level output, and route low-confidence or malformed results for human review. Do not use arithmetic or domain assumptions to silently correct values in the source.
