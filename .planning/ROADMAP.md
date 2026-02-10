# Roadmap: Deny Event Correlation Report (v10)

## Overview

Complete the Deny Event Correlation Report (DEC) solution from WIP v1.1.0 to production-ready v2.0.0. The existing solution has 4 PowerShell extraction scripts, 4 KQL queries, and 3 docs — but outputs to CSV/blob storage with deprecated x-api-key authentication. v2.0.0 adds Entra ID auth, Dataverse persistence, Power Automate orchestration, Teams alerting, zone-based analysis, SHA-256 evidence export, and Compliance Dashboard integration.

**Key insight:** DEC is unique among Tier 2 solutions because it correlates events from three distinct Microsoft data sources (Purview Audit, Purview DLP, Application Insights) rather than validating a single configuration setting. The architecture must normalize heterogeneous event schemas into a common `fsi_denyevent` table before correlation logic can execute. The x-api-key → Entra ID migration (AUTH-01) has a hard deadline of March 31, 2026, making Phase 1 time-critical.

**Existing artifacts (FSI-AgentGov-Solutions):**
- `scripts/Export-CopilotDenyEvents.ps1` — Purview CopilotInteraction extraction
- `scripts/Export-DlpCopilotEvents.ps1` — Purview DLP extraction
- `scripts/Export-RaiTelemetry.ps1` — App Insights extraction (uses deprecated x-api-key)
- `scripts/Invoke-DailyDenyReport.ps1` — Orchestration script
- `kql-queries/` — 4 KQL query files
- `docs/` — architecture.md, prerequisites.md, troubleshooting.md

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4, 5): Planned milestone work

- [x] **Phase 1: Authentication & Script Modernization** — Entra ID migration, DECClient.psm1 module, #Requires statements, Key Vault credential handling ✅ COMPLETE (2026-02-10)
- [ ] **Phase 2: Dataverse Infrastructure** — Schema design, deny event ingestion, correlation logic, zone-based retention
- [ ] **Phase 3: Orchestration & Alerting** — Power Automate daily orchestrator, Teams adaptive cards, severity classification
- [ ] **Phase 4: Evidence Export & Dashboard Integration** — SHA-256 evidence export, IntegrationConfig extension, CD feed sync
- [ ] **Phase 5: Documentation & Framework Integration** — Control tip admonitions, solutions-index update, DEC docs suite, playbook refresh

## Phase Details

### Phase 1: Authentication & Script Modernization
**Goal**: Migrate all extraction scripts from deprecated authentication to Entra ID, create a shared client module, and modernize scripts to match v4-v8 security standards
**Depends on**: Nothing (first phase — TIME-CRITICAL: x-api-key deprecated March 31, 2026)
**Requirements**: AUTH-01, AUTH-02, AUTH-03
**Success Criteria** (what must be TRUE):
  1. `Export-RaiTelemetry.ps1` authenticates via `Connect-AzAccount` + `Get-AzAccessToken` instead of x-api-key
  2. `DECClient.psm1` provides shared authentication helpers, connection management, and reusable extraction functions for all three data sources
  3. All 4 extraction scripts have `#Requires` statements and use Azure Key Vault for credential retrieval (no hardcoded secrets or interactive prompts)
  4. All existing KQL queries validated and updated if needed for Entra ID token-based API access
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Entra ID authentication migration for Export-RaiTelemetry.ps1 (AUTH-01)
- [x] 01-02-PLAN.md — DECClient.psm1 shared module with auth helpers and extraction functions (AUTH-02)
- [x] 01-03-PLAN.md — Script hardening: #Requires, Key Vault, error handling across all scripts (AUTH-03)

### Phase 2: Dataverse Infrastructure
**Goal**: Design and implement Dataverse tables for deny event persistence, correlation engine, and zone-based retention — transforming DEC from stateless CSV export to persistent Dataverse-backed solution
**Depends on**: Phase 1
**Requirements**: DVS-01, DVS-02, DVS-03, DVS-04
**Success Criteria** (what must be TRUE):
  1. Dataverse schema documented with `fsi_denyevent`, `fsi_denycorrelation`, `fsi_denyalert` tables reusing `fsi_acv_zone` and `fsi_acv_severity` option sets
  2. Extraction scripts write normalized deny events to `fsi_denyevent` with source type, agent ID, deny reason, zone, severity, and timestamp
  3. Correlation logic produces daily `fsi_denycorrelation` summaries grouping events by agent, zone, and time window with counts, severity distribution, and 7-day trend indicators
  4. Retention rules configured: Zone 1 = 90 days, Zone 2 = 365 days, Zone 3 = 730 days (SEC 17a-4)
**Plans**: 3 plans

Plans:
- [ ] 02-01-PLAN.md — Dataverse schema design and table definitions (DVS-01)
- [ ] 02-02-PLAN.md — Deny event ingestion: script updates to write to fsi_denyevent (DVS-02)
- [ ] 02-03-PLAN.md — Correlation engine and zone-based retention rules (DVS-03, DVS-04)

### Phase 3: Orchestration & Alerting
**Goal**: Automate daily deny event extraction and correlation with Power Automate orchestration and Teams alerting for high-severity patterns
**Depends on**: Phases 1, 2
**Requirements**: ORC-01, ORC-02, ORC-03
**Success Criteria** (what must be TRUE):
  1. `DEC-DailyOrchestrator` Power Automate flow triggers daily, runs all three extraction scripts via Azure Automation, writes to Dataverse, and generates correlation summaries
  2. Teams adaptive card alerts fire for volume anomalies (>2σ from 7-day baseline), new agent deny events, and Zone 3 critical blocks
  3. Alert severity classification follows cross-solution standard: Critical (Zone 3 jailbreak/XPIA), High (Zone 2 policy block/volume anomaly), Warning (Zone 1 RAI), Info (routine DLP)
