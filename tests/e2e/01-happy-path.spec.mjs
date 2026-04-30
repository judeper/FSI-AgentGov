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
 * 01 — Happy path smoke
 *
 * Welcome → scoping (minimal-ciso, Zone 1) → answer 5 controls →
 * results page → assert overall score band rendered.
 *
 * No exports. This is the canonical smoke for the assessment flow and
 * the template every subsequent regression spec should imitate.
 */
test.describe("happy path @smoke", () => {
  test("scope, answer, summary @smoke", async ({ page }) => {
    // The Phase 1 "View Results" button surfaces a confirm() asking the
    // user to save before viewing results. Auto-dismiss to keep the
    // smoke flow purely UI-driven.
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);
    await clickThroughPhase1(page, persona);

    // Proceed to results.
    await navClick(page, "View Results");

    // The Results "Scorecard" tab renders an `.ag-score-big` element with
    // a RAG class (green/amber/red). Assert presence + a non-empty score.
    const scoreBig = page.locator(".ag-score-big").first();
    await expect(scoreBig).toBeVisible();
    const ragClasses = await scoreBig.evaluate((el) => Array.from(el.classList));
    expect(ragClasses.some((c) => ["green", "amber", "red"].includes(c))).toBe(
      true,
    );
    await expect(scoreBig).not.toHaveText("—");
  });
});
