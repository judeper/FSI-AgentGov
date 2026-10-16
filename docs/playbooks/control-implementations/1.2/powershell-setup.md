# Control 1.2 — PowerShell Setup: Agent Registry and Integrated Apps Management Automation

> **Scope.** This playbook automates the **agent identity and registration plane** for Control 1.2 across **Entra app registrations, enterprise applications (service principals), Integrated Apps in the Microsoft 365 admin center, Microsoft Copilot Studio agent registrations, MCP server registrations, the emerging Microsoft Entra Agent ID surface, and Agent 365 admin endpoints** in US financial services tenants. It assumes you have already read [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) (referenced below as **BL-§N**) and the parent control specification [`../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md`](../../../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md).
>
> **What this playbook is.** A set of registration-plane collection examples: certificate-authenticated Graph reads using a **separate** registry-reader principal, application and service-principal evidence, ownership and permission reviews, and exports for reconciliation with [Control 3.1](../3.1/powershell-setup.md). These examples are not a deployed collector or a complete attestation engine. Validate the selected module versions and the environment-specific evidence workflow before scheduling them.
>
> **What this playbook is not.** It does not replace the authoritative system of record (the Control 3.1 inventory, the GRC tool, or the SharePoint sponsorship register). A successful directory query does not prove that every agent has been found. Reconcile the Agent Registry package catalog, Entra Agent ID, Dataverse, and manual evidence; a missing entitlement or failed collection is **Unknown**, not an empty compliant population. It does not, by itself, *approve, decommission, transfer, or rotate* registrations; it raises evidence and recommends action, and humans accept risk.
>
> **Hedged language reminder.** Output of this harness *supports* compliance with FINRA Rule 4511, FINRA RN 24-09 / Rule 3110, SEC Rule 17a-4(b)(4) / 17a-4(g), SOX 302/404, GLBA 501(b), NYDFS 23 NYCRR 500.07 / 500.16 / 500.17, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Fed SR 26-2 (formerly SR 11-7), NIST AI RMF GOVERN 1.4 / 1.6, and FTC Safeguards Rule 16 CFR §314.4(c). It does not, by itself, *ensure* a passing examination, *guarantee* that every shadow registration has been discovered, or *eliminate* the risk that Microsoft moves an endpoint between v1.0 and beta between releases. Implementation requires that organizations verify endpoint availability, feature-specific support terms, and module pinning at every change window, and reconcile source evidence rather than relying on one surface.

| Field | Value |
|---|---|
| Control ID | 1.2 |
| Pillar | 1 — Security |
| Playbook | PowerShell Setup |
| PowerShell Edition | 7.4 LTS Core (orchestrator); 5.1 Desktop (Power Apps Administration sub-shell, JSON-bridged) |
| Cloud Scope | Commercial |
| Last UI Verified | April 2026 (historical; not re-executed for this review) |
| Companion Playbooks | [`portal-walkthrough.md`](portal-walkthrough.md) · [`verification-testing.md`](verification-testing.md) · [`troubleshooting.md`](troubleshooting.md) · [`sponsorship-lifecycle-workflows.md`](sponsorship-lifecycle-workflows.md) |
| Related Controls | [1.4](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) · [1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) · [1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) · [1.23](../../../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) · [1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) · [2.1](../../../controls/pillar-2-management/2.1-managed-environments.md) · [3.1](../../../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) · [3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) |

---

**Last Verified:** 2026-10-16 (Microsoft Learn documentation review only).

No tenant connections, portal execution, screenshots, module installations, consent changes, or signing-certificate tests were performed for this review. The historical UI date above is not evidence of current tenant parity.

### Documentation verification ledger

