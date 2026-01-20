---
description: Create rt-gamma configuration file
---

Create the rt-gamma configuration file at `.claude/rt-gamma.toml`.

## Instructions

### Step 1: Check if config already exists

Check if `.claude/rt-gamma.toml` exists in the project root.

If the config file ALREADY EXISTS:
- Tell the user: "Config file already exists at `.claude/rt-gamma.toml`. Not overwriting."
- STOP execution here (do not create or modify the file)

### Step 2: Create the config file

If the config file does NOT exist, create `.claude/rt-gamma.toml` with this content:

```toml
# rt-gamma configuration
# Get your API key from: https://gamma.app/settings/api

# Required: Your Gamma API key
api_key = ""

# Optional: Default Gamma theme ID (leave empty for Gamma default)
theme = ""

# Optional: Default Gamma template ID for template-based generation
template = ""

# Text processing mode: generate | condense | preserve
text_mode = "preserve"

# Image source: ai | unsplash | giphy | pexels | pictographic | none
image_source = "ai"

# Card/slide splitting: auto | inputTextBreaks (respects --- markers)
card_split = "inputTextBreaks"

# Batch mode: file pattern to match
batch_pattern = "*_presentation.md"
```

### Step 3: Confirm creation

Tell the user:
- "Created config file at `.claude/rt-gamma.toml`"
- "Please edit the file and add your Gamma API key"
- "Get your API key from: https://gamma.app/settings/api"
