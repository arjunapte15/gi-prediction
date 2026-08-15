// Phase 13 regression test: static site loads and parses foods.json in-browser.
//
// Serves the repo over a real local HTTP server (mirroring how GitHub Pages
// would serve it), loads site/index.html into a jsdom window with a real
// fetch, manually executes app.js against that window, and checks the
// resulting in-page dataset.

const { JSDOM } = require("jsdom");
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

async function main() {
  const server = await startServer();
  const { port } = server.address();
  const pageUrl = `http://127.0.0.1:${port}/site/index.html`;

  const html = fs.readFileSync(path.join(ROOT, "site", "index.html"), "utf-8");
  const dom = new JSDOM(html, { url: pageUrl, runScripts: "outside-only" });

  // jsdom does not implement fetch; wire it to Node's fetch, resolving
  // relative URLs against the page's location the way a real browser would.
  dom.window.fetch = (url, opts) => fetch(new URL(url, dom.window.location.href).href, opts);

  const appJsSource = fs.readFileSync(path.join(ROOT, "site", "app.js"), "utf-8");
  dom.window.eval(appJsSource);

  await dom.window.GIApp.ready;
  server.close();

  const foods = dom.window.GIApp.foods;
  assert(Array.isArray(foods), "GIApp.foods is an array after load");
  assert(foods.length === 129, `foods.length is 129 (got ${foods && foods.length})`);

  const names = new Set(foods.map((f) => f.food_name));
  assert(names.has("Apple Blueberry muffin"), 'known food "Apple Blueberry muffin" present');
  assert(
    names.has("Basmati rice, white, polished, cooked 10 min"),
    'known food "Basmati rice, white, polished, cooked 10 min" present'
  );

  const statusText = dom.window.document.getElementById("data-status").textContent;
  assert(
    statusText === "Loaded 129 foods.",
    `#data-status reflects the successful load (got "${statusText}")`
  );

  dom.window.close();

  if (failures > 0) {
    console.error(`\n${failures} assertion(s) failed.`);
    process.exit(1);
  } else {
    console.log("\nAll Phase 13 assertions passed.");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
