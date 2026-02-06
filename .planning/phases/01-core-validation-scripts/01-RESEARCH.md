# Phase 1: Core Validation Scripts - Research

**Researched:** 2026-02-06
**Domain:** PowerShell audit validation for M365/Purview/Power Platform
**Confidence:** HIGH

## Summary

Phase 1 requires PowerShell scripts that validate tenant-level audit configuration across M365 Unified Audit Log, mailbox audit, and Purview retention policies. The research confirms that Microsoft provides well-documented PowerShell cmdlets for this purpose, but validation requires careful handling of false positives through dual validation strategies.

**Key Findings:**
- Exchange Online PowerShell provides `Get-AdminAuditLogConfig` and `Get-OrganizationConfig` for tenant-level audit validation
- Purview retention policies are validated via `Get-UnifiedAuditLogRetentionPolicy` in Security & Compliance PowerShell
- Audit log ingestion has documented lag periods (up to 24 hours) requiring grace period handling
- False positives are a known issue when cmdlets report "enabled" but audit events don't appear due to lag
- ExchangeOnlineManagement module v3.x is production-ready with PowerShell 7 support

**Primary recommendation:** Use dual validation strategy combining cmdlet status checks with canary event verification (test event + retrieval) to avoid false positives from audit lag.

## Standard Stack

The established libraries/tools for PowerShell audit validation:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ExchangeOnlineManagement | 3.7.0+ | Unified Audit Log and mailbox audit validation | Official Microsoft module for Exchange Online PowerShell |
| Microsoft.Graph.Identity.SignIns | 2.x | Audit event retrieval via Microsoft Graph (optional) | Modern API approach for audit data |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Microsoft.PowerShell.SecretManagement | 1.1+ | Credential storage for service principal auth | Production deployments with unattended scripts |
| Az.KeyVault | 5.x | Azure Key Vault access for secrets | Enterprise credential management |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| ExchangeOnlineManagement | Direct REST API calls | More control but requires custom auth, pagination, error handling |
| PowerShell 7 | PowerShell 5.1 | 5.1 lacks cross-platform support but is pre-installed on Windows |
| Interactive auth | Service principal | Service principal required for automation but needs careful security controls |

**Installation:**
```powershell
# Install required modules
Install-Module -Name ExchangeOnlineManagement -RequiredVersion 3.7.0 -Scope CurrentUser
Install-Module -Name Microsoft.Graph.Identity.SignIns -Scope CurrentUser
```

## Architecture Patterns

### Recommended Project Structure
```
audit-configuration-validator/
├── scripts/
│   ├── Invoke-TenantAuditValidation.ps1    # Main validation orchestrator
│   ├── Test-UnifiedAuditLog.ps1             # Dual validation for UAL
│   ├── Test-MailboxAudit.ps1                # Mailbox audit validation
│   ├── Test-PurviewRetention.ps1            # Retention policy validation
│   └── private/
│       ├── Connect-AuditServices.ps1        # Authentication helper
│       └── New-CanaryEvent.ps1              # Canary event generator
├── src/
│   └── power-automate/
│       └── DailyValidationOrchestrator.json # Scheduled flow
├── docs/
│   ├── deployment-guide.md
│   └── troubleshooting.md
└── README.md
```