| Claim family | Verified basis and implementation boundary |
|---|---|
| Agent Registry / Agent 365 | Current documented navigation is **Agents > All Agents > Registry**. The registry article still labels its API integration preview; the [package API reference](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/api/admin-settings/package/copilotpackages-list) documents `/v1.0/copilot/admin/catalog/packages`, `CopilotPackages.Read.All`, Agent 365 licensing, and pagination. Do not infer feature GA solely from a v1.0 URL. [Registry](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-registry), [licensing](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview#licensing-for-agent-management). |
| Entra Agent ID | The [v1.0 list API](https://learn.microsoft.com/en-us/graph/api/agentidentity-list?view=graph-rest-1.0) uses `/servicePrincipals/microsoft.graph.agentIdentity` and `AgentIdentity.Read.All`, not `/agents`. Retain identity object IDs and blueprint references; an app ID is not a universal agent key. |
| Shells / modules / versions | [Graph supports Windows PowerShell 5.1 with prerequisites and recommends PowerShell 7+](https://learn.microsoft.com/en-us/powershell/microsoftgraph/installation); it is not Core-only. The [Power Apps modules documented here require Windows PowerShell 5.x / .NET Framework](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell). Unsupported-shell behavior is not documented as “silently empty.” Pins below are illustrative historical baselines, not Microsoft minimums or tested current package versions. |
| Authentication / paging / throttling | [Certificate app-only authentication](https://learn.microsoft.com/en-us/powershell/microsoftgraph/authentication-commands) does not use delegated `-Scopes`. Check the bound tenant/client/auth type and execute the required read endpoints. Follow [all next links](https://learn.microsoft.com/en-us/graph/paging); honor [HTTP 429 Retry-After](https://learn.microsoft.com/en-us/graph/throttling). |
| Directory objects / owners / grants / credentials | Read both [applications](https://learn.microsoft.com/en-us/graph/api/application-list?view=graph-rest-1.0) and [service principals](https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list?view=graph-rest-1.0). Owner relationships can return [limited information](https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list-owners?view=graph-rest-1.0); an unresolved owner is not proof of deletion. [Delegated grants](https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list-oauth2permissiongrants?view=graph-rest-1.0) require `Directory.Read.All`; [app-role assignments](https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list-approleassignments?view=graph-rest-1.0) require `Application.Read.All`. Resolve roles against each resource SP, not only Microsoft Graph. [Credential properties](https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0) and [federated credentials](https://learn.microsoft.com/en-us/graph/api/application-list-federatedidentitycredentials?view=graph-rest-1.0) are separate evidence. |
| Consent | Collect the [authorization policy](https://learn.microsoft.com/en-us/graph/api/authorizationpolicy-get?view=graph-rest-1.0), [admin consent request policy](https://learn.microsoft.com/en-us/graph/api/adminconsentrequestpolicy-get?view=graph-rest-1.0), and [request queue](https://learn.microsoft.com/en-us/graph/api/appconsentapprovalroute-list-appconsentrequests?view=graph-rest-1.0) separately. The queue requires `ConsentRequest.Read.All`; an empty queue does not prove the workflow is enabled. |
| Sign-ins / risk / Conditional Access | SP sign-in filtering is documented on the [beta sign-in API](https://learn.microsoft.com/en-us/graph/api/signin-list?view=graph-rest-beta), not the user-focused v1.0 list article. [Risky SPs](https://learn.microsoft.com/en-us/graph/api/identityprotectionroot-list-riskyserviceprincipals?view=graph-rest-1.0) and creation/modification of [traditional workload CA](https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity) require Workload ID Premium. Traditional workload CA targets **SP object IDs**, excludes managed identities and third-party/multitenant SaaS apps, and needs runtime evaluation evidence. [CA for agents](https://learn.microsoft.com/en-us/entra/identity/conditional-access/agent-id) is separate: E7, or Agent 365 with Entra P1/M365 E3; target the actual user, agent identity/blueprint, or agent-user token subject. [Default log retention](https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-reports-data-retention) does not provide a 90-day sign-in history; archive ahead of time. |
| Power Platform / MCP | [Dataverse `bots`](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/reference/bot?view=dataverse-latest) requires an [environment application user and security roles](https://learn.microsoft.com/en-us/power-platform/admin/manage-application-users), not just a directory admin title. [Get-AzAccessToken](https://learn.microsoft.com/en-us/powershell/module/az.accounts/get-azaccesstoken) supports explicit tenant/resource targeting and now returns SecureString tokens by default; do not log tokens. [MCP registration](https://learn.microsoft.com/en-us/entra/agent-id/secure-mcp-server-with-entra-id) can reuse an existing resource application; redirect-URI and tag matches are heuristics, not a complete MCP registry. |
| Evidence / signing | Hashes do not enforce WORM storage or implement the three-person attestation chain. [Authenticode](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-authenticodesignature) requires a supported SIP file type, not arbitrary JSON. Sign a [version-2 Windows catalog](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/new-filecatalog) covering the JSON and exports, then verify signature and catalog contents separately. |

## §0 — Wrong-shell trap and registration-plane false-clean defects (READ FIRST)

**The defining fact of Control 1.2.** The package API now documents a tenant catalog, but it is not a substitute for reconciling the identity and environment planes. An agent may have an Entra application or service principal, a catalog package, a Dataverse bot, an Entra Agent ID, or several of these records. A publisher app may also back multiple agents. Preserve source IDs and relationship evidence rather than equating every app with one business agent.

A script that ignores this reality produces a **false-clean registry** — the worst Control 1.2 outcome. False-clean registries understate identity exposure under NYDFS 500.07 / 500.16, leave ownerless privilege grants undetected (NIST AI RMF GOVERN 1.4), and break the approval-trail evidence FINRA Rule 4511 and SEC 17a-4(b)(4) examiners ask for first.

**Why this section exists.** Five classes of silent failure produce false-clean registry output in Control 1.2 specifically:

1. **Wrong PowerShell edition for the plane being queried.** Use Windows PowerShell 5.1 for the documented Power Apps modules. This playbook chooses PowerShell 7.4+ for orchestration; that choice is not a statement that Graph, Az, or MSCommerce are Core-only.
2. **API-version assumptions.** Verify each endpoint against its current reference. Neither a quarterly migration schedule nor automatic endpoint equivalence is documented. Use the ledger above instead of invented `/agents` or `/admin/microsoft365apps/installedApps` routes.
3. **Granted-permission mismatch.** Missing authorization can produce an error such as `403`; a `200` empty collection is not the documented missing-consent signal. A successful connect alone does not prove collection rights. Keep each endpoint outcome.
4. **Tag heuristics.** Tags are custom strings, not a Microsoft-maintained universal agent taxonomy. Full enumeration followed by local classification reduces tag-filter blind spots but still requires reconciliation with the catalog and environment records.
5. **Single-credential read+write.** Running this harness with the same service principal that *creates* or *modifies* applications breaks SOX 404 separation of duties — the principal that produces the evidence could be the principal that altered the configuration the evidence describes.

**Top false-clean defects unique to registration automation.**

| # | Defect | What it looks like | How this playbook traps it |
|---|---|---|---|
| 1 | `Get-MgApplication -Filter "tags/any(t:t eq 'DeclarativeAgent')"` only | Misses untagged or differently tagged records | §3 enumerates applications and SPs without a tag prefilter; classification remains a separate review |
| 2 | Owner check via `Get-MgApplication` `.Owners` navigation property without expansion | `.Owners` returns empty unless `-ExpandProperty owners` is set; ownerless detection produces false positives | §4 explicit `-ExpandProperty owners` plus secondary `Get-MgApplicationOwner` cross-check |
| 3 | Permission-grant audit on requested API permissions only | Misses actual delegated grants and application-role assignments | §5 walks `Get-MgServicePrincipalOauth2PermissionGrant` and `Get-MgServicePrincipalAppRoleAssignment` |
| 4 | Credential expiry calculated as `EndDateTime - Now` without `KeyId` correlation | Rotation evidence loses provenance; can't tie new credential to retired credential | §6 emits `KeyId`, `Hint`, `CustomKeyIdentifier` for every passwordCredential / keyCredential row |
| 5 | Consent-policy assessment via `Get-MgPolicyAuthorizationPolicy` only | Misses the per-app admin-consent-request policy and reviewer queue size | §7 reads `/policies/adminConsentRequestPolicy` plus reviewer queue via `/identityGovernance/appConsent/appConsentRequests` |
| 6 | SP sign-in audit via `Get-MgAuditLogSignIn` without `-Filter "signInEventTypes/any(t:t eq 'servicePrincipal')"` | Returns user sign-ins; SP risk invisible | §8 explicit SP-only filter and Identity Protection `riskyServicePrincipals` cross-check |
| 7 | Conditional Access for workload identities listed but not validated against the SP set | A policy exists but excludes the SPs that need it | §9 resolves each policy's `conditions.clientApplications.includeServicePrincipals` against the §3 inventory and reports gaps |
| 8 | Treating MCP callback patterns as authoritative | Existing API registrations or non-Entra servers are missed | §11 emits candidates only; reconcile with approved endpoint/tool records |
| 9 | Integrated Apps assumed equal to the Power Platform inventory | Catalog packages with no Power Platform footprint missed | §12 reads the documented package catalog; Exchange `Get-App` is Outlook add-in evidence only |
| 10 | Reconciliation that overwrites the canonical record on every run | History destroyed; deltas invisible to examiners | §13 uses distinct run folders; configure immutable retention separately |
| 11 | Single SP for both registry-read and tenant-write | Breaks SOX 404 separation of duties | §1 separate `agt12-registry-reader` audit-only principal |

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
        Write-Warning "AzureAD legacy module present. Do not use it as a registry fallback; migrate to supported Graph or Entra PowerShell commands (§3.4)."
    }
}

Write-Verbose "Control 1.2 shell guard passed: pwsh $($PSVersionTable.PSVersion)"
```

**Fail-closed conditions enforced by this guard:**

- Detected PowerShell edition is `Desktop` or version `< 7.4.0` → `exit 2`.
- v1 `Microsoft.Graph` discoverable on `$env:PSModulePath` → `exit 2`.
- `AzureAD` / `AzureADPreview` legacy module present → warning; the module is not used.

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
    because the documented modules require Windows PowerShell / .NET Framework.
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

```

Installation is an operator prerequisite, not part of a read-only evidence run. The historical pins above have **not** been installed or compatibility-tested in this review. Approve current versions as a set, record their versions, and run the acceptance cases in §14 before production use. Optional modules not used by the selected collection legs need not be installed. Check `$LASTEXITCODE` after each `powershell.exe` child; a failed install must stop provisioning.

### 1.2 Pinned CLI tooling

| Tool | Minimum | Used for | Notes |
|---|---|---|---|
| Power Platform CLI (`pac`, optional) | Tenant-approved version | Environment-scoped `pac copilot list` | Not called by the examples; see [current reference](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/copilot#pac-copilot-list). No claim that a historical minimum covers current commands. |
| Microsoft Graph PowerShell SDK | 2.25.0 | All §3–§9 / §12 enumeration | `Connect-MgGraph -Environment 'Global'` |
| Azure CLI (`az`) | 2.60.0 | Azure managed identity / federated credential cross-check | `az cloud set --name AzureCloud` |
| `Get-FileHash` (built-in) | n/a | SHA-256 evidence hashes | n/a |
| `New-FileCatalog`, `Set-AuthenticodeSignature` | Windows host | Catalog signing in §13 | Code-signing cert must chain to a CA approved by Information Security |

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
    $results += [pscustomobject]@{ Tool='pac (optional)'; Found=$pacVer; Required='record only'; Pass=$true }
} catch { $results += [pscustomobject]@{ Tool='pac (optional)'; Found='not-installed'; Required='record only'; Pass=$true } }

try {
    $azVer = (& az version --output json 2>$null) | ConvertFrom-Json
    $results += [pscustomobject]@{ Tool='az'; Found=$azVer.'azure-cli'; Required='>=2.60.0'; Pass=([version]$azVer.'azure-cli' -ge [version]'2.60.0') }
} catch { $results += [pscustomobject]@{ Tool='az'; Found='not-installed'; Required='>=2.60.0'; Pass=$false } }

$mg = Get-Module -ListAvailable Microsoft.Graph.Authentication | Sort-Object Version -Descending | Select-Object -First 1
$results += [pscustomobject]@{ Tool='Microsoft.Graph.Authentication'; Found=("$($mg.Version)"); Required='==2.25.0 (example pin)'; Pass=($mg -and $mg.Version -eq [version]'2.25.0') }

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
| same SP | Microsoft Graph | `Directory.Read.All` (Application, already listed) | Read `oauth2PermissionGrants`; §5 | Yes |
| same SP | Microsoft Graph | `Application.Read.All` (Application, already listed) | Read appRoleAssignments granted *to* SPs; §5 | Yes |
| same SP | Microsoft Graph | `Policy.Read.All` (Application) | Read consent policies, CA policies; §7, §9 | Yes |
| same SP | Microsoft Graph | `AuditLog.Read.All` (Application) | Read service principal sign-ins and credential events; §6, §8 | Yes |
| same SP | Microsoft Graph | `IdentityRiskyServicePrincipal.Read.All` (Application) | Identity Protection risky SP detection; §8 | Yes |
| same SP | Microsoft Graph | `ConsentRequest.Read.All` (Application) | Read admin consent requests; §7 | Yes |
| same SP, only if enabled | Microsoft Graph | `AgentIdentity.Read.All` (Application) | Read the Entra Agent ID collection; §3.4 | Yes |
| same SP, only if licensed | Microsoft Graph | `CopilotPackages.Read.All` (Application) | Read package catalog; §12 | Yes |
| Separate remediation operator | Microsoft Graph / Entra | Operation-specific permissions approved separately | No remediation is implemented here. Human PIM activation does not make an app-only credential time-bound. | No |
| `agt12-pp-reader` (SP) | Dataverse, each environment | Application user with security-role read privileges for `bot` and related evidence | Separate environment enumeration and Dataverse authorization; §10 | Verify role privileges; a Power Platform Admin role is not read-only |
| Operator (human) | Entra PIM | Entra Global Reader, time-bound | Manual reconciliation review; never used for the unattended pipeline | Yes |
| Operator (human, mutating) | Entra PIM | Operation-specific Entra role approved separately | No remediation is implemented by these collection examples; review owner/consent write authorization independently | No |

**Hedging note on permission scope.** The registry reader is scoped to read-only application permissions; tenant administrators should still review the consent grants quarterly and rotate the certificate at the cadence defined by your PKI policy. "Read-only" is a contract with Microsoft Graph, not a guarantee that the credential cannot be used for reconnaissance — treat the registry reader as a privileged identity for monitoring and detection purposes, with its sign-ins reported into [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## §2 — Authentication bootstrap

**Why this section exists.** The helpers below produce a single `[Agt12Session]`-shaped object the rest of the playbook consumes, and explicitly **reject** the bootstrap if the bound principal is the same identity used elsewhere for write operations.

### 2.1 `Initialize-Agt12Session`

```powershell
# scripts/Initialize-Agt12Session.ps1
function Initialize-Agt12Session {
<#
.SYNOPSIS
    Connects an approved certificate-based Graph registry reader and verifies context identity.
    Successful authentication does not prove every required application permission is granted.
.DESCRIPTION
    Performs Connect-MgGraph (cert-based) and Connect-AzAccount (cert-based, optional). Defers the
    Power Apps environment enumeration to a separate 5.1 session (§10).
    Validates the bound tenant, client, and app-only authentication type. Refuses to bootstrap if the supplied
    ClientId matches the documented write-principal application id (separation-of-duties enforcement).
.PARAMETER TenantId
.PARAMETER RegistryReaderClientId
    Application (client) id of the audit-only registry reader SP. MUST NOT match any write principal.
.PARAMETER CertificateThumbprint
.PARAMETER WritePrincipalClientIdsToReject
    Optional list of application ids that this script will refuse to bind as the registry reader.
    Populate from your tenant's documented write principals (e.g., the SP used by Control 1.4 for
    DLP edits, or the SP used by Control 2.1 for label propagation).
.OUTPUTS
    [pscustomobject] with MgContext, ConnectedAt, RunId, and commercial-cloud profile.
.EXAMPLE
    PS> $session = Initialize-Agt12Session -TenantId $tid -RegistryReaderClientId $cid -CertificateThumbprint $thumb
.EXAMPLE
    PS> $session = Initialize-Agt12Session -TenantId $tid -RegistryReaderClientId $cid -CertificateThumbprint $thumb -WhatIf
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
        [Parameter()] [guid[]]$WritePrincipalClientIdsToReject = @()
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    if ($RegistryReaderClientId -in $WritePrincipalClientIdsToReject) {
        Write-Error "Refusing to bootstrap: RegistryReaderClientId $RegistryReaderClientId is in the documented write-principal list. SOX 404 separation-of-duties requires a distinct read-only principal for §3-§12. Provision agt12-registry-reader and retry."
        exit 2
    }

    $runId = [guid]::NewGuid().ToString()

    if ($PSCmdlet.ShouldProcess('Microsoft Graph','Connect-MgGraph (certificate)')) {
        try {
            Connect-MgGraph -TenantId $TenantId -ClientId $RegistryReaderClientId `
                -CertificateThumbprint $CertificateThumbprint `
                -Environment 'Global' -ContextScope Process -NoWelcome -ErrorAction Stop | Out-Null
        } catch {
            Write-Error "Connect-MgGraph failed: $($_.Exception.Message). Verify the certificate is installed in Cert:\CurrentUser\My or Cert:\LocalMachine\My, that the SP has the cert credential registered, and that the tenant id matches the SP's home tenant."
            throw
        }
    }
    if ($WhatIfPreference) { return }
    $ctx = Get-MgContext
    if (-not $ctx -or $ctx.TenantId -ne [string]$TenantId -or
        $ctx.ClientId -ne [string]$RegistryReaderClientId -or $ctx.AuthType -ne 'AppOnly') {
        throw 'Graph context does not match the approved app-only registry reader.'
    }

    if ($PSCmdlet.ShouldProcess('AzureCloud','Connect-AzAccount (certificate, optional)')) {
        try {
            Connect-AzAccount -ServicePrincipal -Tenant $TenantId -ApplicationId $RegistryReaderClientId `
                -CertificateThumbprint $CertificateThumbprint `
                -Environment 'AzureCloud' -WarningAction SilentlyContinue | Out-Null
        } catch {
            Write-Warning "Connect-AzAccount failed: $($_.Exception.Message). Azure-side managed-identity / federated-credential cross-checks in §6 will be skipped; primary registry data unaffected."
        }
    }

    [pscustomobject]@{
        RunId        = $runId
        MgContext    = $ctx
        ConnectedAt  = (Get-Date).ToUniversalTime()
        TenantId     = $TenantId
        ClientId     = $RegistryReaderClientId
        Thumbprint   = $CertificateThumbprint
        Profile      = [pscustomobject]@{ Cloud = 'Commercial' }
    }
}
```

**Fail-closed conditions enforced by this section:**

- ClientId matches a documented write-principal id → `exit 2` (separation of duties).
- Cert thumbprint not present in `Cert:\CurrentUser\My` or `Cert:\LocalMachine\My` → throw.
- Az leg failure is **best-effort**; primary registry data is collected from Microsoft Graph and unaffected.

### 2.2 Throttle helper used by every leg

```powershell
function Invoke-Agt12WithThrottle {
<#
.SYNOPSIS
    Invokes a collection operation; Graph SDK requests use the SDK retry handler.
.DESCRIPTION
    Does not assume every module exposes the same exception/response/header shape.
    Errors propagate. Non-SDK REST collectors need their own tested retry policy.
.PARAMETER ScriptBlock
.PARAMETER MaxAttempts
.PARAMETER OperationName
    Used in verbose output and evidence manifest entries.
.OUTPUTS
    Whatever the script block emits.
.EXAMPLE
    PS> Invoke-Agt12WithThrottle -OperationName 'Get-MgApplication' -ScriptBlock { Get-MgApplication -All }
.NOTES
    MaxAttempts is retained for old callers but is not a cross-module retry guarantee.
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

    Write-Verbose "Collecting $OperationName"
    return & $ScriptBlock
}
```

---

## §3 — App registration and service principal inventory (`Get-Agt12AppRegistryInventory`)

**Why this section exists.** Directory evidence supports owner, grant, credential and activity review. Application objects in their home tenant and service principals in consenting tenants have different object IDs; preserve those relationships. Enumerating only one collection omits evidence, but enumerating both still does not identify every business agent or establish a universal one-app/two-object model.

```powershell
# scripts/legs/Get-Agt12AppRegistryInventory.ps1
function Get-Agt12AppRegistryInventory {
<#
.SYNOPSIS
    Enumerates every Entra application and service principal that could be an agent registration.
.DESCRIPTION
    Enumerates applications and service principals without a tag prefilter. Returns separate
    source rows; AppId is a relationship hint, not a unique business-agent key.
.PARAMETER Session
.PARAMETER IncludeAllSps
    Retained for callers of the earlier example. All service principals are now enumerated
    regardless of this switch, so untagged records are not omitted.
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $reg = Get-Agt12AppRegistryInventory -Session $session
.EXAMPLE
    PS> $reg = Get-Agt12AppRegistryInventory -Session $session -IncludeAllSps -Verbose
.NOTES
    Custom tags are classification hints only. A full directory inventory includes non-agents.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter()] [switch]$IncludeAllSps
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $accum = New-Object System.Collections.Generic.List[pscustomobject]
    $seenAppIds = New-Object System.Collections.Generic.HashSet[string]

    # 1) Application objects (home-tenant registrations)
    foreach ($tag in @('full-directory-enumeration')) {
        try {
            $apps = Invoke-Agt12WithThrottle -OperationName "Graph:Application[$tag]" -ScriptBlock {
                Get-MgApplication -Property 'id,appId,displayName,publisherDomain,verifiedPublisher,signInAudience,createdDateTime,tags,identifierUris' -ExpandProperty 'owners' -All -ErrorAction Stop
            }
        } catch {
            throw
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
                VerifiedPublisher  = if ($a.VerifiedPublisher) { $a.VerifiedPublisher.DisplayName } else { $null }
                SignInAudience     = $a.SignInAudience
                CreatedDateTime    = $a.CreatedDateTime
                Tags               = ($a.Tags -join ';')
                IdentifierUris     = ($a.IdentifierUris -join ';')
                ReplyUrls          = ''
                OwnerCount         = $ownerCount
                OwnerObjectIds     = (@($a.Owners | ForEach-Object { $_.Id }) -join ';')
                Notes              = ''
                CollectedAt        = (Get-Date).ToUniversalTime()
            })
        }
    }

    # 2) Service principals (consented in this tenant — agents from publishers, MCP servers, etc.)
    foreach ($tag in @('full-directory-enumeration')) {
        try {
            $sps = Invoke-Agt12WithThrottle -OperationName "Graph:ServicePrincipal[$tag]" -ScriptBlock {
                Get-MgServicePrincipal -Property 'id,appId,displayName,publisherName,verifiedPublisher,signInAudience,appOwnerOrganizationId,servicePrincipalType,accountEnabled,replyUrls,tags' -All -ErrorAction Stop
            }
        } catch {
            throw
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
                VerifiedPublisher  = if ($sp.VerifiedPublisher) { $sp.VerifiedPublisher.DisplayName } else { $null }
                SignInAudience     = $sp.SignInAudience
                AppOwnerOrganizationId = $sp.AppOwnerOrganizationId
                ServicePrincipalType = $sp.ServicePrincipalType
                AccountEnabled     = $sp.AccountEnabled
                ReplyUrls          = ($sp.ReplyUrls -join ';')
                IdentifierUris     = ''
                Tags               = ($sp.Tags -join ';')
                Notes              = ''
                CollectedAt        = (Get-Date).ToUniversalTime()
            })
        }
    }

    # IncludeAllSps is retained for existing callers; the primary SP read already enumerates all.

    Write-Verbose "AppRegistry leg returned $($accum.Count) records ($(@($accum | Where-Object Plane -eq 'AppRegistration').Count) Apps, $(@($accum | Where-Object Plane -eq 'ServicePrincipal').Count) SPs)"
    return $accum.ToArray()
}
```

### 3.4 Supported identity-specific collection; no AzureAD fallback

[AzureAD is deprecated](https://learn.microsoft.com/en-us/powershell/azure/active-directory/overview); do not install it as a recovery path. If a supported API is unavailable, record the missing plane and obtain manual evidence rather than reporting a clean run.

The Entra Agent ID list is separate from custom tags. When authorized, request `GET https://graph.microsoft.com/v1.0/servicePrincipals/microsoft.graph.agentIdentity` with `AgentIdentity.Read.All` and follow every `@odata.nextLink`. Retain each `id`, `agentIdentityBlueprintId`, and source type without collapsing identities sharing a blueprint. See the [current API reference](https://learn.microsoft.com/en-us/graph/api/agentidentity-list?view=graph-rest-1.0). This additional collection is not implemented by the generic application/SP helper; attach its raw export separately.

**Collection boundary:** primary application/SP enumeration errors throw. Optional tag observations are not authoritative discovery. A successful directory enumeration includes ordinary applications as well as agent candidates; human classification and reconciliation remain required.

---
## §4 — Owner audit & ownerless agent remediation (`Get-Agt12OwnershipAudit`)

**Why this section exists.** The parent control requires an Agent Owner for every registration and a Backup Owner for Zone 2 / Zone 3. The default two-human-owner check below is a local review threshold, not a universal Microsoft requirement. Directory ownership does not establish sponsor accountability or employment status. A limited-information owner or lookup error must not be labeled deleted; resolve its object type and personnel status separately.

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
        } catch { throw "Owner $uid could not be resolved as a user. Classify its object type and access outcome before attestation: $($_.Exception.Message)" }
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
            throw
        }

        $resolved = @(foreach ($o in $owners) {
            $u = Resolve-User $o.Id
            if ($u) {
                [pscustomobject]@{
                    OwnerId=$u.Id; Upn=$u.UserPrincipalName; DisplayName=$u.DisplayName;
                    Enabled=$u.AccountEnabled; Kind='User'
                }
            } else {
                [pscustomobject]@{
                    OwnerId=$o.Id; Upn=$null; DisplayName=$null; Enabled=$false; Kind='Unresolved'
                }
            }
        })

        $active = @($resolved | Where-Object { $_.Kind -eq 'User' -and $_.Enabled })
        $tombstoned = @($resolved | Where-Object { $_.Kind -eq 'User' -and -not $_.Enabled })
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
            ActiveOwners    = (($active | ForEach-Object Upn) -join ';')
            TombstonedOwnerIds = (($tombstoned | ForEach-Object OwnerId) -join ';')
            ProposedReplacementUpn = $proposed
            CollectedAt     = (Get-Date).ToUniversalTime()
        })
    }

    Write-Verbose "Ownership audit: $(@($rows | Where-Object Posture -eq 'Compliant').Count) compliant, $(@($rows | Where-Object Posture -eq 'Singleton').Count) singleton, $(@($rows | Where-Object Posture -eq 'Ownerless').Count) ownerless, $(@($rows | Where-Object Posture -eq 'TombstonedOwner').Count) disabled-owner findings."
    return $rows.ToArray()
}
```

**Collection boundary:** owner enumeration and user-resolution errors stop this example. Nonhuman owners require a separate classification and cannot be counted as named human owners. `TombstonedOwner` / `TombstonedOwnerIds` are historical output labels for **disabled resolved users**, not evidence that the objects are deleted. Manager proposals are advisory and do not replace sponsor review.

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
    resource service principal's role value (e.g., 'Mail.ReadWrite' rather than a GUID). Flags any grant
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

    $resourceRoleMaps = @{}

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
            throw
        }
        # Application
        try {
            $appAssn = Invoke-Agt12WithThrottle -OperationName "Graph:AppRoleAssn[$($a.AppId)]" -ScriptBlock {
                Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $a.ObjectId -All -ErrorAction Stop
            }
            foreach ($r in $appAssn) {
                if (-not $resourceRoleMaps.ContainsKey($r.ResourceId)) {
                    $resource = Get-MgServicePrincipal -ServicePrincipalId $r.ResourceId -Property 'id,appRoles' -ErrorAction Stop
                    $resourceRoleMaps[$r.ResourceId] = @{}
                    foreach ($role in $resource.AppRoles) {
                        $resourceRoleMaps[$r.ResourceId][[string]$role.Id] = $role.Value
                    }
                }
                $roleMap = $resourceRoleMaps[$r.ResourceId]
                $name = if ($roleMap.ContainsKey([string]$r.AppRoleId)) { $roleMap[[string]$r.AppRoleId] } else { "<unmapped:$($r.AppRoleId)>" }
                $isOver = $name -in $OverPermissionedScopes
                $rows.Add([pscustomobject]@{
                    AppId=$a.AppId; ObjectId=$a.ObjectId; DisplayName=$a.DisplayName;
                    GrantKind='Application'; ResourceDisplayName=$r.ResourceDisplayName;
                    ResourceId=$r.ResourceId; AppRoleId=$r.AppRoleId; AppRoleValue=$name;
                    OverPermissioned=$isOver; OverPermissionedReason= ($(if ($isOver) { $name } else { '' }));
                    CollectedAt=(Get-Date).ToUniversalTime()
                })
            }
        } catch {
            throw
        }
    }

    Write-Verbose "Permission audit: $($rows.Count) grants captured, $(@($rows | Where-Object OverPermissioned).Count) flagged by local triage."
    return $rows.ToArray()
}
```

**Collection boundary:** unmapped app-role IDs remain review findings, never a least-privilege PASS. Failed grant/resource reads throw. The fixed risk list is a local triage aid; it does not implement wildcard detection, contextual least privilege, or inherited Entra Agent ID permissions. Collect inherited grants separately for Agent ID identities and blueprints.

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
            throw
        }

        function Classify([datetime]$end) {
            if ($end -lt $now) { return @('Expired',-1*([int]($now - $end).TotalDays),'RotateImmediately') }
            $d = [int][Math]::Floor(($end - $now).TotalDays)
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
                KeyId=$k.KeyId; CustomKeyIdentifier=$k.CustomKeyIdentifier; Usage=$k.Usage; Type=$k.Type;
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
            throw
        }
    }

    Write-Verbose "Credential hygiene: $(@($rows | Where-Object { $_.PSObject.Properties['ExpiryBucket'] -and $_.ExpiryBucket -eq 'Expired' }).Count) expired, $(@($rows | Where-Object { $_.PSObject.Properties['ExpiryBucket'] -and $_.ExpiryBucket -eq 'LT30' }).Count) <30d."
    return $rows.ToArray()
}
```

**Collection boundary:** failed credential reads throw. No credentials or no federated credentials is not automatically a defect (managed identities use different credential management). The example inspects home-tenant application credentials, not every SP credential or Azure managed identity. Expiry buckets and migration preferences are local policy; they do not prove rotation history or current usage.

---
## §7 — App consent governance (`Get-Agt12ConsentPosture`)

**Why this section exists.** Collect the user-consent authorization policy, admin consent request policy, and request queue independently. Recent approvals and grant changes require separate audit-log evidence; this helper does not collect a quarter of consent history.

```powershell
# scripts/legs/Get-Agt12ConsentPosture.ps1
function Get-Agt12ConsentPosture {
<#
.SYNOPSIS
    Captures user consent policy, admin consent workflow configuration, and request queue.
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
    } catch { throw }

    $requestPolicy = Get-MgPolicyAdminConsentRequestPolicy -ErrorAction Stop
    $rows.Add([pscustomobject]@{
        Kind='AdminConsentRequestPolicy'; IsEnabled=$requestPolicy.IsEnabled;
        Reviewers=($requestPolicy.Reviewers | ConvertTo-Json -Depth 8 -Compress);
        CollectedAt=$now
    })

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
    } catch { throw }

    Write-Verbose "Consent posture: $($rows.Count) records."
    return $rows.ToArray()
}
```

**Collection boundary:** failed policy/queue reads throw. `IsEnabled = false` is a workflow finding even when the queue is empty. Review the assigned permission-grant policies before interpreting user-consent posture; the policy identifier list is not a Boolean “allow consent” switch. Approvals are never auto-applied.

---

## §8 — Service principal sign-in audit (`Get-Agt12ServicePrincipalSignIns`)

**Why this section exists.** SP sign-in records support activity and access review within their actual retention window. They do not independently establish 90-day dormancy, data residency, or effective CA enforcement. The documented beta filter is `signInEventTypes/any(t:t eq 'servicePrincipal')`; validate returned event types and known events rather than assuming malformed filters have a predictable failure mode.

```powershell
# scripts/legs/Get-Agt12ServicePrincipalSignIns.ps1
function Get-Agt12ServicePrincipalSignIns {
<#
.SYNOPSIS
    Captures SP-only sign-in events and Identity Protection risky-SP records.
.PARAMETER Session
.PARAMETER LookbackDays
    Default 30. A larger value does not extend the service's retention window.
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $signins = Get-Agt12ServicePrincipalSignIns -Session $session -LookbackDays 7
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
            Get-MgBetaAuditLogSignIn -Filter "signInEventTypes/any(t:t eq 'servicePrincipal') and createdDateTime ge $since" -All -ErrorAction Stop
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
    } catch { throw }

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
    } catch { throw }

    Write-Verbose "SP sign-in audit: $(@($rows | Where-Object Kind -eq 'SPSignIn').Count) sign-ins, $(@($rows | Where-Object Kind -eq 'RiskyServicePrincipal').Count) risky SPs."
    return $rows.ToArray()
}
```

**Collection boundary:** the SP filter uses the documented beta example and therefore needs preview acceptance; beta APIs are not supported for production applications. Use separately retained service-principal sign-in logs for production evidence if beta is not approved. Ordinary sign-in retention is seven days for Free and 30 days for P1/P2; requesting 90 days does not recover expired logs. Record the actual available interval and a known-event positive control. Zero events means **no observed sign-ins in that interval**, not proven dormancy, zero risk, or a successful security control.

---

## §9 — Conditional Access for workload identities (`Test-Agt12WorkloadIdentityCAPolicy`)

**Why this section exists.** User-targeted CA does not establish workload-identity protection. This leg collects configured policies for manual review; it does **not** calculate effective coverage. Workload CA uses **service-principal object IDs**, not app/client IDs. Review state, exclusions, resource scope, conditions, and evaluated sign-in results. Traditional workload CA does not cover managed identities or third-party/multitenant SaaS applications; evaluate Entra Agent ID controls separately.

```powershell
# scripts/legs/Test-Agt12WorkloadIdentityCAPolicy.ps1
function Test-Agt12WorkloadIdentityCAPolicy {
<#
.SYNOPSIS
    Lists CA policies that target service principals for manual effective-coverage review.
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
        throw
    }

    $wiPolicies = $policies | Where-Object {
        $_.Conditions.ClientApplications -and
        ($_.Conditions.ClientApplications.IncludeServicePrincipals -or $_.Conditions.ClientApplications.ExcludeServicePrincipals)
    }
    foreach ($p in $wiPolicies) {
        $rows.Add([pscustomobject]@{
            Kind='WorkloadIdentityCAPolicy'; PolicyId=$p.Id; DisplayName=$p.DisplayName;
            State=$p.State; IncludeSPs=($p.Conditions.ClientApplications.IncludeServicePrincipals -join ';');
            ExcludeSPs=($p.Conditions.ClientApplications.ExcludeServicePrincipals -join ';');
            GrantControls=($p.GrantControls.BuiltInControls -join ';');
            CollectedAt=(Get-Date).ToUniversalTime()
        })
    }

    foreach ($a in ($Inventory | Where-Object { $_.Plane -eq 'ServicePrincipal' -and $_.Status -eq 'OK' })) {
        $rows.Add([pscustomobject]@{
            Kind='AgentCAReviewRequired'; AppId=$a.AppId; ObjectId=$a.ObjectId;
            DisplayName=$a.DisplayName; EffectiveCoverage='Unknown';
            Recommendation='Review eligibility, enabled policy, object-ID targeting, exclusions, conditions, and sign-in evaluation';
            CollectedAt=(Get-Date).ToUniversalTime()
        })
    }

    Write-Verbose "CA collection completed; effective coverage requires manual review."
    return $rows.ToArray()
}
```

**Collection boundary:** every SP receives `EffectiveCoverage='Unknown'` until the review and evaluation evidence are attached. An enabled policy is not sufficient proof; disabled, report-only, excluded, unsupported, or conditionally unmatched cases must not become “covered.” Workload ID Premium is required to create/modify workload CA; existing policies can continue functioning when that license is absent. A failed read is not itself proof of a licensing problem.

---

## §10 — Power Platform agent registration audit (`Get-Agt12PowerPlatformAgents`)

**Why this section exists.** Copilot Studio bots register as Dataverse `bot` rows per environment; a guessed `Get-AdminPowerApp` app-type filter is not authoritative. This leg accepts a separately collected, normalized environment list and queries Dataverse. An unavailable Dataverse-linked environment emits `ManualEvidenceRequired`; a human acceptance gate must review replacement evidence before signing the cycle.

```powershell
# scripts/legs/Get-Agt12PowerPlatformAgents.ps1
function Get-Agt12PowerPlatformAgents {
<#
.SYNOPSIS
    Enumerates Copilot Studio bots from Dataverse `bot` table across all Power Platform environments.
.PARAMETER Session
.PARAMETER TenantId
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $pp = Get-Agt12PowerPlatformAgents -Session $session -TenantId $tid -Environments $envs
.NOTES
    Requires an environment list exported from the authenticated Windows PowerShell 5.1
    Power Apps session and a separately authenticated Az context for the intended Dataverse
    application user. Directory admin roles do not grant Dataverse table read privileges.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [guid]$TenantId,
        [Parameter(Mandatory)] [object[]]$Environments
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $rows = New-Object System.Collections.Generic.List[pscustomobject]
    $envs = @($Environments)
    if ($envs.Count -eq 0) { throw 'Environment discovery is empty; reconcile the expected environment scope before continuing.' }

    foreach ($env in $envs) {
        $envId = $env.EnvironmentName
        $linkedType = if ($env.DataverseExpected) { 'Dataverse' } else { 'None' }
        $orgUrl = [string]$env.DataverseUrl
        $orgUrl = $orgUrl.TrimEnd('/')

        if ([string]::IsNullOrWhiteSpace($orgUrl)) {
            $rows.Add([pscustomobject]@{
                Kind                  = 'PowerPlatformAgentDataverseBot'
                EnvironmentName       = $envId
                DisplayName           = $env.DisplayName
                LinkedEnvironmentType = $linkedType
                Status                = if ($linkedType -in @('Dataverse','CommonDataService')) { 'ManualEvidenceRequired' } else { 'NoDataverse' }
                BotId                 = $null
                Name                  = $null
                OwnerId               = $null
                EvidenceHint          = 'Capture Copilot Studio Agents portal export + incident note for missing Dataverse URL'
                CollectedAt           = (Get-Date).ToUniversalTime()
            })
            continue
        }

        try {
            $tokenObj = Get-AzAccessToken -ResourceUrl $orgUrl -TenantId $TenantId -ErrorAction Stop
            $token = if ($tokenObj.Token -is [securestring]) { $tokenObj.Token | ConvertFrom-SecureString -AsPlainText } else { $tokenObj.Token }
            if ([string]::IsNullOrWhiteSpace($token)) { throw 'Empty Dataverse token' }

            $headers = @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' }
            $next = "$orgUrl/api/data/v9.2/bots?`$select=botid,name,statecode,statuscode,createdon,modifiedon,schemaname,_ownerid_value"
            while ($next) {
                $resp = Invoke-RestMethod -Method GET -Uri $next -Headers $headers -ErrorAction Stop
                foreach ($b in @($resp.value)) {
                    $rows.Add([pscustomobject]@{
                        Kind                  = 'PowerPlatformAgentDataverseBot'
                        EnvironmentName       = $envId
                        DisplayName           = $env.DisplayName
                        LinkedEnvironmentType = $linkedType
                        Status                = 'Collected'
                        BotId                 = $b.botid
                        Name                  = $b.name
                        OwnerId               = $b.'_ownerid_value'
                        StateCode             = $b.statecode
                        StatusCode            = $b.statuscode
                        SchemaName            = $b.schemaname
                        CreatedOn             = $b.createdon
                        ModifiedOn            = $b.modifiedon
                        CollectedAt           = (Get-Date).ToUniversalTime()
                    })
                }
                $next = if ($resp.PSObject.Properties['@odata.nextLink']) { $resp.'@odata.nextLink' } else { $null }
            }
        } catch {
            $rows.Add([pscustomobject]@{
                Kind                  = 'PowerPlatformAgentDataverseBot'
                EnvironmentName       = $envId
                DisplayName           = $env.DisplayName
                LinkedEnvironmentType = $linkedType
                Status                = 'ManualEvidenceRequired'
                BotId                 = $null
                Name                  = $null
                OwnerId               = $null
                EvidenceHint          = "Dataverse bot query failed: $($_.Exception.Message)"
                CollectedAt           = (Get-Date).ToUniversalTime()
            })
        }
    }

    return $rows.ToArray()
}
```

**Environment bridge:** in an authenticated **Windows PowerShell 5.1** session, export `Get-AdminPowerAppEnvironment` to JSON (`ConvertTo-Json -Depth 20`). Review the actual returned environment metadata, then map it to objects with `EnvironmentName`, `DisplayName`, `DataverseUrl` (organization URL or empty string), and `DataverseExpected` (Boolean). These four input fields are a **local adapter contract**, not a claimed native cmdlet response shape. Read the normalized JSON into `$envs` in PowerShell 7 and pass `-Environments $envs`. Preserve the source environment count and query outcome, including environments returning zero bots. Provision an application user with approved read privileges in each Dataverse environment; an Az token alone does not establish table access.

**Collection boundary:** any Dataverse-linked environment that cannot be queried produces `ManualEvidenceRequired`; this example does not automatically validate the replacement evidence. Reconcile environment scope and Dataverse privileges before signing the cycle.

---

## §11 — MCP server enumeration (`Get-Agt12McpServerRegistrations`)

**Why this section exists.** This helper is a **candidate heuristic**, not authoritative MCP enumeration. An MCP server can reuse an existing protected API registration and need not use a characteristic callback URI or tag. Match approved resource endpoints, application ID URIs, tool catalogs, and owner attestations against these candidates. No pattern match does not mean no MCP servers.

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
        $uris = @($a.ReplyUrls -split ';') + @($a.IdentifierUris -split ';')
        $byUri = $uris | Where-Object { $u = $_.ToLowerInvariant(); $patterns | Where-Object { $u.Contains($_) } }
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

**Collection boundary:** matches retain their source for human acceptance or rejection. Both false positives and false negatives are expected. Application ID URIs are included, but neither they nor callback patterns prove the registered resource is an MCP server.

---

## §12 — Integrated Apps enumeration (`Get-Agt12IntegratedApps`)

**Why this section exists.** Use the documented **Agent and app Package Management API** for tenant catalog packages, with `CopilotPackages.Read.All` and Agent 365 licensing. The current registry guide calls this integration preview even though the package reference provides a v1.0 route; verify support terms before relying on it. If unavailable, capture **Agents > All Agents > Registry > Export** and the applicable **Settings > Integrated apps** views. [Exchange `Get-App -OrganizationApp`](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-app?view=exchange-ps) enumerates organizational Outlook add-ins only; it is not an equivalent fallback for Teams, declarative agents, or the complete registry.

```powershell
# scripts/legs/Get-Agt12IntegratedApps.ps1
function Get-Agt12IntegratedApps {
<#
.SYNOPSIS
    Enumerates catalog packages through the documented package-management endpoint.
.PARAMETER Session
.OUTPUTS
    [pscustomobject[]]
.EXAMPLE
    PS> $ia = Get-Agt12IntegratedApps -Session $session
.NOTES
    Requires CopilotPackages.Read.All and an Agent 365 license. An unavailable route is a
    collection failure requiring manual registry evidence, not a clean empty catalog.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject[]])]
    param([Parameter(Mandatory)] [pscustomobject]$Session)
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $rows = New-Object System.Collections.Generic.List[pscustomobject]
    $next = 'https://graph.microsoft.com/v1.0/copilot/admin/catalog/packages'
    while ($next) {
        $apps = Invoke-Agt12WithThrottle -OperationName 'Graph:CatalogPackages' -ScriptBlock {
            Invoke-MgGraphRequest -Method GET -Uri $next -OutputType Hashtable -ErrorAction Stop
        }
        foreach ($a in $apps.value) {
            $rows.Add([pscustomobject]@{
                Kind='IntegratedApp'; Source='CopilotPackageCatalog'; Id=$a.id; DisplayName=$a.displayName;
                AppId=$a.appId; ManifestId=$a.manifestId; Publisher=$a.publisher;
                ElementTypes=($a.elementTypes -join ';'); IsBlocked=$a.isBlocked;
                AvailableTo=$a.availableTo; DeployedTo=$a.deployedTo;
                CollectedAt=(Get-Date).ToUniversalTime()
            })
        }
        $next = $apps['@odata.nextLink']
    }

    Write-Verbose "Integrated Apps enumeration: $($rows.Count) records."
    return $rows.ToArray()
}
```

**Collection boundary:** follow the opaque next link until absent, even after an empty page. Failure throws; retain the failed plane and use an independently reviewed manual export. Package IDs, manifest IDs, and Entra app IDs are different identifiers. Keep duplicate-looking publisher/lifecycle rows until their relationships are established; do not deduplicate by display name.

---
## §13 — Reconciliation into Control 3.1 canonical schema and quarterly attestation pack

**Why this section exists.** Control 3.1 (Agent Inventory) remains the system-of-record reconciliation target. This example exports raw per-leg CSV/JSONL and a **directory-app grouping projection**, not a completed Control 3.1 merge, an Excel workbook, a WORM store, or a three-person attestation. Preserve raw package, bot, and Agent ID records even when no app ID can be mapped. Validate the local adapter against [Control 3.1](../3.1/powershell-setup.md); grouping by AppId alone cannot distinguish every business agent.

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
    Organization-approved Authenticode HTTP timestamp service.
.OUTPUTS
    [pscustomobject] with PackPath, ManifestPath, SignaturePath, RowCount.
.EXAMPLE
    PS> Export-Agt12AttestationPack -Session $s -Inventory $i -Ownership $o -Permissions $p -Credentials $c -Consent $cs -SignIns $si -CACoverage $ca -PowerPlatform $pp -McpServers $m -IntegratedApps $ia -OutputRoot 'C:\evidence' -SigningCertThumbprint $thumb -TimestampServer $approvedTimestampUrl
.NOTES
    Catalog signature, timestamp, and contents must verify. A local adapter and evidence review
    are still required before Control 3.1 accepts the output.
#>
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session,
        [Parameter(Mandatory)] [pscustomobject[]]$Inventory,
        [Parameter(Mandatory)] [pscustomobject[]]$Ownership,
        [Parameter(Mandatory)] [AllowEmptyCollection()] [pscustomobject[]]$Permissions,
        [Parameter(Mandatory)] [AllowEmptyCollection()] [pscustomobject[]]$Credentials,
        [Parameter(Mandatory)] [pscustomobject[]]$Consent,
        [Parameter(Mandatory)] [AllowEmptyCollection()] [pscustomobject[]]$SignIns,
        [Parameter(Mandatory)] [pscustomobject[]]$CACoverage,
        [Parameter()] [pscustomobject[]]$PowerPlatform = @(),
        [Parameter()] [pscustomobject[]]$McpServers = @(),
        [Parameter()] [pscustomobject[]]$IntegratedApps = @(),
        [Parameter(Mandatory)] [string]$OutputRoot,
        [Parameter(Mandatory)] [string]$SigningCertThumbprint,
        [Parameter(Mandatory)] [string]$TimestampServer
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    if (-not $IsWindows) { throw 'Catalog creation and Authenticode signing require Windows.' }
    if ($TimestampServer -notmatch '^http://') { throw 'Use an approved HTTP Authenticode timestamp endpoint; HTTPS can leave the file signed without a timestamp.' }
    $sig = $null
    $packDir = Join-Path $OutputRoot "agt12-attestation-$($Session.Profile.Cloud)-$stamp-$($Session.RunId)"
    if ($PSCmdlet.ShouldProcess($packDir,'Create attestation pack directory')) {
        New-Item -Path $packDir -ItemType Directory -ErrorAction Stop | Out-Null
    }
    if ($WhatIfPreference) { return }

    # Local application grouping only; a separate Control 3.1 identity adapter is required.
    $canon = New-Object System.Collections.Generic.List[pscustomobject]
    $appsOnly = $Inventory | Where-Object { $_.Plane -in 'AppRegistration','ServicePrincipal' -and $_.Status -eq 'OK' } |
        Group-Object AppId
    foreach ($g in $appsOnly) {
        $appId = $g.Name
        $primary = $g.Group | Sort-Object Plane -Descending | Select-Object -First 1
        $own = $Ownership | Where-Object AppId -eq $appId | Select-Object -First 1
        $permCount = @($Permissions | Where-Object AppId -eq $appId).Count
        $overPerm = @($Permissions | Where-Object { $_.AppId -eq $appId -and $_.OverPermissioned }).Count
        $expCred = @($Credentials | Where-Object { $_.AppId -eq $appId -and $_.PSObject.Properties['ExpiryBucket'] -and $_.ExpiryBucket -in 'Expired','LT30' }).Count
        $signinCount = @($SignIns | Where-Object { $_.Kind -eq 'SPSignIn' -and $_.AppId -eq $appId }).Count
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
            DormancyAssessment = 'ManualReviewRequired'
            ConditionalAccessAssessment = 'Unknown'
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
        ToolVersion='v1.6.2'; FileCount=@($manifest).Count; Files=$manifest
    }
    if ($PSCmdlet.ShouldProcess($manifestPath,'Write manifest')) {
        $manifestObj | ConvertTo-Json -Depth 8 | Set-Content -Path $manifestPath -Encoding UTF8
    }

    # Sign a supported catalog covering the exports and the JSON manifest.
    $cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Where-Object Thumbprint -eq $SigningCertThumbprint | Select-Object -First 1
    if (-not $cert) { throw "Signing cert with thumbprint $SigningCertThumbprint not found in Cert:\CurrentUser\My (CodeSigning EKU required)." }
    $catalogPath = Join-Path $OutputRoot "$(Split-Path $packDir -Leaf).cat"
    if ($PSCmdlet.ShouldProcess($catalogPath,'Create, sign, and verify evidence catalog')) {
        New-FileCatalog -Path $packDir -CatalogFilePath $catalogPath -CatalogVersion 2 -ErrorAction Stop | Out-Null
        Set-AuthenticodeSignature -FilePath $catalogPath -Certificate $cert -TimestampServer $TimestampServer -HashAlgorithm SHA256 -ErrorAction Stop | Out-Null
        $sig = Get-AuthenticodeSignature -FilePath $catalogPath
        if ($sig.Status -ne 'Valid' -or -not $sig.TimeStamperCertificate) { throw 'Catalog signature or timestamp verification failed.' }
        if ((Test-FileCatalog -Path $packDir -CatalogFilePath $catalogPath) -ne 'Valid') { throw 'Catalog content verification failed.' }
    }

    [pscustomobject]@{
        PackPath      = $packDir
        ManifestPath  = $manifestPath
        SignaturePath = $catalogPath
        SignatureStatus = if ($sig) { $sig.Status } else { 'WhatIf' }
        RowCount      = $canon.Count
        FileCount     = $files.Count
    }
}
```

