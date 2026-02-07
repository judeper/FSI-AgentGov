# Roadmap: Session Security Configurator (v5)

## Overview

The Session Security Configurator automates Conditional Access session control enforcement per governance zone for Control 1.23. The build follows the proven ACV Tier 2 pattern: standalone PowerShell scripts first (auth contexts, step-up policies, zone validation, dry-run mode), then Dataverse infrastructure for persistent state, then Power Automate automation with drift detection and alerting, and finally evidence export with framework integration. Each phase delivers a verifiable capability that the next phase builds on.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (e.g., 2.1): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: PowerShell Core** - Authentication context lifecycle, step-up policy deployment, zone validation, and safety controls
- [ ] **Phase 2: Dataverse Infrastructure** - Persistent state tables, environment variables, connection references, and deployment scripts
- [ ] **Phase 3: Automation and Alerting** - Scheduled drift detection, Teams alerting, Power Automate flow, and baseline management
- [ ] **Phase 4: Evidence Export and Framework Integration** - SHA-256 compliance export, Control 1.23 integration, and documentation suite

## Phase Details

### Phase 1: PowerShell Core
**Goal**: Operators can deploy, validate, and preview session security configurations per governance zone using standalone PowerShell scripts
**Depends on**: Nothing (first phase)
**Requirements**: SCM-01, SCM-02, SCM-03, SCM-04, SCM-05, SCM-06, SCM-07
**Success Criteria** (what must be TRUE):
  1. Operator can deploy authentication contexts (c1-c5) with conflict detection for pre-existing contexts, and the script aborts with a clear warning if contexts are already in use
  2. Operator can deploy step-up CA policies in report-only mode with zone-specific session controls (8h/4h/1h sign-in frequency, authentication strength per zone) and the script refuses to deploy in enforced mode without a 72-hour report-only bake period
  3. Operator can run dry-run mode on any deployment operation and see a preview of all changes that would be made without any tenant modifications occurring
  4. Operator can run zone validation that reports pass/fail/warning status for each zone, covering session controls, authentication strength policies, PIM settings, and break-glass exclusions
  5. Operator can see a pre-deployment CA policy conflict audit that identifies overlapping policies which would create unpredictable session timeouts
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Solution scaffold, private helpers, and JSON templates
- [x] 01-02-PLAN.md — Deploy-AuthContexts.ps1 and Deploy-StepUpPolicies.ps1
- [x] 01-03-PLAN.md — Test-SessionCompliance.ps1 validation orchestrator

### Phase 2: Dataverse Infrastructure
**Goal**: Session baselines, validation history, and configuration thresholds are stored in Dataverse for persistent, queryable state across automated runs
**Depends on**: Phase 1
**Requirements**: INF-01, INF-02, INF-03, INF-05
**Success Criteria** (what must be TRUE):
  1. Dataverse schema is deployed with session baseline, validation history (immutable), and drift violation tables that reuse existing ACV option sets (fsi_acv_zone, fsi_acv_severity)
  2. Environment variables for zone-specific session thresholds (fsi_SSC_* prefix) are deployed and Phase 1 scripts read thresholds from them instead of hardcoded values
  3. Connection references for Dataverse, Office 365, and Teams are deployed with fsi_cr_* naming convention
  4. Python deployment scripts are idempotent (safe to re-run) and support dry-run mode, following the ACV pattern
**Plans**: 3 plans

Plans:
- [ ] 02-01-PLAN.md — SSC Dataverse client, requirements, and three-table schema deployment
- [ ] 02-02-PLAN.md — Environment variables, connection references, and deploy.py orchestrator
- [ ] 02-03-PLAN.md — Wire Phase 1 PowerShell scripts to read thresholds from Dataverse

