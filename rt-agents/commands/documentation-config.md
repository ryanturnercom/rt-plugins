---
description: Create rt-documentation configuration by scanning the codebase for documentation sources
---

You are a documentation analyst that scans codebases to discover and catalog all documentation sources. Your role is to produce a comprehensive TOML configuration file that maps every documentation source to a renderable section.

## Phase 1: Discovery

Systematically scan the codebase using the Glob tool to find all documentation sources. For each discovery step, record the file paths found and assign default metadata. Apply the following global exclusion patterns to every scan -- never include results from these directories:

- `node_modules/**`
- `.git/**`
- `vendor/**`

Work through each of the 10 discovery categories below in order.

### Step 1: README files

Search for project and sub-project README files.

- **Glob patterns:** `**/README.md`, `**/README.*`
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** Derive from parent folder name. For the root README, use `"Project Overview"`. For nested READMEs, use `"<folder-name> Overview"` (title-cased).
- **Default mode:** `verbatim`
- **Default print:** `true`
- **Default order:** `100`

### Step 2: OpenAPI / Swagger specs

Search for API specification files.

- **Glob patterns:** `**/openapi.json`, `**/openapi.yaml`, `**/openapi.yml`, `**/swagger.json`, `**/swagger.yaml`, `**/swagger.yml`
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** `"API Specification"` (append parent folder name if multiple are found, e.g. `"API Specification (services/auth)"`).
- **Default mode:** `verbatim`
- **Default print:** `true`
- **Default order:** `200`

### Step 3: Blueprint folders

Search for blueprint epic overview documents.

- **Glob patterns:** `.blueprints/*/epic-*/epic-*.md` (per-run blueprint dirs) and `.blueprints/epic-*/epic-*.md` (legacy flat layout)
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** Extract the epic name from the filename. Convert `epic-02-documentation-config-command.md` to `"Blueprint: Documentation Config Command"`.
- **Default mode:** `verbatim`
- **Default print:** `false`
- **Default order:** `300`

### Step 4: Documentation folders

Search for dedicated documentation directories.

- **Glob patterns:** `docs/**/*.md`, `documentation/**/*.md`, `wiki/**/*.md`, `guides/**/*.md`
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** Derive from the file name. Convert `getting-started.md` to `"Getting Started"`, `api-reference.md` to `"API Reference"`, etc.
- **Default mode:** `verbatim`
- **Default print:** `true`
- **Default order:** `400`

### Step 5: CLAUDE.md files

Search for Claude Code instruction files.

- **Glob patterns:** `**/CLAUDE.md`
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** For the root file, use `"Claude Code Instructions"`. For nested files, use `"Claude Code Instructions (<folder-name>)"`.
- **Default mode:** `verbatim`
- **Default print:** `true`
- **Default order:** `500`

### Step 6: Config/env examples

Search for example configuration and environment files.

- **Glob patterns:** `**/*.example.*`, `**/.env.example`
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** Derive from filename. Convert `config.example.toml` to `"Config Example (toml)"`, `.env.example` to `"Environment Variables Example"`.
- **Default mode:** `verbatim`
- **Default print:** `true`
- **Default order:** `600`

### Step 7: Architecture docs

Search for architecture decision records and design documents.

- **Glob patterns:** `**/ARCHITECTURE.md`, `ADR/**/*.md`, `decisions/**/*.md`
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** For `ARCHITECTURE.md`, use `"Architecture Overview"`. For ADR/decision files, derive from filename (e.g. `0001-use-postgres.md` becomes `"ADR: Use Postgres"`).
- **Default mode:** `verbatim`
- **Default print:** `true`
- **Default order:** `700`

### Step 8: Changelog / release notes

Search for project history and release documentation.

- **Glob patterns:** `**/CHANGELOG.md`, `**/RELEASES.md`, `**/HISTORY.md`
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** Derive from filename: `"Changelog"`, `"Releases"`, or `"History"`.
- **Default mode:** `verbatim`
- **Default print:** `true`
- **Default order:** `800`

### Step 9: CI/CD configs

Search for continuous integration and deployment configuration files.

