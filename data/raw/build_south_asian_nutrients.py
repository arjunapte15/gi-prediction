"""
Builds data/raw/south_asian_nutrients.csv from IFCT 2017 raw-ingredient values
(data/raw/IFCT2017.pdf) plus published nutrition values for a few dairy/meat
ingredients IFCT lacks, combined with the recipe proportions documented in
data/raw/south_asian_decomposition_notes.md.

All nutrient values are expressed per 100g of the food's raw/dry ingredient
mix (not per 100g of the cooked, water-diluted finished dish) -- see the
decomposition notes for why. For composite dishes this is a mass-weighted
average of the per-100g values of the ingredients that go into the dish, so
only ingredient MASS RATIOS matter, not absolute serving size.

Re-running this script regenerates south_asian_nutrients.csv and the
data/raw/recipe_breakdowns/*.json files from the INGREDIENTS/DISHES tables
below.
"""
import csv
import json
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent
BREAKDOWN_DIR = RAW_DIR / "recipe_breakdowns"

NUTRIENT_KEYS = ["fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g"]

# Per-100g nutrient values for raw/dry ingredients.
# IFCT-sourced values cite the IFCT 2017 food code (e.g. "A015").
# Non-IFCT values (chicken avg, butter, ghee, cream, yogurt, honey, oil) are
# cited as "published" -- see decomposition notes for exact source/values.
INGREDIENTS = {
    # cereals / millets / flours (Table 1 code)
    "rice_milled":       {"source": "IFCT A015 Rice, raw, milled",            "fiber_g": 2.81,  "fat_g": 0.52,  "protein_g": 7.94,  "carbs_g": 78.24, "sugar_g": 0.69},
    "rice_brown":        {"source": "IFCT A013 Rice, raw, brown",             "fiber_g": 4.43,  "fat_g": 1.24,  "protein_g": 9.16,  "carbs_g": 74.80, "sugar_g": 0.69},
    "rice_parboiled":    {"source": "IFCT A014 Rice, parboiled, milled",      "fiber_g": 3.74,  "fat_g": 0.55,  "protein_g": 7.81,  "carbs_g": 77.16, "sugar_g": 0.67},
    "rice_flakes":       {"source": "IFCT A011 Rice flakes (poha)",           "fiber_g": 3.46,  "fat_g": 1.14,  "protein_g": 7.44,  "carbs_g": 76.75, "sugar_g": 0.34},
    "little_millet":     {"source": "IFCT A016 Samai (Panicum miliare)",      "fiber_g": 7.72,  "fat_g": 3.89,  "protein_g": 10.13, "carbs_g": 65.55, "sugar_g": 0.37},
    "foxtail_millet":    {"source": "IFCT A017 Varagu (see caveat: labelled Paspalum scrobiculatum in Table 1 but Setaria italica in Table 6)", "fiber_g": 6.39, "fat_g": 2.55, "protein_g": 8.92, "carbs_g": 66.19, "sugar_g": 1.29},
    "wheat_flour_refined": {"source": "IFCT A018 Wheat flour, refined (maida)", "fiber_g": 2.76, "fat_g": 0.76, "protein_g": 10.36, "carbs_g": 74.27, "sugar_g": 1.79},
    "wheat_flour_atta":   {"source": "IFCT A019 Wheat flour, atta",           "fiber_g": 11.36, "fat_g": 1.53,  "protein_g": 10.57, "carbs_g": 64.17, "sugar_g": 1.80},
    "wheat_whole":        {"source": "IFCT A020 Wheat, whole",                "fiber_g": 11.23, "fat_g": 1.47,  "protein_g": 10.59, "carbs_g": 64.72, "sugar_g": 1.77},
    "wheat_bulgur":       {"source": "IFCT A021 Wheat, bulgur (broken wheat proxy)", "fiber_g": 8.81, "fat_g": 1.45, "protein_g": 10.84, "carbs_g": 69.06, "sugar_g": 1.20},
    "semolina":           {"source": "IFCT A022 Wheat, semolina (rava)",      "fiber_g": 9.72,  "fat_g": 0.74,  "protein_g": 11.38, "carbs_g": 68.43, "sugar_g": 1.65},
    "ragi":               {"source": "IFCT A010 Ragi (finger millet, whole)", "fiber_g": 11.18, "fat_g": 1.92,  "protein_g": 7.16,  "carbs_g": 66.82, "sugar_g": 0.34},
    "amaranth_seed":      {"source": "IFCT A001 Amaranth seed, black",        "fiber_g": 7.02,  "fat_g": 5.74,  "protein_g": 14.59, "carbs_g": 59.98, "sugar_g": 0.88},

    # legumes (Table 1 code)
    "bengal_gram_dal":    {"source": "IFCT B001 Bengal gram, dal (used for both chana dal and besan/gram flour)", "fiber_g": 15.15, "fat_g": 5.31, "protein_g": 21.55, "carbs_g": 46.72, "sugar_g": 1.03},
    "bengal_gram_whole":  {"source": "IFCT B002 Bengal gram, whole (chickpea/garbanzo proxy)", "fiber_g": 25.22, "fat_g": 5.11, "protein_g": 18.77, "carbs_g": 39.56, "sugar_g": 0.99},
    "urad_dal":           {"source": "IFCT B003 Black gram, dal (urad dal)",  "fiber_g": 11.93, "fat_g": 1.69,  "protein_g": 23.06, "carbs_g": 51.00, "sugar_g": 0.84},
    "urad_whole":         {"source": "IFCT B004 Black gram, whole (whole urad)", "fiber_g": 20.41, "fat_g": 1.58, "protein_g": 21.97, "carbs_g": 43.99, "sugar_g": 0.94},
    "moong_dal":          {"source": "IFCT B010 Green gram, dal (moong dal)", "fiber_g": 9.37,  "fat_g": 1.35,  "protein_g": 23.88, "carbs_g": 52.59, "sugar_g": 0.95},
    "lentil_brown":       {"source": "IFCT B014 Lentil whole, brown (masoor)", "fiber_g": 16.82, "fat_g": 0.64, "protein_g": 22.49, "carbs_g": 48.47, "sugar_g": 1.63},
    "moth_bean":          {"source": "IFCT B016 Moth bean",                   "fiber_g": 15.12, "fat_g": 1.76,  "protein_g": 19.75, "carbs_g": 52.09, "sugar_g": 1.36},
    "rajmah_red":         {"source": "IFCT B020 Rajmah, red (kidney beans)",  "fiber_g": 16.57, "fat_g": 1.77,  "protein_g": 19.91, "carbs_g": 48.61, "sugar_g": 1.52},
    "toor_dal":           {"source": "IFCT B021 Red gram, dal (toor/arhar dal, for sambar)", "fiber_g": 9.06, "fat_g": 1.56, "protein_g": 21.70, "carbs_g": 55.23, "sugar_g": 2.08},
    "soybean":            {"source": "IFCT B024 Soybean, brown (soy flour proxy)", "fiber_g": 21.55, "fat_g": 19.82, "protein_g": 35.58, "carbs_g": 12.79, "sugar_g": 2.51},

    # vegetables / spices (Table 1 code)
    "spinach":            {"source": "IFCT C033 Spinach",                     "fiber_g": 2.38,  "fat_g": 0.64,  "protein_g": 2.14,  "carbs_g": 2.05,  "sugar_g": 0.24},
    "fenugreek_seeds":    {"source": "IFCT G026 Fenugreek seeds",             "fiber_g": 47.55, "fat_g": 5.72,  "protein_g": 25.41, "carbs_g": 10.57, "sugar_g": 0.55},
    "radish":             {"source": "IFCT F010 Radish, elongate, white skin", "fiber_g": 2.65, "fat_g": 0.15,  "protein_g": 0.77,  "carbs_g": 6.56,  "sugar_g": 0.95},
    "onion":              {"source": "IFCT G017 Onion, big",                  "fiber_g": 2.45,  "fat_g": 0.24,  "protein_g": 1.50,  "carbs_g": 9.56,  "sugar_g": 5.88},
    "tomato":             {"source": "IFCT D076 Tomato, ripe, local",         "fiber_g": 1.77,  "fat_g": 0.47,  "protein_g": 0.90,  "carbs_g": 2.71,  "sugar_g": 1.34},
    "potato":             {"source": "IFCT F006 Potato, brown skin, big",     "fiber_g": 1.71,  "fat_g": 0.23,  "protein_g": 1.54,  "carbs_g": 14.89, "sugar_g": 0.32},
    "chili_red":          {"source": "IFCT G022 Chillies, red (chili powder proxy)", "fiber_g": 31.15, "fat_g": 6.40, "protein_g": 12.69, "carbs_g": 29.46, "sugar_g": 4.70},
    "coconut_fresh":      {"source": "IFCT H007 Coconut, kernel, fresh",      "fiber_g": 10.42, "fat_g": 41.38, "protein_g": 3.84,  "carbs_g": 6.30,  "sugar_g": 6.20},
    "groundnut":          {"source": "IFCT H012 Ground nut (peanut)",         "fiber_g": 10.38, "fat_g": 39.63, "protein_g": 23.65, "carbs_g": 17.27, "sugar_g": 4.42},
    "jaggery":            {"source": "IFCT I001 Jaggery, cane",               "fiber_g": 0.0,   "fat_g": 0.16,  "protein_g": 1.85,  "carbs_g": 84.87, "sugar_g": 84.32},

    # animal products
    "paneer":             {"source": "IFCT L003 Paneer",                      "fiber_g": 0.0,   "fat_g": 24.78, "protein_g": 18.86, "carbs_g": 2.41, "sugar_g": 2.41},
    "egg":                {"source": "IFCT M001 Egg, poultry, whole, raw",    "fiber_g": 0.0,   "fat_g": 9.15,  "protein_g": 13.28, "carbs_g": 0.0,   "sugar_g": 0.0},
    "chicken":             {"source": "IFCT N001-N004 average (Chicken, poultry, leg/thigh/breast/wing, skinless)", "fiber_g": 0.0, "fat_g": 12.42, "protein_g": 19.21, "carbs_g": 0.0, "sugar_g": 0.0},

    # not in IFCT with sufficient detail -- published (USDA FoodData Central
    # typical values, retrieved 2026-08-13, see decomposition notes)
    "butter":             {"source": "published (USDA FDC, salted butter)",   "fiber_g": 0.0,   "fat_g": 82.2,  "protein_g": 0.85, "carbs_g": 0.06, "sugar_g": 0.06},
    "ghee":               {"source": "published (USDA FDC, ghee/clarified butter)", "fiber_g": 0.0, "fat_g": 99.5, "protein_g": 0.3, "carbs_g": 0.0,  "sugar_g": 0.0},
    "cream":              {"source": "published (USDA FDC, heavy cream, ~36% fat)", "fiber_g": 0.0, "fat_g": 36.0, "protein_g": 2.1,  "carbs_g": 2.8,  "sugar_g": 2.8},
    "yogurt":             {"source": "published (USDA FDC, plain whole-milk yogurt)", "fiber_g": 0.0, "fat_g": 4.5, "protein_g": 3.9,  "carbs_g": 5.6,  "sugar_g": 4.7},
    "honey":               {"source": "published (USDA FDC, honey)",         "fiber_g": 0.2,   "fat_g": 0.0,   "protein_g": 0.3,  "carbs_g": 82.4, "sugar_g": 82.1},
    "veg_oil":             {"source": "published (generic vegetable oil)",   "fiber_g": 0.0,   "fat_g": 100.0, "protein_g": 0.0,  "carbs_g": 0.0,  "sugar_g": 0.0},

    # approximated components (see decomposition notes)
    "coconut_chutney":     {"source": "approximated as fresh coconut (chutney's dominant ingredient by mass; onion/chili/lime treated as negligible)", "fiber_g": 10.42, "fat_g": 41.38, "protein_g": 3.84, "carbs_g": 6.30, "sugar_g": 6.20},
}

