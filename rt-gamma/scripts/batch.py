#!/usr/bin/env python3
"""Batch generate Gamma presentations from a folder of markdown files."""
import fnmatch
import json
import sys
import time
from pathlib import Path

from config import load_config, config_exists, get_config_path
from gamma_client import GammaAPIClient
from markdown_utils import extract_title, read_markdown_file, prepare_content


def find_presentation_files(directory: Path, pattern: str) -> list[Path]:
    """
    Find all matching markdown files without corresponding .html files.

    Args:
        directory: Directory to search
        pattern: Glob pattern to match (e.g., "*_presentation.md")

    Returns:
        List of markdown paths that need processing
    """
    files_to_process = []

    for md_file in directory.rglob(pattern):
        html_file = md_file.with_suffix(".html")
        if not html_file.exists():
            files_to_process.append(md_file)

    return sorted(files_to_process)


def generate_single(
    client: GammaAPIClient,
    file_path: Path,
    config: dict,
) -> dict:
    """
    Generate a single presentation.

    Returns dict with success, url, error, etc.
    """
    try:
        # Read and prepare content
        content = read_markdown_file(str(file_path))
        title = extract_title(content)

        if not title:
            # Use filename as fallback title
            title = file_path.stem.replace("_presentation", "").replace("_", " ").title()

        final_content = prepare_content(content, title)

        # Map config image_source to API value
        image_source_map = {
            "ai": "aiGenerated",
            "unsplash": "unsplash",
            "giphy": "giphy",
            "pexels": "webFreeToUse",
            "pictographic": "pictographic",
            "none": "noImages",
        }
        image_source = image_source_map.get(config.get("image_source", "ai"), "aiGenerated")

        # Check if using template
        template_id = config.get("template", "").strip()
        theme_id = config.get("theme", "").strip() or None

        if template_id:
            result = client.create_from_template(
                gamma_id=template_id,
                prompt=final_content,
                theme_id=theme_id,
            )
        else:
            result = client.generate_presentation(
                input_text=final_content,
                text_mode=config.get("text_mode", "preserve"),
                format_type="presentation",
                theme_id=theme_id,
                card_split=config.get("card_split", "inputTextBreaks"),
                image_source=image_source,
            )

        generation_id = result.get("generationId")
        if not generation_id:
            return {
                "path": str(file_path),
                "success": False,
                "error": "No generation ID returned"
            }

        # Poll for completion (max 2 minutes)
        max_attempts = 60
        for _ in range(max_attempts):
            time.sleep(2)
            status = client.get_generation_status(generation_id)

            if status.get("status") == "completed":
                gamma_url = status.get("gammaUrl", status.get("url"))

                # Create HTML redirect file
                html_path = file_path.with_suffix(".html")
                html_content = f'''<!DOCTYPE html>
<html>
<head><meta http-equiv="refresh" content="0;url={gamma_url}"></head>
</html>'''
                html_path.write_text(html_content, encoding="utf-8")

                return {
                    "path": str(file_path),
                    "success": True,
                    "url": gamma_url,
                    "html_path": str(html_path),
                }

            elif status.get("status") == "failed":
                return {
                    "path": str(file_path),
                    "success": False,
                    "error": status.get("error", "Generation failed")
                }

        return {
            "path": str(file_path),
            "success": False,
            "error": "Timeout: Generation took longer than 2 minutes"
        }

    except Exception as e:
        return {
            "path": str(file_path),
            "success": False,
            "error": str(e)
        }


def batch_generate(directory: str) -> dict:
    """
    Generate presentations for all matching files in a directory.

    Args:
        directory: Path to the directory to process

    Returns:
        dict with total, success, failed counts and results array
    """
    dir_path = Path(directory).resolve()

    if not dir_path.exists():
        return {
            "success": False,
            "error": f"Directory not found: {directory}"
        }

    if not dir_path.is_dir():
        return {
            "success": False,
            "error": f"Not a directory: {directory}"
        }

    # Load config
    try:
        config = load_config()
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Config not found. Create {get_config_path()}"
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}

    # Find files
    pattern = config.get("batch_pattern", "*_presentation.md")
    files = find_presentation_files(dir_path, pattern)

    if not files:
        return {
            "success": True,
            "total": 0,
            "processed": 0,
            "failed": 0,
            "results": [],
            "message": f"No files matching '{pattern}' need processing (all have .html files)"
        }

    # Create client
    client = GammaAPIClient(config["api_key"])

    # Process files sequentially to avoid rate limits
    results = []
    for file_path in files:
        result = generate_single(client, file_path, config)
        results.append(result)

    # Calculate summary
    successes = [r for r in results if r.get("success")]
    failures = [r for r in results if not r.get("success")]

    return {
        "success": len(failures) == 0,
        "total": len(files),
        "processed": len(successes),
        "failed": len(failures),
        "results": results,
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: batch.py <directory>"}))
        sys.exit(1)

    directory = sys.argv[1]
    result = batch_generate(directory)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
