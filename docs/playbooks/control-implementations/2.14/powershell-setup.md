# PowerShell Setup: Control 2.14 - Training and Awareness Program

**Last Updated:** January 2026
**Modules Required:** Microsoft.Graph, ExchangeOnlineManagement

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.Graph -Force -Scope CurrentUser
Install-Module -Name ExchangeOnlineManagement -Force -Scope CurrentUser

# Connect to Microsoft Graph
Connect-MgGraph -Scopes "User.Read.All", "LearningContent.Read.All"
```

---

## Training Compliance Report Scripts

### Get Users by Role for Training Assignment

```powershell
<#
.SYNOPSIS
    Identifies users who need AI governance training based on role assignments

.DESCRIPTION
    Queries Azure AD for users with specific roles that require training

.EXAMPLE
    .\Get-TrainingRequiredUsers.ps1
#>

# Connect to Microsoft Graph
Connect-MgGraph -Scopes "User.Read.All", "RoleManagement.Read.All"

# Define roles that require AI governance training
$trainingRequiredRoles = @(
    "Power Platform Administrator",
    "Compliance Administrator",
    "SharePoint Administrator",
    "Exchange Administrator"
)

# Get all role assignments
$roleAssignments = Get-MgDirectoryRole | ForEach-Object {
    $role = $_
    $members = Get-MgDirectoryRoleMember -DirectoryRoleId $role.Id

    foreach ($member in $members) {
        [PSCustomObject]@{
            UserId = $member.Id
            RoleName = $role.DisplayName
            RoleId = $role.Id
        }
    }
}

# Filter to training-required roles
$usersNeedingTraining = $roleAssignments | Where-Object {
    $trainingRequiredRoles -contains $_.RoleName
}

# Get user details
$report = $usersNeedingTraining | ForEach-Object {
    $user = Get-MgUser -UserId $_.UserId
    [PSCustomObject]@{
        DisplayName = $user.DisplayName
        Email = $user.Mail
        Role = $_.RoleName
        Department = $user.Department
        TrainingRequired = "AI Governance Framework"
    }
}

$report | Format-Table
$report | Export-Csv -Path "Training-Required-Users-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
```

### Track Training Completion Status

```powershell
<#
.SYNOPSIS
    Tracks training completion status from a CSV roster

.DESCRIPTION
    Compares required training list against completion records

.PARAMETER RequiredUsersFile
    CSV file with users who need training

.PARAMETER CompletionRecordsFile
    CSV file with training completion records from LMS

.EXAMPLE
    .\Get-TrainingComplianceStatus.ps1 -RequiredUsersFile "required.csv" -CompletionRecordsFile "completed.csv"
#>

param(
    [string]$RequiredUsersFile = "Training-Required-Users.csv",
    [string]$CompletionRecordsFile = "Training-Completions.csv"
)

# Load data
$requiredUsers = Import-Csv $RequiredUsersFile
$completions = Import-Csv $CompletionRecordsFile

# Build completion lookup
$completionLookup = @{}
foreach ($completion in $completions) {
    $completionLookup[$completion.Email] = $completion.CompletionDate
}

# Generate compliance report
$complianceReport = $requiredUsers | ForEach-Object {
    $completed = $completionLookup.ContainsKey($_.Email)
    $completionDate = if ($completed) { $completionLookup[$_.Email] } else { $null }

    [PSCustomObject]@{
        DisplayName = $_.DisplayName
        Email = $_.Email
        Role = $_.Role
        TrainingCompleted = $completed
        CompletionDate = $completionDate
        Status = if ($completed) { "Compliant" } else { "Non-Compliant" }
    }
}

# Summary statistics
$total = $complianceReport.Count
$compliant = ($complianceReport | Where-Object { $_.Status -eq "Compliant" }).Count
$nonCompliant = $total - $compliant
$complianceRate = [math]::Round(($compliant / $total) * 100, 1)

Write-Host "`n=== Training Compliance Summary ===" -ForegroundColor Cyan
Write-Host "Total Users: $total"
Write-Host "Compliant: $compliant" -ForegroundColor Green
Write-Host "Non-Compliant: $nonCompliant" -ForegroundColor $(if ($nonCompliant -gt 0) { "Yellow" } else { "Green" })
Write-Host "Compliance Rate: $complianceRate%"

