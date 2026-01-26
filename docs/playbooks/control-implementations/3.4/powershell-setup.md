# Control 3.4: Incident Reporting and Root Cause Analysis - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 3.4](../../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name PnP.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.Graph -Force -AllowClobber
Install-Module -Name Az.SecurityInsights -Force -AllowClobber

# Connect to services
Connect-PnPOnline -Url "https://[tenant].sharepoint.com/sites/AI-Governance" -Interactive
Connect-MgGraph -Scopes "SecurityEvents.Read.All", "SecurityIncident.ReadWrite.All"
Connect-AzAccount
```

---

## Create Incident Tracking List

```powershell
function New-IncidentTrackingList {
    param(
        [string]$SiteUrl = "https://[tenant].sharepoint.com/sites/AI-Governance",
        [string]$ListName = "AI Agent Incidents"
    )

    Write-Host "Creating Incident Tracking List..." -ForegroundColor Cyan

    Connect-PnPOnline -Url $SiteUrl -Interactive

    # Create list
    $list = New-PnPList -Title $ListName -Template GenericList

    # Add columns
    $columns = @(
        @{ Name = "IncidentID"; Type = "Text"; Required = $true },
        @{ Name = "Category"; Type = "Choice"; Choices = @("Security", "Compliance", "Availability", "Data Quality", "Privacy", "Bias/Fairness") },
        @{ Name = "Severity"; Type = "Choice"; Choices = @("Critical", "High", "Medium", "Low") },
        @{ Name = "AgentName"; Type = "Text"; Required = $true },
        @{ Name = "ReportedDate"; Type = "DateTime"; Required = $true },
        @{ Name = "Status"; Type = "Choice"; Choices = @("New", "Investigating", "Pending RCA", "Remediation", "Closed") },
        @{ Name = "AssignedTo"; Type = "User"; Required = $true },
        @{ Name = "Description"; Type = "Note"; Required = $true },
        @{ Name = "RootCause"; Type = "Note" },
        @{ Name = "CorrectiveActions"; Type = "Note" },
        @{ Name = "ResolutionDate"; Type = "DateTime" },
        @{ Name = "RegulatoryImpact"; Type = "Boolean" },
        @{ Name = "TimeToResolutionHours"; Type = "Number" }
    )

    foreach ($col in $columns) {
        switch ($col.Type) {
            "Text" { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type Text -Required:$col.Required }
            "Choice" { Add-PnPFieldFromXml -List $ListName -FieldXml "<Field Type='Choice' DisplayName='$($col.Name)'><CHOICES>$($col.Choices | ForEach-Object { "<CHOICE>$_</CHOICE>" })</CHOICES></Field>" }
            "DateTime" { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type DateTime }
            "Note" { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type Note }
            "User" { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type User }
            "Boolean" { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type Boolean }
            "Number" { Add-PnPField -List $ListName -DisplayName $col.Name -InternalName $col.Name -Type Number }
        }
    }

    Write-Host "Incident Tracking List created successfully" -ForegroundColor Green
    return $list
}
```

---

## Report New Incident

```powershell
function New-AgentIncident {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Title,
        [Parameter(Mandatory=$true)]
        [ValidateSet("Security", "Compliance", "Availability", "Data Quality", "Privacy", "Bias/Fairness")]
        [string]$Category,
        [Parameter(Mandatory=$true)]
        [ValidateSet("Critical", "High", "Medium", "Low")]
        [string]$Severity,
        [Parameter(Mandatory=$true)]
        [string]$AgentName,
        [Parameter(Mandatory=$true)]
        [string]$Description,
        [string]$AssignTo = "",
        [bool]$RegulatoryImpact = $false
    )

    Write-Host "Reporting new incident..." -ForegroundColor Cyan

    # Generate Incident ID
    $incidentId = "INC-$(Get-Date -Format 'yyyy-MMdd')-$(Get-Random -Minimum 100 -Maximum 999)"

    $incident = @{
        Title = $Title
        IncidentID = $incidentId
        Category = $Category
        Severity = $Severity
        AgentName = $AgentName
        Description = $Description
        ReportedDate = Get-Date
        Status = "New"
        RegulatoryImpact = $RegulatoryImpact
    }

    # Add to SharePoint
    $item = Add-PnPListItem -List "AI Agent Incidents" -Values $incident

    Write-Host "Incident created: $incidentId" -ForegroundColor Green

    # Trigger notifications based on severity
    if ($Severity -eq "Critical") {
        Write-Host "CRITICAL INCIDENT - Initiating emergency escalation" -ForegroundColor Red
        Send-CriticalIncidentNotification -IncidentId $incidentId -Details $incident
    }

    return $incident
}
```

---

## Update Incident Status

```powershell
function Update-IncidentStatus {
    param(
        [Parameter(Mandatory=$true)]
        [string]$IncidentId,
        [Parameter(Mandatory=$true)]
        [ValidateSet("Investigating", "Pending RCA", "Remediation", "Closed")]
        [string]$NewStatus,
        [string]$RootCause = "",
        [string]$CorrectiveActions = ""
    )

    Write-Host "Updating incident $IncidentId to status: $NewStatus" -ForegroundColor Cyan

    $updates = @{
        Status = $NewStatus
    }

    if ($NewStatus -eq "Closed") {
        if ([string]::IsNullOrEmpty($RootCause) -or [string]::IsNullOrEmpty($CorrectiveActions)) {
            Write-Error "Root Cause and Corrective Actions required to close incident"
            return
        }
        $updates.RootCause = $RootCause
        $updates.CorrectiveActions = $CorrectiveActions
        $updates.ResolutionDate = Get-Date
    }

    # Find and update the item
    $items = Get-PnPListItem -List "AI Agent Incidents" -Query "<View><Query><Where><Eq><FieldRef Name='IncidentID'/><Value Type='Text'>$IncidentId</Value></Eq></Where></Query></View>"

    if ($items.Count -eq 1) {
        Set-PnPListItem -List "AI Agent Incidents" -Identity $items[0].Id -Values $updates
        Write-Host "Incident updated successfully" -ForegroundColor Green
    }
    else {
        Write-Error "Incident not found: $IncidentId"
    }
}
```

---

## Generate Incident Metrics

```powershell
function Get-IncidentMetrics {
    param(
        [int]$DaysBack = 30
    )

    Write-Host "Generating incident metrics for last $DaysBack days..." -ForegroundColor Cyan

    $allIncidents = Get-PnPListItem -List "AI Agent Incidents" -PageSize 500

    $recentIncidents = $allIncidents | Where-Object {
        [DateTime]$_["ReportedDate"] -ge (Get-Date).AddDays(-$DaysBack)
    }

    $metrics = @{
        TotalIncidents = $recentIncidents.Count
        BySeverity = @{
            Critical = ($recentIncidents | Where-Object { $_["Severity"] -eq "Critical" }).Count
            High = ($recentIncidents | Where-Object { $_["Severity"] -eq "High" }).Count
            Medium = ($recentIncidents | Where-Object { $_["Severity"] -eq "Medium" }).Count
            Low = ($recentIncidents | Where-Object { $_["Severity"] -eq "Low" }).Count
        }
        OpenIncidents = ($recentIncidents | Where-Object { $_["Status"] -ne "Closed" }).Count
        RegulatoryImpactCount = ($recentIncidents | Where-Object { $_["RegulatoryImpact"] -eq $true }).Count
    }

    Write-Host "Incident Metrics Summary:" -ForegroundColor Green
    Write-Host "Total Incidents: $($metrics.TotalIncidents)"
    Write-Host "Open Incidents: $($metrics.OpenIncidents)"
    Write-Host "Critical: $($metrics.BySeverity.Critical) | High: $($metrics.BySeverity.High)"

    return $metrics
}
```

---

## Check SLA Compliance

```powershell
function Test-IncidentSlaCompliance {

    Write-Host "Checking SLA compliance for open incidents..." -ForegroundColor Cyan

    $slaThresholds = @{
        "Critical" = 0.25  # 15 minutes in hours
        "High" = 1         # 1 hour
        "Medium" = 4       # 4 hours
        "Low" = 24         # 24 hours
    }

    $openIncidents = Get-PnPListItem -List "AI Agent Incidents" -Query "<View><Query><Where><Neq><FieldRef Name='Status'/><Value Type='Text'>Closed</Value></Neq></Where></Query></View>"

    $slaBreaches = @()

    foreach ($incident in $openIncidents) {
        $severity = $incident["Severity"]
        $reportedDate = [DateTime]$incident["ReportedDate"]
        $hoursOpen = ((Get-Date) - $reportedDate).TotalHours
        $threshold = $slaThresholds[$severity]

        if ($hoursOpen -gt $threshold) {
            $slaBreaches += [PSCustomObject]@{
                IncidentId = $incident["IncidentID"]
                Severity = $severity
                HoursOpen = [math]::Round($hoursOpen, 1)
                SlaThreshold = $threshold
                BreachAmount = [math]::Round($hoursOpen - $threshold, 1)
            }
        }
    }

    if ($slaBreaches.Count -gt 0) {
        Write-Host "SLA BREACHES DETECTED:" -ForegroundColor Red
        $slaBreaches | Format-Table -AutoSize
    }
    else {
        Write-Host "All incidents within SLA" -ForegroundColor Green
    }

    return $slaBreaches
}
```

---

## Usage Examples

```powershell
# Create incident tracking list
New-IncidentTrackingList

