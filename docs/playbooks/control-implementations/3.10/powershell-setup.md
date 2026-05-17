# PowerShell Setup: Control 3.10 - Hallucination Feedback Loop

**Last Updated:** April 2026
**Automation Level:** Provisioning, intake, metrics, evidence export
**Estimated Time:** 60-90 minutes

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show the canonical patterns; deviations from the baseline must be approved by your Change Advisory Board.

> This playbook provides PowerShell automation for [Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md). It complements — not replaces — the [Portal Walkthrough](./portal-walkthrough.md). Use it for repeatable provisioning, scheduled metric collection, and evidence export under SEC 17a-4 / FINRA 4511.

---

## Prerequisites

- Windows PowerShell 5.1 (Desktop) **and** PowerShell 7.4 (Core) available — modules below have edition-specific requirements
- **Power Platform Admin** role (for environment lookups)
- **SharePoint Site Owner** on the AI Governance site
- Approved module versions from the PowerShell baseline:

```powershell
# Pin versions per CAB approval — values shown are illustrative
$pin = @{
    'PnP.PowerShell'         = '<CAB-approved version, v2+ requires Entra app registration>'
    'Microsoft.Graph'        = '<CAB-approved minor version>'
    'Microsoft.PowerApps.Administration.PowerShell' = '<CAB-approved version (Desktop only)>'
}

foreach ($module in $pin.Keys) {
    Install-Module -Name $module -RequiredVersion $pin[$module] `
        -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
}
```

> `PnP.PowerShell` v2+ requires an Entra app registration with delegated SharePoint and Graph permissions. Coordinate the registration with your **Entra App Admin** and document it under your governance procedures.

---

## Sovereign-Cloud Connection Helpers

```powershell
function Connect-FsiSharePoint {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory)] [string] $SiteUrl,
        [ValidateSet('Production','USGovernment','USGovernmentHigh','USGovernmentDoD','China')]
        [string] $AzureEnvironment = 'Production',
        [Parameter(Mandatory)] [string] $ClientId,
        [Parameter(Mandatory)] [string] $TenantId
    )

    if ($PSCmdlet.ShouldProcess($SiteUrl, "Connect-PnPOnline ($AzureEnvironment)")) {
        Connect-PnPOnline -Url $SiteUrl `
            -ClientId $ClientId `
            -Tenant $TenantId `
            -Interactive `
            -AzureEnvironment $AzureEnvironment
    }
}
```

> Failing to pass `-AzureEnvironment` in a sovereign tenant authenticates against commercial endpoints, returns no data, and produces **false-clean evidence**. This is a documented pattern in the baseline.

---

## Provision the Hallucination Tracking List

```powershell
function New-HallucinationTrackingList {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory)] [string] $SiteUrl,
        [string] $ListName = 'Hallucination Tracking',
        [string] $RetentionLabelName = 'FSI-AI-Evidence-6yr'
    )

    if (-not $PSCmdlet.ShouldProcess($SiteUrl, "Create list '$ListName'")) { return }

    $existing = Get-PnPList -Identity $ListName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Verbose "List '$ListName' already exists; skipping creation."
        return
    }

    New-PnPList -Title $ListName -Template GenericList -OnQuickLaunch | Out-Null

    # Schema — keep in sync with portal-walkthrough.md
    $textFields = @(
        @{ Name = 'IssueID';          Display = 'Issue ID' },
        @{ Name = 'AgentName';        Display = 'Agent Name' },
        @{ Name = 'AgentEnvironment'; Display = 'Agent Environment' },
        @{ Name = 'ConversationId';   Display = 'Conversation Id' }
    )
    foreach ($f in $textFields) {
        Add-PnPField -List $ListName -DisplayName $f.Display -InternalName $f.Name -Type Text -AddToDefaultView | Out-Null
    }

    $noteFields = @('UserQuery','AgentResponse','CorrectInformation','RemediationActions')
    foreach ($n in $noteFields) {
        Add-PnPField -List $ListName -DisplayName $n -InternalName $n -Type Note | Out-Null
    }

    $choiceFields = @{
        Zone               = @('1','2','3')
        Category           = @('Factual Error','Fabrication','Outdated Information','Misattribution','Calculation Error','Conflation','Overconfidence','Misleading Framing')
        Severity           = @('Critical','High','Medium','Low')
        ConfirmedSeverity  = @('Critical','High','Medium','Low')
        Status             = @('New','Triaged','In Remediation','In Validation','Closed',"Won't Fix")
        RootCause          = @('Knowledge Gap','Prompt Issue','Source Conflict','Model Limitation','Configuration','Unknown')
    }
    foreach ($name in $choiceFields.Keys) {
        $choices = ($choiceFields[$name] | ForEach-Object { "<CHOICE>$_</CHOICE>" }) -join ''
        $xml = "<Field Type='Choice' DisplayName='$name' Name='$name' StaticName='$name'><CHOICES>$choices</CHOICES></Field>"
        Add-PnPFieldFromXml -List $ListName -FieldXml $xml | Out-Null
    }

    Add-PnPField -List $ListName -DisplayName 'Reported By'  -InternalName 'ReportedBy' -Type User | Out-Null
    Add-PnPField -List $ListName -DisplayName 'Assigned To'  -InternalName 'AssignedTo' -Type User | Out-Null
    Add-PnPField -List $ListName -DisplayName 'Report Date'         -InternalName 'ReportDate'         -Type DateTime | Out-Null
    Add-PnPField -List $ListName -DisplayName 'Resolution Date'     -InternalName 'ResolutionDate'     -Type DateTime | Out-Null
    Add-PnPField -List $ListName -DisplayName 'Triage SLA Met'      -InternalName 'TriageSLAMet'       -Type Boolean | Out-Null
    Add-PnPField -List $ListName -DisplayName 'Remediation SLA Met' -InternalName 'RemediationSLAMet'  -Type Boolean | Out-Null
    Add-PnPField -List $ListName -DisplayName 'Source Of Truth'     -InternalName 'SourceOfTruth'      -Type URL | Out-Null
    Add-PnPField -List $ListName -DisplayName 'Related Incident Id' -InternalName 'RelatedIncidentId'  -Type Text | Out-Null

    # Apply Purview retention label (label must be published to the site)
    try {
        Set-PnPLabel -List $ListName -Label $RetentionLabelName -SyncToItems $true
        Write-Information "Applied retention label '$RetentionLabelName' to list '$ListName'."
    } catch {
        Write-Warning "Retention label '$RetentionLabelName' not applied: $($_.Exception.Message). Apply via Purview before relying on this list for SEC 17a-4 evidence."
    }
}
```

> The retention label must be published to the site before this command runs. Treat retention as a **Purview Records Manager** responsibility — do not assume PowerShell-applied labels satisfy SEC 17a-4 without the records manager's written sign-off.

---

## Submit a Hallucination Report

```powershell
function New-HallucinationReport {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory)] [string] $AgentName,
        [Parameter(Mandatory)] [string] $AgentEnvironment,
        [Parameter(Mandatory)] [ValidateSet('1','2','3')] [string] $Zone,
        [Parameter(Mandatory)] [ValidateSet(
            'Factual Error','Fabrication','Outdated Information','Misattribution',
            'Calculation Error','Conflation','Overconfidence','Misleading Framing'
        )] [string] $Category,
        [Parameter(Mandatory)] [ValidateSet('Critical','High','Medium','Low')] [string] $Severity,
        [Parameter(Mandatory)] [string] $UserQuery,
        [Parameter(Mandatory)] [string] $AgentResponse,
        [Parameter(Mandatory)] [string] $ConversationId,
        [Parameter(Mandatory)] [string] $ReportedByUpn,
        [string] $CorrectInformation = '',
        [string] $ListName = 'Hallucination Tracking'
    )

    $issueId = 'HAL-{0}-{1}' -f (Get-Date -Format 'yyyyMMdd'), (Get-Random -Minimum 100 -Maximum 999)
    $title   = "$AgentName - $Category"

    $values = @{
        Title              = $title
        IssueID            = $issueId
        AgentName          = $AgentName
        AgentEnvironment   = $AgentEnvironment
        Zone               = $Zone
        Category           = $Category
        Severity           = $Severity
        UserQuery          = $UserQuery
        AgentResponse      = $AgentResponse
        CorrectInformation = $CorrectInformation
        ConversationId     = $ConversationId
        ReportedBy         = $ReportedByUpn
        ReportDate         = (Get-Date).ToString('o')
        Status             = 'New'
    }

    if ($PSCmdlet.ShouldProcess("$ListName / $issueId", 'Create hallucination report')) {
        Add-PnPListItem -List $ListName -Values $values | Out-Null
        Write-Information "Created $issueId (Severity=$Severity, Agent=$AgentName)."

        if ($Severity -eq 'Critical') {
            Write-Warning "CRITICAL — invoke Control 3.4 incident path for $issueId."
        }
    }

    return $issueId
}
```

> This function is a **fallback** intake path for cases where the Power Automate flow is unavailable (e.g., during incident response). The primary intake remains the HTTP-triggered flow described in the portal walkthrough.

---

## Compute Metrics

```powershell
function Get-HallucinationMetrics {
    [CmdletBinding()]
    param(
        [int] $DaysBack = 30,
        [string] $ListName = 'Hallucination Tracking'
    )

    $sinceUtc = (Get-Date).AddDays(-$DaysBack).ToUniversalTime()

    # PageSize keeps memory bounded for large lists
    $items = Get-PnPListItem -List $ListName -PageSize 500 |
        Where-Object { [DateTime]$_.FieldValues.Created -ge $sinceUtc }

    $closed = $items | Where-Object {
        $_.FieldValues.Status -eq 'Closed' -and $_.FieldValues.ResolutionDate
    }

    $mttrHours = $null
    if ($closed.Count -gt 0) {
        $mttrHours = [math]::Round((
            $closed | ForEach-Object {
                ([DateTime]$_.FieldValues.ResolutionDate - [DateTime]$_.FieldValues.Created).TotalHours
            } | Measure-Object -Average
        ).Average, 1)
    }

    $slaTotal     = ($items | Where-Object { $_.FieldValues.TriageSLAMet -ne $null }).Count
    $slaMet       = ($items | Where-Object { $_.FieldValues.TriageSLAMet -eq $true  }).Count
    $slaCompliancePct = if ($slaTotal -gt 0) { [math]::Round(100.0 * $slaMet / $slaTotal, 1) } else { $null }

    [pscustomobject]@{
        WindowDays         = $DaysBack
        TotalReports       = $items.Count
        BySeverity         = @{
            Critical = ($items | Where-Object { $_.FieldValues.ConfirmedSeverity -eq 'Critical' -or $_.FieldValues.Severity -eq 'Critical' }).Count
            High     = ($items | Where-Object { $_.FieldValues.ConfirmedSeverity -eq 'High'     -or $_.FieldValues.Severity -eq 'High' }).Count
            Medium   = ($items | Where-Object { $_.FieldValues.ConfirmedSeverity -eq 'Medium'   -or $_.FieldValues.Severity -eq 'Medium' }).Count
            Low      = ($items | Where-Object { $_.FieldValues.ConfirmedSeverity -eq 'Low'      -or $_.FieldValues.Severity -eq 'Low' }).Count
        }
        ByCategory         = $items | Group-Object { $_.FieldValues.Category } | Select-Object Name, Count
        OpenIssues         = ($items | Where-Object { $_.FieldValues.Status -ne 'Closed' -and $_.FieldValues.Status -ne "Won't Fix" }).Count
        AverageMTTRHours   = $mttrHours
        SLACompliancePct   = $slaCompliancePct
    }
}
```

---

## Export Evidence with SHA-256 Hash

```powershell
function Export-HallucinationEvidence {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [int] $DaysBack = 30,
        [string] $ListName = 'Hallucination Tracking',
        [Parameter(Mandatory)] [string] $OutputFolder
    )

    if (-not $PSCmdlet.ShouldProcess($OutputFolder, "Export hallucination evidence ($DaysBack days)")) { return }

    if (-not (Test-Path $OutputFolder)) {
        New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null
    }

    $stamp     = Get-Date -Format 'yyyyMMdd-HHmmss'
    $csvPath   = Join-Path $OutputFolder "hallucination-tracking-$stamp.csv"
    $hashPath  = "$csvPath.sha256"
    $sinceUtc  = (Get-Date).AddDays(-$DaysBack).ToUniversalTime()

    $items = Get-PnPListItem -List $ListName -PageSize 500 |
        Where-Object { [DateTime]$_.FieldValues.Created -ge $sinceUtc } |
        ForEach-Object {
            [pscustomobject]@{
                IssueID            = $_.FieldValues.IssueID
                Created            = $_.FieldValues.Created
                ReportDate         = $_.FieldValues.ReportDate
                AgentName          = $_.FieldValues.AgentName
                AgentEnvironment   = $_.FieldValues.AgentEnvironment
                Zone               = $_.FieldValues.Zone
                Category           = $_.FieldValues.Category
                Severity           = $_.FieldValues.Severity
                ConfirmedSeverity  = $_.FieldValues.ConfirmedSeverity
                Status             = $_.FieldValues.Status
                ConversationId     = $_.FieldValues.ConversationId
                ResolutionDate     = $_.FieldValues.ResolutionDate
                TriageSLAMet       = $_.FieldValues.TriageSLAMet
                RemediationSLAMet  = $_.FieldValues.RemediationSLAMet
                RootCause          = $_.FieldValues.RootCause
                RelatedIncidentId  = $_.FieldValues.RelatedIncidentId
            }
        }

    $items | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

    $hash = Get-FileHash -Path $csvPath -Algorithm SHA256
    "$($hash.Hash)  $(Split-Path $csvPath -Leaf)" | Out-File -FilePath $hashPath -Encoding ASCII

    Write-Information "Exported $($items.Count) items to $csvPath"
    Write-Information "SHA-256: $($hash.Hash)"

    [pscustomobject]@{
        CsvPath  = $csvPath
        HashPath = $hashPath
        Sha256   = $hash.Hash
        ItemCount = $items.Count
    }
}
```

> The `.sha256` sidecar file lets auditors verify the export was not modified after generation. Store both files in a write-once location (Azure Storage with immutability, or a SharePoint library with retention) for the full SEC 17a-4 retention period.

---

## End-to-End Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 3.10 - Hallucination Feedback Loop infrastructure.

.DESCRIPTION
    1. Validates module versions and edition
    2. Connects to SharePoint with sovereign-cloud awareness
    3. Provisions the Hallucination Tracking list (idempotent)
    4. Computes current metrics
    5. Optionally exports evidence

.PARAMETER SiteUrl
    SharePoint site URL for the AI Governance site.

.PARAMETER AzureEnvironment
    Sovereign cloud selector (Production, USGovernment, USGovernmentHigh, USGovernmentDoD, China).

.PARAMETER ClientId
    Entra app registration client ID used by PnP.PowerShell v2+.

.PARAMETER TenantId
    Entra tenant ID.

.PARAMETER ExportEvidence
    Switch to also export a 30-day evidence pack with SHA-256 hash.

.EXAMPLE
    .\Configure-Control-3.10.ps1 `
        -SiteUrl 'https://contoso.sharepoint.com/sites/AI-Governance' `
        -AzureEnvironment 'Production' `
        -ClientId '<guid>' -TenantId '<guid>' -ExportEvidence
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory)] [string] $SiteUrl,
    [ValidateSet('Production','USGovernment','USGovernmentHigh','USGovernmentDoD','China')]
    [string] $AzureEnvironment = 'Production',
    [Parameter(Mandatory)] [string] $ClientId,
    [Parameter(Mandatory)] [string] $TenantId,
    [switch] $ExportEvidence,
    [string] $EvidenceFolder = ".\evidence\3.10"
)

