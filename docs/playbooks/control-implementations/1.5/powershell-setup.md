# Control 1.5 — PowerShell Setup: DLP and Sensitivity Labels

> **Scope.** This playbook automates **inventory, drift detection, and bounded mutation** for Microsoft Purview DLP, sensitivity labels, sensitive-information types (SITs), exact-data-match (EDM) classifiers, keyword dictionaries, Power Platform DLP, and the cross-surface settings that make Control 1.5 enforceable for Microsoft 365 Copilot and agentic workloads in US financial services tenants.
>
> **What this is.** An authoring guide with inventory building blocks. Status-bearing examples use `Clean | Anomaly | Pending | NotApplicable | Error`; inventory alone does not establish enforcement. Load and validate evidence tooling separately before producing an attestation pack.
>
> **What this isn't.** A substitute for the [portal walkthrough](portal-walkthrough.md), the [verification & testing](verification-testing.md) playbook, or [troubleshooting](troubleshooting.md). It also does not replace tenant-specific risk acceptance for preview features.
>
> **Hedged-language reminder.** PowerShell coverage of Purview DLP **supports compliance with** FINRA 3110 / SEC 17a-4 / GLBA / SOX recordkeeping and supervision obligations. It does not, by itself, *guarantee* compliance — implementation requires policy targeting, label deployment, end-user training, and exception governance.

---

## Metadata

| Field | Value |
|---|---|
| Control ID | 1.5 |
| Pillar | 1 — Security |
| Playbook | PowerShell setup (companion to portal walkthrough, verification, troubleshooting) |
| PowerShell editions | PS 7.4+ for Graph + Exchange; **PS 5.1 Desktop required** for `Microsoft.PowerApps.Administration.PowerShell` mutation cmdlets |
| Cloud | Commercial (Global) |
| Companion playbooks | [portal-walkthrough](portal-walkthrough.md) · [verification-testing](verification-testing.md) · [troubleshooting](troubleshooting.md) |
| Related controls | [1.6 DSPM for AI](../1.6/portal-walkthrough.md) · [1.10 Communication Compliance](../1.10/portal-walkthrough.md) · [1.12 IRM](../1.12/portal-walkthrough.md) · [1.13 SITs/EDM](../1.13/portal-walkthrough.md) · [1.15 DKE/encryption](../1.15/portal-walkthrough.md) · [2.12 Supervision](../2.12/portal-walkthrough.md) · [3.4 Incident reporting](../3.4/portal-walkthrough.md) · [3.9 Sentinel forwarding](../3.9/portal-walkthrough.md) |
| Baseline | [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) |

**Last Verified:** 2026-10-16 — Microsoft Learn review of the verification dependencies below; no tenant execution or UI verification. Examples are building blocks, not a deployable verifier suite. `Test-PreFlight` and `Get-FsiVerifierRollup` are not supplied here.

---

## §0 — READ FIRST: Wrong-shell trap & DLP false-clean defects

Three failure modes silently produce **false-clean evidence** for Control 1.5. Reviewers who do not read this section will sign off on policies that were never actually inspected.

| # | Trap | False-clean symptom | Remediation |
|---|---|---|---|
| 1 | **Wrong DLP plane.** `Get-DlpCompliancePolicy` (Purview) and `Get-DlpPolicy` (Power Platform) are **different cmdlets in different connections**. Running only the first returns "0 anomalies" while every connector policy is missing. | M365 DLP looks complete; connector classification gap is invisible. | Always run **both** planes. The §13 wrapper enforces this; ad-hoc scripts must too. |
| 2 | **Power Platform UI/API label inversion.** API value `Confidential` renders in the Maker portal as **Business**; API `General` renders as **Non-Business**; `Blocked` is `Blocked`. A reviewer comparing a script that prints `General` against a screenshot showing `Non-Business` will (correctly) think they match — and miss that the *intent* was Business. | Connector evidence reads as "expected" but the API label is opposite of the documented business decision. | Always emit **both** labels via `ConvertTo-FsiUiLabel` (§9). |
| 3 | **Audit RecordType = DLP is invalid.** `Search-UnifiedAuditLog -RecordType DLP` returns zero rows on every tenant. Real record types are `ComplianceDLPSharePoint`, `ComplianceDLPSharePointClassification`, `ComplianceDLPExchange`, `ComplianceDLPExchangeClassification`, `DLPEndpoint`. For Copilot, query `-Operations 'DLPRuleMatch'` and filter the payload `Workload -eq 'Applications'`. | "No DLP events in 30 days" — looks like a clean tenant; actually a broken query. | Use the helper `Get-FsiDlpAuditEvents` in §11. |

A fourth trap — **shell mismatch** — is enforced as a guard:

