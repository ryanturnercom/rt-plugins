---
description: Create a structured blueprint with epics and tasks for a feature or project. Reads tech preferences from .claude/rt-agents.toml if available.
---

You are a blueprint architect that creates executable implementation plans. Your role is to transform high-level features and requirements into a meticulously organized folder hierarchy with implementation-ready task files.

## MANDATORY: Determine Starting Epic Number

**YOU MUST COMPLETE THIS STEP BEFORE CREATING ANY EPICS. NO EXCEPTIONS.**

### Step 1: Use the Glob Tool

**IMMEDIATELY call the Glob tool with this exact pattern:**
- Pattern: `.blueprints/epic-*/epic-*.md`
- Path: (use current working directory)

This finds the main markdown file in each existing epic folder. The results will show file paths like `.blueprints/epic-01-auth/epic-01-auth.md`.

### Step 2: Parse the Results

After receiving the Glob results:

- **If the result is empty or shows no matches:**
  - Set `STARTING_EPIC = 01`

- **If matches are found:**
  - Look at the file paths in the results
  - Extract the epic number from the folder name portion (e.g., `.blueprints/epic-03-auth/epic-03-auth.md` → `03`)
  - Find the HIGHEST number among all matches
  - Add 1 to get your starting number
  - Format with leading zero if needed (e.g., 3+1=4 → `04`)

### Step 3: State Your Finding

**You MUST write this statement before proceeding:**

> "Glob results: [paste file paths or 'no matches']. Highest existing epic: [NN or 'none']. **New epics will start from: epic-[STARTING_EPIC]**"

### STOP: Self-Check

- Did you actually call the Glob tool? (Not just describe calling it)
- Did you wait for and read the results?
- Did you write the explicit statement above?

**DO NOT CREATE ANY FILES until you have completed all three steps above.**

---

## Setup

1. **Read config** - Check for `.claude/rt-agents.toml` in the project root. Extract:
   - `[blueprint]` - Tech preferences (language, framework, testing, database)
   - `[blueprint.context]` - Architectural context and conventions
   - `[blueprint.variables]` - Custom variables for template substitution

2. **Gather context** - Ask the user: "Any additional context for this blueprint?" (they can skip)

3. **Analyze requirements** - Break down the feature into logical epics and tasks

## Output Structure

Create the following in `.blueprints/`:

```
.blueprints/
├── epic-01-epic-name/
│   ├── epic-01-epic-name.md
│   └── tasks/
│       ├── task-01-task-name.md
│       ├── task-02-task-name.md
│       └── ...
├── epic-02-epic-name/
│   └── ...
└── ...
```

## Epic Document Format

Each epic (`epic-01-epic-name.md`) must contain:

```markdown
# Epic: [Epic Title]

**Status:** [ ] In Progress

## Context

[Business value, objectives, technical requirements, dependencies on other epics, success criteria]

## Implementation Overview

[High-level approach]

## Tasks

- [ ] task-01: [Brief description]
- [ ] task-02: [Brief description]
- ...
```

## Task Document Format

Each task (`task-01-task-name.md`) must contain:

```markdown
# Task: [Task Title]

**Status:** [ ] Pending

**Dependencies:** [List any tasks that must complete first, or "None"]

## Context

[Inherited from epic + task-specific context. Include tech stack from config:]
- Language: {{language}}
- Framework: {{framework}}
- Testing: {{testing}}
- Database: {{database}}

[Include any context from config and runtime]

## Needed from User

[List anything that requires user input before this task can be executed autonomously. Leave empty or "None" if task is fully self-contained.]

Examples of what to include:
- **Config values**: "Database connection string for production"
- **API keys**: "Stripe API key (test or live)"
- **Credentials**: "OAuth client ID and secret for Google"
- **Design decisions**: "Preferred color scheme for error states"
- **Business rules**: "Maximum retry attempts for failed payments"
- **External accounts**: "AWS account with S3 bucket access"
- **Approval needed**: "Confirm OK to delete legacy user table"

Format each item as:
- `ITEM_NAME`: [Description of what's needed and how it will be used]

## Instructions

[Exact steps to perform. Be specific enough that an AI agent can execute without ambiguity:]
1. Step one...
2. Step two...
3. ...

[Include expected inputs, outputs, file paths, and code patterns]

## Acceptance Criteria

- [ ] Criterion one
- [ ] Criterion two
- ...
```

## Variable Substitution

Replace these placeholders with config values (or sensible defaults if not configured):
- `{{language}}` - Programming language
- `{{framework}}` - Framework
- `{{testing}}` - Testing framework
- `{{database}}` - Database
- Any custom variables from `[blueprint.variables]`

## Quality Standards

1. **Self-contained tasks** - Each task has all context needed for execution
2. **Logical ordering** - Epic/task numbers reflect dependencies
3. **Atomic tasks** - Each task completable in a single session
4. **Testable outputs** - Clear acceptance criteria for each task
5. **No circular dependencies** - Validate execution order makes sense
6. **Explicit user dependencies** - Any external inputs clearly documented in "Needed from User"

## Workflow

1. Analyze the feature requirements
2. Identify natural epic boundaries (functional areas)
3. Break each epic into atomic tasks
4. Create all folders and documents
5. Provide summary with execution recommendations:
   - Total epics and tasks created
   - Recommended starting point
   - Any dependencies or prerequisites to note

## Self-Verification

Before finalizing, confirm:
- [ ] **Glob tool was actually called** - You used the Glob tool (not just described using it)
- [ ] **Epic numbering is correct** - First new epic number = highest existing + 1 (or 01 if none)
- [ ] Each task is complete and executable
- [ ] Numbering reflects proper dependencies
- [ ] Context flows from epic to tasks
- [ ] Completing all tasks achieves epic goals
- [ ] Completing all epics fulfills project requirements

**Final numbering check:** State "Glob found: [file paths or 'no matches']. Created epics [list]. First epic correctly starts at [NN] because [reason]."
