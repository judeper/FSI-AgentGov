# Control 1.12 — PowerShell Setup: Insider Risk Management Evidence Collection

> **Scope.** This playbook collects supporting evidence for [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) in US commercial-cloud Microsoft 365. Read the [PowerShell baseline](../../_shared/powershell-baseline.md) first. PowerShell can capture the Microsoft 365 audit prerequisite and collect local evidence files; it does not replace manual verification of Insider Risk Management (IRM) policies, indicators, privacy settings, HR ingestion, Adaptive Protection, or alert routing.
>
> **What this playbook is not.** It is not a substitute for the firm's Written Supervisory Procedures (FINRA Rule 3110), HR investigation workflows, legal-hold decisions, or supervisory review by a registered principal. It does not, by itself, configure or enable Forensic Evidence — that capability requires dual-authorization executed in the Purview portal per [Control 1.12](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). It does not retain books-and-records artifacts; durable retention is the responsibility of [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
>
> **Hedged language reminder.** Output of this harness *supports* compliance with FINRA Rule 3110 / 4511, FINRA RN 25-07 (RFC, contextual only), SEC Rule 17a-3 / 17a-4, SEC Regulation S-P (2024 amendments), GLBA 501(b), SOX 302/404, NYDFS 23 NYCRR §500.06 / §500.16 / §500.17, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Fed SR 26-2 (formerly SR 11-7), and FFIEC IT Examination Handbook expectations. It does not, by itself, *ensure* a passing examination, *guarantee* that every insider event is detected, *prevent* exfiltration, or *eliminate* false negatives in ML-driven scoring. Implementation requires that organizations verify endpoint availability, module pinning, HR connector accuracy, and signal-source coverage at every change window, and that they treat any preview surface (Risky Agents, Risky AI usage, Triage Agent) as **additive** evidence rather than a complete substitute for human supervisory review.

| Field | Value |
|---|---|
| Control ID | 1.12 |
| Pillar | 1 — Security |
| Playbook | PowerShell Setup |
| PowerShell Edition | PowerShell 7.4+ Core for the local evidence collector (framework baseline, not an IRM service requirement) |
| Last Verified | 2026-10-18 (live Microsoft Learn technical review; no tenant or screenshot verification) |
| Companion Playbooks | [Portal Walkthrough](portal-walkthrough.md) · [Verification & Testing](verification-testing.md) · [Troubleshooting](troubleshooting.md) |

**Last Verified:** 2026-10-18

## §1 — Supported automation and permissions

Use a CAB-approved `ExchangeOnlineManagement` version compatible with your PowerShell runtime; the `Get-ConnectionInformation` cmdlet used below is available only in version 3.0.0 or later ([reference](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-connectioninformation?view=exchange-ps)). The former fixed 3.7.0 / Graph 2.25.0 examples were not a current Microsoft support baseline. Install a chosen version using the shared baseline; record the actual version in evidence. No Graph module or Graph permission is required by the collector below.