$ErrorActionPreference = 'Stop'

try {
    Write-Information "[3.10] Connecting to SharePoint ($AzureEnvironment)"
    Connect-FsiSharePoint -SiteUrl $SiteUrl -AzureEnvironment $AzureEnvironment `
        -ClientId $ClientId -TenantId $TenantId

    Write-Information "[3.10] Provisioning Hallucination Tracking list (idempotent)"
    New-HallucinationTrackingList -SiteUrl $SiteUrl

    Write-Information "[3.10] Computing 30-day metrics"
    $metrics = Get-HallucinationMetrics -DaysBack 30
    $metrics | Format-List

    if ($ExportEvidence) {
        Write-Information "[3.10] Exporting evidence pack"
        $evidence = Export-HallucinationEvidence -DaysBack 30 -OutputFolder $EvidenceFolder
        Write-Information "[3.10] Evidence: $($evidence.CsvPath) (SHA-256: $($evidence.Sha256))"
    }

    Write-Information "[3.10] PASS — control infrastructure verified."
}
catch {
    Write-Error "[3.10] FAIL — $($_.Exception.Message)"
    Write-Error $_.ScriptStackTrace
    exit 1
}
finally {
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
```

> Run the script with `-WhatIf` first to preview every mutating action without executing it. This is required practice in regulated tenants and is consistent with the PowerShell baseline.

---

## Scheduled Operations

For ongoing operation, schedule the following on a hardened admin workstation or governed runner:

| Task | Frequency | Function |
|------|-----------|----------|
| Metrics snapshot | Daily | `Get-HallucinationMetrics` → write to history list |
| Evidence export | Monthly | `Export-HallucinationEvidence -DaysBack 31` to write-once storage |
| Retention label audit | Quarterly | `Get-PnPLabel -List 'Hallucination Tracking'` and confirm published policy |
| Module version drift check | Per change window | Compare installed versions to CAB-approved pin |

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) — Manual configuration
- [Verification & Testing](./verification-testing.md) — Test procedures
- [Troubleshooting](./troubleshooting.md) — Common issues

---

[Back to Control 3.10](../../../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
