# Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels - PowerShell Setup

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. The snippets below assume you have already complied with that baseline.

> This playbook provides PowerShell automation guidance for [Control 1.5 — Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md).
>
> **Scope of this file:** Microsoft Purview DLP for **Microsoft 365 Copilot and Copilot Chat** (Custom-template policies), label-based DLP for SharePoint / OneDrive content surfaced through Copilot, and **Power Platform** data policies for Copilot Studio connector classification. PowerShell coverage is **partial** — several Copilot-DLP behaviours can only be confirmed in the Purview portal and must be evidenced via screenshots in addition to the JSON exports below.

---

## Wrong-shell trap (READ FIRST)

DLP cmdlets used in this control live in **three separate PowerShell sessions**. Running a cmdlet in the wrong session produces either a `CommandNotFoundException` or, worse, **silent zero results that look like clean evidence**.

| Cmdlet family | Required session | Module |
|---|---|---|
| `*-DlpCompliancePolicy`, `*-DlpComplianceRule`, `Get-Label`, `Get-LabelPolicy`, `New-ComplianceSearch` | `Connect-IPPSSession` (Security & Compliance) | `ExchangeOnlineManagement` |
| `Get-AdminAuditLogConfig`, `Search-UnifiedAuditLog` | `Connect-ExchangeOnline` | `ExchangeOnlineManagement` |
| `Get-DlpPolicy`, `New-DlpPolicy`, `Set-DlpPolicy` (Power Platform connector classification) | `Add-PowerAppsAccount` | `Microsoft.PowerApps.Administration.PowerShell` (Windows PowerShell 5.1 only) |
| `Get-MgBetaSecurityInformationProtectionSensitivityLabel` | `Connect-MgGraph -Scopes 'InformationProtectionPolicy.Read.All'` | `Microsoft.Graph.Beta.Security` |

> **Cmdlet-name pitfall:** `Get-MgBetaInformationProtectionSensitivityPolicyLabel` **does not exist**. The real cmdlet is `Get-MgBetaSecurityInformationProtectionSensitivityLabel` (Security namespace, no `Policy` segment). See Microsoft Learn — [Get-MgBetaSecurityInformationProtectionSensitivityLabel](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.beta.security/get-mgbetasecurityinformationprotectionsensitivitylabel).

Always assert session state before invoking a cmdlet from any of the four families above.

---

## Sovereign cloud connection parameters

```powershell
# ----- Commercial -----
Connect-ExchangeOnline -UserPrincipalName $UPN
Connect-IPPSSession    -UserPrincipalName $UPN
Connect-MgGraph        -Environment Global -Scopes 'InformationProtectionPolicy.Read.All'
Add-PowerAppsAccount   -Endpoint prod

# ----- GCC -----
Connect-ExchangeOnline -UserPrincipalName $UPN -ExchangeEnvironmentName O365USGovGCCHigh   # GCC tenants in EXO use commercial endpoint; GCC High uses O365USGovGCCHigh
Connect-IPPSSession    -UserPrincipalName $UPN `
    -ConnectionUri 'https://ps.compliance.protection.outlook.com/powershell-liveid/' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.com/common'
Connect-MgGraph        -Environment USGov -Scopes 'InformationProtectionPolicy.Read.All'
Add-PowerAppsAccount   -Endpoint usgov

# ----- GCC High -----
Connect-ExchangeOnline -UserPrincipalName $UPN -ExchangeEnvironmentName O365USGovGCCHigh
Connect-IPPSSession    -UserPrincipalName $UPN `
    -ConnectionUri 'https://ps.compliance.protection.office365.us/powershell-liveid/' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/common'
Connect-MgGraph        -Environment USGov -Scopes 'InformationProtectionPolicy.Read.All'
Add-PowerAppsAccount   -Endpoint usgovhigh

# ----- DoD -----
Connect-ExchangeOnline -UserPrincipalName $UPN -ExchangeEnvironmentName O365USGovDoD
Connect-IPPSSession    -UserPrincipalName $UPN `
    -ConnectionUri 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/' `
    -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/common'
