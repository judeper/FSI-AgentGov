import { test, expect } from "@playwright/test";
import { countRenderedMermaid } from "./_mermaid.mjs";

const PROD = process.env.PROD_URL;
const PROD_ROOT = PROD ? new URL(PROD) : null;
const PROD_PATH_PREFIX = PROD_ROOT ? normalizePathPrefix(PROD_ROOT.pathname) : null;
const SAME_ORIGIN_PATTERNS = PROD_ROOT
  ? [
      new RegExp(`^https?:\\/\\/${escapeRegExp(PROD_ROOT.host)}(?:\\/|$)`),
      new RegExp(`^${escapeRegExp(PROD_PATH_PREFIX)}`),
    ]
  : [];
const SAME_ORIGIN_RELATIVE_PATTERN = PROD_PATH_PREFIX
  ? new RegExp(`${escapeRegExp(PROD_PATH_PREFIX)}[^\\s'"\\])>]*`, "i")
  : null;

test.skip(!PROD, "prod-probe only runs with PROD_URL set");

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function normalizePathPrefix(pathname) {
  if (!pathname || pathname === "/") return "/";
  return pathname.endsWith("/") ? pathname : `${pathname}/`;
}

function normalizeUrl(rawUrl) {
  if (!rawUrl || !PROD) return null;
  try {
    const parsed = new URL(String(rawUrl).trim(), PROD);
    if (parsed.origin === "null" || parsed.protocol === "about:") {
      return null;
    }
    return parsed.toString();
  } catch {
    return null;
  }
}

function extractUrlCandidate(text) {
  if (!text) return null;
  const absoluteUrl = text.match(/https?:\/\/[^\s'"\])>]+/i)?.[0];
  if (absoluteUrl) return absoluteUrl;
  return SAME_ORIGIN_RELATIVE_PATTERN ? text.match(SAME_ORIGIN_RELATIVE_PATTERN)?.[0] ?? null : null;
}

function isSameOrigin(rawUrl) {
  if (!rawUrl || !PROD_ROOT) return false;

  const rawValue = String(rawUrl).trim();
  const normalizedValue = normalizeUrl(rawValue);
  const candidates = [rawValue, normalizedValue].filter(Boolean);

  if (candidates.some((value) => SAME_ORIGIN_PATTERNS.some((pattern) => pattern.test(value)))) {
    return true;
  }

  try {
    return new URL(normalizedValue ?? rawValue, PROD).origin === PROD_ROOT.origin;
  } catch {
    return false;
  }
}

function createProbeCollector(page, ignorePatterns = []) {
  const sameOriginErrors = [];
  const thirdPartyErrors = [];
  const seen = new Set();
  const isIgnorable = (text) => ignorePatterns.some((pattern) => pattern.test(text));

  const record = ({ kind, url, detail, fallbackUrl = page.url() }) => {
    if (isIgnorable(detail)) return;

    const sourceUrl = normalizeUrl(url) ?? normalizeUrl(fallbackUrl) ?? url ?? fallbackUrl ?? "unknown";
    const entry = `[${kind}] ${sourceUrl} :: ${detail}`;
    if (seen.has(entry)) return;
    seen.add(entry);

    if (isSameOrigin(sourceUrl)) {
      sameOriginErrors.push(entry);
    } else {
      thirdPartyErrors.push(entry);
    }
  };

  page.on("pageerror", (err) => {
    record({
      kind: "pageerror",
      url: page.url(),
      detail: `${err.name}: ${err.message}`,
      fallbackUrl: PROD,
    });
  });

  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    const sourceUrl = msg.location()?.url || extractUrlCandidate(msg.text());
    const isFailedResourceMessage = /Failed to load resource/i.test(msg.text());
    const fallbackUrl = sourceUrl || isFailedResourceMessage ? null : (page.url() || PROD);
    record({
      kind: "console",
      url: sourceUrl,
      detail: msg.text(),
      fallbackUrl,
    });
  });

  page.on("requestfailed", (request) => {
    record({
      kind: `requestfailed:${request.resourceType()}`,
      url: request.url(),
      detail: request.failure()?.errorText ?? "request failed",
      fallbackUrl: page.url() || PROD,
    });
  });

  page.on("response", (response) => {
    if (response.status() < 400) return;
    const request = response.request();
    record({
      kind: `response:${response.status()}:${request.resourceType()}`,
      url: response.url(),
      detail: `${response.status()} ${response.statusText()}`.trim(),
      fallbackUrl: page.url() || PROD,
    });
  });

  return { sameOriginErrors, thirdPartyErrors };
}

