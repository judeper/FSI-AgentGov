# Phase 3: Automated Orchestration & Alerting - Research

**Researched:** 2026-02-06
**Domain:** Power Automate cloud flows, Azure Automation, configuration drift detection, multi-channel alerting
**Confidence:** HIGH

## Summary

Phase 3 requires creating Power Automate cloud flows that execute the PowerShell validation orchestrators from Phases 1 and 2 on a daily schedule, detect configuration drift by comparing current validation results against historical baselines in Dataverse, and send multi-channel alerts (Teams adaptive cards for Critical/High severity, email for all failures) when issues are detected.

The standard approach is to use Azure Automation runbooks to host the PowerShell scripts, trigger them via Power Automate's Azure Automation connector on a recurrence schedule, query Dataverse validation history for drift detection, and post alerts using the Teams connector (adaptive cards) and Office 365 Outlook connector (email). This pattern is well-established in the Power Platform ecosystem and aligns with the existing solution's Tier 2 architecture (PowerShell + Power Automate + docs).

**Primary recommendation:** Use two Power Automate scheduled cloud flows (one for tenant validation, one for environment validation), Azure Automation runbooks to execute PowerShell orchestrators, Dataverse List Rows with OData filters for drift detection (query last known good baseline by Severity=Passed), and Teams + Outlook connectors for alerting with Scope-based error handling.

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| Power Automate Cloud Flows | Current | Scheduled orchestration and alerting | Native Power Platform automation, licensed with Power Apps Premium, standard for Tier 2 solutions |
| Azure Automation | Current | PowerShell 7 runbook hosting | Industry standard for scheduled PowerShell execution in cloud, supports 3-hour max runtime, MSAL.PS module support |
| Dataverse List Rows Action | Current | Query validation history with OData filters | Native Dataverse connector, supports filtering/sorting/top, standard for querying org-owned tables |
| Teams Connector (Post adaptive card) | Current | Visual alert cards with structured data | Standard for Teams notifications, supports JSON payload, native adaptive card rendering |
| Office 365 Outlook Connector (Send email V2) | Current | Email distribution list alerts | Standard for email automation, supports HTML, attachments, importance levels |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| MSAL.PS | 4.37+ | Dataverse/Graph API authentication in runbooks | Already used in Phase 2 scripts, required for token acquisition |
| ExchangeOnlineManagement | 3.0+ | Unified Audit Log access in tenant validator | Already used in Phase 1 scripts, required for Get-AdminAuditLogConfig |
| Microsoft.PowerApps.Administration.PowerShell | 2.0+ | Environment discovery in environment validator | Already used in Phase 2 scripts, required for Invoke-EnvironmentDiscovery.ps1 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Azure Automation | On-premises data gateway + local PowerShell | Gateway requires server infrastructure, complicates deployment, but avoids Azure subscription requirement |
| Teams adaptive cards | Plain text Teams messages | Simpler but loses structured data, actionability, and visual hierarchy for severity levels |
| Dataverse for drift baseline | Azure Storage/Blob | Lower cost but loses transactional consistency, query flexibility, and integration with existing validation history table |
| Daily recurrence trigger | HTTP trigger with external scheduler | More flexible but requires external dependency and exposes webhook endpoint |

**Installation:**
```bash
# Azure Automation modules (imported via Azure Portal)
# Navigate to Automation Account > Modules > Add module from gallery
- MSAL.PS (v4.37+)
- ExchangeOnlineManagement (v3.0+)
- Microsoft.PowerApps.Administration.PowerShell (v2.0+)

# Power Automate connectors (no installation, licensed features)
- Azure Automation (standard connector)
- Microsoft Dataverse (standard connector)
- Microsoft Teams (standard connector)
- Office 365 Outlook (standard connector)
```

## Architecture Patterns

### Recommended Flow Structure (Tenant Validation Flow)

