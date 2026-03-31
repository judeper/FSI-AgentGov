# Microsoft Learn Documentation Changes

**Run Date:** 2026-03-31
**Run Time:** 2026-03-31T07:18:22.914775+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 5 |
| MEDIUM Changes | 3 |
| Redirects | 13 |
| Errors | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | power-platform-inventory | HIGH | None | Review and update |
| 2 | security-and-governance | HIGH | 1.8, 1.28, 1.1, 1.4, 1.5 | Review and update |
| 3 | microsoft-365-copilot-usage | MEDIUM | 3.8 | Review optional |
| 4 | human-in-the-loop | HIGH | 2.12, 2.17 | Review and update |
| 5 | dlp-policy-reference | HIGH | None | Review and update |
| 6 | dspm-for-ai-considerations | MEDIUM | None | Review optional |
| 7 | information-barriers-sharepoint | MEDIUM | None | Review optional |
| 8 | whats-new | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Power Platform Inventory

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -204,7 +204,9 @@ Power Platform inventory
 isn't currently available in the US Government Community Cloud (GCC, GCC-High, and DoD), 21Vianet (China), or Air Gapped environments.
 Programmatic access
-You can access Power Platform inventory data programmatically. This capability supports advanced scenarios such as automation, reporting, and integration with external tools.
+Power Platform inventory data is available programmatically, supporting advanced scenarios such as automation, reporting, and integration with external tools. For a complete list of resource types and their fields, see
+Power Platform inventory schema reference
+.
 Power Platform for Admins V2 connector
 You can query Power Platform inventory data directly from Power Automate by using the
 Power Platform for Admins V2 connector
@@ -227,14 +229,14 @@ The following are example queries you can use with any of the Azure Resource Graph interfaces. All queries use the
 PowerPlatformResources
 table, which contains your organization's inventory data.
-Query 1: Total count of all resources
+Query: Total count of all resources
 PowerPlatformResources
 | count
-Query 2: Total counts by resource type
+Query: Total counts by resource type
 PowerPlatformResources
 | summarize resourceCount = count() by type
 | order by resourceCount
-Query 3: Discover available fields for a resource type
+Query: Discover available fields for a resource type
 The inventory schema evolves over time as new data fields are added. Use this query to see all available fields for a specific resource type. This query is the recommended way to stay up to date with available data.
 // Discover all available fields for Copilot Studio agents
 PowerPlatformResources
@@ -272,23 +274,23 @@ microsoft.powerautomate/cloudflows
 Note
 This query requires at least one resource of the specified type to exist in your tenant.
