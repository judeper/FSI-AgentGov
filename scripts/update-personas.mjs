/**
 * scripts/update-personas.mjs
 *
 * Boots the SPA for each persona fixture, captures _computedScores from
 * exportJSON(), and writes back expectedScores into the persona JSON file.
 * Also ensures a canonical `responses` field (keyed by control id →
 * {answer, notes, evidenceRef}) is present alongside the legacy `answers`
 * field, which is retained verbatim for E2E harness backward compatibility
 * (tests/e2e/_harness.mjs reads `persona.answers`).
 *
 * Usage:
 *   node scripts/update-personas.mjs           # write mode: update all persona files
 *   node scripts/update-personas.mjs --check   # CI mode: exit 1 if any file would change
 *
 * No new npm dependencies. Imports bootApp from tests/spa/_bootSpa.mjs which
 * uses jsdom (already a devDependency).
 */

import { readFileSync, writeFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import { bootApp } from "../tests/spa/_bootSpa.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..");
const PERSONAS_DIR = join(repoRoot, "tests", "e2e", "fixtures", "personas");
const CHECK_MODE = process.argv.includes("--check");

/**
 * Normalise the legacy `answers` field (flat strings or tuple objects) into
 * the canonical `responses` shape used by the SPA's internal state and the
 * persona-parity vitest spec (persona-parity.test.mjs line 40).
 *
 * Legacy flat:  { "1.1": "yes" }
 * Legacy tuple: { "1.1": { value: "yes", notes: "..." } }   (edge-malicious)
 * Canonical:    { "1.1": { answer: "yes", notes: "", evidenceRef: "" } }
 */
function deriveResponses(answers) {
  if (!answers || typeof answers !== "object") return {};
  const responses = {};
  for (const [id, val] of Object.entries(answers)) {
    if (typeof val === "string") {
      responses[id] = { answer: val, notes: "", evidenceRef: "" };
    } else if (val && typeof val === "object") {
      responses[id] = {
        answer:      val.answer || val.value || "",
        notes:       val.notes  || "",
        evidenceRef: val.evidenceRef || "",
      };
    }
  }
  return responses;
}

/**
 * Process a single persona file:
 *   1. Load the JSON.
 *   2. Determine the canonical responses (prefer existing `responses` field,
 *      fall back to deriving from `answers`).
 *   3. Boot the SPA, apply the answers and persona scoping.
 *   4. Export JSON and extract _computedScores.
 *   5. Build the updated file: preserve all existing fields, add/update
 *      `responses` and `expectedScores`, keep `answers` for E2E compat.
 *   6. Return { filePath, fileName, newRaw, changed }.
 */
async function processPersona(filePath) {
  const raw = readFileSync(filePath, "utf8");
  const persona = JSON.parse(raw);

  // Prefer explicit `responses` if already populated; derive from `answers`
  // during the first run (or if `responses` is missing/empty).
  const responses = (persona.responses && Object.keys(persona.responses).length > 0)
    ? persona.responses
    : deriveResponses(persona.answers || {});

  // Build answerControls list for bootApp
  const answerControls = Object.entries(responses)
    .filter(([, r]) => r && r.answer)
    .map(([id, r]) => ({ id, answer: r.answer }));

  const { app, captured } = await bootApp({ answerControls });

  // Overlay persona scoping on top of bootApp's test defaults
  if (persona.scoping) {
    Object.assign(app.state.scoping, persona.scoping);
  }

  app.exportJSON();

  const envelope = JSON.parse(captured[captured.length - 1].blob.__text);
  const computed = envelope._computedScores;

  const expectedScores = {
    overall:   computed.overall,
    perPillar: computed.perPillar,
  };

  // ── Rebuild persona object with stable key order for idempotency ──────────
  const updated = {};

  if (persona.name        !== undefined) updated.name        = persona.name;
  if (persona.description !== undefined) updated.description = persona.description;
  if (persona.scoping     !== undefined) updated.scoping     = persona.scoping;

  // Legacy `answers` kept verbatim — E2E harness (tests/e2e/_harness.mjs
  // line 196) reads this field; modifying those test files is out of scope.
  if (persona.answers !== undefined) updated.answers = persona.answers;

  // Canonical `responses` — what persona-parity.test.mjs (line 40) reads.
  updated.responses = responses;

  // Scores written/updated by this generator
  updated.expectedScores = expectedScores;

  // Preserve any other fields (e.g. savedAssessments on consultant-multi)
  for (const key of Object.keys(persona)) {
    if (!(key in updated)) {
      updated[key] = persona[key];
    }
  }

  const newRaw = JSON.stringify(updated, null, 2) + "\n";
  return { filePath, fileName: filePath.split(/[\\/]/).pop(), newRaw, changed: newRaw !== raw };
}

async function main() {
  const files = readdirSync(PERSONAS_DIR)
    .filter(f => f.endsWith(".json") && f !== "manifest.json")
    .sort();

  let anyChanged = false;
  const results = [];

  for (const file of files) {
    const filePath = join(PERSONAS_DIR, file);
    const result = await processPersona(filePath);
    results.push(result);

    if (result.changed) {
      anyChanged = true;
      if (CHECK_MODE) {
        console.error(`DRIFT: ${file} would be updated`);
      } else {
        writeFileSync(filePath, result.newRaw, "utf8");
        console.log(`Updated: ${file}`);
      }
    } else {
      console.log(`OK (no change): ${file}`);
    }
  }

  if (CHECK_MODE) {
    if (anyChanged) {
      console.error("\nIdempotency check FAILED — run: node scripts/update-personas.mjs");
      process.exit(1);
    } else {
      console.log("\nIdempotency check PASSED — all persona files are current.");
    }
  } else {
    const updated = results.filter(r => r.changed).length;
    console.log(`\nDone. ${updated} file(s) updated, ${results.length - updated} unchanged.`);
  }
}

main().catch(err => {
  console.error("Fatal:", err);
  process.exit(1);
});
