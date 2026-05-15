/**
 * 32 — Docs accessibility (axe + WCAG 2.1 AA, color-contrast ENABLED)
 *
 * Companion to spec 19 (which only scans the assessment SPA and disables
 * `color-contrast`). This spec extends axe coverage to a representative
 * sample of customer-facing docs pages with `color-contrast` ENABLED so
 * that Phase 3 a11y/contrast fixes have an explicit RED-then-GREEN target.
 *
 * Why color-contrast matters here:
 *   FSI customers (banks, broker-dealers, RIAs) face ADA Title III case-law
 *   exposure on customer-facing public web content (Robles v. Domino's,
 *   Gil v. Winn-Dixie, etc.). The mkdocs-material theme defaults are not
 *   guaranteed WCAG 2.1 AA against the project's custom palette overrides
 *   in extra.css, so we assert it here instead of trusting upstream.
 *
 * Findings family this spec guards:
 *   F-A11Y-DOCS-CONTRAST-*   — axe color-contrast violations on docs pages
 *   F-A11Y-DOCS-WCAG-*       — non-contrast WCAG 2.1 AA violations on docs
 *   F-A11Y-SPA-CONTRAST-*    — color-contrast deltas on the SPA when the
 *                              rule is re-enabled (spec 19 disables it)
 *
 * Sampling strategy:
 *   - One page per top-level nav section (home, getting-started, framework,
 *     controls, playbooks, reference, downloads).
 *   - Plus the Mermaid-bearing framework page (agent-lifecycle) so that
 *     SVG label / aria-label issues surface here, not just in spec 31.
 *   - Plus a representative pillar-1 control (1.1) so the dense control
 *     template (header table + zone table + roles table + footer) gets
 *     contrast-scanned.
 *   - Plus the two CSA-engagement reference pages explicitly called out in
 *     AGENTS.md as "Key reference documents".
 *   - Plus the SPA welcome screen as a contrast-enabled re-scan of spec 19.
 *
 * Failure handling:
 *   Per-page violations are collected SOFT (test.info().annotations) so the
 *   first failing page does not mask the rest — every page in the sample is
 *   scanned every run. The test FAILS at the end with a single aggregate
 *   error listing every offending (page, rule, selector, fix-hint) tuple.
 *
 *   Each blocking violation receives a remediation hint derived from
 *   axe's `help` + `helpUrl` plus the offending element selector so the
 *   reviewer can act on the failure without re-running locally.
 *
 * Severity policy (matches Phase 0 finding rubric):
 *   - WCAG AA (incl. color-contrast) on customer-facing docs → P1
 *   - Keyboard / focus traps with workaround                  → P2
 *   - Cosmetic                                                → P3
 *
 * Per-page raw axe JSON is written to test-results/axe-docs/<slug>.json
 * for triage parity with spec 19.
 *
 * Note on baseURL: playwright.config.mjs sets baseURL to /assessment/.
 * This spec overrides it to the docs root so page.goto('/framework/...') works.
 */

