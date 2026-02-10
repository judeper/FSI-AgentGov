# Roadmap: Content Moderation Governance Monitor (v7)

## Overview

The Content Moderation Governance Monitor automates validation and drift detection of Copilot Studio agent content moderation levels per governance zone for Control 1.8. The build follows the proven ACV/SSC/AAM Tier 2 pattern: standalone PowerShell scripts first (agent enumeration, moderation level query, zone compliance validation), then Dataverse infrastructure for persistent state, then Power Automate automation with drift detection and alerting, and finally evidence export with framework integration. Each phase delivers a verifiable capability that the next phase builds on.

**Key difference from prior milestones:** Content moderation is configured **per-agent** (not per-environment), requiring Copilot Studio bot metadata queries. The solution enumerates agents within each environment and validates their individual content moderation settings against the zone classification of their hosting environment.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (e.g., 2.1): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: PowerShell Core** - Agent enumeration, content moderation level query, zone compliance validation, and severity classification
- [x] **Phase 2: Dataverse Infrastructure** - Persistent state tables, environment variables, connection references, and deployment scripts
- [x] **Phase 3: Automation and Alerting** - Scheduled drift detection, Teams alerting, Power Automate flow, and baseline management
- [x] **Phase 4: Evidence Export and Framework Integration** - SHA-256 compliance export, Control 1.8 integration, and documentation suite

## Phase Details

### Phase 1: PowerShell Core
**Goal**: Operators can enumerate Copilot Studio agents, query content moderation levels, and validate compliance with zone-specific requirements using standalone PowerShell scripts
**Depends on**: Nothing (first phase)
**Requirements**: CMV-01, CMV-02, CMV-03, CMV-04, CMV-05, CMV-06
**Success Criteria** (what must be TRUE):
  1. Operator can enumerate all Copilot Studio agents across Power Platform environments and retrieve generative AI configuration including content moderation level (Low/Medium/High) with a single script invocation
  2. Operator can validate content moderation levels against zone requirements (Zone 1: Medium minimum, Zone 2: High, Zone 3: High) with zone lookup via ELM Dataverse or naming convention fallback
  3. Operator can run dry-run mode to preview all violations without persisting or alerting, showing agent name, environment, zone, current moderation level, expected level, and severity
  4. Operator can see violations classified by severity (Zone 3 agent with Low = CRITICAL, Zone 3 with Medium = HIGH, Zone 2 with Low = HIGH, Zone 2 with Medium = MEDIUM, Zone 1 with Low = HIGH) with regulatory impact context (FINRA 3110, GLBA 501(b))
  5. Operator can filter by agent status (published only vs. include drafts) and exclude sandbox/trial environments from validation
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Solution scaffold, private helpers, and zone lookup logic
- [x] 01-02-PLAN.md — Get-AgentModerationSettings.ps1 and Compare-ModerationCompliance.ps1
- [x] 01-03-PLAN.md — Test-ContentModerationCompliance.ps1 validation orchestrator

### Phase 2: Dataverse Infrastructure
**Goal**: Moderation baselines, validation history, and configuration thresholds are stored in Dataverse for persistent, queryable state across automated runs
**Depends on**: Phase 1
**Requirements**: INF-01, INF-02, INF-03, INF-05
**Success Criteria** (what must be TRUE):
  1. Dataverse schema is deployed with moderation baseline, validation history (immutable), and violation tables that reuse existing ACV option sets (fsi_acv_zone, fsi_acv_severity)
  2. Environment variables for zone-specific moderation thresholds (fsi_CMM_* prefix) are deployed and Phase 1 scripts read thresholds from them instead of hardcoded values
  3. Connection references for Dataverse, Office 365, and Teams are deployed with fsi_cr_* naming convention
  4. Python deployment scripts are idempotent (safe to re-run) and support dry-run mode, following the ACV/SSC/AAM pattern
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — CMM Dataverse client, requirements, and three-table schema deployment
- [x] 02-02-PLAN.md — Environment variables, connection references, and deploy.py orchestrator
- [x] 02-03-PLAN.md — Wire Phase 1 PowerShell scripts to read thresholds from Dataverse

