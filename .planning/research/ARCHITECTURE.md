# Architecture Patterns

**Domain:** Audit Configuration Validator
**Researched:** 2026-02-06

## Recommended Architecture

The Audit Configuration Validator follows the established FSI-AgentGov-Solutions Tier 2 pattern with PowerShell + Power Automate + Dataverse integration. The solution validates that comprehensive audit logging is properly enabled across tenant-level, Power Platform environments, and Microsoft Purview configurations.

### System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  Audit Configuration Validator                  │
├────────────────────────────────────────────────────────────────┤
│  PowerShell      │  Power Automate  │  Teams           │  Export│
│  Scanners        │  Orchestration   │  Alerts          │  Evidence│
└────────────────────────────────────────────────────────────────┘
                            ▲
                            │ Status Tracking
                            │
┌────────────────────────────────────────────────────────────────┐
│             Dataverse (Audit Configuration Status)              │
├────────────────┬────────────────┬────────────────┬─────────────┤
│ Tenant Config  │ Environment    │ Purview        │ Validation  │
│ Status         │ Config Status  │ Config Status  │ History     │
└────────────────┴────────────────┴────────────────┴─────────────┘
                            ▲
                            │ Validation Scans
                            │
┌─────────────┬──────────────┬──────────────┬────────────────────┐
│ Tenant      │ Power        │ Purview      │ Environment        │
│ Audit Log   │ Platform     │ Retention    │ Audit Settings     │
│ Config      │ Admin API    │ Policies     │ (Dataverse)        │
└─────────────┴──────────────┴──────────────┴────────────────────┘
```

## Integration Points with Existing Solutions

### Immediate Integrations (v1.0.0)

| Solution | Integration Point | How |
|----------|------------------|-----|
| **Deny Event Correlation** | Prerequisite check | Validate audit logging enabled before analyzing deny events |
| **Message Center Monitor** | Alert channel reuse | Use same Teams channel for audit config alerts |
| **Control 1.7 Documentation** | Playbook reference | Link to automated validation from manual playbooks |

### Deferred Integrations (v9+)

| Solution | Integration Point | Deferred Reason |
|----------|------------------|-----------------|
| **Environment Lifecycle Management** | Post-provisioning validation | Requires ELM v1.2+ webhook support |
| **Compliance Dashboard** | Aggregate audit config status | Requires dashboard extensibility framework |

**Design Decision:** Focus v1.0.0 on standalone validation capability. Integration with ELM and Compliance Dashboard requires architectural changes to those solutions (webhook/plugin patterns) that are out of scope for this milestone.

## Standard Solution Directory Structure

Based on analysis of scope-drift-monitor, conditional-access-automation, and deny-event-correlation-report, the standard FSI-AgentGov-Solutions structure is:

```
audit-configuration-validator/
├── README.md                          # Overview, quick start, prerequisites
├── CHANGELOG.md                       # Version history
├── docs/
│   ├── prerequisites.md               # Licensing, roles, dependencies
│   ├── dataverse-schema.md            # Table definitions with fsi_ prefix
│   ├── flow-configuration.md          # Power Automate flow specifications
│   ├── architecture.md                # System design (this could be adapted)
│   └── troubleshooting.md             # Common issues, error recovery
├── scripts/
│   ├── Test-TenantAuditConfig.ps1    # Validate tenant-level audit settings
│   ├── Test-EnvironmentAuditConfig.ps1 # Validate environment audit retention
│   ├── Test-PurviewRetention.ps1     # Validate Purview retention policies
│   ├── Export-AuditConfigEvidence.ps1 # Export quarterly evidence
│   └── Invoke-AuditConfigValidation.ps1 # Orchestration script
├── src/
│   └── AuditConfigValidator/          # Power Platform solution (unpacked)
│       ├── environmentvariables.json  # fsi_ACV_* variables
│       ├── connectionreferences.json  # fsi_cr_* references
│       └── Workflows/                 # Power Automate flows (unpacked JSON)
│           ├── ACV-DailyValidator.json
│           └── ACV-AlertDispatcher.json
└── templates/
    └── adaptive-card-alert.json       # Teams notification template