import { test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { expect } from "./_harness.mjs";

const PORT = parseInt(process.env.PW_PORT || "8765", 10);
const DOCS_BASE = `http://127.0.0.1:${PORT}`;
const ARTIFACT_DIR = "test-results/axe-docs";

// ── Sample set ────────────────────────────────────────────────────────────────
// Each entry: { url, label, slug, kind }
//   kind: 'docs' | 'spa' — drives the readiness predicate before scanning.
const SAMPLE_PAGES = [
  { url: "/", label: "Home", slug: "home", kind: "docs" },
  {
    url: "/getting-started/",
    label: "Getting Started",
    slug: "getting-started",
    kind: "docs",
  },
  {
    url: "/framework/agent-lifecycle/",
    label: "Framework: Agent Lifecycle (Mermaid bearer)",
    slug: "framework-agent-lifecycle",
    kind: "docs",
  },
  {
    url: "/controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization/",
    label: "Control 1.1 Restrict Agent Publishing",
    slug: "control-1.1",
    kind: "docs",
  },
  {
    url: "/playbooks/",
    label: "Playbooks index",
    slug: "playbooks-index",
    kind: "docs",
  },
  {
    url: "/reference/role-catalog/",
    label: "Reference: Role Catalog",
    slug: "reference-role-catalog",
    kind: "docs",
  },
  {
    url: "/reference/csa-quick-reference/",
    label: "Reference: CSA Quick Reference",
    slug: "reference-csa-quick-reference",
    kind: "docs",
  },
  {
    url: "/downloads/",
    label: "Downloads index",
    slug: "downloads-index",
    kind: "docs",
  },
  // SPA re-scan with color-contrast ENABLED — spec 19 disables it; this
  // surfaces the trade-off accent colours so we can document the delta.
  {
    url: "/assessment/",
    label: "Assessment SPA (welcome) — color-contrast ENABLED",
    slug: "spa-welcome-contrast",
    kind: "spa",
  },
];

// ── Axe builder factory ──────────────────────────────────────────────────────
// Mirrors spec 19's tag set EXCEPT we do NOT disableRules(['color-contrast']).
// We do exclude the mkdocs-material announce-bar and search overlay because
// they are theme-controlled, surface false-positive contrast hits depending
// on the announce-bar text length, and are out of scope for FSI doc updates.
function buildScan(page) {
  return new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .exclude("[data-md-component='announce']")
    .exclude(".md-search__overlay");
}

// ── Result helpers ───────────────────────────────────────────────────────────
function summarizeNode(node) {
  const target = (node.target && node.target[0]) || "(no selector)";
  // axe attaches `any/all/none` arrays — pull the first failure-message we find.
  const reasons = [
    ...(node.any || []),
    ...(node.all || []),
    ...(node.none || []),
  ]
    .map((r) => r.message)
    .filter(Boolean);
  return {
    target,
    failureSummary: node.failureSummary || reasons.join(" | "),
    html: (node.html || "").slice(0, 240),
  };
}

function fixHintFor(violation, node) {
  // Tailored remediation hints by rule. Falls back to axe's `help`+`helpUrl`.
  const ruleHints = {
    "color-contrast":
      "Increase foreground/background contrast to ≥ 4.5:1 for normal text, ≥ 3:1 for ≥18pt or bold ≥14pt. Adjust extra.css palette tokens (or the mkdocs-material primary/accent custom variables in mkdocs.yml).",
    "color-contrast-enhanced":
      "WCAG AAA enhanced contrast — only required if pursuing AAA. For AA baseline this can be deferred; otherwise raise contrast to ≥ 7:1.",
    "link-in-text-block":
      "Links inside body text need a non-color cue (underline, bold, icon) OR ≥ 3:1 contrast against surrounding text. Add an underline in extra.css.",
    "image-alt":
      "Add a meaningful alt attribute. For decorative images use alt=\"\" so screen readers skip them.",
    "button-name":
      "Add visible text or an aria-label on the button so its purpose is announced.",
    "label":
      "Associate the input with a <label for=...> or wrap it in a <label>; aria-labelledby/aria-label also acceptable.",
    "landmark-one-main":
      "Page must have exactly one <main> landmark. Check the mkdocs-material theme override or main.html block.",
    "region":
      "All page content should sit inside a landmark (main/nav/header/footer/section[aria-label]).",
    "heading-order":
      "Heading levels must not skip (e.g. h2 → h4). Demote/promote markdown ## levels to maintain monotonic order.",
    "html-has-lang":
      "Set <html lang=\"en\"> via theme.language in mkdocs.yml.",
    "frame-title":
      "All <iframe> elements need a title attribute.",
    "duplicate-id":
      "IDs must be unique. Likely a markdown heading-anchor collision — rename a heading or use markdown-attr {#unique-id}.",
    "duplicate-id-aria":
      "ARIA-referenced IDs must be unique site-wide on the rendered page.",
    "scrollable-region-focusable":
      "Make the scrollable region keyboard-focusable (tabindex=\"0\") so keyboard users can scroll it.",
    "aria-allowed-attr":
      "Remove the disallowed ARIA attribute or change the role so the attribute is permitted.",
    "aria-required-children":
      "Add required ARIA child roles (e.g. role=tablist needs role=tab children).",
  };
  const base = ruleHints[violation.id] || violation.help;
  return `${base} (rule: ${violation.id} · ${violation.helpUrl})`;
}

function persistResults(slug, results) {
  mkdirSync(ARTIFACT_DIR, { recursive: true });
  writeFileSync(
    join(ARTIFACT_DIR, `${slug}.json`),
    JSON.stringify(results, null, 2),
    "utf8",
  );
}

// ── Page-readiness gates ─────────────────────────────────────────────────────
async function waitForReady(page, kind) {
  if (kind === "spa") {
    // SPA must hydrate to the welcome state before we scan.
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });
    return;
  }
  // mkdocs-material: wait for the primary article landmark + footer.
  await page.locator("article.md-content__inner").first().waitFor({
    state: "attached",
    timeout: 15_000,
  });
}

