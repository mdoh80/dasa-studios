"""OpenAI Image API provider for character reference view generation."""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


DEFAULT_IMAGE_MODEL = "gpt-image-2.5-sunburst"


class OpenAIImageProvider:
    """Generate reference views with the OpenAI image edits endpoint."""

    provider_name = "openai"

    def __init__(self, *, model: str | None = None, client: Any | None = None) -> None:
        load_dotenv()
        self.model = model or os.getenv("OPENAI_IMAGE_MODEL", DEFAULT_IMAGE_MODEL)
        self.client = client or OpenAI()

    def generate_reference_view(
        self,
        *,
        reference_image: Path,
        prompt: str,
    ) -> bytes:
        """Edit the approved reference sheet into one requested camera view."""

        with reference_image.open("rb") as image_file:
            response = self.client.images.edit(
                model=self.model,
                image=image_file,
                prompt=prompt,
                background="opaque",
                output_format="png",
                size="1024x1024",
                n=1,
            )

        if not response.data:
            raise RuntimeError("OpenAI returned no generated image data.")

        encoded_image = response.data[0].b64_json
        if not encoded_image:
            raise RuntimeError("OpenAI returned no base64 image data.")

        try:
            return base64.b64decode(encoded_image, validate=True)
        except (ValueError, TypeError) as exc:
            raise RuntimeError("OpenAI returned invalid base64 image data.") from exc

