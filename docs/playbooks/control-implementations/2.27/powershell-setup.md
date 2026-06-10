---
control_id: "2.27"
title: "PowerShell Setup — Control 2.27: Consumption-Entitlement Governance"
pillar: "2 — Management"
powershell_edition: "7.4 LTS Core"
last_ui_verified: "June 2026"
---

# PowerShell Setup — Control 2.27: Consumption-Entitlement Governance

> **Scope.** Operational PowerShell and Microsoft Graph automation for the eight Key Configuration Points of Control 2.27: confirm licensing and billing prerequisites, inventory the two consumption policy objects, register and validate the admission-gated security-group registry, classify each agent's consumption pathway, evaluate the switch-on-pathway entitlement contract across the `(agent, user)` population, record per-agent metered spend caps, run the pre-enforcement coverage-gap analysis monitor-only, and persist and forward entitlement and coverage-gap evidence. The automation is implemented by the companion **Copilot Billing Governance (CBG)** solution (`copilot-billing-governance/`).
>
> **What this control governs.** Control 2.27 governs the **entitlement decision** — *which users are entitled to incur metered or premium Copilot consumption on an agent, under which billing or credit policy, on which surface*. It **supports compliance with** the recordkeeping and IT-general-control expectations referenced below; it does not, on its own, satisfy any regulation, and organizations should verify their configuration meets their specific obligations.
>
> **Read-and-analyze first, enforce later.** Every helper in this playbook is read-only or analysis-only. No helper mutates a Microsoft billing/credit policy, writes a cap hard-stop, or activates enforcement. The pre-enforcement coverage-gap analysis (§9) is the gate: its would-be-blocked population is **reviewed and signed off before** any enforcement is contemplated.
>
> **Authentication is managed-identity-first.** See §0. Run inventory and evaluation under a managed identity holding the least-privilege Graph and Dataverse scopes; prefer the **AI Administrator** role over **Entra Global Admin** for day-to-day operation, and use Entra Privileged Identity Management (PIM) for just-in-time elevation where a one-time tenant action is unavoidable.
>
> **Upstream dependency.** The agent dimension (`createdIn`) and usage tier (`configuredTier`) are produced by the sibling solutions `copilot-agent-inventory` (Azure Resource Graph `PowerPlatformResources`) and `work-iq-usage-detection`. Until those are catalog-registered, the entitlement engine operates on an assembled/fixture input set via `-InputPath`. Work IQ general availability and the move of the Work IQ API to Copilot Credits consumption billing are scheduled for **June 16, 2026** — per the Microsoft 365 roadmap (feature 559017) and Microsoft Learn ("use-work-iq"), verified June 2026 (a near-term rollout).
>
> **Write-API posture (verified June 2026).** There is **no public write API to set an enforceable credit cap or hard spend-stop**: per-agent caps and Copilot credit policies are Power Platform admin-center UI features (Licensing > Copilot Studio > Manage Agents) and the Billing Policy CRUD API exposes no credit-cap field (per Microsoft Learn, "manage-copilot-studio-messages-capacity"). Where a hard-stop is unavailable, enforcement **degrades to detect-and-alert** — the cap is recorded and breaches are surfaced; it is **not** represented as a hard-stop. Should Microsoft ship a public cap-enforcement API, caps can be upgraded to a hard-stop. The live credit-policy **read** API is likewise unproven and falls back to the reconciled Dataverse store.

---

## 0. Prerequisites, authentication, and false-clean defects

### 0.1 Authentication and least privilege

!!! note "Prerequisites and least-privilege authentication"
    Configuring and evaluating metered-consumption entitlement requires **Microsoft 365 Copilot** licensing for in-scope users, at least one Microsoft Copilot **consumption-billing policy** (pay-as-you-go and/or prepaid credit), and an operating identity that can read Copilot license assignment, Entra group properties, and the CBG Dataverse tables.

    - **Managed-identity-first.** Acquire tokens from a system-assigned managed identity (Azure Automation, Function, container host), a user-assigned managed identity for shared automation, or workload identity federation (GitHub Actions OIDC → Entra app) for CI. Use interactive / device-code only for one-off admin-workstation runs. A client secret is a **legacy development-only** fallback — rotate and remove it before production; do not prescribe it as the recommended path.
    - **Role preference.** Prefer the **AI Administrator** role for operating Copilot billing/credit policies and Entra scope-group assignment. Reserve **Entra Global Admin** for one-time tenant setup, and activate it through **PIM** for just-in-time, time-bound elevation. This keeps the day-to-day operating principal least-privileged, which is **recommended to** support the SOX 404 ITGC narrative around who can authorize spend.
    - **Graph scopes (read-only):** `User.Read.All` (read Copilot license assignment), `Group.Read.All` (read `securityEnabled` / `mailEnabled` / `groupTypes` at admission), and `Organization.Read.All` (read subscribed SKUs). No write scope is required by any helper in this playbook.

```powershell
#Requires -Version 7.4

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Local checkout path of the Copilot Billing Governance solution scripts (adjust to your machine).
$cbgScripts = 'C:\src\fsi-agentgov-solutions\copilot-billing-governance\scripts'

function Assert-Agt227Shell {
    [CmdletBinding()]
    param()

    if ($PSVersionTable.PSEdition -ne 'Core') {
        throw "Control 2.27 helpers require PowerShell 7.4 Core. Detected edition: $($PSVersionTable.PSEdition). Re-launch under pwsh.exe."
    }
    if ($PSVersionTable.PSVersion -lt [version]'7.4.0') {
        throw "Control 2.27 helpers require PowerShell 7.4 LTS or later. Detected: $($PSVersionTable.PSVersion). Upgrade before continuing."
    }

    $loadedDesktopGraph = Get-Module -Name 'Microsoft.Graph*' |
        Where-Object { $_.Path -match 'WindowsPowerShell\\v1\.0' }
    if ($loadedDesktopGraph) {
        throw "Detected Microsoft.Graph modules loaded from the Windows PowerShell 5.1 path. This shell is contaminated; start a clean pwsh 7.4 process."
    }

    Write-Verbose "Shell parity confirmed: PowerShell $($PSVersionTable.PSVersion) Core."
}

Assert-Agt227Shell -Verbose
```

### 0.2 False-clean defects to refuse

Empty output is the most dangerous signal in a consumption-entitlement control: a tenant with no metered agents, an unlicensed operating principal, or an empty `configuredTier` all produce *quiet* results that look identical to "clean." Each helper in §§3–10 returns a structured object with a `Status` field whose values are `Clean`, `Anomaly`, `Pending`, `NotApplicable`, or `Error`. **No helper returns `$null` or an empty array as a clean signal.** When there is genuinely no data, the helper returns a single object with `Status='NotApplicable'` and a populated `Reason`.

