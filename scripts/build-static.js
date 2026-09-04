const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const dist = path.join(root, "dist");
const entries = [
  "assets",
  "index.html",
  "nos-entrepots",
  "conseils",
  "faq",
  "contact",
  "reservation-en-ligne",
  "en",
];

fs.rmSync(dist, { recursive: true, force: true });
fs.mkdirSync(dist, { recursive: true });

for (const entry of entries) {
  fs.cpSync(path.join(root, entry), path.join(dist, entry), {
    recursive: true,
    dereference: false,
  });
}
