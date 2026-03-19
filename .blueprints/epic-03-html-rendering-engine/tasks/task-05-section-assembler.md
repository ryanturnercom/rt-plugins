# Task: Section Assembler and Output Writer

**Status:** [x] Completed

**Dependencies:** Epic 03 tasks 01-04 (all prior engine tasks)

## Context

- Language: Python
- Framework: None
- Testing: Manual
- Database: None

The final piece of `generate_docs.py` — takes all processed sections, injects them into the HTML template, and writes the output file. Also generates the footer with export UI.

## Needed from User

None

## Instructions

1. Add a `generate_sections_html(sections: list) -> str` function:
   - For each section, wrap the converted HTML content in:
     ```html
     <section class="section" id="section-{slug}" data-print="{print_flag}">
       <h1 class="section-heading">{title}</h1>
       {converted_html_content}
     </section>
     ```
   - Add `<hr class="section-divider">` between sections
   - Before appendix sections (order >= 99), add:
     ```html
     <div class="appendix-divider">
       <span>Appendix</span>
     </div>
     ```

2. Add a `generate_footer_html(project_name: str, sections: list) -> str` function:
   - Generation date in format: "Generated YYYY-MM-DD"
   - Attribution: "rt-agents documentation"
   - Print button (floating):
     ```html
     <button class="print-button" onclick="window.print()" title="Print">&#128438;</button>
     ```
   - Export UI dropdown:
     ```html
     <div class="export-ui">
       <button class="export-toggle">Export PDF &#9660;</button>
       <div class="export-panel" style="display:none;">
         <h3>Select sections to export:</h3>
         <!-- For each section -->
         <label>
           <input type="checkbox" data-section="section-{slug}" {checked}> {title}
         </label>
         <!-- checked if section.print is true -->
         <div class="export-actions">
           <button class="export-save-pdf">Save PDF</button>
           <button class="export-print">Print</button>
         </div>
       </div>
     </div>
     ```

3. Add export UI JavaScript (inline):
   ```javascript
   // Toggle export panel
   document.querySelector('.export-toggle').addEventListener('click', function() {
       const panel = document.querySelector('.export-panel');
       panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
   });

   // Print with section selection
   document.querySelector('.export-print').addEventListener('click', function() {
       // Set data-print attributes based on checkboxes
       document.querySelectorAll('.export-panel input[type="checkbox"]').forEach(cb => {
           const section = document.getElementById(cb.dataset.section);
           if (section) section.setAttribute('data-print', cb.checked ? 'true' : 'false');
       });
       window.print();
   });

   // Save PDF button — calls Python script via placeholder message
   document.querySelector('.export-save-pdf').addEventListener('click', function() {
       const selected = [];
       document.querySelectorAll('.export-panel input[type="checkbox"]:checked').forEach(cb => {
           selected.push(cb.nextElementSibling?.textContent || cb.dataset.section);
       });
       alert('To generate PDF, run:\\npython generate_pdf.py --sections "' + selected.join(',') + '"');
   });
   ```

4. Add the `assemble_and_write(sections, project_config)` function:
   - Load the HTML template via `load_template()`
   - Generate sidebar HTML
   - Generate sections HTML
   - Generate footer HTML
   - Fill template placeholders: `{project_name}`, `{sidebar_html}`, `{sections_html}`, `{footer_html}`
   - Create output directory if it doesn't exist
   - Write to `{output_dir}/index.html`
   - Print: "Documentation written to {output_dir}/index.html"

5. Update `main()` to call the full pipeline:
   ```python
   def main():
       config = parse_config()
       sections = load_sections(config)
       process_all_sections(sections)  # markdown conversion
       assemble_and_write(sections, config["project"])
   ```

## Acceptance Criteria

- [x] All sections are wrapped in `<section>` tags with correct IDs and data-print attributes
- [x] Appendix divider appears before order >= 99 sections
- [x] Footer shows generation date and attribution
- [x] Print button is floating bottom-right
- [x] Export UI has checkboxes for each section, pre-checked based on config print flag
- [x] Export print button applies section selection before printing
- [x] Save PDF button shows the CLI command to run
- [x] Output directory is created if it doesn't exist
- [x] `index.html` is written as a complete, valid HTML file
- [x] Running `python generate_docs.py` end-to-end produces a viewable HTML page

## Implementation Notes

- **`generate_sections_html(sections)`**: Iterates sections, wraps each in `<section class="section" id="section-{slug}" data-print="{flag}">` with an `<h1 class="section-heading">`. Inserts `<hr class="section-divider">` between sections and an appendix divider `<div>` before the first section with `order >= 99`.
- **`generate_footer_html(project_name, sections)`**: Builds a footer with generation date (YYYY-MM-DD via `date.today().isoformat()`), "rt-agents documentation" attribution, and an export UI dropdown. Each section gets a checkbox pre-checked based on `print_flag`. Includes Save PDF and Print action buttons.
- **Export UI JavaScript**: Added three IIFE blocks to `documentation.html` template:
  1. Toggle export panel visibility on `.export-toggle` click
  2. Print button sets `data-print` attributes on sections based on checkbox state, then calls `window.print()`
  3. Save PDF button collects checked section labels and shows a CLI command via `alert()`
- **`assemble_and_write(sections, project_config)`**: Loads template via `load_template()`, generates sidebar/sections/footer HTML, fills template with `.format()`, creates output directory with `mkdir(parents=True, exist_ok=True)`, writes `index.html`.
- **`main()`**: Full pipeline: `parse_config()` -> `load_sections()` -> process each section with `process_section_content()` and `extract_subsections()` -> `assemble_and_write()`.
- All JS in template uses double-brace `{{` / `}}` escaping for Python `.format()` compatibility.
