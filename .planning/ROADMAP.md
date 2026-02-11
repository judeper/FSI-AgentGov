# Roadmap: SSPM Control Coverage Remediation (v14)

## Overview

Remediates SSPM control coverage gaps across 7 controls (1.1, 1.7, 1.8, 1.18, 2.1, 3.7, 3.8) identified by the SSPM alert-to-control mapping analysis. Ensures all 27 in-scope SSPM alerts have proper framework coverage (controls, playbooks, verification criteria), creates a PowerShell hardening baseline verification script, and updates reference catalogs.

**Source:** SSPM alert-to-control mapping analysis (maintainers-local/sspm-alert-mapping.md) — 42 alerts analyzed, 27 in-scope, 13 requirements defined.

**Execution model:** 4 phases. Phases 1 and 2 are independent (different file sets) and can run in parallel. Phase 3 depends on both. Phase 4 depends on all prior phases.

## Phases

- [x] **Phase 1: Control SSPM Alignment** — Bump 3.7 to v1.3, audit 27 SSPM alerts against verification criteria in 7 controls, add GLIC advisory cross-references
- [x] **Phase 2: Hardening Baseline Production** — Add automation feasibility classification, create PowerShell verification script, document evidence export procedures
- [x] **Phase 3: Playbook Remediation** — Remediate 7 portal-walkthrough and 7 verification-testing playbooks for SSPM coverage, add hardening baseline cross-links
- [x] **Phase 4: Reference Updates & Validation** — Update solutions catalog and CONTROL-INDEX, run final build and language validation

## Phase Details

### Phase 1: Control SSPM Alignment
**Goal:** Align 7 SSPM-mapped control files to v1.3 standard with complete verification criteria coverage of all 27 SSPM-flagged configuration points, and add GLIC advisory cross-references
**Depends on:** Nothing (foundational — control changes inform downstream phases)
**Requirements:** CTL-01, CTL-02, CTL-03
**Success Criteria:**
  1. Control 3.7 bumped to v1.3 with aligned footer and complete hardening section
  2. All 27 SSPM alert configuration points have matching verification criteria in their parent control's Section 9
  3. Controls 1.1 and 1.11 include GLIC cross-reference advisory notes for MFA enforcement (Ref 41) and Guest User access (Ref 39)
**Plans:** 2 (A = CTL-01 3.7 v1.3 bump + CTL-02 verification criteria audit across 7 controls, B = CTL-03 GLIC advisory to 1.1 and 1.11)

### Phase 2: Hardening Baseline Production
**Goal:** Finalize the configuration hardening baseline with automation feasibility classification, a PowerShell verification script for automatable items, and evidence export procedures
**Depends on:** Nothing (parallel with Phase 1 — operates on baseline doc and scripts, not control files)
**Requirements:** HBL-01, HBL-02, HBL-03
**Success Criteria:**
  1. 27-item hardening baseline checklist has automation feasibility column (Automated / Semi-Automated / Manual Attestation)
  2. `scripts/governance/Invoke-HardeningBaselineCheck.ps1` validates automatable items (audit logging 7–9, environment provisioning 14–17) via Power Platform Admin Connector and Graph API with pass/fail output and evidence export
  3. Hardening baseline includes evidence export procedures and zone-specific review cadence guidance with SHA-256 hash pattern
**Plans:** 2 (A = HBL-01 automation classification + HBL-03 evidence export and cadence, B = HBL-02 PowerShell verification script)

### Phase 3: Playbook Remediation
**Goal:** Update 14 playbooks (7 portal-walkthrough + 7 verification-testing) to reflect SSPM-aligned controls and add hardening baseline cross-links to control Section 8s
**Depends on:** Phase 1 (control changes inform playbook content) + Phase 2 (baseline doc to cross-link)
**Requirements:** PLB-01, PLB-02, PLB-03
**Success Criteria:**
  1. 7 portal-walkthrough playbooks remediated to cover all SSPM-detectable settings with explicit portal steps
  2. 7 verification-testing playbooks include SSPM-informed test cases (e.g., authentication mode validation, audit retention checks)
  3. Section 8 (Implementation Guides) of all 7 SSPM-mapped controls links to Configuration Hardening Baseline advanced implementation
