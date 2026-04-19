# Control 1.19 — PowerShell Setup: eDiscovery for Agent Interactions

> **Scope.** This playbook is the canonical PowerShell automation reference for Control 1.19 — *eDiscovery for Agent Interactions*. It exercises the **unified eDiscovery experience** in Microsoft Purview through the **Microsoft Graph eDiscovery API** (`Microsoft.Graph.Security`) — case creation, custodian and location-source assignment, KeyQL-based search with the **Copilot interactions** scope, the **legal hold** preservation primitive, review-set add and analytics, defensible review-set export, and Unified Audit Log corroboration via `Search-UnifiedAuditLog`. It supports US financial-services tenants in the Microsoft Commercial, GCC, GCC High, and DoD clouds.
>
> **Companion documents.**
>
> - Control specification — `docs/controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`
> - Portal walkthrough — `./portal-walkthrough.md`
> - Verification & testing — `./verification-testing.md`
> - Troubleshooting — `./troubleshooting.md`
> - Shared baseline — `docs/playbooks/_shared/powershell-baseline.md`
>
> **Important regulatory framing.** Nothing in this playbook *guarantees* regulatory compliance. The cmdlets and patterns below *support* control objectives required by FINRA Rules 4511 and 3110, FINRA Regulatory Notice 25-07 (March 2025), FINRA Rule 8210, SEC Rule 17a-4(b)(4) and 17a-4(f) (October 2022 audit-trail amendment), SOX §802, GLBA §501(b), OCC Bulletin 2011-12, Federal Reserve SR 11-7, FRCP 37(e), and NIST SP 800-53 AU-11 / SI-12. Implementation requires that organizations validate every script against their own change-management, model-risk, supervisory-review, and books-and-records processes before production rollout.
>
> **Latency reality (do not overclaim).** The unified eDiscovery experience does not provide synchronous preservation. Microsoft does not publish a hard SLA for new content to become searchable inside an eDiscovery case; new Copilot interactions can take from minutes to hours to be indexed and to fall under the scope of a previously-created search. **Hold attachment, however, is effective at the time the legal-hold resource is created against a custodian source** — preservation is what defends the duty under FRCP 37(e), not searchability.

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), and SHA-256 evidence emission. Snippets below may show abbreviated patterns; the baseline is authoritative when the two diverge.

!!! danger "Classic eDiscovery retired 31 August 2025"
    Microsoft retired the classic Standard and classic Premium / Advanced eDiscovery experiences on **31 August 2025** for every cloud except 21Vianet (China). The IPPS cmdlets that authored those experiences — `New-ComplianceCase -CaseType "AdvancedEdiscovery"`, `New-ComplianceSearch`, `Start-ComplianceSearch`, `New-ComplianceSearchAction -Action Export`, `New-CaseHoldPolicy` + `New-CaseHoldRule` — are **not** the authoring surface for new cases. The unified eDiscovery experience is exposed in three ways: the Microsoft Purview portal, the **Microsoft Graph eDiscovery API** (`/security/cases/ediscoveryCases` — the canonical PowerShell control plane), and a small set of read-only IPPS noun-equivalents that continue to function for transitional cases. This playbook is **Graph-first**.

---

## 0. Wrong-shell trap (READ FIRST)

Control 1.19 spans **three** PowerShell surfaces. Choosing the wrong one (or invoking the right one without sovereign-cloud parameters) produces silent false-clean evidence — empty case lists, holds that bind to nothing, exports with zero items, audit pulls truncated at 5 000 rows — that will not survive supervisory testing under FINRA Rule 4511 / SEC Rule 17a-4(b)(4) / FRCP 37(e).

| Surface | Connect cmdlet | Module(s) | What it covers in 1.19 |
|---|---|---|---|
| **Microsoft Graph eDiscovery API** | `Connect-MgGraph` | `Microsoft.Graph.Authentication`, `Microsoft.Graph.Security`, `Microsoft.Graph.Users`, `Microsoft.Graph.Sites` | **Canonical authoring surface.** Cases, custodians, custodian user / site sources, non-custodial sources, searches, legal holds, review sets, review-set queries, tags, exports, async-operation polling. |
| **Microsoft 365 Unified Audit (IPPS)** | `Connect-IPPSSession` | `ExchangeOnlineManagement` v3.5+ | Paged retrieval of `Discovery` (`RecordType` 28) and `AeD` (`RecordType` 54) audit records — *who created what case, who applied which hold, which export was downloaded, by whom, when*. Also used for `Get-RoleGroupMember` Purview eDiscovery role-group checks. |
| **Microsoft Purview portal** | n/a | n/a | Some artefacts remain portal-only as of April 2026: case templates, certain reviewer-set tag policies, and the human-workflow custodian hold-notice acknowledgement page. PowerShell can read state for evidence joining; it does not author these artefacts. |

> **There is no `New-MgSecurityCase` cmdlet.** This is the most common author trap on this control. The Graph noun is `MgSecurityCaseEdiscoveryCase` — the parent `case` resource is a container; the eDiscovery-specific resource is what you create. Use `New-MgSecurityCaseEdiscoveryCase`. Verify with `Get-Command -Module Microsoft.Graph.Security -Noun *Ediscovery* | Sort-Object Name`.

> **A search is not a hold.** `New-MgSecurityCaseEdiscoveryCaseSearch` performs *discovery*; it does **not** preserve. The duty-to-preserve under FRCP 37(e) and FINRA 25-07 is met by a `legalHold` resource on the case (§6) bound to per-custodian `legalHoldUserSource` and per-site `legalHoldSiteSource` rows. Treating a search as preservation is the spoliation pattern that drew sanctions in *Zubulake v. UBS Warburg LLC*, 220 F.R.D. 212 (S.D.N.Y. 2003) — and it remains the most common implementation defect in supervisory testing.

> **Microsoft has revised the `Microsoft.Graph.Security` cmdlet noun bindings between 2.x minor versions.** Re-verify the exact noun and parameter names of every `*-MgSecurityCaseEdiscoveryCase*` cmdlet against `Get-Help` and `Get-Command` in your CAB-pinned module version before relying on a literal in a runbook. Where a typed cmdlet is missing or renamed, fall back to `Invoke-MgGraphRequest` against the documented Graph endpoint — never fall back to the retired `New-Compliance*` IPPS path.

### 0.1 The five most common false-clean defects (do not ship without all five guards)

| Defect | Symptom | Guard |
|---|---|---|
| Calling `New-ComplianceCase -CaseType "AdvancedEdiscovery"` after 31 Aug 2025 | Cmdlet either errors out or silently creates a transitional shim that the new portal cannot finish processing; SEC 17a-4 production fails | §3 uses `New-MgSecurityCaseEdiscoveryCase`. The retired cmdlet appears in §13 anti-pattern row 1 only. |
| `Connect-IPPSSession` with no `-ConnectionUri` in GCC High / DoD | Authenticates against commercial endpoints; returns zero records; audit pull looks clean but is empty in the sovereign tenant | §2 bootstrap branches `IPPSConnectionUri` per cloud. Never call `Connect-IPPSSession` bare in a sovereign tenant. |
| `Connect-MgGraph` with no `-Environment` in GCC High / DoD | Wrong tenant ring; zero cases visible; mutations target the commercial directory or fail with `Forbidden` | §2 bootstrap branches `GraphEnvironment` per cloud (`USGov` / `USGovDoD`). |
| Content Search treated as preservation | Search returns hits; custodian deletes the Copilot chat; re-search returns zero; spoliation under FRCP 37(e) | §6 creates a `legalHold` and binds `legalHoldUserSource` per custodian *before* §5 search runs. §11 check 2 hard-fails if any custodian lacks an enabled hold. |
| KeyQL `kind:microsoftteams AND from:"Copilot"` for Copilot scope | Copilot interactions are not Teams chat items with author "Copilot"; they live in the substrate mailbox under a hidden `Copilot Chats` folder; search returns zero | §5 uses `kind:CopilotInteraction` (the canonical Copilot location class) and binds the custodian *mailbox* source — that is what brings Copilot conversations into scope. |

### 0.2 PowerShell edition guard

This playbook standardises on **PowerShell 7.4 LTS**. Every cmdlet referenced is Core-compatible. Standardising on a single edition removes a class of cross-edition serialisation bugs (`ConvertTo-Json -Depth` differences, `Invoke-RestMethod` body-handling differences on Windows PowerShell 5.1) that have historically corrupted evidence packs.

```powershell
#Requires -Version 7.4
#Requires -PSEdition Core

if ($PSVersionTable.PSEdition -ne 'Core') {
    throw "Control 1.19 automation targets PowerShell 7.4+ (Core). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
}
if ($PSVersionTable.PSVersion -lt [version]'7.4.0') {
    throw "PowerShell 7.4.0 or later required. Detected: $($PSVersionTable.PSVersion)."
}
```

---

## 1. Module install and version pinning

Every module must be pinned to a CAB-approved version. The list below is the minimum surface for Control 1.19; record exact versions in your change ticket and substitute the version your CAB has approved. The illustrative pins shown are the framework's April 2026 baseline; **Microsoft revises the `Microsoft.Graph.*` cmdlet surface between 2.x minor versions** — re-verify every `*-MgSecurityCaseEdiscoveryCase*` noun against `Get-Help` in the pinned version before publishing the runbook.

