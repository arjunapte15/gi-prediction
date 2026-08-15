// GI Prediction site — loads the food dataset client-side and wires the
// meal-text input to the fuzzy-matching parser (site/parser.js).
// GI/GL prediction and meal aggregation are wired in later phases.

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
}

window.GIApp.ready = Promise.all([loadFoods(), loadAliases()]).then(([foods]) => {
  const button = document.getElementById("predict-button");
  if (button) {
    button.disabled = false;
    button.addEventListener("click", runParser);
  }
  return foods;
});
