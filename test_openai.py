"""Manual OpenAI API smoke test; run explicitly with ``python test_openai.py``."""

from dotenv import load_dotenv
from openai import OpenAI


def main() -> None:
    load_dotenv()
    client = OpenAI()
    response = client.responses.create(
        model="gpt-5.6",
        input="Write a cheerful two-sentence opening for a children's story about a friendly dinosaur.",
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
