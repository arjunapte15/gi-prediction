"""Phase 8: 5-fold cross-validation and MAE for the Phase 7 baseline model.

n=129 is too small for a single train/test split to give a reliable accuracy
estimate (one unlucky split could over- or under-state error by a lot), so
this uses 5-fold CV instead: the data is split into 5 folds, each fold takes
a turn as the held-out test set while a fresh LinearRegression is fit on the
other 4, and per-fold MAE is averaged into a mean CV-MAE.

Rows in data/processed/foods.csv are grouped by cuisine and then alphabetical
within cuisine, not randomly ordered, so KFold uses shuffle=True (with a
fixed random_state for reproducible test runs) -- otherwise a fold could
easily land entirely within one cuisine.

Also fits on the FULL dataset (same as Phase 7) and compares that in-sample
MAE against the CV mean MAE as an overfitting check: a training MAE far below
the CV MAE would mean the model fits the training data much better than it
generalizes, which is a red flag for a 4-feature linear model at this sample
size (though with only 4 parameters plus intercept on 129 rows, overfitting
is not expected to be severe).
"""

import json
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold

from train import FEATURES, TARGET, load_training_data

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = Path(__file__).resolve().parent / "saved_model" / "cv_results.json"

N_SPLITS = 5
RANDOM_STATE = 42

# A training MAE this much below the CV mean MAE is flagged as an
# overfitting risk. Loose on purpose -- this is a 4-parameter linear model
# on 129 rows, where a training/CV gap driven by ordinary sampling noise
# (rather than genuine overfitting) is expected; the point is to catch a
# large, qualitatively different gap, not to police normal small-sample
# variance.
OVERFITTING_GAP_THRESHOLD = 10.0

# GI is on a roughly 0-110 scale. A mean CV-MAE above this is implausible
# for a reasonably-fit model on this scale and would suggest a pipeline bug
# rather than a genuinely bad model.
MAE_SANITY_CEILING = 50.0


def run_cross_validation(X, y, model_factory=LinearRegression, n_splits=N_SPLITS, random_state=RANDOM_STATE):
    """Returns a list of per-fold MAE values, one per fold.

    model_factory is a zero-argument callable returning a fresh, unfitted
    estimator (e.g. LinearRegression, or a lambda wrapping RidgeCV/LassoCV/
    RandomForestRegressor with fixed hyperparameters) -- a new instance is
    built for every fold so no fitted state leaks across folds. Reused as-is
    by Phase 9's Ridge/Lasso/random forest comparison.
    """
    kfold = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    fold_maes = []
    for train_idx, test_idx in kfold.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = model_factory()
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        fold_maes.append(mean_absolute_error(y_test, predictions))
    return fold_maes


def compute_training_mae(X, y, model_factory=LinearRegression):
    """In-sample MAE: fit on all of X/y, then score against the same rows."""
    model = model_factory()
    model.fit(X, y)
    predictions = model.predict(X)
    return mean_absolute_error(y, predictions), model


def save_results(fold_maes, mean_cv_mae, training_mae, overfitting_gap, path=RESULTS_PATH):
    payload = {
        "n_splits": N_SPLITS,
        "random_state": RANDOM_STATE,
        "features": FEATURES,
        "target": TARGET,
        "fold_mae": fold_maes,
        "mean_cv_mae": mean_cv_mae,
        "training_mae": training_mae,
        "overfitting_gap": overfitting_gap,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main():
    X, y = load_training_data()

    fold_maes = run_cross_validation(X, y)
    mean_cv_mae = sum(fold_maes) / len(fold_maes)

    training_mae, _ = compute_training_mae(X, y)
    overfitting_gap = mean_cv_mae - training_mae

    results_path = save_results(fold_maes, mean_cv_mae, training_mae, overfitting_gap)
    return {
        "fold_mae": fold_maes,
        "mean_cv_mae": mean_cv_mae,
        "training_mae": training_mae,
        "overfitting_gap": overfitting_gap,
        "results_path": results_path,
    }


if __name__ == "__main__":
    results = main()
    print(f"Saved results to {results['results_path']}")
    print(f"Per-fold MAE: {[f'{m:.4f}' for m in results['fold_mae']]}")
    print(f"Mean CV-MAE: {results['mean_cv_mae']:.4f}")
    print(f"Training MAE (in-sample, full-data fit): {results['training_mae']:.4f}")
    print(f"Overfitting gap (mean CV-MAE - training MAE): {results['overfitting_gap']:.4f}")
