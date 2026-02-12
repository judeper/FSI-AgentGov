# Roadmap: Unrestricted Agent Sharing Detector (v16)

## Overview

Continuous agent sharing compliance solution using BAP APIs to detect unsafe sharing configurations, record violations in Dataverse, drive remediation through Power Automate, and enforce time-bound exceptions via an Exception Manager app. Complements the existing Agent Access Governance Monitor (AAM = environment-level; UASD = per-agent).

**Source:** User-provided solution design spec. All APIs, tables, and flows implemented exactly as specified.

**Execution model:** 5 phases, linear dependency chain. Within each phase, plans target non-overlapping file sets for parallel execution where possible.

## Phases

- [x] **Phase 1: Solution Infrastructure** — Dataverse schema (5 tables), option sets (6 UASD-specific + 2 shared), environment variables, connection references, seed data
- [ ] **Phase 2: Detection Engine** — Detector flow, on-demand audit script, adaptive card template
- [ ] **Phase 3: Remediation & Exception Management** — Remediation flow, exception approval flow, Exception Manager canvas app, approved group import script
- [ ] **Phase 4: Deployment & Operations** — Deployment scripts, violation export script, deployment guide documentation
- [ ] **Phase 5: Framework Integration & Validation** — Solutions-index entry, control updates (1.1, 3.8), architecture docs, mkdocs nav, AAM status reconciliation, full validation

## Phase Details

### Phase 1: Solution Infrastructure
**Goal:** Create all Dataverse tables, option sets, environment variables, and connection references needed by downstream phases
**Depends on:** Nothing (foundational)
**Requirements:** INFRA-01, INFRA-02, INFRA-03
**Success Criteria:**
  1. Schema script creates 5 tables with `fsi_` prefix, all columns per spec §2
  2. `fsi_acv_zone` and `fsi_acv_severity` shared option sets referenced (not duplicated)
  3. 6 solution-specific option sets created (`fsi_UASD_sharingscope`, `fsi_UASD_violationtype`, `fsi_UASD_violationstatus`, `fsi_UASD_exceptionstatus`, `fsi_UASD_authmode`, `fsi_UASD_dataclassification`)
  4. 4 environment variables and 2 connection references defined
  5. Seed policy row documented: `MaxIndividualSharesPerAgent = 100, Zone = All`
**Plans:** 2 (A = schema script + option sets, B = env vars + connection refs + seed data)

### Phase 2: Detection Engine
**Goal:** Build the detection flow and on-demand audit script implementing all 5 violation rules
**Depends on:** Phase 1 (tables must exist for Dataverse operations)
**Requirements:** DET-01, DET-02, DET-03
**Success Criteria:**
  1. Detector flow JSON importable into Power Automate with correct trigger, BAP API calls, and Dataverse operations
  2. All 5 violation rules implemented per spec §4.1 (ORG_WIDE_SHARING, PUBLIC_INTERNET_LINK, UNAPPROVED_GROUP, EXCESSIVE_INDIVIDUAL, CROSS_TENANT_ACCESS)
  3. `Invoke-SharingAudit.ps1` runs on-demand with `#Requires -Version 7.0`, standard header, `-OutputFormat`/`-OutputPath` parameters
  4. Adaptive card template follows established pattern with severity-based styling
**Plans:** 2 (A = detector flow JSON + adaptive card, B = `Invoke-SharingAudit.ps1`)

### Phase 3: Remediation & Exception Management
**Goal:** Build remediation workflow with approval-based principal overwrite and exception lifecycle management
**Depends on:** Phase 1 (tables), conceptually Phase 2 (violations trigger remediation)
**Requirements:** REM-01, REM-02, REM-03
**Success Criteria:**
  1. Remediation flow triggers on `fsi_SharingViolation` creation where status = Open
  2. Exception check suppresses remediation for agents with active, non-expired exceptions
  3. Default mode is Approval for ALL zones; auto only for PUBLIC_INTERNET_LINK when `fsi_UASD_AutoRemediatePublicLink = true`
  4. BAP PATCH overwrites principals with approved security group(s) per spec §3.3
  5. Exception Approval flow implements sequential dual approval (Security → Data Owner)
  6. Exception Manager canvas app provides submission, status view, and expiration display
  7. `Import-ApprovedSecurityGroups.ps1` upserts from CSV/JSON, idempotent
**Plans:** 2 (A = remediation flow + exception approval flow, B = canvas app + import script)

### Phase 4: Deployment & Operations
**Goal:** Create deployment and operations scripts enabling enterprise teams to import, configure, and operate the solution
**Depends on:** Phases 1-3 (all artifacts must exist for deployment and export)
**Requirements:** OPS-01, OPS-02, OPS-03
**Success Criteria:**
  1. `Deploy-DetectionFlow.ps1` imports detector flow, binds connection references, idempotent
  2. `Deploy-RemediationFlow.ps1` imports remediation flow, binds connections, sets auto-remediation flag
  3. `Export-ViolationReport.ps1` queries Dataverse violations, outputs CSV/JSON, `-IncludeEvidence` SHA-256 hash
  4. Deployment guide with prerequisites, step-by-step instructions, and validation checklist
**Plans:** 2 (A = deploy scripts, B = export script + deployment guide)

