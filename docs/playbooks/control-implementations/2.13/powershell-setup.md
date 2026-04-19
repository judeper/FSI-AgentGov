# Control 2.13 — PowerShell Setup: Documentation and Record Keeping

**Control:** 2.13 — Documentation and Record Keeping
**Pillar:** Pillar 2 — Management
**Audience:** SharePoint Admin, Purview Records Manager, Purview Compliance Admin, Power Platform Admin
**Companion playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [Verification & Testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below may show abbreviated patterns; the baseline is authoritative.

> This playbook automates Control 2.13 via **PnP.PowerShell** (SharePoint site and library provisioning) and **ExchangeOnlineManagement** (the IPPS endpoint for Purview retention labels and policies). Every mutating command is wrapped in idempotency checks, supports `-WhatIf`, emits SHA-256 evidence hashes, and writes to a timestamped transcript.
>
> **Hedging note.** This automation helps support, and is recommended for compliance with, FINRA 4511 (books and records), FINRA 3110 (supervision documentation), SEC 17a-3/4 (record creation and preservation), SOX §§302/404 (internal controls), GLBA 501(b) (safeguards), OCC 2011-12 / Fed SR 11-7 (model risk documentation), and CFTC 1.31 (regulatory records). It does **not by itself** satisfy SEC 17a-4(f) preservation requirements — see the parent control's SEC 17a-4 guidance.

---

## §1. Pre-flight

### 1.1 Module and edition requirements

| Module | Required Edition | Minimum Version | Purpose |
|---|---|---|---|
| `PnP.PowerShell` v2+ | **Core only** (PS 7.2+) | 2.x (CAB-approved) | SharePoint site, library, column, and content type management |
| `ExchangeOnlineManagement` | Desktop (5.1) or Core (7.2+) | CAB-approved stable release | Purview retention labels, policies, auto-labeling |
| `Microsoft.Graph` | Core (PS 7+) | CAB-approved | Optional: agent metadata retrieval |

```powershell
# REQUIRED: Replace <version> with the version approved by your CAB.
Install-Module -Name PnP.PowerShell `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense

Install-Module -Name ExchangeOnlineManagement `
    -RequiredVersion '<version>' `
    -Repository PSGallery `
    -Scope CurrentUser `
    -AllowClobber `
    -AcceptLicense
```

### 1.2 Required roles

| Task | Required Role |
|---|---|
| SharePoint site and library provisioning | **SharePoint Admin** |
| Retention label and policy creation | **Purview Records Manager** + **Purview Compliance Admin** |
| Auto-labeling policy creation | **Purview Compliance Admin** |
| Copilot Studio agent metadata export | **Power Platform Admin** |

### 1.3 Initialize evidence directory and transcript

```powershell
$EvidenceRoot = 'C:\fsi-evidence\2.13'
$null = New-Item -ItemType Directory -Path $EvidenceRoot -Force
$Stamp = (Get-Date).ToString('yyyyMMdd-HHmmss')
$TranscriptPath = Join-Path $EvidenceRoot "transcript-2.13-$Stamp.log"
Start-Transcript -Path $TranscriptPath -Append

Write-Host "=== Control 2.13: Documentation and Record Keeping ===" -ForegroundColor Cyan
Write-Host "Evidence Root : $EvidenceRoot" -ForegroundColor Cyan
Write-Host "Timestamp     : $Stamp" -ForegroundColor Cyan
Write-Host "Transcript    : $TranscriptPath" -ForegroundColor Cyan
```

### 1.4 Common parameters

```powershell
# SharePoint configuration
$TenantAdminUrl  = 'https://contoso-admin.sharepoint.com'        # Replace with your tenant admin URL
$SiteAlias       = 'AI-Governance'
$SiteUrl         = 'https://contoso.sharepoint.com/sites/AI-Governance'  # Replace

# Purview configuration
$ReviewerStage1  = 'records-mgmt@contoso.com'     # Replace with your org's records manager
$ReviewerStage2  = 'compliance@contoso.com'         # Replace with your org's compliance reviewer

# Evidence manifest
$ManifestPath    = Join-Path $EvidenceRoot "manifest-2.13-$Stamp.csv"
$ManifestEntries = [System.Collections.ArrayList]::new()

function Add-EvidenceToManifest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $FilePath,
        [Parameter(Mandatory)] [string] $Description
    )
    if (Test-Path $FilePath) {
        $hash = (Get-FileHash -Path $FilePath -Algorithm SHA256).Hash
        $null = $ManifestEntries.Add([PSCustomObject]@{
            File        = (Split-Path $FilePath -Leaf)
            FullPath    = $FilePath
            SHA256      = $hash
            Description = $Description
            Timestamp   = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssZ')
        })
        Write-Host "[EVIDENCE] SHA-256: $hash — $Description" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Evidence file not found: $FilePath" -ForegroundColor Yellow
    }
}
```

### 1.5 Connect to SharePoint and Purview

```powershell
# Connect to SharePoint admin
Connect-PnPOnline -Url $TenantAdminUrl -Interactive

# Connect to Security & Compliance (Purview)
Connect-IPPSSession -ShowBanner:$false

# GCC High alternative:
# Connect-IPPSSession -ConnectionUri https://ps.compliance.protection.office365.us/powershell-liveid/ `
#     -AzureADAuthorizationEndpointUri https://login.microsoftonline.us/common -ShowBanner:$false
```

---

## §2. Idempotent SharePoint site provisioning

### 2.1 Helper: ensure AI Governance site exists

```powershell
function Ensure-AIGovernanceSite {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $AdminUrl,
        [Parameter(Mandatory)] [string] $SiteAlias,
        [Parameter(Mandatory)] [string] $SiteUrl
    )

    $existing = Get-PnPTenantSite -Url $SiteUrl -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "[SKIP] AI Governance site already exists: $SiteUrl" -ForegroundColor Yellow
        return $existing
    }

    if ($PSCmdlet.ShouldProcess($SiteUrl, "Create AI Governance SharePoint site")) {
        $site = New-PnPSite -Type TeamSite -Title "AI Governance" -Alias $SiteAlias
        Write-Host "[CREATED] AI Governance site: $SiteUrl" -ForegroundColor Green
        return $site
    }
}