```

## New Components Required

### PowerShell Scripts (scripts/)

| Script | Purpose | APIs Used | Evidence Output |
|--------|---------|-----------|-----------------|
| `Test-TenantAuditConfig.ps1` | Validate unified audit log enabled | Exchange Online PowerShell | JSON, CSV |
| `Test-EnvironmentAuditConfig.ps1` | Validate environment audit retention (180d/1yr/7yr) | Power Platform Admin API | JSON, CSV |
| `Test-PurviewRetention.ps1` | Validate Purview retention policies exist | Security & Compliance PowerShell | JSON, CSV |
| `Export-AuditConfigEvidence.ps1` | Export quarterly compliance evidence | All APIs | JSON with SHA-256 hashes |
| `Invoke-AuditConfigValidation.ps1` | Orchestration script calling all validators | N/A | Aggregated report |

**Naming Convention:** Follows PowerShell Verb-Noun standard. `Test-*` for validation scripts, `Export-*` for evidence extraction, `Invoke-*` for orchestration.

### Dataverse Schema (src/AuditConfigValidator/)

Following fsi_ publisher prefix pattern from scope-drift-monitor:

#### Table: fsi_audittenantconfig

Tenant-level audit configuration status.

| Column | Type | Purpose |
|--------|------|---------|
| `fsi_audittenantconfigid` | GUID | Primary key |
| `fsi_name` | String (100) | "Tenant Audit Configuration" |
| `fsi_unifiedauditenabled` | Boolean | Unified audit log enabled |
| `fsi_mailboxauditenabled` | Boolean | Mailbox audit enabled |
| `fsi_lastvalidated` | DateTime | Last validation timestamp |
| `fsi_validationstatus` | Choice | Pass/Fail/Warning |
| `fsi_validationdetails` | Text | JSON with detailed findings |

#### Table: fsi_auditenvironmentconfig

Per-environment audit configuration status.

| Column | Type | Purpose |
|--------|------|---------|
| `fsi_auditenvironmentconfigid` | GUID | Primary key |
| `fsi_name` | String (200) | Environment name |
| `fsi_environmentid` | String (36) | Power Platform environment ID |
| `fsi_zone` | Choice | Zone 1/2/3 classification |
| `fsi_auditenabled` | Boolean | Audit enabled |
| `fsi_retentiondays` | Integer | Configured retention period |
| `fsi_expectedretentiondays` | Integer | Expected retention (180/365/2557) |
| `fsi_compliant` | Boolean | Meets zone requirements |
| `fsi_lastvalidated` | DateTime | Last validation timestamp |
| `fsi_validationdetails` | Text | JSON with detailed findings |

#### Table: fsi_purviewretentionconfig

Purview retention policy validation.

| Column | Type | Purpose |
|--------|------|---------|
| `fsi_purviewretentionconfigid` | GUID | Primary key |
| `fsi_name` | String (200) | Policy name |
| `fsi_policyid` | String (36) | Purview policy ID |
| `fsi_retentionperiod` | Integer | Retention in days |
| `fsi_recordtypes` | Text | Comma-separated record types |
| `fsi_coveredusers` | Text | User scope (All/Specific) |
| `fsi_enabled` | Boolean | Policy is active |
| `fsi_lastvalidated` | DateTime | Last validation timestamp |
| `fsi_compliant` | Boolean | Meets requirements |

#### Table: fsi_auditvalidationhistory

Immutable validation history log.

| Column | Type | Purpose |
|--------|------|---------|
| `fsi_auditvalidationhistoryid` | GUID | Primary key |
| `fsi_name` | String (200) | Validation run name |
| `fsi_validationtype` | Choice | Tenant/Environment/Purview/Full |
| `fsi_timestamp` | DateTime | Validation timestamp |
| `fsi_overallstatus` | Choice | Pass/Fail/Warning |
| `fsi_tenantstatus` | Choice | Pass/Fail/Warning |
| `fsi_environmentspassed` | Integer | Count of compliant environments |
| `fsi_environmentsfailed` | Integer | Count of non-compliant environments |
| `fsi_purviewpolicycompliant` | Boolean | Retention policies valid |
| `fsi_validationdetails` | Text | JSON with full results |
| `fsi_runby` | Lookup (User) | Who initiated validation |
| `fsi_correlationid` | String (36) | Workflow run ID |

**Security Model:** Organization-owned table with read-only privileges for non-admins. Follows ProvisioningLog immutability pattern from ELM.

### Power Automate Flows (src/AuditConfigValidator/Workflows/)

#### Flow 1: ACV-DailyValidator

| Component | Configuration |
|-----------|---------------|
| **Trigger** | Recurrence - Daily at 6 AM UTC |
| **Connections** | fsi_cr_powerapps, fsi_cr_http_azuread, fsi_cr_dataverse |
| **Steps** | 1. Run PowerShell scripts via Azure Automation<br>2. Parse JSON results<br>3. Upsert to Dataverse status tables<br>4. Create immutable history record<br>5. Trigger alert dispatcher if failures |
| **Concurrency** | Single run (prevent overlapping validations) |

#### Flow 2: ACV-AlertDispatcher

| Component | Configuration |
|-----------|---------------|
| **Trigger** | Dataverse - When validation history created with status = Fail/Warning |
| **Connections** | fsi_cr_dataverse, fsi_cr_teams, fsi_cr_outlook |
| **Steps** | 1. Read validation details<br>2. Format adaptive card<br>3. Post to Teams channel<br>4. Send email to compliance team |
| **Alert Severity** | Tenant failure = Critical, Environment failure = High, Purview warning = Medium |

### Connection References (src/AuditConfigValidator/connectionreferences.json)

Following fsi_cr_* naming convention:

```json
{
  "connectionReferences": [
    {
      "connectionReferenceLogicalName": "fsi_cr_dataverse",
      "connectionReferenceDisplayName": "Dataverse Connection",
      "connectorId": "/providers/Microsoft.PowerApps/apis/shared_commondataserviceforapps",
      "description": "Dataverse connection for audit configuration status tracking"
    },
    {
      "connectionReferenceLogicalName": "fsi_cr_exchangeonline",
      "connectionReferenceDisplayName": "Exchange Online Connection",
      "connectorId": "/providers/Microsoft.PowerApps/apis/shared_excelonline",
      "description": "Exchange Online PowerShell for tenant audit settings validation"
    },
    {
      "connectionReferenceLogicalName": "fsi_cr_http_azuread",
      "connectionReferenceDisplayName": "HTTP with Azure AD Connection",
      "connectorId": "/providers/Microsoft.PowerApps/apis/shared_webcontents",
      "description": "Power Platform Admin API for environment audit settings"
    },
    {
      "connectionReferenceLogicalName": "fsi_cr_teams",
      "connectionReferenceDisplayName": "Microsoft Teams Connection",
      "connectorId": "/providers/Microsoft.PowerApps/apis/shared_teams",
      "description": "Microsoft Teams for posting audit configuration alerts"
    },
    {
      "connectionReferenceLogicalName": "fsi_cr_outlook",
      "connectionReferenceDisplayName": "Office 365 Outlook Connection",
      "connectorId": "/providers/Microsoft.PowerApps/apis/shared_office365",
      "description": "Office 365 Outlook for email alerts to compliance team"
    }
  ]
}
```

### Environment Variables (src/AuditConfigValidator/environmentvariables.json)

Following fsi_ACV_* naming convention:

```json
{
  "environmentVariables": [
    {
      "schemaName": "fsi_ACV_TenantId",
      "displayName": "Tenant ID",
      "description": "Azure AD tenant ID for API authentication",
      "type": "String",
      "isRequired": true
    },
    {
      "schemaName": "fsi_ACV_ComplianceTeamEmail",
      "displayName": "Compliance Team Email",
      "description": "Email distribution list for audit configuration alerts",
      "type": "String",
      "isRequired": true
    },
    {
      "schemaName": "fsi_ACV_TeamsChannelId",
      "displayName": "Teams Channel ID",
      "description": "Teams channel for posting audit configuration alerts",
      "type": "String",
      "isRequired": false
    },
    {
      "schemaName": "fsi_ACV_TeamsGroupId",
      "displayName": "Teams Group ID",
      "description": "Teams group (team) ID for posting alerts",
      "type": "String",
      "isRequired": false
    },
    {
      "schemaName": "fsi_ACV_AlertOnWarnings",
      "displayName": "Alert on Warnings",
      "description": "Send alerts for warning-level findings (not just failures)",
      "type": "String",
      "defaultValue": "false",
      "isRequired": false
    }
  ]
}
```

## Teams Notification Pattern

Based on message-center-monitor and scope-drift-monitor patterns:

### Alert Delivery

| Method | Use Case | Implementation |
|--------|----------|----------------|
| **Adaptive Card to Teams** | Real-time visual alerts | Power Automate "Post adaptive card in a chat or channel" |
| **Email to Compliance Team** | Audit trail, escalation | Office 365 Outlook connector |
| **Dataverse Record** | Complete history | fsi_auditvalidationhistory table |

**Design Decision:** Use native Power Automate Teams connector (not deprecated incoming webhooks). Follows message-center-monitor pattern post Office 365 connector deprecation (March 31, 2026).

### Adaptive Card Template

```json
{
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    {
      "type": "TextBlock",
      "text": "Audit Configuration Validation Failed",
      "weight": "Bolder",
      "size": "Large",
      "color": "Attention"
    },
    {
      "type": "FactSet",
      "facts": [
        {"title": "Validation Time", "value": "${timestamp}"},
        {"title": "Overall Status", "value": "${status}"},
        {"title": "Tenant Audit", "value": "${tenantStatus}"},
        {"title": "Environments Failed", "value": "${environmentsFailed}"},
        {"title": "Purview Policies", "value": "${purviewStatus}"}
      ]
    },
    {
      "type": "TextBlock",
      "text": "Details:",
      "weight": "Bolder"
    },
    {
      "type": "TextBlock",
      "text": "${details}",
      "wrap": true
    }
  ],
  "actions": [
    {
      "type": "Action.OpenUrl",
      "title": "View Full Report",
      "url": "${reportUrl}"
    }
  ]
}
```

## Evidence Export Format

Following deny-event-correlation-report pattern for regulatory evidence:

### Export Structure

```
exports/
├── Q1-2026/
│   ├── TenantAuditConfig-Q1-2026.json       # Tenant validation results
│   ├── EnvironmentAuditConfig-Q1-2026.json  # Per-environment results
│   ├── PurviewRetention-Q1-2026.json        # Retention policy details
│   ├── ValidationHistory-Q1-2026.json       # Complete validation runs
│   └── manifest.json                        # SHA-256 integrity hashes
```

### Manifest Format

```json
{
  "quarter": "Q1-2026",
  "exportDate": "2026-04-01T00:00:00Z",
  "files": [
    {
      "name": "TenantAuditConfig-Q1-2026.json",
      "sha256": "abcd1234...",
      "recordCount": 90
    }
  ]
}
```

## Data Flow Architecture

### Scan → Validate → Alert → Evidence

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Scheduled Scan (Daily 6 AM UTC)                     │
│ - Trigger: Power Automate recurrence                        │
│ - Action: Call PowerShell scripts via Azure Automation      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        v
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Validation (PowerShell Scripts)                     │
│ - Test-TenantAuditConfig.ps1 → Tenant audit settings       │
│ - Test-EnvironmentAuditConfig.ps1 → Per-environment audit  │
│ - Test-PurviewRetention.ps1 → Retention policies           │
│ - Output: JSON results with Pass/Fail/Warning               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        v
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Status Update (Power Automate Flow)                 │
│ - Parse JSON results                                        │
│ - Upsert to fsi_audittenantconfig                          │
│ - Upsert to fsi_auditenvironmentconfig (per env)           │
│ - Upsert to fsi_purviewretentionconfig (per policy)        │
│ - Create immutable record in fsi_auditvalidationhistory    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        v
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Alert Dispatch (Conditional on Failures)            │
│ - Trigger: fsi_auditvalidationhistory status = Fail/Warning│
│ - Action: Post adaptive card to Teams                       │
│ - Action: Send email to compliance team                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        v
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Evidence Export (Quarterly via PowerShell)          │
│ - Manual or scheduled: Export-AuditConfigEvidence.ps1      │
│ - Export all validation results for Q1/Q2/Q3/Q4            │
│ - Generate SHA-256 hashes in manifest.json                 │
│ - Store in exports/ directory or Azure Blob Storage        │
└─────────────────────────────────────────────────────────────┘
```

