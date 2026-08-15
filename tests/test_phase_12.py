import sys
from fractions import Fraction
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "parser"))

from meal_aggregator import aggregate_meal  # noqa: E402


def hand_carb_weighted(gi_gl_pairs):
    """Independent, exact-fraction re-implementation of the carb-weighting
    math (carb_i = GL_i / (GI_i/100), meal_GI = 100 * sum(GL) / sum(carb),
    meal_GL = sum(GL)) used to hand-verify expected test values, kept
    separate from meal_aggregator.py's own implementation."""
    total_carb = Fraction(0)
    total_gl = Fraction(0)
    for gi, gl in gi_gl_pairs:
        carb = Fraction(gl, 1) * 100 / Fraction(gi, 1) if gi != 0 else Fraction(0)
        total_carb += carb
        total_gl += Fraction(gl, 1)
    meal_gi = float(Fraction(100) * total_gl / total_carb) if total_carb != 0 else 0.0
    return meal_gi, float(total_gl)


def test_single_food_meal_returns_its_own_gi_gl_unchanged():
    result = aggregate_meal(["Naan bread"])
    assert result["meal_status"] == "resolved"
    assert result["GI"] == pytest.approx(71.0)
    assert result["GL"] == pytest.approx(25.0)
    assert len(result["foods"]) == 1
    assert result["foods"][0]["food_name"] == "Naan bread"
    assert result["foods"][0]["weight"] == pytest.approx(1.0)


def test_two_food_meal_carb_weighted_aggregation():
    """Naan bread (GI=71, GL=25) + Chana masala (GI=35, GL=8). Naan
    contributes far more reference carbs (~35.2g) than chana masala
    (~22.9g), so meal GI should sit closer to naan's GI than a plain
    average of 53.0 would suggest."""
    expected_gi, expected_gl = hand_carb_weighted([(71, 25), (35, 8)])
    result = aggregate_meal(["Naan bread", "Chana masala"])
    assert result["meal_status"] == "resolved"
    assert result["GI"] == pytest.approx(expected_gi)
    assert result["GL"] == pytest.approx(expected_gl)
    assert expected_gi != pytest.approx((71 + 35) / 2)  # not a plain average
    weights = {f["food_name"]: f["weight"] for f in result["foods"]}
    assert weights["Naan bread"] > weights["Chana masala"]
    assert sum(weights.values()) == pytest.approx(1.0)


def test_second_two_food_meal_carb_weighted_aggregation():
    """Doughnut (GI=75, GL=23) + Watermelon, raw (GI=55, GL=8)."""
    expected_gi, expected_gl = hand_carb_weighted([(75, 23), (55, 8)])
    result = aggregate_meal(["Doughnut", "Watermelon, raw"])
    assert result["meal_status"] == "resolved"
    assert result["GI"] == pytest.approx(expected_gi)
    assert result["GL"] == pytest.approx(expected_gl)


def test_three_food_meal_with_zero_gi_dish():
    """Chapati (GI=63, GL=22) + Rajmah (GI=19, GL=7) + Butter chicken
    (GI=0, GL=0, documented negligible-carb dish -- contributes 0 carb
    weight, not a division-by-zero crash)."""
    expected_gi, expected_gl = hand_carb_weighted([(63, 22), (19, 7), (0, 0)])
    result = aggregate_meal(["Chapati, flatbread", "Rajmah (kidney beans), boiled", "Butter chicken"])
    assert result["meal_status"] == "resolved"
    assert result["GI"] == pytest.approx(expected_gi)
    assert result["GL"] == pytest.approx(expected_gl)
    weights = {f["food_name"]: f["weight"] for f in result["foods"]}
    assert weights["Butter chicken"] == pytest.approx(0.0)


def test_matched_plus_not_found_needs_clarification_without_crashing():
    result = aggregate_meal(["Naan bread", "zzxxqqjjbbnnmm12345"])
    assert result["meal_status"] == "needs_clarification"
    assert result["resolved_foods"] == ["Naan bread"]
    assert result["ambiguous_foods"] == []
    assert result["unmatched_foods"] == ["zzxxqqjjbbnnmm12345"]
    assert "GI" not in result
    assert "GL" not in result


def test_matched_plus_ambiguous_needs_clarification_without_crashing():
    result = aggregate_meal(["Naan bread", "dosa"])
    assert result["meal_status"] == "needs_clarification"
    assert result["resolved_foods"] == ["Naan bread"]
    assert result["unmatched_foods"] == []
    assert len(result["ambiguous_foods"]) == 1
    ambiguous_entry = result["ambiguous_foods"][0]
    assert ambiguous_entry["input"] == "dosa"
    assert "Dosa, rice and black gram dhal" in ambiguous_entry["candidates"]
    assert "Rice dosa" in ambiguous_entry["candidates"]
    assert "GI" not in result
    assert "GL" not in result
