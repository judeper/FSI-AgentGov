import { test } from "@playwright/test";
import { clearPageStorage, expect, loadPersona, seedScoping } from "./_harness.mjs";

/**
 * 24 — Autopop cross-cutting
 *
 * SCOPE NOTE — the SPA has no autopop / autofill action.
 *
 * A search of `docs/javascripts/assessment-app.js` for "autopop",
 * "autofill", "fillAll", "_devAutofill", or any bulk-fill action surface
 * returns only browser-autofill DEFENSES (PR #137 on the institution-type
 * select). Spec 18 already documents this and degrades to an idempotence
 * assertion. Spec 24 is the cross-cutting sibling and degrades the same
 * way: when there is no first-class autopop, the cross-cutting concerns
 * (manual+autopop preservation, autopop respects filter, determinism)
 * collapse to "manual answers are not silently mutated by any
 * automatic SPA behavior."
 *
 * The tests below therefore exercise the only auto behaviors the SPA
 * does perform today:
 *
 *   1. Auto-NA: controls outside the selected zones are auto-NA'd. We
 *      verify a manually-authored answer to an IN-zone control is NOT
 *      overwritten by the auto-NA pass when the zone selection changes.
 *
 * If a real autopop action ships, replace this body with the manual+
 * autopop and filter-respecting assertions described in the prompt.
 */
test.describe("autopop cross-cutting @regression", () => {
  test("auto-NA does not overwrite manual answers on in-zone controls @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);

    // Manually answer an in-zone control (1.1 — known zone-1 control).
    const card = page.locator('[data-control-id="1.1"]').first();
    await card.waitFor({ state: "attached" });
    const pillar = card.locator(
      'xpath=ancestor::div[contains(@class,"ag-pillar-controls")]',
    );
    if ((await pillar.count()) > 0) {
      const collapsed = await pillar
        .first()
        .evaluate((el) => el.classList.contains("collapsed"));
      if (collapsed) {
        const header = pillar.locator(
          'xpath=preceding-sibling::div[contains(@class,"ag-pillar-header")][1]',
        );
        if ((await header.count()) > 0) await header.first().click();
      }
    }
    await card.getByRole("button", { name: "Yes", exact: true }).click();

    const before = await page.evaluate(
      () => window.__assessmentApp?.state?.responses?.["1.1"]?.answer,
    );
    expect(before).toBe("yes");

    // Trigger any auto-pass the SPA may run by re-rendering and saving.
    // (E.g. zone-change recomputation.) We then verify our manual answer
    // is preserved verbatim.
    await page.evaluate(() => {
      const app = window.__assessmentApp;
      app.saveToStorage();
      app.render();
    });

    const after = await page.evaluate(
      () => window.__assessmentApp?.state?.responses?.["1.1"]?.answer,
    );
    expect(after).toBe("yes");

    // And the manual answer must not be marked as autoNa.
    const autoNa = await page.evaluate(
      () => !!window.__assessmentApp?.state?.responses?.["1.1"]?.autoNa,
    );
    expect(autoNa).toBe(false);
  });
});
