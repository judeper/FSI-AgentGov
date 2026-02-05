# Phase 5: Scope Drift Monitor Completion - Research

**Researched:** 2026-02-04
**Domain:** Power Platform Solution Development, Audit Log Integration, Detection Flow Architecture
**Confidence:** HIGH

## Summary

This research covers the technical requirements for moving the Scope Drift Monitor from WIP (v1.0.0) to production-ready (v1.1.0). The solution requires implementing detection logic that compares agent baselines against actual access events from multiple audit sources, alerting workflows that deliver notifications via Teams and email, and a scope expansion approval workflow.

The existing solution has a solid foundation: Dataverse schema with 4 tables (fsi_agentscope, fsi_scopeitem, fsi_scopeviolation, fsi_expansionrequest), security roles (SDM Viewer/Analyst/Admin), and a baseline capture script (New-AgentBaseline.ps1). This phase focuses on implementing the missing detection and alerting components using patterns established in Phase 4 (Compliance Dashboard).

The standard approach uses Power Automate scheduled flows for polling audit sources (Unified Audit Log via Office 365 Management API, Dataverse audit tables), comparing accessed resources against scope definitions, and creating violation records with Teams Adaptive Card and email notifications. Per CONTEXT.md decisions: fixed 15-minute detection frequency, dual delivery (Teams + email), single-approver expansion workflow, and graceful degradation when audit sources are unavailable.

**Primary recommendation:** Follow the Compliance Dashboard flow pattern (scheduled recurrence triggers, Dataverse connector operations, HTTP with Azure AD for Graph/Management API calls) to implement detection and alerting. Prioritize Unified Audit Log CopilotInteraction events as the primary data source with graceful fallback when other sources are unavailable.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Power Automate Cloud Flows | Latest | Detection logic, alerting, expansion workflow | Microsoft's standard low-code automation platform for M365 integration |
| Power Platform CLI (pac) | Latest (2026) | Solution pack/unpack operations | Microsoft's recommended tool for solution packaging |
| Office 365 Management API | v1.0 | Unified Audit Log access for CopilotInteraction events | Primary source for Copilot agent activity data |
| Microsoft Graph API | v1.0 | SharePoint audit, user details | Standard M365 API for audit data access |
| Dataverse Web API | v9.2 | Scope definitions, violations, expansion requests | Standard data store for Power Platform solutions |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Microsoft Teams Adaptive Cards | v1.5 | Alert notifications with actionable buttons | When posting violation alerts to Teams channels |
| HTTP with Azure AD connector | Latest | Authenticated API calls to Graph/Management APIs | When querying audit logs from Power Automate flows |
| PowerShell 7.0+ | 7.0+ | Baseline capture script enhancements | For New-AgentBaseline.ps1 improvements |
| msal | Latest | Azure AD authentication for PowerShell scripts | Token acquisition for API calls |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Office 365 Management API | AuditLogQuery Graph API | Graph API is in beta status (moved back from v1.0 in April 2025); Management API is stable |
| Scheduled polling | Webhook subscriptions | Webhooks have 90-minute latency; polling at 15 min achieves real-time detection goal |
| Teams Adaptive Card | Email only | Teams provides richer UX with actionable buttons; CONTEXT.md requires both |

**Installation:**
```bash
# Power Platform CLI (via MSI installer)
# Download from: https://aka.ms/PowerPlatformCLI

# PowerShell dependencies for baseline script
Install-Module -Name Microsoft.PowerShell.SecretManagement -Scope CurrentUser
Install-Module -Name Az.Accounts -Scope CurrentUser

# Python dependencies (if using Python for testing)
pip install msal requests
```

## Architecture Patterns