**Plans:** 2 (A = PLB-01 portal-walkthrough remediation + PLB-03 Section 8 cross-links, B = PLB-02 verification-testing SSPM test cases)

### Phase 4: Reference Updates & Validation
**Goal:** Update reference catalogs to reflect v14 changes and run final validation across all modified files
**Depends on:** Phases 1–3 (needs all content changes finalized before catalog updates and validation)
**Requirements:** REF-01, REF-02, VAL-01, VAL-02
**Success Criteria:**
  1. solutions-index.md includes Configuration Hardening Baseline entry; solutions-coverage-gaps.md updated for 7 controls
  2. CONTROL-INDEX.md descriptions for 7 SSPM-mapped controls note v1.3 enhancements
  3. All 7 controls pass `verify_controls.py` with v1.3 footer and `mkdocs build --strict` produces 0 errors
  4. `verify_language_rules.py` reports zero prohibited phrases across all updated controls, playbooks, and baseline
**Plans:** 2 (A = REF-01 solutions catalog + REF-02 CONTROL-INDEX descriptions, B = VAL-01 build validation + VAL-02 language rules)

## Progress

| Phase | Plans Complete | Status |
|-------|---------------|--------|
| 1. Control SSPM Alignment | 2/2 | Complete |
| 2. Hardening Baseline Production | 2/2 | Complete |
| 3. Playbook Remediation | 2/2 | Complete |
| 4. Reference Updates & Validation | 2/2 | Complete |

## Parallel Execution Guide

Phases 1 and 2 have **no file overlap** and can run in parallel:

| Phase | Plan A Files | Plan B Files |
|-------|-------------|-------------|
| 1 | docs/controls/pillar-1-security/1.1-*.md, 1.7-*.md, 1.8-*.md, 1.18-*.md, docs/controls/pillar-2-management/2.1-*.md, docs/controls/pillar-3-reporting/3.7-*.md, 3.8-*.md | docs/controls/pillar-1-security/1.1-*.md, 1.11-*.md |
| 2 | docs/playbooks/advanced-implementations/configuration-hardening-baseline/ | scripts/governance/Invoke-HardeningBaselineCheck.ps1 |
| 3 | 7 portal-walkthrough playbooks + 7 control Section 8s | 7 verification-testing playbooks |
| 4 | docs/reference/solutions-index.md, solutions-coverage-gaps.md, CONTROL-INDEX.md | Validation scripts (read-only) |

**Phase 1 Plan A/B overlap:** Both plans touch Control 1.1 — Plan A adds verification criteria, Plan B adds GLIC advisory. Execute sequentially (A→B) within Phase 1.

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| CTL-01 | 1 | 01-01 | Control 3.7 v1.3 bump |
| CTL-02 | 1 | 01-01 | 27-alert verification criteria audit across 7 controls |
| CTL-03 | 1 | 01-02 | GLIC advisory cross-references (1.1, 1.11) |
| HBL-01 | 2 | 02-01 | Automation feasibility classification column |
| HBL-03 | 2 | 02-01 | Evidence export procedures + zone-specific cadence |
| HBL-02 | 2 | 02-02 | PowerShell hardening baseline verification script |
| PLB-01 | 3 | 03-01 | Portal-walkthrough playbook remediation |
| PLB-03 | 3 | 03-01 | Hardening baseline cross-links in control Section 8 |
| PLB-02 | 3 | 03-02 | Verification-testing SSPM test cases |
| REF-01 | 4 | 04-01 | Solutions catalog + coverage gaps update |
| REF-02 | 4 | 04-01 | CONTROL-INDEX description updates |
| VAL-01 | 4 | 04-02 | Build validation (verify_controls.py + mkdocs build) |
| VAL-02 | 4 | 04-02 | Language rules validation (verify_language_rules.py) |

**Total: 13/13 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-11*
*Depth: comprehensive*
*Phases: 4 (control alignment + hardening baseline → playbook remediation → reference + validation)*