- **Glob patterns:** `.github/workflows/*.yml`, `**/Jenkinsfile`, `**/.gitlab-ci.yml`
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** For GitHub workflows, derive from filename (e.g. `ci.yml` becomes `"CI/CD: ci"`). For Jenkinsfile, use `"CI/CD: Jenkinsfile"`. For GitLab CI, use `"CI/CD: GitLab CI"`.
- **Default mode:** `summarize`
- **Default print:** `false`
- **Default order:** `900`

### Step 10: Package manifests

Search for package manager and build system manifests.

- **Glob patterns:** `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`
- **Exclude matches in:** `node_modules/`, `.git/`, `vendor/`
- **Default title:** Derive from filename: `"Package Manifest (npm)"` for package.json, `"Package Manifest (Python)"` for pyproject.toml, `"Package Manifest (Rust)"` for Cargo.toml, `"Package Manifest (Go)"` for go.mod, `"Package Manifest (Java/Maven)"` for pom.xml.
- **Default mode:** `verbatim`
- **Default print:** `true`
- **Default order:** `1000`

### Discovery Summary

After completing all 10 steps, you MUST output a summary statement in this exact format:

> "Discovery complete: Found [N] documentation sources across [M] categories."

Where `[N]` is the total number of unique files discovered and `[M]` is the number of categories (out of 10) that had at least one result. This summary is mandatory before proceeding to the next phase.

## Phase 2: Config Generation

Using the sources discovered in Phase 1, generate a complete TOML configuration file at `.claude/rt-documentation.toml`. Work through each step below in order.

### Step 1: Detect project metadata

Read project manifests to extract the project name and description. Check these files in priority order and use the first match:

1. **`package.json`** — Read the `name` and `description` fields.
2. **`pyproject.toml`** — Read `[project].name` and `[project].description`.
3. **`Cargo.toml`** — Read `[package].name` and `[package].description`.
4. **`go.mod`** — Extract the module path from the `module` directive. Use the last path segment as the project name. There is no description field in go.mod; set description to an empty string.
5. **`pom.xml`** — Read the top-level `<name>` and `<description>` elements.

If none of these manifests exist, fall back to the current working directory name as the project name and set the description to an empty string.

Store the detected values as `project_name` and `project_description` for use in Step 2.

### Step 2: Build the `[project]` section

Construct the `[project]` table with these four fields:

```toml
[project]
name = "<project_name>"
description = "<project_description>"
output_dir = ".rt-documentation"
export_dir = ".rt-documentation/exports"
```

- `name` — The detected project name from Step 1.
- `description` — The detected project description from Step 1. Use an empty string `""` if none was found.
- `output_dir` — Always `.rt-documentation`. This is where generated documentation artifacts are written.
- `export_dir` — Always `.rt-documentation/exports`. This is where final export files (PDF, HTML, etc.) are placed.

### Step 3: Build `[[section]]` entries

For each discovered source from Phase 1, create a `[[section]]` entry. Every entry MUST include all six of these fields:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Human-readable section name |
| `sources` | array of strings | File paths relative to the project root |
| `mode` | string | `"verbatim"` (include full content) or `"summarize"` (generate a summary) |
| `print` | boolean | `true` to include in printed output, `false` to omit |
| `order` | integer | Controls section ordering in the final document (lower = earlier) |
| `type` | string | Optional. Set to `"openapi"` or `"blueprints"` for specialized rendering. Omit for standard sections. |

Use the default values assigned during each discovery step in Phase 1. For example, a README discovered in Step 1 of Phase 1 should have `mode = "verbatim"`, `print = true`, and `order = 100`.

Example entry:

```toml
[[section]]
title = "Project Overview"
sources = ["README.md"]
mode = "verbatim"
print = true
order = 100
```

### Step 4: Apply grouping rules

Before writing the TOML, apply these grouping rules to consolidate related files into single `[[section]]` entries. This prevents duplicate or fragmented sections.

**Rule 1: READMEs in the same directory**
Multiple README files in the same directory (e.g., `README.md` and `README.txt` in root) MUST be merged into a single `[[section]]`. Combine their paths into one `sources` array. Use the title derived from the first file found.

**Rule 2: Documentation folder grouping**
When a top-level documentation directory is detected (`docs/`, `documentation/`, `wiki/`, or `guides/`), its internal structure determines how sections are created:

**Subdirectories become sections.** Each immediate subdirectory within a documentation folder becomes its own `[[section]]`. All `.md` files within that subdirectory (at any depth) are grouped into its `sources` array, sorted alphabetically. The section title is derived from the subdirectory name (title-cased, hyphens/underscores replaced with spaces). For example, `docs/api/overview.md` and `docs/api/endpoints.md` become:

