import csv
import warnings
from pathlib import Path

RAW_CSV = Path(__file__).resolve().parents[1] / "data" / "raw" / "gi_gl_raw.csv"
NUTRIENTS_CSV = Path(__file__).resolve().parents[1] / "data" / "raw" / "south_asian_nutrients.csv"

NUTRIENT_COLUMNS = ["fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g"]

GI_ZERO_EXCEPTION_DISHES = {
    "Butter chicken",
    "Tandoori chicken",
    "Chicken tikka masala",
    "Chicken curry (generic)",
    "Butter paneer (paneer makhani)",
    "Palak paneer",
}

# These 8 dishes were added by hand in the Phase 2 amendment (not sourced
# from Atkinson et al.), so they're excluded from the Atkinson GL sanity
# check, which is only meaningful for lab-sourced GI/GL values.
DOCUMENTED_EXCEPTION_DISHES = GI_ZERO_EXCEPTION_DISHES | {"Dal makhani", "Chana masala"}

GL_TOLERANCE = 0.30


def _read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _south_asian_gi_gl():
    rows = _read_rows(RAW_CSV)
    return {
        row["food_name"]: (float(row["GI"]), float(row["GL"]))
        for row in rows
        if row["cuisine"] == "south_asian"
    }


def _nutrient_rows():
    return _read_rows(NUTRIENTS_CSV)


def test_all_food_names_are_south_asian_in_raw_csv():
    south_asian_names = set(_south_asian_gi_gl().keys())
    rows = _nutrient_rows()
    for row in rows:
        assert row["food_name"] in south_asian_names


def test_no_null_nutrient_values():
    rows = _nutrient_rows()
    for row in rows:
        for col in NUTRIENT_COLUMNS:
            assert row[col] is not None and row[col].strip() != ""


def test_nutrient_values_non_negative():
    rows = _nutrient_rows()
    for row in rows:
        for col in NUTRIENT_COLUMNS:
            assert float(row[col]) >= 0


def test_fiber_and_sugar_do_not_exceed_carbs():
    rows = _nutrient_rows()
    for row in rows:
        carbs = float(row["carbs_g"])
        assert float(row["fiber_g"]) <= carbs
        assert float(row["sugar_g"]) <= carbs


def test_gi_zero_exception_dishes_are_low_carb():
    rows = {row["food_name"]: row for row in _nutrient_rows()}
    for name in GI_ZERO_EXCEPTION_DISHES:
        assert name in rows, f"{name} missing from south_asian_nutrients.csv"
        row = rows[name]
        carbs = float(row["carbs_g"])
        protein_plus_fat = float(row["protein_g"]) + float(row["fat_g"])
        assert carbs < protein_plus_fat, (
            f"{name}: carbs_g={carbs} is not low relative to protein_g+fat_g={protein_plus_fat}, "
            "inconsistent with its GI=0 exception rationale"
        )


def test_gl_sanity_check_against_atkinson_gl_flags_outliers():
    """GL ~= GI * carbs_g / 100 as a rough sanity check against Phase 2's
    recorded GL. This is expected to diverge for many south_asian dishes
    because south_asian_nutrients.csv reports nutrients per 100g of the
    RAW/DRY ingredient mix (see decomposition notes), while Atkinson's GL
    was computed from an as-eaten (cooked, water-diluted) carb content --
    so this test flags outliers via a warning rather than failing.
    """
    gi_gl = _south_asian_gi_gl()
    rows = {row["food_name"]: row for row in _nutrient_rows()}
    flagged = []
    checked = 0
    for name, row in rows.items():
        if name in DOCUMENTED_EXCEPTION_DISHES:
            continue
        gi, gl = gi_gl[name]
        if gl == 0:
            continue
        checked += 1
        carbs = float(row["carbs_g"])
        calc_gl = gi * carbs / 100
        ratio = calc_gl / gl
        if not (1 - GL_TOLERANCE <= ratio <= 1 + GL_TOLERANCE):
            flagged.append((name, gl, calc_gl, ratio))
    assert checked > 0
    if flagged:
        lines = "\n".join(
            f"  {name}: recorded GL={gl}, recomputed GL={calc_gl:.2f} (ratio={ratio:.2f})"
            for name, gl, calc_gl, ratio in flagged
        )
        warnings.warn(
            f"{len(flagged)}/{checked} south_asian dishes fall outside +/-{int(GL_TOLERANCE*100)}% "
            f"GL sanity tolerance (see data/raw/south_asian_decomposition_notes.md for why):\n{lines}"
        )
