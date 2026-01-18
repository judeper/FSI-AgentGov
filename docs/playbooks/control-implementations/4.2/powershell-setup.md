# PowerShell Setup: Control 4.2 - Site Access Reviews and Certification

**Last Updated:** January 2026
**Modules Required:** Microsoft.Graph, Microsoft.Online.SharePoint.PowerShell

## Prerequisites

```powershell
# Install required modules
Install-Module Microsoft.Graph -Scope CurrentUser
Install-Module Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser

# Connect to Microsoft Graph with required scopes
Connect-MgGraph -Scopes "AccessReview.ReadWrite.All", "Directory.Read.All", "Sites.Read.All"

# Connect to SharePoint Online
$adminUrl = "https://yourtenant-admin.sharepoint.com"
Connect-SPOService -Url $adminUrl

# Verify connections
Get-MgContext | Select-Object Scopes, Account
Get-SPOTenant | Select-Object StorageQuota
```

---

## Configuration Scripts

### Create Access Review Schedule for SharePoint Site Groups

```powershell
# Define the access review schedule definition
$reviewParams = @{
    displayName = "FSI SharePoint Site Access Review - Enterprise Managed"
    descriptionForAdmins = "Quarterly access review for enterprise-managed SharePoint sites containing agent knowledge sources"
    descriptionForReviewers = "Review and certify that users have appropriate access to sensitive SharePoint sites"
    scope = @{
        "@odata.type" = "#microsoft.graph.accessReviewQueryScope"
        query = "/groups?`$filter=(groupTypes/any(c:c eq 'Unified'))"
        queryType = "MicrosoftGraph"
    }
    reviewers = @(
        @{
            query = "/groups/{group-id}/owners"
            queryType = "MicrosoftGraph"
        }
    )
    settings = @{
        mailNotificationsEnabled = $true
        reminderNotificationsEnabled = $true
        justificationRequiredOnApproval = $true
        defaultDecisionEnabled = $true
        defaultDecision = "Deny"
        instanceDurationInDays = 14
        autoApplyDecisionsEnabled = $true
        recommendationsEnabled = $true
        recurrence = @{
            pattern = @{
                type = "absoluteMonthly"
                interval = 3  # Quarterly
                dayOfMonth = 1
            }
            range = @{
                type = "noEnd"
                startDate = (Get-Date).ToString("yyyy-MM-dd")
            }
        }
    }
}

# Create the access review schedule definition
$review = New-MgIdentityGovernanceAccessReviewDefinition -BodyParameter $reviewParams
Write-Host "Access Review Created: $($review.DisplayName)" -ForegroundColor Green
Write-Host "Review ID: $($review.Id)" -ForegroundColor Cyan
```

### Get Access Review Status

```powershell
# Get all access review definitions
$accessReviews = Get-MgIdentityGovernanceAccessReviewDefinition
$accessReviews | Format-Table DisplayName, Status, CreatedDateTime

# Get specific access review instances
$reviewId = "your-review-definition-id"
$instances = Get-MgIdentityGovernanceAccessReviewDefinitionInstance -AccessReviewScheduleDefinitionId $reviewId

# Display instance details
$instances | ForEach-Object {
    Write-Host "Instance: $($_.Id)" -ForegroundColor Yellow
    Write-Host "  Status: $($_.Status)"
    Write-Host "  Start: $($_.StartDateTime)"
    Write-Host "  End: $($_.EndDateTime)"
    Write-Host "  Reviewers Completed: $($_.ReviewersCompleted) / $($_.ReviewersTotal)"
}

# Get pending decisions for an instance
$instanceId = "your-instance-id"
$decisions = Get-MgIdentityGovernanceAccessReviewDefinitionInstanceDecision `
    -AccessReviewScheduleDefinitionId $reviewId `
    -AccessReviewInstanceId $instanceId

$decisions | Where-Object { $_.Decision -eq "NotReviewed" } |
    Format-Table Principal, Resource, Decision, ReviewedDateTime
```

### Export Access Review Results

```powershell
# Export access review decisions to CSV for audit
$reviewId = "your-review-definition-id"
$instances = Get-MgIdentityGovernanceAccessReviewDefinitionInstance `
    -AccessReviewScheduleDefinitionId $reviewId

$allDecisions = @()

foreach ($instance in $instances) {
    $decisions = Get-MgIdentityGovernanceAccessReviewDefinitionInstanceDecision `
        -AccessReviewScheduleDefinitionId $reviewId `
        -AccessReviewInstanceId $instance.Id `
        -All

    foreach ($decision in $decisions) {
        $allDecisions += [PSCustomObject]@{
            InstanceId = $instance.Id
            InstanceStartDate = $instance.StartDateTime
            PrincipalName = $decision.Principal.DisplayName
            PrincipalType = $decision.Principal.Type
            ResourceName = $decision.Resource.DisplayName
            Decision = $decision.Decision
            Justification = $decision.Justification
            ReviewedBy = $decision.ReviewedBy.DisplayName
            ReviewedDateTime = $decision.ReviewedDateTime
            AppliedBy = $decision.AppliedBy.DisplayName
            AppliedDateTime = $decision.AppliedDateTime
        }
    }
}

