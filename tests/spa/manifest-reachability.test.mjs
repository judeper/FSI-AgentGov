/**
 * manifest-reachability.test.mjs
 *
 * Bug class caught: control added to assessment/manifest/controls.json but the
 * SPA scorer silently emits NaN/undefined for it, producing a wrong overall
 * score with no visible error.
 *
 * Strategy: drive the SPA scorer with synthetic answers covering EVERY control
 * in the manifest, then assert _computedScores.perControl contains exactly 79
 * finite numeric keys with no NaN/null/undefined/Infinity values.
 *
 * Three scenarios exercise both score extremes and a mixed state:
 *   1. All-yes  — every control answered "yes"
 *   2. All-no   — every control answered "no"
 *   3. Half-half — even-index controls "yes", odd-index controls "partial"
 */
import { describe, it, expect, beforeAll } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { bootApp } from "./_bootSpa.mjs";

const here = dirname(fileURLToPath(import.meta.url));
const MANIFEST_PATH = join(here, "..", "..", "assessment", "manifest", "controls.json");

const manifest = JSON.parse(readFileSync(MANIFEST_PATH, "utf8"));
const manifestIds = manifest.map(c => c.id);
const manifestPillars = [...new Set(manifest.map(c => String(c.pillar)))].sort();

// ─── shared assertion helper ───────────────────────────────────────────────

/**
 * Runs all reachability assertions against an exported envelope.
 *
 * @param {object} envelope  - Parsed JSON export from app.exportJSON()
 * @param {string} scenarioLabel - Used in failure messages
 */
function assertReachability(envelope, scenarioLabel) {
  const tag = `[${scenarioLabel}]`;

  // 1. _computedScores block must exist
  expect(envelope._computedScores, `${tag} _computedScores missing`).toBeDefined();

  // 2. perControl must be a plain object (not an array)
  const pc = envelope._computedScores.perControl;
  expect(pc, `${tag} perControl missing`).toBeDefined();
  expect(Array.isArray(pc), `${tag} perControl should be object not array`).toBe(false);
  expect(typeof pc, `${tag} perControl should be object`).toBe("object");

  // 3. Key coverage: every manifest control id must appear in perControl
  const pcIds = Object.keys(pc);
  for (const id of manifestIds) {
    expect(pcIds, `${tag} perControl missing manifest control "${id}"`).toContain(id);
  }

  // 4. No extra ids that aren't in the manifest (optional guard against phantom controls)
  const manifestIdSet = new Set(manifestIds);
  for (const id of pcIds) {
    expect(manifestIdSet.has(id), `${tag} perControl has unknown id "${id}"`).toBe(true);
  }

  // 5. Every value is a finite number — explicitly reject NaN, undefined, null, Infinity
  const badEntries = [];
  for (const id of manifestIds) {
    const score = pc[id];
    if (!Number.isFinite(score)) {
      badEntries.push({ id, score });
    }
  }
  if (badEntries.length > 0) {
    // Surface all bad entries in one failure message for easy P0 diagnosis
    const details = badEntries
      .map(e => `  ${e.id}: ${JSON.stringify(e.score)}`)
      .join("\n");
    expect.fail(
      `${tag} ${badEntries.length} control(s) have non-finite scores (P0 — SPA scorer gap):\n${details}`
    );
  }

  // 6. overall is null or a finite number in [0, 100]
  const overall = envelope._computedScores.overall;
  if (overall !== null) {
    expect(
      Number.isFinite(overall),
      `${tag} overall should be finite or null, got ${overall}`
    ).toBe(true);
    expect(overall, `${tag} overall should be >= 0`).toBeGreaterThanOrEqual(0);
    expect(overall, `${tag} overall should be <= 100`).toBeLessThanOrEqual(100);
  }

  // 7. perPillar covers all pillars present in the manifest with finite scores
  const pp = envelope._computedScores.perPillar;
  expect(pp, `${tag} perPillar missing`).toBeDefined();

  if (Array.isArray(pp)) {
    // Alternative array form {pillar, score}
    for (const pillar of manifestPillars) {
      const entry = pp.find(e => String(e.pillar) === pillar);
      expect(entry, `${tag} perPillar missing pillar ${pillar}`).toBeDefined();
      expect(
        Number.isFinite(entry.score),
        `${tag} perPillar[${pillar}].score is not finite: ${entry.score}`
      ).toBe(true);
    }
  } else {
    // Object form {"1": number, "2": number, ...}
    for (const pillar of manifestPillars) {
      const score = pp[pillar];
      expect(
        Number.isFinite(score),
        `${tag} perPillar["${pillar}"] is not finite: ${score}`
      ).toBe(true);
    }
  }
}

// ─── helper: export and parse ──────────────────────────────────────────────

function doExport(app, captured) {
  app.exportJSON();
  expect(captured.length, "exportJSON must trigger a download").toBeGreaterThan(0);
  const blob = captured[captured.length - 1].blob;
  const text = blob.__text ?? blob.__parts?.join("") ?? "";
  return JSON.parse(text);
}

// ─── Test 1: All-yes ───────────────────────────────────────────────────────

describe("manifest-reachability: all controls answered 'yes'", () => {
  let envelope;

  beforeAll(async () => {
    const answerControls = manifestIds.map(id => ({ id, answer: "yes" }));
    const { app, captured } = await bootApp({ answerControls });
    app.state.scoping.zones = [1, 2, 3];
    envelope = doExport(app, captured);
  });

  it("perControl contains exactly 79 keys", () => {
    expect(Object.keys(envelope._computedScores.perControl)).toHaveLength(79);
  });

  it("all 79 controls have finite numeric scores (no NaN/null/undefined)", () => {
    assertReachability(envelope, "all-yes");
  });
});

// ─── Test 2: All-no ────────────────────────────────────────────────────────

describe("manifest-reachability: all controls answered 'no'", () => {
  let envelope;

  beforeAll(async () => {
    const answerControls = manifestIds.map(id => ({ id, answer: "no" }));
    const { app, captured } = await bootApp({ answerControls });
    app.state.scoping.zones = [1, 2, 3];
    envelope = doExport(app, captured);
  });

  it("perControl contains exactly 79 keys", () => {
    expect(Object.keys(envelope._computedScores.perControl)).toHaveLength(79);
  });

  it("all 79 controls have finite numeric scores (no NaN/null/undefined)", () => {
    assertReachability(envelope, "all-no");
  });
});

// ─── Test 3: Half-half (even-index "yes", odd-index "partial") ─────────────

describe("manifest-reachability: mixed answers (half 'yes', half 'partial')", () => {
  let envelope;

  beforeAll(async () => {
    const answerControls = manifestIds.map((id, i) => ({
      id,
      answer: i % 2 === 0 ? "yes" : "partial",
    }));
    const { app, captured } = await bootApp({ answerControls });
    app.state.scoping.zones = [1, 2, 3];
    envelope = doExport(app, captured);
  });

  it("perControl contains exactly 79 keys", () => {
    expect(Object.keys(envelope._computedScores.perControl)).toHaveLength(79);
  });

  it("all 79 controls have finite numeric scores (no NaN/null/undefined)", () => {
    assertReachability(envelope, "half-half");
  });
});
