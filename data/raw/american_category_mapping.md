# American food -> Atkinson et al. 2021 category mapping

Maps each of the 63 matched american foods in `american_nutrients.csv` to one
of Atkinson et al. 2021's 21 food categories, each of which has a
standardized carbohydrate portion (grams) used to compute GL:
`GL = GI/100 * standardized_carb_g`. This mapping is what
`tests/test_phase_05.py`'s GL sanity check uses, in the same way
`south_asian_category_mapping.md` was used by `tests/test_phase_04.py`.

## Provenance note -- what the source PDF actually contains

The PDF supplied for this phase (`data/raw/atkinson21.pdf`, gitignored, not
committed) is the Atkinson et al. 2021 *Am J Clin Nutr* journal article
itself ("International tables of glycemic index and glycemic load values
2021: a systematic review"). It contains:

- The full list of the 21 food categories and each one's standardized
  available-carbohydrate portion (Methods section, reproduced below).
- Table 1, an aggregate summary (mean/SD GI, % low/medium/high-GI) per
  category -- not a per-food listing.

It does **not** contain the actual per-food Supplemental Table 1 / Table 2
entries -- the article states those are hosted separately via the
"Supplementary data" link on the publisher's site and weren't included in
what was provided this session. So, exactly as happened for the South Asian
mapping in Phase 4, there is no literal per-food "category header" to read
off a table of contents. Category assignment below is done by matching each
food's name/nature to Atkinson's 21 category *definitions*, the same
judgment-call methodology `south_asian_category_mapping.md` used -- flagged
per food below where the call is non-obvious.

## The 21 categories and standardized carbohydrate portions (from Methods)

| category | standard carb (g) | notes |
|---|---|---|
| Bakery products | 30 | |
| Beverages | 25 | 10g for beer |
| Breads | 15 | |
| Breakfast cereals | 20 | |
| Cereal grains | 45 | |
| Cookies | 20 | |
| Crackers | 15 | |
| Dairy products and alternatives | 10 / 20 | 10g plain, 20g flavored/sweetened |
| Fruit and fruit products | 15 | includes fruit spreads/jams subgroup |
| Fruit and vegetable juices | 20 | 10g for tomato/carrot/vegetable juices |
| Infant formula and weaning foods | 10 | |
| Legumes | 15 | |
| Meal replacements and weight management products | 20 | |
| Nutritional support products | 30 | |
| Nuts | 5 | |
| Pasta and noodles | 40 | |
| Snack foods and confectionery | 25 | |
| Soups | 20 | |
| Sugars and syrups | 5 | 2.5g for sugar replacers |
| Vegetables | 20 | 10g for beetroot/parsnip/pumpkin/carrot/peas/tomato sauces |
| Regional or traditional foods | 35 | |

Only the categories actually used below are relevant to this dataset; the
rest are listed for completeness/provenance since they came directly from
the article text.

## Breads (15g standard carb) -- 10 foods

| food | rationale |
|---|---|
| White bread | plain bread, unambiguous |
| Burger Buns, 100% Whole wheat | bread product |
| Rye bread, Pumpernickel | bread product |
| Multigrain bread, gluten-free | bread product |
| Multigrain batch bread | bread product |
| White sourdough bread, gluten free | bread product |
| Oat bran concentrate bread | bread product |
| Fruit and Muesli bread (Bürgen) | bread product (fruit/muesli inclusions don't change the base category) |
| Muesli bread (packet mix) | bread product |
| Mixed Grain bread roll (Bürgen) | bread roll, same family as sliced bread |

## Breakfast cereals (20g standard carb) -- 5 foods

| food | rationale |
|---|---|
| Oats, rolled, uncooked | judgment call: consumed as a breakfast porridge cereal, not a standalone "Cereal grains" raw grain; matches Atkinson's own commentary on oats/muesli products under breakfast cereals |
| Weet-Bix breakfast biscuit | name explicitly says "breakfast" |
| Rice Bubbles (Kellogg's) | branded breakfast cereal |
| Cornflakes | branded breakfast cereal |
| Bran Flakes (Kellogg's) | branded breakfast cereal |

## Bakery products (30g standard carb) -- 8 foods

| food | rationale |
|---|---|
| Doughnut | bakery item |
| Chocolate cake (Betty Crocker) | bakery item |
| Danish Pastry, Apple and Peach | bakery item |
| Apple Blueberry muffin | bakery item |
| Banana, oat and honey muffin | bakery item |
| Cranberry Raisin muffin | bakery item |
| Apricot, coconut and honey muffin | bakery item |
| Pizza base, oven-baked (Boboli) | judgment call: pizza bases/dough products are grouped with bakery products rather than "Breads" in common GI-table practice (distinct from sliced loaf bread); a bread-family assignment would also be plausible but this is the more standard fit |

## Vegetables (20g standard carb, 10g for the low-carb exception list) -- 5 foods

| food | standard carb | rationale |
|---|---|---|
| French Fries, baked (OreIda) | 20g | potato product; potato is not on Atkinson's low-carb vegetable exception list (beetroot/parsnip/pumpkin/carrot/peas/tomato sauces), so the standard 20g applies |
| Sweet corn, cooked in microwave | 20g | judgment call: Atkinson's article notes corn appears under both "Vegetables" and "Cereal grains"; classified here as Vegetables since it's fresh/cooked corn, not a milled grain product |
| Carrots, unpeeled, boiled | 10g | carrot is explicitly named on Atkinson's low-carb vegetable exception list |
| Carrots, diced, frozen | 10g | same exception |
| Peas, plain and frozen | 10g | peas explicitly named on the exception list |

## Snack foods and confectionery (25g standard carb) -- 7 foods

| food | rationale |
|---|---|
| Cheddar Cheese Crackers (Combos) | judgment call: "Combos" is a branded savory snack product (stuffed pretzel/cracker shape), grouped with savory snack foods rather than the standalone "Crackers" category (which fits plain crackers like saltines) |
| Cheddar Cheese Pretzels (Combos) | same Combos-brand reasoning |
| Soft pretzel, wheat | savory snack food |
| Microwave popcorn, butter flavor | savory snack food |
| Cheese Puffs, rice and corn (Pirate's Booty) | savory snack food |
| Peanut Butter Granola bars (Kudos) | matches Table 1's "snack bars" subgroup of this category |
| Chocolate covered almonds (Cocoavia) | judgment call: majority-chocolate-coated confectionery product (50g carbs/100g, far above raw almonds' ~20g), fits "sweet snacks and confectionery" subgroup rather than the "Nuts" category, which is for unprocessed nuts |

## Dairy products and alternatives (10g plain / 20g flavored-sweetened) -- 6 foods

| food | standard carb | rationale |
|---|---|---|
| Ice cream, premium chocolate, 15% fat | 20g | flavored/sweetened |
| Milk, reduced fat | 10g | plain |
| Yoghurt, Greek style, honey topped | 20g | flavored/sweetened (honey topped) |
| Yoghurt, black cherry | 20g | flavored/sweetened |
| Yoghurt, bourbon vanilla | 20g | flavored/sweetened |
| Yoghurt, natural, no added sugar | 10g | plain, name explicitly says "no added sugar" |

## Fruit and fruit products (15g standard carb) -- 10 foods

| food | rationale |
|---|---|
| Custard apple, raw | whole fruit |
| Pineapple, raw | whole fruit |
| Grapes, Crimson seedless | whole fruit |
| Grapes, green, Menidee, seedless | whole fruit |
| Watermelon, raw | whole fruit |
| Raisins | dried fruit, same category family |
| Strawberries, fresh, raw | whole fruit |
| Fruit Salad, canned (peach/pear/apricot/pineapple/cherry) | fruit product |
| Apricot fruit spread, no added sugar | matches Table 1's "fruit spreads, jams" subgroup of this category |
| Apricot fruit spread (Cottees) | same fruit-spreads subgroup |

## Fruit and vegetable juices (20g standard carb) -- 2 foods

| food | rationale |
|---|---|
| Orange juice | fruit juice, not on the tomato/carrot/vegetable-juice 10g exception list |
| Apple juice, unsweetened | fruit juice |

## Legumes (15g standard carb) -- 4 foods

| food | rationale |
|---|---|
| Hommus dip | chickpea-based; same legume-family reasoning `south_asian_category_mapping.md` used for chickpea entries |
| Baked Beans in Cheesy Tomato sauce (Heinz) | bean-based, tomato sauce is a minor prep detail on an otherwise plain legume dish |
| Baked Beans in Barbecue sauce (Heinz) | same reasoning |
| Baked Beans in Tomato sauce (Heinz) | same reasoning |

## Sugars and syrups (5g standard carb) -- 3 foods

| food | rationale |
|---|---|
| Manuka honey MGO 440+ | honey, canonical member of this category |
| Capilano Premium Honey | honey |
| Maple syrup, pure Canadian | syrup |

Note: this category's 5g standard portion is intentionally small (Atkinson
scales it to a condiment-sized serving, e.g. roughly a teaspoon of honey).
Combined with these foods' very high carb density (~67-82g/100g), the
implied serving weight the GL check computes is correspondingly small
(~6-7g) -- see `tests/test_phase_05.py` for how the plausibility range
accounts for this.

## Cereal grains (45g standard carb) -- 1 food

| food | rationale |
|---|---|
| Brown rice, instant (Uncle Ben's) | plain cooked/reconstituted rice, no other named component -- same "Cereal grains" reasoning as the South Asian mapping's plain-rice entries |

## Soups (20g standard carb) -- 2 foods

| food | rationale |
|---|---|
| Tomato soup, condensed, prepared with water (Campbell's) | soup product |
| Chunky Roast Chicken and Vegetable soup (Campbell's) | soup product |

## Summary

| category | count |
|---|---|
| Breads | 10 |
| Breakfast cereals | 5 |
| Bakery products | 8 |
| Vegetables | 5 |
| Snack foods and confectionery | 7 |
| Dairy products and alternatives | 6 |
| Fruit and fruit products | 10 |
| Fruit and vegetable juices | 2 |
| Legumes | 4 |
| Sugars and syrups | 3 |
| Cereal grains | 1 |
| Soups | 2 |
| **Total** | **63** |
