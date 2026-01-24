#!/usr/bin/env python3
"""
rt-voice: Play sounds for Claude Code hook events.
Usage: python play_sound.py <event_name>
"""

import sys
import os
import random
from pathlib import Path


def get_base_python():
    """Get the base/system Python executable, outside any venv."""
    if sys.prefix == sys.base_prefix:
        # Not in a venv
        return None

    # We're in a venv - find the base Python
    if sys.platform == "win32":
        base_python = Path(sys.base_exec_prefix) / "python.exe"
    else:
        base_python = Path(sys.base_exec_prefix) / "bin" / "python3"
        if not base_python.exists():
            base_python = Path(sys.base_exec_prefix) / "bin" / "python"

    return base_python if base_python.exists() else None


def reexec_with_base_python():
    """Re-execute this script using the base/system Python if in a venv."""
    base_python = get_base_python()
    if base_python:
        os.execv(str(base_python), [str(base_python)] + sys.argv)


# If running inside a venv, re-exec with system Python to avoid polluting
# the project's venv and ensure pygame is installed system-wide
reexec_with_base_python()

# Auto-install pygame if missing (now guaranteed to be system Python)
try:
    import pygame
except ImportError:
    import subprocess
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pygame", "-q", "--user"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    import pygame

# Python 3.11+ has tomllib built-in, fallback to tomli for older versions
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        import subprocess
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "tomli", "-q", "--user"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        import tomli as tomllib

SUPPORTED_FORMATS = (".mp3", ".wav", ".ogg")


def get_config():
    """Load config from .claude/rt-voice.toml or return defaults."""
    config_path = Path.cwd() / ".claude" / "rt-voice.toml"
    defaults = {"enabled": True, "theme": "default", "volume": 0.8}

    if config_path.exists():
        with open(config_path, "rb") as f:
            user_config = tomllib.load(f)
        return {**defaults, **user_config}
    return defaults


def find_sound(plugin_root, theme, event):
    """Find sound file or folder for an event. Returns path or None."""
    theme_dir = plugin_root / "themes" / theme

    # Check for folder first (random selection)
    event_folder = theme_dir / event
    if event_folder.is_dir():
        sounds = [
            f for f in event_folder.iterdir()
            if f.suffix.lower() in SUPPORTED_FORMATS
        ]
        return random.choice(sounds) if sounds else None

    # Check for single file
    for ext in SUPPORTED_FORMATS:
        sound_file = theme_dir / f"{event}{ext}"
        if sound_file.exists():
            return sound_file

    return None  # Silent fallback


def play_sound(sound_path, volume):
    """Play sound file with pygame."""
    pygame.mixer.init()
    pygame.mixer.music.load(str(sound_path))
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()
    # Wait for playback to finish
    while pygame.mixer.music.get_busy():
        pygame.time.wait(10)
    pygame.mixer.quit()


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    event = sys.argv[1]
    plugin_root = Path(__file__).parent.parent
    config = get_config()

    if not config["enabled"]:
        return

    sound_path = find_sound(plugin_root, config["theme"], event)
    if sound_path:
        play_sound(sound_path, config["volume"])


if __name__ == "__main__":
    main()
