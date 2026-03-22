# Playbook: PowerShell Setup — Control 2.26

**Control:** 2.26 — Entra Agent ID: Identity Governance for Agents
**Playbook Type:** PowerShell Setup
**Estimated Time:** 1–2 hours (initial setup and first report run); 15–30 minutes per subsequent governance report
**Prerequisites:** Microsoft Graph PowerShell SDK installed; Global Administrator, Identity Governance Administrator, or custom role with agent identity read permissions; Frontier enrollment active

---

!!! info "Preview Feature — Microsoft Entra Agent ID"
    The Microsoft Graph API endpoints for Entra Agent ID are in **PREVIEW** as part of the Frontier program. The specific `/beta` endpoints and agent identity properties used in this playbook may change before general availability. Always test against a non-production tenant or with a limited scope before running governance queries against production agent inventories.

    Graph API calls in this playbook use the `/beta` endpoint where agent identity properties are available. The `/v1.0` endpoint may not expose agent-specific properties until the feature reaches general availability.

!!! warning "Permissions Required"
    The following Microsoft Graph API permissions are required for the operations in this playbook:

    | Permission | Type | Required For |
    |---|---|---|
    | `Application.Read.All` | Application | Read agent identities and application properties |
    | `EntitlementManagement.Read.All` | Application | Read access packages and assignments |
    | `EntitlementManagement.ReadWrite.All` | Application | Write sponsor assignments and access package requests |
    | `IdentityGovernance.Read.All` | Application | Read lifecycle workflows and access review results |
    | `Directory.Read.All` | Application | Read user and organizational data for sponsor validation |

    For read-only governance reporting, use `Application.Read.All`, `EntitlementManagement.Read.All`, and `IdentityGovernance.Read.All`. Write operations (bulk sponsor assignment) additionally require `EntitlementManagement.ReadWrite.All`.

---

## Section 1: Environment Setup

### Step 1.1: Install and Connect Microsoft Graph PowerShell SDK

```powershell
# Install Microsoft Graph PowerShell SDK (if not already installed)
Install-Module -Name Microsoft.Graph -Scope CurrentUser -Force

# Install required submodules
Install-Module -Name Microsoft.Graph.Applications -Scope CurrentUser -Force
Install-Module -Name Microsoft.Graph.Identity.Governance -Scope CurrentUser -Force

# Connect with required scopes for governance reporting (read-only)
Connect-MgGraph -Scopes `
    "Application.Read.All", `
    "EntitlementManagement.Read.All", `
    "IdentityGovernance.Read.All", `
    "Directory.Read.All"

# Verify connection
Get-MgContext | Select-Object TenantId, Account, Scopes
```

### Step 1.2: Set Variables for Your Environment

```powershell
# -------------------------------------------------------
# CONFIGURATION — Update these values for your tenant
# -------------------------------------------------------

# Your tenant ID (from Entra admin center > Overview)
$TenantId = "your-tenant-id-here"

# Name of the entitlement management catalog for agent resources
$AgentCatalogName = "AI Agent Resources"

# Output directory for governance reports
$ReportOutputPath = "C:\GovernanceReports\AgentIdentity"

# Governance zones — adjust display names if your tenant uses different naming
$Zone2Tag = "Zone2"
$Zone3Tag = "Zone3"

# -------------------------------------------------------
# Create output directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $ReportOutputPath | Out-Null
Write-Host "Reports will be saved to: $ReportOutputPath" -ForegroundColor Green
```

---

## Section 2: Governance Gap Reports

### Step 2.1: Query All Agent Identities

The following query retrieves all agent identity objects from the Entra tenant. Agent identities are a subset of application/service principal objects with agent-specific properties set via the Frontier preview.

```powershell
# Query all agent identities via Microsoft Graph beta endpoint
# Note: Agent identity properties are in /beta during preview
function Get-AllAgentIdentities {
    param(
        [switch]$IncludeDisabled
    )

    Write-Host "Querying agent identities from Microsoft Graph (beta)..." -ForegroundColor Cyan

    # Retrieve service principals with agent-type classification
    # During Frontier preview, agents are identified by the 'servicePrincipalType' = 'Agent'
    # or by the presence of agent metadata properties
    $agents = Get-MgBetaServicePrincipal -Filter "servicePrincipalType eq 'Agent'" -All

    if (-not $IncludeDisabled) {
        $agents = $agents | Where-Object { $_.AccountEnabled -eq $true }
    }

    Write-Host "Found $($agents.Count) agent identities." -ForegroundColor Green
    return $agents
}

$allAgents = Get-AllAgentIdentities
$allAgents | Select-Object DisplayName, AppId, AccountEnabled, CreatedDateTime |
    Format-Table -AutoSize
```

