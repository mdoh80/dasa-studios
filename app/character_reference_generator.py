"""Generate reviewable front, side, and back views for any character."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv

from .image_providers.base import ImageProvider
from .image_providers.openai_provider import OpenAIImageProvider


VIEWS = ("front", "side", "back")
METADATA_FILENAME = "character_reference_generation.json"


class CharacterValidationError(ValueError):
    """Raised when a character definition cannot drive image generation."""


@dataclass
class ViewResult:
    """The outcome of one requested character view."""

    view: str
    status: str
    output_filename: str
    prompt: str
    error: str | None = None


def project_root() -> Path:
    """Return the repository root based on this module's location."""

    return Path(__file__).resolve().parents[1]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CharacterValidationError(f"Invalid character JSON: {path}") from exc

    if not isinstance(data, dict):
        raise CharacterValidationError(f"Character definition must be an object: {path}")
    return data


def load_character(character_id: str, root: Path | None = None) -> tuple[dict[str, Any], Path, Path]:
    """Load a character definition and its approved visual reference sheet."""

    repository_root = root or project_root()
    character_dir = repository_root / "characters" / character_id
    definition_path = character_dir / "character.json"

    if not definition_path.is_file():
        raise FileNotFoundError(f"Character definition not found: {definition_path}")

    character = _read_json(definition_path)
    if character.get("character_id") != character_id:
        raise CharacterValidationError(
            f"Character ID in {definition_path} does not match '{character_id}'."
        )

    appearance = character.get("appearance")
    if not isinstance(appearance, dict) or not appearance:
        raise CharacterValidationError(
            f"Character '{character_id}' is missing a visual appearance description."
        )

    consistency_rules = character.get("consistency_rules")
    if not isinstance(consistency_rules, list) or not consistency_rules:
        raise CharacterValidationError(
            f"Character '{character_id}' is missing consistency rules."
        )

    visual_reference = character.get("visual_reference")
    if not isinstance(visual_reference, str) or not visual_reference.strip():
        raise CharacterValidationError(
            f"Character '{character_id}' is missing visual_reference."
        )

    reference_path = character_dir / visual_reference
    if not reference_path.is_file():
        raise FileNotFoundError(f"Approved reference sheet not found: {reference_path}")

    return character, character_dir, reference_path


def _format_character_details(character: dict[str, Any]) -> str:
    """Serialize visual character data into stable prompt text."""

    appearance = character["appearance"]
    appearance_lines = [f"- {key.replace('_', ' ').title()}: {value}" for key, value in appearance.items()]
    rules = [f"- {rule}" for rule in character["consistency_rules"]]
    style = character.get("animation_style", {})
    style_lines = [f"- {key.replace('_', ' ').title()}: {value}" for key, value in style.items()]

    sections = [
        f"Character: {character.get('name', character['character_id'])}",
        f"Species: {character.get('species', 'Not specified')}",
        "Approved appearance description:\n" + "\n".join(appearance_lines),
        "Approved consistency rules:\n" + "\n".join(rules),
    ]
    if style_lines:
        sections.append("Approved animation style:\n" + "\n".join(style_lines))
    return "\n\n".join(sections)


def build_view_prompt(character: dict[str, Any], view: str) -> str:
    """Build a view-specific prompt without character-specific hardcoding."""

    if view not in VIEWS:
        raise ValueError(f"Unsupported character view: {view}")

    angle = {
        "front": "a straight-on front view",
        "side": "a clean, true side profile view",
        "back": "a straight-on back view",
    }[view]

    return f"""Edit the approved character reference image into {angle} of the same character.

Use the uploaded approved reference sheet as the visual source of truth. Preserve the exact approved character design, including all colours, markings, proportions, eyes, face, limbs, spikes, tail, clothing (if any), and distinctive features. Change only the camera angle required for this view; do not redesign, embellish, simplify, or reinterpret the character.

{_format_character_details(character)}

Output requirements:
- Show one single full-body character, fully visible from head to feet and tail.
- Use a neutral, consistent, uncluttered background.
- Use even studio lighting and a clear readable silhouette.
- Do not include text, labels, turntable grids, watermarks, logos, props, scenery, or extra characters.
- Do not crop, pose dramatically, or add accessories.
- This is a production reference image for children aged 4–6 and must remain friendly and reassuring.
""".strip()


