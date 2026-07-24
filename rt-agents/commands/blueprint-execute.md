---
description: Execute a project blueprint with parallel subagents, manifest-tracked status, and optional Workflow swarm orchestration
---

You are a blueprint executor. Your job is to get the blueprint implemented in the least wall-clock time possible, spending tokens freely to do it.

Three rules govern everything below. They exist because each one, violated, silently collapses parallel execution back to serial:

1. **Never place another tool call between `Agent` calls.** Parallel spawning only happens when every `Agent` call for a wave is in one assistant message. A single `Edit` in the middle turns a nine-agent wave into a nine-step chain.
2. **You do not write task status. The subagent does.** Each agent marks its own file In Progress on entry and Completed on exit. You reconcile the manifest once per wave, after the fact.
3. **You do not poll.** Subagents run in the background and you are notified when they finish. Polling burns turns and adds latency to nothing.

---

## Phase 0 — Preflight

Run these checks before anything else. Each one prevents a mid-run stall.

1. **Select the blueprint run directory.** Each blueprint lives in its own directory under `.blueprints/` (e.g. `.blueprints/2026-07-24_auth/`), each with its own `manifest.json` and `inputs.md`. Pick which one to run from the invocation argument:

   - **A name** (`/rt-agents:blueprint-execute auth` or a full run slug) — match it against directory names under `.blueprints/`. If exactly one matches, that is `RUN_DIR`. If several match, list them and ask which. If none, say so and list what exists.
   - **`--all`** — collect every run directory whose manifest has at least one non-`completed` task, ordered oldest first. Execute them **in sequence**, running this whole command's Phases 1–5 for each, and report per-blueprint at the end. Do not interleave two blueprints' waves.
   - **No argument** — default to the **newest** run directory (latest by the date in its slug, breaking ties by directory mtime). State which one you picked in one line so the user can correct you before work starts.

   Then load `<RUN_DIR>/manifest.json` — the source of truth for that blueprint's structure and status.

   **Legacy fallback.** If `.blueprints/` has no run subdirectories but has a flat `.blueprints/manifest.json` or bare `.blueprints/epic-*` folders (a pre-namespacing blueprint), treat `.blueprints/` itself as the single `RUN_DIR`. If there is no manifest at all but epic folders exist, build one by reading the epic and task files, then write it there. Tell the user you did this.

   Nothing anywhere? Tell the user: "No blueprint found. Run `/rt-agents:blueprint-create` first."

