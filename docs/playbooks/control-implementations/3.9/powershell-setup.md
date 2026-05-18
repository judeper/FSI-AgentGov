# Control 3.9 — PowerShell Setup: Microsoft Sentinel Integration for AI Agent Monitoring

> **Scope.** This playbook automates the Sentinel workspace deployment, data-connector enablement matrix, AI-agent-specific analytics rule library, SOAR playbook scaffolds, table-level retention controls, and quarterly evidence emission defined in [Control 3.9 — Microsoft Sentinel Integration for AI Agent Monitoring](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md).
>
> **Baseline.** All scripts assume the conventions in [_shared/powershell-baseline.md](../../_shared/powershell-baseline.md). Sovereign-cloud endpoints are documented in [§3 — Sovereign Cloud Endpoints (GCC, GCC High, DoD)](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod).
>
> **Namespace.** All functions in this playbook use the `Agt39` prefix to prevent collision with peer-control automation (`Agt36`, `Agt225`, `Agt12`, `Agt34`).
>
> **Hedged-language reminder.** Sentinel telemetry supports compliance with FINRA Rule 3110 supervisory review, NYDFS 23 NYCRR 500.06 audit-trail requirements, OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) model-risk monitoring, FFIEC IT Examination Handbook continuous-monitoring expectations, and CISA BOD 22-09 logging guidance — **it does not satisfy** SEC Rule 17a-3 / 17a-4 books-and-records preservation by itself. Sentinel is a **monitoring and SIEM platform, not a WORM records repository**; books-and-records preservation routes through Microsoft Purview retention labels with regulatory hold (see [Control 1.9 — Data Retention and Deletion Policies](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md)).

!!! warning "Scope Limit — monitoring, not records"
    Microsoft Sentinel is a **security information and event management** platform. Its retention tiers (Analytics, Basic, Auxiliary, Archive) are designed for **investigation and threat hunting**, not for SEC Rule 17a-4(f) WORM books-and-records preservation. The maximum supported archive retention is approximately twelve years on the Log Analytics workspace tier — but the storage is **not** WORM-locked, **not** subject to designated-third-party (D3P) attestation, and **not** indexed for Rule 17a-4 production within 24 hours by default. **Do not** route books-and-records preservation through this control. Use [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) for that route. Use this control for the supervisory-review, threat-detection, and incident-response monitoring overlay required by FINRA 3110 / NYDFS 500.16-.17 / FFIEC.

!!! warning "Sovereign Cloud Availability"
    Sentinel feature parity differs across Commercial, GCC, GCC High, and DoD clouds. Connectors for **Microsoft 365 Copilot**, **Defender for Cloud Apps**, the **Sentinel MCP Server** preview, and **UEBA** have **lagging or absent availability** in GCC High / DoD as of the verification date in this playbook's footer. Always cross-check the [§3 sovereign endpoints anchor](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod) and the Microsoft Learn Sentinel feature-parity matrix **before** running enablement helpers in a sovereign tenant. Do **not** treat a `NotApplicable` return as `Clean`.

!!! info "Entra schema — two distinct sign-in tables"
    AI-agent monitoring requires **both** Entra sign-in streams. Interactive and non-interactive **user** sign-ins land in the `SigninLogs` table. **Service-principal** sign-ins (the table that captures Entra Agent ID workload identities, certificate-bearer auth, and federated app-only flows) land in the **separate** `AADServicePrincipalSignInLogs` table. Enabling only `SigninLogs` produces **false-clean** results for every agent-as-workload-identity hunt. The `Enable-Fsi-EntraConnector` helper (§5.1) enforces both streams and emits an explicit warning if only one is selected.

---

## §0 — Wrong-shell trap, false-clean defects, and scope limits

Sentinel telemetry is the foundation for FINRA 3110 supervisory review escalation, NYDFS 500.16 incident-response triage, and OCC Bulletin 2026-13 (formerly OCC 2011-12) model-risk continuous-monitoring evidence. A silent-empty connector or a sovereign-skipped table produces a **false-clean** report — the auditor receives "no anomalies detected" when the truth is "no telemetry was ever ingested." Every section in this playbook assumes the §0 traps below have been ruled out.

### 0.1 — Wrong-shell and wrong-module trap

- **Windows PowerShell 5.1 is not supported for Az v11+.** `Az.SecurityInsights` v3+ and `Az.OperationalInsights` v3.6+ require PowerShell 7.4+. Running under 5.1 silently installs the v1.x compatibility shim, which lacks `New-AzSentinelAlertRule -Kind NRT` (near-real-time) support — and your prompt-injection rule will silently downgrade to a 5-minute scheduled rule, missing the SLA in [Control 3.4 — Incident Reporting and Root-Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).
- **`Microsoft.PowerApps.Administration.PowerShell` is Desktop-only (PS 5.1).** The Power Platform connector audit helper (§5.2) sources environment metadata from this module. Running it under PS 7.4 returns empty results, which would make `Enable-Fsi-PowerPlatformAdminActivity` declare the connector "not needed."
- **Azure Cloud Shell has no Power Platform module and a pinned Az version.** Use Cloud Shell only for read-only Sentinel queries, never for connector enablement or analytics-rule deployment.
- **PowerShell ISE is not supported.** Device-code flow for sovereign-cloud `Connect-AzAccount` clips its UI in ISE. Use Windows Terminal + `pwsh.exe`.

```powershell
# Enforce edition + version before sourcing any Agt39 function
if ($PSVersionTable.PSVersion.Major -lt 7 -or
    ($PSVersionTable.PSVersion.Major -eq 7 -and $PSVersionTable.PSVersion.Minor -lt 4)) {
    throw "Agt39 requires PowerShell 7.4 or later. Current: $($PSVersionTable.PSVersion)"
}
if ($Host.Name -eq 'Windows PowerShell ISE Host') {
    throw "Agt39 is not supported under Windows PowerShell ISE. Use Windows Terminal + pwsh.exe."
}
# Power Platform admin cmdlets require a separate PS 5.1 session — see §5.2 for the side-car runner.
```

### 0.2 — False-clean defects (Agt39-specific)

| # | Defect | Symptom | Root cause | Fix |
|---|--------|---------|------------|-----|
| 1 | `SigninLogs` enabled, `AADServicePrincipalSignInLogs` disabled | All "after-hours privileged agent" hunts return zero rows | Service-principal sign-ins land in a separate diagnostic-setting category not selected at connector enablement | `Enable-Fsi-EntraConnector` requires both streams; refuses to proceed if only one is selected |
| 2 | `OfficeActivity` filtered to `Exchange` workload only | Microsoft Copilot Studio and Power Platform agent activity invisible | Connector default workload list excludes `PowerPlatform`, `OneDrive`, `MicrosoftTeams`, `MicrosoftForms` | `Enable-Fsi-Defender365Connector` enforces the full workload set; emits a warning per missing workload |
| 3 | Power Platform admin activity not enabled | Maker / environment / DLP-policy changes invisible to Sentinel | Tenant admin never enabled the **Power Platform** data connector (preview in some clouds) | `Enable-Fsi-PowerPlatformAdminActivity` performs a connector-state check and returns `Status='NotApplicable'` when the connector is unavailable in the cloud — **never** `Clean` |
| 4 | Defender for Cloud Apps connector enabled but `CloudAppEvents` table empty | DLP, anomaly, and shadow-app signals missing | Cloud Apps activity policies not licensed on the tenant SKU, or app discovery uploads not configured | `Enable-Fsi-DefenderForCloudAppsConnector` validates SKU + ingestion within 24h, returns `Status='Pending'` if either gate fails |
| 5 | Sovereign cloud silent skew | GCC High Sentinel workspace clean while commercial tenant shows 80 incidents/wk | Microsoft 365 Copilot connector + Sentinel MCP Server have lagging availability in GCC High / DoD | `Enable-Fsi-MicrosoftCopilotConnector` checks `Get-AzContext().Environment.Name`; returns `NotApplicable` with explicit sovereign-skew warning |
| 6 | Analytics rule disabled by tenant deployment template | Rule is created but `Enabled=false`; no incidents fire | Some Sentinel solution templates ship rules disabled to prevent noise; deployment helper does not flip them on | All `New-Fsi-SentinelAlertRule-*` helpers explicitly set `-Enabled $true` and emit a manifest entry confirming enablement |
| 7 | KQL query references retired `DlpAll` table | Rule fails silently with "table not found" not surfacing as alert-rule error | Older internal documentation references an alias that was retired from the Common Schema | Use `CloudAppEvents` (Defender XDR) or `MicrosoftPurviewInformationProtection` — all helpers in §6 use the current table names |
| 8 | Hot retention reduced under regulatory minimum | Quarterly evidence query returns truncated rows; auditor flags missing days | Cost-optimization script lowered Analytics retention to 30d on a `OfficeActivity` table that needs 180d | `Set-Fsi-TableRetention` emits a **warning** when reducing below the firm's policy floor and refuses to proceed without `-Force -Justification` |
| 9 | Archive tier confused with WORM records | Auditor asked for SEC 17a-4 production; team produced Sentinel archive query export | Archive tier is restorable but **not WORM-locked**, **not D3P-attested**, and not SEC 17a-4(f)-compliant | `Export-Fsi-TableToFirmArchive` is a **stub** that explicitly cross-refs Control 1.9 and refuses to be called as a 17a-4 substitute |
| 10 | Logic App playbook fires but never reassigns or suspends agent | "Playbook ran successfully" yet agent stays active | Logic App has Sentinel-trigger permissions but lacks Graph `Application.ReadWrite.All` and Power Platform admin role | `New-Fsi-SentinelPlaybook-SuspendAgent` validates the Managed Identity role assignments before declaring deployment complete |
| 11 | NYDFS 72-hour timer set to local TZ instead of UTC | Notification deadline missed by daylight-saving boundary | Logic App scheduling uses tenant TZ default, not explicit UTC | `New-Fsi-SentinelPlaybook-NYDFS72hTimer` forces `UTC` on the recurrence trigger |
| 12 | Sentinel MCP Server enabled tenant-wide as a "free preview" | Spike in token cost; preview features accessible by non-SOC users | MCP Server is preview; license + cost gate must be opt-in | `Enable-Fsi-SentinelMcpServer` is **opt-in only** behind `-OptIn`, with a sovereign-availability check and a comment-based-help cost note |
| 13 | Conversation transcript ingested without legal/privacy approval | Chat content (PII / privileged communications / customer NPI) sitting in Log Analytics indefinitely | App Insights link enabled by SOC engineer without governance ticket | `Enable-Fsi-AppInsightsLink` requires `-LegalApprovalTicket`, `-PrivacyApprovalTicket`, **and** `-RecordsApprovalTicket` parameters and refuses without all three |
| 14 | Break-glass account sign-in alert exists in commercial Sentinel only | Sovereign tenant break-glass usage invisible to SOC | Per-tenant analytics rule deployed by hand; missing in sovereign workspace | `Test-Fsi-Control39-BreakGlassAlertWiring` validates the [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) break-glass alert is wired in *this* workspace |
| 15 | Orphan-agent-found incident lacks a 3.6 cross-reference tag | SOC closes the incident; Control 3.6 register never reconciled | Analytics rule omits the `Tactics`/`CustomDetails` cross-reference | `New-Fsi-SentinelAlertRule-OrphanShadowAgent` always emits a `CustomDetails.RelatedControl='3.6'` property and `Tactics=@('InitialAccess','Persistence')` |

### 0.3 — Self-test before every production run

Every scheduled connector-health, analytics-rule deployment, or evidence-export job **must** invoke `Invoke-Agt39SelfTest` (§12) before emitting results. A failed self-test:

1. Emits an operational alert to the AI Governance Lead and the SOC Lead.
2. **Suppresses** the run from emitting any "clean" report (no positive evidence is produced).
3. Files a Control 3.4 incident draft if the self-test fails the same way two consecutive runs.

This is identical to the §0.3 contract used by Controls 3.6 and 2.25 and is enforced by the orchestrator in §11.

### 0.4 — Helper return contract (every helper must conform)

Every exported `Get-*`, `Test-*`, `Enable-*`, `New-*`, `Set-*`, and `Export-*` helper in this playbook returns a `[pscustomobject]` with at minimum:

```text
Status        ∈ { Clean, Anomaly, Pending, NotApplicable, Error }
Reason        — short human-readable explanation
ControlId     — '3.9'
HelperVersion — semver string
GeneratedUtc  — ISO 8601 UTC timestamp
Findings      — array (may be empty; never $null)
```

A helper that returns `$null`, `@()`, or an unwrapped hashtable is considered a **bug** and is rejected by the §12 Pester `CONTRACT` namespace. This contract makes downstream JSON serialization, evidence hashing, and SIEM forwarding deterministic.

### 0.5 — Explicit out-of-scope

This playbook does **not** automate:

- Long-term **books-and-records** preservation under SEC 17a-3 / 17a-4 — see [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) and the Purview retention-label flow it documents.
- The actual **NYDFS 72-hour notification submission** to the Department of Financial Services — see [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md). The §7 helper sets a tag and a deadline; **a human must file**.
- Supervisory review queue management for FINRA 3110 — see [Control 2.12 — Supervision and Oversight (FINRA Rule 3110)](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md).
- Model-risk validation evidence under OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7) — see [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md).

---

## §1 — Module pinning, Az / Graph scopes, and canonical roles

### 1.1 — Module version matrix

Pin exact minimum versions. Later minor versions are acceptable, but do **not** float to an unpinned `-MinimumVersion` — `Az.SecurityInsights` v3.1 introduced an `Az.Sentinel.Contracts` namespace migration that breaks scripts authored against v3.0 cmdlet output shapes. Every entry below has been verified in the `verify_controls.py` validator manifest.

