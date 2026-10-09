
import json
import os
import sys

from ddgs import DDGS
from dotenv import load_dotenv
from openai import OpenAI


PROFILE_PATH = "data/output/vessel_profile.json"
RESULTS_PATH = "data/output/search_results.json"
LLM_QUERIES_PATH = "data/output/llm_search_queries.json"


def configure_console_encoding():
    """Make Windows console output UTF-8 safe."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def load_vessel_profile():
    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def search_web(query, max_results=10):
    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=max_results)

            for result in search_results:
                title = result.get("title")
                url = result.get("href")
                snippet = result.get("body")

                if not title or not url:
                    continue

                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                })

    except Exception as error:
        print(
            f"\nSearch failed for query:\n{query}\n"
            f"Error: {error}"
        )

    return results


def build_search_queries(vessel):
    """Existing rule-based queries used as a fallback."""

    vessel_name = vessel.get("vessel_name") or ""
    vessel_type = vessel.get("vessel_type") or ""
    loa = vessel.get("length_overall_m")
    breadth = vessel.get("breadth_m")
    dwt = vessel.get("deadweight_t")
    speed = vessel.get("service_speed_knots")

    queries = [
        f'"{vessel_name}" vessel',
        f'"{vessel_type}" vessel',
        f'"buoy maintenance vessel" "{loa} m" vessel',
        f'"buoy maintenance vessel" "{dwt} t" vessel',

        f'"buoy maintenance vessel" "{loa} m" "{breadth} m"',
        f'"buoy maintenance vessel" "{loa} m" "{dwt} t"',
        f'"91m" vessel "1450" DWT',
        f'"91 metre" maintenance vessel',

        '"buoy maintenance vessel" newbuilding contract',
        '"buoy maintenance vessel" newbuild price',
        '"buoy maintenance vessel" contract value',
        '"buoy maintenance vessel" purchase price',

        '"91M Maintenance/Work Vessel"',
        '"91M Maintenance/Work Vessel" "purchase consideration"',
        '"91M Maintenance/Work Vessel" "contract value"',
        '"91M Maintenance/Work Vessel" "purchase price"',
        '"91M Maintenance/Work Vessel" "RM117,696,000"',
        '"91M Maintenance/Work Vessel" "RM117"',
        '"91M Maintenance/Work Vessel" "Shin Yang"',
        '"91M Maintenance/Work Vessel" "DESB Marine Services"',

        '"Shin Yang Shipyard" "91M" vessel',
        '"Shin Yang" "91m" maintenance vessel',
        '"DESB Marine Services" "91M" vessel',
        '"Dayang Enterprise" "91m" maintenance vessel',

        'site:shinyanggroup.com.my "91M" "Maintenance" "Work Vessel"',
        'site:shinyanggroup.com.my "91M Maintenance/Work Vessel"',
        'site:shinyanggroup.com.my "RM117,696,000"',
        'site:shinyanggroup.com.my "DESB Marine Services"',

        '"91m" maintenance vessel newbuild price',
        '"91m" maintenance vessel contract price',
        '"91m" maintenance vessel purchase consideration',
        '"91m" maintenance vessel USD million',
        '"91m" maintenance vessel cost',
    ]

    # Keep this variable available for future query improvements.
    _ = speed

    return list(dict.fromkeys(queries))


def generate_queries_with_llm(vessel):
    """Generate queries through the Databricks-hosted LLM."""

    load_dotenv()

    api_key = os.getenv("DATABRICKS_API_KEY")
    endpoint = os.getenv("DATABRICKS_ENDPOINT")

    if not api_key or not endpoint:
        raise ValueError(
            "DATABRICKS_API_KEY or DATABRICKS_ENDPOINT is missing in .env"
        )

    client = OpenAI(
        api_key=api_key,
        base_url=endpoint,
    )

    prompt = f"""
You are a maritime vessel research assistant.

Generate 8 to 12 useful web search queries for researching this vessel's
specifications, comparable vessels, and construction cost.

