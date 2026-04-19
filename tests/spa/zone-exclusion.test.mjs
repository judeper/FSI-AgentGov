import { describe, it, expect, beforeAll } from "vitest";
import { loadSpa } from "./_loadSpa.mjs";

let SPA;
let app;

function makeApp(stateOverrides = {}) {
  const a = new SPA.AssessmentApp(document.createElement("div"));
  a.state = a.newState();
  Object.assign(a.state, stateOverrides);
  a.data = { controls: [] };
  return a;
}

beforeAll(() => {
  SPA = loadSpa();
  app = makeApp();
});

describe("isControlExcluded", () => {
  it("does not exclude when no scoping zones are set", () => {
    const a = makeApp();
    a.state.scoping.zones = [];
    expect(a.isControlExcluded({ id: "x", zonesApplicable: [3] })).toBe(false);
  });

  it("excludes a Zone-3-only control when scoping is Zone 1", () => {
    const a = makeApp();
    a.state.scoping.zones = [1];
    expect(a.isControlExcluded({ id: "x", zonesApplicable: [3] })).toBe(true);
  });

  it("does not exclude a control applicable to all zones", () => {
    const a = makeApp();
    a.state.scoping.zones = [1];
    expect(a.isControlExcluded({ id: "x", zonesApplicable: [1, 2, 3] })).toBe(false);
  });

  it("does not exclude when at least one zone intersects", () => {
    const a = makeApp();
    a.state.scoping.zones = [2, 3];
    expect(a.isControlExcluded({ id: "x", zonesApplicable: [1, 3] })).toBe(false);
  });

  it("treats an explicit applicable override as not excluded", () => {
    const a = makeApp();
    a.state.scoping.zones = [1];
    a.state.overrides = { x: { applicable: true, note: "needed" } };
    expect(a.isControlExcluded({ id: "x", zonesApplicable: [3] })).toBe(false);
  });

  it("falls back to legacy ctrl.zones when zonesApplicable absent", () => {
    const a = makeApp();
    a.state.scoping.zones = [1];
    expect(a.isControlExcluded({ id: "x", zones: [3] })).toBe(true);
    expect(a.isControlExcluded({ id: "y", zones: [1, 2] })).toBe(false);
  });

  it("defaults to applicable to all zones when neither field present", () => {
    const a = makeApp();
    a.state.scoping.zones = [1];
    expect(a.isControlExcluded({ id: "x" })).toBe(false);
  });
});

describe("applyZoneExclusions", () => {
  it("auto-marks excluded controls as N/A with autoNa flag", () => {
    const a = makeApp();
    a.state.scoping.zones = [1];
    a.data.controls = [
      { id: "1.1", zonesApplicable: [1, 2, 3] },
      { id: "1.2", zonesApplicable: [3] },
      { id: "1.3", zonesApplicable: [2, 3] },
    ];
    a.applyZoneExclusions();
    expect(a.state.responses["1.1"]).toBeUndefined();
    expect(a.state.responses["1.2"]).toEqual({ answer: "na", notes: "", evidenceRef: "", autoNa: true });
    expect(a.state.responses["1.3"]).toEqual({ answer: "na", notes: "", evidenceRef: "", autoNa: true });
  });

  it("preserves existing user-set answers", () => {
    const a = makeApp();
    a.state.scoping.zones = [1];
    a.data.controls = [{ id: "1.2", zonesApplicable: [3] }];
    a.state.responses["1.2"] = { answer: "yes", notes: "have it", evidenceRef: "" };
    a.applyZoneExclusions();
    expect(a.state.responses["1.2"].answer).toBe("yes");
    expect(a.state.responses["1.2"].autoNa).toBeUndefined();
  });

  it("is idempotent", () => {
    const a = makeApp();
    a.state.scoping.zones = [1];
    a.data.controls = [{ id: "1.2", zonesApplicable: [3] }];
    a.applyZoneExclusions();
    const first = JSON.stringify(a.state.responses["1.2"]);
    a.applyZoneExclusions();
    const second = JSON.stringify(a.state.responses["1.2"]);
    expect(second).toBe(first);
  });
});
