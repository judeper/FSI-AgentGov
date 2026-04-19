# Control 2.4: Business Continuity and Disaster Recovery — PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

> Automation scripts for [Control 2.4: Business Continuity and Disaster Recovery](../../../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md).

---

## Audience

M365 administrators in US financial services automating customer-side BC/DR operations for Power Platform and Copilot Studio agents. All scripts are designed for review by a Change Advisory Board before being scheduled in production tenants.

---

## Module Prerequisites

Pin every module to a CAB-approved version per the [PowerShell baseline §1](../../_shared/powershell-baseline.md). The snippets below show module names only; substitute `-RequiredVersion '<version>'` per the baseline.

| Module | Used For | Edition |
|--------|----------|---------|
| `Microsoft.PowerApps.Administration.PowerShell` | Environment, backup, copy-environment operations | Windows PowerShell 5.1 (Desktop) |
| `Microsoft.PowerApps.PowerShell` | App / connection inventory | Desktop |
| `Microsoft.Graph` | Service Health, Entra app and credential checks | PowerShell 7+ |
| `Az.Storage` | Push solution exports to immutable Azure Blob | PowerShell 7+ |
| `Microsoft.Xrm.Tooling.CrmConnector.PowerShell` | Solution export / import | Desktop |

The Power Platform CLI (`pac`) is also used for solution export — install via `winget install Microsoft.PowerAppsCLI` or `dotnet tool install --global Microsoft.PowerApps.CLI` and pin the version.

!!! note "Edition guard"
    Power Apps Administration cmdlets require Windows PowerShell 5.1 (Desktop). Per baseline §2, every script that imports `Microsoft.PowerApps.Administration.PowerShell` should include the edition guard.

---

## 1. Inventory In-Scope Environments and Agents

```powershell
<#
  .SYNOPSIS  Build a BC/DR scope inventory of Power Platform environments
             and their hosted Copilot Studio agents (bots) with last-modified
             timestamps. Output feeds the BIA and exercise evidence pack.
  .OUTPUT    Tagged JSON with SHA-256 evidence hash per baseline §6.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $OutputFolder
)

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "This script requires Windows PowerShell 5.1 (Desktop)."
}

Import-Module Microsoft.PowerApps.Administration.PowerShell
Add-PowerAppsAccount  # interactive; use -ApplicationId/-ClientSecret/-TenantID for unattended

$envs = Get-AdminPowerAppEnvironment | Where-Object {
    $_.EnvironmentType -in @('Production','Sandbox')
}

$inventory = foreach ($env in $envs) {
    [pscustomobject]@{
        EnvironmentName = $env.DisplayName
        EnvironmentId   = $env.EnvironmentName
        Region          = $env.Location
        Type            = $env.EnvironmentType
        IsManaged       = $env.GovernanceConfiguration.ProtectionLevel
        CreatedOn       = $env.CreatedTime
        LastModified    = $env.LastModifiedTime
    }
}

$timestamp  = (Get-Date).ToString('yyyyMMdd-HHmmss')
$outFile    = Join-Path $OutputFolder "bcdr-inventory-$timestamp.json"
$inventory | ConvertTo-Json -Depth 6 | Out-File -FilePath $outFile -Encoding UTF8

# Evidence hash per baseline §6
$hash = (Get-FileHash -Path $outFile -Algorithm SHA256).Hash
"$hash  $(Split-Path -Leaf $outFile)" | Out-File -FilePath "$outFile.sha256"

Write-Host "Inventory written: $outFile" -ForegroundColor Green
Write-Host "SHA-256: $hash"
```

Cross-reference output with the agent inventory maintained under [Control 3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).

---

## 2. Trigger and Verify a Manual Dataverse Backup

Manual backups complement Microsoft's continuous system backups and are required before any high-risk change. The cmdlet `Backup-PowerAppEnvironment` initiates a backup; `Get-PowerAppEnvironmentBackups` lists existing backups.