# Export detailed report
$complianceReport | Export-Csv -Path "Training-Compliance-Report-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
Write-Host "`nReport exported to Training-Compliance-Report-$(Get-Date -Format 'yyyyMMdd').csv"

# Return non-compliant users for follow-up
$nonCompliantUsers = $complianceReport | Where-Object { $_.Status -eq "Non-Compliant" }
if ($nonCompliantUsers) {
    Write-Host "`n=== Non-Compliant Users ===" -ForegroundColor Yellow
    $nonCompliantUsers | Format-Table DisplayName, Email, Role
}
```

### Send Training Reminder Emails

```powershell
<#
.SYNOPSIS
    Sends training reminder emails to non-compliant users

.DESCRIPTION
    Uses Exchange Online to send reminder emails

.PARAMETER NonCompliantFile
    CSV file with non-compliant users

.EXAMPLE
    .\Send-TrainingReminders.ps1 -NonCompliantFile "non-compliant.csv"
#>

param(
    [string]$NonCompliantFile = "Training-Non-Compliant.csv",
    [string]$SenderEmail = "aigovernance@company.com",
    [string]$TrainingUrl = "https://learning.company.com/ai-governance"
)

# Connect to Exchange Online
Connect-ExchangeOnline

# Load non-compliant users
$nonCompliant = Import-Csv $NonCompliantFile

foreach ($user in $nonCompliant) {
    $emailParams = @{
        From = $SenderEmail
        To = $user.Email
        Subject = "Action Required: AI Governance Training"
        Body = @"
Dear $($user.DisplayName),

Our records indicate that you have not yet completed the required AI Governance Training for your role as $($user.Role).

Please complete this training within 14 days by visiting:
$TrainingUrl

This training is required for compliance with our AI governance framework and regulatory obligations.

If you have questions, please contact the AI Governance team.

Best regards,
AI Governance Team
"@
        BodyAsHtml = $false
    }

    # Note: Actual sending would use Send-MailMessage or Graph API
    Write-Host "Would send reminder to: $($user.Email)" -ForegroundColor Yellow
}

Write-Host "`nReminder process completed for $($nonCompliant.Count) users"
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.14 - Training and Awareness Program

.DESCRIPTION
    Checks training program configuration and compliance rates

.EXAMPLE
    .\Validate-Control-2.14.ps1
#>

Write-Host "=== Control 2.14 Validation ===" -ForegroundColor Cyan

# Check 1: Verify training content exists
Write-Host "`n[Check 1] Training Content Configuration" -ForegroundColor Cyan
# This would integrate with your LMS API
Write-Host "[INFO] Verify training modules exist in LMS" -ForegroundColor Yellow
Write-Host "[INFO] Required modules: AI Governance Framework, Data Handling, Security Awareness"

# Check 2: Verify role-based assignments
Write-Host "`n[Check 2] Role-Based Training Assignments" -ForegroundColor Cyan
# Run the role identification script
Write-Host "[INFO] Run Get-TrainingRequiredUsers.ps1 to identify users needing training"

# Check 3: Compliance rate check
Write-Host "`n[Check 3] Training Compliance Rate" -ForegroundColor Cyan
Write-Host "[INFO] Target: 100% for Zone 3, 95% for Zone 2, 80% for Zone 1"

# Check 4: Evidence retention
Write-Host "`n[Check 4] Evidence Retention" -ForegroundColor Cyan
Write-Host "[INFO] Verify training records are retained per policy (7 years for regulated)"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
Write-Host "Document findings and remediate any gaps identified"
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Complete training and awareness configuration for Control 2.14

.DESCRIPTION
    Executes end-to-end training setup including:
    - User identification by role
    - Training compliance check
    - Non-compliant user reporting

.PARAMETER RequiredUsersFile
    CSV file with users requiring training

.PARAMETER CompletionRecordsFile
    CSV file with training completion records from LMS

.PARAMETER OutputPath
    Path for output reports

.EXAMPLE
    .\Configure-Control-2.14.ps1 -OutputPath ".\Training"

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.14 - Training and Awareness Program
#>

param(
    [string]$RequiredUsersFile,
    [string]$CompletionRecordsFile,
    [string]$OutputPath = ".\Training-Report"
)

