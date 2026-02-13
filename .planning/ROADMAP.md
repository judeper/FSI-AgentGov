# Roadmap: Audit Logging Compliance Automation (v21)

## Overview

Build an enterprise-grade audit logging compliance solution for Power Platform environments — automated detection of Purview unified audit and Dataverse audit status, remediation with entity-level audit enablement, Azure Automation runbook execution via Managed Identity, Dataverse compliance tracking, and optional approval workflow. Complements existing Audit Configuration Validator (ACV v1.0.0, shipped v4). Maps to Control 1.7 (no new control).

**Source:** v21 requirements (21 requirements across 8 categories). Maps to existing Control 1.7 — no new control, framework stays at 71 controls. No control count, playbook count, or pillar count changes.

**Execution model:** 7 phases. Phases 1–2 are independent (parallel-eligible). Phases 3–4 depend on Phase 1 only (parallel-eligible with each other). Phase 5 depends on Phases 1–4. Phase 6 depends on Phases 2–3. Phase 7 depends on all. Within each phase, plans target non-overlapping file sets for parallel execution.

**Cross-repo:** Solution artifacts in FSI-AgentGov-Solutions (`audit-logging-compliance-automation/`); documentation and framework integration in FSI-AgentGov.

**Key constraints:**
- Enterprise auth: System-Assigned Managed Identity in Azure Automation (NEVER interactive, NEVER hardcoded credentials)
- `fsi_` prefix for all Dataverse tables (not `jude_` from dev environment)
- Upsert pattern (query-then-create-or-update) — different from ACV's immutable history
- Audit enablement ONLY — retention is OUT OF SCOPE (managed by Microsoft Purview)
- 6 Copilot Studio entities for entity-level audit: bot, botcomponent, connectionreference, environmentvariablevalue, workflow, systemuser

## Phases

- [x] **Phase 1: Helper Module & Tests** — `AuditComplianceHelpers.psm1` (6 functions), module manifest (.psd1), Pester 5 unit tests
- [ ] **Phase 2: Dataverse Schema** — `fsi_auditenvironmentcompliance` table, schema creation script (Python), seed data configuration
- [x] **Phase 3: Detection Runbook** — `Check-AuditLoggingCompliance.ps1` with MI + Exchange Online + BAP auth, per-environment scanning, compliance determination, CSV + email output
- [ ] **Phase 4: Remediation Runbook** — `Enable-AuditLogging.ps1` with org-level + entity-level audit enablement, WhatIf, validation, compliance record updates
- [ ] **Phase 5: Deployment & Documentation** — Deployment guide (Azure Automation, MI permissions, scheduling), testing scenarios (15), troubleshooting guide (10 issues)
- [ ] **Phase 6: Approval Flow** — Power Automate approval flow specification, flow template JSON or config guide
- [ ] **Phase 7: Framework Integration & Validation** — Solutions-index entry, Control 1.7 cross-references, ACV cross-reference, build validation

## Phase Details

### Phase 1: Helper Module & Tests
**Goal:** Create the shared PowerShell helper module used by both detection and remediation runbooks, with module manifest and comprehensive Pester 5 unit tests
**Depends on:** Nothing (independent)
**Requirements:** MOD-01, MOD-02, MOD-03
**Success Criteria:**
  1. `AuditComplianceHelpers.psm1` exports 6 functions — `Invoke-WithRetry` (exponential backoff with jitter for 429/503/504, configurable MaxRetries/InitialDelaySeconds/MaxDelaySeconds), `Get-ManagedIdentityToken` (Azure Automation MI token via IDENTITY_ENDPOINT/IDENTITY_HEADER), `Get-DataverseToken` (Dataverse-specific token with URL normalization), `Invoke-DataverseRequest` (Web API wrapper with OData headers, retry logic, GET/POST/PATCH/DELETE/PUT), `Write-DataverseComplianceRecord` (upsert by fsi_environmentid with option set mapping: Compliant=100000000, Non-Compliant=100000001, Remediation Pending=100000002, Error=100000003), `Send-ComplianceNotification` (Graph sendMail via shared mailbox with base64 attachment)
  2. Module manifest (.psd1) with version 1.0.0, proper FunctionsToExport, description, and PowerShell 7.2 compatibility. Module packageable as .zip for Azure Automation import. NEVER uses interactive auth or hardcoded credentials.
  3. Pester 5 unit tests covering: `Invoke-WithRetry` retry behavior (retryable vs non-retryable), `Get-ManagedIdentityToken` with mocked endpoints, `Write-DataverseComplianceRecord` upsert logic (create new + update existing), `Send-ComplianceNotification` payload construction, status string-to-option-set mapping
  4. All files in `FSI-AgentGov-Solutions/audit-logging-compliance-automation/src/`
