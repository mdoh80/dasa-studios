# Roadmap

This roadmap describes the planned evolution of the Dasa Studios prototype. Priorities may change as creative and production requirements become clearer.

## Milestone 1: Stabilize the prototype

- Add a dependency manifest and reproducible installation instructions.
- Centralize model and API configuration.
- Make project paths independent of the caller's current working directory.
- Add clear errors for missing API keys, invalid model responses, and missing input files.
- Replace live API execution in the smoke test with mocked automated tests.
- Add repository-level CI for syntax, JSON, and schema validation.

## Milestone 2: Make projects configurable

- Accept project IDs and input paths through a CLI.
- Support multiple characters and story projects.
- Load character JSON into story and storyboard prompts.
- Validate continuity requirements and storyboard timing.
- Add configurable target age, duration, language, and tone.

## Milestone 3: Improve the creative pipeline

- Add an explicit draft, review, approval, and revision workflow.
- Preserve prompt and model metadata for reproducibility.
- Support storyboard revisions without overwriting approved outputs.
- Add content-safety and age-appropriateness review checks.
- Detect continuity conflicts between character definitions and generated scenes.

## Milestone 4: Production assets

- Generate or attach character reference images and scene references.
- Add shot-level asset manifests.
- Integrate narration, music, and sound-effect production workflows.
- Add video-generation provider adapters behind a common interface.
- Track asset versions and approvals.

## Milestone 5: Production operations

- Add a service or web interface for project management.
- Add background jobs for long-running generation tasks.
- Add structured logging, retries, rate-limit handling, and cost tracking.
- Add role-based access and secure secret management.
- Add observability for generation failures and output quality.

## Definition of production readiness

The pipeline should have reproducible inputs and outputs, automated validation, human approval gates, secure secret handling, versioned assets, and tests that do not require live model calls.

