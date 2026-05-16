# Scorched-Earth Audit Methodology

**Status:** Active — adopted April 2026 after three successive "deep audit" passes failed to find issues that a fourth pass surfaced.

> Internal process doc. Not published to the docs site.

---

## Why this exists

Every prior "deep audit" of this repository was a **deeper sample**, not an enumeration. The same failure mode repeated:

| Pass | What was checked | What was missed | Root cause |
|---|---|---|---|
| Original Monday-readiness | 4 user-facing surfaces (README, site, assessment) | Solutions Bridge wired to nothing; v1.3 footers everywhere | Sampled what a customer would *click*, not what *exists* |
| Post-fix "deep audit" | Top-of-tree docs + framework + controls + 1 shared playbook | 312 per-control playbook footers; 3 AI-config files; advanced-impl page footers | Scope was **assumption-driven** ("where I expect drift to be") not **enumeration-driven** |
| AI-files check | `.github/copilot-instructions.md`, `.claude/CLAUDE.md`, `.claude/skills/verify-ui.md` | Per-control playbooks (3-clicks-deep) | Treated playbooks as second-tier despite customers clicking into them |
| Drift-sweep (this methodology) | All 12 dimensions enumerated | SPA scoring modal "72 controls" string; 16 cells across 6 Excel files; control authoring template still on v1.2 | These were caught — methodology worked |

**Three structural failures we keep making:**

1. **No complete enumeration step.** We list files we expect to be affected, instead of running ONE repo-wide grep for the symptom and triaging EVERY hit.
2. **No classification matrix.** Hits are implicitly "in scope" or "out of scope" — never explicitly **MUST CHANGE / MUST KEEP / FLAG-FOR-HUMAN.**
3. **Single-dimension audit.** We chase one drift symptom (e.g., "v1.3 in footers"). We never ask "what *other* drift dimensions might exist that we haven't grep'd for?"

## The 12 rules