# grams per common measure -- see decomposition notes for rationale.
G = {
    "cup_rice": 190, "cup_millet": 190, "cup_dal": 200, "cup_flour": 120,
    "cup_semolina": 165, "cup_bulgur": 170, "cup_coconut": 80, "cup_onion": 150,
    "cup_tomato": 180, "cup_yogurt": 245, "cup_cream": 240, "cup_poha": 80,
    "tbsp_fat": 14, "tbsp_dal": 12, "tbsp_flour": 8, "tbsp_peanut": 9,
    "tbsp_honey": 20, "tsp_fat": 5, "tsp_dal": 3,
    "medium_onion": 110, "medium_tomato": 123, "medium_potato": 150, "egg": 50,
}


def _weighted(parts):
    """parts: list of (ingredient_key, grams). Returns per-100g nutrient dict."""
    total_g = sum(g for _, g in parts)
    out = {}
    for key in NUTRIENT_KEYS:
        out[key] = round(sum(INGREDIENTS[ing][key] * g for ing, g in parts) / total_g, 2)
    return out, total_g


# Composite dishes: food_name -> list of (ingredient_key, grams, note)
DISHES = {
    "Rice dosa": [
        ("rice_milled", 3 * G["cup_rice"], "3 cups rice"),
        ("urad_dal", 1 * G["cup_dal"], "1 cup urad dal"),
    ],
    "Dosa, rice and black gram dhal": [
        ("rice_milled", 3 * G["cup_rice"], "3 cups rice"),
        ("urad_dal", 1 * G["cup_dal"], "1 cup urad dal"),
    ],
    "Dosai (parboiled and raw rice), with chutney": [
        ("rice_milled", 3 * G["cup_rice"], "3 cups rice"),
        ("urad_dal", 1 * G["cup_dal"], "1 cup urad dal"),
        ("coconut_chutney", 18, "chutney side, ~18g"),
    ],
    "Dosa, foxtail millet and black gram dhal": [
        ("foxtail_millet", 3 * G["cup_millet"], "3 cups foxtail millet"),
        ("urad_dal", 1 * G["cup_dal"], "1 cup urad dal"),
    ],
    "Rice idli (commercial dry mix)": [
        ("rice_milled", 4 * G["cup_rice"], "4 cups rice"),
        ("urad_dal", 1 * G["cup_dal"], "1 cup urad dal"),
    ],
    "Idli, brown, parboiled rice and black gram dhal, with sambar": [
        ("rice_parboiled", 4 * G["cup_rice"], "4 cups parboiled rice"),
        ("urad_dal", 1 * G["cup_dal"], "1 cup urad dal"),
        ("toor_dal", 15, "sambar dal, dry-equivalent ~15g"),
        ("tomato", 10, "sambar vegetable, ~10g tomato-equivalent"),
    ],
    "Idli (parboiled and raw rice, black dhal), with chutney": [
        ("rice_parboiled", 4 * G["cup_rice"], "4 cups parboiled rice"),
        ("urad_dal", 1 * G["cup_dal"], "1 cup urad dal"),
        ("coconut_chutney", 18, "chutney side, ~18g"),
    ],
    "Upma": [
        ("semolina", 1 * G["cup_semolina"], "1 cup semolina/rava"),
        ("ghee", 2 * G["tbsp_fat"], "2 tbsp oil/ghee"),
        ("urad_dal", 1 * G["tsp_dal"], "1 tsp urad dal tempering"),
        ("bengal_gram_dal", 1 * G["tsp_dal"], "1 tsp chana dal tempering"),
    ],
    "Finger millet upma": [
        ("ragi", 1 * G["cup_flour"], "1 cup ragi flour"),
        ("ghee", 2 * G["tbsp_fat"], "2 tbsp oil/ghee"),
        ("urad_dal", 1 * G["tsp_dal"], "1 tsp urad dal tempering"),
        ("bengal_gram_dal", 1 * G["tsp_dal"], "1 tsp chana dal tempering"),
    ],
    "Finger millet flakes upma": [
        ("ragi", 1 * G["cup_flour"], "1 cup ragi flakes (flour composition used, see notes)"),
        ("ghee", 2 * G["tbsp_fat"], "2 tbsp oil/ghee"),
        ("urad_dal", 1 * G["tsp_dal"], "1 tsp urad dal tempering"),
        ("bengal_gram_dal", 1 * G["tsp_dal"], "1 tsp chana dal tempering"),
    ],
    "Finger millet vermicelli upma": [
        ("ragi", 1 * G["cup_flour"], "1 cup ragi vermicelli (flour composition used, see notes)"),
        ("ghee", 2 * G["tbsp_fat"], "2 tbsp oil/ghee"),
        ("urad_dal", 1 * G["tsp_dal"], "1 tsp urad dal tempering"),
        ("bengal_gram_dal", 1 * G["tsp_dal"], "1 tsp chana dal tempering"),
    ],
    "Broken wheat upma, with green gram, chutney": [
        ("wheat_bulgur", 1 * G["cup_bulgur"], "1 cup broken wheat/daliya"),
        ("ghee", 2 * G["tbsp_fat"], "2 tbsp oil/ghee"),
        ("urad_dal", 1 * G["tsp_dal"], "1 tsp urad dal tempering"),
        ("bengal_gram_dal", 1 * G["tsp_dal"], "1 tsp chana dal tempering"),
        ("moong_dal", G["cup_bulgur"] / 4, "green gram, ~1:4 ratio to grain"),
        ("coconut_chutney", 18, "chutney side, ~18g"),
    ],
    "Upittu, roasted semolina and onions": [
        ("semolina", 1 * G["cup_semolina"], "1 cup semolina/rava"),
        ("ghee", 2 * G["tbsp_fat"], "2 tbsp oil/ghee"),
        ("onion", G["medium_onion"], "1 medium onion"),
        ("urad_dal", 1 * G["tsp_dal"], "1 tsp urad dal tempering"),
        ("bengal_gram_dal", 1 * G["tsp_dal"], "1 tsp chana dal tempering"),
    ],
    "Dhokla, chickpea and wheat semolina": [
        ("bengal_gram_dal", 1.5 * G["cup_flour"], "1.5 cups besan"),
        ("yogurt", 0.75 * G["cup_yogurt"], "0.75 cup yogurt"),
        ("semolina", 2 * (G["cup_semolina"] / 48), "2 tsp semolina"),
    ],
    "Dhokla, parboiled rice, Bengal gram, green gram, with chutney": [
        ("rice_parboiled", 1 * G["cup_rice"], "1 cup parboiled rice"),
        ("bengal_gram_dal", 1 * G["cup_dal"], "1 cup Bengal gram dal"),
        ("moong_dal", 1 * G["cup_dal"], "1 cup green gram dal"),
        ("coconut_chutney", 18, "chutney side, ~18g"),
    ],
    "Poha, rice flakes with ground nuts": [
        ("rice_flakes", 1 * G["cup_poha"], "1 cup poha"),
        ("groundnut", 3 * G["tbsp_peanut"], "3 tbsp peanuts"),
        ("veg_oil", 1 * G["tbsp_fat"], "1 tbsp oil"),
    ],
    "Pongal, rice and roasted green gram dhal": [
        ("rice_milled", 1.5 * G["cup_rice"], "1.5 cups rice"),
        ("moong_dal", 1 * G["cup_dal"], "1 cup moong dal"),
        ("ghee", 2.5 * G["tbsp_fat"], "2.5 tbsp ghee"),
    ],
    "Cheela, bengal gram": [("bengal_gram_dal", 100, "100% besan basis")],
    "Cheela, bengal gram, fermented batter": [("bengal_gram_dal", 100, "100% besan basis, fermented (macros unchanged)")],
    "Cheela, green gram": [("moong_dal", 100, "100% ground moong basis")],
    "Cheela, green gram, fermented batter": [("moong_dal", 100, "100% ground moong basis, fermented (macros unchanged)")],
    "Poori, deep-fried wheat dough, with potato palya": [
        ("wheat_flour_atta", 1 * G["cup_flour"], "1 cup wheat flour"),
        ("veg_oil", 2 * G["tsp_fat"], "2 tsp oil in dough (see notes: excludes frying absorption)"),
        ("potato", 100, "potato palya side, ~100g"),
    ],
    "Laddu (popped amaranth, foxtail millet, legume, fenugreek)": [
        ("amaranth_seed", 40, "popped amaranth, ~40g"),
        ("foxtail_millet", 40, "popped foxtail millet, ~40g"),
        ("bengal_gram_dal", 15, "besan, ~15g"),
        ("fenugreek_seeds", 5, "fenugreek, ~5g"),
        ("jaggery", 33.3, "jaggery, ~25% of total weight"),
    ],
    "Parantha, radish, wheat/mothbean/Bengal gram, with curd": [
        ("wheat_flour_atta", 3 * G["cup_flour"], "3 cups wheat flour"),
        ("moth_bean", 0.5 * G["cup_flour"], "0.5 cup mothbean flour"),
        ("bengal_gram_dal", 0.5 * G["cup_flour"], "0.5 cup Bengal gram flour"),
        ("radish", 100, "radish filling, ~100g"),
        ("yogurt", 2.5 * 15, "curd side, ~2.5 tbsp"),
    ],
    "Tahlipeeth, wheat/bengal gram/green gram, with chutney": [
        ("wheat_flour_atta", 3 * G["cup_flour"], "3 cups wheat flour"),
        ("bengal_gram_dal", 0.5 * G["cup_flour"], "0.5 cup Bengal gram flour"),
        ("moong_dal", 0.5 * G["cup_flour"], "0.5 cup green gram flour"),
        ("coconut_chutney", 18, "chutney side, ~18g"),
    ],
    "Stringhoppers, red rice flour, with sambol/egg/gravy": [
        ("rice_milled", 150, "rice flour dough, ~150g dry-equivalent"),
        ("coconut_chutney", 30, "coconut sambol, ~30g"),
        ("egg", G["egg"], "1 egg"),
        ("coconut_chutney", 25, "coconut gravy, ~50ml treated as 25g coconut-equivalent"),
    ],
    "Puttu/Pittu, industrially-milled finger millet flour": [
        ("ragi", 2 * G["cup_flour"], "2 cups finger millet flour"),
        ("coconut_fresh", 1 * G["cup_coconut"], "1 cup grated coconut"),
    ],
    "Puttu/Pittu, stone-ground finger millet flour": [
        ("ragi", 2 * G["cup_flour"], "2 cups finger millet flour"),
        ("coconut_fresh", 1 * G["cup_coconut"], "1 cup grated coconut"),
    ],
    "Basmati rice (microwave), with coconut sambol - Pakistan": [
        ("rice_milled", 175, "basmati rice, ~175g dry-equivalent"),
        ("coconut_chutney", 25, "coconut sambol, ~25g"),
    ],
    "Basmati rice (microwave), with coconut sambol - India": [
        ("rice_milled", 175, "basmati rice, ~175g dry-equivalent"),
        ("coconut_chutney", 25, "coconut sambol, ~25g"),
    ],
    "Basmati rice (rice cooker), with coconut sambal": [
        ("rice_milled", 175, "basmati rice, ~175g dry-equivalent"),
        ("coconut_chutney", 25, "coconut sambol, ~25g"),
    ],
    "Basmati rice (rice cooker), with coconut sambol": [
        ("rice_milled", 175, "basmati rice, ~175g dry-equivalent"),
        ("coconut_chutney", 25, "coconut sambol, ~25g"),
    ],
    "Butter chicken": [
        ("chicken", 400, "400g chicken"),
        ("yogurt", 0.5 * G["cup_yogurt"], "0.5 cup yogurt marinade"),
        ("tomato", 0.75 * G["cup_tomato"], "0.75 cup tomato puree"),
        ("butter", 3 * G["tbsp_fat"], "3 tbsp butter"),
        ("cream", 3 * 15, "3 tbsp cream"),
        ("honey", 1.5 * G["tbsp_honey"], "1.5 tbsp honey/sugar"),
    ],
    "Tandoori chicken": [
        ("chicken", 400, "400g chicken"),
        ("yogurt", 0.5 * G["cup_yogurt"], "0.5 cup yogurt marinade"),
    ],
    "Chicken tikka masala": [
        ("chicken", 400, "400g chicken"),
        ("yogurt", 0.5 * G["cup_yogurt"], "0.5 cup yogurt marinade"),
        ("tomato", 0.75 * G["cup_tomato"], "0.75 cup tomato puree"),
        ("butter", 3 * G["tbsp_fat"], "3 tbsp butter"),
        ("cream", 3 * 15, "3 tbsp cream"),
        ("honey", 1.5 * G["tbsp_honey"], "1.5 tbsp honey/sugar"),
    ],
    "Chicken curry (generic)": [
        ("chicken", 400, "400g chicken"),
        ("onion", 1 * G["cup_onion"], "1 cup chopped onion"),
        ("tomato", 1 * G["cup_tomato"], "1 cup chopped tomato"),
        ("veg_oil", 2.5 * G["tbsp_fat"], "2.5 tbsp oil"),
    ],
    "Butter paneer (paneer makhani)": [
        ("paneer", 400, "400g paneer"),
        ("butter", 4 * G["tbsp_fat"], "0.25 cup butter"),
        ("tomato", 2 * G["cup_tomato"], "2 cups tomato puree"),
        ("cream", 1 * G["cup_cream"], "1 cup cream"),
        ("honey", 2 * G["tbsp_honey"], "2 tbsp sugar/honey"),
    ],
    "Palak paneer": [
        ("paneer", 300, "300g paneer"),
        ("spinach", 500, "~500g spinach"),
        ("cream", 2 * 15, "2 tbsp cream"),
        ("onion", 80, "1 small onion"),
    ],
    "Dal makhani": [
        ("urad_whole", 4 * G["cup_dal"], "4 cups whole urad dal"),
        ("rajmah_red", 1 * G["cup_dal"], "1 cup rajma"),
        ("butter", 2.5 * G["tbsp_fat"], "2.5 tbsp butter"),
        ("cream", 0.5 * G["cup_cream"], "0.5 cup cream"),
        ("onion", 75, "onion, ~0.5 cup"),
        ("tomato", 90, "tomato, ~0.5 cup"),
    ],
    "Chana masala": [
        ("bengal_gram_whole", 1 * G["cup_dal"], "1 cup chickpeas"),
        ("ghee", 3 * G["tbsp_fat"], "3 tbsp ghee"),
        ("potato", 2 * G["medium_potato"], "2 medium potatoes"),
        ("onion", 2 * G["medium_onion"], "2 medium onions"),
        ("tomato", 4 * G["medium_tomato"], "4 medium tomatoes"),
    ],
}