Ensure-AIGovernanceSite -AdminUrl $TenantAdminUrl -SiteAlias $SiteAlias -SiteUrl $SiteUrl
```

### 2.2 Helper: ensure document library exists

```powershell
function Ensure-DocumentLibrary {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $SiteUrl,
        [Parameter(Mandatory)] [string] $LibraryName,
        [string] $Description = ''
    )

    Connect-PnPOnline -Url $SiteUrl -Interactive
    $existing = Get-PnPList -Identity $LibraryName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "[SKIP] Library '$LibraryName' exists ($($existing.ItemCount) items)" -ForegroundColor Yellow
        return $existing
    }

    if ($PSCmdlet.ShouldProcess($LibraryName, "Create document library")) {
        $lib = New-PnPList -Title $LibraryName -Template DocumentLibrary -Description $Description
        Write-Host "[CREATED] Library: $LibraryName" -ForegroundColor Green
        return $lib
    }
}
```

### 2.3 Provision all required libraries

```powershell
Connect-PnPOnline -Url $SiteUrl -Interactive

$RequiredLibraries = @(
    @{ Name = 'AgentConfigurations';  Desc = 'Agent manifest exports, prompt versions, system instructions' }
    @{ Name = 'InteractionLogs';      Desc = 'Conversation transcripts, session logs' }
    @{ Name = 'ApprovalRecords';      Desc = 'Deployment approvals, change requests, WSP addenda' }
    @{ Name = 'IncidentReports';      Desc = 'Security incidents, compliance findings, remediation evidence' }
    @{ Name = 'GovernanceDecisions';  Desc = 'Policy decisions, risk acceptances, governance meeting minutes' }
    @{ Name = 'SupervisionRecords';   Desc = 'FINRA 3110 supervision logs, sampling evidence, review outcomes' }
)

$libraryReport = @()
foreach ($lib in $RequiredLibraries) {
    $result = Ensure-DocumentLibrary -SiteUrl $SiteUrl -LibraryName $lib.Name -Description $lib.Desc
    $status = if ($result -and $result.ItemCount -ge 0) { 'Exists' } else { 'Created' }
    $libraryReport += [PSCustomObject]@{
        Library   = $lib.Name
        Status    = $status
        ItemCount = if ($result) { $result.ItemCount } else { 0 }
    }
}

