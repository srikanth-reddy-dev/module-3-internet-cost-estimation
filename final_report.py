import json

PROFILE_PATH = "data/output/vessel_profile.json"
ANALYSIS_PATH = "data/output/comparable_analysis.json"
ESTIMATE_PATH = "data/output/final_estimate.json"

REPORT_PATH = "data/output/final_report.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_report():
    profile = load_json(PROFILE_PATH)
    analysis = load_json(ANALYSIS_PATH)
    estimate = load_json(ESTIMATE_PATH)

    comparable_vessels = []

    for vessel in analysis:

        specification_matches = []

        for match in vessel.get("specification_matches", []):

            specification_matches.append({
                "specification": match.get("specification"),
                "input": match.get("input"),
                "internet": match.get("internet"),
                "match": match.get("match"),
                "match_percentage": match.get("match_percentage")
            })

        cost = vessel.get("adjusted_cost")

        cost_information = None

        if cost:
            cost_information = {
                "original_cost_min_million_usd":
                    cost.get("original_cost_min_million_usd"),

                "original_cost_max_million_usd":
                    cost.get("original_cost_max_million_usd"),

                "adjusted_cost_min_million_usd":
                    cost.get("adjusted_cost_min_million_usd"),

                "adjusted_cost_max_million_usd":
                    cost.get("adjusted_cost_max_million_usd"),

                "adjusted_cost_midpoint_million_usd":
                    cost.get("adjusted_cost_midpoint_million_usd"),

                "cost_year":
                    cost.get("cost_year"),

                "target_year":
                    cost.get("target_year"),

                "cost_type":
                    cost.get("cost_type"),

                "scope":
                    cost.get("scope"),

                "limitation":
                    cost.get("limitation"),

                "source_title":
                    cost.get("source_title"),

                "source_url":
                    cost.get("source_url")
            }

        comparable_vessels.append({
            "vessel_name": vessel.get("vessel_name"),
            "design": vessel.get("design"),
            "specification_matches": specification_matches,
            "cost_information": cost_information
        })

    report = {
        "input_vessel": {
            "vessel_name": profile.get("vessel_name"),
            "design": profile.get("design"),
            "vessel_type": profile.get("vessel_type"),
            "yard": profile.get("yard"),
            "delivery_year": profile.get("delivery_year"),
            "length_overall_m": profile.get("length_overall_m"),
            "breadth_m": profile.get("breadth_m"),
            "design_draft_m": profile.get("design_draft_m"),
            "deadweight_t": profile.get("deadweight_t"),
            "gross_tonnage": profile.get("gross_tonnage"),
            "net_tonnage": profile.get("net_tonnage"),
            "deck_area_m2": profile.get("deck_area_m2"),
            "service_speed_knots": profile.get("service_speed_knots"),
            "classification": profile.get("classification")
        },

        "vessel_level_estimate": estimate.get("estimate"),

        "currency": estimate.get("currency"),

        "comparable_vessels_used":
            estimate.get("comparable_vessels_used", []),

        "comparables_without_cost":
            estimate.get("comparables_without_cost", []),

        "comparable_vessel_analysis":
            comparable_vessels,

        "assumptions":
            estimate.get("assumptions", [])
    }

    return report


def print_report(report):

    print("\n" + "=" * 70)
    print("FINAL VESSEL COST ESTIMATION REPORT")
    print("=" * 70)

    vessel = report["input_vessel"]

    print("\nINPUT VESSEL")
    print("-" * 70)

    print("Vessel Name:", vessel.get("vessel_name"))
    print("Design:", vessel.get("design"))
    print("Vessel Type:", vessel.get("vessel_type"))
    print("LOA:", vessel.get("length_overall_m"), "m")
    print("Breadth:", vessel.get("breadth_m"), "m")
    print("DWT:", vessel.get("deadweight_t"), "t")
    print("Deck Area:", vessel.get("deck_area_m2"), "m2")
    print("Service Speed:", vessel.get("service_speed_knots"), "knots")

    print("\nVESSEL-LEVEL ESTIMATE")
    print("-" * 70)

    estimate = report.get("vessel_level_estimate")

    if estimate:

        print(
            "Estimated Cost Range:",
            estimate.get("min_million_usd"),
            "-",
            estimate.get("max_million_usd"),
            "million USD"
        )

        print(
            "Estimated Midpoint:",
            estimate.get("midpoint_million_usd"),
            "million USD"
        )

    else:
        print("No vessel-level estimate available.")

    print("\nCOMPARABLE VESSELS")
    print("-" * 70)

    for vessel in report["comparable_vessel_analysis"]:

        print("\nVessel:", vessel.get("vessel_name"))
        print("Design:", vessel.get("design"))

        print("Specification Matches:")

        for match in vessel["specification_matches"]:

            specification = match.get("specification")
            input_value = match.get("input")
            internet_value = match.get("internet")

            if match.get("match_percentage") is not None:

                print(
                    f"  {specification}: "
                    f"{input_value} -> {internet_value} "
                    f"= {match.get('match_percentage')}%"
                )

            elif match.get("match") is not None:

                print(
                    f"  {specification}: "
                    f"{input_value} -> {internet_value} "
                    f"= {match.get('match')}"
                )

        cost = vessel.get("cost_information")

        if cost:

            print("Cost Evidence:")

            print(
                "  Original:",
                cost.get("original_cost_min_million_usd"),
                "-",
                cost.get("original_cost_max_million_usd"),
                "million USD"
            )

            print(
                "  Adjusted:",
                cost.get("adjusted_cost_min_million_usd"),
                "-",
                cost.get("adjusted_cost_max_million_usd"),
                "million USD"
            )

            print(
                "  Source:",
                cost.get("source_title")
            )

            print(
                "  URL:",
                cost.get("source_url")
            )

        else:

            print("Cost Evidence: Not available")

    print("\nASSUMPTIONS / LIMITATIONS")
    print("-" * 70)

    for assumption in report["assumptions"]:
        print("-", assumption)


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
        f"Saved final report to: {REPORT_PATH}"
    )

    print_report(report)