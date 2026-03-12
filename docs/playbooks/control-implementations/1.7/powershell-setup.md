# Control 1.7: Comprehensive Audit Logging - PowerShell Setup

> This playbook provides PowerShell automation guidance for [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).

---

## Prerequisites

Before running the scripts in this playbook:

- **Required module:** `ExchangeOnlineManagement` v3.0 or later
- **Required roles:** Purview Audit Admin or Purview Compliance Admin (audit search and retention policies), Exchange Online Admin (audit config)
- **Required licenses:** Microsoft 365 E5 or E5 Compliance add-on for Audit (Premium) retention policies

```powershell
# Install the Exchange Online Management module (run once)
Install-Module -Name ExchangeOnlineManagement -MinimumVersion 3.0.0 -Scope CurrentUser

# Import the module
Import-Module ExchangeOnlineManagement
```

!!! note "Connection Requirements"
    This playbook uses two connection types:

    - **`Connect-ExchangeOnline`** — Required for `Set-AdminAuditLogConfig`, `Get-AdminAuditLogConfig`, and `Get-OrganizationConfig`
    - **`Connect-IPPSSession`** — Required for `Search-UnifiedAuditLog`

    Some script sections need both connections. The Complete Configuration Script at the end handles both.

---

## Enable Unified Audit Logging

```powershell
# Connect to Exchange Online (required for audit config cmdlets)
Connect-ExchangeOnline -UserPrincipalName admin@contoso.com

# Enable unified audit logging
Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true

# Verify status — expected output: UnifiedAuditLogIngestionEnabled = True
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled

# Check Mailbox Audit Logging — expected output: AuditDisabled = False
Get-OrganizationConfig | Select-Object AuditDisabled

# Disconnect when done
Disconnect-ExchangeOnline -Confirm:$false
```

---

## Search Copilot and Agent Audit Events

!!! warning "Pagination Required for Large Tenants"
    `Search-UnifiedAuditLog` returns a maximum of 5,000 records per call. In high-volume FSI environments, queries may silently truncate results. For production evidence collection, use session-based pagination as described in the [Purview Audit Query Pack](../../monitoring-and-validation/purview-audit-query-pack.md).

```powershell
# Connect to Security & Compliance (required for Search-UnifiedAuditLog)
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Define search parameters
$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

# Search for Copilot interactions
$copilotEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType CopilotInteraction -ResultSize 5000

if ($null -eq $copilotEvents) {
    Write-Warning "No Copilot events found in the last 30 days"
} else {
    Write-Host "Found $(@($copilotEvents).Count) Copilot events"

    # Export to CSV for analysis
    $copilotEvents | Select-Object CreationDate, UserIds, Operations, AuditData |
        Export-Csv -Path "Copilot-Audit-Log-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation
}

# Search for Copilot Studio agent events
$agentEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType PowerPlatformAdminActivity -ResultSize 1000

if ($null -ne $agentEvents) {
    $agentEvents | Export-Csv -Path "Agent-Lifecycle-Events.csv" -NoTypeInformation
    Write-Host "Found $(@($agentEvents).Count) Power Platform admin events"
}

# Disconnect when done
Disconnect-ExchangeOnline -Confirm:$false
```

!!! tip "Operation Names"
    Power Platform operation names vary by tenant configuration. Run a broad `-RecordType PowerPlatformAdminActivity` search first, then review the `Operations` column to identify the exact names your tenant emits before applying `-Operations` filters.

---

## Export AI Interactions for WORM Storage

