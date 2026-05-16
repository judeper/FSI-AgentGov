/**
 * 35 — Docs site mobile viewport regression
 *
 * Closes F-DOCS-MOBILE-VIEWPORT-UNAUDITED-01 (Phase 3 AS15a).
 *
 * Scope: SPA mobile coverage already exists (specs 17 + 23). The DOCS
 * site (/, /framework/..., /controls/..., /playbooks/..., /downloads/,
 * /disclaimer/) has had no mobile viewport assertions. This spec fills
 * that gap with a representative 6-page sample at three Playwright
 * device profiles.
 *
 * Why representative pages were chosen (not full sitemap):
 *   - / and /downloads/         — landing pages with tables
 *   - /framework/agent-identity-architecture/        (3 mermaid)
 *   - /playbooks/.../environment-lifecycle-management/architecture/
 *     (4 mermaid — widest sequence diagrams; verified via render-
 *      expectations.json oracle)
 *   - /controls/pillar-1-security/1.2-agent-registry-...     (control + 1 diagram)
 *   - /disclaimer/              — simple text-only control sample
 *
 * Per-page assertions (per device profile):
 *   - body has no horizontal overflow (scrollWidth ≤ clientWidth + 1px
 *     to tolerate sub-pixel rounding)
 *   - .mermaid containers, when present, have getBoundingClientRect().width
 *     ≤ window.innerWidth + 1px (mermaid SVGs must scale to viewport,
 *     not break the layout)
 *   - On profiles ≤ Material's 1219px collapse breakpoint (iPhone, Pixel,
 *     iPad portrait), the Material hamburger menu is visible
 *     (.md-header__button[for="__drawer"] is the hamburger control)
 *
 * Tagged @regression @slow because emulating 3 profiles serially across
 * 6 URLs is ~18 navigations.
 *
 * NOTE: AS15 letter convention (a/b/c/d) denotes INDEPENDENT findings
 * within the AS15 fix-set, NOT the content/verifier split used in
 * AS9/AS11/AS13.
 */

import { test, devices } from "@playwright/test";
import { expect } from "./_harness.mjs";

// Override the SPA-focused baseURL from playwright.config.mjs so we
// can use docs-root paths like "/framework/...".
const PORT = parseInt(process.env.PW_PORT || "8765", 10);
const DOCS_BASE = `http://127.0.0.1:${PORT}`;
test.use({ baseURL: DOCS_BASE });

// Material's responsive layout collapses tabs to a hamburger at <1220px.
// All three device profiles below are below that threshold.
const DEVICE_PROFILES = [
  { label: "iPhone 14", config: devices["iPhone 14"] },
  { label: "Pixel 5", config: devices["Pixel 5"] },
  { label: "iPad (gen 7)", config: devices["iPad (gen 7)"] },
];

// Representative docs URLs. Selected via render-expectations.json oracle
// to include the widest-Mermaid pages plus one of each major doc type.
const DOCS_URLS = [
  "/",
  "/disclaimer/",
  "/downloads/",
  "/framework/agent-identity-architecture/",
  "/playbooks/advanced-implementations/environment-lifecycle-management/architecture/",
  "/controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management/",
];

for (const profile of DEVICE_PROFILES) {
  if (!profile.config) {
    test.skip(
      `docs mobile ${profile.label} (device profile not registered) @regression`,
      () => {},
    );
    continue;
  }

  const cfg = profile.config;
  const useOpts = {
    viewport: cfg.viewport,
    userAgent: cfg.userAgent,
    deviceScaleFactor: cfg.deviceScaleFactor,
    isMobile: cfg.isMobile,
    hasTouch: cfg.hasTouch,
  };

  test.describe(`docs mobile viewport ${profile.label} @regression @slow`, () => {
    test.use(useOpts);

    test(`docs pages render without horizontal overflow on ${profile.label} @regression @slow`, async ({
      page,
    }) => {
      test.setTimeout(120_000);

      const failures = [];

      for (const urlPath of DOCS_URLS) {
        await page.goto(urlPath, { waitUntil: "domcontentloaded" });

        // (a) Body-level overflow check — 1px tolerance for sub-pixel
        //     rounding under deviceScaleFactor.
        const overflow = await page.evaluate(() => {
          const d = document.documentElement;
          return d.scrollWidth - d.clientWidth;
        });
        if (overflow > 1) {
          failures.push(
            `[F-DOCS-MOBILE-VIEWPORT-UNAUDITED-01] ${urlPath} on ${profile.label}: ` +
              `body overflows viewport by ${overflow}px (scrollWidth - clientWidth)`,
          );
        }

        // (b) Per-Mermaid-container width check. .mermaid divs must scale
        //     to fit the viewport. We only check pages that actually have
        //     mermaid (others have count=0 → loop is no-op).
        const mermaidOverflows = await page.evaluate(() => {
          const winW = window.innerWidth;
          const overflowing = [];
          document.querySelectorAll(".mermaid").forEach((el, idx) => {
            const w = el.getBoundingClientRect().width;
            if (w > winW + 1) overflowing.push({ idx, w, winW });
          });
          return overflowing;
        });
        for (const m of mermaidOverflows) {
          failures.push(
            `[F-DOCS-MOBILE-VIEWPORT-UNAUDITED-01] ${urlPath} on ${profile.label}: ` +
              `.mermaid[${m.idx}] width ${m.w}px exceeds viewport ${m.winW}px`,
          );
        }

        // (c) Hamburger menu visibility — Material renders the drawer
        //     toggle as <label class="md-header__button md-icon"
        //     for="__drawer"> at viewports below the breakpoint.
        const hamburgerVisible = await page
          .locator('label.md-header__button[for="__drawer"]')
          .first()
          .isVisible()
          .catch(() => false);
        if (!hamburgerVisible) {
          failures.push(
            `[F-DOCS-MOBILE-VIEWPORT-UNAUDITED-01] ${urlPath} on ${profile.label}: ` +
              `Material hamburger menu (label[for="__drawer"]) not visible — ` +
              `mobile nav unreachable`,
          );
        }
      }

      expect(
        failures,
        `Docs mobile failures on ${profile.label} (${failures.length} total):\n` +
          failures.join("\n"),
      ).toEqual([]);
    });
  });
}
