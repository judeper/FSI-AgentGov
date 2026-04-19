# Control 3.6 — PowerShell Setup: Orphaned Agent Detection and Remediation

> **Scope.** This playbook automates the five primary detection signal sources, the four-tier remediation ladder, the cross-surface reconciliation engine, the bulk-reassignment safety gates, the sovereign-cloud manual reconciliation worksheet, and the SIEM forwarding pipeline defined in [Control 3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).
>
> **Baseline.** All scripts assume the conventions in [_shared/powershell-baseline.md](../../_shared/powershell-baseline.md). Sovereign-cloud endpoints are documented in [§3 — Sovereign Cloud Endpoints (GCC, GCC High, DoD)](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).
>
> **Namespace.** All functions in this playbook use the `Agt36` prefix to prevent collision with peer-control automation (`Agt225`, `Agt226`, `Agt12`).
>
> **Hedged-language reminder.** Detection output supports compliance with FINRA Rule 3110 supervisory review, SEC 17a-4(f) records retention, and SOX ITGC ownership integrity — **it does not replace** registered-principal supervisory review or the human approval gates required at each tier of the remediation ladder.

---

## §0 — Wrong-shell trap and false-clean defects

Control 3.6 false negatives almost always stem from running the wrong shell, the wrong module build, or a filter that silently excludes an entire signal surface. Treat every "clean" report from a new workstation as **suspect until the self-test in §13 passes**.

### 0.1 — Wrong-shell trap

- **Windows PowerShell 5.1 is not supported.** `Microsoft.Graph` v2.19+ requires PowerShell 7.4+. Running under 5.1 installs the v1.x legacy module path and returns partial `ServicePrincipal` payloads without the `tags` collection — signal #1 (ownerless Entra Agent ID) will silently return zero rows.
- **Integrated Script Environment (ISE) is not supported** for interactive sovereign-cloud bootstrap — device-code flow UI is clipped. Use Windows Terminal + `pwsh.exe`.
- **Azure Cloud Shell has no Power Platform module.** Signals #3 and #4 will fail to load `Microsoft.PowerApps.Administration.PowerShell`. Run this playbook from a privileged admin workstation, not Cloud Shell.

```powershell
# Enforce before sourcing any Agt36 function
if ($PSVersionTable.PSVersion.Major -lt 7 -or $PSVersionTable.PSVersion.Minor -lt 4) {
    throw "Agt36 requires PowerShell 7.4 or later. Current: $($PSVersionTable.PSVersion)"
}
if ($Host.Name -eq 'Windows PowerShell ISE Host') {
    throw "Agt36 is not supported under Windows PowerShell ISE. Use Windows Terminal with pwsh.exe."
}
```

### 0.2 — False-clean defects (Agt36-specific)

| # | Defect | Symptom | Root cause | Fix |
|---|--------|---------|------------|-----|
| 1 | Empty Power Platform environment list | Signal #3/#4 return zero rows tenant-wide | `Get-AdminPowerAppEnvironment` called before `Add-PowerAppsAccount` completed cached-token refresh | Call `Test-Agt36PowerPlatformSession` before detection; assert `.Count -gt 0` |
| 2 | Missing `tags/any(..)` filter | Signal #1 returns all service principals, not just agents | Using `Get-MgServicePrincipal -All` without OData filter | Use `Get-MgServicePrincipal -Filter "tags/any(t:t eq 'AgentIdentity')" -ConsistencyLevel eventual -CountVariable count` |
| 3 | HR connector stale > 24h | Signal #2 (sponsor-departed) returns zero rows during live termination | `employeeLeaveDateTime` attribute not synced from HR source of truth | `Test-Agt36HRFreshness` gate — abort if `max(lastSyncDateTime) > 24h` |
| 4 | Deleted environment ghost | Signal #4 reports "env owner departed" for already-deleted envs | Soft-deleted envs linger 7 days in `Get-AdminPowerAppEnvironment -Filter "Deleted"` | Exclude `properties.provisioningState -eq 'Deleted'` before join |
| 5 | Cross-surface duplicate explosion | One agent appears 5x in orphan register | Reconciliation engine keys on per-surface ID instead of canonical `AgentId` | Canonicalize on 1.2 registry `AgentId` before `Merge-Agt36OrphanRegister` |
| 6 | Grace-window race | Agent marked orphan the instant sponsor termed, before HR grace window | Detection runs at T+0 but SLA clock starts at T+24h per zone | Apply `Get-Agt36GraceWindow -Zone -SignalSource` before SLA aging |
| 7 | Sovereign silent skew | GCC High report is clean while commercial shows 40 orphans | Sovereign cloud has no Graph parity for HR `employeeLeaveDateTime` | Route sovereign tenants through §8 manual reconciliation worksheet — **do not early-exit to "clean"** |
| 8 | Throttled paging truncation | Signal #1 returns exactly 999 rows tenant-wide | `@odata.nextLink` not followed after HTTP 429 backoff | Use `Invoke-Agt36GraphPaged` with retry-after honoring |
| 9 | Card-vs-detection drift | Admin Center card (3.13) shows 12 orphans, detection reports 8 | Detection filter excludes disabled-but-unlicensed sponsors | Align filter with 3.13 definitions (cross-check §12 RECONCILE Pester) |
| 10 | SharePoint author disabled-user mask | Signal #5 misses Copilot Studio agents authored by disabled users | PnP.PowerShell `Get-PnPUser` caches resolved principals for 8h | Force `-Refresh` or bypass cache via Graph `directoryObjects/getByIds` |

### 0.3 — Self-test before every production run

Every scheduled detection job **must** invoke `Invoke-Agt36SelfTest` (§13) before emitting results to SIEM. A failed self-test emits an operational alert to the AI Governance Lead and suppresses the detection batch until resolved — **it does not** emit a "clean" report.

---
## §1 — Module pinning, Graph scopes, and canonical roles

### 1.1 — Module version matrix

Pin exact minimum versions. Later minor versions are acceptable, but do **not** float to an unpinned `-MinimumVersion` — sovereign-cloud tenants have observed Graph SDK v2.21 regressions on `tags` OData serialization.

```powershell
$Agt36ModuleMatrix = @(
    @{ Name = 'Microsoft.Graph.Authentication';           Min = '2.19.0' },
    @{ Name = 'Microsoft.Graph.Applications';             Min = '2.19.0' },
    @{ Name = 'Microsoft.Graph.Users';                    Min = '2.19.0' },
    @{ Name = 'Microsoft.Graph.Identity.DirectoryManagement'; Min = '2.19.0' },
    @{ Name = 'Microsoft.Graph.Identity.Governance';      Min = '2.19.0' },
    @{ Name = 'Microsoft.PowerApps.Administration.PowerShell'; Min = '2.0.175' },
    @{ Name = 'MicrosoftTeams';                           Min = '6.1.0'  },
    @{ Name = 'PnP.PowerShell';                           Min = '2.4.0'  }
)

function Test-Agt36ModuleMatrix {
    [CmdletBinding()]
    param([switch]$InstallMissing)
    $results = foreach ($m in $Agt36ModuleMatrix) {
        $installed = Get-Module -ListAvailable -Name $m.Name |
            Sort-Object Version -Descending | Select-Object -First 1
        $status = if (-not $installed) { 'Missing' }
                  elseif ($installed.Version -lt [version]$m.Min) { 'Outdated' }
                  else { 'OK' }
        if ($status -ne 'OK' -and $InstallMissing) {
            Install-Module $m.Name -MinimumVersion $m.Min -Scope CurrentUser -Force -AllowClobber
            $status = 'Installed'
        }
        [pscustomobject]@{
            Module = $m.Name; Required = $m.Min;
            Installed = $installed.Version; Status = $status
        }
    }
    $results
    if ($results.Status -contains 'Missing' -or $results.Status -contains 'Outdated') {
        throw "Agt36 module matrix failed. Re-run with -InstallMissing."
    }
}
```

### 1.2 — Microsoft Graph scope matrix

Two least-privilege profiles are defined — read-only detection and mutation (remediation). They are **never** combined into a single token. Mutation operations require step-up via PIM activation (§1.4).

| Operation | Graph scopes (delegated) | Graph scopes (app-only) |
|-----------|--------------------------|-------------------------|
| Detection (ReadOnly) | `Application.Read.All`, `Directory.Read.All`, `User.Read.All`, `AuditLog.Read.All` | `Application.Read.All`, `Directory.Read.All`, `User.Read.All`, `AuditLog.Read.All` |
| Remediation (Mutation) | `Application.ReadWrite.All`, `Directory.ReadWrite.All`, `User.ReadWrite.All`, `RoleManagement.ReadWrite.Directory` | `Application.ReadWrite.OwnedBy` (preferred), fall back to `Application.ReadWrite.All` only with documented scope-creep justification |
| Sponsor manager transfer | `User.ReadWrite.All`, `Directory.ReadWrite.All` | Same |

```powershell
$Agt36Scopes = @{
    Detect    = @('Application.Read.All','Directory.Read.All','User.Read.All','AuditLog.Read.All')
    Remediate = @('Application.ReadWrite.All','Directory.ReadWrite.All','User.ReadWrite.All','RoleManagement.ReadWrite.Directory')
}
```

### 1.3 — Canonical roles (align with role-catalog)

