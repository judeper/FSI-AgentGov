# Control 1.7 — PowerShell Setup: Comprehensive Audit Logging and Compliance Automation

> **Scope.** This playbook automates the **audit capture and preservation plane** for Control 1.7 across **Microsoft Purview Audit (Standard, Premium, and the 10-Year Audit Log Retention add-on), Microsoft 365 Copilot and agent record types (`CopilotInteraction`, `ConnectedAIAppInteraction`, `AIAppInteraction` (PAYG), `MicrosoftCopilotStudio`), Audit pay-as-you-go (PAYG) AI App Interaction enablement, Dataverse per-table auditing for the six Microsoft Copilot Studio entities, the Microsoft Graph audit log API (the strategic forward path as `Search-UnifiedAuditLog` enters maintenance), the Microsoft 365 Substrate content tier reachable through DSPM for AI / eDiscovery Premium / Communication Compliance, and an SEC 17a-4(f)-compatible preservation pipeline into Azure immutable blob storage** in US financial services tenants. It assumes you have already read [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) (referenced below as **BL-§N**) and the parent control specification [`../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).
>
> **What this playbook is.** A reproducible, fail-closed audit-plane harness that (a) pins module / CLI versions; (b) bootstraps **two distinct connections** (Exchange Online and Security & Compliance PowerShell — the same cmdlet name returns different and silently misleading values from the wrong session) plus a Microsoft Graph context for the new Audit Search API and a Power Apps Administration session for Dataverse per-table audit; (c) verifies tenant-level unified audit log ingestion, Audit (Premium) license entitlement, the 10-Year Audit Log Retention add-on, and PAYG opt-in for `AIAppInteraction`; (d) enumerates the four Copilot / agent record types with paginated, large-set, date-windowed search; (e) confirms Dataverse per-entity audit is on for the six Copilot Studio entities (`bot`, `botcomponent`, `botcomponentcollection`, `conversationtranscript`, `aiplugin`, `aipluginauth`) in every applicable environment; (f) verifies a 17a-4(f) preservation pipeline is exporting unified audit results into an attested archive (Azure immutable blob with a *locked* time-based retention policy, or a third-party books-and-records connector); (g) verifies the Sentinel Office 365 connector is ingesting `CopilotInteraction` events end-to-end; and (h) emits a SHA-256-hashed evidence manifest aligned to the Control 3.1 canonical reconciliation schema.
>
> **What this playbook is not.** It is not, by itself, a SEC Rule 17a-4(f)-compliant electronic recordkeeping system. Microsoft 365 Audit (including the 10-year add-on) is **record-CAPTURE operational telemetry**; preservation requires either WORM storage of the books-and-records record set (e.g., Azure immutable blob storage with a time-based retention policy in a *locked* state — Cohasset-attested for SEC 17a-4(f), CFTC 1.31, and FINRA 4511 — see [Microsoft Learn: Immutable storage for Azure blob data](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)) or the audit-trail alternative under the October 2022 amendments to Rule 17a-4(f) (compliance date 3 May 2023). This harness verifies that the export pipeline exists and is healthy; it does not, by itself, *guarantee* attestation, *eliminate* preservation risk, or replace the Designated Executive Officer (DEO) representation or Designated Third Party (DTP) undertaking required under the audit-trail alternative.
>
> **Hedged language reminder.** Output of this harness *supports compliance with* FINRA Rule 4511, FINRA Rule 3110, FINRA RN 24-09 / Rule 3110, SEC Rule 17a-3, SEC Rule 17a-4(b)(4) / 17a-4(f), SOX 302/404, GLBA 501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Fed SR 26-2 (formerly SR 11-7), NIST AI RMF MEASURE 2.7 / GOVERN 1.4, CFTC Rule 1.31, and NYDFS 23 NYCRR 500.06. It does not, by itself, *ensure* a passing examination, *guarantee* completeness of the books-and-records record set, or *eliminate* the risk that a record type is silently re-classified between Audit Standard, Audit Premium, and Audit PAYG between Microsoft releases. Implementation requires that organizations verify Audit Premium licensing, PAYG opt-in scope, and Dataverse audit settings at every change window, and that they treat any preview surface (the Microsoft Graph audit search query API, `agentSignIn`, `MicrosoftServicePrincipalSignInLogs`) as **additive** evidence rather than the sole source of truth.

| Field | Value |
|---|---|
| Control ID | 1.7 |
| Pillar | 1 — Security |
| Playbook | PowerShell Setup |
| PowerShell Edition | 7.4 LTS Core (orchestrator, Graph, Az.Storage); 5.1 Desktop (Power Apps Administration sub-shell for Dataverse audit, JSON-bridged); both Desktop and Core supported for `Connect-ExchangeOnline` and `Connect-IPPSSession` (verify against your CAB-pinned `ExchangeOnlineManagement` version) |
| Cloud | Commercial (Global) |
| Last UI Verified | April 2026 |
| Companion Playbooks | [`portal-walkthrough.md`](portal-walkthrough.md) · `verification-testing.md` (planned) · [`troubleshooting.md`](troubleshooting.md) |
| Related Controls | [1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) · [1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) · [1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) · [2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) · [2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) · [3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) · [3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |

---

## §0 — Wrong-shell trap and audit-plane false-clean defects (READ FIRST)

**The defining fact of Control 1.7.** Audit configuration cmdlets in `ExchangeOnlineManagement` exist in **both** the Exchange Online (`Connect-ExchangeOnline`) and the Security & Compliance (`Connect-IPPSSession`) PowerShell connections, with the **same names** and **different return semantics**. Per Microsoft Learn, `Get-AdminAuditLogConfig.UnifiedAuditLogIngestionEnabled` **always returns `$false` from the Security & Compliance session**, regardless of the actual tenant state, because the property is a property of the Exchange Online configuration object — not the compliance one. A script that does not assert which session it is reading from is producing **audit-grade misinformation**.

A script that ignores this reality produces a **false-clean audit posture** — the worst Control 1.7 outcome. False-clean audit posture means examiners are told records were captured when they were not, breaks SEC 17a-4(b)(4) communications-retention attestation for broker-dealer Copilot rollouts, leaves FINRA Rule 3110 supervisory queues operating on incomplete sets, and invalidates the Cohasset attestation chain that downstream SEC 17a-4(f) preservation depends on.

**Why this section exists.** Eight classes of silent failure produce false-clean audit-plane output in Control 1.7 specifically:

1. **Wrong-shell trap on `Get-AdminAuditLogConfig`.** Always returns `$false` for `UnifiedAuditLogIngestionEnabled` from the Security & Compliance session. Helpers in §3 hard-fail unless the active session URI matches `outlook.office365.(com|us)`.
2. **Invalid `-RecordType` returns zero rows silently.** Earlier playbooks shipped `-RecordType PowerPlatformAdminActivity`; that name is **not** in the `AuditLogRecordType` enumeration. Some module versions silently return zero rows for invalid RecordType values. The canonical names are `MicrosoftCopilotStudio`, `PowerPlatformAdminEnvironment`, `PowerPlatformAdministratorActivity`, `PowerPlatformServiceActivity`, `MicrosoftFlow`, `PowerAppsApp`, `MicrosoftPowerBIAudits`, `CopilotInteraction`, `ConnectedAIAppInteraction`, `AIAppInteraction`. Validate against the live enum at runtime.
3. **`Search-UnifiedAuditLog` `-ResultSize` truncation.** Default `-ResultSize 100`; per-call cap **5,000**; per-session ceiling **50,000**. Single-shot calls silently drop records past those limits. Use `-SessionCommand ReturnLargeSet` with a fresh `-SessionId` per date window, and split windows when the session ceiling is approached.
4. **`Search-UnifiedAuditLog` is in maintenance.** Microsoft has signalled the **Audit Search Graph API** (`/security/auditLog/queries`) as the strategic forward path. `Search-AdminAuditLog` was already deprecated 15 September 2024. New investment should target the Graph API; this playbook ships both paths and labels the legacy one.
5. **Audit Premium silently downgrades to Audit Standard.** If a user does not have an Audit (Premium) entitlement, their `CopilotInteraction` records fall back to **180-day retention** regardless of any custom retention policy. License reconciliation (§4) must be tenant-wide before retention claims.
6. **PAYG record types require explicit opt-in.** `AIAppInteraction` and *some* `ConnectedAIAppInteraction` scenarios (non-Microsoft AI apps surfaced via Connected AI App) fall under [Audit pay-as-you-go billing](https://learn.microsoft.com/en-us/purview/purview-billing-models). Until the PAYG meter is turned on, these records do not flow at all.
7. **Dataverse per-table audit is environment-scoped.** Tenant-level "Start auditing" enables the *capability*; per-table auditing on the six Copilot Studio entities must be enabled **per environment, per table**. A solution-installed entity in a new environment does not inherit table audit settings from the source environment.
8. **Single-credential read+write.** Running this harness with the same service principal that *modifies* audit configuration breaks SOX 404 separation of duties — the principal that produces the evidence could be the principal that altered the configuration the evidence describes. Use a separate `agt17-audit-reader` audit-only principal.

**Top false-clean defects unique to audit-plane automation.**

| # | Defect | What it looks like | How this playbook traps it |
|---|---|---|---|
| 1 | `Get-AdminAuditLogConfig` from `Connect-IPPSSession` | `UnifiedAuditLogIngestionEnabled = False` regardless of truth | §3 `Assert-FsiExoSession` hard-fails on session URI mismatch |
| 2 | `Search-UnifiedAuditLog -RecordType PowerPlatformAdminActivity` | Returns zero rows; exit 0 | §7 enum validation against `[Microsoft.Office.CompliancePolicy.PSCmdlets.AuditRecordType]` |
| 3 | `Search-UnifiedAuditLog` without pagination | Caps at 100 / 5,000 / 50,000 silently | §7 `Search-FsiAuditLogPaged` with `ReturnLargeSet` and date-window splitter |
| 4 | Custom retention policy without per-user Audit Premium | Records fall to 180 days | §4 `Get-FsiAuditPremiumStatus` cross-reconciles SkuId set |
| 5 | `AIAppInteraction` queried but PAYG never enabled | Empty result interpreted as "no shadow AI" | §5 `Get-FsiAuditPaygEnablement` reads PAYG opt-in state |
| 6 | Mailbox audit bypass set on a regulated user | `Search-UnifiedAuditLog` returns no mailbox events for that user | §6 `Get-FsiMailboxAuditBypass` enumerates non-zero bypass associations |
| 7 | Tenant-level Dataverse audit on, per-table audit off | UAL has Dataverse signal but content lacks before/after values | §9 `Get-FsiCopilotStudioDataverseAudit` walks six entities per environment |
| 8 | "Audit captured = books-and-records preserved" assumption | 17a-4(f) attestation chain broken | §10 `Test-FsiAuditTo17a4Preservation` verifies immutable container with **locked** time-based policy |
| 9 | Sentinel connector enabled but no analytics rule on `CopilotInteraction` | Events ingested, never alerted | §11 `Test-FsiAuditToSentinel` verifies connector + rule presence |

**Required shell guard (run this at the top of every Control 1.7 session).**

```powershell
# Save as: scripts/Assert-Agt17Shell.ps1
[CmdletBinding()]
[OutputType([void])]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [version]'7.4.0') {
    Write-Error "Control 1.7 orchestrator requires PowerShell 7.4 LTS Core (pwsh). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). The Power Apps Administration leg in §9 will be spawned into a Windows PowerShell 5.1 child process per BL-§2."
    exit 2
}

