
import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

MODEL = "gpt-5.6"
client = OpenAI()

PROJECT_DIR = Path("projects/danny_lost_star")
STORY_FILE = PROJECT_DIR / "script" / "story.txt"
OUTPUT_FILE = PROJECT_DIR / "storyboard" / "storyboard.json"


class DialogueLine(BaseModel):
    character: str
    text: str


class Scene(BaseModel):
    scene_number: int
    title: str
    duration_seconds: int
    location: str
    characters: list[str]
    visual_action: str
    camera_direction: str
    narration: str
    dialogue: list[DialogueLine]
    music_mood: str
    sound_effects: list[str]
    video_prompt: str
    continuity_notes: str


class Storyboard(BaseModel):
    episode_title: str
    target_age: str
    total_duration_seconds: int
    scenes: list[Scene]


def generate_storyboard(story: str) -> Storyboard:
    """Convert an approved children's story into a structured storyboard."""

    prompt = f"""
    You are an experienced animation director and storyboard writer.

    Convert the following approved children's story into a detailed
    animation storyboard.

    TARGET AUDIENCE: Children aged 4–6.

    REQUIREMENTS:

    - Preserve the original story and its happy ending.
    - Do not introduce unrelated characters or subplots.
    - Aim for approximately 2 minutes of finished animation.
    - Create approximately 6–10 individual scenes.
    - Aim for scene durations of 10–20 seconds.
    - Give every scene a clear beginning, action and conclusion.
    - Describe character movements and facial expressions.
    - Include camera directions suitable for animation.
    - Separate narration from character dialogue.
    - Include suitable music moods and sound effects.
    - Keep the visual style colourful, warm and appealing.
    - Keep the atmosphere gentle, friendly and reassuring.
    - Maintain consistent character appearances between scenes.
    - Write a useful video generation prompt for every scene.

    The video prompts should describe actual movement and action,
    not simply describe a static image.

    STORY:

    {story}
    """

    response = client.responses.parse(
        model=MODEL,
        input=prompt,
        text_format=Storyboard
    )

    storyboard = response.output_parsed

    if storyboard is None:
        raise RuntimeError("OpenAI did not return a valid storyboard.")

    return storyboard


def main():
    if not STORY_FILE.exists():
        raise FileNotFoundError(f"Story not found: {STORY_FILE}")

    story = STORY_FILE.read_text(encoding="utf-8")

    print("Generating storyboard...")

    storyboard = generate_storyboard(story)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        storyboard.model_dump_json(indent=2),
        encoding="utf-8"
    )

    print("\nStoryboard generated successfully!")
    print(f"Episode: {storyboard.episode_title}")
    print(f"Scenes: {len(storyboard.scenes)}")
    print(f"Duration: {storyboard.total_duration_seconds} seconds")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