### Recommended Project Structure
```
scope-drift-monitor/
├── templates/                          # Deployable artifacts (currently empty)
│   └── ScopeDriftMonitor_1_1_0.zip    # Unmanaged solution package
├── scripts/                            # PowerShell scripts
│   ├── New-AgentBaseline.ps1          # Enhanced baseline capture (exists)
│   ├── Invoke-DriftScan.ps1           # Manual drift detection (to create)
│   └── Test-AlertDelivery.ps1         # Alert testing utility (to create)
├── src/                                # Solution source (pac unpack output)
│   └── ScopeDriftMonitor/
│       ├── Other/
│       │   ├── Solution.xml           # Solution manifest
│       │   └── Customizations.xml     # Table definitions
│       ├── Workflows/
│       │   ├── SDM-DriftDetector.json      # Main detection flow
│       │   ├── SDM-AlertDispatcher.json    # Alert delivery flow
│       │   └── SDM-ExpansionProcessor.json # Approval workflow
│       ├── connectionreferences.json       # Connection definitions
│       └── environmentvariables.json       # Configurable settings
├── docs/                               # Implementation guides (existing)
│   ├── prerequisites.md               # Licensing/permissions (exists)
│   ├── dataverse-schema.md            # Table definitions (exists)
│   ├── baseline-configuration.md      # Baseline setup guide (to enhance)
│   ├── flow-configuration.md          # Flow setup guide (to create)
│   └── troubleshooting.md             # Common issues (to create)
└── README.md                           # Deployment documentation (to enhance)
```

### Pattern 1: Scheduled Detection Flow with Multi-Source Polling
**What:** Power Automate flow that runs on 15-minute schedule, queries multiple audit sources, and creates violations for out-of-scope access
**When to use:** Primary detection mechanism for all agent scope monitoring
**Example:**
```json
// Source: Compliance Dashboard CD-ScoreCalculator pattern + Office 365 Management API docs
{
  "triggers": {
    "Recurrence": {
      "recurrence": {
        "frequency": "Minute",
        "interval": 15,
        "startTime": "2026-01-01T00:00:00Z",
        "timeZone": "UTC"
      },
      "type": "Recurrence"
    }
  },
  "actions": {
    "Initialize_LastCheckTime": {
      "type": "InitializeVariable",
      "inputs": {
        "variables": [{
          "name": "LastCheckTime",
          "type": "string",
          "value": "@{addMinutes(utcNow(), -15)}"
        }]
      }
    },
    "Query_Unified_Audit_Log": {
      "type": "OpenApiConnection",
      "inputs": {
        "host": {
          "connectionName": "shared_http",
          "operationId": "InvokeHttp"
        },
        "parameters": {
          "method": "GET",
          "uri": "https://manage.office.com/api/v1.0/@{variables('TenantId')}/activity/feed/subscriptions/content?contentType=Audit.General&startTime=@{variables('LastCheckTime')}&endTime=@{utcNow()}",
          "authentication": {
            "type": "ActiveDirectoryOAuth",
            "audience": "https://manage.office.com",
            "tenant": "@{variables('TenantId')}",
            "clientId": "@{variables('ClientId')}",
            "secret": "@{variables('ClientSecret')}"
          }
        }
      }
    }
  }
}
```

### Pattern 2: Graceful Degradation for Missing Audit Sources
**What:** Detect which audit sources are available and continue with reduced coverage when sources fail
**When to use:** Every detection cycle to handle licensing/permission gaps
**Example:**
```json
// Source: CONTEXT.md decision on graceful degradation
{
  "Check_UAL_Available": {
    "type": "Scope",
    "actions": {
      "Query_UAL": { /* ... */ }
    },
    "runAfter": {},
    "metadata": {
      "comment": "Try Unified Audit Log - primary source"
    }
  },
  "UAL_Error_Handler": {
    "type": "Compose",
    "inputs": {
      "source": "Unified Audit Log",
      "status": "unavailable",
      "reason": "@{result('Query_UAL')?['error']?['message']}",
      "timestamp": "@{utcNow()}"
    },
    "runAfter": {
      "Check_UAL_Available": ["Failed", "TimedOut"]
    }
  },
  "Append_Source_Status": {
    "type": "AppendToArrayVariable",
    "inputs": {
      "name": "SourceStatus",
      "value": "@outputs('UAL_Error_Handler')"
    },
    "runAfter": {
      "UAL_Error_Handler": ["Succeeded"]
    }
  },
  "Continue_With_Available_Sources": {
    "type": "Compose",
    "runAfter": {
      "Check_UAL_Available": ["Succeeded", "Failed", "TimedOut"]
    }
  }
}
```

