# Control 1.29 — PowerShell Setup: Global Secure Access Network Controls

**Playbook Type:** PowerShell Setup
**Control:** 1.29 — Global Secure Access: Network Controls for Copilot Studio Agents
**Audience:** Platform Engineers, Security Engineers, Power Platform CoE
**Estimated Duration:** 30–60 minutes for initial setup; scripts can run in minutes once configured
**Prerequisites:** Power Platform PowerShell modules, Microsoft Graph PowerShell SDK, Global Secure Access license, appropriate admin roles

!!! warning "Preview Feature"
    This is a preview feature. Preview features aren't meant for production use and may have restricted functionality. Features may change before becoming generally available. Subject to the [Microsoft Azure Preview Supplemental Terms of Use](https://azure.microsoft.com/en-us/support/legal/preview-supplemental-terms/). API endpoints, module cmdlet names, and parameter structures may change during the preview period. Pin module versions and validate against current documentation before executing in production pipelines.

!!! note "Portal Walkthrough Prerequisite"
    Complete [Portal Walkthrough](portal-walkthrough.md) Phase 2–4 first (create the three filtering policies in Entra admin center). The PowerShell scripts in this playbook primarily automate GSA forwarding enablement across environments and audit/reporting tasks. Policy creation for the filtering types currently requires portal-based configuration or Microsoft Graph API calls. Both approaches are documented below.

---

## Module Installation and Authentication

### Required Modules

```powershell
# Install required PowerShell modules
# Run in an elevated PowerShell session

# Power Platform Admin module — for environment management and GSA forwarding toggle
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force -AllowClobber

# Microsoft Graph PowerShell SDK — for Entra / GSA policy management and log queries
Install-Module -Name Microsoft.Graph -Scope CurrentUser -Force -AllowClobber

# Import modules for current session
Import-Module Microsoft.PowerApps.Administration.PowerShell
Import-Module Microsoft.Graph.Identity.SignIns
Import-Module Microsoft.Graph.Reports
```

### Authentication Setup

```powershell
# ── Authentication ────────────────────────────────────────────────────────────
# Authenticate to Power Platform
# Requires Power Platform admin role
Add-PowerAppsAccount -Endpoint prod

# Authenticate to Microsoft Graph
# Requires Security Administrator role (for GSA policy management)
# Required scopes:
#   Policy.ReadWrite.ConditionalAccess  — for GSA policy linking
#   NetworkAccess.ReadWrite.All         — for Global Secure Access configuration
#   AuditLog.Read.All                   — for traffic log queries
Connect-MgGraph -Scopes `
    "Policy.ReadWrite.ConditionalAccess",
    "NetworkAccess.ReadWrite.All",
    "AuditLog.Read.All",
    "Directory.Read.All"

# Verify connection
Get-MgContext | Select-Object -Property Account, TenantId, Scopes
```

!!! info "Service Principal Authentication for CI/CD"
    For automated pipelines (e.g., Azure DevOps, GitHub Actions), use certificate-based service principal authentication rather than interactive login. The service principal requires the same Graph permission scopes listed above, granted as Application permissions (not delegated). Store the certificate or client secret in Azure Key Vault; never in pipeline YAML or scripts committed to source control.

```powershell
# Service principal authentication example (for pipelines)
$TenantId     = $env:AZURE_TENANT_ID
$ClientId     = $env:AZURE_CLIENT_ID
$CertThumb    = $env:AZURE_CERT_THUMBPRINT

Connect-MgGraph -TenantId $TenantId -ClientId $ClientId -CertificateThumbprint $CertThumb
```

---

## Script 1: Inventory Environments and GSA Forwarding Status

Run this script first to establish a baseline inventory of all environments and their current GSA forwarding state before making changes.

```powershell
# ── Script 1: GSA Forwarding Status Inventory ─────────────────────────────────
# Queries all Power Platform environments and reports GSA forwarding state
# Output: CSV report suitable for audit evidence and change tracking
# Role required: Power Platform admin

[CmdletBinding()]
param(
    [string]$OutputPath = ".\GSA-Inventory-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
)

Write-Host "Retrieving Power Platform environment list..." -ForegroundColor Cyan

