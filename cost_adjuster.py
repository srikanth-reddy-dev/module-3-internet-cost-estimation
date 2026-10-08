import json


NORMALIZED_PATH = "data/output/normalized_costs.json"
MATCH_PATH = "data/output/spec_matches.json"
ADJUSTED_PATH = "data/output/adjusted_costs.json"


# ============================================================
# PROTOTYPE SCENARIO CONFIGURATION
# ============================================================
#
# IMPORTANT:
# These are scenario assumptions only.
#
# They are NOT:
# - market prices
# - client-approved factors
# - engineering cost coefficients
# - historical regression coefficients
#
# Once historical vessel-cost data becomes available,
# these scenario percentages should be replaced by a
# calibrated cost model.
# ============================================================

ADJUSTMENT_CONFIG = {

    "target_country": "India",

    "target_currency": "INR",

    # --------------------------------------------------------
    # Prototype MYR -> INR conversion
    # --------------------------------------------------------
    #
    # This is only for displaying an INR equivalent.
    #
    "myr_to_inr": 20.0,

    # --------------------------------------------------------
    # Scenario assumptions
    # --------------------------------------------------------
    #
    # Low:
    # Assume no additional specification premium.
    #
    # Base:
    # Apply a moderate 5% prototype adjustment.
    #
    # High:
    # Apply a 10% prototype adjustment.
    #
    "low_adjustment_percentage": 0.0,

    "base_adjustment_percentage": 5.0,

    "high_adjustment_percentage": 10.0
}


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def get_primary_normalized_cost(
    normalized_data
):
    """
    Get the primary comparable cost.
    """

    primary = normalized_data.get(
        "primary_comparable"
    )

    if primary:
        return primary

    normalized_costs = normalized_data.get(
        "normalized_costs",
        []
    )

    if normalized_costs:

        return normalized_costs[0]

    return None


def find_primary_match(
    spec_matches
):
    """
    Find the Shin Yang / Dayang comparable.
    """

    for result in spec_matches:

        vessel_name = str(
            result.get(
                "vessel_name"
            ) or ""
        ).lower()

        if (
            "shin yang" in vessel_name
            or "dayang" in vessel_name
            or "91m maintenance/work vessel"
            in vessel_name
        ):

            return result

    return None


