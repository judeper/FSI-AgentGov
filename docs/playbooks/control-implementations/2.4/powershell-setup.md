# Control 2.4: Business Continuity and Disaster Recovery - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 2.4](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md).

---

## Automated Solution Backup Script

```powershell
# Automated BC/DR Backup Script
param(
    [string]$EnvironmentUrl = "https://yourorg.crm.dynamics.com",
    [string]$BackupPath = "\\fileserver\backups\PowerPlatform",
    [string[]]$SolutionNames = @("TradingAssistant", "CustomerService", "ComplianceBot")
)

# Install/Import modules
Import-Module Microsoft.PowerApps.Administration.PowerShell

# Connect to Power Platform
Connect-PowerApps

# Create backup folder
$backupDate = Get-Date -Format "yyyyMMdd_HHmm"
$backupFolder = Join-Path $BackupPath $backupDate
New-Item -ItemType Directory -Path $backupFolder -Force

# Backup each solution
$backupResults = @()

foreach ($solution in $SolutionNames) {
    Write-Host "Backing up solution: $solution" -ForegroundColor Cyan

    try {
        $outputFile = Join-Path $backupFolder "$solution.zip"

        # Export solution (requires connection to Dataverse)
        # Using Power Platform CLI
        pac solution export --name $solution --path $outputFile --managed true

        $backupResults += [PSCustomObject]@{
            Solution = $solution
            Status = "Success"
            FilePath = $outputFile
            FileSize = (Get-Item $outputFile).Length
            Timestamp = Get-Date
        }
    }
    catch {
        $backupResults += [PSCustomObject]@{
            Solution = $solution
            Status = "Failed"
            Error = $_.Exception.Message
            Timestamp = Get-Date
        }
    }
}

# Generate backup report
$reportPath = Join-Path $backupFolder "BackupReport.html"
$html = @"
<!DOCTYPE html>
<html>
<head><title>BC/DR Backup Report</title>
<style>
body { font-family: 'Segoe UI', sans-serif; margin: 20px; }
h1 { color: #0078d4; }
.success { color: green; }
.failed { color: red; }
table { border-collapse: collapse; width: 100%; }
th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
th { background: #0078d4; color: white; }
</style>
</head>
<body>
<h1>BC/DR Backup Report</h1>
<p>Backup Date: $backupDate</p>
<p>Environment: $EnvironmentUrl</p>
<table>
<tr><th>Solution</th><th>Status</th><th>File Size</th><th>Timestamp</th></tr>
$(
$backupResults | ForEach-Object {
    $statusClass = if ($_.Status -eq "Success") { "success" } else { "failed" }
    "<tr><td>$($_.Solution)</td><td class='$statusClass'>$($_.Status)</td><td>$([math]::Round($_.FileSize/1MB, 2)) MB</td><td>$($_.Timestamp)</td></tr>"
}
)
</table>
</body>
</html>
"@

$html | Out-File -FilePath $reportPath
Write-Host "Backup complete. Report: $reportPath" -ForegroundColor Green

# Return results
$backupResults
```

---

## DR Environment Health Check

```powershell
# DR Environment Health Check Script
param(
    [string]$DREnvironmentUrl = "https://yourorg-dr.crm.dynamics.com"
)

Write-Host "=== DR Environment Health Check ===" -ForegroundColor Cyan
Write-Host "Environment: $DREnvironmentUrl"
Write-Host "Timestamp: $(Get-Date)"
Write-Host ""

# Check environment connectivity
Write-Host "Checking environment connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $DREnvironmentUrl -Method Head -TimeoutSec 30
    Write-Host "  Environment reachable: Yes" -ForegroundColor Green
    Write-Host "  Response code: $($response.StatusCode)"
}
catch {
    Write-Host "  Environment reachable: No" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)"
}

# Get Power Platform environment status
Write-Host "`nChecking Power Platform status..." -ForegroundColor Yellow
Connect-PowerApps

$environments = Get-AdminPowerAppEnvironment | Where-Object {
    $_.DisplayName -like "*-DR"
}

foreach ($env in $environments) {
    Write-Host "  Environment: $($env.DisplayName)"
    Write-Host "    State: $($env.EnvironmentSku)"
    Write-Host "    Region: $($env.Location)"
    Write-Host "    Last Modified: $($env.LastModifiedTime)"
}

# Check solution versions
Write-Host "`nChecking solution deployment status..." -ForegroundColor Yellow
# Would require Dataverse connection to verify solutions