# Retrieve all environments
$environments = Get-AdminPowerAppEnvironment -ErrorAction Stop

$report = @()

foreach ($env in $environments) {
    Write-Host "  Processing: $($env.DisplayName) [$($env.EnvironmentName)]" -ForegroundColor Gray

    # Retrieve environment settings to check GSA forwarding state
    # Note: GSA forwarding setting retrieval may require direct API call
    # depending on module version — see API fallback below
    try {
        $envDetail = Get-AdminPowerAppEnvironment -EnvironmentName $env.EnvironmentName

        # Attempt to read GSA forwarding property
        # Property name may vary by module version during preview
        $gsaEnabled = $null
        if ($envDetail.Internal.properties.PSObject.Properties.Name -contains "globalSecureAccessEnabled") {
            $gsaEnabled = $envDetail.Internal.properties.globalSecureAccessEnabled
        } elseif ($envDetail.Internal.properties.PSObject.Properties.Name -contains "networkSecurityGroupId") {
            # Alternative property path — check current module documentation
            $gsaEnabled = "Check manually — property path varies"
        } else {
            $gsaEnabled = "Not determined — verify in PPAC"
        }
    } catch {
        $gsaEnabled = "Error: $($_.Exception.Message)"
    }

    $report += [PSCustomObject]@{
        EnvironmentName   = $env.EnvironmentName
        DisplayName       = $env.DisplayName
        EnvironmentType   = $env.EnvironmentType
        Region            = $env.Location
        CreatedTime       = $env.Internal.properties.createdTime
        GSAForwardingState = $gsaEnabled
        ReportDate        = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
        ReviewedBy        = $env:USERNAME
    }
}

# Export to CSV
$report | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8

Write-Host "`nInventory complete. $($report.Count) environments processed." -ForegroundColor Green
Write-Host "Report saved to: $OutputPath" -ForegroundColor Green

# Display summary
$report | Format-Table DisplayName, EnvironmentType, GSAForwardingState -AutoSize
```

---

## Script 2: Enable GSA Forwarding for Multiple Environments

Use this script to enable GSA forwarding across multiple environments in bulk. This is the primary automation for Zone 2 and Zone 3 rollout.

```powershell
# ── Script 2: Enable GSA Forwarding via Power Platform REST API ────────────────
# Enables GSA agent traffic forwarding for specified environments
# Uses Power Platform admin API directly (most reliable during preview period)
# Role required: Power Platform admin

[CmdletBinding(SupportsShouldProcess)]
param(
    # Provide a list of environment IDs, or leave empty to process from CSV
    [string[]]$EnvironmentIds,

    # Path to CSV file with EnvironmentName column (output from Script 1)
    [string]$EnvironmentCsvPath,

    # Zone classification for documentation purposes
    [ValidateSet("Zone1", "Zone2", "Zone3")]
    [string]$ZoneClassification = "Zone2",

    # Set to $true to actually apply changes; $false for dry run
    [bool]$Apply = $false
)

# ── Authenticate to Power Platform API ────────────────────────────────────────
$ppacToken = (Get-PowerAppsAccount).Token
$ppacBaseUrl = "https://api.bap.microsoft.com"

# ── Build environment list ─────────────────────────────────────────────────────
$targetEnvironments = @()

if ($EnvironmentIds) {
    $targetEnvironments = $EnvironmentIds
} elseif ($EnvironmentCsvPath) {
    $csv = Import-Csv -Path $EnvironmentCsvPath
    $targetEnvironments = $csv | Select-Object -ExpandProperty EnvironmentName
} else {
    Write-Error "Provide either -EnvironmentIds or -EnvironmentCsvPath"
    exit 1
}

Write-Host "Target environments: $($targetEnvironments.Count)" -ForegroundColor Cyan
Write-Host "Zone classification: $ZoneClassification" -ForegroundColor Cyan
Write-Host "Apply mode: $Apply" -ForegroundColor $(if ($Apply) { "Yellow" } else { "Green" })

$results = @()

