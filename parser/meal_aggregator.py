"""Phase 12: multi-food carb-weighted meal aggregation.

Turns a list of free-text food queries -- each resolved individually via
Phase 11's `meal_parser.match_food` -- into a single meal-level GI/GL, or a
structured report of what is blocking that computation.

PORTION-SIZE ASSUMPTION (documented, not guessed per food)
------------------------------------------------------------
This project's dataset (data/processed/foods.json) records no serving size
for a food beyond what is implicit in its GI and GL: per
`data/data_dictionary.md`'s "GL methodology" section,
    GL = GI / 100 * category_standard_carb_g
where `category_standard_carb_g` is Atkinson et al. 2021's standardized
available-carbohydrate reference portion for that food's category (e.g.
Breads=15g, Cereal grains=45g). Rather than inventing a new, undocumented
per-food gram assumption for this phase, this module reuses that same
reference portion: each food in a meal is assumed to be present in the
amount that contains `category_standard_carb_g` grams of available carb --
recovered per food by solving the data dictionary's own formula for carbs:

    carb_contribution = GL / (GI / 100)      if GI > 0
                       = 0                    if GI == 0

The GI == 0 case (Butter chicken, Tandoori chicken, etc. -- see the data
dictionary's "Documented GI/GL exceptions") is not a division-by-zero
workaround: those dishes are already documented as protein/fat-dominant
with negligible carbohydrate content, so a carb_contribution of 0 is the
correct value, not a fallback guess.

LIMITATION (known, not fixed here): this assumes "one standard reference
serving of each food", not whatever quantity a user actually ate -- the
parser has no portion-size input from free text yet (no "2 rotis" / "a
small bowl of..." parsing). A future phase that adds that should replace
carb_contribution's source with a parsed quantity instead of this
standardized-portion stand-in.

CARB-WEIGHTED AGGREGATION MATH
------------------------------------------------------------
Given each resolved food's own (GI_i, GL_i, carb_contribution_i):

    meal_GL = sum(GL_i)
    meal_GI = 100 * meal_GL / sum(carb_contribution_i)

GL is additive across foods (each GL_i already is that food's absolute
glycemic contribution at its reference portion). meal_GI is the
carb-weighted mean of the per-food GI values -- a food supplying more of
the meal's total reference carbs pulls meal_GI further toward its own GI
than a minor side item does, rather than every food counting equally as in
a plain average.

AMBIGUOUS / NOT_FOUND HANDLING
------------------------------------------------------------
If every food resolves cleanly, meal_status="resolved" and the computed
meal GI/GL (plus a per-food breakdown) is returned. If any food comes back
"ambiguous" or "not_found" from the matcher, meal_status="needs_clarification"
is returned instead and no GI/GL is computed -- carb-weighting requires
knowing every food's contribution, so a partial number computed only from
the cleanly-matched foods would misrepresent the whole meal rather than
merely approximate it. Ambiguous foods keep their full, untouched candidate
list (as food names) so a future UI can ask the user to pick one; not_found
foods are listed separately so the user knows what to rephrase or that it
is simply not in the dataset.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from meal_parser import load_aliases, load_food_records, match_food  # noqa: E402


def aggregate_meal(food_queries, records=None, aliases=None):
    """Resolve every query in `food_queries` and carb-weight-aggregate them
    into a meal-level GI/GL.

    Returns one of two shapes:

    Needs clarification (any food ambiguous or not_found):
        {
            "meal_status": "needs_clarification",
            "resolved_foods": [<food_name>, ...],
            "ambiguous_foods": [{"input": <query>, "candidates": [<food_name>, ...]}, ...],
            "unmatched_foods": [<query>, ...],
        }

    Resolved (every food matched cleanly):
        {
            "meal_status": "resolved",
            "GI": <float>,
            "GL": <float>,
            "foods": [
                {"food_name": ..., "GI": ..., "GL": ..., "carb_contribution": ..., "weight": ...},
                ...
            ],
        }
    """
    if records is None:
        records = load_food_records()
    if aliases is None:
        aliases = load_aliases()

    resolved = []
    ambiguous_foods = []
    unmatched_foods = []

    for query in food_queries:
        result = match_food(query, records=records, aliases=aliases)
        if result["status"] == "matched":
            resolved.append(result["food"])
        elif result["status"] == "ambiguous":
            ambiguous_foods.append(
                {
                    "input": query,
                    "candidates": [c["food_name"] for c in result["candidates"]],
                }
            )
        else:
            unmatched_foods.append(query)

    if ambiguous_foods or unmatched_foods:
        return {
            "meal_status": "needs_clarification",
            "resolved_foods": [food["food_name"] for food in resolved],
            "ambiguous_foods": ambiguous_foods,
            "unmatched_foods": unmatched_foods,
        }

    breakdown = []
    total_carb_contribution = 0.0
    total_gl = 0.0
    for food in resolved:
        gi = food["GI"]
        gl = food["GL"]
        carb_contribution = (gl / (gi / 100)) if gi > 0 else 0.0
        breakdown.append(
            {
                "food_name": food["food_name"],
                "GI": gi,
                "GL": gl,
                "carb_contribution": carb_contribution,
            }
        )
        total_carb_contribution += carb_contribution
        total_gl += gl

    for item in breakdown:
        item["weight"] = (
            item["carb_contribution"] / total_carb_contribution if total_carb_contribution > 0 else 0.0
        )

    meal_gi = 100 * total_gl / total_carb_contribution if total_carb_contribution > 0 else 0.0

    return {
        "meal_status": "resolved",
        "GI": meal_gi,
        "GL": total_gl,
        "foods": breakdown,
    }


if __name__ == "__main__":
    import json
    import sys as _sys

    if len(_sys.argv) > 1:
        print(json.dumps(aggregate_meal(_sys.argv[1:]), indent=2))
    else:
        print('Usage: python parser/meal_aggregator.py "<food 1>" "<food 2>" ...')
