
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

PROFILE_PATH = "data/output/vessel_profile.json"
OUTPUT_PATH = "data/output/llm_search_queries.json"

load_dotenv()

api_key = os.getenv("DATABRICKS_API_KEY")
endpoint = os.getenv("DATABRICKS_ENDPOINT")

if not api_key:
    raise ValueError("DATABRICKS_API_KEY is missing in .env")

if not endpoint:
    raise ValueError("DATABRICKS_ENDPOINT is missing in .env")

client = OpenAI(
    api_key=api_key,
    base_url=endpoint,
)


def load_vessel_profile():
    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_search_queries(vessel):
    prompt = f"""
You are a maritime vessel research assistant.

Generate 8 to 12 useful web search queries for researching
the vessel's specifications, comparable vessels, and construction cost.

Use the vessel profile below:
{json.dumps(vessel, indent=2, ensure_ascii=False)}

Requirements:
- Prioritize official shipyard websites, company announcements,
  vessel specifications, and published contract values.
- Search for comparable vessels with similar size and purpose.
- Include queries about newbuilding cost or purchase consideration.
- Include queries that help verify vessel dimensions and machinery.
- Use specific vessel details when available.
- Do not invent vessel names, costs, or specifications.
- Return ONLY valid JSON in this format:
  {{
    "queries": [
      "first search query",
      "second search query"
    ]
  }}
"""

    response = client.chat.completions.create(
        model="databricks-meta-llama-3-3-70b-instruct",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=1200,
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "").strip()

    result = json.loads(content)
    queries = result.get("queries")

    if not isinstance(queries, list) or not queries:
        raise ValueError("LLM did not return a valid queries list.")

    queries = [
        query.strip()
        for query in queries
        if isinstance(query, str) and query.strip()
    ]

    if not queries:
        raise ValueError("No usable search queries were generated.")

    return queries


def main():
    vessel = load_vessel_profile()
    queries = generate_search_queries(vessel)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {"queries": queries},
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("\nLLM search queries generated successfully.")
    print(f"Saved to: {OUTPUT_PATH}\n")

    for index, query in enumerate(queries, start=1):
        print(f"{index}. {query}")


if __name__ == "__main__":
    main()