### Step 2.2: Export Agents Without Sponsors (Governance Gap Report)

This report is the primary governance gap detection tool. Any Zone 2 or Zone 3 agent without an assigned sponsor is a compliance gap requiring immediate remediation.

```powershell
function Get-AgentsWithoutSponsors {
    param(
        [Parameter(Mandatory)]
        [array]$Agents
    )

    Write-Host "Identifying agents without assigned sponsors..." -ForegroundColor Cyan

    $gapReport = @()

    foreach ($agent in $Agents) {
        # Retrieve extended agent properties including sponsor
        # Sponsor is stored in agent identity additional data during Frontier preview
        $agentDetail = Get-MgBetaServicePrincipal -ServicePrincipalId $agent.Id `
            -Property "id,displayName,appId,accountEnabled,createdDateTime,additionalData"

        $sponsor = $agentDetail.AdditionalData["sponsor"]
        $zone = $agentDetail.AdditionalData["governanceZone"]

        if ([string]::IsNullOrEmpty($sponsor)) {
            $gapReport += [PSCustomObject]@{
                AgentDisplayName    = $agent.DisplayName
                AgentId             = $agent.Id
                AppId               = $agent.AppId
                AccountEnabled      = $agent.AccountEnabled
                CreatedDateTime     = $agent.CreatedDateTime
                GovernanceZone      = if ($zone) { $zone } else { "Not Tagged" }
                SponsorAssigned     = "NO — GOVERNANCE GAP"
                RemediationRequired = "Assign sponsor immediately via Entra admin center"
            }
        }
    }

    Write-Host "Agents without sponsors: $($gapReport.Count)" -ForegroundColor $(
        if ($gapReport.Count -gt 0) { "Red" } else { "Green" }
    )

    return $gapReport
}

# Run the gap report
$sponsorGaps = Get-AgentsWithoutSponsors -Agents $allAgents

# Export to CSV for governance file
$reportDate = Get-Date -Format "yyyyMMdd-HHmm"
$gapReportPath = "$ReportOutputPath\AgentSponsorGaps_$reportDate.csv"
$sponsorGaps | Export-Csv -Path $gapReportPath -NoTypeInformation

Write-Host "Governance gap report exported to: $gapReportPath" -ForegroundColor Green

# Display summary for immediate review
if ($sponsorGaps.Count -gt 0) {
    Write-Host "`n--- GOVERNANCE GAPS REQUIRING IMMEDIATE REMEDIATION ---" -ForegroundColor Red
    $sponsorGaps | Format-Table AgentDisplayName, GovernanceZone, SponsorAssigned -AutoSize
}
```

### Step 2.3: List Access Packages Assigned to Agents with Expiration Dates

This report provides a full view of access package assignments for all agents, including expiration dates. It is used to identify agents with expired or near-expiring access and to produce the access package evidence required for SOX 404 attestation.

```powershell
function Get-AgentAccessPackageAssignments {
    Write-Host "Querying entitlement management for agent access package assignments..." -ForegroundColor Cyan

    # Get the AI Agent Resources catalog
    $catalog = Get-MgEntitlementManagementAccessPackageCatalog -Filter "displayName eq '$AgentCatalogName'"

    if (-not $catalog) {
        Write-Warning "Catalog '$AgentCatalogName' not found. Verify catalog name in configuration."
        return $null
    }

    Write-Host "Found catalog: $($catalog.DisplayName) (ID: $($catalog.Id))" -ForegroundColor Green

    # Get all access packages in the catalog
    $accessPackages = Get-MgEntitlementManagementAccessPackage `
        -Filter "catalogId eq '$($catalog.Id)'" -All

    $assignmentReport = @()

    foreach ($package in $accessPackages) {
        Write-Host "  Checking assignments for: $($package.DisplayName)" -ForegroundColor Gray

        # Get assignments for this access package
        $assignments = Get-MgEntitlementManagementAccessPackageAssignment `
            -Filter "accessPackageId eq '$($package.Id)'" -All

        foreach ($assignment in $assignments) {
            $daysUntilExpiry = $null
            $expiryStatus = "No Expiration Set — REVIEW REQUIRED"

            if ($assignment.ExpiredDateTime) {
                $daysUntilExpiry = ($assignment.ExpiredDateTime - (Get-Date)).Days
                $expiryStatus = switch ($true) {
                    ($daysUntilExpiry -lt 0)  { "EXPIRED — ACCESS SHOULD BE REMOVED" }
                    ($daysUntilExpiry -le 30) { "EXPIRING WITHIN 30 DAYS — ACTION REQUIRED" }
                    ($daysUntilExpiry -le 90) { "Expiring within 90 days" }
                    default                    { "Active" }
                }
            }

            $assignmentReport += [PSCustomObject]@{
                AccessPackageName    = $package.DisplayName
                AssignedToId         = $assignment.TargetId
                AssignmentState      = $assignment.AssignmentState
                CreatedDateTime      = $assignment.CreatedDateTime
                ExpirationDateTime   = $assignment.ExpiredDateTime
                DaysUntilExpiry      = $daysUntilExpiry
                ExpiryStatus         = $expiryStatus
                AssignmentId         = $assignment.Id
            }
        }
    }

    return $assignmentReport
}