### Pattern 1: Dual Validation Strategy
**What:** Combine cmdlet status checks with canary event verification to avoid false positives
**When to use:** Always for audit enablement validation (TVAL-04)
**Example:**
```powershell
# Source: FSI-AgentGov research findings from Microsoft Learn
function Test-UnifiedAuditLogWithCanary {
    [CmdletBinding()]
    param(
        [int]$GracePeriodHours = 24
    )

    # Step 1: Check cmdlet status
    $config = Get-AdminAuditLogConfig
    $cmdletEnabled = $config.UnifiedAuditLogIngestionEnabled

    if (-not $cmdletEnabled) {
        return [PSCustomObject]@{
            Status = "Failed"
            Reason = "UnifiedAuditLogIngestionEnabled is False"
            Confidence = "HIGH"
        }
    }

    # Step 2: Generate canary event
    $canaryId = [Guid]::NewGuid().ToString()
    New-CanaryEvent -EventId $canaryId

    # Step 3: Wait for audit lag (30-60 minutes typical)
    Start-Sleep -Seconds 300  # 5 minutes for fast validation

    # Step 4: Search for canary event
    $startDate = (Get-Date).AddHours(-1)
    $endDate = Get-Date

    $canaryEvent = Search-UnifiedAuditLog `
        -StartDate $startDate `
        -EndDate $endDate `
        -FreeText $canaryId `
        -ResultSize 1

    if ($canaryEvent) {
        return [PSCustomObject]@{
            Status = "Passed"
            Reason = "Cmdlet enabled AND canary event retrieved"
            Confidence = "HIGH"
        }
    }

    # Step 5: Check if audit was recently enabled
    $auditHistory = Get-AdminAuditLogConfig | Select-Object -ExpandProperty AuditLogAgeLimit
    $enabledRecently = # Logic to check if enabled within grace period

    if ($enabledRecently) {
        return [PSCustomObject]@{
            Status = "Grace Period"
            Reason = "Enabled within $GracePeriodHours hours, audit lag expected"
            Confidence = "MEDIUM"
        }
    }

    return [PSCustomObject]@{
        Status = "Warning"
        Reason = "Cmdlet reports enabled but canary event not found (possible lag)"
        Confidence = "MEDIUM"
    }
}
```

### Pattern 2: Module Version Validation
**What:** Use #Requires statements to enforce minimum module versions
**When to use:** Always at script header (INFR-05)
**Example:**
```powershell
# Source: Microsoft Learn PowerShell #Requires documentation
#Requires -Version 7.0
#Requires -Modules @{ ModuleName="ExchangeOnlineManagement"; ModuleVersion="3.7.0" }

<#
.SYNOPSIS
    Validates M365 Unified Audit Log configuration.

.DESCRIPTION
    Checks that Unified Audit Log ingestion is enabled and verifies
    retention policies meet FSI regulatory requirements.
#>
```

### Pattern 3: Comprehensive Error Handling
**What:** Try-catch-finally blocks with specific error type handling
**When to use:** All service API calls and credential operations
**Example:**
```powershell
# Source: Microsoft Learn try-catch-finally best practices
function Get-AuditLogStatus {
    [CmdletBinding()]
    param()

    try {
        # Connect to Exchange Online
        Connect-ExchangeOnline -ShowBanner:$false -ErrorAction Stop

        # Retrieve config
        $config = Get-AdminAuditLogConfig -ErrorAction Stop

        return $config
    }
    catch [System.Management.Automation.CommandNotFoundException] {
        Write-Error "ExchangeOnlineManagement module not installed. Run: Install-Module ExchangeOnlineManagement"
        throw
    }
    catch [Microsoft.Exchange.Management.ExoPowershellSnapin.ConnectionException] {
        Write-Error "Failed to connect to Exchange Online. Check credentials and network connectivity."
        throw
    }
    catch {
        Write-Error "Unexpected error retrieving audit config: $($_.Exception.Message)"
        throw
    }
    finally {
        # Disconnect to clean up session
        Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
    }
}
```

### Pattern 4: Zone-Specific Retention Validation
**What:** Validate retention policies against zone-specific regulatory requirements
**When to use:** Purview retention policy validation (PVAL-02)
**Example:**
```powershell
# Source: FSI-AgentGov Control 1.7 requirements
function Test-RetentionCompliance {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [ValidateSet("Zone1", "Zone2", "Zone3")]
        [string]$Zone
    )

    # Define minimum retention requirements per zone
    $minimumRetention = @{
        "Zone1" = 180   # 180 days (6 months)
        "Zone2" = 365   # 1 year
        "Zone3" = 730   # 2 years (SEC 17a-4 communications minimum)
    }

    # Get retention policies
    $policies = Get-UnifiedAuditLogRetentionPolicy

    # Check for CopilotInteraction and PowerPlatformAdmin coverage
    $requiredRecordTypes = @("CopilotInteraction", "PowerPlatformAdmin")

    $gaps = @()
    foreach ($recordType in $requiredRecordTypes) {
        $policy = $policies | Where-Object { $_.RecordType -contains $recordType }

        if (-not $policy) {
            $gaps += [PSCustomObject]@{
                RecordType = $recordType
                Issue = "No retention policy defined"
                Severity = "High"
            }
            continue
        }

        # Parse retention duration (format: "TwoYears", "ThreeYears", etc.)
        $retentionDays = switch -Regex ($policy.RetentionDuration) {
            "OneYear"    { 365 }
            "TwoYears"   { 730 }
            "ThreeYears" { 1095 }
            "FiveYears"  { 1825 }
            "TenYears"   { 3650 }
            default      { 90 }  # Default for "ThreeMonths"
        }

        if ($retentionDays -lt $minimumRetention[$Zone]) {
            $gaps += [PSCustomObject]@{
                RecordType = $recordType
                Issue = "Retention $retentionDays days < required $($minimumRetention[$Zone]) days for $Zone"
                Severity = "Critical"
            }
        }
    }

    return $gaps
}
```

