from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6",
    input="Write a cheerful two-sentence opening for a children's story about a friendly dinosaur."
)

print(response.output_text)
