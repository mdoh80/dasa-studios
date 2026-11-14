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

Both commands currently use the configured OpenAI model and require network access and a valid API key.

## Validation

Compile the Python modules locally with:

```bash
python -m compileall app
```

The current API smoke test is intended for manual use and makes a real API request. It should not be run automatically as part of a test suite until it is converted to a mocked test.