# Export library inventory
$libReportPath = Join-Path $EvidenceRoot "library-inventory-$Stamp.csv"
$libraryReport | Export-Csv -Path $libReportPath -NoTypeInformation
Add-EvidenceToManifest -FilePath $libReportPath -Description 'SharePoint library inventory for AI Governance site'
```

---

## §3. Idempotent site column and metadata schema provisioning

### 3.1 Helper: ensure site column exists

```powershell
function Ensure-SiteColumn {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $DisplayName,
        [Parameter(Mandatory)] [string] $InternalName,
        [Parameter(Mandatory)] [string] $Type,
        [string[]] $Choices,
        [string] $Group = 'AI Governance'
    )

    $existing = Get-PnPField -Identity $InternalName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "[SKIP] Site column '$DisplayName' already exists" -ForegroundColor Yellow
        return $existing
    }

    if ($PSCmdlet.ShouldProcess($DisplayName, "Create site column")) {
        $params = @{
            DisplayName  = $DisplayName
            InternalName = $InternalName
            Type         = $Type
            Group        = $Group
        }
        if ($Choices -and $Type -eq 'Choice') {
            $params.Choices = $Choices
        }
        $field = New-PnPField @params
        Write-Host "[CREATED] Site column: $DisplayName" -ForegroundColor Green
        return $field
    }
}
```

### 3.2 Create all metadata columns

```powershell
# Core columns (Zone 1+)
Ensure-SiteColumn -DisplayName 'Agent ID'           -InternalName 'AgentID'           -Type Text
Ensure-SiteColumn -DisplayName 'Document Category'  -InternalName 'DocCategory'       -Type Choice `
    -Choices @('Configuration','Log','Approval','Incident','Decision','Supervision')
Ensure-SiteColumn -DisplayName 'Classification Date'-InternalName 'ClassificationDate'-Type DateTime

# Extended columns (Zone 2+)
Ensure-SiteColumn -DisplayName 'Regulatory Reference' -InternalName 'RegReference'    -Type Choice `
    -Choices @('FINRA 4511','FINRA 3110','SEC 17a-3','SEC 17a-4','SOX 302','SOX 404','GLBA 501(b)','OCC 2011-12','Fed SR 11-7','CFTC 1.31')
Ensure-SiteColumn -DisplayName 'Retention Period'    -InternalName 'RetentionPeriod'  -Type Choice `
    -Choices @('3 years','5 years','6 years','7 years','10 years','Permanent')
Ensure-SiteColumn -DisplayName 'Governance Zone'     -InternalName 'GovZone'          -Type Choice `
    -Choices @('Zone 1','Zone 2','Zone 3')
Ensure-SiteColumn -DisplayName 'Record Owner'        -InternalName 'RecordOwner'      -Type User

# Export column configuration as evidence
$columns = Get-PnPField | Where-Object { $_.Group -eq 'AI Governance' } |
    Select-Object InternalName, Title, TypeDisplayName, Required
$colReportPath = Join-Path $EvidenceRoot "site-columns-$Stamp.csv"
$columns | Export-Csv -Path $colReportPath -NoTypeInformation
Add-EvidenceToManifest -FilePath $colReportPath -Description 'AI Governance site columns configuration'
```

---

## §4. Idempotent retention label creation

### 4.1 Helper: ensure a retention label exists

```powershell
function Ensure-RetentionLabel {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string] $Name,
        [Parameter(Mandatory)] [string] $Comment,
        [Parameter(Mandatory)] [int]    $RetentionDurationDays,
        [Parameter(Mandatory)] [ValidateSet('Keep','Delete','KeepAndDelete')] [string] $RetentionAction,
        [bool]   $IsRecordLabel  = $false,
        [bool]   $Regulatory     = $false,
        [string] $ReviewerEmail
    )

    $existing = Get-ComplianceTag -Identity $Name -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "[SKIP] Retention label '$Name' already exists (Duration: $($existing.RetentionDuration) days)" -ForegroundColor Yellow
        return $existing
    }

    if ($PSCmdlet.ShouldProcess($Name, "Create retention label")) {
        $params = @{
            Name              = $Name
            Comment           = $Comment
            RetentionDuration = $RetentionDurationDays
            RetentionAction   = $RetentionAction
            RetentionType     = 'CreationAgeInDays'
        }
        if ($IsRecordLabel)  { $params.IsRecordLabel = $true }
        if ($Regulatory)     { $params.Regulatory    = $true }
        if ($ReviewerEmail)  { $params.ReviewerEmail = $ReviewerEmail }

        $label = New-ComplianceTag @params -ErrorAction Stop
        $labelPath = Join-Path $EvidenceRoot "label-$Name-$Stamp.json"
        $label | ConvertTo-Json -Depth 5 | Out-File -FilePath $labelPath -Encoding UTF8
        Add-EvidenceToManifest -FilePath $labelPath -Description "Retention label created: $Name"
        Write-Host "[CREATED] Retention label: $Name ($RetentionDurationDays days)" -ForegroundColor Green
        return $label
    }
}
```

!!! warning "Regulatory record labels are one-way"
    Once `Regulatory = $true` is set on a label, the label cannot be unmarked or deleted, items it has been applied to cannot have the label removed, and retention can only be extended. Treat creation of a regulatory label as a SEV-2 change requiring second-person approval. Organizations should verify this behavior meets their requirements.

### 4.2 Create the FSI retention label set

```powershell
# --- Zone 2 labels (standard record) ---

