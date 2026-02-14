# Requirements: v21 — Audit Logging Compliance Automation (ALCA)

## Overview

Build an enterprise-grade audit logging compliance solution for Power Platform environments — automated detection of Purview unified audit and Dataverse audit status, remediation with entity-level audit enablement, Azure Automation runbook execution via Managed Identity, Dataverse compliance tracking, and optional approval workflow. Complements existing Audit Configuration Validator (ACV v1.0.0, shipped v4). Maps to Control 1.7 (no new control).

**Source:** Production-ready implementation spec (43 pages, 3 architect reviews, approved for production deployment, 2026-02-12). Defines Managed Identity auth, Azure Automation runbooks, Exchange Online integration, Dataverse upsert pattern.

**Accuracy notes:**
- Maps to existing Control 1.7 (Comprehensive Audit Logging) — no new control, framework stays at 71 controls
- Complements ACV (v4): ACV validates configs with drift detection + SHA-256 evidence; ALCA detects + remediates + automates approval
- Enterprise auth model: System-Assigned Managed Identity in Azure Automation (evolution from lab-grade interactive in v4-v18)
- PDF uses `jude_` prefix for Dataverse tables — rename to `fsi_` for framework consistency (v16+ convention)
- Upsert pattern (query-then-create-or-update) vs ACV's immutable history — different compliance data model
- Scope boundary: Audit enablement ONLY — retention OUT OF SCOPE (managed by Microsoft Purview)
- Entity-level audit enables auditing on 6 Copilot Studio entities (bot, botcomponent, connectionreference, environmentvariablevalue, workflow, systemuser)
- Exchange Online integration via Connect-ExchangeOnline -ManagedIdentity for Purview audit status
- 3 optional enhancements captured as deferred todos (RunId column, API monitoring, batch operations)

## Requirement Categories

| Code | Category | Count |
|------|----------|-------|
| MOD | Helper Module | 3 |
| DET | Detection Runbook | 3 |
| REM | Remediation Runbook | 3 |
| DVS | Dataverse Schema | 2 |
| DPL | Deployment & Automation | 3 |
| FLW | Approval Flow | 2 |
| TST | Testing & Troubleshooting | 2 |
| FRM | Framework Integration | 3 |
| **Total** | | **21** |

## MOD — Helper Module

- [ ] **MOD-01:** Create `AuditComplianceHelpers.psm1` PowerShell module with 6 exported functions — `Invoke-WithRetry` (exponential backoff with jitter for 429/503/504, configurable MaxRetries/InitialDelaySeconds/MaxDelaySeconds), `Get-ManagedIdentityToken` (Azure Automation MI token acquisition via IDENTITY_ENDPOINT/IDENTITY_HEADER), `Get-DataverseToken` (Dataverse-specific token with URL normalization), `Invoke-DataverseRequest` (Web API wrapper with OData headers, retry logic, support for GET/POST/PATCH/DELETE/PUT), `Write-DataverseComplianceRecord` (upsert by fsi_environmentid with option set status mapping: Compliant=100000000, Non-Compliant=100000001, Remediation Pending=100000002, Error=100000003), `Send-ComplianceNotification` (Graph sendMail via shared mailbox with base64 attachment support)

- [ ] **MOD-02:** Create module manifest (.psd1) with proper versioning, function exports, and module description. All functions must use Managed Identity authentication (NEVER interactive auth, NEVER hardcoded credentials). Module must be packageable as .zip for Azure Automation import.

- [ ] **MOD-03:** Create Pester 5 unit tests for helper module — test Invoke-WithRetry retry behavior (retryable vs non-retryable errors), test Get-ManagedIdentityToken with mocked endpoints, test Write-DataverseComplianceRecord upsert logic (create new + update existing), test Send-ComplianceNotification payload construction, test status string-to-option-set mapping

## DET — Detection Runbook

- [ ] **DET-01:** Create `Check-AuditLoggingCompliance.ps1` runbook with parameters — `DataverseEnvironmentUrl` (mandatory, URL hosting compliance table), `NotificationFromAddress` (optional, shared mailbox default), `NotificationToAddresses` (optional, comma-separated), `SendEmail` (switch, default false), `TenantDomain` (mandatory, e.g., contoso.onmicrosoft.com). Requires PowerShell 7.2, Microsoft.PowerApps.Administration.PowerShell v2.0+, ExchangeOnlineManagement v3.0+.

- [ ] **DET-02:** Implement detection flow — Step 1: Authenticate to Power Platform via MI token + Add-PowerAppsAccount, Step 2: Authenticate to Exchange Online via Connect-ExchangeOnline -ManagedIdentity -Organization, Step 3: Get all environments via Get-AdminPowerAppEnvironment, Step 4: For each environment check Purview unified audit (Get-AdminConfig → UnifiedAuditLogIngestionEnabled), check Dataverse audit (query /api/data/v9.2/organizations?$select=isauditenabled), validate recent audit events (Search-UnifiedAuditLog last 7 days for PowerAppsApp/PowerAppsPlan/PowerAppsResource), Step 5: Determine compliance (Dataverse env requires BOTH Purview + Dataverse audit; non-Dataverse env requires Purview only), Step 6: Write compliance record to Dataverse via Write-DataverseComplianceRecord upsert

