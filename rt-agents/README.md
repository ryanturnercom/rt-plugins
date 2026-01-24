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

### `/rt-agents:blueprint-create`

Creates structured implementation blueprints with epics and tasks.

**Usage:**
```
/rt-agents:blueprint-create user authentication with OAuth and email/password
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
