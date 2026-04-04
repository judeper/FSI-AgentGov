# Microsoft Learn Documentation Changes

**Run Date:** 2026-04-04
**Run Time:** 2026-04-04T07:03:40.999225+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 20 |
| MEDIUM Changes | 12 |
| Redirects | 26 |
| Errors | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | managed-environment-overview | MEDIUM | 2.1, 2.2, 2.15, 1.8, 3.7 | Review optional |
| 2 | default-environment-routing | MEDIUM | 2.15 | Review optional |
| 3 | ...en-us/connectors/connector-reference/ | MEDIUM | 1.4 | Review optional |
| 4 | power-platform-inventory | HIGH | None | Review and update |
| 5 | activity-logs-power-platform-admin | CRITICAL | None | Monitor |
| 6 | capacity-storage | HIGH | 3.5 | Review and update |
| 7 | ...ilot-security-enhanced-admin-controls | MEDIUM | 2.8, 2.3, 1.18 | Review optional |
| 8 | security-and-governance | HIGH | 1.8, 1.28, 1.1, 1.4, 1.5 | Review and update |
| 9 | advanced-connectors | MEDIUM | None | Review optional |
| 10 | knowledge-copilot-studio | HIGH | 2.16, 4.8 | Review and update |
| 11 | nlu-gpt-overview | MEDIUM | 2.12 | Review optional |
| 12 | planned-features | MEDIUM | 2.25 | Review optional |
| 13 | ...gent-external-data-custom-mcp-servers | HIGH | 2.17, 1.4, 1.5, 3.8 | Review and update |
| 14 | microsoft-365-copilot-usage | HIGH | 3.8 | Review and update |
| 15 | human-in-the-loop | HIGH | 2.12, 2.17 | Review and update |
| 16 | dlp-policy-reference | HIGH | None | Review and update |
| 17 | sensitivity-labels | HIGH | 1.26, 1.3, 1.5, 4.9 | Review and update |
| 18 | sensitivity-labels-teams-groups-sites | HIGH | 1.3 | Review and update |
| 19 | dspm-for-ai-considerations | MEDIUM | None | Review optional |
| 20 | ...o-conditional-access-session-lifetime | CRITICAL | 1.23 | Monitor |
| 21 | overview-authentication | HIGH | 1.11 | Review and update |
| 22 | access-reviews-overview | HIGH | 1.3 | Review and update |
| 23 | create-access-review | HIGH | 2.8, 4.2 | Review and update |
| 24 | ...n.microsoft.com/en-us/entra/agent-id/ | HIGH | 1.11, 1.2, 1.18 | Review and update |
| 25 | ...-entra-agent-identities-for-ai-agents | HIGH | 1.11, 1.18 | Review and update |
| 26 | advanced-management | HIGH | 1.3, 4.2, 4.5, 4.6, 4.1 | Review and update |
| 27 | data-access-governance-reports | HIGH | 4.4, 4.2, 4.5, 4.6, 4.1 | Review and update |
| 28 | information-barriers-sharepoint | MEDIUM | None | Review optional |
| 29 | message-center | HIGH | 2.10 | Review and update |
| 30 | application | MEDIUM | 1.2 | Review optional |
| 31 | whats-new | HIGH | None | Review and update |
| 32 | microsoft-purview-service-description | HIGH | None | Review and update |

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

### 2. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

**What Changed:**
```diff
--- +++ @@ -242,13 +242,7 @@ Use
 Search
 to search by environment name and environment type.
-Dataverse page in Licenses (preview)
-Important
-This is a preview feature.
-Don't use preview features in production environments. Preview features might have restricted functionality. They're subject to
-supplemental terms of use
-. Microsoft makes preview features available before an official release so that customers can get early access and provide feedback.
-This feature is being gradually rolled out across regions and might not be available in your region yet.
+Dataverse page in Licenses
 Track tenant usage
 You can track and manage Dataverse capacity in the
 Licenses
@@ -268,6 +262,39 @@ In the
 Usage per storage type
 tile, you can view the consumption of your database, log, and file storage. This section displays your prepaid entitled capacity along with the corresponding usage. Additionally, it indicates if any part of your Dataverse usage is billed under a pay-as-you-go plan.
+The tile provides the following details for database, file, and log storage:
+Total prepaid entitlement
+: Database and file capacity can be pooled across
+Dataverse
+and
+Operations
+workloads respectively. Log entitlement is provided separately for
+Dataverse only.
+Total consumption
+: Combined usage from both Dataverse and finance and operations environments.
+Reserved capacity
+: Capacity reserved for specific environments. Currently applicable to Dataverse only.
+Pay-as-you-go usage
+: Any consumption that exceeds prepaid entitlement and is billed under a pay-as-you-go plan.
+Dataverse - Database capacity
+: Tracks structured data stored directly in Dataverse, including table rows, metadata, and relational data created by Power Apps, Power Automate, Dynamics 365 customer engagement apps (Dynamics 365 Sales, Dynamics 365 Service, Dynamics 365 Marketing), and custom model-driven apps.
+Operations - Database capacity
+: Tracks structured data stored in finance and operations environmen
```

