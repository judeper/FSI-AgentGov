# PowerShell Setup — Control 3.5: Cost Allocation and Budget Tracking

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below show the abbreviated patterns; the baseline is authoritative.

> **Control under management:** [`3.5 — Cost Allocation and Budget Tracking`](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md)
>
> **Sister playbooks:** [Portal Walkthrough](portal-walkthrough.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)
>
> **Namespace.** Internal helpers use the literal `Fsi35` prefix (e.g., `Assert-Fsi35ShellHost`, `Invoke-Fsi35CostQuery`). Public exports use the `Get-Fsi-*` / `New-Fsi-*` / `Test-Fsi-*` shape.

---

!!! warning "Non-Substitution"
    The helpers in this playbook **support** — they do not **replace** — the elements of the firm's cost-governance program that must be performed by named human officers:

    1. Approval and sign-off of the **rate card** by the Controller / CFO.
    2. **Variance investigation and memo authorship** by Finance and the AI Governance Lead.
    3. **Books-and-records retention** under SEC Rule 17a-4(b)(4) — exports landing in immutable storage are records; exports to mutable storage are operational data. The helpers below emit signed manifests but the immutability binding is the operator's responsibility (cross-reference [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)).
    4. **SOX 404 ITGC walkthrough sign-off** by external audit and Internal Audit.
    5. **Hard cost caps.** No helper here stops spend; budget alerts are notification-only. Cost-cap enforcement is a separate operational workflow (deactivate billing policy, remove Entra ID group membership, suspend agents via Control 2.1).

    Tooling **aids in** meeting these obligations. It does not satisfy them.

!!! danger "Status discipline — never return `$null` as a clean signal"
    Every helper in this playbook returns a `[pscustomobject]` with one of five `Status` values: **`Clean`**, **`Anomaly`**, **`Pending`**, **`NotApplicable`**, **`Error`**. When `Status -ne 'Clean'`, the `Reason` string is non-empty. **Helpers never return `$null` or `@()` to mean "all good."** Sovereign-cloud surfaces that do not exist return `NotApplicable` with a compensating-control pointer — never `Clean`.

---

## §0 Wrong-Shell Trap and False-Clean Defects

Cost helpers in particular are vulnerable to false-clean defects: an empty Cost Management response (because of throttling, wrong scope, or missing role) looks indistinguishable from a tenant that genuinely has no AI spend. Every helper below explicitly distinguishes these states.

### 0.1 Wrong-shell trap

- **`Microsoft.PowerApps.Administration.PowerShell` is Desktop-edition only** (Windows PowerShell 5.1). Running under PS 7.4 silently fails for capacity-reading cmdlets and emits empty arrays — interpreted as "no consumption" by naive callers.
- **`Az.CostManagement` and `Az.Billing` require PowerShell 7.4+ Core**. Loading them under PS 5.1 with WSMan can produce partial results or auth failures.
- **Azure Cloud Shell has no Power Platform module path.** Run from a privileged-access workstation (PAW) for any tenant subject to FINRA / SEC oversight.

```powershell
function Assert-Fsi35ShellHost {
    [CmdletBinding()]
    param([ValidateSet('Core74','Sidecar51')] [string]$RequiredHost = 'Core74')

    if ($RequiredHost -eq 'Sidecar51') {
        if ($PSVersionTable.PSEdition -ne 'Desktop' -or $PSVersionTable.PSVersion -lt [version]'5.1') {
            throw [System.InvalidOperationException]::new(
                "Fsi35-WrongShell: Power Platform Administration cmdlets require Windows PowerShell 5.1. Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion).")
        }
        return [pscustomobject]@{ Status='Clean'; Mode='Sidecar51'; PSVersion=$PSVersionTable.PSVersion.ToString(); Reason='' }
    }

    if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [version]'7.4') {
        throw [System.InvalidOperationException]::new(
            "Fsi35-WrongShell: PowerShell 7.4+ Core required for Az.CostManagement / Az.Billing / Microsoft.Graph. Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion).")
    }
    if ($Host.Name -eq 'Windows PowerShell ISE Host') {
        throw [System.InvalidOperationException]::new("Fsi35-WrongShell: ISE not supported.")
    }
    [pscustomobject]@{ Status='Clean'; Mode='Pwsh74'; PSVersion=$PSVersionTable.PSVersion.ToString(); Reason='' }
}
```

### 0.2 False-clean defect catalogue (Fsi35-specific)