```powershell
#Requires -Version 7.4
#Requires -PSEdition Core

$modules = @(
    @{ Name = 'Microsoft.Graph.Authentication'; RequiredVersion = '2.19.0' }
    @{ Name = 'Microsoft.Graph.Security';       RequiredVersion = '2.19.0' }
    @{ Name = 'Microsoft.Graph.Users';          RequiredVersion = '2.19.0' }
    @{ Name = 'Microsoft.Graph.Sites';          RequiredVersion = '2.19.0' }
    @{ Name = 'ExchangeOnlineManagement';       RequiredVersion = '3.5.0'  }
    # Az.Accounts / Az.Storage are required only when landing the §8 export package
    # to an Azure Storage container with an immutability policy lock (SEC 17a-4(f) WORM path).
    @{ Name = 'Az.Accounts';                    RequiredVersion = '2.15.0' }
    @{ Name = 'Az.Storage';                     RequiredVersion = '6.1.1'  }
)

foreach ($m in $modules) {
    if (-not (Get-Module -ListAvailable -Name $m.Name |
              Where-Object Version -EQ $m.RequiredVersion)) {
        Install-Module -Name $m.Name `
                       -RequiredVersion $m.RequiredVersion `
                       -Repository PSGallery `
                       -Scope CurrentUser `
                       -AllowClobber `
                       -AcceptLicense
    }
    Import-Module -Name $m.Name -RequiredVersion $m.RequiredVersion -Force
}
```

Treat `Install-Module ... -Force` *without* `-RequiredVersion` as an unacceptable shortcut in regulated tenants — it breaks reproducibility and will fail SOX §404 and OCC 2023-17 evidence requirements. The release-notes review for every pinned version is part of the change record.

### 1.1 Cmdlet status table — the wrong-cmdlet trap

The following table is the authoring guard for this control. Every cmdlet that existed under the classic Standard / Premium experiences has either been retired or replaced; copying a pre-2025 runbook into a 2026 change window is the most common cause of a silent eDiscovery failure.

| Cmdlet | Module | Status as of April 2026 | Use in 1.19? |
|---|---|---|---|
| `New-ComplianceCase -CaseType "AdvancedEdiscovery"` | `ExchangeOnlineManagement` (IPPS) | **Retired for new cases** — the `AdvancedEdiscovery` case type is gone. Some tenants may still create a transitional shim with `-CaseType "eDiscovery"`. | **No.** Anti-pattern row 1. |
| `New-ComplianceCase` (other case kinds — DSR, Insider Risk) | IPPS | Continues to function for non-eDiscovery case kinds. | Out of scope for 1.19. |
| `Get-ComplianceCase` | IPPS | Read-only enumeration of legacy / transitional cases. Continues to function. | **Read-only fallback only**, flagged as transitional. |
| `Add-ComplianceCaseMember` | IPPS | Tied to legacy case identity. | **No.** Use Graph case role assignment in §3. |
| `New-ComplianceSearch` | IPPS | Tied to classic Content Search and Standard eDiscovery. Content Search has been migrated into a system-generated case in unified eDiscovery. | **No.** Use `New-MgSecurityCaseEdiscoveryCaseSearch`. |
| `Start-ComplianceSearch` | IPPS | Replaced by the `estimateStatistics` action on the Graph search resource. | **No.** Use `Invoke-MgEstimateSecurityCaseEdiscoveryCaseSearchStatistics`. |
| `Get-ComplianceSearch` | IPPS | Read-only enumeration of legacy searches. | Read-only fallback only. |
| `New-ComplianceSearchAction -Action Export` | IPPS | Replaced by Graph review-set export. | **No.** Use `Export-MgSecurityCaseEdiscoveryCaseReviewSet`. |
| `New-CaseHoldPolicy` / `New-CaseHoldRule` | IPPS | Legacy *case hold policy + rule* model, replaced by the unified `legalHold` resource. | **No.** Use `New-MgSecurityCaseEdiscoveryCaseLegalHold`. |
| `Set-CaseHoldPolicy -Enabled $false` | IPPS | Continues for transitional case holds; the Graph release path is `Update-MgSecurityCaseEdiscoveryCaseLegalHold -IsEnabled $false`. | Transitional fallback only. |
| `Get-CaseHoldPolicy` | IPPS | Read-only verification of legacy / transitional holds. Useful in §11 cross-check during transition. | Read-only fallback. |
| `Search-UnifiedAuditLog` | `ExchangeOnlineManagement` | **Fully supported.** This is the only IPPS cmdlet in the *active* path of this rewrite — used in §9 audit-log integration with `SessionId` + `SessionCommand 'ReturnLargeSet'` paging. | **Yes — §9.** |
| `Get-RoleGroupMember 'eDiscovery Manager'` | `ExchangeOnlineManagement` | Verifies Purview eDiscovery role-group membership pre-flight. | **Yes — §2 role check.** |
| `New-MgSecurityCase` | `Microsoft.Graph.Security` | **Does not exist.** The Graph noun is `MgSecurityCaseEdiscoveryCase`. | **No** — author trap. |
| `New-MgSecurityCaseEdiscoveryCase` | `Microsoft.Graph.Security` | **Canonical case creator** — wraps `POST /security/cases/ediscoveryCases`. | **Yes — §3.** |
| `Get-MgSecurityCaseEdiscoveryCase` | `Microsoft.Graph.Security` | Read of a case (idempotency, validation). | Yes — §3 / §11. |
| `Update-MgSecurityCaseEdiscoveryCase` | `Microsoft.Graph.Security` | Patch case status / description. | Yes. |
| `Remove-MgSecurityCaseEdiscoveryCase` | `Microsoft.Graph.Security` | Deletes a case. High-impact. | Yes — gated, `ConfirmImpact='High'`. |
| `New-MgSecurityCaseEdiscoveryCaseCustodian` | `Microsoft.Graph.Security` | Add a custodian to the case. | **Yes — §4.** |
| `New-MgSecurityCaseEdiscoveryCaseCustodianUserSource` | `Microsoft.Graph.Security` | Map a custodian's mailbox / OneDrive (the implicit user-bound sources). | Yes — §4. |
| `New-MgSecurityCaseEdiscoveryCaseCustodianSiteSource` | `Microsoft.Graph.Security` | Add a SharePoint site source for a custodian. | Yes — §4. |
| `New-MgSecurityCaseEdiscoveryCaseNoncustodialDataSource` | `Microsoft.Graph.Security` | Non-custodial site / mailbox source attached to the case. | Yes — §4 for shared mailboxes / Teams channel files. |
| `New-MgSecurityCaseEdiscoveryCaseSearch` | `Microsoft.Graph.Security` | Create a search inside the case with KeyQL `contentQuery`. | **Yes — §5.** |
| `Update-MgSecurityCaseEdiscoveryCaseSearch` | `Microsoft.Graph.Security` | Patch query / sources. | Yes. |
| `Invoke-MgEstimateSecurityCaseEdiscoveryCaseSearchStatistics` | `Microsoft.Graph.Security` | Triggers the `estimateStatistics` action. | **Yes — §5.** |
| `New-MgSecurityCaseEdiscoveryCaseLegalHold` | `Microsoft.Graph.Security` | Create the unified `legalHold` resource on the case. | **Yes — §6.** |
| `Update-MgSecurityCaseEdiscoveryCaseLegalHold` | `Microsoft.Graph.Security` | Patch `isEnabled` / `contentQuery` (release path). | **Yes — §6.** |
| `New-MgSecurityCaseEdiscoveryCaseLegalHoldUserSource` | `Microsoft.Graph.Security` | Mailbox sources covered by the hold (covers Copilot substrate). | **Yes — §6.** |
| `New-MgSecurityCaseEdiscoveryCaseLegalHoldSiteSource` | `Microsoft.Graph.Security` | SharePoint site sources covered by the hold. | **Yes — §6.** |
| `New-MgSecurityCaseEdiscoveryCaseReviewSet` | `Microsoft.Graph.Security` | Create a review set in the case. | **Yes — §7.** |
| `Add-MgSecurityCaseEdiscoveryCaseSearchToReviewSet` | `Microsoft.Graph.Security` | Action `addToReviewSet` — moves search hits into a review set. | **Yes — §7.** |
| `New-MgSecurityCaseEdiscoveryCaseReviewSetQuery` | `Microsoft.Graph.Security` | Query within a review set (analytics). | Yes — §7. |
| `New-MgSecurityCaseEdiscoveryCaseTag` | `Microsoft.Graph.Security` | Reviewer tags (relevant / privileged / non-responsive). | Yes — §7. |
| `Update-MgSecurityCaseEdiscoveryCaseSettings` | `Microsoft.Graph.Security` | OCR / dedup / threading / near-dup toggles. | Yes — §7. |
| `Export-MgSecurityCaseEdiscoveryCaseReviewSet` | `Microsoft.Graph.Security` | Action `exportReviewSet` — generates the export package. | **Yes — §8.** |
| `Get-MgSecurityCaseEdiscoveryCaseOperation` | `Microsoft.Graph.Security` | Read async operation status — estimate, addToReviewSet, export are all long-running operations. | **Yes — §5 / §7 / §8 polling.** |

### 1.2 Graph delegated permissions required

| Scope | Why |
|---|---|
| `eDiscovery.Read.All` | Read cases, custodians, searches, holds, review sets |
| `eDiscovery.ReadWrite.All` | Mutate cases, holds, searches, exports |
| `User.Read.All` | Resolve custodian UPN → object ID for user-source attach |
| `Sites.Read.All` | Resolve SharePoint site sources |
| `AuditLog.Read.All` | §9 cross-check — Graph audit fallback when IPPS audit is unavailable |
| `Directory.Read.All` | §2 operator role-assignment check (Entra role display names) |

> **Application-only access to eDiscovery is restricted.** Several Graph eDiscovery operations require **delegated** permissions only. Run from a delegated context with an operator who holds an eDiscovery role group (eDiscovery Manager or eDiscovery Administrator). Service principals are not a substitute for an operator UPN in evidence attribution.

### 1.3 Purview eDiscovery role groups — pre-flight membership

| Role group | Why it must be checked in §2 |
|---|---|
| **eDiscovery Manager** | Default operator role; case-scoped. Required to create a case and act on cases the operator owns. |
| **eDiscovery Administrator** | Tenant-scoped superset; required to act on any case in the tenant and to **release holds**. Treat as super-user; assign sparingly and via Entra PIM. |
| **Reviewer** | Review-set view-only. Optional for the runtime path; required only if §11 reads tag state from a non-owner principal. |

---


## 2. Sovereign-aware bootstrap — `Initialize-Agt119Session`

`Initialize-Agt119Session` is the canonical entry point for every Control 1.19 runbook. It performs eight things in order:

1. Asserts PowerShell 7.4 Core (re-checks §0.2).
2. Resolves the sovereign cloud parameter set — Graph environment, IPPS connection URI, Azure environment.
3. Validates that the operator UPN exists in the directory.
4. Connects to Microsoft Graph with the §1.2 delegated scopes (or, where MFA is enforced, with `-UseDeviceAuthentication`).
5. Connects to IPPS for the §9 audit-log integration only.
6. Verifies operator membership in the **eDiscovery Manager** role group (or **eDiscovery Administrator** for hold-release operations).
7. Creates the evidence root for the session (`./evidence/1.19/<UTC stamp>/`) and emits a session manifest.
8. Returns a typed `[pscustomobject]` session context that downstream cmdlets accept on the pipeline.

`Initialize-Agt119Session` **does not mutate tenant state**. It is safe to run in a dry-run pipeline against any cloud.

```powershell
function Initialize-Agt119Session {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
        [string] $Cloud,

        [Parameter(Mandatory)]
        [ValidatePattern('^[^@\s]+@[^@\s]+\.[^@\s]+$')]
        [string] $OperatorUpn,

        [Parameter(Mandatory)]
        [ValidatePattern('^[A-Za-z0-9-]{4,64}$')]
        [string] $CaseTag,

        [ValidateScript({ Test-Path -Path (Split-Path $_ -Parent) -PathType Container })]
        [string] $EvidenceRoot = (Join-Path (Get-Location) 'evidence/1.19'),

        [ValidateSet('eDiscoveryManager','eDiscoveryAdministrator')]
        [string] $RequiredRole = 'eDiscoveryManager',

        [switch] $UseDeviceAuthentication
    )

    # ---- 1. PowerShell edition / version guard ------------------------------
    if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [version]'7.4.0') {
        throw "Initialize-Agt119Session requires PowerShell 7.4+ (Core). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
    }

    # ---- 2. Sovereign parameter resolution ----------------------------------
    $cloudMap = @{
        Commercial = @{
            GraphEnvironment = 'Global'
            IPPSConnectionUri = 'https://ps.compliance.protection.outlook.com/powershell-liveid/'
            AzureEnvironment = 'AzureCloud'
            GraphAudience = 'https://graph.microsoft.com/'
        }
        GCC = @{
            GraphEnvironment = 'Global'   # GCC uses commercial Graph endpoint
            IPPSConnectionUri = 'https://ps.compliance.protection.office365.us/powershell-liveid/'
            AzureEnvironment = 'AzureCloud'
            GraphAudience = 'https://graph.microsoft.com/'
        }
        GCCHigh = @{
            GraphEnvironment = 'USGov'
            IPPSConnectionUri = 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/'
            AzureEnvironment = 'AzureUSGovernment'
            GraphAudience = 'https://graph.microsoft.us/'
        }
        DoD = @{
            GraphEnvironment = 'USGovDoD'
            IPPSConnectionUri = 'https://ps.compliance.apps.mil/powershell-liveid/'
            AzureEnvironment = 'AzureUSGovernment'
            GraphAudience = 'https://dod-graph.microsoft.us/'
        }
    }
    $cloudCfg = $cloudMap[$Cloud]
    Write-Verbose "Cloud=$Cloud GraphEnv=$($cloudCfg.GraphEnvironment) IPPSUri=$($cloudCfg.IPPSConnectionUri)"

    # ---- 3. Evidence root ---------------------------------------------------
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $sessionRoot = Join-Path $EvidenceRoot ("{0}-{1}" -f $stamp, $CaseTag)
    $null = New-Item -Path $sessionRoot -ItemType Directory -Force

    # ---- 4. Connect Microsoft Graph -----------------------------------------
    $graphScopes = @(
        'eDiscovery.Read.All'
        'eDiscovery.ReadWrite.All'
        'User.Read.All'
        'Sites.Read.All'
        'AuditLog.Read.All'
        'Directory.Read.All'
    )
    if ($UseDeviceAuthentication) {
        Connect-MgGraph -Environment $cloudCfg.GraphEnvironment -Scopes $graphScopes -UseDeviceAuthentication -NoWelcome -ErrorAction Stop | Out-Null
    } else {
        Connect-MgGraph -Environment $cloudCfg.GraphEnvironment -Scopes $graphScopes -NoWelcome -ErrorAction Stop | Out-Null
    }
    $ctxGraph = Get-MgContext
    if (-not $ctxGraph) { throw "Connect-MgGraph did not establish a context for cloud '$Cloud'." }
    if ($ctxGraph.Account -ne $OperatorUpn) {
        Write-Warning "Connected Graph account '$($ctxGraph.Account)' does not match -OperatorUpn '$OperatorUpn'. Attribution evidence will record the connected account."
    }
    foreach ($scope in $graphScopes) {
        if ($ctxGraph.Scopes -notcontains $scope) {
            throw "Required Graph scope '$scope' was not granted. Granted: $($ctxGraph.Scopes -join ', ')"
        }
    }

    # ---- 5. Connect IPPS for §9 audit pull ----------------------------------
    Connect-IPPSSession -ConnectionUri $cloudCfg.IPPSConnectionUri -UserPrincipalName $OperatorUpn -ErrorAction Stop | Out-Null

    # ---- 6. Role-group membership check -------------------------------------
    $roleName = if ($RequiredRole -eq 'eDiscoveryAdministrator') { 'eDiscovery Administrator' } else { 'eDiscovery Manager' }
    $members = Get-RoleGroupMember -Identity $roleName -ErrorAction Stop
    $upns = @($members | ForEach-Object {
        try { (Get-User -Identity $_.Name -ErrorAction Stop).UserPrincipalName } catch { $_.Name }
    })
    if ($upns -notcontains $OperatorUpn) {
        throw "Operator '$OperatorUpn' is not a member of Purview role group '$roleName'. Assign via Entra PIM with a time-bounded activation before re-running."
    }

    # ---- 7. Session manifest ------------------------------------------------
    $session = [pscustomobject]@{
        ModuleVersion       = 'Agt119/1.4'
        Cloud               = $Cloud
        GraphEnvironment    = $cloudCfg.GraphEnvironment
        IPPSConnectionUri   = $cloudCfg.IPPSConnectionUri
        AzureEnvironment    = $cloudCfg.AzureEnvironment
        OperatorUpn         = $OperatorUpn
        ConnectedGraphUpn   = $ctxGraph.Account
        TenantId            = $ctxGraph.TenantId
        CaseTag             = $CaseTag
        SessionRoot         = $sessionRoot
        StartedUtc          = (Get-Date).ToUniversalTime().ToString('o')
        GrantedGraphScopes  = $ctxGraph.Scopes
        RequiredRole        = $roleName
        PSVersion           = $PSVersionTable.PSVersion.ToString()
    }
    $manifestPath = Join-Path $sessionRoot 'session-manifest.json'
    $session | ConvertTo-Json -Depth 6 | Set-Content -Path $manifestPath -Encoding utf8

    # ---- 8. Return ----------------------------------------------------------
    Write-Verbose "Session initialised. Evidence root: $sessionRoot"
    return $session
}
```

**Usage.**

```powershell
$session = Initialize-Agt119Session `
    -Cloud         GCCHigh `
    -OperatorUpn   'jane.doe@contoso.us' `
    -CaseTag       'matter-2026-0418-supervisory' `
    -RequiredRole  eDiscoveryManager `
    -Verbose
```

