import json
import re


INPUT_PATH = "data/output/verified_sources.json"
OUTPUT_PATH = "data/output/cost_evidence.json"


# ============================================================
# COST EXTRACTION CONFIGURATION
# ============================================================

# A vessel construction / purchase cost below this value
# is treated as unlikely to represent the vessel-level
# purchase price for this Module 3 research.
#
# This prevents unrelated small amounts such as RM4,000
# from becoming vessel cost evidence.
MIN_VESSEL_COST_MYR = 1_000_000


def load_verified_sources():

    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def clean_text(text):

    if not text:

        return ""

    return re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()


def extract_amounts(text):
    """
    Extract Malaysian Ringgit cost references.

    Supported examples:

        RM117,696,000
        RM117.7 million
        RM117.7mil
        RM118mil
        RM118-million

    Returns all detected monetary references.
    """

    text = clean_text(
        text
    )

    amounts = []

    # ========================================================
    # EXACT RM AMOUNT
    #
    # Example:
    # RM117,696,000
    # ========================================================

    exact_pattern = re.compile(
        r"""
        RM\s*
        (
            [0-9]{1,3}
            (?:,[0-9]{3})+
            (?:\.[0-9]+)?
        )
        """,
        re.IGNORECASE | re.VERBOSE
    )

    for match in exact_pattern.finditer(
        text
    ):

        raw_value = match.group(
            1
        )

        numeric_value = float(
            raw_value.replace(
                ",",
                ""
            )
        )

        amounts.append({

            "raw":
                match.group(0),

            "amount":
                numeric_value,

            "currency":
                "MYR",

            "amount_type":
                "exact"
        })

    # ========================================================
    # RM MILLION / MIL
    #
    # Supports:
    #
    # RM117.7 million
    # RM117.7mil
    # RM118mil
    # RM118-million
    # RM118 million
    # ========================================================

    million_pattern = re.compile(
        r"""
        RM\s*
        (
            [0-9]+
            (?:\.[0-9]+)?
        )
        \s*
        (?:-\s*)?
        (million|mil)
        \b
        """,
        re.IGNORECASE | re.VERBOSE
    )

    for match in million_pattern.finditer(
        text
    ):

        raw_number = match.group(
            1
        )

        numeric_value = (
            float(raw_number)
            * 1_000_000
        )

        amounts.append({

            "raw":
                match.group(0),

            "amount":
                numeric_value,

            "currency":
                "MYR",

            "amount_type":
                "million"
        })

    return amounts


def extract_year(text):
    """
    Extract likely transaction year.

    Prioritizes explicit 2026 references.
    """

    text = clean_text(
        text
    )

    years = re.findall(
        r"\b(20[0-9]{2})\b",
        text
    )

    if not years:

        return None

    # Prefer 2026 because the current
    # comparable transaction occurred
    # in January 2026.

    if "2026" in years:

        return 2026

    return int(
        years[0]
    )


def extract_vessel_particulars(text):
    """
    Extract the main technical particulars of the
    comparable vessel when they are available.
    """

    text = clean_text(
        text
    )

    particulars = {}

    # ========================================================
    # LENGTH OVERALL
    # ========================================================

    length_patterns = [

        r"""
        length\ overall
        \s*
        (?:of|is)?
        \s*
        ([0-9]+(?:\.[0-9]+)?)
        \s*M
        """,

        r"""
        length\ overall
        \s*
        [:\-]?
        \s*
        ([0-9]+(?:\.[0-9]+)?)
        \s*M
        """
    ]

    for pattern in length_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.VERBOSE
        )

        if match:

            particulars[
                "length_overall_m"
            ] = float(
                match.group(1)
            )

            break

    # ========================================================
    # BEAM
    # ========================================================

    beam_patterns = [

        r"""
        beam\ moulded
        \s*
        (?:of|is)?
        \s*
        ([0-9]+(?:\.[0-9]+)?)
        \s*M
        """,

        r"""
        beam\ moulded
        \s*
        [:\-]?
        \s*
        ([0-9]+(?:\.[0-9]+)?)
        \s*M
        """
    ]

    for pattern in beam_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.VERBOSE
        )

        if match:

            particulars[
                "breadth_m"
            ] = float(
                match.group(1)
            )

            break

    # ========================================================
    # DEPTH
    # ========================================================

    depth_patterns = [

        r"""
        depth\ moulded
        \s*
        (?:of|is)?
        \s*
        ([0-9]+(?:\.[0-9]+)?)
        \s*M
        """,

        r"""
        depth\ moulded
        \s*
        [:\-]?
        \s*
        ([0-9]+(?:\.[0-9]+)?)
        \s*M
        """
    ]

    for pattern in depth_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.VERBOSE
        )

        if match:

            particulars[
                "depth_m"
            ] = float(
                match.group(1)
            )

            break

    # ========================================================
    # DRAFT
    # ========================================================

    draft_pattern = re.compile(
        r"""
        draft
        \s*
        (?:designed/max)?
        \s*
        (?:of|is|:)?
        \s*
        ([0-9]+(?:\.[0-9]+)?)
        \s*M
        (?:
            /
            ([0-9]+(?:\.[0-9]+)?)
            \s*M
        )?
        """,
        re.IGNORECASE | re.VERBOSE
    )

    match = draft_pattern.search(
        text
    )

    if match:

        particulars[
            "draft_designed_m"
        ] = float(
            match.group(1)
        )

        if match.group(2):

            particulars[
                "draft_max_m"
            ] = float(
                match.group(2)
            )

    # ========================================================
    # COMPLEMENT
    # ========================================================

    complement_patterns = [

        r"""
        complement
        \s*
        ([0-9]+)
        \s*men
        """,

        r"""
        complement
        \s*
        (?:of|is)?
        \s*
        ([0-9]+)
        """
    ]

    for pattern in complement_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.VERBOSE
        )

        if match:

            particulars[
                "complement"
            ] = int(
                match.group(1)
            )

            break

    return particulars


