# rt-gamma Plugin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create an rt-gamma plugin that converts Markdown files to Gamma.app presentations via `/rt-gamma` slash command.

**Architecture:** Slash command (`rt-gamma.md`) orchestrates config detection and calls Python scripts (`generate.py` for single files, `batch.py` for folders). Scripts use `gamma_client.py` for API calls and `config.py` for loading `.claude/rt-gamma.toml`.

**Tech Stack:** Python 3.11+, requests library, TOML config

---

### Task 1: Create Plugin Folder Structure

**Files:**
- Create: `rt-gamma/.claude-plugin/plugin.json`
- Create: `rt-gamma/commands/` (directory)
- Create: `rt-gamma/scripts/` (directory)

**Step 1: Create the directory structure**

```bash
mkdir -p rt-gamma/.claude-plugin
mkdir -p rt-gamma/commands
mkdir -p rt-gamma/scripts
```

**Step 2: Create plugin.json**

Create file `rt-gamma/.claude-plugin/plugin.json`:

```json
{
  "name": "rt-gamma",
  "version": "1.0.0",
  "description": "Convert Markdown to Gamma.app presentations via slash command",
  "author": {
    "name": "rt"
  },
  "license": "MIT",
  "keywords": ["gamma", "presentations", "markdown", "slides", "converter"]
}
```

**Step 3: Verify structure exists**

Run: `ls -la rt-gamma/`
Expected: `.claude-plugin`, `commands`, `scripts` directories

**Step 4: Commit**

```bash
git add rt-gamma/
git commit -m "feat(rt-gamma): create plugin folder structure"
```

---

### Task 2: Create config.py

**Files:**
- Create: `rt-gamma/scripts/config.py`

**Step 1: Create config.py**

Create file `rt-gamma/scripts/config.py`:

```python
"""Configuration management for rt-gamma plugin."""
import os
import sys
from pathlib import Path
from typing import Optional

# Python 3.11+ has tomllib built-in
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tomli", "-q"])
        import tomli as tomllib


def find_project_root() -> Path:
    """Find the project root by looking for .claude directory."""
    # Start from current working directory
    current = Path.cwd()

    # Walk up looking for .claude directory
    for parent in [current] + list(current.parents):
        if (parent / ".claude").is_dir():
            return parent

    # Fallback to current directory
    return current


def get_config_path() -> Path:
    """Get the path to the rt-gamma config file."""
    return find_project_root() / ".claude" / "rt-gamma.toml"


def config_exists() -> bool:
    """Check if config file exists."""
    return get_config_path().exists()


def load_config() -> dict:
    """
    Load configuration from .claude/rt-gamma.toml.

    Returns dict with all config values, using defaults for missing keys.
    Raises ValueError if api_key is missing or empty.
    """
    config_path = get_config_path()

    # Defaults
    defaults = {
        "api_key": "",
        "theme": "",
        "template": "",
        "text_mode": "preserve",
        "image_source": "ai",
        "card_split": "inputTextBreaks",
        "batch_pattern": "*_presentation.md",
    }

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    # Load TOML
    with open(config_path, "rb") as f:
        user_config = tomllib.load(f)

    # Merge with defaults
    config = {**defaults, **user_config}

    # Validate API key
    if not config.get("api_key"):
        raise ValueError(
            f"API key not found in config. "
            f"Please set 'api_key' in {config_path}"
        )

    return config


def create_config_template(path: Optional[Path] = None) -> Path:
    """
    Create a config file with placeholder values.

    Returns the path to the created file.
    """
    if path is None:
        path = get_config_path()

    # Ensure .claude directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    template = '''# rt-gamma configuration
# Get your API key from: https://gamma.app/settings/api

# Required: Your Gamma API key
api_key = ""

# Optional: Default Gamma theme ID (leave empty for Gamma default)
theme = ""

# Optional: Default Gamma template ID for template-based generation
template = ""

# Text processing mode: generate | condense | preserve
text_mode = "preserve"

# Image source: ai | unsplash | giphy | pexels | pictographic | none
image_source = "ai"

# Card/slide splitting: auto | inputTextBreaks (respects --- markers)
card_split = "inputTextBreaks"

# Batch mode: file pattern to match
batch_pattern = "*_presentation.md"
'''

    path.write_text(template, encoding="utf-8")
    return path
```

