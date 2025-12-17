Increase the rt-voice volume by 0.1 (max 1.0).

1. Read the user's config at `.claude/rt-voice.toml` in the current working directory
2. If it doesn't exist, create it with `volume = 0.9` (default 0.8 + 0.1)
3. If it exists, increase the volume value by 0.1, capping at 1.0
4. Write the updated config back
5. Tell the user the new volume level
