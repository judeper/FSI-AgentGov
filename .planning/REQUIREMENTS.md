# Requirements: Unrestricted Agent Sharing Detector (v16)

## Overview

Continuous agent sharing compliance solution that detects unsafe or noncompliant sharing configurations using BAP APIs, records violations in Dataverse, drives remediation through Power Automate, and enforces time-bound exceptions via an Exception Manager app.

**Source:** User-provided solution design spec (Unrestricted Agent Sharing Detector AI Implementation Spec)

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| INFRA | Solution Infrastructure | 3 |
| DET | Detection Engine | 3 |
| REM | Remediation & Exceptions | 3 |
| OPS | Deployment & Operations | 3 |
| FRM | Framework Integration | 3 |
| VAL | Validation | 1 |
| **Total** | | **16** |

## INFRA — Solution Infrastructure

- [ ] **INFRA-01:** Create Dataverse schema with 5 tables (`fsi_AgentSharingSetting`, `fsi_SharingViolation`, `fsi_SharingException`, `fsi_ApprovedSecurityGroup`, `fsi_SharingPolicy`) using `fsi_` prefix convention, reusing `fsi_acv_zone` and `fsi_acv_severity` shared option sets, creating 6 solution-specific option sets (`fsi_UASD_*`)
- [ ] **INFRA-02:** Define environment variables (`fsi_UASD_AutoRemediatePublicLink`, `fsi_UASD_ScanFrequencyHours`, `fsi_UASD_HomeTenantId`, `fsi_UASD_DefaultExceptionDays`) and connection references (`fsi_cr_dataverse_sharingdetector`, `fsi_cr_teams_sharingdetector`)
- [ ] **INFRA-03:** Seed default sharing policy row (`MaxIndividualSharesPerAgent = 100, Zone = All`) in `fsi_SharingPolicy`; inline agent identity fields (`fsi_agent_id`, `fsi_agent_name`, `fsi_environment_id`) on agent-referencing tables

## DET — Detection Engine

- [ ] **DET-01:** Build Detector flow (`fsi-UASD-Detector-ScanAgents`) — scheduled trigger, BAP API agent enumeration (spec §3.1), principal retrieval (spec §3.2), Dataverse upsert to `fsi_AgentSharingSetting`, all 5 violation rules (ORG_WIDE_SHARING, PUBLIC_INTERNET_LINK, UNAPPROVED_GROUP, EXCESSIVE_INDIVIDUAL, CROSS_TENANT_ACCESS) per spec §4.1
- [ ] **DET-02:** Build `Invoke-SharingAudit.ps1` — on-demand PowerShell detection script calling BAP APIs directly, writing to Dataverse, evaluating violation rules; `#Requires -Version 7.0`, standard header, `-OutputFormat`, `-OutputPath` parameters
- [ ] **DET-03:** Build adaptive card template (`adaptive-card-uasd-alert.json`) for sharing violation Teams notifications following established pattern

## REM — Remediation & Exceptions

- [ ] **REM-01:** Build Remediation flow (`fsi-UASD-Remediation-ApplySharingPolicy`) — triggered on `fsi_SharingViolation` creation/update where status = Open; exception check, approval/automatic path (auto only for PUBLIC_INTERNET_LINK when enabled), BAP PATCH to overwrite principals (spec §3.3)
- [ ] **REM-02:** Build Exception Approval flow (`fsi-UASD-ExceptionApproval-Workflow`) — dual approval (security + data owner), 90-day default expiration, expiration scanner to mark expired exceptions
- [ ] **REM-03:** Build Exception Manager Canvas App — exception submission (agent selection, business justification, data classification), dual approval status display, expiration enforcement

## OPS — Deployment & Operations

- [ ] **OPS-01:** Implement `Import-ApprovedSecurityGroups.ps1` — CSV/JSON import into `fsi_ApprovedSecurityGroup`, upsert on `fsi_entraid_group_id`, idempotent
- [ ] **OPS-02:** Implement deployment scripts (`Deploy-DetectionFlow.ps1`, `Deploy-RemediationFlow.ps1`) — import/update flows, bind connection references, idempotent re-run
- [ ] **OPS-03:** Implement `Export-ViolationReport.ps1` — query violations and sharing settings from Dataverse, CSV/JSON output, `-IncludeEvidence` SHA-256 hash support

## FRM — Framework Integration

- [ ] **FRM-01:** Add Unrestricted Agent Sharing Detector entry to `solutions-index.md` with status, components, regulatory alignment (FINRA 4511, SOX 404, SEC 17a-3/4, GLBA 501(b)), control mappings (1.1, 3.8)
- [ ] **FRM-02:** Update Controls 1.1 and 3.8 with tip admonitions linking to UASD solution; create architecture and deployment docs in `docs/playbooks/advanced-implementations/unrestricted-agent-sharing-detector/`
- [ ] **FRM-03:** Add nav entries to `mkdocs.yml` under Advanced Implementations; reconcile AAM status discrepancy in solutions-index.md (WIP → Completed)

## VAL — Validation

- [ ] **VAL-01:** All 7 spec validation tests pass (compliant agent, org-wide violation, public internet link, excessive individual, cross-tenant, exception suppression, exception expiration); `mkdocs build --strict` passes; `verify_controls.py` 62/62; `verify_language_rules.py` 0 violations

## Out of Scope

| Item | Reason |
|------|--------|
| Microsoft Graph for sharing decisions | Non-Negotiable Rule #2 — BAP APIs only |
| Managed identity / production-grade auth | Lab-grade implementation; expandable later |
| Agent inventory Dataverse table | Control 3.1 is CSV/SharePoint-based; inline fields sufficient |
| Power BI dataset | Optional, implement last per spec — deferred beyond v16 |
| Real-time detection | Scheduled/on-demand sufficient per framework constraints |
| Cross-solution Compliance Dashboard feed | Deferred to future integration milestone |

## Traceability

| Requirement | Spec Section | Phase |
|-------------|-------------|-------|
| INFRA-01 | §2 (Dataverse Schema) | 1 |
| INFRA-02 | §7 (Execution Identity) | 1 |
| INFRA-03 | §2.5 (Seed Data) | 1 |
| DET-01 | §3.1, §3.2, §4.1 | 2 |
| DET-02 | §8 (Invoke-SharingAudit) | 2 |
| DET-03 | Adaptive Card pattern | 2 |
| REM-01 | §5 (Remediation Flow) | 3 |
| REM-02 | §6 (Exception Manager) | 3 |
| REM-03 | §6 (Exception Manager App) | 3 |
| OPS-01 | §8 (Import-ApprovedSecurityGroups) | 4 |
| OPS-02 | §8 (Deploy-*Flow) | 4 |
| OPS-03 | §8 (Export-ViolationReport) | 4 |
| FRM-01 | — (framework standard) | 5 |
| FRM-02 | — (framework standard) | 5 |
| FRM-03 | — (framework standard) | 5 |
| VAL-01 | §9 (Validation Tests) | 5 |

---
*Requirements defined: 2026-02-12*
*Source: Unrestricted Agent Sharing Detector AI Implementation Spec*
