# PowerShell Setup: Control 1.24 - Defender AI Security Posture Management

**Last Updated:** January 2026
**Modules Required:** Az.Security, Az.ResourceGraph

## Prerequisites

```powershell
Install-Module -Name Az.Security -Force -Scope CurrentUser
Install-Module -Name Az.ResourceGraph -Force -Scope CurrentUser
```

---

## Automated Scripts

### Check AI-SPM Status

```powershell
<#
.SYNOPSIS
    Checks if AI-SPM is enabled for subscriptions

.EXAMPLE
    .\Get-AISPMStatus.ps1
#>

Write-Host "=== Check AI-SPM Status ===" -ForegroundColor Cyan

Connect-AzAccount

$subscriptions = Get-AzSubscription

foreach ($sub in $subscriptions) {
    Set-AzContext -SubscriptionId $sub.Id
    Write-Host "`nSubscription: $($sub.Name)" -ForegroundColor Yellow

    # Check Defender CSPM status
    $pricing = Get-AzSecurityPricing -Name "CloudPosture" -ErrorAction SilentlyContinue

    if ($pricing) {
        Write-Host "  Defender CSPM: $($pricing.PricingTier)" -ForegroundColor Green

        # Check extensions
        $extensions = $pricing.Extension
        $aiSpm = $extensions | Where-Object { $_.Name -eq "AIThreatProtection" }
        Write-Host "  Extensions enabled: $($extensions.Name -join ', ')"
    } else {
        Write-Host "  Defender CSPM: Not enabled" -ForegroundColor Red
    }
}
```

### Inventory AI Workloads

```powershell
<#
.SYNOPSIS
    Inventories AI workloads across subscriptions using Resource Graph

.EXAMPLE
    .\Get-AIWorkloadInventory.ps1 -OutputPath ".\AIWorkloads.csv"
#>

param(
    [string]$OutputPath = ".\AIWorkloads.csv"
)

Write-Host "=== AI Workload Inventory ===" -ForegroundColor Cyan

Connect-AzAccount

# Query for AI-related resources
$query = @"
Resources
| where type in~ (
    'microsoft.cognitiveservices/accounts',
    'microsoft.machinelearningservices/workspaces',
    'microsoft.search/searchservices'
)
| project
    name,
    type,
    resourceGroup,
    subscriptionId,
    location,
    sku = properties.sku.name,
    kind = kind
| order by type, name
"@

$results = Search-AzGraph -Query $query

Write-Host "AI workloads found: $($results.Count)" -ForegroundColor Green

if ($results.Count -gt 0) {
    $results | Export-Csv -Path $OutputPath -NoTypeInformation
    Write-Host "Inventory exported to: $OutputPath" -ForegroundColor Green

    # Summary by type
    $results | Group-Object -Property type | ForEach-Object {
        Write-Host "  $($_.Name): $($_.Count)"
    }
}
```

### Export Attack Paths

```powershell
<#
.SYNOPSIS
    Exports attack paths from Defender for Cloud

.EXAMPLE
    .\Export-AttackPaths.ps1 -OutputPath ".\AttackPaths.csv"
#>

param(
    [string]$OutputPath = ".\AttackPaths.csv",
    [string]$SubscriptionId
)

Write-Host "=== Export Attack Paths ===" -ForegroundColor Cyan

Connect-AzAccount

if ($SubscriptionId) {
    Set-AzContext -SubscriptionId $SubscriptionId
}

# Get attack paths via REST API (PowerShell module doesn't have direct cmdlet)
$token = (Get-AzAccessToken -ResourceUrl "https://management.azure.com").Token
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$subscriptionId = (Get-AzContext).Subscription.Id
$uri = "https://management.azure.com/subscriptions/$subscriptionId/providers/Microsoft.Security/attackPaths?api-version=2024-01-01"

try {
    $response = Invoke-RestMethod -Uri $uri -Method Get -Headers $headers
    $attackPaths = $response.value

    Write-Host "Attack paths found: $($attackPaths.Count)" -ForegroundColor Green

    # Filter for AI-related paths
    $aiPaths = $attackPaths | Where-Object {
        $_.properties.displayName -match "AI|ML|cognitive|openai" -or
        $_.properties.description -match "AI|ML|cognitive|openai"
    }

    Write-Host "AI-related attack paths: $($aiPaths.Count)" -ForegroundColor Yellow

    if ($aiPaths.Count -gt 0) {
        $export = $aiPaths | ForEach-Object {
            [PSCustomObject]@{
                Name = $_.name
                DisplayName = $_.properties.displayName
                Description = $_.properties.description
                RiskLevel = $_.properties.riskLevel
                EntryPointCount = $_.properties.entryPointEntityInfos.Count
            }
        }

        $export | Export-Csv -Path $OutputPath -NoTypeInformation
        Write-Host "Attack paths exported to: $OutputPath" -ForegroundColor Green
    }
}
catch {
    Write-Host "Error retrieving attack paths: $($_.Exception.Message)" -ForegroundColor Red
}
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 1.24 - Defender AI-SPM configuration

.EXAMPLE
    .\Validate-Control-1.24.ps1
#>

Write-Host "=== Control 1.24 Validation ===" -ForegroundColor Cyan

Connect-AzAccount

$results = @()

# Check 1: Defender CSPM enabled
Write-Host "`n[Check 1] Defender CSPM Status" -ForegroundColor Cyan
$pricing = Get-AzSecurityPricing -Name "CloudPosture" -ErrorAction SilentlyContinue

