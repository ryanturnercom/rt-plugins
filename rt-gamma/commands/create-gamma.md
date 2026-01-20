---
description: Convert Markdown to Gamma.app presentations
---

Convert a Markdown file or folder of files to Gamma.app presentations.

## Instructions

Parse `$ARGUMENTS` to get the path. The path can be:
- A single markdown file (e.g., `presentation.md`)
- A folder containing markdown files (batch mode)

### Step 1: Check if config exists

Check if `.claude/rt-gamma.toml` exists in the project root.

If the config file does NOT exist:

1. Tell the user: "No rt-gamma config found. I'll create one at `.claude/rt-gamma.toml`"

2. Ask the user using AskUserQuestion:
   - Question: "How would you like to configure rt-gamma?"
   - Options:
     - "Interactive setup" - Walk through configuration options
     - "Manual setup" - Create template file for manual editing

3. If "Interactive setup":
   - Ask for their Gamma API key (required): "Enter your Gamma API key (get one at https://gamma.app/settings/api)"
   - Ask for default text mode: "preserve" (keep text as-is), "generate" (expand content), "condense" (summarize)
   - Ask for default image source: "ai" (AI generated), "unsplash", "none"
   - Create the config file with their values
   - Continue to Step 2

4. If "Manual setup":
   - Create the config template at `.claude/rt-gamma.toml` with placeholder values
   - Tell user: "Config template created at `.claude/rt-gamma.toml`. Please fill in your `api_key` and run the command again."
   - STOP execution here

### Step 2: Validate config has API key

Read `.claude/rt-gamma.toml` and check that `api_key` is not empty.

If `api_key` is empty, tell the user:
"API key is missing. Please add your Gamma API key to `.claude/rt-gamma.toml`"
STOP execution.

### Step 3: Determine path type

If no path provided in `$ARGUMENTS`:
- Ask user: "Please provide the path to a markdown file or folder"
- STOP until they provide a path

Check if the path is a file or directory:
- If it's a file → Go to Step 4 (Single Generation)
- If it's a directory → Go to Step 5 (Batch Generation)
- If path doesn't exist → Error: "Path not found: {path}"

### Step 4: Single File Generation

Run the generate script:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/generate.py" "PATH_TO_FILE"
```

The script outputs JSON. Parse it and report to the user:

If success:
- "Presentation created: {url}"
- "HTML redirect saved to: {html_path}"

If error:
- "Error: {error message}"

### Step 5: Batch Generation

Tell user: "Starting batch generation for folder: {path}"
Tell user: "Looking for files matching the pattern in config (default: *_presentation.md)"

Run the batch script:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/batch.py" "PATH_TO_FOLDER"
```

The script outputs JSON. Parse it and report to the user:

- "Processed {processed} of {total} files"
- List each result with URL or error
- If any failures, list them with their error messages

## Examples

Single file:
```
/rt-gamma my_talk.md
```

Batch folder:
```
/rt-gamma ./presentations/
```