# Communications classification (3 years per SEC 17a-4(b)(4))
Ensure-RetentionLabel -Name 'FSI-Agent-Communications-3Year' `
    -Comment 'Agent conversation logs classified as communications under SEC 17a-4(b)(4). 3-year retention.' `
    -RetentionDurationDays 1095 `
    -RetentionAction KeepAndDelete `
    -IsRecordLabel $true `
    -ReviewerEmail $ReviewerStage1

# Books and records (6 years per SEC 17a-4(a))
Ensure-RetentionLabel -Name 'FSI-Agent-BooksRecords-6Year' `
    -Comment 'Agent records that evidence or generate a 17a-3 record. 6-year retention per SEC 17a-4(a).' `
    -RetentionDurationDays 2190 `
    -RetentionAction KeepAndDelete `
    -IsRecordLabel $true `
    -ReviewerEmail $ReviewerStage1

# Governance records (6 years per FINRA 4511)
Ensure-RetentionLabel -Name 'FSI-Agent-Governance-6Year' `
    -Comment 'AI governance decisions, policy records per FINRA 4511. 6-year retention.' `
    -RetentionDurationDays 2190 `
    -RetentionAction KeepAndDelete `
    -ReviewerEmail $ReviewerStage1

# Supervision records (6 years per FINRA 3110)
Ensure-RetentionLabel -Name 'FSI-Agent-Supervision-6Year' `
    -Comment 'FINRA 3110 supervision records including review logs and sampling evidence. 6-year retention.' `
    -RetentionDurationDays 2190 `
    -RetentionAction KeepAndDelete `
    -IsRecordLabel $true `
    -ReviewerEmail $ReviewerStage1

# Agent configuration (6 years)
Ensure-RetentionLabel -Name 'FSI-Agent-Configuration-6Year' `
    -Comment 'Agent definitions, version history, manifest exports. 6-year retention.' `
    -RetentionDurationDays 2190 `
    -RetentionAction Delete

# --- Zone 3 labels (regulatory record — IRREVERSIBLE) ---

# SEC 17a-4 regulatory record (7 years = 6-year requirement + 1-year buffer)
Ensure-RetentionLabel -Name 'FSI-Agent-RegRecord-7Year' `
    -Comment 'SEC 17a-4 regulatory record. 7-year retention (6-year requirement + buffer). IRREVERSIBLE.' `
    -RetentionDurationDays 2555 `
    -RetentionAction KeepAndDelete `
    -IsRecordLabel $true `
    -Regulatory $true `
    -ReviewerEmail $ReviewerStage2

# CFTC 1.31 (5 years for derivatives records)
Ensure-RetentionLabel -Name 'FSI-Agent-CFTC-5Year' `
    -Comment 'CFTC 1.31 regulatory record for FCMs, swap dealers, CPOs. 5-year retention. IRREVERSIBLE.' `
    -RetentionDurationDays 1825 `
    -RetentionAction KeepAndDelete `
    -IsRecordLabel $true `
    -Regulatory $true `
    -ReviewerEmail $ReviewerStage2

# Model risk documentation (6 years per OCC 2011-12 / Fed SR 11-7)
Ensure-RetentionLabel -Name 'FSI-Agent-ModelRisk-6Year' `
    -Comment 'OCC 2011-12 / Fed SR 11-7 model risk documentation. 6-year retention.' `
    -RetentionDurationDays 2190 `
    -RetentionAction KeepAndDelete `
    -IsRecordLabel $true `
    -ReviewerEmail $ReviewerStage2
```