**Step 2: Verify file created**

Run: `cat rt-gamma/scripts/config.py | head -20`
Expected: See the config module header

**Step 3: Commit**

```bash
git add rt-gamma/scripts/config.py
git commit -m "feat(rt-gamma): add config loader for .claude/rt-gamma.toml"
```

---

### Task 3: Create gamma_client.py

**Files:**
- Create: `rt-gamma/scripts/gamma_client.py`

**Step 1: Create gamma_client.py**

Create file `rt-gamma/scripts/gamma_client.py`:

```python
"""Gamma API client for generating presentations."""
import sys
from typing import Optional

# Auto-install requests if missing
try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


class GammaAPIClient:
    """Client for the Gamma public API."""

    def __init__(self, api_key: str, base_url: str = "https://public-api.gamma.app/v1.0"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        })

    def list_themes(self) -> list[dict]:
        """Fetch all available themes in the workspace."""
        url = f"{self.base_url}/themes"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data

    def generate_presentation(
        self,
        input_text: str,
        text_mode: str = "preserve",
        format_type: str = "presentation",
        theme_id: Optional[str] = None,
        num_cards: int = 10,
        card_split: str = "inputTextBreaks",
        image_source: str = "aiGenerated",
    ) -> dict:
        """
        Generate a new presentation using the Gamma API.

        Args:
            input_text: Content to generate the presentation from (max 100k tokens)
            text_mode: How to handle text - 'generate', 'condense', or 'preserve'
            format_type: Output format - 'presentation', 'document', 'social', 'webpage'
            theme_id: Theme identifier (get from list_themes)
            num_cards: Number of cards/slides (1-60 for Pro, 1-75 for Ultra)
            card_split: 'auto' or 'inputTextBreaks' (respects --- markers)
            image_source: Image source type

        Returns:
            API response with generation details including generationId
        """
        payload = {
            "inputText": input_text,
            "textMode": text_mode,
            "format": format_type,
            "numCards": num_cards,
            "cardSplit": card_split,
            "imageOptions": {"source": image_source},
        }

        if theme_id:
            payload["themeId"] = theme_id

        url = f"{self.base_url}/generations"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def create_from_template(
        self,
        gamma_id: str,
        prompt: str,
        theme_id: Optional[str] = None,
    ) -> dict:
        """
        Create a presentation from an existing template.

        Args:
            gamma_id: The template ID to use
            prompt: Content and instructions for filling the template
            theme_id: Override the template's theme

        Returns:
            API response with generation details
        """
        payload = {
            "gammaId": gamma_id,
            "prompt": prompt,
            "imageOptions": {"model": "flux-1-quick", "style": "match my theme"},
        }

        if theme_id:
            payload["themeId"] = theme_id

        url = f"{self.base_url}/generations/from-template"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_generation_status(self, generation_id: str) -> dict:
        """Check the status of a generation and get URLs if ready."""
        url = f"{self.base_url}/generations/{generation_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
```

**Step 2: Verify file created**

Run: `cat rt-gamma/scripts/gamma_client.py | head -20`
Expected: See the API client module header

**Step 3: Commit**

```bash
git add rt-gamma/scripts/gamma_client.py
git commit -m "feat(rt-gamma): add Gamma API client"
```

---

### Task 4: Create markdown_utils.py

**Files:**
- Create: `rt-gamma/scripts/markdown_utils.py`

**Step 1: Create markdown_utils.py**

Create file `rt-gamma/scripts/markdown_utils.py`:

