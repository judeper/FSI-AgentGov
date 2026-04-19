# Control 1.8 — PowerShell Setup: Runtime Protection and External Threat Detection

**Control:** [1.8 Runtime Protection and External Threat Detection](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md)
**Baseline:** [PowerShell baseline (`_shared/powershell-baseline.md`)](../../_shared/powershell-baseline.md)
**Audience:** M365 administrator at a US financial services organization (FINRA / SEC / GLBA / OCC / Fed SR 11-7 / CFTC oversight) operating Microsoft 365 Copilot, Agent Builder, and Copilot Studio agents.
**Sovereign clouds:** Commercial / GCC / GCC High / DoD — connection helper in [Section 1](#1-pre-flight) and full reference in [Section 11](#11-sovereign-cloud-reference). Several Control 1.8 surfaces (Defender for Cloud Apps AI Agent Protection, Additional Threat Detection webhooks) are **Preview** or **Prerelease** in commercial cloud and have **not** been documented at parity for US Government clouds — see [Section 11](#11-sovereign-cloud-reference) and [Section 12](#12-anti-patterns-what-not-to-do).

**Required modules:**

- `Microsoft.PowerApps.Administration.PowerShell` — pinned per CAB. **Windows PowerShell 5.1 (Desktop edition) only**, per [PowerShell baseline § 2](../../_shared/powershell-baseline.md#2-powershell-edition-and-version-requirements). Provides `Add-PowerAppsAccount`, `Get-AdminPowerAppEnvironment`, `Get-DlpPolicy`.
- `Microsoft.Graph.Authentication` ≥ 2.15.0 — provides `Connect-MgGraph` and `Invoke-MgGraphRequest` for application registration, federated identity credential creation, Defender XDR alerts, and Microsoft Sentinel hunting queries against the beta endpoint.
- `Microsoft.Graph.Applications` ≥ 2.15.0 — typed cmdlets `New-MgApplication`, `Get-MgApplication`, `New-MgApplicationFederatedIdentityCredential`, `Remove-MgApplicationFederatedIdentityCredential`, `Remove-MgApplication`.
- `Microsoft.Graph.Beta.Security` ≥ 2.15.0 — typed cmdlet `Get-MgBetaSecurityAlert_v2` and supporting types for Defender XDR AI agent alerts; this playbook also calls the raw `Invoke-MgGraphRequest` against `/beta/security/runHuntingQuery` to keep schema stable as the surface evolves.
- `ExchangeOnlineManagement` ≥ 3.5.0 — provides `Connect-IPPSSession` and `Search-UnifiedAuditLog` (paged) for the Copilot Studio and Microsoft 365 Copilot audit families.

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), transcript capture, and SHA-256 evidence emission. Snippets below assume you have already complied with that baseline.

!!! danger "READ FIRST — Control 1.8 has FOUR surfaces, TWO portals, and a hard PowerShell ceiling"

    Control 1.8 — *Runtime Protection and External Threat Detection* — covers four distinct runtime-security surfaces for Copilot Studio agents:

    1. **Native Microsoft Defender for Cloud Apps AI Agent Protection** — `Microsoft Defender — Copilot Studio AI Agents` toggle in the **Power Platform Admin Center** plus AI agent inventory, activity logging, and real-time protection in the **Microsoft Defender XDR portal**. Per [Defender for Cloud Apps — AI Agent Protection](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-protection), this surface is **portal-only for configuration**; PowerShell coverage is read-only via the Microsoft Graph beta security alerts endpoint and Microsoft Sentinel KQL.
    2. **Additional Threat Detection — third-party security webhooks** — Power Platform Admin Center → Security → Threat protection → Additional threat detection. Configured by pasting the App ID of an Entra app registration with a **federated identity credential** that PPAC trusts to call out to your security provider on every Copilot Studio agent invocation. Per [Configure an external security provider](https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-provider), the FIC `subject` and `issuer` values are **issued by the Power Platform service and copied from the PPAC UI by the operator** — they are **not** constructible by client-side script.
    3. **Prompt Shields and content moderation (Azure AI Content Safety)** — per-agent settings in **Copilot Studio Maker** at *Settings → Generative AI → Content moderation*. There is **no** Microsoft-supported PowerShell cmdlet that creates, updates, or reads per-agent moderation level. Evidence comes from the audit log (`PromptInjectionDetected`, `ContentSafetyBlock`) and from solution-export inspection.
    4. **Egress / DLP guardrails** — `Get-DlpPolicy`, `New-DlpPolicy`, `Set-DlpPolicy` for **environment-scoped DLP** that constrains the connectors Copilot Studio agents can reach at runtime. This is the only Control 1.8 surface with full PowerShell CRUD, and it is shared with [Control 1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md).

    **What PowerShell *can* do for Control 1.8:**

    - Pre-flight role / license / module / sovereign-endpoint / Managed-Environments / M365 App Connector status.
    - Inventory environments (with the **correct** managed-environment property path), webhook FIC bindings on the registered app, and DLP policies that govern connector egress.
    - **Mutate** the Entra app registration and federated identity credential that backs Additional Threat Detection — but only after the operator has copied the **PPAC-issued `subject` and `issuer`** from the portal.
    - Collect audit-log evidence (`Search-UnifiedAuditLog`, paged) across **two** RecordType families that surface Copilot Studio runtime threat events, and reconcile them.
    - Read Defender XDR AI agent alerts (`/beta/security/alerts_v2`), and run Microsoft Sentinel KQL with the **correct** column name (`EventOriginalType`, **not** `Operation`) on `PowerPlatformAdminActivity`.
    - Roll back partial app-registration creation so a half-configured app does not become orphaned tenant debt.    **What PowerShell *cannot* do for Control 1.8:**

    - Toggle the `Microsoft Defender — Copilot Studio AI Agents` setting in PPAC (portal-only).
    - Bind a registered app as the active Additional Threat Detection provider on an environment (portal-only — operator pastes the App ID into PPAC).
    - Create or read per-agent Prompt Shield strength, content moderation level, or jailbreak-detection toggle (Maker portal only).
    - Configure Defender XDR notification policies, AI agent inventory thresholds, or AISPM dashboard pivots (Defender XDR portal only).

    **Treat this playbook as the *evidence, inventory, app-registration, and reconciliation automation layer* for Control 1.8 — not as a substitute for portal-driven runtime-protection administration.**

---

## 0. Wrong-shell trap (READ FIRST)

Control 1.8 cmdlets live across **four** PowerShell sessions and two PowerShell editions. Running a cmdlet in the wrong session produces either a `CommandNotFoundException` or, worse, **silent zero results that look like clean evidence** — the worst possible outcome under SEC 17a-4(f) and FINRA 4511 record-keeping expectations. Every script block in this playbook is labelled with its required session — do not strip those labels when copying.

| Cmdlet family | Required session | Module | Edition | If you run it in the wrong session |
|---|---|---|---|---|
| `Add-PowerAppsAccount`, `Get-AdminPowerAppEnvironment`, `Get-DlpPolicy`, `New-DlpPolicy`, `Set-DlpPolicy` | `Add-PowerAppsAccount` (Power Platform) | `Microsoft.PowerApps.Administration.PowerShell` | **Windows PowerShell 5.1 (Desktop) only** | From PowerShell 7 (Core), import succeeds but cmdlets silently return null or throw schema-deserialization errors. Per [PowerShell baseline § 2](../../_shared/powershell-baseline.md#2-powershell-edition-and-version-requirements). |
| `New-MgApplication`, `Get-MgApplication`, `New-MgApplicationFederatedIdentityCredential`, `Remove-MgApplicationFederatedIdentityCredential`, `Remove-MgApplication` | `Connect-MgGraph` (Graph v1.0) | `Microsoft.Graph.Applications` | PS 7.2+ (Core) | From `Connect-AzureAD` (deprecated) or with no Graph session, throws `AuthenticationException`. From a Graph session **without** `Application.ReadWrite.All`, throws **403 Insufficient privileges** at mutation time — no rollback unless the script catches and reverses. |
| `Get-MgBetaSecurityAlert_v2`, `Invoke-MgGraphRequest -Uri /beta/security/runHuntingQuery` | `Connect-MgGraph` (Graph beta) | `Microsoft.Graph.Beta.Security`, `Microsoft.Graph.Authentication` | PS 7.2+ (Core) | From a v1.0-only Graph session, returns 404 on beta paths and **silently returns zero alerts** if the typed cmdlet swallows the error. |
| `Search-UnifiedAuditLog` for **Copilot Studio runtime threat events** (`PromptInjectionDetected`, `ContentSafetyBlock`, `JailbreakAttemptDetected`, `ExternalThreatDetectionCallout`) | `Connect-IPPSSession` (Security & Compliance / IPPS) | `ExchangeOnlineManagement` | Both | From `Connect-ExchangeOnline`, the cmdlet exists but **silently misses** Copilot Studio operations indexed only on the IPPS endpoint. |
| `Search-UnifiedAuditLog` for **Microsoft 365 Copilot user-side events** (`CopilotInteraction` RecordType) | `Connect-IPPSSession` (IPPS) | `ExchangeOnlineManagement` | Both | Same as above. **Critical:** `CopilotInteraction` is the M365 Copilot user-prompt audit surface — it is **adjacent to but distinct from** the Copilot Studio runtime threat events. Both are required for full Control 1.8 evidence (see [Section 5](#5-evidence-collection-audit-log-and-runtime-threat-events)). |

> Always assert session and edition state at the top of every script. The `Initialize-Agt18Session` helper in [Section 1](#1-pre-flight) does this for you. The PPAC inventory script (`Get-Agt18Inventory.ps1`) is a **separate Windows PowerShell 5.1 entrypoint** — do not attempt to call it from a PowerShell 7 host.

```powershell
# Session-edition guard — drop this at the top of any PPAC script
if ($PSVersionTable.PSEdition -ne 'Desktop') {
    throw "This script uses Microsoft.PowerApps.Administration.PowerShell, which requires Windows PowerShell 5.1 (Desktop edition). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Run from a 'Windows PowerShell' host (powershell.exe), not 'PowerShell' (pwsh.exe)."
}
```

```powershell
# Session-edition guard — drop this at the top of any Graph / EXO / IPPS script
if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion.Major -lt 7) {
    throw "This script uses Microsoft.Graph and ExchangeOnlineManagement on PowerShell 7+. Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Run from a 'PowerShell' host (pwsh.exe), not 'Windows PowerShell' (powershell.exe)."
}
```

---

## 1. Pre-flight

Every Control 1.8 PowerShell session **must** start with the same nine steps:

1. Pin module versions (CAB-approved): `Microsoft.PowerApps.Administration.PowerShell`, `Microsoft.Graph.Authentication`, `Microsoft.Graph.Applications`, `Microsoft.Graph.Beta.Security`, `ExchangeOnlineManagement`.
2. Resolve sovereign-cloud connection parameters from a single `-Cloud` switch and **emit a clear warning** if the cloud is GCC / GCC High / DoD — Defender for Cloud Apps AI Agent Protection and Additional Threat Detection have **not** been documented at parity in those clouds.
3. Connect to **Power Platform** (Desktop session only; the helper detects edition and skips the PPAC connection from Core sessions, leaving it to a sibling Desktop entrypoint).
4. Connect to **Microsoft Graph** with the read / write scopes required for app-registration + FIC mutation, Defender alert read, and Sentinel hunting query execution.
5. Connect to **IPPS** (Security & Compliance) — Copilot Studio audit operations are IPPS-only.
6. Verify the caller has **Power Platform Administrator** (PPAC enumeration), **Application Administrator** or **Cloud Application Administrator** (Graph app + FIC mutation), and **Audit Reader** (UAL search) directory roles. Surface 403 / role-missing as a **PRE-FLIGHT FAIL**, not a silent skip.
7. Verify the tenant has the licensing required for each surface — External Threat Detection requires **Managed Environments (Power Platform Premium add-on)**; UAL retention beyond 180 days requires **Microsoft 365 E5 Compliance** or the **Audit Premium** add-on. Surface SKU-denied as PRE-FLIGHT FAIL.
8. Verify the **Microsoft 365 App Connector** is healthy in Defender for Cloud Apps (the connector that ingests Copilot Studio agent activity into the AI Agents Inventory).
9. Verify the named test agents exist (`1.8-TEST-Agent-Z1-Control`, `1.8-TEST-Agent-Z2-Control`, `1.8-TEST-Agent-Z3-Control`) for the canary-prompt evidence loop in [Section 7](#7-reconciliation-ual-defender-alerts-webhook-callout-outcomes).

Save the helper below as `Initialize-Agt18Session.ps1` in your evidence-collection module.

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Authentication';  RequiredVersion = '2.15.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Applications';    RequiredVersion = '2.15.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Beta.Security';   RequiredVersion = '2.15.0' }
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement';        RequiredVersion = '3.5.0' }

function Initialize-Agt18Session {
    <#
    .SYNOPSIS
        Pre-flight for Control 1.8 (Runtime Protection and External Threat Detection).
    .DESCRIPTION
        Resolves sovereign endpoint, opens a Microsoft Graph session (v1.0 + beta)
        with the scopes required for app registration, FIC mutation, Defender
        alert read, and Sentinel hunting query execution; opens an IPPS session
        for Copilot Studio audit; asserts module version pins; asserts caller
        directory-role membership; asserts tenant license surface. Read-only —
        no tenant mutation. Returns a session-context PSCustomObject for
        downstream scripts to consume.

        DOES NOT open a Power Platform Admin session — that requires Windows
        PowerShell 5.1 (Desktop edition) and is opened by the sibling Desktop
        helper Initialize-Agt18PpacSession (see Section 3).
    .PARAMETER UserPrincipalName
        UPN used to authenticate to Microsoft Graph and IPPS.
    .PARAMETER Cloud
        Microsoft 365 cloud the tenant is in. Default: Commercial.
    .PARAMETER RequiredDirectoryRoles
        Caller must be assigned at least one of these directory roles. Default
        list covers PPAC enumeration, Graph app mutation, and UAL search.
    .EXAMPLE
        $ctx = Initialize-Agt18Session -UserPrincipalName admin@contoso.com -Cloud GCCHigh
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $UserPrincipalName,
        [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
        [string] $Cloud = 'Commercial',
        [string[]] $RequiredDirectoryRoles = @(
            'Power Platform Administrator',
            'Application Administrator',
            'Cloud Application Administrator',
            'Audit Reader'
        )
    )

    $ErrorActionPreference = 'Stop'

    # 1. Module pin assertion ------------------------------------------------
    $required = @(
        @{ Name = 'Microsoft.Graph.Authentication';  Min = '2.15.0' }
        @{ Name = 'Microsoft.Graph.Applications';    Min = '2.15.0' }
        @{ Name = 'Microsoft.Graph.Beta.Security';   Min = '2.15.0' }
        @{ Name = 'ExchangeOnlineManagement';        Min = '3.5.0'  }
    )
    foreach ($r in $required) {
        $m = Get-Module -ListAvailable -Name $r.Name |
             Sort-Object Version -Descending | Select-Object -First 1
        if (-not $m)                              { throw "Module $($r.Name) not installed. Install pinned version per CAB approval." }
        if ($m.Version -lt [version]$r.Min)       { throw "$($r.Name) $($m.Version) is below the $($r.Min) minimum required for Control 1.8." }
        Import-Module $r.Name -RequiredVersion $m.Version -Force | Out-Null
    }

    # 2. Resolve sovereign endpoints ----------------------------------------
    $endpoint = switch ($Cloud) {
        'Commercial' { @{
            IppsUri    = 'https://ps.compliance.protection.outlook.com/powershell-liveid/'
            Aad        = 'https://login.microsoftonline.com/organizations'
            GraphEnv   = 'Global'
            GraphHost  = 'https://graph.microsoft.com'
            PpacEndpt  = 'prod'
        } }
        'GCC'        { @{
            IppsUri    = 'https://ps.compliance.protection.outlook.com/powershell-liveid/'
            Aad        = 'https://login.microsoftonline.com/organizations'
            GraphEnv   = 'Global'
            GraphHost  = 'https://graph.microsoft.com'
            PpacEndpt  = 'usgov'
        } }
        'GCCHigh'    { @{
            IppsUri    = 'https://ps.compliance.protection.office365.us/powershell-liveid/'
            Aad        = 'https://login.microsoftonline.us/organizations'
            GraphEnv   = 'USGov'
            GraphHost  = 'https://graph.microsoft.us'
            PpacEndpt  = 'usgovhigh'
        } }
        'DoD'        { @{
            IppsUri    = 'https://l5.ps.compliance.protection.office365.us/powershell-liveid/'
            Aad        = 'https://login.microsoftonline.us/organizations'
            GraphEnv   = 'USGovDoD'
            GraphHost  = 'https://dod-graph.microsoft.us'
            PpacEndpt  = 'dod'
        } }
    }

    # 2a. Sovereign-availability warning (CRITICAL — Defender AI Agent Protection
    #     and Additional Threat Detection are documented for Commercial only;
    #     gov-cloud parity is undocumented as of February 2026)
    if ($Cloud -in @('GCC','GCCHigh','DoD')) {
        Write-Warning @"
Control 1.8 has LIMITED documented availability in $Cloud per Microsoft Learn:
  - Defender for Cloud Apps AI Agent Protection (Preview, commercial only):
    https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-protection
  - Additional Threat Detection / Security Webhooks API (Prerelease, commercial only):
    https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-provider
  - Copilot Studio is GA in GCC and GCC High per requirements-licensing-gcc, but
    generative-AI dependencies (Prompt Shields, content moderation) have separate
    availability constraints by cloud.
ZERO ROWS IN $Cloud DOES NOT MEAN A CLEAN TENANT.
Document the gap as a Control 1.8 exception in your control register and apply
compensating controls: Prompt Shields + content moderation (per-agent, Maker
portal), DLP for connector egress (Control 1.4), Audit Premium (Control 1.7),
Communication Compliance (Control 1.10), and Microsoft Sentinel hunting queries
against the Power Platform connector. Reverify gov-cloud availability against
Microsoft Learn before each change window.
"@
    }

    # 3. Open Microsoft Graph session (v1.0 + beta share the same connection)
    #    Scopes:
    #      - Application.ReadWrite.OwnedBy        (least-privilege for FIC scripts)
    #        OR Application.ReadWrite.All         (required for cross-owner FIC)
    #      - Directory.Read.All                    (role-membership pre-flight)
    #      - SecurityAlert.Read.All                (Defender alerts_v2)
    #      - SecurityEvents.Read.All               (Sentinel hunting query)
    #      - ThreatHunting.Read.All                (advanced hunting on /beta/security/runHuntingQuery)
    #      - Organization.Read.All                 (Get-MgSubscribedSku for license pre-flight)
    $mgCtx = Get-MgContext -ErrorAction SilentlyContinue
    $needScopes = @(
        'Application.ReadWrite.All',
        'Directory.Read.All',
        'SecurityAlert.Read.All',
        'SecurityEvents.Read.All',
        'ThreatHunting.Read.All',
        'Organization.Read.All'
    )
    if (-not $mgCtx -or $mgCtx.Environment -ne $endpoint.GraphEnv) {
        Connect-MgGraph -Environment $endpoint.GraphEnv -Scopes $needScopes -NoWelcome | Out-Null
        $mgCtx = Get-MgContext
    }

    # 4. Open IPPS session (idempotent) -------------------------------------
    $existing = Get-ConnectionInformation -ErrorAction SilentlyContinue |
                Where-Object { $_.ConnectionUri -like '*compliance.protection*' -and $_.State -eq 'Connected' }
    if (-not $existing) {
        Connect-IPPSSession `
            -UserPrincipalName $UserPrincipalName `
            -ConnectionUri $endpoint.IppsUri `
            -AzureADAuthorizationEndpointUri $endpoint.Aad | Out-Null
    }

    # 5. Directory-role membership pre-flight (caller must hold AT LEAST ONE)
    #    Per Microsoft Learn — directoryRoles graph endpoint:
    #    https://learn.microsoft.com/en-us/graph/api/directoryrole-list
    $callerId  = (Get-MgContext).Account
    $me        = Invoke-MgGraphRequest -Method GET -Uri "$($endpoint.GraphHost)/v1.0/me" -ErrorAction Stop
    $myMemb    = Invoke-MgGraphRequest -Method GET -Uri "$($endpoint.GraphHost)/v1.0/me/memberOf?`$top=999" -ErrorAction Stop
    $myRoles   = @($myMemb.value | Where-Object { $_.'@odata.type' -eq '#microsoft.graph.directoryRole' } |
                   ForEach-Object { $_.displayName })
    $matched   = $myRoles | Where-Object { $_ -in $RequiredDirectoryRoles }
    if (-not $matched) {
        throw @"
PRE-FLIGHT FAIL: caller $callerId is not assigned any of the directory roles
required for Control 1.8: $($RequiredDirectoryRoles -join ', ').
Caller currently holds: $(($myRoles -join ', '))
Without these roles, queries return zero rows that look identical to a clean
tenant — the worst possible false-clean pattern under SEC 17a-4(f) /
FINRA 4511. Have your Entra Privileged Role Administrator activate the
appropriate role(s) via PIM and re-run.
"@
    }

    # 6. License pre-flight --------------------------------------------------
    #    Managed Environments require the Power Platform Premium add-on. UAL
    #    retention >180 days requires Microsoft 365 E5 Compliance or the Audit
    #    Premium add-on. Per Get-MgSubscribedSku:
    #    https://learn.microsoft.com/en-us/graph/api/subscribedsku-list
    $skus = Get-MgSubscribedSku -ErrorAction Stop
    $hasPremium = [bool]($skus | Where-Object { $_.SkuPartNumber -match 'POWERAPPS_PER_USER|POWER_APPS_PREMIUM|PowerApps_Premium|POWERAPPS_PER_APP' })
    $hasAuditPremium = [bool]($skus | Where-Object { $_.SkuPartNumber -match 'M365_E5_COMPLIANCE|Microsoft_365_E5_Compliance|EQUIVIO_ANALYTICS|AUDIT_PREMIUM' })
    if (-not $hasPremium) {
        Write-Warning "PRE-FLIGHT WARN: tenant does not appear to carry a Power Platform Premium SKU. Managed Environments and Additional Threat Detection require Premium per https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview. Inventory will still run; mutation scripts will surface 403 if Premium is genuinely absent."
    }
    if (-not $hasAuditPremium) {
        Write-Warning "PRE-FLIGHT WARN: tenant does not appear to carry Audit Premium / E5 Compliance. UAL retention is capped at 180 days per https://learn.microsoft.com/en-us/purview/audit-solutions-overview. Evidence runs spanning >180 days WILL return truncated results."
    }

    # 7. Microsoft 365 App Connector health (Defender for Cloud Apps) -------
    #    Read-only via Graph beta security/dataConnectors endpoint where
    #    available; fall back to a documented manual check.
    #    Per https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory
    #    AI Agents Inventory requires the M365 App Connector to be in Connected state.
    try {
        $connectors = Invoke-MgGraphRequest -Method GET `
            -Uri "$($endpoint.GraphHost)/beta/security/dataConnectors" -ErrorAction Stop
        $m365 = @($connectors.value | Where-Object { $_.displayName -match 'Microsoft 365|Office 365' })
        if (-not $m365 -or ($m365 | Where-Object { $_.status -ne 'connected' })) {
            Write-Warning "PRE-FLIGHT WARN: Microsoft 365 App Connector status is not 'connected' for all instances. Defender for Cloud Apps AI Agents Inventory will be empty or stale. Verify in the Defender XDR portal: Settings -> Cloud Apps -> Connected apps -> Microsoft 365."
        }
    } catch {
        Write-Warning "PRE-FLIGHT INFO: dataConnectors endpoint not available on $Cloud or caller lacks SecurityEvents.Read.All. Manually verify Microsoft 365 App Connector status at https://security.microsoft.com -> Settings -> Cloud Apps."
    }

    # 8. Emit session context -----------------------------------------------
    [PSCustomObject]@{
        Cloud             = $Cloud
        Endpoint          = $endpoint
        TenantId          = $mgCtx.TenantId
        Account           = $mgCtx.Account
        DirectoryRolesHeld= $myRoles
        DirectoryRolesMet = $matched
        HasPremium        = $hasPremium
        HasAuditPremium   = $hasAuditPremium
        InitializedUtc    = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

> **Why a separate Desktop entrypoint for PPAC?** `Microsoft.PowerApps.Administration.PowerShell` ships only Windows PowerShell 5.1 binaries. Importing it into PowerShell 7 succeeds (the loader does not block it), but the cmdlets either return null or throw deserialization errors — producing **false-clean** evidence. The `Initialize-Agt18Session` helper above runs in PS 7.2+ for everything Graph and EXO can do; the `Initialize-Agt18PpacSession` helper in [Section 3](#3-inventory-read-only) runs in Windows PowerShell 5.1 for everything PPAC must do.

---

## 2. Coverage boundary — PowerShell vs portal vs Maker

This is the single source of truth for what belongs in PowerShell vs the Power Platform Admin Center, the Microsoft Defender XDR portal, and the Copilot Studio Maker for Control 1.8. **Verify against Microsoft Learn before each change window** — Microsoft has been moving capabilities between surfaces, and the beta Graph endpoints in particular evolve.

| Capability | PowerShell? | Where it lives |
|---|---|---|
| Toggle `Microsoft Defender — Copilot Studio AI Agents` (the native DCA → Copilot Studio integration) | **No** | PPAC → Security → Threat protection → *Microsoft Defender* |
| Toggle `Additional threat detection` (the third-party webhook surface) on a per-environment basis | **No** | PPAC → Security → Threat protection → *Additional threat detection* |
| Paste the Entra App ID for the registered third-party webhook provider into the environment binding | **No** — the App ID is **typed by the operator** into PPAC. PPAC then issues the FIC `subject` and `issuer` strings that the operator copies back into the Entra app registration. | PPAC (paste App ID + copy `subject` / `issuer`) |
| Create the Entra app registration the webhook will run as | **Yes** — `New-MgApplication` | Microsoft Graph |
| Create the federated identity credential on that app, **using the operator-supplied `subject` and `issuer` from PPAC** | **Yes** — `New-MgApplicationFederatedIdentityCredential` | Microsoft Graph |
| Read AI agent inventory (Defender for Cloud Apps AI Agents) | **Yes — read-only.** Microsoft Graph beta `/beta/security/runHuntingQuery` against the `AIAppEvents` schema. No typed cmdlet. | Microsoft Graph beta |
| Read Defender XDR alerts for AI agent runtime threats | **Yes — read-only.** `Get-MgBetaSecurityAlert_v2 -Filter "serviceSource eq 'microsoftDefenderForCloudApps' and category eq 'InitialAccess'"` (and similar). | Microsoft Graph beta |
| Read Microsoft Sentinel logs for Power Platform admin activity | **Yes — read-only.** `Run-MgSecurityHuntingQuery` against the `PowerPlatformAdminActivity` table. **Critical:** the activity-name column is `EventOriginalType`, **not** `Operation`. | Microsoft Sentinel / Graph beta |
| Audit-log evidence stream for Copilot Studio runtime threat events (`PromptInjectionDetected`, `ContentSafetyBlock`, `JailbreakAttemptDetected`, `ExternalThreatDetectionCallout`) and `CopilotInteraction` user-prompt events | **Yes** — `Search-UnifiedAuditLog` (paged) over **two** RecordType families | IPPS PowerShell |
| Per-agent Prompt Shield strength, content moderation level, jailbreak-detection toggle | **No** | Copilot Studio Maker → Settings → Generative AI → Content moderation |
| Environment-scoped DLP for connector egress (the Control-1.8 sliver of DLP) | **Yes** — `Get-DlpPolicy`, `New-DlpPolicy`, `Set-DlpPolicy` | Power Platform Admin (Desktop) |
| Conditional Access policies that constrain who can run AI agents (signal source for AI Agent Protection) | **Read via Graph; write via Graph or Entra portal.** This is **Control 1.2** territory; Control 1.8 only consumes the signal. | Microsoft Graph / Entra portal |
| Rollback of a partial app + FIC creation | **Yes** — `Remove-MgApplicationFederatedIdentityCredential` then `Remove-MgApplication`, with safety guards that confirm the app is the one created by the Configure script (via tag / displayName / app-creation-time-window). | Microsoft Graph |

> **Do not promote PowerShell as a substitute for portal-driven runtime-protection administration.** If a sub-script in this playbook appears to "enable Defender integration" or "set the Additional Threat Detection provider", it is doing something else — most likely creating the app registration that the operator will then bind in PPAC, or reading the audit log for evidence that someone bound a provider in the portal. Document the boundary in every change ticket so reviewers do not expect a PS-based diff.

### 2.1 The webhook contract (what Power Platform sends; what your provider must answer)

Per [Configure an external security provider](https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-provider):

- Power Platform sends an **HTTP POST** to your provider URL on every Copilot Studio agent invocation, authenticated via a federated identity credential whose **`subject` and `issuer`** are issued by the Power Platform service and copied into the Entra app registration by the operator.
- The request body carries the user prompt, agent identifier, environment identifier, and tenant identifier (verify the current schema against Learn — it has changed during the Prerelease window).
- Your provider responds with `allow` or `block` and an optional `reason` string surfaced in the audit log as `ExternalThreatDetectionCallout`.
- The PPAC binding includes an **`errorBehavior`** setting. **Set `errorBehavior = "Block"`** when the provider is part of a regulated control story — otherwise provider downtime causes Copilot Studio to fall back to `allow`, producing exactly the behavior the control was meant to prevent. Document the chosen behavior in your change ticket and reference it from the Control 1.8 exception register.
- The webhook callout is **synchronous** — it sits in the agent invocation latency budget. Per Learn, a typical end-to-end target is sub-second, but **specific SLA timing is variable; depends on provider region and tenant load** — measure for your provider and record in your runtime SLO.

---

## 3. Inventory (read-only)

The PPAC inventory entrypoint runs in **Windows PowerShell 5.1 (Desktop)** because `Microsoft.PowerApps.Administration.PowerShell` requires it. Save as `Get-Agt18Inventory.ps1` and run from `powershell.exe`, not `pwsh.exe`.

```powershell
#Requires -Version 5.1
#Requires -PSEdition Desktop
#Requires -Modules @{ ModuleName = 'Microsoft.PowerApps.Administration.PowerShell'; RequiredVersion = '2.0.198' }

function Initialize-Agt18PpacSession {
    <#
    .SYNOPSIS
        Pre-flight for the PPAC half of Control 1.8 (Power Platform Admin
        cmdlets, which require Windows PowerShell 5.1).
    .DESCRIPTION
        Asserts edition, pins module version, resolves the sovereign
        -Endpoint switch, and opens an Add-PowerAppsAccount session. Read-only.
    #>
    [CmdletBinding()]
    param(
        [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
        [string] $Cloud = 'Commercial'
    )

    $ErrorActionPreference = 'Stop'

    if ($PSVersionTable.PSEdition -ne 'Desktop') {
        throw "Microsoft.PowerApps.Administration.PowerShell requires Windows PowerShell 5.1 (Desktop). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Run from powershell.exe, not pwsh.exe."
    }

    $m = Get-Module -ListAvailable -Name Microsoft.PowerApps.Administration.PowerShell |
         Sort-Object Version -Descending | Select-Object -First 1
    if (-not $m) {
        throw "Microsoft.PowerApps.Administration.PowerShell is not installed. Install the CAB-pinned version: Install-Module Microsoft.PowerApps.Administration.PowerShell -RequiredVersion <pinned> -Scope CurrentUser."
    }
    Import-Module $m.Name -RequiredVersion $m.Version -Force

    $ppacEndpoint = switch ($Cloud) {
        'Commercial' { 'prod' }
        'GCC'        { 'usgov' }
        'GCCHigh'    { 'usgovhigh' }
        'DoD'        { 'dod' }
    }

    Add-PowerAppsAccount -Endpoint $ppacEndpoint | Out-Null
    [PSCustomObject]@{
        Cloud         = $Cloud
        PpacEndpoint  = $ppacEndpoint
        ModuleVersion = $m.Version.ToString()
        Edition       = $PSVersionTable.PSEdition
        InitializedUtc= (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

### 3.1 Environment inventory with the *correct* managed-environments property path

The most common false-clean pattern in Control 1.8 inventory is reading the wrong property to detect Managed Environments. The current Microsoft.PowerApps.Administration.PowerShell schema exposes the managed-environment governance configuration under `Properties.governanceConfiguration` — **not** `Properties.protectionLevel` directly on the environment object. **Reverify the property path against the pinned module version before each change window** — Microsoft has refactored this object more than once.

```powershell
# Session: Add-PowerAppsAccount (Desktop)
function Get-Agt18EnvironmentInventory {
    <#
    .SYNOPSIS
        Read-only inventory of every Power Platform environment with the
        Managed Environments and Additional Threat Detection signals needed
        for Control 1.8.
    .DESCRIPTION
        Reads governanceConfiguration.protectionLevel (NOT properties.protectionLevel),
        captures the Additional Threat Detection binding if present in the
        environment-properties bag, and emits JSON + CSV with SHA-256 sidecars.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $OutputDirectory
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $runId = [guid]::NewGuid().Guid
    Start-Transcript -Path (Join-Path $OutputDirectory "transcript-env-inventory-$ts.log") -IncludeInvocationHeader

    try {
        $envs = Get-AdminPowerAppEnvironment

        $rows = foreach ($e in $envs) {
            $gov = $null
            if ($e.Internal.properties.PSObject.Properties.Name -contains 'governanceConfiguration') {
                $gov = $e.Internal.properties.governanceConfiguration
            }
            elseif ($e.Properties.PSObject.Properties.Name -contains 'governanceConfiguration') {
                $gov = $e.Properties.governanceConfiguration
            }

            $protectionLevel = $null
            if ($gov) { $protectionLevel = $gov.protectionLevel }

            # Additional Threat Detection binding (when present, surfaces under
            # security.threatProtection or threatProtection in the env properties
            # bag — verify the path against your pinned module version)
            $atd = $null
            foreach ($candidate in @('security.threatProtection','threatProtection','additionalThreatDetection')) {
                $val = $e.Internal.properties
                $hit = $true
                foreach ($seg in $candidate.Split('.')) {
                    if ($val -and $val.PSObject.Properties.Name -contains $seg) {
                        $val = $val.$seg
                    } else { $hit = $false; break }
                }
                if ($hit -and $val) { $atd = $val; break }
            }

            [PSCustomObject]@{
                DisplayName         = $e.DisplayName
                EnvironmentName     = $e.EnvironmentName
                EnvironmentType     = $e.EnvironmentType
                Location            = $e.Location
                IsManagedEnvironment= ($protectionLevel -in @('Standard','Basic','Custom'))
                ProtectionLevel     = $protectionLevel
                AdditionalThreatDetection = ($atd | ConvertTo-Json -Depth 6 -Compress)
                CreatedTime         = $e.CreatedTime
            }
        }

        $jsonPath = Join-Path $OutputDirectory "env-inventory-$ts.json"
        $csvPath  = Join-Path $OutputDirectory "env-inventory-$ts.csv"
        $rows | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath -Encoding UTF8
        $rows | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

        $jsonHash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        $csvHash  = (Get-FileHash -Path $csvPath  -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $jsonHash -Encoding ASCII
        Set-Content -Path "$csvPath.sha256"  -Value $csvHash  -Encoding ASCII

        $manifest = [PSCustomObject]@{
            runId          = $runId
            control        = '1.8'
            artifact       = 'env-inventory'
            modulePin      = (Get-Module Microsoft.PowerApps.Administration.PowerShell).Version.ToString()
            ppacEndpoint   = (Get-PowerAppsAccount).Endpoint
            runner         = "$env:USERDOMAIN\$env:USERNAME"
            outputs        = @(
                @{ file = (Split-Path $jsonPath -Leaf); sha256 = $jsonHash; bytes = (Get-Item $jsonPath).Length }
                @{ file = (Split-Path $csvPath  -Leaf); sha256 = $csvHash;  bytes = (Get-Item $csvPath ).Length }
            )
            rowCount       = ($rows | Measure-Object).Count
            generatedUtc   = (Get-Date).ToUniversalTime().ToString('o')
        }
        $manifest | ConvertTo-Json -Depth 6 |
            Set-Content -Path (Join-Path $OutputDirectory "manifest-env-inventory-$ts.json") -Encoding UTF8

        $manifest
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

### 3.2 DLP policy inventory (the Control-1.8 sliver of DLP)

`Get-DlpPolicy` returns every Power Platform DLP policy in the tenant. For Control 1.8 we care about the policies that constrain **connector egress** for the environments hosting Copilot Studio agents — the runtime guardrail that prevents an agent from being prompt-injected into reaching a non-business connector at request time.

```powershell
# Session: Add-PowerAppsAccount (Desktop)
function Get-Agt18DlpInventory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $OutputDirectory
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'
    $runId = [guid]::NewGuid().Guid
    Start-Transcript -Path (Join-Path $OutputDirectory "transcript-dlp-inventory-$ts.log") -IncludeInvocationHeader

    try {
        $policies = Get-DlpPolicy
        $rows = foreach ($p in $policies.value) {
            [PSCustomObject]@{
                Name              = $p.displayName
                PolicyName        = $p.name
                Type              = $p.environmentType
                CreatedBy         = $p.createdBy.userPrincipalName
                CreatedTime       = $p.createdTime
                LastModifiedTime  = $p.lastModifiedTime
                EnvironmentCount  = ($p.environments | Measure-Object).Count
                BusinessGroup     = ($p.connectorGroups | Where-Object { $_.classification -eq 'Confidential' }).connectors.Count
                NonBusinessGroup  = ($p.connectorGroups | Where-Object { $_.classification -eq 'General'      }).connectors.Count
                BlockedGroup      = ($p.connectorGroups | Where-Object { $_.classification -eq 'Blocked'      }).connectors.Count
            }
        }

        $jsonPath = Join-Path $OutputDirectory "dlp-inventory-$ts.json"
        $csvPath  = Join-Path $OutputDirectory "dlp-inventory-$ts.csv"
        $policies | ConvertTo-Json -Depth 12 | Set-Content -Path $jsonPath -Encoding UTF8
        $rows     | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

        $jsonHash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        $csvHash  = (Get-FileHash -Path $csvPath  -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $jsonHash -Encoding ASCII
        Set-Content -Path "$csvPath.sha256"  -Value $csvHash  -Encoding ASCII

        [PSCustomObject]@{
            runId        = $runId
            control      = '1.8'
            artifact     = 'dlp-inventory'
            outputs      = @(
                @{ file = (Split-Path $jsonPath -Leaf); sha256 = $jsonHash; bytes = (Get-Item $jsonPath).Length }
                @{ file = (Split-Path $csvPath  -Leaf); sha256 = $csvHash;  bytes = (Get-Item $csvPath ).Length }
            )
            rowCount     = ($rows | Measure-Object).Count
            generatedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

### 3.3 Webhook FIC binding inventory

For each Entra app registration tagged as a Copilot Studio webhook provider (we recommend tag `fsi:control:1.8:webhook-provider` — set on creation in [Section 4](#4-mutation-app-registration-federated-identity-credential)), enumerate the federated identity credentials and report on `subject` / `issuer` mismatch with the PPAC-issued values.

```powershell
# Session: Connect-MgGraph (PS 7+)
function Get-Agt18WebhookFicInventory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $OutputDirectory,
        [string] $Tag = 'fsi:control:1.8:webhook-provider'
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    Start-Transcript -Path (Join-Path $OutputDirectory "transcript-fic-inventory-$ts.log") -IncludeInvocationHeader

    try {
        $apps = Get-MgApplication -Filter "tags/any(t:t eq '$Tag')" -All -ErrorAction Stop
        $rows = foreach ($a in $apps) {
            $fics = Get-MgApplicationFederatedIdentityCredential -ApplicationId $a.Id -ErrorAction SilentlyContinue
            foreach ($fic in $fics) {
                [PSCustomObject]@{
                    AppDisplayName = $a.DisplayName
                    AppId          = $a.AppId
                    AppObjectId    = $a.Id
                    FicName        = $fic.Name
                    FicSubject     = $fic.Subject
                    FicIssuer      = $fic.Issuer
                    FicAudiences   = ($fic.Audiences -join ',')
                    Tag            = $Tag
                }
            }
        }

        $jsonPath = Join-Path $OutputDirectory "fic-inventory-$ts.json"
        $csvPath  = Join-Path $OutputDirectory "fic-inventory-$ts.csv"
        $rows | ConvertTo-Json -Depth 6 | Set-Content -Path $jsonPath -Encoding UTF8
        $rows | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

        $jsonHash = (Get-FileHash -Path $jsonPath -Algorithm SHA256).Hash
        $csvHash  = (Get-FileHash -Path $csvPath  -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $jsonHash -Encoding ASCII
        Set-Content -Path "$csvPath.sha256"  -Value $csvHash  -Encoding ASCII

        $rows
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

> **Reconciliation rule.** Every app tagged `fsi:control:1.8:webhook-provider` MUST have at least one FIC whose `issuer` matches the PPAC-issued issuer URL for the bound environment, and whose `subject` matches the PPAC-issued subject string. Any drift between the FIC `subject` / `issuer` and the values still displayed in PPAC means the binding is broken and the webhook will never be invoked — surface as `[ALERT]`.

---
## 4. Mutation — app registration + federated identity credential

> **Operator workflow (READ FIRST).** Per [Configure an external security provider](https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-provider), the binding flow is:
>
> 1. **Run this script** to create the Entra app registration. It emits the new `AppId`.
> 2. **Operator pastes the App ID into PPAC** at *Security → Threat protection → Additional threat detection*. PPAC then **displays the `subject` and `issuer`** that the federated identity credential must use. **Copy them from the PPAC UI.** They are issued by the Power Platform service per environment + tenant + app and **cannot be constructed client-side**.
> 3. **Re-run this script with `-Issuer` and `-Subject`** populated from PPAC. The script creates the FIC bound to those exact values.
> 4. **Operator returns to PPAC** and confirms the binding now shows green / connected. The first agent invocation will exercise the webhook.
>
> Any script that *generates* a `subject` value client-side — for example, by hashing the App ID or concatenating tenant + environment + app GUIDs — is **fabricating credentials**. It will produce a federated identity credential that PPAC will never trust. Earlier drafts of this playbook contained that fabrication. **Do not.**

`Configure-AdditionalThreatDetection.ps1`:

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Authentication';  RequiredVersion = '2.15.0' }
#Requires -Modules @{ ModuleName = 'Microsoft.Graph.Applications';    RequiredVersion = '2.15.0' }

[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string] $UserPrincipalName,
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
    [string] $Cloud = 'Commercial',

    # App registration parameters -------------------------------------------
    [Parameter(Mandatory)] [string] $DisplayName,
    [Parameter(Mandatory)] [string] $OutputDirectory,

    # FIC parameters --- must be COPIED FROM PPAC AFTER FIRST RUN -----------
    # First run: omit -Issuer / -Subject. Script creates the app, emits the
    # AppId, and instructs the operator to paste it into PPAC.
    # Second run: pass -Issuer / -Subject as displayed by PPAC.
    [string] $Issuer,
    [string] $Subject,
    [string[]] $Audiences = @('api://AzureADTokenExchange'),
    [string] $FicName = 'PowerPlatform-AdditionalThreatDetection',

    # App identification on second run --------------------------------------
    [string] $AppObjectId,

    [string] $Tag = 'fsi:control:1.8:webhook-provider'
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Initialize-Agt18Session.ps1')
$ctx = Initialize-Agt18Session -UserPrincipalName $UserPrincipalName -Cloud $Cloud

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'
$runId = [guid]::NewGuid().Guid
$transcriptPath = Join-Path $OutputDirectory "transcript-configure-atd-$ts.log"
Start-Transcript -Path $transcriptPath -IncludeInvocationHeader

try {
    if (-not $AppObjectId) {
        # First run -----------------------------------------------------------
        if ($PSCmdlet.ShouldProcess($DisplayName, "Create new Entra app registration tagged '$Tag'")) {
            $app = New-MgApplication -DisplayName $DisplayName -Tags @($Tag) -SignInAudience 'AzureADMyOrg'
            Write-Host ""
            Write-Host "STEP 1 OF 2 COMPLETE — App registration created." -ForegroundColor Green
            Write-Host "  AppId       : $($app.AppId)"
            Write-Host "  ObjectId    : $($app.Id)"
            Write-Host "  DisplayName : $($app.DisplayName)"
            Write-Host ""
            Write-Host "NEXT STEPS (operator):" -ForegroundColor Yellow
            Write-Host "  1. Open PPAC -> environment -> Settings -> Security -> Threat protection ->"
            Write-Host "     Additional threat detection."
            Write-Host "  2. Paste this AppId: $($app.AppId)"
            Write-Host "  3. PPAC will display an Issuer URL and a Subject string."
            Write-Host "  4. Copy them and re-run this script with:"
            Write-Host "       -AppObjectId $($app.Id) -Issuer '<paste from PPAC>' -Subject '<paste from PPAC>'"
            Write-Host ""

            $result = [PSCustomObject]@{
                runId        = $runId
                control      = '1.8'
                step         = '1-of-2'
                appId        = $app.AppId
                appObjectId  = $app.Id
                displayName  = $app.DisplayName
                tag          = $Tag
                generatedUtc = (Get-Date).ToUniversalTime().ToString('o')
            }
            $resultPath = Join-Path $OutputDirectory "configure-atd-step1-$ts.json"
            $result | ConvertTo-Json -Depth 4 | Set-Content -Path $resultPath -Encoding UTF8
            $resultHash = (Get-FileHash -Path $resultPath -Algorithm SHA256).Hash
            Set-Content -Path "$resultPath.sha256" -Value $resultHash -Encoding ASCII
        }
        return
    }

    # Second run --------------------------------------------------------------
    if (-not $Issuer)  { throw "Second run requires -Issuer (copied from PPAC after pasting AppId)." }
    if (-not $Subject) { throw "Second run requires -Subject (copied from PPAC after pasting AppId)." }

    $app = Get-MgApplication -ApplicationId $AppObjectId -ErrorAction Stop
    if ($Tag -notin @($app.Tags)) {
        throw "App $($app.AppId) is missing the safety tag '$Tag'. Refusing to mutate an app this script did not create. If this app was created out-of-band, add the tag manually after verifying provenance, or run with a fresh app."
    }

    # Idempotence: if a FIC with the same Name + Subject + Issuer already exists, skip.
    $existing = Get-MgApplicationFederatedIdentityCredential -ApplicationId $AppObjectId -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -eq $FicName -and $_.Subject -eq $Subject -and $_.Issuer -eq $Issuer }
    if ($existing) {
        Write-Host "[NO-CHANGE] FIC '$FicName' already exists with matching Subject + Issuer." -ForegroundColor Cyan
    }
    elseif ($PSCmdlet.ShouldProcess("App $($app.AppId)", "Create federated identity credential '$FicName' with Subject='$Subject' Issuer='$Issuer'")) {
        $fic = New-MgApplicationFederatedIdentityCredential -ApplicationId $AppObjectId -BodyParameter @{
            name      = $FicName
            issuer    = $Issuer
            subject   = $Subject
            audiences = $Audiences
        }
        Write-Host "STEP 2 OF 2 COMPLETE — FIC created." -ForegroundColor Green
        Write-Host "  FIC Name : $($fic.Name)"
        Write-Host "  Issuer   : $($fic.Issuer)"
        Write-Host "  Subject  : $($fic.Subject)"
    }

    $result = [PSCustomObject]@{
        runId        = $runId
        control      = '1.8'
        step         = '2-of-2'
        appId        = $app.AppId
        appObjectId  = $app.Id
        ficName      = $FicName
        ficIssuer    = $Issuer
        ficSubject   = $Subject
        ficAudiences = $Audiences
        generatedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
    $resultPath = Join-Path $OutputDirectory "configure-atd-step2-$ts.json"
    $result | ConvertTo-Json -Depth 4 | Set-Content -Path $resultPath -Encoding UTF8
    $resultHash = (Get-FileHash -Path $resultPath -Algorithm SHA256).Hash
    Set-Content -Path "$resultPath.sha256" -Value $resultHash -Encoding ASCII

    Write-Host ""
    Write-Host "REMAINING STEPS (operator):" -ForegroundColor Yellow
    Write-Host "  - Return to PPAC and confirm the Additional Threat Detection binding shows green."
    Write-Host "  - Set errorBehavior = 'Block' if this is a regulated control story."
    Write-Host "  - Run a canary prompt against a test agent and confirm one ExternalThreatDetectionCallout"
    Write-Host "    row appears in the unified audit log within 15 minutes (Section 5)."
}
finally {
    Stop-Transcript | Out-Null
}
```

> Module pin assertion lives inside `Initialize-Agt18Session`. The transcript captures every Graph API URL, status code, and request body — store it under `maintainers-local/tenant-evidence/` and reference it from your change ticket.

---

## 5. Evidence collection — audit log and runtime threat events

The Copilot Studio runtime threat surface produces audit events in **two RecordType families**:

- `CopilotStudio` — the dedicated Copilot Studio audit family. Per [Copilot Studio admin logging](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio), this family carries operations such as `PromptInjectionDetected`, `ContentSafetyBlock`, `JailbreakAttemptDetected`, and `ExternalThreatDetectionCallout`. **Reverify the operation list against Learn before each change window** — the schema has expanded during the Prerelease window.
- `CopilotInteraction` — the Microsoft 365 Copilot user-prompt audit family. Per [Microsoft 365 Copilot auditing](https://learn.microsoft.com/en-us/purview/audit-copilot), this family carries the user-side prompt + response correlation that pairs with the Copilot Studio runtime threat events.

Always query **both** RecordTypes and reconcile in [Section 7](#7-reconciliation-ual-defender-alerts-webhook-callout-outcomes). Use an **operation-name allow-list** — never regex on English words like `"prompt"` or `"jailbreak"`, which trips on user content and produces both false positives and false negatives.

`Collect-RuntimeEvidence.ps1` — paged UAL collector with hard-fail at the documented 50 000-row session ceiling. Per [Search-UnifiedAuditLog](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog), `-SessionCommand ReturnLargeSet` returns rows in pages of up to 5 000 each; the same `SessionId` is capped at 50 000 rows total. Going past the ceiling without re-windowing produces silent truncation — the worst possible failure mode for an audit-log evidence script.

```powershell
#Requires -Version 7.2
#Requires -Modules @{ ModuleName = 'ExchangeOnlineManagement'; RequiredVersion = '3.5.0' }

[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $UserPrincipalName,
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
    [string] $Cloud = 'Commercial',
    [Parameter(Mandatory)] [datetime] $StartUtc,
    [Parameter(Mandatory)] [datetime] $EndUtc,
    [Parameter(Mandatory)] [string]   $OutputDirectory,
    [string[]] $RuntimeOperations = @(
        'PromptInjectionDetected',
        'ContentSafetyBlock',
        'JailbreakAttemptDetected',
        'ExternalThreatDetectionCallout'
    )
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Initialize-Agt18Session.ps1')
$ctx = Initialize-Agt18Session -UserPrincipalName $UserPrincipalName -Cloud $Cloud

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$ts    = Get-Date -Format 'yyyyMMddTHHmmssZ'
$runId = [guid]::NewGuid().Guid
Start-Transcript -Path (Join-Path $OutputDirectory "transcript-collect-$ts.log") -IncludeInvocationHeader

function Invoke-Agt18PagedSearch {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]   $RecordType,
        [Parameter(Mandatory)] [datetime] $StartUtc,
        [Parameter(Mandatory)] [datetime] $EndUtc,
        [string[]] $Operations
    )

    $sessionId   = [guid]::NewGuid().Guid
    $rows        = New-Object System.Collections.Generic.List[object]
    $pages       = 0
    $maxPages    = 10              # 10 pages * 5000 rows = 50,000-row session ceiling
    $resultSize  = 5000

    do {
        $pages++
        $page = Search-UnifiedAuditLog `
            -StartDate $StartUtc -EndDate $EndUtc `
            -RecordType $RecordType `
            -Operations $Operations `
            -SessionId $sessionId -SessionCommand ReturnLargeSet `
            -ResultSize $resultSize
        if ($page) { $rows.AddRange($page) }
    } while ($page -and $page.Count -eq $resultSize -and $pages -lt $maxPages)

    if ($pages -ge $maxPages -and $page.Count -eq $resultSize) {
        throw "PAGE-CEILING HIT: Search-UnifiedAuditLog SessionId $sessionId returned $($rows.Count) rows over $pages pages of $resultSize and is still saturated. The 50,000-row session ceiling is in effect; re-run with a narrower [-StartUtc, -EndUtc] window. DO NOT attempt to continue the same session — silent truncation is the documented failure mode."
    }

    [PSCustomObject]@{
        RecordType      = $RecordType
        Rows            = $rows
        Pages           = $pages
        SessionId       = $sessionId
        Saturated       = ($pages -ge $maxPages -and $page.Count -eq $resultSize)
    }
}

try {
    $copilotStudio       = Invoke-Agt18PagedSearch -RecordType 'CopilotStudio'      -StartUtc $StartUtc -EndUtc $EndUtc -Operations $RuntimeOperations
    $copilotInteraction  = Invoke-Agt18PagedSearch -RecordType 'CopilotInteraction' -StartUtc $StartUtc -EndUtc $EndUtc -Operations $RuntimeOperations

    function Save-Agt18AuditPage {
        param($Page, [string]$Stem)
        $jsonPath = Join-Path $OutputDirectory "$Stem-$ts.json"
        $csvPath  = Join-Path $OutputDirectory "$Stem-$ts.csv"
        $Page.Rows | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonPath -Encoding UTF8
        $Page.Rows | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
        $jh = (Get-FileHash $jsonPath -Algorithm SHA256).Hash
        $ch = (Get-FileHash $csvPath  -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $jh -Encoding ASCII
        Set-Content -Path "$csvPath.sha256"  -Value $ch -Encoding ASCII
        @(
            @{ file = (Split-Path $jsonPath -Leaf); sha256 = $jh; bytes = (Get-Item $jsonPath).Length }
            @{ file = (Split-Path $csvPath  -Leaf); sha256 = $ch; bytes = (Get-Item $csvPath ).Length }
        )
    }

    $outputs  = @()
    $outputs += Save-Agt18AuditPage -Page $copilotStudio      -Stem 'ual-copilot-studio'
    $outputs += Save-Agt18AuditPage -Page $copilotInteraction -Stem 'ual-copilot-interaction'

    $manifest = [PSCustomObject]@{
        runId           = $runId
        control         = '1.8'
        artifact        = 'runtime-evidence'
        tenantId        = $ctx.TenantId
        cloud           = $ctx.Cloud
        runner          = $ctx.Account
        startUtc        = $StartUtc.ToUniversalTime().ToString('o')
        endUtc          = $EndUtc.ToUniversalTime().ToString('o')
        params          = @{
            recordTypes = @('CopilotStudio','CopilotInteraction')
            operations  = $RuntimeOperations
        }
        outputs         = $outputs
        rowCount        = ($copilotStudio.Rows.Count + $copilotInteraction.Rows.Count)
        pagesConsumed   = ($copilotStudio.Pages + $copilotInteraction.Pages)
        sessionsCopilotStudio      = $copilotStudio.SessionId
        sessionsCopilotInteraction = $copilotInteraction.SessionId
        generatedUtc    = (Get-Date).ToUniversalTime().ToString('o')
    }
    $manifest | ConvertTo-Json -Depth 6 |
        Set-Content -Path (Join-Path $OutputDirectory "manifest-runtime-evidence-$ts.json") -Encoding UTF8

    $manifest
}
finally {
    Stop-Transcript | Out-Null
}
```

> **Why a 50 000-row hard-fail.** Per [Search-UnifiedAuditLog](https://learn.microsoft.com/en-us/powershell/module/exchange/search-unifiedauditlog), the documented session-row ceiling is 50 000. Past this point, additional pages return zero rows even when more records exist — there is no error, just silent truncation. Hard-failing at 10 pages of 5 000 forces the operator to narrow the time window, which keeps the evidence honest. **Do not** "retry" or "continue" past the ceiling within the same `SessionId`.

---

## 6. Evidence collection — Defender XDR alerts (read-only, Graph beta)

Defender for Cloud Apps surfaces AI agent runtime alerts in `/beta/security/alerts_v2`. Filter on `serviceSource eq 'microsoftDefenderForCloudApps'` and a category list relevant to AI agent threats. **Verify the category and detection-source enumerations against [the alerts_v2 schema on Learn](https://learn.microsoft.com/en-us/graph/api/resources/security-alert) before each change window** — Microsoft has been adding categories during the AI Agent Protection Preview.

```powershell
# Session: Connect-MgGraph (PS 7+)
function Get-Agt18DefenderAlerts {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [datetime] $StartUtc,
        [Parameter(Mandatory)] [datetime] $EndUtc,
        [Parameter(Mandatory)] [string]   $OutputDirectory,
        [string] $GraphHost = 'https://graph.microsoft.com'
    )

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'
    Start-Transcript -Path (Join-Path $OutputDirectory "transcript-defender-$ts.log") -IncludeInvocationHeader

    try {
        $startIso = $StartUtc.ToUniversalTime().ToString('o')
        $endIso   = $EndUtc.ToUniversalTime().ToString('o')
        $filter   = "serviceSource eq 'microsoftDefenderForCloudApps' and createdDateTime ge $startIso and createdDateTime le $endIso"
        $uri      = "$GraphHost/beta/security/alerts_v2?`$filter=$([uri]::EscapeDataString($filter))&`$top=200"

        $rows = New-Object System.Collections.Generic.List[object]
        do {
            $resp = Invoke-MgGraphRequest -Method GET -Uri $uri -ErrorAction Stop
            if ($resp.value) { $rows.AddRange($resp.value) }
            $uri = $resp.'@odata.nextLink'
        } while ($uri)

        $jsonPath = Join-Path $OutputDirectory "defender-alerts-$ts.json"
        $rows | ConvertTo-Json -Depth 12 | Set-Content -Path $jsonPath -Encoding UTF8
        $hash = (Get-FileHash $jsonPath -Algorithm SHA256).Hash
        Set-Content -Path "$jsonPath.sha256" -Value $hash -Encoding ASCII

        [PSCustomObject]@{
            File         = $jsonPath
            Sha256       = $hash
            RowCount     = $rows.Count
            generatedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
    finally {
        Stop-Transcript | Out-Null
    }
}
```

> **OData-injection prevention.** The `$filter` value is built from datetimes, not from caller-supplied strings, so this query is safe by construction. If you extend the script with a `-AppId` or `-EnvironmentId` parameter, validate it with `[ValidatePattern('^[0-9a-fA-F-]{36}$')]` on the parameter declaration before interpolating it into a `$filter` clause — concatenating an unvalidated string into an OData filter is the same attack class as SQL injection.

---

## 7. Reconciliation — UAL ↔ Defender alerts ↔ webhook callout outcomes

For every Copilot Studio agent invocation that triggers a runtime threat detection, you should see **three correlated artifacts** within roughly 15 minutes (specific propagation timing is variable; depends on tenant load and cloud — measure for your tenant and record in your Control 1.8 SLO):

1. A `CopilotStudio` audit record with `Operation` in your runtime allow-list.
2. (Where the Defender for Cloud Apps AI Agent Protection toggle is on) a Defender XDR alert with `serviceSource = microsoftDefenderForCloudApps` and an AI-agent-related category.
3. (Where Additional Threat Detection is bound) an `ExternalThreatDetectionCallout` audit record with the bound provider's response — `allow` or `block` plus optional `reason`.

The reconciliation script joins these three streams on `correlationId` (Copilot Studio populates this on every invocation) and emits an exception report for any invocation that produced a runtime threat in one stream but not the others. Use it as the canary-loop verifier after every change window:

```powershell
function Compare-Agt18Reconciliation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $UalCopilotStudioJson,
        [Parameter(Mandatory)] [string] $DefenderAlertsJson,
        [Parameter(Mandatory)] [string] $OutputDirectory
    )

    $ErrorActionPreference = 'Stop'
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'

    $ualRows = Get-Content $UalCopilotStudioJson -Raw | ConvertFrom-Json
    $alerts  = Get-Content $DefenderAlertsJson  -Raw | ConvertFrom-Json

    # Normalize correlation IDs --------------------------------------------
    $ualByCorr = @{}
    foreach ($r in $ualRows) {
        $audit = $r.AuditData | ConvertFrom-Json -ErrorAction SilentlyContinue
        $corr  = $audit.correlationId
        if ($corr) { $ualByCorr[$corr] = $r }
    }
    $alertCorrs = @{}
    foreach ($a in $alerts) {
        foreach ($e in @($a.evidence)) {
            if ($e.correlationId) { $alertCorrs[$e.correlationId] = $a }
        }
    }

    $orphanUal    = $ualByCorr.Keys | Where-Object { -not $alertCorrs.ContainsKey($_) }
    $orphanAlert  = $alertCorrs.Keys | Where-Object { -not $ualByCorr.ContainsKey($_) }

    $report = [PSCustomObject]@{
        ualCount             = $ualByCorr.Count
        defenderAlertCount   = $alertCorrs.Count
        ualRowsWithoutAlert  = @($orphanUal)
        alertsWithoutUalRow  = @($orphanAlert)
        generatedUtc         = (Get-Date).ToUniversalTime().ToString('o')
    }
    $reportPath = Join-Path $OutputDirectory "reconciliation-$ts.json"
    $report | ConvertTo-Json -Depth 6 | Set-Content -Path $reportPath -Encoding UTF8
    $reportHash = (Get-FileHash $reportPath -Algorithm SHA256).Hash
    Set-Content -Path "$reportPath.sha256" -Value $reportHash -Encoding ASCII

    $report
}
```

> **Surface results as `[OK]` / `[WARN]` / `[ALERT]` based on the reconciliation report**, not as hardcoded `[PASS]`. `[OK]` means orphan counts are within tolerance for the tenant's known noise floor; `[WARN]` means orphans exceed tolerance but no high-severity Defender alerts are involved; `[ALERT]` means orphan Defender alerts of `high` severity exist (the most common indicator of a stale UAL ingestion or a missed Copilot Studio audit).

---

## 8. Microsoft Sentinel KQL — `EventOriginalType`, NOT `Operation`

If the tenant streams Power Platform admin activity into Microsoft Sentinel via the [Microsoft Power Platform connector for Microsoft Sentinel](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors/microsoft-power-platform), Control 1.8 evidence can also be queried via Sentinel KQL. Per the [`PowerPlatformAdminActivity` table reference](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/powerplatformadminactivity), the operation-name column is **`EventOriginalType`** — not `Operation`. Earlier drafts of this playbook used `Operation` and silently returned zero rows. **Do not.**

```kql
// All Copilot Studio runtime threat events surfaced in PowerPlatformAdminActivity
PowerPlatformAdminActivity
| where TimeGenerated >= ago(7d)
| where EventOriginalType in (
    "PromptInjectionDetected",
    "ContentSafetyBlock",
    "JailbreakAttemptDetected",
    "ExternalThreatDetectionCallout"
  )
| project TimeGenerated, EventOriginalType, EnvironmentName, AgentId = ResourceId,
          UserPrincipalName, ResultType, CorrelationId, AdditionalProperties
| order by TimeGenerated desc
```

Pair the table query with a Defender XDR alert join to surface high-severity, unreviewed AI agent alerts in the same window:

```kql
// Defender XDR AI agent alerts of high severity in the last 7 days
SecurityAlert
| where TimeGenerated >= ago(7d)
| where ProductName == "Microsoft Defender for Cloud Apps"
| where Severity == "High"
| where AlertName has_any ("AI agent", "Copilot agent", "Prompt injection", "Jailbreak")
| extend Correlation = tostring(parse_json(ExtendedProperties).CorrelationId)
| join kind=leftouter (
    PowerPlatformAdminActivity
    | where TimeGenerated >= ago(7d)
    | where EventOriginalType in (
        "PromptInjectionDetected",
        "ContentSafetyBlock",
        "JailbreakAttemptDetected",
        "ExternalThreatDetectionCallout"
      )
    | project Correlation = CorrelationId, EventOriginalType, EnvironmentName
  ) on Correlation
| project TimeGenerated, AlertName, Severity, EnvironmentName, EventOriginalType, Correlation, AlertLink
| order by TimeGenerated desc
```

> The KQL queries also run through the Graph beta hunting endpoint when the tenant does not have Sentinel: `Invoke-MgGraphRequest -Method POST -Uri "$($ctx.Endpoint.GraphHost)/beta/security/runHuntingQuery" -Body (@{ Query = $kql } | ConvertTo-Json)`. The schema is the same; the column-name correctness rule (`EventOriginalType`, not `Operation`) is identical.

---

## 9. Manifest pattern (recap)

Every script in this playbook emits a `manifest-*.json` next to its outputs. The manifest schema is the same across Controls 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.12 — re-use the parser in `_shared/parse-manifest.ps1`:

```jsonc
{
  "runId":          "9a2c1f30-8d11-4e0a-9c9c-7f2c6d9b8e21",
  "control":        "1.8",
  "artifact":       "runtime-evidence",
  "tenantId":       "00000000-0000-0000-0000-000000000000",
  "cloud":          "Commercial",
  "runner":         "admin@contoso.com",
  "startUtc":       "2026-02-01T00:00:00Z",
  "endUtc":         "2026-02-08T00:00:00Z",
  "params":         { "recordTypes": ["CopilotStudio","CopilotInteraction"], "operations": ["PromptInjectionDetected", "ContentSafetyBlock", "JailbreakAttemptDetected", "ExternalThreatDetectionCallout"] },
  "outputs":        [ { "file": "ual-copilot-studio-20260208T010203Z.json", "sha256": "…", "bytes": 12345 } ],
  "rowCount":       42,
  "pagesConsumed":  3,
  "generatedUtc":   "2026-02-08T01:02:03Z"
}
```

The `outputs[*].sha256` is what your auditor will check against the sidecar `.sha256` files when validating record integrity. Per SEC 17a-4(f), records held electronically must be retained in a non-rewriteable, non-erasable format — keep the manifests, the JSON / CSV outputs, the `.sha256` sidecars, and the transcripts together in a write-once store (Microsoft Purview Records Management or your equivalent).

---

## 10. Rollback — `Rollback-AdditionalThreatDetection.ps1`

Removes the FIC and the app registration created by `Configure-AdditionalThreatDetection.ps1`. **Never** delete an app the script did not create — the `-Tag` and `-CreatedAfter` safety guards refuse to operate on apps with missing or mismatched provenance.

```powershell
#Requires -Version 7.2
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [Parameter(Mandatory)] [string] $UserPrincipalName,
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')] [string] $Cloud = 'Commercial',
    [Parameter(Mandatory)] [string] $AppObjectId,
    [Parameter(Mandatory)] [string] $OutputDirectory,
    [string] $RequiredTag = 'fsi:control:1.8:webhook-provider'
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Initialize-Agt18Session.ps1')
$ctx = Initialize-Agt18Session -UserPrincipalName $UserPrincipalName -Cloud $Cloud
$ts  = Get-Date -Format 'yyyyMMddTHHmmssZ'
Start-Transcript -Path (Join-Path $OutputDirectory "transcript-rollback-$ts.log") -IncludeInvocationHeader

try {
    $app = Get-MgApplication -ApplicationId $AppObjectId -ErrorAction Stop
    if ($RequiredTag -notin @($app.Tags)) {
        throw "REFUSING TO DELETE: App $($app.AppId) is missing the required safety tag '$RequiredTag'. This script only removes apps it (or a sibling Configure-AdditionalThreatDetection.ps1 run) created. Apps created out-of-band must be removed via a tracked change ticket and a separate, explicit cmdlet — not this script."
    }

    Write-Warning @"
About to remove federated identity credentials AND the app registration for:
  AppId       : $($app.AppId)
  ObjectId    : $($app.Id)
  DisplayName : $($app.DisplayName)
This will BREAK any PPAC Additional Threat Detection binding still pointing at
this AppId. CONFIRM the binding has been removed in PPAC FIRST, otherwise the
next Copilot Studio agent invocation will fail closed (if errorBehavior=Block)
or fall through with no provider check (if errorBehavior=Allow).
"@

    $fics = Get-MgApplicationFederatedIdentityCredential -ApplicationId $AppObjectId -ErrorAction SilentlyContinue
    foreach ($fic in $fics) {
        if ($PSCmdlet.ShouldProcess("App $($app.AppId)", "Remove FIC '$($fic.Name)'")) {
            Remove-MgApplicationFederatedIdentityCredential -ApplicationId $AppObjectId -FederatedIdentityCredentialId $fic.Id -ErrorAction Stop
        }
    }

    if ($PSCmdlet.ShouldProcess("App $($app.AppId)", "Remove app registration")) {
        Remove-MgApplication -ApplicationId $AppObjectId -ErrorAction Stop
    }

    [PSCustomObject]@{
        runId        = [guid]::NewGuid().Guid
        control      = '1.8'
        artifact     = 'rollback'
        appId        = $app.AppId
        appObjectId  = $app.Id
        ficsRemoved  = ($fics | Measure-Object).Count
        generatedUtc = (Get-Date).ToUniversalTime().ToString('o')
    } | ConvertTo-Json -Depth 4 |
        Set-Content -Path (Join-Path $OutputDirectory "rollback-$ts.json") -Encoding UTF8
}
finally {
    Stop-Transcript | Out-Null
}
```

## 10a. Disconnect

Always disconnect at the end of every session. Do **not** wrap with `-ErrorAction SilentlyContinue` — a failed disconnect is a signal worth seeing (it usually means a parallel session is still running, which can produce inconsistent evidence).

```powershell
Disconnect-MgGraph
Disconnect-ExchangeOnline -Confirm:$false
# Power Platform (Desktop session): no documented Remove-PowerAppsAccount; close the host process.
```

---

## 11. Sovereign cloud reference

| Cloud | Connect-MgGraph -Environment | Graph host | IPPS ConnectionUri | AAD authority | PPAC `-Endpoint` | Notes |
|---|---|---|---|---|---|---|
| Commercial | `Global` | `https://graph.microsoft.com` | `https://ps.compliance.protection.outlook.com/powershell-liveid/` | `https://login.microsoftonline.com/organizations` | `prod` | Defender AI Agent Protection in Preview; Additional Threat Detection in Prerelease — verify per change window. |
| GCC | `Global` | `https://graph.microsoft.com` | `https://ps.compliance.protection.outlook.com/powershell-liveid/` | `https://login.microsoftonline.com/organizations` | `usgov` | Same Graph endpoints as Commercial. **Defender AI Agent Protection and Additional Threat Detection availability NOT documented at parity** — apply compensating controls. |
| GCC High | `USGov` | `https://graph.microsoft.us` | `https://ps.compliance.protection.office365.us/powershell-liveid/` | `https://login.microsoftonline.us/organizations` | `usgovhigh` | Distinct Graph + IPPS hosts. Verify Copilot Studio + Defender for Cloud Apps availability against [requirements-licensing-gcc](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-gcc) before each change window. |
| DoD (L5) | `USGovDoD` | `https://dod-graph.microsoft.us` | `https://l5.ps.compliance.protection.office365.us/powershell-liveid/` | `https://login.microsoftonline.us/organizations` | `dod` | Dedicated L5 IPPS host. Generative-AI dependencies have separate availability constraints — reverify per change window. |

Sources:

- [Connect-MgGraph -Environment values](https://learn.microsoft.com/en-us/powershell/microsoftgraph/authentication-commands)
- [Connect-IPPSSession sovereign endpoints](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell)
- [Add-PowerAppsAccount -Endpoint values](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell)
- [Microsoft Copilot Studio licensing requirements (US Government clouds)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-gcc)

> **ZERO ROWS IN A GOV CLOUD DOES NOT MEAN A CLEAN TENANT.** Several Control 1.8 surfaces are not available in GCC / GCC High / DoD as of February 2026. A successful run that returns no Defender alerts and no `CopilotStudio` audit rows in those clouds means *the surfaces are not active*, not *the tenant is clean*. Document the gap and apply compensating controls.

---

## 12. Anti-patterns — what NOT to do

Every item in this list maps to a real failure mode discovered during Control 1.8 review.

1. **Constructing FIC `subject` or `issuer` client-side.** PPAC issues these per environment + tenant + app. Any script that hashes the App ID, concatenates GUIDs, or generates a "predictable" subject is **fabricating credentials** — PPAC will never trust them. Always pass `-Issuer` and `-Subject` from the PPAC UI on the second run of `Configure-AdditionalThreatDetection.ps1`.
2. **`Search-UnifiedAuditLog` without `-SessionId` + `-SessionCommand ReturnLargeSet`.** A single-shot call returns at most 5 000 rows and **silently truncates** beyond that. The paged pattern in [Section 5](#5-evidence-collection-audit-log-and-runtime-threat-events) is non-negotiable for evidence runs.
3. **Continuing past the 50 000-row session ceiling.** Per Learn, the same `SessionId` is capped at 50 000 rows. Past that point, additional calls return zero rows with no error. Hard-fail at 10 pages of 5 000 and force the operator to narrow the time window.
4. **Querying only `RecordType = CopilotInteraction`.** That family carries Microsoft 365 Copilot user-prompt events; it does **not** carry Copilot Studio runtime threat operations. Always query `CopilotStudio` **and** `CopilotInteraction` and reconcile.
5. **Regexing on English words like `prompt` or `jailbreak` instead of an operation-name allow-list.** User content containing those words trips false positives; legitimate detections under operation names you did not enumerate are missed entirely. Use the explicit `-Operations` allow-list and reverify it against Learn before each change window.
6. **Using the wrong KQL column.** `PowerPlatformAdminActivity` exposes activity names under `EventOriginalType`, not `Operation`. The query silently returns zero rows when the column is wrong — there is no schema error.
7. **Hard-coded `[PASS]` / `[FAIL]` banners.** Verification scripts that always print `[PASS]` regardless of state are evidence theatre. Surface `[OK]` / `[WARN]` / `[ALERT]` based on the reconciliation report and the orphan-alert tolerance documented in your Control 1.8 SLO.
8. **Reading `$env.Properties.protectionLevel` to detect Managed Environments.** The current schema exposes the value at `$env.Internal.properties.governanceConfiguration.protectionLevel` (or `$env.Properties.governanceConfiguration.protectionLevel` depending on module version). The wrong path returns `$null`, which the script then false-clean reports as "not managed".
9. **Mutation cmdlets without `[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]`.** No `-WhatIf` or `-Confirm` support means the change-management trail is missing. CAB will reject.
10. **Removing app registrations without a provenance tag check.** `Remove-MgApplication` is irreversible. The rollback script must refuse to operate on apps without the `fsi:control:1.8:webhook-provider` tag (or whatever tag the Configure script set).
11. **Wrapping `Connect-*` or `Disconnect-*` with `-ErrorAction SilentlyContinue`.** Both signals matter — a failed connect is a sovereign-endpoint or scope problem; a failed disconnect is a parallel-session problem. Suppressing them produces silent drift.
12. **Skipping the role pre-flight.** Without an `Application Administrator` (or higher) role, `New-MgApplication` returns 403 — but a Graph session opened with delegated `Application.ReadWrite.OwnedBy` will sometimes accept the call and create an app the operator cannot manage afterwards. Always assert role membership in `Initialize-Agt18Session`.
13. **Skipping the Microsoft 365 App Connector health check.** Defender for Cloud Apps AI Agents Inventory will be empty or stale if the connector is degraded. Empty inventory looks identical to "no agents in tenant" — false-clean.
14. **Treating commercial-cloud Learn URLs as authoritative for GCC / GCC High / DoD.** Several Control 1.8 surfaces have no documented gov-cloud parity. Reverify per cloud against the [GCC requirements page](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-gcc) and, where the surface is unavailable, document the gap and apply compensating controls.
15. **Skipping transcript capture.** `Start-Transcript` + `-IncludeInvocationHeader` is what your auditor will read when reconstructing what happened in the session. It is not optional for mutation scripts.

---

## 13. Cross-links

| Related control | Why it matters for Control 1.8 |
|---|---|
| [1.4 — Advanced Connector Policies (ACP)](../../../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Connector-level controls that constrain which connectors a Copilot Studio agent can invoke at runtime. |
| [1.5 — Data Loss Prevention (DLP) and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | Environment-scoped DLP referenced in [Section 3.2](#32-dlp-policy-inventory-the-control-18-sliver-of-dlp); sensitivity labels feed AI Agent Protection alert evidence. |
| [1.6 — Microsoft Purview DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI surfaces the data-classification posture that AI Agent Protection alerts cite in their evidence. |
| [1.7 — Comprehensive Audit Logging and Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | UAL retention beyond 180 days requires the Audit Premium SKU asserted in the [Section 1 pre-flight](#1-pre-flight). |
| [1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Defines how long Copilot Studio audit, transcript, and Defender alert evidence is retained — pairs with SEC 17a-4(f) record-keeping requirements. |
| [1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | The companion Comms Compliance review surface for human-language threat patterns — pairs with the Control 1.8 runtime threat events. |
| [1.13 — Sensitive Information Types (SITs) and Pattern Recognition](../../../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | SIT detections are evidence inputs to AI Agent Protection alerts and Communication Compliance reviews. |
| [2.7 — Vendor and Third-Party Risk Management](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Third-party security webhook providers bound via Additional Threat Detection are vendors subject to this control's risk-management requirements. |

---

*Updated: February 2026 | Version: v1.4.0*