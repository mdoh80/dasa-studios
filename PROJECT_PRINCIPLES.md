# Dasa Studios – Project Principles

## Project Vision

Dasa Studios is an AI-assisted children's animation production studio. Its purpose is to create original, high-quality animated stories featuring memorable recurring characters.

The initial target audience is children aged 4–6. The initial objective is to develop a repeatable production workflow capable of producing a short animated pilot, eventually scaling to 10–15-minute episodes.

## Core Principles

### 1. Creative Quality and Originality

- Create original stories, characters, dialogue, music and branding.
- Prioritise storytelling and character development.
- Maintain consistent character designs, personalities and voices.
- Ensure all content is appropriate for the intended age group.
- Aim for high-quality, polished 3D animation.

### 2. Human-in-the-Loop Production

- Human approval is required at significant production stages.
- Stories, storyboards, character designs and generated scenes must be reviewable.
- Do not automatically progress through approval gates.
- Allow individual scenes and assets to be regenerated.
- Require final human approval before publishing.
- Do not implement automatic publishing without explicit future approval.

### 3. Modular Architecture

- Python is the primary application language.
- Use OpenAI for creative intelligence, story generation and image generation where appropriate.
- Use external video and audio generation services through interchangeable provider interfaces.
- Avoid coupling application logic to a single AI provider.
- Use Pydantic models and structured data for production assets.
- Keep configuration separate from application logic.

### 4. Production Asset Management

- Treat each episode as an independent production project.
- Treat individual scenes as independently manageable production units.
- Preserve scripts, storyboards, prompts, reference images, video clips and audio.
- Track generation status, approvals and provider/model information.
- Maintain reusable character reference libraries.
- Keep generated media separate from application source code.

### 5. Infrastructure and Security

- Initially operate on the existing AWS Lightsail server.
- Maintain complete separation from other applications hosted on the server.
- Use dedicated Python virtual environments.
- Store secrets in environment variables; never commit credentials.
- Monitor resource consumption and storage.
- Maintain backups of valuable production assets.
- Avoid unnecessary infrastructure expenditure.

### 6. Development Standards

- Develop incrementally in small, testable changes.
- Use feature and fix branches rather than committing directly to `main`.
- Use pull requests for code review and integration.
- Maintain automated tests.
- Keep documentation up to date.
- Prefer simple, maintainable solutions over unnecessary complexity.
- Preserve existing functionality when extending the application.

## Initial Production Target

Produce an approved 60–90-second animated pilot featuring Danny the Dinosaur.

The longer-term objective is a repeatable production pipeline supporting longer episodes, recurring characters and multiple stories.

