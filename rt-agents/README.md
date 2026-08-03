# rt-agents

Specialized agents for supercharged Claude Code development.

## Installation

Add to your Claude Code settings or install via the rt-plugins marketplace.

## Available Commands

### `/rt-agents:create-config`

Creates the configuration file, sets up the execution permission allowlist, and opens the config for editing.

```
/rt-agents:create-config
```

Creates:
- `.claude/rt-agents.toml` — tech stack, architectural context, execution defaults
- `.claude/settings.json` `permissions.allow` entries — merged, never overwritten
- `.gitignore` entry for `.blueprints/*/inputs.md` (per-blueprint input files, which may hold secrets)

**Run this before your first `blueprint-execute`.** Without the allowlist, every parallel subagent stalls on a permission prompt mid-run, which serializes execution and is the most common cause of slow blueprint runs.

---

### `/rt-agents:spec-create`

Interviews you to produce a source-of-truth spec markdown file that `blueprint-create` can consume directly. The kind of spec is picked upfront as a dropdown, then the interview adapts to that kind — so `chore` and `docs` stay quick (1–3 questions) while `feat`, `prd`, and `migration` get the depth they need.

**Usage:**
```
/rt-agents:spec-create item state tracking for extracted reminders
```

**Features:**
- **Kind-first** — dropdown selection of `feat`, `fix`, `chore`, `refactor`, `migration`, `integration`, `infra`, `docs`, or `prd`; drives the filename and the question track
- **Right-sized interview** — per-kind question tracks (e.g. `fix` asks repro/root-cause/regression; `migration` asks backfill/rollback/downtime) so you only get questions that matter
- **One question at a time** — multiple-choice options with `other` and `not sure — help me think through this` on every question
- **Adaptive** — re-evaluates remaining questions after every answer; drops irrelevant ones, adds ones surfaced by your answers
- **Brainstorming mode** — pick `?)` on any question to get tradeoff analysis and a recommendation
- **Escape hatches** — type `skip`, `back`, `why`, `preview`, or `done` at any prompt
- **Draft review** — shows a Design Decisions table for confirmation before writing the file
- **Per-kind sections** — output only includes the sections relevant to the kind (e.g. `fix` gets Reproduction + Root Cause; `migration` gets Migration Plan; `prd` gets Success Metrics)

**Output:**
```
.specs/YYYY-MM-DD_<kind>_<slug>.md
```

Example: `.specs/2026-04-18_feat_item-state-tracking.md`. Feeds straight into `/rt-agents:blueprint-create @.specs/<file>.md`.

---

### `/rt-agents:blueprint-create`

Creates structured implementation blueprints with epics and tasks. Best results when fed a spec produced by `/rt-agents:spec-create`.

**Usage:**
```
/rt-agents:blueprint-create user authentication with OAuth and email/password
/rt-agents:blueprint-create @.specs/2026-04-18_feature_auth.md
/rt-agents:blueprint-create swarm @.specs/2026-04-18_feature_auth.md
```

**How it works:**

1. **Surveys the codebase** — delegated to a single `Explore` agent on large repos, which returns a compact map instead of a file dump. Keeps the architect's context small for every phase that follows.
2. **Designs the skeleton centrally** — epics, tasks, dependencies, file ownership, complexity, and **the exact interfaces that cross task boundaries** are decided in one place, where global reasoning is possible.
3. **Approves and collects inputs in one interaction** — the skeleton table, the approval question, and every credential or decision arrive in the same turn. One human round-trip, not two. Everything is written to the blueprint's `inputs.md` so execution never has to ask.
4. **Fans out authoring** — one subagent per epic writes that epic's files, all spawned in parallel. A six-epic blueprint goes from ~40 sequential writes to a single wave. Epics with no `deep` task are authored on Sonnet; oversized epics are sharded along the dependency graph.
5. **Writes a manifest** — the blueprint's `manifest.json` becomes the machine-readable source of truth for structure and status. Written *after* the fan-out is dispatched, so it overlaps with the authors instead of delaying them.