!!! warning "CopilotInteraction Schema Limitation"
    The `CopilotInteraction` audit record captures **interaction metadata** (timestamps, user IDs, application context), not the actual prompt and response text. To capture full prompt/response content for FINRA 4511 compliance, configure a dedicated communications archiver or Purview Communication Compliance policy. See the "Audit Schema Captures Metadata, Not Full Content" callout in [Control 1.7](../../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for details.

```powershell
function Export-AIInteractionsToWORM {
    param(
        [DateTime]$StartDate = (Get-Date).AddDays(-1),
        [DateTime]$EndDate = (Get-Date),
        [string]$OutputPath = "C:\Compliance\AIInteractions"
    )

    # Verify Security & Compliance session is active
    if (-not (Get-Command Search-UnifiedAuditLog -ErrorAction SilentlyContinue)) {
        throw "Connect-IPPSSession must be called before running this function. Run: Connect-IPPSSession -UserPrincipalName admin@contoso.com"
    }

    Write-Host "Exporting AI interactions for WORM storage..." -ForegroundColor Cyan

    # Ensure output directory exists
    if (-not (Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    }

    # Search for Copilot interactions
    $interactions = Search-UnifiedAuditLog -StartDate $StartDate -EndDate $EndDate `
        -RecordType CopilotInteraction -ResultSize 5000

    if ($null -eq $interactions) {
        Write-Warning "No Copilot interactions found for the specified date range"
        return $null
    }

    # Parse and structure audit metadata for compliance export
    $complianceRecords = foreach ($event in $interactions) {
        $data = $event.AuditData | ConvertFrom-Json
        [PSCustomObject]@{
            Timestamp    = $event.CreationDate
            UserId       = $event.UserIds
            Operation    = $event.Operations
            RecordType   = $data.RecordType
            RecordId     = $data.Id
            AuditDataRaw = $event.AuditData
            RecordedAt   = Get-Date -Format "o"
        }
    }

    # Export to JSON for WORM storage
    $fileName = "AIInteractions_$($StartDate.ToString('yyyyMMdd'))_$($EndDate.ToString('yyyyMMdd')).json"
    $fullPath = Join-Path $OutputPath $fileName

    $complianceRecords | ConvertTo-Json -Depth 10 | Out-File -FilePath $fullPath -Encoding UTF8

    # Generate hash for integrity verification
    $hash = (Get-FileHash -Path $fullPath -Algorithm SHA256).Hash

    # Initialize CSV with header if it doesn't exist
    $hashFile = Join-Path $OutputPath "AIInteraction_Hashes.csv"
    if (-not (Test-Path $hashFile)) {
        "Date,FileName,Algorithm,Hash" | Out-File -FilePath $hashFile -Encoding UTF8
    }
    "$($EndDate.ToString('yyyy-MM-dd')),$fileName,SHA256,$hash" |
        Out-File -FilePath $hashFile -Append

    Write-Host "Exported $(@($complianceRecords).Count) interactions to: $fullPath" -ForegroundColor Green
    Write-Host "SHA-256: $hash" -ForegroundColor Cyan

    return $fullPath
}

# Example invocation (requires active Connect-IPPSSession):
# Export-AIInteractionsToWORM -StartDate (Get-Date).AddDays(-1) -EndDate (Get-Date)
```

---

## Audit Specific Agent Activities

```powershell
# Connect to Security & Compliance (if not already connected)
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Define search parameters
$startDate = (Get-Date).AddDays(-30)
$endDate = Get-Date

# Search for all Power Platform admin events first to identify operation names
$agentAudit = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
    -RecordType PowerPlatformAdminActivity -ResultSize 1000

if ($null -eq $agentAudit) {
    Write-Warning "No Power Platform admin events found in the specified date range"
} else {
    # Show unique operations found in your tenant
    Write-Host "Operations found in your tenant:" -ForegroundColor Cyan
    $agentAudit | Group-Object Operations | Select-Object Name, Count | Format-Table

    # Parse and display agent-related events
    foreach ($event in $agentAudit) {
        $data = $event.AuditData | ConvertFrom-Json
        Write-Host "$($event.CreationDate): $($event.Operations) by $($event.UserIds)"
    }

    # Export agent audit trail
    $agentAudit | ForEach-Object {
        $data = $_.AuditData | ConvertFrom-Json
        [PSCustomObject]@{
            Date        = $_.CreationDate
            Operation   = $_.Operations
            User        = $_.UserIds
            ObjectId    = $data.ObjectId
            Environment = $data.EnvironmentName
        }
    } | Export-Csv -Path "Agent-Lifecycle-Audit.csv" -NoTypeInformation
}

# Disconnect when done
Disconnect-ExchangeOnline -Confirm:$false
```

---

## Monitor Audit Log Health

```powershell
# Connect to Security & Compliance (if not already connected)
Connect-IPPSSession -UserPrincipalName admin@contoso.com