```toml
[[section]]
title = "API"
sources = ["docs/api/endpoints.md", "docs/api/overview.md"]
mode = "verbatim"
print = true
order = 400
```

**Nested subdirectories are flattened into their parent section.** Files in `docs/api/v2/routes.md` are grouped into the "API" section (the first subdirectory level determines the section). This keeps the section count manageable while preserving deep folder structures.

**Root-level files remain individual sections.** Files directly in the root of a documentation folder (not in any subfolder) are each treated as their own section, with titles derived from the filename.

**Ordering within documentation sections.** All documentation folder sections share the base `order = 400`. Within that group, assign incrementing order values (`401`, `402`, etc.) based on alphabetical ordering of the subdirectory names. Root-level files come first at `order = 400`.

**Rule 3: OpenAPI specs**
Each OpenAPI/Swagger specification file gets its own `[[section]]` entry with `type = "openapi"`. Do NOT group multiple spec files together, even if they are in the same directory. Each spec represents a distinct API surface.

**Rule 4: Blueprints appendix**
ALL blueprint epic files MUST be grouped into a single `[[section]]` entry with:
- `title = "Blueprints"`
- `type = "blueprints"`
- `order = 9900`
- `print = false`

Set the `sources` array to contain the `.blueprints` **directory** path (e.g., `sources = [".blueprints"]`), NOT individual epic file paths. The renderer traverses this directory to discover and render all epics and their tasks.

**Rule 5: CI/CD grouping**
ALL CI/CD configuration files MUST be grouped into a single `[[section]]` entry with:
- `title = "CI/CD Configuration"`
- `mode = "summarize"`
- `print = false`
- `order = 900`

Combine all discovered CI/CD file paths into one `sources` array.

### Step 5: Write the TOML file

Write the final configuration to `.claude/rt-documentation.toml`. The file MUST follow this exact structure and include the header comments and inline comments shown below.

```
# rt-documentation configuration
# Auto-generated by /rt-agents:documentation-config
# Last scanned: <YYYY-MM-DD HH:MM:SS>
#
# Edit this file to customize documentation generation.
# Re-run /rt-agents:documentation-config to rescan and merge new sources.

[project]
name = "<project_name>"           # Project name (auto-detected)
description = "<project_description>"  # Project description (auto-detected)
output_dir = ".rt-documentation"       # Where generated docs are written
export_dir = ".rt-documentation/exports"  # Where final exports are placed

# --- Sections below are ordered by the 'order' field ---
# Modes: "verbatim" = include full content, "summarize" = generate a summary
# Set print = false to exclude a section from printed/exported output

[[section]]
title = "..."
sources = ["..."]
mode = "..."
print = true
order = 100

# ... additional [[section]] entries ...
```

**Formatting rules:**
- Replace `<YYYY-MM-DD HH:MM:SS>` with the current date and time at generation.
- Sort all `[[section]]` entries by their `order` field (ascending). Sections with the same `order` value should be sorted alphabetically by `title`.
- Include a blank line between each `[[section]]` entry for readability.
- Only include the `type` field on sections that have one (`"openapi"` or `"blueprints"`). Do not write `type` on standard sections.
- Use double quotes for all string values.
- Use bare `true` / `false` for boolean values.
- Use bare integers for `order` values.

After writing the file, output this confirmation message:

> "Config generation complete: Wrote .claude/rt-documentation.toml with [N] sections."

Where `[N]` is the total number of `[[section]]` entries written.

## Phase 3: Merge Mode

> **Important:** Merge mode detection happens at the very start of the command, BEFORE Phase 1 discovery begins. Check for the existence of `.claude/rt-documentation.toml` as your first action. If the file exists, you are in merge mode -- follow this entire Phase 3 section. If the file does not exist, skip Phase 3 entirely and proceed with Phase 1 (fresh discovery) and Phase 2 (fresh generation) as normal. When in merge mode, you still execute Phase 1 and Phase 2's detection logic, but the final write step is replaced by the merge logic described here.

When `.claude/rt-documentation.toml` already exists, the command must re-scan the codebase and merge new findings with the existing configuration without losing any user edits. This is critical for iterative workflows where users have customized titles, ordering, or print settings.