Connect-MgGraph        -Environment USGovDoD -Scopes 'InformationProtectionPolicy.Read.All'
Add-PowerAppsAccount   -Endpoint dod
```

> Verify endpoints against Microsoft Learn — [Connect-IPPSSession](https://learn.microsoft.com/en-us/powershell/module/exchange/connect-ippssession) and [Microsoft Graph PowerShell installation](https://learn.microsoft.com/en-us/powershell/microsoftgraph/installation) before each change window. Sovereign-cloud endpoints are updated by Microsoft without notice.

---

## Module pinning (mandatory)

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement';                RequiredVersion = '3.5.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Beta.Security';           RequiredVersion = '2.20.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Authentication';         RequiredVersion = '2.20.0' }
# Note: Microsoft.PowerApps.Administration.PowerShell is Desktop-only (Windows PowerShell 5.1).
# Run Power-Platform sections from a separate PS 5.1 host; do NOT mix in this PS 7 session.
```

Power Platform Administration cmdlets are **Desktop-only**. Add the guard from the baseline:

```powershell
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
```

---

## Pre-flight: license, role, module, and connection checks

```powershell
function Test-PreFlight {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $UPN,
        [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud,
        [Parameter(Mandatory)] [string] $EvidencePath
    )

    $results = [ordered]@{}

    # Module presence (do NOT auto-install in regulated tenants)
    foreach ($m in 'ExchangeOnlineManagement','Microsoft.Graph.Beta.Security','Microsoft.Graph.Authentication') {
        $results["Module:$m"] = [bool](Get-Module -ListAvailable -Name $m)
    }

    # IPPS session
    $results['IPPSConnected'] = [bool](Get-Command Get-DlpCompliancePolicy -ErrorAction SilentlyContinue)

    # EXO session (different from IPPS)
    $results['EXOConnected'] = [bool](Get-Command Get-AdminAuditLogConfig -ErrorAction SilentlyContinue)

    # Graph context
    try { $ctx = Get-MgContext } catch { $ctx = $null }
    $results['GraphConnected'] = [bool]$ctx
    $results['GraphScopes']    = if ($ctx) { $ctx.Scopes -join ',' } else { '' }

    # SKU floor — Microsoft 365 Copilot is required for the Copilot DLP location
    if ($ctx) {
        $skus = Get-MgSubscribedSku -ErrorAction SilentlyContinue
        $results['HasCopilotSku'] = [bool]($skus | Where-Object { $_.SkuPartNumber -eq 'Microsoft_365_Copilot' })
    }

    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    $path = Join-Path $EvidencePath ("preflight-{0}.json" -f (Get-Date -Format 'yyyyMMddTHHmmssZ'))
    $results | ConvertTo-Json | Set-Content -Path $path -Encoding UTF8
    return [pscustomobject]$results
}
```

---

## Evidence emission (SHA-256 manifest)

```powershell
function Write-FsiEvidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] $InputObject,
        [Parameter(Mandatory)] [string] $Name,
        [Parameter(Mandatory)] [string] $EvidencePath,
        [ValidateSet('Json','Csv')] [string] $As = 'Json',
        [string] $ScriptVersion = '1.5-v1.4'
    )
    $ts   = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $ext  = if ($As -eq 'Json') { 'json' } else { 'csv' }
    $path = Join-Path $EvidencePath "$Name-$ts.$ext"

    if ($As -eq 'Json') {
        $InputObject | ConvertTo-Json -Depth 20 | Set-Content -Path $path -Encoding UTF8
    } else {
        $InputObject | Export-Csv -Path $path -NoTypeInformation -Encoding UTF8
    }

    $hash = (Get-FileHash -Path $path -Algorithm SHA256).Hash

    $manifestPath = Join-Path $EvidencePath 'manifest.json'
    $manifest = @()
    if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
    $manifest += [pscustomobject]@{
        file           = (Split-Path $path -Leaf)
        sha256         = $hash
        bytes          = (Get-Item $path).Length
        generated_utc  = $ts
        script_version = $ScriptVersion
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    return $path
}
```

The wrapper script in section 7 starts a `Start-Transcript`, hashes the transcript on close, and appends both the transcript and the manifest to immutable storage (Purview retention label / WORM blob) per Control 1.7.

---

## 1 — Create the Microsoft 365 Copilot DLP policy (Custom template)

> **Session: `Connect-IPPSSession`** — these are `*-DlpCompliance*` cmdlets in the Security & Compliance shell.

The Microsoft 365 Copilot and Copilot Chat DLP location is exposed **only when the policy is created from the Custom template**. Standard templates do not surface the Copilot location. There is no public API field that records "this policy was created from the Custom template" — the technical proxy is the **rule shape** (separate SIT and sensitivity-label rules in the same policy) plus a portal screenshot retained as evidence. See section 5.

