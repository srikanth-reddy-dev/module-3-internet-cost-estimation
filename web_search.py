import json
import sys

from ddgs import DDGS


PROFILE_PATH = "data/output/vessel_profile.json"
RESULTS_PATH = "data/output/search_results.json"


def configure_console_encoding():
    """
    Make Windows console output UTF-8 safe.

    Search results can contain Unicode characters that
    Windows cp1252 cannot print. Using UTF-8 with
    errors='replace' prevents the pipeline from stopping
    because of a single unusual character.
    """

    try:

        if hasattr(
            sys.stdout,
            "reconfigure"
        ):

            sys.stdout.reconfigure(
                encoding="utf-8",
                errors="replace"
            )

        if hasattr(
            sys.stderr,
            "reconfigure"
        ):

            sys.stderr.reconfigure(
                encoding="utf-8",
                errors="replace"
            )

    except Exception:

        # Console configuration should never stop
        # the actual web-search pipeline.
        pass


def load_vessel_profile():

    with open(
        PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def search_web(
    query,
    max_results=10
):

    results = []

    try:

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                max_results=max_results
            )

            for result in search_results:

                title = result.get(
                    "title"
                )

                url = result.get(
                    "href"
                )

                snippet = result.get(
                    "body"
                )

                if not title or not url:

                    continue

                results.append({

                    "title":
                        title,

                    "url":
                        url,

                    "snippet":
                        snippet
                })

    except Exception as error:

        print(
            f"\nSearch failed for query:\n"
            f"{query}\n"
            f"Error: {error}"
        )

    return results


def build_search_queries(
    vessel
):

    vessel_name = (
        vessel.get(
            "vessel_name"
        )
        or ""
    )

    vessel_type = (
        vessel.get(
            "vessel_type"
        )
        or ""
    )

    loa = vessel.get(
        "length_overall_m"
    )

    breadth = vessel.get(
        "breadth_m"
    )

    dwt = vessel.get(
        "deadweight_t"
    )

    speed = vessel.get(
        "service_speed_knots"
    )

    queries = [

        # =====================================================
        # INPUT VESSEL
        # =====================================================

        f'"{vessel_name}" vessel',

        f'"{vessel_type}" vessel',

        f'"buoy maintenance vessel" "{loa} m" vessel',

        f'"buoy maintenance vessel" "{dwt} t" vessel',


        # =====================================================
        # TECHNICAL COMPARABLE SEARCH
        # =====================================================

        f'"buoy maintenance vessel" '
        f'"{loa} m" '
        f'"{breadth} m"',

        f'"buoy maintenance vessel" '
        f'"{loa} m" '
        f'"{dwt} t"',

        f'"91m" vessel '
        f'"1450" DWT',

        f'"91 metre" '
        f'maintenance vessel',


        # =====================================================
        # NEWBUILD / CONTRACT SEARCH
        # =====================================================

        f'"buoy maintenance vessel" '
        f'newbuilding contract',

        f'"buoy maintenance vessel" '
        f'newbuild price',

        f'"buoy maintenance vessel" '
        f'contract value',

        f'"buoy maintenance vessel" '
        f'purchase price',


        # =====================================================
        # IMPORTANT 91M MAINTENANCE VESSEL COMPARABLE
        # =====================================================

        f'"91M Maintenance/Work Vessel"',

        f'"91M Maintenance/Work Vessel" '
        f'"purchase consideration"',

        f'"91M Maintenance/Work Vessel" '
        f'"contract value"',

        f'"91M Maintenance/Work Vessel" '
        f'"purchase price"',

        f'"91M Maintenance/Work Vessel" '
        f'"RM117,696,000"',

        f'"91M Maintenance/Work Vessel" '
        f'"RM117"',

        f'"91M Maintenance/Work Vessel" '
        f'"Shin Yang"',

        f'"91M Maintenance/Work Vessel" '
        f'"DESB Marine Services"',


        # =====================================================
        # COMPANY / SHIPYARD SEARCH
        # =====================================================

        f'"Shin Yang Shipyard" '
        f'"91M" vessel',

        f'"Shin Yang" '
        f'"91m" '
        f'maintenance vessel',

        f'"DESB Marine Services" '
        f'"91M" vessel',

        f'"Dayang Enterprise" '
        f'"91m" maintenance vessel',


        # =====================================================
        # OFFICIAL SOURCE SEARCH
        # =====================================================

        'site:shinyanggroup.com.my '
        '"91M" '
        '"Maintenance" '
        '"Work Vessel"',

        'site:shinyanggroup.com.my '
        '"91M Maintenance/Work Vessel"',

        'site:shinyanggroup.com.my '
        '"RM117,696,000"',

        'site:shinyanggroup.com.my '
        '"DESB Marine Services"',


        # =====================================================
        # COST + SPECIFICATION SEARCH
        # =====================================================

        f'"91m" '
        f'maintenance vessel '
        f'newbuild price',

        f'"91m" '
        f'maintenance vessel '
        f'contract price',

        f'"91m" '
        f'maintenance vessel '
        f'purchase consideration',

        f'"91m" '
        f'maintenance vessel '
        f'USD million',

        f'"91m" '
        f'maintenance vessel '
        f'cost'
    ]

    return queries


