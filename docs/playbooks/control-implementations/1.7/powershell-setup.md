# Control 1.7: Comprehensive Audit Logging - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## Enable Unified Audit Logging

```powershell
# Connect to Security & Compliance Center
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Enable unified audit logging
Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true

# Verify status
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled

# Check Mailbox Audit Logging
Get-OrganizationConfig | Select-Object AuditDisabled
# Should return False (auditing enabled)
```

---

## Search Copilot and Agent Audit Events

```powershell
# Define search parameters
$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

# Search for Copilot interactions
$copilotEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType CopilotInteraction -ResultSize 5000

Write-Host "Found $($copilotEvents.Count) Copilot events"

# Export to CSV for analysis
$copilotEvents | Select-Object CreationDate, UserIds, Operations, AuditData |
    Export-Csv -Path "Copilot-Audit-Log-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation

# Search for Copilot Studio agent events
$agentEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType PowerPlatformAdminActivity -Operations "PublishedAgent","UpdatedAgent" -ResultSize 1000

$agentEvents | Export-Csv -Path "Agent-Publish-Events.csv" -NoTypeInformation
```

---

## Export AI Interactions for WORM Storage

```powershell
function Export-AIInteractionsToWORM {
    param(
        [DateTime]$StartDate = (Get-Date).AddDays(-1),
        [DateTime]$EndDate = (Get-Date),
        [string]$OutputPath = "C:\Compliance\AIInteractions"
    )

    Write-Host "Exporting AI interactions for WORM storage..." -ForegroundColor Cyan

    # Search for Copilot interactions
    $interactions = Search-UnifiedAuditLog -StartDate $StartDate -EndDate $EndDate `
        -RecordType CopilotInteraction -ResultSize 5000

    # Parse and structure for compliance
    $complianceRecords = foreach ($event in $interactions) {
        $data = $event.AuditData | ConvertFrom-Json
        [PSCustomObject]@{
            Timestamp = $event.CreationDate
            UserId = $event.UserIds
            AgentId = $data.AgentId
            SessionId = $data.SessionId
            RawUserPrompt = $data.UserQuery
            CompleteAIResponse = $data.Response
            ConfidenceScore = $data.Confidence
            Citations = ($data.Citations | ConvertTo-Json -Compress)
            Channel = $data.Channel
            RecordedAt = Get-Date -Format "o"
        }
    }

    # Export to JSON for WORM storage
    $fileName = "AIInteractions_$($StartDate.ToString('yyyyMMdd'))_$($EndDate.ToString('yyyyMMdd')).json"
    $fullPath = Join-Path $OutputPath $fileName

    $complianceRecords | ConvertTo-Json -Depth 10 | Out-File -FilePath $fullPath -Encoding UTF8

    # Generate hash for integrity verification
    $hash = (Get-FileHash -Path $fullPath -Algorithm SHA256).Hash
    "$($EndDate.ToString('yyyy-MM-dd')),$fileName,SHA256,$hash" |
        Out-File -FilePath "$OutputPath\AIInteraction_Hashes.csv" -Append

    Write-Host "Exported $($complianceRecords.Count) interactions to: $fullPath" -ForegroundColor Green
    Write-Host "SHA-256: $hash" -ForegroundColor Cyan

    return $fullPath
}
```

---

## Audit Specific Agent Activities

```powershell
# Define agent-related operations to monitor
$agentOperations = @(
    "PublishedAgent",
    "UpdatedAgent",
    "DeletedAgent",
    "AgentConfigChanged",
    "ConnectorAdded",
    "ConnectorRemoved"
)

# Search for agent lifecycle events
$agentAudit = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -Operations ($agentOperations -join ",") -ResultSize 1000

# Parse and display
foreach ($event in $agentAudit) {
    $data = $event.AuditData | ConvertFrom-Json
    Write-Host "$($event.CreationDate): $($event.Operations) by $($event.UserIds)"
}