```
┌─ Recurrence Trigger (daily, 6:00 AM)
│
├─ Scope: Try
│   ├─ Azure Automation: Create job (runbook: Invoke-TenantAuditValidation)
│   ├─ Do Until: Job status = Completed/Failed
│   │   ├─ Delay (30 seconds)
│   │   └─ Azure Automation: Get job status
│   ├─ Azure Automation: Get job output
│   ├─ Parse JSON: Extract validation results
│   │
│   ├─ Dataverse: List rows (drift detection query)
│   │   Filter: Scope eq 'Tenant' and Severity eq 1 (Passed)
│   │   Order by: createdon desc
│   │   Top: 1
│   │
│   ├─ Condition: Current severity worse than baseline?
│   │   ├─ Yes (drift detected):
│   │   │   ├─ Compose: Build adaptive card JSON
│   │   │   ├─ Condition: Severity = Critical or High?
│   │   │   │   └─ Yes: Teams: Post adaptive card to channel
│   │   │   └─ Office 365 Outlook: Send email (all failures)
│   │   └─ No (no drift): (no action)
│
└─ Scope: Catch (configure run after: has failed, has timed out)
    └─ Office 365 Outlook: Send error notification
```

### Recommended Flow Structure (Environment Validation Flow)

```
┌─ Recurrence Trigger (daily, 7:00 AM)
│
├─ Scope: Try
│   ├─ Azure Automation: Create job (runbook: Invoke-EnvironmentAuditValidation)
│   ├─ Do Until: Job status = Completed/Failed
│   │   ├─ Delay (30 seconds)
│   │   └─ Azure Automation: Get job status
│   ├─ Azure Automation: Get job output
│   ├─ Parse JSON: Extract validation results
│   │
│   ├─ Apply to each: Environment in results
│   │   ├─ Dataverse: List rows (per-environment drift detection)
│   │   │   Filter: EnvironmentId eq '{env_id}' and ValidationType eq 'Orchestrator' and Severity eq 1
│   │   │   Order by: createdon desc
│   │   │   Top: 1
│   │   │
│   │   ├─ Condition: Current severity worse than baseline?
│   │   │   ├─ Yes (drift detected):
│   │   │   │   ├─ Compose: Build adaptive card JSON (environment-specific)
│   │   │   │   ├─ Condition: Severity = Critical or High?
│   │   │   │   │   └─ Yes: Teams: Post adaptive card to channel
│   │   │   │   └─ Office 365 Outlook: Send email
│   │   │   └─ No (no drift): (no action)
│
└─ Scope: Catch (configure run after: has failed, has timed out)
    └─ Office 365 Outlook: Send error notification
```

### Pattern 1: Azure Automation Integration

**What:** Power Automate triggers Azure Automation runbooks and retrieves output.

**When to use:** PowerShell scripts require modules, long runtime (>2 minutes), or complex logic not suited for inline code.

**Example:**
```yaml
# Azure Automation: Create job action
Runbook name: Invoke-TenantAuditValidation
Parameters:
  Zone: 3
  OutputFormat: JSON
Wait for job: No

# Do Until: Job complete
Condition: @equals(body('Get_job_status')?['status'], 'Completed')
Actions:
  - Delay: 30 seconds
  - Azure Automation: Get job status (Job ID from previous step)

# Azure Automation: Get job output
Job ID: [dynamic content from Create job]
Output: JSON string containing validation results
```

**Key insights:**
- Azure Automation jobs run asynchronously; must poll for completion
- Job output is retrieved separately via Get job output action
- Maximum runtime: 3 hours per job
- Startup overhead: 30-60 seconds per job

### Pattern 2: Configuration Drift Detection via Dataverse Query

**What:** Compare current validation result severity against last known good baseline (Severity=Passed).

**When to use:** Need to detect when audit configurations have regressed from compliant to non-compliant state.

**Example:**
```yaml
# Dataverse: List rows action
Table: Audit Validation History (fsi_auditvalidationhistory)
Filter rows: |
  fsi_scope eq 100000000 and
  fsi_severity eq 1 and
  fsi_validationtype eq 'UnifiedAuditLog'
Sort by: createdon descending
Row count: 1

# Comparison logic
Current severity: [from Parse JSON output]
Baseline severity: [from List rows - first result fsi_severity]

Drift detected: Current severity > Baseline severity
  (Error=5, Failed=4, GracePeriod=3, Warning=2, Passed=1)
```

