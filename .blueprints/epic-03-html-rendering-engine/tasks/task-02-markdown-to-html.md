# Task: Markdown-to-HTML Converter

**Status:** [x] Completed

**Dependencies:** Epic 03 task-01 (TOML parser and loader must exist)

## Context

- Language: Python
- Framework: `markdown` library
- Testing: Manual
- Database: None

Converts markdown source content to HTML fragments. Must handle standard markdown, code blocks (with language hints for styling), tables, and detect mermaid/plantuml blocks to replace with placeholders.

## Needed from User

None

## Instructions

1. Add a `convert_markdown(content: str) -> str` function to `generate_docs.py`

2. Use the `markdown` library with these extensions:
   ```python
   import markdown

   def convert_markdown(content: str) -> str:
       md = markdown.Markdown(extensions=[
           'tables',
           'fenced_code',
           'toc',
           'attr_list',
       ])
       return md.convert(content)
   ```

3. Add diagram placeholder detection:
   - Before passing to the markdown converter, scan for fenced code blocks with language `mermaid` or `plantuml`
   - Replace them with a styled placeholder div:
     ```html
     <div class="diagram-placeholder">
       <span class="diagram-icon">&#9633;</span>
       <span>Diagram (<code>mermaid</code>): see source file</span>
     </div>
     ```
   - Use a regex to find and replace: `` ```mermaid\n...\n``` `` and `` ```plantuml\n...\n``` ``

4. Add a `process_section_content(section: dict) -> str` function:
   - Takes a section dict from the loader
   - If section has multiple source files: concatenate with an `<hr>` separator between them
   - Convert each source's content via `convert_markdown()`
   - Return the combined HTML string

5. Handle non-markdown sources:
   - `.json`, `.yaml`, `.yml`, `.toml` files: wrap content in a `<pre><code>` block
   - `.html` files: pass through as-is
   - Everything else: treat as markdown

## Acceptance Criteria

- [x] Markdown converts to HTML with tables, fenced code, and TOC support
- [x] Mermaid code blocks are replaced with styled placeholders
- [x] PlantUML code blocks are replaced with styled placeholders
- [x] Multiple source files per section are concatenated with separators
- [x] Non-markdown files (JSON, YAML, TOML) render as code blocks
- [x] Function integrates cleanly with the section loader from task-01

## Implementation Notes

- Added `convert_markdown(content: str) -> str` using the `markdown` library with extensions: tables, fenced_code, toc, attr_list.
- Added `_DIAGRAM_RE` regex that detects `` ```mermaid `` and `` ```plantuml `` fenced blocks and replaces them with styled `<div class="diagram-placeholder">` elements **before** markdown parsing.
- Added `_convert_source(content, filepath)` that routes by file extension: `.json/.yaml/.yml/.toml` -> `<pre><code>` with HTML-escaped content and language class; `.html/.htm` -> pass-through; everything else -> `convert_markdown()`.
- Added `process_section_content(section: dict) -> str` that iterates `sources_content` + `sources_paths`, converts each via `_convert_source`, and joins with `<hr>`.
- Updated `load_sections()` to also populate `sources_paths` (list of file path strings) alongside `sources_content`, so downstream functions can determine file type.
