import os
import subprocess
import sys


PIPELINE = [
    ("PDF Extraction", "pdf_extractor.py"),
    ("Vessel Profile Extraction", "vessel_profile_extractor.py"),
    ("Web Search", "web_search.py"),
    ("Source Verification", "source_verifier.py"),
    ("Cost Extraction", "cost_extractor.py"),
    ("Specification Matching", "spec_matcher.py"),
    ("Cost Normalization", "cost_normalizer.py"),
    ("Cost Adjustment", "cost_adjuster.py"),
    ("Comparable Vessel Analysis", "comparable_analysis.py"),
    ("Vessel-Level Cost Estimate", "vessel_estimator.py"),
    ("Final Report", "final_report.py"),
]


def configure_environment():
    """
    Configure child Python processes to use UTF-8.

    This prevents Windows cp1252 decoding errors when
    subprocess output contains Unicode characters.
    """

    environment = os.environ.copy()

    environment["PYTHONIOENCODING"] = "utf-8"

    return environment


def run_step(step_name, script_name):

    print("\n" + "=" * 60)
    print(f"STARTING: {step_name}")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=configure_environment()
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:

        print(
            f"\n❌ {step_name} failed."
        )

        return False

    print(
        f"✅ {step_name} completed."
    )

    return True


def run_pipeline():

    print(
        "\n🚢 MODULE 3 - VESSEL COST ESTIMATION HARNESS"
    )

    print("=" * 60)

    for step_name, script_name in PIPELINE:

        success = run_step(
            step_name,
            script_name
        )

        if not success:

            print(
                "\n❌ Pipeline stopped."
            )

            return

    print(
        "\n" + "=" * 60
    )

    print(
        "✅ COMPLETE PIPELINE FINISHED"
    )

    print(
        "=" * 60
    )

    print(
        "\nGenerated / updated outputs:"
    )

    print(
        "- C:\\OCR_Test\\module3_ocr_test.txt"
    )

    print(
        "- data/output/vessel_profile.json"
    )

    print(
        "- data/output/search_results.json"
    )

    print(
        "- data/output/verified_sources.json"
    )

    print(
        "- data/output/cost_evidence.json"
    )

    print(
        "- data/output/spec_matches.json"
    )

    print(
        "- data/output/normalized_costs.json"
    )

    print(
        "- data/output/adjusted_costs.json"
    )

    print(
        "- data/output/comparable_analysis.json"
    )

    print(
        "- data/output/final_estimate.json"
    )

    print(
        "- data/output/final_report.json"
    )


if __name__ == "__main__":

    run_pipeline()