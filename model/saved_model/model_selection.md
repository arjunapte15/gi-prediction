# Phase 10: model selection decision

## Decision

**Ridge regression is the primary model.** Chosen by the user (this is a
product decision, not something Claude Code decided). Exported coefficients
live in `coefficients.json` -- that is the file the static site fetches and
parses client-side; no server or live Python process is involved in applying
the model.

## Candidates and their 5-fold CV-MAE (Phase 8/9 results)

| model | mean CV-MAE | overfitting gap | formula? |
|---|---|---|---|
| Baseline OLS (Phase 7/8) | 12.5219 | 0.7819 | single linear formula |
| **Ridge (chosen)** | **12.4956** | 0.7502 | single linear formula |
| Lasso | 12.5219 | 0.7819 | single linear formula |
| Random forest | 10.8013 | 3.0399 | ~100 averaged trees, no single formula |

## Reasoning

- Ridge's CV-MAE (12.4956) was marginally better than baseline OLS
  (12.5219), so there's no accuracy cost to preferring Ridge over the
  unregularized baseline.
- Random forest's CV-MAE was meaningfully lower (10.8013, ~14% lower /
  ~1.7 points better on the GI scale). That gap was judged **not large
  enough to give up a physician-checkable formula** for an uninterpretable
  ensemble of ~100 trees with no single equation. This tradeoff is decided
  by the project's own stated design premise: models from Phase 7 onward
  exist specifically to be handed to a physician and checked for biological
  plausibility (see `data/data_dictionary.md`, `model/saved_model/linear_regression_notes.md`).
  A random forest's `feature_importances_` can say "carbs_g matters most,"
  but it cannot produce the single signed weight-per-nutrient formula that
  plausibility-checking requires.
- Ridge over Lasso: with this dataset's four features, Lasso's CV-selected
  alpha (0.001, the smallest value in the search grid) barely regularized
  at all, landing almost exactly on the unregularized OLS coefficients --
  effectively no sparsity benefit here (nothing got zeroed out). Ridge's
  CV-selected alpha (100.0) does meaningfully shrink the coefficients
  (visible in `fiber_g` moving from OLS's 0.7631 to Ridge's 0.6291), which
  is the guardrail-against-over-relying-on-one-nutrient behavior this
  project wants, without dropping a feature entirely.

## The fiber_g anomaly, carried forward (not masked)

Ridge's `fiber_g` coefficient is **+0.6291** -- still positive, still
contrary to the biologically expected `<= 0` sign, though shrunk from OLS's
+0.7631 by Ridge's regularization. This positive sign **survives** Ridge's
penalty; it isn't an artifact specific to unregularized OLS.

This was diagnosed in Phase 7 (`model/saved_model/linear_regression_notes.md`)
as a genuine, weak (`r=0.06`) small-sample confound in this specific 129-food
dataset -- higher-fiber items here skew toward whole grains that also
happen to be higher-GI (Bran Flakes, Weet-Bix, millet dishes, whole-wheat
breads) -- not a data-entry bug, and not something more data cleaning would
resolve. It is carried into the primary model **as a documented, known
limitation**, not something hidden or "fixed" by adjusting the formula.
Anyone handing this formula to a physician for a plausibility check should
be told this coefficient's sign is a known, investigated small-sample
artifact, not an unexamined red flag.

## Reversibility

This choice is not irreversible. Random forest's fitted results (CV-MAE,
per-fold MAE, feature importances) remain saved in
`model/saved_model/model_comparison.json` from Phase 9. Switching the
primary model later means re-running an export step against random forest
(or whichever model) instead of Ridge -- it does not require rebuilding the
data pipeline (Phases 1-6) or retraining from scratch.

## Files

- `coefficients.json` -- the exported primary model: Ridge's per-feature
  coefficients, intercept, and alpha, plus the exact prediction formula.
  This is what the website fetches.
- `linear_regression.json` / `linear_regression_notes.md` -- Phase 7's
  baseline OLS model and its fiber_g diagnostic write-up.
- `model_comparison.json` -- Phase 9's Ridge/Lasso/random forest CV results
  and feature coefficients/importances, including random forest's, kept for
  the reversibility path above.