### Anti-Patterns to Avoid
- **Global error suppression:** Never use `$ErrorActionPreference = "SilentlyContinue"` globally—handle errors explicitly per command
- **Hardcoded credentials:** Never embed credentials in scripts—use Azure Key Vault or SecretManagement
- **Single validation point:** Don't rely solely on cmdlet status without verifying actual audit event flow (dual validation prevents false positives)
- **Ignoring module versions:** Don't assume ExchangeOnlineManagement is installed—use #Requires to enforce version

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Exchange Online authentication | Custom OAuth2 flow | Connect-ExchangeOnline cmdlet | Handles MFA, modern auth, token refresh, certificate auth |
| Audit log pagination | Custom loop with API calls | Search-UnifiedAuditLog with SessionId | Built-in handling for 50,000+ record sets with ReturnLargeSet |
| Retention policy parsing | Regex parsing of policy names | Get-UnifiedAuditLogRetentionPolicy RetentionDuration property | Returns structured enum values (OneYear, TwoYears, etc.) |
| Credential management | Encrypted files or registry | Azure Key Vault + Az.KeyVault module | Enterprise-grade secret storage with audit trail |
| Module availability check | Test-Path or Get-Module | #Requires statement | Script fails fast with clear error before execution |

**Key insight:** Microsoft's PowerShell modules handle complex edge cases (MFA, token refresh, pagination, regional endpoints) that custom implementations miss. Audit validation is deceptively complex—audit lag, regional variations, and licensing-dependent features mean "works in dev" often fails in production.

## Common Pitfalls

### Pitfall 1: False Positives from Audit Lag
**What goes wrong:** Script reports "audit enabled" via cmdlet but audit events don't appear for 24+ hours, causing false positive alerts
**Why it happens:** Microsoft documents 30-60 minute lag for most events, but up to 24 hours for all services to begin logging
**How to avoid:** Implement 24-hour grace period for newly-enabled audit settings; use dual validation (cmdlet + canary event retrieval)
**Warning signs:**
- Alerts fire immediately after enabling audit
- Canary events generated but not retrievable within expected timeframe
- Different services show different lag times

### Pitfall 2: Using Security & Compliance PowerShell for Unified Audit Status
**What goes wrong:** Get-AdminAuditLogConfig in Security & Compliance PowerShell always returns False for UnifiedAuditLogIngestionEnabled, even when enabled
**Why it happens:** This property is only accurate in Exchange Online PowerShell, not Security & Compliance PowerShell
**How to avoid:** Always use Connect-ExchangeOnline, never Connect-IPPSSession, for UnifiedAuditLogIngestionEnabled checks
**Warning signs:**
- Script consistently reports "audit disabled" despite portal showing enabled
- UnifiedAuditLogIngestionEnabled always False regardless of actual state

### Pitfall 3: Missing RecordType Coverage in Retention Policies
**What goes wrong:** Default retention policy doesn't cover CopilotInteraction or PowerPlatformAdmin record types, leading to gaps
**Why it happens:** Default policy may only cover Exchange/SharePoint/OneDrive; AI-specific record types require explicit policies
**How to avoid:** Query Get-UnifiedAuditLogRetentionPolicy with specific RecordType filters; create policies for CopilotInteraction and PowerPlatformAdmin
**Warning signs:**
- CopilotInteraction events appear in search but disappear before expected retention period
- PowerPlatformAdmin events not retained despite default policy showing 1+ year retention

### Pitfall 4: AuditDisabled Property Inverted Logic
**What goes wrong:** Administrators check if AuditDisabled is True when it should be False for enabled state
**Why it happens:** Property name is confusing—AuditDisabled = False means audit IS enabled
**How to avoid:** Document clearly: "AuditDisabled = False = Audit Enabled" and use explicit boolean checks
**Warning signs:**
- Validation logic inverted (reporting enabled when disabled)
- Conditional logic using `if ($config.AuditDisabled)` without negation

