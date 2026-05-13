# Control 4.9 — PowerShell Setup: Embedded File Content Governance

!!! warning "Read the FSI PowerShell baseline first"
    Before running any command in this playbook, read the [**PowerShell Authoring Baseline for FSI Implementations**](../../_shared/powershell-baseline.md). It is the canonical source for module version pinning, sovereign-cloud (GCC / GCC High / DoD) endpoints, mutation safety (`-WhatIf` / `SupportsShouldProcess`), Dataverse compatibility, and SHA-256 evidence emission. Snippets below may show abbreviated patterns; the baseline is authoritative.

**Playbook Type:** PowerShell Setup
**Control:** [4.9 — Embedded File Content Governance](../../../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md)
**Audience:** SharePoint Admins, M365 Administrators, IT Operations, Security Engineering
**Estimated Time:** 45–90 minutes (initial setup); 15 minutes (quarterly script run)
**Last UI Verified:** April 2026
**Required Modules:** PnP.PowerShell (4.x+), Microsoft.Graph (2.x+), ExchangeOnlineManagement

!!! danger "Critical IB Limitation"
    Microsoft Purview Information Barriers are NOT enforced on SharePoint Embedded containers. The scripts in this playbook help you **inventory and audit** embedded file agents — they do not enforce IB controls. Use the IB assessment procedure in the Portal Walkthrough before approving any agent with embedded files.

!!! warning "Permission Requirements"
    The scripts in this playbook require the following permissions:

    - **SharePoint Admin** role (for container enumeration via PnP.PowerShell)
    - **Entra Global Reader** or **Purview Compliance Admin** (for reading sensitivity label metadata)
    - **Microsoft Graph API** permissions: `Sites.Read.All`, `Files.Read.All` (for Graph-based queries)

    Run all scripts in a dedicated service account context where possible. Do not run with Entra Global Admin credentials as a routine practice.

## Overview

This playbook provides PowerShell scripts and configuration steps for:

1. Prerequisite module installation and authentication
2. Querying all Declarative Agent containers in the SharePoint Embedded container registry
3. Exporting the embedded file inventory with sensitivity labels
4. Reconciling containers against the M365 agent inventory
5. Configuring automated monitoring for new container creation
6. Scheduling the quarterly audit script

---

## Section 1: Prerequisites and Module Installation

### Step 1.1 — Install Required PowerShell Modules

Run the following in an elevated PowerShell session. These modules provide SharePoint container management capabilities.

```powershell
# Install PnP.PowerShell (SharePoint Embedded container management)
Install-Module -Name PnP.PowerShell -Scope CurrentUser -Force -AllowClobber

# Install Microsoft.Graph (for Copilot agent metadata and sensitivity label queries)
Install-Module -Name Microsoft.Graph -Scope CurrentUser -Force -AllowClobber

# Install ExchangeOnlineManagement (for compliance audit queries)
Install-Module -Name ExchangeOnlineManagement -Scope CurrentUser -Force -AllowClobber

# Verify installations
Get-Module -ListAvailable PnP.PowerShell | Select-Object Name, Version
Get-Module -ListAvailable Microsoft.Graph | Select-Object Name, Version
```

### Step 1.2 — Authenticate to SharePoint Admin Center

```powershell
# Replace with your tenant admin site URL
$TenantAdminUrl = "https://YOURTENANT-admin.sharepoint.com"

# Interactive authentication (use service principal in automated scenarios — see Step 1.3)
Connect-PnPOnline -Url $TenantAdminUrl -Interactive

# Verify connection
Get-PnPTenantSite -Limit 1 | Select-Object Url
```

### Step 1.3 — Service Principal Authentication (Recommended for Automation)

For scheduled quarterly audits, use an Entra ID App Registration with certificate-based authentication.

```powershell
# Authenticate using App Registration (certificate)
# Replace placeholders with your App Registration values
$TenantId     = "YOUR-TENANT-ID"
$ClientId     = "YOUR-APP-CLIENT-ID"
$CertThumb    = "YOUR-CERTIFICATE-THUMBPRINT"
$TenantAdminUrl = "https://YOURTENANT-admin.sharepoint.com"

Connect-PnPOnline -Url $TenantAdminUrl `
    -ClientId $ClientId `
    -Thumbprint $CertThumb `
    -Tenant $TenantId

