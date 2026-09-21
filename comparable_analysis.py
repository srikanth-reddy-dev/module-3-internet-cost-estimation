import json

MATCH_PATH = "data/output/spec_matches.json"
COST_PATH = "data/output/adjusted_costs.json"
ANALYSIS_PATH = "data/output/comparable_analysis.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_design(vessel_match):
    """
    Get the comparable vessel design from specification matches.
    """
    for match in vessel_match.get("matches", []):
        if match.get("specification") == "Design":
            return str(match.get("internet", "")).strip()

    return None


def find_cost_by_design(vessel_match, costs):
    """
    Attach cost evidence only when the design matches exactly.

    Example:
        Ulstein PX121 -> Ulstein PX121       = match
        Ulstein PX121 H -> Ulstein PX121     = no match
    """

    vessel_design = get_design(vessel_match)

    if not vessel_design:
        return None

    vessel_design = vessel_design.lower()

    for cost in costs:
        cost_design = str(
            cost.get("vessel", "")
        ).strip().lower()

        if cost_design == vessel_design:
            return cost

    return None


def build_analysis():
    matches = load_json(MATCH_PATH)
    costs = load_json(COST_PATH)

    analysis = []

    for vessel_match in matches:

        vessel_name = vessel_match.get("vessel_name")

        cost_data = find_cost_by_design(
            vessel_match,
            costs
        )

        analysis.append({
            "vessel_name": vessel_name,
            "design": get_design(vessel_match),
            "specification_matches": vessel_match.get(
                "matches",
                []
            ),
            "adjusted_cost": cost_data
        })

    return analysis


def print_analysis(analysis):

    for vessel in analysis:

        print("\nVessel:", vessel["vessel_name"])
        print("Design:", vessel["design"])

        print("\nSpecification Matches:")

        for match in vessel["specification_matches"]:

            specification = match.get("specification")

            if "match_percentage" in match:

                percentage = match.get("match_percentage")

                if percentage is None:

                    print(
                        f"{specification}: "
                        f"{match.get('input')} -> "
                        f"{match.get('internet')} = "
                        "Not available"
                    )

                else:

                    print(
                        f"{specification}: "
                        f"{match.get('input')} -> "
                        f"{match.get('internet')} = "
                        f"{percentage}%"
                    )

            else:

                print(
                    f"{specification}: "
                    f"{match.get('input')} -> "
                    f"{match.get('internet')} = "
                    f"{match.get('match')}"
                )

        cost = vessel.get("adjusted_cost")

        print("\nCost Evidence:")

        if cost:

            print(
                "Original Cost:",
                cost["original_cost_min_million_usd"],
                "-",
                cost["original_cost_max_million_usd"],
                "million USD"
            )

            print(
                "Adjusted Cost:",
                cost["adjusted_cost_min_million_usd"],
                "-",
                cost["adjusted_cost_max_million_usd"],
                "million USD"
            )

            print(
                "Adjusted Midpoint:",
                cost["adjusted_cost_midpoint_million_usd"],
                "million USD"
            )

            print(
                "Adjusted Midpoint:",
                cost["adjusted_cost_midpoint_million_inr"],
                "million INR"
            )

            print(
                "Cost Year:",
                cost["cost_year"]
            )

            print(
                "Target Year:",
                cost["target_year"]
            )

            print(
                "Adjustment Note:",
                cost["adjustment_note"]
            )

        else:

            print(
                "No matching cost evidence found."
            )


if __name__ == "__main__":

    analysis = build_analysis()

    with open(
        ANALYSIS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            analysis,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved {len(analysis)} comparable vessel analyses "
        f"to: {ANALYSIS_PATH}"
    )

    print_analysis(analysis)