import json


PROFILE_PATH = "data/output/vessel_profile.json"
ANALYSIS_PATH = "data/output/comparable_analysis.json"
ESTIMATE_PATH = "data/output/final_estimate.json"

REPORT_PATH = "data/output/final_report.json"


def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def build_comparable_vessel(
    vessel
):
    """
    Build a clean comparable-vessel section
    for the final report.
    """

    specification_matches = []

    for match in vessel.get(
        "specification_matches",
        []
    ):

        specification_matches.append({

            "specification":
                match.get(
                    "specification"
                ),

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
                match.get(
                    "match_percentage"
                ),

            "available":
                match.get(
                    "available"
                )
        })

    cost = vessel.get(
        "cost_evidence"
    )

    cost_information = None

    if cost:

        cost_information = {

            # ----------------------------------------------
            # Original observed cost
            # ----------------------------------------------

            "original_cost":
                cost.get(
                    "original_cost"
                ),

            "original_currency":
                cost.get(
                    "original_currency"
                ),

            "original_cost_million":
                cost.get(
                    "original_cost_million"
                ),

            "cost_year":
                cost.get(
                    "cost_year"
                ),

            # ----------------------------------------------
            # Scenario costs
            # ----------------------------------------------

            "low_scenario":
                cost.get(
                    "low_scenario"
                ),

            "base_scenario":
                cost.get(
                    "base_scenario"
                ),

            "high_scenario":
                cost.get(
                    "high_scenario"
                ),

            # ----------------------------------------------
            # Currency conversion
            # ----------------------------------------------

            "myr_to_inr":
                cost.get(
                    "myr_to_inr"
                ),

            "target_country":
                cost.get(
                    "target_country"
                ),

            "target_currency":
                cost.get(
                    "target_currency"
                ),

            # ----------------------------------------------
            # Source
            # ----------------------------------------------

            "source_title":
                cost.get(
                    "source_title"
                ),

            "source_url":
                cost.get(
                    "source_url"
                ),

            # ----------------------------------------------
            # Methodology
            # ----------------------------------------------

            "methodology":
                cost.get(
                    "methodology"
                ),

            "prototype_warning":
                cost.get(
                    "prototype_warning"
                )
        }

    return {

        "vessel_name":
            vessel.get(
                "vessel_name"
            ),

        "design":
            vessel.get(
                "design"
            ),

        "is_primary_comparable":
            vessel.get(
                "is_primary_comparable"
            ),

        "overall_match_percentage":
            vessel.get(
                "overall_match_percentage"
            ),

        "available_specification_average":
            vessel.get(
                "available_specification_average"
            ),

        "specification_matches":
            specification_matches,

        "cost_information":
            cost_information
    }


