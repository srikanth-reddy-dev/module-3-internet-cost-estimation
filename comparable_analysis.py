import json


MATCH_PATH = "data/output/spec_matches.json"
COST_PATH = "data/output/adjusted_costs.json"
ANALYSIS_PATH = "data/output/comparable_analysis.json"


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def get_design(vessel_match):
    """
    Get the comparable vessel design from
    specification matches.
    """

    for match in vessel_match.get(
        "matches",
        []
    ):

        if match.get(
            "specification"
        ) == "Design":

            return str(
                match.get(
                    "internet",
                    ""
                )
            ).strip()

    return None


def get_match_percentage(
    vessel_match,
    specification
):
    """
    Get a specification match percentage.
    """

    for match in vessel_match.get(
        "matches",
        []
    ):

        if match.get(
            "specification"
        ) == specification:

            return match.get(
                "match_percentage"
            )

    return None


def find_primary_cost(
    costs
):
    """
    Get the primary adjusted cost record.

    The current cost_adjuster.py creates
    exactly one primary_adjusted_cost record.
    """

    if isinstance(
        costs,
        dict
    ):

        primary = costs.get(
            "primary_adjusted_cost"
        )

        if primary:

            return primary

    return None


def is_primary_comparable(
    vessel_match,
    primary_cost
):
    """
    Check whether a specification-match record
    represents the same primary comparable vessel
    used by the cost adjustment stage.
    """

    if not primary_cost:

        return False

    vessel_name = str(
        vessel_match.get(
            "vessel_name",
            ""
        )
    ).lower()

    primary_vessel = str(
        primary_cost.get(
            "comparable_vessel",
            ""
        )
    ).lower()

    # --------------------------------------------------------
    # Exact / strong current comparable identification
    # --------------------------------------------------------

    if (
        "shin yang" in vessel_name
        and "shin yang" in primary_vessel
    ):

        return True

    if (
        "dayang" in vessel_name
        and "dayang" in primary_vessel
    ):

        return True

    if (
        "91m" in vessel_name
        and "91m" in primary_vessel
        and (
            "maintenance" in vessel_name
            or "work vessel" in vessel_name
        )
    ):

        return True

    return False


def build_specification_summary(
    vessel_match
):
    """
    Build a clean specification comparison summary.

    Missing specifications remain unavailable.
    """

    specifications = [
        "Design",
        "Vessel Type",
        "LOA",
        "Breadth",
        "Depth",
        "DWT",
        "Service Speed",
        "Deck Area",
        "Design Draft",
        "Maximum Draft"
    ]

    summary = []

    for specification in specifications:

        for match in vessel_match.get(
            "matches",
            []
        ):

            if match.get(
                "specification"
            ) != specification:

                continue

            percentage = match.get(
                "match_percentage"
            )

            item = {

                "specification":
                    specification,

                "input":
                    match.get(
                        "input"
                    ),

                "internet":
                    match.get(
                        "internet"
                    ),

                "match":
                    match.get(
                        "match"
                    ),

                "match_percentage":
                    percentage,

                "available":
                    percentage is not None
            }

            summary.append(
                item
            )

            break

    return summary


def calculate_available_match_average(
    vessel_match
):
    """
    Calculate the average of available numeric
    specification match percentages.

    This is used only as a descriptive metric.

    It is NOT used as a cost multiplier.
    """

    percentages = []

    for match in vessel_match.get(
        "matches",
        []
    ):

        percentage = match.get(
            "match_percentage"
        )

        if percentage is not None:

            percentages.append(
                float(percentage)
            )

    if not percentages:

        return None

    return round(
        sum(percentages)
        / len(percentages),
        2
    )


def build_cost_summary(
    primary_cost
):
    """
    Extract the cost scenarios produced by
    cost_adjuster.py.
    """

    if not primary_cost:

        return None

    return {

        "original_cost": primary_cost.get(
            "original_cost"
        ),

        "original_currency": primary_cost.get(
            "original_currency"
        ),

        "original_cost_million": primary_cost.get(
            "original_cost_million"
        ),

        "cost_year": primary_cost.get(
            "cost_year"
        ),

        "low_scenario": primary_cost.get(
            "low_scenario"
        ),

        "base_scenario": primary_cost.get(
            "base_scenario"
        ),

        "high_scenario": primary_cost.get(
            "high_scenario"
        ),

        "myr_to_inr": primary_cost.get(
            "myr_to_inr"
        ),

        "target_country": primary_cost.get(
            "target_country"
        ),

        "target_currency": primary_cost.get(
            "target_currency"
        ),

        "source_title": primary_cost.get(
            "source_title"
        ),

        "source_url": primary_cost.get(
            "source_url"
        ),

        "methodology": primary_cost.get(
            "methodology"
        ),

        "prototype_warning": primary_cost.get(
            "prototype_warning"
        )
    }


def build_analysis(
    matches,
    primary_cost
):
    """
    Build the comparable vessel analysis.

    All specification matches are retained.

    Cost information is attached only to the
    primary Shin Yang / Dayang comparable.
    """

    analysis = []

    for vessel_match in matches:

        vessel_name = vessel_match.get(
            "vessel_name"
        )

        design = get_design(
            vessel_match
        )

        specification_summary = (
            build_specification_summary(
                vessel_match
            )
        )

        average_match = (
            calculate_available_match_average(
                vessel_match
            )
        )

        primary = is_primary_comparable(
            vessel_match,
            primary_cost
        )

        record = {

            # ------------------------------------------------
            # Vessel identification
            # ------------------------------------------------

            "vessel_name":
                vessel_name,

            "design":
                design,

            "is_primary_comparable":
                primary,

            # ------------------------------------------------
            # Specification comparison
            # ------------------------------------------------

            "overall_match_percentage":
                vessel_match.get(
                    "overall_match_percentage"
                ),

            "available_specification_average":
                average_match,

            "specification_matches":
                specification_summary,

            # ------------------------------------------------
            # Cost evidence
            # ------------------------------------------------

            "cost_evidence":
                (
                    build_cost_summary(
                        primary_cost
                    )
                    if primary
                    else None
                )
        }

        analysis.append(
            record
        )

    return analysis


