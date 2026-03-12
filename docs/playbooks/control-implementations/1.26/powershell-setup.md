# PowerShell Setup: Control 1.26 - Agent File Upload and File Analysis Restrictions

**Last Updated:** February 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
# Install the Power Platform administration module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser
Import-Module Microsoft.PowerApps.Administration.PowerShell

# Authenticate to Power Platform
Add-PowerAppsAccount
```

> **Note:** The Power Platform administration module provides cmdlets for managing Copilot Studio agent settings at scale. Ensure you have Power Platform Admin or Entra Global Admin permissions before running these scripts.

---

## Automated Scripts

### Get File Upload Status Across All Agents

```powershell
<#
.SYNOPSIS
    Retrieves file upload enablement status for all Copilot Studio agents across environments.

.DESCRIPTION
    Queries all managed environments and lists agents with their file upload toggle state,
    environment name, zone classification, and last modified date.

.EXAMPLE
    .\Get-AgentFileUploadStatus.ps1

.EXAMPLE
    .\Get-AgentFileUploadStatus.ps1 | Export-Csv -Path ".\FileUploadInventory.csv" -NoTypeInformation
#>

Write-Host "=== Agent File Upload Inventory ===" -ForegroundColor Cyan

$environments = Get-AdminPowerAppEnvironment

$results = @()