### Pattern 3: Teams Adaptive Card for Violation Alerts
**What:** Post rich notification cards with violation details and action buttons to Teams
**When to use:** Every violation detection to notify agent owner and security team
**Example:**
```json
// Source: https://learn.microsoft.com/en-us/power-automate/create-adaptive-cards
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.5",
  "body": [
    {
      "type": "TextBlock",
      "text": "Scope Drift Violation Detected",
      "weight": "Bolder",
      "size": "Large",
      "color": "Attention"
    },
    {
      "type": "FactSet",
      "facts": [
        { "title": "Agent:", "value": "${agentName}" },
        { "title": "Violation:", "value": "${violationType}" },
        { "title": "Resource:", "value": "${resourceName}" },
        { "title": "Severity:", "value": "${severity}" },
        { "title": "Detected:", "value": "${detectedTime}" }
      ]
    },
    {
      "type": "TextBlock",
      "text": "The agent accessed a resource not included in its declared scope.",
      "wrap": true
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View Violation",
      "url": "${violationUrl}"
    },
    {
      "type": "Action.Submit",
      "title": "Request Scope Expansion",
      "data": {
        "action": "requestExpansion",
        "violationId": "${violationId}"
      }
    }
  ]
}
```

### Pattern 4: Baseline vs Actual Comparison Logic
**What:** Compare agent's declared scope (from fsi_agentscope) against accessed resources (from audit events)
**When to use:** Core detection logic executed for each audit event
**Example:**
```
// Pseudocode for comparison logic (implement in Power Automate Compose actions)

FOR EACH audit_event IN filtered_events:
  agent_id = extract_agent_id(audit_event)

  // Get agent's baseline scope
  scope = Query Dataverse: fsi_agentscope WHERE fsi_agentid = agent_id AND fsi_status = 2 (Active)

  IF scope IS NULL:
    // New agent with no baseline - create empty baseline, flag all access
    Create fsi_scopeviolation with type "No Baseline Defined"
    CONTINUE

  // Parse allowed resources from scope
  allowed_connectors = JSON.parse(scope.fsi_allowedconnectors)
  allowed_sites = JSON.parse(scope.fsi_allowedsites)
  allowed_tables = JSON.parse(scope.fsi_allowedtables)
  allowed_apis = JSON.parse(scope.fsi_allowedapis)

  // Check accessed resource against allowed list
  accessed_resource = extract_resource(audit_event)

  IF accessed_resource.type = "Connector":
    IF accessed_resource.name NOT IN allowed_connectors:
      Create fsi_scopeviolation with:
        fsi_violationtype = 1 (Unauthorized Connector)
        fsi_severity = 2 (High)
        fsi_resourcename = accessed_resource.name
        fsi_auditrecordid = audit_event.id

  IF accessed_resource.type = "SharePointSite":
    IF accessed_resource.url NOT IN allowed_sites:
      Create fsi_scopeviolation with:
        fsi_violationtype = 2 (Unauthorized SharePoint Site)
        fsi_severity = 3 (Medium)
        // ... etc
```