---

## §5. Idempotent retention policy creation

### 5.1 Helper: ensure a retention policy exists

```powershell
function Ensure-RetentionPolicy {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string]   $PolicyName,
        [Parameter(Mandatory)] [string[]] $LabelNames,
        [Parameter(Mandatory)] [string]   $SharePointLocation,
        [string] $Comment = ''
    )

    $existing = Get-RetentionCompliancePolicy -Identity $PolicyName -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "[SKIP] Retention policy '$PolicyName' already exists (Mode: $($existing.Mode))" -ForegroundColor Yellow
        return $existing
    }

    if ($PSCmdlet.ShouldProcess($PolicyName, "Publish retention labels via policy")) {
        $policy = New-RetentionCompliancePolicy -Name $PolicyName `
            -Comment $Comment `
            -SharePointLocation $SharePointLocation `
            -Enabled $true `
            -ErrorAction Stop

        foreach ($labelName in $LabelNames) {
            New-RetentionComplianceRule -Policy $PolicyName `
                -PublishComplianceTag $labelName `
                -ErrorAction Stop
            Write-Host "  [PUBLISHED] Label '$labelName' via policy '$PolicyName'" -ForegroundColor Green
        }

        $policyPath = Join-Path $EvidenceRoot "policy-$PolicyName-$Stamp.json"
        $policy | ConvertTo-Json -Depth 5 | Out-File -FilePath $policyPath -Encoding UTF8
        Add-EvidenceToManifest -FilePath $policyPath -Description "Retention policy created: $PolicyName"
        Write-Host "[CREATED] Retention policy: $PolicyName" -ForegroundColor Green
        return $policy
    }
}
```

### 5.2 Publish labels to the AI Governance site

```powershell
$Zone2Labels = @(
    'FSI-Agent-Communications-3Year',
    'FSI-Agent-BooksRecords-6Year',
    'FSI-Agent-Governance-6Year',
    'FSI-Agent-Supervision-6Year',
    'FSI-Agent-Configuration-6Year'
)

Ensure-RetentionPolicy -PolicyName 'FSI-AI-Governance-Retention-Zone2' `
    -LabelNames $Zone2Labels `
    -SharePointLocation $SiteUrl `
    -Comment 'Zone 2 retention labels for AI governance documentation per FINRA 4511 / SEC 17a-4'

# Zone 3 regulatory labels (separate policy for audit segregation)
$Zone3Labels = @(
    'FSI-Agent-RegRecord-7Year',
    'FSI-Agent-CFTC-5Year',
    'FSI-Agent-ModelRisk-6Year'
)

Ensure-RetentionPolicy -PolicyName 'FSI-AI-Governance-Retention-Zone3' `
    -LabelNames $Zone3Labels `
    -SharePointLocation $SiteUrl `
    -Comment 'Zone 3 regulatory record labels per SEC 17a-4(f) / CFTC 1.31 / OCC 2011-12'
```

!!! note "Propagation delay"
    Published labels may take up to 7 days to appear in SharePoint libraries. Schedule policy creation at least 1 week before planned label application.

---

## §6. Documentation completeness audit

### 6.1 Audit required documents

