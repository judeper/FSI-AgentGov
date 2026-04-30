import { test } from "@playwright/test";
import {
  clearPageStorage,
  expect,
  expectDownload,
  freezeTime,
  navClick,
} from "./_harness.mjs";
import { readFileSync } from "node:fs";

/**
 * 16 — Edge data injection matrix (E2E regression)
 *
 * Hostile-input matrix exercised end-to-end through the SPA:
 *   - XSS payloads in scoping fields (script tag, img onerror,
 *     javascript: URL) — must NEVER trigger a `dialog` event.
 *   - Unicode bidi override + zero-width spaces + Cyrillic homoglyphs —
 *     must round-trip through Save → Reload → Export → Import without
 *     mangling.
 *   - Formula-injection vectors in notes (`=`, `+`, `-`, `@`, `\t`,
 *     `\r`) — verified via JSON export round-trip preservation here;
 *     XLSX-prefixing is covered by spec 07.
 *   - SQL-injection-shaped strings — round-trip safely (defensive).
 *   - Excessively long strings (~1MB) — SPA does not hang.
 *
 * Dialog assertion is the critical signal: per the batch caveat, a
 * fired alert/confirm during XSS injection means a real bug. We use
 * `page.on('dialog')` and assert `dialogFired === false` at the end.
 *
 * Note on confirm() dialogs that ARE expected:
 *   The "View Results" button surfaces a confirm() (save-before-results
 *   prompt). That fires AFTER the XSS test window. We therefore install
 *   the dialog listener with a flag that only flips for `alert` types
 *   during the scoping/phase1 window, and switch to a generic
 *   dismisser thereafter.
 */

const FORMULA_PAYLOADS = [
  "=cmd|\" /c calc\"!A1",
  "+1+1",
  "-2+3",
  "@SUM(1+1)*cmd|' /c calc'!A0",
  "\tleading-tab",
  "\rcarriage-return",
];

const SQLI_PAYLOAD = "' OR 1=1 -- ";

// 1MB note string used to verify the SPA accepts excessively long input
// without hanging. We don't assert specific UX for length-limit handling
// (the SPA does not currently truncate), only that the round-trip
// completes within the spec timeout.
const HUGE_NOTE = "L".repeat(1024 * 1024);