## Suggested Build Order

Based on dependency analysis and existing solution patterns:

### Phase 1: Core PowerShell Scripts (Week 1)

**Rationale:** Foundation components needed before any automation.

1. **Test-TenantAuditConfig.ps1** - Validate unified audit log enabled
2. **Test-EnvironmentAuditConfig.ps1** - Validate environment audit retention
3. **Test-PurviewRetention.ps1** - Validate Purview retention policies
4. **Invoke-AuditConfigValidation.ps1** - Orchestration script

**Deliverable:** Standalone PowerShell validation capability.

### Phase 2: Dataverse Schema (Week 1)

**Rationale:** Required before Power Automate flows can store results.

1. Create option sets (Choices) for status values
2. Create fsi_audittenantconfig table
3. Create fsi_auditenvironmentconfig table
4. Create fsi_purviewretentionconfig table
5. Create fsi_auditvalidationhistory table (immutable, org-owned)
6. Configure security roles (Viewer, Operator, Admin)

**Deliverable:** Dataverse schema deployed to dev environment.

### Phase 3: Power Automate Flows (Week 2)

**Rationale:** Automates script execution and result storage.

1. Configure connection references (fsi_cr_dataverse, fsi_cr_http_azuread, etc.)
2. Configure environment variables (fsi_ACV_TenantId, etc.)
3. Build ACV-DailyValidator flow (scheduled trigger, script execution, result storage)
4. Build ACV-AlertDispatcher flow (Dataverse trigger, Teams/email notifications)
5. Test end-to-end flow execution

