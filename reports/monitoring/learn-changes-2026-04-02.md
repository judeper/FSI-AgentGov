# Microsoft Learn Documentation Changes

**Run Date:** 2026-04-02
**Run Time:** 2026-04-02T07:15:45.629203+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 15 |
| MEDIUM Changes | 8 |
| Redirects | 14 |
| Errors | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | managed-environment-overview | MEDIUM | 2.1, 2.2, 2.15, 1.8, 3.7 | Review optional |
| 2 | default-environment-routing | MEDIUM | 2.15 | Review optional |
| 3 | ...en-us/connectors/connector-reference/ | MEDIUM | 1.4 | Review optional |
| 4 | power-platform-inventory | HIGH | None | Review and update |
| 5 | capacity-storage | HIGH | 3.5 | Review and update |
| 6 | security-and-governance | HIGH | 1.8, 1.28, 1.1, 1.4, 1.5 | Review and update |
| 7 | advanced-connectors | MEDIUM | None | Review optional |
| 8 | microsoft-365-copilot-usage | HIGH | 3.8 | Review and update |
| 9 | human-in-the-loop | HIGH | 2.12, 2.17 | Review and update |
| 10 | dlp-policy-reference | HIGH | None | Review and update |
| 11 | sensitivity-labels | HIGH | 1.26, 1.3, 1.5, 4.9 | Review and update |
| 12 | sensitivity-labels-teams-groups-sites | HIGH | 1.3 | Review and update |
| 13 | dspm-for-ai-considerations | MEDIUM | None | Review optional |
| 14 | ...o-conditional-access-session-lifetime | CRITICAL | 1.23 | Monitor |
| 15 | overview-authentication | HIGH | 1.11 | Review and update |
| 16 | access-reviews-overview | HIGH | 1.3 | Review and update |
| 17 | create-access-review | HIGH | 2.8, 4.2 | Review and update |
| 18 | ...-entra-agent-identities-for-ai-agents | HIGH | 1.11, 1.18 | Review and update |
| 19 | information-barriers-sharepoint | MEDIUM | None | Review optional |
| 20 | message-center | HIGH | 2.10 | Review and update |
| 21 | application | MEDIUM | 1.2 | Review optional |
| 22 | whats-new | HIGH | None | Review and update |
| 23 | microsoft-purview-service-description | HIGH | None | Review and update |

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

### 4. Copilot Usage Reports

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
@@ -255,7 +255,7 @@ Display name
 The full name of the user.
 Prompts submitted (any app)
-The total number of prompts this user submitted to Microsoft 365 Copilot Chat during the selected timeframe.
+Total number of prompts a user submitted in Copilot across all in-scope host applications during the selected timeframe.
 Copilot Chat (work) prompts submitted
 The total number of prompts this user submitted to Copilot Chat (work) during the selected timeframe.
 Copilot Chat (web) prompts submitted
@@ -291,7 +291,9 @@ Display user-specific data
 By default, usernames and display names in Copilot Search usage reports are anonymous. Global administrators can update the settings to reveal usernames and display names.
 Important
-Microsoft recommends that you use roles with the fewest permissions. This helps improve security for your organization. Global Administrator is a highly privileged role that should be limited to emergency scenarios when you can't use an existing role.
+Microsoft recommends that you use roles with the fewest permissions. Using roles with the fewest permissions helps improve securit
```

---

### 5. Human-in-the-Loop Workflows

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

### 6. DLP Policy Reference

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

### 7. Sensitivity Labels

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

### 8. Sensitivity Labels for Sites

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

### 9. Authentication Methods

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

### 10. Access Reviews

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

### 11. Create Access Review

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

### 12. Agent Identities for AI Agents

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

### 13. Message Center

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

### 14. Purview What's New

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
@@ -67,7 +84,27 @@ : New support for the Data Security Posture Agent in Microsoft Purview. The
 Data Security Posture agent (preview)
 in Data Security Investigations helps your organization proactively surface credentials buried in data across your organization at scale.
+Updated
+: New guidance for
+how categorization processes data
+in Data Security Investigations. Categorization uses relevance scoring to prioritize the most relevant content for each selected category. Updated
```

---

### 15. Purview Licensing

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

### 4. Connectors
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors
**Classification:** MEDIUM (General content update)

---

### 5. DSPM Considerations
**URL:** https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations
**Classification:** MEDIUM (General content update)

---

### 6. Session Controls
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime
**Classification:** CRITICAL (Deprecation notice)

---

### 7. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-sharepoint
**Classification:** MEDIUM (General content update)

---

### 8. Application Resources
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