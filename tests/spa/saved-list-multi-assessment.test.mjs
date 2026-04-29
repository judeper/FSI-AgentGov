/**
 * Regression test for the "saved-list data loss" P0 bug.
 *
 * BEFORE FIX:
 *   - saveToStorage wrote only to `STORAGE_KEY + "-current"` (single slot)
 *   - loadFromStorage(id) read only `-current` and required data.assessmentId === id
 *   - Result: a consultant managing two clients sees both in the saved list, but
 *     clicking "Resume" on the OLDER one silently no-ops because `-current` only
 *     holds the most recently edited assessment.
 *
 * AFTER FIX:
 *   - saveToStorage writes per-assessment slot `STORAGE_KEY + "-data-" + id`
 *     and keeps `-current` as a "most recently edited" pointer.
 *   - loadFromStorage(id) prefers the per-id slot, falls back to `-current`.
 *   - init() runs a one-time migration that copies legacy `-current` into the
 *     per-id slot if the slot is empty.
 *
 * SPA region: docs/javascripts/assessment-app.js : saveToStorage (~L740),
 *             loadFromStorage (~L770), deleteSaved (~L790),
 *             _migrateLegacySavedAssessments (~L218).
 * Regresses: iter3-2-001 (P0).
 */
import { describe, it, expect, beforeEach } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { JSDOM } from "jsdom";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");
const APP_PATH = join(repoRoot, "docs", "javascripts", "assessment-app.js");
const MANIFEST_PATH = join(repoRoot, "assessment", "manifest", "controls.json");

function buildAssessmentDataStub(manifest) {
  const controls = manifest.map((m) => ({
    id: m.id,
    title: m.title,
    pillar: m.pillar,
    zones: m.zonesApplicable && m.zonesApplicable.length ? m.zonesApplicable : [1, 2, 3],
    regulations: Array.isArray(m.regulatory) ? m.regulatory : [],
    automation: m.automation || "manual",
  }));
  return {
    pillars: [
      { num: 1, name: "Security" },
      { num: 2, name: "Management" },
      { num: 3, name: "Reporting" },
      { num: 4, name: "SharePoint" },
    ],
    controls,
    regulatoryMappings: {},
    roleAssignments: {},
    adoptionPhases: [],
  };
}

function bootSPA() {
  const manifest = JSON.parse(readFileSync(MANIFEST_PATH, "utf8"));
  const dataStub = buildAssessmentDataStub(manifest);
  const solutionsLockStub = { schemaVersion: "1.4.0", solutions: {} };

  const dom = new JSDOM("<!doctype html><html><body><div id='ag-app'></div></body></html>", {
    url: "http://localhost/assessment/",
    runScripts: "outside-only",
  });
  const { window } = dom;

  window.fetch = async (url) => {
    const u = String(url);
    let body;
    if (u.endsWith("assessment-data.json")) body = dataStub;
    else if (u.endsWith("controls.json")) body = manifest;
    else if (u.endsWith("solutions-lock.json")) body = solutionsLockStub;
    else if (u.endsWith("/i18n/en.json")) body = {};
    else throw new Error("unexpected fetch: " + u);
    return { ok: true, status: 200, json: async () => body };
  };

  const code = readFileSync(APP_PATH, "utf8");
  window.eval(code);
  return { window };
}

const STORAGE_KEY = "fsi-agentgov-assessment";

async function makeApp() {
  const { window } = bootSPA();
  const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
  await app.loadData();
  return { app, window };
}

function seedAssessment(app, id, name) {
  app.state = app.newState();
  app.state.assessmentId = id;
  app.state.assessmentName = name;
  app.state.scoping.organizationName = name;
  app.state.scoping.zones = [1, 2, 3];
  app.state.responses["1.1"] = { answer: "yes", notes: "", evidenceRef: "" };
  app.saveToStorage();
}

describe("saved-list multi-assessment durability (iter3-2-001 P0)", () => {
  beforeEach(() => {
    // Fresh storage for each test.
    if (globalThis.localStorage) globalThis.localStorage.clear();
  });

  it("persists each saved assessment under its own per-id slot", async () => {
    const { app, window } = await makeApp();

    seedAssessment(app, "id-A", "Acme Bank");
    seedAssessment(app, "id-B", "Beta Brokers");

    expect(window.localStorage.getItem(STORAGE_KEY + "-data-id-A")).not.toBeNull();
    expect(window.localStorage.getItem(STORAGE_KEY + "-data-id-B")).not.toBeNull();

    const list = app.getSavedList();
    expect(list.map((s) => s.id).sort()).toEqual(["id-A", "id-B"]);
  });

  it("Resume on a non-current saved assessment loads the correct data", async () => {
    const { app } = await makeApp();

    seedAssessment(app, "id-A", "Acme Bank"); // older
    seedAssessment(app, "id-B", "Beta Brokers"); // most recently edited; `-current` points here

    // Simulate user clicking "Resume" on the OLDER entry.
    const ok = app.loadFromStorage("id-A");
    expect(ok, "loadFromStorage('id-A') must succeed").toBe(true);
    expect(app.state.assessmentId).toBe("id-A");
    expect(app.state.assessmentName).toBe("Acme Bank");
  });

  it("deleteSaved removes only the targeted per-id slot", async () => {
    const { app, window } = await makeApp();

    seedAssessment(app, "id-A", "Acme Bank");
    seedAssessment(app, "id-B", "Beta Brokers");

    app.deleteSaved("id-A");

    expect(window.localStorage.getItem(STORAGE_KEY + "-data-id-A")).toBeNull();
    expect(window.localStorage.getItem(STORAGE_KEY + "-data-id-B")).not.toBeNull();
    expect(app.getSavedList().map((s) => s.id)).toEqual(["id-B"]);
  });

  it("init() migrates a pre-fix `-current` blob into its per-id slot", async () => {
    // Simulate a customer who saved an assessment with the OLD code: only
    // `-current` exists and there is no per-id slot.
    const { window } = bootSPA();
    const legacyState = {
      assessmentId: "legacy-id",
      assessmentName: "Legacy Assessment",
      schemaVersion: "1.4.0",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      scoping: { organizationName: "Legacy Org", assessorName: "L", zones: [1, 2, 3], roles: [] },
      responses: { "1.1": { answer: "yes", notes: "", evidenceRef: "" } },
      overrides: {},
      drilldown: {},
      currentStep: "phase1",
      completedSteps: [],
      assessmentStatus: "in-progress",
    };
    window.localStorage.setItem(STORAGE_KEY + "-current", JSON.stringify(legacyState));
    // No `-data-legacy-id` yet.
    expect(window.localStorage.getItem(STORAGE_KEY + "-data-legacy-id")).toBeNull();

    // Boot the SPA fresh and run init() (the migration step).
    const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
    app._migrateLegacySavedAssessments();

    const migrated = window.localStorage.getItem(STORAGE_KEY + "-data-legacy-id");
    expect(migrated, "migration must populate the per-id slot").not.toBeNull();
    expect(JSON.parse(migrated).assessmentId).toBe("legacy-id");

    // Migration is idempotent: running again does not clobber a now-newer per-id slot.
    window.localStorage.setItem(
      STORAGE_KEY + "-data-legacy-id",
      JSON.stringify(Object.assign({}, legacyState, { assessmentName: "Newer" }))
    );
    app._migrateLegacySavedAssessments();
    expect(JSON.parse(window.localStorage.getItem(STORAGE_KEY + "-data-legacy-id")).assessmentName).toBe("Newer");
  });
});
