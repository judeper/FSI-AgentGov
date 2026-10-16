# Control 1.7 — PowerShell Setup: Comprehensive Audit Logging and Compliance Automation

> **Scope.** This playbook provides examples and explicit evidence-review prerequisites for the **audit capture and preservation plane** for Control 1.7 across **Microsoft Purview Audit (Standard, Premium, and the 10-Year Audit Log Retention add-on), Microsoft 365 Copilot and agent record types (`CopilotInteraction`, `ConnectedAIAppInteraction`, `AIAppInteraction` (PAYG), `PowerPlatformAdministratorActivity`), Audit pay-as-you-go (PAYG) AI App Interaction enablement, environment-specific Dataverse auditing, the Microsoft Graph v1.0 audit search API, the Microsoft 365 Substrate content tier reachable through DSPM for AI / eDiscovery Premium / Communication Compliance, and an SEC 17a-4(f)-compatible preservation pipeline into Azure immutable blob storage** in US financial services tenants. It assumes you have already read [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) (referenced below as **BL-§N**) and the parent control specification [`../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).
>
> **What this playbook is.** A set of documentation-reviewed examples, not a tenant-tested turnkey harness: (a) module / CLI pins require CAB-supplied versions; (b) prefixed Exchange Online and Security & Compliance commands separate their provenance; (c) license, PAYG, and environment-specific Dataverse checks remain `Pending` until independent evidence is collected; (d) audit queries require completeness checks and tenant parity testing; (e) archive configuration and Sentinel rule inventory alone do not establish delivery; and (f) evidence files have SHA-256 hashes, but the manifest is not digitally signed. A 17a-4(f) preservation pipeline into an attested archive (Azure immutable blob with a *locked* time-based retention policy, or a third-party books-and-records connector) requires separate implementation and verification.
>
> **What this playbook is not.** It is not, by itself, a SEC Rule 17a-4(f)-compliant electronic recordkeeping system. Microsoft 365 Audit (including the 10-year add-on) is **record-CAPTURE operational telemetry**; preservation requires either WORM storage of the books-and-records record set (e.g., Azure immutable blob storage with a time-based retention policy in a *locked* state — Cohasset-attested for SEC 17a-4(f), CFTC 1.31, and FINRA 4511 — see [Microsoft Learn: Immutable storage for Azure blob data](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)) or the audit-trail alternative under the October 2022 amendments to Rule 17a-4(f) (compliance date 3 May 2023). This playbook does not yet verify that the export pipeline exists and is healthy; it does not, by itself, *guarantee* attestation, *eliminate* preservation risk, or replace the Designated Executive Officer (DEO) representation or Designated Third Party (DTP) undertaking required under the audit-trail alternative.
>
> **Hedged language reminder.** Output of this harness *supports compliance with* FINRA Rule 4511, FINRA Rule 3110, FINRA RN 24-09 / Rule 3110, SEC Rule 17a-3, SEC Rule 17a-4(b)(4) / 17a-4(f), SOX 302/404, GLBA 501(b), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Fed SR 26-2 (formerly SR 11-7), NIST AI RMF MEASURE 2.7 / GOVERN 1.4, CFTC Rule 1.31, and NYDFS 23 NYCRR 500.06. It does not, by itself, *ensure* a passing examination, *guarantee* completeness of the books-and-records record set, or *eliminate* the risk that a record type is silently re-classified between Audit Standard, Audit Premium, and Audit PAYG between Microsoft releases. Implementation requires that organizations verify Audit Premium licensing, PAYG opt-in scope, and Dataverse audit settings at every change window, and that they treat any preview surface as **additive** evidence rather than the sole source of truth.

| Field | Value |
|---|---|
| Control ID | 1.7 |
| Pillar | 1 — Security |
| Playbook | PowerShell Setup |
| PowerShell Edition | 7.4 LTS Core for these examples; Windows PowerShell 5.x for optional Power Apps Administration enumeration; verify EXO/IPPS and other module requirements against CAB-pinned versions |
| Cloud Scope | Commercial |
| Last UI Verified | October 2026 — documentation-only review; no tenant UI verification |
| Companion Playbooks | [`portal-walkthrough.md`](portal-walkthrough.md) · `verification-testing.md` (planned) · [`troubleshooting.md`](troubleshooting.md) |
| Related Controls | [1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) · [1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) · [1.19](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) · [2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) · [2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) · [3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) · [3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |

---

**Last Verified:** 2026-10-16 — live official Microsoft documentation review only. No tenant sessions, portal UI, licenses, ingestion, exports, or alerts were exercised. `Pending` placeholders are not passing evidence.

## §0 — Wrong-shell trap and audit-plane false-clean defects (READ FIRST)

**The defining fact of Control 1.7.** Audit configuration cmdlets in `ExchangeOnlineManagement` exist in **both** the Exchange Online (`Connect-ExchangeOnline`) and the Security & Compliance (`Connect-IPPSSession`) PowerShell connections, with the **same names** and **different return semantics**. Per Microsoft Learn, `Get-AdminAuditLogConfig.UnifiedAuditLogIngestionEnabled` **always returns `$false` from the Security & Compliance session**, regardless of the actual tenant state, because the property is a property of the Exchange Online configuration object — not the compliance one. A script that does not assert which session it is reading from is producing **audit-grade misinformation**.

A script that ignores this reality produces a **false-clean audit posture** — the worst Control 1.7 outcome. False-clean audit posture means examiners are told records were captured when they were not, breaks SEC 17a-4(b)(4) communications-retention attestation for broker-dealer Copilot rollouts, leaves FINRA Rule 3110 supervisory queues operating on incomplete sets, and invalidates the Cohasset attestation chain that downstream SEC 17a-4(f) preservation depends on.

**Why this section exists.** Eight classes of silent failure produce false-clean audit-plane output in Control 1.7 specifically:

1. **Wrong-shell trap on `Get-AdminAuditLogConfig`.** Always returns `$false` for `UnifiedAuditLogIngestionEnabled` from the Security & Compliance session. Helpers in §3 use the EXO-prefixed command and verify its module against the intended connection; finding any EXO session is insufficient.
2. **Validate record types, don't suppress errors.** `PowerPlatformAdminActivity` is not the documented `PowerPlatformAdministratorActivity` value. `Search-UnifiedAuditLog -RecordType` accepts a single enum value, not an array. An invalid value can cause parameter binding failure; do not promise a silent-zero behavior. Other relevant names include `CopilotInteraction`, `ConnectedAIAppInteraction`, `AIAppInteraction`, `MicrosoftFlow`, `PowerAppsApp`, and `PowerBIAudit`; validate against the pinned command's parameter type and confirm a known event for each required scenario.
3. **`Search-UnifiedAuditLog` `-ResultSize` truncation.** Default `-ResultSize 100`; per-call cap **5,000**; per-session ceiling **50,000**. Single-shot calls silently drop records past those limits. Use `-SessionCommand ReturnLargeSet` with a fresh `-SessionId` per date window, and split windows when the session ceiling is approached.
4. **Different audit APIs are not interchangeable.** `Search-AdminAuditLog` is deprecated in Exchange Online; its documented replacement is `Search-UnifiedAuditLog`, which remains supported. The Microsoft Graph v1.0 **Audit Search API** (`/security/auditLog/queries`) queries the unified log; `/auditLogs/directoryAudits` and `/auditLogs/signIns` query Microsoft Entra logs. The `Search-UnifiedAuditLog` reference recommends the Microsoft 365 Management Activity API for programmatic downloads; it does not establish a maintenance-only status.
5. **Policy presence does not prove retention entitlement.** Audit Standard's default is **180 days**. Premium's default one-year coverage is workload-specific, and a custom policy can shorten retention. Reconcile licenses and the highest-priority applicable policy (§4), not a blanket fallback assertion.
6. **PAYG record types require explicit opt-in.** `AIAppInteraction` and *some* `ConnectedAIAppInteraction` scenarios (non-Microsoft AI apps surfaced via Connected AI App) fall under [Audit pay-as-you-go billing](https://learn.microsoft.com/en-us/purview/purview-billing-models). Until the PAYG meter is turned on, these records do not flow at all.
7. **Dataverse auditing is distinct from default Copilot Studio SDK events.** Dataverse change auditing requires environment, table, and column settings. Copilot Studio administrative activity collection is enabled by default and can't be disabled. Microsoft does not document a universal six-table prerequisite; solution audit customizations can be exported, but verify the target environment and managed-property restrictions.
8. **Single-credential read+write.** Running this harness with the same service principal that *modifies* audit configuration breaks SOX 404 separation of duties — the principal that produces the evidence could be the principal that altered the configuration the evidence describes. Use a separate `agt17-audit-reader` audit-only principal.

**Top false-clean defects unique to audit-plane automation.**

| # | Defect | What it looks like | How this playbook traps it |
|---|---|---|---|
| 1 | `Get-AdminAuditLogConfig` from `Connect-IPPSSession` | `UnifiedAuditLogIngestionEnabled = False` regardless of truth | §3 prefixed EXO command and module-provenance assertion |
| 2 | `Search-UnifiedAuditLog -RecordType PowerPlatformAdminActivity` | Invalid enum can fail binding | §7 checks the imported command's actual parameter type and fails closed |
| 3 | `Search-UnifiedAuditLog` without pagination | Caps at 100 / 5,000 / 50,000 silently | §7 `Search-FsiAuditLogPaged` with `ReturnLargeSet` and date-window splitter |
| 4 | Custom retention policy without required per-user licensing | Requested duration is not established by policy presence | §4 requires effective service-plan and policy evidence; placeholder returns `Pending` |
| 5 | `AIAppInteraction` queried but PAYG never enabled | Empty result interpreted as "no shadow AI" | §5 requires Purview billing configuration evidence; placeholder returns `Pending` |
| 6 | Mailbox audit bypass set on a regulated user | `Search-UnifiedAuditLog` returns no mailbox events for that user | §6 `Get-FsiMailboxAuditBypass` enumerates non-zero bypass associations |
| 7 | Dataverse environment/table audit mistaken for SDK activity capture | Different audit streams conflated | §9 requires environment-specific scope and evidence |
| 8 | "Audit captured = books-and-records preserved" assumption | 17a-4(f) attestation chain broken | §10 configuration check remains `Pending` without delivery/retrieval evidence |
| 9 | Sentinel connector/rule objects mistaken for ingestion | Events or alerts may be absent | §11 inventory remains `Pending` without workspace and alert evidence |
| 10 | Commercial Graph endpoint mistaken for tenant selection | Correct endpoint, wrong tenant | §2 requires explicit tenant ID; `Global` is the default cloud, not tenant identity |

**Required shell guard (run this at the top of every Control 1.7 session).**

```powershell
# Save as: scripts/Assert-Agt17Shell.ps1
[CmdletBinding()]
[OutputType([void])]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [version]'7.4.0') {
    Write-Error "These examples require PowerShell 7.4+ Core (pwsh). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Optional Power Apps Administration commands require a separate Windows PowerShell 5.x process."
    exit 2
}