| # | Defect | Symptom | Why it appears clean | Structural guard |
|---|--------|---------|----------------------|------------------|
| 0.1 | No Copilot licensing in tenant | License read returns zero Copilot SKUs | No exception is thrown; the entitlement input has no licensed users, so every `mcp-cs` / `mcp-agentbuilder` evaluation blocks on "Missing license" and the result looks decisive | §3 `Test-Agt227Prerequisite` checks `Get-MgSubscribedSku` for a Copilot SKU and returns `Status='NotApplicable'` with a reason rather than an empty allow-set |
| 0.2 | Wrong shell edition | Graph cmdlets succeed but return `@()` | Microsoft.Graph 2.x assemblies fail to bind under Desktop edition; the SDK swallows the bind failure and returns empty | `Assert-Agt227Shell` (§0.1) blocks Desktop edition entirely |
| 0.3 | Empty `configuredTier` silently classed as `none` | Many agents resolve to `none → Allow (eligibility N/A)` | When the upstream Work IQ feed is missing, `configuredTier` is empty and the engine's `createdIn` fallback may still land on `none`; the agent majority looks entitled when it is actually unclassified | §6 flags agents whose `configuredTier` **and** `createdIn` are both empty as `unmapped` candidates and counts them separately; a high `unmapped`/empty rate is treated as a feed defect, not a clean pass |
| 0.4 | Mail-enabled group accepted into the registry | A distribution or Microsoft 365 group is used as a credit-scope / audience group and evaluates as valid | Membership reads succeed against a mail-enabled group, so eligibility "works" while violating the admission gate | §5 `Test-Agt227GroupAdmission` rejects any group that is not `securityEnabled` or that is `mailEnabled`, emitting `Admitted=$false` |
| 0.5 | Detect-and-alert mistaken for a hard-stop | A per-agent cap row exists, so spend "looks capped" | No public write API enforces the cap; the row records intent only | §8 stamps `EnforcementMode='Detect-and-alert'` and `EnforcementIsHardStop=$false` whenever the write API is unconfirmed; the cap is never reported as a hard-stop |
| 0.6 | Zero-rating default hides fail-closed cases | `mcp-cs` users broadly resolve to Allow | `-ZeroRatingResolved` defaults `$true` per the June 2026 Licensing Guide (footnotes 6 & 7, verified June 2026); a licensed user on a zero-rated M365 surface is allowed, which can mask users who would fail-closed under the conservative posture | §7 records the `ZeroRatingResolved` posture per run and supports a paired `-ZeroRatingResolved:$false` shadow run so the conservative fail-closed population is visible before enforcement |
| 0.7 | Coverage-gap run as if it were enforcement | A gap export exists but enforcement assumptions are baked in | An operator runs the analysis after toggling enforcement, so `monitorOnly` is false and the would-be-blocked population is understated | §9 asserts `fsi_monitoronly = true` on every pre-enforcement row and refuses to treat any export with a non-monitor row as a valid pre-enforcement sign-off artifact |
| 0.8 | Credit-policy "live read" assumed authoritative | `-FromPlatform` returns PAYG rows but no credit rows | The credit-policy admin API is unproven; the live read falls back to Dataverse and may under-report | §3 surfaces `Source='platform-with-dataverse-fallback'` and warns that credit rows came from the reconciled store, not a live platform read |
| 0.9 | Native retention assumed sufficient | Entra/Graph audit query for an old decision finds nothing | Directory audit retention is far shorter than the FINRA 4511 six-year horizon; the SIEM is the system of record | §10 emits an explicit retention horizon and a SIEM-forwarding pointer; the materialized decision store carries `fsi_retainuntil` |

---

## 1. Modules, permissions, and canonical roles

### 1.1 Module pinning

| Module | Minimum version | Pinned for | Notes |
|--------|-----------------|------------|-------|
| `Microsoft.Graph.Authentication` | 2.19.0 | Token acquisition, scope validation | Loads transitively; pin explicitly to lock the cmdlet surface |
| `Microsoft.Graph.Users` | 2.19.0 | `Get-MgUserLicenseDetail` (per-user Copilot license read) | Entitlement input for the license-gated pathways |
| `Microsoft.Graph.Groups` | 2.19.0 | `Get-MgGroup` (registry admission: `securityEnabled` / `mailEnabled` / `groupTypes`) | Backs §5 admission gating |
| `Microsoft.Graph.Identity.DirectoryManagement` | 2.19.0 | `Get-MgSubscribedSku` (Copilot SKU presence) | Backs §3 licensing preflight |
| `Az.Accounts` | 2.15.0 | Managed-identity / `Get-AzAccessToken` for Dataverse and the Power Platform billing-policy admin API (BAP) | Token source only; no Az resource mutation |

```powershell
function Install-Agt227ModuleBaseline {
    [CmdletBinding(SupportsShouldProcess)]
    param()

    $required = @(
        @{ Name = 'Microsoft.Graph.Authentication';               RequiredVersion = '2.19.0' }
        @{ Name = 'Microsoft.Graph.Users';                        RequiredVersion = '2.19.0' }
        @{ Name = 'Microsoft.Graph.Groups';                       RequiredVersion = '2.19.0' }
        @{ Name = 'Microsoft.Graph.Identity.DirectoryManagement'; RequiredVersion = '2.19.0' }
        @{ Name = 'Az.Accounts';                                  RequiredVersion = '2.15.0' }
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

### 1.2 Permission matrix (Graph, Dataverse, and the billing-policy admin API)

The read surface spans three resources: Microsoft Graph (license + group reads), the CBG Dataverse environment (reconciled policy / entitlement / coverage-gap rows), and — only for `-FromPlatform` PAYG reads — the Power Platform **billing-policy admin API (BAP)**.

| Operation | Resource / scope | Type | Helpers |
|-----------|------------------|------|---------|
| Read per-user Copilot license assignment | Graph `User.Read.All` | Application or delegated | §3, §6 |
| Read Entra group admission properties | Graph `Group.Read.All` | Application or delegated | §5 |
| Read subscribed SKUs (Copilot presence) | Graph `Organization.Read.All` | Application or delegated | §3 |
| Read CBG reconciled rows | Dataverse Web API on the environment URL (e.g. `https://contoso.crm.dynamics.com`) | Dataverse app-user (least-privilege read role) | §3, §6, §8, §9, §10 |
| Read PAYG billing policies live (`-FromPlatform`) | Power Platform BAP `https://api.bap.microsoft.com/` | Managed identity / workload identity | §3 |
| Persist materialized decisions / coverage-gap rows | Dataverse Web API (`PATCH` on alternate key) | Dataverse app-user (write role) | §10 |

> **Write-API boundary.** There is **no** Microsoft billing/credit policy **write** scope in this matrix. Creating a PAYG policy, a credit policy, or a cap hard-stop is performed through the documented portal flows in §4 and §8, not through these helpers. The only writes any helper performs are to the **CBG Dataverse evidence tables** (§10) — never to a Microsoft consumption policy.

### 1.3 Canonical roles

Use the canonical doc-body role names. Mixing legacy long-form names across scripts and runbooks creates audit-trail friction.

| Canonical role | When required | Scope |
|----------------|---------------|-------|
| **AI Governance Lead** | Owns the control; convenes the §9 coverage-gap review; approves enforcement activation | Tenant (governance) |
| **AI Administrator** | Operates §3–§9 (policy inventory, registry assignment, evaluation, caps, coverage-gap); Copilot usage exports. **Preferred over Entra Global Admin** | Tenant (privileged; activate via PIM) |
| **Entra Global Admin** | One-time tenant setup of Copilot billing policies only; subsequent operation delegates to AI Administrator under PIM | Tenant |
| **Power Platform Admin** | Dataverse schema (entitlement / cap / coverage-gap tables) and the evaluation flows | Tenant / environment |
| **Entra User Admin** | Maintains the admission-gated security-group registry (credit-scope, API-audience, billing groups) | Tenant |
| **Finance / Controller** | Approves cap thresholds and spend appetite; signs the cost-estimate basis; maintains SOX 404 ITGC documentation | Governance |
| **Compliance Officer** | Confirms retention per FINRA 4511 / SEC 17a-4(b)(4); produces examination evidence | Governance |
| **Business Unit Owner** | Approves entitled cohorts for their unit's agents; responds to coverage-gap findings | Business unit |