def build_report():

    profile = load_json(
        PROFILE_PATH
    )

    analysis_data = load_json(
        ANALYSIS_PATH
    )

    estimate = load_json(
        ESTIMATE_PATH
    )

    # ========================================================
    # COMPARABLE VESSELS
    # ========================================================

    comparable_vessels = []

    for vessel in analysis_data.get(
        "analysis",
        []
    ):

        comparable_vessels.append(
            build_comparable_vessel(
                vessel
            )
        )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    report = {

        # ----------------------------------------------------
        # Report metadata
        # ----------------------------------------------------

        "report_title":
            "Final Vessel Cost Estimation Report",

        "methodology":
            (
                "Comparable-vessel cost estimation "
                "using verified cost evidence, "
                "specification matching, and "
                "scenario-based cost adjustment."
            ),

        # ----------------------------------------------------
        # Input vessel
        # ----------------------------------------------------

        "input_vessel": {

            "vessel_name":
                profile.get(
                    "vessel_name"
                ),

            "design":
                profile.get(
                    "design"
                ),

            "vessel_type":
                profile.get(
                    "vessel_type"
                ),

            "yard":
                profile.get(
                    "yard"
                ),

            "delivery_year":
                profile.get(
                    "delivery_year"
                ),

            "length_overall_m":
                profile.get(
                    "length_overall_m"
                ),

            "breadth_m":
                profile.get(
                    "breadth_m"
                ),

            "depth_m":
                profile.get(
                    "depth_m"
                ),

            "design_draft_m":
                profile.get(
                    "design_draft_m"
                ),

            "deadweight_t":
                profile.get(
                    "deadweight_t"
                ),

            "gross_tonnage":
                profile.get(
                    "gross_tonnage"
                ),

            "net_tonnage":
                profile.get(
                    "net_tonnage"
                ),

            "deck_area_m2":
                profile.get(
                    "deck_area_m2"
                ),

            "service_speed_knots":
                profile.get(
                    "service_speed_knots"
                ),

            "propulsion":
                profile.get(
                    "propulsion"
                ),

            "propulsion_motor":
                profile.get(
                    "propulsion_motor"
                ),

            "main_generator":
                profile.get(
                    "main_generator"
                ),

            "tunnel_thrusters":
                profile.get(
                    "tunnel_thrusters"
                ),

            "fresh_water_m3":
                profile.get(
                    "fresh_water_m3"
                ),

            "fuel_oil_m3":
                profile.get(
                    "fuel_oil_m3"
                ),

            "water_ballast_m3":
                profile.get(
                    "water_ballast_m3"
                ),

            "cargo_hold_m3":
                profile.get(
                    "cargo_hold_m3"
                ),

            "classification":
                profile.get(
                    "classification"
                )
        },

        # ----------------------------------------------------
        # Vessel-level estimate
        # ----------------------------------------------------

        "vessel_level_estimate":
            estimate.get(
                "estimate"
            ),

        "currency":
            estimate.get(
                "currency"
            ),

        "target_currency":
            estimate.get(
                "target_currency"
            ),

        # ----------------------------------------------------
        # Comparable vessels
        # ----------------------------------------------------

        "comparable_vessels_used":
            estimate.get(
                "comparable_vessels_used",
                []
            ),

        "comparables_without_cost":
            estimate.get(
                "comparables_without_cost",
                []
            ),

        "cost_bearing_comparable_count":
            estimate.get(
                "cost_bearing_comparable_count",
                0
            ),

        # ----------------------------------------------------
        # Detailed comparable analysis
        # ----------------------------------------------------

        "comparable_vessel_analysis":
            comparable_vessels,

        # ----------------------------------------------------
        # Assumptions
        # ----------------------------------------------------

        "assumptions":
            estimate.get(
                "assumptions",
                []
            )
    }

    return report