$accessPackageReport = Get-AgentAccessPackageAssignments

# Export full report
$apReportPath = "$ReportOutputPath\AgentAccessPackages_$reportDate.csv"
$accessPackageReport | Export-Csv -Path $apReportPath -NoTypeInformation
Write-Host "Access package report exported to: $apReportPath" -ForegroundColor Green

# Highlight expired assignments
$expiredAssignments = $accessPackageReport | Where-Object {
    $_.ExpiryStatus -like "EXPIRED*"
}

if ($expiredAssignments.Count -gt 0) {
    Write-Host "`n--- EXPIRED ACCESS PACKAGES — IMMEDIATE REMOVAL REQUIRED ---" -ForegroundColor Red
    $expiredAssignments | Format-Table AccessPackageName, AssignedToId, ExpirationDateTime, ExpiryStatus -AutoSize
}
```

### Step 2.4: Combined Compliance Summary Report

```powershell
function Get-AgentGovernanceSummary {
    param(
        [array]$Agents,
        [array]$SponsorGaps,
        [array]$AccessPackageAssignments
    )

    $summary = [PSCustomObject]@{
        ReportGeneratedAt        = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
        TotalActiveAgents        = $Agents.Count
        AgentsWithoutSponsors    = $SponsorGaps.Count
        TotalAccessAssignments   = $AccessPackageAssignments.Count
        ExpiredAssignments       = ($AccessPackageAssignments | Where-Object { $_.ExpiryStatus -like "EXPIRED*" }).Count
        ExpiringWithin30Days     = ($AccessPackageAssignments | Where-Object { $_.ExpiryStatus -like "EXPIRING*" }).Count
        NoExpirationConfigured   = ($AccessPackageAssignments | Where-Object { $_.ExpiryStatus -like "No Expiration*" }).Count
        OverallComplianceStatus  = if ($SponsorGaps.Count -eq 0 -and
                                       ($AccessPackageAssignments | Where-Object { $_.ExpiryStatus -like "EXPIRED*" }).Count -eq 0) {
                                        "COMPLIANT"
                                    } else {
                                        "NON-COMPLIANT — Remediation Required"
                                    }
    }

    return $summary
}

$summary = Get-AgentGovernanceSummary `
    -Agents $allAgents `
    -SponsorGaps $sponsorGaps `
    -AccessPackageAssignments $accessPackageReport

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   CONTROL 2.26 COMPLIANCE SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
$summary | Format-List

# Export summary
$summaryPath = "$ReportOutputPath\ComplianceSummary_$reportDate.csv"
$summary | Export-Csv -Path $summaryPath -NoTypeInformation
Write-Host "Summary exported to: $summaryPath" -ForegroundColor Green
```

---

## Section 3: Bulk Sponsor Assignment

Use this section when remediating a large number of agents identified in the governance gap report (Section 2.2). This is also used during initial deployment of this control when agents pre-exist without sponsors.

