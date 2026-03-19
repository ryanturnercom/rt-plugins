# Task: Section Filtering for Selective Export

**Status:** [✓] Completed

**Dependencies:** Epic 05 task-01 (core PDF script must exist)

## Context

- Language: Python
- Framework: weasyprint, html parsing
- Testing: Manual
- Database: None

When the user passes `--sections` or the export UI sends a section list, the PDF should only include those sections. This requires modifying the HTML before rendering to PDF.

## Needed from User

None

## Instructions

1. Open `rt-agents/scripts/generate_pdf.py`

2. Add HTML manipulation to hide/remove sections before PDF rendering:
   ```python
   from html.parser import HTMLParser
   import re

   def filter_sections(html_content: str, selected_sections: list[str]) -> str:
       """Hide sections not in the selected list by setting data-print='false'."""
       # Read the config to map section titles to slugs
       config = load_config()
       sections = config.get("section", [])

       # Build a set of section IDs to include
       include_ids = set()
       for section in sections:
           title = section.get("title", "")
           if title in selected_sections:
               slug = title.lower().replace(" ", "-").replace("/", "-")
               include_ids.add(f"section-{slug}")

       # For each <section> tag, set data-print based on inclusion
       def replace_section(match):
           section_id = re.search(r'id="([^"]*)"', match.group(0))
           if section_id and section_id.group(1) not in include_ids:
               return match.group(0).replace('data-print="true"', 'data-print="false"')
           return match.group(0)

       return re.sub(r'<section[^>]*>', replace_section, html_content)
   ```

3. Alternative approach — inject CSS to hide non-selected sections:
   ```python
   def filter_sections_via_css(html_content: str, selected_sections: list[str]) -> str:
       """Inject CSS to hide non-selected sections for PDF rendering."""
       config = load_config()
       sections = config.get("section", [])

       hide_rules = []
       for section in sections:
           title = section.get("title", "")
           if title not in selected_sections:
               slug = title.lower().replace(" ", "-").replace("/", "-")
               hide_rules.append(f'#section-{slug} {{ display: none !important; }}')

       if hide_rules:
           css_block = f"<style>{''.join(hide_rules)}</style>"
           html_content = html_content.replace("</head>", f"{css_block}</head>")

       return html_content
   ```

4. Update `main()` to use filtering when `--sections` is provided:
   ```python
   def main():
       args = parse_args()
       config = load_config()
       # ... existing path setup ...

       html_content = html_path.read_text(encoding="utf-8")

       if args.sections:
           selected = [s.strip() for s in args.sections.split(",")]
           html_content = filter_sections_via_css(html_content, selected)
           # Write filtered HTML to a temp file for weasyprint
           temp_path = html_path.parent / "_export_temp.html"
           temp_path.write_text(html_content, encoding="utf-8")
           generate_pdf(str(temp_path), str(pdf_path))
           temp_path.unlink()  # Clean up temp file
       else:
           # No filter: use config print flags (already handled by print CSS)
           generate_pdf(str(html_path), str(pdf_path))
   ```

5. When no `--sections` flag: respect the `print` flag in config by ensuring the HTML has correct `data-print` attributes (these are set by generate_docs.py in Epic 03)

## Acceptance Criteria

- [x] `--sections "Overview,API Reference"` only includes those sections in the PDF
- [x] Sections not in the selected list are hidden via CSS injection
- [x] Temp HTML file is created for filtered rendering and cleaned up after
- [x] Without `--sections`, PDF respects `data-print` attributes from the HTML
- [x] Section title matching is case-sensitive and matches config titles exactly
- [x] Works correctly when all sections are selected (same as no filter)

## Implementation Notes

- Added `_slugify()` function to `generate_pdf.py` using the exact same logic as `generate_docs.py` (lowercase, strip non-alphanumeric except spaces/hyphens, collapse whitespace to hyphens, collapse multiple hyphens)
- Added `filter_sections_via_css()` that reads the TOML config, identifies sections not in the selected list, and injects `display: none !important` CSS rules before `</head>`
- Updated `main()` to: read HTML content, apply CSS filtering, write to `_export_temp.html` in the same directory, render PDF from temp file, and clean up with `try/finally` to ensure temp file is removed even on error
- When no `--sections` flag is provided, the HTML is rendered as-is (data-print attributes from config are already handled by print CSS)
- Added `import re` for the slugify regex operations