---

### 3. Security and Governance

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

### 4. Knowledge Sources

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`

**What Changed:**
```diff
--- +++ @@ -27,18 +27,18 @@ Knowledge sources summary
 Feedback
 Summarize this article for me
-In Copilot Studio, knowledge sources work together with generative answers. When knowledge sources are added, agents can use enterprise data from Power Platform, Dynamics 365 data, websites, and external systems. Knowledge sources allow your agents to provide relevant information and insights for your customers.
-Published agents that contain knowledge use the configured knowledge sources to ground the published agent. Knowledge can be incorporated at the agent level, in the
+In Copilot Studio, knowledge sources work together with generative answers. When you add knowledge sources, agents can use enterprise data from Power Platform, Dynamics 365 data, websites, and external systems. Knowledge sources allow your agents to provide relevant information and insights for your customers.
+Published agents that contain knowledge use the configured knowledge sources to ground the published agent. You can incorporate knowledge at the agent level, in the
 Knowledge
 page, or at the topic level, with a
 generative answers node
 in an agent topic.
-Knowledge sources can be incorporated into agents during their initial creation, added after the agent is created, or added to a generative answers topic node.
+You can incorporate knowledge sources into agents during their initial creation, add them after the agent is created, or add them to a generative answers topic node.
 Add and manage knowledge for generative answers
-Generative answers allow your agent to find and present information from multiple sources, internal or external, without having to create specific topics. Generative answers can be used as primary information sources or as a fallback source when authored topics can't answer a user's query. As a result, you can quickly create and deploy a functional agent. Makers don't need to manually author multiple topics, which might not address all customer questions.
+Generative an
```

---

### 5. Custom MCP Servers [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/connect-agent-external-data-custom-mcp-servers
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -24,52 +24,128 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Connect any agent to any external data with custom MCP servers
+What's new and planned for Microsoft Copilot Studio
 Feedback
 Summarize this article for me
-Important
-Some of the functionality described in this release plan has not been released.
-Delivery timelines may change and projected functionality may not be released (see
+This topic lists features that are planned to release from April 2026 through September 2026. Because this topic lists features that may not have released yet,
+delivery timelines may change and projected functionality may not be released
+. For more information, go to
 Microsoft policy
-). Learn more:
-What's new and planned
+.
+For a list of the previous wave's release plans, go to
+2025 release wave 2 plan
+.
+In the
+General availability
+column, the feature will be delivered within the month listed. The delivery date can be any day within that month. Released features show the full date, including the date of release.
+This check mark (
+) shows which features have been released for public preview and general availability.
+Copilot and AI innovation
+Use industry leading generative AI capabilities in Microsoft Copilot Studio to do the work so you and your team don't have to.
+Feature
 Enabled for
 Public preview
 General availability
+Automate web and desktop apps with computer use
+Admins, makers, marketers, or analysts, automatically
+May 27, 2025
+May 2026
+Configure triggers with end-user credentials
+Admins, makers, marketers, or analysts, automatically
+Apr 2026
+Jun 2026
+Use code interpreter on SharePoint sources in agent conversations
 Admins, makers, marketers, or analysts, automatically
 Mar 2026
+May 2026
+Define custom metrics for analytics
+Admins, makers, marketers, or analysts, automatically
 Apr 2026
-Business value
-Custom Model Context Protocol (MCP) servers let you connect Microsoft Copilot, VS Code, Git,
```

---

### 6. Copilot Usage Reports

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -27,30 +27,44 @@ Microsoft 365 Copilot usage report - Microsoft 365 admin center
 Feedback
 Summarize this article for me
-The Microsoft 365 Usage report dashboard shows the activity overview across the Microsoft 365 apps in your organization. The dashboard lets you drill down into individual product-level reports to gain more granular insights about the activities within each app. For general information about reports and to see a list of all available reports, see
+The Microsoft 365 Copilot usage report provides a summary of how users adopt, retain, and engage with Microsoft 365 Copilot and its associated enabled apps, including agent usage. For Copilot activity on a given day, the report typically becomes available within 72 hours of the end of that day (in UTC).
+For general information about Microsoft 365 Usage reports and to see a list of all available reports, see
 Microsoft 365 admin center usage reports overview
 .