!!! warning "Write Permissions Required"
    Bulk sponsor assignment requires the `EntitlementManagement.ReadWrite.All` permission. Reconnect to Graph with write permissions before running Section 3 commands.

    ```powershell
    Connect-MgGraph -Scopes `
        "Application.Read.All", `
        "EntitlementManagement.ReadWrite.All", `
        "Directory.ReadWrite.All"
    ```

### Step 3.1: Prepare Sponsor Assignment Input File

Create a CSV file with the following columns and save it to the reports directory:

```
AgentId,AgentDisplayName,SponsorUPN,GovernanceZone,BusinessJustification
```

Example contents:

```csv
AgentId,AgentDisplayName,SponsorUPN,GovernanceZone,BusinessJustification
"aaaaaaaa-0000-0000-0000-000000000001","Compliance Research Agent","jane.smith@contoso.com","Zone3","Compliance document analysis agent owned by Jane Smith per Nov 2025 deployment approval"
"bbbbbbbb-0000-0000-0000-000000000002","Team Reporting Agent","john.doe@contoso.com","Zone2","Team-level reporting agent for Operations department, owned by John Doe"
```

### Step 3.2: Execute Bulk Sponsor Assignment

```powershell
function Set-AgentSponsorBulk {
    param(
        [Parameter(Mandatory)]
        [string]$InputCsvPath
    )

    if (-not (Test-Path $InputCsvPath)) {
        Write-Error "Input CSV not found: $InputCsvPath"
        return
    }

    $assignments = Import-Csv -Path $InputCsvPath
    $results = @()
    $successCount = 0
    $failureCount = 0

    Write-Host "Processing $($assignments.Count) sponsor assignments..." -ForegroundColor Cyan

    foreach ($row in $assignments) {
        try {
            # Resolve sponsor UPN to object ID
            $sponsorUser = Get-MgUser -Filter "userPrincipalName eq '$($row.SponsorUPN)'"

            if (-not $sponsorUser) {
                throw "Sponsor user not found: $($row.SponsorUPN)"
            }

            # Set sponsor on the agent identity (via additionalData patch)
            # Note: Exact property path may vary during Frontier preview — verify against
            # current Microsoft Graph API documentation before running in production
            $body = @{
                additionalData = @{
                    sponsor          = $sponsorUser.Id
                    governanceZone   = $row.GovernanceZone
                    sponsorAssignedBy = (Get-MgContext).Account
                    sponsorAssignedAt = (Get-Date -Format "o")
                    businessJustification = $row.BusinessJustification
                }
            }

            Update-MgBetaServicePrincipal -ServicePrincipalId $row.AgentId -BodyParameter $body

            $results += [PSCustomObject]@{
                AgentId      = $row.AgentId
                AgentName    = $row.AgentDisplayName
                SponsorUPN   = $row.SponsorUPN
                SponsorId    = $sponsorUser.Id
                Zone         = $row.GovernanceZone
                Status       = "SUCCESS"
                Error        = ""
                Timestamp    = Get-Date -Format "o"
            }
            $successCount++
            Write-Host "  [OK] $($row.AgentDisplayName) -> $($row.SponsorUPN)" -ForegroundColor Green

        } catch {
            $results += [PSCustomObject]@{
                AgentId      = $row.AgentId
                AgentName    = $row.AgentDisplayName
                SponsorUPN   = $row.SponsorUPN
                SponsorId    = ""
                Zone         = $row.GovernanceZone
                Status       = "FAILED"
                Error        = $_.Exception.Message
                Timestamp    = Get-Date -Format "o"
            }
            $failureCount++
            Write-Warning "  [FAIL] $($row.AgentDisplayName): $($_.Exception.Message)"
        }
    }

    # Export results
    $bulkResultPath = "$ReportOutputPath\BulkSponsorAssignment_$reportDate.csv"
    $results | Export-Csv -Path $bulkResultPath -NoTypeInformation

    Write-Host "`nBulk assignment complete: $successCount succeeded, $failureCount failed" -ForegroundColor Cyan
    Write-Host "Results exported to: $bulkResultPath" -ForegroundColor Green

    if ($failureCount -gt 0) {
        Write-Warning "Review failed assignments and remediate manually via Entra admin center."
    }

    return $results
}

