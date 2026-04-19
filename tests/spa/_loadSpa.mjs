// Shared test helper: loads docs/javascripts/assessment-app.js (an IIFE script,
// not an ES/CommonJS module) inside the current jsdom realm and returns the
// conditional `module.exports` block defined at the bottom of the file.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const SPA_PATH = join(here, "..", "..", "docs", "javascripts", "assessment-app.js");

export function loadSpa() {
  const src = readFileSync(SPA_PATH, "utf8");
  const mod = { exports: {} };
  // Provide `module` to the IIFE via a Function wrapper. `window`, `document`,
  // and `localStorage` come from jsdom; we forward them explicitly so the IIFE
  // sees them even if it captured outer-scope identifiers.
  const fn = new Function("module", "exports", "window", "document", "localStorage", src);
  fn(mod, mod.exports, globalThis.window, globalThis.document, globalThis.localStorage);
  return mod.exports;
}

export const SPA_FILE = SPA_PATH;
