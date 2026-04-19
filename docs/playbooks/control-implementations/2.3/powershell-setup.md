# Control 2.3: Change Management and Release Planning — PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show abbreviated patterns; the baseline is authoritative.

> Automation scripts for [Control 2.3: Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).
>
> **Audience:** Power Platform Admins and pipeline engineers in US financial services organizations.

---

## Module Inventory

| Module / CLI | Purpose | Notes |
|--------------|---------|-------|
| `Microsoft.PowerApps.Administration.PowerShell` | Tenant + environment admin operations | Pin per FSI baseline |
| `Microsoft.PowerApps.PowerShell` | Maker-side operations | Pin per FSI baseline |
| `Microsoft.Xrm.Tooling.CrmConnector.PowerShell` | Solution export / import via SDK | Required v3.3+ for `Import-CrmSolutionAsync` |
| `Microsoft.Graph.Authentication` + `Microsoft.Graph.Reports` | Service Communications API (Message Center) | Use the Graph SDK; do not script raw token acquisition |
| Power Platform CLI (`pac`) | Modern, recommended for new automation | Microsoft has signaled `pac` as the long-term path; the legacy `Crm` cmdlets remain supported |

> **FSI guidance:** New automation should be authored against `pac` and Microsoft Graph SDKs. The `Crm`/`PowerApps` modules below are retained because they remain in widespread use and the FSI baseline currently pins them. Track the baseline for migration timelines.

---

## Prerequisites

```powershell
# Install required modules (run as administrator; pin versions per FSI baseline)
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.PowerApps.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.Xrm.Tooling.CrmConnector.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.Graph.Authentication -Force
Install-Module -Name Microsoft.Graph.Reports -Force

# Interactive sign-in (developer / break-glass use only)
Add-PowerAppsAccount

# Service principal sign-in (production automation; recommended)
# Store secrets in Azure Key Vault or equivalent; never inline in scripts
# $appId    = (Get-Secret -Name 'fsi-pp-pipeline-spn-appid'    -AsPlainText)
# $secret   = (Get-Secret -Name 'fsi-pp-pipeline-spn-secret'   -AsPlainText)
# $tenantId = (Get-Secret -Name 'fsi-tenant-id'                -AsPlainText)
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

> **Sovereign-cloud note:** For GCC, GCC High, and DoD tenants, override the endpoint via `Add-PowerAppsAccount -Endpoint usgov` (GCC), `usgovhigh`, or `dod`. See the FSI PowerShell baseline for the canonical endpoint table.

---

## 1. Solution Export

> **Note:** Copilot Studio solution exports include topics, agent metadata, and packaged knowledge sources. Externally hosted knowledge sources, files referenced by URL, and tenant-level connector configurations are **not** part of the solution boundary and must be captured in a parallel inventory.

```powershell
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)] [string] $EnvironmentUrl,
    [Parameter(Mandatory = $true)] [string] $SolutionUniqueName,
    [Parameter(Mandatory = $true)] [string] $OutputDirectory,
    [switch] $Managed
)

$ErrorActionPreference = 'Stop'

$conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -Interactive
$suffix = if ($Managed) { '_managed' } else { '_unmanaged' }
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outFile = Join-Path $OutputDirectory ("{0}{1}_{2}.zip" -f $SolutionUniqueName, $suffix, $timestamp)

if ($PSCmdlet.ShouldProcess($EnvironmentUrl, "Export solution $SolutionUniqueName to $outFile")) {
    Export-CrmSolution -conn $conn -SolutionName $SolutionUniqueName -SolutionFilePath $outFile -Managed:$Managed.IsPresent
    $hash = (Get-FileHash -Path $outFile -Algorithm SHA256).Hash
    [PSCustomObject]@{
        SolutionName = $SolutionUniqueName
        File         = $outFile
        Managed      = [bool]$Managed
        SizeBytes    = (Get-Item $outFile).Length
        SHA256       = $hash
        ExportedAt   = (Get-Date).ToString('o')
        ExportedBy   = $env:USERNAME
    } | ConvertTo-Json -Depth 4 | Out-File -FilePath ($outFile + '.evidence.json') -Encoding utf8
    Write-Output "Exported $outFile (SHA256 $hash)"
}
```

The `.evidence.json` sidecar is the artifact you commit to source control alongside the solution zip; the SHA-256 hash supports SEC 17a-4 integrity expectations for retained records.

---

## 2. Solution Import

```powershell
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)] [string] $TargetEnvironmentUrl,
    [Parameter(Mandatory = $true)] [string] $SolutionFilePath,
    [string] $ChangeRequestId
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path $SolutionFilePath)) { throw "Solution file not found: $SolutionFilePath" }

