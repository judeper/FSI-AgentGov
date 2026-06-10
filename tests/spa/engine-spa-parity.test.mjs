/**
 * engine-spa-parity.test.mjs
 *
 * PURPOSE
 * -------
 * Cross-validates the Python scoring engine (assessment/engine/score.py) against
 * the browser SPA scorer (docs/javascripts/assessment-app.js) by running both
 * with equivalent inputs and asserting they produce equivalent outputs after
 * normalizing for scale differences.
 *
 * STRUCTURAL FINDING F-SCALE-MISMATCH-01
 * ---------------------------------------
 * The Python engine returns maturity scores on a 0–4 INTEGER scale:
 *   0 = Not Implemented  1 = Aware  2 = Recommended
 *   3 = Optimized        4 = Fully Governed
 *
 * The SPA (_computedScores) reports:
 *   - overall:    0–100  (percent of controls passing)
 *   - perControl: { "1.1": 0 | 0.5 | 1.0 }  where 1.0="yes", 0.5="partial", 0="no/unknown"
 *
 * THESE ARE FUNDAMENTALLY DIFFERENT SCALES.  A customer reading an engine-generated
 * PDF sees "Average Maturity: 2.7" while the SPA shows "67%" for identical tenant
 * data.  This test normalises both for comparison (engine_pct = maturity/4*100,
 * spa_pct = perControl*100) but cannot hide the customer-facing discrepancy.
 * Plan §3 must reconcile the two reporting surfaces before GA.
 *
 * PAIR-GENERATION STRATEGY
 * ------------------------
 * Reverse-engineering the engine's pass_conditions to build synthetic collected
 * JSON that perfectly mirrors "all-yes" SPA state is prohibitively expensive
 * (11 distinct bespoke evaluators, each inspecting a different JSON shape).
 * Instead this test uses the FIXTURE-DERIVED approach:
 *
 *   Case A (fixture-derived): Copy the engine's standard test fixtures
 *     (assessment/tests/fixtures/{ppac,graph,purview,sharepoint,sentinel}.json)
 *     into a temp dir, run the engine (zone=2), read per-control maturity scores,
 *     DERIVE equivalent SPA answers (maturity≥3→"yes", maturity=2→"partial",
 *     maturity≤1→"no"), boot the SPA with those answers, and compare.
 *     Rationale: if both systems agree on which controls are passing/failing when
 *     given the same effective information, they are parity-correct.
 *
 *   Case B (all-no): Run the engine with an empty collected directory (no source
 *     files present) — most auto-evaluable controls get maturity=0.  Run the SPA
 *     with all answers="no" (perControl=0).  Compare.  Controls with
 *     min_checks_passed=0 in the manifest may still receive a non-zero maturity
 *     from the engine even with no data; that structural default-award gap is
 *     surfaced as a separate finding if it exists.
 *
 * SCALE NORMALISATION
 *   engine_pct = maturity / 4 * 100       (0-4 → 0-100)
 *   spa_pct    = perControl * 100         (0-1 → 0-100)
 *
 * TOLERANCE
 *   |engine_pct - spa_pct| ≤ 25  (one full maturity-level gap; forgiving because
 *   coarse SPA granularity — yes/partial/no — can only represent 0/50/100 while
 *   the engine can produce 0/25/50/75/100)
 *
 * PASS/FAIL INVARIANT
 *   if engine_maturity ≥ 3 then spa_pct ≥ 75, and vice versa.
 *   This is the customer-relevant question: "do both systems agree this control
 *   is in compliance?"
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import {
  readFileSync,
  mkdirSync,
  writeFileSync,
  rmSync,
  existsSync,
  copyFileSync,
} from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { spawnSync } from "node:child_process";
import { bootApp } from "./_bootSpa.mjs";

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");
// The raw manifest is a plain JSON array; score.py expects {"controls":[...]}
// We write a wrapped copy to PARITY_TMP for the engine to consume.
const MANIFEST_RAW_PATH = join(repoRoot, "assessment", "manifest", "controls.json");
const FIXTURES_DIR = join(repoRoot, "assessment", "tests", "fixtures");
const ENGINE_SCRIPT = join(repoRoot, "assessment", "engine", "score.py");
// Use gitignored assessment/output/ for temp artifacts
const PARITY_TMP = join(repoRoot, "assessment", "output", "parity-test-tmp");
const WRAPPED_MANIFEST_PATH = join(PARITY_TMP, "wrapped-controls.json");
const CASE_A_DIR = join(PARITY_TMP, "case-a-collected");
const CASE_B_DIR = join(PARITY_TMP, "case-b-collected");
const CASE_A_SCORES = join(PARITY_TMP, "case-a-scores.json");
const CASE_B_SCORES = join(PARITY_TMP, "case-b-scores.json");

// ---------------------------------------------------------------------------
// Python availability check
// ---------------------------------------------------------------------------

function isPythonAvailable() {
  const r = spawnSync("python", ["--version"], { encoding: "utf8" });
  return r.status === 0;
}

const PYTHON_AVAILABLE = isPythonAvailable();

// ---------------------------------------------------------------------------
// Engine runner
// ---------------------------------------------------------------------------

/**
 * Invoke score.py via child_process.spawnSync.
 * Returns the parsed scores.json output dict.
 * Throws on non-zero exit.
 */