### Anti-Patterns to Avoid
- **Blocking on missing audit sources:** Per CONTEXT.md, log warning and continue with available sources; don't fail the entire detection run
- **Individual alert per violation:** Batch violations for same agent within same detection window into single notification
- **Hardcoded recipients:** Use environment variables for notification recipients (SDM_NotificationEmail, SDM_SecurityTeam)
- **Missing baseline = skip detection:** Per CONTEXT.md, empty baseline means "monitor everything" - any access triggers violation
- **Synchronous approval workflow:** Use async approval actions that don't block the detection flow

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Audit log subscription | Custom webhook handler | Office 365 Management API subscription model | Handles retries, pagination, content availability delays |
| Adaptive Card formatting | Raw JSON construction | Adaptive Cards Designer + template | Visual editor validates schema, ensures Teams compatibility |
| Token acquisition | Manual OAuth flow | HTTP with Azure AD connector / msal library | Handles refresh, caching, multi-tenant scenarios |
| Solution packaging | Manual XML editing | pac solution pack CLI | Handles dependencies, connection refs, version control |
| Approval workflow | Custom approval table/logic | Power Automate Approvals connector | Built-in escalation, reminders, mobile experience |
| Deduplication | Custom duplicate check | Filter expressions + unique constraint | Let Dataverse handle at database level |

**Key insight:** The Office 365 Management API subscription model handles significant complexity (pagination, content availability, retries) that would be error-prone to implement manually. Use the established CoE Starter Kit pattern for audit log collection.

## Common Pitfalls

### Pitfall 1: CopilotInteraction Events Not Available
**What goes wrong:** Detection flow runs but finds no Copilot activity events in Unified Audit Log
**Why it happens:** Copilot audit events require E5/E5 Compliance license and up to 90 minutes latency from activity to log availability
**How to avoid:**
- Document E5 Compliance requirement in prerequisites
- Set expectation that events have ~90 minute lag
- Test with known Copilot activities and verify events appear
- Don't fail detection if no events found in window
**Warning signs:** "0 events found" in every detection run despite active Copilot usage

### Pitfall 2: Agent ID Mapping Failures
**What goes wrong:** Cannot match audit event to agent scope definition
**Why it happens:** Copilot Studio agent IDs may differ between authoring and runtime contexts; AppHost field varies by Copilot type
**How to avoid:**
- Store both agent ID and environment ID in scope definition
- Use combination of agent ID + environment for matching
- Log unmapped events for review rather than silently discarding
**Warning signs:** Violations created with "Unknown Agent" instead of resolved name

### Pitfall 3: Alert Flooding
**What goes wrong:** Security team receives hundreds of alerts for normal agent behavior
**Why it happens:** New agent with empty baseline (per CONTEXT.md: "monitor everything") triggers violation for every data access
**How to avoid:**
- Implement alert batching: one summary per agent per detection window
- Include "New Agent - Baseline Needed" classification separate from actual violations
- Provide link to baseline capture in new agent alerts
- Daily summary rollup for recurring low-severity violations
**Warning signs:** Security team disabling notifications or ignoring alerts

### Pitfall 4: Expansion Request Never Processed
**What goes wrong:** Approved expansion requests don't update agent scope
**Why it happens:** Expansion approval flow doesn't trigger scope update, or update fails silently
**How to avoid:**
- Use Power Automate Approvals with on-approval trigger
- Update scope immediately on approval (not batch)
- Verify scope update succeeded before closing expansion request
- Include rollback logic if scope update fails
**Warning signs:** Approved requests stay in "Approved" status but agent still gets violations

### Pitfall 5: 7-Day Auto-Deny Timeout Not Implemented
**What goes wrong:** Expansion requests sit in pending state indefinitely
**Why it happens:** No scheduled job to check request age and auto-deny
**How to avoid:**
- Add scheduled flow that runs daily to check request age
- Auto-deny after 7 days per CONTEXT.md
- Send notification to requestor before and after auto-deny
- Document timeout in expansion request creation notification
**Warning signs:** Old requests accumulating in "Pending" status

### Pitfall 6: Dataverse Audit Source Requires Separate Configuration
**What goes wrong:** Dataverse table access not detected despite enabled auditing
**Why it happens:** Dataverse auditing must be enabled at environment level, then per-table, then per-column; different from Unified Audit Log
**How to avoid:**
- Document Dataverse audit configuration as separate prerequisite
- Check audit configuration before assuming source is available
- Fall back gracefully if Dataverse audit not configured
**Warning signs:** SharePoint and connector access detected but Dataverse table access invisible

