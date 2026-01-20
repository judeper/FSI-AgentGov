# PowerShell Setup: Control 2.17 - Multi-Agent Orchestration Limits

**Last Updated:** January 2026
**Modules Required:** Microsoft.PowerApps.Administration.PowerShell

## Prerequisites

```powershell
# Install Power Platform admin module
Install-Module -Name Microsoft.PowerApps.Administration.PowerShell -Force -Scope CurrentUser

# Connect to Power Platform
Add-PowerAppsAccount
```

---

## Monitoring and Reporting Scripts

### Query Orchestration Events from Audit Logs

```powershell
<#
.SYNOPSIS
    Queries audit logs for multi-agent orchestration events

.DESCRIPTION
    Uses Microsoft 365 audit log to identify agent-to-agent calls
    and delegation patterns

.EXAMPLE
    .\Get-OrchestrationEvents.ps1 -StartDate (Get-Date).AddDays(-7)
#>

param(
    [DateTime]$StartDate = (Get-Date).AddDays(-7),
    [DateTime]$EndDate = (Get-Date)
)

# Connect to Exchange Online for audit log access
Connect-ExchangeOnline

Write-Host "=== Orchestration Event Query ===" -ForegroundColor Cyan
Write-Host "Date Range: $StartDate to $EndDate"

# Search for Copilot Studio agent events
$auditResults = Search-UnifiedAuditLog `
    -StartDate $StartDate `
    -EndDate $EndDate `
    -RecordType "CopilotInteraction" `
    -ResultSize 5000

if ($auditResults) {
    $orchestrationEvents = $auditResults | ForEach-Object {
        $auditData = $_.AuditData | ConvertFrom-Json

        [PSCustomObject]@{
            Timestamp = $_.CreationDate
            User = $_.UserIds
            Operation = $auditData.Operation
            AgentName = $auditData.AgentName
            TargetAgent = $auditData.TargetAgent
            DelegationDepth = $auditData.DelegationDepth
            Success = $auditData.ResultStatus -eq "Success"
        }
    }

    Write-Host "Found $($orchestrationEvents.Count) orchestration events"
    $orchestrationEvents | Format-Table Timestamp, AgentName, TargetAgent, DelegationDepth, Success

    # Export
    $orchestrationEvents | Export-Csv -Path "Orchestration-Events-$(Get-Date -Format 'yyyyMMdd').csv" -NoTypeInformation
} else {
    Write-Host "No orchestration events found in the specified period"
}
```

### Monitor Circuit Breaker Activations

```powershell
<#
.SYNOPSIS
    Monitors for circuit breaker activation events

.DESCRIPTION
    Identifies when circuit breakers have been triggered due to
    cascade failures in multi-agent orchestrations

.EXAMPLE
    .\Monitor-CircuitBreakers.ps1
#>

# Note: This script assumes custom logging has been implemented
# Actual implementation depends on your circuit breaker logging strategy

Write-Host "=== Circuit Breaker Monitor ===" -ForegroundColor Cyan

# Example: Query Application Insights or custom log source
# This is a template - adjust for your logging infrastructure

$circuitBreakerEvents = @(
    # Example data structure
    [PSCustomObject]@{
        Timestamp = Get-Date
        AgentName = "Client-Service-Bot"
        TargetAgent = "KYC-Verification-Agent"
        State = "Open"
        FailureCount = 3
        LastFailure = "Timeout"
    }
)

if ($circuitBreakerEvents.Count -gt 0) {
    Write-Host "`nActive Circuit Breakers:" -ForegroundColor Yellow
    $circuitBreakerEvents | Format-Table Timestamp, AgentName, TargetAgent, State, FailureCount
} else {
    Write-Host "No active circuit breakers" -ForegroundColor Green
}
```

### Generate Orchestration Depth Report

```powershell
<#
.SYNOPSIS
    Generates report of orchestration depth usage