```python
"""Markdown parsing utilities for extracting content and titles."""
import re
from pathlib import Path
from typing import Optional


def extract_title(content: str) -> Optional[str]:
    """
    Extract title from markdown content.

    Looks for:
    1. YAML frontmatter 'title' field
    2. First H1 heading (# Title)
    3. First line if it looks like a title

    Returns None if no clear title is found.
    """
    # Check for YAML frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()

    # Check for H1 heading
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if h1_match:
        return h1_match.group(1).strip()

    # Check first non-empty line (if it looks like a title)
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('---'):
            # If it's short and doesn't look like a paragraph, treat as title
            if len(line) < 100 and not line.endswith('.'):
                return line
            break

    return None


def read_markdown_file(file_path: str) -> str:
    """Read and return the contents of a markdown file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Markdown file not found: {file_path}")
    if path.suffix.lower() not in ['.md', '.markdown', '.txt']:
        raise ValueError(f"Expected markdown file, got: {path.suffix}")

    return path.read_text(encoding='utf-8')


def prepare_content(content: str, title: Optional[str] = None) -> str:
    """
    Prepare markdown content for Gamma API.

    Optionally prepends a title if provided.
    Preserves --- markers for card breaks if present.

    Returns prepared content string.
    """
    if title:
        # Add title as H1 if not already present
        if not content.strip().startswith('# '):
            content = f"# {title}\n\n{content}"

    return content
```

**Step 2: Verify file created**

Run: `cat rt-gamma/scripts/markdown_utils.py | head -20`
Expected: See the markdown utilities module header

**Step 3: Commit**

```bash
git add rt-gamma/scripts/markdown_utils.py
git commit -m "feat(rt-gamma): add markdown parsing utilities"
```

---

### Task 5: Create generate.py (Single File Generation)

**Files:**
- Create: `rt-gamma/scripts/generate.py`

**Step 1: Create generate.py**

Create file `rt-gamma/scripts/generate.py`:

```python
#!/usr/bin/env python3
"""Generate a single Gamma presentation from a markdown file."""
import json
import sys
import time
from pathlib import Path

from config import load_config, config_exists, get_config_path
from gamma_client import GammaAPIClient
from markdown_utils import extract_title, read_markdown_file, prepare_content


def generate_presentation(file_path: str) -> dict:
    """
    Generate a presentation from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        dict with success, url, html_path, and optionally error
    """
    path = Path(file_path).resolve()

    # Load config
    try:
        config = load_config()
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Config not found. Create {get_config_path()}"
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}

    # Read markdown
    try:
        content = read_markdown_file(str(path))
    except (FileNotFoundError, ValueError) as e:
        return {"success": False, "error": str(e)}

    # Extract title
    title = extract_title(content)
    if not title:
        title = path.stem.replace("_", " ").title()

    # Prepare content
    final_content = prepare_content(content, title)

    # Create client
    client = GammaAPIClient(config["api_key"])

    # Map config image_source to API value
    image_source_map = {
        "ai": "aiGenerated",
        "unsplash": "unsplash",
        "giphy": "giphy",
        "pexels": "webFreeToUse",
        "pictographic": "pictographic",
        "none": "noImages",
    }
    image_source = image_source_map.get(config.get("image_source", "ai"), "aiGenerated")

    try:
        # Check if using template
        template_id = config.get("template", "").strip()
        theme_id = config.get("theme", "").strip() or None

        if template_id:
            # Template-based generation
            result = client.create_from_template(
                gamma_id=template_id,
                prompt=final_content,
                theme_id=theme_id,
            )
        else:
            # Standard generation
            result = client.generate_presentation(
                input_text=final_content,
                text_mode=config.get("text_mode", "preserve"),
                format_type="presentation",
                theme_id=theme_id,
                card_split=config.get("card_split", "inputTextBreaks"),
                image_source=image_source,
            )

        generation_id = result.get("generationId")
        if not generation_id:
            return {
                "success": False,
                "error": "No generation ID returned from API"
            }

        # Poll for completion (max 2 minutes)
        max_attempts = 60
        for _ in range(max_attempts):
            time.sleep(2)
            status = client.get_generation_status(generation_id)

            if status.get("status") == "completed":
                gamma_url = status.get("gammaUrl", status.get("url"))

                # Create HTML redirect file
                html_path = path.with_suffix(".html")
                html_content = f'''<!DOCTYPE html>
<html>
<head><meta http-equiv="refresh" content="0;url={gamma_url}"></head>
</html>'''
                html_path.write_text(html_content, encoding="utf-8")

                return {
                    "success": True,
                    "url": gamma_url,
                    "html_path": str(html_path),
                    "title": title,
                }

            elif status.get("status") == "failed":
                return {
                    "success": False,
                    "error": status.get("error", "Generation failed")
                }

        return {
            "success": False,
            "error": "Timeout: Generation took longer than 2 minutes"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: generate.py <markdown_file>"}))
        sys.exit(1)

    file_path = sys.argv[1]
    result = generate_presentation(file_path)

    print(json.dumps(result))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
```