## Code Examples

Verified patterns from official sources:

### CopilotInteraction Event Structure
```json
// Source: https://learn.microsoft.com/en-us/office/office-365-management-api/copilot-schema
{
  "RecordType": 261,
  "Operation": "CopilotInteraction",
  "UserId": "admin@contoso.onmicrosoft.com",
  "Workload": "Copilot",
  "EventData": {
    "AppHost": "CopilotStudio",
    "Contexts": [
      {
        "Id": "https://contoso.sharepoint.com/sites/CustomerKB/Documents/FAQ.docx",
        "Type": "docx"
      }
    ],
    "AccessedResources": [
      {
        "Id": "document-guid",
        "Name": "FAQ.docx",
        "SiteUrl": "https://contoso.sharepoint.com/sites/CustomerKB",
        "Type": "docx",
        "SensitivityLabelId": "label-guid",
        "Action": "Read"
      }
    ],
    "AISystemPlugin": [
      { "Name": "SharePointConnector", "Enabled": true }
    ]
  }
}
```

### Office 365 Management API Subscription Setup
```powershell
# Source: https://learn.microsoft.com/en-us/power-platform/guidance/coe/setup-auditlog-http

# Start subscription (run once)
$tenantId = $env:AZURE_TENANT_ID
$token = Get-AccessToken -Scope "https://manage.office.com/.default"

$uri = "https://manage.office.com/api/v1.0/$tenantId/activity/feed/subscriptions/start?contentType=Audit.General"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers
# Returns 200 if new subscription, 400 if already subscribed

# List available content blobs
$startTime = (Get-Date).AddMinutes(-15).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss")
$endTime = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss")

$contentUri = "https://manage.office.com/api/v1.0/$tenantId/activity/feed/subscriptions/content?contentType=Audit.General&startTime=$startTime&endTime=$endTime"
$contentBlobs = Invoke-RestMethod -Uri $contentUri -Headers $headers

# Fetch each content blob
foreach ($blob in $contentBlobs) {
    $events = Invoke-RestMethod -Uri $blob.contentUri -Headers $headers

    # Filter for CopilotInteraction events
    $copilotEvents = $events | Where-Object { $_.RecordType -eq 261 }

    foreach ($event in $copilotEvents) {
        # Process event...
    }
}
```

### Dataverse Violation Record Creation
```json
// Source: Existing dataverse-schema.md + Compliance Dashboard pattern
{
  "fsi_name": "Unauthorized SharePoint Site Access - Customer Service Agent",
  "fsi_agentscopeid@odata.bind": "/fsi_agentscopes(scope-guid)",
  "fsi_violationtype": 2,
  "fsi_resourcename": "HR Policies Site",
  "fsi_resourceurl": "https://contoso.sharepoint.com/sites/HR-Policies",
  "fsi_severity": 3,
  "fsi_status": 1,
  "fsi_detectedon": "2026-02-04T15:30:00Z",
  "fsi_auditrecordid": "audit-record-guid",
  "fsi_accessdetails": "{\"user\":\"user@contoso.com\",\"action\":\"Read\",\"file\":\"Policy-2026.docx\"}"
}
```