foreach ($envId in $targetEnvironments) {
    Write-Host "`nProcessing environment: $envId" -ForegroundColor Gray

    if ($Apply) {
        if ($PSCmdlet.ShouldProcess($envId, "Enable GSA forwarding")) {
            try {
                # Power Platform API call to enable GSA forwarding
                # Endpoint and body structure — verify against current API docs
                $apiUrl = "$ppacBaseUrl/providers/Microsoft.BusinessAppPlatform/environments/$envId" +
                          "?api-version=2021-04-01"

                $body = @{
                    properties = @{
                        globalSecureAccess = @{
                            enabled = $true
                        }
                    }
                } | ConvertTo-Json -Depth 5

                $headers = @{
                    Authorization  = "Bearer $ppacToken"
                    "Content-Type" = "application/json"
                }

                $response = Invoke-RestMethod -Uri $apiUrl -Method Patch `
                    -Headers $headers -Body $body -ErrorAction Stop

                $status = "Enabled"
                $errorMsg = $null
                Write-Host "  [OK] GSA forwarding enabled for $envId" -ForegroundColor Green

            } catch {
                $status = "Error"
                $errorMsg = $_.Exception.Message
                Write-Host "  [FAIL] $envId — $errorMsg" -ForegroundColor Red
            }
        }
    } else {
        # Dry run — report what would be done
        $status = "DryRun-WouldEnable"
        $errorMsg = $null
        Write-Host "  [DRY RUN] Would enable GSA forwarding for $envId" -ForegroundColor Yellow
    }

    $results += [PSCustomObject]@{
        EnvironmentId    = $envId
        ZoneClassification = $ZoneClassification
        Action           = if ($Apply) { "Enable-GSA-Forwarding" } else { "DryRun" }
        Status           = $status
        Error            = $errorMsg
        Timestamp        = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
        ExecutedBy       = $env:USERNAME
    }
}

# Output results
$outputPath = ".\GSA-Enablement-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
$results | Export-Csv -Path $outputPath -NoTypeInformation -Encoding UTF8

Write-Host "`nCompleted. Results saved to: $outputPath" -ForegroundColor Green
$results | Format-Table EnvironmentId, Status, Error -AutoSize
```

!!! warning "API Endpoint Validation"
    The Power Platform REST API endpoint for enabling GSA forwarding may differ from the example above during the preview period. Validate against [https://learn.microsoft.com/en-us/power-platform/admin/api-overview](https://learn.microsoft.com/en-us/power-platform/admin/api-overview) before running in production. If the API call fails, fall back to the portal-based toggle described in the [Portal Walkthrough](portal-walkthrough.md).

---

## Script 3: Query GSA Traffic Logs for Agent Events

This script retrieves GSA traffic log entries filtered for agent-originated traffic, for use in periodic review and audit evidence generation.

```powershell
# ── Script 3: Query GSA Traffic Logs for Agent Events ─────────────────────────
# Retrieves Global Secure Access traffic logs filtered for agent traffic
# Uses Microsoft Graph networkAccess/logs endpoint
# Role required: Security Reader or Security Administrator

[CmdletBinding()]
param(
    # Number of hours back to query (default: 24 hours for daily review)
    [int]$HoursBack = 24,

    # Filter for blocked events only ($true = blocked only, $false = all events)
    [bool]$BlockedOnly = $false,

    # Output CSV path
    [string]$OutputPath = ".\GSA-AgentLogs-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv",

    # Maximum number of log entries to retrieve
    [int]$MaxRecords = 5000
)

Write-Host "Querying GSA traffic logs..." -ForegroundColor Cyan
Write-Host "  Time range: Last $HoursBack hours" -ForegroundColor Gray
Write-Host "  Blocked only: $BlockedOnly" -ForegroundColor Gray

# Build the filter timestamp
$startTime = (Get-Date).AddHours(-$HoursBack).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

# Build OData filter string
# Note: filter property names are based on the networkAccess logs schema — verify against current docs
$filterParts = @("createdDateTime ge $startTime")

if ($BlockedOnly) {
    $filterParts += "action eq 'block'"
}

# Agent-specific filter — traffic type property name may vary during preview
# Use "trafficType eq 'agent'" or equivalent per current schema
$filterParts += "trafficType eq 'agent'"

$odataFilter = $filterParts -join " and "

try {
    # Query Microsoft Graph for GSA traffic logs
    # Endpoint: GET /beta/networkAccess/logs/traffic
    $graphUrl = "https://graph.microsoft.com/beta/networkAccess/logs/traffic" +
                "?`$filter=$([System.Uri]::EscapeDataString($odataFilter))" +
                "&`$top=$MaxRecords" +
                "&`$orderby=createdDateTime desc"

    Write-Host "  Graph query: $graphUrl" -ForegroundColor Gray

    $response = Invoke-MgGraphRequest -Uri $graphUrl -Method GET -ErrorAction Stop

    $logEntries = $response.value

    if ($null -eq $logEntries -or $logEntries.Count -eq 0) {
        Write-Host "No log entries found for the specified filter." -ForegroundColor Yellow
        Write-Host "  This may indicate: GSA forwarding not yet active, propagation delay, or no agent traffic in the time window." -ForegroundColor Yellow
        exit 0
    }

    Write-Host "  Retrieved $($logEntries.Count) log entries." -ForegroundColor Green

    # Normalize log entries for export
    $normalizedLogs = $logEntries | ForEach-Object {
        [PSCustomObject]@{
            Timestamp            = $_.createdDateTime
            TrafficType          = $_.trafficType
            Action               = $_.action
            DestinationFQDN      = $_.destinationFqdn
            DestinationIP        = $_.destinationIp
            DestinationPort      = $_.destinationPort
            PolicyName           = $_.policyName
            PolicyRuleId         = $_.policyRuleId
            SourceEnvironmentId  = $_.sourceEnvironmentId
            AgentId              = $_.agentId
            TransactionId        = $_.transactionId
            BytesSent            = $_.bytesSent
            BytesReceived        = $_.bytesReceived
            Protocol             = $_.protocol
        }
    }

    # Export to CSV
    $normalizedLogs | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
    Write-Host "Log export saved to: $OutputPath" -ForegroundColor Green

    # Summary statistics
    $blockedCount = ($normalizedLogs | Where-Object { $_.Action -eq 'block' }).Count
    $allowedCount = ($normalizedLogs | Where-Object { $_.Action -eq 'allow' }).Count
    $uniqueDestinations = ($normalizedLogs | Select-Object -ExpandProperty DestinationFQDN -Unique).Count

    Write-Host "`nSummary:" -ForegroundColor Cyan
    Write-Host "  Total entries  : $($normalizedLogs.Count)"
    Write-Host "  Allowed        : $allowedCount"
    Write-Host "  Blocked        : $blockedCount"
    Write-Host "  Unique destinations: $uniqueDestinations"

    # Show blocked entries inline for quick review
    if ($blockedCount -gt 0) {
        Write-Host "`nBlocked Requests (top 20):" -ForegroundColor Yellow
        $normalizedLogs | Where-Object { $_.Action -eq 'block' } |
            Select-Object -First 20 |
            Format-Table Timestamp, DestinationFQDN, PolicyName, AgentId -AutoSize
    }

} catch {
    Write-Error "Failed to query GSA traffic logs: $($_.Exception.Message)"
    Write-Host "Verify Graph connection and required scopes (AuditLog.Read.All, NetworkAccess.ReadWrite.All)" -ForegroundColor Yellow
    exit 1
}
```

---

## Script 4: Export GSA Configuration as Audit Evidence

This script produces a structured audit evidence export documenting the current GSA configuration state for FINRA/SEC examination packages or SOX ITGC evidence files.

```powershell
# ── Script 4: GSA Configuration Audit Evidence Export ─────────────────────────
# Exports GSA configuration state as a structured JSON + CSV audit evidence package
# Output suitable for FINRA examination evidence, SOX ITGC documentation
# Role required: Security Reader or Security Administrator

[CmdletBinding()]
param(
    [string]$OutputDirectory = ".\GSA-AuditEvidence-$(Get-Date -Format 'yyyyMMdd')",
    [string]$ReviewerName    = $env:USERNAME,
    [string]$ReviewPurpose   = "Routine compliance evidence — Control 1.29"
)

# Create output directory
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
Write-Host "Audit evidence export starting..." -ForegroundColor Cyan
Write-Host "  Output directory: $OutputDirectory" -ForegroundColor Gray

$evidencePackage = [ordered]@{
    ExportMetadata = @{
        ControlId        = "1.29"
        ControlTitle     = "Global Secure Access: Network Controls for Copilot Studio Agents"
        Framework        = "FSI-AgentGov"
        ExportTimestamp  = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
        ExportedBy       = $ReviewerName
        ReviewPurpose    = $ReviewPurpose
        TenantId         = (Get-MgContext).TenantId
    }
    BaselineProfile  = $null
    WebContentFilterPolicies = @()
    ThreatIntelligenceConfig = $null
    NetworkFileFilterPolicies = @()
    EnvironmentForwardingState = @()
}

# ── 1. Retrieve GSA Baseline Profile ──────────────────────────────────────────
Write-Host "  Retrieving baseline profile..." -ForegroundColor Gray
try {
    $baselineProfile = Invoke-MgGraphRequest `
        -Uri "https://graph.microsoft.com/beta/networkAccess/forwardingProfiles" `
        -Method GET -ErrorAction Stop
    $evidencePackage.BaselineProfile = $baselineProfile.value | Where-Object { $_.profileType -eq "baseline" }
    Write-Host "  [OK] Baseline profile retrieved." -ForegroundColor Green
} catch {
    Write-Warning "  Could not retrieve baseline profile: $($_.Exception.Message)"
}

# ── 2. Retrieve Web Content Filtering Policies ────────────────────────────────
Write-Host "  Retrieving web content filtering policies..." -ForegroundColor Gray
try {
    $wcfPolicies = Invoke-MgGraphRequest `
        -Uri "https://graph.microsoft.com/beta/networkAccess/filteringPolicies?`$filter=policyType eq 'webContentFiltering'" `
        -Method GET -ErrorAction Stop
    $evidencePackage.WebContentFilterPolicies = $wcfPolicies.value
    Write-Host "  [OK] $($wcfPolicies.value.Count) web content filtering policy/policies retrieved." -ForegroundColor Green
} catch {
    Write-Warning "  Could not retrieve web content filtering policies: $($_.Exception.Message)"
}

# ── 3. Retrieve Threat Intelligence Configuration ─────────────────────────────
Write-Host "  Retrieving threat intelligence configuration..." -ForegroundColor Gray
try {
    $threatIntel = Invoke-MgGraphRequest `
        -Uri "https://graph.microsoft.com/beta/networkAccess/filteringPolicies?`$filter=policyType eq 'threatIntelligence'" `
        -Method GET -ErrorAction Stop
    $evidencePackage.ThreatIntelligenceConfig = $threatIntel.value
    Write-Host "  [OK] Threat intelligence configuration retrieved." -ForegroundColor Green
} catch {
    Write-Warning "  Could not retrieve threat intelligence config: $($_.Exception.Message)"
}

# ── 4. Retrieve Network File Filtering Policies ───────────────────────────────
Write-Host "  Retrieving network file filtering policies..." -ForegroundColor Gray
try {
    $nffPolicies = Invoke-MgGraphRequest `
        -Uri "https://graph.microsoft.com/beta/networkAccess/filteringPolicies?`$filter=policyType eq 'networkFileFiltering'" `
        -Method GET -ErrorAction Stop
    $evidencePackage.NetworkFileFilterPolicies = $nffPolicies.value
    Write-Host "  [OK] $($nffPolicies.value.Count) network file filtering policy/policies retrieved." -ForegroundColor Green
} catch {
    Write-Warning "  Could not retrieve network file filtering policies: $($_.Exception.Message)"
}

# ── 5. Retrieve Power Platform Environment Forwarding States ──────────────────
Write-Host "  Retrieving environment GSA forwarding states..." -ForegroundColor Gray
try {
    $allEnvs = Get-AdminPowerAppEnvironment -ErrorAction Stop
    $envForwardingList = $allEnvs | ForEach-Object {
        [PSCustomObject]@{
            EnvironmentId   = $_.EnvironmentName
            DisplayName     = $_.DisplayName
            EnvironmentType = $_.EnvironmentType
            Region          = $_.Location
            # GSA state retrieval — property path varies by module version
            GSAForwarding   = "Verify in PPAC — see portal-walkthrough.md Phase 6"
        }
    }
    $evidencePackage.EnvironmentForwardingState = $envForwardingList
    Write-Host "  [OK] $($allEnvs.Count) environments retrieved." -ForegroundColor Green
} catch {
    Write-Warning "  Could not retrieve environments: $($_.Exception.Message)"
}

# ── Export JSON evidence file ──────────────────────────────────────────────────
$jsonPath = Join-Path $OutputDirectory "gsa-config-evidence.json"
$evidencePackage | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding UTF8
Write-Host "  JSON evidence: $jsonPath" -ForegroundColor Green

# ── Export environment state CSV ───────────────────────────────────────────────
$csvPath = Join-Path $OutputDirectory "environment-forwarding-state.csv"
$evidencePackage.EnvironmentForwardingState | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8
Write-Host "  Environment CSV: $csvPath" -ForegroundColor Green

# ── Write evidence cover note ─────────────────────────────────────────────────
$coverNotePath = Join-Path $OutputDirectory "evidence-cover-note.txt"
@"
FSI-AgentGov Control 1.29 — Audit Evidence Package
===================================================
Control Title  : Global Secure Access: Network Controls for Copilot Studio Agents
Export Date    : $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
Exported By    : $ReviewerName
Purpose        : $ReviewPurpose
Tenant ID      : $((Get-MgContext).TenantId)

Files Included:
  gsa-config-evidence.json          — Full GSA policy configuration export
  environment-forwarding-state.csv  — Power Platform environment GSA forwarding states

Regulatory References:
  GLBA 501(b) — Safeguards Rule: system security controls
  FINRA 4511  — General requirements: system security records
  OCC 2011-12 — Technology Risk Management
  SOX 302/404 — IT General Controls evidence

Notes:
  - This evidence package documents the GSA configuration state at time of export.
  - GSA forwarding states for individual environments should be verified in
    Power Platform admin center (portal walkthrough Phase 6) as API retrieval
    may be limited during preview.
  - Log evidence for specific periods should be generated separately using
    Script 3 (GSA traffic log export).
  - Retain this package per organizational records retention schedule.
"@ | Out-File -FilePath $coverNotePath -Encoding UTF8

Write-Host "`nAudit evidence package complete: $OutputDirectory" -ForegroundColor Green
```

---

## Script 5: Validate GSA Configuration Completeness

Use this script as a pre-examination readiness check to verify all required configuration elements are in place.

```powershell
# ── Script 5: GSA Configuration Completeness Validation ──────────────────────
# Validates that all required GSA elements are configured per Control 1.29
# Output: Pass/Fail checklist suitable for internal audit review
# Role required: Security Reader or Security Administrator

Write-Host "Control 1.29 — GSA Configuration Validation" -ForegroundColor Cyan
Write-Host "=" * 60

$checks = @()

# Check 1: Baseline profile exists
try {
    $profiles = Invoke-MgGraphRequest `
        -Uri "https://graph.microsoft.com/beta/networkAccess/forwardingProfiles" -Method GET
    $baseline = $profiles.value | Where-Object { $_.profileType -eq "baseline" }
    $checks += [PSCustomObject]@{
        Check  = "GSA baseline profile exists"
        Status = if ($baseline) { "PASS" } else { "FAIL" }
        Detail = if ($baseline) { "Profile: $($baseline.displayName)" } else { "No baseline profile found" }
    }
} catch {
    $checks += [PSCustomObject]@{ Check = "GSA baseline profile exists"; Status = "ERROR"; Detail = $_.Exception.Message }
}

# Check 2: Web content filtering policy linked to baseline
try {
    $wcfPolicies = Invoke-MgGraphRequest `
        -Uri "https://graph.microsoft.com/beta/networkAccess/filteringPolicies?`$filter=policyType eq 'webContentFiltering'" -Method GET
    $activePolicies = $wcfPolicies.value | Where-Object { $_.state -eq "enabled" }
    $checks += [PSCustomObject]@{
        Check  = "Web content filtering policy (enabled)"
        Status = if ($activePolicies.Count -gt 0) { "PASS" } else { "FAIL" }
        Detail = "$($activePolicies.Count) enabled policy/policies found"
    }
} catch {
    $checks += [PSCustomObject]@{ Check = "Web content filtering policy"; Status = "ERROR"; Detail = $_.Exception.Message }
}

# Check 3: Threat intelligence filtering active
try {
    $tiPolicies = Invoke-MgGraphRequest `
        -Uri "https://graph.microsoft.com/beta/networkAccess/filteringPolicies?`$filter=policyType eq 'threatIntelligence'" -Method GET
    $activeTI = $tiPolicies.value | Where-Object { $_.state -eq "enabled" -and $_.action -eq "block" }
    $checks += [PSCustomObject]@{
        Check  = "Threat intelligence filtering (enabled + block action)"
        Status = if ($activeTI.Count -gt 0) { "PASS" } else { "FAIL" }
        Detail = "$($activeTI.Count) active block policy/policies found"
    }
} catch {
    $checks += [PSCustomObject]@{ Check = "Threat intelligence filtering"; Status = "ERROR"; Detail = $_.Exception.Message }
}

# Check 4: Network file filtering policy linked
try {
    $nffPolicies = Invoke-MgGraphRequest `
        -Uri "https://graph.microsoft.com/beta/networkAccess/filteringPolicies?`$filter=policyType eq 'networkFileFiltering'" -Method GET
    $activeNFF = $nffPolicies.value | Where-Object { $_.state -eq "enabled" }
    $checks += [PSCustomObject]@{
        Check  = "Network file filtering policy (enabled)"
        Status = if ($activeNFF.Count -gt 0) { "PASS" } else { "FAIL" }
        Detail = "$($activeNFF.Count) enabled policy/policies found"
    }
} catch {
    $checks += [PSCustomObject]@{ Check = "Network file filtering policy"; Status = "ERROR"; Detail = $_.Exception.Message }
}

# Output results
Write-Host "`nValidation Results:" -ForegroundColor Cyan
$checks | Format-Table Check, Status, Detail -AutoSize

$failCount  = ($checks | Where-Object { $_.Status -eq "FAIL" }).Count
$errorCount = ($checks | Where-Object { $_.Status -eq "ERROR" }).Count

if ($failCount -eq 0 -and $errorCount -eq 0) {
    Write-Host "All checks passed. GSA configuration aligns with Control 1.29 requirements." -ForegroundColor Green
} else {
    Write-Host "$failCount check(s) FAILED, $errorCount check(s) ERROR." -ForegroundColor Red
    Write-Host "Remediate failures before declaring compliance. See portal-walkthrough.md for configuration steps." -ForegroundColor Yellow
}

# Export validation result
$validationPath = ".\GSA-Validation-$(Get-Date -Format 'yyyyMMdd-HHmmss').csv"
$checks | Export-Csv -Path $validationPath -NoTypeInformation -Encoding UTF8
Write-Host "Validation record saved to: $validationPath" -ForegroundColor Gray
```

---

## Quick Reference: Key Cmdlets and Endpoints

| Task | Approach | Notes |
|---|---|---|
| List all environments | `Get-AdminPowerAppEnvironment` | Power Platform admin module |
| Enable GSA forwarding | `Invoke-RestMethod` — Power Platform admin REST API | Portal fallback if API unavailable during preview |
| List GSA filtering policies | `Invoke-MgGraphRequest` — `/beta/networkAccess/filteringPolicies` | Graph beta endpoint — subject to change |
| Query traffic logs | `Invoke-MgGraphRequest` — `/beta/networkAccess/logs/traffic` | Requires AuditLog.Read.All scope |
| Get baseline profile | `Invoke-MgGraphRequest` — `/beta/networkAccess/forwardingProfiles` | Filter for profileType eq 'baseline' |

---

[Back to Control 1.29](../../../controls/pillar-1-security/1.29-global-secure-access-network-controls.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: March 2026 | Version: v1.3*
