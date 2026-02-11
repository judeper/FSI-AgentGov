# Roadmap: Conditional Access Automation (v10)

## Overview

The Conditional Access Automation solution extends existing validated scripts (Deploy-CAPolicies.ps1, Register-ServicePrincipal.ps1, Test-PolicyCompliance.ps1) with Tier 2 governance infrastructure to create a complete policy lifecycle management solution for Controls 1.11, 1.23, and 1.18. The build follows the proven Tier 2 pattern: script modernization with module structure first, then Dataverse infrastructure for persistent state, then Power Automate automation with drift detection and alerting, and finally evidence export with framework integration.

**Existing assets:** 3 PowerShell scripts, 8 zone-specific CA policy templates (JSON), 5 documentation files in FSI-AgentGov-Solutions companion repo. Status: Validated.

**Key insight:** Unlike other Tier 2 solutions that purely monitor configuration, this solution both *deploys* CA policies and *validates* compliance. The deployment path (report-only → enforced) with break-glass exclusions is already implemented. The gap is persistent state management, automated compliance scanning, drift detection, and evidence export — the same infrastructure all Tier 2 solutions share.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work

- [ ] **Phase 1: Script Modernization & Core Validation** — Module structure, template validation, zone integration, drift detection core
- [ ] **Phase 2: Dataverse Infrastructure** — Persistent state tables, environment variables, connection references, deployment scripts
- [x] **Phase 3: Automation & Alerting** — Daily compliance scan flow, drift detection, Teams alerting, ELM provisioning hook
- [x] **Phase 4: Evidence Export & Framework Integration** — SHA-256 evidence export, Control 1.11 integration, solutions-index, documentation, CD feed

## Phase Details

