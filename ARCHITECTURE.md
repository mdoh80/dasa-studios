# Architecture

## Overview

Dasa Studios currently uses a small, sequential content-generation pipeline:

```text
Story idea
    ↓
Story generator
    ↓
Approved story text
    ↓
Storyboard generator
    ↓
Structured storyboard JSON
```

The OpenAI API provides model generation, while the local filesystem stores character definitions, scripts, and storyboard outputs.

## Components

### Story generator

`app/story_generator.py` accepts a story idea and builds a prompt for an age-appropriate children's story. It calls the OpenAI Responses API and returns the generated text. When run as a script, it saves the result to the Danny project directory.

Responsibilities:

- Define the story-writing constraints.
- Select the configured model.
- Submit the story idea to the OpenAI API.
- Persist the generated story.

### Storyboard generator

`app/storyboard_generator.py` reads an existing story and requests a structured storyboard through the OpenAI Responses API's typed parsing interface.

The Pydantic models define the output contract:

- `DialogueLine` represents one character's dialogue.
- `Scene` represents a timed scene and its production details.
- `Storyboard` represents the complete episode.

Responsibilities:

- Read an approved script.
- Request scenes with consistent production fields.
- Validate the model response using Pydantic.
- Serialize the storyboard to JSON.

### Character data

Character definitions live under `characters/`. Danny's JSON file contains his appearance, personality, animation style, and continuity rules. This data is currently reference material; the generators do not yet load it automatically into their prompts.

### Project data

Each content project lives under `projects/`. The current project, `danny_lost_star`, contains:

- `script/story.txt` — the approved story text.
- `storyboard/storyboard.json` — the structured storyboard.

## Data flow

1. A story idea is embedded in the story-generation prompt.
2. The model returns plain text containing a title and story.
3. The story is saved as UTF-8 text.
4. The storyboard generator reads that text.
5. The model returns a parsed `Storyboard` object.
6. The validated object is serialized as formatted JSON.

## Current boundaries and limitations

- The pipeline is file-based and currently targets one fixed project path.
- API clients are created during module import.
- Story and storyboard model configuration is not yet centralized.
- Character data is not automatically injected into generation prompts.
- There is no database, web service, job queue, media renderer, or asset management layer.
- Generated content still requires human review before downstream production use.

## Design direction

Future components should preserve the separation between content generation, content validation, and project storage. Model calls should be isolated behind small service functions so they can be mocked in tests and replaced without changing project orchestration.

