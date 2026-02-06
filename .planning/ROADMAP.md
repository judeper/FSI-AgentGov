# Roadmap: FSI-AgentGov v4 — Audit Configuration Validator

## Overview

This milestone delivers an automated audit configuration validation solution for Microsoft 365 and Power Platform environments. The solution validates that audit logging is properly enabled and configured across tenant-level unified audit, per-environment Power Platform audit, and Purview retention policies. The validator provides continuous monitoring, configuration drift detection, and compliance evidence export to support SEC 17a-4(f) automatic verification requirements.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (1.1, 1.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Core Validation Scripts** - PowerShell validation logic with dual validation strategy ✓
- [x] **Phase 2: Infrastructure & Environment Validation** - Solution structure, Dataverse schema, environment-level validation ✓
- [ ] **Phase 3: Automated Orchestration & Alerting** - Power Automate flows with Teams/email notifications
- [ ] **Phase 4: Evidence Export & Framework Integration** - Compliance evidence generation and documentation

## Phase Details

### Phase 1: Core Validation Scripts

**Goal**: PowerShell scripts validate tenant-level audit configuration with robust error handling and dual validation strategy to prevent false positives.

**Depends on**: Nothing (first phase)

**Requirements**: TVAL-01, TVAL-02, TVAL-03, TVAL-04, PVAL-01, PVAL-02, PVAL-03, INFR-05

**Success Criteria** (what must be TRUE):
1. Validator checks M365 Unified Audit Log enablement status using dual validation (cmdlet + canary event)
2. Validator checks mailbox audit on-by-default status separately from unified audit
3. Validator checks Purview audit retention policies and validates they meet FSI regulatory minimums (730 days for Zone 3)
4. Scripts include comprehensive error handling with try-catch blocks and module version validation (#Requires statements)
5. False positives are prevented through 24-hour audit lag grace period and result set validation

**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Auth helpers and Unified Audit Log validation with dual strategy (TVAL-01, TVAL-03, TVAL-04, INFR-05) ✓
- [x] 01-02-PLAN.md — Mailbox audit and Purview retention validation (TVAL-02, PVAL-01, PVAL-02, PVAL-03) ✓
- [x] 01-03-PLAN.md — Main orchestrator and end-to-end verification ✓

### Phase 2: Infrastructure & Environment Validation

**Goal**: Solution infrastructure established with Dataverse schema for status tracking, and per-environment audit validation using Dataverse Web API.

**Depends on**: Phase 1

**Requirements**: INFR-01, INFR-02, INFR-03, INFR-04, EVAL-01, EVAL-02, EVAL-03, EVAL-04, EVAL-05, EVID-03

**Success Criteria** (what must be TRUE):
1. Solution follows established Tier 2 pattern with README, CHANGELOG, docs/, scripts/, src/ structure
2. Dataverse tables use fsi_ publisher prefix with immutable validation history table (organization-owned, no update/delete)
3. Connection references use fsi_cr_* naming and environment variables use fsi_ACV_* convention
4. Validator checks per-environment audit enablement and retention periods via Dataverse Web API
5. Zone-specific retention rules are enforced (Zone 1: 180d, Zone 2: 365d, Zone 3: 730d)
6. Trial and Developer environments are filtered out from validation and alerting
7. Recently-enabled environments get 24-hour grace period before alerts fire

**Plans**: 3 plans in 3 waves

Plans:
- [x] 02-01-PLAN.md — Solution structure, Dataverse API client, schema scripts, env vars, connection refs, and deploy orchestrator (INFR-01, INFR-02, INFR-03, INFR-04, EVID-03) ✓
- [x] 02-02-PLAN.md — Power Platform auth helper, Dataverse write helper, and environment discovery with registry sync (EVAL-04) ✓
- [x] 02-03-PLAN.md — Per-environment audit and retention validators with environment-level orchestrator (EVAL-01, EVAL-02, EVAL-03, EVAL-05) ✓

### Phase 3: Automated Orchestration & Alerting

**Goal**: Scheduled validation runs with automatic drift detection and multi-channel alerting when configuration issues are detected.

**Depends on**: Phase 2

**Requirements**: AUTO-01, AUTO-02, AUTO-03, AUTO-04

**Success Criteria** (what must be TRUE):
1. Daily validation runs automatically via Power Automate scheduled flow
2. Configuration drift is detected by comparing current state against last known good baseline
3. Teams adaptive cards are posted when Critical or High severity validation failures occur
4. Email alerts are sent to compliance team distribution list for all validation failures

**Plans**: 2 plans in 2 waves

Plans:
- [ ] 03-01-PLAN.md — Azure Automation runbook wrappers and drift detection helper (AUTO-01, AUTO-02)
- [ ] 03-02-PLAN.md — Power Automate flow definitions, adaptive card templates, and deployment guide (AUTO-01, AUTO-02, AUTO-03, AUTO-04)

### Phase 4: Evidence Export & Framework Integration

**Goal**: Compliance evidence export with integrity hashing and Control 1.7 documentation updates for complete framework integration.

**Depends on**: Phase 3

**Requirements**: EVID-01, EVID-02, EVID-04, DOCS-01, DOCS-02, DOCS-03, DOCS-04

**Success Criteria** (what must be TRUE):
1. Evidence exports to JSON format with full validation results including timestamp, validation type, overall status, and per-environment details
2. SHA-256 integrity hashes are generated for all exported evidence files
3. Control 1.7 (Comprehensive Audit Logging) includes new "Automated Validation" section referencing the solution
4. Solution is added to solutions-index.md with controls covered mapping
5. Solution README provides prerequisites, quick start guide, and zone-specific requirements
6. Deployment guide provides step-by-step setup instructions for administrators

**Plans**: TBD

Plans:
- [ ] 04-01: TBD during planning
- [ ] 04-02: TBD during planning

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Validation Scripts | 3/3 | Complete | 2026-02-06 |
| 2. Infrastructure & Environment Validation | 3/3 | Complete | 2026-02-06 |
| 3. Automated Orchestration & Alerting | 0/2 | Not started | - |
| 4. Evidence Export & Framework Integration | 0/TBD | Not started | - |

---
*Last updated: 2026-02-06 — Phase 3 planned (2 plans in 2 waves)*
