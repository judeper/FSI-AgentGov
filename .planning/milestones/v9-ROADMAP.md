# Roadmap: Cross-Solution Integration (v9)

## Overview

Cross-solution integration that wires the 5 Tier 2 governance solutions (ACV, SSC, AAM, CMM, FUS) into the Compliance Dashboard, adds ELM provisioning hooks for downstream solution initialization, and delivers unified evidence export for regulatory examinations. This milestone transitions standalone solutions into an integrated governance platform.

**Key insight:** Each Tier 2 solution follows identical triple-table architecture (baseline → validation history → violation) with shared option sets (`fsi_acv_zone`, `fsi_acv_severity`). The integration layer maps each solution's `overall_status` to the Compliance Dashboard's `fsi_controlassessment` table, creating automated compliance scoring for 7 controls across 5 solutions. ELM provisioning completion events cascade to ACV environment auto-registration, closing the environment-to-validation lifecycle gap.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4, 5): Planned milestone work

- [x] **Phase 1: Schema Normalization & Integration Constants** — Canonical option set contract, status mapping reference, and shared integration module
- [x] **Phase 2: Compliance Dashboard Feed Layer** — Solution-to-dashboard data pipeline with PowerShell sync script, flow definition, and evidence auto-registration
- [x] **Phase 3: ELM Provisioning Hooks** — Post-provisioning child flow, ACV environment auto-registration, and integration configuration
- [x] **Phase 4: Unified Evidence Export** — Master evidence aggregation, manifest generation, and integrity chain validation
- [x] **Phase 5: Documentation & Framework Integration** — Architecture docs, solutions-index updates, CD README updates, and integration solution docs

## Phase Details

### Phase 1: Schema Normalization & Integration Constants
**Goal**: Establish the canonical data contract that all solutions and integration components reference — option set alignment, status mapping logic, and a shared constants module
**Depends on**: Nothing (first phase)
**Requirements**: SCH-01, SCH-02, SCH-03
**Success Criteria** (what must be TRUE):
  1. Canonical option set contract documented with zone values (1/2/3) and severity values (1-5) as the cross-solution standard
  2. Status mapping reference defines per-solution translation from `overall_status` → CD `fsi_status` with explicit logic
  3. `IntegrationConfig.psm1` provides exported functions for solution-to-control mapping, severity translation, and table name lookups
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Canonical option set contract and status mapping reference document (SCH-01, SCH-02)
- [x] 01-02-PLAN.md — IntegrationConfig.psm1 shared constants module (SCH-03)
- [x] 01-03-PLAN.md — Integration solution scaffold and directory structure

### Phase 2: Compliance Dashboard Feed Layer
**Goal**: Daily automated pipeline that pulls validation results from all 5 Tier 2 solutions, creates/updates CD assessments per control, auto-registers evidence, and updates the CD score calculator
**Depends on**: Phase 1
**Requirements**: CDF-01, CDF-02, CDF-03, CDF-04, CDF-05
**Success Criteria** (what must be TRUE):
  1. `Sync-SolutionAssessments.ps1` queries 5 solution validation history tables, translates status/severity, and upserts `fsi_controlassessment` records for 7 controls
  2. CD-SolutionFeedCollector flow definition triggers daily sync with configurable schedule
  3. Evidence auto-registration creates `fsi_complianceevidence` records with SHA-256 hashes from Tier 2 solution evidence exports
  4. CD-ScoreCalculator flow updated to differentiate automated (solution-sourced) vs manual assessments
**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md — Sync-SolutionAssessments.ps1 PowerShell script with per-solution query and CD upsert logic (CDF-02, CDF-03)
- [x] 02-02-PLAN.md — Evidence auto-registration and CD evidence linking (CDF-04)
- [x] 02-03-PLAN.md — CD-SolutionFeedCollector flow definition (CDF-01)
- [x] 02-04-PLAN.md — CD-ScoreCalculator flow update for automated assessment weighting (CDF-05)

### Phase 3: ELM Provisioning Hooks
**Goal**: When ELM provisions a new environment, automatically register it in ACV and notify downstream solutions, closing the environment-to-validation lifecycle gap
**Depends on**: Phase 1
**Requirements**: ELM-01, ELM-02, ELM-03
**Success Criteria** (what must be TRUE):
  1. `ELM-SolutionInitializer` child flow triggers on ProvisioningCompleted log entry
  2. ACV `fsi_environmentregistry` record auto-created with zone, environment ID, URL, and status from ELM request
  3. Integration configuration document defines the cascade contract per downstream solution
