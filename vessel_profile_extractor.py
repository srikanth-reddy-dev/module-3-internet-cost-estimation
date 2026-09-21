import json
import re

TEXT_PATH = "data/samples/energy_passion.txt"
OUTPUT_PATH = "data/output/vessel_profile.json"


def load_text():
    with open(TEXT_PATH, "r", encoding="utf-8") as file:
        return file.read()


def find_value_after_label(text, label, pattern):
    match = re.search(
        rf"{re.escape(label)}\s*[:\-]?\s*(?:\n\s*)?{pattern}",
        text,
        re.IGNORECASE
    )
    return match.group(1).strip() if match else None


def normalize_number(value):
    if value is None:
        return None

    value = value.replace(",", ".").strip()

    try:
        return float(value)
    except ValueError:
        return None


def extract_profile(text):
    profile = {}

    # Basic information
    match = re.search(r"Name of ship:\s*(.+)", text, re.IGNORECASE)
    profile["vessel_name"] = match.group(1).strip() if match else None

    match = re.search(r"(Ulstein PX121[^\n]*)", text, re.IGNORECASE)
    profile["design"] = match.group(1).strip() if match else None

    if profile["design"]:
        profile["design"] = profile["design"].replace(" DESIGN", "").strip()

    match = re.search(
        r"TECHNICAL OUTLINE SPECIFICATION\s+(.+?VESSEL)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if match:
        vessel_type = match.group(1).replace("\n", " ").strip()
        profile["vessel_type"] = vessel_type
    else:
        profile["vessel_type"] = None

    match = re.search(r"Yard:\s*(.+)", text, re.IGNORECASE)
    profile["yard"] = match.group(1).strip() if match else None

    match = re.search(r"Delivered\s+(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
    if match:
        profile["delivery_year"] = int(match.group(1)[-4:])
    else:
        profile["delivery_year"] = None

    # Main dimensions
    match = re.search(
        r"Length o\.a\.\s*:\s*(?:\n\s*)?([\d,.]+)\s*m",
        text,
        re.IGNORECASE
    )
    profile["length_overall_m"] = normalize_number(match.group(1)) if match else None

    match = re.search(
        r"Breadth mld\.\s*:\s*(?:\n\s*)?([\d,.]+)\s*m",
        text,
        re.IGNORECASE
    )
    profile["breadth_m"] = normalize_number(match.group(1)) if match else None

    match = re.search(
        r"Design draft\s*:\s*(?:\n\s*)?([\d,.]+)\s*m",
        text,
        re.IGNORECASE
    )
    profile["design_draft_m"] = normalize_number(match.group(1)) if match else None

    # Tonnage
    match = re.search(
        r"DWT\s*:\s*(?:\n\s*)?([\d,.]+)",
        text,
        re.IGNORECASE
    )
    profile["deadweight_t"] = normalize_number(match.group(1)) if match else None

    match = re.search(
        r"Gross Tonnage\s*:\s*(?:\n\s*)?([\d,.]+)",
        text,
        re.IGNORECASE
    )
    profile["gross_tonnage"] = normalize_number(match.group(1)) if match else None

    match = re.search(
        r"Net Tonnage\s*:\s*(?:\n\s*)?([\d,.]+)",
        text,
        re.IGNORECASE
    )
    profile["net_tonnage"] = normalize_number(match.group(1)) if match else None

    # Deck area
    match = re.search(
        r"Work/Cargo Deck area:\s*([\d,.]+)\s*m2",
        text,
        re.IGNORECASE
    )
    profile["deck_area_m2"] = normalize_number(match.group(1)) if match else None

    # Service speed
    match = re.search(
        r"Service speed/cons\.[\s\S]{0,300}?(\d+(?:[.,]\d+)?)\s*kts",
        text,
        re.IGNORECASE
    )
    profile["service_speed_knots"] = (
        normalize_number(match.group(1)) if match else None
    )

    # Main engine
    match = re.search(
        r"Main engine\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )
    profile["main_engine"] = match.group(1).strip() if match else None

    # Propulsion
    match = re.search(
        r"Propulsion\s*:\s*(.+)",
        text,
        re.IGNORECASE
    )
    profile["propulsion"] = match.group(1).strip() if match else None

    # Tunnel thrusters
    match = re.search(
        r"Bow thruster:\s*(.+)",
        text,
        re.IGNORECASE
    )
    profile["tunnel_thrusters"] = match.group(1).strip() if match else None

    # Classification
    match = re.search(
        r"Classification:\s*(?:\n\s*)?([^\n]+)",
        text,
        re.IGNORECASE
    )
    profile["classification"] = match.group(1).strip() if match else None

    profile["source_document"] = "energy_passion_clean.pdf"

    return profile


if __name__ == "__main__":
    text = load_text()
    profile = extract_profile(text)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(profile, file, indent=2, ensure_ascii=False)

    print("\nVessel profile extracted successfully.")
    print(f"Saved to: {OUTPUT_PATH}\n")

    print("Extracted Profile:")

    for key, value in profile.items():
        print(f"{key}: {value}")