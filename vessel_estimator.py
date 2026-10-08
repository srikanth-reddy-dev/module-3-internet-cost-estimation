import json


ANALYSIS_PATH = "data/output/comparable_analysis.json"
ESTIMATE_PATH = "data/output/final_estimate.json"


def load_analysis():
    with open(
        ANALYSIS_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def calculate_estimate(data):
    """
    Build the vessel-level cost estimate from
    comparable_analysis.json.

    Only comparables with verified cost evidence
    are used for the cost estimate.

    Supporting comparables without cost evidence
    are retained for transparency but are not
    assigned an estimated price.
    """

    analysis = data.get(
        "analysis",
        []
    )

    usable_costs = []

    comparable_vessels_used = []

    comparables_without_cost = []

    # ========================================================
    # COLLECT COST-BEARING COMPARABLES
    # ========================================================

    for vessel in analysis:

        vessel_name = vessel.get(
            "vessel_name"
        )

        cost = vessel.get(
            "cost_evidence"
        )

        if not cost:

            comparables_without_cost.append(
                vessel_name
            )

            continue

        low = cost.get(
            "low_scenario"
        )

        base = cost.get(
            "base_scenario"
        )

        high = cost.get(
            "high_scenario"
        )

        if (
            not low
            or not base
            or not high
        ):

            comparables_without_cost.append(
                vessel_name
            )

            continue

        low_cost = low.get(
            "adjusted_cost_million_myr"
        )

        base_cost = base.get(
            "adjusted_cost_million_myr"
        )

        high_cost = high.get(
            "adjusted_cost_million_myr"
        )

        low_inr = low.get(
            "adjusted_cost_million_inr"
        )

        base_inr = base.get(
            "adjusted_cost_million_inr"
        )

        high_inr = high.get(
            "adjusted_cost_million_inr"
        )

        if (
            low_cost is None
            or base_cost is None
            or high_cost is None
        ):

            comparables_without_cost.append(
                vessel_name
            )

            continue

        usable_costs.append({

            "vessel_name":
                vessel_name,

            "low_million_myr":
                low_cost,

            "base_million_myr":
                base_cost,

            "high_million_myr":
                high_cost,

            "low_million_inr":
                low_inr,

            "base_million_inr":
                base_inr,

            "high_million_inr":
                high_inr,

            "match_percentage":
                vessel.get(
                    "overall_match_percentage"
                ),

            "source_title":
                cost.get(
                    "source_title"
                ),

            "source_url":
                cost.get(
                    "source_url"
                )
        })

        comparable_vessels_used.append(
            vessel_name
        )

    # ========================================================
    # NO COST EVIDENCE
    # ========================================================

    if not usable_costs:

        return {

            "estimate":
                None,

            "currency":
                "MYR",

            "target_currency":
                "INR",

            "comparable_vessels_used":
                [],

            "comparables_without_cost":
                comparables_without_cost,

            "assumptions": [

                (
                    "No comparable vessel with "
                    "usable cost evidence was found."
                ),

                (
                    "No cost was inferred for vessels "
                    "without direct cost evidence."
                )
            ]
        }

    # ========================================================
    # CURRENT DATASET
    # ========================================================
    #
    # At present there is one verified cost-bearing
    # comparable: Shin Yang / Dayang.
    #
    # Therefore the vessel-level estimate is based
    # directly on its scenario costs.
    #
    # If additional verified cost-bearing comparables
    # are added later, their scenario values can be
    # combined here.
    # ========================================================

    low_cost_myr = sum(
        item[
            "low_million_myr"
        ]
        for item in usable_costs
    ) / len(
        usable_costs
    )

    base_cost_myr = sum(
        item[
            "base_million_myr"
        ]
        for item in usable_costs
    ) / len(
        usable_costs
    )

    high_cost_myr = sum(
        item[
            "high_million_myr"
        ]
        for item in usable_costs
    ) / len(
        usable_costs
    )

    low_cost_inr = sum(
        item[
            "low_million_inr"
        ]
        for item in usable_costs
        if item[
            "low_million_inr"
        ] is not None
    )

    base_cost_inr = sum(
        item[
            "base_million_inr"
        ]
        for item in usable_costs
        if item[
            "base_million_inr"
        ] is not None
    )

    high_cost_inr = sum(
        item[
            "high_million_inr"
        ]
        for item in usable_costs
        if item[
            "high_million_inr"
        ] is not None
    )

    # ========================================================
    # BUILD ESTIMATE
    # ========================================================

    return {

        "estimate": {

            "low": {

                "million_myr":
                    round(
                        low_cost_myr,
                        4
                    ),

                "million_inr":
                    round(
                        low_cost_inr,
                        4
                    ),

                "crore_inr":
                    round(
                        low_cost_inr
                        / 10,
                        4
                    )
            },

            "base": {

                "million_myr":
                    round(
                        base_cost_myr,
                        4
                    ),

                "million_inr":
                    round(
                        base_cost_inr,
                        4
                    ),

                "crore_inr":
                    round(
                        base_cost_inr
                        / 10,
                        4
                    )
            },

            "high": {

                "million_myr":
                    round(
                        high_cost_myr,
                        4
                    ),

                "million_inr":
                    round(
                        high_cost_inr,
                        4
                    ),

                "crore_inr":
                    round(
                        high_cost_inr
                        / 10,
                        4
                    )
            }
        },

        "currency":
            "MYR",

        "target_currency":
            "INR",

        "comparable_vessels_used":
            comparable_vessels_used,

        "comparables_without_cost":
            comparables_without_cost,

        "cost_bearing_comparable_count":
            len(
                usable_costs
            ),

        "cost_bearing_comparables":
            usable_costs,

        "assumptions": [

            (
                "Only comparable vessels with "
                "available direct cost evidence "
                "were used for the vessel-level "
                "cost estimate."
            ),

            (
                "The Shin Yang / Dayang 91M "
                "Maintenance/Work Vessel is the "
                "current primary cost-bearing "
                "comparable."
            ),

            (
                "Energy Pace and ULSTEIN PX121 H "
                "are retained as technical "
                "comparables but have no verified "
                "purchase cost and therefore are "
                "not assigned a cost."
            ),

            (
                "Low, base, and high values come "
                "from the scenario-based cost "
                "adjustment stage."
            ),

            (
                "The 0%, 5%, and 10% scenario "
                "adjustments are prototype "
                "assumptions."
            ),

            (
                "Specification match percentage "
                "is used as a comparison metric "
                "and is not directly multiplied "
                "against vessel cost."
            ),

            (
                "No cost was inferred for vessels "
                "without direct cost evidence."
            ),

            (
                "The MYR-to-INR conversion is a "
                "prototype conversion used for "
                "display purposes."
            )
        ]
    }


def print_estimate(result):

    print(
        "\n" + "=" * 60
    )

    print(
        "VESSEL-LEVEL COST ESTIMATE"
    )

    print(
        "=" * 60
    )

    estimate = result.get(
        "estimate"
    )

    if not estimate:

        print(
            "\nNo usable cost evidence available."
        )

        return

    # ========================================================
    # LOW
    # ========================================================

    print(
        "\nLOW SCENARIO"
    )

    print(
        "Cost:",
        estimate[
            "low"
        ][
            "million_myr"
        ],
        "million MYR"
    )

    print(
        "INR:",
        estimate[
            "low"
        ][
            "million_inr"
        ],
        "million INR"
    )

    print(
        "INR:",
        estimate[
            "low"
        ][
            "crore_inr"
        ],
        "crore"
    )

    # ========================================================
    # BASE
    # ========================================================

    print(
        "\nBASE SCENARIO"
    )

    print(
        "Cost:",
        estimate[
            "base"
        ][
            "million_myr"
        ],
        "million MYR"
    )

    print(
        "INR:",
        estimate[
            "base"
        ][
            "million_inr"
        ],
        "million INR"
    )

    print(
        "INR:",
        estimate[
            "base"
        ][
            "crore_inr"
        ],
        "crore"
    )

    # ========================================================
    # HIGH
    # ========================================================

    print(
        "\nHIGH SCENARIO"
    )

    print(
        "Cost:",
        estimate[
            "high"
        ][
            "million_myr"
        ],
        "million MYR"
    )

    print(
        "INR:",
        estimate[
            "high"
        ][
            "million_inr"
        ],
        "million INR"
    )

    print(
        "INR:",
        estimate[
            "high"
        ][
            "crore_inr"
        ],
        "crore"
    )

    # ========================================================
    # COMPARABLES
    # ========================================================

    print(
        "\nComparable Vessels Used:"
    )

    for vessel in result[
        "comparable_vessels_used"
    ]:

        print(
            "-",
            vessel
        )

    print(
        "\nComparables Without Cost Evidence:"
    )

    for vessel in result[
        "comparables_without_cost"
    ]:

        print(
            "-",
            vessel
        )

    # ========================================================
    # ASSUMPTIONS
    # ========================================================

    print(
        "\nAssumptions:"
    )

    for assumption in result[
        "assumptions"
    ]:

        print(
            "-",
            assumption
        )


def main():

    # ========================================================
    # LOAD ANALYSIS
    # ========================================================

    data = load_analysis()

    # ========================================================
    # CALCULATE ESTIMATE
    # ========================================================

    result = calculate_estimate(
        data
    )

    # ========================================================
    # SAVE
    # ========================================================

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
        f"Saved final estimate to: "
        f"{ESTIMATE_PATH}"
    )

    # ========================================================
    # PRINT
    # ========================================================

    print_estimate(
        result
    )


if __name__ == "__main__":

    main()