# Direct-lookup foods: food_name -> ingredient_key (nutrient values copied as-is)
DIRECT = {
    "Basmati rice pilau, with onion and curry powder": "rice_milled",
    "Chapatti (Elephant Atta Medium flour)": "wheat_flour_atta",
    "Chapatti": "wheat_flour_atta",
    "Chapati, flatbread": "wheat_flour_atta",
    "Naan bread": "wheat_flour_refined",
    "Paratha, frozen, heated in dry pan": "wheat_flour_atta",
    "Pilaf porridge, whole grain": "rice_brown",
    "Basmati rice, white, polished, cooked 10 min": "rice_milled",
    "Basmati rice (Dreamrice)": "rice_milled",
    "Basmati rice, white, boiled (Mahatma)": "rice_milled",
    "Basmati rice, white, boiled (SunRice)": "rice_milled",
    "Basmati rice (Laila)": "rice_milled",
    "Chickpeas, canned, drained": "bengal_gram_whole",
    "Chickpeas (Garbanzo beans, Bengal gram), canned": "bengal_gram_whole",
    "Lentils, brown, canned, drained": "lentil_brown",
    "Unpolished little millet, plain cooked": "little_millet",
    "Unpolished foxtail millet, plain cooked": "foxtail_millet",
    "Finger millet extruded snack": "ragi",
    "Chapatti, wheat flour, thin, with green gram dhal": "wheat_flour_atta",
    "Lentils, Mothbean, sprouted, cooked in buttermilk": "moth_bean",
    "Porridge, scoured wheat, with gram mix": "wheat_whole",
    "Porridge, decorticated finger millet, with gram mix": "ragi",
    "Rajmah (kidney beans), boiled": "rajmah_red",
    "Roti (unleavened flatbread), whole wheat flour": "wheat_flour_atta",
}