# Stale Windows PowerShell module shadowing trap
$bad = Get-Module -ListAvailable -Name 'Microsoft.Graph' |
    Where-Object { $_.Version.Major -lt 2 }
if ($bad) {
    Write-Error "Microsoft.Graph v1 is visible: $($bad.Version -join ', '). This example requires explicit CAB-pinned imports; resolve module selection before continuing."
    exit 2
}
Write-Verbose "Control 1.7 shell guard passed: pwsh $($PSVersionTable.PSVersion)"
```

---

## §1 — Module, CLI, and permission matrix

**Why this section exists.** Declare and record CAB-approved versions separately with the evidence. The examples below do not install pins automatically, and §12 does not currently record a module inventory. Microsoft Graph audit search is documented in v1.0; pin and test the SDK version your CAB has approved. See **BL-§1** for the canonical pinning pattern.

### 1.1 Pinned PowerShell modules

| Module | Edition | Approved Pinning Pattern | Purpose |
|---|---|---|---|
| `ExchangeOnlineManagement` | Core or Desktop (verify per version) | `Install-Module ExchangeOnlineManagement -RequiredVersion '<CAB version>' -Repository PSGallery -Scope CurrentUser` | EXO for ingestion status, mailbox bypass, and `Search-UnifiedAuditLog`; IPPS for retention policies and supported compliance operations. Use the distinct prefixes in §2. See [Connect to Exchange Online PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-exchange-online-powershell) and [Connect to Security & Compliance PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell). |
| `Microsoft.Graph.Reports` | Core | `Install-Module Microsoft.Graph.Reports -RequiredVersion '<CAB version>' -Repository PSGallery -Scope CurrentUser` | `Get-MgAuditLogDirectoryAudit`, `Get-MgAuditLogSignIn` query Microsoft Entra logs, not the unified Microsoft 365 audit log. See [Microsoft Graph audit logs](https://learn.microsoft.com/en-us/graph/api/resources/azure-ad-auditlog-overview). |
| `Microsoft.Graph.Security` | Core | Same CAB-pinned pattern | Graph v1.0 Audit Search (`/security/auditLog/queries`), including [`New-MgSecurityAuditLogQuery`](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.security/new-mgsecurityauditlogquery). Beta SDK counterpart is `Microsoft.Graph.Beta.Security`, not `Beta.Reports`. |
| `Microsoft.Graph.Authentication` | Core | Pinned with the meta module | `Connect-MgGraph -Environment 'Global'` for commercial tenants. |
| `Microsoft.Graph.Users` / `Microsoft.Graph.Identity.DirectoryManagement` | Core | Pinned with the meta module | License entitlement reconciliation (§4) and tenant SKU enumeration. |
| `Microsoft.PowerApps.Administration.PowerShell` | **Desktop only** (PS 5.x) per Microsoft Learn | `Install-Module Microsoft.PowerApps.Administration.PowerShell -RequiredVersion '<CAB version>' -Repository PSGallery -Scope CurrentUser` | Optional environment enumeration. Microsoft documents .NET Framework incompatibility with PowerShell 6+; it does not promise a specific silent-empty failure. A separate process requires its own authentication and exit-code checks. |
| `Az.Accounts`, `Az.Storage` | Core | `Install-Module Az.Storage -RequiredVersion '<CAB version>'` | §10 17a-4(f) preservation pipeline: enumerate immutable containers, verify time-based retention is **locked**, validate export blobs. |
| `Az.OperationalInsights`, `Az.SecurityInsights` | Core | Same pattern | Optional Sentinel inventory/workspace queries; §11 remains an evidence prerequisite, not an implemented end-to-end verifier. |
| Microsoft Power Platform CLI (`pac`) | n/a | CAB-pinned supported distribution | Optional organization-level settings inspection: `pac env list-settings`; changes use `pac env update-settings`, not `pac org settings update`. This does not configure table/column auditing. |

### 1.2 Permission matrix (least-privilege; separate read and write principals)

| Surface | Read role | Write role | Notes |
|---|---|---|---|
| Tenant unified audit log status | Confirm cmdlet RBAC in the target tenant | `Audit Logs` in Exchange Online for enable/disable | Retention-policy authoring separately requires `Organization Configuration` in Purview. |
| Audit search (legacy) | `View-Only Audit Logs` | n/a | Assigned in Exchange admin center role groups. |
| Audit search (Graph) | `AuditLogsQuery.Read.All` for cross-workload unified audit search (delegated or application); service-specific alternatives exist | n/a | `AuditLog.Read.All` is for Entra audit/sign-in APIs. Validate actual query access, not just context scopes. |
| Audit retention policies | Confirm cmdlet RBAC in the target tenant | `Organization Configuration` on **Roles & scopes** in the Microsoft Purview portal | `Get/New/Set/Remove-UnifiedAuditLogRetentionPolicy` use Security & Compliance PowerShell. |
| Mailbox audit bypass | Confirm `Get-MailboxAuditBypassAssociation` RBAC in the target tenant | Confirm `Set-MailboxAuditBypassAssociation` RBAC in the target tenant | Do not infer command access from a role-group label alone. |
| License entitlement | `LicenseAssignment.Read.All` for SKU/license details; `User.Read.All` for user enumeration | n/a | Reconcile effective service-plan provisioning and policy scope, not guessed SKU names. |
| Dataverse per-table audit | Dataverse access and applicable privileges for each environment | `System Administrator`, `System Customizer`, or equivalent Dataverse permissions | Power Platform environment enumeration is not Dataverse metadata authorization. |
| 17a-4(f) preservation pipeline | Management-plane policy read permission plus `Storage Blob Data Reader` for blob retrieval | Separate management-plane policy permissions and `Storage Blob Data Contributor` for blob upload | Time-based retention policies must be in the **Locked** state to satisfy 17a-4(f). |
| Sentinel forwarding | `Microsoft Sentinel Reader` plus applicable workspace query access | `Microsoft Sentinel Contributor` for Sentinel configuration | Microsoft Copilot connector configuration, `CopilotActivity` queries, and actual alert evidence are separate checks. |

**SOX 404 separation of duties.** This playbook assumes `agt17-audit-reader` (read-only across all surfaces above) is *distinct* from any principal that mutates audit configuration. The reader principal authenticates with a certificate (no client secret) per BL-§3.

---

## §2 — Authentication bootstrap

**Why this section exists.** Cloud selection and tenant selection are separate. `Global` is Graph's default environment; specifying it does not select a tenant. Use an explicit tenant ID and distinct EXO/IPPS prefixes. These connection examples require pre-provisioned consent, roles, certificates where applicable, and CAB-pinned imports; connecting does not prove authorization for every helper.

### 2.1 Two distinct connections (interactive flow)

```powershell
function Connect-Agt17Audit {
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)] [string]$UserPrincipalName,
        [Parameter(Mandatory)] [string]$TenantId
    )

    if ($PSCmdlet.ShouldProcess('Exchange Online','Connect-ExchangeOnline')) {
        Connect-ExchangeOnline -UserPrincipalName $UserPrincipalName -Prefix Agt17Exo -ShowBanner:$false
    }
    if ($PSCmdlet.ShouldProcess('Security & Compliance','Connect-IPPSSession')) {
        Connect-IPPSSession -UserPrincipalName $UserPrincipalName -Prefix Agt17Ip
    }
    if ($PSCmdlet.ShouldProcess('Microsoft Graph','Connect-MgGraph')) {
        Connect-MgGraph -Environment 'Global' -TenantId $TenantId -ContextScope Process -Scopes @(
            'AuditLogsQuery.Read.All','AuditLog.Read.All','LicenseAssignment.Read.All','User.Read.All'
        ) -NoWelcome
    }
    if ($PSCmdlet.ShouldProcess('Azure','Connect-AzAccount')) {
        Connect-AzAccount -Environment 'AzureCloud' -Tenant $TenantId | Out-Null
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
            -AppId $AppId -CertificateThumbprint $CertificateThumbprint -Organization $Organization -Prefix Agt17Exo -ShowBanner:$false
    }
    if ($PSCmdlet.ShouldProcess('Security & Compliance','Connect-IPPSSession (cert)')) {
        Connect-IPPSSession -AppId $AppId -CertificateThumbprint $CertificateThumbprint -Organization $Organization -Prefix Agt17Ip
    }
    if ($PSCmdlet.ShouldProcess('Microsoft Graph','Connect-MgGraph (cert)')) {
        Connect-MgGraph -Environment 'Global' -ClientId $AppId -CertificateThumbprint $CertificateThumbprint -TenantId $TenantId -NoWelcome
    }
    # App permissions require prior admin consent; validate with the intended API.
    # Azure and Dataverse require separate resource-specific authentication.
}
```

### 2.3 Defensive EXO command-provenance assertion

Use a fresh PowerShell process with CAB-pinned module imports. The `Agt17Exo` and `Agt17Ip` prefixes prevent shared names from being resolved to the wrong imported connection. [`Get-ConnectionInformation`](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-connectioninformation) exposes `ModuleName`, `ModulePrefix`, `TenantID`, and `IsEopSession`; availability and generated-module matching must be checked against the pinned module in a tenant test. A mismatch is an error, never permission to fall back to an unprefixed command.

```powershell
function Assert-FsiExoSession {
    [CmdletBinding()]
    param([string]$CommandName = 'Get-Agt17ExoAdminAuditLogConfig')
    $connections = @(Get-ConnectionInformation |
        Where-Object { $_.State -eq 'Connected' -and $_.ModulePrefix -eq 'Agt17Exo' -and -not $_.IsEopSession })
    if ($connections.Count -ne 1) {
        throw 'Exactly one Agt17Exo connection is required; use a fresh process and reconnect.'
    }
    $conn = $connections[0]
    $graph = Get-MgContext
    if (-not $graph -or $graph.Environment -ne 'Global' -or $conn.TenantID -ne $graph.TenantId) {
        throw 'EXO and commercial Graph tenant contexts must match the explicitly selected tenant.'
    }
    $command = Get-Command $CommandName -ErrorAction Stop
    if ($command.ModuleName -ne $conn.ModuleName) {
        throw 'EXO command module does not match the intended connection.'
    }
    # Repeat command provenance checks for additional imported commands if connections change.
    return $conn
}
```

---

## §3 — Tenant unified audit log enablement (`Get-FsiAuditCopilotEnablement`)

**Why this section exists.** When unified audit logging is disabled, UAL searches return no results. That is distinct from whether a product collects administrative SDK activity internally. Status checks must run from the EXO session (BL-§0; §0 trap #1).

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
        [ValidateRange(1,720)] [int]$LookbackHours = 24,
        [ValidateCount(1,100)] [string[]]$RecordTypes = @('CopilotInteraction','ConnectedAIAppInteraction','PowerPlatformAdministratorActivity')
    )
    try {
        $conn = Assert-FsiExoSession
        $cfg  = Get-Agt17ExoAdminAuditLogConfig -ErrorAction Stop
        $ingestEnabled = [bool]$cfg.UnifiedAuditLogIngestionEnabled

        $start = (Get-Date).ToUniversalTime().AddHours(-$LookbackHours)
        $end   = (Get-Date).ToUniversalTime()
        $flowing = foreach ($rt in $RecordTypes) {
            Assert-FsiExoSession -CommandName 'Search-Agt17ExoUnifiedAuditLog' | Out-Null
            $hit = Search-Agt17ExoUnifiedAuditLog -StartDate $start -EndDate $end -RecordType $rt -ResultSize 1 -ErrorAction Stop
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
            Note                            = if (-not $ingestEnabled) { 'Tenant unified audit logging is OFF; UAL search availability is not established. Coordinate enablement per portal-walkthrough.md.' }
                                              elseif ($status -eq 'Pending') { 'Ingestion enabled but required record types were not observed. Configuration can take up to 60 minutes; events can take several hours to become searchable. Corroborate with known activity.' }
                                              else { 'Clean applies only to the ingestion setting and observed sample flow; it does not verify complete capture, required channel coverage, retention, or preservation.' }
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
    $before = Get-Agt17ExoAdminAuditLogConfig -ErrorAction Stop
    if ($before.UnifiedAuditLogIngestionEnabled) {
        Write-Verbose "Already enabled; no mutation."
        return [pscustomobject]@{ Status='Clean'; Action='NoOp'; SessionUri=$conn.ConnectionUri }
    }
    if ($PSCmdlet.ShouldProcess('Tenant', 'Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true')) {
        Assert-FsiExoSession -CommandName 'Set-Agt17ExoAdminAuditLogConfig' | Out-Null
        Set-Agt17ExoAdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true -ErrorAction Stop
        Write-Warning 'Submitted. Per Microsoft Learn, allow up to 60 minutes for configuration propagation; ingestion of events takes longer. Re-run Get-FsiAuditCopilotEnablement after the propagation window before stamping Clean.'
        return [pscustomobject]@{ Status='Pending'; Action='Set'; SessionUri=$conn.ConnectionUri }
    }
}
```

