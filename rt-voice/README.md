# rt-voice

A Claude Code plugin that plays themed sounds for hook events.

## Installation

```bash
/plugin marketplace add ryanturnercom/rt-plugins
/plugin install rt-voice@rt-plugins
```

## Configuration

Create `.claude/rt-voice.toml` in your project:

```toml
# Enable or disable all sounds
enabled = true

# Theme name (folder name in themes/)
theme = "default"

# Master volume (0.0 to 1.0)
volume = 0.8
```

## Supported Events

- `SessionStart` - When a session starts/resumes
- `SessionEnd` - When a session ends
- `UserPromptSubmit` - When user sends a message
- `PreToolUse` - Before a tool runs
- `PostToolUse` - After a tool completes
- `PermissionRequest` - When permission dialog shows
- `Notification` - When Claude sends a notification
- `Stop` - When main agent finishes responding
- `SubagentStop` - When a subagent finishes
- `PreCompact` - Before context compaction

## Creating Themes

Themes are folders in `themes/` containing sound files named after events.

```
themes/my-theme/
├── SessionStart.mp3      # Single file
├── PreToolUse/           # Folder = random selection
│   ├── sound1.mp3
│   └── sound2.mp3
└── PostToolUse.ogg
```

Supported formats: `.mp3`, `.wav`, `.ogg`

Missing sounds are silently skipped.

## Requirements

- Python 3.8+
- No third-party dependencies on Windows or macOS
- Linux: one of `mpg123`, `ffplay`, or `aplay` for audio playback
