
import json
import sys
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader


RESULTS_PATH = "data/output/search_results.json"
VERIFIED_PATH = "data/output/verified_sources.json"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.google.com/",
}

SHIN_YANG_HOST = "www.shinyanggroup.com.my"


def configure_console_encoding():
    """Keep Windows console output UTF-8 safe."""
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def load_search_results():
    with open(RESULTS_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data.get("results", [])


def build_url_candidates(url):
    """
    Try the original URL first.

    For the known Shin Yang PDF, also try the working URL form:
    www hostname, spaces encoded as %20.
    """
    candidates = [url]

    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()

        is_shin_yang_pdf = (
            host.endswith("shinyanggroup.com.my")
            and parsed.path.lower().endswith(".pdf")
        )

        if is_shin_yang_pdf:
            path = parsed.path.replace("+", "%20")

            alternate = urlunparse((
                parsed.scheme or "https",
                SHIN_YANG_HOST,
                path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            ))

            if alternate not in candidates:
                candidates.append(alternate)

    except Exception:
        pass

    return candidates


def extract_pdf_text(content):
    """Extract readable text from PDF bytes."""
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
    """Extract readable text and title from HTML."""
    soup = BeautifulSoup(content, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.decompose()

    title = (
        soup.title.get_text(strip=True)
        if soup.title
        else None
    )

    text = soup.get_text(" ", strip=True)
    return title, text


def verify_source(url):
    result = {
        "verified": False,
        "status_code": None,
        "content_type": None,
        "title": None,
        "text_preview": None,
        "error": None,
        "resolved_url": None,
    }

    candidates = build_url_candidates(url)
    last_error = None

    for candidate in candidates:
        try:
            response = requests.get(
                candidate,
                headers=DEFAULT_HEADERS,
                timeout=30,
                allow_redirects=True,
            )

            result["status_code"] = response.status_code
            result["content_type"] = response.headers.get(
                "Content-Type", ""
            )
            result["resolved_url"] = response.url

            if response.status_code != 200:
                last_error = f"HTTP status {response.status_code}"

                # Try the alternate URL only for the known official PDF.
                if candidate != candidates[-1]:
                    continue

                result["error"] = last_error
                return result

            content_type = (
                response.headers.get("Content-Type", "").lower()
            )
            path = urlparse(response.url).path.lower()

            is_pdf = (
                "application/pdf" in content_type
                or path.endswith(".pdf")
                or response.content.startswith(b"%PDF-")
            )

            if is_pdf:
                text = extract_pdf_text(response.content)

                if not text.strip():
                    result["error"] = (
                        "PDF downloaded successfully, but no text "
                        "could be extracted."
                    )
                    return result

                result["verified"] = True
                result["text_preview"] = text
                return result

            title, text = extract_html_text(response.content)

            if not text.strip():
                result["error"] = "HTTP 200 but page text is empty."
                return result

            result["verified"] = True
            result["title"] = title
            result["text_preview"] = text
            return result

        except requests.RequestException as error:
            last_error = str(error)

        except Exception as error:
            result["error"] = str(error)
            return result

    result["error"] = last_error or "Source could not be retrieved."
    return result


def source_priority(result):
    """Rank useful sources; ranking does not prove factual accuracy."""
    url = str(result.get("url") or "").lower()
    title = str(result.get("title") or "").lower()
    snippet = str(result.get("snippet") or "").lower()

    verification = result.get("verification") or {}
    verified_text = str(
        verification.get("text_preview") or ""
    ).lower()

    combined = f"{url} {title} {snippet} {verified_text}"
    score = 0

    if "shinyanggroup.com.my" in url:
        score += 100
    if "shin yang" in combined:
        score += 20
    if "91m maintenance" in combined:
        score += 20
    if "maintenance/work vessel" in combined:
        score += 20
    if "91m" in combined:
        score += 10

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

    if "thestar.com.my" in url:
        score += 15
    if "klsescreener.com" in url:
        score += 10

    return score


def main():
    configure_console_encoding()

    results = load_search_results()
    verified_results = []

    print("\n" + "=" * 60)
    print("SOURCE VERIFICATION")
    print("=" * 60)

    total = len(results)

    for index, result in enumerate(results, start=1):
        url = result.get("url")
        if not url:
            continue

        print(f"\n[{index}/{total}] Checking source...")
        print(f"URL: {url}")

        verification = verify_source(url)
        verified_result = {
            **result,
            "verification": verification,
        }
        verified_results.append(verified_result)

        status = (
            "Verified"
            if verification.get("verified")
            else "Not Verified"
        )
        print(f"Status: {status}")

        if verification.get("status_code") is not None:
            print(f"HTTP: {verification['status_code']}")

        if verification.get("resolved_url"):
            print(f"Resolved URL: {verification['resolved_url']}")

        if verification.get("error"):
            print(f"Error: {verification['error']}")

    verified_results.sort(key=source_priority, reverse=True)

    output_dir = Path(VERIFIED_PATH).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(VERIFIED_PATH, "w", encoding="utf-8") as file:
        json.dump(
            verified_results,
            file,
            indent=2,
            ensure_ascii=False,
        )

    verified_count = sum(
        1
        for item in verified_results
        if (item.get("verification") or {}).get("verified", False)
    )
    not_verified_count = len(verified_results) - verified_count

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total sources: {len(verified_results)}")
    print(f"Verified sources: {verified_count}")
    print(f"Not verified: {not_verified_count}")
    print(f"Saved to: {VERIFIED_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