```powershell
function Invoke-DocumentationAudit {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $SiteUrl
    )

    Connect-PnPOnline -Url $SiteUrl -Interactive

    $requiredDocs = @(
        @{ Library = 'GovernanceDecisions'; DocPattern = 'AI-Governance-Policy';            Zone = 'Zone 1' }
        @{ Library = 'GovernanceDecisions'; DocPattern = 'Annual-Documentation-Review';     Zone = 'Zone 1' }
        @{ Library = 'GovernanceDecisions'; DocPattern = 'Examination-Response-Procedure';  Zone = 'Zone 3' }
        @{ Library = 'GovernanceDecisions'; DocPattern = 'Quarterly-Audit-Schedule';        Zone = 'Zone 3' }
        @{ Library = 'GovernanceDecisions'; DocPattern = 'WSP-Addendum';                    Zone = 'Zone 2' }
        @{ Library = 'SupervisionRecords';  DocPattern = 'Supervision-Sampling-Report';     Zone = 'Zone 2' }
    )

    $auditResults = @()
    foreach ($req in $requiredDocs) {
        $items = Get-PnPListItem -List $req.Library -Query @"
<View><Query><Where>
    <Contains><FieldRef Name='FileLeafRef'/><Value Type='Text'>$($req.DocPattern)</Value></Contains>
</Where></Query></View>
"@ -ErrorAction SilentlyContinue

        $status = if ($items -and $items.Count -gt 0) { 'PASS' } else { 'FAIL' }
        $color  = if ($status -eq 'PASS') { 'Green' } else { 'Red' }
        Write-Host "[$status] $($req.DocPattern) in $($req.Library) ($($req.Zone))" -ForegroundColor $color

        $auditResults += [PSCustomObject]@{
            Library     = $req.Library
            Document    = $req.DocPattern
            Zone        = $req.Zone
            Status      = $status
            ItemCount   = if ($items) { $items.Count } else { 0 }
            AuditDate   = (Get-Date).ToString('yyyy-MM-dd')
        }
    }

    return $auditResults
}

$auditResults = Invoke-DocumentationAudit -SiteUrl $SiteUrl
$auditPath = Join-Path $EvidenceRoot "doc-completeness-audit-$Stamp.csv"
$auditResults | Export-Csv -Path $auditPath -NoTypeInformation
Add-EvidenceToManifest -FilePath $auditPath -Description 'Documentation completeness audit results'
```

---

## §7. Retention policy status export

```powershell
function Export-RetentionStatus {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $EvidenceRoot,
        [Parameter(Mandatory)] [string] $Stamp
    )

    Write-Host "`n=== Retention Label and Policy Status ===" -ForegroundColor Cyan

    # Export labels
    $labels = Get-ComplianceTag | Where-Object { $_.Name -like 'FSI-Agent*' } |
        Select-Object Name, Comment, RetentionDuration, RetentionAction, IsRecordLabel,
                      @{N='IsRegulatory';E={$_.Regulatory}}, Disabled, WhenCreatedUTC
    $labelPath = Join-Path $EvidenceRoot "retention-labels-$Stamp.csv"
    $labels | Export-Csv -Path $labelPath -NoTypeInformation
    Add-EvidenceToManifest -FilePath $labelPath -Description 'Purview retention label inventory'

    Write-Host "Labels found: $($labels.Count)" -ForegroundColor Cyan
    $labels | Format-Table Name, RetentionDuration, RetentionAction, IsRecordLabel -AutoSize

    # Export policies
    $policies = Get-RetentionCompliancePolicy | Where-Object {
        $_.Name -like '*AI*' -or $_.Name -like '*Agent*' -or $_.Name -like '*FSI*'
    } | Select-Object Name, Mode, Enabled, SharePointLocation, WhenCreatedUTC

    $policyPath = Join-Path $EvidenceRoot "retention-policies-$Stamp.csv"
    $policies | Export-Csv -Path $policyPath -NoTypeInformation
    Add-EvidenceToManifest -FilePath $policyPath -Description 'Purview retention policy inventory'

    Write-Host "Policies found: $($policies.Count)" -ForegroundColor Cyan
    $policies | Format-Table Name, Mode, Enabled -AutoSize
}

