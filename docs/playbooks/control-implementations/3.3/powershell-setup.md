# PowerShell Setup: Control 3.3 - Compliance and Regulatory Reporting

**Last Updated:** April 2026

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show the framework's required patterns.

> Automation scripts for [Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md). All scripts are designed to be **read-only against tenant data** (collection only) or to write only to **scoped SharePoint locations** under explicit `-WhatIf` support.

---

## Prerequisites

### Modules (pinned per FSI baseline §1)

```powershell
# REQUIRED: substitute <version> with the version approved by your CAB.
# Do NOT use -Force without -RequiredVersion in regulated tenants.

Install-Module -Name Microsoft.Graph                  -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name ExchangeOnlineManagement         -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
Install-Module -Name PnP.PowerShell                   -RequiredVersion '<version>' -Repository PSGallery -Scope CurrentUser -AllowClobber -AcceptLicense
```

### PowerShell edition guards

```powershell
# PnP.PowerShell v2+ requires PowerShell 7
if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion.Major -lt 7) {
    throw "PnP.PowerShell v2+ requires PowerShell 7 (Core). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
```

### Sovereign-aware connections

```powershell
param(
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
    [string]$Cloud = 'Commercial',
    [Parameter(Mandatory=$true)][string]$TenantId,
    [Parameter(Mandatory=$true)][string]$SharePointSiteUrl
)

$graphEnv = switch ($Cloud) {
    'Commercial' { 'Global'    }
    'GCC'        { 'USGov'     }
    'GCCHigh'    { 'USGovDoD'  }   # verify per Microsoft Learn for your tenant
    'DoD'        { 'USGovDoD'  }
}

# Required Graph scopes — request only the minimum
Connect-MgGraph -Environment $graphEnv -TenantId $TenantId -Scopes @(
    'SecurityEvents.Read.All',
    'ComplianceManager.Read.All',
    'Reports.Read.All',
    'AuditLog.Read.All'
) -NoWelcome

Connect-PnPOnline -Url $SharePointSiteUrl -Interactive
```

> **False-clean evidence risk:** Failing to pass the correct `-Environment` against a sovereign tenant returns zero results without error. Always log the resolved environment in your evidence emission (see §6).

---

## 1. Compliance Manager Assessment Score Collector

Pulls current assessment scores via Microsoft Graph and writes a normalized snapshot. **Read-only**.

```powershell
function Get-ComplianceManagerSnapshot {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$OutputPath
    )

    Write-Verbose "Collecting Compliance Manager assessment snapshot..."

    # The Compliance Manager Graph beta surface evolves; check current docs:
    # https://learn.microsoft.com/en-us/graph/api/resources/security-api-overview
    # If the Graph endpoint is unavailable in your tenant, fall back to the
    # Compliance Manager portal CSV export (Compliance Manager > Assessments > Export).
    $snapshot = [PSCustomObject]@{
        CollectedAt    = (Get-Date).ToString('o')
        Tenant         = (Get-MgContext).TenantId
        GraphEnvironment = (Get-MgContext).Environment
        Source         = 'Microsoft Graph (beta) / Compliance Manager portal export'
        Assessments    = @()
        Note           = 'Replace this collector body with your tenant-validated Graph call or CSV import.'
    }

    $snapshot | ConvertTo-Json -Depth 6 | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Output $snapshot
}
```

> **Why this is a stub:** the Compliance Manager Graph surface is in flux as of April 2026. Hardcoding fictional scores would create **false-clean evidence**, which is the opposite of what regulators want to see. This script intentionally collects context and points the operator at the portal CSV export.

---

## 2. FSI-AgentGov Control Status Collector

Reads control status from a SharePoint list (the canonical source of truth for FSI control attestations). **Read-only**.

