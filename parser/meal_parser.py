"""Phase 11: single-food fuzzy matching -- free text -> a dataset food_name.

At 129 foods, matching typed text against every entry via string-distance
comparison (rapidfuzz) is the one part of this pipeline with real, if still
tiny, computational cost -- everything upstream (Phases 1-10) was simple
arithmetic over a fixed table.

Matching order for a query:
  1. Exact match (case-insensitive) against a real `food_name`.
  2. The alias table (food_aliases.json) -- common/colloquial names and
     spelling variants mapped to one specific dataset entry.
  3. Fuzzy string match (rapidfuzz WRatio) against every `food_name`, only
     accepted above FUZZY_MATCH_THRESHOLD; below that, "not found" (None).

The alias table is a plain JSON dict (alias -> canonical food_name), loaded
at call time, not hardcoded into matching logic -- entries can be added,
removed, or corrected by editing food_aliases.json alone. It is a DRAFT:
some entries are genuinely ambiguous in the dataset (e.g. "roti" vs
"chapati" -- see the Phase 11 report) and are included as a best guess
pending user confirmation, not a final decision.
"""

import json
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz, process, utils

REPO_ROOT = Path(__file__).resolve().parents[1]
FOODS_CSV = REPO_ROOT / "data" / "processed" / "foods.csv"
ALIASES_PATH = Path(__file__).resolve().parent / "food_aliases.json"

# rapidfuzz WRatio score (0-100) a fuzzy match must clear to be accepted;
# below this, the query is reported as not found rather than guessing.
FUZZY_MATCH_THRESHOLD = 80


def load_food_names(path=FOODS_CSV):
    df = pd.read_csv(path)
    return df["food_name"].tolist()


def load_aliases(path=ALIASES_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def match_food(query, food_names=None, aliases=None, threshold=FUZZY_MATCH_THRESHOLD):
    """Returns the matched food_name, or None if nothing matches confidently
    enough (garbage input, or a food genuinely not in the dataset)."""
    if food_names is None:
        food_names = load_food_names()
    if aliases is None:
        aliases = load_aliases()

    query_norm = query.strip().lower()
    if not query_norm:
        return None

    for name in food_names:
        if name.strip().lower() == query_norm:
            return name

    if query_norm in aliases:
        return aliases[query_norm]

    result = process.extractOne(
        query_norm,
        food_names,
        scorer=fuzz.WRatio,
        processor=utils.default_process,
        score_cutoff=threshold,
    )
    if result is None:
        return None
    matched_name, _score, _index = result
    return matched_name


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(match_food(query))
    else:
        print("Usage: python parser/meal_parser.py <free-text food name>")