# Verify connection
Write-Host "Connected to: $TenantAdminUrl" -ForegroundColor Green
```

!!! note "App Registration Permissions"
    The App Registration requires the following API permissions for full script functionality:

    - SharePoint: `Sites.Read.All` (Application)
    - SharePoint: `TermStore.Read.All` (Application)
    - Microsoft Graph: `Sites.Read.All` (Application)
    - Microsoft Graph: `InformationProtectionPolicy.Read.All` (Application)

    Grant admin consent for all Application permissions after creating the registration.

### Step 1.4 — Authenticate to Microsoft Graph

```powershell
# Authenticate to Microsoft Graph for agent metadata
$TenantId = "YOUR-TENANT-ID"
$ClientId = "YOUR-APP-CLIENT-ID"
$CertThumb = "YOUR-CERTIFICATE-THUMBPRINT"

Connect-MgGraph -TenantId $TenantId `
    -ClientId $ClientId `
    -CertificateThumbprint $CertThumb

# Verify connection
Get-MgContext | Select-Object TenantId, Scopes
```

---

## Section 2: Query All Declarative Agent Containers

The following script enumerates all SharePoint Embedded containers associated with the "Declarative Agent" application. This produces the authoritative container inventory for reconciliation.

### Step 2.1 — Enumerate Declarative Agent Containers

```powershell
<#
.SYNOPSIS
    Enumerates all SharePoint Embedded containers associated with Declarative Agent
    (M365 Copilot Agent Builder embedded file knowledge sources).

.DESCRIPTION
    Queries the SharePoint Admin Center container registry, filters for the
    "Declarative Agent" application, and returns structured container metadata
    for audit and reconciliation purposes.

.OUTPUTS
    Array of PSCustomObject with container metadata.

.NOTES
    Requires PnP.PowerShell and SharePoint Admin role.
    Run Connect-PnPOnline before executing this function.
#>
function Get-DeclarativeAgentContainers {
    [CmdletBinding()]
    param(
        [Parameter()]
        [switch]$IncludeDeleted
    )

    Write-Host "Retrieving Declarative Agent containers from SharePoint Embedded registry..." -ForegroundColor Cyan

    try {
        # Retrieve all SharePoint Embedded containers
        $allContainers = Get-PnPContainer -IncludeAll

        # Filter for Declarative Agent application
        $agentContainers = $allContainers | Where-Object {
            $_.ApplicationName -eq "Declarative Agent"
        }

        if (-not $IncludeDeleted) {
            $agentContainers = $agentContainers | Where-Object {
                $_.Status -ne "Deleted"
            }
        }

        $results = foreach ($container in $agentContainers) {
            [PSCustomObject]@{
                ContainerId       = $container.ContainerId
                ContainerName     = $container.ContainerName
                ApplicationName   = $container.ApplicationName
                Status            = $container.Status
                CreatedDateTime   = $container.CreatedDateTime
                StorageUsedInMB   = [math]::Round($container.StorageUsedInBytes / 1MB, 2)
                SensitivityLabel  = $container.SensitivityLabel
                OwnerId           = $container.OwnerId
                SiteUrl           = $container.SiteUrl
            }
        }

        Write-Host "Found $($results.Count) Declarative Agent containers." -ForegroundColor Green
        return $results

    } catch {
        Write-Error "Failed to retrieve containers: $_"
    }
}

# Execute the function
$containers = Get-DeclarativeAgentContainers

# Display summary
$containers | Format-Table ContainerId, ContainerName, Status, CreatedDateTime, StorageUsedInMB, SensitivityLabel -AutoSize
```

### Step 2.2 — Export Container Inventory to CSV

```powershell
# Export to CSV for audit records
$auditDate = Get-Date -Format "yyyy-MM-dd"
$quarter   = "Q$([math]::Ceiling((Get-Date).Month / 3))"
$outputFile = ".\declarative-agent-containers-$auditDate.csv"

$containers | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8

