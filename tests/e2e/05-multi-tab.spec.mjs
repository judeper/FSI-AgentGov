import { test } from "@playwright/test";
import { clearPageStorage, expect } from "./_harness.mjs";

/**
 * 05 — Multi-tab durability (E2E regression)
 *
 * Two tabs of the SAME browser context (= same localStorage origin)
 * concurrently editing different saved assessments. This mirrors the
 * actual user scenario: a consultant with Bank A open in tab 1 and
 * Bank B open in tab 2 of the same Chrome window.
 *
 * NOTE: Playwright's `browser.newContext()` returns a context with its
 * own isolated localStorage. To share localStorage across pages — which
 * is the realistic SPA scenario — we use the SAME context with two
 * `context.newPage()` pages. A separate cross-context spec would have
 * value (it would verify NO leakage across browser profiles), but the
 * shared-storage variant is the higher-signal regression target and is
 * what this spec exercises.
 *
 * Asserted contracts:
 *  - Both assessments persist in localStorage after concurrent edits.
 *  - A third fresh page in the same context sees both Resume buttons.
 *  - Deleting tab A's assessment does not corrupt tab B's slot.
 *
 * SPA literal STORAGE_KEY value (docs/javascripts/assessment-app.js L16):
 *   "fsi-agentgov-assessment"
 */

const STORAGE_KEY = "fsi-agentgov-assessment";

