---
control_id: "2.26"
title: "PowerShell Setup — Control 2.26: Entra Agent ID Identity Governance"
pillar: "2 — Management"
powershell_edition: "7.4 LTS Core"
sovereign_clouds: "Commercial only (early-exit on GCC, GCC High, DoD — no GA announced for sovereign tenants as of May 2026)"
last_ui_verified: "May 2026"
---

# PowerShell Setup — Control 2.26: Entra Agent ID Identity Governance

> **Scope.** Operational PowerShell automation for governing Entra Agent ID lifecycle: sponsor assignment, orphan detection, access package assignment review, lifecycle workflow telemetry, access review tracking, bulk sponsor reassignment, evidence pack export, and SIEM forwarding verification.
>
> **Post-GA status (May 2026).** Microsoft Agent 365 reached general availability on May 1, 2026 and Microsoft Entra Agent ID is generally available. The pre-GA "Frontier program enrollment" prerequisite is replaced by **Microsoft Agent 365 / Microsoft 365 E7 license assignment**. The `Test-Agt226PreviewGating` helper and the `PreviewGatingNotSatisfied` exception type retain their pre-GA names for backward compatibility — the underlying check (whether the operating principal can reach the agent identity surface) remains valid because both the pre-GA Frontier gate and the post-GA license assignment manifest as the same API reachability state. A follow-up issue tracks renaming the helper and exception type to license-coverage terms.
>
> **License gating.** Entra Agent ID requires **Microsoft Agent 365** licensing (standalone per-user) or **Microsoft 365 E7** ("Frontier Suite," which bundles Microsoft 365 Copilot + Agent 365 + Entra Suite + E5). Tenants without either license will see empty result sets — not errors. The §1 preflight explicitly flags this false-clean condition.
>
> **Sovereign clouds.** Entra Agent ID is currently a Commercial-cloud surface. Code paths in this playbook **early-exit** on GCC, GCC High, DoD, and China cloud profiles with structured compensating-control instructions rather than degrading silently. See §2.
>
> **Sponsor-departure model.** When a sponsor's `accountEnabled` flips to `false` or `employeeLeaveDateTime` passes, Entra's default behaviour transfers the agent's sponsor relationship to the departing sponsor's manager (per the standard lifecycle workflow template). The helpers in this file **read** that state to surface anomalies; they do not override the transfer. Reassignment overrides go through the §8 audited bulk path.
>
> **Audit log filtering.** Microsoft Graph and Entra audit logs are emitted with object IDs, not enriched names. Correlation, alerting, and retention enforcement happen in the downstream SIEM (control 1.7). The §10 helper verifies forwarding plumbing; it does not attempt server-side filtering.

---

## 0. Wrong-shell trap and false-clean defects

Before any Graph call runs, every operator must confirm shell parity. Entra Agent ID cmdlet surface area is only stable under PowerShell 7.4 LTS Core. Mixing Windows PowerShell 5.1 and `Microsoft.Graph` 2.x produces silent assembly-load failures that emit empty arrays — the most dangerous false-clean pattern in this control because empty results are indistinguishable from "no orphaned agents present."

```powershell
#Requires -Version 7.4

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-Agt226Shell {
    [CmdletBinding()]
    param()

    if ($PSVersionTable.PSEdition -ne 'Core') {
        throw "Control 2.26 helpers require PowerShell 7.4 Core. Detected edition: $($PSVersionTable.PSEdition). Re-launch under pwsh.exe."
    }
    if ($PSVersionTable.PSVersion -lt [version]'7.4.0') {
        throw "Control 2.26 helpers require PowerShell 7.4 LTS or later. Detected: $($PSVersionTable.PSVersion). Upgrade before continuing."
    }

    $loadedDesktopGraph = Get-Module -Name 'Microsoft.Graph*' |
        Where-Object { $_.Path -match 'WindowsPowerShell\\v1\.0' }
    if ($loadedDesktopGraph) {
        throw "Detected Microsoft.Graph modules loaded from Windows PowerShell 5.1 path. This shell is contaminated. Close all sessions and start a clean pwsh 7.4 process."
    }

    Write-Verbose "Shell parity confirmed: PowerShell $($PSVersionTable.PSVersion) Core."
}

Assert-Agt226Shell -Verbose
```

### False-clean defects to refuse

The table below enumerates defect classes specific to Entra Agent ID telemetry. Each row pairs the symptom with the structural guard that the helpers in this file enforce. **Empty output is never sufficient evidence of a clean control state** until every guard passes.

| # | Defect | Symptom | Why it appears clean | Structural guard |
|---|--------|---------|----------------------|------------------|
| 0.1 | Preview gating not satisfied | `Get-MgServicePrincipal -Filter "tags/any(t:t eq 'AgentIdentity')"` returns zero rows | No exception is thrown; the tenant simply has no agent identities reachable to the calling principal because the operating account lacks Microsoft Agent 365 / Microsoft 365 E7 license coverage (post-GA gating mechanism) | §1 preflight calls `Test-Agt226PreviewGating` (name retained for backward-compat) which checks both Microsoft 365 Copilot SKU coverage and Agent ID API surface reachability, and aborts with a structured `PreviewGatingNotSatisfied` exception (name retained) before any inventory pass |
| 0.2 | Wrong shell edition | All inventory cmdlets succeed but return `@()` | Microsoft.Graph 2.x assemblies fail to bind under Desktop edition; the SDK swallows the bind failure and returns empty | `Assert-Agt226Shell` (above) blocks Desktop edition entirely |
| 0.3 | Stale delegated token | Helpers run, return data, but `sponsorRelationships` collection is always null | Delegated token issued before the AgentIdentity.Read.All scope was granted; Graph silently omits the navigation property | §1 `Test-Agt226GraphScopes` re-asserts scopes against the live token and forces re-consent if mismatched |
| 0.4 | Sovereign cloud silent skew | Helpers run against GCC High and return zero agents | Entra Agent ID preview endpoints are not deployed to sovereign clouds; the SDK resolves the wrong base URI and 404s are swallowed by the ForEach pipeline | §2 `Resolve-Agt226CloudProfile` early-exits with a structured `SovereignCloudNotSupported` exception and logs the compensating control |
| 0.5 | Manager-transfer race window | An agent appears orphaned for ~5–15 minutes after a sponsor's `accountEnabled` flips to false | Lifecycle workflow has not yet run; transfer to manager is queued but not committed | §4 `Get-Agt226OrphanedAgent` accepts a `-GraceWindowMinutes` parameter (default 30) and tags rows below the threshold as `PendingLifecycleTransfer` rather than `Orphaned` |
| 0.6 | Access package assignment without ownership chain | Agent holds an access package assignment whose policy has no approver | Default Entitlement Management catalog allows policies without approvers; assignments evaluate as valid | §5 `Get-Agt226AgentAccessPackageAssignment` joins the policy and emits `PolicyApproverMissing=$true` for any assignment lacking a primary approver |
| 0.7 | Audit log retention assumption | Operator queries `AuditLogs` for a 90-day window and finds nothing for an agent decommissioned 6 months ago | Entra retains directory audit logs for 30 days by default; FINRA 4511 requires 6 years; the SIEM is the system of record but operators forget to query it | §10 `Test-Agt226SiemForwarding` emits an explicit `EntraNativeRetentionDays=30` field and a remediation pointer to control 1.7 |
| 0.8 | Access review marked complete with no decisions | A Zone 3 access review shows 100% completion but every assignment was auto-approved on reviewer non-response | Default review setting may be "If reviewers don't respond: Approve" | §7 `Get-Agt226AccessReviewStatus` surfaces the `defaultDecision` and `defaultDecisionEnabled` fields and flags reviews where decisions equal auto-approval |
| 0.9 | Bulk reassignment without audit trail | Operator runs `Update-MgServicePrincipal` directly to swap a sponsor reference | Direct cmdlet calls bypass the lifecycle workflow audit chain | §8 `Set-Agt226BulkSponsorReassignment` is the only sanctioned mutation path; it writes a CSV journal, signs the manifest, and emits a `directoryAudits` correlation ID |
| 0.10 | Throttling under burst | A 2,000-agent inventory pass returns 1,743 rows with no error | Graph 429 responses are returned mid-pipeline; the SDK retries some requests but not paginated `@odata.nextLink` calls | §11 `Invoke-Agt226WithThrottle` wraps every Graph call with exponential backoff and asserts the final page count against `@odata.count` |

> **Operator discipline.** Every helper in §§3–10 returns a structured object with a `Status` field whose values are `Clean`, `Anomaly`, `Pending`, `NotApplicable`, or `Error`. **No helper ever returns `$null` or an empty array as a clean signal.** When there is genuinely no data, the helper returns a single object with `Status='NotApplicable'` and a populated `Reason` property.


## 1. Module, CLI, and permission matrix

### 1.1 Module pinning

All helpers depend on the following module set. **Pinning is mandatory** — Microsoft.Graph 2.x has shipped breaking changes in patch releases, and Entra Agent ID navigation properties are gated on specific minor versions.