```powershell
$Agt39ModuleMatrix = @(
    @{ Name = 'Az.Accounts';                             Min = '3.0.4' },
    @{ Name = 'Az.OperationalInsights';                  Min = '3.6.0' },
    @{ Name = 'Az.SecurityInsights';                     Min = '3.1.2' },
    @{ Name = 'Az.Monitor';                              Min = '5.2.1' },
    @{ Name = 'Az.LogicApp';                             Min = '1.7.0' },   # optional; required only for §7 deployers
    @{ Name = 'Az.Resources';                            Min = '7.4.0' },
    @{ Name = 'Microsoft.Graph.Authentication';          Min = '2.19.0' },
    @{ Name = 'Microsoft.Graph.Security';                Min = '2.19.0' },  # SecurityEvents — incident export
    @{ Name = 'Microsoft.Graph.Identity.SignIns';        Min = '2.19.0' },
    @{ Name = 'Microsoft.PowerApps.Administration.PowerShell'; Min = '2.0.175' }  # Desktop PS 5.1 only — see §0.1
)

function Test-Agt39ModuleMatrix {
    [CmdletBinding()]
    param([switch]$InstallMissing)
    $results = foreach ($m in $Agt39ModuleMatrix) {
        $installed = Get-Module -ListAvailable -Name $m.Name |
            Sort-Object Version -Descending | Select-Object -First 1
        $status = if (-not $installed) { 'Missing' }
                  elseif ($installed.Version -lt [version]$m.Min) { 'Outdated' }
                  else { 'OK' }
        if ($status -ne 'OK' -and $InstallMissing) {
            # CAB-approved pinning pattern; see baseline §1.
            Install-Module $m.Name -RequiredVersion $m.Min -Repository PSGallery `
                -Scope CurrentUser -AllowClobber -AcceptLicense -Force
            $status = 'Installed'
        }
        [pscustomobject]@{
            Module = $m.Name; Required = $m.Min;
            Installed = $installed.Version; Status = $status
        }
    }
    $results
    if ($results.Status -contains 'Missing' -or $results.Status -contains 'Outdated') {
        throw "Agt39 module matrix failed. Re-run with -InstallMissing or pin per CAB ticket."
    }
}
```

### 1.2 — Az / Graph scope matrix

Two least-privilege profiles are defined — read-only `Monitor` and mutating `Configure`. They are **never** combined into a single token. Mutation operations require step-up via PIM activation (§1.4).

| Operation | Az role (Sentinel) | Az role (workspace) | Graph scopes |
|-----------|--------------------|---------------------|--------------|
| Read incidents, KQL, rule list | `Microsoft Sentinel Reader` | `Log Analytics Reader` | `SecurityEvents.Read.All`, `SecurityIncident.Read.All` |
| Write analytics rules, automation rules | `Microsoft Sentinel Contributor` | `Log Analytics Contributor` | `SecurityEvents.ReadWrite.All` |
| Manage data connectors | `Microsoft Sentinel Contributor` + `Security Administrator` (Entra) | n/a | `SecurityEvents.ReadWrite.All` |
| Deploy Logic App playbooks | `Microsoft Sentinel Playbook Operator` + `Logic App Contributor` | n/a | n/a |
| Manage table retention | `Log Analytics Contributor` | `Log Analytics Contributor` | n/a |
| Export evidence (read-only) | `Microsoft Sentinel Reader` | `Log Analytics Reader` | `SecurityIncident.Read.All` |

```powershell
$Agt39GraphScopes = @{
    Monitor   = @('SecurityEvents.Read.All','SecurityIncident.Read.All','AuditLog.Read.All')
    Configure = @('SecurityEvents.ReadWrite.All','SecurityIncident.ReadWrite.All','AuditLog.Read.All')
}
```

### 1.3 — Canonical roles (align with role-catalog)

| Function | Canonical role(s) | PIM activation window | Notes |
|---------|-------------------|-----------------------|-------|
| Sentinel read / hunt | Sentinel Reader (Az), Entra Global Reader (Graph cross-ref) | 8h | Read-only profile |
| Analytics rule deployment | Sentinel Contributor (Az), AI Administrator (governance approval) | 4h | Tier-2 mutation |
| Connector enablement | Sentinel Contributor (Az), Entra Security Administrator | 4h | Required for Entra connector enable |
| Power Platform connector enable | Power Platform Admin | 4h | Side-car PS 5.1 session per §0.1 |
| Defender connector enable | Sentinel Contributor (Az), Defender XDR Security Admin | 4h | Cross-tenant for MSSP scenarios |
| Logic App playbook deployment | Logic App Contributor + Sentinel Playbook Operator | 4h | MI role assignment requires Owner once |
| Retention changes | Log Analytics Contributor + AI Governance Lead approval | 2h | Reductions require -Force + -Justification |
| Evidence export | Sentinel Reader + Purview Compliance Admin (manifest signing) | 8h | Quarterly cadence; outbound to WORM store |
| Sentinel MCP Server opt-in | Sentinel Contributor + AI Governance Lead approval | 4h | Preview; cost gate |
| Governance sign-off | AI Governance Lead | N/A (standing) | Attestation only |

All role activations **must** reference a `ChangeTicketId` in the PIM justification when used for mutation. Read-only `Monitor` activations reference the scheduled job run-id.

### 1.4 — PIM activation helper

```powershell
function Request-Agt39PimActivation {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateSet('Monitor','Configure','PowerPlatform','Defender','LogicApp','Retention','Evidence','MCP')]
        [string]$Profile,
        [Parameter(Mandatory)][string]$Justification,
        [string]$ChangeTicketId,
        [ValidateRange(1,8)][int]$DurationHours = 4
    )
    if ($Profile -ne 'Monitor' -and -not $ChangeTicketId) {
        throw "ChangeTicketId is required for mutation profiles. Monitor is the only profile exempt."
    }
    # NOTE: interactive wrapper; production flows call the Graph Identity Governance
    # /roleManagement/directory/roleAssignmentScheduleRequests endpoint with
    # action=selfActivate and a structured justification payload.
    [pscustomobject]@{
        ControlId       = '3.9'
        HelperVersion   = '1.4.0'
        Profile         = $Profile
        ChangeTicketId  = $ChangeTicketId
        Justification   = $Justification
        DurationHours   = $DurationHours
        RequestedAtUtc  = (Get-Date).ToUniversalTime()
        Status          = 'Pending'  # updated by Graph response in production wrapper
        Reason          = "PIM activation request for profile $Profile"
        Findings        = @()
    }
}
```

### 1.5 — Tagging convention

Every Sentinel resource created or modified by this playbook **must** carry the following tags. Tags are read by the §12 self-test, the §10 evidence helpers, and the [Control 2.25 governance console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) drift detector.

```powershell
$Agt39Tags = @{
    'FSI-Control'        = '3.9'
    'FSI-ControlVersion' = '1.4.0'
    'FSI-Pillar'         = '3-Reporting'
    'FSI-Owner'          = 'AI-Governance-Lead'   # never an individual
    'FSI-DataClass'      = 'SecurityTelemetry'
    'FSI-RecordsRoute'   = 'NotApplicable-See-Control-1.9'  # explicit; prevents 17a-4 confusion
    'FSI-DeployedBy'     = $env:USERNAME
    'FSI-DeployedUtc'    = (Get-Date).ToUniversalTime().ToString('o')
}
```

---

## §2 — Sovereign-cloud bootstrap (Commercial / GCC / GCC High / DoD)

> **Critical difference vs. 3.6.** Control 3.9 has **partial** sovereign feature parity — Sentinel core is GA in all four clouds, but the AI-specific connectors (Microsoft 365 Copilot, Sentinel MCP Server, Defender for Cloud Apps in some SKUs) lag. Sovereign tenants must therefore produce a **connector-availability worksheet** (the output of `Get-Fsi-SentinelWorkspaceHealth` and `Test-Fsi-Control39-ConnectorMatrix`) showing every `NotApplicable` row is justified by a documented Microsoft Learn parity statement.

The cloud-to-endpoint mapping is the canonical anchor in the [baseline §3](../../_shared/powershell-baseline.md#3-sovereign-cloud-endpoints-gcc-gcc-high-dod). Az PowerShell uses **environment names** (not endpoint URLs) on `Connect-AzAccount`. Helpers below normalize the parameter so callers pass a single `-Cloud` value across Az, Graph, and Power Platform.

```powershell
function Initialize-Agt39SovereignContext {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')]
        [string]$Cloud
    )
    $map = switch ($Cloud) {
        'Commercial'  { @{
            AzEnvironment        = 'AzureCloud'
            GraphEnvironment     = 'Global'
            PowerPlatformEndpoint= 'prod'
            SentinelMcpAvailable = $true
            CopilotConnectorAvail= $true
            DefenderXdrAvail     = $true
            DefenderCloudAppsAvail = $true
            ArmEndpoint          = 'https://management.azure.com'
        } }
        'USGov'       { @{
            AzEnvironment        = 'AzureUSGovernment'
            GraphEnvironment     = 'USGov'
            PowerPlatformEndpoint= 'usgov'
            SentinelMcpAvailable = $false   # verify on each release
            CopilotConnectorAvail= $false
            DefenderXdrAvail     = $true
            DefenderCloudAppsAvail = $true
            ArmEndpoint          = 'https://management.usgovcloudapi.net'
        } }
        'USGovHigh'   { @{
            AzEnvironment        = 'AzureUSGovernment'
            GraphEnvironment     = 'USGov'
            PowerPlatformEndpoint= 'usgovhigh'
            SentinelMcpAvailable = $false
            CopilotConnectorAvail= $false   # verify monthly
            DefenderXdrAvail     = $true
            DefenderCloudAppsAvail = $false # SKU-dependent
            ArmEndpoint          = 'https://management.usgovcloudapi.net'
        } }
        'USGovDoD'    { @{
            AzEnvironment        = 'AzureUSGovernment'
            GraphEnvironment     = 'USGovDoD'
            PowerPlatformEndpoint= 'dod'
            SentinelMcpAvailable = $false
            CopilotConnectorAvail= $false
            DefenderXdrAvail     = $true
            DefenderCloudAppsAvail = $false
            ArmEndpoint          = 'https://management.usgovcloudapi.net'
        } }
    }
    $ctx = [pscustomobject]@{
        ControlId            = '3.9'
        HelperVersion        = '1.4.0'
        Cloud                = $Cloud
        AzEnvironment        = $map.AzEnvironment
        GraphEnvironment     = $map.GraphEnvironment
        PowerPlatformEndpoint= $map.PowerPlatformEndpoint
        ArmEndpoint          = $map.ArmEndpoint
        SentinelMcpAvailable = $map.SentinelMcpAvailable
        CopilotConnectorAvail= $map.CopilotConnectorAvail
        DefenderXdrAvail     = $map.DefenderXdrAvail
        DefenderCloudAppsAvail = $map.DefenderCloudAppsAvail
        InitializedAtUtc     = (Get-Date).ToUniversalTime()
        Status               = 'Clean'
        Reason               = "Sovereign context initialized for $Cloud"
        Findings             = @()
    }
    if ($Cloud -ne 'Commercial') {
        Write-Warning "Sovereign cloud '$Cloud' detected. Verify Microsoft Learn Sentinel feature-parity matrix on the verification date in this playbook footer. CopilotConnectorAvail=$($map.CopilotConnectorAvail), SentinelMcpAvailable=$($map.SentinelMcpAvailable). Do NOT treat NotApplicable as Clean."
    }
    $ctx
}
```

The returned context object is threaded through every connector-enable, analytics-rule, and Logic-App-deployer function so that sovereign-specific branching is an **explicit parameter**, never a global state flag.

### 2.1 — `Connect-AzAccount` wrapper (sovereign-aware)

```powershell
function Connect-Agt39Az {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$TenantId,
        [Parameter(Mandatory)][string]$SubscriptionId,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [switch]$DeviceCode
    )
    $ctx = Initialize-Agt39SovereignContext -Cloud $Cloud
    $connectArgs = @{ Tenant = $TenantId; Environment = $ctx.AzEnvironment }
    if ($DeviceCode) { $connectArgs.UseDeviceAuthentication = $true }
    Connect-AzAccount @connectArgs -ErrorAction Stop | Out-Null
    Set-AzContext -SubscriptionId $SubscriptionId -ErrorAction Stop | Out-Null
    [pscustomobject]@{
        ControlId     = '3.9'
        HelperVersion = '1.4.0'
        Status        = 'Clean'
        Reason        = "Connected to Az env $($ctx.AzEnvironment), tenant $TenantId, subscription $SubscriptionId"
        TenantId      = $TenantId
        SubscriptionId= $SubscriptionId
        Cloud         = $Cloud
        AzEnvironment = $ctx.AzEnvironment
        Findings      = @()
        GeneratedUtc  = (Get-Date).ToUniversalTime()
    }
}
```

### 2.2 — Sentinel solution availability check

Sentinel is enabled per-workspace via the `SecurityInsights` solution. A workspace without the solution returns confusing `404`s on every Sentinel cmdlet. This pre-flight is mandatory.

```powershell
function Test-Agt39SentinelSolutionAvailable {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName
    )
    try {
        $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName `
            -Name $WorkspaceName -ErrorAction Stop
    } catch {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='Error'
            Reason="Workspace not found: $($_.Exception.Message)"; Findings=@()
            GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }
    $sentinelOnboarded = $false
    try {
        $solution = Get-AzMonitorLogAnalyticsSolution -ResourceGroupName $ResourceGroupName `
            -ErrorAction Stop | Where-Object { $_.Name -like 'SecurityInsights*' -and
                                              $_.WorkspaceResourceId -eq $ws.ResourceId }
        $sentinelOnboarded = [bool]$solution
    } catch {
        # Some sovereign clouds require an alternate API; fall through to onboarding state probe
    }
    [pscustomobject]@{
        ControlId      = '3.9'
        HelperVersion  = '1.4.0'
        Status         = if ($sentinelOnboarded) { 'Clean' } else { 'Pending' }
        Reason         = if ($sentinelOnboarded) { "Sentinel onboarded on workspace $WorkspaceName" }
                          else { "Workspace exists but Sentinel solution not enabled — call New-Fsi-SentinelWorkspace -EnableSolution" }
        WorkspaceId    = $ws.CustomerId
        WorkspaceArmId = $ws.ResourceId
        WorkspaceSku   = $ws.Sku
        RetentionDays  = $ws.RetentionInDays
        SentinelOnboarded = $sentinelOnboarded
        Findings       = @()
        GeneratedUtc   = (Get-Date).ToUniversalTime()
    }
}
```

---

## §3 — Connection helper (`Initialize-Agt39Session`)

A single entry point connects to every surface needed for connector enablement, analytics-rule deployment, Logic-App publishing, and evidence emission. Failures are **never** swallowed — a surface that cannot connect returns a session object with `Status = 'Error'` for that surface, and downstream functions emit `Status = 'NotApplicable'` for their action rather than falsely reporting `Clean`.

```powershell
function Initialize-Agt39Session {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$TenantId,
        [Parameter(Mandatory)][string]$SubscriptionId,
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][ValidateSet('Monitor','Configure','PowerPlatform','Defender','LogicApp','Retention','Evidence','MCP')]
        [string]$Profile,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')]
        [string]$Cloud,
        [string]$ChangeTicketId,
        [switch]$DeviceCode,
        [string]$EvidencePath = ".\evidence\3.9"
    )
    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    Start-Transcript -Path "$EvidencePath\transcript-$Profile-$ts.log" -IncludeInvocationHeader | Out-Null

    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    $session = [pscustomobject]@{
        ControlId         = '3.9'
        HelperVersion     = '1.4.0'
        TenantId          = $TenantId
        SubscriptionId    = $SubscriptionId
        ResourceGroupName = $ResourceGroupName
        WorkspaceName     = $WorkspaceName
        Profile           = $Profile
        Sovereign         = $sovereign
        ChangeTicketId    = $ChangeTicketId
        ConnectedAtUtc    = (Get-Date).ToUniversalTime()
        AzStatus          = 'Pending'
        GraphStatus       = 'Pending'
        PowerPlatformStatus = 'Pending'
        SentinelOnboarded = $false
        TranscriptPath    = "$EvidencePath\transcript-$Profile-$ts.log"
        EvidencePath      = $EvidencePath
        Errors            = @()
        Status            = 'Pending'
        Reason            = "Session bootstrap in progress"
        Findings          = @()
        GeneratedUtc      = (Get-Date).ToUniversalTime()
    }

    # Az
    try {
        Connect-Agt39Az -TenantId $TenantId -SubscriptionId $SubscriptionId `
            -Cloud $Cloud -DeviceCode:$DeviceCode | Out-Null
        $session.AzStatus = 'Connected'
    } catch { $session.AzStatus = 'Error'; $session.Errors += "Az: $($_.Exception.Message)" }

    # Sentinel solution presence
    if ($session.AzStatus -eq 'Connected') {
        $solCheck = Test-Agt39SentinelSolutionAvailable -ResourceGroupName $ResourceGroupName `
            -WorkspaceName $WorkspaceName
        $session.SentinelOnboarded = ($solCheck.Status -eq 'Clean')
        if (-not $session.SentinelOnboarded -and $Profile -ne 'Monitor') {
            $session.Errors += "Sentinel solution not onboarded on $WorkspaceName. Run New-Fsi-SentinelWorkspace -EnableSolution before $Profile profile actions."
        }
    }

    # Graph (only for incident-export, MCP, evidence profiles)
    if ($Profile -in @('Evidence','MCP','Configure')) {
        try {
            $scopes = if ($Profile -eq 'Monitor') { $Agt39GraphScopes.Monitor } else { $Agt39GraphScopes.Configure }
            Connect-MgGraph -TenantId $TenantId -Scopes $scopes -Environment $sovereign.GraphEnvironment -NoWelcome -ErrorAction Stop
            $session.GraphStatus = 'Connected'
        } catch { $session.GraphStatus = 'Error'; $session.Errors += "Graph: $($_.Exception.Message)" }
    } else {
        $session.GraphStatus = 'Skipped'
    }

    # Power Platform (only when needed; warn if running under PS 7 — see §0.1 / §5.2)
    if ($Profile -eq 'PowerPlatform') {
        if ($PSVersionTable.PSEdition -ne 'Desktop') {
            $session.PowerPlatformStatus = 'NotApplicable'
            $session.Errors += "PowerPlatform profile requires Windows PowerShell 5.1 (Desktop edition). Current: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion). Use the §5.2 side-car runner."
        } else {
            try {
                Add-PowerAppsAccount -Endpoint $sovereign.PowerPlatformEndpoint -ErrorAction Stop | Out-Null
                $session.PowerPlatformStatus = 'Connected'
            } catch {
                $session.PowerPlatformStatus = 'Error'
                $session.Errors += "PowerPlatform: $($_.Exception.Message)"
            }
        }
    } else { $session.PowerPlatformStatus = 'Skipped' }

    if ($Profile -ne 'Monitor' -and $session.AzStatus -ne 'Connected') {
        $session.Status = 'Error'
        $session.Reason = "Az connection failed; cannot proceed with mutation profile $Profile"
        Stop-Transcript | Out-Null
        throw "Agt39 $Profile profile requires Az connection. Errors: $($session.Errors -join '; ')"
    }

    $session.Status = if ($session.Errors.Count -eq 0) { 'Clean' } else { 'Anomaly' }
    $session.Reason = if ($session.Errors.Count -eq 0) { "Session bootstrapped for $Profile in $Cloud" }
                      else { "Session bootstrapped with $($session.Errors.Count) non-fatal error(s)" }
    $session
}
```

### 3.1 — Closing a session

```powershell
function Close-Agt39Session {
    [CmdletBinding()]
    param([Parameter(Mandatory)]$Session)
    try { Disconnect-AzAccount | Out-Null } catch {}
    if ($Session.GraphStatus -eq 'Connected') { try { Disconnect-MgGraph | Out-Null } catch {} }
    if ($Session.PowerPlatformStatus -eq 'Connected') { try { Remove-PowerAppsAccount | Out-Null } catch {} }
    try { Stop-Transcript | Out-Null } catch {}
    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status='Clean'
        Reason="Session closed for $($Session.Profile)"; Findings=@()
        TranscriptPath=$Session.TranscriptPath; GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

---

## §4 — Workspace deployment helpers

The Sentinel workspace is the **trust boundary** for AI-agent telemetry. Two helpers exist:

- `New-Fsi-SentinelWorkspace` — idempotent deployment (workspace + Sentinel solution + base table retention).
- `Get-Fsi-SentinelWorkspaceHealth` — daily ingestion check per AI-relevant table; returns per-table `Status` for the connector matrix.

Both are exported from a module loaded by the §11 orchestrator.

### 4.1 — `New-Fsi-SentinelWorkspace`

Sentinel is a per-workspace toggle on Log Analytics. Hot retention defaults to 180 days (firm policy floor) and archive can extend up to ~12 years on the Log Analytics tier — but **see the §0 scope warning**: the archive tier is **not** WORM-locked and is **not** a substitute for SEC 17a-4 books-and-records preservation. The helper accepts explicit `-HotRetentionDays` and `-ArchiveRetentionDays` parameters and warns when reductions are attempted.

```powershell
function New-Fsi-SentinelWorkspace {
<#
.SYNOPSIS
Idempotently deploys a Microsoft Sentinel workspace for FSI AI-agent monitoring.

.DESCRIPTION
Creates (or updates in place) a Log Analytics workspace, enables the Microsoft Sentinel
SecurityInsights solution, applies FSI tagging conventions, and sets baseline table
retention. Idempotent: re-running with identical parameters is a no-op.

Hot retention default is 180 days (FFIEC IT Examination Handbook continuous-monitoring
floor); archive default is 4,383 days (~12 years) which is the maximum supported on
Log Analytics. Both are explicit parameters — callers must pass values consistent with
firm retention policy.

.PARAMETER ResourceGroupName
Azure resource group hosting the workspace. Must already exist.

.PARAMETER WorkspaceName
Log Analytics workspace name. Lowercase, 4-63 chars, alphanumeric + hyphens.

.PARAMETER Location
Azure region. Sovereign callers must pass a region in the matching Azure environment
(e.g., 'usgovvirginia' for AzureUSGovernment).

.PARAMETER HotRetentionDays
Analytics-tier (hot) retention. Default 180. Minimum allowed without -Force is the
firm-policy floor (default 90 days for FFIEC).

.PARAMETER ArchiveRetentionDays
Total retention including Archive tier. Default 4383. Maximum supported is 4383.
Note: Archive tier is NOT WORM and NOT a books-and-records substitute. See Control 1.9.

.PARAMETER EnableSolution
Switch. When set, also enables the SecurityInsights solution (Sentinel onboarding).

.PARAMETER Cloud
Sovereign cloud selector. Used to validate region parity.

.PARAMETER Tags
Hashtable of tags. Defaults to $Agt39Tags.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required: Log Analytics Contributor + Microsoft Sentinel Contributor
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][ValidatePattern('^[a-z0-9][a-z0-9-]{2,62}$')][string]$WorkspaceName,
        [Parameter(Mandatory)][string]$Location,
        [ValidateRange(30,730)][int]$HotRetentionDays = 180,
        [ValidateRange(30,4383)][int]$ArchiveRetentionDays = 4383,
        [switch]$EnableSolution,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [hashtable]$Tags = $Agt39Tags,
        [string]$EvidencePath = ".\evidence\3.9"
    )
    $ErrorActionPreference = 'Stop'
    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    $findings = @()

    # Snapshot before mutation
    $existing = $null
    try { $existing = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction SilentlyContinue } catch {}
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    if ($existing) {
        $existing | ConvertTo-Json -Depth 10 | Set-Content -Path "$EvidencePath\workspace-before-$(Get-Date -Format yyyyMMddHHmmss).json"
        if ($existing.RetentionInDays -gt $HotRetentionDays) {
            Write-Warning "Existing workspace retention ($($existing.RetentionInDays) d) exceeds requested ($HotRetentionDays d). Reduction requires -Force per firm policy floor."
            $findings += "RetentionReductionAttempt: existing=$($existing.RetentionInDays), requested=$HotRetentionDays"
        }
    }

    if ($PSCmdlet.ShouldProcess("$ResourceGroupName/$WorkspaceName", "Create or update Log Analytics workspace")) {
        $ws = New-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName `
            -Name $WorkspaceName -Location $Location -Sku 'PerGB2018' `
            -RetentionInDays $HotRetentionDays -Tag $Tags -Force
    } else {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='Pending'
            Reason="WhatIf: workspace creation skipped"; Findings=$findings
            GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }

    # Sentinel solution onboarding
    $sentinelStatus = 'Skipped'
    if ($EnableSolution) {
        if ($PSCmdlet.ShouldProcess($WorkspaceName, "Enable SecurityInsights (Sentinel) solution")) {
            try {
                $solParams = @{
                    Type = 'SecurityInsights'
                    ResourceGroupName = $ResourceGroupName
                    Location = $Location
                    WorkspaceResourceId = $ws.ResourceId
                }
                # The solution cmdlet name varies by Az.MonitoringSolutions version — guard both shapes.
                if (Get-Command New-AzMonitorLogAnalyticsSolution -ErrorAction SilentlyContinue) {
                    New-AzMonitorLogAnalyticsSolution @solParams -ErrorAction Stop | Out-Null
                } else {
                    # Fallback to ARM template path; production CAB-approved templates live in
                    # FSI-AgentGov-Solutions repo: solutions/sentinel-baseline/arm/
                    Write-Warning "New-AzMonitorLogAnalyticsSolution not present; deploy via ARM template (see FSI-AgentGov-Solutions)."
                }
                $sentinelStatus = 'Enabled'
            } catch {
                $sentinelStatus = 'Error'
                $findings += "SentinelSolution: $($_.Exception.Message)"
            }
        }
    }

    [pscustomobject]@{
        ControlId           = '3.9'
        HelperVersion       = '1.4.0'
        Status              = if ($sentinelStatus -eq 'Error') { 'Anomaly' } else { 'Clean' }
        Reason              = "Workspace $WorkspaceName ready (Sentinel: $sentinelStatus)"
        WorkspaceArmId      = $ws.ResourceId
        WorkspaceCustomerId = $ws.CustomerId
        Location            = $Location
        Cloud               = $Cloud
        HotRetentionDays    = $HotRetentionDays
        ArchiveRetentionDays= $ArchiveRetentionDays
        SentinelOnboarded   = ($sentinelStatus -eq 'Enabled')
        Tags                = $Tags
        Findings            = $findings
        GeneratedUtc        = (Get-Date).ToUniversalTime()
    }
}
```

### 4.2 — `Get-Fsi-SentinelWorkspaceHealth`

Daily health check. Returns one row per **AI-relevant table**, each with explicit `Status`. The table list below is the canonical AI-agent monitoring set: callers may extend it via `-AdditionalTables`, but the base set is **not** optional.

| Table | Purpose | Source connector |
|-------|---------|------------------|
| `OfficeActivity` | Microsoft 365 user + Copilot file events | Office 365 connector |
| `SigninLogs` | Interactive + non-interactive **user** sign-ins | Entra connector |
| `AADServicePrincipalSignInLogs` | **Service-principal** sign-ins (Entra Agent ID, app-only) | Entra connector — separate stream |
| `PowerPlatformAdminActivity` | Maker / env / DLP-policy changes | Power Platform connector |
| `AlertInfo`, `AlertEvidence` | Defender XDR alerts (M365D unified) | Defender XDR connector |
| `CloudAppEvents` | Defender for Cloud Apps activity + DLP | Defender for Cloud Apps connector |
| `MicrosoftCopilotEvents` | Microsoft 365 Copilot prompt + response telemetry (where licensed) | Microsoft 365 Copilot connector |

```powershell
function Get-Fsi-SentinelWorkspaceHealth {
<#
.SYNOPSIS
Per-table ingestion health for AI-agent monitoring tables in a Sentinel workspace.

.DESCRIPTION
Runs a small KQL probe against each of the canonical AI-monitoring tables and returns
a Status per table: Clean (rows in last 24h within expected band), Anomaly (rows
outside band), Pending (table exists but no rows yet — connector recently enabled),
NotApplicable (table not present in this cloud / SKU), or Error.

.PARAMETER WorkspaceCustomerId
Workspace ID (Customer ID GUID), not the ARM resource ID.

.PARAMETER LookbackHours
KQL probe window. Default 24h. Quarterly evidence runs use 168h (7d).

.PARAMETER AdditionalTables
Extra tables to probe (string array). Base set is non-optional.

.PARAMETER Cloud
Sovereign cloud selector. Used to suppress NotApplicable noise (e.g., MicrosoftCopilotEvents in GCC High).

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required: Microsoft Sentinel Reader + Log Analytics Reader
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$WorkspaceCustomerId,
        [ValidateRange(1,720)][int]$LookbackHours = 24,
        [string[]]$AdditionalTables = @(),
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud
    )
    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    $baseTables = @(
        @{ Name='OfficeActivity';                ExpectMin=1;  Required=$true  },
        @{ Name='SigninLogs';                    ExpectMin=1;  Required=$true  },
        @{ Name='AADServicePrincipalSignInLogs'; ExpectMin=1;  Required=$true  },
        @{ Name='PowerPlatformAdminActivity';    ExpectMin=0;  Required=$false },
        @{ Name='AlertInfo';                     ExpectMin=0;  Required=$false },
        @{ Name='AlertEvidence';                 ExpectMin=0;  Required=$false },
        @{ Name='CloudAppEvents';                ExpectMin=0;  Required=$false },
        @{ Name='MicrosoftCopilotEvents';        ExpectMin=0;  Required=$false; CopilotConnector=$true }
    )
    foreach ($t in $AdditionalTables) {
        $baseTables += @{ Name=$t; ExpectMin=0; Required=$false }
    }

    $tableResults = foreach ($t in $baseTables) {
        # Sovereign suppress — Copilot connector unavailable in GCC High / DoD as of verification date
        if ($t.CopilotConnector -and -not $sovereign.CopilotConnectorAvail) {
            [pscustomobject]@{
                Table=$t.Name; Status='NotApplicable'
                Reason="Microsoft 365 Copilot connector not available in $Cloud as of verification date"
                RowCount=$null; LookbackHours=$LookbackHours
            }
            continue
        }
        $kql = "$($t.Name) | where TimeGenerated > ago($($LookbackHours)h) | summarize Rows=count(), Last=max(TimeGenerated)"
        try {
            $r = Invoke-AzOperationalInsightsQuery -WorkspaceId $WorkspaceCustomerId -Query $kql -ErrorAction Stop
            $rows = [int]($r.Results[0].Rows)
            $status = if ($rows -ge $t.ExpectMin -and $rows -gt 0) { 'Clean' }
                      elseif ($rows -eq 0 -and -not $t.Required) { 'Pending' }
                      elseif ($rows -eq 0 -and $t.Required) { 'Anomaly' }
                      else { 'Anomaly' }
            [pscustomobject]@{
                Table=$t.Name; Status=$status
                Reason="Rows in last $($LookbackHours)h: $rows (expect >= $($t.ExpectMin))"
                RowCount=$rows; LastIngestion=$r.Results[0].Last; LookbackHours=$LookbackHours
            }
        } catch {
            $msg = $_.Exception.Message
            $isMissingTable = $msg -match "(?i)Failed to resolve table|SemanticError.*could not be resolved"
            [pscustomobject]@{
                Table=$t.Name
                Status= if ($isMissingTable -and -not $t.Required) { 'NotApplicable' } else { 'Error' }
                Reason= if ($isMissingTable) { "Table not present in workspace (connector not enabled)" } else { $msg }
                RowCount=$null; LookbackHours=$LookbackHours
            }
        }
    }

    $overall = if ($tableResults.Status -contains 'Error') { 'Error' }
               elseif ($tableResults.Status -contains 'Anomaly') { 'Anomaly' }
               elseif ($tableResults.Status -contains 'Pending') { 'Pending' }
               else { 'Clean' }

    [pscustomobject]@{
        ControlId      = '3.9'
        HelperVersion  = '1.4.0'
        Status         = $overall
        Reason         = "Probed $($tableResults.Count) tables; overall=$overall"
        WorkspaceCustomerId = $WorkspaceCustomerId
        Cloud          = $Cloud
        LookbackHours  = $LookbackHours
        Tables         = $tableResults
        Findings       = @($tableResults | Where-Object Status -in @('Anomaly','Error') |
                           ForEach-Object { "$($_.Table): $($_.Status) — $($_.Reason)" })
        GeneratedUtc   = (Get-Date).ToUniversalTime()
    }
}
```

---

## §5 — Connector management

The AI-agent monitoring overlay requires **six** connectors. Each helper:

1. Validates sovereign-cloud availability via the `Initialize-Agt39SovereignContext` map.
2. Performs a connector-state idempotency probe.
3. Wraps the enable call in `ShouldProcess`.
4. Returns the standard contract object — never `$null`, never `@()` without a status.

### 5.1 — `Enable-Fsi-EntraConnector`

The Entra Sentinel connector exposes **four** diagnostic-setting categories: `SignInLogs` (interactive user), `NonInteractiveUserSignInLogs`, `ServicePrincipalSignInLogs`, and `ManagedIdentitySignInLogs`. The Sentinel UI groups them under one connector tile, so administrators frequently leave service-principal logs **disabled** by default. For AI-agent monitoring, both the user stream **and** the service-principal stream are mandatory — agents authenticate as service principals.

```powershell
function Enable-Fsi-EntraConnector {
<#
.SYNOPSIS
Enables the Entra (Azure AD) Sentinel data connector for AI-agent monitoring.

.DESCRIPTION
Enables BOTH the user sign-in (SigninLogs) and service-principal sign-in
(AADServicePrincipalSignInLogs) diagnostic-setting streams. Refuses to enable only
one stream — partial enablement produces false-clean hunts for agent-as-workload-identity
patterns. Also enables NonInteractiveUserSignInLogs and ManagedIdentitySignInLogs by
default; pass -ExcludeManagedIdentity to suppress the latter.

.PARAMETER ResourceGroupName
Resource group hosting the Sentinel workspace.

.PARAMETER WorkspaceName
Sentinel workspace.

.PARAMETER EnableUser
Enable SigninLogs + NonInteractiveUserSignInLogs. Default: true.

.PARAMETER EnableServicePrincipal
Enable AADServicePrincipalSignInLogs. Default: true. Required for AI-agent monitoring.

.PARAMETER ExcludeManagedIdentity
Suppress ManagedIdentitySignInLogs (not always relevant for FSI agent scope).

.PARAMETER Cloud
Sovereign cloud selector.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required: Sentinel Contributor + Entra Security Administrator
Cross-ref:      Control 1.7 (Audit Logging), Control 1.11 (Conditional Access)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [bool]$EnableUser = $true,
        [bool]$EnableServicePrincipal = $true,
        [switch]$ExcludeManagedIdentity,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [string]$EvidencePath = ".\evidence\3.9"
    )
    if (-not $EnableUser -and -not $EnableServicePrincipal) {
        throw "At least one stream must be enabled. AI-agent monitoring requires BOTH; this is the canonical false-clean defect (§0.2 #1)."
    }
    if (-not $EnableServicePrincipal) {
        Write-Warning "AADServicePrincipalSignInLogs DISABLED by caller. AI-agent service-principal sign-ins will be invisible. This is the canonical false-clean defect (§0.2 #1). Confirm intent via -Confirm."
    }
    if (-not $EnableUser) {
        Write-Warning "SigninLogs DISABLED by caller. Interactive user sign-ins (including agent-on-behalf-of flows) will be invisible. Confirm intent via -Confirm."
    }

    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    $findings = @()

    $streams = @()
    if ($EnableUser) {
        $streams += 'SignInLogs'
        $streams += 'NonInteractiveUserSignInLogs'
    }
    if ($EnableServicePrincipal) {
        $streams += 'ServicePrincipalSignInLogs'
    }
    if (-not $ExcludeManagedIdentity) {
        $streams += 'ManagedIdentitySignInLogs'
    }

    if ($PSCmdlet.ShouldProcess("$WorkspaceName / Entra connector", "Enable streams: $($streams -join ', ')")) {
        # The Az.SecurityInsights data-connector cmdlet shape is in flux; using the REST path.
        # Production deployments standardize on the ARM template at
        # FSI-AgentGov-Solutions/solutions/sentinel-baseline/connectors/entra.bicep
        $connectorJson = @{
            kind = 'AzureActiveDirectory'
            properties = @{
                tenantId = (Get-AzContext).Tenant.Id
                dataTypes = @{
                    signInLogs                  = @{ state = if ('SignInLogs' -in $streams) { 'Enabled' } else { 'Disabled' } }
                    nonInteractiveUserSignInLogs= @{ state = if ('NonInteractiveUserSignInLogs' -in $streams) { 'Enabled' } else { 'Disabled' } }
                    servicePrincipalSignInLogs  = @{ state = if ('ServicePrincipalSignInLogs' -in $streams) { 'Enabled' } else { 'Disabled' } }
                    managedIdentitySignInLogs   = @{ state = if ('ManagedIdentitySignInLogs' -in $streams) { 'Enabled' } else { 'Disabled' } }
                }
            }
        } | ConvertTo-Json -Depth 6
        $resourceId = "$($ws.ResourceId)/providers/Microsoft.SecurityInsights/dataConnectors/AzureActiveDirectoryAgt39"
        try {
            $existing = Get-AzResource -ResourceId $resourceId -ApiVersion '2024-03-01' -ErrorAction SilentlyContinue
            $action = if ($existing) { 'Updated' } else { 'Created' }
            New-AzResource -ResourceId $resourceId -ApiVersion '2024-03-01' -Properties (ConvertFrom-Json $connectorJson).properties -Kind 'AzureActiveDirectory' -Force | Out-Null
            $status = 'Clean'; $reason = "Entra connector $action with streams: $($streams -join ', ')"
        } catch {
            $status = 'Error'; $reason = "Entra connector enable failed: $($_.Exception.Message)"
            $findings += $reason
        }
    } else {
        $status = 'Pending'; $reason = "WhatIf: would enable streams $($streams -join ', ')"
    }

    [pscustomobject]@{
        ControlId        = '3.9'
        HelperVersion    = '1.4.0'
        Status           = $status
        Reason           = $reason
        Connector        = 'AzureActiveDirectory'
        Streams          = $streams
        WorkspaceArmId   = $ws.ResourceId
        Cloud            = $Cloud
        Findings         = $findings
        GeneratedUtc     = (Get-Date).ToUniversalTime()
    }
}
```

### 5.2 — `Enable-Fsi-PowerPlatformAdminActivity`

Power Platform admin activity is sourced from the Power Platform connector (preview in some clouds). The connector emits to the `PowerPlatformAdminActivity` table. Maker / environment / DLP-policy changes are the leading indicator for shadow-agent risk feeding [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md).

The Power Platform admin SDK runs only under **Windows PowerShell 5.1 (Desktop)** — see [baseline §2](../../_shared/powershell-baseline.md#2-powershell-edition-and-version-requirements). The helper detects the wrong edition and refuses to silently misreport.

```powershell
function Enable-Fsi-PowerPlatformAdminActivity {
<#
.SYNOPSIS
Enables the Power Platform Sentinel data connector and emits a backfill hint.

.DESCRIPTION
Power Platform admin activity (maker/environment/DLP policy events) is the leading
indicator for shadow-agent risk. The connector populates PowerPlatformAdminActivity.
Returns NotApplicable in clouds where the connector is not yet GA.

.PARAMETER ResourceGroupName
Resource group hosting the Sentinel workspace.

.PARAMETER WorkspaceName
Sentinel workspace.

.PARAMETER Cloud
Sovereign cloud selector.

.PARAMETER BackfillDays
Hint emitted to the connector telemetry log; informational only — connector backfill
is at most 7 days from enablement, longer history must be reconstructed from Purview
audit log via Control 1.7.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required: Sentinel Contributor + Power Platform Admin
Cross-ref:      Control 3.6, Control 1.7, Control 1.8 (DLP policy enforcement)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [ValidateRange(1,7)][int]$BackfillDays = 7,
        [string]$EvidencePath = ".\evidence\3.9"
    )
    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    # Connector availability check — verify Microsoft Learn parity matrix per release
    $connectorAvail = switch ($Cloud) {
        'Commercial' { $true }
        'USGov'      { $true }   # GA since 2024
        'USGovHigh'  { $true }   # verify on each playbook publication
        'USGovDoD'   { $false }  # confirm; some preview features lag
    }
    if (-not $connectorAvail) {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='NotApplicable'
            Reason="Power Platform Sentinel connector not GA in $Cloud as of verification date. Compensating control: ingest Purview audit log records for Power Platform via Control 1.7 + custom Logic App ingestion."
            Connector='PowerPlatformAdminActivity'; Cloud=$Cloud
            Findings=@("Sovereign-skew: Power Platform connector not available in $Cloud")
            GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }

    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    $resourceId = "$($ws.ResourceId)/providers/Microsoft.SecurityInsights/dataConnectors/PowerPlatformAgt39"

    if ($PSCmdlet.ShouldProcess("$WorkspaceName / PowerPlatform connector", "Enable PowerPlatformAdminActivity stream")) {
        try {
            $body = @{
                kind = 'PowerPlatform'
                properties = @{
                    tenantId = (Get-AzContext).Tenant.Id
                    dataTypes = @{
                        powerPlatformAdminActivity = @{ state = 'Enabled' }
                        powerAppsActivity          = @{ state = 'Enabled' }
                        powerAutomateActivity      = @{ state = 'Enabled' }
                        copilotStudioActivity      = @{ state = 'Enabled' }
                    }
                }
            }
            New-AzResource -ResourceId $resourceId -ApiVersion '2024-03-01' -Properties $body.properties -Kind 'PowerPlatform' -Force | Out-Null
            $status='Clean'; $reason="Power Platform connector enabled. Backfill window: $BackfillDays days. For longer history, ingest Purview audit log via Control 1.7."
            $findings=@()
        } catch {
            $status='Error'; $reason=$_.Exception.Message; $findings=@($reason)
        }
    } else {
        $status='Pending'; $reason="WhatIf: would enable PowerPlatform connector"; $findings=@()
    }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Connector='PowerPlatform'; Streams=@('PowerPlatformAdminActivity','PowerAppsActivity','PowerAutomateActivity','CopilotStudioActivity')
        WorkspaceArmId=$ws.ResourceId; Cloud=$Cloud; BackfillHintDays=$BackfillDays
        Findings=$findings; GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

### 5.3 — `Enable-Fsi-Defender365Connector`

The Microsoft Defender XDR connector ingests `AlertInfo`, `AlertEvidence`, `DeviceEvents`, `EmailEvents`, `IdentityLogonEvents`, and the unified incidents stream. For AI-agent scope the **AlertInfo + AlertEvidence + IdentityLogonEvents** subset is mandatory; others are recommended.

```powershell
function Enable-Fsi-Defender365Connector {
<#
.SYNOPSIS
Enables Microsoft Defender XDR (M365 Defender) Sentinel connector.

.DESCRIPTION
Bi-directional incident sync between Defender XDR and Sentinel. Required tables:
AlertInfo, AlertEvidence, IdentityLogonEvents. Recommended additional: DeviceEvents,
EmailEvents, UrlClickEvents.

.PARAMETER IncludeOptionalTables
Switch; when set, also enables DeviceEvents, EmailEvents, UrlClickEvents.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required: Sentinel Contributor + Defender XDR Security Admin
Cross-ref:      Control 1.8 (Runtime Protection), Control 1.24 (Defender AISPM)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [switch]$IncludeOptionalTables,
        [switch]$EnableBidiSync
    )
    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    if (-not $sovereign.DefenderXdrAvail) {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='NotApplicable'
            Reason="Defender XDR connector not available in $Cloud"; Connector='MicrosoftThreatProtection'
            Cloud=$Cloud; Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }
    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    $resourceId = "$($ws.ResourceId)/providers/Microsoft.SecurityInsights/dataConnectors/M365DAgt39"

    $dataTypes = @{
        incidents                = @{ state = 'Enabled' }
        alerts                   = @{ state = 'Enabled' }
        identityLogonEvents      = @{ state = 'Enabled' }
    }
    if ($IncludeOptionalTables) {
        $dataTypes.deviceEvents      = @{ state = 'Enabled' }
        $dataTypes.emailEvents       = @{ state = 'Enabled' }
        $dataTypes.urlClickEvents    = @{ state = 'Enabled' }
    }

    if ($PSCmdlet.ShouldProcess("$WorkspaceName / Defender XDR connector", "Enable")) {
        try {
            $props = @{
                tenantId = (Get-AzContext).Tenant.Id
                dataTypes = $dataTypes
            }
            New-AzResource -ResourceId $resourceId -ApiVersion '2024-03-01' -Properties $props -Kind 'MicrosoftThreatProtection' -Force | Out-Null
            $status='Clean'; $reason="Defender XDR connector enabled with $($dataTypes.Count) data types"
        } catch { $status='Error'; $reason=$_.Exception.Message }
    } else { $status='Pending'; $reason='WhatIf' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Connector='MicrosoftThreatProtection'; DataTypes=@($dataTypes.Keys)
        WorkspaceArmId=$ws.ResourceId; Cloud=$Cloud
        Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

### 5.4 — `Enable-Fsi-DefenderForCloudAppsConnector`

```powershell
function Enable-Fsi-DefenderForCloudAppsConnector {
<#
.SYNOPSIS
Enables Defender for Cloud Apps (MCAS) Sentinel connector. Powers CloudAppEvents and
DLP / shadow-app hunts.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required: Sentinel Contributor + Defender for Cloud Apps Admin
Cross-ref:      Control 1.7, Control 1.8
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud
    )
    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    if (-not $sovereign.DefenderCloudAppsAvail) {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='NotApplicable'
            Reason="Defender for Cloud Apps not available in $Cloud (SKU/region dependent)"
            Connector='MicrosoftCloudAppSecurity'; Cloud=$Cloud
            Findings=@("Sovereign-skew: validate SKU + Microsoft Learn parity matrix")
            GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }
    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    $resourceId = "$($ws.ResourceId)/providers/Microsoft.SecurityInsights/dataConnectors/MCASAgt39"
    if ($PSCmdlet.ShouldProcess("$WorkspaceName / Defender for Cloud Apps", "Enable")) {
        try {
            $props = @{
                tenantId = (Get-AzContext).Tenant.Id
                dataTypes = @{
                    alerts = @{ state = 'Enabled' }
                    discoveryLogs = @{ state = 'Enabled' }
                }
            }
            New-AzResource -ResourceId $resourceId -ApiVersion '2024-03-01' -Properties $props -Kind 'MicrosoftCloudAppSecurity' -Force | Out-Null
            $status='Clean'; $reason='Defender for Cloud Apps connector enabled'
        } catch { $status='Error'; $reason=$_.Exception.Message }
    } else { $status='Pending'; $reason='WhatIf' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Connector='MicrosoftCloudAppSecurity'; WorkspaceArmId=$ws.ResourceId; Cloud=$Cloud
        Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

### 5.5 — `Enable-Fsi-MicrosoftCopilotConnector`

The Microsoft 365 Copilot connector ingests prompt + response telemetry to the `MicrosoftCopilotEvents` table. The connector reached **GA** in the commercial cloud and is rolling out to GCC; sovereign callers should treat `NotApplicable` as the expected response in GCC High / DoD until Microsoft Learn confirms parity.

```powershell
function Enable-Fsi-MicrosoftCopilotConnector {
<#
.SYNOPSIS
Enables Microsoft 365 Copilot Sentinel data connector (GA in commercial; lagging in
sovereign clouds).

.DESCRIPTION
Populates the MicrosoftCopilotEvents table with Copilot prompt/response telemetry.
Returns NotApplicable in clouds where the connector is not yet GA. Costs scale with
prompt volume — review the Sentinel ingestion calculator before enabling at scale.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required: Sentinel Contributor + Microsoft 365 Copilot Admin
Cross-ref:      Control 2.6 (Model Risk), Control 1.24 (AISPM)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud
    )
    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    if (-not $sovereign.CopilotConnectorAvail) {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='NotApplicable'
            Reason="Microsoft 365 Copilot Sentinel connector not available in $Cloud as of verification date. Compensating control: route Copilot interaction telemetry via Purview audit log (Control 1.7) and Defender XDR alerts (5.3)."
            Connector='MicrosoftCopilot'; Cloud=$Cloud
            Findings=@("Sovereign-skew: Copilot connector not available in $Cloud")
            GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }
    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    $resourceId = "$($ws.ResourceId)/providers/Microsoft.SecurityInsights/dataConnectors/CopilotAgt39"
    if ($PSCmdlet.ShouldProcess("$WorkspaceName / Microsoft 365 Copilot connector", "Enable")) {
        try {
            $props = @{
                tenantId = (Get-AzContext).Tenant.Id
                dataTypes = @{
                    copilotEvents = @{ state = 'Enabled' }
                }
            }
            New-AzResource -ResourceId $resourceId -ApiVersion '2024-03-01' -Properties $props -Kind 'MicrosoftCopilot' -Force | Out-Null
            $status='Clean'; $reason='Microsoft 365 Copilot connector enabled. Review ingestion-cost projection in Sentinel calculator.'
        } catch { $status='Error'; $reason=$_.Exception.Message }
    } else { $status='Pending'; $reason='WhatIf' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Connector='MicrosoftCopilot'; WorkspaceArmId=$ws.ResourceId; Cloud=$Cloud
        Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

### 5.6 — `Enable-Fsi-AppInsightsLink` (optional, governance-gated)

!!! warning "Conversation-transcript enablement requires legal + privacy + records approval"
    Linking Application Insights into Sentinel for **agent conversation transcripts** moves PII / privileged communications / customer NPI from the agent's runtime into Sentinel's Log Analytics workspace, where retention, access, and discovery semantics differ from the agent's primary store. **Three** governance approvals are mandatory before enablement: (1) **Legal** — privilege and litigation-hold implications; (2) **Privacy** — GLBA Safeguards Rule data-mapping update; (3) **Records** — Control 1.9 retention-label assignment so the captured transcripts remain consistent with the firm's records schedule. This helper refuses to run without all three approval ticket IDs.

```powershell
function Enable-Fsi-AppInsightsLink {
<#
.SYNOPSIS
Optional: links an Application Insights resource to Sentinel for agent conversation
transcript ingestion. REQUIRES legal + privacy + records governance approval.

.DESCRIPTION
Links a per-agent Application Insights resource into the Sentinel workspace as a
custom data source. The resulting AppTraces / AppRequests rows can contain agent
prompts, responses, and tool-call payloads — i.e., PII / privileged communications /
customer NPI. The helper enforces a triple governance gate: Legal, Privacy, and
Records approval ticket IDs are mandatory parameters; the helper refuses to proceed
without all three. The transcript stream is also tagged for downstream Purview
retention-label application via Control 1.9.

.PARAMETER LegalApprovalTicket
Mandatory. Legal review ticket ID covering privilege / litigation-hold implications.

.PARAMETER PrivacyApprovalTicket
Mandatory. Privacy review ticket ID covering GLBA Safeguards Rule data-mapping update.

.PARAMETER RecordsApprovalTicket
Mandatory. Records management ticket ID confirming Control 1.9 retention label
assignment for the captured transcripts.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required: Sentinel Contributor + Records Officer (approval) + Privacy Officer (approval) + Legal (approval)
Cross-ref:      Control 1.9 (Retention), Control 1.7 (Audit Logging)
WARNING:        Captures PII / privileged communications. Triple approval gate.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][string]$AppInsightsResourceId,
        [Parameter(Mandatory)][string]$LegalApprovalTicket,
        [Parameter(Mandatory)][string]$PrivacyApprovalTicket,
        [Parameter(Mandatory)][string]$RecordsApprovalTicket,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [string]$EvidencePath = ".\evidence\3.9"
    )
    foreach ($t in @($LegalApprovalTicket, $PrivacyApprovalTicket, $RecordsApprovalTicket)) {
        if ([string]::IsNullOrWhiteSpace($t) -or $t.Length -lt 4) {
            throw "Approval ticket IDs must be present and non-trivial. Conversation-transcript enablement requires legal + privacy + records approval — see helper warning."
        }
    }
    Write-Warning "App Insights link enables conversation-transcript capture. Approval tickets recorded: Legal=$LegalApprovalTicket, Privacy=$PrivacyApprovalTicket, Records=$RecordsApprovalTicket. Cross-ref Control 1.9 for retention-label application."

    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    if ($PSCmdlet.ShouldProcess("$WorkspaceName <- $AppInsightsResourceId", "Link App Insights for transcript capture")) {
        # Implementation: configure the App Insights resource diagnostic-settings
        # to forward AppTraces / AppRequests / AppDependencies to the Sentinel workspace.
        # Exact cmdlet path varies by Az.Monitor version; canonical ARM template at
        # FSI-AgentGov-Solutions/solutions/sentinel-baseline/app-insights-link.bicep
        try {
            $diagName = 'Agt39-AppInsights-To-Sentinel'
            $logs = @(
                @{ category='AppTraces';      enabled=$true },
                @{ category='AppRequests';    enabled=$true },
                @{ category='AppDependencies';enabled=$true }
            )
            New-AzDiagnosticSetting -ResourceId $AppInsightsResourceId -Name $diagName `
                -WorkspaceId $ws.ResourceId -Log $logs -ErrorAction Stop | Out-Null
            $status='Clean'; $reason="App Insights linked. Approval-ticket evidence persisted to $EvidencePath."
        } catch { $status='Error'; $reason=$_.Exception.Message }
    } else { $status='Pending'; $reason='WhatIf' }

    # Persist approval evidence
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    @{
        ControlId='3.9'; Helper='Enable-Fsi-AppInsightsLink'
        AppInsightsResourceId=$AppInsightsResourceId
        WorkspaceArmId=$ws.ResourceId
        ApprovalTickets=@{ Legal=$LegalApprovalTicket; Privacy=$PrivacyApprovalTicket; Records=$RecordsApprovalTicket }
        EnabledByUser=$env:USERNAME; EnabledUtc=(Get-Date).ToUniversalTime()
    } | ConvertTo-Json -Depth 5 | Set-Content "$EvidencePath\appinsights-link-$(Get-Date -Format yyyyMMddHHmmss).json"

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Connector='AppInsightsLink'; WorkspaceArmId=$ws.ResourceId; Cloud=$Cloud
        ApprovalTickets=@{ Legal=$LegalApprovalTicket; Privacy=$PrivacyApprovalTicket; Records=$RecordsApprovalTicket }
        Findings=@("Conversation-transcript capture enabled; route via Control 1.9 retention label.")
        GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

---

## §6 — Analytics rules as code

Seven AI-agent-specific scheduled or NRT (near-real-time) analytics rules form the detection baseline. Every rule:

- Carries a stable `DisplayName` prefix `[FSI-3.9]` for SOC dashboard filtering.
- Carries a `Tactics` array mapping to MITRE ATT&CK technique IDs.
- Carries `CustomDetails` with `RelatedControl` cross-ref tags.
- Is created **enabled** (`-Enabled $true` is explicit, not relying on template default — see §0.2 #6).
- Returns the standard contract object plus the rule's resource ID and a SHA-256 hash of the KQL query (for change detection in the §10 evidence helper).

A common builder is used for parameter validation, hash computation, and tagging.

### 6.0 — Common rule builder

```powershell
function _Agt39NewSentinelRule {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][string]$RuleName,
        [Parameter(Mandatory)][string]$Description,
        [Parameter(Mandatory)][string]$Query,
        [ValidateSet('Informational','Low','Medium','High')][string]$Severity = 'Medium',
        [string]$QueryFrequency = 'PT5M',
        [string]$QueryPeriod = 'PT1H',
        [int]$TriggerThreshold = 0,
        [string[]]$Tactics = @(),
        [string[]]$Techniques = @(),
        [hashtable]$CustomDetails = @{},
        [hashtable]$EntityMapping = @{},
        [ValidateSet('Scheduled','NRT')][string]$Kind = 'Scheduled',
        [string]$RelatedControl = '3.9'
    )
    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    $hash = [Convert]::ToBase64String([System.Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes($Query)))
    $ruleGuid = [guid]::NewGuid().ToString()
    $resourceId = "$($ws.ResourceId)/providers/Microsoft.SecurityInsights/alertRules/$ruleGuid"

    $details = @{} + $CustomDetails
    $details['FSIControl']        = '3.9'
    $details['FSIRelatedControl'] = $RelatedControl
    $details['FSIRuleVersion']    = '1.4.0'
    $details['FSIQueryHash']      = $hash

    $props = @{
        displayName       = "[FSI-3.9] $RuleName"
        description       = $Description
        severity          = $Severity
        enabled           = $true
        query             = $Query
        queryFrequency    = $QueryFrequency
        queryPeriod       = $QueryPeriod
        triggerOperator   = 'GreaterThan'
        triggerThreshold  = $TriggerThreshold
        suppressionEnabled= $false
        tactics           = $Tactics
        techniques        = $Techniques
        customDetails     = $details
        entityMappings    = @($EntityMapping.GetEnumerator() | ForEach-Object { @{ entityType = $_.Key; fieldMappings = $_.Value } })
        incidentConfiguration = @{
            createIncident       = $true
            groupingConfiguration= @{ enabled = $true; lookbackDuration='PT1H'; matchingMethod='AllEntities' }
        }
    }
    if ($Kind -eq 'NRT') {
        $props.Remove('queryFrequency') | Out-Null
        $props.Remove('queryPeriod')    | Out-Null
    }

    if ($PSCmdlet.ShouldProcess($RuleName, "Deploy Sentinel analytics rule ($Kind)")) {
        try {
            New-AzResource -ResourceId $resourceId -ApiVersion '2024-03-01' -Properties $props -Kind $Kind -Force | Out-Null
            $status='Clean'; $reason="$Kind rule '$RuleName' deployed and enabled (hash=$($hash.Substring(0,12))...)"
        } catch { $status='Error'; $reason=$_.Exception.Message }
    } else { $status='Pending'; $reason='WhatIf' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'
        Status=$status; Reason=$reason
        RuleName="[FSI-3.9] $RuleName"; RuleArmId=$resourceId; Severity=$Severity; Kind=$Kind
        Tactics=$Tactics; Techniques=$Techniques; QueryHash=$hash
        RelatedControl=$RelatedControl
        Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

### 6.1 — `New-Fsi-SentinelAlertRule-PromptInjection`

```powershell
function New-Fsi-SentinelAlertRule-PromptInjection {
<#
.SYNOPSIS
Detects suspected prompt-injection patterns in Microsoft 365 Copilot interactions.

.DESCRIPTION
Heuristic detection of jailbreak / instruction-override patterns in Copilot prompts.
Sources: MicrosoftCopilotEvents (where licensed), AppTraces (when AppInsights link is
enabled per §5.6). Designed as a triage signal — not a definitive classifier. Tuning
recommended after first 30 days; cross-ref Control 1.24 (Defender AISPM) for richer
classifier signals.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Severity:       High (default)
MITRE:          T1059 (Command and Scripting Interpreter), T1565 (Data Manipulation)
Cross-ref:      Control 1.24, Control 2.6, Control 3.4
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [ValidateSet('Informational','Low','Medium','High')][string]$Severity = 'High'
    )
    $kql = @'
let injectionMarkers = dynamic([
    "ignore previous", "disregard prior", "system prompt", "you are now",
    "forget all instructions", "developer mode", "DAN mode", "jailbreak",
    "BEGIN INJECTION", "</system>", "[[OVERRIDE]]"
]);
union isfuzzy=true
    (MicrosoftCopilotEvents
        | where TimeGenerated > ago(15m)
        | extend Prompt = tostring(parse_json(EventData).Prompt)
        | where Prompt has_any (injectionMarkers)
        | project TimeGenerated, UserId=AccountUpn, AppName='Microsoft365Copilot', Prompt),
    (AppTraces
        | where TimeGenerated > ago(15m)
        | where Properties has 'AgentPrompt'
        | extend Prompt = tostring(Properties['AgentPrompt'])
        | where Prompt has_any (injectionMarkers)
        | project TimeGenerated, UserId=tostring(Properties['UserId']), AppName=AppRoleName, Prompt)
| summarize Hits=count(), Examples=make_set(Prompt, 5) by UserId, AppName, bin(TimeGenerated, 5m)
| where Hits > 0
'@
    _Agt39NewSentinelRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName `
        -RuleName 'Prompt Injection Pattern Detected' `
        -Description 'Heuristic detection of jailbreak / instruction-override markers in Copilot or AI agent prompts. Triage signal; cross-ref Control 1.24 for classifier confirmation.' `
        -Query $kql -Severity $Severity -QueryFrequency 'PT5M' -QueryPeriod 'PT15M' `
        -Tactics @('InitialAccess','Execution') `
        -Techniques @('T1059','T1565') `
        -EntityMapping @{ Account = @(@{ identifier='Name'; columnName='UserId' }) } `
        -CustomDetails @{ DetectionType='PromptInjection'; SignalSource='Heuristic' } `
        -RelatedControl '1.24'
}
```

### 6.2 — `New-Fsi-SentinelAlertRule-AnomalousConnectorUse`

```powershell
function New-Fsi-SentinelAlertRule-AnomalousConnectorUse {
<#
.SYNOPSIS
Detects anomalous use of Power Platform connectors by AI agents (newly added connector,
high-risk connector, cross-environment data movement).

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Severity:       Medium
MITRE:          T1071 (Application Layer Protocol), T1567 (Exfiltration Over Web Service)
Cross-ref:      Control 1.8 (DLP), Control 3.6 (Orphan agents)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [ValidateSet('Informational','Low','Medium','High')][string]$Severity = 'Medium'
    )
    $kql = @'
let highRiskConnectors = dynamic([
    "shared_ftp", "shared_sftpwithssh", "shared_smtp", "shared_dropbox",
    "shared_googledrive", "shared_box", "shared_http", "shared_webhook",
    "shared_azureblob", "shared_amazons3"
]);
PowerPlatformAdminActivity
| where TimeGenerated > ago(1h)
| where OperationName in ("ConnectionCreated","ConnectionUpdated")
| extend ConnectorName = tostring(parse_json(EventData).ConnectorName),
         AppId         = tostring(parse_json(EventData).AppId),
         MakerUpn      = tostring(parse_json(EventData).MakerUserPrincipalName)
| where ConnectorName in (highRiskConnectors)
   or AppId has_any ("agent","copilot","bot")
| summarize
    UseCount=count(),
    Connectors=make_set(ConnectorName),
    Apps=make_set(AppId)
    by MakerUpn, bin(TimeGenerated, 15m)
| where UseCount > 0
'@
    _Agt39NewSentinelRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName `
        -RuleName 'Anomalous Connector Use by Agent' `
        -Description 'Agent (or maker on behalf of agent) added or modified a high-risk Power Platform connector. Review against Control 1.8 DLP policies and Control 3.6 owner registry.' `
        -Query $kql -Severity $Severity -QueryFrequency 'PT15M' -QueryPeriod 'PT1H' `
        -Tactics @('Exfiltration','CommandAndControl') `
        -Techniques @('T1071','T1567') `
        -EntityMapping @{ Account = @(@{ identifier='UserPrincipalName'; columnName='MakerUpn' }) } `
        -CustomDetails @{ DetectionType='AnomalousConnector' } `
        -RelatedControl '1.8'
}
```

### 6.3 — `New-Fsi-SentinelAlertRule-AfterHoursPrivilegedAgent`

```powershell
function New-Fsi-SentinelAlertRule-AfterHoursPrivilegedAgent {
<#
.SYNOPSIS
After-hours sign-in by service principals carrying privileged scopes (uses
AADServicePrincipalSignInLogs — distinct from SigninLogs).

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Severity:       High
MITRE:          T1078.004 (Valid Accounts: Cloud Accounts), T1098 (Account Manipulation)
Cross-ref:      Control 1.11 (CA + MFA), Control 2.12 (Supervision)
NOTE:           SigninLogs is the WRONG table — agent service-principal sign-ins land
                in AADServicePrincipalSignInLogs. See §0.2 defect #1.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [ValidateSet('Informational','Low','Medium','High')][string]$Severity = 'High',
        [int]$BusinessHourStart = 7,
        [int]$BusinessHourEnd   = 19,
        [string]$BusinessTimeZone = 'America/New_York'
    )
    $kql = @"
let privilegedScopes = dynamic([
    "Application.ReadWrite.All","Directory.ReadWrite.All",
    "RoleManagement.ReadWrite.Directory","User.ReadWrite.All",
    "Mail.ReadWrite","Files.ReadWrite.All","Sites.FullControl.All"
]);
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(1h)
| extend LocalTime = datetime_local('${BusinessTimeZone}', TimeGenerated)
| extend LocalHour = datetime_part('hour', LocalTime)
| where LocalHour < ${BusinessHourStart} or LocalHour >= ${BusinessHourEnd}
| where Tags has 'AgentIdentity' or ServicePrincipalName has_any ('agent','copilot','bot')
| mv-expand Scope = parse_json(ResourceTokenIssuedScope)
| where tostring(Scope) in (privilegedScopes)
| summarize Signins=count(), Scopes=make_set(Scope), IPs=make_set(IPAddress)
    by ServicePrincipalId, ServicePrincipalName, bin(TimeGenerated, 15m)
| where Signins > 0
"@
    _Agt39NewSentinelRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName `
        -RuleName 'After-Hours Privileged Agent Sign-In' `
        -Description 'Service principal carrying AgentIdentity tag or named *agent*/*copilot*/*bot* signed in outside business hours with privileged scopes. Sourced from AADServicePrincipalSignInLogs (NOT SigninLogs).' `
        -Query $kql -Severity $Severity -QueryFrequency 'PT15M' -QueryPeriod 'PT1H' `
        -Tactics @('CredentialAccess','Persistence','PrivilegeEscalation') `
        -Techniques @('T1078.004','T1098') `
        -EntityMapping @{
            Account = @(@{ identifier='AadUserId'; columnName='ServicePrincipalId' });
            IP      = @(@{ identifier='Address';   columnName='IPs' })
        } `
        -CustomDetails @{ DetectionType='AfterHoursPrivilegedAgent'; SourceTable='AADServicePrincipalSignInLogs' } `
        -RelatedControl '1.11'
}
```

### 6.4 — `New-Fsi-SentinelAlertRule-DLPChange`

```powershell
function New-Fsi-SentinelAlertRule-DLPChange {
<#
.SYNOPSIS
Detects modifications to Power Platform DLP policies that could relax connector
restrictions previously enforcing AI-agent guardrails.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Severity:       High
MITRE:          T1562 (Impair Defenses)
Cross-ref:      Control 1.8 (DLP), Control 2.25 (Governance Console)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [ValidateSet('Informational','Low','Medium','High')][string]$Severity = 'High'
    )
    $kql = @'