**Key insights:**
- Severity option set values: Passed=1, Warning=2, GracePeriod=3, Failed=4, Error=5
- Numeric comparison: higher value = worse status
- Filter by ValidationType to detect drift per validation type (UAL, Mailbox, Retention)
- Use RunId to correlate all checks from single execution

### Pattern 3: Teams Adaptive Card Alerts

**What:** Post structured JSON alert cards to Teams channel with visual severity indicators.

**When to use:** Need actionable, visually distinctive alerts for Critical/High severity findings that require immediate attention.

**Example:**
```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    {
      "type": "Container",
      "style": "attention",
      "items": [
        {
          "type": "TextBlock",
          "text": "🚨 Audit Configuration Drift Detected",
          "size": "ExtraLarge",
          "weight": "Bolder",
          "color": "Attention"
        },
        {
          "type": "FactSet",
          "facts": [
            {"title": "Severity", "value": "@{items('Apply_to_each')?['Severity']}"},
            {"title": "Validation Type", "value": "@{items('Apply_to_each')?['ValidationType']}"},
            {"title": "Environment", "value": "@{items('Apply_to_each')?['EnvironmentName']}"},
            {"title": "Status", "value": "@{items('Apply_to_each')?['OverallStatus']}"},
            {"title": "Timestamp", "value": "@{items('Apply_to_each')?['Timestamp']}"}
          ]
        },
        {
          "type": "TextBlock",
          "text": "@{items('Apply_to_each')?['Reason']}",
          "wrap": true
        }
      ]
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View Details",
      "url": "https://make.powerapps.com/environments/@{items('Apply_to_each')?['EnvironmentId']}"
    }
  ]
}
```

**Key insights:**
- Use `Container` with `style: "attention"` for critical alerts (red border)
- `FactSet` provides clean key-value display
- Dynamic content inserted via @{expression} syntax
- `Action.OpenUrl` for direct navigation to environment or validation history
- Validate JSON at https://adaptivecards.io/designer/ before deployment

### Pattern 4: Error Handling with Scope Try-Catch

**What:** Group flow actions in Scope containers and configure run-after conditions for error handling.

**When to use:** Need to prevent flow failures from silently failing and ensure error notifications are sent.

**Example:**
```yaml
# Scope: Try
Actions:
  - Azure Automation: Create job
  - Do Until: Job complete
  - Parse JSON
  - Dataverse queries
  - Teams/Email alerts

# Scope: Catch
Configure run after:
  - Scope: Try has failed ✓
  - Scope: Try has timed out ✓
  - Scope: Try is skipped (leave unchecked)
  - Scope: Try has succeeded (leave unchecked)

Actions:
  - Office 365 Outlook: Send email
    To: compliance-team@organization.com
    Subject: "[ERROR] Audit Validation Flow Failed"
    Body: |
      The automated audit validation flow encountered an error.

      Flow: @{workflow()['name']}
      Run ID: @{workflow()['run']['name']}
      Error: @{body('Scope_Try')?['error']}
```

**Key insights:**
- Try/Catch pattern not built-in; emulated with Scope + Configure run after
- Catch scope runs only when Try scope fails or times out
- Access error details via `@{body('Scope_Try')?['error']}`
- Send error notifications to ensure no silent failures

### Anti-Patterns to Avoid

