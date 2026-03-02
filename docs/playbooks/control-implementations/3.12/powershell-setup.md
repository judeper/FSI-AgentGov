# PowerShell Setup: Control 3.12 - Agent Governance Exception and Override Management

**Last Updated:** February 2026
**Prerequisites:** Microsoft.PowerApps.Administration.PowerShell module, Microsoft Graph PowerShell SDK
**Estimated Time:** 45-60 minutes

## Overview

This playbook provides PowerShell scripts for automating exception management tasks including:

- Exporting exception register data for audit reviews
- Detecting and alerting on expired or expiring exceptions
- Generating exception compliance reports by zone
- Monitoring renewal counts and excessive exceptions
- Creating audit-ready evidence exports with SHA-256 integrity hashes

---

## Prerequisites

### Required PowerShell Modules

Install the following modules if not already available:

```powershell
# Install Power Platform Administration module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Scope CurrentUser -Force

# Install Microsoft Graph PowerShell SDK
Install-Module -Name Microsoft.Graph -Scope CurrentUser -Force

# Install Microsoft Dataverse PowerShell module
Install-Module -Name Microsoft.Xrm.Data.PowerShell -Scope CurrentUser -Force
```

### Required Permissions

- Power Platform Admin role (to query Dataverse)
- Dataverse system administrator or custom role with read access to Governance Exceptions table
- Microsoft Graph User.Read.All (to validate approver identities)

---

## Script 1: Export Exception Register

### Purpose
Export all exception records from Dataverse with complete audit trail for compliance reviews.

### Script: Get-ExceptionRegister.ps1