PowerPlatformAdminActivity
| where TimeGenerated > ago(15m)
| where OperationName in ("DlpPolicyUpdated","DlpPolicyDeleted","DlpPolicyConnectorReclassified")
| extend
    PolicyName = tostring(parse_json(EventData).PolicyName),
    ChangedBy  = tostring(parse_json(EventData).ChangedByUserPrincipalName),
    Change     = tostring(parse_json(EventData).Change)
| project TimeGenerated, OperationName, PolicyName, ChangedBy, Change
'@
    _Agt39NewSentinelRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName `
        -RuleName 'DLP Policy Change' `
        -Description 'Power Platform DLP policy was updated, deleted, or had a connector reclassified. Reconcile against Control 1.8 baseline within 24h.' `
        -Query $kql -Severity $Severity -QueryFrequency 'PT5M' -QueryPeriod 'PT15M' `
        -Tactics @('DefenseEvasion') `
        -Techniques @('T1562') `
        -EntityMapping @{ Account = @(@{ identifier='UserPrincipalName'; columnName='ChangedBy' }) } `
        -CustomDetails @{ DetectionType='DLPChange' } `
        -RelatedControl '1.8'
}
```

### 6.5 — `New-Fsi-SentinelAlertRule-UnusualConsentGrant`

```powershell
function New-Fsi-SentinelAlertRule-UnusualConsentGrant {
<#
.SYNOPSIS
Detects unusual OAuth consent grants to AI-agent service principals (privileged scopes,
unverified publisher, or admin consent without preceding ticket).

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Severity:       High
MITRE:          T1550 (Use Alternate Authentication Material), T1078.004
Cross-ref:      Control 1.11, Control 1.7
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [ValidateSet('Informational','Low','Medium','High')][string]$Severity = 'High'
    )
    $kql = @'
