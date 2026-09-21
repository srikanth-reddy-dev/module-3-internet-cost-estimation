import json
import re


COST_PATH = "data/output/cost_evidence.json"
NORMALIZED_PATH = "data/output/normalized_costs.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def parse_cost(cost_text):
    """
    Convert values such as:
    $41m
    $42m
    USD 41 million
    USD 42 million

    into a numeric USD million value.
    """

    text = cost_text.strip().lower()

    match = re.search(
        r"(?:us\$|usd|\$)\s*(\d+(?:\.\d+)?)\s*(million|m|billion|bn)",
        text
    )

    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2)

    if unit in ["billion", "bn"]:
        value = value * 1000

    return value


def normalize_cost_evidence(cost_evidence):
    normalized = []

    for source in cost_evidence:

        costs = []

        for item in source.get("costs_found", []):
            cost_text = item.get("cost")
            cost_value = parse_cost(cost_text)

            if cost_value is not None:
                costs.append(cost_value)

        if not costs:
            continue

        cost_min = min(costs)
        cost_max = max(costs)

        cost_midpoint = round(
            (cost_min + cost_max) / 2,
            2
        )

        normalized.append({
            "vessel": "Ulstein PX121",
            "cost_min_million_usd": cost_min,
            "cost_max_million_usd": cost_max,
            "cost_midpoint_million_usd": cost_midpoint,
            "currency": "USD",
            "cost_unit": "million",
            "cost_year": 2024,
            "cost_type": "Newbuilding slot / asking price",
            "scope": "Per vessel",
            "limitation": "Excluding option items",
            "source_title": source.get("title"),
            "source_url": source.get("url"),
            "evidence": source.get("costs_found")
        })

    return normalized


if __name__ == "__main__":

    cost_evidence = load_json(COST_PATH)

    normalized_costs = normalize_cost_evidence(
        cost_evidence
    )

    with open(NORMALIZED_PATH, "w", encoding="utf-8") as file:
        json.dump(
            normalized_costs,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved {len(normalized_costs)} normalized cost records "
        f"to: {NORMALIZED_PATH}"
    )

    for cost in normalized_costs:
        print("\nVessel:", cost["vessel"])
        print(
            "Cost Range:",
            cost["cost_min_million_usd"],
            "-",
            cost["cost_max_million_usd"],
            "million USD"
        )
        print(
            "Midpoint:",
            cost["cost_midpoint_million_usd"],
            "million USD"
        )
        print("Year:", cost["cost_year"])
        print("Type:", cost["cost_type"])
        print("Scope:", cost["scope"])
        print("Limitation:", cost["limitation"])