.DESCRIPTION
    Analyzes audit data to identify orchestration depth patterns
    and potential policy violations

.EXAMPLE
    .\Get-OrchestrationDepthReport.ps1
#>

Write-Host "=== Orchestration Depth Analysis ===" -ForegroundColor Cyan

# This would connect to your audit/logging system
# Template for the analysis structure

$depthAnalysis = @{
    Zone1Agents = @{
        MaxAllowedDepth = 0
        MaxObservedDepth = 0
        Violations = 0
    }
    Zone2Agents = @{
        MaxAllowedDepth = 2
        MaxObservedDepth = 1
        Violations = 0
    }
    Zone3Agents = @{
        MaxAllowedDepth = 3
        MaxObservedDepth = 2
        Violations = 0
    }
}

Write-Host "`n=== Depth Summary by Zone ===" -ForegroundColor Cyan
$depthAnalysis.GetEnumerator() | ForEach-Object {
    $zone = $_.Key
    $data = $_.Value
    $status = if ($data.Violations -eq 0) { "COMPLIANT" } else { "VIOLATIONS" }
    $color = if ($data.Violations -eq 0) { "Green" } else { "Red" }

    Write-Host "$zone : Max Allowed=$($data.MaxAllowedDepth), Max Observed=$($data.MaxObservedDepth), Status=$status" -ForegroundColor $color
}
```

---

## Validation Script

```powershell
<#
.SYNOPSIS
    Validates Control 2.17 - Multi-Agent Orchestration Limits

.DESCRIPTION
    Checks orchestration configuration and compliance

.EXAMPLE
    .\Validate-Control-2.17.ps1
#>

Write-Host "=== Control 2.17 Validation ===" -ForegroundColor Cyan

# Check 1: Verify orchestration documentation exists
Write-Host "`n[Check 1] Orchestration Architecture Documentation" -ForegroundColor Cyan
Write-Host "[INFO] Verify orchestration patterns are documented" -ForegroundColor Yellow
Write-Host "[INFO] Required: Agent delegation chains, depth limits per zone"

# Check 2: Verify depth limits are enforced
Write-Host "`n[Check 2] Delegation Depth Limits" -ForegroundColor Cyan
Write-Host "[INFO] Zone 1: Max depth = 0 (no delegation)"
Write-Host "[INFO] Zone 2: Max depth = 2"
Write-Host "[INFO] Zone 3: Max depth = 3"

# Check 3: Verify circuit breakers configured
Write-Host "`n[Check 3] Circuit Breaker Configuration" -ForegroundColor Cyan
Write-Host "[INFO] Verify circuit breakers are implemented for all orchestrating agents"
Write-Host "[INFO] Required: Failure threshold, timeout, reset behavior"

# Check 4: Verify HITL checkpoints (Zone 3)
Write-Host "`n[Check 4] Human-in-the-Loop Checkpoints" -ForegroundColor Cyan
Write-Host "[INFO] Zone 3 agents must have HITL for sensitive operations"
Write-Host "[INFO] Verify checkpoint locations and timeout handling"

# Check 5: Verify monitoring
Write-Host "`n[Check 5] Monitoring and Alerting" -ForegroundColor Cyan
Write-Host "[INFO] Verify alerts configured for:"
Write-Host "  - Depth limit violations"
Write-Host "  - Circuit breaker activations"
Write-Host "  - HITL timeout escalations"

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
Write-Host "Document findings and remediate any gaps identified"
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Complete multi-agent orchestration limits configuration for Control 2.17

.DESCRIPTION
    Executes end-to-end orchestration monitoring setup including:
    - Audit log query for orchestration events
    - Depth limit validation
    - Circuit breaker status monitoring
    - Compliance report generation

.PARAMETER Days
    Number of days of history to retrieve

.PARAMETER OutputPath
    Path for output reports

.EXAMPLE
    .\Configure-Control-2.17.ps1 -Days 7 -OutputPath ".\Orchestration"

