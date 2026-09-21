import json
import re


RESULTS_PATH = "data/output/search_results.json"
VERIFIED_PATH = "data/output/verified_sources.json"
COST_PATH = "data/output/cost_evidence.json"


COST_PATTERNS = [
    r"(?:US\$|USD|\$)\s?\d+(?:\.\d+)?\s?(?:million|m|billion|bn)"
    r"(?:\s?[-–]\s?\d+(?:\.\d+)?\s?(?:million|m|billion|bn))?",
    r"(?:EUR|€)\s?\d+(?:\.\d+)?\s?(?:million|m|billion|bn)"
    r"(?:\s?[-–]\s?\d+(?:\.\d+)?\s?(?:million|m|billion|bn))?"
]


def load_search_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["results"]


def load_verified_sources():
    with open(VERIFIED_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_costs(text):
    costs = []

    for pattern in COST_PATTERNS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        for match in matches:
            match = match.strip()

            if match and match not in costs:
                costs.append(match)

    return costs


def find_verified_source(url, verified_sources):
    for source in verified_sources:
        if source.get("url") == url:
            return source

    return None


def extract_context(text, cost):
    index = text.lower().find(cost.lower())

    if index == -1:
        return text[:500]

    start = max(0, index - 250)
    end = min(len(text), index + len(cost) + 250)

    return text[start:end]


if __name__ == "__main__":
    search_results = load_search_results()
    verified_sources = load_verified_sources()

    cost_evidence = []

    for result in search_results:
        title = result.get("title")
        url = result.get("url")
        snippet = result.get("snippet") or ""

        verified_source = find_verified_source(url, verified_sources)

        if not verified_source:
            continue

        verification = verified_source.get("verification", {})

        if not verification.get("verified"):
            continue

        page_text = verification.get("text_preview") or ""

        # Search both the search-engine snippet and verified page text.
        combined_text = snippet + "\n" + page_text

        costs = extract_costs(combined_text)

        if not costs:
            continue

        evidence_items = []

        for cost in costs:
            context = extract_context(combined_text, cost)

            evidence_items.append({
                "cost": cost,
                "context": context
            })

        cost_evidence.append({
            "title": title,
            "url": url,
            "costs_found": evidence_items
        })

        print(f"\n{title}")

        for item in evidence_items:
            print("Cost:", item["cost"])
            print("Context:", item["context"][:500])

    with open(COST_PATH, "w", encoding="utf-8") as file:
        json.dump(
            cost_evidence,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"\nSaved cost evidence to: {COST_PATH}")