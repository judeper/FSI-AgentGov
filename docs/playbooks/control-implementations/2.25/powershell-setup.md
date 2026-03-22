# Control 2.25: Microsoft Agent 365 — Admin Center Governance Console — PowerShell Setup

This playbook provides PowerShell and Microsoft Graph API automation scripts for Control 2.25. These scripts support recurring governance operations — Frontier enrollment verification, agent inventory export, pending request monitoring, and ownerless agent detection — that must run on a scheduled cadence in financial services environments to meet FINRA supervision, SEC recordkeeping, and OCC technology risk management requirements.

!!! info "Frontier Preview — Graph API Availability"
    The Microsoft Graph API endpoints for Agent 365 are in preview as of March 2026. Preview endpoints use the `/beta` Graph path and are subject to breaking changes before General Availability (May 1, 2026). Do not use `/beta` endpoints in production automation pipelines without a change management plan to migrate to `/v1.0` endpoints at GA. All scripts in this playbook use the beta endpoint and are clearly labeled.

!!! warning "Permissions Required"
    The automation patterns in this playbook require one or more of the following Microsoft Graph API permissions depending on the operation. Grant these permissions to a dedicated service principal — do not use a user account for scheduled automation. Document the service principal in your privileged access inventory per OCC 2011-12.

    - `AgentApp.Read.All` — Read agent registry and metrics
    - `AgentApp.ReadWrite.All` — Manage agent lifecycle (approve, assign owner)
    - `Directory.Read.All` — Read Entra directory for owner validation
    - `Reports.Read.All` — Access usage and analytics data

## Prerequisites

- PowerShell 7.2 or later (cross-platform; recommended for CI/CD pipeline use)
- Microsoft Graph PowerShell SDK: `Install-Module Microsoft.Graph -Scope AllUsers`
- Service principal (app registration) with appropriate Graph API permissions and admin consent granted
- Client certificate or client secret stored in Azure Key Vault (never hardcoded in scripts)
- Output storage path configured (local compliance repository or Azure Blob Storage with immutability policy)
- Change management ticket open for initial automation deployment (per Control 2.3)

## Module Installation and Connection

```powershell
# Install Microsoft Graph PowerShell SDK (run once as admin)
Install-Module Microsoft.Graph -Scope AllUsers -Force

# Connect using a service principal with certificate authentication
# Store certificate thumbprint and tenant/client IDs in environment variables or Key Vault
# Never hardcode credentials in scripts

$TenantId     = $env:AZURE_TENANT_ID
$ClientId     = $env:AZURE_CLIENT_ID
$CertThumb    = $env:AZURE_CERT_THUMBPRINT

Connect-MgGraph `
    -TenantId $TenantId `
    -ClientId $ClientId `
    -CertificateThumbprint $CertThumb `
    -Scopes "AgentApp.Read.All","Directory.Read.All","Reports.Read.All"

Write-Host "Connected to Microsoft Graph for tenant: $TenantId"
```

## Script 1: Verify Frontier Enrollment Status

This script confirms that Copilot Frontier is enabled and that Agent 365 Frontier licenses are provisioned. Run this as a prerequisite check before any Agent 365 governance automation. For scheduled runs, execute weekly and alert if enrollment status changes (e.g., Frontier accidentally disabled).