Export-RetentionStatus -EvidenceRoot $EvidenceRoot -Stamp $Stamp
```

---

## §8. Copilot Studio agent documentation export

```powershell
function Export-AgentDocumentation {
    <#
    .SYNOPSIS
        Exports Copilot Studio agent metadata for governance documentation.
    .DESCRIPTION
        Retrieves agent metadata from Power Platform Admin Center and exports
        to the evidence directory for record-keeping per FINRA 4511 / OCC 2011-12.
    .PARAMETER EnvironmentId
        The Power Platform environment ID containing the agents.
    .PARAMETER EvidenceRoot
        Path to the evidence output directory.
    .EXAMPLE
        Export-AgentDocumentation -EnvironmentId 'abc-123' -EvidenceRoot 'C:\fsi-evidence\2.13'
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $EnvironmentId,
        [Parameter(Mandatory)] [string] $EvidenceRoot
    )

    # Guard: requires Windows PowerShell 5.1 for PPAC module
    if ($PSVersionTable.PSEdition -ne 'Desktop') {
        Write-Host "[WARN] Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1." -ForegroundColor Yellow
        Write-Host "[INFO] Run this section in Windows PowerShell (Desktop edition)." -ForegroundColor Cyan
        return
    }

    Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
    Add-PowerAppsAccount  # Interactive login; use -Endpoint 'usgov' for GCC

    $localStamp = (Get-Date).ToString('yyyyMMdd-HHmmss')
    $agents = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId |
              ForEach-Object { Get-AdminPowerApp -EnvironmentName $EnvironmentId }

    if (-not $agents -or $agents.Count -eq 0) {
        Write-Host "[INFO] No agents found in environment $EnvironmentId" -ForegroundColor Yellow
        return
    }

    $agentReport = $agents | Select-Object @{N='AgentName';E={$_.DisplayName}},
        @{N='AgentId';E={$_.AppName}},
        @{N='Owner';E={$_.Owner.displayName}},
        @{N='CreatedTime';E={$_.CreatedTime}},
        @{N='LastModified';E={$_.LastModifiedTime}},
        @{N='EnvironmentId';E={$EnvironmentId}}

    $agentPath = Join-Path $EvidenceRoot "agent-inventory-$EnvironmentId-$localStamp.csv"
    $agentReport | Export-Csv -Path $agentPath -NoTypeInformation
    Add-EvidenceToManifest -FilePath $agentPath -Description "Agent inventory for environment $EnvironmentId"

    Write-Host "[PASS] Exported $($agents.Count) agents from environment $EnvironmentId" -ForegroundColor Green
}

# Usage (uncomment and set your environment ID):
# Export-AgentDocumentation -EnvironmentId '<your-environment-id>' -EvidenceRoot $EvidenceRoot
```

---

## §9. Evidence manifest finalization

```powershell
# Write the manifest CSV
$ManifestEntries | Export-Csv -Path $ManifestPath -NoTypeInformation
Write-Host "`n=== Evidence Manifest ===" -ForegroundColor Cyan
Write-Host "Manifest: $ManifestPath" -ForegroundColor Cyan
Write-Host "Entries:  $($ManifestEntries.Count)" -ForegroundColor Cyan
$ManifestEntries | Format-Table File, SHA256, Description -AutoSize

# Hash the manifest itself
$manifestHash = (Get-FileHash -Path $ManifestPath -Algorithm SHA256).Hash
Write-Host "`n[MANIFEST SHA-256] $manifestHash" -ForegroundColor Green

# Stop the transcript
Stop-Transcript
Write-Host "[COMPLETE] Transcript saved to: $TranscriptPath" -ForegroundColor Green

# Hash the transcript
$transcriptHash = (Get-FileHash -Path $TranscriptPath -Algorithm SHA256).Hash
Write-Host "[TRANSCRIPT SHA-256] $transcriptHash" -ForegroundColor Green
```

---

## §10. Complete validation script

```powershell
<#
.SYNOPSIS
    Validates Control 2.13 — Documentation and Record Keeping configuration.
.DESCRIPTION
    Performs a read-only validation of SharePoint site structure, retention labels,
    retention policies, and documentation completeness for Control 2.13.
    This script does not mutate any configuration.
.PARAMETER SiteUrl
    URL of the AI Governance SharePoint site.
.PARAMETER EvidenceRoot
    Path to write validation evidence.
.EXAMPLE
    .\Validate-Control-2.13.ps1 -SiteUrl 'https://contoso.sharepoint.com/sites/AI-Governance'
.NOTES
    Supports compliance with FINRA 4511, SEC 17a-3/4, SOX 302/404.
    Does not guarantee regulatory compliance.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $SiteUrl,
    [string] $EvidenceRoot = 'C:\fsi-evidence\2.13'
)

$null = New-Item -ItemType Directory -Path $EvidenceRoot -Force
$Stamp = (Get-Date).ToString('yyyyMMdd-HHmmss')
$results = @()

Write-Host "=== Control 2.13 Validation ===" -ForegroundColor Cyan