def print_report(
    report
):

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL VESSEL COST ESTIMATION REPORT"
    )

    print(
        "=" * 70
    )

    # ========================================================
    # INPUT VESSEL
    # ========================================================

    vessel = report[
        "input_vessel"
    ]

    print(
        "\nINPUT VESSEL"
    )

    print(
        "-" * 70
    )

    print(
        "Vessel Name:",
        vessel.get(
            "vessel_name"
        )
    )

    print(
        "Design:",
        vessel.get(
            "design"
        )
    )

    print(
        "Vessel Type:",
        vessel.get(
            "vessel_type"
        )
    )

    print(
        "LOA:",
        vessel.get(
            "length_overall_m"
        ),
        "m"
    )

    print(
        "Breadth:",
        vessel.get(
            "breadth_m"
        ),
        "m"
    )

    print(
        "Depth:",
        vessel.get(
            "depth_m"
        ),
        "m"
    )

    print(
        "Design Draft:",
        vessel.get(
            "design_draft_m"
        ),
        "m"
    )

    print(
        "DWT:",
        vessel.get(
            "deadweight_t"
        ),
        "t"
    )

    print(
        "Deck Area:",
        vessel.get(
            "deck_area_m2"
        ),
        "m2"
    )

    print(
        "Service Speed:",
        vessel.get(
            "service_speed_knots"
        ),
        "knots"
    )

    print(
        "Propulsion:",
        vessel.get(
            "propulsion"
        )
    )

    # ========================================================
    # VESSEL-LEVEL ESTIMATE
    # ========================================================

    print(
        "\nVESSEL-LEVEL ESTIMATE"
    )

    print(
        "-" * 70
    )

    estimate = report.get(
        "vessel_level_estimate"
    )

    if estimate:

        low = estimate.get(
            "low"
        )

        base = estimate.get(
            "base"
        )

        high = estimate.get(
            "high"
        )

        # ----------------------------------------------------
        # LOW
        # ----------------------------------------------------

        print(
            "\nLow Scenario:"
        )

        print(
            "  Cost:",
            low.get(
                "million_myr"
            ),
            "million MYR"
        )

        print(
            "  INR:",
            low.get(
                "million_inr"
            ),
            "million INR"
        )

        print(
            "  INR:",
            low.get(
                "crore_inr"
            ),
            "crore"
        )

        # ----------------------------------------------------
        # BASE
        # ----------------------------------------------------

        print(
            "\nBase Scenario:"
        )

        print(
            "  Cost:",
            base.get(
                "million_myr"
            ),
            "million MYR"
        )

        print(
            "  INR:",
            base.get(
                "million_inr"
            ),
            "million INR"
        )

        print(
            "  INR:",
            base.get(
                "crore_inr"
            ),
            "crore"
        )

        # ----------------------------------------------------
        # HIGH
        # ----------------------------------------------------

        print(
            "\nHigh Scenario:"
        )

        print(
            "  Cost:",
            high.get(
                "million_myr"
            ),
            "million MYR"
        )

        print(
            "  INR:",
            high.get(
                "million_inr"
            ),
            "million INR"
        )

        print(
            "  INR:",
            high.get(
                "crore_inr"
            ),
            "crore"
        )

    else:

        print(
            "No vessel-level estimate available."
        )

    # ========================================================
    # COMPARABLE VESSELS
    # ========================================================

    print(
        "\nCOMPARABLE VESSELS"
    )

    print(
        "-" * 70
    )

    for vessel in report[
        "comparable_vessel_analysis"
    ]:

        print(
            "\nVessel:",
            vessel.get(
                "vessel_name"
            )
        )

        print(
            "Design:",
            vessel.get(
                "design"
            )
        )

        print(
            "Primary Comparable:",
            vessel.get(
                "is_primary_comparable"
            )
        )

        print(
            "Overall Match:",
            vessel.get(
                "overall_match_percentage"
            ),
            "%"
        )

        print(
            "Specification Matches:"
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

            if percentage is not None:

                print(
                    f"  {specification}: "
                    f"{input_value} -> "
                    f"{internet_value} "
                    f"= {percentage}%"
                )

            elif match.get(
                "match"
            ) is not None:

                print(
                    f"  {specification}: "
                    f"{input_value} -> "
                    f"{internet_value} "
                    f"= {match.get('match')}"
                )

            else:

                print(
                    f"  {specification}: "
                    f"{input_value} -> "
                    f"{internet_value} "
                    "= Not available"
                )

        # ====================================================
        # COST INFORMATION
        # ====================================================

        cost = vessel.get(
            "cost_information"
        )

        if cost:

            print(
                "\nCost Evidence:"
            )

            print(
                "  Original:",
                cost.get(
                    "original_cost_million"
                ),
                "million",
                cost.get(
                    "original_currency"
                )
            )

            print(
                "  Cost Year:",
                cost.get(
                    "cost_year"
                )
            )

            low = cost.get(
                "low_scenario"
            )

            base = cost.get(
                "base_scenario"
            )

            high = cost.get(
                "high_scenario"
            )

            if low:

                print(
                    "  Low:",
                    low.get(
                        "adjusted_cost_million_myr"
                    ),
                    "million MYR"
                )

            if base:

                print(
                    "  Base:",
                    base.get(
                        "adjusted_cost_million_myr"
                    ),
                    "million MYR"
                )

            if high:

                print(
                    "  High:",
                    high.get(
                        "adjusted_cost_million_myr"
                    ),
                    "million MYR"
                )

            print(
                "  Source:",
                cost.get(
                    "source_title"
                )
            )

            print(
                "  URL:",
                cost.get(
                    "source_url"
                )
            )

        else:

            print(
                "\nCost Evidence: Not available"
            )

    # ========================================================
    # COMPARABLE SUMMARY
    # ========================================================

    print(
        "\nCOMPARABLE SUMMARY"
    )

    print(
        "-" * 70
    )

    print(
        "Cost-bearing comparables:",
        report.get(
            "cost_bearing_comparable_count"
        )
    )

    print(
        "Used:"
    )

    for vessel in report.get(
        "comparable_vessels_used",
        []
    ):

        print(
            "  -",
            vessel
        )

    print(
        "Without cost evidence:"
    )

    for vessel in report.get(
        "comparables_without_cost",
        []
    ):

        print(
            "  -",
            vessel
        )

    # ========================================================
    # ASSUMPTIONS
    # ========================================================

    print(
        "\nASSUMPTIONS / LIMITATIONS"
    )

    print(
        "-" * 70
    )

    for assumption in report[
        "assumptions"
    ]:

        print(
            "-",
            assumption
        )

    print(
        "\n" + "=" * 70
    )


if __name__ == "__main__":

    report = build_report()

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved final report to: "
        f"{REPORT_PATH}"
    )

    print_report(
        report
    )