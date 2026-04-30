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
 * KNOWN DEFECTS this canary surfaces (NOT introduced by this PR):
 *   1. mkdocs-material's announce-bar wires a release-notes fetch to
 *      `https://api.github.com/repos/judeper/FSI-AgentGov/releases/latest`
 *      and `…/repos/judeper/FSI-AgentGov`. The site's CSP
 *      `connect-src 'self'` blocks both, producing two console errors
 *      per page navigation. This is a real CSP regression that should
 *      either (a) add api.github.com to connect-src + the allowlist
 *      fixture, or (b) disable the announce-bar release widget. Logged
 *      as follow-up.
 *   2. `frame-ancestors` is declared on the meta-CSP, but per spec
 *      meta-CSP cannot deliver `frame-ancestors`; Chromium emits a
 *      console warning. This directive should move to an HTTP header
 *      (Pages config) or be dropped from the meta. Logged as follow-up.
 *
 * Until those are fixed, the spec is wrapped in `test.fail` per the
 * batch caveat ("If a spec catches a real bug … use `test.fail` with
 * documentation, NOT a silent skip"). When the underlying defects land,
 * remove the `test.fail` wrapper and the canary returns to fail-loud.
 */
test.describe("zero pageerror canary @smoke", () => {
  test("happy path produces zero pageerrors / console errors @smoke", async ({
    page,
  }) => {
    // Mark as expected-to-fail until the two CSP defects above are fixed.
    test.fail(
      true,
      "Surfacing pre-existing CSP violations (api.github.com connect-src + frame-ancestors via meta). Remove when fixed.",
    );
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
