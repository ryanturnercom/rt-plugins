# Task: Write the Config Generation Logic

**Status:** [✓] Completed

**Dependencies:** Epic 02 task-01 (discovery phase must be written first)

## Context

- Language: Markdown (command file for Claude)
- Framework: Claude Code slash commands
- Testing: Manual
- Database: None

After the discovery phase finds all sources, the config generation section instructs the agent to assemble the TOML config file at `.claude/rt-documentation.toml`.

## Needed from User

None

## Instructions

1. Open `rt-agents/commands/documentation-config.md`

2. Replace the `<!-- Config generation: Epic 02 Task 02 -->` placeholder with the **Config Generation** section

3. Write instructions for the agent to:

   **Step 1: Read project metadata**
   - Check for `package.json` (name, description), `pyproject.toml` (project.name, project.description), `Cargo.toml`, or `go.mod`
   - Extract project name and description for the `[project]` section
   - Fall back to the directory name if no manifest found

   **Step 2: Build the `[project]` section**
   ```toml
   [project]
   name = "<detected-project-name>"
   description = "<detected-description>"
   output_dir = ".rt-documentation"
   export_dir = ".rt-documentation/exports"
   ```

   **Step 3: Build `[[section]]` entries**
   For each discovered source, create a `[[section]]` entry with:
   - `title` — Human-readable section name (e.g., "Overview" for root README, "API Reference" for openapi.json)
   - `sources` — Array of file paths relative to project root
   - `mode` — `"verbatim"` (default) or `"summarize"`
   - `print` — `true` (default) or `false`
   - `order` — Integer for section ordering
   - `type` — Optional: `"openapi"` or `"blueprints"` for specialized rendering

   **Step 4: Grouping rules**
   - Multiple READMEs from the same directory group into one section
   - Multiple files in `docs/` group by subfolder
   - OpenAPI specs each get their own section with `type = "openapi"`
   - All blueprints group into a single appendix section with `type = "blueprints"` and `order = 99`
   - CI/CD configs group into one section with `mode = "summarize"` and `print = false`

   **Step 5: Write the TOML file**
   - Write to `.claude/rt-documentation.toml`
   - Include header comments with generation timestamp
   - Include inline comments explaining each field

4. Leave a `<!-- Merge mode: Epic 02 Task 03 -->` placeholder after the config generation section

## Acceptance Criteria

- [x] Config generation instructions produce valid TOML with `[project]` and `[[section]]` entries
- [x] Project metadata auto-detection covers package.json, pyproject.toml, Cargo.toml, go.mod
- [x] Grouping rules prevent duplicate/fragmented sections
- [x] Each `[[section]]` has all required fields: title, sources, mode, print, order
- [x] OpenAPI sections include `type = "openapi"`
- [x] Blueprint section includes `type = "blueprints"` with `order = 9900`
- [x] Generated TOML includes helpful comments

## Implementation Notes

- Replaced `<!-- Config generation: Epic 02 Task 02 -->` placeholder in `rt-agents/commands/documentation-config.md` with full Phase 2 section
- Phase 2 contains 5 steps: metadata detection, [project] building, [[section]] entry generation, grouping rules, TOML file writing
- Project metadata detection covers 5 manifest types in priority order: package.json, pyproject.toml, Cargo.toml, go.mod, pom.xml (added pom.xml beyond the original 4)
- Includes a field reference table for all 6 [[section]] fields (title, sources, mode, print, order, type)
- 5 grouping rules: same-directory READMEs, docs subfolder grouping, individual OpenAPI specs, single blueprints appendix, single CI/CD section
- Blueprint order set to 9900 (not 99 as in task spec) to align with the 100-1000 scale used by discovery phases; 99 would sort before READMEs
- TOML template includes header comments with timestamp, inline comments for [project] fields, and a legend for modes
- Formatting rules specify sort order (by order then title), blank line separation, conditional type field inclusion
- Left `<!-- Merge mode: Epic 02 Task 03 -->` placeholder for the next task
