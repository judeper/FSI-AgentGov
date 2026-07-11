import { test } from "@playwright/test";
import {
  clearPageStorage,
  expect,
  getSavedListResumeButton,
  selectControlAnswer,
  navClick,
} from "./_harness.mjs";

/**
 * 03b — Saved-list multi-assessment durability (E2E regression)
 *
 * E2E counterpart to tests/spa/saved-list-multi-assessment.test.mjs (PR #144,
 * iter3-2-001 P0). Verifies the per-id storage slot behaviour end-to-end
 * through the real browser localStorage:
 *
 *   - Each saved assessment lives in its own STORAGE_KEY+"-data-<id>" slot.
 *   - Resuming a non-current saved assessment loads the correct data.
 *   - Deleting one assessment leaves the other intact + resumable.
 *
 * BEFORE PR #144: saveToStorage wrote only to STORAGE_KEY+"-current", so the
 * older of two saved assessments silently lost its data and "Resume" no-op'd.
 * This spec is the regression net for that bug at the UI level — if it
 * regresses, this spec fails before the unit-level vitest does.
 *
 * SPA literal STORAGE_KEY value (docs/javascripts/assessment-app.js L16):
 *   "fsi-agentgov-assessment"
 */

const STORAGE_KEY = "fsi-agentgov-assessment";

/** Helpers -------------------------------------------------------- */

/** Read the SPA's app instance state via the per-id slot in localStorage. */
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

async function listDataSlotKeys(page) {
  return await page.evaluate(() =>
    Object.keys(localStorage).filter((k) => k.includes("-data-")),
  );
}

/** Drive: welcome → scoping → Phase 1 with custom org name. */
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

/** Force a synchronous flush of the debounced save by going Phase1→Scoping→Back. */
async function navigateBackToWelcome(page) {
  // Wait for the 500ms debounced save to flush.
  await page.waitForTimeout(700);
  await page.getByRole("button", { name: "Back to Scoping" }).dispatchEvent("click");
  await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();
  await page.getByRole("button", { name: "Back", exact: true }).dispatchEvent("click");
  // The mkdocs page itself emits an h1 with the same text as the SPA's
  // welcome h2; scope inside the SPA container to disambiguate.
  await page
    .locator("#assessment-app")
    .getByRole("heading", { name: "Governance Readiness Assessment" })
    .waitFor();
}