**Plans:** 2 (A = module .psm1 + manifest .psd1, B = Pester 5 unit tests)

### Phase 2: Dataverse Schema
**Goal:** Create the Dataverse table schema for audit environment compliance tracking with schema creation script and seed data documentation
**Depends on:** Nothing (independent)
**Requirements:** DVS-01, DVS-02
**Success Criteria:**
  1. `fsi_auditenvironmentcompliance` table schema — Display Name: "Audit Environment Compliance", Primary Column: fsi_environmentname. Columns: `fsi_environmentid` (Single Line Text, upsert key), `fsi_environmentname` (Single Line Text), `fsi_auditenabled` (Yes/No, Purview unified audit), `fsi_dataverseauditenabled` (Yes/No, Dataverse auditing), `fsi_lastchecked` (DateTime UTC), `fsi_compliancestatus` (Choice: Compliant=100000000, Non-Compliant=100000001, Remediation Pending=100000002, Error=100000003), `fsi_remediationdate` (DateTime), `fsi_remediatedby` (Single Line Text), `fsi_errormessage` (Multi-line Text), `fsi_lasteventcaptured` (DateTime). Alternate key on fsi_environmentid for upsert support.
  2. Schema creation script (Python) — table definition JSON, column definitions with proper data types and option set values, alternate key creation, seed data configuration documentation
  3. All files in `FSI-AgentGov-Solutions/audit-logging-compliance-automation/src/`
**Plans:** 1 (table schema + creation script + seed data docs)

### Phase 3: Detection Runbook
**Goal:** Create the detection runbook that scans all Power Platform environments for Purview unified audit and Dataverse audit compliance, writing results to Dataverse
**Depends on:** Phase 1 (imports AuditComplianceHelpers module functions)
**Requirements:** DET-01, DET-02, DET-03
**Success Criteria:**
  1. `Check-AuditLoggingCompliance.ps1` with parameters — `DataverseEnvironmentUrl` (mandatory), `NotificationFromAddress` (optional), `NotificationToAddresses` (optional, comma-separated), `SendEmail` (switch, default false), `TenantDomain` (mandatory). Requires PowerShell 7.2, Microsoft.PowerApps.Administration.PowerShell v2.0+, ExchangeOnlineManagement v3.0+.
  2. Detection flow — MI auth to Power Platform (Add-PowerAppsAccount) + Exchange Online (Connect-ExchangeOnline -ManagedIdentity -Organization), enumerate environments (Get-AdminPowerAppEnvironment), per-environment: check Purview unified audit (Get-AdminConfig → UnifiedAuditLogIngestionEnabled), check Dataverse audit (/api/data/v9.2/organizations?$select=isauditenabled), validate recent audit events (Search-UnifiedAuditLog last 7 days), determine compliance (Dataverse env = BOTH Purview + Dataverse; non-Dataverse = Purview only), write compliance record via Write-DataverseComplianceRecord upsert
  3. Output — console with numbered progress steps, per-environment status display, compliance summary (total/compliant/non-compliant/errors), CSV export to $env:TEMP, optional HTML email with summary + CSV attachment. Error handling: try/catch per environment (ComplianceStatus=Error, continue), fatal auth failures throw and exit, finally block disconnects
  4. All files in `FSI-AgentGov-Solutions/audit-logging-compliance-automation/src/`
**Plans:** 2 (A = runbook core — parameters, auth, scanning, compliance determination, B = output formatting, email notification, error handling, CSV export)