async function attachProbeSummary(testInfo, label, sameOriginErrors, thirdPartyErrors) {
  if (!sameOriginErrors.length && !thirdPartyErrors.length) return;

  const summary = [
    `[prod-probe] ${label} summary`,
    `same-origin failures (fatal): ${sameOriginErrors.length}`,
    `third-party warnings (non-fatal): ${thirdPartyErrors.length}`,
    ...(sameOriginErrors.length ? ["", "Same-origin failures:", ...sameOriginErrors] : []),
    ...(thirdPartyErrors.length ? ["", "Third-party warnings:", ...thirdPartyErrors] : []),
  ].join("\n");

  console.log(summary);
  await testInfo.attach(`${label}-origin-summary`, {
    body: summary,
    contentType: "text/plain",
  });
}

async function assertNoSameOriginFailures(testInfo, label, collector) {
  await attachProbeSummary(testInfo, label, collector.sameOriginErrors, collector.thirdPartyErrors);
  if (collector.sameOriginErrors.length) {
    throw new Error(
      `[prod-probe] ${label} captured ${collector.sameOriginErrors.length} same-origin failure(s):\n${collector.sameOriginErrors.join("\n")}`,
    );
  }
}

function expectStatus200(response, urlLabel) {
  if (!response) {
    throw new Error(`${urlLabel} did not return an HTTP response`);
  }
  expect(response.status(), `${urlLabel} should return 200`).toBe(200);
}

// Scheduled prod-smoke should only fail on same-origin regressions. Third-party
// console/network noise (api.github.com, analytics, CDNs we do not control) is
// still logged for debugging, but it is warn-only so transient upstream blips do
// not auto-file customer-facing incidents.
test("@prod-probe assessment SPA loads on production (same-origin failures only)", async ({ page }, testInfo) => {
  const collector = createProbeCollector(page, [
    // frame-ancestors via <meta> is browser-ignored by spec (CSP3 §3.1.1).
    // GitHub Pages doesn't allow custom HTTP response headers, so we ship
    // an inline JS frame-busting guard instead. The console warning is
    // intentional and unavoidable.
    /Content Security Policy directive 'frame-ancestors' is ignored/i,
  ]);

  const assessmentResp = await page.goto(`${PROD}assessment/`, {
    waitUntil: "domcontentloaded",
    timeout: 30_000,
  });
  expectStatus200(assessmentResp, `${PROD}assessment/`);

  await expect(page.getByRole("heading", { level: 1 })).toBeVisible({
    timeout: 15_000,
  });

  const verResp = await page.request.get(`${PROD}version.json`);
  expect(verResp.status(), `${PROD}version.json should return 200`).toBe(200);
  const ver = await verResp.json();
  expect(ver.sha).toBeTruthy();
  expect(ver.builtAt).toBeTruthy();

  await assertNoSameOriginFailures(testInfo, "assessment-spa", collector);
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
test("@prod-probe agent-lifecycle Mermaid renders on production", async ({ page, browserName }, testInfo) => {
  test.skip(browserName !== "chromium", "Mermaid render is engine-agnostic; chromium only saves CI minutes.");

  const collector = createProbeCollector(page);

  const lifecycleResp = await page.goto(`${PROD}framework/agent-lifecycle/`, {
    waitUntil: "domcontentloaded",
    timeout: 30_000,
  });
  expectStatus200(lifecycleResp, `${PROD}framework/agent-lifecycle/`);

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

  await assertNoSameOriginFailures(testInfo, "agent-lifecycle-mermaid", collector);
});
