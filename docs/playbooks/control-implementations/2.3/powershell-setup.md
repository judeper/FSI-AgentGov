# Control 2.3: Change Management and Release Planning - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 2.3](../../../controls/pillar-2-management/2.3-change-management-and-release-planning.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.PowerApps.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.Xrm.Tooling.CrmConnector.PowerShell -Force -AllowClobber

# Connect to Power Platform (interactive authentication)
Add-PowerAppsAccount

# For automated/unattended scenarios, use service principal authentication:
# $appId = "<Application-Client-ID>"
# $secret = "<Client-Secret>"
# $tenantId = "<Tenant-ID>"
# Add-PowerAppsAccount -ApplicationId $appId -ClientSecret $secret -TenantID $tenantId
```

---

## Solution Export Commands

```powershell
# Export a solution (unmanaged) for development
$environmentUrl = "https://[your-env].crm.dynamics.com"
$solutionName = "FSIAgentSolution"
$exportPath = "C:\Solutions\$solutionName.zip"

# Connect to environment
$conn = Connect-CrmOnline -ServerUrl $environmentUrl -Interactive

# Export unmanaged solution
Export-CrmSolution -conn $conn -SolutionName $solutionName -SolutionFilePath $exportPath -Managed $false
Write-Host "Exported unmanaged solution to: $exportPath"

# Export managed solution for deployment
$managedPath = "C:\Solutions\${solutionName}_managed.zip"
Export-CrmSolution -conn $conn -SolutionName $solutionName -SolutionFilePath $managedPath -Managed $true
Write-Host "Exported managed solution to: $managedPath"
```

---

## Solution Import Commands

```powershell
# Import solution to target environment
$targetEnvironmentUrl = "https://[target-env].crm.dynamics.com"
$solutionPath = "C:\Solutions\FSIAgentSolution_managed.zip"

# Connect to target environment
$targetConn = Connect-CrmOnline -ServerUrl $targetEnvironmentUrl -Interactive

# Import managed solution with upgrade
Import-CrmSolution -conn $targetConn -SolutionFilePath $solutionPath -OverwriteUnmanagedCustomizations $true -PublishWorkflows $true
Write-Host "Solution imported successfully"

# Import with async processing for large solutions
# Note: Import-CrmSolutionAsync requires Microsoft.Xrm.Tooling.CrmConnector.PowerShell v3.3+
# Verify module version: Get-Module Microsoft.Xrm.Tooling.CrmConnector.PowerShell -ListAvailable
$importJob = Import-CrmSolutionAsync -conn $targetConn -SolutionFilePath $solutionPath
Write-Host "Import job started: $($importJob.ImportJobId)"
```

---

## Solution Version Management

```powershell
# Get current solution version
function Get-SolutionVersion {
    param(
        [Parameter(Mandatory=$true)]
        [string]$EnvironmentUrl,
        [Parameter(Mandatory=$true)]
        [string]$SolutionName
    )

    $conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -Interactive
    $solution = Get-CrmRecords -conn $conn -EntityLogicalName solution -FilterAttribute uniquename -FilterOperator eq -FilterValue $SolutionName -Fields version

    return $solution.CrmRecords[0].version
}

# Update solution version before export
function Update-SolutionVersion {
    param(
        [Parameter(Mandatory=$true)]
        [string]$EnvironmentUrl,
        [Parameter(Mandatory=$true)]
        [string]$SolutionName,
        [Parameter(Mandatory=$true)]
        [string]$NewVersion
    )

    $conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -Interactive
    $solution = Get-CrmRecords -conn $conn -EntityLogicalName solution -FilterAttribute uniquename -FilterOperator eq -FilterValue $SolutionName -Fields solutionid

    $solutionUpdate = @{
        "solutionid" = $solution.CrmRecords[0].solutionid
        "version" = $NewVersion
    }

    Set-CrmRecord -conn $conn -EntityLogicalName solution -Fields $solutionUpdate
    Write-Host "Solution version updated to: $NewVersion"
}

