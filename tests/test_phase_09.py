import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "model"))

import compare_models  # noqa: E402
import evaluate  # noqa: E402


def test_all_three_models_run_across_exactly_five_folds():
    reports, _ = compare_models.main()
    assert set(reports.keys()) == {"ridge", "lasso", "random_forest"}
    for name, report in reports.items():
        assert len(report["fold_mae"]) == 5, f"{name}: expected 5 folds"
        for mae in report["fold_mae"]:
            assert math.isfinite(mae), f"{name}: non-finite fold MAE"
            assert mae >= 0, f"{name}: negative fold MAE"


def test_all_three_models_have_sane_mean_cv_mae():
    reports, _ = compare_models.main()
    for name, report in reports.items():
        mean_cv_mae = report["mean_cv_mae"]
        assert math.isfinite(mean_cv_mae), f"{name}: non-finite mean CV-MAE"
        assert mean_cv_mae >= 0, f"{name}: negative mean CV-MAE"
        assert mean_cv_mae <= evaluate.MAE_SANITY_CEILING, (
            f"{name}: mean CV-MAE={mean_cv_mae:.4f} exceeds the sanity ceiling of "
            f"{evaluate.MAE_SANITY_CEILING} for a roughly 0-110 GI scale -- "
            "likely a pipeline bug, not just a weak model."
        )


def test_random_forest_feature_importances_sum_to_one():
    reports, _ = compare_models.main()
    importances = reports["random_forest"]["feature_importances"]
    assert set(importances.keys()) == set(compare_models.FEATURES)
    total = sum(importances.values())
    assert math.isclose(total, 1.0, abs_tol=1e-6), f"feature importances sum to {total}, expected 1.0"
    for feat, value in importances.items():
        assert value >= 0, f"{feat}: importance {value} is negative"