> **PIM discipline.** Operate from a session whose privileged role activation is fresh. The §2 bootstrap stamps the operating role into session metadata so evidence records the principal under which an evaluation ran.

---

## 2. Session initialization

The bootstrap connects to Microsoft Graph (US commercial cloud), resolves a Dataverse token managed-identity-first, and records the operating posture. It does not connect to any billing/credit policy write surface.

```powershell
function Initialize-Agt227Session {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$EnvironmentUrl,                # CBG Dataverse environment, e.g. https://contoso.crm.dynamics.com

        [Parameter()]
        [string]$TenantId,

        [Parameter()]
        [string]$ClientId,                      # user-assigned managed identity / app registration

        [Parameter()]
        [switch]$UseDeviceCode,                 # one-off admin-workstation runs only

        [Parameter()]
        [string]$DataverseAccessToken           # managed-identity-supplied; omit to fall back (dev-only)
    )

    Assert-Agt227Shell

    $scopes = @('User.Read.All','Group.Read.All','Organization.Read.All')

    $connectArgs = @{ Scopes = $scopes; NoWelcome = $true; ContextScope = 'Process' }
    if ($TenantId)      { $connectArgs.TenantId = $TenantId }
    if ($ClientId)      { $connectArgs.ClientId = $ClientId }
    if ($UseDeviceCode) { $connectArgs.UseDeviceCode = $true }

    Connect-MgGraph @connectArgs | Out-Null

    $context = Get-MgContext
    $missing = $scopes | Where-Object { $_ -notin $context.Scopes }
    if ($missing) {
        throw "Token missing required read scopes: $($missing -join ', '). Re-consent required."
    }

    # Dataverse token, managed-identity-first. Resolve-Agt227DataverseToken is defined in §3.1.
    $dvToken = Resolve-Agt227DataverseToken -ResourceUrl $EnvironmentUrl -ProvidedToken $DataverseAccessToken

    $session = [pscustomobject]@{
        ControlId        = '2.27'
        Cloud            = 'Commercial'
        GraphEndpoint    = 'https://graph.microsoft.com'
        EnvironmentUrl   = $EnvironmentUrl.TrimEnd('/')
        TenantId         = $context.TenantId
        OperatingScopes  = $scopes
        DataverseToken   = $dvToken
        SessionStarted   = (Get-Date).ToUniversalTime()
        Status           = 'Clean'
    }

    Set-Variable -Name 'Agt227Session' -Value $session -Scope Script -Force
    return $session
}
```

> **Token hygiene.** The session object carries a live Dataverse bearer token. Treat the variable as sensitive: do not serialize `$Agt227Session` into evidence exports, and clear it (`Remove-Variable Agt227Session -Scope Script`) at the end of an operating run.

---

## 3. Key Configuration Point 1 — Confirm licensing and billing prerequisites

Verify that in-scope users hold a **Microsoft 365 Copilot** license, that at least one consumption-billing policy object exists, and that the operating principal holds **AI Administrator** (preferred over Entra Global Admin; PIM for JIT). The policy inventory itself is read by the CBG `Get-BillingPolicyInventory.ps1` script (§4); this preflight establishes that evaluation is meaningful before any pathway is classified.

### 3.1 Dataverse token resolution (managed-identity-first)

This mirrors the CBG `Get-BillingPolicyInventory.ps1` token helper exactly: a supplied token is used as-is; otherwise it falls back to `Get-AzAccessToken` for development only.

```powershell
function Resolve-Agt227DataverseToken {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ResourceUrl,
        [string]$ProvidedToken
    )

    if (-not [string]::IsNullOrWhiteSpace($ProvidedToken)) {
        return $ProvidedToken
    }

    # legacy: dev-only — replace with a managed-identity-supplied -DataverseAccessToken in production
    Write-Verbose 'No Dataverse token supplied; falling back to Get-AzAccessToken (dev-only).'
    if (-not (Get-Command -Name Get-AzAccessToken -ErrorAction SilentlyContinue)) {
        throw "No token provided and Az.Accounts (Get-AzAccessToken) is unavailable. Supply a managed-identity token, or install Az.Accounts and sign in."
    }
    $secure = (Get-AzAccessToken -ResourceUrl $ResourceUrl -AsSecureString).Token
    return ($secure | ConvertFrom-SecureString -AsPlainText)
}
```

### 3.2 Licensing preflight

```powershell
function Test-Agt227Prerequisite {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        # Copilot SKU part numbers vary by tenant; verify in your tenant with Get-MgSubscribedSku.
        [string[]]$CopilotSkuPattern = @('Microsoft_365_Copilot','Copilot')
    )

    $now = (Get-Date).ToUniversalTime()

    $skus = Get-MgSubscribedSku -All -ErrorAction Stop
    $copilotSku = $skus | Where-Object {
        $part = $_.SkuPartNumber
        ($CopilotSkuPattern | Where-Object { $part -match $_ })
    }

    $hasCopilot = [bool]$copilotSku
    $enabledUnits = if ($hasCopilot) { ( $copilotSku | ForEach-Object { $_.PrepaidUnits.Enabled } | Measure-Object -Sum ).Sum } else { 0 }

    $status = if ($hasCopilot) { 'Clean' } else { 'NotApplicable' }
    $reason = if ($hasCopilot) {
        $null
    } else {
        'No Microsoft 365 Copilot SKU found in the tenant. Entitlement evaluation is not meaningful without licensed users; verify the SKU part number pattern against Get-MgSubscribedSku.'
    }

    [pscustomobject]@{
        ControlId          = '2.27'
        Criterion          = 'LicensingAndBillingPrerequisite'
        HasCopilotSku      = $hasCopilot
        CopilotSkuParts    = @($copilotSku.SkuPartNumber)
        CopilotPrepaidUnits = $enabledUnits
        Status             = $status
        Reason             = $reason
        Timestamp          = $now
    }
}
```

> **Verify.** A `Status='NotApplicable'` here is a **stop** condition for Zone 2/3 evaluation, not a clean pass — it means the entitlement input has no licensed users. Record the `CopilotSkuParts` actually observed; Copilot SKU part numbers change and the regex is a starting point, not an assertion. 🔎

---

## 4. Key Configuration Point 2 — Establish the two policy objects and choose a configuration

Two policy objects back metered spend, and three configurations compose them:

| | PAYG billing policy (`fsi_cbgbillingpolicy`) | Prepaid credit policy (`fsi_cbgcreditpolicy`) |
|---|---|---|
| Backing | Azure subscription | Prepaid (no Azure subscription) |
| Tenant ceiling 🔎 | **50** | **10** |
| Setup | Two-step **add → connect** | Standalone |
| Spend control | **Budget alerts only — not a hard-stop** | Standalone **hard-stop** |
| Surfaces | All metered surfaces **including SharePoint** grounding | **Chat-only today**; SharePoint stays on PAYG |

Three supported configurations: **credit-only**, **credit + PAYG**, **PAYG-only**.

### 4.1 Creating the policies (documented portal flows)

There is **no confirmed public PowerShell cmdlet** that creates a Copilot PAYG billing policy or a prepaid credit policy. Do not substitute the SharePoint `New-SPOAppBillingPolicy` cmdlet — it governs SharePoint add-in billing, not Copilot consumption. Create the policies through the documented portal flows:

