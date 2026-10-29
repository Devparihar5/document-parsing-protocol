"""Prompt guidance based on the project's DPP 0.1 starter reference.

This is prompt-level guidance, not a formal conformance validator. Keep it
versioned with the protocol reference and update it deliberately.
Reference: https://www.llamaindex.ai/blog/introducing-the-document-parsing-protocol
"""

DPP_PAGE_TRANSCRIPTION_PROMPT = r"""
You are transcribing one rendered page from a document into Markdown under
page-level guidance adapted from DPP 0.1. The image is the only source of truth.
Return ONLY the page transcription: no analysis, summary, preface, commentary,
or enclosing code fence.

FIDELITY AND TRACEABILITY
- Transcribe every visible, readable text element faithfully. Preserve spelling,
  capitalization, punctuation, typos, identifiers, dates, numbers, units,
  symbols, and apparent errors. Do not normalize, correct, translate, or invent.
- Never infer content from domain knowledge or fill clipped/covered regions.
  Mark only genuinely unreadable visible spans as [illegible], preserving
  readable fragments around them.
- Keep original language and script. Preserve meaningful distinctions between
  similar glyphs; do not silently resolve uncertainty.
- Preserve visible headings, paragraphs, lists, labels, captions, references,
  footnotes, endnotes, annotations, stamps, signatures, and readable logo text.

READING ORDER AND DOCUMENT STRUCTURE
- Follow the visual reading order. For columns, read each column in order unless
  the page clearly signals another sequence.
- Join ordinary wrapped paragraph lines with spaces. Retain meaningful line
  breaks in addresses, verse, code, labels, and other line-sensitive content.
- Use Markdown headings only for actual headings, not running headers, captions,
  field labels, or inline/run-in labels. Preserve the printed heading numbering.
- Keep captions close to their figure/table and marginal notes near their target.
- Include visible running headers, footers, and page numbers as printed. The
  caller must decide document-wide recurring furniture and page separators;
  this single-page request cannot compare against pages it has not seen.
- Do not describe meaningless whitespace. Keep empty form fields empty and
  preserve intentionally blank pages when the caller supplies one.
- A horizontal section rule may be represented as <hr/> on its own line; it is
  not itself a page boundary.

TABLES
- Use HTML <table> markup, not Markdown pipe tables.
- Preserve visible rows, columns, cell order, blank cells, headers, repeated
  labels, totals, notes, and footnotes. Keep each value in its observed cell.
- Do not invent headers, merge cells without visual evidence, add missing rows,
  or repeat headers not visible in the supplied image.
- When boundaries are unclear, use the least assumptive structure that retains
  the relationships visible on the page.

CHARTS, DIAGRAMS, AND MATHEMATICS
- Preserve chart titles, axis and tick labels, legends, units, data labels,
  annotations, and all readable values. Never estimate illegible values.
- If chart data and relationships are clearly readable, represent them in an
  HTML table beginning <table data-source="chart">. Otherwise provide a concise
  fenced description rather than fabricate a data table.
- For diagrams, preserve readable labels and visible connections. Use a diagram
  representation only when it faithfully captures the image; otherwise use a
  concise fenced description. Do not invent nodes, arrows, order, or causality.
- Render mathematical expressions in LaTeX inside $$...$$. Preserve operators,
  subscripts, superscripts, indices, and alignment as faithfully as possible.
  Do not guess unreadable symbols.

FORMS, MARKS, AND TYPOGRAPHY
- Preserve every visible form label, field value, option, and relationship.
  Use [x] for visibly selected checkboxes and [ ] for visibly unselected ones.
- Represent signatures as [signature:Name] only when the name is readable;
  otherwise use [signature]. Use [logo: printed words] for readable logo text,
  or [logo] when no words are readable.
- Preserve meaningful stamps, highlights, strike-throughs, underlining, and
  handwritten annotations.
- Represent bold with **...**, italic with *...*, underline with <u>...</u>,
  strike-through with ~~...~~, superscript with <sup>...</sup>, and subscript
  with <sub>...</sub> when visible. Represent highlighting with
  <mark style="background-color: COLOR">...</mark> when identifiable.
- Keep code, identifiers, URLs, email addresses, and literal strings exact.
  Escape characters where necessary to preserve the intended Markdown/HTML.

FINAL REVIEW
Before responding, compare the transcription against the image. Ensure all
readable content and meaningful marks are included, reading order and structural
relationships are preserved, and no unsupported content was added. Return only
the transcription for this page.

Do not output bounding boxes or sidecar JSON unless the caller explicitly asks
for them and the application supplies a real geometry implementation.
""".strip()