def get_match_value(
    match_result,
    specification
):
    """
    Get the numeric specification match percentage.
    """

    for match in match_result.get(
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


def calculate_difference(
    match_percentage
):
    """
    Convert similarity into specification difference.

    Example:

    99.78% similarity
    -> 0.22% difference
    """

    if match_percentage is None:
        return None

    return round(
        max(
            0,
            100 - match_percentage
        ),
        2
    )


def collect_specification_differences(
    match_result
):
    """
    Collect available specification differences.

    Missing values are retained as unavailable and
    are NOT converted to zero.
    """

    specifications = [
        "LOA",
        "Breadth",
        "Depth",
        "DWT",
        "Service Speed",
        "Deck Area",
        "Design Draft",
        "Maximum Draft"
    ]

    differences = []

    for specification in specifications:

        match_percentage = get_match_value(
            match_result,
            specification
        )

        difference_percentage = (
            calculate_difference(
                match_percentage
            )
        )

        differences.append({

            "specification":
                specification,

            "match_percentage":
                match_percentage,

            "difference_percentage":
                difference_percentage,

            "available":
                difference_percentage is not None
        })

    return differences


def calculate_scenario_cost(
    original_cost,
    adjustment_percentage
):
    """
    Apply a scenario adjustment to the
    comparable vessel cost.
    """

    factor = (
        1
        + adjustment_percentage / 100
    )

    return round(
        original_cost * factor,
        2
    )


def convert_myr_to_inr(
    myr_amount
):
    """
    Convert MYR to INR using the configured
    prototype exchange rate.
    """

    rate = ADJUSTMENT_CONFIG[
        "myr_to_inr"
    ]

    return round(
        myr_amount * rate,
        2
    )


def build_scenario(
    original_cost,
    adjustment_percentage
):
    """
    Build one cost scenario.
    """

    adjusted_cost = calculate_scenario_cost(
        original_cost,
        adjustment_percentage
    )

    adjusted_cost_inr = convert_myr_to_inr(
        adjusted_cost
    )

    return {

        "adjustment_percentage":
            adjustment_percentage,

        "adjusted_cost_myr":
            adjusted_cost,

        "adjusted_cost_million_myr":
            round(
                adjusted_cost / 1_000_000,
                4
            ),

        "adjusted_cost_inr":
            adjusted_cost_inr,

        "adjusted_cost_million_inr":
            round(
                adjusted_cost_inr / 1_000_000,
                4
            )
    }


def build_adjusted_record(
    primary_cost,
    match_result
):

    original_cost = primary_cost.get(
        "reported_cost"
    )

    original_currency = primary_cost.get(
        "currency"
    )

    if original_cost is None:

        raise ValueError(
            "Primary comparable has no reported cost."
        )

    # ========================================================
    # SPECIFICATION DIFFERENCES
    # ========================================================

    specification_differences = (
        collect_specification_differences(
            match_result
        )
    )

    available_differences = [
        item
        for item in specification_differences
        if item["available"]
    ]

    # ========================================================
    # SCENARIOS
    # ========================================================

    low_scenario = build_scenario(
        original_cost,
        ADJUSTMENT_CONFIG[
            "low_adjustment_percentage"
        ]
    )

    base_scenario = build_scenario(
        original_cost,
        ADJUSTMENT_CONFIG[
            "base_adjustment_percentage"
        ]
    )

    high_scenario = build_scenario(
        original_cost,
        ADJUSTMENT_CONFIG[
            "high_adjustment_percentage"
        ]
    )

    # ========================================================
    # BUILD RESULT
    # ========================================================

    return {

        # ----------------------------------------------------
        # Comparable
        # ----------------------------------------------------

        "comparable_vessel":
            primary_cost.get(
                "vessel"
            ),

        "comparable_match_percentage":
            match_result.get(
                "overall_match_percentage"
            ),

        # ----------------------------------------------------
        # Original observed cost
        # ----------------------------------------------------

        "original_cost":
            original_cost,

        "original_currency":
            original_currency,

        "original_cost_million":
            round(
                original_cost / 1_000_000,
                4
            ),

        "cost_year":
            primary_cost.get(
                "cost_year"
            ),

        # ----------------------------------------------------
        # Specification comparison
        # ----------------------------------------------------

        "specification_differences":
            specification_differences,

        "available_specification_count":
            len(
                available_differences
            ),

        # ----------------------------------------------------
        # Scenario assumptions
        # ----------------------------------------------------

        "scenario_assumptions": {

            "low_percentage":
                ADJUSTMENT_CONFIG[
                    "low_adjustment_percentage"
                ],

            "base_percentage":
                ADJUSTMENT_CONFIG[
                    "base_adjustment_percentage"
                ],

            "high_percentage":
                ADJUSTMENT_CONFIG[
                    "high_adjustment_percentage"
                ],

            "basis":
                (
                    "Prototype scenario assumptions "
                    "used because validated historical "
                    "cost sensitivity coefficients are "
                    "not currently available."
                )
        },

        # ----------------------------------------------------
        # Low scenario
        # ----------------------------------------------------

        "low_scenario":
            low_scenario,

        # ----------------------------------------------------
        # Base scenario
        # ----------------------------------------------------

        "base_scenario":
            base_scenario,

        # ----------------------------------------------------
        # High scenario
        # ----------------------------------------------------

        "high_scenario":
            high_scenario,

        # ----------------------------------------------------
        # INR conversion
        # ----------------------------------------------------

        "myr_to_inr":
            ADJUSTMENT_CONFIG[
                "myr_to_inr"
            ],

        "target_country":
            ADJUSTMENT_CONFIG[
                "target_country"
            ],

        "target_currency":
            ADJUSTMENT_CONFIG[
                "target_currency"
            ],

        # ----------------------------------------------------
        # Source
        # ----------------------------------------------------

        "source_title":
            primary_cost.get(
                "source_title"
            ),

        "source_url":
            primary_cost.get(
                "source_url"
            ),

        # ----------------------------------------------------
        # Methodology
        # ----------------------------------------------------

        "methodology":
            (
                "Scenario-based comparable-vessel "
                "cost estimation. The observed "
                "comparable price is preserved as "
                "the evidence baseline. Low, base, "
                "and high scenarios are applied "
                "because validated historical cost "
                "sensitivity coefficients are not "
                "available."
            ),

        # ----------------------------------------------------
        # Warning
        # ----------------------------------------------------

        "prototype_warning":
            (
                "The 0%, 5%, and 10% adjustment "
                "scenarios are prototype assumptions. "
                "They are not client-approved commercial "
                "adjustments and should be calibrated "
                "using historical vessel-cost data."
            )
    }


def main():

    # ========================================================
    # LOAD NORMALIZED COST
    # ========================================================

    normalized_data = load_json(
        NORMALIZED_PATH
    )

    primary_cost = (
        get_primary_normalized_cost(
            normalized_data
        )
    )

    if primary_cost is None:

        raise ValueError(
            "No primary normalized cost found."
        )

    # ========================================================
    # LOAD SPECIFICATION MATCHES
    # ========================================================

    spec_matches = load_json(
        MATCH_PATH
    )

    match_result = find_primary_match(
        spec_matches
    )

    if match_result is None:

        raise ValueError(
            "Shin Yang / Dayang comparable "
            "was not found in spec_matches.json."
        )

    # ========================================================
    # BUILD ADJUSTED RECORD
    # ========================================================

    adjusted_record = build_adjusted_record(
        primary_cost,
        match_result
    )

    # ========================================================
    # SAVE
    # ========================================================

    output = {

        "primary_adjusted_cost":
            adjusted_record,

        "count":
            1
    }

    with open(
        ADJUSTED_PATH,
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
        "\n" + "=" * 60
    )

    print(
        "COST ADJUSTMENT"
    )

    print(
        "=" * 60
    )

    print(
        "\nComparable Vessel:"
    )

    print(
        adjusted_record[
            "comparable_vessel"
        ]
    )

    print(
        "\nComparable Match:"
    )

    print(
        f"{adjusted_record['comparable_match_percentage']}%"
    )

    print(
        "\nObserved Comparable Cost:"
    )

    print(
        f"{adjusted_record['original_cost_million']} "
        f"million "
        f"{adjusted_record['original_currency']}"
    )

    print(
        "\nCost Year:"
    )

    print(
        adjusted_record[
            "cost_year"
        ]
    )

    # ========================================================
    # SPECIFICATION DIFFERENCES
    # ========================================================

    print(
        "\nSpecification Differences:"
    )

    for item in (
        adjusted_record[
            "specification_differences"
        ]
    ):

        if item["available"]:

            print(
                f"  "
                f"{item['specification']}: "
                f"match="
                f"{item['match_percentage']}%, "
                f"difference="
                f"{item['difference_percentage']}%"
            )

        else:

            print(
                f"  "
                f"{item['specification']}: "
                f"Not available"
            )

    # ========================================================
    # SCENARIOS
    # ========================================================

    print(
        "\nScenario Estimates:"
    )

    print(
        "  Low:"
    )

    print(
        f"    Adjustment: "
        f"{adjusted_record['low_scenario']['adjustment_percentage']}%"
    )

    print(
        f"    Cost: "
        f"{adjusted_record['low_scenario']['adjusted_cost_million_myr']} "
        f"million MYR"
    )

    print(
        f"    INR: "
        f"{adjusted_record['low_scenario']['adjusted_cost_million_inr']} "
        f"million INR"
    )

    print(
        "  Base:"
    )

    print(
        f"    Adjustment: "
        f"{adjusted_record['base_scenario']['adjustment_percentage']}%"
    )

    print(
        f"    Cost: "
        f"{adjusted_record['base_scenario']['adjusted_cost_million_myr']} "
        f"million MYR"
    )

    print(
        f"    INR: "
        f"{adjusted_record['base_scenario']['adjusted_cost_million_inr']} "
        f"million INR"
    )

    print(
        "  High:"
    )

    print(
        f"    Adjustment: "
        f"{adjusted_record['high_scenario']['adjustment_percentage']}%"
    )

    print(
        f"    Cost: "
        f"{adjusted_record['high_scenario']['adjusted_cost_million_myr']} "
        f"million MYR"
    )

    print(
        f"    INR: "
        f"{adjusted_record['high_scenario']['adjusted_cost_million_inr']} "
        f"million INR"
    )

    # ========================================================
    # METHODOLOGY
    # ========================================================

    print(
        "\nMethod:"
    )

    print(
        adjusted_record[
            "methodology"
        ]
    )

    print(
        "\nWARNING:"
    )

    print(
        adjusted_record[
            "prototype_warning"
        ]
    )

    print(
        "\nSaved adjusted cost to:"
    )

    print(
        ADJUSTED_PATH
    )


if __name__ == "__main__":
    main()