# Check for recent audit events to verify logging is active
$recentEvents = Search-UnifiedAuditLog -StartDate (Get-Date).AddHours(-24) -EndDate (Get-Date) `
    -ResultSize 100

if ($null -eq $recentEvents -or @($recentEvents).Count -eq 0) {
    Write-Warning "No audit events in last 24 hours - verify audit logging is enabled"
    Write-Host "Run: Connect-ExchangeOnline; Get-AdminAuditLogConfig | Select UnifiedAuditLogIngestionEnabled" -ForegroundColor Yellow
} else {
    Write-Host "Audit logging active: $(@($recentEvents).Count) events in last 24 hours"

    # Show distribution by workload
    $recentEvents | Group-Object -Property RecordType |
        Sort-Object Count -Descending |
        Select-Object Name, Count | Format-Table
}

# Disconnect when done
Disconnect-ExchangeOnline -Confirm:$false
```

---

## Adversarial Pattern Detection (KQL)

!!! warning "Data Source Requirements"
    The `CopilotInteraction` audit schema captures **interaction metadata** (timestamps, user IDs, detection flags), not the actual prompt text.

    This query uses the `OfficeActivity` table with CopilotInteraction records and detects adversarial patterns via the `JailbreakDetected` flag nested within individual message objects in `CopilotEventData.Messages`. For organizations that ingest user input into a custom table via Application Insights or a communications archiver, adapt a text-matching pattern to your custom table.

```kql
// Detect adversarial patterns using built-in detection flags in audit data
// Run in: Sentinel > Logs or Log Analytics workspace
OfficeActivity
| where TimeGenerated > ago(7d)
| where RecordType == "CopilotInteraction"
| extend AuditDetail = parse_json(AuditData)
| mv-expand Message = AuditDetail.CopilotEventData.Messages
| where tobool(Message.JailbreakDetected) == true
| extend DetectedPattern = "Jailbreak Attempt"
| project TimeGenerated, UserId, DetectedPattern, RecordType
| order by TimeGenerated desc
```

---

## Complete Configuration Script