| # | Defect | Symptom | Root cause | Mitigation in this playbook |
|---|--------|---------|------------|-----------------------------|
| 1 | Wrong shell | `Get-AdminPowerAppEnvironment` returns `@()` against tenants that obviously have environments | PS 7.4 host | `Assert-Fsi35ShellHost -RequiredHost Sidecar51` |
| 2 | Sovereign tenant treated as commercial | `Get-Fsi-CopilotBillingPolicy` returns `Clean / no policies` for a `.us` tenant where the surface is GCC-only | Connected to commercial Graph endpoint | `Resolve-Fsi35CloudProfile` (§2) routes to correct endpoint or returns `NotApplicable` |
| 3 | Read-only token used against export create | `New-Fsi-CostExport` 403s; helper swallows and reports "skipped" | Caller used `Cost Management Reader` only | `Test-Fsi35Rbac` preflight refuses to dispatch mutation helpers without write role |
| 4 | Throttled cost query returns empty | `Invoke-AzCostManagementQuery` returns `200 OK` with empty rows on throttle | No retry/backoff | `Invoke-Fsi35CostQuery` (§3) honours `Retry-After`, raises `Status='Error'` after 3 retries |
| 5 | Empty result conflated with "no spend" | Helper returns `$null` or `@()`; downstream chargeback emits `$0.00` for a real BU | Helpers must distinguish `Clean` (no spend confirmed) from `NotApplicable` (surface absent) from `Error` | All helpers return explicit `Status` enum |
| 6 | Cached delegated token from prior tenant | Helper enumerates the wrong tenant's costs | Operator switched tenants without disconnect | `Initialize-Fsi35Session` always disconnects first |
| 7 | Random/stub data treated as production | A development helper using `Get-Random` is committed and runs in prod, producing fake chargeback | Stubs not gated | `[Fsi35Mode]::Production` enforced via env var; stubs throw under prod |
| 8 | Pricing baked into helper | Hard-coded `$0.01` per message used after Microsoft re-priced the SKU; chargeback is now wrong | Rate card not externalised | `Get-Fsi35RateCard` reads the CFO-approved rate card from a versioned storage location and refuses to operate without a current version |
| 9 | Export lands in mutable blob | Cost export written to a regular Storage account; treated as evidence; not a 17a-4(b)(4) record | No immutability binding | `Test-Fsi-Control35-ExportImmutability` flags `Anomaly` if the target container lacks an active immutability policy |
| 10 | License-utilization stale | Inactive-seat report missed weeks of usage data | Microsoft Graph reports lag 24–72h; report consumer assumed real-time | `Get-Fsi-CopilotLicenseUtilization` annotates results with `DataLagHours` and refuses to mark `Clean` for periods inside the lag window |

### 0.3 Mode gating — production vs sandbox

```powershell
$script:Fsi35Mode = if ($env:FSI_MODE) { $env:FSI_MODE } else { 'Sandbox' }

function Assert-Fsi35Mode {
    param([Parameter(Mandatory)][ValidateSet('Sandbox','Production')] [string]$RequiredMode)
    if ($script:Fsi35Mode -ne $RequiredMode) {
        throw [System.InvalidOperationException]::new(
            "Fsi35-WrongMode: Helper requires `$env:FSI_MODE = '$RequiredMode'; current = '$script:Fsi35Mode'.")
    }
}
```

Stub or random-data helpers below are guarded with `Assert-Fsi35Mode -RequiredMode 'Sandbox'` so they cannot be invoked in production.

---

## §1 Module Pinning, RBAC Matrix, and Preview Gating

### 1.1 Module version matrix

Pin exact minimum versions. Floating versions break SOX 404 reproducibility.

```powershell
$Fsi35ModuleMatrix = @(
    @{ Name = 'Az.Accounts';                                     Min = '2.16.0'  ; Edition = 'Core'    },
    @{ Name = 'Az.CostManagement';                               Min = '0.4.0'   ; Edition = 'Core'    },
    @{ Name = 'Az.Billing';                                      Min = '2.2.0'   ; Edition = 'Core'    },
    @{ Name = 'Az.Resources';                                    Min = '6.16.0'  ; Edition = 'Core'    },
    @{ Name = 'Az.PolicyInsights';                               Min = '1.6.0'   ; Edition = 'Core'    },
    @{ Name = 'Az.Storage';                                      Min = '6.0.0'   ; Edition = 'Core'    },
    @{ Name = 'Microsoft.Graph.Authentication';                  Min = '2.25.0'  ; Edition = 'Core'    },
    @{ Name = 'Microsoft.Graph.Reports';                         Min = '2.25.0'  ; Edition = 'Core'    },
    @{ Name = 'Microsoft.Graph.Identity.DirectoryManagement';    Min = '2.25.0'  ; Edition = 'Core'    },
    @{ Name = 'Microsoft.PowerApps.Administration.PowerShell';   Min = '2.0.175' ; Edition = 'Desktop' }
)