```powershell
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory)] [string] $EnvironmentId,
    [Parameter(Mandatory)] [string] $Label
)

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "This script requires Windows PowerShell 5.1 (Desktop)."
}

Import-Module Microsoft.PowerApps.Administration.PowerShell
Add-PowerAppsAccount

if ($PSCmdlet.ShouldProcess($EnvironmentId, "Create manual backup '$Label'")) {
    $result = Backup-PowerAppEnvironment `
        -EnvironmentName $EnvironmentId `
        -BackupLabel     $Label

    if ($result.Code -ne 200 -and $result.Code -ne 202) {
        throw "Backup request failed: $($result.Code) $($result.Description)"
    }
}

Start-Sleep -Seconds 30
$backups = Get-PowerAppEnvironmentBackups -EnvironmentName $EnvironmentId
$backups | Sort-Object BackupDateTime -Descending | Select-Object -First 5 |
    Format-Table BackupDateTime, BackupLabel, BackupType
```

**FSI guidance:**

- Always run with `-WhatIf` first in the change window (baseline §3)
- Capture the output as exercise / change evidence
- Manual backup retention is governed by the published Power Platform policy — verify current retention before assuming a specific window

---

## 3. Provision and Refresh the Secondary-Region Environment

```powershell
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory)] [string] $PrimaryDisplayName,
    [Parameter(Mandatory)] [string] $DrRegion,           # e.g., 'unitedstates' or specific paired region per Microsoft Learn
    [Parameter(Mandatory)] [string] $SecurityGroupId,    # restricted security group
    [string] $CurrencyName = 'USD',
    [string] $LanguageName = 'English'
)

if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "This script requires Windows PowerShell 5.1 (Desktop)."
}

Import-Module Microsoft.PowerApps.Administration.PowerShell
Add-PowerAppsAccount

$drDisplayName = "$PrimaryDisplayName-DR"

if ($PSCmdlet.ShouldProcess($drDisplayName, "Provision DR environment in region '$DrRegion'")) {
    $env = New-AdminPowerAppEnvironment `
        -DisplayName        $drDisplayName `
        -LocationName       $DrRegion `
        -EnvironmentSku     'Production' `
        -ProvisionDatabase `
        -CurrencyName       $CurrencyName `
        -LanguageName       $LanguageName `
        -SecurityGroupId    $SecurityGroupId

    Write-Host "DR environment created: $($env.EnvironmentName)" -ForegroundColor Green
}
```

To refresh DR from production on a schedule, use **Copy environment** rather than re-provisioning. `Copy-PowerAppEnvironment` supports `Full` or `Minimal` copy modes (note: only environments with the same governance settings can be copied).

```powershell
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory)] [string] $SourceEnvironmentId,
    [Parameter(Mandatory)] [string] $TargetEnvironmentId,
    [ValidateSet('Full','Minimal')] [string] $CopyType = 'Full'
)

if ($PSCmdlet.ShouldProcess($TargetEnvironmentId, "Copy '$CopyType' from $SourceEnvironmentId")) {
    Copy-PowerAppEnvironment `
        -EnvironmentName       $SourceEnvironmentId `
        -TargetEnvironmentName $TargetEnvironmentId `
        -CopyType              $CopyType
}
```

**FSI guidance:**

- Copy-environment is destructive on the target — always confirm the target is the DR environment, not production
- Copying overwrites Dataverse data — coordinate with users of the DR environment if it is also used for read-only standby queries
- After copy, re-apply DR-specific environment variable values and re-bind connection references

---

## 4. Customer-Managed Solution Export to Immutable Storage

This script exports each in-scope solution as a managed `.zip` and uploads to an Azure Blob container with an immutability policy (WORM) sufficient for SEC 17a-4 reconstruction.

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]   $EnvironmentUrl,        # https://<org>.crm.dynamics.com
    [Parameter(Mandatory)] [string[]] $SolutionNames,
    [Parameter(Mandatory)] [string]   $StagingFolder,
    [Parameter(Mandatory)] [string]   $StorageAccountName,
    [Parameter(Mandatory)] [string]   $ContainerName          # must have time-based retention policy enabled
)

# Authenticate Power Platform CLI
pac auth create --environment $EnvironmentUrl