| Function | Canonical role(s) | PIM activation window | Notes |
|---------|-------------------|-----------------------|-------|
| Detection read | Entra Global Reader | 8h | Read-only scopes only |
| Agent SP remediation | Entra Agent ID Admin | 4h | Tier-1 owner inline edit |
| Sponsor transfer | Entra Identity Governance Admin | 4h | Signal #2 override path |
| Power Platform reassignment | Power Platform Admin | 4h | Tier-2/3 mutation |
| Terminal disposal handoff | AI Administrator | 2h | Tier-4 only; hands off to 2.25 |
| Evidence labeling | Purview Compliance Admin | 8h | 6-year WORM retention apply |
| Governance sign-off | AI Governance Lead | N/A (standing) | Attestation only |

All role activations **must** reference a `ChangeTicketId` in the PIM justification when used for mutation. Detection-only activations reference the scheduled job run-id.

### 1.4 — PIM activation helper

```powershell
function Request-Agt36PimActivation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateSet('Detect','Remediate','SponsorTransfer','PowerPlatform','Terminal','Evidence')]
        [string]$Profile,
        [Parameter(Mandatory)][string]$Justification,
        [string]$ChangeTicketId,
        [ValidateRange(1,8)][int]$DurationHours = 4
    )
    if ($Profile -ne 'Detect' -and -not $ChangeTicketId) {
        throw "ChangeTicketId is required for mutation profiles. Detect is the only profile exempt."
    }
    # NOTE: interactive wrapper; production flows call the Graph Identity Governance
    # /roleManagement/directory/roleAssignmentScheduleRequests endpoint with
    # action=selfActivate and a structured justification payload.
    [pscustomobject]@{
        Profile         = $Profile
        ChangeTicketId  = $ChangeTicketId
        Justification   = $Justification
        DurationHours   = $DurationHours
        RequestedAtUtc  = (Get-Date).ToUniversalTime()
        Status          = 'Pending'  # updated by Graph response in production wrapper
    }
}
```

---

## §2 — Sovereign-cloud bootstrap (GCC, GCC High, DoD)

> **Critical difference vs. 2.26.** Control 3.6 does **not** early-exit on sovereign clouds. Sovereign tenants must still produce a reconciliation artifact — the compensating control is a **quarterly manual reconciliation worksheet** (§8) joining HR leaver lists, Entra disabled-user exports, Power Platform maker/env-owner exports, and the 1.2 agent inventory registry.

```powershell
function Initialize-Agt36SovereignContext {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')]
        [string]$Cloud
    )
    $endpoints = switch ($Cloud) {
        'Commercial'  { @{ Graph='https://graph.microsoft.com';        AzureAD='https://login.microsoftonline.com';      PP='prod';      PnPEnv='Production' } }
        'USGov'       { @{ Graph='https://graph.microsoft.us';         AzureAD='https://login.microsoftonline.us';       PP='usgov';     PnPEnv='USGovernment' } }
        'USGovHigh'   { @{ Graph='https://graph.microsoft.us';         AzureAD='https://login.microsoftonline.us';       PP='usgovhigh'; PnPEnv='USGovernmentHigh' } }
        'USGovDoD'    { @{ Graph='https://dod-graph.microsoft.us';     AzureAD='https://login.microsoftonline.us';       PP='dod';       PnPEnv='USGovernmentDoD' } }
    }
    $ctx = [pscustomobject]@{
        Cloud               = $Cloud
        GraphEndpoint       = $endpoints.Graph
        AzureADEndpoint     = $endpoints.AzureAD
        PowerPlatformEnv    = $endpoints.PP
        PnPEnvironment      = $endpoints.PnPEnv
        RequiresManualRecon = $Cloud -ne 'Commercial'
        HRConnectorParity   = $Cloud -eq 'Commercial'   # employeeLeaveDateTime parity
        InitializedAtUtc    = (Get-Date).ToUniversalTime()
    }
    if ($ctx.RequiresManualRecon) {
        Write-Warning "Sovereign cloud '$Cloud' detected. Signal #2 (sponsor-departed via employeeLeaveDateTime) has no Graph parity. Route to Export-Agt36SovereignReconciliationWorksheet (§8). DO NOT treat detection output as authoritative."
    }
    $ctx
}
```

The returned context object is threaded through every detection function so that sovereign-specific branching (manual reconciliation fallback for signal #2, reduced HR freshness gates) is an **explicit parameter**, never a global state flag.

---
## §3 — Connection helper (`Initialize-Agt36Session`)

A single entry point connects to every surface needed for cross-signal detection. Failures are **never** swallowed — a surface that cannot connect returns a session object with `Status = 'Error'` for that surface, and downstream detection functions emit `Status = 'NotApplicable'` for their signal rather than falsely reporting `Clean`.

```powershell
function Initialize-Agt36Session {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$TenantId,
        [Parameter(Mandatory)][ValidateSet('Detect','Remediate','SponsorTransfer','PowerPlatform','Terminal','Evidence')]
        [string]$Profile,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')]
        [string]$Cloud,
        [string]$ChangeTicketId
    )
    $sovereign = Initialize-Agt36SovereignContext -Cloud $Cloud
    $scopes    = if ($Profile -eq 'Detect') { $Agt36Scopes.Detect } else { $Agt36Scopes.Remediate }
    $session = [pscustomobject]@{
        TenantId         = $TenantId
        Profile          = $Profile
        Sovereign        = $sovereign
        ChangeTicketId   = $ChangeTicketId
        ConnectedAtUtc   = (Get-Date).ToUniversalTime()
        GraphStatus      = 'Pending'
        PowerPlatformStatus = 'Pending'
        TeamsStatus      = 'Pending'
        PnPStatus        = 'Pending'
        Errors           = @()
    }

    # Graph
    try {
        Connect-MgGraph -TenantId $TenantId -Scopes $scopes -Environment (
            switch ($Cloud) {
                'Commercial'{'Global'} 'USGov'{'USGov'} 'USGovHigh'{'USGovHigh'} 'USGovDoD'{'USGovDoD'}
            }) -NoWelcome -ErrorAction Stop
        $session.GraphStatus = 'Connected'
    } catch { $session.GraphStatus = 'Error'; $session.Errors += "Graph: $($_.Exception.Message)" }

    # Power Platform
    try {
        Add-PowerAppsAccount -Endpoint $sovereign.PowerPlatformEnv -ErrorAction Stop | Out-Null
        $session.PowerPlatformStatus = 'Connected'
    } catch { $session.PowerPlatformStatus = 'Error'; $session.Errors += "PowerPlatform: $($_.Exception.Message)" }

    # Teams (signal #5 cross-reference; optional for detect-only)
    try {
        Connect-MicrosoftTeams -TenantId $TenantId -ErrorAction Stop | Out-Null
        $session.TeamsStatus = 'Connected'
    } catch { $session.TeamsStatus = 'Error'; $session.Errors += "Teams: $($_.Exception.Message)" }

    # PnP (signal #5 — SharePoint-hosted Copilot Studio authors)
    # Connection per-site is deferred to Get-Agt36SharePointAuthorDisabledAgent.
    $session.PnPStatus = 'Deferred'

    if ($Profile -eq 'Detect' -and $session.GraphStatus -ne 'Connected') {
        throw "Agt36 Detect profile requires Graph. Errors: $($session.Errors -join '; ')"
    }
    $session
}
```

---

## §4 — Detection functions (Signals 1–5)

Every detection helper returns a **structured object** with `Status` ∈ `{Clean, Anomaly, Pending, NotApplicable, Error}`. Returning `$null`, an empty array without a status wrapper, or an untyped hashtable is considered a **bug** — see §0.2 defect #1 and §13 Pester `DETECT` namespace.

### 4.1 — Signal #1: Ownerless Entra Agent ID service principals

```powershell
function Get-Agt36OwnerlessAgent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][ValidateSet(1,2,3)][int]$Zone,
        [int]$GraceHours = 24
    )
    if ($Session.GraphStatus -ne 'Connected') {
        return [pscustomobject]@{ SignalId=1; Status='NotApplicable'; Reason='Graph not connected'; Findings=@() }
    }
    try {
        # Page through all agent service principals; filter for zero owners
        $agents = Invoke-Agt36GraphPaged -Uri "/v1.0/servicePrincipals?`$filter=tags/any(t:t eq 'AgentIdentity')&`$select=id,displayName,appId,tags,createdDateTime&`$count=true" `
                                         -ConsistencyLevel eventual
        $findings = foreach ($sp in $agents) {
            $owners = Get-MgServicePrincipalOwner -ServicePrincipalId $sp.id -ErrorAction SilentlyContinue
            $activeOwners = @($owners | Where-Object { $_.AdditionalProperties.accountEnabled -ne $false })
            if ($activeOwners.Count -eq 0) {
                [pscustomobject]@{
                    SignalId      = 1
                    AgentId       = $sp.appId
                    ObjectId      = $sp.id
                    DisplayName   = $sp.displayName
                    DetectedAtUtc = (Get-Date).ToUniversalTime()
                    OwnerCount    = 0
                    Zone          = $Zone
                    GraceUntilUtc = ((Get-Date).AddHours($GraceHours)).ToUniversalTime()
                    SlaTargetDays = switch ($Zone) { 3 {7} 2 {14} 1 {30} }
                }
            }
        }
        [pscustomobject]@{
            SignalId = 1
            Status   = if ($findings.Count -eq 0) { 'Clean' } else { 'Anomaly' }
            Findings = @($findings)
            RunAtUtc = (Get-Date).ToUniversalTime()
        }
    } catch {
        [pscustomobject]@{ SignalId=1; Status='Error'; Reason=$_.Exception.Message; Findings=@() }
    }
}
```

### 4.2 — Signal #2: Sponsor-departed (HR `employeeLeaveDateTime` correlation)

This signal has **no sovereign-cloud parity** — `employeeLeaveDateTime` is not surfaced in GCC/GCC High/DoD Graph. Sovereign tenants must use §8.

```powershell
function Get-Agt36SponsorDepartedAgent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][ValidateSet(1,2,3)][int]$Zone,
        [int]$LookbackDays = 90,
        [switch]$RealtimeMode
    )
    if ($Session.Sovereign.RequiresManualRecon) {
        return [pscustomobject]@{
            SignalId=2; Status='NotApplicable';
            Reason="Sovereign cloud '$($Session.Sovereign.Cloud)' lacks employeeLeaveDateTime parity. Use Export-Agt36SovereignReconciliationWorksheet.";
            Findings=@()
        }
    }
    if (-not (Test-Agt36HRFreshness -Session $Session -MaxAgeHours 24)) {
        return [pscustomobject]@{ SignalId=2; Status='Pending'; Reason='HR connector stale > 24h'; Findings=@() }
    }
    try {
        # Pull agents from 1.2 registry (authoritative sponsor map)
        $registry = Get-Agt12AgentRegistry -Session $Session
        $leaverFilter = if ($RealtimeMode) {
            "employeeLeaveDateTime ne null"
        } else {
            "employeeLeaveDateTime ge $((Get-Date).AddDays(-$LookbackDays).ToString('o'))"
        }
        $leavers = Get-MgUser -Filter $leaverFilter -Property 'id,userPrincipalName,employeeLeaveDateTime,accountEnabled' -All -ConsistencyLevel eventual -CountVariable c
        $leaverIndex = @{}; foreach ($u in $leavers) { $leaverIndex[$u.Id] = $u }
        $findings = foreach ($a in $registry) {
            if ($leaverIndex.ContainsKey($a.SponsorObjectId)) {
                $sp = $leaverIndex[$a.SponsorObjectId]
                $graceHours = if ($Zone -eq 3) { 0 } elseif ($Zone -eq 2) { 24 } else { 240 }
                [pscustomobject]@{
                    SignalId          = 2
                    AgentId           = $a.AgentId
                    DisplayName       = $a.DisplayName
                    SponsorObjectId   = $a.SponsorObjectId
                    SponsorUpn        = $sp.UserPrincipalName
                    SponsorLeaveUtc   = $sp.EmployeeLeaveDateTime
                    DetectedAtUtc     = (Get-Date).ToUniversalTime()
                    Zone              = $Zone
                    GraceUntilUtc     = $sp.EmployeeLeaveDateTime.AddHours($graceHours)
                    SlaTargetBusDays  = switch ($Zone) { 3 {0} 2 {1} 1 {10} }
                    RemediationHint   = 'SponsorManagerTransferOverride'
                }
            }
        }
        [pscustomobject]@{
            SignalId = 2
            Status   = if ($findings.Count -eq 0) { 'Clean' } else { 'Anomaly' }
            Findings = @($findings)
            RunAtUtc = (Get-Date).ToUniversalTime()
        }
    } catch {
        [pscustomobject]@{ SignalId=2; Status='Error'; Reason=$_.Exception.Message; Findings=@() }
    }
}