The Copilot location is configured via the `Locations` parameter (a JSON array of workload descriptors), and the rule action is set on `EnforcementPlanes`. See Microsoft Learn — [New-DlpCompliancePolicy](https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy), [New-DlpComplianceRule](https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancerule), and [Learn about the Microsoft 365 Copilot location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about).

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string] $TenantId,                 # Entra tenant GUID
    [Parameter(Mandatory)] [string] $PolicyName = 'FSI-Copilot-DLP',
    [Parameter(Mandatory)] [string] $HighlyConfidentialLabelGuid,  # from Get-Label
    [switch] $TestMode,
    [Parameter(Mandatory)] [string] $EvidencePath
)

$mode = if ($TestMode) { 'TestWithNotifications' } else { 'Enable' }

# Snapshot before mutation
$before = Get-DlpCompliancePolicy -Identity $PolicyName -ErrorAction SilentlyContinue
Write-FsiEvidence -InputObject $before -Name "policy-before-$PolicyName" -EvidencePath $EvidencePath

# Locations descriptor for the Microsoft 365 Copilot and Copilot Chat workload
$copilotLocation = @(
    @{
        Workload   = 'Applications'
        Location   = $TenantId
        Inclusions = @(@{ Type = 'Tenant'; Identity = 'All' })
    }
) | ConvertTo-Json -Depth 6 -Compress

if ($PSCmdlet.ShouldProcess($PolicyName, "New-DlpCompliancePolicy (Copilot location, mode=$mode)")) {
    New-DlpCompliancePolicy `
        -Name      $PolicyName `
        -Comment   'Custom-template policy for Microsoft 365 Copilot and Copilot Chat. Implementation requires Microsoft 365 Copilot license and may take up to 4 hours to fully propagate.' `
        -Mode      $mode `
        -Priority  1 `
        -Locations $copilotLocation
}
```

> **Why `Locations` and not `ExchangeLocation` / `SharePointLocation` / etc.:** the legacy per-workload location parameters do **not** cover Microsoft 365 Copilot or Copilot Chat. A policy that uses only `ExchangeLocation`/`SharePointLocation`/`OneDriveLocation`/`TeamsLocation` will compile and run, but it will **not** evaluate Copilot prompts — producing false-clean evidence. The `Locations` JSON with `Workload = 'Applications'` is required.

### Rule A — block prompts that contain SITs

`-AdvancedRule` is required for the Copilot location; you cannot mix SIT and sensitivity-label conditions in a single rule (the Purview portal blocks this and the cmdlet will accept it but produce undefined behaviour). Keep them as separate rules in the same policy.

```powershell
$sitRule = @{
    Version    = '1.0'
    Condition  = @{
        Operator     = 'Or'
        SubConditions = @(
            @{ ConditionName = 'ContentContainsSensitiveInformation';
               Value = @(
                   @{ groups = @(@{ name = 'Default'; operator = 'Or';
                       sensitivetypes = @(
                           @{ name = 'U.S. Social Security Number (SSN)';     mincount = 1; confidencelevel = 'High' },
                           @{ name = 'ABA Routing Number';                    mincount = 1; confidencelevel = 'High' },
                           @{ name = 'Credit Card Number';                    mincount = 1; confidencelevel = 'High' },
                           @{ name = 'U.S. Bank Account Number';              mincount = 1; confidencelevel = 'High' }
                       )
                   })}
               )
            }
        )
    }
} | ConvertTo-Json -Depth 12 -Compress

if ($PSCmdlet.ShouldProcess("$PolicyName / Rule-SIT", 'New-DlpComplianceRule (SIT, Copilot)')) {
    New-DlpComplianceRule `
        -Name              "$PolicyName-Rule-SIT" `
        -Policy            $PolicyName `
        -AdvancedRule      $sitRule `
        -EnforcementPlanes @('CopilotExperiences') `
        -BlockAccess       $true `
        -NotifyUser        @('SiteAdmin','LastModifier') `
        -NotifyEndpointUser $false `
        -GenerateIncidentReport @('SiteAdmin') `
        -IncidentReportContent  @('All')
}
```

### Rule B — block prompts that touch Highly Confidential labelled content

```powershell
$labelRule = @{
    Version   = '1.0'
    Condition = @{
        Operator     = 'And'
        SubConditions = @(
            @{ ConditionName = 'ContentContainsSensitivityLabel';
               Value = @(
                   @{ labels = @(@{ name = $HighlyConfidentialLabelGuid; type = 'Sensitivity' }) }
               )
            }
        )
    }
} | ConvertTo-Json -Depth 12 -Compress