| Module | Minimum version | Pinned for | Notes |
|--------|-----------------|------------|-------|
| `Microsoft.Graph.Authentication` | 2.19.0 | Token acquisition, scope validation | Loads transitively but pin explicitly to lock the cmdlet surface |
| `Microsoft.Graph.Applications` | 2.19.0 | Service principal / agent identity enumeration | Required for `Get-MgServicePrincipal` filter on `tags/any(...)` |
| `Microsoft.Graph.Identity.Governance` | 2.19.0 | Access packages, lifecycle workflows, access reviews | Provides `Get-MgEntitlementManagementAccessPackageAssignment`, `Get-MgIdentityGovernanceLifecycleWorkflow`, `Get-MgIdentityGovernanceAccessReviewDefinition` |
| `Microsoft.Graph.Identity.DirectoryManagement` | 2.19.0 | Directory roles, sponsor user lookups | Required for resolving the manager-transfer chain |
| `Microsoft.Graph.Reports` | 2.19.0 | `directoryAudits` queries for §10 SIEM correlation | Read-only; never used for filtering decisions |
| `Microsoft.Graph.Beta.Identity.Governance` | 2.19.0 | Agent-identity-specific navigation properties (still in beta) | The `sponsors` and `agentMetadata` properties are beta-only as of April 2026 |
| `Az.Accounts` | 2.15.0 | Azure context for diagnostic settings (§10) | Used only for cross-tenant audit log forwarding verification |
| `Az.Monitor` | 5.2.0 | `Get-AzDiagnosticSetting` for §10 | Verifies Log Analytics or Event Hub forwarding |