# Example usage:
# $bulkResults = Set-AgentSponsorBulk -InputCsvPath "$ReportOutputPath\SponsorAssignments.csv"
```

---

## Section 4: Examination Evidence Export

These functions produce the evidence bundles typically requested during FINRA, OCC, or SEC examinations for this control.

### Step 4.1: Generate Full Evidence Package

```powershell
function Export-Control226EvidencePackage {
    param(
        [string]$ExamPeriodStart = ((Get-Date).AddMonths(-12).ToString("yyyy-MM-dd")),
        [string]$ExamPeriodEnd   = (Get-Date -Format "yyyy-MM-dd"),
        [string]$OutputDirectory = "$ReportOutputPath\ExaminationEvidence_$(Get-Date -Format 'yyyyMMdd')"
    )

    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

    Write-Host "Generating Control 2.26 examination evidence package..." -ForegroundColor Cyan
    Write-Host "Exam period: $ExamPeriodStart to $ExamPeriodEnd" -ForegroundColor Gray
    Write-Host "Output directory: $OutputDirectory" -ForegroundColor Gray

    # 1. Agent inventory with sponsor status
    Write-Host "`n[1/5] Agent inventory with sponsor status..." -ForegroundColor Gray
    $agents = Get-AllAgentIdentities -IncludeDisabled
    $agentInventory = $agents | ForEach-Object {
        $detail = Get-MgBetaServicePrincipal -ServicePrincipalId $_.Id `
            -Property "id,displayName,appId,accountEnabled,createdDateTime,additionalData"
        [PSCustomObject]@{
            AgentDisplayName  = $detail.DisplayName
            AgentId           = $detail.Id
            AppId             = $detail.AppId
            AccountEnabled    = $detail.AccountEnabled
            CreatedDateTime   = $detail.CreatedDateTime
            GovernanceZone    = $detail.AdditionalData["governanceZone"]
            Sponsor           = $detail.AdditionalData["sponsor"]
            SponsorAssigned   = if ($detail.AdditionalData["sponsor"]) { "YES" } else { "NO — GAP" }
        }
    }
    $agentInventory | Export-Csv "$OutputDirectory\01_AgentInventory.csv" -NoTypeInformation
    Write-Host "  Exported: 01_AgentInventory.csv ($($agentInventory.Count) agents)" -ForegroundColor Green

    # 2. Access package assignments (current)
    Write-Host "[2/5] Access package assignments..." -ForegroundColor Gray
    $apAssignments = Get-AgentAccessPackageAssignments
    $apAssignments | Export-Csv "$OutputDirectory\02_AccessPackageAssignments.csv" -NoTypeInformation
    Write-Host "  Exported: 02_AccessPackageAssignments.csv ($($apAssignments.Count) assignments)" -ForegroundColor Green

    # 3. Governance gap summary
    Write-Host "[3/5] Governance gap analysis..." -ForegroundColor Gray
    $gaps = Get-AgentsWithoutSponsors -Agents ($agents | Where-Object { $_.AccountEnabled -eq $true })
    $gaps | Export-Csv "$OutputDirectory\03_GovernanceGaps.csv" -NoTypeInformation
    Write-Host "  Exported: 03_GovernanceGaps.csv ($($gaps.Count) gaps)" -ForegroundColor Green

    # 4. Lifecycle workflow history (last 12 months)
    Write-Host "[4/5] Lifecycle workflow history..." -ForegroundColor Gray
    $workflows = Get-MgIdentityGovernanceLifecycleWorkflow -All
    $workflowHistory = $workflows | ForEach-Object {
        $runs = Get-MgIdentityGovernanceLifecycleWorkflowRun -WorkflowId $_.Id -All |
                Where-Object { $_.StartedDateTime -ge [datetime]$ExamPeriodStart }
        $runs | ForEach-Object {
            [PSCustomObject]@{
                WorkflowName    = ($workflows | Where-Object { $_.Id -eq $_.WorkflowId }).DisplayName
                RunId           = $_.Id
                Status          = $_.RunStatus
                StartedDateTime = $_.StartedDateTime
                CompletedDateTime = $_.CompletedDateTime
                ProcessedCount  = $_.ProcessedCount
                FailedCount     = $_.FailedCount
            }
        }
    }
    $workflowHistory | Export-Csv "$OutputDirectory\04_LifecycleWorkflowHistory.csv" -NoTypeInformation
    Write-Host "  Exported: 04_LifecycleWorkflowHistory.csv ($($workflowHistory.Count) runs)" -ForegroundColor Green

    # 5. Access review results (completed in exam period)
    Write-Host "[5/5] Access review certification results..." -ForegroundColor Gray
    $accessReviews = Get-MgIdentityGovernanceAccessReviewInstance -All |
                     Where-Object {
                         $_.Status -eq "Completed" -and
                         $_.EndDateTime -ge [datetime]$ExamPeriodStart
                     }
    $reviewResults = $accessReviews | ForEach-Object {
        $decisions = Get-MgIdentityGovernanceAccessReviewInstanceDecision `
            -AccessReviewInstanceId $_.Id -All
        $decisions | ForEach-Object {
            [PSCustomObject]@{
                ReviewId        = $_.AccessReviewId
                TargetId        = $_.Target.Id
                ReviewedBy      = $_.ReviewedBy.UserPrincipalName
                Decision        = $_.Decision
                Justification   = $_.Justification
                ReviewedDateTime = $_.ReviewedDateTime
            }
        }
    }
    $reviewResults | Export-Csv "$OutputDirectory\05_AccessReviewDecisions.csv" -NoTypeInformation
    Write-Host "  Exported: 05_AccessReviewDecisions.csv ($($reviewResults.Count) decisions)" -ForegroundColor Green

    # Generate index file
    $indexContent = @"
Control 2.26 — Examination Evidence Package
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
Exam Period: $ExamPeriodStart to $ExamPeriodEnd
Tenant: $TenantId

Files Included:
  01_AgentInventory.csv           — All agent identities with sponsor assignment status
  02_AccessPackageAssignments.csv — Current access package assignments with expiration dates
  03_GovernanceGaps.csv           — Agents without sponsors (compliance gaps)
  04_LifecycleWorkflowHistory.csv — Lifecycle workflow execution history
  05_AccessReviewDecisions.csv    — Completed access review certification decisions

Regulatory Cross-References:
  SOX 404    — Files 01, 02, 03 (access control documentation and attestation)
  GLBA 501b  — Files 01, 02 (safeguard evidence for NPI-accessing agents)
  FINRA 3110 — Files 01, 03, 05 (supervisory accountability evidence)
  FINRA 4511 — All files (books and records; retain minimum 6 years)
  OCC 2011-12 — Files 03, 04 (technology risk management evidence)
"@
    $indexContent | Out-File "$OutputDirectory\EVIDENCE-INDEX.txt" -Encoding UTF8

    Write-Host "`nEvidence package complete: $OutputDirectory" -ForegroundColor Cyan
    Write-Host "Index file: $OutputDirectory\EVIDENCE-INDEX.txt" -ForegroundColor Cyan
}

