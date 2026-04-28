# Changelog — v1.4.0

**Release Date:** April 2026

All notable changes to the FSI Agent Governance Framework v1.4.0 are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to semantic versioning.

**Other versions:** [Index](CHANGELOG.md) | [v1.3.x](CHANGELOG-v1.3.md) | v1.2.x and earlier — archived (see git history prior to April 2026)

---

## Maintenance — April 28, 2026

Documentation hygiene and CI maintenance pass; no framework feature changes.

### Fixed
- **Dead external links repaired across 73 docs files** ([#119](https://github.com/judeper/FSI-AgentGov/pull/119)) — repaired ~145 broken Microsoft Learn URLs (renamed/moved pages), the FINRA rulebook URL pattern (`rulebook` → `rulebooks`), Federal Reserve `srletters/sr1107.htm` → `srletters/SR2602.htm`, and two empty `https://` link targets in playbooks 3.4 and 3.6. Restored the `Link Validation` workflow to passing (was failing 5/5 prior runs).

### Changed
- **Federal Reserve guidance label updated**: 54 textual references across 22 docs files updated from "SR 11-7" to "SR 26-2 (formerly SR 11-7)" to reflect the Fed's April 17, 2026 supersession of SR 11-7 by SR 26-2 (Model Risk Management). Filename of control 2.6 was kept (`2.6-...sr-11-7.md`) to preserve permalinks.
- **GitHub Actions bumped to Node 24 majors** ([#120](https://github.com/judeper/FSI-AgentGov/pull/120)) across all 5 workflows (12 references): `actions/checkout` v4→v5, `actions/setup-python` v5→v6, `actions/cache` v4→v5, `actions/setup-node` v4→v5. Eliminates Node.js 20 deprecation warnings ahead of GitHub's June 2, 2026 forced migration.

### Operations
- Cleared 21 stale Learn Monitor PRs (#97–#117) by merging cumulative state PR #118 and bulk-closing the supersedes.
- Pruned 20 stale `monitoring/learn-*` remote branches.

---

## Overview

Version 1.4.0 represents a major advancement in the FSI Agent Governance Framework's assessment capabilities. This release unifies the manifest schema across both the Python scoring engine and the browser-based assessment single-page application (SPA), establishing a single source of truth for all 78 controls. The release delivers 10 new SPA enhancements that significantly improve the facilitator experience, role-based collaboration, sector-specific calibration, and cross-repository integration with the companion FSI-AgentGov-Solutions repository.

The v1.4.0 manifest extension supports progressive control maturation by allowing `TODO:` placeholders in author-judgment fields (yesBar, partialBar, noBar, priority scores, sector-specific thresholds, and facilitator hints) while maintaining full backward compatibility with the existing Python assessment engine.

---

## What's New in v1.4

### Unified Assessment Platform
- **Single source of truth**: All control metadata, verification procedures, scoring thresholds, regulatory mappings, and solution references now live in the extended `assessment/manifest/controls.json` schema
- **Build-time static asset delivery**: MkDocs hook exposes the manifest at `/assessment/data/controls.json` for runtime SPA consumption
- **Graceful degradation**: Missing or incomplete data fails safely with console warnings, not user-facing errors
- **Progressive maturation**: `TODO:` placeholders permitted in authored fields until content review completes

### Solutions Bridge (Cross-Repository Integration)
- **Lock-file contract**: Solution metadata from FSI-AgentGov-Solutions v1.4.1 tag frozen in `assessment/data/solutions-lock.json` for reproducible builds
- **Folder-name IDs**: Control→solution references use kebab-case folder names from FSI-AgentGov-Solutions (e.g., `"agent-observability-foundation"`)
- **Rich metadata lookup**: Solution name, version, domain, tier, description, URL, prerequisites, and verification steps loaded from lock file
- **35 solutions indexed**: Lock file includes 7 newly-delivered solutions from the v1.4.0 / v1.4.1 companion releases

### Sector-Specific Calibration
- **8 institution types**: Bank, broker-dealer, investment-adviser, insurance-carrier, insurance-wholesale, credit-union, holding-company, other
- **Per-sector thresholds**: Controls can specify differing yesBar requirements by institution type (e.g., broker-dealer audit retention vs bank retention)
- **Fallback logic**: Missing sector thresholds gracefully fall back to control-level defaults

### Facilitator Enhancements
- **Facilitator mode**: URL parameter `?mode=facilitate` unlocks facilitator-only hints, time budgets, and follow-up questions
- **Inline evidence capture**: Phase 1 responses now accept evidence URLs and notes alongside Yes/Partial/No answers
- **Pre-session homework pages**: per-role auto-generated pages (top 8 roles in primary nav) list relevant controls for pre-assessment review
- **Next Session Agenda export**: Markdown + PDF agenda builder targeting top 10 gaps with remediation roadmap and solution links

### Control Verification Enhancements
- **How to verify drawer**: Per-control expandable panel showing portal paths, PowerShell commands, expected evidence, and collector field mappings
- **Collector evidence import**: Phase 1 button imports JSON outputs from Python assessment collectors (`Collect-PPAC.ps1`, `Collect-Graph.ps1`, etc.) to pre-populate responses
- **Zone auto-exclusion**: Controls with "optional", "awareness-only", or "N/A" zone requirements automatically excluded from zone scores

### Priority Starter Set
- **5 foundation controls**: 2.1 (Change Control), 1.4 (Advanced Connector Policies), 1.5 (DLP), 1.7 (Audit Logging), 1.11 (MFA + Conditional Access)
- **Quick-start filter**: One-click filter on the 5 highest-priority controls for fast initial assessment

### Role-Based Workflow
- **Role filter dropdown**: Filter Phase 1 control list by administrator role (Power Platform Admin, Purview Compliance Admin, etc.)
- **Role-scoped homework**: per-role pre-session pages group controls by responsible role
- **Remediation grouping**: Results dashboard groups gap controls by role for task delegation

---

---

## Portal Export Envelope (v1.4.1-prep, additive)

### What changed
The portal SPA's JSON export (`assessment-app.js → exportJSON`, `exportRoleSection`) now emits a versioned envelope alongside the existing top-level state keys. **This is fully backwards-compatible** — every key present in pre-1.4.1 exports remains at the same top-level path, so legacy importers continue to work unchanged. Three new top-level keys are added:

| New key             | Type    | Purpose |
|---------------------|---------|---------|
| `_metadata`         | object  | Envelope: `exportSchemaVersion` (int, currently `1`), `schemaType` (`"full"` or `"section"`), `frameworkVersion` (string from JS const), `manifestSchemaVersion` (string, sourced from `solutions-lock.json`), `exportedAt` (ISO-8601), `exportedBy` (assessor name). |
| `_computedScores`   | object  | Snapshot of the same numbers the Results dashboard renders: `overall` (0–100 int or `null`), `perPillar.{1..4}` (0–100 int or `null`), `perControl.{id}` (0.0–1.0 or `null`). |
| `assessmentStatus`  | string  | One of `"draft"` (no responses), `"in-progress"` (any response), `"final"` (only set when `completedSteps` includes `"full"` or `"complete"`). |

### Why
Removes three full risk classes for any downstream tool consuming portal exports (e.g., the FSI-Assessment-Agent CSA reporting agent):
- **Silent version mismatch** — consumer can hard-refuse a JSON whose `frameworkVersion` doesn't match its grounding knowledge.
- **In-prompt arithmetic risk** — LLM-based consumers no longer need to re-implement the scoring algorithm; they consume `_computedScores` directly.
- **DRAFT inference ambiguity** — `assessmentStatus` is now an explicit enum instead of a heuristic on `completedSteps`.

### Backwards compatibility
- Importer (`importState`) reads named state keys only and silently ignores `_metadata` / `_computedScores` / `assessmentStatus`. **Snapshot fields are dropped on import**, which forces a recompute on the next export — preventing stale-score roundtrip drift.
- Round-trip test: tampered `_computedScores.overall` does not survive an import → re-export cycle (verified in `tests/spa/export-shape.test.mjs`).
- All 31 pre-existing SPA tests pass unchanged.

### Files touched
- `docs/javascripts/assessment-app.js` — added `FRAMEWORK_VERSION` + `EXPORT_SCHEMA_VERSION` constants, `deriveAssessmentStatus()`, `computeExportScores()`, `buildExportMetadata()` helpers, modified `exportJSON()` and `exportRoleSection()`.
- `tests/spa/export-shape.test.mjs` — 5 new contract tests covering envelope shape, score computation, status enum, top-level back-compat, and import-drop-recompute round-trip.
- `assessment/data/README.md` — documented the portal export schema (Portal Export Schema section).

### Known follow-ups (deferred to v1.4.1+)
- Wire a UI control on the Results step that lets the assessor explicitly set `assessmentStatus = "final"` (currently can only be reached by writing `"full"`/`"complete"` to `completedSteps`).
- Publish a JSON Schema file (`assessment/schema/portal-export.schema.json`) so consumers can validate envelope shape deterministically.
- Backfill the 53 controls with `TODO` priority/yesBar/partialBar/noBar/facilitatorNotes (content work, SME-gated).

---

## Manifest Unification (E0)

### Schema Extension
The `assessment/manifest/controls.json` schema now includes 11 additive fields per control. All existing fields (`id`, `title`, `pillar`, `checks`, `zone_thresholds`, `manual_question`, `automation`, `source_file`, `collection_methods`) remain unchanged—the existing Python engine tests pass without modification.

**New fields:**
- `name` — Display name without "Control X.Y:" prefix (derived from title)
- `zonesApplicable` — Array of zones where the control applies (derived deterministically from `checks[].zone_required`)
- `roles` — Array of canonical administrator role names (parsed from control Roles & Responsibilities section)
- `regulatory` — Array of regulatory tokens (parsed from Regulatory Reference header: FINRA 4511/3110/4530/25-07, SEC 17a-3/17a-4, Reg S-P, SOX, GLBA, OCC 2011-12/2023-17, Fed SR 11-7, CFTC 1.31, NIST AI RMF, NYDFS, HIPAA, PCI, NCUA)
- `priority` — Integer 1–5 (1 = critical, 5 = foundational); `TODO:` placeholder permitted
- `yesBar`, `partialBar`, `noBar` — Human-readable strings describing thresholds; `TODO:` placeholder permitted
- `verifyIn` — Array of portal verification objects (portal name, path, URL)
- `verifyPowerShell` — PowerShell command string for validation
- `evidenceExpected` — Array of expected evidence types (config exports, screenshots, audit logs)
- `controlDocUrl` — Site-root URL to control doc (derived deterministically from `source_file`)
- `portalPlaybookUrl` — Site-root URL to portal-walkthrough playbook (derived from control ID)
- `collectorField` — Collector output JSON path for automated evidence mapping (e.g., `"ppac.settings.dlp.enabled"`)
- `sectorYesBar` — Object with 8 institution-type keys; value is sector-specific yesBar override or `TODO:` placeholder
- `facilitatorNotes` — Object with `ask` (open-ended question), `followUp` (probing questions array), `timeBudgetMinutes` (integer)
- `solutions` — String array of kebab-case folder-name IDs from FSI-AgentGov-Solutions (e.g., `["agent-observability-foundation", "audit-compliance-manager"]`)

### Harvest Script
`scripts/harvest_manifest_extension.py` generates the additive v1.4 fields from existing control markdown files:
- Parses control docs to extract roles, regulatory tokens, zone applicability, and URLs
- Uses `TODO:` placeholders for author-judgment fields (priority, thresholds, facilitator notes, sector calibrations)
- Never overwrites existing values—safe to re-run after manual curation
- Provides console warnings for missing sections or malformed content

### Validators
Three new validation scripts ensure manifest integrity:

**`scripts/validate_manifest.py`:**
- Verifies all 78 controls present with unique IDs
- Checks all v1.4 schema fields exist on every control
- Validates `solutions[]` contains only kebab-case folder-name strings
- Validates `zonesApplicable` subset of {1, 2, 3}
- Validates URLs are site-rooted (e.g., `/controls/pillar-1-security/1.5-dlp/`)
- `--allow-todo` mode permits `TODO:` in authored fields (default for CI during progressive maturation)
- Strict mode (no flag) fails on any `TODO:` occurrence (for production release gate)

**`scripts/validate_solutions_lock.py`:**
- Verifies `assessment/data/solutions-lock.json` schema version starts with `"1.4."`
- Checks all required solution fields present (id, name, version, domain, tier, description, url, prerequisites, verification)
- Cross-references every `controls.json.solutions[]` ID against lock file—emits warning (not failure) if ID missing (graceful degradation contract)
- `--allow-missing` flag skips cross-reference check for early testing

**`scripts/refresh_solutions_lock.py`:**
- Fetches `solutions.json` from FSI-AgentGov-Solutions repository at pinned tag (e.g., v1.4.1)
- Writes to `assessment/data/solutions-lock.json`
- Verifies schema version, expected solution count (35), and presence of 7 v1.4-new solution IDs
- Run only on companion-repo tag bump—not on every framework PR

### Build Integration
`scripts/hooks/copy_assessment_data.py` (mkdocs on_pre_build hook):
- Copies `assessment/manifest/controls.json` to `docs/assessment/data/controls.json` as a static asset
- Enables runtime SPA access via `/assessment/data/controls.json` URL path
- Validates copy succeeded; fails build if manifest missing

---

## Cross-Repo Solutions Integration

Version 1.4.0 establishes a formal contract between FSI-AgentGov and FSI-AgentGov-Solutions for solution metadata exchange.

### Lock-File Architecture
- **Pinned tag**: Framework v1.4.0 pinned to FSI-AgentGov-Solutions v1.4.1 tag (not main branch)
- **Committed lock file**: `assessment/data/solutions-lock.json` committed locally—builds never cross repos at CI time
- **Reproducibility**: Locks tag version, count (35), and expected solution IDs
- **Schema version gate**: Lock file must declare `schemaVersion` starting with `"1.4."` for compatibility validation

### Graceful Degradation
- **Missing solution ID**: Control references a solution not in lock → E1 drawer renders `(solution pending)` chip with console warning
- **Missing lock file**: Lock absent entirely → E1/E7 render without solutions section; build emits warning but does not fail
- **Future-proof**: Schema allows additive solution metadata fields without breaking older framework versions

### URL Constant
All solution links use a single URL base constant: `https://judeper.github.io/FSI-AgentGov-Solutions/solutions/{id}/`

Eliminates scattered hardcoded URLs across codebase; simplifies maintenance if companion repo changes hosting.

---

## Assessment SPA Enhancements (E1–E10)

### E1: How to Verify Drawer
Per-control expandable drawer showing implementation verification steps:
- **Portal paths**: Admin center paths with exact navigation breadcrumbs (e.g., Power Platform Admin Center → Environments → {env} → Settings → Features → Advanced Connector Policies)
- **PowerShell commands**: Copy-pasteable validation commands with parameter examples
- **Expected evidence**: List of evidence types (screenshots, exports, audit logs) with collection instructions
- **Collector field mapping**: Shows which Python collector JSON path auto-populates this control (e.g., `ppac.environments[].settings.acp.enabled`)
- **Solution chips**: Linked chips for matched automation solutions with tier badge (T1/T2/T3) and version pill

### E2: Zone Auto-Exclusion
Controls with zone requirements marked "optional", "awareness-only", or "N/A" are automatically excluded from that zone's aggregate score. Prevents penalizing organizations for enterprise-only controls that don't apply to personal productivity agents.

**Example:** Control 2.19 (Model Risk Management) has Zone 1 requirement "Awareness only"—excluded from Zone 1 percentage calculation but visible in the control list with N/A badge.

### E3: Collector Evidence Import
Phase 1 "Import Collector Data" button accepts JSON outputs from Python assessment collectors (`Collect-PPAC.ps1`, `Collect-Graph.ps1`, `Collect-Purview.ps1`, `Collect-SharePoint.ps1`, `Collect-Sentinel.ps1`). Maps collector fields to control IDs via manifest `collectorField` property and pre-populates responses where evidence threshold met. Speeds assessment by 60–70% for organizations that run automated collectors first.

**Validation:** Sanitizes imported JSON keys, validates structure, ignores unknown fields. Console logs mapping results with match counts.

### E4: Role Filter
Dropdown filter on Phase 1 control list by administrator role (e.g., "Power Platform Admin", "Purview Compliance Admin"). Shows only controls where that role is listed as primary responsible party. Enables role-scoped delegation ("Admin A, complete your 18 controls; Admin B, complete your 22 controls").

**All roles option:** Default shows full 78-control list.

### E5: Sector Calibration
Institution type selection (bank, broker-dealer, investment-adviser, insurance-carrier, insurance-wholesale, credit-union, holding-company, other) on Scoping step adjusts control yesBar thresholds dynamically.

**How it works:** Controls with `sectorYesBar.{type}` override the generic `yesBar` threshold for that institution type. Example: broker-dealer firms may require 7-year audit retention per FINRA while banks default to 5 years per OCC guidance.

**Fallback:** Missing sector overrides gracefully fall back to control-level `yesBar`.

**E1 drawer integration:** Drawer shows sector-adjusted threshold in bold when active.

### E6: Priority Starter Set
One-click filter button showing only the 5 foundation controls (2.1, 1.4, 1.5, 1.7, 1.11) for fast initial assessment. Designed for organizations in early adoption phases who want to validate foundational governance before full 78-control assessment.

**Badge:** Foundation controls display "Priority" badge in Phase 1 list.

**Clear filter:** Button toggles—second click restores full control list.

### E7: Next Session Agenda Export
Results dashboard "Export Agenda" button generates a structured Markdown file listing:
- **Top 10 gaps** (highest riskPriority scores) with current score, gap size, regulatory exposure count, and zone applicability
- **Remediation block per gap**: Lists matched solutions from `solutions-lock.json` with name, tier, description, verification steps, and prerequisites filtered by primary responsible role
- **Phase/wave grouping**: Groups gaps by adoption phase (e.g., "Phase 2: Quick Wins") for incremental remediation
- **Playbook links**: Direct URLs to portal-walkthrough, powershell-setup, verification-testing playbooks

**Formats:** Markdown (.md) for collaborative editing; browser print-to-PDF for distribution.

### E8: Inline Evidence/Notes Capture
Phase 1 response buttons now include optional evidence URL field and notes textarea. Facilitators can document evidence source and implementation caveats at time of scoring instead of retroactively.

**Export integration:** Excel export includes evidence/notes columns; JSON export preserves structured data for re-import.

### E9: Facilitator Mode
URL parameter `?mode=facilitate` unlocks facilitator-specific content:
- **Facilitator hints**: Shows `facilitatorNotes.ask` question and `followUp` probes in E1 drawer
- **Time budgets**: Displays `timeBudgetMinutes` for planning workshop pacing
- **UI badge**: "Facilitator Mode" badge in header confirms mode active
- **Persistent across navigation**: URL parameter preserved during instant navigation

**Security note:** No authentication—facilitator mode is a UI convenience, not a security boundary. All data remains client-side.

### E10: Per-Role Pre-Session Homework Pages
Auto-generated pages at `docs/assessment/pre-session/{role-slug}/index.md` group controls by responsible administrator role. Generated on every build via the `scripts/hooks/generate_homework_pages_hook.py` mkdocs pre-build hook (source: `scripts/generate_homework_pages.py`). The generated directory is gitignored — only the generator and manifest are versioned.

**Top roles (in primary nav):**
- Governance Lead (57 controls)
- Compliance Officer (53 controls)
- Power Platform Admin (44 controls)
- Purview Compliance Admin (17 controls)
- Entra Security Admin (16 controls)
- AI Administrator (14 controls)
- Entra Global Admin (14 controls)
- SharePoint Admin (14 controls)

The full long-tail role set (currently ~140 entries reflecting unnormalized role strings in the in-progress manifest content authoring) is reachable by direct URL and search; the harvester's role normalization will be tightened in a follow-up to collapse near-duplicates.

**Content:** Each page lists control IDs, names, portal-walkthrough playbook links, and verification criteria. Designed for pre-workshop reading assignments ("Before the assessment session, review your assigned controls and collect evidence").

**Navigation:** Added to `mkdocs.yml` under a top-level *Assessment* section linking the assessment tool plus the top eight roles.

---

## Documentation & Consistency

### Control Count Normalization
- **Fixed 71/72 → 78**: Corrected stale control counts across README, AGENTS.md, copilot-instructions.md, framework docs, assessment page, Excel templates, and CONTRIBUTING.md
- **Pillar totals updated**: Security 29, Management 26, Reporting 14, SharePoint 9 (total 78)

### Version Bump
- **1.3.3 → 1.4.0**: Updated version strings in README badge, mkdocs.yml, CITATION.cff, package manifests, and all meta references
- **Footer metadata**: Updated footer version references across framework and control docs where v1.3 appeared

### Existing Content Corrections
- **Assessment page "About This Tool"**: Added v1.4 enhancements paragraph (how-to-verify drawer, sector calibration, solutions bridge, pre-session homework)
- **CONTRIBUTING.md manifest section**: Documented single source of truth architecture, mkdocs hook, validator usage, and solutions lock-file contract

---

## Breaking Changes

### Assessment SPA Export Schema
The assessment tool's exported JSON schema has changed and is **NOT backward compatible** with v1.3.x exports.

**What changed:**
- Added `evidence`, `notes`, `sectorType`, `facilitatorMode` fields to scoping object
- Added `evidence`, `notes` fields per Phase 1 response
- Added `sectorAdjustedThreshold` boolean per control in results
- Renamed `savedAssessments` localStorage key to `savedAssessments_v1.4` to prevent schema conflicts

**Impact:** Organizations with in-progress v1.3.x assessments exported to JSON cannot re-import them into v1.4.0 SPA. Attempts to import will fail schema validation with console error.

**Migration:** No automated migration tool provided. Recommendation: Complete in-progress v1.3.x assessments in the v1.3.4 release before upgrading, or re-run assessment from scratch in v1.4.0 (collector import mitigates re-entry burden).

**Why no migration:** The added evidence/notes fields and sector calibration require user input that doesn't exist in v1.3 exports—automated backfill would produce incomplete records.

---

## Cross-Repo Compatibility

**FSI-AgentGov v1.4.0 is compatible with FSI-AgentGov-Solutions v1.4.1.**

Control→solution references in `assessment/manifest/controls.json` use folder-name IDs (e.g., `"agent-observability-foundation"`, `"audit-compliance-manager"`) that match the top-level solution directories in the companion repository. Solution metadata (display name, version, tier, description, URL, prerequisites, verification steps) is looked up from the committed `assessment/data/solutions-lock.json` file, which was generated from the FSI-AgentGov-Solutions v1.4.1 tag.

The canonical path for the cross-repository solutions lock file is `assessment/data/solutions-lock.json`; it is consumed by `docs/javascripts/assessment-app.js`, `tests/spa/solutions-lock.test.mjs`, `scripts/refresh_solutions_lock.py`, `scripts/validate_solutions_lock.py`, and `scripts/hooks/copy_assessment_data.py`.

Organizations using both repositories should upgrade in sequence:
1. Verify FSI-AgentGov-Solutions v1.4.1 is tagged and published
2. Run `python scripts/refresh_solutions_lock.py --tag v1.4.1` to update lock file
3. Validate lock contains 35 solutions and 7 expected new IDs
4. Merge FSI-AgentGov v1.4.0 branch

The lock-file contract ensures FSI-AgentGov builds remain reproducible even if the companion repository updates—framework CI never crosses repos at build time.

---

## Internal Refactoring

### Phase A — Foundation Work
The v1.4.0 release was structured as a phased implementation with Phase A (E0 manifest unification) as the blocking foundation for all subsequent SPA enhancements.

**Phase A deliverables:**
- Extended `controls.json` schema with 11 additive fields
- Harvest script to scaffold v1.4 fields from existing control docs
- Three validators (manifest schema, solutions lock, cross-references)
- Solutions lock refresh script
- MkDocs build hook for static asset delivery
- 11 new pytest tests validating manifest structure

**Total tests after Phase A:** 22 passed (11 baseline engine tests + 11 new manifest tests)

### MkDocs Hook
`scripts/hooks/copy_assessment_data.py` registered in `mkdocs.yml` as `on_pre_build` hook:
```python
hooks:
  - scripts/hooks/copy_assessment_data.py
```

Copies `assessment/manifest/controls.json` → `docs/assessment/data/controls.json` before site build. SPA loads manifest via `/assessment/data/controls.json` static asset path at runtime.

**Validation:** Hook logs copy operation to stdout; fails build with exit code 1 if source manifest missing or copy fails.

### Validator Integration
CI workflow (`publish_docs.yml`) runs validators before build:
```bash
python scripts/validate_manifest.py --allow-todo
python scripts/validate_solutions_lock.py --allow-missing
mkdocs build --strict
```

`--allow-todo` mode permits progressive authoring (controls can have `TODO:` in priority/threshold fields during maturation). Production release gate switches to strict mode (no `TODO:` allowed).

---

## Migration Notes

### For Framework Contributors
After the companion FSI-AgentGov-Solutions repository cuts a new tag (e.g., v1.5.0):

1. **Refresh solutions lock:**
   ```bash
   python scripts/refresh_solutions_lock.py --tag v1.5.0
   ```
   This fetches the updated `solutions.json` from the new tag and writes to `assessment/data/solutions-lock.json`.

2. **Validate lock file:**
   ```bash
   python scripts/validate_solutions_lock.py
   ```
   Verifies schema version, count, and cross-references against current `controls.json`.

3. **Commit lock update:**
   ```bash
   git add assessment/data/solutions-lock.json
   git commit -m "chore: refresh solutions lock to v1.5.0"
   ```

4. **Update CHANGELOG:** Document compatibility with the new companion tag version.

### For Assessment Tool Users
**No migration steps required.** Assessment data stays in browser localStorage; no server-side state. Organizations re-running assessments after upgrade start fresh (or import collector JSON to accelerate).

**Facilitators using v1.3.x JSON exports:** Export must be completed in v1.3.4 release before upgrading to v1.4.0, or re-run assessment using v1.4.0 collector import feature.

### For Companion Solutions Maintainers
When adding new solutions to FSI-AgentGov-Solutions:

1. **Add solution metadata** to `solutions.json` (id, name, version, domain, tier, description, url, prerequisites, verification)
2. **Tag release** (e.g., `v1.5.0`)
3. **Notify framework maintainers** to refresh lock file via `refresh_solutions_lock.py --tag v1.5.0`
4. **Update control references** in FSI-AgentGov `controls.json` to include new solution ID in `solutions[]` array where applicable

---

## Known Limitations

### Author-Judgment Fields
Approximately 50 controls have `TODO:` placeholders in author-judgment fields:
- `priority` (1–5 scale)
- `yesBar`, `partialBar`, `noBar` (threshold descriptions)
- `facilitatorNotes.ask`, `facilitatorNotes.followUp`, `facilitatorNotes.timeBudgetMinutes`
- `sectorYesBar.{institution-type}` (546 sector-specific thresholds across 78 controls × 7 regulated sectors)

These fields require subject-matter expertise and regulatory interpretation. They will be progressively populated in subsequent v1.4.x patch releases as control reviews complete. The validator's `--allow-todo` mode permits CI to pass during progressive maturation.

**Impact on SPA:** Controls with `TODO:` thresholds fall back to generic descriptions ("Implementation required", "Partial implementation", "Not implemented"). Facilitator hints do not render if `TODO:` placeholder present.

### Sector Calibration Coverage
Only ~15 controls (primarily audit, retention, DLP, and reporting controls) have institution-type-specific threshold overrides in v1.4.0. Remaining controls use generic `yesBar` for all sectors. Sector calibration will expand in future releases as regulatory-mapping research completes.

### Collector Field Mapping
Only ~40 controls have `collectorField` mappings for automated evidence import. Controls requiring manual attestation (human-in-the-loop approvals, governance committee decisions, policy acknowledgments) cannot be auto-populated from collector JSON. The E3 collector import feature marks these controls as "Manual review required" in import results.

---

## Test Coverage

### Python Tests
`assessment/tests/` directory contains 22 pytest tests:
- 11 baseline engine tests (scoring, thresholds, manual questions)
- 11 new manifest validation tests (schema, solutions[], zones, URLs, count consistency)

**Run tests:**
```bash
cd assessment
pytest tests/ -v
```

All 22 tests pass with the extended v1.4 manifest schema.

### JavaScript Tests
*(Planned for future release — not included in v1.4.0)*

E1–E10 SPA enhancements currently validated via manual testing and Playwright end-to-end tests. Unit tests for scoring math, zone exclusion, sector fallback, and collector mapping logic planned for v1.4.1.

### Playwright Tests
*(Planned for future release — not included in v1.4.0)*

End-to-end workflow tests covering full assessment lifecycle (scoping → Phase 1 → Phase 2 → results → export) with snapshot diff validation for agenda export. UI component tests for drawer, filter, collector import, sector selector.

---

*Updated: April 2026 | Version: v1.4.0 | Status: Released*
