---
description: Create rt-agents configuration file and the execution permission allowlist, then open the config for editing
---

Create the rt-agents configuration at `.claude/rt-agents.toml` **and** ensure `.claude/settings.json` grants the permissions that `blueprint-execute` subagents need to run without prompting.

Both halves matter. Without the permission allowlist, every parallel subagent stalls on a permission prompt mid-run, which destroys the clock-time advantage of parallel execution.

## Instructions

### Step 1: Check if config already exists

Check if `.claude/rt-agents.toml` exists in the project root.

If the config file ALREADY EXISTS:
- Tell the user: "Config file already exists at `.claude/rt-agents.toml`"
- Skip to Step 3 (the permission allowlist is still worth verifying)

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

[execution]
# Defaults for /rt-agents:blueprint-execute
# mode: "standard" (Agent fan-out) or "swarm" (Workflow orchestration, higher token cost)
mode = "standard"
# stop_at_epic_checkpoints: pause for review after each epic
stop_at_epic_checkpoints = true
# max_parallel: soft cap on concurrent subagents per wave (runtime cap is min(16, cores-2))
max_parallel = 10
# model_for_mechanical: model override for tasks marked **Complexity:** mechanical
model_for_mechanical = "sonnet"
```

### Step 3: Ensure the execution permission allowlist

Read `.claude/settings.json` (create it if missing).

**First, inspect any existing `permissions.allow` entries to match the project's existing syntax style.** Claude Code accepts prefix matchers like `Bash(npm:*)`; if the file already uses a different form, follow it rather than introducing a second style.

Merge the following into `permissions.allow` — **add only entries that are not already present**, and never remove or reorder existing entries:

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Glob",
      "Grep",
      "Edit",
      "Write(.blueprints/**)",
      "Write(.specs/**)",
      "Bash(npm:*)",
      "Bash(npx:*)",
      "Bash(pnpm:*)",
      "Bash(yarn:*)",
      "Bash(node:*)",
      "Bash(python:*)",
      "Bash(pip:*)",
      "Bash(cargo:*)",
      "Bash(go:*)",
      "Bash(pytest:*)",
      "Bash(jest:*)",
      "Bash(vitest:*)",
      "Bash(mkdir:*)",
      "Bash(ls:*)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)"
    ]
  }
}
```

Notes on scope:
- `Write` is scoped to `.blueprints/**` and `.specs/**` only. Source-file writes go through `Edit`, which requires the file to have been read first — that is the safety boundary.
- Deliberately **not** included: `Bash(git push:*)`, `Bash(git reset:*)`, `Bash(rm:*)`, any migration runner. Those stay prompt-gated.

Ask the user before writing: show the entries you are about to add and confirm. If they decline, tell them `blueprint-execute` will prompt during runs and offer `--dangerously-skip-permissions` as their alternative (their call, not yours).

### Step 4: Ensure inputs files are gitignored

`blueprint-create` writes collected credentials and decisions to `<run-dir>/inputs.md` — one per blueprint, each in its own directory under `.blueprints/`. The glob below covers every run directory. Append to `.gitignore` if not already present:

```
.blueprints/*/inputs.md
```

If an older flat `.blueprints/inputs.md` entry is already present, leave it — it does no harm and covers pre-namespacing blueprints.

### Step 5: Open for editing

Open `.claude/rt-agents.toml` so the user can edit it.

- If in VS Code/Cursor: `code .claude/rt-agents.toml`
- If in another IDE: use the IDE's open file command
- If CLI only: tell the user to open the file manually

### Step 6: Confirm

Report in ≤5 lines:
- Whether the config was created or already existed
- How many permission entries were added to `.claude/settings.json` (or that it was already complete)
- Whether `.gitignore` was updated
- "Fill in your tech stack preferences and any project-specific context"
