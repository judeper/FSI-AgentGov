<#
.SYNOPSIS
    Collects Microsoft Purview compliance configuration data for FSI Agent Governance assessment.

.DESCRIPTION
    Enumerates audit log configuration, DLP compliance policies, retention policies,
    communication compliance, eDiscovery cases, insider risk evidence status
    (manual policy inventory + audit dependency only), DSPM for AI, sensitivity label
    policies, and endpoint DLP settings via Security & Compliance PowerShell
    (ExchangeOnlineManagement).

    Outputs a structured JSON file (purview.json) consumed by the assessment engine.

    Pattern references:
      - Invoke-HardeningBaselineCheck.ps1 — audit log configuration checks (Items 7-9)
      - restrict-agent-publishing.ps1 — DLP connector classification patterns
      - FsiMimeControl.psm1 — MIME type compliance evaluation patterns

.PARAMETER TenantId
    Mandatory. Microsoft Entra tenant ID.

.PARAMETER AuthMode
    Mandatory. Authentication mode: Interactive or ServicePrincipal.

.PARAMETER ClientId
    Optional. Application (client) ID for certificate-based service principal authentication.

.PARAMETER ClientSecret
    Optional. Client secret as SecureString (not used for IPPS — certificate auth preferred for SP).

.PARAMETER OutputDir
    Mandatory. Root output directory. Collected JSON is written to $OutputDir\collected\purview.json.

.OUTPUTS
    purview.json — JSON file with audit config, DLP policies, retention,
    communication compliance, eDiscovery, insider risk manual-evidence status,
    DSPM, sensitivity labels, and endpoint DLP.

.NOTES
    Part of the FSI Agent Governance Assessment Engine — Purview Collector.
    Requires ExchangeOnlineManagement module for Connect-IPPSSession.
    Exit codes: 0 = success, 1 = partial failure (some sections null), 2 = total failure.
    Version: 1.0.0
#>

#Requires -Version 7.0

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$TenantId,

    [Parameter(Mandatory)]
    [ValidateSet('Interactive', 'ServicePrincipal')]
    [string]$AuthMode,

    [Parameter()]
    [string]$ClientId,

    [Parameter()]
    [securestring]$ClientSecret,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$OutputDir
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# ─── Initialise ──────────────────────────────────────────────────────
$warnings = [System.Collections.Generic.List[string]]::new()
$collectedDir = Join-Path $OutputDir 'collected'
if (-not (Test-Path $collectedDir)) {
    New-Item -ItemType Directory -Path $collectedDir -Force | Out-Null
}
$outputFile = Join-Path $collectedDir 'purview.json'

function Invoke-CollectorOperation {
    param(
        [Parameter(Mandatory)][string]$Target,
        [Parameter(Mandatory)][string]$Action,
        [Parameter(Mandatory)][scriptblock]$ScriptBlock
    )

    if (-not $PSCmdlet.ShouldProcess($Target, $Action)) {
        Write-Verbose "Skipping $Action on $Target because -WhatIf was specified."
        return $null
    }

    & $ScriptBlock
}

$collectorRoot = Split-Path -Parent $PSCommandPath
. (Join-Path $collectorRoot 'lib\InsiderRiskSupport.ps1')
. (Join-Path $collectorRoot 'lib\PurviewDspmSupport.ps1')

# ─── Module Import ───────────────────────────────────────────────────
Import-Module ExchangeOnlineManagement -ErrorAction Stop
Write-Verbose "Loaded ExchangeOnlineManagement module."

# ─── Authentication ──────────────────────────────────────────────────
# Connect-IPPSSession for Security & Compliance PowerShell.
# Interactive: user sign-in prompt. SP: certificate-based app auth.
Write-Verbose "Authenticating to Security & Compliance Center in $AuthMode mode..."

