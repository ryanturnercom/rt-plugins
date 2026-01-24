---
name: create-config
description: Create rt-agents configuration file and open it for editing
---

Create the rt-agents configuration file at `.claude/rt-agents.toml`.

## Instructions

### Step 1: Check if config already exists

Check if `.claude/rt-agents.toml` exists in the project root.

If the config file ALREADY EXISTS:
- Tell the user: "Config file already exists at `.claude/rt-agents.toml`"
- Ask if they want to open it for editing anyway
- If yes, proceed to Step 3
- If no, STOP execution

### Step 2: Create the config file

If the config file does NOT exist, create `.claude/rt-agents.toml` with this content:

```toml
# rt-agents configuration
# Tech preferences and context for agent-generated content

[blueprint]
# Preferred tech stack (used in generated task prompts)
language = ""
framework = ""
testing = ""
database = ""

[blueprint.context]
# Architectural context included in all tasks
# Add your project's patterns and conventions here
architecture = ""
conventions = ""

[blueprint.variables]
# Custom variables available as {{variable_name}} in prompts
# Example: company = "Acme Corp"
```

### Step 3: Open for editing

Open the file `.claude/rt-agents.toml` so the user can edit it.

Use the appropriate method:
- If in VS Code/Cursor: `code .claude/rt-agents.toml`
- If in another IDE: use the IDE's open file command
- If CLI only: tell user to open the file manually

### Step 4: Confirm

Tell the user:
- "Created config file at `.claude/rt-agents.toml`" (if newly created)
- "File is now open for editing"
- "Fill in your tech stack preferences and any project-specific context"
