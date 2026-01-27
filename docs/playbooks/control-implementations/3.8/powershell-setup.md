# Control 3.8: Copilot Hub and Governance Dashboard - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.Graph -Force -AllowClobber
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber

# Connect with required scopes
Connect-MgGraph -Scopes @(
    "Organization.Read.All",
    "Policy.Read.All",
    "Reports.Read.All",
    "User.Read.All"
)

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

---

## Get Copilot Configuration

```powershell
function Get-CopilotConfiguration {

    Write-Host "Retrieving Copilot configuration..." -ForegroundColor Cyan

    # Get organization settings
    $orgSettings = Get-MgOrganization
    Write-Host "Organization: $($orgSettings.DisplayName)"

    # Get Copilot service principal
    $copilotSP = Get-MgServicePrincipal -Filter "displayName eq 'Microsoft 365 Copilot'"
    if ($copilotSP) {
        Write-Host "Copilot Service Principal ID: $($copilotSP.Id)"
        Write-Host "Copilot App ID: $($copilotSP.AppId)"
    }

    # Get related enterprise apps
    $copilotApps = Get-MgServicePrincipal -All | Where-Object {
        $_.DisplayName -like "*Copilot*" -or $_.DisplayName -like "*Agent*"
    }

    Write-Host "`nCopilot-related applications:" -ForegroundColor Green
    $copilotApps | Select-Object DisplayName, AppId, AccountEnabled | Format-Table

    return $copilotApps
}
```

---

## Export Copilot Settings

```powershell
function Export-CopilotSettings {
    param(
        [string]$OutputPath = ".\CopilotExport"
    )

    Write-Host "Exporting Copilot settings..." -ForegroundColor Cyan

    if (!(Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

    # Export service principals
    $copilotApps = Get-MgServicePrincipal -Filter "startswith(displayName, 'Copilot') or startswith(displayName, 'Microsoft 365 Copilot')"
    $copilotApps | Select-Object DisplayName, AppId, Id, AccountEnabled |
        Export-Csv -Path "$OutputPath\CopilotServicePrincipals_$timestamp.csv" -NoTypeInformation

    # Export policies
    $policies = Get-MgPolicyAuthorizationPolicy
    $policies | ConvertTo-Json -Depth 5 | Out-File "$OutputPath\AuthorizationPolicies_$timestamp.json"

    Write-Host "Export completed to: $OutputPath" -ForegroundColor Green
}
```

---

## Audit Copilot Configuration Changes

```powershell
function Get-CopilotAuditEvents {
    param(
        [int]$DaysBack = 30
    )

    Write-Host "Retrieving Copilot audit events..." -ForegroundColor Cyan

    $startDate = (Get-Date).AddDays(-$DaysBack).ToString("yyyy-MM-ddTHH:mm:ssZ")
    $endDate = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")

    $auditLogs = Get-MgAuditLogDirectoryAudit -Filter "activityDateTime ge $startDate and activityDateTime le $endDate" -All

    $copilotEvents = $auditLogs | Where-Object {
        $_.TargetResources.DisplayName -like "*Copilot*" -or
        $_.ActivityDisplayName -like "*Copilot*" -or
        $_.ActivityDisplayName -like "*consent*" -or
        $_.ActivityDisplayName -like "*policy*"
    }

    Write-Host "Found $($copilotEvents.Count) Copilot-related audit events" -ForegroundColor Green

    $copilotEvents | Select-Object ActivityDateTime, ActivityDisplayName, InitiatedBy, Result |
        Format-Table -AutoSize

    return $copilotEvents
}
```

---

## Generate Governance Report

```powershell
function New-CopilotGovernanceReport {
    param(
        [string]$OutputPath = ".\CopilotGovernanceReport-$(Get-Date -Format 'yyyyMMdd').html"
    )

    Write-Host "Generating Copilot governance report..." -ForegroundColor Cyan

    $config = Get-CopilotConfiguration
    $events = Get-CopilotAuditEvents -DaysBack 30

    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Copilot Governance Report</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; }
        h1 { color: #0078d4; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #0078d4; color: white; padding: 12px; text-align: left; }
        td { border: 1px solid #ddd; padding: 10px; }
    </style>
</head>
<body>
    <h1>Copilot Governance Report</h1>
    <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')</p>

    <h2>Copilot Applications</h2>
    <table>
        <tr><th>Application</th><th>App ID</th><th>Enabled</th></tr>
        $($config | ForEach-Object {
            "<tr><td>$($_.DisplayName)</td><td>$($_.AppId)</td><td>$($_.AccountEnabled)</td></tr>"
        })
    </table>

    <h2>Recent Configuration Changes (30 days)</h2>
    <p>Total events: $($events.Count)</p>

    <h2>Recommendations</h2>
    <ul>
        <li>Review Copilot settings weekly</li>
        <li>Disable web search for compliance-sensitive environments</li>
        <li>Block external AI providers</li>
        <li>Monitor agent creation and sharing</li>
    </ul>
</body>
</html>
"@

    $html | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host "Report generated: $OutputPath" -ForegroundColor Green
}
```

---

## Usage Examples

```powershell
# Get Copilot configuration
Get-CopilotConfiguration

# Export settings
Export-CopilotSettings -OutputPath ".\CopilotBackup"

# Get audit events
Get-CopilotAuditEvents -DaysBack 30

# Generate governance report
New-CopilotGovernanceReport
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 3.8 - Copilot Hub and Governance Dashboard

.DESCRIPTION
    This script configures Copilot governance monitoring:
    1. Retrieves Copilot configuration
    2. Exports settings for documentation
    3. Audits configuration changes
    4. Generates governance report

.PARAMETER OutputPath
    Path for exported Copilot settings

.PARAMETER DaysBack
    Number of days to look back for audit events

.EXAMPLE
    .\Configure-Control-3.8.ps1 -OutputPath "C:\CopilotBackup" -DaysBack 30

.NOTES
    Last Updated: January 2026
    Related Control: Control 3.8 - Copilot Hub and Governance Dashboard
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\CopilotExport",

    [Parameter(Mandatory=$false)]
    [int]$DaysBack = 30
)

try {
    # Connect to Microsoft Graph
    Write-Host "Connecting to Microsoft Graph..." -ForegroundColor Cyan
    Connect-MgGraph -Scopes @(
        "Organization.Read.All",
        "Policy.Read.All",
        "Reports.Read.All",
        "User.Read.All"
    )

    Write-Host "Executing Control 3.8 Copilot Governance Configuration" -ForegroundColor Cyan

    # Get Copilot configuration
    Write-Host "`nRetrieving Copilot configuration..." -ForegroundColor Yellow
    $config = Get-CopilotConfiguration

    # Export settings
    Write-Host "Exporting Copilot settings..." -ForegroundColor Yellow
    Export-CopilotSettings -OutputPath $OutputPath

    # Get audit events
    Write-Host "Retrieving audit events (last $DaysBack days)..." -ForegroundColor Yellow
    $events = Get-CopilotAuditEvents -DaysBack $DaysBack

    # Generate governance report
    Write-Host "Generating governance report..." -ForegroundColor Yellow
    New-CopilotGovernanceReport

    Write-Host "`nCopilot Governance Summary:" -ForegroundColor Cyan
    Write-Host "  Copilot applications found: $($config.Count)" -ForegroundColor Green
    Write-Host "  Audit events (last $DaysBack days): $($events.Count)" -ForegroundColor Green
    Write-Host "  Export location: $OutputPath" -ForegroundColor Green

    Write-Host "`n[PASS] Control 3.8 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup Graph connection
    Disconnect-MgGraph -ErrorAction SilentlyContinue
}
```

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.2*
