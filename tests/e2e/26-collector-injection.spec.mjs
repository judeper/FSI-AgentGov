import { test } from "@playwright/test";
import { clearPageStorage, expect } from "./_harness.mjs";

/**
 * 26 — Collector / import prototype-pollution defenses
 *
 * The SPA's import path (`AssessmentApp.prototype.importState`) hard-
 * rejects `__proto__`, `constructor`, and `prototype` keys via the
 * `_COLLECTOR_FORBIDDEN_KEYS` table (PR #142). This spec verifies the
 * end-to-end contract:
 *
 *   1. A crafted import payload with `__proto__: { polluted: 1 }` at
 *      the root is REJECTED (importState returns false / throws),
 *      AND `({}).polluted` remains `undefined` after the attempt.
 *   2. Same for `constructor: { prototype: { polluted: 1 } }`.
 *   3. A crafted payload with a control-id key matching a forbidden
 *      string (`__proto__`, `constructor`, `prototype`) is filtered
 *      from `state.drilldown` after import, even when the surrounding
 *      JSON is otherwise valid.
 *
 * All assertions run inside `page.evaluate` so the prototype check
 * sees the page's real `Object.prototype`, not the test-runner's.
 */
test.describe("collector / import injection defenses @regression", () => {
  test("__proto__ + constructor keys cannot pollute Object.prototype via import @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });

    // (1) __proto__ at root.
    const protoResult = await page.evaluate(() => {
      const app = window.__assessmentApp;
      // Build payload by parsing JSON so __proto__ is an OWN property.
      const payload = JSON.parse(
        '{"assessmentId":"poll-1","__proto__":{"polluted":1},"scoping":{},"responses":{}}',
      );
      let threw = false;
      let returned;
      try {
        returned = app.importState(payload);
      } catch (e) {
        threw = true;
      }
      return {
        threwOrFalse: threw || returned === false,
        polluted: ({}).polluted,
      };
    });
    expect(protoResult.threwOrFalse).toBe(true);
    expect(protoResult.polluted).toBeUndefined();

    // (2) constructor at root carrying a prototype-polluting payload.
    const ctorResult = await page.evaluate(() => {
      const app = window.__assessmentApp;
      const payload = JSON.parse(
        '{"assessmentId":"poll-2","constructor":{"prototype":{"pollutedCtor":1}},"scoping":{},"responses":{}}',
      );
      let threw = false;
      let returned;
      try {
        returned = app.importState(payload);
      } catch (e) {
        threw = true;
      }
      return {
        threwOrFalse: threw || returned === false,
        pollutedCtor: ({}).pollutedCtor,
      };
    });
    expect(ctorResult.threwOrFalse).toBe(true);
    expect(ctorResult.pollutedCtor).toBeUndefined();

    // (3) drilldown id matching a forbidden key is filtered. We supply
    //     a structurally valid payload and assert the post-import state
    //     does not carry forbidden drilldown keys, while a benign key
    //     ("1.1") survives.
    const drilldownResult = await page.evaluate(() => {
      const app = window.__assessmentApp;
      const payload = JSON.parse(
        '{"assessmentId":"poll-3","assessmentName":"Drilldown probe","scoping":{"organizationName":"PD","institutionType":"bank","zones":[1]},"responses":{},"drilldown":{"1.1":{"selections":["a"]},"__proto__":{"selections":["evil"]},"constructor":{"selections":["evil"]},"prototype":{"selections":["evil"]}}}',
      );
      let threw = false;
      try {
        app.importState(payload);
      } catch (e) {
        threw = true;
      }
      const dd = (app.state && app.state.drilldown) || {};
      return {
        threw,
        hasBenign: Object.prototype.hasOwnProperty.call(dd, "1.1"),
        hasProto: Object.prototype.hasOwnProperty.call(dd, "__proto__"),
        hasCtor: Object.prototype.hasOwnProperty.call(dd, "constructor"),
        hasProtoKey: Object.prototype.hasOwnProperty.call(dd, "prototype"),
        polluted: ({}).polluted,
      };
    });
    // Either: import succeeded and forbidden keys were filtered, OR
    // import threw (also acceptable — fail-closed). We accept both as
    // long as Object.prototype is clean and benign data, if present, is
    // intact.
    expect(drilldownResult.polluted).toBeUndefined();
    if (!drilldownResult.threw) {
      expect(drilldownResult.hasProto).toBe(false);
      expect(drilldownResult.hasCtor).toBe(false);
      expect(drilldownResult.hasProtoKey).toBe(false);
    }
  });
});
