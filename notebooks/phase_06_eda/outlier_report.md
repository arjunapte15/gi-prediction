# Phase 6 EDA: outlier-flagging report

Source: `data/processed/foods.csv` (129 rows).

Method: IQR (Tukey's fences), flagged as < Q1 - 1.5*IQR or > Q3 + 1.5*IQR per column. Chosen over z-score because several nutrient columns are visibly right-skewed at this sample size (n=129), where z-score's normality assumption is a poor fit; IQR is based on order statistics and stays robust to skew.

## Zero-variance check

None flagged -- every numeric column has nonzero variance.


## Documented GI/GL=0 dishes (not outliers)

The following dishes carry `GI=0`/`GL=0` by documented first-principles reasoning (near-zero carbohydrate mixed meals excluded from Atkinson et al.'s lab testing), not measurement or coding error -- see `data/data_dictionary.md`, "Documented GI/GL exceptions". They will appear as low-end outliers on `GI` below; that is expected.

- Butter chicken
- Butter paneer (paneer makhani)
- Chicken curry (generic)
- Chicken tikka masala
- Palak paneer
- Tandoori chicken

## Per-column IQR outlier flags

### `fiber_g`

Q1=1.12, Q3=6.05, IQR=4.93, fence=[-6.27, 13.45]

| food_name | cuisine | value |
|---|---|---|
| Bran Flakes (Kellogg's) | american | 20.50 |

### `fat_g`

Q1=0.41, Q3=5.48, IQR=5.07, fence=[-7.20, 13.09]

| food_name | cuisine | value |
|---|---|---|
| Chocolate cake (Betty Crocker) | american | 15.00 |
| Butter chicken (documented GI=0 exception) | south_asian | 15.80 |
| Chicken tikka masala (documented GI=0 exception) | south_asian | 15.80 |
| Apple Blueberry muffin | american | 16.07 |
| Cranberry Raisin muffin | american | 16.10 |
| Banana, oat and honey muffin | american | 16.10 |
| Apricot, coconut and honey muffin | american | 16.10 |
| Hommus dip | american | 17.82 |
| Cheese Puffs, rice and corn (Pirate's Booty) | american | 17.86 |
| Cheddar Cheese Pretzels (Combos) | american | 17.86 |
| Danish Pastry, Apple and Peach | american | 18.50 |
| Peanut Butter Granola bars (Kudos) | american | 20.78 |
| Poha, rice flakes with ground nuts | south_asian | 21.17 |
| Butter paneer (paneer makhani) (documented GI=0 exception) | south_asian | 21.28 |
| Doughnut | american | 22.90 |
| Cheddar Cheese Crackers (Combos) | american | 25.00 |
| Microwave popcorn, butter flavor | american | 30.60 |
| Chocolate covered almonds (Cocoavia) | american | 37.07 |

### `protein_g`

Q1=3.21, Q3=7.90, IQR=4.69, fence=[-3.83, 14.94]

| food_name | cuisine | value |
|---|---|---|
| Cheela, green gram | south_asian | 15.92 |
| Cheela, green gram, fermented batter | south_asian | 15.92 |
| Tandoori chicken (documented GI=0 exception) | south_asian | 19.32 |

### `carbs_g`

Q1=20.00, Q3=47.53, IQR=27.53, fence=[-21.30, 88.83]

No outliers flagged.

### `sugar_g`

Q1=0.60, Q3=8.76, IQR=8.16, fence=[-11.64, 21.00]

| food_name | cuisine | value |
|---|---|---|
| Laddu (popped amaranth, foxtail millet, legume, fenugreek) | south_asian | 21.85 |
| Doughnut | american | 23.50 |
| Ice cream, premium chocolate, 15% fat | american | 25.40 |
| Chocolate covered almonds (Cocoavia) | american | 26.92 |
| Danish Pastry, Apple and Peach | american | 27.50 |
| Apple Blueberry muffin | american | 31.47 |
| Banana, oat and honey muffin | american | 31.50 |
| Apricot, coconut and honey muffin | american | 31.50 |
| Cranberry Raisin muffin | american | 31.50 |
| Chocolate cake (Betty Crocker) | american | 36.00 |
| Apricot fruit spread, no added sugar | american | 38.89 |
| Apricot fruit spread (Cottees) | american | 43.40 |
| Peanut Butter Granola bars (Kudos) | american | 44.29 |
| Maple syrup, pure Canadian | american | 59.92 |
| Raisins | american | 65.20 |
| Manuka honey MGO 440+ | american | 82.12 |
| Capilano Premium Honey | american | 82.12 |

### `GI`

Q1=39.00, Q3=63.00, IQR=24.00, fence=[3.00, 99.00]

| food_name | cuisine | value |
|---|---|---|
| Butter chicken (documented GI=0 exception) | south_asian | 0.00 |
| Butter paneer (paneer makhani) (documented GI=0 exception) | south_asian | 0.00 |
| Chicken curry (generic) (documented GI=0 exception) | south_asian | 0.00 |
| Chicken tikka masala (documented GI=0 exception) | south_asian | 0.00 |
| Palak paneer (documented GI=0 exception) | south_asian | 0.00 |
| Tandoori chicken (documented GI=0 exception) | south_asian | 0.00 |

### `GL`

Q1=8.00, Q3=19.00, IQR=11.00, fence=[-8.50, 35.50]

| food_name | cuisine | value |
|---|---|---|
| Unpolished foxtail millet, plain cooked | south_asian | 40.00 |
| Unpolished little millet, plain cooked | south_asian | 40.00 |

## Summary

- Rows: 129
- Zero-variance columns: 0
- Total outlier flags across all columns: 47
- Reminder: this report does not assert the data is clean. It surfaces candidates for human review per Phase 6's definition of done.
