# Document Parsing Protocol (DPP)

A Python/FastAPI starter for page-by-page document parsing with any vision model available through an OpenAI-compatible Chat Completions API. It aims to produce faithful Markdown transcripts guided by the project's DPP reference notes, including HTML tables and preservation of visible page content.

> **Important:** This is an implementation guided by a project-maintained reference, not a claim of formal certification or guaranteed protocol compliance. Validate output against the exact specification version adopted by your project.

## Features

- PDF, PNG, JPEG, and WebP uploads
- PDF rendering into ordered page images
- OpenAI-compatible vision parsing, one page at a time
- Markdown prose and HTML tables
- Configurable API endpoint, model, and credentials
- Upload size and page-count limits
- Structured response with per-page output and combined Markdown
- Health endpoint and basic tests

## Requirements

- Python 3.11+
- API key for your OpenAI-compatible endpoint

## Run locally

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1

pip install -r requirements-dev.txt
cp .env.example .env
# Configure OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL in .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs.

Run tests with `pytest`.

## Run with Docker

```bash
docker build -t dpp-openai-compatible .
docker run --rm -p 8000:8000 --env-file .env dpp-openai-compatible
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

See `.env.example`. Configure `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `OPENAI_MODEL` for your provider. The endpoint must support the OpenAI Chat Completions API with image input, and the selected model must accept images. Do not commit API keys.

## DPP reference and prompt

The adopted project reference notes are stored in `dpp/DPP-0.1-starter-reference.md`. The prompt loader in `app/dpp_prompt.py` reads this file at startup and combines it with application-specific instructions. Update the reference file to revise guidance without embedding the entire specification in Python source.

The reference file currently contains compact, project-maintained operational notes; it is **not** a verbatim copy of the full protocol source. Use the [Parse Protocol adoption page](https://www.parseprotocol.com/#adopt) to identify the official source and version. If exact rule-by-rule conformance is needed, store the exact adopted specification in `dpp/`, document its version and provenance, and add a formal validator.

The prompt is operational guidance, not a substitute for a formal validator. The current parser processes pages independently and does not implement document-wide pre-analysis, geometric bounding boxes, or sidecar JSON output.

## Production considerations

Before exposing this service publicly, add authentication/authorization, rate limiting, request timeouts, malware scanning, private object storage, retention/deletion policies, structured logging, metrics, and a durable queue for long-running documents. Model calls may be billed and subject to provider quotas. For sensitive documents, review your organization's data-processing and retention requirements before sending content to an external model.

Parsing is inherently fallible. Preserve source files when permitted, retain page-level output, and route low-confidence or malformed results for human review. Do not use arithmetic or domain assumptions to silently correct values in the source.
