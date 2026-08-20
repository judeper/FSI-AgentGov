/**
 * Prototype-pollution validator contract tests.
 *
 * Desired behavior (spa-fix-prototype-pollution): importState must REJECT any
 * payload containing __proto__, constructor, or prototype keys at any depth.
 *
 * Today's SPA defends *partially* — it only copies known keys into a fresh
 * `clean` object — but it doesn't outright reject the import. The strict
 * "rejects" assertions are therefore skipped (XFAIL) until the explicit deep-
 * scan validator lands. The Object.prototype-not-polluted sanity checks ARE
 * exercised today; that's the security-critical invariant we don't ever want
 * to regress.
 */
import { describe, it, expect } from "vitest";
import { bootApp } from "./_bootSpa.mjs";
import { loadSpa } from "./_loadSpa.mjs";

function baseValidPayload() {
  return {
    assessmentId: "test-1",
    assessmentName: "test",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    scoping: {
      organizationName: "X", assessorName: "Y", assessorRole: "",
      institutionType: "", zones: [1, 2, 3], adoptionPhase: 0,
      regulations: [], scope: "full",
    },
    responses: {},
    drilldown: {},
    completedSteps: [],
  };
}

describe("import payload prototype-pollution validator", () => {
  it("rejects forbidden collector keys without mutating object prototypes", () => {
    const SPA = loadSpa();
    const payload = { controlId: "1.1" };
    Object.defineProperty(payload, "__proto__", {
      value: { polluted: true }, enumerable: true,
    });

    expect(SPA.validateCollectorPayload(payload)).toBe(false);
    expect(({}).polluted).toBeUndefined();
  });

  it("Object.prototype is NOT polluted after importing a __proto__ payload (sanity)", async () => {
    const { app, window } = await bootApp();
    window.alert = () => {};
    const payload = baseValidPayload();
    Object.defineProperty(payload, "__proto__", {
      value: { polluted: true }, enumerable: true, configurable: true, writable: true,
    });
    try { app.importState(JSON.stringify(payload)); } catch { /* tolerated */ }
    expect(({}).polluted).toBeUndefined();
    expect(Object.prototype.polluted).toBeUndefined();
  });

  it("nested __proto__ payload also leaves Object.prototype untouched (sanity)", async () => {
    const { app, window } = await bootApp();
    window.alert = () => {};
    const payload = baseValidPayload();
    Object.defineProperty(payload.scoping, "__proto__", {
      value: { polluted: true }, enumerable: true, configurable: true, writable: true,
    });
    try { app.importState(JSON.stringify(payload)); } catch { /* tolerated */ }
    expect(({}).polluted).toBeUndefined();
    expect(Object.prototype.polluted).toBeUndefined();
  });

  // [XFAIL: spa-fix-prototype-pollution] outright rejection of payloads with
  // __proto__/constructor/prototype keys at any depth is the desired contract.
  // Activate these once an explicit deep-scan validator is added to importState.
  it("rejects payload with own __proto__ key at root", async () => {
    const { app, window } = await bootApp();
    window.alert = () => {};
    const json = '{"__proto__":{"polluted":true},"assessmentId":"x","scoping":{},"responses":{},"completedSteps":[]}';
    expect(app.importState(json)).toBe(false);
  });

  it("rejects payload with nested __proto__ key", async () => {
    const { app, window } = await bootApp();
    window.alert = () => {};
    const json = '{"assessmentId":"x","scoping":{"__proto__":{"polluted":true}},"responses":{},"completedSteps":[]}';
    expect(app.importState(json)).toBe(false);
  });

  it("rejects payload with constructor/prototype keys", async () => {
    const { app, window } = await bootApp();
    window.alert = () => {};
    const json = '{"assessmentId":"x","scoping":{},"responses":{"1.1":{"constructor":{"prototype":{"x":1}},"answer":"yes"}},"completedSteps":[]}';
    expect(app.importState(json)).toBe(false);
  });
});
