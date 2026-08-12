import csv
from pathlib import Path

RAW_CSV = Path(__file__).resolve().parents[1] / "data" / "raw" / "gi_gl_raw.csv"


def _read_rows():
    with open(RAW_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_row_count_in_range():
    rows = _read_rows()
    assert 120 <= len(rows) <= 150


def test_gi_within_bounds():
    rows = _read_rows()
    for row in rows:
        gi = float(row["GI"])
        assert 0 <= gi <= 110


def test_no_duplicate_food_cuisine_pairs():
    rows = _read_rows()
    pairs = [(row["food_name"], row["cuisine"]) for row in rows]
    assert len(pairs) == len(set(pairs))


def test_no_null_gi_values():
    rows = _read_rows()
    for row in rows:
        assert row["GI"] is not None and row["GI"].strip() != ""


def test_both_cuisines_represented():
    rows = _read_rows()
    cuisines = {row["cuisine"] for row in rows}
    assert "south_asian" in cuisines
    assert "american" in cuisines
