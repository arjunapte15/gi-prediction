// Phase 15 test: parser -> carb-weighted aggregation -> displayed GI/GL,
// wired end-to-end and driven through the live page in a real browser.
//
// Re-runs the exact multi-food test-meal cases from tests/test_phase_12.py
// (same hand-computed expected GI/GL) through the actual site, plus the
// ambiguous/not-found "needs_clarification" cases -- confirming no number
// is ever computed or displayed from partial data. Expected values below
// were cross-checked against parser/meal_aggregator.py's own output for
// the same inputs (see PROJECT scratch verification during development).
//
// Serves the repo over a real local HTTP server (mirroring GitHub Pages'
// sibling-folder layout), same pattern as tests/test_phase_13.js and
// tests/test_phase_14.js.

const { chromium } = require("playwright");
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");

const MIME = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".css": "text/css",
  ".json": "application/json",
};

function startServer() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      const urlPath = decodeURIComponent(req.url.split("?")[0]);
      const filePath = path.join(ROOT, urlPath);
      if (!filePath.startsWith(ROOT)) {
        res.writeHead(403);
        res.end();
        return;
      }
      fs.readFile(filePath, (err, data) => {
        if (err) {
          res.writeHead(404);
          res.end();
          return;
        }
        const ext = path.extname(filePath);
        res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
        res.end(data);
      });
    });
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

let failures = 0;
function assert(cond, msg) {
  if (cond) {
    console.log(`PASS: ${msg}`);
  } else {
    failures += 1;
    console.error(`FAIL: ${msg}`);
  }
}

function close(a, b, tol) {
  return Math.abs(a - b) <= tol;
}

// Mirrors tests/test_phase_12.py's test-meal cases exactly.
const RESOLVED_CASES = [
  {
    name: "single-food meal matches its own GI/GL unchanged",
    input: "Naan bread",
    expectedGI: 71.0,
    expectedGL: 25.0,
  },
  {
    name: "two-food meal carb-weighted aggregation (naan + chana masala)",
    input: "Naan bread\nChana masala",
    expectedGI: 56.83,
    expectedGL: 33.0,
  },
  {
    name: "second two-food meal carb-weighted aggregation (doughnut + watermelon)",
    input: "Doughnut\nWatermelon, raw",
    expectedGI: 68.57,
    expectedGL: 31.0,
  },
  {
    name: "three-food meal with zero-GI dish (chapati + rajmah + butter chicken)",
    input: "Chapati, flatbread\nRajmah (kidney beans), boiled\nButter chicken",
    expectedGI: 40.41,
    expectedGL: 29.0,
  },
];

const CLARIFICATION_CASES = [
  {
    name: "ambiguous food blocks the number and shows candidates",
    input: "Naan bread\ndosa",
    checkParseResults: (items) =>
      items.some((t) => t.includes("ambiguous") && t.includes("Rice dosa") && t.includes("Dosa, rice and black gram dhal")),
  },
  {
    name: "not-found food blocks the number and shows clearly",
    input: "Naan bread\nzzxxqqjjbbnnmm12345",
    checkParseResults: (items) => items.some((t) => t.includes("not found")),
  },
];

async function main() {
  const server = await startServer();
  const { port } = server.address();
  const pageUrl = `http://127.0.0.1:${port}/site/index.html`;

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(pageUrl);
  await page.waitForSelector("#predict-button:not([disabled])", { timeout: 15000 });

  for (const { name, input, expectedGI, expectedGL } of RESOLVED_CASES) {
    await page.fill("#meal-text", input);
    await page.click("#predict-button");
    await page.waitForSelector("#prediction-summary");

    const giText = await page.textContent("#prediction-gi");
    const glText = await page.textContent("#prediction-gl");
    const gi = parseFloat(giText);
    const gl = parseFloat(glText);

    assert(close(gi, expectedGI, 0.1), `${name}: GI ${gi} ≈ expected ${expectedGI}`);
    assert(close(gl, expectedGL, 0.1), `${name}: GL ${gl} ≈ expected ${expectedGL}`);

    const clarification = await page.$("#prediction-clarification");
    assert(clarification === null, `${name}: no needs-clarification message shown`);

    const breakdownItems = await page.$$eval("#prediction-breakdown li", (lis) => lis.length);
    assert(breakdownItems === input.split("\n").length, `${name}: per-food breakdown has one row per food`);
  }

  for (const { name, input, checkParseResults } of CLARIFICATION_CASES) {
    await page.fill("#meal-text", input);
    await page.click("#predict-button");
    await page.waitForSelector("#prediction-clarification");

    const summary = await page.$("#prediction-summary");
    assert(summary === null, `${name}: no GI/GL number is displayed`);

    const parseItems = await page.$$eval("#parse-results li", (lis) => lis.map((li) => li.textContent));
    assert(checkParseResults(parseItems), `${name}: matched-foods list still shows the per-line detail`);
  }

  await browser.close();
  server.close();

  if (failures > 0) {
    console.error(`\n${failures} assertion(s) failed.`);
    process.exit(1);
  } else {
    console.log("\nAll Phase 15 assertions passed.");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