### Phase 4: Remediation Runbook
**Goal:** Create the remediation runbook that enables org-level and entity-level Dataverse auditing on non-compliant environments with WhatIf support and validation
**Depends on:** Phase 1 (imports AuditComplianceHelpers module functions)
**Requirements:** REM-01, REM-02, REM-03
**Success Criteria:**
  1. `Enable-AuditLogging.ps1` with parameters — `DataverseEnvironmentUrl` (mandatory), `TenantDomain` (mandatory), `EnvironmentId` (optional, specific env or all non-compliant), `EnableTenantUnifiedAudit` (switch, default true), `WhatIf` (switch, default false). CmdletBinding with SupportsShouldProcess. Requires PowerShell 7.2, same modules as detection.
  2. Remediation flow — MI auth (same as detection), determine targets (specific env or query Dataverse for fsi_compliancestatus=100000001), optionally enable tenant-wide Purview unified audit via Set-AdminConfig (with tenant-wide change warning), per-environment: enable Dataverse org-level audit (PATCH /api/data/v9.2/organizations({id}) isauditenabled=true), enable entity-level audit on 6 entities (bot, botcomponent, connectionreference, environmentvariablevalue, workflow, systemuser) via PUT EntityDefinitions IsAuditEnabled.Value=true, validate after 5-second propagation wait, update Dataverse compliance record to Compliant
  3. Output — console with progress steps, per-environment remediation status, WhatIf simulation ("[WHATIF] Would enable..."), remediation summary (processed/successful/no-changes/failed), CSV export, validation pass/fail. Error handling: per-environment try/catch, validation failures set status="Validation Failed", continue processing
  4. All files in `FSI-AgentGov-Solutions/audit-logging-compliance-automation/src/`
**Plans:** 2 (A = runbook core — parameters, auth, remediation flow, entity-level enablement, B = output formatting, WhatIf logic, validation, error handling, CSV export)

### Phase 5: Deployment & Documentation
**Goal:** Create comprehensive deployment guides, testing scenarios, and troubleshooting documentation for the ALCA solution
**Depends on:** Phases 1–4 (needs to reference actual module, runbook, and schema artifacts)
**Requirements:** DPL-01, DPL-02, DPL-03, TST-01, TST-02
**Success Criteria:**
  1. Deployment guide Phase 1-3 — Azure Automation Account setup (FSI-AgentGov-Automation, PowerShell 7.2, System-Assigned MI, same region as PP tenant), MI permissions (Entra roles: Power Platform Administrator + Exchange Administrator; Graph: Mail.Send with admin consent; Dataverse: Application User with System Administrator per target environment), shared mailbox setup (powerplatform-governance@, SendAs permission for MI)
  2. Deployment guide Phase 4-5 — Module import (AuditComplianceHelpers.psm1 as .zip, gallery modules verified Status=Available on Runtime 7.2), runbook creation (Check-AuditLoggingCompliance + Enable-AuditLogging, both PowerShell type, Runtime 7.2, publish)
  3. Scheduling documentation — Weekly-Audit-Compliance-Check schedule (Monday 6:00 AM ET, linked to detection runbook), optional Daily-Audit-Validation, parameter configuration reference
  4. Testing scenarios (15 scenarios) — all compliant, mixed compliance, Purview disabled, event validation, 4 remediation scenarios (WhatIf, Dataverse enable, tenant Purview, validation failure), retry/throttling, multi-recipient email, 2 Dataverse upsert (create + update), 2 error handling (env-level + fatal auth), scheduled execution. Each with setup, expected results, verification steps.
  5. Troubleshooting guide (10 issues) — Power Platform auth failure, Exchange Online auth failure, Dataverse 401, email not sent, Dataverse table not updated, 429 throttling, validation failure after remediation, Search-UnifiedAuditLog not found, CSV export path failure, WhatIf not working. Each with symptoms, causes, resolution steps.
  6. Deployment + scheduling docs in `FSI-AgentGov-Solutions/audit-logging-compliance-automation/docs/`; testing + troubleshooting in `FSI-AgentGov-Solutions/audit-logging-compliance-automation/docs/`
**Plans:** 3 (A = deployment guide phases 1-3, B = deployment guide phases 4-5 + scheduling, C = testing scenarios + troubleshooting guide)

