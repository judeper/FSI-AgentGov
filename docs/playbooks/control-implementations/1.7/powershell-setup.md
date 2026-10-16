# Control 1.7 — PowerShell Setup: Comprehensive Audit Logging and Compliance Automation

> **Scope.** This playbook covers the **audit capture and preservation plane** for Control 1.7: Purview Audit Standard/Premium and the 10-Year add-on, Copilot/AI/Power Platform record types, non-Microsoft AI PAYG collection, Dataverse data-change history, supported audit search APIs, content retrieval, and an SEC 17a-4(f)-compatible preservation pipeline into Azure immutable blob storage. `Search-UnifiedAuditLog` remains supported; Graph Audit Search is available at `v1.0`. Read the [PowerShell baseline](../../_shared/powershell-baseline.md) (**BL-§N**) and [parent control](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) first.
>
> **What this playbook is.** A set of audit-plane examples for connection separation, licensing, PAYG evidence, paginated search, approved Dataverse table/column history, preservation export, and SHA-256 evidence manifests. The six-table Dataverse starting inventory is framework-selected, not a Microsoft prerequisite for default-on Copilot Studio authoring collection. The Sentinel check verifies a known audit ID in `CopilotActivity`; connector/rule configuration alone does not prove ingestion. Adapt and test examples before production use.
>
> **What this playbook is not.** It is not, by itself, a SEC Rule 17a-4(f)-compliant electronic recordkeeping system. Microsoft 365 Audit (including the 10-year add-on) is **record-CAPTURE operational telemetry**; preservation requires either WORM storage of the books-and-records record set (e.g., Azure immutable blob storage with a time-based retention policy in a *locked* state — Cohasset-attested for SEC 17a-4(f), CFTC 1.31, and FINRA 4511 — see [Microsoft Learn: Immutable storage for Azure blob data](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)) or the audit-trail alternative under the October 2022 amendments to Rule 17a-4(f) (compliance date 3 May 2023). This harness verifies that the export pipeline exists and is healthy; it does not, by itself, *guarantee* attestation, *eliminate* preservation risk, or replace the Designated Executive Officer (DEO) representation or Designated Third Party (DTP) undertaking required under the audit-trail alternative.
>
> **Hedged language reminder.** Output of this harness *supports compliance with* FINRA Rule 4511, FINRA Rule 3110, FINRA RN 24-09 / Rule 3110, SEC Rule 17a-3, SEC Rule 17a-4(b)(4) / 17a-4(f), SOX 302/404, GLBA 501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Fed SR 26-2 (formerly SR 11-7), NIST AI RMF MEASURE 2.7 / GOVERN 1.4, CFTC Rule 1.31, and NYDFS 23 NYCRR 500.06. It does not, by itself, *ensure* a passing examination, *guarantee* completeness of the books-and-records record set, or *eliminate* the risk that a record type is silently re-classified between Audit Standard, Audit Premium, and Audit PAYG between Microsoft releases. Implementation requires that organizations verify Audit Premium licensing, PAYG opt-in scope, and Dataverse audit settings at every change window, and that they treat any preview surface (agent-specific beta Graph queries) as **additive** evidence rather than the sole source of truth.

