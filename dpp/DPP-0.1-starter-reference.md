# DPP 0.1 — Project Reference Notes

> **Reference source:** [Parse Protocol — Adopt](https://www.parseprotocol.com/#adopt)  
> **Local reference status:** This is a compact, project-maintained operational reference, not a verbatim copy of the full starter reference document. Keep the full adopted reference in this directory if exact rule-by-rule conformance is required.

## Purpose

Convert supplied document pages into faithful Markdown. The rendered page is the source of truth. Preserve printed content and its visible structure; do not add inferred information or silently correct source errors.

## Core transcription rules

- Transcribe all readable text, numbers, symbols, labels, footnotes, captions, annotations, stamps, and page numbers.
- Preserve spelling, capitalization, punctuation, language, script, identifiers, dates, units, and apparent errors.
- Mark only genuinely unreadable visible spans as `[illegible]`; do not fill clipped or obscured content from context.
- Follow visual reading order, including columns and grouped content.
- Join ordinary wrapped paragraph lines, but retain meaningful line breaks in addresses, verse, code, labels, and similar content.
- Preserve headings and their numbering. Keep captions and notes close to the content they describe.
- Preserve visible headers, footers, and page numbers. Document-wide recurring page furniture requires looking across the full document.
- Separate page transcriptions with a line containing only `---` when assembling a multi-page document.

## Tables

- Use HTML `<table>` markup rather than Markdown pipe tables.
- Preserve visible rows, columns, cell order, blank cells, headers, repeated labels, totals, notes, and footnotes.
- Do not invent headers, rows, values, or cell merges.
- When cell boundaries are uncertain, choose the least assumptive structure that retains visible relationships.

## Charts, diagrams, and formulas

- Preserve chart titles, axes, tick labels, legends, units, data labels, annotations, and readable values.
- Never estimate unreadable chart values or fabricate a data table.
- Preserve diagram labels and visible connections; do not invent nodes, arrows, order, or causality.
- Preserve mathematical operators, subscripts, superscripts, indices, and alignment as faithfully as possible. Do not guess unreadable symbols.

## Forms and visual marks

- Preserve form labels, values, options, and relationships. Use `[x]` and `[ ]` for visibly selected and unselected checkboxes.
- Represent signatures and logos conservatively; do not invent names or text.
- Preserve meaningful stamps, highlights, strike-throughs, underlining, handwritten annotations, and visible typography.

## Final review

Compare the transcription with the page image. Confirm that readable content and meaningful marks are included, reading order and relationships are preserved, and unsupported content has not been added.

## Implementation limitations

This project currently sends pages to the model independently. It does not yet implement document-wide pre-analysis, geometric bounding boxes, sidecar JSON, or a formal DPP conformance validator. Do not claim those capabilities until implemented and tested.
