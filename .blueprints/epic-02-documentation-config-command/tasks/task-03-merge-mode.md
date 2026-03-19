# Task: Write the Merge Mode Logic

**Status:** [✓] Completed

**Dependencies:** Epic 02 task-02 (config generation must be written first)

## Context

- Language: Markdown (command file for Claude)
- Framework: Claude Code slash commands
- Testing: Manual
- Database: None

When `.claude/rt-documentation.toml` already exists, the config agent must re-scan the codebase and merge new findings without losing user edits. This is critical for iterative workflows.

## Needed from User

None

## Instructions

1. Open `rt-agents/commands/documentation-config.md`

2. Replace the `<!-- Merge mode: Epic 02 Task 03 -->` placeholder with the **Merge Mode** section

3. Write instructions that the agent must follow when a config file already exists:

   **Step 0: Detection**
   - At the very start of the command (before discovery), check if `.claude/rt-documentation.toml` exists
   - If YES → enter merge mode
   - If NO → proceed with fresh generation (skip this section)

   **Step 1: Read existing config**
   - Parse the existing TOML file
   - Build a map of existing sections keyed by their `sources` arrays
   - Note all user-modified fields (anything that differs from auto-generated defaults)

   **Step 2: Run full discovery**
   - Execute the same discovery phase as fresh generation
   - Produce a new set of discovered sources

   **Step 3: Diff and merge**
   - **New sources** (found in scan but not in existing config):
     - Add as new `[[section]]` entries at the end (before blueprints appendix)
     - Use auto-generated defaults for title, mode, print, order
   - **Removed sources** (in existing config but file no longer exists):
     - Comment out the `[[section]]` entry (prepend `#` to each line)
     - Add a comment: `# REMOVED: source file no longer found (<timestamp>)`
   - **Existing sources** (in both):
     - Preserve ALL user edits (title, mode, print, order, any custom fields)
     - Do NOT overwrite or modify these sections
   - **`[project]` section**:
     - Preserve user edits to name and description
     - Do not change output_dir or export_dir

   **Step 4: Write merged config**
   - Update the `# Last scanned:` timestamp in the header
   - Write the merged TOML back to `.claude/rt-documentation.toml`

   **Step 5: Report changes**
   - Print a summary: "Merge complete: Added [N] new sections, flagged [M] removed sources, preserved [K] existing sections."

4. Leave a `<!-- Summarization cache: Epic 02 Task 04 -->` placeholder after the merge section

## Acceptance Criteria

- [ ] Merge mode is triggered when `.claude/rt-documentation.toml` already exists
- [ ] New sources are added without disrupting existing sections
- [ ] Removed sources are commented out, not deleted
- [ ] All user edits to existing sections are preserved
- [ ] `[project]` section user edits are preserved
- [ ] Last scanned timestamp is updated
- [ ] A clear change summary is reported to the user

## Implementation Notes

- Added Phase 3: Merge Mode section to `rt-agents/commands/documentation-config.md` (lines 285-367)
- Merge mode detection note placed at the top of the section as a blockquote, emphasizing it runs BEFORE Phase 1
- Step 1 covers reading existing config: parsing `[project]`, all `[[section]]` entries, identifying commented-out `# REMOVED:` blocks, and building the existing-sources set
- Step 2 mandates running the full Phase 1 discovery (all 10 categories) plus Phase 2 grouping rules
- Step 3 handles the three-way diff: new sources (added with defaults before Blueprints appendix), removed sources (commented out with timestamp, partial removal for multi-source sections), existing sources (all user edits preserved)
- `[project]` section handling explicitly preserves all user fields including custom ones
- Step 4 writes merged config with updated timestamp, preserved header, correct ordering (active sorted by order/title, removed before Blueprints, Blueprints last)
- Step 5 provides two output formats: one for changes detected, one for no-changes case
- Left `<!-- Summarization cache: Epic 02 Task 04 -->` placeholder at the end for the next task