test.describe("saved-list multi-assessment @regression", () => {
  test("two assessments persist independently, resume + delete are isolated @regression", async ({ page }) => {
    // Default dialog handler: dismiss any incidental confirm() prompts (e.g.
    // the Phase 1 "save before results" prompt). The destructive-gate flow
    // in step "Delete Bank A" is handled with explicit one-shot hooks
    // installed AFTER removing this default — see comment below.
    const defaultDialogHandler = (d) => { d.dismiss().catch(() => {}); };
    page.on("dialog", defaultDialogHandler);

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // -- Assessment A -------------------------------------------------
    await startNewAndScope(page, "Bank A");
    await selectControlAnswer(page, "1.1", "yes");
    await selectControlAnswer(page, "1.2", "partial");
    const idA = await readCurrentAssessmentId(page);
    expect(idA, "assessment A id should exist after first save").toBeTruthy();
    await navigateBackToWelcome(page);

    // -- Assessment B (different org) ---------------------------------
    await startNewAndScope(page, "Bank B");
    await selectControlAnswer(page, "1.3", "no");
    await selectControlAnswer(page, "1.4", "yes");
    await selectControlAnswer(page, "1.5", "partial");
    const idB = await readCurrentAssessmentId(page);
    expect(idB, "assessment B id should exist after first save").toBeTruthy();
    expect(idB).not.toBe(idA);

    // -- Resume A: assert A's 2 answers, NOT B's ---------------------
    await navigateBackToWelcome(page);
    // Resume buttons are labelled "Resume <assessmentName>" where the
    // assessmentName is "<org> — <YYYY-MM-DD>" (set by Begin Assessment).
    // We match by prefix to stay date-agnostic.
    await getSavedListResumeButton(page, /^Resume Bank A/).dispatchEvent("click");
    await page.getByRole("heading", { name: /Phase 1: Control-Level Assessment/ }).waitFor();
    const slotA = await readPerIdSlot(page, idA);
    expect(slotA, "Per-id slot for A must exist").not.toBeNull();
    expect(slotA.responses["1.1"]?.answer).toBe("yes");
    expect(slotA.responses["1.2"]?.answer).toBe("partial");
    // A must NOT contain B's responses.
    expect(slotA.responses["1.3"]).toBeUndefined();
    expect(slotA.responses["1.4"]).toBeUndefined();
    expect(slotA.responses["1.5"]).toBeUndefined();
    expect(slotA.scoping?.organizationName).toBe("Bank A");

    // -- Resume B: assert B's 3 answers, A's absent -------------------
    await navigateBackToWelcome(page);
    await getSavedListResumeButton(page, /^Resume Bank B/).dispatchEvent("click");
    await page.getByRole("heading", { name: /Phase 1: Control-Level Assessment/ }).waitFor();
    const slotB = await readPerIdSlot(page, idB);
    expect(slotB, "Per-id slot for B must exist").not.toBeNull();
    expect(slotB.responses["1.3"]?.answer).toBe("no");
    expect(slotB.responses["1.4"]?.answer).toBe("yes");
    expect(slotB.responses["1.5"]?.answer).toBe("partial");
    expect(slotB.responses["1.1"]).toBeUndefined();
    expect(slotB.responses["1.2"]).toBeUndefined();
    expect(slotB.scoping?.organizationName).toBe("Bank B");

    // -- Delete A: B remains intact, list shows only B ----------------
    await navigateBackToWelcome(page);

    // Two confirm() prompts fire on a Delete with answered controls:
    //   1. Welcome-level "Delete this assessment?" → accept (proceed).
    //   2. deleteSaved's destructive-gate "export to JSON before deleting?"
    //      → DISMISS (skip export so we don't trigger a stray download).
    // Multiple page.on("dialog") listeners all race to handle the same
    // dialog and only the first .accept/.dismiss call wins, so we must
    // remove the default dismiss-all listener before installing this
    // counted handler.
    page.off("dialog", defaultDialogHandler);
    let dialogIdx = 0;
    const dialogHandler = (d) => {
      dialogIdx += 1;
      if (dialogIdx === 1) return d.accept().catch(() => {});
      return d.dismiss().catch(() => {});
    };
    page.on("dialog", dialogHandler);
    await page.getByRole("button", { name: /^Delete Bank A/ }).dispatchEvent("click");
    await page.waitForTimeout(500); // settle async dialog + delete + re-render
    page.off("dialog", dialogHandler);
    page.on("dialog", defaultDialogHandler);

    // Welcome list now shows only B.
    await expect(getSavedListResumeButton(page, /^Resume Bank A/)).toHaveCount(0);
    await expect(getSavedListResumeButton(page, /^Resume Bank B/)).toHaveCount(1);

    // localStorage: exactly one -data- slot remains, and it's B's.
    const remainingDataKeys = await listDataSlotKeys(page);
    expect(remainingDataKeys).toEqual([STORAGE_KEY + "-data-" + idB]);

    // B is still resumable end-to-end.
    await getSavedListResumeButton(page, /^Resume Bank B/).dispatchEvent("click");
    await page.getByRole("heading", { name: /Phase 1: Control-Level Assessment/ }).waitFor();
    const slotBAfterDelete = await readPerIdSlot(page, idB);
    expect(slotBAfterDelete.responses["1.3"]?.answer).toBe("no");
    expect(slotBAfterDelete.responses["1.4"]?.answer).toBe("yes");
    expect(slotBAfterDelete.responses["1.5"]?.answer).toBe("partial");
  });
});