- **Manual JSON parsing instead of Parse JSON action:** Error-prone, loses dynamic content IntelliSense, harder to maintain
- **Single flow for both tenant and environment validation:** Creates long-running flows prone to timeout, harder to debug, loss of granular error handling
- **Hard-coded severity thresholds instead of Dataverse baseline comparison:** Breaks when baseline improves (e.g., Warning → Passed), generates false alerts
- **Inline PowerShell in Power Automate instead of runbooks:** Limited to 2-minute execution, no module support, no credential management

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| PowerShell execution from cloud flows | Custom HTTP API wrapper for PowerShell scripts | Azure Automation runbooks with Create job action | Azure Automation provides module management, credential storage, logging, long runtime support (3 hours), retry logic, and native Power Automate integration |
| Drift detection logic | Custom timestamp comparison or file-based baselines | Dataverse query with OData filter for last Passed result | Dataverse provides transactional consistency, query flexibility, audit trail, and avoids file system dependencies or external storage |
| Teams notification formatting | Plain text concatenation or HTML email to Teams channel | Teams adaptive cards with JSON schema | Adaptive cards provide structured data display, visual hierarchy, action buttons, mobile support, and accessibility compliance |
| Error handling | Email on every step failure | Scope Try-Catch pattern with centralized error notification | Scope pattern provides granular error isolation, reduces alert fatigue, consolidates error handling logic, and follows Power Automate best practices |
| Job status polling | Fixed delay (e.g., wait 5 minutes) | Do Until loop with 30-second interval checking job status | Do Until provides early completion detection (job finishes in 1 minute but only waits 1 minute, not 5), prevents unnecessary delays, and adapts to varying job durations |

**Key insight:** Azure Automation + Power Automate integration is the Microsoft-endorsed pattern for scheduled PowerShell execution from cloud flows. Custom API wrappers introduce maintenance burden, security risks, and lack native credential management.

## Common Pitfalls

### Pitfall 1: Job Output Truncation

**What goes wrong:** Azure Automation job output exceeds 5 MB limit, causing Get job output to fail or return truncated results.

**Why it happens:** PowerShell Write-Output accumulates all output in job stream. Large validation runs (100+ environments) generate verbose logs that exceed limit.

**How to avoid:**
- Use -OutputPath parameter in orchestrators to write JSON results to file/blob storage instead of output stream
- Limit Write-Host/Write-Verbose usage in production runbooks
- Retrieve results from Dataverse validation history table instead of job output for large runs

**Warning signs:**
- Flow fails at Get job output step with "Output too large" error
- JSON parsing fails with incomplete data
- Missing environment results in Apply to each loop

### Pitfall 2: Runbook Module Version Drift

**What goes wrong:** Flow works in test but fails in production because runbook modules are outdated or missing.

**Why it happens:** Azure Automation modules must be manually updated; they don't auto-update. New module versions may be required by PowerShell scripts but not available in Automation Account.

**How to avoid:**
- Pin module versions in runbook #Requires statements (e.g., #Requires -Modules @{ModuleName='MSAL.PS'; RequiredVersion='4.37.0'})
- Document required module versions in deployment guide
- Test runbooks in Automation Account before deploying flows
- Set up Azure Automation module update schedule (weekly)

**Warning signs:**
- Runbook fails with "Module not found" or "Method not found" errors
- Scripts work locally but fail in Automation Account
- Different behavior between dev and prod Automation Accounts

### Pitfall 3: OData Filter Syntax Errors

**What goes wrong:** Dataverse List Rows returns no results or errors out due to malformed OData filter.

**Why it happens:** OData syntax is case-sensitive, requires specific operators (eq not =), and column names must match schema exactly (fsi_severity not Severity).

**How to avoid:**
- Use Dataverse schema names (fsi_severity, fsi_scope) not display names
- Test filters in Dataverse Advanced Find or OData query builder first
- Use eq/ne/gt/lt operators (not =, !=, >, <)
- Quote string values: `fsi_validationtype eq 'UnifiedAuditLog'`
- Use numeric values for option sets: `fsi_severity eq 1` (not 'Passed')

**Warning signs:**
- List Rows returns empty array despite records existing
- Error: "Invalid filter clause"
- Flow succeeds but drift detection never triggers

### Pitfall 4: Teams Connector Permissions

**What goes wrong:** Flow fails to post adaptive cards with "Forbidden" or "Unauthorized" error.

**Why it happens:** Power Automate Teams connector requires Workflows app to be installed in target Teams channel, and flow owner must have posting permissions.