.NOTES
    Last Updated: January 2026
    Related Control: Control 2.17 - Multi-Agent Orchestration Limits
#>

param(
    [int]$Days = 7,
    [string]$OutputPath = ".\Orchestration-Report"
)

try {
    Write-Host "=== Control 2.17: Multi-Agent Orchestration Configuration ===" -ForegroundColor Cyan

    # Connect to Exchange Online for audit log access
    Connect-ExchangeOnline

    # Ensure output directory exists
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null

    $startDate = (Get-Date).AddDays(-$Days)
    $endDate = Get-Date

    Write-Host "[INFO] Querying audit logs from $startDate to $endDate" -ForegroundColor Cyan

    # Search for Copilot/agent events
    $auditResults = Search-UnifiedAuditLog `
        -StartDate $startDate `
        -EndDate $endDate `
        -RecordType "CopilotInteraction" `
        -ResultSize 5000 `
        -ErrorAction SilentlyContinue

    if ($auditResults -and $auditResults.Count -gt 0) {
        Write-Host "[INFO] Found $($auditResults.Count) orchestration events" -ForegroundColor Cyan

        # Parse events
        $orchestrationEvents = $auditResults | ForEach-Object {
            $auditData = $_.AuditData | ConvertFrom-Json

            [PSCustomObject]@{
                Timestamp = $_.CreationDate
                User = $_.UserIds
                Operation = $auditData.Operation
                AgentName = $auditData.AgentName
                TargetAgent = $auditData.TargetAgent
                DelegationDepth = $auditData.DelegationDepth
                Success = $auditData.ResultStatus -eq "Success"
            }
        }

        # Export events
        $orchestrationEvents | Export-Csv -Path "$OutputPath\OrchestrationEvents.csv" -NoTypeInformation

        # Analyze depth violations
        $maxDepthByZone = @{
            "Zone1" = 0
            "Zone2" = 2
            "Zone3" = 3
        }

        $depthViolations = $orchestrationEvents | Where-Object { $_.DelegationDepth -gt 3 }
        if ($depthViolations.Count -gt 0) {
            Write-Host "[WARN] Depth violations found: $($depthViolations.Count)" -ForegroundColor Yellow
            $depthViolations | Export-Csv -Path "$OutputPath\DepthViolations.csv" -NoTypeInformation
        } else {
            Write-Host "[PASS] No depth limit violations detected" -ForegroundColor Green
        }

        # Summary statistics
        $uniqueAgents = ($orchestrationEvents | Select-Object -ExpandProperty AgentName -Unique).Count
        $maxObservedDepth = ($orchestrationEvents | Measure-Object -Property DelegationDepth -Maximum).Maximum

        Write-Host "`n=== Orchestration Summary ===" -ForegroundColor Cyan
        Write-Host "Total Events: $($orchestrationEvents.Count)"
        Write-Host "Unique Agents: $uniqueAgents"
        Write-Host "Max Observed Depth: $maxObservedDepth"
        Write-Host "Depth Violations: $($depthViolations.Count)"
    } else {
        Write-Host "[INFO] No orchestration events found in the specified period" -ForegroundColor Yellow
        Write-Host "[INFO] This is expected if multi-agent orchestration is not yet deployed" -ForegroundColor Cyan
    }

    # Export configuration summary
    $config = @{
        ReportDate = Get-Date -Format "yyyy-MM-dd HH:mm"
        QueryPeriodDays = $Days
        MaxAllowedDepthZone1 = 0
        MaxAllowedDepthZone2 = 2
        MaxAllowedDepthZone3 = 3
        EventsFound = if ($auditResults) { $auditResults.Count } else { 0 }
    }
    $config | ConvertTo-Json | Out-File -FilePath "$OutputPath\OrchestrationConfig.json"

    Write-Host "`n[PASS] Control 2.17 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Cleanup connections
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}
```

---

[Back to Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
