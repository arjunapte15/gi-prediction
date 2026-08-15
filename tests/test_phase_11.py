import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "parser"))

from meal_parser import match_food  # noqa: E402

# (input string, expected match) -- expected=None means "should report not
# found," not "should crash."
TEST_CASES = [
    ("Naan bread", "Naan bread"),  # exact match
    ("Doughnutt", "Doughnut"),  # typo (extra trailing letter)
    ("raisin", "Raisins"),  # plural in dataset, singular query
    ("donut", "Doughnut"),  # known alias, from the draft table
    ("zzxxqqjjbbnnmm12345", None),  # garbage -> not found
]


def test_fixed_match_cases():
    failures = []
    for query, expected in TEST_CASES:
        actual = match_food(query)
        if actual != expected:
            failures.append(f"match_food({query!r}) = {actual!r}, expected {expected!r}")
    assert not failures, "\n".join(failures)
