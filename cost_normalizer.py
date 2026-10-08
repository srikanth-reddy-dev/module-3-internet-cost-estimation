import json


COST_PATH = "data/output/cost_evidence.json"
MATCH_PATH = "data/output/spec_matches.json"
NORMALIZED_PATH = "data/output/normalized_costs.json"


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def normalize_cost_evidence(
    cost_evidence
):
    """
    Normalize extracted vessel cost evidence.

    Current source data is primarily in MYR.

    This stage does NOT:
    - convert currencies
    - adjust for inflation
    - adjust for vessel specification differences
    - estimate the target vessel cost

    Those operations belong to later pipeline stages.
    """

    normalized = []

    for source in cost_evidence:

        reported_cost = source.get(
            "reported_cost"
        )

        currency = source.get(
            "currency"
        )

        if reported_cost is None:
            continue

        if not currency:
            continue

        normalized.append({
            "vessel": (
                "91M Maintenance/Work Vessel "
                "(Shin Yang / Dayang)"
            ),

            "reported_cost": reported_cost,

            "currency": currency,

            "cost_million": round(
                reported_cost / 1_000_000,
                4
            ),

            "cost_year": source.get(
                "year"
            ),

            "cost_type": (
                "Reported vessel purchase "
                "consideration"
            ),

            "scope": "Per vessel",

            "amount_type": source.get(
                "amount_type"
            ),

            "raw_cost_text": source.get(
                "raw_cost_text"
            ),

            "source_title": source.get(
                "source_title"
            ),

            "source_url": source.get(
                "source_url"
            ),

            "verified": source.get(
                "verified",
                False
            ),

            "relevance_matches": source.get(
                "relevance_matches",
                []
            )
        })

    return normalized


def select_primary_comparable(
    normalized_costs
):
    """
    Select the strongest cost record.

    Preference is given to:
    1. Official Shin Yang source
    2. Exact 2026 transaction
    3. Main RM117.7M reported value
    """

    if not normalized_costs:
        return None

    def score(item):

        score_value = 0

        url = str(
            item.get(
                "source_url"
            ) or ""
        ).lower()

        title = str(
            item.get(
                "source_title"
            ) or ""
        ).lower()

        if "shinyanggroup.com.my" in url:
            score_value += 100

        if "91m maintenance" in title:
            score_value += 50

        if item.get(
            "reported_cost"
        ) == 117700000:
            score_value += 40

        if item.get(
            "cost_year"
        ) == 2026:
            score_value += 20

        if item.get(
            "currency"
        ) == "MYR":
            score_value += 10

        return score_value

    return max(
        normalized_costs,
        key=score
    )


def build_normalized_output(
    normalized_costs
):
    """
    Build final normalized-cost output.

    The primary comparable is explicitly identified,
    while supporting cost evidence is retained.
    """

    primary = select_primary_comparable(
        normalized_costs
    )

    return {
        "primary_comparable": primary,

        "normalized_costs": normalized_costs,

        "count": len(
            normalized_costs
        ),

        "normalization_notes": [
            (
                "Costs are preserved in the "
                "original reported currency."
            ),
            (
                "No currency conversion is performed "
                "at this stage."
            ),
            (
                "No inflation adjustment is performed "
                "at this stage."
            ),
            (
                "No vessel specification adjustment "
                "is performed at this stage."
            ),
            (
                "The primary comparable is the "
                "verified 2026 Shin Yang / Dayang "
                "91M Maintenance/Work Vessel."
            )
        ]
    }


def main():

    # =====================================================
    # LOAD COST EVIDENCE
    # =====================================================

    cost_data = load_json(
        COST_PATH
    )

    cost_evidence = cost_data.get(
        "cost_evidence",
        []
    )

    # =====================================================
    # NORMALIZE
    # =====================================================

    normalized_costs = (
        normalize_cost_evidence(
            cost_evidence
        )
    )

    # =====================================================
    # BUILD OUTPUT
    # =====================================================

    output = build_normalized_output(
        normalized_costs
    )

    # =====================================================
    # SAVE
    # =====================================================

    with open(
        NORMALIZED_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    # =====================================================
    # PRINT SUMMARY
    # =====================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "COST NORMALIZATION"
    )

    print(
        "=" * 60
    )

    print(
        f"Normalized cost records: "
        f"{len(normalized_costs)}"
    )

    primary = output.get(
        "primary_comparable"
    )

    if primary:

        print(
            "\nPRIMARY COMPARABLE"
        )

        print(
            f"Vessel: "
            f"{primary.get('vessel')}"
        )

        print(
            f"Cost: "
            f"{primary.get('raw_cost_text')}"
        )

        print(
            f"Numeric: "
            f"{primary.get('reported_cost')}"
        )

        print(
            f"Currency: "
            f"{primary.get('currency')}"
        )

        print(
            f"Cost Million: "
            f"{primary.get('cost_million')}"
        )

        print(
            f"Year: "
            f"{primary.get('cost_year')}"
        )

        print(
            f"Type: "
            f"{primary.get('cost_type')}"
        )

        print(
            f"Source: "
            f"{primary.get('source_title')}"
        )

        print(
            f"URL: "
            f"{primary.get('source_url')}"
        )

    print(
        "\nSaved normalized costs to: "
        f"{NORMALIZED_PATH}"
    )


if __name__ == "__main__":
    main()