```powershell
#Requires -Modules Microsoft.Graph.Identity.SignIns

<#
.SYNOPSIS
    Verifies Copilot Frontier enrollment status and Agent 365 license provisioning.
.DESCRIPTION
    Queries the Microsoft Graph API (beta) for Frontier enrollment state and confirms
    the expected Agent 365 Frontier license count. Outputs a structured result for
    use in governance reports and automated alerting pipelines.
.NOTES
    Graph endpoint: /beta — Subject to change at GA (May 1, 2026).
    Regulatory purpose: OCC 2011-12 — Technology risk management control verification.
#>

function Get-FrontierEnrollmentStatus {
    [CmdletBinding()]
    param (
        [Parameter()]
        [int]$ExpectedFrontierLicenseCount = 25
    )

    $result = [PSCustomObject]@{
        CheckDate                = (Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
        FrontierEnabled          = $false
        Agent365LicenseCount     = 0
        Agent365LicensesAssigned = 0
        EnrollmentHealthy        = $false
        Notes                    = ""
    }

    try {
        # Check Frontier enrollment via admin settings (beta endpoint)
        $frontierSettings = Invoke-MgGraphRequest `
            -Method GET `
            -Uri "https://graph.microsoft.com/beta/admin/microsoft365Apps/installation/appCatalogConfiguration" `
            -ErrorAction Stop

        $result.FrontierEnabled = $true  # If the call succeeds, Frontier is accessible

        # Query subscribed SKUs to confirm Agent 365 Frontier license availability
        $skus = Get-MgSubscribedSku -All

        $agent365Sku = $skus | Where-Object {
            $_.SkuPartNumber -like "*AGENT365*" -or $_.ServicePlans.ServicePlanName -like "*Agent365*"
        }

        if ($agent365Sku) {
            $result.Agent365LicenseCount     = $agent365Sku.PrepaidUnits.Enabled
            $result.Agent365LicensesAssigned = $agent365Sku.ConsumedUnits
            $result.EnrollmentHealthy        = ($result.Agent365LicenseCount -ge $ExpectedFrontierLicenseCount)
        } else {
            $result.Notes = "Agent 365 Frontier SKU not found in subscribed licenses. Verify Frontier enrollment in admin center."
            $result.EnrollmentHealthy = $false
        }
    }
    catch {
        $result.FrontierEnabled   = $false
        $result.EnrollmentHealthy = $false
        $result.Notes             = "Graph API call failed: $($_.Exception.Message). Verify Frontier enrollment and service principal permissions."
    }

    return $result
}

# Execute and output
$enrollmentStatus = Get-FrontierEnrollmentStatus -ExpectedFrontierLicenseCount 25
$enrollmentStatus | Format-List
$enrollmentStatus | ConvertTo-Json | Out-File ".\frontier-enrollment-check-$(Get-Date -Format 'yyyy-MM-dd').json"
```

## Script 2: Export Full Agent Inventory

This script retrieves the complete agent registry from the Agent 365 API and exports it as a CSV file for compliance retention. Schedule this script to run monthly for Zone 3 and quarterly for Zone 2. Outputs are retained as SEC 17a-4 examination evidence.

```powershell
<#
.SYNOPSIS
    Exports the full Agent 365 agent inventory to CSV for compliance retention.
.DESCRIPTION
    Retrieves all agents from the Agent 365 registry via Microsoft Graph (beta),
    including owner, platform, governance template, and status fields. Exports
    to a dated CSV file for SEC 17a-4 recordkeeping and FINRA examination readiness.
.NOTES
    Graph endpoint: /beta — Subject to change at GA (May 1, 2026).
    Regulatory purpose: SEC 17a-3/17a-4 recordkeeping; FINRA Rule 3110 supervisory records.
    Retention: Store in immutable/WORM storage per SEC Rule 17a-4(f).
    Schedule: Monthly for Zone 3; Quarterly for Zone 2.
#>