Write-Host "`n=== Health Check Complete ===" -ForegroundColor Cyan
```

---

## Azure DevOps Backup Pipeline

```yaml
# backup-pipeline.yml
trigger: none  # Scheduled trigger

schedules:
- cron: "0 2 * * *"  # Daily at 2 AM
  displayName: Daily Solution Backup
  branches:
    include:
      - main
  always: true

pool:
  vmImage: 'windows-latest'

variables:
  - group: 'PowerPlatform-Backup'
  - name: BackupDate
    value: $[format('{0:yyyyMMdd_HHmm}', pipeline.startTime)]

stages:
- stage: BackupTier1
  displayName: 'Backup Tier 1 Critical Agents'
  jobs:
  - job: BackupCritical
    steps:
    - task: PowerPlatformToolInstaller@2
      displayName: 'Install Power Platform CLI'

    - task: PowerPlatformExportSolution@2
      displayName: 'Export Trading Assistant Solution'
      inputs:
        authenticationType: 'PowerPlatformSPN'
        PowerPlatformSPN: 'Prod-Environment-Connection'
        SolutionName: 'TradingAssistant'
        SolutionOutputFile: '$(Build.ArtifactStagingDirectory)/TradingAssistant_$(BackupDate).zip'
        Managed: true

    - task: AzureCLI@2
      displayName: 'Upload to Azure Blob'
      inputs:
        azureSubscription: 'DR-Storage-Connection'
        scriptType: 'ps'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az storage blob upload `
            --account-name fsibackupstorage `
            --container-name solution-backups `
            --file "$(Build.ArtifactStagingDirectory)/TradingAssistant_$(BackupDate).zip" `
            --name "TradingAssistant/TradingAssistant_$(BackupDate).zip"

    - task: PublishBuildArtifacts@1
      inputs:
        PathtoPublish: '$(Build.ArtifactStagingDirectory)'
        ArtifactName: 'Tier1Backup_$(BackupDate)'

- stage: BackupTier2
  displayName: 'Backup Tier 2 High Priority Agents'
  dependsOn: BackupTier1
  jobs:
  - job: BackupHighPriority
    steps:
    # Similar steps for Tier 2 agents
    - script: echo "Backup Tier 2 agents"
```

---

## DR Sync Pipeline

```yaml
# dr-sync-pipeline.yml
# Runs weekly to keep DR environment current
schedules:
- cron: "0 4 * * 0"  # Weekly on Sunday at 4 AM
  displayName: Weekly DR Sync

stages:
- stage: SyncDR
  jobs:
  - job: DeployToDR
    steps:
    - task: PowerPlatformImportSolution@2
      displayName: 'Import to DR Environment'
      inputs:
        authenticationType: 'PowerPlatformSPN'
        PowerPlatformSPN: 'DR-Environment-Connection'
        SolutionInputFile: '$(Pipeline.Workspace)/latest-backup/solution.zip'
```

---

## Backup Retention Management

```powershell
# Backup Retention Cleanup Script
param(
    [string]$BackupPath = "\\fileserver\backups\PowerPlatform",
    [int]$DailyRetentionDays = 30,
    [int]$WeeklyRetentionWeeks = 12,
    [int]$MonthlyRetentionMonths = 12
)

Write-Host "=== Backup Retention Cleanup ===" -ForegroundColor Cyan
Write-Host "Path: $BackupPath"
Write-Host "Daily retention: $DailyRetentionDays days"

# Get all backup folders
$folders = Get-ChildItem -Path $BackupPath -Directory | Sort-Object Name -Descending

$cutoffDate = (Get-Date).AddDays(-$DailyRetentionDays)
$deletedCount = 0

foreach ($folder in $folders) {
    # Parse date from folder name (format: yyyyMMdd_HHmm)
    $folderDateStr = $folder.Name.Substring(0, 8)
    $folderDate = [datetime]::ParseExact($folderDateStr, "yyyyMMdd", $null)

    if ($folderDate -lt $cutoffDate) {
        Write-Host "Deleting old backup: $($folder.Name)" -ForegroundColor Yellow
        # Remove-Item -Path $folder.FullName -Recurse -Force
        # Uncomment above line to actually delete
        $deletedCount++
    }
}

Write-Host "`nCleanup complete. Deleted: $deletedCount folders" -ForegroundColor Green
```

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.2*