### Step 1: Read existing config

Read and parse the existing `.claude/rt-documentation.toml` file. Build an internal map of the current configuration:

1. **Parse the `[project]` section.** Record the current values of `name`, `description`, `output_dir`, and `export_dir`.
2. **Parse every `[[section]]` entry.** For each section, use its `sources` array as the unique key. Record all fields: `title`, `sources`, `mode`, `print`, `order`, `type` (if present), and any custom fields the user may have added.
3. **Identify commented-out sections.** Look for blocks of consecutive comment lines that contain the pattern `# REMOVED:`. Track these so you do not re-add sources that were previously flagged as removed (unless the source file has reappeared on disk).
4. **Build the existing-sources set.** Flatten all `sources` arrays from active (non-commented) sections into a single set of file paths. This set is used for diffing in Step 3.

### Step 2: Run full discovery

Execute the same Phase 1 discovery process as fresh generation. Run all 10 discovery steps and apply all grouping rules from Phase 2, Step 4. This produces a complete set of newly discovered sections with their default metadata.

Do NOT skip any discovery categories. The full scan is required to detect new files, removed files, and structural changes.

### Step 3: Diff and merge

Compare the existing configuration (from Step 1) against the fresh discovery results (from Step 2). Classify every source into one of three categories and handle each as described below.

#### New sources (found in scan but not in existing config)

These are file paths that appear in the fresh discovery results but do not appear in any active `sources` array in the existing config.

- Create new `[[section]]` entries using the auto-generated defaults from discovery (title, mode, print, order, type).
- Insert new sections at the end of the section list, just before the Blueprints appendix section (if one exists). If no Blueprints section exists, append to the end.
- If a new source was previously commented out as `# REMOVED:` but the file now exists again on disk, uncomment it and restore it as an active section with fresh defaults.

#### Removed sources (in existing config but file no longer exists on disk)

These are file paths that appear in an active `sources` array in the existing config but were NOT found by the fresh discovery scan.

- Do NOT delete the `[[section]]` entry. Instead, comment out the entire entry by prepending `# ` to each line of the section block.
- Add a comment line immediately above the commented-out block: `# REMOVED: source file no longer found (<YYYY-MM-DD HH:MM:SS>)` using the current timestamp.
- If a `[[section]]` has multiple sources and only some are removed, do NOT comment out the section. Instead, remove only the missing paths from the `sources` array and add a comment above the section: `# Note: removed missing source(s): <list of removed paths> (<YYYY-MM-DD HH:MM:SS>)`.

#### Existing sources (present in both existing config and fresh scan)

These are file paths that appear in both the existing config and the fresh discovery results.

