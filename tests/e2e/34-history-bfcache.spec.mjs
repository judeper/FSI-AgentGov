/**
 * 34 — Browser history / BFCache regression suite
 *
 * Attack model: Two distinct events fire on back-navigation:
 *   1. popstate — fires when pushState history entry changes (Material instant-nav).
 *   2. pageshow(persisted=true) — BFCache restore, bypasses JS re-execution.
 *
 * navigation.instant (mkdocs.yml line 28) means users trigger these events on
 * every back-press. If Mermaid re-init only hooks DOMContentLoaded / pushState,
 * popstate / BFCache restores leave raw <pre class="mermaid"> blocks — same
 * symptom as F-NAVINSTANT-MERMAID-REINIT (spec 31 T3) but different event path.
 *
 * The assessment SPA uses in-memory goToStep() and never calls pushState
 * (confirmed by spec 04 inspection), so browser back does NOT navigate within
 * SPA screens. A customer pressing back from results expects phase1 with
 * answers intact — the SPA cannot fulfil this. (F-SPA-BACK-NO-ROUTING)
 *
 * Tests:
 *   1 @regression — Docs back: .mermaid svg > 0 after goBack()
 *   2 @regression — Docs BFCache: .mermaid svg > 0 after pageshow persisted
 *                   (soft-warn if BFCache does not fire — Chromium/localhost limitation)
 *   3 @regression — SPA back×2 mid-assessment: Phase 1 + answers + scope intact
 *   4 @smoke      — SPA back×2 + forward×2: results re-render with same score
 *
 * Expected failures on current main (pre-fix):
 *   T1 — svg count = 0 after goBack() — popstate path not covered
 *   T2 — svg count = 0 if BFCache fires — same root cause
 *   T3 — goBack() exits /assessment/ (white-screen); Phase 1 heading not found
 *   T4 — goForward() re-lands on welcome screen, not results
 */

import { test } from "@playwright/test";
import {
  clearPageStorage,
  clickThroughPhase1,
  expect,
  loadPersona,
  navClick,
  seedScoping,
} from "./_harness.mjs";

// ── Runtime config ──────────────────────────────────────────────────────────
const PORT = parseInt(process.env.PW_PORT || "8765", 10);
const DOCS_BASE = `http://127.0.0.1:${PORT}`;

// ── Docs pages with known Mermaid content ────────────────────────────────────
// agent-lifecycle: confirmed Mermaid-bearing (spec 31 oracle; render-expectations.json).
// agent-identity-architecture: second framework page with Mermaid blocks.
const PAGE_A = `${DOCS_BASE}/framework/agent-lifecycle/`;
const PAGE_B = `${DOCS_BASE}/framework/agent-identity-architecture/`;
const FRAMEWORK_INDEX = `${DOCS_BASE}/framework/`;

// ── Mini persona for SPA tests (only yes/partial/no — avoids unknown → throw) ──
const MINI_PERSONA = {
  scoping: {
    organizationName: "Acme Bank",
    assessorName: "Test Runner",
    institutionType: "bank",
    zones: [2],
  },
  answers: {
    "1.1": "yes",
    "1.2": "partial",
    "1.3": "no",
    "1.4": "yes",
    "1.5": "partial",
  },
};

// ── Storage key documented here for Phase 3 reference ───────────────────────
// "fsi-agentgov-assessment" — slots: -current, -data-<id>  (assessment-app.js L16)

// ── Helpers ──────────────────────────────────────────────────────────────────

/** Assert Mermaid processed: SVGs present, no raw <pre> blocks remain. */
async function assertMermaidRendered(page, context) {
  const svgCount = await page.locator(".mermaid svg").count();
  expect(
    svgCount,
    `[${context}] .mermaid svg count ${svgCount}; expected > 0 — Mermaid did not re-init`,
  ).toBeGreaterThan(0);
  const preCount = await page.locator("pre.mermaid").count();
  expect(
    preCount,
    `[${context}] ${preCount} raw <pre class="mermaid"> blocks remain — Mermaid JS never fired`,
  ).toBe(0);
}

// ── Override baseURL to docs root for Tests 1 and 2 ─────────────────────────