# Verify hash against evidence sidecar before import
$evidencePath = "$SolutionFilePath.evidence.json"
if (Test-Path $evidencePath) {
    $evidence = Get-Content $evidencePath -Raw | ConvertFrom-Json
    $currentHash = (Get-FileHash -Path $SolutionFilePath -Algorithm SHA256).Hash
    if ($currentHash -ne $evidence.SHA256) {
        throw "Hash mismatch for $SolutionFilePath. Expected $($evidence.SHA256), got $currentHash. Aborting import."
    }
}

$conn = Connect-CrmOnline -ServerUrl $TargetEnvironmentUrl -Interactive

if ($PSCmdlet.ShouldProcess($TargetEnvironmentUrl, "Import $SolutionFilePath (CR $ChangeRequestId)")) {
    # Microsoft.Xrm.Tooling.CrmConnector.PowerShell v3.3+ required for async
    $job = Import-CrmSolutionAsync -conn $conn -SolutionFilePath $SolutionFilePath `
        -OverwriteUnmanagedCustomizations $true -PublishWorkflows $true
    Write-Output "Import job started: $($job.ImportJobId) for CR $ChangeRequestId"
    return $job
}
```

> **Verify the module version** before running: `Get-Module Microsoft.Xrm.Tooling.CrmConnector.PowerShell -ListAvailable`. If `Import-CrmSolutionAsync` is unavailable, fall back to the synchronous `Import-CrmSolution` cmdlet.

---

## 3. Solution Version Management

```powershell
function Get-FsiSolutionVersion {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)] [string] $EnvironmentUrl,
        [Parameter(Mandatory = $true)] [string] $SolutionUniqueName
    )
    $conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -Interactive
    $rec = Get-CrmRecords -conn $conn -EntityLogicalName solution `
        -FilterAttribute uniquename -FilterOperator eq -FilterValue $SolutionUniqueName -Fields version
    if (-not $rec.CrmRecords) { throw "Solution not found: $SolutionUniqueName" }
    return $rec.CrmRecords[0].version
}

function Set-FsiSolutionVersion {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory = $true)] [string] $EnvironmentUrl,
        [Parameter(Mandatory = $true)] [string] $SolutionUniqueName,
        [Parameter(Mandatory = $true)] [string] $NewVersion
    )
    if ($NewVersion -notmatch '^\d+\.\d+\.\d+\.\d+$') {
        throw "Version must be in [Major].[Minor].[Build].[Revision] format. Got: $NewVersion"
    }
    $conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -Interactive
    $rec = Get-CrmRecords -conn $conn -EntityLogicalName solution `
        -FilterAttribute uniquename -FilterOperator eq -FilterValue $SolutionUniqueName -Fields solutionid
    $solutionId = $rec.CrmRecords[0].solutionid
    if ($PSCmdlet.ShouldProcess("$SolutionUniqueName ($EnvironmentUrl)", "Set version to $NewVersion")) {
        Set-CrmRecord -conn $conn -EntityLogicalName solution -Fields @{
            solutionid = $solutionId
            version    = $NewVersion
        }
    }
}
```

**Conventions:**

- `Major.Minor` — incremented for documented business changes; mapped to a CAB-approved change record
- `Build` — incremented on every successful Dev export
- `Revision` — incremented on every pipeline run; provides a unique deployment artifact identifier

---

## 4. Configuration Snapshot

Capture the agent's current configuration **before** every change. The snapshot is the rollback reference for in-place changes and the diff baseline for solution-packaged changes.

```powershell
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)] [string] $AgentId,
    [Parameter(Mandatory = $true)] [string] $ChangeRequestId,
    [string] $OutputRoot = '.\agent-snapshots'
)

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$snapshotDir = Join-Path $OutputRoot (Join-Path $AgentId $timestamp)
if ($PSCmdlet.ShouldProcess($snapshotDir, 'Create snapshot directory')) {
    New-Item -ItemType Directory -Path $snapshotDir -Force | Out-Null
}

# Replace the placeholder values below with calls to your inventory source
# (Copilot Studio export, Dataverse query, or Graph beta agent endpoints).
$snapshot = [ordered]@{
    metadata = [ordered]@{
        agentId          = $AgentId
        changeRequestId  = $ChangeRequestId
        snapshotDate     = (Get-Date).ToString('o')
        snapshotBy       = $env:USERNAME
        tenantId         = $env:AZURE_TENANT_ID
    }
    configuration = [ordered]@{
        systemPrompt        = '<<populate from Copilot Studio export>>'
        topics              = @()
        knowledgeSources    = @()
        connectors          = @()
        actions             = @()
        settings            = [ordered]@{
            authenticationMode  = '<<populate>>'
            fallbackBehavior    = '<<populate>>'
            contentModeration   = '<<populate>>'
            sharingScope        = '<<populate>>'
        }
    }
}

$snapshotFile = Join-Path $snapshotDir 'agent-config.json'
$snapshot | ConvertTo-Json -Depth 12 | Out-File -FilePath $snapshotFile -Encoding utf8

$hash = (Get-FileHash -Path $snapshotFile -Algorithm SHA256).Hash
$evidence = [ordered]@{
    AgentId          = $AgentId
    ChangeRequestId  = $ChangeRequestId
    SnapshotFile     = $snapshotFile
    SHA256           = $hash
    CapturedAt       = (Get-Date).ToString('o')
}
$evidence | ConvertTo-Json | Out-File -FilePath ($snapshotFile + '.evidence.json') -Encoding utf8

Write-Output "Snapshot: $snapshotFile (SHA256 $hash)"
Write-Output 'Commit the snapshot directory to source control before proceeding with the change.'
```

