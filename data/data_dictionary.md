# Data Dictionary

## `data/processed/foods.csv` / `foods.json`

The finalized dataset every later phase reads from. Produced by
`data/raw/build_foods_dataset.py`, which merges `data/raw/gi_gl_raw.csv`
(GI/GL ground truth) with `data/raw/american_nutrients.csv` and
`data/raw/south_asian_nutrients.csv` (decomposed nutrient profiles) on
`food_name`, dropping the 9 foods that were never matched to nutrient data
(see "Excluded foods" below). 129 rows: 66 south_asian, 63 american.

| column | type | source | description |
|---|---|---|---|
| `food_name` | string | Atkinson et al. 2021 / IFCT 2017 branded-product naming | Unique food identifier, as named in `gi_gl_raw.csv` |
| `cuisine` | string (`south_asian` \| `american`) | `gi_gl_raw.csv` | Which nutrient source and category-mapping table the food belongs to |
| `fiber_g` | float | USDA FoodData Central (american) / IFCT 2017 decomposition (south_asian) | Dietary fiber, grams per 100g of the food as consumed (cooked/prepared basis) |
| `fat_g` | float | same | Total fat, grams per 100g |
| `protein_g` | float | same | Protein, grams per 100g |
| `carbs_g` | float | same | Available carbohydrate, grams per 100g |
| `sugar_g` | float | same | Total sugars, grams per 100g (subset of `carbs_g`) |
| `GI` | float | Atkinson et al. 2021 (lab-tested) or documented first-principles exceptions (see below) | Glycemic index, 0-110 scale (glucose = 100) |
| `GL` | float | Atkinson et al. 2021, `GL = GI/100 * category_standard_carb_g` (or documented exceptions) | Glycemic load for Atkinson's standardized category serving, **not** derived from this row's own `carbs_g` -- see "GL methodology" below |

GI and GL are properties of the food, not of any individual eating it.

## South Asian nutrient decomposition methodology

South Asian foods are frequently composite regional dishes (e.g. dosa,
upma, dal makhani) without a direct IFCT 2017 entry. Where no direct
IFCT lookup existed, nutrients were computed as a recipe decomposition:
each dish's `data/raw/recipe_breakdowns/<slug>.json` lists ingredients in
raw grams, applies a per-ingredient cooking yield factor, and produces a
mass-weighted average per-100g nutrient profile on a **cooked-mass basis**
(not raw-mass basis -- see `data/raw/south_asian_decomposition_notes.md`,
"raw-vs-cooked basis" fix). Portion-to-gram conversions for cups/tbsp/tsp
measures, and assumptions for unquantified sides (chutney, sambol, etc.),
are documented in that same file. Where a dish name had a qualifier not
covered by a named recipe group (e.g. "with onion and curry powder"), it
was resolved as a direct single-ingredient IFCT lookup on the dominant
grain/legume, per the phase's catch-all instruction.

## American nutrient source

American foods were matched to USDA FoodData Central entries (Foundation,
SR Legacy, FNDDS, or Branded, by `fdc_id`) via `data/raw/fetch_american_nutrients.py`.
Nutrient values are per 100g as reported by FDC for that specific entry.

## Excluded foods (unresolved, see Phase 3/4 notes)

9 foods appear in `data/raw/gi_gl_raw.csv` but have no row in either
nutrients CSV, so they do **not** appear in `foods.csv`/`foods.json`. This
is deliberate, not a data-loss bug -- see `data/raw/south_asian_nutrients_unmatched.txt`
and `data/raw/american_nutrients_unmatched.txt` for the original per-food
reasoning.

South Asian (8, all multi-component meal-assembly dishes or
species-specific preparations with no confirmed recipe/portion source):
- Arrowroot (Canna indica) with coconut
- Arrowroot (Maranta arundinacea) with coconut
- Jackfruit with coconut and onion sambal
- Lentil and cauliflower curry with rice
- Lentil curry with wholemeal bread
- Manioc (cassava) with coconut sambol
- Red rice with lentil curry/salad/egg/coconut gravy
- Yam (Dioscorea alata) white, with coconut