```powershell
function Get-FSIControlStatus {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$ListName,    # e.g., 'FSI-Control-Status'
        [Parameter(Mandatory=$true)][string]$OutputPath
    )

    Write-Verbose "Reading control status from SharePoint list '$ListName'..."

    $items = Get-PnPListItem -List $ListName -PageSize 1000 |
        ForEach-Object {
            [PSCustomObject]@{
                ControlId   = $_.FieldValues.ControlId
                Pillar      = $_.FieldValues.Pillar
                Status      = $_.FieldValues.Status        # Compliant / Needs Attention / Non-Compliant
                LastReview  = $_.FieldValues.LastReview
                Owner       = $_.FieldValues.Owner.LookupValue
                EvidenceUrl = $_.FieldValues.EvidenceUrl
            }
        }

    $snapshot = [PSCustomObject]@{
        CollectedAt = (Get-Date).ToString('o')
        SourceList  = $ListName
        ItemCount   = $items.Count
        Items       = $items
    }

    $snapshot | ConvertTo-Json -Depth 5 | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Output $snapshot
}
```

---

## 3. Regulatory Alignment Snapshot

Builds a regulation-by-control coverage matrix from a maintained mapping file (do not hardcode regulatory mappings in scripts).

```powershell
function Get-RegulatoryAlignmentSnapshot {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$MappingCsvPath,    # CSV: Regulation,Requirement,ControlIds
        [Parameter(Mandatory=$true)][object]$ControlStatus,     # output of Get-FSIControlStatus
        [Parameter(Mandatory=$true)][string]$OutputPath
    )

    if (-not (Test-Path $MappingCsvPath)) {
        throw "Regulatory mapping CSV not found at '$MappingCsvPath'. Maintain this mapping under change control; do not embed regulatory text in scripts."
    }

    $mappings = Import-Csv -Path $MappingCsvPath
    $statusByControl = @{}
    foreach ($item in $ControlStatus.Items) { $statusByControl[$item.ControlId] = $item.Status }

    $rows = foreach ($m in $mappings) {
        $controlIds = $m.ControlIds -split ';' | ForEach-Object { $_.Trim() }
        $statuses   = $controlIds | ForEach-Object { $statusByControl[$_] }
        $compliant  = ($statuses | Where-Object { $_ -eq 'Compliant' }).Count
        [PSCustomObject]@{
            Regulation       = $m.Regulation
            Requirement      = $m.Requirement
            MappedControls   = $controlIds -join ', '
            CompliantCount   = $compliant
            TotalCount       = $controlIds.Count
            CoveragePercent  = if ($controlIds.Count) { [math]::Round(($compliant / $controlIds.Count) * 100, 0) } else { 0 }
        }
    }

    $snapshot = [PSCustomObject]@{
        CollectedAt = (Get-Date).ToString('o')
        MappingFile = $MappingCsvPath
        Rows        = $rows
    }

    $snapshot | ConvertTo-Json -Depth 5 | Out-File -FilePath $OutputPath -Encoding UTF8
    Write-Output $snapshot
}
```

---

## 4. Examination Package Manifest Builder

Builds a manifest of expected examination package contents — does **not** copy or move documents. Operators run the resulting manifest through their evidence-collection workflow.

