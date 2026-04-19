/**
 * v1.4.1 export-envelope shape tests.
 *
 * Verifies the contract documented above exportJSON() in assessment-app.js:
 *   - _metadata envelope is present with required fields
 *   - _computedScores has overall + perPillar (1..4) + perControl
 *   - assessmentStatus enum is one of {draft, in-progress, final}
 *   - Original state keys remain at top level (importer compatibility)
 *   - Round-trip: importing then re-exporting drops snapshot fields and recomputes
 *
 * The SPA is a non-module browser script that uses fetch() and the DOM, so we
 * load it under jsdom + a fetch shim that serves the local manifest files.
 */
import { describe, it, expect, beforeAll } from "vitest";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { JSDOM } from "jsdom";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");
const APP_PATH = join(repoRoot, "docs", "javascripts", "assessment-app.js");
const MANIFEST_PATH = join(repoRoot, "assessment", "manifest", "controls.json");

/** Minimal stand-in for assessment-data.json so the SPA can boot. */
function buildAssessmentDataStub(manifest) {
  // Map manifest controls into the legacy assessment-data.json shape that the
  // SPA reads (id/title/pillar/zones/regulations are required for scoring).
  const controls = manifest.map(m => ({
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

  // fetch shim: route the SPA's known URLs to local fixtures.
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

  // Capture downloads instead of writing files. The SPA flow is:
  //   blob = new Blob([...])  →  url = URL.createObjectURL(blob)  →  a.href=url; a.click()
  // We map url→blob in the createObjectURL shim and resolve in the click handler.
  const blobsByUrl = new Map();
  let urlCounter = 0;
  window.URL.createObjectURL = (blob) => {
    const u = "blob:stub#" + (++urlCounter);
    blobsByUrl.set(u, blob);
    return u;
  };
  window.URL.revokeObjectURL = () => {};
  const captured = [];
  window.HTMLAnchorElement.prototype.click = function () {
    const blob = blobsByUrl.get(this.href);
    captured.push({ name: this.download, blob });
  };
  // Wrap Blob so we can recover the text content synchronously (jsdom Blob
  // doesn't expose a sync .text() method).
  const RealBlob = window.Blob;
  function WrappedBlob(parts, opts) {
    const b = new RealBlob(parts, opts);
    b.__text = parts.join("");
    return b;
  }
  WrappedBlob.prototype = RealBlob.prototype;
  window.Blob = WrappedBlob;

  const code = readFileSync(APP_PATH, "utf8");
  window.eval(code);
  return { window, captured };
}

describe("v1.4.1 portal export envelope", () => {
  let window, captured, app;

  beforeAll(async () => {
    ({ window, captured } = bootSPA());
    // The SPA constructs an instance on DOMContentLoaded; we drive it directly.
    app = new window.AssessmentApp(window.document.getElementById("ag-app"));
    await app.loadData();
    app.state = app.newState();
    app.state.scoping.organizationName = "Acme Bank";
    app.state.scoping.assessorName = "Jane Doe";
    app.state.scoping.zones = [1, 2, 3];
    // Answer two controls so we have non-trivial scores.
    app.state.responses["1.1"] = { answer: "yes", notes: "", evidenceRef: "" };
    app.state.responses["1.2"] = { answer: "no", notes: "", evidenceRef: "" };
    app.exportJSON();
  });

  function getExport() {
    expect(captured.length, "exportJSON should have triggered a download").toBeGreaterThan(0);
    const text = captured[captured.length - 1].blob.__text;
    return JSON.parse(text);
  }

  it("includes _metadata envelope with required fields", () => {
    const out = getExport();
    expect(out._metadata).toBeDefined();
    expect(out._metadata.exportSchemaVersion).toBe(1);
    expect(out._metadata.schemaType).toBe("full");
    expect(out._metadata.frameworkVersion).toMatch(/^\d+\.\d+\.\d+$/);
    expect(out._metadata.manifestSchemaVersion).toMatch(/^1\.4\./);
    expect(out._metadata.exportedAt).toMatch(/^\d{4}-\d{2}-\d{2}T/);
    expect(typeof out._metadata.exportedBy).toBe("string");
  });

  it("includes _computedScores with overall, perPillar (1-4), perControl", () => {
    const out = getExport();
    expect(out._computedScores).toBeDefined();
    expect(out._computedScores.perPillar).toBeDefined();
    expect(Object.keys(out._computedScores.perPillar).sort()).toEqual(["1", "2", "3", "4"]);
    expect(out._computedScores.perControl["1.1"]).toBe(1);
    expect(out._computedScores.perControl["1.2"]).toBe(0);
    // overall is integer percent or null
    const o = out._computedScores.overall;
    expect(o === null || (Number.isInteger(o) && o >= 0 && o <= 100)).toBe(true);
  });

  it("emits assessmentStatus enum derived from state", () => {
    const out = getExport();
    expect(["draft", "in-progress", "final"]).toContain(out.assessmentStatus);
    // Two answered controls → in-progress
    expect(out.assessmentStatus).toBe("in-progress");
  });

  it("preserves original state keys at top level (importer back-compat)", () => {
    const out = getExport();
    expect(out.assessmentId).toBeTypeOf("string");
    expect(out.responses).toBeDefined();
    expect(out.scoping).toBeDefined();
    expect(out.scoping.organizationName).toBe("Acme Bank");
    expect(out.responses["1.1"].answer).toBe("yes");
    expect(out.completedSteps).toBeDefined();
  });

  it("round-trips: import drops snapshot fields, re-export recomputes", () => {
    const first = getExport();
    // Mutate the embedded scores to a wrong value, then reimport — the new
    // export must show the correctly-recomputed value (proves importer ignores
    // _computedScores).
    first._computedScores.overall = 999;
    first._metadata.frameworkVersion = "0.0.0-stale";
    const tampered = JSON.stringify(first);
    const ok = app.importState(tampered);
    expect(ok).toBe(true);
    app.exportJSON();
    const second = getExport();
    expect(second._computedScores.overall).not.toBe(999);
    expect(second._metadata.frameworkVersion).not.toBe("0.0.0-stale");
  });
});