---

## 5. Microsoft 365 Message Center — Delta Pull

Use the Microsoft Graph **Service Communications API** to pull Message Center messages on a schedule. Delta queries return only changes since the last poll, which keeps load low and supports near-real-time triage.

```powershell
[CmdletBinding()]
param(
    [string] $StateFile = '.\.message-center-delta.txt',
    [string[]] $Services = @('Microsoft Copilot', 'Power Platform', 'Power Automate', 'Common Data Service', 'SharePoint Online')
)

# Connect with delegated or app-only context. ServiceMessage.Read.All is required.
Connect-MgGraph -Scopes 'ServiceMessage.Read.All' -NoWelcome

$baseUri = 'https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/messages'
$uri = if (Test-Path $StateFile) { Get-Content $StateFile -Raw } else { "$baseUri/delta" }

$results = @()
do {
    $page = Invoke-MgGraphRequest -Method GET -Uri $uri
    if ($page.value) { $results += $page.value }
    $uri = $page.'@odata.nextLink'
} while ($uri)

if ($page.'@odata.deltaLink') {
    $page.'@odata.deltaLink' | Out-File -FilePath $StateFile -Encoding ascii
}

$relevant = $results | Where-Object {
    $msg = $_
    ($msg.services | Where-Object { $Services -contains $_ }).Count -gt 0
}

$relevant | ForEach-Object {
    [PSCustomObject]@{
        Id           = $_.id
        Title        = $_.title
        Severity     = $_.severity
        Category     = $_.category
        ActionType   = $_.actionType
        Services     = ($_.services -join ', ')
        StartDate    = $_.startDateTime
        EndDate      = $_.endDateTime
        LastModified = $_.lastModifiedDateTime
        WebUrl       = $_.viewPointBy.WebUrl
    }
} | ConvertTo-Json -Depth 5
```

Route the relevant messages into your change-intake queue (Dataverse table, ServiceNow, or Azure DevOps work items). See the [Message Center Monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor) companion solution for a production implementation.

---

## 6. Orchestrator: End-to-End Pipeline Deployment

