import { test } from "@playwright/test";
import {
  clearPageStorage,
  clickThroughPhase1,
  expect,
  loadPersona,
  navClick,
  seedScoping,
} from "./_harness.mjs";

/**
 * 18 — Autofill / autopop idempotence (E2E regression)
 *
 * SCOPE NOTE — there is no SPA autofill action.
 *   Searches for "autofill", "autopop", "fillAll", "_devAutofill" in
 *   docs/javascripts/assessment-app.js return only browser-autofill
 *   *defenses* (PR #137) on the institution-type select. There is no
 *   developer or test action that bulk-fills assessment answers; PR #137
 *   shipped layered protections AGAINST silent autofill, not a
 *   convenience action. Smoke spec 02 already covers the defenses.
 *
 *   Per the prompt's degradation clause ("If autofill is purely
 *   user-initiated (no auto-on-load), the spec degrades to ..."), we
 *   reframe this spec as the IDEMPOTENCE assertion the prompt cares
 *   about: re-mounting Phase 1 (e.g. by navigating away and back) and
 *   reloading the page must NOT silently re-apply or duplicate user
 *   answers, and any one-shot side-effects must remain one-shot.
 *
 * Active assertions:
 *   1. Seed an assessment, answer 5 controls.
 *   2. Navigate to results then back to phase1 → assert answers
 *      unchanged in count, identity, and order.
 *   3. Reload the page → assert answers unchanged after rehydration.
 *
 * If a true `_devAutofill`-style action ships in a later PR, replace
 * the body below with the click-N-times-but-fill-once pattern.
 */
test.describe("autofill idempotence @regression", () => {
  test("answers unchanged across phase1↔results round-trip and reload @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);
    await clickThroughPhase1(page, persona);

    const baseline = await page.evaluate(() => {
      const app = window.__assessmentApp;
      const r = app.state.responses || {};
      // Sort keys for stable comparison.
      return Object.keys(r)
        .sort()
        .map((k) => ({ id: k, answer: r[k].answer }));
    });
    // The SPA auto-applies N/A to controls outside the selected zones,
    // so baseline length includes both persona answers + auto-NA. We
    // don't assert exact length — only that round-trip is idempotent.
    expect(baseline.length).toBeGreaterThanOrEqual(
      Object.keys(persona.answers).length,
    );

    // Round-trip: Phase 1 → Results → Phase 1.
    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();
    await page
      .getByRole("button", { name: "Back to Assessment" })
      .dispatchEvent("click");
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    const afterRoundTrip = await page.evaluate(() => {
      const app = window.__assessmentApp;
      const r = app.state.responses || {};
      return Object.keys(r)
        .sort()
        .map((k) => ({ id: k, answer: r[k].answer }));
    });
    expect(afterRoundTrip).toEqual(baseline);

    // Fresh visit — saved state should rehydrate and Phase 1 must show
    // identical answer set without any re-fire. Uses page.goto instead of
    // page.reload because AS8's URL routing would auto-resume to results
    // step (the saved state's last step) and bypass the manual resume flow.
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });
    // Resume the saved assessment.
    await page
      .getByRole("button", { name: /Resume Acme Bank/ })
      .first()
      .click();
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    const afterReload = await page.evaluate(() => {
      const app = window.__assessmentApp;
      const r = (app && app.state && app.state.responses) || {};
      return Object.keys(r)
        .sort()
        .map((k) => ({ id: k, answer: r[k].answer }));
    });
    expect(afterReload).toEqual(baseline);
  });
});