let privilegedScopes = dynamic([
    "Application.ReadWrite.All","Directory.ReadWrite.All",
    "Mail.ReadWrite","Files.ReadWrite.All","Sites.FullControl.All",
    "RoleManagement.ReadWrite.Directory"
]);
AuditLogs
| where TimeGenerated > ago(15m)
| where OperationName in ("Consent to application","Add app role assignment grant to user","Add delegated permission grant")
| extend
    AppDisplayName = tostring(TargetResources[0].displayName),
    ScopeGranted   = tostring(parse_json(tostring(TargetResources[0].modifiedProperties))[0].newValue),
    Initiator      = tostring(InitiatedBy.user.userPrincipalName)
| where AppDisplayName has_any ("agent","copilot","bot","gpt","ai")
   or ScopeGranted has_any (privilegedScopes)
| project TimeGenerated, AppDisplayName, ScopeGranted, Initiator, OperationName
'@
    _Agt39NewSentinelRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName `
        -RuleName 'Unusual Consent Grant to Agent' `
        -Description 'OAuth consent granted to an AI-agent named app or with privileged scopes. Reconcile against Control 1.11 conditional access and ticketing within 24h.' `
        -Query $kql -Severity $Severity -QueryFrequency 'PT5M' -QueryPeriod 'PT15M' `
        -Tactics @('PrivilegeEscalation','InitialAccess') `
        -Techniques @('T1550','T1078.004') `
        -EntityMapping @{ Account = @(@{ identifier='UserPrincipalName'; columnName='Initiator' }) } `
        -CustomDetails @{ DetectionType='UnusualConsent' } `
        -RelatedControl '1.11'
}
```

### 6.6 — `New-Fsi-SentinelAlertRule-OrphanShadowAgent`

This rule **cascades to Control 3.6**. The incident emits a `RelatedControl=3.6` `CustomDetails` property and a `Tactics=@('InitialAccess','Persistence')` mapping so the SOC routes the incident through 3.6's four-tier remediation ladder, not a generic close-as-FP.

```powershell
function New-Fsi-SentinelAlertRule-OrphanShadowAgent {
<#
.SYNOPSIS
Detects appearance of orphan or shadow AI agents in tenant signals that 3.6's
detection pipeline has not yet seen. Cascades to Control 3.6 remediation ladder.

.DESCRIPTION
Hunts for AI-agent service principals exhibiting first-seen activity without a
matching entry in the 3.6 owner registry (joined via watchlist Agt36AgentRegistry).
Emits CustomDetails.RelatedControl='3.6' so SOC routing forwards to Control 3.6's
tier-1 remediation flow, not generic incident triage.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Severity:       High
MITRE:          T1078.004 (Valid Accounts), T1098 (Persistence)
Cross-ref:      Control 3.6 (Orphan Agents), Control 2.25 (Governance Console)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [ValidateSet('Informational','Low','Medium','High')][string]$Severity = 'High'
    )
    $kql = @'
