# Task: Write the Discovery Phase Instructions

**Status:** [✓] Completed

**Dependencies:** Epic 01 task-01 (placeholder command file must exist)

## Context

- Language: Markdown (command file for Claude)
- Framework: Claude Code slash commands
- Testing: Manual (run the command against a test project)
- Database: None

The discovery phase is the first section of `documentation-config.md`. It instructs the agent to systematically scan the codebase using Glob and Grep tools to find all documentation sources.

## Needed from User

None

## Instructions

1. Open `rt-agents/commands/documentation-config.md`

2. Replace the placeholder content with the full command file, starting with the frontmatter and role description:
   ```markdown
   ---
   description: Create rt-documentation configuration by scanning the codebase for documentation sources
   ---

   You are a documentation analyst that scans codebases to discover and catalog all documentation sources. Your role is to produce a comprehensive TOML configuration file that maps every documentation source to a renderable section.
   ```

3. Write the **Discovery Phase** section with these exact scan steps (each using Glob patterns):

   **Step 1: README files**
   - Pattern: `**/README.md`, `**/README.*`
   - Exclude: `node_modules/`, `.git/`, `vendor/`

   **Step 2: OpenAPI / Swagger specs**
   - Patterns: `**/openapi.json`, `**/openapi.yaml`, `**/openapi.yml`, `**/swagger.json`, `**/swagger.yaml`, `**/swagger.yml`

   **Step 3: Blueprint folders**
   - Pattern: `.blueprints/epic-*/epic-*.md`

   **Step 4: Documentation folders**
   - Patterns: `docs/**/*.md`, `documentation/**/*.md`, `wiki/**/*.md`, `guides/**/*.md`

   **Step 5: CLAUDE.md files**
   - Pattern: `**/CLAUDE.md`

   **Step 6: Config/env examples**
   - Patterns: `**/*.example.*`, `**/.env.example`

   **Step 7: Architecture docs**
   - Patterns: `**/ARCHITECTURE.md`, `ADR/**/*.md`, `decisions/**/*.md`

   **Step 8: Changelog / release notes**
   - Patterns: `**/CHANGELOG.md`, `**/RELEASES.md`, `**/HISTORY.md`

   **Step 9: CI/CD configs**
   - Patterns: `.github/workflows/*.yml`, `**/Jenkinsfile`, `**/.gitlab-ci.yml`

   **Step 10: Package manifests**
   - Patterns: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `pom.xml`

4. After each scan step, instruct the agent to:
   - Record found file paths
   - Extract a suggested section title from the file/folder name
   - Determine default `mode` (verbatim for most, summarize for CI/CD configs)
   - Determine default `print` flag (true for most, false for CI/CD and blueprints)
   - Assign an `order` value based on discovery category

5. End the discovery phase with a mandatory summary statement:
   > "Discovery complete: Found [N] documentation sources across [M] categories."

6. **Only write the discovery phase section** in this task. Leave a `<!-- Config generation: Epic 02 Task 02 -->` placeholder after it.

## Acceptance Criteria

- [x] `documentation-config.md` has correct frontmatter with description
- [x] Role description establishes the agent as a documentation analyst
- [x] All 10 discovery categories are covered with correct Glob patterns
- [x] Each category specifies: patterns, default title, default mode, default print, default order
- [x] Discovery phase ends with a summary statement requirement
- [x] Exclusion patterns for `node_modules/`, `.git/`, `vendor/` are specified

## Implementation Notes

- Wrote full Discovery Phase (Phase 1) to `rt-agents/commands/documentation-config.md`
- All 10 discovery categories implemented with exact Glob patterns from the spec
- Global exclusion patterns listed at the top of the phase, plus repeated per-step for clarity
- Order values assigned in increments of 100 (100-1000) matching category order
- CI/CD configs (Step 9) is the only category with `mode = summarize` and `print = false`
- Blueprints (Step 3) also have `print = false` but use `mode = verbatim`
- All other categories default to `mode = verbatim` and `print = true`
- Mandatory summary statement uses `[N]` and `[M]` placeholder format
- Task 02 placeholder comment `<!-- Config generation: Epic 02 Task 02 -->` placed at end of file
