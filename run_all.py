"""
Reproducibility check — Phase 6.

Runs all 5 notebooks top-to-bottom in order using nbconvert, then
verifies every required artefact exists.

Usage:
    python run_all.py

Exit code 0 = all checks passed.
Exit code 1 = one or more checks failed.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent

NOTEBOOKS = [
    "notebooks/01_data_collection.ipynb",
    "notebooks/02_cleaning.ipynb",
    "notebooks/03_eda.ipynb",
    "notebooks/04_feature_engineering.ipynb",
    "notebooks/05_modelling.ipynb",
]

REQUIRED_VISUALS = [
    "visuals/pitstop_lap_distribution.png",
    "visuals/team_stop_duration.png",
    "visuals/strategy_frequency_by_season.png",
    "visuals/undercut_success_by_circuit.png",
    "visuals/position_change_distribution.png",
    "visuals/position_change_heatmap.png",
    "visuals/roc_curves.png",
    "visuals/shap_summary_plot.png",
]

REQUIRED_SRC = [
    "src/api.py",
    "src/features.py",
    "src/model.py",
]

REQUIRED_DATA = [
    "data/eda_reports/pit_stops_eda_report.md",
    "data/eda_reports/lap_times_eda_report.md",
    "data/eda_reports/results_eda_report.md",
    "data/cleaned/pit_stops_clean.csv",
    "data/cleaned/lap_times_clean.csv",
    "data/cleaned/results_clean.csv",
    "data/features.parquet",
    "requirements.txt",
]


def run_notebook(path: str) -> bool:
    """Execute a notebook in-place via nbconvert. Returns True on success."""
    print(f"\n{'='*60}")
    print(f"Running: {path}")
    print("="*60)
    result = subprocess.run(
        [
            sys.executable, "-m", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            "--ExecutePreprocessor.timeout=600",
            str(ROOT / path),
        ],
        capture_output=False,
    )
    if result.returncode == 0:
        print(f"  PASSED: {path}")
        return True
    else:
        print(f"  FAILED: {path}")
        return False


def check_artefacts() -> bool:
    """Verify all required output files exist."""
    print(f"\n{'='*60}")
    print("Artefact check")
    print("="*60)

    all_present = True
    for group_label, paths in [
        ("Visuals",     REQUIRED_VISUALS),
        ("Source files", REQUIRED_SRC),
        ("Data files",  REQUIRED_DATA),
    ]:
        print(f"\n  {group_label}:")
        for p in paths:
            exists = (ROOT / p).exists()
            status = "OK" if exists else "MISSING"
            print(f"    [{status}] {p}")
            if not exists:
                all_present = False

    return all_present


def main():
    failures = []

    # Run notebooks in order
    for nb in NOTEBOOKS:
        ok = run_notebook(nb)
        if not ok:
            failures.append(nb)

    # Check artefacts
    artefacts_ok = check_artefacts()

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("="*60)

    if failures:
        print(f"\nFailed notebooks ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
    else:
        print("\nAll notebooks: PASSED")

    if artefacts_ok:
        print("All artefacts: PRESENT")
    else:
        print("Artefact check: MISSING FILES (see above)")

    if not failures and artefacts_ok:
        print("\nPhase 6 COMPLETE — project is fully reproducible.")
        sys.exit(0)
    else:
        print("\nPhase 6 INCOMPLETE — fix failures above and re-run.")
        sys.exit(1)


if __name__ == "__main__":
    main()
