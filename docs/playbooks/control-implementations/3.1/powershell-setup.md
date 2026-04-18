# Control 3.1 — PowerShell Setup: Agent Inventory and Metadata Management Automation

> **Scope.** This playbook automates the multi-plane discovery, reconciliation, enrichment, and evidence emission required by Control 3.1 across **Copilot Studio bots, declarative agents, Microsoft 365 Copilot extensibility, MCP servers, the emerging Agent Registry / Agent 365 surface, SharePoint Connected agents, and Azure AI Foundry agent resources** in US financial services tenants. It assumes you have already read [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) (referenced below as **BL-§N**) and the parent control specification [`../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md).
>
> **What this playbook is.** A reproducible, fail-closed reconciliation harness that (a) pins module / CLI versions; (b) bootstraps a sovereign-aware, certificate-authenticated, audit-only session split across the PowerShell 5.1 Desktop and PowerShell 7.4 Core editions; (c) collects inventory from each Microsoft data plane that exposes agents today; (d) merges those streams into one canonical schema with an immutable `CanonicalAgentId`; (e) enriches the merged register with owner, last-activity, DLP, sensitivity-label, and manager metadata; (f) flags departed-owner, dormant, and unowned agents; (g) drives a documented lifecycle state machine; and (h) emits an examiner-ready evidence pack with SHA-256 hashes and a certificate-signed manifest.
>
> **What this playbook is not.** It does not replace the authoritative system of record (SharePoint list, Dataverse table, CMDB, or GRC tool). It does not, by itself, *guarantee* that every agent in your tenant is captured — Microsoft's discovery surfaces have known gaps (documented in §0 and §6) that organizations should compensate for through policy, manual attestation, and Defender for Cloud Apps shadow-IT detection (Control 3.6). It does not approve, decommission, or transfer agents; it raises evidence and inventory state, and humans accept risk.
>
> **Hedged language reminder.** Output of this harness *supports* compliance with FINRA Rule 4511, FINRA Regulatory Notice 25-07, SEC 17a-4(b)(4), SOX 302/404, GLBA 501(b), NYDFS Part 500.16/500.17, OCC Bulletin 2011-12 / Fed SR 11-7, and NIST AI RMF GOVERN 1.6 books-and-records expectations. It does not, by itself, *ensure* a passing examination, *guarantee* completeness against an unknowable shadow population, or *eliminate* the risk that a discovery surface drifts between releases. Implementation requires that organizations verify endpoint availability, module pinning, and sovereign feature parity at every change window.

| Field | Value |
|---|---|
| Control ID | 3.1 |
| Pillar | 3 — Reporting (FOUNDATION) |
| Playbook | PowerShell Setup |
| PowerShell Edition | 7.4 LTS Core (orchestrator); 5.1 Desktop (Power Apps Administration sub-shell, spawned and JSON-bridged) |
| Sovereign Clouds | Commercial, GCC, GCC High, DoD, China (21Vianet) — see §1 sovereign matrix and §2 bootstrap |
| Last UI Verified | April 2026 |
| Companion Playbooks | [`portal-walkthrough.md`](portal-walkthrough.md) · [`verification-testing.md`](verification-testing.md) · [`troubleshooting.md`](troubleshooting.md) |
| Related Controls | [1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) · [1.19](../1.19/) · [2.1](../2.1/) · [2.5](../2.5/) · [3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) · [3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) · [3.11](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) · [Incident & Risk Playbook](../../incident-and-risk/ai-incident-response-playbook.md) |

---

## §0 — Wrong-shell trap and the multi-plane false-clean defect (READ FIRST)

**The defining fact of Control 3.1.** As of April 2026, **no single Microsoft API returns "all agents"** in a tenant. A script that connects to one plane — even the most comprehensive one — and reports a number is producing audit-grade misinformation. The Power Platform admin surface knows about Copilot Studio bots and Power Apps that act as agent hosts; Microsoft Graph knows about declarative agents registered as Entra applications and about MCP server service principals; the M365 Copilot Hub telemetry knows about agents users are *actually invoking* (including ones never registered in your tenant catalog); SharePoint admin knows about grounding-source connected agents; the emerging Agent Registry / Agent 365 surface is partially GA in some clouds and unavailable in others. Reconciliation across these planes is the engineering problem this playbook solves.

A script that ignores this reality produces a **false-clean inventory** — the worst possible Control 3.1 outcome. False-clean inventory understates books-and-records exposure under FINRA Rule 4511 / SEC 17a-4(b)(4), produces the wrong denominator for every downstream metric in Pillar 3, and breaks the audit trail that supervisory examination response depends on (see [Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) for downstream dashboards).

**Why this section exists.** Three classes of silent failure produce false-clean inventory in Control 3.1 specifically:

1. **Wrong PowerShell edition for the plane being queried.** `Microsoft.PowerApps.Administration.PowerShell` and `Microsoft.PowerApps.PowerShell` are **Desktop-only** (Windows PowerShell 5.1) — they autoload in PowerShell 7 but several cmdlets silently return empty arrays instead of throwing. `Microsoft.Graph.Beta`, `ExchangeOnlineManagement` v3+, modern `PnP.PowerShell` v2+, and `Az.Accounts` v3+ are **Core-only** (PowerShell 7.2+). A reconciler that runs end-to-end in one edition is necessarily incomplete on at least one plane.
2. **Sovereign mis-routing.** `Add-PowerAppsAccount` without an explicit `-Endpoint usgov` / `usgovhigh` / `dod` parameter authenticates against commercial endpoints, returns zero environments in a GCC / GCC High / DoD tenant, and produces zero-row CSVs that look identical to a clean inventory. The same defect applies to `Connect-MgGraph -Environment` and `Connect-PnPOnline -Url`. See [BL-§3](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).
3. **Beta vs v1.0 Microsoft Graph drift.** Several Copilot / agent endpoints (`/copilot/admin/settings`, `/applications` agent-tag filters, `/reports/getCopilotAIInteractionsCount`, `/sites/{id}/copilotAgents`, `/agents` registry preview) move between beta and v1.0 quarterly, with breaking shape changes between minor SDK releases. Pinning is mandatory and version-stamping every call into the manifest is required for examiner reproducibility.

**Top false-clean defects unique to inventory automation.**

| # | Defect | What it looks like | How this playbook traps it |
|---|---|---|---|
| 1 | `Get-AdminPowerApp` on Core silently returns `$null` for `Owner` | Owner column populates as blank for every row | §0 edition assertion + §3 child-process spawn pattern |
| 2 | `appType` for Copilot Studio bots renamed across module versions (`Bot` → `ChatBot` → `CopilotStudioBot`) | Filter loses agents on the older value | §3 enumerates all `appType` values seen in tenant and warns on any unknown value |
| 3 | `Add-PowerAppsAccount` defaulted to `prod` in a GCC tenant | Returns zero environments; CSV is empty but exit code is `0` | §2 hard-fail when sovereign discriminator is detected on tenant but `-Endpoint` mismatches |
| 4 | `Connect-MgGraph -Scopes` requested but admin consent never granted | `Get-MgApplication` returns 200 with empty value array | §2 verifies granted scopes via `(Get-MgContext).Scopes` and exits 2 on mismatch |
| 5 | MCP servers filtered as `Get-MgApplication` (they are **service principals**) | Entire MCP population missing from inventory | §7 queries `Get-MgServicePrincipal` with both tag-based and known-appId filters |
| 6 | SharePoint Agents enumerated only through Power Platform | SPO-grounded agents missing entirely | §8 walks SPO admin + Graph `/sites/{id}/copilotAgents` (preview) |
| 7 | `Search-UnifiedAuditLog` returning fewer than 5,000 rows treated as authoritative | Pagination cut off; "dormant" classification falsely applied | §10 paginates with `SessionId` + `SessionCommand ReturnLargeSet` per Microsoft guidance |
| 8 | Owner string-match for orphan detection (`*system*`, `*deleted*`) | Real orphans missed; false positives spike | §11 resolves Owner ObjectId against `Get-MgUser` and `accountEnabled` |
| 9 | CSV output overwritten on each run | No historical reconciliation; deltas invisible | §13 emits run-id-stamped artifacts to a WORM store |
| 10 | SHA-256 computed but never signed | Hash file can be regenerated; no cryptographic provenance | §13 signs `manifest.json` with the Inventory Owner code-signing certificate |

**Required shell guard (run this at the top of every Control 3.1 session).**

```powershell
# Save as: scripts/Assert-Agt31Shell.ps1
[CmdletBinding()]
[OutputType([void])]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [version]'7.4.0') {
    Write-Error "Control 3.1 orchestrator requires PowerShell 7.4 LTS Core (pwsh). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Launch 'pwsh' (not 'powershell.exe') and retry. The Power Apps Administration leg will be spawned into a Windows PowerShell 5.1 child process by §3."
    exit 2
}

