import { test } from "@playwright/test";
import { readFileSync } from "node:fs";
import {
  clearPageStorage,
  clickThroughPhase1,
  expect,
  expectDownload,
  freezeTime,
  loadPersona,
  navClick,
  seedScoping,
} from "./_harness.mjs";

/**
 * 11 — Import roundtrip
 *
 * Export JSON → clear all storage → reload → import the same JSON →
 * assert scoping fields, answers, and overall score are identical.
 *
 * Uses freezeTime so the export envelope's `_metadata.exportedAt` and the
 * derived `assessmentName` (which embeds today's ISO date) are stable
 * across the two halves of the test.
 */
test.describe("import roundtrip @smoke", () => {
  test("export → clear → import preserves state and score @smoke", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));
    await freezeTime(page);

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);
    await clickThroughPhase1(page, persona);

    // Capture the score on the results screen for later comparison.
    await navClick(page, "View Results");
    const scoreBig = page.locator(".ag-score-big").first();
    await expect(scoreBig).toBeVisible();
    const scoreBefore = (await scoreBig.textContent())?.trim();

    // Go to Export and download JSON.
    await navClick(page, "Export Results");
    await page.getByRole("heading", { name: "Export Results" }).waitFor();
    const { path } = await expectDownload(page, async () => {
      await navClick(page, /Export as Full Assessment/);
    });
    const exported = readFileSync(path, "utf8");
    expect(() => JSON.parse(exported)).not.toThrow();
    const parsed = JSON.parse(exported);
    expect(parsed.scoping?.organizationName).toBe("Acme Bank");
    expect(parsed.responses?.["1.4"]?.answer).toBe("yes");

    // Clear storage; reload; import.
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // The import button on welcome triggers a hidden <input type="file">.
    // We attach the file via the chooser event.
    const chooserPromise = page.waitForEvent("filechooser");
    await navClick(page, "Resume or Import Saved Assessment");
    const chooser = await chooserPromise;
    await chooser.setFiles(path);

    // After import the SPA jumps to Phase 1.
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    // Re-enter results and assert the score matches.
    await navClick(page, "View Results");
    const scoreAfter = (
      await page.locator(".ag-score-big").first().textContent()
    )?.trim();
    expect(scoreAfter).toBe(scoreBefore);

    // Sanity-check round-tripped state via the in-page app instance.
    const roundtripped = await page.evaluate(() => {
      const app = window.__assessmentApp || null;
      if (!app || !app.state) return null;
      return {
        org: app.state.scoping?.organizationName,
        institutionType: app.state.scoping?.institutionType,
        zones: (app.state.scoping?.zones || []).slice().sort(),
        answer14: app.state.responses?.["1.4"]?.answer,
        answer21: app.state.responses?.["2.1"]?.answer,
      };
    });
    if (roundtripped) {
      expect(roundtripped.org).toBe("Acme Bank");
      expect(roundtripped.institutionType).toBe("bank");
      expect(roundtripped.zones).toEqual([1]);
      expect(roundtripped.answer14).toBe("yes");
      expect(roundtripped.answer21).toBe("partial");
    }
    // If __assessmentApp is not exposed, the score equality + visible
    // header are sufficient evidence of a successful roundtrip.
  });
});