**Evidence boundary:** a valid catalog signature, timestamp, and matching file catalog are required for this export path. Keep the `.cat` beside the pack, not inside the hashed folder. Validate again after transfer. A signature proves neither source completeness nor immutability of the destination. Empty leg arrays are skipped in this example, so attach a separate per-plane status ledger recording **Collected (including zero), Failed, NotApplicable, or ManualEvidenceRequired**, expected scope, actual interval, and reviewer acceptance. Do not sign a cycle with unresolved required evidence. Raw JSONL retains heterogeneous fields that a first-object-shaped CSV can omit.

---

## §14 — End-to-end validation, anti-patterns, and operating cadence

### 14.1 `Test-Agt12Implementation`

```powershell
# scripts/Test-Agt12Implementation.ps1
function Test-Agt12Implementation {
<#
.SYNOPSIS
    Collects directory evidence for review without declaring control PASS or signing a cycle.
.PARAMETER Session
.OUTPUTS
    [pscustomobject] with collection outcomes; not a verification result.
.EXAMPLE
    PS> Test-Agt12Implementation -Session $session
.NOTES
    Run after every dependency upgrade and every quarter before the attestation pack is signed.
#>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [pscustomobject]$Session
    )
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    $checks = [ordered]@{}
    $inv = Get-Agt12AppRegistryInventory -Session $Session
    $checks['Inventory'] = "Collected: $(@($inv).Count); reconcile expected scope"
    $own = Get-Agt12OwnershipAudit -Session $Session -Inventory $inv
    $checks['Ownership'] = "Collected: $(@($own).Count); review findings"
    $perm = Get-Agt12PermissionGrantAudit -Session $Session -Inventory $inv
    $checks['Permissions'] = "Collected: $(@($perm).Count); review findings"
    $cred = Get-Agt12CredentialHygiene -Session $Session -Inventory $inv
    $checks['Credentials'] = "Collected: $(@($cred).Count); review findings"
    $cons = Get-Agt12ConsentPosture -Session $Session
    $checks['Consent'] = "Collected: $(@($cons).Count); review workflow and queue"
    $si = Get-Agt12ServicePrincipalSignIns -Session $Session -LookbackDays 7
    $checks['SignIns'] = "Collected: $(@($si).Count); validate retention and known event"
    $ca = Test-Agt12WorkloadIdentityCAPolicy -Session $Session -Inventory $inv
    $checks['CACoverage'] = 'ManualReviewRequired'
    $mcp = Get-Agt12McpServerRegistrations -Session $Session -Inventory $inv
    $checks['MCP'] = "Candidates: $(@($mcp).Count); reconcile approved endpoints"
    $ia = Get-Agt12IntegratedApps -Session $Session
    $checks['IntegratedApps'] = "Collected: $(@($ia).Count); reconcile publisher/lifecycle records"
    $checks['PowerPlatform'] = 'Separate environment collection required (§10)'
    $checks['AgentID'] = 'Separate identity export required (§3.4)'
    $checks['PackExport'] = 'NotRun; per-plane ledger and human review required'

    [pscustomobject]@{
        RunId=$Session.RunId; Cloud=$Session.Profile.Cloud; Checks=$checks;
        Inventory=$inv; Ownership=$own; Permissions=$perm; Credentials=$cred;
        Consent=$cons; SignIns=$si; CACoverage=$ca; McpServers=$mcp; IntegratedApps=$ia
    }
}
```