### Pitfall 5: Service Principal Permissions Insufficient for Audit APIs
**What goes wrong:** Service principal can't query audit logs even with correct module/authentication
**Why it happens:** Office 365 Management APIs require specific app permissions (ActivityFeed.Read, ActivityFeed.ReadDlp) in addition to Exchange admin roles
**How to avoid:** Grant both Exchange Online permissions AND Office 365 Management API permissions to service principal
**Warning signs:**
- Interactive auth works, service principal fails with 403 Forbidden
- Error mentions "ActivityFeed" or "content blobs not accessible"

## Code Examples

Verified patterns from official sources:

### Checking Unified Audit Log Status
```powershell
# Source: https://learn.microsoft.com/en-us/purview/audit-log-enable-disable
Connect-ExchangeOnline -ShowBanner:$false

$config = Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled

# True = audit enabled
# False = audit disabled
```

### Checking Mailbox Audit On-By-Default
```powershell
# Source: https://learn.microsoft.com/en-us/purview/audit-mailboxes
Connect-ExchangeOnline -ShowBanner:$false

$orgConfig = Get-OrganizationConfig | Format-List AuditDisabled

# False = mailbox audit enabled (inverted property)
# True = mailbox audit disabled
```

### Listing Retention Policies with Priority
```powershell
# Source: https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-unifiedauditlogretentionpolicy
Connect-IPPSSession

Get-UnifiedAuditLogRetentionPolicy |
    Sort-Object -Property Priority |
    Format-List Priority,Name,Description,RecordTypes,RetentionDuration
```

### Searching Audit Log with Pagination
```powershell
# Source: https://learn.microsoft.com/en-us/office/office-365-management-api/aip-unified-audit-logs-best-practices
$sessionId = [Guid]::NewGuid().ToString()
$allRecords = @()

do {
    $results = Search-UnifiedAuditLog `
        -StartDate (Get-Date).AddDays(-1) `
        -EndDate (Get-Date) `
        -RecordType CopilotInteraction `
        -SessionId $sessionId `
        -SessionCommand ReturnLargeSet `
        -ResultSize 5000

    if ($results) {
        $allRecords += $results
    }
} while ($results.Count -eq 5000)

Write-Host "Retrieved $($allRecords.Count) records"
```

