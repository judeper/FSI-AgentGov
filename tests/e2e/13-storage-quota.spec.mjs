import { test } from "@playwright/test";
import {
  clearPageStorage,
  expect,
  loadPersona,
  seedScoping,
} from "./_harness.mjs";

/**
 * 13 — Storage quota banner regression (PR #142 hardening)
 *
 * The SPA's saveToStorage (assessment-app.js L987–L996) catches
 * QuotaExceededError and surfaces a sticky `.ag-quota-banner` with
 * actionable copy: "Browser storage is full. Your latest changes may not
 * have been saved. Export your assessment to JSON, then clear old saved
 * assessments to free space."
 *
 * This spec exercises the full lifecycle:
 *   1. Seed an assessment (saves cleanly).
 *   2. Fill localStorage near quota with synthetic filler entries.
 *   3. Trigger another save (via window.__assessmentApp.saveToStorage()).
 *   4. Assert the quota banner appears with actionable text.
 *   5. Verify pre-existing saved data is preserved (no silent loss).
 *   6. Clear fillers; trigger save again; assert banner clears + saving works.
 *
 * Tagged @slow because the localStorage fill loop pushes a Chromium tab to
 * its 5–10MB quota and can take 2–6s per attempt.
 */
test.describe("storage quota banner @regression @slow", () => {
  test("quota fills → banner appears → cleanup restores save @regression @slow", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);
    // seedScoping leaves us on Phase 1 with a saved state slot.

    // Capture pre-existing storage snapshot (the SPA's own keys, not fillers).
    // We assert on durable IDENTITY (assessmentId + organizationName) rather
    // than full-text equality because the SPA's debounced save can update
    // `updatedAt` between snapshots.
    const before = await page.evaluate(() => {
      const cur = JSON.parse(
        localStorage.getItem("fsi-agentgov-assessment-current") || "null",
      );
      const ownKeys = Object.keys(localStorage).filter(
        (k) => k.indexOf("__filler_") !== 0,
      );
      return { id: cur && cur.assessmentId, org: cur && cur.scoping && cur.scoping.organizationName, ownKeys };
    });
    expect(before.ownKeys.length).toBeGreaterThan(0);
    expect(before.id).toBeTruthy();
    expect(before.org).toBe("Acme Bank");

    // Force the SPA to hit the quota error path deterministically by
    // monkey-patching localStorage.setItem to throw QuotaExceededError on
    // the SPA's data keys. Relying on actually saturating Chromium's
    // localStorage quota with filler entries is flaky across runs because
    // Chromium permits in-place updates of pre-existing keys even when
    // total usage is at the quota ceiling, and the per-origin quota can
    // grow with cumulative disk usage during a regression batch.
    await page.evaluate(() => {
      const realSetItem = Storage.prototype.setItem;
      window.__realSetItem = realSetItem;
      Storage.prototype.setItem = function (k, v) {
        if (typeof k === "string" && k.indexOf("fsi-agentgov-assessment") === 0) {
          const err = new Error("Quota exceeded (test stub)");
          err.name = "QuotaExceededError";
          err.code = 22;
          throw err;
        }
        return realSetItem.call(this, k, v);
      };
    });

    // Pre-existing assessment identity must NOT have been clobbered by fillers.
    const during = await page.evaluate(() => {
      const cur = JSON.parse(
        localStorage.getItem("fsi-agentgov-assessment-current") || "null",
      );
      return { id: cur && cur.assessmentId, org: cur && cur.scoping && cur.scoping.organizationName };
    });
    expect(during.id).toBe(before.id);
    expect(during.org).toBe(before.org);

    // Trigger a save while quota is exhausted. The SPA must detect the
    // QuotaExceededError and re-render with the banner.
    const bannerShown = await page.evaluate(() => {
      const app = window.__assessmentApp;
      if (!app) return null;
      // Force a save attempt; should throw internally and set _quotaError.
      try { app.saveToStorage(); } catch (_) { /* swallowed by SPA */ }
      return !!app._quotaError;
    });
    expect(bannerShown).toBe(true);

    // Banner DOM is rendered (re-render happens inside saveToStorage's
    // catch when _quotaError flips to true).
    const banner = page.locator(".ag-quota-banner");
    await expect(banner).toBeVisible();
    await expect(banner).toContainText(/storage is full/i);
    await expect(banner).toContainText(/Export.*JSON|clear old saved/i);

    // Cleanup: restore real setItem and confirm SPA can save again.
    await page.evaluate(() => {
      Storage.prototype.setItem = window.__realSetItem;
      delete window.__realSetItem;
    });
    const recovered = await page.evaluate(() => {
      const app = window.__assessmentApp;
      if (!app) return null;
      app.saveToStorage();
      return !!app._quotaError;
    });
    expect(recovered).toBe(false);
    await expect(page.locator(".ag-quota-banner")).toHaveCount(0);
  });
});
