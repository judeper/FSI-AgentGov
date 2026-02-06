# Technology Stack - Audit Configuration Validator

**Project:** FSI Agent Governance Framework - Audit Configuration Validator Solution
**Research Date:** 2026-02-06
**Scope:** PowerShell modules, APIs, and tooling for automated audit configuration validation

---

## Executive Summary

This research identifies the specific PowerShell modules, API endpoints, and authentication patterns needed to build an automated audit configuration validator for the FSI Agent Governance Framework. The solution must validate audit logging across three surfaces: tenant-level unified audit (Exchange Online), per-environment audit (Power Platform), and audit retention policies (Purview Compliance).

**Key Finding:** All three audit surfaces support service principal authentication, but each requires different modules, permissions, and API approaches. No single module covers all three surfaces.

**Recommendation:** Use a multi-module approach with ExchangeOnlineManagement 3.9.2+, Microsoft.PowerApps.Administration.PowerShell 2.0.214+, and Dataverse Web API for environment-level audit configuration.

---

## Core Stack Requirements

### 1. Exchange Online PowerShell (Tenant-Level Unified Audit)

**Purpose:** Enable/disable unified audit logging at tenant level, verify audit status

| Component | Version | Why |
|-----------|---------|-----|
| **ExchangeOnlineManagement** | 3.9.2+ | Latest GA version with REST API support, no WinRM Basic Auth required |

**Installation:**
```powershell
Install-Module ExchangeOnlineManagement -MinimumVersion 3.9.2 -Scope CurrentUser
```

**Key Cmdlets:**

| Cmdlet | Purpose | Notes |
|--------|---------|-------|
| `Get-AdminAuditLogConfig` | Check unified audit status | Returns `UnifiedAuditLogIngestionEnabled` property |
| `Set-AdminAuditLogConfig` | Enable/disable unified audit | `-UnifiedAuditLogIngestionEnabled $true/$false` |
| `Search-UnifiedAuditLog` | Query audit log events | Used for evidence collection, not configuration |

**Service Principal Authentication:**
```powershell
Connect-ExchangeOnline -CertificateThumbprint "THUMBPRINT" `
  -AppId "APP-GUID" `
  -Organization "tenant.onmicrosoft.com"
```

**Required Permissions:**
- **Application Permission:** `Office 365 Exchange Online` > `Exchange.ManageAsApp`
- **Directory Role:** Compliance Management OR Organization Management role group
- **Audit Logs Role:** Required for Set-AdminAuditLogConfig (assigned via role groups above)

**Version 3.x Key Changes:**
- All cmdlets are REST API-backed (as of v3.0.0, September 2022)
- Remote PowerShell (RPS) protocol deprecated but available via `-UseRPSSession` switch
- Certificate-based authentication supported (v2.0.4+, enhanced in v3.x)
- PowerShell 7.4.0+ required for versions 3.5.0+ (due to .NET 8.0 dependencies)

**Rationale:**
- Version 3.9.2 (released January 5, 2026) is current stable release
- REST API removes WinRM dependency, critical for FSI automation scenarios
- Service principal authentication with certificates meets FSI audit requirements (no password secrets)
- `Get-AdminAuditLogConfig` and `Set-AdminAuditLogConfig` cmdlets unchanged in v3.x (verified via cmdlet documentation)

