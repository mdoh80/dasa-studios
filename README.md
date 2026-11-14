# Dasa Studios

Dasa Studios is a Python-based storytelling pipeline for creating short, age-appropriate animated content. The current prototype generates a children's story with the OpenAI API and converts an approved story into a structured animation storyboard.

## Current capabilities

- Generate a children's story for ages 4–6.
- Save a generated story to a project script directory.
- Convert a story into a typed storyboard containing scenes, narration, dialogue, camera direction, sound, and video-generation prompts.
- Store character definitions and project assets as JSON and text files.

## Project structure

```text
app/
  character_reference_generator.py  Character reference workflow
  image_providers/                   Image provider implementations
  story_generator.py       Story generation entry point
  storyboard_generator.py  Storyboard generation entry point
characters/
  danny/                   Danny character definition
projects/
  danny_lost_star/
    script/                Generated or approved scripts
    storyboard/            Structured storyboard output
test_openai.py              Manual API smoke test
```

## Requirements

- Python 3.10 or newer
- An OpenAI API key
- The `openai`, `python-dotenv`, and `pydantic` Python packages
- Python 3.12 is the project development version

## Setup

Create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv pydantic
```

Create a `.env` file in the repository root:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_supported_model_name
OPENAI_IMAGE_MODEL=gpt-image-2.5-sunburst
```

Do not commit `.env` or expose the API key in source control.

## Usage

Run the story generator from the repository root:

```bash
python app/story_generator.py
```

The prototype writes the generated story to `projects/danny_lost_star/script/story.txt`.

After reviewing or approving the story, generate its storyboard:

```bash
python app/storyboard_generator.py
```

The storyboard is written to `projects/danny_lost_star/storyboard/storyboard.json`.

### Generate character reference views

The reusable character reference workflow uses the approved reference sheet and character definition to generate front, side, and back views for any character:

```bash
python -m app.character_reference_generator --character danny
```

Generated images are saved under `characters/<character_id>/references/` as `<character_id>_front.png`, `<character_id>_side.png`, and `<character_id>_back.png`. Each run also writes `character_reference_generation.json` with prompts, provider/model information, per-view status, and an initial `pending_review` approval status.

The default is `--views all`. Generate only one view by passing `front`, `side`, or `back`:

```bash
python -m app.character_reference_generator --character danny --views front
```

Multiple individual views can also be selected:

```bash
python -m app.character_reference_generator --character danny --views front side
```

`all` cannot be combined with individual view names.

Existing generated images are skipped by default. To replace them explicitly:

```bash
python -m app.character_reference_generator --character danny --overwrite
```

Preview the prompts without calling the API or writing output files:

```bash
python -m app.character_reference_generator --character danny --dry-run
```

The workflow never overwrites the approved character sheet or character definition. It uses `OPENAI_IMAGE_MODEL` for the image edit provider; the default is the current precision-oriented GPT Image model. Image generation requires a valid API key and may incur API charges.

Both commands currently use the configured OpenAI model and require network access and a valid API key.

## Validation

Compile the Python modules locally with:

```bash
python -m compileall app
python -m pytest
```

The automated character-reference tests mock the image provider and do not incur API costs. The API smoke test is intended for manual use only:

```bash
python test_openai.py
```