American (1, no confident FDC match found):
- Mango dessert, prepared (Nestlé)

## Documented GI/GL exceptions (non-Atkinson south_asian dishes)

Eight North Indian meat/paneer/legume dishes were added to `gi_gl_raw.csv`
(south_asian cuisine) that are absent from Atkinson et al. 2021 because
that paper's own methodology excludes "mixed meals" (e.g. dishes like
"spaghetti Bolognese") from GI testing. They are included here anyway so
the app can recognize and log them, with GI/GL values reasoned from first
principles rather than sourced from a lab study. These are **not**
lab-tested GI values, and are excluded from the GL category-based
plausibility check below (they have no Atkinson category to check against).

- **Butter chicken, Tandoori chicken, Chicken tikka masala, Chicken curry
  (generic), Butter paneer (paneer makhani), Palak paneer** -- GI = 0, GL = 0.
  Protein/fat-dominant with negligible carbohydrate content, so a near-zero
  glycemic response is scientifically defensible. A reasoned estimate, not
  a placeholder and not a lab measurement.
- **Dal makhani** -- GI = 30, GL = 5. Legume-dominant dish; GI estimated
  from the known GI of its base legumes already in this dataset (Table 1:
  "Lentils, brown, canned" GI=42, "Rajmah, boiled" GI=19, "Chickpeas,
  canned" GI=35-38), adjusted downward for the enriching effect of added
  fat (butter/cream tends to lower GI further). GL computed from an
  estimated standard-serving carb content of ~18g.
- **Chana masala** -- GI = 35, GL = 8. Same legume-GI-basis reasoning as
  dal makhani. GL computed from an estimated standard-serving carb content
  of ~22g, which includes potato per the source recipe.

## GL methodology and category-based plausibility check

Atkinson et al. 2021 do **not** compute GL from a food's own carbohydrate
content at whatever serving size someone happens to eat. Instead, GL is
computed from a *standardized* available-carbohydrate portion assigned per
food category (21 categories total, e.g. Breads=15g, Regional or
traditional foods=35g, Cereal grains=45g, Legumes=15g, Snack foods and
confectionery=25g, Sugars and syrups=5g): `GL = GI/100 * category_standard_carb_g`.
This means GL is mathematically independent of this dataset's own
`carbs_g` column -- a flat `GL ≈ GI * carbs_g / 100` sanity check (which an
earlier draft of this project used) is methodologically wrong and produces
false positives whenever a food's standardized portion differs from 100g
of carbohydrate, which is nearly always. This was first identified and
fixed in Phase 4 (see `south_asian_decomposition_notes.md`, "GL sanity
check methodology correction").

Each food's Atkinson category is recorded in:
- `data/raw/south_asian_category_mapping.md` (66 south_asian foods, 8
  non-Atkinson exception dishes excluded)
- `data/raw/american_category_mapping.md` (63 american foods)

Category assignment for both cuisines is a documented judgment call, not a
literal per-food table lookup: the Atkinson supplemental data actually
containing per-food category assignments is hosted separately from the
systematic-review PDF used as this phase's source and wasn't available in
this session, so foods were matched to Atkinson's 21 category *definitions*
by name and nature, following the same methodology and documentation style
in both mapping files.

`tests/test_phase_05.py`'s GL check works out, per food, what serving
weight (in this dataset's decomposed/matched `carbs_g`, per 100g) would
contain that food's category's standardized carb amount:
`implied_weight_g = category_standard_carb_g / carbs_g_per_100g * 100`.
This is a plausibility check (is the implied weight a realistic serving?),
not an exact-match check. The plausible range used is 5-600g: the lower
bound is 5g rather than Phase 4's original 15g because this phase's
American mapping introduces the "Sugars and syrups" category (honey, maple
syrup), whose 5g standardized portion combined with ~70-82g/100g carb
density legitimately implies a serving of only ~6-7g (roughly a teaspoon)
-- correct, not a decomposition error. The check runs across both cuisines
now that both have category mappings, excluding the 9 documented
non-Atkinson exception dishes (the 8 South Asian ones listed above, plus
Dal makhani and Chana masala).
