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

[Back to Control 2.17](../../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | [Portal Walkthrough](portal-walkthrough.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)
