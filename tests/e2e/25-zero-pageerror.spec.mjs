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
 * 25 — Zero pageerror canary (smoke)
 *
 * Narrow high-signal smoke that runs the happy path while listening for
 * ALL `pageerror` events and any `console` event of severity `error`.
 * Asserts EXACTLY zero. This is intentionally redundant with spec 01's
 * implicit error-cleanliness expectation — the value here is a single
 * focused assertion that runs first in CI for fast feedback when a
 * deploy ships a JS regression.
 *
 * Previously surfaced two CSP defects (now fixed in fix/csp-meta-defects):
 *   1. api.github.com blocked by connect-src 'self' — fixed by allow-listing
 *      https://api.github.com in overrides/main.html and csp-allowed.json.
 *   2. frame-ancestors via meta-CSP (browser-ignored) — removed from meta;
 *      replaced with inline JS frame-busting guard at top of <head>.
 */
test.describe("zero pageerror canary @smoke", () => {
  test("happy path produces zero pageerrors / console errors @smoke", async ({
    page,
  }) => {
    const pageErrors = [];
    const consoleErrors = [];
    page.on("pageerror", (err) => {
      pageErrors.push(`${err.name}: ${err.message}`);
    });
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    const persona = loadPersona("minimal-ciso");
    await seedScoping(page, persona);
    await clickThroughPhase1(page, persona);
    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();

    const summary = (label, list) =>
      list.length === 0 ? "" : `\n${label}:\n  - ${list.join("\n  - ")}`;
    expect(
      pageErrors.length + consoleErrors.length,
      `Expected zero JS errors during happy path.${summary("pageerror", pageErrors)}${summary("console.error", consoleErrors)}`,
    ).toBe(0);
  });
});
