Change the rt-voice sound theme.

1. List all available themes by reading the folders in `rt-voice/themes/` directory (use the CLAUDE_PLUGIN_ROOT or find the rt-voice plugin location)
2. Use AskUserQuestion to present the available themes and ask the user which one they want to use
3. Read the user's config at `.claude/rt-voice.toml` in the current working directory
4. If it doesn't exist, create it with the selected theme
5. If it exists, update the `theme` value to the selected theme name
6. Write the updated config back
7. Confirm to the user which theme is now active
