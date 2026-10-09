import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("DATABRICKS_API_KEY")
endpoint = os.getenv("DATABRICKS_ENDPOINT")

if not api_key:
    raise ValueError("DATABRICKS_API_KEY is missing in .env")

if not endpoint:
    raise ValueError("DATABRICKS_ENDPOINT is missing in .env")

client = OpenAI(
    api_key=api_key,
    base_url=endpoint
)

response = client.chat.completions.create(
    model="databricks-meta-llama-3-3-70b-instruct",
    messages=[
        {
            "role": "user",
            "content": "Explain what a vessel specification is in two simple sentences."
        }
    ],
    max_tokens=100
)

print("\nLLM Response:")
print(response.choices[0].message.content)