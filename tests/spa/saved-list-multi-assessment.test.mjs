/**
 * Regression test for the "saved-list data loss" P0 bug (iter3-2-001).
 *
 * BEFORE FIX: saveToStorage wrote only to STORAGE_KEY+"-current"; loading any
 * saved assessment that was not the most recently edited one silently failed
 * because loadFromStorage(id) only consulted -current and required
 * data.assessmentId === id. A consultant managing two clients lost access to
 * the older one with no recovery path.
 *
 * AFTER FIX: per-assessment slot at STORAGE_KEY+"-data-"+id is the source of
 * truth; -current is kept as a "most recently edited" pointer for back-compat;
 * init() runs a one-time migration to copy a legacy -current blob into its
 * per-id slot.
 *
 * SPA file: docs/javascripts/assessment-app.js
 *   - saveToStorage (~L889)
 *   - loadFromStorage (~L933)
 *   - deleteSaved (~L944)
 *   - _migrateLegacySavedAssessments (~L310)
 */
import { describe, it, expect, beforeEach } from "vitest";
import { bootSPA } from "./_bootSpa.mjs";

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
    if (globalThis.localStorage && typeof globalThis.localStorage.clear === "function") {
      globalThis.localStorage.clear();
    }
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
    seedAssessment(app, "id-A", "Acme Bank");
    seedAssessment(app, "id-B", "Beta Brokers");

    const ok = app.loadFromStorage("id-A");
    expect(ok, "loadFromStorage('id-A') must succeed").toBe(true);
    expect(app.state.assessmentId).toBe("id-A");
    expect(app.state.assessmentName).toBe("Acme Bank");
  });

  it("deleteSaved removes only the targeted per-id slot", async () => {
    const { app, window } = await makeApp();
    seedAssessment(app, "id-A", "Acme Bank");
    seedAssessment(app, "id-B", "Beta Brokers");

    // deleteSaved may invoke confirm(); jsdom's default returns false (no export).
    app.deleteSaved("id-A");

    expect(window.localStorage.getItem(STORAGE_KEY + "-data-id-A")).toBeNull();
    expect(window.localStorage.getItem(STORAGE_KEY + "-data-id-B")).not.toBeNull();
    expect(app.getSavedList().map((s) => s.id)).toEqual(["id-B"]);
  });

  it("init() migrates a pre-fix `-current` blob into its per-id slot", async () => {
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
    expect(window.localStorage.getItem(STORAGE_KEY + "-data-legacy-id")).toBeNull();

    const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
    app._migrateLegacySavedAssessments();

    const migrated = window.localStorage.getItem(STORAGE_KEY + "-data-legacy-id");
    expect(migrated, "migration must populate the per-id slot").not.toBeNull();
    expect(JSON.parse(migrated).assessmentId).toBe("legacy-id");

    // Idempotent: rerunning does NOT clobber a now-newer per-id slot.
    window.localStorage.setItem(
      STORAGE_KEY + "-data-legacy-id",
      JSON.stringify(Object.assign({}, legacyState, { assessmentName: "Newer" }))
    );
    app._migrateLegacySavedAssessments();
    expect(JSON.parse(window.localStorage.getItem(STORAGE_KEY + "-data-legacy-id")).assessmentName).toBe("Newer");
  });
});
