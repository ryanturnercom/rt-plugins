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
python "PLUGIN_DIR/scripts/generate_docs.py"
```

Where `PLUGIN_DIR` is the directory containing the rt-agents plugin. To resolve this path, find the location of this command file and navigate up one level to the plugin root. For example, if this command file is at `/path/to/rt-agents/commands/documentation-create.md`, then `PLUGIN_DIR` is `/path/to/rt-agents`.

Use the Bash tool to run the script. The script reads `.claude/rt-documentation.toml` from the current working directory, so run it from the project root.

Check the exit code:
- Success (0): continue to Step 4
- Failure (non-zero): show the error output and STOP

## Step 4: Generate PDF

Run the PDF export script:

```bash
python "PLUGIN_DIR/scripts/generate_pdf.py"
```

Use the same `PLUGIN_DIR` resolution as Step 3.

Check the exit code:
- Success (0): continue to Step 5
- Failure (non-zero): show the error output but DO NOT stop (HTML was already generated successfully)
  - Common failure: weasyprint system dependencies missing
  - Tell user: "HTML generated successfully but PDF export failed. You can still use the HTML documentation and browser print-to-PDF."

## Step 5: Report Results

Tell the user:
- "Documentation generated successfully!"
- "HTML: {output_dir}/index.html"
- "PDF: {export_dir}/{timestamp}.pdf" (if PDF succeeded)
- "Open the HTML file in a browser to view your documentation."
- "Use the Export PDF button in the page to generate custom PDF exports."

## Step 6: Open Output

Attempt to open the HTML file in the user's browser using a platform-appropriate command:

- **Windows:** `start {output_dir}/index.html`
- **macOS:** `open {output_dir}/index.html`
- **Linux:** `xdg-open {output_dir}/index.html`

If running inside VS Code or Cursor, suggest using the "Open in Browser" context menu or the Live Server extension as an alternative.