1. **Enumerate, don't sample.** ONE repo-wide grep per symptom. No file lists from memory.
2. **Classify every single hit** into 🔴 MUST-CHANGE / 🟢 MUST-KEEP / 🟡 FLAG-FOR-HUMAN.
3. **Document the classification rule** so a second human can re-run and verify.
4. **Emit a coverage report** before executing: "N hits → X change, Y keep, Z flag."
5. **Execute fixes**, then **re-run the same enumeration** and verify residuals == initial KEEP count.
6. **Open the aperture.** Beyond the obvious symptom, ask: what *adjacent* drift dimensions could exist? List them, grep them, classify them.
7. **Pin a clean baseline first.** Before any bulk operation, prove the pre-state passes validation, so post-state failures aren't misattributed.
8. **Commit isolation.** Group atomic logical units into separate commits so any one can be rolled back without entangling others.
9. **Programmatic diff verification, not statistical spot-check.** Parse `git diff`, assert each change matches the expected transformation. (6 random samples = 4.6% — won't catch correlated regex bugs.)
10. **Autopilot defaults.** When user input unavailable: ambiguous → FLAG_HUMAN + leave alone (conservative). Never bulk-edit a FLAG_HUMAN row. If ≥20% of a dimension is FLAG_HUMAN, refine rules and re-classify.
11. **Honesty over completeness.** Don't bump version claims (e.g., "v1.4 compatible") without positive re-validation evidence. Companion-repo solution version stamps in particular: leave alone unless re-validation evidence exists.
12. **Time budget + ship trigger.** Set a wall-clock budget per phase. On 50% overrun, commit P0+P1 work, document P2 deferred, ship partial. Better a clean partial than incomplete attempt at full.

## Lessons from the April–May 2026 Phase-0 / Phase-3 audit

This section captures hard-won discoveries from the 47-commit `audit/phase-0-red-tests` sweep. Each lesson maps to a specific failure mode that prior "deep audits" missed, paired with the discipline that catches it next time. Citations point at the commit + finding ID that surfaced the pattern.

### Lesson 1 — Static-build cleanliness is not runtime cleanliness

**Pattern:** `mkdocs build --strict` returned green, link checkers passed, the dev console looked quiet. The site loaded in a browser with broken Mermaid blocks, broken diagram downloads, and broken emoji because of CSP denials, CDN URLs hard-coded inside compiled theme bundles, and a `theme: font: false` setting that left orphan font CSP loosenings.

**Why prior audits missed it:** mkdocs only validates *build-time* invariants (broken markdown links, missing nav targets, schema errors). It cannot see script-load failures, CSP violations, or external-CDN denials. Those only manifest when the built HTML is loaded by a real browser against a real CSP.

**Discipline going forward:**

> **Required dimension for any "build clean" claim:** an actual headless-browser crawl over a representative page set, with the Console + Network panels instrumented, before declaring a release shippable. `tests/e2e/31-docs-render.spec.mjs` is the canonical implementation: spawns Playwright against the built site, walks a curated must-cover URL list, fails on any unexpected `pre.mermaid` survivor, CSP violation, or broken diagram href.

**Citations:** AS1 `f9aeb1f3` (Mermaid CDN block — F-MERMAID-CDN-BLOCK-01), AS1B `d28cc825` (twemoji CDN block), AS2 `003d079c` (`exclude_docs: images/` 404'd 64 diagram downloads — F-IMAGES-EXCLUDED-01), AS3 `d8e29e64` (orphan `fonts.*` CSP entries — F-CSP-ORPHAN-LOOSENINGS-01), Phase 0B `687f946d` (the spec itself).

### Lesson 2 — Negative assertions need a positive oracle

**Pattern:** A test that asserts `expect(page.locator('pre.mermaid')).toHaveCount(0)` silently passes on every page that has no Mermaid blocks at all. That is the default state for ~600 of 688 docs pages. The test is tautological for them and only meaningful for the ~30 pages that *should* render Mermaid. Without knowing in advance which pages those are, the assertion provides no signal.

**Why prior audits missed it:** Negative assertions are a familiar test pattern. It is non-obvious that they degrade silently when applied to a heterogeneous corpus.

**Discipline going forward:**

> **Render-expectations oracle:** before running a negative assertion across a corpus, compute a per-page expectation file by walking the source markdown and recording what each page *should* render (number of Mermaid blocks, list of diagram links, list of inline asset references). Test assertions then compare actual vs expected per-page. The oracle regenerates on every test run from source so it cannot drift. See `tests/e2e/render-expectations.json` + the generator wired into Playwright `globalSetup`.

**Citations:** Phase 0A `b263a5d2` (oracle generator), Phase 0B `687f946d` (consumer spec).

### Lesson 3 — RED-before-fix discipline

**Pattern:** It is easy, when fixing a known bug, to write the regression test *against the fixed code*. The test passes immediately and looks healthy. Months later when the underlying mechanism quietly regresses, the test still passes because it was never a falsifiable assertion to begin with — it captures the post-fix shape, not the pre-fix symptom.

**Discipline going forward:**

> **Every regression-guard test lands RED first.** Commit the test against the pre-fix `HEAD`, observe it fail for the right reason in CI, then commit the source fix on top so the same test goes GREEN in the next commit. If the test cannot be made RED against the broken code, the test is probably tautological and needs redesign. The Phase 0 commits (Phase 0A through Phase 0I + M1/M2/M3 + TQ4/TQ5/F1/F3) are the canonical reference: every RED test was committed before its corresponding fix in Phase 3.

**Citations:** AS15b-spec `9af507b5` ("RED-before-fix discipline" called out in the body), AS14 `cea32031` ("RED-before/GREEN-after-same-commit guard mandated by Phase 3 protocol"), Phase 0 commits as a class.

### Lesson 4 — Built-HTML link verifier required (mkdocs page-dir transform quirk)

**Pattern:** Within `docs/playbooks/control-implementations/1.1-foo/portal-walkthrough.md`, a relative link `../1.2-foo/` *appears* correct because both `1.1-foo` and `1.2-foo` are sibling directories in the source tree. MkDocs' link validator is happy. The built site renders the page at `/playbooks/control-implementations/1.1-foo/portal-walkthrough/index.html`, so the browser resolves `../1.2-foo/` to `/playbooks/control-implementations/1.1-foo/1.2-foo/` — a 404.

The bug is invisible to `mkdocs build --strict`: mkdocs sees `../1.2-foo/` from the *source* page and resolves it against the *source* directory, where `1.2-foo/` is a real folder. The page-dir transform that ships with `use_directory_urls: true` only takes effect at build emit time, so the INFO-level "unresolved-link" diagnostic never fires. This shipped silently for months across 22 hrefs in 4 control playbooks (`2.5/powershell-setup.md`, `3.1/powershell-setup.md`, `1.2/sponsorship-lifecycle-workflows.md`, `1.2/troubleshooting.md`) and across other paths under `exclude_docs:`-removed targets.

**Discipline going forward:**

> **Built-site HREF verifier required.** `scripts/verify_doc_links.py` walks every `<a href>` in `site/**/*.html`, resolves it against the actual built filesystem, and exits 1 on any broken target. Wired into `python-quality.yml` after the strict build. Total runtime ~70s for 688 pages on a precomputed valid-paths cache. Treat it as the authoritative internal-link health gate; mkdocs strict alone is insufficient.
>
> **When authoring relative inter-control links from inside a sub-playbook** (any `docs/playbooks/control-implementations/X.Y/<sub>.md`), use the explicit form `../X.Y/portal-walkthrough.md` (or another concrete `.md` target). The bare `../X.Y/` form is broken in production but appears valid to mkdocs.

**Citations:** AS13a `4973b296` (the verifier + 41 broken HREF fixes — F-BUILD-CROSS-PLAYBOOK-DEPTH-BUG-01, F-BUILD-EXCLUDE-DOCS-DEAD-LINK-01, F-CI-GAP-ANCHOR-VALIDATOR-01); commit body explicitly names this the "cross-playbook depth bug".

### Lesson 5 — Engine ↔ SPA contract testing

**Pattern:** The Python assessment engine and the browser-side SPA both score the 78-control framework. They share `assessment/manifest/controls.json` as a data source but have independent scoring code paths. The engine's `load_collected_data()` had never been exercised against the production manifest; it called `manifest.get("controls", [])` which raised `AttributeError` because the production file is a bare 78-element JSON array, not a dict with a `controls` key. The orchestrator pytest had been silently working around the bug since inception by writing a dict-wrapped copy to `tmp_path`.

Separately, the SPA's agenda-Markdown export quietly applied a fake `(percent / 100) * 4` linear conversion to its self-assessed 0–100% score and emitted `**Overall maturity:** 3.0 / 4` — a number whose units did not match either the SPA UI ("Overall Score: 75%") or the engine PDF (which actually computes 0–4 maturity from telemetry). Leadership reading the two reports side-by-side saw two maturity figures in disagreement with no signal that the two sides were measuring different things.

**Why prior audits missed it:** Both code paths had unit tests. Neither side had a contract test that exercised both.

**Discipline going forward:**

> **Two-sided score parity test.** `tests/spa/engine-spa-parity.test.mjs` drives the SPA scorer with the same fixture inputs as the engine pytest, then asserts PASS/FAIL agreement (engine maturity ≥3 ↔ SPA ≥75%). Any divergence in scoring algorithms surfaces as a contract failure.
>
> **Production-manifest reachability test.** `tests/spa/manifest-reachability.test.mjs` + `assessment/tests/test_score.py::TestProductionManifestLoads` BOTH exercise the on-disk production manifest end-to-end. Engine code now has `normalize_manifest_controls()` so the engine accepts both bare-list and dict-wrapped forms.
>
> **Honest scale labels.** Where two scoring systems with different units coexist, every customer-facing surface that emits a score must carry an in-band scale-basis disclaimer. The agenda export now reads "Self-assessed score: N%" with a "Score basis:" disclaimer that names the engine's separate 0–4 scale and tells the reader they are not directly comparable.

**Citations:** AS6 `b6121b7d` (engine manifest normalization — F-MANIFEST-FORMAT-MISMATCH-01), Phase 0F `1ad6f2e5` (parity test), Phase 0G `e5865cfb` (engine pytest), Phase 0H `86edd898` (manifest reachability), AS15d `cdfb3792` (agenda-export honest labelling).

### Lesson 6 — Canonical naming for evolving regulatory references (token-level over proximity rules)

**Pattern:** The OCC's model-risk-management bulletin was renumbered from 2011-12 to 2026-13 (April 2026); the Federal Reserve's SR letter 11-7 was re-issued as SR 26-2 the same week. The previous names persisted in 209+ files across pillar control bodies, per-control playbooks, downloads, the manifest generator, and the assessment SPA. Spot fixes only canonicalized the customer-facing summary surfaces (28 files in AS3'); the long-tail of playbooks remained on the old names until AS11. Even after AS11, 30+ admonition-body shorthand references leaked into the Material Lunr search index because the verifier's admonition carve-out was unconditional. AS15b had to tighten the carve-out to require supersession context before skipping a block.

A naïve guardrail proposal — "allow `OCC 2011-12` if the string `(formerly` appears within 50 characters" — was rejected because proximity rules produce false negatives across line breaks, table cells, and admonition boundaries. The shipped guardrail is **token-level**: every bare reference must be wrapped in an explicit supersession span (`(formerly OCC 2011-12)`) in the same node, OR the entire enclosing block must carry an explicit supersession-context keyword in its body.

**Discipline going forward:**

> **Adopt the "(formerly ...)" convention for renamed authorities** in any body, bullet, or table cell:
>
> - Bare `OCC 2011-12` → `OCC Bulletin 2026-13 (formerly OCC 2011-12)`
> - Bare `SR 11-7` → `Fed SR 26-2 (formerly SR 11-7)`
> - Headings (`#` through `######`): use the short canonical form (`OCC Bulletin 2026-13` / `SR 26-2`) so the TOC stays readable. Drop the formerly-span in headings only.
>
> **Add a CI gate enforcing the convention.** `scripts/verify_regulatory_naming.py` scans the entire `docs/` corpus and fails on any bare reference outside an explicit carve-out. The script imports its skip predicate from the companion `scripts/canonicalize_regulatory_naming.py` so the rewriter and the verifier can never disagree on what counts as off-limits. Carve-outs are conditional: a Material admonition only suppresses the check if the block carries supersession context (`formerly`, `superseded`, `rescinded`, `predecessor`, `supersession`, `superseding`, `rescission`, `rescinding`).
>
> **Prefer token-level guardrails over proximity-window rules.** Proximity rules ("if X within N chars of Y") produce silent false negatives across line breaks, table boundaries, and admonition fences. Token-level rules ("X must be wrapped in a sibling span Y, or the enclosing block must contain keyword Z") are stricter, easier to audit, and survive markdown reflow.
>
> **Watch the search index too.** Material's Lunr indexer treats fenced code as plain text. Templates inside code blocks that quote the old shorthand still surface in customer search results. Treat the built `search_index.json` as a verifier surface in its own right.

**Citations:** AS3'a `370c7364` (28-file canonicalization), AS3'b `bd0b21ec` (verifier), AS10 `30e0132a` (high-traffic surfaces — F-DOWNLOADS-OCC-STALE-01), AS11a `aec519d0` (corpus-wide 201-file sweep + canonicalize script), AS11b `b7aa7ddb` (verifier extended to all of `docs/` — F-CI-GAP-TERMINOLOGY-DRIFT-01), AS15b-spec `9af507b5` (search-index regression spec — F-DOCS-SEARCH-CORRECTNESS-UNAUDITED-01), AS15b-verifier `af0d3884` (admonition carve-out tightened), AS15b-content `fb958ca6` (final 39-file content sweep).

### Lesson 7 — CI path-filter trap

**Pattern:** When AS3'b first added `verify_regulatory_naming.py` to `python-quality.yml`, the path filter was scoped to the original 28-file allowlist (`docs/getting-started/**` plus a handful of explicit reference files). The job would not trigger on any change to `docs/framework/**`, `docs/controls/**`, or `docs/playbooks/**`. A future drift in any of those trees — exactly the surfaces AS11 had to canonicalize a week later — would not have been caught by CI. The narrow filter was caught by a rubber-duck review pass before the workflow shipped.

**Discipline going forward:**

> **When adding a CI gate, ask: "what surface should this gate cover *next year*, not just today?"** A path filter that matches today's affected files is prima facie too narrow if the underlying drift dimension can plausibly appear elsewhere in the future. Default to the broadest correct filter (e.g., `docs/**/*.md` for any docs-content gate); narrow only with an explicit rationale.
>
> Rubber-duck review checklist item: **for every new path filter, ask "what would happen if a future contributor edits a file outside this path that introduces the symptom this gate is supposed to catch?"** If the answer is "nothing", the filter is too narrow.

**Citations:** AS3'b `bd0b21ec` (initial narrow filter), AS11b `b7aa7ddb` (later expanded to `docs/**/*.md`).

### Lesson 8 — The "informational test" anti-pattern, used carefully

**Pattern:** The light-palette docs a11y axe scan (AS5 fix) needed a dark-mode counterpart. Adding the dark-palette scan as a hard CI gate would have immediately failed CI on ~11–25 contrast violations per page across 8 docs pages — all of which warrant their own dedicated dark-mode contrast remediation fix-set, not bundled into AS19. Two failure modes were on the table: (a) skip the test entirely until the fix-set lands (loses test coverage; risk of fix-set never landing), or (b) write the test as a hard gate and leave CI red (blocks all other unrelated PRs).

**Resolution:** the dark-palette test was added as **INFORMATIONAL**: it runs on every CI cycle, writes per-page violation artifacts to `tests/artifacts/a11y-axe/*-dark.json`, and annotates per-page violation counts in test output. The test only fails if the palette-switch infrastructure itself breaks. The discovered violations are tracked under a separate finding ID for the dedicated remediation fix-set.

**Discipline going forward:**

> **The `INFORMATIONAL` mode is a legitimate trade-off, but only under three conditions:**
>
> 1. The test would generate immediate, known-real failures that warrant a separately-scoped fix-set.
> 2. The discovered violations are tracked in the findings register under a distinct finding ID so they cannot be lost.
> 3. The test artifacts (per-page JSON, screenshots, etc.) are persisted on every run so the next fix-set has a baseline to work against.
>
> The test stays in the suite (so the *coverage* won't drift), but it does not turn CI red on already-known violations. When the dedicated fix-set lands, flip the assertion from informational to BLOCKING in the same commit that closes the finding.
>
> Anti-pattern to avoid: marking a test informational because the assertion is *flaky*. Flaky assertions need to be fixed or removed; they do not qualify for informational mode.

**Citations:** AS19b dark-palette test (staged on `audit/phase-0-red-tests`); finding `F-A11Y-DARKMODE-VIOLATIONS-01` deferred to AS21.

### Lesson 9 — Multi-purpose CSS class hazard

**Pattern:** AS18a's print-mode fix removed `.ag-disclaimer` from the `@media print` hide-list so the legal caveat ("does not constitute a compliance certification") would appear in archived PDFs. The change *looked* like a one-line fix. Investigation revealed the `.ag-disclaimer` class has FOUR use-sites in `assessment-app.js`:

- L2051: results dashboard legal disclaimer (the original target)
- L3089: Phase 2 reminder
- L3299: results-page Phase 2 prompt
- L4235: trend-comparison validation error

Removing the print-hide rule applied the change to all four. Two of the non-target use-sites are contextually defensible in print (Phase 2 reminders explain a section). One (the validation error) only renders on bad upload — unlikely to be in print scope but possible. The decision to ship the change to all four was deliberate, but it required visiting every use-site to confirm.

**Discipline going forward:**

> **Before changing any CSS class rule, enumerate every use-site of that class** (markup + selectors). For multi-purpose classes, the change must be evaluated against each use-site independently. Ship the broad change only if every use-site is acceptable; otherwise scope the change with a use-site-specific selector (e.g., `.ag-disclaimer.ag-legal`) and refactor the markup so the targeted use-site has the discriminating class.
>
> When the broad change is acknowledged-acceptable across all use-sites, add an explanatory comment in the CSS so future maintainers don't read it as oversight.

**Citations:** AS18a `32b7827c` (the print-mode disclaimer fix; commit body enumerates the 4 use-sites and explains why the broad change was deliberate).

### Lesson 10 — Material 9.x is in maintenance mode (forward risk)

**Pattern:** The framework runs MkDocs Material `9.7.6`. Material 10 is upcoming. Several Phase 3 fixes had to override Material internals (the Mermaid CDN intercept in `overrides/main.html`, the `partials/copyright.html` fork for path-portable footer links, the task-list a11y shim that subscribes to Material's `document$` observable, the OG/Twitter meta block in `extrahead`). Each of these is pinned to Material 9.x behavior; a major Material upgrade may invalidate any of them.

**Discipline going forward:**

> **Pin every Material override with a version banner.** Each file under `overrides/` should carry a comment header naming the Material version it was forked from, and a one-line statement of what about Material's behavior the override depends on. When a Material major upgrade lands, grep `overrides/` for the banner to drive a re-review.
>
> **Audit-register an explicit "Material 10 readiness" line item.** The overrides currently in scope:
>
> - `overrides/main.html` — Mermaid CDN intercept (relies on `Element.prototype.appendChild` patch firing before Material's bundle.js dynamic script append) AND OG/Twitter meta in `extrahead` (relies on `{% if page %}` guard for 404.html where `page=None`).
> - `overrides/partials/copyright.html` — fork that emits the disclaimer link via Material's `url` Jinja filter.
> - `docs/javascripts/a11y.js` — subscribes to Material's `document$` `BehaviorSubject` for `navigation.instant` re-application.
> - `mkdocs.yml` — `theme.font: false`, `emoji_generator: pymdownx.emoji.to_alt` are explicit overrides of Material defaults.
>
> Watch for Material 10 release notes touching: `navigation.instant` lifecycle, Mermaid integration (CDN URL stops being interceptable), the `social` plugin being enabled by default (would duplicate our OG/Twitter meta), or any `partials/copyright.html` reshape.

**Citations:** AS1 `f9aeb1f3`, AS3 `d8e29e64`, AS12 `affd006c`, AS14 `cea32031`, AS16 `1690efcd`, AS1B `d28cc825`.

### Lesson 11 — Integration-test the customer entry point, not just its libraries

**Pattern:** The documented customer entry-point is `assessment/run-assessment.ps1`. Engine pytest only invoked `score.py` and `report.py` directly via `subprocess.run(...)` with a `_subprocess_env()` helper that set `PYTHONIOENCODING=utf-8`. The orchestrator was never run end-to-end during testing. Result: **four distinct customer-impacting P0 defects shipped** for months, each invisible to the library-level pytest suite:

- StrictMode crash on the empty `$collectorJobs` pipe — `($collectorJobs).Count` is a runtime error in `Set-StrictMode -Version Latest` when the pipeline is empty.
- BOM read/write mismatch — collectors wrote UTF-8 with BOM via `Set-Content`, the engine read UTF-8 sans-BOM via Python's default decoder, and the BOM bytes leaked into the first JSON key.
- cp1252 stdout encoding — the orchestrator inherited the parent process's cp1252 console encoding so any non-ASCII byte from the engine (`✓`, `→`, `≥`) crashed the orchestrator with `UnicodeEncodeError`.
- `OrderedDictionary.ContainsKey(...)` vs `.Contains(...)` — `[ordered]@{}` exposes `Contains`, not `ContainsKey`. Library tests that use plain hashtables never hit this path.

The library tests were green throughout. Each library function in isolation worked. The orchestrator wiring on top did not.

**Why prior audits missed it:** The pytest harness exercised the *callable units* (score, report) but never composed them through the customer's documented entry script. It was structurally incapable of detecting orchestrator-only defects (PowerShell strict-mode behaviour, cross-process encoding, cross-language byte handling, .NET collection-API drift).

**Discipline going forward:**

> **For any customer-documented entry point, integration-test the entry point itself, not just the libraries it composes.** Add to CI a "smoke" job that drives the customer entry point with the simplest possible input (e.g., `assessment/run-assessment.ps1 -SkipCollectors -Zone 2 -CustomerName Smoke` against `assessment/tests/fixtures/`) and asserts exit code 0 + every documented output file exists + each contains the framework version string. This is cheaper than fixing four P0s discovered in production.
>
> Generalize: **if you have an orchestrator + libraries pattern, your unit tests of the libraries don't tell you whether the orchestrator works. Integration-test the orchestrator.** The orchestrator-only failure modes (strict-mode pipeline behaviour, console encoding, cross-language byte handling, collection-API drift between hashtable and ordered-dictionary) are structurally invisible to library-level tests.

**Citations:** AS-ORCH-FIX cascade in Phase 4D (4 P0s closed in single integration-test pass: StrictMode + empty-pipe-Count, BOM read/write mismatch, cp1252 stdout encoding, OrderedDictionary.ContainsKey vs .Contains); plan v3.x rubber-duck #9 ("Orchestrator smoke" — drive the real customer path against fixture data and assert all five reports generate).

### Lesson 12 — Subpath / deploy parity probe

**Pattern:** Local development serves the built site at `http://127.0.0.1:8765/` via `python -m http.server site/`; production serves at `https://judeper.github.io/FSI-AgentGov/`. Anything that depends on the deploy base path (the mkdocs `copyright` field, hard-coded `/FSI-AgentGov/...` hrefs, theme assets resolving against `<base>`) renders correctly locally and 404s in production. The footer disclaimer link `<a href="/FSI-AgentGov/disclaimer/">` worked in production but 404'd in every local Playwright run; nobody noticed because no spec asserted on footer links from the local mount.

**Why prior audits missed it:** the entire test pipeline runs against the root mount. The subpath-only failure surface is structurally invisible to a root-mount test suite.

**Discipline going forward:**

> **Mount the built site under the production subpath for at least one Playwright pass per release.** Recipe:
>
> ```powershell
> New-Item -ItemType Directory -Force _subpath/FSI-AgentGov | Out-Null
> Copy-Item -Recurse -Force site/* _subpath/FSI-AgentGov/
> python -m http.server --directory _subpath 8001
> ```
>
> Then point Playwright `baseURL` at `http://127.0.0.1:8001/FSI-AgentGov/` and re-run the must-cover render spec. Add as a gated CI variant or a manual-dispatch workflow; the cost is one extra Playwright pass.
>
> A complementary **production parity probe** (`tests/e2e/prod-probe.spec.mjs`) hits the live deployed URL after each `publish_docs.yml` run with a stripped-down render spec. Together the two cover (a) what production *will* serve once the next push lands and (b) what production is *currently* serving.

**Citations:** F-DEPLOY-COPYRIGHT-PATH-01 (`/FSI-AgentGov/disclaimer/` 404 against root mount), AS14 `cea32031` (subpath fixture commit), F-DEPLOY-WORKFLOW-NO-EXPLICIT-BASEURL-01 (`gh-deploy --force` with no explicit `--site-url` — defense-in-depth gap).

### Lesson 13 — CSP fixture atomicity

**Pattern:** The site's Content Security Policy is declared in three places that must agree: `overrides/main.html` (the meta tag the browser actually enforces), `tests/e2e/fixtures/csp-allowed.json` (the test-suite expectation, used by every render and asset-skew spec), and any per-spec assertion that expects a particular directive. Three Phase-3 commits silently shipped a CSP loosening in `overrides/main.html` without updating the fixture, which made the fixture's "expected directives" the *pre-loosening* set; subsequent render specs passed because they checked subset-of-allowed, not equality. A fourth commit went the other way — tightened the fixture without touching `overrides/main.html` — and the next CDN-blocked release made it through CI because no spec compared the meta tag against the fixture.

**Discipline going forward:**

> **Any change to CSP must update `overrides/main.html` AND `tests/e2e/fixtures/csp-allowed.json` AND any spec expectations in the same commit.** Treat the three artifacts as a single atomic unit. Add a pre-commit hook (or a Phase 0 RED test) that diffs the meta-tag directives against `csp-allowed.json` and fails on mismatch — drift between fixture and source is the actual bug, regardless of which side moved.
>
> Code-review checklist item for any commit touching `overrides/main.html`: confirm `csp-allowed.json` was edited in the same commit, OR the diff explicitly justifies why CSP is unchanged.

**Citations:** AS3 `d8e29e64` (initial fixture sync), AS1 `f9aeb1f3` (Mermaid CSP intercept that needed coordinated fixture update), AS1B `d28cc825` (twemoji CDN block — CSP-fixture sync done atomically only after the cascade was identified).

### Lesson 14 — Inverse CSP orphan check

**Pattern:** Every `style-src`, `script-src`, `font-src`, `connect-src` entry in `csp-allowed.json` exists because some asset was supposed to load from it. When an asset stops loading (CDN dropped, theme setting changed, plugin removed), the loosening becomes an orphan: the CSP is wider than it needs to be, but every page still renders fine because nothing was trying to use the loosening anyway. The test suite stays green; the threat surface stays expanded. `mkdocs.yml`'s `theme.font: false` removed all Google Fonts loads, but `fonts.googleapis.com` (style-src) and `fonts.gstatic.com` (font-src) stayed in `csp-allowed.json` for months. `api.github.com` (connect-src) was added speculatively for a feature that never shipped.

**Discipline going forward:**

> **Inverse-orphan CSP check.** Run a Playwright pass that records every Content-Security-Policy-relevant request the browser actually made (network log + reported CSP violations). Diff the observed origin set against `csp-allowed.json`. Any allowlist entry with **zero** corresponding requests across the must-cover URL set is an orphan loosening — flag for removal.
>
> The check is the inverse of the standard CSP-violation check: the standard check fails when a request is **denied** that should be allowed; the inverse check fails when an allowance is **unused**. Both are needed. Removing dead loosenings is a low-risk way to tighten the threat surface; the tests prove no production page actually needs them.

**Citations:** F-CSP-ORPHAN-LOOSENINGS-01 (`fonts.googleapis.com` + `fonts.gstatic.com` orphaned by `theme.font: false`), AS3 `d8e29e64` (orphan removal commit).

### Lesson 15 — Sampling violates the methodology for repo-wide claims

**Pattern:** This methodology already opens with a four-row table of prior "deep audits" that missed P0s by sampling instead of enumerating. The April–May 2026 audit added a fifth row by accident: AS3' shipped a 28-file regulatory-rename canonicalization that "seemed sufficient" because all sampled high-traffic surfaces were clean. AS10 then found the same drift on `docs/downloads/index.md` (a high-traffic landing page that wasn't in the sample). AS11 then found 201 more files corpus-wide. AS15b then found 39 files that AS11 missed because the verifier's admonition carve-out was unconditional. **Four sampling passes; a fifth surfaced the residual.** The right move on day one would have been the corpus-wide rewrite + verifier (AS11 + AS15b combined), not three iterations of "I'll just fix the obvious ones first".

**Discipline going forward:**

> Reinforces existing rule 1 (Enumerate, don't sample) and the four-row failure table at the top of this document. **For any change class that could plausibly appear in ≥3 file types or ≥3 directories, enumerate the entire corpus on day one. Do not ship a sampled subset and tell yourself the long tail can wait — the long tail compounds and surfaces as more P0s.**
>
> Concrete rule: if a fix-set's "files changed" count is materially smaller than the result of a corpus-wide grep for the same symptom, the fix-set is incomplete by definition. Run the grep before commit, not after.

**Citations:** AS3'a `370c7364` (28-file pass), AS10 `30e0132a` (next round, F-DOWNLOADS-OCC-STALE-01), AS11a `aec519d0` (corpus-wide 201-file rewrite), AS15b-content `fb958ca6` (final 39-file residual after the verifier carve-out was tightened).

## When to invoke this methodology

**USE for:**
- Version bump (e.g., v1.3.x → v1.4.0)
- Count change (e.g., 71 → 78 controls, 33 → 35 solutions)
- Structural rename (folder, schema field, template)
- Any repo-wide claim ("all controls", "every page", "100% coverage")
- **Any change that touches the runtime browser surface** (CSP, vendored JS/CSS, theme overrides, `mkdocs.yml` extension toggles, emoji or font configuration). The cost of a Playwright must-cover crawl is ~30s on a built site; the cost of shipping a CSP-blocked render to production and discovering it from a customer report is days. *(Added Phase 4C — see Lessons 1, 13, 14.)*
- **Any change to a customer-documented entry script** (e.g., `assessment/run-assessment.ps1`) or to its inputs (`controls.json`, fixture data, manifest schema). Run the orchestrator smoke end-to-end before commit; library pytest is not sufficient. *(Added Phase 4C — see Lesson 11.)*

**Do NOT invoke for:**
- Single-file fixes
- Typo passes
- Content additions to a known location

**Threshold rule:** If the symptom could plausibly appear in ≥3 file types OR ≥3 directories, invoke this methodology. Otherwise direct edit is fine.

## Standard drift dimensions

Dimensions A–L are the original 12 (April 2026). Dimensions M–Q were added Phase 4C (May 2026) — see Lessons 1, 11, 12, 13, 14.

| Dim | Name | Symptom regex | Notes |
|---|---|---|---|
| A | Version stamps | `v1\.[0-3](\.\d+)?` | Exclude `CHANGELOG-v1.[0-3].md`, `package-lock.json`, `node_modules/`, `site/`, `releases/` |
| B | Solution count | `\b(28\|33\|35)\s+(live\s+)?solutions?\b` | `35 live = 35 lock entries` is consistent (preview-placeholder concept retired in v1.4.0) |
| C | Control count | `\b(71\|72)[\s\-]+controls?\b` | Historical changelog rows are MUST_KEEP; check live docs |
| D | Year/month stamps | `v1\.4\.0[\s\-—\|]+(NotApril)\s+2026` | Catches footer date mismatches |
| E | Manifest field completeness | Programmatic JSON walk for empty fields | Catches "wired-to-nothing" patterns like Solutions Bridge |
| F | Lock file cross-consistency | Diff `solutions-lock.json` keys vs companion-repo folders | Catches added/removed solutions out of sync |
| G | Excel templates | openpyxl walk over `docs/downloads/*.xlsx` for v1.3 / 71 / 72 | AMWINS downloads these |
| H | Workflow / CI files | Grep `.github/workflows/*.yml` for v1.3 + counts | Catches CI depending on stale paths/versions |
| I | Top-level meta files | Grep root `*.md` for v1.0-v1.3 | README, AGENTS.md, CONTRIBUTING — historical changelog table is OK |
| J | Companion repo cross-refs | Grep companion repo for "v1.3 framework" | **AUDIT-ONLY by default per rule 11** — bumping requires positive re-validation |
| K | Schema / template files | `docs/templates/**/*.md` | Affects future content — P1 not P0 |
| L | Assessment SPA | `docs/javascripts/assessment*.js`, `docs/stylesheets/assessment.css`, `overrides/main.html` | Customer-visible, P0 |
| M | Browser-runtime render | n/a (use Playwright crawl) | mkdocs strict + link-check do not see CSP denials, CDN blocks, or shadow-DOM render failures. `tests/e2e/31-docs-render.spec.mjs` is the canonical implementation; the must-cover URL list is curated to include the widest-Mermaid pages plus one of each major doc type. |
| N | Orchestrator end-to-end | n/a (drive `assessment/run-assessment.ps1 -SkipCollectors`) | Library-level pytest cannot see strict-mode pipeline behaviour, console encoding, BOM mismatches, or `[ordered]@{}` API drift. Drive the documented customer entry point against fixture data; assert exit code 0 + all documented outputs generated. |
| O | Subpath / deploy parity | n/a (mount `site/` under `/FSI-AgentGov/`) | Root-mount tests miss any href that hard-codes the deploy subpath. Add one Playwright pass per release that mounts under the production subpath; complement with `prod-probe.spec.mjs` against the live URL. |
| P | CSP fixture / source coherence | diff `overrides/main.html` meta-tag directives vs `tests/e2e/fixtures/csp-allowed.json` | Drift between the enforced CSP and the test-suite expectation is the actual bug; the test suite goes green either way. Pre-commit / RED test catches it. |
| Q | CSP orphan loosenings | inverse Playwright crawl: every allowlist entry with zero observed requests | Removed CDNs, retired plugins, and false-start integrations leave dead `csp-allowed.json` entries that widen the threat surface. Inverse check tightens it. |

Path verification BEFORE running any dimension: actual paths drift over time (e.g., SPA may move from `docs/assessment/` to `docs/javascripts/`). Always `Test-Path` / `Get-ChildItem` first.

## Workflow checklist

```
[ ] Phase 0: Pin clean baseline (mkdocs build --strict on pre-state)
[ ] Phase 1: Enumeration sweep — grep each dimension, count hits, classify TRIVIAL/MEDIUM/LARGE
[ ] Phase 2: Per-dimension classification — write findings file with rule documentation
[ ] Phase 3: Coverage report — N hits → X change, Y keep, Z flag (gate to execution)
[ ] Phase 4: Execute MUST_CHANGE fixes, atomic commit per dimension
[ ] Phase 5: Re-run grep, verify residuals == MUST_KEEP count
[ ] Phase 6: Single push at end (Pages throttle protection), monitor deploy, verify live
[ ] Phase 7: Update flag-for-human file with un-fixed items
[ ] Phase 8: Built-site link integrity (verify_doc_links.py — 0 broken HREFs across all built pages)
[ ] Phase 9: Browser-runtime crawl (Playwright must-cover render + a11y axe + CSP orphan detection)
[ ] Phase 10: Orchestrator smoke (drive customer entry script -SkipCollectors against fixtures; assert exit 0 + outputs exist)
[ ] Phase 11: Subpath parity (mount under /FSI-AgentGov/ for one Playwright pass; prod-probe against live URL after deploy)
```

Phases 8–11 were added Phase 4C (May 2026). Phase 8 runs after `mkdocs build --strict` (Phase 0). Phases 9–11 run after the per-dimension re-grep (Phase 5) and are the last gates before push.

## Findings file template

Per-dimension findings live in session workspace as `audit-dim-X.md`:

```markdown
# Dimension X — <Name>
**Total hits:** N | **MUST_CHANGE:** X | **MUST_KEEP:** Y | **FLAG_HUMAN:** Z

**Classification rules:**
- 🔴 MUST_CHANGE: <explicit pattern>
- 🟢 MUST_KEEP: <explicit allowlist patterns>
- 🟡 FLAG_HUMAN: <ambiguity criteria>

| File | Line | Match | Class | Priority | Action | Status |
|---|---|---|---|---|---|---|
```

## Priority levels

Every finding gets P0 / P1 / P2:

- **P0** = Customer-visible immediately (live site, assessment SPA, README, downloadable artifacts)
- **P1** = Will be visible eventually (templates, advanced-impl pages, schemas)
- **P2** = Internal only (CI, scripts, AI config history lines, audit reports)

Only P0 + P1 must ship before customer-facing milestones. P2 can defer.

## Session ownership

If this methodology is being run as part of a GSD workflow, see `.github/instructions/session-ownership.instructions.md`. Findings files (`files/audit-*.md` in session workspace) are safe to write; shared state files (`.planning/STATE.md`, `ROADMAP.md`) require ownership claim.