Write-Host "Container inventory exported to: $outputFile" -ForegroundColor Green

# Summary statistics
Write-Host "`n=== Container Audit Summary ===" -ForegroundColor Yellow
Write-Host "Total containers:          $($containers.Count)"
Write-Host "Containers with labels:    $(($containers | Where-Object { $_.SensitivityLabel }).Count)"
Write-Host "Containers WITHOUT labels: $(($containers | Where-Object { -not $_.SensitivityLabel }).Count)" -ForegroundColor $(if (($containers | Where-Object { -not $_.SensitivityLabel }).Count -gt 0) { 'Red' } else { 'Green' })
Write-Host "Active containers:         $(($containers | Where-Object { $_.Status -eq 'Active' }).Count)"
```

---

## Section 3: Export Embedded File Inventory with Sensitivity Labels

This section retrieves the file-level metadata for each container, producing a complete inventory of all embedded files across all agents.

### Step 3.1 — Retrieve Files Within Each Container

```powershell
<#
.SYNOPSIS
    Retrieves embedded file metadata from all Declarative Agent containers.

.DESCRIPTION
    For each container identified in Section 2, retrieves the list of files
    and their sensitivity labels. Produces a flat file-level inventory for
    compliance review and agent inventory reconciliation.

.PARAMETER Containers
    Array of container objects from Get-DeclarativeAgentContainers.

.OUTPUTS
    Array of PSCustomObject with per-file metadata.
#>
function Get-EmbeddedFileInventory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [array]$Containers
    )

    $fileInventory = [System.Collections.Generic.List[PSCustomObject]]::new()

    foreach ($container in $Containers) {
        Write-Host "Processing container: $($container.ContainerName) [$($container.ContainerId)]" -ForegroundColor Cyan

        try {
            # Connect to container site to retrieve files
            $containerSiteUrl = $container.SiteUrl

            if (-not $containerSiteUrl) {
                Write-Warning "  No site URL for container $($container.ContainerId) — skipping file enumeration"
                continue
            }

            # Get files in the container document library
            $files = Get-PnPListItem -List "Documents" -PageSize 100 -ErrorAction SilentlyContinue

            if ($files) {
                foreach ($file in $files) {
                    $fileItem = [PSCustomObject]@{
                        ContainerId         = $container.ContainerId
                        ContainerName       = $container.ContainerName
                        ContainerLabel      = $container.SensitivityLabel
                        FileName            = $file.FieldValues["FileLeafRef"]
                        FileSize_MB         = [math]::Round($file.FieldValues["File_x0020_Size"] / 1MB, 2)
                        FileType            = [System.IO.Path]::GetExtension($file.FieldValues["FileLeafRef"])
                        FileSensitivityLabel = $file.FieldValues["_ComplianceTag"]
                        FileCreated         = $file.FieldValues["Created"]
                        FileModified        = $file.FieldValues["Modified"]
                        FileAuthor          = $file.FieldValues["Author"].LookupValue
                        HasLabel            = ($null -ne $file.FieldValues["_ComplianceTag"] -and $file.FieldValues["_ComplianceTag"] -ne "")
                    }
                    $fileInventory.Add($fileItem)
                }
                Write-Host "  Found $($files.Count) files" -ForegroundColor Green
            } else {
                Write-Host "  No files found in container" -ForegroundColor Yellow
            }

        } catch {
            Write-Warning "  Error retrieving files for container $($container.ContainerId): $_"
        }
    }

    return $fileInventory.ToArray()
}

# Execute file inventory retrieval
$fileInventory = Get-EmbeddedFileInventory -Containers $containers

# Display files missing sensitivity labels
$unlabeledFiles = $fileInventory | Where-Object { -not $_.HasLabel }
if ($unlabeledFiles.Count -gt 0) {
    Write-Host "`n=== FILES WITHOUT SENSITIVITY LABELS (COMPLIANCE GAP) ===" -ForegroundColor Red
    $unlabeledFiles | Format-Table ContainerName, FileName, FileType, FileCreated -AutoSize
} else {
    Write-Host "`nAll embedded files have sensitivity labels." -ForegroundColor Green
}

