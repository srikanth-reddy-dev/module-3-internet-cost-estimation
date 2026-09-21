import json

ANALYSIS_PATH = "data/output/comparable_analysis.json"
ESTIMATE_PATH = "data/output/final_estimate.json"


def load_analysis():
    with open(ANALYSIS_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_estimate(analysis):
    usable_costs = []
    comparable_vessels_used = []
    comparables_without_cost = []

    for vessel in analysis:

        vessel_name = vessel.get("vessel_name")
        cost = vessel.get("adjusted_cost")

        if not cost:
            comparables_without_cost.append(vessel_name)
            continue

        midpoint = cost.get(
            "adjusted_cost_midpoint_million_usd"
        )

        minimum = cost.get(
            "adjusted_cost_min_million_usd"
        )

        maximum = cost.get(
            "adjusted_cost_max_million_usd"
        )

        if (
            midpoint is None
            or minimum is None
            or maximum is None
        ):
            comparables_without_cost.append(vessel_name)
            continue

        usable_costs.append({
            "vessel_name": vessel_name,
            "min": minimum,
            "max": maximum,
            "midpoint": midpoint
        })

        comparable_vessels_used.append(vessel_name)

    if not usable_costs:
        return {
            "estimate": None,
            "currency": "USD",
            "comparable_vessels_used": [],
            "comparables_without_cost": comparables_without_cost,
            "assumptions": [
                "No comparable vessel with usable cost evidence was found."
            ]
        }

    # Prototype approach:
    # Use the average of available comparable vessel costs.
    min_cost = sum(
        item["min"] for item in usable_costs
    ) / len(usable_costs)

    max_cost = sum(
        item["max"] for item in usable_costs
    ) / len(usable_costs)

    midpoint_cost = sum(
        item["midpoint"] for item in usable_costs
    ) / len(usable_costs)

    return {
        "estimate": {
            "min_million_usd": round(min_cost, 2),
            "max_million_usd": round(max_cost, 2),
            "midpoint_million_usd": round(midpoint_cost, 2)
        },
        "currency": "USD",
        "comparable_vessels_used": comparable_vessels_used,
        "comparables_without_cost": comparables_without_cost,
        "assumptions": [
            "Only comparable vessels with available cost evidence were used.",
            "The estimate uses the average of available comparable vessel costs.",
            "Cost adjustment factors are prototype assumptions.",
            "Specification matching methodology is still a prototype.",
            "No cost was inferred for vessels without direct cost evidence."
        ]
    }


def print_estimate(result):

    print("\n" + "=" * 60)
    print("VESSEL-LEVEL COST ESTIMATE")
    print("=" * 60)

    estimate = result.get("estimate")

    if not estimate:
        print("\nNo usable cost evidence available.")
        return

    print(
        "\nEstimated Cost Range:",
        estimate["min_million_usd"],
        "-",
        estimate["max_million_usd"],
        "million USD"
    )

    print(
        "Estimated Midpoint:",
        estimate["midpoint_million_usd"],
        "million USD"
    )

    print(
        "\nComparable Vessels Used:"
    )

    for vessel in result["comparable_vessels_used"]:
        print("-", vessel)

    print(
        "\nComparables Without Cost Evidence:"
    )

    for vessel in result["comparables_without_cost"]:
        print("-", vessel)

    print("\nAssumptions:")

    for assumption in result["assumptions"]:
        print("-", assumption)


if __name__ == "__main__":

    analysis = load_analysis()

    result = calculate_estimate(analysis)

    with open(
        ESTIMATE_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved final estimate to: {ESTIMATE_PATH}"
    )

    print_estimate(result)