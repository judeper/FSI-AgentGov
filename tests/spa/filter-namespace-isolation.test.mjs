/**
 * Regression test for the "filter view-state leaks across assessments" SPA
 * bug (phase-c-spec-filter-leak).
 *
 * BEFORE FIX: ROLE_FILTER_KEY ("ag.roleFilter") and SECTOR_KEY
 *   ("ag.selectedSector") were stored as global localStorage keys. Newly
 *   created assessments inherited the previous assessment's filters via
 *   newState(), and switching between two saved assessments overwrote the
 *   single global slot.
 * AFTER FIX: filters are persisted under per-assessment keys
 *   (ROLE_FILTER_KEY+"-"+id, SECTOR_KEY+"-"+id). newState() does NOT read
 *   any global filter keys. loadFromStorage hydrates state.roleFilter /
 *   state.selectedSector from the per-id slot. deleteSaved clears them.
 *   _migrateLegacySavedAssessments runs once to move legacy globals onto
 *   the current assessment id (or discards them when none exists).
 *
 * SPA file: docs/javascripts/assessment-app.js
 *   - newState                       (~L881)
 *   - loadFromStorage                (~L988)
 *   - deleteSaved                    (~L1004)
 *   - _migrateLegacySavedAssessments (~L322)
 *   - sector listener                (~L2034)
 *   - role-filter listener           (~L2316)
 */
import { describe, it, expect, beforeEach } from "vitest";
import { bootSPA } from "./_bootSpa.mjs";

const STORAGE_KEY = "fsi-agentgov-assessment";
const ROLE_FILTER_KEY = "ag.roleFilter";
const SECTOR_KEY = "ag.selectedSector";

async function makeApp() {
  const { window } = bootSPA();
  const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
  await app.loadData();
  return { app, window };
}

function seed(app, window, id, name, roleFilter, sector) {
  app.state = app.newState();
  app.state.assessmentId = id;
  app.state.assessmentName = name;
  app.state.scoping.organizationName = name;
  app.state.scoping.zones = [1, 2, 3];
  app.state.roleFilter = roleFilter || "";
  app.state.selectedSector = sector || "";
  if (roleFilter) {
    window.localStorage.setItem(ROLE_FILTER_KEY + "-" + id, roleFilter);
  }
  if (sector) {
    window.localStorage.setItem(SECTOR_KEY + "-" + id, sector);
  }
  app.saveToStorage();
}

describe("filter view-state is namespaced per assessment (phase-c-spec-filter-leak)", () => {
  beforeEach(() => {
    if (globalThis.localStorage && typeof globalThis.localStorage.clear === "function") {
      globalThis.localStorage.clear();
    }
  });

  it("newState does NOT inherit legacy global filter keys", async () => {
    const { app, window } = await makeApp();
    window.localStorage.setItem(ROLE_FILTER_KEY, "AI Governance Lead");
    window.localStorage.setItem(SECTOR_KEY, "broker-dealer");
    const fresh = app.newState();
    expect(fresh.roleFilter).toBe("");
    expect(fresh.selectedSector).toBe("");
  });

  it("loading assessment B does not see assessment A's filters", async () => {
    const { app, window } = await makeApp();
    seed(app, window, "id-A", "Acme Bank", "AI Governance Lead", "broker-dealer");
    seed(app, window, "id-B", "Beta Brokers", "", "");

    expect(app.loadFromStorage("id-B")).toBe(true);
    expect(app.state.roleFilter || "").toBe("");
    expect(app.state.selectedSector || "").toBe("");
  });

  it("loading assessment A retains its own filters even after B was active", async () => {
    const { app, window } = await makeApp();
    seed(app, window, "id-A", "Acme Bank", "AI Governance Lead", "broker-dealer");
    seed(app, window, "id-B", "Beta Brokers", "Compliance Officer", "ria");

    // Reload A
    expect(app.loadFromStorage("id-A")).toBe(true);
    expect(app.state.roleFilter).toBe("AI Governance Lead");
    expect(app.state.selectedSector).toBe("broker-dealer");
  });

  it("deleteSaved removes per-id filter keys for the deleted assessment", async () => {
    const { app, window } = await makeApp();
    seed(app, window, "id-A", "Acme Bank", "AI Governance Lead", "broker-dealer");
    seed(app, window, "id-B", "Beta Brokers", "Compliance Officer", "ria");

    app.deleteSaved("id-A");

    expect(window.localStorage.getItem(ROLE_FILTER_KEY + "-id-A")).toBeNull();
    expect(window.localStorage.getItem(SECTOR_KEY + "-id-A")).toBeNull();
    // B's keys must remain.
    expect(window.localStorage.getItem(ROLE_FILTER_KEY + "-id-B")).toBe("Compliance Officer");
    expect(window.localStorage.getItem(SECTOR_KEY + "-id-B")).toBe("ria");
  });

  it("_migrateLegacySavedAssessments moves legacy global filters onto the current assessment", async () => {
    const { window } = bootSPA();
    const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
    await app.loadData();

    // Plant a legacy current assessment + legacy global filter keys.
    const legacyState = {
      assessmentId: "legacy-id", assessmentName: "Legacy",
      schemaVersion: "1.4.0", createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      scoping: { organizationName: "L", assessorName: "A", zones: [1, 2, 3], roles: [] },
      responses: { "1.1": { answer: "yes", notes: "", evidenceRef: "" } },
      overrides: {}, drilldown: {}, currentStep: "phase1", completedSteps: [],
      assessmentStatus: "in-progress",
    };
    window.localStorage.setItem(STORAGE_KEY + "-current", JSON.stringify(legacyState));
    window.localStorage.setItem(ROLE_FILTER_KEY, "AI Governance Lead");
    window.localStorage.setItem(SECTOR_KEY, "broker-dealer");

    app._migrateLegacySavedAssessments();

    expect(window.localStorage.getItem(ROLE_FILTER_KEY + "-legacy-id")).toBe("AI Governance Lead");
    expect(window.localStorage.getItem(SECTOR_KEY + "-legacy-id")).toBe("broker-dealer");
    // Globals removed.
    expect(window.localStorage.getItem(ROLE_FILTER_KEY)).toBeNull();
    expect(window.localStorage.getItem(SECTOR_KEY)).toBeNull();
    // Flag set.
    expect(window.localStorage.getItem(STORAGE_KEY + "-filter-migration-v1")).toBe("1");

    // Idempotent: second run is a no-op.
    window.localStorage.setItem(ROLE_FILTER_KEY + "-legacy-id", "Compliance Officer");
    app._migrateLegacySavedAssessments();
    expect(window.localStorage.getItem(ROLE_FILTER_KEY + "-legacy-id")).toBe("Compliance Officer");
  });

  it("migration with no current assessment discards legacy filters", async () => {
    const { window } = bootSPA();
    const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
    await app.loadData();

    window.localStorage.setItem(ROLE_FILTER_KEY, "AI Governance Lead");
    window.localStorage.setItem(SECTOR_KEY, "broker-dealer");

    app._migrateLegacySavedAssessments();

    expect(window.localStorage.getItem(ROLE_FILTER_KEY)).toBeNull();
    expect(window.localStorage.getItem(SECTOR_KEY)).toBeNull();
    // No per-id slot was created (no current id existed).
    const allKeys = Object.keys(window.localStorage);
    expect(allKeys.some(k => k.startsWith(ROLE_FILTER_KEY + "-"))).toBe(false);
    expect(allKeys.some(k => k.startsWith(SECTOR_KEY + "-"))).toBe(false);
  });
});
