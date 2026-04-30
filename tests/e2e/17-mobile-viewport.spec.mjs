import { test, devices } from "@playwright/test";
import { clearPageStorage, expect } from "./_harness.mjs";

/**
 * 17 — Mobile viewport + touch-target sizing (E2E regression)
 *
 * Per WCAG 2.5.5 (Target Size, Level AAA) and 2.5.8 (Target Size
 * Minimum, Level AA in WCAG 2.2), interactive controls should be at
 * least 44x44 CSS pixels. We verify the foundational SPA buttons
 * ("Start New Assessment", "Resume or Import Saved Assessment") meet
 * that floor on three device profiles drawn from `playwright.devices`.
 *
 * We also assert no horizontal scroll on the welcome and scoping
 * screens — a classic mobile-layout regression smell.
 *
 * Tagged @slow because emulation across 3 profiles serially can push
 * past 5s wall-clock per device on cold-cache mkdocs builds.
 */

const DEVICE_PROFILES = [
  { label: "iPhone 14", config: devices["iPhone 14"] },
  { label: "iPad (gen 7)", config: devices["iPad (gen 7)"] },
  { label: "Pixel 5", config: devices["Pixel 5"] }, // small Android proxy
];

// Buttons we require to meet the 44x44 touch-target floor on mobile.
const REQUIRED_TAP_TARGETS = [
  "Start New Assessment",
  "Resume or Import Saved Assessment",
];

for (const profile of DEVICE_PROFILES) {
  if (!profile.config) {
    // Defensive: if Playwright drops a device name in a future update,
    // skip rather than crash. Documented per No-Phantom-Coverage.
    test.skip(`mobile viewport ${profile.label} (device profile not registered) @regression`, () => {});
    continue;
  }

  // Strip `defaultBrowserType` and other top-level-only keys before
  // applying via test.use(); Playwright forbids those inside describe.
  const cfg = profile.config;
  const useOpts = {
    viewport: cfg.viewport,
    userAgent: cfg.userAgent,
    deviceScaleFactor: cfg.deviceScaleFactor,
    isMobile: cfg.isMobile,
    hasTouch: cfg.hasTouch,
  };

  test.describe(`mobile viewport ${profile.label} @regression @slow`, () => {
    test.use(useOpts);

    test(`welcome + scoping render without horizontal scroll; tap targets ≥44x44 @regression @slow`, async ({
      page,
    }) => {
      page.on("dialog", (d) => d.dismiss().catch(() => {}));
      await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
      await clearPageStorage(page);
      await page.reload({ waitUntil: "domcontentloaded" });

      await page
        .getByRole("button", { name: "Start New Assessment" })
        .waitFor({ timeout: 15_000 });

      // Horizontal scroll smoke: documentElement.scrollWidth must not
      // exceed clientWidth by more than 1px (sub-pixel rounding).
      const overflow = await page.evaluate(() => {
        const d = document.documentElement;
        return d.scrollWidth - d.clientWidth;
      });
      expect(overflow).toBeLessThanOrEqual(1);

      // Touch-target sizing on welcome.
      for (const name of REQUIRED_TAP_TARGETS) {
        const btn = page.getByRole("button", { name });
        await expect(btn).toBeVisible();
        const box = await btn.boundingBox();
        expect(box, `${name} should have a bounding box`).toBeTruthy();
        expect(box.width, `${name} width on ${profile.label}`).toBeGreaterThanOrEqual(44);
        expect(box.height, `${name} height on ${profile.label}`).toBeGreaterThanOrEqual(44);
      }

      // Advance to scoping; assert no horizontal scroll there either.
      await page
        .getByRole("button", { name: "Start New Assessment" })
        .dispatchEvent("click");
      await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();
      const overflowScoping = await page.evaluate(() => {
        const d = document.documentElement;
        return d.scrollWidth - d.clientWidth;
      });
      expect(overflowScoping).toBeLessThanOrEqual(1);

      // The "Begin Assessment" button must also meet the tap target floor.
      const beginBtn = page.getByRole("button", { name: "Begin Assessment" });
      await expect(beginBtn).toBeVisible();
      const beginBox = await beginBtn.boundingBox();
      expect(beginBox).toBeTruthy();
      expect(beginBox.height).toBeGreaterThanOrEqual(44);
      expect(beginBox.width).toBeGreaterThanOrEqual(44);
    });
  });
}