The `$session` object is the input to every subsequent helper in this playbook.

---

## 3. Create the eDiscovery case

The case is the parent container — it carries the matter name, description, status, retention, and the role-based access boundary inside Purview. **Create the case before the hold; create the hold before the search.**

```powershell
function New-Agt119Case {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [ValidatePattern('^[A-Za-z0-9 \-_/.]{4,128}$')] [string] $DisplayName,
        [Parameter(Mandatory)] [ValidateLength(8,1024)] [string] $Description,
        [string[]] $ExternalIds = @()
    )

    $existing = Get-MgSecurityCaseEdiscoveryCase -All -ErrorAction Stop |
                Where-Object DisplayName -EQ $DisplayName
    if ($existing) {
        Write-Verbose "Case '$DisplayName' already exists (id=$($existing.Id)) — returning existing case (idempotent)."
        return $existing
    }

    $body = @{
        displayName = $DisplayName
        description = $Description
        externalId  = ($ExternalIds -join ';')
    }

    if ($PSCmdlet.ShouldProcess($DisplayName, 'New-MgSecurityCaseEdiscoveryCase')) {
        $case = New-MgSecurityCaseEdiscoveryCase -BodyParameter $body -ErrorAction Stop

        # Evidence row
        Write-Agt119Evidence -Session $Session -Stage 'case-create' -Payload @{
            caseId      = $case.Id
            displayName = $case.DisplayName
            createdBy   = $Session.ConnectedGraphUpn
            createdUtc  = (Get-Date).ToUniversalTime().ToString('o')
            externalIds = $ExternalIds
        }
        return $case
    }
}
```