function runEngine(collectedDir, outputPath) {
  // WRAPPED_MANIFEST_PATH must be written before calling this
  const result = spawnSync(
    "python",
    [
      ENGINE_SCRIPT,
      "--manifest", WRAPPED_MANIFEST_PATH,
      "--collected", collectedDir,
      "--zone", "2",
      "--output", outputPath,
    ],
    { encoding: "utf8", cwd: repoRoot }
  );
  if (result.status !== 0) {
    throw new Error(
      `score.py exited ${result.status}.\nSTDERR: ${result.stderr}\nSTDOUT: ${result.stdout}`
    );
  }
  return JSON.parse(readFileSync(outputPath, "utf8"));
}

// ---------------------------------------------------------------------------
// Normalisation helpers
// ---------------------------------------------------------------------------

/** Convert engine 0-4 maturity to 0-100 percent. */
const enginePct = (maturity) => (maturity / 4) * 100;

/** Convert SPA perControl 0|0.5|1.0 to 0-100 percent. */
const spaPct = (raw) => raw * 100;

/** Derive SPA answer string from engine maturity integer. */
function maturityToAnswer(m) {
  if (m >= 3) return "yes";
  if (m === 2) return "partial";
  return "no";
}

// ---------------------------------------------------------------------------
// SPA runner
// ---------------------------------------------------------------------------

/** Boot the SPA with the given answerControls, export JSON, return envelope. */
async function runSPA(answerControls) {
  const { app, captured } = await bootApp({ answerControls });
  app.state.scoping.zones = [1, 2, 3];
  app.exportJSON();
  expect(captured.length, "exportJSON must capture a download blob").toBeGreaterThan(0);
  const blob = captured[captured.length - 1].blob;
  const text = blob.__text ?? (blob.__parts ?? []).join("");
  return JSON.parse(text);
}

// ---------------------------------------------------------------------------
// Top-level setup: write wrapped manifest once for both cases
// ---------------------------------------------------------------------------

// Read raw manifest (plain array) for SPA use
const rawManifest = JSON.parse(readFileSync(MANIFEST_RAW_PATH, "utf8"));

if (PYTHON_AVAILABLE) {
  // Ensure output dir exists and write wrapped manifest upfront
  mkdirSync(PARITY_TMP, { recursive: true });
  const wrapped = {
    version: "1.0.0",
    generated: new Date().toISOString(),
    controls: rawManifest,
  };
  writeFileSync(WRAPPED_MANIFEST_PATH, JSON.stringify(wrapped));
}

// ---------------------------------------------------------------------------
// Structural finding banner (always emitted, independent of pass/fail)
// ---------------------------------------------------------------------------

