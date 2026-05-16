import { test } from "@playwright/test";
import {
  clearPageStorage,
  expect,
  expectDownload,
  loadPersona,
  navClick,
  seedScoping,
} from "./_harness.mjs";
import { readFileSync } from "node:fs";

/**
 * 22 — edge-empty persona (scoped but zero responses)
 *
 * Verifies graceful handling of a fully-scoped assessment that has not
 * yet recorded any user answers:
 *
 *   1. Welcome → seed the edge-empty persona via the standard flow.
 *   2. Phase 1 renders; no answers stored above the SPA's auto-NA
 *      (controls outside selected zones are auto-NA'd as a feature).
 *   3. saveToStorage + reload + resume preserves zero authored answers
 *      (i.e. no auto-default to "Yes" or any seeded value).
 *   4. JSON export of an empty assessment is structurally valid and
 *      `responses` is an object (possibly containing only auto-NA
 *      entries) — never `null`.
 *   5. Score on results screen renders "—" (em-dash placeholder), NOT
 *      "NaN%", "Infinity%", or an empty cell. Verified at the DOM
 *      level on `.ag-score-big`.
 */
test.describe("edge-empty persona @regression", () => {
  test("zero-response assessment exports cleanly and renders no NaN/Infinity score @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    const persona = loadPersona("edge-empty");
    expect(Object.keys(persona.answers || {}).length).toBe(0);

    await seedScoping(page, persona);

    // (1) Phase 1 reached. Capture the user-authored response count.
    //     The SPA auto-applies N/A to out-of-zone controls; those are
    //     not user authored, so we filter on the autoNa flag.
    const authoredBeforeSave = await page.evaluate(() => {
      const r = window.__assessmentApp?.state?.responses || {};
      return Object.values(r).filter((v) => v && !v.autoNa).length;
    });
    expect(authoredBeforeSave).toBe(0);

    // Force a save so the assessment is on the saved-list when we reload.
    await page.evaluate(() => window.__assessmentApp.saveToStorage());

    // (2) Fresh visit + manual resume; authored count must still be 0.
    // Uses page.goto("/assessment/") rather than page.reload() because AS8's
    // URL routing preserves ?step= across reload and would auto-resume into
    // phase1, bypassing the welcome-list "Resume" affordance this test exercises.
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });
    const resumeBtn = page.getByRole("button", {
      name: new RegExp(`Resume ${persona.scoping.organizationName}`),
    });
    await resumeBtn.first().click();
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    const authoredAfterResume = await page.evaluate(() => {
      const r = window.__assessmentApp?.state?.responses || {};
      return Object.values(r).filter((v) => v && !v.autoNa).length;
    });
    expect(authoredAfterResume).toBe(0);

    // (3) Results screen — overall score must be "—", never NaN/Infinity.
    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();
    const scoreText = await page
      .locator(".ag-score-big")
      .first()
      .textContent();
    const trimmed = (scoreText || "").trim();
    expect(trimmed).not.toMatch(/NaN/i);
    expect(trimmed).not.toMatch(/Infinity/i);
    // Acceptable values: em-dash placeholder OR a valid percentage.
    expect(trimmed === "—" || /^\d+(\.\d+)?%$/.test(trimmed)).toBe(true);

    // (4) JSON export is structurally valid; responses is an object.
    await navClick(page, "Export Results");
    await page.getByRole("heading", { name: "Export Results" }).waitFor();
    const { path } = await expectDownload(page, async () => {
      await navClick(page, /Export as Full Assessment/);
    });
    const exported = JSON.parse(readFileSync(path, "utf8"));
    expect(exported).toBeTruthy();
    expect(typeof exported.responses).toBe("object");
    expect(exported.responses).not.toBeNull();
    expect(Array.isArray(exported.responses)).toBe(false);
    // Authored responses (non-autoNa) must be 0 in the export.
    const authoredInExport = Object.values(exported.responses || {}).filter(
      (v) => v && !v.autoNa,
    ).length;
    expect(authoredInExport).toBe(0);
  });
});
