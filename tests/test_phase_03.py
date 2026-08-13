import csv
from pathlib import Path

RAW_CSV = Path(__file__).resolve().parents[1] / "data" / "raw" / "gi_gl_raw.csv"
NUTRIENTS_CSV = Path(__file__).resolve().parents[1] / "data" / "raw" / "american_nutrients.csv"

NUTRIENT_COLUMNS = ["fiber_g", "fat_g", "protein_g", "carbs_g", "sugar_g"]


def _read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _american_food_names():
    rows = _read_rows(RAW_CSV)
    return {row["food_name"] for row in rows if row["cuisine"] == "american"}


def test_all_food_names_are_american_in_raw_csv():
    american_names = _american_food_names()
    rows = _read_rows(NUTRIENTS_CSV)
    for row in rows:
        assert row["food_name"] in american_names


def test_no_null_nutrient_values():
    rows = _read_rows(NUTRIENTS_CSV)
    for row in rows:
        for col in NUTRIENT_COLUMNS:
            assert row[col] is not None and row[col].strip() != ""


def test_nutrient_values_non_negative():
    rows = _read_rows(NUTRIENTS_CSV)
    for row in rows:
        for col in NUTRIENT_COLUMNS:
            assert float(row[col]) >= 0


def test_fiber_and_sugar_do_not_exceed_carbs():
    rows = _read_rows(NUTRIENTS_CSV)
    for row in rows:
        carbs = float(row["carbs_g"])
        assert float(row["fiber_g"]) <= carbs
        assert float(row["sugar_g"]) <= carbs
