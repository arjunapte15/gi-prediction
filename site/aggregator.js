// Carb-weighted meal aggregation -- JS port of parser/meal_aggregator.py
// (Phase 12). See that module's docstring for the full math derivation
// (portion-size assumption, carb-weighted aggregation formula) and the
// AMBIGUOUS/NOT_FOUND HANDLING contract this mirrors exactly: any
// ambiguous or not_found food blocks GI/GL computation entirely
// (meal_status = "needs_clarification"), no partial number is ever
// computed from only the cleanly-matched foods.

(function (root, factory) {
  if (typeof module !== "undefined" && module.exports) {
    module.exports = factory(require("./parser.js").matchFood);
  } else if (root) {
    root.GIApp = root.GIApp || {};
    root.GIApp.aggregator = factory(root.GIApp.matcher.matchFood);
  }
})(typeof window !== "undefined" ? window : undefined, function (matchFood) {
  // Port of meal_aggregator.aggregate_meal. Returns one of two shapes (see
  // parser/meal_aggregator.py's docstring for the exact contract):
  //   needs_clarification: { meal_status, resolved_foods, ambiguous_foods, unmatched_foods }
  //   resolved:            { meal_status, GI, GL, foods: [{food_name, GI, GL, carb_contribution, weight}, ...] }
  function aggregateMeal(foodQueries, records, aliases) {
    const resolved = [];
    const ambiguousFoods = [];
    const unmatchedFoods = [];

    for (const query of foodQueries) {
      const result = matchFood(query, records, aliases);
      if (result.status === "matched") {
        resolved.push(result.food);
      } else if (result.status === "ambiguous") {
        ambiguousFoods.push({
          input: query,
          candidates: result.candidates.map((c) => c.food_name),
        });
      } else {
        unmatchedFoods.push(query);
      }
    }

    if (ambiguousFoods.length > 0 || unmatchedFoods.length > 0) {
      return {
        meal_status: "needs_clarification",
        resolved_foods: resolved.map((f) => f.food_name),
        ambiguous_foods: ambiguousFoods,
        unmatched_foods: unmatchedFoods,
      };
    }

    const breakdown = [];
    let totalCarbContribution = 0.0;
    let totalGl = 0.0;
    for (const food of resolved) {
      const gi = food.GI;
      const gl = food.GL;
      const carbContribution = gi > 0 ? gl / (gi / 100) : 0.0;
      breakdown.push({ food_name: food.food_name, GI: gi, GL: gl, carb_contribution: carbContribution });
      totalCarbContribution += carbContribution;
      totalGl += gl;
    }

    for (const item of breakdown) {
      item.weight = totalCarbContribution > 0 ? item.carb_contribution / totalCarbContribution : 0.0;
    }

    const mealGi = totalCarbContribution > 0 ? (100 * totalGl) / totalCarbContribution : 0.0;

    return { meal_status: "resolved", GI: mealGi, GL: totalGl, foods: breakdown };
  }

  return { aggregateMeal };
});