| Field | Value |
|---|---|
| Control ID | 1.7 |
| Pillar | 1 — Security |
| Playbook | PowerShell Setup |
| PowerShell Edition | 7.4 LTS Core (orchestrator, Graph, Az.Storage); 5.1 Desktop (Power Apps Administration sub-shell for Dataverse audit, JSON-bridged); both Desktop and Core supported for `Connect-ExchangeOnline` and `Connect-IPPSSession` (verify against your CAB-pinned `ExchangeOnlineManagement` version) |
| Cloud Scope | Commercial |
| Last UI Verified | April 2026 |
| Technical claims reviewed | 2026-10-16 against Microsoft Learn; tenant execution not tested |
| Companion Playbooks | [`portal-walkthrough.md`](portal-walkthrough.md) · `verification-testing.md` (planned) · [`troubleshooting.md`](troubleshooting.md) |
| Related Controls | [1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) · [1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) · [1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) · [2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) · [2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) · [3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) · [3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |

---

## §0 — Wrong-shell trap and audit-plane false-clean defects (READ FIRST)

**The defining fact of Control 1.7.** Audit configuration cmdlets in `ExchangeOnlineManagement` exist in **both** the Exchange Online (`Connect-ExchangeOnline`) and the Security & Compliance (`Connect-IPPSSession`) PowerShell connections, with the **same names** and **different return semantics**. Per Microsoft Learn, `Get-AdminAuditLogConfig.UnifiedAuditLogIngestionEnabled` **always returns `$false` from the Security & Compliance session**, regardless of the actual tenant state, because the property is a property of the Exchange Online configuration object — not the compliance one. A script that does not assert which session it is reading from is producing **audit-grade misinformation**.

A script that ignores this reality produces a **false-clean audit posture** — the worst Control 1.7 outcome. False-clean audit posture means examiners are told records were captured when they were not, breaks SEC 17a-4(b)(4) communications-retention attestation for broker-dealer Copilot rollouts, leaves FINRA Rule 3110 supervisory queues operating on incomplete sets, and invalidates the Cohasset attestation chain that downstream SEC 17a-4(f) preservation depends on.

**Why this section exists.** Eight classes of silent failure produce false-clean audit-plane output in Control 1.7 specifically:

1. **Wrong-shell trap on `Get-AdminAuditLogConfig`.** Always returns `$false` for `UnifiedAuditLogIngestionEnabled` from the Security & Compliance session. Helpers in §3 hard-fail unless the active session URI matches `outlook.office365.(com|us)`.
2. **Invalid `-RecordType` returns zero rows silently.** Earlier playbooks shipped `-RecordType PowerPlatformAdminActivity`; that name is **not** in the `AuditLogRecordType` enumeration. Some module versions silently return zero rows for invalid RecordType values. The canonical names include `CopilotInteraction`, `ConnectedAIAppInteraction`, `AIAppInteraction`, `PowerPlatformAdministratorActivity`, `MicrosoftFlow`, `PowerAppsApp`, and `PowerBIAudit` — for Copilot Studio agent authoring/admin/lifecycle use `PowerPlatformAdministratorActivity`, and for Copilot Studio end-user usage use `CopilotInteraction`. Validate against the live enum at runtime.
3. **`Search-UnifiedAuditLog` `-ResultSize` truncation.** Default `-ResultSize 100`; per-call cap **5,000**; per-session ceiling **50,000**. Single-shot calls silently drop records past those limits. Use `-SessionCommand ReturnLargeSet` with a fresh `-SessionId` per date window, and split windows when the session ceiling is approached.
4. **Use supported extraction surfaces.** `Search-UnifiedAuditLog` remains supported. Its documentation recommends the Office 365 Management Activity API for programmatic downloads. Graph Audit Search is also available at `v1.0`; it needs query-specific permissions and explicit completeness checks.
5. **Audit Premium silently downgrades to Audit Standard.** If a user does not have an Audit (Premium) entitlement, their `CopilotInteraction` records fall back to **180-day retention** regardless of any custom retention policy. License reconciliation (§4) must be tenant-wide before retention claims.
6. **PAYG record types require explicit opt-in.** `AIAppInteraction` and *some* `ConnectedAIAppInteraction` scenarios (non-Microsoft AI apps surfaced via Connected AI App) fall under [Audit pay-as-you-go billing](https://learn.microsoft.com/en-us/purview/purview-billing-models). Until the PAYG meter is turned on, these records do not flow at all.
7. **Dataverse data-change history is environment-scoped.** Environment-level "Start auditing" and the approved table/column audit settings govern data-change history. The six-table starting inventory is a framework choice, not a Microsoft prerequisite for default-on Copilot Studio authoring audit collection. Verify the target environment's settings after solution deployment.
8. **Single-credential read+write.** Running this harness with the same service principal that *modifies* audit configuration breaks SOX 404 separation of duties — the principal that produces the evidence could be the principal that altered the configuration the evidence describes. Use a separate `agt17-audit-reader` audit-only principal.

**Top false-clean defects unique to audit-plane automation.**

| # | Defect | What it looks like | How this playbook traps it |
|---|---|---|---|
| 1 | `Get-AdminAuditLogConfig` from `Connect-IPPSSession` | `UnifiedAuditLogIngestionEnabled = False` regardless of truth | §3 `Assert-FsiExoSession` hard-fails on session URI mismatch |
| 2 | Unsupported `-RecordType PowerPlatformAdminActivity` | Invalid query mistaken for an empty activity set | §7 validates the framework's supported type names and surfaces search errors |
| 3 | `Search-UnifiedAuditLog` without pagination | Caps at 100 / 5,000 / 50,000 silently | §7 `Search-FsiAuditLogPaged` with `ReturnLargeSet` and date-window splitter |
| 4 | Custom retention policy without per-user Audit Premium | Records fall to 180 days | §4 `Get-FsiAuditPremiumStatus` cross-reconciles SkuId set |
| 5 | `AIAppInteraction` queried but PAYG never enabled | Empty result interpreted as "no shadow AI" | §5 `Get-FsiAuditPaygEnablement` reads PAYG opt-in state |
| 6 | Mailbox audit bypass set on a regulated user | `Search-UnifiedAuditLog` returns no mailbox events for that user | §6 `Get-FsiMailboxAuditBypass` enumerates non-zero bypass associations |
| 7 | Tenant-level Dataverse audit on, per-table audit off | UAL has Dataverse signal but content lacks before/after values | §9 `Get-FsiCopilotStudioDataverseAudit` walks six entities per environment |
| 8 | "Audit captured = books-and-records preserved" assumption | 17a-4(f) attestation chain broken | §10 `Test-FsiAuditTo17a4Preservation` verifies immutable container with **locked** time-based policy |
| 9 | Connector configured but known audit record absent | Configuration mistaken for capture evidence | §11 `Test-FsiAuditToSentinel` queries `CopilotActivity` by audit ID; test analytics rules separately |
| 10 | `Connect-MgGraph` without `-Environment 'Global'` | Audit Search Graph API may return wrong tenant scope | §2 bootstrap asserts the Graph environment is `Global` before proceeding |

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

**Why this section exists.** Audit-plane evidence is reproducible only when versions are declared and emitted into the SHA-256-hashed manifest (§12). Pin the SDK/module versions your CAB has approved and verify the returned schema. Graph Audit Search is available at `v1.0`; do not classify the entire API as preview. See **BL-§1** for the canonical pinning pattern.

### 1.1 Pinned PowerShell modules

| Module | Edition | Approved Pinning Pattern | Purpose |
|---|---|---|---|
| `ExchangeOnlineManagement` | Core or Desktop (verify per version) | `Install-Module ExchangeOnlineManagement -RequiredVersion '<CAB version>' -Repository PSGallery -Scope CurrentUser` | Use Exchange Online for `Get/Set-AdminAuditLogConfig`, mailbox audit bypass checks, and the [recommended Search-UnifiedAuditLog session](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/search-unifiedauditlog). Use Security & Compliance PowerShell for retention policies and eDiscovery cmdlets. See [Exchange Online connection](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-exchange-online-powershell) and [Security & Compliance connection](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell). |
| `Microsoft.Graph.Reports` | Core | `Install-Module Microsoft.Graph.Reports -RequiredVersion '<CAB version>' -Repository PSGallery -Scope CurrentUser` | `Get-MgAuditLogDirectoryAudit`, `Get-MgAuditLogSignIn` — strategic forward path replacing legacy `Search-AdminAuditLog`. See [Microsoft Graph audit logs](https://learn.microsoft.com/en-us/graph/api/resources/azure-ad-auditlog-overview). |
| `Microsoft.Graph.Authentication` (REST access) | Core | Pin the approved SDK version | `Invoke-MgGraphRequest` to `/v1.0/security/auditLog/queries`. See [auditLogQuery](https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery?view=graph-rest-1.0); no beta Reports module is required for this REST example. |
| `Microsoft.Graph.Authentication` | Core | Pinned with the meta module | `Connect-MgGraph -Environment 'Global'` for commercial tenants. |
| `Microsoft.Graph.Users` / `Microsoft.Graph.Identity.DirectoryManagement` | Core | Pinned with the meta module | License entitlement reconciliation (§4) and tenant SKU enumeration. |
| `Microsoft.PowerApps.Administration.PowerShell` | **Desktop only** (PS 5.1) per BL-§2 | `Install-Module Microsoft.PowerApps.Administration.PowerShell -RequiredVersion '<CAB version>' -Repository PSGallery -Scope CurrentUser` | Enumerate Power Platform environments for §9 Dataverse per-table audit walk. **Silently returns empty arrays under PowerShell 7** — spawn a 5.1 child process. |
| `Az.Accounts`, `Az.Storage` | Core | `Install-Module Az.Storage -RequiredVersion '<CAB version>'` | §10 17a-4(f) preservation pipeline: enumerate immutable containers, verify time-based retention is **locked**, validate export blobs. |
| `Az.OperationalInsights`, `Az.SecurityInsights` | Core | Same pattern | §11 Sentinel Office 365 connector + analytics rule discovery. |
| Microsoft Power Platform CLI (`pac`) | n/a | Pinned via MSI / `dotnet tool install --version` | Optional alternative for §9 Dataverse audit (`pac admin list`, `pac org settings list`). Use `pac auth create --cloud Public` for commercial. |

### 1.2 Permission matrix (least-privilege; separate read and write principals)

| Surface | Read role | Write role | Notes |
|---|---|---|---|
| Tenant unified audit log status | `View-Only Audit Logs` (Exchange role) | `Audit Logs` (Exchange role); enabling/disabling requires `Organization Configuration` | `Compliance Admin` alone is **not** sufficient to author retention policies — see Microsoft Learn. |
| Audit search (legacy) | `View-Only Audit Logs` | n/a | Assigned in Exchange admin center role groups. |
| Audit search (Graph) | `AuditLogsQuery.Read.All` for cross-workload searches, or applicable workload-specific query permission | n/a | `AuditLog.Read.All` covers Entra audit/sign-in access, not Purview audit queries. See [create query permissions](https://learn.microsoft.com/en-us/graph/api/security-auditcoreroot-post-auditlogqueries?view=graph-rest-1.0). |
| Audit retention policies | `View-Only Audit Logs` | `Organization Configuration` (Exchange) | `Get/New/Set/Remove-UnifiedAuditLogRetentionPolicy`. |
| Mailbox audit bypass | `View-Only Recipients` | `Recipient Management` | `Get/Set-MailboxAuditBypassAssociation`. |
| License entitlement | `Directory.Read.All`, `Organization.Read.All` | n/a | `Get-MgSubscribedSku`, `Get-MgUser -Property AssignedLicenses`. |
| Dataverse per-table audit | `Power Platform Administrator` (read) | `System Administrator` on the environment (write) | Requires Dataverse Web API or `Microsoft.PowerApps.Administration.PowerShell`. |
| 17a-4(f) preservation pipeline | `Storage Blob Data Reader` on the immutable container | `Storage Account Contributor` on the storage account; **immutable policy lock** is one-way | Time-based retention policies must be in the **Locked** state to satisfy 17a-4(f). |
| Sentinel forwarding | `Microsoft Sentinel Reader` | `Microsoft Sentinel Contributor` | Office 365 connector status + analytics rule enumeration. |

**SOX 404 separation of duties.** This playbook assumes `agt17-audit-reader` (read-only across all surfaces above) is *distinct* from any principal that mutates audit configuration. The reader principal authenticates with a certificate (no client secret) per BL-§3.

---

## §2 — Authentication bootstrap

**Why this section exists.** A `Connect-ExchangeOnline` without proper configuration or a `Connect-MgGraph` without the correct environment on a commercial tenant may return zero results. The helpers below establish two distinct connections (EXO and Security & Compliance) plus a Graph context, and assert that the correct session is active before any audit query runs.

### 2.1 Two distinct connections (interactive flow)

```powershell
function Connect-Agt17Audit {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string]$UserPrincipalName
    )

    if ($PSCmdlet.ShouldProcess('Exchange Online','Connect-ExchangeOnline')) {
        Connect-ExchangeOnline -UserPrincipalName $UserPrincipalName -ShowBanner:$false
    }
    if ($PSCmdlet.ShouldProcess('Security & Compliance','Connect-IPPSSession')) {
        Connect-IPPSSession -UserPrincipalName $UserPrincipalName
    }
    if ($PSCmdlet.ShouldProcess('Microsoft Graph','Connect-MgGraph')) {
        Connect-MgGraph -Environment 'Global' -Scopes @(
            'AuditLogsQuery.Read.All','AuditLog.Read.All','Directory.Read.All','Organization.Read.All','User.Read.All','SecurityEvents.Read.All'
        ) -NoWelcome
    }
    if ($PSCmdlet.ShouldProcess('Azure','Connect-AzAccount')) {
        Connect-AzAccount -Environment 'AzureCloud' | Out-Null
    }
}
```

### 2.2 Service-principal-with-certificate flow (recommended for unattended)

Do **not** ship plaintext client secrets. Use a certificate from Key Vault or the local certificate store; rotate per BL-§3.

```powershell
function Connect-Agt17AuditAsApp {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string]$AppId,
        [Parameter(Mandatory)] [string]$CertificateThumbprint,
        [Parameter(Mandatory)] [string]$Organization,   # e.g., 'contoso.onmicrosoft.com'
        [Parameter(Mandatory)] [string]$TenantId
    )

    if ($PSCmdlet.ShouldProcess('Exchange Online','Connect-ExchangeOnline (cert)')) {
        Connect-ExchangeOnline `
            -AppId $AppId -CertificateThumbprint $CertificateThumbprint -Organization $Organization -ShowBanner:$false
    }
    if ($PSCmdlet.ShouldProcess('Microsoft Graph','Connect-MgGraph (cert)')) {
        Connect-MgGraph -Environment 'Global' -ClientId $AppId -CertificateThumbprint $CertificateThumbprint -TenantId $TenantId -NoWelcome
    }
    # Verify granted scopes match requested scopes (false-clean trap)
    $missing = @('AuditLogsQuery.Read.All','AuditLog.Read.All','Directory.Read.All','Organization.Read.All') |
        Where-Object { $_ -notin (Get-MgContext).Scopes }
    if ($missing) { throw "Granted Graph scopes missing: $($missing -join ', '). Admin consent not granted on this app." }
}
```

### 2.3 Defensive session-URI assertion (called by every helper)

```powershell
function Assert-FsiExoSession {
    [CmdletBinding()]
    param()
    $conn = Get-ConnectionInformation | Where-Object State -eq 'Connected' |
        Where-Object { $_.ConnectionUri -match 'outlook\.office365\.com' } |
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
        [string[]]$RecordTypes = @('CopilotInteraction','ConnectedAIAppInteraction','PowerPlatformAdministratorActivity')
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

Always invoke first with `-WhatIf` (BL-§3).

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
        [int]$LookbackDays = 30
    )
    try {
        $start = (Get-Date).ToUniversalTime().AddDays(-$LookbackDays)
        $end   = (Get-Date).ToUniversalTime()
        $hit   = Search-UnifiedAuditLog -StartDate $start -EndDate $end -RecordType AIAppInteraction -ResultSize 1 -ErrorAction SilentlyContinue
        $observed = [bool]$hit

        # Azure billing binding (best-effort signal)
        $billingBound = $null
        try {
            $billingBound = [bool](Get-AzSubscription -ErrorAction SilentlyContinue | Select-Object -First 1)
        } catch { $billingBound = $null }

        $status = if ($observed) { 'Clean' }
                  elseif ($billingBound -eq $false) { 'Anomaly' }
                  else { 'Pending' }

        [pscustomobject]@{
            ControlId         = '1.7'
            Helper            = 'Get-FsiAuditPaygEnablement'
            Status            = $status
            AIAppInteractionObservedInLookback = $observed
            AzureBillingBound = $billingBound
            LookbackDays      = $LookbackDays
            CapturedAtUtc     = (Get-Date).ToUniversalTime().ToString('o')
            Note              = if ($status -eq 'Anomaly') { 'No Azure subscription detected for PAYG meter binding. AIAppInteraction capture is almost certainly off; opt in via Purview portal > Settings > Billing > Pay-as-you-go services.' }
                                elseif ($status -eq 'Pending') { 'PAYG opt-in cannot be confirmed from PowerShell alone; verify in Purview portal. Empty AIAppInteraction results may indicate either no shadow-AI use OR PAYG off — do not interpret as Clean without portal confirmation.' }
                                else { 'AIAppInteraction records observed; PAYG capture is active. Note: PAYG-captured records carry a 180-day retention floor regardless of Audit Premium licensing.' }
        }
    } catch {
        [pscustomobject]@{ ControlId='1.7'; Helper='Get-FsiAuditPaygEnablement'; Status='Error'; ErrorMessage=$_.Exception.Message; CapturedAtUtc=(Get-Date).ToUniversalTime().ToString('o') }
    }
}
```

---

## §6 — Mailbox audit bypass review (`Get-FsiMailboxAuditBypass`)

**Why this section exists.** A mailbox with a non-zero `AuditBypassEnabled` association does **not** emit mailbox events to the unified audit log — even if the user is otherwise in scope for Audit Premium and Copilot. Bypass is occasionally used legitimately for service accounts, but a regulated Copilot user with bypass enabled is a FINRA Rule 4511 / SEC 17a-4 finding.

```powershell
function Get-FsiMailboxAuditBypass {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param([string[]]$RegulatedUserPrincipalNames)

    try {
        Assert-FsiExoSession | Out-Null
        $bypassed = Get-MailboxAuditBypassAssociation -ResultSize Unlimited |
            Where-Object { $_.AuditBypassEnabled -eq $true } |
            Select-Object Identity, AuditBypassEnabled, WhenChangedUTC

        $regulatedHits = if ($RegulatedUserPrincipalNames) {
            $bypassed | Where-Object { $_.Identity -in $RegulatedUserPrincipalNames }
        } else { @() }

        [pscustomobject]@{
            ControlId        = '1.7'
            Helper           = 'Get-FsiMailboxAuditBypass'
            Status           = if ($regulatedHits) { 'Anomaly' } elseif ($bypassed) { 'Pending' } else { 'Clean' }
            BypassedCount    = ($bypassed | Measure-Object).Count
            RegulatedBypassed = $regulatedHits
            BypassedSample   = $bypassed | Select-Object -First 25
            CapturedAtUtc    = (Get-Date).ToUniversalTime().ToString('o')
            Note             = if ($regulatedHits) { 'Regulated user(s) have mailbox audit bypass enabled — mailbox-side audit is suppressed. Remove bypass and document the change in the change-management ticket.' }
                                elseif ($bypassed) { 'Service-account bypass detected. Review the list against the approved service-account inventory; remove any unrecognised entries.' }
                                else { 'No mailbox audit bypass associations.' }
        }
    } catch {
        [pscustomobject]@{ ControlId='1.7'; Helper='Get-FsiMailboxAuditBypass'; Status='Error'; ErrorMessage=$_.Exception.Message; CapturedAtUtc=(Get-Date).ToUniversalTime().ToString('o') }
    }
}
```

To remove bypass on a regulated user (mutation, idempotent get-then-set, confirm prompt):

```powershell
function Remove-FsiMailboxAuditBypass {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param([Parameter(Mandatory)] [string]$Identity)
    Assert-FsiExoSession | Out-Null
    $current = Get-MailboxAuditBypassAssociation -Identity $Identity -ErrorAction Stop
    if (-not $current.AuditBypassEnabled) {
        return [pscustomobject]@{ Status='Clean'; Action='NoOp'; Identity=$Identity }
    }
    if ($PSCmdlet.ShouldProcess($Identity,'Set-MailboxAuditBypassAssociation -AuditBypassEnabled $false')) {
        Set-MailboxAuditBypassAssociation -Identity $Identity -AuditBypassEnabled $false
    }
}
```

---

## §7 — Copilot / agent record-type queries (legacy + Graph forward path)

**Why this section exists.** `Search-UnifiedAuditLog` has a 5,000-per-call / 50,000-per-session ceiling and remains supported. Microsoft recommends the Office 365 Management Activity API for programmatic downloads. The [Graph Audit Search API](https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery?view=graph-rest-1.0) is another supported search surface, with its own [throttling and per-query completeness limits](https://learn.microsoft.com/en-us/graph/throttling-limits#security-audit-log-query-service-limits).

### 7.1 Legacy path: paginated, large-set, date-windowed search

```powershell
function Search-FsiAuditLogPaged {
    <#
    .SYNOPSIS
        Searches the four framework record types, paging each type/window independently.
        Splits capped windows and rejects windows too dense to establish completeness.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [datetime]$StartDate,
        [Parameter(Mandatory)] [datetime]$EndDate,
        [Parameter(Mandatory)]
        [ValidateSet('CopilotInteraction','ConnectedAIAppInteraction','AIAppInteraction','PowerPlatformAdministratorActivity')]
        [string[]]$RecordTypes,
        [string[]]$UserIds,
        [string[]]$Operations,
        [ValidateRange(1,5000)] [int]$PageSize = 5000
    )
    Assert-FsiExoSession | Out-Null
    if ($StartDate -ge $EndDate) { throw 'StartDate must precede EndDate.' }
    $results = [System.Collections.Generic.List[object]]::new()
    foreach ($recordType in $RecordTypes) {
        $pending = [System.Collections.Generic.Stack[object]]::new()
        $pending.Push(@{ Start = $StartDate; End = $EndDate })
        while ($pending.Count -gt 0) {
            $range = $pending.Pop()
            $sessionId = [guid]::NewGuid().ToString()
            $windowResults = [System.Collections.Generic.List[object]]::new()
            do {
                $batch = @(Search-UnifiedAuditLog -StartDate $range.Start -EndDate $range.End `
                    -RecordType $recordType -UserIds $UserIds -Operations $Operations `
                    -ResultSize $PageSize -SessionId $sessionId -SessionCommand ReturnLargeSet -ErrorAction Stop)
                foreach ($row in $batch) { $windowResults.Add($row) }
            } while ($batch.Count -gt 0 -and $windowResults.Count -lt 49000)

            if ($windowResults.Count -ge 49000) {
                $span = $range.End - $range.Start
                if ($span.TotalSeconds -le 2) {
                    throw "Cannot establish completeness for $recordType in $($range.Start)..$($range.End)."
                }
                $midpoint = $range.Start.AddTicks([long]($span.Ticks / 2))
                Write-Warning "Splitting capped $recordType window; discarded partial session $sessionId."
                $pending.Push(@{ Start = $midpoint; End = $range.End })
                $pending.Push(@{ Start = $range.Start; End = $midpoint })
                continue
            }
            foreach ($row in $windowResults) {
                if (-not $row.Identity) { throw 'Audit record identity missing; cannot reconcile duplicates.' }
                $results.Add($row)
            }
        }
    }
    $results | Sort-Object Identity -Unique
}