-Query 4: Counts by environment (inventory distribution across environments)
+Query: Counts by environment (invento
```

---

### 2. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**What Changed:**
```diff
--- +++ @@ -114,6 +114,8 @@ Finally, Copilot Studio supports securely accessing customer data using
 Customer Lockbox
 .
+Important
+The configured Lockbox doesn't cover data sent out from Copilot Studio as part of the Agent 365 security audit logging.
 Feedback
 Was this page helpful?
 Yes

```

---

### 3. Human-in-the-Loop Workflows

**URL:** https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

**What Changed:**
```diff
--- +++ @@ -220,6 +220,33 @@ See this
 full sample
 for a complete runnable file.
+Human-in-the-Loop with Agent Orchestrations
+The
+RequestPort
+pattern described above works with custom executors and
+WorkflowBuilder
+. When using
+agent orchestrations
+(such as sequential, concurrent, or group chat workflows),
+tool approval
+is achieved through the human-in-the-loop request/response mechanism.
+Agents can use tools that require human approval before execution. When the agent attempts to call an approval-required tool, the workflow pauses and emits a
+RequestInfoEvent
+just like the
+RequestPort
+pattern, but the event payload contains a
+ToolApprovalRequestContent
+(C#) or a
+Content
+with
+type == "function_approval_request"
+(Python) instead of a custom request type.
+Tip
+For complete examples with code, see:
+Sequential orchestration with HITL
+GroupChatToolApproval sample (C#)
+Sequential tool approval sample (Python)
+Sequential request info sample (Python)
 Checkpoints and Requests
 To learn more about checkpoints, see
 Checkpoints
@@ -228,6 +255,8 @@ RequestInfoEvent
 objects, allowing you to capture and respond to them. You cannot provide responses directly during the resume operation - instead, you must listen for the re-emitted events and respond using the standard response mechanism.
 Next Steps
+Learn about sequential orchestration with HITL
+.
 Learn how to manage state
 in workflows.
 Learn how to create checkpoints and resume from them

```

---

### 4. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -912,8 +912,9 @@ Yes
 - Distribution groups
 - Security groups
-- Non email enabled security groups
+- Non-email enabled security groups
 - Microsoft 365 groups (Group members only, not the group as an entity)
+- Dynamic groups
 data-in-use
 data-in-motion
 -
@@ -1142,9 +1143,8 @@ . A policy is enforced on an endpoint only when
 both
 the user and the device are included in the policy scope. If a user is in scope but the device is not, the policy isnât applied. Similarly, if a device is in scope but the user is not, the policy isnât applied.
-Note
 Use 101.25072 or higher build for this feature support on macOS.
-Configure scope for common outcomes
+Device scoping does not support Microsoft Entra registered.
 Here's how to configure the scope of a DLP policy for different outcomes.
 If you want to target the policy to...
 Set user scope to...
@@ -1297,9 +1297,9 @@ For endpoints
 When an item matches multiple DLP rules, DLP goes uses through a complex algorithm to decide which actions to apply. Endpoint DLP applies the aggregate or sum of most restrictive actions. DLP uses these factors when making the calculation.
 Policy priority order
-When an item matches multiple policies and those policies have identical actions, the actions from the highest priority policy is applied.
+When an item matches multiple policies and those policies have identical actions, the actions from the highest priority policy are applied.
 Rule priority order
-When an item matches multiple rules in a policy and those rules have identical actions, the actions from the highest priority rule is applied.
+When an item matches multiple rules in a policy and those rules have identical actions, the actions from the highest priority rule are applied.
 Mode of the policy
 When an item matches multiple policies and those policies have identical actions, the actions from all policies that are in
 Turn it on
@@ -1308,7 +1308,40 @@ and
 Run the policy in simulation mode
 state.
-action
+Run
```

---

### 5. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -48,6 +48,10 @@ :
 Authoring custom data quality rules using SQL expression
 language is now generally available. Users can create custom rules using both Azure Data Factory expression and SQL expression languages.
+In preview
+:
+Configurable Data Quality thresholds
+allows users to define minimum acceptable quality scores at the data quality rule and data asset levels to aligns quality evaluation with business criticality.
 Data Loss Prevention
 Preview
 : DLP supports adaptive scopes for scoping SharePoint policies.
@@ -67,7 +71,27 @@ : New support for the Data Security Posture Agent in Microsoft Purview. The
 Data Security Posture agent (preview)
 in Data Security Investigations helps your organization proactively surface credentials buried in data across your organization at scale.
+Updated
+: New guidance for
+how categorization processes data
+in Data Security Investigations. Categorization uses relevance scoring to prioritize the most relevant content for each selected category. Updated documentation includes considerations for results, content volume effects, and recommendations for using examination tools for comprehensive analysis.
+New
+: Data Security Investigations now supports
+soft purge
+for Exchange mailbox items. Soft purge moves items to the recoverable items folder, preserving the ability to restore items based on retention settings. Updated documentation includes guidance for choosing between soft purge and hard purge methods.
+New
+:
+Audit search
+in Data Security Investigations is now generally available. Use audit search to identify and collect content based on user activities recorded in the Microsoft Purview unified audit log, such as accessing, copying, or downloading files, and pull the associated content into your investigation.
+Updated
+: Data Security Investigations searches now respect
+compliance boundaries
+configured with search permissions filters. Investigators whose accounts are scoped by a compliance boundary only
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Copilot Usage Reports
**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage
**Classification:** MEDIUM (General content update)

---

### 2. DSPM Considerations
**URL:** https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations
**Classification:** MEDIUM (General content update)

---

### 3. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-sharepoint
**Classification:** MEDIUM (General content update)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage | https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health | https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide |
| https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai | https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2 |
| https://learn.microsoft.com/en-us/azure/devops/test/overview | https://learn.microsoft.com/en-us/azure/devops/test/overview?view=azure-devops |
| https://learn.microsoft.com/en-us/graph/api/resources/application | https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0 |
| https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview | https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview?view=graph-rest-1.0 |
| https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy | https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpcompliancepolicy?view=exchange-ps |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview | https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview?view=o365-worldwide |

---

## Errors

- **Enhanced Admin Controls for Agent Security [Preview]** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/enhanced-admin-controls-agent-security
- **Agentic Center of Enablement [Preview]** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/automate-governance-agentic-center-enablement
- **Agent Suggestions from M365 Copilot [Preview]** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/get-agent-suggestions-based-work

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*