**Step 2: Verify file created**

Run: `cat rt-gamma/scripts/generate.py | head -20`
Expected: See the generate module header

**Step 3: Commit**

```bash
git add rt-gamma/scripts/generate.py
git commit -m "feat(rt-gamma): add single file generation script"
```

---

### Task 6: Create batch.py (Batch Folder Generation)

**Files:**
- Create: `rt-gamma/scripts/batch.py`

**Step 1: Create batch.py**

Create file `rt-gamma/scripts/batch.py`:

```python
#!/usr/bin/env python3
"""Batch generate Gamma presentations from a folder of markdown files."""
import fnmatch
import json
import sys
import time
from pathlib import Path

from config import load_config, config_exists, get_config_path
from gamma_client import GammaAPIClient
from markdown_utils import extract_title, read_markdown_file, prepare_content


def find_presentation_files(directory: Path, pattern: str) -> list[Path]:
    """
    Find all matching markdown files without corresponding .html files.

    Args:
        directory: Directory to search
        pattern: Glob pattern to match (e.g., "*_presentation.md")

    Returns:
        List of markdown paths that need processing
    """
    files_to_process = []

    for md_file in directory.rglob(pattern):
        html_file = md_file.with_suffix(".html")
        if not html_file.exists():
            files_to_process.append(md_file)

    return sorted(files_to_process)


def generate_single(
    client: GammaAPIClient,
    file_path: Path,
    config: dict,
) -> dict:
    """
    Generate a single presentation.

    Returns dict with success, url, error, etc.
    """
    try:
        # Read and prepare content
        content = read_markdown_file(str(file_path))
        title = extract_title(content)

        if not title:
            # Use filename as fallback title
            title = file_path.stem.replace("_presentation", "").replace("_", " ").title()

        final_content = prepare_content(content, title)

        # Map config image_source to API value
        image_source_map = {
            "ai": "aiGenerated",
            "unsplash": "unsplash",
            "giphy": "giphy",
            "pexels": "webFreeToUse",
            "pictographic": "pictographic",
            "none": "noImages",
        }
        image_source = image_source_map.get(config.get("image_source", "ai"), "aiGenerated")

        # Check if using template
        template_id = config.get("template", "").strip()
        theme_id = config.get("theme", "").strip() or None

        if template_id:
            result = client.create_from_template(
                gamma_id=template_id,
                prompt=final_content,
                theme_id=theme_id,
            )
        else:
            result = client.generate_presentation(
                input_text=final_content,
                text_mode=config.get("text_mode", "preserve"),
                format_type="presentation",
                theme_id=theme_id,
                card_split=config.get("card_split", "inputTextBreaks"),
                image_source=image_source,
            )

        generation_id = result.get("generationId")
        if not generation_id:
            return {
                "path": str(file_path),
                "success": False,
                "error": "No generation ID returned"
            }

        # Poll for completion (max 2 minutes)
        max_attempts = 60
        for _ in range(max_attempts):
            time.sleep(2)
            status = client.get_generation_status(generation_id)

            if status.get("status") == "completed":
                gamma_url = status.get("gammaUrl", status.get("url"))

                # Create HTML redirect file
                html_path = file_path.with_suffix(".html")
                html_content = f'''<!DOCTYPE html>
<html>
<head><meta http-equiv="refresh" content="0;url={gamma_url}"></head>
</html>'''
                html_path.write_text(html_content, encoding="utf-8")

                return {
                    "path": str(file_path),
                    "success": True,
                    "url": gamma_url,
                    "html_path": str(html_path),
                }

            elif status.get("status") == "failed":
                return {
                    "path": str(file_path),
                    "success": False,
                    "error": status.get("error", "Generation failed")
                }

        return {
            "path": str(file_path),
            "success": False,
            "error": "Timeout: Generation took longer than 2 minutes"
        }

    except Exception as e:
        return {
            "path": str(file_path),
            "success": False,
            "error": str(e)
        }


def batch_generate(directory: str) -> dict:
    """
    Generate presentations for all matching files in a directory.

    Args:
        directory: Path to the directory to process

    Returns:
        dict with total, success, failed counts and results array
    """
    dir_path = Path(directory).resolve()

    if not dir_path.exists():
        return {
            "success": False,
            "error": f"Directory not found: {directory}"
        }

    if not dir_path.is_dir():
        return {
            "success": False,
            "error": f"Not a directory: {directory}"
        }

    # Load config
    try:
        config = load_config()
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Config not found. Create {get_config_path()}"
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}

    # Find files
    pattern = config.get("batch_pattern", "*_presentation.md")
    files = find_presentation_files(dir_path, pattern)

    if not files:
        return {
            "success": True,
            "total": 0,
            "processed": 0,
            "failed": 0,
            "results": [],
            "message": f"No files matching '{pattern}' need processing (all have .html files)"
        }

    # Create client
    client = GammaAPIClient(config["api_key"])

    # Process files sequentially to avoid rate limits
    results = []
    for file_path in files:
        result = generate_single(client, file_path, config)
        results.append(result)

    # Calculate summary
    successes = [r for r in results if r.get("success")]
    failures = [r for r in results if not r.get("success")]

    return {
        "success": len(failures) == 0,
        "total": len(files),
        "processed": len(successes),
        "failed": len(failures),
        "results": results,
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: batch.py <directory>"}))
        sys.exit(1)

    directory = sys.argv[1]
    result = batch_generate(directory)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
```

