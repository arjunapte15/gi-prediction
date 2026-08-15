"""Phase 9: Ridge, Lasso, and random forest comparison against Phase 7/8's
baseline linear regression (mean CV-MAE 12.5219).

Ridge and Lasso are still a single linear formula underneath -- same shape as
Phase 7's model -- but fit with an L2 (Ridge) or L1 (Lasso) penalty that
discourages leaning too hard on any one nutrient; Lasso's penalty can drive a
coefficient to exactly zero. Random forest is a genuinely different model
family: many small if/then splits averaged together, no single formula, more
capable of catching nonlinear/interaction patterns but much harder to hand to
a physician for a plausibility check. Given this dataset is only 129 rows,
random forest is not expected to meaningfully beat the linear approaches --
that is itself the reportable finding, not a failure.

Reuses Phase 8's run_cross_validation/compute_training_mae (model/evaluate.py)
unchanged (generalized to take a model_factory) so all four models -- Phase
7/8's baseline plus these three -- are evaluated with the exact same 5-fold
CV procedure and are directly comparable.

Alpha selection for Ridge/Lasso uses their built-in CV variants (RidgeCV,
LassoCV) over a log-spaced grid, refit inside every outer CV fold (nested
CV) rather than a single alpha chosen once on the full dataset -- this avoids
leaking the held-out fold's information into hyperparameter selection.
"""

import json
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LassoCV, RidgeCV

from evaluate import compute_training_mae, run_cross_validation
from train import FEATURES, TARGET, load_training_data

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = Path(__file__).resolve().parent / "saved_model" / "model_comparison.json"
BASELINE_RESULTS_PATH = Path(__file__).resolve().parent / "saved_model" / "cv_results.json"

# Phase 7's baseline fiber_g coefficient, for the sign/magnitude comparison
# this phase is required to report (see model/saved_model/linear_regression_notes.md).
BASELINE_FIBER_COEF = 0.7631015372053028

RANDOM_STATE = 42

# Log-spaced alpha grid for RidgeCV/LassoCV -- wide enough to span
# "barely regularized" to "heavily regularized" for coefficients on this
# nutrient scale (roughly 0-100 per feature, GI target roughly 0-110).
ALPHA_GRID = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]

# Shallow on purpose: 129 rows is little enough data that an unconstrained
# forest would just memorize individual foods rather than learn a pattern
# that generalizes.
RF_N_ESTIMATORS = 100
RF_MAX_DEPTH = 4


def ridge_factory():
    return RidgeCV(alphas=ALPHA_GRID)


def lasso_factory():
    return LassoCV(alphas=ALPHA_GRID, random_state=RANDOM_STATE, max_iter=10000)


def random_forest_factory():
    return RandomForestRegressor(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        random_state=RANDOM_STATE,
    )


MODEL_FACTORIES = {
    "ridge": ridge_factory,
    "lasso": lasso_factory,
    "random_forest": random_forest_factory,
}


def evaluate_model(name, model_factory, X, y):
    fold_maes = run_cross_validation(X, y, model_factory=model_factory)
    mean_cv_mae = sum(fold_maes) / len(fold_maes)
    training_mae, fitted_model = compute_training_mae(X, y, model_factory=model_factory)
    overfitting_gap = mean_cv_mae - training_mae

    report = {
        "model": name,
        "fold_mae": fold_maes,
        "mean_cv_mae": mean_cv_mae,
        "training_mae": training_mae,
        "overfitting_gap": overfitting_gap,
    }

    if hasattr(fitted_model, "coef_"):
        report["coefficients"] = {feat: float(c) for feat, c in zip(FEATURES, fitted_model.coef_)}
        report["intercept"] = float(fitted_model.intercept_)
        if hasattr(fitted_model, "alpha_"):
            report["selected_alpha"] = float(fitted_model.alpha_)
        fiber_coef = report["coefficients"]["fiber_g"]
        report["fiber_g_analysis"] = {
            "value": fiber_coef,
            "sign": "positive" if fiber_coef > 0 else ("negative" if fiber_coef < 0 else "zero"),
            "matches_baseline_sign": (fiber_coef > 0) == (BASELINE_FIBER_COEF > 0),
            "zeroed_out": fiber_coef == 0.0,
        }

    if hasattr(fitted_model, "feature_importances_"):
        importances = fitted_model.feature_importances_
        report["feature_importances"] = {feat: float(imp) for feat, imp in zip(FEATURES, importances)}
        report["feature_importances_sum"] = float(importances.sum())
        fiber_importance = report["feature_importances"]["fiber_g"]
        report["fiber_g_analysis"] = {
            "value": fiber_importance,
            "rank": sorted(report["feature_importances"].values(), reverse=True).index(fiber_importance) + 1,
            "note": "random forest importances are non-negative by construction, not signed -- "
            "not directly comparable to a linear coefficient's sign.",
        }

    return report


def save_results(reports, path=RESULTS_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
    return path


def main():
    X, y = load_training_data()
    reports = {name: evaluate_model(name, factory, X, y) for name, factory in MODEL_FACTORIES.items()}
    results_path = save_results(reports)
    return reports, results_path


if __name__ == "__main__":
    reports, results_path = main()

    baseline_mean_cv_mae = None
    if BASELINE_RESULTS_PATH.exists():
        baseline_mean_cv_mae = json.loads(BASELINE_RESULTS_PATH.read_text(encoding="utf-8"))["mean_cv_mae"]

    print(f"Saved results to {results_path}")
    if baseline_mean_cv_mae is not None:
        print(f"Baseline (Phase 7/8 linear regression) mean CV-MAE: {baseline_mean_cv_mae:.4f}")
    print()

    for name, report in reports.items():
        print(f"--- {name} ---")
        print(f"  Per-fold MAE: {[f'{m:.4f}' for m in report['fold_mae']]}")
        print(f"  Mean CV-MAE: {report['mean_cv_mae']:.4f}")
        print(f"  Training MAE: {report['training_mae']:.4f}")
        print(f"  Overfitting gap: {report['overfitting_gap']:.4f}")
        if "coefficients" in report:
            print(f"  Selected alpha: {report.get('selected_alpha')}")
            print(f"  Coefficients: {report['coefficients']}")
            print(f"  Intercept: {report['intercept']:.4f}")
        if "feature_importances" in report:
            print(f"  Feature importances: {report['feature_importances']}")
            print(f"  Importances sum: {report['feature_importances_sum']:.4f}")
        print(f"  fiber_g analysis: {report['fiber_g_analysis']}")
        print()