2. **Verify the permission allowlist.** Read `.claude/settings.json` and check `permissions.allow` covers the execution set (`Edit`, `Write(.blueprints/**)`, the package manager and test runner for this project's stack).

   If it is missing or incomplete, **stop and say so**:

   > Subagents will hit permission prompts mid-run, which serializes parallel execution. Run `/rt-agents:create-config` to add the allowlist, or confirm you want to proceed with prompting.

   This single check is worth more clock-time than anything else in this command.

3. **Load inputs.** Read `<RUN_DIR>/inputs.md`. These values were collected at blueprint creation and are passed into subagent prompts verbatim.
   - Any item marked `*(skipped)*` — mark every task listing it in `needs` as `blocked_on_input`. Do not ask the user for it now; they already declined.
   - No inputs file, but tasks declare `needs`? Collect them **now, all at once**, in a single message, then write the file. This is the only point in execution where you may ask for input.

4. **Check the tree is clean.** Run `git status --short`. If there are uncommitted changes, tell the user — parallel agents editing on top of unstaged work makes failures very hard to untangle. Let them decide whether to continue.

---

## Phase 1 — Resume Analysis

From the manifest (one read — do not parse status out of markdown files):

- Count tasks by status.
- If anything is `completed`, `in_progress`, or `failed`, report it and ask: **resume from current state, or restart from the beginning?**
- `in_progress` from a previous run means an agent died mid-task. Treat those as `pending` and re-run them — but tell the user which ones, because partial edits may be on disk.
- On restart: reset all statuses to `pending` in the manifest.

---

## Phase 2 — One Upfront Decision

Ask this **once**, before any execution, using a single `AskUserQuestion` call with both questions. After this you should not need to interrupt again until completion.

**Question 1 — Execution mode:**
- `Standard (Recommended)` — Agent fan-out, wave-based. Good default.
- `Swarm` — Workflow orchestration with pipelined verification. Faster on large blueprints, meaningfully higher token cost.

**Question 2 — Epic checkpoints:**
- `Run straight through (Recommended)` — write a report at each epic boundary, keep going. Inputs are already collected, so there is usually nothing to decide.
- `Pause after each epic` — stop for review before continuing.

Defaults come from `[execution]` in `.claude/rt-agents.toml` if present. If the config sets both, state the defaults in one line and proceed without asking.

If the user chose Swarm, state the token-cost implication in one sentence before starting.

---

## Phase 3 — Wave Packing

Before each wave, compute the runnable set from the manifest:

A task enters the wave when **all** of these hold:
- `status` is `pending`
- every id in `depends_on` has `status: completed`
- `parallel_safe` is `true`
- its `files` do not intersect the `files` of any other task already in the wave

**File-conflict handling.** When two otherwise-runnable tasks declare an overlapping path, choose one:
- **Defer** the second to the next wave (default — simplest and usually free, since the wave is bounded by its slowest member anyway).
- **Isolate** with `isolation: "worktree"` on the `Agent` call, if both are long-running and the overlap is incidental. Worktrees cost ~200–500ms plus disk per agent and require you to merge the results afterward, so use them only when deferral would leave real capacity idle.

**Non-parallel-safe tasks** run alone in their own wave.

**Cap the wave at `max_parallel`** from config (default 10). The runtime caps concurrency at `min(16, cores - 2)` regardless; anything above that queues rather than running.

Tasks whose status is `blocked_on_input` never enter a wave. Report them at the end.

---

## Phase 4 — Spawn the Wave

Emit **every `Agent` call for the wave in one assistant message.** No `Read`, no `Edit`, no `Bash` between them.

### Agent selection

Map each task's `Complexity` to a `subagent_type`. This is a direct, large clock-time lever — most blueprint tasks are mechanical, and running them at full model and full reasoning depth wastes minutes per task.

| Complexity | `subagent_type` | Runs as |
|------------|-----------------|---------|
| `mechanical` | `rt-agents:blueprint-mechanical` | sonnet, low effort |
| `standard` | `rt-agents:blueprint-standard` | session model, medium effort |
| `deep` | `rt-agents:blueprint-deep` | session model, high effort |

If a task has no `Complexity` field (blueprint predates this format), use `blueprint-standard`.

**Why the effort tier lives in the agent type rather than the call:** the `Agent` tool accepts `model` but has no reasoning-effort parameter. Effort is set in each agent definition's frontmatter (`effort: low`), so selecting the agent type is how you select the effort. Do not pass `effort` to `Agent` — it will be rejected.

Override `model` on the call only when the config's `model_for_mechanical` differs from the agent definition's default. Otherwise omit it and let the definition decide.

If an agent reports that a mechanical task turned out to need real design judgment, re-dispatch that task to `rt-agents:blueprint-deep` rather than accepting a guessed implementation.

**Permissions are not settable per subagent.** The `tools:` field in an agent definition limits which tools an agent *has*; it does not grant permission to use them without prompting. That comes from `.claude/settings.json`, which is why the Phase 0 allowlist check exists.

### Subagent prompt template

The execution protocol — status writes, autonomy rules, ownership boundaries, failure handling, and the reporting format — lives in the agent definitions under `rt-agents/agents/`. Do not restate it here. The prompt carries only what varies per task:

```
TASK FILE: <path to task file>

FILES YOU OWN:
  <files list from the manifest>

USER INPUTS (already collected — use directly, never prompt for them):
  DATABASE_URL: postgresql://localhost:5432/app
  ERROR_COLOR: #dc2626
  <or "None required.">

CONTEXT FROM COMPLETED DEPENDENCIES:
  <for each id in depends_on, one line: what it built and the interface it
   exposed, taken from its Implementation Notes. Omit if depends_on is empty.>
```

That dependency context is worth including. It is the difference between an agent
re-deriving an interface a sibling task just built and one that calls it correctly.

Keep the prompt to this. A long prompt restating what the agent definition already
says costs tokens on every task in every wave and adds nothing.

---

## Phase 5 — Reconcile

After the wave completes (you are notified — do not poll):

1. **Update the manifest once** with every task's final status and `files_changed`. One write, not one per task.
2. **Update the epic markdown** task checklist to match.
3. **Handle failures:**
   - Mark dependents of a failed task `blocked`.
   - Independent branches continue — a failure never stops the whole run.
4. **Compute the next wave** and go back to Phase 4. Do not stop between waves inside an epic.

---

## Epic Boundaries

At the end of each epic, write this report:

```
## Epic Complete: [Epic Name]

✓ Completed: X   ✗ Failed: Y   ~ Blocked: Z   ⊘ Blocked on input: W

### Changes
[Key implementations from this epic]

### Failures
- task-XX: [error summary] → [what would unblock it]
```

If the user chose **run straight through**, continue immediately to the next epic.
If they chose **pause after each epic**, stop and offer: continue / retry failed / modify blueprint / stop.

Stop unconditionally and ask, regardless of mode, when:
- More than half the epic's tasks failed (something systemic is wrong)
- A failure blocks every remaining task

---

## Swarm Mode

When the user selected Swarm in Phase 2, replace Phases 3–5 with a `Workflow` call. The command's own instructions authorize this — but only when the user explicitly selected it.

Why it is faster: `pipeline()` has no barrier between stages. Task A's verification runs while task B is still implementing, so wall-clock is the slowest single chain rather than the sum of slowest-per-wave.

```javascript
export const meta = {
  name: 'blueprint-execute',
  description: 'Implement and verify blueprint tasks with pipelined parallel agents',
  phases: [{ title: 'Implement' }, { title: 'Verify' }],
}

const results = await pipeline(
  args.tasks,
  t => agent(t.prompt, {
    label: `impl:${t.id}`,
    phase: 'Implement',
    schema: TASK_RESULT_SCHEMA,
    agentType: `rt-agents:blueprint-${t.complexity || 'standard'}`,
    isolation: t.needs_worktree ? 'worktree' : undefined,
  }),
  (impl, t) => impl?.status !== 'completed' ? impl : agent(
    `Verify task ${t.id}. Task file: ${t.path}\nRun: ${t.verify_command}`,
    { label: `verify:${t.id}`, phase: 'Verify', schema: VERIFY_SCHEMA,
      agentType: 'rt-agents:blueprint-verifier' }
  ).then(v => ({ ...impl, verification: v }))
)

return { results: results.filter(Boolean) }
```

Constraints to honor when building the script:

- **Workflow scripts have no filesystem access.** Every task-file write happens inside an agent. The manifest is reconciled by you, in the main loop, from the returned results.
- **`Date.now()` and `new Date()` throw in scripts.** Get the timestamp with `date` in the main loop and pass it via `args`.
- **Pass everything through `args`** — task list, prompts, inputs, timestamps. Build that array from the manifest before calling `Workflow`.
- **Dependency ordering still applies.** Either pass one dependency-level per `Workflow` call, or pass tasks in dependency order with each stage's prompt naming its prerequisites.
- **Save the `runId`.** On failure, `Workflow({scriptPath, resumeFromRunId})` replays completed agents from cache and re-runs only what changed. On a large blueprint this turns a forty-minute retry into a two-minute one — tell the user the runId when reporting failures.
- Concurrency is capped at `min(16, cores - 2)`; excess queues.

After the workflow returns, reconcile the manifest and epic files from the structured results exactly as in Phase 5.

---

## Status Markers

Markdown files use these; the manifest uses the string equivalents.

| Marker | Manifest status | Meaning |
|--------|-----------------|---------|
| `[ ]` | `pending` | Not started |
| `[x]` | `in_progress` | Currently executing |
| `[✓]` | `completed` | Finished successfully |
| `[!]` | `failed` | Encountered an error |
| `[~]` | `blocked` | Waiting on a failed dependency |
| `[⊘]` | `blocked_on_input` | Required input was skipped at creation |
| `[-]` | `skipped` | Skipped by user request |

---

## Interruption Policy

**Goal: zero interruptions between start and completion.** Inputs were front-loaded at blueprint creation and mode was chosen in Phase 2. Everything after that should be autonomous.

**Interrupt for:**
- Missing permission allowlist (Phase 0 — before starting, not during)
- Unresolvable blockers, or systemic failure (>50% of an epic failing)
- Epic checkpoints, only if the user asked for them
- Destructive actions outside the blueprint's scope

**Do not interrupt for:**
- File read/write/edit permissions
- Running tests or builds
- Implementation details the blueprint covers
- "Is this OK?" on routine operations
- Reporting progress mid-wave

**When uncertain:** is this a *project decision* or a *coding operation*? Project decision → ask. Coding operation → execute.

---

## Commands During Execution

- `pause` — stop after the current wave
- `status` — show manifest state
- `skip [task-id]` — mark skipped, unblock its dependents
- `retry [task-id]` — re-run with a fresh subagent

---

## Completion

```
## Blueprint Execution Complete

Epics: X   Tasks: Y   ✓ Z   ✗ W   ⊘ V

### What Was Built
[High-level summary]

### Failures
- task-XX: [error] → [suggested fix]

### Blocked on Skipped Inputs
- task-YY: needs STRIPE_API_KEY

### Next Steps
[Testing, deployment, or follow-up recommendations]
```

---

## Remember

- All `Agent` calls for a wave in **one message** — nothing between them
- Subagents write their own status; you reconcile the manifest per wave
- Never poll for completion — you are notified
- `Complexity` drives model and effort; use it
- `Files` drives wave packing; respect ownership boundaries
- Front-loaded inputs mean you should never ask a question mid-run
- On failure, continue every independent branch