Each blueprint gets its **own directory** under `.blueprints/`, named `<date>_<slug>/`, holding its own manifest, inputs, and epics. Two blueprints created at the same time never share a file, so concurrent `blueprint-create` runs can't clobber each other's inputs or manifest.

Pass `swarm` to author and critique with a `Workflow` pipeline — each epic's task files get an executability critique as soon as they're authored. Higher token cost, better task files.

**Output:**
```
.blueprints/
└── 2026-04-18_auth/              # one directory per blueprint (date_slug)
    ├── manifest.json             # Structure + status, machine-readable
    ├── inputs.md                 # Collected user values (gitignored)
    ├── epic-01-auth-foundation/
    │   ├── epic-01-auth-foundation.md
    │   └── tasks/
    │       ├── task-01-database-schema.md
    │       └── task-02-user-model.md
    └── epic-02-oauth-integration/
        └── ...
```

**Design rules it applies** (these are what determine execution speed):
- Maximize disjoint file ownership — overlapping files can't run concurrently
- Target 6–12 parallel-safe tasks per epic (runtime caps concurrency at `min(16, cores-2)`)
- Minimize dependency *depth*, not count — wall-clock follows the longest chain
- Balance task counts across epics — authoring waits on the slowest single epic
- Pin every cross-task interface centrally — two authors that can't see each other will otherwise invent two incompatible signatures
- Mark complexity honestly — `mechanical` tasks run on a faster model at execution time

---

### `/rt-agents:blueprint-execute`

Executes a blueprint with parallel subagents, manifest-tracked status, and optional Workflow swarm orchestration.

**Usage:**
```
/rt-agents:blueprint-execute              # runs the newest blueprint
/rt-agents:blueprint-execute auth         # runs the blueprint whose slug matches "auth"
/rt-agents:blueprint-execute --all        # runs every pending blueprint, in sequence
```

Blueprints live in per-run directories under `.blueprints/`. With no argument, execute picks the **newest** one and states which. Pass a name to target a specific blueprint, or `--all` to work through every blueprint that still has pending tasks, oldest first.

**Features:**
- **Permission preflight** — verifies the allowlist before starting, so no subagent stalls on a prompt mid-run
- **Zero mid-run interruptions** — inputs were collected at blueprint creation; mode is chosen once up front
- **Conflict-free wave packing** — waves are packed from dependency-satisfied, file-disjoint tasks
- **Per-task model selection** — `mechanical` tasks run on a faster model; in swarm mode they also drop to low reasoning effort while `deep` tasks get high
- **Subagent-owned status** — each agent writes its own task file status, so the orchestrator never interleaves edits between spawns (which would serialize the wave)
- **Manifest reconciliation** — one manifest read per wave instead of parsing status out of every markdown file
- **Swarm mode** — `Workflow` orchestration with pipelined verification, no barrier between implement and verify, plus `resumeFromRunId` so a retry replays completed work from cache
- **Worktree isolation** — used automatically when two long-running tasks have incidental file overlap
- **Error handling** — independent branches continue; only true dependents are blocked

**Execution modes** (chosen once, at start):

| Mode | Orchestration | When |
|------|---------------|------|
| Standard | Agent fan-out, wave-based | Default. Good for most blueprints. |
| Swarm | `Workflow` with `pipeline()` | Large blueprints. Faster wall-clock, meaningfully higher token cost. |

**Status Markers:**
| Marker | Manifest status | Meaning |
|--------|-----------------|---------|
| `[ ]` | `pending` | Not started |
| `[x]` | `in_progress` | Currently executing |
| `[✓]` | `completed` | Finished successfully |
| `[!]` | `failed` | Encountered an error |
| `[~]` | `blocked` | Waiting on a failed dependency |
| `[⊘]` | `blocked_on_input` | Required input was skipped at creation |
| `[-]` | `skipped` | Skipped by user request |

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

[execution]
# Defaults for blueprint-execute
mode = "standard"                  # "standard" or "swarm"
stop_at_epic_checkpoints = false   # run straight through
max_parallel = 10                  # soft cap per wave
model_for_mechanical = "sonnet"    # model for **Complexity:** mechanical tasks

