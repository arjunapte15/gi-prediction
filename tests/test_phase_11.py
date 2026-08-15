import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "parser"))

from meal_parser import load_aliases, match_food  # noqa: E402


def test_exact_match():
    result = match_food("Naan bread")
    assert result["status"] == "matched"
    assert result["food"]["food_name"] == "Naan bread"


def test_typo_match():
    result = match_food("Doughnutt")
    assert result["status"] == "matched"
    assert result["food"]["food_name"] == "Doughnut"


def test_plural_match():
    """Under the old single-best-match approach this silently resolved to
    "Raisins" alone. With ambiguity detection, "raisin" genuinely ties
    closely between "Raisins" (WRatio 92.31) and "Cranberry Raisin muffin"
    (90.00, within the 10-point margin) -- correctly surfaced as ambiguous
    rather than silently picking one."""
    result = match_food("raisin")
    assert result["status"] == "ambiguous"
    candidate_names = {c["food_name"] for c in result["candidates"]}
    assert "Raisins" in candidate_names
    assert "Cranberry Raisin muffin" in candidate_names


def test_known_alias_match():
    result = match_food("donut")
    assert result["status"] == "matched"
    assert result["food"]["food_name"] == "Doughnut"


def test_garbage_not_found():
    result = match_food("zzxxqqjjbbnnmm12345")
    assert result == {"status": "not_found"}


def test_bare_ambiguous_term_returns_multiple_candidates():
    """'dosa' fuzzy-matches two distinct dosa dishes at the same top score
    (see the Phase 11 amendment report) -- this must surface as "ambiguous"
    with both candidates, not silently pick one."""
    result = match_food("dosa")
    assert result["status"] == "ambiguous"
    candidate_names = {c["food_name"] for c in result["candidates"]}
    assert len(result["candidates"]) >= 2
    assert "Dosa, rice and black gram dhal" in candidate_names
    assert "Rice dosa" in candidate_names


def test_renamed_almonds_alias_still_matches():
    """The 'almonds' alias was renamed to 'chocolate covered almonds' so
    bare 'almonds' no longer silently resolves via a curated alias -- the
    fuller phrase must still resolve correctly."""
    result = match_food("chocolate covered almonds")
    assert result["status"] == "matched"
    assert result["food"]["food_name"] == "Chocolate covered almonds (Cocoavia)"


def test_bare_almonds_no_longer_uses_alias_table():
    aliases = load_aliases()
    assert "almonds" not in aliases