```powershell
function Invoke-FsiPipelineDeployment {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory = $true)] [string] $SolutionUniqueName,
        [Parameter(Mandatory = $true)] [string] $SourceEnvironmentUrl,
        [Parameter(Mandatory = $true)] [string] $TargetEnvironmentUrl,
        [Parameter(Mandatory = $true)] [ValidateSet('Zone1', 'Zone2', 'Zone3')] [string] $TargetZone,
        [Parameter(Mandatory = $true)] [string] $ChangeRequestId,
        [string] $LogRoot = 'C:\Logs\FSI-Deployments'
    )

    $ErrorActionPreference = 'Stop'
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    if (-not (Test-Path $LogRoot)) { New-Item -ItemType Directory -Path $LogRoot | Out-Null }
    $logFile = Join-Path $LogRoot ("Deploy_{0}_{1}.log" -f $SolutionUniqueName, $timestamp)

    function Write-Log { param($m) "$((Get-Date).ToString('o')) $m" | Tee-Object -FilePath $logFile -Append }

    Write-Log "Start: CR=$ChangeRequestId Zone=$TargetZone Source=$SourceEnvironmentUrl Target=$TargetEnvironmentUrl"

    try {
        # 1. Increment Build version in source
        $current = Get-FsiSolutionVersion -EnvironmentUrl $SourceEnvironmentUrl -SolutionUniqueName $SolutionUniqueName
        $parts = $current.Split('.')
        if ($parts.Count -ne 4) { throw "Source version must be 4-part. Got: $current" }
        $parts[2] = [int]$parts[2] + 1
        $next = $parts -join '.'
        Set-FsiSolutionVersion -EnvironmentUrl $SourceEnvironmentUrl -SolutionUniqueName $SolutionUniqueName -NewVersion $next
        Write-Log "Version $current -> $next"

        # 2. Export managed
        $exportDir = Join-Path $LogRoot 'artifacts'
        if (-not (Test-Path $exportDir)) { New-Item -ItemType Directory -Path $exportDir | Out-Null }
        & "$PSScriptRoot\Export-FsiSolution.ps1" -EnvironmentUrl $SourceEnvironmentUrl `
            -SolutionUniqueName $SolutionUniqueName -OutputDirectory $exportDir -Managed
        $exported = Get-ChildItem -Path $exportDir -Filter "${SolutionUniqueName}_managed_*.zip" |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        Write-Log "Exported: $($exported.FullName)"

        # 3. Zone 3 explicit pause for delegated-deployment / CAB acknowledgement
        if ($TargetZone -eq 'Zone3') {
            Write-Log 'Zone 3: pausing for delegated-deployment approval. Approval is captured by the Power Automate flow.'
            # In CI, this script should hand off to the pipeline approval gate
            # rather than block locally.
        }

        # 4. Import to target
        if ($PSCmdlet.ShouldProcess($TargetEnvironmentUrl, "Import $($exported.Name)")) {
            & "$PSScriptRoot\Import-FsiSolution.ps1" -TargetEnvironmentUrl $TargetEnvironmentUrl `
                -SolutionFilePath $exported.FullName -ChangeRequestId $ChangeRequestId
            Write-Log 'Import requested.'
        }

        # 5. Verify deployed version
        Start-Sleep -Seconds 30
        $deployed = Get-FsiSolutionVersion -EnvironmentUrl $TargetEnvironmentUrl -SolutionUniqueName $SolutionUniqueName
        if ($deployed -ne $next) {
            Write-Log "WARN: deployed=$deployed expected=$next"
        } else {
            Write-Log "PASS: deployed=$deployed"
        }

        return [PSCustomObject]@{
            Success         = $true
            Version         = $next
            ChangeRequestId = $ChangeRequestId
            ArtifactPath    = $exported.FullName
            LogFile         = $logFile
        }
    } catch {
        Write-Log "FAIL: $($_.Exception.Message)"
        Write-Log 'Rollback may be required. See verification-testing.md for the rollback runbook.'
        return [PSCustomObject]@{
            Success         = $false
            Error           = $_.Exception.Message
            LogFile         = $logFile
        }
    }
}
```

> **CI/CD note:** In a production pipeline (Azure DevOps, GitHub Actions), the explicit Zone 3 pause should be replaced by the pipeline platform's own approval gate so the orchestrator does not block on interactive input. The Power Automate `OnApprovalStarted` flow remains authoritative for the change record.

---

## 7. List Solution Components (Inventory)

```powershell
function Get-FsiSolutionComponents {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)] [string] $EnvironmentUrl,
        [Parameter(Mandatory = $true)] [string] $SolutionUniqueName
    )
    $conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -Interactive
    $sol = Get-CrmRecords -conn $conn -EntityLogicalName solution `
        -FilterAttribute uniquename -FilterOperator eq -FilterValue $SolutionUniqueName -Fields solutionid
    $solutionId = $sol.CrmRecords[0].solutionid

    $components = Get-CrmRecords -conn $conn -EntityLogicalName solutioncomponent `
        -FilterAttribute solutionid -FilterOperator eq -FilterValue $solutionId `
        -Fields componenttype, objectid, rootcomponentbehavior

    $typeMap = @{
        1     = 'Entity'; 2 = 'Attribute'; 3 = 'Relationship'; 9 = 'OptionSet'
        29    = 'Workflow'; 59 = 'SystemForm'; 60 = 'WebResource'; 80 = 'ModelDrivenApp'
        300   = 'CanvasApp'; 371 = 'Connector'; 372 = 'EnvironmentVariableDefinition'
        380   = 'AIModel'; 10029 = 'CopilotStudioAgent'
    }

    $components.CrmRecords | ForEach-Object {
        [PSCustomObject]@{
            Type     = if ($typeMap.ContainsKey($_.componenttype)) { $typeMap[$_.componenttype] } else { "Type$($_.componenttype)" }
            ObjectId = $_.objectid
            Behavior = $_.rootcomponentbehavior
        }
    }
}
```

Use this inventory to confirm that every Copilot Studio agent (`componenttype = 10029`) and its associated topics, connectors, and environment variables are present in the solution before export.

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md) — PPAC and Copilot Studio configuration
- [Verification & Testing](verification-testing.md) — Evidence collection, rollback drills, A/B testing
- [Troubleshooting](troubleshooting.md) — Common failures with pipelines, approvals, and delegated deployments

---

*Updated: April 2026 | Version: v1.4.0*
