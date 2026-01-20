"""Gamma API client for generating presentations."""
import sys
from typing import Optional

# Auto-install requests if missing
try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


class GammaAPIClient:
    """Client for the Gamma public API."""

    def __init__(self, api_key: str, base_url: str = "https://public-api.gamma.app/v1.0"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        })

    def list_themes(self) -> list[dict]:
        """Fetch all available themes in the workspace."""
        url = f"{self.base_url}/themes"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("data", data) if isinstance(data, dict) else data

    def generate_presentation(
        self,
        input_text: str,
        text_mode: str = "preserve",
        format_type: str = "presentation",
        theme_id: Optional[str] = None,
        num_cards: int = 10,
        card_split: str = "inputTextBreaks",
        image_source: str = "aiGenerated",
    ) -> dict:
        """
        Generate a new presentation using the Gamma API.

        Args:
            input_text: Content to generate the presentation from (max 100k tokens)
            text_mode: How to handle text - 'generate', 'condense', or 'preserve'
            format_type: Output format - 'presentation', 'document', 'social', 'webpage'
            theme_id: Theme identifier (get from list_themes)
            num_cards: Number of cards/slides (1-60 for Pro, 1-75 for Ultra)
            card_split: 'auto' or 'inputTextBreaks' (respects --- markers)
            image_source: Image source type

        Returns:
            API response with generation details including generationId
        """
        payload = {
            "inputText": input_text,
            "textMode": text_mode,
            "format": format_type,
            "numCards": num_cards,
            "cardSplit": card_split,
            "imageOptions": {"source": image_source},
        }

        if theme_id:
            payload["themeId"] = theme_id

        url = f"{self.base_url}/generations"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def create_from_template(
        self,
        gamma_id: str,
        prompt: str,
        theme_id: Optional[str] = None,
    ) -> dict:
        """
        Create a presentation from an existing template.

        Args:
            gamma_id: The template ID to use
            prompt: Content and instructions for filling the template
            theme_id: Override the template's theme

        Returns:
            API response with generation details
        """
        payload = {
            "gammaId": gamma_id,
            "prompt": prompt,
            "imageOptions": {"model": "flux-1-quick", "style": "match my theme"},
        }

        if theme_id:
            payload["themeId"] = theme_id

        url = f"{self.base_url}/generations/from-template"
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_generation_status(self, generation_id: str) -> dict:
        """Check the status of a generation and get URLs if ready."""
        url = f"{self.base_url}/generations/{generation_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
