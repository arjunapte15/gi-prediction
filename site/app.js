// GI Prediction site — loads the food dataset client-side and wires the
// meal-text input to the fuzzy-matching parser (site/parser.js) and the
// carb-weighted meal aggregator (site/aggregator.js), which together
// produce the meal's predicted GI/GL.

window.GIApp = window.GIApp || {};

async function loadFoods() {
  const statusEl = document.getElementById("data-status");
  try {
    const response = await fetch("../data/processed/foods.json");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const foods = await response.json();
    window.GIApp.foods = foods;
    if (statusEl) {
      statusEl.textContent = `Loaded ${foods.length} foods.`;
    }
    return foods;
  } catch (err) {
    if (statusEl) {
      statusEl.textContent = "Failed to load food data.";
    }
    console.error("Failed to load foods.json:", err);
    throw err;
  }
}

async function loadAliases() {
  try {
    const response = await fetch("../parser/food_aliases.json");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const aliases = await response.json();
    window.GIApp.aliases = aliases;
    return aliases;
  } catch (err) {
    console.error("Failed to load food_aliases.json:", err);
    throw err;
  }
}

// Fetched for parity with the project's "exported coefficients get
// re-applied in JS" architecture, and made available on window.GIApp, but
// NOT used to compute the displayed meal GI/GL: the displayed number is
// each matched food's own recorded GI/GL, carb-weight-aggregated exactly
// per parser/meal_aggregator.py (site/aggregator.js). Re-deriving GI from
// this regression's macros instead would diverge from those recorded
// values by tens of GI points for some foods (it's a fitted approximation,
// not a lookup), which would silently disagree with the dataset this site
// otherwise treats as ground truth.
async function loadCoefficients() {
  try {
    const response = await fetch("../model/saved_model/coefficients.json");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const coefficients = await response.json();
    window.GIApp.coefficients = coefficients;
    return coefficients;
  } catch (err) {
    console.error("Failed to load coefficients.json:", err);
    throw err;
  }
}

function renderParseResults(results) {
  const list = document.getElementById("parse-results");
  const placeholder = document.querySelector("#parse-output .placeholder");
  if (!list) return;

  list.innerHTML = "";
  if (placeholder) {
    placeholder.style.display = results.length ? "none" : "";
  }

  for (const { input, result } of results) {
    const li = document.createElement("li");
    li.className = `parse-result parse-result--${result.status}`;

    if (result.status === "matched") {
      li.textContent = `"${input}" → ${result.food.food_name}`;
    } else if (result.status === "ambiguous") {
      const names = result.candidates.map((c) => c.food_name).join(", ");
      li.textContent = `"${input}" → ambiguous: ${names}`;
    } else {
      li.textContent = `"${input}" → not found`;
    }

    list.appendChild(li);
  }
}

function renderPrediction(aggregateResult) {
  const placeholder = document.querySelector("#prediction-output .placeholder");
  const container = document.getElementById("prediction-result");
  if (!container) return;

  container.innerHTML = "";
  if (placeholder) {
    placeholder.style.display = aggregateResult ? "none" : "";
  }
  if (!aggregateResult) return;

  if (aggregateResult.meal_status === "resolved") {
    const summary = document.createElement("p");
    summary.id = "prediction-summary";
    summary.innerHTML =
      `Meal GI: <span id="prediction-gi">${aggregateResult.GI.toFixed(1)}</span> · ` +
      `Meal GL: <span id="prediction-gl">${aggregateResult.GL.toFixed(1)}</span>`;
    container.appendChild(summary);

    const list = document.createElement("ul");
    list.id = "prediction-breakdown";
    for (const item of aggregateResult.foods) {
      const li = document.createElement("li");
      li.textContent =
        `${item.food_name} — GI ${item.GI}, GL ${item.GL}, ` +
        `carb contribution ${item.carb_contribution.toFixed(1)}g, ` +
        `weight ${(item.weight * 100).toFixed(1)}%`;
      list.appendChild(li);
    }
    container.appendChild(list);
  } else {
    const notice = document.createElement("p");
    notice.id = "prediction-clarification";
    notice.textContent = "Resolve the ambiguous/not-found food(s) above before a prediction can be calculated.";
    container.appendChild(notice);
  }
}

function runParser() {
  const textEl = document.getElementById("meal-text");
  if (!textEl) return;

  const lines = textEl.value
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  const foods = window.GIApp.foods || [];
  const aliases = window.GIApp.aliases || {};
  const results = lines.map((input) => ({
    input,
    result: window.GIApp.matcher.matchFood(input, foods, aliases),
  }));

  renderParseResults(results);

  const aggregateResult = lines.length
    ? window.GIApp.aggregator.aggregateMeal(lines, foods, aliases)
    : null;
  renderPrediction(aggregateResult);
}

window.GIApp.ready = Promise.all([loadFoods(), loadAliases(), loadCoefficients()]).then(([foods]) => {
  const button = document.getElementById("predict-button");
  if (button) {
    button.disabled = false;
    button.addEventListener("click", runParser);
  }
  return foods;
});