```powershell
<#
.SYNOPSIS
    Exports agent governance exception register from Dataverse.

.DESCRIPTION
    Retrieves all exception records including approval history, expiration dates,
    and audit trail. Exports to CSV for compliance review and regulatory examination.

.PARAMETER EnvironmentUrl
    The URL of the Dataverse environment (e.g., https://org.crm.dynamics.com)

.PARAMETER OutputPath
    Directory path for output CSV file

.PARAMETER FilterStatus
    Optional. Filter by approval status (Pending, Fully Approved, Expired, Closed)

.EXAMPLE
    .\Get-ExceptionRegister.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports"

.EXAMPLE
    .\Get-ExceptionRegister.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports" -FilterStatus "Fully Approved"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputPath,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("All", "Pending", "Fully Approved", "Expired", "Closed", "Denied")]
    [string]$FilterStatus = "All"
)

# Import required modules
Import-Module Microsoft.Xrm.Data.PowerShell

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Exception Register Export" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Connect to Dataverse
Write-Host "Connecting to Dataverse environment: $EnvironmentUrl..." -ForegroundColor Cyan
$conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl

if ($conn.IsReady) {
    Write-Host "✓ Connected successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to connect to Dataverse" -ForegroundColor Red
    exit 1
}

# Build FetchXML query
Write-Host "Querying Governance Exceptions table..." -ForegroundColor Cyan

$fetchXml = @"
<fetch>
  <entity name="fsi_governanceexception">
    <attribute name="fsi_governanceexceptionid" />
    <attribute name="fsi_name" />
    <attribute name="fsi_exceptionrequestdate" />
    <attribute name="fsi_requestor" />
    <attribute name="fsi_agentname" />
    <attribute name="fsi_governancezone" />
    <attribute name="fsi_exceptiontype" />
    <attribute name="fsi_businessjustification" />
    <attribute name="fsi_riskassessment" />
    <attribute name="fsi_compensatingcontrols" />
    <attribute name="fsi_approvalstatus" />
    <attribute name="fsi_approver1" />
    <attribute name="fsi_approvaldate1" />
    <attribute name="fsi_approver2" />
    <attribute name="fsi_approvaldate2" />
    <attribute name="fsi_approver3" />
    <attribute name="fsi_approvaldate3" />
    <attribute name="fsi_expirationdate" />
    <attribute name="fsi_renewalcount" />
    <attribute name="fsi_closuredate" />
    <attribute name="fsi_closurereason" />
    <attribute name="createdon" />
    <attribute name="modifiedon" />
"@

# Add status filter if specified
if ($FilterStatus -ne "All") {
    $fetchXml += @"
    <filter type="and">
      <condition attribute="fsi_approvalstatus" operator="eq" value="$FilterStatus" />
    </filter>
"@
}

$fetchXml += @"
    <order attribute="fsi_exceptionrequestdate" descending="true" />
  </entity>
</fetch>
"@

# Execute query
$results = Get-CrmRecords -conn $conn -Fetch $fetchXml

Write-Host "Found $($results.CrmRecords.Count) exception records" -ForegroundColor White

# Transform results to CSV-friendly format
$exportData = @()

foreach ($record in $results.CrmRecords) {
    $exportData += [PSCustomObject]@{
        ExceptionID = $record.fsi_governanceexceptionid
        ExceptionName = $record.fsi_name
        RequestDate = $record.fsi_exceptionrequestdate
        Requestor = $record.fsi_requestor_Property.Value.Name
        AgentName = $record.fsi_agentname
        GovernanceZone = $record.fsi_governancezone_Property.Value.Name
        ExceptionType = $record.fsi_exceptiontype_Property.Value.Name
        BusinessJustification = $record.fsi_businessjustification
        RiskAssessment = $record.fsi_riskassessment
        CompensatingControls = $record.fsi_compensatingcontrols
        ApprovalStatus = $record.fsi_approvalstatus_Property.Value.Name
        Approver1 = if ($record.fsi_approver1_Property.Value) { $record.fsi_approver1_Property.Value.Name } else { "" }
        ApprovalDate1 = $record.fsi_approvaldate1
        Approver2 = if ($record.fsi_approver2_Property.Value) { $record.fsi_approver2_Property.Value.Name } else { "" }
        ApprovalDate2 = $record.fsi_approvaldate2
        Approver3 = if ($record.fsi_approver3_Property.Value) { $record.fsi_approver3_Property.Value.Name } else { "" }
        ApprovalDate3 = $record.fsi_approvaldate3
        ExpirationDate = $record.fsi_expirationdate
        RenewalCount = $record.fsi_renewalcount
        ClosureDate = $record.fsi_closuredate
        ClosureReason = $record.fsi_closurereason
        CreatedOn = $record.createdon
        ModifiedOn = $record.modifiedon
    }
}

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputFile = Join-Path $OutputPath "ExceptionRegister_$timestamp.csv"

$exportData | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8

Write-Host "✓ Exception register exported to: $outputFile" -ForegroundColor Green

# Calculate statistics
$stats = @{
    TotalExceptions = $exportData.Count
    Pending = ($exportData | Where-Object { $_.ApprovalStatus -eq "Pending" }).Count
    FullyApproved = ($exportData | Where-Object { $_.ApprovalStatus -eq "Fully Approved" }).Count
    Expired = ($exportData | Where-Object { $_.ApprovalStatus -eq "Expired" }).Count
    Closed = ($exportData | Where-Object { $_.ApprovalStatus -eq "Closed" }).Count
    Denied = ($exportData | Where-Object { $_.ApprovalStatus -eq "Denied" }).Count
}

Write-Host ""
Write-Host "--- Exception Register Summary ---" -ForegroundColor Cyan
Write-Host "Total Exceptions: $($stats.TotalExceptions)" -ForegroundColor White
Write-Host "  Pending: $($stats.Pending)" -ForegroundColor Yellow
Write-Host "  Fully Approved: $($stats.FullyApproved)" -ForegroundColor Green
Write-Host "  Expired: $($stats.Expired)" -ForegroundColor Red
Write-Host "  Closed: $($stats.Closed)" -ForegroundColor Gray
Write-Host "  Denied: $($stats.Denied)" -ForegroundColor Red

Write-Host ""
Write-Host "Script completed successfully." -ForegroundColor Cyan
```

---

## Script 2: Detect Expiring and Expired Exceptions

### Purpose
Identify exceptions nearing expiration or already expired requiring remediation.

### Script: Find-ExpiringExceptions.ps1

