# South Asian food -> Atkinson et al. 2021 category mapping

Maps each of the 66 matched south_asian foods in `south_asian_nutrients.csv`
to one of Atkinson et al. 2021's 21 food categories, each of which has a
standardized carbohydrate portion (grams) used to compute GL:
`GL = GI/100 * standardized_carb_g`. This mapping is what
`tests/test_phase_04.py`'s GL sanity check uses to work out, per food, what
serving weight (in our decomposed, cooked-basis carbs_g) would contain that
category's standardized carb amount -- see
`south_asian_decomposition_notes.md`'s "GL sanity check methodology
correction" section for why this replaced the original (flawed) check.

8 south_asian foods are excluded from this mapping and from the sanity
check entirely: Butter chicken, Tandoori chicken, Chicken tikka masala,
Chicken curry (generic), Butter paneer (paneer makhani), Palak paneer, Dal
makhani, Chana masala. These are the Phase 2 amendment's documented
exceptions -- not sourced from Atkinson et al. at all, so they have no
category to map to and no Atkinson GL to sanity-check against.

Two entries were directly confirmed against Atkinson's source tables (GI x
category_carb / 100 reproduces the recorded GL exactly): "Chapatti" -> GI 58
x 35/100 = 20.3 ~ 20 (Regional or traditional foods, 35g), and "Roti
(unleavened flatbread), whole wheat flour" -> GI 45 x 15/100 = 6.75 ~ 7
(Breads, 15g). Everything else below is assigned by matching food nature and
naming convention to the category descriptions, since Atkinson's per-food
category assignment for these specific product entries isn't independently
re-derivable from the data we have -- flagged as a judgment call throughout.

## Cereal grains (45g standardized carb) -- 8 foods

Plain cooked rice/millet with no other named ingredient or preparation
mixed in -- matches Atkinson's "Cereal grains" category (raw/simply-cooked
grains, as opposed to composite regional dishes).

| food | rationale |
|---|---|
| Basmati rice, white, polished, cooked 10 min | plain cooked rice, no other component |
| Basmati rice (Dreamrice) | plain cooked branded basmati rice |
| Basmati rice, white, boiled (Mahatma) | plain cooked branded basmati rice |
| Basmati rice, white, boiled (SunRice) | plain cooked branded basmati rice |
| Basmati rice (Laila) | plain cooked branded basmati rice |
| Unpolished little millet, plain cooked | name explicitly says "plain cooked" |
| Unpolished foxtail millet, plain cooked | name explicitly says "plain cooked" |
| Pilaf porridge, whole grain | judgment call: "whole grain" framing reads closer to a plain cooked grain than a composite regional dish; no other named component |

## Legumes (15g standardized carb) -- 5 foods

| food | rationale |
|---|---|
| Chickpeas, canned, drained | plain legume, no other component |
| Chickpeas (Garbanzo beans, Bengal gram), canned | plain legume, no other component |
| Lentils, brown, canned, drained | plain legume, no other component |
| Rajmah (kidney beans), boiled | plain legume, no other component |
| Lentils, Mothbean, sprouted, cooked in buttermilk | judgment call: buttermilk-cooking is a minor prep detail on an otherwise plain legume, not a composite multi-ingredient regional dish |

## Breads (15g standardized carb) -- 1 food

| food | rationale |
|---|---|
| Roti (unleavened flatbread), whole wheat flour | confirmed directly: GI 45 x 15/100 = 6.75 ~ recorded GL 7 |

## Snack foods and confectionery (25g standardized carb) -- 2 foods

| food | rationale |
|---|---|
| Finger millet extruded snack | name explicitly says "snack"; matches a manufactured/extruded product, not a home-cooked regional dish |
| Laddu (popped amaranth, foxtail millet, legume, fenugreek) | laddus are a traditional sweet snack/confection bound with jaggery -- fits "confectionery" better than "regional or traditional foods" (which is used here for savory composite dishes) |

## Regional or traditional foods (35g standardized carb) -- 42 foods

Composite South Asian dishes (multiple named ingredients/components,
distinctive regional preparation) and flatbreads other than the one
confirmed "Breads" entry. Per the task's guidance, chapatti/naan/paratha and
dosa/idli/upma/dhokla/pongal/cheela-family dishes default here.