function Export-AgentInventory {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory)]
        [string]$OutputPath,

        [Parameter()]
        [string]$DateStamp = (Get-Date -Format "yyyy-MM-dd"),

        [Parameter()]
        [switch]$IncludeInactive
    )

    $outputFile = Join-Path $OutputPath "agent-inventory-$DateStamp.csv"
    $agents     = [System.Collections.Generic.List[PSCustomObject]]::new()
    $pageUri    = "https://graph.microsoft.com/beta/admin/agentApps?`$top=100"

    Write-Host "Starting agent inventory export — $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

    # Paginate through all agents in the registry
    do {
        $response = Invoke-MgGraphRequest -Method GET -Uri $pageUri -ErrorAction Stop
        foreach ($agent in $response.value) {
            # Filter inactive agents unless flag set
            if (-not $IncludeInactive -and $agent.status -ne "Active") { continue }

            $agents.Add([PSCustomObject]@{
                AgentId              = $agent.id
                AgentName            = $agent.displayName
                Publisher            = $agent.publisher
                Platform             = $agent.platform
                OwnerUPN             = $agent.ownerUserPrincipalName
                OwnerDisplayName     = $agent.ownerDisplayName
                Status               = $agent.status
                DeploymentScope      = $agent.deploymentScope
                GovernanceTemplate   = $agent.governanceTemplateName
                CreatedDateTime      = $agent.createdDateTime
                LastModifiedDateTime = $agent.lastModifiedDateTime
                ApprovalStatus       = $agent.approvalStatus
                ApprovedBy           = $agent.approvedByUserPrincipalName
                ApprovalDate         = $agent.approvalDate
            })
        }
        $pageUri = $response.'@odata.nextLink'
    } while ($null -ne $pageUri)

    if ($agents.Count -eq 0) {
        Write-Warning "No agents found in registry. Verify Graph permissions and Frontier enrollment."
        return
    }

    # Export to CSV
    $agents | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8
    Write-Host "Exported $($agents.Count) agents to: $outputFile"

    # Write export log entry
    $logEntry = [PSCustomObject]@{
        ExportDate        = $DateStamp
        ExportedBy        = "ServicePrincipal:$($env:AZURE_CLIENT_ID)"
        AgentCount        = $agents.Count
        OutputFile        = $outputFile
        IncludeInactive   = $IncludeInactive.IsPresent
        RegulatoryPurpose = "SEC 17a-4 / FINRA 3110 examination evidence"
    }
    $logFile = Join-Path $OutputPath "agent-inventory-export-log.json"
    $existingLog = if (Test-Path $logFile) {
        Get-Content $logFile | ConvertFrom-Json
    } else { @() }
    $existingLog += $logEntry
    $existingLog | ConvertTo-Json -Depth 5 | Out-File $logFile -Encoding UTF8

    return $outputFile
}

# Execute — set OutputPath to your compliance repository location
$exportedFile = Export-AgentInventory `
    -OutputPath "C:\ComplianceRepository\AgentInventory" `
    -IncludeInactive

Write-Host "Inventory export complete: $exportedFile"
```

## Script 3: Query Pending Requests and Ownerless Agents

This script queries the two primary governance card data points — pending approval requests and ownerless agents — and produces a structured report for the governance administrator. Configure this script to run daily for Zone 3 and weekly for Zone 2, with email alerting if the SLA threshold is exceeded.

```powershell
<#
.SYNOPSIS
    Queries Agent 365 pending requests and ownerless agents for governance queue management.
.DESCRIPTION
    Retrieves all pending agent approval requests and ownerless agents from the Agent 365
    API. Flags requests exceeding SLA thresholds and generates a governance queue report.
    Sends an alert if any Zone 3 request is older than 1 business day or Zone 2 request
    is older than 5 business days.
.NOTES
    Graph endpoint: /beta — Subject to change at GA (May 1, 2026).
    Regulatory purpose: FINRA Rule 3110 — Supervisory review SLA; SOX 404 — Control timeliness.
    Schedule: Daily for Zone 3; Weekly for Zone 2.
#>