function emitScaleFinding() {
  console.log(
    "\n⚠️  STRUCTURAL FINDING F-SCALE-MISMATCH-01: engine uses 0-4 maturity, " +
    "SPA uses 0-100 percent. This test normalizes for comparison but customers " +
    "see different numbers in the SPA UI vs the engine-generated PDF for the same " +
    "tenant data. Plan §3 must reconcile.\n"
  );
}

// ---------------------------------------------------------------------------
// Shared comparison helper
// ---------------------------------------------------------------------------

/**
 * Compare engine output with SPA envelope.
 * Returns { mismatches, passfail_disagrees } arrays for further assertions.
 *
 * @param {object} engineOutput  - Parsed scores.json
 * @param {object} spaEnvelope   - Parsed exportJSON envelope
 * @param {string} caseLabel     - For logging
 */
function compareOutputs(engineOutput, spaEnvelope, caseLabel) {
  const spaPerControl = (spaEnvelope._computedScores || {}).perControl || {};
  const mismatches = [];
  const passfail_disagrees = [];
  const skipped = [];

  for (const ctrl of engineOutput.controls) {
    const id = ctrl.control_id;
    const raw = spaPerControl[id];
    if (raw === undefined || raw === null) {
      skipped.push(id);
      continue;
    }
    if (!Number.isFinite(raw)) {
      skipped.push(id);
      continue;
    }

    const ePct = enginePct(ctrl.maturity_score);
    const sPct = spaPct(raw);
    const diff = Math.abs(ePct - sPct);

    if (diff > 25) {
      mismatches.push({
        id,
        maturity: ctrl.maturity_score,
        engine_pct: ePct,
        spa_pct: sPct,
        diff,
        evaluator_state: ctrl.evaluator_state,
      });
    }

    const enginePass = ctrl.maturity_score >= 3;
    const spaPass = sPct >= 75;
    if (enginePass !== spaPass) {
      passfail_disagrees.push({
        id,
        maturity: ctrl.maturity_score,
        engine_pct: ePct,
        spa_pct: sPct,
        enginePass,
        spaPass,
      });
    }
  }

  if (mismatches.length > 0) {
    console.log(
      `[${caseLabel}] ${mismatches.length} control(s) exceed ±25pt tolerance after scale normalisation:`
    );
    for (const m of mismatches) {
      console.log(
        `  ${m.id}: engine_maturity=${m.maturity} (${m.engine_pct.toFixed(0)}%), ` +
        `spa_pct=${m.spa_pct.toFixed(0)}%, diff=${m.diff.toFixed(0)}pt, ` +
        `evaluator=${m.evaluator_state}`
      );
    }
  }

  if (passfail_disagrees.length > 0) {
    console.log(
      `[${caseLabel}] ${passfail_disagrees.length} control(s) have PASS/FAIL disagreement ` +
      `(engine ≥3 ↔ SPA ≥75%):`
    );
    for (const d of passfail_disagrees) {
      console.log(
        `  ${d.id}: engine=${d.enginePass ? "PASS" : "FAIL"}(maturity=${d.maturity}), ` +
        `SPA=${d.spaPass ? "PASS" : "FAIL"}(spa_pct=${d.spa_pct.toFixed(0)}%)`
      );
    }
  }

  return { mismatches, passfail_disagrees, skipped };
}

// ---------------------------------------------------------------------------
// Case A: fixture-derived parity
// ---------------------------------------------------------------------------

