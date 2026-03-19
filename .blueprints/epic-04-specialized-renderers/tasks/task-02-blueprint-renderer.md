# Task: Blueprint Appendix Renderer

**Status:** [✓] Completed

**Dependencies:** Epic 03 task-01 (script structure and loader must exist)

## Context

- Language: Python
- Framework: None
- Testing: Manual
- Database: None

Renders `.blueprints/` folder contents as an appendix section. Each epic becomes a subsection with a task table showing name, status, and dependencies. Task details are rendered inline below the table.

## Needed from User

None

## Instructions

1. Add a `render_blueprints(blueprints_dir: str) -> str` function to `generate_docs.py`

2. Discover blueprint structure:
   ```python
   from pathlib import Path

   def render_blueprints(blueprints_dir: str) -> str:
       bp_path = Path(blueprints_dir)
       if not bp_path.exists():
           return "<p><em>No blueprints found.</em></p>"

       epics = sorted(bp_path.glob("epic-*/epic-*.md"))
   ```

3. For each epic markdown file:
   - Parse the epic markdown to extract: title, status, context, task list
   - Extract task references from the `## Tasks` section (lines matching `- [ ] [task-NN: ...](tasks/task-NN-...)`)

4. Render the epic as a subsection:
   ```html
   <div class="blueprint-epic">
     <h2>{epic_title} <span class="epic-status">{status}</span></h2>
     <p>{context_summary}</p>

     <table class="task-table">
       <thead>
         <tr><th>Task</th><th>Status</th><th>Dependencies</th></tr>
       </thead>
       <tbody>
         <!-- for each task -->
         <tr>
           <td>{task_title}</td>
           <td>{status_badge}</td>
           <td>{dependencies}</td>
         </tr>
       </tbody>
     </table>
   ```

5. For each task file referenced in the epic:
   - Read the task markdown file
   - Parse: title, status, dependencies, context, instructions, acceptance criteria
   - Render inline below the table:
     ```html
     <details class="task-details">
       <summary>{task_title}</summary>
       <div class="task-content">
         {task_markdown_converted_to_html}
       </div>
     </details>
     ```

6. Add CSS for blueprint styling:
   ```css
   .blueprint-epic { margin-bottom: 2rem; }
   .epic-status { font-size: 0.75rem; padding: 2px 8px; border-radius: 3px; background: #e8e8e8; }
   .task-table { width: 100%; }
   .task-details { margin: 8px 0; padding: 8px; border: 1px solid #e0e0e0; border-radius: 4px; }
   .task-details summary { cursor: pointer; font-weight: 600; }
   .task-details[open] { background: #fafafa; }
   ```

7. Status badge rendering:
   - `[ ]` or `Pending` → gray badge
   - `[x]` or `[✓]` or `Complete` → green badge
   - `[!]` or `Failed` → red badge
   - `[~]` or `In Progress` → blue badge

## Acceptance Criteria

- [x] Discovers and reads all epic folders in `.blueprints/`
- [x] Each epic renders as a subsection with title and status
- [x] Task table shows all tasks with name, status badge, and dependencies
- [x] Task details are expandable via `<details>` elements
- [x] Task content is converted from markdown to HTML
- [x] Status badges are color-coded
- [x] Gracefully handles missing task files (shows warning, doesn't crash)
- [x] Returns placeholder message if no blueprints exist

## Implementation Notes

- Completed on 2026-03-19
- Added `render_blueprints(blueprints_dir)` function to `rt-agents/scripts/generate_docs.py`
- Helper functions: `_status_badge()` for color-coded status badges, `_parse_epic_tasks()` for extracting task references from epic markdown, `_parse_task_file()` for reading individual task files
- Status badge colors: gray (pending/[ ]), green (complete/[x]/[✓]), red (failed/[!]), blue (in-progress/[~])
- Uses existing `convert_markdown()` function to render task content as HTML inside `<details>` elements
- Missing task files produce a stderr warning but don't crash; the task row shows data from the epic's task list instead
- Added blueprint CSS to `rt-agents/templates/documentation.html`: `.blueprint-epic`, `.epic-status`, `.status-{color}`, `.task-table`, `.task-details`, `.task-content`
- Print styles expand `.task-details` blocks for PDF output
