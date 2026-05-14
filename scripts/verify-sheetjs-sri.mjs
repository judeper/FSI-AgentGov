#!/usr/bin/env node
/*
 * verify-sheetjs-sri.mjs (covers all vendored SRI-pinned libs)
 *
 * Attack model:
 *   The SPA lazy-loads vendored libraries from docs/javascripts/lib/* with
 *   Subresource Integrity (SRI) hash literals in the source. Browsers enforce
 *   SRI by refusing to execute a script whose hash does not match — but the
 *   failure is *silent* from a feature standpoint: the affected feature simply
 *   stops working (XLSX export disappears, results-page charts fail to render,
 *   diagrams stay raw, etc).
 *
 *   If any on-disk file drifts from its declared SRI (supply-chain compromise,
 *   accidental version bump that forgets to rotate the literal, malicious
 *   commit), CI must catch it before merge.
 *
 *   This script verifies every vendored library that has a recorded SRI
 *   literal, and additionally enforces that EVERY *.js file under
 *   docs/javascripts/lib/ has at least one corresponding SRI literal somewhere
 *   in the SPA loader sources — preventing "added a lib but forgot SRI" from
 *   shipping silently.
 *
 *   Sources of SRI literals checked:
 *     - docs/javascripts/assessment-app.js  (legacy: xlsx.full.min.js)
 *     - docs/javascripts/assessment-loader.js (SRI_HASHES dict for chart.min.js
 *       and any future entries — e.g. mermaid.min.js per Phase 3A)
 *
 *   Per Theme 6 / B-009 / Phase 0 plan-checker M1.
 */

import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { resolve, dirname, join, basename } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");

const APP_PATH = resolve(repoRoot, "docs/javascripts/assessment-app.js");
const LOADER_PATH = resolve(repoRoot, "docs/javascripts/assessment-loader.js");
const LIB_DIR = resolve(repoRoot, "docs/javascripts/lib");

function fail(msg) {
  console.error(`ERROR: ${msg}`);
  process.exit(1);
}

function readUtf8(path) {
  try {
    return readFileSync(path, "utf8");
  } catch (err) {
    fail(`Could not read ${path}: ${err.message}`);
  }
}

function sha256Base64(buf) {
  return createHash("sha256").update(buf).digest("base64");
}

/**
 * Resolve the expected SRI literal for a given library file.
 *
 * Looks first in the SRI_HASHES dict in assessment-loader.js (preferred form),
 * then falls back to the legacy "near reference" search in assessment-app.js
 * for libraries that still inline the integrity literal next to their script
 * tag (e.g. xlsx.full.min.js).
 *
 * Returns the bare base64 hash (without the "sha256-" prefix), or null if no
 * SRI literal could be located.
 */
function findExpectedSri(libRelPath, loaderSrc, appSrc) {
  // Form 1: SRI_HASHES["lib/foo.js"] = "sha256-...."  (loader dict)
  const dictRe = new RegExp(
    `["']${libRelPath.replace(/\./g, "\\.")}["']\\s*:\\s*["']sha256-([A-Za-z0-9+/=]+)["']`,
  );
  const dictMatch = loaderSrc.match(dictRe);
  if (dictMatch) return { hash: dictMatch[1], source: "assessment-loader.js" };

  // Form 2: legacy in-app inline literal near the script reference.
  const fname = basename(libRelPath);
  const idx = appSrc.indexOf(fname);
  if (idx !== -1) {
    const slice = appSrc.slice(
      Math.max(0, idx - 500),
      Math.min(appSrc.length, idx + 1500),
    );
    const m = slice.match(/integrity\s*[:=]\s*["']sha256-([A-Za-z0-9+/=]+)["']/);
    if (m) return { hash: m[1], source: "assessment-app.js (inline)" };
  }
  return null;
}

const loaderSrc = readUtf8(LOADER_PATH);
const appSrc = readUtf8(APP_PATH);

const libs = readdirSync(LIB_DIR)
  .filter((f) => f.endsWith(".js"))
  .map((f) => `lib/${f}`);

if (libs.length === 0) {
  fail(`No .js files found in ${LIB_DIR}`);
}

let failures = 0;
let checked = 0;

for (const libRelPath of libs) {
  const onDiskPath = resolve(repoRoot, "docs/javascripts", libRelPath);
  const expected = findExpectedSri(libRelPath, loaderSrc, appSrc);
  if (!expected) {
    failures += 1;
    console.error(
      `FAIL: ${libRelPath} has no SRI literal in assessment-loader.js (SRI_HASHES dict) ` +
        `or assessment-app.js (inline integrity attribute).`,
    );
    console.error(
      "      A vendored library MUST have a corresponding SRI hash so the loader " +
        "can enforce integrity. Add the hash and reference the library through the " +
        "loader. See docs/javascripts/lib/VENDOR-MANIFEST.md for the rotation procedure.",
    );
    continue;
  }
  const actual = sha256Base64(readFileSync(onDiskPath));
  if (actual === expected.hash) {
    console.log(
      `OK:   ${libRelPath} sha256-${actual} (literal in ${expected.source})`,
    );
    checked += 1;
    continue;
  }
  failures += 1;
  console.error(`FAIL: ${libRelPath} SRI mismatch`);
  console.error(`  Expected (${expected.source}): sha256-${expected.hash}`);
  console.error(`  Actual   (on-disk file)      : sha256-${actual}`);
}

if (failures > 0) {
  console.error(
    `\nVENDOR-SRI: ${failures} failure(s) across ${libs.length} library file(s). ` +
      `Either the on-disk file drifted from the SRI literal, or the literal needs ` +
      `rotation. Investigate provenance before changing either.`,
  );
  process.exit(1);
}

console.log(
  `\nVENDOR-SRI: OK — ${checked}/${libs.length} vendored library/libraries verified.`,
);
process.exit(0);
