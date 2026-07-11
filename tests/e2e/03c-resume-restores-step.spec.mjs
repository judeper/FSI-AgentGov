import { test } from "@playwright/test";
import {
  clearPageStorage,
  expect,
  getResumeBannerButton,
  getSavedListResumeButton,
  selectControlAnswer,
} from "./_harness.mjs";

/**
 * 03c — Resume restores saved wizard step (E2E regression)
 *
 * E2E counterpart to tests/spa/resume-step-persistence.test.mjs
 * (phase-c-spec-resume-step). Verifies that a user who reaches Results
 * (or any later step) is taken back to that exact step on Resume —
 * not bounced back to Phase 1.
 *
 * BEFORE FIX: the Resume click handler called goToStep("phase1")
 *   unconditionally and saveToStorage did not persist this.step.
 * AFTER FIX: saveToStorage writes this.step into state on every save;
 *   loadFromStorage restores it; the Resume handler honors self.step.
 *
 * SPA literal STORAGE_KEY (docs/javascripts/assessment-app.js):
 *   "fsi-agentgov-assessment"
 */

const STORAGE_KEY = "fsi-agentgov-assessment";

async function readPerIdSlot(page, id) {
  return await page.evaluate(
    ([k, theId]) => {
      const raw = localStorage.getItem(k + "-data-" + theId);
      return raw ? JSON.parse(raw) : null;
    },
    [STORAGE_KEY, id],
  );
}

async function readCurrentAssessmentId(page) {
  return await page.evaluate((k) => {
    const raw = localStorage.getItem(k + "-current");
    if (!raw) return null;
    try { return JSON.parse(raw).assessmentId || null; } catch { return null; }
  }, STORAGE_KEY);
}

async function activeStep(page) {
  return await page.evaluate(() => {
    const app = window.__assessmentApp;
    return app ? app.step : null;
  });
}

async function startNewAndScope(page, organizationName) {
  const startBtn = page.getByRole("button", { name: "Start New Assessment" });
  await startBtn.waitFor({ timeout: 15_000 });
  await startBtn.dispatchEvent("click");
  await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();
  await page.getByLabel("Organization Name").fill(organizationName);
  await page.getByLabel("Assessor Name").fill("Test Assessor");
  await page.getByLabel("Institution Type", { exact: true }).selectOption("bank");
  const zoneFieldset = page.getByRole("group", { name: "Active Governance Zones" });
  const zone1 = zoneFieldset.locator('input[type="checkbox"][value="1"]');
  if (!(await zone1.isChecked())) await zone1.check();
  const beginBtn = page.getByRole("button", { name: "Begin Assessment" });
  await beginBtn.waitFor({ timeout: 15_000 });
  await beginBtn.dispatchEvent("click");
  await page.getByRole("heading", { name: /Phase 1: Control-Level Assessment/ }).waitFor();
}

async function navigateBackToWelcome(page) {
  await page.waitForTimeout(700);
  // Click the welcome step indicator (top nav) to return.
  await page.locator(".ag-step-indicator").filter({ hasText: /Welcome/ }).first().click();
  await page
    .locator("#assessment-app")
    .getByRole("heading", { name: "Governance Readiness Assessment" })
    .waitFor();
}

test.describe("Resume restores saved wizard step @regression", () => {
  test("Resume from Results lands back on Results, not Phase 1 @regression", async ({ page }) => {
    page.on("dialog", (d) => { d.dismiss().catch(() => {}); });

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });
    // Wait for SPA hydration (window.__assessmentApp).
    await page.waitForFunction(() => !!window.__assessmentApp, null, { timeout: 15_000 });

    await startNewAndScope(page, "Bank Resume");
    await selectControlAnswer(page, "1.1", "yes");
    const id = await readCurrentAssessmentId(page);
    expect(id).toBeTruthy();

    // Navigate forward: Phase 1 → Results (no gaps means no Phase 2 button)
    await page.getByRole("button", { name: "View Results", exact: true }).first().dispatchEvent("click");
    await page.getByRole("heading", { name: /^Results/ }).waitFor();

    // Sanity: app.step is "results" and the persisted slot reflects that.
    expect(await activeStep(page)).toBe("results");
    await page.waitForTimeout(700);
    let slot = await readPerIdSlot(page, id);
    expect(slot, "per-id slot must exist").not.toBeNull();
    expect(slot.step).toBe("results");

    // Go back to welcome and Resume.
    await navigateBackToWelcome(page);
    await expect(getResumeBannerButton(page, /^Resume most recent assessment: Bank Resume/)).toHaveCount(1);
    await expect(getSavedListResumeButton(page, /^Resume Bank Resume/)).toHaveCount(1);
    await getResumeBannerButton(page, /^Resume most recent assessment: Bank Resume/)
      .dispatchEvent("click");

    // Assert Resume landed on Results (NOT Phase 1).
    await page.getByRole("heading", { name: /^Results/ }).waitFor();
    expect(await activeStep(page)).toBe("results");
  });

  test("legacy save without `step` defaults to Phase 1 @regression", async ({ page }) => {
    page.on("dialog", (d) => { d.dismiss().catch(() => {}); });

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);

    // Plant a legacy assessment (no `step` field) directly into localStorage.
    await page.evaluate((K) => {
      const id = "legacy-resume-id";
      const state = {
        assessmentId: id,
        assessmentName: "Legacy Org",
        schemaVersion: "1.4.0",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        scoping: { organizationName: "Legacy Org", assessorName: "L", zones: [1, 2, 3], roles: [] },
        responses: { "1.1": { answer: "yes", notes: "", evidenceRef: "" } },
        overrides: {}, drilldown: {}, currentStep: "phase1", completedSteps: [],
        assessmentStatus: "in-progress",
        // intentionally NO `step` field
      };
      localStorage.setItem(K + "-data-" + id, JSON.stringify(state));
      localStorage.setItem(
        K + "-list",
        JSON.stringify([{ id, name: "Legacy Org — 2026-01-01", updatedAt: state.updatedAt, progress: 1 }]),
      );
    }, STORAGE_KEY);

    await page.reload({ waitUntil: "domcontentloaded" });
    await page.waitForFunction(() => !!window.__assessmentApp, null, { timeout: 15_000 });

    // Click Resume on the legacy assessment.
    await expect(getSavedListResumeButton(page, /^Resume Legacy Org/)).toHaveCount(1);
    await getSavedListResumeButton(page, /^Resume Legacy Org/).dispatchEvent("click");
    await page.getByRole("heading", { name: /Phase 1: Control-Level Assessment/ }).waitFor();
    expect(await activeStep(page)).toBe("phase1");
  });
});
