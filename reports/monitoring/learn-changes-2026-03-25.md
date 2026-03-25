# Microsoft Learn Documentation Changes

**Run Date:** 2026-03-25
**Run Time:** 2026-03-25T07:04:43.091840+00:00
**Total URLs Checked:** 223

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 32 |
| MEDIUM Changes | 23 |
| NOISE Changes | 1 |
| Redirects | 25 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Monitor |
| 2 | power-platform-inventory | HIGH | None | Review and update |
| 3 | alerts | HIGH | None | Review and update |
| 4 | manage-copilot-studio-messages-capacity | MEDIUM | None | Review optional |
| 5 | capacity-storage | HIGH | 3.5 | Review and update |
| 6 | security-and-governance | MEDIUM | 1.8, 1.4, 1.28, 1.1, 1.5 | Review optional |
| 7 | ...ication-fundamentals-publish-channels | HIGH | None | Review and update |
| 8 | admin-share-bots | CRITICAL | None | Monitor |
| 9 | analytics-overview | MEDIUM | 3.2, 3.10, 2.6, 2.9 | Review optional |
| 10 | analytics-improve-agent-effectiveness | HIGH | None | Review and update |
| 11 | nlu-gpt-overview | HIGH | 2.12 | Review and update |
| 12 | admin-network-isolation-vnet | HIGH | 1.20 | Review and update |
| 13 | microsoft-365-copilot-overview | MEDIUM | 3.8, 3.5 | Review optional |
| 14 | microsoft-365-copilot-privacy | MEDIUM | 4.6, 4.7, 2.23 | Review and update |
| 15 | manage-copilot-agents-integrated-apps | HIGH | 3.8, 3.11, 3.6, 3.1, 2.25 | Review and update |
| 16 | microsoft-365-copilot-usage | CRITICAL | 3.8 | Monitor |
| 17 | m365-agents-visual-map | MEDIUM | 1.1 | Review optional |
| 18 | m365-agents-checklist | HIGH | 3.5, 3.1, 1.11, 1.1, 1.6, 1.5 | Review and update |
| 19 | m365-agents-blueprint | HIGH | 2.1, 2.3, 1.11 | Review and update |
| 20 | dlp-policy-reference | HIGH | None | Review and update |
| 21 | audit-copilot | HIGH | None | Review and update |
| 22 | dspm-for-ai-considerations | HIGH | None | Review and update |
| 23 | insider-risk-management-policies | HIGH | 1.12 | Review and update |
| 24 | ...management-settings-policy-indicators | HIGH | 1.12 | Review and update |
| 25 | insider-risk-management-activities | HIGH | 1.12 | Review and update |
| 26 | import-hr-data | HIGH | 1.12 | Review and update |
| 27 | ediscovery-create-holds | MEDIUM | 1.9, 1.19 | Review optional |
| 28 | endpoint-dlp-learn-about | MEDIUM | 1.17 | Review optional |
| 29 | information-barriers | MEDIUM | 1.22 | Review optional |
| 30 | data-classification-activity-explorer | MEDIUM | 1.6 | Review optional |
| 31 | overview | MEDIUM | 1.11 | Review optional |
| 32 | concept-conditional-access-policies | MEDIUM | None | Review optional |
| 33 | concept-conditional-access-cloud-apps | HIGH | 1.23 | Review and update |
| 34 | ...o-conditional-access-session-lifetime | MEDIUM | 1.23 | Review optional |
| 35 | overview-authentication | CRITICAL | 1.11 | Monitor |
| 36 | how-to-enable-passkey-fido2 | CRITICAL | None | Monitor |
| 37 | permissions-reference | HIGH | None | Review and update |
| 38 | access-reviews-overview | HIGH | 1.3 | Review and update |
| 39 | create-access-review | HIGH | 4.2, 2.8 | Review and update |
| 40 | pim-configure | HIGH | 2.8, 1.18 | Review and update |
| 41 | ...-entra-agent-identities-for-ai-agents | MEDIUM | 1.11, 1.18 | Review optional |
| 42 | restricted-access-control | HIGH | 4.1 | Review and update |
| 43 | restricted-content-discovery | HIGH | 4.6, 4.1, 4.7 | Review and update |
| 44 | data-access-governance-reports | HIGH | 4.6, 4.4, 4.1, 4.5, 4.2 | Review and update |
| 45 | site-lifecycle-management | HIGH | 4.3, 4.2 | Review and update |
| 46 | request-site-attestations | HIGH | 4.2 | Review and update |
| 47 | insights-on-sharepoint-agents | HIGH | 4.5 | Review and update |
| 48 | monitor-your-data | HIGH | None | Review and update |
| 49 | private-link-service | MEDIUM | 1.20 | Review optional |
| 50 | service-health-overview | CRITICAL | 2.10 | Monitor |
| 51 | application | MEDIUM | 1.2 | Review optional |
| 52 | new-dlpcompliancepolicy | NOISE | 1.5 | Monitor |
| 53 | whats-new | HIGH | None | Review and update |
| 54 | microsoft-purview-service-description | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Power Platform Inventory

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -27,8 +27,8 @@ Power Platform inventory
 Feedback
 Summarize this article for me
-The Power Platform admin center now offers tenant administrators a comprehensive, unified view of all key resourcesâagents, apps, and flowsâacross their organization with Power Platform inventory. With this centralized inventory, administrators can effortlessly discover, search, filter, and sort their resources to streamline common administrative tasks.
-Power Platform inventory allows you to easily complete the following tasks:
+Power Platform inventory gives tenant administrators a unified view of all agents, apps, and flows built on Power Platform across their organization. Administrators can discover, search, filter, and sort these resources to streamline common administrative tasks.
+By using Power Platform inventory, you can easily complete the following tasks:
 Spot your champions
 : Quickly identify who's creating the most resources so you can recognize, nurture, and empower your top innovators.
 Enforce compliance standards
@@ -75,21 +75,21 @@ Dynamics 365 administrator
 . If you don't have one of these roles, you can't access the inventory.
 Where to access Power Platform inventory
-Power Platform inventory is available through multiple interfaces and APIs, allowing you to integrate inventory data into your workflows and tools of choice. The following sections list the primary ways to access inventory data.
+You can access Power Platform inventory through multiple interfaces and APIs. By using these options, you can integrate inventory data into your workflows and tools of choice. The following sections list the primary ways to access inventory data.
 The Power Platform admin center user interface
 Manage > Inventory
 : The main inventory page provides a unified view of all resources across your tenant.
 Manage > Copilot Studio:
