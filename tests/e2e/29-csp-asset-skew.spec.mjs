import { test } from "@playwright/test";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { clearPageStorage, expect } from "./_harness.mjs";

/**
 * 29 — CSP allowlist + asset version skew
 *
 * Two reliability nets backed by `tests/e2e/fixtures/csp-allowed.json`
 * (the documented loosenings to a strict 'self' baseline) and
 * `overrides/main.html` (the source of truth for the CSP meta tag).
 *
 *   1. CSP meta is present on the assessment page and contains every
 *      directive declared in the fixture's `directives` table. A new
 *      directive missing from the meta = FAIL (caught CSP regression).
 *   2. Every network response loaded by the page comes from an origin
 *      that the CSP allows: either same-origin (the test server) OR
 *      one of the documented `loosenings` entries. A new origin = FAIL
 *      with an informative message naming the origin and the directive
 *      that should be amended.
 *   3. Asset version skew: the SPA emits `docs/version.json` at build
 *      time. mkdocs-material content-hashes its asset filenames (e.g.
 *      `main.<hash>.min.css`) instead of using `?v=<sha>` query params,
 *      so the historical "?v=sha matches /version.json" check does not
 *      apply to this site. We instead assert that `version.json` is
 *      reachable, parses as JSON, and exposes a `sha` field. A missing
 *      or malformed version.json is itself a CDN-skew red flag.
 */

const here = dirname(fileURLToPath(import.meta.url));
const ALLOW = JSON.parse(
  readFileSync(join(here, "fixtures", "csp-allowed.json"), "utf8"),
);

function allowedOrigins(allowFixture) {
  const set = new Set();
  for (const entry of allowFixture.loosenings || []) {
    const v = String(entry.value || "");
    if (v.startsWith("http://") || v.startsWith("https://")) {
      try {
        set.add(new URL(v).origin);
      } catch {
        /* skip malformed */
      }
    }
  }
  return set;
}

test.describe("CSP allowlist + asset version skew @regression", () => {
  test("CSP meta directives present and every loaded origin is allow-listed @regression", async ({
    page,
    baseURL,
  }) => {
    const expectedOrigin = new URL(baseURL).origin;
    const extraAllowed = allowedOrigins(ALLOW);

    const responses = [];
    page.on("response", (resp) => {
      responses.push({
        url: resp.url(),
        status: resp.status(),
      });
    });

    page.on("dialog", (d) => d.dismiss().catch(() => {}));

    await page.goto("/assessment/", { waitUntil: "domcontentloaded" });
    await clearPageStorage(page);
    await page.reload({ waitUntil: "domcontentloaded" });
    await page
      .getByRole("button", { name: "Start New Assessment" })
      .waitFor({ timeout: 15_000 });

    // (1) CSP meta tag is present.
    const cspMeta = await page.evaluate(() => {
      const m = document.querySelector(
        'meta[http-equiv="Content-Security-Policy"]',
      );
      return m ? m.getAttribute("content") : null;
    });
    expect(cspMeta, "CSP meta tag not found in <head>").toBeTruthy();

    // Every directive from the fixture must be present in the meta.
    const missingDirectives = [];
    for (const directive of Object.keys(ALLOW.directives || {})) {
      // Directive is a token like "script-src" / "default-src". Match
      // the token at the start of a CSP directive (preceded by ";" or
      // start-of-string, then whitespace).
      const re = new RegExp(`(^|;)\\s*${directive}\\b`);
      if (!re.test(cspMeta)) missingDirectives.push(directive);
    }
    expect(
      missingDirectives,
      `CSP meta missing directives: ${missingDirectives.join(", ")}`,
    ).toEqual([]);

    // (2) Origin allowlist. Bucket loaded URLs by origin and assert
    //     each bucket is either the test origin or in the loosenings
    //     allowlist. data: / blob: / about: are not network origins.
    const violations = [];
    for (const r of responses) {
      let originStr;
      try {
        originStr = new URL(r.url).origin;
      } catch {
        continue;
      }
      if (originStr === "null") continue; // data:/blob:
      if (originStr === expectedOrigin) continue;
      if (extraAllowed.has(originStr)) continue;
      violations.push(`${originStr} (loaded ${r.url})`);
    }
    expect(
      violations,
      [
        "Loaded resources from origins NOT on the CSP allowlist:",
        ...violations,
        "",
        "If legitimate, add an entry to overrides/main.html CSP and",
        "tests/e2e/fixtures/csp-allowed.json with a justification.",
      ].join("\n"),
    ).toEqual([]);

    // (3) version.json reachable and well-formed.
    const versionInfo = await page.evaluate(async () => {
      try {
        const r = await fetch("/version.json", { cache: "no-store" });
        if (!r.ok) return { ok: false, status: r.status };
        const j = await r.json();
        return { ok: true, sha: j.sha, builtAt: j.builtAt };
      } catch (e) {
        return { ok: false, error: String(e) };
      }
    });
    expect(versionInfo.ok, `version.json not reachable: ${JSON.stringify(versionInfo)}`).toBe(true);
    expect(typeof versionInfo.sha).toBe("string");
    expect(versionInfo.sha.length).toBeGreaterThan(0);
  });
});
