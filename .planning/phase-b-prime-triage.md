# Phase B′ Triage — 2026-04-30

## Summary

**6 findings:** 2 P1, 0 P0, 3 P2, 1 N/A.

**Verdict: Loop back to a small Phase D′ fix wave (1 PR touching `overrides/main.html`)
before changelog.** Both P1 findings are real, user-visible CSP defects already
documented by spec 25's `test.fail()` wrapper; both can be fixed in the same file
with a small, surgical change. After that PR merges and spec 25 flips green, ship
v1.4.1 changelog.

## Suite Health Snapshot

- **Full E2E (Chromium, single-worker, local Windows):**
  61 passed, 6 skipped, **2 failed** in 11.6 min
  - Both failures are local-env flakes (see N/A section). The same suite passed
    on CI (Linux, run `25147508066`, 6m05s) on the identical commit `b02fd896`.
- **Smoke (CI):** ✓ 6/6 passed (`E2E Smoke` run `25147508071`, 2m17s)
- **Vitest:** 93 passed / 1 skipped (24s)
- **mkdocs build --strict:** ✓ green (142s)
- **Latest prod-smoke:** ✓ run `25146469469`, ~40 min ago, 1m29s
- **Latest prod-smoke-scheduled:** ✓ run `25144166994`, ~2 hr ago, 48s
- **Latest sri-check:** ✓ run `25142381082`, ~3 hr ago, 16s (matched on Linux runner)

## P0 Findings (must fix before changelog)

_None._

## P1 Findings (fix-or-defer judgment call → **FIX**)

### P1-1: CSP `frame-ancestors` declared via `<meta>` (browser-ignored, clickjacking gap)

- **Source:** PR #163 (spec `25-zero-pageerror.spec.mjs`, defect #2 in PR body)
- **Impact:** `overrides/main.html:11` declares `frame-ancestors 'none'` inside
  the meta-CSP. Chromium logs:
  `directive 'frame-ancestors' is ignored when delivered via a <meta> element`.
  The site has **no clickjacking protection** — any third-party page can iframe
  `judeper.github.io/FSI-AgentGov/` and overlay UI to harvest interactions
  (relevant for an FSI assessment SPA where users enter org names + roles).
- **Proposed fix:** GitHub Pages does not support custom HTTP response headers,
  so move the protection to a runtime JS guard in `overrides/main.html` (or a
  small `<script>` block in the assessment shell):
  ```js
  if (window.top !== window.self) { window.top.location = window.self.location; }
  ```
  This is the well-known frame-busting workaround for static-host scenarios.
  Drop `frame-ancestors` from the meta-CSP (it's silently ignored anyway, so
  removing it is a cosmetic cleanup — but keep it documented in the commit).
  Also update `tests/e2e/fixtures/csp-allowed.json` if needed and **remove the
  `test.fail()` wrapper from spec 25** so the canary returns to fail-loud.
- **Effort:** Small (1 file edit + 1 spec un-wrap).

### P1-2: `api.github.com` blocked by `connect-src 'self'`

- **Source:** PR #163 (spec `25-zero-pageerror.spec.mjs`, defect #1 in PR body)
- **Impact:** mkdocs-material's announce-bar release widget fetches
  `https://api.github.com/repos/judeper/FSI-AgentGov/releases/latest` and
  `…/repos/judeper/FSI-AgentGov` on every page load. Both are blocked by the
  meta-CSP (`connect-src 'self'`), surfacing as console errors and a missing
  release-version pill in the announce bar. Cosmetic but visible to every user.
- **Proposed fix:** Add `https://api.github.com` to `connect-src` in
  `overrides/main.html:11` and to `tests/e2e/fixtures/csp-allowed.json` so the
  CSP allowlist regression spec keeps working. Then remove `test.fail()` from
  spec 25 (same un-wrap as P1-1 — both defects clear together).
- **Effort:** Small (1 file edit + 1 fixture edit + spec un-wrap; same PR as P1-1).

## P2 Findings (defer to next cycle)

### P2-1: SheetJS SRI verifier fails locally on Windows due to CRLF line-ending conversion

- **Source:** Local `node scripts/verify-sheetjs-sri.mjs` run during this triage.
- **Impact:** Windows checkout converts `xlsx.full.min.js` LF → CRLF (881705 →
  881749 bytes), changing the on-disk SHA-256. CI (Linux) sees LF and matches
  the SPA literal; production (also Linux) serves LF and browsers verify SRI
  successfully. **Production is fine; this is purely a Windows-dev annoyance.**
- **Proposed fix:** Add `docs/javascripts/lib/xlsx.full.min.js binary` (or
  `*.min.js binary`) to a `.gitattributes` file so Windows checkouts preserve
  LF for vendored minified JS. Then re-clone or `git rm --cached` + re-add to
  apply.
