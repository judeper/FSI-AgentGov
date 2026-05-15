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
 *     - docs/javascripts/assessment-app.js   (legacy: xlsx.full.min.js)
 *     - docs/javascripts/assessment-loader.js (SRI_HASHES dict for chart.min.js
 *       and any future SPA-loaded entries)
 *     - overrides/main.html                  (site-wide static intercepts —
 *       e.g. the Mermaid CDN-block fix in Phase 3A AS1, where the SRI literal
 *       lives next to the `VENDORED_MERMAID` URL constant)
 *
 *   Files scanned on disk:
 *     - docs/javascripts/lib/*.js     (SPA lazy-loaded vendor libs)
 *     - docs/javascripts/vendor/*.js  (site-wide statically-loaded vendor libs
 *       referenced from overrides/main.html — mermaid, etc)
 *
 *   Per Theme 6 / B-009 / Phase 0 plan-checker M1, plus Phase 3A AS1.
 */

import { createHash } from "node:crypto";
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { resolve, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");

const APP_PATH = resolve(repoRoot, "docs/javascripts/assessment-app.js");
const LOADER_PATH = resolve(repoRoot, "docs/javascripts/assessment-loader.js");
const OVERRIDES_PATH = resolve(repoRoot, "overrides/main.html");
const LIB_DIR = resolve(repoRoot, "docs/javascripts/lib");
const VENDOR_DIR = resolve(repoRoot, "docs/javascripts/vendor");

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
 * Looks in this order:
 *   Form 1 — SRI_HASHES["lib/foo.js"] = "sha256-...." in assessment-loader.js
 *            (preferred form for SPA lazy-loaded libs).
 *   Form 2 — legacy inline `integrity: "sha256-..."` near the script reference
 *            in assessment-app.js (e.g. xlsx.full.min.js).
 *   Form 3 — `var SRI = "sha256-..."` (or any literal matching the pattern)
 *            within ~600 bytes of the file basename in overrides/main.html
 *            (e.g. the Mermaid CDN-block fix vendored under
 *            docs/javascripts/vendor/).
 *
 * Returns the bare base64 hash (without the "sha256-" prefix), or null if no
 * SRI literal could be located.
 */
function findExpectedSri(libRelPath, loaderSrc, appSrc, overridesSrc) {
  // Form 1: SRI_HASHES["lib/foo.js"] = "sha256-...."  (loader dict)
  const escapedPath = libRelPath.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const dictRe = new RegExp(
    `["']${escapedPath}["']\\s*:\\s*["']sha256-([A-Za-z0-9+/=]+)["']`,
  );
  const dictMatch = loaderSrc.match(dictRe);
  if (dictMatch) return { hash: dictMatch[1], source: "assessment-loader.js" };

  // Form 2: legacy in-app inline literal near the script reference.
  const fname = basename(libRelPath);
  const appIdx = appSrc.indexOf(fname);
  if (appIdx !== -1) {
    const slice = appSrc.slice(
      Math.max(0, appIdx - 500),
      Math.min(appSrc.length, appIdx + 1500),
    );
    const m = slice.match(/integrity\s*[:=]\s*["']sha256-([A-Za-z0-9+/=]+)["']/);
    if (m) return { hash: m[1], source: "assessment-app.js (inline)" };
  }

  // Form 3: site-wide intercept literal in overrides/main.html.
  // The basename can appear multiple times (comment references plus the
  // actual code constant). Scan a tight ±600 byte window around EACH
  // occurrence and stop at the first SRI literal found — this avoids
  // bleeding across multiple vendor intercepts that may live in the same
  // file while still tolerating doc-comments above the active code.
  if (overridesSrc) {
    for (
      let pos = overridesSrc.indexOf(fname);
      pos !== -1;
      pos = overridesSrc.indexOf(fname, pos + 1)
    ) {
      const slice = overridesSrc.slice(
        Math.max(0, pos - 600),
        Math.min(overridesSrc.length, pos + 600),
      );
      const m = slice.match(/["']sha256-([A-Za-z0-9+/=]+)["']/);
      if (m) return { hash: m[1], source: "overrides/main.html (vendor intercept)" };
    }
  }
  return null;
}

const loaderSrc = readUtf8(LOADER_PATH);
const appSrc = readUtf8(APP_PATH);
const overridesSrc = existsSync(OVERRIDES_PATH) ? readUtf8(OVERRIDES_PATH) : "";

const libs = readdirSync(LIB_DIR)
  .filter((f) => f.endsWith(".js"))
  .map((f) => `lib/${f}`);

const vendorLibs = existsSync(VENDOR_DIR)
  ? readdirSync(VENDOR_DIR)
      .filter((f) => f.endsWith(".js"))
      .map((f) => `vendor/${f}`)
  : [];

const allLibs = [...libs, ...vendorLibs];

if (allLibs.length === 0) {
  fail(`No .js files found in ${LIB_DIR} or ${VENDOR_DIR}`);
}

let failures = 0;
let checked = 0;

for (const libRelPath of allLibs) {
  const onDiskPath = resolve(repoRoot, "docs/javascripts", libRelPath);
  const expected = findExpectedSri(libRelPath, loaderSrc, appSrc, overridesSrc);
  if (!expected) {
    failures += 1;
    console.error(
      `FAIL: ${libRelPath} has no SRI literal in assessment-loader.js (SRI_HASHES dict), ` +
        `assessment-app.js (inline integrity attribute), or overrides/main.html ` +
        `(site-wide vendor intercept).`,
    );
    console.error(
      "      A vendored library MUST have a corresponding SRI hash so the loader " +
        "(or the static-intercept) can enforce integrity. Add the hash and reference " +
        "the library through one of the three SRI sources above. " +
        "See docs/javascripts/lib/VENDOR-MANIFEST.md for the rotation procedure.",
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
    `\nVENDOR-SRI: ${failures} failure(s) across ${allLibs.length} library file(s). ` +
      `Either the on-disk file drifted from the SRI literal, or the literal needs ` +
      `rotation. Investigate provenance before changing either.`,
  );
  process.exit(1);
}

console.log(
  `\nVENDOR-SRI: OK — ${checked}/${allLibs.length} vendored library/libraries verified ` +
    `(${libs.length} in lib/, ${vendorLibs.length} in vendor/).`,
);
process.exit(0);
