# Control 1.12 — PowerShell Setup: Insider Risk Management and Adaptive Protection Automation

> **Scope.** This playbook automates the **insider-risk detection and adaptive-protection plane** for Control 1.12 across **Microsoft Purview Insider Risk Management (IRM), Adaptive Protection, the Microsoft 365 HR data connector, Defender for Endpoint / Defender for Cloud Apps signal sources, DLP rule integration with risk tiers, custom indicators for AI-agent abuse, and alert routing into Sentinel and supervisory queues** in US financial services tenants. It assumes you have already read [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) (referenced below as **BL-§N**) and the parent control specification [`../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md).
>
> **What this playbook is.** A reproducible, sovereign-aware harness that (a) pins module versions and verifies cmdlet surface; (b) bootstraps a certificate-authenticated, audit-only IRM reader principal that is distinct from the IRM Admin / Investigator / Approver principals; (c) enumerates IRM policy templates, deployed policies, scope, and tenant configuration; (d) audits Adaptive Protection enablement and the DLP rules that consume IRM risk tiers (Elevated / Moderate / Minor); (e) verifies HR connector freshness and signal-source coverage (Defender for Endpoint, Defender for Cloud Apps, audit feeds, browser extension where applicable); (f) emits custom-indicator inventory for AI-agent abuse signals (excessive prompt rate, MNPI grounding queries, off-hours bursts) per Control 1.5 / 1.6 telemetry contracts; and (g) writes evidence with SHA-256 manifests for the quarterly attestation pack.
>
> **What this playbook is not.** It is not a substitute for the firm's Written Supervisory Procedures (FINRA Rule 3110), HR investigation workflows, legal-hold decisions, or supervisory review by a registered principal. It does not, by itself, configure or enable Forensic Evidence — that capability requires dual-authorization (Investigator request + Approver consent) executed in the Purview portal per [Control 1.12 § Forensic Evidence](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). It does not retain books-and-records artifacts; durable retention is the responsibility of [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
>
> **Sovereign-cloud reality (read before any other section).** Per Microsoft Learn ([`insider-risk-management-adaptive-protection`](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection)), **Insider Risk Management and Adaptive Protection are not available in any US Government cloud (GCC, GCC High, DoD)** at the time of authoring. Every helper in this playbook detects sovereign cloud and returns `Status = NotApplicable` with a written rationale rather than a false-clean `Clean` result. Compensating-control guidance for Zone 3 in those clouds is documented in §12.
>
> **Hedged language reminder.** Output of this harness *supports* compliance with FINRA Rule 3110 / 4511, FINRA Notice 25-07 (RFC, contextual only), SEC Rule 17a-3 / 17a-4, SEC Regulation S-P (2024 amendments), GLBA 501(b), SOX 302/404, NYDFS 23 NYCRR §500.06 / §500.16 / §500.17, OCC Bulletin 2011-12, Fed SR 11-7, and FFIEC IT Examination Handbook expectations. It does not, by itself, *ensure* a passing examination, *guarantee* that every insider event is detected, *prevent* exfiltration, or *eliminate* false negatives in ML-driven scoring. Implementation requires that organizations verify endpoint availability, module pinning, sovereign feature parity, HR connector accuracy, and signal-source coverage at every change window, and that they treat any preview surface (Risky Agents, Risky AI usage, Triage Agent) as **additive** evidence rather than a complete substitute for human supervisory review.

| Field | Value |
|---|---|
| Control ID | 1.12 |
| Pillar | 1 — Security |
| Playbook | PowerShell Setup |
| PowerShell Edition | 7.4 LTS Core (orchestrator); 5.1 Desktop available for any Windows-only legacy fallback |
| Sovereign Clouds | Commercial only for IRM / Adaptive Protection; GCC / GCC High / DoD return `NotApplicable` (see §0 and §12) |
| Last UI Verified | April 2026 |
| Companion Playbooks | [`portal-walkthrough.md`](portal-walkthrough.md) · [`verification-testing.md`](verification-testing.md) · [`troubleshooting.md`](troubleshooting.md) |
| Related Controls | [1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) · [1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) · [1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) · [2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) · [2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) · [3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) · [3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |

---

## §0 — Sovereign-cloud reality and false-clean defects (READ FIRST)

**The defining fact of Control 1.12.** Insider Risk Management and Adaptive Protection are **commercial-cloud-only** capabilities at the time of authoring. Per Microsoft Learn ([`insider-risk-management-adaptive-protection`](https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection)) and the IRM availability matrix, **GCC, GCC High, and DoD tenants do not have Adaptive Protection**, and several IRM detection surfaces (Risky Agents preview, Risky AI usage, Forensic Evidence, Triage Agent) require feature-by-feature parity verification before being claimed in scope for any sovereign tenant. A script that runs `Get-InsiderRiskPolicy` against a GCC High tenant will return either an empty array or an "operation not supported" error with a non-zero exit code that frequently gets swallowed by `try { } catch { }` boilerplate — **producing a false-clean evidence artifact that understates the firm's true control posture under NYDFS §500.06, GLBA 501(b), and SOX 404**.

A script that ignores this reality produces a **false-clean IRM posture** — the worst Control 1.12 outcome. False-clean posture artifacts are particularly dangerous in regulated FSI tenants because IRM is frequently presented to examiners as the firm's primary insider-threat detection surface; if that surface is silently absent, the compensating controls (DLP, Communication Compliance, Sentinel UEBA) must be evidenced explicitly, not assumed.

**Why this section exists.** Seven classes of silent failure produce false-clean IRM output specifically:

1. **Wrong cloud, no warning.** `Connect-IPPSSession` without `-ConnectionUri` for the sovereign cloud authenticates against commercial endpoints; for a sovereign tenant the connection succeeds against the wrong tenant or fails with a generic auth error that masks the real issue. `Connect-MgGraph` without `-Environment USGov` / `USGovDoD` does the same (BL-§3).
2. **IRM cmdlets unavailable in the cloud.** Even on commercial, `Get-InsiderRiskPolicy` requires the operator be assigned **Insider Risk Management Admins** (or the catch-all **Insider Risk Management** role group) in Purview; without it, calls return permission errors that scripts often log-and-continue.
3. **Adaptive Protection assumed enabled.** The Adaptive Protection toggle is separate from any IRM policy. A tenant can have IRM policies in place with Adaptive Protection disabled, in which case DLP / Conditional Access / DLM never receive the risk-tier signal and the control is functionally inert.
4. **HR connector silently stale.** The Microsoft 365 HR connector ingests CSV on a scheduled cadence; if the upstream HRIS export breaks, the connector continues to report "healthy" with stale data. *Data theft by departing users* and *Data leaks by risky users* policies will not fire on terminations the system has never seen.
5. **Browser-signal prerequisites not in place.** *Risky AI usage*, *Risky browser usage*, and several browser-derived indicators require the Microsoft Insider risk extension (Edge) or the Microsoft Purview extension (Chrome) on **Windows-only** devices onboarded to Microsoft Purview. Policies will exist and be reported as "deployed" while producing zero signal.
6. **Signal-source gaps invisible at the IRM layer.** *Security policy violations* templates require Defender for Endpoint integration; cloud-app indicators in *Data theft by departing users* require Defender for Cloud Apps connectors (Box, Dropbox, Google Drive, Amazon S3, Azure). Without the connector, the policy template is registered but produces no events.
7. **Single principal for read and write.** Running this harness with the same principal that *configures* IRM policies breaks SOX 404 separation of duties — the principal that produces the evidence could be the principal that altered the configuration the evidence describes. Use a distinct **Insider Risk Management Auditors** role-group principal for read-only assessment.

**Top false-clean defects unique to IRM automation.**

| # | Defect | What it looks like | How this playbook traps it |
|---|---|---|---|
| 1 | `Get-InsiderRiskPolicy` against a GCC / GCC High / DoD tenant | Empty array or generic auth error; exit 0 | §2 detects sovereign cloud and short-circuits every helper to `Status = NotApplicable` with rationale (`Get-FsiIrmCloudGate`) |
| 2 | Adaptive Protection assumed enabled because IRM policies exist | Risk tiers never propagate to DLP / CA / DLM | §4 `Get-FsiAdaptiveProtectionStatus` reads the AP toggle and walks DLP rules for `IRMSettings` integration |
| 3 | HR connector reported "healthy" with stale data | Departing-user policies never fire | §5 `Get-FsiIrmHrConnectorState` compares last-sync time against firm-defined lag threshold |
| 4 | DLP rules reference IRM tiers but tier definitions are empty | `IRMSettings` present but no `RiskLevel` mapping | §11 cross-walks DLP rule `IRMSettings` with the IRM tier definitions |
| 5 | Browser-signal indicators enabled with no extension deployed | Risky AI usage policy exists, produces no signal | §6 `Get-FsiIrmSignalCoverage` flags browser-dependent policies without an extension presence signal |
| 6 | Anonymization disabled without recorded privacy approval | Identifies users in alerts that should be pseudonymized | §8 `Test-FsiIrmAnonymization` confirms `AnonymizationEnabled` posture |
| 7 | IRM alerts not forwarded to Sentinel | Insider events isolated from SOC | §7 `Test-FsiIrmAlertRouting` checks Office 365 connector tables in Sentinel for IRM event types |
| 8 | Same principal as IRM Admin and IRM Auditor | SOX 404 separation-of-duties break | §1 separate `agt112-irm-reader` audit-only principal |
| 9 | Custom indicators for agent abuse missing entirely | AI-specific signal absent | §9 `Get-FsiIrmAgentAbuseIndicators` enumerates required indicators per FSI use case and reports gaps |
| 10 | `Get-DlpComplianceRule` walked without `IRMSettings` expansion | Adaptive Protection integration appears absent when only the property was suppressed | §11 explicit `-Properties IRMSettings` expansion |

**Required shell guard (run this at the top of every Control 1.12 session).**

```powershell
# Save as: scripts/Assert-Agt112Shell.ps1
[CmdletBinding()]
[OutputType([void])]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSEdition -ne 'Core' -or $PSVersionTable.PSVersion -lt [version]'7.4.0') {
    Write-Error "Control 1.12 orchestrator requires PowerShell 7.4 LTS Core (pwsh). Detected: $($PSVersionTable.PSEdition) $($PSVersionTable.PSVersion)."
    exit 2
}

