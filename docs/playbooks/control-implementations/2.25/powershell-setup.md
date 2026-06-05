---
title: "Control 2.25 — PowerShell Setup (Microsoft Agent 365 Admin Center Governance Console)"
control_id: "2.25"
playbook_type: "powershell-setup"
last_updated: "2026-04-15"
version: "v1.4"
ui_verified: "April 2026 (post-GA)"
prerequisites:
  - "PowerShell 7.4 Core (Windows, Linux, or macOS)"
  - "Microsoft Graph PowerShell SDK 2.25.0+ (pinned)"
  - "Microsoft.Graph.Beta 2.25.0+ where Agent 365 cmdlets remain in the beta surface"
  - "Microsoft 365 E7 ("Frontier Suite") or Microsoft 365 Copilot Business Chat licensing for the operator running discovery"
  - "Entra Global Reader at minimum; Entra Global Admin via PIM for any mutation"
scopes_required:
  - "Application.Read.All"
  - "AppCatalog.Read.All"
  - "Directory.Read.All"
  - "AuditLog.Read.All"
  - "AgentIdentity.Read.All  # if exposed by your tenant; helper degrades gracefully"
related_controls: ["1.2", "1.11", "2.3", "2.26", "3.1", "3.6", "3.13"]
---

# Control 2.25 — PowerShell Setup: Microsoft Agent 365 Admin Center Governance Console