# Check 1: Site structure
Write-Host "`n[Check 1] SharePoint Site Structure" -ForegroundColor Cyan
try {
    Connect-PnPOnline -Url $SiteUrl -Interactive
    $lists = Get-PnPList | Where-Object { $_.BaseTemplate -eq 101 } |
        Select-Object Title, ItemCount, Created
    $requiredLibs = @('AgentConfigurations','InteractionLogs','ApprovalRecords',
                      'IncidentReports','GovernanceDecisions','SupervisionRecords')
    foreach ($lib in $requiredLibs) {
        $found = $lists | Where-Object { $_.Title -eq $lib }
        $status = if ($found) { 'PASS' } else { 'FAIL' }
        $color  = if ($status -eq 'PASS') { 'Green' } else { 'Red' }
        Write-Host "  [$status] Library: $lib" -ForegroundColor $color
        $results += [PSCustomObject]@{ Check = "Library-$lib"; Status = $status }
    }
    Disconnect-PnPOnline
} catch {
    Write-Host "  [FAIL] Cannot connect to site: $($_.Exception.Message)" -ForegroundColor Red
    $results += [PSCustomObject]@{ Check = 'SiteConnect'; Status = 'FAIL' }
}

# Check 2: Retention labels
Write-Host "`n[Check 2] Retention Labels" -ForegroundColor Cyan
try {
    Connect-IPPSSession -ShowBanner:$false
    $labels = Get-ComplianceTag | Where-Object { $_.Name -like 'FSI-Agent*' }
    if ($labels -and $labels.Count -ge 4) {
        Write-Host "  [PASS] Found $($labels.Count) FSI-Agent retention labels" -ForegroundColor Green
        $results += [PSCustomObject]@{ Check = 'RetentionLabels'; Status = 'PASS' }
    } else {
        Write-Host "  [WARN] Found $($labels.Count) labels (expected 4+)" -ForegroundColor Yellow
        $results += [PSCustomObject]@{ Check = 'RetentionLabels'; Status = 'WARN' }
    }

    # Check 3: Retention policies
    Write-Host "`n[Check 3] Retention Policies" -ForegroundColor Cyan
    $policies = Get-RetentionCompliancePolicy | Where-Object {
        $_.Name -like '*AI*' -or $_.Name -like '*Agent*' -or $_.Name -like '*FSI*'
    }
    if ($policies -and $policies.Count -ge 1) {
        Write-Host "  [PASS] Found $($policies.Count) retention policies" -ForegroundColor Green
        $results += [PSCustomObject]@{ Check = 'RetentionPolicies'; Status = 'PASS' }
    } else {
        Write-Host "  [WARN] No AI-specific retention policies found" -ForegroundColor Yellow
        $results += [PSCustomObject]@{ Check = 'RetentionPolicies'; Status = 'WARN' }
    }

    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
} catch {
    Write-Host "  [FAIL] Cannot connect to Purview: $($_.Exception.Message)" -ForegroundColor Red
    $results += [PSCustomObject]@{ Check = 'PurviewConnect'; Status = 'FAIL' }
}

# Check 4: SEC 17a-4 compliant storage (manual verification)
Write-Host "`n[Check 4] SEC 17a-4 Compliant Storage (Zone 3)" -ForegroundColor Cyan
Write-Host "  [INFO] Manual verification required: confirm WORM storage or audit-trail" -ForegroundColor Yellow
Write-Host "  [INFO] alternative is configured per October 2022 amendments" -ForegroundColor Yellow
$results += [PSCustomObject]@{ Check = 'SEC17a4Storage'; Status = 'MANUAL' }

# Check 5: Examination procedures (manual verification)
Write-Host "`n[Check 5] Examination Response Procedures" -ForegroundColor Cyan
Write-Host "  [INFO] Verify examination response procedure is documented with" -ForegroundColor Yellow
Write-Host "  [INFO] designated custodians and response SLAs" -ForegroundColor Yellow
$results += [PSCustomObject]@{ Check = 'ExamProcedures'; Status = 'MANUAL' }

# Export results
$resultPath = Join-Path $EvidenceRoot "validation-results-$Stamp.csv"
$results | Export-Csv -Path $resultPath -NoTypeInformation

$passCount = ($results | Where-Object { $_.Status -eq 'PASS' }).Count
$failCount = ($results | Where-Object { $_.Status -eq 'FAIL' }).Count
$warnCount = ($results | Where-Object { $_.Status -eq 'WARN' }).Count

Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "PASS: $passCount | FAIL: $failCount | WARN: $warnCount | MANUAL: $(($results | Where-Object { $_.Status -eq 'MANUAL' }).Count)" -ForegroundColor Cyan
Write-Host "Results: $resultPath" -ForegroundColor Cyan
```

---

[Back to Control 2.13](../../../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3.3 | UI Verification Status: Current*