# Blends: proportions are stated directly in the food name, so no external
# recipe sourcing was needed -- just a mass-weighted blend.
BLENDS = {
    "Chapati, flatbread with 10% fenugreek": [
        ("wheat_flour_atta", 90, "90% wheat flour"),
        ("fenugreek_seeds", 10, "10% fenugreek (seeds used as dry-basis proxy, see notes)"),
    ],
    "Roti, 75% rice flour and 25% soy flour": [
        ("rice_milled", 75, "75% rice flour"),
        ("soybean", 25, "25% soy flour (whole soybean composition used, see notes)"),
    ],
}

UNRESOLVED = {
    "Arrowroot (Canna indica), with coconut": "no reliable modern recipe proportion found; species-specific preparation",
    "Arrowroot (Maranta arundinacea), with coconut": "same issue as Canna indica arrowroot",
    "Jackfruit, with coconut and onion sambal": "meal-assembly dish, portion sizes unclear from available sourcing",
    "Lentil and cauliflower curry with rice": "meal-assembly, portion sizes unclear",
    "Lentil curry, with wholemeal bread": "meal-assembly, portion sizes unclear",
    "Manioc (cassava), with coconut sambol": "manioc alone is a direct IFCT lookup (F015 Tapioca), but exact coconut sambol portion for this specific dish wasn't confirmed",
    "Red rice, with lentil curry, salad, egg, coconut gravy": "multi-component meal-assembly, too many unclear portions to responsibly estimate",
    "Yam (Dioscorea alata), white, with coconut": "yam species-matched IFCT entry not available (only elephant/ordinary/wild yam), and the coconut portion wasn't confirmed",
}