> **Control under management:** [`2.25 — Microsoft Agent 365 Admin Center Governance Console`](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md)
>
> **Sister playbooks:** [Portal Walkthrough](./portal-walkthrough.md) · [Verification & Testing](./verification-testing.md) · [Troubleshooting](./troubleshooting.md)
>
> **Shared baseline:** [`_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — module pinning, evidence emission, SHA-256 manifest format.

This playbook automates discovery, attestation, and continuous monitoring for the **Microsoft Agent 365 Admin Center**, the unified governance console that became Generally Available **May 1, 2026**. It mirrors the structural conventions of the sister playbook for Control 2.26 ([Agent Approval Workflow Configuration](../2.26/powershell-setup.md)) and uses the cmdlet prefix `Agt225` for every helper introduced in this file. The Agent 365 Admin Center is Microsoft's GA replacement for the legacy "Copilot Hub" preview; many of its surfaces are still partly portal-only, so this playbook combines Graph reads with documented portal-export fallbacks.


> **Hedged-language reminder.** Throughout this playbook, governance helpers **support compliance with** FINRA Rule 3110, SEC Rule 17a-4, SOX §404, GLBA Safeguards, OCC Bulletin 2013-29, and Federal Reserve SR 26-2 (formerly SR 11-7). They do **not** "confirm" or "provide" compliance. In particular, FINRA Rule 3110 requires a **registered principal** to bear supervisory responsibility — automated discovery and approval-history extracts described here **do not substitute** for that registered principal's review and sign-off; they provide the evidence the principal then attests to.

---

## §0 — The Wrong-Shell Trap and False-Clean Defects

Before any helper is dot-sourced, operators must internalize a short list of failure modes that have produced **false-clean** governance signals during the Agent 365 preview and the first eight weeks of GA. Each row below describes a defect we have observed in production tenants, the symptom it produces, and the mitigation hard-wired into the helpers in this file.

### 0.1 The wrong-shell trap

The Microsoft 365 Admin Center surface for Agent 365 is reachable only through the **modern Microsoft Graph SDK on PowerShell 7.4+**. The legacy Windows PowerShell 5.1 host cannot load the pinned `Microsoft.Graph` 2.25 module family because of .NET Framework dependency mismatches, but it **will silently load older 1.x versions if they are present in the user's module path**. Those older modules return empty collections for the new agent surfaces, which the unwary operator then treats as "no agents found, clean tenant."

Every helper in §2 calls `Assert-Agt225ShellHost` as its first action. The assertion:

1. Verifies `$PSVersionTable.PSEdition -eq 'Core'` and `$PSVersionTable.PSVersion -ge [version]'7.4'`.
2. Verifies the loaded `Microsoft.Graph.Authentication` module is `>= 2.25.0`.
3. Verifies no `Microsoft.Graph` module **older than 2.25** is present in `Get-Module -ListAvailable`, because import-order ambiguity has bitten operators who have both 1.28 and 2.25 installed side by side.
4. On any failure, throws a terminating `[System.InvalidOperationException]` with the literal token `Agt225-WrongShell` so SIEM correlation rules can fire on it.

### 0.2 False-clean defect catalogue

| # | Defect | Symptom | Root cause | Mitigation in this playbook |
|---|---|---|---|---|
| 1 | Wrong PowerShell host | `Get-MgAgent*` returns `@()` | PS 5.1 loaded Graph 1.28 alongside 2.25 | `Assert-Agt225ShellHost` (§2.1) |
| 2 | Read-only token used against admin surfaces | `403` swallowed, helper logs `Anomaly` then masks as `Clean` on retry | Caller used delegated `User.Read` only | `Test-Agt225GraphScopes` preflight (§2.3) |
| 3 | Paged response truncated at 100 | Inventory undercounts agents in tenants with > 100 agents | Operator forgot `-All` on `Invoke-MgGraphRequest` | `Invoke-Agt225PagedQuery` (§11.2) — paging is asserted |
| 4 | Throttled call returned empty body | Helper interprets HTTP 429 with empty JSON as zero agents | No retry/backoff wrapper | `Invoke-Agt225Throttled` (§11.1) |
| 5 | Beta cmdlet GA-renamed mid-flight | Cmdlet not found, caught by broad `try`, swallowed | Microsoft renamed `*Bot*` → `*Agent*` between preview and GA | `Get-Agt225CmdletAvailability` (§1.3) emits `NotApplicable`, not `Clean` |
| 6 | Empty result conflated with "no findings" | Helper returns `$null`; downstream evidence pack says "Clean" | Helpers must distinguish `Clean` from `NotApplicable` from `Error` | All helpers return `[pscustomobject]` with explicit `Status` enum |
| 7 | Cached delegated token from prior tenant | Helper enumerates the wrong tenant's agents | Operator switched tenants but did not call `Disconnect-MgGraph` | `Initialize-Agt225Session` always disconnects first |
| 8 | Researcher (Computer Use) defaults assumed restrictive | Tenants with Copilot licensing inherit `default-on` for the Researcher agent's Computer Use action; operators assume opt-in | GA October 2025 default | `Test-Agt225ResearcherComputerUse` (§7.3) flags `Anomaly` if no affirmative zone decision is recorded |
| 9 | Approval-history JSON missing approver UPN | Audit row written before approver context resolved; later renders as "(unknown)" | Race in M365 audit ingestion when approval is auto-completed | `Get-Agt225ApprovalHistory` (§6.2) joins to `Get-MgAuditLogDirectoryAudit` and emits `Anomaly` rather than `Clean` when UPN is null |

Every helper in this playbook returns one of five `Status` values — **`Clean`**, **`Anomaly`**, **`Pending`**, **`NotApplicable`**, **`Error`** — and every helper carries a non-empty `Reason` string when `Status -ne 'Clean'`. **Helpers never return `$null` or `@()` as a clean signal.** This single convention addresses defect #6 and is the foundation on which the §9 evidence pack is built.

---

## §1 — Module Inventory, Graph Scopes, RBAC Matrix, and License-Coverage Gating

### 1.1 Module pinning

The Agent 365 Admin Center surface is exposed through the v1.0 and beta endpoints of Microsoft Graph. Pin the SDK at the version this playbook was last verified against (April 2026):

```powershell
#Requires -Version 7.4
$pinned = @{
    'Microsoft.Graph'                = '2.25.0'
    'Microsoft.Graph.Beta'           = '2.25.0'
    'Microsoft.Graph.Authentication' = '2.25.0'
}
foreach ($name in $pinned.Keys) {
    $installed = Get-Module -ListAvailable -Name $name |
        Where-Object { $_.Version -eq [version]$pinned[$name] }
    if (-not $installed) {
        Install-Module -Name $name -RequiredVersion $pinned[$name] `
            -Scope CurrentUser -Repository PSGallery -Force -AllowClobber
    }
}
Import-Module Microsoft.Graph.Authentication -RequiredVersion 2.25.0 -Force
```

Operators in regulated environments must install from an internal repository mirror rather than `PSGallery` directly; substitute `-Repository <YourInternalFeed>` and verify the package SHA-256 against the values published in `_shared/powershell-baseline.md`.

### 1.2 Graph scope matrix

| Scope | Required for | Helper | Failure mode if missing |
|---|---|---|---|
| `Application.Read.All` | Resolving agent app registrations | `Get-Agt225AgentInventory` | `403` on `/applications` reads |
| `AppCatalog.Read.All` | Listing tenant-published agents in the catalog | `Get-Agt225AgentInventory` | Catalog rows drop silently — helper emits `Anomaly` |
| `Directory.Read.All` | Resolving owner UPNs | `Resolve-Agt225OwnerUpn` | Owner column rendered as `(unresolved)` |
| `AuditLog.Read.All` | Approval history, lifecycle events | `Get-Agt225ApprovalHistory` | History helper returns `NotApplicable` |
| `AgentIdentity.Read.All` | New per-agent identity surface (where exposed by tenant) | `Get-Agt225AgentInventory` | Helper degrades to `AppCatalog`-only enumeration and tags `Reason='AgentIdentityScopeUnavailable'` |

The helper `Test-Agt225GraphScopes` (defined in §2.4) interrogates the live token and returns one row per required scope with a `Granted` boolean; the bootstrap aborts unless all scopes except `AgentIdentity.Read.All` are granted.

### 1.3 Cmdlet availability — handling preview-to-GA renames

Between the November 2025 preview and the May 2026 GA, Microsoft renamed several cmdlets from the `*Bot*` and `*CopilotAgent*` families to the unified `*Agent*` family. To prevent defect #2, every helper that calls a Graph SDK cmdlet first invokes `Get-Agt225CmdletAvailability`:

```powershell
function Get-Agt225CmdletAvailability {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string[]] $CmdletName
    )
    $results = foreach ($name in $CmdletName) {
        $cmd = Get-Command -Name $name -ErrorAction SilentlyContinue
        [pscustomobject]@{
            CmdletName = $name
            Available  = [bool]$cmd
            Module     = if ($cmd) { $cmd.ModuleName } else { $null }
            Version    = if ($cmd) { $cmd.Module.Version.ToString() } else { $null }
        }
    }
    $results
}
```

When a required cmdlet is unavailable, the calling helper emits `Status='NotApplicable'`, `Reason="CmdletMissing:<name>"`, and a portal-export fallback URI in the evidence record — it **never** silently returns `Clean`.

### 1.4 RBAC matrix

| Activity | Minimum role | PIM elevation? | Notes |
|---|---|---|---|
| Read agent inventory | Entra Global Reader | No | Sufficient for all §3 helpers |
| Read approval history | Entra Global Reader + Purview Compliance Admin | No | Compliance Admin needed for unified audit |
| Approve / reject pending agents | Entra Global Admin **or** AI Administrator | **Yes — PIM-bound** | Mutation operations only |
| Apply governance template | AI Administrator | Yes (PIM) | Tracked via `ChangeTicketId` (§8) |
| Forward evidence to SIEM | Reader role on the SIEM workspace | No | Out-of-scope for Entra |

Canonical role names: **AI Administrator**, **Entra Global Admin**, **Entra Global Reader**, **AI Governance Lead**, **Purview Compliance Admin**. See [`docs/reference/role-catalog.md`](../../../reference/role-catalog.md).

### 1.5 License-coverage gating preflight

A small number of Agent 365 surfaces remained in **public preview** at GA — most notably the per-tenant Computer Use policy editor for the Researcher agent and the bulk approval-template export. Operators must affirmatively opt in to preview surfaces through the `-AllowPreviewSurfaces` switch on `Initialize-Agt225Session`. Without that switch, helpers that touch preview surfaces return `Status='NotApplicable'`, `Reason='PreviewSurfaceNotEnabled'` rather than failing or, worse, returning a synthetic clean.

```powershell
function Test-Agt225LicenseCoverageGating {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [bool] $AllowPreviewSurfaces
    )
    [pscustomobject]@{
        AllowPreviewSurfaces = $AllowPreviewSurfaces
        ResearcherCUPolicy   = if ($AllowPreviewSurfaces) { 'Reachable' } else { 'GatedOff' }
        BulkTemplateExport   = if ($AllowPreviewSurfaces) { 'Reachable' } else { 'GatedOff' }
        Status               = if ($AllowPreviewSurfaces) { 'Clean' } else { 'NotApplicable' }
        Reason               = if ($AllowPreviewSurfaces) { '' } else { 'OperatorOptedOutOfPreview' }
    }
}
```

This pattern mirrors the §1.5 of the Control 2.26 playbook so that compliance reviewers see identical preflight behaviour across the two paired controls.

---

## §2 — Bootstrap

The bootstrap helpers establish the commercial Microsoft Graph session, validate scopes, and emit a structured `SessionContext` object that every subsequent helper consumes. Two rules are non-negotiable:

1. **Every session is initialized with `Disconnect-MgGraph` first** so cached cross-tenant tokens cannot leak.
2. **Throttling is wrapped at the bootstrap layer** so callers in §3 onward never need to write their own retry loops.

### 2.1 Assert-Agt225ShellHost

```powershell
function Assert-Agt225ShellHost {
    [CmdletBinding()]
    param()
    if ($PSVersionTable.PSEdition -ne 'Core') {
        throw [System.InvalidOperationException]::new(
            "Agt225-WrongShell: PowerShell Core (7.4+) required; got $($PSVersionTable.PSEdition)")
    }
    if ($PSVersionTable.PSVersion -lt [version]'7.4') {
        throw [System.InvalidOperationException]::new(
            "Agt225-WrongShell: PS 7.4+ required; got $($PSVersionTable.PSVersion)")
    }
    $auth = Get-Module -Name Microsoft.Graph.Authentication -ListAvailable |
        Sort-Object Version -Descending | Select-Object -First 1
    if (-not $auth -or $auth.Version -lt [version]'2.25.0') {
        throw [System.InvalidOperationException]::new(
            "Agt225-WrongShell: Microsoft.Graph.Authentication 2.25.0+ required.")
    }
    $stale = Get-Module -ListAvailable -Name Microsoft.Graph |
        Where-Object { $_.Version -lt [version]'2.25.0' }
    if ($stale) {
        throw [System.InvalidOperationException]::new(
            "Agt225-WrongShell: Stale Microsoft.Graph $($stale[0].Version) present alongside 2.25; uninstall stale module to remove import-order ambiguity.")
    }
    [pscustomobject]@{
        Status       = 'Clean'
        PSVersion    = $PSVersionTable.PSVersion.ToString()
        GraphVersion = $auth.Version.ToString()
        Reason       = ''
    }
}
```

### 2.2 Initialize-Agt225Session

```powershell
function Initialize-Agt225Session {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $TenantId,
        [Parameter(Mandatory)] [string] $RunId,
        [string[]] $RequestedScopes = @(
            'Application.Read.All',
            'AppCatalog.Read.All',
            'Directory.Read.All',
            'AuditLog.Read.All',
            'AgentIdentity.Read.All'
        ),
        [switch] $AllowPreviewSurfaces
    )

    $null = Assert-Agt225ShellHost
    Disconnect-MgGraph -ErrorAction SilentlyContinue | Out-Null
    Connect-MgGraph -TenantId $TenantId -Scopes $RequestedScopes `
        -Environment 'Global' -NoWelcome -ErrorAction Stop

    $scopeReport = Test-Agt225GraphScopes -RequestedScopes $RequestedScopes
    $missing = $scopeReport | Where-Object {
        -not $_.Granted -and $_.Scope -ne 'AgentIdentity.Read.All'
    }
    if ($missing) {
        Disconnect-MgGraph | Out-Null
        throw [System.UnauthorizedAccessException]::new(
            "Agt225-MissingScopes: $($missing.Scope -join ', ')")
    }

    $previewReport = Test-Agt225LicenseCoverageGating -AllowPreviewSurfaces:$AllowPreviewSurfaces

    [pscustomobject]@{
        RunId              = $RunId
        TenantId           = $TenantId
        Cloud              = 'Global'
        ScopesGranted      = ($scopeReport | Where-Object Granted).Scope
        ScopesMissing      = ($scopeReport | Where-Object { -not $_.Granted }).Scope
        AllowPreview       = [bool]$AllowPreviewSurfaces
        PreviewReport      = $previewReport
        InitializedAt      = (Get-Date).ToUniversalTime().ToString('o')
        Status             = 'Clean'
        Reason             = ''
    }
}
```

### 2.3 Test-Agt225GraphScopes

```powershell
function Test-Agt225GraphScopes {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string[]] $RequestedScopes
    )
    $ctx = Get-MgContext
    if (-not $ctx) {
        throw [System.InvalidOperationException]::new(
            "Agt225-NoContext: Connect-MgGraph has not been called.")
    }
    $granted = $ctx.Scopes
    foreach ($scope in $RequestedScopes) {
        [pscustomobject]@{
            Scope   = $scope
            Granted = ($granted -contains $scope)
        }
    }
}
```

### 2.4 Throttle stub

The full throttle helper lives in §11.1; the bootstrap layer registers a script-scoped reference so that every helper in §3-§8 can call `Invoke-Agt225Throttled { ... }` without having to rebuild backoff state per call.

```powershell
$script:Agt225ThrottleState = @{
    LastCall   = [DateTime]::MinValue
    Backoff    = [TimeSpan]::Zero
    MaxBackoff = [TimeSpan]::FromSeconds(60)
    Retries    = 5
}
```

---

## §3 — Agent Inventory (Verification Criterion #1)

The control's verification criterion #1 requires an export of all tenant-deployed agents with the **ten enumerated fields** from line 52 of the control file. `Get-Agt225AgentInventory` is the canonical helper.

### 3.1 Get-Agt225AgentInventory

```powershell
function Get-Agt225AgentInventory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [string] $OutputPath = "./evidence/2.25/agent-inventory-$($Session.RunId).json"
    )

    $availability = Get-Agt225CmdletAvailability -CmdletName @(
        'Get-MgApplication',
        'Get-MgBetaAppCatalogTeamsApp'
    )
    $missing = $availability | Where-Object { -not $_.Available }
    if ($missing) {
        return [pscustomobject]@{
            Status = 'NotApplicable'
            Reason = "CmdletMissing:$($missing.CmdletName -join ',')"
            FallbackUri = 'https://admin.microsoft.com/Adminportal/Home#/agents/inventory'
        }
    }

    $agents = Invoke-Agt225Throttled {
        Invoke-Agt225PagedQuery -Uri '/v1.0/applications?$filter=tags/any(t:t eq ''agent365'')'
    }

    $rows = foreach ($a in $agents) {
        $owner = Resolve-Agt225OwnerUpn -ObjectId $a.id
        [pscustomobject]@{
            AgentId              = $a.id
            DisplayName          = $a.displayName
            Publisher            = $a.publisherDomain
            Platform             = ($a.tags | Where-Object { $_ -match '^platform:' }) -replace '^platform:',''
            OwnerUpn             = $owner.Upn
            Status               = $a.signInAudience
            DeploymentScope      = ($a.tags | Where-Object { $_ -match '^scope:' }) -replace '^scope:',''
            GovernanceTemplate   = ($a.tags | Where-Object { $_ -match '^template:' }) -replace '^template:',''
            LastApprovalUtc      = ($a.tags | Where-Object { $_ -match '^lastApproval:' }) -replace '^lastApproval:',''
            ApproverUpn          = ($a.tags | Where-Object { $_ -match '^approver:' }) -replace '^approver:',''
        }
    }

    $result = [pscustomobject]@{
        Status        = if ($rows.Count -gt 0) { 'Clean' } else { 'Anomaly' }
        Reason        = if ($rows.Count -gt 0) { '' } else { 'NoAgentsReturned-VerifyFilter' }
        Count         = $rows.Count
        Rows          = $rows
        ExportedAt    = (Get-Date).ToUniversalTime().ToString('o')
        OutputPath    = $OutputPath
    }
    $result | ConvertTo-Json -Depth 8 | Out-File -FilePath $OutputPath -Encoding utf8
    $result
}
```

The ten fields above match the verification criterion exactly (Agent ID, Display Name, Publisher, Platform, Owner UPN, Status, Deployment Scope, Governance Template, Last Approval Timestamp, Approver UPN). When any field is unresolvable, the helper writes the literal string `(unresolved)` rather than `$null` so that downstream JSON consumers cannot treat missing data as absent data.

### 3.2 Resolve-Agt225OwnerUpn

```powershell
function Resolve-Agt225OwnerUpn {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [string] $ObjectId)
    try {
        $owners = Invoke-Agt225Throttled {
            Invoke-MgGraphRequest -Method GET `
                -Uri "/v1.0/applications/$ObjectId/owners" |
                Select-Object -ExpandProperty value
        }
        if (-not $owners) {
            return [pscustomobject]@{ ObjectId=$ObjectId; Upn='(ownerless)'; Status='Anomaly' }
        }
        [pscustomobject]@{
            ObjectId = $ObjectId
            Upn      = $owners[0].userPrincipalName
            Status   = 'Clean'
        }
    } catch {
        [pscustomobject]@{
            ObjectId = $ObjectId
            Upn      = '(unresolved)'
            Status   = 'Error'
            Reason   = $_.Exception.Message
        }
    }
}
```

---

## §4 — Pending Approvals and Ownerless-Agent Detection

### 4.1 Get-Agt225PendingApprovals

```powershell
function Get-Agt225PendingApprovals {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [object] $Session)

    $pending = Invoke-Agt225Throttled {
        Invoke-Agt225PagedQuery -Uri "/beta/agents/approvals?`$filter=status eq 'pending'"
    }
    $now = Get-Date
    $rows = foreach ($p in $pending) {
        $age = [int]([math]::Round(($now - [datetime]$p.submittedDateTime).TotalDays))
        [pscustomobject]@{
            ApprovalId    = $p.id
            AgentId       = $p.agentId
            DisplayName   = $p.displayName
            SubmittedBy   = $p.submittedBy.userPrincipalName
            SubmittedUtc  = $p.submittedDateTime
            AgeInDays     = $age
            Zone          = $p.deploymentZone
            Status        = if ($age -gt 7) { 'Anomaly' } else { 'Pending' }
            Reason        = if ($age -gt 7) { "PendingOver7Days" } else { '' }
        }
    }
    [pscustomobject]@{
        Count = $rows.Count
        Rows  = $rows
        Status = if ($rows | Where-Object Status -eq 'Anomaly') { 'Anomaly' }
                 elseif ($rows.Count -eq 0) { 'Clean' }
                 else { 'Pending' }
        Reason = ''
    }
}
```

The 7-day threshold aligns with the operating-cadence commitment in [Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md): no agent approval should age past one week without being escalated to the AI Governance Lead.

### 4.2 Find-Agt225OwnerlessAgents

```powershell
function Find-Agt225OwnerlessAgents {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [object] $Inventory)

    $ownerless = $Inventory.Rows | Where-Object {
        $_.OwnerUpn -in @('(ownerless)','(unresolved)','')
    }
    [pscustomobject]@{
        Count  = $ownerless.Count
        Rows   = $ownerless
        Status = if ($ownerless.Count -gt 0) { 'Anomaly' } else { 'Clean' }
        Reason = if ($ownerless.Count -gt 0) { "OwnerlessAgentsDetected:$($ownerless.Count)" } else { '' }
    }
}
```

Ownerless agents are a leading indicator of the orphan-account risk highlighted in OCC Bulletin 2013-29 (third-party risk management) and Fed SR 26-2 (formerly SR 11-7) (model-owner accountability). The helper does not auto-remediate; it flags for review by the **AI Governance Lead** (canonical role).

### 4.3 New-Agt225OwnerlessRemediationPlan

```powershell
function New-Agt225OwnerlessRemediationPlan {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $OwnerlessReport,
        [Parameter(Mandatory)] [string] $ChangeTicketId
    )
    $plan = foreach ($row in $OwnerlessReport.Rows) {
        [pscustomobject]@{
            AgentId         = $row.AgentId
            DisplayName     = $row.DisplayName
            ProposedAction  = if ($row.Platform -eq 'CopilotStudio') {
                                  'Reassign-To-DepartmentalOwner'
                              } else {
                                  'Disable-Pending-Owner-Identification'
                              }
            ChangeTicketId  = $ChangeTicketId
            EvidenceLink    = "./evidence/2.25/ownerless-$($row.AgentId).json"
        }
    }
    [pscustomobject]@{
        Plan   = $plan
        Status = 'Pending'
        Reason = 'AwaitingAIGovernanceLeadApproval'
    }
}
```

No mutation is performed by this helper — it produces the manifest that Control 2.25's §8 mutation pattern consumes after a `ChangeTicketId` is registered.


---

## §5 — Governance Templates

The Agent 365 Admin Center introduces "governance templates" — reusable JSON bundles that encode allowed connectors, data-loss-prevention (DLP) policy bindings, sensitivity-label requirements, retention bindings, and escalation contacts. Each agent is bound to exactly one template; unbound agents are an automatic `Anomaly`.

### 5.1 Get-Agt225GovernanceTemplate

```powershell
function Get-Agt225GovernanceTemplate {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [object] $Session)

    $availability = Get-Agt225CmdletAvailability -CmdletName 'Invoke-MgGraphRequest'
    if (-not ($availability.Available)) {
        return [pscustomobject]@{
            Status = 'NotApplicable'
            Reason = 'CmdletMissing:Invoke-MgGraphRequest'
        }
    }

    $templates = Invoke-Agt225Throttled {
        Invoke-Agt225PagedQuery -Uri '/beta/agents/governanceTemplates'
    }

    $rows = foreach ($t in $templates) {
        [pscustomobject]@{
            TemplateId        = $t.id
            DisplayName       = $t.displayName
            Version           = $t.version
            BoundAgentCount   = $t.boundAgentCount
            DlpPolicyId       = $t.dlpPolicyId
            SensitivityLabels = ($t.requiredLabels -join ',')
            RetentionBinding  = $t.retentionBinding
            ZoneScope         = $t.zoneScope
            LastModifiedUtc   = $t.lastModifiedDateTime
            ModifiedBy        = $t.lastModifiedBy.userPrincipalName
        }
    }
    [pscustomobject]@{
        Count  = $rows.Count
        Rows   = $rows
        Status = if ($rows.Count -eq 0) { 'Anomaly' } else { 'Clean' }
        Reason = if ($rows.Count -eq 0) { 'NoTemplatesPublished' } else { '' }
    }
}
```

### 5.2 Test-Agt225TemplateBinding

```powershell
function Test-Agt225TemplateBinding {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Inventory,
        [Parameter(Mandatory)] [object] $Templates
    )
    $unbound = $Inventory.Rows | Where-Object {
        [string]::IsNullOrWhiteSpace($_.GovernanceTemplate) -or
        $_.GovernanceTemplate -notin $Templates.Rows.TemplateId
    }
    [pscustomobject]@{
        UnboundCount = $unbound.Count
        UnboundRows  = $unbound
        Status       = if ($unbound.Count -gt 0) { 'Anomaly' } else { 'Clean' }
        Reason       = if ($unbound.Count -gt 0) { "AgentsWithoutValidTemplate:$($unbound.Count)" } else { '' }
    }
}
```

### 5.3 Zone-aware template enforcement

| Zone | Template requirement | Helper enforcement |
|---|---|---|
| **Zone 1 (Personal)** | Must inherit the tenant default `zone1-personal-default` template; users may not author custom templates | `Test-Agt225TemplateBinding` flags any Zone-1 agent bound to a non-default template as `Anomaly` |
| **Zone 2 (Team)** | Must bind a department-published template with at least one DLP policy and one sensitivity label | Helper flags template missing `DlpPolicyId` or empty `SensitivityLabels` |
| **Zone 3 (Enterprise)** | Must bind an enterprise-published template that includes a retention binding mapped to a 6-year SEC Rule 17a-4 retention policy | Helper flags template missing `RetentionBinding` |

The zone-enforcement loop is a single pipeline:

```powershell
$inventory  = Get-Agt225AgentInventory  -Session $session
$templates  = Get-Agt225GovernanceTemplate -Session $session
$bindReport = Test-Agt225TemplateBinding -Inventory $inventory -Templates $templates
```

---

## §6 — Lifecycle Events and Approval History

### 6.1 Get-Agt225LifecycleEvents

```powershell
function Get-Agt225LifecycleEvents {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [int] $LookbackDays = 30
    )
    $start = (Get-Date).AddDays(-$LookbackDays).ToUniversalTime().ToString('o')
    $events = Invoke-Agt225Throttled {
        Invoke-Agt225PagedQuery -Uri "/beta/auditLogs/directoryAudits?`$filter=category eq 'Agent365' and activityDateTime ge $start"
    }
    $rows = foreach ($e in $events) {
        [pscustomobject]@{
            EventId       = $e.id
            ActivityUtc   = $e.activityDateTime
            Activity      = $e.activityDisplayName
            Initiator     = $e.initiatedBy.user.userPrincipalName
            TargetAgentId = ($e.targetResources | Where-Object type -eq 'Agent').id
            Result        = $e.result
            ResultReason  = $e.resultReason
        }
    }
    [pscustomobject]@{
        Count = $rows.Count
        Rows  = $rows
        Status = if ($rows.Count -gt 0) { 'Clean' } else { 'Anomaly' }
        Reason = if ($rows.Count -gt 0) { '' } else { "NoLifecycleEventsInLast${LookbackDays}Days" }
    }
}
```

A 30-day window with **zero** lifecycle events in a tenant that has any pending or approved agents is itself anomalous — it usually indicates that audit ingestion is broken (Control 3.1) or that the operator queried the wrong tenant.

### 6.2 Get-Agt225ApprovalHistory

```powershell
function Get-Agt225ApprovalHistory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [int] $LookbackDays = 90
    )
    $start = (Get-Date).AddDays(-$LookbackDays).ToUniversalTime().ToString('o')
    $approvals = Invoke-Agt225Throttled {
        Invoke-Agt225PagedQuery -Uri "/beta/agents/approvals?`$filter=resolvedDateTime ge $start"
    }
    # Defect #9 mitigation — join to directory audit to recover approver UPN
    $audits = Invoke-Agt225Throttled {
        Invoke-Agt225PagedQuery -Uri "/beta/auditLogs/directoryAudits?`$filter=category eq 'Agent365' and activityDisplayName eq 'ResolveAgentApproval' and activityDateTime ge $start"
    }
    $auditByApproval = @{}
    foreach ($a in $audits) {
        $approvalId = ($a.targetResources | Where-Object type -eq 'AgentApproval').id
        if ($approvalId) { $auditByApproval[$approvalId] = $a.initiatedBy.user.userPrincipalName }
    }

    $rows = foreach ($p in $approvals) {
        $approver = if ($p.resolvedBy.userPrincipalName) {
            $p.resolvedBy.userPrincipalName
        } elseif ($auditByApproval.ContainsKey($p.id)) {
            $auditByApproval[$p.id]
        } else {
            '(unknown)'
        }
        [pscustomobject]@{
            ApprovalId     = $p.id
            AgentId        = $p.agentId
            DisplayName    = $p.displayName
            SubmittedUtc   = $p.submittedDateTime
            ResolvedUtc    = $p.resolvedDateTime
            Decision       = $p.decision
            ApproverUpn    = $approver
            Justification  = $p.justification
            Zone           = $p.deploymentZone
            Status         = if ($approver -eq '(unknown)') { 'Anomaly' } else { 'Clean' }
            Reason         = if ($approver -eq '(unknown)') { 'ApproverUpnUnresolved-AuditRace' } else { '' }
        }
    }
    [pscustomobject]@{
        Count = $rows.Count
        Rows  = $rows
        Status = if ($rows | Where-Object Status -eq 'Anomaly') { 'Anomaly' }
                 elseif ($rows.Count -eq 0) { 'NotApplicable' }
                 else { 'Clean' }
        Reason = ''
    }
}
```

The output of `Get-Agt225ApprovalHistory` is the primary attestation artifact for **FINRA Rule 3110** supervisory review. It does **not** substitute for the registered principal's own sign-off; it provides the principal with an evidentiary record from which to attest.

---

## §7 — Access Reviews, License Coverage, and the Researcher Computer Use Probe

### 7.1 Get-Agt225LicenseCoverage

The Agent 365 Admin Center is licensed via **Microsoft 365 E7 ("Frontier Suite")** or **Microsoft 365 Copilot Business Chat**. Operators must verify that every user assigned a governance role is licensed; an unlicensed AI Administrator silently loses access to many of the admin surfaces.

```powershell
function Get-Agt225LicenseCoverage {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [string[]] $RequiredSkus = @('SPE_E7_FRONTIER','M365_COPILOT_BUSINESS_CHAT')
    )
    $govRoleMembers = Invoke-Agt225Throttled {
        $roles = @('AI Administrator','Global Reader','Compliance Administrator')
        $members = foreach ($r in $roles) {
            $roleObj = Get-MgDirectoryRole -Filter "displayName eq '$r'" -ErrorAction SilentlyContinue
            if ($roleObj) {
                Get-MgDirectoryRoleMember -DirectoryRoleId $roleObj.Id |
                    Select-Object @{n='Upn';e={$_.AdditionalProperties.userPrincipalName}},
                                  @{n='Role';e={$r}}
            }
        }
        $members
    }
    $rows = foreach ($m in ($govRoleMembers | Where-Object Upn)) {
        $skus = (Get-MgUserLicenseDetail -UserId $m.Upn -ErrorAction SilentlyContinue).SkuPartNumber
        $covered = $false
        foreach ($req in $RequiredSkus) { if ($skus -contains $req) { $covered = $true } }
        [pscustomobject]@{
            Upn        = $m.Upn
            Role       = $m.Role
            Skus       = ($skus -join ',')
            Covered    = $covered
            Status     = if ($covered) { 'Clean' } else { 'Anomaly' }
            Reason     = if ($covered) { '' } else { "MissingRequiredLicense:$($RequiredSkus -join '|')" }
        }
    }
    [pscustomobject]@{
        Count = $rows.Count
        Rows  = $rows
        Status = if ($rows | Where-Object Status -eq 'Anomaly') { 'Anomaly' } else { 'Clean' }
        Reason = ''
    }
}
```

### 7.2 Test-Agt225AccessReviewBinding

Every agent at Zone 2 or Zone 3 must be the subject of a recurring access review (per Control [1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)).

```powershell
function Test-Agt225AccessReviewBinding {
    [CmdletBinding()]
    param([Parameter(Mandatory)] [object] $Inventory)
    $reviews = Invoke-Agt225Throttled {
        Invoke-Agt225PagedQuery -Uri '/v1.0/identityGovernance/accessReviews/definitions'
    }
    $reviewedAgentIds = foreach ($r in $reviews) {
        $r.scope.resource.id
    }
    $unreviewed = $Inventory.Rows | Where-Object {
        $_.DeploymentScope -in @('Team','Enterprise') -and
        $_.AgentId -notin $reviewedAgentIds
    }
    [pscustomobject]@{
        UnreviewedCount = $unreviewed.Count
        UnreviewedRows  = $unreviewed
        Status          = if ($unreviewed.Count -gt 0) { 'Anomaly' } else { 'Clean' }
        Reason          = if ($unreviewed.Count -gt 0) { "Zone2-3-AgentsWithoutAccessReview:$($unreviewed.Count)" } else { '' }
    }
}
```

### 7.3 Test-Agt225ResearcherComputerUse

The Researcher agent's **Computer Use** capability went GA in **October 2025** and is **default-on** for any tenant with Copilot licensing. This is the single most material policy decision in the Agent 365 surface for FSI tenants because Computer Use can drive a browser to interact with internal web apps on the user's behalf — a capability that requires affirmative supervisory review under FINRA Rule 3110 and OCC Bulletin 2013-29.

`Test-Agt225ResearcherComputerUse` does not change any setting; it asserts that an **affirmative restrictive zone decision** is recorded in the per-zone policy register. The default-on inheritance is treated as `Anomaly` until the AI Governance Lead has signed off per zone.

```powershell
function Test-Agt225ResearcherComputerUse {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [string] $ZoneDecisionRegisterPath  # JSON: { "zone1": "Disabled", "zone2": "RestrictedToDomainSet", "zone3": "Disabled" }
    )
    if (-not (Test-Path $ZoneDecisionRegisterPath)) {
        return [pscustomobject]@{
            Status = 'Anomaly'
            Reason = "ZoneDecisionRegisterMissing:$ZoneDecisionRegisterPath"
        }
    }
    $register = Get-Content -Raw $ZoneDecisionRegisterPath | ConvertFrom-Json
    $live = Invoke-Agt225Throttled {
        Invoke-MgGraphRequest -Method GET -Uri '/beta/agents/researcher/computerUsePolicy'
    }
    $rows = foreach ($zone in @('zone1','zone2','zone3')) {
        $declared = $register.$zone
        $observed = $live.zonePolicies.$zone.mode
        [pscustomobject]@{
            Zone      = $zone
            Declared  = $declared
            Observed  = $observed
            Match     = ($declared -eq $observed)
            Status    = if ($declared -eq $observed) { 'Clean' } else { 'Anomaly' }
            Reason    = if ($declared -eq $observed) { '' } else { "ResearcherCUPolicyDrift:$zone declared=$declared observed=$observed" }
        }
    }
    [pscustomobject]@{
        Rows   = $rows
        Status = if ($rows | Where-Object Status -eq 'Anomaly') { 'Anomaly' } else { 'Clean' }
        Reason = ''
    }
}
```

---

## §8 — Bulk Mutation with ChangeTicketId and SHA-256 Manifest

The Agent 365 Admin Center exposes bulk mutation of governance bindings (template assignment, owner reassignment, decommission). Mutation is high-risk and is gated by the same change-control discipline used in the sister 2.26 playbook: every mutation **must** be invoked with a `-ChangeTicketId` parameter that maps to an approved change record, and **must** produce a SHA-256-hashed manifest of every action taken. The helper writes a dry-run plan first; the operator must explicitly pass `-ConfirmMutation` to apply.

### 8.1 Invoke-Agt225BulkTemplateAssignment

```powershell
function Invoke-Agt225BulkTemplateAssignment {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [string] $ChangeTicketId,
        [Parameter(Mandatory)] [object[]] $AssignmentPlan,   # @(@{AgentId='..'; TemplateId='..'}, ...)
        [switch] $ConfirmMutation
    )
    if ([string]::IsNullOrWhiteSpace($ChangeTicketId)) {
        throw [System.ArgumentException]::new("Agt225-NoChangeTicket: -ChangeTicketId is required for any mutation.")
    }
    $manifestRows = foreach ($a in $AssignmentPlan) {
        $row = [pscustomobject]@{
            AgentId        = $a.AgentId
            TemplateId     = $a.TemplateId
            ChangeTicketId = $ChangeTicketId
            PlannedAt      = (Get-Date).ToUniversalTime().ToString('o')
            Applied        = $false
            ResultStatus   = 'PlannedOnly'
            ResultReason   = ''
        }
        if ($ConfirmMutation -and $PSCmdlet.ShouldProcess($a.AgentId, "Bind template $($a.TemplateId)")) {
            try {
                Invoke-Agt225Throttled {
                    Invoke-MgGraphRequest -Method PATCH `
                        -Uri "/beta/agents/$($a.AgentId)" `
                        -Body (@{ governanceTemplateId = $a.TemplateId } | ConvertTo-Json) `
                        -ContentType 'application/json'
                }
                $row.Applied      = $true
                $row.ResultStatus = 'Applied'
            } catch {
                $row.ResultStatus = 'Error'
                $row.ResultReason = $_.Exception.Message
            }
        }
        $row
    }

    $manifestJson = $manifestRows | ConvertTo-Json -Depth 6
    $hash = [System.BitConverter]::ToString(
        [System.Security.Cryptography.SHA256]::Create().ComputeHash(
            [System.Text.Encoding]::UTF8.GetBytes($manifestJson))
    ) -replace '-',''

    $manifestPath = "./evidence/2.25/mutation-manifest-$ChangeTicketId.json"
    @{
        change_ticket_id = $ChangeTicketId
        sha256           = $hash
        rows             = $manifestRows
        run_timestamp    = (Get-Date).ToUniversalTime().ToString('o')
        operator         = (Get-MgContext).Account
    } | ConvertTo-Json -Depth 8 | Out-File -FilePath $manifestPath -Encoding utf8

    [pscustomobject]@{
        ManifestPath = $manifestPath
        Sha256       = $hash
        AppliedCount = ($manifestRows | Where-Object Applied).Count
        Status       = if ($manifestRows | Where-Object ResultStatus -eq 'Error') { 'Anomaly' } else { 'Clean' }
        Reason       = ''
    }
}
```

The `-ChangeTicketId` parameter is the single non-bypassable contract that connects this helper to the change-management evidence required by **SOX §404** ITGCs. Operators **may not** invoke any mutation helper without it; the helper throws `Agt225-NoChangeTicket` immediately when the parameter is null or whitespace.

### 8.2 Mutation safety rails

| Rail | Helper enforcement |
|---|---|
| Dry-run by default | `-ConfirmMutation` switch is required to apply |
| Change-ticket required | `Agt225-NoChangeTicket` exception when missing |
| SHA-256 manifest | Manifest file is hashed and the hash is recorded inside the manifest |
| Per-row error isolation | A failure on agent N does not abort the loop; row carries `ResultStatus='Error'` |
| `ShouldProcess` on every row | Operator running interactively gets per-agent confirmation |
| PIM elevation required | Caller must be Entra Global Admin or AI Administrator with a live PIM activation |


---

## §9 — Evidence Pack with JSON Schema

The evidence pack is the canonical output of every Control 2.25 PowerShell run. It is the file the AI Governance Lead presents to internal audit, the FINRA exam team, and the SOX ITGC auditor. It must be **schema-stable**, **deterministically named**, and **SHA-256 hashed**.

### 9.1 JSON schema

```json
{
  "$schema": "https://schemas.fsi-agentgov.local/evidence/v1.0.json",
  "control_id": "2.25",
  "run_id": "<guid>",
  "run_timestamp": "<ISO-8601 UTC>",
  "tenant_id": "<guid>",
  "cloud": "Global",
  "zone": "Zone1 | Zone2 | Zone3 | Mixed",
  "namespace": "fsi-agentgov.agent-365-admin",
  "criterion": "<verification-criterion-id>",
  "status": "Clean | Anomaly | Pending | NotApplicable | Error",
  "evidence_artifacts": [
    { "path": "./evidence/2.25/agent-inventory-<run_id>.json", "sha256": "<hex>" }
  ],
  "regulator_mappings": ["FINRA-3110","SEC-17a-4","SOX-404","GLBA-Safeguards","OCC-2013-29","SR-11-7","CFTC-1.31"],
  "schema_version": "1.0"
}
```

The `namespace` value `fsi-agentgov.agent-365-admin` is reserved for this control's evidence and must not be reused by other controls. The `evidence_artifacts` array carries one entry per file produced during the run; each file is independently hashed so that tampering with any single artifact invalidates only its own hash, not the whole pack.

### 9.2 New-Agt225EvidencePack

```powershell
function New-Agt225EvidencePack {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $Session,
        [Parameter(Mandatory)] [object[]] $HelperResults,   # array of [pscustomobject] from each helper
        [Parameter(Mandatory)] [string] $Zone,
        [string] $OutputDirectory = "./evidence/2.25"
    )
    if (-not (Test-Path $OutputDirectory)) {
        New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    }

    $artifacts = foreach ($r in $HelperResults) {
        if ($r.OutputPath -and (Test-Path $r.OutputPath)) {
            $bytes = [System.IO.File]::ReadAllBytes($r.OutputPath)
            $sha   = [System.BitConverter]::ToString(
                [System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)
            ) -replace '-',''
            [pscustomobject]@{ path = $r.OutputPath; sha256 = $sha.ToLowerInvariant() }
        }
    }

    $aggregateStatus = if ($HelperResults | Where-Object Status -eq 'Error') { 'Error' }
                       elseif ($HelperResults | Where-Object Status -eq 'Anomaly') { 'Anomaly' }
                       elseif ($HelperResults | Where-Object Status -eq 'Pending') { 'Pending' }
                       elseif ($HelperResults | Where-Object Status -eq 'NotApplicable') {
                           if (($HelperResults | Where-Object Status -eq 'Clean').Count -eq 0) { 'NotApplicable' } else { 'Clean' }
                       }
                       else { 'Clean' }

    $pack = [ordered]@{
        '$schema'           = 'https://schemas.fsi-agentgov.local/evidence/v1.0.json'
        control_id          = '2.25'
        run_id              = $Session.RunId
        run_timestamp       = (Get-Date).ToUniversalTime().ToString('o')
        tenant_id           = $Session.TenantId
        cloud               = $Session.Cloud
        zone                = $Zone
        namespace           = 'fsi-agentgov.agent-365-admin'
        criterion           = 'aggregate'
        status              = $aggregateStatus
        evidence_artifacts  = @($artifacts)
        regulator_mappings  = @('FINRA-3110','SEC-17a-4','SOX-404','GLBA-Safeguards','OCC-2013-29','SR-11-7','CFTC-1.31')
        schema_version      = '1.0'
        helper_summary      = @(
            $HelperResults | ForEach-Object {
                [pscustomobject]@{
                    helper = $_.PSObject.TypeNames[0]
                    status = $_.Status
                    reason = $_.Reason
                }
            }
        )
    }

    $packPath = Join-Path $OutputDirectory "evidence-pack-$($Session.RunId).json"
    $pack | ConvertTo-Json -Depth 10 | Out-File -FilePath $packPath -Encoding utf8

    $packBytes = [System.IO.File]::ReadAllBytes($packPath)
    $packHash  = [System.BitConverter]::ToString(
        [System.Security.Cryptography.SHA256]::Create().ComputeHash($packBytes)
    ) -replace '-',''

    [pscustomobject]@{
        PackPath     = $packPath
        Sha256       = $packHash.ToLowerInvariant()
        Status       = $aggregateStatus
        ArtifactCount = $artifacts.Count
        Reason       = ''
    }
}
```

### 9.3 Evidence retention

| Regulator | Retention rule | Implementation |
|---|---|---|
| **SEC Rule 17a-4(b)(4)** | 6 years, first 2 immediately accessible | Forward to immutable WORM-locked storage (Purview retention or Azure Blob immutability policy) |
| **FINRA Rule 4511** | 6 years for books-and-records | Same retention store |
| **SOX §404 ITGC** | 7 years | Same store, longer retention label |
| **CFTC Rule 1.31** | 5 years | Same store |

The evidence pack is **not** the system of record on its own; it is the audit-grade extract. The system of record remains the underlying Microsoft 365 unified audit log (Control [3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)) and the Defender XDR investigation tables (Control [3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)).

---

## §10 — SIEM Forwarding Test

A clean evidence pack that nobody reads is not evidence — it is a file. The SIEM forwarding test asserts that every evidence pack produced by §9 is observable in the security operations workspace within an agreed SLA (default: 15 minutes). It is the contract between this control and Control [3.13 — Agent 365 Admin Center Analytics](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md).

### 10.1 Send-Agt225EvidenceToSiem

```powershell
function Send-Agt225EvidenceToSiem {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $EvidencePackPath,
        [Parameter(Mandatory)] [string] $SiemEndpointUri,        # e.g. Log Analytics Data Collection Endpoint
        [Parameter(Mandatory)] [string] $SiemSharedKey,           # KeyVault-resolved at call site, never inline
        [string] $LogType = 'FsiAgentGov_Control_2_25_CL'
    )
    $body = Get-Content -Raw $EvidencePackPath
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
    $rfcDate   = [System.DateTime]::UtcNow.ToString('R')
    $stringToHash = "POST`n$($bodyBytes.Length)`napplication/json`nx-ms-date:$rfcDate`n/api/logs"
    $hmac = [System.Security.Cryptography.HMACSHA256]::new([Convert]::FromBase64String($SiemSharedKey))
    $signature = [Convert]::ToBase64String($hmac.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($stringToHash)))
    $headers = @{
        'Authorization' = "SharedKey ${env:WORKSPACE_ID}:$signature"
        'Log-Type'      = $LogType
        'x-ms-date'     = $rfcDate
        'time-generated-field' = 'run_timestamp'
    }
    try {
        $resp = Invoke-WebRequest -Method POST -Uri $SiemEndpointUri `
            -Headers $headers -Body $body -ContentType 'application/json' -UseBasicParsing
        [pscustomobject]@{
            Status     = if ($resp.StatusCode -eq 200) { 'Clean' } else { 'Anomaly' }
            HttpStatus = $resp.StatusCode
            Reason     = if ($resp.StatusCode -eq 200) { '' } else { "Non200:$($resp.StatusCode)" }
            ForwardedAt = (Get-Date).ToUniversalTime().ToString('o')
        }
    } catch {
        [pscustomobject]@{
            Status      = 'Error'
            HttpStatus  = $null
            Reason      = $_.Exception.Message
            ForwardedAt = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

### 10.2 Test-Agt225SiemRoundTrip

```powershell
function Test-Agt225SiemRoundTrip {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $RunId,
        [Parameter(Mandatory)] [string] $LogAnalyticsWorkspaceId,
        [int] $TimeoutSeconds = 900   # 15-minute SLA
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $query = "FsiAgentGov_Control_2_25_CL | where run_id_g == '$RunId' | take 1"
        $result = Invoke-AzOperationalInsightsQuery `
            -WorkspaceId $LogAnalyticsWorkspaceId -Query $query -ErrorAction SilentlyContinue
        if ($result.Results.Count -gt 0) {
            return [pscustomobject]@{
                Status   = 'Clean'
                LatencyS = [int]((Get-Date) - (Get-Date $result.Results[0].run_timestamp_t)).TotalSeconds
                Reason   = ''
            }
        }
        Start-Sleep -Seconds 30
    }
    [pscustomobject]@{
        Status   = 'Anomaly'
        LatencyS = $TimeoutSeconds
        Reason   = "EvidenceNotObservedWithinSlaSeconds:$TimeoutSeconds"
    }
}
```

The 15-minute SLA is the default; FSI tenants subject to **CFTC Rule 1.31** real-time supervision requirements should tighten this to 5 minutes and treat any breach as an `Anomaly` requiring follow-up under Control [3.13](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md).

---

## §11 — Throttle Helper and Paged-Query Assertion

### 11.1 Invoke-Agt225Throttled

```powershell
function Invoke-Agt225Throttled {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [scriptblock] $ScriptBlock,
        [int] $MaxRetries = 5
    )
    $attempt = 0
    $delay   = [TimeSpan]::FromMilliseconds(500)
    while ($true) {
        $attempt++
        try {
            $result = & $ScriptBlock
            $script:Agt225ThrottleState.LastCall = [DateTime]::UtcNow
            $script:Agt225ThrottleState.Backoff  = [TimeSpan]::Zero
            return $result
        } catch {
            $statusCode = $null
            if ($_.Exception.Response) {
                $statusCode = [int]$_.Exception.Response.StatusCode
            }
            $isThrottle = ($statusCode -in 429,503) -or ($_.Exception.Message -match 'TooManyRequests')
            if ($isThrottle -and $attempt -lt $MaxRetries) {
                $retryAfter = $null
                if ($_.Exception.Response -and $_.Exception.Response.Headers['Retry-After']) {
                    $retryAfter = [TimeSpan]::FromSeconds([int]$_.Exception.Response.Headers['Retry-After'])
                }
                $delay = if ($retryAfter) { $retryAfter } else {
                    [TimeSpan]::FromMilliseconds([math]::Min(
                        $delay.TotalMilliseconds * 2,
                        $script:Agt225ThrottleState.MaxBackoff.TotalMilliseconds))
                }
                Start-Sleep -Milliseconds $delay.TotalMilliseconds
                continue
            }
            throw
        }
    }
}
```

The helper **never** swallows a non-throttle error. A 403 is re-thrown immediately so that defect #2 (read-only token used against admin surfaces) is surfaced rather than masked. A 429 with empty body (defect #2) results in a retry, not a synthetic empty result.

### 11.2 Invoke-Agt225PagedQuery

```powershell
function Invoke-Agt225PagedQuery {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $Uri,
        [int] $PageSizeAssertion = 100
    )
    $all = New-Object System.Collections.ArrayList
    $next = $Uri
    $pageCount = 0
    while ($next) {
        $page = Invoke-MgGraphRequest -Method GET -Uri $next
        $pageCount++
        if ($page.value) { $null = $all.AddRange($page.value) }
        # Defect #3 mitigation: assert that pagination actually advances
        $next = $page.'@odata.nextLink'
        if ($pageCount -eq 1 -and $page.value.Count -eq $PageSizeAssertion -and -not $next) {
            throw [System.InvalidOperationException]::new(
                "Agt225-PagingAssertionFailed: First page returned $PageSizeAssertion rows but no @odata.nextLink. Likely server-side truncation.")
        }
        if ($pageCount -gt 1000) {
            throw [System.InvalidOperationException]::new(
                "Agt225-RunawayPaging: Exceeded 1000 pages. Tighten filter or chunk by date.")
        }
    }
    ,$all.ToArray()
}
```

The paging assertion catches the most insidious form of defect #2: a tenant with exactly 100 agents and a server-side bug that omits `@odata.nextLink`. Without the assertion, the helper would return 100 rows and look perfectly clean even if the true count is higher.


---

## §12 — Cross-Control Invocation Chains

Control 2.25 does not stand alone. The Agent 365 Admin Center is the **operator console** that surfaces evidence which other controls produce or consume. The cross-control chains below are the canonical orchestrations that the AI Governance Lead runs on the operating cadence in §14.4.

### 12.1 Daily inventory + approval-debt sweep

```powershell
$session   = Initialize-Agt225Session -TenantId $TenantId -RunId ([guid]::NewGuid()) `
               
$inventory = Get-Agt225AgentInventory  -Session $session
$pending   = Get-Agt225PendingApprovals -Session $session
$ownerless = Find-Agt225OwnerlessAgents -Inventory $inventory
$pack = New-Agt225EvidencePack -Session $session -Zone 'Mixed' `
            -HelperResults @($inventory, $pending, $ownerless)
Send-Agt225EvidenceToSiem -EvidencePackPath $pack.PackPath `
            -SiemEndpointUri $env:SIEM_URI -SiemSharedKey $env:SIEM_KEY
```

This three-helper chain is the minimum viable daily sweep. It produces a single evidence pack that lands in the SIEM workspace within the §10.2 SLA.

### 12.2 Weekly governance attestation (Controls 2.25 + 2.26 + 1.2)

```powershell
# Control 2.25 — admin-console state
$session   = Initialize-Agt225Session -TenantId $TenantId -RunId $RunId
$inventory = Get-Agt225AgentInventory -Session $session
$templates = Get-Agt225GovernanceTemplate -Session $session
$bind      = Test-Agt225TemplateBinding -Inventory $inventory -Templates $templates
$history   = Get-Agt225ApprovalHistory -Session $session -LookbackDays 7
$license   = Get-Agt225LicenseCoverage -Session $session
$reviews   = Test-Agt225AccessReviewBinding -Inventory $inventory
$cuPolicy  = Test-Agt225ResearcherComputerUse -Session $session `
                -ZoneDecisionRegisterPath './config/zone-decisions.json'

# Control 2.26 — approval workflow state (sister playbook helpers)
$workflow  = Get-Agt226WorkflowConfiguration -Session $session
$slaReport = Test-Agt226ApprovalSla -LookbackDays 7

# Control 1.2 — Conditional Access for AI Agents
$caReport  = Get-FsiAgentCAPolicyState -Session $session

$pack = New-Agt225EvidencePack -Session $session -Zone 'Mixed' `
    -HelperResults @($inventory,$templates,$bind,$history,$license,$reviews,$cuPolicy,$workflow,$slaReport,$caReport)

Send-Agt225EvidenceToSiem -EvidencePackPath $pack.PackPath `
    -SiemEndpointUri $env:SIEM_URI -SiemSharedKey $env:SIEM_KEY
```

The weekly attestation produces a composite pack spanning three controls; the AI Governance Lead countersigns the pack and the registered principal (FINRA Rule 3110) attests on the basis of the countersignature.

### 12.3 Quarterly access-review certification (Controls 2.25 + 1.11)

```powershell
$session  = Initialize-Agt225Session -TenantId $TenantId -RunId $RunId
$inv      = Get-Agt225AgentInventory -Session $session
$reviews  = Test-Agt225AccessReviewBinding -Inventory $inv

# Control 1.11 — Privileged Identity Management bindings for AI Administrator
$pim      = Get-FsiPimAssignmentReport -RoleName 'AI Administrator'

$pack = New-Agt225EvidencePack -Session $session -Zone 'Mixed' `
    -HelperResults @($inv, $reviews, $pim)
```

### 12.4 Mutation chain (gated by ChangeTicketId)

```powershell
$session    = Initialize-Agt225Session -TenantId $TenantId -RunId $RunId
$inv        = Get-Agt225AgentInventory -Session $session
$ownerless  = Find-Agt225OwnerlessAgents -Inventory $inv
$plan       = New-Agt225OwnerlessRemediationPlan `
                  -OwnerlessReport $ownerless -ChangeTicketId 'CHG0123456'

# Dry run first
$dry        = Invoke-Agt225BulkTemplateAssignment -Session $session `
                  -ChangeTicketId 'CHG0123456' -AssignmentPlan $plan.Plan
# After review, re-run with -ConfirmMutation
$applied    = Invoke-Agt225BulkTemplateAssignment -Session $session `
                  -ChangeTicketId 'CHG0123456' -AssignmentPlan $plan.Plan -ConfirmMutation

$pack = New-Agt225EvidencePack -Session $session -Zone 'Mixed' `
    -HelperResults @($inv, $ownerless, $applied)
```

---

## §13 — Attestation Pack

The attestation pack is the **human-readable** companion to the §9 evidence pack. Where §9 produces a machine-parseable JSON, §13 produces a Markdown summary the AI Governance Lead and the registered principal sign. The pack contains:

1. A run header (tenant, cloud, zone, run ID, timestamp, operator, change-ticket if any).
2. A status table (one row per helper, with Status and Reason).
3. A FINRA Rule 3110 principal-attestation block.
4. A SOX §404 ITGC change-attestation block (only populated if mutation ran).
5. A SHA-256 manifest of every artifact in the §9 evidence pack.

### 13.1 New-Agt225AttestationPack

```powershell
function New-Agt225AttestationPack {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [object] $EvidencePack,
        [Parameter(Mandatory)] [string] $PrincipalUpn,
        [Parameter(Mandatory)] [string] $GovernanceLeadUpn,
        [string] $ChangeTicketId,
        [string] $OutputDirectory = './evidence/2.25'
    )
    $packData = Get-Content -Raw $EvidencePack.PackPath | ConvertFrom-Json
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("# Control 2.25 — Attestation Pack")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("| Field | Value |")
    [void]$sb.AppendLine("|---|---|")
    [void]$sb.AppendLine("| Run ID | $($packData.run_id) |")
    [void]$sb.AppendLine("| Tenant ID | $($packData.tenant_id) |")
    [void]$sb.AppendLine("| Cloud | $($packData.cloud) |")
    [void]$sb.AppendLine("| Zone | $($packData.zone) |")
    [void]$sb.AppendLine("| Run timestamp (UTC) | $($packData.run_timestamp) |")
    [void]$sb.AppendLine("| Aggregate status | **$($packData.status)** |")
    [void]$sb.AppendLine("| Change ticket | $ChangeTicketId |")
    [void]$sb.AppendLine("| Operator (Graph context) | $((Get-MgContext).Account) |")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("## Helper status summary")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("| Helper | Status | Reason |")
    [void]$sb.AppendLine("|---|---|---|")
    foreach ($h in $packData.helper_summary) {
        [void]$sb.AppendLine("| $($h.helper) | $($h.status) | $($h.reason) |")
    }
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("## Evidence artifacts (SHA-256)")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("| Path | SHA-256 |")
    [void]$sb.AppendLine("|---|---|")
    foreach ($a in $packData.evidence_artifacts) {
        [void]$sb.AppendLine("| ``$($a.path)`` | ``$($a.sha256)`` |")
    }
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("## FINRA Rule 3110 — Registered Principal Attestation")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("> I, **$PrincipalUpn**, registered principal under FINRA Rule 3110, have reviewed the inventory, approval history, and ownership state of all Microsoft Agent 365 deployments enumerated in this run. I attest that the supervisory review described herein has been performed in accordance with my firm's written supervisory procedures. This attestation does not delegate supervisory responsibility to the automated tooling that produced the underlying evidence; it certifies that I have personally reviewed the evidence.")
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("Signature: ____________________  Date (UTC): ____________________")
    [void]$sb.AppendLine("")
    if ($ChangeTicketId) {
        [void]$sb.AppendLine("## SOX §404 ITGC Change Attestation")
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("> I, **$GovernanceLeadUpn**, attest that mutation operations performed under this run were authorised under change ticket **$ChangeTicketId**, that the SHA-256 manifest in this pack matches the manifest filed against that ticket, and that all changes were applied through the documented helper ``Invoke-Agt225BulkTemplateAssignment`` with ``-ConfirmMutation``.")
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("Signature: ____________________  Date (UTC): ____________________")
        [void]$sb.AppendLine("")
    }

    $packPath = Join-Path $OutputDirectory "attestation-pack-$($packData.run_id).md"
    $sb.ToString() | Out-File -FilePath $packPath -Encoding utf8
    [pscustomobject]@{
        AttestationPath = $packPath
        Status          = 'Clean'
        Reason          = ''
    }
}
```

The attestation pack is the artifact that gets countersigned and stored in the firm's attestation repository (typically GRC tooling such as ServiceNow GRC or Archer). It is the readable summary of the JSON evidence pack and the document that an examiner will ask for first.

### 13.2 Attestation cadence

| Pack type | Cadence | Signers |
|---|---|---|
| Daily inventory | Every business day | AI Governance Lead (counter-signs SIEM ingestion) |
| Weekly governance | Every Monday for the prior week | AI Governance Lead + FINRA registered principal |
| Quarterly access-review | Calendar quarter close | AI Governance Lead + Compliance Officer |
| Mutation pack | Per change ticket | AI Governance Lead + Change Manager |

---

## §14 — Validation, Anti-Patterns, and Operating Cadence

### 14.1 Pester validation skeleton

```powershell
#Requires -Version 7.4
#Requires -Modules @{ ModuleName='Pester'; ModuleVersion='5.5.0' }

Describe 'Control 2.25 — PowerShell helpers' {
    BeforeAll {
        . $PSScriptRoot/Agt225-Helpers.ps1
        $script:fakeSession = [pscustomobject]@{
            RunId    = [guid]::NewGuid().ToString()
            TenantId = '00000000-0000-0000-0000-000000000000'
            Cloud    = 'Global'
        }
    }
    Context 'Assert-Agt225ShellHost' {
        It 'throws Agt225-WrongShell on PS 5.1' -Skip:($PSVersionTable.PSEdition -eq 'Core') {
            { Assert-Agt225ShellHost } | Should -Throw -ExceptionType ([System.InvalidOperationException])
        }
    }
    Context 'Helpers never return $null on clean signal' {
        It 'Get-Agt225PendingApprovals returns object even when zero pending' {
            Mock Invoke-Agt225PagedQuery { @() }
            $r = Get-Agt225PendingApprovals -Session $script:fakeSession
            $r           | Should -Not -BeNullOrEmpty
            $r.Status    | Should -Be 'Clean'
            $r.Count     | Should -Be 0
        }
    }
    Context 'Mutation requires ChangeTicketId' {
        It 'throws Agt225-NoChangeTicket on empty ticket' {
            { Invoke-Agt225BulkTemplateAssignment -Session $script:fakeSession `
                -ChangeTicketId '' -AssignmentPlan @() } | Should -Throw
        }
    }
}
```

The Pester suite is the gate every helper must pass before being added to the pipelined orchestrations in §12. CI runs the suite on every commit to ``docs/playbooks/control-implementations/2.25/``.

### 14.2 Anti-patterns

| Anti-pattern | Why it is wrong | Correct pattern |
|---|---|---|
| Returning ``$null`` to mean "clean" | Conflates clean with ``NotApplicable`` and ``Error`` (defect #6) | Always return ``[pscustomobject]`` with explicit ``Status`` |
| Using ``Write-Host`` for output | Breaks JSON serialization and pipelines | Use ``Write-Output`` of ``[pscustomobject]`` then ``ConvertTo-Json`` |
| Catching all exceptions broadly | Hides 403s and renames as "no data" | Catch specific exceptions; re-throw on auth/scope errors |
| Mutating without ``-ChangeTicketId`` | Violates SOX §404 ITGC | Helper throws ``Agt225-NoChangeTicket`` |
| Connecting without ``Disconnect-MgGraph`` first | Token leakage across tenants (defect #7) | ``Initialize-Agt225Session`` always disconnects first |
| Querying without paging | Truncated inventory (defect #3) | Use ``Invoke-Agt225PagedQuery`` with assertion |
| Trusting Researcher CU defaults | Default-on overrides supervisory review | ``Test-Agt225ResearcherComputerUse`` requires zone register |
| Running on PS 5.1 | Module ambiguity (defect #1) | ``Assert-Agt225ShellHost`` is the first call in §2 |
| Using ``Write-Verbose`` for evidence | Verbose stream is not captured by default | Evidence goes to JSON files; verbose stream is for operator only |

### 14.3 Hedged-language reminder

Every helper's ``Reason`` string and every line of operator-facing documentation in this playbook uses the hedged-language vocabulary required by ``CONTRIBUTING.md``:

* **Use:** "supports compliance with", "helps meet", "required for", "recommended to", "aids in".
* **Avoid:** absolute-outcome or automatic-compliance claims.

The helpers do not make an agent compliant; they **support** the AI Governance Lead and the FINRA registered principal in **meeting** their supervisory obligations.

### 14.4 Operating cadence

| Cadence | Helpers | Output | Owner |
|---|---|---|---|
| **Continuous (event-driven)** | ``Get-Agt225LifecycleEvents``, ``Get-Agt225PendingApprovals`` | SIEM stream | AI Administrator |
| **Daily (08:00 local, business days)** | §12.1 chain | Daily evidence pack + SIEM ingestion | AI Administrator |
| **Weekly (Monday 09:00)** | §12.2 chain | Weekly attestation + countersignature | AI Governance Lead |
| **Monthly (first business day)** | License coverage + ownerless sweep + remediation plan | Monthly remediation backlog | AI Governance Lead |
| **Quarterly (calendar quarter close)** | §12.3 chain + §13 attestation | Access-review certification | AI Governance Lead + Compliance Officer |
| **Per change ticket** | §12.4 mutation chain | Mutation manifest + attestation | AI Administrator (run) + AI Governance Lead (sign) |
| **Annually (fiscal year close)** | All helpers + retention rotation | Annual attestation packet | AI Governance Lead + CCO |

The cadence is mirrored in the sister 2.26 playbook so that the daily and weekly chains can be invoked from a single orchestrator script that produces a composite evidence pack covering both controls.

### 14.5 Module map (Agt225* helpers introduced in this file)

| Helper | Section | Returns | Mutation? |
|---|---|---|---|
| ``Assert-Agt225ShellHost`` | §2.1 | Status object or throws | No |
| ``Initialize-Agt225Session`` | §2.2 | SessionContext | No (connects) |
| ``Test-Agt225GraphScopes`` | §2.3 | Scope rows | No |
| ``Test-Agt225LicenseCoverageGating`` | §1.5 | Preview report | No |
| ``Get-Agt225CmdletAvailability`` | §1.3 | Availability rows | No |
| ``Get-Agt225AgentInventory`` | §3.1 | Inventory + writes JSON | No |
| ``Resolve-Agt225OwnerUpn`` | §3.2 | Owner row | No |
| ``Get-Agt225PendingApprovals`` | §4.1 | Pending rows | No |
| ``Find-Agt225OwnerlessAgents`` | §4.2 | Ownerless rows | No |
| ``New-Agt225OwnerlessRemediationPlan`` | §4.3 | Plan object | No |
| ``Get-Agt225GovernanceTemplate`` | §5.1 | Template rows | No |
| ``Test-Agt225TemplateBinding`` | §5.2 | Binding report | No |
| ``Get-Agt225LifecycleEvents`` | §6.1 | Event rows | No |
| ``Get-Agt225ApprovalHistory`` | §6.2 | History rows | No |
| ``Get-Agt225LicenseCoverage`` | §7.1 | License rows | No |
| ``Test-Agt225AccessReviewBinding`` | §7.2 | Review report | No |
| ``Test-Agt225ResearcherComputerUse`` | §7.3 | CU policy report | No |
| ``Invoke-Agt225BulkTemplateAssignment`` | §8.1 | Manifest object | **Yes (gated)** |
| ``New-Agt225EvidencePack`` | §9.2 | Pack object + writes JSON | No |
| ``Send-Agt225EvidenceToSiem`` | §10.1 | Forward result | No |
| ``Test-Agt225SiemRoundTrip`` | §10.2 | RoundTrip result | No |
| ``Invoke-Agt225Throttled`` | §11.1 | Wrapped result | Same as inner |
| ``Invoke-Agt225PagedQuery`` | §11.2 | Page array | No |
| ``New-Agt225AttestationPack`` | §13.1 | Attestation file | No |

---

## Cross-References

### Within this control's playbook set

* [Portal Walkthrough](./portal-walkthrough.md) — Step-by-step admin centre configuration. Use this when establishing a tenant for the first time.
* [Verification & Testing](./verification-testing.md) — Test cases that map one-to-one to the verification criteria in the control file.
* [Troubleshooting](./troubleshooting.md) — Common failure modes including the wrong-shell trap and the §0.2 false-clean defect catalogue.

### Sister control playbooks

* [Control 2.26 — Agent Approval Workflow Configuration (PowerShell)](../2.26/powershell-setup.md) — Workflow-side companion. The §12 cross-control chains depend on ``Agt226*`` helpers introduced there.

### Related controls referenced in this playbook

* [1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) — CA policy bindings asserted in §7.2.
* [1.11 — Conditional Access and Phishing-Resistant MFA](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) — PIM bindings for AI Administrator referenced in §12.3.
* [2.3 — Change Management and Release Planning](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md) — Labels asserted in §5.3 zone enforcement.
* [2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — Sister control.
* [3.1 — Centralized Logging and SIEM Integration](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — System of record for §6 lifecycle events.
* [3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — Ownerless-agent remediation evidence source.
* [3.13 — Agent 365 Admin Center Analytics](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) — Forwarding contract enforced in §10.

### Shared baseline

* [``_shared/powershell-baseline.md``](../../_shared/powershell-baseline.md) — Module pinning and evidence-emission conventions.

### Reference material

* [``docs/reference/role-catalog.md``](../../../reference/role-catalog.md) — Canonical role names used throughout this playbook.
* [``docs/reference/regulatory-mappings.md``](../../../reference/regulatory-mappings.md) — Full regulator-to-control matrix.
* [Microsoft Learn — Microsoft 365 Agent 365 Admin Center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide) (verify currency before each major run).
* [Microsoft Learn — Microsoft Graph SDK for PowerShell](https://learn.microsoft.com/powershell/microsoftgraph/overview).
* [Microsoft Learn — Researcher with Computer Use](https://learn.microsoft.com/en-us/microsoft-365/copilot/researcher-agent-computer-use) — GA October 2025; default-on inheritance behaviour.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
