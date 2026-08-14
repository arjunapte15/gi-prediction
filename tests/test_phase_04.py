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

# Atkinson et al. 2021's standardized carbohydrate portion per food
# category, in grams. GL = GI/100 * category_carb_g -- this is what
# Atkinson's recorded GL actually encodes, independent of any specific
# food's nutrient density. See data/raw/south_asian_category_mapping.md.
CATEGORY_STANDARD_CARB_G = {
    "Cereal grains": 45,
    "Legumes": 15,
    "Breads": 15,
    "Snack foods and confectionery": 25,
    "Regional or traditional foods": 35,
}

# Per-food category assignment -- kept in sync with
# data/raw/south_asian_category_mapping.md (which documents the rationale
# for each one). Foods not listed in CEREAL_GRAINS/LEGUMES/BREADS/SNACKS
# default to "Regional or traditional foods".
CEREAL_GRAINS = {
    "Basmati rice, white, polished, cooked 10 min",
    "Basmati rice (Dreamrice)",
    "Basmati rice, white, boiled (Mahatma)",
    "Basmati rice, white, boiled (SunRice)",
    "Basmati rice (Laila)",
    "Unpolished little millet, plain cooked",
    "Unpolished foxtail millet, plain cooked",
    "Pilaf porridge, whole grain",
}
LEGUMES = {
    "Chickpeas, canned, drained",
    "Chickpeas (Garbanzo beans, Bengal gram), canned",
    "Lentils, brown, canned, drained",
    "Rajmah (kidney beans), boiled",
    "Lentils, Mothbean, sprouted, cooked in buttermilk",
}
BREADS = {"Roti (unleavened flatbread), whole wheat flour"}
SNACK_FOODS = {
    "Finger millet extruded snack",
    "Laddu (popped amaranth, foxtail millet, legume, fenugreek)",
}

# A plausible real-world serving weight range, wide enough not to false-flag
# legitimate recipe/portion variation but tight enough to catch a
# decomposition that's off by an order of magnitude.
PLAUSIBLE_SERVING_G = (15, 600)

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


def _category_of(name):
    if name in CEREAL_GRAINS:
        return "Cereal grains"
    if name in LEGUMES:
        return "Legumes"
    if name in BREADS:
        return "Breads"
    if name in SNACK_FOODS:
        return "Snack foods and confectionery"
    return "Regional or traditional foods"


def test_gl_implies_a_plausible_serving_weight():
    """Atkinson et al. 2021 compute GL from a category-specific STANDARDIZED
    carbohydrate portion, not from any particular food's actual nutrient
    density: GL = GI/100 * category_standard_carb_g. So GL is mathematically
    independent of our decomposed carbs_g, and directly comparing
    GI*carbs_g/100 against GL (the original version of this check) produces
    false positives whenever a food's standardized portion differs from
    100g of carbs -- which is nearly always, since the portions range from
    5g to 45g depending on category.

    A methodologically sound check instead asks: given our decomposed
    carbs_g (per 100g of cooked dish) and the food's category, what serving
    weight would contain the category's standardized carb amount? That's
    implied_weight_g = category_standard_carb_g / carbs_g_per_100g * 100.
    This is a plausibility check, not an exact-match check -- Atkinson's
    standardized portions are reference amounts for calculating GL, not a
    guarantee that any specific recipe's real serving size matches them.

    Also prints each food's implied serving weight next to its category's
    standard carb portion, as groundwork for Phase 11's meal parser (which
    will need typical serving-size assumptions to convert free-text meal
    descriptions into gram quantities).
    """
    gi_gl = _south_asian_gi_gl()
    rows = {row["food_name"]: row for row in _nutrient_rows()}
    lo, hi = PLAUSIBLE_SERVING_G
    failures = []
    checked = 0
    info_lines = []
    for name, row in sorted(rows.items()):
        if name in DOCUMENTED_EXCEPTION_DISHES:
            continue
        gi, gl = gi_gl[name]
        carbs = float(row["carbs_g"])
        category = _category_of(name)
        standard_carb_g = CATEGORY_STANDARD_CARB_G[category]
        assert carbs > 0, f"{name}: carbs_g must be > 0 to imply a serving weight"
        checked += 1
        implied_weight_g = standard_carb_g / carbs * 100
        info_lines.append(
            f"  {name} [{category}, {standard_carb_g}g standard carb]: "
            f"implied serving = {implied_weight_g:.1f}g (carbs_g/100g={carbs:.2f}, GI={gi:.0f}, GL={gl:.1f})"
        )
        if not (lo <= implied_weight_g <= hi):
            failures.append((name, category, implied_weight_g))
    assert checked > 0
    warnings.warn(
        "Implied serving weight per south_asian dish (category standard carb "
        f"portion / decomposed carbs_g), informational for Phase 11's meal "
        f"parser:\n" + "\n".join(info_lines)
    )
    assert not failures, (
        f"{len(failures)} south_asian dish(es) imply an implausible serving weight "
        f"(outside {lo}-{hi}g) given their category's standardized carb portion -- "
        "likely a genuine decomposition error, not just category-mapping uncertainty:\n"
        + "\n".join(f"  {name} [{category}]: {w:.1f}g" for name, category, w in failures)
    )