# Export full file inventory
$fileOutputFile = ".\embedded-file-inventory-$(Get-Date -Format 'yyyy-MM-dd').csv"
$fileInventory | Export-Csv -Path $fileOutputFile -NoTypeInformation -Encoding UTF8
Write-Host "`nFile inventory exported to: $fileOutputFile" -ForegroundColor Green
```

### Step 3.2 — Flag High-Risk Files for IB Review

```powershell
<#
.SYNOPSIS
    Identifies embedded files that may require Information Barrier assessment.

.DESCRIPTION
    Applies keyword-based heuristics to flag file names that suggest IB-sensitive
    content categories. This is a screening tool — all flagged files require
    manual IB assessment. Non-flagged files are not guaranteed to be IB-safe.
#>
function Invoke-IBRiskScreening {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [array]$FileInventory
    )

    # IB-risk keyword patterns — customize for your firm's terminology
    $ibRiskPatterns = @(
        "deal",
        "pipeline",
        "m&a",
        "acquisition",
        "merger",
        "research",
        "analyst",
        "rating",
        "recommendation",
        "price.?target",
        "mnpi",
        "material.?non.?public",
        "confidential",
        "restricted",
        "client",
        "customer",
        "prospect",
        "term.?sheet",
        "pitch",
        "roadshow",
        "ipo",
        "offering",
        "underwriting",
        "syndicate"
    )

    $flaggedFiles = [System.Collections.Generic.List[PSCustomObject]]::new()

    foreach ($file in $FileInventory) {
        foreach ($pattern in $ibRiskPatterns) {
            if ($file.FileName -imatch $pattern) {
                $flagged = $file | Select-Object *
                Add-Member -InputObject $flagged -MemberType NoteProperty -Name "IBRiskPattern" -Value $pattern
                $flaggedFiles.Add($flagged)
                break  # Only flag once per file even if multiple patterns match
            }
        }
    }

    return $flaggedFiles.ToArray()
}

$flaggedFiles = Invoke-IBRiskScreening -FileInventory $fileInventory

if ($flaggedFiles.Count -gt 0) {
    Write-Host "`n=== IB RISK SCREENING — FILES REQUIRING MANUAL IB ASSESSMENT ===" -ForegroundColor Red
    Write-Host "The following $($flaggedFiles.Count) files matched IB-risk keyword patterns." -ForegroundColor Red
    Write-Host "Each must be reviewed by Compliance before the agent remains in production." -ForegroundColor Red
    $flaggedFiles | Format-Table ContainerName, FileName, IBRiskPattern, FileSensitivityLabel -AutoSize

    # Export flagged files for compliance review
    $flaggedOutputFile = ".\ib-risk-flagged-files-$(Get-Date -Format 'yyyy-MM-dd').csv"
    $flaggedFiles | Export-Csv -Path $flaggedOutputFile -NoTypeInformation -Encoding UTF8
    Write-Host "`nFlagged file list exported to: $flaggedOutputFile" -ForegroundColor Yellow
} else {
    Write-Host "`nNo files matched IB-risk keyword patterns. Manual review still recommended for all Zone 2/3 agents." -ForegroundColor Yellow
}
```

---

## Section 4: Monitor for New Container Creation

This section sets up a PowerShell-based monitoring approach to detect when new Declarative Agent containers are created, enabling proactive compliance review.

### Step 4.1 — Baseline Container Count Check

```powershell
<#
.SYNOPSIS
    Compares current Declarative Agent container count against a saved baseline.

.DESCRIPTION
    Run this script on a scheduled basis (e.g., daily). If new containers are
    detected since the last baseline, alerts the SharePoint admin and compliance
    mailbox. Designed to be run as a scheduled task or Azure Automation runbook.

.PARAMETER BaselineFile
    Path to the CSV file containing the previous container baseline.

.PARAMETER AlertRecipients
    Array of email addresses to notify when new containers are detected.
    Requires ExchangeOnlineManagement or SMTP relay configuration.