-In the Microsoft 365 Copilot usage report, which is in continuous enhancement, you can view a summary of how users' adoption, retention, and engagement are with Microsoft 365 Copilot and its associated enabled apps, including agent usage. For Copilot activity on a given day, the report becomes available typically within 72 hours of the end of that day (in UTC).
 View the Microsoft 365 Copilot usage report
 For information about the roles needed to view usage reports, see
 Microsoft 365 admin center usage reports overview
 .
-In the
+Go to the
 Microsoft 365 admin center
-, go toâ¯
+.
+In the navigation menu, selectâ¯
 Reports
-â¯>â¯
+. If you don't see
+Reports
+, select
+Show all
+, and then select
+Reports
+.
+Select
 Usage
 .
-Select the
+On the
+Usage
+page, under
+Reports
+, select
 Microsoft 365 Copilot
-page.
-Select the
+, and then select
+Copilot
+.
+On the report page, select the
 Usage
 tab to view adoption and usage metrics.
 Interpret the Microsoft 365 Copilot usage report
 Use the Microsoft 365 Copilot usage report t
```

---

### 7. Human-in-the-Loop Workflows

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

### 8. DLP Policy Reference

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

### 9. Sensitivity Labels

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

### 10. Sensitivity Labels for Sites

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

### 11. Authentication Methods

**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/overview-authentication
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**What Changed:**
```diff
--- +++ @@ -69,7 +69,7 @@ Software OATH tokens
 No
 MFA and SSPR
-External authentication methods (preview)
+External MFA
 No
 MFA
 Temporary Access Pass (TAP)

```

---

### 12. Access Reviews

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**What Changed:**
```diff
--- +++ @@ -113,10 +113,6 @@ recommendations, or an
 access review of multiple resources together (preview)
 , requires a Microsoft Entra ID Governance license.
-Access Review Agent (Preview)
-The Access Review Agent works for your reviewers by automatically gathering insights and generating recommendations. It then guides reviewers through the review process in Microsoft Teams with natural language, with simple summaries and proposed decisions, so they can make the final call with confidence and clarity. For more information, see
-Access Review Agent
-.
 Next steps
 Prepare for an access review of users' access to an application
 Create an access review of groups or applications

```

---

### 13. Create Access Review

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/create-access-review
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**What Changed:**
```diff
--- +++ @@ -230,12 +230,6 @@ : Select this checkbox to have Microsoft Entra ID send reminders of access reviews in progress to all reviewers. Reviewers receive the reminders halfway through the review, no matter if they've finished their review or not.
 Additional content for reviewer email
 : The content of the email sent to reviewers is autogenerated based on the review details, such as review name, resource name, and due date. If you need to communicate more information, you can specify details such as instructions or contact information in the box. The information that you enter is included in the invitation, and reminder emails are sent to assigned reviewers. The section highlighted in the following image shows where this information appears.
-Access Review Agent (Preview)
-: Select this checkbox to allow reviewers to complete the access review in Microsoft Teams with natural language, insights, and recommendations.
-Note
-This setting is only available for review configurations currently supported by the Access Review Agent and additional setup steps are required. For more information, see:
-Access Review Agent with Microsoft Security Copilot
-.
 Select
 Next: Review + Create
 .
@@ -246,12 +240,6 @@ .
 Create a multi-stage access review
 A multi-stage review allows the administrator to define two or three sets of reviewers to complete a review one after another. In a single-stage review, all reviewers make a decision within the same period and the last reviewer to make a decision, has their decision applied. In a multi-stage review, two or three independent sets of reviewers each make a decision within their own stage. The stages are sequential, and the next stage doesn't happen until a decision is recorded in the previous stage. Multi-stage reviews can be used to reduce the burden on later-stage reviewers, allow for escalation of reviewers, or have independent groups of reviewers agree on decisions.
-Note
-Data of users included in multi-stage access reviews 
```

---

### 14. Agent ID Overview

**URL:** https://learn.microsoft.com/en-us/entra/agent-id/
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.2: Control 1.2: Agent Registry and Integrated Apps Management
  - File: `controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**What Changed:**