### Teams Adaptive Card Post via Power Automate
```json
// Source: https://learn.microsoft.com/en-us/power-automate/create-adaptive-cards
// Action: Post adaptive card in a chat or channel
{
  "host": {
    "connectionName": "shared_teams",
    "operationId": "PostCardToChannel",
    "apiId": "/providers/Microsoft.PowerApps/apis/shared_teams"
  },
  "parameters": {
    "poster": "Flow bot",
    "location": "Channel",
    "groupId": "@{variables('SDM_TeamsGroupId')}",
    "channelId": "@{variables('SDM_TeamsChannelId')}",
    "card": {
      "type": "AdaptiveCard",
      "version": "1.5",
      "body": [
        {
          "type": "Container",
          "style": "attention",
          "items": [
            {
              "type": "TextBlock",
              "text": "Scope Drift Violation",
              "weight": "Bolder",
              "size": "Large"
            }
          ]
        },
        {
          "type": "FactSet",
          "facts": [
            { "title": "Agent", "value": "@{items('Apply_to_each')?['fsi_agentscopeid/fsi_name']}" },
            { "title": "Resource", "value": "@{items('Apply_to_each')?['fsi_resourcename']}" },
            { "title": "Severity", "value": "@{if(equals(items('Apply_to_each')?['fsi_severity'],1),'Critical',if(equals(items('Apply_to_each')?['fsi_severity'],2),'High',if(equals(items('Apply_to_each')?['fsi_severity'],3),'Medium','Low')))}" }
          ]
        }
      ]
    }
  }
}
```

