#!/usr/bin/env python3
"""Generate a single Gamma presentation from a markdown file."""
import json
import sys
import time
from pathlib import Path

from config import load_config, config_exists, get_config_path
from gamma_client import GammaAPIClient
from markdown_utils import extract_title, read_markdown_file, prepare_content


def generate_presentation(file_path: str) -> dict:
    """
    Generate a presentation from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        dict with success, url, html_path, and optionally error
    """
    path = Path(file_path).resolve()

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

    # Read markdown
    try:
        content = read_markdown_file(str(path))
    except (FileNotFoundError, ValueError) as e:
        return {"success": False, "error": str(e)}

    # Extract title
    title = extract_title(content)
    if not title:
        title = path.stem.replace("_", " ").title()

    # Prepare content
    final_content = prepare_content(content, title)

    # Create client
    client = GammaAPIClient(config["api_key"])

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

    try:
        # Check if using template
        template_id = config.get("template", "").strip()
        theme_id = config.get("theme", "").strip() or None

        if template_id:
            # Template-based generation
            result = client.create_from_template(
                gamma_id=template_id,
                prompt=final_content,
                theme_id=theme_id,
            )
        else:
            # Standard generation
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
                "success": False,
                "error": "No generation ID returned from API"
            }

        # Poll for completion (max 2 minutes)
        max_attempts = 60
        for _ in range(max_attempts):
            time.sleep(2)
            status = client.get_generation_status(generation_id)

            if status.get("status") == "completed":
                gamma_url = status.get("gammaUrl", status.get("url"))

                # Create HTML redirect file
                html_path = path.with_suffix(".html")
                html_content = f'''<!DOCTYPE html>
<html>
<head><meta http-equiv="refresh" content="0;url={gamma_url}"></head>
</html>'''
                html_path.write_text(html_content, encoding="utf-8")

                return {
                    "success": True,
                    "url": gamma_url,
                    "html_path": str(html_path),
                    "title": title,
                }

            elif status.get("status") == "failed":
                return {
                    "success": False,
                    "error": status.get("error", "Generation failed")
                }

        return {
            "success": False,
            "error": "Timeout: Generation took longer than 2 minutes"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "Usage: generate.py <markdown_file>"}))
        sys.exit(1)

    file_path = sys.argv[1]
    result = generate_presentation(file_path)

    print(json.dumps(result))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
