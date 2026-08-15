"""Phase 7: baseline linear regression, fiber_g/fat_g/protein_g/carbs_g -> GI.

Fits on the full data/processed/foods.csv (no train/test split -- that's
Phase 8's job). Chosen as the primary model because it's transparent: the
fitted formula GI ~ intercept + sum(coef_i * feature_i) can be handed to a
physician and checked for biological plausibility, and it's exactly what
gets re-applied client-side in JS (not an approximation of the model --
for linear regression, the formula IS the model).

GI is a property of the food being predicted, not of any person eating it.
"""

import json
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression

REPO_ROOT = Path(__file__).resolve().parents[1]
FOODS_CSV = REPO_ROOT / "data" / "processed" / "foods.csv"
SAVED_MODEL_PATH = Path(__file__).resolve().parent / "saved_model" / "linear_regression.json"

FEATURES = ["fiber_g", "fat_g", "protein_g", "carbs_g"]
TARGET = "GI"


def load_training_data():
    df = pd.read_csv(FOODS_CSV)
    return df[FEATURES], df[TARGET]


def fit_model(X, y):
    model = LinearRegression()
    model.fit(X, y)
    return model


def save_coefficients(model, n_samples, path=SAVED_MODEL_PATH):
    """Saves as JSON (not pickle) so the exact same file can be fetched and
    parsed client-side in JS without a Python-specific deserializer."""
    payload = {
        "model_type": "linear_regression",
        "target": TARGET,
        "features": FEATURES,
        "coefficients": {feat: float(c) for feat, c in zip(FEATURES, model.coef_)},
        "intercept": float(model.intercept_),
        "n_samples": n_samples,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main():
    X, y = load_training_data()
    model = fit_model(X, y)
    path = save_coefficients(model, n_samples=len(X))
    return model, path


if __name__ == "__main__":
    fitted_model, saved_path = main()
    print(f"Saved coefficients to {saved_path}")
    print(f"intercept: {fitted_model.intercept_:.4f}")
    for feature, coef in zip(FEATURES, fitted_model.coef_):
        print(f"  {feature}: {coef:.4f}")
