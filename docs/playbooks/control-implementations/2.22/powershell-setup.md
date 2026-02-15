# PowerShell Setup: Control 2.22 - Inactivity Timeout Enforcement

> **Parent Control:** [2.22 - Inactivity Timeout Enforcement](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md)

**Last Updated:** February 2026
**Module Requirements:** Az.Accounts (for service principal auth), Invoke-RestMethod (built-in)
**Estimated Time:** 30 minutes for setup; 5 minutes per remediation run

## Prerequisites

- [ ] PowerShell 7.x or later installed
- [ ] Az.Accounts module installed (`Install-Module Az.Accounts`)
- [ ] Authenticated session via `Connect-AzAccount` (service principal or interactive)
- [ ] Service principal with Power Platform Admin role or delegated environment admin
- [ ] App registration with `https://api.bap.microsoft.com/.default` scope granted (for service principal auth)
- [ ] Environment names (EnvironmentName, not display name) identified for remediation

---

## Script: Set-InactivityTimeout.ps1

### Synopsis

Configures the inactivity timeout duration for a Power Platform environment via the BAP Admin API privacy settings endpoint. Uses a GET-PATCH-GET pattern to read current state, apply changes, and verify. Supports `-WhatIf` for preview mode, optional Dataverse audit record writing, and evidence packaging with SHA-256 integrity hashing.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `-EnvironmentName` | String | Yes | — | Power Platform Environment Name (canonical GUID, not display name) |
| `-TimeoutDuration` | Int32 | No | 120 | Inactivity timeout duration in minutes (valid range: 5-120) |
| `-WarningDuration` | Int32 | No | 5 | Warning notification duration in minutes before timeout (valid range: 1-30) |
| `-DataverseUrl` | String | No | — | Dataverse environment URL for writing remediation audit records (e.g., `https://org12345.crm.dynamics.com/`) |
| `-OutputFormat` | String | No | Object | Output format: `Table`, `JSON`, or `Object` |
| `-OutputPath` | String | No | — | File path to export JSON results |
| `-IncludeEvidence` | Switch | No | — | Computes SHA-256 integrity hash over results for evidence packaging |
| `-WhatIf` | Switch | No | — | Preview mode — displays current vs. target configuration without making changes |
| `-Verbose` | Switch | No | — | Detailed output including API request/response details |

!!! note "Authentication"
    The script requires an authenticated Azure session via `Connect-AzAccount` before execution. It obtains BAP API tokens automatically using `Get-AzAccessToken`. No `-ClientId`, `-TenantId`, or `-ClientSecret` parameters are needed — authentication is handled by the pre-existing session.

### Example Commands

#### Preview changes (WhatIf mode)

```powershell
# Authenticate first (one-time per session)
Connect-AzAccount -ServicePrincipal `
    -ApplicationId $clientId `
    -CertificateThumbprint $thumbprint `
    -TenantId $tenantId

# Preview what would change
.\Set-InactivityTimeout.ps1 `
    -EnvironmentName "d1234567-abcd-ef01-2345-6789abcdef01" `
    -TimeoutDuration 60 `
    -WhatIf
```

**Expected output:**
```
What if: Performing the operation "Set inactivity timeout to 60 min with 5 min warning" on target "d1234567-abcd-ef01-2345-6789abcdef01".
```

#### Apply remediation to a single environment (Zone 3)

```powershell
.\Set-InactivityTimeout.ps1 `
    -EnvironmentName "d1234567-abcd-ef01-2345-6789abcdef01" `
    -TimeoutDuration 60 `
    -WarningDuration 10 `
    -Verbose
```

#### Apply remediation with Dataverse audit record

```powershell
.\Set-InactivityTimeout.ps1 `
    -EnvironmentName "d1234567-abcd-ef01-2345-6789abcdef01" `
    -TimeoutDuration 60 `
    -DataverseUrl "https://org12345.crm.dynamics.com/" `
    -IncludeEvidence `
    -OutputFormat JSON `
    -OutputPath .\evidence\timeout-remediation.json
```

