import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "model"))

import export_model  # noqa: E402
from train import load_training_data  # noqa: E402

# Row indices (into data/processed/foods.csv, 0-indexed) used for the
# round-trip check: first row, a middle row, and a south_asian row near the
# end -- spans both cuisines and both ends of the file.
SAMPLE_ROW_INDICES = [0, 64, 128]


def _manual_predict(coefficients_payload, row):
    total = coefficients_payload["intercept"]
    for feature in coefficients_payload["features"]:
        total += coefficients_payload["coefficients"][feature] * row[feature]
    return total


def test_coefficients_file_has_expected_shape():
    _, saved_path = export_model.main()
    payload = json.loads(saved_path.read_text(encoding="utf-8"))
    assert payload["model_type"] == "ridge_regression"
    assert payload["target"] == "GI"
    assert set(payload["coefficients"].keys()) == set(payload["features"])
    assert isinstance(payload["intercept"], (int, float))
    assert isinstance(payload["alpha"], (int, float))
    assert payload["alpha"] > 0


def test_exported_coefficients_reproduce_ridge_predictions_for_known_rows():
    """Round-trip: recompute predictions using ONLY the exported JSON
    (intercept + sum(coef_i * feature_i)), simulating what the JS side will
    eventually do, and confirm they match Ridge's own .predict() output for
    the same rows. This is what guarantees the website's formula won't
    silently diverge from the real model.
    """
    model, saved_path = export_model.main()
    payload = json.loads(saved_path.read_text(encoding="utf-8"))

    X, _ = load_training_data()
    python_predictions = model.predict(X)

    for idx in SAMPLE_ROW_INDICES:
        row = X.iloc[idx]
        manual_prediction = _manual_predict(payload, row)
        python_prediction = python_predictions[idx]
        assert math.isclose(manual_prediction, python_prediction, rel_tol=1e-9, abs_tol=1e-6), (
            f"row {idx}: manual={manual_prediction!r} vs python={python_prediction!r}"
        )
