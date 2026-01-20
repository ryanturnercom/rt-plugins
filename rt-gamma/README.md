# rt-gamma

Convert Markdown files to beautiful [Gamma.app](https://gamma.app) presentations directly from Claude Code.

## Installation

```bash
# Add the marketplace (if not already added)
/plugin marketplace add ryanturnercom/rt-plugins

# Install rt-gamma
/plugin install rt-gamma@rt-plugins
```

## Commands

| Command | Description |
|---------|-------------|
| `/rt-gamma:create-gamma <path>` | Convert markdown file or folder to Gamma presentations |
| `/rt-gamma:create-presentation <file>` | Transform any markdown into presentation-ready format |
| `/rt-gamma:create-config` | Create config file template (won't overwrite existing) |

## Usage

### Generate Presentation from Markdown

```bash
/rt-gamma:create-gamma my_presentation.md
```

Converts a single markdown file to a Gamma presentation.

### Batch Mode

```bash
/rt-gamma:create-gamma ./presentations/
```

Converts all `*_presentation.md` files in the folder (and subfolders) that don't already have `.html` files.

### Create Presentation-Ready Markdown

```bash
/rt-gamma:create-presentation my_document.md
```

Transforms any markdown document into presentation format with:
- One idea per slide
- Speaker notes with delivery cues
- `---` slide breaks (Gamma-compatible)
- Outputs `*_presentation.md` file

**Typical workflow:**
1. `/rt-gamma:create-presentation notes.md` → creates `notes_presentation.md`
2. `/rt-gamma:create-gamma notes_presentation.md` → uploads to Gamma

## First-Time Setup

On first run, rt-gamma will prompt you to configure:

1. **Interactive setup**: Walk through options step-by-step
2. **Manual setup**: Creates a template config file for you to edit

You'll need a Gamma API key from [gamma.app/settings/api](https://gamma.app/settings/api).

## Configuration

Config file: `.claude/rt-gamma:create-gamma.toml`

```toml
# Required: Your Gamma API key
api_key = "your-api-key-here"

# Optional: Default Gamma theme ID
theme = ""

# Optional: Default Gamma template ID
template = ""

# Text processing mode: generate | condense | preserve
text_mode = "preserve"

# Image source: ai | unsplash | giphy | pexels | pictographic | none
image_source = "ai"

# Card/slide splitting: auto | inputTextBreaks (respects --- markers)
card_split = "inputTextBreaks"

# Batch mode file pattern
batch_pattern = "*_presentation.md"
```

### Configuration Options

| Option | Values | Description |
|--------|--------|-------------|
| `api_key` | string | **Required.** Your Gamma API key |
| `theme` | string | Gamma theme ID (leave empty for default) |
| `template` | string | Gamma template ID for template-based generation |
| `text_mode` | `preserve`, `generate`, `condense` | How Gamma processes your text |
| `image_source` | `ai`, `unsplash`, `giphy`, `pexels`, `pictographic`, `none` | Where images come from |
| `card_split` | `auto`, `inputTextBreaks` | How slides are split (`inputTextBreaks` respects `---` markers) |
| `batch_pattern` | glob pattern | File pattern for batch mode (default: `*_presentation.md`) |

## Output

For each markdown file processed:
- Creates an `.html` redirect file next to the source (e.g., `talk.md` → `talk.html`)
- The HTML file auto-redirects to your Gamma presentation URL

## Markdown Tips

### Slide Breaks

Use `---` to manually control slide breaks:

```markdown
# Slide 1

Content here

---

# Slide 2

More content
```

### Titles

rt-gamma extracts titles from (in order of priority):
1. YAML frontmatter `title:` field
2. First `# Heading` in the document
3. Filename (as fallback)

### Example Markdown

```markdown
---
title: My Amazing Presentation
---

# Introduction

Welcome to my presentation!

---

# Key Points

- Point one
- Point two
- Point three

---

# Conclusion

Thanks for watching!
```

## Troubleshooting

### "API key is missing"

Add your Gamma API key to `.claude/rt-gamma:create-gamma.toml`:

```toml
api_key = "your-key-here"
```

### "No files matching pattern"

For batch mode, files must match the `batch_pattern` (default: `*_presentation.md`).

Rename your files or change the pattern in config.

### "Generation timed out"

Gamma presentations can take up to 2 minutes to generate. If you're consistently timing out:
- Try shorter content
- Reduce the number of slides
- Check your Gamma account status

## License

MIT
