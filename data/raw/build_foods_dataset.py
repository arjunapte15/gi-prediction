"""Phase 5: merge gi_gl_raw.csv with american_nutrients.csv and
south_asian_nutrients.csv into data/processed/foods.csv and foods.json.

Excludes the 9 foods never matched to nutrient data in Phases 3-4 (8 south
asian, 1 american) -- see data/data_dictionary.md for the full list and
rationale. A food is excluded by simply not appearing in either nutrients
CSV, so the merge below is an inner join; the explicit EXCLUDED_FOOD_NAMES
set exists only to assert that exactly those 9, and no others, are dropped.
"""
import csv
import json
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = RAW_DIR.parent / "processed"

GI_GL_RAW = RAW_DIR / "gi_gl_raw.csv"
AMERICAN_NUTRIENTS = RAW_DIR / "american_nutrients.csv"
SOUTH_ASIAN_NUTRIENTS = RAW_DIR / "south_asian_nutrients.csv"

NUTRIENT_COLUMNS = ["fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g"]
OUTPUT_COLUMNS = ["food_name", "cuisine", "fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g", "GI", "GL"]

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


def _read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build():
    gi_gl_rows = _read_rows(GI_GL_RAW)
    nutrients_by_name = {}
    for row in _read_rows(AMERICAN_NUTRIENTS):
        nutrients_by_name[row["food_name"]] = row
    for row in _read_rows(SOUTH_ASIAN_NUTRIENTS):
        nutrients_by_name[row["food_name"]] = row

    merged = []
    dropped = []
    for row in gi_gl_rows:
        name = row["food_name"]
        nutrients = nutrients_by_name.get(name)
        if nutrients is None:
            dropped.append(name)
            continue
        merged.append({
            "food_name": name,
            "cuisine": row["cuisine"],
            "fiber_g": float(nutrients["fiber_g"]),
            "fat_g": float(nutrients["fat_g"]),
            "protein_g": float(nutrients["protein_g"]),
            "carbs_g": float(nutrients["carbs_g"]),
            "sugar_g": float(nutrients["sugar_g"]),
            "GI": float(row["GI"]),
            "GL": float(row["GL"]),
        })

    assert set(dropped) == EXCLUDED_FOOD_NAMES, (
        f"Dropped foods don't match the documented exclusion list.\n"
        f"Dropped but not expected: {set(dropped) - EXCLUDED_FOOD_NAMES}\n"
        f"Expected but not dropped: {EXCLUDED_FOOD_NAMES - set(dropped)}"
    )

    merged.sort(key=lambda r: (r["cuisine"], r["food_name"]))

    PROCESSED_DIR.mkdir(exist_ok=True)

    csv_path = PROCESSED_DIR / "foods.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in merged:
            writer.writerow(row)

    json_path = PROCESSED_DIR / "foods.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(merged)} rows to {csv_path} and {json_path}")
    print(f"Dropped {len(dropped)} unresolved foods (expected 9): {sorted(dropped)}")


if __name__ == "__main__":
    build()