**How to avoid:**
- Install Workflows app in Teams channel (Apps > Search "Workflows" > Add to channel)
- Grant flow service account posting permissions to channel
- Test with "Post as Flow bot" option before using adaptive cards
- Document Teams setup in deployment guide

**Warning signs:**
- HTTP 403 error when posting to Teams
- "App not installed" error message
- Adaptive cards work in test channel but fail in production channel

### Pitfall 5: Email Distribution List Resolution

**What goes wrong:** Outlook connector fails to send email with "Recipient not found" error for distribution list.

**Why it happens:** Some connectors require full SMTP address (group@domain.com) and don't resolve Exchange aliases or display names.

**How to avoid:**
- Use full SMTP addresses in To/CC fields (not display names)
- Test email action with single recipient first, then distribution list
- Verify distribution list allows external senders if flow runs from service account
- Use connection reference with named account (not default user connection)

**Warning signs:**
- Email sends to individual users but fails for groups
- "Recipient could not be resolved" error
- Emails arrive for some recipients but not all

## Code Examples

Verified patterns from official sources:

### Scheduled Trigger Configuration

```yaml
# Power Automate: Recurrence trigger
# Source: https://learn.microsoft.com/en-us/power-automate/run-scheduled-tasks
Trigger: Recurrence
Interval: 1
Frequency: Day
Time zone: (UTC-08:00) Pacific Time (US & Canada)
At these hours: 6
At these minutes: 0
# Result: Runs daily at 6:00 AM Pacific Time
```

### Azure Automation Job Execution Pattern

```yaml
# Source: https://damobird365.com/power-automate-meets-powershell-in-azure/
Action: Azure Automation - Create job
  Resource Group: rg-audit-validator
  Automation Account: aa-fsi-validation
  Runbook Name: Invoke-TenantAuditValidation
  Run On: Azure
  Parameters:
    Zone: 3
    Verbose: false
  Wait for Job: No

Action: Do Until
  Condition: @equals(body('Get_job_status')?['status'], 'Completed')
  Timeout: PT2H
  Count: 240
  Actions:
    - Delay
        Count: 30
        Unit: Second
    - Azure Automation - Get job
        Job ID: @{body('Create_job')?['jobId']}

Action: Azure Automation - Get job output
  Job ID: @{body('Create_job')?['jobId']}
  Output: @{body('Get_job_output')?['value']}
```

### Dataverse Drift Detection Query

```yaml
# Source: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query/filter-rows
Action: Microsoft Dataverse - List rows
  Table name: Audit Validation History (fsi_auditvalidationhistory)
  Filter Query: |
    fsi_scope eq 100000000 and
    fsi_validationtype eq 'UnifiedAuditLog' and
    fsi_severity eq 1
  Sort By: createdon desc
  Row count: 1

# Parse baseline result
Baseline severity: @{first(body('List_rows')?['value'])?['fsi_severity']}
Current severity: @{body('Parse_JSON')?['Validators']?['UnifiedAuditLog']?['SeverityValue']}

# Drift condition
Condition: @greater(variables('CurrentSeverity'), variables('BaselineSeverity'))
```

### Teams Adaptive Card Alert Template

```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    {
      "type": "Container",
      "style": "attention",
      "items": [
        {
          "type": "ColumnSet",
          "columns": [
            {
              "type": "Column",
              "width": "auto",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "🚨",
                  "size": "ExtraLarge"
                }
              ]
            },
            {
              "type": "Column",
              "width": "stretch",
              "items": [
                {
                  "type": "TextBlock",
                  "text": "Audit Configuration Drift",
                  "size": "Large",
                  "weight": "Bolder",
                  "color": "Attention"
                },
                {
                  "type": "TextBlock",
                  "text": "@{utcNow()}",
                  "isSubtle": true,
                  "spacing": "None"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "FactSet",
      "facts": [
        {
          "title": "Severity",
          "value": "@{body('Parse_JSON')?['OverallStatus']}"
        },
        {
          "title": "Validation Type",
          "value": "@{body('Parse_JSON')?['ValidationType']}"
        },
        {
          "title": "Environment",
          "value": "@{coalesce(body('Parse_JSON')?['EnvironmentName'], 'Tenant-level')}"
        }
      ]
    },
    {
      "type": "TextBlock",
      "text": "**Reason:** @{body('Parse_JSON')?['Reason']}",
      "wrap": true
    },
    {
      "type": "TextBlock",
      "text": "**Remediation:** @{body('Parse_JSON')?['RemediationHint']}",
      "wrap": true,
      "spacing": "Small"
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View Validation History",
      "url": "https://make.powerapps.com"
    }
  ]
}
```