// ── baseURL override (docs root, not /assessment/) ───────────────────────────
test.use({ baseURL: DOCS_BASE });

// =============================================================================
// Aggregate axe scan across the docs sample. SERIAL so per-page failures
// surface in one consolidated error rather than first-fail short-circuit.
// =============================================================================
test.describe.serial("docs a11y axe (color-contrast ENABLED) @regression", () => {
  test(
    "WCAG 2.1 AA across customer-facing docs sample @regression",
    async ({ page }) => {
      // Larger budget: 9 pages × ~2-3s axe analyze each + page load.
      test.setTimeout(180_000);

      page.on("dialog", (d) => d.dismiss().catch(() => {}));

      const allFailures = [];
      const perPageCounts = [];

      for (const sample of SAMPLE_PAGES) {
        try {
          await page.goto(sample.url, { waitUntil: "domcontentloaded" });
          await waitForReady(page, sample.kind);
        } catch (e) {
          allFailures.push({
            page: sample.url,
            label: sample.label,
            rule: "(navigation)",
            impact: "critical",
            selector: "(n/a)",
            fixHint: `Page failed to load before scan: ${e.message}`,
          });
          perPageCounts.push({
            page: sample.url,
            label: sample.label,
            total: 0,
            blocking: 1,
            byRule: { "(navigation)": 1 },
          });
          continue;
        }

        const results = await buildScan(page).analyze();
        persistResults(sample.slug, results);

        // Blocking = serious|critical (matches spec 19's gate). Minor/moderate
        // are written to the JSON artifact for triage but don't fail the suite.
        const blocking = (results.violations || []).filter(
          (v) => v.impact === "serious" || v.impact === "critical",
        );

        const byRule = {};
        for (const v of blocking) {
          byRule[v.id] = (byRule[v.id] || 0) + (v.nodes?.length || 1);
          for (const node of v.nodes || []) {
            const summary = summarizeNode(node);
            allFailures.push({
              page: sample.url,
              label: sample.label,
              rule: v.id,
              impact: v.impact,
              selector: summary.target,
              snippet: summary.html,
              fixHint: fixHintFor(v, node),
            });
          }
        }

        perPageCounts.push({
          page: sample.url,
          label: sample.label,
          total: (results.violations || []).length,
          blocking: blocking.length,
          byRule,
        });
      }

      // Always emit a per-page summary to the test annotations so reviewers
      // can see counts even on a green run.
      for (const c of perPageCounts) {
        test
          .info()
          .annotations.push({
            type: "axe-summary",
            description: `${c.label} (${c.page}): ${c.total} total violation(s), ${c.blocking} serious/critical · by-rule: ${JSON.stringify(c.byRule)}`,
          });
      }

      if (allFailures.length > 0) {
        const lines = allFailures.map(
          (f) =>
            `  - [${f.impact}] ${f.rule} on ${f.page}\n      selector: ${f.selector}\n      fix: ${f.fixHint}`,
        );
        // RED guard: this is expected to fail on current main until Phase 3
        // contrast/a11y fixes land. The aggregate message gives Phase 3 a
        // single GREEN target.
        throw new Error(
          `axe found ${allFailures.length} serious/critical accessibility violation(s) across ${perPageCounts.length} docs pages:\n${lines.join("\n")}`,
        );
      }

      expect(allFailures.length).toBe(0);
    },
  );
});