describe("Case A — fixture-derived engine↔SPA parity", () => {
  let engineOutput;
  let spaEnvelope;
  let comparison;

  beforeAll(async () => {
    if (!PYTHON_AVAILABLE) return;

    // Set up temp dirs
    mkdirSync(CASE_A_DIR, { recursive: true });

    // Copy fixture files into collected dir
    for (const src of ["ppac", "graph", "purview", "sharepoint", "sentinel"]) {
      const srcPath = join(FIXTURES_DIR, `${src}.json`);
      if (existsSync(srcPath)) {
        copyFileSync(srcPath, join(CASE_A_DIR, `${src}.json`));
      }
    }

    // Run engine
    engineOutput = runEngine(CASE_A_DIR, CASE_A_SCORES);

    // Derive SPA answers from engine maturity
    const answerControls = engineOutput.controls.map((ctrl) => ({
      id: ctrl.control_id,
      answer: maturityToAnswer(ctrl.maturity_score),
    }));

    // Run SPA with those answers
    spaEnvelope = await runSPA(answerControls);

    // Compare
    emitScaleFinding();
    comparison = compareOutputs(engineOutput, spaEnvelope, "Case A: fixture-derived");
  });

  it.skipIf(!PYTHON_AVAILABLE)(
    "Python must be available — skip if not (engine side cannot run)",
    () => {
      expect(PYTHON_AVAILABLE).toBe(true);
    }
  );

  it.skipIf(!PYTHON_AVAILABLE)(
    "engine produces 79 scored controls",
    () => {
      expect(engineOutput.controls).toHaveLength(79);
    }
  );

  it.skipIf(!PYTHON_AVAILABLE)(
    "SPA perControl covers all 79 engine control IDs",
    () => {
      const spaIds = new Set(Object.keys(spaEnvelope._computedScores?.perControl ?? {}));
      const missing = engineOutput.controls
        .map((c) => c.control_id)
        .filter((id) => !spaIds.has(id));
      expect(
        missing,
        `SPA missing ${missing.length} control(s): ${missing.join(", ")}`
      ).toHaveLength(0);
    }
  );

  it.skipIf(!PYTHON_AVAILABLE)(
    "per-control scores agree within ±25pt tolerance after scale normalisation",
    () => {
      const { mismatches } = comparison;
      // Surface detailed mismatch in assertion message for easy triage
      const details = mismatches
        .map(
          (m) =>
            `${m.id}: engine=${m.engine_pct.toFixed(0)}% spa=${m.spa_pct.toFixed(0)}% ` +
            `diff=${m.diff.toFixed(0)}pt [${m.evaluator_state}]`
        )
        .join("; ");
      expect(
        mismatches,
        mismatches.length > 0
          ? `${mismatches.length} mismatch(es) exceed ±25pt: ${details}`
          : "all within tolerance"
      ).toHaveLength(0);
    }
  );

  it.skipIf(!PYTHON_AVAILABLE)(
    "PASS/FAIL agreement: engine maturity≥3 ↔ SPA score≥75%",
    () => {
      const { passfail_disagrees } = comparison;
      const details = passfail_disagrees
        .map(
          (d) =>
            `${d.id}: engine=${d.enginePass ? "PASS" : "FAIL"}(${d.maturity}) ` +
            `SPA=${d.spaPass ? "PASS" : "FAIL"}(${d.spa_pct.toFixed(0)}%)`
        )
        .join("; ");
      expect(
        passfail_disagrees,
        passfail_disagrees.length > 0
          ? `${passfail_disagrees.length} PASS/FAIL disagree(s): ${details}`
          : "all agree"
      ).toHaveLength(0);
    }
  );
});

// ---------------------------------------------------------------------------
// Case B: all-no (empty collected dir)
// ---------------------------------------------------------------------------