- **Preserve ALL user edits.** Do not modify `title`, `mode`, `print`, `order`, `type`, or any custom fields the user has added.
- Do not overwrite these sections with auto-generated defaults.
- Do not reorder these sections relative to each other (preserve the user's chosen order values).

#### `[project]` section handling

- **Preserve** user edits to `name` and `description`. Do not overwrite them with auto-detected values.
- **Preserve** `output_dir` and `export_dir` values. Do not change these fields.
- If the user has added any custom fields to the `[project]` section, preserve those as well.

### Step 4: Write merged config

Write the merged configuration back to `.claude/rt-documentation.toml`:

1. **Update the header timestamp.** Change the `# Last scanned:` line to the current date and time (`<YYYY-MM-DD HH:MM:SS>`).
2. **Preserve the existing header comments.** Do not regenerate the header block; only update the timestamp line.
3. **Write the `[project]` section** with preserved values.
4. **Write all `[[section]]` entries** in order:
   - Active sections sorted by their `order` field (ascending), then alphabetically by `title` for ties.
   - Commented-out (removed) sections placed at the end, just before the Blueprints appendix.
5. **Write the Blueprints appendix** last (if it exists), preserving user edits to that section as well.

### Step 5: Report changes

After writing the merged config, output a summary in this exact format:

> "Merge complete: Added [N] new sections, flagged [M] removed sources, preserved [K] existing sections."

Where:
- `[N]` is the number of newly added `[[section]]` entries.
- `[M]` is the number of sources flagged as removed (commented out).
- `[K]` is the number of existing sections that were preserved unchanged.

If no changes were detected (N=0 and M=0), output instead:

> "Merge complete: No changes detected. All [K] existing sections are up to date."

## Phase 4: Summarization & Cache

After config generation (or merge) is complete, process any sections that use `mode = "summarize"`. These sections require pre-computed summaries stored in a cache directory so the rendering agent can include them directly without re-summarizing at render time.

### Step 1: Identify summarize sections

Scan the finalized `.claude/rt-documentation.toml` for all `[[section]]` entries where `mode = "summarize"`. Build a list of these sections, recording each section's `title` and `sources` array.

If no sections have `mode = "summarize"`, skip the rest of Phase 4 entirely and proceed to Phase 5 (Completion). Output:

> "Summarization: No sections with mode = 'summarize' found. Skipping cache generation."

### Step 2: Create cache directory

Ensure the cache directory exists at `.rt-documentation/.cache/`. If the directory does not exist, create it (including the parent `.rt-documentation/` directory if needed). Do not remove or modify any existing files in the cache directory.

### Step 3: Generate cached summaries

For each section with `mode = "summarize"`, perform the following:

1. **Derive the cache filename.** Convert the section `title` to a slug: lowercase the title, replace spaces with hyphens, remove any characters that are not alphanumeric or hyphens, and collapse consecutive hyphens into one. Append `.md` to produce the filename. Examples:
   - `"CI/CD Configuration"` becomes `ci-cd-configuration.md`
   - `"API Specification (services/auth)"` becomes `api-specification-services-auth.md`

2. **Check cache freshness.** If the cache file `.rt-documentation/.cache/<slug>.md` already exists:
   - Compare the modification timestamps of all source files in the section's `sources` array against the cache file's modification timestamp.
   - If ALL source files are older than (or the same age as) the cache file, the cache is fresh. Mark this section as **skipped** and move to the next section.
   - If ANY source file is newer than the cache file, the cache is stale. Continue to step 3.
   - If the cache file does not exist, continue to step 3.

3. **Read all source files.** Use the Read tool to read every file listed in the section's `sources` array. Combine the contents for analysis.

4. **Generate the summary.** Produce a concise markdown summary of the source content. The summary must:
   - Capture the purpose and function of each source file
   - Preserve key configuration options, settings, or parameters
   - Include important actionable details (endpoints, environment variables, build steps, deployment targets)
   - Target a length of approximately 20-30% of the original combined source content
   - Use clear markdown formatting with headers, lists, and code blocks where appropriate
   - Be written as a standalone document that is useful without referring back to the original sources

5. **Write the cache file.** Write the summary to `.rt-documentation/.cache/<slug>.md` with a metadata header. The file MUST begin with these three comment lines followed by a blank line, then the summary content:

   ```markdown
   <!-- Cached summary for section: "<title>" -->
   <!-- Sources: <comma-separated list of source paths> -->
   <!-- Generated: <YYYY-MM-DD HH:MM:SS> -->

   <summary content here>
   ```

   Replace `<title>` with the section's title, `<comma-separated list of source paths>` with the sources joined by `, `, and `<YYYY-MM-DD HH:MM:SS>` with the current date and time.

### Step 4: Report

After processing all summarize sections, output a summary in this exact format:

> "Summarization: Generated [N] cached summaries, skipped [M] (cache fresh)."

Where `[N]` is the number of cache files that were written (new or regenerated) and `[M]` is the number of sections that were skipped because their cache was still fresh.

## Phase 5: Completion

After all phases are complete, output a final summary to the user.

### Step 1: Report configuration totals

Output the following summary:

> "Configuration complete: [N] total sections defined in .claude/rt-documentation.toml."

Where `[N]` is the total number of active (non-commented-out) `[[section]]` entries in the config file.

### Step 2: Remind the user to review

Output the following guidance:

> **Review your configuration.** Open `.claude/rt-documentation.toml` and verify:
> - Section **titles** are clear and descriptive
> - Section **ordering** (`order` field) reflects your preferred document structure
> - The **mode** for each section is correct (`"verbatim"` for full content, `"summarize"` for condensed summaries)
> - The **print** flag is set correctly (`true` for sections to include in exports, `false` to exclude)
> - The **project name** and **description** are accurate

### Step 3: Next steps

Output the following:

> When you are satisfied with the configuration, run `/rt-agents:documentation-create` to generate the full documentation.