# Examples — the four Copilot/agent record types
$copilot     = Search-FsiAuditLogPaged -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) -RecordTypes 'CopilotInteraction'
$connectedAI = Search-FsiAuditLogPaged -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) -RecordTypes 'ConnectedAIAppInteraction'
$payg        = Search-FsiAuditLogPaged -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) -RecordTypes 'AIAppInteraction'    # PAYG — see §5
$studio      = Search-FsiAuditLogPaged -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) -RecordTypes 'PowerPlatformAdministratorActivity'
```

### 7.2 Forward path: Microsoft Graph audit endpoints

```powershell
# Directory audits (admin and configuration changes)
Get-MgAuditLogDirectoryAudit -Filter "activityDateTime ge $((Get-Date).AddDays(-7).ToString('yyyy-MM-ddTHH:mm:ssZ'))" -Top 100

# Sign-in logs (correlate agent identity sign-ins per Control 1.2 §8)
Get-MgAuditLogSignIn -Filter "createdDateTime ge $((Get-Date).AddDays(-1).ToString('yyyy-MM-ddTHH:mm:ssZ'))" -Top 100

# Audit Search query API (v1.0); see completeness and throttling caveats below
$query = @{
    '@odata.type'              = '#microsoft.graph.security.auditLogQuery'
    displayName                = 'Control 1.7 — CopilotInteraction last 24h'
    filterStartDateTime        = [DateTime]::UtcNow.AddHours(-24).ToString('o')
    filterEndDateTime          = [DateTime]::UtcNow.ToString('o')
    operationFilters           = @('CopilotInteraction')
}
$created = Invoke-MgGraphRequest -Method POST `
    -Uri 'https://graph.microsoft.com/v1.0/security/auditLog/queries' `
    -Body ($query | ConvertTo-Json) -ContentType 'application/json'