### Email Alert Template

```yaml
# Source: https://learn.microsoft.com/en-us/power-automate/email-overview
Action: Office 365 Outlook - Send an email (V2)
  To: compliance-team@organization.com
  Subject: "[ALERT] Audit Configuration Drift - @{body('Parse_JSON')?['ValidationType']}"
  Body: |
    <h2 style="color: #d13438;">⚠️ Audit Configuration Drift Detected</h2>

    <table style="border-collapse: collapse; width: 100%;">
      <tr>
        <td style="padding: 8px; font-weight: bold;">Severity:</td>
        <td style="padding: 8px;">@{body('Parse_JSON')?['OverallStatus']}</td>
      </tr>
      <tr>
        <td style="padding: 8px; font-weight: bold;">Validation Type:</td>
        <td style="padding: 8px;">@{body('Parse_JSON')?['ValidationType']}</td>
      </tr>
      <tr>
        <td style="padding: 8px; font-weight: bold;">Environment:</td>
        <td style="padding: 8px;">@{coalesce(body('Parse_JSON')?['EnvironmentName'], 'Tenant-level')}</td>
      </tr>
      <tr>
        <td style="padding: 8px; font-weight: bold;">Timestamp:</td>
        <td style="padding: 8px;">@{body('Parse_JSON')?['Timestamp']}</td>
      </tr>
    </table>

    <h3>Details</h3>
    <p><strong>Reason:</strong> @{body('Parse_JSON')?['Reason']}</p>
    <p><strong>Remediation:</strong> @{body('Parse_JSON')?['RemediationHint']}</p>

    <hr/>
    <p style="font-size: 0.9em; color: #666;">
      This is an automated alert from the Audit Configuration Validator solution.
      Run ID: @{body('Parse_JSON')?['RunId']}
    </p>
  Importance: High
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| On-premises data gateway for PowerShell execution | Azure Automation runbooks with cloud-native module support | 2021-2022 (PowerShell 7 runbook support GA) | Eliminated server infrastructure dependency, enabled credential vault integration, reduced maintenance overhead |
| Plain text Teams messages or email-only alerts | Teams adaptive cards with JSON schema | 2020 (Adaptive Cards v1.4 support in Teams) | Improved actionability, visual hierarchy, mobile support, and accessibility compliance |
| Manual drift detection via scheduled reports | Automated baseline comparison with Dataverse queries | 2022-2023 (Power Automate Dataverse connector maturity) | Real-time drift detection, reduced alert fatigue (only alerts on regression), automated compliance evidence |
| Hard-coded SMTP servers for email | Office 365 Outlook connector with managed authentication | 2019-2020 (Power Platform connector standardization) | Eliminated credential management, supported MFA, reduced configuration complexity |

**Deprecated/outdated:**
- **HTTP action with custom PowerShell API:** Replaced by Azure Automation connector (2021). Custom APIs introduce security risks, lack credential management, and require separate hosting infrastructure.
- **Flow Bot for Teams posting:** Replaced by Workflows app + adaptive cards (2022). Flow Bot had limited formatting, no interactive elements, and inconsistent mobile rendering.
- **SharePoint lists for validation history:** Replaced by Dataverse tables (2020-2021). SharePoint lists lack transactional consistency, option set support, and org-owned table immutability.

## Open Questions

Things that couldn't be fully resolved:

1. **Azure Automation Account Placement**
   - What we know: Runbooks can run in same subscription as Dataverse or separate subscription
   - What's unclear: Whether cross-subscription execution affects latency or authentication complexity
   - Recommendation: Deploy in same Azure subscription as Power Platform Dataverse environment for simplified RBAC and reduced network latency. Document cross-subscription alternative in deployment guide.

2. **Adaptive Card Severity Color Coding**
   - What we know: `style: "attention"` provides red border, `style: "good"` provides green, `style: "warning"` provides yellow
   - What's unclear: Whether Teams mobile app renders all three styles consistently
   - Recommendation: Test adaptive cards on Teams mobile (iOS/Android) before production deployment. Fall back to emoji indicators (🚨/⚠️/✅) if color rendering is inconsistent.

3. **Distribution List Size Limits**
   - What we know: Office 365 Outlook connector supports distribution lists
   - What's unclear: Maximum number of recipients per email (some sources cite 500, others cite 1000)
   - Recommendation: Start with small distribution lists (<100 recipients). For larger compliance teams, use nested distribution lists or multiple email actions.

4. **Runbook Credential Management**
   - What we know: Azure Automation supports managed identities for Azure resource authentication
   - What's unclear: Whether managed identity supports all required PowerShell module operations (Exchange Online, Power Platform Admin)
   - Recommendation: Test managed identity authentication first. Fall back to Automation Account credential assets (username/password or certificate) if modules don't support managed identity.

## Sources

### Primary (HIGH confidence)

- [Power Automate scheduled flows](https://learn.microsoft.com/en-us/power-automate/run-scheduled-tasks) - Microsoft Learn official documentation on recurrence triggers and scheduling options
- [Azure Automation PowerShell runbooks](https://learn.microsoft.com/en-us/azure/automation/automation-runbook-output-and-messages) - Microsoft Learn official documentation on runbook output streams and job execution
- [Power Automate Teams adaptive cards](https://learn.microsoft.com/en-us/power-automate/create-adaptive-cards) - Microsoft Learn official documentation on posting adaptive cards to Teams channels
- [Office 365 Outlook connector](https://learn.microsoft.com/en-us/power-automate/email-overview) - Microsoft Learn official documentation on sending emails with Outlook connector
- [Dataverse OData filter queries](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/query/filter-rows) - Microsoft Learn official documentation on OData syntax for Dataverse queries
- [Azure Automation connector](https://learn.microsoft.com/en-us/connectors/azureautomation/) - Microsoft Learn connector reference for creating jobs and retrieving output
- [Power Automate error handling](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/error-handling) - Microsoft Learn best practices for Scope-based try-catch pattern

### Secondary (MEDIUM confidence)

- [Power Automate meets PowerShell in Azure](https://damobird365.com/power-automate-meets-powershell-in-azure/) - DamoBird365 blog post on Azure Automation integration patterns (2020, verified against current Microsoft Learn docs)
- [Schedule PowerShell Scripts Using Azure Automation](https://m365scripts.com/microsoft365/how-to-schedule-powershell-scripts-using-azure-automation/) - M365Scripts practical guide on module management and scheduling (2023)
- [Adaptive Cards with Power Automate](https://dev.to/seenakhan/adaptive-cards-with-power-automate-5bcm) - DEV Community tutorial on card design patterns (2022)
- [Configuration drift detection tools](https://www.josys.com/article/article-saas-security-automating-configuration-drift-detection-tools-and-techniques-for-it-managers) - Josys article on baseline comparison patterns (2024)

### Tertiary (LOW confidence)

- Community forum discussions on OData filter syntax edge cases (not linked - general pattern identification only)
- Stack Overflow posts on Teams connector permissions (not authoritative - verified against Microsoft Learn)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All components verified via Microsoft Learn official documentation and existing solution patterns (message-center-monitor)
- Architecture: HIGH - Patterns verified against Microsoft Learn best practices and existing Tier 2 solution implementations
- Pitfalls: MEDIUM - Based on community reports and best practices documentation; some scenarios not directly tested in this research phase

**Research date:** 2026-02-06
**Valid until:** 2026-05-06 (90 days - Power Platform is fast-moving, monthly feature releases may introduce new patterns)