function Test-Fsi35ModuleMatrix {
    [CmdletBinding()] param([switch]$InstallMissing)
    $rows = foreach ($m in $Fsi35ModuleMatrix) {
        $isDesktopOnly = ($m.Edition -eq 'Desktop')
        $hostMatchesEdition = -not ($isDesktopOnly -and $PSVersionTable.PSEdition -ne 'Desktop')
        $installed = Get-Module -ListAvailable -Name $m.Name |
            Sort-Object Version -Descending | Select-Object -First 1
        $status = if (-not $hostMatchesEdition) { 'NotApplicable-WrongEdition' }
                  elseif (-not $installed)        { 'Missing' }
                  elseif ($installed.Version -lt [version]$m.Min) { 'Outdated' }
                  else { 'OK' }
        if (($status -in @('Missing','Outdated')) -and $InstallMissing -and $hostMatchesEdition) {
            Install-Module -Name $m.Name -RequiredVersion $m.Min -Scope CurrentUser `
                -Repository PSGallery -AllowClobber -AcceptLicense
            $status = 'Installed'
        }
        [pscustomobject]@{ Module=$m.Name; Required=$m.Min; Edition=$m.Edition;
            Installed = if ($installed) { $installed.Version.ToString() } else { '' };
            Status=$status }
    }
    $bad = $rows | Where-Object { $_.Status -in @('Missing','Outdated') }
    [pscustomobject]@{
        Status  = if ($bad) { 'Anomaly' } else { 'Clean' }
        Modules = $rows
        Reason  = if ($bad) { "Missing/outdated: $($bad.Module -join ', ')" } else { '' }
    }
}
```

### 1.2 RBAC preflight

```powershell
function Test-Fsi35Rbac {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$SubscriptionId,
        [ValidateSet('Read','Write')] [string]$Mode = 'Read'
    )
    $required = if ($Mode -eq 'Write') {
        @('Cost Management Contributor','Resource Policy Contributor')
    } else {
        @('Cost Management Reader')
    }
    $ctx = Set-AzContext -Subscription $SubscriptionId
    $upn = $ctx.Account.Id
    $assignments = Get-AzRoleAssignment -SignInName $upn -Scope "/subscriptions/$SubscriptionId" -ErrorAction SilentlyContinue
    $missing = $required | Where-Object { $_ -notin $assignments.RoleDefinitionName }

    [pscustomobject]@{
        Status  = if ($missing) { 'Anomaly' } else { 'Clean' }
        UPN     = $upn
        Subscription = $SubscriptionId
        Missing = $missing
        Reason  = if ($missing) { "Missing roles: $($missing -join ', ')" } else { '' }
    }
}
```

### 1.3 Microsoft Graph scopes

For Copilot usage / inactive-license helpers:

| Scope | Purpose |
|-------|---------|
| `Reports.Read.All` | Microsoft 365 usage reports (Copilot activity) |
| `Directory.Read.All` | Resolve UPN → security group → BU |
| `LicenseAssignment.Read.All` | Inactive seat detection |
| `Group.Read.All` | Read Entra ID security groups bound to billing policies |

Always read-only for this control. Mutation surfaces (creating Copilot billing policies via Graph beta) are deliberately not implemented as automation in v1.3.3 — the GA Graph surface is moving; perform via portal (see [Portal Walkthrough §3](portal-walkthrough.md#§3-microsoft-365-admin-center--copilot-billing--usage-policies)) until the API stabilises.

---

## §2 Sovereign-Aware Bootstrap

```powershell
function Resolve-Fsi35CloudProfile {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [string]$TenantId)

    # Heuristic: caller can override; otherwise infer from default Azure context.
    $env = $env:FSI_CLOUD
    if (-not $env) {
        $ctx = Get-AzContext -ErrorAction SilentlyContinue
        $env = switch ($ctx.Environment.Name) {
            'AzureCloud'        { 'Commercial' }
            'AzureUSGovernment' { 'GCC' }   # caller may need to refine GCC vs GCC High
            'AzureChinaCloud'   { 'China' }
            default             { 'Commercial' }
        }
    }

    $profile = switch ($env) {
        'Commercial' { @{ AzEnv='AzureCloud';        GraphEnv='Global';   PowerAppsEndpoint='prod' } }
        'GCC'        { @{ AzEnv='AzureUSGovernment'; GraphEnv='USGov';    PowerAppsEndpoint='usgov' } }
        'GCCHigh'    { @{ AzEnv='AzureUSGovernment'; GraphEnv='USGovDoD'; PowerAppsEndpoint='usgovhigh' } }
        'DoD'        { @{ AzEnv='AzureUSGovernment'; GraphEnv='USGovDoD'; PowerAppsEndpoint='dod' } }
        'China'      { @{ AzEnv='AzureChinaCloud';   GraphEnv='China';    PowerAppsEndpoint='china' } }
        default      { throw "Fsi35-Sovereign: unknown FSI_CLOUD value '$env'." }
    }

    [pscustomobject]@{
        Status   = 'Clean'
        Cloud    = $env
        Profile  = $profile
        TenantId = $TenantId
        Reason   = ''
    }
}

function Initialize-Fsi35Session {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string]$TenantId,
        [Parameter(Mandatory)] [string]$SubscriptionId
    )

    Assert-Fsi35ShellHost -RequiredHost Core74 | Out-Null
    $modules = Test-Fsi35ModuleMatrix
    if ($modules.Status -ne 'Clean') {
        throw "Fsi35-ModuleMatrix: $($modules.Reason). Run Test-Fsi35ModuleMatrix -InstallMissing."
    }

    Disconnect-AzAccount -ErrorAction SilentlyContinue | Out-Null
    Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null

    $cloud = Resolve-Fsi35CloudProfile -TenantId $TenantId

    if ($PSCmdlet.ShouldProcess("Tenant $TenantId / Sub $SubscriptionId", 'Connect Az + Graph')) {
        Connect-AzAccount -Tenant $TenantId -Subscription $SubscriptionId `
            -Environment $cloud.Profile.AzEnv | Out-Null
        Connect-MgGraph -TenantId $TenantId -Environment $cloud.Profile.GraphEnv `
            -Scopes 'Reports.Read.All','Directory.Read.All','Group.Read.All' -NoWelcome
    }

    [pscustomobject]@{
        Status      = 'Clean'
        Cloud       = $cloud.Cloud
        TenantId    = $TenantId
        Subscription= $SubscriptionId
        Reason      = ''
    }
}
```

---

## §3 Cost Query Helpers (Az.CostManagement)

### 3.1 Wrapped query with retry / backoff

```powershell
function Invoke-Fsi35CostQuery {
    <#
    .SYNOPSIS
        Wraps Invoke-AzCostManagementQuery with retry, backoff, and explicit empty-vs-error distinction.
    .NOTES
        Returns [pscustomobject] with Status (Clean | Anomaly | Error | NotApplicable).
        An empty result with HTTP 200 is Status=Clean, RowCount=0 — the caller decides whether
        zero spend is plausible.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$Scope,           # /subscriptions/<id> or /providers/Microsoft.Management/managementGroups/<id>
        [Parameter(Mandatory)] [datetime]$From,
        [Parameter(Mandatory)] [datetime]$To,
        [ValidateSet('Daily','Monthly')] [string]$Granularity = 'Daily',
        [string[]]$GroupBy = @('ResourceGroup','ServiceName')
    )

    $query = @{
        type      = 'AmortizedCost'
        timeframe = 'Custom'
        timePeriod = @{
            from = $From.ToString('yyyy-MM-ddTHH:mm:ssZ')
            to   = $To.ToString('yyyy-MM-ddTHH:mm:ssZ')
        }
        dataset = @{
            granularity = $Granularity
            aggregation = @{ totalCost = @{ name='Cost'; function='Sum' } }
            grouping    = $GroupBy | ForEach-Object { @{ type='Dimension'; name=$_ } }
        }
    }

    $maxAttempts = 3
    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        try {
            $r = Invoke-AzCostManagementQuery -Scope $Scope -Type 'AmortizedCost' `
                    -Timeframe 'Custom' -TimePeriodFrom $query.timePeriod.from `
                    -TimePeriodTo $query.timePeriod.to `
                    -DatasetGranularity $Granularity `
                    -DatasetAggregation @{ totalCost = @{ name='Cost'; function='Sum' } } `
                    -DatasetGrouping ($GroupBy | ForEach-Object { @{ type='Dimension'; name=$_ } }) `
                    -ErrorAction Stop
            return [pscustomobject]@{
                Status   = 'Clean'
                Scope    = $Scope
                RowCount = ($r.Row).Count
                Rows     = $r.Row
                Columns  = $r.Column
                From     = $From; To = $To; Granularity = $Granularity
                Reason   = ''
            }
        } catch {
            $isThrottle = $_.Exception.Message -match '429|TooManyRequests'
            if ($isThrottle -and $attempt -lt $maxAttempts) {
                $sleep = [math]::Pow(2, $attempt) * 5
                Start-Sleep -Seconds $sleep
                continue
            }
            return [pscustomobject]@{
                Status = 'Error'; Scope=$Scope; RowCount=0; Rows=@(); Reason=$_.Exception.Message
            }
        }
    }
}
```

### 3.2 BU rollup from tags

```powershell
function Get-Fsi-CostByBusinessUnit {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$Scope,
        [Parameter(Mandatory)] [datetime]$From,
        [Parameter(Mandatory)] [datetime]$To
    )

    $r = Invoke-Fsi35CostQuery -Scope $Scope -From $From -To $To -GroupBy @('TagKey','TagValue')
    if ($r.Status -ne 'Clean') { return $r }

    # The Az.CostManagement payload returns rows as arrays in the order of $Columns.
    $idxCost   = $r.Columns.Name.IndexOf('Cost')
    $idxKey    = $r.Columns.Name.IndexOf('TagKey')
    $idxValue  = $r.Columns.Name.IndexOf('TagValue')

    $bu = $r.Rows | Where-Object { $_[$idxKey] -eq 'CostCenter' } | ForEach-Object {
        [pscustomobject]@{
            CostCenter = $_[$idxValue]
            Cost       = [decimal]$_[$idxCost]
        }
    } | Group-Object CostCenter | ForEach-Object {
        [pscustomobject]@{
            CostCenter = $_.Name
            TotalCost  = [math]::Round((($_.Group | Measure-Object Cost -Sum).Sum), 2)
            RowCount   = $_.Count
        }
    } | Sort-Object TotalCost -Descending

    [pscustomobject]@{
        Status     = 'Clean'
        Scope      = $Scope
        Period     = "$($From.ToString('yyyy-MM-dd')) → $($To.ToString('yyyy-MM-dd'))"
        Rows       = $bu
        Untagged   = ($r.Rows | Where-Object { -not $_[$idxKey] }).Count
        Reason     = if (($bu).Count -eq 0) { 'No CostCenter-tagged resources in scope' } else { '' }
    }
}
```

!!! warning "Untagged rows are not zero spend"
    `Get-Fsi-CostByBusinessUnit` exposes an `Untagged` count. A non-zero `Untagged` value means real spend exists outside the cost-allocation taxonomy — investigate via the Azure Policy compliance report (see [Portal Walkthrough §4.3](portal-walkthrough.md#§4-azure-portal--tagging-policy-and-tag-inheritance)). Do not bury untagged spend into a `SHARED` cost center silently — that is a SOX 404 documentation gap.

---

## §4 Monthly-Close Helpers

### 4.1 Rate-card retrieval (CFO-approved, version-pinned)

```powershell
function Get-Fsi35RateCard {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$StorageAccountName,
        [Parameter(Mandatory)] [string]$ContainerName,   # immutable container
        [Parameter(Mandatory)] [string]$EffectiveDate    # 'yyyy-MM-dd'
    )

    $ctx = New-AzStorageContext -StorageAccountName $StorageAccountName -UseConnectedAccount
    $blobName = "rate-cards/rate-card-$EffectiveDate.json"
    $tmp = New-TemporaryFile
    try {
        Get-AzStorageBlobContent -Container $ContainerName -Blob $blobName -Context $ctx `
            -Destination $tmp.FullName -Force | Out-Null
        $card = Get-Content $tmp.FullName -Raw | ConvertFrom-Json
    } catch {
        return [pscustomobject]@{ Status='Error'; Reason="Rate card not found for $EffectiveDate: $_" }
    } finally {
        Remove-Item $tmp.FullName -ErrorAction SilentlyContinue
    }

    if (-not $card.signedBy -or -not $card.signedDate) {
        return [pscustomobject]@{ Status='Anomaly'; Card=$card; Reason='Rate card missing CFO signature metadata' }
    }

    [pscustomobject]@{
        Status        = 'Clean'
        EffectiveDate = $EffectiveDate
        Version       = $card.version
        SignedBy      = $card.signedBy
        SignedDate    = $card.signedDate
        Card          = $card
        Reason        = ''
    }
}
```

The rate-card JSON is the single source of truth for internal pricing. Example structure (do not commit list prices to this repo):

```json
{
  "version": "2026-Q2-v1",
  "effectiveDate": "2026-04-01",
  "signedBy": "controller@example.com",
  "signedDate": "2026-03-28",
  "rates": {
    "CopilotStudioMessage": { "unit": "message", "rate": "<set-by-firm>" },
    "M365CopilotPerUser":   { "unit": "user-month", "rate": "<set-by-firm>" },
    "AIBuilderCredit":      { "unit": "credit", "rate": "<set-by-firm>" },
    "DataverseGB":          { "unit": "gb-month", "rate": "<set-by-firm>" }
  }
}
```

### 4.2 Monthly chargeback ledger

```powershell
function Get-Fsi-MonthlyChargeback {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$ManagementGroupId,
        [Parameter(Mandatory)] [int]$Year,
        [Parameter(Mandatory)] [ValidateRange(1,12)] [int]$Month,
        [Parameter(Mandatory)] [string]$RateCardStorageAccount,
        [Parameter(Mandatory)] [string]$RateCardContainer
    )

    $from  = [datetime]::new($Year, $Month, 1)
    $to    = $from.AddMonths(1).AddSeconds(-1)
    $scope = "/providers/Microsoft.Management/managementGroups/$ManagementGroupId"

    $card = Get-Fsi35RateCard -StorageAccountName $RateCardStorageAccount `
                -ContainerName $RateCardContainer -EffectiveDate $from.ToString('yyyy-MM-dd')
    if ($card.Status -ne 'Clean') { return $card }

    $bu = Get-Fsi-CostByBusinessUnit -Scope $scope -From $from -To $to
    if ($bu.Status -ne 'Clean') { return $bu }

    if ($bu.Untagged -gt 0) {
        return [pscustomobject]@{
            Status='Anomaly'; Period="$Year-$Month"; UntaggedRowCount=$bu.Untagged
            Reason='Untagged spend present in scope; resolve before issuing chargeback'
        }
    }

    $ledger = $bu.Rows | ForEach-Object {
        [pscustomobject]@{
            Period       = "$Year-$('{0:D2}' -f $Month)"
            CostCenter   = $_.CostCenter
            ActualCost   = $_.TotalCost
            RateCardVer  = $card.Version
            ChargebackId = "CB-$Year$('{0:D2}' -f $Month)-$($_.CostCenter)"
        }
    }

    [pscustomobject]@{
        Status      = 'Clean'
        Period      = "$Year-$('{0:D2}' -f $Month)"
        Ledger      = $ledger
        Total       = [math]::Round((($ledger | Measure-Object ActualCost -Sum).Sum), 2)
        RateCard    = $card.Version
        SignedBy    = $card.SignedBy
        Reason      = ''
    }
}
```

### 4.3 Variance reconciliation against invoice

```powershell
function Test-Fsi-Control35-InvoiceVariance {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [decimal]$LedgerTotal,
        [Parameter(Mandatory)] [decimal]$InvoiceTotal,
        [decimal]$ThresholdPercent = 5.0
    )
    if ($InvoiceTotal -le 0) {
        return [pscustomobject]@{ Status='Anomaly'; Reason='Invoice total <= 0; cannot compute variance' }
    }
    $variance = [math]::Round((($LedgerTotal - $InvoiceTotal) / $InvoiceTotal) * 100, 2)
    $status   = if ([math]::Abs($variance) -le $ThresholdPercent) { 'Clean' } else { 'Anomaly' }
    [pscustomobject]@{
        Status         = $status
        LedgerTotal    = $LedgerTotal
        InvoiceTotal   = $InvoiceTotal
        VariancePct    = $variance
        ThresholdPct   = $ThresholdPercent
        Reason         = if ($status -eq 'Anomaly') { "Variance ${variance}% exceeds threshold ${ThresholdPercent}%" } else { '' }
    }
}
```

---

## §5 Power Platform Capacity (Sidecar 5.1)

```powershell
function Get-Fsi-PowerPlatformCapacity {
    [CmdletBinding()]
    param([string]$OutputPath)

    Assert-Fsi35ShellHost -RequiredHost Sidecar51 | Out-Null

    Add-PowerAppsAccount -Endpoint $env:FSI_PP_ENDPOINT  # 'prod' | 'usgov' | 'usgovhigh' | 'dod' | 'china'

    $envs = Get-AdminPowerAppEnvironment
    $rows = foreach ($e in $envs) {
        $d = Get-AdminPowerAppEnvironment -EnvironmentName $e.EnvironmentName
        [pscustomobject]@{
            EnvironmentDisplayName = $e.DisplayName
            EnvironmentName        = $e.EnvironmentName
            EnvironmentType        = $e.EnvironmentType
            DatabaseSizeMB         = $d.OrganizationSettings.DatabaseSettings.Size
            FileSizeMB             = $d.OrganizationSettings.FileSettings.Size
            LogSizeMB              = $d.OrganizationSettings.LogSettings.Size
            CapturedUtc            = (Get-Date).ToUniversalTime().ToString('o')
        }
    }

    if ($OutputPath) { $rows | Export-Csv -Path $OutputPath -NoTypeInformation }

    [pscustomobject]@{
        Status   = if (($rows).Count -eq 0) { 'NotApplicable' } else { 'Clean' }
        RowCount = ($rows).Count
        Rows     = $rows
        Reason   = if (($rows).Count -eq 0) { 'No environments returned — verify shell host and endpoint' } else { '' }
    }
}
```

---

## §6 Microsoft 365 Copilot Usage and License Utilization (Microsoft Graph)

```powershell
function Get-Fsi-CopilotLicenseUtilization {
    <#
    .SYNOPSIS
        Returns assigned vs active Copilot seats with explicit DataLagHours annotation.
    .NOTES
        Microsoft Graph reports lag 24–72h; this helper flags results inside the lag window
        as Status='Pending' rather than 'Clean'.
    #>
    [CmdletBinding()]
    param(
        [int]$Days = 30,
        [int]$LagHours = 72
    )

    # SubscribedSku → list assigned licenses
    $skus = Get-MgSubscribedSku -All
    $copilot = $skus | Where-Object { $_.SkuPartNumber -match 'COPILOT' }

    if (-not $copilot) {
        return [pscustomobject]@{ Status='NotApplicable'; Reason='No Copilot SKUs found in tenant' }
    }

    # M365 Copilot user-activity report (CSV stream)
    $period = "D$Days"
    $tmp    = New-TemporaryFile
    try {
        Invoke-MgGraphRequest -Method GET `
            -Uri "/v1.0/reports/getMicrosoft365CopilotUserCountSummary(period='$period')" `
            -OutputFilePath $tmp.FullName -ErrorAction Stop
    } catch {
        return [pscustomobject]@{ Status='Error'; Reason="Graph report fetch failed: $_" }
    }

    # Detail report
    $detailTmp = New-TemporaryFile
    try {
        Invoke-MgGraphRequest -Method GET `
            -Uri "/v1.0/reports/getMicrosoft365CopilotUserDetail(period='$period')" `
            -OutputFilePath $detailTmp.FullName -ErrorAction Stop
        $detail = Import-Csv $detailTmp.FullName
    } catch {
        return [pscustomobject]@{ Status='Error'; Reason="Graph detail fetch failed: $_" }
    } finally {
        Remove-Item $tmp.FullName, $detailTmp.FullName -ErrorAction SilentlyContinue
    }

    $assigned = ($copilot | Measure-Object ConsumedUnits -Sum).Sum
    $active   = ($detail | Where-Object { $_.'Last activity date' }).Count
    $idle30   = ($detail | Where-Object {
        -not $_.'Last activity date' -or
        ([datetime]$_.'Last activity date') -lt ((Get-Date).AddDays(-30))
    }).Count

    $reportRefreshUtc = ($detail | Select-Object -First 1).'Report Refresh Date'
    $lagOk = $reportRefreshUtc -and ([datetime]$reportRefreshUtc) -gt (Get-Date).AddHours(-1 * $LagHours)

    [pscustomobject]@{
        Status         = if ($lagOk) { 'Clean' } else { 'Pending' }
        AssignedSeats  = $assigned
        ActiveSeats    = $active
        IdleOver30Days = $idle30
        UtilizationPct = if ($assigned -gt 0) { [math]::Round(($active / $assigned) * 100, 1) } else { 0 }
        ReportRefresh  = $reportRefreshUtc
        DataLagHours   = $LagHours
        Reason         = if (-not $lagOk) { "Report refresh older than $LagHours h — treat as preliminary" } else { '' }
    }
}
```

---

## §7 Azure Budgets

### 7.1 Create / update budget (`New-AzConsumptionBudget`)

```powershell
function New-Fsi-AzureBudget {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string]$BudgetName,
        [Parameter(Mandatory)] [string]$ResourceGroupName,
        [Parameter(Mandatory)] [decimal]$MonthlyAmount,
        [Parameter(Mandatory)] [string[]]$AlertRecipients,
        [decimal[]]$Thresholds = @(50, 75, 90, 100)
    )

    $rbac = Test-Fsi35Rbac -SubscriptionId (Get-AzContext).Subscription.Id -Mode Write
    if ($rbac.Status -ne 'Clean') { return $rbac }

    if (-not $PSCmdlet.ShouldProcess("RG=$ResourceGroupName / $BudgetName", "Create budget $MonthlyAmount/mo")) {
        return [pscustomobject]@{ Status='Pending'; Reason='WhatIf' }
    }

    $startDate = (Get-Date).ToString('yyyy-MM-01')
    $endDate   = (Get-Date).AddYears(1).ToString('yyyy-MM-01')

    $notifications = @{}
    foreach ($t in $Thresholds) {
        $notifications["Threshold$t"] = @{
            Enabled        = $true
            Operator       = 'GreaterThanOrEqualTo'
            Threshold      = $t
            ContactEmails  = $AlertRecipients
            NotificationLanguage = 'en-us'
        }
    }

    try {
        New-AzConsumptionBudget -Name $BudgetName -Amount $MonthlyAmount -Category 'Cost' `
            -TimeGrain 'Monthly' -StartDate $startDate -EndDate $endDate `
            -ResourceGroupName $ResourceGroupName -Notification $notifications -ErrorAction Stop | Out-Null

        return [pscustomobject]@{
            Status        = 'Clean'
            BudgetName    = $BudgetName
            ResourceGroup = $ResourceGroupName
            Amount        = $MonthlyAmount
            Thresholds    = $Thresholds
            Reason        = ''
        }
    } catch {
        return [pscustomobject]@{ Status='Error'; Reason="Budget create failed: $_" }
    }
}
```

> **Cmdlet note.** `New-AzConsumptionBudget` (Az.Billing) is the GA cmdlet for Azure budgets at subscription / resource-group scope as of April 2026. The previously-circulated `New-AzCostManagementBudget` is **not a GA cmdlet**; do not use earlier versions of this playbook that reference it.

### 7.2 Confirm budgets exist for every BU

```powershell
function Test-Fsi-Control35-BudgetCoverage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string[]]$RequiredCostCenters
    )
    $existing = Get-AzConsumptionBudget -ErrorAction SilentlyContinue
    $missing  = $RequiredCostCenters | Where-Object { $_ -notin ($existing.Name -join ' ') }

    [pscustomobject]@{
        Status              = if ($missing) { 'Anomaly' } else { 'Clean' }
        ExistingBudgetCount = ($existing).Count
        Missing             = $missing
        Reason              = if ($missing) { "No budget for: $($missing -join ', ')" } else { '' }
    }
}
```

---

## §8 Cost Management Exports (Immutability-Bound)

```powershell
function New-Fsi-CostExport {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string]$ExportName,
        [Parameter(Mandatory)] [string]$Scope,
        [Parameter(Mandatory)] [string]$StorageAccountResourceId,
        [Parameter(Mandatory)] [string]$ContainerName,
        [string]$RootFolderPath = 'cost-mgmt-exports'
    )

    # Refuse to create export if container is not immutable.
    $imm = Test-Fsi-Control35-ExportImmutability -StorageAccountResourceId $StorageAccountResourceId -ContainerName $ContainerName
    if ($imm.Status -ne 'Clean') { return $imm }

    if (-not $PSCmdlet.ShouldProcess("$Scope → $ContainerName", "Create cost export $ExportName")) {
        return [pscustomobject]@{ Status='Pending'; Reason='WhatIf' }
    }

    try {
        New-AzCostManagementExport -Scope $Scope -Name $ExportName `
            -ScheduleRecurrence 'Daily' `
            -DefinitionType 'AmortizedCost' `
            -DefinitionTimeframe 'MonthToDate' `
            -DestinationResourceId $StorageAccountResourceId `
            -DestinationContainer $ContainerName `
            -DestinationRootFolderPath $RootFolderPath `
            -Format 'Parquet' `
            -ErrorAction Stop | Out-Null

        return [pscustomobject]@{ Status='Clean'; ExportName=$ExportName; Scope=$Scope; Reason='' }
    } catch {
        return [pscustomobject]@{ Status='Error'; Reason="Export create failed: $_" }
    }
}

function Test-Fsi-Control35-ExportImmutability {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$StorageAccountResourceId,
        [Parameter(Mandatory)] [string]$ContainerName
    )
    try {
        $sa = Get-AzResource -ResourceId $StorageAccountResourceId
        $ctx = (Get-AzStorageAccount -ResourceGroupName $sa.ResourceGroupName -Name $sa.Name).Context
        $policy = Get-AzRmStorageContainerImmutabilityPolicy `
            -ResourceGroupName $sa.ResourceGroupName `
            -StorageAccountName $sa.Name `
            -ContainerName $ContainerName -ErrorAction Stop

        if ($policy.State -in @('Locked','Unlocked') -and $policy.ImmutabilityPeriodSinceCreationInDays -ge 2190) {
            return [pscustomobject]@{
                Status      = 'Clean'
                Container   = $ContainerName
                PolicyState = $policy.State
                RetentionDays = $policy.ImmutabilityPeriodSinceCreationInDays
                Reason      = if ($policy.State -eq 'Unlocked') { 'Immutability policy is Unlocked — lock before relying on for 17a-4(b)(4)' } else { '' }
            }
        }
        return [pscustomobject]@{
            Status='Anomaly'; Container=$ContainerName
            Reason='Immutability policy missing or retention <6 years (2190 d)'
        }
    } catch {
        return [pscustomobject]@{ Status='Error'; Reason="Immutability check failed: $_" }
    }
}
```

!!! danger "Locked vs Unlocked immutability"
    An *Unlocked* immutability policy can still be shortened or removed. Records-grade evidence requires a **Locked** policy. The helper above returns `Clean` for Unlocked but flags the `Reason` so the operator does not silently proceed.

---

## §9 Tag-Policy Compliance

```powershell
function Test-Fsi-Control35-TagPolicyCompliance {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [string]$ScopeId)

    $assignments = Get-AzPolicyAssignment -Scope $ScopeId | Where-Object {
        $_.Properties.DisplayName -match 'CostCenter|BusinessUnit|Zone|Owner|Application'
    }
    if (-not $assignments) {
        return [pscustomobject]@{ Status='Anomaly'; Reason='No tag-enforcement assignments found at scope' }
    }

    $nonCompliant = foreach ($a in $assignments) {
        Get-AzPolicyState -PolicyAssignmentName $a.Name -Filter "ComplianceState eq 'NonCompliant'" |
            Select-Object ResourceId, PolicyDefinitionAction, Timestamp
    }

    [pscustomobject]@{
        Status              = if ($nonCompliant) { 'Anomaly' } else { 'Clean' }
        AssignmentsCount    = ($assignments).Count
        NonCompliantCount   = ($nonCompliant).Count
        NonCompliantResources = $nonCompliant
        Reason              = if ($nonCompliant) { "$($nonCompliant.Count) resources non-compliant with tag policy" } else { '' }
    }
}
```

---

## §10 Self-Test Orchestrator

```powershell
function Invoke-Fsi35SelfTest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$SubscriptionId,
        [Parameter(Mandatory)] [string[]]$RequiredCostCenters,
        [Parameter(Mandatory)] [string]$ExportStorageAccountResourceId,
        [Parameter(Mandatory)] [string]$ExportContainerName,
        [string]$ScopeForTagPolicy
    )

    $results = [ordered]@{}
    $results['Modules']      = Test-Fsi35ModuleMatrix
    $results['Rbac']         = Test-Fsi35Rbac -SubscriptionId $SubscriptionId -Mode Read
    $results['BudgetCover']  = Test-Fsi-Control35-BudgetCoverage -RequiredCostCenters $RequiredCostCenters
    $results['ExportImmut']  = Test-Fsi-Control35-ExportImmutability `
                                -StorageAccountResourceId $ExportStorageAccountResourceId `
                                -ContainerName $ExportContainerName
    if ($ScopeForTagPolicy) {
        $results['TagPolicy'] = Test-Fsi-Control35-TagPolicyCompliance -ScopeId $ScopeForTagPolicy
    }
    $results['LicenseUtil']  = Get-Fsi-CopilotLicenseUtilization

    $rollup = if ($results.Values.Status -contains 'Error')   { 'Error'
              } elseif ($results.Values.Status -contains 'Anomaly') { 'Anomaly'
              } elseif ($results.Values.Status -contains 'Pending') { 'Pending'
              } else { 'Clean' }

    [pscustomobject]@{
        Status   = $rollup
        RunId    = "AGT35-$((Get-Date).ToString('yyyyMMdd-HHmmss'))-$((New-Guid).Guid.Substring(0,8))"
        Results  = $results
        Reason   = if ($rollup -ne 'Clean') {
            ($results.GetEnumerator() | Where-Object { $_.Value.Status -ne 'Clean' } |
                ForEach-Object { "$($_.Key)=$($_.Value.Status): $($_.Value.Reason)" }) -join ' | '
        } else { '' }
    }
}
```

A failed self-test must **suppress** the affected scheduled batch (chargeback emission, evidence-pack assembly) and alert the AI Governance Lead. It must **not** emit a "clean" report.

---

## §11 Evidence Manifest (SHA-256)

Every monthly chargeback emission produces a SHA-256-signed manifest covering: rate-card blob, cost-export blobs for the period, ledger CSV, variance memo PDF, sign-off PDF.

```powershell
function New-Fsi-Control35-EvidenceManifest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string[]]$Files,
        [Parameter(Mandatory)] [string]$OutputManifestPath,
        [Parameter(Mandatory)] [string]$RunId
    )
    $entries = foreach ($f in $Files) {
        if (-not (Test-Path $f)) {
            return [pscustomobject]@{ Status='Error'; Reason="Missing file: $f" }
        }
        $hash = Get-FileHash -Path $f -Algorithm SHA256
        [pscustomobject]@{
            File          = (Resolve-Path $f).Path
            SizeBytes     = (Get-Item $f).Length
            SHA256        = $hash.Hash
            CapturedUtc   = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
    $manifest = [pscustomobject]@{
        RunId       = $RunId
        Control     = '3.5'
        GeneratedUtc= (Get-Date).ToUniversalTime().ToString('o')
        Entries     = $entries
    }
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -Path $OutputManifestPath -Encoding UTF8
    [pscustomobject]@{ Status='Clean'; Manifest=$OutputManifestPath; EntryCount=($entries).Count; Reason='' }
}
```

The manifest itself is then countersigned (e.g., uploaded to the immutable container, with the resulting Storage `ETag` and `Last-Modified` recorded in the chargeback ledger as the "binding").

---

## §12 Anti-Patterns

The following patterns appeared in earlier versions of this playbook and must not be reintroduced:

- **`Get-Random` for cost data.** Stub data masquerading as production produces fraudulent chargeback. Use real `Az.CostManagement` queries; if no data exists, return `Status='Clean'` with `RowCount=0` — never fabricate.
- **Hard-coded prices in helper bodies.** Always read from the rate card (§4.1).
- **`-Force` on `Install-Module` without `-RequiredVersion`.** Floats the module version and breaks SOX 404 reproducibility.
- **`New-AzCostManagementBudget`.** Not a GA cmdlet. Use `New-AzConsumptionBudget` (Az.Billing).
- **Cost exports to mutable storage.** Operational data, not a 17a-4(b)(4) record.
- **Treating an HTTP 200 with empty rows as "no spend".** Distinguish `Clean / RowCount=0` from `Error` from `NotApplicable`.
- **Standing Global Admin on a service principal.** Use Cost Management Contributor + Resource Policy Contributor, scoped.

---

## §13 Operating Cadence

| Cadence | Helper | Owner |
|---------|--------|-------|
| Hourly (informational) | `Invoke-Fsi35SelfTest` (sandbox tenant) | Platform engineering |
| Daily | `New-Fsi-CostExport` (auto-runs); `Test-Fsi-Control35-TagPolicyCompliance` | Power Platform Admin |
| Monthly close (by 5th BD) | `Get-Fsi-MonthlyChargeback` → `Test-Fsi-Control35-InvoiceVariance` → `New-Fsi-Control35-EvidenceManifest` | AI Administrator + Finance |
| Quarterly | `Invoke-Fsi35SelfTest` full + sample evidence walkthrough | Compliance Officer + Internal Audit |
| Annual | Re-pin module matrix; re-baseline rate card; re-attest BU mapping | Power Platform Admin + Finance |

---

## Cross-references

- [Portal Walkthrough](portal-walkthrough.md) — surface-by-surface portal procedure
- [Verification & Testing](verification-testing.md) — Pester suite and evidence pack
- [Troubleshooting](troubleshooting.md) — defect catalogue and recovery
- [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — module pinning, sovereign endpoints, mutation safety
- [Control 1.9 — Data Retention and Deletion](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) — WORM retention surface
- [Control 3.1 — Agent Inventory and Metadata](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — source of `CostCenter` / `Owner` tag values

---

[Back to Control 3.5](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) · [Portal Walkthrough](portal-walkthrough.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.3.3*