if ($pricing -and $pricing.PricingTier -eq "Standard") {
    Write-Host "  [PASS] Defender CSPM enabled" -ForegroundColor Green
    $results += [PSCustomObject]@{Check="Defender CSPM"; Status="PASS"; Details="Enabled"}
} else {
    Write-Host "  [FAIL] Defender CSPM not enabled" -ForegroundColor Red
    $results += [PSCustomObject]@{Check="Defender CSPM"; Status="FAIL"; Details="Not enabled"}
}

# Check 2: AI workloads discovered
Write-Host "`n[Check 2] AI Workload Discovery" -ForegroundColor Cyan
$query = "Resources | where type in~ ('microsoft.cognitiveservices/accounts', 'microsoft.machinelearningservices/workspaces') | count"
$count = (Search-AzGraph -Query $query).Count

if ($count -gt 0) {
    Write-Host "  [PASS] AI workloads discovered: $count" -ForegroundColor Green
    $results += [PSCustomObject]@{Check="AI Discovery"; Status="PASS"; Details="$count workloads"}
} else {
    Write-Host "  [INFO] No AI workloads found (may be expected)" -ForegroundColor Yellow
    $results += [PSCustomObject]@{Check="AI Discovery"; Status="INFO"; Details="No workloads"}
}

# Check 3: Security recommendations
Write-Host "`n[Check 3] AI Security Recommendations" -ForegroundColor Cyan
$recommendations = Get-AzSecurityTask | Where-Object {
    $_.Name -match "AI|cognitive|machine learning|openai"
}

Write-Host "  AI-related recommendations: $($recommendations.Count)"
$results += [PSCustomObject]@{Check="Recommendations"; Status="INFO"; Details="$($recommendations.Count) found"}

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.24 - Defender AI Security Posture Management

.DESCRIPTION
    This script validates AI-SPM configuration, inventories AI workloads,
    and exports security posture data for compliance evidence.

.PARAMETER ExportPath
    Path for exports (default: current directory)

.EXAMPLE
    .\Configure-Control-1.24.ps1 -ExportPath "C:\Evidence"

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.24 - Defender AI Security Posture Management
#>

param(
    [string]$ExportPath = "."
)

try {
    # Connect to Azure
    Write-Host "Connecting to Azure..." -ForegroundColor Cyan
    Connect-AzAccount

    Write-Host "Configuring Control 1.24: Defender AI Security Posture Management" -ForegroundColor Cyan

    # Step 1: Check Defender CSPM
    Write-Host "`n[Step 1] Checking Defender CSPM status..." -ForegroundColor Yellow
    $pricing = Get-AzSecurityPricing -Name "CloudPosture" -ErrorAction SilentlyContinue

    if ($pricing) {
        Write-Host "  Defender CSPM: $($pricing.PricingTier)" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Defender CSPM not configured" -ForegroundColor Yellow
        Write-Host "  Enable in Azure Portal: Defender for Cloud > Environment settings > Defender CSPM"
    }

    # Step 2: Inventory AI workloads
    Write-Host "`n[Step 2] Inventorying AI workloads..." -ForegroundColor Yellow

    $query = @"
Resources
| where type in~ (
    'microsoft.cognitiveservices/accounts',
    'microsoft.machinelearningservices/workspaces'
)
| project name, type, resourceGroup, location
"@

    $aiWorkloads = Search-AzGraph -Query $query
    Write-Host "  AI workloads found: $($aiWorkloads.Count)" -ForegroundColor Green

    if ($aiWorkloads.Count -gt 0) {
        $workloadFile = Join-Path $ExportPath "AIWorkloads-$(Get-Date -Format 'yyyyMMdd').csv"
        $aiWorkloads | Export-Csv -Path $workloadFile -NoTypeInformation
        Write-Host "  Exported to: $workloadFile" -ForegroundColor Green
    }

    # Step 3: Export security recommendations
    Write-Host "`n[Step 3] Exporting AI security recommendations..." -ForegroundColor Yellow

    $tasks = Get-AzSecurityTask
    $aiTasks = $tasks | Where-Object {
        $_.RecommendationType -match "AI|cognitive|machine|openai" -or
        $_.ResourceId -match "cognitive|machinelearning|openai"
    }

    Write-Host "  AI recommendations: $($aiTasks.Count)"

    if ($aiTasks.Count -gt 0) {
        $taskFile = Join-Path $ExportPath "AIRecommendations-$(Get-Date -Format 'yyyyMMdd').csv"
        $aiTasks | Select-Object Name, RecommendationType, State, ResourceId |
            Export-Csv -Path $taskFile -NoTypeInformation
        Write-Host "  Exported to: $taskFile" -ForegroundColor Green
    }

    # Step 4: Summary report
    Write-Host "`n[Step 4] Generating summary..." -ForegroundColor Yellow

    $summary = [PSCustomObject]@{
        Timestamp = Get-Date
        DefenderCSPM = $pricing.PricingTier
        AIWorkloads = $aiWorkloads.Count
        SecurityRecommendations = $aiTasks.Count
        SubscriptionId = (Get-AzContext).Subscription.Id
    }

    $summaryFile = Join-Path $ExportPath "AISPM-Summary-$(Get-Date -Format 'yyyyMMdd').json"
    $summary | ConvertTo-Json | Out-File -FilePath $summaryFile
    Write-Host "  Summary saved to: $summaryFile" -ForegroundColor Green

    Write-Host "`n[PASS] Control 1.24 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    if (Get-AzContext) {
        Disconnect-AzAccount -ErrorAction SilentlyContinue | Out-Null
        Write-Host "`nDisconnected from Azure" -ForegroundColor Gray
    }
}
```

---

[Back to Control 1.24](../../../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
