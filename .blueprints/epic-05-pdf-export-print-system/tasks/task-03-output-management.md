# Task: Output Management and Timestamping

**Status:** [x] Completed

**Dependencies:** Epic 05 task-01 (core PDF script must exist)

## Context

- Language: Python
- Framework: None
- Testing: Manual
- Database: None

Polish the PDF export workflow: proper timestamped filenames, export directory management, and a summary report after generation.

## Needed from User

None

## Instructions

1. Open `rt-agents/scripts/generate_pdf.py`

2. Ensure the export directory structure is clean:
   ```python
   def setup_export_dir(export_dir: Path) -> Path:
       """Create export directory if it doesn't exist."""
       export_dir.mkdir(parents=True, exist_ok=True)
       return export_dir
   ```

3. Timestamp format for PDF filenames: `YYYY-MM-DD_HH-MM-SS.pdf`
   ```python
   from datetime import datetime

   def generate_filename() -> str:
       return datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".pdf"
   ```

4. Add a `--list` flag to show existing exports:
   ```python
   parser.add_argument("--list", action="store_true", help="List existing PDF exports")
   ```

   Implementation:
   ```python
   def list_exports(export_dir: Path):
       pdfs = sorted(export_dir.glob("*.pdf"), reverse=True)
       if not pdfs:
           print("No exports found.")
           return
       print(f"Exports in {export_dir}/:")
       for pdf in pdfs:
           size_mb = pdf.stat().st_size / (1024 * 1024)
           print(f"  {pdf.name}  ({size_mb:.1f} MB)")
   ```

5. Update `main()` to handle `--list`:
   ```python
   def main():
       args = parse_args()
       config = load_config()
       export_dir = Path.cwd() / config.get("project", {}).get("export_dir", ".rt-documentation/exports")

       if args.list:
           list_exports(export_dir)
           return

       # ... existing generation logic ...
   ```

6. Add a completion report after PDF generation:
   ```python
   pdf_size = pdf_path.stat().st_size / (1024 * 1024)
   print(f"\nPDF Export Complete:")
   print(f"  File: {pdf_path}")
   print(f"  Size: {pdf_size:.1f} MB")
   if args.sections:
       print(f"  Sections: {args.sections}")
   else:
       print(f"  Sections: All printable (per config)")
   ```

## Acceptance Criteria

- [x] Export directory is created automatically if missing
- [x] PDF filename uses `YYYY-MM-DD_HH-MM-SS.pdf` format
- [x] `--list` flag shows all existing exports with sizes
- [x] Completion report shows file path, size, and included sections
- [x] Multiple exports don't overwrite each other (unique timestamps)
- [x] Script handles the case where export dir already has many PDFs without issues

## Implementation Notes

- Added `setup_export_dir()` function that wraps `mkdir(parents=True, exist_ok=True)` for clean directory creation
- Added `list_exports()` function that globs `*.pdf`, sorts reverse (newest first), and prints filename + size in MB
- Added `--list` flag to `parse_args()` alongside existing `--sections` flag
- `main()` handles `--list` early: loads config to resolve export_dir, calls `list_exports()`, and returns before any HTML/PDF work
- Completion report prints after successful PDF generation: file path, size in MB, and which sections were included
- All changes are additive; existing core PDF generation and section filtering logic preserved intact
- Timestamped filenames (already present from task-01) ensure no overwrites