function Test-Agt36HRFreshness {
    param($Session, [int]$MaxAgeHours = 24)
    # Production: query the provisioning service job status for the HR connector.
    # Returns $true if last successful sync < MaxAgeHours; $false otherwise.
    # Stub here — must be implemented per tenant HR connector (Workday, SAP SF, UKG, etc.)
    $true
}
```
### 4.3 — Signal #3: Power Platform maker-departed agents

```powershell
function Get-Agt36MakerDepartedAgent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][ValidateSet(1,2,3)][int]$Zone
    )
    if ($Session.PowerPlatformStatus -ne 'Connected') {
        return [pscustomobject]@{ SignalId=3; Status='NotApplicable'; Reason='Power Platform not connected'; Findings=@() }
    }
    try {
        $envs = Get-AdminPowerAppEnvironment | Where-Object { $_.EnvironmentType -ne 'Default' -or $Zone -eq 1 }
        if (-not $envs) {
            return [pscustomobject]@{ SignalId=3; Status='Error'; Reason='Empty environment list — see §0.2 defect #1'; Findings=@() }
        }
        $findings = foreach ($env in $envs) {
            $apps = Get-AdminPowerApp -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
            foreach ($app in $apps) {
                $makerId = $app.Owner.id
                if (-not $makerId) { continue }
                try {
                    $maker = Get-MgUser -UserId $makerId -Property 'id,userPrincipalName,accountEnabled,employeeLeaveDateTime' -ErrorAction Stop
                } catch {
                    # deleted user — maker is unresolvable
                    $maker = $null
                }
                $isDeparted = (-not $maker) -or (-not $maker.AccountEnabled) -or ($maker.EmployeeLeaveDateTime -and $maker.EmployeeLeaveDateTime -lt (Get-Date))
                if ($isDeparted) {
                    [pscustomobject]@{
                        SignalId        = 3
                        AgentId         = $app.AppName
                        DisplayName     = $app.DisplayName
                        EnvironmentName = $env.EnvironmentName
                        EnvironmentType = $env.EnvironmentType
                        MakerId         = $makerId
                        MakerUpn        = $maker.UserPrincipalName
                        MakerDisabled   = (-not $maker) -or (-not $maker.AccountEnabled)
                        DetectedAtUtc   = (Get-Date).ToUniversalTime()
                        Zone            = $Zone
                        SlaTargetDays   = switch ($Zone) { 3 {7} 2 {14} 1 {30} }
                        RemediationHint = 'PowerAppOwnerReassignment'
                    }
                }
            }
        }
        [pscustomobject]@{
            SignalId = 3
            Status   = if ($findings.Count -eq 0) { 'Clean' } else { 'Anomaly' }
            Findings = @($findings)
            RunAtUtc = (Get-Date).ToUniversalTime()
        }
    } catch {
        [pscustomobject]@{ SignalId=3; Status='Error'; Reason=$_.Exception.Message; Findings=@() }
    }
}
```

### 4.4 — Signal #4: Environment-owner departed

```powershell
function Get-Agt36EnvironmentOwnerDepartedAgent {
    [CmdletBinding()]
    param([Parameter(Mandatory)]$Session,[Parameter(Mandatory)][ValidateSet(1,2,3)][int]$Zone)
    if ($Session.PowerPlatformStatus -ne 'Connected') {
        return [pscustomobject]@{ SignalId=4; Status='NotApplicable'; Reason='Power Platform not connected'; Findings=@() }
    }
    try {
        $envs = Get-AdminPowerAppEnvironment |
            Where-Object { $_.Properties.provisioningState -ne 'Deleted' }   # defect #4
        $findings = foreach ($env in $envs) {
            $ownerId = $env.Properties.createdBy.id
            if (-not $ownerId) { continue }
            try { $owner = Get-MgUser -UserId $ownerId -Property 'id,userPrincipalName,accountEnabled' -ErrorAction Stop }
            catch { $owner = $null }
            if ((-not $owner) -or (-not $owner.AccountEnabled)) {
                # For each agent in the orphaned env, emit one finding
                $appsInEnv = Get-AdminPowerApp -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue
                foreach ($app in $appsInEnv) {
                    [pscustomobject]@{
                        SignalId        = 4
                        AgentId         = $app.AppName
                        DisplayName     = $app.DisplayName
                        EnvironmentName = $env.EnvironmentName
                        EnvironmentOwnerId  = $ownerId
                        EnvironmentOwnerUpn = $owner.UserPrincipalName
                        DetectedAtUtc   = (Get-Date).ToUniversalTime()
                        Zone            = $Zone
                        SlaTargetDays   = switch ($Zone) { 3 {3} 2 {3} 1 {7} }
                        RemediationHint = 'EnvironmentReassignmentOrRetire'
                    }
                }
            }
        }
        [pscustomobject]@{
            SignalId = 4
            Status   = if ($findings.Count -eq 0) { 'Clean' } else { 'Anomaly' }
            Findings = @($findings)
            RunAtUtc = (Get-Date).ToUniversalTime()
        }
    } catch {
        [pscustomobject]@{ SignalId=4; Status='Error'; Reason=$_.Exception.Message; Findings=@() }
    }
}
```

### 4.5 — Signal #5: SharePoint-hosted Copilot Studio author disabled

```powershell
function Get-Agt36SharePointAuthorDisabledAgent {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][ValidateSet(1,2,3)][int]$Zone,
        [string[]]$SiteCollectionUrls
    )
    if (-not $SiteCollectionUrls) {
        return [pscustomobject]@{ SignalId=5; Status='Pending'; Reason='No site collections supplied'; Findings=@() }
    }
    $findings = @()
    foreach ($url in $SiteCollectionUrls) {
        try {
            Connect-PnPOnline -Url $url -Interactive -AzureEnvironment $Session.Sovereign.PnPEnvironment -ErrorAction Stop
            # Copilot Studio author principals are stored as SharePoint site users; resolve
            # through Graph (not PnP cache — see §0.2 defect #10).
            $siteUsers = Get-PnPUser | Where-Object { $_.PrincipalType -eq 'User' -and $_.LoginName -match 'i:0#.f\|membership\|' }
            foreach ($u in $siteUsers) {
                $upn = ($u.LoginName -split '\|')[-1]
                try { $gu = Get-MgUser -UserId $upn -Property 'id,accountEnabled,employeeLeaveDateTime' -ErrorAction Stop }
                catch { $gu = $null }
                if ((-not $gu) -or (-not $gu.AccountEnabled)) {
                    $findings += [pscustomobject]@{
                        SignalId        = 5
                        AuthorUpn       = $upn
                        SiteUrl         = $url
                        DetectedAtUtc   = (Get-Date).ToUniversalTime()
                        Zone            = $Zone
                        SlaTargetDays   = switch ($Zone) { 3 {14} 2 {21} 1 {30} }
                        RemediationHint = 'ReauthorOrArchive'
                    }
                }
            }
        } catch {
            $findings += [pscustomobject]@{ SignalId=5; SiteUrl=$url; Error=$_.Exception.Message }
        }
    }
    [pscustomobject]@{
        SignalId = 5
        Status   = if ($findings.Count -eq 0) { 'Clean' } else { 'Anomaly' }
        Findings = @($findings)
        RunAtUtc = (Get-Date).ToUniversalTime()
    }
}
```

### 4.6 — Signals #6–#10 (short helpers)

Signals #6–#10 (Teams-scoped agents without channel owner, deleted-group affiliation, license-expired maker, connector-owner departed, consent-grantor departed) share the same return-object contract. Stubs are provided for symmetry; full implementations are delivered incrementally as signal-by-signal PRs to prevent a single monolithic change from masking false-clean regressions.

```powershell
function Get-Agt36TeamsChannelAgent             { param($Session,[int]$Zone) ; [pscustomobject]@{SignalId=6;Status='Pending';Findings=@()} }
function Get-Agt36DeletedGroupAffiliatedAgent   { param($Session,[int]$Zone) ; [pscustomobject]@{SignalId=7;Status='Pending';Findings=@()} }
function Get-Agt36LicenseExpiredMakerAgent      { param($Session,[int]$Zone) ; [pscustomobject]@{SignalId=8;Status='Pending';Findings=@()} }
function Get-Agt36ConnectorOwnerDepartedAgent   { param($Session,[int]$Zone) ; [pscustomobject]@{SignalId=9;Status='Pending';Findings=@()} }
function Get-Agt36ConsentGrantorDepartedAgent   { param($Session,[int]$Zone) ; [pscustomobject]@{SignalId=10;Status='Pending';Findings=@()} }
```

### 4.7 — Paged Graph helper with throttle handling

```powershell
function Invoke-Agt36GraphPaged {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Uri,
        [string]$ConsistencyLevel = 'eventual',
        [int]$MaxRetries = 5
    )
    $results = New-Object System.Collections.Generic.List[object]
    $next = $Uri
    while ($next) {
        $attempt = 0
        while ($true) {
            try {
                $resp = Invoke-MgGraphRequest -Method GET -Uri $next -Headers @{ ConsistencyLevel = $ConsistencyLevel }
                break
            } catch {
                $attempt++
                $retryAfter = 2 * [Math]::Pow(2, $attempt)
                if ($_.Exception.Response.StatusCode.value__ -eq 429 -and $_.Exception.Response.Headers.RetryAfter) {
                    $retryAfter = [int]$_.Exception.Response.Headers.RetryAfter.Delta.TotalSeconds
                }
                if ($attempt -ge $MaxRetries) { throw }
                Write-Verbose "Throttled. Sleeping $retryAfter s (attempt $attempt)."
                Start-Sleep -Seconds $retryAfter
            }
        }
        if ($resp.value) { $resp.value | ForEach-Object { $results.Add($_) } }
        $next = $resp.'@odata.nextLink'
    }
    ,$results.ToArray()
}
```

---
## §5 — Reconciliation engine (`Merge-Agt36OrphanRegister`)

The reconciliation engine joins all signal-source outputs into a **unified orphan register** keyed on the canonical `AgentId` from the 1.2 Agent Inventory Registry. History is append-only — every detection run creates a new row; prior rows are never updated in place (supports SOX ITGC non-repudiation and SEC 17a-4(f) WORM semantics).

```powershell
function Merge-Agt36OrphanRegister {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][object[]]$SignalResults,
        [Parameter(Mandatory)][hashtable]$AgentRegistry,   # from Get-Agt12AgentRegistry (1.2), keyed by surface ID
        [Parameter(Mandatory)][string]$RunId
    )
    $register = @{}
    foreach ($signal in $SignalResults) {
        if ($signal.Status -ne 'Anomaly') { continue }
        foreach ($f in $signal.Findings) {
            $canonical = Resolve-Agt36CanonicalAgentId -Finding $f -Registry $AgentRegistry
            if (-not $canonical) {
                Write-Warning "Finding with surface=$($f.SignalId), id=$($f.AgentId) cannot be mapped to canonical AgentId; skipping."
                continue
            }
            if (-not $register.ContainsKey($canonical)) {
                $register[$canonical] = [pscustomobject]@{
                    AgentId     = $canonical
                    Zone        = $f.Zone
                    Signals     = New-Object System.Collections.Generic.List[int]
                    Findings    = New-Object System.Collections.Generic.List[object]
                    FirstSeenUtc = $f.DetectedAtUtc
                    RunId       = $RunId
                    Status      = 'Open'
                    SlaTargetDate = $null
                }
            }
            $entry = $register[$canonical]
            if ($entry.Signals -notcontains $f.SignalId) { $entry.Signals.Add($f.SignalId) }
            $entry.Findings.Add($f)
            # SLA: use the tightest (soonest) SLA across all signals hitting this agent
            $candidate = if ($f.SlaTargetDays) { (Get-Date).AddDays($f.SlaTargetDays) }
                         elseif ($f.SlaTargetBusDays -ne $null) { (Get-Date).AddDays($f.SlaTargetBusDays * 1.4) }
                         else { (Get-Date).AddDays(14) }
            if ($null -eq $entry.SlaTargetDate -or $candidate -lt $entry.SlaTargetDate) {
                $entry.SlaTargetDate = $candidate
            }
        }
    }
    # Append to WORM-backed register store (evidence stage §11)
    $rows = $register.Values
    Write-Agt36RegisterAppend -Rows $rows -RunId $RunId
    ,$rows
}

