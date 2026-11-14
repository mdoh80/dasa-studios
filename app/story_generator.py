
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")

client = OpenAI()


def generate_story(story_idea: str) -> str:
    """Generate an original children's story for ages 4–6."""

    prompt = f"""
    You are a professional children's story writer.

    Write an original, engaging story for children aged 4–6.

    Requirements:
    - Use simple, friendly English.
    - Use short sentences and age-appropriate vocabulary.
    - Create warm, memorable original characters.
    - Include a gentle adventure or problem to solve.
    - Keep the story positive, reassuring and comforting.
    - Avoid frightening situations, violence or upsetting themes.
    - Give the story a satisfying, happy ending.
    - Include opportunities for expressive narration.
    - Aim for approximately 2 minutes of spoken narration.

    Story idea:
    {story_idea}

    Return only the finished story, with a suitable title.
    """

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    return response.output_text


if __name__ == "__main__":
    idea = (
        "Danny the friendly little green dinosaur discovers "
        "a star that has fallen into his garden. "
        "He helps it find its way home."
    )

    print("\nGenerating story...\n")

    story = generate_story(idea)

    print(story)

    os.makedirs("projects/danny_lost_star/script", exist_ok=True)

    with open(
        "projects/danny_lost_star/script/story.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(story)

    print("\nStory saved successfully!")

