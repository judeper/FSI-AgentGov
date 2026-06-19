# Changelog

All notable changes to the FSI Agent Governance Framework are documented here, organized by major version.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

<!--start-->

## [Unreleased]

### Added
- **Autodoc scheduler + activation runbook (Phase 3 — pipeline complete).** `scripts/Register-AutodocTask.ps1` registers the daily Windows Scheduled Task that runs the unattended runner (pruning stale worktrees first; PSScriptAnalyzer-clean). The maintainer runbook `.github/AUTODOC-RUNBOOK.md` is finalized: full component table, the **two `AUTODOC_ENABLED` switches** (the local env var that gates the runner vs the repo variable that gates the CI verify gate / F5), end-to-end provisioning (Copilot CLI EMU login, `judeper` git creds, register task, set both switches), operations (disable/inspect/dry-run, stale-worktree cleanup, escalation), and a **portability** section for onboarding `FSI-CopilotGov` / `FSI-CopilotGov-Solutions` (via per-repo `autodoc_route` allowlists and the `AUTODOC_REPO` env var). The published description (`docs/reference/learn-monitor-ai-enhancement.md`) is flipped to *implemented*. With this, the local-CLI pivot is complete; the pipeline remains **off by default**.
- **Unattended autodoc runner (`scripts/autodoc_runner.py`).** Phase 2 of the local-CLI pivot — the orchestration engine. On a schedule it reads the latest Learn Monitor report, routes each change (`autodoc_route`), and for every *autodraft* change: drafts a minimal doc edit with the GitHub Copilot CLI (headless), gates it through the deterministic verifier (`autodoc_verify_gate`) **and** the independent cross-model review (`autodoc_cli_review`, a different Copilot model family), and — only when both pass — opens a pull request for a **human** to merge. Failures retry a bounded number of times (`autodoc_retry.decide`, default 2) then escalate to a human; *human*-routed changes are never drafted (escalation issue only); per-change failures are fault-isolated; idempotent via the `data/autodoc-ledger.json` fingerprint ledger. Off by default — `run()` is a no-op unless `AUTODOC_ENABLED=true`. All side effects (draft/verify/review/git/PR/escalate) are isolated module functions so the orchestration is unit-tested by monkeypatching; covered by `scripts/test_autodoc_runner.py` (25 tests: combine-conclusion matrix, contract extraction, both-pass→PR, draft-needs-human/empty-diff→escalate, deterministic-needs-human→escalate, retry-then-succeed, exceed-fix-cycles→escalate, review-fail→escalate, base-branch restoration, disabled no-op, human-route escalation, fault isolation).
- **Independent cross-model autodoc reviewer (`scripts/autodoc_cli_review.py`).** Phase 2 of the local-CLI pivot: the faithfulness check that replaces the retired third-party LLM verifier. It re-reviews a drafted doc edit with a **different GitHub Copilot model family** (passed via `--model`) so the author never grades its own work, treating the Learn change report as source-of-truth and the diff's added lines as the claims to verify. The single Copilot CLI call is isolated behind a mockable runner; everything fails **closed** — an exec failure yields `needs_human`, any malformed/non-conforming model output yields `fail` (never a silent `pass`). The reviewer runs with `write`/`shell` tools denied so it cannot mutate the repo. Covered by `scripts/test_autodoc_cli_review.py` (17 tests: prompt assembly, tolerant JSON extraction, fail-closed coercion, runner mocking, exit codes).
- **Autonomous Learn Monitor documentation pipeline — workflow layer (Stage 1, opt-in).** Wires the merged scaffolding into a runnable, fail-closed, human-merge-gated pipeline, **off by default** (`AUTODOC_ENABLED` repo variable): `scripts/autodoc_route.py` (classify the latest Learn report → an authoring contract per change, fingerprint-idempotent via `data/autodoc-ledger.json`); `autodoc-verify.yml` + `scripts/autodoc_verify_gate.py` (shim-aware required check running the deterministic verifier, hardened `pull_request_target`, fails closed); bounded retry/escalation decision logic in `scripts/autodoc_retry.py`. Maintainer operations + provisioning in `.github/AUTODOC-RUNBOOK.md`; published description updated in `docs/reference/learn-monitor-ai-enhancement.md`. The F5 baseline-deferral ledger (advance the monitor baseline only when the downstream doc task is terminal) is implemented and gated off (`scripts/autodoc_defer.py`, `scripts/autodoc_advance.py`, `.github/workflows/learn-monitor-advance.yml`) — a byte-identical no-op unless `AUTODOC_ENABLED=true`. Each piece independently reviewed (cross-family owl-mode) before merge.
- **`.github/CODEOWNERS` — human review gate for compliance-sensitive paths.** Names `@judeper` as required reviewer for customer-facing compliance content (`docs/controls/`, `docs/reference/`, `docs/framework/`, `docs/playbooks/`, `mkdocs.yml`), the control manifest, and the autonomous-pipeline safety machinery (`scripts/autodoc_*.py`, workflows). Scaffolding for the autonomous Learn Monitor pipeline's human-merge gate (Stage 1). Note: this becomes an *enforced* gate only once branch protection on `main` is set to "Require review from Code Owners" (a tracked admin prerequisite — `main` currently requires 11 status checks but no code-owner review).
- **Deterministic, fail-closed autodoc routing classifier (`scripts/autodoc_classifier.py`).** First component of the autonomous Learn Monitor documentation pipeline (Stage 1). Parses a Learn Monitor change report and decides, per change, whether it is mechanically safe for an agent to *draft* a doc edit (`route="autodraft"`, human still merges) or must be analyzed by a human (`route="human"`), plus a much stricter `automerge_eligible` flag for a future Stage 2. The decision is deterministic (no LLM) and fail-closed: regulatory citations, dates/deadlines, retention durations, license SKUs, deprecations, policy language, overclaim words, and any edit to existing control prose always route to a human, regardless of the monitor's own (noisy) CRITICAL/HIGH/MEDIUM tier. Covered by 20 unit/integration tests (`scripts/test_autodoc_classifier.py`) including real report fixtures. Implements the June 2026 council review's top finding (the form-vs-meaning classifier gap).
- **Autodoc canary / poison-pill guard (`scripts/autodoc_canary.py`).** A standing safety guard that feeds deliberately bad changes (hallucinated citation, fabricated retention duration, overclaim, deprecation, license-SKU change, control-prose edit, CRITICAL tier, future deadline) through the routing gate and fails loudly (exit 1) if any is mis-promoted for unattended handling — the deterministic half of the "who verifies the verifier" control. Extension point reserved for the future cross-vendor LLM verifier. Covered by `scripts/test_autodoc_canary.py`.
- **Control 2.27 — Consumption-Entitlement Governance (Pillar 2 — Management).** New framework control governing *who is entitled to consume metered and premium Microsoft Copilot capabilities* — enforcing a switch-on-pathway entitlement contract per agent consumption pathway, applying per-agent spend caps, and running a pre-enforcement coverage-gap ("who would be blocked") analysis before any spend control is activated. Pairs with Control 3.5 (cost reporting) and is distinct from Control 2.26 (agent identity governance) and Control 1.18 (functional RBAC). Documents the companion `copilot-billing-governance` solution's entitlement contract. Catalog expands from 78 to 79 controls (Pillar 2 from 26 to 27). Added to `assessment/manifest/controls.json`, `CONTROL-INDEX.md`, `mkdocs.yml`, and the Pillar 2 index; the four implementation playbooks are tracked as follow-up work. Resolves #440.
- Consolidated 9 Learn Monitor daily drift reports (2026-05-27 through 2026-06-04) from bot PRs #343–#383 into main via consolidation PR #385. Superseded PRs closed; `data/monitor-state.json` updated to newest cumulative state.