# Stale Windows PowerShell module shadowing trap
$bad = Get-Module -ListAvailable -Name 'Microsoft.Graph' |
    Where-Object { $_.Version.Major -lt 2 }
if ($bad) {
    Write-Error "Stale v1 Microsoft.Graph visible: $($bad.Version -join ', '). Uninstall before continuing — autoload would silently shadow the pinned v2 modules and produce wrong-shape audit output."
    exit 2
}
Write-Verbose "Control 1.7 shell guard passed: pwsh $($PSVersionTable.PSVersion)"
```

---

## §1 — Module, CLI, and permission matrix

**Why this section exists.** Audit-plane evidence is reproducible only when versions are declared and emitted into the SHA-256-hashed manifest (§12). Microsoft ships breaking shape changes across `ExchangeOnlineManagement` minor versions on the audit cmdlet surface, and the Microsoft Graph audit search query API is itself preview-adjacent — pin the SDK version your CAB has approved. See **BL-§1** for the canonical pinning pattern.

### 1.1 Pinned PowerShell modules

| Module | Edition | Approved Pinning Pattern | Purpose |
|---|---|---|---|
| `ExchangeOnlineManagement` | Core or Desktop (verify per version) | `Install-Module ExchangeOnlineManagement -RequiredVersion '<CAB version>' -Repository PSGallery -Scope CurrentUser` | `Connect-ExchangeOnline` for `Get/Set-AdminAuditLogConfig`, `Get/Set-MailboxAuditBypassAssociation`. **Separate** `Connect-IPPSSession` for compliance cmdlets (`Search-UnifiedAuditLog`, `Get-UnifiedAuditLogRetentionPolicy`, `New-ComplianceCase`, `New-ComplianceSearch`). See [Connect to Exchange Online PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-exchange-online-powershell) and [Connect to Security & Compliance PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell). |
| `Microsoft.Graph.Reports` | Core | `Install-Module Microsoft.Graph.Reports -RequiredVersion '<CAB version>' -Repository PSGallery -Scope CurrentUser` | `Get-MgAuditLogDirectoryAudit`, `Get-MgAuditLogSignIn` — strategic forward path replacing legacy `Search-AdminAuditLog`. See [Microsoft Graph audit logs](https://learn.microsoft.com/en-us/graph/api/resources/azure-ad-auditlog-overview). |
| `Microsoft.Graph.Beta.Reports` | Core | Same pattern; **beta** | Audit Search query API (`/security/auditLog/queries`) — preview surface for the new Microsoft 365 audit search experience. See [auditLogQuery resource type (beta)](https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery). Treat as additive evidence pending GA. |
| `Microsoft.Graph.Authentication` | Core | Pinned with the meta module | `Connect-MgGraph -Environment Global` (commercial). |
| `Microsoft.Graph.Users` / `Microsoft.Graph.Identity.DirectoryManagement` | Core | Pinned with the meta module | License entitlement reconciliation (§4) and tenant SKU enumeration. |
| `Microsoft.PowerApps.Administration.PowerShell` | **Desktop only** (PS 5.1) per BL-§2 | `Install-Module Microsoft.PowerApps.Administration.PowerShell -RequiredVersion '<CAB version>' -Repository PSGallery -Scope CurrentUser` | Enumerate Power Platform environments for §9 Dataverse per-table audit walk. **Silently returns empty arrays under PowerShell 7** — spawn a 5.1 child process. |
| `Az.Accounts`, `Az.Storage` | Core | `Install-Module Az.Storage -RequiredVersion '<CAB version>'` | §10 17a-4(f) preservation pipeline: enumerate immutable containers, verify time-based retention is **locked**, validate export blobs. |
| `Az.OperationalInsights`, `Az.SecurityInsights` | Core | Same pattern | §11 Sentinel Office 365 connector + analytics rule discovery. |
| Microsoft Power Platform CLI (`pac`) | n/a | Pinned via MSI / `dotnet tool install --version` | Optional alternative for §9 Dataverse audit (`pac admin list`, `pac org settings list`). |

### 1.2 Permission matrix (least-privilege; separate read and write principals)

| Surface | Read role | Write role | Notes |
|---|---|---|---|
| Tenant unified audit log status | `View-Only Audit Logs` (Exchange role) | `Audit Logs` (Exchange role); enabling/disabling requires `Organization Configuration` | `Compliance Admin` alone is **not** sufficient to author retention policies — see Microsoft Learn. |
| Audit search (legacy) | `View-Only Audit Logs` | n/a | Assigned in Exchange admin center role groups. |
| Audit search (Graph) | `AuditLog.Read.All` (delegated or app) | n/a | Graph application permission requires admin consent; verify `(Get-MgContext).Scopes` after connect. |
| Audit retention policies | `View-Only Audit Logs` | `Organization Configuration` (Exchange) | `Get/New/Set/Remove-UnifiedAuditLogRetentionPolicy`. |
| Mailbox audit bypass | `View-Only Recipients` | `Recipient Management` | `Get/Set-MailboxAuditBypassAssociation`. |
| License entitlement | `Directory.Read.All`, `Organization.Read.All` | n/a | `Get-MgSubscribedSku`, `Get-MgUser -Property AssignedLicenses`. |
| Dataverse per-table audit | `Power Platform Administrator` (read) | `System Administrator` on the environment (write) | Requires Dataverse Web API or `Microsoft.PowerApps.Administration.PowerShell`. |
| 17a-4(f) preservation pipeline | `Storage Blob Data Reader` on the immutable container | `Storage Account Contributor` on the storage account; **immutable policy lock** is one-way | Time-based retention policies must be in the **Locked** state to satisfy 17a-4(f). |
| Sentinel forwarding | `Microsoft Sentinel Reader` | `Microsoft Sentinel Contributor` | Office 365 connector status + analytics rule enumeration. |

**SOX 404 separation of duties.** This playbook assumes `agt17-audit-reader` (read-only across all surfaces above) is *distinct* from any principal that mutates audit configuration. The reader principal authenticates with a certificate (no client secret) per BL-§4.

---

## §2 — Authentication bootstrap

**Why this section exists.** A properly authenticated session is required for all cmdlets in §3–§12. The helper below opens connections to the commercial Microsoft 365 endpoints.

### 2.1 Cloud profile resolver

```powershell
function Resolve-Agt17CloudProfile {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        
        [string]$Cloud
    )
    $map = @{
        Commercial = @{ Exo = 'O365Default';        Ipps = 'O365Default';        Graph = 'Global';     Az = 'AzureCloud';        Pac = 'Public' }    }
    [pscustomobject]$map[$Cloud]
}
```

### 2.2 Two distinct connections (interactive flow)

```powershell
function Connect-Agt17Audit {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [string]$Cloud = 'Commercial',
        [Parameter(Mandatory)] [string]$UserPrincipalName
    )
    $profile = Resolve-Agt17CloudProfile -Cloud $Cloud

    if ($PSCmdlet.ShouldProcess('Exchange Online','Connect-ExchangeOnline')) {
        Connect-ExchangeOnline -ExchangeEnvironmentName $profile.Exo -UserPrincipalName $UserPrincipalName -ShowBanner:$false
    }
    if ($PSCmdlet.ShouldProcess('Security & Compliance','Connect-IPPSSession')) {
        Connect-IPPSSession -ConnectionUri (
            switch ($Cloud) {
                'Commercial' { 'https://ps.compliance.protection.outlook.com/PowerShell-LiveId' }
                'GCC'        { 'https://ps.compliance.protection.outlook.com/PowerShell-LiveId' }
            }
        ) -UserPrincipalName $UserPrincipalName
    }
    if ($PSCmdlet.ShouldProcess('Microsoft Graph','Connect-MgGraph')) {
        Connect-MgGraph -Environment $profile.Graph -Scopes @(
            'AuditLog.Read.All','Directory.Read.All','Organization.Read.All','User.Read.All','SecurityEvents.Read.All'
        ) -NoWelcome
    }
    if ($PSCmdlet.ShouldProcess('Azure','Connect-AzAccount')) {
        Connect-AzAccount -Environment $profile.Az | Out-Null
    }
}
```

### 2.3 Service-principal-with-certificate flow (recommended for unattended)

Do **not** ship plaintext client secrets. Use a certificate from Key Vault or the local certificate store; rotate per BL-§4.

```powershell
function Connect-Agt17AuditAsApp {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [string]$Cloud = 'Commercial',
        [Parameter(Mandatory)] [string]$AppId,
        [Parameter(Mandatory)] [string]$CertificateThumbprint,
        [Parameter(Mandatory)] [string]$Organization,   # e.g., 'contoso.onmicrosoft.com'
        [Parameter(Mandatory)] [string]$TenantId
    )
    $profile = Resolve-Agt17CloudProfile -Cloud $Cloud

    if ($PSCmdlet.ShouldProcess('Exchange Online','Connect-ExchangeOnline (cert)')) {
        Connect-ExchangeOnline -ExchangeEnvironmentName $profile.Exo `
            -AppId $AppId -CertificateThumbprint $CertificateThumbprint -Organization $Organization -ShowBanner:$false
    }
    # NOTE (April 2026): Connect-IPPSSession certificate-based app-only auth is documented for commercial;
    # Verify module parity at each change window.
    # in your tenant, run §7 compliance searches under a delegated session.
    if ($PSCmdlet.ShouldProcess('Microsoft Graph','Connect-MgGraph (cert)')) {
        Connect-MgGraph -Environment $profile.Graph -ClientId $AppId -CertificateThumbprint $CertificateThumbprint -TenantId $TenantId -NoWelcome
    }
    # Verify granted scopes match requested scopes (BL-§3 false-clean trap)
    $missing = @('AuditLog.Read.All','Directory.Read.All','Organization.Read.All') |
        Where-Object { $_ -notin (Get-MgContext).Scopes }
    if ($missing) { throw "Granted Graph scopes missing: $($missing -join ', '). Admin consent not granted on this app." }
}
```

### 2.4 Defensive session-URI assertion (called by every helper)

```powershell
function Assert-FsiExoSession {
    [CmdletBinding()]
    param()
    $conn = Get-ConnectionInformation | Where-Object State -eq 'Connected' |
        Where-Object { $_.ConnectionUri -match 'outlook\.office365\.(com|us)' } |
        Select-Object -First 1
    if (-not $conn) {
        throw "No Exchange Online session detected. Get-AdminAuditLogConfig from a Security & Compliance session ALWAYS reports UnifiedAuditLogIngestionEnabled=False. Run Connect-Agt17Audit first."
    }
    return $conn
}
```

---

## §3 — Tenant unified audit log enablement (`Get-FsiAuditCopilotEnablement`)

**Why this section exists.** Without unified audit log ingestion enabled at the tenant, **none** of the Copilot or agent record types in §7 ever materialise. Status checks must run from the EXO session (BL-§0; §0 trap #1).

### 3.1 Read-only enablement check

```powershell
function Get-FsiAuditCopilotEnablement {
    <#
    .SYNOPSIS
        Reports whether unified audit log ingestion is enabled and Copilot/agent record types are flowing.
    .OUTPUTS
        [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
    #>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [int]$LookbackHours = 24,
        [string[]]$RecordTypes = @('CopilotInteraction','ConnectedAIAppInteraction','MicrosoftCopilotStudio')
    )
    try {
        $conn = Assert-FsiExoSession
        $cfg  = Get-AdminAuditLogConfig
        $ingestEnabled = [bool]$cfg.UnifiedAuditLogIngestionEnabled

        $start = (Get-Date).ToUniversalTime().AddHours(-$LookbackHours)
        $end   = (Get-Date).ToUniversalTime()
        $flowing = foreach ($rt in $RecordTypes) {
            $hit = Search-UnifiedAuditLog -StartDate $start -EndDate $end -RecordType $rt -ResultSize 1 -ErrorAction SilentlyContinue
            [pscustomobject]@{ RecordType = $rt; SeenInLookback = [bool]$hit }
        }

        $status = if (-not $ingestEnabled) { 'Anomaly' }
                  elseif ($flowing.Where({-not $_.SeenInLookback}).Count -gt 0) { 'Pending' }
                  else { 'Clean' }

        [pscustomobject]@{
            ControlId                       = '1.7'
            Helper                          = 'Get-FsiAuditCopilotEnablement'
            Status                          = $status
            SessionUri                      = $conn.ConnectionUri
            UnifiedAuditLogIngestionEnabled = $ingestEnabled
            AdminAuditLogEnabled            = [bool]$cfg.AdminAuditLogEnabled
            RecordTypeFlow                  = $flowing
            LookbackStartUtc                = $start.ToString('o')
            LookbackEndUtc                  = $end.ToString('o')
            CapturedAtUtc                   = (Get-Date).ToUniversalTime().ToString('o')
            Note                            = if (-not $ingestEnabled) { 'Tenant unified audit log ingestion is OFF — Copilot/agent records are not captured. Coordinate enablement per portal-walkthrough.md.' }
                                              elseif ($status -eq 'Pending') { 'Ingestion enabled but one or more Copilot/agent RecordTypes show no activity in the lookback window. Could be propagation lag (allow up to 60 minutes after enablement) or genuinely zero usage; do not stamp Clean until corroborated.' }
                                              else { 'Ingestion enabled and Copilot/agent record types observed in lookback.' }
        }
    } catch {
        [pscustomobject]@{
            ControlId = '1.7'; Helper = 'Get-FsiAuditCopilotEnablement'; Status = 'Error'
            ErrorMessage = $_.Exception.Message; CapturedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

### 3.2 Idempotent enable (mutation — confirm before applying)

```powershell
function Enable-FsiUnifiedAudit {
    <#
    .SYNOPSIS
        Idempotent enablement of unified audit log ingestion. Reads current state first; only mutates on drift.
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param([string]$EvidencePath = ".\evidence\1.7")

    $conn = Assert-FsiExoSession
    $before = Get-AdminAuditLogConfig
    if ($before.UnifiedAuditLogIngestionEnabled) {
        Write-Verbose "Already enabled; no mutation."
        return [pscustomobject]@{ Status='Clean'; Action='NoOp'; SessionUri=$conn.ConnectionUri }
    }
    if ($PSCmdlet.ShouldProcess('Tenant', 'Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true')) {
        Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
        Write-Warning 'Submitted. Per Microsoft Learn, allow up to 60 minutes for configuration propagation; ingestion of events takes longer. Re-run Get-FsiAuditCopilotEnablement after the propagation window before stamping Clean.'
        return [pscustomobject]@{ Status='Pending'; Action='Set'; SessionUri=$conn.ConnectionUri }
    }
}
```

Always invoke first with `-WhatIf` (BL-§4).

---

## §4 — Audit (Premium) and 10-Year Audit Log Retention add-on entitlement (`Get-FsiAuditPremiumStatus`)

**Why this section exists.** A custom 1-year or 10-year retention policy in §7 silently downgrades to **180-day Audit Standard fallback** for any user lacking the Audit (Premium) entitlement. The single most common Control 1.7 finding is "retention policy in place, license gap means actual retention < policy". Reconcile licenses **before** claiming retention coverage to examiners.

```powershell
function Get-FsiAuditPremiumStatus {
    <#
    .SYNOPSIS
        Reconciles per-user Audit (Premium) and 10-Year Audit Log Retention add-on entitlement against the
        Copilot population. Any Copilot user without Audit Premium is a finding.
    #>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param([string]$EvidencePath = ".\evidence\1.7")

    try {
        # SkuPartNumber values change occasionally — verify against Get-MgSubscribedSku in your tenant.
        $auditPremiumSkus = @(
            'SPE_E5',                                # Microsoft 365 E5
            'ENTERPRISEPREMIUM',                     # Office 365 E5
            'INFORMATION_PROTECTION_COMPLIANCE',     # Microsoft Purview Suite (verify)
            'M365_E5_COMPLIANCE',                    # legacy
            'M365_E5_AUDIT'                          # E5 eDiscovery and Audit add-on (verify)
        )
        $tenYearAddOn = @('M365_AUDIT_PREMIUM_10YR') # verify SkuPartNumber in tenant
        $copilotSkus  = @('Microsoft_365_Copilot')

        $skus = Get-MgSubscribedSku | Select-Object SkuId, SkuPartNumber
        $report = Get-MgUser -All -Property Id,UserPrincipalName,AssignedLicenses | ForEach-Object {
            $assigned = $_.AssignedLicenses.SkuId
            $names    = $skus | Where-Object SkuId -in $assigned | Select-Object -ExpandProperty SkuPartNumber
            [pscustomobject]@{
                UserPrincipalName  = $_.UserPrincipalName
                HasCopilot         = [bool]($names | Where-Object { $_ -in $copilotSkus })
                HasAuditPremium    = [bool]($names | Where-Object { $_ -in $auditPremiumSkus })
                Has10YearRetention = [bool]($names | Where-Object { $_ -in $tenYearAddOn })
            }
        }
        $gaps = $report | Where-Object { $_.HasCopilot -and (-not $_.HasAuditPremium -or -not $_.Has10YearRetention) }

        [pscustomobject]@{
            ControlId        = '1.7'
            Helper           = 'Get-FsiAuditPremiumStatus'
            Status           = if ($gaps) { 'Anomaly' } else { 'Clean' }
            CopilotUserCount = ($report | Where-Object HasCopilot).Count
            AuditPremiumGap  = ($gaps | Where-Object { -not $_.HasAuditPremium }).Count
            TenYearGap       = ($gaps | Where-Object { -not $_.Has10YearRetention }).Count
            GapSample        = $gaps | Select-Object -First 25
            CapturedAtUtc    = (Get-Date).ToUniversalTime().ToString('o')
            Note             = if ($gaps) { 'Copilot users without Audit Premium silently fall back to 180-day retention regardless of any custom retention policy. Resolve license gaps before claiming retention coverage to examiners.' } else { 'Per-user license entitlement aligned with retention policy.' }
        }
    } catch {
        [pscustomobject]@{ ControlId='1.7'; Helper='Get-FsiAuditPremiumStatus'; Status='Error'; ErrorMessage=$_.Exception.Message; CapturedAtUtc=(Get-Date).ToUniversalTime().ToString('o') }
    }
}
```

---

## §5 — Audit pay-as-you-go (PAYG) AI App Interaction enablement (`Get-FsiAuditPaygEnablement`)

**Why this section exists.** Per Microsoft Learn (April 2026), `AIAppInteraction` (and *some* `ConnectedAIAppInteraction` scenarios for non-Microsoft AI apps surfaced via Connected AI App) is captured under [Audit pay-as-you-go billing](https://learn.microsoft.com/en-us/purview/purview-billing-models). **Until the PAYG meter is opted in**, these records do not flow at all — and an empty `Search-UnifiedAuditLog -RecordType AIAppInteraction` result is misread as "no shadow AI use" instead of "PAYG capture is off". PAYG-captured records have a **180-day** retention floor regardless of Audit Premium licensing.

```powershell
function Get-FsiAuditPaygEnablement {
    <#
    .SYNOPSIS
        Reports the Audit PAYG opt-in state for AIAppInteraction (and confirms an Azure subscription is bound).
    .NOTES
        Microsoft Learn: 'Manage pay-as-you-go billing for Microsoft Purview' for the canonical opt-in path
        (Purview portal > Settings > Billing > Pay-as-you-go services). The portal is the source of truth;
        this helper inspects observable signals only (record-type flow + Azure billing binding presence).
    #>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
         [string]$Cloud = 'Commercial',
        [int]$LookbackDays = 30
    )
    try {

    } catch {
        [pscustomobject]@{ ControlId='1.7'; Helper='Get-FsiCopilotStudioDataverseAudit'; Status='Error'; ErrorMessage=$_.Exception.Message; CapturedAtUtc=(Get-Date).ToUniversalTime().ToString('o') }
    }
}
```

### 9.2 Idempotent enable across environments (mutation)

```powershell
function Enable-FsiCopilotStudioDataverseAudit {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param([Parameter(Mandatory)] [string]$EnvironmentWebApiUrl)

    $entities = @('bot','botcomponent','botcomponentcollection','conversationtranscript','aiplugin','aipluginauth')
    foreach ($e in $entities) {
        $metaUri = "$EnvironmentWebApiUrl/api/data/v9.2/EntityDefinitions(LogicalName='$e')"
        $current = Invoke-MgGraphRequest -Method GET -Uri "$metaUri`?`$select=LogicalName,IsAuditEnabled"
        if ($current.IsAuditEnabled.Value) { Write-Verbose "$e already audited; skipping."; continue }
        if ($PSCmdlet.ShouldProcess("$EnvironmentWebApiUrl :: $e", 'PATCH IsAuditEnabled=true')) {
            Invoke-MgGraphRequest -Method PATCH -Uri $metaUri `
                -Body (@{ IsAuditEnabled = @{ Value = $true; CanBeChanged = $true; ManagedPropertyLogicalName = 'canmodifyauditsettings' } } | ConvertTo-Json -Depth 4) `
                -ContentType 'application/json'
        }
    }
}
```

PAC CLI alternative: `pac org settings update --name IsAuditEnabled --value true` per environment.

---

## §10 — SEC 17a-4(f) preservation pipeline (`Test-FsiAuditTo17a4Preservation`)

**Why this section exists.** Microsoft 365 Audit (Standard, Premium, 10-year add-on) is **record-CAPTURE telemetry**, not a 17a-4(f)-compliant electronic recordkeeping system. For broker-dealers, FCMs, swap dealers, and CPOs subject to SEC 17a-4 / FINRA 4511 / CFTC 1.31, preservation must be satisfied through either WORM storage (Azure immutable blob with a *locked* time-based retention policy — see [Microsoft Learn: Immutable storage for Azure blob data](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)) or the audit-trail alternative under the October 2022 amendments to Rule 17a-4(f).

This helper verifies that an export pipeline exists into an attested archive. It does **not**, by itself, *guarantee* 17a-4(f) compliance — Cohasset attestation, Designated Executive Officer (DEO) representation or Designated Third Party (DTP) undertaking, and a documented books-and-records record set are out-of-scope for PowerShell verification.

### 10.1 Reusable preservation export helper

```powershell
function Export-FsiAuditTo17a4 {
    <#
    .SYNOPSIS
        Exports a Search-FsiAuditLogPaged result set to an Azure immutable blob container with a locked
        time-based retention policy. Computes SHA-256 manifest per BL-§5.
    .NOTES
        Hedged: supports SEC 17a-4(f) preservation when configured per Cohasset-attested guidance and
        combined with the firm's books-and-records record set. Does not, by itself, guarantee compliance.
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory)] [object[]]$Records,
        [Parameter(Mandatory)] [string]$StorageAccountName,
        [Parameter(Mandatory)] [string]$ContainerName,
        [Parameter(Mandatory)] [string]$EvidencePrefix,
        [int]$RetentionYears = 7
    )
    $ctx = New-AzStorageContext -StorageAccountName $StorageAccountName -UseConnectedAccount

    # Verify container has an immutable storage policy in the Locked state
    $policy = Get-AzRmStorageContainerImmutabilityPolicy `
        -ResourceGroupName (Get-AzStorageAccount | Where-Object StorageAccountName -eq $StorageAccountName).ResourceGroupName `
        -StorageAccountName $StorageAccountName -ContainerName $ContainerName -ErrorAction Stop
    if ($policy.State -ne 'Locked') {
        throw "Container '$ContainerName' has no LOCKED time-based immutability policy (current state: $($policy.State)). 17a-4(f) preservation requires the Locked state — Unlocked policies can be deleted by storage account contributors and do not satisfy WORM."
    }
    if ($policy.ImmutabilityPeriodSinceCreationInDays -lt ($RetentionYears * 365)) {
        throw "Container immutability period ($($policy.ImmutabilityPeriodSinceCreationInDays) days) is shorter than required retention ($($RetentionYears * 365) days)."
    }

    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $name = "$EvidencePrefix-$ts.json"
    $tmp  = Join-Path ([IO.Path]::GetTempPath()) $name
    try {
        $Records | ConvertTo-Json -Depth 30 | Set-Content -Path $tmp -Encoding UTF8
        $hash = (Get-FileHash -Path $tmp -Algorithm SHA256).Hash
        if ($PSCmdlet.ShouldProcess("$StorageAccountName/$ContainerName/$name","Set-AzStorageBlobContent")) {
            Set-AzStorageBlobContent -Context $ctx -Container $ContainerName -File $tmp -Blob $name -Force | Out-Null
        }
        [pscustomobject]@{
            Blob = "$ContainerName/$name"; Sha256 = $hash; Bytes = (Get-Item $tmp).Length
            ImmutabilityState = $policy.State; RetentionDays = $policy.ImmutabilityPeriodSinceCreationInDays
            CapturedAtUtc = $ts
        }
    } finally {
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    }
}
```

### 10.2 Pipeline health check

```powershell
function Test-FsiAuditTo17a4Preservation {
    <#
    .SYNOPSIS
        Verifies a 17a-4(f)-compatible preservation pipeline exists for unified-audit exports.
        Detects either Azure immutable blob storage (locked time-based policy) or an annotated
        third-party connector reference.
    #>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [string]$StorageAccountName,
        [string]$ContainerName,
        [int]$MinRetentionYears = 7,
        [string]$ThirdPartyConnectorAnnotationPath   # optional path to JSON describing a vendor archive (Smarsh / Global Relay / Proofpoint / Mimecast / Bloomberg Vault / Veritas)
    )
    try {
        $azureBranch = $null
        if ($StorageAccountName -and $ContainerName) {
            $rg = (Get-AzStorageAccount | Where-Object StorageAccountName -eq $StorageAccountName).ResourceGroupName
            $policy = Get-AzRmStorageContainerImmutabilityPolicy -ResourceGroupName $rg -StorageAccountName $StorageAccountName -ContainerName $ContainerName -ErrorAction SilentlyContinue
            $azureBranch = [pscustomobject]@{
                StorageAccount = $StorageAccountName
                Container      = $ContainerName
                PolicyState    = $policy.State
                RetentionDays  = $policy.ImmutabilityPeriodSinceCreationInDays
                MeetsRetention = ($policy.ImmutabilityPeriodSinceCreationInDays -ge ($MinRetentionYears * 365))
                Locked         = ($policy.State -eq 'Locked')
            }
        }

        $vendorBranch = $null
        if ($ThirdPartyConnectorAnnotationPath -and (Test-Path $ThirdPartyConnectorAnnotationPath)) {
            $vendorBranch = Get-Content $ThirdPartyConnectorAnnotationPath -Raw | ConvertFrom-Json
        }

        $passes = ($azureBranch -and $azureBranch.Locked -and $azureBranch.MeetsRetention) -or
                  ($vendorBranch -and $vendorBranch.AttestationOnFile -eq $true)

        [pscustomobject]@{
            ControlId        = '1.7'
            Helper           = 'Test-FsiAuditTo17a4Preservation'
            Status           = if ($passes) { 'Clean' } elseif ($azureBranch -or $vendorBranch) { 'Anomaly' } else { 'Pending' }
            AzureBranch      = $azureBranch
            VendorBranch     = $vendorBranch
            CapturedAtUtc    = (Get-Date).ToUniversalTime().ToString('o')
            Note             = 'Supports SEC 17a-4(f) preservation when configured per Cohasset-attested guidance and combined with the firm''s books-and-records record set. Does not, by itself, guarantee compliance — DEO representation or DTP undertaking and an independent records-management assessment remain out-of-scope for PowerShell verification.'
        }
    } catch {
        [pscustomobject]@{ ControlId='1.7'; Helper='Test-FsiAuditTo17a4Preservation'; Status='Error'; ErrorMessage=$_.Exception.Message; CapturedAtUtc=(Get-Date).ToUniversalTime().ToString('o') }
    }
}
```

---

## §11 — Sentinel forwarding sanity check (`Test-FsiAuditToSentinel`)

**Why this section exists.** Cross-control verification with Control 3.9 (Microsoft Sentinel Integration). The Office 365 connector can be enabled with the connector status reporting healthy while no analytics rule on `CopilotInteraction` exists — events flow into the Log Analytics workspace, and nobody is alerted.

```powershell
function Test-FsiAuditToSentinel {
    <#
    .SYNOPSIS
        Verifies the Sentinel Office 365 connector is enabled AND at least one analytics rule references
        CopilotInteraction. Cross-references Control 3.9.
    #>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroupName,
        [Parameter(Mandatory)] [string]$WorkspaceName,
         [string]$Cloud = 'Commercial'
    )
    try {

        $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
        [pscustomobject]@{ EvidenceFile = "$base.json"; Sha256 = $hash; Manifest = $manifestPath }
    }
}