### Phase 6: Approval Flow
**Goal:** Create a Power Automate approval flow specification and template for governance-approved remediation execution
**Depends on:** Phases 2, 3 (references Dataverse schema for non-compliant environment queries and detection output format)
**Requirements:** FLW-01, FLW-02
**Success Criteria:**
  1. Approval flow specification — trigger: weekly recurrence after detection script, Step 1: HTTP GET non-compliant environments from Dataverse (fsi_compliancestatus=100000001), Step 2: Condition check (count > 0), Step 3: Start approval (Approve/Reject, assigned to governance lead, includes environment list), Step 4: If approved trigger Enable-AuditLogging runbook via Azure Management API PUT, Step 5: Send completion notification
  2. Flow template (JSON definition) or detailed configuration guide — all HTTP action URIs, authentication patterns (Dataverse connection + Azure Management MI), approval card template, variable definitions (DataverseUrl, TenantDomain), error handling for failed runbook execution
  3. All files in `FSI-AgentGov-Solutions/audit-logging-compliance-automation/src/`
**Plans:** 1 (approval flow specification + template/config guide)

### Phase 7: Framework Integration & Validation
**Goal:** Integrate ALCA into the FSI-AgentGov framework documentation — solutions catalog entry, Control 1.7 cross-references, ACV complementary note, and full build validation
**Depends on:** Phases 1–6 (all solution artifacts and documentation must exist before framework references them)
**Requirements:** FRM-01, FRM-02, FRM-03
**Success Criteria:**
  1. `docs/reference/solutions-index.md` includes ALCA entry — summary table row (Audit Logging Compliance Automation, v1.0.0, Completed, description, Related Controls: 1.7), detail section with components (helper module, detection runbook, remediation runbook, Dataverse table, deployment guide, approval flow), regulatory alignment (FINRA 4511, SEC 17a-3/4, SOX 404, GLBA 501(b)), repository link, relationship note explaining ALCA vs ACV complementary scope
  2. Control 1.7 cross-references updated — ALCA added to implementation guides or related solutions section, `mkdocs.yml` updated if new documentation pages added, ACV solution entry updated with cross-reference noting ALCA as complementary solution
  3. `mkdocs build --strict` passes with zero errors/warnings, `python scripts/verify_controls.py` 71/71 controls valid, no broken internal links, navigation matches actual file structure
**Plans:** 2 (A = solutions-index entry + Control 1.7 cross-references + ACV cross-reference + mkdocs.yml, B = build validation + cross-reference verification)

## Progress

| Phase | Plans | Plans Complete | Status |
|-------|-------|---------------|--------|
| 1. Helper Module & Tests | 2 | 2/2 | Complete |
| 2. Dataverse Schema | 1 | 1/1 | Complete |
| 3. Detection Runbook | 2 | 2/2 | Complete |
| 4. Remediation Runbook | 2 | 2/2 | Complete |
| 5. Deployment & Documentation | 3 | 0/3 | Not Started |
| 6. Approval Flow | 1 | 0/1 | Not Started |
| 7. Framework Integration & Validation | 2 | 0/2 | Not Started |

## Parallel Execution Guide

Phases 1 and 2 are **independent** — no shared file targets, parallel-eligible. Phases 3 and 4 both depend on Phase 1 only and target non-overlapping files — parallel-eligible with each other after Phase 1 completes. Phase 6 depends on Phases 2 and 3. Phase 5 depends on Phases 1–4. Phase 7 depends on all.

```
Phase 1 (MOD) ──┬── Phase 3 (DET) ──┬── Phase 6 (FLW) ──┐
                │                    │                    │
                ├── Phase 4 (REM) ──┐│                    ├── Phase 7 (FRM)
                │                   ││                    │
Phase 2 (DVS) ──┼───────────────────┴┴── Phase 5 (DPL) ──┘
```

Within each phase, plans target non-overlapping file sets:

| Phase | Plan A Files | Plan B/C Files | Parallel? |
|-------|-------------|----------------|-----------|
| 1 | `AuditComplianceHelpers.psm1` + `.psd1` | `AuditComplianceHelpers.Tests.ps1` | Yes |
| 2 | Schema script + table JSON + seed data (single plan) | — | N/A |
| 3 | Runbook core (params, auth, scanning, compliance) | Output formatting, email, error handling | Yes |
| 4 | Runbook core (params, auth, remediation, entities) | Output, WhatIf, validation, error handling | Yes |
| 5 | A: Deployment phases 1-3, B: Deployment phases 4-5 + scheduling | C: Testing scenarios + troubleshooting | Yes |
| 6 | Approval flow spec + template (single plan) | — | N/A |
| 7 | Solutions-index + Control 1.7 + ACV cross-ref + mkdocs.yml | Build validation (read-only) | Yes |