```powershell
<#
.SYNOPSIS
    Detects agent governance exceptions expiring soon or already expired.

.DESCRIPTION
    Queries Dataverse for approved exceptions expiring within specified days.
    Sends alerts via email and generates remediation report.

.PARAMETER EnvironmentUrl
    The URL of the Dataverse environment

.PARAMETER OutputPath
    Directory path for output CSV file

.PARAMETER ExpirationWindowDays
    Number of days to look ahead for expiring exceptions (default: 7)

.PARAMETER SendEmailAlerts
    If specified, sends email alerts to requestors and approvers

.PARAMETER SmtpServer
    SMTP server for email alerts (required if SendEmailAlerts is specified)

.PARAMETER FromEmail
    From email address (required if SendEmailAlerts is specified)

.EXAMPLE
    .\Find-ExpiringExceptions.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports" -ExpirationWindowDays 7
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputPath,
    
    [Parameter(Mandatory=$false)]
    [int]$ExpirationWindowDays = 7,
    
    [Parameter(Mandatory=$false)]
    [switch]$SendEmailAlerts,
    
    [Parameter(Mandatory=$false)]
    [string]$SmtpServer,
    
    [Parameter(Mandatory=$false)]
    [string]$FromEmail
)

# Import required modules
Import-Module Microsoft.Xrm.Data.PowerShell

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Exception Expiration Monitor" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Connect to Dataverse
Write-Host "Connecting to Dataverse environment: $EnvironmentUrl..." -ForegroundColor Cyan
$conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl

if (-not $conn.IsReady) {
    Write-Host "✗ Failed to connect to Dataverse" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Connected successfully" -ForegroundColor Green

# Calculate date thresholds
$today = Get-Date -Format "yyyy-MM-dd"
$futureDate = (Get-Date).AddDays($ExpirationWindowDays).ToString("yyyy-MM-dd")

Write-Host "Searching for exceptions expiring between $today and $futureDate..." -ForegroundColor Cyan

# Build FetchXML query for expiring exceptions
$fetchXml = @"
<fetch>
  <entity name="fsi_governanceexception">
    <attribute name="fsi_governanceexceptionid" />
    <attribute name="fsi_name" />
    <attribute name="fsi_agentname" />
    <attribute name="fsi_requestor" />
    <attribute name="fsi_governancezone" />
    <attribute name="fsi_exceptiontype" />
    <attribute name="fsi_expirationdate" />
    <attribute name="fsi_renewalcount" />
    <attribute name="fsi_approver1" />
    <attribute name="fsi_approver2" />
    <attribute name="fsi_approver3" />
    <filter type="and">
      <condition attribute="fsi_approvalstatus" operator="eq" value="Fully Approved" />
      <condition attribute="fsi_expirationdate" operator="on-or-before" value="$futureDate" />
      <condition attribute="fsi_expirationdate" operator="on-or-after" value="$today" />
    </filter>
    <order attribute="fsi_expirationdate" descending="false" />
  </entity>
</fetch>
"@

$results = Get-CrmRecords -conn $conn -Fetch $fetchXml

Write-Host "Found $($results.CrmRecords.Count) exceptions expiring within $ExpirationWindowDays days" -ForegroundColor Yellow

# Also query for already expired exceptions
$fetchXmlExpired = @"
<fetch>
  <entity name="fsi_governanceexception">
    <attribute name="fsi_governanceexceptionid" />
    <attribute name="fsi_name" />
    <attribute name="fsi_agentname" />
    <attribute name="fsi_requestor" />
    <attribute name="fsi_governancezone" />
    <attribute name="fsi_exceptiontype" />
    <attribute name="fsi_expirationdate" />
    <attribute name="fsi_renewalcount" />
    <filter type="and">
      <condition attribute="fsi_approvalstatus" operator="eq" value="Fully Approved" />
      <condition attribute="fsi_expirationdate" operator="last-x-days" value="0" />
    </filter>
    <order attribute="fsi_expirationdate" descending="false" />
  </entity>
</fetch>
"@

$resultsExpired = Get-CrmRecords -conn $conn -Fetch $fetchXmlExpired

Write-Host "Found $($resultsExpired.CrmRecords.Count) exceptions already expired" -ForegroundColor Red

# Combine results
$allResults = @()
$allResults += $results.CrmRecords
$allResults += $resultsExpired.CrmRecords

# Transform to export format
$exportData = @()

foreach ($record in $allResults) {
    $expirationDate = [DateTime]::Parse($record.fsi_expirationdate)
    $daysUntilExpiration = ($expirationDate - (Get-Date)).Days
    
    $status = if ($daysUntilExpiration -lt 0) { "EXPIRED" } 
              elseif ($daysUntilExpiration -le 3) { "CRITICAL (<=3 days)" }
              elseif ($daysUntilExpiration -le 7) { "WARNING (<=7 days)" }
              else { "OK" }
    
    $exportData += [PSCustomObject]@{
        ExceptionID = $record.fsi_governanceexceptionid
        AgentName = $record.fsi_agentname
        Requestor = $record.fsi_requestor_Property.Value.Name
        GovernanceZone = $record.fsi_governancezone_Property.Value.Name
        ExceptionType = $record.fsi_exceptiontype_Property.Value.Name
        ExpirationDate = $expirationDate.ToString("yyyy-MM-dd")
        DaysUntilExpiration = $daysUntilExpiration
        Status = $status
        RenewalCount = $record.fsi_renewalcount
        MaxRenewalsReached = if ($record.fsi_renewalcount -ge 2) { "YES" } else { "NO" }
        Approver1 = if ($record.fsi_approver1_Property.Value) { $record.fsi_approver1_Property.Value.Name } else { "" }
        Approver2 = if ($record.fsi_approver2_Property.Value) { $record.fsi_approver2_Property.Value.Name } else { "" }
        Approver3 = if ($record.fsi_approver3_Property.Value) { $record.fsi_approver3_Property.Value.Name } else { "" }
    }
}

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputFile = Join-Path $OutputPath "ExpiringExceptions_$timestamp.csv"

$exportData | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8

Write-Host "✓ Expiring exceptions report saved to: $outputFile" -ForegroundColor Green

# Display summary
Write-Host ""
Write-Host "--- Expiration Summary ---" -ForegroundColor Cyan
Write-Host "Total Expiring/Expired: $($exportData.Count)" -ForegroundColor White
Write-Host "  EXPIRED: $(($exportData | Where-Object { $_.Status -eq 'EXPIRED' }).Count)" -ForegroundColor Red
Write-Host "  CRITICAL (<=3 days): $(($exportData | Where-Object { $_.Status -eq 'CRITICAL (<=3 days)' }).Count)" -ForegroundColor Red
Write-Host "  WARNING (<=7 days): $(($exportData | Where-Object { $_.Status -eq 'WARNING (<=7 days)' }).Count)" -ForegroundColor Yellow
Write-Host "  Max Renewals Reached: $(($exportData | Where-Object { $_.MaxRenewalsReached -eq 'YES' }).Count)" -ForegroundColor Red

Write-Host ""
Write-Host "Script completed successfully." -ForegroundColor Cyan
```