# Quarterly attestation pack
Start-Transcript -Path ".\evidence\1.7\transcript_$(Get-Date -Format 'yyyyMMddTHHmmssZ').log" -IncludeInvocationHeader

Get-FsiAuditCopilotEnablement                     | Save-FsiAuditEvidence -Name 'AuditCopilotEnablement'
Get-FsiAuditPremiumStatus                         | Save-FsiAuditEvidence -Name 'AuditPremiumStatus'
Get-FsiAuditPaygEnablement -Cloud Commercial      | Save-FsiAuditEvidence -Name 'AuditPaygEnablement'
Get-FsiMailboxAuditBypass                         | Save-FsiAuditEvidence -Name 'MailboxAuditBypass'
Get-FsiCopilotStudioDataverseAudit                | Save-FsiAuditEvidence -Name 'CopilotStudioDataverseAudit'
Test-FsiAuditTo17a4Preservation `
    -StorageAccountName 'fsiarchivewormprod' `
    -ContainerName 'audit-1-7'                    | Save-FsiAuditEvidence -Name '17a4PreservationPipeline'
Test-FsiAuditToSentinel `
    -ResourceGroupName 'rg-sec-prod' `
    -WorkspaceName 'la-sec-prod'                  | Save-FsiAuditEvidence -Name 'SentinelForwarding'

