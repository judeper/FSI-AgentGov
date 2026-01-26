# Control 3.5: Cost Allocation and Budget Tracking - PowerShell Setup

> This playbook provides PowerShell automation scripts for [Control 3.5](../../../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md).

---

## Prerequisites

```powershell
# Install required modules
Install-Module -Name Az.CostManagement -Force -AllowClobber
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -AllowClobber
Install-Module -Name Microsoft.Graph -Force -AllowClobber

# Connect to services
Connect-AzAccount
Connect-MgGraph -Scopes "Reports.Read.All", "Directory.Read.All"
Add-PowerAppsAccount
```

---

## Get Power Platform Capacity Report

```powershell
function Get-PowerPlatformCapacityReport {
    param(
        [string]$OutputPath = ".\Capacity-Report-$(Get-Date -Format 'yyyyMMdd').csv"
    )

    Write-Host "Retrieving Power Platform capacity data..." -ForegroundColor Cyan

    # Get environments
    $environments = Get-AdminPowerAppEnvironment

    $capacityData = @()

    foreach ($env in $environments) {
        $envDetails = Get-AdminPowerAppEnvironment -EnvironmentName $env.EnvironmentName

        $capacityData += [PSCustomObject]@{
            EnvironmentName = $env.DisplayName
            EnvironmentType = $env.EnvironmentType
            DatabaseSize = $envDetails.OrganizationSettings.DatabaseSettings.Size
            FileSize = $envDetails.OrganizationSettings.FileSettings.Size
            LogSize = $envDetails.OrganizationSettings.LogSettings.Size
        }
    }

    $capacityData | Export-Csv -Path $OutputPath -NoTypeInformation

    Write-Host "Capacity report saved: $OutputPath" -ForegroundColor Green

    return $capacityData
}
```

---

## Get Agent Cost by Business Unit

```powershell
function Get-AgentCostByBusinessUnit {
    param(
        [int]$DaysBack = 30
    )

    Write-Host "Calculating agent costs by business unit..." -ForegroundColor Cyan

    # Internal rate card
    $rateCard = @{
        "CopilotStudioMessage" = 0.01
        "M365CopilotUser" = 30
        "AIBuilderCredit" = 0.005
        "DataverseGB" = 2
    }

    # Get environments and parse business unit from name
    $environments = Get-AdminPowerAppEnvironment

    $costReport = @()

    foreach ($env in $environments) {
        # Parse business unit from environment name (e.g., WEALTH-Z3-PRODUCTION)
        $nameParts = $env.DisplayName -split "-"
        $businessUnit = if ($nameParts.Count -ge 1) { $nameParts[0] } else { "Unknown" }
        $zone = if ($nameParts.Count -ge 2) { $nameParts[1] } else { "Unknown" }

        # Get usage data (simplified - actual implementation would query usage APIs)
        $estimatedMessages = Get-Random -Minimum 1000 -Maximum 50000
        $estimatedStorage = Get-Random -Minimum 1 -Maximum 10

        $monthlyMessageCost = $estimatedMessages * $rateCard["CopilotStudioMessage"]
        $monthlyStorageCost = $estimatedStorage * $rateCard["DataverseGB"]

        $costReport += [PSCustomObject]@{
            BusinessUnit = $businessUnit
            Zone = $zone
            Environment = $env.DisplayName
            EstimatedMessages = $estimatedMessages
            MessageCost = $monthlyMessageCost
            StorageGB = $estimatedStorage
            StorageCost = $monthlyStorageCost
            TotalCost = $monthlyMessageCost + $monthlyStorageCost
        }
    }

    # Summarize by business unit
    $summary = $costReport | Group-Object BusinessUnit | ForEach-Object {
        [PSCustomObject]@{
            BusinessUnit = $_.Name
            TotalCost = ($_.Group | Measure-Object TotalCost -Sum).Sum
            EnvironmentCount = $_.Group.Count
        }
    }

    Write-Host "Cost Summary by Business Unit:" -ForegroundColor Green
    $summary | Format-Table -AutoSize

    return $costReport
}
```

---

## Get Azure AI Costs

```powershell
function Get-AzureAICosts {
    param(
        [DateTime]$StartDate = (Get-Date).AddDays(-30),
        [DateTime]$EndDate = (Get-Date),
        [string]$ResourceGroupFilter = "*ai*"
    )

    Write-Host "Retrieving Azure AI costs..." -ForegroundColor Cyan

    $scope = "/subscriptions/$((Get-AzContext).Subscription.Id)"

    $costQuery = @{
        type = "ActualCost"
        timeframe = "Custom"
        timePeriod = @{
            from = $StartDate.ToString("yyyy-MM-dd")
            to = $EndDate.ToString("yyyy-MM-dd")
        }
        dataset = @{
            granularity = "Daily"
            aggregation = @{
                totalCost = @{
                    name = "Cost"
                    function = "Sum"
                }
            }
            grouping = @(
                @{ type = "Dimension"; name = "ResourceGroup" }
                @{ type = "Dimension"; name = "ServiceName" }
            )
        }
    }

    try {
        $costs = Invoke-AzCostManagementQuery -Scope $scope -Query $costQuery

        Write-Host "Azure AI Cost Summary:" -ForegroundColor Green
        Write-Host "Period: $($StartDate.ToString('yyyy-MM-dd')) to $($EndDate.ToString('yyyy-MM-dd'))"

        return $costs
    }
    catch {
        Write-Warning "Failed to retrieve Azure costs: $_"
        return $null
    }
}
```