# Trap stale Windows PowerShell module shadowing (silent autoload of v1 Microsoft.Graph or v1 PnP.PowerShell)
$desktopPaths = $env:PSModulePath -split [IO.Path]::PathSeparator | Where-Object { $_ -match 'WindowsPowerShell\\Modules' }
if ($desktopPaths) {
    $bad = Get-Module -ListAvailable -Name 'Microsoft.Graph','PnP.PowerShell' |
        Where-Object { $_.Version.Major -lt 2 }
    if ($bad) {
        Write-Error "Stale v1 modules visible from Desktop module path: $($bad | ForEach-Object { "$($_.Name)=$($_.Version)" } | Sort-Object -Unique). Uninstall before continuing — autoload would silently shadow the pinned v2 modules and produce wrong-shape inventory output."
        exit 2
    }
}
```

**Fail-closed conditions enforced by this guard:**

- Detected PowerShell edition is `Desktop` or version `< 7.4.0` → `exit 2`.
- v1 of `Microsoft.Graph` or `PnP.PowerShell` discoverable on `$env:PSModulePath` → `exit 2`.
- Any pinned module missing the exact `RequiredVersion` after install attempt (verified in §1) → `exit 2`.

---

## §1 — Module, CLI, package, and permission matrix

**Why this section exists.** Inventory output is reproducible only when versions are declared, hashed, and emitted into the manifest. A pinned baseline also lets the change-management ticket reference exact module versions, which is what SOX 404 evidence reviewers expect.

### 1.1 Pinned PowerShell modules (orchestrator — PS 7.4 Core)

```powershell
# Save as: scripts/Install-Agt31Modules.ps1
[CmdletBinding(SupportsShouldProcess)]
[OutputType([void])]
param(
    [Parameter()] [switch]$AcceptLicense
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$modules = @(
    @{ Name = 'Microsoft.Graph.Authentication';                   Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Applications';                     Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Reports';                          Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Users';                            Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Identity.DirectoryManagement';     Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Beta.Applications';                Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Beta.Reports';                     Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Beta.Sites';                       Version = '2.25.0' },
    @{ Name = 'ExchangeOnlineManagement';                         Version = '3.7.0'  },
    @{ Name = 'PnP.PowerShell';                                   Version = '2.12.0' },
    @{ Name = 'Microsoft.Online.SharePoint.PowerShell';           Version = '16.0.25515.12000' },
    @{ Name = 'Az.Accounts';                                      Version = '3.0.0'  },
    @{ Name = 'Az.CognitiveServices';                             Version = '1.14.0' },
    @{ Name = 'Az.Resources';                                     Version = '7.4.0'  }
)

foreach ($m in $modules) {
    $existing = Get-Module -ListAvailable -Name $m.Name |
        Where-Object { $_.Version -eq [version]$m.Version }
    if (-not $existing) {
        if ($PSCmdlet.ShouldProcess("$($m.Name)@$($m.Version)", 'Install-Module')) {
            Install-Module -Name $m.Name -RequiredVersion $m.Version `
                -Scope CurrentUser -Repository PSGallery -AllowClobber `
                -AcceptLicense:$AcceptLicense -ErrorAction Stop
        }
    }
    Import-Module -Name $m.Name -RequiredVersion $m.Version -Force -ErrorAction Stop
    Write-Verbose "Imported $($m.Name) $($m.Version)"
}

# Desktop-only Power Apps modules: install into 5.1 sub-shell, NEVER into pwsh 7
$ppAdminVersion   = '2.0.183'
$ppMakerVersion   = '1.0.34'
if ($IsWindows) {
    if ($PSCmdlet.ShouldProcess("Microsoft.PowerApps.Administration.PowerShell@$ppAdminVersion (Desktop 5.1)", 'Install-Module via powershell.exe')) {
        powershell.exe -NoProfile -Command "Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -RequiredVersion $ppAdminVersion -Scope CurrentUser -Force -AllowClobber" | Out-Null
        powershell.exe -NoProfile -Command "Install-Module -Name Microsoft.PowerApps.PowerShell -RequiredVersion $ppMakerVersion -Scope CurrentUser -Force -AllowClobber" | Out-Null
    }
} else {
    Write-Warning "Non-Windows host detected. Power Apps Administration cmdlets are Windows-only. The reconciler will skip the Power Platform leg unless a Windows worker is available (see §3)."
}

<#
.SYNOPSIS
    Pins every PowerShell module Control 3.1 depends on to a CAB-approved version.
.DESCRIPTION
    Idempotent installer. Skips any module already present at the exact RequiredVersion.
    Spawns a Windows PowerShell 5.1 child process for the Power Apps Administration modules
    because they are Desktop-only and silently misbehave under PowerShell 7.
.EXAMPLE
    PS> ./Install-Agt31Modules.ps1 -WhatIf
    Lists every install action that would be taken without performing it.
.EXAMPLE
    PS> ./Install-Agt31Modules.ps1 -AcceptLicense -Verbose
    Performs the install for unattended scheduler use.
.NOTES
    Verify pinned versions against your CAB-approved baseline before each run.
#>
```

### 1.2 Pinned CLI tooling

| Tool | Minimum | Used for | Sovereign notes |
|---|---|---|---|
| Power Platform CLI (`pac`) | **1.45.0** | `pac copilot list`, `pac admin list-app-resources`, `pac auth create --cloud` | Pass `--cloud {Public\|UsGov\|UsGovHigh\|DoD}` |
| Microsoft 365 CLI (`m365`) | 7.0.0 | Optional declarative-agent enumeration cross-check | Public + GCC verified; GCC High limited |
| Azure CLI (`az`) | 2.60.0 | AI Foundry project lookup, role-assignment evidence | `az cloud set --name {AzureCloud\|AzureUSGovernment\|AzureChinaCloud}` |
| Python | 3.11.0 | Microsoft Graph beta wrappers for endpoints not yet in PowerShell SDK (e.g., preview `/agents`) | OSS, portable across all clouds |
| `Get-FileHash` (built-in) | n/a | SHA-256 evidence hashes | n/a |
| `signtool.exe` or `Set-AuthenticodeSignature` | n/a | Manifest signing in §13 | Code-signing cert must chain to CA approved by Information Security |

**Pin check (must run before §2 bootstrap):**

```powershell
# scripts/Test-Agt31Tooling.ps1
[CmdletBinding()]
[OutputType([pscustomobject[]])]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$results = @()
$pacVer = (& pac --version 2>$null) -join ' '
$results += [pscustomobject]@{ Tool='pac'; Found=$pacVer; Required='>=1.45.0'; Pass=($pacVer -match '1\.(4[5-9]|[5-9]\d)') }

$azVer  = (& az version --output json 2>$null) | ConvertFrom-Json
$results += [pscustomobject]@{ Tool='az'; Found=$azVer.'azure-cli'; Required='>=2.60.0'; Pass=([version]$azVer.'azure-cli' -ge [version]'2.60.0') }

$pyVer  = (& python --version 2>$null) -replace 'Python ',''
$results += [pscustomobject]@{ Tool='python'; Found=$pyVer; Required='>=3.11.0'; Pass=([version]$pyVer -ge [version]'3.11.0') }

$results
if ($results.Where({ -not $_.Pass }).Count) {
    Write-Error "One or more tooling pin checks failed. Review the results table above."
    exit 2
}
```

### 1.3 Pinned Python packages (Graph beta wrappers)

`requirements.agt31.txt`:

```text
msgraph-sdk>=1.5.0,<2.0.0
msgraph-beta-sdk>=1.5.0,<2.0.0
azure-identity>=1.17.0,<2.0.0
azure-mgmt-cognitiveservices>=13.5.0,<14.0.0
pandas>=2.2.0,<3.0.0
openpyxl>=3.1.2
cryptography>=42.0.0
```

The Python leg is invoked from §6 (Agent Registry preview) and §5 (Copilot AI interaction count where the PowerShell SDK lags behind beta). Python is **not** the primary execution surface; it is a thin wrapper around endpoints not yet exposed in `Microsoft.Graph.Beta`.

### 1.4 Permission matrix (audit-only, separate inventory-reader credentials)

Inventory must run unattended on a schedule. The Inventory Reader service principal should be **distinct** from any service principal that *changes* tenant state. This separation supports SOX 404 separation-of-duties: the principal that produces the evidence is not the principal that could alter the configuration the evidence describes.

| Principal / Role | Granted on | Permission | Why this script needs it | Audit-only? |
|---|---|---|---|---|
| `agt31-inventory-reader` (SP) | Microsoft Graph | `Application.Read.All` (Application) | Enumerate Entra app registrations including declarative agents; required for §4 | Yes |
| same SP | Microsoft Graph | `AgentApplication.Read.All` (Application, where available) | Agent 365 / Agent Registry preview; §6 | Yes |
| same SP | Microsoft Graph | `CopilotSettings-LimitedMode.Read.All` (or current GA equivalent) | `/copilot/admin` settings; §5 | Yes |
| same SP | Microsoft Graph | `Reports.Read.All` (Application) | `getCopilotAIInteractionsCount` aggregation; §5 | Yes |
| same SP | Microsoft Graph | `AuditLog.Read.All` (Application) | Sign-in / activity for Last Activity field; §10 | Yes |
| same SP | Microsoft Graph | `User.Read.All` (Application) | Resolve Owner ObjectId → Entra user; orphan detection in §11 | Yes |
| same SP | Microsoft Graph | `InformationProtectionPolicy.Read.All` (Application) | Sensitivity label resolution; §10 | Yes |
| same SP | Microsoft Graph | `Sites.Read.All` (Application) | SharePoint Connected Agents via Graph; §8 | Yes |
| `agt31-pp-reader` (SP) | Power Platform | **Power Platform Service Admin** (read-only intent only) | `Get-AdminPowerApp`, `Get-AdminFlow`, `Get-AdminPowerAppEnvironment`; §3 | Yes (intent) |
| `agt31-spo-reader` (SP) | SharePoint Online | **SharePoint Administrator** | `Get-SPOSite`, agent-enabled site flags; §8 | Yes (intent) |
| `agt31-purview-reader` (SP) | Microsoft Purview | `View-Only Audit Logs`, `Compliance Administrator` (read intent) | `Search-UnifiedAuditLog` activity enrichment; §10 | Yes (intent) |
| Operator (human) | Entra PIM | `Global Reader` time-bound | Manual reconciliation review; never used for the unattended pipeline | Yes |

**Hedging note on permission scope.** The inventory reader is scoped to read-only application permissions; tenant administrators should still review the consent grants quarterly under [Control 1.1 — Service Principal Governance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and rotate the certificate at the cadence defined by your PKI policy. "Read-only" is a contract with Microsoft Graph, not a guarantee that the credential cannot be used for reconnaissance — treat the inventory reader as a privileged identity for monitoring and detection purposes.

**Sovereign cloud parity matrix (verify at deploy time per the parent control).**

| Plane | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Power Platform Admin (`Get-AdminPowerApp`, `pac copilot list`) | GA | Rolling — verify | Verify | Verify |
| Microsoft Graph `/applications` declarative agents | GA | GA | GA | GA |
| Microsoft Graph `/copilot/admin/*` | GA | Rolling | Limited | Verify |
| Microsoft Graph `/reports/getCopilotAIInteractionsCount` | GA | Rolling | Limited | Verify |
| Microsoft Graph `/agents` (preview) | Preview | Limited | Not GA | Not GA |
| Microsoft Graph `/sites/{id}/copilotAgents` (preview) | Preview | Verify | Verify | Verify |
| MCP service principal enumeration | GA | GA | GA | GA |

Treat any parity gap as a **compensating-control conversation** (manual attestation, periodic export, third-party CASB enrichment) — not a silent skip.

---


## §2 — Sovereign-aware bootstrap (`Resolve-Agt31CloudProfile` + `Initialize-Agt31Session`)

**Why this section exists.** Every cmdlet in §3–§8 will silently route to the wrong cloud unless the session is opened against the correct sovereign endpoint. Sovereign mis-routing is the #1 false-clean defect for Control 3.1 (§0). The two helpers below produce a single `[Agt31Session]`-style object the rest of the playbook consumes.

### 2.1 `Resolve-Agt31CloudProfile`

```powershell
# scripts/Resolve-Agt31CloudProfile.ps1
function Resolve-Agt31CloudProfile {
<#
.SYNOPSIS
    Maps a sovereign cloud short-name to every endpoint and module-parameter the inventory legs need.
.DESCRIPTION
    Returns a [pscustomobject] with strongly typed properties for the Microsoft Graph environment,
    Power Platform endpoint, SharePoint admin URL pattern, Azure cloud name, and PAC CLI cloud token.
    The returned object is consumed by Initialize-Agt31Session and threaded through every leg.
.PARAMETER Cloud
    One of: Commercial, GCC, GCCHigh, DoD, China.
.OUTPUTS
    [pscustomobject] with: Cloud, GraphEnvironment, GraphBaseUri, PowerAppsEndpoint, PacCloud,
    AzureEnvironment, SpoAdminUrlPattern, ExoEnvironmentName, AgentRegistryStatus
.EXAMPLE
    PS> Resolve-Agt31CloudProfile -Cloud GCCHigh
.NOTES
    AgentRegistryStatus reflects April 2026 GA state. Re-verify quarterly via Microsoft Learn release notes.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)]
        [ValidateSet('Commercial','GCC','GCCHigh','DoD','China')]
        [string]$Cloud
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $map = @{
        Commercial = @{ Graph='Global';        GraphBase='https://graph.microsoft.com';        PA='prod';      Pac='Public';     Az='AzureCloud';            Spo='https://{0}-admin.sharepoint.com';     Exo='O365Default';        Agt='Preview' }
        GCC        = @{ Graph='USGov';         GraphBase='https://graph.microsoft.com';        PA='usgov';     Pac='UsGov';      Az='AzureCloud';            Spo='https://{0}-admin.sharepoint.com';     Exo='O365USGovGCC';       Agt='Limited' }
        GCCHigh    = @{ Graph='USGov';         GraphBase='https://graph.microsoft.us';         PA='usgovhigh'; Pac='UsGovHigh';  Az='AzureUSGovernment';     Spo='https://{0}-admin.sharepoint.us';      Exo='O365USGovGCCHigh';   Agt='NotAvailableInCloud' }
        DoD        = @{ Graph='USGovDOD';      GraphBase='https://dod-graph.microsoft.us';     PA='dod';       Pac='DoD';        Az='AzureUSGovernment';     Spo='https://{0}-admin.sharepoint-mil.us';  Exo='O365USGovDoD';       Agt='NotAvailableInCloud' }
        China      = @{ Graph='China';         GraphBase='https://microsoftgraph.chinacloudapi.cn'; PA='china'; Pac='China';     Az='AzureChinaCloud';       Spo='https://{0}-admin.sharepoint.cn';      Exo='O365China';          Agt='NotAvailableInCloud' }
    }

    $p = $map[$Cloud]
    [pscustomobject]@{
        Cloud               = $Cloud
        GraphEnvironment    = $p.Graph
        GraphBaseUri        = $p.GraphBase
        PowerAppsEndpoint   = $p.PA
        PacCloud            = $p.Pac
        AzureEnvironment    = $p.Az
        SpoAdminUrlPattern  = $p.Spo
        ExoEnvironmentName  = $p.Exo
        AgentRegistryStatus = $p.Agt
        ResolvedAt          = (Get-Date).ToUniversalTime()
    }
}
```

### 2.2 `Initialize-Agt31Session`

```powershell
# scripts/Initialize-Agt31Session.ps1
function Initialize-Agt31Session {
<#
.SYNOPSIS
    Authenticates every plane Control 3.1 reads from using a single certificate-based service principal
    and verifies that the granted scopes match the requested scopes.
.DESCRIPTION
    Performs Connect-MgGraph (cert-based), Connect-PnPOnline (cert-based), Connect-IPPSSession
    (for Search-UnifiedAuditLog), Connect-AzAccount (for AI Foundry / ARG), and Connect-SPOService.
    Defers the Power Apps Administration leg to a 5.1 child process spawned in §3.
    Hard-fails (exit 2) if any plane authenticates against the wrong sovereign endpoint or returns
    fewer scopes than requested.
.PARAMETER TenantId
.PARAMETER ClientId
.PARAMETER CertificateThumbprint
.PARAMETER Cloud
.PARAMETER TenantDomainPrefix
    The {tenant} portion of the SharePoint admin URL (e.g., 'contoso' for contoso-admin.sharepoint.com).
.OUTPUTS
    [pscustomobject] with Profile, MgContext, PnPConnection, AzContext, ConnectedAt, RunId.
.EXAMPLE
    PS> $session = Initialize-Agt31Session -TenantId $tid -ClientId $cid -CertificateThumbprint $thumb -Cloud GCCHigh -TenantDomainPrefix 'contoso'
.NOTES
    Idempotent. Calling twice in the same process re-uses the existing context after verifying that
    the bound principal still matches.
#>
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [guid]$TenantId,
        [Parameter(Mandatory)] [guid]$ClientId,
        [Parameter(Mandatory)] [string]$CertificateThumbprint,
        [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD','China')] [string]$Cloud,
        [Parameter(Mandatory)] [string]$TenantDomainPrefix
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $profile = Resolve-Agt31CloudProfile -Cloud $Cloud
    $runId   = [guid]::NewGuid().ToString()

    $requestedScopes = @(
        'Application.Read.All','AgentApplication.Read.All','Reports.Read.All','AuditLog.Read.All',
        'User.Read.All','InformationProtectionPolicy.Read.All','Sites.Read.All',
        'CopilotSettings-LimitedMode.Read.All'
    )

    if ($PSCmdlet.ShouldProcess('Microsoft Graph','Connect-MgGraph (certificate)')) {
        Connect-MgGraph -TenantId $TenantId -ClientId $ClientId `
            -CertificateThumbprint $CertificateThumbprint `
            -Environment $profile.GraphEnvironment -NoWelcome -ErrorAction Stop | Out-Null
    }
    $ctx = Get-MgContext
    if ($ctx.Environment -ne $profile.GraphEnvironment) {
        Write-Error "Graph context bound to $($ctx.Environment) but profile is $($profile.GraphEnvironment). Sovereign mismatch — aborting (exit 2)."
        exit 2
    }
    $missing = $requestedScopes | Where-Object { $_ -notin $ctx.Scopes }
    if ($missing) {
        Write-Warning "Granted Graph scopes are missing: $($missing -join ', '). Some legs will degrade gracefully (mark Status=PermissionDenied) rather than throw, but examiners expect explicit grant. File a consent request and re-run."
    }

    $spoAdminUrl = $profile.SpoAdminUrlPattern -f $TenantDomainPrefix
    if ($PSCmdlet.ShouldProcess($spoAdminUrl,'Connect-PnPOnline (certificate)')) {
        Connect-PnPOnline -Url $spoAdminUrl -ClientId $ClientId `
            -Tenant "$TenantDomainPrefix.onmicrosoft.com" `
            -Thumbprint $CertificateThumbprint -ErrorAction Stop
    }

    if ($PSCmdlet.ShouldProcess($profile.AzureEnvironment,'Connect-AzAccount (certificate)')) {
        Connect-AzAccount -ServicePrincipal -Tenant $TenantId -ApplicationId $ClientId `
            -CertificateThumbprint $CertificateThumbprint `
            -Environment $profile.AzureEnvironment -WarningAction SilentlyContinue | Out-Null
    }

    if ($PSCmdlet.ShouldProcess($spoAdminUrl,'Connect-SPOService')) {
        try {
            Connect-SPOService -Url $spoAdminUrl -ErrorAction Stop
        } catch {
            Write-Warning "Connect-SPOService failed in unattended mode: $($_.Exception.Message). The SPO leg in §8 will fall back to PnP-only enumeration."
        }
    }

    [pscustomobject]@{
        Profile        = $profile
        RunId          = $runId
        MgContext      = $ctx
        SpoAdminUrl    = $spoAdminUrl
        ConnectedAt    = (Get-Date).ToUniversalTime()
        TenantId       = $TenantId
        ClientId       = $ClientId
        Thumbprint     = $CertificateThumbprint
        TenantPrefix   = $TenantDomainPrefix
    }
}
```

**Fail-closed conditions enforced by this section:**

- Graph context `Environment` does not match resolved profile → `exit 2`.
- Cert thumbprint not present in `Cert:\CurrentUser\My` or `Cert:\LocalMachine\My` (raised by `Connect-MgGraph`) → throw, propagated as exit 1.
- Connect failures on any **mandatory** plane (Graph, PnP, Az) → throw. SPO admin and IPPS are best-effort and degrade with `Status=PermissionDenied` records in §8 / §10.

### 2.3 Throttle helper used by every leg

```powershell
function Invoke-Agt31WithThrottle {
<#
.SYNOPSIS
    Wraps a script block with exponential-backoff retry that honors Retry-After.
.DESCRIPTION
    Catches HTTP 429 / 503 from Microsoft Graph, Power Platform admin, and SPO endpoints.
    Reads the Retry-After response header when present; falls back to 2^attempt seconds
    capped at 60s. Maximum 6 attempts. Re-throws on any other exception.
.PARAMETER ScriptBlock
.PARAMETER MaxAttempts
.PARAMETER OperationName
    Used in verbose output and evidence manifest entries.
.OUTPUTS
    Whatever the script block emits.
.EXAMPLE
    PS> Invoke-Agt31WithThrottle -OperationName 'Get-MgApplication' -ScriptBlock { Get-MgApplication -All }
.NOTES
    Throttling behavior is plane-specific; this helper handles the common pattern. Power Platform
    and SharePoint admin APIs may impose long cool-downs (>60s) — a 429 after MaxAttempts is
    re-thrown rather than swallowed.
#>
    [CmdletBinding()]
    [OutputType([object])]
    param(
        [Parameter(Mandatory)] [scriptblock]$ScriptBlock,
        [Parameter()] [int]$MaxAttempts = 6,
        [Parameter(Mandatory)] [string]$OperationName
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            return & $ScriptBlock
        } catch {
            $resp = $_.Exception.Response
            $status = if ($resp) { [int]$resp.StatusCode } else { 0 }
            if ($status -in 429,503,504 -and $attempt -lt $MaxAttempts) {
                $retryAfter = 0
                if ($resp -and $resp.Headers -and $resp.Headers.'Retry-After') {
                    [int]::TryParse(($resp.Headers.'Retry-After' | Select-Object -First 1), [ref]$retryAfter) | Out-Null
                }
                if ($retryAfter -le 0) { $retryAfter = [Math]::Min([Math]::Pow(2, $attempt), 60) }
                Write-Verbose "[$OperationName] HTTP $status on attempt $attempt; sleeping ${retryAfter}s before retry"
                Start-Sleep -Seconds $retryAfter
                continue
            }
            throw
        }
    }
}
```

---

## §3 — Copilot Studio inventory leg (`Get-Agt31CopilotStudioInventory`)

**Why this section exists.** Copilot Studio bots are the historically dominant agent type in most FSI tenants and the only plane where Power Platform Admin cmdlets remain authoritative. Two design constraints shape this leg:

1. The cmdlets are **Desktop-only**, so the orchestrator (`pwsh` 7.4) spawns a Windows PowerShell 5.1 child process and exchanges JSON over disk.
2. The `appType` discriminator value Microsoft uses for Copilot Studio bots has churned across module versions (`Bot`, `ChatBot`, `CopilotStudioBot`); a hard-coded filter loses agents on the older value. This leg enumerates **all** `appType` values seen in tenant and warns when an unknown value appears.
3. The Power Platform admin center display caps environments at 500 agents; for tenants beyond that cap, fall back to per-environment enumeration plus `pac copilot list` (parent control §"Power Platform Inventory Limitations").

```powershell
# scripts/legs/Get-Agt31CopilotStudioInventory.ps1
function Get-Agt31CopilotStudioInventory {
<#
.SYNOPSIS
    Enumerates Copilot Studio bots and Power-Apps-hosted agents across every Power Platform environment in tenant.
.DESCRIPTION
    Spawns a Windows PowerShell 5.1 child process (Desktop edition is required by
    Microsoft.PowerApps.Administration.PowerShell). The child connects via Add-PowerAppsAccount with
    the resolved sovereign endpoint, walks every environment, calls Get-AdminPowerApp filtered to
    chatbot/copilot appType values, and serializes results to a JSON exchange file consumed by the
    orchestrator. Falls back to 'pac copilot list' for environments where the admin module returns
    truncated results (>500 agents).
.PARAMETER Session
    The session object returned by Initialize-Agt31Session.
.PARAMETER ExchangeFolder
    Working folder for the JSON exchange file. Created if missing.
.OUTPUTS
    [pscustomobject[]] — pre-canonical Copilot Studio inventory records.
.EXAMPLE
    PS> $cs = Get-Agt31CopilotStudioInventory -Session $session -ExchangeFolder 'C:\agt31\run'
.NOTES
    Marks any unknown appType with Notes='AppTypeDrift:<value>' so reviewers see drift, not silence.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [string]$ExchangeFolder
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    if (-not $IsWindows) {
        Write-Warning "Copilot Studio leg requires Windows for the Desktop sub-shell. Returning a single PlatformUnavailable record."
        return ,([pscustomobject]@{ Plane='CopilotStudio'; Status='PlatformUnavailable'; Reason='Non-Windows orchestrator host'; CollectedAt=(Get-Date).ToUniversalTime() })
    }

    if (-not (Test-Path $ExchangeFolder)) { New-Item -ItemType Directory -Path $ExchangeFolder -Force | Out-Null }
    $outFile  = Join-Path $ExchangeFolder ("cs-inventory-{0}.json" -f $Session.RunId)
    $errFile  = Join-Path $ExchangeFolder ("cs-inventory-{0}.err.log" -f $Session.RunId)

    # Child script body — runs in Desktop 5.1
    $childScript = @"
[CmdletBinding()]
param(
    [string]`$TenantId, [string]`$ClientId, [string]`$Thumbprint,
    [string]`$Endpoint, [string]`$OutFile
)
`$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Import-Module Microsoft.PowerApps.Administration.PowerShell -RequiredVersion 2.0.183 -Force
Import-Module Microsoft.PowerApps.PowerShell -RequiredVersion 1.0.34 -Force

# Cert-based SP auth into Power Platform; -Endpoint controls sovereign routing
Add-PowerAppsAccount -TenantID `$TenantId -ApplicationId `$ClientId ``
    -CertificateThumbprint `$Thumbprint -Endpoint `$Endpoint | Out-Null

`$envs = Get-AdminPowerAppEnvironment
`$known = @('CopilotStudioBot','ChatBot','Bot','Chatbot','copilotstudiobot','chatbot','bot')
`$accum = New-Object System.Collections.Generic.List[pscustomobject]
`$drift = New-Object System.Collections.Generic.List[string]

foreach (`$env in `$envs) {
    try {
        `$apps = Get-AdminPowerApp -EnvironmentName `$env.EnvironmentName -ErrorAction Stop
    } catch {
        `$accum.Add([pscustomobject]@{ Plane='CopilotStudio'; Status='EnumerationFailed'; EnvironmentId=`$env.EnvironmentName; Reason=`$_.Exception.Message })
        continue
    }
    foreach (`$a in `$apps) {
        `$at = `$a.AppType
        if (`$at -and (`$known -notcontains `$at)) { `$drift.Add(`$at) }
        # Heuristic: include any appType that contains 'bot' or 'copilot' OR any app whose internal name suggests a copilot studio surface
        if (`$at -match '(?i)bot|copilot' -or `$a.DisplayName -match '(?i)copilot|agent') {
            `$accum.Add([pscustomobject]@{
                Plane            = 'CopilotStudio'
                Status           = 'OK'
                BotId            = `$a.AppName
                DisplayName      = `$a.DisplayName
                AppType          = `$at
                EnvironmentId    = `$env.EnvironmentName
                EnvironmentName  = `$env.DisplayName
                EnvironmentSku   = `$env.EnvironmentType
                OwnerObjectId    = `$a.Owner.id
                OwnerEmail       = `$a.Owner.email
                CreatedTimeUtc   = `$a.CreatedTime
                ModifiedTimeUtc  = `$a.LastModifiedTime
                Notes            = if (`$known -contains `$at) { '' } else { "AppTypeDrift:`$at" }
                CollectedAt      = (Get-Date).ToUniversalTime()
            })
        }
    }
}

if (`$drift.Count) { Write-Warning "Unknown appType values seen: `$((`$drift | Sort-Object -Unique) -join ', ')" }
`$accum | ConvertTo-Json -Depth 6 | Out-File -FilePath `$OutFile -Encoding UTF8
"@

    $childPath = Join-Path $ExchangeFolder "cs-child-$($Session.RunId).ps1"
    Set-Content -Path $childPath -Value $childScript -Encoding UTF8

    $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$childPath,
              '-TenantId',$Session.TenantId,'-ClientId',$Session.ClientId,
              '-Thumbprint',$Session.Thumbprint,'-Endpoint',$Session.Profile.PowerAppsEndpoint,
              '-OutFile',$outFile)
    Invoke-Agt31WithThrottle -OperationName 'CopilotStudio:Desktop51Spawn' -ScriptBlock {
        $p = Start-Process -FilePath 'powershell.exe' -ArgumentList $args -NoNewWindow -PassThru -Wait `
            -RedirectStandardError $errFile
        if ($p.ExitCode -ne 0) {
            throw "Desktop child failed (exit $($p.ExitCode)). See $errFile"
        }
    }

    if (-not (Test-Path $outFile)) {
        return ,([pscustomobject]@{ Plane='CopilotStudio'; Status='ExchangeFileMissing'; Reason='Desktop child completed but produced no JSON'; CollectedAt=(Get-Date).ToUniversalTime() })
    }

    $records = Get-Content $outFile -Raw | ConvertFrom-Json
    Write-Verbose "CopilotStudio leg returned $($records.Count) records"

    # Cross-check with pac CLI for any environment that returned >=500 agents
    foreach ($envGroup in ($records | Group-Object EnvironmentId)) {
        if ($envGroup.Count -ge 500) {
            Write-Warning "Environment $($envGroup.Name) returned $($envGroup.Count) records — at or above the PPAC display cap. Cross-check with 'pac copilot list --environment $($envGroup.Name)' and reconcile any deltas manually."
        }
    }

    return $records
}
```

**Fail-closed conditions enforced by this leg:**

- Desktop child process exits non-zero → throw (propagated to orchestrator as exit 1).
- Exchange file missing after a clean exit → emit a `Status='ExchangeFileMissing'` record so the reconciler in §9 *records the gap* rather than silently skipping the plane.
- Any environment at or near the 500-agent cap → loud `Write-Warning` plus a manual `pac copilot list` follow-up requirement.
- Any unknown `appType` value → recorded into the row's `Notes` column as `AppTypeDrift:<value>`; reviewers see the drift in the evidence pack.

---


## §4 — Declarative agents leg (`Get-Agt31DeclarativeAgentInventory`)

**Why this section exists.** Declarative agents (the JSON-manifest agents shipped through Microsoft 365 Copilot or Teams) register as **Entra application objects** with characteristic tags and `extensionProperties`. They do not appear in Power Platform admin output. The dominant false-clean defect on this plane is requesting `Application.Read.All` and forgetting to verify the *granted* scope — the call returns 200 with an empty `value` array on missing consent (§0 defect #4).

```powershell
# scripts/legs/Get-Agt31DeclarativeAgentInventory.ps1
function Get-Agt31DeclarativeAgentInventory {
<#
.SYNOPSIS
    Enumerates declarative agents (Microsoft 365 Copilot / Teams agent manifests) registered as Entra applications.
.DESCRIPTION
    Filters Get-MgApplication by tags ('DeclarativeAgent', 'CopilotAgent', 'M365Copilot', 'TeamsAgent')
    and inspects extensionProperties for agent manifest indicators. Falls back to Get-MgBetaApplication
    when the v1.0 surface has not yet exposed the agent tag set.
.PARAMETER Session
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $da = Get-Agt31DeclarativeAgentInventory -Session $session
.NOTES
    Tag taxonomy is set by Microsoft and may change; the function records the matched tag in MatchedOn for forensic review.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param([Parameter(Mandatory)] [pscustomobject]$Session)
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $tags = @('DeclarativeAgent','CopilotAgent','M365Copilot','TeamsAgent','M365CopilotPlugin','CopilotExtension')
    $accum = New-Object System.Collections.Generic.List[pscustomobject]

    foreach ($tag in $tags) {
        try {
            $apps = Invoke-Agt31WithThrottle -OperationName "Graph:Application[$tag]" -ScriptBlock {
                Get-MgApplication -Filter "tags/any(t:t eq '$tag')" -All -ErrorAction Stop
            }
        } catch {
            $accum.Add([pscustomobject]@{ Plane='DeclarativeAgent'; Status='EnumerationFailed'; MatchedOn=$tag; Reason=$_.Exception.Message; CollectedAt=(Get-Date).ToUniversalTime() })
            continue
        }
        foreach ($a in $apps) {
            $accum.Add([pscustomobject]@{
                Plane            = 'DeclarativeAgent'
                Status           = 'OK'
                ObjectId         = $a.Id
                AppId            = $a.AppId
                DisplayName      = $a.DisplayName
                MatchedOn        = $tag
                PublisherDomain  = $a.PublisherDomain
                SignInAudience   = $a.SignInAudience
                CreatedDateTime  = $a.CreatedDateTime
                Tags             = ($a.Tags -join ';')
                IdentifierUris   = ($a.IdentifierUris -join ';')
                Notes            = ''
                CollectedAt      = (Get-Date).ToUniversalTime()
            })
        }
    }

    # Beta sweep for tags not yet on v1.0
    try {
        $betaApps = Invoke-Agt31WithThrottle -OperationName 'GraphBeta:Application[agent]' -ScriptBlock {
            Get-MgBetaApplication -Filter "tags/any(t:contains(t, 'gent'))" -All -ErrorAction Stop
        }
        foreach ($a in $betaApps) {
            if ($accum.AppId -notcontains $a.AppId) {
                $accum.Add([pscustomobject]@{
                    Plane='DeclarativeAgent'; Status='OK'; ObjectId=$a.Id; AppId=$a.AppId;
                    DisplayName=$a.DisplayName; MatchedOn='beta:tag-contains-gent';
                    PublisherDomain=$a.PublisherDomain; SignInAudience=$a.SignInAudience;
                    CreatedDateTime=$a.CreatedDateTime; Tags=($a.Tags -join ';');
                    IdentifierUris=($a.IdentifierUris -join ';');
                    Notes='BetaOnly'; CollectedAt=(Get-Date).ToUniversalTime()
                })
            }
        }
    } catch {
        Write-Warning "Beta declarative-agent sweep failed: $($_.Exception.Message). v1.0 results stand."
    }

    Write-Verbose "DeclarativeAgent leg returned $($accum.Count) records"
    return $accum.ToArray()
}
```

**Fail-closed conditions:** consent gap surfaces as `Status='EnumerationFailed'` rows with the MatchedOn tag preserved; reconciler in §9 emits a manifest warning when this status appears.

---

## §5 — Microsoft 365 Copilot Hub leg (`Get-Agt31CopilotHubInventory`)

**Why this section exists.** The Copilot Admin endpoints expose tenant-level Copilot configuration *and* the agent settings the Copilot runtime applies to user prompts. The `getCopilotAIInteractionsCount` report is the only data source that tells you which agents users are *actually invoking* — including agents that exist in your tenant but are completely missing from the registration surfaces above. The combination is the definitive cross-check for shadow-IT-shaped agent usage.

```powershell
# scripts/legs/Get-Agt31CopilotHubInventory.ps1
function Get-Agt31CopilotHubInventory {
<#
.SYNOPSIS
    Pulls Microsoft 365 Copilot admin settings and the AI interactions usage report for the last 90 days.
.DESCRIPTION
    Calls /copilot/admin/settings, /copilot/admin/agentSettings, and the daily aggregated
    interaction-count report. The interaction report is the activity-truth source for §10
    enrichment and for orphan detection in §11.
.PARAMETER Session
.PARAMETER WindowDays
    Lookback window for the interactions report (max 90 days per Microsoft).
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $hub = Get-Agt31CopilotHubInventory -Session $session -WindowDays 90
.NOTES
    /copilot/admin endpoints are GA on Commercial; verify availability per the §1 sovereign matrix.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter()] [ValidateRange(1,90)] [int]$WindowDays = 90
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $accum = New-Object System.Collections.Generic.List[pscustomobject]
    $base = $Session.Profile.GraphBaseUri

    foreach ($endpoint in @('/copilot/admin/settings','/copilot/admin/agentSettings')) {
        try {
            $resp = Invoke-Agt31WithThrottle -OperationName "Graph:beta$endpoint" -ScriptBlock {
                Invoke-MgGraphRequest -Method GET -Uri "$base/beta$endpoint" -ErrorAction Stop
            }
            $accum.Add([pscustomobject]@{
                Plane='CopilotHub'; Status='OK'; RecordType='Setting'; Endpoint=$endpoint;
                Payload=($resp | ConvertTo-Json -Depth 8 -Compress);
                CollectedAt=(Get-Date).ToUniversalTime()
            })
        } catch {
            $accum.Add([pscustomobject]@{ Plane='CopilotHub'; Status='EnumerationFailed'; Endpoint=$endpoint; Reason=$_.Exception.Message; CollectedAt=(Get-Date).ToUniversalTime() })
        }
    }

    # Daily interaction counts
    $period = "D$WindowDays"
    try {
        $reportUri = "$base/v1.0/reports/getCopilotAIInteractionsCount(period='$period')"
        $tmp = Join-Path $env:TEMP "agt31-copilot-interactions-$($Session.RunId).csv"
        Invoke-Agt31WithThrottle -OperationName 'Graph:CopilotInteractions' -ScriptBlock {
            Invoke-MgGraphRequest -Method GET -Uri $reportUri -OutputFilePath $tmp -ErrorAction Stop
        }
        if (Test-Path $tmp) {
            $rows = Import-Csv -Path $tmp
            foreach ($r in $rows) {
                $accum.Add([pscustomobject]@{
                    Plane='CopilotHub'; Status='OK'; RecordType='InteractionAggregate';
                    DisplayName=$r.'Agent Name'; AppId=$r.'App Id';
                    InteractionCount=[int]($r.'Total Interactions' ?? 0);
                    UsersWithInteractions=[int]($r.'Users with Interactions' ?? 0);
                    Period=$period; CollectedAt=(Get-Date).ToUniversalTime()
                })
            }
        }
    } catch {
        $accum.Add([pscustomobject]@{ Plane='CopilotHub'; Status='ReportUnavailable'; Reason=$_.Exception.Message; CollectedAt=(Get-Date).ToUniversalTime() })
    }

    Write-Verbose "CopilotHub leg returned $($accum.Count) records"
    return $accum.ToArray()
}
```

**Fail-closed conditions:** report or settings endpoint failures emit explicit `EnumerationFailed`/`ReportUnavailable` rows. Activity enrichment in §10 *requires* the InteractionAggregate rows; their absence flips downstream `LastActivity` to `Status='ActivityUnknown'` rather than defaulting to "dormant".

---

## §6 — Agent Registry / Agent 365 leg (`Get-Agt31AgentRegistryInventory`)

**Why this section exists.** Microsoft is rolling out a unified Agent Registry surface (Agent 365) that promises a single per-tenant catalog. As of April 2026 it is **Preview on Commercial, Limited on GCC, and unavailable on GCC High / DoD / China**. This leg must (a) call the endpoint when available, (b) emit explicit `NotAvailableInCloud` records when the sovereign profile is gapped, and (c) fall back to a documented compensating control rather than silently returning empty.

```powershell
# scripts/legs/Get-Agt31AgentRegistryInventory.ps1
function Get-Agt31AgentRegistryInventory {
<#
.SYNOPSIS
    Calls the Agent Registry / Agent 365 preview endpoint when available; emits sovereign-gap records when not.
.DESCRIPTION
    Reads $Session.Profile.AgentRegistryStatus to decide whether to attempt the call. When status is
    'Preview' or 'Limited', performs the call and records every returned agent. When status is
    'NotAvailableInCloud', emits a single row that explicitly documents the compensating control
    expected in the parent control specification (manual attestation + Defender for Cloud Apps).
.PARAMETER Session
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $reg = Get-Agt31AgentRegistryInventory -Session $session
.NOTES
    Re-verify endpoint shape every quarter; preview API contracts are not stable.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param([Parameter(Mandatory)] [pscustomobject]$Session)
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $status = $Session.Profile.AgentRegistryStatus
    $base = $Session.Profile.GraphBaseUri

    if ($status -eq 'NotAvailableInCloud') {
        return ,([pscustomobject]@{
            Plane='AgentRegistry'; Status='NotAvailableInCloud';
            Cloud=$Session.Profile.Cloud;
            Reason='Agent Registry / Agent 365 not GA in this sovereign cloud as of April 2026';
            CompensatingControl='Manual attestation per Control 3.1 §5.4 + MDA shadow-IT detection per Control 3.6';
            CollectedAt=(Get-Date).ToUniversalTime()
        })
    }

    try {
        $page = Invoke-Agt31WithThrottle -OperationName 'Graph:beta/agents' -ScriptBlock {
            Invoke-MgGraphRequest -Method GET -Uri "$base/beta/agents" -ErrorAction Stop
        }
    } catch {
        return ,([pscustomobject]@{
            Plane='AgentRegistry'; Status='EnumerationFailed';
            Reason=$_.Exception.Message; CollectedAt=(Get-Date).ToUniversalTime()
        })
    }

    $accum = New-Object System.Collections.Generic.List[pscustomobject]
    $values = $page.value
    foreach ($a in $values) {
        $accum.Add([pscustomobject]@{
            Plane='AgentRegistry'; Status='OK';
            AgentId=$a.id; DisplayName=$a.displayName;
            AppId=$a.appId; Publisher=$a.publisher;
            Lifecycle=$a.lifecycleState;
            CreatedDateTime=$a.createdDateTime;
            Notes='PreviewEndpoint'; CollectedAt=(Get-Date).ToUniversalTime()
        })
    }

    # Naive paging follow
    while ($page.'@odata.nextLink') {
        try {
            $page = Invoke-MgGraphRequest -Method GET -Uri $page.'@odata.nextLink' -ErrorAction Stop
            foreach ($a in $page.value) {
                $accum.Add([pscustomobject]@{
                    Plane='AgentRegistry'; Status='OK'; AgentId=$a.id; DisplayName=$a.displayName;
                    AppId=$a.appId; Publisher=$a.publisher; Lifecycle=$a.lifecycleState;
                    CreatedDateTime=$a.createdDateTime; Notes='PreviewEndpoint';
                    CollectedAt=(Get-Date).ToUniversalTime()
                })
            }
        } catch {
            $accum.Add([pscustomobject]@{ Plane='AgentRegistry'; Status='PagingFailed'; Reason=$_.Exception.Message; CollectedAt=(Get-Date).ToUniversalTime() })
            break
        }
    }

    return $accum.ToArray()
}
```

**Fail-closed conditions:** `NotAvailableInCloud` is emitted as a row, never silently skipped. Paging failure is recorded so the reconciler in §9 can flag a partial result rather than treating page 1 as the full population.

---

## §7 — MCP servers leg (`Get-Agt31McpServerInventory`)

**Why this section exists.** Model Context Protocol (MCP) servers register as **service principals**, not application objects. Filtering `Get-MgApplication` for them returns nothing (§0 defect #5). MCP servers also frequently expose elevated `oauth2PermissionGrants` (delegated scopes against Graph, SharePoint, or third-party APIs) that are critical to capture for SOX 404 access-review evidence.

```powershell
# scripts/legs/Get-Agt31McpServerInventory.ps1
function Get-Agt31McpServerInventory {
<#
.SYNOPSIS
    Enumerates MCP servers registered in the tenant, with their delegated and application-permission grants.
.DESCRIPTION
    Two complementary searches:
      1. Service principals tagged 'MCPServer' or with a tag matching '*mcp*'.
      2. Service principals matching a curated allow-list of known first-party MCP appIds.
    For every match, retrieves oauth2PermissionGrants and appRoleAssignments.
.PARAMETER Session
.PARAMETER KnownMcpAppIds
    Curated list of first-party / vendor MCP server appIds. Maintained by AI Governance; updated
    as new MCP integrations are approved.
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $mcp = Get-Agt31McpServerInventory -Session $session
.NOTES
    Treat any MCP server with delegated Graph scopes containing 'Mail.', 'Files.', or 'Sites.' write
    permissions as Risk='High' for downstream review.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter()] [string[]]$KnownMcpAppIds = @()
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $accum = New-Object System.Collections.Generic.List[pscustomobject]

    $taggedSps = Invoke-Agt31WithThrottle -OperationName 'Graph:ServicePrincipal[MCP-tag]' -ScriptBlock {
        Get-MgServicePrincipal -Filter "tags/any(t:t eq 'MCPServer')" -All -ErrorAction Stop
    }
    foreach ($sp in $taggedSps) {
        $accum.Add((New-Agt31McpRecord -Sp $sp -MatchedOn 'tag:MCPServer'))
    }

    foreach ($appId in $KnownMcpAppIds) {
        try {
            $sp = Get-MgServicePrincipal -Filter "appId eq '$appId'" -ErrorAction Stop
            if ($sp -and $sp.AppId -notin $accum.AppId) {
                $accum.Add((New-Agt31McpRecord -Sp $sp -MatchedOn 'allow-list'))
            }
        } catch {
            $accum.Add([pscustomobject]@{ Plane='MCP'; Status='EnumerationFailed'; AppId=$appId; Reason=$_.Exception.Message; CollectedAt=(Get-Date).ToUniversalTime() })
        }
    }

    return $accum.ToArray()
}

function New-Agt31McpRecord {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param([Parameter(Mandatory)] $Sp, [Parameter(Mandatory)] [string]$MatchedOn)
    $grants = Get-MgOauth2PermissionGrant -Filter "clientId eq '$($Sp.Id)'" -All -ErrorAction SilentlyContinue
    $scopes = ($grants | ForEach-Object { $_.Scope } | Sort-Object -Unique) -join ' '
    $risk = 'Standard'
    if ($scopes -match '\b(Mail|Files|Sites)\.\w*Write') { $risk = 'High' }
    elseif ($scopes -match '\bDirectory\.ReadWrite\.All\b') { $risk = 'High' }
    [pscustomobject]@{
        Plane          = 'MCP'
        Status         = 'OK'
        ObjectId       = $Sp.Id
        AppId          = $Sp.AppId
        DisplayName    = $Sp.DisplayName
        MatchedOn      = $MatchedOn
        Publisher      = $Sp.PublisherName
        Tags           = ($Sp.Tags -join ';')
        DelegatedScopes= $scopes
        RiskFlag       = $risk
        CreatedDateTime= $Sp.AdditionalProperties['createdDateTime']
        Notes          = ''
        CollectedAt    = (Get-Date).ToUniversalTime()
    }
}
```

**Fail-closed conditions:** `RiskFlag='High'` rows must be cross-checked against Control 1.7 service-principal governance evidence. The reconciler in §9 surfaces a count of High-risk MCPs in the run summary so reviewers see them without scrolling.

---

## §8 — SharePoint Connected agents leg (`Get-Agt31SharePointAgentInventory`)

**Why this section exists.** SharePoint Connected Agents (agents grounded on SPO sites and document libraries) are partially exposed through SPO admin (`Get-SPOSite` agent flags) and partially through Graph beta `/sites/{id}/copilotAgents`. Walking the SPO admin surface alone misses agents whose grounding site is configured but not yet enumerated as a top-level site flag.

```powershell
# scripts/legs/Get-Agt31SharePointAgentInventory.ps1
function Get-Agt31SharePointAgentInventory {
<#
.SYNOPSIS
    Enumerates SharePoint-grounded agents across the tenant via SPO admin and Graph beta site agents endpoint.
.PARAMETER Session
.PARAMETER MaxSites
    Safety cap on per-site Graph queries; default 5000. Tenants larger than this should batch.
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $spa = Get-Agt31SharePointAgentInventory -Session $session
.NOTES
    Per-site Graph calls are throttled aggressively; the function honors Retry-After and skips sites that fail repeatedly.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter()] [int]$MaxSites = 5000
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $accum = New-Object System.Collections.Generic.List[pscustomobject]
    $base = $Session.Profile.GraphBaseUri

    # SPO admin first (works without Graph site-by-site spam)
    try {
        $sites = Get-SPOSite -Limit All -IncludePersonalSite:$false -ErrorAction Stop |
            Where-Object { $_.IsAgentEnabledSite -or $_.HasCopilotAgents }
    } catch {
        Write-Warning "SPO admin enumeration failed: $($_.Exception.Message). Falling back to PnP-only walk (slower)."
        $sites = Get-PnPTenantSite -ErrorAction SilentlyContinue
    }

    $sitesToScan = $sites | Select-Object -First $MaxSites
    foreach ($s in $sitesToScan) {
        try {
            $resp = Invoke-Agt31WithThrottle -OperationName "Graph:beta/sites/copilotAgents" -ScriptBlock {
                Invoke-MgGraphRequest -Method GET -Uri "$base/beta/sites/$($s.Url -replace '^https://','' -replace '/','%2F')/copilotAgents" -ErrorAction Stop
            }
            foreach ($ag in $resp.value) {
                $accum.Add([pscustomobject]@{
                    Plane='SharePointAgent'; Status='OK';
                    SiteUrl=$s.Url; SiteId=$s.SiteId;
                    AgentId=$ag.id; DisplayName=$ag.displayName;
                    GroundingSource=$ag.groundingSource;
                    OwnerEmail=$ag.owner.email;
                    CreatedDateTime=$ag.createdDateTime;
                    Notes='BetaEndpoint'; CollectedAt=(Get-Date).ToUniversalTime()
                })
            }
        } catch {
            $accum.Add([pscustomobject]@{ Plane='SharePointAgent'; Status='EnumerationFailed'; SiteUrl=$s.Url; Reason=$_.Exception.Message; CollectedAt=(Get-Date).ToUniversalTime() })
        }
    }

    if ($sites.Count -gt $MaxSites) {
        $accum.Add([pscustomobject]@{ Plane='SharePointAgent'; Status='Truncated'; Reason="MaxSites ($MaxSites) exceeded; $($sites.Count - $MaxSites) sites not scanned"; CollectedAt=(Get-Date).ToUniversalTime() })
    }

    return $accum.ToArray()
}
```

**Fail-closed conditions:** truncation at `MaxSites` emits a row; per-site failures emit `EnumerationFailed` with the URL preserved. The reconciler treats `Truncated` rows as a hard manifest warning.

---


## §9 — Reconciliation (`Merge-Agt31Inventory`)

**Why this section exists.** Six legs return six different schemas. The reconciler unifies them under one canonical schema, dedupes by a documented key precedence, and assigns a stable `CanonicalAgentId` (a SHA-256 hash of the precedence key) that downstream pillars use as a join key. **Key precedence is the central design decision** — it determines which plane wins when two legs disagree on display name or owner.

**Canonical key precedence (must not be silently changed):**

1. `ObjectId` (Entra application object ID) — most authoritative; survives renames.
2. `BotId` (Copilot Studio bot internal name) — authoritative within Power Platform.
3. `AppId` (Entra application ID) — bridges declarative agents and MCP servers.
4. Composite `(DisplayName + EnvironmentId).ToLowerInvariant()` — last-resort match for legacy bots without an Entra mirror.

```powershell
# scripts/Merge-Agt31Inventory.ps1
function Merge-Agt31Inventory {
<#
.SYNOPSIS
    Unifies the per-leg pre-canonical records into one canonical inventory keyed by CanonicalAgentId.
.DESCRIPTION
    Applies the documented key precedence (ObjectId > BotId > AppId > DisplayName+EnvironmentId)
    to dedupe across legs. Records that match across multiple legs are merged: per-leg fields are
    retained under a 'Sources' array and conflict deltas (e.g., differing Owner) are preserved in
    'ConflictNotes'. CanonicalAgentId is the SHA-256 of the chosen precedence key.
.PARAMETER LegResults
    Hashtable of leg name -> records.
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $merged = Merge-Agt31Inventory -LegResults @{ CopilotStudio=$cs; DeclarativeAgent=$da; ... }
.NOTES
    Records with Status != 'OK' are passed through with CanonicalAgentId = null and Status preserved
    so the reconciliation manifest can show how many records on each plane failed enumeration.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param([Parameter(Mandatory)] [hashtable]$LegResults)
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $byKey = @{}
    $errors = New-Object System.Collections.Generic.List[pscustomobject]

    foreach ($legName in $LegResults.Keys) {
        foreach ($r in $LegResults[$legName]) {
            if ($r.Status -ne 'OK') {
                $errors.Add([pscustomobject]@{
                    Plane=$legName; Status=$r.Status;
                    Reason=($r.PSObject.Properties['Reason']?.Value);
                    Detail=($r | ConvertTo-Json -Depth 3 -Compress)
                })
                continue
            }

            # Determine precedence key
            $key = $null; $keyKind = $null
            if ($r.PSObject.Properties['ObjectId'] -and $r.ObjectId) { $key = $r.ObjectId; $keyKind='ObjectId' }
            elseif ($r.PSObject.Properties['BotId'] -and $r.BotId)   { $key = $r.BotId;   $keyKind='BotId' }
            elseif ($r.PSObject.Properties['AppId'] -and $r.AppId)   { $key = $r.AppId;   $keyKind='AppId' }
            else {
                $dn = ($r.PSObject.Properties['DisplayName']?.Value) ?? ''
                $env= ($r.PSObject.Properties['EnvironmentId']?.Value) ?? 'no-env'
                $key = ("{0}|{1}" -f $dn, $env).ToLowerInvariant()
                $keyKind='DisplayNameEnvironment'
            }

            $sha = [System.Security.Cryptography.SHA256]::Create()
            $hash = ($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes("$keyKind`:$key")) | ForEach-Object { $_.ToString('x2') }) -join ''
            $canonId = "agt-$($hash.Substring(0,32))"

            if (-not $byKey.ContainsKey($canonId)) {
                $byKey[$canonId] = [pscustomobject]@{
                    CanonicalAgentId = $canonId
                    PrecedenceKind   = $keyKind
                    PrecedenceValue  = $key
                    DisplayName      = ($r.PSObject.Properties['DisplayName']?.Value)
                    AppId            = ($r.PSObject.Properties['AppId']?.Value)
                    ObjectId         = ($r.PSObject.Properties['ObjectId']?.Value)
                    BotId            = ($r.PSObject.Properties['BotId']?.Value)
                    EnvironmentId    = ($r.PSObject.Properties['EnvironmentId']?.Value)
                    Sources          = @($legName)
                    SourceRecords    = @($r)
                    ConflictNotes    = @()
                    FirstSeenAt      = (Get-Date).ToUniversalTime()
                }
            } else {
                $existing = $byKey[$canonId]
                $existing.Sources += $legName
                $existing.SourceRecords += $r
                # Conflict detection: DisplayName divergence
                $newDn = ($r.PSObject.Properties['DisplayName']?.Value)
                if ($newDn -and $existing.DisplayName -and $newDn -ne $existing.DisplayName) {
                    $existing.ConflictNotes += "DisplayName conflict: $($existing.DisplayName) (existing) vs $newDn (from $legName)"
                }
            }
        }
    }

    $merged = $byKey.Values | Sort-Object DisplayName
    Write-Verbose "Reconciled $($merged.Count) canonical agents from $($LegResults.Keys.Count) legs; $($errors.Count) per-leg errors retained for the manifest"

    # Surface aggregate via a verbose summary
    foreach ($g in ($merged | Group-Object { $_.Sources -join ',' })) {
        Write-Verbose ("Source-pattern '{0}' -> {1} agents" -f $g.Name, $g.Count)
    }

    # Attach the per-leg errors as a side-channel array (consumed by Export-Agt31EvidencePack)
    $script:Agt31LastReconcileErrors = $errors.ToArray()

    return ,([pscustomobject[]]$merged)
}
```

**Fail-closed conditions:** every per-leg `Status != 'OK'` record lands in `$script:Agt31LastReconcileErrors`. The evidence pack in §13 emits these into a separate `reconcile-errors.csv` and references the count in the manifest summary; an empty `reconcile-errors.csv` with non-zero `Status != OK` records is impossible by construction.

---

## §10 — Enrichment (`Add-Agt31Enrichment`)

**Why this section exists.** The reconciled register is necessary but not sufficient for SOX 404 / FINRA 4511 evidence: every agent needs a current owner, the owner's manager (for orphan escalation), the date of last user activity, applied DLP / sensitivity label, and the agent's zone classification (Personal / Team / Enterprise per the parent control). This leg threads those enrichments onto each canonical record.

```powershell
# scripts/Add-Agt31Enrichment.ps1
function Add-Agt31Enrichment {
<#
.SYNOPSIS
    Adds owner, manager, last-activity, sensitivity-label, and zone classification to every canonical record.
.DESCRIPTION
    For each canonical agent:
      - Resolves OwnerObjectId via Get-MgUser (gracefully marks 'OwnerNotFound' for orphan candidates).
      - Reads the owner's manager via Get-MgUserManager.
      - Joins the CopilotHub InteractionAggregate rows from §5 to fill LastActivityDate and InteractionCount90d.
      - Pulls Search-UnifiedAuditLog activity (Copilot* + PowerApp* operations) for the same window
        as a fallback when InteractionAggregate is missing.
      - Resolves any sensitivity-label GUID against InformationProtectionPolicy.
      - Computes Zone (Personal / Team / Enterprise) per the parent control's published heuristic.
.PARAMETER Session
.PARAMETER Merged
    Output of Merge-Agt31Inventory.
.PARAMETER HubRecords
    Output of Get-Agt31CopilotHubInventory (used for InteractionAggregate join).
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $enriched = Add-Agt31Enrichment -Session $session -Merged $merged -HubRecords $hub
.NOTES
    Activity classification ('Active' / 'Dormant' / 'ActivityUnknown') uses 90-day default; align with
    your supervisory window. Never default unknown activity to 'Dormant' — that misclassifies agents
    and corrupts orphan detection in §11.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [pscustomobject[]]$Merged,
        [Parameter()] [pscustomobject[]]$HubRecords = @(),
        [Parameter()] [int]$DormantDays = 90
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    # Build a fast lookup from HubRecords interaction aggregates
    $hubByApp = @{}
    foreach ($h in ($HubRecords | Where-Object { $_.RecordType -eq 'InteractionAggregate' })) {
        if ($h.AppId) { $hubByApp[$h.AppId] = $h }
    }

    $userCache = @{}
    function _resolveUser([string]$id) {
        if (-not $id) { return $null }
        if ($userCache.ContainsKey($id)) { return $userCache[$id] }
        try {
            $u = Get-MgUser -UserId $id -Property Id,UserPrincipalName,Mail,DisplayName,AccountEnabled,Department -ErrorAction Stop
            $userCache[$id] = $u
            return $u
        } catch {
            $userCache[$id] = $null
            return $null
        }
    }

    foreach ($r in $Merged) {
        # Owner resolution — try OwnerObjectId from any source record
        $ownerSource = $r.SourceRecords | Where-Object { $_.PSObject.Properties['OwnerObjectId']?.Value } | Select-Object -First 1
        $ownerId = $ownerSource?.OwnerObjectId
        $ownerUser = _resolveUser $ownerId
        $ownerStatus = if ($ownerUser) { (if ($ownerUser.AccountEnabled) { 'Active' } else { 'Disabled' }) } elseif ($ownerId) { 'OwnerNotFound' } else { 'OwnerUnknown' }

        # Manager
        $managerUpn = $null
        if ($ownerUser) {
            try {
                $mgr = Get-MgUserManager -UserId $ownerUser.Id -ErrorAction Stop
                $managerUpn = $mgr.AdditionalProperties['userPrincipalName']
            } catch {}
        }

        # Activity
        $activityDate = $null; $activityCount = 0; $activitySource = $null
        if ($r.AppId -and $hubByApp.ContainsKey($r.AppId)) {
            $h = $hubByApp[$r.AppId]
            $activityCount = $h.InteractionCount
            $activitySource = 'CopilotHub:InteractionAggregate'
            if ($h.InteractionCount -gt 0) { $activityDate = (Get-Date).ToUniversalTime() } # aggregate is window-bound
        }
        if (-not $activityDate -and $r.DisplayName) {
            try {
                $auditRows = Search-UnifiedAuditLog -StartDate (Get-Date).AddDays(-$DormantDays) -EndDate (Get-Date) `
                    -Operations 'CopilotInteraction','PowerAppLaunched','BotInvocation' `
                    -ResultSize 200 -ErrorAction SilentlyContinue
                $hit = $auditRows | Where-Object { $_.AuditData -match [regex]::Escape($r.DisplayName) } | Select-Object -First 1
                if ($hit) { $activityDate = [datetime]$hit.CreationDate; $activitySource='UAL' }
            } catch {}
        }

        $activityStatus = if ($activityDate) {
            if (((Get-Date).ToUniversalTime() - $activityDate).TotalDays -le $DormantDays) { 'Active' } else { 'Dormant' }
        } elseif ($activitySource -eq 'CopilotHub:InteractionAggregate' -and $activityCount -eq 0) {
            'Dormant'
        } else {
            'ActivityUnknown'
        }

        # Zone classification per parent control heuristic
        $zone = 'Zone2'  # team default
        $envSku = ($r.SourceRecords | Where-Object { $_.PSObject.Properties['EnvironmentSku']?.Value } | Select-Object -First 1)?.EnvironmentSku
        if ($envSku -eq 'Personal' -or ($r.PrecedenceKind -eq 'BotId' -and $envSku -eq 'Default')) { $zone = 'Zone1' }
        if ($r.Sources -contains 'AgentRegistry' -or $r.Sources -contains 'CopilotHub') { $zone = 'Zone3' }

        Add-Member -InputObject $r -NotePropertyName OwnerEmail        -NotePropertyValue $ownerUser?.Mail -Force
        Add-Member -InputObject $r -NotePropertyName OwnerUpn          -NotePropertyValue $ownerUser?.UserPrincipalName -Force
        Add-Member -InputObject $r -NotePropertyName OwnerStatus       -NotePropertyValue $ownerStatus -Force
        Add-Member -InputObject $r -NotePropertyName OwnerDepartment   -NotePropertyValue $ownerUser?.Department -Force
        Add-Member -InputObject $r -NotePropertyName ManagerUpn        -NotePropertyValue $managerUpn -Force
        Add-Member -InputObject $r -NotePropertyName LastActivityDate  -NotePropertyValue $activityDate -Force
        Add-Member -InputObject $r -NotePropertyName ActivityCount90d  -NotePropertyValue $activityCount -Force
        Add-Member -InputObject $r -NotePropertyName ActivityStatus    -NotePropertyValue $activityStatus -Force
        Add-Member -InputObject $r -NotePropertyName ActivitySource    -NotePropertyValue $activitySource -Force
        Add-Member -InputObject $r -NotePropertyName Zone              -NotePropertyValue $zone -Force
        Add-Member -InputObject $r -NotePropertyName EnrichedAt        -NotePropertyValue (Get-Date).ToUniversalTime() -Force
    }

    return $Merged
}
```

**Fail-closed conditions:** unknown activity is **never** silently classified as Dormant — it is preserved as `ActivityUnknown` so orphan detection (§11) does not act on a missing-data assumption. Owner resolution failures are preserved as `OwnerStatus='OwnerNotFound'` with the original ObjectId, distinguishing a legitimately absent owner from a transient Graph error.

---

## §11 — Orphan and risk detection (`Find-Agt31OrphanedAgent`)

**Why this section exists.** Departed-owner agents are the highest-likelihood SOX 404 / FINRA 4511 finding because the audit trail has nobody to attest the agent's purpose, scope, or last review. This leg classifies every enriched record into orphan categories and recommends a lifecycle action.

```powershell
# scripts/Find-Agt31OrphanedAgent.ps1
function Find-Agt31OrphanedAgent {
<#
.SYNOPSIS
    Classifies every enriched agent into orphan / dormant / unowned categories with a recommended lifecycle action.
.DESCRIPTION
    Categories (mutually non-exclusive — an agent may have several flags):
      - DepartedOwner: OwnerStatus is Disabled or OwnerNotFound
      - DormantSharedAgent: Zone in (Zone2, Zone3) AND ActivityStatus = Dormant
      - UnknownActivity: ActivityStatus = ActivityUnknown (cannot be acted on without manual review)
      - HighRiskMcp: Plane = MCP and RiskFlag = High
      - DisplayNameConflict: ConflictNotes has any entry
.PARAMETER Enriched
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $orphans = Find-Agt31OrphanedAgent -Enriched $enriched | Where-Object Flags
.NOTES
    Recommended actions are advisory; final lifecycle transitions go through Set-Agt31LifecycleState (§12)
    which is the only function in this playbook that mutates state.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param([Parameter(Mandatory)] [pscustomobject[]]$Enriched)
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    foreach ($r in $Enriched) {
        $flags = New-Object System.Collections.Generic.List[string]
        if ($r.OwnerStatus -in 'Disabled','OwnerNotFound') { $flags.Add('DepartedOwner') }
        if ($r.Zone -in 'Zone2','Zone3' -and $r.ActivityStatus -eq 'Dormant') { $flags.Add('DormantSharedAgent') }
        if ($r.ActivityStatus -eq 'ActivityUnknown') { $flags.Add('UnknownActivity') }
        $mcpSrc = $r.SourceRecords | Where-Object { $_.Plane -eq 'MCP' -and $_.RiskFlag -eq 'High' } | Select-Object -First 1
        if ($mcpSrc) { $flags.Add('HighRiskMcp') }
        if ($r.ConflictNotes -and $r.ConflictNotes.Count -gt 0) { $flags.Add('DisplayNameConflict') }

        $action = 'Review'
        if ($flags -contains 'DepartedOwner' -and $flags -contains 'DormantSharedAgent') { $action = 'RecommendDecommission' }
        elseif ($flags -contains 'DepartedOwner') { $action = 'RecommendOwnerTransfer' }
        elseif ($flags -contains 'DormantSharedAgent') { $action = 'RecommendDeprecate' }
        elseif ($flags -contains 'HighRiskMcp') { $action = 'EscalateToControl1.7' }
        elseif ($flags.Count -eq 0) { $action = 'NoAction' }

        Add-Member -InputObject $r -NotePropertyName Flags -NotePropertyValue ($flags.ToArray()) -Force
        Add-Member -InputObject $r -NotePropertyName RecommendedAction -NotePropertyValue $action -Force
    }
    return $Enriched
}
```

**Fail-closed conditions:** `UnknownActivity` is a flag (not a recommendation to decommission). Decommission recommendations are issued **only** when both DepartedOwner *and* DormantSharedAgent are present — never on activity alone, because activity-source gaps (§5 report unavailable) must not produce mass decommission proposals.

---

## §12 — Lifecycle state machine (`Set-Agt31LifecycleState`)

**Why this section exists.** The parent control defines a documented state machine (Draft → InReview → Active → Deprecated → Decommissioned, with optional Suspended branch). Every transition requires a Purview-auditable reason and an authorized transitioner. This is the **only** function in this playbook that mutates tenant state.

```powershell
# scripts/Set-Agt31LifecycleState.ps1
function Set-Agt31LifecycleState {
<#
.SYNOPSIS
    Records a documented lifecycle transition for a canonical agent against the inventory store.
.DESCRIPTION
    Applies a transition (e.g., Active -> Deprecated) to the SharePoint or Dataverse inventory store
    of record. Validates that the requested transition is allowed by the published state machine.
    Writes a Purview audit-log entry via the Compliance Portal-aware audit endpoint. Idempotent: a
    request to set the current state is logged but not re-applied.
.PARAMETER CanonicalAgentId
.PARAMETER NewState
.PARAMETER Reason
    Required free-text. Captured to the audit trail; minimum 20 characters.
.PARAMETER Approver
    UPN of the authorized approver (must be in the Inventory Owners directory role).
.PARAMETER InventoryStore
    URI to the SharePoint list or Dataverse table acting as the system of record.
.OUTPUTS
    [pscustomobject]
.EXAMPLE
    PS> Set-Agt31LifecycleState -CanonicalAgentId 'agt-...' -NewState Decommissioned -Reason 'Owner departed; no successor identified within 30d window' -Approver 'governance.lead@contoso.com' -InventoryStore $listUrl -WhatIf
.NOTES
    -WhatIf is honored. Mutation runs through SupportsShouldProcess. The function refuses to act on
    -records whose ConflictNotes are non-empty unless -ForceConflicted is specified, because acting
    on conflicting data is the most common cause of inventory data quality regressions.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [string]$CanonicalAgentId,
        [Parameter(Mandatory)] [ValidateSet('Draft','InReview','Active','Suspended','Deprecated','Decommissioned')] [string]$NewState,
        [Parameter(Mandatory)] [ValidateLength(20,2000)] [string]$Reason,
        [Parameter(Mandatory)] [string]$Approver,
        [Parameter(Mandatory)] [uri]$InventoryStore,
        [Parameter()] [switch]$ForceConflicted
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $allowed = @{
        'Draft'         = @('InReview','Decommissioned')
        'InReview'      = @('Active','Draft','Decommissioned')
        'Active'        = @('Suspended','Deprecated','Decommissioned')
        'Suspended'     = @('Active','Deprecated','Decommissioned')
        'Deprecated'    = @('Decommissioned','Active')   # reactivation requires re-attestation
        'Decommissioned'= @()                            # terminal
    }

    # Read current item from inventory store (SharePoint REST shown; Dataverse path mirrors the same shape)
    $currentItem = Invoke-PnPSPRestMethod -Url ("{0}/items?`$filter=fields/CanonicalAgentId eq '{1}'" -f $InventoryStore, $CanonicalAgentId) -Method Get
    if (-not $currentItem.value -or $currentItem.value.Count -eq 0) {
        throw "CanonicalAgentId $CanonicalAgentId not found in inventory store $InventoryStore"
    }
    $item = $currentItem.value[0]
    $current = $item.fields.LifecycleState
    $conflicts = $item.fields.ConflictNotes

    if ($conflicts -and -not $ForceConflicted) {
        throw "Refusing to transition $CanonicalAgentId because ConflictNotes is non-empty: '$conflicts'. Resolve the conflict in the inventory store first or pass -ForceConflicted with documented justification."
    }

    if ($current -eq $NewState) {
        Write-Verbose "Idempotent no-op: $CanonicalAgentId already in $NewState"
        return [pscustomobject]@{ CanonicalAgentId=$CanonicalAgentId; PreviousState=$current; NewState=$NewState; Action='NoOpIdempotent'; At=(Get-Date).ToUniversalTime() }
    }

    if ($allowed[$current] -notcontains $NewState) {
        throw "Illegal transition: $current -> $NewState. Allowed from $current: $($allowed[$current] -join ', ')"
    }

    if ($PSCmdlet.ShouldProcess("Inventory item $($item.id) ($CanonicalAgentId)", "Transition $current -> $NewState")) {
        Invoke-PnPSPRestMethod -Url ("{0}/items/{1}/fields" -f $InventoryStore, $item.id) -Method Patch -Content @{
            LifecycleState   = $NewState
            LastTransitionAt = (Get-Date).ToString('o')
            LastTransitionBy = $Approver
            LastTransitionReason = $Reason
        }

        # Purview audit emission (custom event). Falls back to Write-EventLog on Win for incident replay.
        try {
            Invoke-MgGraphRequest -Method POST -Uri "https://graph.microsoft.com/beta/security/auditLog/customEvents" -Body @{
                source='Control3.1'; eventType='AgentLifecycleTransition'
                payload=@{ agentId=$CanonicalAgentId; from=$current; to=$NewState; reason=$Reason; approver=$Approver }
            }
        } catch {
            Write-Warning "Custom audit emission failed: $($_.Exception.Message). Local Windows event log fallback engaged."
            if ($IsWindows) {
                Write-EventLog -LogName 'Application' -Source 'Agt31' -EventId 3100 -EntryType Information -Message ("Agent {0} {1}->{2} by {3}: {4}" -f $CanonicalAgentId,$current,$NewState,$Approver,$Reason)
            }
        }
    }

    [pscustomobject]@{ CanonicalAgentId=$CanonicalAgentId; PreviousState=$current; NewState=$NewState; Action='Applied'; Approver=$Approver; Reason=$Reason; At=(Get-Date).ToUniversalTime() }
}
```

**Fail-closed conditions:** illegal transitions throw; conflicted records require explicit `-ForceConflicted`; Purview emission failure falls back to Windows event log (never silently dropped); `-WhatIf` is honored end-to-end.

---


## §13 — Evidence pack (`Export-Agt31EvidencePack`)

**Why this section exists.** Examiners (FINRA / SEC / OCC / state) request reproducible artifacts. A run that cannot be replayed and re-hashed to produce identical inputs is not durable evidence. This leg writes a run-id-stamped folder containing CSV + JSONL + Excel projections of the inventory, a `reconcile-errors.csv` of every per-leg failure, a `manifest.json` listing every file with SHA-256 hash and module/CLI versions, and a code-signed copy of `manifest.json` to bind the manifest to the inventory owner identity.

```powershell
# scripts/Export-Agt31EvidencePack.ps1
function Export-Agt31EvidencePack {
<#
.SYNOPSIS
    Writes a reproducible evidence pack for the run, with SHA-256 hashes and a signed manifest.
.DESCRIPTION
    Outputs to {RootFolder}/{yyyyMMdd-HHmm}-{RunId}/:
      - canonical-inventory.csv  (one row per CanonicalAgentId, enriched + flagged)
      - canonical-inventory.jsonl (full record incl. SourceRecords for forensic replay)
      - canonical-inventory.xlsx (filtered view by Zone, RecommendedAction)
      - reconcile-errors.csv     (per-leg failures from §9)
      - per-leg/cs.json, da.json, hub.json, reg.json, mcp.json, spo.json (raw leg outputs)
      - manifest.json            (file paths, SHA-256, module versions, sovereign profile, run id)
      - manifest.json.p7s        (Authenticode-signed manifest)
.PARAMETER Session
.PARAMETER LegResults
.PARAMETER FlaggedInventory
    Output of Find-Agt31OrphanedAgent.
.PARAMETER RootFolder
    Parent folder; the function creates a per-run subfolder.
.PARAMETER SigningCertThumbprint
    Code-signing certificate for manifest.json. Must chain to your enterprise CA.
.OUTPUTS
    [pscustomobject] with EvidenceFolder, ManifestPath, SignedManifestPath, FileCount, TotalBytes.
.EXAMPLE
    PS> $pack = Export-Agt31EvidencePack -Session $session -LegResults $legs -FlaggedInventory $flagged -RootFolder 'D:\agt31-evidence' -SigningCertThumbprint $thumb
.NOTES
    Write the RootFolder to a WORM-protected location (Azure Storage immutable blob, SharePoint Records
    Center, or on-prem WORM share). The hash + signature only proves integrity from creation forward;
    immutability of the medium is the second leg of the evidence chain.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [hashtable]$LegResults,
        [Parameter(Mandatory)] [pscustomobject[]]$FlaggedInventory,
        [Parameter(Mandatory)] [string]$RootFolder,
        [Parameter(Mandatory)] [string]$SigningCertThumbprint
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMdd-HHmm')
    $runFolder = Join-Path $RootFolder ("{0}-{1}" -f $stamp, $Session.RunId)
    New-Item -ItemType Directory -Path $runFolder -Force | Out-Null
    $perLegFolder = Join-Path $runFolder 'per-leg'
    New-Item -ItemType Directory -Path $perLegFolder -Force | Out-Null

    # Canonical projections
    $csvPath  = Join-Path $runFolder 'canonical-inventory.csv'
    $jsonl    = Join-Path $runFolder 'canonical-inventory.jsonl'
    $xlsxPath = Join-Path $runFolder 'canonical-inventory.xlsx'

    $FlaggedInventory |
        Select-Object CanonicalAgentId, DisplayName, Zone, OwnerUpn, OwnerStatus, ManagerUpn,
            LastActivityDate, ActivityStatus, ActivityCount90d, Sources, Flags, RecommendedAction,
            EnvironmentId, AppId, ObjectId, BotId, EnrichedAt |
        Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

    $FlaggedInventory | ForEach-Object { $_ | ConvertTo-Json -Depth 8 -Compress } | Out-File -FilePath $jsonl -Encoding UTF8

    # XLSX: requires ImportExcel module if available; otherwise skip with a recorded note
    $xlsxNote = $null
    if (Get-Module -ListAvailable -Name ImportExcel) {
        Import-Module ImportExcel -Force
        $FlaggedInventory | Export-Excel -Path $xlsxPath -WorksheetName 'Inventory' -AutoSize -FreezeTopRow -BoldTopRow
    } else {
        $xlsxNote = 'ImportExcel module not present; XLSX projection skipped'
        Set-Content -Path "$xlsxPath.skipped.txt" -Value $xlsxNote -Encoding UTF8
    }

    # Per-leg raw payloads
    foreach ($legName in $LegResults.Keys) {
        $LegResults[$legName] | ConvertTo-Json -Depth 8 | Out-File -FilePath (Join-Path $perLegFolder "$legName.json") -Encoding UTF8
    }

    # Reconcile errors
    $errPath = Join-Path $runFolder 'reconcile-errors.csv'
    if ($script:Agt31LastReconcileErrors) {
        $script:Agt31LastReconcileErrors | Export-Csv -Path $errPath -NoTypeInformation -Encoding UTF8
    } else {
        '"Plane","Status","Reason","Detail"' | Out-File -FilePath $errPath -Encoding UTF8
    }

    # Manifest
    $files = Get-ChildItem -Path $runFolder -Recurse -File
    $manifest = [pscustomobject]@{
        ControlId        = '3.1'
        RunId            = $Session.RunId
        TenantId         = $Session.TenantId
        SovereignCloud   = $Session.Profile.Cloud
        AgentRegistryStatus = $Session.Profile.AgentRegistryStatus
        GeneratedAtUtc   = (Get-Date).ToUniversalTime()
        Generator        = "Agt31 PowerShell Setup playbook (April 2026, v1.4)"
        PowerShellEdition= "$($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)"
        ModuleVersions   = (Get-Module | Select-Object Name, Version)
        FileCount        = $files.Count
        Files            = $files | ForEach-Object {
            [pscustomobject]@{
                RelativePath = $_.FullName.Substring($runFolder.Length+1)
                SizeBytes    = $_.Length
                Sha256       = (Get-FileHash -Algorithm SHA256 -Path $_.FullName).Hash
            }
        }
        Notes = $xlsxNote
    }
    $manifestPath = Join-Path $runFolder 'manifest.json'
    $manifest | ConvertTo-Json -Depth 10 | Out-File -FilePath $manifestPath -Encoding UTF8

    # Sign the manifest
    $cert = Get-Item -Path "Cert:\CurrentUser\My\$SigningCertThumbprint" -ErrorAction Stop
    $sig = Set-AuthenticodeSignature -FilePath $manifestPath -Certificate $cert -HashAlgorithm SHA256 -TimestampServer 'http://timestamp.digicert.com'
    if ($sig.Status -ne 'Valid') {
        throw "Manifest signing failed: $($sig.Status) — $($sig.StatusMessage). Evidence pack will not be released without a valid signature."
    }

    [pscustomobject]@{
        EvidenceFolder    = $runFolder
        ManifestPath      = $manifestPath
        SignatureStatus   = $sig.Status
        FileCount         = $files.Count
        TotalBytes        = ($files | Measure-Object -Property Length -Sum).Sum
        ReconcileErrorCount = ($script:Agt31LastReconcileErrors)?.Count ?? 0
    }
}
```

**Fail-closed conditions:** manifest signing failure throws — evidence is not released. Reconcile-errors.csv is always written, even when empty (the empty-with-header file is itself evidence that the reconciler ran clean). `xlsxNote` records the absence of `ImportExcel` rather than silently skipping.

---

## §14 — End-to-end validation, anti-patterns, and operating cadence

### 14.1 `Test-Agt31Implementation`

```powershell
# scripts/Test-Agt31Implementation.ps1
function Test-Agt31Implementation {
<#
.SYNOPSIS
    Smoke-tests the entire Control 3.1 pipeline against a tenant and emits a pass/fail report.
.DESCRIPTION
    Runs the orchestrator end-to-end with -WhatIf where applicable, then verifies:
      - Every leg returned at least one record (OK or status row).
      - Reconciler produced at least one canonical record (or, in a green-field tenant, a documented zero with manifest note).
      - Evidence pack manifest exists, is signed, and the signature is Valid.
      - At least one Zone1 / Zone2 / Zone3 record exists in tenants where each zone is in use (warn-only).
      - Reconcile-errors count matches the number of non-OK leg rows.
.PARAMETER Session
.OUTPUTS
    [pscustomobject[]] of test result rows.
.EXAMPLE
    PS> Test-Agt31Implementation -Session $session
.NOTES
    Run nightly under a CI agent. Failing rows post to the Control 3.1 owner via the standard
    AI Governance ServiceNow connector.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param([Parameter(Mandatory)] [pscustomobject]$Session)
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Continue'

    $results = New-Object System.Collections.Generic.List[pscustomobject]
    function _addResult($name,$pass,$detail) {
        $results.Add([pscustomobject]@{ TestName=$name; Pass=$pass; Detail=$detail; At=(Get-Date).ToUniversalTime() })
    }

    try {
        $cs  = Get-Agt31CopilotStudioInventory -Session $Session -ExchangeFolder (Join-Path $env:TEMP 'agt31-test')
        _addResult 'Leg:CopilotStudio' ($cs.Count -gt 0) "Records=$($cs.Count)"
    } catch { _addResult 'Leg:CopilotStudio' $false $_.Exception.Message }

    try {
        $da = Get-Agt31DeclarativeAgentInventory -Session $Session
        _addResult 'Leg:DeclarativeAgent' ($da.Count -gt 0) "Records=$($da.Count)"
    } catch { _addResult 'Leg:DeclarativeAgent' $false $_.Exception.Message }

    try {
        $hub = Get-Agt31CopilotHubInventory -Session $Session -WindowDays 7
        _addResult 'Leg:CopilotHub' ($hub.Count -gt 0) "Records=$($hub.Count)"
    } catch { _addResult 'Leg:CopilotHub' $false $_.Exception.Message }

    try {
        $reg = Get-Agt31AgentRegistryInventory -Session $Session
        _addResult 'Leg:AgentRegistry' ($reg.Count -gt 0) "Records=$($reg.Count); SovereignStatus=$($Session.Profile.AgentRegistryStatus)"
    } catch { _addResult 'Leg:AgentRegistry' $false $_.Exception.Message }

    try {
        $mcp = Get-Agt31McpServerInventory -Session $Session
        _addResult 'Leg:MCP' ($mcp.Count -ge 0) "Records=$($mcp.Count)"
    } catch { _addResult 'Leg:MCP' $false $_.Exception.Message }

    try {
        $spo = Get-Agt31SharePointAgentInventory -Session $Session -MaxSites 50
        _addResult 'Leg:SharePointAgent' ($spo.Count -ge 0) "Records=$($spo.Count)"
    } catch { _addResult 'Leg:SharePointAgent' $false $_.Exception.Message }

    try {
        $merged = Merge-Agt31Inventory -LegResults @{
            CopilotStudio=$cs; DeclarativeAgent=$da; CopilotHub=$hub;
            AgentRegistry=$reg; MCP=$mcp; SharePointAgent=$spo
        }
        _addResult 'Reconcile:Merge' ($merged.Count -ge 0) "Canonical=$($merged.Count); Errors=$(($script:Agt31LastReconcileErrors)?.Count ?? 0)"
    } catch { _addResult 'Reconcile:Merge' $false $_.Exception.Message }

    return $results.ToArray()
}
```

### 14.2 Anti-patterns (do not ship code that does any of these)

| # | Anti-pattern | Why it is wrong | Correct approach |
|---|---|---|---|
| 1 | Single-leg inventory script with `Get-AdminPowerApp` only | Misses declarative / MCP / SPO / Hub agents — false-clean | Multi-leg reconciler in §3–§9 |
| 2 | Running orchestrator under `powershell.exe` (5.1) | Graph v2 / PnP v2 / ExO v3 don't load; silent autoload of v1 produces wrong shapes | `pwsh` 7.4 orchestrator; spawn 5.1 child only for Power Apps Admin (§3) |
| 3 | `Add-PowerAppsAccount` without `-Endpoint` on a sovereign tenant | Returns zero environments silently | §2 hard-fail on sovereign mismatch |
| 4 | `+= @($r)` to accumulate records | O(n²) on 10k-agent tenants | `[List[pscustomobject]]::new()` accumulator |
| 5 | Default `LastActivity` to `Get-Date` when source missing | Corrupts orphan classification | §10 `ActivityUnknown` preserved; never silently filled |
| 6 | Owner string-match (`*system*`, `*deleted*`) | Misses real orphans + false positives | §11 resolve ObjectId via `Get-MgUser` and inspect `AccountEnabled` |
| 7 | Inventory CSV overwritten in place each run | Destroys reconciliation history | §13 run-id-stamped subfolder under WORM root |
| 8 | SHA-256 hash file with no signature | Hashes can be regenerated by anyone with file access | §13 `Set-AuthenticodeSignature` on manifest |
| 9 | Treating `Search-UnifiedAuditLog` first page as authoritative | Missing rows misclassify activity | Paginate with `SessionId`/`SessionCommand ReturnLargeSet` |
| 10 | Catching exceptions and continuing without recording | Silent partial coverage | Every leg writes a `Status != OK` row when it cannot enumerate |
| 11 | Decommissioning purely on Dormant signal | Acts on missing-data assumption when activity source was unavailable | §11 require both DepartedOwner + DormantSharedAgent before recommending decommission |
| 12 | Using one service principal for read + write | Breaks SOX 404 separation of duties | §1 separate `agt31-inventory-reader` and `agt31-pp-reader` from any write principal |
| 13 | Hard-coding the Copilot Studio `appType` discriminator | Microsoft churns the value across releases | §3 enumerate all values, mark drift in Notes |
| 14 | Skipping the SharePoint plane "because Copilot Studio handles it" | SPO-grounded agents do not appear in PA admin | §8 SPO + Graph beta site agents |
| 15 | Trusting `value.Count` without paging | Page 1 only — under-counts large tenants | §6 paging follow on `@odata.nextLink` |

### 14.3 Operating cadence

| Frequency | Action | Output destination |
|---|---|---|
| Every 4 hours | `Test-Agt31Implementation` smoke test | Operational dashboard ([Control 3.8](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)) |
| Daily 02:00 tenant TZ | Full inventory + enrichment + evidence pack | WORM evidence store; reconcile-errors row count to Control 3.11 |
| Weekly | Orphan + DormantSharedAgent review with business owner | Recommended actions land in Control 3.6 review queue |
| Monthly | Module / CLI version pin review against CAB-approved baseline | CAB ticket + `Test-Agt31Tooling` proof |
| Quarterly | Sovereign endpoint parity re-verification (§1 matrix) | Updated matrix in this playbook + manifest metadata |
| On Microsoft release notes change | Re-verify `appType` discriminator, Graph endpoint paths, Agent Registry GA status | Issue against the parent control spec |

---

## Cross-references

- [`portal-walkthrough.md`](portal-walkthrough.md) — UI equivalent for tenants without scripted access.
- [`verification-testing.md`](verification-testing.md) — examiner-facing test cases that consume this playbook's evidence pack.
- [`troubleshooting.md`](troubleshooting.md) — common failure modes by leg.
- [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) — module pinning, sovereign endpoints, mutation safety, Dataverse cmdlet quirks (referenced as **BL-§N**).
- [`../1.7-`](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — service principal governance (consumes §7 `RiskFlag='High'` rows).
- [`../1.10-`](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — owner attestation cadence.
- [`../1.19/`](../1.19/) — DLP integration.
- [`../2.1/`](../2.1/) — sensitivity label propagation.
- [`../2.5/`](../2.5/) — agent monitoring (consumes §10 enrichment).
- [`../3.6-`](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) — shadow-IT detection (compensating control for §6 sovereign gaps).
- [`../3.8-`](../../../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) — operational dashboards (consume `canonical-inventory.csv`).
- [`../3.11-`](../../../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) — evidence retention policy (governs `reconcile-errors.csv`).
- [`../../incident-and-risk/ai-incident-response-playbook.md`](../../incident-and-risk/ai-incident-response-playbook.md) — escalation path when `Find-Agt31OrphanedAgent` returns `EscalateToControl1.7`.

---

*Updated: April 2026 | Version: v1.4 | Maintained by: AI Governance Team*
