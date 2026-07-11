/**
 * 36 — Material Lunr search correctness regression
 *
 * Closes F-DOCS-SEARCH-CORRECTNESS-UNAUDITED-01 (Phase 3 AS15b).
 *
 * Three independent assertions:
 *
 * (1) **Search corpus shorthand check** — the built search index
 *     (site/search/search_index.json, ~16MB) must not surface
 *     non-canonical regulatory shorthand to customer queries.
 *     Patterns checked:
 *         OCC/SR
 *         OCC 2011-12 / SR 11-7
 *         SR 11-7 / OCC 2011-12
 *         OCC Bulletin 2011-12 / Fed SR 11-7
 *         OCC Bulletin 2011-12 / Federal Reserve SR 11-7
 *     Each hit's 100-char window must contain a supersession marker
 *     (formerly | superseded | rescinded | predecessor | supersession |
 *     supersedes). Catches admonition-body shorthand the AS3'b
 *     verifier carve-out (block-level admonition skip) currently
 *     allows but customers see in search snippets.
 *
 * (2) **Source-side verifier subprocess** — spawn
 *     scripts/verify_regulatory_naming.py --check as a subprocess
 *     and assert exit 0. Single source of truth for source-side
 *     canonical naming. After AS15b-verifier tightens the
 *     admonition carve-out and AS15b-content sweeps the leakage,
 *     this assertion stays GREEN and prevents future regressions.
 *
 * (3) **Lunr typed-query smoke** — open the docs site, type 5
 *     customer queries through Material's search box, assert each
 *     query's top-10 results include expected pages. Validates
 *     end-to-end that:
 *     - The search worker initializes
 *     - The corpus is indexed correctly
 *     - Legacy-name searches ("OCC 2011-12", "SR 11-7") still
 *       return the canonicalized pages (because every page now
 *       contains "(formerly OCC 2011-12)" / "(formerly SR 11-7)" —
 *       Lunr indexes the parenthetical content)
 *
 * RED-before-fix discipline: assertion (1) is RED today against the
 * 21-page admonition-body leakage AS3'b's carve-out misses. After
 * AS15b-verifier + AS15b-content land, all three turn GREEN.
 *
 * AS15 letter convention: a/b/c/d denote INDEPENDENT findings
 * within the AS15 fix-set; AS15b internally splits into spec /
 * verifier / content sub-commits per RED-first discipline.
 */

import { test } from "@playwright/test";
import { expect } from "./_harness.mjs";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const REPO_ROOT = path.resolve(__dirname, "..", "..");

const PORT = parseInt(process.env.PW_PORT || "8765", 10);
const DOCS_BASE = `http://127.0.0.1:${PORT}`;
test.use({ baseURL: DOCS_BASE });

// ---------------------------------------------------------------------------
// (1) Search corpus shorthand check
// ---------------------------------------------------------------------------

const SHORTHAND_PATTERNS = [
  { name: "OCC/SR shorthand", re: /\bOCC\/SR\b/g },
  { name: "inline OCC 2011-12 / SR 11-7", re: /\bOCC 2011-12 \/ SR 11-7\b/g },
  { name: "inline SR 11-7 / OCC 2011-12", re: /\bSR 11-7 \/ OCC 2011-12\b/g },
  {
    name: "Bulletin 2011-12 / Fed SR 11-7",
    re: /\bOCC Bulletin 2011-12 \/ (?:Federal Reserve |Fed )?SR 11-7\b/g,
  },
];

// Supersession markers any of which legitimizes a legacy mention
// (matches the canonical "(formerly OCC 2011-12)" pattern as well as
// the supersession narrative in control 2.6 + 2.6 playbooks).
const SUPERSESSION_MARKER_RE =
  /\b(formerly|superseded|rescinded|predecessor|supersession|supersedes)\b/i;
const WINDOW_CHARS = 100;

