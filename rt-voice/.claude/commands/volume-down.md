Decrease the rt-voice volume by 0.1 (min 0.0).

1. Read the user's config at `.claude/rt-voice.toml` in the current working directory
2. If it doesn't exist, create it with `volume = 0.7` (default 0.8 - 0.1)
3. If it exists, decrease the volume value by 0.1, with minimum of 0.0
4. Write the updated config back
5. Tell the user the new volume level
