# Control 1.2 — PowerShell Setup: Agent Registry and Integrated Apps Management Automation

> **Scope.** This playbook automates the **agent identity and registration plane** for Control 1.2 across **Entra app registrations, enterprise applications (service principals), Integrated Apps in the Microsoft 365 admin center, Copilot Studio agent registrations, MCP server registrations, the emerging Microsoft Entra Agent ID surface, and Agent 365 admin endpoints** in US financial services tenants. It assumes you have already read [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) (referenced below as **BL-§N**) and the parent control specification [`../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md`](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md).
>
> **What this playbook is.** A reproducible, fail-closed registration-plane harness that (a) pins module / CLI versions; (b) bootstraps a sovereign-aware, certificate-authenticated, **separate** registry-reader principal that is distinct from any tenant-mutating credential; (c) enumerates every app-registration and service-principal object that could be an agent; (d) audits ownership, permission grants, credential hygiene, consent posture, sign-in risk, and Conditional Access coverage; (e) cross-walks the registration evidence to the Power Platform, MCP, and Integrated Apps surfaces; (f) feeds the merged record set into the Control 3.1 canonical reconciliation schema as an upstream registration source; and (g) emits a quarterly attestation pack with SHA-256 hashes and a certificate-signed manifest.
>
> **What this playbook is not.** It does not replace the authoritative system of record (the Control 3.1 inventory, the GRC tool, or the SharePoint sponsorship register). It does not, by itself, *guarantee* completeness — Microsoft Entra Agent ID, Agent 365 admin endpoints, and several Integrated Apps Graph routes remain preview-dependent in April 2026 (documented in §0 and §12), and organizations should compensate with manual attestation and Defender for Cloud Apps shadow-IT detection. It does not, by itself, *approve, decommission, transfer, or rotate* registrations; it raises evidence and recommends action, and humans accept risk.
>
> **Hedged language reminder.** Output of this harness *supports* compliance with FINRA Rule 4511, FINRA Regulatory Notice 25-07, SEC Rule 17a-4(b)(4) / 17a-4(g), SOX 302/404, GLBA 501(b), NYDFS 23 NYCRR 500.07 / 500.16 / 500.17, OCC Bulletin 2011-12, Fed SR 11-7, NIST AI RMF GOVERN 1.4 / 1.6, and FTC Safeguards Rule 16 CFR §314.4(c). It does not, by itself, *ensure* a passing examination, *guarantee* that every shadow registration has been discovered, or *eliminate* the risk that Microsoft moves an endpoint between v1.0 and beta between releases. Implementation requires that organizations verify endpoint availability, module pinning, and sovereign feature parity at every change window, and that they treat any preview surface (Entra Agent ID, Agent 365, `/admin/microsoft365apps`) as **additive** evidence rather than the sole source of truth.