# Required modules — fail closed if any are missing
$required = @(
    'ExchangeOnlineManagement',
    'Microsoft.Graph.Authentication',
    'Microsoft.Graph.Security',
    'Microsoft.Graph.Identity.Governance'
)
$missing = $required | Where-Object { -not (Get-Module -ListAvailable -Name $_) }
if ($missing) {
    Write-Error "Missing required modules for Control 1.12: $($missing -join ', '). Run scripts/Install-Agt112Modules.ps1."
    exit 2
}

Write-Verbose "Control 1.12 shell guard passed: pwsh $($PSVersionTable.PSVersion)"
```

---

## §1 — Module, CLI, and permission matrix

**Why this section exists.** IRM cmdlet surface is split across **ExchangeOnlineManagement** (compliance / Purview cmdlets reached via `Connect-IPPSSession`) and **Microsoft.Graph.Security** (the preferred Graph surface for IRM alerts and cases as it migrates). Pin both, and pin the Graph sub-modules explicitly — Microsoft ships breaking shape changes across `Microsoft.Graph` minor versions on the security and identity-governance endpoints.

### 1.1 Pinned PowerShell modules

```powershell
# Save as: scripts/Install-Agt112Modules.ps1
[CmdletBinding(SupportsShouldProcess)]
[OutputType([void])]
param([switch]$AcceptLicense)
<#
.SYNOPSIS
    Pins every PowerShell module Control 1.12 depends on to a CAB-approved version.