```powershell
function New-ExaminationManifest {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet('FINRA','SEC','OCC','State','InternalAudit')]
        [string]$Regulator,

        [Parameter(Mandatory=$true)][string]$OutputFolder
    )

    $packageContents = @{
        'FINRA' = @{
            '01-AI-Governance-Framework-Overview.pdf' = 'Framework documentation'
            '02-Agent-Inventory.xlsx'                 = 'Complete agent inventory (Control 3.1)'
            '03-Written-Supervisory-Procedures.pdf'   = 'WSP — AI agent supervision (Rule 3110)'
            '04-Control-Status-Summary.pdf'           = 'Current control compliance status'
            '05-Usage-Analytics-90-Days.xlsx'         = 'Agent usage data (Control 3.2)'
            '06-Incident-Log.xlsx'                    = 'Incident tracking log (Control 3.4)'
            '07-Training-Completion-Records.xlsx'     = 'Staff training records'
            '08-Policy-Documents/'                    = 'All AI governance policies'
            '09-Records-Retention-Attestation.pdf'    = 'Rule 4511 / 17a-4 retention attestation'
        }
        'SEC' = @{
            '01-Records-Retention-Policy.pdf'    = '17 CFR 240.17a-4 retention policy'
            '02-Agent-Interaction-Logs.xlsx'     = 'Customer interaction records'
            '03-Records-Storage-Attestation.pdf' = '17a-4(f) non-rewriteable storage attestation'
            '04-Access-Control-Documentation.pdf' = 'Access management evidence'
            '05-Audit-Trail-Export.xlsx'         = 'Unified audit log export (Control 1.7)'
            '06-RegSP-Incident-Response-Policy.pdf' = 'Regulation S-P incident response policy and 30-day notification procedure'
        }
        'OCC' = @{
            '01-Third-Party-Risk-Assessment.pdf' = 'Vendor risk documentation'
            '02-Technology-Risk-Controls.pdf'    = 'IT control documentation'
            '03-Business-Continuity-Plans.pdf'   = 'BCP documentation'
            '04-Change-Management-Evidence.xlsx' = 'Change control records'
            '05-Model-Risk-Validation.pdf'       = 'OCC 2011-12 / Fed SR 11-7 model validation evidence'
        }
        'State' = @{
            '01-State-AI-Law-Mapping.pdf' = 'Mapping of state AI laws (e.g., NYDFS, CO SB205)'
            '02-Customer-Notification-Procedures.pdf' = 'State breach notification procedures'
        }
        'InternalAudit' = @{
            '01-Quarterly-Audit-Evidence-Bundle.zip' = 'Quarterly evidence bundle'
            '02-SOX-302-Sub-Certifications.pdf'      = 'Quarterly sub-certifications'
            '03-SOX-404-IT-Controls-Evidence.pdf'    = 'Annual IT general controls evidence'
        }
    }

    if (-not $packageContents.ContainsKey($Regulator)) {
        throw "Unknown regulator: $Regulator"
    }

    if ($PSCmdlet.ShouldProcess($OutputFolder, "Create examination manifest for $Regulator")) {
        New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null

        $manifest = [PSCustomObject]@{
            Regulator      = $Regulator
            GeneratedAt    = (Get-Date).ToString('o')
            GeneratedBy    = (Get-MgContext).Account
            TenantId       = (Get-MgContext).TenantId
            Cloud          = (Get-MgContext).Environment
            Contents       = $packageContents[$Regulator]
            Instructions   = 'Operator must collect each listed item from its source-of-truth location and verify recency before submission. Do not rely on this manifest as evidence — it is a checklist.'
        }

        $manifestPath = Join-Path $OutputFolder 'MANIFEST.json'
        $manifest | ConvertTo-Json -Depth 4 | Out-File -FilePath $manifestPath -Encoding UTF8

        Write-Output $manifest
    }
}
```

---

## 5. Archive Snapshot to SharePoint Records Library

Uploads collected snapshots to the records library, applies metadata, and lets the published retention label take effect. Mutation-safe with `-WhatIf`.