- **PAYG billing policy (two-step add → connect).** In the **Power Platform admin center** → **Licensing** → **Pay-as-you-go plans** → **New billing plan**, choose **Azure subscription** (general metered surfaces) or **Microsoft 365 Copilot Chat** (the Copilot consumption meter), name the plan, select the Azure subscription and resource group (**add**), then select the environments to link (**connect**). PAYG provides **budget alerts only — not a hard-stop**. Reference: [Set up pay-as-you-go](https://learn.microsoft.com/power-platform/admin/pay-as-you-go-set-up) and [pay-as-you-go overview](https://learn.microsoft.com/power-platform/admin/pay-as-you-go-overview). *(The current portal labels these "billing plans"; the API and the CBG schema use "billing policy" — they are the same object.)*
- **Prepaid credit policy.** Configure the Copilot credit policy in the **Microsoft 365 admin center** Copilot management surface. Credit policies are a **standalone hard-stop** and are **Chat-only today** 🔎; SharePoint-grounded consumption stays on PAYG.

> **Write-API reality (verified June 2026).** A public **Billing Policy CRUD API does exist**: `POST` / `PUT` / `DELETE https://api.powerplatform.com/licensing/billingPolicies?api-version=2024-10-01`, plus Add / Remove Billing Policy Environment — so a PAYG billing policy *can* be created and connected programmatically. **That API exposes no credit-cap or spend-ceiling field**, however (its writable fields are name, status `Enabled`/`Disabled`, and the Azure billing instrument only), and PAYG **budgets are alert-only** — Microsoft states the system doesn't enforce the budget or stop the organization from exceeding it. **Copilot credit policies** (≤10 per tenant) and **per-agent monthly credit caps** are Microsoft 365 / Power Platform admin-center UI features (Licensing > Copilot Studio > Manage Agents) with **no public write API**, per [Microsoft Learn — manage Copilot Studio message capacity](https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity). Net: there is **no public API to set an enforceable credit cap or hard spend-stop**, so cap enforcement correctly **degrades to detect-and-alert**. Should Microsoft ship a cap/credit-policy write surface, validate it in a non-production tenant before automating.

### 4.2 Inventory the policies and the ceilings (read-only)

The CBG `Get-BillingPolicyInventory.ps1` script reads both objects and reports headroom against the **50 / 10** ceilings. The PAYG **live** read uses the documented BAP endpoint; the credit **live** read is unproven and falls back to the reconciled Dataverse store.

```powershell
# Proven path — read the reconciled Dataverse rows the CBG-PolicySync flow maintains:
$inventory = & "$cbgScripts\Get-BillingPolicyInventory.ps1" `
    -EnvironmentUrl $Agt227Session.EnvironmentUrl `
    -AccessToken    $Agt227Session.DataverseToken

# Optional live PAYG read (credit policies still fall back to Dataverse):
$inventory = & "$cbgScripts\Get-BillingPolicyInventory.ps1" `
    -EnvironmentUrl $Agt227Session.EnvironmentUrl `
    -AccessToken    $Agt227Session.DataverseToken `
    -FromPlatform `
    -BillingApiAccessToken $bapToken            # resource https://api.bap.microsoft.com/

$inventory.PayAsYouGo | Format-List Count, Ceiling, Headroom, AtCeiling
$inventory.Credit     | Format-List Count, Ceiling, Headroom, AtCeiling
$inventory.Source      # 'dataverse' or 'platform-with-dataverse-fallback'
```

The documented BAP read the script performs (real, from the CBG source) is:

```text
GET https://api.bap.microsoft.com/providers/Microsoft.BusinessAppPlatform/billingPolicies?api-version=2022-03-01-preview
Authorization: Bearer <BAP token>
```

> **Verify.** Record the chosen configuration (credit-only / credit + PAYG / PAYG-only), the observed `Count` vs `Ceiling` for each object, and the `Source`. A `Source='platform-with-dataverse-fallback'` means the **credit** rows came from the reconciled store, not a live platform read (defect 0.8) — note it in the configuration record. Re-confirm the **50 / 10** ceilings against current Microsoft documentation. 🔎

---

## 5. Key Configuration Point 3 — Register the admission-gated security-group registry

Entitlement scope (credit-scope, API-audience, and billing groups) is expressed through Entra security groups held in the admission-gated registry `fsi_cbgapprovedgrouppolicy`. **Every registered group must be `securityEnabled` and not `mailEnabled`** — a mail-enabled distribution or Microsoft 365 group is rejected at admission. This is the source of the "who is in credit scope / eligible cohort" checks the engine relies on.

### 5.1 Admission gate

```powershell
function Test-Agt227GroupAdmission {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)][string]$GroupId,
        # fsi_cbg_grouplayer: Maker | Audience | Billing
        [Parameter(Mandatory)][ValidateSet('Maker','Audience','Billing')][string]$GroupLayer
    )

    $g = Get-MgGroup -GroupId $GroupId -Property 'id,displayName,securityEnabled,mailEnabled,groupTypes' -ErrorAction Stop

    $admitted = ($g.SecurityEnabled -eq $true) -and ($g.MailEnabled -ne $true)
    $rejectReason = @()
    if ($g.SecurityEnabled -ne $true) { $rejectReason += 'not securityEnabled' }
    if ($g.MailEnabled -eq $true)     { $rejectReason += 'mailEnabled (distribution / M365 group rejected)' }

    [pscustomobject]@{
        ControlId       = '2.27'
        Criterion       = 'GroupRegistryAdmission'   # manifest check 2.27.d
        GroupId         = $g.Id
        GroupDisplayName = $g.DisplayName
        GroupLayer      = $GroupLayer
        SecurityEnabled = [bool]$g.SecurityEnabled
        MailEnabled     = [bool]$g.MailEnabled
        GroupTypes      = ($g.GroupTypes -join ',')
        Admitted        = $admitted
        Status          = if ($admitted) { 'Clean' } else { 'Anomaly' }
        Reason          = if ($admitted) { $null } else { "Rejected: $($rejectReason -join '; ')" }
        Timestamp       = (Get-Date).ToUniversalTime()
    }
}
```

The admitted row maps to `fsi_cbgapprovedgrouppolicy` with these logical names: `fsi_groupid`, `fsi_grouplayer` (`Maker` = 100000000, `Audience` = 100000001, `Billing` = 100000002), `fsi_securityenabled`, `fsi_mailenabled`, `fsi_grouptypes`, `fsi_zoneclassification`, `fsi_isactive`, `fsi_approvedby`, `fsi_approvedat`. The alternate key is `(fsi_groupid, fsi_grouplayer)`.

### 5.2 Sweep the registry and prove zero mail-enabled scope groups

```powershell
function Get-Agt227RegistryAdmissionReport {
    [CmdletBinding()]
    param([Parameter(Mandatory)][pscustomobject[]]$Registry)  # each row: GroupId, GroupLayer

    $rows = foreach ($entry in $Registry) {
        Test-Agt227GroupAdmission -GroupId $entry.GroupId -GroupLayer $entry.GroupLayer
    }

    $rejected = @($rows | Where-Object { -not $_.Admitted })
    [pscustomobject]@{
        ControlId        = '2.27'
        Criterion        = 'GroupRegistryAdmission'
        GroupsChecked    = $rows.Count
        MailEnabledFound = @($rows | Where-Object MailEnabled).Count
        RejectedCount    = $rejected.Count
        Rejected         = $rejected
        Status           = if ($rejected.Count -eq 0 -and $rows.Count -gt 0) { 'Clean' }
                           elseif ($rows.Count -eq 0) { 'NotApplicable' }
                           else { 'Anomaly' }
        Timestamp        = (Get-Date).ToUniversalTime()
    }
}
```

> **Verify (manifest check `2.27.d`).** The evidence for criterion 2 is this report showing **zero mail-enabled scope groups** and a non-empty `GroupsChecked`. An empty registry returns `NotApplicable`, not `Clean` — a Zone 2/3 tenant with metered agents must have populated scope groups.

---

## 6. Key Configuration Point 4 — Classify each agent's consumption pathway

Each agent maps to exactly one `fsi_cbg_pathway`: `none` (100000000), `mcp-cs` (100000001), `mcp-agentbuilder` (100000002), `api-direct` (100000003), `metered` (100000004), `unmapped` (100000005). **The Work IQ `configuredTier` is authoritative and evaluated first; the Azure Resource Graph `createdIn` signal is a last-resort fallback** consulted only when `configuredTier` is empty or unrecognized. `unmapped` is an **anomaly to investigate**, not a reason to block users.

### 6.1 Classification, mirroring the engine's `Get-AgentPathway`

The runnable classifier is `Get-AgentPathway` inside the CBG `Invoke-EntitlementEvaluation.ps1`. The mapping it applies (verbatim from the engine):

| `configuredTier` (Work IQ, lowercased) | Pathway |
|---|---|
| `nativemcpcopilotstudio` | `mcp-cs` |
| `nativeapidirect` | `api-direct` |
| `notconfigured`, `adjacent`, `none`, `classic`, `non-metered`, `nonmetered` | `none` |
| `metered`, `generative`, `grounded`, `agent-action`, `premium` | `metered` |

Only when `configuredTier` is empty/unrecognized does the engine fall back to `createdIn` (regex): Copilot Studio → `mcp-cs`; Agent Builder → `mcp-agentbuilder`; api / declarative / direct-line / custom → `api-direct`; otherwise `unmapped`.

```powershell
function Get-Agt227PathwayPreview {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][AllowNull()][AllowEmptyString()][string]$CreatedIn,
        [Parameter(Mandatory)][AllowNull()][AllowEmptyString()][string]$ConfiguredTier
    )

    $tier    = ("$ConfiguredTier").Trim().ToLowerInvariant()
    $created = ("$CreatedIn").Trim().ToLowerInvariant()

    # configuredTier is authoritative — evaluated FIRST.
    $pathway =
        if     ($tier -eq 'nativemcpcopilotstudio') { 'mcp-cs' }
        elseif ($tier -eq 'nativeapidirect')        { 'api-direct' }
        elseif ($tier -in @('notconfigured','adjacent','none','classic','non-metered','nonmetered')) { 'none' }
        elseif ($tier -in @('metered','generative','grounded','agent-action','premium')) { 'metered' }
        elseif ($created -match 'copilot.?studio|^cs$|mcp-cs')        { 'mcp-cs' }
        elseif ($created -match 'agent.?builder|mcp-agentbuilder')    { 'mcp-agentbuilder' }
        elseif ($created -match 'api|declarative|direct.?line|custom'){ 'api-direct' }
        else { 'unmapped' }

    $bothEmpty = [string]::IsNullOrWhiteSpace($tier) -and [string]::IsNullOrWhiteSpace($created)

    [pscustomobject]@{
        ControlId       = '2.27'
        Criterion       = 'PathwayClassification'   # manifest checks 2.27.a / .c
        ConfiguredTier  = $ConfiguredTier
        CreatedIn       = $CreatedIn
        Pathway         = $pathway
        FeedMissing     = $bothEmpty                # defect 0.3: both signals empty
        Status          = if ($pathway -eq 'unmapped') { 'Anomaly' } elseif ($bothEmpty) { 'Anomaly' } else { 'Clean' }
        Timestamp       = (Get-Date).ToUniversalTime()
    }
}
```

> **Verify.** This helper is a **preview** for triage — the authoritative classification is performed inside the engine in §7. Treat a non-zero `unmapped` count (or a non-zero `FeedMissing` count) as an upstream-feed defect to investigate, and record each `unmapped` agent as an anomaly with a follow-up owner (criterion 3). A high `unmapped`/empty rate when the Work IQ feed is offline is the §0.2 defect 0.3 condition, not a clean pass.

---

## 7. Key Configuration Point 5 — Apply the entitlement contract per pathway

The contract is evaluated by the CBG `Invoke-EntitlementEvaluation.ps1` engine. It classifies the pathway (§6), then applies pathway-specific eligibility for each intended user, emitting one decision per `(agent, user)` and one per-agent coverage-gap aggregate (§9). Decisions map to `fsi_cbg_decision`:

| Decision | `fsi_cbg_decision` | When |
|---|---|---|
| **Allow** | 100000000 | `mcp-agentbuilder`/`api-direct`/`mcp-cs`/`metered` eligibility satisfied |
| **Block** | 100000001 | A bounded block **inside a metered or license/cohort-gated pathway** (no eligible cohort / missing license) |
| **Allow - Eligibility N/A** | 100000002 | `none` — the non-metered agent majority |
| **Fail-open - Anomaly** | 100000003 | `unmapped` — permits the user but records an anomaly (a detection defect must not deny a user) |
| **Fail-closed - Zero-rating Unresolved** | 100000004 | Licensed `mcp-cs` user, surface not zero-rated (or zero-rating reverted) and not in credit scope |

Eligibility by pathway (verbatim from the engine's `Resolve-EntitlementDecision`):

- `none` → **Allow - Eligibility N/A** (no metered consumption; no billing decision).
- `mcp-agentbuilder` → requires a Copilot license, else **Block (Missing license)**.
- `api-direct` → requires API-audience-cohort membership, else **Block (No eligible cohort)**.
- `mcp-cs` → requires a Copilot license **AND** (the surface is zero-rated when `ZeroRatingResolved` **OR** the user is in credit scope); otherwise **Fail-closed - Zero-rating Unresolved**.
- `metered` → requires eligible-cohort membership; the only unbounded `ELSE`, bounded to a metered pathway, else **Block (No eligible cohort)**.
- `unmapped` → **Fail-open - Anomaly**.

### 7.1 Input shape

Each agent record carries `agentId`, `agentName`, `createdIn`, `configuredTier`, `spendScope` (`Chat` / `SharePoint` / `Mixed`), optional `sourcePolicyId`, and an `intendedUsers[]` array. Each user carries `upn`, `hasCopilotLicense`, `inApiAudienceGroup`, `inEligibleCohort`, `inCreditScopeGroup`, and `surfaceZeroRated`. Today the engine reads this from a fixture via `-InputPath` (the upstream `copilot-agent-inventory` and `work-iq-usage-detection` feeds are not yet live); the boolean user attributes are assembled from the Graph license read (§3) and the registry membership reads (§5).

```powershell
# Assemble one intended-user record from the Graph license read + registry membership.
function New-Agt227IntendedUser {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Upn,
        [Parameter(Mandatory)][bool]$HasCopilotLicense,   # from Get-MgUserLicenseDetail (Copilot service plan present)
        [bool]$InApiAudienceGroup,
        [bool]$InEligibleCohort,
        [bool]$InCreditScopeGroup,
        [bool]$SurfaceZeroRated
    )
    [pscustomobject]@{
        upn                = $Upn
        hasCopilotLicense  = $HasCopilotLicense
        inApiAudienceGroup = [bool]$InApiAudienceGroup
        inEligibleCohort   = [bool]$InEligibleCohort
        inCreditScopeGroup = [bool]$InCreditScopeGroup
        surfaceZeroRated   = [bool]$SurfaceZeroRated
    }
}
```

A per-user Copilot license read uses the real Graph cmdlet:

```powershell
$details = Get-MgUserLicenseDetail -UserId $upn
$hasCopilot = [bool]($details.ServicePlans |
    Where-Object { $_.ServicePlanName -match 'COPILOT' -and $_.ProvisioningStatus -eq 'Success' })   # 🔎 confirm the service-plan name in your tenant
```

### 7.2 Run the evaluation

```powershell
# Default posture: zero-rating RESOLVED per the June 2026 Licensing Guide (footnotes 6 & 7, verified June 2026).
& "$cbgScripts\Invoke-EntitlementEvaluation.ps1" `
    -InputPath  .\agents.input.json `
    -OutputPath .\entitlement-result.json

# Conservative shadow run: revert to fail-closed so the at-risk mcp-cs population is visible.
& "$cbgScripts\Invoke-EntitlementEvaluation.ps1" `
    -InputPath  .\agents.input.json `
    -OutputPath .\entitlement-result.failclosed.json `
    -ZeroRatingResolved:$false
```

The engine's real parameters: `-InputPath` (mandatory), `-OutputPath`, `-ZeroRatingResolved` (bool, default `$true`), `-CacheTtlMinutes` (default 1440), `-SampleCap` (default 20), `-GroupSizeThreshold` (default 500), `-RetentionDays` (default 183). It emits a result object with `Decisions[]` (shaped to `fsi_cbgentitlementmaterialized`) and `CoverageGaps[]` (shaped to `fsi_cbgcoveragegap`). The engine is **write-free** — Dataverse persistence is performed by the CBG-CoverageGapAnalyzer flow (and the §10 evidence helper).

### 7.3 Decision field reference (`fsi_cbgentitlementmaterialized`)

Each emitted decision carries these logical names: `fsi_name` (`agentid:userupn` cache key), `fsi_agentid`, `fsi_userupn`, `fsi_pathway`, `fsi_decision`, `fsi_decisionreason` (`fsi_cbg_blockreason`, **null for allows**), `fsi_spendscope`, `fsi_sourcepolicyid`, `fsi_evaluatedat`, `fsi_ttlexpiresat`, `fsi_notes` (the evaluation trace). The alternate key is `(fsi_agentid, fsi_userupn)`.

> **Verify (manifest check `2.27.a`).** Evidence for criterion 4 is the materialized decision export showing pathway, decision, and block reason, with the `ZeroRatingResolved` posture recorded per run. Run both the default and the `-ZeroRatingResolved:$false` shadow so the fail-closed delta is visible before enforcement (defect 0.6).

!!! warning "Entitlement-decision caveat"
    The contract resolves a single auditable decision per `(agent, user)`; it governs the **entitlement decision** and does not, on its own, satisfy any regulation. The zero-rating default reflects the June 2026 Microsoft Copilot Studio Licensing Guide (footnotes 6 & 7) — verified June 2026 and corroborated on [Microsoft Learn — Copilot Studio billing and licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing) — a Copilot-licensed user on a Microsoft 365 surface under their own identity is **included** in the Microsoft 365 Copilot User SL at no additional charge, subject to fair-usage limits. The generative-answer-with-tenant-grounding and beyond-fair-use refinements affect credit **cost**, not this allow/deny, and should be confirmed per tenant.

---

## 8. Key Configuration Point 6 — Configure per-agent metered spend caps (Zone 3)

For each Zone 3 metered agent, record a per-agent cap in `fsi_cbgagentcap`: `fsi_agentid`, `fsi_monthlycreditcap`, `fsi_creditsconsumedmtd`, `fsi_enforcementmode` (`fsi_cbg_enforcementmode`: `Detect-and-alert` = 100000000, `Hard-stop` = 100000001), `fsi_capenforced`, `fsi_zoneclassification`, `fsi_lastevaluatedat`. The alternate key is `fsi_agentid`.

**Because there is no public write API to set an enforceable credit cap or hard spend-stop as of June 2026 (the Billing Policy CRUD API has no credit-cap field, and per-agent caps are Power Platform admin-center UI-managed), automation degrades to detect-and-alert.** The helper records the cap and surfaces a month-to-date breach; it does **not** apply a programmatic hard-stop, and it does **not** report the cap as a hard-stop.

```powershell
function Set-Agt227AgentCapRecord {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)][string]$AgentId,
        [Parameter(Mandatory)][int]$MonthlyCreditCap,
        [int]$CreditsConsumedMtd = 0,
        [ValidateSet('Team (Zone 2)','Enterprise (Zone 3)')][string]$Zone = 'Enterprise (Zone 3)',
        # Only set $true when a hard-stop write API has been confirmed for your tenant.
        [bool]$HardStopApiConfirmed = $false
    )

    $mode = if ($HardStopApiConfirmed) { 'Hard-stop' } else { 'Detect-and-alert' }
    $breached = $CreditsConsumedMtd -ge $MonthlyCreditCap

    [pscustomobject]@{
        ControlId             = '2.27'
        Criterion             = 'PerAgentCap'        # manifest check 2.27.b
        fsi_agentid           = $AgentId
        fsi_monthlycreditcap  = $MonthlyCreditCap
        fsi_creditsconsumedmtd = $CreditsConsumedMtd
        fsi_enforcementmode   = $mode                # never 'Hard-stop' unless the API is confirmed
        EnforcementIsHardStop = [bool]$HardStopApiConfirmed
        fsi_capenforced       = [bool]$HardStopApiConfirmed
        fsi_zoneclassification = $Zone
        BreachDetected        = $breached
        Status                = if ($breached) { 'Anomaly' } else { 'Clean' }
        Reason                = if ($breached) { "Month-to-date consumption ($CreditsConsumedMtd) at or above cap ($MonthlyCreditCap). Detect-and-alert surfaces the breach; no programmatic hard-stop is applied." } else { $null }
        fsi_lastevaluatedat   = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

> **Verify (manifest check `2.27.b`).** Evidence for criterion 5 is the cap-record export with the enforcement mode recorded per agent. **No Zone 3 agent is documented as a hard-stop where the write API is unproven** (defect 0.5): `EnforcementIsHardStop` stays `$false` until a tenant-confirmed write API exists. Detect-and-alert surfaces breaches; it does not stop spend.

---

## 9. Key Configuration Point 7 — Run the pre-enforcement coverage-gap analysis (monitor-only)

Before any enforcement, produce the per-agent coverage-gap aggregate **in monitor-only mode**, review the would-be-blocked population, and obtain sign-off. The engine emits one `fsi_cbgcoveragegap` row per agent — aggregating **per agent** (not per agent × user) keeps the output bounded.

### 9.1 Coverage-gap field reference (`fsi_cbgcoveragegap`)

| Logical name | Meaning |
|---|---|
| `fsi_agentid` / `fsi_agentname` | Analyzed agent |
| `fsi_pathway` | Classified pathway |
| `fsi_eligibleusers` | Count of users **not** blocked |
| `fsi_blockeduserscount` | Count of intended users who **would be blocked** |
| `fsi_blockedsampleupns` | **Capped** JSON array of blocked UPNs (bounded by `-SampleCap`, default 20) |
| `fsi_blockreasonsummary` | Dominant block reason (`fsi_cbg_blockreason`) across the blocked cohort |
| `fsi_spendscope` | Surface-aware scope: `Chat` (100000000), `SharePoint` (100000001), `Mixed` (100000002) |
| `fsi_groupsizepartition` | Total intended-audience size (flags groups above threshold `T`, default 500) |
| `fsi_monitoronly` | `true` first — gap rows take no enforcement action |
| `fsi_analyzedat` / `fsi_retainuntil` | Analysis time and retention horizon |

> **"Blocked" semantics (engine `Test-DecisionIsAllow`).** A user counts as **blocked** in the coverage gap when the decision is **not** one of `Allow`, `Allow - Eligibility N/A`, or `Fail-open - Anomaly`. That means **Fail-closed - Zero-rating Unresolved counts as blocked**, while **Fail-open - Anomaly does not** (an `unmapped`-pathway user is permitted). Read `fsi_blockeduserscount` with that rule in mind.

### 9.2 Confirm monitor-only and summarize the would-be-blocked population

```powershell
function Get-Agt227CoverageGapReview {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param([Parameter(Mandatory)][string]$ResultPath)   # entitlement-result.json from §7.2

    $result = Get-Content -LiteralPath $ResultPath -Raw | ConvertFrom-Json
    $gaps   = @($result.CoverageGaps)

    $nonMonitor = @($gaps | Where-Object { $_.fsi_monitoronly -ne $true })
    if ($nonMonitor.Count -gt 0) {
        # defect 0.7 — not a valid pre-enforcement artifact
        return [pscustomobject]@{
            ControlId = '2.27'; Criterion = 'CoverageGap'; Status = 'Anomaly'
            Reason    = "$($nonMonitor.Count) coverage-gap row(s) are not monitor-only; this export cannot serve as a pre-enforcement sign-off artifact."
            Timestamp = (Get-Date).ToUniversalTime()
        }
    }

    $totalBlocked = ($gaps | Measure-Object -Property fsi_blockeduserscount -Sum).Sum
    [pscustomobject]@{
        ControlId          = '2.27'
        Criterion          = 'CoverageGap'              # manifest check 2.27.c
        AgentsAnalyzed     = $gaps.Count
        TotalWouldBeBlocked = [int]$totalBlocked
        AgentsWithBlocks   = @($gaps | Where-Object { $_.fsi_blockeduserscount -gt 0 }).Count
        AllMonitorOnly     = $true
        Status             = if ($gaps.Count -gt 0) { 'Clean' } else { 'NotApplicable' }
        Timestamp          = (Get-Date).ToUniversalTime()
    }
}
```

### 9.3 Coverage-gap spend estimate (reference constants — not an invoice)

The engine carries per-feature **Copilot credit** reference rates for cost estimation. These are constants (not a Dataverse table); **verify against current Microsoft licensing documentation before relying on them** 🔎.

| Feature | Credits 🔎 |
|---|---|
| Classic answer | 1 |
| Generative answer | 2 |
| Agent action | 5 |
| Tenant-graph grounding | 10 |
| Agent flow | 13 per 100 flow actions |

Pricing context 🔎: **$0.01 per credit**; the prepaid pack is **25,000 credits per month, non-rolling** (unused credits do not carry over). PAYG consumption meters against an Azure subscription with **budget alerts only — not a hard-stop**.

> **Verify (manifest check `2.27.c`).** Evidence for criteria 6 and 7 is the coverage-gap export with `fsi_monitoronly = true` on **all** rows, the per-agent eligible / would-be-blocked counts, the capped UPN sample, and the dominant block reason — plus a **documented sign-off** on the would-be-blocked population and a spend **estimate** reconciled against the Microsoft 365 admin center and Azure cost reporting. These figures support cost *estimation*; they do not produce a billing-accurate invoice. **Sign-off is required before any enforcement is activated.**

---

## 10. Key Configuration Point 8 — Retain decisions and forward evidence

Persist the materialized decisions and coverage-gap aggregates, apply a retention horizon aligned to **FINRA 4511 (six-year minimum)** and **SEC 17a-4(b)(4)**, and forward the records to the SIEM so the evidence is examination-ready.

### 10.1 Persist to Dataverse (mirrors the CBG-CoverageGapAnalyzer flow)

The engine is write-free; the **CBG-CoverageGapAnalyzer flow is the canonical writer**. For an operator-run evidence pass, the same idempotent upsert can be performed against the Dataverse Web API using the alternate keys defined in the schema (`(fsi_agentid, fsi_userupn)` for decisions; `fsi_agentid` for coverage gaps).

```powershell
function Save-Agt227Evidence {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)][string]$ResultPath,
        [Parameter(Mandatory)][string]$EnvironmentUrl,
        [Parameter(Mandatory)][string]$DataverseToken
    )

    $base    = $EnvironmentUrl.TrimEnd('/')
    $headers = @{
        Authorization      = "Bearer $DataverseToken"
        'OData-MaxVersion' = '4.0'
        'OData-Version'    = '4.0'
        'Content-Type'     = 'application/json'
        'If-Match'         = '*'            # upsert on the alternate key
    }
    $result = Get-Content -LiteralPath $ResultPath -Raw | ConvertFrom-Json

    foreach ($d in @($result.Decisions)) {
        $key = "fsi_cbgentitlementmaterializeds(fsi_agentid='$($d.fsi_agentid)',fsi_userupn='$($d.fsi_userupn)')"
        if ($PSCmdlet.ShouldProcess($key, 'PATCH materialized decision')) {
            Invoke-RestMethod -Method Patch -Uri "$base/api/data/v9.2/$key" -Headers $headers `
                -Body ($d | ConvertTo-Json -Depth 6)
        }
    }
    foreach ($g in @($result.CoverageGaps)) {
        $key = "fsi_cbgcoveragegaps(fsi_agentid='$($g.fsi_agentid)')"
        if ($PSCmdlet.ShouldProcess($key, 'PATCH coverage-gap row')) {
            Invoke-RestMethod -Method Patch -Uri "$base/api/data/v9.2/$key" -Headers $headers `
                -Body ($g | ConvertTo-Json -Depth 6)
        }
    }

    [pscustomobject]@{
        ControlId    = '2.27'
        Criterion    = 'EvidenceRetention'
        Decisions    = @($result.Decisions).Count
        CoverageGaps = @($result.CoverageGaps).Count
        Status       = 'Clean'
        Timestamp    = (Get-Date).ToUniversalTime()
    }
}
```

Each decision row already carries `fsi_ttlexpiresat`; each coverage-gap row carries `fsi_retainuntil` (the engine's `-RetentionDays`, default 183). For the FINRA 4511 six-year horizon, set `-RetentionDays` on the evaluation run accordingly **and** confirm the SIEM/archive retention policy — Dataverse and directory-native retention are far shorter than six years, so the SIEM/records archive is the system of record (defect 0.9).

### 10.2 SIEM forwarding

```powershell
function Export-Agt227SiemBatch {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ResultPath,
        [Parameter(Mandatory)][string]$SiemDropPath   # Log Analytics ingestion / Event Hub stage / records archive
    )

    $result = Get-Content -LiteralPath $ResultPath -Raw | ConvertFrom-Json
    $batch  = [pscustomobject]@{
        controlId    = '2.27'
        evaluatedAt  = $result.EvaluatedAt
        zeroRatingResolved = $result.ZeroRatingResolved
        decisions    = $result.Decisions
        coverageGaps = $result.CoverageGaps
        forwardedAt  = (Get-Date).ToUniversalTime().ToString('o')
    }
    $batch | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $SiemDropPath -Encoding UTF8

    [pscustomobject]@{
        ControlId  = '2.27'
        Criterion  = 'SiemForwarding'
        Records    = @($result.Decisions).Count + @($result.CoverageGaps).Count
        Destination = $SiemDropPath
        RetentionGuidance = 'Retain >= 6 years (FINRA 4511) / SEC 17a-4(b)(4). Dataverse and directory-native retention are shorter than the examination horizon; the SIEM / records archive is the system of record.'
        Status     = 'Clean'
        Timestamp  = (Get-Date).ToUniversalTime()
    }
}
```

> **Filtering boundary.** Correlation, alerting, deduplication, and long-horizon retention belong to the SIEM and the records archive (pair with Control 1.7). This helper confirms the batch is staged for ingestion; it does not perform server-side filtering. Evidence for criterion 8 is the retention policy configuration plus SIEM ingestion confirmation.

---

## 11. Validation, anti-patterns, and operating cadence

### 11.1 Validation harness

```powershell
function Test-Agt227PlaybookHealth {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$EnvironmentUrl)

    $checks = @(
        @{ Name = 'ShellEdition';    Test = { Assert-Agt227Shell; $true } }
        @{ Name = 'ModulesPinned';   Test = { (Install-Agt227ModuleBaseline).Status -eq 'Clean' } }
        @{ Name = 'Prerequisite';    Test = { (Test-Agt227Prerequisite).Status -in @('Clean','NotApplicable') } }
        @{ Name = 'EnginePresent';   Test = { Test-Path "$cbgScripts\Invoke-EntitlementEvaluation.ps1" } }
        @{ Name = 'InventoryPresent'; Test = { Test-Path "$cbgScripts\Get-BillingPolicyInventory.ps1" } }
    )

    foreach ($c in $checks) {
        $ok = $false
        try { $ok = & $c.Test } catch { $ok = $false }
        [pscustomobject]@{ Check = $c.Name; Passed = $ok }
    }
}
```

### 11.2 Anti-patterns table

| # | Anti-pattern | Why it fails | Sanctioned alternative |
|---|--------------|--------------|------------------------|
| 11.1 | Treating an empty entitlement result as `Clean` | A tenant with no Copilot licensing or an offline Work IQ feed produces an empty/undecided set | Check `Test-Agt227Prerequisite` and the `FeedMissing` / `unmapped` counts; `NotApplicable` is not `Clean` |
| 11.2 | Inventing a `New-*BillingPolicy` cmdlet for Copilot PAYG/credit policies | No confirmed public create cmdlet exists; `New-SPOAppBillingPolicy` is SharePoint-only | Create via the portal flows in §4; mark any REST create 🔎 until verified |
| 11.3 | Admitting a mail-enabled group into the registry | Violates the admission gate; eligibility silently "works" against the wrong group type | `Test-Agt227GroupAdmission` rejects `mailEnabled` / non-`securityEnabled` |
| 11.4 | Letting `createdIn` override an authoritative `configuredTier` | Forces the `none` agent majority into the stricter license-gated `mcp-cs` arm | `configuredTier` is evaluated first; `createdIn` is fallback only (§6) |
| 11.5 | Reporting a per-agent cap as a hard-stop | The cap write API is unproven; the row records intent only | Keep `EnforcementMode='Detect-and-alert'` and `EnforcementIsHardStop=$false` until a tenant-confirmed write API exists |
| 11.6 | Running coverage-gap after toggling enforcement | `monitorOnly=false` understates the would-be-blocked population | `Get-Agt227CoverageGapReview` rejects any export with a non-monitor row |
| 11.7 | Presenting the credit-rate estimate as an invoice | Reference constants are not billing-accurate | State the estimate caveat; reconcile against the Microsoft 365 admin center / Azure cost reporting |
| 11.8 | Assuming Dataverse/native retention satisfies FINRA 4511 | Native retention is far shorter than six years | Forward to SIEM / records archive; set `-RetentionDays` and the archive policy to the six-year horizon |
| 11.9 | Hardcoding a client secret for unattended runs | Secret sprawl; not least-privilege | Managed-identity-first; client secret is a dev-only legacy fallback |

### 11.3 Operating cadence

| Cadence | Activity | Owner | Section |
|---------|----------|-------|---------|
| **Daily** | Run the entitlement evaluation (default + fail-closed shadow) and persist evidence | AI Administrator | §7, §10 |
| **Daily** | Review per-agent cap breaches surfaced by detect-and-alert | AI Administrator | §8 |
| **Weekly** | Sweep the security-group registry for admission violations | Entra User Admin | §5 |
| **Weekly** | Reconcile policy inventory against the 50 / 10 ceilings | AI Administrator | §4 |
| **Before any enforcement** | Coverage-gap review + would-be-blocked sign-off | AI Governance Lead + Finance / Controller + Business Unit Owner | §9 |
| **Quarterly** | Confirm retention and SIEM forwarding for examination readiness | Compliance Officer | §10 |
| **Quarterly** | Re-verify the remaining 🔎 reference values (per-feature credit rates, tenant ceilings 50/10) against Microsoft documentation, and watch for a public cap-enforcement write API (caps degrade to detect-and-alert until one ships) | AI Governance Lead | §0, §4, §7, §8, §9 |

### 11.4 Hedged language reminder

When documenting findings produced by these helpers, use only the framework's hedged phrasing:

- ✅ "Supports compliance with FINRA 4511 by retaining materialized entitlement decisions and coverage-gap evidence for the examination horizon."
- ✅ "Helps meet SOX 404 ITGC expectations by documenting who is entitled to incur metered spend and recording the approval of cap thresholds."
- ❌ "Ensures compliance with…" / "Guarantees…" / "Will prevent uncontrolled spend" / "Eliminates spend risk" — all overclaim.

Implementation caveat to retain in narrative reports:

> "This control governs the entitlement **decision** and does not, on its own, satisfy any regulation. Implementation requires Microsoft 365 Copilot licensing, at least one consumption-billing policy, and the AI Administrator role. Zero-rating, credit rates, tenant ceilings, the June 16 2026 consumption-billing switch, and the existence of a cap/credit-policy write API should be verified against current Microsoft documentation before enforcement. Organizations should verify their configuration meets their specific obligations."

---

## Cross-references

**Control specification**

- [Control 2.27 — Consumption-Entitlement Governance](../../../controls/pillar-2-management/2.27-consumption-entitlement-governance.md)

**Companion playbooks for this control**

- [Portal Walkthrough](portal-walkthrough.md)
- [Verification & Testing](verification-testing.md)
- [Troubleshooting](troubleshooting.md)

**Companion solution (FSI-AgentGov-Solutions)**

- `copilot-billing-governance/scripts/Invoke-EntitlementEvaluation.ps1` — the switch-on-pathway engine + coverage-gap aggregate
- `copilot-billing-governance/scripts/Get-BillingPolicyInventory.ps1` — PAYG + credit policy read (Dataverse + BAP)
- `copilot-billing-governance/scripts/create_cbg_dataverse_schema.py` — single source of truth for the table / column logical names
- `copilot-billing-governance/docs/entitlement-contract.md` — decision tree, pseudocode, and zero-rating analysis

**Related controls referenced in this playbook**

- [Control 3.5 — Cost Allocation and Budget Tracking](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) — reports the spend this control governs
- [Control 1.18 — Application-Level Authorization and RBAC](../../../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) — functional access is an input
- [Control 1.14 — Data Minimization and Agent Scope Control](../../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) — surface-aware spend scope
- [Control 2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) — third-party AI spend oversight
- [Control 1.7 — Comprehensive Audit Logging & Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — SIEM forwarding and six-year retention

---

*Updated: June 2026 | Version: v1.0 | UI Verification Status: Needs Review — the June 16 2026 Work IQ switch, Licensing Guide footnotes 6 & 7, and the absence of a public cap/credit-policy write API were verified June 2026; still verify the remaining 🔎-flagged figures (per-feature credit rates, $0.01/credit, 25,000-credit pack, tenant ceilings 50/10) before relying on enforcement.*