Vessel profile:
{json.dumps(vessel, indent=2, ensure_ascii=False)}

Requirements:
- Prioritize official shipyard websites and company announcements.
- Search for comparable vessels with similar size and purpose.
- Include newbuilding cost and purchase consideration searches.
- Include queries to verify dimensions and machinery.
- Do not invent vessel names, costs, or specifications.
- Avoid duplicate queries.
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
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
    )

    content = (response.choices[0].message.content or "").strip()

    if content.startswith("```"):
        content = content.replace("```json", "", 1)
        content = content.replace("```", "").strip()

    result = json.loads(content)
    queries = result.get("queries")

    if not isinstance(queries, list):
        raise ValueError("LLM did not return a valid queries list.")

    queries = list(dict.fromkeys(
        query.strip()
        for query in queries
        if isinstance(query, str) and query.strip()
    ))

    if not queries:
        raise ValueError("LLM returned no usable search queries.")

    return queries


def save_llm_queries(queries):
    """Save the generated queries for inspection."""

    os.makedirs(os.path.dirname(LLM_QUERIES_PATH), exist_ok=True)

    with open(LLM_QUERIES_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {"queries": queries},
            file,
            indent=2,
            ensure_ascii=False,
        )


def get_search_queries(vessel):
    """Prefer LLM queries; fall back to existing rule-based queries."""

    try:
        queries = generate_queries_with_llm(vessel)
        save_llm_queries(queries)

        print("Using Databricks LLM-generated search queries.")
        print(f"Generated query count: {len(queries)}")

        return queries

    except Exception as error:
        print(f"\nLLM query generation failed: {error}")
        print("Falling back to existing rule-based queries.")

        return build_search_queries(vessel)


def deduplicate_results(results):
    unique_results = []
    seen_urls = set()

    for result in results:
        url = result.get("url")

        if not url or url in seen_urls:
            continue

        seen_urls.add(url)
        unique_results.append(result)

    return unique_results


def rank_results(results):
    """Rank potentially useful results; this does not verify sources."""

    high_priority_keywords = [
        "shinyanggroup.com.my",
        "shinyang",
        "desb",
        "dayang",
        "maintenance vessel",
        "work vessel",
        "newbuild",
        "newbuilding",
        "contract",
        "purchase",
    ]

    cost_keywords = [
        "rm117,696,000",
        "purchase consideration",
        "contract value",
        "contract price",
        "purchase price",
    ]

    def score(result):
        text = (
            f"{result.get('title', '')} "
            f"{result.get('url', '')} "
            f"{result.get('snippet', '')}"
        ).lower()

        score_value = sum(
            1 for keyword in high_priority_keywords if keyword in text
        )

        if "shinyanggroup.com.my" in text:
            score_value += 10

        score_value += sum(
            5 for keyword in cost_keywords if keyword in text
        )

        return score_value

    return sorted(results, key=score, reverse=True)


def main():
    configure_console_encoding()

    vessel = load_vessel_profile()
    queries = get_search_queries(vessel)

    all_results = []

    print("\n" + "=" * 60)
    print("WEB RESEARCH")
    print("=" * 60)

    for index, query in enumerate(queries, start=1):
        print("\n" + "-" * 60)
        print(f"SEARCH {index}")
        print("-" * 60)
        print(f"Query:\n{query}")

        results = search_web(query, max_results=10)
        print(f"Results returned: {len(results)}")

        for result in results:
            print(f"\nTitle: {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Snippet: {result['snippet']}")

        all_results.extend(results)

    all_results = deduplicate_results(all_results)
    all_results = rank_results(all_results)

    output = {
        "vessel_profile": vessel,
        "queries": queries,
        "results": all_results,
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print(f"Total unique search results: {len(all_results)}")
    print(f"Saved to: {RESULTS_PATH}")
    print("=" * 60)

    print("\nTOP SEARCH RESULTS:")

    for index, result in enumerate(all_results[:15], start=1):
        print(f"\n{index}. {result['title']}")
        print(f"   {result['url']}")


if __name__ == "__main__":
    main()