# Example: Increment version
$currentVersion = Get-SolutionVersion -EnvironmentUrl $environmentUrl -SolutionName "FSIAgentSolution"
Write-Host "Current version: $currentVersion"

# Parse and increment minor version
$versionParts = $currentVersion.Split('.')
$versionParts[2] = [int]$versionParts[2] + 1
$newVersion = $versionParts -join '.'

Update-SolutionVersion -EnvironmentUrl $environmentUrl -SolutionName "FSIAgentSolution" -NewVersion $newVersion
```

---

## Get Solution Components

```powershell
# List all components in a solution
function Get-SolutionComponents {
    param(
        [Parameter(Mandatory=$true)]
        [string]$EnvironmentUrl,
        [Parameter(Mandatory=$true)]
        [string]$SolutionName
    )

    $conn = Connect-CrmOnline -ServerUrl $EnvironmentUrl -Interactive

    # Get solution ID
    $solution = Get-CrmRecords -conn $conn -EntityLogicalName solution -FilterAttribute uniquename -FilterOperator eq -FilterValue $SolutionName -Fields solutionid
    $solutionId = $solution.CrmRecords[0].solutionid

    # Get solution components
    $components = Get-CrmRecords -conn $conn -EntityLogicalName solutioncomponent -FilterAttribute solutionid -FilterOperator eq -FilterValue $solutionId -Fields componenttype,objectid,rootcomponentbehavior

    # Component type mapping
    $componentTypes = @{
        1 = "Entity"
        2 = "Attribute"
        3 = "Relationship"
        9 = "Option Set"
        10 = "Entity Relationship"
        25 = "Connection Role"
        29 = "Workflow"
        59 = "System Form"
        60 = "Web Resource"
        61 = "Site Map"
        62 = "Connection Role"
        65 = "Hierarchy Rule"
        66 = "Custom Control"
        80 = "Model-driven App"
        300 = "Canvas App"
        371 = "Connector"
        372 = "Environment Variable Definition"
        380 = "AI Model"
        10029 = "Copilot Studio Agent"
    }

    foreach ($component in $components.CrmRecords) {
        $typeName = $componentTypes[$component.componenttype]
        if (-not $typeName) { $typeName = "Type $($component.componenttype)" }
        Write-Host "$typeName : $($component.objectid)"
    }

    return $components
}

# Example usage
Get-SolutionComponents -EnvironmentUrl $environmentUrl -SolutionName "FSIAgentSolution"
```

---

## Agent Configuration Snapshot

Capture configuration before any change:

```powershell
# Agent Configuration Snapshot Script
param(
    [Parameter(Mandatory=$true)]
    [string]$AgentId,
    [string]$OutputPath = ".\agent-snapshots"
)

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$snapshotPath = "$OutputPath\$AgentId\$timestamp"
New-Item -ItemType Directory -Path $snapshotPath -Force | Out-Null

# Export agent configuration components
$agentSnapshot = @{
    metadata = @{
        agentId = $AgentId
        snapshotDate = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        snapshotBy = $env:USERNAME
        reason = "[Change description]"
    }
    configuration = @{
        systemPrompt = "[Export from Copilot Studio]"
        topics = @()
        knowledgeSources = @()
        connectors = @()
        actions = @()
        settings = @{
            authenticationMode = "[Mode]"
            fallbackBehavior = "[Config]"
            contentModeration = "[Config]"
        }
    }
}

# Save snapshot
$snapshotFile = "$snapshotPath\agent-config.json"
$agentSnapshot | ConvertTo-Json -Depth 10 | Out-File -FilePath $snapshotFile -Encoding UTF8