# Report new incident
New-AgentIncident -Title "Customer data exposed in agent response" -Category "Privacy" -Severity "Critical" -AgentName "Account Inquiry Bot" -Description "Agent displayed another customer's account details" -RegulatoryImpact $true

# Update incident status
Update-IncidentStatus -IncidentId "INC-2026-0115-123" -NewStatus "Closed" -RootCause "Session management bug" -CorrectiveActions "Patched session handler"

# Generate metrics
Get-IncidentMetrics -DaysBack 30

# Check SLA compliance
Test-IncidentSlaCompliance
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 3.4 - Incident Reporting and Root Cause Analysis

.DESCRIPTION
    This script sets up incident tracking infrastructure:
    1. Creates SharePoint incident tracking list
    2. Configures incident categories and severity levels
    3. Sets up SLA monitoring

.PARAMETER SiteUrl
    SharePoint site URL for incident tracking

.EXAMPLE
    .\Configure-Control-3.4.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/AI-Governance"

.NOTES
    Last Updated: January 2026
    Related Control: Control 3.4 - Incident Reporting and Root Cause Analysis
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$SiteUrl = "https://[tenant].sharepoint.com/sites/AI-Governance"
)

try {
    # Connect to SharePoint
    Write-Host "Connecting to SharePoint..." -ForegroundColor Cyan
    Connect-PnPOnline -Url $SiteUrl -Interactive

    Write-Host "Configuring Control 3.4 Incident Tracking" -ForegroundColor Cyan

    # Check if list exists
    $existingList = Get-PnPList -Identity "AI Agent Incidents" -ErrorAction SilentlyContinue

    if (-not $existingList) {
        Write-Host "Creating Incident Tracking List..." -ForegroundColor Yellow
        New-IncidentTrackingList -SiteUrl $SiteUrl
    } else {
        Write-Host "Incident Tracking List already exists" -ForegroundColor Green
    }

    # Verify configuration
    $list = Get-PnPList -Identity "AI Agent Incidents"
    $fields = Get-PnPField -List "AI Agent Incidents"

    Write-Host "`nIncident Tracking Configuration:" -ForegroundColor Cyan
    Write-Host "  List: $($list.Title)" -ForegroundColor Green
    Write-Host "  Fields configured: $($fields.Count)" -ForegroundColor Green
    Write-Host "  URL: $SiteUrl/Lists/AI%20Agent%20Incidents" -ForegroundColor Green

    Write-Host "`n[PASS] Control 3.4 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup SharePoint connection
    Disconnect-PnPOnline -ErrorAction SilentlyContinue
}
```

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.2*
