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

### `/rt-agents:blueprint`

Creates structured implementation blueprints with epics and tasks.

**Usage:**
```
/rt-agents:blueprint user authentication with OAuth and email/password
```

**Output:**
```
.blueprints/
└── epics/
    ├── 01-auth-foundation/
    │   ├── 01-auth-foundation.md
    │   └── tasks/
    │       ├── task-01-database-schema.md
    │       └── task-02-user-model.md
    └── 02-oauth-integration/
        └── ...
```

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
- **Instructions** - Step-by-step implementation guide
- **Acceptance Criteria** - Definition of done

## Tips

- Run without config for sensible defaults
- Add project-specific context to get tailored prompts
- Execute tasks in numbered order for best results
