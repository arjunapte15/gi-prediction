import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "model"))

import evaluate  # noqa: E402


def test_cross_validation_runs_across_exactly_five_folds():
    results = evaluate.main()
    assert len(results["fold_mae"]) == 5
    for mae in results["fold_mae"]:
        assert math.isfinite(mae)
        assert mae >= 0


def test_mean_cv_mae_is_finite_nonnegative_and_sane():
    results = evaluate.main()
    mean_cv_mae = results["mean_cv_mae"]
    assert math.isfinite(mean_cv_mae)
    assert mean_cv_mae >= 0
    assert mean_cv_mae <= evaluate.MAE_SANITY_CEILING, (
        f"mean CV-MAE={mean_cv_mae:.4f} exceeds the sanity ceiling of "
        f"{evaluate.MAE_SANITY_CEILING} for a roughly 0-110 GI scale -- "
        "likely a pipeline bug, not just a weak model."
    )


def test_overfitting_gap_is_not_implausibly_large():
    """Flags rather than silently passes: a training MAE far below the CV
    mean MAE means the model fits the training data much better than it
    generalizes, which is a real overfitting signal even for a small linear
    model, and shouldn't be swallowed."""
    results = evaluate.main()
    gap = results["overfitting_gap"]
    assert math.isfinite(gap)
    assert gap <= evaluate.OVERFITTING_GAP_THRESHOLD, (
        f"overfitting gap (mean CV-MAE {results['mean_cv_mae']:.4f} - "
        f"training MAE {results['training_mae']:.4f}) = {gap:.4f}, exceeds "
        f"the {evaluate.OVERFITTING_GAP_THRESHOLD} threshold -- flag as an "
        "overfitting risk."
    )