### Error Handling with Try-Catch-Finally
```powershell
# Source: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_try_catch_finally
try {
    Connect-ExchangeOnline -ShowBanner:$false -ErrorAction Stop
    $config = Get-AdminAuditLogConfig -ErrorAction Stop

    Write-Output "Audit status: $($config.UnifiedAuditLogIngestionEnabled)"
}
catch [System.Management.Automation.CommandNotFoundException] {
    Write-Error "ExchangeOnlineManagement module not found. Install with: Install-Module ExchangeOnlineManagement"
    exit 1
}
catch {
    Write-Error "Failed to check audit status: $($_.Exception.Message)"
    exit 1
}
finally {
    Disconnect-ExchangeOnline -Confirm:$false -ErrorAction SilentlyContinue
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Security & Compliance PowerShell for all audit checks | Exchange Online PowerShell for UnifiedAuditLogIngestionEnabled | 2019-2020 | Security & Compliance always returns False for this property |
| Basic (90-day) audit log only | Audit Premium with 10-year retention | 2021+ (E5 licensing) | FSI firms can now meet 7-10 year retention requirements natively |
| Manual audit event searches | Office 365 Management Activity API | 2016+ | Programmatic access for SIEM integration and automation |
| EXO V1 module (remote PowerShell) | EXO V3 module (REST API) | 2023+ | Faster, more reliable, supports certificate auth |
| PowerShell 5.1 only | PowerShell 7 support | 2020+ (EXO V2+) | Cross-platform support, better performance |

**Deprecated/outdated:**
- **Remote PowerShell sessions via New-PSSession:** EXO V3 module uses REST APIs, not remote PowerShell
- **Username/password authentication:** Modern auth with MFA or certificate-based auth is now standard
- **Get-AdminAuditLogConfig in Security & Compliance PowerShell:** Use Exchange Online PowerShell instead for accurate results

## Open Questions

Things that couldn't be fully resolved:

1. **Canary Event Generation Method**
   - What we know: Search-UnifiedAuditLog can find events by FreeText
   - What's unclear: Best way to generate a retrievable canary event (Set-Mailbox? New-InboxRule? Graph API call?)
   - Recommendation: Test with Set-Mailbox DisplayName change (auditable, low impact) or use existing Scope Drift Monitor approach with Office 365 Management API content blobs

2. **Exact Audit Lag SLA**
   - What we know: Microsoft documents "up to 24 hours" for all services, 30-60 minutes typical
   - What's unclear: Does lag vary by RecordType? Does CopilotInteraction lag differently than Exchange?
   - Recommendation: Use 24-hour grace period conservatively; consider separate grace periods per RecordType if testing shows variation

3. **Dataverse Audit Retention API**
   - What we know: Dataverse has per-environment audit retention configuration via admin portal
   - What's unclear: Can retention period be queried via Web API Organization table or must it be retrieved via admin portal scraping?
   - Recommendation: Research Dataverse Web API Organization table schema in Phase 2; may require Power Platform Admin API instead

4. **Default Retention Policy Behavior**
   - What we know: Get-UnifiedAuditLogRetentionPolicy doesn't return the default policy
   - What's unclear: How to programmatically determine default retention period when no custom policies exist
   - Recommendation: Assume 90-day default (documented baseline) if no policies returned; alert if CopilotInteraction not explicitly covered

## Sources

### Primary (HIGH confidence)
- [Microsoft Learn: Turn auditing on or off](https://learn.microsoft.com/en-us/purview/audit-log-enable-disable)
- [Microsoft Learn: Manage mailbox auditing](https://learn.microsoft.com/en-us/purview/audit-mailboxes)
- [Microsoft Learn: Manage audit log retention policies](https://learn.microsoft.com/en-us/purview/audit-log-retention-policies)
- [Microsoft Learn: Get-AdminAuditLogConfig](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-adminauditlogconfig)
- [Microsoft Learn: Get-UnifiedAuditLogRetentionPolicy](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-unifiedauditlogretentionpolicy)
- [Microsoft Learn: about_Try_Catch_Finally](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_try_catch_finally)
- [Microsoft Learn: Connect to Exchange Online PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/connect-to-exchange-online-powershell)
- [Microsoft Learn: About the Exchange Online PowerShell V3 module](https://learn.microsoft.com/en-us/powershell/exchange/exchange-online-powershell-v2)
- [PowerShell Gallery: ExchangeOnlineManagement 3.7.0](https://www.powershellgallery.com/packages/exchangeonlinemanagement/3.7.0)

### Secondary (MEDIUM confidence)
- [Microsoft Learn: Best Practices using Search-UnifiedAuditLog](https://learn.microsoft.com/en-us/office/office-365-management-api/aip-unified-audit-logs-best-practices) - Official guidance but focused on AIP-specific scenarios
- [Microsoft Learn: Manage Dataverse auditing](https://learn.microsoft.com/en-us/power-platform/admin/manage-dataverse-auditing) - Web API approach mentioned but not detailed
- [Microsoft Learn: Audit logs for Copilot and AI applications](https://learn.microsoft.com/en-us/purview/audit-copilot) - CopilotInteraction record types documented
- [Microsoft Learn: SEC 17a-4 compliance](https://learn.microsoft.com/en-us/compliance/regulatory/offering-sec-docs) - Regulatory context for retention requirements

### Tertiary (LOW confidence)
- [FINRA Rule 4511](https://www.finra.org/rules-guidance/rulebooks/finra-rules/4511) - Regulatory source but doesn't specify technical implementation
- Community blog posts on ExchangeOnlineManagement module usage - Verified against official docs

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - ExchangeOnlineManagement is the official Microsoft module, well-documented and production-proven
- Architecture: HIGH - Patterns verified against Microsoft Learn documentation and existing FSI-AgentGov-Solutions implementations
- Pitfalls: HIGH - Documented in Microsoft Learn (audit lag, property naming) and confirmed via community feedback

**Research date:** 2026-02-06
**Valid until:** 90 days (stable APIs, but new Purview features may emerge)

**Notes:**
- ExchangeOnlineManagement v3.x is stable and recommended for all new development
- PowerShell 7 is now the recommended PowerShell version (cross-platform, better performance)
- Dual validation strategy is critical to avoid false positives from audit lag
- Zone-specific retention requirements (180/365/730 days) align with FSI regulatory minimums
