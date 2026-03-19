# Epic: Documentation-Create Command

**Status:** [✓] Completed

## Context

The `documentation-create` command is the "renderer" agent — it reads the TOML config and orchestrates the full rendering pipeline: invoking `generate_docs.py` for HTML and `generate_pdf.py` for PDF export. This is a command markdown file (instructions for Claude), similar to how `blueprint-execute` orchestrates blueprint tasks.

Dependencies: Epic 02 (config command), Epic 03-05 (rendering engine and PDF export scripts)

## Implementation Overview

Write the `documentation-create.md` command file that:
1. Validates the config exists
2. Runs the Python HTML generator
3. Runs the Python PDF generator
4. Opens the HTML output for the user
5. Reports results

## Tasks

- [✓] [task-01: Write the documentation-create command file](tasks/task-01-write-create-command.md)
- [✓] [task-02: End-to-end integration test](tasks/task-02-integration-test.md)
