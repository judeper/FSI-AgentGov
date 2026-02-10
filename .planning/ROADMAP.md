# Roadmap: File Upload Security Configurator (v8)

## Overview

Automated validation of Copilot Studio agent file upload settings per governance zone, for Control 1.14 (Data Minimization and Agent Scope Control). File uploads expand agent data intake beyond declared operational scope — FSI organizations must validate that agents accepting file uploads comply with zone-specific security posture requirements. Follows the proven ACV/SSC/AAM/CMM Tier 2 solution pattern with 4–phase build progression: PowerShell core → Dataverse infrastructure → automation and alerting → evidence export and framework integration.

**Key insight:** Unlike content moderation (multi-level setting), file upload is primarily a binary setting (enabled/disabled) per agent. The solution validates that agents in restrictive zones do not have file uploads enabled, and that agents with file uploads enabled meet minimum content moderation levels. This makes the validation logic simpler but still requires per-agent enumeration.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work

- [x] **Phase 1: PowerShell Core** — Per-agent file upload enumeration, zone compliance comparison, and orchestrator with dry-run mode
- [x] **Phase 2: Dataverse Infrastructure** — Persistent state tables, environment variables, deployment scripts, and baseline capture
- [x] **Phase 3: Automation and Alerting** — Daily validation flow, Teams adaptive card alerts, Azure Automation runbook
- [x] **Phase 4: Evidence Export and Framework Integration** — SHA-256 evidence export, Control 1.14 tip admonition, solutions-index.md entry, docs suite

## Phase Details

### Phase 1: PowerShell Core
**Goal**: Operator can run a single command to enumerate all Copilot Studio agents, check file upload status per zone policy, and get a compliance report with severity classifications — all from a standalone PowerShell session
**Depends on**: Nothing (first phase)
**Requirements**: FUS-01, FUS-02, FUS-03, FUS-04, FUS-05, INF-01
**Success Criteria** (what must be TRUE):
  1. `Get-AgentFileUploadSettings` enumerates agents across environments and returns FileUploadEnabled status per agent
  2. `Compare-FileUploadCompliance` evaluates each agent's settings against zone baselines with severity classification (Critical/High/Medium/Warning)
  3. `Test-FileUploadCompliance` orchestrates end-to-end validation with dry-run mode and multiple output formats
  4. Content moderation cross-check flags agents with file uploads enabled but insufficient moderation level
  5. FUSClient.psm1 module provides Dataverse bot table queries for file upload metadata
  6. Solution scaffold follows Tier 2 pattern with proven helpers (Get-ZoneClassification, Connect-EnvironmentDataverse, Test-ParameterValidation)
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Solution scaffold, FUSClient module, and zone lookup logic (FUS-01, FUS-02, INF-01)
- [x] 01-02-PLAN.md — Compliance comparison and content moderation cross-check (FUS-03, FUS-05)
- [x] 01-03-PLAN.md — Orchestrator with dry-run mode and multi-format output (FUS-04)

### Phase 2: Dataverse Infrastructure
**Goal**: Operator can deploy Dataverse tables, capture baselines, and have persistent validation history for audit trail
**Depends on**: Phase 1
**Requirements**: DDA-01, DDA-02, DDA-03, INF-02
**Success Criteria** (what must be TRUE):
  1. Dataverse tables created: fsi_fileupload_baseline, fsi_fileupload_validation, fsi_fileupload_violation
  2. Environment variables with fsi_FUS_ prefix and connection references deployed
  3. Baseline capture records current file upload settings per agent as compliance reference
  4. Schema reuses existing ACV option sets (fsi_acv_zone, fsi_acv_severity) for cross-solution consistency
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — Dataverse schema, environment variables, connection references (DDA-01, DDA-02, INF-02)
- [x] 02-02-PLAN.md — FUSClient.psm1 Dataverse CRUD operations for baselines and validations (DDA-01)
- [x] 02-03-PLAN.md — Baseline capture and Python deployment orchestrator (DDA-03)

### Phase 3: Automation and Alerting
**Goal**: Daily automated file upload compliance validation with Teams alerting and Azure Automation support
**Depends on**: Phase 2
**Requirements**: DDA-04, DDA-05, DDA-06
**Success Criteria** (what must be TRUE):
  1. Power Automate flow runs daily, triggers file upload compliance validation, stores results in Dataverse
  2. Teams adaptive card alerts include file upload status, zone context, severity, and remediation guidance
  3. Azure Automation runbook wrapper supports scheduled unattended execution
**Plans**: 3 plans

Plans:
- [x] 03-01-PLAN.md — Power Automate daily validation flow definition (DDA-04)
- [x] 03-02-PLAN.md — Teams adaptive card template and alerting logic (DDA-05)
- [x] 03-03-PLAN.md — Azure Automation runbook wrapper (DDA-06)

### Phase 4: Evidence Export and Framework Integration
**Goal**: Compliance evidence export with SHA-256 integrity hashing and framework integration (control tip, solutions-index, docs)
**Depends on**: Phase 3
**Requirements**: CEV-01, CEV-02, CEV-03, INF-03
**Success Criteria** (what must be TRUE):
  1. Evidence export generates JSON with SHA-256 hash companion files for SEC 17a-4(f) support
  2. Control 1.14 contains tip admonition linking to File Upload Security Configurator solution
  3. solutions-index.md has catalog entry for File Upload Security Configurator
  4. Complete docs suite: README, PREREQUISITES, SCHEMA, EVIDENCE_EXPORT, FLOW_SETUP, TROUBLESHOOTING, CHANGELOG
**Plans**: 3 plans

Plans:
- [x] 04-FUS-01-PLAN.md — Evidence export and integrity verification scripts (CEV-01, INF-03)
- [x] 04-FUS-02-PLAN.md — Control 1.14 tip admonition and solutions-index.md entry (CEV-02)
- [x] 04-FUS-03-PLAN.md — Documentation suite and CHANGELOG (CEV-03)

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

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| FUS-01 | Phase 1 | 01-01 | Agent enumeration and file upload status retrieval |
| FUS-02 | Phase 1 | 01-01 | Zone classification for file upload policy |
| FUS-03 | Phase 1 | 01-02 | Compliance comparison with severity classification |
| FUS-04 | Phase 1 | 01-03 | Orchestrator with dry-run and multi-format output |
| FUS-05 | Phase 1 | 01-02 | Content moderation cross-check for file upload agents |
| INF-01 | Phase 1 | 01-01 | Tier 2 scaffold with shared helpers |
| DDA-01 | Phase 2 | 02-01 | Dataverse tables for persistent state |
| DDA-02 | Phase 2 | 02-01 | Python deployment scripts |
| DDA-03 | Phase 2 | 02-03 | Baseline capture script |
| INF-02 | Phase 2 | 02-01 | ACV option set reuse |
| DDA-04 | Phase 3 | 03-01 | Power Automate daily validation flow |
| DDA-05 | Phase 3 | 03-02 | Teams adaptive card alerts |
| DDA-06 | Phase 3 | 03-03 | Azure Automation runbook wrapper |
| CEV-01 | Phase 4 | 04-FUS-01 | SHA-256 evidence export |
| CEV-02 | Phase 4 | 04-FUS-02 | Control 1.14 and solutions-index integration |
| CEV-03 | Phase 4 | 04-FUS-03 | Documentation suite |
| INF-03 | Phase 4 | 04-FUS-01 | Evidence integrity verification |

**Total: 17/17 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-10*
*Depth: comprehensive*
*Phases: 4 (PowerShell core → Dataverse → automation → evidence/integration)*

