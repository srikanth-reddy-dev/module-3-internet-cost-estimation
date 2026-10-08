import json


PROFILE_PATH = "data/output/vessel_profile.json"
COMPARABLES_PATH = "data/output/comparable_vessels.json"
COST_EVIDENCE_PATH = "data/output/cost_evidence.json"
MATCH_PATH = "data/output/spec_matches.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_match_percentage(input_value, comparable_value):
    """
    Calculate percentage similarity.

    Example:
        Target = 91.0
        Comparable = 91.2

    Result is close to 100%.
    """

    if input_value is None or comparable_value is None:
        return None

    if input_value == 0:
        return 100.0 if comparable_value == 0 else 0.0

    percentage = (
        1
        - abs(input_value - comparable_value)
        / abs(input_value)
    ) * 100

    return round(
        max(0, percentage),
        2
    )


def compare_text(input_value, comparable_value):
    """
    Compare two text specifications.
    """

    if not input_value or not comparable_value:
        return "Not available"

    input_text = str(
        input_value
    ).strip().lower()

    comparable_text = str(
        comparable_value
    ).strip().lower()

    if input_text == comparable_text:
        return "Exact"

    if input_text in comparable_text:
        return "Close"

    if comparable_text in input_text:
        return "Close"

    return "No match"


def add_numeric_match(
    matches,
    specification,
    input_value,
    comparable_value
):
    """
    Add a numeric specification comparison.
    """

    percentage = calculate_match_percentage(
        input_value,
        comparable_value
    )

    matches.append({
        "specification": specification,
        "input": input_value,
        "internet": comparable_value,
        "match_percentage": percentage
    })


def calculate_overall_match(matches):
    """
    Calculate the average of only the available
    numeric specification matches.

    Missing specifications are NOT treated as 0%.
    """

    percentages = []

    for match in matches:

        percentage = match.get(
            "match_percentage"
        )

        if percentage is not None:
            percentages.append(
                percentage
            )

    if not percentages:
        return None

    return round(
        sum(percentages) / len(percentages),
        2
    )