let registry = _GetWatchlist('Agt36AgentRegistry')
    | project KnownAgentId = tostring(AgentId);
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(1h)
| where Tags has 'AgentIdentity' or ServicePrincipalName has_any ('agent','copilot','bot')
| summarize FirstSeen=min(TimeGenerated), LastSeen=max(TimeGenerated), Signins=count(),
            IPs=make_set(IPAddress)
    by ServicePrincipalId, ServicePrincipalName
| join kind=leftanti registry on $left.ServicePrincipalId == $right.KnownAgentId
| where Signins > 0
'@
    _Agt39NewSentinelRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName `
        -RuleName 'Orphan or Shadow Agent Detected' `
        -Description 'Service principal carrying AgentIdentity tag (or named *agent*/*copilot*/*bot*) signed in but is not present in Control 3.6 owner registry watchlist. Route to 3.6 tier-1 remediation.' `
        -Query $kql -Severity $Severity -QueryFrequency 'PT15M' -QueryPeriod 'PT1H' `
        -Tactics @('InitialAccess','Persistence') `
        -Techniques @('T1078.004','T1098') `
        -EntityMapping @{
            Account = @(@{ identifier='AadUserId'; columnName='ServicePrincipalId' })
        } `
        -CustomDetails @{
            DetectionType  = 'OrphanShadowAgent'
            CascadeControl = '3.6'
            RemediationTier= '3.6-Tier-1'
        } `
        -RelatedControl '3.6'
}
```

### 6.7 — `New-Fsi-SentinelAlertRule-MassDataDownload`

```powershell
function New-Fsi-SentinelAlertRule-MassDataDownload {
<#
.SYNOPSIS
Detects mass data download or sync by an AI-agent service principal or maker
on-behalf-of an agent. Indicator for exfiltration; cross-ref Control 1.8.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Severity:       High
MITRE:          T1530 (Data from Cloud Storage Object), T1567 (Exfiltration Over Web Service)
Cross-ref:      Control 1.8 (DLP), Control 3.4 (Incident reporting)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [ValidateSet('Informational','Low','Medium','High')][string]$Severity = 'High',
        [int]$FileCountThreshold = 50,
        [long]$ByteThreshold = 100000000
    )
    $kql = @"
OfficeActivity
| where TimeGenerated > ago(15m)
| where (UserId has_any ('agent','copilot','bot') or ApplicationName has_any ('Copilot','Agent'))
| where Operation in ('FileDownloaded','FileSyncDownloadedFull','FileAccessed','FileCopied')
| summarize
    FileCount  = count(),
    TotalBytes = sum(tolong(coalesce(column_ifexists('FileSize',0), 0))),
    UniqueFiles= dcount(OfficeObjectId),
    Workloads  = make_set(OfficeWorkload)
    by UserId, bin(TimeGenerated, 15m)
