"""
rt-agents PDF exporter.
Renders generated HTML documentation to timestamped PDF files.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def ensure_dependencies():
    """Auto-install weasyprint on first run."""
    try:
        import weasyprint  # noqa: F401
    except ImportError:
        print("Installing weasyprint...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "weasyprint"]
        )


ensure_dependencies()

try:
    import weasyprint
except OSError as e:
    print(f"weasyprint installed but system dependencies missing: {e}")
    print(
        "See: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html"
    )
    sys.exit(1)

# Python 3.11+ has tomllib built-in
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "tomli"]
        )
        import tomli as tomllib


def load_config() -> dict:
    """Read .claude/rt-documentation.toml from the current working directory.

    Returns:
        Parsed TOML config as a dict.
    """
    config_path = Path.cwd() / ".claude" / "rt-documentation.toml"
    if not config_path.exists():
        print(
            "Error: .claude/rt-documentation.toml not found. "
            "Run /rt-agents:documentation-config first."
        )
        sys.exit(1)

    with open(config_path, "rb") as f:
        return tomllib.load(f)


def _slugify(title: str) -> str:
    """Convert a section title to a URL/ID-safe slug.

    Uses the same logic as generate_docs.py so section IDs match.

    Example: "CI/CD Configuration" -> "ci-cd-configuration"
    """
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9\s-]", " ", slug)
    slug = slug.strip()
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug)
    return slug


def filter_sections_via_css(
    html_content: str, selected_sections: list
) -> str:
    """Inject CSS to hide non-selected sections for PDF rendering.

    Reads the TOML config to discover all section titles. For any
    section whose title is NOT in *selected_sections*, a CSS rule
    ``#section-{slug} { display: none !important; }`` is injected
    before ``</head>``.

    Args:
        html_content: Full HTML document as a string.
        selected_sections: List of section titles to include in the PDF.

    Returns:
        Modified HTML with hide rules injected.
    """
    config = load_config()
    sections = config.get("section", [])

    hide_rules = []
    for section in sections:
        title = section.get("title", "")
        if title not in selected_sections:
            slug = _slugify(title)
            hide_rules.append(
                f"#section-{slug} {{ display: none !important; }}"
            )

    if hide_rules:
        css_block = f"<style>{''.join(hide_rules)}</style>"
        html_content = html_content.replace("</head>", f"{css_block}</head>")

    return html_content


def setup_export_dir(export_dir: Path) -> Path:
    """Create export directory if it doesn't exist.

    Args:
        export_dir: Path to the export directory.

    Returns:
        The export directory path.
    """
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir


def list_exports(export_dir: Path):
    """List existing PDF exports with file sizes.

    Args:
        export_dir: Path to the export directory.
    """
    if not export_dir.exists():
        print("No exports found.")
        return
    pdfs = sorted(export_dir.glob("*.pdf"), reverse=True)
    if not pdfs:
        print("No exports found.")
        return
    print(f"Exports in {export_dir}/:")
    for pdf in pdfs:
        size_mb = pdf.stat().st_size / (1024 * 1024)
        print(f"  {pdf.name}  ({size_mb:.1f} MB)")


def generate_pdf(html_path: str, output_path: str) -> None:
    """Render HTML file to PDF via weasyprint.

    Args:
        html_path: Absolute path to the source HTML file.
        output_path: Absolute path for the generated PDF file.
    """
    html = weasyprint.HTML(filename=html_path)
    html.write_pdf(output_path)
    print(f"PDF generated: {output_path}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Generate PDF from rt-documentation HTML"
    )
    parser.add_argument(
        "--sections",
        type=str,
        help="Comma-separated section titles to include in the PDF",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing PDF exports",
    )
    return parser.parse_args()


def main():
    """Run the PDF export pipeline.

    1. Parse CLI arguments
    2. Read config to find HTML and export paths
    3. If --list, show existing exports and return
    4. Verify generated HTML exists
    5. Create export directory if needed
    6. If --sections provided, filter HTML via CSS injection
    7. Generate timestamped PDF and print completion report
    """
    args = parse_args()

    config = load_config()

    output_dir = config.get("project", {}).get(
        "output_dir", ".rt-documentation"
    )

    export_dir = Path.cwd() / config.get("project", {}).get(
        "export_dir", f"{output_dir}/exports"
    )

    if args.list:
        list_exports(export_dir)
        return

    html_path = Path.cwd() / output_dir / "index.html"

    if not html_path.exists():
        print(
            f"Error: {html_path} not found. "
            "Run /rt-agents:documentation-create first."
        )
        sys.exit(1)

    setup_export_dir(export_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_path = export_dir / f"{timestamp}.pdf"

    if args.sections:
        selected = [s.strip() for s in args.sections.split(",")]
        html_content = html_path.read_text(encoding="utf-8")
        html_content = filter_sections_via_css(html_content, selected)
        # Write filtered HTML to a temp file for weasyprint
        temp_path = html_path.parent / "_export_temp.html"
        temp_path.write_text(html_content, encoding="utf-8")
        try:
            generate_pdf(str(temp_path), str(pdf_path))
        finally:
            temp_path.unlink(missing_ok=True)  # Clean up temp file
    else:
        # No filter: use config print flags (already handled by print CSS)
        generate_pdf(str(html_path), str(pdf_path))

    # Completion report
    pdf_size = pdf_path.stat().st_size / (1024 * 1024)
    print(f"\nPDF Export Complete:")
    print(f"  File: {pdf_path}")
    print(f"  Size: {pdf_size:.1f} MB")
    if args.sections:
        print(f"  Sections: {args.sections}")
    else:
        print(f"  Sections: All printable (per config)")


if __name__ == "__main__":
    main()
