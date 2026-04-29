/**
 * Shared bootSPA() helper for vitest contract specs.
 *
 * Mirrors the boot pattern in export-shape.test.mjs: spins up jsdom with a
 * fetch shim that serves the local manifest and a Blob/anchor shim that
 * captures download payloads in-memory. Returns { window, captured }; tests
 * then construct `new window.AssessmentApp(...)` and drive it directly.
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { JSDOM } from "jsdom";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");
const APP_PATH = join(repoRoot, "docs", "javascripts", "assessment-app.js");
const MANIFEST_PATH = join(repoRoot, "assessment", "manifest", "controls.json");

function buildAssessmentDataStub(manifest) {
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

export function bootSPA() {
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
  const RealBlob = window.Blob;
  function WrappedBlob(parts, opts) {
    const b = new RealBlob(parts, opts);
    b.__parts = parts;
    b.__text = parts.map(p => (typeof p === "string" ? p : "")).join("");
    return b;
  }
  WrappedBlob.prototype = RealBlob.prototype;
  window.Blob = WrappedBlob;

  const code = readFileSync(APP_PATH, "utf8");
  window.eval(code);
  return { window, captured, manifest };
}

/** Boot, instantiate, load data, and prep a usable state. */
export async function bootApp({ answerControls = [] } = {}) {
  const { window, captured, manifest } = bootSPA();
  const app = new window.AssessmentApp(window.document.getElementById("ag-app"));
  await app.loadData();
  app.state = app.newState();
  app.state.scoping.organizationName = "Test Org";
  app.state.scoping.assessorName = "Tester";
  app.state.scoping.zones = [1, 2, 3];
  for (const { id, answer } of answerControls) {
    app.state.responses[id] = { answer, notes: "", evidenceRef: "" };
  }
  return { window, captured, app, manifest };
}