- [ ] **DET-03:** Implement detection output — console output with numbered progress steps, per-environment status display (ID, Dataverse provisioned, audit status, last event, compliance status), compliance summary (total/compliant/non-compliant/errors), CSV export to $env:TEMP, optional HTML email notification with summary table + CSV attachment via Send-ComplianceNotification. Error handling: try/catch per environment (ComplianceStatus=Error, continue), fatal auth failures throw and exit, finally block disconnects Exchange Online and Power Platform

## REM — Remediation Runbook

- [ ] **REM-01:** Create `Enable-AuditLogging.ps1` runbook with parameters — `DataverseEnvironmentUrl` (mandatory), `TenantDomain` (mandatory), `EnvironmentId` (optional, specific env or all non-compliant), `EnableTenantUnifiedAudit` (switch, default true), `WhatIf` (switch, default false). CmdletBinding with SupportsShouldProcess. Requires PowerShell 7.2, same modules as detection.

- [ ] **REM-02:** Implement remediation flow — Step 1: Authenticate (same as detection), Step 2: Determine targets (if EnvironmentId provided use that; otherwise query Dataverse for fsi_compliancestatus=100000001), Step 3: Optionally enable tenant-wide Purview unified audit via Set-AdminConfig (with tenant-wide change warning), Step 4: For each environment enable Dataverse org-level audit (PATCH /api/data/v9.2/organizations({id}) with isauditenabled=true), enable entity-level audit on 6 entities (bot, botcomponent, connectionreference, environmentvariablevalue, workflow, systemuser) via PUT EntityDefinitions with IsAuditEnabled.Value=true, Step 5: Validate changes after 5-second propagation wait (re-read org settings + entity settings), Step 6: Update Dataverse compliance record to Compliant

- [ ] **REM-03:** Implement remediation output — console output with progress steps, per-environment remediation status, WhatIf simulation output ("[WHATIF] Would enable..."), remediation summary (processed/successful/no-changes/failed), CSV export, validation pass/fail reporting. Error handling: per-environment try/catch, validation failures set status="Validation Failed", continue processing

## DVS — Dataverse Schema

- [ ] **DVS-01:** Create `fsi_auditenvironmentcompliance` table schema — Display Name: "Audit Environment Compliance", Primary Column: fsi_environmentname (environment display name). Columns: `fsi_environmentid` (Single Line Text, environment GUID — upsert key), `fsi_environmentname` (Single Line Text), `fsi_auditenabled` (Yes/No, Purview unified audit), `fsi_dataverseauditenabled` (Yes/No, Dataverse auditing), `fsi_lastchecked` (DateTime UTC, last compliance check), `fsi_compliancestatus` (Choice: Compliant=100000000, Non-Compliant=100000001, Remediation Pending=100000002, Error=100000003), `fsi_remediationdate` (DateTime, when remediation applied), `fsi_remediatedby` (Single Line Text), `fsi_errormessage` (Multi-line Text), `fsi_lasteventcaptured` (DateTime, most recent audit event). Key: upsert by fsi_environmentid.

- [ ] **DVS-02:** Create Dataverse schema creation script (Python) — create table definition JSON, create all columns with proper data types and option set values, create alternate key on fsi_environmentid for upsert support. Include seed data configuration documentation.

## DPL — Deployment & Automation

- [ ] **DPL-01:** Create deployment guide documentation — Phase 1: Azure Automation Account setup (FSI-AgentGov-Automation, PowerShell 7.2, System-Assigned MI enabled, same region as PP tenant), Phase 2: MI permissions (Entra ID roles: Power Platform Administrator + Exchange Administrator; Graph app permission: Mail.Send with admin consent; Dataverse Application User with System Administrator role in each target environment), Phase 3: Shared mailbox setup (powerplatform-governance@, SendAs permission for MI)

- [ ] **DPL-02:** Create deployment guide documentation — Phase 4: Module import (AuditComplianceHelpers.psm1 as .zip, gallery modules: Microsoft.PowerApps.Administration.PowerShell v2.0+, ExchangeOnlineManagement v3.0+, verify all Status=Available on Runtime 7.2), Phase 5: Runbook creation (Check-AuditLoggingCompliance + Enable-AuditLogging, both PowerShell type, Runtime 7.2, publish)

- [ ] **DPL-03:** Create scheduling documentation — Weekly-Audit-Compliance-Check schedule (Monday 6:00 AM ET, linked to detection runbook with configured parameters), optional Daily-Audit-Validation schedule, parameter configuration reference for both runbooks

## FLW — Approval Flow

- [ ] **FLW-01:** Create Power Automate approval flow specification — trigger: weekly recurrence after detection script, Step 1: HTTP GET non-compliant environments from Dataverse, Step 2: Condition check (count > 0), Step 3: Start approval (Approve/Reject, assigned to governance lead, includes environment list), Step 4: If approved trigger Enable-AuditLogging runbook via Azure Management API PUT, Step 5: Send completion notification

