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

*Updated: January 2026 | Version: v1.1*
