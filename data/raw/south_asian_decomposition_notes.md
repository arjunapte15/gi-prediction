# South Asian nutrient decomposition notes (Phase 4)

`data/raw/south_asian_nutrients.csv` is built by `data/raw/build_south_asian_nutrients.py`
from IFCT 2017 (`data/raw/IFCT2017.pdf`, Table 1 "Proximate Principles and
Dietary Fibre" and Table 6 "Starch and Individual Sugars") plus a handful of
published values for ingredients IFCT doesn't cover in enough detail. Re-run
the script to regenerate the CSV and the `recipe_breakdowns/*.json` files
from the ingredient/dish tables inside it.

## Basis: cooked/as-eaten weight (corrected post-Phase-4; see below)

Every value in `south_asian_nutrients.csv` is per 100g of the food's
**cooked/as-eaten weight**, matching the basis Atkinson et al. used for
their GL values. This was NOT the original Phase 4 basis -- see "Cooking-yield
correction (post-Phase-4 fix)" below for what changed, why, and what's still
imperfect about it. The rest of this section is kept for history/audit.

Phase 4 originally reported every value per 100g of the food's **raw/dry
ingredient mix** instead -- e.g. "Basmati rice, white, boiled (Mahatma)" used
IFCT's raw-milled-rice composition directly, not the composition of a 100g
plate of cooked rice (which is roughly 68% water and therefore much less
carb-dense per 100g). That was a deliberate choice at the time, reasoned as
follows, but it turned out to make the GL sanity check fail almost
everywhere (see the correction section below for the fix):

- Phase 4's instructions said to treat names like "Basmati rice, white,
  boiled" and "Rajmah, boiled" as **direct lookups** to the matching raw
  IFCT entry, "no decomposition needed" -- read at the time as license to use
  the raw value as-is despite the state-name mismatch.
- IFCT itself only tabulates raw/dry ingredient composition; it has no
  "cooked rice", "cooked dal", etc. entries to substitute in.
- Using ingredient mass *ratios* directly (rather than estimating the
  water-diluted finished weight of a serving) avoided stacking a second,
  uncertain layer of assumptions (how much water a grain/legume absorbs when
  cooked) on top of the recipe-proportion assumptions already needed.

**Consequence (Phase 4, now fixed):** the GL sanity check flagged 55-57 of
58-66 checkable dishes, essentially all of them, because recomputed GL ran
1.3x-2x higher than Atkinson's recorded GL -- the raw/dry-vs-cooked basis gap
showing up systematically. See below for the fix and the much smaller set of
dishes still flagged afterward.

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

## Cooking-yield correction (post-Phase-4 fix)

Fixes the raw-vs-cooked basis error described above. `INGREDIENTS` in
`build_south_asian_nutrients.py` still stores each ingredient's per-100g
**raw** nutrient values (unchanged from Phase 4 -- IFCT and the published
dairy/meat values are inherently raw-basis, and cooking doesn't destroy
macros, so the raw values are still the correct *content* figures). What
changed is the mass denominator: each ingredient line in a dish now carries
a `yield_factor`, and `cooked_grams = raw_grams * yield_factor`. A dish's
per-100g-cooked nutrient value is then `total_nutrient_content /
total_cooked_grams * 100`, instead of Phase 4's `total_nutrient_content /
total_raw_grams * 100`. For direct-lookup foods this collapses to
`raw_value / yield_factor`. `yield_factor = 1.0` for ingredients that don't
meaningfully change mass during preparation (oils, ghee, butter, cream,
yogurt, paneer, coconut used raw/grated, nuts, sugars/jaggery/honey,
spices, vegetables, eggs) -- their Phase 4 values are unchanged.

Yield factors used (standard published cooking-yield multipliers; the
grain/legume ones are well-established, the dough/batter ones are flagged
as approximations per the fix's own instructions):

| category | factor | applies to |
|---|---|---|
| Rice, boiled or steamed | 2.5 | all rice varieties, including rice ground into a batter that's then steamed/griddled (dosa, idli, dhokla-with-rice) |
| Millets/broken wheat/whole wheat cooked like rice | 2.5 | little millet, foxtail millet, ragi (when boiled as porridge/upma, not steamed as a pressed shape), broken wheat/dalia, whole wheat porridge |
| Semolina/rava cooked in water | 2.5 | upma, upittu, the semolina portion of dhokla |
| Split dal boiled directly in liquid | 2.3 | moong dal in pongal (khichdi-style), toor dal in sambar, moong dal boiled into broken-wheat upma |
| Whole legumes boiled | 2.5 | whole urad, rajma, dried/canned chickpeas, brown lentils, moth bean |
| Dal/besan ground into a wet batter, steamed or pan-fried | 1.5 (approximation) | dosa/idli's urad dal, cheela, the dal/besan portion of dhokla |
| Wheat-flour dough cooked on tawa or fried | 1.35 (approximation) | chapati, roti, naan, paratha, poori, tahlipeeth, parantha (including the mothbean/besan flour mixed into the same dough), the rice+soy roti blend |
| Flour reconstituted into a pressed/steamed dough shape | 1.8 (approximation) | stringhoppers, pittu/puttu |
| Raw chicken -> cooked (moisture loss, concentrates nutrients) | 0.75 | butter chicken, tandoori chicken, chicken tikka masala, chicken curry |

**Chicken/paneer check (the 6 GI=0 exception dishes):** `chicken`'s IFCT
source is N001-N004 (leg/thigh/breast/wing, skinless), and IFCT labels these
rows without any "cooked"/"boiled" qualifier, i.e. they're raw -- confirmed
by cross-checking the values against known raw-chicken macros (~19-22g
protein, ~9-14g fat per 100g raw, which is what N001-N004 show; cooked
chicken breast runs closer to 26-31g protein per 100g). The 0.75 yield
factor was therefore applied to all 4 chicken-containing dishes. `paneer`'s
IFCT source is L003 "Paneer" -- paneer is definitionally a prepared dairy
product (milk curdled with acid, then pressed), not something eaten in a
"raw ingredient" state the way raw chicken is, and IFCT's own values
(51.96g water, 18.86g protein, 24.78g fat per 100g) match real-world
ready-to-eat paneer nutrition closely. No correction was applied to paneer
(butter paneer, palak paneer, both left with `yield_factor = 1.0` on the
paneer line).

**Ingredients left uncorrected because none of the given yield categories
apply** (documented per-dish in `recipe_breakdowns/*.json`, `yield_factor =
1.0`, still on a raw basis -- these are expected to keep failing the GL
sanity check and that's a known, called-out limitation, not a bug):

- **Rice flakes (poha)**: already a parboiled/flaked product that's briefly
  rehydrated, not boiled from raw grain the way whole rice is -- the "rice,
  boiled/steamed: 2.5" category doesn't obviously transfer to it, and no
  poha-specific factor was given.
- **Popped amaranth / popped foxtail millet (laddu)**: popping is a
  dry-heat puffing process (like popcorn), not water-cooking -- it doesn't
  fit any of the water-absorption or dough categories.
- **Finger millet extruded snack**: a manufactured, industrially extruded
  product, not something home-cooked by boiling -- none of the given
  categories describe its actual processing.

### Result

61 of the 66 matched rows changed value (the other 5 -- butter paneer,
palak paneer, the finger millet extruded snack, the laddu, and the poha --
have no water-absorbing ingredient that a given yield factor applies to, so
they're identical to their Phase 4 values). Re-running
`tests/test_phase_04.py::test_gl_sanity_check_against_atkinson_gl_flags_outliers`
after the fix: **22 of 58 checkable dishes** now fall outside the +/-30%
tolerance (down from 55-57 of 58-66 before the fix). Remaining outliers,
by likely cause:

- **Consistently overshooting (~1.33x-1.56x): chapati/chapatti variants,
  naan, the rice+soy roti blend.** All use the 1.35 wheat-dough factor,
  which the fix's own instructions flagged as an approximation net of
  hydration and evaporation -- this cluster suggests the true factor for
  plain tawa-cooked flatbread is a bit higher than 1.35 (maybe ~1.5-1.6),
  though it's derived from only one data point (Atkinson's tested product)
  per food name, so it isn't possible to recalibrate confidently from this
  alone.
- **"Roti (unleavened flatbread), whole wheat flour" (3.06x, the largest
  remaining outlier)**: uses the exact same ingredient and yield factor as
  the Chapatti entries (which only overshoot ~1.35x-1.4x), so this
  particular food's recorded GL=7 looks anomalous relative to comparable
  wheat-flatbread items in the same dataset rather than pointing at a
  problem with the correction itself -- worth the user spot-checking
  Atkinson's source entry for this one.
- **Consistently undershooting (~0.53x-0.70x): the 4 remaining basmati rice
  variants, rajmah boiled, both millet "plain cooked" entries, dhokla with
  semolina, upittu, broken wheat upma, mothbean-in-buttermilk, canned
  lentils.** These mostly use the 2.5 rice/millet/whole-legume factors,
  which the fix's instructions called "well-established" -- but the
  systematic undershoot direction (opposite of the pre-fix systematic
  overshoot) suggests 2.5 may run a little high for some of these foods as
  tested by Atkinson (i.e. true cooked-yield might sit closer to 2.0-2.2 for
  some grains/legumes/millets). Also plausible per-food: canned/drained
  lentils may hydrate less than home-boiled dry lentils, and "Basmati rice
  (Dreamrice)" (same ingredient/factor, not flagged) shows this is at least
  partly ordinary per-product GI/GL variance rather than a pure basis error.
- **Poha, laddu, finger millet extruded snack**: expected, per the
  "ingredients left uncorrected" list above -- no matching yield category
  was given for these preparations.

None of these were adjusted by changing the yield factors beyond what this
fix specified, or by loosening the test's tolerance -- they're reported here
as open questions for a future pass rather than resolved.

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

Each composite dish's `recipe_breakdowns/<slug>.json` lists the ingredients,
their raw gram quantities, each one's `yield_factor` and resulting
`cooked_grams`, the total raw and cooked mix mass, and both
`per_100g_nutrients_cooked_basis` (what's in the CSV) and
`per_100g_nutrients_raw_basis_phase4_original` (what Phase 4 originally
produced, kept for audit so the fix itself is auditable alongside the
original). The per-100g value is a **mass-weighted average** of the
ingredients' per-100g raw nutrient values, divided by total *cooked* mass
instead of total *raw* mass -- this is still scale-invariant, so only
ingredient mass *ratios* matter, not the absolute batch size shown in the
JSON (some JSON files show a full-recipe batch, e.g. dal makhani's 4-cup dal
base, rather than a single serving; the reported per-100g figure is
unaffected by that choice either way).

## Unmatched foods

See `data/raw/south_asian_nutrients_unmatched.txt` for the 8 foods left
unresolved, per the phase's UNRESOLVED list (arrowroot x2, jackfruit sambal,
lentil-cauliflower-rice, lentil curry with bread, manioc with sambol, red
rice multi-component meal, yam with coconut) -- all either lack a
confirmed recipe/portion source or are multi-component meal-assembly dishes
where the constituent proportions are unclear.
