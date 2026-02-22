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

## AI Feature Access Control Management

### Create Admin Exclusion Group

```powershell
function New-CopilotAdminExclusionGroup {
    param(
        [string]$GroupName = "CopilotForM365AdminExclude",
        [string]$Description = "Users excluded from Microsoft 365 Copilot access for compliance reasons"
    )

    Write-Host "Creating Admin Exclusion Group: $GroupName" -ForegroundColor Cyan

    # Check if group already exists
    $existingGroup = Get-MgGroup -Filter "displayName eq '$GroupName'" -ErrorAction SilentlyContinue

    if ($existingGroup) {
        Write-Host "Group already exists: $($existingGroup.Id)" -ForegroundColor Yellow
        return $existingGroup
    }

    # Create new security group
    $groupParams = @{
        DisplayName = $GroupName
        Description = $Description
        MailEnabled = $false
        SecurityEnabled = $true
        MailNickname = $GroupName.Replace(" ", "")
    }

    $newGroup = New-MgGroup -BodyParameter $groupParams
    Write-Host "Admin Exclusion Group created successfully: $($newGroup.Id)" -ForegroundColor Green

    return $newGroup
}
```

### Add Users to Admin Exclusion Group

```powershell
function Add-UsersToAdminExclusionGroup {
    param(
        [Parameter(Mandatory=$true)]
        [string[]]$UserPrincipalNames,

        [string]$GroupName = "CopilotForM365AdminExclude"
    )

    Write-Host "Adding users to Admin Exclusion Group..." -ForegroundColor Cyan

    # Get the exclusion group
    $group = Get-MgGroup -Filter "displayName eq '$GroupName'"

    if (!$group) {
        Write-Host "Error: Admin Exclusion Group not found. Create it first." -ForegroundColor Red
        return
    }

    foreach ($upn in $UserPrincipalNames) {
        try {
            # Get user object
            $user = Get-MgUser -Filter "userPrincipalName eq '$upn'"

            if (!$user) {
                Write-Host "Warning: User not found: $upn" -ForegroundColor Yellow
                continue
            }

            # Add user to group
            $memberParams = @{
                "@odata.id" = "https://graph.microsoft.com/v1.0/directoryObjects/$($user.Id)"
            }

            New-MgGroupMember -GroupId $group.Id -BodyParameter $memberParams
            Write-Host "Added: $upn" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to add $upn : $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    Write-Host "`nNote: Changes take up to 24 hours to propagate." -ForegroundColor Yellow
}
```

### Bulk Add Users from CSV

```powershell
function Import-AdminExclusionGroupFromCSV {
    param(
        [Parameter(Mandatory=$true)]
        [string]$CsvPath,

        [string]$GroupName = "CopilotForM365AdminExclude"
    )

    Write-Host "Importing users from CSV: $CsvPath" -ForegroundColor Cyan

    # Import CSV (expects column: UserPrincipalName)
    $users = Import-Csv -Path $CsvPath

    if (!$users) {
        Write-Host "Error: No users found in CSV" -ForegroundColor Red
        return
    }

    Write-Host "Found $($users.Count) users in CSV" -ForegroundColor Green

    # Extract UPNs
    $upns = $users | Select-Object -ExpandProperty UserPrincipalName

    # Add to exclusion group
    Add-UsersToAdminExclusionGroup -UserPrincipalNames $upns -GroupName $GroupName
}
```

**Example CSV format:**

```csv
UserPrincipalName,Reason,AddedBy,AddedDate
trader1@contoso.com,Blackout period Q1 2026,compliance@contoso.com,2026-02-06
trader2@contoso.com,Blackout period Q1 2026,compliance@contoso.com,2026-02-06
employee3@contoso.com,Under compliance investigation,legal@contoso.com,2026-02-06
```

### Export Admin Exclusion Group Membership

```powershell
function Export-AdminExclusionGroupMembers {
    param(
        [string]$GroupName = "CopilotForM365AdminExclude",
        [string]$OutputPath = ".\AdminExclusionGroup_Members_$(Get-Date -Format 'yyyyMMdd').csv"
    )

    Write-Host "Exporting Admin Exclusion Group members..." -ForegroundColor Cyan

    # Get group
    $group = Get-MgGroup -Filter "displayName eq '$GroupName'"

    if (!$group) {
        Write-Host "Error: Group not found: $GroupName" -ForegroundColor Red
        return
    }

    # Get group members
    $members = Get-MgGroupMember -GroupId $group.Id -All

    # Expand member details
    $memberDetails = foreach ($member in $members) {
        $user = Get-MgUser -UserId $member.Id -ErrorAction SilentlyContinue
        if ($user) {
            [PSCustomObject]@{
                UserPrincipalName = $user.UserPrincipalName
                DisplayName = $user.DisplayName
                JobTitle = $user.JobTitle
                Department = $user.Department
                AddedToGroup = $member.AdditionalProperties.createdDateTime
            }
        }
    }

    # Export to CSV
    $memberDetails | Export-Csv -Path $OutputPath -NoTypeInformation
    Write-Host "Export completed: $OutputPath" -ForegroundColor Green
    Write-Host "Total members: $($memberDetails.Count)" -ForegroundColor Green
}
```

### Query Copilot Settings via Microsoft Graph

```powershell
function Get-CopilotSettings {

    Write-Host "Retrieving Copilot settings via Microsoft Graph..." -ForegroundColor Cyan

    # Note: As of February 2026, Copilot-specific settings may require
    # direct REST API calls as dedicated PowerShell cmdlets may not exist

    try {
        # Query organization settings
        $orgSettings = Get-MgOrganization | Select-Object -First 1

        # Query service principals related to Copilot
        $copilotSPs = Get-MgServicePrincipal -Filter "startswith(displayName, 'Microsoft 365 Copilot')" -All

        # Query authorization policies (may contain Copilot-related policies)
        $authPolicies = Get-MgPolicyAuthorizationPolicy

        Write-Host "`nOrganization: $($orgSettings.DisplayName)" -ForegroundColor Green
        Write-Host "Copilot Service Principals found: $($copilotSPs.Count)" -ForegroundColor Green

        # Build result object
        $result = [PSCustomObject]@{
            OrganizationName = $orgSettings.DisplayName
            TenantId = $orgSettings.Id
            CopilotServicePrincipals = $copilotSPs
            AuthorizationPolicies = $authPolicies
            RetrievedAt = Get-Date
        }

        return $result
    }
    catch {
        Write-Host "Error retrieving Copilot settings: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}
```

### Export Copilot Configuration for Compliance

```powershell
function Export-CopilotConfigurationForCompliance {
    param(
        [string]$OutputPath = ".\CopilotCompliance_$(Get-Date -Format 'yyyyMMdd')"
    )

    Write-Host "Exporting Copilot configuration for compliance documentation..." -ForegroundColor Cyan

    if (!(Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

    # 1. Export Admin Exclusion Group membership
    $exclusionGroupMembers = Export-AdminExclusionGroupMembers -OutputPath "$OutputPath\AdminExclusionGroup_$timestamp.csv"

    # 2. Export Copilot settings
    $copilotSettings = Get-CopilotSettings
    $copilotSettings | ConvertTo-Json -Depth 5 | Out-File "$OutputPath\CopilotSettings_$timestamp.json"

    # 3. Export deployment group assignments (if accessible via Graph API)
    # Note: This may require custom Graph API calls depending on API availability

    # 4. Export audit log of Copilot configuration changes
    $auditEvents = Get-CopilotAuditEvents -DaysBack 90
    $auditEvents | Select-Object ActivityDateTime, ActivityDisplayName, InitiatedBy, Result |
        Export-Csv -Path "$OutputPath\CopilotAuditEvents_$timestamp.csv" -NoTypeInformation

    Write-Host "`nCompliance export completed: $OutputPath" -ForegroundColor Green
    Write-Host "Files created:" -ForegroundColor Cyan
    Get-ChildItem -Path $OutputPath | Select-Object Name, Length, LastWriteTime | Format-Table
}
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
