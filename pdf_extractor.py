import argparse
import pymupdf
import numpy as np
from paddleocr import PaddleOCR


DEFAULT_PDF_PATH = "data/samples/energy_passion_clean.pdf"
DEFAULT_OUTPUT_PATH = "data/samples/energy_passion.txt"


def extract_ocr_text(page, ocr):
    """
    Render a PDF page as an image and extract text using PaddleOCR.
    """

    pix = page.get_pixmap(
        dpi=300,
        alpha=False
    )

    image = np.frombuffer(
        pix.samples,
        dtype=np.uint8
    ).reshape(
        pix.height,
        pix.width,
        pix.n
    )

    result = ocr.predict(image)

    ocr_text = []

    for res in result:

        data = res.json

        if callable(data):
            data = data()

        # PaddleOCR result may contain the actual
        # prediction data inside the "res" key.
        if isinstance(data, dict):
            data = data.get("res", data)

        if isinstance(data, dict):

            rec_texts = data.get(
                "rec_texts",
                []
            )

            for text in rec_texts:

                text = str(text).strip()

                if text:
                    ocr_text.append(text)

    return "\n".join(ocr_text)


def extract_pdf_text(pdf_path, output_path):

    doc = pymupdf.open(pdf_path)

    page_count = len(doc)

    text = ""

    ocr = None

    for page_number, page in enumerate(
        doc,
        start=1
    ):

        page_text = page.get_text().strip()

        # -------------------------------------------------
        # 1. Use normal PDF text when available
        # -------------------------------------------------

        if page_text:

            text += (
                f"\n\n--- PAGE {page_number} ---\n\n"
            )

            text += page_text

            print(
                f"Page {page_number}: "
                "embedded PDF text found."
            )

            continue

        # -------------------------------------------------
        # 2. OCR fallback for scanned/image pages
        # -------------------------------------------------

        if ocr is None:

            print(
                "\nNo embedded text found."
            )

            print(
                "Initializing PaddleOCR..."
            )

            ocr = PaddleOCR(
                lang="en",
                enable_mkldnn=False
            )

        print(
            f"Running OCR on page {page_number}..."
        )

        ocr_text = extract_ocr_text(
            page,
            ocr
        )

        if ocr_text.strip():

            text += (
                f"\n\n--- PAGE {page_number} ---\n\n"
            )

            text += ocr_text

        else:

            print(
                f"Warning: No OCR text found "
                f"on page {page_number}."
            )

    doc.close()

    # -------------------------------------------------
    # Save extracted text
    # -------------------------------------------------

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(text)

    print(
        "\nPDF extraction completed."
    )

    print(
        f"Pages processed: {page_count}"
    )

    print(
        f"Extracted text length: "
        f"{len(text)} characters."
    )

    print(
        f"Saved to: {output_path}"
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Extract text from a vessel PDF "
            "using normal PDF extraction with "
            "PaddleOCR fallback for scanned pages."
        )
    )

    parser.add_argument(
        "pdf_path",
        nargs="?",
        default=DEFAULT_PDF_PATH
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_PATH
    )

    args = parser.parse_args()

    extract_pdf_text(
        args.pdf_path,
        args.output
    )