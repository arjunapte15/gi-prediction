"""Phase 11 (+ amendment): single-food fuzzy matching -- free text -> a
dataset food record.

At 129 foods, matching typed text against every entry via string-distance
comparison (rapidfuzz) is the one part of this pipeline with real, if still
tiny, computational cost -- everything upstream (Phases 1-10) was simple
arithmetic over a fixed table.

RETURN CONTRACT (match_food's return value) -- Phase 12's aggregation logic
is expected to branch on this, so it is documented here explicitly. Every
call returns a dict with a "status" key and exactly one of three shapes:

    {"status": "matched", "food": <food record>}
        Exactly one confident match. <food record> is the full row from
        data/processed/foods.json for that food (food_name, cuisine,
        fiber_g, fat_g, protein_g, carbs_g, sugar_g, GI, GL).

    {"status": "ambiguous", "candidates": [<food record>, <food record>, ...]}
        Multiple distinct entries are all plausible matches for a bare/
        generic query (e.g. "dosa" matches several dosa dishes) -- see
        "Ambiguity detection rule" below. Candidates are ordered by
        descending fuzzy-match score.

    {"status": "not_found"}
        Nothing cleared the match threshold; the food is not confidently in
        this dataset (or the query was empty/garbage).

Matching order for a query:
  1. Exact match (case-insensitive) against a real `food_name` -> "matched".
  2. The alias table (food_aliases.json) -- common/colloquial names and
     spelling variants curated to one specific dataset entry -> "matched".
     An alias is a deliberate, curated 1:1 mapping, so it is NOT run through
     ambiguity detection even if other entries would also fuzzy-match the
     same text; that is the point of curating it.
  3. Fuzzy string match (rapidfuzz WRatio) against every `food_name`,
     collected via ambiguity detection (below) into "matched", "ambiguous",
     or "not_found".

Ambiguity detection rule: every candidate scoring >= FUZZY_MATCH_THRESHOLD
(80) is a match candidate; among those, only ones scoring within
AMBIGUITY_MARGIN (10) points of the single highest score are kept (so a
clear top match with only weak, distant echoes below it still resolves to
"matched", not "ambiguous"). If exactly one candidate survives that filter,
the result is "matched"; if more than one survives, the result is
"ambiguous" with all of them listed.

This is a documented DRAFT rule (see the Phase 11 amendment report), not a
guarantee of clean results for every query -- WRatio's partial-ratio
behavior on shared single words (e.g. "rice" in "basmati rice") can pull in
loosely-related entries at a similar score tier, and can just as easily
under-detect real ambiguity when phrasing differs a lot (e.g. bare "idli"
scores far higher against "Rice idli (commercial dry mix)" than against the
dataset's other two idli dishes, which use very different wording). Known
cases are catalogued in the Phase 11 amendment report rather than papered
over here.

The alias table is a plain JSON dict (alias -> canonical food_name), loaded
at call time, not hardcoded into matching logic -- entries can be added,
removed, or corrected by editing food_aliases.json alone.
"""

import json
from pathlib import Path

from rapidfuzz import fuzz, process, utils

REPO_ROOT = Path(__file__).resolve().parents[1]
FOODS_JSON = REPO_ROOT / "data" / "processed" / "foods.json"
ALIASES_PATH = Path(__file__).resolve().parent / "food_aliases.json"

# rapidfuzz WRatio score (0-100) a fuzzy match must clear to be considered
# at all; below this, the query is reported as not found rather than
# guessing.
FUZZY_MATCH_THRESHOLD = 80

# How close (in WRatio points) a candidate must be to the single highest-
# scoring candidate to count as a genuine alternative rather than a weak,
# distant echo of it.
AMBIGUITY_MARGIN = 10


def load_food_records(path=FOODS_JSON):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_aliases(path=ALIASES_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def match_food(
    query,
    records=None,
    aliases=None,
    threshold=FUZZY_MATCH_THRESHOLD,
    ambiguity_margin=AMBIGUITY_MARGIN,
):
    """Returns a dict per the RETURN CONTRACT documented in the module
    docstring: {"status": "matched"|"ambiguous"|"not_found", ...}."""
    if records is None:
        records = load_food_records()
    if aliases is None:
        aliases = load_aliases()

    records_by_name = {r["food_name"]: r for r in records}
    food_names = list(records_by_name.keys())

    query_norm = query.strip().lower()
    if not query_norm:
        return {"status": "not_found"}

    for name in food_names:
        if name.strip().lower() == query_norm:
            return {"status": "matched", "food": records_by_name[name]}

    if query_norm in aliases:
        canonical = aliases[query_norm]
        return {"status": "matched", "food": records_by_name[canonical]}

    results = process.extract(
        query_norm,
        food_names,
        scorer=fuzz.WRatio,
        processor=utils.default_process,
        score_cutoff=threshold,
        limit=None,
    )
    if not results:
        return {"status": "not_found"}

    score_by_name = {name: score for name, score, _ in results}
    top_score = max(score_by_name.values())
    candidate_names = [name for name, score in score_by_name.items() if score >= top_score - ambiguity_margin]
    candidate_names.sort(key=lambda n: (-score_by_name[n], n))

    if len(candidate_names) == 1:
        return {"status": "matched", "food": records_by_name[candidate_names[0]]}
    return {"status": "ambiguous", "candidates": [records_by_name[n] for n in candidate_names]}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(match_food(query))
    else:
        print("Usage: python parser/meal_parser.py <free-text food name>")