def main():
    BREAKDOWN_DIR.mkdir(exist_ok=True)
    rows = []

    for name, ingredient_key in DIRECT.items():
        vals = INGREDIENTS[ingredient_key]
        rows.append({"food_name": name, **{k: vals[k] for k in NUTRIENT_KEYS}})

    for name, parts in BLENDS.items():
        vals, total_g = _weighted([(k, g) for k, g, _ in parts])
        rows.append({"food_name": name, **vals})
        _write_breakdown(name, parts, vals, total_g)

    for name, parts in DISHES.items():
        vals, total_g = _weighted([(k, g) for k, g, _ in parts])
        rows.append({"food_name": name, **vals})
        _write_breakdown(name, parts, vals, total_g)

    rows.sort(key=lambda r: r["food_name"])
    out_path = RAW_DIR / "south_asian_nutrients.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["food_name"] + NUTRIENT_KEYS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {out_path}")

    unmatched_path = RAW_DIR / "south_asian_nutrients_unmatched.txt"
    with open(unmatched_path, "w", encoding="utf-8") as f:
        for name, reason in UNRESOLVED.items():
            f.write(f"{name}\t{reason}\n")
    print(f"wrote {len(UNRESOLVED)} unmatched foods to {unmatched_path}")


def _slug(name):
    keep = "".join(c.lower() if c.isalnum() else " " for c in name)
    return "-".join(keep.split())[:60]


def _write_breakdown(name, parts, vals, total_g):
    data = {
        "food_name": name,
        "ingredients": [
            {"ingredient": ing, "grams": round(g, 2), "note": note, "source": INGREDIENTS[ing]["source"]}
            for ing, g, note in parts
        ],
        "total_mix_grams": round(total_g, 2),
        "per_100g_nutrients": vals,
        "method": "mass-weighted average of ingredient per-100g nutrient values; "
                  "per-100g output is scale-invariant so only ingredient mass ratios matter, "
                  "not the absolute batch size shown here",
    }
    path = BREAKDOWN_DIR / f"{_slug(name)}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    main()
