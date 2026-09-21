import json


PROFILE_PATH = "data/output/vessel_profile.json"
COMPARABLES_PATH = "data/output/comparable_vessels.json"
MATCH_PATH = "data/output/spec_matches.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_match_percentage(input_value, internet_value):
    if input_value is None or internet_value is None:
        return None

    if input_value == 0:
        return 100.0 if internet_value == 0 else 0.0

    percentage = (
        1 - abs(input_value - internet_value) / abs(input_value)
    ) * 100

    return round(max(0, percentage), 2)


def compare_numeric(input_value, internet_value, tolerance):
    if input_value is None or internet_value is None:
        return "Not available"

    difference = abs(input_value - internet_value)

    if difference == 0:
        return "Exact"

    if difference <= tolerance:
        return "Close"

    return "No match"


def compare_text(input_value, internet_value):
    if not input_value or not internet_value:
        return "Not available"

    if input_value.strip().lower() == internet_value.strip().lower():
        return "Exact"

    if input_value.lower() in internet_value.lower():
        return "Close"

    if internet_value.lower() in input_value.lower():
        return "Close"

    return "No match"


def match_vessel(input_vessel, comparable):
    matches = []

    matches.append({
        "specification": "Design",
        "input": input_vessel["design"],
        "internet": comparable["design"],
        "match": compare_text(
            input_vessel["design"],
            comparable["design"]
        )
    })

    matches.append({
        "specification": "Vessel Type",
        "input": input_vessel["vessel_type"],
        "internet": comparable["vessel_type"],
        "match": compare_text(
            input_vessel["vessel_type"],
            comparable["vessel_type"]
        )
    })

    loa_percentage = calculate_match_percentage(
        input_vessel["length_overall_m"],
        comparable["length_overall_m"]
    )

    matches.append({
        "specification": "LOA",
        "input": input_vessel["length_overall_m"],
        "internet": comparable["length_overall_m"],
        "match_percentage": loa_percentage
    })

    breadth_percentage = calculate_match_percentage(
        input_vessel["breadth_m"],
        comparable["breadth_m"]
    )

    matches.append({
        "specification": "Breadth",
        "input": input_vessel["breadth_m"],
        "internet": comparable["breadth_m"],
        "match_percentage": breadth_percentage
    })

    dwt_percentage = calculate_match_percentage(
        input_vessel["deadweight_t"],
        comparable["deadweight_t"]
    )

    matches.append({
        "specification": "DWT",
        "input": input_vessel["deadweight_t"],
        "internet": comparable["deadweight_t"],
        "match_percentage": dwt_percentage
    })

    service_speed_percentage = calculate_match_percentage(
        input_vessel["service_speed_knots"],
        comparable["service_speed_knots"]
    )

    matches.append({
        "specification": "Service Speed",
        "input": input_vessel["service_speed_knots"],
        "internet": comparable["service_speed_knots"],
        "match_percentage": service_speed_percentage
    })

    deck_area_percentage = calculate_match_percentage(
        input_vessel["deck_area_m2"],
        comparable["deck_area_m2"]
    )

    matches.append({
        "specification": "Deck Area",
        "input": input_vessel["deck_area_m2"],
        "internet": comparable["deck_area_m2"],
        "match_percentage": deck_area_percentage
    })

    return {
        "vessel_name": comparable["vessel_name"],
        "source": comparable["source"],
        "matches": matches
    }


if __name__ == "__main__":
    input_vessel = load_json(PROFILE_PATH)
    comparables = load_json(COMPARABLES_PATH)

    results = []

    for comparable in comparables:
        result = match_vessel(input_vessel, comparable)
        results.append(result)

    with open(MATCH_PATH, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Saved specification matches to: {MATCH_PATH}")

    for result in results:
        print(f"\n{result['vessel_name']}")

        for match in result["matches"]:
            if "match_percentage" in match:
                if match["match_percentage"] is None:
                    match_result = "Not available"
                else:
                    match_result = f"{match['match_percentage']}%"
            else:
                match_result = match["match"]

            print(
                f"{match['specification']}: "
                f"{match['input']} -> "
                f"{match['internet']} = "
                f"{match_result}"
            )