# Epic: Documentation-Config Command

**Status:** [✓] Completed

## Context

The `documentation-config` command is the "smart" agent — it scans the entire codebase to discover documentation sources, extracts knowledge and metadata, and generates a comprehensive TOML config file. It must support merge mode on re-runs to preserve user edits while incorporating new findings.

This is a command markdown file (instructions for Claude), not a Python script. The agent executing this command will use Claude's built-in tools (Glob, Grep, Read) to scan the codebase.

## Implementation Overview

Write the full `documentation-config.md` command file with:
1. Codebase discovery phase (10+ source types)
2. TOML config generation with `[[section]]` entries
3. Merge mode logic for re-runs
4. Summarization + cache writing for `mode = "summarize"` sections

## Tasks

- [✓] [task-01: Write the discovery phase instructions](tasks/task-01-discovery-phase.md)
- [✓] [task-02: Write the config generation logic](tasks/task-02-config-generation.md)
- [✓] [task-03: Write the merge mode logic](tasks/task-03-merge-mode.md)
- [✓] [task-04: Write the summarization cache logic](tasks/task-04-summarization-cache.md)