**Notes.**

- `externalId` is a single string property in the Graph schema — collapse multiple matter / ticket IDs with a delimiter the downstream parser understands.
- The case **name is immutable in the portal listing** for evidence purposes; pick a name that encodes matter ID, date, and supervisory category. `matter-2026-0418-supervisory-fa` is a typical pattern (`fa` = financial advisor).
- `ConfirmImpact='Medium'` — operators can `-Confirm:$false` in a CI pipeline once the change ticket has explicit approval.

---

## 4. Add custodians and location sources

The custodian is the human; the **sources** are the locations that custodian's content lives in. For Copilot interaction discovery, the relevant source classes are:

| Source class | Where Copilot interactions land | Cmdlet |
|---|---|---|
| `userSource` (mailbox) | Substrate-stored Copilot conversations live in the custodian's mailbox under hidden folders. **This is the source that brings Copilot chats into scope.** | `New-MgSecurityCaseEdiscoveryCaseCustodianUserSource` |
| `userSource` (OneDrive) | Files referenced by Copilot prompts; some agent file outputs | Same cmdlet, OneDrive URL |
| `siteSource` | SharePoint sites referenced by grounded prompts | `New-MgSecurityCaseEdiscoveryCaseCustodianSiteSource` |
| `noncustodialDataSource` (site or mailbox) | Shared mailboxes, Teams channel files, departmental sites — content not bound to a single custodian but in scope of the matter | `New-MgSecurityCaseEdiscoveryCaseNoncustodialDataSource` |