### Expansion Approval Flow Pattern
```json
// Source: Power Automate Approvals + CONTEXT.md single-approver decision
{
  "Start_Approval": {
    "type": "OpenApiConnection",
    "inputs": {
      "host": {
        "connectionName": "shared_approvals",
        "operationId": "CreateAnApproval",
        "apiId": "/providers/Microsoft.PowerApps/apis/shared_approvals"
      },
      "parameters": {
        "approvalType": "Basic",
        "title": "Scope Expansion Request: @{triggerOutputs()?['body/fsi_name']}",
        "assignedTo": "@{variables('SDM_SecurityTeamEmail')}",
        "details": "Agent: @{triggerOutputs()?['body/fsi_agentscopeid/fsi_name']}\n\nResource: @{triggerOutputs()?['body/fsi_resourcename']}\n\nJustification: @{triggerOutputs()?['body/fsi_justification']}\n\nRequested by: @{triggerOutputs()?['body/fsi_requestedby/fullname']}",
        "itemLink": "@{concat('https://make.powerapps.com/environments/', variables('EnvironmentId'), '/entities/fsi_expansionrequest/', triggerOutputs()?['body/fsi_expansionrequestid'])}",
        "itemLinkDescription": "View Request in Dataverse"
      }
    }
  },
  "Wait_For_Approval": {
    "type": "OpenApiConnection",
    "inputs": {
      "host": {
        "connectionName": "shared_approvals",
        "operationId": "WaitForAnApproval",
        "apiId": "/providers/Microsoft.PowerApps/apis/shared_approvals"
      },
      "parameters": {
        "approvalId": "@{body('Start_Approval')?['approvalId']}"
      }
    },
    "runAfter": {
      "Start_Approval": ["Succeeded"]
    }
  },
  "Condition_Approved": {
    "type": "If",
    "expression": {
      "equals": ["@{body('Wait_For_Approval')?['outcome']}", "Approve"]
    },
    "actions": {
      "Update_Agent_Scope": { /* ... */ },
      "Update_Request_Approved": { /* ... */ },
      "Close_Related_Violations": { /* ... */ }
    },
    "else": {
      "actions": {
        "Update_Request_Denied": { /* ... */ },
        "Notify_Requestor_Denied": { /* ... */ }
      }
    }
  }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SolutionPackager.exe | pac solution CLI | 2023-2024 | Unified CLI, better errors, integrated auth |
| Teams incoming webhooks | Power Automate + Teams connector | March 2026 deadline | O365 Connectors retiring; must use Power Automate |
| AuditLogQuery Graph API v1.0 | Office 365 Management API | April 2025 | Graph API moved back to beta; Management API is stable |
| Defender CloudAppEvents only | Unified Audit Log + CloudAppEvents | January 2026 | CopilotInteraction events added to Unified Audit Log |
| Custom approval tables | Power Automate Approvals connector | 2023+ | Built-in escalation, reminders, mobile experience |

**Deprecated/outdated:**
- **Teams incoming webhooks / O365 Connectors:** Retiring March 31, 2026; migrate to Power Automate workflows
- **AuditLogQuery Graph API v1.0:** Moved back to beta in April 2025 due to issues; use Office 365 Management API instead
- **Manual JSON construction for Adaptive Cards:** Use Adaptive Cards Designer for validation and preview

## Open Questions

Things that couldn't be fully resolved:

1. **CopilotInteraction Event Field Mapping for Custom Agents**
   - What we know: AppHost field indicates Copilot type; CopilotStudio appears for custom agents
   - What's unclear: Exact field that contains Copilot Studio agent ID vs generic Copilot session ID
   - Recommendation: Implement logging of raw events during testing to discover exact field paths; use Contexts array "Id" field for agent identification

2. **Defender CloudAppEvents Access via Power Automate**
   - What we know: CloudAppEvents available via Advanced Hunting in Defender portal
   - What's unclear: Whether Power Automate can query CloudAppEvents directly or only via Microsoft Graph Security API
   - Recommendation: Treat CloudAppEvents as "nice to have" source in v1.1.0; focus on Unified Audit Log as primary

3. **SharePoint Audit Log Granularity**
   - What we know: SharePoint audit captures site/library access
   - What's unclear: Whether individual file access within a library can be attributed to specific AI agent vs user
   - Recommendation: Use SharePoint site-level matching; document limitation in troubleshooting guide

4. **Alert Batching Window Duration**
   - What we know: CONTEXT.md specifies dual delivery (Teams + email) per violation
   - What's unclear: Whether to batch multiple violations for same agent into one notification
   - Recommendation: Batch violations per agent per detection window (15 min) into single notification with list of resources

## Sources

### Primary (HIGH confidence)
- [Office 365 Management API - CopilotInteraction Schema](https://learn.microsoft.com/en-us/office/office-365-management-api/copilot-schema) - Event structure, fields, access patterns
- [Power Automate - Dataverse Triggers](https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger) - When a row is added/modified trigger
- [Power Automate - Adaptive Cards](https://learn.microsoft.com/en-us/power-automate/create-adaptive-cards) - Teams card creation and posting
- [CoE Starter Kit - Audit Log HTTP](https://learn.microsoft.com/en-us/power-platform/guidance/coe/setup-auditlog-http) - Office 365 Management API integration pattern
- Existing Compliance Dashboard solution (`/Users/admin/dev/FSI-AgentGov-Solutions/compliance-dashboard/`) - Flow patterns, connection references, environment variables

### Secondary (MEDIUM confidence)
- [Defender for Cloud Apps - AI Agent Protection](https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-protection) - Preview feature documentation
- [Microsoft Security Blog - Runtime Risk to Real-Time Defense](https://www.microsoft.com/en-us/security/blog/2026/01/23/runtime-risk-realtime-defense-securing-ai-agents/) - January 2026 AI agent security patterns
- [Dataverse Auditing Overview](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/auditing/overview) - Table-level audit configuration
- [Practical365 - AuditLog Query API](https://practical365.com/auditlog-query-api-deeper-look/) - Graph API status and workarounds

### Tertiary (LOW confidence)
- Community discussions on CopilotInteraction event parsing - general patterns observed
- Teams webhook migration blog posts - transition patterns documented

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Power Platform CLI, Office 365 Management API, and Power Automate patterns are official Microsoft tools with current documentation
- Architecture: HIGH - Patterns derived from Compliance Dashboard (successfully completed in Phase 4) and official CoE Starter Kit
- Pitfalls: HIGH - Common issues documented in Microsoft troubleshooting guides and verified against existing solution structure
- Code examples: HIGH - All examples from official Microsoft Learn docs or existing solution patterns
- Detection logic: MEDIUM - CopilotInteraction event structure documented but exact agent ID mapping for custom agents needs runtime validation

**Research date:** 2026-02-04
**Valid until:** 30 days (Power Platform updates monthly; Office 365 Management API stable; Teams Adaptive Cards stable)