$timestamp = (Get-Date).ToString('yyyyMMdd-HHmmss')
$results = foreach ($solution in $SolutionNames) {
    $outFile = Join-Path $StagingFolder "${solution}_${timestamp}.zip"
    pac solution export --name $solution --path $outFile --managed true
    if (-not (Test-Path $outFile)) {
        [pscustomobject]@{ Solution = $solution; Status = 'Failed'; Path = $null }
        continue
    }
    $hash = (Get-FileHash -Path $outFile -Algorithm SHA256).Hash
    "$hash  $(Split-Path -Leaf $outFile)" | Out-File "$outFile.sha256"

    [pscustomobject]@{
        Solution = $solution
        Status   = 'Exported'
        Path     = $outFile
        SizeMB   = [math]::Round((Get-Item $outFile).Length / 1MB, 2)
        Sha256   = $hash
    }
}

# Upload to immutable Blob (storage account must have version-level immutability enabled)
Import-Module Az.Storage
$ctx = New-AzStorageContext -StorageAccountName $StorageAccountName -UseConnectedAccount
foreach ($r in $results | Where-Object Status -eq 'Exported') {
    $blobName = "$timestamp/$([System.IO.Path]::GetFileName($r.Path))"
    Set-AzStorageBlobContent -File $r.Path -Container $ContainerName -Blob $blobName -Context $ctx -Force | Out-Null
    Set-AzStorageBlobContent -File "$($r.Path).sha256" -Container $ContainerName -Blob "$blobName.sha256" -Context $ctx -Force | Out-Null
}

$results | Format-Table
```

**FSI guidance:**

- The Azure Blob container must have an active **time-based retention policy** that meets the longest applicable retention requirement (typically six years for SEC 17a-4)
- The SHA-256 sidecar file supports independent integrity verification of the export
- Schedule via Azure Automation, Azure DevOps Pipelines, or GitHub Actions with a service principal that has only the necessary Dataverse and Storage Blob Data Contributor roles
- **Solution export does not always include knowledge sources, certain custom topics, or external data referenced by Copilot Studio agents.** Document and script separate export procedures for excluded components

---

## 5. Validate Agent Identity Continuity in the DR Environment

This Microsoft Graph script enumerates app registrations / Entra Agent IDs used by in-scope agents and verifies they still have valid federated credentials and have not exceeded credential expiry windows.

```powershell
#Requires -Version 7.2
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string[]] $AppDisplayNames,
    [int] $MinDaysToCredentialExpiry = 30
)

Import-Module Microsoft.Graph.Applications
Connect-MgGraph -Scopes 'Application.Read.All','Directory.Read.All'

$findings = foreach ($name in $AppDisplayNames) {
    $app = Get-MgApplication -Filter "displayName eq '$name'" -ErrorAction Stop |
        Select-Object -First 1
    if (-not $app) {
        [pscustomobject]@{ App = $name; Status = 'NotFound' }
        continue
    }

    $secrets   = $app.PasswordCredentials
    $certs     = $app.KeyCredentials
    $fedCreds  = Get-MgApplicationFederatedIdentityCredential -ApplicationId $app.Id

    $now       = Get-Date
    $expiring  = @($secrets + $certs) |
        Where-Object { $_.EndDateTime -lt $now.AddDays($MinDaysToCredentialExpiry) }

    [pscustomobject]@{
        App                 = $name
        AppId               = $app.AppId
        FederatedCredsCount = $fedCreds.Count
        SecretsExpiringSoon = $expiring.Count
        Status              = if ($expiring.Count -gt 0) { 'CredentialRotationNeeded' } else { 'OK' }
    }
}