### Phase 3: Automation and Alerting
**Goal**: Content moderation violations are automatically detected daily and operators receive classified alerts when agent moderation settings deviate from zone requirements
**Depends on**: Phase 2
**Requirements**: DDA-01, DDA-02, DDA-03, DDA-04, INF-04
**Success Criteria** (what must be TRUE):
  1. A scheduled Power Automate flow runs daily moderation validation that compares live agent content moderation levels against zone requirements and writes results to immutable validation history
  2. When violations are detected (moderation level weakened, new agent with non-compliant setting), a Teams adaptive card alert is sent with severity classification matching the zone and violation type
  3. Operators can capture a baseline snapshot of all agent moderation levels and compare subsequent scans against it, with violations detected when levels change
  4. All scan results and violations are persisted in Dataverse with immutable validation history for audit trail
**Plans**: 3 plans

Plans:
- [x] 03-01-PLAN.md — Runbook wrapper, baseline capture, and CMMClient drift detection functions (Wave 1)
- [x] 03-02-PLAN.md — Adaptive card template, Power Automate flow JSON, and flow setup guide (Wave 2)
- [x] 03-03-PLAN.md — Drift detection refinement, integration verification, and CHANGELOG update (Wave 3)

### Phase 4: Evidence Export and Framework Integration
**Goal**: Content moderation compliance evidence is exportable for regulatory examinations and the solution is integrated into the FSI-AgentGov framework documentation
**Depends on**: Phase 3
**Requirements**: CEV-01, CEV-02, CEV-03
**Success Criteria** (what must be TRUE):
  1. Operator can export content moderation compliance evidence with SHA-256 integrity hashing that produces a verifiable manifest file for FINRA/SEC examination support
  2. Control 1.8 documentation includes a tip admonition linking to the Content Moderation Governance Monitor solution, and solutions-index.md contains the catalog entry
  3. A complete documentation suite exists covering prerequisites, Dataverse schema, configuration, deployment, and troubleshooting
**Plans**: 3 plans

Plans:
- [x] 04-CMM-01-PLAN.md — Evidence export scripts (Export-ContentModerationEvidence, Get-CMMValidationResults, Test-EvidenceIntegrity)
- [x] 04-CMM-02-PLAN.md — Control 1.8 tip admonition and solutions-index.md catalog entry
- [x] 04-CMM-03-PLAN.md — Documentation suite (prerequisites, schema, evidence export, troubleshooting)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|---------------|--------|-----------|
| 1. PowerShell Core | 3/3 | Complete | 2026-02-10 |
| 2. Dataverse Infrastructure | 3/3 | Complete | 2026-02-10 |
| 3. Automation and Alerting | 3/3 | Complete | 2026-02-10 |
| 4. Evidence Export and Framework Integration | 3/3 | Complete | 2026-02-10 |

## Coverage

| Requirement | Phase | Description |
|-------------|-------|-------------|
| CMV-01 | Phase 1 | Enumerate agents and retrieve content moderation levels |
| CMV-02 | Phase 1 | Validate moderation levels against zone requirements |
| CMV-03 | Phase 1 | Classify violations by severity with regulatory context |
| CMV-04 | Phase 1 | Dry-run mode for all validation operations |
| CMV-05 | Phase 1 | Agent status filtering and sandbox/trial exclusion |
| CMV-06 | Phase 1 | Zone lookup via ELM Dataverse or naming convention |
| INF-01 | Phase 2 | Dataverse tables reusing ACV option sets |
| INF-02 | Phase 2 | Environment variables for moderation thresholds |
| INF-03 | Phase 2 | Connection references for Dataverse, Office 365, Teams |
| INF-05 | Phase 2 | Python deployment scripts (idempotent, dry-run) |
| DDA-01 | Phase 3 | Detect content moderation setting drift |
| DDA-02 | Phase 3 | Teams adaptive card alerts with severity |
| DDA-03 | Phase 3 | Dataverse immutable validation history |
| DDA-04 | Phase 3 | Baseline capture and comparison |
| INF-04 | Phase 3 | Power Automate scheduled daily scan flow |
| CEV-01 | Phase 4 | SHA-256 integrity-hashed evidence export |
| CEV-02 | Phase 4 | Control 1.8 framework integration |
| CEV-03 | Phase 4 | Documentation suite |

**Total: 18/18 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-09*
*Depth: comprehensive*
*Phases: 4 (derived from ACV/SSC/AAM proven pattern)*

