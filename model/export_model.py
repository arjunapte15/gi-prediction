"""Phase 10: export the chosen primary model (Ridge) to coefficients.json --
the file the eventual static site fetches and parses client-side.

This is not an approximation of "the real model": for a linear model
(including Ridge, still a linear formula under an L2 penalty), the exported
{feature: coefficient} map plus intercept and alpha IS the model. No Python
process or server is needed to apply it -- reconstructing a prediction is
just `intercept + sum(coef_i * feature_i)`, done in JS instead of Python.

Ridge was chosen over baseline OLS (marginally better CV-MAE) and over
random forest (which had a lower CV-MAE but no single formula to check for
biological plausibility) -- see model_selection.md for the full reasoning.
Reuses Phase 9's ridge_factory (same alpha grid, same RidgeCV selection) so
this export is the same Ridge fit already evaluated in
model_comparison.json, refit here on the full dataset as the final,
canonical model.
"""

import json
from pathlib import Path

from compare_models import ridge_factory
from train import FEATURES, TARGET, load_training_data

COEFFICIENTS_PATH = Path(__file__).resolve().parent / "saved_model" / "coefficients.json"


def fit_final_ridge():
    X, y = load_training_data()
    model = ridge_factory()
    model.fit(X, y)
    return model, len(X)


def export_coefficients(model, n_samples, path=COEFFICIENTS_PATH):
    payload = {
        "model_type": "ridge_regression",
        "target": TARGET,
        "features": FEATURES,
        "coefficients": {feat: float(c) for feat, c in zip(FEATURES, model.coef_)},
        "intercept": float(model.intercept_),
        "alpha": float(model.alpha_),
        "n_samples": n_samples,
        "prediction_formula": "GI ≈ intercept + sum(coefficients[feature] * feature_value for feature in features)",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main():
    model, n_samples = fit_final_ridge()
    path = export_coefficients(model, n_samples)
    return model, path


if __name__ == "__main__":
    fitted_model, saved_path = main()
    print(f"Exported Ridge coefficients to {saved_path}")
    print(f"alpha: {fitted_model.alpha_}")
    print(f"intercept: {fitted_model.intercept_:.4f}")
    for feature, coef in zip(FEATURES, fitted_model.coef_):
        print(f"  {feature}: {coef:.4f}")