def deduplicate_results(
    results
):

    unique_results = []

    seen_urls = set()

    for result in results:

        url = result.get(
            "url"
        )

        if not url:

            continue

        if url in seen_urls:

            continue

        seen_urls.add(
            url
        )

        unique_results.append(
            result
        )

    return unique_results


def rank_results(
    results
):

    """
    Put potentially useful vessel/cost sources first.

    This does NOT verify the source.
    Source verification is handled by
    source_verifier.py.
    """

    high_priority_keywords = [

        "shinyanggroup.com.my",

        "shinyang",

        "desb",

        "dayang",

        "maintenance vessel",

        "work vessel",

        "newbuild",

        "newbuilding",

        "contract",

        "purchase"
    ]

    def score(
        result
    ):

        text = (

            f"{result.get('title', '')} "

            f"{result.get('url', '')} "

            f"{result.get('snippet', '')}"

        ).lower()

        score_value = 0

        for keyword in (
            high_priority_keywords
        ):

            if keyword in text:

                score_value += 1

        # ----------------------------------------------------
        # Strong priority for official company source
        # ----------------------------------------------------

        if (
            "shinyanggroup.com.my"
            in text
        ):

            score_value += 10

        # ----------------------------------------------------
        # Priority for explicit cost language
        # ----------------------------------------------------

        for keyword in [

            "rm117,696,000",

            "purchase consideration",

            "contract value",

            "contract price",

            "purchase price"

        ]:

            if keyword in text:

                score_value += 5

        return score_value

    return sorted(

        results,

        key=score,

        reverse=True
    )


def main():

    # ========================================================
    # CONFIGURE CONSOLE
    # ========================================================

    configure_console_encoding()

    # ========================================================
    # LOAD PROFILE
    # ========================================================

    vessel = load_vessel_profile()

    # ========================================================
    # BUILD QUERIES
    # ========================================================

    queries = build_search_queries(
        vessel
    )

    all_results = []

    # ========================================================
    # WEB RESEARCH
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "WEB RESEARCH"
    )

    print(
        "=" * 60
    )

    for index, query in enumerate(
        queries,
        start=1
    ):

        print(
            "\n" + "-" * 60
        )

        print(
            f"SEARCH {index}"
        )

        print(
            "-" * 60
        )

        print(
            f"Query:\n{query}"
        )

        results = search_web(
            query,
            max_results=10
        )

        print(
            f"Results returned: "
            f"{len(results)}"
        )

        for result in results:

            print(
                f"\nTitle: "
                f"{result['title']}"
            )

            print(
                f"URL: "
                f"{result['url']}"
            )

            print(
                f"Snippet: "
                f"{result['snippet']}"
            )

        all_results.extend(
            results
        )

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    all_results = deduplicate_results(
        all_results
    )

    # ========================================================
    # RANK RESULTS
    # ========================================================

    all_results = rank_results(
        all_results
    )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    output = {

        "vessel_profile":
            vessel,

        "queries":
            queries,

        "results":
            all_results
    }

    with open(
        RESULTS_PATH,
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
        f"Total unique search results: "
        f"{len(all_results)}"
    )

    print(
        f"Saved to: "
        f"{RESULTS_PATH}"
    )

    print(
        "=" * 60
    )

    # ========================================================
    # TOP RESULTS
    # ========================================================

    print(
        "\nTOP SEARCH RESULTS:"
    )

    for index, result in enumerate(
        all_results[:15],
        start=1
    ):

        print(
            f"\n{index}. "
            f"{result['title']}"
        )

        print(
            f"   {result['url']}"
        )


if __name__ == "__main__":

    main()