#>
function Compare-ContainerBaseline {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaselineFile,

        [Parameter()]
        [string[]]$AlertRecipients = @("m365admin@yourdomain.com", "compliance@yourdomain.com")
    )

    # Get current containers
    $currentContainers = Get-DeclarativeAgentContainers

    if (-not (Test-Path $BaselineFile)) {
        # First run — create baseline
        $currentContainers | Export-Csv -Path $BaselineFile -NoTypeInformation -Encoding UTF8
        Write-Host "Baseline created with $($currentContainers.Count) containers at: $BaselineFile" -ForegroundColor Green
        return
    }

    # Load baseline
    $baselineContainers = Import-Csv -Path $BaselineFile

    # Find new containers
    $baselineIds = $baselineContainers.ContainerId
    $newContainers = $currentContainers | Where-Object {
        $_.ContainerId -notin $baselineIds
    }

    if ($newContainers.Count -gt 0) {
        Write-Host "`n=== NEW DECLARATIVE AGENT CONTAINERS DETECTED ===" -ForegroundColor Yellow
        Write-Host "Found $($newContainers.Count) new container(s) since last baseline check." -ForegroundColor Yellow
        $newContainers | Format-Table ContainerId, ContainerName, CreatedDateTime, SensitivityLabel -AutoSize

        # Send alert email (requires ExchangeOnlineManagement or SMTP relay)
        # Uncomment and configure for your environment:
        #
        # $emailBody = @"
        # NEW DECLARATIVE AGENT CONTAINERS DETECTED - Control 4.9 Alert
        #
        # $($newContainers.Count) new SharePoint Embedded container(s) associated with Declarative Agent
        # were detected since the last baseline check.
        #
        # New containers:
        # $($newContainers | ConvertTo-Csv -NoTypeInformation | Out-String)
        #
        # Action required: Complete IB assessment per Control 4.9 procedures.
        # "@
        #
        # Send-MgUserMail -UserId "m365admin@yourdomain.com" -BodyContent $emailBody ...

        # Update baseline with new containers
        $currentContainers | Export-Csv -Path $BaselineFile -NoTypeInformation -Encoding UTF8
        Write-Host "Baseline updated." -ForegroundColor Cyan

    } else {
        Write-Host "No new containers detected since last baseline check. Container count: $($currentContainers.Count)" -ForegroundColor Green
    }
}

# Execute baseline comparison
# Set baseline file path appropriate for your environment
$baselineFilePath = "C:\FSI-AgentGov\Baselines\declarative-agent-containers-baseline.csv"

Compare-ContainerBaseline -BaselineFile $baselineFilePath `
    -AlertRecipients @("m365admin@yourdomain.com", "compliance@yourdomain.com")
```

### Step 4.2 — Schedule the Monitoring Script

The monitoring script should run on a daily schedule. Options:

**Option A — Windows Task Scheduler:**
```powershell
# Create a scheduled task to run the container monitoring script daily
$action = New-ScheduledTaskAction -Execute "pwsh.exe" `
    -Argument "-NonInteractive -File C:\FSI-AgentGov\Scripts\Monitor-AgentContainers.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At "07:00AM"

$principal = New-ScheduledTaskPrincipal `
    -UserId "DOMAIN\svc-m365audit" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName "FSI-AgentGov-ContainerMonitor" `
    -Description "Control 4.9: Daily monitoring for new Declarative Agent containers" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal
```

**Option B — Azure Automation Runbook:**
```powershell
# Publish the monitoring script as an Azure Automation Runbook
# and configure a daily schedule via the Azure portal or az CLI.
# See your organization's Azure Automation runbook deployment procedures.
#
# az automation runbook create \
#   --resource-group rg-m365governance \
#   --automation-account-name aa-fsi-agentgov \
#   --name "Monitor-DeclarativeAgentContainers" \
#   --type PowerShell
```

---

## Section 5: Complete Quarterly Audit Script

This consolidated script runs the full quarterly audit workflow and produces a single audit report package.

```powershell
<#
.SYNOPSIS
    Runs the complete Control 4.9 quarterly embedded file content audit.

.DESCRIPTION
    Executes container enumeration, file inventory, sensitivity label check,
    IB risk screening, and produces a dated audit report package.

.PARAMETER OutputDirectory
    Directory where audit report files will be saved.

