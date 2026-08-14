import csv
import json
import warnings
from pathlib import Path

FOODS_CSV = Path(__file__).resolve().parents[1] / "data" / "processed" / "foods.csv"
FOODS_JSON = Path(__file__).resolve().parents[1] / "data" / "processed" / "foods.json"

EXPECTED_COLUMNS = ["food_name", "cuisine", "fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g", "GI", "GL"]
FLOAT_COLUMNS = ["fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g", "GI", "GL"]

EXCLUDED_FOOD_NAMES = {
    "Arrowroot (Canna indica), with coconut",
    "Arrowroot (Maranta arundinacea), with coconut",
    "Jackfruit, with coconut and onion sambal",
    "Lentil and cauliflower curry with rice",
    "Lentil curry, with wholemeal bread",
    "Manioc (cassava), with coconut sambol",
    "Red rice, with lentil curry, salad, egg, coconut gravy",
    "Yam (Dioscorea alata), white, with coconut",
    "Mango dessert, prepared (Nestlé)",
}

# The 8 hand-added North Indian dishes (Phase 2 amendment) plus Dal makhani
# and Chana masala are not sourced from Atkinson et al. at all, so they have
# no Atkinson category to check GL plausibility against.
DOCUMENTED_EXCEPTION_DISHES = {
    "Butter chicken",
    "Tandoori chicken",
    "Chicken tikka masala",
    "Chicken curry (generic)",
    "Butter paneer (paneer makhani)",
    "Palak paneer",
    "Dal makhani",
    "Chana masala",
}

# Atkinson et al. 2021's standardized carbohydrate portion per food
# category, in grams. GL = GI/100 * category_standard_carb_g -- see
# data/data_dictionary.md's "GL methodology" section and
# data/raw/south_asian_category_mapping.md / american_category_mapping.md.
CATEGORY_STANDARD_CARB_G = {
    "Cereal grains": 45,
    "Legumes": 15,
    "Breads": 15,
    "Snack foods and confectionery": 25,
    "Regional or traditional foods": 35,
    "Breakfast cereals": 20,
    "Bakery products": 30,
    "Vegetables": 20,
    "Vegetables (low-carb exception)": 10,
    "Dairy products and alternatives (plain)": 10,
    "Dairy products and alternatives (flavored)": 20,
    "Fruit and fruit products": 15,
    "Fruit and vegetable juices": 20,
    "Sugars and syrups": 5,
    "Soups": 20,
}

# South Asian category assignment, kept in sync with
# data/raw/south_asian_category_mapping.md. Amendment: "Rajmah (kidney
# beans), boiled" was verified against the real Atkinson supplemental
# tables and moved out of SOUTH_ASIAN_LEGUMES (it now falls through to the
# default "Regional or traditional foods" in _south_asian_category below) --
# see that file's "Amendment: additional spot-checks" section.
SOUTH_ASIAN_CEREAL_GRAINS = {
    "Basmati rice, white, polished, cooked 10 min",
    "Basmati rice (Dreamrice)",
    "Basmati rice, white, boiled (Mahatma)",
    "Basmati rice, white, boiled (SunRice)",
    "Basmati rice (Laila)",
    "Unpolished little millet, plain cooked",
    "Unpolished foxtail millet, plain cooked",
    "Pilaf porridge, whole grain",
}
SOUTH_ASIAN_LEGUMES = {
    "Chickpeas, canned, drained",
    "Chickpeas (Garbanzo beans, Bengal gram), canned",
    "Lentils, brown, canned, drained",
    "Lentils, Mothbean, sprouted, cooked in buttermilk",
}
SOUTH_ASIAN_BREADS = {"Roti (unleavened flatbread), whole wheat flour"}
SOUTH_ASIAN_SNACK_FOODS = {
    "Finger millet extruded snack",
    "Laddu (popped amaranth, foxtail millet, legume, fenugreek)",
}