**Step 2: Verify file created**

Run: `cat rt-gamma/scripts/batch.py | head -20`
Expected: See the batch module header

**Step 3: Commit**

```bash
git add rt-gamma/scripts/batch.py
git commit -m "feat(rt-gamma): add batch folder generation script"
```

---

### Task 7: Create rt-gamma.md Slash Command

**Files:**
- Create: `rt-gamma/commands/rt-gamma.md`

**Step 1: Create rt-gamma.md**

Create file `rt-gamma/commands/rt-gamma.md`:

```markdown
---
description: Convert Markdown to Gamma.app presentations
---

Convert a Markdown file or folder of files to Gamma.app presentations.

## Instructions

Parse `$ARGUMENTS` to get the path. The path can be:
- A single markdown file (e.g., `presentation.md`)
- A folder containing markdown files (batch mode)

### Step 1: Check if config exists

Check if `.claude/rt-gamma.toml` exists in the project root.

If the config file does NOT exist:

1. Tell the user: "No rt-gamma config found. I'll create one at `.claude/rt-gamma.toml`"

2. Ask the user using AskUserQuestion:
   - Question: "How would you like to configure rt-gamma?"
   - Options:
     - "Interactive setup" - Walk through configuration options
     - "Manual setup" - Create template file for manual editing

3. If "Interactive setup":
   - Ask for their Gamma API key (required): "Enter your Gamma API key (get one at https://gamma.app/settings/api)"
   - Ask for default text mode: "preserve" (keep text as-is), "generate" (expand content), "condense" (summarize)
   - Ask for default image source: "ai" (AI generated), "unsplash", "none"
   - Create the config file with their values
   - Continue to Step 2

4. If "Manual setup":
   - Create the config template at `.claude/rt-gamma.toml` with placeholder values
   - Tell user: "Config template created at `.claude/rt-gamma.toml`. Please fill in your `api_key` and run the command again."
   - STOP execution here

### Step 2: Validate config has API key

Read `.claude/rt-gamma.toml` and check that `api_key` is not empty.

If `api_key` is empty, tell the user:
"API key is missing. Please add your Gamma API key to `.claude/rt-gamma.toml`"
STOP execution.

### Step 3: Determine path type

If no path provided in `$ARGUMENTS`:
- Ask user: "Please provide the path to a markdown file or folder"
- STOP until they provide a path

Check if the path is a file or directory:
- If it's a file → Go to Step 4 (Single Generation)
- If it's a directory → Go to Step 5 (Batch Generation)
- If path doesn't exist → Error: "Path not found: {path}"

### Step 4: Single File Generation

Run the generate script:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/generate.py" "PATH_TO_FILE"
```