foreach ($env in $environments) {
    Write-Host "`nEnvironment: $($env.DisplayName)" -ForegroundColor Yellow

    # Retrieve agents (chatbots) in the environment
    $agents = Get-AdminPowerAppChatbot -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

    if (-not $agents) {
        Write-Host "  No agents found" -ForegroundColor Gray
        continue
    }

    foreach ($agent in $agents) {
        $fileUploadEnabled = $agent.Properties.FileUploadEnabled -eq $true

        $status = if ($fileUploadEnabled) { "Enabled" } else { "Disabled" }
        $color = if ($fileUploadEnabled) { "Yellow" } else { "Green" }

        Write-Host "  Agent: $($agent.Properties.DisplayName) — File Upload: $status" -ForegroundColor $color

        $results += [PSCustomObject]@{
            Environment       = $env.DisplayName
            EnvironmentId     = $env.EnvironmentName
            AgentName         = $agent.Properties.DisplayName
            AgentId           = $agent.ChatbotId
            FileUploadEnabled = $fileUploadEnabled
            LastModified      = $agent.Properties.LastModifiedTime
            CreatedBy         = $agent.Properties.CreatedBy.displayName
        }
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Total agents: $($results.Count)"
Write-Host "File upload enabled: $(($results | Where-Object FileUploadEnabled -eq $true).Count)"
Write-Host "File upload disabled: $(($results | Where-Object FileUploadEnabled -eq $false).Count)"

$results | Format-Table -AutoSize
```

!!! danger "API Availability — Verify Before Use"
    The `Set-AdminPowerAppChatbot` cmdlet with `-FileUploadEnabled` parameter is based on **anticipated API schema** as of February 2026. This parameter may not be available in all tenants. Before running Script 2 or Script 4, test cmdlet availability:

    ```powershell
    Get-Help Set-AdminPowerAppChatbot -Parameter FileUploadEnabled
    ```

    If the parameter is not recognized, use the [Portal Walkthrough](portal-walkthrough.md) to manage file upload settings manually.

### Bulk Disable File Upload for Zone 3 Agents

```powershell
<#
.SYNOPSIS
    Disables file upload for all agents in specified Zone 3 environments.

.DESCRIPTION
    Iterates through agents in the target environments and disables the file upload
    toggle. Supports -WhatIf for dry-run preview.

.PARAMETER EnvironmentNames
    Array of Power Platform environment names (GUIDs) to process.

.PARAMETER WhatIf
    Preview changes without applying them.

.EXAMPLE
    .\Disable-FileUpload-Zone3.ps1 -EnvironmentNames @("env-guid-1", "env-guid-2") -WhatIf

.EXAMPLE
    .\Disable-FileUpload-Zone3.ps1 -EnvironmentNames @("env-guid-1")
#>

param(
    [Parameter(Mandatory)]
    [string[]]$EnvironmentNames,

    [Parameter()]
    [switch]$WhatIf
)

Write-Host "=== Bulk Disable File Upload (Zone 3) ===" -ForegroundColor Cyan
Write-Host "Mode: $(if ($WhatIf) { 'Preview (WhatIf)' } else { 'Apply' })" -ForegroundColor Yellow

$results = @()

foreach ($envName in $EnvironmentNames) {
    $env = Get-AdminPowerAppEnvironment -EnvironmentName $envName
    Write-Host "`nEnvironment: $($env.DisplayName)" -ForegroundColor Yellow

    $agents = Get-AdminPowerAppChatbot -EnvironmentName $envName -ErrorAction SilentlyContinue

    if (-not $agents) {
        Write-Host "  No agents found" -ForegroundColor Gray
        continue
    }

    foreach ($agent in $agents) {
        $fileUploadEnabled = $agent.Properties.FileUploadEnabled -eq $true

        if ($fileUploadEnabled) {
            if ($WhatIf) {
                Write-Host "  [WHATIF] Would disable file upload: $($agent.Properties.DisplayName)" -ForegroundColor Yellow
            } else {
                try {
                    Set-AdminPowerAppChatbot -EnvironmentName $envName `
                        -ChatbotId $agent.ChatbotId `
                        -FileUploadEnabled $false

                    Write-Host "  [DISABLED] $($agent.Properties.DisplayName)" -ForegroundColor Green
                } catch {
                    Write-Host "  [ERROR] $($agent.Properties.DisplayName): $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        } else {
            Write-Host "  [OK] $($agent.Properties.DisplayName) — already disabled" -ForegroundColor Gray
        }

        $results += [PSCustomObject]@{
            Environment       = $env.DisplayName
            AgentName         = $agent.Properties.DisplayName
            PreviousState     = if ($fileUploadEnabled) { "Enabled" } else { "Disabled" }
            Action            = if ($fileUploadEnabled -and -not $WhatIf) { "Disabled" } elseif ($fileUploadEnabled) { "Would Disable" } else { "No Change" }
            Timestamp         = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
    }
}

Write-Host "`n=== Results ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize
```

### Audit File Upload Enablement with Zone Compliance

```powershell
<#
.SYNOPSIS
    Audits file upload enablement against zone governance requirements.

.DESCRIPTION
    Compares each agent's file upload toggle state against its environment's
    zone classification and outputs [PASS], [FAIL], or [WARN] results.

.PARAMETER ZoneMapping
    Hashtable mapping environment names to zone numbers.

.EXAMPLE
    $zones = @{
        "env-guid-personal" = 1
        "env-guid-team"     = 2
        "env-guid-enterprise" = 3
    }
    .\Audit-FileUploadCompliance.ps1 -ZoneMapping $zones
#>

param(
    [Parameter(Mandatory)]
    [hashtable]$ZoneMapping
)

Write-Host "=== File Upload Compliance Audit ===" -ForegroundColor Cyan

$results = @()

foreach ($envName in $ZoneMapping.Keys) {
    $zone = $ZoneMapping[$envName]
    $env = Get-AdminPowerAppEnvironment -EnvironmentName $envName
    Write-Host "`nEnvironment: $($env.DisplayName) (Zone $zone)" -ForegroundColor Yellow

    $agents = Get-AdminPowerAppChatbot -EnvironmentName $envName -ErrorAction SilentlyContinue

    if (-not $agents) {
        Write-Host "  No agents found" -ForegroundColor Gray
        continue
    }

    foreach ($agent in $agents) {
        $fileUploadEnabled = $agent.Properties.FileUploadEnabled -eq $true
        $compliant = $true
        $finding = ""

        switch ($zone) {
            1 {
                # Zone 1: file upload allowed with defaults
                if ($fileUploadEnabled) {
                    Write-Host "  [PASS] $($agent.Properties.DisplayName) — file upload enabled (Zone 1 allows)" -ForegroundColor Green
                    $finding = "Enabled — acceptable for Zone 1"
                } else {
                    Write-Host "  [INFO] $($agent.Properties.DisplayName) — file upload disabled (no issue)" -ForegroundColor Gray
                    $finding = "Disabled — no action required"
                }
            }
            2 {
                # Zone 2: file upload should be disabled unless approved
                if ($fileUploadEnabled) {
                    Write-Host "  [WARN] $($agent.Properties.DisplayName) — file upload enabled (requires approval for Zone 2)" -ForegroundColor Yellow
                    $compliant = $false
                    $finding = "Enabled — verify approval documentation exists"
                } else {
                    Write-Host "  [PASS] $($agent.Properties.DisplayName) — file upload disabled (Zone 2 default)" -ForegroundColor Green
                    $finding = "Disabled — compliant with Zone 2 default"
                }
            }
            3 {
                # Zone 3: file upload must be disabled unless formally approved
                if ($fileUploadEnabled) {
                    Write-Host "  [FAIL] $($agent.Properties.DisplayName) — file upload enabled (default deny for Zone 3)" -ForegroundColor Red
                    $compliant = $false
                    $finding = "Enabled — requires formal risk assessment and approval"
                } else {
                    Write-Host "  [PASS] $($agent.Properties.DisplayName) — file upload disabled (Zone 3 default deny)" -ForegroundColor Green
                    $finding = "Disabled — compliant with Zone 3 default deny"
                }
            }
        }

        $results += [PSCustomObject]@{
            Environment       = $env.DisplayName
            Zone              = $zone
            AgentName         = $agent.Properties.DisplayName
            FileUploadEnabled = $fileUploadEnabled
            Compliant         = $compliant
            Finding           = $finding
        }
    }
}

Write-Host "`n=== Audit Summary ===" -ForegroundColor Cyan
$total = $results.Count
$compliantCount = ($results | Where-Object Compliant -eq $true).Count
$nonCompliant = ($results | Where-Object Compliant -eq $false).Count
Write-Host "Total agents assessed: $total"
Write-Host "Compliant: $compliantCount" -ForegroundColor Green
Write-Host "Non-compliant: $nonCompliant" -ForegroundColor $(if ($nonCompliant -gt 0) { "Red" } else { "Green" })

$results | Format-Table -AutoSize
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.26 - Agent File Upload Restrictions across all environments.

.EXAMPLE
    .\Validate-Control-1.26.ps1
#>

Write-Host "=== Control 1.26 Validation ===" -ForegroundColor Cyan

Import-Module Microsoft.PowerApps.Administration.PowerShell

$environments = Get-AdminPowerAppEnvironment

$results = @()

foreach ($env in $environments) {
    Write-Host "`nEnvironment: $($env.DisplayName)" -ForegroundColor Yellow

    $agents = Get-AdminPowerAppChatbot -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

    if (-not $agents) {
        Write-Host "  [INFO] No agents found" -ForegroundColor Gray
        continue
    }

    $totalAgents = $agents.Count
    $uploadEnabled = ($agents | Where-Object { $_.Properties.FileUploadEnabled -eq $true }).Count
    $uploadDisabled = $totalAgents - $uploadEnabled

    # Check 1: Agent inventory
    Write-Host "  [PASS] Agent inventory: $totalAgents agents found" -ForegroundColor Green

    # Check 2: File upload enablement count
    if ($uploadEnabled -gt 0) {
        Write-Host "  [WARN] $uploadEnabled agent(s) with file upload enabled — verify approval documentation" -ForegroundColor Yellow
    } else {
        Write-Host "  [PASS] No agents with file upload enabled" -ForegroundColor Green
    }

    # Check 3: List agents with upload enabled for review
    foreach ($agent in ($agents | Where-Object { $_.Properties.FileUploadEnabled -eq $true })) {
        Write-Host "    → $($agent.Properties.DisplayName) (created by $($agent.Properties.CreatedBy.displayName))" -ForegroundColor Yellow
    }

    $results += [PSCustomObject]@{
        Environment    = $env.DisplayName
        TotalAgents    = $totalAgents
        UploadEnabled  = $uploadEnabled
        UploadDisabled = $uploadDisabled
    }
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures agent file upload restrictions for Control 1.26 across Power Platform environments.

.DESCRIPTION
    Applies zone-appropriate file upload governance to Copilot Studio agents.
    Supports dry-run preview with -WhatIf, multiple output formats, and file export.

.PARAMETER EnvironmentName
    The Power Platform environment name to configure. If not specified, processes all environments.

.PARAMETER ZoneLevel
    The governance zone level to enforce: 1, 2, or 3.

.PARAMETER OutputFormat
    Output format for the report: Table, JSON, or CSV. Default: Table.

.PARAMETER OutputPath
    File path to export results. If not specified, results are written to the console.

.PARAMETER WhatIf
    Preview changes without applying them.

.EXAMPLE
    .\Configure-Control-1.26.ps1 -ZoneLevel 3 -WhatIf

.EXAMPLE
    .\Configure-Control-1.26.ps1 -EnvironmentName "env-guid" -ZoneLevel 2 -OutputFormat JSON -OutputPath ".\results.json"
#>

param(
    [Parameter()]
    [string]$EnvironmentName,

    [Parameter(Mandatory)]
    [ValidateSet(1, 2, 3)]
    [int]$ZoneLevel,

    [Parameter()]
    [ValidateSet("Table", "JSON", "CSV")]
    [string]$OutputFormat = "Table",

    [Parameter()]
    [string]$OutputPath,

    [Parameter()]
    [switch]$WhatIf
)

try {
    Import-Module Microsoft.PowerApps.Administration.PowerShell -ErrorAction Stop
    Write-Host "=== Control 1.26: Agent File Upload Restrictions Configuration ===" -ForegroundColor Cyan
    Write-Host "Zone Level: $ZoneLevel" -ForegroundColor Yellow
    Write-Host "Mode: $(if ($WhatIf) { 'Preview (WhatIf)' } else { 'Apply' })" -ForegroundColor Yellow

    # Determine target environments
    if ($EnvironmentName) {
        $environments = @(Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentName)
    } else {
        $environments = Get-AdminPowerAppEnvironment
    }

    $results = @()

    foreach ($env in $environments) {
        Write-Host "`nProcessing: $($env.DisplayName)" -ForegroundColor Yellow

        $agents = Get-AdminPowerAppChatbot -EnvironmentName $env.EnvironmentName -ErrorAction SilentlyContinue

        if (-not $agents) {
            Write-Host "  No agents found — skipping" -ForegroundColor Gray
            continue
        }

        foreach ($agent in $agents) {
            $fileUploadEnabled = $agent.Properties.FileUploadEnabled -eq $true
            $shouldDisable = ($ZoneLevel -ge 2) -and $fileUploadEnabled
            $action = "No Change"

            if ($shouldDisable) {
                if ($WhatIf) {
                    Write-Host "  [WHATIF] Would disable: $($agent.Properties.DisplayName)" -ForegroundColor Yellow
                    $action = "Would Disable"
                } else {
                    Set-AdminPowerAppChatbot -EnvironmentName $env.EnvironmentName `
                        -ChatbotId $agent.ChatbotId `
                        -FileUploadEnabled $false
                    Write-Host "  [DISABLED] $($agent.Properties.DisplayName)" -ForegroundColor Green
                    $action = "Disabled"
                }
            } else {
                Write-Host "  [OK] $($agent.Properties.DisplayName) — no change needed" -ForegroundColor Gray
            }

            $results += [PSCustomObject]@{
                Environment       = $env.DisplayName
                EnvironmentId     = $env.EnvironmentName
                AgentName         = $agent.Properties.DisplayName
                AgentId           = $agent.ChatbotId
                PreviousState     = if ($fileUploadEnabled) { "Enabled" } else { "Disabled" }
                Action            = $action
                ZoneLevel         = $ZoneLevel
                Timestamp         = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        }
    }

    # Output results
    switch ($OutputFormat) {
        "Table" { $results | Format-Table -AutoSize }
        "JSON"  { $results | ConvertTo-Json -Depth 3 }
        "CSV"   { $results | ConvertTo-Csv -NoTypeInformation }
    }

    # Export to file if OutputPath specified
    if ($OutputPath) {
        switch ($OutputFormat) {
            "Table" { $results | Format-Table -AutoSize | Out-File -FilePath $OutputPath }
            "JSON"  { $results | ConvertTo-Json -Depth 3 | Out-File -FilePath $OutputPath }
            "CSV"   { $results | Export-Csv -Path $OutputPath -NoTypeInformation }
        }
        Write-Host "`nResults exported to: $OutputPath" -ForegroundColor Green
    }
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}
finally {
    Write-Host "`n=== Configuration Complete ===" -ForegroundColor Cyan
}
```

---

[Back to Control 1.26](../../../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification & Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