# Poll status, then page records
do {
    Start-Sleep -Seconds 10
    $state = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/security/auditLog/queries/$($created.id)"
} while ($state.status -in 'notStarted','running')

if ($state.status -ne 'succeeded') { throw "Audit query ended with status $($state.status)." }
if (-not $state.Contains('isRecordCountLimitExceeded')) {
    throw 'Completeness metadata absent; reconcile the result before accepting it.'
}
if ($state.isRecordCountLimitExceeded) { throw 'Audit query truncated; split the UTC window and retry.' }
$records = [System.Collections.Generic.List[object]]::new()
$next = "https://graph.microsoft.com/v1.0/security/auditLog/queries/$($created.id)/records?`$top=100"
do {
    $page = Invoke-MgGraphRequest -Method GET -Uri $next
    foreach ($record in $page.value) { $records.Add($record) }
    $next = $page.'@odata.nextLink'
} while ($next)
```

!!! warning "Successful query does not prove completeness"
    Graph can return `succeeded` after reaching its per-query record-count limit. Check `isRecordCountLimitExceeded`, exhaust pagination, and split capped windows. Production orchestration must also bound polling and handle HTTP 429 with `Retry-After` or exponential backoff. This example fails visibly rather than silently accepting missing completeness metadata.

---

## §8 — Cross-source content retrieval (DSPM for AI / eDiscovery Premium / Communication Compliance)

**Why this section exists.** The `CopilotInteraction` audit *record* is metadata only — `UserId`, `AgentId`, `Messages[].ID`, `IsPrompt`, detection flags. The prompt and response **text** lives in the Microsoft 365 Substrate (the per-user Copilot interaction history mailbox) and is reachable through:

| Surface | Hook | Use case |
|---|---|---|
| **DSPM for AI** (Control 1.6) | Compliance portal → DSPM for AI → Activity explorer; PowerShell surface is limited — DSPM for AI is currently portal-led | Compliance manager review of Copilot transcripts in-line with the audit record |
| **eDiscovery (Premium)** (Control 1.19) | `New-ComplianceCase`, `New-CaseHoldPolicy`, `New-ComplianceSearch` with Copilot-scoped location | Legal hold, collection, and review across custodians |
| **Communication Compliance** (Control 1.10) | `New-SupervisoryReviewPolicyV2` with Copilot conditions | FINRA Rule 3110 supervisory review of AI-generated communications |

### 8.1 eDiscovery Premium scoping example

```powershell
# Run from Connect-IPPSSession session (NOT Connect-ExchangeOnline)
$caseName = "Control-1.7-Copilot-Investigation-$(Get-Date -Format 'yyyyMMdd')"