**Deliverable:** Automated daily validation with alerts.

### Phase 4: Evidence Export (Week 2)

**Rationale:** Regulatory compliance requirement.

1. **Export-AuditConfigEvidence.ps1** - Quarterly evidence export
2. Test evidence export with SHA-256 hashing
3. Document evidence collection procedures

**Deliverable:** Compliance evidence export capability.

### Phase 5: Documentation (Week 3)

**Rationale:** User-facing documentation for deployment and operation.

1. README.md with quick start
2. docs/prerequisites.md with licensing and roles
3. docs/dataverse-schema.md with complete table definitions
4. docs/flow-configuration.md with flow specifications
5. docs/troubleshooting.md with common issues

**Deliverable:** Complete solution documentation.

### Phase 6: Control 1.7 Integration (Week 3)

**Rationale:** Link automated solution to framework documentation.

1. Update Control 1.7 with link to solution
2. Update PowerShell Setup playbook with reference to automated validator
3. Update Verification Testing playbook with automated validation option
4. Add solution to solutions-index.md

**Deliverable:** Framework documentation updated.

## Component Dependencies

```
Test-*.ps1 scripts (no dependencies)
    ↓
Invoke-AuditConfigValidation.ps1 (depends on Test-*.ps1)
    ↓
Dataverse schema (no dependencies)
    ↓
Power Automate flows (depend on Dataverse + scripts)
    ↓
Export-AuditConfigEvidence.ps1 (depends on Dataverse schema)
    ↓
Documentation (depends on all above)
    ↓
Control 1.7 integration (depends on documentation)
```