Always invoke first with `-WhatIf` (BL-§3).

---

## §4 — Audit (Premium) and 10-Year Audit Log Retention add-on entitlement (`Get-FsiAuditPremiumStatus`)

**Why this section exists.** A custom retention policy does not establish the required per-user license entitlement. Audit Premium's default one-year policy covers Exchange, SharePoint, OneDrive, and Entra workloads; other workloads, including Copilot, default to 180 days unless an applicable custom policy changes the duration. Retention beyond one year requires the applicable add-on; the 10-year add-on is not mandatory for every Copilot user. Reconcile effective licensing and the highest-priority applicable policy **before** claiming retention coverage to examiners. See [Manage audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies).

**Supported custom policy durations and entitlement.** Microsoft documents **7 Days, 30 Days, 6 Months, 9 Months, 1 Year, 3 Years, 5 Years, and 7 Years**, plus **10 Years** with the 10-Year Audit Log Retention add-on. The **3-, 5-, and 7-year** options require that add-on **in addition to Microsoft 365 Enterprise E5**; the 7- and 30-day options also require Microsoft 365 Enterprise E5. The add-on's name does not force every policy to retain data for ten years. Select the approved record-class duration and verify each generating user's entitlement and applicable policy; these examples do not verify either. Creating or modifying audit retention policies requires **Organization Configuration** on **Roles & scopes** in the Microsoft Purview portal.