```powershell
function Add-Agt119Custodian {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [string] $CaseId,
        [Parameter(Mandatory)] [ValidatePattern('^[^@\s]+@[^@\s]+\.[^@\s]+$')] [string] $CustodianUpn,
        [string[]] $AdditionalSiteUrls = @(),
        [switch] $IncludeOneDrive
    )

    $user = Get-MgUser -UserId $CustodianUpn -ErrorAction Stop

    if ($PSCmdlet.ShouldProcess($CustodianUpn, 'New-MgSecurityCaseEdiscoveryCaseCustodian')) {
        $custodian = New-MgSecurityCaseEdiscoveryCaseCustodian `
            -EdiscoveryCaseId $CaseId `
            -BodyParameter @{ email = $CustodianUpn } `
            -ErrorAction Stop

        # Mailbox source — covers Copilot substrate
        $mailboxSource = New-MgSecurityCaseEdiscoveryCaseCustodianUserSource `
            -EdiscoveryCaseId $CaseId `
            -EdiscoveryCustodianId $custodian.Id `
            -BodyParameter @{ email = $CustodianUpn; includedSources = 'mailbox' } `
            -ErrorAction Stop

        # OneDrive source (optional but recommended for grounded-prompt files)
        if ($IncludeOneDrive) {
            $od = $null
            try { $od = Get-MgUserDefaultDrive -UserId $user.Id -ErrorAction Stop } catch { $od = $null }
            if ($od) {
                New-MgSecurityCaseEdiscoveryCaseCustodianUserSource `
                    -EdiscoveryCaseId $CaseId `
                    -EdiscoveryCustodianId $custodian.Id `
                    -BodyParameter @{ email = $CustodianUpn; includedSources = 'site'; siteWebUrl = $od.WebUrl } `
                    -ErrorAction Stop | Out-Null
            } else {
                Write-Warning "OneDrive not provisioned for $CustodianUpn — skipping OneDrive source."
            }
        }

        foreach ($siteUrl in $AdditionalSiteUrls) {
            New-MgSecurityCaseEdiscoveryCaseCustodianSiteSource `
                -EdiscoveryCaseId $CaseId `
                -EdiscoveryCustodianId $custodian.Id `
                -BodyParameter @{ site = @{ webUrl = $siteUrl } } `
                -ErrorAction Stop | Out-Null
        }

        Write-Agt119Evidence -Session $Session -Stage 'custodian-add' -Payload @{
            caseId            = $CaseId
            custodianId       = $custodian.Id
            custodianUpn      = $CustodianUpn
            mailboxSourceId   = $mailboxSource.Id
            siteUrls          = $AdditionalSiteUrls
            includeOneDrive   = [bool]$IncludeOneDrive
            addedUtc          = (Get-Date).ToUniversalTime().ToString('o')
        }
        return $custodian
    }
}
```

> **Custodian acknowledgement workflow.** The hold-notice acknowledgement page (where the custodian signs the hold-notice in the portal) is portal-only as of April 2026. The Graph schema includes a `customNoticeFormat` and the legal-hold object exposes an `acknowledgedDateTime` per recipient — the runtime path is portal-driven; the PowerShell path *reads* state for §11 verification, it does not author the workflow.

---


## 5. Create the search and run estimate statistics

The search resource carries the **KeyQL** content query and the bound sources. For Copilot interaction discovery the canonical scope is `kind:CopilotInteraction` — the Copilot location class introduced in the unified eDiscovery experience. Combine it with date and content filters using KeyQL's standard boolean grammar.

### 5.1 KeyQL — the small set of clauses you actually need for 1.19

| Clause | Meaning | Notes |
|---|---|---|
| `kind:CopilotInteraction` | Limit hits to Copilot prompt / response items | The canonical Copilot scope. **Do not** substitute `kind:microsoftteams` — Copilot conversations are not Teams chat items. |
| `(received>=2026-01-01 AND received<=2026-04-30)` | Inclusive date window | KeyQL date math is UTC. |
| `participants:user@contoso.us` | Restricts to messages where the UPN appears as a participant | Useful when one custodian's chats with a *specific* counterparty are in scope. |
| `subject:"trade idea"` OR `body:"trade idea"` | Substring on the subject / body | Quote multi-word terms. |
| `attachment:xlsx` | Items with Excel attachments | Useful for grounded prompts that pulled spreadsheets. |
| `(NOT body:"out of office")` | Boolean exclusion | Standard precedence — wrap logical groups in parens. |

A typical 1.19 search query for a single-custodian, single-quarter supervisory pull is:

```text
kind:CopilotInteraction AND (received>=2026-01-01 AND received<=2026-03-31)
```

```powershell
function New-Agt119Search {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [string] $CaseId,
        [Parameter(Mandatory)] [ValidatePattern('^[A-Za-z0-9 \-_]{4,128}$')] [string] $DisplayName,
        [Parameter(Mandatory)] [ValidateLength(1,4096)] [string] $ContentQuery,
        [string[]] $CustodianIds = @(),
        [string[]] $NoncustodialDataSourceIds = @()
    )

    $body = @{
        displayName  = $DisplayName
        contentQuery = $ContentQuery
        dataSourceScopes = 'none'
    }
    if ($CustodianIds.Count -gt 0) {
        $body['custodianSources@odata.bind'] = $CustodianIds | ForEach-Object {
            "https://graph.microsoft.com/v1.0/security/cases/ediscoveryCases/$CaseId/custodians/$_/userSources"
        }
    }
    if ($NoncustodialDataSourceIds.Count -gt 0) {
        $body['noncustodialSources@odata.bind'] = $NoncustodialDataSourceIds | ForEach-Object {
            "https://graph.microsoft.com/v1.0/security/cases/ediscoveryCases/$CaseId/noncustodialDataSources/$_"
        }
    }

    if ($PSCmdlet.ShouldProcess($DisplayName, 'New-MgSecurityCaseEdiscoveryCaseSearch')) {
        $search = New-MgSecurityCaseEdiscoveryCaseSearch `
            -EdiscoveryCaseId $CaseId `
            -BodyParameter $body `
            -ErrorAction Stop

        Write-Agt119Evidence -Session $Session -Stage 'search-create' -Payload @{
            caseId       = $CaseId
            searchId     = $search.Id
            displayName  = $DisplayName
            contentQuery = $ContentQuery
            custodianIds = $CustodianIds
            createdUtc   = (Get-Date).ToUniversalTime().ToString('o')
        }
        return $search
    }
}
```

### 5.2 Estimate statistics — `Invoke-MgEstimateSecurityCaseEdiscoveryCaseSearchStatistics`

`estimateStatistics` is asynchronous. The cmdlet returns immediately; you poll the case operations endpoint for completion. **Do not** treat the synchronous return value as the result.

```powershell
function Invoke-Agt119Estimate {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [string] $CaseId,
        [Parameter(Mandatory)] [string] $SearchId,
        [int] $TimeoutSeconds = 1800,
        [int] $PollSeconds = 15
    )

    Invoke-MgEstimateSecurityCaseEdiscoveryCaseSearchStatistics `
        -EdiscoveryCaseId $CaseId `
        -EdiscoverySearchId $SearchId `
        -ErrorAction Stop | Out-Null

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    do {
        Start-Sleep -Seconds $PollSeconds
        $ops = Get-MgSecurityCaseEdiscoveryCaseOperation -EdiscoveryCaseId $CaseId -All -ErrorAction Stop |
               Where-Object { $_.Action -eq 'estimateStatistics' -and $_.AdditionalProperties['searchId'] -eq $SearchId } |
               Sort-Object CreatedDateTime -Descending
        $latest = $ops | Select-Object -First 1
        Write-Verbose "Estimate status: $($latest.Status) (elapsed=$($sw.Elapsed))"
    } while ($latest.Status -in @('notStarted','running','submitted') -and $sw.Elapsed.TotalSeconds -lt $TimeoutSeconds)

    if ($latest.Status -ne 'succeeded') {
        throw "Estimate did not succeed within $TimeoutSeconds s. Last status: $($latest.Status). Operation id: $($latest.Id)."
    }

    $stats = (Get-MgSecurityCaseEdiscoveryCaseSearch -EdiscoveryCaseId $CaseId -EdiscoverySearchId $SearchId -ErrorAction Stop).LastEstimateStatisticsOperation

    Write-Agt119Evidence -Session $Session -Stage 'search-estimate' -Payload @{
        caseId           = $CaseId
        searchId         = $SearchId
        operationId      = $latest.Id
        status           = $latest.Status
        indexedItemCount = $stats.IndexedItemCount
        indexedItemsSize = $stats.IndexedItemsSize
        unindexedItemCount = $stats.UnindexedItemCount
        completedUtc     = (Get-Date).ToUniversalTime().ToString('o')
    }
    return $stats
}
```

> **Estimate is not preservation.** The estimate tells you what the index sees *now*. It does not freeze content. If the hold (§6) was created after the relevant Copilot interaction was deleted by the custodian, the estimate may show zero — a result that is consistent with FRCP 37(e) spoliation. The order of operations matters: hold first, search second.

---

## 6. Create and bind the legal hold (the preservation primitive)

This is the section that satisfies the duty-to-preserve. The unified eDiscovery experience exposes preservation as a **`legalHold`** resource on the case, with **`legalHoldUserSource`** rows for mailbox / OneDrive coverage and **`legalHoldSiteSource`** rows for SharePoint coverage. A hold takes effect at the time the source row is created — Microsoft does not publish a hard enable-time SLA, but for legal sufficiency the binding moment is what defends the duty, not the moment the index reflects the hold.

```powershell
function New-Agt119Hold {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [string] $CaseId,
        [Parameter(Mandatory)] [ValidatePattern('^[A-Za-z0-9 \-_]{4,128}$')] [string] $DisplayName,
        [Parameter(Mandatory)] [string[]] $CustodianUpns,
        [string[]] $SiteUrls = @(),
        [ValidateLength(0,4096)] [string] $ContentQuery = ''
    )

    $body = @{
        displayName  = $DisplayName
        description  = "Hold for case $CaseId. Author: $($Session.ConnectedGraphUpn). Created: $((Get-Date).ToUniversalTime().ToString('o'))."
        contentQuery = $ContentQuery
        isEnabled    = $true
    }

    if ($PSCmdlet.ShouldProcess($DisplayName, 'New-MgSecurityCaseEdiscoveryCaseLegalHold')) {
        $hold = New-MgSecurityCaseEdiscoveryCaseLegalHold `
            -EdiscoveryCaseId $CaseId `
            -BodyParameter $body `
            -ErrorAction Stop

        $userSourceIds = @()
        foreach ($upn in $CustodianUpns) {
            $us = New-MgSecurityCaseEdiscoveryCaseLegalHoldUserSource `
                -EdiscoveryCaseId $CaseId `
                -EdiscoveryHoldId $hold.Id `
                -BodyParameter @{ email = $upn; includedSources = 'mailbox,site' } `
                -ErrorAction Stop
            $userSourceIds += $us.Id
        }

        $siteSourceIds = @()
        foreach ($siteUrl in $SiteUrls) {
            $ss = New-MgSecurityCaseEdiscoveryCaseLegalHoldSiteSource `
                -EdiscoveryCaseId $CaseId `
                -EdiscoveryHoldId $hold.Id `
                -BodyParameter @{ site = @{ webUrl = $siteUrl } } `
                -ErrorAction Stop
            $siteSourceIds += $ss.Id
        }

        # Notification evidence row — hold-notice acknowledgement is portal-driven;
        # this row asserts that PowerShell created the hold and wrote the binding.
        Write-Agt119Evidence -Session $Session -Stage 'hold-create' -Payload @{
            caseId            = $CaseId
            holdId            = $hold.Id
            holdDisplayName   = $DisplayName
            isEnabled         = $true
            custodianUpns     = $CustodianUpns
            userSourceIds     = $userSourceIds
            siteUrls          = $SiteUrls
            siteSourceIds     = $siteSourceIds
            contentQuery      = $ContentQuery
            createdUtc        = (Get-Date).ToUniversalTime().ToString('o')
            createdBy         = $Session.ConnectedGraphUpn
            notificationModel = 'portal-driven custodian acknowledgement (Graph schema acknowledgedDateTime)'
        }

        $notifyPath = Join-Path $Session.SessionRoot ("notification-{0}.json" -f $hold.Id)
        @{
            holdId          = $hold.Id
            caseId          = $CaseId
            displayName     = $DisplayName
            custodians      = $CustodianUpns
            sites           = $SiteUrls
            issuedBy        = $Session.ConnectedGraphUpn
            issuedUtc       = (Get-Date).ToUniversalTime().ToString('o')
            sovereignCloud  = $Session.Cloud
            acknowledgement = 'pending portal acknowledgement (read via Get-MgSecurityCaseEdiscoveryCaseLegalHold expanded property)'
        } | ConvertTo-Json -Depth 5 | Set-Content -Path $notifyPath -Encoding utf8

        return $hold
    }
}
```

### 6.1 Hold release — `ConfirmImpact='High'` and an explicit ticket

Releasing a hold is the most dangerous operation in this control. It must be:

- gated by a release ticket reference,
- restricted to the **eDiscovery Administrator** role group (§2 `RequiredRole = 'eDiscoveryAdministrator'`),
- evidenced separately,
- *never* executed in a non-interactive pipeline without `-Confirm:$false` and a documented approver in the change ticket.

```powershell
function Disable-Agt119Hold {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [string] $CaseId,
        [Parameter(Mandatory)] [string] $HoldId,
        [Parameter(Mandatory)] [ValidatePattern('^[A-Z]{2,6}-\d{4,8}$')] [string] $ReleaseTicket,
        [Parameter(Mandatory)] [string] $Approver
    )
    if ($Session.RequiredRole -ne 'eDiscovery Administrator') {
        throw "Hold release requires the eDiscovery Administrator role. Re-initialise the session with -RequiredRole eDiscoveryAdministrator."
    }
    if ($PSCmdlet.ShouldProcess("Hold $HoldId", "Disable (release)")) {
        Update-MgSecurityCaseEdiscoveryCaseLegalHold `
            -EdiscoveryCaseId $CaseId `
            -EdiscoveryHoldId $HoldId `
            -BodyParameter @{ isEnabled = $false } `
            -ErrorAction Stop | Out-Null

        Write-Agt119Evidence -Session $Session -Stage 'hold-release' -Payload @{
            caseId         = $CaseId
            holdId         = $HoldId
            releaseTicket  = $ReleaseTicket
            approver       = $Approver
            releasedBy     = $Session.ConnectedGraphUpn
            releasedUtc    = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

---

## 7. Review set, analytics, and reviewer tags

The review set is the work surface for the privilege / responsiveness review that produces the production set. Review-set creation is synchronous; `addToReviewSet` is asynchronous and must be polled via `Get-MgSecurityCaseEdiscoveryCaseOperation`.

```powershell
function Add-Agt119SearchToReviewSet {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [string] $CaseId,
        [Parameter(Mandatory)] [string] $SearchId,
        [Parameter(Mandatory)] [string] $ReviewSetDisplayName,
        [int] $TimeoutSeconds = 7200,
        [int] $PollSeconds = 30
    )

    $rs = Get-MgSecurityCaseEdiscoveryCaseReviewSet -EdiscoveryCaseId $CaseId -All -ErrorAction Stop |
          Where-Object DisplayName -EQ $ReviewSetDisplayName
    if (-not $rs) {
        if ($PSCmdlet.ShouldProcess($ReviewSetDisplayName, 'New-MgSecurityCaseEdiscoveryCaseReviewSet')) {
            $rs = New-MgSecurityCaseEdiscoveryCaseReviewSet `
                -EdiscoveryCaseId $CaseId `
                -BodyParameter @{ displayName = $ReviewSetDisplayName } `
                -ErrorAction Stop
        }
    }

    Add-MgSecurityCaseEdiscoveryCaseSearchToReviewSet `
        -EdiscoveryCaseId $CaseId `
        -EdiscoverySearchId $SearchId `
        -BodyParameter @{
            reviewSet = @{ id = $rs.Id }
            additionalDataOptions = 'linkedFiles'
        } `
        -ErrorAction Stop | Out-Null

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    do {
        Start-Sleep -Seconds $PollSeconds
        $latest = Get-MgSecurityCaseEdiscoveryCaseOperation -EdiscoveryCaseId $CaseId -All -ErrorAction Stop |
                  Where-Object { $_.Action -eq 'addToReviewSet' } |
                  Sort-Object CreatedDateTime -Descending |
                  Select-Object -First 1
        Write-Verbose "addToReviewSet status: $($latest.Status) (elapsed=$($sw.Elapsed))"
    } while ($latest.Status -in @('notStarted','running','submitted') -and $sw.Elapsed.TotalSeconds -lt $TimeoutSeconds)

    if ($latest.Status -ne 'succeeded') {
        throw "addToReviewSet did not succeed within $TimeoutSeconds s. Last status: $($latest.Status)."
    }

    Write-Agt119Evidence -Session $Session -Stage 'review-set-load' -Payload @{
        caseId             = $CaseId
        searchId           = $SearchId
        reviewSetId        = $rs.Id
        reviewSetName      = $ReviewSetDisplayName
        operationId        = $latest.Id
        status             = $latest.Status
        completedUtc       = (Get-Date).ToUniversalTime().ToString('o')
    }
    return $rs
}
```

**Reviewer tags** (relevant / privileged / non-responsive) are created with `New-MgSecurityCaseEdiscoveryCaseTag`. **Analytics** (near-duplicate detection, email threading, themes) is enabled per case via `Update-MgSecurityCaseEdiscoveryCaseSettings`. Both are case-scoped; revisit them once per matter.

---

## 8. Defensible export with SHA-256 manifest

Export is the most regulator-facing operation in this control. The output package must be:

- written to a directory the operator does not have write access to once finalised (recommended: an Azure Storage container with an **immutability policy lock** for SEC 17a-4(f) WORM compliance),
- accompanied by a **per-file SHA-256 manifest** signed by the operator's session,
- referenced in the §10 evidence pack and the §11 verification record.

```powershell
function Export-Agt119ReviewSet {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [string] $CaseId,
        [Parameter(Mandatory)] [string] $ReviewSetId,
        [Parameter(Mandatory)] [ValidatePattern('^[A-Za-z0-9 \-_]{4,128}$')] [string] $ExportName,
        [Parameter(Mandatory)] [ValidateScript({ Test-Path $_ -PathType Container })] [string] $LocalLandingDir,
        [int] $TimeoutSeconds = 14400,
        [int] $PollSeconds = 60
    )

    if ($PSCmdlet.ShouldProcess($ExportName, 'Export-MgSecurityCaseEdiscoveryCaseReviewSet')) {
        Export-MgSecurityCaseEdiscoveryCaseReviewSet `
            -EdiscoveryCaseId $CaseId `
            -EdiscoveryReviewSetId $ReviewSetId `
            -BodyParameter @{
                outputName       = $ExportName
                description      = "Export by $($Session.ConnectedGraphUpn) at $((Get-Date).ToUniversalTime().ToString('o'))"
                exportOptions    = 'originalFiles,fileInfo,tags'
                exportStructure  = 'directory'
            } `
            -ErrorAction Stop | Out-Null

        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        do {
            Start-Sleep -Seconds $PollSeconds
            $latest = Get-MgSecurityCaseEdiscoveryCaseOperation -EdiscoveryCaseId $CaseId -All -ErrorAction Stop |
                      Where-Object { $_.Action -eq 'exportReviewSet' } |
                      Sort-Object CreatedDateTime -Descending |
                      Select-Object -First 1
            Write-Verbose "Export status: $($latest.Status) (elapsed=$($sw.Elapsed))"
        } while ($latest.Status -in @('notStarted','running','submitted') -and $sw.Elapsed.TotalSeconds -lt $TimeoutSeconds)

        if ($latest.Status -ne 'succeeded') {
            throw "Export did not succeed within $TimeoutSeconds s. Last status: $($latest.Status)."
        }

        # The Graph export delivers a download URL on the operation; download with the operator's delegated token
        $opDetail = Get-MgSecurityCaseEdiscoveryCaseOperation -EdiscoveryCaseId $CaseId -EdiscoveryCaseOperationId $latest.Id -ErrorAction Stop
        $exportUri = $opDetail.AdditionalProperties['exportFileMetadata'] | Where-Object { $_.fileName -like '*.zip' } | Select-Object -First 1
        if (-not $exportUri) {
            throw "Export operation succeeded but no zip metadata returned. Operation id: $($latest.Id)."
        }

        $localZip = Join-Path $LocalLandingDir ("{0}-{1}.zip" -f $ExportName, (Get-Date -Format 'yyyyMMddHHmmss'))
        Invoke-MgGraphRequest -Method GET -Uri $exportUri.downloadUrl -OutputFilePath $localZip -ErrorAction Stop

        # SHA-256 the bundle and every file in it after expansion
        $bundleHash = (Get-FileHash -Algorithm SHA256 -Path $localZip).Hash
        $expandDir  = Join-Path $LocalLandingDir ("{0}-{1}-expanded" -f $ExportName, (Get-Date -Format 'yyyyMMddHHmmss'))
        Expand-Archive -Path $localZip -DestinationPath $expandDir -Force

        $perFile = Get-ChildItem -Path $expandDir -Recurse -File | ForEach-Object {
            [pscustomobject]@{
                relativePath = $_.FullName.Substring($expandDir.Length).TrimStart('\','/')
                sizeBytes    = $_.Length
                sha256       = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash
            }
        }

        $manifest = [pscustomobject]@{
            caseId         = $CaseId
            reviewSetId    = $ReviewSetId
            exportName     = $ExportName
            operationId    = $latest.Id
            bundleZipPath  = $localZip
            bundleSha256   = $bundleHash
            expandedDir    = $expandDir
            files          = $perFile
            exportedBy     = $Session.ConnectedGraphUpn
            exportedUtc    = (Get-Date).ToUniversalTime().ToString('o')
            sovereignCloud = $Session.Cloud
        }
        $manifestPath = Join-Path $Session.SessionRoot ("export-manifest-{0}.json" -f $latest.Id)
        $manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding utf8

        Write-Agt119Evidence -Session $Session -Stage 'export' -Payload @{
            caseId        = $CaseId
            reviewSetId   = $ReviewSetId
            exportName    = $ExportName
            operationId   = $latest.Id
            bundleSha256  = $bundleHash
            fileCount     = $perFile.Count
            manifestPath  = $manifestPath
            exportedUtc   = (Get-Date).ToUniversalTime().ToString('o')
        }
        return $manifest
    }
}
```

> **WORM landing.** For SEC Rule 17a-4(f) compliance the export bundle and its SHA-256 manifest must land in storage that enforces immutability. The recommended pattern is an Azure Storage container with a **time-based immutability policy** (locked, not unlocked) and `enableAutoTieringToCool=$false`. The Az.Storage path is out of scope for this snippet but referenced in the verification-testing playbook.

---


## 9. Unified Audit Log integration — paged `Search-UnifiedAuditLog`

The Unified Audit Log corroborates *operator activity around the case*: who created the case, who applied which hold, which export was downloaded, by whom, when. This is the supervisory-attribution evidence FINRA Rule 3110 expects to see alongside the Graph case manifest.

The two `RecordType` values that matter for 1.19 are **`Discovery`** (record type 28 — eDiscovery activity) and **`AeD`** (record type 54 — Advanced eDiscovery activity, retained as a record-type label for transitional and unified events).

> **Pagination is mandatory.** `Search-UnifiedAuditLog` returns a maximum of **5 000** records per call. A bare invocation against a busy tenant *silently* truncates evidence — and this truncation is the most common false-clean defect on this control. Use a stable `SessionId` and `SessionCommand 'ReturnLargeSet'` and loop until the page returns fewer than `ResultSize` rows.

```powershell
function Get-Agt119AuditEvents {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [datetime] $StartUtc,
        [Parameter(Mandatory)] [datetime] $EndUtc,
        [string] $CaseId,
        [int] $PageSize = 5000
    )

    if (($EndUtc - $StartUtc).TotalDays -gt 31) {
        Write-Warning "Pulling more than 31 days in a single call. Microsoft documents reduced reliability for windows >31 days; consider splitting."
    }

    $sessionId = "agt119-{0}-{1}" -f $Session.CaseTag, ([guid]::NewGuid().ToString('N').Substring(0,8))
    $allEvents = New-Object System.Collections.Generic.List[object]
    $page = 0

    do {
        $page++
        $batch = Search-UnifiedAuditLog `
            -StartDate     $StartUtc `
            -EndDate       $EndUtc `
            -RecordType    Discovery,AeD `
            -ResultSize    $PageSize `
            -SessionId     $sessionId `
            -SessionCommand ReturnLargeSet `
            -ErrorAction   Stop

        if ($null -ne $batch -and @($batch).Count -gt 0) {
            foreach ($r in $batch) { [void]$allEvents.Add($r) }
            Write-Verbose "Page $page returned $((@($batch)).Count) rows. Cumulative: $($allEvents.Count)."
        }
        $lastCount = (@($batch)).Count
    } while ($lastCount -ge $PageSize -and $page -lt 200)

    if ($page -ge 200) {
        Write-Warning "Hit hard page cap (200) — split the time window and re-pull. Evidence may be incomplete."
    }

    if ($CaseId) {
        $allEvents = $allEvents | Where-Object {
            $au = ConvertFrom-Json $_.AuditData -ErrorAction SilentlyContinue
            $au.CaseId -eq $CaseId -or $au.ObjectId -like "*$CaseId*"
        }
    }

    $outPath = Join-Path $Session.SessionRoot ("audit-discovery-{0}-to-{1}.json" -f `
                $StartUtc.ToString('yyyyMMddTHHmmssZ'), `
                $EndUtc.ToString('yyyyMMddTHHmmssZ'))
    $allEvents | ConvertTo-Json -Depth 10 | Set-Content -Path $outPath -Encoding utf8

    Write-Agt119Evidence -Session $Session -Stage 'audit-pull' -Payload @{
        sessionId     = $sessionId
        startUtc      = $StartUtc.ToString('o')
        endUtc        = $EndUtc.ToString('o')
        recordTypes   = @('Discovery','AeD')
        eventCount    = $allEvents.Count
        pageCount     = $page
        outputPath    = $outPath
        truncated     = ($page -ge 200)
        capturedUtc   = (Get-Date).ToUniversalTime().ToString('o')
    }
    return $allEvents
}
```

The complementary Graph audit endpoint (`/auditLogs/directoryAudits` and `/security/auditLog/queries`) is the **fallback** when IPPS is unavailable in a sovereign cloud. Treat it as fallback, not as the canonical source — `Search-UnifiedAuditLog` remains the regulator-recognised supervisory artefact for Microsoft 365 audit retrieval.

---

## 10. `Write-Agt119Evidence` — SHA-256 evidence manifest

Every operation in this playbook calls `Write-Agt119Evidence`. This helper appends a hashed JSON line to `evidence.jsonl` in the session root and updates a per-session **manifest** that records the SHA-256 of every file it has emitted. The manifest is what the verification-testing playbook (`./verification-testing.md`) loads to assert that each evidence row is unmodified.

```powershell
function Write-Agt119Evidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [ValidateSet(
            'case-create','custodian-add','search-create','search-estimate',
            'hold-create','hold-release','review-set-load','export',
            'audit-pull','session-close')] [string] $Stage,
        [Parameter(Mandatory)] [hashtable] $Payload
    )

    $row = [ordered]@{
        controlId      = '1.19'
        controlVersion = $Session.ModuleVersion
        cloud          = $Session.Cloud
        operatorUpn    = $Session.ConnectedGraphUpn
        tenantId       = $Session.TenantId
        caseTag        = $Session.CaseTag
        stage          = $Stage
        recordedUtc    = (Get-Date).ToUniversalTime().ToString('o')
        payload        = $Payload
    }
    $json = $row | ConvertTo-Json -Depth 12 -Compress

    # Row hash binds the evidence row to its content
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $rowHash = ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join ''
    $sha.Dispose()

    $hashed = ($json.TrimEnd('}') + ',"rowSha256":"' + $rowHash + '"}')

    $jsonl = Join-Path $Session.SessionRoot 'evidence.jsonl'
    Add-Content -Path $jsonl -Value $hashed -Encoding utf8

    # Update the file-level manifest — used by §11 check 6
    $manifestPath = Join-Path $Session.SessionRoot 'manifest.json'
    $manifest = if (Test-Path $manifestPath) {
        Get-Content -Path $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
    } else {
        [pscustomobject]@{ files = @() }
    }
    $files = @($manifest.files | Where-Object { $_ })
    $existing = $files | Where-Object { $_.path -eq $jsonl } | Select-Object -First 1
    $newHash = (Get-FileHash -Algorithm SHA256 -Path $jsonl).Hash
    if ($existing) {
        $existing.sha256 = $newHash
        $existing.sizeBytes = (Get-Item $jsonl).Length
        $existing.lastUpdatedUtc = (Get-Date).ToUniversalTime().ToString('o')
    } else {
        $files += [pscustomobject]@{
            path           = $jsonl
            sha256         = $newHash
            sizeBytes      = (Get-Item $jsonl).Length
            lastUpdatedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
    # Add any sibling artefacts emitted during this stage (notification-*.json, export-manifest-*.json, audit-discovery-*.json)
    Get-ChildItem -Path $Session.SessionRoot -File |
        Where-Object { $_.Name -ne 'manifest.json' -and $_.Name -ne 'evidence.jsonl' -and $_.FullName -notin $files.path } |
        ForEach-Object {
            $files += [pscustomobject]@{
                path           = $_.FullName
                sha256         = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash
                sizeBytes      = $_.Length
                lastUpdatedUtc = (Get-Date).ToUniversalTime().ToString('o')
            }
        }
    $manifest = [pscustomobject]@{
        controlId      = '1.19'
        cloud          = $Session.Cloud
        caseTag        = $Session.CaseTag
        operatorUpn    = $Session.ConnectedGraphUpn
        tenantId       = $Session.TenantId
        sessionRoot    = $Session.SessionRoot
        files          = $files
        lastUpdatedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding utf8
}
```

The evidence pack is the authoritative artefact for SEC Rule 17a-4 production, FINRA 4511 books-and-records, and SOX §802 audit-trail evidence. **Do not mutate it after the fact.** If you need to add commentary, add it as a sibling `commentary.md` and re-hash; the manifest will record the addition.

---

## 11. Verification — six checks that return `[pscustomobject]@{Check;Pass;...}`

Each check is structured for direct ingestion by the `verification-testing.md` playbook. Pass / fail / detail makes it Pester-friendly.

```powershell
function Test-Agt119Implementation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [pscustomobject] $Session,
        [Parameter(Mandatory)] [string] $CaseId,
        [string] $ExpectedHoldDisplayName,
        [string[]] $ExpectedCustodianUpns = @(),
        [string] $ExpectedSearchDisplayName,
        [string] $ExpectedReviewSetDisplayName,
        [string] $ExpectedExportName
    )

    $results = New-Object System.Collections.Generic.List[object]

    # ---- Check 1: case exists, status active, owned by operator -------------
    $case = Get-MgSecurityCaseEdiscoveryCase -EdiscoveryCaseId $CaseId -ErrorAction SilentlyContinue
    $results.Add([pscustomobject]@{
        Check  = '1. Case exists and is active'
        Pass   = ($null -ne $case -and $case.Status -in @('active','open','unknownFutureValue'))
        Detail = if ($case) { "id=$($case.Id) status=$($case.Status) displayName=$($case.DisplayName)" } else { 'case not found' }
    })

    # ---- Check 2: at least one enabled hold and every expected custodian has a userSource on it
    $holds = Get-MgSecurityCaseEdiscoveryCaseLegalHold -EdiscoveryCaseId $CaseId -All -ErrorAction SilentlyContinue
    $enabledHolds = @($holds | Where-Object IsEnabled)
    $coveredUpns = @()
    foreach ($h in $enabledHolds) {
        $us = Get-MgSecurityCaseEdiscoveryCaseLegalHoldUserSource -EdiscoveryCaseId $CaseId -EdiscoveryHoldId $h.Id -All -ErrorAction SilentlyContinue
        $coveredUpns += @($us.Email)
    }
    $missing = @($ExpectedCustodianUpns | Where-Object { $_ -notin $coveredUpns })
    $results.Add([pscustomobject]@{
        Check  = '2. Enabled hold covers every expected custodian (preservation primitive bound)'
        Pass   = ($enabledHolds.Count -gt 0 -and $missing.Count -eq 0)
        Detail = "enabledHolds=$($enabledHolds.Count) coveredUpns=$($coveredUpns.Count) missing=[$($missing -join ', ')]"
    })

    # ---- Check 3: search exists with KeyQL kind:CopilotInteraction --------
    $searches = Get-MgSecurityCaseEdiscoveryCaseSearch -EdiscoveryCaseId $CaseId -All -ErrorAction SilentlyContinue
    $copilotSearch = @($searches | Where-Object { $_.ContentQuery -match 'kind:CopilotInteraction' })
    $results.Add([pscustomobject]@{
        Check  = '3. Search uses KeyQL kind:CopilotInteraction (Copilot scope bound)'
        Pass   = ($copilotSearch.Count -gt 0)
        Detail = "searches=$($searches.Count) withCopilotKind=$($copilotSearch.Count)"
    })

    # ---- Check 4: search has been estimated (LastEstimateStatisticsOperation present and succeeded)
    $estimated = @($copilotSearch | Where-Object { $_.LastEstimateStatisticsOperation.Status -eq 'succeeded' })
    $results.Add([pscustomobject]@{
        Check  = '4. Estimate completed for the Copilot-scoped search'
        Pass   = ($estimated.Count -gt 0)
        Detail = "estimatedSearches=$($estimated.Count) of $($copilotSearch.Count)"
    })

    # ---- Check 5: review set exists and at least one export operation has succeeded
    $reviewSets = Get-MgSecurityCaseEdiscoveryCaseReviewSet -EdiscoveryCaseId $CaseId -All -ErrorAction SilentlyContinue
    $ops = Get-MgSecurityCaseEdiscoveryCaseOperation -EdiscoveryCaseId $CaseId -All -ErrorAction SilentlyContinue
    $exportOps = @($ops | Where-Object { $_.Action -eq 'exportReviewSet' -and $_.Status -eq 'succeeded' })
    $results.Add([pscustomobject]@{
        Check  = '5. Review set exists and at least one export has succeeded'
        Pass   = ($reviewSets.Count -gt 0 -and $exportOps.Count -gt 0)
        Detail = "reviewSets=$($reviewSets.Count) succeededExports=$($exportOps.Count)"
    })

    # ---- Check 6: every file in the session-root manifest hashes to its recorded SHA-256
    $manifestPath = Join-Path $Session.SessionRoot 'manifest.json'
    $tampered = @()
    if (Test-Path $manifestPath) {
        $manifest = Get-Content -Path $manifestPath -Raw -Encoding utf8 | ConvertFrom-Json
        foreach ($f in @($manifest.files)) {
            if (-not (Test-Path $f.path)) { $tampered += "$($f.path) (missing)"; continue }
            $actual = (Get-FileHash -Algorithm SHA256 -Path $f.path).Hash
            if ($actual -ne $f.sha256 -and $f.path -notmatch 'manifest\.json$') {
                $tampered += "$($f.path) (expected=$($f.sha256) actual=$actual)"
            }
        }
        $manifestPresent = $true
    } else {
        $manifestPresent = $false
    }
    $results.Add([pscustomobject]@{
        Check  = '6. Evidence manifest present and every file hash matches'
        Pass   = ($manifestPresent -and $tampered.Count -eq 0)
        Detail = if (-not $manifestPresent) { 'manifest.json missing' } elseif ($tampered.Count -eq 0) { "files=$($manifest.files.Count) all hashes match" } else { "tampered=[$($tampered -join '; ')]" }
    })

    # Summary
    $pass = @($results | Where-Object Pass).Count
    Write-Verbose "Verification summary: $pass / $($results.Count) checks passed."

    Write-Agt119Evidence -Session $Session -Stage 'session-close' -Payload @{
        verificationResults = $results | ForEach-Object { @{ check = $_.Check; pass = $_.Pass; detail = $_.Detail } }
        passCount           = $pass
        totalChecks         = $results.Count
        sealedUtc           = (Get-Date).ToUniversalTime().ToString('o')
    }

    return $results
}
```

**Exit criteria:** all six checks return `Pass = $true`. Anything less is a defect — log it, raise a change ticket, do not declare the matter ready for production.

---

## 12. Sovereign-cloud variant matrix

| Cloud | `Connect-MgGraph -Environment` | `Connect-IPPSSession -ConnectionUri` | Az environment | Graph audience | Notes |
|---|---|---|---|---|---|
| **Commercial** | `Global` | `https://ps.compliance.protection.outlook.com/powershell-liveid/` | `AzureCloud` | `https://graph.microsoft.com/` | Default. Most documentation examples assume this cloud. |
| **GCC** | `Global` | `https://ps.compliance.protection.office365.us/powershell-liveid/` | `AzureCloud` | `https://graph.microsoft.com/` | GCC uses the **commercial** Graph endpoint but the **government** IPPS endpoint. Most common silent-failure cloud. |
| **GCC High** | `USGov` | `https://l5.ps.compliance.protection.office365.us/powershell-liveid/` | `AzureUSGovernment` | `https://graph.microsoft.us/` | Both Graph and IPPS are sovereign. Connect-MgGraph **must** specify `-Environment USGov`. |
| **DoD** | `USGovDoD` | `https://ps.compliance.apps.mil/powershell-liveid/` | `AzureUSGovernment` | `https://dod-graph.microsoft.us/` | Highest assurance. The `apps.mil` IPPS URI is the canonical DoD endpoint. |