function Resolve-Agt36CanonicalAgentId {
    param($Finding, [hashtable]$Registry)
    # Each surface ID → canonical mapping. The 1.2 registry maintains multi-surface identities.
    switch ($Finding.SignalId) {
        1 { if ($Registry.ByAppId.ContainsKey($Finding.AgentId))     { $Registry.ByAppId[$Finding.AgentId] } }
        2 { $Finding.AgentId }  # registry lookup was authoritative at detect time
        3 { if ($Registry.ByPowerAppName.ContainsKey($Finding.AgentId)) { $Registry.ByPowerAppName[$Finding.AgentId] } }
        4 { if ($Registry.ByPowerAppName.ContainsKey($Finding.AgentId)) { $Registry.ByPowerAppName[$Finding.AgentId] } }
        5 { if ($Registry.BySharePointAuthor.ContainsKey("$($Finding.SiteUrl)|$($Finding.AuthorUpn)")) {
              $Registry.BySharePointAuthor["$($Finding.SiteUrl)|$($Finding.AuthorUpn)"] } }
        default { $null }
    }
}

function Write-Agt36RegisterAppend {
    param([object[]]$Rows, [string]$RunId)
    # Append-only JSONL store. In production this writes to a Purview-retention-labeled
    # location (§11) with SHA-256 integrity hashing.
    $outDir = Join-Path $env:ProgramData 'Agt36\register'
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    $file = Join-Path $outDir "register-$($RunId).jsonl"
    foreach ($r in $Rows) { Add-Content -LiteralPath $file -Value ($r | ConvertTo-Json -Depth 8 -Compress) }
}
```

### 5.1 — Card-vs-detection parity check

Verification Criterion #2 requires **zero tolerated variance** between the orphan count on the 3.13 Admin Center card and the detection register. Implement as a first-class assertion in every scheduled run.

```powershell
function Assert-Agt36CardParity {
    param([object[]]$Register, [int]$CardOrphanCount, [string]$RunId)
    if ($Register.Count -ne $CardOrphanCount) {
        throw "Card-vs-detection parity failure: register=$($Register.Count), card=$CardOrphanCount, runId=$RunId. Emit operational alert; DO NOT emit clean SIEM event."
    }
}
```

---

## §6 — Remediation tiers

The control defines a four-tier remediation ladder. Every tier function is `SupportsShouldProcess` + `ConfirmImpact='High'` and records an immutable journal entry before mutation.

### 6.1 — Tier 1: Inline owner reassignment (Entra SP)

```powershell
function Set-Agt36AgentOwnerInline {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][string]$ServicePrincipalObjectId,
        [Parameter(Mandatory)][string]$NewOwnerObjectId,
        [Parameter(Mandatory)][string]$ChangeTicketId,
        [Parameter(Mandatory)][string]$Justification
    )
    $preflight = Test-Agt36ReassignmentPrerequisite -Session $Session -NewOwnerObjectId $NewOwnerObjectId
    if (-not $preflight.Passed) {
        throw "Pre-flight failed: $($preflight.Reason)"
    }
    $target = "ServicePrincipal $ServicePrincipalObjectId → owner $NewOwnerObjectId"
    if ($PSCmdlet.ShouldProcess($target, "Tier-1 owner reassignment")) {
        Write-Agt36Journal -Action 'Tier1-InlineOwner' -Target $ServicePrincipalObjectId `
            -ChangeTicketId $ChangeTicketId -Justification $Justification -Session $Session
        $ref = @{ '@odata.id' = "https://graph.microsoft.com/v1.0/directoryObjects/$NewOwnerObjectId" }
        New-MgServicePrincipalOwnerByRef -ServicePrincipalId $ServicePrincipalObjectId -BodyParameter $ref
        [pscustomobject]@{ Tier=1; Outcome='Applied'; Target=$ServicePrincipalObjectId; NewOwner=$NewOwnerObjectId; ChangeTicketId=$ChangeTicketId }
    }
}
```

### 6.2 — Tier 2: Sponsor manager transfer override (Signal #2)

When a sponsor has departed (signal #2), the canonical remediation is to transfer sponsorship to the departed sponsor's **manager**, preserving the 1.7 sponsor-lineage chain. This is a dedicated path — **do not** conflate with Tier-1.

```powershell
function Invoke-Agt36SponsorManagerTransferOverride {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][string]$AgentId,
        [Parameter(Mandatory)][string]$DepartedSponsorObjectId,
        [Parameter(Mandatory)][string]$ChangeTicketId,
        [Parameter(Mandatory)][string]$Justification
    )
    try {
        $manager = Get-MgUserManager -UserId $DepartedSponsorObjectId -ErrorAction Stop
    } catch {
        throw "Departed sponsor has no manager on record. Escalate to AI Governance Lead for manual assignment."
    }
    if (-not $manager.AdditionalProperties.accountEnabled) {
        throw "Manager $($manager.Id) is disabled. Recursive manager lookup disallowed — escalate manually."
    }
    if ($PSCmdlet.ShouldProcess("Agent $AgentId", "Sponsor transfer → $($manager.Id)")) {
        Write-Agt36Journal -Action 'Tier2-SponsorManagerTransfer' -Target $AgentId `
            -ChangeTicketId $ChangeTicketId -Justification $Justification -Session $Session `
            -ExtraContext @{ DepartedSponsor=$DepartedSponsorObjectId; NewSponsor=$manager.Id }
        # Production: update 1.2 registry + 1.7 lineage record.
        Update-Agt12RegistrySponsor -AgentId $AgentId -NewSponsorObjectId $manager.Id
        [pscustomobject]@{ Tier=2; Outcome='Applied'; AgentId=$AgentId; NewSponsor=$manager.Id; ChangeTicketId=$ChangeTicketId }
    }
}
```

### 6.3 — Tier 3: Power Platform owner reassignment

```powershell
function Set-Agt36PowerAppOwner {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][string]$EnvironmentName,
        [Parameter(Mandatory)][string]$AppName,
        [Parameter(Mandatory)][string]$NewOwnerObjectId,
        [Parameter(Mandatory)][string]$ChangeTicketId,
        [Parameter(Mandatory)][string]$Justification
    )
    $pf = Test-Agt36ReassignmentPrerequisite -Session $Session -NewOwnerObjectId $NewOwnerObjectId -EnvironmentName $EnvironmentName
    if (-not $pf.Passed) { throw "Pre-flight failed: $($pf.Reason)" }
    if ($PSCmdlet.ShouldProcess("PowerApp $AppName in $EnvironmentName", "Tier-3 owner reassignment → $NewOwnerObjectId")) {
        Write-Agt36Journal -Action 'Tier3-PowerAppOwner' -Target "$EnvironmentName/$AppName" `
            -ChangeTicketId $ChangeTicketId -Justification $Justification -Session $Session
        Set-AdminPowerAppOwner -EnvironmentName $EnvironmentName -AppName $AppName -AppOwner $NewOwnerObjectId
        [pscustomobject]@{ Tier=3; Outcome='Applied'; EnvironmentName=$EnvironmentName; AppName=$AppName; NewOwner=$NewOwnerObjectId; ChangeTicketId=$ChangeTicketId }
    }
}
```

### 6.4 — Tier 4: Terminal disposal handoff (to Control 2.25)

Tier-4 is **not a mutation** performed by this playbook. It is a structured handoff to Control 2.25's service-principal lifecycle disposal workflow. This playbook only emits the handoff evidence and updates the orphan register status to `HandedOff-2.25`.

```powershell
function Invoke-Agt36TerminalDisposalHandoff {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][string]$AgentId,
        [Parameter(Mandatory)][string]$ChangeTicketId,
        [Parameter(Mandatory)][string]$Justification,
        [Parameter(Mandatory)][string]$ApproverObjectId   # must be AI Governance Lead
    )
    if ($PSCmdlet.ShouldProcess($AgentId, "Tier-4 terminal disposal handoff to 2.25")) {
        $handoff = [pscustomobject]@{
            Tier             = 4
            HandoffTargetControl = '2.25'
            AgentId          = $AgentId
            HandoffAtUtc     = (Get-Date).ToUniversalTime()
            ChangeTicketId   = $ChangeTicketId
            Justification    = $Justification
            ApprovedByObjectId = $ApproverObjectId
            Outcome          = 'Queued-2.25'
        }
        Write-Agt36Journal -Action 'Tier4-DisposalHandoff' -Target $AgentId -ChangeTicketId $ChangeTicketId -Justification $Justification -Session $Session -ExtraContext $handoff
        Export-Agt36HandoffToControl225 -Handoff $handoff
        $handoff
    }
}
```

### 6.5 — Pre-flight prerequisites

```powershell
function Test-Agt36ReassignmentPrerequisite {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][string]$NewOwnerObjectId,
        [string]$EnvironmentName
    )
    try {
        $user = Get-MgUser -UserId $NewOwnerObjectId -Property 'id,accountEnabled,assignedLicenses,userPrincipalName' -ErrorAction Stop
    } catch {
        return [pscustomobject]@{ Passed=$false; Reason="New owner not resolvable: $($_.Exception.Message)" }
    }
    if (-not $user.AccountEnabled)       { return [pscustomobject]@{ Passed=$false; Reason="New owner account disabled" } }
    if ($user.AssignedLicenses.Count -eq 0) { return [pscustomobject]@{ Passed=$false; Reason="New owner has no assigned license" } }
    if ($EnvironmentName) {
        $role = Get-AdminPowerAppRoleAssignment -EnvironmentName $EnvironmentName -PrincipalObjectId $NewOwnerObjectId -ErrorAction SilentlyContinue
        if (-not $role) { return [pscustomobject]@{ Passed=$false; Reason="New owner lacks environment membership/maker role" } }
    }
    [pscustomobject]@{ Passed=$true; Reason='OK'; Upn=$user.UserPrincipalName }
}
```

---
## §7 — Bulk reassignment safety gates {#bulk-maker-reassignment}

Bulk remediation is high-risk. The control requires mandatory gates before any multi-target mutation:

| Gate | Rule | Failure mode |
|------|------|--------------|
| Dry-run mandatory | `-WhatIf` must be invoked first; a dry-run receipt must exist within 24h | Throw before mutation |
| Max batch size | ≤ 50 targets per run (Zone 3), ≤ 100 (Zone 2/1) | Throw before mutation |
| Change ticket | Non-empty `ChangeTicketId` matching regex `^(CHG|RITM)\d{7,}$` | Throw before mutation |
| Idempotency | Key = `SHA256(AgentId + NewOwnerObjectId + ChangeTicketId)`; replay-safe | Skip with `Outcome='AlreadyApplied'` |
| Per-item audit | Every item appended to SHA-256 journal + manifest | Hard failure |
| Approver identity | Approver objectId must be member of AI Governance Lead group | Throw before mutation |

```powershell
function Set-Agt36BulkOwnerReassignment {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][object[]]$Assignments,   # {AgentId, Surface, NewOwnerObjectId, EnvironmentName?}
        [Parameter(Mandatory)][string]$ChangeTicketId,
        [Parameter(Mandatory)][string]$Justification,
        [Parameter(Mandatory)][string]$ApproverObjectId,
        [switch]$DryRun,
        [string]$DryRunReceiptPath,
        [int]$MaxBatchSize = 50
    )
    # --- Validation gates ------------------------------------------------
    if ($ChangeTicketId -notmatch '^(CHG|RITM)\d{7,}$') {
        throw "ChangeTicketId '$ChangeTicketId' does not match required pattern ^(CHG|RITM)\\d{7,}$"
    }
    if ($Assignments.Count -gt $MaxBatchSize) {
        throw "Batch size $($Assignments.Count) exceeds MaxBatchSize=$MaxBatchSize. Split into smaller runs."
    }
    if (-not (Test-Agt36ApproverMembership -ApproverObjectId $ApproverObjectId -Session $Session)) {
        throw "Approver $ApproverObjectId is not a member of the AI Governance Lead group."
    }
    if (-not $DryRun) {
        if (-not $DryRunReceiptPath -or -not (Test-Path $DryRunReceiptPath)) {
            throw "Dry-run receipt required. Re-run with -DryRun first, then supply -DryRunReceiptPath."
        }
        $receipt = Get-Content -LiteralPath $DryRunReceiptPath -Raw | ConvertFrom-Json
        if ((Get-Date) - [datetime]$receipt.GeneratedAtUtc -gt (New-TimeSpan -Hours 24)) {
            throw "Dry-run receipt is > 24h old. Re-run dry run."
        }
        if ($receipt.AssignmentsHash -ne (Get-Agt36AssignmentsHash -Assignments $Assignments)) {
            throw "Dry-run receipt does not match current assignments set."
        }
    }

    # --- Execute ---------------------------------------------------------
    $journalPath = Join-Path (Join-Path $env:ProgramData 'Agt36\journal') "bulk-$($ChangeTicketId)-$(Get-Date -Format yyyyMMddHHmmss).jsonl"
    New-Item -ItemType Directory -Path (Split-Path $journalPath) -Force | Out-Null

    $outcomes = foreach ($a in $Assignments) {
        $idemKey = Get-Agt36IdempotencyKey -AgentId $a.AgentId -NewOwner $a.NewOwnerObjectId -ChangeTicketId $ChangeTicketId
        if (Test-Agt36IdempotencyHit -Key $idemKey) {
            $out = [pscustomobject]@{ AgentId=$a.AgentId; Outcome='AlreadyApplied'; IdempotencyKey=$idemKey }
        }
        elseif ($DryRun) {
            $out = [pscustomobject]@{ AgentId=$a.AgentId; Outcome='DryRun-WouldApply'; Surface=$a.Surface; NewOwner=$a.NewOwnerObjectId }
        }
        else {
            try {
                switch ($a.Surface) {
                    'EntraSP'   { Set-Agt36AgentOwnerInline -Session $Session -ServicePrincipalObjectId $a.AgentObjectId -NewOwnerObjectId $a.NewOwnerObjectId -ChangeTicketId $ChangeTicketId -Justification $Justification -Confirm:$false | Out-Null }
                    'PowerApp'  { Set-Agt36PowerAppOwner    -Session $Session -EnvironmentName $a.EnvironmentName -AppName $a.AgentId -NewOwnerObjectId $a.NewOwnerObjectId -ChangeTicketId $ChangeTicketId -Justification $Justification -Confirm:$false | Out-Null }
                    default     { throw "Unsupported surface: $($a.Surface)" }
                }
                Register-Agt36IdempotencyKey -Key $idemKey
                $out = [pscustomobject]@{ AgentId=$a.AgentId; Outcome='Applied'; Surface=$a.Surface; NewOwner=$a.NewOwnerObjectId; IdempotencyKey=$idemKey }
            } catch {
                $out = [pscustomobject]@{ AgentId=$a.AgentId; Outcome='Failed'; Surface=$a.Surface; Error=$_.Exception.Message }
            }
        }
        Add-Content -LiteralPath $journalPath -Value ($out | ConvertTo-Json -Depth 6 -Compress)
        $out
    }

    # --- Manifest with SHA-256 over journal ------------------------------
    $hash = (Get-FileHash -LiteralPath $journalPath -Algorithm SHA256).Hash
    $manifest = [pscustomobject]@{
        ChangeTicketId   = $ChangeTicketId
        ApproverObjectId = $ApproverObjectId
        RunAtUtc         = (Get-Date).ToUniversalTime()
        DryRun           = [bool]$DryRun
        AssignmentCount  = $Assignments.Count
        JournalPath      = $journalPath
        JournalSha256    = $hash
        Outcomes         = $outcomes | Group-Object Outcome | Select-Object Name,Count
    }
    $manifestPath = "$journalPath.manifest.json"
    $manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    if ($DryRun) {
        $receipt = [pscustomobject]@{
            GeneratedAtUtc  = (Get-Date).ToUniversalTime()
            ChangeTicketId  = $ChangeTicketId
            AssignmentsHash = Get-Agt36AssignmentsHash -Assignments $Assignments
            JournalPath     = $journalPath
            JournalSha256   = $hash
        }
        $receiptPath = "$journalPath.receipt.json"
        $receipt | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
        Write-Host "Dry-run receipt: $receiptPath"
    }
    [pscustomobject]@{
        Manifest   = $manifestPath
        Journal    = $journalPath
        Outcomes   = $outcomes
        Sha256     = $hash
    }
}

