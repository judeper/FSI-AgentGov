# Control 3.6: Orphaned Agent Detection and Remediation - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.Graph -Force -AllowClobber

# Connect to services
Add-PowerAppsAccount
Connect-MgGraph -Scopes "User.Read.All", "Application.Read.All"
```

---

## Detect Orphaned Agents

```powershell
function Find-OrphanedAgents {
    param(
        [int]$InactiveDays = 90
    )

    Write-Host "Scanning for orphaned agents..." -ForegroundColor Cyan

    # Get active users
    $activeUsers = Get-MgUser -Filter "accountEnabled eq true" -All | Select-Object -ExpandProperty Id

    # Get all environments
    $environments = Get-AdminPowerAppEnvironment

    $orphanedAgents = @()

    foreach ($env in $environments) {
        $apps = Get-AdminPowerApp -EnvironmentName $env.EnvironmentName

        foreach ($app in $apps) {
            $isOrphan = $false
            $orphanReason = ""

            # Check if owner is active
            if ($app.Owner -and $app.Owner.id -notin $activeUsers) {
                $isOrphan = $true
                $orphanReason = "Owner Departed"
            }

            # Check for inactivity (would need usage data in production)
            $lastModified = [DateTime]$app.LastModifiedTime
            if ($lastModified -lt (Get-Date).AddDays(-$InactiveDays)) {
                $isOrphan = $true
                $orphanReason = if ($orphanReason) { "$orphanReason; No Activity" } else { "No Activity" }
            }

            if ($isOrphan) {
                $orphanedAgents += [PSCustomObject]@{
                    AgentId = $app.AppName
                    AgentName = $app.DisplayName
                    Environment = $env.DisplayName
                    OwnerEmail = $app.Owner.email
                    OrphanReason = $orphanReason
                    LastModified = $lastModified
                    DiscoveryDate = Get-Date
                }
            }
        }
    }

    Write-Host "Found $($orphanedAgents.Count) orphaned agents" -ForegroundColor $(if ($orphanedAgents.Count -gt 0) { "Yellow" } else { "Green" })

    return $orphanedAgents
}
```

---

## Reassign Agent Owner

```powershell
function Set-AgentOwner {
    param(
        [Parameter(Mandatory=$true)]
        [string]$AgentId,
        [Parameter(Mandatory=$true)]
        [string]$EnvironmentName,
        [Parameter(Mandatory=$true)]
        [string]$NewOwnerEmail
    )

    Write-Host "Reassigning agent $AgentId to $NewOwnerEmail..." -ForegroundColor Cyan

    try {
        # Get new owner's ID
        $newOwner = Get-MgUser -Filter "mail eq '$NewOwnerEmail'"

        if (-not $newOwner) {
            Write-Error "User not found: $NewOwnerEmail"
            return $false
        }

        # Set new owner
        Set-AdminPowerAppOwner -AppName $AgentId -EnvironmentName $EnvironmentName -AppOwner $newOwner.Id

        Write-Host "Agent ownership transferred successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Error "Failed to reassign owner: $_"
        return $false
    }
}
```

---

## Archive Agent

```powershell
function Disable-OrphanedAgent {
    param(
        [Parameter(Mandatory=$true)]
        [string]$AgentId,
        [Parameter(Mandatory=$true)]
        [string]$EnvironmentName,
        [string]$Reason = "Orphaned - pending review"
    )

    Write-Host "Archiving agent: $AgentId" -ForegroundColor Yellow

    try {
        # Disable the app (quarantine)
        Set-AdminPowerAppAsSysAdmin -AppName $AgentId -EnvironmentName $EnvironmentName -Disable

        Write-Host "Agent disabled successfully" -ForegroundColor Green

        # Log the action
        $archiveLog = [PSCustomObject]@{
            AgentId = $AgentId
            Action = "Archived"
            Reason = $Reason
            ActionDate = Get-Date
            ActionBy = (Get-MgContext).Account
        }

        return $archiveLog
    }
    catch {
        Write-Error "Failed to archive agent: $_"
        return $null
    }
}
```

---

## Generate Orphan Report

```powershell
function New-OrphanAgentReport {
    param(
        [string]$OutputPath = ".\OrphanAgentReport-$(Get-Date -Format 'yyyyMMdd').html"
    )

    $orphans = Find-OrphanedAgents

    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Orphaned Agent Report</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; }
        h1 { color: #0078d4; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #0078d4; color: white; padding: 12px; text-align: left; }
        td { border: 1px solid #ddd; padding: 10px; }
        .warning { background: #fff3cd; }
        .critical { background: #f8d7da; }
    </style>
</head>
<body>
    <h1>Orphaned Agent Report</h1>
    <p>Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')</p>
    <p>Total Orphaned Agents: $($orphans.Count)</p>

    <table>
        <tr><th>Agent Name</th><th>Environment</th><th>Orphan Reason</th><th>Last Modified</th><th>Owner</th></tr>
        $($orphans | ForEach-Object {
            "<tr class='$(if ($_.OrphanReason -like '*Departed*') { 'critical' } else { 'warning' })'>
                <td>$($_.AgentName)</td>
                <td>$($_.Environment)</td>
                <td>$($_.OrphanReason)</td>
                <td>$($_.LastModified.ToString('yyyy-MM-dd'))</td>
                <td>$($_.OwnerEmail)</td>
            </tr>"
        })
    </table>
</body>
</html>
"@

    $html | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Host "Report generated: $OutputPath" -ForegroundColor Green

    return $OutputPath
}
```

---

## Usage Examples

```powershell
# Find orphaned agents
$orphans = Find-OrphanedAgents -InactiveDays 90

# Reassign an orphaned agent
Set-AgentOwner -AgentId "agent-123" -EnvironmentName "Default" -NewOwnerEmail "newowner@company.com"

# Archive an orphaned agent
Disable-OrphanedAgent -AgentId "agent-456" -EnvironmentName "Default" -Reason "Owner departed, no replacement identified"

# Generate report
New-OrphanAgentReport
```

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.1*
