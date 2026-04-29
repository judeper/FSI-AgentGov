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
 * 09 — PDF/print spy
 *
 * The SPA's PDF export is implemented as `window.print()` (see
 * `assessment-app.js` ~L3636). This spec:
 *   1. Spies on window.print before navigation, counts calls.
 *   2. Walks scope → answer → results → export.
 *   3. Clicks the "Print to PDF" export card.
 *   4. Asserts window.print was invoked exactly once.
 *   5. Asserts that PR #142's print-only stylesheet (`@media print`
 *      rules injected by `_injectPrintStyles`) is present in
 *      `document.styleSheets` — proves the print hygiene CSS was applied.
 */
test.describe("pdf print spy @smoke", () => {
  test("window.print + @media print stylesheet @smoke", async ({ page }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    // Install the print spy BEFORE the SPA loads so it is in place when
    // the export card click handler runs.
    await page.addInitScript(() => {
      window.__printCalls = 0;
      const orig = window.print ? window.print.bind(window) : null;
      window.print = function () {
        window.__printCalls++;
        // Don't actually trigger Chromium's print preview in headless;
        // calling the original is unnecessary for the assertion.
        return undefined;
      };
      window.__origPrint = orig;
    });

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);
    await clickThroughPhase1(page, persona);
    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();

    // Navigate Results → Export
    await navClick(page, "Export Results");
    await page
      .getByRole("heading", { name: "Export Results" })
      .waitFor();

    // Trigger the PDF export card. The handler does goToStep("results")
    // then setTimeout(window.print, 300), so we wait > 300ms.
    await navClick(page, /Export as Print to PDF/);

    await expect
      .poll(async () => await page.evaluate(() => window.__printCalls), {
        timeout: 5_000,
        message: "Expected window.print to be invoked exactly once",
      })
      .toBe(1);

    // Verify PR #142's print stylesheet is present. The injected <style>
    // tag has id="ag-print-styles" and contains "@media print {".
    const hasPrintMedia = await page.evaluate(() => {
      const sheets = Array.from(document.styleSheets);
      for (const sheet of sheets) {
        try {
          const rules = sheet.cssRules || [];
          for (const r of rules) {
            if (
              r.type === CSSRule.MEDIA_RULE &&
              /print/i.test(r.media?.mediaText || "")
            ) {
              return true;
            }
          }
        } catch (_) {
          /* cross-origin sheet — skip */
        }
      }
      return false;
    });
    expect(hasPrintMedia).toBe(true);

    const styleTag = page.locator("#ag-print-styles");
    await expect(styleTag).toHaveCount(1);
    const styleText = await styleTag.evaluate((el) => el.textContent || "");
    expect(styleText).toMatch(/@media\s+print\s*\{/);
  });
});
