# Task: Write the documentation-create Command File

**Status:** [✓] Completed

**Dependencies:** Epic 05 (PDF export must be complete), Epic 03 (HTML engine must be complete)

## Context

- Language: Markdown (command file for Claude)
- Framework: Claude Code slash commands
- Testing: Manual (run the command against a project with a config)
- Database: None

The `documentation-create` command orchestrates the full rendering pipeline. Unlike the config command (which is a complex scanning agent), this command is relatively simple — it validates prerequisites and runs the Python scripts.

## Needed from User

None

## Instructions

1. Open `rt-agents/commands/documentation-create.md`

2. Replace the placeholder content with the full command:

```markdown
---
description: Generate HTML documentation and PDF export from rt-documentation config
---

You are a documentation renderer that generates a single-page HTML documentation site from a pre-configured TOML file. Your role is to validate the configuration, run the rendering scripts, and present the output to the user.

## Step 1: Validate Prerequisites

Check that `.claude/rt-documentation.toml` exists in the project root.

If it does NOT exist:
- Tell the user: "No documentation config found. Run `/documentation-config` first to scan your codebase and generate the config."
- STOP execution

If it DOES exist:
- Read the config file
- Extract `[project]` settings: name, output_dir, export_dir
- Count the number of `[[section]]` entries
- Tell the user: "Found config with [N] sections for project '[name]'."

## Step 2: Validate Source Files

For each `[[section]]` in the config:
- Check that all files in `sources` exist
- For `mode = "summarize"` sections, also check that the cache file exists at `.rt-documentation/.cache/<slug>.md`

Report any issues:
- Missing source files: "Warning: [file] not found, section '[title]' will be skipped"
- Missing cache files: "Warning: cache missing for '[title]', will use source verbatim"

If ALL sources are missing: "Error: No valid source files found. Check your config."

## Step 3: Generate HTML

Run the HTML rendering script:

```bash
python <path-to-rt-agents>/scripts/generate_docs.py
```

Where `<path-to-rt-agents>` is the directory containing the rt-agents plugin. Use the script's location relative to this command file.

Check the exit code:
- Success (0): continue to Step 4
- Failure (non-zero): show the error output and STOP

## Step 4: Generate PDF

Run the PDF export script:

```bash
python <path-to-rt-agents>/scripts/generate_pdf.py
```

Check the exit code:
- Success (0): continue to Step 5
- Failure (non-zero): show the error output but DO NOT stop (HTML was already generated successfully)
  - Common failure: weasyprint system dependencies missing
  - Tell user: "HTML generated successfully but PDF export failed. You can still use the HTML documentation and browser print."

## Step 5: Report Results

Tell the user:
- "Documentation generated successfully!"
- "HTML: {output_dir}/index.html"
- "PDF: {export_dir}/{timestamp}.pdf" (if PDF succeeded)
- "Open the HTML file in a browser to view your documentation."
- "Use the Export PDF button in the page to generate custom PDF exports."

## Step 6: Open Output

Attempt to open the HTML file:
- If VS Code/Cursor: suggest "Open in browser" or Live Server
- If CLI: `start {output_dir}/index.html` (Windows) or `open {output_dir}/index.html` (macOS) or `xdg-open` (Linux)
```

## Acceptance Criteria

- [x] Command file has correct frontmatter with description
- [x] Validates config exists before proceeding
- [x] Validates source files and cache files with clear warnings
- [x] Runs generate_docs.py and handles success/failure
- [x] Runs generate_pdf.py and handles success/failure gracefully (HTML success is independent)
- [x] Reports clear results with file paths
- [x] Attempts to open the HTML output
- [x] Errors are actionable (tells user what to do next)

## Implementation Notes

**Completed:** 2026-03-19

### Summary
Replaced placeholder frontmatter in `documentation-create.md` with the full 6-step command file covering prerequisite validation, source file validation, HTML generation, PDF generation, results reporting, and platform-aware output opening.

### Files Changed
- `rt-agents/commands/documentation-create.md` - Full command file with all 6 steps

### Key Decisions
- Used `PLUGIN_DIR` as a symbolic placeholder with explicit resolution instructions (navigate up one level from the command file location) rather than hardcoding an absolute path, since the plugin may be installed in different locations.
- Both Python scripts (`generate_docs.py`, `generate_pdf.py`) read config from `.claude/rt-documentation.toml` in the current working directory, so the command instructs running them from the project root.
- PDF failure is non-blocking: if HTML succeeds but PDF fails, the user is told about both the success and the failure with guidance on weasyprint system dependencies.
- Platform-aware opening: Windows (`start`), macOS (`open`), Linux (`xdg-open`), with VS Code/Cursor Live Server as an alternative suggestion.
