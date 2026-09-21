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

    return data["results"]


def verify_source(url):
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        if response.status_code != 200:
            return {
                "verified": False,
                "status_code": response.status_code,
                "title": None,
                "text_preview": None
            }

        content_type = response.headers.get("Content-Type", "").lower()

        # Handle PDF sources
        if "application/pdf" in content_type or url.lower().endswith(".pdf"):
            reader = PdfReader(BytesIO(response.content))

            text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            return {
                "verified": True,
                "status_code": response.status_code,
                "title": None,
                "text_preview": text
            }

        # Handle normal HTML webpages
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.get_text(strip=True) if soup.title else None

        text = soup.get_text(" ", strip=True)

        return {
            "verified": True,
            "status_code": response.status_code,
            "title": title,
            "text_preview": text
        }

    except requests.RequestException as error:
        return {
            "verified": False,
            "status_code": None,
            "title": None,
            "text_preview": None,
            "error": str(error)
        }

    except Exception as error:
        return {
            "verified": False,
            "status_code": None,
            "title": None,
            "text_preview": None,
            "error": str(error)
        }


if __name__ == "__main__":
    results = load_search_results()
    verified_results = []

    for result in results:
        verification = verify_source(result["url"])

        verified_results.append({
            **result,
            "verification": verification
        })

        print(
            f"{result['title']} -> "
            f"{'Verified' if verification['verified'] else 'Not Verified'}"
        )

    with open(VERIFIED_PATH, "w", encoding="utf-8") as file:
        json.dump(
            verified_results,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"\nSaved verification results to: {VERIFIED_PATH}")