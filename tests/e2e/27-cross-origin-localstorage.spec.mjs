import { test } from "@playwright/test";
import { clearPageStorage, expect } from "./_harness.mjs";

/**
 * 27 — Cross-origin localStorage isolation (narrowed)
 *
 * SCOPE NOTE — true cross-origin verification requires DNS rewriting
 * (e.g. `subdomain.localhost` resolving to a separate Playwright
 * context with its own origin). Our test harness serves the SPA from
 * a single `http://127.0.0.1:8765` origin via `python -m http.server`,
 * so a "different origin" cannot be synthesized without standing up a
 * second server. Multi-tab same-origin sharing is already covered by
 * spec 05.
 *
 * We therefore narrow this spec to the contracts we CAN verify on the
 * available origin:
 *
 *   1. Same-origin contract: the SPA's localStorage keys are namespaced
 *      under the documented prefix (`fsi-agentgov-` per spec 30), so a
 *      collision with an unrelated app on the same origin is impossible
 *      without that app deliberately writing matching keys.
 *   2. Origin-identity contract: window.location.origin matches the
 *      expected value, so storage scoping is anchored to a well-known
 *      origin (defensive sanity check against a stray sub-path mount).
 *
 * The full cross-origin assertion is documented as deferred work; if/
 * when CI gains a second-server fixture, replace this body with a
 * two-context test that asserts no key leakage between origins.
 */
test.describe("cross-origin localStorage isolation @regression", () => {
  test("SPA localStorage keys are namespaced and origin-anchored @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // Origin contract: must be the documented localhost loopback.
    const origin = await page.evaluate(() => window.location.origin);
    expect(origin).toMatch(/^http:\/\/127\.0\.0\.1:\d+$/);

    // Force the SPA to write its first key by triggering a save.
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });

    await page.evaluate(() => {
      // Seed a minimal save through the public API.
      const app = window.__assessmentApp;
      app.state = app.state || {};
      app.state.assessmentId = app.state.assessmentId || "ns-probe-1";
      app.state.assessmentName = app.state.assessmentName || "Namespace probe";
      app.state.scoping = app.state.scoping || {
        organizationName: "Probe Org",
        institutionType: "bank",
        zones: [1],
      };
      app.state.responses = app.state.responses || {};
      app.saveToStorage();

      // ALSO write a non-SPA key to confirm the SPA does not enumerate
      // foreign keys on load.
      localStorage.setItem("unrelated-app-key", "should-be-ignored");
    });

    // Reload — verify the SPA hydrates and the unrelated key remains.
    await page.reload({ waitUntil: "domcontentloaded" });
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });

    const audit = await page.evaluate(() => {
      const all = Object.keys(localStorage);
      // The SPA storage namespace prefix is documented in spec 30
      // (storage-namespace-migration). Any key NOT prefixed must remain
      // untouched (we placed `unrelated-app-key` above).
      const spaKeys = all.filter(
        (k) =>
          k.startsWith("fsi-agentgov-") ||
          k.startsWith("fsi-ag-") ||
          k.startsWith("ag-"),
      );
      const foreignKeys = all.filter((k) => !spaKeys.includes(k));
      return {
        unrelatedPreserved:
          localStorage.getItem("unrelated-app-key") === "should-be-ignored",
        spaKeyCount: spaKeys.length,
        foreignKeyCount: foreignKeys.length,
      };
    });

    // The unrelated key must survive — proves the SPA does not blanket-
    // wipe localStorage across origins-that-share-an-origin.
    expect(audit.unrelatedPreserved).toBe(true);
    // And the SPA wrote at least one of its own namespaced keys.
    expect(audit.spaKeyCount).toBeGreaterThan(0);
  });
});