---

## Generate Chargeback Report

```powershell
function New-ChargebackReport {
    param(
        [Parameter(Mandatory=$true)]
        [int]$Month,
        [Parameter(Mandatory=$true)]
        [int]$Year,
        [string]$OutputPath = ".\Chargeback-Report-$Year-$Month.xlsx"
    )

    Write-Host "Generating chargeback report for $Month/$Year..." -ForegroundColor Cyan

    # Get cost data
    $agentCosts = Get-AgentCostByBusinessUnit

    # Group and summarize
    $chargebackData = $agentCosts | Group-Object BusinessUnit | ForEach-Object {
        [PSCustomObject]@{
            BusinessUnit = $_.Name
            CostCenter = "CC-$(Get-Random -Minimum 1001 -Maximum 1010)"
            Period = "$Month/$Year"
            CopilotCost = [math]::Round(($_.Group | Measure-Object MessageCost -Sum).Sum, 2)
            StorageCost = [math]::Round(($_.Group | Measure-Object StorageCost -Sum).Sum, 2)
            TotalChargeback = [math]::Round(($_.Group | Measure-Object TotalCost -Sum).Sum, 2)
        }
    }

    # Export to CSV (or Excel with ImportExcel module)
    $csvPath = $OutputPath -replace ".xlsx", ".csv"
    $chargebackData | Export-Csv -Path $csvPath -NoTypeInformation

    Write-Host "Chargeback report generated: $csvPath" -ForegroundColor Green

    # Display summary
    $totalChargeback = ($chargebackData | Measure-Object TotalChargeback -Sum).Sum
    Write-Host "Total Chargeback for $Month/$Year: $($totalChargeback.ToString('C'))" -ForegroundColor Yellow

    return $chargebackData
}
```

---

## Set Budget Alerts

```powershell
function Set-AICostBudgetAlert {
    param(
        [Parameter(Mandatory=$true)]
        [string]$BudgetName,
        [Parameter(Mandatory=$true)]
        [decimal]$MonthlyBudget,
        [Parameter(Mandatory=$true)]
        [string]$ResourceGroupName,
        [string[]]$AlertRecipients = @("ai-governance@company.com")
    )

    Write-Host "Creating budget alert: $BudgetName" -ForegroundColor Cyan

    $scope = "/subscriptions/$((Get-AzContext).Subscription.Id)/resourceGroups/$ResourceGroupName"

    $budget = @{
        Name = $BudgetName
        Category = "Cost"
        Amount = $MonthlyBudget
        TimeGrain = "Monthly"
        TimePeriod = @{
            StartDate = (Get-Date).ToString("yyyy-MM-01")
            EndDate = (Get-Date).AddYears(1).ToString("yyyy-MM-01")
        }
        Notifications = @{
            "Alert_50" = @{
                Enabled = $true
                Operator = "GreaterThanOrEqualTo"
                Threshold = 50
                ContactEmails = $AlertRecipients
            }
            "Alert_75" = @{
                Enabled = $true
                Operator = "GreaterThanOrEqualTo"
                Threshold = 75
                ContactEmails = $AlertRecipients
            }
            "Alert_100" = @{
                Enabled = $true
                Operator = "GreaterThanOrEqualTo"
                Threshold = 100
                ContactEmails = $AlertRecipients
            }
        }
    }

    try {
        New-AzConsumptionBudget @budget
        Write-Host "Budget alert created successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to create budget: $_"
    }
}
```

---

## Usage Examples

```powershell
# Get Power Platform capacity
Get-PowerPlatformCapacityReport

# Get costs by business unit
Get-AgentCostByBusinessUnit -DaysBack 30

# Generate monthly chargeback report
New-ChargebackReport -Month 1 -Year 2026

# Create budget alert
Set-AICostBudgetAlert -BudgetName "AI-Agents-Monthly" -MonthlyBudget 10000 -ResourceGroupName "rg-ai-agents" -AlertRecipients @("ai-team@company.com", "finance@company.com")
```

---

## Next Steps

- [Portal Walkthrough](./portal-walkthrough.md) - Manual configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues

---

*Updated: January 2026 | Version: v1.2*
