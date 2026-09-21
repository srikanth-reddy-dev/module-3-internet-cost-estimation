import json
from ddgs import DDGS


PROFILE_PATH = "data/output/vessel_profile.json"
RESULTS_PATH = "data/output/search_results.json"


def load_vessel_profile():
    with open(PROFILE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def search_web(query, max_results=10):
    results = []

    with DDGS() as ddgs:
        search_results = ddgs.text(
            query,
            max_results=max_results
        )

        for result in search_results:
            results.append({
                "title": result.get("title"),
                "url": result.get("href"),
                "snippet": result.get("body")
            })

    return results


if __name__ == "__main__":
    vessel = load_vessel_profile()

    query = (
    f'"{vessel["design"]}" '
    f'"{vessel["vessel_type"]}" '
    f'("contract value" OR "contract price" OR "newbuild price" OR "vessel price") '
    f'USD million'
)

    print(f"\nSearch query:\n{query}\n")

    results = search_web(query)

    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {
                "query": query,
                "results": results
            },
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved {len(results)} search results to: {RESULTS_PATH}")

    for result in results:
        print("\nTitle:", result["title"])
        print("URL:", result["url"])