### Fixed
- **Redirect changes can now pass the verifier (`scripts/autodoc_route.py`).** Redirect autodrafts edit `docs/reference/microsoft-learn-urls.md`, whose section headings are topic names (`Copilot Studio`, `Microsoft Purview`, …) — not the generic *control* headings the contract assigned, so the deterministic verifier's `section_allowlist` check blocked every redirect edit and they always escalated. The redirect contract now sets `allowed_headings` to the **target file's own headings** (extracted with the same markdown-it-py oracle the verifier uses, so they match exactly); the other five checks (path-allowlist, diff-minimality, claim-support, FSI language, fingerprint) still gate the edit. Fails closed if the file can't be read. Surfaced by a controlled live dry-run.
- **Autodoc runner draft timeout too tight (`scripts/autodoc_runner.py`).** A live Opus draft exploring a fresh ~1,280-file worktree can take 10+ minutes; the 600s default timed out mid-draft (the same change completed under 600s on another run — it sits right at the boundary). Raised the default draft timeout to 1200s (review to 300s) and exposed `--draft-timeout` / `--review-timeout` CLI flags for tuning. Surfaced by the second controlled dry-run.
- **Autodoc runner worktree cleanup (`scripts/autodoc_runner.py`).** The per-change `finally` cleanup ran `git checkout --force main` inside the disposable linked worktree, which git rejects with `fatal: 'main' is already used by worktree …` (exit 128) because the base branch is checked out in the primary worktree. It now detaches (`git checkout --force --detach main`). Found by the first controlled live dry-run (mocked unit tests stub `git`, so they could not surface it); the draft → deterministic verify → cross-model review path itself worked end-to-end.
- Replaced non-rendering Material shortcode markup on the homepage quick-start cards (`docs/index.md`) with plain text labels so GitHub Pages no longer displays literal `:material-*:` tokens.

