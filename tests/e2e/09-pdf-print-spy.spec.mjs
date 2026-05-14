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
 * 09 — PDF/print spy + PDF content integrity
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
 *
 * PDF content integrity assertions (added post-Phase-0E — RED test
 * discipline: these catch silent regressions where window.print fires
 * but the printed content is wrong or missing):
 *
 *   A. Zero Mermaid blocks (defensive): The SPA uses only Chart.js canvases,
 *      never Mermaid. If a `pre.mermaid` block ever appears in print DOM,
 *      customers would see raw diagram code instead of a rendered image.
 *      Bug class: PDF shows raw Mermaid source.
 *
 *   B. Score numeral visible in @media print: `.ag-score-big` must not be
 *      hidden (`display:none` / `visibility:hidden`) under the print
 *      stylesheet. The headline score is the primary asset of the report.
 *      Bug class: PDF has blank where the score should appear.
 *
 *   C. Chart.js canvases present and sized in print mode: The results page
 *      embeds at least one radar/bar canvas. In print, all tab panels expand
 *      (`display: block !important` in assessment.css @media print), so
 *      canvases must be present and have non-zero layout width.
 *      Bug class: PDF lacks pillar/maturity charts.
 *
 *   D. Score numeral matches persona's expectedScores.overall: Confirms that
 *      the number a customer reads in the PDF matches the engine-recorded
 *      expected score for this persona fixture (within ±1 for rounding).
 *      Bug class: PDF shows wrong score — silent scoring or rendering
 *      regression; customer cannot trust report numbers.
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

    // ── PDF content integrity assertions ──────────────────────────────────
    // Switch to print media emulation so @media print rules apply before
    // querying layout and computed styles.
    await page.emulateMedia({ media: "print" });
    await page.waitForTimeout(100); // allow CSS recalc after media change

    // ── Assertion A — zero Mermaid blocks in print DOM ────────────────────
    // The SPA uses only Chart.js canvases; no Mermaid blocks should ever
    // appear. If this fails, customers see raw mermaid source code in their
    // PDF instead of rendered diagrams.
    const mermaidCount = await page.locator("pre.mermaid").count();
    expect(
      mermaidCount,
      "If this fails, customer's printed PDF will show raw mermaid code blocks instead of diagrams.",
    ).toBe(0);

    // ── Assertion B — score numeral visible under @media print ────────────
    // `.ag-score-big` must not be hidden. It is the primary headline number
    // on the results page. The print stylesheet in assessment.css does NOT
    // add display:none for this class — if it ever does, customers receive
    // a blank where the score should appear.
    const scoreEl = page.locator(".ag-score-big").first();
    await expect(
      scoreEl,
      "If this fails, customer's printed PDF lacks the headline score number — primary asset of the PDF is missing.",
    ).toBeVisible();

    const scoreDisplay = await scoreEl.evaluate(
      (el) => getComputedStyle(el).display,
    );
    const scoreVisibility = await scoreEl.evaluate(
      (el) => getComputedStyle(el).visibility,
    );
    expect(
      scoreDisplay,
      "If this fails, customer's printed PDF lacks the headline score number — primary asset of the PDF is missing.",
    ).not.toBe("none");
    expect(
      scoreVisibility,
      "If this fails, customer's printed PDF lacks the headline score number — primary asset of the PDF is missing.",
    ).not.toBe("hidden");

    // ── Assertion C — Chart.js canvases present and sized in print mode ───
    // In @media print, assessment.css forces `.ag-tab-panel { display: block
    // !important }` so ALL result panels (scorecard radar + zones bar chart)
    // expand. At least one canvas must exist with a non-zero layout width.
    // If this fails, the PDF lacks pillar/maturity charts.
    const canvases = page.locator("canvas");
    const canvasCount = await canvases.count();
    expect(
      canvasCount,
      "If this fails, customer's printed PDF lacks pillar/maturity charts — only numbers, no visualizations.",
    ).toBeGreaterThan(0);

    for (let i = 0; i < canvasCount; i++) {
      const width = await canvases.nth(i).evaluate((c) => c.offsetWidth);
      expect(
        width,
        `canvas[${i}]: If this fails, customer's printed PDF lacks pillar/maturity charts — only numbers, no visualizations.`,
      ).toBeGreaterThan(0);
    }

    // ── Assertion D — score numeral matches persona's expectedScores.overall
    // Strip non-numeric characters (e.g. the "%" suffix the SPA appends),
    // parse to integer, and compare to persona.expectedScores.overall.
    // Allow ±1 tolerance: expectedScores may be precise; displayed value may
    // be Math.round()-ed. If this fails, the PDF shows the WRONG score —
    // a silent scoring or rendering regression that undermines customer trust.
    const scoreText = await scoreEl.textContent();
    const displayedScore = parseInt(
      (scoreText || "").replace(/[^0-9]/g, ""),
      10,
    );
    const expectedOverall = persona.expectedScores.overall;
    expect(
      Math.abs(displayedScore - expectedOverall),
      `If this fails, the score CONTENT in the PDF does not match the persona's recorded engine score (expected ~${expectedOverall}, got ${displayedScore}) — silent regression in scoring or rendering. Customer cannot trust report numbers.`,
    ).toBeLessThanOrEqual(1);
  });
});
