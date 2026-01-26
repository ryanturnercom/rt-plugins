#!/usr/bin/env python3
"""
rt-voice: Play sounds for Claude Code hook events.
Usage: python play_sound.py <event_name>

No third-party dependencies required. Uses native OS audio playback:
  - Windows: winmm.dll (mciSendString) via ctypes
  - macOS: afplay
  - Linux: mpg123 or ffplay
"""

import sys
import os

# Suppress stderr to prevent hook error messages
sys.stderr = open(os.devnull, "w")

import random
import subprocess
from pathlib import Path

# Python 3.11+ has tomllib built-in
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

SUPPORTED_FORMATS = (".mp3", ".wav", ".ogg")


def get_config():
    """Load config from .claude/rt-voice.toml or return defaults."""
    config_path = Path.cwd() / ".claude" / "rt-voice.toml"
    defaults = {"enabled": True, "theme": "default", "volume": 0.8}

    if config_path.exists() and tomllib:
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

    return None


def play_sound(path, volume=0.8):
    """Play sound using native OS audio. No third-party dependencies needed."""
    path_str = str(path)

    if sys.platform in ("win32", "msys"):
        import ctypes
        winmm = ctypes.windll.winmm
        # Get 8.3 short path to avoid issues with special chars in filenames
        buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.kernel32.GetShortPathNameW(path_str, buf, 260)
        safe_path = buf.value or path_str
        vol = int(volume * 1000)
        winmm.mciSendStringW(f'open "{safe_path}" type mpegvideo alias rtv', None, 0, None)
        winmm.mciSendStringW(f"setaudio rtv volume to {vol}", None, 0, None)
        winmm.mciSendStringW("play rtv wait", None, 0, None)
        winmm.mciSendStringW("close rtv", None, 0, None)

    elif sys.platform == "darwin":
        subprocess.run(
            ["afplay", "-v", str(volume), path_str],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )

    else:
        # Linux: try common CLI players
        for cmd in (
            ["mpg123", "-q", path_str],
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
             "-volume", str(int(volume * 100)), path_str],
            ["aplay", path_str],
        ):
            try:
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                return
            except Exception:
                continue


def main():
    if len(sys.argv) < 2:
        return

    event = sys.argv[1]
    plugin_root = Path(__file__).parent.parent
    config = get_config()

    if not config["enabled"]:
        return

    sound_path = find_sound(plugin_root, config["theme"], event)
    if sound_path:
        play_sound(sound_path, config["volume"])


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