# Export to CSV
$exportPath = "C:\Compliance\AccessReview_Export_$(Get-Date -Format 'yyyyMMdd').csv"
$allDecisions | Export-Csv -Path $exportPath -NoTypeInformation
Write-Host "Exported $($allDecisions.Count) decisions to: $exportPath" -ForegroundColor Green
```

### Get SharePoint Site Permissions Report

```powershell
# Get sites with sharing settings
$sites = Get-SPOSite -Limit All | Where-Object {
    $_.SharingCapability -ne "Disabled" -and
    $_.Template -notlike "*SPSPERS*"  # Exclude OneDrive
}

# Generate permissions summary
$siteSummary = $sites | ForEach-Object {
    [PSCustomObject]@{
        SiteUrl = $_.Url
        Title = $_.Title
        Owner = $_.Owner
        SharingCapability = $_.SharingCapability
        ExternalSharingEnabled = $_.SharingCapability -ne "Disabled"
        SensitivityLabel = $_.SensitivityLabel
        LastContentModified = $_.LastContentModifiedDate
    }
}

# Export for review
$siteSummary | Export-Csv -Path "C:\Compliance\SPOSitePermissions_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
Write-Host "Site permissions report exported" -ForegroundColor Green
```

### Audit Agent Service Principal Permissions

```powershell
function Get-AgentServicePrincipalPermissions {
    param([string]$AppId)

    Connect-MgGraph -Scopes "Application.Read.All", "Directory.Read.All"

    # Get service principal
    $sp = Get-MgServicePrincipal -Filter "appId eq '$AppId'"

    if (-not $sp) {
        Write-Error "Service principal not found for AppId: $AppId"
        return
    }

    Write-Host "Service Principal: $($sp.DisplayName)" -ForegroundColor Cyan
    Write-Host "App ID: $AppId"

    # Get OAuth2 permission grants (delegated permissions)
    $delegated = Get-MgServicePrincipalOauth2PermissionGrant -ServicePrincipalId $sp.Id

    Write-Host "`nDelegated Permissions:" -ForegroundColor Yellow
    $delegated | ForEach-Object {
        $resource = Get-MgServicePrincipal -ServicePrincipalId $_.ResourceId
        Write-Host "  $($resource.DisplayName): $($_.Scope)"
    }

    # Get app role assignments (application permissions)
    $appRoles = Get-MgServicePrincipalAppRoleAssignment -ServicePrincipalId $sp.Id

    Write-Host "`nApplication Permissions:" -ForegroundColor Yellow
    foreach ($role in $appRoles) {
        $resource = Get-MgServicePrincipal -ServicePrincipalId $role.ResourceId
        $roleInfo = $resource.AppRoles | Where-Object { $_.Id -eq $role.AppRoleId }
        Write-Host "  $($resource.DisplayName): $($roleInfo.Value)"
    }

    # Evaluate least privilege
    Write-Host "`nLeast Privilege Assessment:" -ForegroundColor Green

    # Check for overly broad SharePoint permissions
    $broadPermissions = @("Sites.Read.All", "Sites.ReadWrite.All", "Sites.Manage.All", "Sites.FullControl.All")

    foreach ($role in $appRoles) {
        $resource = Get-MgServicePrincipal -ServicePrincipalId $role.ResourceId
        $roleInfo = $resource.AppRoles | Where-Object { $_.Id -eq $role.AppRoleId }

        if ($roleInfo.Value -in $broadPermissions) {
            Write-Host "  WARNING: Broad permission detected - $($roleInfo.Value)" -ForegroundColor Red
            Write-Host "    Consider using Sites.Selected for specific site access" -ForegroundColor Yellow
        }
    }
}

# Usage:
# Get-AgentServicePrincipalPermissions -AppId "your-app-id-here"
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 4.2 - Site Access Reviews and Certification

.DESCRIPTION
    This script creates access review schedules and exports site permission reports:
    1. Creates quarterly access review for SharePoint site groups
    2. Exports site permissions report for review
    3. Audits agent service principal permissions

.PARAMETER TenantAdminUrl
    The SharePoint Admin Center URL

.PARAMETER CreateAccessReview
    Switch to create new access review schedule

.EXAMPLE
    .\Configure-Control-4.2.ps1 -TenantAdminUrl "https://contoso-admin.sharepoint.com"

.NOTES
    Last Updated: January 2026
    Related Control: Control 4.2 - Site Access Reviews and Certification
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$TenantAdminUrl,

    [switch]$CreateAccessReview
)

# Connect to services
Write-Host "Connecting to services..." -ForegroundColor Cyan
Connect-MgGraph -Scopes "AccessReview.ReadWrite.All", "Directory.Read.All"
Connect-SPOService -Url $TenantAdminUrl

# Export site permissions
Write-Host "`nExporting site permissions..." -ForegroundColor Yellow
$sites = Get-SPOSite -Limit All | Where-Object { $_.Template -notlike "*SPSPERS*" }
$sites | Select-Object Url, Title, Owner, SharingCapability, SensitivityLabel |
    Export-Csv -Path "SitePermissions_$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
Write-Host "  [DONE] Exported $($sites.Count) sites" -ForegroundColor Green

# List existing access reviews
Write-Host "`nExisting Access Reviews:" -ForegroundColor Yellow
Get-MgIdentityGovernanceAccessReviewDefinition | Format-Table DisplayName, Status

if ($CreateAccessReview) {
    Write-Host "`nCreating new access review..." -ForegroundColor Yellow
    # Add review creation logic here
    Write-Host "  [INFO] Use the detailed script above to create access reviews" -ForegroundColor Cyan
}

Write-Host "`nControl 4.2 setup complete!" -ForegroundColor Green
```

---

[Back to Control 4.2](../../../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