## Scalability Considerations

| Concern | At 10 Environments | At 100 Environments | At 1000 Environments |
|---------|-------------------|---------------------|---------------------|
| **Scan Duration** | 2-3 minutes | 15-20 minutes | 2-3 hours |
| **Dataverse Storage** | Negligible | <10 MB | <100 MB |
| **API Throttling** | No risk | Implement retry | Batch processing required |
| **Alert Volume** | Direct Teams/email | Aggregated summary | Daily digest only |
| **Evidence Export** | Single JSON file | Multiple files by zone | Partitioned by region/zone |

**Design Decision:** Initial implementation targets <100 environments (sufficient for FSI SMB/mid-market). For enterprise scale (1000+ environments), add:
- Batch processing with continuation tokens
- Partitioned evidence exports
- Alert aggregation (daily digest vs per-failure)

## Architecture Patterns to Follow

Based on existing solutions analysis:

### Pattern 1: PowerShell-First Validation

**Source:** deny-event-correlation-report

**What:** Implement core validation logic in PowerShell scripts, not Power Automate expressions.

**Why:** PowerShell provides superior error handling, logging, and testability for API interactions.

**Example:**
```powershell
# GOOD: PowerShell script
function Test-EnvironmentAuditConfig {
    param([string]$EnvironmentId)
    try {
        $config = Get-AdminPowerAppEnvironment -EnvironmentName $EnvironmentId
        return [PSCustomObject]@{
            Status = if($config.AuditEnabled) { "Pass" } else { "Fail" }
            Details = $config
        }
    } catch {
        return [PSCustomObject]@{
            Status = "Error"
            Details = $_.Exception.Message
        }
    }
}

# BAD: Complex Power Automate expression
@{if(body('Get_Environment')?['auditEnabled'], 'Pass', 'Fail')}
```

### Pattern 2: Immutable Audit Log Table

**Source:** environment-lifecycle-management (ProvisioningLog)

**What:** Create organization-owned Dataverse table with read-only privileges for non-admins.

**Why:** Ensures validation history cannot be tampered with, supporting regulatory evidence requirements.

**Implementation:**
- fsi_auditvalidationhistory is org-owned
- Security roles have Create privilege only (no Update/Delete)
- All validation runs create new records (never update existing)