.PARAMETER TenantAdminUrl
    SharePoint Admin Center URL for the tenant.

.EXAMPLE
    .\Invoke-Control49QuarterlyAudit.ps1 `
        -OutputDirectory "C:\FSI-AgentGov\Audits\2026-Q1" `
        -TenantAdminUrl "https://contoso-admin.sharepoint.com"
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory,

    [Parameter(Mandatory = $true)]
    [string]$TenantAdminUrl,

    [Parameter()]
    [string]$TenantId = $env:AZURE_TENANT_ID,

    [Parameter()]
    [string]$ClientId = $env:AZURE_CLIENT_ID,

    [Parameter()]
    [string]$CertThumbprint = $env:AZURE_CERT_THUMBPRINT
)

$auditTimestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$auditDir = Join-Path $OutputDirectory $auditTimestamp
New-Item -ItemType Directory -Path $auditDir -Force | Out-Null

Write-Host "=== FSI-AgentGov Control 4.9 — Quarterly Embedded File Audit ===" -ForegroundColor Cyan
Write-Host "Audit timestamp: $auditTimestamp"
Write-Host "Output directory: $auditDir"
Write-Host ""

# Step 1: Connect
Write-Host "[1/5] Connecting to SharePoint Admin Center..." -ForegroundColor Yellow
Connect-PnPOnline -Url $TenantAdminUrl `
    -ClientId $ClientId `
    -Thumbprint $CertThumbprint `
    -Tenant $TenantId

# Step 2: Enumerate containers
Write-Host "[2/5] Enumerating Declarative Agent containers..." -ForegroundColor Yellow
$containers = Get-DeclarativeAgentContainers
$containers | Export-Csv -Path "$auditDir\01-container-inventory.csv" -NoTypeInformation -Encoding UTF8

# Step 3: Retrieve file inventory
Write-Host "[3/5] Retrieving embedded file inventory..." -ForegroundColor Yellow
$fileInventory = Get-EmbeddedFileInventory -Containers $containers
$fileInventory | Export-Csv -Path "$auditDir\02-file-inventory.csv" -NoTypeInformation -Encoding UTF8

# Step 4: Identify unlabeled files
Write-Host "[4/5] Checking for unlabeled files (compliance gap analysis)..." -ForegroundColor Yellow
$unlabeledFiles = $fileInventory | Where-Object { -not $_.HasLabel }
$unlabeledFiles | Export-Csv -Path "$auditDir\03-unlabeled-files-GAPS.csv" -NoTypeInformation -Encoding UTF8

# Step 5: IB risk screening
Write-Host "[5/5] Running IB risk screening..." -ForegroundColor Yellow
$flaggedFiles = Invoke-IBRiskScreening -FileInventory $fileInventory
$flaggedFiles | Export-Csv -Path "$auditDir\04-ib-risk-flagged-files.csv" -NoTypeInformation -Encoding UTF8

# Generate audit summary report
$summaryReport = @"
FSI-AgentGov Control 4.9 — Quarterly Embedded File Content Audit Report
Generated: $auditTimestamp
Auditor: $([System.Security.Principal.WindowsIdentity]::GetCurrent().Name)
Tenant Admin URL: $TenantAdminUrl

=== SUMMARY ===
Total Declarative Agent Containers:    $($containers.Count)
Containers with Sensitivity Labels:    $(($containers | Where-Object { $_.SensitivityLabel }).Count)
Containers WITHOUT Labels (GAP):       $(($containers | Where-Object { -not $_.SensitivityLabel }).Count)

Total Embedded Files:                  $($fileInventory.Count)
Files with Sensitivity Labels:         $(($fileInventory | Where-Object { $_.HasLabel }).Count)
Files WITHOUT Labels (GAP):            $($unlabeledFiles.Count)
Files Flagged for IB Review:           $($flaggedFiles.Count)

=== COMPLIANCE STATUS ===
$(if ($unlabeledFiles.Count -eq 0 -and $flaggedFiles.Count -eq 0) {
    "PASS — No unlabeled files detected. No files flagged for IB review."
} else {
    "ACTION REQUIRED — See gap files:
  - Unlabeled files: 03-unlabeled-files-GAPS.csv ($($unlabeledFiles.Count) items)
  - IB risk flagged: 04-ib-risk-flagged-files.csv ($($flaggedFiles.Count) items)"
})

=== AUDIT FILES ===
01-container-inventory.csv   - All Declarative Agent containers
02-file-inventory.csv        - All embedded files with metadata
03-unlabeled-files-GAPS.csv  - Files without sensitivity labels (compliance gaps)
04-ib-risk-flagged-files.csv - Files flagged for IB review by keyword screening

=== NEXT ACTIONS ===
1. Review all items in 03-unlabeled-files-GAPS.csv with file owners — apply sensitivity labels.
2. Submit 04-ib-risk-flagged-files.csv to Compliance for IB assessment.
3. Verify agent inventory (Control 3.1) is updated with current container IDs and IB assessment status.
4. Store this audit package in the examination-ready compliance file.
5. Schedule next quarterly audit.
"@

$summaryReport | Out-File -FilePath "$auditDir\00-audit-summary.txt" -Encoding UTF8

Write-Host "`n=== AUDIT COMPLETE ===" -ForegroundColor Green
Write-Host $summaryReport
Write-Host "`nAudit files saved to: $auditDir" -ForegroundColor Green
```

---

## Section 6: Verify Default Sensitivity Label Policy Configuration

```powershell
<#
.SYNOPSIS
    Verifies that a default sensitivity label policy is configured for documents.

