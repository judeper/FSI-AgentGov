import { test } from "@playwright/test";
import { clearPageStorage, expect } from "./_harness.mjs";

/**
 * 12 — Import malformed / hostile payload matrix (E2E regression)
 *
 * Drives the SPA's "Resume or Import Saved Assessment" entry point with a
 * series of hostile and malformed inputs and asserts:
 *
 *   1. No uncaught `pageerror` fires.
 *   2. No `console.error` fires (the SPA uses alert() for user-facing
 *      import errors; console.error during import indicates a real bug).
 *   3. The SPA stays on the welcome screen (does not white-screen, does
 *      not advance to phase1 with corrupt state).
 *
 * Inputs covered:
 *   - Empty file (0 bytes)
 *   - Truncated JSON
 *   - Valid JSON missing required fields (no assessmentId / responses)
 *   - Wrong-schema JSON
 *   - Wrong file extension (.txt with valid JSON)
 *   - >10MB JSON
 *   - __proto__ pollution payload (PR #142 defense)
 *   - frameworkVersion from a future major (see SKIP NOTE below)
 *
 * SKIP NOTE — future-frameworkVersion sub-test:
 *   The SPA's importState (assessment-app.js L1103) does NOT currently
 *   surface a version-mismatch warning for future frameworkVersion values.
 *   It either accepts the import (if the rest of the schema is valid) or
 *   alerts a generic "Invalid assessment file structure" error. Per the
 *   No-Phantom-Coverage policy and the batch caveat ("DO NOT touch
 *   assessment-app.js"), we DO NOT assert a version-mismatch banner here.
 *   Sub-test is `test.skip` with a follow-up note. If a future PR adds
 *   `_metadata.frameworkVersion` validation to importState, replace the
 *   skip with the assertion.
 */

const SPA_URL = "/assessment/";

async function gotoWelcomeFresh(page) {
  await page.goto(SPA_URL, { waitUntil: "domcontentloaded" });
  await clearPageStorage(page);
  await page.reload({ waitUntil: "domcontentloaded" });
  await page
    .getByRole("button", { name: "Start New Assessment" })
    .waitFor({ timeout: 15_000 });
}

/**
 * Drive the import flow with a synthetic file payload. The SPA's
 * triggerImport (assessment-app.js L1957) creates a hidden <input
 * type="file"> and calls .click(); Playwright surfaces this as a
 * filechooser event we satisfy with setFiles(buffer).
 *
 * Returns { pageErrors, consoleErrors, dialogs } observed during the
 * import attempt. The caller asserts on these.
 */
async function attemptImport(page, { name, mimeType, buffer }) {
  const pageErrors = [];
  const consoleErrors = [];
  const dialogs = [];
  const onPageError = (e) => pageErrors.push(String(e.message || e));
  const onConsole = (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  };
  const onDialog = (d) => {
    dialogs.push({ type: d.type(), message: d.message() });
    d.dismiss().catch(() => {});
  };
  page.on("pageerror", onPageError);
  page.on("console", onConsole);
  page.on("dialog", onDialog);

  try {
    const chooserPromise = page.waitForEvent("filechooser");
    await page
      .getByRole("button", { name: "Resume or Import Saved Assessment" })
      .dispatchEvent("click");
    const chooser = await chooserPromise;
    await chooser.setFiles({ name, mimeType, buffer });
    // Give the SPA time to read + dispatch alert/render.
    await page.waitForTimeout(300);
  } finally {
    page.off("pageerror", onPageError);
    page.off("console", onConsole);
    page.off("dialog", onDialog);
  }
  return { pageErrors, consoleErrors, dialogs };
}

async function expectStillOnWelcome(page) {
  await expect(
    page.getByRole("button", { name: "Start New Assessment" }),
  ).toBeVisible();
}