- **Effort:** Small. Defer; doesn't block changelog.

### P2-2: Markdown export raw-source `**Customer:**` not escape-prefixed

- **Source:** PR #159 commit body (spec `10-export-markdown-formula.spec.mjs`).
- **Impact:** The `**Customer:**` metadata header in the exported `.md` file is
  emitted as raw text. `markdown-it` with `html:false` (the SPA's renderer)
  neutralizes any embedded HTML/JS at render time, so this is **not an XSS
  vector in any rendered context the SPA controls**. Only matters if a
  downstream tool re-renders the file with HTML enabled.
- **Proposed fix:** Apply the same formula/HTML escape pass used for cell
  values to the metadata header lines in the markdown exporter.
- **Effort:** Small. Defer; not user-visible in the SPA itself.

### P2-3: Local E2E flakes — `14-fetch-failure` (offline mid-flow) and `28-perf-budget` (welcome TTI)

- **Source:** Local full E2E run during this triage.
  - `14-fetch-failure.spec.mjs:108` — `TimeoutError` waiting 5s for "Assessment
    Scoping" heading after `dispatchEvent("click")` on Start New Assessment.
  - `28-perf-budget.spec.mjs:42` — welcome TTI 6438ms vs 4000ms budget.
- **Impact:** Both passed on the same commit on CI Linux (run `25147508066`,
  full e2e green in 6m05s). Local Windows machine was simultaneously running
  `mkdocs build --strict` and `npm test`, so resource contention is the most
  likely root cause.
- **Proposed fix:**
  - Spec 14: bump waitFor timeout to 10s and add a `page.waitForLoadState`
    sentinel before the dispatchEvent (defensive against slow boots).
  - Spec 28: keep the current 4000ms budget but consider a longer WIN-only
    multiplier, OR document that local-Windows runs are advisory-only.
- **Effort:** Small. Not blocking — CI is the canonical signal.

## N/A / Already Addressed

### N/A-1: Skipped specs across the suite (6 skips total)

Audited via `Select-String -Pattern "test\.skip|test\.fixme|test\.fail"`.
All 6 skips are documented per the No-Phantom-Coverage policy with clear
re-enable conditions:

| Spec | Lines | Rationale | Re-enable when |
|------|-------|-----------|----------------|
| `04-hash-routing.spec.mjs` | 65, 77, 89 | SPA does not implement hash routing | hash routing ships |
| `12-import-malformed.spec.mjs` | 208 | SPA does not warn on newer `frameworkVersion` | warning ships |
| `15-delegation-handoff.spec.mjs` | 157 | SPA has no `delegated-by` field | provenance field ships |
| `17-mobile-viewport.spec.mjs` | 36 | Defensive guard for missing device profile | always (defensive) |
| `23-mobile-deep.spec.mjs` | 40 | Same defensive guard | always (defensive) |
| `prod-probe.spec.mjs` | 4 | Skipped unless `PROD_URL` env set | running with PROD_URL |

Plus 1 `test.fail` wrapper in `25-zero-pageerror.spec.mjs:45` — this is the
intentional canary documenting P1-1 + P1-2 above. Removed in the same PR that
fixes those.

## Verdict

**Loop back to Phase D′ for one small PR**, then changelog.

The two P1 CSP defects (frame-ancestors not enforced; api.github.com blocked)
are real, user-visible (or user-relevant in the case of clickjacking), share
the same target file (`overrides/main.html` line 11), and are wrapped together
by spec 25's `test.fail()` canary. Fixing both in one PR — and unwrapping spec
25 in the same change — restores the fail-loud canary and ships v1.4.1 with a
demonstrably hardened CSP, not a CSP with two quietly-documented gaps.

P2-1 (Windows CRLF), P2-2 (markdown raw-source), and P2-3 (two local-only
flakes) are all genuinely deferrable: none affect production, none gate the
changelog, and all have clean fix paths for a future cycle.

The Windows-local SRI false-positive (P2-1) was the highest-risk item to
investigate on this triage because it _looked_ like a P0 ("XLSX export broken
in production"). Confirmed false-positive: the SPA's hardcoded SRI literal
matches the LF version of the file (which is what GitHub Pages serves); the
SRI verifier on CI Linux passes (run `25142381082`); end-user XLSX export is
unaffected.

## Action items added to SQL todos

- `triage-fix-csp-meta-defects` (P1-1 + P1-2 combined into one PR)
  - Edge: `changelog-update` depends on it
- `triage-fix-windows-crlf-sri` (P2-1, deferred — pending bucket only)
- `triage-fix-md-rawsource-escape` (P2-2, deferred — pending bucket only)
- `triage-harden-local-e2e-flakes` (P2-3, deferred — pending bucket only)