| food | rationale |
|---|---|
| Basmati rice pilau, with onion and curry powder | flavored/composite rice dish, not plain cooked grain |
| Chapatti (Elephant Atta Medium flour) | flatbread, regional-foods family (see "Chapatti" confirmation above) |
| Chapatti | confirmed directly: GI 58 x 35/100 = 20.3 ~ recorded GL 20 |
| Chapati, flatbread | flatbread, regional-foods family |
| Chapati, flatbread with 10% fenugreek | flatbread, regional-foods family |
| Naan bread | flatbread, regional-foods family (distinct from the one confirmed "Breads" roti) |
| Paratha, frozen, heated in dry pan | flatbread, regional-foods family |
| Rice dosa | composite regional dish |
| Rice idli (commercial dry mix) | composite regional dish |
| Upma | composite regional dish |
| Finger millet upma | composite regional dish |
| Finger millet flakes upma | composite regional dish |
| Finger millet vermicelli upma | composite regional dish |
| Basmati rice (microwave), with coconut sambol - Pakistan | rice + coconut sambol tested as one composite item |
| Basmati rice (microwave), with coconut sambol - India | rice + coconut sambol tested as one composite item |
| Basmati rice (rice cooker), with coconut sambal | rice + coconut sambol tested as one composite item |
| Basmati rice (rice cooker), with coconut sambol | rice + coconut sambol tested as one composite item |
| Broken wheat upma, with green gram, chutney | composite regional dish |
| Chapatti, wheat flour, thin, with green gram dhal | flatbread + dal side, composite |
| Cheela, bengal gram | composite regional dish |
| Cheela, bengal gram, fermented batter | composite regional dish |
| Cheela, green gram | composite regional dish |
| Cheela, green gram, fermented batter | composite regional dish |
| Dhokla, chickpea and wheat semolina | composite regional dish |
| Dhokla, parboiled rice, Bengal gram, green gram, with chutney | composite regional dish |
| Dosa, foxtail millet and black gram dhal | composite regional dish |
| Dosa, rice and black gram dhal | composite regional dish |
| Dosai (parboiled and raw rice), with chutney | composite regional dish |
| Idli, brown, parboiled rice and black gram dhal, with sambar | composite regional dish |
| Idli (parboiled and raw rice, black dhal), with chutney | composite regional dish |
| Parantha, radish, wheat/mothbean/Bengal gram, with curd | composite regional dish |
| Poha, rice flakes with ground nuts | composite regional dish |
| Pongal, rice and roasted green gram dhal | composite regional dish |
| Poori, deep-fried wheat dough, with potato palya | composite regional dish |
| Porridge, scoured wheat, with gram mix | composite regional dish ("with gram mix" makes this multi-component, not a plain cooked grain) |
| Porridge, decorticated finger millet, with gram mix | composite regional dish |
| Puttu/Pittu, industrially-milled finger millet flour | composite regional dish (millet flour + coconut, steamed) |
| Puttu/Pittu, stone-ground finger millet flour | composite regional dish |
| Roti, 75% rice flour and 25% soy flour | judgment call: only the exact name "Roti (unleavened flatbread), whole wheat flour" was confirmed as "Breads"; this differently-named, differently-composed roti defaults to the regional-foods family instead of assuming the same category |
| Stringhoppers, red rice flour, with sambol/egg/gravy | composite regional dish |
| Tahlipeeth, wheat/bengal gram/green gram, with chutney | composite regional dish |
| Upittu, roasted semolina and onions | composite regional dish |

## Summary

| category | count |
|---|---|
| Cereal grains | 8 |
| Legumes | 5 |
| Breads | 1 |
| Snack foods and confectionery | 2 |
| Regional or traditional foods | 42 |
| (excluded: non-Atkinson exceptions) | 8 |
| **Total** | **66** |

*Note: the table above reflects the file's original state and is left as-is
per this amendment's additive-only scope -- see the correction to Rajmah's
category directly below, which supersedes this table's Legumes/Regional
counts (Legumes 5->4, Regional 42->43) and is what `tests/test_phase_05.py`
now uses for the GL check.*