| Operation | Documented surface / permissions |
|---|---|
| Microsoft 365 audit status | Exchange Online PowerShell: `Get-AdminAuditLogConfig`. Use the Exchange audit permissions appropriate to the operation; enabling/disabling auditing requires the **Audit Logs** role. |
| IRM policy/settings administration | Purview portal; **Insider Risk Management Admins** |
| Alert/case investigation and content access | Purview portal; consult the [IRM permissions matrix](https://learn.microsoft.com/en-us/purview/insider-risk-management-permissions) for Analysts versus Investigators |
| IRM solution audit-log view/export | **Insider Risk Management Auditors** (or the broad **Insider Risk Management** group) |
| Forensic capture request / approval / viewing | **Admins** request, **Approvers** approve, **Investigators** view captures; the broad IRM group also has these permissions. Preserve the firm's separation-of-duties requirements. |
| HR connector monitoring | Purview **Settings > Data connectors > My connectors**; connector permissions per [Import HR data](https://learn.microsoft.com/en-us/purview/import-hr-data) |

The Auditors role is not an API permission for policy inventory or alert investigation. Do not assign an application to that role and assume it can enumerate policies. This playbook uses a human operator for portal evidence and does not provision a service principal.

Sources: [Exchange connection](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-exchange-online-powershell?view=exchange-ps), [auditing status](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable), [forensic request workflow](https://learn.microsoft.com/en-us/purview/insider-risk-management-forensic-evidence-manage).

## §2 — Policy and alert evidence (manual)

In Purview **Insider Risk Management > Policies**, record each in-scope policy's name, template, status, scope, exclusions, triggering event, and indicators. Capture the Alerts view and the review/disposition evidence separately. Use supported exports where available; otherwise attach timestamped screenshots and reviewer notes. A policy CSV with a `Template` column is a **firm-defined inventory**, not a promised native export schema.

Compare only the firm's approved, applicable templates with [Microsoft's template catalog](https://learn.microsoft.com/en-us/purview/insider-risk-management-policy-templates). Do not require every template for every tenant. **Risky Agents (preview)** is applied by default and covers Copilot Studio and Microsoft Foundry agents; it is not a user-created general-purpose agent-abuse template.

The local collector below checks file availability and integrity only. A present export, or an empty alert queue, does not establish policy effectiveness.

## §3 — Audit prerequisite and Adaptive Protection

In a **separate Exchange Online PowerShell process**, capture the audit prerequisite:

```powershell
#Requires -Version 7.4
Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline
$session = @(Get-ConnectionInformation |
    Where-Object { $_.State -eq 'Connected' -and $_.IsEopSession -eq $false })
if ($session.Count -ne 1) {
    throw 'Expected exactly one connected Exchange Online (non-Security & Compliance) session.'
}
$tenantId = ([guid]$session[0].TenantID).ToString('D')
$runId = 'IRM112-{0:yyyyMMdd-HHmmss}-{1}' -f [datetime]::UtcNow, [guid]::NewGuid().ToString('N').Substring(0, 8)
$audit = Get-AdminAuditLogConfig -ErrorAction Stop
$path = ".\Control-1.12_${tenantId}_Commercial_ExchangeAuditStatus_${runId}.json"
[pscustomobject]@{
    TenantId = $tenantId
    RunId = $runId
    CollectedUtc = [datetime]::UtcNow.ToString('o')
    Session = $session[0] | Select-Object ConnectionId, State, TokenStatus, IsEopSession, ModulePrefix, TenantID
    UnifiedAuditLogIngestionEnabled = $audit.UnifiedAuditLogIngestionEnabled
} | ConvertTo-Json -Depth 5 | Out-File -LiteralPath $path -Encoding utf8 -NoClobber
(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash |
    Out-File -LiteralPath "$path.sha256" -Encoding ascii -NoClobber
Disconnect-ExchangeOnline -Confirm:$false
```

Check `UnifiedAuditLogIngestionEnabled` is `True`. **Do not read this property through `Connect-IPPSSession`: Microsoft documents that it always returns `False` there.** This read-only example does not enable auditing; use the approved [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) change procedure when necessary.

An assessment report's audit flag is not sufficient without evidence that it was collected through Exchange Online rather than Security & Compliance. The artifact name and body carry the tenant ID and a unique run ID, and `-NoClobber` makes a repeated run fail instead of replacing earlier evidence. Retain the artifact with its SHA-256 sidecar and the recorded session context for review; `IsEopSession` is `False` for Exchange Online and `True` for Security & Compliance connections ([Get-ConnectionInformation](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-connectioninformation?view=exchange-ps)).

**The IRM solution audit log is independent of the Microsoft 365 unified audit log.** It is always enabled, retains activities for 180 days, and is exported by an Auditor from **Insider risk audit log > Export**. Preserve its local timestamps and record the timezone plus UTC normalization. Do not search for invented `InsiderRiskMgmt*` operations or a record type named `InsiderRiskManagement` to attest IRM administrative activity.

For Adaptive Protection, capture enablement, configured **Minor / Moderate / Elevated** risk conditions, assigned risk levels, and the consumer policies in **Insider Risk Management > Adaptive protection**. Risk levels are not the **Low / Medium / High** alert-severity scale. Audit ingestion alone cannot prove Adaptive Protection is enabled.

Sources: [audit status](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable), [IRM audit log](https://learn.microsoft.com/en-us/purview/insider-risk-management-audit-log), [Adaptive Protection](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection).

## §4 — HR connector evidence (manual)

Open **Settings > Data connectors > My connectors**, select the HR connector, and under **Progress** select **Download log**. Capture upload timestamps, errors, and `RecordsSaved`; compare these with the source CSV and the firm's ingestion schedule. An empty upload is not automatically a failure if the approved source contains no events.

For employee resignation data, Microsoft documents `UserPrincipalName`, `ResignationDate`, and `LastWorkingDate` with **ISO 8601 date-time** values. `EmployeeID` and `EmploymentStatus` are not mandatory resignation columns. `LastWorkingDate` must be no more than six months before or one year after upload. Other HR scenarios have different schemas.

The former `v1.0/security/dataConnectors` query is not a documented Microsoft 365 HR connector inventory API. A Graph permission or a guessed `connectorType` cannot validate ingestion. Use [Microsoft's HR connector workflow and logs](https://learn.microsoft.com/en-us/purview/import-hr-data).

## §5 — Signal-source coverage (manual)

For each enabled policy, record the source-specific prerequisites and evidence:

| Signal | Evidence to capture |
|---|---|
| Microsoft 365 audit feeds | The Exchange Online audit-status artifact from §3 and observed source activity |
| Defender for Endpoint security violations | Onboarding coverage, enabled IRM integration, enabled policy indicators, and a known test activity; the absence of Defender alerts is not proof integration is disabled |
| Cloud-storage indicators | The configured connector and current indicator requirements, including PAYG where indicated; do not infer connector inventory from Graph `security/dataConnectors` |
| Browser-derived signals | Supported Windows device onboarding, enabled indicators, browser version and **Microsoft Compliance Extension** deployment. Edge has native support for some file activities; extension requirements depend on the activity. |

Record unavailable or out-of-scope signals explicitly. A broad claim that all signal coverage is verified from one security alert is not supported.

Sources: [IRM prerequisites](https://learn.microsoft.com/en-us/purview/insider-risk-management-configure), [policy indicators](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators), [browser support](https://learn.microsoft.com/en-us/purview/insider-risk-management-browser-support).

## §6 — Alert routing (manual end-to-end correlation)

Choose and record the route that is actually deployed:

- **Office 365 Management Activity API:** enable **Settings > Insider Risk Management > Export alerts**. Microsoft documents `SecurityComplianceAlerts` filtered by the `InsiderRiskManagement` **category**, with alert exports available every 60 minutes. This is not an IRM administrative audit-log feed.
- **Defender XDR / Microsoft Graph:** configure IRM data sharing and validate a known shared alert. Current Microsoft documentation supports Graph security alerts/incidents and advanced hunting for shared IRM data; it does not establish a Graph policy-inventory or HR-connector endpoint.
- **Microsoft Sentinel:** verify the IRM connector and the actual ingested alert schema, then correlate a known alert ID and timestamp with its source. Do not assume the general Office 365 connector or `OfficeActivity` contains IRM alerts or forensic approval records.

Capture source alert, destination record, connector/configuration evidence, UTC timestamps, and supervisory handoff acknowledgement. No alerts in a quiet window means **Pending**, not a routing pass. API exports can expose real usernames even when portal CSV exports preserve pseudonymization; restrict access accordingly.

Sources: [IRM data sharing and export](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-share-data), [IRM in Defender XDR](https://learn.microsoft.com/en-us/defender-xdr/irm-investigate-alerts-defender).

**Routing limitation:** the documented Defender integration has preview limitations and does not support every IRM event type, including risky AI usage, third-party cloud-app, email-exfiltration, and pre-alert events. Administrator exclusions are not shared. IRM incidents currently lack alert content for some Sentinel automation scenarios; Microsoft recommends the dedicated IRM Sentinel connector. Record these exclusions instead of asserting blanket coverage through Defender incident synchronization.

## §7 — Privacy and forensic evidence (manual)

Capture **Settings > Insider Risk Management > Privacy** and review authorized activity using the independent IRM audit log (§3). Pseudonymization is on by default; do not invent a `Get-IRMConfiguration` cmdlet or treat audit ingestion as proof of the privacy setting.

For forensic evidence, capture the **Admins** request, separate **Approvers** decision, approved-user state, and Investigator review evidence in the portal. Clips are deleted **120 days after capture**; use capture time, not approval time, when tracking expiry. This playbook does not enable capture or change approvals.

Sources: [permissions](https://learn.microsoft.com/en-us/purview/insider-risk-management-permissions), [forensic evidence management](https://learn.microsoft.com/en-us/purview/insider-risk-management-forensic-evidence-manage).

## §8 — AI indicators (manual)

Export or record the actual enabled indicators and policy assignments. Names such as "Excessive Copilot prompt rate per user", "MNPI keyword extraction attempt", or "Off-hours agent access burst" were **organization-defined detection ideas**, not a Microsoft built-in indicator catalog.

For custom detections, document the upstream detection, ingestion, field mapping, threshold, and policy assignment. Microsoft's custom indicators use the **Insider Risk Indicators (preview) connector**; merely adding a name to a CSV does not wire telemetry into IRM. Unsupported or unimplemented scenarios remain coverage gaps, not automatic failures of a Microsoft feature.

Source: [built-in versus custom indicators](https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators).

## §9 — Changes and connection boundaries

Perform IRM policy/settings changes through the documented Purview portal workflow, with before/after evidence and the firm's approval record. The local collector is read-only and cannot create policies, assign roles, or enable Adaptive Protection.

If capturing DLP rule definitions with `Get-DlpComplianceRule`, use a separate Security & Compliance PowerShell session via `Connect-IPPSSession -UserPrincipalName <operator-UPN>`. Parameterless connection uses the documented interactive sign-in flow; it is not a promise of device-code authentication. App-only authentication is a separate deployment with documented application permissions and RBAC, not the mixed interactive/app-only flow formerly shown here.

Source: [Security & Compliance connection](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-scc-powershell?view=exchange-ps).

## §10 — DLP integration with Adaptive Protection

Use the DLP rule condition **Insider risk level for Adaptive Protection is** for the approved risk levels and workload-specific actions. Capture the rule before/after the approved change and verify enforcement and risk-level expiration using the deployed policy.

The current [`Set-DlpComplianceRule` reference](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/set-dlpcompliancerule?view=exchange-ps) does **not** document `-IRMSettings` or `-AdaptiveProtectionRiskLevel`. The former mutation example is withdrawn; do not copy guessed parameters into production. Configure this condition in the portal using [Adaptive Protection in DLP](https://learn.microsoft.com/en-us/purview/dlp-adaptive-protection-learn) and the [configuration guide](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection-guide).

## §11 — Local evidence packaging

Save the following helper and collector as local files outside tracked customer data. `PolicyExportPath` and `AlertExportPath` may be portal exports or reviewer-authored inventories. The collector hashes files but deliberately returns **Pending**: a reviewer must validate completeness, source, scope, freshness, and effectiveness. Missing files remain Pending; file access/hash errors terminate the run. It never converts a manual review into `Clean`.

```powershell
function Get-FsiIrmPolicyEvidenceStatus {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string]$PolicyExportPath,
        [Parameter(Mandatory)] [string]$AlertExportPath
    )
    $files = foreach ($path in @($PolicyExportPath, $AlertExportPath)) {
        $exists = Test-Path -LiteralPath $path -PathType Leaf -ErrorAction Stop
        [pscustomobject]@{
            Path = $path
            Exists = $exists
            Sha256 = if ($exists) {
                (Get-FileHash -LiteralPath $path -Algorithm SHA256 -ErrorAction Stop).Hash
            } else { $null }
        }
    }
    [pscustomobject]@{
        Status = 'Pending'
        AutomationSupported = $false
        ManualVerificationRequired = $true
        Files = @($files)
        CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
        Note = 'File integrity only; review policy scope, alerts, and sections 3-10 separately.'
    }
}
```

```powershell
# Save as: scripts/Invoke-Agt112Sweep.ps1
#Requires -Version 7.4
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [ValidateNotNullOrWhiteSpace()] [string]$EvidencePath,
    [Parameter(Mandatory)] [ValidateNotNullOrWhiteSpace()] [string]$PolicyExportPath,
    [Parameter(Mandatory)] [ValidateNotNullOrWhiteSpace()] [string]$AlertExportPath,
    [Parameter(Mandatory)] [ValidateScript({ $g = [guid]::Empty; [guid]::TryParse($_, [ref]$g) })] [string]$TenantId,
    [ValidatePattern('^IRM112-\d{8}-\d{6}-[0-9a-f]{8}$')] [string]$RunId,
    [string]$WorkspaceId
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-NewEvidenceFile {
    param(
        [Parameter(Mandatory)] [string]$Path,
        [Parameter(Mandatory)] [string]$Text,
        [Parameter(Mandatory)] [System.Text.Encoding]$Encoding
    )
    $bytes = $Encoding.GetBytes($Text)
    # CreateNew fails if the file exists, so earlier evidence is never replaced.
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}

$resolvedEvidencePath = [System.IO.Path]::GetFullPath($EvidencePath)
$resolvedPolicyExport = [System.IO.Path]::GetFullPath($PolicyExportPath)
$resolvedAlertExport = [System.IO.Path]::GetFullPath($AlertExportPath)
foreach ($path in @($resolvedPolicyExport, $resolvedAlertExport)) {
    $parent = Split-Path -Path $path -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        throw "Evidence input parent directory not found: $parent"
    }
}

$tenant = ([guid]$TenantId).ToString('D')
$generatedUtc = [datetime]::UtcNow
if (-not $PSBoundParameters.ContainsKey('RunId')) {
    $RunId = 'IRM112-{0:yyyyMMdd-HHmmss}-{1}' -f $generatedUtc, [guid]::NewGuid().ToString('N').Substring(0, 8)
}
$output = Join-Path $resolvedEvidencePath "Control-1.12_${tenant}_Commercial_PolicyEvidenceAggregate_${RunId}.json"
$sidecar = "$output.sha256"
foreach ($path in @($output, $sidecar)) {
    if (Test-Path -LiteralPath $path) {
        throw "Evidence file already exists and will not be overwritten: $path"
    }
}
New-Item -ItemType Directory -Force -Path $resolvedEvidencePath | Out-Null

$policy = Get-FsiIrmPolicyEvidenceStatus -PolicyExportPath $resolvedPolicyExport -AlertExportPath $resolvedAlertExport
$aggregate = [pscustomobject]@{
    TenantId = $tenant
    RunId = $RunId
    OverallStatus = $policy.Status
    Components = [ordered]@{ PolicyInventory = $policy }
    WorkspaceId = $WorkspaceId
    ManualReviewSections = @(3,4,5,6,7,8,9,10)
    Cloud = 'Commercial'
    GeneratedUtc = $generatedUtc.ToString('o')
}
$utf8 = [System.Text.UTF8Encoding]::new($false)
Write-NewEvidenceFile -Path $output -Text ($aggregate | ConvertTo-Json -Depth 20) -Encoding $utf8
$hash = (Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash
Write-NewEvidenceFile -Path $sidecar -Text ($hash + [Environment]::NewLine) -Encoding ([System.Text.Encoding]::ASCII)
Write-Output "RunId=$RunId; OverallStatus=$($aggregate.OverallStatus); manual review required. Evidence: $output"
```

Load the helper in the same process before invoking the saved collector, and pass the tenant ID (GUID) that the reviewer confirmed. Each run is bound to that tenant and to a unique run ID of the form `IRM112-yyyyMMdd-HHmmss-<8 hex>`; the ID is generated unless the cycle's ID from the verification catalogue is supplied with `-RunId`. The tenant ID and run ID are embedded in the JSON and in the file name, which follows the evidence-pack convention in the [portal walkthrough](portal-walkthrough.md#evidence-pack). The collector refuses to write if the aggregate file or its sidecar already exists, so earlier results are never replaced and the same evidence directory can be reused across runs; reusing a `-RunId` for the same tenant is rejected. The identity is a reviewer-supplied label, not an authenticated claim: this collector does not connect to a tenant, so confirm the tenant ID against the Exchange Online session context recorded in §3. `WorkspaceId` is optional context only; supplying it does not query Sentinel. Retain the source files, aggregate JSON, SHA-256 sidecars, human-readable review, and the firm's manifest identifying each file, byte count, source, UTC collection time, and reviewer. Hashes establish integrity, not immutable storage or retention configuration.

**Scheduler cadence.** Run weekly at minimum; run after any IRM-policy change ticket; run on the day before each quarterly attestation. Land artifacts in WORM storage (Purview Data Lifecycle Management retention lock or Azure Storage immutability policy) per BL-§4 and SEC 17a-4(f).

## Cross-links

- [Control 1.5 — DLP and Sensitivity Labels](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — DLP as Adaptive Protection consumer
- [Control 1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — posture source that complements IRM scoring
- [Control 1.7 — Audit Logging & Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — Unified Audit Log dependency
- [Control 1.10 — Communication Compliance](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — risky-language compensating control
- [Control 1.21 — Adversarial Input Logging](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) — prompt-level signal source
- [Control 2.6 — Model Risk Management (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7))](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — IRM ML scoring inventory and validation
- [Control 2.12 — Supervision of AI-Generated Content](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — supervisory queue for IRM alerts
- [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — NYDFS §500.17 / Reg S-P notice triggers
- [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — IRM alert-ingestion and correlation

*Updated: October 2026 | Version: v1.6.2 | UI Verification Status: Needs Review (technical sources checked; tenant UI not exercised)*
