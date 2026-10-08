import json
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from pypdf import PdfReader


RESULTS_PATH = "data/output/search_results.json"
VERIFIED_PATH = "data/output/verified_sources.json"


def load_search_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("results", [])


def extract_pdf_text(content):
    """
    Extract text from a PDF response.
    """

    reader = PdfReader(BytesIO(content))

    pages = []

    for page in reader.pages:

        try:
            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)

        except Exception:
            continue

    return "\n".join(pages)


def extract_html_text(content):
    """
    Extract readable text from an HTML page.
    """

    soup = BeautifulSoup(
        content,
        "html.parser"
    )

    # Remove non-content elements.
    for element in soup(
        ["script", "style", "noscript"]
    ):
        element.decompose()

    title = (
        soup.title.get_text(strip=True)
        if soup.title
        else None
    )

    text = soup.get_text(
        " ",
        strip=True
    )

    return title, text


def verify_source(url):

    result = {
        "verified": False,
        "status_code": None,
        "content_type": None,
        "title": None,
        "text_preview": None,
        "error": None
    }

    try:

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/154.0.0.0 "
                    "Safari/537.36"
                )
            }
        )

        result["status_code"] = response.status_code

        result["content_type"] = (
            response.headers.get(
                "Content-Type",
                ""
            )
        )

        if response.status_code != 200:

            result["error"] = (
                f"HTTP status "
                f"{response.status_code}"
            )

            return result


        content_type = (
            response.headers
            .get("Content-Type", "")
            .lower()
        )

        clean_url = url.lower().split("?")[0]

        is_pdf = (
            "application/pdf" in content_type
            or clean_url.endswith(".pdf")
        )


        # =====================================================
        # PDF
        # =====================================================

        if is_pdf:

            text = extract_pdf_text(
                response.content
            )

            result["verified"] = True
            result["text_preview"] = text

            return result


        # =====================================================
        # HTML
        # =====================================================

        title, text = extract_html_text(
            response.content
        )

        result["verified"] = True
        result["title"] = title
        result["text_preview"] = text

        return result


    except requests.RequestException as error:

        result["error"] = str(error)

        return result


    except Exception as error:

        result["error"] = str(error)

        return result


def source_priority(result):
    """
    Rank sources so useful official sources appear first.

    This is only ranking.
    It is NOT source truth validation.
    """

    url = str(
        result.get("url") or ""
    ).lower()

    title = str(
        result.get("title") or ""
    ).lower()

    snippet = str(
        result.get("snippet") or ""
    ).lower()

    verification = (
        result.get("verification") or {}
    )

    verified_text = str(
        verification.get(
            "text_preview"
        ) or ""
    ).lower()

    combined = (
        url
        + " "
        + title
        + " "
        + snippet
        + " "
        + verified_text
    )

    score = 0


    # =====================================================
    # OFFICIAL SHIN YANG
    # =====================================================

    if "shinyanggroup.com.my" in url:
        score += 100


    if "shin yang" in combined:
        score += 20


    # =====================================================
    # TARGET VESSEL
    # =====================================================

    if "91m maintenance" in combined:
        score += 20


    if "maintenance/work vessel" in combined:
        score += 20


    if "91m" in combined:
        score += 10


    # =====================================================
    # COST EVIDENCE
    # =====================================================

    if "rm117,696,000" in combined:
        score += 50


    if "rm117.7" in combined:
        score += 30


    if "117.7 million" in combined:
        score += 30


    if "purchase consideration" in combined:
        score += 20


    if "sale and purchase agreement" in combined:
        score += 15


    if "construction, build and sale" in combined:
        score += 10


    # =====================================================
    # SECONDARY RELIABLE SOURCES
    # =====================================================

    if "thestar.com.my" in url:
        score += 15


    if "klsescreener.com" in url:
        score += 10


    return score


def main():

    results = load_search_results()

    verified_results = []


    print("\n" + "=" * 60)
    print("SOURCE VERIFICATION")
    print("=" * 60)


    total = len(results)


    for index, result in enumerate(
        results,
        start=1
    ):

        url = result.get("url")

        if not url:
            continue


        print(
            f"\n[{index}/{total}] "
            f"Checking source..."
        )

        print(
            f"URL: {url}"
        )


        verification = verify_source(
            url
        )


        verified_result = {
            **result,
            "verification": verification
        }


        verified_results.append(
            verified_result
        )


        if verification.get(
            "verified",
            False
        ):
            status = "Verified"
        else:
            status = "Not Verified"


        print(
            f"Status: {status}"
        )


        if verification.get(
            "status_code"
        ):

            print(
                f"HTTP: "
                f"{verification['status_code']}"
            )


        if verification.get(
            "title"
        ):

            print(
                f"Title: "
                f"{verification['title']}"
            )


        if verification.get(
            "error"
        ):

            print(
                f"Error: "
                f"{verification['error']}"
            )


    # =====================================================
    # RANK RESULTS
    # =====================================================

    verified_results.sort(
        key=source_priority,
        reverse=True
    )


    # =====================================================
    # SAVE
    # =====================================================

    with open(
        VERIFIED_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            verified_results,
            file,
            indent=2,
            ensure_ascii=False
        )


    # =====================================================
    # SUMMARY
    # =====================================================

    verified_count = sum(
        1
        for result in verified_results
        if (
            result.get("verification") or {}
        ).get(
            "verified",
            False
        )
    )


    not_verified_count = (
        len(verified_results)
        - verified_count
    )


    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)


    print(
        f"Total sources: "
        f"{len(verified_results)}"
    )

    print(
        f"Verified sources: "
        f"{verified_count}"
    )

    print(
        f"Not verified: "
        f"{not_verified_count}"
    )

    print(
        f"Saved to: "
        f"{VERIFIED_PATH}"
    )


    # =====================================================
    # TOP VERIFIED SOURCES
    # =====================================================

    print("\nTOP VERIFIED SOURCES:")

    shown = 0


    for result in verified_results:

        verification = (
            result.get("verification") or {}
        )

        if not verification.get(
            "verified",
            False
        ):
            continue


        shown += 1


        print(
            f"\n{shown}. "
            f"{result.get('title') or 'Untitled source'}"
        )

        print(
            f"   URL: "
            f"{result.get('url')}"
        )

        print(
            f"   Score: "
            f"{source_priority(result)}"
        )


        if shown >= 10:
            break


if __name__ == "__main__":
    main()