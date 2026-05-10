# Changelog

All notable changes to the FSI Agent Governance Framework are documented here, organized by major version.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

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

Patch release closing out the three P2 items deferred from v1.4.1. Markdown export customer header now escapes special characters so admin-entered names render correctly in raw source (#168); the vendored `xlsx.full.min.js` is marked binary in `.gitattributes` so Windows checkouts no longer flip its SRI hash via CRLF normalization (#169); and two locally-flaky Playwright specs (`14-fetch-failure`, `28-perf-budget`) are hardened with deterministic ordering and a more realistic perf threshold (#170). Phase B″ triage report (#171) confirmed 0 P0/P1 findings — recommended ship. See [CHANGELOG-v1.4.md](CHANGELOG-v1.4.md#v142--april-30-2026) for the full entry.

---

## [1.4.1] — April 30, 2026 (E2E Test Infrastructure & SPA Hardening)

Quality + assurance release. No control catalog changes. Ships an end-to-end Playwright test suite (~60 specs across smoke, regression, edge cases, accessibility, and production probes), 4 new CI workflows (including SheetJS supply-chain SRI verification and post-deploy production smoke), branch protection as code, and 12+ assessment SPA hardening fixes covering saved-list integrity, storage quotas, formula-injection defenses, prototype-pollution guards, CSP allowlist enforcement, and per-assessment filter namespacing. See [CHANGELOG-v1.4.md](CHANGELOG-v1.4.md#v141--april-30-2026) for the full entry.

---

## [1.4.0] — April 2026 (Assessment Tool Unification & Solutions Bridge)

### Added
- **Unified manifest schema**: Single source of truth (`assessment/manifest/controls.json`) for Python scoring engine and assessment SPA with 11 additive fields per control
- **Solutions bridge**: Cross-repository integration with FSI-AgentGov-Solutions v1.4.0 via committed `solutions-lock.json` (35 solutions indexed)
- **10 SPA enhancements**: How-to-verify drawer (E1), zone auto-exclusion (E2), collector evidence import (E3), role filter (E4), sector calibration for 8 institution types (E5), priority starter set of 5 foundation controls (E6), Next Session Agenda export (E7), inline evidence/notes capture (E8), facilitator mode with hints and time budgets (E9), 7 per-role pre-session homework pages (E10)
- **Harvest script**: `scripts/harvest_manifest_extension.py` scaffolds v1.4 fields from existing control docs with TODO placeholders for author-judgment content
- **3 validators**: Manifest schema validator, solutions lock validator, and lock refresh script with tag pinning
- **Portal export envelope (v1.4.1-prep, additive)**: SPA `exportJSON` and `exportRoleSection` now emit a `_metadata` block (framework version, export schema version, manifest commit hint, pillar names, schema type) plus `_computedScores` (pillar/overall percentages and counts) and a derived `assessmentStatus` enum (`draft`/`in-progress`/`final`). Existing top-level state keys are preserved, so v1.3.x consumers continue to work unchanged. Importer silently drops snapshot fields and recomputes on next export. See [CHANGELOG-v1.4.md](CHANGELOG-v1.4.md) and [`assessment/data/README.md`](assessment/data/README.md#portal-export-schema).

### Changed
- **Control count normalization**: Fixed stale "71 controls" / "72 controls" references to "78 controls" across all documentation
- **Version bump**: 1.3.3 → 1.4.0 across README, mkdocs.yml, CITATION.cff, and meta references

### Breaking Changes
- **Assessment SPA export schema**: JSON export format incompatible with v1.3.x—no migration tool provided; recommend completing in-progress v1.3 assessments before upgrading or re-running from scratch with v1.4 collector import

---

| Version | Period | File |
|---------|--------|------|
| **v1.4.x** (current) | April 2026 | [CHANGELOG-v1.4.md](CHANGELOG-v1.4.md) |
| **v1.3.x** | March–April 2026 | [CHANGELOG-v1.3.md](CHANGELOG-v1.3.md) |
| **v1.2.x and earlier** | October 2025 – March 2026 | Archived — see [git history](https://github.com/judeper/FSI-AgentGov/commits/main/) prior to April 2026 |