```powershell
function Get-FsiAuditPremiumStatus {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param()
    [pscustomobject]@{
        ControlId = '1.7'; Helper = 'Get-FsiAuditPremiumStatus'; Status = 'Pending'
        CapturedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        Note = 'Manual evidence prerequisite: enumerate the intended user population, resolve SKU/service-plan IDs using Microsoft licensing reference and tenant license details, check provisioning/disabled plans, and reconcile policy scope, priority, and required duration. No entitlement or retention coverage has been verified.'
    }
}
```

---

## §5 — Audit pay-as-you-go (PAYG) AI App Interaction enablement (`Get-FsiAuditPaygEnablement`)

**Why this section exists.** `AIAppInteraction` and some non-Microsoft `ConnectedAIAppInteraction` scenarios require [Audit pay-as-you-go enablement](https://learn.microsoft.com/en-us/purview/audit-copilot). Microsoft documents **180-day retention**, not a universal retention floor or a Premium override rule. Microsoft applications, including Copilot Studio custom applications, are included in Audit Standard. Empty search results don't distinguish missing enablement from no activity or unsupported coverage.

```powershell
function Get-FsiAuditPaygEnablement {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param()
    [pscustomobject]@{
        ControlId = '1.7'; Helper = 'Get-FsiAuditPaygEnablement'; Status = 'Pending'
        CapturedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        Note = 'Manual evidence prerequisite: confirm the Microsoft 365 tenant is associated with the intended active Azure subscription and the applicable Purview PAYG features are enabled. Get-AzSubscription only lists accessible subscriptions; it does not prove a Purview billing association. Corroborate configuration with a known, recent in-scope event.'
    }
}
```

---

## §6 — Mailbox audit bypass review (`Get-FsiMailboxAuditBypass`)

**Why this section exists.** `AuditBypassEnabled` applies to the **acting account**: its access or actions against **any mailbox** aren't logged. It does not disable all other actors' events on that account's own mailbox, and doesn't establish suppression of Copilot interaction events. Bypass is occasionally used legitimately for service accounts, but a regulated Copilot user with bypass enabled is a FINRA Rule 4511 / SEC 17a-4 finding.

```powershell
function Get-FsiMailboxAuditBypass {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param([string[]]$RegulatedUserPrincipalNames)

    try {
        Assert-FsiExoSession -CommandName 'Get-Agt17ExoMailboxAuditBypassAssociation' | Out-Null
        $bypassed = Get-Agt17ExoMailboxAuditBypassAssociation -ResultSize Unlimited -ErrorAction Stop |
            Where-Object { $_.AuditBypassEnabled -eq $true } |
            Select-Object Identity, AuditBypassEnabled, WhenChangedUTC

        # Identity is not guaranteed to be a UPN; resolve stable IDs before population matching.
        $regulatedHits = @()

        [pscustomobject]@{
            ControlId        = '1.7'
            Helper           = 'Get-FsiMailboxAuditBypass'
            Status           = if ($bypassed) { 'Pending' } else { 'Clean' }
            BypassedCount    = ($bypassed | Measure-Object).Count
            RegulatedBypassed = $regulatedHits
            BypassedSample   = $bypassed | Select-Object -First 25
            CapturedAtUtc    = (Get-Date).ToUniversalTime().ToString('o')
            Note             = if ($regulatedHits) { 'Regulated user(s) have mailbox audit bypass enabled — mailbox-side audit is suppressed. Remove bypass and document the change in the change-management ticket.' }
                                elseif ($bypassed) { 'Bypass accounts detected; population matching is not implemented. Resolve each Identity to a stable recipient ID/UPN and review all actors before classification.' }
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
    if ([string]::IsNullOrWhiteSpace($Identity)) { throw 'Identity must not be empty.' }
    Assert-FsiExoSession -CommandName 'Get-Agt17ExoMailboxAuditBypassAssociation' | Out-Null
    $current = @(Get-Agt17ExoMailboxAuditBypassAssociation -Identity $Identity -ErrorAction Stop)
    if ($current.Count -ne 1) { throw 'Identity must resolve to exactly one bypass association.' }
    if (-not $current.AuditBypassEnabled) {
        return [pscustomobject]@{ Status='Clean'; Action='NoOp'; Identity=$Identity }
    }
    if ($PSCmdlet.ShouldProcess($Identity,'Set-MailboxAuditBypassAssociation -AuditBypassEnabled $false')) {
        Assert-FsiExoSession -CommandName 'Set-Agt17ExoMailboxAuditBypassAssociation' | Out-Null
        Set-Agt17ExoMailboxAuditBypassAssociation -Identity $Identity -AuditBypassEnabled $false -ErrorAction Stop
        $after = @(Get-Agt17ExoMailboxAuditBypassAssociation -Identity $Identity -ErrorAction Stop)
        if ($after.Count -ne 1 -or $after[0].AuditBypassEnabled) { throw 'Bypass removal read-back failed.' }
    }
}
```

---

## §7 — Copilot / agent record-type queries (legacy + Graph forward path)

**Why this section exists.** The supported `Search-UnifiedAuditLog` and [Graph v1.0 audit search](https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogquery?view=graph-rest-1.0) are distinct query paths. Entra directory/sign-in logs aren't replacements for unified audit. Establish parity for each required record type in your tenant. For continuous programmatic downloads, also evaluate the [Microsoft 365 Management Activity API](https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference), recommended by the cmdlet reference.

### 7.1 Legacy path: paginated, large-set, date-windowed search

```powershell
function Search-FsiAuditLogPaged {
    <#
    .SYNOPSIS
        Paginated Search-UnifiedAuditLog wrapper. Validates RecordType enum, uses ReturnLargeSet with a fresh
        SessionId per date window, and splits the window when the 50,000 session ceiling is approached.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [datetime]$StartDate,
        [Parameter(Mandatory)] [datetime]$EndDate,
        [Parameter(Mandatory)] [string[]]$RecordTypes,
        [string[]]$UserIds,
        [string[]]$Operations,
        [int]$PageSize = 5000
    )
    Assert-FsiExoSession -CommandName 'Search-Agt17ExoUnifiedAuditLog' | Out-Null
    if ($PageSize -lt 1 -or $PageSize -gt 5000) { throw 'PageSize must be 1..5000.' }
    $StartDate = $StartDate.ToUniversalTime()
    $EndDate = $EndDate.ToUniversalTime()
    if ($StartDate -ge $EndDate -or -not $RecordTypes.Count) { throw 'Invalid time range or empty record types.' }
    $command = Get-Command Search-Agt17ExoUnifiedAuditLog -ErrorAction Stop
    $enumType = $command.Parameters['RecordType'].ParameterType
    if (-not $enumType.IsEnum) { throw 'RecordType enum unavailable; validate the pinned module before use.' }
    $valid = [Enum]::GetNames($enumType)
    foreach ($rt in $RecordTypes) {
        if ($rt -notin $valid) { throw "Invalid RecordType: $rt" }
    }
    $results = [System.Collections.Generic.List[object]]::new()
    foreach ($rt in $RecordTypes) {
        $cursor = $StartDate
        $window = [TimeSpan]::FromDays(1)
        while ($cursor -lt $EndDate) {
            $windowEnd = if ($cursor.Add($window) -lt $EndDate) { $cursor.Add($window) } else { $EndDate }
            $sessionId = [guid]::NewGuid().ToString()
            $windowResults = [System.Collections.Generic.List[object]]::new()
            $seen = [System.Collections.Generic.HashSet[string]]::new()
            do {
                $parameters = @{
                    StartDate = $cursor; EndDate = $windowEnd; RecordType = $rt
                    ResultSize = $PageSize; SessionId = $sessionId
                    SessionCommand = 'ReturnLargeSet'; ErrorAction = 'Stop'
                }
                if ($UserIds) { $parameters.UserIds = $UserIds }
                if ($Operations) { $parameters.Operations = $Operations }
                $batch = @(Search-Agt17ExoUnifiedAuditLog @parameters)
                foreach ($row in $batch) {
                    if (-not $row.Identity) { throw 'Audit row lacks a stable Identity; completeness unknown.' }
                    if (-not $seen.Add([string]$row.Identity)) { throw 'Repeated audit row/page; stop rather than report completeness.' }
                    $windowResults.Add($row)
                }
            } while ($batch.Count -gt 0 -and $windowResults.Count -lt 49000)
            if ($windowResults.Count -ge 49000) {
                if ($window.TotalSeconds -le 1) { throw 'Dense one-second window exceeds safe session size; use an alternate export path.' }
                $window = [TimeSpan]::FromSeconds([Math]::Max(1, $window.TotalSeconds / 2))
                continue
            }
            $results.AddRange($windowResults)
            $cursor = $windowEnd
        }
    }
    # Adjacent windows can overlap at their boundary.
    return $results | Sort-Object Identity -Unique
}

# Examples — the four Copilot/agent record types
$copilot     = Search-FsiAuditLogPaged -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) -RecordTypes 'CopilotInteraction'
$connectedAI = Search-FsiAuditLogPaged -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) -RecordTypes 'ConnectedAIAppInteraction'
$payg        = Search-FsiAuditLogPaged -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) -RecordTypes 'AIAppInteraction'    # PAYG — see §5
$studio      = Search-FsiAuditLogPaged -StartDate (Get-Date).AddDays(-30) -EndDate (Get-Date) -RecordTypes 'PowerPlatformAdministratorActivity'
```

### 7.2 Forward path: Microsoft Graph audit endpoints

The live [Graph v1.0 `auditLogRecordType` enum](https://learn.microsoft.com/en-us/graph/api/resources/security-auditlogrecordtype?view=graph-rest-1.0) does not list `CopilotInteraction`, `ConnectedAIAppInteraction`, `AIAppInteraction`, or `PowerPlatformAdministratorActivity`. Do not copy the UAL enum values into Graph `recordTypeFilters`. Related documented members such as `CRM`, `PowerPlatformAdminDlp`, and `PowerPlatformAdminEnvironment` are not interchangeable substitutes. Use documented operation filters where the required operations are known, or omit record-type filtering and validate coverage against known events; no tenant parity is established here.

```powershell
# Entra-only correlation examples; not unified audit exports.
Get-MgAuditLogDirectoryAudit -Filter "activityDateTime ge $((Get-Date).ToUniversalTime().AddDays(-7).ToString('yyyy-MM-ddTHH:mm:ssZ'))" -All

# Sign-in logs (correlate agent identity sign-ins per Control 1.2 §8)
Get-MgAuditLogSignIn -Filter "createdDateTime ge $((Get-Date).ToUniversalTime().AddDays(-1).ToString('yyyy-MM-ddTHH:mm:ssZ'))" -All

# Audit Search v1.0. Requires AuditLogsQuery.Read.All, not AuditLog.Read.All.
# Use operationFilters rather than assuming a newer record type is in the Graph enum.
$query = @{
    '@odata.type'              = '#microsoft.graph.security.auditLogQuery'
    displayName                = 'Control 1.7 — CopilotInteraction last 24h'
    filterStartDateTime        = (Get-Date).ToUniversalTime().AddHours(-24).ToString('o')
    filterEndDateTime          = (Get-Date).ToUniversalTime().ToString('o')
    operationFilters           = @('CopilotInteraction')
}
$created = Invoke-MgGraphRequest -Method POST `
    -Uri 'https://graph.microsoft.com/v1.0/security/auditLog/queries' `
    -Body ($query | ConvertTo-Json) -ContentType 'application/json' -ErrorAction Stop

# Poll status, then page records
$deadline = (Get-Date).AddMinutes(15) # Example timeout; tune for measured tenant latency.
do {
    if ((Get-Date) -ge $deadline) { throw 'Audit query timed out; no complete result asserted.' }
    Start-Sleep -Seconds 10
    $state = Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/security/auditLog/queries/$($created.id)" -ErrorAction Stop
} while ($state.status -in 'notStarted','running')
if ($state.status -ne 'succeeded') { throw "Audit query ended with status $($state.status)." }
if ($state.isRecordCountLimitExceeded) { throw 'Query succeeded but exceeded its record limit; split the date range.' }
$records = [System.Collections.Generic.List[object]]::new()
$next = "https://graph.microsoft.com/v1.0/security/auditLog/queries/$($created.id)/records?`$top=100"
while ($next) {
    $page = Invoke-MgGraphRequest -Method GET -Uri $next -ErrorAction Stop
    foreach ($record in $page.value) { $records.Add($record) }
    $next = $page.'@odata.nextLink'
}
# Compare a known in-scope event and required record-type coverage across query paths.
# Pagination doesn't prove the source captured every expected event.
```

!!! warning "Search-UnifiedAuditLog deprecation status"
    As of the October 2026 documentation review, `Search-UnifiedAuditLog` remains supported. `Search-AdminAuditLog` is deprecated in Exchange Online and its reference points to `Search-UnifiedAuditLog`. Graph audit search is documented in v1.0, not beta-only. Verify workload/record-type parity and service limits rather than treating any one path as a complete drop-in replacement.

---

## §8 — Cross-source content retrieval (DSPM for AI / eDiscovery Premium / Communication Compliance)

**Why this section exists.** The `CopilotInteraction` audit *record* is metadata only — `UserId`, `AgentId`, `Messages[].ID`, `IsPrompt`, detection flags. The prompt and response **text** lives in the Microsoft 365 Substrate (the per-user Copilot interaction history mailbox) and is reachable through:

| Surface | Hook | Use case |
|---|---|---|
| **DSPM for AI** (Control 1.6) | Compliance portal → DSPM for AI → Activity explorer; PowerShell surface is limited — DSPM for AI is currently portal-led | Compliance manager review of Copilot transcripts in-line with the audit record |
| **eDiscovery (Premium)** (Control 1.19) | Current eDiscovery case/search workflow; mailbox and item-class scope must be verified | Legal hold, collection, and review across custodians |
| **Communication Compliance** (Control 1.10) | Portal-led Copilot policy configuration; a policy object alone does not define complete detection rules | FINRA Rule 3110 supervisory review of AI-generated communications |

### 8.1 eDiscovery Premium scoping example

**Non-executable scoping sketch — not a completed collection.** In the current eDiscovery experience, create a case and a search with the intended custodians' mailboxes, time range, and validated item-class conditions. Microsoft lists `IPM.SkypeTeams.Message.Copilot.*` for Microsoft 365 Copilot and `IPM.SkypeTeams.Message.Copilot.Studio.*` for Copilot Studio. Broad Teams filters are not Copilot-specific and don't establish complete coverage. Validate results against known interactions and their transcript thread IDs before relying on the search.

See [Search for AI application data in eDiscovery](https://learn.microsoft.com/en-us/purview/edisc-search-copilot-data). App-only EXO/IPPS authentication does **not** make eDiscovery PowerShell supported for unattended use; see [app-only authentication limitations](https://learn.microsoft.com/en-us/powershell/exchange/app-only-auth-powershell-v2).

> **Hedged note.** This pattern *supports* the content-tier obligations under SEC 17a-4(b)(4) and FINRA Rule 4511 when paired with §10 preservation. It does not, by itself, *guarantee* completeness of the books-and-records record set; verify scope against the Substrate documentation in [Microsoft Learn: Audit logs for Copilot and AI activities](https://learn.microsoft.com/en-us/purview/audit-copilot) at every change window.

### 8.2 Communication Compliance Copilot policy stub

**Non-executable policy-design sketch.** Configure and validate the Copilot policy in the portal with the required users, reviewers, conditions, and sampling. [`New-SupervisoryReviewPolicyV2`](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-supervisoryreviewpolicyv2) does not document a `-ReviewPercentage` parameter, and its reference explicitly says `-WhatIf` doesn't work in Security & Compliance PowerShell. Do not use an apparent dry-run command to create a policy.

---

## §9 — Environment-specific Dataverse auditing (`Get-FsiCopilotStudioDataverseAudit`)

**Why this section exists.** [Copilot Studio administrative activities](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-logging-copilot-studio) are collected by default at the SDK layer. Their collection cannot be disabled, although Purview audit logging can be disabled; usage audit metadata and transcript text are separate, and some channels are excluded. This default activity stream has **no documented universal six-table enablement prerequisite**.

For additional [Dataverse change auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing), define the required environments, tables, and columns from the deployed solution and records requirements. Environment-level auditing must be enabled, as must the applicable table and column settings. Audit settings can be transported in solutions; inspect the target settings and managed-property restrictions instead of assuming either inheritance or noninheritance.

Microsoft's [May 2026 change notice](https://learn.microsoft.com/en-us/power-platform/important-changes-coming#removal-of-before-and-after-field-change-values-in-audit-events-sent-to-microsoft-purview) removes before-and-after field values from **Purview-bound** Dataverse events, not the native Dataverse audit history. Retrieve required details using [Dataverse audit-history operations](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/auditing/retrieve-audit-data), such as `RetrieveAuditDetails`, with the required audit privileges and paging. This is not a generic `auditdetails` entity-set endpoint.

### 9.1 Read state across all environments

```powershell
function Get-FsiCopilotStudioDataverseAudit {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param()
    [pscustomobject]@{
        ControlId = '1.7'; Helper = 'Get-FsiCopilotStudioDataverseAudit'; Status = 'Pending'
        CapturedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        Note = 'Implementation prerequisite: supply an approved environment/table/column inventory and authenticate independently to each Dataverse resource. Check organization.isauditenabled and EntityDefinitions/Attributes IsAuditEnabled and managed restrictions. Zero discovered environments or missing metadata is unknown, not Clean. No Dataverse evidence has been collected.'
    }
}
```

### 9.2 Idempotent enable across environments (mutation)

**Non-executable configuration sketch.** Use [Configure auditing](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/auditing/configure) with the environment's own Dataverse OAuth audience and security roles, not a Graph access token or `Invoke-MgGraphRequest` against a Dataverse URL. Read existing organization/table/column settings and managed restrictions first. Update only approved settings using the documented metadata operations, publish required customizations, then independently read them back and create/retrieve a known audit event. Do not manufacture `CanBeChanged = true` to bypass managed restrictions.

For organization-level settings only, the documented CLI form is `pac env update-settings --name isauditenabled --value true --environment <approved-environment-url>`, followed by `pac env list-settings --filter isauditenabled --environment <approved-environment-url>`. These are examples requiring authorization, not commands to execute as part of the read-only evidence pack; they do not enable table/column audit. See [PAC env reference](https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/env).

---

## §10 — SEC 17a-4(f) preservation pipeline (`Test-FsiAuditTo17a4Preservation`)

**Why this section exists.** Microsoft 365 Audit (Standard, Premium, 10-year add-on) is **record-CAPTURE telemetry**, not a 17a-4(f)-compliant electronic recordkeeping system. For broker-dealers, FCMs, swap dealers, and CPOs subject to SEC 17a-4 / FINRA 4511 / CFTC 1.31, preservation must be satisfied through either WORM storage (Azure immutable blob with a *locked* time-based retention policy — see [Microsoft Learn: Immutable storage for Azure blob data](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview)) or the audit-trail alternative under the October 2022 amendments to Rule 17a-4(f).

This helper inspects container-level policy configuration only; it does not verify that an export pipeline exists or that deliveries are complete and retrievable. It does **not**, by itself, *guarantee* 17a-4(f) compliance — Cohasset attestation, Designated Executive Officer (DEO) representation or Designated Third Party (DTP) undertaking, and a documented books-and-records record set are out-of-scope for PowerShell verification.

### 10.1 Reusable preservation export helper

```powershell
function Export-FsiAuditTo17a4 {
    <#
    .SYNOPSIS
        Exports a Search-FsiAuditLogPaged result set to an Azure immutable blob container with a locked
        time-based retention policy.         Computes a SHA-256 hash for this export; this helper does not write a manifest.
    .NOTES
        Hedged: supports SEC 17a-4(f) preservation when configured per Cohasset-attested guidance and
        combined with the firm's books-and-records record set. Does not, by itself, guarantee compliance.
    #>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='Medium')]
    param(
        [Parameter(Mandatory)] [object[]]$Records,
        [Parameter(Mandatory)] [string]$StorageAccountName,
        [Parameter(Mandatory)] [string]$ResourceGroupName,
        [Parameter(Mandatory)] [string]$ContainerName,
        [Parameter(Mandatory)] [string]$EvidencePrefix,
        [Parameter(Mandatory)] [ValidateRange(1,146000)] [int]$RequiredRetentionDays,
        [string]$StagingPath = '.\evidence\1.7\staging'
    )
    $ctx = New-AzStorageContext -StorageAccountName $StorageAccountName -UseConnectedAccount

    # Verify container has an immutable storage policy in the Locked state
    $policy = Get-AzRmStorageContainerImmutabilityPolicy `
        -ResourceGroupName $ResourceGroupName `
        -StorageAccountName $StorageAccountName -ContainerName $ContainerName -ErrorAction Stop
    if ($policy.State -ne 'Locked') {
        throw "Container '$ContainerName' has no LOCKED time-based immutability policy (current state: $($policy.State)). 17a-4(f) preservation requires the Locked state — Unlocked policies can be deleted by storage account contributors and do not satisfy WORM."
    }
    if ($policy.ImmutabilityPeriodSinceCreationInDays -lt $RequiredRetentionDays) {
        throw "Container immutability period ($($policy.ImmutabilityPeriodSinceCreationInDays) days) is shorter than required retention ($RequiredRetentionDays days)."
    }

    $ts   = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
    $name = "$EvidencePrefix-$ts-$([guid]::NewGuid().ToString('N')).json"
    if (-not $PSCmdlet.ShouldProcess("$StorageAccountName/$ContainerName/$name","Stage and upload audit evidence")) {
        return [pscustomobject]@{ Status='Pending'; Uploaded=$false; Blob=$null }
    }
    New-Item -ItemType Directory -Path $StagingPath -Force -ErrorAction Stop | Out-Null
    $stagedFile = Join-Path $StagingPath $name
    try {
        ConvertTo-Json -InputObject @($Records) -Depth 30 | Set-Content -Path $stagedFile -Encoding UTF8 -ErrorAction Stop
        $hash = (Get-FileHash -Path $stagedFile -Algorithm SHA256).Hash
        Set-AzStorageBlobContent -Context $ctx -Container $ContainerName -File $stagedFile -Blob $name -ErrorAction Stop | Out-Null
        $download = "$stagedFile.readback"
        Get-AzStorageBlobContent -Context $ctx -Container $ContainerName -Blob $name -Destination $download -ErrorAction Stop | Out-Null
        if ((Get-FileHash -Path $download -Algorithm SHA256).Hash -ne $hash) { throw 'Uploaded blob read-back hash mismatch.' }
        [pscustomobject]@{
            Status = 'Pending'; Uploaded = $true; ReadBackHashVerified = $true
            Blob = "$ContainerName/$name"; Sha256 = $hash; Bytes = (Get-Item $stagedFile).Length
            ImmutabilityState = $policy.State; RetentionDays = $policy.ImmutabilityPeriodSinceCreationInDays
            CapturedAtUtc = $ts
            Note = 'This blob was read back; source completeness, scheduling, and full pipeline health remain unverified.'
        }
    } finally {
        Remove-Item $stagedFile, "$stagedFile.readback" -Force -ErrorAction SilentlyContinue
    }
}
```

### 10.2 Pipeline health check

```powershell
function Test-FsiAuditTo17a4Preservation {
    <#
    .SYNOPSIS
        Inspects a container-level immutable policy or an annotated third-party connector reference.
        Neither configuration nor a local annotation proves pipeline health.
    #>
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [string]$StorageAccountName,
        [string]$ResourceGroupName,
        [string]$ContainerName,
        [Parameter(Mandatory)] [ValidateRange(1,146000)] [int]$RequiredRetentionDays,
        [string]$ThirdPartyConnectorAnnotationPath   # optional path to JSON describing a vendor archive (Smarsh / Global Relay / Proofpoint / Mimecast / Bloomberg Vault / Veritas)
    )
    try {
        $azureBranch = $null
        if ($StorageAccountName -and $ContainerName) {
            if (-not $ResourceGroupName) { throw 'ResourceGroupName is required for policy inspection.' }
            $policy = Get-AzRmStorageContainerImmutabilityPolicy -ResourceGroupName $ResourceGroupName -StorageAccountName $StorageAccountName -ContainerName $ContainerName -ErrorAction Stop
            $azureBranch = [pscustomobject]@{
                StorageAccount = $StorageAccountName
                Container      = $ContainerName
                PolicyState    = $policy.State
                RetentionDays  = $policy.ImmutabilityPeriodSinceCreationInDays
                MeetsRetention = ($policy.ImmutabilityPeriodSinceCreationInDays -ge $RequiredRetentionDays)
                Locked         = ($policy.State -eq 'Locked')
            }
        }

        $vendorBranch = $null
        if ($ThirdPartyConnectorAnnotationPath -and (Test-Path $ThirdPartyConnectorAnnotationPath)) {
            $vendorBranch = Get-Content $ThirdPartyConnectorAnnotationPath -Raw | ConvertFrom-Json
        }

        $configurationAnomaly = $azureBranch -and (-not $azureBranch.Locked -or -not $azureBranch.MeetsRetention)

        [pscustomobject]@{
            ControlId        = '1.7'
            Helper           = 'Test-FsiAuditTo17a4Preservation'
            Status           = if ($configurationAnomaly) { 'Anomaly' } else { 'Pending' }
            DeliveryVerified = $false
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

**Required separate evidence:** compare expected source-window counts/IDs with archived exports, check successful scheduled-run freshness, retrieve representative blobs and verify hashes and effective protection, and validate archive attestations independently. A JSON `AttestationOnFile` flag is an unverified assertion. These examples cover container-level policies only; version-level WORM requires inspection of effective version policies. Supply an approved retention duration in **days**, rather than approximating calendar years as `years * 365`. Blob upload requires a data-plane write role; a reader-only evidence principal cannot also run the export.

---

## §11 — Sentinel forwarding sanity check (`Test-FsiAuditToSentinel`)

**Why this section exists.** Cross-control verification with Control 3.9 (Microsoft Sentinel Integration). The [Microsoft Copilot connector](https://learn.microsoft.com/en-us/azure/sentinel/data-connectors-reference#microsoft-copilot) maps to [`CopilotActivity`](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/copilotactivity), not Office 365's `OfficeActivity`. Dataverse has a separate connector/table. Do not assume all four record types in §7 arrive through one connector. A connector object or a rule query containing a string proves neither ingestion nor an enabled, successfully executing alert.

```powershell
function Test-FsiAuditToSentinel {
    [CmdletBinding()]
    [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [string]$ResourceGroupName,
        [Parameter(Mandatory)] [string]$WorkspaceName
    )
    [pscustomobject]@{
        ControlId = '1.7'; Helper = 'Test-FsiAuditToSentinel'; Status = 'Pending'
        ResourceGroupName = $ResourceGroupName; WorkspaceName = $WorkspaceName
        IngestionVerified = $false; AlertVerified = $false
        CapturedAtUtc = (Get-Date).ToUniversalTime().ToString('o')
        Note = 'Implementation prerequisite: inspect Microsoft Copilot connector configuration, correlate a known event RecordId in CopilotActivity, verify freshness and each required record type, then exercise an enabled analytics rule and inspect the resulting alert. No ingestion or alert evidence has been collected.'
    }
}
```

Run a read-only workspace query after generating an approved known interaction:

```kusto
CopilotActivity
| where TimeGenerated > ago(24h)
| where RecordType == "CopilotInteraction"
| project TimeGenerated, RecordId, ActorName, AppHost, RecordType, LLMEventData
```

This probe is not a pass criterion by itself: match `RecordId` to the known source event and verify the expected tenant and timestamps. Empty rows can mean no activity, latency, missing access, or missing coverage. If an existing deployment uses `OfficeActivity`, document and validate its explicit legacy/custom adapter rather than assuming the Microsoft Copilot connector uses that schema.

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
        $ErrorActionPreference = 'Stop'
        if (-not $PSCmdlet.ShouldProcess($RootPath, "Write evidence and update unsigned manifest for $Name")) { return }
        if (-not (Test-Path $RootPath)) { New-Item -ItemType Directory -Path $RootPath -Force | Out-Null }
        $ts     = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
        $tenant = (Get-MgContext).TenantId
        if (-not $tenant) { throw 'An explicit Graph tenant context is required for evidence naming.' }
        $base   = Join-Path $RootPath "Control-1.7_${tenant}_${Name}_${ts}_$([guid]::NewGuid().ToString('N'))"
        $InputObject | ConvertTo-Json -Depth 30 | Set-Content -Path "$base.json" -Encoding UTF8
        $hash = (Get-FileHash -Path "$base.json" -Algorithm SHA256).Hash

        $manifestPath = Join-Path $RootPath 'manifest.json'
        $manifest = if (Test-Path $manifestPath) { @(Get-Content $manifestPath -Raw | ConvertFrom-Json) } else { @() }
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
        ConvertTo-Json -InputObject @($manifest) -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8
        [pscustomobject]@{ EvidenceFile = "$base.json"; Sha256 = $hash; Manifest = $manifestPath }
    }
}

# Quarterly attestation pack
if (-not (Get-Variable RequiredRetentionDays -ErrorAction SilentlyContinue)) {
    throw 'Set RequiredRetentionDays to the independently approved duration before running this example.'
}
New-Item -ItemType Directory -Path '.\evidence\1.7' -Force | Out-Null
Start-Transcript -Path ".\evidence\1.7\transcript_$(Get-Date -Format 'yyyyMMddTHHmmssZ').log" -IncludeInvocationHeader

try {
Get-FsiAuditCopilotEnablement                     | Save-FsiAuditEvidence -Name 'AuditCopilotEnablement'
Get-FsiAuditPremiumStatus                         | Save-FsiAuditEvidence -Name 'AuditPremiumStatus'
Get-FsiAuditPaygEnablement                        | Save-FsiAuditEvidence -Name 'AuditPaygEnablement'
Get-FsiMailboxAuditBypass                         | Save-FsiAuditEvidence -Name 'MailboxAuditBypass'
Get-FsiCopilotStudioDataverseAudit                | Save-FsiAuditEvidence -Name 'CopilotStudioDataverseAudit'
Test-FsiAuditTo17a4Preservation `
    -StorageAccountName 'fsiarchivewormprod' `
    -ResourceGroupName 'rg-archive-prod' `
    -RequiredRetentionDays $RequiredRetentionDays `
    -ContainerName 'audit-1-7'                    | Save-FsiAuditEvidence -Name '17a4PreservationPipeline'
Test-FsiAuditToSentinel `
    -ResourceGroupName 'rg-sec-prod' `
    -WorkspaceName 'la-sec-prod'                  | Save-FsiAuditEvidence -Name 'SentinelForwarding'

} finally {
    Stop-Transcript
}
```

After the run, review every `Pending`, `Anomaly`, and `Error` result; none is a pass. Copy the `evidence\1.7\` folder using the separately authorized export principal and verify delivery/retrieval. `Test-FsiAuditTo17a4Preservation` does not verify the full pipeline. The manifest is unsigned, contains no module inventory, and requires a single writer; use a separately implemented signing/serialization process where required. Reference each artifact's SHA-256 in the attestation statement.

---

## §13 — Cross-control links

| Control | Why it cross-cuts 1.7 |
|---|---|
| [1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP policy match events surface in the same UAL; validate documented record types such as `ComplianceDLPSharePoint` and correlate with `CopilotInteraction`. |
| [1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | Content-tier viewer for `CopilotInteraction` transcripts (§8). |
| [1.10 — Communication Compliance Monitoring](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | FINRA Rule 3110 supervisory review of AI-generated communications (§8). |
| [1.19 — eDiscovery for Agent Interactions](../../../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | Legal hold and collection of Copilot transcripts via Premium eDiscovery (§8). |
| [2.6 — Model Risk Management Alignment](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Audit `ModelTransparencyDetails` can contain model metadata; Microsoft 365 Copilot scenarios do not expose `ModelName` or `ModelVersion` in this field. |
| [2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Consumes UAL `CopilotInteraction` events as the supervisory queue source. |
| [3.4 — Incident Reporting and Root-Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | UAL is the primary timeline source for Copilot/agent incidents. |
| [3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | §11 describes required end-to-end evidence; `Test-FsiAuditToSentinel` remains a `Pending` placeholder. |

---

## §14 — Operating cadence and anti-patterns

### 14.1 Cadence

| Task | Frequency | Helper |
|---|---|---|
| Tenant unified audit ingestion + record-type flow | Daily | `Get-FsiAuditCopilotEnablement` |
| License entitlement reconciliation against required duration (including add-on where applicable) | Weekly | `Get-FsiAuditPremiumStatus` (`Pending` prerequisite) |
| PAYG `AIAppInteraction` opt-in confirmation | Monthly + after every Microsoft billing change | `Get-FsiAuditPaygEnablement` |
| Mailbox audit bypass review | Monthly + on every regulated-user provisioning event | `Get-FsiMailboxAuditBypass` |
| Environment/table/column audit against approved Dataverse inventory | Weekly + after every solution import into a new environment | `Get-FsiCopilotStudioDataverseAudit` (`Pending` prerequisite) |
| 17a-4(f) preservation pipeline health | Daily | `Test-FsiAuditTo17a4Preservation` |
| Sentinel forwarding + analytics rule presence | Daily | `Test-FsiAuditToSentinel` |
| Quarterly attestation pack (review incomplete evidence; signing is separate) | Quarterly | All of the above |

### 14.2 Anti-patterns (do not ship)

- ❌ Calling `Get-AdminAuditLogConfig` without first calling `Assert-FsiExoSession` — false-clean trap #1.
- ❌ `Search-UnifiedAuditLog -ResultSize 5000` without `-SessionCommand ReturnLargeSet` and a session-ceiling splitter — silent truncation.
- ❌ Hard-coding `-RecordType PowerPlatformAdminActivity` (or any non-enum value) or swallowing its parameter-binding error.
- ❌ Claiming retention coverage on the basis of a custom retention policy alone — `Get-FsiAuditPremiumStatus` first.
- ❌ Treating an empty `AIAppInteraction` result as "no shadow AI" without confirming PAYG opt-in via `Get-FsiAuditPaygEnablement`.
- ❌ Treating a fixed table list as a prerequisite for default Copilot Studio SDK audit events, or skipping target environment/table/column checks for additional Dataverse change auditing.
- ❌ Treating the 10-Year Audit Log Retention add-on as a 17a-4(f) preservation layer — it is record-CAPTURE telemetry; `Test-FsiAuditTo17a4Preservation` remains `Pending` without independent pipeline evidence.
- ❌ Treating Office 365 connector presence or a rule-query string as proof of Copilot ingestion/alerting; validate the Microsoft Copilot connector, `CopilotActivity`, and a known event plus alert.
- ❌ Using the same service principal for both `Set-AdminAuditLogConfig` and the audit-evidence pack — SOX 404 separation-of-duties violation.

---

[Back to Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [Portal Walkthrough](portal-walkthrough.md) · [Troubleshooting](troubleshooting.md)

---

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Documentation reviewed only; no tenant UI verification*