# Run the evidence export:
# Export-Control226EvidencePackage
```

---

## Quick Reference: Useful One-Liners

```powershell
# Count all active agents
(Get-MgBetaServicePrincipal -Filter "servicePrincipalType eq 'Agent'" -All |
    Where-Object { $_.AccountEnabled }).Count

# List all access packages in the AI Agent Resources catalog
$catalogId = (Get-MgEntitlementManagementAccessPackageCatalog -Filter "displayName eq 'AI Agent Resources'").Id
Get-MgEntitlementManagementAccessPackage -Filter "catalogId eq '$catalogId'" -All |
    Select-Object DisplayName, Id, CreatedDateTime

# Find assignments expiring within 30 days
Get-MgEntitlementManagementAccessPackageAssignment -All |
    Where-Object { $_.ExpiredDateTime -and $_.ExpiredDateTime -lt (Get-Date).AddDays(30) } |
    Select-Object TargetId, AccessPackageId, ExpiredDateTime |
    Format-Table

# Check lifecycle workflow status
Get-MgIdentityGovernanceLifecycleWorkflow -All |
    Select-Object DisplayName, IsEnabled, ExecutionConditions |
    Format-Table

# Check which agents have no access review scheduled
Get-MgIdentityGovernanceAccessReviewScheduleDefinition -All |
    Where-Object { $_.Status -ne "active" } |
    Select-Object DisplayName, Status, CreatedDateTime
```

---

[Back to Control 2.26](../../../controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

*Updated: March 2026 | Version: v1.3*
