#!/usr/bin/env python3
"""
rt-voice: Play sounds for Claude Code hook events.

Usage:
    play_sound.py <EventName>           # hook entry point, returns immediately
    play_sound.py --play <path> <vol>   # internal: blocking playback in a child

Playback is asynchronous. The hook process only decides *which* sound to play,
hands it to a detached process, and exits — Claude Code never waits on audio.

No third-party dependencies. Native OS audio:
  - Windows: winmm.dll (mciSendString) via ctypes, in a detached child process
  - macOS:   afplay
  - Linux:   mpg123 / ffplay / aplay

Imports are kept lazy on purpose: this runs once per hook event, so a few
milliseconds of module import is a real share of the total cost.
"""

import sys
import os

# Suppress stderr to prevent hook error messages
sys.stderr = open(os.devnull, "w")

SUPPORTED_FORMATS = (".mp3", ".wav", ".ogg")
DEFAULTS = {"enabled": True, "theme": "default", "volume": 0.8, "cooldown": 1.5}
IS_WINDOWS = sys.platform in ("win32", "msys")

# CreateProcess flags: no console, and survives the parent exiting
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200


def get_config():
    """Load config from .claude/rt-voice.toml or return defaults."""
    config_path = os.path.join(os.getcwd(), ".claude", "rt-voice.toml")
    if not os.path.isfile(config_path):
        return DEFAULTS

    # Only pay for the TOML parser when there is actually a config to read
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            return DEFAULTS

    with open(config_path, "rb") as f:
        return {**DEFAULTS, **tomllib.load(f)}


def find_sound(plugin_root, theme, event):
    """Find sound file or folder for an event. Returns path or None."""
    theme_dir = os.path.join(plugin_root, "themes", theme)

    # Check for folder first (random selection)
    event_folder = os.path.join(theme_dir, event)
    if os.path.isdir(event_folder):
        sounds = [
            os.path.join(event_folder, name)
            for name in os.listdir(event_folder)
            if name.lower().endswith(SUPPORTED_FORMATS)
        ]
        if not sounds:
            return None
        if len(sounds) == 1:
            return sounds[0]
        import random
        return random.choice(sounds)

    # Check for single file
    for ext in SUPPORTED_FORMATS:
        sound_file = os.path.join(theme_dir, event + ext)
        if os.path.isfile(sound_file):
            return sound_file

    return None


def claim_slot(event, cooldown):
    """Debounce an event. Returns False if it already fired within `cooldown`.

    Async playback means nothing serialises the sounds any more. Claude Code
    fires PreToolUse once per tool call and issues tool calls in parallel, so
    without this a burst would stack overlapping copies of the same clip.
    """
    if cooldown <= 0:
        return True

    import time

    tmp = os.environ.get("TEMP") or os.environ.get("TMPDIR") or "/tmp"
    safe_event = "".join(c for c in event if c.isalnum()) or "event"
    stamp = os.path.join(tmp, "rt-voice-%s.stamp" % safe_event)

    try:
        if time.time() - os.path.getmtime(stamp) < cooldown:
            return False
    except OSError:
        pass  # no stamp yet, or unreadable - treat as free

    try:
        with open(stamp, "w"):
            pass
    except OSError:
        pass  # a read-only temp dir shouldn't cost you the sound

    return True


def _spawn(cmd, **kwargs):
    """Popen without waiting. Returns False if the executable is missing."""
    import subprocess

    try:
        subprocess.Popen(cmd, **kwargs)
        return True
    except OSError:
        return False


def _python_exe():
    """Prefer pythonw.exe so the detached child never flashes a console."""
    exe = sys.executable
    windowless = os.path.join(os.path.dirname(exe), "pythonw.exe")
    return windowless if os.path.isfile(windowless) else exe


def play_async(path, volume):
    """Start playback in a detached process and return immediately."""
    import subprocess

    kwargs = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }

    if IS_WINDOWS:
        # MCI playback is owned by the process that opened it, so it can't
        # outlive this one. Hand the job to a detached copy of this script
        # instead of a player binary.
        kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        _spawn(
            [_python_exe(), os.path.abspath(__file__), "--play", path, str(volume)],
            **kwargs
        )
        return

    # Elsewhere the player is already a separate binary - just don't wait on it
    kwargs["start_new_session"] = True

    if sys.platform == "darwin":
        candidates = [["afplay", "-v", str(volume), path]]
    else:
        candidates = [
            ["mpg123", "-q", path],
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
             "-volume", str(int(volume * 100)), path],
            ["aplay", path],
        ]

    for cmd in candidates:
        if _spawn(cmd, **kwargs):
            return


def play_blocking_windows(path, volume):
    """Blocking MCI playback. Only ever runs in the detached child process."""
    import ctypes

    winmm = ctypes.windll.winmm
    # Get 8.3 short path to avoid issues with special chars in filenames
    buf = ctypes.create_unicode_buffer(260)
    ctypes.windll.kernel32.GetShortPathNameW(path, buf, 260)
    safe_path = buf.value or path

    # Unique alias per child, so concurrent events don't fight over one device
    alias = "rtv%d" % os.getpid()
    vol = int(volume * 1000)

    winmm.mciSendStringW(
        'open "%s" type mpegvideo alias %s' % (safe_path, alias), None, 0, None
    )
    winmm.mciSendStringW("setaudio %s volume to %d" % (alias, vol), None, 0, None)
    winmm.mciSendStringW("play %s wait" % alias, None, 0, None)
    winmm.mciSendStringW("close %s" % alias, None, 0, None)


def main():
    args = sys.argv[1:]
    if not args:
        return

    # Detached child: play the file we were handed, then exit
    if args[0] == "--play":
        if IS_WINDOWS and len(args) >= 3:
            play_blocking_windows(args[1], float(args[2]))
        return

    event = args[0]
    config = get_config()

    if not config["enabled"]:
        return

    plugin_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sound_path = find_sound(plugin_root, config["theme"], event)
    if not sound_path:
        return

    if not claim_slot(event, float(config.get("cooldown", 1.5))):
        return

    play_async(sound_path, float(config["volume"]))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