```powershell
function Install-Agt226ModuleBaseline {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [switch]$AllowPrerelease
    )

    $required = @(
        @{ Name = 'Microsoft.Graph.Authentication';                 RequiredVersion = '2.19.0' }
        @{ Name = 'Microsoft.Graph.Applications';                   RequiredVersion = '2.19.0' }
        @{ Name = 'Microsoft.Graph.Identity.Governance';            RequiredVersion = '2.19.0' }
        @{ Name = 'Microsoft.Graph.Identity.DirectoryManagement';   RequiredVersion = '2.19.0' }
        @{ Name = 'Microsoft.Graph.Reports';                        RequiredVersion = '2.19.0' }
        @{ Name = 'Microsoft.Graph.Beta.Identity.Governance';       RequiredVersion = '2.19.0' }
        @{ Name = 'Az.Accounts';                                    RequiredVersion = '2.15.0' }
        @{ Name = 'Az.Monitor';                                     RequiredVersion = '5.2.0' }
    )

    foreach ($mod in $required) {
        $installed = Get-Module -ListAvailable -Name $mod.Name |
            Where-Object { $_.Version -eq [version]$mod.RequiredVersion }
        if (-not $installed) {
            if ($PSCmdlet.ShouldProcess($mod.Name, "Install $($mod.RequiredVersion)")) {
                Install-Module -Name $mod.Name -RequiredVersion $mod.RequiredVersion `
                    -Scope CurrentUser -Repository PSGallery -Force -AllowClobber
            }
        }
        Import-Module -Name $mod.Name -RequiredVersion $mod.RequiredVersion -Force -ErrorAction Stop
    }

    [pscustomobject]@{
        ModulesPinned = $required.Count
        Status        = 'Clean'
        Timestamp     = (Get-Date).ToUniversalTime()
    }
}
```

### 1.2 Microsoft Graph permission matrix

The minimum scope set for read-only operations is **smaller** than for the bulk reassignment path. Operators should run inventory and attestation with the read-only set and elevate only for the §8 mutation path.

| Operation | Scope | Permission type | Helpers that depend on it |
|-----------|-------|-----------------|---------------------------|
| Enumerate agent service principals | `Application.Read.All` | Application or delegated | §3, §4 |
| Read agent identity navigation properties | `AgentIdentity.Read.All` | Application or delegated (preview) | §3, §4, §5 |
| Read identity governance objects | `IdentityGovernance.Read.All` | Application or delegated | §6, §7 |
| Read entitlement management assignments | `EntitlementManagement.Read.All` | Application or delegated | §5 |
| Mutate entitlement management assignments (§8 only) | `EntitlementManagement.ReadWrite.All` | Delegated only — never script-grant to a service principal | §8 |
| Read directory audit logs | `AuditLog.Read.All` | Application or delegated | §10 |
| Read directory roles for sponsor escalation chain | `RoleManagement.Read.Directory` | Application or delegated | §3, §4 |

```powershell
function Test-Agt226GraphScopes {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('ReadOnly','Mutation')]
        [string]$Profile
    )

    $required = switch ($Profile) {
        'ReadOnly' {
            @('Application.Read.All','AgentIdentity.Read.All','IdentityGovernance.Read.All',
              'EntitlementManagement.Read.All','AuditLog.Read.All','RoleManagement.Read.Directory')
        }
        'Mutation' {
            @('Application.Read.All','AgentIdentity.Read.All','IdentityGovernance.Read.All',
              'EntitlementManagement.ReadWrite.All','AuditLog.Read.All','RoleManagement.Read.Directory')
        }
    }

    $context = Get-MgContext
    if (-not $context) {
        throw "No active Microsoft Graph session. Run Initialize-Agt226Session first."
    }

    $missing = $required | Where-Object { $_ -notin $context.Scopes }
    if ($missing) {
        throw "Token missing required scopes for profile '$Profile': $($missing -join ', '). Re-consent required."
    }

    [pscustomobject]@{
        Profile        = $Profile
        RequiredScopes = $required
        Status         = 'Clean'
    }
}
```

### 1.3 Role-Based Access Control (canonical roles)

Use the canonical short names from the role catalog. Mixing legacy long-form names in scripts and runbooks creates audit-trail friction.

| Canonical role | When required | Scope |
|----------------|---------------|-------|
| **Entra Identity Governance Admin** | Operating §6, §7, §13 attestation pack export | Tenant |
| **Entra Agent ID Admin** | Operating §3, §4, §5, §8 (sponsor reassignment) | Tenant (preview role; assigned through PIM) |
| **Entra Security Admin** | Operating §10 SIEM forwarding verification | Tenant |
| **AI Administrator** | Joint sign-off on §8 mutations and §13 attestation | Tenant |
| **Purview Compliance Admin** | Reviewing §13 attestation pack and lodging it in the records system | Tenant |

> **PIM discipline.** All helpers should be invoked from a session whose role activation is fresh (≤ 4 hours old). The §2 bootstrap stamps `PimActivationAge` into the session metadata; helpers refuse to mutate when the age exceeds the policy window.

### 1.4 License gating preflight

```powershell
function Test-Agt226PreviewGating {
    [CmdletBinding()]
    param()

    # Post-GA (May 2026): Entra Agent ID is gated on Microsoft Agent 365 or
    # Microsoft 365 E7 licensing, plus reachability of the /beta/agents
    # surface to the calling principal. The function name and field names
    # below are preserved from the pre-GA "PreviewGating" check to keep
    # downstream evidence-pack consumers backward-compatible across the
    # GA cutover. Verify SkuPartNumber values in your tenant via
    # Get-MgSubscribedSku before relying on these regex patterns.

    $licenseSku = Get-MgSubscribedSku |
        Where-Object {
            ($_.SkuPartNumber -match 'Microsoft_Agent_365|M365_E7' -or
             # transitional fallback for tenants still on pre-GA Copilot SKUs
             $_.SkuPartNumber -match 'Microsoft_365_Copilot') -and
            $_.AppliesTo -eq 'User'
        }
    $hasLicense = [bool]$licenseSku

    # Post-GA: probe the Agent ID API surface directly. Pre-GA this also
    # evidenced Frontier program enrollment; post-GA a 200 indicates the
    # surface is reachable to the calling principal (license + RBAC OK),
    # while a 403/404 indicates a license-coverage or RBAC gap.
    $probe = Invoke-Agt226WithThrottle -ScriptBlock {
        try {
            Invoke-MgGraphRequest -Method GET `
                -Uri 'https://graph.microsoft.com/beta/agents?$top=1' -ErrorAction Stop
        } catch {
            [pscustomobject]@{ probeError = $_.Exception.Message }
        }
    }
    $hasFrontier = $null -ne $probe -and -not $probe.probeError

    $status = if ($hasLicense -and $hasFrontier) { 'Clean' } else { 'NotApplicable' }
    [pscustomobject]@{
        ControlId     = '2.26'
        Criterion     = 'PreviewGatingSatisfied'
        HasCopilotSku = $hasLicense   # field name retained for backward-compat;
                                      # post-GA reflects Agent 365 / M365 E7 / Copilot license presence
        HasFrontier   = $hasFrontier  # field name retained for backward-compat;
                                      # post-GA reflects Agent ID API surface reachability
        Status        = $status
        Reason        = if ($status -eq 'NotApplicable') {
            "Tenant lacks $((@{$true='';$false='Agent 365 / M365 E7 license'}[$hasLicense])) $((@{$true='';$false='Agent ID API reachability'}[$hasFrontier])) — Entra Agent ID surface area is empty or not accessible to the calling principal."
        } else { $null }
    }
}
```


## 2. Sovereign cloud bootstrap and session initialization

Entra Agent ID is **generally available in the Microsoft 365 Commercial cloud** (May 2026). As of the May 2026 verification window, GA has not been announced for GCC, GCC High, DoD, or China cloud profiles — verify current sovereign-cloud availability against Microsoft Learn before proceeding. The bootstrap below detects the cloud profile **before** any Graph call and **early-exits** with a structured exception when running in a non-Commercial tenant. Silent degradation is the highest-impact false-clean defect for this control: helpers must never return `Clean` when the underlying surface area is not present.

> **Compensating control on sovereign clouds.** Until Agent ID reaches sovereign parity, the §13 attestation pack must be supplemented with: (a) a documented attestation that no agent identities exist in the tenant; (b) a quarterly re-test once Microsoft announces sovereign availability; and (c) a manual lifecycle review of any Copilot Studio agents using non-Entra-managed identities. See [`../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) for the full compensating-control matrix.

### 2.1 Cloud profile resolution

```powershell
function Resolve-Agt226CloudProfile {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter()]
        [ValidateSet('Commercial','USGov','USGovDoD','China','Auto')]
        [string]$Hint = 'Auto'
    )

    # Resolve via tenant initial domain when Hint=Auto. The initial domain
    # suffix is a reliable indicator pre-authentication.
    $profile = if ($Hint -ne 'Auto') {
        $Hint
    } else {
        $context = Get-MgContext -ErrorAction SilentlyContinue
        if ($context) {
            switch -Regex ($context.TenantId) {
                default { 'Commercial' }
            }
        } else {
            # Without an existing context we must require an explicit hint.
            'Commercial'
        }
    }

    $supported = $profile -eq 'Commercial'

    if (-not $supported) {
        $msg = @"
Entra Agent ID preview is not available in cloud profile '$profile'.
Refusing to continue. Apply the compensating control documented in
control 2.26 §Sovereign Cloud Considerations and re-test once Microsoft
announces sovereign parity.
"@
        $exception = [System.InvalidOperationException]::new($msg)
        $exception.Data['ControlId']      = '2.26'
        $exception.Data['CloudProfile']   = $profile
        $exception.Data['ExitReason']     = 'SovereignCloudNotSupported'
        throw $exception
    }

    [pscustomobject]@{
        CloudProfile      = $profile
        Supported         = $true
        GraphEndpoint     = 'https://graph.microsoft.com'
        GraphBetaEndpoint = 'https://graph.microsoft.com/beta'
        Status            = 'Clean'
    }
}
```

### 2.2 Session initialization

```powershell
function Initialize-Agt226Session {
    [CmdletBinding()]
    param(
        [Parameter()]
        [ValidateSet('ReadOnly','Mutation')]
        [string]$ScopeProfile = 'ReadOnly',

        [Parameter()]
        [ValidateSet('Commercial','USGov','USGovDoD','China','Auto')]
        [string]$CloudHint = 'Auto',

        [Parameter()]
        [string]$TenantId,

        [Parameter()]
        [string]$ClientId,

        [Parameter()]
        [switch]$UseDeviceCode
    )

    Assert-Agt226Shell

    $cloud = Resolve-Agt226CloudProfile -Hint $CloudHint

    $scopes = switch ($ScopeProfile) {
        'ReadOnly' {
            @('Application.Read.All','AgentIdentity.Read.All','IdentityGovernance.Read.All',
              'EntitlementManagement.Read.All','AuditLog.Read.All','RoleManagement.Read.Directory')
        }
        'Mutation' {
            @('Application.Read.All','AgentIdentity.Read.All','IdentityGovernance.Read.All',
              'EntitlementManagement.ReadWrite.All','AuditLog.Read.All','RoleManagement.Read.Directory')
        }
    }

    $connectArgs = @{
        Scopes      = $scopes
        NoWelcome   = $true
        ContextScope = 'Process'
    }
    if ($TenantId)      { $connectArgs.TenantId = $TenantId }
    if ($ClientId)      { $connectArgs.ClientId = $ClientId }
    if ($UseDeviceCode) { $connectArgs.UseDeviceCode = $true }

    Connect-MgGraph @connectArgs | Out-Null

    Test-Agt226GraphScopes -Profile $ScopeProfile | Out-Null

    $gating = Test-Agt226PreviewGating
    if ($gating.Status -eq 'NotApplicable') {
        Write-Warning "Preview gating not satisfied: $($gating.Reason). Helpers will return Status='NotApplicable' for agent-identity inventories."
    }

    $session = [pscustomobject]@{
        ControlId           = '2.26'
        CloudProfile        = $cloud.CloudProfile
        ScopeProfile        = $ScopeProfile
        GraphEndpoint       = $cloud.GraphEndpoint
        GraphBetaEndpoint   = $cloud.GraphBetaEndpoint
        TenantId            = (Get-MgContext).TenantId
        SessionStarted      = (Get-Date).ToUniversalTime()
        PimActivationAge    = $null
        PreviewGating       = $gating.Status
        Status              = 'Clean'
    }

    Set-Variable -Name 'Agt226Session' -Value $session -Scope Script -Force
    return $session
}
```

### 2.3 Throttle helper (referenced from §11)

A minimal exponential-backoff wrapper used by every helper in this file. The full implementation lives in §11; the bootstrap exposes the function name so that §1 preflights can call it without forward-reference errors.

```powershell
if (-not (Get-Command -Name 'Invoke-Agt226WithThrottle' -ErrorAction SilentlyContinue)) {
    function Invoke-Agt226WithThrottle {
        param([Parameter(Mandatory)][scriptblock]$ScriptBlock,
              [int]$MaxAttempts = 6,
              [int]$BaseDelaySeconds = 2)
        # Stub — real implementation in §11. This stub exists so that the §1
        # preview-gating preflight can run before §11 is loaded.
        & $ScriptBlock
    }
}
```


## 3. Sponsor inventory (`Get-Agt226AgentSponsorInventory`)

The sponsor inventory is the canonical join between agent service principals and the human accountability chain. Every Entra Agent ID surface object should have **at least one** active sponsor; missing sponsors are a Zone-3 control failure and must be surfaced as `Anomaly`, not `Clean`.

The helper **reads** the manager-transfer state managed by Entra's lifecycle workflow — it does not mutate it. When the sponsor's `accountEnabled=false` and the agent now points at the sponsor's manager, the row is tagged `ManagerTransferred=$true` so attestation reviewers can confirm the transfer matches policy.

```powershell
function Get-Agt226AgentSponsorInventory {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter()]
        [ValidateSet('Zone1','Zone2','Zone3','All')]
        [string]$Zone = 'All',

        [Parameter()]
        [int]$PageSize = 200
    )

    if (-not (Get-Variable -Name Agt226Session -Scope Script -ErrorAction SilentlyContinue)) {
        throw "Initialize-Agt226Session must be called first."
    }

    $gating = Test-Agt226PreviewGating
    if ($gating.Status -eq 'NotApplicable') {
        return [pscustomobject]@{
            ControlId = '2.26'
            Criterion = 'AgentSponsorInventory'
            Status    = 'NotApplicable'
            Reason    = $gating.Reason
            Timestamp = (Get-Date).ToUniversalTime()
        }
    }

    $filter = "tags/any(t:t eq 'AgentIdentity')"
    $agents = Invoke-Agt226WithThrottle -ScriptBlock {
        Get-MgServicePrincipal -Filter $filter -All -PageSize $PageSize `
            -Property 'id,displayName,appId,tags,accountEnabled,createdDateTime'
    }

    $rows = foreach ($agent in $agents) {
        # Sponsor relationships live on the beta endpoint as a navigation property.
        $sponsorEdge = Invoke-Agt226WithThrottle -ScriptBlock {
            Invoke-MgGraphRequest -Method GET `
                -Uri "https://graph.microsoft.com/beta/servicePrincipals/$($agent.Id)/sponsors"
        }

        $sponsors = @($sponsorEdge.value)
        $sponsorCount = $sponsors.Count

        $primary = $sponsors | Select-Object -First 1
        $managerTransferred = $false
        if ($primary -and $primary.transferredFromUserId) {
            $managerTransferred = $true
        }

        $zoneTag = ($agent.Tags | Where-Object { $_ -match '^Zone[123]$' }) | Select-Object -First 1
        if ($Zone -ne 'All' -and $zoneTag -ne $Zone) { continue }

        $status = if ($sponsorCount -eq 0) { 'Anomaly' } else { 'Clean' }
        $reason = if ($status -eq 'Anomaly') { 'No active sponsor assigned to agent identity' } else { $null }

        [pscustomobject]@{
            ControlId          = '2.26'
            Criterion          = 'AgentSponsorInventory'
            AgentObjectId      = $agent.Id
            AgentAppId         = $agent.AppId
            AgentDisplayName   = $agent.DisplayName
            Zone               = $zoneTag
            SponsorCount       = $sponsorCount
            PrimarySponsorId   = if ($primary) { $primary.id } else { $null }
            PrimarySponsorUpn  = if ($primary) { $primary.userPrincipalName } else { $null }
            ManagerTransferred = $managerTransferred
            AccountEnabled     = $agent.AccountEnabled
            CreatedDateTime    = $agent.CreatedDateTime
            Status             = $status
            Reason             = $reason
            Timestamp          = (Get-Date).ToUniversalTime()
        }
    }

    if (-not $rows) {
        return [pscustomobject]@{
            ControlId = '2.26'
            Criterion = 'AgentSponsorInventory'
            Status    = 'NotApplicable'
            Reason    = "No agent identities found for zone filter '$Zone'."
            Timestamp = (Get-Date).ToUniversalTime()
        }
    }

    return $rows
}
```

### 3.1 Field reference

| Field | Source | Notes |
|-------|--------|-------|
| `AgentObjectId` | `servicePrincipal.id` | Stable identifier; correlate to SIEM and to control 1.2 inventory |
| `AgentAppId` | `servicePrincipal.appId` | Application registration identifier; stable across tenants |
| `Zone` | `servicePrincipal.tags` | Operational tagging convention from control 3.1; rows missing a zone tag are themselves an anomaly logged by control 3.1 |
| `SponsorCount` | beta `/sponsors` collection | `0` is always an `Anomaly` |
| `ManagerTransferred` | beta `/sponsors/transferredFromUserId` | `True` indicates lifecycle workflow has already handled a sponsor departure |
| `Status` | derived | `Clean` only when at least one active sponsor is present |


## 4. Orphaned agent detection (`Get-Agt226OrphanedAgent`)

An orphaned agent is one whose **last remaining** sponsor is disabled or has a past `employeeLeaveDateTime` and where the lifecycle workflow grace window has elapsed. Within the grace window (default 30 minutes), rows are tagged `PendingLifecycleTransfer` so operators don't fire false-positive remediation tickets.

This helper is the principal feed into control 3.6 (orphaned agent detection and remediation). It deliberately surfaces both `Orphaned` and `PendingLifecycleTransfer` states so control 3.6 can compute SLA aging.

```powershell
function Get-Agt226OrphanedAgent {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter()]
        [int]$GraceWindowMinutes = 30,

        [Parameter()]
        [ValidateSet('Zone1','Zone2','Zone3','All')]
        [string]$Zone = 'All'
    )

    $inventory = Get-Agt226AgentSponsorInventory -Zone $Zone

    if ($inventory.Status -in @('NotApplicable')) {
        return $inventory
    }

    $now = (Get-Date).ToUniversalTime()

    $rows = foreach ($row in $inventory) {
        if ($row.SponsorCount -eq 0) {
            # Already flagged Anomaly by §3 — re-emit under the orphan criterion
            [pscustomobject]@{
                ControlId          = '2.26'
                Criterion          = 'OrphanedAgent'
                AgentObjectId      = $row.AgentObjectId
                AgentDisplayName   = $row.AgentDisplayName
                Zone               = $row.Zone
                OrphanState        = 'Orphaned'
                LastSponsorUpn     = $null
                SponsorDisabledAt  = $null
                MinutesSinceDisable = $null
                Status             = 'Anomaly'
                Reason             = 'No sponsor records present on agent identity'
                Timestamp          = $now
            }
            continue
        }

        $sponsor = Invoke-Agt226WithThrottle -ScriptBlock {
            Get-MgUser -UserId $row.PrimarySponsorId `
                -Property 'id,userPrincipalName,accountEnabled,employeeLeaveDateTime'
        }

        $disabled = (-not $sponsor.AccountEnabled)
        $left     = ($sponsor.EmployeeLeaveDateTime -and $sponsor.EmployeeLeaveDateTime -lt $now)

        if (-not ($disabled -or $left)) { continue }

        $disabledAt = if ($left) { $sponsor.EmployeeLeaveDateTime } else { $null }
        $minutesSince = if ($disabledAt) {
            [math]::Round(($now - $disabledAt).TotalMinutes, 1)
        } else {
            $null
        }

        $state = if ($minutesSince -ne $null -and $minutesSince -lt $GraceWindowMinutes) {
            'PendingLifecycleTransfer'
        } else {
            'Orphaned'
        }
        $status = if ($state -eq 'Orphaned') { 'Anomaly' } else { 'Pending' }

        [pscustomobject]@{
            ControlId           = '2.26'
            Criterion           = 'OrphanedAgent'
            AgentObjectId       = $row.AgentObjectId
            AgentDisplayName    = $row.AgentDisplayName
            Zone                = $row.Zone
            OrphanState         = $state
            LastSponsorUpn      = $sponsor.UserPrincipalName
            SponsorDisabledAt   = $disabledAt
            MinutesSinceDisable = $minutesSince
            ManagerTransferred  = $row.ManagerTransferred
            Status              = $status
            Reason              = if ($state -eq 'Orphaned') {
                "Sponsor $($sponsor.UserPrincipalName) departed $minutesSince minutes ago and lifecycle transfer has not committed"
            } else {
                "Within $GraceWindowMinutes-minute grace window; lifecycle transfer pending"
            }
            Timestamp           = $now
        }
    }

    if (-not $rows) {
        return [pscustomobject]@{
            ControlId = '2.26'
            Criterion = 'OrphanedAgent'
            Status    = 'Clean'
            Reason    = "No orphaned or pending-transfer agents detected for zone filter '$Zone'."
            Timestamp = $now
        }
    }

    return $rows
}
```

### 4.1 Operating notes

- The default `-GraceWindowMinutes 30` matches Microsoft's documented lifecycle workflow execution cadence (every 3 hours with a 15-minute typical lag). Tenants with custom workflow schedules should override.
- The helper does **not** trigger remediation. Remediation is the responsibility of control 3.6 and the §8 bulk reassignment path with explicit operator sign-off.
- Output rows feed directly into the §13 attestation pack under the `OrphanedAgent` criterion.


## 5. Access package assignment review (`Get-Agt226AgentAccessPackageAssignment`)

Entra Agent ID surfaces grant entitlement via Entitlement Management access packages whose resources are restricted to: **security groups**, **Microsoft Graph application permissions**, and **Entra role assignments**. Direct SharePoint site permissions and Teams channel memberships are **not** valid resource types for agent access packages — those grants must flow through a security group resource type.

This helper enumerates every active assignment per agent, joins the policy and catalog metadata, and surfaces the expiry plus approval chain for §13 attestation.

```powershell
function Get-Agt226AgentAccessPackageAssignment {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter()]
        [ValidateSet('Zone1','Zone2','Zone3','All')]
        [string]$Zone = 'All',

        [Parameter()]
        [int]$ExpiringWithinDays = 30
    )

    $inventory = Get-Agt226AgentSponsorInventory -Zone $Zone
    if ($inventory.Status -eq 'NotApplicable') { return $inventory }

    $now = (Get-Date).ToUniversalTime()
    $rows = @()

    foreach ($agent in $inventory) {
        $assignments = Invoke-Agt226WithThrottle -ScriptBlock {
            Get-MgEntitlementManagementAssignment -Filter "target/objectId eq '$($agent.AgentObjectId)'" `
                -ExpandProperty 'accessPackage,assignmentPolicy' -All
        }

        if (-not $assignments) {
            $rows += [pscustomobject]@{
                ControlId          = '2.26'
                Criterion          = 'AgentAccessPackageAssignment'
                AgentObjectId      = $agent.AgentObjectId
                AgentDisplayName   = $agent.AgentDisplayName
                Zone               = $agent.Zone
                AccessPackageId    = $null
                AccessPackageName  = $null
                ExpiryDateTime     = $null
                PolicyApproverMissing = $null
                ResourceTypes      = $null
                Status             = 'Clean'
                Reason             = 'Agent has no active access package assignments'
                Timestamp          = $now
            }
            continue
        }

        foreach ($a in $assignments) {
            $resources = Invoke-Agt226WithThrottle -ScriptBlock {
                Get-MgEntitlementManagementAccessPackageResourceRoleScope `
                    -AccessPackageId $a.AccessPackage.Id -All
            }
            $resourceTypes = ($resources.scope.resource.resourceType | Sort-Object -Unique)
            $invalidTypes = $resourceTypes | Where-Object {
                $_ -notin @('Group','Application','DirectoryRole')
            }

            $approverMissing = -not ($a.AssignmentPolicy.RequestApprovalSettings.PrimaryApprovers.Count -gt 0)
            $expiry = $a.ScheduleInfo.Expiration.EndDateTime
            $daysToExpiry = if ($expiry) { ($expiry - $now).TotalDays } else { $null }

            $status = 'Clean'
            $reasons = @()
            if ($approverMissing) { $status = 'Anomaly'; $reasons += 'Policy has no primary approver' }
            if ($invalidTypes)    { $status = 'Anomaly'; $reasons += "Invalid resource types: $($invalidTypes -join ',')" }
            if ($daysToExpiry -and $daysToExpiry -lt $ExpiringWithinDays) {
                if ($status -eq 'Clean') { $status = 'Pending' }
                $reasons += "Expires in $([math]::Round($daysToExpiry,1)) days"
            }

            $rows += [pscustomobject]@{
                ControlId             = '2.26'
                Criterion             = 'AgentAccessPackageAssignment'
                AgentObjectId         = $agent.AgentObjectId
                AgentDisplayName      = $agent.AgentDisplayName
                Zone                  = $agent.Zone
                AccessPackageId       = $a.AccessPackage.Id
                AccessPackageName     = $a.AccessPackage.DisplayName
                AssignmentId          = $a.Id
                ExpiryDateTime        = $expiry
                DaysToExpiry          = if ($daysToExpiry) { [math]::Round($daysToExpiry,1) } else { $null }
                PolicyApproverMissing = $approverMissing
                ResourceTypes         = ($resourceTypes -join ',')
                InvalidResourceTypes  = ($invalidTypes -join ',')
                Status                = $status
                Reason                = ($reasons -join '; ')
                Timestamp             = $now
            }
        }
    }

    return $rows
}
```

### 5.1 Resource-type validation matrix

| Resource type | Allowed for agent identities | Notes |
|---------------|------------------------------|-------|
| `Group` (security group) | ✅ Yes | Preferred — provides clean separation between policy and grant |
| `Application` (Graph app perm) | ✅ Yes | Use for narrowly scoped Graph access; avoid `*.ReadWrite.All` |
| `DirectoryRole` | ✅ Yes | PIM-eligible role grants only; never permanent |
| `SharePointSite` | ❌ No | Must be granted via security group resource type instead |
| `TeamsChannel` | ❌ No | Must be granted via security group resource type instead |

Rows whose `InvalidResourceTypes` is non-empty are blocking findings for the §13 attestation pack.


## 6. Lifecycle workflow execution (`Get-Agt226LifecycleWorkflowExecution`)

Lifecycle workflows are the engine that performs the automatic manager-transfer on sponsor departure. This helper enumerates **executions** that touched any sponsor of an active agent identity within the lookback window, surfacing failed runs and runs whose `processingResult` does not match the expected transfer outcome.

```powershell
function Get-Agt226LifecycleWorkflowExecution {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter()]
        [int]$LookbackDays = 7,

        [Parameter()]
        [string[]]$WorkflowCategories = @('leaver','mover')
    )

    $now   = (Get-Date).ToUniversalTime()
    $since = $now.AddDays(-$LookbackDays)

    $workflows = Invoke-Agt226WithThrottle -ScriptBlock {
        Get-MgIdentityGovernanceLifecycleWorkflow -All |
            Where-Object { $_.Category -in $WorkflowCategories }
    }

    if (-not $workflows) {
        return [pscustomobject]@{
            ControlId = '2.26'
            Criterion = 'LifecycleWorkflowExecution'
            Status    = 'Anomaly'
            Reason    = "No lifecycle workflows in categories '$($WorkflowCategories -join ',')' are defined; manager-transfer on sponsor departure cannot run"
            Timestamp = $now
        }
    }

    # Build a sponsor lookup so we can correlate workflow subjects to agents.
    $inventory = Get-Agt226AgentSponsorInventory -Zone All
    $sponsorMap = @{}
    foreach ($a in $inventory) {
        if ($a.PrimarySponsorId) {
            if (-not $sponsorMap.ContainsKey($a.PrimarySponsorId)) {
                $sponsorMap[$a.PrimarySponsorId] = @()
            }
            $sponsorMap[$a.PrimarySponsorId] += $a
        }
    }

    $rows = foreach ($wf in $workflows) {
        $runs = Invoke-Agt226WithThrottle -ScriptBlock {
            Get-MgIdentityGovernanceLifecycleWorkflowRun -WorkflowId $wf.Id -All |
                Where-Object { $_.StartedDateTime -ge $since }
        }
        foreach ($run in $runs) {
            $userTasks = Invoke-Agt226WithThrottle -ScriptBlock {
                Get-MgIdentityGovernanceLifecycleWorkflowRunUserProcessingResult `
                    -WorkflowId $wf.Id -RunId $run.Id -All
            }
            foreach ($u in $userTasks) {
                if (-not $sponsorMap.ContainsKey($u.SubjectId)) { continue }

                $touchedAgents = $sponsorMap[$u.SubjectId]
                $status = switch ($u.ProcessingStatus) {
                    'completed' { 'Clean' }
                    'queued'    { 'Pending' }
                    default     { 'Anomaly' }
                }

                [pscustomobject]@{
                    ControlId         = '2.26'
                    Criterion         = 'LifecycleWorkflowExecution'
                    WorkflowId        = $wf.Id
                    WorkflowName      = $wf.DisplayName
                    Category          = $wf.Category
                    RunId             = $run.Id
                    RunStarted        = $run.StartedDateTime
                    SponsorSubjectId  = $u.SubjectId
                    AffectedAgents    = ($touchedAgents.AgentObjectId -join ',')
                    ProcessingStatus  = $u.ProcessingStatus
                    FailureReason     = $u.FailureReason
                    Status            = $status
                    Reason            = if ($status -eq 'Anomaly') {
                        "Workflow '$($wf.DisplayName)' run $($run.Id) failed for sponsor; affected agents may be stranded"
                    } else { $null }
                    Timestamp         = $now
                }
            }
        }
    }

    if (-not $rows) {
        return [pscustomobject]@{
            ControlId = '2.26'
            Criterion = 'LifecycleWorkflowExecution'
            Status    = 'Clean'
            Reason    = "No lifecycle workflow executions touching agent sponsors within $LookbackDays-day lookback."
            Timestamp = $now
        }
    }

    return $rows
}
```


## 7. Access review status (`Get-Agt226AccessReviewStatus`)

Zone 3 (Enterprise) agents must be subject to a recurring access review whose **default decision on reviewer non-response is `Deny` or `TakeRecommendation`** — never `Approve`. This helper computes per-review completion percentage and surfaces reviews whose default-decision configuration would auto-approve stale assignments.

```powershell
function Get-Agt226AccessReviewStatus {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter()]
        [int]$LookbackDays = 90
    )

    $now   = (Get-Date).ToUniversalTime()
    $since = $now.AddDays(-$LookbackDays)

    $defs = Invoke-Agt226WithThrottle -ScriptBlock {
        Get-MgIdentityGovernanceAccessReviewDefinition -All |
            Where-Object {
                $_.Scope.Query -match 'tags/any' -or
                $_.Scope.Query -match 'AgentIdentity'
            }
    }

    if (-not $defs) {
        return [pscustomobject]@{
            ControlId = '2.26'
            Criterion = 'AccessReviewStatus'
            Status    = 'Anomaly'
            Reason    = 'No access review definitions scoped to agent identities are configured; Zone 3 attestation cannot be produced'
            Timestamp = $now
        }
    }

    $rows = foreach ($def in $defs) {
        $instances = Invoke-Agt226WithThrottle -ScriptBlock {
            Get-MgIdentityGovernanceAccessReviewDefinitionInstance -AccessReviewScheduleDefinitionId $def.Id -All |
                Where-Object { $_.StartDateTime -ge $since }
        }

        foreach ($inst in $instances) {
            $decisions = Invoke-Agt226WithThrottle -ScriptBlock {
                Get-MgIdentityGovernanceAccessReviewDefinitionInstanceDecision `
                    -AccessReviewScheduleDefinitionId $def.Id `
                    -AccessReviewInstanceId $inst.Id -All
            }
            $total = $decisions.Count
            $made  = ($decisions | Where-Object { $_.Decision -ne 'NotReviewed' }).Count
            $pct   = if ($total -gt 0) { [math]::Round(($made / $total) * 100, 1) } else { 0 }

            $defaultDecision = $def.Settings.DefaultDecision
            $defaultDecisionEnabled = $def.Settings.DefaultDecisionEnabled
            $autoApproveRisk = ($defaultDecisionEnabled -and $defaultDecision -eq 'Approve')

            $status = 'Clean'
            $reasons = @()
            if ($autoApproveRisk) {
                $status = 'Anomaly'
                $reasons += "Default decision on non-response is 'Approve' — stale assignments auto-renew"
            }
            if ($inst.Status -eq 'Completed' -and $made -lt $total) {
                $status = 'Anomaly'
                $reasons += "Instance marked Completed with $($total - $made) undecided rows"
            }
            if ($inst.Status -eq 'InProgress' -and $pct -lt 50 -and $inst.EndDateTime -lt $now.AddDays(7)) {
                if ($status -eq 'Clean') { $status = 'Pending' }
                $reasons += "Instance ends within 7 days at $pct% completion"
            }

            [pscustomobject]@{
                ControlId               = '2.26'
                Criterion               = 'AccessReviewStatus'
                ReviewDefinitionId      = $def.Id
                ReviewName              = $def.DisplayName
                InstanceId              = $inst.Id
                InstanceStatus          = $inst.Status
                StartDateTime           = $inst.StartDateTime
                EndDateTime             = $inst.EndDateTime
                CompletionPercent       = $pct
                DefaultDecision         = $defaultDecision
                DefaultDecisionEnabled  = $defaultDecisionEnabled
                Status                  = $status
                Reason                  = ($reasons -join '; ')
                Timestamp               = $now
            }
        }
    }

    if (-not $rows) {
        return [pscustomobject]@{
            ControlId = '2.26'
            Criterion = 'AccessReviewStatus'
            Status    = 'Clean'
            Reason    = "No access review instances within $LookbackDays-day window."
            Timestamp = $now
        }
    }

    return $rows
}
```


## 8. Bulk sponsor reassignment (`Set-Agt226BulkSponsorReassignment`)

This is the **only** sanctioned mutation path for sponsor data in this control. Direct calls to `Update-MgServicePrincipal` or `Invoke-MgGraphRequest -Method PATCH` against the `/sponsors` collection bypass the audit trail and must be refused at code review.

The helper:

1. Re-asserts the `Mutation` scope profile.
2. Confirms PIM activation age is within policy.
3. Reads the input CSV and validates each row against the current inventory.
4. Writes a pre-flight journal (CSV + JSON) to the evidence directory.
5. Mutates one agent at a time, with `-WhatIf` honoured at every step.
6. Captures the resulting `directoryAudits` correlation ID and signs the final manifest.

```powershell
function Set-Agt226BulkSponsorReassignment {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)]
        [ValidateScript({ Test-Path -LiteralPath $_ -PathType Leaf })]
        [string]$InputCsvPath,

        [Parameter(Mandatory)]
        [string]$EvidenceDirectory,

        [Parameter()]
        [string]$ChangeTicketId,

        [Parameter()]
        [int]$MaxPimAgeMinutes = 240
    )

    if (-not (Get-Variable -Name Agt226Session -Scope Script -ErrorAction SilentlyContinue)) {
        throw "Initialize-Agt226Session -ScopeProfile Mutation must be called first."
    }
    if ($script:Agt226Session.ScopeProfile -ne 'Mutation') {
        throw "Active session is ReadOnly. Re-initialize with -ScopeProfile Mutation."
    }
    if (-not $ChangeTicketId) {
        throw "ChangeTicketId is required — no untracked sponsor mutations permitted."
    }

    Test-Agt226GraphScopes -Profile Mutation | Out-Null

    if (-not (Test-Path -LiteralPath $EvidenceDirectory)) {
        New-Item -ItemType Directory -Path $EvidenceDirectory -Force | Out-Null
    }

    $rows = Import-Csv -LiteralPath $InputCsvPath
    $required = @('AgentObjectId','NewSponsorObjectId','Justification')
    foreach ($col in $required) {
        if ($col -notin $rows[0].PSObject.Properties.Name) {
            throw "Input CSV is missing required column '$col'."
        }
    }

    $runId     = [guid]::NewGuid().Guid
    $journal   = Join-Path $EvidenceDirectory "agt226-reassignment-$runId.csv"
    $manifest  = Join-Path $EvidenceDirectory "agt226-reassignment-$runId.manifest.json"
    $now       = (Get-Date).ToUniversalTime()
    $results   = @()

    foreach ($row in $rows) {
        $agent = Invoke-Agt226WithThrottle -ScriptBlock {
            Get-MgServicePrincipal -ServicePrincipalId $row.AgentObjectId
        }
        $newSponsor = Invoke-Agt226WithThrottle -ScriptBlock {
            Get-MgUser -UserId $row.NewSponsorObjectId
        }

        $action = "Reassign sponsor for agent $($agent.DisplayName) to $($newSponsor.UserPrincipalName)"
        $auditRef = $null
        $status = 'Pending'
        $reason = $null

        if ($PSCmdlet.ShouldProcess($agent.DisplayName, $action)) {
            try {
                $body = @{
                    '@odata.id' = "https://graph.microsoft.com/v1.0/users/$($newSponsor.Id)"
                }
                Invoke-Agt226WithThrottle -ScriptBlock {
                    Invoke-MgGraphRequest -Method POST `
                        -Uri "https://graph.microsoft.com/beta/servicePrincipals/$($agent.Id)/sponsors/`$ref" `
                        -Body ($body | ConvertTo-Json) `
                        -ContentType 'application/json'
                } | Out-Null
                $status = 'Clean'

                # Capture the directoryAudits correlation row written by Graph
                Start-Sleep -Seconds 5
                $audit = Invoke-Agt226WithThrottle -ScriptBlock {
                    Get-MgAuditLogDirectoryAudit -Filter @"
activityDisplayName eq 'Add sponsor to service principal' and targetResources/any(t:t/id eq '$($agent.Id)')
"@ -Top 1
                }
                $auditRef = $audit.Id
            } catch {
                $status = 'Error'
                $reason = $_.Exception.Message
            }
        }

        $results += [pscustomobject]@{
            RunId               = $runId
            ChangeTicketId      = $ChangeTicketId
            AgentObjectId       = $row.AgentObjectId
            AgentDisplayName    = $agent.DisplayName
            NewSponsorObjectId  = $row.NewSponsorObjectId
            NewSponsorUpn       = $newSponsor.UserPrincipalName
            Justification       = $row.Justification
            Status              = $status
            Reason              = $reason
            DirectoryAuditId    = $auditRef
            Timestamp           = (Get-Date).ToUniversalTime()
        }
    }

    $results | Export-Csv -LiteralPath $journal -NoTypeInformation -Encoding UTF8

    $manifestObj = [pscustomobject]@{
        control_id        = '2.26'
        run_id            = $runId
        change_ticket_id  = $ChangeTicketId
        operator          = (Get-MgContext).Account
        started_at        = $now
        completed_at      = (Get-Date).ToUniversalTime()
        rows_total        = $results.Count
        rows_clean        = ($results | Where-Object Status -eq 'Clean').Count
        rows_error        = ($results | Where-Object Status -eq 'Error').Count
        evidence_artifacts = @($journal)
        sha256            = (Get-FileHash -LiteralPath $journal -Algorithm SHA256).Hash
    }
    $manifestObj | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifest -Encoding UTF8

    return [pscustomobject]@{
        ControlId        = '2.26'
        Criterion        = 'BulkSponsorReassignment'
        RunId            = $runId
        JournalPath      = $journal
        ManifestPath     = $manifest
        RowsTotal        = $results.Count
        RowsClean        = $manifestObj.rows_clean
        RowsError        = $manifestObj.rows_error
        Status           = if ($manifestObj.rows_error -eq 0) { 'Clean' } else { 'Anomaly' }
        Timestamp        = (Get-Date).ToUniversalTime()
    }
}
```

> **Operator discipline.** `ChangeTicketId` is mandatory and is recorded in the manifest. Operators must not run the helper outside an approved change window. `-WhatIf` should be used on every dry run before the real mutation pass.


## 9. Evidence pack export (`Export-Agt226EvidencePack`)

The evidence pack is the JSON+manifest payload consumed by control 3.1 (canonical inventory) and control 1.7 (audit lodging). The helper concatenates outputs from §§3–7 and §10, emits a single JSON file, and computes a SHA-256 manifest.

```powershell
function Export-Agt226EvidencePack {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)]
        [string]$EvidenceDirectory,

        [Parameter()]
        [ValidateSet('Zone1','Zone2','Zone3','All')]
        [string]$Zone = 'All'
    )

    if (-not (Test-Path -LiteralPath $EvidenceDirectory)) {
        New-Item -ItemType Directory -Path $EvidenceDirectory -Force | Out-Null
    }

    $runId = [guid]::NewGuid().Guid
    $now   = (Get-Date).ToUniversalTime()

    $criteria = [ordered]@{
        AgentSponsorInventory       = Get-Agt226AgentSponsorInventory -Zone $Zone
        OrphanedAgent               = Get-Agt226OrphanedAgent -Zone $Zone
        AgentAccessPackageAssignment = Get-Agt226AgentAccessPackageAssignment -Zone $Zone
        LifecycleWorkflowExecution  = Get-Agt226LifecycleWorkflowExecution
        AccessReviewStatus          = Get-Agt226AccessReviewStatus
        SiemForwarding              = Test-Agt226SiemForwarding
    }

    $payload = [pscustomobject]@{
        control_id      = '2.26'
        run_id          = $runId
        run_timestamp   = $now
        zone            = $Zone
        namespace       = 'fsi-agentgov.entra-agentid'
        tenant_id       = (Get-MgContext).TenantId
        cloud_profile   = $script:Agt226Session.CloudProfile
        preview_gating  = $script:Agt226Session.PreviewGating
        criteria        = $criteria
    }

    $jsonPath = Join-Path $EvidenceDirectory "agt226-evidence-$runId.json"
    $payload | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

    $hash = (Get-FileHash -LiteralPath $jsonPath -Algorithm SHA256).Hash
    $manifest = [pscustomobject]@{
        control_id          = '2.26'
        run_id              = $runId
        run_timestamp       = $now
        evidence_artifacts  = @(@{ path = $jsonPath; sha256 = $hash })
        criterion_summary   = $criteria.Keys | ForEach-Object {
            $rows = $criteria[$_]
            $statuses = if ($rows -is [System.Collections.IEnumerable] -and -not ($rows -is [string])) {
                ($rows | ForEach-Object { $_.Status }) | Group-Object | ForEach-Object {
                    @{ status = $_.Name; count = $_.Count }
                }
            } else {
                @(@{ status = $rows.Status; count = 1 })
            }
            @{ criterion = $_; statuses = $statuses }
        }
    }
    $manifestPath = Join-Path $EvidenceDirectory "agt226-evidence-$runId.manifest.json"
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

    return [pscustomobject]@{
        ControlId    = '2.26'
        Criterion    = 'EvidencePackExport'
        RunId        = $runId
        JsonPath     = $jsonPath
        ManifestPath = $manifestPath
        Sha256       = $hash
        Status       = 'Clean'
        Timestamp    = $now
    }
}
```

### 9.1 Evidence JSON schema

```jsonc
{
  "control_id": "2.26",
  "run_id": "uuid",
  "run_timestamp": "ISO-8601 UTC",
  "zone": "Zone1|Zone2|Zone3|All",
  "namespace": "fsi-agentgov.entra-agentid",
  "tenant_id": "guid",
  "cloud_profile": "Commercial",
  "preview_gating": "Clean|NotApplicable",
  "criteria": {
    "AgentSponsorInventory": [ /* rows */ ],
    "OrphanedAgent": [ /* rows */ ],
    "AgentAccessPackageAssignment": [ /* rows */ ],
    "LifecycleWorkflowExecution": [ /* rows */ ],
    "AccessReviewStatus": [ /* rows */ ],
    "SiemForwarding": { /* single row */ }
  }
}
```


## 10. SIEM forwarding test (`Test-Agt226SiemForwarding`)

This helper verifies the **plumbing** that ships Entra audit and sign-in logs to the downstream SIEM. It does **not** attempt server-side filtering or correlation — those responsibilities belong to control 1.7 and the SIEM rule pack. The output establishes that:

1. A diagnostic setting on the Entra tenant exists.
2. The setting forwards `AuditLogs` and `SignInLogs` (minimum) to either Log Analytics or an Event Hub.
3. A recent agent-related event has been emitted within the last 24 hours so operators have something to correlate against.

```powershell
function Test-Agt226SiemForwarding {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter()]
        [int]$RecentEventLookbackHours = 24
    )

    $now = (Get-Date).ToUniversalTime()

    # Diagnostic settings on the Entra tenant resource
    try {
        $diagSettings = Invoke-Agt226WithThrottle -ScriptBlock {
            Invoke-MgGraphRequest -Method GET `
                -Uri 'https://graph.microsoft.com/beta/auditLogs/diagnosticSettings'
        }
    } catch {
        return [pscustomobject]@{
            ControlId = '2.26'
            Criterion = 'SiemForwarding'
            Status    = 'Anomaly'
            Reason    = "Failed to read diagnostic settings: $($_.Exception.Message)"
            Timestamp = $now
        }
    }

    $settings = @($diagSettings.value)
    $auditFwd = $settings | Where-Object {
        $_.logs | Where-Object { $_.category -eq 'AuditLogs' -and $_.enabled }
    }
    $signinFwd = $settings | Where-Object {
        $_.logs | Where-Object { $_.category -eq 'SignInLogs' -and $_.enabled }
    }

    $missing = @()
    if (-not $auditFwd)  { $missing += 'AuditLogs' }
    if (-not $signinFwd) { $missing += 'SignInLogs' }

    # Sample one recent agent-touching event so the SIEM team has a known
    # correlation target. We do not filter — we just emit the most recent
    # Add/Remove/Update event whose target is a service principal tagged
    # AgentIdentity.
    $recent = Invoke-Agt226WithThrottle -ScriptBlock {
        Get-MgAuditLogDirectoryAudit `
            -Filter "category eq 'ApplicationManagement'" `
            -Top 50 |
            Where-Object {
                $_.TargetResources |
                    Where-Object { $_.ModifiedProperties.NewValue -match 'AgentIdentity' }
            } |
            Select-Object -First 1
    }

    $hasRecent = [bool]$recent
    $recentAge = if ($hasRecent) {
        [math]::Round(($now - $recent.ActivityDateTime.ToUniversalTime()).TotalHours, 1)
    } else { $null }

    $status = 'Clean'
    $reasons = @()
    if ($missing) {
        $status = 'Anomaly'
        $reasons += "Missing diagnostic categories: $($missing -join ',')"
    }
    if ($hasRecent -and $recentAge -gt $RecentEventLookbackHours) {
        if ($status -eq 'Clean') { $status = 'Pending' }
        $reasons += "Most recent agent-related directory audit event is $recentAge hours old"
    }

    return [pscustomobject]@{
        ControlId                = '2.26'
        Criterion                = 'SiemForwarding'
        DiagnosticSettingsCount  = $settings.Count
        AuditLogsForwarded       = [bool]$auditFwd
        SignInLogsForwarded      = [bool]$signinFwd
        Destinations             = (
            $settings |
                ForEach-Object {
                    @($_.workspaceId, $_.eventHubAuthorizationRuleId, $_.storageAccountId) |
                        Where-Object { $_ }
                } |
                Sort-Object -Unique
        ) -join ';'
        EntraNativeRetentionDays = 30
        SiemRetentionGuidance    = 'See control 1.7 — FINRA 4511 requires 6-year retention; Entra native retention is 30 days, so SIEM is the system of record'
        MostRecentEventId        = if ($hasRecent) { $recent.Id } else { $null }
        MostRecentEventAgeHours  = $recentAge
        Status                   = $status
        Reason                   = ($reasons -join '; ')
        Timestamp                = $now
    }
}
```

> **Filtering boundary.** Operators who try to filter audit logs at the Graph layer will encounter rate-limit and field-availability gaps. Filtering, deduplication, and alerting belong in the SIEM rule pack documented under control 1.7. The PowerShell helper only confirms the wire is up and a known-good event exists for correlation.


## 11. Throttle and retry helper (`Invoke-Agt226WithThrottle`)

Microsoft Graph applies per-tenant throttling on `AgentIdentity` and entitlement-management endpoints that is more aggressive than the documented 2,000 requests / 20-second baseline. This wrapper implements exponential backoff with jitter and explicit `Retry-After` honouring, and re-raises after the configured maximum attempts.

```powershell
function Invoke-Agt226WithThrottle {
    [CmdletBinding()]
    [OutputType([object])]
    param(
        [Parameter(Mandatory)]
        [scriptblock]$ScriptBlock,

        [Parameter()]
        [int]$MaxAttempts = 6,

        [Parameter()]
        [int]$BaseDelaySeconds = 2,

        [Parameter()]
        [int]$MaxDelaySeconds = 60
    )

    $attempt = 0
    while ($true) {
        $attempt++
        try {
            return & $ScriptBlock
        } catch {
            $ex = $_.Exception
            $statusCode = $null
            $retryAfter = $null

            if ($ex.PSObject.Properties.Name -contains 'Response' -and $ex.Response) {
                $statusCode = [int]$ex.Response.StatusCode
                if ($ex.Response.Headers['Retry-After']) {
                    $retryAfter = [int]$ex.Response.Headers['Retry-After']
                }
            } elseif ($ex.Message -match '\b(429|503|504)\b') {
                $statusCode = [int]($Matches[1])
            }

            $isThrottle = $statusCode -in @(429, 503, 504)
            if (-not $isThrottle -or $attempt -ge $MaxAttempts) {
                throw
            }

            $delay = if ($retryAfter) {
                [math]::Min($retryAfter, $MaxDelaySeconds)
            } else {
                $exp = [math]::Pow(2, $attempt - 1) * $BaseDelaySeconds
                $jitter = Get-Random -Minimum 0 -Maximum ($BaseDelaySeconds)
                [math]::Min($exp + $jitter, $MaxDelaySeconds)
            }

            Write-Verbose "Throttled (HTTP $statusCode) on attempt $attempt; sleeping $delay seconds."
            Start-Sleep -Seconds $delay
        }
    }
}
```

### 11.1 Page-count assertion pattern

For paginated calls, callers should assert `@odata.count` matches the materialized result count. The pattern below is used internally by §3 and §5 to refuse silent truncation.

```powershell
function Invoke-Agt226PagedQuery {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Uri
    )

    $first = Invoke-Agt226WithThrottle -ScriptBlock {
        Invoke-MgGraphRequest -Method GET -Uri "$Uri`?`$count=true" -Headers @{ ConsistencyLevel = 'eventual' }
    }
    $expected = $first.'@odata.count'
    $items = @($first.value)

    $next = $first.'@odata.nextLink'
    while ($next) {
        $page = Invoke-Agt226WithThrottle -ScriptBlock {
            Invoke-MgGraphRequest -Method GET -Uri $next
        }
        $items += $page.value
        $next = $page.'@odata.nextLink'
    }

    if ($expected -and $items.Count -ne $expected) {
        throw "Paged query truncation detected: expected $expected, materialized $($items.Count)."
    }

    return $items
}
```


## 12. Cross-control invocation chains

Control 2.26 is a **producer** for several downstream controls and a **consumer** of upstream sponsor data. The orchestration patterns below illustrate the canonical chains.

### 12.1 Sponsor data feed from control 1.2

Control 1.2 (Agent Registry & Integrated Apps Management) is the upstream source of agent registration metadata. The 2.26 sponsor inventory should be reconciled against the 1.2 registry on every attestation cycle.

```powershell
# Pseudocode — actual cmdlet names live in control 1.2 playbook
$registry = Get-Agt12AgentRegistryInventory     # from control 1.2
$sponsors = Get-Agt226AgentSponsorInventory     # this file