### 14.2 Anti-patterns to refuse in code review

| # | Anti-pattern | Why it is rejected | Correct approach |
|---|---|---|---|
| 1 | Hard-coding a tenant-specific URI in Connect-MgGraph instead of `-Environment 'Global'` | Breaks reproducibility and makes the runbook non-portable | Always use `-Environment 'Global'` for commercial tenants |
| 2 | Treating an unexpanded/limited owner relationship as proof of no owners | Missing fields become false ownership findings | Enumerate `/owners` with pagination; resolve object type and access outcome separately |
| 3 | Filtering sign-ins by UPN containing `svc_` or `app_` | Hostname / pretty-name heuristics miss SPs without convention; capture user sign-ins | Use `signInEventTypes/any(t:t eq 'servicePrincipal')` exclusively |
| 4 | Using AzureAD as a fallback | Deprecated module is not a supported recovery strategy | Supported Graph / Entra PowerShell or documented manual evidence (§3.4) |
| 5 | Auto-applying owner reassignment from manager-hierarchy proposals | SOX 404 SoD: bulk identity changes require human approval | Emit-and-route to PIM-activated writer with `-WhatIf` first |
| 6 | Treating tags as a universal taxonomy | Custom strings miss untagged agents | Full directory enumeration plus catalog/environment reconciliation |
| 7 | Treating empty or failed catalog response as "no agents" | Missing license/permissions or incomplete paging can hide records | Retain collection outcomes and manual registry export; Outlook add-ins are not an equivalent fallback |
| 8 | Using the same SP for read and write operations | Defeats SoD; one compromised credential becomes both audit and remediation | Separate reader and approved writer; human PIM does not time-bound an app-only credential |
| 9 | Authenticode-signing arbitrary JSON | JSON is not a generally supported SIP file type | Create/sign a version-2 Windows catalog; read back signature, timestamp, and content verification |
| 10 | Catching exceptions silently in legs | Partial / wrong-shape data masquerades as clean | Catch-and-emit a `Status='*Failed'` row — never swallow |

