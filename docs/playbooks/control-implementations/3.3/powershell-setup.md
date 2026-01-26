# Control 3.3: Compliance and Regulatory Reporting - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 3.3](../../../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.Graph -Force -AllowClobber
Install-Module -Name ExchangeOnlineManagement -Force -AllowClobber
Install-Module -Name PnP.PowerShell -Force -AllowClobber

# Connect to services
Connect-MgGraph -Scopes "Reports.Read.All", "Compliance.Read.All"
Connect-ExchangeOnline
Connect-PnPOnline -Url "https://[tenant].sharepoint.com/sites/AI-Compliance-Reports" -Interactive
```

---

## Control Status Report Generation

```powershell
function New-ControlStatusReport {
    param(
        [Parameter(Mandatory=$true)]
        [string]$OutputPath,
        [ValidateSet("Weekly", "Monthly", "Quarterly")]
        [string]$ReportType = "Weekly"
    )

    Write-Host "Generating $ReportType Control Status Report..." -ForegroundColor Cyan

    # Define control status structure
    $controlStatus = @{
        ReportDate = Get-Date -Format "yyyy-MM-dd"
        ReportType = $ReportType
        Pillars = @(
            @{
                Name = "Pillar 1: Security"
                Controls = @(
                    @{ Id = "1.1"; Name = "Restrict Agent Publishing"; Status = "Compliant"; LastReview = (Get-Date).AddDays(-7) },
                    @{ Id = "1.2"; Name = "Agent Registry Management"; Status = "Compliant"; LastReview = (Get-Date).AddDays(-14) },
                    @{ Id = "1.3"; Name = "SharePoint Content Governance"; Status = "Compliant"; LastReview = (Get-Date).AddDays(-10) }
                    # Add all Pillar 1 controls
                )
                ComplianceScore = 95
            },
            @{
                Name = "Pillar 2: Management"
                Controls = @(
                    @{ Id = "2.1"; Name = "Managed Environments"; Status = "Compliant"; LastReview = (Get-Date).AddDays(-5) },
                    @{ Id = "2.2"; Name = "Environment Groups"; Status = "Needs Attention"; LastReview = (Get-Date).AddDays(-30) }
                    # Add all Pillar 2 controls
                )
                ComplianceScore = 88
            },
            @{
                Name = "Pillar 3: Reporting"
                Controls = @(
                    @{ Id = "3.1"; Name = "Agent Inventory"; Status = "Compliant"; LastReview = (Get-Date).AddDays(-3) },
                    @{ Id = "3.2"; Name = "Usage Analytics"; Status = "Compliant"; LastReview = (Get-Date).AddDays(-7) }
                    # Add all Pillar 3 controls
                )
                ComplianceScore = 92
            },
            @{
                Name = "Pillar 4: SharePoint"
                Controls = @(
                    @{ Id = "4.1"; Name = "Agent Source Governance"; Status = "Compliant"; LastReview = (Get-Date).AddDays(-14) }
                    # Add all Pillar 4 controls
                )
                ComplianceScore = 97
            }
        )
    }

    # Calculate overall score
    $overallScore = ($controlStatus.Pillars | ForEach-Object { $_.ComplianceScore } |
        Measure-Object -Average).Average

    $controlStatus.OverallComplianceScore = [math]::Round($overallScore, 1)

    # Generate HTML report
    $htmlReport = New-ComplianceHtmlReport -ControlStatus $controlStatus

    $htmlReport | Out-File -FilePath $OutputPath -Encoding UTF8

    Write-Host "Report generated: $OutputPath" -ForegroundColor Green
    Write-Host "Overall Compliance Score: $($controlStatus.OverallComplianceScore)%" -ForegroundColor $(
        if ($controlStatus.OverallComplianceScore -ge 90) { "Green" }
        elseif ($controlStatus.OverallComplianceScore -ge 75) { "Yellow" }
        else { "Red" }
    )

    return $controlStatus
}
```

---

## Regulatory Alignment Report

```powershell
function New-RegulatoryAlignmentReport {
    param(
        [string]$Regulation = "All",
        [string]$OutputPath = ".\RegulatoryAlignmentReport.html"
    )

    Write-Host "Generating Regulatory Alignment Report..." -ForegroundColor Cyan

    $regulations = @{
        "FINRA_4511" = @{
            Name = "FINRA Rule 4511 - Books and Records"
            Requirements = @(
                @{ Requirement = "Retain business records for required period"; Control = "1.9, 2.13"; Status = "Compliant" },
                @{ Requirement = "Maintain records in accessible format"; Control = "2.13, 3.1"; Status = "Compliant" },
                @{ Requirement = "Preserve electronic communications"; Control = "1.7, 1.10"; Status = "Compliant" }
            )
        }
        "SEC_17a-4" = @{
            Name = "SEC Rule 17a-4 - Records Preservation"
            Requirements = @(
                @{ Requirement = "WORM storage for required records"; Control = "2.13"; Status = "Compliant" },
                @{ Requirement = "Index and retrieve records"; Control = "3.1"; Status = "Compliant" },
                @{ Requirement = "Third-party access letter"; Control = "2.13"; Status = "Compliant" }
            )
        }
        "SOX_404" = @{
            Name = "SOX Section 404 - Internal Controls"
            Requirements = @(
                @{ Requirement = "Document IT general controls"; Control = "2.8, 2.1"; Status = "Compliant" },
                @{ Requirement = "Access control and segregation of duties"; Control = "2.8"; Status = "Compliant" },
                @{ Requirement = "Change management controls"; Control = "2.3, 2.4"; Status = "Compliant" }
            )
        }
        "GLBA_501b" = @{
            Name = "GLBA Section 501(b) - Safeguards Rule"
            Requirements = @(
                @{ Requirement = "Protect NPI confidentiality"; Control = "1.5, 1.15"; Status = "Compliant" },
                @{ Requirement = "Monitor for unauthorized access"; Control = "3.2, 1.8"; Status = "Compliant" },
                @{ Requirement = "Third-party oversight"; Control = "2.7"; Status = "Compliant" }
            )
        }
    }

    # Calculate compliance by regulation
    $summary = $regulations.GetEnumerator() | ForEach-Object {
        $compliantCount = ($_.Value.Requirements | Where-Object { $_.Status -eq "Compliant" }).Count
        $totalCount = $_.Value.Requirements.Count

        [PSCustomObject]@{
            Regulation = $_.Value.Name
            Compliant = $compliantCount
            Total = $totalCount
            Percentage = [math]::Round(($compliantCount / $totalCount) * 100, 0)
        }
    }

    Write-Host "Regulatory Alignment Summary:" -ForegroundColor Green
    $summary | Format-Table -AutoSize

    return $summary
}
```

---

## Examination Package Generator

```powershell
function New-ExaminationPackage {
    param(
        [Parameter(Mandatory=$true)]
        [ValidateSet("FINRA", "SEC", "OCC", "State")]
        [string]$Regulator,
        [string]$OutputFolder = ".\ExamPackage"
    )

    Write-Host "Generating $Regulator Examination Ready Package..." -ForegroundColor Cyan

    # Create output folder
    New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null

    # Define package contents by regulator
    $packageContents = @{
        "FINRA" = @{
            "01-AI-Governance-Framework-Overview.pdf" = "Framework documentation"
            "02-Agent-Inventory-Full-List.xlsx" = "Complete agent inventory"
            "03-Supervisory-Procedures-WSP.pdf" = "Written Supervisory Procedures"
            "04-Control-Status-Summary.pdf" = "Current control compliance status"
            "05-Usage-Analytics-90-Days.xlsx" = "Agent usage data"
            "06-Incident-Log.xlsx" = "Incident tracking log"
            "07-Training-Completion-Records.xlsx" = "Staff training records"
            "08-Policy-Documents/" = "All AI governance policies"
        }
        "SEC" = @{
            "01-Records-Retention-Policy.pdf" = "17a-4 compliant retention policy"
            "02-Agent-Interaction-Logs.xlsx" = "Customer interaction records"
            "03-WORM-Storage-Certification.pdf" = "Storage compliance certification"
            "04-Access-Control-Documentation.pdf" = "Access management evidence"
            "05-Audit-Trail-Export.xlsx" = "Unified audit log export"
        }
        "OCC" = @{
            "01-Third-Party-Risk-Assessment.pdf" = "Vendor risk documentation"
            "02-Technology-Risk-Controls.pdf" = "IT control documentation"
            "03-Business-Continuity-Plans.pdf" = "BCP documentation"
            "04-Change-Management-Evidence.xlsx" = "Change control records"
            "05-Security-Assessment-Results.pdf" = "Security testing evidence"
        }
    }

    Write-Host "Package Contents for $Regulator Examination:" -ForegroundColor Yellow
    $packageContents[$Regulator].GetEnumerator() | ForEach-Object {
        Write-Host "  - $($_.Key): $($_.Value)" -ForegroundColor Gray
    }

    # Create manifest
    $manifest = @{
        Regulator = $Regulator
        GeneratedDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        GeneratedBy = (Get-MgContext).Account
        Contents = $packageContents[$Regulator]
        Instructions = "Upload all documents to secure examination portal within 48 hours of request"
    }

    $manifest | ConvertTo-Json -Depth 3 | Out-File "$OutputFolder\MANIFEST.json"

    Write-Host "Package manifest created at: $OutputFolder\MANIFEST.json" -ForegroundColor Green

    return $manifest
}
```

---

## Archive Report to SharePoint

```powershell
function Save-ComplianceReportToSharePoint {
    param(
        [Parameter(Mandatory=$true)]
        [string]$ReportPath,
        [Parameter(Mandatory=$true)]
        [string]$LibraryPath
    )

    Write-Host "Archiving report to SharePoint..." -ForegroundColor Cyan

    $fileName = Split-Path $ReportPath -Leaf

    try {
        Add-PnPFile -Path $ReportPath -Folder $LibraryPath

        Write-Host "Report archived: $LibraryPath/$fileName" -ForegroundColor Green

        return $true
    }
    catch {
        Write-Error "Failed to archive report: $_"
        return $false
    }
}
```

---

## Usage Examples

```powershell
# Generate control status report
New-ControlStatusReport -OutputPath ".\WeeklyComplianceReport.html" -ReportType "Weekly"

# Generate regulatory alignment report
New-RegulatoryAlignmentReport -Regulation "All"

# Generate examination package
New-ExaminationPackage -Regulator "FINRA" -OutputFolder ".\FINRA_Exam_Package"
```

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.2*
