# South Asian nutrient decomposition notes (Phase 4)

`data/raw/south_asian_nutrients.csv` is built by `data/raw/build_south_asian_nutrients.py`
from IFCT 2017 (`data/raw/IFCT2017.pdf`, Table 1 "Proximate Principles and
Dietary Fibre" and Table 6 "Starch and Individual Sugars") plus a handful of
published values for ingredients IFCT doesn't cover in enough detail. Re-run
the script to regenerate the CSV and the `recipe_breakdowns/*.json` files
from the ingredient/dish tables inside it.

## Basis: raw/dry ingredient mix, not cooked/as-eaten weight

Every value in `south_asian_nutrients.csv` is per 100g of the food's
**raw/dry ingredient mix** -- e.g. "Basmati rice, white, boiled (Mahatma)" is
reported using IFCT's raw-milled-rice composition, not the composition of a
100g plate of cooked rice (which is roughly 68% water and therefore much
less carb-dense per 100g). This was a deliberate choice, not an oversight:

- The Phase 4 instructions explicitly say to treat names like "Basmati rice,
  white, boiled" and "Rajmah, boiled" as **direct lookups** to the matching
  raw IFCT entry, "no decomposition needed" -- i.e. use the raw value as-is
  despite the state-name mismatch.
- IFCT itself only tabulates raw/dry ingredient composition; it has no
  "cooked rice", "cooked dal", etc. entries to substitute in.
- For composite dishes, using ingredient mass *ratios* (rather than
  estimating the water-diluted finished weight of a serving) avoids stacking
  a second, much less certain layer of assumptions (how much water a
  particular grain/legume absorbs when cooked, how much oil a fried item
  absorbs, etc.) on top of the recipe-proportion assumptions already needed.
  Nutrient content doesn't change with added cooking water, so a mass-ratio
  computation is exact for whatever ratios go in -- it's just not on the
  same water-diluted basis as a plate of the finished food.

**Consequence:** `tests/test_phase_04.py::test_gl_sanity_check_against_atkinson_gl_flags_outliers`
flags 57 of the 66 matched south_asian dishes as falling outside the +/-30%
GL tolerance, essentially all of them because the recomputed GL runs
1.3x-2x higher than Atkinson's recorded GL. This is the raw/dry-vs-cooked
basis gap showing up systematically, not per-dish estimation noise (the
ratio clusters tightly around 1.7-2.1x for rice/wheat/millet dishes
specifically, consistent with cooked grain being roughly 2.5-3x less
carb-dense per 100g than the dry grain it was cooked from). This is a
known, structural limitation of Phase 4's output as built, flagged here for
whoever picks up Phase 5: joining this CSV's carbs_g against Atkinson's GL
will not reproduce GL cleanly for grain/legume-heavy dishes without a
cooked-weight correction, which was out of scope for this phase.

## Ingredient sourcing

Chicken, paneer averaged from IFCT directly. Butter, ghee, cream, and
plain yogurt/curd are not in IFCT's proximate table with usable detail (IFCT
is India-specific and its dairy section only covers milk/paneer/khoa), so
these four use published USDA FoodData Central typical values (per 100g,
retrieved 2026-08-13):

| ingredient | protein_g | fat_g | carbs_g | sugar_g |
|---|---|---|---|---|
| Butter, salted | 0.85 | 82.2 | 0.06 | 0.06 |
| Ghee | 0.3 | 99.5 | 0 | 0 |
| Heavy cream (~36% fat) | 2.1 | 36.0 | 2.8 | 2.8 |
| Yogurt, plain, whole milk | 3.9 | 4.5 | 5.6 | 4.7 |
| Honey | 0.3 | 0 | 82.4 | 82.1 |

Generic vegetable oil (chicken curry, poori dough) is treated as 100g fat /
100g, 0 everything else -- standard for refined cooking oil.

IFCT Table 6's per-food "Total Free Sugars" column (rightmost number in each
row) is used as `sugar_g`; this was validated against a row where the
column arithmetic is fully shown (A001 Amaranth: 0.10 fructose + 0.22
glucose + 0.46 sucrose + 0.10 maltose = 0.88 total free sugars, matching the
last column exactly).

Paneer's Table 6 row didn't cleanly parse (the dairy block's column layout
differs from the cereal blocks and its numbers don't reconcile with Table
1's carb value), so paneer's `sugar_g` is instead set equal to its Table 1
`carbs_g` (2.41g) -- standard practice for unsweetened dairy, since nearly
all of its carbohydrate is lactose.

### Notable proxy/mapping choices

- **Foxtail millet**: IFCT food code A017 is labeled "Varagu (*Paspalum
  scrobiculatum*)" -- botanically kodo millet -- in Table 1, but the same
  code A017 is labeled "Varagu (*Setaria italica*)" -- botanically foxtail
  millet -- in Table 6. This is an inconsistency in the source PDF itself
  (not introduced here). Since no other small-millet entry maps more
  cleanly to foxtail millet, A017 is used as the foxtail millet proxy
  throughout, flagged here rather than silently assumed.
- **Besan (gram flour)** is treated as nutritionally identical to Bengal
  gram dal (IFCT B001), since besan is just ground chana dal.
- **Naan** uses refined wheat flour (maida, A018) rather than atta, since
  naan is traditionally made with refined flour.
- **"Pilaf porridge, whole grain"** is matched to brown rice (A013, IFCT's
  only "whole grain" rice entry) on the reasoning that "pilaf"/"pulao"
  overwhelmingly denotes a rice dish in South Asian cooking.
