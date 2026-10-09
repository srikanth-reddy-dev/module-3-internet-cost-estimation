import json
import os

from dotenv import load_dotenv
from openai import OpenAI

TEXT_PATH = "data/samples/energy_passion.txt"
OUTPUT_PATH = "data/output/llm_vessel_profile.json"

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


def load_text():
    with open(TEXT_PATH, "r", encoding="utf-8") as file:
        return file.read()


def extract_profile_with_llm(text):
    prompt = f"""
You are extracting structured information from a vessel specification document.

Read the document below and return ONLY valid JSON.

Use exactly these fields:

{{
  "vessel_name": null,
  "design": null,
  "vessel_type": null,
  "yard": null,
  "delivery_year": null,
  "length_overall_m": null,
  "breadth_m": null,
  "design_draft_m": null,
  "deadweight_t": null,
  "gross_tonnage": null,
  "net_tonnage": null,
  "deck_area_m2": null,
  "service_speed_knots": null,
  "main_engine": null,
  "propulsion": null,
  "tunnel_thrusters": null,
  "classification": null,
  "source_document": "energy_passion_clean.pdf"
}}

Rules:
- Use only information explicitly present in the document.
- Do not guess or invent values.
- If a field cannot be found, use null.
- Keep technical names and descriptions as they appear in the document.
- Return numbers as numbers, not strings.
- Return ONLY the JSON object. No markdown and no explanation.

DOCUMENT:
{text}
"""

    response = client.chat.completions.create(
        model="databricks-meta-llama-3-3-70b-instruct",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=1500,
    )

    content = response.choices[0].message.content.strip()

    # Remove markdown code fences if the model adds them.
    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "")
        content = content.strip()

    return json.loads(content)


if __name__ == "__main__":
    text = load_text()

    profile = extract_profile_with_llm(text)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=2, ensure_ascii=False)

    print("\nLLM vessel profile extracted successfully.")
    print(f"Saved to: {OUTPUT_PATH}\n")

    print("LLM Extracted Profile:")

    for key, value in profile.items():
        print(f"{key}: {value}")