# Epic: PDF Export & Print System

**Status:** [✓] Completed

## Context

The HTML documentation site (Epic 03-04) needs a robust PDF export system. Four mechanisms: CSS print stylesheet (already scaffolded in Epic 03), Python-generated PDF via weasyprint, floating print button, and an interactive export UI with section selection. The print CSS is already handled in Epic 03 task-03; this epic focuses on the Python PDF generator script.

Dependencies: Epic 03 (HTML rendering engine must produce output)

## Implementation Overview

Build `generate_pdf.py` as a standalone script that reads the generated HTML, optionally filters sections, and produces timestamped PDF files using weasyprint. The export UI JavaScript (Save PDF button) was scaffolded in Epic 03 task-05 — this epic implements the actual PDF generation it calls.

## Tasks

- [✓] [task-01: Build generate_pdf.py core script](tasks/task-01-generate-pdf-core.md)
- [✓] [task-02: Section filtering for selective export](tasks/task-02-section-filtering.md)
- [✓] [task-03: Output management and timestamping](tasks/task-03-output-management.md)