// =============================================================================
// Lightweight contrast probe — surfaces the *measured* contrast ratios on
// representative page surfaces so reviewers can sanity-check axe findings
// against ground-truth pixel values. Always passes (informational); writes
// a JSON artifact for triage.
//
// Per task brief D2: 3 representative pages × {body text, link, button,
// code block} surfaces. Light mode only here — dark-mode mermaid handling
// is covered by F-DARKMODE-MERMAID-01 in spec 31.
// =============================================================================
test.describe("docs contrast probe (informational) @regression", () => {
  test("measure contrast ratios on representative surfaces @regression", async ({
    page,
  }) => {
    test.setTimeout(60_000);

    const PROBE_PAGES = [
      { url: "/", label: "Home" },
      {
        url: "/controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization/",
        label: "Control 1.1",
      },
      {
        url: "/reference/csa-quick-reference/",
        label: "CSA Quick Reference",
      },
    ];

    const probe = async () => {
      // Pure-page probe: walks a few selectors, returns measured fg/bg + ratio.
      // Uses WCAG relative-luminance formula (per WCAG 2.1 §1.4.3).
      return await page.evaluate(() => {
        function parseRgb(s) {
          const m = s.match(/rgba?\(([^)]+)\)/);
          if (!m) return null;
          const parts = m[1].split(",").map((p) => parseFloat(p.trim()));
          return { r: parts[0], g: parts[1], b: parts[2], a: parts[3] ?? 1 };
        }
        function chan(c) {
          const s = c / 255;
          return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
        }
        function lum({ r, g, b }) {
          return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b);
        }
        function ratio(fg, bg) {
          const L1 = lum(fg);
          const L2 = lum(bg);
          const [a, b] = L1 > L2 ? [L1, L2] : [L2, L1];
          return (a + 0.05) / (b + 0.05);
        }
        function effectiveBg(el) {
          let cur = el;
          while (cur && cur !== document.documentElement) {
            const cs = getComputedStyle(cur);
            const bg = parseRgb(cs.backgroundColor);
            if (bg && bg.a > 0) return bg;
            cur = cur.parentElement;
          }
          // fall back to body
          const bodyBg = parseRgb(getComputedStyle(document.body).backgroundColor);
          return bodyBg || { r: 255, g: 255, b: 255, a: 1 };
        }
        const targets = [
          { name: "body-text", selector: "article p" },
          { name: "link-in-body", selector: "article a" },
          { name: "h1", selector: "article h1" },
          { name: "h2", selector: "article h2" },
          { name: "code-inline", selector: "article code" },
          { name: "code-block", selector: "article pre code" },
          { name: "nav-link", selector: ".md-tabs__link" },
          { name: "nav-arrow", selector: ".md-footer__link" },
          { name: "table-cell", selector: "article table td" },
          { name: "table-header", selector: "article table th" },
        ];
        const out = [];
        for (const t of targets) {
          const el = document.querySelector(t.selector);
          if (!el) {
            out.push({ surface: t.name, found: false });
            continue;
          }
          const cs = getComputedStyle(el);
          const fg = parseRgb(cs.color);
          const bg = effectiveBg(el);
          if (!fg || !bg) {
            out.push({ surface: t.name, found: true, error: "color parse" });
            continue;
          }
          const r = ratio(fg, bg);
          const fontSize = parseFloat(cs.fontSize);
          const fontWeight = parseInt(cs.fontWeight, 10) || 400;
          // WCAG large-text threshold: ≥18pt (24px) OR ≥14pt (18.66px) bold.
          const isLarge =
            fontSize >= 24 || (fontSize >= 18.66 && fontWeight >= 700);
          const required = isLarge ? 3.0 : 4.5;
          out.push({
            surface: t.name,
            selector: t.selector,
            fg: `rgb(${fg.r},${fg.g},${fg.b})`,
            bg: `rgb(${bg.r},${bg.g},${bg.b})`,
            ratio: Math.round(r * 100) / 100,
            fontSize,
            fontWeight,
            isLarge,
            required,
            passes: r >= required,
          });
        }
        return out;
      });
    };

    const all = {};
    for (const p of PROBE_PAGES) {
      try {
        await page.goto(p.url, { waitUntil: "domcontentloaded" });
        await page
          .locator("article.md-content__inner")
          .first()
          .waitFor({ state: "attached", timeout: 10_000 });
        all[p.url] = { label: p.label, surfaces: await probe() };
      } catch (e) {
        all[p.url] = { label: p.label, error: e.message };
      }
    }

    mkdirSync(ARTIFACT_DIR, { recursive: true });
    writeFileSync(
      join(ARTIFACT_DIR, "_contrast-probe.json"),
      JSON.stringify(all, null, 2),
      "utf8",
    );

    // Annotate any sub-threshold surfaces so triage can read them without
    // opening the JSON file.
    for (const [url, data] of Object.entries(all)) {
      if (!data.surfaces) continue;
      for (const s of data.surfaces) {
        if (s.passes === false) {
          test.info().annotations.push({
            type: "contrast-fail",
            description: `${url} ${s.surface} (${s.selector}) ratio=${s.ratio} required=${s.required} fg=${s.fg} bg=${s.bg}`,
          });
        }
      }
    }

    // Informational — never fails. The axe describe-block above is the gate.
    expect(Object.keys(all).length).toBe(PROBE_PAGES.length);
  });
});