The script outputs JSON. Parse it and report to the user:

If success:
- "Presentation created: {url}"
- "HTML redirect saved to: {html_path}"

If error:
- "Error: {error message}"

### Step 5: Batch Generation

Tell user: "Starting batch generation for folder: {path}"
Tell user: "Looking for files matching the pattern in config (default: *_presentation.md)"

Run the batch script:

```bash
python "${CLAUDE_PLUGIN_ROOT}/scripts/batch.py" "PATH_TO_FOLDER"
```

The script outputs JSON. Parse it and report to the user:

- "Processed {processed} of {total} files"
- List each result with URL or error
- If any failures, list them with their error messages

## Examples

Single file:
```
/rt-gamma my_talk.md
```

Batch folder:
```
/rt-gamma ./presentations/
```
```

**Step 2: Verify file created**

Run: `cat rt-gamma/commands/rt-gamma.md | head -20`
Expected: See the command frontmatter and description

**Step 3: Commit**

```bash
git add rt-gamma/commands/rt-gamma.md
git commit -m "feat(rt-gamma): add /rt-gamma slash command"
```

---

### Task 8: Update Marketplace Registry

**Files:**
- Modify: `.claude-plugin/marketplace.json`

**Step 1: Update marketplace.json**

Edit `.claude-plugin/marketplace.json` to add rt-gamma to the plugins array:

```json
{
  "name": "rt-plugins",
  "owner": {
    "name": "rt"
  },
  "plugins": [
    {
      "name": "rt-voice",
      "source": "./rt-voice",
      "description": "Play themed sounds for Claude Code hook events",
      "version": "1.1.0"
    },
    {
      "name": "rt-gamma",
      "source": "./rt-gamma",
      "description": "Convert Markdown to Gamma.app presentations",
      "version": "1.0.0"
    }
  ]
}
```

**Step 2: Verify JSON is valid**

Run: `cat .claude-plugin/marketplace.json | python -m json.tool`
Expected: Pretty-printed valid JSON

**Step 3: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit -m "feat(marketplace): add rt-gamma plugin to registry"
```

---

### Task 9: Create README.md

**Files:**
- Create: `rt-gamma/README.md`

**Step 1: Create README.md**

Create file `rt-gamma/README.md`:

```markdown
# rt-gamma

Convert Markdown files to beautiful [Gamma.app](https://gamma.app) presentations directly from Claude Code.

## Installation

```bash
# Add the marketplace (if not already added)
/plugin marketplace add ryanturnercom/rt-plugins

# Install rt-gamma
/plugin install rt-gamma@rt-plugins
```

## Usage

### Single File

```bash
/rt-gamma my_presentation.md
```

Converts a single markdown file to a Gamma presentation.

### Batch Mode

```bash
/rt-gamma ./presentations/
```

Converts all `*_presentation.md` files in the folder (and subfolders) that don't already have `.html` files.

## First-Time Setup

On first run, rt-gamma will prompt you to configure:

1. **Interactive setup**: Walk through options step-by-step
2. **Manual setup**: Creates a template config file for you to edit

You'll need a Gamma API key from [gamma.app/settings/api](https://gamma.app/settings/api).

## Configuration

Config file: `.claude/rt-gamma.toml`

```toml
# Required: Your Gamma API key
api_key = "your-api-key-here"

# Optional: Default Gamma theme ID
theme = ""

