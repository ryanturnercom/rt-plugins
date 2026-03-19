# Task: Build generate_pdf.py Core Script

**Status:** [✓] Completed

**Dependencies:** Epic 03 task-05 (HTML output must be generated)

## Context

- Language: Python
- Framework: weasyprint
- Testing: Manual (generate a PDF and verify it opens correctly)
- Database: None

The standalone PDF export script. Reads the generated `index.html`, renders it to PDF via weasyprint, and saves with a timestamp. Must auto-install weasyprint on first run.

## Needed from User

None

## Instructions

1. Open `rt-agents/scripts/generate_pdf.py`

2. Implement auto-install for weasyprint:
   ```python
   import subprocess
   import sys

   def ensure_dependencies():
       """Auto-install weasyprint on first run."""
       try:
           import weasyprint
       except ImportError:
           print("Installing weasyprint...")
           subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])

   ensure_dependencies()
   ```

   **Note:** weasyprint requires system dependencies (GTK, Pango, etc. on some platforms). Add a try/catch around the import after install that gives a helpful error message if system deps are missing:
   ```python
   try:
       import weasyprint
   except OSError as e:
       print(f"weasyprint installed but system dependencies missing: {e}")
       print("See: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html")
       sys.exit(1)
   ```

3. Implement the core PDF generation:
   ```python
   from pathlib import Path
   import weasyprint

   def generate_pdf(html_path: str, output_path: str) -> None:
       """Render HTML file to PDF."""
       html = weasyprint.HTML(filename=html_path)
       html.write_pdf(output_path)
       print(f"PDF generated: {output_path}")
   ```

4. Read the config to find paths:
   ```python
   try:
       import tomllib
   except ImportError:
       import tomli as tomllib

   def load_config():
       config_path = Path.cwd() / ".claude" / "rt-documentation.toml"
       if not config_path.exists():
           print("Error: .claude/rt-documentation.toml not found. Run /documentation-config first.")
           sys.exit(1)
       with open(config_path, "rb") as f:
           return tomllib.load(f)
   ```

5. Add `main()` function:
   ```python
   def main():
       config = load_config()
       output_dir = config.get("project", {}).get("output_dir", ".rt-documentation")
       html_path = Path.cwd() / output_dir / "index.html"

       if not html_path.exists():
           print(f"Error: {html_path} not found. Run /documentation-create first.")
           sys.exit(1)

       export_dir = Path.cwd() / config.get("project", {}).get("export_dir", f"{output_dir}/exports")
       export_dir.mkdir(parents=True, exist_ok=True)

       timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
       pdf_path = export_dir / f"{timestamp}.pdf"

       generate_pdf(str(html_path), str(pdf_path))

   if __name__ == "__main__":
       main()
   ```

6. Add argument parsing for future section filtering (placeholder):
   ```python
   import argparse

   def parse_args():
       parser = argparse.ArgumentParser(description="Generate PDF from rt-documentation HTML")
       parser.add_argument("--sections", type=str, help="Comma-separated section titles to include")
       return parser.parse_args()
   ```

## Acceptance Criteria

- [x] Auto-installs weasyprint if not present
- [x] Gives helpful error if weasyprint system dependencies are missing
- [x] Reads config to find HTML and export paths
- [x] Errors clearly if config or HTML doesn't exist
- [x] Generates a valid PDF from the HTML documentation
- [x] Supports `--sections` argument (parsed but filtering implemented in task-02)
- [x] Running `python generate_pdf.py` produces a PDF in the exports directory

## Implementation Notes

- Script follows the same patterns as `generate_docs.py` (auto-install at module level, tomllib/tomli fallback, Path.cwd()-relative paths)
- `ensure_dependencies()` is called at module level so weasyprint is installed before first use
- After install, a second `import weasyprint` is wrapped in `except OSError` to catch missing system-level dependencies (GTK, Pango, etc.) with a helpful link to the weasyprint docs
- `load_config()` reads `.claude/rt-documentation.toml` from cwd and exits with a clear error if missing
- `generate_pdf()` uses `weasyprint.HTML(filename=...).write_pdf()` as specified
- `main()` reads `output_dir` and `export_dir` from config with sensible defaults, creates export dir if needed, and generates a timestamped PDF (`YYYY-MM-DD_HH-MM-SS.pdf`)
- `--sections` flag is parsed via argparse but only prints a note; actual filtering deferred to task-02