> **21Vianet (China).** Microsoft **has not** retired the classic Premium / Standard eDiscovery experience for 21Vianet as of April 2026. Tenants in this cloud continue to operate against the legacy IPPS surface and are out of scope for this playbook — see the `troubleshooting.md` section "21Vianet special case" for the legacy authoring path.

> **Conditional Access.** Sovereign tenants frequently enforce CA policies that block non-compliant or non-managed devices from the Graph eDiscovery API. If `Connect-MgGraph` returns `AADSTS50005`, `AADSTS53003`, or `AADSTS53000`, the issue is policy enforcement, not module version — see `troubleshooting.md` for the remediation path.

---

## 13. Anti-patterns — what not to do (and why)

| # | Anti-pattern | Why it's wrong | Correct path |
|---|---|---|---|
| 1 | `New-ComplianceCase -CaseType "AdvancedEdiscovery"` | Retired 31 Aug 2025 (every cloud except 21Vianet). Cmdlet either errors or creates a transitional shim that the new portal cannot finish processing — SEC 17a-4 production fails. | §3 — `New-MgSecurityCaseEdiscoveryCase`. |
| 2 | `Connect-IPPSSession` with no `-ConnectionUri` in GCC / GCC High / DoD | Authenticates against the commercial endpoint silently; queries return zero rows; evidence pack looks clean but is empty in the sovereign tenant. | §2 — `Initialize-Agt119Session -Cloud` branches `IPPSConnectionUri` per cloud. |
| 3 | `Connect-MgGraph` with no `-Environment` in GCC High / DoD | Wrong tenant ring; either zero cases visible or `Forbidden` on mutations. | §2 — branches `GraphEnvironment` (`USGov` / `USGovDoD`). |
| 4 | Treating a search as preservation | A search is discovery, not preservation. Custodian deletes content between search and export → re-search returns zero → spoliation under FRCP 37(e). The *Zubulake* line of cases. | §6 — create a `legalHold` and bind `legalHoldUserSource` per custodian *before* the search runs. §11 check 2 enforces this. |
| 5 | `kind:microsoftteams AND from:"Copilot"` for Copilot scope | Copilot conversations are not Teams chat items with author "Copilot". They live in the substrate mailbox under a hidden `Copilot Chats` folder; the search returns zero. | §5 — `kind:CopilotInteraction` and bind the custodian *mailbox* source. |
| 6 | Bare `Search-UnifiedAuditLog` with no `SessionId` / `SessionCommand` | Returns max 5 000 rows; silently truncates evidence; truncation is invisible without a manual count. | §9 — paged loop with stable `SessionId` + `SessionCommand 'ReturnLargeSet'`, until last batch < `ResultSize`. |
| 7 | `Install-Module … -Force` with no `-RequiredVersion` | Breaks reproducibility; CAB cannot tie evidence to a known cmdlet surface. Fails SOX §404 / OCC 2023-17 evidence. | §1 — pin every module to a CAB-approved version; record release-notes review in change ticket. |
| 8 | Authenticating with a service principal for eDiscovery operations | Several Graph eDiscovery operations require *delegated* permissions; even where app-only works, attribution evidence under FINRA 3110 expects a human operator UPN. | §2 — delegated `Connect-MgGraph` with operator UPN; service principals are not a substitute. |
| 9 | Hold release in a non-interactive pipeline with no ticket reference | High-impact destructive operation; without an approver and ticket, defensibility under FRCP 37(e) collapses. | §6.1 — `Disable-Agt119Hold -ReleaseTicket -Approver`; gated to eDiscovery Administrator role. |
| 10 | Exporting to a writable local directory | Operator can mutate the export after the fact; chain-of-custody breaks. | §8 — land the bundle in an Azure Storage container with a **locked** time-based immutability policy (SEC 17a-4(f) WORM). |
| 11 | Skipping the operation-poll loop and assuming the `Invoke-…` return value is the result | `estimateStatistics`, `addToReviewSet`, `exportReviewSet` are all asynchronous. The synchronous return is acknowledgement, not result. Treating it as result yields false-clean evidence. | §5 / §7 / §8 — poll `Get-MgSecurityCaseEdiscoveryCaseOperation` with timeout. |
| 12 | Mutating the evidence pack after the fact | Breaks SHA-256 manifest; §11 check 6 fails. | §10 — append commentary as a sibling file and re-hash; never edit `evidence.jsonl` rows. |
| 13 | Combining `WhatIf` and a destructive action in the same call by accident | `New-MgSecurityCaseEdiscoveryCase -BodyParameter ... -WhatIf` returns the parameter set without creating; downstream cmdlets fail with "case not found" but the operator sees an apparent success in the console. | All mutating cmdlets in this playbook implement `SupportsShouldProcess` with `ConfirmImpact='Medium'` or `'High'`; the wrapper functions check `$PSCmdlet.ShouldProcess(...)` explicitly. |
| 14 | Using `Get-ComplianceCase` as the case-existence check after migration | Legacy cmdlet enumerates only legacy / transitional cases; new unified cases do not appear; idempotency check (§3) silently always returns "not found" and creates duplicate cases. | §3 — idempotency check uses `Get-MgSecurityCaseEdiscoveryCase -All`. |
| 15 | Pulling > 31 days in a single `Search-UnifiedAuditLog` window | Microsoft documents reduced reliability for windows > 31 days; pages may be silently dropped. | §9 — split windows ≤ 31 days; the helper warns when the window is too wide. |
| 16 | Trusting `IsEnabled = $true` on the *hold* alone as proof of preservation | A hold with no `legalHoldUserSource` rows preserves nothing. | §11 check 2 — enforces that every expected custodian appears as a `userSource` on an enabled hold. |
| 17 | Leaving the operator in the **eDiscovery Administrator** role group permanently | Tenant-scoped superset; should be JIT via Entra PIM. Permanent assignment violates SR 11-7 separation-of-duties expectations. | §2 `RequiredRole eDiscoveryAdministrator` only for hold-release operations; default operator role is **eDiscovery Manager**. |
| 18 | Calling `Disconnect-MgGraph` and re-`Connect-MgGraph` mid-pipeline to "refresh tokens" | Invalidates cached operation IDs and may switch tenant ring if `-Environment` is omitted on the reconnect. | §2 — establish the session once at the top of the runbook; rely on MSAL token refresh transparently. |

---

## 14. Cross-links

- **Control specification:** `docs/controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`
- **Portal walkthrough:** `./portal-walkthrough.md`
- **Verification & testing:** `./verification-testing.md`
- **Troubleshooting:** `./troubleshooting.md`
- **Shared baseline:** `docs/playbooks/_shared/powershell-baseline.md`
- **Related controls:**
  - `1.21-audit-log-retention-for-agents` — supplies the long-window audit retention this control queries
  - `1.20-purview-retention-for-copilot` — supplies the substrate retention the hold relies on
  - `2.04-supervisory-review-workflow` — consumes the review-set output for FINRA 3110 supervision
  - `3.07-records-immutability-storage` — defines the WORM landing for the §8 export bundle

---

*Updated: April 2026 | Version: v1.4.0 | UI Verification Status: Current*
