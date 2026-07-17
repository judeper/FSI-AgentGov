# Control 1.12 — PowerShell Setup: Insider Risk Management and Adaptive Protection Automation

> **Scope.** This playbook automates the **insider-risk detection and adaptive-protection plane** for Control 1.12 across **Microsoft Purview Insider Risk Management (IRM), Adaptive Protection, the Microsoft 365 HR data connector, Defender for Endpoint / Defender for Cloud Apps signal sources, DLP rule integration with risk tiers, custom indicators for AI-agent abuse, and alert routing into Sentinel and supervisory queues** in US financial services tenants. It assumes you have already read [`../../_shared/powershell-baseline.md`](../../_shared/powershell-baseline.md) (referenced below as **BL-§N**) and the parent control specification [`../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md).
>
> **What this playbook is.** A reproducible, reproducible harness that (a) pins module versions and verifies cmdlet surface; (b) bootstraps a certificate-authenticated, audit-only IRM reader principal that is distinct from the IRM Admin / Investigator / Approver principals; (c) enumerates IRM policy templates, deployed policies, scope, and tenant configuration; (d) audits Adaptive Protection enablement and the DLP rules that consume IRM risk tiers (Elevated / Moderate / Minor); (e) verifies HR connector freshness and signal-source coverage (Defender for Endpoint, Defender for Cloud Apps, audit feeds, browser extension where applicable); (f) emits custom-indicator inventory for AI-agent abuse signals (excessive prompt rate, MNPI grounding queries, off-hours bursts) per Control 1.5 / 1.6 telemetry contracts; and (g) writes evidence with SHA-256 manifests for the quarterly attestation pack.
>
> **What this playbook is not.** It is not a substitute for the firm's Written Supervisory Procedures (FINRA Rule 3110), HR investigation workflows, legal-hold decisions, or supervisory review by a registered principal. It does not, by itself, configure or enable Forensic Evidence — that capability requires dual-authorization (Investigator request + Approver consent) executed in the Purview portal per [Control 1.12 § Forensic Evidence](../../../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md). It does not retain books-and-records artifacts; durable retention is the responsibility of [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) and [Control 1.9](../../../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md).
>
>
> **Hedged language reminder.** Output of this harness *supports* compliance with FINRA Rule 3110 / 4511, FINRA RN 25-07 (RFC, contextual only), SEC Rule 17a-3 / 17a-4, SEC Regulation S-P (2024 amendments), GLBA 501(b), SOX 302/404, NYDFS 23 NYCRR §500.06 / §500.16 / §500.17, OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12), Fed SR 26-2 (formerly SR 11-7), and FFIEC IT Examination Handbook expectations. It does not, by itself, *ensure* a passing examination, *guarantee* that every insider event is detected, *prevent* exfiltration, or *eliminate* false negatives in ML-driven scoring. Implementation requires that organizations verify endpoint availability, module pinning, HR connector accuracy, and signal-source coverage at every change window, and that they treat any preview surface (Risky Agents, Risky AI usage, Triage Agent) as **additive** evidence rather than a complete substitute for human supervisory review.

| Field | Value |

| Control ID | 1.12 |
| Pillar | 1 — Security |
| Playbook | PowerShell Setup |
| PowerShell Edition | 7.4 LTS Core (orchestrator); 5.1 Desktop available for any Windows-only legacy fallback |
| Last UI Verified | April 2026 |
| Companion Playbooks | [`portal-walkthrough.md`](portal-walkthrough.md) · [`verification-testing.md`](verification-testing.md) · [`troubleshooting.md`](troubleshooting.md) |
| Related Controls | [1.5](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) · [1.6](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) · [1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) · [1.10](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) · [1.21](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) · [2.6](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) · [2.12](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) · [3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) · [3.9](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) |

---

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

| `Get-AdminAuditLogConfig` (read) | **Exchange Online Admin** or **Compliance Administrator** | Supported only for audit-status dependency evidence (`UnifiedAuditLogIngestionEnabled`). Insider Risk policy inventory remains portal/manual evidence. |
| Insider Risk policy create/update/list operations | **Insider Risk Management Admins** (portal) | Perform in Purview portal only and export evidence manually; do not rely on undocumented PowerShell cmdlets |
| Forensic Evidence capture request | **Insider Risk Management Investigators** | Request only — approval is a separate role (Approvers) |
| Forensic Evidence capture approval | **Insider Risk Management Approvers** | **Must be distinct** from Investigators (dual-authorization) |
| Microsoft Graph IRM read (optional context) | `ThreatIntelligence.Read.All`, `SecurityEvents.Read.All`, `IdentityRiskyUser.Read.All` (verify on Learn at deployment) | Use for adjacent signal context only; not for policy inventory unless Microsoft documents a GA endpoint |
| HR connector read | `User.Read.All`, `AuditLog.Read.All`, plus connector-specific app role | Read-only for assessment |

### 1.3 Separate audit-only principal (recommended)

Create a service principal — `agt112-irm-reader` — that holds **Insider Risk Management Auditors** in Purview plus the read-only Graph scopes above. Never assign it Admin / Investigator / Approver. Authenticate it with a certificate, not a secret (BL-§2).

---

# Save as: scripts/Connect-Agt112.ps1
[CmdletBinding()]
param(
    [string]$Cloud = 'Commercial',

    [Parameter(Mandatory)] [string]$TenantId,
    [Parameter(Mandatory)] [string]$AppId,
    [Parameter(Mandatory)] [string]$CertificateThumbprint,

    [Parameter(Mandatory)] [string]$UserPrincipalName  # for Connect-IPPSSession context
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Helpers in §2-§8 read this variable to short-circuit to NotApplicable.
$script:FsiCloud = $Cloud

$mgEnv = @{
    Commercial = 'Global'
}[$Cloud]

$ippsUri = @{
    Commercial = 'https://ps.compliance.protection.outlook.com/PowerShell-LiveID'
}[$Cloud]

Connect-MgGraph -TenantId $TenantId -ClientId $AppId `
    -CertificateThumbprint $CertificateThumbprint -Environment $mgEnv -NoWelcome

# Connect-IPPSSession is the gateway for IRM cmdlets in commercial cloud.
# §2-§8 detect that and report NotApplicable rather than failing.
Connect-IPPSSession -UserPrincipalName $UserPrincipalName -ConnectionUri $ippsUri

Write-Verbose "Connected: cloud=$Cloud tenant=$TenantId mgEnv=$mgEnv"
```

**Service-principal-with-cert flow** is shown above (preferred for unattended runs). For interactive operator triage, omit `-ClientId` / `-CertificateThumbprint` and pass `-Scopes` explicitly to `Connect-MgGraph`, and run `Connect-IPPSSession` without parameters to get the device-code prompt.


```powershell
function Get-FsiIrmCloudGate {
    [CmdletBinding()] [OutputType([pscustomobject])] param()
    return $null  # null means "proceed"
}
```

---

## §2 — Helper: `Get-FsiIrmPolicyEvidenceStatus` (manual evidence gate)

```powershell
function Get-FsiIrmPolicyEvidenceStatus {
<#
.SYNOPSIS
    Validates that required manual Insider Risk evidence exports are present.
.DESCRIPTION
    Microsoft does not currently document a supported PowerShell or GA Graph endpoint
    to inventory Insider Risk policies for Control 1.12. This helper fails closed until
    reviewers provide portal exports.
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])]
    param(
        [Parameter(Mandatory)] [string]$PolicyExportPath,
        [Parameter(Mandatory)] [string]$AlertExportPath
    )

    $expectedTemplates = @(
        'Data leaks',
        'Data leaks by priority users',
        'Data theft by departing users',
        'General security policy violations',
        'Risky AI usage'
    )

    if (-not (Test-Path $PolicyExportPath) -or -not (Test-Path $AlertExportPath)) {
        return [pscustomobject]@{
            Status               = 'Pending'
            AutomationSupported  = $false
            MissingEvidence      = @(
                if (-not (Test-Path $PolicyExportPath)) { $PolicyExportPath }
                if (-not (Test-Path $AlertExportPath))  { $AlertExportPath }
            )
            CheckedUtc           = (Get-Date).ToUniversalTime().ToString('o')
            Note                 = 'Manual Purview exports are required; no supported policy-inventory cmdlet is available.'
        }
    }

    try {
        $policies = Import-Csv -Path $PolicyExportPath
        $alerts = Import-Csv -Path $AlertExportPath
        $presentTemplates = @($policies.Template | Where-Object { $_ } | Sort-Object -Unique)
        $missingTemplates = @($expectedTemplates | Where-Object { $_ -notin $presentTemplates })

        $status = if ($alerts.Count -eq 0 -or $missingTemplates.Count -gt 0) { 'Anomaly' } else { 'Clean' }

        return [pscustomobject]@{
            Status               = $status
            AutomationSupported  = $false
            PolicyCount          = $policies.Count
            AlertCount           = $alerts.Count
            ExpectedTemplates    = $expectedTemplates
            MissingTemplates     = $missingTemplates
            CheckedUtc           = (Get-Date).ToUniversalTime().ToString('o')
            EvidenceSource       = 'Purview portal exports'
        }
    } catch {
        return [pscustomobject]@{
            Status      = 'Error'
            Error       = $_.Exception.Message
            CheckedUtc  = (Get-Date).ToUniversalTime().ToString('o')
        }
    }
}
```

---

## §3 — Helper: `Get-FsiAdaptiveProtectionStatus`

```powershell
function Get-FsiAdaptiveProtectionStatus {
<#
.SYNOPSIS
    Produces evidence for Adaptive Protection using portal export + audit-status telemetry.
.DESCRIPTION
    Control 1.12 does not accept Get-PolicyConfig properties as authoritative Insider Risk evidence.
    This helper reads a reviewer-exported portal file and pairs it with Unified Audit ingestion state.
.PARAMETER PortalExportPath
    CSV export captured manually from Purview portal settings.
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])]
    param([string]$PortalExportPath = '.\evidence\adaptive-protection-portal.csv')
    $gate = Get-FsiIrmCloudGate
    if ($gate) { return $gate }

    try {
        $audit = Get-AdminAuditLogConfig -ErrorAction Stop
        $auditEnabled = if ($audit.PSObject.Properties.Name -contains 'UnifiedAuditLogIngestionEnabled') {
            [bool]$audit.UnifiedAuditLogIngestionEnabled
        } else {
            $null
        }

        if (-not (Test-Path -LiteralPath $PortalExportPath)) {
            return [pscustomobject]@{
                Status                    = 'Pending'
                Cloud                     = $script:FsiCloud
                AdaptiveProtectionEnabled = $null
                UnifiedAuditDependencyMet = $auditEnabled
                EvidenceSource            = "Manual export required: $PortalExportPath"
                CheckedUtc                = (Get-Date).ToUniversalTime().ToString('o')
            }
        }

        $rows = Import-Csv -LiteralPath $PortalExportPath
        $row = @($rows | Select-Object -First 1)
        $apEnabled = if ($row -and $row[0].PSObject.Properties.Name -contains 'AdaptiveProtectionEnabled') {
            [System.Convert]::ToBoolean($row[0].AdaptiveProtectionEnabled)
        } else {
            $null
        }

        $status = if ($null -eq $apEnabled) { 'Pending' }
                  elseif ($apEnabled -and $auditEnabled) { 'Clean' }
                  else { 'Anomaly' }

        return [pscustomobject]@{
            Status                    = $status
            Cloud                     = $script:FsiCloud
            AdaptiveProtectionEnabled = $apEnabled
            UnifiedAuditDependencyMet = $auditEnabled
            EvidenceSource            = "Purview portal export: $PortalExportPath"
            CheckedUtc                = (Get-Date).ToUniversalTime().ToString('o')
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

## §4 — Helper: `Get-FsiIrmHrConnectorState`

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

## §5 — Helper: `Get-FsiIrmSignalCoverage`

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

        # 4. Browser-dependent template verification is manual (portal evidence)
        $browserDependentTemplates = @('Risky AI usage', 'Risky browser usage')
        $status = if (-not $ualOn) { 'Anomaly' }
                  elseif (-not $mdeOn) { 'Pending' }
                  elseif ($mdcaConnectors.Count -eq 0) { 'Pending' }
                  else { 'Clean' }

        return [pscustomobject]@{
            Status                     = $status
            Cloud                      = $script:FsiCloud
            UnifiedAuditLogEnabled     = $ualOn
            MdeIntegrated              = $mdeOn
            McasConnectorCount         = $mdcaConnectors.Count
            BrowserDependentTemplates  = $browserDependentTemplates
            ManualVerificationRequired = $true
            Notes                      = if (-not $ualOn) {
                                            'Unified Audit Log OFF — IRM policies will produce zero signal. Enable per Control 1.7.'
                                         } else {
                                            'Use Purview portal exports to verify template assignment and policy scope.'
                                         }
            CheckedUtc                 = (Get-Date).ToUniversalTime().ToString('o')
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

## §6 — Helper: `Test-FsiIrmAlertRouting`

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

## §7 — Helper: `Test-FsiIrmAnonymization`

```powershell
function Test-FsiIrmAnonymization {
<#
.SYNOPSIS
    Verifies pseudonymization evidence using manual portal export + audit dependency.
.DESCRIPTION
    Do not use Get-IRMConfiguration as authoritative Control 1.12 evidence. Use Privacy settings
    export from Purview portal and keep Unified Audit ingestion status attached.
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])]
    param([string]$PortalExportPath = '.\evidence\irm-privacy-settings.csv')
    $gate = Get-FsiIrmCloudGate
    if ($gate) { return $gate }

    try {
        $audit = Get-AdminAuditLogConfig -ErrorAction Stop
        $auditEnabled = [bool]$audit.UnifiedAuditLogIngestionEnabled

        if (-not (Test-Path -LiteralPath $PortalExportPath)) {
            return [pscustomobject]@{
                Status                    = 'Pending'
                Cloud                     = $script:FsiCloud
                PseudonymizationEnabled   = $null
                UnifiedAuditDependencyMet = $auditEnabled
                EvidenceSource            = "Manual export required: $PortalExportPath"
                CheckedUtc                = (Get-Date).ToUniversalTime().ToString('o')
            }
        }

        $rows = Import-Csv -LiteralPath $PortalExportPath
        $row = @($rows | Select-Object -First 1)
        $anon = if ($row -and $row[0].PSObject.Properties.Name -contains 'PseudonymizationEnabled') {
            [System.Convert]::ToBoolean($row[0].PseudonymizationEnabled)
        } else {
            $null
        }
        $status = if ($null -eq $anon) { 'Pending' } elseif ($anon) { 'Clean' } else { 'Anomaly' }

        return [pscustomobject]@{
            Status                    = $status
            Cloud                     = $script:FsiCloud
            PseudonymizationEnabled   = $anon
            UnifiedAuditDependencyMet = $auditEnabled
            EvidenceSource            = "Purview portal export: $PortalExportPath"
            CheckedUtc                = (Get-Date).ToUniversalTime().ToString('o')
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

## §8 — Helper: `Get-FsiIrmAgentAbuseIndicators`

```powershell
function Get-FsiIrmAgentAbuseIndicators {
<#
.SYNOPSIS
    Cross-walks expected indicators against a manual Purview export.
.DESCRIPTION
    No documented PowerShell surface exists for Insider Risk policy indicator inventory.
    Export indicator settings from Purview portal and validate coverage from that artifact.
.OUTPUTS
    [pscustomobject] with Status in {Clean, Anomaly, Pending, NotApplicable, Error}.
#>
    [CmdletBinding()] [OutputType([pscustomobject])]
    param([string]$IndicatorExportPath = '.\evidence\irm-indicators.csv')
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
        $audit = Get-AdminAuditLogConfig -ErrorAction Stop
        $auditEnabled = [bool]$audit.UnifiedAuditLogIngestionEnabled

        if (-not (Test-Path -LiteralPath $IndicatorExportPath)) {
            return [pscustomobject]@{
                Status                    = 'Pending'
                Cloud                     = $script:FsiCloud
                UnifiedAuditDependencyMet = $auditEnabled
                EvidenceSource            = "Manual export required: $IndicatorExportPath"
                CheckedUtc                = (Get-Date).ToUniversalTime().ToString('o')
            }
        }

        $custom = Import-Csv -LiteralPath $IndicatorExportPath
        $present = @($custom | Where-Object { $_.Enabled -eq 'True' -or $_.Enabled -eq 'true' } | ForEach-Object { $_.Name })
        $missing = @($expected | Where-Object { $_ -notin $present })

        $status = if ($missing.Count -eq 0) { 'Clean' } else { 'Anomaly' }
        return [pscustomobject]@{
            Status              = $status
            Cloud               = $script:FsiCloud
            ExpectedIndicators  = $expected
            PresentIndicators   = $present
            MissingIndicators   = $missing
            UnifiedAuditDependencyMet = $auditEnabled
            EvidenceSource      = "Purview portal export: $IndicatorExportPath"
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

## §9 — Insider Risk policy changes (portal/manual only)

Insider Risk policy create/update/list actions must be executed in the Purview portal.
Do **not** rely on undocumented PowerShell cmdlets for policy lifecycle operations.

Recommended evidence bundle for each change:

1. Change ticket / approval reference.
2. Purview portal screenshots or CSV export before and after the change.
3. Alert disposition export showing post-change reviewer activity.
4. Reviewer attestation mapping changes to control objective (Control 1.12).

**Adaptive Protection enablement** (separate from any single policy — tenant-level toggle):

```powershell
Connect-IPPSSession -ShowBanner:$false
$audit = Get-AdminAuditLogConfig -ErrorAction Stop
$audit | Select-Object UnifiedAuditLogIngestionEnabled, AdminAuditLogAgeLimit
# Perform Adaptive Protection toggle in Purview portal (Settings -> Insider Risk -> Adaptive Protection),
# then export before/after portal evidence and attach the change ticket in the same evidence bundle.
```

---

## §10 — DLP rule integration with risk tiers (Adaptive Protection escalation)

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


## §11 — Evidence emission and scheduler integration

All helpers return `[pscustomobject]` shapes that flow into the canonical evidence emitter from BL-§4. A reference orchestrator that runs the full Control 1.12 sweep:

```powershell
# Save as: scripts/Invoke-Agt112Sweep.ps1
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [ValidateNotNullOrWhiteSpace()] [string]$EvidencePath,
    [Parameter(Mandatory)] [ValidateNotNullOrWhiteSpace()] [string]$PolicyExportPath,
    [Parameter(Mandatory)] [ValidateNotNullOrWhiteSpace()] [string]$AlertExportPath,
    [string]$WorkspaceId
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$resolvedEvidencePath    = [System.IO.Path]::GetFullPath($EvidencePath)
$resolvedPolicyExport    = [System.IO.Path]::GetFullPath($PolicyExportPath)
$resolvedAlertExport     = [System.IO.Path]::GetFullPath($AlertExportPath)
$policyExportParentPath  = Split-Path -Path $resolvedPolicyExport -Parent
$alertExportParentPath   = Split-Path -Path $resolvedAlertExport -Parent

if (-not [string]::IsNullOrWhiteSpace($policyExportParentPath) -and
    -not (Test-Path -LiteralPath $policyExportParentPath -PathType Container)) {
    throw "PolicyExportPath parent directory not found: $policyExportParentPath"
}

if (-not [string]::IsNullOrWhiteSpace($alertExportParentPath) -and
    -not (Test-Path -LiteralPath $alertExportParentPath -PathType Container)) {
    throw "AlertExportPath parent directory not found: $alertExportParentPath"
}

New-Item -ItemType Directory -Force -Path $resolvedEvidencePath | Out-Null

$results = [ordered]@{
    PolicyInventory      = Get-FsiIrmPolicyEvidenceStatus -PolicyExportPath $resolvedPolicyExport -AlertExportPath $resolvedAlertExport
    AdaptiveProtection   = Get-FsiAdaptiveProtectionStatus
    HrConnector          = Get-FsiIrmHrConnectorState
    SignalCoverage       = Get-FsiIrmSignalCoverage
    AlertRouting         = if ($WorkspaceId) { Test-FsiIrmAlertRouting -WorkspaceId $WorkspaceId } else { $null }
    Anonymization        = Test-FsiIrmAnonymization
    AgentAbuseIndicators = Get-FsiIrmAgentAbuseIndicators
}

# Emit each artifact with SHA-256 manifest per BL-§4
foreach ($k in $results.Keys) {
    if ($null -ne $results[$k]) {
        Write-FsiEvidence -Object $results[$k] -Name "agt112-$k" -EvidencePath $resolvedEvidencePath
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
Write-FsiEvidence -Object $aggregate -Name 'agt112-aggregate' -EvidencePath $resolvedEvidencePath
```

**Scheduler cadence.** Run weekly at minimum; run after any IRM-policy change ticket; run on the day before each quarterly attestation. Land artifacts in WORM storage (Purview Data Lifecycle Management retention lock or Azure Storage immutability policy) per BL-§4 and SEC 17a-4(f).

---

## Cross-links

* [Control 1.5 — Data Loss Prevention](../../../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) — upstream classification and downstream Adaptive-Protection enforcement
* [Control 1.6 — DSPM for AI](../../../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) — AI-interaction signal source
* [Control 1.7 — Audit Logging & Compliance](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) — Unified Audit Log dependency
* [Control 1.10 — Communication Compliance](../../../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) — risky-language compensating control
* [Control 1.21 — Adversarial Input Logging](../../../controls/pillar-1-security/1.21-adversarial-input-logging.md) — prompt-injection telemetry feeding agent-abuse indicators
* [Control 2.6 — Model Risk Management (OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly SR 11-7))](../../../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — IRM ML scoring inventory and validation
* [Control 2.12 — Supervision of AI-Generated Content](../../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) — supervisory queue for IRM alerts
* [Control 3.4 — Incident Reporting and Root Cause Analysis](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) — NYDFS §500.17 / Reg S-P notice triggers
* [Control 3.9 — Microsoft Sentinel Integration](../../../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) — alert forwarding and UEBA compensating control

---

*Updated: May 2026 | Version: v1.6.2 | UI Verification Status: Current*
