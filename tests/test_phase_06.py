import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "notebooks"))

import phase_06_eda  # noqa: E402

EXPECTED_PLOT_FILES = [f"distributions_{col}.png" for col in phase_06_eda.DISTRIBUTION_COLUMNS] + [
    "correlation_matrix.png"
]


def test_eda_script_runs_and_produces_report():
    report_path = phase_06_eda.main()
    assert report_path.exists()
    assert report_path.read_text(encoding="utf-8").strip() != ""


def test_eda_script_produces_all_plots():
    phase_06_eda.main()
    for filename in EXPECTED_PLOT_FILES:
        plot_path = phase_06_eda.OUTPUT_DIR / filename
        assert plot_path.exists(), f"missing plot file: {filename}"
        assert plot_path.stat().st_size > 0
