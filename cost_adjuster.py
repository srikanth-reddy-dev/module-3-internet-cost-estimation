import json

NORMALIZED_PATH = "data/output/normalized_costs.json"
ADJUSTED_PATH = "data/output/adjusted_costs.json"


# Sample prototype assumptions.
# These are NOT client-approved values.
ADJUSTMENT_CONFIG = {
    "target_year": 2026,
    "target_country": "India",
    "target_currency": "INR",

    # Sample factors for prototype testing
    "year_adjustment_factor": 1.05,
    "country_adjustment_factor": 0.95,

    # Sample USD -> INR conversion ratio
    "usd_to_inr": 88.0
}


def load_costs():
    with open(
        NORMALIZED_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def adjust_cost(cost):

    year_factor = ADJUSTMENT_CONFIG[
        "year_adjustment_factor"
    ]

    country_factor = ADJUSTMENT_CONFIG[
        "country_adjustment_factor"
    ]

    usd_to_inr = ADJUSTMENT_CONFIG[
        "usd_to_inr"
    ]

    # --------------------------------------------------
    # Apply year and country adjustment factors
    # --------------------------------------------------

    adjusted_min_usd = (
        cost["cost_min_million_usd"]
        * year_factor
        * country_factor
    )

    adjusted_max_usd = (
        cost["cost_max_million_usd"]
        * year_factor
        * country_factor
    )

    adjusted_midpoint_usd = (
        cost["cost_midpoint_million_usd"]
        * year_factor
        * country_factor
    )

    # --------------------------------------------------
    # Build adjusted cost record
    # --------------------------------------------------

    return {

        # Vessel
        "vessel": cost["vessel"],

        # Original cost
        "original_cost_min_million_usd":
            cost["cost_min_million_usd"],

        "original_cost_max_million_usd":
            cost["cost_max_million_usd"],

        "original_cost_midpoint_million_usd":
            cost["cost_midpoint_million_usd"],

        # Cost year
        "cost_year":
            cost["cost_year"],

        "target_year":
            ADJUSTMENT_CONFIG["target_year"],

        # Adjustment factors
        "year_adjustment_factor":
            year_factor,

        "country_adjustment_factor":
            country_factor,

        # Adjusted USD cost
        "adjusted_cost_min_million_usd":
            round(adjusted_min_usd, 2),

        "adjusted_cost_max_million_usd":
            round(adjusted_max_usd, 2),

        "adjusted_cost_midpoint_million_usd":
            round(adjusted_midpoint_usd, 2),

        # Adjusted INR cost
        "adjusted_cost_min_million_inr":
            round(
                adjusted_min_usd
                * usd_to_inr
                * 10,
                2
            ),

        "adjusted_cost_max_million_inr":
            round(
                adjusted_max_usd
                * usd_to_inr
                * 10,
                2
            ),

        "adjusted_cost_midpoint_million_inr":
            round(
                adjusted_midpoint_usd
                * usd_to_inr
                * 10,
                2
            ),

        # Currency conversion
        "usd_to_inr":
            usd_to_inr,

        # Target information
        "target_country":
            ADJUSTMENT_CONFIG["target_country"],

        "target_currency":
            ADJUSTMENT_CONFIG["target_currency"],

        # --------------------------------------------------
        # Preserve original cost evidence metadata
        # --------------------------------------------------

        "cost_type":
            cost.get("cost_type"),

        "scope":
            cost.get("scope"),

        "limitation":
            cost.get("limitation"),

        "source_title":
            cost.get("source_title"),

        "source_url":
            cost.get("source_url"),

        # Adjustment note
        "adjustment_note":
            "Sample prototype adjustment factors. "
            "Values are not client-approved."
    }


if __name__ == "__main__":

    costs = load_costs()

    adjusted_costs = []

    for cost in costs:

        adjusted_costs.append(
            adjust_cost(cost)
        )

    # Save adjusted costs
    with open(
        ADJUSTED_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            adjusted_costs,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved {len(adjusted_costs)} "
        f"adjusted cost records to: "
        f"{ADJUSTED_PATH}"
    )

    # Display results
    for cost in adjusted_costs:

        print(
            "\nVessel:",
            cost["vessel"]
        )

        print(
            "Original:",
            cost["original_cost_min_million_usd"],
            "-",
            cost["original_cost_max_million_usd"],
            "million USD"
        )

        print(
            "Adjusted:",
            cost["adjusted_cost_min_million_usd"],
            "-",
            cost["adjusted_cost_max_million_usd"],
            "million USD"
        )

        print(
            "Adjusted midpoint:",
            cost["adjusted_cost_midpoint_million_usd"],
            "million USD"
        )

        print(
            "Adjusted midpoint:",
            cost["adjusted_cost_midpoint_million_inr"],
            "million INR"
        )

        print(
            "Cost Type:",
            cost.get("cost_type")
        )

        print(
            "Scope:",
            cost.get("scope")
        )

        print(
            "Source:",
            cost.get("source_title")
        )

        print(
            "URL:",
            cost.get("source_url")
        )