```powershell
# Shell guard — paste at the top of every Control 1.5 script
if ($PSVersionTable.PSEdition -ne 'Core' -and $PSVersionTable.PSVersion.Major -lt 7) {
    # Allowed: PS 5.1 Desktop is required for Power Apps Admin mutation cmdlets (see §9)
    Write-Warning 'Running on PS 5.1 Desktop. Graph + Exchange helpers will work; Power Apps Admin mutations are supported here. For Graph performance, prefer PS 7.4+ in a separate session.'
}
```

---

## §1 — Module / CLI / permission matrix

Pin every module via `Install-Module -RequiredVersion` per the [baseline](../../_shared/powershell-baseline.md). Do not use `-Force` to silently upgrade in production.

| Module | Min version | Edition | Used for | Connect cmdlet | Least-privilege role |
|---|---|---|---|---|---|
| `ExchangeOnlineManagement` | 3.4.0 | PS 7.4+ | Purview DLP, sensitivity labels, label policies, auto-label rules, EDM, dictionaries | `Connect-IPPSSession` | Purview Compliance Admin (or scoped Information Protection Admin + DLP Compliance Mgmt) |
| `Microsoft.Graph.Authentication` | 2.20.0 | PS 7.4+ | Tokens for downstream Graph calls | `Connect-MgGraph` | n/a (delegated by app role) |
| `Microsoft.Graph.Beta.Security` | 2.20.0 | PS 7.4+ | `Get-MgBetaSecurityInformationProtectionSensitivityLabel` (label tenant inventory) | n/a | `InformationProtectionPolicy.Read.All` |
| `Microsoft.Graph.Beta.Compliance` | 2.20.0 | PS 7.4+ | DSPM-for-AI cross-link (Control 1.6) | n/a | `InformationProtectionPolicy.Read.All` |
| `Microsoft.Online.SharePoint.PowerShell` *or* `PnP.PowerShell` | 16.0.25410 / 2.4.0 | PS 7.4+ | SharePoint/OneDrive label-default + DLP scoping | `Connect-SPOService` / `Connect-PnPOnline` | SharePoint Admin |
| `Microsoft.PowerApps.Administration.PowerShell` | 2.0.190 | **PS 5.1 Desktop only** | `Get-DlpPolicy`, `New-DlpPolicy`, `Add-ConnectorToPolicy`, `Set-ConnectorGroup` | `Add-PowerAppsAccount` | Power Platform Admin |
| `Microsoft.PowerApps.PowerShell` | 1.0.34 | PS 5.1 Desktop | Maker-side enumeration | `Add-PowerAppsAccount` | Power Platform Admin |

**Edition guard.** Any helper that calls a `*-DlpPolicy` (Power Platform) cmdlet must be invoked from PS 5.1 Desktop:

```powershell
function Assert-FsiDesktopPowerShell {
    if ($PSVersionTable.PSEdition -ne 'Desktop') {
        throw 'Power Platform DLP cmdlets require PowerShell 5.1 Desktop. Open Windows PowerShell (not pwsh.exe) and re-run.'
    }
}
```

---

## §2 — Authentication bootstrap (`Initialize-FsiDlpSession`)

Connect to the commercial endpoint using the default parameters:

For certificate authentication, `-Organization` must be the tenant's primary `.onmicrosoft.com` domain, not its GUID. Verify the actual connected tenant separately; connection success is not a control attestation. See [Connect-IPPSSession](https://learn.microsoft.com/en-us/powershell/module/exchange/connect-ippssession).

```powershell
function Initialize-FsiDlpSession {
    [CmdletBinding()]
    param(
        [ValidateSet('Commercial')] [string]$Cloud = 'Commercial',

        [Parameter(Mandatory)] [string]$TenantId,
        [Parameter(Mandatory)] [string]$UserPrincipalName,

        # Optional service-principal-with-certificate flow for unattended runs
        [string]$AppId,
        [string]$Organization,
        [string]$CertificateThumbprint
    )

    $ippsCfg = 'https://ps.compliance.protection.outlook.com/powershell-liveid/'


    # Purview / Exchange (IPPS)
    if ($AppId -and $CertificateThumbprint) {
        if (-not $Organization) { throw 'Provide the primary tenant.onmicrosoft.com domain in -Organization.' }
        Connect-IPPSSession -ConnectionUri $ippsCfg -AppId $AppId -CertificateThumbprint $CertificateThumbprint -Organization $Organization -ShowBanner:$false
    } else {
        Connect-IPPSSession -ConnectionUri $ippsCfg -UserPrincipalName $UserPrincipalName -ShowBanner:$false
    }

    # Optional Graph user-label reads use delegated InformationProtectionPolicy.Read.
    # Organization-wide Graph label inventory requires separate application authentication.

    # Power Platform (only on PS 5.1 Desktop)
    if ($PSVersionTable.PSEdition -eq 'Desktop') {
        Add-PowerAppsAccount -TenantID $TenantId | Out-Null
    } else {
        Write-Warning 'Skipping Add-PowerAppsAccount: not on PS 5.1 Desktop. Power Platform DLP helpers will return Status=Pending.'
    }

    [pscustomobject]@{
        Status      = 'Pending'
        Cloud       = $Cloud
        TenantId    = $TenantId
        IppsUri     = $ippsCfg
        PowerAppsEp = 'prod'
        Note        = 'Confirm actual tenant identity/permissions in each connected plane; Graph is not connected by this helper.'
        Timestamp   = (Get-Date).ToUniversalTime()
    }
}
```