# Optional: Default Gamma template ID
template = ""

# Text processing mode: generate | condense | preserve
text_mode = "preserve"

# Image source: ai | unsplash | giphy | pexels | pictographic | none
image_source = "ai"

# Card/slide splitting: auto | inputTextBreaks (respects --- markers)
card_split = "inputTextBreaks"

# Batch mode file pattern
batch_pattern = "*_presentation.md"
```

### Configuration Options

| Option | Values | Description |
|--------|--------|-------------|
| `api_key` | string | **Required.** Your Gamma API key |
| `theme` | string | Gamma theme ID (leave empty for default) |
| `template` | string | Gamma template ID for template-based generation |
| `text_mode` | `preserve`, `generate`, `condense` | How Gamma processes your text |
| `image_source` | `ai`, `unsplash`, `giphy`, `pexels`, `pictographic`, `none` | Where images come from |
| `card_split` | `auto`, `inputTextBreaks` | How slides are split (`inputTextBreaks` respects `---` markers) |
| `batch_pattern` | glob pattern | File pattern for batch mode (default: `*_presentation.md`) |

## Output

For each markdown file processed:
- Creates an `.html` redirect file next to the source (e.g., `talk.md` → `talk.html`)
- The HTML file auto-redirects to your Gamma presentation URL

## Markdown Tips

### Slide Breaks

Use `---` to manually control slide breaks:

```markdown
# Slide 1

Content here

---

# Slide 2

More content
```

### Titles

rt-gamma extracts titles from (in order of priority):
1. YAML frontmatter `title:` field
2. First `# Heading` in the document
3. Filename (as fallback)

### Example Markdown

```markdown
---
title: My Amazing Presentation
---

# Introduction

Welcome to my presentation!

---

# Key Points

- Point one
- Point two
- Point three

---

# Conclusion

Thanks for watching!
```

## Troubleshooting

### "API key is missing"

Add your Gamma API key to `.claude/rt-gamma.toml`:

```toml
api_key = "your-key-here"
```

### "No files matching pattern"

For batch mode, files must match the `batch_pattern` (default: `*_presentation.md`).

Rename your files or change the pattern in config.

### "Generation timed out"

Gamma presentations can take up to 2 minutes to generate. If you're consistently timing out:
- Try shorter content
- Reduce the number of slides
- Check your Gamma account status

## License

MIT
```

**Step 2: Verify file created**

Run: `cat rt-gamma/README.md | head -30`
Expected: See the README header and installation section

**Step 3: Commit**

```bash
git add rt-gamma/README.md
git commit -m "docs(rt-gamma): add README with usage instructions"
```

---

### Task 10: Final Verification

**Step 1: Verify complete folder structure**

Run: `find rt-gamma -type f | sort`

Expected output:
```
rt-gamma/.claude-plugin/plugin.json
rt-gamma/README.md
rt-gamma/commands/rt-gamma.md
rt-gamma/scripts/batch.py
rt-gamma/scripts/config.py
rt-gamma/scripts/gamma_client.py
rt-gamma/scripts/generate.py
rt-gamma/scripts/markdown_utils.py
```

**Step 2: Verify marketplace includes rt-gamma**

Run: `cat .claude-plugin/marketplace.json | grep rt-gamma`

Expected: `"name": "rt-gamma",`

**Step 3: Create final commit if any uncommitted changes**

```bash
git status
# If any changes:
git add -A
git commit -m "chore(rt-gamma): finalize plugin structure"
```

**Step 4: Test the plugin can be discovered**

The plugin is ready for testing. User can:
1. Ensure the marketplace is added
2. Run `/rt-gamma test.md` to test single file
3. Run `/rt-gamma ./folder/` to test batch mode

---

## Summary

Created rt-gamma plugin with:
- **4 Python scripts**: config.py, gamma_client.py, markdown_utils.py, generate.py, batch.py
- **1 slash command**: /rt-gamma for both single and batch generation
- **Plugin metadata**: plugin.json with name, version, description
- **Marketplace registration**: Added to marketplace.json
- **Documentation**: README.md with full usage guide