```diff
--- +++ @@ -1,46 +1,32 @@-Microsoft Entra Agent ID documentation
-Secure and govern AI agents at enterprise scale with Microsoft Entra Agent ID and the Microsoft agent identity platform. Create agent identities, apply Zero Trust controls, and manage agent access to your organization's resources.
-Overview
-What is Microsoft Entra Agent ID?
-Overview
-Microsoft agent identity platform for developers
-Overview
-What is an agent identity?
-How-To Guide
-Create an agent identity
 Microsoft Entra Agent ID
-The comprehensive solution for protecting and governing AI agents in enterprise environments. Includes advanced security controls, and governance policies for agent identities and access management.
+Protect agent identities and secure their access to applications and resources. Part of Microsoft Agent 365, Microsoft Entra Agent ID and the Microsoft agent identity platform provide the foundation for secure and compliant AI agent deployments in the enterprise.
+Learn about Microsoft Entra Agent ID
+Get started with Microsoft Entra Agent ID
+Learn about how Microsoft Entra Agent ID and Agent 365 work together so you can observe, govern, and secure agents across your organization.
 Manage agents
-What is Microsoft Entra Agent ID?
-Owners, sponsors, and managers
-Manage agents in the end user experience
-Agent governance and lifecycles
-Identity Governance for agents
-Agent identity lifecycle management
+Learn how to manage all aspects of agents in your ecosystem, such as assigning sponsors and requesting access packages.
+How it works
+Govern agent lifecycles
+Ensure the lifecycle of your agents are governed with access reviews, entitlement management, and sponsor accountability.
+Get started
 Protect agent access to resources
-Conditional Access for agents
-Identity Protection for agents
-Network controls for agents
-Microsoft agent identity platform for developers
-The platform that enables you to create and manage agent identities.
-Learn about key concepts
-What is an
```

---

### 15. Agent Identities for AI Agents

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

### 16. Advanced Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Section:** SharePoint Administration
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -194,24 +194,16 @@ Restrict site creation by apps
 feature. This ensures that only trusted apps have the capability to create sites, enhancing security and governance.
 Licensing
-To use SharePoint Advanced Management (SAM), your organization must have the appropriate licensing in place. Learn about the main options for accessing SAM features
-here
-.
-SharePoint Advanced Management features in Microsoft 365 Copilot licenses
-Learn about SharePoint Advanced Management features included in Microsoft 365 Copilot licenses
-here
-.
-Which Microsoft 365 Copilot SKUs include SharePoint Advanced Management?
-Learn more about what Microsoft 365 Copilot SKUs include SharePoint Advanced Management features
-here
+To use SharePoint Advanced Management (SAM), your organization must have the appropriate licensing in place. See
+SharePoint Advanced Management licensing and features
 .
 How does SAM support Microsoft 365 Copilot deployment?
 Whether preparing for
 Copilot deployment
 or managing content post-implementation, SharePoint Advanced Management offers capabilities to help you govern your SharePoint and OneDrive content effectively.
-We recommend utilizing SharePoint Advanced Management features along with our
-best practices for Microsoft 365 Copilot
-to reduce the risk of oversharing, control content sprawl, and manage the content lifecycle.
+ALso see
+Get ready for Microsoft 365 Copilot with SharePoint Advanced Management
+.
 Related articles
 Microsoft 365 Government - how to buy
 Get started with Microsoft 365 Copilot

```

---

### 17. Data Access Governance Reports

**URL:** https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -134,8 +134,8 @@ What is the 'Everyone except external users' (EEEU) report?
 EEEU is a built-in SharePoint group that automatically includes all internal users but excludes any external guests. The 'Everyone except external users' (EEEU) report is one of the two activity reports that helps you identify sites where content has been shared with your entire organization in the past 28 days. You can run the
 site permissions for your organization report
-first to understand your organization's current EEEU sharing status, then use this activity report to monitor ongoing EEEU sharing activities. Learn how to create and use the Everyone except external users sharing activity report
-here
+first to understand your organization's current EEEU sharing status, then use this activity report to monitor ongoing EEEU sharing activities. See
+Monitor 'Everyone except external users' (EEEU) sharing with the EEEU activity report
 .
 Limitations or known issues
 Reports may not work if you have nonpseudonymized report data selected for your organization. To change this setting, you must be a Global Administrator. Go to the

```

---

### 18. Message Center

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

### 19. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -42,12 +42,29 @@ for data governance solutions.
 Roadmap
 for data security and risk and compliance solutions.