# American category assignment, kept in sync with
# data/raw/american_category_mapping.md. Amendment: this mapping was
# rebuilt from the real Atkinson supplemental tables (previously judgment-
# matched only). One correction resulted: "Soft pretzel, wheat" moved from
# AMERICAN_SNACK_FOODS to AMERICAN_BREADS (Atkinson item #208 places it in
# a Pretzels subsection of Breads, not Snack foods and confectionery).
AMERICAN_BREADS = {
    "White bread",
    "Burger Buns, 100% Whole wheat",
    "Rye bread, Pumpernickel",
    "Multigrain bread, gluten-free",
    "Multigrain batch bread",
    "White sourdough bread, gluten free",
    "Oat bran concentrate bread",
    "Fruit and Muesli bread (Bürgen)",
    "Muesli bread (packet mix)",
    "Mixed Grain bread roll (Bürgen)",
    "Soft pretzel, wheat",
}
AMERICAN_BREAKFAST_CEREALS = {
    "Oats, rolled, uncooked",
    "Weet-Bix breakfast biscuit",
    "Rice Bubbles (Kellogg's)",
    "Cornflakes",
    "Bran Flakes (Kellogg's)",
}
AMERICAN_BAKERY_PRODUCTS = {
    "Doughnut",
    "Chocolate cake (Betty Crocker)",
    "Danish Pastry, Apple and Peach",
    "Apple Blueberry muffin",
    "Banana, oat and honey muffin",
    "Cranberry Raisin muffin",
    "Apricot, coconut and honey muffin",
    "Pizza base, oven-baked (Boboli)",
}
AMERICAN_VEGETABLES_STANDARD = {
    "French Fries, baked (OreIda)",
    "Sweet corn, cooked in microwave",
}
AMERICAN_VEGETABLES_LOW_CARB_EXCEPTION = {
    "Carrots, unpeeled, boiled",
    "Carrots, diced, frozen",
    "Peas, plain and frozen",
}
AMERICAN_SNACK_FOODS = {
    "Cheddar Cheese Crackers (Combos)",
    "Cheddar Cheese Pretzels (Combos)",
    "Microwave popcorn, butter flavor",
    "Cheese Puffs, rice and corn (Pirate's Booty)",
    "Peanut Butter Granola bars (Kudos)",
    "Chocolate covered almonds (Cocoavia)",
}
AMERICAN_DAIRY_FLAVORED = {
    "Ice cream, premium chocolate, 15% fat",
    "Yoghurt, Greek style, honey topped",
    "Yoghurt, black cherry",
    "Yoghurt, bourbon vanilla",
}
AMERICAN_DAIRY_PLAIN = {
    "Milk, reduced fat",
    "Yoghurt, natural, no added sugar",
}
AMERICAN_FRUIT_PRODUCTS = {
    "Custard apple, raw",
    "Pineapple, raw",
    "Grapes, Crimson seedless",
    "Grapes, green, Menidee, seedless",
    "Watermelon, raw",
    "Raisins",
    "Strawberries, fresh, raw",
    "Fruit Salad, canned (peach/pear/apricot/pineapple/cherry)",
    "Apricot fruit spread, no added sugar",
    "Apricot fruit spread (Cottees)",
}
AMERICAN_JUICES = {
    "Orange juice",
    "Apple juice, unsweetened",
}
AMERICAN_LEGUMES = {
    "Hommus dip",
    "Baked Beans in Cheesy Tomato sauce (Heinz)",
    "Baked Beans in Barbecue sauce (Heinz)",
    "Baked Beans in Tomato sauce (Heinz)",
}
AMERICAN_SUGARS_AND_SYRUPS = {
    "Manuka honey MGO 440+",
    "Capilano Premium Honey",
    "Maple syrup, pure Canadian",
}
AMERICAN_CEREAL_GRAINS = {"Brown rice, instant (Uncle Ben's)"}
AMERICAN_SOUPS = {
    "Tomato soup, condensed, prepared with water (Campbell's)",
    "Chunky Roast Chicken and Vegetable soup (Campbell's)",
}

# A plausible real-world serving weight range. The lower bound is 5g (not
# Phase 4's 15g) because this phase adds the "Sugars and syrups" category
# (honey, maple syrup): its 5g standardized portion combined with these
# foods' very high carb density legitimately implies a ~6-7g serving
# (roughly a teaspoon), which isn't a decomposition error. See
# data/data_dictionary.md's "GL methodology" section.
PLAUSIBLE_SERVING_G = (5, 600)