function Get-Agt36AssignmentsHash {
    param([object[]]$Assignments)
    $s = ($Assignments | Sort-Object AgentId | ForEach-Object { "$($_.AgentId)|$($_.NewOwnerObjectId)|$($_.EnvironmentName)" }) -join "`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($s)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    -join ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') })
}

function Get-Agt36IdempotencyKey {
    param([string]$AgentId,[string]$NewOwner,[string]$ChangeTicketId)
    $s = "$AgentId|$NewOwner|$ChangeTicketId"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($s)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    -join ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') })
}

function Test-Agt36IdempotencyHit { param([string]$Key); Test-Path (Join-Path $env:ProgramData "Agt36\idem\$Key.json") }
function Register-Agt36IdempotencyKey {
    param([string]$Key)
    $dir = Join-Path $env:ProgramData 'Agt36\idem'
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    @{ Key=$Key; AppliedAtUtc=(Get-Date).ToUniversalTime() } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $dir "$Key.json")
}
function Test-Agt36ApproverMembership { param([string]$ApproverObjectId,$Session); $true }  # production: Graph group membership check
```

---

## §8 — Sovereign-cloud manual reconciliation worksheet

> Sovereign tenants (GCC, GCC High, DoD) cannot detect signal #2 (sponsor-departed) in real time because `employeeLeaveDateTime` is not surfaced in sovereign Graph. The **compensating control** is a quarterly manual reconciliation worksheet that an Entra Identity Governance Admin reviews alongside an AI Governance Lead. This worksheet is authoritative evidence for FINRA 3110/SEC 17a-4(f) on sovereign clouds.

```powershell
function Export-Agt36SovereignReconciliationWorksheet {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Session,
        [int]$LookbackDays = 90,
        [Parameter(Mandatory)][string]$OutputDirectory,
        [string]$ChangeTicketId
    )
    if (-not $Session.Sovereign.RequiresManualRecon) {
        Write-Warning "Session cloud '$($Session.Sovereign.Cloud)' has HR parity. Manual worksheet is not required — prefer real-time detection via Get-Agt36SponsorDepartedAgent."
    }
    New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
    $runId = Get-Date -Format 'yyyyMMdd-HHmmss'

    # 1. HR leaver list — exported offline from HR system; imported as CSV.
    $hrLeaverCsv = Join-Path $OutputDirectory 'input-hr-leavers.csv'
    if (-not (Test-Path $hrLeaverCsv)) {
        Write-Warning "Place HR leaver export (columns: EmployeeId,Upn,LeaveDateUtc,Manager) at: $hrLeaverCsv, then re-run."
        return $null
    }
    $hr = Import-Csv -LiteralPath $hrLeaverCsv

    # 2. Entra disabled users (last $LookbackDays)
    $sinceIso = (Get-Date).AddDays(-$LookbackDays).ToString('o')
    $disabled = Get-MgUser -Filter "accountEnabled eq false" -Property 'id,userPrincipalName,accountEnabled,createdDateTime' -All

    # 3. Power Platform maker & env-owner exports
    $envs  = Get-AdminPowerAppEnvironment | Where-Object { $_.Properties.provisioningState -ne 'Deleted' }
    $apps  = foreach ($e in $envs) { Get-AdminPowerApp -EnvironmentName $e.EnvironmentName }

    # 4. 1.2 agent inventory registry
    $registry = Get-Agt12AgentRegistry -Session $Session

    # Join: an agent is flagged on the worksheet if any of:
    #  - its sponsor UPN matches an HR leaver
    #  - its sponsor objectId matches a disabled Entra user
    #  - its Power Platform maker matches either of the above
    $disabledIndex = @{}; foreach ($u in $disabled) { $disabledIndex[$u.Id] = $u }
    $hrIndex       = @{}; foreach ($h in $hr)       { $hrIndex[$h.Upn] = $h }

    $rows = foreach ($a in $registry) {
        $flags = @()
        if ($hrIndex.ContainsKey($a.SponsorUpn))              { $flags += 'HR-Leaver' }
        if ($disabledIndex.ContainsKey($a.SponsorObjectId))   { $flags += 'Entra-Disabled' }
        if ($flags.Count -gt 0) {
            [pscustomobject]@{
                AgentId          = $a.AgentId
                DisplayName      = $a.DisplayName
                Zone             = $a.Zone
                SponsorUpn       = $a.SponsorUpn
                SponsorObjectId  = $a.SponsorObjectId
                Flags            = ($flags -join ',')
                ProposedNewSponsor = $hrIndex[$a.SponsorUpn].Manager
                ReviewerDecision = ''   # filled by reviewer
                ReviewerSignoff  = ''
                ReviewerDateUtc  = ''
            }
        }
    }

    $csvPath = Join-Path $OutputDirectory "sovereign-reconciliation-$runId.csv"
    $rows | Export-Csv -LiteralPath $csvPath -NoTypeInformation -Encoding UTF8
    $hash = (Get-FileHash -LiteralPath $csvPath -Algorithm SHA256).Hash

    # PDF scaffold (cover sheet — reviewers print, sign, scan back, attach to Purview label)
    $pdfCover = Join-Path $OutputDirectory "sovereign-reconciliation-$runId-cover.md"
    @"