// =============================================================================
test.describe("history + BFCache @regression", () => {
  // ===========================================================================
  // Test 1 — Docs back-navigation preserves Mermaid render
  // ===========================================================================
  test(
    "docs back-navigation preserves Mermaid render @regression",
    async ({ page }) => {
      test.setTimeout(60_000);
      const pageErrors = [];
      page.on("pageerror", (e) => pageErrors.push(e.message));

      // (a) Navigate to PAGE_A. Do not pre-assert SVGs: Mermaid CDN blockage
      //     (F-MERMAID-CDN-BLOCK, spec 31 T1) makes that always-fail on main.
      //     This test specifically covers the POPSTATE re-init path, not initial load.
      await page.goto(PAGE_A, { waitUntil: "domcontentloaded" });
      const originPath = new URL(page.url()).pathname;

      // (b) Navigate to PAGE_B — creates a back-stack entry for PAGE_A.
      await page.goto(PAGE_B, { waitUntil: "domcontentloaded" });
      const errsBefore = pageErrors.length;

      // (c) Press back — exercises the popstate event path.
      //     Distinct from instant-nav's pushState path covered by spec 31 T3.
      await page.goBack({ waitUntil: "load", timeout: 15_000 });

      // (d) Assert URL restored to PAGE_A.
      expect(new URL(page.url()).pathname, "goBack() must restore PAGE_A").toBe(originPath);

      // (e) Mermaid must re-init on popstate. [F-NAVINSTANT-MERMAID-REINIT-POPSTATE]
      //     On current main: svg count = 0 (Mermaid not re-initing on popstate path).
      await expect
        .poll(() => page.locator(".mermaid svg").count(), { timeout: 5_000 })
        .toBeGreaterThan(0);
      await assertMermaidRendered(page, "back-navigation");

      // (f) No new pageerrors from the back navigation.
      const newErrors = pageErrors.slice(errsBefore);
      expect(newErrors, `goBack() triggered pageerror(s): ${newErrors.join("; ")}`).toEqual([]);
    },
  );

  // ===========================================================================
  // Test 2 — Docs BFCache restore preserves Mermaid render
  // ===========================================================================
  test(
    "docs BFCache restore preserves Mermaid render @regression",
    async ({ page }) => {
      test.setTimeout(60_000);

      // (a) Navigate to PAGE_A. No initial SVG pre-assertion — F-MERMAID-CDN-BLOCK
      //     (spec 31 T1) makes that always-fail on main. This test covers the
      //     BFCache pageshow-persisted re-init path specifically.
      await page.goto(PAGE_A, { waitUntil: "domcontentloaded" });

      // (b) Plant pageshow listener BEFORE navigating away.
      //     It survives BFCache freeze/restore of the page JS context.
      await page.evaluate(() => {
        window.__bfcacheFired = false;
        window.addEventListener("pageshow", (e) => {
          if (e.persisted) window.__bfcacheFired = true;
        });
      });

      // (c) Navigate away to framework index — triggers BFCache eligibility check.
      await page.goto(FRAMEWORK_INDEX, { waitUntil: "domcontentloaded" });

      // (d) Press back — may restore PAGE_A from BFCache (pageshow persisted=true).
      await page.goBack({ waitUntil: "load", timeout: 15_000 });

      // (e) Check whether BFCache actually fired.
      const bfcacheFired = await page
        .evaluate(() => window.__bfcacheFired ?? false)
        .catch(() => false);

      if (!bfcacheFired) {
        // Soft-warn: BFCache may not activate on Python http.server localhost.
        console.warn(
          "[34-T2] BFCache did not fire — Chromium/localhost may suppress it. " +
            "Asserting Mermaid render on fresh-load path instead.",
        );
      }

      // (f) Mermaid must render — whether BFCache or fresh-load.
      //     [F-NAVINSTANT-MERMAID-REINIT-BFCACHE] on main: svg count = 0.
      await expect
        .poll(() => page.locator(".mermaid svg").count(), { timeout: 5_000 })
        .toBeGreaterThan(0);
      await assertMermaidRendered(page, "BFCache-restore");
    },
  );

  // ===========================================================================
  // Test 3 — SPA back-button mid-assessment preserves answers + scope
  //
  // [F-SPA-BACK-NO-ROUTING] — Expected RED on main.
  // The SPA uses goToStep() (in-memory), never pushState. Browser back either
  // exits /assessment/ or is a no-op. The Phase 1 heading assertion fails.
  // RED guard ensures Phase 3A routing work covers the popstate SPA path.
  // ===========================================================================
  test(
    "SPA back-button mid-assessment preserves answers + scope @regression",
    async ({ page }) => {
      test.setTimeout(90_000);
      page.on("dialog", (d) => d.dismiss().catch(() => {}));

      // (a) Load SPA with clean storage.
      await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
      await clearPageStorage(page);
      await page.reload({ waitUntil: "domcontentloaded" });

      // (b) Scope → 5 answers → results.
      await seedScoping(page, MINI_PERSONA);
      await clickThroughPhase1(page, MINI_PERSONA);
      await navClick(page, "View Results");
      await page
        .getByRole("heading", { name: /Results|Dashboard|Summary/i })
        .waitFor({ timeout: 10_000 });

      // (c) Back twice — expected to restore Phase 1 (fails: SPA has no pushState).
      await page.goBack({ waitUntil: "load", timeout: 10_000 }).catch(() => {});
      await page.goBack({ waitUntil: "load", timeout: 10_000 }).catch(() => {});

      // (d) Assert body + SPA root are visible (no white-screen).
      await expect(page.locator("body"), "body must be visible after goBack").toBeVisible();
      // (d) SPA root must be present (white-screen failure mode caught here).
      await expect(
        page.locator("#assessment-app"),
        "SPA root #assessment-app must be present — white-screen failure mode",
      ).toBeVisible({ timeout: 10_000 });

      // (e) URL must remain /assessment/ (back must not leave the app).
      const urlPath = new URL(page.url()).pathname;
      expect(urlPath, `URL after goBack should remain /assessment/; got ${urlPath}`)
        .toBe("/assessment/");

      // (f) Phase 1 heading visible. [F-SPA-BACK-NO-ROUTING] — currently fails.
      await expect(
        page.getByRole("heading", { name: /Phase 1: Control-Level Assessment/i }),
        "Phase 1 heading must be visible after goBack. FAILURE = F-SPA-BACK-NO-ROUTING",
      ).toBeVisible({ timeout: 10_000 });

      // (g) All 5 answered controls retain their selected answer.
      const labelMap = { yes: "Yes", partial: "Partial", no: "No", na: "N/A" };
      for (const [id, answer] of Object.entries(MINI_PERSONA.answers)) {
        const card = page.locator(`[data-control-id="${id}"]`);
        await expect(
          card.getByRole("button", { name: labelMap[answer], exact: true }),
          `Control ${id}: answer button "${labelMap[answer]}" must remain selected`,
        ).toBeVisible();
      }

      // (h) Scoping fields preserved.
      await expect(page.getByLabel("Organization Name")).toHaveValue("Acme Bank");
      const zoneFieldset = page.getByRole("group", { name: "Active Governance Zones" });
      await expect(
        zoneFieldset.locator('input[type="checkbox"][value="2"]'),
      ).toBeChecked();
    },
  );

  // ===========================================================================
  // Test 4 — SPA forward after back preserves results state  @smoke
  // [F-SPA-BACK-NO-ROUTING] — Expected RED on main (same root cause as T3).
  // ===========================================================================
  test(
    "SPA forward after back preserves results state @smoke",
    async ({ page }) => {
      test.setTimeout(90_000);
      page.on("dialog", (d) => d.dismiss().catch(() => {}));

      // full-cco for deterministic score; filter "unknown" (harness throws on it).
      const rawPersona = loadPersona("full-cco");
      const persona = {
        ...rawPersona,
        answers: Object.fromEntries(
          Object.entries(rawPersona.answers).filter(([, v]) => v !== "unknown"),
        ),
      };

      // (a) Load SPA and run scope → phase1 → results.
      await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
      await clearPageStorage(page);
      await page.reload({ waitUntil: "domcontentloaded" });
      await seedScoping(page, persona);
      await clickThroughPhase1(page, persona);
      await navClick(page, "View Results");
      await page
        .getByRole("heading", { name: /Results|Dashboard|Summary/i })
        .waitFor({ timeout: 10_000 });

      // Capture score before navigation.
      const scoreBefore = await page
        .locator(".ag-overall-score, [data-score], .score-value")
        .first()
        .textContent()
        .catch(() => null);

      // (b) Back twice (no-op on current main — SPA has no pushState).
      await page.goBack({ waitUntil: "load", timeout: 10_000 }).catch(() => {});
      await page.goBack({ waitUntil: "load", timeout: 10_000 }).catch(() => {});

      // (c) Forward twice to return to results.
      await page.goForward({ waitUntil: "load", timeout: 10_000 }).catch(() => {});
      await page.goForward({ waitUntil: "load", timeout: 10_000 }).catch(() => {});

      // (d) URL must remain /assessment/.
      const urlPath = new URL(page.url()).pathname;
      expect(urlPath, `URL after back×2 + forward×2 should be /assessment/; got ${urlPath}`)
        .toBe("/assessment/");

      // (e) Results heading must re-render. [F-SPA-BACK-NO-ROUTING] — fails on main.
      await expect(
        page.getByRole("heading", { name: /Results|Dashboard|Summary/i }),
        "Results heading must be visible after forward×2 (F-SPA-BACK-NO-ROUTING)",
      ).toBeVisible({ timeout: 10_000 });

      // (f) Score must match the pre-back score (state not lost in transit).
      if (scoreBefore !== null) {
        const scoreAfter = await page
          .locator(".ag-overall-score, [data-score], .score-value")
          .first().textContent().catch(() => null);
        expect(scoreAfter, `Score '${scoreBefore}' must survive back+forward`).toBe(scoreBefore);
      }
    },
  );
});