-Agents (Copilot Studio + Microsoft 365 Copilot Agent Builder), agent flows, and workflows
+Agents (Copilot Studio + Microsoft 365 Cop
```

---

### 2. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -30,15 +30,17 @@ [This article is prerelease documentation and is subject to change.]
 Tenant and environment admins in Power Platform use
 alerts
-to track the operational health of their resources. Admins set up custom thresholds and get notifications when metrics for their resources pass specific thresholds. Create alerts on any metrics in the Monitor area of the Power Platform admin center.
+to track the operational health of their resources. Admins set up custom thresholds and get notifications when metrics for their resources pass specific thresholds. Create alerts on any metrics in the
+Monitor
+area of the Power Platform admin center.
 Keep the following principles in mind:
 Alerts are evaluated after new metrics are produced. Currently, all metrics are 24-hour aggregates, which means an alert rule in the
 Monitor
 area is evaluated every 24 hours after the newest 24-hour aggregates are produced. An alert rule does an on-demand evaluation upon its creation.
-Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. Alert rules can be placed on an environment and a specific resource.
+Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. You can place alert rules on an environment and a specific resource.
 A
 triggered alert
-is when one or more of the resources that are being monitored by an alert rule pass specific thresholds defined by the admin who configured the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for how to improve the resources if it's in a managed environment.
+occurs when one or more of the resources that an alert rule monitors pass specific thresholds that the admin defines when configuring the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for 
```

---

### 3. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

**What Changed:**
```diff
--- +++ @@ -28,14 +28,14 @@ Feedback
 Summarize this article for me
 If you purchased storage after April 2019, or if you have a mix of storage purchases made before and after April 2019, you see your storage capacity entitlement and usage by database, file, and log as it appears in the Microsoft Power Platform admin center today.
-Data volume continues to grow exponentially as businesses advance their digital transformation journey and bring data together across their organization. Modern business applications need to support new business scenarios, manage new data types, and help organizations with the increasing complexity of compliance mandates. To support the growing needs of today's organizations, data storage solutions need to evolve continuously and provide the right solution to support expanding business needs.
+Data volume continues to grow exponentially as businesses advance their digital transformation journey and bring data together across their organizations. Modern business applications need to support new business scenarios, manage new data types, and help organizations with the increasing complexity of compliance mandates. To support the growing needs of today's organizations, data storage solutions need to evolve continuously and provide the right solution to support expanding business needs.
 Note
 For licensing information, see the
 Power Platform Licensing Guide
 .
 If you purchased your Dynamics 365 subscription through a Microsoft partner, contact them to manage storage capacity. The following steps don't apply to partner-based subscriptions.
 Licenses for Microsoft Dataverse capacity-based storage model
-The following licenses provide capacity by using the new storage model. If you have any of these licenses, you see the new model report:
+The following licenses provide capacity by using the new storage model. You see the new model report if you have any of these licenses:
 Dataverse for Apps Database Capacity
 Dataverse for Apps File Capacit
```

---

### 4. Agent Publishing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)

**What Changed:**
```diff
--- +++ @@ -169,6 +169,16 @@ Twitter
 ).
 Suggested actions are presented as a text-only list; users must retype an option to respond.
+Troubleshoot publishing errors
+If you run into issues when publishing your agent, use the following troubleshooting steps to resolve common publishing errors:
+Verify all configurations are correct.
+Make sure that the agent settings, authentication options, and channel configurations are set up properly before publishing.
+Check for any missing dependencies.
+Ensure that all required components, such as topics, flows, connectors, and data sources, are available and properly configured.
+Review error logs for specific error codes and messages.
+Go to the
+Publish
+page and check the publish status for any error details. Use the error codes and messages to identify and address the root cause.
 Next steps (Web app)
 Article
 Description

```

---

### 5. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)

**What Changed:**
```diff
--- +++ @@ -276,21 +276,11 @@ Poor
 quality label. The tooltip also indicates the number of answers sampled to arrive at the calculated percent value.
 In the legend below the chart, hover over any of the quality label reasons to highlight that reason in the chart.
-You can provide feedback to Microsoft about this section with the
-Thumbs up
-and
-Thumbs down
-icons
-. Use the
-Submit feedback to Microsoft
-panel to add a comment and share related files. By providing descriptive feedback like this, we can work together to continuously improve our product.
-On the
-Submit feedback to Microsoft
-panel, describe in natural language your likes or dislikes, depending on which icon you selected to open the panel.
-Choose whether to share prompt, generated response, relevant content samples, and additional log files.
 Select
-Submit
-.
+See questions
+to
+see an unfiltered list of all questions
+within the configured time period.
 Select
 See details
 to open a side panel with question answer rates, knowledge source usage, and error rates over your selected time period. You can use these charts to identify which knowledge sources work well to help users, and which to target for improvements.
@@ -318,6 +308,117 @@ thumbs down
 reactions.
 A stacked bar chart showing the breakdown of the quality of response relative weightings for questions referencing this knowledge source. Hover over any segment of the bar chart to see the value of that segment's relative weighting and the number of questions sampled to arrive at that value.
+Drill down to a list of agent questions
+Drill down to view specific questions that contributed to a metric and the supporting context, such as how the agent responded, how users reacted, and which knowledge sources were involved. This view provides better insight into response quality and helps identify possible gaps in knowledge coverage.
+Important
+You need a Bot Transcript Viewer security role to view the list and its metrics. Only admins can gra
```

---

### 6. Generative AI

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-gpt-overview
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

**What Changed:**
```diff
--- +++ @@ -32,59 +32,67 @@ Generative AI
 in the Artificial Intelligence (AI) playbook.
 In Copilot Studio, you can use the following generative AI features to retrieve and create content, either individually or all together.
-Create an agent
-. With no manual authoring of topics required, an
+Create an agent.
+With no manual authoring of topics required, an
 empty
-agent can generate answers based on knowledge sources you specify such as websites and files. See
-Generative answers
-and the
-Quickstart
+agent can generate answers based on knowledge sources you specify such as websites and files. Learn more in
+Quickstart: Create and deploy an agent
 .
-Harness AI general knowledge
-. When this option is enabled, the agent can answer general questions unrelated to your specific knowledge sources or topics. See
-AI general knowledge
+Harness AI general knowledge.
+When
+Use general knowledge
+is turned on, the agent can answer general questions unrelated to your specific knowledge sources or topics. Learn more in
+Allow the agent to use general knowledge
 .
-Author topics using natural language
-. Describe what you want your topic to do, and Copilot Studio creates it for you. Your agent includes conversational responses and multiple types of nodes. Use the suggested default topic or as a starting point for further development. See
+Author topics using natural language.
+Describe what you want your topic to do, and Copilot Studio creates it for you. Your agent includes conversational responses and multiple types of nodes. Use the suggested default topic as a starting point for further development. Learn more in
 Create and edit topics with Copilot
 .
-Author prompts using natural language
-. Describe the prompt you want to create, and Copilot Studio generates it for you. You can use the suggested default prompt or as a starting point for further development. See
-Create and edit prompts with Copilot
+Author prompts using natural language.
+Describe the prompt you want
```

---

### 7. VNet Support

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-network-isolation-vnet
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.20: Control 1.20: Network Isolation and Private Connectivity
  - File: `controls/pillar-1-security/1.20-network-isolation-private-connectivity.md`

**What Changed:**
```diff
--- +++ @@ -40,10 +40,11 @@ capture telemetry with Application Insights
 or
 make HTTP requests with your agent
-over the virtual network, then the calls from Power Platform to Azure resources and Application Insights go through your private network.
+over the virtual network, calls from Power Platform to Azure resources and Application Insights go through your private network.
 Prerequisites
 Your environment must be
 a Managed Environment in Power Platform
+.
 You must have
 Virtual Network support enabled for your Power Platform environment
 . Also see
@@ -53,20 +54,21 @@ tenant admin
 or have the
 Environment Admin role
+.
 Enable virtual network support for your environment
 To connect to services through a private endpoint, you must have
-vitual network support enabled for Power Platform
-.
-You can enable virtual network support manually, by following the instructions at
+virtual network support enabled for Power Platform
+.
+You can enable virtual network support manually by following the instructions at
 Set up Virtual Network support for Power Platform
 to create virtual networks and delegate subnets that can connect between Azure resources and your Power Platform environment.
 You can also use a prebuilt Azure Resource Manager (ARM) template to configure and connect your Power Platform environment with Azure and enable virtual network support:
 Download the
 ARM template from the Microsoft Copilot Studio samples repository on GitHub
 .
-Open PowerShell, connect to your Azure subscription and deploy the template with the
-New-AzDeployment command
-as follows:
+Open PowerShell, connect to your Azure subscription, and deploy the template with the [
+New-AzDeployment
+] command(/powershell/module/az.resources/new-azdeployment#description) as follows:
 Connect-AzAccount -Subscription "<Azure subscription>"
 New-AzSubscriptionDeployment -Name "<name of deployment>" -TemplateFile "<template.json>" -Location "<Azure geo>"
 where:
@@ -81,23 +83,23 @@ is the geogra
```

---

### 8. Data, Privacy, and Security

**URL:** https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy
**Section:** Microsoft 365 Copilot
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -158,7 +158,7 @@ Encryption in the Microsoft Cloud
 .
 Your control over your data is reinforced by Microsoft's commitment to comply with broadly applicable privacy laws, such as the GDPR, and privacy standards, such as ISO/IEC 27018, the worldâs first international code of practice for cloud privacy.
-For content accessed through Microsoft 365 Copilot agents, encryption can exclude programmatic access, thus limiting the agent from accessing the content. For more information, see
+For content accessed through agents in Microsoft 365, encryption can exclude programmatic access, thus limiting the agent from accessing the content. For more information, see
 Configure usage rights for Azure Information Protection
 .
 Meeting regulatory compliance requirements

```

---

### 9. Manage Copilot Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -24,7 +24,7 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Manage Copilot agents in the Microsoft 365 admin center
+Manage agents in the Microsoft 365 admin center
 Feedback
 Summarize this article for me
 Important

```

---

### 10. Deployment Checklist

**URL:** https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-checklist
**Section:** Microsoft Agent 365 & Agent Essentials (Preview)
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**What Changed:**
```diff
--- +++ @@ -27,7 +27,7 @@ Microsoft 365 agents deployment checklist
 Feedback
 Summarize this article for me
-This checklist is intended to assist admins with the successful deployment of Copilot agent governance. This checklisdt provides a comprehensive guide to help you understand, set up, manage, and deploy agents.
+This checklist is intended to assist admins with the successful deployment of Copilot agent governance. This checklist provides a comprehensive guide to help you understand, set up, manage, and deploy agents.
 Required administrators for the engagement
 :
 Microsoft 365 admin
@@ -42,8 +42,8 @@ :
 Downloadable resources
 :
-Microsoft 365 Copilot agents blueprint
-Microsoft 365 Copilot agents visual guide
+Agents blueprint for Microsoft 365
+Agents visual guide for Microsoft 365
 Manage Microsoft 365 Copilot agent access and availability policies
 Agent policies refer to the tenant settings you can make as an administrator in the Copilot Control System within Microsoft 365 admin center. Agent policies relate to the available settings for all agents in your tenant.
 Step
@@ -51,13 +51,13 @@ Description
 Administrator
 1
-Manage access to Microsoft 365 Copilot agents
+Manage access to agents in Microsoft 365
 Control how your users interact with agents:
 Choose who can access agents
 Choose which type of agents users are allowed to install
 Copilot administrator, SharePoint administrator, Copilot Studio administrator
 2
-Share and publish Microsoft 365 Copilot agents
+Share and publish agents in Microsoft 365
 Agent sharing methods:
 Sideload agents for personal use
 Shared agent with others
@@ -178,7 +178,7 @@ You can publish agents to engage with your customers on multiple platforms or channels, such as live websites, mobile apps, Microsoft 365 Copilot or messaging platforms like Teams and Facebook.
 Copilot administrator, Microsoft 365 administrator
 Manage Microsoft 365 Copilot agent inventory and lifecycle
-You can manage your organizationâs availa
```

---

### 11. Deployment Blueprint

**URL:** https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-blueprint
**Section:** Microsoft Agent 365 & Agent Essentials (Preview)
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**What Changed:**
```diff
--- +++ @@ -24,7 +24,7 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Microsoft 365 Copilot agents deployment blueprint
+Agents deployment blueprint for Microsoft 365
 Feedback
 Summarize this article for me
 This deployment blueprint helps you enable agents in
@@ -34,7 +34,7 @@ This blueprint is scoped primarily to agents created in the
 Agent Builder
 experience using the Microsoft 365 Copilot app.
-The primary challenges when enabling Microsoft 365 Copilot agents include the following:
+The primary challenges when enabling agents in Microsoft 365 include the following:
 Security and governance concerns
 - Your organization can address oversharing, data protection, and compliance risks by implementing robust security and governance controls to safely enable agents in Microsoft 365 Copilot.
 Deployment complexity
@@ -64,7 +64,7 @@ PowerPoint
 Documentation resources
 Governance and security best practices overview
-Manage Microsoft 365 Copilot agents in the Microsoft 365 admin center
+Manage agents in the Microsoft 365 admin center
 Related content
 Microsoft Purview blueprint: Secure by default
 Feedback

```

---

### 12. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -69,6 +69,22 @@ Comment length limit: 1,024 characters
 Description length limit: 1,024 characters
 Maximum size of Endpoint DLP Settings: 16,384 characters
+Default DLP policies
+There are four default DLP policies that are created in every tenant. These policies are designed to help you get started with DLP and provide a baseline level of protection for your organization. You can edit or delete these policies as needed.
+Default Office 365 DLP policy
+This policy detects the presence of credit card numbers in externally shared documents and emails. For more information, see
+Learn about the default data loss prevention policy for Microsoft 365 Copilot location
+Default policy for Teams
+The default DLP policy for Teams tracks all the credit card numbers shared internally and externally to the organization. For more information see,
+Learn about the default data loss prevention policy in Microsoft Teams
+Defaul policy for devices
+This policy detects the presence of credit card numbers in files on devices when users perform specific activities (such as printing a file). When detected, the activity is only audited (not blocked). Admins will receive an alert, but policy tips won't be displayed to users. You can edit these actions at any time. For more information, see
+Learn about the default DLP policy for device
+.
+Default DLP policy for Microsoft 365 Copilot location
+Prevent data leakage and oversharing by restricting Microsoft 365 Copilot and agents from using sensitive info in Copilot interactions. For more information, see
+Learn about the default DLP policy for Microsoft 365 Copilot location
+.
 Policy templates
 There are five types of DLP policy templates across two categories.
 Enterprise applications & devices
@@ -863,7 +879,7 @@ No
 SharePoint
 Yes
-site location at the policy level. If the policy is scoped to an administrative unit that includes SharePoint sites, the policy will only apply to all sites in the administrative unit, no further 
```

---

### 13. Audit Copilot Activities

**URL:** https://learn.microsoft.com/en-us/purview/audit-copilot
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -250,16 +250,16 @@ is currently not used.
 "Messages": [ {"ID":"1715186983849", "isPrompt":true}, {"ID":"1715186984291", "isPrompt":false} ]
 ModelTransparencyDetails
-Details of the AI/GAI model provider.
+Details of the AI model used in the interaction.
+-
+ModelProviderName
+is the publisher of the model used.
 -
 ModelName
-is the name of the model used.
+is the name of the model used. This might not be available for all scenarios.
 -
 ModelVersion
-is the version of the model used.
--
-ModelProviderName
-is the publisher of the model.
+is the version of the model used. This might not be available for all scenarios.
 Operation
 Specifies the name of the activity that was audited.
 For user interactions with Copilot, this property uses values like

```

---

### 14. DSPM Considerations

**URL:** https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations
**Section:** Microsoft Purview
**Classification:** HIGH (Policy language)

**What Changed:**
```diff
--- +++ @@ -107,12 +107,34 @@ .
 In the Microsoft Entra admin portal,
 create and configure a registered app
-to be the service principal authentication for Fabric.
+to be the service principal authentication for Fabric. You will authenticate the app in one of two ways: With
+Federated Credentials
+(recommended) or
+Client Secret
+. The federated credentials option is more secure because it lets Kubernetes workloads authenticate to Azure services without hardâcoding secrets, while ensuring each pod only has the permissions it needs. For more information about this authentication method, see
+Overview of federated identity credentials in Microsoft Entra ID
+.
 After you've created this registered app and still in the Entra admin portal, copy and store the
 Application (client) ID
-and
-Client secret
-values that are required to set up data risk assessments in DSPM for AI:
+, which is always required to setup data risk assessments for Fabric. Then, to authenticate with federated credentials, work with your compliance administrator to identify and enter the
+OIDC Issuer URL
+,
+Namespace
+, and
+Service Account Name
+under
+Edit connection
+. Enter these values into the corresponding fields in
+Your App name
+>
+Certificates & Secrets
+>
+Federated Credentials
+>
+Kubernetes accessing Azure resources
+. Alternatively, to authenticate with a client secret, store the
+Client Secret
+value to then enter in the Microsoft Purview portal:
 To locate the
 Application (client) ID
 : In the Microsoft Entra admin portal,

```

---

### 15. Create Insider Risk Policies

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**What Changed:**
```diff
--- +++ @@ -88,7 +88,7 @@ Data theft from Microsoft 365 apps by users leaving your organization
 : Detects potential data theft from Microsoft 365 cloud apps by users leaving your organization or whose account was deleted from Microsoft Entra ID.
 Data theft from non-Microsoft 365 apps by users leaving your organization
-: (preview) Detects potential data theft from non-Microsoft 365 cloud apps, including Microsoft Fabric, by users leaving your organization or whose account was deleted from Microsoft Entra ID.
+: Detects potential data theft from non-Microsoft 365 cloud apps, including Microsoft Fabric, by users leaving your organization or whose account was deleted from Microsoft Entra ID.
 Email exfiltration
 : Detects when users email sensitive assets outside your organization. For example, users emailing sensitive assets to their personal email address.â
 To get started, go to

```

---

### 16. Insider Risk Indicators

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**What Changed:**
```diff
--- +++ @@ -145,7 +145,7 @@ To use this indicator, enable
 pay-as-you-go billing
 in your organization.
-These indicators include policy indicators for Microsoft Fabric workloads such as Power BI and Lakehouse (preview). They help you detect techniques used to:
+These indicators include policy indicators for Microsoft Fabric workloads such as Power BI and Lakehouse. They help you detect techniques used to:
 Figure out the environment (for example, viewing Power BI reports and dashboards).
 Gather data of interest (for example, downloading Power BI reports).
 Obfuscate the data gathered or change protection (for example, downgrading or removing sensitivity labels of Power BI or Lakehouse assets).
@@ -584,7 +584,7 @@ .
 Make your changes.
 Variant limitations
-You can create up to three variants for each built-in indicator.
+You can create up to ten variants for each built-in indicator and a total of 100 variants across all indicators.
 You can add up to five detection groups of a single type for a single variant. For example, you can add a maximum of five groups of domains, five groups of file types, and so on.
 Variants don't support sequences, cumulative exfiltration activities, the risk score booster, or
 real-time analytics

```

---

### 17. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-activities
**Section:** Microsoft Purview
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**What Changed:**
```diff
--- +++ @@ -60,6 +60,9 @@ if needed to help locate these types of alerts.
 Select an alert to discover more information and to review the alert details
 . Review details and connections associated with the alert:
+View the
+agent summary tab
+to review intelligently distilled user activity and risk pattern narratives.
 Use the
 Activity explorer tab
 to review a timeline of the associated potentially risky behavior and to identify all risk activities for the alert.
@@ -148,7 +151,7 @@ at the top of the dashboard page.
 Select an alert to display the Agent summary and overview details for the alert. Select
 View details
-to view details for the alert and for access to the details sections like the risk factors, the Activity explorer, and more.
+to view details for the alert and for access to the details sections like the risk factors, risk pattern narratives (preview), the Activity explorer, and more.
 If you disagree with the
 Agent categorization
 , select
@@ -159,6 +162,51 @@ For an overview of how alerts provide details, context, and related content for risky activity and how to make your investigation process more effective, see the
 Insider Risk Management Alerts Triage Experience video
 .
+Agent summary tab
+This section in the
+Alert details
+page is only available when selecting an alert from the
+Triage Agent in Insider Risk Management
+dashboard. Agent summary information includes details on the categorization for the alert and details about the associated risks used in the triage process. This view provides you with the following information:
+Agent categorization
+: Alerts are categorized as
+Needs attention
+or
+Less urgent
+.
+User info
+: Provides the
+Alert history
+,
+Title
+,
+Organization
+and
+Last working date
+for the user. Select the tile to view additional details (preview).
+Risk patterns
+: Provides a narrative summary of each risk associated with the alert (preview).
+Select the narrative summary (preview) for each listed risk to review th
```

---

### 18. HR Data Connector

**URL:** https://learn.microsoft.com/en-us/purview/import-hr-data
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**What Changed:**
```diff
--- +++ @@ -37,12 +37,13 @@ Assign the Data Connector Admin role to the user who creates the HR connector in Step 3. This role is required to add connectors on the
 Data connectors
 page in the Microsoft Purview portal. Multiple role groups include this role by default. For a list of these role groups, see
-Roles in Microsoft Defender for Office 365 and Microsoft Purview compliance
-. Alternatively, an admin in your organization can create a custom role group, assign the Data Connector Admin role, and add the appropriate users as members. For instructions, see:
+Roles in Microsoft Defender for Office 365 and Microsoft Purview
+. Alternatively, an admin in your organization can create a custom role group, assign the Data Connector Admin role, and then add the appropriate users as members. For instructions, see:-
 Permissions in the Microsoft Purview portal
+-
 Roles and role groups in Microsoft Defender for Office 365 and Microsoft Purview compliance
-Understand that the sample script you run in Step 4 uploads your HR data to the Microsoft cloud so that the insider risk management solution can use it. This sample script isn't supported under any Microsoft standard support program or service. It's provided AS IS without warranty of any kind. Microsoft further disclaims all implied warranties including, without limitation, any implied warranties of merchantability or of fitness for a particular purpose. You assume all risk arising from the use or performance of the sample script and documentation. In no event shall Microsoft, its authors, or anyone else involved in the creation, production, or delivery of the scripts be liable for any damages whatsoever (including, without limitation, damages for loss of business profits, business interruption, loss of business information, or other pecuniary loss) arising out of the use of or inability to use the sample scripts or documentation, even if Microsoft has been advised of the possibility of such damages.
-Know that this con
```

---

### 19. Authentication Contexts

**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-cloud-apps#authentication-context
**Section:** Microsoft Entra ID
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.23: Control 1.23: Step-Up Authentication for AI Agent Operations
  - File: `controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md`

**What Changed:**
```diff
--- +++ @@ -27,6 +27,7 @@ Conditional Access: Target resources
 Feedback
 Summarize this article for me
+Overview
 Target resources (formerly cloud apps, actions, and authentication context) are key signals in a Conditional Access policy. Conditional Access policies let admins assign controls to specific applications, services, actions, or authentication context.
 Admins can choose from the list of applications or services that include built-in Microsoft applications and any
 Microsoft Entra integrated applications
@@ -56,12 +57,12 @@ include multiple related child apps or services. When new Microsoft cloud applications are created, they appear in the app picker list as soon as the service principal is created in the tenant.
 Office 365
 Microsoft 365 offers cloud-based productivity and collaboration services like Exchange, SharePoint, and Microsoft Teams. In Conditional Access, the Microsoft 365 suite of applications appears under 'Office 365'. Microsoft 365 cloud services are deeply integrated to ensure smooth and collaborative experiences. This integration might cause confusion when creating policies because some apps, like Microsoft Teams, depend on others, like SharePoint or Exchange.
-The Office 365 app grouping in Conditional Access makes it possible to target these services all at once. We recommend using the Microsoft 365 grouping, instead of targeting individual cloud apps to avoid issues with
+The Office 365 app grouping in Conditional Access makes it possible to target these services all at once. Use the Microsoft 365 grouping, instead of targeting individual cloud apps, to avoid issues with
 service dependencies
 .
-Targeting this group of applications helps to avoid issues that might arise because of inconsistent policies and dependencies. For example: The Exchange Online app is tied to traditional Exchange Online data like mail, calendar, and contact information. Related metadata might be exposed through different resources like search. To ensure that
```

---

### 20. Admin Roles

**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -91,6 +91,9 @@ Authentication Extensibility Administrator
 Customize sign in and sign up experiences for users by creating and managing custom authentication extensions.
 25a516ed-2fa0-40ea-a2d0-12923a21473a
+Authentication Extensibility Password Administrator
+Trigger a password submit event for custom authentication.
+0b00bede-4072-4d22-b441-e7df02a1ef63
 Authentication Policy Administrator
 Can create and manage the authentication methods policy, tenant-wide MFA settings, password protection policy, and verifiable credentials.
 0526716b-113d-4c15-b2c8-68e3c22b9f80
@@ -127,7 +130,7 @@ Conditional Access Administrator
 Can manage Conditional Access capabilities.
 b1be1c3e-b65d-4f19-8427-f6fa0d97feb9
-Customer LockBox Access Approver
+Customer Lockbox Access Approver
 Can approve Microsoft support requests to access customer organizational data.
 5c4f9dcd-47dc-4cf7-8c9a-9e4207cbfc91
 Desktop Analytics Administrator
@@ -157,6 +160,12 @@ Edge Administrator
 Manage all aspects of Microsoft Edge.
 3f1acade-1e04-4fbc-9b69-f0302cd84aef
+Entra Backup Administrator
+Manage all aspects of Microsoft Entra Backup, such as create recovery jobs and manage backup snapshots.
+b6a27b2b-f905-4b2e-81b5-0d90e0ef1fdb
+Entra Backup Reader
+Read all aspects of Microsoft Entra Backup, such as list all preview jobs, recovery jobs, backup snapshots, and create preview jobs.
+f42252d9-5400-4d7b-b9ef-cc582dbb8577
 Exchange Administrator
 Can manage all aspects of the Exchange product.
 29232cdf-9323-42fd-ade2-1d097af3e4de
@@ -364,6 +373,9 @@ Teams Devices Administrator
 Can perform management related tasks on Teams certified devices.
 3d762c5a-1b6c-493f-843e-55a3b42923d4
+Teams External Collaboration Administrator
+Manage external collaboration policies and settings for Teams, including configuring external domains and controlling which groups and users can interact with the organization.
+2fe872fb-daa8-4afc-8f6c-53c4565cfef4
 Teams Reader
 Read everything in the Teams admin center
```

---

### 21. Access Reviews

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview
**Section:** Microsoft Entra ID
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**What Changed:**
```diff
--- +++ @@ -34,7 +34,7 @@ As new employees join, how do you ensure they have the access they need to be productive?
 As people move teams or leave the company, how do you make sure that their old access is removed?
 Excessive access rights can lead to compromises.
-Excessive access right can also lead audit findings as they indicate a lack of control over access.
+Excessive access rights can also lead to audit findings as they indicate a lack of control over access.
 You have to proactively engage with resource owners to ensure they regularly review who has access to their resources.
 When should you use access reviews?
 Too many users in privileged roles:
@@ -46,9 +46,9 @@ Microsoft Entra Privileged Identity Management (PIM)
 experience.
 When automation is not possible:
-You can create rules for dynamic membership groups, security groups, or Microsoft 365 Groups, but what if the HR data isn't in Microsoft Entra ID or if users still need access after leaving the group to train their replacement? You can then create a review on that group to ensure those who still need access keeps access.
+You can create rules for dynamic membership groups, security groups, or Microsoft 365 Groups, but what if the HR data isn't in Microsoft Entra ID or if users still need access after leaving the group to train their replacements? You can then create a review on that group to ensure those who still need access keeps access.
 When a group is used for a new purpose:
-If you have a group that is going to be synced to Microsoft Entra ID, or if you plan to enable the application Salesforce for everyone in the Sales team group, it would be useful to ask the group owner to review the dynamic membership group before it's used in a different risk content.
+If you have a group that is going to be synced to Microsoft Entra ID, or if you plan to enable the application Salesforce for everyone in the Sales team group, it would be useful to ask the group owner to review the dynamic membership gro
```

---

### 22. Create Access Review

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/create-access-review
**Section:** Microsoft Entra ID
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`

**What Changed:**
```diff
--- +++ @@ -110,7 +110,7 @@ Inactive users (on tenant level)
 . If you check the box, the scope of the review focuses on inactive users only, those who haven't signed in either interactively or non-interactively to the tenant. Then, specify
 Days inactive
-with many days inactive up to 730 days (two years). Users in the group inactive for the specified number of days are the only users in the review.
+with the number of days inactive up to 730 days (two years). Users in the group inactive for the specified number of days are the only users in the review.
 Note
 Recently created users aren't affected when configuring the inactivity time. The Access Review checks if a user has been created in the time frame configured and disregard users who havenât existed for at least that amount of time. For example, if you set the inactivity time as 90 days and a guest user was created or invited less than 90 days ago, the guest user won't be in scope of the Access Review. This ensures that a user can sign in at least once before being removed.
 Select
@@ -119,6 +119,7 @@ Next: Reviews
 You can create a single-stage or multi-stage review. For a single stage review, continue here. To create a multi-stage access review, follow the steps in
 Create a multi-stage access review
+.
 In the
 Specify reviewers
 section, in the
@@ -158,7 +159,6 @@ .
 Note
 When creating an access review, you're able to specify the start date, but the start time could vary a few hours based on system processing. For example, if you create an access review at 03:00 UTC on 09/09 that is set to run on 09/12, then the review is scheduled to run at 03:00 UTC on the start date, but could be delayed due to system processing.
-You're able to specify the start date, but the start time can vary a few hours based on system processing.
 Next: Settings
 In the
 Upon completion settings
@@ -178,7 +178,7 @@ Take recommendations
 : Takes the system's recommendation to deny or approve the user's continued access.
 Warning
```

---

### 23. Privileged Identity Management

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**What Changed:**
```diff
--- +++ @@ -27,6 +27,7 @@ What is Microsoft Entra Privileged Identity Management?
 Feedback
 Summarize this article for me
+Overview
 Privileged Identity Management (PIM) is a service in Microsoft Entra ID that enables you to manage, control, and monitor access to important resources in your organization. These resources include resources in Microsoft Entra ID, Azure, and other Microsoft Online Services such as Microsoft 365 or Microsoft Intune. The following video explains important PIM concepts and features.
 Reasons to use
 Organizations want to minimize the number of people who have access to secure information or resources, because that reduces the chance of
@@ -63,7 +64,7 @@ Download
 audit history
 for internal or external audit
-Prevents removal of the
+Prevent removal of the
 last active Global Administrator
 and
 Privileged Role Administrator
@@ -119,21 +120,21 @@ principle of least privilege access
 A recommended security practice in which every user is provided with only the minimum privileges needed to accomplish the tasks they're authorized to perform. This practice minimizes the number of Global Administrators and instead uses specific administrator roles for certain scenarios.
 Role assignment overview
-The PIM role assignments give you a secure way to grant access to resources in your organization. This section describes the assignment process. It includes assign roles to members, activate assignments, approve or deny requests, extend and renew assignments.
+The PIM role assignments give you a secure way to grant access to resources in your organization. This section describes the assignment process. It includes assigning roles to members, activating assignments, approving or denying requests, and extending and renewing assignments.
 PIM keeps you informed by sending you and other participants
 email notifications
-. These emails might also include links to relevant tasks, such activating, approve or deny a request.
+. These emails might also includ
```

---

### 24. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`

**What Changed:**
```diff
--- +++ @@ -34,7 +34,9 @@ .
 What do you need to restrict site access?
 What are the license requirements?
-Your organization needs to have the right license and meet certain administrative permissions or roles to use the feature described in this article.
+Your organization needs to have the right
+licenses
+and meet certain administrative permissions or roles to use the feature described in this article.
 First, your organization must have one of the following base licenses:
 Office 365 E3, E5, or A5
 Microsoft 365 E1, E3, E5, or A5
@@ -125,7 +127,7 @@ Edit group
 Set-SPOSite -Identity <siteurl> -RestrictedAccessControlGroups <comma separated group GUIDS>
 View group
-Get-SPOSite -Identity <siteurl> Select RestrictedAccessControl, RestrictedAccessControlGroups
+Get-SPOSite -Identity <siteurl> | Select RestrictedAccessControl, RestrictedAccessControlGroups
 Remove group
 Set-SPOSite -Identity <siteurl> -RemoveRestrictedAccessControlGroups <comma separated group GUIDS>
 Reset site access restriction

```

---

### 25. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -38,13 +38,17 @@ Caution
 Overuse of Restricted Content Discovery can negatively affect performance across search, SharePoint, and Copilot. Removing sites or files from tenant-wide discovery means that there's less content for search and Copilot to ground on, leading to inaccurate or incomplete results.
 Use cases for Restricted Content Discovery
-Restricted Content Discovery can be applied to any SharePoint site in your organization. The key use case for this feature is to prevent accidental discovery of high-risk sites.
-We recommend using tools such as Data access governance reports and SharePoint admin center's
+Restricted Content Discovery can be applied to any SharePoint site in your organization
+if at least one user in your organization is assigned a Copilot license
+. The key use case for this feature is to prevent accidental discovery of high-risk sites.
+We recommend using tools such as data access governance reports and the SharePoint admin center's
 Active sites
 tab to first compile a selective list of targeted sites.
 What you need to restrict a specific SharePoint access?
 What are the license requirements?
-Your organization needs to have the right license and meet certain administrative permissions or roles to use the feature described in this article.
+Your organization needs to have the right
+licenses
+and meet certain administrative permissions or roles to use the feature described in this article.
 First, your organization must have one of the following base licenses:
 Office 365 E3, E5, or A5
 Microsoft 365 E1, E3, E5, or A5
@@ -64,13 +68,13 @@ For organizations without a Copilot license, you can use SharePoint Advanced Management features
 by purchasing a standalone SharePoint Advanced Management license
 .
-In addition to above, you also need the latest version of
+In addition to preceding information, you also need the latest version of
 Microsoft SharePoint Online Management Shell
 .
 Configure Restricted Content Discovery
 By 
```

---

### 26. Data Access Governance Reports

**URL:** https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -30,7 +30,9 @@ As sprawl and oversharing of SharePoint sites increase with exponential data growth, organizations need help with governing their data. Data access governance reports can help you govern access to SharePoint data. The reports let you discover sites that contain potentially overshared or sensitive content. You can use these reports to assess and apply the appropriate security and compliance policies.
 What you need to create a data access governance report
 What are the license requirements?
-Your organization needs to have the right license and meet certain administrative permissions or roles to use the feature described in this article.
+Your organization needs to have the right
+licenses
+and meet certain administrative permissions or roles to use the feature described in this article.
 First, your organization must have one of the following base licenses:
 Office 365 E3, E5, or A5
 Microsoft 365 E1, E3, E5, or A5

```

---

### 27. Site Lifecycle Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/site-lifecycle-management
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -34,7 +34,9 @@ . Inactive site policies, part of SharePoint's site lifecycle management features, help you automate this process. You can set up an inactive site policy to automatically detect inactive sites and notify site owners by email. Owners can then confirm if the site is still active.
 What do you need to create an inactive site policy?
 What are the license requirements?
-Your organization needs to have the right license and meet certain administrative permissions or roles to use the feature described in this article.
+Your organization needs to have the right
+licenses
+and meet certain administrative permissions or roles to use the feature described in this article.
 First, your organization must have one of the following base licenses:
 Office 365 E3, E5, or A5
 Microsoft 365 E1, E3, E5, or A5

```

---

### 28. Site Attestation

**URL:** https://learn.microsoft.com/en-us/sharepoint/request-site-attestations
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**What Changed:**
```diff
--- +++ @@ -36,7 +36,9 @@ This article describes how to create and configure a site attestation policy.
 Requirements for a site attestation policy
 What are the license requirements?
-Your organization needs to have the right license and meet certain administrative permissions or roles to use the feature described in this article.
+Your organization needs to have the right
+licenses
+and meet certain administrative permissions or roles to use the feature described in this article.
 First, your organization must have one of the following base licenses:
 Office 365 E3, E5, or A5
 Microsoft 365 E1, E3, E5, or A5
@@ -59,7 +61,7 @@ How does a site attestation policy work?
 When a site attestation policy runs (usually on a monthly basis), it generates a report that lists sites requiring attestation according to policy criteria. Site owners and site admins are notified via email, prompting them to review and address potential issues. Depending on how the policy is configured, specified actions can be taken for sites that are ownerless or that pose a potential risk to your organization.
 As a SharePoint administrator, you can specify the scope of a site attestation policy, what actions should occur, and whether you have exceptions to the policy.
-Part 1 - Create a site attestation policy
+Create a site attestation policy
 As a
 SharePoint administrator
 , go to the
@@ -74,8 +76,7 @@ Site attestation policies
 , select
 Open
-.
-Select
+. Then select
 Create a policy
 .
 On the
@@ -85,14 +86,51 @@ , review the information, and then select
 Next
 . Then proceed to the next section.
-Part 2 - Define the scope of a site attestation policy
 To define the scope of a site attestation policy, on the
 Set policy scope
 page, select one of the following options:
 Upload a CSV file with a list of up to 10,000 URLs
 ; or
 Select sites at scale
-Scope of site attestation policies
+For more information, see the following sections in this article:
+About the scope of site attestation pol
```

---

### 29. Agent Insights

**URL:** https://learn.microsoft.com/en-us/sharepoint/insights-on-sharepoint-agents
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -32,7 +32,9 @@ You can generate and manage agent insights report in SharePoint Admin Center or with SharePoint Online Management Shell.
 What do you need to access agent insights report
 License requirements
-Your organization needs to have the right licenses and meet certain administrative permissions or roles to use the feature described in this article.
+Your organization needs to have the right
+licenses
+and meet certain administrative permissions or roles to use the feature described in this article.
 First, your organization must have one of the following licenses:
 Office 365 E3, E5, or A5
 Microsoft 365 E1, E3, E5, or A5

```

---

### 30. Workbooks

**URL:** https://learn.microsoft.com/azure/sentinel/monitor-your-data
**Section:** Azure Services
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -29,7 +29,6 @@ Summarize this article for me
 After you connect your data sources to Microsoft Sentinel, visualize and monitor the data using workbooks in Microsoft Sentinel. Microsoft Sentinel workbooks are based on Azure Monitor workbooks, and add tables and charts with analytics for your logs and queries to the tools already available in Azure.
 Microsoft Sentinel allows you to create custom workbooks across your data or use existing workbook templates available with packaged solutions or as standalone content from the content hub. Each workbook is an Azure resource like any other, and you can assign it with Azure role-based access control (RBAC) to define and limit who can access.
-This article describes how to visualize your data in Microsoft Sentinel by using workbooks. Editing workbooks directly in the Defender portal is as Preview.
 Important
 After
 March 31, 2027
@@ -247,13 +246,6 @@ Other resources:
 KQL quick reference
 Kusto Query Language learning resources
-Known issues for editing workbooks in the Defender portal (Preview)
-Editing workbooks directly in the Defender portal is currently in Preview, and currently includes the following known issues:
-The advanced editor might show up in light mode, even if your portal is set to dark mode.
-Custom endpoint data isn't supported for editing workbooks in the Defender portal.
-Workbooks within workbooks aren't supported for editing in the Defender portal.
-Read-only sharing isn't supported for workbooks in the Defender portal.
-Mermaid diagrams aren't supported for editing workbooks in the Defender portal.
 Related articles
 For more information, see:
 Commonly used Microsoft Sentinel workbooks

```

---

### 31. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -48,6 +48,10 @@ :
 Authoring custom data quality rules using SQL expression
 language is now generally available. Users can create custom rules using both Azure Data Factory expression and SQL expression languages.
+Data Loss Prevention
+Preview
+: DLP supports adaptive scopes for scoping SharePoint policies.
+SharePoint location scoping
 Data Security Investigations
 New
 :
@@ -59,11 +63,43 @@ option.
 Standard
 categorization can significantly reduce the time it takes to complete processing and the amount of Data Security Investigation Compute Units (compute unit) needed for categorization.
+In preview
+: New support for the Data Security Posture Agent in Microsoft Purview. The
+Data Security Posture agent (preview)
+in Data Security Investigations helps your organization proactively surface credentials buried in data across your organization at scale.
+Data Security Posture Management (preview)
+New
+: You can now use
+federated credentials
+as a more secure method of authentication to run Fabric data risk assessments. This change is also available for data risk assessments in Data Security Posture Management for AI (classic). For more information, see
+Prerequisites for Fabric data risk assessments
+.
+eDiscovery
+In preview
+: Use the new
+Advanced review set explorer
+to query review set data with Kusto Query Language (KQL). Build advanced queries with complex filtering, pattern-based text extraction, and data visualization to analyze and find key information in your review sets.
 Insider Risk Management
 In preview
 : Disable content download to create cases without content to reduce triage time. To get started, see
 Enable or disable content download
 .
+General availability (GA)
+:
+Microsoft Fabric indicators
+now include Lakehouse indicators.
+General availability (GA)
+: A new quick policy template for
+detecting data theft from non-Microsoft 365 apps by users leaving your organization
+is now available.
+General availability (GA)
+:
+Pay-as-y
```

---

### 32. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -176,6 +176,28 @@ Learn more about theâ¯
 list of premium templates
 for Compliance Manager.
+Microsoft Purview Customer Key
+Microsoft Purview Customer Key lets you control your organization's encryption keys and use them to encrypt your data at rest in Microsoft data centers. With Customer Key, you add a layer of encryption using your own keys. Customer Key provides data-at-rest encryption for multiple Microsoft 365 workloads. To learn more, see
+Customer Key overview
+.
+Licensing requirements
+Each user who benefits from Customer Key requires a license. Requirements vary by workload.
+Customer Key for Multiple Workloads
+Because data encryption policies apply at the tenant level, your tenant must have at least as many Customer Key licenses as users assigned Exchange or Teams licensesâwhichever is greater. SharePoint isn't included in this license count because Customer Key for SharePoint is licensed separately. Microsoft periodically validates your license count. If your tenant doesn't have enough eligible licenses, encryption reverts to the default service encryption.
+Customer Key for Exchange
+Each mailbox must have a persistent, eligible license to receive a data encryption policy. Microsoft periodically validates mailbox licenses. If a mailbox doesn't have an eligible license, encryption reverts to the default service encryption.
+Plan availability
+The following table shows Customer Key availability:
+Feature
+Microsoft 365 E5/A5/G5, Microsoft Purview Suite/EDU/GOV/FLW, Microsoft 365 E5/A5/F5/G5 Information Protection and Governance
+Office 365 E5/A5/G5
+Customer Key
+Yes
+Yes
+Related resources
+Set up Customer Key
+Learn about the availability key for Customer Key
+Manage Customer Key
 Microsoft Purview Customer Lockbox
 Customer Lockbox provides an extra layer of control by offering customers the ability to give explicit access authorization for service operations. By demonstrating that procedures are in place for explicit data access auth
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Connector Reference
**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Classification:** CRITICAL (Deprecation notice)

---

### 2. Copilot Studio Message Capacity
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity
**Classification:** MEDIUM (General content update)

---

### 3. Security and Governance
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Classification:** MEDIUM (General content update)

---

### 4. Share and Manage Agents
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Classification:** CRITICAL (Deprecation notice)

---

### 5. Analytics
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Classification:** MEDIUM (General content update)

---

### 6. M365 Copilot Overview
**URL:** https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview
**Classification:** MEDIUM (General content update)

---

### 7. Data, Privacy, and Security
**URL:** https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy
**Classification:** MEDIUM (General content update)

---

### 8. Copilot Usage Reports
**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage
**Classification:** CRITICAL (Deprecation notice)

---

### 9. Visual Governance Guide
**URL:** https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-visual-map
**Classification:** MEDIUM (General content update)

---

### 10. eDiscovery Holds
**URL:** https://learn.microsoft.com/en-us/purview/ediscovery-create-holds
**Classification:** MEDIUM (General content update)

---

### 11. Endpoint DLP
**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Classification:** MEDIUM (General content update)

---

### 12. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers
**Classification:** MEDIUM (General content update)

---

### 13. Activity Explorer
**URL:** https://learn.microsoft.com/en-us/purview/data-classification-activity-explorer
**Classification:** MEDIUM (General content update)

---

### 14. Conditional Access
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview
**Classification:** MEDIUM (General content update)

---

### 15. Conditional Access Policies
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-policies
**Classification:** MEDIUM (General content update)

---

### 16. Session Controls
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime
**Classification:** MEDIUM (General content update)

---

### 17. Authentication Methods
**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/overview-authentication
**Classification:** CRITICAL (Deprecation notice)

---

### 18. FIDO2 Security Keys
**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-enable-passkey-fido2
**Classification:** CRITICAL (Deprecation notice)

---

### 19. Agent Identities for AI Agents
**URL:** https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents
**Classification:** MEDIUM (General content update)

---

### 20. Key Vault Private Endpoints
**URL:** https://learn.microsoft.com/en-us/azure/key-vault/general/private-link-service
**Classification:** MEDIUM (General content update)

---

### 21. Azure Service Health
**URL:** https://learn.microsoft.com/en-us/azure/service-health/service-health-overview
**Classification:** CRITICAL (Deprecation notice)

---

### 22. Application Resources
**URL:** https://learn.microsoft.com/en-us/graph/api/resources/application
**Classification:** MEDIUM (General content update)

---

### 23. DLP Cmdlets
**URL:** https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy
**Classification:** NOISE (Metadata or formatting only)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage | https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/purview/compliance-manager | https://learn.microsoft.com/en-us/purview/compliance-manager |
| https://learn.microsoft.com/purview/compliance-manager-assessments | https://learn.microsoft.com/en-us/purview/compliance-manager-assessments |
| https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-enable-passkey-fido2 | https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-authentication-passkeys-fido2 |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health | https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide |
| https://learn.microsoft.com/azure/sentinel/connect-data-sources | https://learn.microsoft.com/en-us/azure/sentinel/connect-data-sources |
| https://learn.microsoft.com/azure/sentinel/monitor-your-data | https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data |
| https://learn.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules | https://learn.microsoft.com/en-us/azure/sentinel/automate-incident-handling-with-automation-rules |
| https://learn.microsoft.com/azure/sentinel/investigate-cases | https://learn.microsoft.com/en-us/azure/sentinel/investigate-cases |
| https://learn.microsoft.com/en-us/azure/service-health/service-health-overview | https://learn.microsoft.com/en-us/azure/service-health/overview |
| https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai | https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2 |
| https://learn.microsoft.com/azure/cost-management-billing/costs/overview-cost-management | https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management |
| https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets | https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets |
| https://learn.microsoft.com/en-us/azure/devops/test/overview | https://learn.microsoft.com/en-us/azure/devops/test/overview?view=azure-devops |
| https://learn.microsoft.com/en-us/power-apps/guidance/planning/testing-phase | https://learn.microsoft.com/en-us/power-apps/maker/plan-designer/plan-designer |
| https://learn.microsoft.com/en-us/graph/api/resources/application | https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0 |
| https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview | https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview?view=graph-rest-1.0 |
| https://learn.microsoft.com/security/operations/incident-response-planning | https://learn.microsoft.com/en-us/security/operations/incident-response-planning |
| https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy | https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpcompliancepolicy?view=exchange-ps |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview | https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview?view=o365-worldwide |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*