# Export agent audit trail
$agentAudit | ForEach-Object {
    $data = $_.AuditData | ConvertFrom-Json
    [PSCustomObject]@{
        Date = $_.CreationDate
        Operation = $_.Operations
        User = $_.UserIds
        AgentName = $data.ObjectId
        Environment = $data.EnvironmentName
    }
} | Export-Csv -Path "Agent-Lifecycle-Audit.csv" -NoTypeInformation
```

---

## Monitor Audit Log Health

```powershell
# Check for recent audit events to verify logging is active
$recentEvents = Search-UnifiedAuditLog -StartDate (Get-Date).AddHours(-24) -EndDate (Get-Date) `
    -ResultSize 100

if ($recentEvents.Count -eq 0) {
    Write-Warning "No audit events in last 24 hours - verify audit logging is enabled"
} else {
    Write-Host "Audit logging active: $($recentEvents.Count) events in last 24 hours"

    # Show distribution by workload
    $recentEvents | Group-Object -Property RecordType |
        Sort-Object Count -Descending |
        Select-Object Name, Count | Format-Table
}
```

---

## Adversarial Pattern Detection (KQL)

```kql
// Detect adversarial input patterns in audit logs
let adversarial_patterns = dynamic([
    "ignore previous", "disregard instructions", "forget your",
    "you are now", "from now on", "your new role",
    "system prompt", "DAN mode", "developer mode",
    "jailbreak", "bypass", "override"
]);
CopilotInteraction
| where TimeGenerated > ago(7d)
| where UserInput has_any (adversarial_patterns)
| extend DetectedPattern = case(
    UserInput has "ignore previous" or UserInput has "disregard", "Prompt Injection",
    UserInput has "you are now" or UserInput has "your new role", "Role Manipulation",
    UserInput has "DAN mode" or UserInput has "jailbreak", "Jailbreaking",
    "Other Suspicious"
)
| project TimeGenerated, UserId, AgentId, UserInput, DetectedPattern
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.7 - Comprehensive Audit Logging and Compliance

.DESCRIPTION
    This script:
    1. Enables unified audit logging
    2. Verifies mailbox audit logging
    3. Searches for Copilot and agent audit events
    4. Exports AI interactions for WORM storage
    5. Generates compliance report

.PARAMETER OutputPath
    Path for compliance exports (default: C:\Compliance\AIInteractions)

.PARAMETER DaysToSearch
    Number of days to search for audit events (default: 30)

.EXAMPLE
    .\Configure-Control-1.7.ps1 -OutputPath "C:\Compliance\AIInteractions" -DaysToSearch 30

.NOTES
    Last Updated: January 2026
    Related Control: Control 1.7 - Comprehensive Audit Logging and Compliance
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "C:\Compliance\AIInteractions",

    [Parameter(Mandatory=$false)]
    [int]$DaysToSearch = 30
)

try {
    # Connect to Security & Compliance Center
    Connect-IPPSSession

    Write-Host "=== Configuring Control 1.7: Comprehensive Audit Logging ===" -ForegroundColor Cyan

    # Step 1: Enable unified audit logging
    Write-Host "`nStep 1: Enabling unified audit logging..." -ForegroundColor White
    Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true

    $auditConfig = Get-AdminAuditLogConfig
    if ($auditConfig.UnifiedAuditLogIngestionEnabled -eq $true) {
        Write-Host "  [PASS] Unified audit logging is enabled" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Unified audit logging configuration issue" -ForegroundColor Yellow
    }

    # Step 2: Check mailbox audit logging
    Write-Host "`nStep 2: Checking mailbox audit logging..." -ForegroundColor White
    $orgConfig = Get-OrganizationConfig
    if ($orgConfig.AuditDisabled -eq $false) {
        Write-Host "  [PASS] Mailbox auditing is enabled" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Mailbox auditing is disabled" -ForegroundColor Yellow
    }

    # Step 3: Create output directory
    Write-Host "`nStep 3: Creating output directory..." -ForegroundColor White
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }
    Write-Host "  [DONE] Output directory ready: $OutputPath" -ForegroundColor Green

    # Step 4: Search for Copilot interactions
    Write-Host "`nStep 4: Searching for Copilot audit events..." -ForegroundColor White
    $startDate = (Get-Date).AddDays(-$DaysToSearch)
    $endDate = Get-Date

    $copilotEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
        -RecordType CopilotInteraction -ResultSize 5000

    Write-Host "  [DONE] Found $($copilotEvents.Count) Copilot events" -ForegroundColor Green

    # Export to CSV
    $copilotEvents | Select-Object CreationDate, UserIds, Operations, AuditData |
        Export-Csv -Path "$OutputPath\Copilot-Audit-Log-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation

    # Step 5: Search for agent lifecycle events
    Write-Host "`nStep 5: Searching for agent lifecycle events..." -ForegroundColor White
    $agentOperations = @("PublishedAgent", "UpdatedAgent", "DeletedAgent", "AgentConfigChanged")
    $agentEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
        -RecordType PowerPlatformAdminActivity -ResultSize 1000

    $agentLifecycle = $agentEvents | ForEach-Object {
        $data = $_.AuditData | ConvertFrom-Json
        [PSCustomObject]@{
            Date = $_.CreationDate
            Operation = $_.Operations
            User = $_.UserIds
            AgentName = $data.ObjectId
            Environment = $data.EnvironmentName
        }
    }

    $agentLifecycle | Export-Csv -Path "$OutputPath\Agent-Lifecycle-Audit.csv" -NoTypeInformation
    Write-Host "  [DONE] Exported agent lifecycle events" -ForegroundColor Green

    # Step 6: Export AI interactions for WORM storage
    Write-Host "`nStep 6: Creating WORM-ready export..." -ForegroundColor White
    $complianceRecords = foreach ($event in $copilotEvents) {
        $data = $event.AuditData | ConvertFrom-Json
        [PSCustomObject]@{
            Timestamp = $event.CreationDate
            UserId = $event.UserIds
            AgentId = $data.AgentId
            SessionId = $data.SessionId
            RawUserPrompt = $data.UserQuery
            CompleteAIResponse = $data.Response
            ConfidenceScore = $data.Confidence
            Citations = ($data.Citations | ConvertTo-Json -Compress)
            Channel = $data.Channel
            RecordedAt = Get-Date -Format "o"
        }
    }

    $fileName = "AIInteractions_$($startDate.ToString('yyyyMMdd'))_$($endDate.ToString('yyyyMMdd')).json"
    $fullPath = Join-Path $OutputPath $fileName
    $complianceRecords | ConvertTo-Json -Depth 10 | Out-File -FilePath $fullPath -Encoding UTF8

    # Generate hash for integrity verification
    $hash = (Get-FileHash -Path $fullPath -Algorithm SHA256).Hash
    "$($endDate.ToString('yyyy-MM-dd')),$fileName,SHA256,$hash" |
        Out-File -FilePath "$OutputPath\AIInteraction_Hashes.csv" -Append

    Write-Host "  [DONE] WORM export created: $fullPath" -ForegroundColor Green
    Write-Host "  [INFO] SHA-256: $hash" -ForegroundColor Cyan

    # Step 7: Generate summary report
    Write-Host "`nStep 7: Generating summary..." -ForegroundColor White
    $summary = @{
        ReportDate = Get-Date
        SearchPeriod = "$startDate to $endDate"
        UnifiedAuditEnabled = $auditConfig.UnifiedAuditLogIngestionEnabled
        MailboxAuditEnabled = -not $orgConfig.AuditDisabled
        CopilotEventsFound = $copilotEvents.Count
        AgentLifecycleEvents = $agentLifecycle.Count
        OutputPath = $OutputPath
    }

    Write-Host "`n=== AUDIT LOGGING SUMMARY ===" -ForegroundColor Cyan
    $summary | Format-List

    Write-Host "`n[PASS] Control 1.7 configuration completed successfully" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[INFO] Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Yellow
    exit 1
}
finally {
    # Disconnect from Security & Compliance Center
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}
```

---

*Updated: January 2026 | Version: v1.2*
