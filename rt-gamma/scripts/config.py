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