async function startNewAndScope(page, organizationName) {
  await page
    .getByRole("button", { name: "Start New Assessment" })
    .dispatchEvent("click");
  await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();
  await page.getByLabel("Organization Name").fill(organizationName);
  await page.getByLabel("Assessor Name").fill("Multi-Tab Tester");
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

async function findIdForOrg(page, orgName) {
  // Walk every per-id slot in the SHARED localStorage and return the
  // id whose state.scoping.organizationName matches. This is robust
  // across the multi-tab scenario because each tab has its own slot,
  // and the shared `-current` blob is overwritten unpredictably by
  // whichever tab saved last (so we cannot use `-current` to identify
  // a specific tab's assessment).
  return await page.evaluate(
    ([k, org]) => {
      const prefix = k + "-data-";
      for (const key of Object.keys(localStorage)) {
        if (!key.startsWith(prefix)) continue;
        try {
          const parsed = JSON.parse(localStorage.getItem(key));
          if (parsed && parsed.scoping
              && parsed.scoping.organizationName === org) {
            return key.substring(prefix.length);
          }
        } catch (_) { /* ignore corrupt slots */ }
      }
      return null;
    },
    [STORAGE_KEY, orgName],
  );
}

async function listDataSlotKeys(page) {
  return await page.evaluate(() =>
    Object.keys(localStorage).filter((k) => k.includes("-data-")),
  );
}

test.describe("multi-tab same-context durability @regression", () => {
  test("two tabs editing different assessments do not corrupt each other @regression", async ({
    context,
  }) => {
    const dialogDismiss = (d) => d.dismiss().catch(() => {});

    // Tab A.
    const pageA = await context.newPage();
    pageA.on("dialog", dialogDismiss);
    await pageA.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(pageA);
    await pageA.reload({ waitUntil: "domcontentloaded" });
    await startNewAndScope(pageA, "Bank A Multi");
    await answerControl(pageA, "1.1", "Yes");
    await answerControl(pageA, "1.2", "Partial");
    await pageA.waitForTimeout(700); // debounced save flush
    const idA = await findIdForOrg(pageA, "Bank A Multi");
    expect(idA, "Tab A assessment id").toBeTruthy();

    // Tab B in the SAME context (shared localStorage). Opening Tab B
    // re-triggers the SPA boot, which calls `loadFromStorage` →
    // welcome list. Tab B then starts a NEW assessment which becomes
    // the new "current". This race — both tabs writing distinct slots
    // through the 500ms debounced saver — is the exact concern this
    // spec guards.
    const pageB = await context.newPage();
    pageB.on("dialog", dialogDismiss);
    await pageB.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await pageB
      .locator("#assessment-app")
      .getByRole("heading", { name: "Governance Readiness Assessment" })
      .waitFor({ timeout: 15_000 });
    await startNewAndScope(pageB, "Bank B Multi");

    // Concurrent edits: fire in parallel so the debounced save windows
    // overlap.
    await Promise.all([
      answerControl(pageA, "1.3", "No"),
      answerControl(pageB, "1.4", "Yes"),
    ]);
    await Promise.all([
      answerControl(pageA, "1.5", "Yes"),
      answerControl(pageB, "1.5", "Partial"),
    ]);

    // Wait for both debounced saves to flush.
    await pageA.waitForTimeout(700);
    await pageB.waitForTimeout(700);

    const idB = await findIdForOrg(pageB, "Bank B Multi");
    expect(idB, "Tab B assessment id").toBeTruthy();
    expect(idB).not.toBe(idA);

    // localStorage now contains both per-id slots.
    const keysFromB = await listDataSlotKeys(pageB);
    expect(keysFromB).toEqual(
      expect.arrayContaining([
        STORAGE_KEY + "-data-" + idA,
        STORAGE_KEY + "-data-" + idB,
      ]),
    );

    // Third fresh page in the same context — proves both assessments
    // are visible on welcome list, no corruption, no cross-pollution.
    const pageC = await context.newPage();
    pageC.on("dialog", dialogDismiss);
    await pageC.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await pageC
      .locator("#assessment-app")
      .getByRole("heading", { name: "Governance Readiness Assessment" })
      .waitFor({ timeout: 15_000 });
    await expect(
      pageC.getByRole("button", { name: /^Resume Bank A Multi/ }),
    ).toHaveCount(1);
    await expect(
      pageC.getByRole("button", { name: /^Resume Bank B Multi/ }),
    ).toHaveCount(1);

    // Slot integrity: A has 1.1/1.2/1.3/1.5, B has 1.4/1.5, no leakage.
    const slotA = await pageC.evaluate(
      ([k, id]) => JSON.parse(localStorage.getItem(k + "-data-" + id)),
      [STORAGE_KEY, idA],
    );
    const slotB = await pageC.evaluate(
      ([k, id]) => JSON.parse(localStorage.getItem(k + "-data-" + id)),
      [STORAGE_KEY, idB],
    );
    expect(slotA.scoping.organizationName).toBe("Bank A Multi");
    expect(slotA.responses["1.1"].answer).toBe("yes");
    expect(slotA.responses["1.5"].answer).toBe("yes");
    expect(slotA.responses["1.4"]).toBeUndefined();
    expect(slotB.scoping.organizationName).toBe("Bank B Multi");
    expect(slotB.responses["1.4"].answer).toBe("yes");
    expect(slotB.responses["1.5"].answer).toBe("partial");
    expect(slotB.responses["1.1"]).toBeUndefined();

    // Tab A deletes its assessment. Tab B's slot must remain intact.
    // The Welcome Delete flow triggers two confirms (delete? + export?).
    pageC.removeAllListeners("dialog");
    let dialogIdx = 0;
    pageC.on("dialog", (d) => {
      dialogIdx += 1;
      if (dialogIdx === 1) return d.accept().catch(() => {});
      return d.dismiss().catch(() => {});
    });
    await pageC
      .getByRole("button", { name: /^Delete Bank A Multi/ })
      .dispatchEvent("click");
    await pageC.waitForTimeout(500);

    // Tab B's slot survives.
    const slotBAfterDelete = await pageC.evaluate(
      ([k, id]) => {
        const raw = localStorage.getItem(k + "-data-" + id);
        return raw ? JSON.parse(raw) : null;
      },
      [STORAGE_KEY, idB],
    );
    expect(slotBAfterDelete, "Tab B slot must survive Tab A's delete").not.toBeNull();
    expect(slotBAfterDelete.responses["1.4"].answer).toBe("yes");
    expect(slotBAfterDelete.responses["1.5"].answer).toBe("partial");

    await pageA.close();
    await pageB.close();
    await pageC.close();
  });
});