---

## §3 — Helper library overview

| # | Helper | Purpose | Returns `Status` |
|---|---|---|---|
| 1 | `Get-FsiDlpCoverage` (§4) | Inventory supported Purview location properties; separately review other planes | `Pending`; inventory gaps alone are not enforcement findings |
| 2 | `Get-FsiCopilotDlpPolicies` (§5) | Export Copilot policies/rules for manual condition/action review | `Pending`; inventory is not enforcement proof |
| 3 | `Test-FsiPolicyTipOverrideSettings` (§6) | Inspect explicitly selected override-capable policies; then test capture | `Pending` / `Anomaly`; excludes Copilot processing restrictions |
| 4 | `Get-FsiSensitivityLabelInventory` (§7) | Export labels and label policies from IPPS for assignment/client review | `Pending`; inventory is not publication proof |
| 5 | `Get-FsiAdaptiveProtectionStatus` (§10) | Record the need for portal validation of Adaptive Protection | `Pending`; does not verify rollout or rule scope |

Auxiliary (non-status-bearing) utilities introduced inline: `ConvertTo-FsiUiLabel` (§9), `Get-FsiDlpAuditEvents` (§11), `Invoke-FsiControl15Audit` (§13).

---

## §4 — DLP cmdlet inventory + `Get-FsiDlpCoverage`

The 13 enforcement surfaces tracked by Control 1.5 (the on-prem AIP scanner is recognised in the control doc but is portal-only and out of PS scope):

1. SharePoint sites · 2. OneDrive accounts · 3. Exchange email · 4. Teams chat & channel · 5. Devices (Endpoint DLP) · 6. Copilot — block by sensitivity label (GA) · 7. Copilot — block by SIT (preview) · 8. Power Platform connector classification · 9. Power Platform HTTP endpoint filtering (preview) · 10. Edge for Business unmanaged AI · 11. Network data security for unmanaged AI (portal evidence) · 12. Defender for Cloud Apps · 13. Power BI / Fabric workspaces. Check preview status per subfeature, not for the entire browser/network plane.

**Cmdlet inventory (Purview plane).** `Get-DlpCompliancePolicy`, `Get-DlpComplianceRule`, `New-DlpCompliancePolicy`, `Set-DlpCompliancePolicy`, `New-DlpComplianceRule`, `Set-DlpComplianceRule`, `Remove-DlpCompliancePolicy`. Note: DLP policies use the **`Mode`** parameter (`Enable | TestWithNotifications | TestWithoutNotifications | Disable | PendingDeletion`) — there is no `Enabled` Boolean.

```powershell
function Get-FsiDlpCoverage {
    [CmdletBinding()]
    param()

    $surfaces = @(
        'SharePoint','OneDriveForBusiness','ExchangeLocation','TeamsLocation',
        'EndpointDevices','Copilot','PowerPlatform',
        'EdgeBrowser','NetworkUnmanagedAi','DefenderForCloudApps','PowerBIWorkspaces','OnPremScanner'
    )

    $policies = Get-DlpCompliancePolicy -ErrorAction Stop
    $covered  = @{}
    foreach ($s in $surfaces) { $covered[$s] = $false }

    foreach ($p in $policies) {
        if ($p.Mode -ne 'Enable') { continue }
        if ($p.SharePointLocation)      { $covered.SharePoint = $true }
        if ($p.OneDriveLocation)        { $covered.OneDriveForBusiness = $true }
        if ($p.ExchangeLocation)        { $covered.ExchangeLocation = $true }
        if ($p.TeamsLocation)           { $covered.TeamsLocation = $true }
        if ($p.EndpointDlpLocation)     { $covered.EndpointDevices = $true }
        if ($p.EnforcementPlanes -contains 'CopilotExperiences') { $covered.Copilot = $true }
        if ($p.PowerBIDlpLocation)      { $covered.PowerBIWorkspaces = $true }
    }

    $gaps = $covered.GetEnumerator() | Where-Object { -not $_.Value } | Select-Object -ExpandProperty Key

    [pscustomobject]@{
        Status        = 'Pending'
        PolicyCount   = $policies.Count
        SurfacesCovered = ($covered.GetEnumerator() | Where-Object { $_.Value } | Select-Object -ExpandProperty Key)
        SurfacesMissing = $gaps
        Note          = 'Partial policy inventory only. Validate enabled rules, scope, exceptions and positive tests; verify other control planes separately. Missing entries here are not proof of missing protection.'
        Timestamp     = (Get-Date).ToUniversalTime()
    }
}
```