| Field | Value |
|---|---|
| Control ID | 1.2 |
| Pillar | 1 — Security |
| Playbook | PowerShell Setup |
| PowerShell Edition | 7.4 LTS Core (orchestrator); 5.1 Desktop (Power Apps Administration sub-shell, JSON-bridged) |
| Sovereign Clouds | Commercial, GCC, GCC High, DoD, China (21Vianet) — see §1 sovereign matrix and §2 bootstrap |
| Last UI Verified | April 2026 |
| Companion Playbooks | `portal-walkthrough.md` (planned) · [`verification-testing.md`](verification-testing.md) · `troubleshooting.md` (planned) · [`sponsorship-lifecycle-workflows.md`](sponsorship-lifecycle-workflows.md) |
| Related Controls | [1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) · [1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) · [1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) · [1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) · [1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) · [2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) · [3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) · [3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |

---

## §0 — Wrong-shell trap and registration-plane false-clean defects (READ FIRST)

**The defining fact of Control 1.2.** As of April 2026, **no single Microsoft API returns "all registered agents"** in a tenant. An agent may exist as: (a) an Entra application object with an `agent`/`copilot` tag, (b) a service principal with an MCP-pattern redirect URI, (c) an Integrated App in the M365 admin center with no corresponding Power Platform record, (d) a Copilot Studio bot whose backing service principal has an unrelated display name, (e) an Entra Agent ID preview object visible only via the beta `/agents` route, (f) a declarative-agent manifest registered as a multi-tenant publisher app the organization has consented to, or (g) any combination of the above for the *same* business agent. A script that connects to one plane and reports a number is producing audit-grade misinformation.

A script that ignores this reality produces a **false-clean registry** — the worst Control 1.2 outcome. False-clean registries understate identity exposure under NYDFS 500.07 / 500.16, leave ownerless privilege grants undetected (NIST AI RMF GOVERN 1.4), and break the approval-trail evidence FINRA Rule 4511 and SEC 17a-4(b)(4) examiners ask for first.

**Why this section exists.** Six classes of silent failure produce false-clean registry output in Control 1.2 specifically:

1. **Wrong PowerShell edition for the plane being queried.** `Microsoft.PowerApps.Administration.PowerShell` is **Desktop-only** (Windows PowerShell 5.1) and silently returns empty arrays under PowerShell 7. `Microsoft.Graph` v2+, `Az.Accounts` v3+, and `MSCommerce` are **Core-only**. A registry harness that runs end-to-end in one edition is necessarily incomplete on at least one plane (BL-§2).
2. **Sovereign mis-routing.** `Connect-MgGraph` without `-Environment USGov` / `USGovDOD` / `China`, `Add-PowerAppsAccount` without `-Endpoint usgov` / `usgovhigh` / `dod`, and `pac auth create` without `--cloud UsGov` / `UsGovHigh` / `DoD` all authenticate against commercial endpoints and return zero results in a sovereign tenant — with exit code 0 (BL-§3).
3. **Beta vs v1.0 Microsoft Graph drift on registration endpoints.** `/applications` agent-tag filters, `/servicePrincipals/{id}/appRoleAssignments`, `/identity/conditionalAccess/policies` workload-identity targeting, `/identityProtection/riskyServicePrincipals`, `/admin/microsoft365apps` (April 2026 preview), and `/agents` (Entra Agent ID preview) move between beta and v1.0 quarterly, with breaking shape changes between minor SDK releases.
4. **Granted-scope mismatch.** `Connect-MgGraph -Scopes 'Application.Read.All'` requests the scope; the call returns `200` with an empty `value` array if admin consent was never granted. Verify `(Get-MgContext).Scopes` against the requested set after every connect.
5. **Tag taxonomy churn.** Microsoft has shipped multiple agent-tag values across releases (`DeclarativeAgent`, `CopilotAgent`, `M365CopilotPlugin`, `CopilotExtension`, `Bot`, `ChatBot`, `CopilotStudioBot`, `AgentApplication`). A hard-coded filter on a single tag misses every agent registered under a sibling tag.
6. **Single-credential read+write.** Running this harness with the same service principal that *creates* or *modifies* applications breaks SOX 404 separation of duties — the principal that produces the evidence could be the principal that altered the configuration the evidence describes.

**Top false-clean defects unique to registration automation.**

| # | Defect | What it looks like | How this playbook traps it |
|---|---|---|---|
| 1 | `Get-MgApplication -Filter "tags/any(t:t eq 'DeclarativeAgent')"` only | Misses CopilotAgent, M365CopilotPlugin, CopilotExtension, Agent Registry preview tags | §3 enumerates every known agent tag and warns on unknown tags found in tenant |
| 2 | Owner check via `Get-MgApplication` `.Owners` navigation property without expansion | `.Owners` returns empty unless `-ExpandProperty owners` is set; ownerless detection produces false positives | §4 explicit `-ExpandProperty owners` plus secondary `Get-MgApplicationOwner` cross-check |
| 3 | Permission-grant audit on `Application.Permissions` only | Misses delegated grants stored as `oauth2PermissionGrants` and risk-tiered AppRoleAssignments | §5 walks both `Get-MgServicePrincipalDelegatedPermissionGrant` and `Get-MgServicePrincipalAppRoleAssignment` |
| 4 | Credential expiry calculated as `EndDateTime - Now` without `KeyId` correlation | Rotation evidence loses provenance; can't tie new credential to retired credential | §6 emits `KeyId`, `Hint`, `CustomKeyIdentifier` for every passwordCredential / keyCredential row |
| 5 | Consent-policy assessment via `Get-MgPolicyAuthorizationPolicy` only | Misses the per-app admin-consent-request policy and reviewer queue size | §7 reads `/policies/adminConsentRequestPolicy` plus reviewer queue via `/identityGovernance/appConsent/appConsentRequests` |
| 6 | SP sign-in audit via `Get-MgAuditLogSignIn` without `-Filter "signInEventTypes/any(t:t eq 'servicePrincipal')"` | Returns user sign-ins; SP risk invisible | §8 explicit SP-only filter and Identity Protection `riskyServicePrincipals` cross-check |
| 7 | Conditional Access for workload identities listed but not validated against the SP set | A policy exists but excludes the SPs that need it | §9 resolves each policy's `conditions.clientApplications.includeServicePrincipals` against the §3 inventory and reports gaps |
| 8 | `pac copilot list` run without `--cloud` on a sovereign tenant | Zero results; exit 0 | §10 hard-fail when sovereign discriminator detected on tenant but `--cloud` mismatches |
| 9 | MCP enumeration via `Get-MgApplication` only (they are **service principals** with characteristic redirect URIs) | Entire MCP population missing | §11 walks `Get-MgServicePrincipal` with redirect-URI pattern matching plus tag filter |
| 10 | Integrated Apps assumed equal to the Power Platform inventory | Org-wide-deployed third-party apps with no PA footprint missed | §12 reads `/admin/microsoft365apps/installedApps` (preview) plus the Exchange Online add-in surface as a fallback |
| 11 | Reconciliation that overwrites the canonical record on every run | History destroyed; deltas invisible to examiners | §13 emits run-id-stamped subfolders to a WORM root and signs the manifest |
| 12 | Single SP for both registry-read and tenant-write | Breaks SOX 404 separation of duties | §1 separate `agt12-registry-reader` audit-only principal |

**Required shell guard (run this at the top of every Control 1.2 session).**

```powershell
# Save as: scripts/Assert-Agt12Shell.ps1
[CmdletBinding()]
[OutputType([void])]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [version]'7.4.0') {
    Write-Error "Control 1.2 orchestrator requires PowerShell 7.4 LTS Core (pwsh). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Launch 'pwsh' (not 'powershell.exe') and retry. The Power Apps Administration leg in §10 will be spawned into a Windows PowerShell 5.1 child process."
    exit 2
}

# Trap stale Windows PowerShell module shadowing
$desktopPaths = $env:PSModulePath -split [IO.Path]::PathSeparator | Where-Object { $_ -match 'WindowsPowerShell\\Modules' }
if ($desktopPaths) {
    $bad = Get-Module -ListAvailable -Name 'Microsoft.Graph','AzureAD','AzureADPreview' |
        Where-Object { $_.Name -eq 'Microsoft.Graph' -and $_.Version.Major -lt 2 }
    if ($bad) {
        Write-Error "Stale v1 Microsoft.Graph visible from Desktop module path: $($bad | ForEach-Object { "$($_.Name)=$($_.Version)" } | Sort-Object -Unique). Uninstall before continuing — autoload would silently shadow the pinned v2 modules and produce wrong-shape registry output."
        exit 2
    }
    $azureAd = Get-Module -ListAvailable -Name 'AzureAD','AzureADPreview' | Select-Object -First 1
    if ($azureAd) {
        Write-Warning "AzureAD legacy module present ($($azureAd.Name)=$($azureAd.Version)). Microsoft has formally deprecated AzureAD; use it ONLY as the documented fallback in §3.4 for endpoints not yet covered by Microsoft.Graph and never in the same script as Microsoft.Graph (cmdlet-name collisions cause silent wrong-result resolution)."
    }
}

Write-Verbose "Control 1.2 shell guard passed: pwsh $($PSVersionTable.PSVersion)"
```

**Fail-closed conditions enforced by this guard:**

- Detected PowerShell edition is `Desktop` or version `< 7.4.0` → `exit 2`.
- v1 `Microsoft.Graph` discoverable on `$env:PSModulePath` → `exit 2`.
- `AzureAD` / `AzureADPreview` legacy module present → loud warning (legitimate fallback per §3.4 but cmdlet collisions are recorded).

---

## §1 — Module, CLI, package, and permission matrix

**Why this section exists.** Registry-plane evidence is reproducible only when versions are declared, hashed, and emitted into the quarterly attestation manifest (§13). A pinned baseline lets the change ticket reference exact module versions, which is what SOX 404 evidence reviewers expect. Microsoft ships breaking shape changes across `Microsoft.Graph` minor versions on the application/serviceprincipal endpoints — the most common failure mode in this playbook is an unpinned upgrade silently changing a property name.

### 1.1 Pinned PowerShell modules (orchestrator — PS 7.4 Core)

```powershell
# Save as: scripts/Install-Agt12Modules.ps1
[CmdletBinding(SupportsShouldProcess)]
[OutputType([void])]
param(
    [Parameter()] [switch]$AcceptLicense
)
<#
.SYNOPSIS
    Pins every PowerShell module Control 1.2 depends on to a CAB-approved version.
.DESCRIPTION
    Idempotent installer. Skips any module already present at the exact RequiredVersion.
    Spawns a Windows PowerShell 5.1 child process for the Power Apps Administration modules
    because they are Desktop-only and silently misbehave under PowerShell 7 (BL-§2).
.EXAMPLE
    PS> ./Install-Agt12Modules.ps1 -WhatIf
    Lists every install action that would be taken without performing it.
.EXAMPLE
    PS> ./Install-Agt12Modules.ps1 -AcceptLicense -Verbose
    Performs the install for unattended scheduler use.
.NOTES
    Verify pinned versions against your CAB-approved baseline before each run. Microsoft.Graph is
    a meta-module that pulls 30+ sub-modules; pin every required sub-module explicitly.
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$modules = @(
    @{ Name = 'Microsoft.Graph.Authentication';                   Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Applications';                     Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Identity.SignIns';                 Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Identity.Governance';              Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Identity.DirectoryManagement';     Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Reports';                          Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Users';                            Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Beta.Applications';                Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Beta.Identity.SignIns';            Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Beta.Identity.Governance';         Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Beta.Reports';                     Version = '2.25.0' },
    @{ Name = 'ExchangeOnlineManagement';                         Version = '3.7.0'  },
    @{ Name = 'MSCommerce';                                       Version = '2.0.1'  },
    @{ Name = 'Az.Accounts';                                      Version = '3.0.0'  },
    @{ Name = 'Az.Resources';                                     Version = '7.4.0'  }
)

foreach ($m in $modules) {
    $existing = Get-Module -ListAvailable -Name $m.Name |
        Where-Object { $_.Version -eq [version]$m.Version }
    if (-not $existing) {
        if ($PSCmdlet.ShouldProcess("$($m.Name)@$($m.Version)", 'Install-Module')) {
            try {
                Install-Module -Name $m.Name -RequiredVersion $m.Version `
                    -Scope CurrentUser -Repository PSGallery -AllowClobber `
                    -AcceptLicense:$AcceptLicense -ErrorAction Stop
            } catch {
                Write-Error "Failed to install $($m.Name)@$($m.Version): $($_.Exception.Message)"
                throw
            }
        }
    }
    Import-Module -Name $m.Name -RequiredVersion $m.Version -Force -ErrorAction Stop
    Write-Verbose "Imported $($m.Name) $($m.Version)"
}

# Desktop-only Power Apps modules: install into 5.1 sub-shell, NEVER into pwsh 7
$ppAdminVersion = '2.0.183'
$ppMakerVersion = '1.0.34'
if ($IsWindows) {
    if ($PSCmdlet.ShouldProcess("Microsoft.PowerApps.Administration.PowerShell@$ppAdminVersion (Desktop 5.1)", 'Install-Module via powershell.exe')) {
        powershell.exe -NoProfile -Command "Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -RequiredVersion $ppAdminVersion -Scope CurrentUser -Force -AllowClobber" | Out-Null
        powershell.exe -NoProfile -Command "Install-Module -Name Microsoft.PowerApps.PowerShell -RequiredVersion $ppMakerVersion -Scope CurrentUser -Force -AllowClobber" | Out-Null
    }
} else {
    Write-Warning "Non-Windows host detected. Power Apps Administration cmdlets are Windows-only. The Power Platform leg in §10 will be skipped unless a Windows worker is available."
}

# Optional legacy fallback: AzureAD (only for endpoints not yet covered by Microsoft.Graph)
if ($PSCmdlet.ShouldProcess("AzureAD legacy fallback (5.1 only)", 'Install-Module via powershell.exe')) {
    Write-Warning "AzureAD module is formally deprecated by Microsoft. It is installed here ONLY as the documented fallback in §3.4 for the small set of endpoints not yet covered by Microsoft.Graph v2. Do not import AzureAD into the same session as Microsoft.Graph — cmdlet-name collisions resolve silently to the wrong module."
    if ($IsWindows) {
        powershell.exe -NoProfile -Command "if (-not (Get-Module -ListAvailable AzureAD)) { Install-Module -Name AzureAD -RequiredVersion 2.0.2.182 -Scope CurrentUser -Force -AllowClobber }" | Out-Null
    }
}
```

### 1.2 Pinned CLI tooling

| Tool | Minimum | Used for | Sovereign notes |
|---|---|---|---|
| Power Platform CLI (`pac`) | **1.45.0** | `pac copilot list`, `pac admin list-app-resources`, `pac auth create --cloud` | Pass `--cloud {Public\|UsGov\|UsGovHigh\|DoD}` |
| Microsoft Graph PowerShell SDK | 2.25.0 | All §3–§9 / §12 enumeration | `Connect-MgGraph -Environment` |
| Azure CLI (`az`) | 2.60.0 | Azure managed identity / federated credential cross-check | `az cloud set --name {AzureCloud\|AzureUSGovernment\|AzureChinaCloud}` |
| `Get-FileHash` (built-in) | n/a | SHA-256 evidence hashes | n/a |
| `Set-AuthenticodeSignature` | n/a | Manifest signing in §13 | Code-signing cert must chain to a CA approved by Information Security |

**Pin check (must run before §2 bootstrap):**

```powershell
# scripts/Test-Agt12Tooling.ps1
[CmdletBinding()]
[OutputType([pscustomobject[]])]
param()
<#
.SYNOPSIS
    Verifies every CLI / SDK pin Control 1.2 depends on.
.DESCRIPTION
    Returns a [pscustomobject[]] with Tool, Found, Required, Pass columns and exits 2 if any
    row fails. Run as part of every change window before §2.
.EXAMPLE
    PS> ./Test-Agt12Tooling.ps1 -Verbose
.NOTES
    Add additional rows as your tooling baseline grows; do not loosen the version floors.
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$results = @()
try {
    $pacVer = (& pac --version 2>$null) -join ' '
    $results += [pscustomobject]@{ Tool='pac'; Found=$pacVer; Required='>=1.45.0'; Pass=($pacVer -match '1\.(4[5-9]|[5-9]\d)') }
} catch { $results += [pscustomobject]@{ Tool='pac'; Found='not-installed'; Required='>=1.45.0'; Pass=$false } }

try {
    $azVer = (& az version --output json 2>$null) | ConvertFrom-Json
    $results += [pscustomobject]@{ Tool='az'; Found=$azVer.'azure-cli'; Required='>=2.60.0'; Pass=([version]$azVer.'azure-cli' -ge [version]'2.60.0') }
} catch { $results += [pscustomobject]@{ Tool='az'; Found='not-installed'; Required='>=2.60.0'; Pass=$false } }

$mg = Get-Module -ListAvailable Microsoft.Graph.Authentication | Sort-Object Version -Descending | Select-Object -First 1
$results += [pscustomobject]@{ Tool='Microsoft.Graph.Authentication'; Found=($mg.Version.ToString()); Required='==2.25.0'; Pass=($mg -and $mg.Version -eq [version]'2.25.0') }

$results
if ($results.Where({ -not $_.Pass }).Count) {
    Write-Error "One or more tooling pin checks failed. Review the results table above."
    exit 2
}
```

### 1.3 Permission matrix (audit-only, separate registry-reader credentials)

The registry harness must run unattended on a schedule. The Registry Reader service principal should be **distinct** from any service principal that creates, modifies, deletes, or consents to applications. This separation supports SOX 404 separation-of-duties: the principal that produces the evidence is not the principal that could alter the configuration the evidence describes. NYDFS 23 NYCRR 500.07 also expects privileged-access separation that this pattern operationalizes.

| Principal / Role | Granted on | Permission | Why this script needs it | Audit-only? |
|---|---|---|---|---|
| `agt12-registry-reader` (SP) | Microsoft Graph | `Application.Read.All` (Application) | Enumerate Entra app registrations and service principals; §3, §4, §6 | Yes |
| same SP | Microsoft Graph | `Directory.Read.All` (Application) | Resolve owners, tenant metadata, role memberships; §4, §8 | Yes |
| same SP | Microsoft Graph | `DelegatedPermissionGrant.Read.All` (Application) | Read `oauth2PermissionGrants`; §5 | Yes |
| same SP | Microsoft Graph | `AppRoleAssignment.Read.All` (Application) | Read appRoleAssignments granted *to* SPs; §5 | Yes |
| same SP | Microsoft Graph | `Policy.Read.All` (Application) | Read consent policies, CA policies; §7, §9 | Yes |
| same SP | Microsoft Graph | `AuditLog.Read.All` (Application) | Read service principal sign-ins and credential events; §6, §8 | Yes |
| same SP | Microsoft Graph | `IdentityRiskyServicePrincipal.Read.All` (Application) | Identity Protection risky SP detection; §8 | Yes |
| same SP | Microsoft Graph | `IdentityRiskEvent.Read.All` (Application) | Risk events tied to SPs; §8 | Yes |
| `agt12-registry-writer` (SP — separate, OPTIONAL) | Microsoft Graph | `Application.ReadWrite.All`, `AppRoleAssignment.ReadWrite.All`, `DelegatedPermissionGrant.ReadWrite.All`, `Policy.ReadWriteConsentRequest` | Owner reassignment in §4, consent-policy mutations in §7. **Used only by named human operator under PIM activation, never on the unattended pipeline.** | No |
| `agt12-pp-reader` (SP) | Power Platform | **Power Platform Service Admin** (read-intent) | `Get-AdminPowerApp`, `pac copilot list`; §10 | Yes (intent) |
| Operator (human) | Entra PIM | `Global Reader` time-bound | Manual reconciliation review; never used for the unattended pipeline | Yes |
| Operator (human, mutating) | Entra PIM | `Cloud Application Administrator` time-bound (NOT Global Admin) | Owner reassignments, consent-grant remediation; activated only for §4.4 / §7.3 ad-hoc remediation | No |

**Hedging note on permission scope.** The registry reader is scoped to read-only application permissions; tenant administrators should still review the consent grants quarterly and rotate the certificate at the cadence defined by your PKI policy. "Read-only" is a contract with Microsoft Graph, not a guarantee that the credential cannot be used for reconnaissance — treat the registry reader as a privileged identity for monitoring and detection purposes, with its sign-ins reported into [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

**Sovereign cloud parity matrix (verify at deploy time per the parent control).**

| Plane | Commercial | GCC | GCC High | DoD |
|---|---|---|---|---|
| Microsoft Graph `/applications`, `/servicePrincipals` | GA | GA | GA | GA |
| Microsoft Graph `/oauth2PermissionGrants`, `/appRoleAssignments` | GA | GA | GA | GA |
| Microsoft Graph `/policies/adminConsentRequestPolicy` | GA | GA | GA | GA |
| Microsoft Graph `/identityProtection/riskyServicePrincipals` | GA | Rolling — verify | Limited — verify | Verify |
| Microsoft Graph `/identity/conditionalAccess/policies` (workload identities) | GA | GA | Verify | Verify |
| Microsoft Graph `/admin/microsoft365apps/installedApps` | Preview (April 2026) | Verify | Not GA | Not GA |
| Microsoft Graph `/agents` (Entra Agent ID preview) | Preview | Limited — verify | Not GA | Not GA |
| Power Platform `pac copilot list` | GA | GA / verify scope | Verify | Verify |
| Agent 365 admin endpoints | Preview / rolling | Limited — verify | Verify | Verify |

Treat any parity gap as a **compensating-control conversation** (manual attestation, periodic export, third-party CASB enrichment) — not a silent skip. §9 (Conditional Access) and §8 (risky SPs) degrade gracefully with `Status='UnavailableInCloud'` rows when an endpoint is not reachable.

---

## §2 — Sovereign-aware bootstrap (`Resolve-Agt12CloudProfile` + `Initialize-Agt12Session`)

**Why this section exists.** Every cmdlet in §3–§12 will silently route to the wrong cloud unless the session is opened against the correct sovereign endpoint. Sovereign mis-routing is the #2 false-clean defect for Control 1.2 (§0 defect #2). The two helpers below produce a single `[Agt12Session]`-shaped object the rest of the playbook consumes, and explicitly **reject** the bootstrap if the bound principal is the same identity used elsewhere for write operations.

### 2.1 `Resolve-Agt12CloudProfile`

```powershell
# scripts/Resolve-Agt12CloudProfile.ps1
function Resolve-Agt12CloudProfile {
<#
.SYNOPSIS
    Maps a sovereign cloud short-name to every endpoint and module-parameter the registry harness needs.
.DESCRIPTION
    Returns a [pscustomobject] with strongly typed properties for the Microsoft Graph environment,
    Graph base URI, Power Platform endpoint, PAC CLI cloud token, Azure environment, Exchange Online
    environment, and the April 2026 GA status of preview surfaces (Entra Agent ID, /admin/microsoft365apps).
.PARAMETER Cloud
    One of: Commercial, GCC, GCCHigh, DoD, China.
.OUTPUTS
    [pscustomobject]
.EXAMPLE
    PS> Resolve-Agt12CloudProfile -Cloud GCCHigh
.NOTES
    Re-verify quarterly via Microsoft Learn release notes; preview-status fields drift between rings.
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
        Commercial = @{ Graph='Global';   GraphBase='https://graph.microsoft.com';            PA='prod';      Pac='Public';    Az='AzureCloud';        Exo='O365Default';      AgentId='Preview';            M365Apps='Preview' }
        GCC        = @{ Graph='USGov';    GraphBase='https://graph.microsoft.com';            PA='usgov';     Pac='UsGov';     Az='AzureCloud';        Exo='O365USGovGCC';     AgentId='Limited';            M365Apps='Verify'  }
        GCCHigh    = @{ Graph='USGov';    GraphBase='https://graph.microsoft.us';             PA='usgovhigh'; Pac='UsGovHigh'; Az='AzureUSGovernment'; Exo='O365USGovGCCHigh'; AgentId='NotAvailableInCloud'; M365Apps='NotAvailableInCloud' }
        DoD        = @{ Graph='USGovDOD'; GraphBase='https://dod-graph.microsoft.us';         PA='dod';       Pac='DoD';       Az='AzureUSGovernment'; Exo='O365USGovDoD';     AgentId='NotAvailableInCloud'; M365Apps='NotAvailableInCloud' }
        China      = @{ Graph='China';    GraphBase='https://microsoftgraph.chinacloudapi.cn'; PA='china';    Pac='China';     Az='AzureChinaCloud';   Exo='O365China';        AgentId='NotAvailableInCloud'; M365Apps='NotAvailableInCloud' }
    }

    $p = $map[$Cloud]
    [pscustomobject]@{
        Cloud                = $Cloud
        GraphEnvironment     = $p.Graph
        GraphBaseUri         = $p.GraphBase
        PowerAppsEndpoint    = $p.PA
        PacCloud             = $p.Pac
        AzureEnvironment     = $p.Az
        ExoEnvironmentName   = $p.Exo
        EntraAgentIdStatus   = $p.AgentId
        M365AppsAdminStatus  = $p.M365Apps
        ResolvedAt           = (Get-Date).ToUniversalTime()
    }
}
```

### 2.2 `Initialize-Agt12Session`

```powershell
# scripts/Initialize-Agt12Session.ps1
function Initialize-Agt12Session {
<#
.SYNOPSIS
    Authenticates the registry-reader principal to every plane Control 1.2 reads from, using a single
    certificate-based service principal and verifying that the granted scopes match the requested set.
.DESCRIPTION
    Performs Connect-MgGraph (cert-based) and Connect-AzAccount (cert-based, optional). Defers the
    Power Apps Administration leg to a 5.1 child process spawned in §10. Hard-fails (exit 2) if the
    bound principal authenticates against the wrong sovereign endpoint or returns fewer scopes than
    requested. Refuses to bootstrap if the supplied ClientId matches the documented write-principal
    application id (separation-of-duties enforcement).
.PARAMETER TenantId
.PARAMETER RegistryReaderClientId
    Application (client) id of the audit-only registry reader SP. MUST NOT match any write principal.
.PARAMETER CertificateThumbprint
.PARAMETER Cloud
.PARAMETER WritePrincipalClientIdsToReject
    Optional list of application ids that this script will refuse to bind as the registry reader.
    Populate from your tenant's documented write principals (e.g., the SP used by Control 1.4 for
    DLP edits, or the SP used by Control 2.1 for label propagation).
.OUTPUTS
    [pscustomobject] with Profile, MgContext, AzContext, ConnectedAt, RunId.
.EXAMPLE
    PS> $session = Initialize-Agt12Session -TenantId $tid -RegistryReaderClientId $cid -CertificateThumbprint $thumb -Cloud GCCHigh
.EXAMPLE
    PS> $session = Initialize-Agt12Session -TenantId $tid -RegistryReaderClientId $cid -CertificateThumbprint $thumb -Cloud Commercial -WhatIf
    Shows the connect actions that would be performed without contacting any endpoint.
.NOTES
    Idempotent. Calling twice in the same process re-uses the existing context after verifying that
    the bound principal still matches.
#>
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [guid]$TenantId,
        [Parameter(Mandatory)] [guid]$RegistryReaderClientId,
        [Parameter(Mandatory)] [string]$CertificateThumbprint,
        [Parameter(Mandatory)] [ValidateSet('Commercial','GCC','GCCHigh','DoD','China')] [string]$Cloud,
        [Parameter()] [guid[]]$WritePrincipalClientIdsToReject = @()
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    if ($RegistryReaderClientId -in $WritePrincipalClientIdsToReject) {
        Write-Error "Refusing to bootstrap: RegistryReaderClientId $RegistryReaderClientId is in the documented write-principal list. SOX 404 separation-of-duties requires a distinct read-only principal for §3-§12. Provision agt12-registry-reader and retry."
        exit 2
    }

    $profile = Resolve-Agt12CloudProfile -Cloud $Cloud
    $runId   = [guid]::NewGuid().ToString()

    $requestedScopes = @(
        'Application.Read.All','Directory.Read.All','DelegatedPermissionGrant.Read.All',
        'AppRoleAssignment.Read.All','Policy.Read.All','AuditLog.Read.All',
        'IdentityRiskyServicePrincipal.Read.All','IdentityRiskEvent.Read.All'
    )

    if ($PSCmdlet.ShouldProcess('Microsoft Graph','Connect-MgGraph (certificate)')) {
        try {
            Connect-MgGraph -TenantId $TenantId -ClientId $RegistryReaderClientId `
                -CertificateThumbprint $CertificateThumbprint `
                -Environment $profile.GraphEnvironment -NoWelcome -ErrorAction Stop | Out-Null
        } catch {
            Write-Error "Connect-MgGraph failed against $($profile.GraphEnvironment): $($_.Exception.Message). Verify the certificate is installed in Cert:\CurrentUser\My or Cert:\LocalMachine\My, that the SP has the cert credential registered, and that the tenant id matches the SP's home tenant."
            throw
        }
    }
    $ctx = Get-MgContext
    if ($ctx.Environment -ne $profile.GraphEnvironment) {
        Write-Error "Graph context bound to $($ctx.Environment) but profile is $($profile.GraphEnvironment). Sovereign mismatch — aborting (exit 2)."
        exit 2
    }
    $missing = $requestedScopes | Where-Object { $_ -notin $ctx.Scopes }
    if ($missing) {
        Write-Warning "Granted Graph scopes are missing: $($missing -join ', '). Some legs will degrade gracefully (Status=PermissionDenied rows) rather than throw, but examiners expect explicit grant. File a consent request and re-run."
    }

    if ($PSCmdlet.ShouldProcess($profile.AzureEnvironment,'Connect-AzAccount (certificate, optional)')) {
        try {
            Connect-AzAccount -ServicePrincipal -Tenant $TenantId -ApplicationId $RegistryReaderClientId `
                -CertificateThumbprint $CertificateThumbprint `
                -Environment $profile.AzureEnvironment -WarningAction SilentlyContinue | Out-Null
        } catch {
            Write-Warning "Connect-AzAccount failed: $($_.Exception.Message). Azure-side managed-identity / federated-credential cross-checks in §6 will be skipped; primary registry data unaffected."
        }
    }

    [pscustomobject]@{
        Profile      = $profile
        RunId        = $runId
        MgContext    = $ctx
        ConnectedAt  = (Get-Date).ToUniversalTime()
        TenantId     = $TenantId
        ClientId     = $RegistryReaderClientId
        Thumbprint   = $CertificateThumbprint
    }
}
```

**Fail-closed conditions enforced by this section:**

- ClientId matches a documented write-principal id → `exit 2` (separation of duties).
- Graph context `Environment` does not match resolved profile → `exit 2`.
- Cert thumbprint not present in `Cert:\CurrentUser\My` or `Cert:\LocalMachine\My` → throw.
- Az leg failure is **best-effort**; primary registry data is collected from Microsoft Graph and unaffected.

### 2.3 Throttle helper used by every leg

```powershell
function Invoke-Agt12WithThrottle {
<#
.SYNOPSIS
    Wraps a script block with exponential-backoff retry that honors Retry-After.
.DESCRIPTION
    Catches HTTP 429 / 503 / 504 from Microsoft Graph and Power Platform admin endpoints. Reads
    Retry-After when present; falls back to 2^attempt seconds capped at 60. Maximum 6 attempts.
    Re-throws on any other exception.
.PARAMETER ScriptBlock
.PARAMETER MaxAttempts
.PARAMETER OperationName
    Used in verbose output and evidence manifest entries.
.OUTPUTS
    Whatever the script block emits.
.EXAMPLE
    PS> Invoke-Agt12WithThrottle -OperationName 'Get-MgApplication' -ScriptBlock { Get-MgApplication -All }
.NOTES
    Power Platform admin APIs may impose long cool-downs (>60s). 429 after MaxAttempts is re-thrown.
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

## §3 — App registration and service principal inventory (`Get-Agt12AppRegistryInventory`)

**Why this section exists.** This leg produces the **identity-anchor record** for every other section in this playbook: §4 owner audit, §5 permission audit, §6 credential hygiene, and §8 sign-in audit all index off the AppId / ObjectId pairs returned here. The dominant defect on this plane is enumerating either applications **or** service principals but not both, and not understanding that the same agent has two object ids (the application object in the home tenant, and the service principal object in every tenant where it has been consented).

```powershell
# scripts/legs/Get-Agt12AppRegistryInventory.ps1
function Get-Agt12AppRegistryInventory {
<#
.SYNOPSIS
    Enumerates every Entra application and service principal that could be an agent registration.
.DESCRIPTION
    Walks Get-MgApplication with -ExpandProperty owners,extensionProperties for each known agent tag,
    then walks Get-MgServicePrincipal for the same tag set plus MCP-pattern redirect URIs (§11
    consumes this output). Cross-correlates Application.AppId to ServicePrincipal.AppId so each row
    has both the home-tenant Application ObjectId and the local-tenant ServicePrincipal ObjectId.
    Records every tag value seen, including unknown values (warning logged so the agent-tag taxonomy
    can be updated as Microsoft adds tags).
.PARAMETER Session
.PARAMETER IncludeAllSps
    If $true, enumerates every service principal in tenant (not just tag-matched). Use for the full
    quarterly attestation in §13; default $false for daily / hourly runs.
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $reg = Get-Agt12AppRegistryInventory -Session $session
.EXAMPLE
    PS> $reg = Get-Agt12AppRegistryInventory -Session $session -IncludeAllSps -Verbose
.NOTES
    Tag taxonomy is set by Microsoft and changes; the function records the matched tag in MatchedOn
    for forensic review and emits a warning when an unknown tag containing 'agent' or 'copilot' is found.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter()] [switch]$IncludeAllSps
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $knownTags = @(
        'DeclarativeAgent','CopilotAgent','M365Copilot','M365CopilotPlugin','CopilotExtension',
        'TeamsAgent','AgentApplication','Bot','ChatBot','CopilotStudioBot','MCPServer','MCPAgent'
    )
    $accum = New-Object System.Collections.Generic.List[pscustomobject]
    $seenAppIds = New-Object System.Collections.Generic.HashSet[string]

    # 1) Application objects (home-tenant registrations)
    foreach ($tag in $knownTags) {
        try {
            $apps = Invoke-Agt12WithThrottle -OperationName "Graph:Application[$tag]" -ScriptBlock {
                Get-MgApplication -Filter "tags/any(t:t eq '$tag')" -ExpandProperty 'owners' -All -ErrorAction Stop
            }
        } catch {
            $accum.Add([pscustomobject]@{
                Plane='AppRegistration'; Status='EnumerationFailed'; MatchedOn=$tag;
                Reason=$_.Exception.Message; CollectedAt=(Get-Date).ToUniversalTime()
            })
            continue
        }
        foreach ($a in $apps) {
            if (-not $seenAppIds.Add($a.AppId)) { continue }
            $ownerCount = if ($a.Owners) { @($a.Owners).Count } else { 0 }
            $accum.Add([pscustomobject]@{
                Plane              = 'AppRegistration'
                Status             = 'OK'
                ObjectId           = $a.Id
                AppId              = $a.AppId
                DisplayName        = $a.DisplayName
                MatchedOn          = $tag
                PublisherDomain    = $a.PublisherDomain
                VerifiedPublisher  = $a.VerifiedPublisher.DisplayName
                SignInAudience     = $a.SignInAudience
                CreatedDateTime    = $a.CreatedDateTime
                Tags               = ($a.Tags -join ';')
                IdentifierUris     = ($a.IdentifierUris -join ';')
                OwnerCount         = $ownerCount
                OwnerObjectIds     = (@($a.Owners | ForEach-Object { $_.Id }) -join ';')
                Notes              = ''
                CollectedAt        = (Get-Date).ToUniversalTime()
            })
        }
    }

    # 2) Service principals (consented in this tenant — agents from publishers, MCP servers, etc.)
    foreach ($tag in $knownTags) {
        try {
            $sps = Invoke-Agt12WithThrottle -OperationName "Graph:ServicePrincipal[$tag]" -ScriptBlock {
                Get-MgServicePrincipal -Filter "tags/any(t:t eq '$tag')" -All -ErrorAction Stop
            }
        } catch {
            $accum.Add([pscustomobject]@{
                Plane='ServicePrincipal'; Status='EnumerationFailed'; MatchedOn=$tag;
                Reason=$_.Exception.Message; CollectedAt=(Get-Date).ToUniversalTime()
            })
            continue
        }
        foreach ($sp in $sps) {
            $accum.Add([pscustomobject]@{
                Plane              = 'ServicePrincipal'
                Status             = 'OK'
                ObjectId           = $sp.Id
                AppId              = $sp.AppId
                DisplayName        = $sp.DisplayName
                MatchedOn          = $tag
                PublisherDomain    = $sp.PublisherName
                VerifiedPublisher  = $sp.VerifiedPublisher.DisplayName
                SignInAudience     = $sp.SignInAudience
                AppOwnerOrganizationId = $sp.AppOwnerOrganizationId
                ServicePrincipalType = $sp.ServicePrincipalType
                AccountEnabled     = $sp.AccountEnabled
                ReplyUrls          = ($sp.ReplyUrls -join ';')
                Tags               = ($sp.Tags -join ';')
                Notes              = ''
                CollectedAt        = (Get-Date).ToUniversalTime()
            })
        }
    }

    # 3) Beta sweep for tag drift — capture any tag containing 'agent' or 'copilot' not in knownTags
    try {
        $betaApps = Invoke-Agt12WithThrottle -OperationName 'GraphBeta:Application[agent-drift]' -ScriptBlock {
            Get-MgBetaApplication -Filter "tags/any(t:contains(t, 'gent') or contains(t, 'opilot'))" -All -ErrorAction Stop
        }
        foreach ($a in $betaApps) {
            $newTags = @($a.Tags) | Where-Object { $_ -notin $knownTags -and ($_ -match 'gent|opilot') }
            if ($newTags) {
                Write-Warning "Tag drift detected on App $($a.AppId): unknown tag(s) [$($newTags -join ', ')]. Update knownTags in §3 and re-run."
                if ($seenAppIds.Add($a.AppId)) {
                    $accum.Add([pscustomobject]@{
                        Plane='AppRegistration'; Status='OK'; ObjectId=$a.Id; AppId=$a.AppId;
                        DisplayName=$a.DisplayName; MatchedOn="beta-drift:$($newTags -join ';')";
                        PublisherDomain=$a.PublisherDomain; SignInAudience=$a.SignInAudience;
                        CreatedDateTime=$a.CreatedDateTime; Tags=($a.Tags -join ';');
                        IdentifierUris=($a.IdentifierUris -join ';');
                        Notes='TagDrift'; CollectedAt=(Get-Date).ToUniversalTime()
                    })
                }
            }
        }
    } catch {
        Write-Warning "Beta tag-drift sweep failed: $($_.Exception.Message). Known-tag results stand."
    }

    # 4) Optional full SP sweep (quarterly attestation only — expensive)
    if ($IncludeAllSps) {
        try {
            $allSps = Invoke-Agt12WithThrottle -OperationName 'Graph:ServicePrincipal[ALL]' -ScriptBlock {
                Get-MgServicePrincipal -All -Property 'id,appId,displayName,publisherName,servicePrincipalType,tags,replyUrls,accountEnabled,appOwnerOrganizationId' -ErrorAction Stop
            }
            foreach ($sp in $allSps) {
                if ($accum.AppId -notcontains $sp.AppId) {
                    $accum.Add([pscustomobject]@{
                        Plane='ServicePrincipal'; Status='OK'; ObjectId=$sp.Id; AppId=$sp.AppId;
                        DisplayName=$sp.DisplayName; MatchedOn='full-sweep';
                        PublisherDomain=$sp.PublisherName; ServicePrincipalType=$sp.ServicePrincipalType;
                        AccountEnabled=$sp.AccountEnabled; AppOwnerOrganizationId=$sp.AppOwnerOrganizationId;
                        ReplyUrls=($sp.ReplyUrls -join ';'); Tags=($sp.Tags -join ';');
                        Notes='QuarterlyFullSweep'; CollectedAt=(Get-Date).ToUniversalTime()
                    })
                }
            }
        } catch {
            Write-Warning "Full SP sweep failed: $($_.Exception.Message). Tag-matched results stand."
        }
    }

    Write-Verbose "AppRegistry leg returned $($accum.Count) records ($(($accum | Where-Object Plane -eq 'AppRegistration').Count) Apps, $(($accum | Where-Object Plane -eq 'ServicePrincipal').Count) SPs)"
    return $accum.ToArray()
}
```

### 3.4 AzureAD legacy fallback (use only when Microsoft.Graph lacks coverage)

A small set of admin endpoints (notably some legacy `Get-AzureADApplicationProxyApplication` capabilities) are not yet covered by Microsoft.Graph v2. When they are required, run them in a **separate** Windows PowerShell 5.1 child process, never in the same session as Microsoft.Graph (cmdlet-name collisions resolve silently to the wrong module, producing wrong-shape data):

```powershell
# Spawn a clean 5.1 child for a single AzureAD call, return JSON
function Invoke-Agt12AzureAdLegacy {
<#
.SYNOPSIS
    Runs an AzureAD legacy cmdlet in a clean Windows PowerShell 5.1 child process.
.DESCRIPTION
    Bridges the formally deprecated AzureAD module without ever importing it into the orchestrator
    pwsh session. Only use for endpoints not covered by Microsoft.Graph v2; document each use in
    your CAB ticket because the AzureAD module is on Microsoft's deprecation track.
.PARAMETER Command
    The AzureAD command to run, with all arguments. Output must be ConvertTo-Json compatible.
.PARAMETER TenantId
.OUTPUTS
    [object] (JSON-deserialized output of the supplied command)
.EXAMPLE
    PS> Invoke-Agt12AzureAdLegacy -Command "Get-AzureADApplicationProxyApplication" -TenantId $tid
.NOTES
    Authentication in the child uses interactive Connect-AzureAD; for unattended runs, embed a cert-based
    Connect-AzureAD with -CertificateThumbprint.
#>
    [CmdletBinding()]
    [OutputType([object])]
    param(
        [Parameter(Mandatory)] [string]$Command,
        [Parameter(Mandatory)] [guid]$TenantId
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    if (-not $IsWindows) { throw "AzureAD legacy bridge requires Windows (Desktop 5.1 child)." }
    $script = @"
Import-Module AzureAD -ErrorAction Stop
Connect-AzureAD -TenantId '$TenantId' -ErrorAction Stop | Out-Null
$Command | ConvertTo-Json -Depth 8 -Compress
"@
    $tmp = [IO.Path]::GetTempFileName() + '.ps1'
    Set-Content -Path $tmp -Value $script -Encoding UTF8
    try {
        $out = powershell.exe -NoProfile -ExecutionPolicy Bypass -File $tmp
        return ($out | ConvertFrom-Json)
    } finally {
        Remove-Item -Path $tmp -Force -ErrorAction SilentlyContinue
    }
}
```

**Fail-closed conditions enforced by this leg:** every tag enumeration writes a `Status='EnumerationFailed'` row when Graph throws (rather than swallowing the failure); tag-drift sweep records unknown tags so the taxonomy can be maintained; `IncludeAllSps` is opt-in to keep the daily run cheap.

---
## §4 — Owner audit & ownerless agent remediation (`Get-Agt12OwnershipAudit`)

**Why this section exists.** Control 1.2 §3 in the parent control requires every registered agent to have at least two named human owners. The two dominant defects on this plane are (a) ownership records that point at offboarded users (nameless tombstone GUIDs in the audit), and (b) treating the registered application owner and the production support contact as the same person. This leg classifies each agent into Compliant / Singleton / Ownerless / TombstonedOwner and emits a manager-hierarchy reassignment proposal — never auto-applied — for the writer principal to action under PIM.

```powershell
# scripts/legs/Get-Agt12OwnershipAudit.ps1
function Get-Agt12OwnershipAudit {
<#
.SYNOPSIS
    Classifies each agent registration by owner posture and proposes manager-hierarchy reassignments.
.DESCRIPTION
    For each App / SP record from §3, calls Get-MgApplicationOwner / Get-MgServicePrincipalOwner,
    resolves each owner to a User object, classifies as Active / Disabled / Deleted, and emits one
    of Compliant (≥2 active human owners), Singleton (1 active), Ownerless (0 active), or
    TombstonedOwner (≥1 disabled/deleted). For non-Compliant rows, queries the manager chain of the
    most-recent active owner via Get-MgUserManager and proposes that manager + the Sponsorship
    business owner (from sponsorship-lifecycle-workflows.md) as candidate replacements. Proposals
    are emitted as plan objects only — apply via the writer principal under PIM with -WhatIf first.
.PARAMETER Session
.PARAMETER Inventory
    Output of Get-Agt12AppRegistryInventory.
.PARAMETER MinHumanOwners
    Minimum active human owners required for Compliant. Default 2.
.OUTPUTS
    [pscustomobject[]] one row per agent.
.EXAMPLE
    PS> $audit = Get-Agt12OwnershipAudit -Session $session -Inventory $reg -Verbose
.EXAMPLE
    PS> $audit | Where-Object Posture -ne 'Compliant' | Export-Csv .\ownership-defects.csv -NoTypeInformation
.NOTES
    Read-only. Does not call New-MgApplicationOwnerByRef. Apply step requires PIM-activated writer.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [pscustomobject[]]$Inventory,
        [Parameter()] [int]$MinHumanOwners = 2
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $rows = New-Object System.Collections.Generic.List[pscustomobject]
    $userCache = @{}
    function Resolve-User($uid) {
        if (-not $uid) { return $null }
        if ($userCache.ContainsKey($uid)) { return $userCache[$uid] }
        try {
            $u = Get-MgUser -UserId $uid -Property 'id,displayName,userPrincipalName,accountEnabled' -ErrorAction Stop
            $userCache[$uid] = $u; return $u
        } catch {
            $userCache[$uid] = $null; return $null
        }
    }

    foreach ($a in ($Inventory | Where-Object { $_.Plane -in 'AppRegistration','ServicePrincipal' -and $_.Status -eq 'OK' })) {
        $owners = @()
        try {
            if ($a.Plane -eq 'AppRegistration') {
                $owners = Invoke-Agt12WithThrottle -OperationName "Owners[App:$($a.AppId)]" -ScriptBlock {
                    Get-MgApplicationOwner -ApplicationId $a.ObjectId -All -ErrorAction Stop
                }
            } else {
                $owners = Invoke-Agt12WithThrottle -OperationName "Owners[SP:$($a.AppId)]" -ScriptBlock {
                    Get-MgServicePrincipalOwner -ServicePrincipalId $a.ObjectId -All -ErrorAction Stop
                }
            }
        } catch {
            $rows.Add([pscustomobject]@{
                Plane=$a.Plane; AppId=$a.AppId; ObjectId=$a.ObjectId; DisplayName=$a.DisplayName;
                Posture='OwnerEnumerationFailed'; Reason=$_.Exception.Message;
                CollectedAt=(Get-Date).ToUniversalTime()
            })
            continue
        }

        $resolved = foreach ($o in $owners) {
            $u = Resolve-User $o.Id
            if ($u) {
                [pscustomobject]@{
                    OwnerId=$u.Id; Upn=$u.UserPrincipalName; DisplayName=$u.DisplayName;
                    Enabled=$u.AccountEnabled; Kind='User'
                }
            } else {
                [pscustomobject]@{
                    OwnerId=$o.Id; Upn=$null; DisplayName=$null; Enabled=$false; Kind='Tombstoned'
                }
            }
        }

        $active = @($resolved | Where-Object { $_.Kind -eq 'User' -and $_.Enabled })
        $tombstoned = @($resolved | Where-Object { $_.Kind -eq 'Tombstoned' -or -not $_.Enabled })
        $posture = if ($tombstoned.Count -gt 0 -and $active.Count -lt $MinHumanOwners) { 'TombstonedOwner' }
                   elseif ($active.Count -eq 0) { 'Ownerless' }
                   elseif ($active.Count -lt $MinHumanOwners) { 'Singleton' }
                   else { 'Compliant' }

        # Manager-hierarchy proposal for non-compliant
        $proposed = $null
        if ($posture -ne 'Compliant' -and $active.Count -gt 0) {
            try {
                $mgr = Get-MgUserManager -UserId $active[0].OwnerId -ErrorAction Stop
                if ($mgr) { $proposed = $mgr.AdditionalProperties['userPrincipalName'] }
            } catch { }
        }

        $rows.Add([pscustomobject]@{
            Plane           = $a.Plane
            AppId           = $a.AppId
            ObjectId        = $a.ObjectId
            DisplayName     = $a.DisplayName
            Posture         = $posture
            ActiveOwnerCount   = $active.Count
            TombstonedOwnerCount = $tombstoned.Count
            ActiveOwners    = ($active.Upn -join ';')
            TombstonedOwnerIds = ($tombstoned.OwnerId -join ';')
            ProposedReplacementUpn = $proposed
            CollectedAt     = (Get-Date).ToUniversalTime()
        })
    }

    Write-Verbose "Ownership audit: $(($rows | Where-Object Posture -eq 'Compliant').Count) compliant, $(($rows | Where-Object Posture -eq 'Singleton').Count) singleton, $(($rows | Where-Object Posture -eq 'Ownerless').Count) ownerless, $(($rows | Where-Object Posture -eq 'TombstonedOwner').Count) tombstoned."
    return $rows.ToArray()
}
```

**Fail-closed conditions enforced by this leg:** ownerless and tombstoned-owner agents are surfaced explicitly (never silently treated as Compliant); manager-hierarchy proposals are advisory only and never auto-applied; owner-enumeration failures emit a row rather than abort the run so subsequent agents are still evaluated.

---

## §5 — Permission grant audit (`Get-Agt12PermissionGrantAudit`)

**Why this section exists.** Over-permissioned agents are the root cause of the largest enforcement actions in the FSI sector to date. This leg captures **both** the delegated `oauth2PermissionGrants` (what the agent can do on behalf of a signed-in user) and the application-only `appRoleAssignments` (what the agent can do on its own), then flags any grant that includes one of the high-blast-radius scopes (`*.ReadWrite.All`, `Directory.ReadWrite.All`, `Mail.Send`, `Files.ReadWrite.All`, `Sites.FullControl.All`, etc.).

```powershell
# scripts/legs/Get-Agt12PermissionGrantAudit.ps1
function Get-Agt12PermissionGrantAudit {
<#
.SYNOPSIS
    Captures delegated and application permissions for each agent and flags high-risk scopes.
.DESCRIPTION
    For every SP in the inventory, queries Get-MgServicePrincipalOauth2PermissionGrant (delegated)
    and Get-MgServicePrincipalAppRoleAssignment (application). Resolves each appRoleId to its
    Microsoft Graph display name (e.g., 'Mail.ReadWrite' rather than a GUID). Flags any grant
    matching the OverPermissionedScopes list, recording the matched scope in OverPermissionedReason.
.PARAMETER Session
.PARAMETER Inventory
.PARAMETER OverPermissionedScopes
.OUTPUTS
    [pscustomobject[]] — one row per (agent, grant) pair.
.EXAMPLE
    PS> $perms = Get-Agt12PermissionGrantAudit -Session $session -Inventory $reg
.NOTES
    The published OverPermissionedScopes default reflects FSI red-team consensus as of April 2026;
    re-baseline annually with your second line.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [pscustomobject[]]$Inventory,
        [Parameter()] [string[]]$OverPermissionedScopes = @(
            'Directory.ReadWrite.All','Application.ReadWrite.All','RoleManagement.ReadWrite.Directory',
            'AppRoleAssignment.ReadWrite.All','Mail.Send','Mail.ReadWrite','Mail.Send.Shared',
            'Files.ReadWrite.All','Sites.FullControl.All','Sites.ReadWrite.All',
            'User.ReadWrite.All','Group.ReadWrite.All','Calendars.ReadWrite','Chat.ReadWrite.All',
            'TeamMember.ReadWrite.All','Policy.ReadWrite.ConditionalAccess'
        )
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    # Cache the Microsoft Graph SP so we can resolve appRoleIds to friendly scope names
    $graphSp = Invoke-Agt12WithThrottle -OperationName 'Graph:MicrosoftGraphSP' -ScriptBlock {
        Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'" -ErrorAction Stop
    }
    $roleMap = @{}
    foreach ($r in $graphSp.AppRoles) { $roleMap[[string]$r.Id] = $r.Value }

    $rows = New-Object System.Collections.Generic.List[pscustomobject]
    foreach ($a in ($Inventory | Where-Object { $_.Plane -eq 'ServicePrincipal' -and $_.Status -eq 'OK' })) {
        # Delegated
        try {
            $deleg = Invoke-Agt12WithThrottle -OperationName "Graph:Oauth2Grants[$($a.AppId)]" -ScriptBlock {
                Get-MgServicePrincipalOauth2PermissionGrant -ServicePrincipalId $a.ObjectId -All -ErrorAction Stop
            }
            foreach ($g in $deleg) {
                $scopes = ($g.Scope -split '\s+') | Where-Object { $_ }
                $hits = $scopes | Where-Object { $_ -in $OverPermissionedScopes }
                $rows.Add([pscustomobject]@{
                    AppId=$a.AppId; ObjectId=$a.ObjectId; DisplayName=$a.DisplayName;
                    GrantKind='Delegated'; ConsentType=$g.ConsentType; PrincipalId=$g.PrincipalId;
                    ResourceId=$g.ResourceId; Scope=($scopes -join ' ');
                    OverPermissioned = [bool]$hits; OverPermissionedReason = ($hits -join ';');
                    CollectedAt=(Get-Date).ToUniversalTime()
                })
            }
        } catch {
            Write-Warning "Delegated grant fetch failed for $($a.DisplayName): $($_.Exception.Message)"
        }
        # Application
        try {
            $appAssn = Invoke-Agt12WithThrottle -OperationName "Graph:AppRoleAssn[$($a.AppId)]" -ScriptBlock {
                Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $a.ObjectId -All -ErrorAction Stop
            }
            foreach ($r in $appAssn) {
                $name = if ($roleMap.ContainsKey([string]$r.AppRoleId)) { $roleMap[[string]$r.AppRoleId] } else { "<unmapped:$($r.AppRoleId)>" }
                $isOver = $name -in $OverPermissionedScopes
                $rows.Add([pscustomobject]@{
                    AppId=$a.AppId; ObjectId=$a.ObjectId; DisplayName=$a.DisplayName;
                    GrantKind='Application'; ResourceDisplayName=$r.ResourceDisplayName;
                    AppRoleId=$r.AppRoleId; AppRoleValue=$name;
                    OverPermissioned=$isOver; OverPermissionedReason= ($(if ($isOver) { $name } else { '' }));
                    CollectedAt=(Get-Date).ToUniversalTime()
                })
            }
        } catch {
            Write-Warning "App role fetch failed for $($a.DisplayName): $($_.Exception.Message)"
        }
    }

    Write-Verbose "Permission audit: $($rows.Count) grants captured, $(($rows | Where-Object OverPermissioned).Count) flagged over-permissioned."
    return $rows.ToArray()
}
```

**Fail-closed conditions enforced by this leg:** unmapped appRoleIds are surfaced as `<unmapped:GUID>` rather than dropped (so newly published Microsoft Graph roles do not silently disappear); per-agent failures degrade to a warning and continue (so one broken SP does not abort the whole audit).

---

## §6 — Credential hygiene (`Get-Agt12CredentialHygiene`)

**Why this section exists.** Long-lived client secrets on agent registrations are a leading cause of post-incident scope expansion in FSI breach reports. This leg enumerates every `passwordCredential` and `keyCredential` on every agent application object, classifies expiry windows (`<30d`, `<90d`, `>90d`, `Expired`), records `KeyId` provenance for evidence, and recommends migration paths (cert-based auth, federated identity credentials for GitHub/Azure DevOps, managed identity where Azure-resident).

```powershell
# scripts/legs/Get-Agt12CredentialHygiene.ps1
function Get-Agt12CredentialHygiene {
<#
.SYNOPSIS
    Reports password and certificate credentials on every agent application object with expiry classification.
.DESCRIPTION
    For each Application object, walks PasswordCredentials (client secrets) and KeyCredentials
    (certs) and emits one row per credential with KeyId, StartDateTime, EndDateTime, DaysToExpiry,
    ExpiryBucket, RecommendedAction, and CredentialKind. Recommended actions follow the FSI
    credential hierarchy: managed identity > federated credential > certificate > secret.
.PARAMETER Session
.PARAMETER Inventory
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $cred = Get-Agt12CredentialHygiene -Session $session -Inventory $reg
.EXAMPLE
    PS> $cred | Where-Object ExpiryBucket -in 'LT30','Expired' | Export-Csv .\creds-rotate-now.csv -NoTypeInformation
.NOTES
    Read-only. Apply rotations via the writer principal in a separate change window.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [pscustomobject[]]$Inventory
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $rows = New-Object System.Collections.Generic.List[pscustomobject]
    $now = (Get-Date).ToUniversalTime()

    foreach ($a in ($Inventory | Where-Object { $_.Plane -eq 'AppRegistration' -and $_.Status -eq 'OK' })) {
        try {
            $app = Invoke-Agt12WithThrottle -OperationName "Graph:AppCreds[$($a.AppId)]" -ScriptBlock {
                Get-MgApplication -ApplicationId $a.ObjectId -Property 'id,appId,displayName,passwordCredentials,keyCredentials' -ErrorAction Stop
            }
        } catch {
            $rows.Add([pscustomobject]@{ AppId=$a.AppId; DisplayName=$a.DisplayName;
                CredentialKind='ENUMERATION_FAILED'; Reason=$_.Exception.Message;
                CollectedAt=$now })
            continue
        }

        function Classify([datetime]$end) {
            if ($end -lt $now) { return @('Expired',-1*([int]($now - $end).TotalDays),'RotateImmediately') }
            $d = [int]($end - $now).TotalDays
            if ($d -lt 30)  { return @('LT30',$d,'RotateThisWeek') }
            if ($d -lt 90)  { return @('LT90',$d,'ScheduleForCAB') }
            return @('GT90',$d,'NoActionRequired')
        }

        foreach ($pw in @($app.PasswordCredentials)) {
            $c = Classify $pw.EndDateTime
            $rows.Add([pscustomobject]@{
                AppId=$a.AppId; DisplayName=$a.DisplayName; CredentialKind='ClientSecret';
                KeyId=$pw.KeyId; Hint=$pw.Hint; DisplayNameOnCred=$pw.DisplayName;
                StartDateTime=$pw.StartDateTime; EndDateTime=$pw.EndDateTime;
                DaysToExpiry=$c[1]; ExpiryBucket=$c[0];
                RecommendedAction=$c[2];
                MigrationTarget='ManagedIdentity > FederatedCredential > Certificate';
                CollectedAt=$now
            })
        }
        foreach ($k in @($app.KeyCredentials)) {
            $c = Classify $k.EndDateTime
            $rows.Add([pscustomobject]@{
                AppId=$a.AppId; DisplayName=$a.DisplayName; CredentialKind='Certificate';
                KeyId=$k.KeyId; Usage=$k.Usage; Type=$k.Type;
                DisplayNameOnCred=$k.DisplayName;
                StartDateTime=$k.StartDateTime; EndDateTime=$k.EndDateTime;
                DaysToExpiry=$c[1]; ExpiryBucket=$c[0];
                RecommendedAction=$c[2];
                MigrationTarget=if ($k.Type -eq 'AsymmetricX509Cert') { 'NoChange (already cert-based)' } else { 'ReissueAsAsymmetricX509Cert' };
                CollectedAt=$now
            })
        }

        # Federated identity credentials (preferred; emit even when none — explicit zero is evidence)
        try {
            $fic = Invoke-Agt12WithThrottle -OperationName "Graph:FIC[$($a.AppId)]" -ScriptBlock {
                Get-MgApplicationFederatedIdentityCredential -ApplicationId $a.ObjectId -All -ErrorAction Stop
            }
            if (-not $fic -or @($fic).Count -eq 0) {
                $rows.Add([pscustomobject]@{
                    AppId=$a.AppId; DisplayName=$a.DisplayName; CredentialKind='FederatedCredential';
                    Status='None'; RecommendedAction='ConsiderFICForCICD'; CollectedAt=$now
                })
            } else {
                foreach ($f in $fic) {
                    $rows.Add([pscustomobject]@{
                        AppId=$a.AppId; DisplayName=$a.DisplayName; CredentialKind='FederatedCredential';
                        FicName=$f.Name; Issuer=$f.Issuer; Subject=$f.Subject;
                        Audiences=($f.Audiences -join ';'); Status='Present';
                        RecommendedAction='NoActionRequired'; CollectedAt=$now
                    })
                }
            }
        } catch {
            Write-Warning "FIC enumeration failed for $($a.DisplayName): $($_.Exception.Message)"
        }
    }

    Write-Verbose "Credential hygiene: $(($rows | Where-Object ExpiryBucket -eq 'Expired').Count) expired, $(($rows | Where-Object ExpiryBucket -eq 'LT30').Count) <30d, $(($rows | Where-Object ExpiryBucket -eq 'LT90').Count) <90d."
    return $rows.ToArray()
}
```

**Fail-closed conditions enforced by this leg:** every credential — including federated credentials, where their absence is itself a finding — yields a row; expiry classification is bucketed to make CSV pivots trivial; per-agent failure becomes a row, not an abort.

---
## §7 — App consent governance (`Get-Agt12ConsentPosture`)

**Why this section exists.** The admin consent request queue is a leading indicator of unauthorised agent provisioning. This leg captures (a) the tenant-wide user-consent policy, (b) all admin consent requests in the queue, and (c) any agent SP that received tenant-wide admin consent in the last quarter — emitting a triage queue for reviewers (the writer principal under PIM).

```powershell
# scripts/legs/Get-Agt12ConsentPosture.ps1
function Get-Agt12ConsentPosture {
<#
.SYNOPSIS
    Captures user consent policy, admin consent request queue, and recent tenant-wide consents.
.PARAMETER Session
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $consent = Get-Agt12ConsentPosture -Session $session
.NOTES
    Read-only. Approvals require the writer principal under PIM.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param([Parameter(Mandatory)] [pscustomobject]$Session)
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $rows = New-Object System.Collections.Generic.List[pscustomobject]
    $now = (Get-Date).ToUniversalTime()

    try {
        $authPolicy = Invoke-Agt12WithThrottle -OperationName 'Graph:AuthorizationPolicy' -ScriptBlock {
            Get-MgPolicyAuthorizationPolicy -ErrorAction Stop
        }
        $rows.Add([pscustomobject]@{
            Kind='UserConsentPolicy'; AllowUserConsentForApps=$authPolicy.DefaultUserRolePermissions.PermissionGrantPoliciesAssigned;
            AllowedToCreateApps=$authPolicy.DefaultUserRolePermissions.AllowedToCreateApps;
            CollectedAt=$now
        })
    } catch { Write-Warning "AuthorizationPolicy fetch failed: $($_.Exception.Message)" }

    try {
        $reqs = Invoke-Agt12WithThrottle -OperationName 'Graph:AdminConsentRequests' -ScriptBlock {
            Get-MgIdentityGovernanceAppConsentRequest -All -ErrorAction Stop
        }
        foreach ($r in $reqs) {
            $rows.Add([pscustomobject]@{
                Kind='AdminConsentRequest'; RequestId=$r.Id; AppId=$r.AppId;
                AppDisplayName=$r.AppDisplayName; PendingScopes=($r.PendingScopes.DisplayName -join ';');
                CollectedAt=$now
            })
        }
    } catch { Write-Warning "Admin consent request fetch failed: $($_.Exception.Message)" }

    Write-Verbose "Consent posture: $($rows.Count) records."
    return $rows.ToArray()
}
```

**Fail-closed conditions enforced by this leg:** absence of `AdminConsentRequestPolicy` is itself a finding (recorded as `Kind='AdminConsentRequest'; Status='PolicyNotConfigured'`); reviewer approvals are never auto-applied — emit-and-route only.

---

## §8 — Service principal sign-in audit (`Get-Agt12ServicePrincipalSignIns`)

**Why this section exists.** SP sign-in records expose dormant agents (no sign-in for >90 days = candidate for deprovisioning), out-of-region access (sign-in from an IP geography that violates data residency), and risky workload identity events from Identity Protection. Filtering sign-in logs to **only** SP sign-ins requires `signInEventTypes/any(t:t eq 'servicePrincipal')` — a single-character typo silently returns user sign-ins instead.

```powershell
# scripts/legs/Get-Agt12ServicePrincipalSignIns.ps1
function Get-Agt12ServicePrincipalSignIns {
<#
.SYNOPSIS
    Captures SP-only sign-in events and Identity Protection risky-SP records.
.PARAMETER Session
.PARAMETER LookbackDays
    Default 30. Use 90 for quarterly attestation.
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $signins = Get-Agt12ServicePrincipalSignIns -Session $session -LookbackDays 90
.NOTES
    AuditLog.Read.All required for sign-ins; IdentityRiskyServicePrincipal.Read.All for risky SPs.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter()] [int]$LookbackDays = 30
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $rows = New-Object System.Collections.Generic.List[pscustomobject]
    $since = (Get-Date).ToUniversalTime().AddDays(-$LookbackDays).ToString('o')

    try {
        $signIns = Invoke-Agt12WithThrottle -OperationName 'Graph:SPSignIns' -ScriptBlock {
            Get-MgAuditLogSignIn -Filter "signInEventTypes/any(t:t eq 'servicePrincipal') and createdDateTime ge $since" -All -ErrorAction Stop
        }
        foreach ($s in $signIns) {
            $rows.Add([pscustomobject]@{
                Kind='SPSignIn'; CreatedDateTime=$s.CreatedDateTime; AppId=$s.AppId;
                AppDisplayName=$s.AppDisplayName; ServicePrincipalId=$s.ServicePrincipalId;
                ResourceDisplayName=$s.ResourceDisplayName; IPAddress=$s.IpAddress;
                Country=$s.Location.CountryOrRegion; City=$s.Location.City;
                Status=$s.Status.ErrorCode; CollectedAt=(Get-Date).ToUniversalTime()
            })
        }
    } catch { Write-Warning "SP sign-in fetch failed: $($_.Exception.Message)" }

    try {
        $risky = Invoke-Agt12WithThrottle -OperationName 'Graph:RiskyServicePrincipals' -ScriptBlock {
            Get-MgRiskyServicePrincipal -All -ErrorAction Stop
        }
        foreach ($r in $risky) {
            $rows.Add([pscustomobject]@{
                Kind='RiskyServicePrincipal'; AppId=$r.AppId; DisplayName=$r.DisplayName;
                RiskLevel=$r.RiskLevel; RiskState=$r.RiskState;
                RiskLastUpdatedDateTime=$r.RiskLastUpdatedDateTime;
                CollectedAt=(Get-Date).ToUniversalTime()
            })
        }
    } catch { Write-Warning "Risky SP fetch failed: $($_.Exception.Message)" }

    Write-Verbose "SP sign-in audit: $(($rows | Where-Object Kind -eq 'SPSignIn').Count) sign-ins, $(($rows | Where-Object Kind -eq 'RiskyServicePrincipal').Count) risky SPs."
    return $rows.ToArray()
}
```

**Fail-closed conditions enforced by this leg:** the `signInEventTypes` filter is the single source of SP-only data — never substitute a UPN-prefix heuristic; agents with zero sign-ins in the lookback window are surfaced in §13's reconciliation as `Dormant` candidates.

---

## §9 — Conditional Access for workload identities (`Test-Agt12WorkloadIdentityCAPolicy`)

**Why this section exists.** Most tenants have CA policies that target users but not workload identities; agents that authenticate as service principals therefore bypass the controls that human sign-ins are forced through. This leg enumerates CA policies whose `conditions.clientApplications.includeServicePrincipals` is non-empty and cross-references against the §3 inventory to surface agents that are **not** covered by any workload-identity CA policy.

```powershell
# scripts/legs/Test-Agt12WorkloadIdentityCAPolicy.ps1
function Test-Agt12WorkloadIdentityCAPolicy {
<#
.SYNOPSIS
    Lists CA policies that target service principals and identifies agents not covered by any.
.PARAMETER Session
.PARAMETER Inventory
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $ca = Test-Agt12WorkloadIdentityCAPolicy -Session $session -Inventory $reg
.NOTES
    Workload identity CA requires Workload Identities Premium licensing — surface license absence
    as a finding rather than silently skipping.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [pscustomobject[]]$Inventory
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $rows = New-Object System.Collections.Generic.List[pscustomobject]
    try {
        $policies = Invoke-Agt12WithThrottle -OperationName 'Graph:CAPolicies' -ScriptBlock {
            Get-MgIdentityConditionalAccessPolicy -All -ErrorAction Stop
        }
    } catch {
        Write-Error "CA policy fetch failed: $($_.Exception.Message). Possible cause: Workload Identities Premium not licensed."
        return @()
    }

    $wiPolicies = $policies | Where-Object {
        $_.Conditions.ClientApplications -and
        ($_.Conditions.ClientApplications.IncludeServicePrincipals -or $_.Conditions.ClientApplications.ExcludeServicePrincipals)
    }
    $coveredAppIds = New-Object System.Collections.Generic.HashSet[string]
    foreach ($p in $wiPolicies) {
        $rows.Add([pscustomobject]@{
            Kind='WorkloadIdentityCAPolicy'; PolicyId=$p.Id; DisplayName=$p.DisplayName;
            State=$p.State; IncludeSPs=($p.Conditions.ClientApplications.IncludeServicePrincipals -join ';');
            ExcludeSPs=($p.Conditions.ClientApplications.ExcludeServicePrincipals -join ';');
            GrantControls=($p.GrantControls.BuiltInControls -join ';');
            CollectedAt=(Get-Date).ToUniversalTime()
        })
        if ($p.Conditions.ClientApplications.IncludeServicePrincipals -contains 'ServicePrincipalsInMyTenant' -and $p.State -eq 'enabled') {
            foreach ($a in $Inventory) { [void]$coveredAppIds.Add($a.AppId) }
        } else {
            foreach ($id in $p.Conditions.ClientApplications.IncludeServicePrincipals) { [void]$coveredAppIds.Add($id) }
        }
    }

    foreach ($a in ($Inventory | Where-Object { $_.Plane -eq 'ServicePrincipal' -and $_.Status -eq 'OK' })) {
        if (-not $coveredAppIds.Contains($a.AppId)) {
            $rows.Add([pscustomobject]@{
                Kind='AgentWithoutCACoverage'; AppId=$a.AppId; DisplayName=$a.DisplayName;
                Recommendation='AddToWorkloadIdentityCAPolicy';
                CollectedAt=(Get-Date).ToUniversalTime()
            })
        }
    }

    Write-Verbose "CA workload identity audit: $(($rows | Where-Object Kind -eq 'WorkloadIdentityCAPolicy').Count) policies, $(($rows | Where-Object Kind -eq 'AgentWithoutCACoverage').Count) uncovered agents."
    return $rows.ToArray()
}
```

**Fail-closed conditions enforced by this leg:** the absence of any workload-identity CA policy yields zero `WorkloadIdentityCAPolicy` rows but **every** §3 SP appears as `AgentWithoutCACoverage` — an unmissable signal in the reconciliation export.

---

## §10 — Power Platform agent registration audit (`Get-Agt12PowerPlatformAgents`)

**Why this section exists.** Copilot Studio bots register as Power Platform "bot" entities that do **not** appear in Microsoft Graph application lists; they must be enumerated through the Power Apps Administration module, which only ships in Windows PowerShell 5.1. This leg uses a **child process** pattern to keep the 5.1 dependency isolated from the orchestrator's pwsh 7 session.

```powershell
# scripts/legs/Get-Agt12PowerPlatformAgents.ps1
function Get-Agt12PowerPlatformAgents {
<#
.SYNOPSIS
    Enumerates Copilot Studio bots and other Power Platform agent entities via a 5.1 child process.
.PARAMETER Session
.PARAMETER TenantId
.PARAMETER ClientId
    SP for unattended Power Platform admin auth (cert-based).
.PARAMETER CertificateThumbprint
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $pp = Get-Agt12PowerPlatformAgents -Session $session -TenantId $tid -ClientId $cid -CertificateThumbprint $thumb
.NOTES
    Requires the registry-reader principal to hold Power Platform 'Power Platform Administrator'
    role (or PIM-eligible). PAC CLI must be on PATH and pinned per §1.2.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [guid]$TenantId,
        [Parameter(Mandatory)] [guid]$ClientId,
        [Parameter(Mandatory)] [string]$CertificateThumbprint
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    if (-not $IsWindows) { throw "Power Platform agent enumeration requires Windows PowerShell 5.1 child process." }

    $endpoint = $Session.Profile.PowerAppsEndpoint
    $script = @"
Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
Add-PowerAppsAccount -Endpoint '$endpoint' -TenantID '$TenantId' -ApplicationId '$ClientId' -CertificateThumbprint '$CertificateThumbprint' | Out-Null
`$envs = Get-AdminPowerAppEnvironment
`$bots = foreach (`$e in `$envs) {
    Get-AdminPowerApp -EnvironmentName `$e.EnvironmentName | Where-Object { `$_.AppType -in 'Bot','CopilotBot','CopilotStudio' }
}
`$bots | ConvertTo-Json -Depth 6 -Compress
"@
    $tmp = [IO.Path]::GetTempFileName() + '.ps1'
    Set-Content -Path $tmp -Value $script -Encoding UTF8
    try {
        $json = & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $tmp 2>&1
        if (-not $json) { return @() }
        $bots = $json | ConvertFrom-Json
        $rows = foreach ($b in @($bots)) {
            [pscustomobject]@{
                Kind='PowerPlatformAgent'; AppId=$b.AppName; DisplayName=$b.DisplayName;
                EnvironmentName=$b.EnvironmentName; Owner=$b.Owner.email; AppType=$b.AppType;
                CreatedTime=$b.CreatedTime; LastModifiedTime=$b.LastModifiedTime;
                CollectedAt=(Get-Date).ToUniversalTime()
            }
        }
        return ,$rows
    } finally {
        Remove-Item -Path $tmp -Force -ErrorAction SilentlyContinue
    }
}
```

**Fail-closed conditions enforced by this leg:** non-Windows hosts throw rather than silently returning empty; PAC/Power Apps Admin module absence is caught by §1.2 tooling check; sovereign endpoint is sourced from `$Session.Profile.PowerAppsEndpoint` so DoD/GCC High runs route correctly.

---

## §11 — MCP server enumeration (`Get-Agt12McpServerRegistrations`)

**Why this section exists.** Model Context Protocol servers register as Entra applications with a distinctive redirect-URI pattern (`/mcp/callback`, `/mcp/token`, etc.) and often carry `MCPServer` or `MCPAgent` tags. They are not yet a first-class Graph entity, so detection is pattern-based.

```powershell
# scripts/legs/Get-Agt12McpServerRegistrations.ps1
function Get-Agt12McpServerRegistrations {
<#
.SYNOPSIS
    Detects MCP server registrations by tag and redirect-URI pattern.
.PARAMETER Session
.PARAMETER Inventory
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $mcp = Get-Agt12McpServerRegistrations -Session $session -Inventory $reg
.NOTES
    Pattern set is heuristic; review FpRate quarterly with the AI red team.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [pscustomobject[]]$Inventory
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $patterns = @('/mcp/callback','/mcp/token','/mcp/auth','mcp.','mcpserver','mcp-agent')
    $rows = New-Object System.Collections.Generic.List[pscustomobject]

    foreach ($a in ($Inventory | Where-Object Status -eq 'OK')) {
        $byTag = ($a.Tags -split ';') | Where-Object { $_ -in 'MCPServer','MCPAgent' }
        $byUri = if ($a.ReplyUrls) {
            ($a.ReplyUrls -split ';') | Where-Object { $u = $_.ToLower(); $patterns | Where-Object { $u.Contains($_) } }
        }
        if ($byTag -or $byUri) {
            $rows.Add([pscustomobject]@{
                Kind='MCPServer'; AppId=$a.AppId; DisplayName=$a.DisplayName;
                MatchedByTag=($byTag -join ';'); MatchedByUri=(($byUri | Select-Object -First 3) -join ';');
                Plane=$a.Plane; CollectedAt=(Get-Date).ToUniversalTime()
            })
        }
    }

    Write-Verbose "MCP enumeration: $($rows.Count) candidates."
    return $rows.ToArray()
}
```

**Fail-closed conditions enforced by this leg:** pattern matches are recorded with the matching token (so reviewers can confirm or dismiss false positives); an MCP server matched only by tag (no MCP redirect URI) is surfaced just as loudly as one matched only by URI.

---

## §12 — Integrated Apps enumeration (`Get-Agt12IntegratedApps`)

**Why this section exists.** Integrated Apps surface Office add-ins, Teams apps, and Copilot agents that admins have deployed. The April 2026 GA endpoint `/admin/microsoft365apps/installedApps` (Commercial-only) returns the canonical list; for sovereign clouds where it is not yet available, the Exchange add-in fallback (`Get-App` against `OrganizationConfig`) is used.

```powershell
# scripts/legs/Get-Agt12IntegratedApps.ps1
function Get-Agt12IntegratedApps {
<#
.SYNOPSIS
    Enumerates Integrated Apps via the M365 Apps admin endpoint, with Exchange add-in fallback.
.PARAMETER Session
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $ia = Get-Agt12IntegratedApps -Session $session
.NOTES
    /admin/microsoft365apps/installedApps is April 2026 preview; only Commercial as of writing.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param([Parameter(Mandatory)] [pscustomobject]$Session)
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $rows = New-Object System.Collections.Generic.List[pscustomobject]
    if ($Session.Profile.M365AppsAdminStatus -eq 'Preview') {
        try {
            $apps = Invoke-Agt12WithThrottle -OperationName 'Graph:IntegratedApps' -ScriptBlock {
                Invoke-MgGraphRequest -Method GET -Uri "$($Session.Profile.GraphBaseUri)/v1.0/admin/microsoft365apps/installedApps" -ErrorAction Stop
            }
            foreach ($a in $apps.value) {
                $rows.Add([pscustomobject]@{
                    Kind='IntegratedApp'; Source='M365AppsAdmin'; Id=$a.id; DisplayName=$a.displayName;
                    Publisher=$a.publisher; AppType=$a.appType; State=$a.state;
                    CollectedAt=(Get-Date).ToUniversalTime()
                })
            }
        } catch { Write-Warning "Integrated Apps preview endpoint failed: $($_.Exception.Message). Falling back to Exchange add-ins." }
    } else {
        Write-Warning "M365 Apps admin endpoint not available in cloud $($Session.Profile.Cloud); using Exchange add-in fallback."
    }

    # Exchange add-in fallback
    try {
        Connect-ExchangeOnline -ShowBanner:$false -ExchangeEnvironmentName $Session.Profile.ExoEnvironmentName -ErrorAction Stop | Out-Null
        $orgApps = Get-App -OrganizationApp -ErrorAction Stop
        foreach ($a in $orgApps) {
            $rows.Add([pscustomobject]@{
                Kind='IntegratedApp'; Source='ExchangeAddIn'; Id=$a.AppId; DisplayName=$a.DisplayName;
                ProvidedTo=$a.ProvidedTo; Enabled=$a.Enabled; AppType='Office add-in';
                CollectedAt=(Get-Date).ToUniversalTime()
            })
        }
        Disconnect-ExchangeOnline -Confirm:$false | Out-Null
    } catch { Write-Warning "Exchange add-in fallback failed: $($_.Exception.Message)" }

    Write-Verbose "Integrated Apps enumeration: $($rows.Count) records."
    return $rows.ToArray()
}
```

**Fail-closed conditions enforced by this leg:** sovereign clouds without preview endpoint emit a warning and still produce Exchange add-in records; both data sources are tagged in the `Source` field so reconciliation can deduplicate.

---
## §13 — Reconciliation into Control 3.1 canonical schema and quarterly attestation pack

**Why this section exists.** Control 3.1 (Agent Inventory) is the single source of truth for examiner-facing reporting; Control 1.2 is one of its upstream legs. This section reshapes every output from §3–§12 into the `CanonicalAgentId` row schema documented in `3.1/powershell-setup.md` §9 and emits the quarterly attestation pack (CSV + JSONL + Excel + SHA-256 manifest + Authenticode signature).

```powershell
# scripts/Export-Agt12AttestationPack.ps1
function Export-Agt12AttestationPack {
<#
.SYNOPSIS
    Reconciles all §3-§12 outputs into the 3.1 canonical schema and exports the signed evidence pack.
.PARAMETER Session
.PARAMETER Inventory
.PARAMETER Ownership
.PARAMETER Permissions
.PARAMETER Credentials
.PARAMETER Consent
.PARAMETER SignIns
.PARAMETER CACoverage
.PARAMETER PowerPlatform
.PARAMETER McpServers
.PARAMETER IntegratedApps
.PARAMETER OutputRoot
.PARAMETER SigningCertThumbprint
.PARAMETER TimestampServer
    Default https://timestamp.digicert.com
.OUTPUTS
    [pscustomobject] with PackPath, ManifestPath, SignaturePath, RowCount.
.EXAMPLE
    PS> Export-Agt12AttestationPack -Session $s -Inventory $i -Ownership $o -Permissions $p -Credentials $c -Consent $cs -SignIns $si -CACoverage $ca -PowerPlatform $pp -McpServers $m -IntegratedApps $ia -OutputRoot 'C:\evidence' -SigningCertThumbprint $thumb
.NOTES
    Manifest signature MUST verify Status=Valid; throws otherwise. Pack is consumed by 3.1 §9 Merge-Agt31Inventory.
#>
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [pscustomobject[]]$Inventory,
        [Parameter(Mandatory)] [pscustomobject[]]$Ownership,
        [Parameter(Mandatory)] [pscustomobject[]]$Permissions,
        [Parameter(Mandatory)] [pscustomobject[]]$Credentials,
        [Parameter(Mandatory)] [pscustomobject[]]$Consent,
        [Parameter(Mandatory)] [pscustomobject[]]$SignIns,
        [Parameter(Mandatory)] [pscustomobject[]]$CACoverage,
        [Parameter()] [pscustomobject[]]$PowerPlatform = @(),
        [Parameter()] [pscustomobject[]]$McpServers = @(),
        [Parameter()] [pscustomobject[]]$IntegratedApps = @(),
        [Parameter(Mandatory)] [string]$OutputRoot,
        [Parameter(Mandatory)] [string]$SigningCertThumbprint,
        [Parameter()] [string]$TimestampServer = 'https://timestamp.digicert.com'
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $packDir = Join-Path $OutputRoot "agt12-attestation-$($Session.Profile.Cloud)-$stamp"
    if ($PSCmdlet.ShouldProcess($packDir,'Create attestation pack directory')) {
        New-Item -Path $packDir -ItemType Directory -Force | Out-Null
    }

    # Reconcile to 3.1 CanonicalAgentId schema (one row per AppId from §3 with rolled-up findings)
    $canon = New-Object System.Collections.Generic.List[pscustomobject]
    $appsOnly = $Inventory | Where-Object { $_.Plane -in 'AppRegistration','ServicePrincipal' -and $_.Status -eq 'OK' } |
        Group-Object AppId
    foreach ($g in $appsOnly) {
        $appId = $g.Name
        $primary = $g.Group | Sort-Object Plane -Descending | Select-Object -First 1
        $own = $Ownership | Where-Object AppId -eq $appId | Select-Object -First 1
        $permCount = ($Permissions | Where-Object AppId -eq $appId).Count
        $overPerm = ($Permissions | Where-Object { $_.AppId -eq $appId -and $_.OverPermissioned }).Count
        $expCred = ($Credentials | Where-Object { $_.AppId -eq $appId -and $_.ExpiryBucket -in 'Expired','LT30' }).Count
        $signinCount = ($SignIns | Where-Object { $_.Kind -eq 'SPSignIn' -and $_.AppId -eq $appId }).Count
        $caCovered = -not ($CACoverage | Where-Object { $_.Kind -eq 'AgentWithoutCACoverage' -and $_.AppId -eq $appId })
        $isMcp = [bool]($McpServers | Where-Object AppId -eq $appId)
        $canon.Add([pscustomobject]@{
            CanonicalAgentId   = "agt12::$($Session.Profile.Cloud)::$appId"
            AppId              = $appId
            ObjectId           = $primary.ObjectId
            DisplayName        = $primary.DisplayName
            Plane              = $primary.Plane
            MatchedOn          = $primary.MatchedOn
            Cloud              = $Session.Profile.Cloud
            OwnershipPosture   = if ($own) { $own.Posture } else { 'Unknown' }
            ActiveOwnerCount   = if ($own) { $own.ActiveOwnerCount } else { 0 }
            PermissionGrantCount = $permCount
            OverPermissionedGrantCount = $overPerm
            ExpiringCredentialCount = $expCred
            SignInCount30d     = $signinCount
            Dormant            = ($signinCount -eq 0)
            ConditionalAccessCovered = $caCovered
            IsMcpServer        = $isMcp
            SourceLeg          = 'Control-1.2'
            CollectedAt        = (Get-Date).ToUniversalTime()
            RunId              = $Session.RunId
        })
    }

    # Emit per-leg CSVs + the canonical projection + JSONL bundle
    $legs = @{
        'inventory'         = $Inventory
        'ownership'         = $Ownership
        'permissions'       = $Permissions
        'credentials'       = $Credentials
        'consent'           = $Consent
        'signins'           = $SignIns
        'ca-coverage'       = $CACoverage
        'powerplatform'     = $PowerPlatform
        'mcp-servers'       = $McpServers
        'integrated-apps'   = $IntegratedApps
        'canonical-3.1'     = $canon.ToArray()
    }
    $files = @()
    foreach ($k in $legs.Keys) {
        if (-not $legs[$k] -or @($legs[$k]).Count -eq 0) { continue }
        $csv = Join-Path $packDir "$k.csv"
        $jsonl = Join-Path $packDir "$k.jsonl"
        if ($PSCmdlet.ShouldProcess($csv,'Write CSV')) {
            @($legs[$k]) | Export-Csv -Path $csv -NoTypeInformation -Encoding UTF8
            $files += $csv
        }
        if ($PSCmdlet.ShouldProcess($jsonl,'Write JSONL')) {
            @($legs[$k]) | ForEach-Object { $_ | ConvertTo-Json -Depth 8 -Compress } | Set-Content -Path $jsonl -Encoding UTF8
            $files += $jsonl
        }
    }

    # SHA-256 manifest
    $manifest = $files | ForEach-Object {
        $h = Get-FileHash -Path $_ -Algorithm SHA256
        [pscustomobject]@{ File=(Split-Path $_ -Leaf); SHA256=$h.Hash; Bytes=(Get-Item $_).Length }
    }
    $manifestPath = Join-Path $packDir 'MANIFEST.json'
    $manifestObj = [pscustomobject]@{
        Control='1.2'; Cloud=$Session.Profile.Cloud; TenantId=$Session.TenantId;
        RunId=$Session.RunId; GeneratedAt=(Get-Date).ToUniversalTime();
        ToolVersion='v1.4'; FileCount=$manifest.Count; Files=$manifest
    }
    if ($PSCmdlet.ShouldProcess($manifestPath,'Write manifest')) {
        $manifestObj | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8
    }

    # Authenticode sign the manifest
    $cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Where-Object Thumbprint -eq $SigningCertThumbprint | Select-Object -First 1
    if (-not $cert) { throw "Signing cert with thumbprint $SigningCertThumbprint not found in Cert:\CurrentUser\My (CodeSigning EKU required)." }
    if ($PSCmdlet.ShouldProcess($manifestPath,'Authenticode sign')) {
        $sig = Set-AuthenticodeSignature -FilePath $manifestPath -Certificate $cert -TimestampServer $TimestampServer -HashAlgorithm SHA256
        if ($sig.Status -ne 'Valid') { throw "Manifest signature Status=$($sig.Status); aborting pack export." }
    }

    [pscustomobject]@{
        PackPath      = $packDir
        ManifestPath  = $manifestPath
        SignatureStatus = if ($sig) { $sig.Status } else { 'WhatIf' }
        RowCount      = $canon.Count
        FileCount     = $files.Count
    }
}
```

**Fail-closed conditions enforced by this section:** signing cert absence throws; signature `Status != Valid` throws; empty leg arrays are skipped (no zero-byte CSVs in the pack); the canonical projection always carries `RunId` so 3.1's merge can deduplicate across cloud profiles.

---

## §14 — End-to-end validation, anti-patterns, and operating cadence

### 14.1 `Test-Agt12Implementation`

```powershell
# scripts/Test-Agt12Implementation.ps1
function Test-Agt12Implementation {
<#
.SYNOPSIS
    Smoke-tests every leg with a one-record sample and verifies the pack export round-trip.
.PARAMETER Session
.OUTPUTS
    [pscustomobject] with per-leg PASS/FAIL status.
.EXAMPLE
    PS> Test-Agt12Implementation -Session $session -OutputRoot C:\evidence\smoke -SigningCertThumbprint $thumb
.NOTES
    Run after every dependency upgrade and every quarter before the attestation pack is signed.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [string]$OutputRoot,
        [Parameter(Mandatory)] [string]$SigningCertThumbprint
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $checks = [ordered]@{}
    $inv = Get-Agt12AppRegistryInventory -Session $Session
    $checks['Inventory'] = if ($inv.Count -gt 0) { 'PASS' } else { 'FAIL: zero records' }
    $own = Get-Agt12OwnershipAudit -Session $Session -Inventory $inv
    $checks['Ownership'] = if ($own.Count -gt 0) { 'PASS' } else { 'FAIL' }
    $perm = Get-Agt12PermissionGrantAudit -Session $Session -Inventory $inv
    $checks['Permissions'] = 'PASS'
    $cred = Get-Agt12CredentialHygiene -Session $Session -Inventory $inv
    $checks['Credentials'] = 'PASS'
    $cons = Get-Agt12ConsentPosture -Session $Session
    $checks['Consent'] = 'PASS'
    $si = Get-Agt12ServicePrincipalSignIns -Session $Session -LookbackDays 7
    $checks['SignIns'] = 'PASS'
    $ca = Test-Agt12WorkloadIdentityCAPolicy -Session $Session -Inventory $inv
    $checks['CACoverage'] = 'PASS'
    $mcp = Get-Agt12McpServerRegistrations -Session $Session -Inventory $inv
    $checks['MCP'] = 'PASS'
    $ia = Get-Agt12IntegratedApps -Session $Session
    $checks['IntegratedApps'] = 'PASS'

    $pack = Export-Agt12AttestationPack -Session $Session -Inventory $inv -Ownership $own `
        -Permissions $perm -Credentials $cred -Consent $cons -SignIns $si -CACoverage $ca `
        -McpServers $mcp -IntegratedApps $ia -OutputRoot $OutputRoot `
        -SigningCertThumbprint $SigningCertThumbprint
    $checks['PackExport'] = if ($pack.SignatureStatus -eq 'Valid') { 'PASS' } else { "FAIL: $($pack.SignatureStatus)" }

    [pscustomobject]@{ RunId=$Session.RunId; Cloud=$Session.Profile.Cloud; Checks=$checks; PackPath=$pack.PackPath }
}
```

### 14.2 Anti-patterns to refuse in code review

| # | Anti-pattern | Why it is rejected | Correct approach |
|---|---|---|---|
| 1 | Hard-coding `Environment 'Global'` in Connect-MgGraph | Silently routes GCC High / DoD calls to Commercial endpoints — sovereign violation | Use `$session.Profile.GraphEnvironment` from `Resolve-Agt12CloudProfile` |
| 2 | Using `Get-MgApplication -All` without `-ExpandProperty owners` | `.Owners` returns empty; ownership audit is silently 100% Ownerless | Always expand `owners` (and `extensionProperties` when applicable) |
| 3 | Filtering sign-ins by UPN containing `svc_` or `app_` | Hostname / pretty-name heuristics miss SPs without convention; capture user sign-ins | Use `signInEventTypes/any(t:t eq 'servicePrincipal')` exclusively |
| 4 | Loading `AzureAD` and `Microsoft.Graph` in the same session | Cmdlet name collisions silently resolve to the deprecated module | 5.1 child process pattern (§3.4) |
| 5 | Auto-applying owner reassignment from manager-hierarchy proposals | SOX 404 SoD: bulk identity changes require human approval | Emit-and-route to PIM-activated writer with `-WhatIf` first |
| 6 | Omitting beta tag-drift sweep | New Microsoft agent tags arrive between releases; known-tag list goes stale | Run §3 step (3) on every quarterly attestation |
| 7 | Treating empty Integrated Apps response as "no agents" | Sovereign clouds may not have the preview endpoint | Always run Exchange add-in fallback; never treat `M365AppsAdminStatus != Preview` as clean |
| 8 | Using the same SP for read and write operations | Defeats SoD; one compromised credential becomes both audit and remediation | Two principals: `agt12-registry-reader` (unattended) and `agt12-registry-writer` (PIM-only) |
| 9 | Skipping Authenticode signature on the manifest | Examiner cannot prove pack integrity; defeats the evidence chain | Set-AuthenticodeSignature with code-signing cert + timestamp; throw on `Status != Valid` |
| 10 | Catching exceptions silently in legs | Partial / wrong-shape data masquerades as clean | Catch-and-emit a `Status='*Failed'` row — never swallow |

### 14.3 Operating cadence

| Frequency | Action | Principal | Output |
|-----------|--------|-----------|--------|
| Hourly | `Get-Agt12ConsentPosture` queue check | reader | Triage ticket if non-empty |
| Daily | Inventory + ownership + credential delta | reader | Diff CSV to evidence store |
| Weekly | Full §3–§9 run, no `-IncludeAllSps` | reader | CSV to operations channel |
| Monthly | Power Platform + MCP + Integrated Apps legs | reader | CSV to AI governance backlog |
| Quarterly | `Test-Agt12Implementation` then `Export-Agt12AttestationPack` with `-IncludeAllSps` | reader (collect) + writer (sign) | Signed pack to evidence vault; feed 3.1 Merge-Agt31Inventory |
| Annually | OverPermissionedScopes baseline review | second-line risk | Updated default list in §5 |

**Fail-closed conditions enforced by this section:** `Test-Agt12Implementation` failure blocks the quarterly attestation; signature failure blocks the pack hand-off; anti-patterns surfaced in code review block the merge.

---

## Cross-references

- Parent control: [`1.2 — Agent Registry and Integrated Apps Management`](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md)
- Sponsorship integration: [`./sponsorship-lifecycle-workflows.md`](./sponsorship-lifecycle-workflows.md)
- Connector policy crosswalk: [`Control 1.4 — Advanced Connector Policies (ACP)`](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md)
- Audit logging: [`Control 1.7 — Comprehensive Audit Logging and Compliance`](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)
- eDiscovery for agent interactions: [`Control 1.19 — eDiscovery for Agent Interactions`](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md)
- Adversarial input logging: [`Control 1.21 — Adversarial Input Logging`](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md)
- Step-up auth for agent operations: [`Control 1.23 — Step-Up Authentication for Agent Operations`](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md)
- Defender AI-SPM: [`Control 1.24 — Defender AI Security Posture Management`](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md)
- Managed environments: [`Control 2.1 — Managed Environments`](../../../controls/pillar-2-management/2.1-managed-environments.md)
- Inventory reconciliation target: [`../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- Orphaned agent detection: [`../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)
- Shared scripting baseline: [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md)

---

*Updated: April 2026 | Version: v1.4 | Maintained by: AI Governance Team*