.DESCRIPTION
    Checks Microsoft Purview label policies to confirm a default document label
    is set, which ensures unlabeled files uploaded to agent containers receive
    a baseline classification. Requires ExchangeOnlineManagement connection.
#>
function Test-DefaultSensitivityLabelPolicy {
    [CmdletBinding()]
    param()

    Write-Host "Checking default sensitivity label policy configuration..." -ForegroundColor Cyan

    try {
        # Retrieve all label policies
        $labelPolicies = Get-LabelPolicy -ErrorAction Stop

        $defaultLabelConfigured = $false

        foreach ($policy in $labelPolicies) {
            $settings = $policy.Settings

            # Check for default label setting on documents
            $defaultDocLabel = ($settings | Where-Object { $_ -match "defaultlabelid" })

            if ($defaultDocLabel) {
                Write-Host "Policy '$($policy.Name)' has a default document label configured." -ForegroundColor Green
                Write-Host "  Setting: $defaultDocLabel"
                $defaultLabelConfigured = $true
            }
        }

        if (-not $defaultLabelConfigured) {
            Write-Host "`nWARNING: No default sensitivity label policy configured for documents." -ForegroundColor Red
            Write-Host "Unlabeled files uploaded to agent containers will not receive automatic labels." -ForegroundColor Red
            Write-Host "Action: Configure a default label in Microsoft Purview › Information Protection › Label policies." -ForegroundColor Yellow
        }

        return $defaultLabelConfigured

    } catch {
        Write-Error "Failed to retrieve label policies. Verify ExchangeOnlineManagement connection and Compliance Administrator role: $_"
    }
}

# Connect to compliance center and run check
Connect-IPPSSession -UserPrincipalName "compliance-admin@yourdomain.com"
$labelPolicyStatus = Test-DefaultSensitivityLabelPolicy
```

---

## Quick Reference: Key PowerShell Commands

| Task | Command |
|---|---|
| Connect to SharePoint Admin | `Connect-PnPOnline -Url $TenantAdminUrl -Interactive` |
| List all Embedded containers | `Get-PnPContainer -IncludeAll` |
| Filter Declarative Agent containers | `Get-PnPContainer -IncludeAll \| Where-Object { $_.ApplicationName -eq "Declarative Agent" }` |
| Get container details by ID | `Get-PnPContainer -Identity $containerId` |
| Get files in container | `Get-PnPListItem -List "Documents" -PageSize 100` |
| Check label policies | `Get-LabelPolicy` (requires IPPSSession) |
| Export to CSV | `$data \| Export-Csv -Path $file -NoTypeInformation -Encoding UTF8` |

---
[Back to Control 4.9](../../../controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