### Phase 1: Script Modernization & Core Validation
**Goal**: Existing scripts are modernized to Tier 2 standards with module structure, zone lookup integration, and policy drift detection — operators can validate CA policy compliance and detect unauthorized changes using standalone scripts
**Depends on**: Nothing (first phase)
**Requirements**: SMC-01, SMC-02, SMC-03, SMC-04, SMC-05
**Success Criteria** (what must be TRUE):
  1. CAAClient PowerShell module exports core functions following Tier 2 conventions (ErrorAction, #Requires, help comments) consistent with ACV/SSC/AAM module patterns
  2. All 8 CA policy templates validated against current Graph API schema with any needed updates applied
  3. Zone lookup retrieves environment zone from ELM Dataverse table with naming convention fallback, enabling zone-appropriate policy deployment
  4. All deployment and compliance operations support dry-run mode with detailed preview output showing what would change
  5. Policy drift detection compares deployed CA policies against template baselines and identifies unauthorized modifications (enabled→disabled, conditions changed, controls weakened)
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Solution scaffold, module manifest, and private helpers (SMC-01, SMC-03)
- [ ] 01-02-PLAN.md — Template validation and script refactoring with dry-run (SMC-02, SMC-04)
- [ ] 01-03-PLAN.md — Policy drift detection scripts (SMC-05)

### Phase 2: Dataverse Infrastructure
**Goal**: CA policy baselines, validation history, and violation records are stored in Dataverse for persistent, queryable state across automated runs
**Depends on**: Phase 1
**Requirements**: INF-01, INF-02, INF-03, INF-04
**Success Criteria** (what must be TRUE):
  1. Dataverse schema deployed with CA policy baseline, validation history (immutable), and violation tables reusing existing `fsi_acv_zone` and `fsi_acv_severity` option sets
  2. Environment variables for zone-specific CA policy thresholds (`fsi_CAA_*` prefix) deployed and consumed by Phase 1 scripts
  3. Connection references for Dataverse, Office 365, Teams, and Microsoft Graph deployed with `fsi_cr_*` naming convention
  4. Python deployment scripts are idempotent (safe to re-run) and support dry-run mode, following ACV/SSC/AAM pattern
**Plans**: TBD

### Phase 3: Automation & Alerting
**Goal**: CA policy compliance is automatically validated daily with drift detection, and operators receive classified alerts when policies deviate from zone requirements or are modified outside automation
**Depends on**: Phase 2
**Requirements**: AUT-01, AUT-02, AUT-03, AUT-04
**Success Criteria** (what must be TRUE):
  1. Power Automate daily compliance scan flow executes Test-PolicyCompliance logic against all tracked environments and writes results to immutable validation history
  2. Drift detection identifies unauthorized CA policy modifications (policy disabled, conditions weakened, grant controls changed) by comparing against stored baselines
  3. Teams adaptive card alerts sent with severity classification (Zone 3 CRITICAL, Zone 2 HIGH, Zone 1 WARNING) and specific violation details
  4. ELM provisioning hook triggers zone-appropriate CA policy deployment when new environments are provisioned
**Plans**: 4 plans

Plans:
- [x] 03-01-PLAN.md — Azure Automation runbook wrapper (AUT-01 partial, AUT-02)
- [x] 03-02-PLAN.md — Teams adaptive card template (AUT-03)
- [x] 03-03-PLAN.md — Power Automate daily compliance scan flow (AUT-01)
- [x] 03-04-PLAN.md — ELM provisioning hook flow (AUT-04)

**Status:** COMPLETE (2026-02-10) — 4/4 plans, 2 waves, verification PASSED

### Phase 4: Evidence Export & Framework Integration
**Status:** COMPLETE (2026-02-10) — 4/4 plans, 2 waves, verification PASSED
**Goal**: CA policy compliance evidence is exportable for regulatory examinations and the solution is fully integrated into the FSI-AgentGov framework documentation and Compliance Dashboard
**Depends on**: Phase 3
**Requirements**: EFR-01, EFR-02, EFR-03, EFR-04, EFR-05
**Success Criteria** (what must be TRUE):
  1. Operator can export CA policy compliance evidence with SHA-256 integrity hashing producing a verifiable manifest for FINRA/SEC examination support
  2. Control 1.11 documentation includes tip admonition linking to the Conditional Access Automation solution
  3. solutions-index.md catalog entry updated from Work In Progress to Completed with version, description, and related controls
  4. Complete documentation suite in companion repo covering prerequisites, Dataverse schema, deployment, troubleshooting, and CHANGELOG
  5. Compliance Dashboard receives automated Control 1.11 assessment scores via v9 integration feed pattern
**Plans**: 4 plans

Plans:
- [x] 04-01-PLAN.md — SHA-256 evidence export scripts (EFR-01)
- [x] 04-02-PLAN.md — Control 1.11 tip admonition and solutions-index.md update (EFR-02, EFR-03)
- [x] 04-03-PLAN.md — Companion repo documentation suite and CHANGELOG (EFR-04)
- [x] 04-04-PLAN.md — Compliance Dashboard feed integration (EFR-05)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|---------------|--------|-----------|
| 1. Script Modernization & Core | — | Not Started | — |
| 2. Dataverse Infrastructure | — | Not Started | — |
| 3. Automation & Alerting | 4/4 | Complete | 2026-02-10 |
| 4. Evidence Export & Framework Integration | 4/4 | Complete | 2026-02-10 |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| SMC-01 | Phase 1 | 01-01 | CAAClient module structure |
| SMC-02 | Phase 1 | 01-02 | Policy template Graph API validation |
| SMC-03 | Phase 1 | 01-01 | Zone lookup ELM integration |
| SMC-04 | Phase 1 | 01-02 | Dry-run mode for all operations |
| SMC-05 | Phase 1 | 01-03 | Policy drift detection |
| INF-01 | Phase 2 | TBD | Dataverse tables (baseline, history, violations) |
| INF-02 | Phase 2 | TBD | Environment variables (fsi_CAA_*) |
| INF-03 | Phase 2 | TBD | Connection references |
| INF-04 | Phase 2 | TBD | Python deployment scripts |
| AUT-01 | Phase 3 | 03-01, 03-03 | Daily compliance scan flow |
| AUT-02 | Phase 3 | 03-01 | Drift detection flow |
| AUT-03 | Phase 3 | 03-02 | Teams adaptive card alerts |
| AUT-04 | Phase 3 | 03-04 | ELM provisioning hook |
| EFR-01 | Phase 4 | 04-01 | SHA-256 evidence export |
| EFR-02 | Phase 4 | 04-02 | Control 1.11 framework integration |
| EFR-03 | Phase 4 | 04-02 | solutions-index.md update |
| EFR-04 | Phase 4 | 04-03 | Documentation suite |
| EFR-05 | Phase 4 | 04-04 | Compliance Dashboard feed |

**Total: 18/18 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-10*
*Depth: comprehensive*
*Phases: 4 (scripts → dataverse → automation → integration)*

