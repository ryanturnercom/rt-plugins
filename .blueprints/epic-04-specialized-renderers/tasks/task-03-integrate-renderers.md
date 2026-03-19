# Task: Integrate Renderers into Section Assembler

**Status:** [✓] Completed

**Dependencies:** Epic 04 tasks 01-02, Epic 03 task-05 (renderers and assembler must exist)

## Context

- Language: Python
- Framework: None
- Testing: Manual (end-to-end test with a project containing OpenAPI spec and blueprints)
- Database: None

Wire the OpenAPI and blueprint renderers into the section assembler so that sections with `type = "openapi"` or `type = "blueprints"` route to the correct renderer instead of the default markdown converter.

## Needed from User

None

## Instructions

1. Open `rt-agents/scripts/generate_docs.py`

2. Modify the `process_section_content()` function (from Epic 03 task-02) to check the section `type` field:

   ```python
   def process_section_content(section: dict) -> str:
       section_type = section.get("type", "")

       if section_type == "openapi":
           # Use OpenAPI renderer for each source file
           html_parts = []
           for source_path, content in section["sources_content"]:
               html_parts.append(render_openapi(content, source_path))
           return "\n".join(html_parts)

       elif section_type == "blueprints":
           # Use blueprint renderer — sources is a directory path
           source_dir = section["sources"][0]  # e.g., ".blueprints/"
           return render_blueprints(source_dir)

       else:
           # Default: markdown conversion
           html_parts = []
           for source_path, content in section["sources_content"]:
               html_parts.append(convert_markdown(content))
           return "<hr>".join(html_parts)
   ```

3. Update the source loader (Epic 03 task-01) to handle directory sources:
   - For `type = "blueprints"` sections where `sources` contains a directory path: don't try to read the directory as a file
   - Instead, pass the directory path through to `render_blueprints()` which handles its own file discovery

4. Test the integration by verifying that `main()` works with a config containing:
   - At least one standard markdown section
   - One `type = "openapi"` section (if a spec exists)
   - One `type = "blueprints"` section (if `.blueprints/` exists)

## Acceptance Criteria

- [x] Sections with `type = "openapi"` route to `render_openapi()`
- [x] Sections with `type = "blueprints"` route to `render_blueprints()`
- [x] Sections with no `type` (or empty type) route to default markdown conversion
- [x] Directory sources (for blueprints) don't cause file-read errors
- [x] End-to-end `python generate_docs.py` works with mixed section types
- [x] No regressions in standard markdown section rendering

## Implementation Notes

Two changes made to `rt-agents/scripts/generate_docs.py`:

1. **`load_sections()`** — Added a directory-source check for `type = "blueprints"` sections. When `src_path.is_dir()` is true, the path is recorded in `sources_paths` without attempting `read_text()`, with an empty placeholder in `sources_content`. This prevents file-read errors on directory sources.

2. **`process_section_content()`** — Now checks `section["type"]` before processing:
   - `"openapi"` → calls `render_openapi(content, filepath)` for each source
   - `"blueprints"` → calls `render_blueprints(source_dir)` with the directory path from `sources_paths[0]`
   - anything else (empty/missing) → falls through to the existing `_convert_source()` logic (no regression)