if ($AuthMode -eq 'Interactive') {
    Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'Connect to Security & Compliance PowerShell (interactive)' -ScriptBlock {
        Connect-IPPSSession -ErrorAction Stop
    } | Out-Null
}
else {
    if (-not $ClientId) {
        throw "ServicePrincipal auth requires -ClientId. Certificate-based auth is recommended for IPPS."
    }
    # Service principal with certificate auth for IPPS
    # Note: Connect-IPPSSession -AppId / -CertificateThumbprint is the supported SP path.
    # The caller should have the certificate installed in the current user's certificate store.
    Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'Connect to Security & Compliance PowerShell (service principal)' -ScriptBlock {
        Connect-IPPSSession -AppId $ClientId -Organization "$TenantId" -ErrorAction Stop
    } | Out-Null
}

Write-Verbose "Security & Compliance authentication stage complete."

# ═══════════════════════════════════════════════════════════════════════
# Section 1: Audit Log Configuration
# Supports: Controls 3.1 (Audit Logging), 3.2 (Audit Retention)
# Pattern: Invoke-HardeningBaselineCheck.ps1 Items 7-9 (Audit checks)
# ═══════════════════════════════════════════════════════════════════════
$auditConfig = $null
try {
    Write-Verbose "Section 1: Collecting audit log configuration..."

    $adminAuditConfig = Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'Get audit log configuration' -ScriptBlock {
        Get-AdminAuditLogConfig -ErrorAction Stop
    }

    if ($adminAuditConfig) {
        $unifiedAuditEnabled = $adminAuditConfig.UnifiedAuditLogIngestionEnabled

        # Audit configuration policies (audit plan tier)
        $auditPolicies = $null
        try {
            $auditPolicies = Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'List audit configuration policies' -ScriptBlock {
                Get-AuditConfigurationPolicy -ErrorAction Stop
            } | ForEach-Object {
                [PSCustomObject]@{
                    Identity    = $_.Identity
                    Priority    = $_.Priority
                    Workload    = $_.Workload
                }
            }
        }
        catch {
            $warnings.Add("Audit configuration policies not available: $($_.Exception.Message)")
            Write-Warning $warnings[-1]
        }

        $auditConfig = [PSCustomObject]@{
            UnifiedAuditLogIngestionEnabled = $unifiedAuditEnabled
            AdminAuditLogAgeLimit           = $adminAuditConfig.AdminAuditLogAgeLimit
            AuditConfigurationPolicies      = $auditPolicies
        }
        Write-Verbose "  Audit config collected. Unified audit enabled: $unifiedAuditEnabled"
    }
    else {
        Write-Verbose "  Audit log configuration collection skipped."
    }
}
catch {
    $warnings.Add("Section 1 (Audit Config) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 2: DLP Compliance Policies
# Supports: Control 1.4 (DLP), sensitive information type enforcement
# Pattern: restrict-agent-publishing.ps1 — DLP connector classification
# ═══════════════════════════════════════════════════════════════════════
$dlpCompliancePolicies = $null
$dlpCollectionSucceeded = $false
try {
    Write-Verbose "Section 2: Collecting DLP compliance policies..."
    $rawDlp = Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'List DLP compliance policies' -ScriptBlock {
        Get-DlpCompliancePolicy -ErrorAction Stop
    }
    $dlpCompliancePolicies = @(
        foreach ($policy in $rawDlp) {
            # Retrieve associated rules with SIT references
            $policyName = Get-PurviewDspmPropertyValue -InputObject $policy -Name @('Name', 'Identity')
            $rules = $null
            try {
                $rules = Invoke-CollectorOperation -Target $policyName -Action 'List DLP compliance rules' -ScriptBlock {
                    Get-DlpComplianceRule -Policy $policyName -ErrorAction Stop
                } | ForEach-Object {
                    [PSCustomObject]@{
                        Name                       = $_.Name
                        Disabled                   = $_.Disabled
                        ContentContainsSensitiveInformation = $_.ContentContainsSensitiveInformation
                        BlockAccess                = $_.BlockAccess
                        Priority                   = $_.Priority
                    }
                }
            }
            catch {
                $warnings.Add("DLP rules for policy '$policyName' failed: $($_.Exception.Message)")
                Write-Warning $warnings[-1]
            }

            [PSCustomObject]@{
                Name              = $policyName
                Mode              = Get-PurviewDspmPropertyValue -InputObject $policy -Name @('Mode')
                Workload          = Get-PurviewDspmPropertyValue -InputObject $policy -Name @('Workload')
                Locations         = Get-PurviewDspmPropertyValue -InputObject $policy -Name @('Locations')
                Location          = Get-PurviewDspmPropertyValue -InputObject $policy -Name @('Location')
                EnforcementPlanes = Get-PurviewDspmPropertyValue -InputObject $policy -Name @('EnforcementPlanes')
                Enabled           = Get-PurviewDspmPropertyValue -InputObject $policy -Name @('Enabled')
                Rules             = $rules
            }
        }
    )
    $dlpCollectionSucceeded = $true
    Write-Verbose "  Collected $(@($dlpCompliancePolicies).Count) DLP compliance policy/policies."
}
catch {
    $warnings.Add("Section 2 (DLP Compliance) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 3: Retention Policies
# Supports: Control 3.2 (Data Retention), Copilot interaction retention
# ═══════════════════════════════════════════════════════════════════════
$retentionPolicies = $null
try {
    Write-Verbose "Section 3: Collecting retention compliance policies..."
    $rawRetention = Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'List retention compliance policies' -ScriptBlock {
        Get-RetentionCompliancePolicy -ErrorAction Stop
    }
    $retentionPolicies = $rawRetention | ForEach-Object {
        $hasCopilotWorkload = $false
        if ($_.Workload) {
            # Check for Copilot-related workload references
            $hasCopilotWorkload = ($_.Workload -match 'Copilot' -or $_.Workload -match 'CopilotInteraction')
        }
        [PSCustomObject]@{
            Name                 = $_.Name
            Enabled              = $_.Enabled
            Mode                 = $_.Mode
            Workload             = $_.Workload
            RetentionDuration    = $_.RetentionDuration
            RetentionAction      = $_.RetentionAction
            CopilotWorkloadFound = $hasCopilotWorkload
        }
    }
    Write-Verbose "  Collected $(@($retentionPolicies).Count) retention policy/policies."
}
catch {
    $warnings.Add("Section 3 (Retention Policies) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 4: Communication Compliance (Supervisory Review)
# Supports: Control 3.3 (Communication Oversight)
# ═══════════════════════════════════════════════════════════════════════
$communicationCompliance = $null
try {
    Write-Verbose "Section 4: Collecting communication compliance policies..."
    $rawComm = Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'List communication compliance policies' -ScriptBlock {
        Get-SupervisoryReviewPolicyV2 -ErrorAction Stop
    }
    $communicationCompliance = $rawComm | ForEach-Object {
        [PSCustomObject]@{
            Name    = $_.Name
            Scope   = $_.RevieweeScope
            Status  = $_.Enabled
        }
    }
    Write-Verbose "  Collected $(@($communicationCompliance).Count) communication compliance policy/policies."
}
catch {
    # This cmdlet may not be available in all tenants (requires E5/compliance add-on)
    $warnings.Add("Section 4 (Communication Compliance) failed or unavailable: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 5: eDiscovery Cases
# Supports: Control 3.4 (eDiscovery Readiness) — check for agent-scoped cases
# ═══════════════════════════════════════════════════════════════════════
$eDiscoveryCases = $null
try {
    Write-Verbose "Section 5: Collecting eDiscovery cases..."
    $rawCases = Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'List eDiscovery cases' -ScriptBlock {
        Get-ComplianceCase -ErrorAction Stop
    }
    $eDiscoveryCases = $rawCases | ForEach-Object {
        $agentScoped = $false
        if ($_.Name -match 'agent|copilot|bot' -or $_.Description -match 'agent|copilot|bot') {
            $agentScoped = $true
        }
        [PSCustomObject]@{
            Name           = $_.Name
            Status         = $_.Status
            CaseType       = $_.CaseType
            CreatedDate    = $_.CreatedDateTime
            AgentScoped    = $agentScoped
        }
    }
    Write-Verbose "  Collected $(@($eDiscoveryCases).Count) eDiscovery case(s)."
}
catch {
    $warnings.Add("Section 5 (eDiscovery Cases) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 6: Insider Risk evidence status (manual policy inventory + audit dependency)
# Supports: Control 1.12 (manual review evidence), Control 3.5 context
# ═══════════════════════════════════════════════════════════════════════
$insiderRiskPolicies = @()
Write-Verbose "Section 6: Evaluating insider risk evidence support..."

$insiderRiskEvidence = New-InsiderRiskEvidence -AuditConfig $auditConfig
$policyInventory = $insiderRiskEvidence.policyInventory
$auditDependency = $insiderRiskEvidence.auditDependency

$warnings.Add("Section 6 (Insider Risk policy inventory) [$($policyInventory.classification)]: $($policyInventory.detail)")
Write-Warning $warnings[-1]

if ($auditDependency.classification -eq 'audit_dependency_not_met') {
    $warnings.Add("Section 6 (Insider Risk audit dependency) [$($auditDependency.classification)]: $($auditDependency.detail)")
    Write-Warning $warnings[-1]
}
elseif ($auditDependency.classification -eq 'unknown') {
    $warnings.Add("Section 6 (Insider Risk audit dependency) [unknown]: $($auditDependency.detail)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 7: DSPM for AI (Data Security Posture Management)
# Supports: Control 1.6 (DSPM for AI) — actively enforced Microsoft 365 Copilot DLP
#
# DSPM for AI does not have a dedicated cmdlet in ExchangeOnlineManagement.
# Control evidence is derived only from DLP policies matching all documented
# New-DlpCompliancePolicy signals for Microsoft 365 Copilot:
#   Workload=Applications
#   Location=470f2276-e011-4e9d-a6ec-20768be3a4b0
#   EnforcementPlanes=CopilotExperiences
# The policy must also be actively enforced. Retention remains informational.
# ═══════════════════════════════════════════════════════════════════════
$dspmForAi = $null
try {
    Write-Verbose 'Section 7: Checking actively enforced Microsoft 365 Copilot DLP policy presence...'

    $copilotRetentionPolicies = @()
    if ($null -ne $retentionPolicies) {
        $copilotRetentionPolicies = @($retentionPolicies | Where-Object {
            $retentionMode = ([string]$_.Mode).Trim().ToLowerInvariant()
            $retentionEnabled = ConvertTo-PurviewDspmBoolean -InputObject $_.Enabled
            $hasCopilotScope = $_.CopilotWorkloadFound -eq $true -or ($_.Workload -match 'CopilotInteraction')
            $hasCopilotScope -and $retentionEnabled -eq $true -and
                $retentionMode -in @('enable', 'enabled', 'enforce', 'enforced')
        })
    }
    $retentionCoverage = $copilotRetentionPolicies.Count -gt 0
    $retentionPolicyNames = @($copilotRetentionPolicies | ForEach-Object { $_.Name })

    $dspmForAi = New-PurviewDspmEvidence `
        -Policies $dlpCompliancePolicies `
        -DlpCollectionSucceeded $dlpCollectionSucceeded `
        -RetentionCoverage $retentionCoverage `
        -RetentionPolicyNames $retentionPolicyNames

    if ($dspmForAi.CollectionStatus -ne 'collected') {
        $warnings.Add("Section 7 (DSPM for AI) unavailable: $($dspmForAi.Note)")
        Write-Warning $warnings[-1]
    }
    elseif (-not $dspmForAi.Detected) {
        $warnings.Add("Section 7 (DSPM for AI): $($dspmForAi.Note)")
        Write-Warning $warnings[-1]
    }
    Write-Verbose "  DSPM for AI check complete. Status: $($dspmForAi.CollectionStatus). Qualifying active policy count: $($dspmForAi.PolicyCount)."
}
catch {
    $warnings.Add("Section 7 (DSPM for AI) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 8: Sensitivity Label Policies
# Supports: Control 1.25 (Information Protection), label governance
# ═══════════════════════════════════════════════════════════════════════
$sensitivityLabelPolicies = $null
try {
    Write-Verbose "Section 8: Collecting sensitivity label policies..."
    $rawLabels = Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'List sensitivity label policies' -ScriptBlock {
        Get-LabelPolicy -ErrorAction Stop
    }
    $sensitivityLabelPolicies = $rawLabels | ForEach-Object {
        [PSCustomObject]@{
            Name             = $_.Name
            Enabled          = $_.Enabled
            Mode             = $_.Mode
            Labels           = $_.Labels
            ExchangeLocation = $_.ExchangeLocation
            Comment          = $_.Comment
        }
    }
    Write-Verbose "  Collected $(@($sensitivityLabelPolicies).Count) sensitivity label policy/policies."
}
catch {
    $warnings.Add("Section 8 (Sensitivity Labels) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Section 9: Endpoint DLP
# Supports: Control 1.4 (DLP) — endpoint workload coverage
# ═══════════════════════════════════════════════════════════════════════
$endpointDlp = $null
try {
    Write-Verbose "Section 9: Collecting endpoint DLP policies..."
    if ($dlpCompliancePolicies) {
        # Filter for policies targeting Endpoint workload
        $endpointDlp = @($dlpCompliancePolicies | Where-Object {
            $_.Workload -match 'Endpoint' -or $_.Workload -match 'EndpointDevices'
        })
        if ($endpointDlp.Count -eq 0) {
            $endpointDlp = @{ Detected = $false; Note = 'No DLP policies targeting Endpoint workload found.' }
            $warnings.Add("Section 9 (Endpoint DLP): No endpoint-targeted DLP policies found.")
            Write-Warning $warnings[-1]
        }
    }
    else {
        # If DLP collection failed earlier, attempt a direct query
        $rawEndpoint = Invoke-CollectorOperation -Target "Purview tenant $TenantId" -Action 'List endpoint DLP policies' -ScriptBlock {
            Get-DlpCompliancePolicy -ErrorAction Stop
        } | Where-Object {
            $_.Workload -match 'Endpoint' -or $_.Workload -match 'EndpointDevices'
        }
        $endpointDlp = $rawEndpoint | ForEach-Object {
            [PSCustomObject]@{
                Name     = $_.Name
                Mode     = $_.Mode
                Workload = $_.Workload
                Enabled  = $_.Enabled
            }
        }
    }
    Write-Verbose "  Endpoint DLP collection complete."
}
catch {
    $warnings.Add("Section 9 (Endpoint DLP) failed: $($_.Exception.Message)")
    Write-Warning $warnings[-1]
}

# ═══════════════════════════════════════════════════════════════════════
# Build Output
# ═══════════════════════════════════════════════════════════════════════
$result = [ordered]@{
    auditConfig              = $auditConfig
    dlpCompliancePolicies    = $dlpCompliancePolicies
    retentionPolicies        = $retentionPolicies
    communicationCompliance  = $communicationCompliance
    eDiscoveryCases          = $eDiscoveryCases
    insiderRiskPolicies      = $insiderRiskPolicies
    insiderRiskEvidence      = $insiderRiskEvidence
    dspmForAi                = $dspmForAi
    sensitivityLabelPolicies = $sensitivityLabelPolicies
    endpointDlp              = $endpointDlp
    _metadata                = [ordered]@{
        collector   = 'Collect-Purview'
        timestamp   = (Get-Date -Format 'o')
        tenant_id   = $TenantId
        warnings    = @($warnings)
    }
}

$json = $result | ConvertTo-Json -Depth 10
$json | Out-File -FilePath $outputFile -Encoding utf8
Write-Verbose "Output written to $outputFile"

# ─── Exit Code ───────────────────────────────────────────────────────
$sectionValues = @(
    $auditConfig, $dlpCompliancePolicies, $retentionPolicies,
    $communicationCompliance, $eDiscoveryCases, $insiderRiskEvidence,
    $dspmForAi, $sensitivityLabelPolicies, $endpointDlp
)
$nullSections = @($sectionValues | Where-Object { $null -eq $_ })

if ($nullSections.Count -eq $sectionValues.Count) {
    Write-Error "All sections failed to collect data. See warnings for details."
    exit 2
}
elseif ($nullSections.Count -gt 0) {
    Write-Warning "Partial collection: $($nullSections.Count)/$($sectionValues.Count) sections returned null."
    exit 1
}
else {
    Write-Verbose "All sections collected successfully."
    exit 0
}
