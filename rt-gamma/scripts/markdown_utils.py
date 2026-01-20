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