test(
  "search corpus contains no non-canonical regulatory shorthand @regression @smoke",
  async () => {
    const indexPath = path.join(REPO_ROOT, "site", "search", "search_index.json");
    if (!fs.existsSync(indexPath)) {
      throw new Error(
        `search_index.json not found at ${indexPath}. Run \`mkdocs build\` first.`,
      );
    }
    const raw = fs.readFileSync(indexPath, "utf8");
    const index = JSON.parse(raw);
    const docs = index.docs || [];

    const failures = [];
    for (const doc of docs) {
      const text = doc.text || "";
      if (!text) continue;
      for (const { name, re } of SHORTHAND_PATTERNS) {
        re.lastIndex = 0;
        let m;
        while ((m = re.exec(text)) !== null) {
          const start = Math.max(0, m.index - WINDOW_CHARS);
          const end = Math.min(text.length, m.index + m[0].length + WINDOW_CHARS);
          const window = text.substring(start, end);
          if (!SUPERSESSION_MARKER_RE.test(window)) {
            const snippet = window.replace(/\s+/g, " ").trim();
            failures.push(
              `[${name}] location=${doc.location} title="${doc.title}" ::: ${snippet}`,
            );
          }
        }
      }
    }

    expect(
      failures,
      `[F-DOCS-SEARCH-CORRECTNESS-UNAUDITED-01] non-canonical shorthand in search corpus ` +
        `(${failures.length} hits without 'formerly|superseded|rescinded|predecessor' within ${WINDOW_CHARS} chars):\n` +
        failures.slice(0, 50).join("\n") +
        (failures.length > 50 ? `\n  ...and ${failures.length - 50} more` : ""),
    ).toEqual([]);
  },
);

// ---------------------------------------------------------------------------
// (2) Source-side verifier subprocess (single source of truth)
// ---------------------------------------------------------------------------

test(
  "scripts/verify_regulatory_naming.py --check exits 0 on source corpus @regression",
  async () => {
    const pythonExe = process.env.PYTHON || "python";
    const scriptPath = path.join(REPO_ROOT, "scripts", "verify_regulatory_naming.py");
    let stdout = "";
    let stderr = "";
    let exitCode = 0;
    try {
      stdout = execFileSync(pythonExe, [scriptPath, "--check"], {
        cwd: REPO_ROOT,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"],
      });
    } catch (err) {
      exitCode = err.status ?? -1;
      stdout = err.stdout?.toString() ?? "";
      stderr = err.stderr?.toString() ?? "";
    }
    expect(
      exitCode,
      `[F-DOCS-SEARCH-CORRECTNESS-UNAUDITED-01] verifier exited ${exitCode}\n` +
        `stdout:\n${stdout}\nstderr:\n${stderr}`,
    ).toBe(0);
  },
);

// ---------------------------------------------------------------------------
// (3) Lunr typed-query smoke (customer-facing search invariants)
// ---------------------------------------------------------------------------

// Lunr config note (verified in site/search/search_index.json `config`):
// Material's search uses `separator: "[\\s\\-]+"` — queries tokenize on
// whitespace AND hyphens. "OCC 2011-12" becomes 3 tokens [OCC, 2011, 12];
// however Material's UI returns empty results for queries with embedded
// hyphens until the worker is fully warmed (timing-dependent). We use
// hyphen-free queries throughout; legacy-name canonicalization is
// validated via "OCC 2011" / "SR 11-7" (the latter happens to match
// because Lunr re-tokenizes both sides of the hyphen as separate terms).
//
// Each query asserts AT LEAST ONE expected URL substring appears in top
// 5 result hrefs (Material's title boost = 1000 keeps the canonical page
// at the top for natural-language queries).
//
// Reload-per-query strategy: Material does NOT clear its results panel
// when the search input is emptied via fill(""), so stale results from
// the prior query leak into the next assertion. page.goto("/") between
// queries gives each query a fresh worker state. A warmup query precedes
// the assertions because the search worker is not always ready on the
// first interaction (race against Material's lazy-loaded search bundle).
const WARMUP_QUERY = "warmup";