```powershell
function Save-ComplianceSnapshotToSharePoint {
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)][string]$LocalPath,
        [Parameter(Mandatory=$true)][string]$LibraryPath,         # e.g., 'Weekly Reports'
        [string]$RetentionLabel = 'FSI-Compliance-Reports-3Year'
    )

    if (-not (Test-Path $LocalPath)) {
        throw "Local snapshot not found: $LocalPath"
    }

    $fileName = Split-Path $LocalPath -Leaf
    $target   = "$LibraryPath/$fileName"

    if ($PSCmdlet.ShouldProcess($target, "Upload snapshot")) {
        try {
            $uploaded = Add-PnPFile -Path $LocalPath -Folder $LibraryPath -ErrorAction Stop
            # Apply retention label (requires Records Management entitlement)
            Set-PnPListItem -List (Split-Path $LibraryPath -Leaf) -Identity $uploaded.ListItemAllFields.Id `
                -Label $RetentionLabel -ErrorAction SilentlyContinue
            Write-Verbose "Uploaded $fileName to $LibraryPath with label $RetentionLabel"
            return $uploaded
        }
        catch {
            Write-Error "Failed to upload snapshot: $_"
            throw
        }
    }
}
```

---

## 6. Evidence Emission (SHA-256 + Run Log)

Every snapshot run should emit a signed evidence row. This supports SOX 404 / OCC 2023-17 evidence requirements by making each run reproducible and tamper-evident.

```powershell
function Write-FSIEvidenceRow {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)][string]$ArtifactPath,
        [Parameter(Mandatory=$true)][string]$ControlId,        # e.g., '3.3'
        [Parameter(Mandatory=$true)][string]$RunType,          # e.g., 'Weekly'
        [Parameter(Mandatory=$true)][string]$EvidenceLogPath   # CSV append target
    )

    $hash = (Get-FileHash -Path $ArtifactPath -Algorithm SHA256).Hash
    $row  = [PSCustomObject]@{
        Timestamp        = (Get-Date).ToString('o')
        ControlId        = $ControlId
        RunType          = $RunType
        Artifact         = $ArtifactPath
        Sha256           = $hash
        TenantId         = (Get-MgContext).TenantId
        GraphEnvironment = (Get-MgContext).Environment
        Operator         = (Get-MgContext).Account
        Hostname         = $env:COMPUTERNAME
        PSVersion        = $PSVersionTable.PSVersion.ToString()
    }

    $row | Export-Csv -Path $EvidenceLogPath -Append -NoTypeInformation -Encoding UTF8
    Write-Output $row
}
```

---

## End-to-End Example (Read-Only Snapshot)

```powershell
# 1. Connect (sovereign-aware)
. .\Connect-FSI.ps1 -Cloud Commercial -TenantId '<tenant-id>' -SharePointSiteUrl 'https://contoso.sharepoint.com/sites/AI-Compliance-Reports'

# 2. Collect (read-only)
$cm    = Get-ComplianceManagerSnapshot -OutputPath '.\out\cm-snapshot.json'
$ctrls = Get-FSIControlStatus -ListName 'FSI-Control-Status' -OutputPath '.\out\controls.json'
$align = Get-RegulatoryAlignmentSnapshot -MappingCsvPath '.\config\reg-mapping.csv' -ControlStatus $ctrls -OutputPath '.\out\alignment.json'

# 3. Emit evidence
Write-FSIEvidenceRow -ArtifactPath '.\out\controls.json'  -ControlId '3.3' -RunType 'Weekly' -EvidenceLogPath '.\evidence.csv'
Write-FSIEvidenceRow -ArtifactPath '.\out\alignment.json' -ControlId '3.3' -RunType 'Weekly' -EvidenceLogPath '.\evidence.csv'

# 4. Archive (mutation; use -WhatIf first)
Save-ComplianceSnapshotToSharePoint -LocalPath '.\out\controls.json'  -LibraryPath 'Weekly Reports' -WhatIf
Save-ComplianceSnapshotToSharePoint -LocalPath '.\out\alignment.json' -LibraryPath 'Weekly Reports' -WhatIf
```

---

## What This Playbook Does NOT Do

- It does **not** generate fictitious compliance scores. Hardcoded score data in evidence is a red flag for examiners and creates false-clean attestations.
- It does **not** assert that any single script "ensures compliance" with FINRA / SEC / SOX / GLBA. Scripts collect evidence; humans (Compliance Officer, CCO) attest.
- It does **not** modify Compliance Manager assessments or improvement actions. Use the portal walkthrough for those changes so they remain attributable to a named admin.

---

[Back to Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4.0*