$findings | Format-Table -AutoSize
$findings | Where-Object Status -ne 'OK' | ForEach-Object {
    Write-Warning "Action required: $($_.App) — $($_.Status)"
}
```

Run before every quarterly Zone 3 exercise. Any `CredentialRotationNeeded` finding becomes a blocker for the exercise until remediated.

---

## 6. Smoke-Test the DR Environment

After failover (or quarterly), confirm the DR environment is reachable, the application users are present, and key Dataverse tables respond.

```powershell
#Requires -Version 7.2
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $DrEnvironmentUrl,    # https://<dr-org>.crm.dynamics.com
    [Parameter(Mandatory)] [string] $TenantId,
    [Parameter(Mandatory)] [string] $ClientId,
    [Parameter(Mandatory)] [securestring] $ClientSecret
)

# 1. Reachability
try {
    $r = Invoke-WebRequest -Uri $DrEnvironmentUrl -Method Head -TimeoutSec 30 -UseBasicParsing
    Write-Host "Reachability: $($r.StatusCode)" -ForegroundColor Green
} catch {
    Write-Error "DR environment unreachable: $($_.Exception.Message)"
    return
}

# 2. Token acquisition (validates app user exists in DR)
$tokenBody = @{
    grant_type    = 'client_credentials'
    client_id     = $ClientId
    client_secret = (New-Object System.Net.NetworkCredential('', $ClientSecret)).Password
    scope         = "$DrEnvironmentUrl/.default"
}
$token = Invoke-RestMethod -Method POST -Uri "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token" -Body $tokenBody
Write-Host "Token acquired (length: $($token.access_token.Length))" -ForegroundColor Green

# 3. Dataverse WhoAmI smoke test
$headers = @{
    'Authorization'    = "Bearer $($token.access_token)"
    'Accept'           = 'application/json'
    'OData-MaxVersion' = '4.0'
    'OData-Version'    = '4.0'
}
$who = Invoke-RestMethod -Method GET -Uri "$DrEnvironmentUrl/api/data/v9.2/WhoAmI" -Headers $headers
Write-Host "WhoAmI OK — UserId: $($who.UserId)" -ForegroundColor Green
```

---

## 7. Subscribe to Service Health Alerts via Graph

```powershell
#Requires -Version 7.2
Import-Module Microsoft.Graph.DeviceManagement.Administration
Connect-MgGraph -Scopes 'ServiceHealth.Read.All','ServiceMessage.Read.All'

# List active health issues affecting Power Platform / Dataverse / Copilot
Get-MgServiceAnnouncementHealthOverview |
    Where-Object Service -Match 'Power|Dataverse|Copilot|Entra' |
    Select-Object Service, Status, FeatureGroup |
    Format-Table

# List active service messages (Message Center)
Get-MgServiceAnnouncementMessage -Filter "category eq 'planForChange' or category eq 'preventOrFixIssue'" |
    Where-Object { $_.Services -match 'Power|Dataverse|Copilot|Entra' } |
    Sort-Object LastModifiedDateTime -Descending |
    Select-Object Id, Title, Severity, StartDateTime, EndDateTime |
    Format-Table -AutoSize
```

Wire this script to a scheduled job that posts to the DR Teams channel; do not rely solely on email subscriptions in regulated tenants.

---

## 8. Backup Retention Cleanup (Local Staging Only)

The immutable Azure Blob retention policy governs long-term retention. Local staging directories should be cleaned on a short cadence to limit data sprawl.

```powershell
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory)] [string] $StagingFolder,
    [int] $LocalRetentionDays = 14
)

$cutoff  = (Get-Date).AddDays(-$LocalRetentionDays)
$candidates = Get-ChildItem -Path $StagingFolder -File |
    Where-Object { $_.LastWriteTime -lt $cutoff }

foreach ($file in $candidates) {
    if ($PSCmdlet.ShouldProcess($file.FullName, 'Delete local staging file')) {
        Remove-Item -Path $file.FullName -Force
    }
}

Write-Host "Local cleanup complete — removed $($candidates.Count) files older than $LocalRetentionDays days."
```

Never delete from the immutable Blob container — that is governed by the storage account's immutability policy, not this script.

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md) — Step-by-step portal configuration
- [Verification & Testing](verification-testing.md) — Test cases, exercise scenarios, evidence collection
- [Troubleshooting](troubleshooting.md) — Common issues and resolutions

---

*Updated: April 2026 | Version: v1.3.3*