```powershell
<#
.SYNOPSIS
    Configures Control 1.7 - Comprehensive Audit Logging and Compliance

.DESCRIPTION
    This script:
    1. Enables unified audit logging (via Exchange Online)
    2. Verifies mailbox audit logging
    3. Searches for Copilot and agent audit events (via Security & Compliance)
    4. Exports AI interaction metadata for WORM storage
    5. Generates compliance report

.PARAMETER OutputPath
    Path for compliance exports (default: C:\Compliance\AIInteractions)

.PARAMETER DaysToSearch
    Number of days to search for audit events (default: 30)

.EXAMPLE
    .\Configure-Control-1.7.ps1 -OutputPath "C:\Compliance\AIInteractions" -DaysToSearch 30

.NOTES
    Required module: ExchangeOnlineManagement v3.0+
    Required roles: Purview Audit Admin, Exchange Online Admin
    Last Updated: February 2026
    Related Control: Control 1.7 - Comprehensive Audit Logging and Compliance
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "C:\Compliance\AIInteractions",

    [Parameter(Mandatory=$false)]
    [int]$DaysToSearch = 30
)

try {
    # Connect to Exchange Online (for audit config cmdlets)
    Write-Host "Connecting to Exchange Online..." -ForegroundColor Cyan
    Connect-ExchangeOnline -ShowBanner:$false

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

    # Connect to Security & Compliance (for audit log search)
    Write-Host "`nConnecting to Security & Compliance Center..." -ForegroundColor Cyan
    Connect-IPPSSession -ShowBanner:$false

    # Step 4: Search for Copilot interactions
    Write-Host "`nStep 4: Searching for Copilot audit events..." -ForegroundColor White
    $startDate = (Get-Date).AddDays(-$DaysToSearch)
    $endDate = Get-Date

    $copilotEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
        -RecordType CopilotInteraction -ResultSize 5000

    $copilotCount = if ($null -eq $copilotEvents) { 0 } else { @($copilotEvents).Count }
    Write-Host "  [DONE] Found $copilotCount Copilot events" -ForegroundColor Green

    if ($null -ne $copilotEvents) {
        # Export to CSV
        $copilotEvents | Select-Object CreationDate, UserIds, Operations, AuditData |
            Export-Csv -Path "$OutputPath\Copilot-Audit-Log-$(Get-Date -Format 'yyyy-MM-dd').csv" -NoTypeInformation
    }

    # Step 5: Search for agent lifecycle events
    Write-Host "`nStep 5: Searching for agent lifecycle events..." -ForegroundColor White
    $agentEvents = Search-UnifiedAuditLog -StartDate $startDate -EndDate $endDate `
        -RecordType PowerPlatformAdminActivity -ResultSize 1000

    $agentLifecycle = @()
    if ($null -ne $agentEvents) {
        $agentLifecycle = @($agentEvents | ForEach-Object {
            $data = $_.AuditData | ConvertFrom-Json
            [PSCustomObject]@{
                Date        = $_.CreationDate
                Operation   = $_.Operations
                User        = $_.UserIds
                ObjectId    = $data.ObjectId
                Environment = $data.EnvironmentName
            }
        })
        $agentLifecycle | Export-Csv -Path "$OutputPath\Agent-Lifecycle-Audit.csv" -NoTypeInformation
    }
    Write-Host "  [DONE] Exported $($agentLifecycle.Count) agent lifecycle events" -ForegroundColor Green

    # Step 6: Export AI interaction metadata for WORM storage
    Write-Host "`nStep 6: Creating WORM-ready export..." -ForegroundColor White
    if ($null -ne $copilotEvents) {
        $complianceRecords = foreach ($event in $copilotEvents) {
            $data = $event.AuditData | ConvertFrom-Json
            [PSCustomObject]@{
                Timestamp    = $event.CreationDate
                UserId       = $event.UserIds
                Operation    = $event.Operations
                RecordType   = $data.RecordType
                RecordId     = $data.Id
                AuditDataRaw = $event.AuditData
                RecordedAt   = Get-Date -Format "o"
            }
        }

        $fileName = "AIInteractions_$($startDate.ToString('yyyyMMdd'))_$($endDate.ToString('yyyyMMdd')).json"
        $fullPath = Join-Path $OutputPath $fileName
        $complianceRecords | ConvertTo-Json -Depth 10 | Out-File -FilePath $fullPath -Encoding UTF8

        # Generate hash for integrity verification
        $hash = (Get-FileHash -Path $fullPath -Algorithm SHA256).Hash

        $hashFile = Join-Path $OutputPath "AIInteraction_Hashes.csv"
        if (-not (Test-Path $hashFile)) {
            "Date,FileName,Algorithm,Hash" | Out-File -FilePath $hashFile -Encoding UTF8
        }
        "$($endDate.ToString('yyyy-MM-dd')),$fileName,SHA256,$hash" |
            Out-File -FilePath $hashFile -Append

        Write-Host "  [DONE] WORM export created: $fullPath" -ForegroundColor Green
        Write-Host "  [INFO] SHA-256: $hash" -ForegroundColor Cyan
    } else {
        Write-Host "  [SKIP] No Copilot events to export" -ForegroundColor Yellow
    }

    # Step 7: Generate summary report
    Write-Host "`nStep 7: Generating summary..." -ForegroundColor White
    $summary = [PSCustomObject]@{
        ReportDate          = Get-Date
        SearchPeriod        = "$startDate to $endDate"
        UnifiedAuditEnabled = $auditConfig.UnifiedAuditLogIngestionEnabled
        MailboxAuditEnabled = -not $orgConfig.AuditDisabled
        CopilotEventsFound  = $copilotCount
        AgentLifecycleEvents = $agentLifecycle.Count
        OutputPath          = $OutputPath
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
    # Disconnect all sessions
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}
```

---

## Deployable Solutions

For automated validation of tenant and environment audit configurations with drift detection and approval-gated remediation, see the [Audit Compliance Manager (ACM)](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager).

For automated daily deny event extraction and correlation across Purview Audit, DLP, and Application Insights, see the [Deny Event Correlation Report Solution](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report).

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [Verification & Testing](./verification-testing.md) - Test procedures
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: February 2026 | Version: v1.3*