## File Manifest

### Created (new files — FSI-AgentGov-Solutions)

| Phase | File | Purpose |
|-------|------|---------|
| 1 | `audit-logging-compliance-automation/README.md` | Solution README |
| 1 | `audit-logging-compliance-automation/CHANGELOG.md` | Version history |
| 1 | `audit-logging-compliance-automation/src/AuditComplianceHelpers.psm1` | Helper module (6 functions) |
| 1 | `audit-logging-compliance-automation/src/AuditComplianceHelpers.psd1` | Module manifest |
| 1 | `audit-logging-compliance-automation/src/AuditComplianceHelpers.Tests.ps1` | Pester 5 unit tests |
| 2 | `audit-logging-compliance-automation/src/create_audit_compliance_schema.py` | Dataverse schema creation script |
| 3 | `audit-logging-compliance-automation/src/Check-AuditLoggingCompliance.ps1` | Detection runbook |
| 4 | `audit-logging-compliance-automation/src/Enable-AuditLogging.ps1` | Remediation runbook |
| 5 | `audit-logging-compliance-automation/docs/deployment-guide.md` | Azure Automation deployment (phases 1-5) |
| 5 | `audit-logging-compliance-automation/docs/scheduling-guide.md` | Schedule configuration |
| 5 | `audit-logging-compliance-automation/docs/testing-scenarios.md` | 15 test scenarios |
| 5 | `audit-logging-compliance-automation/docs/troubleshooting.md` | 10 common issues |
| 6 | `audit-logging-compliance-automation/src/audit-remediation-approval-flow.json` | Power Automate approval flow template |

### Modified (existing files — FSI-AgentGov)

| Phase | File | Change |
|-------|------|--------|
| 7 | `docs/reference/solutions-index.md` | Add ALCA catalog entry (summary table row + detail section) |
| 7 | `docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md` | Add ALCA to related solutions / implementation guides |
| 7 | `mkdocs.yml` | Add nav entries if new documentation pages are added |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| MOD-01 | 1 | 01-01 | AuditComplianceHelpers.psm1 (6 functions) |
| MOD-02 | 1 | 01-01 | Module manifest (.psd1) with versioning and exports |
| MOD-03 | 1 | 01-02 | Pester 5 unit tests for helper module |
| DVS-01 | 2 | 02-01 | fsi_auditenvironmentcompliance table schema |
| DVS-02 | 2 | 02-01 | Schema creation script (Python) + seed data docs |
| DET-01 | 3 | 03-01 | Check-AuditLoggingCompliance.ps1 runbook (params, requires) |
| DET-02 | 3 | 03-01 | Detection flow (MI auth, scanning, compliance determination) |
| DET-03 | 3 | 03-02 | Detection output (console, CSV, email, error handling) |
| REM-01 | 4 | 04-01 | Enable-AuditLogging.ps1 runbook (params, requires) |
| REM-02 | 4 | 04-01 | Remediation flow (org-level, entity-level, validation) |
| REM-03 | 4 | 04-02 | Remediation output (WhatIf, CSV, validation, error handling) |
| DPL-01 | 5 | 05-01 | Deployment guide phases 1-3 (Azure Automation, MI, mailbox) |
| DPL-02 | 5 | 05-02 | Deployment guide phases 4-5 (module import, runbook creation) |
| DPL-03 | 5 | 05-02 | Scheduling documentation (weekly + optional daily) |
| FLW-01 | 6 | 06-01 | Approval flow specification |
| FLW-02 | 6 | 06-01 | Flow template JSON or configuration guide |
| TST-01 | 5 | 05-03 | Testing scenarios documentation (15 scenarios) |
| TST-02 | 5 | 05-03 | Troubleshooting guide (10 issues) |
| FRM-01 | 7 | 07-01 | Solutions-index ALCA entry + ACV cross-reference |
| FRM-02 | 7 | 07-01 | Control 1.7 cross-references + mkdocs.yml |
| FRM-03 | 7 | 07-02 | Build validation (mkdocs + verify_controls) |

**Total: 21/21 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-13*
*Depth: comprehensive*
*Phases: 7 (helper module → dataverse schema → detection → remediation → deployment/docs → approval flow → framework integration)*