#### Bulk remediation from CSV

```powershell
# CSV format: EnvironmentName,TimeoutDuration
# d1234567-abcd-ef01-2345-6789abcdef01,60
# e2345678-bcde-f012-3456-789abcdef012,120

Import-Csv ".\non-compliant-environments.csv" | ForEach-Object {
    .\Set-InactivityTimeout.ps1 `
        -EnvironmentName $_.EnvironmentName `
        -TimeoutDuration $_.TimeoutDuration
}
```

#### Bulk remediation with WhatIf preview

```powershell
Import-Csv ".\non-compliant-environments.csv" | ForEach-Object {
    .\Set-InactivityTimeout.ps1 `
        -EnvironmentName $_.EnvironmentName `
        -TimeoutDuration $_.TimeoutDuration `
        -WhatIf
}
```

---

## API Reference

### GET — Retrieve Current Privacy Settings

```
GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01

Authorization: Bearer {access_token}
```

**Response (example):**
```json
{
  "properties": {
    "InactivityTimeoutEnabled": true,
    "InactivityTimeoutInMinutes": 120,
    "InactivityWarningInMinutes": 10
  }
}
```

### PATCH — Update Privacy Settings

```
PATCH https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01

Authorization: Bearer {access_token}
Content-Type: application/json

{
  "properties": {
    "InactivityTimeoutEnabled": true,
    "InactivityTimeoutInMinutes": 60,
    "InactivityWarningInMinutes": 5
  }
}
```

---

## Authentication Setup

### Service Principal Configuration

1. Register an application in Azure AD (Entra ID)
2. Grant the application the **Power Platform Admin** role, or assign **Environment Admin** per environment
3. Add the API permission scope: `https://api.bap.microsoft.com/.default`
4. Grant admin consent for the API permission
5. Create a client secret or upload a certificate for authentication

### Authenticating Before Running the Script

The script uses `Get-AzAccessToken` internally to obtain BAP API tokens. You must authenticate via `Connect-AzAccount` before running the script:

```powershell
# Option 1: Service principal with certificate (recommended for automation)
Connect-AzAccount -ServicePrincipal `
    -ApplicationId $clientId `
    -CertificateThumbprint $thumbprint `
    -TenantId $tenantId

# Option 2: Service principal with client secret
$secureSecret = ConvertTo-SecureString $clientSecret -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($clientId, $secureSecret)
Connect-AzAccount -ServicePrincipal -Credential $credential -TenantId $tenantId

# Option 3: Interactive (for manual remediation)
Connect-AzAccount -TenantId $tenantId
```

!!! tip "Token Lifecycle"
    The script obtains tokens automatically via `Get-AzAccessToken`. If your session expires during a long bulk run, re-run `Connect-AzAccount` and retry.

### Obtaining a Token for Diagnostic Commands

For standalone API calls outside the script (e.g., troubleshooting diagnostics):

```powershell
$tokenResult = Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com"
$token = if ($tokenResult.Token -is [securestring]) { $tokenResult.Token | ConvertFrom-SecureString -AsPlainText } else { $tokenResult.Token }
```

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Token expired or invalid scope | Re-authenticate; verify `https://api.bap.microsoft.com/.default` scope |
| `403 Forbidden` | Insufficient permissions | Verify service principal has Power Platform Admin or Environment Admin role |
| `404 Not Found` | Invalid EnvironmentName | Use the canonical EnvironmentName (GUID format), not the display name |
| `429 Too Many Requests` | API rate limiting | Implement retry with exponential backoff; reduce concurrency for bulk runs |

---

## Next Steps

- [Portal Walkthrough](portal-walkthrough.md) — Manual PPAC configuration
- [Verification & Testing](verification-testing.md) — Validate remediation results
- [Troubleshooting](troubleshooting.md) — Advanced diagnostics

---

*Updated: February 2026 | Version: v1.3*