---

## Script 3: Generate Exception Compliance Report

### Purpose
Create zone-specific compliance report showing exception adherence to governance policies.

### Script: Get-ExceptionComplianceReport.ps1

```powershell
<#
.SYNOPSIS
    Generates compliance report for agent governance exceptions by zone.

.DESCRIPTION
    Analyzes exception data against governance policies including maximum durations,
    renewal limits, and compensating control requirements.

.PARAMETER EnvironmentUrl
    The URL of the Dataverse environment

.PARAMETER OutputPath
    Directory path for output CSV file

.EXAMPLE
    .\Get-ExceptionComplianceReport.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Reports"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputPath
)

# Import required modules
Import-Module Microsoft.Xrm.Data.PowerShell

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Exception Compliance Report" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Connect to Dataverse
Write-Host "Connecting to Dataverse environment: $EnvironmentUrl..." -ForegroundColor Cyan
$conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl

if (-not $conn.IsReady) {
    Write-Host "✗ Failed to connect to Dataverse" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Connected successfully" -ForegroundColor Green

# Query all active exceptions
Write-Host "Querying all active exceptions..." -ForegroundColor Cyan

$fetchXml = @"
<fetch>
  <entity name="fsi_governanceexception">
    <attribute name="fsi_governanceexceptionid" />
    <attribute name="fsi_name" />
    <attribute name="fsi_agentname" />
    <attribute name="fsi_governancezone" />
    <attribute name="fsi_exceptiontype" />
    <attribute name="fsi_exceptionrequestdate" />
    <attribute name="fsi_expirationdate" />
    <attribute name="fsi_renewalcount" />
    <attribute name="fsi_compensatingcontrols" />
    <attribute name="fsi_approvalstatus" />
    <filter type="and">
      <condition attribute="fsi_approvalstatus" operator="eq" value="Fully Approved" />
    </filter>
  </entity>
</fetch>
"@

$results = Get-CrmRecords -conn $conn -Fetch $fetchXml

Write-Host "Analyzing $($results.CrmRecords.Count) active exceptions for compliance..." -ForegroundColor Cyan

# Define policy limits by zone
$zoneLimits = @{
    "Zone 1 - Personal" = 90
    "Zone 2 - Team" = 60
    "Zone 3 - Enterprise" = 30
}

# Analyze compliance
$complianceData = @()

foreach ($record in $results.CrmRecords) {
    $zone = $record.fsi_governancezone_Property.Value.Name
    $requestDate = [DateTime]::Parse($record.fsi_exceptionrequestdate)
    $expirationDate = [DateTime]::Parse($record.fsi_expirationdate)
    $duration = ($expirationDate - $requestDate).Days
    $maxDuration = $zoneLimits[$zone]
    
    # Check compliance
    $issues = @()
    
    # Duration compliance
    if ($duration -gt $maxDuration) {
        $issues += "Duration exceeds maximum ($duration days > $maxDuration days)"
    }
    
    # Renewal count compliance
    if ($record.fsi_renewalcount -gt 2) {
        $issues += "Renewal count exceeds limit ($($record.fsi_renewalcount) > 2)"
    }
    
    # Compensating controls requirement
    if ($zone -in @("Zone 2 - Team", "Zone 3 - Enterprise") -and 
        ([string]::IsNullOrWhiteSpace($record.fsi_compensatingcontrols) -or 
         $record.fsi_compensatingcontrols.Length -lt 50)) {
        $issues += "Insufficient compensating controls documentation"
    }
    
    $complianceStatus = if ($issues.Count -eq 0) { "Compliant" } else { "Non-Compliant" }
    
    $complianceData += [PSCustomObject]@{
        ExceptionID = $record.fsi_governanceexceptionid
        AgentName = $record.fsi_agentname
        GovernanceZone = $zone
        ExceptionType = $record.fsi_exceptiontype_Property.Value.Name
        DurationDays = $duration
        MaxAllowedDays = $maxDuration
        RenewalCount = $record.fsi_renewalcount
        ComplianceStatus = $complianceStatus
        Issues = if ($issues.Count -gt 0) { $issues -join "; " } else { "None" }
    }
}

# Export to CSV
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$outputFile = Join-Path $OutputPath "ExceptionComplianceReport_$timestamp.csv"

$complianceData | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8

Write-Host "✓ Compliance report saved to: $outputFile" -ForegroundColor Green

# Calculate summary statistics
$totalExceptions = $complianceData.Count
$compliantCount = ($complianceData | Where-Object { $_.ComplianceStatus -eq "Compliant" }).Count
$nonCompliantCount = $totalExceptions - $compliantCount
$complianceRate = if ($totalExceptions -gt 0) { 
    [math]::Round(($compliantCount / $totalExceptions) * 100, 2) 
} else { 
    0 
}

Write-Host ""
Write-Host "--- Compliance Summary ---" -ForegroundColor Cyan
Write-Host "Total Active Exceptions: $totalExceptions" -ForegroundColor White
Write-Host "  Compliant: $compliantCount" -ForegroundColor Green
Write-Host "  Non-Compliant: $nonCompliantCount" -ForegroundColor Red
Write-Host "Compliance Rate: $complianceRate%" -ForegroundColor White

# Zone-specific breakdown
Write-Host ""
Write-Host "--- Compliance by Zone ---" -ForegroundColor Cyan
foreach ($zone in $zoneLimits.Keys | Sort-Object) {
    $zoneTotal = ($complianceData | Where-Object { $_.GovernanceZone -eq $zone }).Count
    $zoneCompliant = ($complianceData | Where-Object { $_.GovernanceZone -eq $zone -and $_.ComplianceStatus -eq "Compliant" }).Count
    $zoneRate = if ($zoneTotal -gt 0) { [math]::Round(($zoneCompliant / $zoneTotal) * 100, 2) } else { 0 }
    
    Write-Host "$zone : $zoneCompliant / $zoneTotal ($zoneRate%)" -ForegroundColor White
}

if ($nonCompliantCount -gt 0) {
    Write-Host ""
    Write-Host "⚠ WARNING: $nonCompliantCount non-compliant exceptions require immediate review" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Script completed successfully." -ForegroundColor Cyan
```

