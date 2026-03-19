# Task: End-to-End Integration Test

**Status:** [✓] Completed

**Dependencies:** Epic 06 task-01 (command file must be written), all prior epics

## Context

- Language: Manual testing
- Framework: Claude Code slash commands
- Testing: End-to-end
- Database: None

Verify the complete workflow works end-to-end: from running `/documentation-config` on this very repository (rt-plugins) to generating HTML and PDF output.

## Needed from User

None

## Instructions

1. **Test `/documentation-config`** on the rt-plugins repo:
   - Run the command (or simulate it manually)
   - Verify it discovers: README files, CLAUDE.md, config examples, the docs/ folder
   - Verify `.claude/rt-documentation.toml` is generated with correct sections
   - Verify section ordering, modes, and print flags are sensible defaults

2. **Review the generated config:**
   - Open `.claude/rt-documentation.toml`
   - Verify all discovered sources map to logical sections
   - Check that TOML syntax is valid
   - Verify `[project]` section has correct name and description

3. **Test `python generate_docs.py`:**
   - Run the script from the project root
   - Verify it reads the config without errors
   - Verify `.rt-documentation/index.html` is created
   - Open the HTML file in a browser and check:
     - Sidebar shows all sections
     - Sidebar search filters correctly
     - Active section tracking works on scroll
     - Content renders markdown correctly
     - Diagram placeholders appear for any mermaid/plantuml blocks
     - Appendix section is separated visually
     - Export UI shows section checkboxes
     - Print button works (opens browser print dialog)

4. **Test `python generate_pdf.py`:**
   - Run the script from the project root
   - Verify a timestamped PDF is created in `.rt-documentation/exports/`
   - Open the PDF and check:
     - All printable sections are included
     - Non-printable sections (print=false) are excluded
     - Content is legible and well-formatted
     - No sidebar, search, or export UI in the PDF
     - Collapsible sections are fully expanded

5. **Test section filtering:**
   - Run: `python generate_pdf.py --sections "Overview,Architecture"`
   - Verify only those sections appear in the PDF

6. **Test merge mode:**
   - Manually edit `.claude/rt-documentation.toml` (change a title)
   - Re-run `/documentation-config`
   - Verify the edited title is preserved
   - Verify any new sources are added

7. **Document any issues found** as comments in the relevant task files or as new tasks if fixes are needed.

## Acceptance Criteria

- [ ] `/documentation-config` correctly discovers sources in the rt-plugins repo
- [ ] Generated TOML config is valid and has sensible defaults
- [ ] `generate_docs.py` produces a viewable HTML page
- [ ] Sidebar navigation, search, and scroll tracking work in browser
- [ ] `generate_pdf.py` produces a valid PDF
- [ ] PDF respects print flags from config
- [ ] Section filtering via `--sections` works
- [ ] Merge mode preserves user edits
- [ ] No crashes or unhandled errors in the full workflow