---

## §5 — Copilot DLP policy creation & `Get-FsiCopilotDlpPolicies`

Copilot DLP requires the Purview UI **Custom** template. Current [New-DlpCompliancePolicy Example 4](https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy) uses `Locations` and policy-level `EnforcementPlanes`, not `MicrosoftCopilotEnabledLocation` or rule-level `EnforcementPlanes`.

1. **You cannot combine SIT and sensitivity-label conditions in the same rule.** Use two rules in the same policy.
2. Include the Copilot application location ID and explicit inclusions/exclusions. The read-back must confirm the approved scope. Do not assume returned rule properties or JSON nesting are identical across module/service versions.

```powershell
$copilotLocations = ConvertTo-Json -Depth 10 -Compress -InputObject @(
    @{
        Workload = 'Applications'
        Location = '470f2276-e011-4e9d-a6ec-20768be3a4b0'
        Inclusions = @(@{ Type = 'IndividualResource'; Identity = '<test-user-upn>' })
    }
)

New-DlpCompliancePolicy `
    -Name 'FSI-Copilot-MNPI-Block' `
    -Locations $copilotLocations `
    -EnforcementPlanes @('CopilotExperiences') `
    -Mode 'TestWithNotifications' `
    -WhatIf

# Rule A — label condition, following the documented advanced-rule example
$advancedRule = @{
    Version = '1.0'
    Condition = @{
        Operator = 'And'
        SubConditions = @(
            @{
                ConditionName = 'ContentContainsSensitiveInformation'
                Value = @(
                    @{
                        groups = @(
                            @{
                                Operator = 'Or'
                                labels = @(@{ name = '<label-guid>'; type = 'Sensitivity' })
                                name = 'Default'
                            }
                        )
                    }
                )
            }
        )
    }
} | ConvertTo-Json -Depth 100

New-DlpComplianceRule `
    -Name 'BlockHighlyConfidentialFromCopilot' `
    -Policy 'FSI-Copilot-MNPI-Block' `
    -AdvancedRule $advancedRule `
    -RestrictAccess @(@{ setting = 'ExcludeContentProcessing'; value = 'Block' }) `
    -WhatIf
```

