# rt-agents

Specialized agents for supercharged Claude Code development.

## Installation

Add to your Claude Code settings or install via the rt-plugins marketplace.

## Available Commands

### `/rt-agents:create-config`

Creates the configuration file and opens it for editing.

```
/rt-agents:create-config
```

Creates `.claude/rt-agents.toml` with example structure for you to fill in.

---

### `/rt-agents:spec-create`

Interviews you one question at a time (multiple-choice, adaptive, with a brainstorming mode) to produce a source-of-truth spec markdown file that `blueprint-create` can consume directly.

**Usage:**
```
/rt-agents:spec-create item state tracking for extracted reminders
```

**Features:**
- **One question at a time** — multiple-choice options with an `other` and `not sure — help me think through this` option
- **Adaptive** — re-evaluates remaining questions after every answer; drops irrelevant ones, adds ones surfaced by your answers
- **Brainstorming mode** — pick `?)` on any question to get tradeoff analysis and a recommendation
- **Escape hatches** — type `skip`, `back`, `why`, `preview`, or `done` at any prompt
- **Draft review** — shows a Design Decisions table for confirmation before writing the file

**Output:**
```
.specs/YYYY-MM-DD_<kind>_<slug>.md
```

Structure mirrors the sample specs (Design Decisions table, Data Model, Scope, Implementation Order, etc.) and is specific enough to feed straight into `/rt-agents:blueprint-create @.specs/<file>.md`.

---

### `/rt-agents:blueprint-create`

Creates structured implementation blueprints with epics and tasks. Best results when fed a spec produced by `/rt-agents:spec-create`.

**Usage:**
```
/rt-agents:blueprint-create user authentication with OAuth and email/password
/rt-agents:blueprint-create @.specs/2026-04-18_feature_auth.md
```

**Output:**
```
.blueprints/
├── epic-01-auth-foundation/
│   ├── epic-01-auth-foundation.md
│   └── tasks/
│       ├── task-01-database-schema.md
│       └── task-02-user-model.md
├── epic-02-oauth-integration/
│   └── ...
└── ...
```

---

### `/rt-agents:blueprint-execute`

Executes a blueprint with parallel subagents, real-time progress tracking, and implementation notes.

**Usage:**
```
/rt-agents:blueprint-execute
```

**Features:**
- **Pre-flight input gathering** - Collects all configs, keys, and decisions needed before starting each epic
- **Autonomous execution** - Subagents have pre-granted permissions for file/code operations (no routine interruptions)
- **Parallel execution** - Analyzes task dependencies and runs all independent tasks simultaneously
- **Real-time updates** - Updates blueprint files as tasks start and complete
- **Implementation notes** - Adds summary, files changed, and key decisions to each completed task
- **Epic checkpoints** - Pauses after each epic for review before continuing
- **Smart resume** - Detects existing progress and offers to resume or restart
- **Error handling** - On failure, continues independent branches while blocking dependents

**Status Markers:**
| Marker | Meaning |
|--------|---------|
| `[ ]` | Pending |
| `[x]` | In Progress |
| `[✓]` | Completed |
| `[!]` | Failed |
| `[~]` | Blocked |

**Commands during execution:**
- `pause` - Stop after current wave
- `status` - Show current state
- `skip [task-id]` - Skip a task
- `retry [task-id]` - Retry a failed task

---

### `/rt-agents:documentation-config`

Scans the codebase for documentation sources (READMEs, OpenAPI specs, blueprints, etc.) and generates a structured TOML config at `.claude/rt-documentation.toml`. Supports merge mode on re-runs to preserve user edits.

**Usage:**
```
/rt-agents:documentation-config
```

**Output:**
```
.claude/rt-documentation.toml
```

---

### `/rt-agents:documentation-create`

Reads the documentation config and generates a single-page HTML documentation site at `.rt-documentation/index.html` with a timestamped snapshot.

**Usage:**
```
/rt-agents:documentation-create
```

**Output:**
```
.rt-documentation/
├── index.html                           # Always-current version
└── {project}_{YYYY-MM-DD_HH-MM-SS}.html  # Timestamped snapshot
```

**Print UI:**
- Click the print button to enter print mode
- Use **Select All** / **Select None** to quickly toggle sections
- Check/uncheck individual sections, then click **Print**
- Sections marked `print = false` in config are unchecked by default but can be re-enabled

## Documentation

Generate project documentation in three steps:

1. **Scan** — Run `/rt-agents:documentation-config` to scan the codebase and generate a config at `.claude/rt-documentation.toml`
2. **Edit** — Review the config to adjust sections, ordering, verbatim/summarize mode, and print flags
3. **Render** — Run `/rt-agents:documentation-create` to produce timestamped HTML

Output lives in `.rt-documentation/`.

## Configuration

Create `.claude/rt-agents.toml` in your project:

```toml
[blueprint]
# Preferred tech stack
language = "typescript"
framework = "nextjs"
testing = "vitest"
database = "postgres"

[blueprint.context]
# Architectural context included in all tasks
architecture = "We use repository pattern for data access."
conventions = "All models must extend BaseEntity."

[blueprint.variables]
# Custom variables available as {{variable_name}} in prompts
company = "Acme Corp"
style_guide = "airbnb"
```

### Config Sections

| Section | Purpose |
|---------|---------|
| `[blueprint]` | Tech stack preferences |
| `[blueprint.context]` | Architectural patterns and conventions |
| `[blueprint.variables]` | Custom template variables |

## Task Format

Generated tasks include:

- **Status** - Tracking checkbox
- **Dependencies** - What must complete first
- **Context** - Tech stack + architectural context
- **Needed from User** - Configs, keys, accounts, decisions required (collected before epic starts)
- **Instructions** - Step-by-step implementation guide
- **Acceptance Criteria** - Definition of done

## Tips

- Run without config for sensible defaults
- Add project-specific context to get tailored prompts
- Execute tasks in numbered order for best results
