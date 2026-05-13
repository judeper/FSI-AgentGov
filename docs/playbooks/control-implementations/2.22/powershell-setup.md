# PowerShell Setup: Control 2.22 - Inactivity Timeout Enforcement

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below may show abbreviated patterns; the baseline is authoritative.

> **Parent Control:** [2.22 - Inactivity Timeout Enforcement](../../../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md)

**Last Updated:** April 2026
**Module Requirements:** Az.Accounts, PowerShell 7.0+
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

!!! note "Script Location"
    The script is located at `scripts/governance/Set-InactivityTimeout.ps1` in the FSI-AgentGov repository. Navigate to the `scripts/governance/` directory or adjust paths in the commands below accordingly.

### Synopsis

Configures the inactivity timeout duration for a Power Platform environment via the BAP Admin API privacy settings endpoint. Uses a GET-PATCH-GET pattern to read current state, apply changes, and verify. Supports `-WhatIf` for preview mode, optional Dataverse audit record writing, and evidence packaging with SHA-256 integrity hashing.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `-EnvironmentName` | String | Yes | — | Power Platform Environment Name (canonical GUID, not display name) |
| `-TimeoutDuration` | Int32 | No | 120 | Inactivity timeout duration in minutes (valid range: 5-120) |
| `-WarningDuration` | Int32 | No | 5 | Warning notification duration in minutes before timeout (valid range: 1-30; must be less than `-TimeoutDuration`) |
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
# CSV file must include a header row.
# Required columns: EnvironmentName, TimeoutDuration
# Optional column: WarningDuration (defaults to 5 if omitted)
#
# Example CSV (non-compliant-environments.csv):
# EnvironmentName,TimeoutDuration,WarningDuration
# d1234567-abcd-ef01-2345-6789abcdef01,60,10
# e2345678-bcde-f012-3456-789abcdef012,120,15

Import-Csv ".\non-compliant-environments.csv" | ForEach-Object {
    $params = @{
        EnvironmentName = $_.EnvironmentName
        TimeoutDuration = [int]$_.TimeoutDuration
    }
    if ($_.WarningDuration) {
        $params['WarningDuration'] = [int]$_.WarningDuration
    }
    .\Set-InactivityTimeout.ps1 @params
}
```

#### Bulk remediation with WhatIf preview

```powershell
Import-Csv ".\non-compliant-environments.csv" | ForEach-Object {
    $params = @{
        EnvironmentName = $_.EnvironmentName
        TimeoutDuration = [int]$_.TimeoutDuration
        WhatIf          = $true
    }
    if ($_.WarningDuration) {
        $params['WarningDuration'] = [int]$_.WarningDuration
    }
    .\Set-InactivityTimeout.ps1 @params
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

!!! note "Session Expiration via BAP Admin API"
    The BAP Admin API privacy settings endpoint also returns session expiration properties alongside inactivity timeout settings. When querying an environment's privacy settings using the GET endpoint above, the response may include session expiration fields. Organizations can use this endpoint to programmatically verify both inactivity timeout and session expiration configuration in a single API call. Refer to the existing patterns in the GET and PATCH examples above for authentication and request format.

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

1. Register an application in Microsoft Entra ID
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
| Other HTTP errors | Various API issues | Check the error message for details; verify API endpoint availability and request format |

---

## Evidence Hash Verification

When `-IncludeEvidence` is used, the script computes a SHA-256 integrity hash over the result object. The hash is computed on **compressed JSON** (no whitespace). To verify a previously exported evidence file:

```powershell
# 1. Read the exported evidence JSON
$evidence = Get-Content .\evidence\timeout-remediation.json -Raw | ConvertFrom-Json

# 2. Capture the recorded hash, then null it out for recomputation
$recordedHash = $evidence.Metadata.IntegrityHash
$evidence.Metadata.IntegrityHash = $null

# 3. Recompute the hash using compressed JSON (must match original format)
$json = $evidence | ConvertTo-Json -Depth 10 -Compress
$hashBytes = [System.Security.Cryptography.SHA256]::Create().ComputeHash(
    [System.Text.Encoding]::UTF8.GetBytes($json)
)
$computedHash = [BitConverter]::ToString($hashBytes) -replace '-'

# 4. Compare
if ($computedHash -eq $recordedHash) {
    Write-Host "Evidence integrity verified" -ForegroundColor Green
} else {
    Write-Warning "Hash mismatch — evidence may have been modified"
}
```

!!! warning "Compression Required"
    The hash is computed on compressed JSON (`ConvertTo-Json -Compress`). Using pretty-printed JSON for verification will produce a different hash. If hash verification fails on an unmodified file, ensure you are using the same PowerShell version that generated the evidence — JSON property ordering may vary between PowerShell versions.

---

## Next Steps

- [Portal Walkthrough](portal-walkthrough.md) — Manual PPAC configuration
- [Verification & Testing](verification-testing.md) — Validate remediation results
- [Troubleshooting](troubleshooting.md) — Advanced diagnostics

---

*Updated: April 2026 | Version: v1.6.2*