def is_relevant_source(source):
    """
    Determine whether the source appears relevant
    to the vessel cost research.
    """

    title = clean_text(
        source.get(
            "title"
        )
    ).lower()

    snippet = clean_text(
        source.get(
            "snippet"
        )
    ).lower()

    verification = (
        source.get(
            "verification"
        )
        or {}
    )

    text = clean_text(
        verification.get(
            "text_preview"
        )
    ).lower()

    combined = (
        title
        + " "
        + snippet
        + " "
        + text
    )

    relevant_keywords = [

        "91m maintenance",

        "91m maintenance/work vessel",

        "maintenance work vessel",

        "rm117.7",

        "rm117,696,000",

        "rm118mil",

        "rm118-million",

        "rm118 million",

        "purchase consideration",

        "sale and purchase agreement",

        "dayang",

        "desb",

        "shin yang"
    ]

    matches = [

        keyword

        for keyword in relevant_keywords

        if keyword in combined
    ]

    return matches


def select_best_amount(
    amounts
):
    """
    Select the strongest vessel-cost amount.

    Priority:

    1. Exact amount >= minimum threshold
    2. Million amount >= minimum threshold
    3. Otherwise no usable vessel cost

    Small unrelated amounts such as RM4,000
    are rejected.
    """

    usable_amounts = [

        item

        for item in amounts

        if item.get(
            "amount",
            0
        ) >= MIN_VESSEL_COST_MYR
    ]

    if not usable_amounts:

        return None

    exact_amounts = [

        item

        for item in usable_amounts

        if item.get(
            "amount_type"
        ) == "exact"
    ]

    if exact_amounts:

        # If several exact values exist,
        # choose the first explicit exact value.

        return exact_amounts[0]

    million_amounts = [

        item

        for item in usable_amounts

        if item.get(
            "amount_type"
        ) == "million"
    ]

    if million_amounts:

        return million_amounts[0]

    return usable_amounts[0]


def extract_cost_evidence(
    source
):
    """
    Extract cost information from one verified source.
    """

    verification = (
        source.get(
            "verification"
        )
        or {}
    )

    text = clean_text(
        verification.get(
            "text_preview"
        )
    )

    title = clean_text(
        source.get(
            "title"
        )
    )

    snippet = clean_text(
        source.get(
            "snippet"
        )
    )

    combined_text = (
        title
        + " "
        + snippet
        + " "
        + text
    )

    # ========================================================
    # RELEVANCE
    # ========================================================

    relevant_matches = (
        is_relevant_source(
            source
        )
    )

    if not relevant_matches:

        return None

    # ========================================================
    # COST AMOUNTS
    # ========================================================

    amounts = extract_amounts(
        combined_text
    )

    if not amounts:

        return None

    # ========================================================
    # SELECT USABLE COST
    # ========================================================

    selected_amount = select_best_amount(
        amounts
    )

    if selected_amount is None:

        # This is important:
        # a source containing only something like
        # RM4,000 is not treated as vessel cost evidence.

        return None

    # ========================================================
    # OTHER INFORMATION
    # ========================================================

    year = extract_year(
        combined_text
    )

    particulars = extract_vessel_particulars(
        combined_text
    )

    return {

        "source_title":
            title,

        "source_url":
            source.get(
                "url"
            ),

        "source_snippet":
            snippet,

        "verified":
            verification.get(
                "verified",
                False
            ),

        "reported_cost":
            selected_amount[
                "amount"
            ],

        "currency":
            selected_amount[
                "currency"
            ],

        "raw_cost_text":
            selected_amount[
                "raw"
            ],

        "amount_type":
            selected_amount[
                "amount_type"
            ],

        "year":
            year,

        "vessel_particulars":
            particulars,

        "relevance_matches":
            relevant_matches,

        "all_detected_costs":
            amounts
    }


