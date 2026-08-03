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

# Minimum seconds between two plays of the same event (0 = play every fire)
cooldown = 1.5
```

## Performance

Sounds play asynchronously. The hook process decides which file to play, hands
it to a detached process, and exits — Claude Code never waits for audio to
finish. On a typical machine the hook returns in ~150ms regardless of how long
the clip runs.

Because nothing serialises playback any more, each event is debounced by
`cooldown` seconds. `PreToolUse` fires once per tool call and Claude Code issues
tool calls in parallel, so this collapses a burst into a single sound instead of
several overlapping copies.

## Supported Events

- `SessionStart` - When a session starts/resumes
- `SessionEnd` - When a session ends
- `UserPromptSubmit` - When user sends a message
- `PreToolUse` - Before a tool runs
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
└── Stop.ogg
```

Supported formats: `.mp3`, `.wav`, `.ogg`

Missing sounds are silently skipped.

## Requirements

- Python 3.8+
- No third-party dependencies on Windows or macOS
- Linux: one of `mpg123`, `ffplay`, or `aplay` for audio playback