test.describe("import malformed @regression", () => {
  test("empty file → no crash, no advance @regression", async ({ page }) => {
    await gotoWelcomeFresh(page);
    const { pageErrors, consoleErrors } = await attemptImport(page, {
      name: "empty.json",
      mimeType: "application/json",
      buffer: Buffer.from(""),
    });
    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
    await expectStillOnWelcome(page);
  });

  test("truncated JSON → no crash @regression", async ({ page }) => {
    await gotoWelcomeFresh(page);
    const { pageErrors, consoleErrors } = await attemptImport(page, {
      name: "truncated.json",
      mimeType: "application/json",
      buffer: Buffer.from('{"scoping":'),
    });
    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
    await expectStillOnWelcome(page);
  });

  test("valid JSON missing required fields → no crash @regression", async ({
    page,
  }) => {
    await gotoWelcomeFresh(page);
    const { pageErrors, consoleErrors } = await attemptImport(page, {
      name: "missing-fields.json",
      mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify({ scoping: {} })),
    });
    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
    await expectStillOnWelcome(page);
  });

  test("wrong-schema JSON → no crash @regression", async ({ page }) => {
    await gotoWelcomeFresh(page);
    const { pageErrors, consoleErrors } = await attemptImport(page, {
      name: "wrong.json",
      mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify({ foo: "bar", baz: [1, 2, 3] })),
    });
    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
    await expectStillOnWelcome(page);
  });

  test("wrong extension (.txt with valid JSON) → no crash @regression", async ({
    page,
  }) => {
    await gotoWelcomeFresh(page);
    // The SPA's <input> sets accept=".json" but browsers do not enforce
    // that; setFiles bypasses the chooser filter regardless.
    const { pageErrors, consoleErrors } = await attemptImport(page, {
      name: "renamed.txt",
      mimeType: "text/plain",
      buffer: Buffer.from(JSON.stringify({ foo: "bar" })),
    });
    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
    await expectStillOnWelcome(page);
  });

  test("oversized (>10MB) JSON → no crash, no silent freeze @regression @slow", async ({
    page,
  }) => {
    await gotoWelcomeFresh(page);
    // Build an >10MB JSON payload inline. Use a single oversized notes
    // string so the file is parseable but overweight.
    const big = "x".repeat(11 * 1024 * 1024);
    const buffer = Buffer.from(JSON.stringify({ scoping: { note: big } }));
    expect(buffer.length).toBeGreaterThan(10 * 1024 * 1024);
    const { pageErrors, consoleErrors } = await attemptImport(page, {
      name: "huge.json",
      mimeType: "application/json",
      buffer,
    });
    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
    await expectStillOnWelcome(page);
  });

  test("__proto__ pollution payload (PR #142) → rejected, no global pollution @regression", async ({
    page,
  }) => {
    await gotoWelcomeFresh(page);
    // Use a JSON literal with the string key "__proto__" — JSON.parse
    // preserves it as an own property (unlike a JS object literal).
    const pollute = '{"assessmentId":"x","scoping":{},"responses":{},"__proto__":{"polluted":true}}';
    const { pageErrors, consoleErrors } = await attemptImport(page, {
      name: "proto.json",
      mimeType: "application/json",
      buffer: Buffer.from(pollute),
    });
    expect(pageErrors).toEqual([]);
    expect(consoleErrors).toEqual([]);
    await expectStillOnWelcome(page);
    // Verify Object prototype was not mutated.
    const polluted = await page.evaluate(() => ({}).polluted === true);
    expect(polluted).toBe(false);
  });

  // SKIP — see header SKIP NOTE. The SPA does not currently emit a
  // version-mismatch warning for future frameworkVersion values; it
  // either rejects on schema (alert) or accepts silently. Asserting a
  // banner that does not exist would be phantom coverage. Re-enable this
  // sub-test when SPA gains version-mismatch handling.
  test.skip("future frameworkVersion shows version-mismatch warning @regression", async () => {
    // Intentionally empty — see header SKIP NOTE.
  });
});