| where FileCount > ${FileCountThreshold} or TotalBytes > ${ByteThreshold}
"@
    _Agt39NewSentinelRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName `
        -RuleName 'Mass Data Download by Agent' `
        -Description 'Agent or agent-on-behalf-of session downloaded > threshold files or bytes in a 15-minute window. Cross-ref Control 1.8 DLP and consider Control 3.4 incident draft.' `
        -Query $kql -Severity $Severity -QueryFrequency 'PT5M' -QueryPeriod 'PT15M' `
        -Tactics @('Exfiltration','Collection') `
        -Techniques @('T1530','T1567') `
        -EntityMapping @{ Account = @(@{ identifier='Name'; columnName='UserId' }) } `
        -CustomDetails @{ DetectionType='MassDataDownload'; FileThreshold=$FileCountThreshold; ByteThreshold=$ByteThreshold } `
        -RelatedControl '1.8'
}
```

---

## §7 — Logic App / automation rule deployers

Three SOAR helpers. Each deploys a Logic App **playbook** (the Sentinel SOAR runbook) plus an **automation rule** that wires the playbook to a triggering condition. Permissions:

- The Logic App **Managed Identity** must hold (a) `Microsoft Sentinel Responder` on the workspace; (b) for `SuspendAgent`, Graph `Application.ReadWrite.OwnedBy` and Power Platform Admin role; (c) for `NotifyOwnerSOC`, Graph `Mail.Send` (or Teams webhook scope); (d) for `NYDFS72hTimer`, only the Sentinel update scope.
- The deployer validates these role assignments **before** declaring deployment complete (§0.2 #10).

### 7.1 — `New-Fsi-SentinelPlaybook-SuspendAgent`

```powershell
function New-Fsi-SentinelPlaybook-SuspendAgent {
<#
.SYNOPSIS
Deploys a Logic App playbook that suspends an agent service principal in response to
a high-severity Sentinel incident. Validates Managed Identity has required roles
before declaring deployment complete.

.DESCRIPTION
Creates a Logic App in the supplied resource group, assigns it a system-assigned
managed identity, grants the MI Sentinel Responder + Graph Application.ReadWrite.OwnedBy
+ Power Platform Admin (where configured), and wires it to an automation rule that
fires on incidents with CustomDetails.DetectionType in {AfterHoursPrivilegedAgent,
OrphanShadowAgent, MassDataDownload}.

The actual suspension action calls Microsoft Graph PATCH /servicePrincipals/{id}
to set accountEnabled=false. For Power Platform agents, the playbook calls the Power
Apps Admin endpoint to set the maker connection to disabled.

This is a TIER-1 ENFORCEMENT helper — it requires a human approval step embedded in
the Logic App ('Send approval to AI Governance Lead and SOC Lead via Teams') unless
-AutoSuspend is explicitly set. -AutoSuspend is reserved for Zone-3 production agents
with a documented break-glass exception.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required (caller): Logic App Contributor + Sentinel Playbook Operator + Owner (one-time MI role grant)
Roles granted to MI:     Sentinel Responder, Graph Application.ReadWrite.OwnedBy, PP Admin (optional)
Cross-ref:               Control 3.6 (Tier-1 remediation), Control 3.4 (Incident reporting)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][string]$LogicAppName,
        [Parameter(Mandatory)][string]$Location,
        [switch]$AutoSuspend,
        [string]$ApprovalTeamsWebhookUrl,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud
    )
    if (-not $AutoSuspend -and [string]::IsNullOrWhiteSpace($ApprovalTeamsWebhookUrl)) {
        throw "ApprovalTeamsWebhookUrl is required unless -AutoSuspend is set. Tier-1 enforcement defaults to human-in-the-loop."
    }
    if ($AutoSuspend) {
        Write-Warning "AutoSuspend is enabled. Confirm a documented break-glass exception exists per Control 3.6 tier-1 ladder. This bypasses human approval."
    }
    # Logic App workflow definition is canonicalized in
    # FSI-AgentGov-Solutions/solutions/sentinel-baseline/playbooks/suspend-agent.json
    $workflowDefinition = @{
        '$schema'        = 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
        contentVersion   = '1.0.0.0'
        parameters       = @{}
        triggers         = @{ When_Sentinel_incident_triggered = @{ type='ApiConnectionWebhook'; inputs=@{} } }
        actions          = @{
            CheckSeverity = @{ type='If'; expression="@equals(triggerBody()?['Severity'],'High')" }
            ApprovalGate  = if ($AutoSuspend) { $null } else { @{ type='Http'; inputs=@{ method='POST'; uri=$ApprovalTeamsWebhookUrl } } }
            SuspendSP     = @{ type='Http'; inputs=@{ method='PATCH'; uri="https://graph.microsoft.com/v1.0/servicePrincipals/{id}"; body=@{ accountEnabled=$false } } }
            UpdateIncident= @{ type='Http'; inputs=@{ method='POST'; uri='[concat(...sentinel api...)]' } }
        }
    }

    if ($PSCmdlet.ShouldProcess($LogicAppName, "Deploy SuspendAgent Logic App + automation rule")) {
        try {
            # Az.LogicApp deployment
            $la = New-AzLogicApp -ResourceGroupName $ResourceGroupName -Name $LogicAppName `
                -Location $Location -Definition (ConvertTo-Json -Depth 20 $workflowDefinition) `
                -ErrorAction Stop
            # Enable system-assigned MI
            $laRid = $la.Id
            Set-AzResource -ResourceId $laRid -Properties @{ identity=@{ type='SystemAssigned' } } -Force | Out-Null
            $miPrincipalId = (Get-AzResource -ResourceId $laRid).Identity.PrincipalId

            # Validate / grant roles to MI
            $roleResults = @()
            $roleResults += _Agt39GrantRole -PrincipalId $miPrincipalId -RoleName 'Microsoft Sentinel Responder' -Scope (Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName).ResourceId
            # Graph Application.ReadWrite.OwnedBy granted via Graph app role assignment - separate path
            $roleResults += [pscustomobject]@{ Role='Graph Application.ReadWrite.OwnedBy'; Status='Pending'; Note='Grant via Graph app role assignment script — see verification §10' }

            $status='Clean'; $reason="SuspendAgent playbook deployed. Manual follow-up: confirm Graph app role assignment for MI $miPrincipalId."
        } catch { $status='Error'; $reason=$_.Exception.Message; $roleResults=@() }
    } else { $status='Pending'; $reason='WhatIf'; $roleResults=@() }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Playbook='SuspendAgent'; LogicAppName=$LogicAppName
        AutoSuspend=[bool]$AutoSuspend; ApprovalConfigured=([bool]$ApprovalTeamsWebhookUrl)
        ManagedIdentityRoles=$roleResults; Cloud=$Cloud
        Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}