def _read_csv_rows():
    with open(FOODS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _read_json_rows():
    with open(FOODS_JSON, encoding="utf-8") as f:
        return json.load(f)


def test_files_exist():
    assert FOODS_CSV.exists()
    assert FOODS_JSON.exists()


def test_schema_exact_columns():
    rows = _read_csv_rows()
    assert rows, "foods.csv must not be empty"
    assert list(rows[0].keys()) == EXPECTED_COLUMNS


def test_schema_dtypes():
    rows = _read_json_rows()
    assert rows, "foods.json must not be empty"
    for row in rows:
        assert isinstance(row["food_name"], str)
        assert isinstance(row["cuisine"], str)
        for col in FLOAT_COLUMNS:
            assert isinstance(row[col], (int, float)), f"{row['food_name']}.{col} is not numeric"


def test_gi_in_valid_range():
    rows = _read_json_rows()
    for row in rows:
        assert 0 <= row["GI"] <= 110, f"{row['food_name']}: GI={row['GI']} out of [0,110]"


def test_row_count_in_expected_range():
    rows = _read_json_rows()
    assert 111 <= len(rows) <= 141, f"expected 111-141 rows, got {len(rows)}"


def test_no_nulls_in_required_columns():
    rows = _read_csv_rows()
    for row in rows:
        for col in EXPECTED_COLUMNS:
            assert row[col] is not None and row[col].strip() != "", f"{row['food_name']}.{col} is null/empty"


def test_neither_cuisine_under_30_percent():
    rows = _read_json_rows()
    total = len(rows)
    counts = {}
    for row in rows:
        counts[row["cuisine"]] = counts.get(row["cuisine"], 0) + 1
    for cuisine, count in counts.items():
        fraction = count / total
        assert fraction >= 0.30, f"{cuisine} is only {fraction:.1%} of rows, under the 30% floor"


def test_excluded_foods_do_not_appear():
    rows = _read_json_rows()
    names = {row["food_name"] for row in rows}
    overlap = names & EXCLUDED_FOOD_NAMES
    assert not overlap, f"excluded foods leaked into the merged output: {overlap}"


def _south_asian_category(name):
    if name in SOUTH_ASIAN_CEREAL_GRAINS:
        return "Cereal grains"
    if name in SOUTH_ASIAN_LEGUMES:
        return "Legumes"
    if name in SOUTH_ASIAN_BREADS:
        return "Breads"
    if name in SOUTH_ASIAN_SNACK_FOODS:
        return "Snack foods and confectionery"
    return "Regional or traditional foods"


def _american_category(name):
    if name in AMERICAN_BREADS:
        return "Breads"
    if name in AMERICAN_BREAKFAST_CEREALS:
        return "Breakfast cereals"
    if name in AMERICAN_BAKERY_PRODUCTS:
        return "Bakery products"
    if name in AMERICAN_VEGETABLES_STANDARD:
        return "Vegetables"
    if name in AMERICAN_VEGETABLES_LOW_CARB_EXCEPTION:
        return "Vegetables (low-carb exception)"
    if name in AMERICAN_SNACK_FOODS:
        return "Snack foods and confectionery"
    if name in AMERICAN_DAIRY_FLAVORED:
        return "Dairy products and alternatives (flavored)"
    if name in AMERICAN_DAIRY_PLAIN:
        return "Dairy products and alternatives (plain)"
    if name in AMERICAN_FRUIT_PRODUCTS:
        return "Fruit and fruit products"
    if name in AMERICAN_JUICES:
        return "Fruit and vegetable juices"
    if name in AMERICAN_LEGUMES:
        return "Legumes"
    if name in AMERICAN_SUGARS_AND_SYRUPS:
        return "Sugars and syrups"
    if name in AMERICAN_CEREAL_GRAINS:
        return "Cereal grains"
    if name in AMERICAN_SOUPS:
        return "Soups"
    raise AssertionError(f"{name}: no category assignment found in american_category_mapping.md sets")


def test_gl_implies_a_plausible_serving_weight_both_cuisines():
    """Atkinson et al. 2021 compute GL from a category-specific STANDARDIZED
    carbohydrate portion, not from any particular food's actual nutrient
    density: GL = GI/100 * category_standard_carb_g. A methodologically
    sound plausibility check asks: given this dataset's carbs_g (per 100g)
    and the food's category, what serving weight would contain the
    category's standardized carb amount? implied_weight_g =
    category_standard_carb_g / carbs_g_per_100g * 100. See
    data/data_dictionary.md's "GL methodology" section for the full
    rationale, and Phase 4's south_asian-only version of this check.

    Runs across both cuisines now that both have category mappings
    (data/raw/south_asian_category_mapping.md and
    data/raw/american_category_mapping.md), excluding the 9 documented
    non-Atkinson exception dishes.
    """
    rows = {row["food_name"]: row for row in _read_json_rows()}
    lo, hi = PLAUSIBLE_SERVING_G
    failures = []
    checked = 0
    info_lines = []
    for name, row in sorted(rows.items()):
        if name in DOCUMENTED_EXCEPTION_DISHES:
            continue
        carbs = row["carbs_g"]
        if row["cuisine"] == "south_asian":
            category = _south_asian_category(name)
        else:
            category = _american_category(name)
        standard_carb_g = CATEGORY_STANDARD_CARB_G[category]
        assert carbs > 0, f"{name}: carbs_g must be > 0 to imply a serving weight"
        checked += 1
        implied_weight_g = standard_carb_g / carbs * 100
        info_lines.append(
            f"  {name} [{row['cuisine']}/{category}, {standard_carb_g}g standard carb]: "
            f"implied serving = {implied_weight_g:.1f}g (carbs_g/100g={carbs:.2f}, GI={row['GI']:.0f}, GL={row['GL']:.1f})"
        )
        if not (lo <= implied_weight_g <= hi):
            failures.append((name, category, implied_weight_g))
    assert checked > 0
    warnings.warn(
        "Implied serving weight per dish (category standard carb portion / "
        f"decomposed carbs_g), across both cuisines:\n" + "\n".join(info_lines)
    )
    assert not failures, (
        f"{len(failures)} dish(es) imply an implausible serving weight "
        f"(outside {lo}-{hi}g) given their category's standardized carb portion:\n"
        + "\n".join(f"  {name} [{category}]: {w:.1f}g" for name, category, w in failures)
    )