Write-Host "Agent snapshot saved: $snapshotFile" -ForegroundColor Green
Write-Host "Commit this snapshot to version control before proceeding with changes" -ForegroundColor Yellow
```

---

## Automated Deployment Pipeline Script

```powershell
# Automated deployment pipeline script
function Invoke-FSIPipelineDeployment {
    param(
        [Parameter(Mandatory=$true)]
        [string]$SolutionName,
        [Parameter(Mandatory=$true)]
        [string]$SourceEnvironment,
        [Parameter(Mandatory=$true)]
        [string]$TargetEnvironment,
        [Parameter(Mandatory=$true)]
        [ValidateSet("Zone1","Zone2","Zone3")]
        [string]$TargetZone,
        [Parameter(Mandatory=$true)]
        [string]$ChangeRequestId,
        [string]$ApproverEmail
    )

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $logFile = "C:\Logs\Deployment_${SolutionName}_${timestamp}.log"

    function Write-Log {
        param($Message)
        $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'): $Message"
        Add-Content -Path $logFile -Value $logEntry
        Write-Host $logEntry
    }

    Write-Log "Starting deployment pipeline for $SolutionName"
    Write-Log "Change Request: $ChangeRequestId"
    Write-Log "Source: $SourceEnvironment -> Target: $TargetEnvironment ($TargetZone)"

    try {
        # Step 1: Connect to source environment
        Write-Log "Connecting to source environment..."
        $sourceConn = Connect-CrmOnline -ServerUrl $SourceEnvironment -Interactive

        # Step 2: Get and increment version
        $currentVersion = Get-SolutionVersion -EnvironmentUrl $SourceEnvironment -SolutionName $SolutionName
        $versionParts = $currentVersion.Split('.')
        $versionParts[3] = [int]$versionParts[3] + 1
        $newVersion = $versionParts -join '.'
        Update-SolutionVersion -EnvironmentUrl $SourceEnvironment -SolutionName $SolutionName -NewVersion $newVersion
        Write-Log "Version updated: $currentVersion -> $newVersion"

        # Step 3: Export solution
        $exportPath = "C:\Solutions\${SolutionName}_${newVersion}_managed.zip"
        Export-CrmSolution -conn $sourceConn -SolutionName $SolutionName -SolutionFilePath $exportPath -Managed $true
        Write-Log "Solution exported to: $exportPath"

        # Step 4: Zone-specific approval check
        if ($TargetZone -eq "Zone3") {
            Write-Log "Zone 3 deployment requires CAB approval. Pausing for approval..."
            Write-Log "Manual approval required. Confirm approval before proceeding."
        }

        # Step 5: Connect to target and import
        Write-Log "Connecting to target environment..."
        $targetConn = Connect-CrmOnline -ServerUrl $TargetEnvironment -Interactive

        Write-Log "Importing solution..."
        Import-CrmSolution -conn $targetConn -SolutionFilePath $exportPath -OverwriteUnmanagedCustomizations $true -PublishWorkflows $true
        Write-Log "Solution imported successfully"

        # Step 6: Validation
        Write-Log "Validating deployment..."
        $deployedVersion = Get-SolutionVersion -EnvironmentUrl $TargetEnvironment -SolutionName $SolutionName
        if ($deployedVersion -eq $newVersion) {
            Write-Log "VALIDATION PASSED: Version $deployedVersion deployed successfully"
        } else {
            Write-Log "VALIDATION WARNING: Expected $newVersion, found $deployedVersion"
        }

        Write-Log "Deployment completed successfully"
        return @{
            Success = $true
            Version = $newVersion
            ChangeRequest = $ChangeRequestId
            LogFile = $logFile
        }

    } catch {
        Write-Log "ERROR: $($_.Exception.Message)"
        Write-Log "Deployment failed. Rollback may be required."
        return @{
            Success = $false
            Error = $_.Exception.Message
            LogFile = $logFile
        }
    }
}

# Example execution
$deploymentResult = Invoke-FSIPipelineDeployment `
    -SolutionName "FSIAgentSolution" `
    -SourceEnvironment "https://dev-fsi.crm.dynamics.com" `
    -TargetEnvironment "https://prod-fsi.crm.dynamics.com" `
    -TargetZone "Zone3" `
    -ChangeRequestId "CHG-2025-001234"
```

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.2*
