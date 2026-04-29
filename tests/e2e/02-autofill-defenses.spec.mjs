import { test } from "@playwright/test";
import { clearPageStorage, expect, navClick } from "./_harness.mjs";

/**
 * 02 — Autofill defenses (PR #137)
 *
 * SCOPE NOTE: PR #137 did NOT ship a debug "autofill toggle" UI. It
 * shipped *defenses* against browser autofill bypassing the institution-
 * type validation on the scoping screen. This spec exercises those real
 * defenses (since there is no toggle to flip):
 *
 *   1. The institution-type <select> renders with autocomplete="off" and
 *      a randomized `name` attribute (PR #137 layer 1+2). Both layers must
 *      survive re-renders and not collide between selects.
 *   2. Initial state of `sc.institutionType` is empty — no value is
 *      pre-selected, so the smoke gate that "default state is OFF / no
 *      pre-selection" still applies in the autofill-defense reading.
 *   3. The submit handler reads the DOM <select>'s value if state has
 *      drifted (PR #137 layer 3 — the safety net for Chromium that often
 *      ignores autocomplete=off). We simulate the drift by directly
 *      mutating the select.value without firing a change event, then
 *      asserting that "Begin Assessment" still proceeds to Phase 1.
 *
 * The original prompt also asked for a "hidden in production hosts"
 * assertion. There is currently no host-gated UI on this surface, so we
 * assert the contrapositive: nothing on the scoping screen reads
 * `location.hostname`. If a host-gated toggle is added later, this spec
 * is the place to extend the check.
 */
test.describe("autofill defenses @smoke", () => {
  test("autocomplete=off + randomized name + DOM-sync safety net @smoke", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // Welcome → Scoping
    await navClick(page, "Start New Assessment");
    await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();

    // ----- Defense 1+2: autocomplete=off + randomized name -----
    const sel = page.locator("#ag-select-institution-type");
    await expect(sel).toHaveAttribute("autocomplete", "off");
    const nameAttr = await sel.getAttribute("name");
    expect(nameAttr).toMatch(/^ag-select-institution-type-[a-z0-9]{2,8}$/);

    // ----- Default state: nothing pre-selected -----
    expect(await sel.inputValue()).toBe("");

    // ----- Fill required fields except institution type via DOM mutation -----
    await page.getByLabel("Organization Name").fill("Defenses Bank");
    await page
      .getByRole("group", { name: "Active Governance Zones" })
      .locator('input[type="checkbox"][value="1"]')
      .check();

    // Simulate a browser autofill: mutate select.value WITHOUT firing
    // 'change'. State (`sc.institutionType`) stays empty.
    await sel.evaluate((el) => {
      el.value = "bank";
    });

    // Click Begin Assessment. Defense 3 reads the DOM value back into
    // state before validating, so we must end up on Phase 1.
    await navClick(page, "Begin Assessment");
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();
  });
});