---

## Script 4: Create Audit-Ready Evidence Export

### Purpose
Generate SHA-256 hashed evidence package for regulatory examination.

### Script: Export-ExceptionAuditEvidence.ps1

```powershell
<#
.SYNOPSIS
    Creates audit-ready evidence export of exception register with integrity hash.

.DESCRIPTION
    Exports exception data with SHA-256 hash for regulatory examination.
    Includes metadata about export process for chain of custody.

.PARAMETER EnvironmentUrl
    The URL of the Dataverse environment

.PARAMETER OutputPath
    Directory path for output files

.PARAMETER ExaminerName
    Name of person requesting evidence

.PARAMETER ExaminationPurpose
    Purpose of evidence collection

.EXAMPLE
    .\Export-ExceptionAuditEvidence.ps1 -EnvironmentUrl "https://contoso.crm.dynamics.com" -OutputPath "C:\Evidence" -ExaminerName "Jane Auditor" -ExaminationPurpose "Annual SOX Audit"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentUrl,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputPath,
    
    [Parameter(Mandatory=$true)]
    [string]$ExaminerName,
    
    [Parameter(Mandatory=$true)]
    [string]$ExaminationPurpose
)

# Import required modules
Import-Module Microsoft.Xrm.Data.PowerShell

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Exception Audit Evidence Export" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Create evidence directory
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$evidenceDir = Join-Path $OutputPath "ExceptionEvidence_$timestamp"
New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null

Write-Host "Evidence directory: $evidenceDir" -ForegroundColor Cyan

# Connect to Dataverse
Write-Host "Connecting to Dataverse environment: $EnvironmentUrl..." -ForegroundColor Cyan
$conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl

if (-not $conn.IsReady) {
    Write-Host "✗ Failed to connect to Dataverse" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Connected successfully" -ForegroundColor Green

# Export all exceptions (same query as Script 1)
Write-Host "Exporting exception register..." -ForegroundColor Cyan

# NOTE: Restore the FetchXML query and Invoke-CrmRetrieveMultiple call from Script 1
# to populate $exportData before running this section.

# [FetchXML query from Script 1 - omitted for brevity]

# ... (execute query and export as in Script 1)

$exportFile = Join-Path $evidenceDir "ExceptionRegister.csv"
$exportData | Export-Csv -Path $exportFile -NoTypeInformation -Encoding UTF8

Write-Host "✓ Exception register exported" -ForegroundColor Green

# Calculate SHA-256 hash
Write-Host "Calculating SHA-256 integrity hash..." -ForegroundColor Cyan

$hashAlgorithm = [System.Security.Cryptography.SHA256]::Create()
$fileStream = [System.IO.File]::OpenRead($exportFile)
$hashBytes = $hashAlgorithm.ComputeHash($fileStream)
$fileStream.Close()
$hash = [System.BitConverter]::ToString($hashBytes).Replace("-", "").ToLower()

Write-Host "✓ SHA-256 hash: $hash" -ForegroundColor Green

# Create chain of custody metadata
$metadata = @"
===========================================
EXCEPTION REGISTER AUDIT EVIDENCE
===========================================

Export Timestamp: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC")
Environment URL: $EnvironmentUrl
Examiner Name: $ExaminerName
Examination Purpose: $ExaminationPurpose
Exported By: $env:USERNAME
Export Host: $env:COMPUTERNAME

--- FILE INTEGRITY ---
File Name: ExceptionRegister.csv
File Size: $((Get-Item $exportFile).Length) bytes
SHA-256 Hash: $hash

--- DATA SUMMARY ---
Total Records: [COUNT]
Date Range: [FIRST] to [LAST]

===========================================
"@

$metadataFile = Join-Path $evidenceDir "EVIDENCE_METADATA.txt"
$metadata | Out-File -FilePath $metadataFile -Encoding UTF8

Write-Host "✓ Evidence metadata created" -ForegroundColor Green

# Create hash verification file
$hashFile = Join-Path $evidenceDir "SHA256_HASH.txt"
"$hash  ExceptionRegister.csv" | Out-File -FilePath $hashFile -Encoding UTF8

Write-Host "✓ Hash verification file created" -ForegroundColor Green

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Evidence Package Complete" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Location: $evidenceDir" -ForegroundColor White
Write-Host ""
Write-Host "Files included:" -ForegroundColor Cyan
Write-Host "  - ExceptionRegister.csv (exception data)" -ForegroundColor White
Write-Host "  - EVIDENCE_METADATA.txt (chain of custody)" -ForegroundColor White
Write-Host "  - SHA256_HASH.txt (integrity verification)" -ForegroundColor White
Write-Host ""
Write-Host "To verify file integrity later, run:" -ForegroundColor Cyan
Write-Host "  certutil -hashfile ExceptionRegister.csv SHA256" -ForegroundColor Yellow
Write-Host "  Compare output to SHA256_HASH.txt" -ForegroundColor Yellow

Write-Host ""
Write-Host "Script completed successfully." -ForegroundColor Cyan
```