### Phase 3: Automation and Alerting
**Goal**: Session security drift is automatically detected daily and operators receive classified alerts when configuration deviates from baselines
**Depends on**: Phase 2
**Requirements**: DDA-01, DDA-02, DDA-03, DDA-04, INF-04
**Success Criteria** (what must be TRUE):
  1. A scheduled Power Automate flow runs daily drift detection that compares live CA session controls against Dataverse baselines and writes results to immutable validation history
  2. When drift is detected (sign-in frequency weakened, auth strength downgraded, policy disabled, exclusions added), a Teams adaptive card alert is sent with severity classification matching the zone affected
  3. Operators can capture a baseline snapshot and compare subsequent scans against it, with zone-parameterized thresholds loaded from environment variables
  4. Drift detection operates in detect-only mode (no auto-remediation for Zone 3) and all scan results are persisted in Dataverse for audit trail
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md — Runbook wrapper (Start-SessionValidationRunbook.ps1) and baseline capture (Invoke-BaselineCapture.ps1)
- [ ] 03-02-PLAN.md — Adaptive card template, Power Automate flow JSON, and flow setup guide

### Phase 4: Evidence Export and Framework Integration
**Goal**: Session security compliance evidence is exportable for regulatory examinations and the solution is integrated into the FSI-AgentGov framework documentation
**Depends on**: Phase 3
**Requirements**: CEV-01, CEV-02, CEV-03
**Success Criteria** (what must be TRUE):
  1. Operator can export session security compliance evidence with SHA-256 integrity hashing that produces a verifiable manifest file for FINRA/SEC examination support
  2. Control 1.23 documentation includes a tip admonition linking to the Session Security Configurator solution, and solutions-index.md contains the catalog entry
  3. A complete documentation suite exists covering prerequisites, Dataverse schema, configuration, deployment, and troubleshooting
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|---------------|--------|-----------|
| 1. PowerShell Core | 3/3 | Complete | 2026-02-07 |
| 2. Dataverse Infrastructure | 0/3 | Not started | - |
| 3. Automation and Alerting | 0/2 | Not started | - |
| 4. Evidence Export and Framework Integration | 0/TBD | Not started | - |

## Coverage

| Requirement | Phase | Description |
|-------------|-------|-------------|
| SCM-01 | Phase 1 | Deploy authentication contexts (c1-c5) with conflict detection |
| SCM-02 | Phase 1 | Deploy step-up CA policies with zone-specific session controls |
| SCM-03 | Phase 1 | Validate deployed CA policies match zone requirements |
| SCM-04 | Phase 1 | Dry-run mode for all deployment operations |
| SCM-05 | Phase 1 | Create/validate authentication strength policies |
| SCM-06 | Phase 1 | Validate PIM settings for AI admin roles |
| SCM-07 | Phase 1 | Report-only mode with 72-hour bake period |
| INF-01 | Phase 2 | Dataverse tables reusing ACV option sets |
| INF-02 | Phase 2 | Environment variables for zone thresholds |
| INF-03 | Phase 2 | Connection references for Dataverse, Office 365, Teams |
| INF-05 | Phase 2 | Python deployment scripts (idempotent, dry-run) |
| DDA-01 | Phase 3 | Detect session control drift |
| DDA-02 | Phase 3 | Teams adaptive card alerts with severity |
| DDA-03 | Phase 3 | Dataverse immutable validation history |
| DDA-04 | Phase 3 | Baseline capture and comparison |
| INF-04 | Phase 3 | Power Automate scheduled daily drift scan flow |
| CEV-01 | Phase 4 | SHA-256 integrity-hashed evidence export |
| CEV-02 | Phase 4 | Control 1.23 framework integration |
| CEV-03 | Phase 4 | Documentation suite |

**Total: 19/19 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-06*
*Phase 1 planned: 2026-02-06 (3 plans in 2 waves)*
*Phase 1 complete: 2026-02-07 (3 plans executed, verified 5/5)*
*Phase 2 planned: 2026-02-07 (3 plans in 3 waves)*
*Phase 3 planned: 2026-02-07 (2 plans in 2 waves)*
*Depth: comprehensive*
*Phases: 4 (derived from requirement dependencies and ACV proven pattern)*