try {
    Write-Host "=== Control 2.14: Training and Awareness Configuration ===" -ForegroundColor Cyan

    # Connect to Microsoft Graph
    Connect-MgGraph -Scopes "User.Read.All", "RoleManagement.Read.All"

    # Ensure output directory exists
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

    # Define roles that require AI governance training
    $trainingRequiredRoles = @(
        "Power Platform Administrator",
        "Compliance Administrator",
        "SharePoint Administrator",
        "Exchange Administrator"
    )

    Write-Host "`n[Step 1] Identifying users requiring training..." -ForegroundColor Cyan

    # Get all role assignments
    $roleAssignments = Get-MgDirectoryRole | ForEach-Object {
        $role = $_
        $members = Get-MgDirectoryRoleMember -DirectoryRoleId $role.Id -ErrorAction SilentlyContinue

        foreach ($member in $members) {
            [PSCustomObject]@{
                UserId = $member.Id
                RoleName = $role.DisplayName
                RoleId = $role.Id
            }
        }
    }

    # Filter to training-required roles
    $usersNeedingTraining = $roleAssignments | Where-Object {
        $trainingRequiredRoles -contains $_.RoleName
    }

    # Get user details
    $requiredUsers = $usersNeedingTraining | ForEach-Object {
        $user = Get-MgUser -UserId $_.UserId -ErrorAction SilentlyContinue
        if ($user) {
            [PSCustomObject]@{
                DisplayName = $user.DisplayName
                Email = $user.Mail
                Role = $_.RoleName
                Department = $user.Department
                TrainingRequired = "AI Governance Framework"
            }
        }
    } | Sort-Object Email -Unique

    Write-Host "  [INFO] Found $($requiredUsers.Count) users requiring training" -ForegroundColor Cyan
    $requiredUsers | Export-Csv -Path "$OutputPath\Training-Required-Users.csv" -NoTypeInformation

    # Check completions if file provided
    if ($CompletionRecordsFile -and (Test-Path $CompletionRecordsFile)) {
        Write-Host "`n[Step 2] Checking training completions..." -ForegroundColor Cyan
        $completions = Import-Csv $CompletionRecordsFile

        $completionLookup = @{}
        foreach ($completion in $completions) {
            $completionLookup[$completion.Email] = $completion.CompletionDate
        }

        $complianceReport = $requiredUsers | ForEach-Object {
            $completed = $completionLookup.ContainsKey($_.Email)
            [PSCustomObject]@{
                DisplayName = $_.DisplayName
                Email = $_.Email
                Role = $_.Role
                TrainingCompleted = $completed
                CompletionDate = if ($completed) { $completionLookup[$_.Email] } else { $null }
                Status = if ($completed) { "Compliant" } else { "Non-Compliant" }
            }
        }

        # Calculate statistics
        $total = $complianceReport.Count
        $compliant = ($complianceReport | Where-Object { $_.Status -eq "Compliant" }).Count
        $nonCompliant = $total - $compliant
        $complianceRate = if ($total -gt 0) { [math]::Round(($compliant / $total) * 100, 1) } else { 0 }

        Write-Host "`n=== Training Compliance Summary ===" -ForegroundColor Cyan
        Write-Host "Total Users: $total"
        Write-Host "Compliant: $compliant" -ForegroundColor Green
        Write-Host "Non-Compliant: $nonCompliant" -ForegroundColor $(if ($nonCompliant -gt 0) { "Yellow" } else { "Green" })
        Write-Host "Compliance Rate: $complianceRate%"

        $complianceReport | Export-Csv -Path "$OutputPath\Training-Compliance-Report.csv" -NoTypeInformation

        # Export non-compliant users
        $nonCompliantUsers = $complianceReport | Where-Object { $_.Status -eq "Non-Compliant" }
        if ($nonCompliantUsers) {
            $nonCompliantUsers | Export-Csv -Path "$OutputPath\Training-Non-Compliant.csv" -NoTypeInformation
        }
    } else {
        Write-Host "`n[INFO] No completion records provided - export required users list for LMS comparison" -ForegroundColor Yellow
    }

    Write-Host "`n[PASS] Control 2.14 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-MgGraph -ErrorAction SilentlyContinue
}
```

---

[Back to Control 2.14](../../../controls/pillar-2-management/2.14-training-and-awareness-program.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