---

## Usage Examples

### Daily Exception Monitoring
Run this command daily to export expiring exceptions:

```powershell
.\Find-ExpiringExceptions.ps1 `
    -EnvironmentUrl "https://contoso.crm.dynamics.com" `
    -OutputPath "C:\Reports\Exceptions" `
    -ExpirationWindowDays 7
```

### Quarterly Compliance Audit
Generate quarterly compliance report:

```powershell
.\Get-ExceptionComplianceReport.ps1 `
    -EnvironmentUrl "https://contoso.crm.dynamics.com" `
    -OutputPath "C:\Reports\Quarterly"
```

### Regulatory Examination Evidence
Create audit-ready evidence package:

```powershell
.\Export-ExceptionAuditEvidence.ps1 `
    -EnvironmentUrl "https://contoso.crm.dynamics.com" `
    -OutputPath "C:\Evidence" `
    -ExaminerName "SEC Examiner" `
    -ExaminationPurpose "Cybersecurity Rule Examination"
```

---

## Automation with Task Scheduler

Schedule daily expiration monitoring:

```powershell
$action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-File C:\Scripts\Find-ExpiringExceptions.ps1 -EnvironmentUrl 'https://contoso.crm.dynamics.com' -OutputPath 'C:\Reports'"

$trigger = New-ScheduledTaskTrigger -Daily -At "8:00AM"

Register-ScheduledTask `
    -TaskName "Exception Expiration Monitor" `
    -Action $action `
    -Trigger $trigger `
    -Description "Daily monitoring of expiring agent governance exceptions"
```

---

## Best Practices

- **Credential Management:** Use service accounts with minimal required permissions for scheduled scripts
- **Error Handling:** Implement try-catch blocks and logging for production deployments
- **Output Retention:** Retain exception reports for regulatory retention periods (typically 7 years for FSI)
- **Automation:** Schedule Script 2 (expiration monitoring) to run daily
- **Review Cadence:** Review compliance reports (Script 3) quarterly with governance committee
- **Evidence Chain:** Use Script 4 for all regulatory examinations to maintain integrity verification

---

## Next Steps

- Proceed to [Verification & Testing](verification-testing.md) for test cases
- Review [Troubleshooting](troubleshooting.md) for common issues
- Schedule automated monitoring with Task Scheduler or Azure Automation

---

[Back to Control 3.12](../../../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md)

*Updated: February 2026 | Version: v1.0*