## Amendment: additional spot-checks against the real Atkinson supplemental tables

This mapping was originally built by judgment-matching each food to
Atkinson's category *definitions*, because the actual supplemental tables
weren't available at the time (only two entries -- Chapatti and Roti --
had been independently arithmetic-confirmed). The real tables are now
available at `data/raw/atkinson_files/SupplementalTable1.pdf` and
`SupplementalTable2.pdf` (gitignored, not committed). 10 south_asian
foods spanning 4 categories were spot-checked directly against them:

| food | original category | Atkinson item # (table) | matched entry | GI/GL | result |
|---|---|---|---|---|---|
| Naan bread | Regional or traditional foods | #2083 (T1, p138) | "Naan bread (True Foods Pty Ltd, VIC, Australia), heated in microwave for 25 sec" (Australia, 2013) | 71/25 | **CONFIRMED** |
| Upma | Regional or traditional foods | #2091 (T1, p138) | "Upma" (India, 2018) | 71/25 | **CONFIRMED** |
| Basmati rice, white, polished, cooked 10 min | Cereal grains | #574 (T1, p40) | "Basmati, white, polished, cooked 10 min" (UK, 2009), under "Basmati, white rice, boiled" subheading | 50/23 | **CONFIRMED** |
| Chickpeas, canned, drained | Legumes | #1284 (T1, p87) | "Chickpeas, canned, drained (Edgell, Simplot Australia, Australia)" (2018), under "Chickpeas and chickpea products" subheading | 35/5 | **CONFIRMED** |
| Lentils, brown, canned, drained | Legumes | #1299 (T1, p88) | "Lentils, brown, canned, drained, Edgell's™ brand (Simplot Australia, Australia)" (2008) | 42/6 | **CONFIRMED** |
| Unpolished little millet, plain cooked | Cereal grains | #564 (T1, p40) | "Unpolished little millet, plain cooked (Earth 360, Kadiri, Andhra Pradesh, India)" (2017-18) | 89/40 | **CONFIRMED** |
| Finger millet extruded snack | Snack foods and confectionery | #1560 (T1, p105) | "Finger millet extruded snack" (India, 2018) | 65/16 | **CONFIRMED** |
| Dosa, rice and black gram dhal | Regional or traditional foods | #3856 (T2, p124) | "Dosa, made from rice and black gram dhal" (India, 2015) | 55/19 | **CONFIRMED** (found in Table 2, not Table 1) |
| Idli (parboiled and raw rice, black dhal), with chutney | Regional or traditional foods | #3863 (T2, p124) | "Idli (parboiled and raw rice with black dhal, soaked, ground, fermented, steamed) with chutney" (India, 1998) | 60/21 | **CONFIRMED** (found in Table 2, not Table 1) |
| Rajmah (kidney beans), boiled | Legumes | #3891 (T2, p126) | "Rajmah (Phaseolus vulgaris), boiled" (India, 1981) | 19/7 | **CORRECTED** -- real source places this specific entry under **Regional or traditional foods (35g)**, not Legumes (15g). Page 126 falls within Table 2's Regional or Traditional Foods page range (112-134), not its Legumes range (70-78). Likely explanation: this is an older (1981), India-specific single-food test that the reviewers filed among the regional-foods literature rather than the generic legumes literature, unlike the newer branded "Chickpeas"/"Lentils" entries above which are in the Legumes section proper. |

**Result: 9/10 confirmed, 1/10 corrected.** All 4 spot-checked categories
(Cereal grains, Legumes, Snack foods and confectionery, Regional or
traditional foods) had at least one directly-confirmed entry. Combined
with the 2 arithmetic-confirmed foods from the original mapping (Chapatti,
Roti), this is now 11 of the 66 south_asian foods with direct source
confirmation.

**Correction applied**: "Rajmah (kidney beans), boiled" moves from Legumes
(15g standard carb) to Regional or traditional foods (35g standard carb)
in `tests/test_phase_05.py`'s category assignment. carbs_g=19.44 for this
food, so the implied serving weight changes from 15/19.44*100=77.2g (old,
Legumes) to 35/19.44*100=180.0g (new, Regional or traditional foods) --
both are within the 5-600g plausibility range, so this correction does not
cause a test failure.
