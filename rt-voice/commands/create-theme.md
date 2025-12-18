---
description: Creates a new theme folder with all event subfolders
---

Create a new rt-voice sound theme with the name provided in $ARGUMENTS.

If no theme name is provided, ask the user for one.

Create the following folder structure inside `rt-voice/themes/<theme-name>/`:

- SessionStart
- SessionEnd
- UserPromptSubmit
- PreToolUse
- PostToolUse
- PermissionRequest
- Notification
- Stop
- SubagentStop
- PreCompact

After creating the folders, tell the user:

1. The full path to the created theme folder
2. Instructions to place audio files (.mp3, .wav, or .ogg) in each event folder
3. Remind them they can put multiple audio files in a folder for random selection
4. Tell them to update their `.claude/rt-voice.toml` config to use the new theme by setting `theme = "<theme-name>"`
