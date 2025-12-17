# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin marketplace containing `rt-voice`, a plugin that plays themed audio sounds for Claude Code hook events (SessionStart, ToolUse, etc.).

## Architecture

```
rt-plugins/
├── .claude-plugin/marketplace.json   # Plugin registry
├── rt-voice/                         # Main plugin
│   ├── hooks/hooks.json              # Hook event → command mappings
│   ├── scripts/play_sound.py         # Audio playback script (entry point)
│   ├── themes/default/               # Sound files organized by event
│   └── config.example.toml           # User config template
└── sounds/                           # Raw sound assets
```

## Running the Plugin

```bash
# Play a sound for a specific event
python scripts/play_sound.py <EventName>

# Example events: SessionStart, SessionEnd, UserPromptSubmit, PreToolUse, PostToolUse
```

The script auto-installs dependencies (`pygame`, `tomli`) on first run.

## Configuration

User config lives at `.claude/rt-voice.toml` in the project directory:
```toml
enabled = true
theme = "default"
volume = 0.8
```

## Sound Theme Structure

Themes support single files or folders with random selection:
- Single: `themes/mytheme/SessionStart.mp3`
- Random: `themes/mytheme/PreToolUse/*.mp3` (picks one at random)

Supported formats: .mp3, .wav, .ogg

## Hook Events

The plugin responds to 10 Claude Code hooks defined in `rt-voice/hooks/hooks.json`:
- SessionStart, SessionEnd, UserPromptSubmit
- PreToolUse, PostToolUse, PermissionRequest
- Notification, Stop, SubagentStop, PreCompact

## Slash Commands

| Command | Description |
|---------|-------------|
| `/create-theme <name>` | Creates a new theme folder with all event subfolders |
| `/change-theme` | Lists available themes and lets user select one |
| `/volume-up` | Increases volume by 0.1 (max 1.0) |
| `/volume-down` | Decreases volume by 0.1 (min 0.0) |

Commands modify `.claude/rt-voice.toml` in the user's project directory.

## Key Implementation Details

- `play_sound.py` blocks until audio finishes (required for hook behavior)
- Missing sounds/themes are silently skipped (no errors)
- Python 3.11+ uses built-in `tomllib`; older versions use `tomli` package
- Audio playback uses pygame for cross-platform support
