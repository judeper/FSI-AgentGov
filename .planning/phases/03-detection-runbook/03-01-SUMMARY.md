# Phase 3 Plan A Summary: Detection Runbook Core

**Phase:** 3 — Detection Runbook
**Plan:** 03-01 (A)
**Executed:** 2026-02-13
**Result:** PASS

## Dependency Graph

```
03-01-PLAN.md → 01-01-PLAN.md (imports AuditComplianceHelpers module)
```

## Tech Stack

- PowerShell 7.2+
- Microsoft.PowerApps.Administration.PowerShell 2.0+
- ExchangeOnlineManagement 3.0+
- Azure Automation System-Assigned Managed Identity
- Dataverse Web API v9.2
- Exchange Online Search-UnifiedAuditLog

## Key Files Created

| File | Purpose |
|------|---------|
| `audit-logging-compliance-automation/src/Check-AuditLoggingCompliance.ps1` | Detection runbook (446 lines) |

## Implementation Details

- **Parameters:** DataverseEnvironmentUrl (mandatory), TenantDomain (mandatory), NotificationFromAddress (optional), NotificationToAddresses (optional, comma-separated), SendEmail (switch)
- **Auth flow:** MI token → Power Platform (Add-PowerAppsAccount), Exchange Online (Connect-ExchangeOnline -ManagedIdentity), Dataverse (Get-DataverseToken)
- **Scanning:** Get-AdminPowerAppEnvironment → per-env: Purview check (Get-AdminConfig), Dataverse check (Web API), event validation (Search-UnifiedAuditLog, 7-day window)
- **Compliance logic:** Dataverse envs require BOTH Purview + Dataverse audit; non-Dataverse require Purview only
- **Dataverse write:** Write-DataverseComplianceRecord upsert per environment

## Commits

| Hash | Message |
|------|---------|
| `02f3d65` | feat(alca): add detection runbook Check-AuditLoggingCompliance.ps1 (Phase 3) |

## Self-Check

- [x] File created at correct path
- [x] All 5 parameters present with correct types
- [x] MI auth (never interactive/hardcoded)
- [x] Environment enumeration implemented
- [x] Purview + Dataverse audit checks implemented
- [x] Compliance determination logic correct
- [x] Write-DataverseComplianceRecord called per environment