### 14.3 Operating cadence

| Frequency | Action | Principal | Output |
|-----------|--------|-----------|--------|
| Hourly | `Get-Agt12ConsentPosture` queue check | reader | Triage ticket if non-empty |
| Daily | Inventory + ownership + credential delta | reader | Diff CSV to evidence store |
| Weekly | Full §3–§9 run, no `-IncludeAllSps` | reader | CSV to operations channel |
| Monthly | Power Platform + MCP + Integrated Apps legs | reader | CSV to AI governance backlog |
| Quarterly | Collect all required planes, reconcile, review status ledger, then export | reader (collect) + evidence signer (no tenant-write permission needed) | Signed catalog and raw pack to the configured evidence vault; validate the Control 3.1 adapter |
| Annually | OverPermissionedScopes baseline review | second-line risk | Updated default list in §5 |

**Acceptance cases required before scheduling:** unavailable/forbidden API; missing package license; multi-page and empty-page-with-next-link responses; untagged and same-name agents; multiple SPs sharing an AppId; nonhuman/limited-information owners; non-Graph resource app roles; zero/expired-retention sign-in history; disabled/report-only/excluded/unsupported CA targets; inaccessible and zero-bot environments; missing timestamp; changed file after signing; and empty collections. A successful function call is collection evidence, not a control PASS. Confirm a known record/event in each authoritative plane as a positive control.

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

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation verified 2026-10-16; tenant execution and current UI evidence outstanding)*