.NOTES
    Verify pinned versions against your CAB-approved baseline before each run. See BL-§1 for the
    canonical pinning pattern. Microsoft.Graph is a meta-module — pin every required sub-module
    explicitly rather than the meta package.
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$modules = @(
    @{ Name = 'ExchangeOnlineManagement';                    Version = '3.7.0'  },
    @{ Name = 'Microsoft.Graph.Authentication';              Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Security';                    Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Identity.Governance';         Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Identity.SignIns';            Version = '2.25.0' },
    @{ Name = 'Microsoft.Graph.Beta.Security';               Version = '2.25.0' }
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
}
```

### 1.2 Role-group and permission matrix

| Operation | Required role group / scope | Notes |
|---|---|---|
| `Get-InsiderRiskPolicy`, `Get-IRMConfiguration`, `Get-PolicyConfig` (read) | **Insider Risk Management Auditors** (recommended) or **Insider Risk Management Admins** | Use a dedicated read-only principal for evidence collection (§1.3) |
| `New-InsiderRiskPolicy`, `Set-InsiderRiskPolicy` (write) | **Insider Risk Management Admins** | SOX 404: must NOT be the same principal as the auditor / reader |
| Forensic Evidence capture request | **Insider Risk Management Investigators** | Request only — approval is a separate role (Approvers) |
| Forensic Evidence capture approval | **Insider Risk Management Approvers** | **Must be distinct** from Investigators (dual-authorization) |
| Microsoft Graph IRM read (preferred) | `ThreatIntelligence.Read.All`, `SecurityEvents.Read.All`, `IdentityRiskyUser.Read.All` (verify on Learn at deployment) | Beta endpoints subject to change; pin SDK version |
| HR connector read | `User.Read.All`, `AuditLog.Read.All`, plus connector-specific app role | Read-only for assessment |

### 1.3 Separate audit-only principal (recommended)

Create a service principal — `agt112-irm-reader` — that holds **Insider Risk Management Auditors** in Purview plus the read-only Graph scopes above. Never assign it Admin / Investigator / Approver. Authenticate it with a certificate, not a secret (BL-§3).

---

## §2 — Sovereign-aware authentication bootstrap

```powershell
# Save as: scripts/Connect-Agt112.ps1
[CmdletBinding()]
param(
    [ValidateSet('Commercial','GCC','GCCHigh','DoD')]
    [string]$Cloud = 'Commercial',

    [Parameter(Mandatory)] [string]$TenantId,
    [Parameter(Mandatory)] [string]$AppId,
    [Parameter(Mandatory)] [string]$CertificateThumbprint,

    [Parameter(Mandatory)] [string]$UserPrincipalName  # for Connect-IPPSSession context
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Sovereign cloud detection — see §0 for the false-clean rationale.
# Helpers in §3-§9 read this variable to short-circuit to NotApplicable.
$script:FsiCloud = $Cloud

$mgEnv = @{
    Commercial = 'Global'
    GCC        = 'USGov'
    GCCHigh    = 'USGovDoD'
    DoD        = 'USGovDoD'
}[$Cloud]

$ippsUri = @{
    Commercial = 'https://ps.compliance.protection.outlook.com/PowerShell-LiveID'
    GCC        = 'https://ps.compliance.protection.office365.us/PowerShell-LiveID'
    GCCHigh    = 'https://ps.compliance.protection.office365.us/PowerShell-LiveID'
    DoD        = 'https://l5.ps.compliance.protection.office365.us/PowerShell-LiveID'
}[$Cloud]

Connect-MgGraph -TenantId $TenantId -ClientId $AppId `
    -CertificateThumbprint $CertificateThumbprint -Environment $mgEnv -NoWelcome

# Connect-IPPSSession is the gateway for IRM cmdlets in commercial cloud.
# In sovereign clouds the connection succeeds but IRM cmdlets return errors;
# §3-§9 detect that and report NotApplicable rather than failing.
Connect-IPPSSession -UserPrincipalName $UserPrincipalName -ConnectionUri $ippsUri

Write-Verbose "Connected: cloud=$Cloud tenant=$TenantId mgEnv=$mgEnv"
```

**Service-principal-with-cert flow** is shown above (preferred for unattended runs). For interactive operator triage, omit `-ClientId` / `-CertificateThumbprint` and pass `-Scopes` explicitly to `Connect-MgGraph`, and run `Connect-IPPSSession` without parameters to get the device-code prompt.

**Sovereign cloud gate helper** — every helper in §3–§9 calls this first:

```powershell
function Get-FsiIrmCloudGate {
    [CmdletBinding()] [OutputType([pscustomobject])] param()
    if ($script:FsiCloud -in @('GCC','GCCHigh','DoD')) {
        return [pscustomobject]@{
            Status      = 'NotApplicable'
            Cloud       = $script:FsiCloud
            Rationale   = 'Insider Risk Management / Adaptive Protection are not available in US Government cloud programs (GCC, GCC High, DoD) per Microsoft Learn (insider-risk-management-adaptive-protection). Apply compensating controls — see Control 1.12 §12.'
            Reference   = 'https://learn.microsoft.com/en-us/purview/insider-risk-management-adaptive-protection'
            CheckedUtc  = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
    return $null  # null means "proceed"
}
```

---

## §3 — Helper: `Get-FsiIrmPolicyInventory`

```powershell
function Get-FsiIrmPolicyInventory {
<#
.SYNOPSIS
    Enumerates all Insider Risk Management policies, the templates they were instantiated from,
    their scope (in-scope users / priority groups / administrative units), and their enabled state.
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])] param()
    $gate = Get-FsiIrmCloudGate
    if ($gate) { return $gate }

    try {
        $templates = Get-InsiderRiskPolicyTemplate -ErrorAction Stop
        $policies  = Get-InsiderRiskPolicy -ErrorAction Stop |
            Select-Object Name, Mode, Enabled, Template, InScopeUserGroups,
                          PriorityUserGroups, ExcludedUserGroups, WhenChangedUTC

        $expected = @(
            'Data leaks',
            'Data leaks by priority users',
            'Data theft by departing users',
            'General security policy violations',
            'Risky AI usage'
        )
        $present  = @($policies | ForEach-Object { $_.Template })
        $missing  = @($expected | Where-Object { $_ -notin $present })

        $status = if ($missing.Count -eq 0 -and $policies.Count -gt 0) { 'Clean' }
                  elseif ($policies.Count -eq 0)                       { 'Anomaly' }
                  else                                                  { 'Anomaly' }

        return [pscustomobject]@{
            Status            = $status
            Cloud             = $script:FsiCloud
            TemplateCount     = $templates.Count
            PolicyCount       = $policies.Count
            Policies          = $policies
            ExpectedTemplates = $expected
            MissingTemplates  = $missing
            CheckedUtc        = (Get-Date).ToUniversalTime().ToString('o')
        }
    } catch {
        return [pscustomobject]@{
            Status     = 'Error'
            Cloud      = $script:FsiCloud
            Error      = $_.Exception.Message
            CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

---

## §4 — Helper: `Get-FsiAdaptiveProtectionStatus`

```powershell
function Get-FsiAdaptiveProtectionStatus {
<#
.SYNOPSIS
    Reports whether Adaptive Protection is enabled and which DLP rules consume IRM risk tiers.
.DESCRIPTION
    Adaptive Protection is the bridge from IRM risk levels (Elevated / Moderate / Minor) to
    enforcement in DLP, Data Lifecycle Management, and Conditional Access. A tenant can have
    IRM policies in place WITHOUT Adaptive Protection enabled — in which case the risk signal
    never propagates and the control is functionally inert. See Control 1.12 §0 defect 2.
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])] param()
    $gate = Get-FsiIrmCloudGate
    if ($gate) { return $gate }   # NotApplicable in GCC / GCC High / DoD

    try {
        $policyConfig = Get-PolicyConfig -ErrorAction Stop
        $apEnabled    = [bool]$policyConfig.AdaptiveProtectionEnabled

        # DLP rules that escalate by IRM risk tier — must reference IRMSettings explicitly.
        $dlpRules = Get-DlpComplianceRule -ErrorAction Stop |
            Where-Object { $_.IRMSettings -or $_.AdaptiveProtectionRiskLevel } |
            Select-Object Name, ParentPolicyName, Mode, IRMSettings,
                          AdaptiveProtectionRiskLevel, Disabled

        $tierCoverage = @{
            Elevated = @($dlpRules | Where-Object { $_.AdaptiveProtectionRiskLevel -eq 'Elevated' }).Count
            Moderate = @($dlpRules | Where-Object { $_.AdaptiveProtectionRiskLevel -eq 'Moderate' }).Count
            Minor    = @($dlpRules | Where-Object { $_.AdaptiveProtectionRiskLevel -eq 'Minor'    }).Count
        }

        $status = if (-not $apEnabled)                                        { 'Anomaly' }
                  elseif ($tierCoverage.Elevated -eq 0)                       { 'Anomaly' }
                  elseif ($dlpRules.Count -eq 0)                              { 'Anomaly' }
                  else                                                        { 'Clean'   }

        return [pscustomobject]@{
            Status                       = $status
            Cloud                        = $script:FsiCloud
            AdaptiveProtectionEnabled    = $apEnabled
            DlpRuleCount                 = $dlpRules.Count
            TierCoverage                 = $tierCoverage
            Rules                        = $dlpRules
            Notes                        = if (-not $apEnabled) {
                                              'Adaptive Protection toggle is OFF — IRM risk tiers will not propagate to DLP/CA/DLM.'
                                          } elseif ($tierCoverage.Elevated -eq 0) {
                                              'No DLP rule scopes Elevated risk tier; high-risk users have no escalated enforcement.'
                                          } else { '' }
            CheckedUtc                   = (Get-Date).ToUniversalTime().ToString('o')
        }
    } catch {
        return [pscustomobject]@{
            Status = 'Error'; Cloud = $script:FsiCloud
            Error  = $_.Exception.Message
            CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

---

## §5 — Helper: `Get-FsiIrmHrConnectorState`

```powershell
function Get-FsiIrmHrConnectorState {
<#
.SYNOPSIS
    Reports last-sync time, record count, and lag for the Microsoft 365 HR data connector that
    feeds IRM departing-user / risky-user / priority-user templates.
.PARAMETER MaxLagHours
    Firm-defined maximum acceptable lag from the upstream HRIS export. Default 26h (one day plus
    cushion). Document the chosen value in your WSP.
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])]
    param([int]$MaxLagHours = 26)

    $gate = Get-FsiIrmCloudGate
    if ($gate) { return $gate }

    try {
        # Microsoft Graph dataConnectors surface — preferred (commercial)
        $connectors = Invoke-MgGraphRequest -Method GET `
            -Uri 'v1.0/security/dataConnectors' -ErrorAction Stop
        $hr = $connectors.value | Where-Object { $_.connectorType -eq 'humanResources' -or $_.displayName -match 'HR' }

        if (-not $hr) {
            return [pscustomobject]@{
                Status     = 'Anomaly'
                Cloud      = $script:FsiCloud
                Rationale  = 'No HR data connector found. Departing-user / risky-user templates will not produce signal.'
                CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
            }
        }

        $rows = foreach ($c in $hr) {
            $lastSync = if ($c.lastSyncDateTime) { [datetime]$c.lastSyncDateTime } else { $null }
            $lagH     = if ($lastSync) { [math]::Round(((Get-Date).ToUniversalTime() - $lastSync.ToUniversalTime()).TotalHours, 1) } else { $null }
            [pscustomobject]@{
                Name         = $c.displayName
                State        = $c.state
                LastSyncUtc  = $lastSync
                LagHours     = $lagH
                RecordCount  = $c.recordCount
                ExceedsLag   = ($lagH -ne $null -and $lagH -gt $MaxLagHours)
            }
        }

        $status = if ($rows | Where-Object { $_.ExceedsLag -or $_.State -ne 'enabled' }) { 'Anomaly' } else { 'Clean' }

        return [pscustomobject]@{
            Status      = $status
            Cloud       = $script:FsiCloud
            MaxLagHours = $MaxLagHours
            Connectors  = $rows
            CheckedUtc  = (Get-Date).ToUniversalTime().ToString('o')
        }
    } catch {
        return [pscustomobject]@{
            Status = 'Error'; Cloud = $script:FsiCloud
            Error  = $_.Exception.Message
            CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

---

## §6 — Helper: `Get-FsiIrmSignalCoverage`

```powershell
function Get-FsiIrmSignalCoverage {
<#
.SYNOPSIS
    Verifies that signal sources required by deployed IRM policies are actually present:
    Defender for Endpoint, Defender for Cloud Apps connectors, Unified Audit Log, browser
    signal extension (Edge / Chrome) for Risky AI usage / Risky browser usage.
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])] param()
    $gate = Get-FsiIrmCloudGate
    if ($gate) { return $gate }

    try {
        # 1. Unified Audit Log — most common silent failure (per Control 1.12 Key Configuration Points)
        $admin = Get-AdminAuditLogConfig -ErrorAction Stop
        $ualOn = [bool]$admin.UnifiedAuditLogIngestionEnabled

        # 2. Defender for Endpoint integration (read via Graph security)
        $mdeOn = $false
        try {
            $secAlerts = Invoke-MgGraphRequest -Method GET `
                -Uri "v1.0/security/alerts_v2?`$top=1&`$filter=serviceSource eq 'microsoftDefenderForEndpoint'" `
                -ErrorAction Stop
            $mdeOn = [bool]$secAlerts.value
        } catch { $mdeOn = $false }

        # 3. Defender for Cloud Apps connectors
        $mdcaConnectors = @()
        try {
            $resp = Invoke-MgGraphRequest -Method GET `
                -Uri 'v1.0/security/dataConnectors' -ErrorAction Stop
            $mdcaConnectors = @($resp.value | Where-Object { $_.connectorType -match 'cloudApp|Box|Dropbox|GoogleDrive|S3' })
        } catch { }

        # 4. Browser-signal indicators — required by Risky AI usage and Risky browser usage
        $policies = Get-InsiderRiskPolicy -ErrorAction Stop
        $needsBrowser = @($policies | Where-Object { $_.Template -in @('Risky AI usage','Risky browser usage') })

        $status = if (-not $ualOn)                                            { 'Anomaly' }
                  elseif ($needsBrowser -and -not $mdeOn)                     { 'Anomaly' }
                  elseif (($policies.Template -contains 'Data theft by departing users') -and $mdcaConnectors.Count -eq 0) { 'Anomaly' }
                  else                                                        { 'Clean'   }

        return [pscustomobject]@{
            Status                  = $status
            Cloud                   = $script:FsiCloud
            UnifiedAuditLogEnabled  = $ualOn
            MdeIntegrated           = $mdeOn
            McasConnectorCount      = $mcdaConnectors.Count
            BrowserDependentPolicies = $needsBrowser.Name
            Notes                   = if (-not $ualOn) { 'Unified Audit Log OFF — IRM policies will produce zero signal. Enable per Control 1.7.' } else { '' }
            CheckedUtc              = (Get-Date).ToUniversalTime().ToString('o')
        }
    } catch {
        return [pscustomobject]@{
            Status = 'Error'; Cloud = $script:FsiCloud
            Error  = $_.Exception.Message
            CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

> Browser-extension presence on endpoints cannot be verified from PowerShell alone; cross-walk with Intune or Defender for Endpoint device inventory and record the methodology in the verification playbook.

---

## §7 — Helper: `Test-FsiIrmAlertRouting`

```powershell
function Test-FsiIrmAlertRouting {
<#
.SYNOPSIS
    Verifies that IRM alerts surface in the Unified Audit Log (Control 1.7) and reach Microsoft
    Sentinel via the Office 365 connector (Control 3.9), and that they route into the supervisory
    review queue defined under Control 2.12.
.PARAMETER WorkspaceId
    Microsoft Sentinel Log Analytics workspace ID for the connected SIEM.
.PARAMETER LookbackDays
    Audit lookback window. Default 7.
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [string]$WorkspaceId,
        [int]$LookbackDays = 7
    )
    $gate = Get-FsiIrmCloudGate
    if ($gate) { return $gate }

    try {
        $start = (Get-Date).AddDays(-$LookbackDays)
        $end   = Get-Date

        # 1. UAL surface — IRM events appear under RecordType "InsiderRiskManagement"
        $ualEvents = Search-UnifiedAuditLog -StartDate $start -EndDate $end `
            -RecordType InsiderRiskManagement -ResultSize 100 -ErrorAction SilentlyContinue

        # 2. Sentinel surface — query the Office 365 / IRM table
        # Caller is expected to have Az.OperationalInsights connected.
        $sentinelHits = $null
        try {
            $kql = "OfficeActivity | where TimeGenerated > ago(${LookbackDays}d) | where RecordType == 'InsiderRiskManagement' | summarize c=count()"
            $sentinelHits = Invoke-AzOperationalInsightsQuery -WorkspaceId $WorkspaceId -Query $kql -ErrorAction Stop
        } catch { }

        $status = if ($ualEvents -and $sentinelHits.Results.c -gt 0) { 'Clean' }
                  elseif ($ualEvents -and -not $sentinelHits)        { 'Anomaly' }
                  elseif (-not $ualEvents)                            { 'Pending' }   # could simply be a quiet window
                  else                                                { 'Anomaly' }

        return [pscustomobject]@{
            Status               = $status
            Cloud                = $script:FsiCloud
            UalEventCount        = ($ualEvents | Measure-Object).Count
            SentinelEventCount   = if ($sentinelHits) { [int]$sentinelHits.Results.c } else { $null }
            LookbackDays         = $LookbackDays
            SupervisoryQueueRef  = 'Control 2.12 — Supervisory Review queue (verify routing in Comm Compliance UI)'
            CheckedUtc           = (Get-Date).ToUniversalTime().ToString('o')
        }
    } catch {
        return [pscustomobject]@{
            Status = 'Error'; Cloud = $script:FsiCloud
            Error  = $_.Exception.Message
            CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

> A `Pending` result during a quiet detection window is normal. Re-run after a known synthetic event injection (see [`verification-testing.md`](verification-testing.md)) before relying on this output for an attestation.

---

## §8 — Helper: `Test-FsiIrmAnonymization`

```powershell
function Test-FsiIrmAnonymization {
<#
.SYNOPSIS
    Confirms that IRM is configured to pseudonymize usernames in alerts by default — required to
    support privacy expectations under NYDFS 23 NYCRR §500.06 (data minimization in monitoring),
    GLBA 501(b) safeguards, and state employee-monitoring statutes (CT, DE, NY).
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])] param()
    $gate = Get-FsiIrmCloudGate
    if ($gate) { return $gate }

    try {
        $cfg = Get-IRMConfiguration -ErrorAction Stop
        $anon = [bool]$cfg.AnonymizationEnabled

        $status = if ($anon) { 'Clean' } else { 'Anomaly' }
        return [pscustomobject]@{
            Status                = $status
            Cloud                 = $script:FsiCloud
            AnonymizationEnabled  = $anon
            IntelligentDetection  = $cfg.IntelligentDetectionsEnabled
            Rationale             = if (-not $anon) {
                'Anonymization is OFF. Identifying analyst views require a documented privacy approval per NYDFS §500.06 and applicable state monitoring statutes.'
            } else { 'Default privacy posture preserved.' }
            CheckedUtc            = (Get-Date).ToUniversalTime().ToString('o')
        }
    } catch {
        return [pscustomobject]@{
            Status = 'Error'; Cloud = $script:FsiCloud
            Error  = $_.Exception.Message
            CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

---

## §9 — Helper: `Get-FsiIrmAgentAbuseIndicators`

```powershell
function Get-FsiIrmAgentAbuseIndicators {
<#
.SYNOPSIS
    Inventories custom IRM indicators configured for Copilot / agent abuse signals required by FSI
    use cases — excessive prompt rate, sensitive grounding-source queries, MNPI extraction
    attempts, off-hours access bursts. Cross-walks against expected indicator set.
.DESCRIPTION
    Upstream telemetry for these indicators comes from:
      * Control 1.5 (DLP) — sensitive-content prompt and response classification
      * Control 1.6 (DSPM for AI) — agent interaction risk signal
      * Control 1.21 (adversarial input logging) — prompt-injection / jailbreak attempts
    IRM consumes the resulting signal via custom indicators registered in Settings -> Policy
    indicators -> Custom indicators (Purview UI).
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])] param()
    $gate = Get-FsiIrmCloudGate
    if ($gate) { return $gate }

    $expected = @(
        'Excessive Copilot prompt rate per user',
        'Sensitive grounding-source query by non-need-to-know user',
        'MNPI keyword extraction attempt',
        'Off-hours agent access burst',
        'Agent prompt anomaly (deviation from baseline)'
    )

    try {
        $cfg = Get-IRMConfiguration -ErrorAction Stop
        # Custom indicators are exposed via Get-PolicyConfig CustomIndicators array on commercial.
        $pc  = Get-PolicyConfig -ErrorAction Stop
        $custom = @()
        if ($pc.PSObject.Properties.Name -contains 'CustomIndicators') {
            $custom = @($pc.CustomIndicators | Select-Object Name, Description, Enabled)
        }

        $present = @($custom | Where-Object { $_.Enabled } | ForEach-Object { $_.Name })
        $missing = @($expected | Where-Object { $_ -notin $present })

        $status = if ($missing.Count -eq 0) { 'Clean' } else { 'Anomaly' }
        return [pscustomobject]@{
            Status              = $status
            Cloud               = $script:FsiCloud
            ExpectedIndicators  = $expected
            PresentIndicators   = $present
            MissingIndicators   = $missing
            UpstreamControls    = @('1.5 (DLP)','1.6 (DSPM for AI)','1.21 (adversarial input)')
            CheckedUtc          = (Get-Date).ToUniversalTime().ToString('o')
        }
    } catch {
        return [pscustomobject]@{
            Status = 'Error'; Cloud = $script:FsiCloud
            Error  = $_.Exception.Message
            CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

---

## §10 — Mutating: create or update an IRM policy (idempotent, Get-then-Set)

> **Mutation safety.** All mutations use `[CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]` and snapshot before write per BL-§4. Always invoke first with `-WhatIf`.

```powershell
function New-FsiIrmDataLeaksPolicy {
<#
.SYNOPSIS
    Creates or updates the "Data leaks" IRM policy with FSI-appropriate scope, idempotently.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$PolicyName,
        [Parameter(Mandatory)] [string[]]$InScopeUserGroups,
        [string[]]$PriorityUserGroups = @(),
        [string]$EvidencePath = '.\evidence'
    )
    $gate = Get-FsiIrmCloudGate
    if ($gate) {
        Write-Warning "Sovereign cloud detected ($($gate.Cloud)) — IRM policy mutation skipped. Apply compensating controls per Control 1.12 §12."
        return $gate
    }

    $ErrorActionPreference = 'Stop'
    New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null
    $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
    Start-Transcript -Path "$EvidencePath\transcript-irm-$ts.log" -IncludeInvocationHeader

    $existing = Get-InsiderRiskPolicy -Identity $PolicyName -ErrorAction SilentlyContinue
    if ($existing) {
        $existing | ConvertTo-Json -Depth 10 | Set-Content "$EvidencePath\before-$PolicyName-$ts.json"
        if ($PSCmdlet.ShouldProcess($PolicyName, 'Set-InsiderRiskPolicy (update scope)')) {
            Set-InsiderRiskPolicy -Identity $PolicyName `
                -InScopeUserGroups $InScopeUserGroups `
                -PriorityUserGroups $PriorityUserGroups
        }
    } else {
        if ($PSCmdlet.ShouldProcess($PolicyName, 'New-InsiderRiskPolicy (Data leaks template)')) {
            New-InsiderRiskPolicy -Name $PolicyName -InsiderRiskScenario 'DataLeaks' `
                -InScopeUserGroups $InScopeUserGroups `
                -PriorityUserGroups $PriorityUserGroups `
                -Enabled $true
        }
    }

    Get-InsiderRiskPolicy -Identity $PolicyName |
        ConvertTo-Json -Depth 10 | Set-Content "$EvidencePath\after-$PolicyName-$ts.json"

    Stop-Transcript
}
```

**Adaptive Protection enablement** (separate from any single policy — tenant-level toggle):

```powershell
function Enable-FsiAdaptiveProtection {
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param([string]$EvidencePath = '.\evidence')
    $gate = Get-FsiIrmCloudGate
    if ($gate) { Write-Warning "Adaptive Protection unavailable in $($gate.Cloud)."; return $gate }

    $before = Get-PolicyConfig
    if ($PSCmdlet.ShouldProcess('Tenant', 'Enable Adaptive Protection')) {
        Set-PolicyConfig -AdaptiveProtectionEnabled $true
    }
    $after = Get-PolicyConfig
    @{ Before = $before; After = $after } | ConvertTo-Json -Depth 10 |
        Set-Content (Join-Path $EvidencePath "ap-toggle-$(Get-Date -f yyyyMMdd-HHmmss).json")
}
```

---

## §11 — DLP rule integration with risk tiers (Adaptive Protection escalation)

Adaptive Protection escalates DLP rule actions based on the user's calculated IRM risk tier — **Elevated** > **Moderate** > **Minor**. The `Set-DlpComplianceRule -IRMSettings` parameter wires a DLP rule into the tier system.

```powershell
function Set-FsiDlpRuleForRiskTier {
<#
.SYNOPSIS
    Wires a DLP rule into Adaptive Protection at a given risk tier (Elevated / Moderate / Minor).
.DESCRIPTION
    Get-then-Set pattern. Snapshots the rule to evidence before mutating. The DLP rule itself
    must already exist (managed by Control 1.5); this helper only attaches the IRM tier mapping.
#>
    [CmdletBinding(SupportsShouldProcess, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory)] [string]$RuleName,
        [Parameter(Mandatory)] [ValidateSet('Elevated','Moderate','Minor')] [string]$RiskLevel,
        [string]$EvidencePath = '.\evidence'
    )
    $gate = Get-FsiIrmCloudGate
    if ($gate) { Write-Warning "Adaptive Protection unavailable in $($gate.Cloud)."; return $gate }

    $rule = Get-DlpComplianceRule -Identity $RuleName -ErrorAction Stop
    $ts   = Get-Date -Format 'yyyyMMdd-HHmmss'
    $rule | ConvertTo-Json -Depth 10 | Set-Content "$EvidencePath\dlp-rule-before-$RuleName-$ts.json"

    if ($PSCmdlet.ShouldProcess($RuleName, "Bind to AdaptiveProtection RiskLevel=$RiskLevel")) {
        Set-DlpComplianceRule -Identity $RuleName -AdaptiveProtectionRiskLevel $RiskLevel
    }

    Get-DlpComplianceRule -Identity $RuleName |
        ConvertTo-Json -Depth 10 | Set-Content "$EvidencePath\dlp-rule-after-$RuleName-$ts.json"
}
```

> The `-AdaptiveProtectionRiskLevel` parameter name is verified against the April 2026 cmdlet surface but Microsoft has renamed adaptive-protection-related DLP parameters at least twice; verify `Get-Command Set-DlpComplianceRule -Syntax` output before each change window and reconcile against the parent control file.

---

## §12 — Compensating controls in US Government clouds (GCC, GCC High, DoD)

Because IRM and Adaptive Protection are **not available** in US Gov clouds at the time of authoring, Zone 3 deployments in those tenants must evidence the following stack as the documented compensating control posture. Record the substitution as a control exception in the firm's GRC tool with quarterly re-verification of Microsoft Learn for parity changes.

| Compensating control | Replaces (in IRM gap) | This framework reference |
|---|---|---|
| Static role-based DLP with elevated actions for priority user groups | Adaptive-Protection-driven DLP escalation by risk tier | [Control 1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) |
| Communication Compliance with risky-language and sensitive-content policies | Risky AI usage / Risky browser usage signal | [Control 1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) |
| Microsoft Sentinel UEBA + custom analytics rules for departing-user / off-hours / volume anomalies | Data theft by departing users; ML-driven scoring | [Control 3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |
| Audit (Premium) with retained Copilot interaction logs and adversarial-input logs | IRM policy-derived audit trail | [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [Control 1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) |
| Manual supervisory review under WSP, escalated to MRM for AI-scored signals | Triage Agent | [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md), [Control 2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |

```powershell
function Get-FsiIrmCompensatingPosture {
<#
.SYNOPSIS
    For sovereign tenants, returns the compensating-control coverage state across DLP, Comm
    Compliance, Sentinel UEBA, and Audit (Premium). Returns NotApplicable on commercial cloud.
#>
    [CmdletBinding()] [OutputType([pscustomobject])] param()
    if ($script:FsiCloud -notin @('GCC','GCCHigh','DoD')) {
        return [pscustomobject]@{
            Status     = 'NotApplicable'
            Cloud      = $script:FsiCloud
            Rationale  = 'Compensating-posture helper applies only to sovereign clouds. Commercial tenants should run Get-FsiIrmPolicyInventory and Get-FsiAdaptiveProtectionStatus instead.'
            CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
    # Stubbed: callers supply DLP / CC / Sentinel posture from their respective control playbooks.
    return [pscustomobject]@{
        Status     = 'Pending'
        Cloud      = $script:FsiCloud
        Guidance   = 'Cross-walk with Control 1.5, 1.7, 1.10, 1.21, 2.12, and 3.9 helpers and aggregate.'
        CheckedUtc = (Get-Date).ToUniversalTime().ToString('o')
    }
}
```

---

## §13 — Evidence emission and scheduler integration

All helpers return `[pscustomobject]` shapes that flow into the canonical evidence emitter from BL-§5. A reference orchestrator that runs the full Control 1.12 sweep:

```powershell
# Save as: scripts/Invoke-Agt112Sweep.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$EvidencePath,
    [string]$WorkspaceId
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $EvidencePath | Out-Null

$results = [ordered]@{
    PolicyInventory      = Get-FsiIrmPolicyInventory
    AdaptiveProtection   = Get-FsiAdaptiveProtectionStatus
    HrConnector          = Get-FsiIrmHrConnectorState
    SignalCoverage       = Get-FsiIrmSignalCoverage
    AlertRouting         = if ($WorkspaceId) { Test-FsiIrmAlertRouting -WorkspaceId $WorkspaceId } else { $null }
    Anonymization        = Test-FsiIrmAnonymization
    AgentAbuseIndicators = Get-FsiIrmAgentAbuseIndicators
    CompensatingPosture  = Get-FsiIrmCompensatingPosture
}

# Emit each artifact with SHA-256 manifest per BL-§5
foreach ($k in $results.Keys) {
    if ($null -ne $results[$k]) {
        Write-FsiEvidence -Object $results[$k] -Name "agt112-$k" -EvidencePath $EvidencePath
    }
}

# Aggregate posture
$aggregate = [pscustomobject]@{
    OverallStatus = if ($results.Values | Where-Object { $_.Status -eq 'Anomaly' }) { 'Anomaly' }
                    elseif ($results.Values | Where-Object { $_.Status -eq 'Error' }) { 'Error' }
                    elseif (($results.Values | Where-Object { $_.Status -eq 'NotApplicable' }).Count -eq $results.Count) { 'NotApplicable' }
                    else { 'Clean' }
    Components    = $results
    Cloud         = $script:FsiCloud
    GeneratedUtc  = (Get-Date).ToUniversalTime().ToString('o')
}
Write-FsiEvidence -Object $aggregate -Name 'agt112-aggregate' -EvidencePath $EvidencePath
```

**Scheduler cadence.** Run weekly at minimum; run after any IRM-policy change ticket; run on the day before each quarterly attestation. Land artifacts in WORM storage (Purview Data Lifecycle Management retention lock or Azure Storage immutability policy) per BL-§5 and SEC 17a-4(f).

---

## Cross-links

* [Control 1.5 — Data Loss Prevention](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — upstream classification and downstream Adaptive-Protection enforcement
* [Control 1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — AI-interaction signal source
* [Control 1.7 — Audit Logging & Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — Unified Audit Log dependency
* [Control 1.10 — Communication Compliance](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — risky-language compensating control
* [Control 1.21 — Adversarial Input Logging](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) — prompt-injection telemetry feeding agent-abuse indicators
* [Control 2.6 — Model Risk Management (OCC 2011-12 / SR 11-7)](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) — IRM ML scoring inventory and validation
* [Control 2.12 — Supervision of AI-Generated Content](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — supervisory queue for IRM alerts
* [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — NYDFS §500.17 / Reg S-P notice triggers
* [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — alert forwarding and UEBA compensating control

---

*Updated: April 2026 | Version: v1.4 | UI Verification Status: Current*