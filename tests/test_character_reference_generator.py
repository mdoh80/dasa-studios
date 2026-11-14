"""Tests for the reusable character reference generation workflow."""

import json
from pathlib import Path

import pytest

from app.character_reference_generator import (
    METADATA_FILENAME,
    VIEWS,
    CharacterReferenceGenerator,
    CharacterValidationError,
    build_view_prompt,
    load_character,
    select_views,
)


class FakeProvider:
    """Deterministic provider used to ensure tests never call an API."""

    provider_name = "fake"
    model = "fake-model"

    def __init__(self, failures: set[str] | None = None) -> None:
        self.failures = failures or set()
        self.calls: list[tuple[Path, str]] = []

    def generate_reference_view(self, *, reference_image: Path, prompt: str) -> bytes:
        self.calls.append((reference_image, prompt))
        for view in VIEWS:
            if f"{view} view" in prompt or f"{view} profile" in prompt:
                if view in self.failures:
                    raise RuntimeError(f"simulated {view} failure")
                return f"generated-{view}".encode()
        raise AssertionError("view was not represented in prompt")


@pytest.fixture
def character_root(tmp_path: Path) -> Path:
    character_dir = tmp_path / "characters" / "test-character"
    references_dir = character_dir / "references"
    references_dir.mkdir(parents=True)
    (references_dir / "approved.png").write_bytes(b"approved-reference")
    (character_dir / "character.json").write_text(
        json.dumps(
            {
                "character_id": "test-character",
                "name": "Test Character",
                "species": "Friendly creature",
                "appearance": {
                    "body_colour": "Blue",
                    "eyes": "Large brown eyes",
                    "tail": "Short rounded tail",
                },
                "animation_style": {"visual_style": "Soft 3D animation"},
                "consistency_rules": ["Always preserve the blue body colour"],
                "visual_reference": "references/approved.png",
            }
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_valid_character_loading(character_root: Path) -> None:
    character, character_dir, reference = load_character("test-character", character_root)

    assert character["name"] == "Test Character"
    assert character_dir == character_root / "characters" / "test-character"
    assert reference.name == "approved.png"


def test_missing_character_definition(character_root: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Character definition not found"):
        load_character("missing", character_root)


def test_missing_reference_sheet(character_root: Path) -> None:
    definition = character_root / "characters" / "test-character" / "character.json"
    data = json.loads(definition.read_text(encoding="utf-8"))
    data["visual_reference"] = "references/missing.png"
    definition.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="Approved reference sheet not found"):
        load_character("test-character", character_root)


def test_missing_visual_description(character_root: Path) -> None:
    definition = character_root / "characters" / "test-character" / "character.json"
    data = json.loads(definition.read_text(encoding="utf-8"))
    data["appearance"] = {}
    definition.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(CharacterValidationError, match="visual appearance"):
        load_character("test-character", character_root)


def test_prompt_creation_covers_all_views(character_root: Path) -> None:
    character, _, _ = load_character("test-character", character_root)

    prompts = {view: build_view_prompt(character, view) for view in VIEWS}

    assert set(prompts) == {"front", "side", "back"}
    assert "Blue" in prompts["front"]
    assert "Always preserve the blue body colour" in prompts["side"]
    assert "single full-body character" in prompts["back"]
    assert "Do not include text" in prompts["front"]
    assert prompts["front"] != prompts["side"]


def test_view_selection_defaults_to_all_and_supports_individual_views() -> None:
    assert select_views(None) == ("front", "side", "back")
    assert select_views(["all"]) == ("front", "side", "back")
    assert select_views(["front"]) == ("front",)
    assert select_views(["back", "front", "back"]) == ("back", "front")


def test_view_selection_rejects_all_with_individual_view() -> None:
    with pytest.raises(ValueError, match="cannot be combined"):
        select_views(["all", "front"])


def test_individual_view_generation_only_calls_selected_view(character_root: Path) -> None:
    provider = FakeProvider()

    results = CharacterReferenceGenerator(root=character_root, provider=provider).run(
        "test-character", views=["side"]
    )

    assert [result.view for result in results] == ["side"]
    assert [result.status for result in results] == ["generated"]
    assert len(provider.calls) == 1
    references_dir = character_root / "characters" / "test-character" / "references"
    assert (references_dir / "test-character_side.png").exists()
    assert not (references_dir / "test-character_front.png").exists()
    assert not (references_dir / "test-character_back.png").exists()


def test_dry_run_displays_prompts_without_writing_or_calling_provider(
    character_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    results = CharacterReferenceGenerator(root=character_root).run(
        "test-character", dry_run=True
    )

    assert [result.status for result in results] == ["dry_run"] * 3
    references_dir = character_root / "characters" / "test-character" / "references"
    assert not (references_dir / METADATA_FILENAME).exists()
    assert not (references_dir / "test-character_front.png").exists()
    assert all(result.prompt for result in results)

    from app.character_reference_generator import _print_results

    _print_results(results)
    assert "front" in capsys.readouterr().out


def test_existing_file_protection(character_root: Path) -> None:
    references_dir = character_root / "characters" / "test-character" / "references"
    front = references_dir / "test-character_front.png"
    front.write_bytes(b"keep-this")
    provider = FakeProvider()

    results = CharacterReferenceGenerator(root=character_root, provider=provider).run(
        "test-character"
    )

    assert results[0].status == "skipped_existing"
    assert front.read_bytes() == b"keep-this"
    assert len(provider.calls) == 2


def test_overwrite_replaces_existing_generated_file(character_root: Path) -> None:
    references_dir = character_root / "characters" / "test-character" / "references"
    front = references_dir / "test-character_front.png"
    front.write_bytes(b"old")
    provider = FakeProvider()

    results = CharacterReferenceGenerator(root=character_root, provider=provider).run(
        "test-character", overwrite=True
    )

    assert [result.status for result in results] == ["generated"] * 3
    assert front.read_bytes() == b"generated-front"
    assert len(provider.calls) == 3


def test_provider_error_is_recorded_and_other_views_continue(character_root: Path) -> None:
    provider = FakeProvider(failures={"side"})

    results = CharacterReferenceGenerator(root=character_root, provider=provider).run(
        "test-character"
    )

    assert [result.status for result in results] == ["generated", "failed", "generated"]
    assert "simulated side failure" in (results[1].error or "")
    references_dir = character_root / "characters" / "test-character" / "references"
    assert (references_dir / "test-character_front.png").exists()
    assert not (references_dir / "test-character_side.png").exists()
    assert (references_dir / "test-character_back.png").exists()


def test_metadata_creation(character_root: Path) -> None:
    provider = FakeProvider()

    CharacterReferenceGenerator(root=character_root, provider=provider).run("test-character")

    metadata_path = (
        character_root
        / "characters"
        / "test-character"
        / "references"
        / METADATA_FILENAME
    )
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["character_id"] == "test-character"
    assert metadata["provider"] == "fake"
    assert metadata["model"] == "fake-model"
    assert metadata["approval_status"] == "pending_review"
    assert len(metadata["views"]) == 3
    assert all(view["prompt"] for view in metadata["views"])
    assert all(view["status"] == "generated" for view in metadata["views"])