if ($PSCmdlet.ShouldProcess("$PolicyName / Rule-Label", 'New-DlpComplianceRule (Sensitivity Label, Copilot)')) {
    New-DlpComplianceRule `
        -Name              "$PolicyName-Rule-Label" `
        -Policy            $PolicyName `
        -AdvancedRule      $labelRule `
        -EnforcementPlanes @('CopilotExperiences') `
        -BlockAccess       $true `
        -NotifyUser        @('SiteAdmin','LastModifier') `
        -NotifyEndpointUser $false `
        -GenerateIncidentReport @('SiteAdmin') `
        -IncidentReportContent  @('All')
}
```

> **Type pitfalls fixed in v1.4:**
>
> - `ContentPropertyContainsWords` is a `MultiValuedProperty` (string array) — it is **not** a hashtable and **cannot** carry `"Document.SensitivityLabel" = "Highly Confidential"`. Label matching for the Copilot location must use `-AdvancedRule` with a `ContentContainsSensitivityLabel` condition referencing the label **GUID**.
> - `NotifyEndpointUser` is **Boolean** (`$true` / `$false`), not a string like `"NotifyUser"`.
> - `NotifyUser` is a **string array** — pass `@('SiteAdmin','LastModifier')`, not the comma-joined string `"SiteAdmin,LastModifier"`.

---

## 2 — List sensitivity labels (correct cmdlet name)

> **Session: `Connect-MgGraph`** — read-only.

```powershell
Connect-MgGraph -Environment Global -Scopes 'InformationProtectionPolicy.Read.All' -NoWelcome

$labels = Get-MgBetaSecurityInformationProtectionSensitivityLabel |
    Select-Object Id, Name, Description, IsDefault, Sensitivity

Write-FsiEvidence -InputObject $labels -Name 'sensitivity-labels' -EvidencePath $EvidencePath -As Csv
```

> **Cmdlet correction:** previous versions of this playbook referenced `Get-MgBetaInformationProtectionSensitivityPolicyLabel` — that cmdlet does not exist. Use `Get-MgBetaSecurityInformationProtectionSensitivityLabel` from the `Microsoft.Graph.Beta.Security` module. Alternative: `Get-Label` from `Connect-IPPSSession`.

---

## 3 — Power Platform connector classification (Copilot Studio)

> **Session: `Add-PowerAppsAccount`** in **Windows PowerShell 5.1** (Desktop).
>
> **API ↔ UI label inversion (CRITICAL):** the Power Platform DLP API returns `Classification` strings that do **not** match the UI labels:
>
> | API value (`$_.Classification`) | UI label in Power Platform Admin Center |
> |---|---|
> | `Confidential` | **Business** (the protected/restricted group) |
> | `General`      | **Non-Business** |
> | `Blocked`      | **Blocked** |
>
> Audit scripts that compare `$_.Classification -eq 'General'` while labelling the result "Business" (and vice-versa) will silently emit **inverted evidence**. Reference: Microsoft Learn — [New-DlpPolicy (Power Platform Administration)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/new-dlppolicy) — observe that the cmdlet documentation and the portal use opposite vocabularies for the protected group.

### Normalization helper (use in every audit script)

```powershell
function ConvertTo-FsiUiLabel {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string] $ApiClassification)
    switch ($ApiClassification) {
        'Confidential' { 'Business'      ; break }
        'General'      { 'Non-Business'  ; break }
        'Blocked'      { 'Blocked'       ; break }
        default        { "UNKNOWN($ApiClassification)" }
    }
}
```

### List connector classifications (API value AND normalized UI label)

```powershell
Add-PowerAppsAccount -Endpoint $Endpoint   # 'prod' / 'usgov' / 'usgovhigh' / 'dod'

$rows = foreach ($p in Get-DlpPolicy) {
    $detail = Get-DlpPolicy -PolicyName $p.PolicyName
    foreach ($group in $detail.ConnectorGroups) {
        $uiLabel = ConvertTo-FsiUiLabel -ApiClassification $group.Classification
        foreach ($c in $group.Connectors) {
            [pscustomobject]@{
                PolicyDisplayName  = $detail.DisplayName
                PolicyName         = $detail.PolicyName
                ConnectorId        = $c.Id
                ConnectorName      = $c.Name
                ConnectorType      = $c.Type
                ApiClassification  = $group.Classification   # 'Confidential' | 'General' | 'Blocked'
                UiClassification   = $uiLabel                # 'Business'     | 'Non-Business' | 'Blocked'
            }
        }
    }
}

Write-FsiEvidence -InputObject $rows -Name 'powerplatform-connector-classifications' -EvidencePath $EvidencePath -As Csv
```

### Audit Zone 3 expectations

```powershell
$expectedBlocked = @('*HTTP Webhook*','*Custom Website*','*SharePoint Channel*')

$findings = foreach ($pattern in $expectedBlocked) {
    $hit = $rows | Where-Object { $_.ConnectorName -like $pattern -and $_.UiClassification -eq 'Blocked' }
    [pscustomobject]@{
        Pattern  = $pattern
        Status   = if ($hit) { 'PASS' } else { 'FAIL' }
        Evidence = ($hit | Select-Object PolicyDisplayName,ConnectorName -First 5)
    }
}

Write-FsiEvidence -InputObject $findings -Name 'zone3-blocked-connectors-audit' -EvidencePath $EvidencePath
```

---

## 4 — List DLP policies that include the Copilot location

This is the technical proxy for "Custom template was used". A DLP policy whose `Locations` JSON contains a `Workload = "Applications"` entry was created from the Custom template (Standard templates do not expose this workload). Pair this output with a portal screenshot of the policy creation flow as evidence.

```powershell
$copilotPolicies = foreach ($p in Get-DlpCompliancePolicy) {
    $locsRaw = $p.Locations
    $hasCopilot = $false
    try {
        $parsed = $locsRaw | ConvertFrom-Json -ErrorAction Stop
        $hasCopilot = [bool]($parsed | Where-Object { $_.Workload -eq 'Applications' })
    } catch {
        # Locations may be returned as a string in some module builds; fall back to substring match
        $hasCopilot = ($locsRaw -match '"Workload"\s*:\s*"Applications"')
    }

    $rules = Get-DlpComplianceRule -Policy $p.Name -ErrorAction SilentlyContinue
    [pscustomobject]@{
        Name                = $p.Name
        Mode                = $p.Mode
        IncludesCopilotLoc  = $hasCopilot
        RuleCount           = ($rules | Measure-Object).Count
        RuleNames           = ($rules.Name -join '|')
        EnforcementPlanes   = (($rules | ForEach-Object { $_.EnforcementPlanes }) -join '|')
        # Custom-template proxy: separate SIT and Label rules in the same policy
        CustomTemplateProxy = (
            ($rules.Name -match 'SIT')   -ne $null -and
            ($rules.Name -match 'Label') -ne $null
        )
    }
} | Where-Object { $_.IncludesCopilotLoc }

Write-FsiEvidence -InputObject $copilotPolicies -Name 'copilot-dlp-policies' -EvidencePath $EvidencePath
```

> **Custom-template caveat:** there is no API field that records the originating template. Retain a portal screenshot of the policy creation wizard alongside this JSON. If the `CustomTemplateProxy` column is `$false`, do **not** infer non-compliance — verify in the portal.

---

## 5 — Audit log search for DLP rule matches

> **Session: `Connect-ExchangeOnline`** — `Search-UnifiedAuditLog` is an EXO cmdlet, not IPPS.
>
> **`-RecordType DLP` is not a valid value** for `Search-UnifiedAuditLog`. The real DLP record types are `ComplianceDLPSharePoint`, `ComplianceDLPSharePointClassification`, `ComplianceDLPExchange`, `ComplianceDLPExchangeClassification`, and `DLPEndpoint`. Passing the invalid value `DLP` returns an error in newer modules and **silently zero rows** in older module builds — a classic false-clean trap. See Microsoft Learn — [Search-UnifiedAuditLog](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog).
>
> Microsoft 365 Copilot DLP rule matches surface in the unified audit log under the `DLPRuleMatch` operation with a `Workload` of `Applications` (Microsoft 365 Copilot and Copilot Chat). Filter on `Operations`, not `RecordType`, to pick up Copilot evaluations.

```powershell
$end     = (Get-Date).ToUniversalTime()
$start   = $end.AddDays(-7)
$session = "ctrl15-dlp-$(Get-Date -Format 'yyyyMMddHHmmss')"

# 5a — file/email DLP rule matches across SharePoint, OneDrive, Exchange, Endpoint
$fileEmailDlp = New-Object System.Collections.Generic.List[object]
foreach ($rt in 'ComplianceDLPSharePoint','ComplianceDLPSharePointClassification',
                'ComplianceDLPExchange','ComplianceDLPExchangeClassification','DLPEndpoint') {
    do {
        $batch = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
            -RecordType $rt -ResultSize 5000 `
            -SessionId "$session-$rt" -SessionCommand ReturnLargeSet
        if ($batch) { $fileEmailDlp.AddRange($batch) }
    } while ($batch -and $batch.Count -gt 0 -and $fileEmailDlp.Count -lt 50000)
}

