"""
rt-agents documentation generator.
Reads .claude/rt-documentation.toml and renders single-page HTML documentation.
"""

import html as _html
import json
import subprocess
import sys
import os
import re
from typing import Tuple


def ensure_dependencies():
    """Auto-install required packages on first run."""
    required = {"markdown": "markdown", "yaml": "pyyaml"}
    for import_name, pkg_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg_name]
            )


ensure_dependencies()

# Python 3.11+ has tomllib built-in
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "tomli"]
        )
        import tomli as tomllib

import markdown
from pathlib import Path


def parse_config(config_path: Path = None) -> dict:
    """Parse .claude/rt-documentation.toml and return project config and sections.

    Args:
        config_path: Path to the TOML config file. Defaults to
                     .claude/rt-documentation.toml relative to cwd.

    Returns:
        dict with keys:
            - "project": dict with name, description, output_dir, export_dir
            - "sections": list of section dicts sorted by order
    """
    if config_path is None:
        config_path = Path.cwd() / ".claude" / "rt-documentation.toml"

    if not config_path.exists():
        print(
            f"Error: Config file not found: {config_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(config_path, "rb") as f:
        raw = tomllib.load(f)

    project = raw.get("project", {})
    project.setdefault("name", "Untitled Project")
    project.setdefault("description", "")
    project.setdefault("output_dir", ".rt-documentation")
    project.setdefault("export_dir", ".rt-documentation/exports")

    sections = raw.get("section", [])

    # Sort sections by order (ascending), then by title alphabetically for ties
    sections.sort(key=lambda s: (s.get("order", 9999), s.get("title", "")))

    return {"project": project, "sections": sections}


def _slugify(title: str) -> str:
    """Convert a section title to a filename-safe slug.

    Example: "CI/CD Configuration" -> "ci-cd-configuration"
    """
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", " ", slug)
    slug = slug.strip()
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug


def load_sections(config: dict) -> list[dict]:
    """Validate source files and load their content.

    For each section in the config:
      - Check that all source files exist; warn on missing, skip missing sources.
      - If ALL sources for a section are missing, skip the entire section.
      - For mode="summarize" sections, read from .rt-documentation/.cache/<slug>.md
        instead of the original source; fall back to original if cache is missing.

    Args:
        config: The parsed config dict from parse_config().

    Returns:
        List of section dicts, each containing:
            title, sources_content, type, mode, print_flag, order
    """
    cwd = Path.cwd()
    cache_dir = cwd / ".rt-documentation" / ".cache"
    loaded = []

    for section in config["sections"]:
        title = section.get("title", "Untitled")
        sources = section.get("sources", [])
        mode = section.get("mode", "verbatim")
        section_type = section.get("type", "")
        print_flag = section.get("print", True)
        order = section.get("order", 9999)

        if not sources:
            print(
                f"Warning: Section '{title}' has no sources, skipping.",
                file=sys.stderr,
            )
            continue

        # Validate and load sources
        sources_content = []
        sources_paths = []
        for src in sources:
            src_path = cwd / src

            if not src_path.exists():
                print(
                    f"Warning: Source file not found: {src} "
                    f"(section '{title}'), skipping source.",
                    file=sys.stderr,
                )
                continue

            # For blueprint sections, we need the .blueprints/ root directory.
            # Sources may be listed as individual epic .md files or as dirs.
            # Resolve to the top-level blueprints directory in either case.
            if section_type == "blueprints":
                if src_path.is_dir():
                    bp_root = str(src_path)
                else:
                    # Source is a file like .blueprints/epic-01/epic-01.md
                    # Walk up to find the .blueprints root directory
                    bp_root = str(src_path.parent)
                    while bp_root and not Path(bp_root).name.startswith(".blueprints"):
                        parent = str(Path(bp_root).parent)
                        if parent == bp_root:
                            break
                        bp_root = parent
                # Only record each unique blueprints root once
                if bp_root not in sources_paths:
                    sources_content.append("")  # placeholder, not used
                    sources_paths.append(bp_root)
                continue

            # For summarize mode, try reading from cache first
            if mode == "summarize":
                slug = _slugify(title)
                cache_path = cache_dir / f"{slug}.md"
                if cache_path.exists():
                    try:
                        content = cache_path.read_text(encoding="utf-8")
                        sources_content.append(content)
                        sources_paths.append(str(cache_path))
                        continue
                    except Exception as e:
                        print(
                            f"Warning: Failed to read cache file "
                            f"{cache_path}: {e}, falling back to original.",
                            file=sys.stderr,
                        )

                # Cache miss — fall back to original with warning
                print(
                    f"Warning: Cache file not found for summarize section "
                    f"'{title}' ({cache_path}), using original source.",
                    file=sys.stderr,
                )

            # Read the original source file
            try:
                content = src_path.read_text(encoding="utf-8")
                sources_content.append(content)
                sources_paths.append(str(src_path))
            except Exception as e:
                print(
                    f"Warning: Failed to read {src}: {e}, skipping source.",
                    file=sys.stderr,
                )

        # If all sources were missing or failed, skip the entire section
        if not sources_content:
            print(
                f"Warning: All sources missing for section '{title}', "
                f"skipping entire section.",
                file=sys.stderr,
            )
            continue

        loaded.append(
            {
                "title": title,
                "sources_content": sources_content,
                "sources_paths": sources_paths,
                "type": section_type,
                "mode": mode,
                "print_flag": print_flag,
                "order": order,
            }
        )

    return loaded


# ---------------------------------------------------------------------------
# Markdown-to-HTML conversion
# ---------------------------------------------------------------------------

# Regex to detect ```mermaid ... ``` and ```plantuml ... ``` fenced blocks
_DIAGRAM_RE = re.compile(
    r"```(?P<lang>mermaid|plantuml)\s*\n(?P<body>.*?)```",
    re.DOTALL,
)

# File extensions treated as raw code (shown in <pre><code> blocks)
_CODE_EXTENSIONS = {".json", ".yaml", ".yml", ".toml"}

# File extensions passed through as-is (already HTML)
_HTML_EXTENSIONS = {".html", ".htm"}


def _diagram_placeholder(match: re.Match) -> str:
    """Return an HTML placeholder div for a diagram fenced-code block."""
    lang = match.group("lang")
    return (
        '<div class="diagram-placeholder">\n'
        '  <span class="diagram-icon">&#9633;</span>\n'
        f"  <span>Diagram (<code>{lang}</code>): see source file</span>\n"
        "</div>"
    )


def convert_markdown(content: str) -> str:
    """Convert a markdown string to an HTML fragment.

    Before conversion, mermaid and plantuml fenced-code blocks are replaced
    with styled placeholder divs so that the markdown parser does not mangle
    them.

    Args:
        content: Raw markdown text.

    Returns:
        HTML string.
    """
    # Replace diagram blocks with placeholders before markdown parsing
    content = _DIAGRAM_RE.sub(_diagram_placeholder, content)

    md = markdown.Markdown(
        extensions=[
            "tables",
            "fenced_code",
            "attr_list",
        ]
    )
    return md.convert(content)


def _convert_source(content: str, filepath: str) -> str:
    """Convert a single source's content to HTML based on its file extension.

    - .json / .yaml / .yml / .toml  ->  <pre><code> block
    - .html / .htm                  ->  pass through unchanged
    - everything else               ->  markdown -> HTML
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext in _CODE_EXTENSIONS:
        # Escape HTML entities so raw code renders correctly inside <pre>
        escaped = _html.escape(content)
        lang_hint = ext.lstrip(".")
        return f'<pre><code class="language-{lang_hint}">{escaped}</code></pre>'

    if ext in _HTML_EXTENSIONS:
        return content

    # Default: treat as markdown
    return convert_markdown(content)


# ---------------------------------------------------------------------------
# OpenAPI / Swagger renderer
# ---------------------------------------------------------------------------

import yaml  # noqa: E402  (pyyaml auto-installed by ensure_dependencies)


def render_openapi(content: str, file_path: str) -> str:
    """Render an OpenAPI/Swagger spec as collapsible endpoint cards.

    Parses a JSON or YAML OpenAPI spec and produces an HTML fragment with:
    - An API header block (title, version, description)
    - One collapsible card per endpoint (method + path + summary)
    - Expanded details: description, parameters table, request body, responses

    Args:
        content: Raw spec text (JSON or YAML).
        file_path: Original file path, used to decide JSON vs YAML parsing.

    Returns:
        HTML string fragment.
    """
    # --- Parse spec ---
    if file_path.endswith(".json"):
        spec = json.loads(content)
    else:
        spec = yaml.safe_load(content)

    parts: list[str] = []

    # --- API header ---
    info = spec.get("info", {})
    title = _html.escape(info.get("title", "Untitled API"))
    version = _html.escape(info.get("version", ""))
    description = _html.escape(info.get("description", ""))

    parts.append('<div class="api-header">')
    parts.append(f'  <h2>{title} <span class="api-version">v{version}</span></h2>')
    if description:
        parts.append(f"  <p>{description}</p>")
    parts.append("</div>")

    # --- Endpoints ---
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            # Skip non-HTTP-method keys (e.g. "parameters", "summary")
            if method.lower() not in (
                "get", "post", "put", "patch", "delete",
                "head", "options", "trace",
            ):
                continue
            if not isinstance(operation, dict):
                continue

            method_lower = method.lower()
            method_upper = method.upper()
            summary = _html.escape(operation.get("summary", ""))
            op_description = _html.escape(operation.get("description", ""))

            parts.append('<div class="endpoint">')

            # Toggle button
            parts.append(
                '  <button class="endpoint-toggle" '
                "onclick=\"this.parentElement.classList.toggle('expanded')\">"
            )
            parts.append(
                f'    <span class="method-badge method-{method_lower}">'
                f"{method_upper}</span>"
            )
            parts.append(
                f'    <span class="endpoint-path">{_html.escape(path)}</span>'
            )
            if summary:
                parts.append(
                    f'    <span class="endpoint-summary">{summary}</span>'
                )
            parts.append('    <span class="toggle-icon">&#9660;</span>')
            parts.append("  </button>")

            # Details (collapsed by default)
            parts.append('  <div class="endpoint-details collapsible-content">')

            if op_description:
                parts.append(
                    f'    <p class="endpoint-description">{op_description}</p>'
                )

            # Parameters table
            parameters = operation.get("parameters", [])
            if parameters:
                parts.append('    <div class="endpoint-params">')
                parts.append("      <h4>Parameters</h4>")
                parts.append("      <table>")
                parts.append(
                    "        <tr><th>Name</th><th>In</th>"
                    "<th>Type</th><th>Required</th><th>Description</th></tr>"
                )
                for param in parameters:
                    if not isinstance(param, dict):
                        continue
                    p_name = _html.escape(str(param.get("name", "")))
                    p_in = _html.escape(str(param.get("in", "")))
                    # Type can come from param.schema.type or param.type (Swagger 2)
                    p_schema = param.get("schema", {})
                    if isinstance(p_schema, dict):
                        p_type = _html.escape(
                            p_schema.get("type", p_schema.get("$ref", ""))
                        )
                    else:
                        p_type = _html.escape(str(param.get("type", "")))
                    p_required = "Yes" if param.get("required", False) else "No"
                    p_desc = _html.escape(str(param.get("description", "")))
                    parts.append(
                        f"        <tr><td>{p_name}</td><td>{p_in}</td>"
                        f"<td>{p_type}</td><td>{p_required}</td>"
                        f"<td>{p_desc}</td></tr>"
                    )
                parts.append("      </table>")
                parts.append("    </div>")

            # Request body
            request_body = operation.get("requestBody", {})
            if isinstance(request_body, dict) and request_body:
                parts.append('    <div class="endpoint-request">')
                parts.append("      <h4>Request Body</h4>")
                rb_content = request_body.get("content", {})
                for media_type, media_obj in rb_content.items():
                    if not isinstance(media_obj, dict):
                        continue
                    schema = media_obj.get("schema", {})
                    schema_str = _html.escape(
                        json.dumps(schema, indent=2)
                    )
                    parts.append(f"      <pre><code>{schema_str}</code></pre>")
                parts.append("    </div>")

            # Responses
            responses = operation.get("responses", {})
            if responses:
                parts.append('    <div class="endpoint-responses">')
                parts.append("      <h4>Responses</h4>")
                for code, resp in responses.items():
                    if not isinstance(resp, dict):
                        continue
                    resp_desc = _html.escape(resp.get("description", ""))
                    parts.append('      <div class="response-code">')
                    parts.append(
                        f'        <span class="status-code">'
                        f"{_html.escape(str(code))}</span>: {resp_desc}"
                    )
                    # Render response schema if present
                    resp_content = resp.get("content", {})
                    for media_type, media_obj in resp_content.items():
                        if not isinstance(media_obj, dict):
                            continue
                        schema = media_obj.get("schema", {})
                        schema_str = _html.escape(
                            json.dumps(schema, indent=2)
                        )
                        parts.append(
                            f"        <pre><code>{schema_str}</code></pre>"
                        )
                    # Swagger 2.0 style: schema directly on response
                    if "schema" in resp and "content" not in resp:
                        schema = resp["schema"]
                        schema_str = _html.escape(
                            json.dumps(schema, indent=2)
                        )
                        parts.append(
                            f"        <pre><code>{schema_str}</code></pre>"
                        )
                    parts.append("      </div>")
                parts.append("    </div>")

            parts.append("  </div>")  # endpoint-details
            parts.append("</div>")  # endpoint

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Blueprint appendix renderer
# ---------------------------------------------------------------------------

# Status patterns and their corresponding badge color classes
_STATUS_PATTERNS = {
    "green": [r"\[x\]", r"\[✓\]", r"Complete"],
    "red": [r"\[!\]", r"Failed"],
    "blue": [r"\[~\]", r"In Progress"],
    "gray": [r"\[ \]", r"Pending"],
}


def _status_badge(status_text: str) -> str:
    """Return an HTML badge span for the given status text.

    Maps status markers to color classes:
      - [ ] or Pending     -> gray
      - [x] or [✓] or Complete -> green
      - [!] or Failed      -> red
      - [~] or In Progress -> blue
    """
    for color, patterns in _STATUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, status_text):
                # Extract a clean label
                label = re.sub(r"\[.\]|\[✓\]", "", status_text).strip()
                if not label:
                    label_map = {
                        "green": "Complete",
                        "red": "Failed",
                        "blue": "In Progress",
                        "gray": "Pending",
                    }
                    label = label_map[color]
                return (
                    f'<span class="epic-status status-{color}">'
                    f"{_html.escape(label)}</span>"
                )
    # Fallback: gray badge with the raw text
    return (
        f'<span class="epic-status status-gray">'
        f"{_html.escape(status_text.strip())}</span>"
    )


def _parse_epic_tasks(epic_content: str) -> list[dict]:
    """Extract task references from an epic markdown file's ## Tasks section.

    Parses lines matching patterns like:
      - [ ] [task-01: Title](tasks/task-01-slug.md)
      - [✓] [task-02: Title](tasks/task-02-slug.md)

    Returns:
        List of dicts with keys: title, status, path (relative to epic dir).
    """
    tasks = []
    in_tasks_section = False

    for line in epic_content.splitlines():
        stripped = line.strip()

        if stripped.startswith("## Tasks"):
            in_tasks_section = True
            continue

        if in_tasks_section and stripped.startswith("## "):
            break  # New section reached

        if not in_tasks_section:
            continue

        # Match task lines: - [x] [task-NN: Title](tasks/task-NN-slug.md)
        task_match = re.match(
            r"^-\s+(\[.\]|\[✓\])\s+\[([^\]]+)\]\(([^)]+)\)",
            stripped,
        )
        if task_match:
            status_marker = task_match.group(1)
            task_title = task_match.group(2)
            task_path = task_match.group(3)
            tasks.append(
                {
                    "title": task_title,
                    "status": status_marker,
                    "path": task_path,
                }
            )

    return tasks


def _parse_task_file(task_path: Path) -> dict:
    """Read and parse a task markdown file.

    Extracts title, status, dependencies, and full content.

    Args:
        task_path: Path to the task markdown file.

    Returns:
        Dict with keys: title, status, dependencies, content.
        Returns None if file doesn't exist or can't be read.
    """
    if not task_path.exists():
        return None

    try:
        content = task_path.read_text(encoding="utf-8")
    except Exception:
        return None

    title = "Untitled Task"
    status = "Pending"
    dependencies = "None"

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# ") and title == "Untitled Task":
            title = stripped[2:].strip()
        elif stripped.startswith("**Status:**"):
            status = stripped.replace("**Status:**", "").strip()
        elif stripped.startswith("**Dependencies:**"):
            dependencies = stripped.replace("**Dependencies:**", "").strip()

    return {
        "title": title,
        "status": status,
        "dependencies": dependencies,
        "content": content,
    }


def render_blueprints(blueprints_dir: str) -> str:
    """Render .blueprints/ folder contents as an HTML appendix section.

    Discovers epic folders, parses each epic's markdown for title, status,
    context, and task list.  Renders epic subsections with task tables and
    expandable task details.

    Args:
        blueprints_dir: Path to the .blueprints/ directory.

    Returns:
        HTML string for the blueprints appendix.
    """
    bp_path = Path(blueprints_dir)
    if not bp_path.exists():
        return "<p><em>No blueprints found.</em></p>"

    epics = sorted(bp_path.glob("epic-*/epic-*.md"))
    if not epics:
        return "<p><em>No blueprints found.</em></p>"

    parts: list[str] = []

    for epic_file in epics:
        epic_dir = epic_file.parent

        try:
            epic_content = epic_file.read_text(encoding="utf-8")
        except Exception as e:
            print(
                f"Warning: Failed to read epic file {epic_file}: {e}",
                file=sys.stderr,
            )
            continue

        # Parse epic metadata
        epic_title = "Untitled Epic"
        epic_status = "Pending"
        context_lines: list[str] = []
        in_context = False

        for line in epic_content.splitlines():
            stripped = line.strip()
            if stripped.startswith("# ") and epic_title == "Untitled Epic":
                epic_title = stripped[2:].strip()
                # Remove "Epic: " prefix if present
                if epic_title.startswith("Epic: "):
                    epic_title = epic_title[6:]
            elif stripped.startswith("**Status:**"):
                epic_status = stripped.replace("**Status:**", "").strip()
            elif stripped.startswith("## Context"):
                in_context = True
                continue
            elif stripped.startswith("## ") and in_context:
                in_context = False
            elif in_context and stripped:
                context_lines.append(stripped)

        context_summary = " ".join(context_lines[:3])  # First 3 non-empty lines
        status_html = _status_badge(epic_status)

        # Parse task list from epic
        epic_tasks = _parse_epic_tasks(epic_content)

        # Build epic section
        parts.append('<div class="blueprint-epic">')
        parts.append(
            f"  <h2>{_html.escape(epic_title)} {status_html}</h2>"
        )
        if context_summary:
            parts.append(f"  <p>{_html.escape(context_summary)}</p>")

        # Task table
        if epic_tasks:
            parts.append('  <table class="task-table">')
            parts.append("    <thead>")
            parts.append(
                "      <tr><th>Task</th><th>Status</th>"
                "<th>Dependencies</th></tr>"
            )
            parts.append("    </thead>")
            parts.append("    <tbody>")

            task_details_parts: list[str] = []

            for task_ref in epic_tasks:
                task_file_path = epic_dir / task_ref["path"]
                task_data = _parse_task_file(task_file_path)

                if task_data:
                    task_title = task_data["title"]
                    task_status_badge = _status_badge(task_data["status"])
                    task_deps = task_data["dependencies"]
                else:
                    task_title = task_ref["title"]
                    task_status_badge = _status_badge(task_ref["status"])
                    task_deps = "N/A"
                    print(
                        f"Warning: Task file not found: {task_file_path}",
                        file=sys.stderr,
                    )

                parts.append("      <tr>")
                parts.append(
                    f"        <td>{_html.escape(task_title)}</td>"
                )
                parts.append(f"        <td>{task_status_badge}</td>")
                parts.append(
                    f"        <td>{_html.escape(task_deps)}</td>"
                )
                parts.append("      </tr>")

                # Build details element for this task
                if task_data:
                    task_html = convert_markdown(task_data["content"])
                    task_details_parts.append(
                        f'  <details class="task-details">\n'
                        f"    <summary>"
                        f"{_html.escape(task_title)}</summary>\n"
                        f'    <div class="task-content">\n'
                        f"      {task_html}\n"
                        f"    </div>\n"
                        f"  </details>"
                    )

            parts.append("    </tbody>")
            parts.append("  </table>")

            # Add task details after the table
            parts.extend(task_details_parts)

        parts.append("</div>")

    return "\n".join(parts)


def process_section_content(section: dict) -> str:
    """Convert all source contents of a section into a single HTML string.

    Routes to the appropriate renderer based on the section's ``type`` field:

    - ``"openapi"``    -- render each source with :func:`render_openapi`
    - ``"blueprints"`` -- render the directory with :func:`render_blueprints`
    - anything else    -- default per-file conversion via :func:`_convert_source`

    When a section contains multiple sources they are separated by an
    ``<hr>`` element.

    Args:
        section: A section dict as returned by ``load_sections()``, expected
                 to contain ``sources_content`` (list[str]),
                 ``sources_paths`` (list[str]), and optionally ``type``.

    Returns:
        Combined HTML string for the entire section.
    """
    section_type = section.get("type", "")
    contents = section.get("sources_content", [])
    paths = section.get("sources_paths", [])

    if section_type == "openapi":
        # Use the OpenAPI renderer for each source file
        html_parts = []
        for idx, content in enumerate(contents):
            filepath = paths[idx] if idx < len(paths) else "unknown.yaml"
            html_parts.append(render_openapi(content, filepath))
        return "\n".join(html_parts)

    if section_type == "blueprints":
        # Use the blueprint renderer — sources[0] is the directory path
        source_dir = paths[0] if paths else ".blueprints"
        return render_blueprints(source_dir)

    # Default: per-file conversion based on extension
    html_parts = []
    for idx, content in enumerate(contents):
        filepath = paths[idx] if idx < len(paths) else "unknown.md"
        html_parts.append(_convert_source(content, filepath))

    return "\n<hr>\n".join(html_parts)


# ---------------------------------------------------------------------------
# Subsection extraction & sidebar navigation
# ---------------------------------------------------------------------------

# Regex to find <h2> and <h3> tags (with or without existing attributes)
_HEADING_RE = re.compile(
    r"<(?P<tag>h[23])(?P<attrs>[^>]*)>(?P<text>.*?)</(?P=tag)>",
    re.DOTALL,
)


def extract_subsections(html_content: str, section_slug: str) -> Tuple[str, list]:
    """Parse HTML for h2/h3 headings, inject unique IDs, and return subsection metadata.

    For each ``<h2>`` or ``<h3>`` found in *html_content*, a unique ``id``
    attribute of the form ``subsection-{section_slug}-{heading_slug}`` is
    injected into the tag (replacing any existing ``id``).

    Args:
        html_content: The converted HTML string for a single section.
        section_slug: The slug for the parent section (used to namespace IDs).

    Returns:
        A tuple of (modified_html, subsections) where *subsections* is a list
        of dicts with keys ``id``, ``label``, and ``tag`` (``"h2"`` or ``"h3"``).
    """
    subsections: list[dict] = []

    def _replace_heading(match: re.Match) -> str:
        tag = match.group("tag")
        attrs = match.group("attrs")
        text = match.group("text")

        # Strip HTML tags from text to get plain label
        label = re.sub(r"<[^>]+>", "", text).strip()
        heading_slug = _slugify(label)
        sub_id = f"subsection-{section_slug}-{heading_slug}"

        subsections.append({"id": sub_id, "label": label, "tag": tag})

        # Remove any existing id attribute from attrs
        cleaned_attrs = re.sub(r'\s*id="[^"]*"', "", attrs)
        return f'<{tag} id="{sub_id}"{cleaned_attrs}>{text}</{tag}>'

    modified_html = _HEADING_RE.sub(_replace_heading, html_content)
    return modified_html, subsections


def generate_sidebar_html(sections: list) -> str:
    """Generate the sidebar navigation HTML from processed sections.

    Each section becomes a top-level nav link. Subsections (extracted from h2/h3
    headings) are nested beneath their parent section. An appendix separator is
    inserted before sections with ``order >= 99``.

    Args:
        sections: List of section dicts. Each must have ``title``, ``order``,
                  and ``subsections`` (list of dicts with ``id`` and ``label``).

    Returns:
        HTML string for the sidebar navigation list.
    """
    parts: list[str] = []
    appendix_separator_added = False

    for section in sections:
        title = section.get("title", "Untitled")
        order = section.get("order", 9999)
        slug = _slugify(title)
        subsections = section.get("subsections", [])

        # Add appendix separator before the first section with order >= 99
        if order >= 99 and not appendix_separator_added:
            parts.append('        <div class="appendix-separator"></div>')
            appendix_separator_added = True

        print_flag = section.get("print_flag", True)
        checked = "checked" if print_flag else ""

        parts.append(f'        <div class="nav-section" data-section-id="section-{slug}">')
        parts.append(
            f'          <input type="checkbox" class="print-check" '
            f'data-section="section-{slug}" {checked}>'
            f'<a href="#section-{slug}" class="nav-link">'
            f"{_html.escape(title)}</a>"
        )

        if subsections:
            parts.append('          <div class="nav-subsections">')
            for sub in subsections:
                parts.append(
                    f'            <a href="#{sub["id"]}" class="nav-sublink">'
                    f'{_html.escape(sub["label"])}</a>'
                )
            parts.append("          </div>")

        parts.append("        </div>")

    return "\n".join(parts)


def load_template() -> str:
    """Read the HTML template and return it as a string.

    The template lives at ``rt-agents/templates/documentation.html`` relative
    to the repository root.  We locate it relative to this script's own
    directory (``rt-agents/scripts/``) so it works regardless of the caller's
    working directory.

    Returns:
        The raw template string with Python ``.format()`` placeholders:
        ``{project_name}``, ``{sidebar_html}``, ``{sections_html}``,
        ``{footer_html}``.
    """
    template_path = Path(__file__).parent.parent / "templates" / "documentation.html"
    return template_path.read_text(encoding="utf-8")


def generate_sections_html(sections: list) -> str:
    """Generate the main content HTML by wrapping each section in proper markup.

    Each section is wrapped in a ``<section>`` tag with a unique ``id`` and a
    ``data-print`` attribute controlling print visibility.  An ``<hr>`` divider
    is placed between sections, and an appendix divider is inserted before the
    first section with ``order >= 99``.

    Args:
        sections: List of section dicts.  Each must have ``title``, ``order``,
                  ``print_flag``, and ``html`` (the converted HTML content).

    Returns:
        Combined HTML string for all sections.
    """
    parts: list[str] = []
    appendix_divider_added = False

    for idx, section in enumerate(sections):
        title = section.get("title", "Untitled")
        order = section.get("order", 9999)
        print_flag = "true" if section.get("print_flag", True) else "false"
        slug = _slugify(title)
        html_content = section.get("html", "")

        # Add divider between sections (but not before the very first one)
        if idx > 0:
            parts.append('            <hr class="section-divider">')

        # Add appendix divider before the first section with order >= 99
        if order >= 99 and not appendix_divider_added:
            parts.append(
                '            <div class="appendix-divider">\n'
                "              <span>Appendix</span>\n"
                "            </div>"
            )
            appendix_divider_added = True

        parts.append(
            f'            <section class="section" id="section-{slug}" '
            f'data-print="{print_flag}">'
        )
        parts.append(
            f'              <h1 class="section-heading">'
            f"{_html.escape(title)}</h1>"
        )
        parts.append(f"              {html_content}")
        parts.append("            </section>")

    return "\n".join(parts)


def generate_footer_html(project_name: str, sections: list, project_config: dict = None) -> str:
    """Generate the footer HTML with generation date.

    Args:
        project_name: The project name from config.
        sections: List of section dicts (unused, kept for API compatibility).
        project_config: The project dict from parse_config(), used for repo_url.

    Returns:
        HTML string for the footer.
    """
    from datetime import date

    today = date.today().isoformat()

    project_config = project_config or {}
    repo_url = project_config.get("repo_url", "")
    if repo_url:
        name_html = f'<a href="{_html.escape(repo_url)}">{_html.escape(project_name)}</a>'
    else:
        name_html = _html.escape(project_name)

    return (
        f"        <p>{name_html} &mdash; Generated {today} &mdash; "
        f"rt-agents documentation</p>"
    )


def assemble_and_write(sections: list, project_config: dict) -> None:
    """Load the template, fill placeholders, and write the final HTML file.

    Orchestrates sidebar, sections, and footer HTML generation, fills in
    the template placeholders, creates the output directory if needed,
    and writes ``index.html``.

    Args:
        sections: List of fully processed section dicts (with ``html``,
                  ``subsections``, etc.).
        project_config: The ``project`` dict from ``parse_config()``.
    """
    project_name = project_config.get("name", "Untitled Project")
    output_dir = Path.cwd() / project_config.get("output_dir", ".rt-documentation")

    template = load_template()

    sidebar_html = generate_sidebar_html(sections)
    sections_html = generate_sections_html(sections)
    footer_html = generate_footer_html(project_name, sections, project_config)

    final_html = template.format(
        project_name=project_name,
        sidebar_html=sidebar_html,
        sections_html=sections_html,
        footer_html=footer_html,
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    # Write index.html (always-current version)
    output_path = output_dir / "index.html"
    output_path.write_text(final_html, encoding="utf-8")
    print(f"Documentation written to {output_path}")

    # Write timestamped snapshot
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    slug_name = _slugify(project_name) or "docs"
    snapshot_path = output_dir / f"{slug_name}_{timestamp}.html"
    snapshot_path.write_text(final_html, encoding="utf-8")
    print(f"Snapshot written to {snapshot_path}")


def main():
    """Run the full documentation generation pipeline.

    1. Parse the TOML config
    2. Load and validate section sources
    3. Convert each section's content to HTML
    4. Extract subsections (h2/h3 headings) for sidebar navigation
    5. Assemble everything into the HTML template and write output
    """
    config = parse_config()
    sections = load_sections(config)

    # Process each section: convert markdown/code to HTML, extract subsections
    for section in sections:
        html_content = process_section_content(section)
        slug = _slugify(section["title"])
        html_content, subsections = extract_subsections(html_content, slug)
        section["html"] = html_content
        section["subsections"] = subsections

    print(f"Loaded {len(sections)} sections from config")

    assemble_and_write(sections, config["project"])


if __name__ == "__main__":
    main()
