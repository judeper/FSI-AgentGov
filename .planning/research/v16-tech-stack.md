# v16 Research: Technology Stack — Unrestricted Agent Sharing Detector

**Dimension:** Technology Stack
**Created:** 2026-02-12

## APIs

### Primary: BAP API (api.bap.microsoft.com)

| Endpoint | Purpose | Status |
|----------|---------|--------|
| `GET .../environments/{envId}/...` (enumerate agents) | List all agents/bots in target environment | Spec-defined |
| `GET .../environments/{envId}/...` (get principals) | Read per-agent sharing principals | Spec-defined |
| `PATCH .../environments/{envId}/...` (overwrite principals) | Remediate sharing by overwriting principals array | Spec-defined |

**Principal interpretation:**
- `type = Organization` → org-wide sharing
- `type = Group` → security group sharing
- `type = User` → individual sharing

**Authentication:** Entra service principal with Power Platform API permission (`8578e004-a5c6-46e7-913e-12f58912df43`). Lab-grade: interactive auth initially.

### Secondary: Dataverse OData (environment-specific)

- `GET [OrgUri]/api/data/v9.2/chatbots` — alternative agent enumeration
- Standard CRUD for governance tables

### Excluded: Microsoft Graph

- Graph is NOT used for sharing decisions (Non-Negotiable Rule #2)
- Optional use only for Teams-packaged agent discovery

## PowerShell Modules

| Module | Purpose |
|--------|---------|
| `Microsoft.PowerApps.Administration.PowerShell` | Environment queries, tenant settings |
| `Az.Accounts` | Azure authentication |
| PowerShell 7.0+ | Required version |

## Dataverse

- 5 custom tables with `fsi_` prefix
- Organization-owned for audit immutability
- Reuse `fsi_acv_zone` and `fsi_acv_severity` global option sets
- 5 solution-specific option sets (`fsi_UASD_*`)

## Power Automate

- 3 cloud flows: Detector, Remediation, Exception Approval
- Connection references: `fsi_cr_dataverse_sharingdetector`, `fsi_cr_teams_sharingdetector`
- Scope_Try/Scope_Catch error handling pattern

## Power Apps

- 1 Canvas App: Exception Manager
- Dataverse-connected for `fsi_SharingException`, `fsi_ApprovedSecurityGroup`

## Environment Variables

| Variable | Type | Default |
|----------|------|---------|
| `fsi_UASD_AutoRemediatePublicLink` | Boolean | false |
| `fsi_UASD_ScanFrequencyHours` | Integer | 24 |
| `fsi_UASD_HomeTenantId` | Text | (tenant-specific) |
| `fsi_UASD_DefaultExceptionDays` | Integer | 90 |

## Confidence: High

Stack is well-established in the framework. BAP API endpoints are spec-defined and must be used as-is.