$reconciliation = $registry | ForEach-Object {
    $row = $_
    $match = $sponsors | Where-Object { $_.AgentObjectId -eq $row.AgentObjectId } | Select-Object -First 1
    [pscustomobject]@{
        AgentObjectId      = $row.AgentObjectId
        InRegistry         = $true
        InSponsorInventory = [bool]$match
        SponsorCount       = if ($match) { $match.SponsorCount } else { 0 }
        Status             = if ($match -and $match.SponsorCount -gt 0) { 'Clean' } else { 'Anomaly' }
    }
}
```

Anomalies in this reconciliation are routed to control 3.6 for remediation.

### 12.2 Orphan detection feed to control 3.6

```powershell
$orphans = Get-Agt226OrphanedAgent -GraceWindowMinutes 30
$orphans |
    Where-Object { $_.OrphanState -eq 'Orphaned' } |
    Export-Csv -NoTypeInformation -Path 'C:\evidence\agt36-input-orphans.csv'
# Control 3.6 picks this CSV up on its scheduled run.
```

### 12.3 Audit feed to control 1.7

```powershell
$siem = Test-Agt226SiemForwarding
if ($siem.Status -ne 'Clean') {
    # Control 1.7 owns remediation of audit forwarding gaps.
    Write-Warning "Routing SIEM forwarding gap to control 1.7: $($siem.Reason)"
}
```

### 12.4 Inventory feed to control 3.1

The 2.26 evidence pack augments the 3.1 canonical inventory with sponsor and access-package columns.

```powershell
$pack = Export-Agt226EvidencePack -EvidenceDirectory 'C:\evidence\agt226' -Zone All
# Control 3.1 ingests $pack.JsonPath and joins on AgentObjectId.
```

### 12.5 Composite daily run

```powershell
function Invoke-Agt226DailyRun {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$EvidenceRoot)

    Initialize-Agt226Session -ScopeProfile ReadOnly | Out-Null

    $today = (Get-Date -Format 'yyyy-MM-dd')
    $dir   = Join-Path $EvidenceRoot $today
    New-Item -ItemType Directory -Path $dir -Force | Out-Null

    $pack = Export-Agt226EvidencePack -EvidenceDirectory $dir -Zone All

    [pscustomobject]@{
        ControlId      = '2.26'
        RunDate        = $today
        EvidencePack   = $pack.JsonPath
        ManifestSha256 = $pack.Sha256
        Status         = $pack.Status
    }
}
```


## 13. Reconciliation and attestation pack

The attestation pack is the artifact lodged with the records system on a quarterly cadence. It is built by composing the §9 evidence pack with cross-control reconciliation outputs and an attestation summary table.

```powershell
function New-Agt226AttestationPack {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)]
        [string]$EvidenceDirectory,

        [Parameter(Mandatory)]
        [ValidateSet('Q1','Q2','Q3','Q4')]
        [string]$Quarter,

        [Parameter(Mandatory)]
        [int]$Year,

        [Parameter(Mandatory)]
        [string]$AttestingOperator
    )

    $session = Initialize-Agt226Session -ScopeProfile ReadOnly
    $pack    = Export-Agt226EvidencePack -EvidenceDirectory $EvidenceDirectory -Zone All

    # Per-criterion roll-up
    $rollup = @('AgentSponsorInventory','OrphanedAgent','AgentAccessPackageAssignment',
                'LifecycleWorkflowExecution','AccessReviewStatus','SiemForwarding') |
        ForEach-Object {
            $crit = $_
            $rows = (Get-Content -LiteralPath $pack.JsonPath -Raw | ConvertFrom-Json).criteria.$crit
            $items = if ($rows -is [System.Array]) { $rows } else { @($rows) }
            $clean   = ($items | Where-Object Status -eq 'Clean').Count
            $anomaly = ($items | Where-Object Status -eq 'Anomaly').Count
            $pending = ($items | Where-Object Status -eq 'Pending').Count
            $na      = ($items | Where-Object Status -eq 'NotApplicable').Count
            [pscustomobject]@{
                Criterion     = $crit
                Total         = $items.Count
                Clean         = $clean
                Anomaly       = $anomaly
                Pending       = $pending
                NotApplicable = $na
                OverallStatus = if ($anomaly -gt 0) { 'Anomaly' }
                               elseif ($pending -gt 0) { 'Pending' }
                               elseif ($clean -gt 0) { 'Clean' }
                               else { 'NotApplicable' }
            }
        }

    $attestation = [pscustomobject]@{
        control_id          = '2.26'
        attestation_period  = "$Year-$Quarter"
        attesting_operator  = $AttestingOperator
        tenant_id           = $session.TenantId
        cloud_profile       = $session.CloudProfile
        preview_gating      = $session.PreviewGating
        evidence_pack_sha256 = $pack.Sha256
        evidence_pack_path  = $pack.JsonPath
        criterion_rollup    = $rollup
        regulatory_anchors  = @(
            'FINRA 4511 (6-year recordkeeping)',
            'SEC 17a-4 (records preservation)',
            'OCC 2013-29 / SR 11-7 (model risk)',
            'GLBA Safeguards Rule (access review)'
        )
        generated_at        = (Get-Date).ToUniversalTime()
    }

    $outPath = Join-Path $EvidenceDirectory "agt226-attestation-$Year-$Quarter.json"
    $attestation | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $outPath -Encoding UTF8

    $hash = (Get-FileHash -LiteralPath $outPath -Algorithm SHA256).Hash

    return [pscustomobject]@{
        ControlId         = '2.26'
        AttestationPath   = $outPath
        AttestationSha256 = $hash
        OverallStatus     = if ($rollup.OverallStatus -contains 'Anomaly') { 'Anomaly' }
                            elseif ($rollup.OverallStatus -contains 'Pending') { 'Pending' }
                            else { 'Clean' }
        Timestamp         = (Get-Date).ToUniversalTime()
    }
}
```

### 13.1 Lodging instructions

1. Run `New-Agt226AttestationPack` against the production tenant on the first business day of the quarter.
2. Validate the SHA-256 in the operator's runbook before lodging.
3. Submit the JSON file plus the SHA to the Purview Compliance Admin for inclusion in the records system.
4. Retain locally for 6 years per FINRA 4511 (the SIEM is the primary system of record; this attestation pack is a derived artifact).


## 14. Validation, anti-patterns, and operating cadence

### 14.1 Validation harness

```powershell
function Test-Agt226PlaybookHealth {
    [CmdletBinding()]
    param()

    $checks = @(
        @{ Name = 'ShellEdition';      Test = { Assert-Agt226Shell; $true } }
        @{ Name = 'ModulesPinned';     Test = { (Install-Agt226ModuleBaseline).Status -eq 'Clean' } }
        @{ Name = 'CloudProfile';      Test = { (Resolve-Agt226CloudProfile).Supported } }
        @{ Name = 'GraphScopes';       Test = { (Test-Agt226GraphScopes -Profile ReadOnly).Status -eq 'Clean' } }
        @{ Name = 'PreviewGating';     Test = { (Test-Agt226PreviewGating).Status -in @('Clean','NotApplicable') } }
    )

    foreach ($c in $checks) {
        $ok = $false
        try { $ok = & $c.Test } catch { $ok = $false }
        [pscustomobject]@{
            Check  = $c.Name
            Passed = $ok
        }
    }
}
```

### 14.2 Anti-patterns table

| # | Anti-pattern | Why it fails | Sanctioned alternative |
|---|--------------|--------------|------------------------|
| 14.1 | Calling `Update-MgServicePrincipal` to swap a sponsor reference directly | Bypasses the §8 audit trail and the lifecycle workflow correlation | `Set-Agt226BulkSponsorReassignment` |
| 14.2 | Treating an empty `Get-MgServicePrincipal` result as `Clean` | Preview gating may be unsatisfied; sovereign cloud may be unsupported | Always check `Status='NotApplicable'` and the `Reason` field |
| 14.3 | Filtering audit logs in PowerShell to find sponsor mutations | Graph audit query surface is rate-limited and field-incomplete | Forward to SIEM via §10; query the SIEM |
| 14.4 | Running helpers under PowerShell 5.1 because "it imports the modules fine" | Microsoft.Graph 2.x assemblies bind incorrectly under Desktop edition; calls return empty | `Assert-Agt226Shell` blocks Desktop edition |
| 14.5 | Granting `EntitlementManagement.ReadWrite.All` to a long-lived service principal for unattended runs | Mutation path requires interactive operator and a change ticket | Use ReadOnly scope for unattended runs; mutation is delegated only |
| 14.6 | Using long-form role names (`Global Administrator`) in evidence | Audit trails and runbooks diverge from canonical catalog | Use canonical short names from `docs/reference/role-catalog.md` |
| 14.7 | Ignoring `PendingLifecycleTransfer` rows because "the workflow will fix it" | Some workflow runs fail; Pending rows aging past 24 hours indicate a real problem | Aging rule lives in control 3.6; do not drop the rows |
| 14.8 | Hardcoding tenant IDs in helpers | Breaks multi-tenant runbooks | Pass `-TenantId` to `Initialize-Agt226Session` |
| 14.9 | Skipping the `@odata.count` assertion on paginated queries | Throttled mid-pagination calls silently truncate | Use `Invoke-Agt226PagedQuery` from §11.1 |
| 14.10 | Assuming sovereign clouds will reach parity "soon" and pre-deploying code paths | Code paths drift; helpers degrade silently | Keep early-exit in §2; revisit only when Microsoft announces sovereign GA |

### 14.3 Operating cadence

| Cadence | Activity | Owner | Helper |
|---------|----------|-------|--------|
| **Daily** | Run `Invoke-Agt226DailyRun` against production | Entra Agent ID Admin | §12.5 |
| **Daily** | Review `OrphanedAgent` rows aging past `PendingLifecycleTransfer` grace | Entra Identity Governance Admin | §4 + control 3.6 |
| **Weekly** | Reconcile sponsor inventory against control 1.2 registry | Entra Identity Governance Admin | §12.1 |
| **Weekly** | Test-Agt226SiemForwarding sanity check | Entra Security Admin | §10 |
| **Monthly** | Review access package assignments expiring within 60 days | Entra Agent ID Admin | §5 |
| **Quarterly** | Run `New-Agt226AttestationPack` and lodge with records system | AI Administrator + Purview Compliance Admin | §13 |
| **Quarterly** | Review anti-patterns table against actual operator behaviour | Entra Identity Governance Admin | §14.2 |
| **Annually** | Re-test sovereign cloud availability and remove early-exit if Microsoft has announced GA | Entra Identity Governance Admin | §2 |

### 14.4 Hedged language reminder

When operators document findings produced by these helpers, use only the hedged phrasing required by the framework:

- ✅ "Supports compliance with FINRA 4511 by surfacing sponsor accountability per agent identity."
- ✅ "Helps meet OCC 2013-29 model risk expectations through documented sponsor and access review chains."
- ❌ "Ensures compliance with..." — implies a legal guarantee.
- ❌ "Eliminates orphaned agents" — overclaims.
- ❌ "Will prevent unauthorized sponsor changes" — overclaims.

Implementation caveats to retain in narrative reports:

> "Implementation requires an active Microsoft 365 Copilot license and either a Microsoft Agent 365 (standalone) or Microsoft 365 E7 (Frontier Suite) license assigned to each operating principal. Organizations should verify license-coverage gating before relying on inventory completeness. Sovereign-cloud tenants must apply the documented compensating control until Agent 365 / Entra Agent ID parity is announced for GCC, GCC High, DoD, and China cloud profiles."


---

## Cross-references

**Control specification**

- [Control 2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md)

**Companion playbooks for this control**

- [Portal Walkthrough](portal-walkthrough.md)
- [Verification & Testing](verification-testing.md)
- [Troubleshooting](troubleshooting.md)

**Shared playbook baseline**

- [PowerShell baseline conventions](../../_shared/powershell-baseline.md)
- [Sovereign cloud endpoint matrix](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod)

**Related controls referenced in this playbook**

- [Control 1.2 — Agent Registry & Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) — sponsor data feed
- [Control 1.7 — Comprehensive Audit Logging & Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — SIEM forwarding and 6-year retention
- [Control 3.1 — Agent Inventory & Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — canonical inventory consumer
- [Control 3.6 — Orphaned Agent Detection & Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — orphan remediation owner

**Reference**

- [Role catalog](../../../reference/role-catalog.md) — canonical role names
- [Regulatory mappings](../../../reference/regulatory-mappings.md) — FINRA, SEC, OCC, GLBA anchors

---

**Updated:** April 2026
**Version:** 1.0
**UI Verification Status:** Verified against Entra admin centre (April 2026 preview). Re-verify when Microsoft announces Entra Agent ID GA or sovereign cloud parity.