function Get-GovernanceQueueStatus {
    [CmdletBinding()]
    param (
        [Parameter()]
        [int]$Zone3SLADays = 1,

        [Parameter()]
        [int]$Zone2SLADays = 5,

        [Parameter()]
        [string]$OutputPath = ".",

        [Parameter()]
        [string]$AlertEmailAddress = ""
    )

    $reportDate = Get-Date -Format "yyyy-MM-dd"
    $report = [PSCustomObject]@{
        ReportDate            = $reportDate
        PendingRequestsTotal  = 0
        PendingRequestsSLA    = @()
        OwnerlessAgentsTotal  = 0
        OwnerlessAgents       = @()
        SLABreachDetected     = $false
        AlertSent             = $false
    }

    # --- Pending Requests ---
    Write-Host "Querying pending agent requests..."
    try {
        $pendingUri = "https://graph.microsoft.com/beta/admin/agentApps/requests?`$filter=status eq 'Pending'&`$orderby=createdDateTime asc"
        $pendingResponse = Invoke-MgGraphRequest -Method GET -Uri $pendingUri -ErrorAction Stop
        $pendingRequests = $pendingResponse.value

        $report.PendingRequestsTotal = $pendingRequests.Count
        $slaBreaches = [System.Collections.Generic.List[PSCustomObject]]::new()

        foreach ($req in $pendingRequests) {
            $submittedDate = [datetime]$req.createdDateTime
            $ageInDays     = ([datetime]::UtcNow - $submittedDate).TotalDays
            $zone          = if ($req.zoneClassification -eq "Zone3") { "Zone3" } else { "Zone2" }
            $slaThreshold  = if ($zone -eq "Zone3") { $Zone3SLADays } else { $Zone2SLADays }
            $slaBreach     = $ageInDays -gt $slaThreshold

            if ($slaBreach) {
                $report.SLABreachDetected = $true
                $slaBreaches.Add([PSCustomObject]@{
                    RequestId      = $req.id
                    AgentName      = $req.agentDisplayName
                    RequestType    = $req.requestType
                    SubmittedBy    = $req.requestedByUserPrincipalName
                    SubmittedDate  = $req.createdDateTime
                    AgeInDays      = [math]::Round($ageInDays, 1)
                    Zone           = $zone
                    SLAThresholdDays = $slaThreshold
                    SLAStatus      = "BREACHED"
                })
            }
        }
        $report.PendingRequestsSLA = $slaBreaches
    }
    catch {
        Write-Warning "Failed to query pending requests: $($_.Exception.Message)"
    }

    # --- Ownerless Agents ---
    Write-Host "Querying ownerless agents..."
    try {
        $ownerlessUri = "https://graph.microsoft.com/beta/admin/agentApps?`$filter=ownerUserPrincipalName eq null and status eq 'Active'"
        $ownerlessResponse = Invoke-MgGraphRequest -Method GET -Uri $ownerlessUri -ErrorAction Stop
        $ownerlessAgents = $ownerlessResponse.value

        $report.OwnerlessAgentsTotal = $ownerlessAgents.Count
        $report.OwnerlessAgents = $ownerlessAgents | ForEach-Object {
            [PSCustomObject]@{
                AgentId          = $_.id
                AgentName        = $_.displayName
                Platform         = $_.platform
                Publisher        = $_.publisher
                Status           = $_.status
                CreatedDateTime  = $_.createdDateTime
                RegulatoryRisk   = "HIGH — No supervisory chain (FINRA 3110)"
            }
        }

        if ($ownerlessAgents.Count -gt 0) {
            $report.SLABreachDetected = $true
        }
    }
    catch {
        Write-Warning "Failed to query ownerless agents: $($_.Exception.Message)"
    }

    # --- Output report ---
    $reportFile = Join-Path $OutputPath "governance-queue-$reportDate.json"
    $report | ConvertTo-Json -Depth 5 | Out-File $reportFile -Encoding UTF8
    Write-Host "Governance queue report saved: $reportFile"

    # --- Summary to console ---
    Write-Host ""
    Write-Host "=== GOVERNANCE QUEUE SUMMARY — $reportDate ===" -ForegroundColor Cyan
    Write-Host "Pending Requests:  $($report.PendingRequestsTotal)"
    Write-Host "SLA Breaches:      $($report.PendingRequestsSLA.Count)"
    Write-Host "Ownerless Agents:  $($report.OwnerlessAgentsTotal)"

    if ($report.SLABreachDetected) {
        Write-Host ""
        Write-Warning "ACTION REQUIRED: SLA breach or ownerless agents detected. Review governance queue immediately."
        if ($report.PendingRequestsSLA.Count -gt 0) {
            Write-Host "SLA Breached Requests:" -ForegroundColor Yellow
            $report.PendingRequestsSLA | Format-Table RequestId, AgentName, Zone, AgeInDays, SLAThresholdDays -AutoSize
        }
        if ($report.OwnerlessAgentsTotal -gt 0) {
            Write-Host "Ownerless Agents:" -ForegroundColor Yellow
            $report.OwnerlessAgents | Format-Table AgentId, AgentName, Platform, CreatedDateTime -AutoSize
        }
    } else {
        Write-Host "Governance queue healthy — no SLA breaches or ownerless agents." -ForegroundColor Green
    }

    return $report
}

# Execute
$queueStatus = Get-GovernanceQueueStatus `
    -Zone3SLADays 1 `
    -Zone2SLADays 5 `
    -OutputPath "C:\ComplianceRepository\GovernanceReports" `
    -AlertEmailAddress "ai-governance@yourfirm.com"
```

## Script 4: Assign Owner to Ownerless Agent

When the governance queue report identifies ownerless agents, use this script to programmatically assign a new owner. Always pair this with a change management ticket per Control 2.3.

```powershell
<#
.SYNOPSIS
    Assigns a new owner to an ownerless agent in the Agent 365 registry.