**Plans**: 3 plans

Plans:
- [x] 03-01-PLAN.md — ELM-SolutionInitializer child flow definition (ELM-01, ELM-03)
- [x] 03-02-PLAN.md — ACV environment auto-registration logic (ELM-02)
- [x] 03-03-PLAN.md — Integration configuration and cascade contract documentation (ELM-03)

### Phase 4: Unified Evidence Export
**Goal**: Single-command evidence aggregation from all Tier 2 solutions into a master evidence package with SHA-256 chain integrity for quarterly regulatory examinations
**Depends on**: Phases 2, 3
**Requirements**: UEV-01, UEV-02, UEV-03
**Success Criteria** (what must be TRUE):
  1. `Export-UnifiedComplianceEvidence.ps1` orchestrates per-solution evidence export and produces master package
  2. Master manifest JSON includes solution inventory, per-solution hashes, timestamps, and compliance summary
  3. `Test-UnifiedEvidenceIntegrity.ps1` verifies all solution evidence packages and master manifest hash chain
**Plans**: 3 plans

Plans:
- [x] 04-01-PLAN.md — Export-UnifiedComplianceEvidence.ps1 orchestration script (UEV-01, UEV-02)
- [x] 04-02-PLAN.md — Master evidence manifest and integrity chain (UEV-02)
- [x] 04-03-PLAN.md — Test-UnifiedEvidenceIntegrity.ps1 validation script (UEV-03)

### Phase 5: Documentation & Framework Integration
**Goal**: Update framework documentation, solutions-index, and Compliance Dashboard README to reflect the integrated governance platform
**Depends on**: Phases 1-4
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04
**Success Criteria** (what must be TRUE):
  1. Integration architecture document describes cross-solution data flow with diagram
  2. solutions-index.md updated with integration status badges for connected solutions
  3. Compliance Dashboard README updated with Tier 2 solution feed documentation
  4. Complete integration solution docs suite shipped
**Plans**: 3 plans

Plans:
- [x] 05-01-PLAN.md — Integration architecture framework document (DOC-01)
- [x] 05-02-PLAN.md — solutions-index.md and control updates (DOC-02)
- [x] 05-03-PLAN.md — CD README update and integration solution docs suite (DOC-03, DOC-04)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2/3 (parallel possible) → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|---------------|--------|-----------|
| 1. Schema Normalization | 3/3 | COMPLETE | 2026-02-10 |
| 2. Dashboard Feed Layer | 4/4 | COMPLETE | 2026-02-10 |
| 3. ELM Provisioning Hooks | 3/3 | COMPLETE | 2026-02-10 |
| 4. Unified Evidence Export | 3/3 | COMPLETE | 2026-02-10 |
| 5. Documentation & Framework | 3/3 | COMPLETE | 2026-02-10 |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| SCH-01 | Phase 1 | 01-01 | Canonical option set contract |
| SCH-02 | Phase 1 | 01-01 | Solution status mapping reference |
| SCH-03 | Phase 1 | 01-02 | IntegrationConfig.psm1 shared module |
| CDF-01 | Phase 2 | 02-03 | CD-SolutionFeedCollector flow |
| CDF-02 | Phase 2 | 02-01 | Solution-to-control mapping table |
| CDF-03 | Phase 2 | 02-01 | Sync-SolutionAssessments.ps1 |
| CDF-04 | Phase 2 | 02-02 | Evidence auto-registration |
| CDF-05 | Phase 2 | 02-04 | CD-ScoreCalculator update |
| ELM-01 | Phase 3 | 03-01 | ELM-SolutionInitializer flow |
| ELM-02 | Phase 3 | 03-02 | ACV environment auto-registration |
| ELM-03 | Phase 3 | 03-01 | Integration cascade configuration |
| UEV-01 | Phase 4 | 04-01 | Export-UnifiedComplianceEvidence.ps1 |
| UEV-02 | Phase 4 | 04-02 | Master evidence manifest |
| UEV-03 | Phase 4 | 04-03 | Test-UnifiedEvidenceIntegrity.ps1 |
| DOC-01 | Phase 5 | 05-01 | Integration architecture document |
| DOC-02 | Phase 5 | 05-02 | solutions-index.md updates |
| DOC-03 | Phase 5 | 05-03 | CD README updates |
| DOC-04 | Phase 5 | 05-03 | Integration solution docs |

**Total: 18/18 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-10*
*Depth: comprehensive*
*Phases: 5 (schema → dashboard feeds → ELM hooks → evidence → docs)*