def get_shin_yang_cost_evidence(
    cost_evidence
):
    """
    Find the strongest verified Shin Yang / Dayang
    91M maintenance/work vessel cost evidence.
    """

    candidates = []

    for evidence in cost_evidence:

        title = str(
            evidence.get(
                "source_title"
            ) or ""
        ).lower()

        url = str(
            evidence.get(
                "source_url"
            ) or ""
        ).lower()

        cost = evidence.get(
            "reported_cost"
        )

        score = 0

        # Official Shin Yang source
        if "shinyanggroup.com.my" in url:
            score += 100

        # 91M maintenance vessel
        if "91m maintenance" in title:
            score += 50

        # Shin Yang
        if "shin yang" in title:
            score += 20

        # Dayang
        if "dayang" in title:
            score += 20

        # Main reported cost
        if cost == 117700000:
            score += 40

        if cost == 117696000:
            score += 50

        # 2026 transaction
        if evidence.get("year") == 2026:
            score += 10

        candidates.append(
            (
                score,
                evidence
            )
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return candidates[0][1]


def build_shin_yang_comparable(
    cost_evidence
):
    """
    Create the Shin Yang / Dayang comparable.

    The technical particulars below come from the
    verified 91M vessel source used during the research.

    They are kept separate from the generic
    cost_evidence extraction because the cost source
    preview did not reliably expose all particulars.
    """

    evidence = get_shin_yang_cost_evidence(
        cost_evidence
    )

    if evidence is None:
        return None

    return {
        "vessel_name": (
            "91M Maintenance/Work Vessel "
            "(Shin Yang / Dayang)"
        ),

        "source": evidence.get(
            "source_url"
        ),

        "design": (
            "91M Maintenance/Work Vessel"
        ),

        "vessel_type": (
            "Maintenance/Work Vessel"
        ),

        "length_overall_m": 91.20,

        "breadth_m": 23.60,

        "depth_m": 7.50,

        "deadweight_t": None,

        "service_speed_knots": None,

        "deck_area_m2": None,

        "draft_designed_m": 5.00,

        "draft_max_m": 5.50,

        "cost_evidence": {
            "reported_cost": evidence.get(
                "reported_cost"
            ),

            "currency": evidence.get(
                "currency"
            ),

            "raw_cost_text": evidence.get(
                "raw_cost_text"
            ),

            "amount_type": evidence.get(
                "amount_type"
            ),

            "year": evidence.get(
                "year"
            ),

            "source_title": evidence.get(
                "source_title"
            ),

            "source_url": evidence.get(
                "source_url"
            )
        }
    }


def match_vessel(
    input_vessel,
    comparable
):
    """
    Compare the target vessel against one comparable.
    """

    matches = []

    # =====================================================
    # DESIGN
    # =====================================================

    matches.append({
        "specification": "Design",
        "input": input_vessel.get(
            "design"
        ),
        "internet": comparable.get(
            "design"
        ),
        "match": compare_text(
            input_vessel.get("design"),
            comparable.get("design")
        )
    })

    # =====================================================
    # VESSEL TYPE
    # =====================================================

    matches.append({
        "specification": "Vessel Type",
        "input": input_vessel.get(
            "vessel_type"
        ),
        "internet": comparable.get(
            "vessel_type"
        ),
        "match": compare_text(
            input_vessel.get("vessel_type"),
            comparable.get("vessel_type")
        )
    })

    # =====================================================
    # LOA
    # =====================================================

    add_numeric_match(
        matches,
        "LOA",
        input_vessel.get(
            "length_overall_m"
        ),
        comparable.get(
            "length_overall_m"
        )
    )

    # =====================================================
    # BREADTH
    # =====================================================

    add_numeric_match(
        matches,
        "Breadth",
        input_vessel.get(
            "breadth_m"
        ),
        comparable.get(
            "breadth_m"
        )
    )

    # =====================================================
    # DEPTH
    # =====================================================

    add_numeric_match(
        matches,
        "Depth",
        input_vessel.get(
            "depth_m"
        ),
        comparable.get(
            "depth_m"
        )
    )

    # =====================================================
    # DWT
    # =====================================================

    add_numeric_match(
        matches,
        "DWT",
        input_vessel.get(
            "deadweight_t"
        ),
        comparable.get(
            "deadweight_t"
        )
    )

    # =====================================================
    # SERVICE SPEED
    # =====================================================

    add_numeric_match(
        matches,
        "Service Speed",
        input_vessel.get(
            "service_speed_knots"
        ),
        comparable.get(
            "service_speed_knots"
        )
    )

    # =====================================================
    # DECK AREA
    # =====================================================

    add_numeric_match(
        matches,
        "Deck Area",
        input_vessel.get(
            "deck_area_m2"
        ),
        comparable.get(
            "deck_area_m2"
        )
    )

    # =====================================================
    # DESIGN DRAFT
    # =====================================================

    add_numeric_match(
        matches,
        "Design Draft",
        input_vessel.get(
            "design_draft_m"
        ),
        comparable.get(
            "draft_designed_m"
        )
    )

    # =====================================================
    # MAX DRAFT
    # =====================================================

    target_max_draft = input_vessel.get(
        "design_draft_m"
    )

    comparable_max_draft = comparable.get(
        "draft_max_m"
    )

    add_numeric_match(
        matches,
        "Maximum Draft",
        target_max_draft,
        comparable_max_draft
    )

    # =====================================================
    # OVERALL SCORE
    # =====================================================

    overall_score = calculate_overall_match(
        matches
    )

    return {
        "vessel_name": comparable.get(
            "vessel_name"
        ),

        "source": comparable.get(
            "source"
        ),

        "overall_match_percentage": (
            overall_score
        ),

        "matches": matches,

        "cost_evidence": comparable.get(
            "cost_evidence"
        )
    }


def main():

    # =====================================================
    # LOAD TARGET VESSEL
    # =====================================================

    input_vessel = load_json(
        PROFILE_PATH
    )

    # =====================================================
    # LOAD EXISTING TECHNICAL COMPARABLES
    # =====================================================

    comparables = load_json(
        COMPARABLES_PATH
    )

    # =====================================================
    # LOAD COST EVIDENCE
    # =====================================================

    cost_data = load_json(
        COST_EVIDENCE_PATH
    )

    cost_evidence = cost_data.get(
        "cost_evidence",
        []
    )

    # =====================================================
    # BUILD SHIN YANG COMPARABLE
    # =====================================================

    shin_yang_comparable = (
        build_shin_yang_comparable(
            cost_evidence
        )
    )

    # =====================================================
    # MATCH EXISTING COMPARABLES
    # =====================================================

    results = []

    for comparable in comparables:

        result = match_vessel(
            input_vessel,
            comparable
        )

        results.append(
            result
        )

    # =====================================================
    # MATCH SHIN YANG COST COMPARABLE
    # =====================================================

    if shin_yang_comparable:

        shin_yang_result = match_vessel(
            input_vessel,
            shin_yang_comparable
        )

        results.append(
            shin_yang_result
        )

    # =====================================================
    # SORT
    # =====================================================

    def sort_key(result):

        score = result.get(
            "overall_match_percentage"
        )

        if score is None:
            return -1

        return score

    results.sort(
        key=sort_key,
        reverse=True
    )

    # =====================================================
    # SAVE JSON
    # =====================================================

    with open(
        MATCH_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved specification matches to: "
        f"{MATCH_PATH}"
    )

    # =====================================================
    # PRINT RESULTS
    # =====================================================

    for result in results:

        print(
            f"\n{result['vessel_name']}"
        )

        overall = result.get(
            "overall_match_percentage"
        )

        if overall is None:
            print(
                "Overall Match: "
                "Not available"
            )
        else:
            print(
                f"Overall Match: "
                f"{overall}%"
            )

        for match in result["matches"]:

            if "match_percentage" in match:

                percentage = match.get(
                    "match_percentage"
                )

                if percentage is None:
                    match_result = (
                        "Not available"
                    )
                else:
                    match_result = (
                        f"{percentage}%"
                    )

            else:

                match_result = match.get(
                    "match",
                    "Not available"
                )

            print(
                f"{match['specification']}: "
                f"{match['input']} -> "
                f"{match['internet']} = "
                f"{match_result}"
            )

        # =================================================
        # COST EVIDENCE
        # =================================================

        cost = result.get(
            "cost_evidence"
        )

        if cost:

            print(
                "\nCost Evidence:"
            )

            print(
                f"  Cost: "
                f"{cost.get('raw_cost_text')}"
            )

            print(
                f"  Numeric: "
                f"{cost.get('reported_cost')}"
            )

            print(
                f"  Currency: "
                f"{cost.get('currency')}"
            )

            print(
                f"  Year: "
                f"{cost.get('year')}"
            )

            print(
                f"  Source: "
                f"{cost.get('source_title')}"
            )


if __name__ == "__main__":
    main()