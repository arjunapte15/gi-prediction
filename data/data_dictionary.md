# Data Dictionary

To be filled in once a data source is selected (Phase 2+).

## Documented exceptions

Eight North Indian meat/paneer/legume dishes were added to `data/raw/gi_gl_raw.csv`
(south_asian cuisine) that are absent from Atkinson et al. 2021 because that paper's
own methodology excludes "mixed meals" (e.g. dishes like "spaghetti Bolognese") from
GI testing. They are included here anyway so the app can recognize and log them, with
GI/GL values reasoned from first principles rather than sourced from a lab study.
These are **not** lab-tested GI values.

- **Butter chicken, Tandoori chicken, Chicken tikka masala, Chicken curry (generic),
  Butter paneer (paneer makhani), Palak paneer** — GI = 0, GL = 0. These dishes are
  protein/fat-dominant with negligible carbohydrate content, so a near-zero glycemic
  response is scientifically defensible. This is a reasoned estimate, not a
  placeholder and not a lab measurement.
- **Dal makhani** — GI = 30, GL = 5. Legume-dominant dish; GI estimated from the known
  GI of its base legumes already in this dataset (Table 1: "Lentils, brown, canned"
  GI=42, "Rajmah, boiled" GI=19, "Chickpeas, canned" GI=35-38), adjusted downward for
  the enriching effect of added fat (butter/cream tends to lower GI further). GL
  computed from an estimated standard-serving carb content of ~18g.
- **Chana masala** — GI = 35, GL = 8. Same legume-GI-basis reasoning as dal makhani.
  GL computed from an estimated standard-serving carb content of ~22g, which includes
  potato per the source recipe.