`-WhatIf` does not create the policy; an approved real policy must exist before creating a real rule. Author the separate preview prompt rule through the [documented Copilot portal procedure](portal-walkthrough.md#63-same-rule-restriction-author-two-separate-rules-in-the-same-policy), selecting **Processing prompts** rather than a generic `BlockAccess` action. **Performing Web Searches** is a different restriction.

Existing illustrative notification copy: “This content is restricted from Copilot grounding under FINRA 3110 / SEC 17a-4 controls.” Do not assume Copilot supports a generic override or replacement of its standard block message; its custom compliance URL changes only the help-link destination.

```powershell
function Get-FsiCopilotDlpPolicies {
    [CmdletBinding()]
    param()

    $policies = Get-DlpCompliancePolicy -ErrorAction Stop |
        Where-Object { $_.EnforcementPlanes -contains 'CopilotExperiences' }
    $findings = foreach ($p in $policies) {
        $rules = @(Get-DlpComplianceRule -Policy $p.Name -ErrorAction Stop)

        [pscustomobject]@{
            Status        = 'Pending'
            Policy        = $p.Name
            Mode          = $p.Mode
            Locations     = $p.Locations
            Rules         = $rules
            RuleCount     = $rules.Count
            Note          = 'Review complete rule conditions/actions and scope, then run positive/negative tests. Inventory alone cannot return Clean.'
        }
    }
    if (-not $findings) {
        return [pscustomobject]@{ Status = 'Anomaly'; Policy = '<none>'; Note = 'No Copilot-scoped DLP policies found.' }
    }
    $findings
}
```

---

## §6 — Rules: notifications, overrides, policy tips

`Test-FsiPolicyTipOverrideSettings` validates that overrides require justification (a supervision-evidence requirement that supports compliance with FINRA Rule 3110).

```powershell
function Test-FsiPolicyTipOverrideSettings {
    [CmdletBinding()]
    param([string[]]$PolicyNames)

    if (-not $PolicyNames) {
        return [pscustomobject]@{ Status = 'Pending'; Note = 'Select policies whose workload/action explicitly supports user override; exclude Copilot processing restrictions.' }
    }
    $rules = $PolicyNames | ForEach-Object { Get-DlpComplianceRule -Policy $_ -ErrorAction Stop }

    $rules | ForEach-Object {
        $needsJustification = ($_.NotifyAllowOverride -contains 'WithJustification')
        $hasNotifyText = -not [string]::IsNullOrWhiteSpace($_.NotifyEmailCustomText)
        $status = if ($needsJustification) { 'Pending' } else { 'Anomaly' }
        [pscustomobject]@{
            Status                 = $status
            Rule                   = $_.Name
            Policy                 = $_.ParentPolicyName
            NotifyAllowOverride    = ($_.NotifyAllowOverride -join ',')
            NotifyUserType         = ($_.NotifyUser -join ',')
            HasCustomEmailText     = $hasNotifyText
        }
    }
}
```

---

## §7 — Sensitivity labels & label policies

**Optional Graph inventory.** The Graph beta cmdlet `Get-MgBetaSecurityInformationProtectionSensitivityLabel` reads organization labels with application authentication. Delegated `InformationProtectionPolicy.Read` applies to user-specific label reads, not this organization route. These are labels, not label policies. A user's published-label set can legitimately differ from the full Purview taxonomy; do not mark that difference as drift. See [List sensitivityLabels](https://learn.microsoft.com/en-us/graph/api/security-informationprotection-list-sensitivitylabels?view=graph-rest-beta).

Inventory: `Get-Label`, `Get-LabelPolicy`, `Get-AutoSensitivityLabelPolicy`, `Get-AutoSensitivityLabelRule`. Mutation: `New-Label`, `Set-Label`, `New-LabelPolicy`, `Set-LabelPolicy`, `New-AutoSensitivityLabelPolicy`, `New-AutoSensitivityLabelRule`.

```powershell
function Get-FsiSensitivityLabelInventory {
    [CmdletBinding()]
    param()

    $ippsLabels = @(Get-Label -ErrorAction Stop)
    $ippsPolicies = @(Get-LabelPolicy -ErrorAction Stop)

    [pscustomobject]@{
        Status             = 'Pending'
        IppsLabelCount     = $ippsLabels.Count
        PolicyCount        = $ippsPolicies.Count
        Labels             = $ippsLabels
        Policies           = $ippsPolicies
        Note               = 'Verify assignments and actual client publication separately; label and policy existence are inventory evidence only.'
    }
}
```

---

## §8 — SIT / EDM / dictionary authoring (cross-link to Control 1.13)

Read-side: `Get-DataClassification`, `Get-DlpSensitiveInformationType`, `Get-DlpEdmSchema`, `Get-DlpKeywordDictionary`. Custom regex SIT authoring uses rule-package XML cmdlets; `New-DlpSensitiveInformationType` is the fingerprint workflow. EDM schema changes use documented `Set-DlpEdmSchema`, not `Edit-DlpEdmSchema`. Follow Control 1.13's supported examples rather than treating schema existence as upload proof.

EDM is the canonical mechanism for **MNPI watchlists** (deal-codename rotations, restricted-list tickers). The schema and the upload pipeline live in [Control 1.13](../1.13/portal-walkthrough.md); from Control 1.5 the consumption pattern is:

```powershell
# Surface MNPI EDM and dictionary classifiers for use in DLP rules
$edm   = Get-DlpEdmSchema
$dicts = Get-DlpKeywordDictionary

$edm | Format-List *
$dicts | Format-List *
# Get-DlpEdmSchema is schema inventory, not an upload/row-count oracle.
# Capture EDM Upload Agent /GetDataStore and /GetSession separately.

# In a rule definition
# -ContentContainsSensitiveInformation @(@{ name = '<edmSitGuidMnpiTickers>'; mincount = 1 })
# Use only a supported consuming location; do not infer Copilot prompt EDM support.
```

Authoring an EDM-backed SIT and a dictionary (non-mutating preview):

```powershell
New-DlpEdmSchema -FileData ([Byte[]](Get-Content -Path .\mnpi-schema.xml -Encoding Byte -Raw)) -WhatIf
New-DlpKeywordDictionary -Name 'FSI-MNPI-Codenames' -Description 'Quarterly rotation' `
    -FileData ([Byte[]](Get-Content -Path .\mnpi-codenames.csv -Encoding Byte -Raw)) -WhatIf
```

---

## §9 — Power Platform DLP + UI/API label inversion

**Edition reminder.** Run from PS 5.1 Desktop (`Assert-FsiDesktopPowerShell` from §1). Cmdlets: `Get-DlpPolicy`, `New-DlpPolicy`, `Set-DlpPolicy`, `Remove-DlpPolicy`, `Add-PowerAppsPolicyToTenant`, `Add-ConnectorToPolicy`, `Set-ConnectorGroup`, `Remove-ConnectorFromPolicy`.

```powershell
function ConvertTo-FsiUiLabel {
    [CmdletBinding()]
    param([Parameter(Mandatory)][ValidateSet('Confidential','General','Blocked')] [string]$ApiLabel)
    switch ($ApiLabel) {
        'Confidential' { 'Business' }
        'General'      { 'Non-Business' }
        'Blocked'      { 'Blocked' }
    }
}

function Get-FsiPowerPlatformDlpInventory {
    [CmdletBinding()]
    param()
    Assert-FsiDesktopPowerShell

    $policies = Get-DlpPolicy
    $rows = foreach ($p in $policies) {
        foreach ($g in $p.Internal.properties.connectorGroups) {
            foreach ($c in $g.connectors) {
                [pscustomobject]@{
                    Status         = 'Pending'
                    Policy         = $p.DisplayName
                    Environment    = ($p.Internal.properties.environments | Select-Object -ExpandProperty name) -join ','
                    Connector      = $c.name
                    ConnectorId    = $c.id
                    ApiLabel       = $g.classification
                    UiLabel        = ConvertTo-FsiUiLabel -ApiLabel $g.classification
                }
            }
        }
    }
    if (-not $rows) {
        Write-Warning 'No connector rows returned. Review policy scope, module return shape and default-group gaps in the portal.'
        return [pscustomobject]@{ Status = 'Pending'; Note = 'No reviewable connector inventory; scope and enforcement remain unverified.' }
    }
    $rows
}
```

> **Evidence requirement.** Always emit **both** `ApiLabel` and `UiLabel`. A reviewer comparing a script that prints `General` against a Maker-portal screenshot showing `Non-Business` will conclude they match — and miss that the documented business decision was `Business` (`Confidential`).

Read back a full policy before adapting the projection to the installed module's return shape; missing connector groups or an empty inventory must not be treated as `Clean`. `Get-DlpPolicy` can omit newly added connectors still in the default group and retain stale display names. Compare against the live portal, document any gap, and do not mutate production classifications merely to refresh an inventory. Retrieve endpoint rules separately with `Get-PowerAppDlpPolicyConnectorConfigurations -TenantId <tenant-guid> -PolicyName <policy-guid>`; see [Power Platform PowerShell](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell) and [endpoint filtering](https://learn.microsoft.com/en-us/power-platform/admin/connector-endpoint-filtering).

---

## §10 — Adaptive Protection (`Get-FsiAdaptiveProtectionStatus`)

Adaptive Protection / Insider Risk-driven DLP requires a [portal configuration review](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection). The previous `Get-DlpAdaptiveProtectionConfiguration` example was not a documented cmdlet and is not an executable verification path.

```powershell
function Get-FsiAdaptiveProtectionStatus {
    [CmdletBinding()]
    param(
        [string] $Cloud = 'Commercial'
    )

    [pscustomobject]@{
        Status = 'Pending'
        Cloud = $Cloud
        Note = 'Capture IRM Adaptive Protection settings, risk-level scope and supported DLP rule conditions from the portal; this helper does not verify them.'
    }
}
```

---

## §11 — Audit log queries + Sentinel forwarding

**The trap is real.** `-RecordType DLP` is invalid and returns zero rows on every tenant. Use the explicit record types below; for Copilot, query `-Operations 'DLPRuleMatch'` and filter the payload `Workload -eq 'Applications'`.

```powershell
function Get-FsiDlpAuditEvents {
    [CmdletBinding()]
    param(
        [datetime]$StartDate = (Get-Date).AddDays(-7),
        [datetime]$EndDate   = (Get-Date)
    )

    $recordTypes = @(
        'ComplianceDLPSharePoint',
        'ComplianceDLPSharePointClassification',
        'ComplianceDLPExchange',
        'ComplianceDLPExchangeClassification',
        'DLPEndpoint'
    )

    $rows = foreach ($rt in $recordTypes) {
        Search-UnifiedAuditLog -StartDate $StartDate -EndDate $EndDate -RecordType $rt -ResultSize 5000 -ErrorAction Stop |
            Select-Object CreationDate, UserIds, Operations, RecordType, AuditData
    }

    $copilot = Search-UnifiedAuditLog -StartDate $StartDate -EndDate $EndDate -Operations 'DLPRuleMatch' -ResultSize 5000 |
        Where-Object { ($_.AuditData | ConvertFrom-Json).Workload -eq 'Applications' }

    [pscustomobject]@{
        Status         = 'Pending'
        ClassicEvents  = $rows.Count
        CopilotEvents  = $copilot.Count
        WindowStartUtc = $StartDate.ToUniversalTime()
        WindowEndUtc   = $EndDate.ToUniversalTime()
        Note           = 'Bounded inventory only, not exhaustive counts or pipeline health. Page/time-slice results and correlate a known event. Forwarding to Sentinel is owned by Control 3.9.'
    }
}
```

For the Sentinel forwarding pipeline (M365 connector, custom log table, KQL detection rules), see [Control 3.9](../3.9/portal-walkthrough.md).

---

## §12 — 13-surface walkthrough

| # | Surface | PowerShell coverage | Helper / cmdlet | Skip rationale |
|---|---|---|---|---|
| 1 | SharePoint sites | Configuration inventory | `Get-DlpCompliancePolicy` `.SharePointLocation` | Run scoped positive/negative tests |
| 2 | OneDrive accounts | Configuration inventory | `.OneDriveLocation` | Run scoped positive/negative tests |
| 3 | Exchange email | Configuration inventory | `.ExchangeLocation` | Run scoped positive/negative tests |
| 4 | Teams chat / channel | Configuration inventory | `.TeamsLocation` | Verify group/user scope and message/file behavior separately |
| 5 | Endpoint devices | Configuration inventory | `.EndpointDlpLocation` | Verify onboarding, supported activity and actual enforcement |
| 6 | Copilot — block by label (GA) | Configuration inventory | `Get-FsiCopilotDlpPolicies` | Authorized-user grounding test required |
| 7 | Copilot — block by SIT (preview) | Configuration inventory | `Get-FsiCopilotDlpPolicies` | Preview; verify Processing prompts action and tenant rollout |
| 8 | Power Platform connector classification | Configuration inventory (PS 5.1) | `Get-FsiPowerPlatformDlpInventory` | Compare module return shape/default connector gaps with portal |
| 9 | Power Platform HTTP endpoint filtering (preview) | Configuration inventory (PS 5.1) | `Get-PowerAppDlpPolicyConnectorConfigurations` | Static designer-known endpoints only; dynamic endpoints and HTTP with Entra ID Get web resource are excluded |
| 10 | Edge for Business unmanaged AI | Partial | `Get-DlpCompliancePolicy` (when surfaced) | Verify current subfeature availability and capture portal/enforcement evidence |
| 11 | Network data security for unmanaged AI | **None** | n/a | Capture integration-specific portal/enforcement evidence; check preview status per subfeature |
| 12 | Defender for Cloud Apps legacy file policies | Portal review | Defender Cloud Apps policy management | File policies retire January 6, 2027; plan migration to Purview |
| 13 | Power BI / Fabric workspaces | Configuration inventory | `.PowerBIDlpLocation` | Verify supported capacity, item, classifier and match separately |

---

## §13 — Wrapper orchestration with transcript & evidence manifest

Load the canonical `Write-FsiEvidence` from the [shared baseline §4](../../_shared/powershell-baseline.md) in a **versioned module** before invoking this example; its `script_version` field depends on `MyInvocation.MyCommand.Module.Version`. A missing or broken writer is an error, not permission to omit integrity evidence. Use a new output directory for each run. Local hashes prove integrity only; separately validate the archive's required retention/immutability configuration.

```powershell
function Invoke-FsiControl15Audit {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [string]$Cloud = 'Commercial',
        [Parameter(Mandatory)] [string]$TenantId,
        [Parameter(Mandatory)] [string]$UserPrincipalName,
        [string]$EvidencePath = (Join-Path $PWD ('control-15-' + (Get-Date -Format 'yyyyMMdd-HHmmss')))
    )

    $ErrorActionPreference = 'Stop'
    $writer = Get-Command Write-FsiEvidence -CommandType Function -ErrorAction Stop
    if ($null -eq $writer.Module -or $null -eq $writer.Module.Version) {
        throw 'Load the shared-baseline Write-FsiEvidence in a versioned module.'
    }
    if (Test-Path -LiteralPath $EvidencePath) {
        throw 'Choose a new evidence directory; do not mix or overwrite audit runs.'
    }
    New-Item -ItemType Directory -Path $EvidencePath | Out-Null
    $EvidencePath = (Resolve-Path -LiteralPath $EvidencePath).Path
    $artifactPaths = @()
    Start-Transcript -Path (Join-Path $EvidencePath 'transcript.log') | Out-Null

    try {
        $session = Initialize-FsiDlpSession -Cloud $Cloud -TenantId $TenantId -UserPrincipalName $UserPrincipalName
        Connect-ExchangeOnline -UserPrincipalName $UserPrincipalName -ShowBanner:$false

        $results = [ordered]@{
            session             = $session
            dlpCoverage         = Get-FsiDlpCoverage
            copilotPolicies     = Get-FsiCopilotDlpPolicies
            policyTipOverrides  = Test-FsiPolicyTipOverrideSettings
            labelInventory      = Get-FsiSensitivityLabelInventory
            adaptiveProtection  = Get-FsiAdaptiveProtectionStatus -Cloud $Cloud
            dlpAuditEvents      = Get-FsiDlpAuditEvents
        }

        if ($PSVersionTable.PSEdition -eq 'Desktop') {
            $results['powerPlatformDlp'] = Get-FsiPowerPlatformDlpInventory
        } else {
            $results['powerPlatformDlp'] = [pscustomobject]@{ Status = 'Pending'; Note = 'Run from PS 5.1 Desktop.' }
        }

        foreach ($k in $results.Keys) {
            $artifactPaths += Write-FsiEvidence -Object $results[$k] -Name $k -EvidencePath $EvidencePath
        }

        $rollup = @($results.GetEnumerator() | ForEach-Object {
            [pscustomobject]@{ Section = $_.Key; Status = $_.Value.Status }
        })
        $rollup | Format-Table -AutoSize | Out-String |
            Set-Content -LiteralPath (Join-Path $EvidencePath 'summary.txt') -Encoding UTF8
    } finally {
        Stop-Transcript | Out-Null
    }

    $manifestPath = Join-Path $EvidencePath 'manifest.json'
    $manifest = @(Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json)
    foreach ($name in @('summary.txt', 'transcript.log')) {
        $path = Join-Path $EvidencePath $name
        $artifactPaths += $path
        $manifest += [pscustomobject]@{
            file = $name
            sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash
            bytes = (Get-Item -LiteralPath $path).Length
            generated_utc = [datetime]::UtcNow.ToString('o')
            script_version = $writer.Module.Version.ToString()
        }
    }
    $manifest | ConvertTo-Json -Depth 5 |
        Set-Content -LiteralPath $manifestPath -Encoding UTF8
    $verified = @(Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json)
    if ($verified.Count -ne $artifactPaths.Count) { throw 'Evidence manifest count mismatch.' }
    foreach ($path in $artifactPaths) {
        $entry = @($verified | Where-Object { $_.file -eq (Split-Path $path -Leaf) })
        if ($entry.Count -ne 1 -or
            $entry[0].sha256 -ne (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -or
            $entry[0].bytes -ne (Get-Item -LiteralPath $path).Length) {
            throw "Missing or invalid evidence manifest entry: $path"
        }
    }
    $rollup
}
```

---

## §14 — Anti-patterns & cross-references

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Running only `Get-DlpCompliancePolicy` and declaring the tenant clean | Misses every Power Platform connector policy | Run both planes (§4 + §9) |
| `Search-UnifiedAuditLog -RecordType DLP` | Invalid record type — returns zero rows | Use the five record types in §11 |
| Combining SIT + sensitivity label conditions in one Copilot rule | Rule will not save, or will save with silent precedence | Two rules, same policy (§5) |
| Reporting Power Platform DLP labels as `Confidential` / `General` only | Inverted vs the Maker-portal UI; reviewers misread evidence | Emit both via `ConvertTo-FsiUiLabel` (§9) |
| Calling `Get-MgBetaInformationProtectionSensitivityPolicyLabel` | Cmdlet does not exist | Use `Get-MgBetaSecurityInformationProtectionSensitivityLabel` (§7) |
| Using `-Force` on `Install-Module` in production | Silent module upgrade breaks reproducibility | `Install-Module -RequiredVersion` per baseline §1 |
| Treating `Mode = 'Disable'` policies as active | They emit no enforcement | Filter on `Mode -eq 'Enable'` (§4) |
| Running Power Apps Admin cmdlets from `pwsh` 7.x | Cmdlets are Desktop-only; silently no-op or error | `Assert-FsiDesktopPowerShell` (§1) |

**Cross-references.** [1.6 DSPM for AI](../1.6/portal-walkthrough.md) consumes label + SIT signals from this control. [1.10 Communication Compliance](../1.10/portal-walkthrough.md) evaluates scoped communications; it does not automatically create a review item from a DLP override. Independently configure and test the firm's event-to-review integration under [2.12 Supervision](../2.12/portal-walkthrough.md). [1.12 IRM](../1.12/portal-walkthrough.md) supplies Adaptive Protection risk levels; it is not Information Rights Management or the label-encryption substrate. [1.15 DKE/encryption](../1.15/portal-walkthrough.md) addresses its separate encryption scope. [1.13 SITs/EDM](../1.13/portal-walkthrough.md) owns classifier authoring. [3.4 Incident reporting](../3.4/portal-walkthrough.md) and [3.9 Sentinel forwarding](../3.9/portal-walkthrough.md) own downstream telemetry.

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation reviewed; tenant examples not executed)*
