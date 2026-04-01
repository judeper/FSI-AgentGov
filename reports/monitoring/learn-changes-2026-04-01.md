# Microsoft Learn Documentation Changes

**Run Date:** 2026-04-01
**Run Time:** 2026-04-01T07:23:51.287096+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 10 |
| MEDIUM Changes | 6 |
| Redirects | 14 |
| Errors | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | managed-environment-overview | MEDIUM | 2.1, 2.2, 2.15, 1.8, 3.7 | Review optional |
| 2 | default-environment-routing | MEDIUM | 2.15 | Review optional |
| 3 | power-platform-inventory | HIGH | None | Review and update |
| 4 | security-and-governance | HIGH | 1.8, 1.28, 1.1, 1.4, 1.5 | Review and update |
| 5 | advanced-connectors | MEDIUM | None | Review optional |
| 6 | microsoft-365-copilot-usage | HIGH | 3.8 | Review and update |
| 7 | human-in-the-loop | HIGH | 2.12, 2.17 | Review and update |
| 8 | dlp-policy-reference | HIGH | None | Review and update |
| 9 | sensitivity-labels | HIGH | 1.26, 1.3, 1.5, 4.9 | Review and update |
| 10 | sensitivity-labels-teams-groups-sites | HIGH | 1.3 | Review and update |
| 11 | dspm-for-ai-considerations | MEDIUM | None | Review optional |
| 12 | ...-entra-agent-identities-for-ai-agents | HIGH | 1.11, 1.18 | Review and update |
| 13 | information-barriers-sharepoint | MEDIUM | None | Review optional |
| 14 | message-center | HIGH | 2.10 | Review and update |
| 15 | application | MEDIUM | 1.2 | Review optional |
| 16 | whats-new | HIGH | None | Review and update |

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

### 3. Copilot Usage Reports

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -210,7 +210,7 @@ Welcome to Copilot in OneNote - Microsoft Support
 .
 Loop
-All Copilot in Loop features are automatically included in the Microsoft 365 Copilot usage report. Usage of any Copilot in Loop feature counts towards the Active users metric and is indicated in the per-user Last activity date (UTC).
+All Copilot in Loop features are automatically included in the Microsoft 365 Copilot usage report. Usage of any Copilot in Loop feature counts towards the Active users metric and is indicated in the per-user Last activity date (UTC). User views of Loop documents generated by the Facilitator feature in Teams meetings are included in active usage for the Loop app and all up Microsoft 365 Copilot usage, effective December 11, 2025.
 To learn more about Copilot in Loop features, refer to
 Get started with Microsoft 365 Copilot in Loop - Microsoft Support
 .
@@ -291,7 +291,9 @@ Display user-specific data
 By default, usernames and display names in Copilot Search usage reports are anonymous. Global administrators can update the settings to reveal usernames and display names.
 Important
-Microsoft recommends that you use roles with the fewest permissions. This helps improve security for your organization. Global Administrator is a highly privileged role that should be limited to emergency scenarios when you can't use an existing role.
+Microsoft recommends that you use roles with the fewest permissions. Using roles with the fewest permissions helps improve security for your organization. Global Administrator is a highly privileged role that should be limited to emergency scenarios when you can't use an existing role. For more information, see
+About administrator roles in the Microsoft 365 admin center
+.
 In the admin center, go to
 Settings
 >

```

---

### 4. Human-in-the-Loop Workflows

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

### 5. DLP Policy Reference

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

### 6. Sensitivity Labels

**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 4.9: Control 4.9: Embedded File Content Governance
  - File: `controls/pillar-4-sharepoint/4.9-embedded-file-content-governance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.26/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.8/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -60,7 +60,7 @@ Identify content for eDiscovery cases
 . The condition builder to create search queries in eDiscovery supports sensitivity labels that are applied to content. For example, as part of your eDiscovery case, restrict content to files and emails that have a "Highly Confidential" sensitivity label. Or conversely, exclude content to files and emails that have a "Public" sensitivity label.
 Protect containers
-that include Teams, Microsoft 365 Groups, SharePoint sites, and Loop workspaces. For example, set privacy settings, external user access and external sharing, access from unmanaged devices, and control how channels can be shared with other teams.
+that include Teams, Microsoft 365 Groups, SharePoint sites, Viva Engage communities, and Loop workspaces. For example, set privacy settings, external user access and external sharing, access from unmanaged devices, and control how channels can be shared with other teams.
 Protect meetings and chat
 by labeling (and optionally, encrypting) meeting invites and any responses, and enforce Teams-specific options for the meeting and chat.
 Extend sensitivity labels to Power BI
@@ -124,9 +124,9 @@ Watermarks are limited to 255 characters. Headers and footers are limited to 1024 characters, except in Excel. Excel has a total limit of 255 characters for headers and footers but this limit includes characters that aren't visible, such as formatting codes. If that limit is reached, the string you enter isn't displayed in Excel.
 Protect content in containers such as sites and groups
 when you enable the capability to
