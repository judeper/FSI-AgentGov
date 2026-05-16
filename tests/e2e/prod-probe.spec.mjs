import { test, expect } from "@playwright/test";
import { countRenderedMermaid } from "./_mermaid.mjs";

const PROD = process.env.PROD_URL;
test.skip(!PROD, "prod-probe only runs with PROD_URL set");

test("@prod-probe assessment SPA loads on production", async ({ page }) => {
  const errors = [];
  // IGNORE_PATTERNS: only true browser-or-platform limitations that produce
  // unavoidable console noise on every load. Anything else must surface as a
  // failure so production regressions don't silently pass.
  //
  // Closes F-CSP-PROD-PROBE-CONNECTSRC-SUPPRESS-01: the previous
  //   /violates the following Content Security Policy directive: "connect-src/i
  // pattern was a defensive carve-out added during the audit transition (when
  // the connect-src allowlist was being tightened from `*` down to
  // `'self' https://api.github.com`). Now that the audit is deployed
  // (PR #255 → c39e4762; prod-smoke green on every run since 2026-05-14)
  // and `connect-src` is finalized, the broad regex masks real regressions —
  // any future connect-src violation indicates either an unintended outbound
  // fetch or a CSP misconfiguration, both of which we want to learn about
  // immediately. Restoration path if a legitimate, transient connect-src
  // warning appears: add a narrow, origin-specific pattern (e.g.,
  //   /Refused to connect to 'https:\/\/expected-origin\.example'/
  // ) — never a substring match on the directive name alone.
  const IGNORE_PATTERNS = [
    // frame-ancestors via <meta> is browser-ignored by spec (CSP3 §3.1.1).
    // GitHub Pages doesn't allow custom HTTP response headers, so we ship
    // an inline JS frame-busting guard instead. The console warning is
    // intentional and unavoidable.
    /Content Security Policy directive 'frame-ancestors' is ignored/i,
    // mkdocs-material announce-bar release-version fetch occasionally surfaces
    // a CSP-shaped warning during preflight even though api.github.com is in
    // the connect-src allowlist; the actual fetch succeeds. Narrow regex —
    // only api.github.com/repos/* paths.
    /api\.github\.com\/repos\/.+Content Security Policy/i,
  ];
  const isIgnorable = (text) => IGNORE_PATTERNS.some((re) => re.test(text));
  page.on("pageerror", (e) => {
    if (!isIgnorable(e.message)) errors.push(`pageerror: ${e.message}`);
  });
  page.on("console", (msg) => {
    if (msg.type() === "error" && !isIgnorable(msg.text())) {
      errors.push(`console: ${msg.text()}`);
    }
  });

  await page.goto(`${PROD}assessment/`, {
    waitUntil: "domcontentloaded",
    timeout: 30_000,
  });

  await expect(page.getByRole("heading", { level: 1 })).toBeVisible({
    timeout: 15_000,
  });

  const verResp = await page.request.get(`${PROD}version.json`);
  expect(verResp.status()).toBe(200);
  const ver = await verResp.json();
  expect(ver.sha).toBeTruthy();
  expect(ver.builtAt).toBeTruthy();

  if (errors.length) {
    throw new Error(`Production console/page errors:\n${errors.join("\n")}`);
  }
});

// =============================================================================
// Mermaid render canary on production
// =============================================================================
// WHY THIS PAGE: /framework/agent-lifecycle/ is one of the canonical Mermaid-
// bearing pages in the framework tier. Per tests/e2e/fixtures/render-expectations.json
// it has expected_mermaid_count = 1 -- a single, stable diagram that is
// extremely unlikely to be removed without an intentional framework rewrite.
// Framework-tier pages change less often than playbooks, so this canary won't
// false-positive on routine doc churn. The 2026-05-15 prod probe confirmed
// this page currently ships raw <pre class="mermaid"> on production (Mermaid
// runner blocked by CSP -- F-MERMAID-CDN-BLOCK), so this test is the canary
// that closes the loop on the audit branch's AS1 vendoring fix.
//
// WHY countRenderedMermaid INSTEAD OF page.locator(".mermaid svg"):
// Material 9.7.6's mermaid plugin renders into attachShadow({ mode: "closed" }).
// A direct `.mermaid svg` locator returns 0 even on a successful render. The
// shared helper in _mermaid.mjs detects render via layout-side signals
// (bounding-box height + open-shadow fallback). Re-implementing inline would
// diverge from spec 31's per-PR test and create maintenance debt.
//
// WHY expect.poll INSTEAD OF A SYNCHRONOUS COUNT:
// Mermaid v11's `mermaid.run()` processes diagrams asynchronously after
// DOMContentLoaded. A sync `count()` immediately after `goto()` races the
// runner. 5 s is generous: a single-block page renders in <1 s on a healthy
// build; the polling interval ramp tolerates slow GitHub Pages edge nodes.
//
// WHY THE NEGATIVE pre.mermaid ASSERTION:
// Once Mermaid runs, it replaces <pre class="mermaid"> with <div class="mermaid">.
// Surviving <pre class="mermaid"> elements mean the runner never fired -- the
// exact regression visible on prod today. The positive count check alone could
// pass on a half-render; the negative check guards the whole-page invariant.
//
// WHY CHROMIUM-ONLY: Mermaid is engine-agnostic (External finding E7); running
// the same render check on webkit/firefox costs CI minutes for zero coverage
// gain. The existing prod-smoke.yml workflow already installs chromium only.
//
// WHY NO SEPARATE /version.json POLL: prod-smoke.yml lines 56-92 already gate
// the entire Playwright invocation behind a SHA + version match on
// /version.json (5-min poll, max 30 attempts). Re-polling here would be
// redundant and would mask deploy-skew bugs rather than detect them.
test("@prod-probe agent-lifecycle Mermaid renders on production", async ({ page, browserName }) => {
  test.skip(browserName !== "chromium", "Mermaid render is engine-agnostic; chromium only saves CI minutes.");

  page.on("pageerror", (err) => {
    throw new Error(`pageerror on /framework/agent-lifecycle/: ${err.name}: ${err.message}`);
  });

  await page.goto(`${PROD}framework/agent-lifecycle/`, {
    waitUntil: "domcontentloaded",
    timeout: 30_000,
  });

  // Positive: at least one Mermaid block rendered into an SVG (in shadow DOM
  // or open DOM; layout-detected by countRenderedMermaid).
  await expect
    .poll(async () => await countRenderedMermaid(page), {
      timeout: 5_000,
      intervals: [200, 400, 800, 1_600],
      message: "[F-MERMAID-CDN-BLOCK] /framework/agent-lifecycle/ rendered no Mermaid SVG within 5 s",
    })
    .toBeGreaterThanOrEqual(1);

  // Negative: no raw <pre class="mermaid"> survivors. Audit-branch AS1 fix
  // (vendor mermaid@11 + intercept Material's CDN load) is required for this
  // to pass on production.
  expect(
    await page.locator("pre.mermaid").count(),
    "[F-MERMAID-CDN-BLOCK] raw <pre class='mermaid'> blocks survived -- Mermaid runner never fired",
  ).toBe(0);
});
