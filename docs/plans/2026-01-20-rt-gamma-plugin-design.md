# rt-gamma Plugin Design

**Date:** 2026-01-20
**Status:** Approved

## Overview

Convert a standalone Gamma presentation generator tool into a Claude Code plugin. The plugin allows users to convert Markdown files to Gamma.app presentations via `/rt-gamma` slash command.

## Plugin Structure

```
rt-gamma/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── commands/
│   └── rt-gamma.md              # Main slash command
├── scripts/
│   ├── gamma_client.py          # API wrapper
│   ├── config.py                # Config loader for .claude/rt-gamma.toml
│   ├── generate.py              # Single file generation
│   └── batch.py                 # Batch folder generation
└── README.md                    # Documentation
```

## Command Interface

**Usage:**
- `/rt-gamma path/to/file.md` - Generate single presentation
- `/rt-gamma path/to/folder/` - Batch process all `*_presentation.md` files

**Auto-detection:** Command automatically determines if path is file or folder.

## Command Flow

### Step 1: Config Check
Check if `.claude/rt-gamma.toml` exists in the project root.

### Step 2: Missing Config Handler
If missing:
- Notify user: "No rt-gamma config found. Creating .claude/rt-gamma.toml"
- Show the file path
- Ask: "Would you like to set this up interactively or edit manually?"

**Interactive path:**
- Ask for API key (required)
- Ask for default theme (optional)
- Ask for text_mode preference
- Ask for image_source preference
- Write config file

**Manual path:**
- Create config with placeholder values
- Tell user to fill in api_key and run again
- Stop execution

### Step 3: Path Detection
Parse `$ARGUMENTS` to get the path:
- If path is a file → single generation
- If path is a folder → batch generation
- If path missing → ask user for path

### Step 4: Execute
- Single: `python scripts/generate.py "path/to/file.md"`
- Batch: `python scripts/batch.py "path/to/folder/"`

### Step 5: Report Results
Display: URL(s) generated, HTML file(s) created, any errors.

## Configuration

**File:** `.claude/rt-gamma.toml`

```toml
# Gamma API credentials (required)
api_key = ""

# Generation defaults (all optional)
theme = ""                        # Gamma theme ID
template = ""                     # Gamma template ID
text_mode = "preserve"            # generate | condense | preserve
image_source = "ai"               # ai | unsplash | giphy | pexels | none
card_split = "inputTextBreaks"    # respect --- markers for slides

# Batch settings
batch_pattern = "*_presentation.md"
```

## Script Behavior

### generate.py (single file)

**Input:** Path to markdown file
**Config:** Reads from `.claude/rt-gamma.toml`

**Process:**
1. Load config, validate API key exists
2. Read markdown file
3. Extract title (YAML frontmatter > H1 > filename)
4. Call Gamma API with config settings
5. Poll for completion (up to 2 min, check every 2 sec)
6. Create HTML redirect file next to source
7. Print JSON result

**Output format:**
```json
{"success": true, "url": "https://gamma.app/...", "html_path": "path/to/file.html"}
```

### batch.py (folder)

**Input:** Path to folder
**Config:** Reads from `.claude/rt-gamma.toml`

**Process:**
1. Find all `*_presentation.md` files recursively
2. Skip files that already have `.html` siblings
3. Process each file sequentially
4. Create HTML redirect for each success
5. Print JSON summary

**Output format:**
```json
{"total": 5, "success": 4, "failed": 1, "results": [...]}
```

### gamma_client.py
Thin wrapper around Gamma API (adapted from original `api_client.py`).

### config.py
Loads `.claude/rt-gamma.toml`, returns dict with defaults merged.

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No config file | Trigger setup wizard |
| Empty `api_key` | Error: "API key required. Run /rt-gamma to configure." |
| Invalid API key | Error from Gamma API, display message |
| File not found | Error: "File not found: {path}" |
| Not a .md file | Error: "Expected markdown file, got: {ext}" |
| Folder has no matches | Warning: "No *_presentation.md files found in {path}" |
| API timeout (>2min) | Error: "Generation timed out for: {file}" |
| API rate limit | Error with retry suggestion |

**Exit codes:**
- `0` = success
- `1` = error (message in stderr or JSON output)

## Marketplace Integration

**Update `.claude-plugin/marketplace.json`:**
```json
{
  "plugins": [
    { "name": "rt-voice", ... },
    {
      "name": "rt-gamma",
      "source": "./rt-gamma",
      "description": "Convert Markdown files to Gamma.app presentations",
      "version": "1.0.0"
    }
  ]
}
```

**Plugin metadata (`rt-gamma/.claude-plugin/plugin.json`):**
```json
{
  "name": "rt-gamma",
  "version": "1.0.0",
  "description": "Convert Markdown to Gamma.app presentations via slash command",
  "author": { "name": "rt" },
  "license": "MIT",
  "keywords": ["gamma", "presentations", "markdown", "slides"]
}
```

## Output Behavior

- **Single file:** Creates `.html` redirect file next to source markdown
- **Batch:** Creates `.html` redirect file for each successfully processed file
- **No speaker notes extraction** (simplified from original tool)

## Source Material

Original standalone tool location: `D:\_Brain\1 - Projects\AI Classes\gamma\`

Key files to adapt:
- `api_client.py` → `gamma_client.py`
- `cli.py` → `generate.py` (simplified, non-interactive)
- `batch.py` → `batch.py` (adapted for plugin)
- `config.py` → `config.py` (reads from `.claude/rt-gamma.toml`)
