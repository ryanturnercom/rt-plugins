# Task: TOML Parser and Source File Loader

**Status:** [✓] Completed

**Dependencies:** Epic 01 task-01 (placeholder script must exist)

## Context

- Language: Python
- Framework: None (standalone script)
- Testing: Manual
- Database: None

The entry point of `generate_docs.py`. Parses the TOML config, validates that all referenced source files exist, and loads their content. Must auto-install dependencies following the rt-voice pattern.

## Needed from User

None

## Instructions

1. Open `rt-agents/scripts/generate_docs.py`

2. Implement the auto-install pattern (copy from rt-voice's `play_sound.py`):
   ```python
   import subprocess
   import sys

   def ensure_dependencies():
       """Auto-install required packages on first run."""
       required = ["markdown", "pyyaml"]
       for pkg in required:
           try:
               __import__(pkg)
           except ImportError:
               subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

   ensure_dependencies()
   ```

3. Implement TOML parsing:
   ```python
   import sys
   try:
       import tomllib
   except ImportError:
       import tomli as tomllib
   ```
   - Parse `.claude/rt-documentation.toml` from the current working directory
   - Extract `[project]` section (name, description, output_dir, export_dir)
   - Extract `[[section]]` entries into a list, sorted by `order`

4. Implement source file validation:
   - For each section, check that all files in `sources` exist
   - If a source file is missing: print a warning to stderr, skip that source (don't fail)
   - If ALL sources for a section are missing: skip the entire section with a warning

5. Implement source file loading:
   - For each valid section, read all source files into memory
   - For `mode = "summarize"` sections: read from `.rt-documentation/.cache/<slug>.md` instead of the original source
   - If cache file is missing for a summarize section: fall back to reading the original source with a warning
   - Return a list of section dicts: `{title, sources_content, type, mode, print_flag, order}`

6. Add a `main()` function that:
   - Calls the parser
   - Calls the validator/loader
   - Prints: "Loaded [N] sections from config"
   - Returns the loaded sections (for use by assembler in later tasks)

7. Add `if __name__ == "__main__": main()` guard

## Acceptance Criteria

- [x] Auto-installs `markdown` and `pyyaml` if not present
- [x] Parses TOML config using `tomllib` (3.11+) or `tomli` fallback
- [x] Validates all source files exist, warns on missing
- [x] Loads source content for verbatim sections from original files
- [x] Loads source content for summarize sections from `.cache/` directory
- [x] Falls back gracefully if cache is missing
- [x] Sections are sorted by `order` field
- [x] Script runs without errors when invoked directly

## Implementation Notes

- `ensure_dependencies()` auto-installs `markdown` and `pyyaml` at module load time, matching the rt-voice pattern. Also auto-installs `tomli` if `tomllib` is not available (Python < 3.11).
- `parse_config(config_path)` reads `.claude/rt-documentation.toml` relative to `Path.cwd()` by default. Returns `{"project": {...}, "sections": [...]}` with sections sorted by `(order, title)`.
- `load_sections(config)` validates each source file exists, prints warnings to stderr for missing files, and skips sections where all sources are missing. Returns list of dicts with keys: `title`, `sources_content`, `type`, `mode`, `print_flag`, `order`.
- For `mode="summarize"` sections, reads from `.rt-documentation/.cache/<slug>.md` first; falls back to original source with a warning if cache is missing.
- `_slugify(title)` converts titles to filename-safe slugs (lowercase, alphanumeric + hyphens).
- `main()` orchestrates parsing and loading, prints summary, and returns loaded sections for downstream pipeline use.