### Phase 5: Framework Integration & Validation
**Goal:** Integrate solution into framework controls, reference catalogs, and site navigation; validate everything
**Depends on:** Phases 1-4 (all content finalized before framework cross-references)
**Requirements:** FRM-01, FRM-02, FRM-03, VAL-01
**Success Criteria:**
  1. `solutions-index.md` includes UASD entry with status, components, regulatory alignment, control mappings
  2. Controls 1.1 and 3.8 updated with tip admonitions linking to UASD
  3. Architecture and deployment docs created in `docs/playbooks/advanced-implementations/unrestricted-agent-sharing-detector/`
  4. `mkdocs.yml` nav updated under Advanced Implementations
  5. AAM status reconciled (WIP → Completed in solutions-index.md)
  6. All 7 spec validation tests pass
  7. `mkdocs build --strict` passes, `verify_controls.py` 62/62, `verify_language_rules.py` 0 violations
**Plans:** 2 (A = solutions-index + control updates + architecture docs, B = mkdocs nav + AAM reconciliation + build validation)

## Progress

| Phase | Plans Complete | Status |
|-------|---------------|--------|
| 1. Solution Infrastructure | 2/2 | Complete |
| 2. Detection Engine | 0/2 | Not Started |
| 3. Remediation & Exception Management | 0/2 | Not Started |
| 4. Deployment & Operations | 0/2 | Not Started |
| 5. Framework Integration & Validation | 0/2 | Not Started |

## Parallel Execution Guide

Phases have a **linear dependency chain** (1 → 2 → 3 → 4 → 5). Within each phase, plans target non-overlapping file sets:

| Phase | Plan A Files | Plan B Files | Parallel? |
|-------|-------------|-------------|-----------|
| 1 | `scripts/create_uasd_dataverse_schema.py` | `scripts/create_uasd_environment_variables.py`, `scripts/create_uasd_connection_references.py` | Yes |
| 2 | `src/uasd-detector-scan-agents.json`, `src/adaptive-card-uasd-alert.json` | `scripts/governance/Invoke-SharingAudit.ps1` | Yes |
| 3 | `src/uasd-remediation-*.json`, `src/uasd-exception-*.json` | Canvas app, `scripts/governance/Import-ApprovedSecurityGroups.ps1` | Yes |
| 4 | `scripts/governance/Deploy-*Flow.ps1` | `scripts/governance/Export-ViolationReport.ps1`, deployment guide | Yes |
| 5 | `docs/reference/solutions-index.md`, `docs/controls/pillar-*`, architecture docs | `mkdocs.yml`, validation (read-only) | Yes |

## File Manifest

### Created (new files)

| Phase | File | Purpose |
|-------|------|---------|
| 1 | `scripts/create_uasd_dataverse_schema.py` | Dataverse table definitions |
| 1 | `scripts/create_uasd_environment_variables.py` | Environment variable definitions |
| 1 | `scripts/create_uasd_connection_references.py` | Connection reference definitions |
| 2 | `src/uasd-detector-scan-agents.json` | Detector flow JSON |
| 2 | `src/adaptive-card-uasd-alert.json` | Teams alert adaptive card |
| 2 | `scripts/governance/Invoke-SharingAudit.ps1` | On-demand detection script |
| 3 | `src/uasd-remediation-apply-sharing-policy.json` | Remediation flow JSON |
| 3 | `src/uasd-exception-approval-workflow.json` | Exception approval flow JSON |
| 3 | `scripts/governance/Import-ApprovedSecurityGroups.ps1` | Approved group import |
| 4 | `scripts/governance/Deploy-DetectionFlow.ps1` | Detector flow deployment |
| 4 | `scripts/governance/Deploy-RemediationFlow.ps1` | Remediation flow deployment |
| 4 | `scripts/governance/Export-ViolationReport.ps1` | Violation export with SHA-256 |
| 4 | `docs/playbooks/advanced-implementations/unrestricted-agent-sharing-detector/deployment-guide.md` | Deployment guide |
| 5 | `docs/playbooks/advanced-implementations/unrestricted-agent-sharing-detector/index.md` | Solution architecture overview |

### Modified (existing files)

| Phase | File | Change |
|-------|------|--------|
| 5 | `docs/reference/solutions-index.md` | Add UASD entry, fix AAM status |
| 5 | `docs/controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md` | Add tip admonition |
| 5 | `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md` | Add tip admonition |
| 5 | `mkdocs.yml` | Add nav entries |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| INFRA-01 | 1 | 01-01 | Dataverse schema with 5 tables |
| INFRA-02 | 1 | 01-02 | Environment variables + connection references |
| INFRA-03 | 1 | 01-02 | Seed data + inline agent identity |
| DET-01 | 2 | 02-01 | Detector flow with 5 violation rules |
| DET-02 | 2 | 02-02 | On-demand audit script |
| DET-03 | 2 | 02-01 | Adaptive card template |
| REM-01 | 3 | 03-01 | Remediation flow |
| REM-02 | 3 | 03-01 | Exception approval flow |
| REM-03 | 3 | 03-02 | Exception Manager canvas app |
| OPS-01 | 3 | 03-02 | Import approved security groups script |
| OPS-02 | 4 | 04-01 | Deployment scripts |
| OPS-03 | 4 | 04-02 | Violation export script |
| FRM-01 | 5 | 05-01 | Solutions-index entry |
| FRM-02 | 5 | 05-01 | Control updates + architecture docs |
| FRM-03 | 5 | 05-02 | mkdocs nav + AAM reconciliation |
| VAL-01 | 5 | 05-02 | Build and language validation |

**Total: 16/16 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-12*
*Depth: comprehensive*
*Phases: 5 (infrastructure → detection → remediation/exceptions → deployment/ops → framework integration)*
