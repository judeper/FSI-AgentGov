/**
 * Regression test for the "Resume always lands on phase1" SPA bug
 * (phase-c-spec-resume-step).
 *
 * BEFORE FIX: saveToStorage did not persist this.step; the Resume click
 *   handler always called goToStep("phase1"). A user on results/export
 *   was bounced back to phase1 on Resume.
 * AFTER FIX: saveToStorage writes this.step into state; loadFromStorage
 *   restores it; the Resume click handler honors self.step. Legacy saves
 *   without a step field default to "phase1" for safety.
 *
 * SPA file: docs/javascripts/assessment-app.js
 *   - saveToStorage   (~L920)
 *   - loadFromStorage (~L988)
 *   - goToStep        (~L1696)
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

function seed(app, id, name) {
  app.state = app.newState();
  app.state.assessmentId = id;
  app.state.assessmentName = name;
  app.state.scoping.organizationName = name;
  app.state.scoping.zones = [1, 2, 3];
  app.state.responses["1.1"] = { answer: "yes", notes: "", evidenceRef: "" };
  app.saveToStorage();
}

describe("resume restores saved wizard step (phase-c-spec-resume-step)", () => {
  beforeEach(() => {
    if (globalThis.localStorage && typeof globalThis.localStorage.clear === "function") {
      globalThis.localStorage.clear();
    }
  });

  it("saveToStorage persists the current step into the per-id slot", async () => {
    const { app, window } = await makeApp();
    seed(app, "id-A", "Acme Bank");
    app.step = "results";
    app.saveToStorage();

    const raw = window.localStorage.getItem(STORAGE_KEY + "-data-id-A");
    expect(raw).not.toBeNull();
    expect(JSON.parse(raw).step).toBe("results");
  });

  it("loadFromStorage restores app.step from the saved data when it is results/export", async () => {
    const { app } = await makeApp();
    seed(app, "id-A", "Acme Bank");
    app.step = "export";
    app.saveToStorage();

    // Simulate a fresh load
    app.state = null;
    app.step = "welcome";
    const ok = app.loadFromStorage("id-A");
    expect(ok).toBe(true);
    expect(app.step).toBe("export");
  });

  it("legacy saves without a `step` field default to phase1", async () => {
    const { window } = bootSPA();
    const legacy = {
      assessmentId: "legacy-id",
      assessmentName: "Legacy",
      schemaVersion: "1.4.0",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      scoping: { organizationName: "L", assessorName: "A", zones: [1, 2, 3], roles: [] },
      responses: { "1.1": { answer: "yes", notes: "", evidenceRef: "" } },
      overrides: {}, drilldown: {}, currentStep: "phase1", completedSteps: [],
      assessmentStatus: "in-progress",
    };
    window.localStorage.setItem(STORAGE_KEY + "-data-legacy-id", JSON.stringify(legacy));

    const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
    await app.loadData();
    app.step = "welcome";
    expect(app.loadFromStorage("legacy-id")).toBe(true);
    expect(app.step).toBe("phase1");
  });

  it("Resume only restores results/export; in-progress steps default to phase1", async () => {
    const { app } = await makeApp();
    seed(app, "id-A", "Acme Bank");
    // Steps that should round-trip exactly:
    for (const target of ["results", "export"]) {
      app.step = target;
      app.saveToStorage();
      app.state = null;
      app.step = "welcome";
      app.loadFromStorage("id-A");
      expect(app.step, "Resume should restore " + target).toBe(target);
    }
    // In-progress / pre-results steps always normalize to "phase1" on Resume:
    for (const target of ["scoping", "phase1", "phase2"]) {
      app.step = target;
      app.saveToStorage();
      app.state = null;
      app.step = "welcome";
      app.loadFromStorage("id-A");
      expect(app.step, target + " should normalize to phase1 on Resume").toBe("phase1");
    }
  });
});