# 5b — Copilot DLP rule matches (filter by Operation, then by Workload in the JSON payload)
$copilotDlp = New-Object System.Collections.Generic.List[object]
do {
    $batch = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
        -Operations 'DLPRuleMatch' -ResultSize 5000 `
        -SessionId "$session-copilot" -SessionCommand ReturnLargeSet
    if ($batch) {
        foreach ($e in $batch) {
            try {
                $data = $e.AuditData | ConvertFrom-Json -ErrorAction Stop
                if ($data.Workload -eq 'Applications' -or
                    $data.Workload -match 'Copilot' -or
                    $data.PolicyDetails.Rules.RuleMode -match 'Copilot') {
                    $copilotDlp.Add($e)
                }
            } catch { }
        }
    }
} while ($batch -and $batch.Count -gt 0 -and $copilotDlp.Count -lt 50000)

Write-FsiEvidence -InputObject ($fileEmailDlp | Select-Object CreationDate,UserIds,Operations,RecordType,AuditData) `
    -Name 'dlp-rule-matches-files-email' -EvidencePath $EvidencePath -As Csv
Write-FsiEvidence -InputObject ($copilotDlp  | Select-Object CreationDate,UserIds,Operations,RecordType,AuditData) `
    -Name 'dlp-rule-matches-copilot'      -EvidencePath $EvidencePath -As Csv

if ($copilotDlp.Count -eq 0) {
    Write-Warning "Zero Copilot DLP rule matches in last 7 days. Possible causes: (a) policy still in TestWithoutNotifications, (b) policy propagation in progress (up to 4 h), (c) no qualifying prompts, (d) license gap. Investigate before declaring 'no incidents' as evidence."
}
```

---

## 6 — Inventory: policies, rules, and labels (read-only)

```powershell
# Policy inventory (note: filter on Mode, not Enabled)
$policies = Get-DlpCompliancePolicy | Select-Object Name, Mode, Workload, Locations, CreatedBy, WhenCreated, WhenChanged
Write-FsiEvidence -InputObject $policies -Name 'dlp-policies-inventory' -EvidencePath $EvidencePath -As Csv

# Rule inventory (per policy)
$rules = foreach ($p in $policies) {
    Get-DlpComplianceRule -Policy $p.Name -ErrorAction SilentlyContinue |
        Select-Object @{n='Policy';e={$p.Name}}, Name, Priority, Disabled, BlockAccess,
                      EnforcementPlanes, NotifyUser, NotifyEndpointUser,
                      ContentContainsSensitiveInformation, AdvancedRule
}
Write-FsiEvidence -InputObject $rules -Name 'dlp-rules-inventory' -EvidencePath $EvidencePath
```

> **Anti-pattern reminder:** `Get-DlpCompliancePolicy | Where-Object { $_.Enabled -eq $true }` is wrong — DLP compliance policies use `Mode` (`Enable` / `TestWithNotifications` / `TestWithoutNotifications` / `Disable` / `PendingDeletion`), not a Boolean `Enabled`.

---

## 7 — Wrapper: orchestration with transcript + teardown

```powershell
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string] $UPN,
    [Parameter(Mandatory)] [string] $TenantId,
    [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud,
    [Parameter(Mandatory)] [string] $EvidencePath,
    [string] $PolicyName = 'FSI-Copilot-DLP',
    [string] $HighlyConfidentialLabelGuid,
    [switch] $TestMode
)

$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null

$ts         = Get-Date -Format 'yyyyMMdd-HHmmss'
$transcript = Join-Path $EvidencePath "Control-1.5_${TenantId}_${Cloud}_Transcript_$ts.log"
Start-Transcript -Path $transcript -IncludeInvocationHeader

try {
    # --- Connect (sovereign-aware) ---
    switch ($Cloud) {
        'Commercial' {
            Connect-ExchangeOnline -UserPrincipalName $UPN -ShowBanner:$false
            Connect-IPPSSession    -UserPrincipalName $UPN
            Connect-MgGraph        -Environment Global  -Scopes 'InformationProtectionPolicy.Read.All' -NoWelcome
        }
        'GCC' {
            Connect-ExchangeOnline -UserPrincipalName $UPN -ShowBanner:$false
            Connect-IPPSSession    -UserPrincipalName $UPN `
                -ConnectionUri 'https://ps.compliance.protection.outlook.com/powershell-liveid/' `
                -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.com/common'
            Connect-MgGraph        -Environment USGov   -Scopes 'InformationProtectionPolicy.Read.All' -NoWelcome
        }
        'GCCHigh' {
            Connect-ExchangeOnline -UserPrincipalName $UPN -ExchangeEnvironmentName O365USGovGCCHigh -ShowBanner:$false
            Connect-IPPSSession    -UserPrincipalName $UPN `
                -ConnectionUri 'https://ps.compliance.protection.office365.us/powershell-liveid/' `
                -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/common'
            Connect-MgGraph        -Environment USGov   -Scopes 'InformationProtectionPolicy.Read.All' -NoWelcome
        }
        'DoD' {
            Connect-ExchangeOnline -UserPrincipalName $UPN -ExchangeEnvironmentName O365USGovDoD -ShowBanner:$false
            Connect-IPPSSession    -UserPrincipalName $UPN `
                -ConnectionUri 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/' `
                -AzureADAuthorizationEndpointUri 'https://login.microsoftonline.us/common'
            Connect-MgGraph        -Environment USGovDoD -Scopes 'InformationProtectionPolicy.Read.All' -NoWelcome
        }
    }

    Test-PreFlight -UPN $UPN -Cloud $Cloud -EvidencePath $EvidencePath | Out-Null

    # --- Read-only audit (always safe) ---
    # Section 2, 4, 5, 6 invocations go here (omitted for brevity; copy from sections above)

    # --- Mutations gated by ShouldProcess + presence of label GUID ---
    if ($HighlyConfidentialLabelGuid -and
        $PSCmdlet.ShouldProcess($PolicyName, "Create Copilot DLP policy + 2 rules (mode=$(if($TestMode){'TestWithNotifications'}else{'Enable'}))")) {
        # Section 1 invocation (omitted)
    } else {
        Write-Information "Mutation skipped (use -HighlyConfidentialLabelGuid '<guid>' -Confirm:`$false to apply, or -WhatIf to preview)." -InformationAction Continue
    }
}
finally {
    try { Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue } catch {}
    try { Disconnect-MgGraph -ErrorAction SilentlyContinue }                              catch {}
    Stop-Transcript | Out-Null

    # Hash the transcript so the audit trail itself has integrity
    if (Test-Path $transcript) {
        $h = (Get-FileHash -Path $transcript -Algorithm SHA256).Hash
        $manifestPath = Join-Path $EvidencePath 'manifest.json'
        $manifest = @()
        if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
        $manifest += [pscustomobject]@{
            file           = (Split-Path $transcript -Leaf)
            sha256         = $h
            bytes          = (Get-Item $transcript).Length
            generated_utc  = (Get-Date).ToUniversalTime().ToString('o')
            script_version = '1.5-v1.4'
        }
        $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
    }
}
```

> **Always invoke first with `-WhatIf`.** The wrapper supports `SupportsShouldProcess` end-to-end; `-WhatIf` emits the planned `New-DlpCompliancePolicy` / `New-DlpComplianceRule` calls without applying them, which is the difference between an undo-able config change and a production incident.

---

## Anti-patterns (each one was a real defect found in v1.3 of this file)

| Anti-pattern | Why it's wrong | Correct pattern |
|---|---|---|
| `Get-MgBetaInformationProtectionSensitivityPolicyLabel` | Cmdlet does not exist | `Get-MgBetaSecurityInformationProtectionSensitivityLabel` |
| `Search-UnifiedAuditLog -RecordType DLP` | `DLP` is not a valid `RecordType` enum value — silent zero rows | Use `ComplianceDLPSharePoint`, `ComplianceDLPExchange`, `DLPEndpoint`; for Copilot, filter `-Operations 'DLPRuleMatch'` then payload `Workload -eq 'Applications'` |
| Mapping API `Confidential -> Non-Business` and `General -> Business` in connector audit | Power Platform DLP API uses **inverted** vocabulary vs the UI | Use `ConvertTo-FsiUiLabel` (`Confidential -> Business`, `General -> Non-Business`) and emit **both** values |
| `ContentPropertyContainsWords = @{ 'Document.SensitivityLabel' = 'Highly Confidential' }` | Parameter is `MultiValuedProperty` (string[]); label match for Copilot location requires `-AdvancedRule` | `-AdvancedRule` JSON with `ContentContainsSensitivityLabel` referencing the label **GUID** |
| `NotifyEndpointUser = 'NotifyUser'` | Parameter is Boolean | `NotifyEndpointUser = $true` (or `$false`) |
| `NotifyUser = 'SiteAdmin,LastModifier'` | Parameter is string array | `NotifyUser = @('SiteAdmin','LastModifier')` |
| Copilot-DLP policy using only `ExchangeLocation`/`SharePointLocation`/`OneDriveLocation`/`TeamsLocation` | Legacy locations do **not** cover Copilot — false-clean evaluation | Use `-Locations` JSON with `Workload = 'Applications'` and `EnforcementPlanes = @('CopilotExperiences')` from a **Custom**-template policy |
| Combining SIT + Sensitivity Label conditions in one Copilot rule | Portal blocks; cmdlet accepts but behaviour is undefined | Split into two rules in the same policy |
| `Get-DlpCompliancePolicy \| Where-Object { $_.Enabled -eq $true }` | Property is `Mode`, not `Enabled` | Filter on `Mode -eq 'Enable'` |
| `Install-Module -Name X -Force` without `-RequiredVersion` | Floating versions break SOX 404 / OCC 2023-17 reproducibility evidence | Pin via `#Requires -Modules @{...; RequiredVersion='...'}` |
| Running Power Platform Admin cmdlets from PowerShell 7 | Module is Desktop-only — silent empties | Add the PSEdition guard from the baseline; run from Windows PowerShell 5.1 |
| Hard-coded `admin@contoso.com` UPN | Must be parameterized for CAB approval | `-UPN` parameter |
| Creating DLP policies in `Enable` mode on first deployment | Bypasses 4-hour propagation validation window | Start in `TestWithNotifications`; promote to `Enable` after validation |