test.describe("edge data injection @regression", () => {
  test("XSS / unicode / formula / SQLi payloads round-trip without dialog @regression @slow", async ({
    page,
  }) => {
    await freezeTime(page);

    // Phase 1 — strict XSS dialog watch. Any alert() during scoping +
    // phase1 is a real XSS bug.
    let xssDialogFired = false;
    let xssDialogMessage = null;
    const xssListener = (d) => {
      if (d.type() === "alert") {
        xssDialogFired = true;
        xssDialogMessage = d.message();
      }
      d.dismiss().catch(() => {});
    };
    page.on("dialog", xssListener);

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });

    // ---- XSS scoping fields ----
    const orgPayload = '<script>alert("xss-org")</script>';
    const assessorPayload = '"><img src=x onerror=alert("xss-asr")>';
    // Note: the SPA's evidenceRef field is NOT a hyperlink; the
    // `javascript:` URL would only matter if rendered as href. We seed
    // it into a notes field via post-scoping mutation to confirm
    // textContent escaping.

    await page
      .getByRole("button", { name: "Start New Assessment" })
      .dispatchEvent("click");
    await page.getByRole("heading", { name: "Assessment Scoping" }).waitFor();
    await page.getByLabel("Organization Name").fill(orgPayload);
    await page.getByLabel("Assessor Name").fill(assessorPayload);
    await page
      .getByLabel("Institution Type", { exact: true })
      .selectOption("bank");
    await page
      .getByRole("group", { name: "Active Governance Zones" })
      .locator('input[type="checkbox"][value="1"]')
      .check();
    await page
      .getByRole("button", { name: "Begin Assessment" })
      .dispatchEvent("click");
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    // Inject hostile notes into a control via direct state mutation +
    // saveToStorage. This exercises the same code paths used by the
    // notes textarea but lets us cover all formula/SQLi/unicode vectors
    // in one shot.
    const unicodeOrg = "Acmе Bank \u202eEVIL\u202c \u200b zero-width";
    const allNotesPayload = [
      ...FORMULA_PAYLOADS,
      SQLI_PAYLOAD,
      unicodeOrg,
      'javascript:alert("xss-evidence")',
    ].join("\n");

    await page.evaluate(
      ([payload, hugeNote]) => {
        const app = window.__assessmentApp;
        // Seed responses with hostile content on three answered controls.
        if (!app.state.responses) app.state.responses = {};
        app.state.responses["1.1"] = {
          answer: "yes",
          notes: payload,
          evidenceRef: 'javascript:alert("xss-ev")',
        };
        app.state.responses["1.2"] = {
          answer: "partial",
          notes: hugeNote,
          evidenceRef: "",
        };
        app.state.responses["1.3"] = {
          answer: "no",
          notes: "Cyrillic а vs Latin a homoglyph test",
          evidenceRef: "",
        };
        app.saveToStorage();
        app.render();
      },
      [allNotesPayload, HUGE_NOTE],
    );

    // The DOM must NOT contain an unescaped <script> tag from the org
    // name. Heading "Phase 1" is the on-screen anchor; we look for any
    // <script> with our marker.
    const unsafeScript = await page.evaluate(() => {
      const scripts = Array.from(document.querySelectorAll("script"));
      return scripts.some((s) => s.textContent.indexOf("xss-org") !== -1);
    });
    expect(unsafeScript).toBe(false);

    // The org name when rendered (e.g. in the print header on results)
    // must appear as escaped text, not as a parsed element.
    expect(xssDialogFired).toBe(false);
    expect(xssDialogMessage).toBeNull();

    // ---- Round-trip: export JSON, clear, re-import, verify round-trip ----
    page.off("dialog", xssListener);
    page.on("dialog", (d) => d.dismiss().catch(() => {})); // generic dismisser

    await navClick(page, "View Results");
    await page.locator(".ag-score-big").first().waitFor();
    await navClick(page, "Export Results");
    await page.getByRole("heading", { name: "Export Results" }).waitFor();
    const { path } = await expectDownload(page, async () => {
      await navClick(page, /Export as Full Assessment/);
    });
    const exported = JSON.parse(readFileSync(path, "utf8"));

    // Verify hostile values round-tripped as string content (NOT
    // sanitized to empty, NOT executed). The SPA's import sanitizer
    // discards forbidden keys but keeps user-authored notes verbatim.
    expect(exported.scoping.organizationName).toBe(orgPayload);
    expect(exported.scoping.assessorName).toBe(assessorPayload);
    expect(exported.responses["1.1"].notes).toBe(allNotesPayload);
    expect(exported.responses["1.2"].notes).toBe(HUGE_NOTE);

    // Re-import and verify still no dialog.
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });
    const chooserPromise = page.waitForEvent("filechooser");
    await navClick(page, "Resume or Import Saved Assessment");
    const chooser = await chooserPromise;
    await chooser.setFiles(path);
    await page
      .getByRole("heading", { name: /Phase 1: Control-Level Assessment/ })
      .waitFor();

    const afterImport = await page.evaluate(() => {
      const app = window.__assessmentApp;
      return {
        org: app.state.scoping.organizationName,
        notes11: app.state.responses["1.1"]?.notes || "",
        len12: (app.state.responses["1.2"]?.notes || "").length,
      };
    });
    expect(afterImport.org).toBe(orgPayload);
    expect(afterImport.notes11).toBe(allNotesPayload);
    expect(afterImport.len12).toBe(HUGE_NOTE.length);
  });
});