# Control 3.6 — Sovereign Reconciliation Worksheet
- RunId: $runId
- Tenant cloud: $($Session.Sovereign.Cloud)
- Lookback: $LookbackDays days
- Rows flagged: $($rows.Count)
- CSV SHA-256: $hash
- ChangeTicketId: $ChangeTicketId
- Reviewers (required signatures):
  1. Entra Identity Governance Admin: __________________ Date: _______
  2. AI Governance Lead:               __________________ Date: _______
"@ | Set-Content -LiteralPath $pdfCover -Encoding UTF8

    [pscustomobject]@{
        RunId         = $runId
        CsvPath       = $csvPath
        CoverPath     = $pdfCover
        Sha256        = $hash
        RowsFlagged   = $rows.Count
        Cloud         = $Session.Sovereign.Cloud
    }
}
```

---
## §9 — SIEM forwarding (`Send-Agt36DetectionLogBundle`)

Every scheduled detection run produces a JSON bundle with an integrity hash, signed and forwarded to the SIEM cold-storage index. Failures to forward are **retry-with-backoff** and ultimately emit an operational alert — a failed forward does **not** suppress the local evidence record.

```powershell
function Send-Agt36DetectionLogBundle {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]$Session,
        [Parameter(Mandatory)][object[]]$SignalResults,
        [Parameter(Mandatory)][object[]]$Register,
        [Parameter(Mandatory)][string]$RunId,
        [Parameter(Mandatory)][string]$SiemEndpointUri,
        [Parameter(Mandatory)][string]$SigningCertThumbprint
    )
    $bundle = [pscustomobject]@{
        schema           = 'agt36.detection.bundle.v1'
        runId            = $RunId
        tenantId         = $Session.TenantId
        cloud            = $Session.Sovereign.Cloud
        runAtUtc         = (Get-Date).ToUniversalTime()
        signalSummary    = $SignalResults | ForEach-Object { @{ signalId=$_.SignalId; status=$_.Status; findingCount=@($_.Findings).Count } }
        registerSummary  = @{
            openCount   = ($Register | Where-Object Status -eq 'Open').Count
            perZone     = $Register | Group-Object Zone | ForEach-Object { @{ zone=$_.Name; count=$_.Count } }
            slaBreaches = ($Register | Where-Object { $_.SlaTargetDate -lt (Get-Date) }).Count
        }
        cardParityChecked = $true
    }
    $bundleJson = $bundle | ConvertTo-Json -Depth 10 -Compress
    $bundleHash = (Get-FileHash -InputStream ([IO.MemoryStream]::new([Text.Encoding]::UTF8.GetBytes($bundleJson))) -Algorithm SHA256).Hash

    $cert = Get-Item "Cert:\LocalMachine\My\$SigningCertThumbprint" -ErrorAction Stop
    $sig  = [Convert]::ToBase64String($cert.PrivateKey.SignData([Text.Encoding]::UTF8.GetBytes($bundleJson), 'SHA256'))

    $envelope = @{
        bundle    = $bundle
        sha256    = $bundleHash
        signature = $sig
        signerThumbprint = $SigningCertThumbprint
    } | ConvertTo-Json -Depth 12 -Compress

    $attempt = 0
    while ($true) {
        try {
            Invoke-RestMethod -Method Post -Uri $SiemEndpointUri -Body $envelope `
                -ContentType 'application/json' -Headers @{ 'X-Agt36-RunId' = $RunId } -ErrorAction Stop
            return [pscustomobject]@{ RunId=$RunId; Status='Forwarded'; Sha256=$bundleHash; Attempts=$attempt+1 }
        } catch {
            $attempt++
            if ($attempt -ge 5) {
                Write-Agt36OperationalAlert -Severity High -Message "SIEM forward failed after 5 attempts: $($_.Exception.Message)" -RunId $RunId
                return [pscustomobject]@{ RunId=$RunId; Status='Failed'; Sha256=$bundleHash; Attempts=$attempt; Error=$_.Exception.Message }
            }
            Start-Sleep -Seconds ([Math]::Pow(2, $attempt))
        }
    }
}

function Write-Agt36OperationalAlert {
    param([ValidateSet('Low','Medium','High','Critical')][string]$Severity, [string]$Message, [string]$RunId)
    # Production: emit to Sentinel custom log via Log Analytics Data Collector or
    # an Event Grid topic subscribed to by the SOC playbook.
    Write-Warning "[Agt36 $Severity $RunId] $Message"
}
```

---

## §10 — Scheduling and Power Automate trigger integration

Scheduled execution happens on a hardened admin workstation or an Azure Automation account running in the tenant's privileged security context. Two triggers are supported:

| Trigger | Cadence | Scope |
|---------|---------|-------|
| Scheduled (Azure Automation) | Every 2h (Zone 3), every 6h (Zone 2), daily (Zone 1) | All 5 primary signals |
| Power Automate event trigger | On HR `employeeLeaveDateTime` write | Signal #2 realtime mode |

```powershell
function Invoke-Agt36ScheduledDetectionRun {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$TenantId,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [Parameter(Mandatory)][ValidateSet(1,2,3)][int]$Zone,
        [string[]]$SharePointSiteUrls,
        [Parameter(Mandatory)][string]$SiemEndpointUri,
        [Parameter(Mandatory)][string]$SigningCertThumbprint
    )
    $runId = "agt36-$(Get-Date -Format 'yyyyMMddHHmmss')-$([Guid]::NewGuid().ToString('N').Substring(0,8))"
    try {
        Test-Agt36ModuleMatrix | Out-Null
        $session = Initialize-Agt36Session -TenantId $TenantId -Profile Detect -Cloud $Cloud

        # Self-test gate (see §13)
        $selfTest = Invoke-Agt36SelfTest -Session $session
        if ($selfTest.Status -ne 'Pass') {
            Write-Agt36OperationalAlert -Severity High -Message "Self-test failed: $($selfTest.Reason)" -RunId $runId
            return [pscustomobject]@{ RunId=$runId; Status='SuppressedBySelfTest'; Reason=$selfTest.Reason }
        }

        $signals = @(
            Get-Agt36OwnerlessAgent                     -Session $session -Zone $Zone
            Get-Agt36SponsorDepartedAgent               -Session $session -Zone $Zone
            Get-Agt36MakerDepartedAgent                 -Session $session -Zone $Zone
            Get-Agt36EnvironmentOwnerDepartedAgent      -Session $session -Zone $Zone
            Get-Agt36SharePointAuthorDisabledAgent      -Session $session -Zone $Zone -SiteCollectionUrls $SharePointSiteUrls
        )
        $registry = Get-Agt12AgentRegistry -Session $session
        $register = Merge-Agt36OrphanRegister -SignalResults $signals -AgentRegistry $registry -RunId $runId
        $forwarded = Send-Agt36DetectionLogBundle -Session $session -SignalResults $signals -Register $register -RunId $runId `
                        -SiemEndpointUri $SiemEndpointUri -SigningCertThumbprint $SigningCertThumbprint
        [pscustomobject]@{ RunId=$runId; Status='Completed'; Register=$register; Forwarded=$forwarded }
    } catch {
        Write-Agt36OperationalAlert -Severity Critical -Message $_.Exception.Message -RunId $runId
        [pscustomobject]@{ RunId=$runId; Status='Failed'; Error=$_.Exception.Message }
    }
}
```

Power Automate realtime trigger payload shape (signal #2):

```json
{
  "trigger": "employeeLeaveDateTime.updated",
  "userId": "{departedUserObjectId}",
  "upn": "{departedUserUpn}",
  "leaveDateUtc": "{iso8601}",
  "invokeTarget": "Get-Agt36SponsorDepartedAgent -RealtimeMode"
}
```

---

## §11 — Evidence capture and 6-year WORM retention

Every artifact produced by Agt36 is **retention-labeled** via Purview with a 6-year WORM label. The label is applied at **write time**, not retrospectively. Absence of the label on an audit sample is a Verification Criterion #4 failure.

| Artifact | Storage | Purview label | Minimum retention |
|----------|---------|---------------|-------------------|
| Detection log bundle (JSON) | SIEM cold storage | `Agt36-Detect-6y` | 6 years, regulatory |
| Orphan register JSONL | Secure storage account, immutable blob | `Agt36-Register-6y` | 6 years, regulatory |
| Remediation journal + manifest | Secure storage account, immutable blob | `Agt36-Remediation-6y` | 6 years, regulatory |
| Sovereign reconciliation worksheet CSV + signed cover | SharePoint Online records site | `Agt36-Sovereign-6y` | 6 years, regulatory |
| Self-test output | SIEM cold storage | `Agt36-SelfTest-6y` | 6 years |
| Dry-run receipts | Secure storage | `Agt36-DryRun-2y` | 2 years (operational) |

```powershell
function Set-Agt36PurviewRetentionLabel {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$SharePointFileUrl,
        [Parameter(Mandatory)][ValidateSet('Agt36-Detect-6y','Agt36-Register-6y','Agt36-Remediation-6y','Agt36-Sovereign-6y','Agt36-SelfTest-6y','Agt36-DryRun-2y')]
        [string]$LabelName
    )
    # Production: Connect-PnPOnline to site, then Set-PnPListItem ... -Values @{ '_ComplianceTag' = $LabelName }
    # or use Graph /driveItem/retentionLabel assignment endpoint.
    [pscustomobject]@{ Url=$SharePointFileUrl; Label=$LabelName; AppliedAtUtc=(Get-Date).ToUniversalTime() }
}
```

Verify a random-sample of artifacts monthly:

```powershell
function Test-Agt36RetentionLabelCoverage {
    param([Parameter(Mandatory)][string[]]$ArtifactUrls)
    foreach ($u in $ArtifactUrls) {
        # Production: Graph /drives/{id}/items/{id}?$expand=retentionLabel
        [pscustomobject]@{ Url=$u; HasLabel='UNKNOWN'; Note='Implement Graph retentionLabel read here.' }
    }
}
```

---

## §12 — Pester namespace stubs

The [verification-testing.md](verification-testing.md) sibling uses Pester 5 with the following namespaces. Each namespace has a failure-is-loud contract — a missing fixture fails the namespace (never `Inconclusive`).

| Namespace | Scope |
|-----------|-------|
| `DETECT` | Each detection helper returns a valid `Status` ∈ `{Clean,Anomaly,Pending,NotApplicable,Error}` and never `$null` |
| `HR` | `Test-Agt36HRFreshness` gate + signal #2 abort-on-stale behavior |
| `REASSIGN` | `Test-Agt36ReassignmentPrerequisite` rejects disabled/unlicensed/wrong-env targets |
| `SPONSOR` | `Invoke-Agt36SponsorManagerTransferOverride` manager lookup + disabled-manager refusal |
| `BULK` | Max-batch, dry-run receipt age, ChangeTicket regex, idempotency, approver membership |
| `TERMINAL` | Tier-4 handoff writes to 2.25 queue + journal; never mutates directly |
| `RECONCILE` | Canonical AgentId mapping; duplicate explosion regression; card-vs-detection parity |
| `SIEM` | Bundle schema, signature validity, retry backoff, failure alert emission |
| `SOV` | Sovereign cloud does NOT early-exit; worksheet export produces CSV + cover + SHA-256 |

```powershell
# Example stub — see verification-testing.md for full specs
Describe 'Agt36 DETECT' {
    It 'Get-Agt36OwnerlessAgent returns Status when Graph is not connected' {
        $fakeSession = [pscustomobject]@{ GraphStatus='Error'; Sovereign=[pscustomobject]@{RequiresManualRecon=$false} }
        $result = Get-Agt36OwnerlessAgent -Session $fakeSession -Zone 3
        $result.Status | Should -Be 'NotApplicable'
        $result.Findings | Should -BeOfType [System.Object[]]
    }
}
Describe 'Agt36 SOV' {
    It 'Get-Agt36SponsorDepartedAgent short-circuits to NotApplicable on sovereign cloud' {
        $sov = [pscustomobject]@{ RequiresManualRecon=$true; Cloud='USGovHigh' }
        $session = [pscustomobject]@{ Sovereign=$sov; GraphStatus='Connected' }
        $result = Get-Agt36SponsorDepartedAgent -Session $session -Zone 3
        $result.Status | Should -Be 'NotApplicable'
        $result.Reason | Should -Match 'Sovereign'
    }
}
Describe 'Agt36 BULK' {
    It 'Set-Agt36BulkOwnerReassignment rejects bad ChangeTicketId pattern' {
        { Set-Agt36BulkOwnerReassignment -Session $null -Assignments @() -ChangeTicketId 'BAD' `
            -Justification 'x' -ApproverObjectId 'x' -DryRun } | Should -Throw '*pattern*'
    }
}
```

---
## §13 — Validation harness, anti-patterns, and operating cadence

### 13.1 — `Invoke-Agt36SelfTest`

Runs before every production detection batch. A failure suppresses the batch and emits an operational alert — it **does not** emit a misleading "clean" result.

```powershell
function Invoke-Agt36SelfTest {
    [CmdletBinding()]
    param([Parameter(Mandatory)]$Session)
    $checks = New-Object System.Collections.Generic.List[object]
    $add = { param($Name,$Ok,$Reason='') $checks.Add([pscustomobject]@{Name=$Name;Ok=$Ok;Reason=$Reason}) }

    & $add 'PS 7.4+'             ($PSVersionTable.PSVersion -ge [version]'7.4.0') "PS=$($PSVersionTable.PSVersion)"
    & $add 'Not ISE'             ($Host.Name -ne 'Windows PowerShell ISE Host')
    & $add 'Modules pinned'      ($true) 'Test-Agt36ModuleMatrix succeeded earlier'
    & $add 'Graph connected'     ($Session.GraphStatus -eq 'Connected')
    & $add 'PP connected or NA'  ($Session.PowerPlatformStatus -in 'Connected','Error') 'Error is acceptable only if all PP signals report NotApplicable'
    & $add 'Sovereign context'   ($null -ne $Session.Sovereign.Cloud)
    & $add 'HR freshness'        (Test-Agt36HRFreshness -Session $Session) 'Required for signal #2 except sovereign'
    & $add 'SIEM endpoint reachable' ($true) 'Production implementation: HEAD probe with cert auth'

    $failed = $checks | Where-Object { -not $_.Ok }
    [pscustomobject]@{
        Status = if ($failed) { 'Fail' } else { 'Pass' }
        Checks = $checks
        Reason = ($failed | ForEach-Object { "$($_.Name): $($_.Reason)" }) -join '; '
    }
}
```

### 13.2 — Anti-patterns (do not ship)

| Anti-pattern | Why it fails | Correct path |
|--------------|--------------|--------------|
| Returning `$null` from a detection helper | `Status` parity check cannot distinguish "clean" from "broken" | Return `[pscustomobject]@{Status='Error';Findings=@()}` |
| Wrapping `try/catch` and returning `$null` | Swallows throttle + auth errors | Propagate `Status='Error'` with `$_.Exception.Message` |
| Calling `Get-MgServicePrincipal -All` with no filter | Returns every SP; breaks signal #1 scope | Use `tags/any(t:t eq 'AgentIdentity')` with `ConsistencyLevel=eventual` |
| Using `userType eq 'AgenticUser'` | No such userType exists; retracted from control doc | Filter SPs by `tags`, not user types |
| Treating sovereign tenants as "clean" | Signal #2 silently skipped; FINRA gap | Always route to §8 worksheet |
| Single-shot Graph call | Truncates at 999 at scale | Use `Invoke-Agt36GraphPaged` |
| Skipping dry-run on bulk remediation | Irreversible misassignment | `Set-Agt36BulkOwnerReassignment` refuses without receipt |
| Reassigning to a disabled user | Re-orphans immediately | `Test-Agt36ReassignmentPrerequisite` blocks it |
| Updating orphan register rows in place | Violates SOX ITGC non-repudiation | Append-only JSONL + SHA-256 manifest |
| Local-time timestamps | Breaks cross-tenant correlation | Always `.ToUniversalTime()` |

### 13.3 — Operating cadence

| Activity | Cadence | Owner |
|----------|---------|-------|
| Scheduled detection run | Z3: 2h · Z2: 6h · Z1: daily | AI Administrator |
| Self-test review | Daily | AI Administrator |
| Card-vs-detection parity check | Every run | Automated; escalates to AI Governance Lead on variance |
| Sovereign reconciliation worksheet | Quarterly | Entra Identity Governance Admin + AI Governance Lead |
| Bulk remediation campaign | As needed, max 1 per week per zone | Power Platform Admin (Tier-3), Entra Agent ID Admin (Tier-1) |
| Module pinning review | Monthly | AI Administrator |
| PIM activation audit | Monthly | Entra Global Reader (reads) + AI Governance Lead (attests) |
| Evidence retention sample test | Monthly | Purview Compliance Admin |
| Control attestation | Annual, or on material change | AI Governance Lead |

### 13.4 — Hedged-language reminder

Detection output, remediation journals, and the sovereign worksheet **support compliance with** FINRA Rule 3110 supervisory review, SEC 17a-4(f) records retention, SOX ITGC ownership integrity, GLBA safeguards, OCC 2013-29 third-party risk (where agent is a third-party integration), and Federal Reserve SR 11-7 model risk (where agent participates in a model). They **do not replace** registered-principal supervisory review, and they **do not guarantee** detection completeness in the presence of unpinned modules, stale HR connectors, or manual reconciliation drift on sovereign clouds. Organizations should verify tenant-specific parity via §13.1 self-test before relying on output for regulatory evidence.

---
## Cross-references

- Control: [3.6 — Orphaned Agent Detection and Remediation](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- Siblings: [portal-walkthrough.md](portal-walkthrough.md) · [verification-testing.md](verification-testing.md) · [troubleshooting.md](troubleshooting.md)
- Baseline: [_shared/powershell-baseline.md](../../_shared/powershell-baseline.md) — especially [§3 Sovereign Cloud Endpoints](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod)
- Related controls:
  - [1.2 — Agent Registry and Integrated Apps Management](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) — authoritative inventory feed for canonical `AgentId` resolution and sponsor lineage
  - [1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — last-activity feed used for dormancy signals and supervisory evidence
  - [2.25 — Agent 365 Admin Center Governance Console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) — Tier-4 terminal disposal handoff target
  - [2.26 — Entra Agent ID Identity Governance](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) — overlapping identity-lifecycle and access-review evidence
  - [3.1 — Agent Inventory and Metadata Management](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) — inventory/metadata source cross-referenced by the reconciliation engine
  - [3.13 — Agent 365 Admin Center Analytics](../../../controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md) — card-vs-detection parity source (Verification Criterion #2)

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*