---

## Cross-references

- [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md)
- [Control 1.5 — Portal Walkthrough](portal-walkthrough.md)
- [Control 1.5 — Verification & Testing](verification-testing.md)
- [Control 1.5 — Troubleshooting](troubleshooting.md)
- [Control 1.6 — DSPM for AI (PowerShell Setup)](../1.6/powershell-setup.md) — pairs `CopilotInteraction` audit evidence with this control's DLP rule-match evidence
- [Control 1.7 — Audit Log Retention (PowerShell Setup)](../1.7/powershell-setup.md) — durable storage for the evidence emitted here
- Microsoft Learn — [New-DlpCompliancePolicy](https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy)
- Microsoft Learn — [New-DlpComplianceRule](https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancerule)
- Microsoft Learn — [Get-DlpComplianceRule](https://learn.microsoft.com/en-us/powershell/module/exchange/get-dlpcompliancerule)
- Microsoft Learn — [Search-UnifiedAuditLog](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog)
- Microsoft Learn — [Connect-IPPSSession](https://learn.microsoft.com/en-us/powershell/module/exchange/connect-ippssession)
- Microsoft Learn — [Learn about the Microsoft 365 Copilot and Copilot Chat DLP location](https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about)
- Microsoft Learn — [New-DlpPolicy (Power Platform Administration)](https://learn.microsoft.com/en-us/powershell/module/microsoft.powerapps.administration.powershell/new-dlppolicy)
- Microsoft Learn — [Get-MgBetaSecurityInformationProtectionSensitivityLabel](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.beta.security/get-mgbetasecurityinformationprotectionsensitivitylabel)
- Microsoft Learn — [Microsoft Graph PowerShell installation (sovereign clouds)](https://learn.microsoft.com/en-us/powershell/microsoftgraph/installation)

[Back to Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*