-use sensitivity labels with Microsoft Teams, Microsoft 365 groups, and SharePoint sites
-.
-You can't configure protection settings for groups and sites until you enable this capability. This label configuration doesn't result in documents or emails being automatically labeled but instead, the label settings protect content by controlling access to the container where content can be stored. These
```

---

### 7. Sensitivity Labels for Sites

**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels-teams-groups-sites
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**What Changed:**
```diff
--- +++ @@ -24,16 +24,14 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Use sensitivity labels to protect content in Microsoft Teams, Microsoft 365 groups, and SharePoint sites
+Use sensitivity labels to protect collaborative workspaces (groups and sites)
 Feedback
 Summarize this article for me
 Microsoft Purview service description
 In addition to using
 sensitivity labels
-to protect documents and emails, you can also use sensitivity labels to protect content in the following containers: Microsoft Teams sites, Microsoft 365 groups (
-formerly Office 365 groups
-), and SharePoint sites. For this container-level protection, use the following label settings:
-Privacy (public or private) of teams sites and Microsoft 365 groups
+to protect items such as documents and emails, you can also use sensitivity labels to protect content in the following containers: Microsoft Teams sites, Microsoft 365 groups, SharePoint sites, Viva Engage communities, and Loop workspaces. To protect these collaborative workspaces, use the following label settings:
+Privacy (public or private)
 External user access
 External sharing from SharePoint sites
 Access from unmanaged devices
@@ -45,17 +43,20 @@ Default label for channel meetings
 Important
 The settings for unmanaged devices and authentication contexts work in conjunction with Microsoft Entra Conditional Access. You must configure this dependent feature if you want to use a sensitivity label for these settings. Additional information is included in the instructions that follow.
-When you apply this sensitivity label to a supported container, the label automatically applies the sensitivity category and configured protection settings to the site or group.
+Support for container-level protection by using sensitivity labels is growing all the time. Refer to the documentation for each collaborative workspace and the
+Microsoft public roadmap
+to learn about new capabilities.
+When you apply a sensitiv
```

---

### 8. Agent Identities for AI Agents

**URL:** https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**What Changed:**
```diff
--- +++ @@ -27,56 +27,27 @@ What is Microsoft Entra Agent ID?
 Feedback
 Summarize this article for me
-As assistive and autonomous agents become more prevalent in organizations, new security, governance, and compliance challenges must be addressed. Microsoft Entra Agent ID extends the comprehensive security capabilities of Microsoft Entra to agents, enabling organizations to build, discover, govern, and protect agent identities.
-Security for AI
-spans multiple Microsoft Entra features and is integrated through Microsoft Entra Agent ID and the
-Microsoft agent identity platform for developers
-.
-This article explains how Microsoft Entra Agent ID extends security capabilities to agents through conditional access policies, identity protection, identity governance, network-level controls, and the agent identity platform.
+Microsoft Entra Agent ID is an identity and security framework that extends Microsoft Entra capabilities to AI agents. As organizations deploy assistive, autonomous, and user-like agents, they need purpose-built identity constructs to authenticate, authorize, govern, and protect these nonhuman identities. Microsoft Entra Agent ID addresses these needs by providing a unified platform for managing agent identities at enterprise scale.
 Important
 Microsoft Entra Agent ID
 is currently in PREVIEW.
 This information relates to a prerelease product that may be substantially modified before it's released. Microsoft makes no warranties, expressed or implied, with respect to the information provided here.
-Protect access to resources
-Microsoft Entra Agent ID provides many of the same protections for agents that Microsoft Entra provides for users. These protections include the policies and controls you use to make sure your AI agents can only access what they need, for the right amount of time, and only if they're not at risk.
+Microsoft Entra Agent ID brings together identity management, access protection, governance, and compliance for AI agents.
+Agent i
```

---

### 9. Message Center

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center
**Section:** Microsoft 365 Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**What Changed:**
```diff
--- +++ @@ -336,7 +336,9 @@ Message ID
 Microsoft tracks our Message center posts by message ID. You can refer to this ID if you want to give feedback or if you call Support about a particular message.
 Important
-Microsoft recommends that you use roles with the fewest permissions. This helps improve security for your organization. Global Administrator is a highly privileged role that should be limited to emergency scenarios when you can't use an existing role.
+Microsoft recommends that you use roles with the fewest permissions. Using roles with the fewest permissions helps improve security for your organization. Global Administrator is a highly privileged role that should be limited to emergency scenarios when you can't use an existing role. For more information, see
+About administrator roles in the Microsoft 365 admin center
+.
 Admin roles that don't have access to the Message center
 Compliance administrator
 Conditional access administrator

```

---

### 10. Purview What's New

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

### 1. Managed Environments
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview
**Classification:** MEDIUM (General content update)

---

### 2. Environment Routing
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing
**Classification:** MEDIUM (General content update)

---

### 3. Connectors
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors
**Classification:** MEDIUM (General content update)

---

### 4. DSPM Considerations
**URL:** https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations
**Classification:** MEDIUM (General content update)

---

### 5. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-sharepoint
**Classification:** MEDIUM (General content update)

---

### 6. Application Resources
**URL:** https://learn.microsoft.com/en-us/graph/api/resources/application
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
| https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents | https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/what-is-microsoft-entra-agent-id |
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