[documentation]
# Defaults for documentation-create
output_dir = ".rt-documentation"   # output directory, relative to project root
repo_url = ""                      # repository URL, linked in the footer
default_mode = "verbatim"          # section content mode: verbatim | summarize
default_print = true               # default print inclusion for sections
```

### Config Sections

| Section | Purpose |
|---------|---------|
| `[blueprint]` | Tech stack preferences |
| `[blueprint.context]` | Architectural patterns and conventions |
| `[blueprint.variables]` | Custom template variables |
| `[execution]` | Execution mode, concurrency, and model defaults |
| `[documentation]` | Output location and default section rendering |

## Task Format

Generated tasks include:

- **Status** — tracking checkbox, written by the executing agent itself
- **Dependencies** — task ids that must complete first
- **Files** — every path the task creates or modifies; drives conflict-free wave packing
- **Parallel-safe** — whether the task can run alongside others
- **Complexity** — `mechanical` | `standard` | `deep`; drives model and effort selection
- **Context** — tech stack, architectural context, and the pinned interfaces of every dependency
- **User Inputs** — values collected at blueprint creation, inlined and ready to use
- **Instructions** — step-by-step implementation guide
- **Verification** — the exact command to run and what passing looks like
- **Acceptance Criteria** — definition of done

`Files`, `Parallel-safe`, and `Complexity` are load-bearing. Tasks missing them fall back to the slowest, most conservative execution path.

## Bundled Agents

The plugin ships five agent definitions in `agents/`. Each sets its own model, reasoning effort, and tool set in frontmatter, and the commands dispatch to them by `subagent_type`.

| Agent | Model / Effort | Role |
|-------|----------------|------|
| `blueprint-author` | sonnet or session model, high | Writes one epic's (or one shard's) task files. Sonnet when the epic has no `deep` task. Read/Write/Glob/Grep only — cannot touch source code. |
| `blueprint-mechanical` | sonnet, low | Executes tasks whose instructions fully determine the output. |
| `blueprint-standard` | session model, medium | Executes tasks needing normal implementation judgment. |
| `blueprint-deep` | session model, high | Executes tasks needing architectural judgment. |
| `blueprint-verifier` | session model, high | Independently checks a completed task against its acceptance criteria. Read-only. |

**This is how per-task effort tuning works.** The `Agent` tool accepts a `model` parameter but has no reasoning-effort parameter — effort is set in the agent definition's frontmatter (`effort: low`). Selecting the agent type is therefore how you select the effort tier, and a task's `**Complexity:**` field is what picks the agent. In swarm mode, Workflow's `agent()` can additionally override `effort` per call.

Two consequences worth knowing:

- **Cheap tasks get cheap agents.** Most tasks in a well-specified blueprint are mechanical, and running them on sonnet at low effort rather than the session model at full depth is a large share of the wall-clock saving.
- **The protocol lives in the agent, not the prompt.** Status writes, ownership rules, failure handling, and reporting format are in the definitions, so per-task prompts carry only the task path, file ownership, inputs, and dependency context. That keeps prompt cost flat across large waves.

The `tools:` field limits which tools an agent *has*. It does not grant permission to use them without prompting — that still comes from `.claude/settings.json`, which is why `create-config` writes the allowlist.

## Workflow

```
/rt-agents:create-config                        # once per project
/rt-agents:spec-create <topic>                  # interview → .specs/*.md
/rt-agents:blueprint-create @.specs/<file>.md   # skeleton → inputs → fan-out authoring (own dir)
/rt-agents:blueprint-execute                    # runs the newest blueprint (or name / --all)
```

## Tips

- **Run `create-config` first.** The permission allowlist it writes is what keeps parallel subagents from stalling on prompts — it's the biggest single factor in execution wall-clock.
- Feed `blueprint-create` a spec rather than a prose description. Better task files, fewer execution failures.
- Be exhaustive in the spec's "Needed from User" section. Anything missed there becomes an interruption mid-execution.
- Use `swarm` mode on large blueprints when clock-time matters more than token cost.
- On a failed swarm run, keep the `runId` — resuming replays completed agents from cache instead of re-running them.
- Add project-specific context to `[blueprint.context]` to get tailored task prompts.
