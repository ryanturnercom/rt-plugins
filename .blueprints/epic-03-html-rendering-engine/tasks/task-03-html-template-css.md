# Task: HTML Template and CSS Styling

**Status:** [x] Completed

**Dependencies:** Epic 03 task-01 (script structure must exist)

## Context

- Language: Python, HTML, CSS
- Framework: None (inline template)
- Testing: Manual (open in browser)
- Database: None

Create the HTML template with all CSS inline in a `<style>` tag. Single built-in professional theme: dark sidebar, light content area. Must support `@media print` for clean PDF output.

## Needed from User

None

## Instructions

1. Create `rt-agents/templates/documentation.html` as a complete HTML template with Python string format placeholders.

2. HTML structure:
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <meta name="viewport" content="width=device-width, initial-scale=1.0">
       <title>{project_name} — Internal Documentation</title>
       <style>
           /* All CSS inline */
       </style>
   </head>
   <body>
       <div class="layout">
           <nav class="sidebar">
               {sidebar_html}
           </nav>
           <main class="content">
               {sections_html}
           </main>
       </div>
       <footer class="footer">
           {footer_html}
       </footer>
       <script>
           /* Sidebar search + scroll tracking + export UI */
       </script>
   </body>
   </html>
   ```

3. CSS theme — implement these styles:

   **Layout:**
   - `.layout` — CSS grid: sidebar 280px fixed, content fills remaining
   - `.sidebar` — Fixed position, full height, overflow-y auto, dark bg (#1a1a2e)
   - `.content` — Max-width 800px, centered with padding, white/off-white (#fafafa)

   **Sidebar:**
   - Light text (#e0e0e0) on dark background
   - Section links: padding 8px 16px, hover bg (#2a2a4e), border-left accent on active
   - Subsection links: indented, slightly smaller font, lighter color (#b0b0b0)
   - Search input: full-width, dark input bg (#2a2a4e), light text, subtle border
   - Appendix separator: thin border-top with margin

   **Content:**
   - Typography: `font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
   - `h1`: 2rem, border-bottom 1px solid #e0e0e0, padding-bottom 0.5rem
   - `h2`: 1.5rem, margin-top 2rem
   - `h3`: 1.25rem
   - `code` (inline): bg #f0f0f0, padding 2px 6px, border-radius 3px, monospace
   - `pre > code`: bg #f5f5f5, padding 16px, border-radius 6px, overflow-x auto, border 1px solid #e0e0e0
   - Tables: border-collapse, th bg #f5f5f5, td border-bottom 1px solid #e8e8e8
   - `.diagram-placeholder`: bg #fff3cd, border 1px dashed #ffc107, padding 12px, border-radius 4px, italic

   **Footer:**
   - Light bg (#f5f5f5), border-top, centered text, small font
   - Contains generation date and export button

   **Print button:**
   - Fixed bottom-right, circular, subtle shadow
   - Printer icon or "Print" text

4. CSS `@media print` rules:
   ```css
   @media print {
       .sidebar { display: none !important; }
       .content { max-width: 100%; margin: 0; padding: 0; }
       .footer { display: none !important; }
       .print-button { display: none !important; }
       .export-ui { display: none !important; }
       .collapsible-content { display: block !important; max-height: none !important; }
       .section[data-print="false"] { display: none !important; }
       h1, h2, h3 { page-break-after: avoid; }
       pre, table { page-break-inside: avoid; }
       body { font-size: 11pt; }
   }
   ```

5. Add a `load_template()` function in `generate_docs.py` that reads this template file and returns it as a string. Use the script's own directory to locate the template:
   ```python
   def load_template():
       template_path = Path(__file__).parent.parent / "templates" / "documentation.html"
       return template_path.read_text(encoding="utf-8")
   ```

## Acceptance Criteria

- [ ] HTML template is a valid, complete HTML5 document
- [ ] All CSS is inline in a `<style>` tag (no external stylesheets)
- [ ] Sidebar is dark (#1a1a2e), fixed, 280px wide
- [ ] Content area is white, max-width 800px, centered
- [ ] Typography uses system font stack with clear heading hierarchy
- [ ] Code blocks have subtle background and monospace font
- [ ] Tables are cleanly styled with borders
- [ ] Diagram placeholders have a distinct warning-style appearance
- [ ] `@media print` hides sidebar, footer, export UI, and expands collapsibles
- [ ] Print respects `data-print="false"` attribute to hide sections
- [ ] `load_template()` function loads the template relative to script location
- [ ] Page renders correctly in Chrome, Firefox, Edge

## Implementation Notes

- Template created at `rt-agents/templates/documentation.html` (10,899 chars)
- All CSS is inline in a single `<style>` tag -- no external dependencies
- All literal CSS curly braces doubled (`{{ }}`) for Python `.format()` compatibility
- Verified with a round-trip `.format()` test that all four placeholders (`{project_name}`, `{sidebar_html}`, `{sections_html}`, `{footer_html}`) resolve correctly
- `load_template()` added to `generate_docs.py` using `Path(__file__).parent.parent / "templates" / "documentation.html"` for script-relative resolution
- Print button uses Unicode printer icon (&#128438;) with `window.print()` onclick
- CSS grid layout: sidebar 280px fixed column, content fills remaining space
- Sidebar scrollbar styled for WebKit browsers
- `@media print` hides sidebar, footer, print button, export UI; expands collapsibles; respects `data-print="false"`; sets 11pt body font