if (-not (Get-ComplianceCase -Identity $caseName -ErrorAction SilentlyContinue)) {
    New-ComplianceCase -Name $caseName -CaseType AdvancedEdiscovery `
        -Description 'Control 1.7 — Copilot interaction collection for examination'
}

# Scope: per-user Copilot interaction mailbox locations
$custodians = @('jane.doe@contoso.com','john.roe@contoso.com')
New-ComplianceSearch -Name "$caseName-Search" `
    -ExchangeLocation $custodians `
    -ContentMatchQuery 'ItemClass:IPM.SkypeTeams.Message.Copilot.*'
```

> **Hedged note.** This pattern *supports* the content-tier obligations under SEC 17a-4(b)(4) and FINRA Rule 4511 when paired with §10 preservation. It does not, by itself, *guarantee* completeness of the books-and-records record set; verify scope against the Substrate documentation in [Microsoft Learn: Audit logs for Copilot and AI activities](https://learn.microsoft.com/en-us/purview/audit-copilot) at every change window.

The example's item class covers Microsoft 365 Copilot, not every AI application. Use the [current eDiscovery AI item-class table](https://learn.microsoft.com/en-us/purview/edisc-search-copilot-data#data-sources-for-ai-data) for workload-specific searches, or the portal **Item class > Copilot activity** condition for the documented cross-AI scope. Validate known messages before accepting the content export.

### 8.2 Communication Compliance Copilot policy stub

```powershell
# Policy authoring is portal-led; the PowerShell surface (New-SupervisoryReviewPolicyV2) is documented but
# Copilot-specific condition templates evolve quickly. See Control 1.10 playbook for the canonical authoring
# walkthrough; this stub is a hook for the cross-source evidence pack.
New-SupervisoryReviewPolicyV2 -Name 'FSI-Copilot-Supervision' `
    -Reviewers 'supervisor.group@contoso.com' -ReviewPercentage 100 -Confirm:$false -WhatIf
```

---

## §9 — Dataverse per-table audit on the six Copilot Studio entities (`Get-FsiCopilotStudioDataverseAudit`)

**Why this section exists.** Dataverse environment, table, and column settings govern data-change history. The six tables below are the framework-selected starting scope, not a Microsoft-mandated authoring-audit prerequisite. Confirm supported/installed tables and approved columns in each environment. [Copilot Studio authoring collection is enabled by default](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio) and must be tested separately using `PowerPlatformAdministratorActivity` operations.

The Power Apps Administration cmdlets that enumerate environments are **Desktop-only** (BL-§2; §0 trap). Spawn a Windows PowerShell 5.1 child process and bridge the result as JSON.

### 9.1 Read state across all environments

```powershell
function Get-FsiCopilotStudioDataverseAudit {
    <#
    .SYNOPSIS
        Reports per-environment, per-table audit state for the six Copilot Studio Dataverse entities.
    .NOTES
        Spawns a Windows PowerShell 5.1 child for the Microsoft.PowerApps.Administration.PowerShell leg.
        Per-table audit is queried via the Dataverse Web API (entity metadata IsAuditEnabled property).
    #>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param([Parameter(Mandatory)] [hashtable]$DataverseHeadersByEnvironment)
    try {
        $entities = @('bot','botcomponent','botcomponentcollection','conversationtranscript','aiplugin','aipluginauth')

        # Spawn PS 5.1 child to enumerate environments
        $child = @"
            Add-PowerAppsAccount | Out-Null
            Get-AdminPowerAppEnvironment |
                Where-Object { `$_.CommonDataServiceDatabaseProvisioningState -eq 'Succeeded' } |
                Select-Object EnvironmentName, DisplayName, @{n='WebApiUrl';e={`$_.Internal.properties.linkedEnvironmentMetadata.instanceApiUrl}} |
                ConvertTo-Json -Depth 4
"@
        $envsJson = & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command $child
        $envs = $envsJson | ConvertFrom-Json
        if (-not $envs) { throw 'No Dataverse environments returned; audit scope is not verified.' }

        $rows = foreach ($env in @($envs)) {
            $headers = $DataverseHeadersByEnvironment[$env.EnvironmentName]
            if (-not $headers) { throw "Dataverse authorization not supplied for $($env.EnvironmentName)." }
            # Per-environment org-level audit setting
            $orgUri = "$($env.WebApiUrl)/api/data/v9.2/organizations?`$select=isauditenabled,organizationid"
            $org = (Invoke-RestMethod -Method GET -Uri $orgUri -Headers $headers -ErrorAction Stop).value |
                Select-Object -First 1
            if (-not $org) { throw "No organization audit configuration returned for $($env.EnvironmentName)." }
            foreach ($e in $entities) {
                $metaUri = "$($env.WebApiUrl)/api/data/v9.2/EntityDefinitions(LogicalName='$e')?`$select=LogicalName,IsAuditEnabled"
                try {
                    $meta = Invoke-RestMethod -Method GET -Uri $metaUri -Headers $headers -ErrorAction Stop
                    [pscustomobject]@{
                        EnvironmentName    = $env.EnvironmentName
                        DisplayName        = $env.DisplayName
                        OrgAuditEnabled    = [bool]$org.isauditenabled
                        Entity             = $e
                        EntityAuditEnabled = [bool]$meta.IsAuditEnabled.Value
                    }
                } catch {
                    [pscustomobject]@{
                        EnvironmentName    = $env.EnvironmentName
                        DisplayName        = $env.DisplayName
                        OrgAuditEnabled    = [bool]$org.isauditenabled
                        Entity             = $e
                        EntityAuditEnabled = $null
                        Error              = $_.Exception.Message
                    }
                }
            }
        }
        $gaps = $rows | Where-Object { -not $_.OrgAuditEnabled -or -not $_.EntityAuditEnabled }
        [pscustomobject]@{
            ControlId    = '1.7'
            Helper       = 'Get-FsiCopilotStudioDataverseAudit'
            Status       = if ($gaps) { 'Anomaly' } else { 'Clean' }
            EnvironmentCount = ($envs | Measure-Object).Count
            Rows         = $rows
            GapCount     = ($gaps | Measure-Object).Count
            CapturedAtUtc= (Get-Date).ToUniversalTime().ToString('o')
            Note         = 'Per Microsoft Learn (May 2026 Dataverse change), before-and-after field change values will no longer flow to Microsoft Purview audit. Programs depending on field-level change records should retrieve them directly from Dataverse APIs in addition to UAL.'
        }
    } catch {
        [pscustomobject]@{ ControlId='1.7'; Helper='Get-FsiCopilotStudioDataverseAudit'; Status='Error'; ErrorMessage=$_.Exception.Message; CapturedAtUtc=(Get-Date).ToUniversalTime().ToString('o') }
    }
}
```

### 9.2 Idempotent enable across environments (mutation)

```powershell
function Enable-FsiCopilotStudioDataverseAudit {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$EnvironmentWebApiUrl,
        [Parameter(Mandatory)] [hashtable]$DataverseHeaders
    )

    $entities = @('bot','botcomponent','botcomponentcollection','conversationtranscript','aiplugin','aipluginauth')
    foreach ($e in $entities) {
        $metaUri = "$EnvironmentWebApiUrl/api/data/v9.2/EntityDefinitions(LogicalName='$e')"
        $current = Invoke-RestMethod -Method GET -Uri $metaUri `
            -Headers $DataverseHeaders -ErrorAction Stop
        if ($current.IsAuditEnabled.Value) { Write-Verbose "$e already audited; skipping."; continue }
        if (-not $current.IsAuditEnabled.CanBeChanged) { throw "$e auditing cannot be changed." }
        if ($PSCmdlet.ShouldProcess("$EnvironmentWebApiUrl :: $e", 'PUT EntityDefinition IsAuditEnabled=true + PublishXml')) {
            $current.IsAuditEnabled.Value = $true
            $putHeaders = @{} + $DataverseHeaders
            $putHeaders['MSCRM.MergeLabels'] = 'true'
            Invoke-RestMethod -Method PUT -Uri $metaUri -Headers $putHeaders -ErrorAction Stop `
                -Body ($current | ConvertTo-Json -Depth 10) `
                -ContentType 'application/json'
            $publishBody = @{ ParameterXml = "<importexportxml><entities><entity>$e</entity></entities></importexportxml>" } | ConvertTo-Json
            Invoke-RestMethod -Method POST -Uri "$EnvironmentWebApiUrl/api/data/v9.2/PublishXml" `
                -Headers $DataverseHeaders -Body $publishBody -ContentType 'application/json' -ErrorAction Stop | Out-Null
            $verified = Invoke-RestMethod -Method GET -Uri "$metaUri`?`$select=LogicalName,IsAuditEnabled" `
                -Headers $DataverseHeaders -ErrorAction Stop
            if (-not $verified.IsAuditEnabled.Value) { throw "$e audit enablement was not confirmed." }
        }
    }
}
```

Supply environment-specific Dataverse authorization headers through the firm's approved authentication flow; **Graph tokens are not Dataverse tokens**. Do not log or persist bearer values. The read helper takes a map keyed by environment name; the mutation helper takes headers for its one target environment. See [Dataverse authentication](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/authenticate-oauth) and [configure table and column auditing](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/auditing/configure#configure-tables-and-columns). The mutation example only changes table metadata: verify environment and column settings separately using the portal walkthrough.

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
        time-based retention policy. Computes SHA-256 manifest per BL-§4.
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

**Why this section exists.** Connector or analytics-rule presence does not prove ingestion. The [Microsoft Copilot connector](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference#microsoft-copilot) writes to `CopilotActivity`. Verify a known Purview audit record by `RecordId`; assess analytics rules separately. Inventory other AI/Power Platform destinations independently.

```powershell
function Test-FsiAuditToSentinel {
    <#
    .SYNOPSIS
        Verifies a known Purview audit record reached CopilotActivity.
    #>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroupName,
        [Parameter(Mandatory)] [string]$WorkspaceName,
        [Parameter(Mandatory)] [guid]$AuditRecordId
    )
    try {
        $workspace = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName `
            -Name $WorkspaceName -ErrorAction Stop
        $query = "CopilotActivity | where RecordId == '$AuditRecordId' | project RecordId, TimeGenerated"
        $result = Invoke-AzOperationalInsightsQuery -WorkspaceId $workspace.CustomerId `
            -Query $query -Timespan ([TimeSpan]::FromDays(7)) -ErrorAction Stop
        if ($result.Error) { throw ($result.Error | Out-String) }
        $rows = @($result.Results)

        [pscustomobject]@{
            ControlId             = '1.7'
            Helper                = 'Test-FsiAuditToSentinel'
            Status                = if ($rows.Count -gt 0) { 'Clean' } else { 'Anomaly' }
            AuditRecordId         = $AuditRecordId
            DestinationTable      = 'CopilotActivity'
            MatchedRows           = $rows.Count
            CapturedAtUtc         = (Get-Date).ToUniversalTime().ToString('o')
            Note                  = 'Known-record ingestion check only. Verify latency, other record types, and analytics-rule firing separately per Control 3.9.'
        }
    } catch {
        [pscustomobject]@{ ControlId='1.7'; Helper='Test-FsiAuditToSentinel'; Status='Error'; ErrorMessage=$_.Exception.Message; CapturedAtUtc=(Get-Date).ToUniversalTime().ToString('o') }
    }
}
```

---

## §12 — Evidence emission and quarterly attestation pack

**Why this section exists.** Audit-defensible evidence requires content-integrity proofs (BL-§4). Screenshots alone are not sufficient under SEC 17a-4(f) WORM requirements or FINRA 4511 record-keeping rules.

```powershell
function Save-FsiAuditEvidence {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory, ValueFromPipeline)] $InputObject,
        [Parameter(Mandatory)] [string]$Name,
        [string]$RootPath = ".\evidence\1.7"
    )
    process {
        if (-not (Test-Path $RootPath)) { New-Item -ItemType Directory -Path $RootPath -Force | Out-Null }
        $ts     = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
        $tenant = (Get-MgContext).TenantId
        $base   = Join-Path $RootPath "Control-1.7_${tenant}_${Name}_${ts}"
        $InputObject | ConvertTo-Json -Depth 30 | Set-Content -Path "$base.json" -Encoding UTF8
        $hash = (Get-FileHash -Path "$base.json" -Algorithm SHA256).Hash

        $manifestPath = Join-Path $RootPath 'manifest.json'
        $manifest = if (Test-Path $manifestPath) { @(Get-Content $manifestPath | ConvertFrom-Json) } else { @() }
        $manifest += [pscustomobject]@{
            file            = (Split-Path "$base.json" -Leaf)
            sha256          = $hash
            bytes           = (Get-Item "$base.json").Length
            generated_utc   = $ts
            control_id      = '1.7'
            helper_name     = $Name
            tenant_id       = $tenant
            script_version  = '1.4'
        }
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
Get-FsiCopilotStudioDataverseAudit -DataverseHeadersByEnvironment $dataverseHeadersByEnvironment |
    Save-FsiAuditEvidence -Name 'CopilotStudioDataverseAudit'
Test-FsiAuditTo17a4Preservation `
    -StorageAccountName 'fsiarchivewormprod' `
    -ContainerName 'audit-1-7'                    | Save-FsiAuditEvidence -Name '17a4PreservationPipeline'
Test-FsiAuditToSentinel `
    -ResourceGroupName 'rg-sec-prod' `
    -WorkspaceName 'la-sec-prod' `
    -AuditRecordId $knownRecentPurviewAuditId     | Save-FsiAuditEvidence -Name 'SentinelForwarding'

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
| Known-record Sentinel forwarding; separate analytics-rule firing test | Daily | `Test-FsiAuditToSentinel` with a recent known audit ID |
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

---

[Back to Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Portal Walkthrough](portal-walkthrough.md) · [Troubleshooting](troubleshooting.md)

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (documentation checked; tenant execution not tested)*