**Sources:**
- [PowerShell Gallery - ExchangeOnlineManagement 3.9.2](https://www.powershellgallery.com/packages/ExchangeOnlineManagement/3.9.2)
- [Microsoft Learn - About Exchange Online PowerShell V3](https://learn.microsoft.com/en-us/powershell/exchange/exchange-online-powershell-v2?view=exchange-ps)
- [Microsoft Learn - App-only authentication in Exchange Online PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2?view=exchange-ps)
- [Microsoft Learn - Turn auditing on or off](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable)

---

### 2. Security & Compliance PowerShell (Audit Retention Policies)

**Purpose:** Manage audit log retention policies (default 90 days, up to 10 years for Audit Premium)

| Component | Version | Why |
|-----------|---------|-----|
| **ExchangeOnlineManagement** | 3.9.2+ | Same module, different connection endpoint (Security & Compliance) |

**Installation:**
```powershell
# Same module as Exchange Online, different connection cmdlet
Install-Module ExchangeOnlineManagement -MinimumVersion 3.9.2 -Scope CurrentUser
```

**Key Cmdlets:**

| Cmdlet | Purpose | Notes |
|--------|---------|-------|
| `Get-UnifiedAuditLogRetentionPolicy` | View retention policies | Returns policy name, priority, retention duration, record types |
| `Set-UnifiedAuditLogRetentionPolicy` | Modify retention policy | Change `RetentionDuration` (values: ThreeMonths, SixMonths, NineMonths, TwelveMonths, TenYears) |
| `New-UnifiedAuditLogRetentionPolicy` | Create retention policy | Useful for record types not available in portal UI |
| `Remove-UnifiedAuditLogRetentionPolicy` | Delete retention policy | Cleanup for deprecated policies |

**Service Principal Authentication:**
```powershell
Connect-IPPSSession -CertificateThumbprint "THUMBPRINT" `
  -AppId "APP-GUID" `
  -Organization "tenant.onmicrosoft.com"
```

**Required Permissions:**
- **Application Permission:** `Office 365 Exchange Online` > `Exchange.ManageAsApp` (same as Exchange Online)
- **Role:** Organization Configuration role in Microsoft Purview portal
- **Note:** Certificate-based authentication for SCC PowerShell rolled out mid-February 2025 (GA)

**Retention Policy Capabilities:**
- Default retention: 90 days (180 days for E5/Audit Premium)
- Custom retention: Up to 10 years (requires Audit Premium license)
- Maximum policies: 50 per organization
- Granularity: Per record type (e.g., MicrosoftTeams, PowerPlatformAdminActivity, CopilotInteraction)

**FSI Validation Requirements:**
| Regulation | Minimum Retention | Recommended Policy |
|------------|-------------------|-------------------|
| FINRA 4511 | 3 years | `RetentionDuration TenYears` (covers all FSI regs) |
| SEC 17a-4 | 7 years | TenYears |
| SOX 302/404 | 7 years | TenYears |

**Rationale:**
- Audit retention is FSI-critical — default 90 days does NOT meet regulatory requirements
- Validator must check retention policies, alert if <3 years for key record types
- Auto-enablement workflow can create retention policy via `New-UnifiedAuditLogRetentionPolicy`
- Record types to prioritize: `CopilotInteraction`, `PowerPlatformAdminActivity`, `MicrosoftTeams`, `SharePointFileOperation`

**Sources:**
- [Microsoft Learn - Manage audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies)
- [Microsoft Learn - Get-UnifiedAuditLogRetentionPolicy](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-unifiedauditlogretentionpolicy?view=exchange-ps)
- [Microsoft Learn - Set-UnifiedAuditLogRetentionPolicy](https://learn.microsoft.com/en-us/powershell/module/exchange/set-unifiedauditlogretentionpolicy?view=exchange-ps)
- [Blog - Security & Compliance PowerShell Certificate Authentication](https://michev.info/blog/post/3796/connect-to-the-security-and-compliance-center-powershell-via-certificate-based-authentication)

---

### 3. Power Platform PowerShell (Environment Audit Settings)

**Purpose:** Validate per-environment audit enablement in Power Platform (Dataverse)

| Component | Version | Why |
|-----------|---------|-----|
| **Microsoft.PowerApps.Administration.PowerShell** | 2.0.214+ | Latest version with environment management capabilities |

**Installation:**
```powershell
Install-Module Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser
```

**Key Cmdlets:**

| Cmdlet | Purpose | Audit Relevance |
|--------|---------|----------------|
| `Get-AdminPowerAppEnvironment` | Retrieve environment metadata | Returns environment GUID, display name, type, region |
| `Get-AdminPowerAppEnvironmentLocations` | List available regions | Used for environment provisioning context |

**Service Principal Authentication:**
```powershell
Add-PowerAppsAccount -Endpoint prod `
  -TenantID $tenantId `
  -ApplicationId $appId `
  -ClientSecret $secret `
  -Verbose
```

**Required Setup:**
1. Register application in Entra ID
2. Register service principal with Power Platform:
   ```powershell
   New-PowerAppManagementApp -ApplicationId $appId
   ```
3. Create Application User in Dataverse environment
4. Assign System Administrator or System Customizer role to Application User

**Limitations:**
- `Get-AdminPowerAppEnvironment` does NOT return audit settings directly
- Audit configuration requires Dataverse Web API (see below)
- PowerShell module supports environment discovery only, not audit configuration

**Rationale:**
- Power Apps PowerShell module is environment discovery layer
- Audit settings live in Dataverse Organization table, not exposed via PowerShell cmdlets
- Version 2.0.214 is latest (verified via PowerShell Gallery)
- Service principal authentication supported for environment management operations

**Sources:**
- [PowerShell Gallery - Microsoft.PowerApps.Administration.PowerShell 2.0.214](https://www.powershellgallery.com/packages/Microsoft.PowerApps.Administration.PowerShell/2.0.214)
- [Microsoft Learn - Get started using Power Apps admin module](https://learn.microsoft.com/en-us/powershell/powerapps/get-started-powerapps-admin?view=pa-ps-latest)
- [Microsoft Learn - Creating a service principal with PowerShell](https://learn.microsoft.com/en-us/power-platform/admin/powershell-create-service-principal)
- [Microsoft Learn - Get-AdminPowerAppEnvironment](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminpowerappenvironment?view=pa-ps-latest)

---

### 4. Dataverse Web API (Environment Audit Configuration)

**Purpose:** Check and configure audit settings for Power Platform environments programmatically

| Component | Version | Why |
|-----------|---------|-----|
| **Dataverse Web API** | v9.2 | Current stable version for organization settings management |

**Authentication:**
- OAuth 2.0 client credentials flow via Microsoft Entra ID
- Service principal with client secret or certificate
- Requires Application User created in target Dataverse environment

**Key Endpoints:**

#### Retrieve Environment Audit Settings
```http
GET [Organization URI]/api/data/v9.2/organizations?$select=auditsettings,isauditenabled,auditretentionperiodv2,isuseraccessauditenabled,useraccessauditinginterval HTTP/1.1
Accept: application/json
OData-MaxVersion: 4.0
OData-Version: 4.0
Authorization: Bearer {token}
```

**Response:**
```json
{
    "@odata.context": "[Organization URI]/api/data/v9.2/$metadata#organizations(...)",
    "value": [
        {
            "@odata.etag": "W/\"67404512\"",
            "auditsettings": "{\"IsSqlAuditWriteDisabled\":true}",
            "isauditenabled": true,
            "auditretentionperiodv2": 30,
            "isuseraccessauditenabled": true,
            "useraccessauditinginterval": 4,
            "organizationid": "<organizationid value>"
        }
    ]
}
```

#### Enable Environment Auditing
```http
PATCH [Organization URI]/api/data/v9.2/organizations([Organization ID]) HTTP/1.1
Content-Type: application/json
OData-MaxVersion: 4.0
OData-Version: 4.0
If-Match: *
Authorization: Bearer {token}

{
   "isauditenabled": true,
   "auditretentionperiodv2": 30
}
```

#### Query Tables Enabled for Auditing
```http
GET [Organization URI]/api/data/v9.2/EntityDefinitions?$select=LogicalName,IsAuditEnabled&$filter=IsAuditEnabled/Value eq true and IsPrivate eq false HTTP/1.1
Accept: application/json
OData-MaxVersion: 4.0
OData-Version: 4.0
Authorization: Bearer {token}
```

**Organization Table Properties:**

| Property | Type | Purpose |
|----------|------|---------|
| `isauditenabled` | Boolean | Master switch for environment auditing |
| `auditretentionperiodv2` | Integer | Retention period in days (default 30, max varies by license) |
| `isuseraccessauditenabled` | Boolean | Track user sign-ins |
| `useraccessauditinginterval` | Integer | Interval for user access logging (4 = every 4 hours) |
| `auditsettings` | String (JSON) | Advanced settings (e.g., `IsSqlAuditWriteDisabled`, `StoreLabelNameforPicklistAudits`) |

**OAuth Token Acquisition (PowerShell Example):**
```powershell
# Using MSAL.PS module
Install-Module MSAL.PS -Scope CurrentUser

$tokenParams = @{
    ClientId     = $appId
    ClientSecret = (ConvertTo-SecureString $clientSecret -AsPlainText -Force)
    TenantId     = $tenantId
    Scopes       = @("$organizationUri/.default")
}
$token = Get-MsalToken @tokenParams

$headers = @{
    "Authorization" = "Bearer $($token.AccessToken)"
    "OData-MaxVersion" = "4.0"
    "OData-Version" = "4.0"
    "Accept" = "application/json"
}

$response = Invoke-RestMethod -Uri "$organizationUri/api/data/v9.2/organizations?`$select=isauditenabled" -Headers $headers -Method Get
```

**Required Permissions:**
- **Dataverse:** Application User with System Administrator or System Customizer role
- **Entra ID:** Application registered with client secret or certificate
- **No Graph API permissions required** (Dataverse uses its own resource endpoint)

**FSI Validation Checks:**
1. `isauditenabled` = true (CRITICAL)
2. `auditretentionperiodv2` >= 1095 days (3 years minimum for FINRA 4511)
3. `isuseraccessauditenabled` = true (recommended for SOX 302 compliance)

**Rationale:**
- Dataverse Web API is the ONLY programmatic way to check/configure environment audit settings
- PowerShell module does not expose audit configuration cmdlets
- REST API approach consistent with existing FSI-AgentGov-Solutions patterns (deny-event-correlation-report uses REST APIs)
- Service principal authentication supports unattended automation
- Organization table is standard Dataverse schema, stable across versions

**Sources:**
- [Microsoft Learn - Configure auditing (Dataverse)](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/auditing/configure)
- [Microsoft Learn - Manage Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing)
- [Microsoft Learn - Use OAuth authentication with Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth)
- [GitHub - Dataverse Audit Management PowerShell](https://github.com/jenschristianschroder/Dataverse-Audit-Management)

---

## Microsoft Graph API (Audit Log Query - Optional)

**Purpose:** Query Entra ID audit logs (directory audits, sign-ins) for evidence collection

| Component | Version | Why |
|-----------|---------|-----|
| **Microsoft.Graph PowerShell SDK** | 2.x | Unified Graph SDK for Entra ID audit logs |

**Installation:**
```powershell
Install-Module Microsoft.Graph -Scope CurrentUser
```

**Key Endpoints:**

| Endpoint | Purpose | Notes |
|----------|---------|-------|
| `/v1.0/auditLogs/directoryAudits` | Entra ID directory changes | Admin role assignments, app registrations |
| `/v1.0/auditLogs/signIns` | User sign-in logs | Authentication events, MFA prompts |
| `/beta/security/auditLog/queries` | Unified Audit Log query | Alternative to Search-UnifiedAuditLog (preview) |

**Service Principal Authentication:**
```powershell
Connect-MgGraph -ClientId $appId `
  -TenantId $tenantId `
  -CertificateThumbprint $thumbprint
```

**Required Permissions:**
- **Application Permission:** `AuditLog.Read.All` (Microsoft Graph)
- **Admin consent required:** Yes

**Use Case in Audit Configuration Validator:**
- Evidence collection for compliance reports
- Track changes to audit configuration (who enabled/disabled auditing)
- NOT required for audit configuration validation itself
- OPTIONAL: Include for comprehensive compliance evidence

**Rationale:**
- Graph API provides Entra ID audit context (e.g., "Who granted System Administrator role to the service principal?")
- Complements Exchange/Dataverse audit logs
- `AuditLog.Read.All` is read-only, safe for automation scenarios
- NOT a blocker for MVP — can be added in v2 for enhanced compliance reporting

**Sources:**
- [Microsoft Learn - Microsoft Entra audit logs API overview](https://learn.microsoft.com/en-us/graph/api/resources/azure-ad-auditlog-overview?view=graph-rest-1.0)
- [Microsoft Learn - AuditLog.Read.All permission](https://graphpermissions.merill.net/permission/AuditLog.Read.All)
- [Blog - Querying the Unified Audit Log via Graph API](https://michev.info/blog/post/6001/querying-the-microsoft-365-unified-audit-log-datamart-via-the-graph-api)

---

## Supporting Libraries

### MSAL.PS (OAuth Token Acquisition)

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| **MSAL.PS** | 4.x | Acquire OAuth tokens for Dataverse Web API | Simplifies service principal authentication |

**Installation:**
```powershell
Install-Module MSAL.PS -Scope CurrentUser
```

**Usage:**
```powershell
$token = Get-MsalToken -ClientId $appId `
  -ClientSecret (ConvertTo-SecureString $secret -AsPlainText -Force) `
  -TenantId $tenantId `
  -Scopes @("https://contoso.crm.dynamics.com/.default")
```

**Rationale:**
- Dataverse Web API requires OAuth token via client credentials flow
- MSAL.PS is Microsoft-supported library for token acquisition
- Alternative: Use `Invoke-RestMethod` to call Entra ID token endpoint directly (more verbose)
- MSAL.PS handles token caching, simplifies retry logic

**Sources:**
- [PowerShell Gallery - MSAL.PS](https://www.powershellgallery.com/packages/MSAL.PS)

---

## Authentication Architecture

### Service Principal Setup

**Required Azure Resources:**

1. **Entra ID App Registration**
   - Client ID (Application ID)
   - Client secret OR certificate (FSI: certificate preferred)
   - Tenant ID

2. **Certificate-Based Authentication (FSI Recommended):**
```powershell
# Generate self-signed certificate (1-year validity)
$cert = New-SelfSignedCertificate -Subject "CN=FSI-AuditValidator" `
  -CertStoreLocation "Cert:\CurrentUser\My" `
  -NotAfter (Get-Date).AddYears(1) `
  -KeySpec KeyExchange

# Export certificate (upload .cer to Entra ID app registration)
$certPath = "C:\Certs\FSI-AuditValidator.cer"
Export-Certificate -Cert $cert -FilePath $certPath

# Get thumbprint for authentication
$thumbprint = $cert.Thumbprint
```

3. **Application Permissions:**

| Service | Permission | Type | Why |
|---------|------------|------|-----|
| Office 365 Exchange Online | `Exchange.ManageAsApp` | Application | Manage unified audit logging |
| Microsoft Graph (optional) | `AuditLog.Read.All` | Application | Query Entra ID audit logs |

4. **Dataverse Application User:**
```powershell
# Register service principal with Power Platform
Add-PowerAppsAccount -TenantID $tenantId `
  -ApplicationId $appId `
  -ClientSecret $secret

New-PowerAppManagementApp -ApplicationId $appId

# Then create Application User in each environment via UI:
# Settings > Security > Users > app users > + New app user
# Assign: System Administrator OR System Customizer role
```

**FSI Security Requirements:**
- **Certificate over secret:** Audit trail in Azure Key Vault for secret access, but certificate rotation simpler
- **Certificate rotation:** 90-day maximum (automate via Key Vault or Entra ID policies)
- **Least privilege:** Use System Customizer role if possible (read/write audit settings, not full admin)
- **Key Vault integration:** Store certificate thumbprint and tenant ID in Key Vault, NOT in scripts

**Sources:**
- [Microsoft Learn - App-only authentication for Exchange Online](https://learn.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2?view=exchange-ps)
- [Microsoft Learn - Creating a service principal for Power Platform](https://learn.microsoft.com/en-us/power-platform/admin/powershell-create-service-principal)

---

## What NOT to Add

### Deferred or Excluded Technologies

| Technology | Why Excluded |
|------------|--------------|
| **PnP.PowerShell** | SharePoint-focused, no audit configuration capabilities for Exchange/Purview |
| **Microsoft365DSC** | Desired State Configuration framework overkill for targeted validator solution |
| **Azure Monitor REST API** | For monitoring audit log ingestion pipeline health, not configuration validation (future v2 feature) |
| **Power Platform Admin API (REST)** | Environment metadata only, does not expose audit settings (use Dataverse Web API instead) |
| **ExchangeOnlineManagement v2.x** | Deprecated, v3.x is GA since September 2022 |
| **Security & Compliance PowerShell (separate module)** | No longer exists as standalone module, integrated into ExchangeOnlineManagement v3.x |

**Anti-Patterns to Avoid:**
- **Do NOT** use basic authentication (deprecated since September 2022)
- **Do NOT** use client secrets with >90-day expiration in FSI environments
- **Do NOT** mix PowerShell remoting (RPS) with REST API cmdlets (stick to REST for consistency)
- **Do NOT** assume `Get-AdminPowerAppEnvironment` returns audit settings (it does not)

---

## Integration with Existing Stack

### FSI-AgentGov-Solutions Existing Patterns

**Current Modules in Use (from existing scripts):**
- `Microsoft.PowerApps.Administration.PowerShell` (environment-lifecycle-management, deny-event-correlation-report)
- `Microsoft.Graph` (deny-event-correlation-report, scope-drift-monitor)
- `ExchangeOnlineManagement` (NOT yet used in existing solutions)

**Consistency Patterns:**
```powershell
# Existing pattern from deny-event-correlation-report/scripts/Export-CopilotDenyEvents.ps1
#Requires -Version 7.0
# No #Requires for modules (they check/install dynamically)

# New pattern for audit-configuration-validator:
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.9.2" }
#Requires -Modules @{ ModuleName="Microsoft.PowerApps.Administration.PowerShell"; ModuleVersion="2.0.214" }
```

**Error Handling Pattern:**
```powershell
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

try {
    # Script logic
} catch {
    Write-Error "Audit validation failed: $_"
    throw  # Propagate for Power Automate flow failure detection
}
```

**Secret Management Pattern (from existing STACK.md v2):**
```powershell
# Use Azure Key Vault via SecretManagement module
$credential = Get-Secret -Name "AuditValidatorServicePrincipal" `
  -Vault "FSIAgentGov" `
  -AsPlainText
```

---

## Installation Instructions

### Prerequisites
- PowerShell 7.4.0+ (required for ExchangeOnlineManagement 3.5.0+)
- Windows, macOS, or Linux
- Entra ID tenant admin access (for app registration)
- Power Platform admin access (for Application User creation)

### Full Setup Script

```powershell
# 1. Install PowerShell modules
Install-Module ExchangeOnlineManagement -MinimumVersion 3.9.2 -Scope CurrentUser -Force
Install-Module Microsoft.PowerApps.Administration.PowerShell -MinimumVersion 2.0.214 -Scope CurrentUser -Force
Install-Module MSAL.PS -Scope CurrentUser -Force
Install-Module Microsoft.Graph -Scope CurrentUser -Force  # Optional

# 2. Verify installations
Get-Module -ListAvailable ExchangeOnlineManagement
Get-Module -ListAvailable Microsoft.PowerApps.Administration.PowerShell

# 3. Generate service principal certificate
$cert = New-SelfSignedCertificate -Subject "CN=FSI-AuditValidator" `
  -CertStoreLocation "Cert:\CurrentUser\My" `
  -NotAfter (Get-Date).AddYears(1) `
  -KeySpec KeyExchange

# 4. Export certificate for Entra ID upload
$certPath = "$env:TEMP\FSI-AuditValidator.cer"
Export-Certificate -Cert $cert -FilePath $certPath
Write-Host "Upload certificate to Entra ID: $certPath"
Write-Host "Certificate thumbprint: $($cert.Thumbprint)"

# 5. Test Exchange Online connection
Connect-ExchangeOnline -CertificateThumbprint $cert.Thumbprint `
  -AppId "YOUR-APP-ID" `
  -Organization "tenant.onmicrosoft.com"

Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled

# 6. Test Security & Compliance connection
Connect-IPPSSession -CertificateThumbprint $cert.Thumbprint `
  -AppId "YOUR-APP-ID" `
  -Organization "tenant.onmicrosoft.com"

Get-UnifiedAuditLogRetentionPolicy

# 7. Test Power Platform connection
Add-PowerAppsAccount -TenantID "YOUR-TENANT-ID" `
  -ApplicationId "YOUR-APP-ID" `
  -ClientSecret "YOUR-CLIENT-SECRET"

Get-AdminPowerAppEnvironment | Select-Object DisplayName, EnvironmentName

# 8. Register service principal with Power Platform
New-PowerAppManagementApp -ApplicationId "YOUR-APP-ID"

# 9. Test Dataverse Web API connection
$token = Get-MsalToken -ClientId "YOUR-APP-ID" `
  -ClientSecret (ConvertTo-SecureString "YOUR-SECRET" -AsPlainText -Force) `
  -TenantId "YOUR-TENANT-ID" `
  -Scopes @("https://YOUR-ORG.crm.dynamics.com/.default")

$headers = @{
    "Authorization" = "Bearer $($token.AccessToken)"
    "OData-MaxVersion" = "4.0"
    "OData-Version" = "4.0"
    "Accept" = "application/json"
}

$orgUri = "https://YOUR-ORG.crm.dynamics.com"
$response = Invoke-RestMethod -Uri "$orgUri/api/data/v9.2/organizations?`$select=isauditenabled" -Headers $headers -Method Get
$response.value | Format-List isauditenabled
```

---

## Version Pinning Recommendations

| Package | Minimum Version | Maximum Version | Rationale |
|---------|-----------------|-----------------|-----------|
| ExchangeOnlineManagement | 3.9.2 | 3.x | Pin to v3.x line, allow minor updates for security patches |
| Microsoft.PowerApps.Administration.PowerShell | 2.0.214 | 2.x | Current stable, allow minor updates |
| MSAL.PS | 4.0 | 4.x | Stable OAuth library, semantic versioning |
| Microsoft.Graph | 2.0 | 2.x | Optional dependency, stable v2.x line |

**Pin Strategy:**
- Use `-MinimumVersion` in `#Requires` statements for fail-fast validation
- Allow minor updates (e.g., 3.9.2 → 3.9.3) for security patches
- Test major version updates in non-production before adopting
- Review release notes for breaking changes in ExchangeOnlineManagement v4.x (when released)

---

## Security Considerations

### Certificate Management (FSI Requirements)

**Certificate Lifecycle:**
1. **Generation:** Self-signed OR CA-issued (FSI: CA-issued preferred for production)
2. **Storage:** Certificate private key in Windows Certificate Store OR Azure Key Vault
3. **Rotation:** Maximum 90-day validity for FSI environments
4. **Audit:** Certificate usage logged via Entra ID sign-in logs (Application sign-ins)

**Automated Rotation Pattern:**
```powershell
# Check certificate expiration
$cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq "CN=FSI-AuditValidator" }
$daysUntilExpiration = ($cert.NotAfter - (Get-Date)).Days

if ($daysUntilExpiration -lt 30) {
    Write-Warning "Certificate expires in $daysUntilExpiration days. Rotate immediately."
    # Trigger automated rotation workflow via Power Automate
}
```

### Least Privilege Access

**Exchange Online:**
- **Role Group:** Compliance Management (NOT Organization Management)
- **Justification:** Read/write audit configuration, no mailbox access

**Power Platform:**
- **Dataverse Role:** System Customizer (NOT System Administrator)
- **Justification:** Modify organization settings, no user impersonation or environment deletion

**Entra ID:**
- **Directory Role:** None required (permissions granted via app registration API permissions)
- **Application Permissions:** Exchange.ManageAsApp, AuditLog.Read.All (read-only Graph)

### Audit Trail Requirements

**FSI Compliance:**
- **Certificate access:** Azure Key Vault access logs → Log Analytics → 7-year retention
- **Script execution:** Power Automate flow run history → Dataverse → custom retention policy
- **Audit configuration changes:** Unified Audit Log → `Set-AdminAuditLogConfig` operation → 10-year retention
- **Service principal sign-ins:** Entra ID sign-in logs → 90-day default (export to SIEM for long-term retention)

---

## API Rate Limits and Throttling

### Exchange Online Management

| Operation | Limit | Notes |
|-----------|-------|-------|
| `Get-AdminAuditLogConfig` | 10,000 requests/day | Per app ID |
| `Set-AdminAuditLogConfig` | 500 requests/day | Per app ID |
| `Search-UnifiedAuditLog` | 10 requests/second | Burst limit |

**Mitigation:**
- Validator runs daily (not hourly), well within limits
- Implement retry logic with exponential backoff

### Dataverse Web API

| Operation | Limit | Notes |
|-----------|-------|-------|
| API requests | 6,000 requests/5 minutes | Per user/app |
| Concurrent requests | 52 | Per organization |

**Mitigation:**
- Validator queries one environment at a time (sequential, not parallel)
- Batch GET requests where possible (e.g., query all environments in single request)

### Microsoft Graph API

| Operation | Limit | Notes |
|-----------|-------|-------|
| `auditLogs/directoryAudits` | 1,800 requests/minute | Per app |
| `auditLogs/signIns` | 1,800 requests/minute | Per app |

**Mitigation:**
- Graph API is optional for MVP
- If implemented, limit to daily batch queries (not real-time)

**Sources:**
- [Microsoft Learn - Exchange Online throttling](https://learn.microsoft.com/en-us/office365/servicedescriptions/exchange-online-service-description/exchange-online-limits)
- [Microsoft Learn - Dataverse API limits](https://learn.microsoft.com/en-us/power-platform/admin/api-request-limits-allocations)
- [Microsoft Learn - Graph API throttling](https://learn.microsoft.com/en-us/graph/throttling)

---

## Confidence Assessment

| Area | Confidence | Source Quality | Notes |
|------|------------|----------------|-------|
| ExchangeOnlineManagement v3.9.2 | **HIGH** | PowerShell Gallery, Microsoft Learn | Version verified on PSGallery (1/5/2026), cmdlet docs current |
| Service principal auth (Exchange) | **HIGH** | Microsoft Learn official docs | Certificate-based auth GA since v2.0.4, enhanced in v3.x |
| Audit retention cmdlets | **HIGH** | Microsoft Learn official docs | Cmdlet syntax verified, FSI retention requirements validated |
| Power Platform PowerShell | **MEDIUM** | PowerShell Gallery, Microsoft Learn | Version 2.0.214 verified, but audit settings NOT exposed via cmdlets |
| Dataverse Web API audit endpoints | **HIGH** | Microsoft Learn official docs | Endpoint syntax verified with examples, Organization table schema documented |
| Service principal auth (Dataverse) | **HIGH** | Microsoft Learn, community examples | OAuth client credentials flow standard, Application User pattern documented |
| Graph API audit endpoints | **HIGH** | Microsoft Learn official docs | Optional for MVP, but well-documented if needed |

**Overall Confidence: HIGH** — All core components verified with official Microsoft documentation and version numbers confirmed via PowerShell Gallery. Dataverse Web API is only path for environment audit configuration (no PowerShell cmdlet alternative exists).

**Key Uncertainty:**
- **Power Platform PowerShell module roadmap:** Will Microsoft add `Set-AdminPowerAppEnvironmentAudit` cmdlet in future versions? Currently NOT on public roadmap. Dataverse Web API remains canonical approach.

---

## Open Questions / Validation Needed

1. **ExchangeOnlineManagement v4.x:** When will v4.x release? Check for breaking changes to audit cmdlets before upgrading.

2. **Dataverse Application User permissions:** Can System Customizer role modify `Organization.isauditenabled`, or is System Administrator required? TEST in non-production environment.

3. **Audit retention policy priority:** If multiple policies conflict (e.g., default 90 days vs custom 10 years for CopilotInteraction), which wins? VERIFY via `Get-UnifiedAuditLogRetentionPolicy | Sort-Object Priority`.

4. **Certificate rotation automation:** Does Azure Key Vault managed certificates work with `Connect-ExchangeOnline -CertificateThumbprint`? TEST certificate stored in Key Vault vs local certificate store.

5. **Dataverse audit settings propagation delay:** After PATCH to `organizations` endpoint to enable auditing, how long until audit logs start appearing? MEASURE in test environment.

---

## Appendix: PowerShell Module Comparison

### ExchangeOnlineManagement vs PnP.PowerShell

| Feature | ExchangeOnlineManagement | PnP.PowerShell | Winner for Audit Validator |
|---------|--------------------------|----------------|---------------------------|
| Unified audit logging | `Get-AdminAuditLogConfig`, `Set-AdminAuditLogConfig` | NOT AVAILABLE | **ExchangeOnlineManagement** |
| Audit retention policies | `Get-UnifiedAuditLogRetentionPolicy`, `Set-UnifiedAuditLogRetentionPolicy` | NOT AVAILABLE | **ExchangeOnlineManagement** |
| Service principal auth | Certificate-based auth supported | Certificate or client secret | Tie (both support) |
| REST API-backed | Yes (v3.0.0+) | Yes | Tie |
| Focus | Exchange Online, Security & Compliance | SharePoint Online, PnP features | **ExchangeOnlineManagement** for audit |

**Verdict:** ExchangeOnlineManagement is the ONLY module with audit configuration cmdlets. PnP.PowerShell is irrelevant for this solution.

---

## Sources

**Exchange Online PowerShell:**
- [PowerShell Gallery - ExchangeOnlineManagement 3.9.2](https://www.powershellgallery.com/packages/ExchangeOnlineManagement/3.9.2)
- [Microsoft Learn - About Exchange Online PowerShell V3](https://learn.microsoft.com/en-us/powershell/exchange/exchange-online-powershell-v2?view=exchange-ps)
- [Microsoft Learn - What's new in ExchangeOnlineManagement](https://learn.microsoft.com/en-us/powershell/exchange/whats-new-in-the-exo-module?view=exchange-ps)
- [Microsoft Learn - App-only authentication in Exchange Online PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2?view=exchange-ps)
- [Microsoft Learn - Turn auditing on or off](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable)
- [Microsoft Learn - Set-AdminAuditLogConfig](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/set-adminauditlogconfig?view=exchange-ps)

**Audit Retention Policies:**
- [Microsoft Learn - Manage audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies)
- [Microsoft Learn - Get-UnifiedAuditLogRetentionPolicy](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-unifiedauditlogretentionpolicy?view=exchange-ps)
- [Microsoft Learn - Set-UnifiedAuditLogRetentionPolicy](https://learn.microsoft.com/en-us/powershell/module/exchange/set-unifiedauditlogretentionpolicy?view=exchange-ps)

**Power Platform PowerShell:**
- [PowerShell Gallery - Microsoft.PowerApps.Administration.PowerShell 2.0.214](https://www.powershellgallery.com/packages/Microsoft.PowerApps.Administration.PowerShell/2.0.214)
- [Microsoft Learn - Get started using Power Apps admin module](https://learn.microsoft.com/en-us/powershell/powerapps/get-started-powerapps-admin?view=pa-ps-latest)
- [Microsoft Learn - Creating a service principal with PowerShell](https://learn.microsoft.com/en-us/power-platform/admin/powershell-create-service-principal)
- [Microsoft Learn - Get-AdminPowerAppEnvironment](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/get-adminpowerappenvironment?view=pa-ps-latest)

**Dataverse Web API:**
- [Microsoft Learn - Configure auditing (Dataverse)](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/auditing/configure)
- [Microsoft Learn - Manage Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing)
- [Microsoft Learn - Use OAuth authentication with Dataverse](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth)
- [Microsoft Learn - Organization table reference](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/reference/entities/organization)

**Microsoft Graph API:**
- [Microsoft Learn - Microsoft Entra audit logs API overview](https://learn.microsoft.com/en-us/graph/api/resources/azure-ad-auditlog-overview?view=graph-rest-1.0)
- [Graph Permissions - AuditLog.Read.All](https://graphpermissions.merill.net/permission/AuditLog.Read.All)
- [Microsoft Learn - Microsoft Graph permissions reference](https://learn.microsoft.com/en-us/graph/permissions-reference)

**Community Resources:**
- [Blog - Certificate-based authentication for SCC PowerShell (Vasil Michev)](https://michev.info/blog/post/3796/connect-to-the-security-and-compliance-center-powershell-via-certificate-based-authentication)
- [Blog - Querying Unified Audit Log via Graph API (Vasil Michev)](https://michev.info/blog/post/6001/querying-the-microsoft-365-unified-audit-log-datamart-via-the-graph-api)
- [GitHub - Dataverse Audit Management PowerShell](https://github.com/jenschristianschroder/Dataverse-Audit-Management)

---

## Appendix: Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-06 | Initial research for Audit Configuration Validator solution |