def print_analysis(
    analysis
):
    """
    Print a readable comparable analysis.
    """

    print(
        "\n" + "=" * 60
    )

    print(
        "COMPARABLE VESSEL ANALYSIS"
    )

    print(
        "=" * 60
    )

    for vessel in analysis:

        print(
            "\nVessel:"
        )

        print(
            vessel[
                "vessel_name"
            ]
        )

        print(
            "Design:",
            vessel[
                "design"
            ]
        )

        print(
            "Primary Comparable:",
            vessel[
                "is_primary_comparable"
            ]
        )

        print(
            "Overall Match:",
            vessel[
                "overall_match_percentage"
            ],
            "%"
        )

        print(
            "Available Specification Average:",
            vessel[
                "available_specification_average"
            ],
            "%"
        )

        print(
            "\nSpecification Matches:"
        )

        for match in vessel[
            "specification_matches"
        ]:

            specification = match.get(
                "specification"
            )

            input_value = match.get(
                "input"
            )

            internet_value = match.get(
                "internet"
            )

            percentage = match.get(
                "match_percentage"
            )

            if percentage is None:

                print(
                    f"  {specification}: "
                    f"{input_value} -> "
                    f"{internet_value} = "
                    "Not available"
                )

            else:

                print(
                    f"  {specification}: "
                    f"{input_value} -> "
                    f"{internet_value} = "
                    f"{percentage}%"
                )

        # ----------------------------------------------------
        # COST
        # ----------------------------------------------------

        cost = vessel.get(
            "cost_evidence"
        )

        print(
            "\nCost Evidence:"
        )

        if cost:

            print(
                "  Original Cost:",
                cost[
                    "original_cost_million"
                ],
                "million",
                cost[
                    "original_currency"
                ]
            )

            print(
                "  Cost Year:",
                cost[
                    "cost_year"
                ]
            )

            # ------------------------------------------------
            # LOW
            # ------------------------------------------------

            low = cost[
                "low_scenario"
            ]

            print(
                "\n  Low Scenario:"
            )

            print(
                "    Adjustment:",
                low[
                    "adjustment_percentage"
                ],
                "%"
            )

            print(
                "    Cost:",
                low[
                    "adjusted_cost_million_myr"
                ],
                "million MYR"
            )

            print(
                "    INR:",
                low[
                    "adjusted_cost_million_inr"
                ],
                "million INR"
            )

            # ------------------------------------------------
            # BASE
            # ------------------------------------------------

            base = cost[
                "base_scenario"
            ]

            print(
                "\n  Base Scenario:"
            )

            print(
                "    Adjustment:",
                base[
                    "adjustment_percentage"
                ],
                "%"
            )

            print(
                "    Cost:",
                base[
                    "adjusted_cost_million_myr"
                ],
                "million MYR"
            )

            print(
                "    INR:",
                base[
                    "adjusted_cost_million_inr"
                ],
                "million INR"
            )

            # ------------------------------------------------
            # HIGH
            # ------------------------------------------------

            high = cost[
                "high_scenario"
            ]

            print(
                "\n  High Scenario:"
            )

            print(
                "    Adjustment:",
                high[
                    "adjustment_percentage"
                ],
                "%"
            )

            print(
                "    Cost:",
                high[
                    "adjusted_cost_million_myr"
                ],
                "million MYR"
            )

            print(
                "    INR:",
                high[
                    "adjusted_cost_million_inr"
                ],
                "million INR"
            )

            # ------------------------------------------------
            # SOURCE
            # ------------------------------------------------

            print(
                "\n  Source:"
            )

            print(
                "   ",
                cost[
                    "source_title"
                ]
            )

            print(
                "   ",
                cost[
                    "source_url"
                ]
            )

        else:

            print(
                "  No cost evidence attached."
            )

    print(
        "\n" + "=" * 60
    )


def main():

    # ========================================================
    # LOAD INPUTS
    # ========================================================

    matches = load_json(
        MATCH_PATH
    )

    cost_data = load_json(
        COST_PATH
    )

    # ========================================================
    # PRIMARY COST
    # ========================================================

    primary_cost = find_primary_cost(
        cost_data
    )

    if primary_cost is None:

        raise ValueError(
            "No primary adjusted cost found "
            "in adjusted_costs.json."
        )

    # ========================================================
    # BUILD ANALYSIS
    # ========================================================

    analysis = build_analysis(
        matches,
        primary_cost
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    output = {

        "primary_comparable":
            primary_cost.get(
                "comparable_vessel"
            ),

        "primary_match_percentage":
            primary_cost.get(
                "comparable_match_percentage"
            ),

        "comparable_count":
            len(
                analysis
            ),

        "analysis":
            analysis
    }

    with open(
        ANALYSIS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    # ========================================================
    # PRINT
    # ========================================================

    print(
        f"Saved {len(analysis)} comparable vessel analyses "
        f"to: {ANALYSIS_PATH}"
    )

    print_analysis(
        analysis
    )


if __name__ == "__main__":

    main()