+April 2026
+Data Governance
+General availability (GA)
+: Now rolling out, the
+advanced resource sets
+capability is available to all customers. Pricing for advanced resource sets is consistent with existing rates for
+classic Microsoft Purview data governance
+.
+Sensitivity labels
+General availability (GA)
+:
+Auto-labeling policies
+introduce a new flow where you must decide whether to automatically apply a sensitivity label, or remove a label when the configured conditions apply for files in SharePoint and OneDrive. When you chose to automatically apply a sensitivity label, you can now optionally choose to always overriding an existing label that has a lower priority label, even if it was manually applied. This option was previously available for emails only and now extends to files in SharePoint and OneDrive.
 March 2026
 Data Governance
 General availability (GA)
 :
 Authoring custom data quality rules using SQL expression
 language is now generally available. Users can create custom rules using both Azure Data Factory expression and SQL expression languages.
+In preview
+:
+Configurable Data Quality thresholds
+allows users to define minimum acceptable quality scores at the data quality rule and data asset levels to align quality evaluation with business criticality.
 Data Loss Prevention
 Preview
 : DLP supports adaptive scopes for scoping SharePoint policies.
@@ -67,13 +84,48 @@ : New support for the Data Security Posture Agent in Microsoft Purview. The
 Data Security Posture agent (preview)
 in Data Security Investigations helps your organization proactively surface credentials buried in data across your organization at scale.
+Updated
+: New guidance for
+how categorization processes data
+in Data Security Investigations. Categorization uses relevance scoring to prioritize the most relevant content for each selected category. Update
```

---

### 20. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -607,6 +607,9 @@ Activity Explorer provides a single pane of glass for admins to get visibility about activities that are related to sensitive information that's being used by end users. These data include label activities, data loss prevention (DLP) logs, auto-labeling, Endpoint DLP and more.
 Content Explorer provides admins the ability to index the sensitive documents that are stored within supported Microsoft 365 workloads and identify the sensitive information that they're storing. In addition, Content Explorer helps identify documents that are classified with sensitivity and retention labels.
 Information protection and compliance admins can access the service to get access to these logs and indexed data to understand where sensitive data are stored, and which activities are related to this data and performed by end users.
+Microsoft Purview Posture Reports provide pre-built reports that surface key insights about your organization's information protection and data loss prevention performance, based on a rolling 30-day data window. Information Protection reports cover sensitivity label distribution and adoption, auto-labeling policy coverage, and sensitivity label activity. Data Loss Prevention reports highlight the most triggered DLP rules, highest-volume policies, and top policy violators. Posture Reports are accessible in the
+Microsoft Purview portal
+under Information Protection > Reports, Data Loss Prevention > Reports, or DSPM > Reports.
 While Data classification analytics (Content & Activity Explorer interfaces) requires E5/A5/G5 licensing, the underlying data aggregation continues for E3/A3/G3 tenants to support analytics and compliance scenarios.
 Feature availability
 Feature
@@ -656,6 +659,8 @@ or
 Apply a sensitivity label to content automatically
 .
+Licensing note
+: The RMS Connector is used to integrate onâpremises workloads with Microsoft Purview Information Protection. Licensing requirements depend on the Information Protection
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

### 3. Connector Reference
**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Classification:** MEDIUM (General content update)

---

### 4. Admin Activity Logging
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/activity-logging-auditing/activity-logs-power-platform-admin
**Classification:** CRITICAL (Deprecation notice)

---

### 5. Enhanced Admin Controls [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls
**Classification:** MEDIUM (General content update)

---

### 6. Connectors
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors
**Classification:** MEDIUM (General content update)

---

### 7. Quickstart: Create and deploy an agent
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-gpt-overview
**Classification:** MEDIUM (General content update)

---

### 8. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)

---

### 9. DSPM Considerations
**URL:** https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations
**Classification:** MEDIUM (General content update)

---

### 10. Session Controls
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime
**Classification:** CRITICAL (Deprecation notice)

---

### 11. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-sharepoint
**Classification:** MEDIUM (General content update)

---

### 12. Application Resources
**URL:** https://learn.microsoft.com/en-us/graph/api/resources/application
**Classification:** MEDIUM (General content update)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/connect-agent-external-data-custom-mcp-servers | https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview | https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy | https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-enable-users | https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-enable-users |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage | https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/copilot-control-system/overview | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/overview |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/copilot-control-system/security-governance | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/security-governance |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/copilot-control-system/management-controls | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/management-controls |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/agent-essentials-overview | https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-essentials-overview |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/agent-prerequisites | https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-prerequisites |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-visual-map | https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-visual-map |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-checklist | https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-checklist |
| https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-blueprint | https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-blueprint |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents | https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id |
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