#!/usr/bin/env node
/*
 * verify-sheetjs-sri.mjs
 *
 * Attack model:
 *   The SPA (docs/javascripts/assessment-app.js) lazy-loads SheetJS from the
 *   vendored file docs/javascripts/lib/xlsx.full.min.js with a Subresource
 *   Integrity (SRI) hash literal in the source. Browsers enforce SRI by
 *   refusing to execute a script whose hash does not match — but the failure
 *   is *silent* from a feature standpoint: XLSX export simply stops working.
 *
 *   If the on-disk file is replaced (supply-chain compromise, an accidental
 *   bump that forgets to rotate the SRI literal, or a malicious commit), the
 *   SPA's integrity check at runtime will reject the file and the export
 *   feature will silently fail in production. CI must catch this drift before
 *   merge.
 *
 *   This script:
 *     1. Reads the SRI literal from assessment-app.js (next to the
 *        xlsx.full.min.js reference).
 *     2. Computes sha256(base64) of the on-disk vendored file.
 *     3. Asserts they match. Exits 0 on match, 1 on any mismatch / parse error.
 *
 *   Wired into .github/workflows/sri-check.yml on PRs and pushes that touch
 *   the SPA or the vendored file. Also runnable locally via `npm run verify:sri`.
 *   Per Theme 6 / B-009 / spa-fix-sheetjs-sri-ci.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");

const SPA_PATH = resolve(repoRoot, "docs/javascripts/assessment-app.js");
const LIB_PATH = resolve(repoRoot, "docs/javascripts/lib/xlsx.full.min.js");

function fail(msg) {
  console.error(`ERROR: ${msg}`);
  process.exit(1);
}

let spaSource;
try {
  spaSource = readFileSync(SPA_PATH, "utf8");
} catch (err) {
  fail(`Could not read SPA source at ${SPA_PATH}: ${err.message}`);
}

// Locate the xlsx.full.min.js reference, then extract the nearest SRI literal.
const xlsxIdx = spaSource.indexOf("xlsx.full.min.js");
if (xlsxIdx === -1) {
  fail(
    `Could not find 'xlsx.full.min.js' reference in ${SPA_PATH}. The SPA may have moved the lazy-load logic; update this script.`,
  );
}

// Search a window around the reference (covers both `integrity: "..."` object
// literal form and `s.integrity = "..."` assignment form).
const windowStart = Math.max(0, xlsxIdx - 500);
const windowEnd = Math.min(spaSource.length, xlsxIdx + 1500);
const slice = spaSource.slice(windowStart, windowEnd);

const sriRegex = /integrity\s*[:=]\s*["']sha256-([A-Za-z0-9+/=]+)["']/;
const match = slice.match(sriRegex);
if (!match) {
  fail(
    `Could not find an SRI literal (sha256-...) near the xlsx.full.min.js reference in ${SPA_PATH}.`,
  );
}
const expected = match[1];

let libBuf;
try {
  libBuf = readFileSync(LIB_PATH);
} catch (err) {
  fail(`Could not read vendored SheetJS file at ${LIB_PATH}: ${err.message}`);
}

const actual = createHash("sha256").update(libBuf).digest("base64");

if (expected === actual) {
  console.log(`OK: SheetJS SRI matches (sha256-${actual})`);
  process.exit(0);
}

console.error("FAIL: SheetJS SRI mismatch");
console.error(`  Expected (from SPA literal): sha256-${expected}`);
console.error(`  Actual   (from on-disk file): sha256-${actual}`);
console.error(`  SPA file: ${SPA_PATH}`);
console.error(`  Lib file: ${LIB_PATH}`);
console.error(
  "  Either the vendored file drifted from the SRI literal, or the literal needs rotation. Investigate provenance before changing either.",
);
process.exit(1);
