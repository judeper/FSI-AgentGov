import { test } from "@playwright/test";
import {
  clearPageStorage,
  expect,
} from "./_harness.mjs";

/**
 * 03d — Filter view-state does not leak across assessments (E2E regression)
 *
 * E2E counterpart to tests/spa/filter-namespace-isolation.test.mjs
 * (phase-c-spec-filter-leak). Verifies role-filter and sector view-state
 * are stored under per-assessment keys and never leak from assessment A
 * into a freshly created assessment B.
 *
 * BEFORE FIX: filters were persisted under global keys ag.roleFilter and
 *   ag.selectedSector; newState() seeded a new assessment from those
 *   globals so a new assessment inherited the previous one's filter.
 * AFTER FIX: filters write to ag.roleFilter-<id> / ag.selectedSector-<id>;
 *   newState() does NOT read globals; loadFromStorage rehydrates
 *   per-id values; deleteSaved cleans them up; init() runs a one-shot
 *   migration of legacy globals onto the most-recent current assessment.
 */

const STORAGE_KEY = "fsi-agentgov-assessment";
const ROLE_FILTER_KEY = "ag.roleFilter";
const SECTOR_KEY = "ag.selectedSector";

async function readCurrentAssessmentId(page) {
  return await page.evaluate((k) => {
    const raw = localStorage.getItem(k + "-current");
    if (!raw) return null;
    try { return JSON.parse(raw).assessmentId || null; } catch { return null; }
  }, STORAGE_KEY);
}

async function startNewAndScope(page, organizationName) {
  await page.getByRole("button", { name: "Start New Assessment" }).dispatchEvent("click");
  await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();
  await page.getByLabel("Organization Name").fill(organizationName);
  await page.getByLabel("Assessor Name").fill("Test Assessor");
  await page.getByLabel("Institution Type", { exact: true }).selectOption("bank");
  const zoneFieldset = page.getByRole("group", { name: "Active Governance Zones" });
  const zone1 = zoneFieldset.locator('input[type="checkbox"][value="1"]');
  if (!(await zone1.isChecked())) await zone1.check();
  await page.getByRole("button", { name: "Begin Assessment" }).dispatchEvent("click");
  await page.getByRole("heading", { name: /Phase 1: Control-Level Assessment/ }).waitFor();
}

async function navigateBackToWelcome(page) {
  await page.waitForTimeout(700);
  await page.locator(".ag-step-indicator").filter({ hasText: /Welcome/ }).first().click();
  await page
    .locator("#assessment-app")
    .getByRole("heading", { name: "Governance Readiness Assessment" })
    .waitFor();
}

test.describe("Filter view-state is namespaced per assessment @regression", () => {
  test("setting a role filter on A does not leak into a freshly-created B @regression", async ({ page }) => {
    page.on("dialog", (d) => { d.dismiss().catch(() => {}); });

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => !!window.__assessmentApp, null, { timeout: 15_000 });

    // -- A: pick a non-default role filter --------------------------------
    await startNewAndScope(page, "Bank A");
    const idA = await readCurrentAssessmentId(page);
    expect(idA).toBeTruthy();

    const filterSelect = page.locator("#ag-role-filter-select");
    await filterSelect.waitFor();
    // Select first non-empty option.
    const firstNonEmpty = await filterSelect.evaluate((el) => {
      for (const o of el.options) if (o.value) return o.value;
      return "";
    });
    expect(firstNonEmpty, "expected at least one non-empty role-filter option").toBeTruthy();
    await filterSelect.selectOption(firstNonEmpty);
    await page.waitForTimeout(700);

    // Assert the filter was saved under per-id slot, not the global key.
    const aFilter = await page.evaluate(([rk, sk, id]) => ({
      perA: localStorage.getItem(rk + "-" + id),
      perSectorA: localStorage.getItem(sk + "-" + id),
      legacyRole: localStorage.getItem(rk),
      legacySector: localStorage.getItem(sk),
    }), [ROLE_FILTER_KEY, SECTOR_KEY, idA]);
    expect(aFilter.perA).toBe(firstNonEmpty);
    // Global legacy keys must NOT be written by the post-fix listener.
    expect(aFilter.legacyRole).toBeNull();

    // -- B: brand new assessment must NOT inherit A's filter ---------------
    await navigateBackToWelcome(page);
    await startNewAndScope(page, "Bank B");
    const idB = await readCurrentAssessmentId(page);
    expect(idB).toBeTruthy();
    expect(idB).not.toBe(idA);

    const stateB = await page.evaluate(() => {
      const app = window.__assessmentApp;
      return app && app.state ? { roleFilter: app.state.roleFilter || "", selectedSector: app.state.selectedSector || "" } : null;
    });
    expect(stateB).not.toBeNull();
    expect(stateB.roleFilter).toBe("");

    const filterSelectB = page.locator("#ag-role-filter-select");
    await filterSelectB.waitFor();
    expect(await filterSelectB.evaluate((el) => el.value)).toBe("");

    // -- Resume A: filter still set ---------------------------------------
    await navigateBackToWelcome(page);
    await page.getByRole("button", { name: /^Resume Bank A/ }).dispatchEvent("click");
    await page.getByRole("heading", { name: /Phase 1: Control-Level Assessment/ }).waitFor();
    const filterSelectA = page.locator("#ag-role-filter-select");
    await filterSelectA.waitFor();
    expect(await filterSelectA.evaluate((el) => el.value)).toBe(firstNonEmpty);
  });

  test("legacy global filter keys migrate to current assessment on init @regression", async ({ page }) => {
    page.on("dialog", (d) => { d.dismiss().catch(() => {}); });

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);

    // Plant a legacy current assessment + legacy global filter keys.
    await page.evaluate(([K, RK, SK]) => {
      const id = "legacy-filter-id";
      const state = {
        assessmentId: id,
        assessmentName: "Legacy Filter Org",
        schemaVersion: "1.4.0",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        scoping: { organizationName: "Legacy Filter Org", assessorName: "L", zones: [1, 2, 3], roles: [] },
        responses: {},
        overrides: {}, drilldown: {}, currentStep: "phase1", completedSteps: [],
        assessmentStatus: "in-progress",
      };
      localStorage.setItem(K + "-current", JSON.stringify(state));
      localStorage.setItem(K + "-data-" + id, JSON.stringify(state));
      localStorage.setItem(
        K + "-list",
        JSON.stringify([{ id, name: "Legacy Filter Org — 2026-01-01", updatedAt: state.updatedAt, progress: 0 }]),
      );
      localStorage.setItem(RK, "AI Governance Lead");
      localStorage.setItem(SK, "broker-dealer");
    }, [STORAGE_KEY, ROLE_FILTER_KEY, SECTOR_KEY]);

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => !!window.__assessmentApp, null, { timeout: 15_000 });

    // Init should have moved legacy globals onto the legacy id.
    const after = await page.evaluate(([K, RK, SK, id]) => ({
      perRole: localStorage.getItem(RK + "-" + id),
      perSector: localStorage.getItem(SK + "-" + id),
      legacyRole: localStorage.getItem(RK),
      legacySector: localStorage.getItem(SK),
      flag: localStorage.getItem(K + "-filter-migration-v1"),
    }), [STORAGE_KEY, ROLE_FILTER_KEY, SECTOR_KEY, "legacy-filter-id"]);

    expect(after.perRole).toBe("AI Governance Lead");
    expect(after.perSector).toBe("broker-dealer");
    expect(after.legacyRole).toBeNull();
    expect(after.legacySector).toBeNull();
    expect(after.flag).toBe("1");
  });
});
