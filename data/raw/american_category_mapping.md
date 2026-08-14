# American food -> Atkinson et al. 2021 category mapping

Maps each of the 63 matched american foods in `american_nutrients.csv` to one
of Atkinson et al. 2021's 21 food categories, each of which has a
standardized carbohydrate portion (grams) used to compute GL:
`GL = GI/100 * standardized_carb_g`. This mapping is what
`tests/test_phase_05.py`'s GL sanity check uses, in the same way
`south_asian_category_mapping.md` was used by `tests/test_phase_04.py`.

## Amendment: rebuilt from the real supplemental tables

**This file was rebuilt from source data and supersedes the original
Phase 5 version**, which had to rely on judgment-matching each food to
Atkinson's category *definitions* because the actual supplemental tables
weren't available at the time (only the journal article itself was).

The real tables are now available at `data/raw/atkinson_files/SupplementalTable1.pdf`
(2091 items, ISO-standard methodology -- preferred) and `SupplementalTable2.pdf`
(1927 items, non-ISO methodology -- fallback). Both are gitignored and not
committed (copyrighted/paywalled, same handling as `IFCT2017.pdf` and
`atkinson21.pdf`).

**Every one of the 63 american foods was found directly in Supplemental
Table 1** (none needed the Table 2 fallback, and none needed to fall back
to a judgment-only assignment). Each entry below cites the matched
Atkinson item number, its exact source description, and its GI/GL --
which in every case reproduces this dataset's `gi_gl_raw.csv` values
exactly, confirming both the category assignment and the original GI/GL
sourcing from Phase 2 in one pass.

**One category correction resulted**: "Soft pretzel, wheat" was originally
assigned to Snack foods and confectionery (25g) by judgment (pretzels
read as a savory snack). The real table places it in **Breads (15g)**
instead -- item #208, page 15 of Table 1, in a "Pretzels" subsection
within the Breads category (pages 11-25). This is corrected below; see
the amendment's regression-test section in `data_dictionary.md` for the
GL-plausibility impact (none -- still well within range).

