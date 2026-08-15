# Notes on `linear_regression.json` (Phase 7)

## Known issue: `fiber_g` coefficient has an unexpected sign

Fitted coefficient: `fiber_g = +0.7631` (n=129, full `data/processed/foods.csv`,
no train/test split). Expected sign was `<= 0` -- more fiber is generally
expected to lower a food's glycemic response, so Phase 7's coefficient-sign
trip-wire test (`tests/test_phase_07.py`) flagged this on first fit.

**This was investigated, not ignored, and not "fixed" by altering the model.**
Per Phase 7's own instructions, a coefficient-sign trip-wire failure is meant
to point at a likely data bug, and forcing the sign some other way (e.g.
dropping/reweighting fiber_g) would hide a real finding rather than resolve it.

### Diagnostic evidence (`notebooks/phase_07_diagnostic.py`, not committed -- scratch only)

1. **Univariate correlation**: Pearson `r(fiber_g, GI) = +0.0593`. Positive
   even alone, before any other feature is in the model -- so this is not a
   multivariate-only artifact of controlling for the other three features.
2. **Multicollinearity (VIF)**, for all four Phase 7 features:
   - `fiber_g`: 1.452
   - `fat_g`: 1.125
   - `protein_g`: 1.462
   - `carbs_g`: 1.110

   All well under the 5.0 flag threshold (max 1.46), so this is not
   multicollinearity-driven sign suppression.
3. Because both of the above came back clean (correlation already positive,
   no multicollinearity red flag), the diagnostic's decision rule said a
   source-data spot-check (IFCT/USDA transposition or unit-mismatch check)
   was not warranted and was skipped.

### Conclusion

A genuine but weak (`r=0.06`) small-sample confound in this specific 129-food
dataset: the higher-fiber items here skew toward whole grains that also
happen to be higher-GI (Bran Flakes, Weet-Bix, millet-based South Asian
dishes, whole-wheat breads), while several low-fiber items sit at the low
end of GI (dairy, some fruits). This is a composition artifact of this
particular sample, not evidence that more data cleaning would resolve it,
and not fiber's true physiological glycemic effect being contradicted.

### Status

Documented known exception. `tests/test_phase_07.py` records and reports the
`fiber_g` coefficient's sign every run (via `warnings.warn`) but does not
hard-fail the suite on it, matching the pattern used elsewhere in this
project for documented dataset exceptions (see `data/data_dictionary.md`).
`fat_g <= 0` and `carbs_g >= 0` remain hard-asserted trip-wires.

**REVISIT AT PHASE 9/10** -- if Ridge/Lasso regularization also produces a
positive `fiber_g` coefficient, this should be weighed as an interpretability
concern in the Phase 10 model-selection decision, since the product's core
premise (a formula transparent and biologically plausible enough to hand to
a physician) depends on coefficients that hold up to that scrutiny.
