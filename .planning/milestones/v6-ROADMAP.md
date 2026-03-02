# Roadmap: Agent Access Governance Monitor (v6)

## Overview

The Agent Access Governance Monitor automates detection of unrestricted agent access configurations across Power Platform environments for Control 3.8. The build follows the proven ACV/SSC Tier 2 pattern: standalone PowerShell scripts first (environment query, zone validation, severity classification), then Dataverse infrastructure for persistent state, then Power Automate automation with drift detection and alerting, and finally evidence export with framework integration. Each phase delivers a verifiable capability that the next phase builds on.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (e.g., 2.1): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: PowerShell Core** - Environment access settings query, zone compliance validation, and severity classification
- [x] **Phase 2: Dataverse Infrastructure** - Persistent state tables, environment variables, connection references, and deployment scripts
- [x] **Phase 3: Automation and Alerting** - Scheduled drift detection, Teams alerting, Power Automate flow, and baseline management
- [x] **Phase 4: Evidence Export and Framework Integration** - SHA-256 compliance export, Control 3.8 integration, and documentation suite

## Phase Details

### Phase 1: PowerShell Core
**Goal**: Operators can query, validate, and preview agent access configuration violations per governance zone using standalone PowerShell scripts
**Depends on**: Nothing (first phase)
**Requirements**: ACV-01, ACV-02, ACV-03, ACV-04, ACV-05, ACV-06
**Success Criteria** (what must be TRUE):
  1. Operator can query all Power Platform environments and retrieve agent access settings (`bot-limitSharingMode`, `bot-authoringSharingDisabled`, `bot-publishedBotLimitSharingMode`) with a single script invocation
  2. Operator can validate agent access settings against zone requirements (Zone 1: all allowed, Zone 2: org+verified, Zone 3: org-only) with zone lookup via ELM Dataverse or naming convention fallback
  3. Operator can run dry-run mode to preview all violations without persisting or alerting, showing environment name, zone, setting, expected vs actual, and severity
  4. Operator can see violations classified by severity (Zone 3 CRITICAL, Zone 2 HIGH, Zone 1 INFO) with regulatory impact context (FINRA 4511, SOX 404)
  5. Operator can exclude sandbox/trial environments and newly provisioned environments (48-hour grace period) from violation reporting
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Solution scaffold, private helpers, and zone lookup logic
- [x] 01-02-PLAN.md — Get-EnvironmentAccessSettings.ps1 and Compare-ZoneCompliance.ps1
- [x] 01-03-PLAN.md — Test-AgentAccessCompliance.ps1 validation orchestrator

### Phase 2: Dataverse Infrastructure
**Goal**: Access baselines, validation history, and configuration thresholds are stored in Dataverse for persistent, queryable state across automated runs
**Depends on**: Phase 1
**Requirements**: INF-01, INF-02, INF-03, INF-05
**Success Criteria** (what must be TRUE):
  1. Dataverse schema is deployed with access baseline, validation history (immutable), and violation tables that reuse existing ACV option sets (fsi_acv_zone, fsi_acv_severity)
  2. Environment variables for zone-specific access thresholds (fsi_AAM_* prefix) are deployed and Phase 1 scripts read thresholds from them instead of hardcoded values
  3. Connection references for Dataverse, Office 365, and Teams are deployed with fsi_cr_* naming convention
  4. Python deployment scripts are idempotent (safe to re-run) and support dry-run mode, following the ACV/SSC pattern
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — AAM Dataverse client, requirements, and three-table schema deployment
- [x] 02-02-PLAN.md — Environment variables, connection references, and deploy.py orchestrator
- [x] 02-03-PLAN.md — Wire Phase 1 PowerShell scripts to read thresholds from Dataverse