Every other food's category matched the original judgment-based
assignment exactly, including several non-obvious calls that are now
directly confirmed rather than inferred:
- Pizza base (Boboli) -> Bakery products, not Breads (item #68, p6)
- Both Combos-brand items -> Snack foods and confectionery, not the
  literal Crackers category -- and the source table itself files them
  under a "Combos Snacks" sub-label (items #1550-1551, p105), so this
  wasn't even a close call
- Chocolate covered almonds (Cocoavia) -> Snack foods and confectionery
  (item #1603, "Cocoavia™ high flavanol chocolate covered almonds"), not
  the Nuts category
- Sweet corn -> Vegetables (not the alternate Cereal grains categorization
  the article mentions corn can take), standard 20g portion (not a
  low-carb exception)
- Carrots and peas -> Vegetables, 10g low-carb-exception portion (source
  text confirms: "except for green peas, pumpkin, carrot, parsnip, and
  tomato sauce products where 10 g was used")
- Orange juice and Apple juice -> a "Fruit and vegetable juices" 20g
  sub-portion declared partway through the Fruit and fruit products page
  range (p80 in Table 1: "Average available carbohydrate portion = 20 g
  ... except for tomato juice and carrot juice where 10 g was used"),
  distinct from the 15g portion declared at the top of that same
  page-range section (p73) for whole fruit/fruit products. This
  "Fruit and vegetable juices" category is not a separate top-level
  entry in Table 1's own table of contents (unlike the journal article's
  Methods section, which lists it as one of the 21 categories) -- it's
  nested as a sub-declaration inside the Fruit and fruit products pages.
  Page-range lookup alone would have missed this; the item's *local*
  "Average available carbohydrate portion" declaration is what's
  authoritative.

## The 21 categories and standardized carbohydrate portions

Confirmed against the "Average available carbohydrate portion" declarations
printed at the start of each category/sub-category in Supplemental Table 1
itself (not just the journal article's Methods section, which was the only
source for this list in the original Phase 5 version).

| category | standard carb (g) | notes |
|---|---|---|
| Bakery products | 30 | confirmed, p2 |
| Beverages | 25 | 10g for beer; confirmed, p6 |
| Breads | 15 | confirmed, p11 |
| Breakfast cereals | 20 | confirmed, p26 |
| Cereal grains | 45 | confirmed, p37 |
| Cookies | 20 | |
| Crackers | 15 | |
| Dairy products and alternatives | 10 / 20 | 10g plain, 20g flavored/sweetened; confirmed, p60 |
| Fruit and fruit products | 15 | confirmed, p73; includes fruit spreads/jams subgroup |
| Fruit and vegetable juices | 20 | 10g for tomato/carrot juice; sub-declaration within Fruit and fruit products pages, confirmed p80 |
| Infant formula and weaning foods | 10 | |
| Legumes | 15 | confirmed, p87 |
| Meal replacements and weight management products | 20 | |
| Nutritional support products | 30 | |
| Nuts | 5 | |
| Pasta and noodles | 40 | |
| Snack foods and confectionery | 25 | confirmed, p102/p115 boundary |
| Soups | 20 | confirmed, p115/p116 boundary |
| Sugars and syrups | 5 | 2.5g for sugar replacers; confirmed, p116 |
| Vegetables | 20 | 10g for green peas/pumpkin/carrot/parsnip/tomato sauce; confirmed, p120 |
| Regional or traditional foods | 35 | |

## Breads (15g standard carb) -- 11 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| White bread | #235 (p17) | "White bread" (UK, 2006) | 59/9 | judgment call: several generic "White bread" entries across the table share GI=59, GL=9; item #235 sits under the "White wheat flour bread" subheading and is the plainest match for an unbranded name. Category is unambiguous regardless of which specific entry is the true source. |
| Burger Buns, 100% Whole wheat | #164 (p12) | "Burger Buns, 100% Whole wheat Gigantico, President's Choice® Blue Menu™ (Loblaw Brands Limited, Canada)" | 62/9 | exact name+brand match |
| Rye bread, Pumpernickel | #216 (p16) | "Pumpernickel Rye bread (Van der Meulen BV, Netherlands)" | 49/7 | judgment call: word order flipped ("Pumpernickel Rye bread" vs. our "Rye bread, Pumpernickel") -- same product |
| Multigrain bread, gluten-free | #159 (p12) | "Multigrain bread, gluten-free (Country Life Bakery, Dandenong, Australia)" | 79/12 | exact name+brand match |
| Multigrain batch bread | #179 (p13) | "Multigrain batch bread" (UK, 2005) | 62/9 | exact name match |
| White sourdough bread, gluten free | #163 (p12) | "White sourdough bread, gluten free, sliced (Dr Schär AG/SPA, Italy)" | 63/9 | exact name match (our dataset drops "sliced") |
| Oat bran concentrate bread | #203 (p15) | "Degraded oat bran concentrate bread (50% oat bran concentrate + 50% wheat, 5 h proving time)" (Norway, 2019) | 64/10 | judgment call: our name drops the "Degraded" process qualifier (there's also a paired "Optimal" variant, GI=57, at item #204 -- item #203 is the one matching our recorded GI/GL) |
| Fruit and Muesli bread (Bürgen) | #151 (p12) | "Fruit and Muesli bread, Bürgen® (Tip Top Bakeries, Australia)" | 53/8 | exact name+brand match |
| Muesli bread (packet mix) | #156 (p12) | "Muesli bread, made from packet mix in bread making machine (Con Agra Inc., USA)" | 54/8 | exact name match |
| Mixed Grain bread roll (Bürgen) | #167 (p13) | "Mixed Grain bread roll, Bürgen™ (Tip Top Bakeries, Chatswood, Australia)" | 52/8 | exact name+brand match |
| Soft pretzel, wheat | #208 (p15) | "Soft pretzel, wheat" (USA, 2011) | 66/10 | exact name match. **Category correction**: originally assigned to Snack foods and confectionery by judgment; the source table places pretzels in a subsection of Breads instead |

## Breakfast cereals (20g standard carb) -- 5 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| Oats, rolled, uncooked | #499 (p35) | "Oats, rolled, uncooked (Lowan's Whole Foods, Box Hill, Australia)" | 59/12 | exact name+brand match -- confirms original judgment call that raw/rolled oats sit under Breakfast cereals, not Cereal grains |
| Weet-Bix breakfast biscuit | #454 (p32) | "Weet-Bix™ (Sanitarium, Australia)" (2004) | 69/14 | judgment call: a second identical Weet-Bix entry (item #455, 2001) has the same GI/GL; either is a correct match |
| Rice Bubbles (Kellogg's) | #446 (p32) | "Rice Bubbles™ (Kellogg's, Australia)" (2000) | 85/17 | exact name+brand match |
| Cornflakes | #366 (p26) | "Cornflakes" (France, 2019) | 66/13 | judgment call: several differently-scored Cornflakes entries exist; item #366 is the one matching our recorded GI/GL |
| Bran Flakes (Kellogg's) | #361 (p26) | "Bran Flakes™ (Kellogg's, Australia)" (2000) | 74/15 | exact name+brand match |

## Bakery products (30g standard carb) -- 8 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| Doughnut | #61 (p6) | "Doughnut" (Oman, 2020) | 75/23 | exact name match |
| Chocolate cake (Betty Crocker) | #3 (p2) | "Chocolate cake made from packet mix with chocolate frosting (Betty Crocker, General Mills Inc., Minneapolis, USA)" | 38/11 | exact name+brand match |
| Danish Pastry, Apple and Peach | #26 (p3) | "Danish Pastry, Apple & Peach, light (Sara Lee Bakery, Australia)" | 50/15 | exact name match |
| Apple Blueberry muffin | #32 (p4) | "Apple Blueberry muffin (Sara Lee Bakery, Australia)" | 49/15 | exact name match |
| Banana, oat and honey muffin | #35 (p4) | "Banana, oat and honey muffin" (Australia, 2000) | 65/20 | exact name match |
| Cranberry Raisin muffin | #41 (p4) | "Cranberry Raisin muffin" (Australia, 2013) | 43/13 | exact name match |
| Apricot, coconut and honey muffin | #34 (p4) | "Apricot, coconut and honey muffin" (Australia, 2000) | 60/18 | exact name match |
| Pizza base, oven-baked (Boboli) | #68 (p6) | "Pizza base, baked in oven at 220°C for 9 min (Boboli, Orograin Bakeries Manufacturing Inc, PA, USA)" | 52/16 | exact name+brand match -- confirms original judgment call (Bakery products, not Breads) |

## Vegetables (20g standard carb, 10g for the low-carb exception list) -- 5 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | standard carb | name-matching notes |
|---|---|---|---|---|---|
| French Fries, baked (OreIda) | #1854 (p124) | "French Fries, baked 15 min (OreIda Golden Fries, H.J. Heinz Co, Pittsburgh, PA, USA)" | 64/13 | 20g | exact name+brand match; potato confirmed not on the low-carb exception list |
| Sweet corn, cooked in microwave | #1801 (p120) | "Sweet corn, cooked in microwave for 1.5 min" (Australia, 2015) | 51/10 | 20g | exact name match; confirms original judgment call (Vegetables, not the article's alternate Cereal grains categorization for corn) |
| Carrots, unpeeled, boiled | #1804 (p121) | "Carrots, unpeeled, boiled" (Australia, 2020) | 32/3 | 10g | exact name match; carrot confirmed on the source's own low-carb exception list |
| Carrots, diced, frozen | #1805 (p121) | "Carrots, diced, frozen (Talleys Group Ltd)" (New Zealand, 2011) | 31/3 | 10g | exact name+brand match |
| Peas, plain and frozen | #1797 (p120) | "Peas, plain and frozen (Talleys Group Ltd, New Zealand)" | 29/3 | 10g | exact name+brand match; peas confirmed on the exception list |

## Snack foods and confectionery (25g standard carb) -- 6 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| Cheddar Cheese Crackers (Combos) | #1550 (p105) | "Combos Snacks Cheddar Cheese Crackers (M&M/Mars, USA)" | 54/14 | exact name+brand match -- the source itself labels this "Combos Snacks," confirming the original judgment call over the literal Crackers category |
| Cheddar Cheese Pretzels (Combos) | #1551 (p105) | "Combos Snacks Cheddar Cheese Pretzels (M&M/Mars, USA)" | 52/13 | same, confirmed |
| Microwave popcorn, butter flavor | #1568 (p106) | "Poppin Microwave Popcorn, butter flavor (Green's Foods, Australia)" (2013) | 51/13 | judgment call: our name drops the "Poppin" brand prefix; several similarly-named entries with different GI exist (e.g. #1570, #1571), item #1568 matches our recorded GI/GL |
| Cheese Puffs, rice and corn (Pirate's Booty) | #1552 (p105) | "Cheese Puffs, made from rice and corn puffs, aged white cheddar extruded snack, Pirate's Booty brand (Robert's American Gourmet, Sea Cliff, NY, USA)" | 70/18 | exact name+brand match |
| Peanut Butter Granola bars (Kudos) | #1659 (p112) | "Kudos Milk Chocolate Granola bars, Peanut Butter flavor (M&M/Mars, USA)" | 45/11 | exact name+brand match (our name shortens the full product description) |
| Chocolate covered almonds (Cocoavia) | #1603 (p108) | "Cocoavia™ high flavanol chocolate covered almonds (M&M/Mars, USA)" | 21/5 | exact name+brand match -- confirms original judgment call (Snack foods, not Nuts) |

## Dairy products and alternatives (10g plain / 20g flavored-sweetened) -- 6 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | standard carb | name-matching notes |
|---|---|---|---|---|---|
| Ice cream, premium chocolate, 15% fat | #926 (p63) | "Ice cream, premium, Ultra chocolate, 15% fat (Sara Lee, Gosford, NSW, Australia)" | 37/7 | 20g flavored | exact match |
| Milk, reduced fat | #942 (p64) | "Milk, reduced fat (Dairy Farmers Ltd, Australia)" | 26/3 | 10g plain | exact name+brand match |
| Yoghurt, Greek style, honey topped | #982 (p66) | "Yoghurt, Greek style, honey topped (UK)" | 36/7 | 20g flavored | exact name match |
| Yoghurt, black cherry | #978 (p66) | "Yoghurt, black cherry (Finest, UK)" | 17/3 | 20g flavored | judgment call: a second "Yoghurt, black cherry" (Healthy Living Light, UK) exists with a different GI; item #978 matches our recorded GI/GL |
| Yoghurt, bourbon vanilla | #980 (p66) | "Yoghurt, bourbon vanilla (Finest, UK)" | 64/13 | 20g flavored | exact name match |
| Yoghurt, natural, no added sugar | #1046 (p70) | "No Added Sugar Natural yoghurt (Tamar Valley Dairy, Australia)" | 17/2 | 10g plain | judgment call: word order differs ("No Added Sugar Natural" vs. our "natural, no added sugar") -- same product |

## Fruit and fruit products (15g standard carb) -- 10 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| Custard apple, raw | #1098 (p74) | "Custard apple, raw, flesh only" (Australia, 2000) | 54/8 | exact name match |
| Pineapple, raw | #1164 (p79) | "Pineapple, raw (Ananas comosa)" (Malaysia, 2008) | 82/12 | exact name match |
| Grapes, Crimson seedless | #1133 (p76) | "Grapes, Crimson seedless" (Australia, 2008) | 50/8 | exact name match |
| Grapes, green, Menidee, seedless | #1134 (p76) | "Grapes, green, Menidee, seedless" (Australia, 2008) | 54/8 | exact name match |
| Watermelon, raw | #1145 (p77) | "Watermelon, raw (Citrullus vulgaris-red variety)" (Malaysia, 2008) | 55/8 | exact name match |
| Raisins | #1173 (p79) | "Raisins" (USA, 2009) | 61/9 | exact name match |
| Strawberries, fresh, raw | #1174 (p79) | "Strawberries, fresh, raw" (Australia, 2001) | 40/6 | exact name match |
| Fruit Salad, canned (peach/pear/apricot/pineapple/cherry) | #1177 (p80) | "Fruit Salad canned in fruit juice, containing peach, pear, apricot, pineapple and cherries (Langeberg and Ashton Foods Pty Ltd, South Africa)" | 54/8 | exact name match |
| Apricot fruit spread, no added sugar | #1207 (p82) | "Apricot 100% Pure Fruit spread, no added sugar (Freedom Foods, Australia)" | 43/6 | exact name match; fruit spreads/jams confirmed as a subgroup of this category, not Sugars and syrups |
| Apricot fruit spread (Cottees) | #1208 (p82) | "Apricot 100% Fruit Spread, Cottees™ (Cadbury Schweppes, Australia)" | 50/8 | exact name+brand match |

## Fruit and vegetable juices (20g standard carb) -- 2 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| Orange juice | #1196 (p81) | "Orange juice" (New Zealand, 2019) | 41/8 | exact name match; confirms this sits under a separate 20g sub-declaration within the Fruit and fruit products page range, not the 15g whole-fruit portion |
| Apple juice, unsweetened | #1180 (p80) | "Apple juice, unsweetened, reconstituted (Berrivale Orchards Ltd, Berri, Australia)" | 39/8 | exact name match |

## Legumes (15g standard carb) -- 4 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| Hommus dip | #1287 (p87) | "Chickpea Hommus dip, Chris' Traditional brand (Capitol Chilled Foods Pty Ltd, ACT, Australia)" | 22/3 | exact name match (our name drops "Chickpea" and "Traditional brand") |
| Baked Beans in Cheesy Tomato sauce (Heinz) | #1278 (p87) | "Baked Beans in Cheesy Tomato sauce (HJ Heinz, Australia)" | 44/7 | exact name+brand match |
| Baked Beans in Barbecue sauce (Heinz) | #1279 (p87) | "Baked Beans in Barbecue sauce (HJ Heinz, Australia)" | 47/7 | exact name+brand match |
| Baked Beans in Tomato sauce (Heinz) | #1282 (p87) | "Baked Beans in Tomato sauce (HJ Heinz, Australia)" | 40/6 | exact name+brand match |

## Sugars and syrups (5g standard carb) -- 3 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| Manuka honey MGO 440+ | #1758 (p118) | "Manuka honey, MGO 440+ (Manuka Health New Zealand Ltd)" | 65/3 | exact name match |
| Capilano Premium Honey | #1752 (p117) | "Capilano Premium Honey, blend of eucalypt & floral honeys (Capilano Honey Limited, QLD, Australia)" | 51/3 | exact name+brand match |
| Maple syrup, pure Canadian | #1785 (p119) | "Maple syrup, pure Canadian (Queen Foods, Australia)" | 54/3 | exact name match |

Note: this category's 5g standard portion is intentionally small (a
condiment-sized serving, e.g. roughly a teaspoon of honey). Combined with
these foods' very high carb density (~67-82g/100g), the implied serving
weight the GL check computes is correspondingly small (~6-7g) -- see
`tests/test_phase_05.py` for how the plausibility range accounts for this.

## Cereal grains (45g standard carb) -- 1 food

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| Brown rice, instant (Uncle Ben's) | #625 (p44) | "Brown Rice, Uncle Ben's® Ready Whole Grain (pouch) (Effem Foods, USA)" | 48/22 | exact name+brand match |

## Soups (20g standard carb) -- 2 foods

| food | Atkinson item # | matched entry (Table 1) | GI/GL | name-matching notes |
|---|---|---|---|---|
| Tomato soup, condensed, prepared with water (Campbell's) | #1735 (p116) | "Tomato soup, condensed, prepared with water (Campbell's Soup Company, Camden, NJ, USA)" | 52/10 | exact name+brand match |
| Chunky Roast Chicken and Vegetable soup (Campbell's) | #1724 (p115) | "Chunky Roast Chicken and Vegetable soup (Campbell's Soups, Homebush, NSW, Australia)" | 52/10 | exact name+brand match |

## Summary

| category | count | change from original |
|---|---|---|
| Breads | 11 | +1 (Soft pretzel, wheat, corrected in) |
| Breakfast cereals | 5 | unchanged |
| Bakery products | 8 | unchanged |
| Vegetables | 5 | unchanged |
| Snack foods and confectionery | 6 | -1 (Soft pretzel, wheat, corrected out) |
| Dairy products and alternatives | 6 | unchanged |
| Fruit and fruit products | 10 | unchanged |
| Fruit and vegetable juices | 2 | unchanged |
| Legumes | 4 | unchanged |
| Sugars and syrups | 3 | unchanged |
| Cereal grains | 1 | unchanged |
| Soups | 2 | unchanged |
| **Total** | **63** | |

**Result: 63/63 found directly in the source tables (all in Supplemental
Table 1, none needed Table 2 fallback, none left as judgment-only). 62/63
category assignments matched the original judgment-based mapping; 1
correction (Soft pretzel, wheat: Snack foods and confectionery -> Breads).**