Stop-Transcript
```

After the run, copy the `evidence\1.7\` folder into the immutable container verified by `Test-FsiAuditTo17a4Preservation`. Reference each artifact's SHA-256 in the attestation statement.

---

## §13 — Cross-control links

| Control | Why it cross-cuts 1.7 |
|---|---|
| [1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP policy match events surface in the same UAL; correlate `RecordType=DLP.SharePoint` etc. with `CopilotInteraction`. |
| [1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Content-tier viewer for `CopilotInteraction` transcripts (§8). |
| [1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | FINRA Rule 3110 supervisory review of AI-generated communications (§8). |
| [1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | Legal hold and collection of Copilot transcripts via Premium eDiscovery (§8). |
| [2.6 — Model Risk Management Alignment](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model identity / version cross-reference for Audit `ModelTransparencyDetails`. |
| [2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Consumes UAL `CopilotInteraction` events as the supervisory queue source. |
| [3.4 — Incident Reporting and Root-Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | UAL is the primary timeline source for Copilot/agent incidents. |
| [3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Verified end-to-end by §11 `Test-FsiAuditToSentinel`. |

---

## §14 — Operating cadence and anti-patterns

### 14.1 Cadence

| Task | Frequency | Helper |
|---|---|---|
| Tenant unified audit ingestion + record-type flow | Daily | `Get-FsiAuditCopilotEnablement` |
| License entitlement reconciliation (Audit Premium + 10y add-on) | Weekly | `Get-FsiAuditPremiumStatus` |
| PAYG `AIAppInteraction` opt-in confirmation | Monthly + after every Microsoft billing change | `Get-FsiAuditPaygEnablement` |
| Mailbox audit bypass review | Monthly + on every regulated-user provisioning event | `Get-FsiMailboxAuditBypass` |
| Dataverse per-table audit on six Copilot Studio entities | Weekly + after every solution import into a new environment | `Get-FsiCopilotStudioDataverseAudit` |
| 17a-4(f) preservation pipeline health | Daily | `Test-FsiAuditTo17a4Preservation` |
| Sentinel forwarding + analytics rule presence | Daily | `Test-FsiAuditToSentinel` |
| Quarterly attestation pack (full evidence set, manifest signed) | Quarterly | All of the above |

### 14.2 Anti-patterns (do not ship)

- ❌ Calling `Get-AdminAuditLogConfig` without first calling `Assert-FsiExoSession` — false-clean trap #1.
- ❌ `Search-UnifiedAuditLog -ResultSize 5000` without `-SessionCommand ReturnLargeSet` and a session-ceiling splitter — silent truncation.
- ❌ Hard-coding `-RecordType PowerPlatformAdminActivity` (or any non-enum value) — silent zero-row return.
- ❌ Claiming retention coverage on the basis of a custom retention policy alone — `Get-FsiAuditPremiumStatus` first.
- ❌ Treating an empty `AIAppInteraction` result as "no shadow AI" without confirming PAYG opt-in via `Get-FsiAuditPaygEnablement`.
- ❌ Enabling tenant-level Dataverse audit and assuming the six Copilot Studio entities inherit per-table audit — they do not, per environment.
- ❌ Treating the 10-Year Audit Log Retention add-on as a 17a-4(f) preservation layer — it is record-CAPTURE telemetry; preservation requires `Test-FsiAuditTo17a4Preservation` to pass.
- ❌ Enabling the Sentinel Office 365 connector and not authoring an analytics rule on `CopilotInteraction` — events ingested, never alerted.
- ❌ Using the same service principal for both `Set-AdminAuditLogConfig` and the audit-evidence pack — SOX 404 separation-of-duties violation.
- ❌ Connecting to Microsoft Graph or Power Apps without proper authentication — check that `Get-MgContext` shows the correct tenant and scope.

---

[Back to Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Portal Walkthrough](portal-walkthrough.md) · [Troubleshooting](troubleshooting.md)

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