### Pattern 3: Connection Reference Abstraction

**Source:** scope-drift-monitor

**What:** Use connection references (fsi_cr_*) instead of hardcoded connections.

**Why:** Allows solution portability across environments. Connection references are resolved at import time.

**Implementation:**
```json
// In workflow JSON, reference connection by logical name
"connection": {
    "connectionReferenceLogicalName": "fsi_cr_http_azuread"
}
// NOT hardcoded connectionId
```

### Pattern 4: Environment Variable Configuration

**Source:** All solutions

**What:** Store tenant-specific configuration (IDs, emails, URLs) in environment variables, not hardcoded in flows.

**Why:** Enables solution import to different tenants without editing flow JSON.

**Implementation:**
- fsi_ACV_TenantId for tenant ID
- fsi_ACV_ComplianceTeamEmail for alert recipient
- fsi_ACV_TeamsChannelId for Teams channel

### Pattern 5: Adaptive Card Alerts over Webhooks

**Source:** message-center-monitor

**What:** Use Power Automate "Post adaptive card in a chat or channel" action, not incoming webhooks.

**Why:** Office 365 incoming webhooks are deprecated (March 31, 2026). Native connector is supported.

**Implementation:**
```
Action: "Post adaptive card in a chat or channel"
Team: @{variables('fsi_ACV_TeamsGroupId')}
Channel: @{variables('fsi_ACV_TeamsChannelId')}
Card: @{body('Format_Adaptive_Card')}
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Storing Secrets in Environment Variables

**What goes wrong:** Client secrets, API keys in plain-text environment variables.

**Why bad:** Security risk, exposed in solution export.

**Instead:** Use Azure Key Vault connector to retrieve secrets at runtime. Follow environment-lifecycle-management pattern.

### Anti-Pattern 2: Synchronous API Polling

**What goes wrong:** Power Automate flow waits in loop for async operation to complete.

**Why bad:** Flow timeouts, API throttling, poor resource utilization.

**Instead:** Use Dataverse trigger patterns. Update status field when operation completes, trigger new flow.

### Anti-Pattern 3: Mixing Publisher Prefixes

**What goes wrong:** Some tables use fsi_, others use custom prefix.

**Why bad:** Inconsistent naming breaks solution packaging and documentation patterns.

**Instead:** All Dataverse objects must use fsi_ publisher prefix consistently.

## Verification Points

Before marking architecture complete:

- [ ] All components follow established solution patterns (PowerShell + Power Automate + Dataverse)
- [ ] Connection references use fsi_cr_* naming convention
- [ ] Environment variables use fsi_ACV_* naming convention
- [ ] Dataverse tables use fsi_ publisher prefix
- [ ] Immutable audit log table follows ProvisioningLog pattern
- [ ] Teams notifications use native connector (not deprecated webhooks)
- [ ] Evidence export includes SHA-256 integrity hashing
- [ ] Build order accounts for component dependencies
- [ ] Integration points with existing solutions documented
- [ ] Deferred integrations (ELM, Compliance Dashboard) explicitly called out

## Sources

**HIGH Confidence (Read directly from solution code):**

- FSI-AgentGov-Solutions/scope-drift-monitor/README.md - Dataverse schema, connection references, flow patterns
- FSI-AgentGov-Solutions/scope-drift-monitor/src/ScopeDriftMonitor/environmentvariables.json - Environment variable naming
- FSI-AgentGov-Solutions/scope-drift-monitor/src/ScopeDriftMonitor/connectionreferences.json - Connection reference naming
- FSI-AgentGov-Solutions/conditional-access-automation/README.md - PowerShell script patterns, evidence export
- FSI-AgentGov-Solutions/deny-event-correlation-report/README.md - Evidence export with SHA-256 hashing
- FSI-AgentGov-Solutions/message-center-monitor/README.md - Teams notification patterns, webhook deprecation
- FSI-AgentGov-Solutions/environment-lifecycle-management/README.md - Immutable audit log pattern
- FSI-AgentGov-Solutions/environment-lifecycle-management/docs/flow-configuration.md - Power Automate flow architecture
- FSI-AgentGov/docs/controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md - Audit logging requirements
- FSI-AgentGov/docs/playbooks/control-implementations/1.7/portal-walkthrough.md - Manual audit configuration steps
- FSI-AgentGov/docs/playbooks/control-implementations/1.7/powershell-setup.md - PowerShell audit validation patterns

---

*Audit Configuration Validator Architecture Research - February 2026*
