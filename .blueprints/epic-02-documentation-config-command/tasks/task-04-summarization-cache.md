# Task: Write the Summarization Cache Logic

**Status:** [x] Completed

**Dependencies:** Epic 02 task-03 (merge mode must be written first)

## Context

- Language: Markdown (command file for Claude)
- Framework: Claude Code slash commands
- Testing: Manual
- Database: None

When a section has `mode = "summarize"`, the config agent should generate a condensed summary of the source content and cache it in `.rt-documentation/.cache/`. The create agent (renderer) reads from cache instead of re-summarizing at render time.

## Needed from User

None

## Instructions

1. Open `rt-agents/commands/documentation-config.md`

2. Replace the `<!-- Summarization cache: Epic 02 Task 04 -->` placeholder with the **Summarization & Cache** section

3. Write instructions for the summarization workflow:

   **Step 1: Identify summarize sections**
   - After config generation/merge, scan the TOML for sections with `mode = "summarize"`

   **Step 2: Create cache directory**
   - Ensure `.rt-documentation/.cache/` exists (create if missing)

   **Step 3: For each summarize section**
   - Read all source files listed in the section's `sources` array
   - Generate a concise summary that captures:
     - Purpose/function of the source
     - Key configuration options or settings
     - Important details (endpoints, variables, steps)
   - Target length: ~20-30% of original, preserving all actionable information
   - Write the summary as markdown to `.rt-documentation/.cache/<slug>.md`
     - Slug derived from section title: lowercase, spaces → hyphens (e.g., "CI/CD Pipeline" → `ci-cd-pipeline.md`)
   - Add a header comment to the cache file:
     ```markdown
     <!-- Cached summary for section: "<title>" -->
     <!-- Sources: <source list> -->
     <!-- Generated: <timestamp> -->
     ```

   **Step 4: Skip if cache is fresh**
   - If a cache file already exists AND the source files haven't been modified since the cache was written (compare timestamps), skip re-summarizing
   - If source files are newer than cache, regenerate

   **Step 5: Report**
   - "Summarization: Generated [N] cached summaries, skipped [M] (cache fresh)."

4. End the command file with a **Completion** section:
   - Report total sections in config
   - Remind user to review `.claude/rt-documentation.toml` and adjust titles, ordering, mode, and print flags
   - Tell user to run `/documentation-create` when ready to render

## Implementation Notes

- Added Phase 4 (Summarization & Cache) with 4 steps: identify summarize sections, create cache directory, generate cached summaries with freshness detection, and report results
- Added Phase 5 (Completion) with 3 steps: report totals, remind user to review config, and direct to `/documentation-create`
- Cache files are written to `.rt-documentation/.cache/<slug>.md` with metadata header comments (title, sources, timestamp)
- Slug derivation: lowercase, spaces to hyphens, strip non-alphanumeric/hyphen chars, collapse consecutive hyphens
- Cache freshness uses file modification timestamp comparison: skip if all sources are older than cache
- Summary target is ~20-30% of original content, preserving actionable information
- The `documentation-config.md` command file is now complete with no remaining placeholders

## Acceptance Criteria

- [ ] Summarize sections produce cached markdown files in `.rt-documentation/.cache/`
- [ ] Cache file naming uses slugified section titles
- [ ] Cache files include header comments with metadata
- [ ] Fresh cache detection skips unnecessary re-summarization
- [ ] Summary quality targets ~20-30% of original length
- [ ] Command ends with clear next-step guidance for the user
- [ ] The complete `documentation-config.md` file is coherent when all 4 tasks are assembled
