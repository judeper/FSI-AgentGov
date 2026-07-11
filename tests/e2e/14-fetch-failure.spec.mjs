import { test } from "@playwright/test";
import { clearPageStorage, expect } from "./_harness.mjs";

/**
 * 14 — Fetch failure resilience (E2E regression)
 *
 * The SPA loads four runtime JSON manifests (assessment-app.js L450–L536):
 *   - <base>assessment-data.json    (REQUIRED — error UI on failure)
 *   - <site>/assessment/data/controls.json        (optional — console.warn)
 *   - <site>/assessment/data/solutions-lock.json  (optional — console.warn)
 *   - <site>/assessment/i18n/en.json              (optional — console.warn)
 *
 * Optional manifests must degrade silently. The required one shows a
 * retry-able error banner. There is NO `/version.json` runtime fetch (that
 * file exists for the prod-smoke probe only). This spec verifies all four
 * documented behaviors.
 *
 * IMPORTANT page.route timing: routes MUST be installed BEFORE navigation
 * so the SPA's first fetch is intercepted. Each sub-test sets routes on a
 * fresh page.goto.
 */

const REQUIRED = "**/javascripts/assessment-data.json";
const OPTIONAL_CONTROLS = "**/assessment/data/controls.json";
const OPTIONAL_SOLUTIONS = "**/assessment/data/solutions-lock.json";
const OPTIONAL_I18N = "**/assessment/i18n/en.json";

test.describe("fetch failure resilience @regression", () => {
  test("required manifest 404 → SPA shows retry-able error UI @regression", async ({
    page,
  }) => {
    // Ordering requirement: page.route() MUST be installed before
    // page.goto() so the SPA's first fetch of assessment-data.json is
    // intercepted by the 404 stub. Inverting this order races the route
    // handler against the network request and is a known local-Windows
    // flake source (Phase B' triage P2).
    await page.route(REQUIRED, (route) =>
      route.fulfill({ status: 404, body: "not found" }),
    );
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    // The SPA injects an admonition with a Retry button on data load failure.
    await page
      .locator("#ag-retry-load")
      .waitFor({ state: "visible", timeout: 15_000 });
    // Default expect timeout (5s) is too tight on slow local hardware
    // when the failure-UI render races initial layout. Use 10s.
    await expect(page.locator(".admonition.failure")).toBeVisible({
      timeout: 10_000,
    });
    await expect(page.locator(".admonition.failure")).toContainText(
      /Could not load assessment data/i,
      { timeout: 10_000 },
    );
  });

  test("required manifest 500 → SPA shows retry-able error UI @regression", async ({
    page,
  }) => {
    await page.route(REQUIRED, (route) =>
      route.fulfill({ status: 500, body: "boom" }),
    );
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await page
      .locator("#ag-retry-load")
      .waitFor({ state: "visible", timeout: 15_000 });
  });

  test("optional manifest 404 → SPA degrades silently (no error UI) @regression", async ({
    page,
  }) => {
    const consoleErrors = [];
    page.on("console", (msg) => {
      if (msg.type() !== "error") return;
      const text = msg.text();
      // Browser auto-emits a `console.error` for any failed fetch and
      // for various site-wide CSP / mixed-content events that have
      // nothing to do with the SPA's manifest handling. Filter those.
      if (/Failed to load resource/i.test(text)) return;
      if (/Content Security Policy/i.test(text)) return;
      if (/frame-ancestors/i.test(text)) return;
      consoleErrors.push(text);
    });
    await page.route(OPTIONAL_CONTROLS, (route) =>
      route.fulfill({ status: 404, body: "not found" }),
    );
    await page.route(OPTIONAL_SOLUTIONS, (route) =>
      route.fulfill({ status: 404, body: "not found" }),
    );
    await page.route(OPTIONAL_I18N, (route) =>
      route.fulfill({ status: 404, body: "not found" }),
    );
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    // Welcome screen still renders.
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });
    // No retry-able error banner.
    await expect(page.locator("#ag-retry-load")).toHaveCount(0);
    // The SPA logs console.warn for optional manifest failures, NOT
    // console.error. Asserting no console.error means no unexpected
    // exceptions leaked.
    expect(consoleErrors).toEqual([]);
  });

  test("optional manifest 500 → SPA degrades silently @regression", async ({
    page,
  }) => {
    await page.route(OPTIONAL_CONTROLS, (route) =>
      route.fulfill({ status: 500, body: "boom" }),
    );
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });
    await expect(page.locator("#ag-retry-load")).toHaveCount(0);
  });

  test("offline mid-flow → in-progress state preserved in localStorage @regression", async ({
    page,
    context,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // Drive scoping inline (cheap; no network needed once SPA is loaded).
    await page.getByRole("button", { name: "Start New Assessment" })
      .dispatchEvent("click");
    await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();
    await page.getByLabel("Organization Name").fill("Offline Bank");
    await page.getByLabel("Assessor Name").fill("Net Off");
    await page
      .getByLabel("Institution Type", { exact: true })
      .selectOption("bank");
    await page
      .getByRole("group", { name: "Active Governance Zones" })
      .locator('input[type="checkbox"][value="1"]')
      .check();
    await page.getByRole("button", { name: "Begin Assessment" })
      .dispatchEvent("click");
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    // Take the network offline. The SPA does not fetch during phase1, so
    // the user can keep answering controls; the in-progress state is
    // already in localStorage from the scoping handoff.
    await context.setOffline(true);

    const stateOffline = await page.evaluate(() =>
      localStorage.getItem("fsi-agentgov-assessment-current"),
    );
    expect(stateOffline).toBeTruthy();
    const parsed = JSON.parse(stateOffline);
    expect(parsed.scoping.organizationName).toBe("Offline Bank");

    // Restore network and visit fresh — assessment must be resumable.
    // page.goto("/assessment/") instead of page.reload() so AS8's URL routing
    // doesn't auto-resume back into the offline-saved phase1 step (which would
    // bypass the welcome-list saved-assessments surface this test asserts).
    await context.setOffline(false);
    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });
    // The saved-assessments list surface shows our resumable entry.
    await expect(page.locator(".ag-saved-list")).toBeVisible();
    await expect(
      page.getByRole("heading", { name: /^(All saved assessments|Saved assessment)$/i }),
    ).toBeVisible();
  });
});
