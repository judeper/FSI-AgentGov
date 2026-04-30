import { test } from "@playwright/test";
import { expect } from "./_harness.mjs";

/**
 * 04 — Hash routing (E2E regression — currently a documented gap)
 *
 * Original task scope: verify SPA uses `location.hash` for routing
 * (`#/welcome`, `#/scope`, `#/phase1`, `#/results`), back/forward,
 * deep-link with `?id=<savedId>`, etc.
 *
 * INSPECTION FINDING (assessment-app.js as of v1.4.0):
 *   - The SPA does NOT use hash routing. Navigation is driven entirely
 *     by `AssessmentApp.prototype.goToStep(step)` which mutates an
 *     in-memory `this.step` field and calls `this.render()`. There is
 *     no `hashchange`, `popstate`, `location.hash`, or `history.*` use
 *     in the file (verified by grep).
 *   - There is no deep-link parameter parsing. `?id=` query strings are
 *     ignored. The user always lands on `welcome` and must click
 *     "Start New Assessment" or "Resume <name>".
 *   - The Back button navigates the document, not the SPA: pressing
 *     Back from `/assessment/` leaves the page entirely.
 *
 * Per the No-Phantom-Coverage policy this spec is fully `test.skip`'d
 * with a code-level explanation. The test bodies still document the
 * behavioural contract we WOULD assert if hash routing landed, so the
 * skips can be flipped to active assertions in one pass when the
 * routing feature ships.
 *
 * Per-spec smoke that the SPA boots and ignores any hash fragment is
 * kept as an active `@regression` assertion below — that part is
 * verifiable today and protects against a regression where a future
 * change accidentally crashes the SPA on `#/results` deep-links.
 */

test.describe("hash routing @regression", () => {
  test("SPA boots cleanly when loaded with a hash fragment (graceful no-op) @regression", async ({
    page,
  }) => {
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    // Deep-link with a hash that — were hash routing implemented —
    // would target the Results step. With no routing, the SPA must
    // boot to the Welcome screen and ignore the fragment without
    // throwing.
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));

    await page.goto("/assessment/#/results", { waitUntil: "domcontentloaded" });

    // The Welcome-screen affordance only the SPA emits is the
    // "Start New Assessment" button (the surrounding mkdocs page has its
    // own h1 with the same name as the SPA welcome heading, so a
    // heading-based locator is ambiguous; the button is unambiguous).
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });

    // The hash is preserved (the browser kept it; the SPA did not strip it).
    expect(page.url()).toMatch(/#\/results$/);

    // No uncaught exceptions during boot.
    expect(errors, errors.join("\n")).toEqual([]);
  });

  test.skip(
    "click navigation updates location.hash (FUTURE: hash routing) @regression",
    async ({ page }) => {
      // Skipped until SPA implements hash routing. Asserted contract:
      //   await navClick(page, "Start New Assessment");
      //   expect(page.url()).toMatch(/#\/scope$/);
      //   await navClick(page, "Begin Assessment");
      //   expect(page.url()).toMatch(/#\/phase1$/);
      void page;
    },
  );

  test.skip(
    "browser Back button restores prior SPA screen (FUTURE: hash routing) @regression",
    async ({ page }) => {
      // Skipped until SPA implements hash routing. Asserted contract:
      //   ...navigate Welcome → Scoping → Phase 1
      //   await page.goBack();
      //   expect(page.url()).toMatch(/#\/scope$/);
      //   await expect(page.getByRole("heading", { name: "Assessment Scoping" })).toBeVisible();
      void page;
    },
  );

  test.skip(
    "deep-link #/phase1?id=<savedId> resumes that assessment (FUTURE: deep-link param) @regression",
    async ({ page }) => {
      // Skipped until SPA parses the `id` deep-link parameter. Today,
      // resuming a specific saved assessment requires clicking its
      // "Resume <name>" button on the welcome screen.
      void page;
    },
  );
});
