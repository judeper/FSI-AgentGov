# PowerShell Setup: Control 2.22 - Inactivity Timeout Enforcement

**Last Updated:** February 2026
**Module Requirements:** Az.Accounts (for service principal auth), Invoke-RestMethod (built-in)
**Estimated Time:** 30 minutes for setup; 5 minutes per remediation run

## Prerequisites

- [ ] PowerShell 7.x or later installed
- [ ] Az.Accounts module installed (`Install-Module Az.Accounts`)
- [ ] Service principal with Power Platform Admin role or delegated environment admin
- [ ] App registration with `https://api.bap.microsoft.com/.default` scope granted
- [ ] Client ID, Client Secret (or Certificate), and Tenant ID available
- [ ] Environment names (EnvironmentName, not display name) identified for remediation

---

## Script: Set-InactivityTimeout.ps1

### Synopsis

Configures the inactivity timeout duration for a Power Platform environment via the BAP Admin API privacy settings endpoint. Supports `-WhatIf` for preview mode and bulk remediation through pipeline input.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `-EnvironmentName` | String | Yes | Power Platform Environment Name (canonical ID, not display name) |
| `-TimeoutDuration` | Int32 | Yes | Inactivity timeout duration in minutes (e.g., 30, 60, 120) |
| `-EnableTimeout` | Switch | No | Enables the inactivity timeout if currently disabled (default: assumes enabled) |
| `-ClientId` | String | Yes | Azure AD App Registration Client ID for service principal auth |
| `-TenantId` | String | Yes | Azure AD Tenant ID |
| `-ClientSecret` | SecureString | No | Client secret for authentication (use `-Certificate` alternatively) |
| `-Certificate` | X509Certificate2 | No | Certificate for authentication (preferred over client secret) |
| `-WhatIf` | Switch | No | Preview mode — displays what would be changed without making modifications |
| `-Verbose` | Switch | No | Detailed output including API request/response details |

### Example Commands

#### Preview changes (WhatIf mode)

```powershell
.\Set-InactivityTimeout.ps1 `
    -EnvironmentName "d1234567-abcd-ef01-2345-6789abcdef01" `
    -TimeoutDuration 60 `
    -ClientId $clientId `
    -TenantId $tenantId `
    -ClientSecret $clientSecret `
    -WhatIf
```

**Expected output:**
```
[WhatIf] Would set inactivity timeout for environment 'd1234567-abcd-ef01-2345-6789abcdef01':
  Current timeout enabled: True
  Current duration: 120 minutes
  New duration: 60 minutes
```

#### Apply remediation to a single environment

```powershell
.\Set-InactivityTimeout.ps1 `
    -EnvironmentName "d1234567-abcd-ef01-2345-6789abcdef01" `
    -TimeoutDuration 60 `
    -EnableTimeout `
    -ClientId $clientId `
    -TenantId $tenantId `
    -ClientSecret $clientSecret `
    -Verbose
```

#### Bulk remediation from CSV

```powershell
# CSV format: EnvironmentName,TimeoutDuration
# d1234567-abcd-ef01-2345-6789abcdef01,60
# e2345678-bcde-f012-3456-789abcdef012,120

Import-Csv ".\non-compliant-environments.csv" | ForEach-Object {
    .\Set-InactivityTimeout.ps1 `
        -EnvironmentName $_.EnvironmentName `
        -TimeoutDuration $_.TimeoutDuration `
        -EnableTimeout `
        -ClientId $clientId `
        -TenantId $tenantId `
        -ClientSecret $clientSecret
}
```

#### Bulk remediation with WhatIf preview

```powershell
Import-Csv ".\non-compliant-environments.csv" | ForEach-Object {
    .\Set-InactivityTimeout.ps1 `
        -EnvironmentName $_.EnvironmentName `
        -TimeoutDuration $_.TimeoutDuration `
        -ClientId $clientId `
        -TenantId $tenantId `
        -ClientSecret $clientSecret `
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
  "settings": {
    "inactivityTimeout": {
      "enabled": true,
      "inactivityTimeoutInMinutes": 120,
      "warningTimeoutInMinutes": 10
    }
  }
}
```

### PATCH — Update Privacy Settings

```
PATCH https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/scopes/admin/environments/{EnvironmentName}/settings/privacy?api-version=2021-04-01

Authorization: Bearer {access_token}
Content-Type: application/json

{
  "settings": {
    "inactivityTimeout": {
      "enabled": true,
      "inactivityTimeoutInMinutes": 60,
      "warningTimeoutInMinutes": 5
    }
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

### Obtaining an Access Token

```powershell
# Using Az.Accounts module
Connect-AzAccount -ServicePrincipal `
    -ApplicationId $clientId `
    -CertificateThumbprint $thumbprint `
    -TenantId $tenantId

$token = (Get-AzAccessToken -ResourceUrl "https://api.bap.microsoft.com").Token
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
