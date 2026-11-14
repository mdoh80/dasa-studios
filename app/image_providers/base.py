"""Provider contract used by reusable image-generation workflows."""

from pathlib import Path
from typing import Protocol


class ImageProvider(Protocol):
    """Generate one image using a supplied reference image and prompt."""

    provider_name: str
    model: str

    def generate_reference_view(
        self,
        *,
        reference_image: Path,
        prompt: str,
    ) -> bytes:
        """Return the generated image bytes for one character view."""