- **Ragi flakes / ragi vermicelli** (Finger millet flakes upma, Finger
  millet vermicelli upma) have no separate IFCT entries; whole ragi (A010)
  composition is used for both, since it's the same species and processing
  form doesn't materially change macro-nutrient density.
- **Chapati, flatbread with 10% fenugreek**: fenugreek *seeds* (G026) were
  used rather than fresh fenugreek leaves as the 10% component, even though
  the real product likely uses dried leaf powder (kasuri methi). IFCT only
  has a *fresh* leaf entry (86.7% water), which doesn't blend sensibly into
  a dry flour mix; seeds are dry-basis and blend correctly, even though the
  real ingredient is probably closer to dried leaves nutritionally.
- **Coconut chutney / sambol / gravy**: approximated throughout as fresh
  coconut kernel (H007) alone -- the onion/chili/lime/water components of a
  real chutney or sambol are treated as a negligible mass contribution next
  to the coconut. "Coconut gravy" (stringhoppers) is treated as half its
  stated liquid volume, since a gravy is water-diluted relative to grated
  coconut.
- **Chana dal / bengal gram dal** tempering ingredient reused for besan
  throughout upma/dhokla/tahlipeeth recipes (same reasoning as above).
- **Sambar** (idli with sambar) is approximated as a small addendum of dry
  toor dal (B021) + tomato, not modeled as its own multi-vegetable dish.

### "With X" qualifiers not covered by a named recipe group

A few south_asian foods have a "with X" qualifier that isn't covered by any
of the named recipe groups supplied for this phase, and weren't listed as
unresolved either. Per the phase's catch-all instruction ("foods not
explicitly listed above ... treat as single-ingredient direct IFCT
lookups"), these were resolved as direct lookups to their dominant grain/
legume, with the qualifier treated as an unquantified side note:

- "Basmati rice pilau, with onion and curry powder" -> basmati rice only
- "Chapatti, wheat flour, thin, with green gram dhal" -> wheat flour only
- "Lentils, Mothbean, sprouted, cooked in buttermilk" -> moth bean only
- "Porridge, scoured wheat, with gram mix" -> whole wheat only
- "Porridge, decorticated finger millet, with gram mix" -> ragi only
- "Paratha, frozen, heated in dry pan" -> wheat flour atta only (no
  separate oil-layering accounted for)
- "Naan bread" -> refined wheat flour only

## Measures-to-grams conversion table

Recipe proportions were given in cups/tbsp/tsp/medium-sized units. These
standard, commonly-cited home-cooking conversions were used (documented
here since they're assumptions, not IFCT data):

| measure | grams | measure | grams |
|---|---|---|---|
| 1 cup rice/millet (raw) | 190 | 1 tbsp oil/ghee/butter | 14 |
| 1 cup dal/lentils (raw) | 200 | 1 tbsp dal (tempering) | 12 |
| 1 cup flour (wheat/besan) | 120 | 1 tbsp flour | 8 |
| 1 cup semolina/rava | 165 | 1 tbsp peanuts | 9 |
| 1 cup broken wheat/bulgur | 170 | 1 tbsp honey | 20 |
| 1 cup grated fresh coconut | 80 | 1 tsp oil | 5 |
| 1 cup chopped onion | 150 | 1 tsp dal | 3 |
| 1 cup chopped tomato | 180 | 1 medium onion | 110 |
| 1 cup yogurt | 245 | 1 medium tomato | 123 |
| 1 cup cream | 240 | 1 medium potato | 150 |
| 1 cup poha (flattened rice) | 80 | 1 egg (edible portion) | 50 |

Where a recipe gave a range (e.g. "2-4 tbsp peanuts", "20-30g sambol"), the
midpoint was used. Where a recipe gave an absolute serving-style quantity
(e.g. butter chicken's "400g chicken"), that was used directly.

## Portion-size assumptions for unquantified sides/fillings

- Coconut chutney side (dosa/idli "with chutney"): ~18g
- Coconut sambol/gravy side (rice-with-sambol dishes, stringhoppers): ~25-30g
- Potato palya side (poori): ~100g potato
- Radish filling (parantha): ~100g
- Sambar addendum (idli with sambar): ~15g dry toor dal + ~10g tomato
- Laddu jaggery binder: ~25% of total finished weight

## Method (composite dishes)

Each composite dish's `recipe_breakdowns/<slug>.json` lists the ingredients
and gram quantities used, the total mix mass, and the resulting per-100g
nutrient values. The per-100g value is a **mass-weighted average** of the
ingredients' per-100g values, weighted by each ingredient's fraction of the
total mix mass -- this is scale-invariant, so only ingredient mass *ratios*
matter, not the absolute batch size shown in the JSON (some JSON files show
a full-recipe batch, e.g. dal makhani's 4-cup dal base, rather than a single
serving; the reported per-100g figure is unaffected by that choice either
way).

## Unmatched foods

See `data/raw/south_asian_nutrients_unmatched.txt` for the 8 foods left
unresolved, per the phase's UNRESOLVED list (arrowroot x2, jackfruit sambal,
lentil-cauliflower-rice, lentil curry with bread, manioc with sambol, red
rice multi-component meal, yam with coconut) -- all either lack a
confirmed recipe/portion source or are multi-component meal-assembly dishes
where the constituent proportions are unclear.