def _output_filename(character_id: str, view: str) -> str:
    return f"{character_id}_{view}.png"


def select_views(requested_views: Sequence[str] | None) -> tuple[str, ...]:
    """Validate and normalize requested views, defaulting to all views."""

    if not requested_views or "all" in requested_views:
        if requested_views and len(requested_views) > 1:
            raise ValueError("'all' cannot be combined with individual views.")
        return VIEWS

    invalid_views = sorted(set(requested_views) - set(VIEWS))
    if invalid_views:
        raise ValueError(f"Unsupported character view(s): {', '.join(invalid_views)}")

    return tuple(dict.fromkeys(requested_views))


class CharacterReferenceGenerator:
    """Orchestrate safe, independently reportable character view generation."""

    def __init__(self, *, root: Path | None = None, provider: ImageProvider | None = None) -> None:
        self.root = root or project_root()
        self.provider = provider

    def run(
        self,
        character_id: str,
        *,
        overwrite: bool = False,
        dry_run: bool = False,
        views: Sequence[str] | None = None,
    ) -> list[ViewResult]:
        """Generate all views, continuing after individual provider failures."""

        character, character_dir, reference_path = load_character(character_id, self.root)
        references_dir = character_dir / "references"
        selected_views = select_views(views)
        results: list[ViewResult] = []

        if dry_run:
            for view in selected_views:
                prompt = build_view_prompt(character, view)
                filename = _output_filename(character_id, view)
                results.append(ViewResult(view, "dry_run", filename, prompt))
            return results

        provider = self.provider or OpenAIImageProvider()
        references_dir.mkdir(parents=True, exist_ok=True)

        for view in selected_views:
            filename = _output_filename(character_id, view)
            output_path = references_dir / filename
            prompt = build_view_prompt(character, view)

            if output_path.exists() and not overwrite:
                results.append(ViewResult(view, "skipped_existing", filename, prompt))
                continue

            try:
                image_bytes = provider.generate_reference_view(
                    reference_image=reference_path,
                    prompt=prompt,
                )
                if not image_bytes:
                    raise RuntimeError("Image provider returned empty image data.")
                output_path.write_bytes(image_bytes)
                results.append(ViewResult(view, "generated", filename, prompt))
            except Exception as exc:  # Continue so partial failures are recorded per view.
                results.append(ViewResult(view, "failed", filename, prompt, str(exc)))

        self._write_metadata(character_id, character, reference_path, provider, results)
        return results

    def _write_metadata(
        self,
        character_id: str,
        character: dict[str, Any],
        reference_path: Path,
        provider: ImageProvider,
        results: list[ViewResult],
    ) -> None:
        metadata = {
            "character_id": character_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "provider": provider.provider_name,
            "model": provider.model,
            "approved_reference_sheet": str(reference_path.relative_to(self.root)),
            "approval_status": "pending_review",
            "views": [asdict(result) for result in results],
        }
        output_path = reference_path.parent / METADATA_FILENAME
        output_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def _print_results(results: Sequence[ViewResult]) -> None:
    for result in results:
        print(f"{result.view}: {result.status} ({result.output_filename})")
        if result.error:
            print(f"  error: {result.error}")
        if result.status == "dry_run":
            print(f"  prompt:\n{result.prompt}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", required=True, help="Character ID under characters/")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing generated view images; never replaces the approved sheet.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Display prompts without calling the image provider or writing files.",
    )
    parser.add_argument(
        "--views",
        nargs="+",
        choices=("front", "side", "back", "all"),
        default=["all"],
        metavar="VIEW",
        help="Views to generate: front, side, back, or all (default: all).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    load_dotenv()
    args = build_parser().parse_args(argv)
    try:
        results = CharacterReferenceGenerator().run(
            args.character,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            views=args.views,
        )
    except (CharacterValidationError, FileNotFoundError, RuntimeError, ValueError, OSError) as exc:
        print(f"error: {exc}")
        return 1

    _print_results(results)
    return 0 if all(result.status != "failed" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