**Plans**: 3 plans

Plans:
- [ ] 03-01-PLAN.md — DEC-DailyOrchestrator Power Automate flow definition (ORC-01)
- [ ] 03-02-PLAN.md — Teams adaptive card alerting with anomaly detection (ORC-02)
- [ ] 03-03-PLAN.md — Alert severity classification and threshold configuration (ORC-03)

### Phase 4: Evidence Export & Dashboard Integration
**Goal**: Deliver SHA-256 evidence export for regulatory examinations and wire DEC into the Compliance Dashboard via v9 integration infrastructure
**Depends on**: Phases 2, 3
**Requirements**: EVI-01, EVI-02, EVI-03, EVI-04, EVI-05
**Success Criteria** (what must be TRUE):
  1. `Export-DenyEventEvidence.ps1` produces timestamped examination packages with deny events, correlation summaries, and trend analysis, all SHA-256 hashed
  2. Evidence packages include regulatory alignment mapping (deny events → FINRA/SEC requirements)
  3. DEC evidence registered with v9 `Export-UnifiedComplianceEvidence.ps1` via IntegrationConfig extension
  4. `IntegrationConfig.psm1` extended with DEC mapping: DEC → Controls 1.5, 1.7, 3.4
  5. `Sync-SolutionAssessments.ps1` extended to query `fsi_denycorrelation` and translate to CD assessment records
**Plans**: 3 plans

Plans:
- [ ] 04-01-PLAN.md — Export-DenyEventEvidence.ps1 with SHA-256 hashing and regulatory alignment (EVI-01, EVI-02)
- [ ] 04-02-PLAN.md — Unified evidence integration and IntegrationConfig extension (EVI-03, EVI-04)
- [ ] 04-03-PLAN.md — Sync-SolutionAssessments.ps1 extension for DEC dashboard feed (EVI-05)

### Phase 5: Documentation & Framework Integration
**Goal**: Update framework controls, solutions-index, DEC playbook, and complete solution documentation suite — validating with mkdocs build --strict
**Depends on**: Phases 1-4
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04
**Success Criteria** (what must be TRUE):
  1. Controls 1.5, 1.7, 1.8, and 3.4 have tip admonitions referencing DEC v2.0.0 with deployment links
  2. `solutions-index.md` updated: status = "Completed", version = v2.0.0, component list and regulatory alignment refreshed
  3. DEC solution documentation suite complete in FSI-AgentGov-Solutions (README, PREREQUISITES, SCHEMA, EVIDENCE_EXPORT, FLOW_SETUP, TROUBLESHOOTING, CHANGELOG)
  4. Framework playbook `deny-event-correlation-report/index.md` updated for v2.0.0 architecture
  5. `mkdocs build --strict` passes with all changes
**Plans**: 3 plans

Plans:
- [ ] 05-01-PLAN.md — Control tip admonitions and solutions-index.md update (DOC-01, DOC-02)
- [ ] 05-02-PLAN.md — DEC solution documentation suite in FSI-AgentGov-Solutions (DOC-03)
- [ ] 05-03-PLAN.md — Framework playbook v2.0.0 refresh and build validation (DOC-04)

## Progress

**Execution Order:**
Phase 1 (critical path) → Phase 2 → Phase 3 → Phase 4 → Phase 5

| Phase | Plans Complete | Status | Completed |
|-------|---------------|--------|-----------|
| 1. Auth & Script Modernization | 3/3 | COMPLETE | 2026-02-10 |
| 2. Dataverse Infrastructure | 0/3 | PENDING | — |
| 3. Orchestration & Alerting | 0/3 | PENDING | — |
| 4. Evidence & Dashboard | 0/3 | PENDING | — |
| 5. Documentation & Framework | 0/3 | PENDING | — |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| AUTH-01 | Phase 1 | 01-01 | Entra ID migration for Export-RaiTelemetry.ps1 |
| AUTH-02 | Phase 1 | 01-02 | DECClient.psm1 shared module |
| AUTH-03 | Phase 1 | 01-03 | Script hardening (#Requires, Key Vault) |
| DVS-01 | Phase 2 | 02-01 | Dataverse schema design |
| DVS-02 | Phase 2 | 02-02 | Deny event ingestion to Dataverse |
| DVS-03 | Phase 2 | 02-03 | Correlation engine |
| DVS-04 | Phase 2 | 02-03 | Zone-based retention rules |
| ORC-01 | Phase 3 | 03-01 | DEC-DailyOrchestrator flow |
| ORC-02 | Phase 3 | 03-02 | Teams adaptive card alerting |
| ORC-03 | Phase 3 | 03-03 | Alert severity classification |
| EVI-01 | Phase 4 | 04-01 | Export-DenyEventEvidence.ps1 |
| EVI-02 | Phase 4 | 04-01 | Regulatory alignment mapping |
| EVI-03 | Phase 4 | 04-02 | Unified evidence integration |
| EVI-04 | Phase 4 | 04-02 | IntegrationConfig.psm1 DEC extension |
| EVI-05 | Phase 4 | 04-03 | Sync-SolutionAssessments.ps1 DEC feed |
| DOC-01 | Phase 5 | 05-01 | Control tip admonitions |
| DOC-02 | Phase 5 | 05-01 | solutions-index.md update |
| DOC-03 | Phase 5 | 05-02 | DEC solution docs suite |
| DOC-04 | Phase 5 | 05-03 | Framework playbook v2.0.0 refresh |

**Total: 19/19 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-10*
*Depth: comprehensive*
*Phases: 5 (auth → dataverse → orchestration → evidence/dashboard → docs)*