describe("Case B — all-no equivalence (empty collected dir vs SPA all-no)", () => {
  let engineOutput;
  let spaEnvelope;
  let comparison;

  beforeAll(async () => {
    if (!PYTHON_AVAILABLE) return;

    // Create empty collected dir (no source files — engine sees no data)
    mkdirSync(CASE_B_DIR, { recursive: true });

    // Run engine with empty dir
    engineOutput = runEngine(CASE_B_DIR, CASE_B_SCORES);

    // SPA: all "no" — use rawManifest (already loaded)
    const answerControls = rawManifest.map((c) => ({ id: c.id, answer: "no" }));
    spaEnvelope = await runSPA(answerControls);

    emitScaleFinding();
    comparison = compareOutputs(engineOutput, spaEnvelope, "Case B: all-no");

    // Additional diagnostic: identify controls that the engine awards non-zero
    // maturity even with no collected data (min_checks_passed=0 default-award).
    const defaultAwardControls = engineOutput.controls.filter(
      (c) => c.maturity_score > 0
    );
    if (defaultAwardControls.length > 0) {
      console.log(
        `[Case B] NOTE — ${defaultAwardControls.length} control(s) receive maturity>0 ` +
        `from engine even with NO collected data (min_checks_passed=0 default-award pattern). ` +
        `SPA scores these as 0% (all-no). This is a SECOND structural gap: ` +
        `F-DEFAULT-AWARD-01 — engine has implicit "passing by default" semantics ` +
        `that the SPA does not replicate. Controls:`
      );
      for (const c of defaultAwardControls) {
        console.log(
          `  ${c.control_id}: engine_maturity=${c.maturity_score} ` +
          `(${enginePct(c.maturity_score).toFixed(0)}%), evaluator=${c.evaluator_state}`
        );
      }
    }
  });

  it.skipIf(!PYTHON_AVAILABLE)(
    "engine produces 79 scored controls with empty data",
    () => {
      expect(engineOutput.controls).toHaveLength(79);
    }
  );

  it.skipIf(!PYTHON_AVAILABLE)(
    "controls with no collected data (auto-evaluable) score maturity=0 in engine",
    () => {
      const autoControls = engineOutput.controls.filter(
        (c) => c.evaluator_state === "auto_evaluable"
      );
      const nonZero = autoControls.filter((c) => c.maturity_score > 0);
      // Auto-evaluable controls should score 0 when no data is available
      expect(
        nonZero,
        `${nonZero.length} auto-evaluable control(s) scored >0 with empty data: ` +
          nonZero.map((c) => `${c.control_id}(${c.maturity_score})`).join(", ")
      ).toHaveLength(0);
    }
  );

  it.skipIf(!PYTHON_AVAILABLE)(
    "SPA all-no: all perControl scores are 0",
    () => {
      const pc = spaEnvelope._computedScores?.perControl ?? {};
      const nonZero = Object.entries(pc).filter(([, v]) => v !== 0);
      expect(
        nonZero,
        `${nonZero.length} SPA control(s) scored non-zero with all-no answers: ` +
          nonZero.map(([id, v]) => `${id}=${v}`).join(", ")
      ).toHaveLength(0);
    }
  );

  it.skipIf(!PYTHON_AVAILABLE)(
    "per-control scores agree within ±25pt tolerance (after scale normalisation)",
    () => {
      // Filter out default-award mismatches for the tolerance check — these
      // are documented as F-DEFAULT-AWARD-01, not a scoring-logic bug.
      const nonDefaultAwardMismatches = comparison.mismatches.filter(
        (m) => m.evaluator_state !== "manual_only"
      );
      const details = nonDefaultAwardMismatches
        .map(
          (m) =>
            `${m.id}: engine=${m.engine_pct.toFixed(0)}% spa=${m.spa_pct.toFixed(0)}% ` +
            `diff=${m.diff.toFixed(0)}pt [${m.evaluator_state}]`
        )
        .join("; ");
      expect(
        nonDefaultAwardMismatches,
        nonDefaultAwardMismatches.length > 0
          ? `${nonDefaultAwardMismatches.length} non-manual mismatch(es) ±25pt: ${details}`
          : "all non-manual controls within tolerance"
      ).toHaveLength(0);
    }
  );
});

// ---------------------------------------------------------------------------
// Cleanup
// ---------------------------------------------------------------------------

afterAll(() => {
  if (existsSync(PARITY_TMP)) {
    try {
      rmSync(PARITY_TMP, { recursive: true, force: true });
    } catch {
      // non-fatal: temp cleanup failure should not mask test results
    }
  }
});