### Changed
- **Redirect changes are handled deterministically, with no LLM (`scripts/autodoc_runner.py`).** A URL redirect is a mechanical string swap, and the URL list (`microsoft-learn-urls.md`) stores entries as table rows (`| Title | URL | Date |`) — so an LLM draft + prose verifier was the wrong tool (it failed `claim_support` because swapping the URL marks the whole row's title/date as unsupported "new claims"). The runner now detects redirect changes and applies the exact `source_url`→new-URL replacement itself, verifies the staged diff is a **clean URL-only swap** confined to the URL list, and opens a human-merge PR — escalating if the URL isn't found, the new URL is already present, the swap isn't clean, or the URLs can't be parsed. In a live dry-run this took **~6 seconds** and reached `pr_opened` (vs ~13 min of flaky LLM drafting that always escalated). No cross-model review is needed (there's no model output to review).
- **Autodoc draft + review are faster and Windows-safe (`scripts/autodoc_runner.py`, `scripts/autodoc_cli_review.py`).** The draft now inlines the current content of the allowed file(s) (capped at 60 KB each) into the prompt and tells the model not to explore the rest of the worktree — cutting a live Opus draft from ~18 min to ~3 min per attempt. Both the draft and the review now pass their (potentially large) prompt to the Copilot CLI via **stdin** instead of a `-p` argument, avoiding the Windows command-line length limit (`WinError 206`). Found while validating the pipeline with controlled live dry-runs.
- **Autodoc pipeline pivots from GitHub's cloud coding agent to a local, unattended GitHub Copilot CLI drafter.** GitHub's cloud coding agent cannot drive this pipeline on these repositories: the enterprise Copilot license lives on an EMU account that is barred from the public personal repo, and GitHub disallows cloud-agent **automations on public repositories**. The drafter is therefore the GitHub Copilot CLI itself (the EMU license provides reasoning; the `judeper` token performs all repo writes — independent auths), run headless on a schedule, with independent review performed by a **different Copilot model family** rather than a third-party API. **Phase 1 of the pivot (this change):** retires the cloud-agent workflows (`learn-autodoc-route.yml`, `autodoc-fix-retry.yml`) and the Anthropic LLM verifier (`scripts/autodoc_llm_verify.py`), and makes the `autodoc-verify.yml` CI gate **deterministic-only** (drops the `ANTHROPIC_API_KEY` dependency). Routing (`autodoc_route.py`), the deterministic verifier, the canary, the retry/escalation decision logic, and the F5 ledger are all retained. The pipeline remains **off by default** (`AUTODOC_ENABLED`).
- **Learn Monitor PRs now self-consolidate and auto-merge (Stage 0 monitoring hardening).** `.github/workflows/learn-monitor.yml` gained two steps after PR creation: (1) close older bot-created `monitoring/learn-<n>` PRs as superseded (the newest carries the cumulative `data/monitor-state.json` baseline), and (2) enable squash auto-merge on the new PR once the required checks pass. Safety constraints: PR creation uses `add-paths` so the branch can only contain `data/monitor-state.json(.backup)` and `reports/monitoring/**`; auto-merge re-validates that every changed file matches that allowlist (else it labels `needs-review` and skips); consolidation closes only PRs carrying the `learn-watch` label, matching the exact `^monitoring/learn-[0-9]+$` pattern, with a strictly lower run number (never a human PR sharing the prefix); both steps are gated by the `LEARN_STATE_AUTOMERGE` kill-switch and the workflow runs under a `concurrency` group. Documented in `docs/reference/learn-monitor-guide.md`. Addresses the recurring monitoring-PR pile-up (#447).
- Added explicit Markdown authoring guidance in `README.md` and `CONTRIBUTING.md` to avoid `:material-*:` shortcodes in page content under the current CSP-safe MkDocs emoji configuration.

## [1.6.2] — May 11, 2026 (Frontier Readiness auto-evaluator wave)

**Release theme:** Six-PR wave wiring telemetry-driven auto-scoring for the Frontier Readiness assessment, taking auto-evaluable coverage from **0/25 (0%)** to **6/25 (24%)**. After this release, the Frontier auto-evaluable backlog is **structurally exhausted** — the remaining 19 questions (76%) are facilitator-only by design (board attestation, written policy text, executive interviews, regulatory committee minutes, business strategy alignment) and cannot be honestly derived from M365/PPAC/Sentinel/SharePoint telemetry.

**Upgrade safety:** No breaking changes. No control IDs renamed. Schema additions only on the Frontier manifest (six entries flipped to `auto_evaluable: true` with new `notes` fields). Assessment engine grows by six evaluator functions plus 21 new tests; existing 78-control assessment behaviour unchanged. Safe to upgrade in place.

**Honesty principle:** Every evaluator added in this wave is **partial-capped** — none ever returns `"yes"`. Each Frontier question has at least one facilitator-only sub-claim (governance maturity, written attestation, named executive sponsor) that telemetry cannot verify, so auto-scoring asserts only what telemetry can support and explicitly names the residual facilitator burden in evidence strings. The honest assessment-coverage report at `docs/reference/frontier-assessment-coverage.md` reflects this structural floor — it is not a roadmap target to "improve."

### Coverage progression

| Wave | PRs | Auto | Manual | % Auto |
|------|-----|------|--------|--------|
| Pre-evaluators (v1.6.1) | — | 0 | 25 | 0% |
| Q16 + Q17 framework | [#215](https://github.com/judeper/FSI-AgentGov/pull/215), [#216](https://github.com/judeper/FSI-AgentGov/pull/216) | 2 | 23 | 8% |
| Q13 partial-cap pattern | [#218](https://github.com/judeper/FSI-AgentGov/pull/218) | 3 | 22 | 12% |
| Q01 word-boundary regex | [#219](https://github.com/judeper/FSI-AgentGov/pull/219) | 4 | 21 | 16% |
| Q18 + Q03 closeout | [#220](https://github.com/judeper/FSI-AgentGov/pull/220) | **6** | **19** | **24%** |

### PR [#215](https://github.com/judeper/FSI-AgentGov/pull/215) — Q16 + Q17 evaluator framework

Established the Frontier evaluator infrastructure: `assessment/engine/score_frontier.py` with `_load_collected_json` helper, `EVALUATORS` registry, `compute_evaluator_coverage` API, and the first two evaluators:

- **Q16** (`zone_classification_present`) — pure auto: PPAC environment Tags / Group naming for Zone 1/2/3 classification
- **Q17** (`audit_log_retention_meets_finra`) — pure auto: M365 audit retention policies via Purview audit-log search export

Coverage matrix infrastructure (`docs/reference/frontier-assessment-coverage.md`) and CI gating (`scripts/generate_coverage_matrix.py --type frontier --check`) added in this PR.

### PR [#216](https://github.com/judeper/FSI-AgentGov/pull/216) — PPAC environment-group enrichment

Extended `assessment/collectors/Collect-PPAC.ps1` with two new sections:

- **Section 8** — Environment Groups via BAP API (`Id`, `DisplayName`, `Description`, `CreatedTime`, `EnvironmentCount`)
- **Section 9** — per-environment tag/group enrichment (`EnvironmentGroupId`, `Tags`)

These sections back the 3-way correlation in PR #220 (Q18) and improve Q16's signal precision.

### PR [#218](https://github.com/judeper/FSI-AgentGov/pull/218) — Q13 partial-cap pattern

**Q13** (`zone_classification_with_audit_supervision_and_model_risk`) — established the **partial-cap** pattern that the rest of the wave inherits. Combines Q16's PPAC zone signal with Q17's audit signal and Purview supervision policy presence. Returns `"partial"` when telemetry signals are present but caps there because model-risk-management governance attestation is facilitator-only.

Pattern features replicated by Q18 + Q03:
- `_metadata.errors` short-circuit per source
- `None` only when ALL sources unavailable
- Evidence string explicitly names every missing signal AND every facilitator-only caveat
- `NEVER_returns_yes` test invariant

### PR [#219](https://github.com/judeper/FSI-AgentGov/pull/219) — Q01 + Graph job-title enumeration

**Q01** (`ai_initiative_owner_identified`) — keyword search over Graph user job titles for AI leadership signals (CDO, Chief AI Officer, Chief AI Risk Officer, VP AI, Head of AI, etc.). Required collector extension:

- **Collect-Graph.ps1 §7** added: AI Leadership Job Titles via two narrow `Get-MgUser` `startswith` queries + post-filter (Graph API does not support `contains` on job-title)

Word-boundary regex (`r'\bVP\b'`, `r'\bCDO\b'`) used for short acronyms to prevent false positives like "VPC" or "CDOs". Capped at `"partial"` because mere title presence does not confirm active sponsorship.

### PR [#220](https://github.com/judeper/FSI-AgentGov/pull/220) — Q18 + Q03 closeout (this release)

**Q18** (`env_groups_with_inventory_siem_rag_and_lineage`, L300 Tech & Data) — 3-way telemetry correlation across:
- PPAC environment groups (Sections 8+9 from #216)
- Sentinel SIEM data connectors (`Office365Enabled`, `McasEnabled`, `TotalConnectors`)
- SharePoint item-level permission scan (`itemLevelPermissions[].SampledItems` + `groundingCrossRef.ApprovedFound`)

Telemetry gap explicitly acknowledged: **automated agent inventory is not collected** by any current collector. Q18 evidence string names this as `"agent inventory not collected (out of scope)"` rather than silently degrading. RAG-integrity validation + data lineage documentation are flagged as facilitator-only.

**Q03** (`enterprise_ai_strategy_published_with_portfolio`, L300 AI Strategy & Experience) — SharePoint site-name heuristic against 8 multi-word strategic keywords (`ai strategy`, `ai governance`, `ai council`, `ai portfolio`, `agent portfolio`, `frontier`, `executive sponsor`, `governance committee`). All keywords are multi-word so plain substring matching avoids the false-positive risk that Q01 had to navigate for short acronyms. Capped at `"partial"` because "published" is telemetry-verifiable but "with portfolio" + "active governance" are facilitator-only.

Generator update: `scripts/generate_coverage_matrix.py` `_FRONTIER_EVALUATOR_CANDIDATES` list **emptied** — Q03 + Q18 removed because they are no longer "future." The list is now structurally complete; any new Frontier evaluator wiring would require an explicit governance decision to relax the facilitator-only floor.

### Test additions across the wave

- v1.6.1 baseline: 72 tests
- After #215: 81 tests (+9 for Q16 + Q17)
- After #218: 85 tests (+4 for Q13)
- After #219: 93 tests (+8 for Q01)
- After #220: **114 tests** (+21 for Q18 + Q03) — release-time count for v1.6.2 PR-wave-220
- Current suite (post-release additions): **140 tests** (verified 2026-05-16)

All six evaluators ship with `NEVER_returns_yes` invariant tests, evidence-string assertions, and facilitator-override (driver-level upgrade/downgrade) tests.

### Validation gates (all six PRs)

Every PR in this wave passed the full gauntlet locally and in CI:

- `pytest assessment/tests/ -q`
- `ruff check assessment scripts`
- `generate_coverage_matrix.py --type frontier --check`
- `generate_coverage_matrix.py --check` (78-control assessment)
- `check_manifest_doc_drift.py --check`
- `verify_language_rules.py`

PowerShell static analysis (`PSScriptAnalyzer`) gated PR #216 (collector changes). All other PRs were Python-only.

### Files changed (cumulative across the wave)

- `assessment/engine/score_frontier.py` — new module, 6 evaluators + helpers + EVALUATORS registry
- `assessment/manifest/frontier-readiness.json` — 6 entries flipped `auto_evaluable: true` with `notes`
- `assessment/tests/test_score_frontier.py` — 6 evaluator test classes (~1300 lines)
- `assessment/tests/fixtures/` — 14+ new fixtures (PPAC env-group variants, Sentinel connector variants, SharePoint variants)
- `assessment/collectors/Collect-PPAC.ps1` — Sections 8+9 added (#216)
- `assessment/collectors/Collect-Graph.ps1` — Section 7 added (#219)
- `docs/reference/frontier-assessment-coverage.md` — auto-regenerated; final state 6/25 (24%) Auto, 19/25 (76%) Manual, 0 Unimplemented
- `scripts/generate_coverage_matrix.py` — `--type frontier` mode + `_FRONTIER_EVALUATOR_CANDIDATES` retired

### Forward-looking note

The Frontier auto-evaluable backlog is closed. Future Frontier work belongs in three categories:

1. **Facilitator playbooks** — published guidance on how to evidence the 19 facilitator-only questions during an actual Frontier engagement
2. **Driver/pattern coverage docs** — narrative guidance mapping each Frontier transformation pattern to which controls in the 78-control framework it leans on
3. **Telemetry honesty maintenance** — keeping the 6 existing evaluators current as collectors evolve (e.g., if Microsoft adds an "agent inventory" Graph endpoint, Q18's evidence string would need an update)

No further Frontier evaluator wiring is planned. The 76% manual floor is a feature, not a defect.

### Post-release triage fix cycle (2026-05-17)

Triage of 3 independent external audits (51 unified findings + 8 rubber-duck additions = 59 total). 12 PRs merged on 2026-05-17. No VERSION bump — fixes stay under v1.6.2.

**Regulatory correctness**
- **PR-3** (#273): Added SR 26-2 / OCC 2026-13 generative-AI scope caveat to `docs/reference/regulatory-mappings.md` and `docs/framework/regulatory-framework.md`. The interagency MRM guidance issued April 17, 2026 explicitly excludes generative AI and agentic AI from scope per primary-source verification. Re-characterized GenAI-specific control mappings (Controls 2.11, 2.16, 2.20, 3.10) as analogous principles rather than direct regulatory obligations.
- **PR-4** (#280): Added NAIC Model Bulletin on Use of AI by Insurance Companies (December 2023), NFA Compliance Rule 2-9 (FCM/IB/CPO/CTA supervisory baseline), SEC Regulation S-P (including the May 2024 30-day NPI notification amendments). Upgraded NYDFS Part 500 surfacing in `regulatory-framework.md`. Added OCC Bulletin 2023-17 number to existing Interagency Third-Party Guidance citations.
- **PR-6** (#281): Resolved 624 sector-specific TODO placeholders in `assessment/manifest/controls.json` (replaced with `null` per schema preservation). Canonicalized 61 stale `OCC-2011-12` / `Fed-SR-11-7` machine-readable codes to `OCC-2026-13` / `Fed-SR-26-2`.

**Assessment engine**
- **PR-5** (#276): Fixed 8 of 11 evaluator drift (6 manifest `pass_condition` strings rewired, 2 preserved for future wiring). Added collector payload normalization layer in `score.py`. Regenerated `frontier-assessment-coverage.md` (correctly shows 6/25 = 24% — previously stale at 0%). Documented SPA vs Python engine semantic divergence in `assessment/README.md` and `docs/assessment/index.md`. Auto-evaluable controls: 1/78 → 7/78.

**Customer-facing surfaces**
- **PR-1** (#271): Fixed count drift on home page (`5 → 6 Regulatory Frameworks`) + Solutions Integration repo-structure block + Summary Statistics block.
- **PR-2** (#275): ~240 playbook footer canonicalizations + 6 stale non-playbook stamps brought to canonical `v1.6.2 / May 2026`.
- **PR-7** (#274): Refreshed all 6 Excel templates from `v1.4.0 — April 2026` to `v1.6.2 — May 2026`. Restored 20 dashboard rollup formulas (`governance-maturity-dashboard.xlsx`). Added missing controls 2.26 / 1.29 / 4.8 / 4.9 to `docs/downloads/index.md`. Hardened `scripts/verify_excel_templates.py`.
- **PR-8** (#279): Corrected Control 1.1 SEC 17a-4(f) overclaim to align with Control 1.7's capture-vs-preservation framing. Removed duplicate `AIAppInteraction` bullet from Control 1.7.
- **PR-11** (#270): Corrected static SVG pillar counts in `solutions-integration-overview.svg` (28/24/12/7 → 29/26/14/9).
- **PR-13** (#269): Replaced 2 redirecting Microsoft Learn URLs across 8 files.
- **PR-15** (#282): Final footer cleanup on 7 top-level customer-facing pages that PR-2's playbook-scoped sweep didn't reach.

**Hygiene**
- **PR-14** (#272): Clarified `CHANGELOG.md` test-count narrative (114 release-time vs 140 current). Also added `CHANGELOG.md` to `python-quality.yml` paths trigger so changelog-only PRs satisfy branch protection.

**Companion repository (FSI-AgentGov-Solutions)**
- 5 GitHub issues drafted and posted at #143–#147 for future work (MRM Automation regulatory refresh, solutions inventory reconciliation, version drift between site and repo, preview-vs-live status, canonical control-coverage metadata export).

**Audit artifacts (private, gitignored)**
- All 3 external audits + 12 verification tracks + 8 enumeration follow-ups + Phase 3 rubber-duck critique + unified findings register (59 findings) + fix plan + final QA + handoff brief stored in `maintainers-local/audits/2026-05-16/` for internal record.

**Net findings disposition**: 30 confirmed-fixed / 13 rejected (audits read stale corpus state) / 9 deferred-informational / 7 pending external Microsoft product-surface research.

**Pending user actions (not blocking customer handoff)**
- Forward 7 Microsoft product-surface researcher prompts to specialized researcher (`maintainers-local/audits/2026-05-16/findings/track-j-msft-research-prompts.md`)
- Review 5 companion-repo issues #143–#147 in FSI-AgentGov-Solutions

---

## [1.6.1] — May 10, 2026 (Microsoft Learn drift patch)

**Release theme:** Documentation-only patch responding to upstream Microsoft Learn changes detected by the Learn Monitor (run 114, 2026-05-10). Five follow-up issues were filed (#205–#209); four resulted in doc updates; one (#205) was investigated and closed `not planned` (the framework had never adopted the deprecated terminology). Five parallel Sonnet agents in five git worktrees executed the fixes simultaneously, validating the worktree-per-agent pattern at scale.

**Upgrade safety:** No breaking changes. No schema changes. No control IDs renamed. No file additions. Pure documentation patches across 5 controls + 5 playbooks + `license-requirements.md`. Safe to upgrade in place.

### Issue #206 — Analytics retention + 7-area effectiveness ([#211](https://github.com/judeper/FSI-AgentGov/pull/211), `3a936123`)

Modified:

- `docs/controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md` — Data Availability info box: 180-day analytics, 28-day session details
- `docs/controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md` — retention windows admonition
- `docs/controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md` — retention admonition in §Platform-Enabled Monitoring; footer to May 2026
- `docs/controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md` — retention admonition in §Verification Criteria
- `docs/controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md` — retention admonition after Feedback Capture table
- `docs/playbooks/control-implementations/2.5/portal-walkthrough.md` — new §9.8 covering 7-area effectiveness panel structure (added "Knowledge source use")
- `docs/playbooks/control-implementations/2.6/portal-walkthrough.md` — retention admonition in §3.1

Net change: +49 / −4 lines.

### Issue #207 — IRM DLP workload caveats + role groups ([#212](https://github.com/judeper/FSI-AgentGov/pull/212), `7a026bb1`)

Modified:

- `docs/controls/pillar-1-security/1.12-insider-risk-detection-and-response.md` — `!!! warning "IRM DLP workload limitations"` admonition listing 5 unsupported workloads (Teams, Endpoint DLP, M365 Copilot, Power BI, on-premises repositories); 3 verbatim role groups cited from Microsoft Learn (`Insider Risk Management`, `Insider Risk Management Analysts`, `Insider Risk Management Investigators`); cross-references to controls 1.5, 1.6, 1.10, 1.13
- `docs/playbooks/control-implementations/1.12/portal-walkthrough.md` — workload caveat surfaced in walkthrough

Net change: +72 / −2 lines.

### Issue #208 — BCDR retention defaults + RPO/RTO surfacing ([#213](https://github.com/judeper/FSI-AgentGov/pull/213), `8cb6bbec`)

Modified:

- `docs/controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md` — retention table corrected: 7-day default ALL environments; extended retention up to 28 days requires production Managed Environments. Surfaces RPO/RTO from new Microsoft FAQ: within-region near-zero RPO + <5min RTO; cross-region typical replication lag <15min
- `docs/playbooks/control-implementations/2.4/portal-walkthrough.md` — retention defaults aligned
- `docs/playbooks/control-implementations/2.4/troubleshooting.md` — footer
- `docs/images/2.4/EXPECTED.md` — screenshot specs aligned to new defaults

Net change: +25 / −15 lines.

### Issue #209 — Agent 365 license deadline 2026-07-01 ([#214](https://github.com/judeper/FSI-AgentGov/pull/214), `cbfbb463`)

Modified:

- `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md` — `!!! danger` deadline callout: AI Agent Inventory in Defender for Cloud Apps requires Agent 365 after 2026-07-01; orgs without Agent 365 lose AI Agent Inventory visibility entirely
- `docs/controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md` — deadline callout for Defender for Cloud Apps cross-reference (walkthrough Step 8)
- `docs/playbooks/control-implementations/1.8/portal-walkthrough.md` — danger admonition in walkthrough
- `docs/playbooks/control-implementations/3.7/portal-walkthrough.md` — danger admonition in walkthrough
- `docs/reference/license-requirements.md` — two new rows for controls 1.8 / 3.7 documenting the Agent 365 transition

Net change: +60 / −10 lines.

### Issue #205 — Sensitivity labels Entra group classification migration (closed `not planned`)

Investigated, no changes required. Exhaustive grep across the entire framework for `Entra group classification`, `Convert Entra group classification`, `Classic Azure AD classification`, and `Convert classic group classifications` returned zero matches. The framework had never adopted the deprecated terminology. Three classification-adjacent terms (DLP connector classification, Entra group membership for DLP scoping, SharePoint classic sites) were verified unrelated. Issue closed with audit comment; branch never pushed.

### Workflow validation

- **5 parallel Sonnet agents in 5 git worktrees** — zero filesystem race conditions, zero merge conflicts, all 5 agents independently ran `mkdocs build --strict` against the same global Python install with no contention. Wall time per agent: 9–12 minutes.
- **Empty-commit pattern (#205)** — agent created an audit-trail commit when investigation found nothing to fix; orchestrator chose to skip the empty PR and close the issue directly with the investigation comment instead.
- **CI gates per PR** — 8/8 required checks green (mkdocs --strict, verify_language_rules, verify_controls, drift, coverage matrix, ruff, pytest, codeql) before merge.

### Hard rules

- **Tier-1 banlist enforced** — 0 banned-phrase hits across all 4 PRs.
- **78-control catalog unchanged.** Pillar structure unchanged. Zone model unchanged.
- **No manifest changes.** `controls.json` byte-identical to v1.6.0.
- **No solutions catalog changes.** Companion repo untouched.
- **Documentation-only patch.** No code changes to `assessment/`, `scripts/`, or workflows.

### Validation at release

| Gate | Result |
|---|---|
| `mkdocs build --strict` | 0 warnings |
| `verify_language_rules.py` | 0 banned phrases |
| `verify_controls.py` | 78 controls pass |
| `check_manifest_doc_drift.py --check` | 78=78=78 |
| `generate_coverage_matrix.py --check` | current |
| `generate_pattern_coverage.py --check` (with companion repo) | current (78 controls, 35 solutions) |
| `ruff check` | all pass |
| `pytest assessment/tests/` | 56 passed |

---

## [1.6.0] — May 10, 2026 (Solutions Discoverability Release)

**Release theme:** Make the 35 companion solutions discoverable by Microsoft CAPE alignment metadata. Phase 6a tagged every solution README in the companion repo with `applicable_patterns`, `applicable_drivers`, and `coe_function` frontmatter; Phase 6b consumed those tags in the framework repo to enrich the Solutions Index and the Pattern Coverage matrix. No control catalog changes; no schema changes.

**Upgrade safety:** No breaking changes. No control IDs renamed. No `controls.json` schema changes. Safe to upgrade in place. Existing Solutions Index consumers that grep on existing column headers continue to work — three new columns (Patterns, Drivers, CoE) were appended before Summary.

### Phase 6a — Companion repo tagging (judeper/FSI-AgentGov-Solutions [#134](https://github.com/judeper/FSI-AgentGov-Solutions/pull/134), `d1d6f653`)

Added (in companion repo):

- YAML frontmatter on all 35 production solution READMEs with `applicable_patterns` (subset of P1–P6), `applicable_drivers` (subset of the 5 canonical Capability Drivers, snake_case IDs), and `coe_function` (one of govern / enable / optimize / scale)
- Tag derivation: `applicable_patterns` from `pattern_critical` field in framework `controls.json` for each solution's primary controls (with purpose-based inference where `pattern_critical` was empty across all primary controls); `applicable_drivers` from union of primary controls' `applicable_drivers`; `coe_function` mapped per `agentic-coe.md` definitions
- 282 frontmatter insertions across 35 files; zero README content changes
- Distribution: govern=20, optimize=8, enable=4, scale=2

### Phase 6b — Framework repo consumption ([#210](https://github.com/judeper/FSI-AgentGov/pull/210), `45dd2cfc`)

Added:

- `docs/reference/solutions-index.md` — three new columns (Patterns, Drivers, CoE) on the 35-solution table; same fields added to per-solution detail blocks; new "Discovering by CAPE alignment" intro section linking to framework documents
- `docs/reference/pattern-coverage.md` — regenerated with new `Solutions count` column on the coverage summary and a new "Solutions per pattern" section listing all 84 pattern declarations across the 35 solutions

Modified:

- `scripts/generate_pattern_coverage.py` — new `--solutions-repo` CLI flag (also honors `$FSI_SOLUTIONS_REPO` env var) for parsing companion repo frontmatter via pyyaml; graceful skip when companion repo unavailable
- `.github/workflows/python-quality.yml` — new drift step clones companion repo and runs `generate_pattern_coverage.py --check` to keep `pattern-coverage.md` in sync with companion frontmatter
- `CHANGELOG.md` — this entry

### Solutions count per pattern

| Pattern | Solutions |
|---|---|
| P1 — Employee AI Enablement | 14 |
| P2 — Business Expert Empowerment | 9 |
| P3 — Workplace & IT Services | 5 |
| P4 — Core Business Process Transformation | 25 |
| P5 — External Engagement | 19 |
| P6 — AI-First Capabilities | 12 |
| **Total declarations** | **84** |

### Hard rules and brand boundary

- **Tier-1 banlist enforced** — "ensures compliance", "guarantees", "will prevent", "eliminates risk" remain banned across all docs (0 hits at release).
- **No control IDs renamed**, no manifest schema breaks. `controls.json` unchanged from v1.5.0.
- **78-control catalog unchanged.** Pillar structure unchanged. Zone model unchanged.
- **Companion repo as authoritative source** — Pattern/Driver/CoE assignments live in companion repo READMEs; framework repo regenerates `pattern-coverage.md` from those tags via CI gate. Single source of truth.

### Validation at release

| Gate | Result |
|---|---|
| `mkdocs build --strict` | 0 warnings |
| `verify_language_rules.py` | 0 banned phrases |
| `verify_controls.py` | 78 controls pass |
| `check_manifest_doc_drift.py --check` | 78=78=78 |
| `generate_coverage_matrix.py --check` (controls + frontier) | current |
| `generate_pattern_coverage.py --check` (with companion repo) | current (78 controls, 35 solutions) |
| `ruff check` | all pass |
| `pytest assessment/tests/` | 56 passed |

---

## [1.5.0] — May 10, 2026 (Microsoft Alignment Release)

**Release theme:** FSI translation layer for Microsoft CAPE (Copilot Acceleration Engineering) materials. Adds vocabulary crosswalks, framework layer for CAPE concepts, assessment-engine support for CAPE Frontier Readiness scoring, and partner-facing reference docs (CSA + diagram catalog) — all as additive, non-breaking content.

**Upgrade safety:** No breaking changes. No schema breaks. No control IDs renamed. Safe to upgrade in place. Existing `controls.json` schema is backward-compatible (only field additions). Existing assessment runs continue to work; CAPE Frontier scoring is opt-in via new `-AssessmentType` parameter.

### Phase 1 — Reference layer ([#199](https://github.com/judeper/FSI-AgentGov/pull/199), `f3e8edc4`)

Added:

- `docs/reference/microsoft-cape-crosswalk.md` — bridge document mapping the 6 CAPE patterns to FSI controls and regulatory exposure per pattern
- `docs/reference/cco-quick-reference.md` — pocket lookup for compliance officers

Modified:

- `docs/framework/regulatory-framework.md` — CAPE pattern annotations
- `docs/reference/glossary.md` — CAPE vocabulary additions
- `docs/reference/role-catalog.md` — expanded role entries
- `scripts/verify_language_rules.py` — added Tier-2 banlist (CAPE vendor-marketing language) with `<!-- verify-language-rules: allow-second-tier -->` CSA annotation support

### Phase 2 — Framework layer ([#201](https://github.com/judeper/FSI-AgentGov/pull/201), `429ab90c`)

Added:

- `docs/framework/transformation-patterns.md` — canonical 6-pattern framework summary with Pattern 6 D3 guardrail
- `docs/framework/agentic-capability-drivers.md` — Microsoft's 5 Capability Drivers and maturity model
- `docs/framework/agentic-coe.md` — standalone CoE blueprint with 4 functions (Govern/Enable/Optimize/Scale), CoE shapes, anti-patterns, and federation guardrail

Modified:

- `docs/framework/agent-lifecycle.md`, `governance-fundamentals.md`, `index.md`, `operating-model.md` — CAPE concept integration and cross-references
- `docs/reference/microsoft-cape-crosswalk.md` — Phase 2 additions
- `docs/reference/role-catalog.md` — CoE role additions

### Phase 3 — Assessment integration ([#202](https://github.com/judeper/FSI-AgentGov/pull/202), `0adf51df`)

Added:

- `assessment/manifest/frontier-readiness.json` — 25 questions × 5 drivers × 5 maturity levels
- `assessment/engine/score_frontier.py` — full Frontier Readiness scoring algorithm
- `assessment/collectors/Collect-Frontier.ps1` — interactive + batch collector
- `assessment/tests/test_score_frontier.py` — 30 tests (56 total green at release)
- `docs/reference/pattern-coverage.md` — 78×6 generated control × pattern matrix
- `docs/reference/frontier-assessment-coverage.md` — honest coverage report (0% auto v1; all Frontier scoring is manual-questionnaire-driven)
- `scripts/generate_pattern_coverage.py` — coverage matrix generator

Modified:

- `assessment/manifest/controls.json` — 78 controls tagged with `applicable_drivers`, `applicable_patterns`, `pattern_critical` (additive fields; backward-compatible)
- `assessment/engine/report.py` — added `--type controls|frontier|both` flag with new report generators
- `assessment/run-assessment.ps1` — added `-AssessmentType` and `-FrontierAnswersFile` parameters
- `assessment/README.md` — decision tree, Frontier Quick Start, maturity scale
- `scripts/generate_coverage_matrix.py` — added `--type controls|frontier` flag

### Phase 4 — Partner-facing reference ([#203](https://github.com/judeper/FSI-AgentGov/pull/203), `294ae358`)

Added:

- `docs/reference/csa-quick-reference.md` — Microsoft FSI CSA pocket lookup (197 lines)
- `docs/reference/csa-positioning-guide.md` — long-form CSA positioning narrative (390 lines)

### Phase 5 — Diagrams + Release closeout (this release)

Added:

- 5 net-new Mermaid diagrams embedded in framework and reference docs: Pattern × Zone matrix, CoE structure by pattern, Decision rights framework, CAPE 90-day × FSI Phase timeline, Agent lifecycle 7-stage
- `docs/reference/diagram-catalog.md` — catalog of all repo diagrams (60+ existing + 5 new) with audience, use-case, and format columns
- `docs/images/diagrams/source/cape/*.mmd` — editable Mermaid source files for CSA customer-deck export
- `CHANGELOG.md` — this entry

### Hard rules and brand boundary

This release adopts CAPE vocabulary as a translation layer, not as endorsement. FSI-AgentGov remains an independent FSI governance framework. Microsoft is not a publisher, sponsor, or reviewer of this content.

- **Tier-1 banlist enforced** — "ensures compliance", "guarantees", "will prevent", "eliminates risk" remain banned across all docs (0 hits at release).
- **Tier-2 banlist** (CAPE vendor-marketing language: "self-improving", "autonomous decision-making", etc.) is suspended only inside CSA-facing reference docs via the `<!-- verify-language-rules: allow-second-tier -->` annotation, where CSAs need to teach customers to reframe the language.
- **Pattern 6 D3 guardrail and Federation guardrail** appear verbatim in all partner-facing reference docs.
- **No control IDs renamed**, no manifest schema breaks. `controls.json` gained 3 additive fields (`applicable_drivers`, `applicable_patterns`, `pattern_critical`).
- **78-control catalog unchanged.** Pillar structure unchanged. Zone model unchanged.

### Validation at release

| Gate | Result |
|---|---|
| `mkdocs build --strict` | 0 warnings |
| `verify_language_rules.py` | 0 banned phrases |
| `verify_controls.py` | 78 controls pass |
| `check_manifest_doc_drift.py --check` | 78=78=78 |
| `generate_coverage_matrix.py --check` (controls + frontier) | current |
| `generate_pattern_coverage.py --check` | current |
| `ruff check` | all pass |
| `pytest assessment/tests/` | 56 passed |

---

## [1.4.2] — April 30, 2026 (Phase B′ Triage Fixes)

Patch release closing out the three P2 items deferred from v1.4.1. Markdown export customer header now escapes special characters so admin-entered names render correctly in raw source (#168); the vendored `xlsx.full.min.js` is marked binary in `.gitattributes` so Windows checkouts no longer flip its SRI hash via CRLF normalization (#169); and two locally-flaky Playwright specs (`14-fetch-failure`, `28-perf-budget`) are hardened with deterministic ordering and a more realistic perf threshold (#170). Phase B″ triage report (#171) confirmed 0 P0/P1 findings — recommended ship. See [CHANGELOG-v1.4.md](https://github.com/judeper/FSI-AgentGov/blob/main/releases/CHANGELOG-archive/CHANGELOG-v1.4.md#v142--april-30-2026) for the full entry.

---

## [1.4.1] — April 30, 2026 (E2E Test Infrastructure & SPA Hardening)

Quality + assurance release. No control catalog changes. Ships an end-to-end Playwright test suite (~60 specs across smoke, regression, edge cases, accessibility, and production probes), 4 new CI workflows (including SheetJS supply-chain SRI verification and post-deploy production smoke), branch protection as code, and 12+ assessment SPA hardening fixes covering saved-list integrity, storage quotas, formula-injection defenses, prototype-pollution guards, CSP allowlist enforcement, and per-assessment filter namespacing. See [CHANGELOG-v1.4.md](https://github.com/judeper/FSI-AgentGov/blob/main/releases/CHANGELOG-archive/CHANGELOG-v1.4.md#v141--april-30-2026) for the full entry.

---

## [1.4.0] — April 2026 (Assessment Tool Unification & Solutions Bridge)

### Added
- **Unified manifest schema**: Single source of truth (`assessment/manifest/controls.json`) for Python scoring engine and assessment SPA with 11 additive fields per control
- **Solutions bridge**: Cross-repository integration with FSI-AgentGov-Solutions v1.4.0 via committed `solutions-lock.json` (35 solutions indexed)
- **10 SPA enhancements**: How-to-verify drawer (E1), zone auto-exclusion (E2), collector evidence import (E3), role filter (E4), sector calibration for 8 institution types (E5), priority starter set of 5 foundation controls (E6), Next Session Agenda export (E7), inline evidence/notes capture (E8), facilitator mode with hints and time budgets (E9), 7 per-role pre-session homework pages (E10)
- **Harvest script**: `scripts/harvest_manifest_extension.py` scaffolds v1.4 fields from existing control docs with TODO placeholders for author-judgment content
- **3 validators**: Manifest schema validator, solutions lock validator, and lock refresh script with tag pinning
- **Portal export envelope (v1.4.1-prep, additive)**: SPA `exportJSON` and `exportRoleSection` now emit a `_metadata` block (framework version, export schema version, manifest commit hint, pillar names, schema type) plus `_computedScores` (pillar/overall percentages and counts) and a derived `assessmentStatus` enum (`draft`/`in-progress`/`final`). Existing top-level state keys are preserved, so v1.3.x consumers continue to work unchanged. Importer silently drops snapshot fields and recomputes on next export. See [CHANGELOG-v1.4.md](https://github.com/judeper/FSI-AgentGov/blob/main/releases/CHANGELOG-archive/CHANGELOG-v1.4.md) and [`assessment/data/README.md`](https://github.com/judeper/FSI-AgentGov/blob/main/assessment/data/README.md#portal-export-schema).

### Changed
- **Control count normalization**: Fixed stale "71 controls" / "72 controls" references to "78 controls" across all documentation
- **Version bump**: 1.3.3 → 1.4.0 across README, mkdocs.yml, CITATION.cff, and meta references

### Breaking Changes
- **Assessment SPA export schema**: JSON export format incompatible with v1.3.x—no migration tool provided; recommend completing in-progress v1.3 assessments before upgrading or re-running from scratch with v1.4 collector import

---

| Version | Period | File |
|---------|--------|------|
| **v1.6.x** (current) | May 2026 | [CHANGELOG.md](https://github.com/judeper/FSI-AgentGov/blob/main/CHANGELOG.md) |
| **v1.5.x** | May 2026 | [CHANGELOG.md](https://github.com/judeper/FSI-AgentGov/blob/main/CHANGELOG.md#150--may-10-2026-microsoft-cape-alignment-release) |
| **v1.4.x** | April 2026 | [CHANGELOG-v1.4.md](https://github.com/judeper/FSI-AgentGov/blob/main/releases/CHANGELOG-archive/CHANGELOG-v1.4.md) |
| **v1.3.x** | March–April 2026 | [CHANGELOG-v1.3.md](https://github.com/judeper/FSI-AgentGov/blob/main/releases/CHANGELOG-archive/CHANGELOG-v1.3.md) |
| **v1.1.x** | December 2025 | [CHANGELOG-v1.1.md](https://github.com/judeper/FSI-AgentGov/blob/main/releases/CHANGELOG-archive/CHANGELOG-v1.1.md) |
| **v1.2.x and earlier** | October 2025 – March 2026 | Archived — see [git history](https://github.com/judeper/FSI-AgentGov/commits/main/) prior to April 2026 |
