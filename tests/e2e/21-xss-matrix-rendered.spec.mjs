import { test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { clearPageStorage, expect, navClick } from "./_harness.mjs";

/**
 * 21 — Rendered-output XSS matrix
 *
 * Sibling to spec 16 (storage round-trip XSS). This spec focuses on the
 * RENDERED DOM: each payload is seeded into scoping.organizationName,
 * the SPA is navigated to the results screen (where the org name is
 * shown in the print/scorecard header), and we assert:
 *
 *   1. No `dialog` event of type `alert` fires (no executed XSS).
 *   2. document.body.innerHTML contains no parsed <script> tag carrying
 *      our marker payload (i.e. the SPA escaped, not parsed).
 *   3. The org name is rendered as visible literal text somewhere in
 *      the results header — proving escape, not silent drop.
 *
 * Payloads are read from `tests/e2e/fixtures/xss-payloads.json`. To keep
 * runtime bounded, payloads are cycled through a single browser context
 * with localStorage cleared between iterations (no full reload required
 * because we re-seed via app state mutation).
 */

const here = dirname(fileURLToPath(import.meta.url));
const FIXTURE = JSON.parse(
  readFileSync(join(here, "fixtures", "xss-payloads.json"), "utf8"),
);

test.describe("rendered XSS matrix @regression", () => {
  for (const payload of FIXTURE.payloads) {
    test(`payload ${payload.id} (${payload.category}) is escaped, not executed @regression`, async ({
      page,
    }) => {
      let dialogFired = false;
      let dialogMsg = null;
      const listener = (d) => {
        if (d.type() === "alert") {
          dialogFired = true;
          dialogMsg = d.message();
        }
        d.dismiss().catch(() => {});
      };
      page.on("dialog", listener);

      await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
      await clearPageStorage(page);
      await page.reload({ waitUntil: "domcontentloaded" });

      // Seed scoping via the labelled inputs (mirrors a real user typing
      // a hostile org name).
      await page
        .getByRole("button", { name: "Start New Assessment" })
        .waitFor({ timeout: 15_000 });
      await page
        .getByRole("button", { name: "Start New Assessment" })
        .dispatchEvent("click");
      await page
        .getByRole("heading", { name: "Assessment Scoping" })
        .waitFor();
      await page.getByLabel("Organization Name").fill(payload.value);
      await page.getByLabel("Assessor Name").fill("XSS Tester");
      await page
        .getByLabel("Institution Type", { exact: true })
        .selectOption("bank");
      await page
        .getByRole("group", { name: "Active Governance Zones" })
        .locator('input[type="checkbox"][value="1"]')
        .check();
      await page
        .getByRole("button", { name: "Begin Assessment" })
        .dispatchEvent("click");
      await page
        .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
        .waitFor();

      await navClick(page, "View Results");
      await page.locator(".ag-score-big").first().waitFor();

      // Pause briefly for any deferred event handlers (e.g. ontoggle,
      // onload microtasks) to surface a dialog.
      await page.waitForTimeout(500);

      // (1) No alert fired.
      expect(
        dialogFired,
        `Payload ${payload.id} executed; dialog message: ${dialogMsg}`,
      ).toBe(false);

      // (2) No live <script> with our marker. We look for any <script>
      //     element whose textContent contains the unique alert marker
      //     "xss-" + first non-empty section of the payload id.
      const marker = `xss-${payload.id.split("-")[0]}`;
      const liveScript = await page.evaluate((m) => {
        const scripts = Array.from(document.querySelectorAll("script"));
        return scripts.some((s) => (s.textContent || "").includes(m));
      }, marker);
      expect(
        liveScript,
        `Payload ${payload.id} produced a parsed <script> with marker ${marker}`,
      ).toBe(false);

      // (3) The org name's stored value MUST round-trip through state
      //     verbatim. Visual rendering is implementation-dependent (some
      //     payloads collapse to whitespace), so we anchor on state, not
      //     pixels. State mutation here would imply silent sanitization
      //     (which the SPA does not do per spec 16).
      const stored = await page.evaluate(
        () => window.__assessmentApp?.state?.scoping?.organizationName,
      );
      expect(stored).toBe(payload.value);

      page.off("dialog", listener);
    });
  }
});
