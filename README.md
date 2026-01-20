# rt-plugins

A Claude Code plugin marketplace featuring audio feedback and presentation tools.

## Author

**Ryan Turner** - [ryanturner.com](https://ryanturner.com)

---

## Installation

### Step 1: Clone the Repository

Choose a permanent location for the plugins (they must stay here after installation).

**macOS/Linux:**
```bash
cd ~/Projects  # or wherever you keep your projects
git clone https://github.com/ryanturnercom/rt-plugins.git
```

**Windows (PowerShell):**
```powershell
cd C:\Projects  # or wherever you keep your projects
git clone https://github.com/ryanturnercom/rt-plugins.git
```

### Step 2: Add the Marketplace to Claude Code

Run this command in your terminal to open Claude Code settings:

```bash
claude settings
```

Add the marketplace path to your settings. Your `settings.json` should include:

**macOS/Linux:**
```json
{
  "pluginMarketplaces": [
    "~/Projects/rt-plugins/.claude-plugin/marketplace.json"
  ]
}
```

**Windows:**
```json
{
  "pluginMarketplaces": [
    "C:\\Projects\\rt-plugins\\.claude-plugin\\marketplace.json"
  ]
}
```

> **Note:** Replace the path with wherever you cloned the repository.

### Step 3: Install a Plugin

After adding the marketplace, install plugins using:

```bash
claude plugin install rt-voice@rt-plugins
```

Or for rt-gamma:

```bash
claude plugin install rt-gamma@rt-plugins
```

### Step 4: Restart Claude Code

Close and reopen Claude Code (or start a new session) for the plugins to take effect.

---

## Plugins Included

### rt-voice

Plays sound effects when Claude Code triggers hook events like SessionStart, ToolUse, Notifications, and more. Supports custom themes with randomized sound selection.

**Features:**
- 10 hook events supported (SessionStart, SessionEnd, PreToolUse, PostToolUse, etc.)
- Custom sound themes
- Volume control via slash commands
- Cross-platform audio playback (pygame)

**Slash Commands:**
| Command | Description |
|---------|-------------|
| `/rt-voice:create-theme <name>` | Create a new theme folder with all event subfolders |
| `/rt-voice:change-theme` | List available themes and switch between them |
| `/rt-voice:volume-up` | Increase volume by 0.1 (max 1.0) |
| `/rt-voice:volume-down` | Decrease volume by 0.1 (min 0.0) |

See [rt-voice/README.md](rt-voice/README.md) for detailed usage.

---

### rt-gamma

Convert Markdown files to beautiful [Gamma.app](https://gamma.app) presentations directly from Claude Code.

**Features:**
- Convert markdown to Gamma presentations with one command
- Batch processing for multiple files
- Speaker notes and slide formatting
- Configurable themes and image sources

**Slash Commands:**
| Command | Description |
|---------|-------------|
| `/rt-gamma:create-gamma <path>` | Convert markdown file or folder to Gamma presentations |
| `/rt-gamma:create-presentation <file>` | Transform any markdown into presentation-ready format |
| `/rt-gamma:create-config` | Create config file template |

See [rt-gamma/README.md](rt-gamma/README.md) for detailed usage.

---

## Troubleshooting

### "Plugin not found" after installation

Make sure:
1. The path in `pluginMarketplaces` points to the exact location of `marketplace.json`
2. You've restarted Claude Code after modifying settings
3. The cloned repository hasn't been moved

### Sounds not playing (rt-voice)

The plugin auto-installs `pygame` on first run. If issues persist:

```bash
pip install pygame
```

### Verifying installation

Check your installed plugins:

```bash
claude plugin list
```

---

## License

This software is **free to use as-is**.

**Disclaimer:** The author is not liable for anything whatsoever. Use at your own risk. No warranty is provided, express or implied. The author assumes no responsibility for any damages, issues, or consequences arising from the use of this software.
