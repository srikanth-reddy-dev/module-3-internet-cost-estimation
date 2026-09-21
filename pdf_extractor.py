import pymupdf

PDF_PATH = "data/samples/energy_passion_clean.pdf"
OUTPUT_PATH = "data/samples/energy_passion.txt"


def extract_pdf_text():
    doc = pymupdf.open(PDF_PATH)

    page_count = len(doc)
    text = ""

    for page_number, page in enumerate(doc, start=1):
        page_text = page.get_text()

        if page_text.strip():
            text += f"\n\n--- PAGE {page_number} ---\n\n"
            text += page_text

    doc.close()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        file.write(text)

    print("PDF extraction completed.")
    print(f"Pages processed: {page_count}")
    print(f"Extracted text length: {len(text)} characters.")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    extract_pdf_text()