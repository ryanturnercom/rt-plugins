# Task: Update README with New Commands

**Status:** [✓] Completed

**Dependencies:** None

## Context

- Language: Markdown
- Framework: None
- Testing: Manual
- Database: None

The existing `rt-agents/README.md` lists the blueprint commands. It needs to be updated with the two new documentation commands and their descriptions.

## Needed from User

None

## Instructions

1. Read the existing `rt-agents/README.md`

2. Add the new commands to the "Available Commands" section (or equivalent). Add entries for:
   - `/documentation-config` — "Scans the codebase for documentation sources (READMEs, OpenAPI specs, blueprints, etc.) and generates a structured TOML config at `.claude/rt-documentation.toml`. Supports merge mode on re-runs to preserve user edits."
   - `/documentation-create` — "Reads the documentation config and generates a single-page HTML documentation site at `.rt-documentation/index.html` with PDF export capability."

3. Add a brief "Documentation" section explaining the workflow:
   - Run `/documentation-config` first to scan and generate config
   - Edit the config to adjust sections, ordering, verbatim/summarize mode, and print flags
   - Run `/documentation-create` to render HTML and export PDF
   - Output lives in `.rt-documentation/`

4. Preserve existing README content and formatting style

## Acceptance Criteria

- [x] README lists both new commands with descriptions
- [x] README includes a documentation workflow section
- [x] Existing blueprint command documentation is unchanged
- [x] Formatting matches existing README style

## Implementation Notes

**Summary:** Updated `rt-agents/README.md` with two new documentation commands and a workflow section.

**Files changed:**
- `rt-agents/README.md` — Added `/rt-agents:documentation-config` and `/rt-agents:documentation-create` command entries in the Available Commands section, plus a new "Documentation" section explaining the three-step workflow (scan, edit, render).

**Key decisions:**
- Followed the existing formatting pattern: each command gets an H3 heading, description, Usage code block, and Output code block, separated by horizontal rules.
- Placed the new commands after `blueprint-execute` (the last existing command) and before the Configuration section.
- Added the "Documentation" workflow section between the new commands and the existing Configuration section to maintain logical flow.