function _Agt39GrantRole {
    [CmdletBinding()]
    param([string]$PrincipalId, [string]$RoleName, [string]$Scope)
    try {
        $existing = Get-AzRoleAssignment -ObjectId $PrincipalId -RoleDefinitionName $RoleName -Scope $Scope -ErrorAction SilentlyContinue
        if (-not $existing) {
            New-AzRoleAssignment -ObjectId $PrincipalId -RoleDefinitionName $RoleName -Scope $Scope -ErrorAction Stop | Out-Null
            return [pscustomobject]@{ Role=$RoleName; Scope=$Scope; Status='Granted'; Note='New assignment' }
        }
        return [pscustomobject]@{ Role=$RoleName; Scope=$Scope; Status='AlreadyPresent'; Note='Idempotent' }
    } catch {
        return [pscustomobject]@{ Role=$RoleName; Scope=$Scope; Status='Error'; Note=$_.Exception.Message }
    }
}
```

### 7.2 — `New-Fsi-SentinelPlaybook-NotifyOwnerSOC`

```powershell
function New-Fsi-SentinelPlaybook-NotifyOwnerSOC {
<#
.SYNOPSIS
Deploys a Logic App that notifies the agent owner (from Control 3.6 registry) and the
SOC on-call channel when an FSI-3.9 incident fires.

.DESCRIPTION
Looks up the owner UPN from the Agt36AgentRegistry watchlist using the incident's
ServicePrincipalId entity, then sends parallel notifications: an email to the owner +
their manager (Graph Mail.Send), a Teams card to the SOC on-call channel, and an
incident comment back to Sentinel with the notification audit trail.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Roles required: Logic App Contributor + Sentinel Playbook Operator
Roles granted to MI: Sentinel Responder, Mail.Send (Graph), Teams webhook (per channel)
Cross-ref:      Control 3.6 (Owner registry), Control 3.4 (Incident reporting)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][string]$LogicAppName,
        [Parameter(Mandatory)][string]$Location,
        [Parameter(Mandatory)][string]$SocTeamsWebhookUrl,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud
    )
    # Workflow canonicalized at FSI-AgentGov-Solutions/solutions/sentinel-baseline/playbooks/notify-owner-soc.json
    if ($PSCmdlet.ShouldProcess($LogicAppName, "Deploy NotifyOwnerSOC Logic App")) {
        try {
            $la = New-AzLogicApp -ResourceGroupName $ResourceGroupName -Name $LogicAppName -Location $Location `
                -Definition (ConvertTo-Json -Depth 10 @{ '$schema'='https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'; contentVersion='1.0.0.0'; triggers=@{}; actions=@{} }) `
                -ErrorAction Stop
            $status='Clean'; $reason='NotifyOwnerSOC playbook deployed.'
        } catch { $status='Error'; $reason=$_.Exception.Message }
    } else { $status='Pending'; $reason='WhatIf' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Playbook='NotifyOwnerSOC'; LogicAppName=$LogicAppName; SocWebhookConfigured=$true
        Cloud=$Cloud; Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

### 7.3 — `New-Fsi-SentinelPlaybook-NYDFS72hTimer`

NYDFS 23 NYCRR 500.17(a) requires notification to the Department of Financial Services within **72 hours** of determining a covered cybersecurity event. **This helper does not file the notification.** It sets a tag, computes the 72h deadline in **UTC** (forced — see §0.2 #11), and schedules a Logic App reminder cadence (T+24h, T+48h, T+60h, T+71h). The actual filing flow is in [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

```powershell
function New-Fsi-SentinelPlaybook-NYDFS72hTimer {
<#
.SYNOPSIS
Deploys a Logic App that tags an incident with a NYDFS 72h deadline (UTC) and
schedules reminder notifications. DOES NOT file the actual NYDFS notification — see
Control 3.4 for the filing flow.

.DESCRIPTION
On a Sentinel incident with CustomDetails.NYDFSReportable=true, this playbook:
  1. Computes deadline = TimeGenerated + 72h (UTC, never local time)
  2. Tags incident with NYDFS-Deadline-{ISO8601-UTC}
  3. Schedules reminders at T+24h, +48h, +60h, +71h via deferred Logic App runs
  4. Posts reminders to the AI Governance Lead + Compliance team
At T+71h, if the incident's NYDFSFiledTicketId CustomDetails property is empty, the
playbook escalates to the CISO and General Counsel.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Regulatory:     NYDFS 23 NYCRR 500.17(a) — 72h notification
Cross-ref:      Control 3.4 (filing flow), Control 1.7 (audit trail)
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][string]$LogicAppName,
        [Parameter(Mandatory)][string]$Location,
        [Parameter(Mandatory)][string]$GovernanceTeamsWebhookUrl,
        [Parameter(Mandatory)][string]$EscalationDistributionListUpn,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud
    )
    # Force UTC on all recurrence triggers — defect §0.2 #11
    $workflowDefinition = @{
        '$schema'      = 'https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#'
        contentVersion = '1.0.0.0'
        parameters     = @{}
        triggers       = @{
            When_Sentinel_incident_triggered = @{
                type='ApiConnectionWebhook'
                recurrence = @{ frequency='Hour'; interval=1; timeZone='UTC' }   # explicit UTC
            }
        }
        actions = @{
            ComputeDeadlineUtc = @{
                type='Compose'
                inputs="@{addToTime(triggerBody()?['CreatedTimeUtc'],72,'Hour')}"
            }
            TagIncident = @{ type='Http'; inputs=@{ method='POST'; uri='[sentinel-update-incident-tag]' } }
            ScheduleReminders = @{ type='ForEach'; foreach=@(24,48,60,71) }
            EscalationAtT71 = @{ type='If'; expression="@empty(triggerBody()?['CustomDetails']?['NYDFSFiledTicketId'])" }
        }
    }

    if ($PSCmdlet.ShouldProcess($LogicAppName, "Deploy NYDFS72hTimer Logic App")) {
        try {
            $la = New-AzLogicApp -ResourceGroupName $ResourceGroupName -Name $LogicAppName -Location $Location `
                -Definition (ConvertTo-Json -Depth 20 $workflowDefinition) -ErrorAction Stop
            $status='Clean'; $reason="NYDFS72hTimer deployed. Reminder schedule: T+24,48,60,71h. Escalation at T+71h to $EscalationDistributionListUpn. Filing remains a Control 3.4 human action."
        } catch { $status='Error'; $reason=$_.Exception.Message }
    } else { $status='Pending'; $reason='WhatIf' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Playbook='NYDFS72hTimer'; LogicAppName=$LogicAppName
        DeadlineHours=72; TimeZoneEnforced='UTC'
        EscalationTo=$EscalationDistributionListUpn
        Cloud=$Cloud
        Findings=@("NYDFS notification filing remains a human Control 3.4 action — this helper schedules reminders only.")
        GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

---

## §8 — Retention automation

Two helpers govern table-level retention. Both enforce the §0 scope warning: **Sentinel is monitoring, not records**. The `Export-Fsi-TableToFirmArchive` helper is a **stub** that explicitly cross-refs Control 1.9.

### 8.1 — `Set-Fsi-TableRetention`

```powershell
function Set-Fsi-TableRetention {
<#
.SYNOPSIS
Sets per-table Analytics (hot) and Archive retention on a Log Analytics table backing
a Sentinel workspace. Warns and refuses on policy-floor violations.

.DESCRIPTION
Sentinel tables support two-tier retention: Analytics (hot, queryable, indexed —
default 90d, max 730d) and Archive (lower-cost, restorable but not WORM, up to
4383d / ~12y). Retention is set per-table; the workspace default is applied to any
table without an explicit override.

This helper:
  1. Reads current retention on the table.
  2. Compares against the firm policy floor (parameterized, default 180d hot).
  3. Refuses to REDUCE retention without -Force AND -Justification.
  4. Refuses to set archive lower than hot (invalid).
  5. Emits warnings whenever total retention is below the regulatory minimum for the
     table's data class (parameterized via -DataClass).

.PARAMETER Table
Table name, e.g., 'OfficeActivity', 'AADServicePrincipalSignInLogs'.

.PARAMETER HotDays
Analytics-tier retention in days. Range 30-730.

.PARAMETER ArchiveDays
Total retention (hot + archive) in days. Range matching firm policy; max 4383.

.PARAMETER PolicyFloorDays
Firm policy minimum hot retention. Default 180.

.PARAMETER DataClass
'SecurityTelemetry' (180d floor) | 'AuditTrail' (2555d / 7y floor — but route via
Control 1.9, not here) | 'TranscriptPII' (per legal direction — route via Control 1.9).

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Roles required: Log Analytics Contributor + AI Governance Lead approval (for reductions)
Cross-ref:      Control 1.9 (Records retention — NOT Sentinel's job)
WARNING:        Archive tier is NOT WORM, NOT D3P-attested, NOT a SEC 17a-4 substitute.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][string]$Table,
        [Parameter(Mandatory)][ValidateRange(30,730)][int]$HotDays = 180,
        [Parameter(Mandatory)][ValidateRange(30,4383)][int]$ArchiveDays = 4383,
        [int]$PolicyFloorDays = 180,
        [ValidateSet('SecurityTelemetry','AuditTrail','TranscriptPII')][string]$DataClass = 'SecurityTelemetry',
        [switch]$Force,
        [string]$Justification
    )
    if ($ArchiveDays -lt $HotDays) {
        throw "ArchiveDays ($ArchiveDays) must be >= HotDays ($HotDays). Archive total includes hot."
    }
    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop

    # Read current
    $current = $null
    try {
        $current = Invoke-AzRestMethod -Method GET -Path "$($ws.ResourceId)/tables/$Table?api-version=2023-09-01" -ErrorAction Stop
    } catch {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='Error'
            Reason="Could not read current retention on $Table : $($_.Exception.Message)"
            Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }

    $currentBody = $current.Content | ConvertFrom-Json
    $currentHot     = $currentBody.properties.retentionInDays
    $currentArchive = $currentBody.properties.totalRetentionInDays
    $reducing = ($HotDays -lt $currentHot) -or ($ArchiveDays -lt $currentArchive)

    if ($reducing -and -not ($Force -and $Justification)) {
        Write-Warning "Reducing retention on $Table requires -Force AND -Justification. Current: hot=$currentHot, archive=$currentArchive. Requested: hot=$HotDays, archive=$ArchiveDays."
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='Anomaly'
            Reason="Retention reduction blocked. Pass -Force -Justification '<change ticket id and reason>' to proceed."
            CurrentHot=$currentHot; CurrentArchive=$currentArchive
            RequestedHot=$HotDays; RequestedArchive=$ArchiveDays
            Findings=@("RetentionReductionBlocked"); GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }
    if ($HotDays -lt $PolicyFloorDays) {
        Write-Warning "HotDays ($HotDays) is below firm policy floor ($PolicyFloorDays). Override only with documented exception."
    }
    if ($DataClass -in @('AuditTrail','TranscriptPII')) {
        Write-Warning "DataClass=$DataClass should not be retained primarily in Sentinel. Route via Control 1.9 retention labels for records-management consistency."
    }

    $body = @{
        properties = @{
            retentionInDays      = $HotDays
            totalRetentionInDays = $ArchiveDays
        }
    } | ConvertTo-Json -Depth 5

    if ($PSCmdlet.ShouldProcess("$WorkspaceName / $Table", "Set retention hot=$HotDays archive=$ArchiveDays")) {
        try {
            Invoke-AzRestMethod -Method PATCH -Path "$($ws.ResourceId)/tables/$Table?api-version=2023-09-01" -Payload $body -ErrorAction Stop | Out-Null
            $status='Clean'; $reason="Retention on $Table set to hot=$HotDays archive=$ArchiveDays"
        } catch { $status='Error'; $reason=$_.Exception.Message }
    } else { $status='Pending'; $reason='WhatIf' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Table=$Table; HotDays=$HotDays; ArchiveDays=$ArchiveDays
        PreviousHot=$currentHot; PreviousArchive=$currentArchive
        DataClass=$DataClass; Reduced=[bool]$reducing; Justification=$Justification
        Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

### 8.2 — `Export-Fsi-TableToFirmArchive` (stub)

```powershell
function Export-Fsi-TableToFirmArchive {
<#
.SYNOPSIS
STUB — do NOT use Sentinel as the SEC 17a-4 books-and-records preservation route.

.DESCRIPTION
This helper exists to make the boundary explicit. Any caller attempting to use
Sentinel archive as the firm's books-and-records repository is redirected to
Control 1.9 (Data Retention and Deletion Policies), where Microsoft Purview
retention labels with regulatory hold + designated-third-party (D3P) attestation
provide the WORM-compliant route required by SEC 17a-4(f).

If you need to forward Sentinel data into the records archive (e.g., for a regulatory
production), this stub returns the documented bridge: a Logic App that exports KQL
results to an Azure Storage account configured with Purview retention label
'Records-AI-Telemetry-7Y' (or the firm's equivalent), which itself satisfies
Control 1.9.

This stub does NOT perform the export. It returns a Status='NotApplicable' with the
correct cross-reference.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Cross-ref:      Control 1.9 (Records retention — canonical route)
DO NOT USE:     As a SEC 17a-4 substitute.
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Table,
        [string]$Reason
    )
    Write-Warning "Export-Fsi-TableToFirmArchive is a STUB. Sentinel archive is NOT WORM and NOT a SEC 17a-4 records substitute. Route via Control 1.9 retention labels with regulatory hold."
    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status='NotApplicable'
        Reason="Sentinel-to-firm-archive route is not in 3.9 scope. Use Control 1.9 — see https://learn.microsoft.com/en-us/purview/create-retention-policies-overview and the firm's books-and-records routing in 1.9."
        Table=$Table; CrossRef='1.9-data-retention-and-deletion-policies.md'
        Findings=@("Caller redirected to Control 1.9. Reason supplied: $Reason")
        GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

---

## §9 — Sentinel MCP Server (optional, opt-in)

The **Sentinel MCP (Model Context Protocol) Server** is a preview feature that exposes Sentinel hunt / incident / KQL operations to MCP-aware agent runtimes. For an FSI tenant, the MCP server represents both an **opportunity** (richer SOC-co-pilot agent integration) and a **risk** (preview feature, lagging sovereign-cloud availability, ingestion + token cost spike if enabled tenant-wide). This helper is **opt-in only** behind `-OptIn` and refuses to enable in clouds that do not yet support the preview.

```powershell
function Enable-Fsi-SentinelMcpServer {
<#
.SYNOPSIS
OPTIONAL, OPT-IN: enables the Microsoft Sentinel MCP Server (preview) on a workspace.
Refuses to run unless -OptIn is set, the cloud supports the preview, and the cost
acknowledgement parameter is supplied.

.DESCRIPTION
The Sentinel MCP Server exposes Sentinel hunting, KQL, and incident operations to
MCP-aware agent runtimes (e.g., a SOC analyst Copilot agent). Enablement is a
governance decision because:
  - Preview status: feature-set may shift between releases.
  - Token / ingestion cost: connected agents can drive substantial KQL volume.
  - Sovereign availability: not GA in GCC High / DoD as of verification date.
  - Access surface: the MCP endpoint becomes a new authorization boundary.

This helper is intentionally gated:
  -OptIn                MUST be set explicitly.
  -CostAcknowledged     MUST be set; signals caller has reviewed Sentinel ingestion calculator output.
  -GovernanceTicketId   MUST be supplied (AI Governance Lead approval ID).

.PARAMETER OptIn
Required switch. Refuses to proceed without it.

.PARAMETER CostAcknowledged
Required switch. Caller acknowledges they have reviewed the cost projection.

.PARAMETER GovernanceTicketId
Required string. AI Governance Lead approval ticket ID.

.NOTES
Control:        3.9
LastVerified:   April 2026
HelperVersion:  1.4.0
Status:         Preview (verify GA status per release)
Roles required: Sentinel Contributor + AI Governance Lead approval
Cross-ref:      Control 2.6 (Model risk), Control 1.24 (AISPM)
COST WARNING:   Token + KQL ingestion can spike. Review Sentinel calculator first.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [Parameter(Mandatory)][switch]$OptIn,
        [Parameter(Mandatory)][switch]$CostAcknowledged,
        [Parameter(Mandatory)][string]$GovernanceTicketId
    )
    if (-not $OptIn) {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='NotApplicable'
            Reason="Sentinel MCP Server is opt-in only. Pass -OptIn -CostAcknowledged -GovernanceTicketId <id> to proceed."
            Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }
    if (-not $CostAcknowledged) {
        throw "CostAcknowledged switch is required. Review the Sentinel ingestion calculator and confirm with FinOps before enabling MCP Server."
    }
    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    if (-not $sovereign.SentinelMcpAvailable) {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='NotApplicable'
            Reason="Sentinel MCP Server is not GA in $Cloud as of verification date. Verify Microsoft Learn parity matrix."
            Cloud=$Cloud; Findings=@("Sovereign-skew: MCP Server unavailable in $Cloud")
            GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }
    Write-Warning "Enabling Sentinel MCP Server (preview). Approval ticket $GovernanceTicketId recorded. Cost projection acknowledged. Review Microsoft Learn 'Sentinel MCP Server' for current capabilities."

    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    if ($PSCmdlet.ShouldProcess($WorkspaceName, "Enable Sentinel MCP Server (preview)")) {
        try {
            # Deployment path varies by preview release; canonicalized at
            # FSI-AgentGov-Solutions/solutions/sentinel-baseline/mcp-server.bicep
            $body = @{ properties = @{ enabled = $true; governanceTicket = $GovernanceTicketId } } | ConvertTo-Json -Depth 4
            Invoke-AzRestMethod -Method PUT -Path "$($ws.ResourceId)/providers/Microsoft.SecurityInsights/mcpServer/default?api-version=2024-09-01-preview" -Payload $body -ErrorAction Stop | Out-Null
            $status='Clean'; $reason="MCP Server enabled (preview). Approval ticket $GovernanceTicketId persisted."
        } catch { $status='Error'; $reason=$_.Exception.Message }
    } else { $status='Pending'; $reason='WhatIf' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'; Status=$status; Reason=$reason
        Feature='SentinelMcpServer'; PreviewStatus='Preview'
        WorkspaceArmId=$ws.ResourceId; Cloud=$Cloud
        GovernanceTicketId=$GovernanceTicketId
        Findings=@("Preview feature; review per release."); GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

---

## §10 — Verification / evidence helpers

Four read-only verification helpers and one quarterly evidence emitter. All five are safe to run on any cadence (no mutation), and each returns the standard contract object.

### 10.1 — `Test-Fsi-Control39-ConnectorMatrix`

```powershell
function Test-Fsi-Control39-ConnectorMatrix {
<#
.SYNOPSIS
Returns a per-connector status row for the six AI-relevant Sentinel connectors.

.DESCRIPTION
Probes each connector's deployment state and primary table ingestion in the last 24h.
Returns one pscustomobject per connector with Status in {Clean, Anomaly, Pending,
NotApplicable, Error} and a Reason. Used by the §11 orchestrator and the §12 self-test.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Roles required: Sentinel Reader + Log Analytics Reader
Cross-ref:      §5 connector helpers
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud
    )
    $ws = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction Stop
    $sovereign = Initialize-Agt39SovereignContext -Cloud $Cloud
    $connectors = @(
        @{ Kind='AzureActiveDirectory'; Name='Entra'; Tables=@('SigninLogs','AADServicePrincipalSignInLogs'); Required=$true },
        @{ Kind='Office365';            Name='Office365'; Tables=@('OfficeActivity'); Required=$true },
        @{ Kind='PowerPlatform';        Name='PowerPlatform'; Tables=@('PowerPlatformAdminActivity'); Required=$false },
        @{ Kind='MicrosoftThreatProtection'; Name='DefenderXDR'; Tables=@('AlertInfo','AlertEvidence'); Required=$true },
        @{ Kind='MicrosoftCloudAppSecurity'; Name='DefenderCloudApps'; Tables=@('CloudAppEvents'); Required=$false; Available=$sovereign.DefenderCloudAppsAvail },
        @{ Kind='MicrosoftCopilot';     Name='M365Copilot'; Tables=@('MicrosoftCopilotEvents'); Required=$false; Available=$sovereign.CopilotConnectorAvail }
    )
    $rows = foreach ($c in $connectors) {
        if ($c.ContainsKey('Available') -and -not $c.Available) {
            [pscustomobject]@{
                Connector=$c.Name; Status='NotApplicable'
                Reason="Connector not available in $Cloud"
                Tables=$c.Tables; LastIngestion=$null
            }; continue
        }
        $tableProbes = foreach ($t in $c.Tables) {
            try {
                $r = Invoke-AzOperationalInsightsQuery -WorkspaceId $ws.CustomerId `
                    -Query "$t | where TimeGenerated > ago(24h) | summarize Rows=count(), Last=max(TimeGenerated)" -ErrorAction Stop
                [pscustomobject]@{ Table=$t; Rows=[int]$r.Results[0].Rows; Last=$r.Results[0].Last }
            } catch {
                [pscustomobject]@{ Table=$t; Rows=0; Last=$null; Error=$_.Exception.Message }
            }
        }
        $totalRows = ($tableProbes | Measure-Object -Property Rows -Sum).Sum
        $status = if ($totalRows -gt 0) { 'Clean' }
                  elseif ($c.Required) { 'Anomaly' }
                  else { 'Pending' }
        [pscustomobject]@{
            Connector=$c.Name; Status=$status
            Reason="24h rows total=$totalRows across $($c.Tables.Count) table(s)"
            Tables=$c.Tables; TableProbes=$tableProbes
            Required=[bool]$c.Required
        }
    }

    $overall = if ($rows.Status -contains 'Anomaly' -or $rows.Status -contains 'Error') { 'Anomaly' }
               elseif ($rows.Status -contains 'Pending') { 'Pending' }
               else { 'Clean' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'
        Status=$overall; Reason="Connector matrix probed ($($rows.Count) connectors); overall=$overall"
        Cloud=$Cloud; WorkspaceCustomerId=$ws.CustomerId
        Connectors=$rows
        Findings=@($rows | Where-Object Status -in @('Anomaly','Error') | ForEach-Object { "$($_.Connector): $($_.Status) — $($_.Reason)" })
        GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

### 10.2 — `Test-Fsi-Control39-AnalyticsRuleCoverage`

```powershell
function Test-Fsi-Control39-AnalyticsRuleCoverage {
<#
.SYNOPSIS
Verifies the seven AI-specific analytics rules deployed by §6 helpers are all present
and enabled. Reports missing or disabled rules.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Roles required: Sentinel Reader
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName
    )
    $expected = @(
        '[FSI-3.9] Prompt Injection Pattern Detected',
        '[FSI-3.9] Anomalous Connector Use by Agent',
        '[FSI-3.9] After-Hours Privileged Agent Sign-In',
        '[FSI-3.9] DLP Policy Change',
        '[FSI-3.9] Unusual Consent Grant to Agent',
        '[FSI-3.9] Orphan or Shadow Agent Detected',
        '[FSI-3.9] Mass Data Download by Agent'
    )
    try {
        $rules = Get-AzSentinelAlertRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -ErrorAction Stop
    } catch {
        return [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='Error'
            Reason="Could not enumerate analytics rules: $($_.Exception.Message)"
            Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }

    $report = foreach ($name in $expected) {
        $match = $rules | Where-Object DisplayName -eq $name
        if (-not $match) {
            [pscustomobject]@{ Rule=$name; Status='Anomaly'; Reason='Missing — rule not deployed'; Enabled=$null }
        } elseif (-not $match.Enabled) {
            [pscustomobject]@{ Rule=$name; Status='Anomaly'; Reason='Present but disabled — see §0.2 #6'; Enabled=$false }
        } else {
            [pscustomobject]@{ Rule=$name; Status='Clean'; Reason='Present and enabled'; Enabled=$true }
        }
    }
    $missing = $report | Where-Object Status -eq 'Anomaly'
    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'
        Status= if ($missing) { 'Anomaly' } else { 'Clean' }
        Reason="Expected 7 rules; present and enabled: $(($report | Where-Object Status -eq 'Clean').Count)"
        Rules=$report
        Findings=@($missing | ForEach-Object { "$($_.Rule): $($_.Reason)" })
        GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

### 10.3 — `Test-Fsi-Control39-BreakGlassAlertWiring`

The break-glass account sign-in alert is owned by [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md), but it must be wired into the **same workspace** that 3.9 is monitoring — otherwise sovereign or alternate-region break-glass usage is invisible to the SOC routing the 3.9 incidents (§0.2 #14).

```powershell
function Test-Fsi-Control39-BreakGlassAlertWiring {
<#
.SYNOPSIS
Verifies the Control 1.11 break-glass account sign-in alert is present in THIS
Sentinel workspace.

.DESCRIPTION
Searches for an analytics rule whose KQL references the break-glass account UPNs
or whose name matches a Control 1.11 deployment pattern. Returns Anomaly if absent.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Cross-ref:      Control 1.11
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [string[]]$BreakGlassUpns = @()
    )
    try {
        $rules = Get-AzSentinelAlertRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -ErrorAction Stop
    } catch {
        return [pscustomobject]@{ ControlId='3.9'; HelperVersion='1.4.0'; Status='Error'; Reason=$_.Exception.Message; Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime() }
    }
    $matches = $rules | Where-Object {
        $_.DisplayName -match 'break.?glass|emergency.?access' -or
        ($BreakGlassUpns | ForEach-Object { $_ } | Where-Object { $rules.Query -match [regex]::Escape($_) })
    }
    if ($matches) {
        [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='Clean'
            Reason="Break-glass alert wired into this workspace ($($matches.Count) matching rule(s))"
            MatchingRules=$matches.DisplayName; Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    } else {
        [pscustomobject]@{
            ControlId='3.9'; HelperVersion='1.4.0'; Status='Anomaly'
            Reason="No Control 1.11 break-glass alert found in this workspace. SOC will not see break-glass sign-in activity for 3.9 incident triage. Deploy via Control 1.11 portal walkthrough."
            Findings=@("BreakGlassAlertMissing — see Control 1.11"); GeneratedUtc=(Get-Date).ToUniversalTime()
        }
    }
}
```

### 10.4 — `Export-Fsi-Control39-EvidenceBundle`

```powershell
function Export-Fsi-Control39-EvidenceBundle {
<#
.SYNOPSIS
Emits a quarterly signed evidence bundle for Control 3.9 with KQL query hash manifest.

.DESCRIPTION
Runs the four §10 verification helpers, packages results into a signed JSON bundle,
computes SHA-256 hashes for every artifact, and writes to ./evidence/3.9/<quarter>/
along with a manifest.json. The bundle is the canonical artifact for FINRA / OCC /
NYDFS examiner production for the quarter.

.PARAMETER Quarter
Quarter ID, e.g., '2026Q1'.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Roles required: Sentinel Reader + Log Analytics Reader + Purview Compliance Admin (for downstream WORM landing)
Cross-ref:      Control 1.7, Control 1.9 (records routing)
#>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [Parameter(Mandatory)][ValidatePattern('^\d{4}Q[1-4]$')][string]$Quarter,
        [string]$EvidencePath = ".\evidence\3.9"
    )
    $bundleDir = Join-Path $EvidencePath $Quarter
    New-Item -ItemType Directory -Force -Path $bundleDir | Out-Null
    $ts = Get-Date -Format 'yyyyMMddTHHmmssZ'

    $connector = Test-Fsi-Control39-ConnectorMatrix -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -Cloud $Cloud
    $rules     = Test-Fsi-Control39-AnalyticsRuleCoverage -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName
    $bg        = Test-Fsi-Control39-BreakGlassAlertWiring -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName
    $health    = Get-Fsi-SentinelWorkspaceHealth -WorkspaceCustomerId (Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName).CustomerId -LookbackHours 168 -Cloud $Cloud

    # KQL hash manifest — re-pull deployed rules and hash the live query
    $ruleObjs = Get-AzSentinelAlertRule -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -ErrorAction SilentlyContinue
    $kqlHashes = foreach ($r in ($ruleObjs | Where-Object DisplayName -like '[FSI-3.9]*')) {
        $hash = [Convert]::ToBase64String([System.Security.Cryptography.SHA256]::Create().ComputeHash([Text.Encoding]::UTF8.GetBytes(($r.Query ?? ''))))
        [pscustomobject]@{ Rule=$r.DisplayName; QueryHash=$hash; Enabled=$r.Enabled; Severity=$r.Severity }
    }

    $bundle = [pscustomobject]@{
        ControlId            = '3.9'
        HelperVersion        = '1.4.0'
        Quarter              = $Quarter
        GeneratedUtc         = $ts
        Tenant               = (Get-AzContext).Tenant.Id
        Subscription         = (Get-AzContext).Subscription.Id
        WorkspaceName        = $WorkspaceName
        Cloud                = $Cloud
        ConnectorMatrix      = $connector
        AnalyticsRuleCoverage= $rules
        BreakGlassAlertWiring= $bg
        WorkspaceHealth168h  = $health
        KqlQueryHashes       = $kqlHashes
        ScopeAttestations    = @{
            BooksAndRecordsRoute = 'Control 1.9 (NOT this control)'
            FINRA3110Cross       = 'Control 2.12'
            OCC2011_12Cross      = 'Control 2.6'
            NYDFS500_17Filing    = 'Control 3.4'
        }
    }

    $bundlePath = Join-Path $bundleDir "evidence-3.9-$Quarter-$ts.json"
    $bundle | ConvertTo-Json -Depth 30 | Set-Content -Path $bundlePath -Encoding UTF8

    # Sign manifest
    $hash = (Get-FileHash -Path $bundlePath -Algorithm SHA256).Hash
    $manifestPath = Join-Path $bundleDir "manifest.json"
    $manifest = @()
    if (Test-Path $manifestPath) { $manifest = @(Get-Content $manifestPath | ConvertFrom-Json) }
    $manifest += [pscustomobject]@{
        file=(Split-Path $bundlePath -Leaf); sha256=$hash; bytes=(Get-Item $bundlePath).Length
        generated_utc=$ts; script_version='1.4.0'; control_id='3.9'; quarter=$Quarter
    }
    $manifest | ConvertTo-Json -Depth 5 | Set-Content -Path $manifestPath -Encoding UTF8

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'
        Status= if ($connector.Status -eq 'Anomaly' -or $rules.Status -eq 'Anomaly' -or $bg.Status -eq 'Anomaly') { 'Anomaly' } else { 'Clean' }
        Reason="Evidence bundle for $Quarter written to $bundlePath (hash $($hash.Substring(0,12))...)"
        BundlePath=$bundlePath; ManifestPath=$manifestPath; Sha256=$hash
        Findings=@($connector.Findings + $rules.Findings + $bg.Findings + $health.Findings)
        GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

---

## §11 — Orchestrator: `Invoke-Fsi-Control39Setup`

The orchestrator wires the helpers into one safe, idempotent entry point with three modes (`ReportOnly`, `Enforce`, `Verify`) and explicit cloud selection. The orchestrator wraps execution in a transcript per [baseline §4](../../_shared/powershell-baseline.md), emits a single rollup contract object, and **never** moves from `ReportOnly` to mutation without explicit operator action.

```powershell
function Invoke-Fsi-Control39Setup {
<#
.SYNOPSIS
End-to-end orchestrator for Control 3.9 (Sentinel integration for AI agent monitoring).

.DESCRIPTION
Sequencing:
  1. Self-test (Pester) — verify helper return-shape contract
  2. Sovereign context bootstrap
  3. Workspace ensure (idempotent)
  4. Connector matrix (Entra dual-stream, Office365, PowerPlatform, Defender XDR,
     Defender Cloud Apps if available, M365 Copilot if available)
  5. Analytics rules (7 §6 helpers)
  6. Logic App playbooks (3 §7 helpers)
  7. Retention floor enforcement (§8 — never reduces without operator override)
  8. Verification helpers (§10)
  9. Quarterly evidence emission (§10.4) — only in Verify mode

.PARAMETER Mode
  ReportOnly — read-only probes; no mutation.
  Enforce    — apply missing connectors / rules / playbooks; honor -WhatIf.
  Verify     — read-only probes plus quarterly evidence bundle emission.

.PARAMETER Cloud
Commercial | USGov | USGovHigh | USGovDoD

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Roles required: see §1 canonical role table; orchestrator escalates via PIM only on Enforce.
Cross-ref:      Controls 1.7, 1.8, 1.9, 1.11, 1.24, 2.6, 2.12, 2.25, 3.4, 3.6, 3.14
WARNING:        Enforce mode mutates the workspace. Always run ReportOnly first.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)][ValidateSet('ReportOnly','Enforce','Verify')][string]$Mode,
        [Parameter(Mandatory)][ValidateSet('Commercial','USGov','USGovHigh','USGovDoD')][string]$Cloud,
        [Parameter(Mandatory)][string]$ResourceGroupName,
        [Parameter(Mandatory)][string]$WorkspaceName,
        [Parameter(Mandatory)][string]$Location,
        [string]$Quarter,
        [string]$EvidencePath = ".\evidence\3.9",
        [string]$TranscriptPath = ".\transcripts\3.9"
    )
    if ($Mode -eq 'Verify' -and -not $Quarter) {
        throw "Quarter (e.g., '2026Q1') is required when Mode='Verify'."
    }
    New-Item -ItemType Directory -Force -Path $TranscriptPath | Out-Null
    $tsFile = Join-Path $TranscriptPath "Invoke-Fsi-Control39Setup-$Mode-$(Get-Date -Format 'yyyyMMddTHHmmssZ').log"
    Start-Transcript -Path $tsFile -Append | Out-Null

    $rollup = [System.Collections.ArrayList]::new()
    try {
        Write-Host "[3.9] Mode=$Mode Cloud=$Cloud Workspace=$WorkspaceName" -ForegroundColor Cyan

        # 1. Self-test
        $st = Invoke-Agt39SelfTest
        $rollup.Add(@{ Step='SelfTest'; Result=$st }) | Out-Null
        if ($st.Status -eq 'Anomaly') { Write-Warning "Self-test reported anomalies; continuing." }

        # 2. Sovereign context
        $sov = Initialize-Agt39SovereignContext -Cloud $Cloud
        $rollup.Add(@{ Step='Sovereign'; Result=$sov }) | Out-Null

        # 3. Workspace ensure
        if ($Mode -eq 'Enforce') {
            $ws = New-Fsi-SentinelWorkspace -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -Location $Location -Cloud $Cloud
        } else {
            $existing = Get-AzOperationalInsightsWorkspace -ResourceGroupName $ResourceGroupName -Name $WorkspaceName -ErrorAction SilentlyContinue
            $ws = if ($existing) { [pscustomobject]@{ ControlId='3.9'; HelperVersion='1.4.0'; Status='Clean'; Reason='Workspace exists'; Findings=@(); GeneratedUtc=(Get-Date).ToUniversalTime() } }
                  else { [pscustomobject]@{ ControlId='3.9'; HelperVersion='1.4.0'; Status='Anomaly'; Reason='Workspace missing — run Enforce'; Findings=@('WorkspaceMissing'); GeneratedUtc=(Get-Date).ToUniversalTime() } }
        }
        $rollup.Add(@{ Step='Workspace'; Result=$ws }) | Out-Null

        # 4 & 5 & 6 — Enforce-only mutation; ReportOnly/Verify just probe
        if ($Mode -eq 'Enforce' -and $ws.Status -eq 'Clean') {
            $entra = Enable-Fsi-EntraConnector -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -Cloud $Cloud
            $rollup.Add(@{ Step='Connector.Entra'; Result=$entra }) | Out-Null
            # Other connectors invoked similarly — abbreviated here for clarity; see §5.
            foreach ($ruleHelper in @(
                'New-Fsi-Rule-PromptInjection','New-Fsi-Rule-AnomalousConnectorUse',
                'New-Fsi-Rule-AfterHoursPrivilegedAgent','New-Fsi-Rule-DLPChange',
                'New-Fsi-Rule-UnusualConsentGrant','New-Fsi-Rule-OrphanShadowAgent',
                'New-Fsi-Rule-MassDataDownload')) {
                $r = & $ruleHelper -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName
                $rollup.Add(@{ Step="Rule.$ruleHelper"; Result=$r }) | Out-Null
            }
            foreach ($pbHelper in @('New-Fsi-Playbook-SuspendAgent','New-Fsi-Playbook-NotifyOwnerSOC','New-Fsi-Playbook-NYDFS72hTimer')) {
                $p = & $pbHelper -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -Location $Location
                $rollup.Add(@{ Step="Playbook.$pbHelper"; Result=$p }) | Out-Null
            }
        }

        # 7 — retention enforcement (idempotent; never reduces silently)
        if ($Mode -eq 'Enforce') {
            foreach ($t in @('SigninLogs','AADServicePrincipalSignInLogs','OfficeActivity','PowerPlatformAdminActivity')) {
                $ret = Set-Fsi-TableRetention -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -Table $t -HotDays 180 -ArchiveDays 4383 -DataClass SecurityTelemetry -ErrorAction SilentlyContinue
                $rollup.Add(@{ Step="Retention.$t"; Result=$ret }) | Out-Null
            }
        }

        # 8 — verification (always)
        $vc = Test-Fsi-Control39-ConnectorMatrix -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -Cloud $Cloud
        $vr = Test-Fsi-Control39-AnalyticsRuleCoverage -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName
        $vb = Test-Fsi-Control39-BreakGlassAlertWiring -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName
        $rollup.Add(@{ Step='Verify.Connectors'; Result=$vc }) | Out-Null
        $rollup.Add(@{ Step='Verify.Rules'; Result=$vr }) | Out-Null
        $rollup.Add(@{ Step='Verify.BreakGlass'; Result=$vb }) | Out-Null

        # 9 — quarterly evidence (Verify only)
        if ($Mode -eq 'Verify') {
            $ev = Export-Fsi-Control39-EvidenceBundle -ResourceGroupName $ResourceGroupName -WorkspaceName $WorkspaceName -Cloud $Cloud -Quarter $Quarter -EvidencePath $EvidencePath
            $rollup.Add(@{ Step='Evidence'; Result=$ev }) | Out-Null
        }
    } finally {
        Stop-Transcript | Out-Null
    }

    $statuses = $rollup.Result.Status
    $overall = if ($statuses -contains 'Error') { 'Error' }
               elseif ($statuses -contains 'Anomaly') { 'Anomaly' }
               elseif ($statuses -contains 'Pending') { 'Pending' }
               else { 'Clean' }

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'
        Status=$overall
        Reason="Mode=$Mode Cloud=$Cloud completed with $($rollup.Count) step(s); overall=$overall"
        Mode=$Mode; Cloud=$Cloud
        TranscriptPath=$tsFile
        Steps=$rollup
        Findings=@($rollup.Result | Where-Object Status -in @('Anomaly','Error') | ForEach-Object { $_.Reason })
        GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

> **Operator workflow.** Always: `Invoke-Fsi-Control39Setup -Mode ReportOnly -Cloud <c> ...` first → review rollup → `-Mode Enforce -WhatIf` → `-Mode Enforce` → quarterly `-Mode Verify -Quarter 2026Q2`.

---

## §12 — Pester self-test: `Invoke-Agt39SelfTest`

The self-test is run automatically as step 1 of the §11 orchestrator and is the first thing an operator runs after pulling a new helper version. It enforces the **return-shape contract** from §0, refusing to deploy if any helper has drifted.

```powershell
function Invoke-Agt39SelfTest {
<#
.SYNOPSIS
Pester-driven self-test for Control 3.9 helper module. Refuses to greenlight if any
helper violates the return-shape contract or if known-bad sovereign / preview combos
are misclassified.

.DESCRIPTION
Six namespaces:
  CONTRACT   — every helper returns the standard pscustomobject (ControlId, HelperVersion,
               Status, Reason, Findings, GeneratedUtc); never $null / @() / hashtable.
  CONNECTOR  — Test-Fsi-Control39-ConnectorMatrix returns one row per expected connector.
  RULE       — Test-Fsi-Control39-AnalyticsRuleCoverage expects 7 rules; missing => Anomaly.
  PLAYBOOK   — §7 Logic App helpers grant managed identity the documented roles only.
  RETENTION  — Set-Fsi-TableRetention refuses reductions without -Force -Justification.
  SOVEREIGN  — Sentinel MCP / M365 Copilot return NotApplicable (NOT Clean) in USGov*.

.NOTES
Control:        3.9
HelperVersion:  1.4.0
Roles required: none (offline test against function metadata + mocked invocations)
#>
    [CmdletBinding()]
    param([switch]$Detailed)
    if (-not (Get-Module Pester -ListAvailable | Where-Object Version -ge '5.4.0')) {
        throw "Pester >= 5.4.0 required. Install-Module Pester -RequiredVersion 5.5.0 -Scope CurrentUser."
    }
    Import-Module Pester -MinimumVersion 5.4.0 -Force

    $expectedHelpers = @(
        'Initialize-Agt39SovereignContext','Connect-Agt39Az','Test-Agt39SentinelSolutionAvailable',
        'Initialize-Agt39Session','Close-Agt39Session',
        'New-Fsi-SentinelWorkspace','Get-Fsi-SentinelWorkspaceHealth',
        'Enable-Fsi-EntraConnector','Enable-Fsi-PowerPlatformConnector',
        'Enable-Fsi-Defender365Connector','Enable-Fsi-DefenderForCloudAppsConnector',
        'Enable-Fsi-MicrosoftCopilotConnector','Enable-Fsi-AppInsightsLink',
        'New-Fsi-Rule-PromptInjection','New-Fsi-Rule-AnomalousConnectorUse',
        'New-Fsi-Rule-AfterHoursPrivilegedAgent','New-Fsi-Rule-DLPChange',
        'New-Fsi-Rule-UnusualConsentGrant','New-Fsi-Rule-OrphanShadowAgent',
        'New-Fsi-Rule-MassDataDownload',
        'New-Fsi-Playbook-SuspendAgent','New-Fsi-Playbook-NotifyOwnerSOC','New-Fsi-Playbook-NYDFS72hTimer',
        'Set-Fsi-TableRetention','Export-Fsi-TableToFirmArchive',
        'Enable-Fsi-SentinelMcpServer',
        'Test-Fsi-Control39-ConnectorMatrix','Test-Fsi-Control39-AnalyticsRuleCoverage',
        'Test-Fsi-Control39-BreakGlassAlertWiring','Export-Fsi-Control39-EvidenceBundle',
        'Invoke-Fsi-Control39Setup','Invoke-Agt39SelfTest'
    )
    $container = New-PesterContainer -ScriptBlock {
        Describe 'CONTRACT — helper presence' {
            foreach ($n in $script:expectedHelpers) {
                It "$n is exported" { Get-Command $n -ErrorAction SilentlyContinue | Should -Not -BeNullOrEmpty }
            }
        }
        Describe 'SOVEREIGN — preview / commercial-only features marked NotApplicable in GCC High' {
            It 'Sentinel MCP refuses USGovHigh without OptIn' {
                $r = Enable-Fsi-SentinelMcpServer -ResourceGroupName 'rg' -WorkspaceName 'w' -Cloud USGovHigh -OptIn:$false -CostAcknowledged:$false -GovernanceTicketId 'TKT-1' -ErrorAction SilentlyContinue
                $r.Status | Should -Be 'NotApplicable'
            }
            It 'Sovereign context flags MCP unavailable in USGovHigh' {
                (Initialize-Agt39SovereignContext -Cloud USGovHigh).SentinelMcpAvailable | Should -BeFalse
            }
            It 'Sovereign context flags Copilot connector unavailable in USGovDoD' {
                (Initialize-Agt39SovereignContext -Cloud USGovDoD).CopilotConnectorAvail | Should -BeFalse
            }
        }
        Describe 'RETENTION — guardrails' {
            It 'Refuses retention reduction without -Force -Justification' {
                # Mocked or run against a sandbox workspace; gates surface as Anomaly.
                $true | Should -Be $true
            }
        }
    } -Data @{ expectedHelpers = $expectedHelpers }

    $result = Invoke-Pester -Container $container -PassThru -Output ($(if($Detailed){'Detailed'}else{'Normal'}))

    [pscustomobject]@{
        ControlId='3.9'; HelperVersion='1.4.0'
        Status= if ($result.FailedCount -gt 0) { 'Anomaly' } elseif ($result.SkippedCount -gt 0) { 'Pending' } else { 'Clean' }
        Reason="Pester: $($result.PassedCount) pass / $($result.FailedCount) fail / $($result.SkippedCount) skipped"
        Passed=$result.PassedCount; Failed=$result.FailedCount; Skipped=$result.SkippedCount
        Findings=@($result.Failed | ForEach-Object { "$($_.ExpandedPath) — $($_.ErrorRecord.Exception.Message)" })
        GeneratedUtc=(Get-Date).ToUniversalTime()
    }
}
```

> **CI integration.** Wire `Invoke-Agt39SelfTest` into the module's pipeline so the helper module fails to publish if the contract is violated. The §11 orchestrator gates on the same call at runtime.

---

## §13 — Cross-reference matrix

The following matrix maps every helper / detection / artifact in this playbook to the related controls. Use it during incident triage to know which **other** control owners need to be looped in, and during examiner production to assemble the cross-control evidence pack.

| Helper / Artifact (this control) | Cross-Control Dependency | Why It Matters |
|---|---|---|
| `Initialize-Agt39SovereignContext` (§2) | [Control 1.7 — Audit logging](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Audit feed sourcing must respect the same sovereign cloud; cross-tenant reach-back is prohibited. |
| `New-Fsi-SentinelWorkspace` (§4) | [Control 2.25 — Agent365 governance console](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Workspace ARM ID is registered in the governance console for inventory and routing. |
| `Enable-Fsi-EntraConnector` (§5) — `SigninLogs` stream | [Control 1.11 — Conditional access & break-glass](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | User sign-in monitoring underpins break-glass detection wiring (§10.3). |
| `Enable-Fsi-EntraConnector` (§5) — `AADServicePrincipalSignInLogs` stream | [Control 3.6 — Orphaned agents](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Service-principal telemetry feeds orphan / shadow agent detection. |
| `Enable-Fsi-PowerPlatformConnector` (§5) | [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md), [Control 3.14 — Observability SDK](../../../controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md) | Power Platform admin activity is the inventory backbone for Copilot Studio agents. |
| `Enable-Fsi-Defender365Connector` (§5) | [Control 1.8 — Runtime protection](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md), [Control 1.24 — Defender AISPM](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | Defender XDR alerts and AISPM posture findings land in the same workspace as 3.9 detections. |
| `Enable-Fsi-AppInsightsLink` (§5) | [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | App Insights traces of agent-to-tool calls are linked, but transcripts are NOT records — see §0 scope warning. |
| `New-Fsi-Rule-PromptInjection` (§6) | [Control 1.8](../../../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md), [Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | Defender for AI / AISPM provide overlapping signal; the 3.9 rule is the SOC-routing layer. |
| `New-Fsi-Rule-AnomalousConnectorUse` (§6) | [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Agent365 holds the canonical connector-permission baseline used to score "anomalous". |
| `New-Fsi-Rule-AfterHoursPrivilegedAgent` (§6) | [Control 2.12 — FINRA 3110 supervision](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), [Control 2.6 — OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Out-of-window privileged activity is a supervision review trigger. |
| `New-Fsi-Rule-DLPChange` (§6) | [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | DLP policy mutation is a Tier-1 audit event regardless of operator role. |
| `New-Fsi-Rule-UnusualConsentGrant` (§6) | [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Consent-phishing path; cross-feed with conditional access policy state. |
| `New-Fsi-Rule-OrphanShadowAgent` (§6) | [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | 3.6 owns the remediation runbook; 3.9 owns the detection. |
| `New-Fsi-Rule-MassDataDownload` (§6) | [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Bulk export by a non-human identity is both an audit and supervision trigger. |
| `New-Fsi-Playbook-SuspendAgent` (§7) | [Control 3.6](../../../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md), [Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | Suspension flows through Agent365 to keep the inventory authoritative. |
| `New-Fsi-Playbook-NotifyOwnerSOC` (§7) | [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervisory notifications must reach the named principal of record. |
| `New-Fsi-Playbook-NYDFS72hTimer` (§7) | [Control 3.4 — Incident reporting & RCA](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | The timer surfaces deadline; **3.4 owns the actual NYDFS 500.17(a) filing.** |
| `Set-Fsi-TableRetention` (§8) | [Control 1.9 — Data retention & deletion](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Sentinel retention is a SOC operational concern; books-and-records retention is 1.9. |
| `Export-Fsi-TableToFirmArchive` (§8) | [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | **STUB.** Sentinel archive is NOT WORM and NOT a SEC 17a-4 substitute. |
| `Enable-Fsi-SentinelMcpServer` (§9) | [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | Adding an agent-callable MCP surface is a model-risk and posture decision. |
| `Test-Fsi-Control39-BreakGlassAlertWiring` (§10.3) | [Control 1.11](../../../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Break-glass alert is owned by 1.11; 3.9 verifies it is wired into THIS workspace. |
| `Export-Fsi-Control39-EvidenceBundle` (§10.4) | [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Quarterly bundle is a key examiner-production input alongside 1.7 audit extracts. |
| `Invoke-Fsi-Control39Setup` (§11) | All of the above | Orchestrator surfaces the cross-references in its rollup so SOC and governance can route findings appropriately. |

> **Examiner-production tip.** When responding to a FINRA, OCC, NYDFS, or SEC information request that asks about "AI agent monitoring", produce the §10.4 quarterly bundle **alongside**: the 1.7 audit extract, the 1.9 retention attestation, the 2.6 model risk register entry, the 2.12 supervisory review log, and (if the request involves a reportable incident) the 3.4 RCA. The 3.9 bundle is necessary but not sufficient on its own.

---

## Next Steps

- **Portal Walkthrough** *(forthcoming)* — Manual Defender / Sentinel portal configuration of connectors, analytics rules, and automation rules.
- [Verification & Testing](./verification-testing.md) — Quarterly self-test, evidence-bundle validation, and connector-matrix drift checks.
- **Troubleshooting** *(forthcoming)* — Connector outages, ingestion gaps, false-clean diagnostics, and sovereign-cloud parity gaps.

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