const TYPED_QUERIES = [
  {
    // Legacy-name invariant: AS3'/AS11 canonicalization promises that
    // every legacy "OCC 2011-12" mention is followed by "(formerly..."
    // — Lunr indexes "OCC", "2011", "12" tokens and returns canonical
    // 2.6 control for customers searching by old name.
    query: "OCC 2011",
    expectedAny: ["2.6-model-risk-management-sr-26-2"],
  },
  {
    // Same Fed-side legacy invariant.
    query: "SR 11-7",
    expectedAny: ["2.6-model-risk-management-sr-26-2"],
  },
  {
    // Most common customer journey — find the Conditional Access
    // control or its playbook.
    query: "Conditional Access",
    expectedAny: ["1.11/", "1.11-conditional-access"],
  },
  {
    // Acronym-to-canonical: customer types industry shorthand, must
    // land on the canonical model-risk-management page.
    query: "MRM",
    expectedAny: ["2.6/", "2.6-model-risk-management"],
  },
  {
    // Direct natural-language match.
    query: "model risk management",
    expectedAny: ["2.6-model-risk-management-sr-26-2"],
  },
];

async function getSearchInput(page, timeoutMs = 15_000) {
  const visibleInput = page
    .locator('input[data-md-component="search-query"]:visible')
    .first();
  try {
    await visibleInput.waitFor({ state: "visible", timeout: 2_000 });
    return visibleInput;
  } catch {
    const toggle = page.locator('label[for="__search"]').first();
    if (await toggle.count()) {
      await toggle.click();
    }
    await visibleInput.waitFor({ state: "visible", timeout: timeoutMs });
    return visibleInput;
  }
}

async function waitForSearchReady(page, timeoutMs = 15_000) {
  await getSearchInput(page, timeoutMs);
}

async function waitForResults(page, timeoutMs = 15_000) {
  // Material's `.md-search-result__meta` shows "Initializing search"
  // while the worker is loading, then "N matching documents" once
  // results are available. Wait for the "N matching documents" state.
  await page.waitForFunction(
    () => {
      const m = document.querySelector(".md-search-result__meta");
      return m && m.textContent && /\d+/.test(m.textContent) && !/Initializing/i.test(m.textContent);
    },
    { timeout: timeoutMs },
  );
}

async function readTopHrefs(page, n = 5) {
  return await page.evaluate((max) => {
    return Array.from(document.querySelectorAll('a.md-search-result__link[href]'))
      .filter((a) => a.offsetParent !== null)
      .slice(0, max)
      .map((a) => (a.getAttribute("href") || "").replace(/^https?:\/\/[^/]+/, "").split("?")[0]);
  }, n);
}

async function runQuery(page, query) {
  await page.goto("/", { waitUntil: "domcontentloaded" });
  await waitForSearchReady(page);
  const input = await getSearchInput(page);
  await input.click();
  await input.fill(query);
  await waitForResults(page).catch(() => {});
  await expect
    .poll(async () => (await readTopHrefs(page, 5)).length, {
      timeout: 10_000,
      message: `Search did not return visible results for query "${query}"`,
    })
    .toBeGreaterThan(0);
  return await readTopHrefs(page, 5);
}

test(
  "Material Lunr search returns expected pages for customer queries @regression @slow",
  async ({ page }) => {
    test.setTimeout(180_000);
    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    // Warmup: first interaction with Material's search bundle can race
    // against the worker registration. Discard the result; subsequent
    // queries will have a primed worker.
    await runQuery(page, WARMUP_QUERY).catch(() => {});

    const queryFailures = [];

    for (const { query, expectedAny } of TYPED_QUERIES) {
      let topHrefs = [];
      try {
        topHrefs = await runQuery(page, query);
      } catch (err) {
        queryFailures.push(
          `[F-DOCS-SEARCH-CORRECTNESS-UNAUDITED-01] query="${query}" — error: ${err.message}`,
        );
        continue;
      }
      if (topHrefs.length === 0) {
        queryFailures.push(
          `[F-DOCS-SEARCH-CORRECTNESS-UNAUDITED-01] query="${query}" — no results returned`,
        );
        continue;
      }
      const matchFound = expectedAny.some((needle) =>
        topHrefs.some((href) => href.includes(needle)),
      );
      if (!matchFound) {
        queryFailures.push(
          `[F-DOCS-SEARCH-CORRECTNESS-UNAUDITED-01] query="${query}" — top 5 ` +
            `hrefs did not contain any of [${expectedAny.join(", ")}]\n` +
            `  got: ${JSON.stringify(topHrefs, null, 2)}`,
        );
      }
    }

    expect(queryFailures, queryFailures.join("\n\n")).toEqual([]);
  },
);
