// Phase 14 test: the JS-ported fuzzy matcher, wired to the live site's
// input box, agrees with Phase 11's Python matcher on the exact same
// test-case table (tests/test_phase_11.py) -- run against the real page in
// a real browser via Playwright, so a Python->JS porting bug can't hide
// behind a jsdom shortcut.
//
// Serves the repo over a real local HTTP server (mirroring GitHub Pages),
// same pattern as tests/test_phase_13.js.

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

// Mirrors tests/test_phase_11.py's test-case table exactly: exact match,
// typo, plural (ambiguous), known alias, garbage not-found, bare ambiguous
// term. Each check function receives the text content of one <li> from
// #parse-results for that input.
const CASES = [
  {
    name: "exact match",
    input: "Naan bread",
    check: (text) => text.includes("Naan bread") && !text.includes("ambiguous") && !text.includes("not found"),
  },
  {
    name: "typo match",
    input: "Doughnutt",
    check: (text) => text.includes("Doughnut") && !text.includes("ambiguous") && !text.includes("not found"),
  },
  {
    name: "plural ambiguous match",
    input: "raisin",
    check: (text) => text.includes("ambiguous") && text.includes("Raisins") && text.includes("Cranberry Raisin muffin"),
  },
  {
    name: "known alias match",
    input: "donut",
    check: (text) => text.includes("Doughnut") && !text.includes("ambiguous") && !text.includes("not found"),
  },
  {
    name: "garbage not found",
    input: "zzxxqqjjbbnnmm12345",
    check: (text) => text.includes("not found"),
  },
  {
    name: "bare ambiguous term",
    input: "dosa",
    check: (text) =>
      text.includes("ambiguous") &&
      text.includes("Dosa, rice and black gram dhal") &&
      text.includes("Rice dosa"),
  },
];

async function main() {
  const server = await startServer();
  const { port } = server.address();
  const pageUrl = `http://127.0.0.1:${port}/site/index.html`;

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(pageUrl);

  // Wait for data + aliases to load and the button to become enabled
  // (site/app.js enables #predict-button once window.GIApp.ready resolves).
  await page.waitForSelector("#predict-button:not([disabled])", { timeout: 15000 });

  for (const { name, input, check } of CASES) {
    await page.fill("#meal-text", input);
    await page.click("#predict-button");
    await page.waitForSelector("#parse-results li");

    const items = await page.$$eval("#parse-results li", (lis) => lis.map((li) => li.textContent));
    assert(items.length === 1, `${name}: exactly one result row rendered for "${input}" (got ${items.length})`);
    assert(check(items[0] || ""), `${name}: "${input}" -> ${JSON.stringify(items[0])}`);
  }

  // Multi-line input: one food per line, each matched independently.
  await page.fill("#meal-text", "Naan bread\nzzxxqqjjbbnnmm12345\ndosa");
  await page.click("#predict-button");
  await page.waitForSelector("#parse-results li");
  const multiItems = await page.$$eval("#parse-results li", (lis) => lis.map((li) => li.textContent));
  assert(multiItems.length === 3, `multi-line input: three result rows rendered (got ${multiItems.length})`);
  assert(
    multiItems[0].includes("Naan bread") && !multiItems[0].includes("not found"),
    `multi-line input: line 1 matched -> ${JSON.stringify(multiItems[0])}`
  );
  assert(
    multiItems[1].includes("not found"),
    `multi-line input: line 2 not found -> ${JSON.stringify(multiItems[1])}`
  );
  assert(
    multiItems[2].includes("ambiguous") && multiItems[2].includes("Rice dosa"),
    `multi-line input: line 3 ambiguous -> ${JSON.stringify(multiItems[2])}`
  );

  await browser.close();
  server.close();

  if (failures > 0) {
    console.error(`\n${failures} assertion(s) failed.`);
    process.exit(1);
  } else {
    console.log("\nAll Phase 14 assertions passed.");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