- [ ] **FLW-02:** Create flow template (JSON definition) or detailed configuration guide — include all HTTP action URIs, authentication patterns (Dataverse connection + Azure Management MI), approval card template, variable definitions (DataverseUrl, TenantDomain), error handling for failed runbook execution

## TST — Testing & Troubleshooting

- [ ] **TST-01:** Create testing scenarios documentation — 15 test scenarios: (1) all compliant, (2) mixed compliance, (3) Purview disabled, (4) event validation, (5-8) remediation scenarios (WhatIf, Dataverse enable, tenant Purview, validation failure), (9) retry/throttling, (10) multi-recipient email, (11-12) Dataverse upsert (create + update), (13-14) error handling (env-level + fatal auth), (15) scheduled execution. Each with setup, expected results, and verification steps.

- [ ] **TST-02:** Create troubleshooting guide — 10 issues: (1) Power Platform auth failure, (2) Exchange Online auth failure, (3) Dataverse 401 access denied, (4) email not sent, (5) Dataverse table not updated, (6) 429 throttling, (7) validation failure after remediation, (8) Search-UnifiedAuditLog not found, (9) CSV export path failure, (10) WhatIf not working. Each with symptoms, possible causes, step-by-step resolution.

## FRM — Framework Integration

- [ ] **FRM-01:** Add ALCA solution entry to `docs/reference/solutions-index.md` — summary table row (Audit Logging Compliance Automation, v1.0.0, Completed, description, Related Controls: 1.7), detail section with components (helper module, detection runbook, remediation runbook, Dataverse table, deployment guide, approval flow), regulatory alignment (FINRA 4511, SEC 17a-3/4, SOX 404, GLBA 501(b)), repository link, relationship note explaining ALCA vs ACV complementary scope

- [ ] **FRM-02:** Update Control 1.7 cross-references — add ALCA to implementation guides section or related solutions, update `mkdocs.yml` if new documentation pages are added, add cross-reference from ACV solution entry noting ALCA as complementary solution

- [ ] **FRM-03:** All validations pass — `mkdocs build --strict` zero errors/warnings, `python scripts/verify_controls.py` 71/71 controls valid, no broken internal links, navigation matches actual file structure

## Traceability Matrix

| Requirement | Spec Section | Controls | Regulatory |
|-------------|-------------|----------|------------|
| MOD-01, MOD-02, MOD-03 | Component 1: Helper Functions Module | 1.7 | All applicable |
| DET-01, DET-02, DET-03 | Component 2: Detection Script | 1.7 | FINRA 4511, SEC 17a-3/4, SOX 404, GLBA 501(b) |
| REM-01, REM-02, REM-03 | Component 3: Remediation Script | 1.7 | FINRA 4511, SEC 17a-3/4, SOX 404, GLBA 501(b) |
| DVS-01, DVS-02 | Dataverse Table Schema | 1.7 | SEC 17a-4 (audit trail), SOX 302 |
| DPL-01, DPL-02, DPL-03 | Deployment Guide (Phases 1-5) | 1.7 | All applicable |
| FLW-01, FLW-02 | Phase 6: Power Automate Integration | 1.7 | SOX 302 (approval controls) |
| TST-01, TST-02 | Testing Scenarios + Troubleshooting Guide | 1.7 | All applicable |
| FRM-01, FRM-02, FRM-03 | Repository Structure + Production Readiness | 1.7 | All applicable |

## Out of Scope

| Item | Reason |
|------|--------|
| Retention policy configuration | Explicitly excluded in spec — managed separately via Microsoft Purview |
| ACV replacement or modification | ALCA complements ACV, does not replace it |
| New control creation | Maps to existing Control 1.7; framework stays at 71 controls |
| Control count updates | No change to control, playbook, or pillar counts |
| Compliance Dashboard integration | Future enhancement — ACV already feeds Dashboard via v9 |
| SHA-256 evidence export | Covered by ACV; not duplicated in ALCA |
| RunId column for dashboard filtering | Optional enhancement — deferred as future todo |
| API change monitoring script | Optional enhancement — deferred as future todo |
| Batch Dataverse operations | Optional enhancement — deferred as future todo |

## Deferred Enhancements (Future Todos)

| Enhancement | Description | Effort |
|------------|-------------|--------|
| RunId column | Add `fsi_runid` GUID column to filter Power BI to latest run | 2-4 hours |
| API monitoring | `Test-AuditAPIAvailability.ps1` — monthly cmdlet/connectivity validation | 4-6 hours |
| Batch operations | `Write-DataverseComplianceRecordBatch` — reduce API calls for 100+ environments | 6-8 hours |

## Priority Summary

- **P1 (15):** MOD-01, MOD-02, DET-01, DET-02, DET-03, REM-01, REM-02, DVS-01, DVS-02, DPL-01, DPL-02, DPL-03, FRM-01, FRM-02, FRM-03
- **P2 (6):** MOD-03, REM-03, FLW-01, FLW-02, TST-01, TST-02

---
*Requirements defined: 2026-02-13*
*Milestone: v21 — Audit Logging Compliance Automation (ALCA)*
