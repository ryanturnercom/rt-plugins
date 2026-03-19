# Epic: HTML Rendering Engine

**Status:** [✓] Completed

## Context

The core Python script (`generate_docs.py`) that reads the TOML config, processes all source files, and assembles a single-page HTML documentation site. This is the heart of the `documentation-create` command — the script it invokes to do the actual rendering work.

Dependencies: Epic 01 (scaffolding must exist)

## Implementation Overview

Build `generate_docs.py` with:
1. TOML config parsing and source file validation
2. Markdown-to-HTML conversion
3. HTML template with inline CSS (dark sidebar, light content, professional theme)
4. Two-level sidebar navigation with search
5. Section assembly with proper ordering
6. Auto-install of dependencies on first run

## Tasks

- [x] [task-01: TOML parser and source file loader](tasks/task-01-toml-parser-source-loader.md)
- [x] [task-02: Markdown-to-HTML converter](tasks/task-02-markdown-to-html.md)
- [x] [task-03: HTML template and CSS styling](tasks/task-03-html-template-css.md)
- [x] [task-04: Sidebar navigation and search](tasks/task-04-sidebar-nav-search.md)
- [x] [task-05: Section assembler and output writer](tasks/task-05-section-assembler.md)