.DESCRIPTION
    Updates the owner field of a specified agent via Microsoft Graph (beta).
    This script should only be executed after a named individual accepts accountability
    for the agent. Document the assignment in the change management system.
.NOTES
    Graph endpoint: /beta — Subject to change at GA (May 1, 2026).
    Regulatory purpose: FINRA Rule 3110 — Supervisory chain re-establishment.
    Permission required: AgentApp.ReadWrite.All
#>

function Set-AgentOwner {
    [CmdletBinding(SupportsShouldProcess)]
    param (
        [Parameter(Mandatory)]
        [string]$AgentId,

        [Parameter(Mandatory)]
        [string]$NewOwnerUPN,

        [Parameter(Mandatory)]
        [string]$ChangeTicketId,

        [Parameter()]
        [string]$BusinessJustification = ""
    )

    # Validate new owner exists in directory
    $newOwner = Get-MgUser -UserId $NewOwnerUPN -ErrorAction Stop
    if (-not $newOwner) {
        throw "User '$NewOwnerUPN' not found in directory. Verify UPN before assigning ownership."
    }

    $updateBody = @{
        ownerUserId = $newOwner.Id
    } | ConvertTo-Json

    if ($PSCmdlet.ShouldProcess("Agent $AgentId", "Assign owner $NewOwnerUPN (Change ticket: $ChangeTicketId)")) {
        $uri = "https://graph.microsoft.com/beta/admin/agentApps/$AgentId"
        Invoke-MgGraphRequest -Method PATCH -Uri $uri -Body $updateBody -ContentType "application/json" -ErrorAction Stop

        Write-Host "Owner assigned successfully." -ForegroundColor Green
        Write-Host "Agent ID:          $AgentId"
        Write-Host "New Owner:         $NewOwnerUPN ($($newOwner.DisplayName))"
        Write-Host "Change Ticket:     $ChangeTicketId"
        Write-Host "Timestamp:         $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')"

        # Write audit log entry
        [PSCustomObject]@{
            Timestamp            = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            AgentId              = $AgentId
            NewOwnerUPN          = $NewOwnerUPN
            NewOwnerDisplayName  = $newOwner.DisplayName
            ChangeTicketId       = $ChangeTicketId
            BusinessJustification = $BusinessJustification
            ExecutedBy           = "ServicePrincipal:$($env:AZURE_CLIENT_ID)"
            RegulatoryNote       = "Owner assignment per FINRA Rule 3110 supervisory chain re-establishment"
        } | ConvertTo-Json | Add-Content -Path "C:\ComplianceRepository\OwnerAssignmentLog.json"
    }
}

# Example usage
Set-AgentOwner `
    -AgentId "00000000-0000-0000-0000-000000000001" `
    -NewOwnerUPN "jane.doe@yourfirm.com" `
    -ChangeTicketId "CHG-2026-03-001" `
    -BusinessJustification "Reassignment following departure of original owner per orphaned agent policy" `
    -WhatIf  # Remove -WhatIf to execute
```

## Scheduling Recommendations

Configure these scripts in your automation platform (Azure Automation, GitHub Actions, or internal scheduler) on the following cadence:

| Script | Zone 2 Schedule | Zone 3 Schedule | Output Retention |
|---|---|---|---|
| Script 1: Frontier Enrollment Check | Weekly | Daily | 1 year |
| Script 2: Inventory Export | Quarterly | Monthly | 6 years (SEC 17a-4) |
| Script 3: Governance Queue Status | Weekly | Daily | 3 years |
| Script 4: Assign Owner | On demand | On demand | 6 years (audit trail) |

!!! danger "Service Principal Security Requirements"
    The service principal used for Agent 365 automation must comply with your firm's privileged access management (PAM) policy:

    - Use certificate authentication (not client secrets) in production
    - Store credentials in Azure Key Vault with access restricted to the automation account
    - Enable Entra ID audit logging for all service principal sign-ins
    - Review and rotate credentials on a schedule (annually at minimum; quarterly for Zone 3)
    - Document this service principal in your OCC 2011-12 technology risk inventory
    - Never assign Global Administrator or Global Reader roles to the service principal; use the minimum permissions listed at the top of this playbook

---

[Back to Control 2.25](../../../controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: March 2026 | Version: v1.3*
