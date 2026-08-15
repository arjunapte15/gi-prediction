// GI Prediction site — loads the food dataset client-side.
// Prediction, meal parsing, and model logic are wired in later phases.

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

window.GIApp.ready = loadFoods();
