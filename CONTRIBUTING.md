# Contributing

Thank you for contributing to Dasa Studios. Keep changes focused, easy to review, and aligned with the content pipeline described in `ARCHITECTURE.md`.

## Development workflow

1. Create a branch for the change.
2. Read the relevant project documentation before editing code or content.
3. Keep application changes small and preserve existing user-authored work.
4. Add or update tests for non-trivial behavior.
5. Run local validation before opening a pull request.
6. Describe the change, validation performed, and any known limitations.

## Local setup

Follow the setup instructions in `README.md`. Keep API credentials in a local `.env` file and never commit them.

## Coding standards

- Use Python with clear type annotations for public functions.
- Prefer small functions with one responsibility.
- Use UTF-8 for text files.
- Use `pathlib.Path` for filesystem paths.
- Keep model calls behind functions that can be mocked.
- Validate structured model output before writing it to disk.
- Raise clear, actionable errors for invalid input and failed generation.
- Avoid hardcoded secrets, machine-specific paths, and unnecessary global state.
- Keep prompts explicit about audience, tone, safety, and output format.

## Content standards

- Keep content suitable for the configured target age.
- Preserve approved story intent when generating storyboards.
- Maintain character appearance and personality continuity.
- Separate narration, dialogue, visual action, and production notes.
- Treat generated content as a draft until it passes human review.
- Do not add copyrighted or confidential material without permission.

## Testing and validation

Before submitting changes, run the checks relevant to the change:

```bash
python -m compileall app
```

Also validate changed JSON files and run the automated test suite when one is available. Do not run live API calls in automated tests. Live API checks should be explicit, documented, and performed only with an approved development key.

## Commit and pull request guidance

Use concise commit messages that describe the change, such as `Add storyboard schema validation`.

Pull requests should include:

- A short summary of the behavior or documentation change.
- The project or components affected.
- Tests and validation commands run.
- Any API, content, cost, or migration considerations.
- Screenshots or sample output when visual or content output changes.