### Phase 3: Automation and Alerting
**Goal**: Agent access violations are automatically detected daily and operators receive classified alerts when configuration deviates from zone requirements
**Depends on**: Phase 2
**Requirements**: DDA-01, DDA-02, DDA-03, DDA-04, INF-04
**Success Criteria** (what must be TRUE):
  1. A scheduled Power Automate flow runs daily access validation that compares live environment settings against zone requirements and writes results to immutable validation history
  2. When violations are detected (sharing mode weakened, authoring sharing enabled, settings downgraded), a Teams adaptive card alert is sent with severity classification matching the zone and violation type
  3. Operators can capture a baseline snapshot of all environment access settings and compare subsequent scans against it, with violations detected when settings change
  4. All scan results and violations are persisted in Dataverse with immutable validation history for audit trail
**Plans**: 3 plans

Plans:
- [x] 03-01-PLAN.md — Runbook wrapper, baseline capture, and AAMClient drift detection functions (Wave 1)
- [x] 03-02-PLAN.md — Adaptive card template, Power Automate flow JSON, and flow setup guide (Wave 2)
- [x] 03-03-PLAN.md — Drift detection refinement, integration verification, and CHANGELOG update (Wave 3)

### Phase 4: Evidence Export and Framework Integration
**Goal**: Agent access compliance evidence is exportable for regulatory examinations and the solution is integrated into the FSI-AgentGov framework documentation
**Depends on**: Phase 3
**Requirements**: CEV-01, CEV-02, CEV-03
**Success Criteria** (what must be TRUE):
  1. Operator can export agent access compliance evidence with SHA-256 integrity hashing that produces a verifiable manifest file for FINRA/SEC examination support
  2. Control 3.8 documentation includes a tip admonition linking to the Agent Access Governance Monitor solution, and solutions-index.md contains the catalog entry
  3. A complete documentation suite exists covering prerequisites, Dataverse schema, configuration, deployment, and troubleshooting
**Plans**: 3 plans

Plans:
- [x] 04-AAM-01-PLAN.md — Evidence export scripts (Export-AgentAccessEvidence, Get-AAMValidationResults, Test-EvidenceIntegrity)
- [x] 04-AAM-02-PLAN.md — Control 3.8 tip admonition and solutions-index.md catalog entry
- [x] 04-AAM-03-PLAN.md — Documentation suite (prerequisites, schema, evidence export, troubleshooting)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|---------------|--------|-----------|
| 1. PowerShell Core | 3/3 | Complete | 2026-02-09 |
| 2. Dataverse Infrastructure | 3/3 | Complete | 2026-02-09 |
| 3. Automation and Alerting | 3/3 | Complete | 2026-02-09 |
| 4. Evidence Export and Framework Integration | 3/3 | Complete | 2026-02-09 |

## Coverage

| Requirement | Phase | Description |
|-------------|-------|-------------|
| ACV-01 | Phase 1 | Query Power Platform environment agent access settings |
| ACV-02 | Phase 1 | Validate settings against zone-specific requirements |
| ACV-03 | Phase 1 | Classify violations by severity with regulatory context |
| ACV-04 | Phase 1 | Dry-run mode for all validation operations |
| ACV-05 | Phase 1 | Query environment groups for group-level rules |
| ACV-06 | Phase 1 | Exclude sandbox/trial, apply 48h grace period |
| INF-01 | Phase 2 | Dataverse tables reusing ACV option sets |
| INF-02 | Phase 2 | Environment variables for zone thresholds |
| INF-03 | Phase 2 | Connection references for Dataverse, Office 365, Teams |
| INF-05 | Phase 2 | Python deployment scripts (idempotent, dry-run) |
| DDA-01 | Phase 3 | Detect agent access setting drift |
| DDA-02 | Phase 3 | Teams adaptive card alerts with severity |
| DDA-03 | Phase 3 | Dataverse immutable validation history |
| DDA-04 | Phase 3 | Baseline capture and comparison |
| INF-04 | Phase 3 | Power Automate scheduled daily scan flow |
| CEV-01 | Phase 4 | SHA-256 integrity-hashed evidence export |
| CEV-02 | Phase 4 | Control 3.8 framework integration |
| CEV-03 | Phase 4 | Documentation suite |

**Total: 18/18 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-09*
*Depth: comprehensive*
*Phases: 4 (derived from ACV/SSC proven pattern)*