def main():

    sources = load_verified_sources()

    cost_evidence = []

    print(
        "\n" + "=" * 60
    )

    print(
        "COST EVIDENCE EXTRACTION"
    )

    print(
        "=" * 60
    )

    for index, source in enumerate(
        sources,
        start=1
    ):

        verification = (
            source.get(
                "verification"
            )
            or {}
        )

        if not verification.get(
            "verified",
            False
        ):

            continue

        evidence = extract_cost_evidence(
            source
        )

        if evidence is None:

            continue

        cost_evidence.append(
            evidence
        )

        print(
            "\nCost evidence found:"
        )

        print(
            f"Source: "
            f"{evidence['source_title']}"
        )

        print(
            f"URL: "
            f"{evidence['source_url']}"
        )

        print(
            f"Cost: "
            f"{evidence['raw_cost_text']}"
        )

        print(
            f"Currency: "
            f"{evidence['currency']}"
        )

        print(
            f"Year: "
            f"{evidence['year']}"
        )

    # ========================================================
    # REMOVE DUPLICATE SOURCE + COST COMBINATIONS
    # ========================================================

    unique_evidence = []

    seen = set()

    for evidence in cost_evidence:

        key = (

            evidence.get(
                "source_url"
            ),

            evidence.get(
                "reported_cost"
            ),

            evidence.get(
                "currency"
            )
        )

        if key in seen:

            continue

        seen.add(
            key
        )

        unique_evidence.append(
            evidence
        )

    cost_evidence = unique_evidence

    # ========================================================
    # RANK COST EVIDENCE
    # ========================================================

    def evidence_score(
        item
    ):

        score = 0

        url = str(
            item.get(
                "source_url"
            )
            or ""
        ).lower()

        title = str(
            item.get(
                "source_title"
            )
            or ""
        ).lower()

        matches = (
            item.get(
                "relevance_matches"
            )
            or []
        )

        # ----------------------------------------------------
        # Official company source
        # ----------------------------------------------------

        if (
            "shinyanggroup.com.my"
            in url
        ):

            score += 100

        # ----------------------------------------------------
        # Exact transaction amount
        # ----------------------------------------------------

        if (
            item.get(
                "reported_cost"
            )
            == 117696000
        ):

            score += 50

        # ----------------------------------------------------
        # Strong vessel terminology
        # ----------------------------------------------------

        if (
            "91m maintenance"
            in title
        ):

            score += 30

        # ----------------------------------------------------
        # Transaction terminology
        # ----------------------------------------------------

        if (
            "purchase consideration"
            in matches
        ):

            score += 20

        if (
            "sale and purchase agreement"
            in matches
        ):

            score += 20

        # ----------------------------------------------------
        # Secondary sources
        # ----------------------------------------------------

        if (
            "thestar.com.my"
            in url
        ):

            score += 15

        if (
            "klsescreener.com"
            in url
        ):

            score += 10

        return score

    cost_evidence.sort(
        key=evidence_score,
        reverse=True
    )

    # ========================================================
    # SAVE
    # ========================================================

    output = {

        "cost_evidence":
            cost_evidence,

        "count":
            len(
                cost_evidence
            ),

        "minimum_vessel_cost_myr":
            MIN_VESSEL_COST_MYR
    }

    with open(
        OUTPUT_PATH,
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
    # SUMMARY
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "COST EXTRACTION SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        f"Cost evidence records: "
        f"{len(cost_evidence)}"
    )

    print(
        f"Saved to: "
        f"{OUTPUT_PATH}"
    )

    # ========================================================
    # TOP COST EVIDENCE
    # ========================================================

    print(
        "\nTOP COST EVIDENCE:"
    )

    for index, item in enumerate(
        cost_evidence[:10],
        start=1
    ):

        print(
            f"\n{index}. "
            f"{item['source_title']}"
        )

        print(
            f"   URL: "
            f"{item['source_url']}"
        )

        print(
            f"   Cost: "
            f"{item['raw_cost_text']}"
        )

        print(
            f"   Numeric: "
            f"{item['reported_cost']}"
        )

        print(
            f"   Currency: "
            f"{item['currency']}"
        )

        print(
            f"   Year: "
            f"{item['year']}"
        )

        print(
            f"   Particulars: "
            f"{item['vessel_particulars']}"
        )


if __name__ == "__main__":

    main()