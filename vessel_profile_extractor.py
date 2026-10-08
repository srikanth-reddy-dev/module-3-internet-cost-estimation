import json
import re


TEXT_PATH = r"C:\OCR_Test\module3_ocr_test.txt"
OUTPUT_PATH = "data/output/vessel_profile.json"


def load_text():
    with open(TEXT_PATH, "r", encoding="utf-8") as file:
        return file.read()


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

    # =========================================================
    # VESSEL NAME
    # =========================================================

    match = re.search(
        r"91M\s+BUOY\s+MAINTENANCE\s+VESSEL",
        text,
        re.IGNORECASE
    )

    profile["vessel_name"] = (
        match.group(0).strip()
        if match
        else None
    )


    # =========================================================
    # DESIGN
    # =========================================================

    profile["design"] = profile["vessel_name"]


    # =========================================================
    # VESSEL TYPE
    # =========================================================

    cable_layer_match = re.search(
        r"Cable\s+layer\s*-\s*future\s+provision",
        text,
        re.IGNORECASE
    )

    if cable_layer_match:
        profile["vessel_type"] = (
            "Buoy maintenance vessel "
            "(Cable layer - future provision)"
        )
    else:
        profile["vessel_type"] = "Buoy maintenance vessel"


    # =========================================================
    # LENGTH OVERALL
    # =========================================================
    # OCR:
    # 91.0M
    # Length o a.

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*M"
        r"[ \t]*\n[ \t]*"
        r"Length\s+o\s*a",
        text,
        re.IGNORECASE
    )

    profile["length_overall_m"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # BREADTH
    # =========================================================
    # OCR:
    # 18.20 M
    # Breadth mouices

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*M"
        r"[ \t]*\n[ \t]*"
        r"Breadth\s+(?:mouices|moulded)",
        text,
        re.IGNORECASE
    )

    profile["breadth_m"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # DEPTH
    # =========================================================
    # OCR:
    # 7.80 M
    # Depth

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*M"
        r"[ \t]*\n[ \t]*"
        r"Depth",
        text,
        re.IGNORECASE
    )

    profile["depth_m"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # DESIGN DRAFT
    # =========================================================
    # OCR:
    # Design draft max.
    # 4.20 M

    match = re.search(
        r"Design\s+draft\s+max\.?"
        r"[\s\S]{0,30}?"
        r"(\d+(?:[.,]\d+)?)\s*M",
        text,
        re.IGNORECASE
    )

    profile["design_draft_m"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # DEADWEIGHT
    # =========================================================
    # OCR:
    # Deadweight
    # 1450 T (approx.)

    match = re.search(
        r"Deadweight"
        r"[ \t]*\n[ \t]*"
        r"(\d+(?:[.,]\d+)?)\s*T",
        text,
        re.IGNORECASE
    )

    profile["deadweight_t"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # DECK AREA
    # =========================================================
    # OCR:
    # Deck area (aporox.)
    # 700 MF

    match = re.search(
        r"Deck\s+area"
        r"[\s\S]{0,30}?"
        r"(\d+(?:[.,]\d+)?)\s*M[F²2]?",
        text,
        re.IGNORECASE
    )

    profile["deck_area_m2"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # SERVICE SPEED
    # =========================================================
    # OCR:
    # Service speed
    # 12 Knots

    match = re.search(
        r"Service\s+speed"
        r"[ \t]*\n[ \t]*"
        r"(\d+(?:[.,]\d+)?)\s*Knots?",
        text,
        re.IGNORECASE
    )

    profile["service_speed_knots"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # PROPULSION
    # =========================================================
    # OCR:
    # Propulsion
    # Twin azimuth thruster (diesel electric)

    match = re.search(
        r"Twin\s+azimuth\s+thruster\s*"
        r"\(diesel\s+electric\)",
        text,
        re.IGNORECASE
    )

    profile["propulsion"] = (
        match.group(0).strip()
        if match
        else None
    )


    # =========================================================
    # PROPULSION MOTOR
    # =========================================================
    # OCR:
    # Propulsion motor
    # 2 nos. x 1200 kW

    match = re.search(
        r"Propulsion\s+motor"
        r"\s*\n\s*"
        r"(\d+)\s*(?:nos?\.?\s*)?"
        r"[x×]\s*"
        r"(\d+(?:[.,]\d+)?)\s*kW",
        text,
        re.IGNORECASE
    )

    if match:
        profile["propulsion_motor"] = (
            f"{match.group(1)} x "
            f"{match.group(2)} kW"
        )
    else:
        profile["propulsion_motor"] = None


    # =========================================================
    # MAIN GENERATOR
    # =========================================================
    # OCR:
    # 4 nos. × 2000 ekW. 415V, 50 Hz. 3 phase
    # Main generator

    match = re.search(
        r"(\d+)\s*(?:nos?\.?\s*)?"
        r"[x×]\s*"
        r"(\d+(?:[.,]\d+)?)\s*ekW"
        r"[^\n]*"
        r"\n[ \t]*"
        r"Main\s+generator",
        text,
        re.IGNORECASE
    )

    if match:
        profile["main_generator"] = (
            f"{match.group(1)} x "
            f"{match.group(2)} ekW"
        )
    else:
        profile["main_generator"] = None


    # =========================================================
    # BOW / TUNNEL THRUSTER
    # =========================================================
    # OCR:
    # 1 no x 900 kW (motor driven)
    # Bow thruster

    match = re.search(
        r"(\d+)\s*(?:nos?\.?\s*)?"
        r"[x×]\s*"
        r"(\d+(?:[.,]\d+)?)\s*kW"
        r"\s*\(motor\s+driven\)"
        r"\s*\n[ \t]*"
        r"Bow\s+thruster",
        text,
        re.IGNORECASE
    )

    if match:
        profile["tunnel_thrusters"] = (
            f"{match.group(1)} x "
            f"{match.group(2)} kW"
        )
    else:
        profile["tunnel_thrusters"] = None


    # =========================================================
    # FRESH WATER
    # =========================================================
    # OCR:
    # 400 M³ (approx.)
    # Fresh water

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*M[³3]"
        r"[\s\S]{0,30}?"
        r"Fresh\s+water",
        text,
        re.IGNORECASE
    )

    profile["fresh_water_m3"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # FUEL OIL
    # =========================================================
    # OCR:
    # Fuel oil
    # 300 M³ (approx.)

    match = re.search(
        r"Fuel\s+oil"
        r"[ \t]*\n[ \t]*"
        r"(\d+(?:[.,]\d+)?)\s*M[³3]",
        text,
        re.IGNORECASE
    )

    profile["fuel_oil_m3"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # WATER BALLAST
    # =========================================================
    # OCR:
    # Water ballast
    # 1500 M³ (approx.)

    match = re.search(
        r"Water\s+ballast"
        r"[ \t]*\n[ \t]*"
        r"(\d+(?:[.,]\d+)?)\s*M[³3]",
        text,
        re.IGNORECASE
    )

    profile["water_ballast_m3"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # CARGO HOLD
    # =========================================================
    # OCR:
    # Cargo hola
    # 700 M³ (approx.)

    match = re.search(
        r"(?:Cargo\s+hola|Cargo\s+hold)"
        r"[\s\S]{0,30}?"
        r"(\d+(?:[.,]\d+)?)\s*M[³3]",
        text,
        re.IGNORECASE
    )

    profile["cargo_hold_m3"] = (
        normalize_number(match.group(1))
        if match
        else None
    )


    # =========================================================
    # OTHER FIELDS
    # =========================================================

    profile["classification"] = None
    profile["delivery_year"] = None

    profile["source_document"] = (
        "OCR extracted vessel specification"
    )

    return profile


# =============================================================
# MAIN
# =============================================================

if __name__ == "__main__":

    text = load_text()

    profile = extract_profile(text)

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        "\nVessel profile extracted successfully."
    )

    print(
        f"Saved to: {OUTPUT_PATH}\n"
    )

    print("Extracted Profile:")

    for key, value in profile.items():
        print(f"{key}: {value}")