// =============================================================================
// Skip-link + landmark sanity (D3 + D4 quick-pass).
//   - <html lang> present
//   - exactly one <main> landmark
//   - skip-to-content link is the first focusable element OR is reachable
//     via a single Tab from the document body
//   - every <img> in the article has an alt attribute (empty alt allowed for
//     decorative)
//   - every form input has a programmatic label
//
// Non-axe checks that complement the axe scan above. Failures here are
// classified as "soft" annotations rather than test failures because the
// axe describe-block is already the WCAG enforcement point — these are
// targeted RED guards for findings that axe sometimes misses (skip-link
// presence in particular is not in the default rule set).
// =============================================================================
test.describe("docs landmark + skip-link sanity @regression", () => {
  test("home + control page expose required landmarks @regression", async ({
    page,
  }) => {
    test.setTimeout(45_000);
    const PAGES = [
      "/",
      "/controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization/",
    ];

    const issues = [];
    for (const url of PAGES) {
      await page.goto(url, { waitUntil: "domcontentloaded" });
      await page
        .locator("article.md-content__inner")
        .first()
        .waitFor({ state: "attached", timeout: 10_000 });

      const audit = await page.evaluate(() => {
        const out = { url: location.pathname };
        out.htmlLang = document.documentElement.getAttribute("lang") || null;
        out.mainCount = document.querySelectorAll("main").length;
        out.navCount = document.querySelectorAll("nav").length;
        out.headerCount = document.querySelectorAll("header").length;
        out.footerCount = document.querySelectorAll("footer").length;
        // Skip-link heuristic: first <a href="#..."> in source order whose
        // text contains "skip" (case-insensitive). mkdocs-material does NOT
        // ship one by default — this is expected to fail until added.
        const firstSkip = Array.from(document.querySelectorAll("a[href^='#']"))
          .find((a) => /skip/i.test(a.textContent || ""));
        out.skipLinkPresent = !!firstSkip;
        // Heading order — flag any skip > 1 in monotonic descent.
        const hs = Array.from(
          document.querySelectorAll("article h1, article h2, article h3, article h4, article h5, article h6"),
        ).map((h) => parseInt(h.tagName.slice(1), 10));
        const skips = [];
        for (let i = 1; i < hs.length; i++) {
          if (hs[i] - hs[i - 1] > 1)
            skips.push(`h${hs[i - 1]} → h${hs[i]} at index ${i}`);
        }
        out.headingSkips = skips;
        // Images without alt
        out.imgsMissingAlt = Array.from(
          document.querySelectorAll("article img:not([alt])"),
        ).map((img) => img.getAttribute("src"));
        // Form inputs without programmatic label
        out.inputsWithoutLabel = Array.from(
          document.querySelectorAll(
            "article input:not([type='hidden']), article select, article textarea",
          ),
        )
          .filter((inp) => {
            if (inp.getAttribute("aria-label")) return false;
            if (inp.getAttribute("aria-labelledby")) return false;
            const id = inp.getAttribute("id");
            if (id && document.querySelector(`label[for='${id}']`)) return false;
            if (inp.closest("label")) return false;
            return true;
          })
          .map((inp) => inp.outerHTML.slice(0, 120));
        return out;
      });

      const pageIssues = [];
      if (!audit.htmlLang) pageIssues.push("missing html[lang]");
      if (audit.mainCount !== 1)
        pageIssues.push(`main landmark count = ${audit.mainCount} (expected 1)`);
      if (audit.headerCount === 0) pageIssues.push("no <header> landmark");
      if (audit.footerCount === 0) pageIssues.push("no <footer> landmark");
      if (!audit.skipLinkPresent)
        pageIssues.push("no 'skip to content' link in document order");
      if (audit.headingSkips.length > 0)
        pageIssues.push(`heading-level skips: ${audit.headingSkips.join("; ")}`);
      if (audit.imgsMissingAlt.length > 0)
        pageIssues.push(
          `imgs without alt: ${audit.imgsMissingAlt.slice(0, 3).join(", ")}${audit.imgsMissingAlt.length > 3 ? " …" : ""}`,
        );
      if (audit.inputsWithoutLabel.length > 0)
        pageIssues.push(
          `inputs without label: ${audit.inputsWithoutLabel.length}`,
        );

      if (pageIssues.length > 0) {
        issues.push({ url, problems: pageIssues, audit });
        for (const p of pageIssues) {
          test.info().annotations.push({
            type: "landmark-issue",
            description: `${url}: ${p}`,
          });
        }
      }
    }

    if (issues.length > 0) {
      const lines = issues.flatMap((i) =>
        i.problems.map((p) => `  - ${i.url}: ${p}`),
      );
      throw new Error(
        `Landmark / skip-link sanity check failed:\n${lines.join("\n")}`,
      );
    }
    expect(issues.length).toBe(0);
  });
});
