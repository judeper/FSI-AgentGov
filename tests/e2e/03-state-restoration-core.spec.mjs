import { test } from "@playwright/test";
import {
  clearPageStorage,
  expect,
  navClick,
} from "./_harness.mjs";

/**
 * 03 — State restoration core (E2E regression)
 *
 * Different angle from 03b/c/d:
 *  - 03b proves multi-assessment per-id slot durability.
 *  - 03c proves resume-step restores wizard step.
 *  - 03d proves filter state isolation across assessments.
 *
 * 03 is a single-assessment **byte-diff** restoration check: we save a
 * partially-completed Phase 1 (scoping done, 4 answers, 1 with notes,
 * 1 with evidence URL), then reload the SPA cold and assert the
 * post-reload `STORAGE_KEY+"-data-<id>"` slot is byte-for-byte identical
 * to the pre-reload slot (modulo a single allowed `updatedAt` skew, since
 * the SPA may bump that field on resume — we explicitly check both
 * possibilities and assert NO other field differs).
 *
 * SPA literal STORAGE_KEY value (docs/javascripts/assessment-app.js L16):
 *   "fsi-agentgov-assessment"
 */

const STORAGE_KEY = "fsi-agentgov-assessment";

async function readSlotJson(page, id) {
  return await page.evaluate(
    ([k, theId]) => localStorage.getItem(k + "-data-" + theId),
    [STORAGE_KEY, id],
  );
}

async function readCurrentId(page) {
  return await page.evaluate((k) => {
    const raw = localStorage.getItem(k + "-current");
    if (!raw) return null;
    try { return JSON.parse(raw).assessmentId || null; } catch { return null; }
  }, STORAGE_KEY);
}

async function answerControl(page, controlId, label) {
  const card = page.locator(`[data-control-id="${controlId}"]`);
  await card.first().waitFor({ state: "attached" });
  const pillar = card.locator(
    'xpath=ancestor::div[contains(@class,"ag-pillar-controls")]',
  );
  if ((await pillar.count()) > 0) {
    const collapsed = await pillar
      .first()
      .evaluate((el) => el.classList.contains("collapsed"));
    if (collapsed) {
      const header = pillar.locator(
        'xpath=preceding-sibling::div[contains(@class,"ag-pillar-header")][1]',
      );
      if ((await header.count()) > 0) await header.first().click();
    }
  }
  await card.getByRole("button", { name: label, exact: true }).click();
}

test.describe("state restoration core @regression", () => {
  test("partial Phase 1 (answers + notes + evidence) survives reload byte-for-byte @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // Welcome → scoping (manual to keep this spec self-contained).
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .dispatchEvent("click");
    await page
      .getByRole("heading", { name: "Assessment Scoping" })
      .waitFor();
    await page.getByLabel("Organization Name").fill("Restoration Bank");
    await page.getByLabel("Assessor Name").fill("Restore Tester");
    await page
      .getByLabel("Institution Type", { exact: true })
      .selectOption("bank");
    const zoneFieldset = page.getByRole("group", {
      name: "Active Governance Zones",
    });
    const zone1 = zoneFieldset.locator('input[type="checkbox"][value="1"]');
    if (!(await zone1.isChecked())) await zone1.check();
    await page
      .getByRole("button", { name: "Begin Assessment" })
      .dispatchEvent("click");
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    // 4 answers covering yes/partial/no/na.
    await answerControl(page, "1.1", "Yes");
    await answerControl(page, "1.2", "Partial");
    await answerControl(page, "1.3", "No");
    await answerControl(page, "1.4", "N/A");

    // Notes on 1.1.
    const noteText = "Encryption baseline reviewed by CISO 2025-Q4.";
    const notes = page.locator("#ag-notes-1\\.1");
    await notes.fill(noteText);

    // Evidence URL on 1.2.
    const evidenceUrl = "https://example.com/evidence/1.2/audit-log.pdf";
    const evidence = page.locator("#ag-evref-1\\.2");
    await evidence.fill(evidenceUrl);

    // Wait > 500ms for the debounced saveToStorage flush.
    await page.waitForTimeout(700);

    const id = await readCurrentId(page);
    expect(id, "assessmentId must exist after partial save").toBeTruthy();

    // Capture pre-reload slot (raw string for byte diff).
    const before = await readSlotJson(page, id);
    expect(before, "pre-reload slot must exist").toBeTruthy();
    const beforeParsed = JSON.parse(before);
    // Sanity: state contents we expect.
    expect(beforeParsed.scoping.organizationName).toBe("Restoration Bank");
    expect(beforeParsed.scoping.assessorName).toBe("Restore Tester");
    expect(beforeParsed.responses["1.1"].answer).toBe("yes");
    expect(beforeParsed.responses["1.1"].notes).toBe(noteText);
    expect(beforeParsed.responses["1.2"].answer).toBe("partial");
    expect(beforeParsed.responses["1.2"].evidenceRef).toBe(evidenceUrl);
    expect(beforeParsed.responses["1.3"].answer).toBe("no");
    expect(beforeParsed.responses["1.4"].answer).toBe("na");

    // Cold reload.
    await page.reload({ waitUntil: "domcontentloaded" });
    await page
      .locator("#assessment-app")
      .getByRole("heading", { name: "Governance Readiness Assessment" })
      .waitFor({ timeout: 15_000 });

    // Resume — restoration of in-memory state goes through the same
    // import code path; the slot itself must already be intact pre-resume.
    const afterPreResume = await readSlotJson(page, id);
    expect(afterPreResume, "slot must persist across reload").toBeTruthy();

    // Byte-diff: every field except `updatedAt` MUST be identical. The SPA
    // does not bump updatedAt on a passive reload (no save fires), so in
    // practice the entire string is identical, but we guard against an
    // updatedAt-only delta to keep the assertion robust to a future
    // boot-time touch.
    const beforeForDiff = { ...beforeParsed };
    const afterForDiff = JSON.parse(afterPreResume);
    delete beforeForDiff.updatedAt;
    delete afterForDiff.updatedAt;
    expect(JSON.stringify(afterForDiff)).toBe(JSON.stringify(beforeForDiff));

    // Resume the assessment and re-verify field-level restoration via the
    // live UI (defends against a future bug where the slot is intact but
    // the in-memory hydration drops fields).
    await page
      .getByRole("button", { name: /^Resume Restoration Bank/ })
      .dispatchEvent("click");
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    // Notes / evidence textarea + input retain their values.
    await expect(page.locator("#ag-notes-1\\.1")).toHaveValue(noteText);
    await expect(page.locator("#ag-evref-1\\.2")).toHaveValue(evidenceUrl);

    // The Yes/Partial/No/N/A buttons surface the active state via
    // `aria-pressed="true"` (rendered by renderControlCard). Verify each.
    const expected = {
      "1.1": "Yes",
      "1.2": "Partial",
      "1.3": "No",
      "1.4": "N/A",
    };
    for (const [cid, label] of Object.entries(expected)) {
      const btn = page
        .locator(`[data-control-id="${cid}"]`)
        .getByRole("button", { name: label, exact: true });
      await expect(btn).toHaveAttribute("aria-pressed", "true");
    }
  });
});
