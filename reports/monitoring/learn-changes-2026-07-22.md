# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-22
**Run Time:** 2026-07-22T08:30:43.017773+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 6 |
| HIGH Changes | 11 |
| MEDIUM Changes | 1 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | advanced-connector-policies | HIGH | 1.4 | Update portal-walkthrough |
| 2 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 3 | alerts | HIGH | None | Review and update |
| 4 | business-continuity-disaster-recovery | CRITICAL | 2.4 | Update portal-walkthrough |
| 5 | security-and-governance | MEDIUM | 1.1, 1.4, 1.3, 1.8, 1.28, 1.5, 2.8 | Update portal-walkthrough |
| 6 | knowledge-copilot-studio | HIGH | 1.14, 4.8, 2.16 | Update portal-walkthrough |
| 7 | whats-new | HIGH | 2.10, 2.5, 2.25 | Review and update |
| 8 | whats-new | HIGH | None | Review and update |
| 9 | microsoft-365-copilot-usage | HIGH | 3.8 | Review and update |
| 10 | human-in-the-loop | HIGH | 2.17, 2.12 | Review and update |
| 11 | audit-copilot | HIGH | 1.21, 1.19, 1.6, 1.7, 1.14 | Review and update |
| 12 | audit-search | HIGH | 1.7, 3.12, 3.2 | Update portal-walkthrough |
| 13 | endpoint-dlp-learn-about | HIGH | 1.17 | Review and update |
| 14 | dlp-configure-endpoint-settings | HIGH | 1.17 | Review and update |
| 15 | restricted-access-control | HIGH | 1.3, 4.1 | Review and update |
| 16 | ai-agent-inventory | HIGH | 1.21 | Review and update |
| 17 | microsoft-purview-service-description | HIGH | None | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Advanced Connector Policies

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:2422c33b5bdf3b079d2b014e9cbceb7afffcc593168eac1217fc80d1d40b4f5e

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.4/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -22,9 +22,9 @@ Advanced connector policies
 Feedback
 Summarize this article for me
-Advanced connector policies (ACP) represent the next generation of securing connector usage within Power Platform. ACP provides a modern, flexible approach to managing
+Advanced connector policies (ACP) provide the next generation of securing connector usage within Power Platform. ACP offers a modern, flexible approach to managing
 certified connectors
-, replacing the Business/Non-Business/Blocked classification model in classic
+. It replaces the Business, Non-Business, and Blocked classification model in classic
 data policies
 with a strict allowlist that blocks all connectors by default.
 Key principles of advanced connector policies:
@@ -47,6 +47,19 @@ . Custom connectors and HTTP connectors aren't yet supported. They're planned as a separate rule type in the future. For governing custom connectors and HTTP connectors today, continue using classic
 data policies
 .
+Enforcement modes
+When you enable ACP, you choose how it works alongside your existing classic
+data policies
+. Two modes are available:
+Mixed mode (default)
+: ACP runs alongside classic data policies, and the most restrictive settings from both are enforced. This mode is the starting state when you first enable ACP and is recommended while you migrate. For details, see
+Data policy mixed mode
+.
+ACP-only mode
+: ACP becomes the sole policy evaluator. Classic data policies are ignored but not deleted for the affected scope. Choose this mode after you fully migrate connector governance to ACP. For details, see
+ACP-only mode
+.
+Set the mode independently on an environment group or a single environment.
 Supported connector types
 Advanced connector policies are built on the certified connector catalog. ACP doesn't support all connector types from classic data policies.
 Connector type
@@ -8
```

---

### 2. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:eb81aafa10c84dc9a184e8413ff26e83d753df10133daddc7fabd0b3d9328a05

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -22,6 +22,8 @@ Business continuity and disaster recovery
 Feedback
 Summarize this article for me
+Note
+As of June 22, 2026, Self-Service Disaster Recovery (SSDR) is also available for Finance & Operations (F&O) applications. SSDR enables organizations to maintain an asynchronous secondary copy of their production environment in a paired Azure region and perform self-service failover, failback, and disaster recovery testing.
 Businesses expect their applications and customer data to be protected and resilient during unavoidable outages and disruptions. It's important to document a business continuity plan that minimizes the effects of outages. To recover and resume operations, make sure the plan lists stakeholders, processes, and specific steps.
 Microsoft provides business continuity and disaster recovery capabilities to all
 production type environments
@@ -52,9 +54,6 @@ Most geographies have region pairs separated by at least 300 miles when possible, to help protect your data in large-scale disasters.
 Self-service disaster recovery is a Power Platform infrastructure capability that lets you replicate your environment across long distances and start environment failover between regions yourself.
 You usually have multiple environments of different types in your tenant. This capability is available only for production environments.
-To turn on self-service disaster recovery, make sure your environment is managed and linked to a
-pay-as-you-go billing plan
-.
 Allow virtual network pairing for self-service disaster recovery in Dynamics 365
 If you deploy your Dynamics 365 environment within a virtual network and plan to use self-service disaster recovery, you need to configure a
 virtual network pair
@@ -101,7 +100,7 @@ Disaster recovery drill
 Emergency response for a major regional outage
 Disaster recovery drills
-Your company might have dis
```

---

### 3. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c44725e3549e8a7e84ab5af977afebc298511d5d35c88484b4791b673257c360

**Affected Controls:**
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -80,11 +80,11 @@ Microsoft Security Development Lifecycle Practices
 .
 Data processing and license agreements
-The Copilot Studio service is governed by your commercial license agreements, including the
+Your commercial license agreements, including the
 Microsoft Product Terms
 and the
 Data Protection Addendum
-. For the location of data processing, refer to the
+, govern the Copilot Studio service. For the location of data processing, refer to the
 geographical availability documentation
 .
 Compliance with standards and practices

```

---

### 4. Knowledge Sources

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:6c583aad68d7172df8cb3af771d89af731ae88cda211a40103d04d5d445cc6c7

**Affected Controls:**
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -29,23 +29,6 @@ generative answers node
 in an agent topic.
 You can incorporate knowledge sources into agents during their initial creation, add them after the agent is created, or add them to a generative answers topic node.
-Add and manage knowledge for generative answers
-Generative answers allow your agent to find and present information from multiple sources, internal or external, without having to create specific topics. Use generative answers as primary information sources or as a fallback source when authored topics can't answer a user's query. As a result, you can quickly create and deploy a functional agent. Makers don't need to manually author multiple topics, which might not address all customer questions.
-By default, when you create an agent, Copilot Studio automatically creates the
-Conversational boosting
-system topic. This topic contains a generative answers node, which you can use to begin utilizing knowledge sources immediately. All knowledge sources that you add at the agent level are added to generative answers node in the
-Conversational boosting
-system topic.
-For prerequisites and information on limitations, see
-Generative answers
-.
-For information on analytic metrics on a per knowledge source basis, see:
-Generated answer rate and quality
-for conversational agents.
-Knowledge source use
-for autonomous agents.
-Drill down on a theme
-for knowledge source metrics in the context of themes.
 Supported knowledge sources
 Name
 Source
@@ -101,6 +84,15 @@ Limits and limitations
 .
 Currently, citations returned from a knowledge source can't be used as inputs to other tools or actions.
+Source authentication
+If you're using SharePoint, Dataverse, or enterprise data with Microsoft Copilot connectors, you need to incorporate authentication. For more information, see
+Configure user authentication in Copilot Studio
+. For i
```

---

### 5. Search the Audit Log

**URL:** https://learn.microsoft.com/en-us/purview/audit-search
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:b95348011ab2b95eb6e7ccc616e3efe6e4cf0190b5c5fcbfdebf4464c870c831

**Affected Controls:**
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 3.12: Control 3.12: Agent Governance Exception and Override Management
  - File: `controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.23/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -28,7 +28,7 @@ Each admin Audit account user can have up to 10 search jobs running at the same time, with a limit of one unfiltered search job.
 Before you search the audit log
 Review the following items before you start searching the audit log.
-Audit log search is turned on by default for Microsoft 365 and Office 365 enterprise organizations. To verify that audit log search is turned on, run the following command in
+Audit log search is turned on by default for Microsoft 365 and Office 365 enterprise organizations. Verify the current unified audit log ingestion setting for your organization by running the following command in
 Exchange Online PowerShell
 :
 Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled
@@ -79,9 +79,9 @@ Even when mailbox auditing on by default is turned on, you might notice that mailbox audit events for some users aren't found in audit log searches in the Microsoft Purview portal or via the Office 365 Management Activity API. For more information, see
 Mailbox audit logging
 .
-To turn off audit log search for your organization, run the following command in Exchange Online PowerShell:
+To turn off audit log search for your organization, use the following command to disable unified audit log ingestion in Exchange Online PowerShell:
 Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $false
-To turn on audit search again, run the following command in Exchange Online PowerShell:
+To turn unified audit log ingestion back on for your organization, run the following command in Exchange Online PowerShell:
 Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
 For more information, see
 Turn off audit log search
@@ -95,8 +95,8 @@ .
 For information about exporting the search results returned by the
 Search-UnifiedAuditLog
-cmdlet to a CSV file, see the "Tips for exporting and viewing the audit l
```

---

### 6. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:f82ce62816cfc41a2c0c50870b2190eb9b0fb52cd54719cc7f017a46d69a9a01

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -72,8 +72,8 @@ 1
 Audit logs for Microsoft 365 Copilot interactions are generated only when Microsoft 365 Copilot is licensed and in use.
 Microsoft Purview Audit (Premium)
-Audit (Premium) (formerly named Microsoft 365 Advanced Audit) provides one-year retention of audit logs for user and admin activities and provides the ability to create custom audit log retention policies to manage audit log retention for other Microsoft 365 services. It also provides access to crucial events for investigations and high-bandwidth access to the Office 365 Management Activity API.
-Users benefit from Audit (Premium) because audit records related to user activity in Microsoft 365 services can be retained for up to one year. Additionally, high-value auditing events are logged, such as when items in a user's mailbox are accessed or read.
+Audit (Premium) (formerly named Microsoft 365 Advanced Audit) provides up to one-year retention of audit logs for user and admin activities and provides the ability to create custom audit log retention policies to manage audit log retention for other Microsoft 365 services. It also provides access to crucial events for investigations and high-bandwidth access to the Office 365 Management Activity API.
+Users benefit from Audit (Premium) because audit records related to user activity in Microsoft 365 services can be retained for up to one year. Additionally, intelligent insights for certain auditing events are logged, such as the sensitivity label for items accessed in a user's mailbox.
 By default, Audit (Premium) is enabled at the tenant level for all users that benefit from the service, and automatically provides one-year retention of audit logs for activities (performed by users with the appropriate license) in Microsoft Entra ID, Exchange, and SharePoint.
 Additionally, organizations can use audit log retention policies to ma
```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:97f32254db64ef1f4cb79319af71f9a52af5d10b975b776987f9d9983e425874

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -126,6 +126,8 @@ By: Africa's Talking
 AfterShip (Independent Publisher)
 By: Taiki Yoshida
+Agent SDK
+By: Microsoft
 AgilePoint NX
 By: AgilePoint Inc
 Agilite
@@ -177,11 +179,11 @@ Amazon Redshift [DEPRECATED]
 By: Microsoft
 Amazon S3
-By: Microsoft
+By:
 Amazon S3 Bucket (Independent Publisher)
 By: Michael Megel
 Amazon SQS
-By: Microsoft
+By:
 Ambee (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 AMEE Open Business (Independent Publisher)
@@ -270,8 +272,6 @@ By: Microsoft
 Azure - Foundry IQ
 By: Microsoft
-Azure AD Identity and Access
-By: Microsoft, Daniel Laskewitz
 Azure AI Content Understanding
 By: Microsoft
 Azure AI Document Intelligence (form recognizer)
@@ -283,7 +283,7 @@ Azure AI Search
 By: Microsoft
 Azure App Service
-By: Microsoft
+By:
 Azure Application Insights [DEPRECATED]
 By: Microsoft
 Azure Automation
@@ -340,8 +340,12 @@ By: Microsoft
 Azure Log Analytics Data Collector
 By: Microsoft
+Azure Maps
+By: Microsoft
 Azure Monitor Logs
 By: Microsoft
+Azure Monitor Logs Ingestion
+By: Microsoft
 Azure OpenAI
 By: Microsoft
 Azure Queues
@@ -357,7 +361,7 @@ Azure Text to speech
 By: Microsoft
 Azure VM
-By: Microsoft
+By:
 Badgr (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 Basecamp 2
@@ -548,6 +552,8 @@ By: Cireson
 Cisco Webex Meetings
 By: Cisco
+Cisco Workspaces
+By: Cisco Systems.
 Citymapper (Independent Publisher)
 By: Troy Taylor
 CivicPlus Transform
@@ -626,6 +632,8 @@ By: Roy Paar
 Commercient
 By: Commercient LLC
+CommunitycliQ Agent
+By: Mentorcliq, Inc.
 Companies House (Independent Publisher)
 By: Matt Collins
 Company Connect
@@ -665,7 +673,7 @@ ConvertKit (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 Copilot for Finance
-By: Microsoft
+By:
 Copilot for Sales
 By: Microsoft Corporation

```

---

### 2. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:05968faf084b5065e3d27deb3dd398ef340a5f7e0cb8cf250f1567f6a85c1254

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -34,14 +34,14 @@ Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. You can place alert rules on an environment and a specific resource.
 A
 triggered alert
-occurs when one or more of the resources that an alert rule monitors pass specific thresholds that the admin defines when configuring the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for how to improve the resources if it's in a Managed Environment.
+occurs when one or more of the resources that an alert rule monitors pass specific thresholds that the admin defines when configuring the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for how to improve the resources if it's in a managed environment.
 When to use alerts
 Teams and admins use alerts to find resources that are used more than expected. For example, an admin creates an alert to know if apps in the default environment exceed 50 launches a day.
 Teams use alerts to find resources with degraded health, and work with their makers to fix issues.
 For operations, admins create alerts to know if apps in their production environment are slow to open for users.
 Prerequisites
 You must be a tenant administrator or an environment administrator to access alerts.
-You can only place alerts on a Managed Environment.
+You can only place alerts on a managed environment.
 You must be using the
 new and improved Power Platform admin center
 .
@@ -160,7 +160,7 @@ Find your resource, and select it to open a resource pane, which has more detailed metric information.
 In the upper-right corner of the pane, you see a link labeled
 + New alert rule
-if the resource is in a Managed Environment.
+if the resource is in a managed environ
```

---

### 3. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:53720664769bbff6e5b97fd4df176db2dcbc927cea7764cb9079b2cae1bc85d7

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -35,13 +35,44 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+June 2026
+(Production-ready preview) Use the
+new agent experience
+in Copilot Studio to build agents. The new experience uses an enhanced orchestration runtime for improved response quality and reasoning, available alongside the classic experience.
+Use
+Microsoft IQ
+in the new agent experience to connect your agent to organizational data, giving it access to emails, calendar events, files, Teams messages, and people information.
+Build and reuse
+skills
+in the new agent experience to extend your agent's capabilities with modular, self-contained sets of instructions. Create a skill once, add it to multiple agents, and export it as a Markdown file or package to share with others.
+Turn on
+memory
+in the new agent experience to give your agent persistent context across interactions. It captures user preferences and patterns, stores them per user, and applies them to deliver more relevant and personalized responses over time.
+(General availability) Use the
+Windows 365 for Agents MCP server
+to give your agents full operational control of a Windows 365 cloud PC, including desktop interaction, browser automation, and semantic UI inspection.
+Use
+condition groups
+to manage multiple conditions in a single Message, Question, or prompt node, reducing branching and making topic flows easier to review and maintain.
+(Preview) Integrate
+voice agents with Teams Phone Agent
+to handle specialized call workflows like billing, prescription refills, and order status, with a seamless handoff between Teams Phone Agent and your custom voice agent.
+(Preview) Connect
+other agents
+to your agent in the new agent experience so it
```

---

### 4. Copilot Studio Kit — Compliance Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:a21f7b97b0e12cc11ee4ec25532ff94b24139a9a95d1f7af4d51a36de76b486b

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -23,10 +23,35 @@ Feedback
 Summarize this article for me
 Get the latest information about what's new and what changed in the Copilot Studio guidance hub.
+July 2026
+New articles
+New Copilot Agent Kit capabilities, including
+Agent Debugger
+,
+Agent Library
+,
+Agent Insights Hub
+,
+Power Shield
+, and
+Agent Review Pipeline
+, with significant updates to
+Agent Review Tool
+to describe its expanded scope. This update marks the first phase of the rename from
+Copilot Studio Kit
+to
+Copilot Agent Kit
+.
 June 2026
 New articles
 Measure the return on investment (ROI) and business value of AI agents
 Plan Copilot Studio agent deployments for throughput and rate limits
+Other updates
+New real-world case studies, on how
+Grupo Bimbo standardizes global audit processes with Copilot Studio
+and on how
+Copilot Agent Kit helps organizations improve visibility, monitor performance, and refine their agents
+.
 May 2026
 Architecting agent solutions
 moved to the

```

---

### 5. Copilot Usage Reports

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:b96d16cb3b5826548b73afd5a18d7345769e4de76e4c5d7f9d7e8fe4abb0f64f

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -22,7 +22,7 @@ Microsoft 365 Copilot usage report
 Feedback
 Summarize this article for me
-The Microsoft 365 Copilot usage report provides a summary of how users adopt, retain, and engage with Microsoft 365 Copilot and its associated enabled apps, including agent usage. For Copilot activity on a given day, the report typically becomes available within 72 hours of the end of that day (in UTC).
+The Microsoft 365 Copilot usage report provides a summary of how users adopt, retain, and engage with Microsoft 365 Copilot and its associated enabled apps. For Copilot activity on a given day, the report typically becomes available within 48 hours of the end of that day (in UTC).
 For general information about usage reports in the Microsoft 365 admin center, and to see a list of all available reports, see
 Microsoft 365 admin center usage reports overview
 .
@@ -57,7 +57,7 @@ Usage
 tab to view adoption and usage metrics.
 Interpret the Microsoft 365 Copilot usage report
-At the top, you can filter by different timeframes. You can view the Microsoft 365 Copilot report over the last 7, 30, 90, or 180 days.
+At the top, you can filter by different timeframes. You can view the Microsoft 365 Copilot report over the last 7, 28, 90, or 180 days.
 You can view several numbers for Microsoft 365 Copilot usage, which highlight the enablement number and the adoption of the enablement:
 Enabled Users
 shows the total number of unique users in your organization with Microsoft 365 Copilot licenses over the selected timeframe.
@@ -70,10 +70,6 @@ , the recommended action card highlights
 Microsoft Copilot Dashboard
 , where you can deliver insights to your IT leaders to explore Copilot readiness, adoption, and impact in Viva Insights.
-Active agent users
-shows the total number of unique Microsoft 365 Copilot users in your org who used agents built by your org (including
```

---

### 6. Human-in-the-Loop Workflows

**URL:** https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:91ccd8e16faba4f5088150c3462a8608e8f274ad3cc30fd703b622ab037eae22

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -144,6 +144,30 @@ and
 response
 parameters.
+Workflows support human-in-the-loop patterns through
+RequestPort
+, which pauses execution and waits for external input.
+approvalPort := workflow.RequestPort{
+ ID: "ApprovalPort",
+ Request: reflect.TypeFor[string](),
+ Response: reflect.TypeFor[bool](),
+}
+
+approval := approvalPort.Bind()
+finalize := workflow.NewExecutor("FinalizeExecutor", func(approved bool) string {
+ if approved {
+ return "Request approved by the human reviewer"
+ }
+ return "Request rejected by the human reviewer"
+}).Bind()
+
+wf, err := workflow.NewBuilder(approval).
+ AddEdge(approval, finalize).
+ WithOutputFrom(finalize).
+ Build()
+A
+RequestPort
+defines a typed request/response channel between the workflow and the outside world. When an executor reaches a request port, the workflow pauses and emits an external request event. The workflow resumes when an external response is provided.
 Handling Requests and Responses
 An
 RequestPort
@@ -215,6 +239,40 @@ See this
 full sample
 for a complete runnable file.
+Listen for
+workflow.RequestInfoEvent
+, create a response from the request, and resume the run with that response:
+run, err := inproc.Default.Run(ctx, wf, "Approve deployment to production?")
+if err != nil {
+ return err
+}
+
+var request *workflow.ExternalRequest
+for evt := range run.NewEvents() {
+ if requestEvent, ok := evt.(workflow.RequestInfoEvent); ok {
+ request = requestEvent.Request
+ break
+ }
+}
+
+response, err := request.CreateResponse(true)
+if err != nil {
+ return err
+}
+
+if _, err := run.Resume(ctx, response); err != nil {
+ return err
+}
+
+for evt := range run.NewEvents() {
+ if output, ok := evt.(workflow.OutputEvent); ok {
+ fmt.Println(output.Output)
+ }
+}
+Tip
+See the
+human-in-the-loop sample
+for a complete runnable file.
 Human-in-the-Loop with Agent Orchestrations
 The
 Reques
```

---

### 7. Audit Copilot Activities

**URL:** https://learn.microsoft.com/en-us/purview/audit-copilot
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:66fb7b549f9ef6400aca7fe0e96b15f8f46ba022938722d3e0d465a496b70d14

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/deny-event-correlation-report/deployment-guide.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -49,8 +49,8 @@ The system generates audit logs when an administrator performs activities related to Copilot settings, plugins, promptbooks, or workspaces. For more information, see
 Microsoft 365 Copilot activities
 .
-User activities with Copilot and AI applications
-The system automatically generates audit logs when a user interacts with Copilot or an AI Application. These audit records contain details about which user interacted with Copilot, when the interaction took place, and where it occurred. Audit records also include references to files, sites, or other resources Copilot and AI applications accessed to generate responses to user prompts.
+User activities with Copilot, Cowork, and AI applications
+The system automatically generates audit logs when a user interacts with Copilot, Cowork, or an AI application. These audit records contain details about which user interacted with Copilot, when the interaction took place, and where it occurred. Audit records also include references to files, sites, or other resources Copilot, Cowork, and AI applications accessed to generate responses to user prompts.
 Common properties in Copilot audit logs
 The following table outlines some of the common properties included in audit logs.
 Attribute
@@ -229,6 +229,28 @@ -
 Type
 contains values like docx, pptx, xlsx, TeamsMeeting, TeamsChannel, TeamsChat, and others.
+DLPEvaluationDeferred
+An integer bitmask that indicates DLP evaluation of one or more content processing stages couldn't be completed, so it's deferred for later reevaluation.
+The value is a bitmask where each bit represents a specific evaluation scenario that was deferred. Multiple deferred scenarios can be represented by combining bit values using a bitwise OR operation.
+-
+1 â Prompt
+: DLP evaluation of the user prompt was deferred.
+-
+2 â Response
+: DLP evaluation of the generated 
```

---

### 8. Endpoint DLP

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:652a57f692a4dc5bc52bb5d77b46e7e83bd76c80169310f56e05cb6f39f1b0c3

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -42,13 +42,7 @@ Note
 Endpoint DLP cannot detect the sensitivity label from another tenant on a document.
 Endpoint DLP Windows 10/11 and macOS support
-Endpoint DLP allows you to onboard devices running the following versions of Windows Server:
-Windows Server 2019 (
-November 14, 2023âKB5032196 (OS Build 17763.5122) - Microsoft Support
-)
-Windows Server 2022 (
-November 14, 2023 Security update (KB5032198) - Microsoft Support
-)
+Endpoint DLP allows you to onboard devices running Windows Server 2019 and later versions.
 Note
 Installing the supported Windows Server KBs disables the
 Classification
@@ -59,7 +53,7 @@ Once properly configured, the same data loss protection policies can be automatically applied to both Windows PCs and Windows servers.
 Setting
 Subsetting
-Windows 10, 1809 and later, Windows 11, Windows Server 2019, Windows Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows 10, 1809 and later, Windows 11, Windows Server 2019 and later versions for Endpoints (X64)
 macOS (three latest released versions)
 Notes
 Advanced classification scanning and protection
@@ -131,6 +125,11 @@ n/a
 Supported
 Supported
+Following parameters are only supported on Windows:
+- Print to file
+- Universal print deployed on a printer
+- Corporate printer
+- Print to local
 Removable USB device groups
 n/a
 Supported
@@ -168,7 +167,7 @@ Other settings
 Setting
 Windows 10/11, Windows 10, 1809 and later, Windows 11
-Windows Server 2019, Windows Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows Server 2019 and later versions for Endpoints (X64)
 macOS (three latest released versions)
 Archive file
 Supported
@@ -188,7 +187,7 @@ Endpoint DLP enables you to audit and manage the following types of activities users take on sensitive items that are physically stored Windows 10, Windows 11, or macOS devices.
 Activity
 Description
-Windows 10 (21H2
```

---

### 9. Configure Settings

**URL:** https://learn.microsoft.com/en-us/purview/dlp-configure-endpoint-settings
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:fea397192886ce9071612f39b66b6ca30d71613645f8161d167987be5935f698

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -47,7 +47,7 @@ Microsoft Purview Information Protection Support in Acrobat
 .
 Advanced classification scanning and protection
-When you turn on advanced classification scanning and protection, the Microsoft Purview cloud-based data classification service scans items, classifies them, and returns the results to the local machine. Therefore, you can take advantage of classification techniques such as
+When you turn on advanced classification scanning and protection, the Microsoft Purview cloud-based data classification service scans items, classifies them, and returns the results to the local machine. Because advanced classification runs in the cloud, you can take advantage of classification techniques such as
 exact data match
 classification,
 trainable classifiers
@@ -85,15 +85,15 @@ Tip
 To use advanced classification for Windows 10 devices, you must install KB5016688. To use advanced classification for Windows 11 devices, you must install KB5016691 on those Windows 11 devices. Additionally, you must enable advanced classification before
 Activity explorer
-displays contextual text for DLP rule-matched events. To learn more about contextual text, see
-Contextual summary
+displays contextual text for DLP rule-matched events. To learn more about contextual text, see the "Contextual summary" section in
+Learn about data loss prevention
 .
 Advanced label-based protection for all files on devices
-When you turn on this feature, users can work on files - including files other than Office and PDF files - that have sensitivity labels applying access control settings in an unencrypted state, on their devices. Endpoint DLP continues to monitor and enforce access control and label-based protections on these files even in an unencrypted state. It automatically encrypts them before they're transferred outside from a user's device. For more information abo
```

---

### 10. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:ee6eff880bcbe76f1edb3a7496375cfb9f2d9eac35e5e7443f95c44afdf41c3e

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -22,12 +22,15 @@ Restrict SharePoint site access with Microsoft 365 groups and Microsoft Entra security groups
 Feedback
 Summarize this article for me
-Restricted site access control helps prevent oversharing by designating access of SharePoint sites and its content to users in a specific group. Users not in the specified group can't access the site or its content, even if they had prior permissions or a shared link. You can apply this policy on Microsoft 365 group-connected, Teams-connected, and nongroup connected sites by using Microsoft 365 groups or Microsoft Entra security groups.
-Site access restriction policies take effect when a user attempts to open a site or access a file. Users with direct permissions to the file can still view files in search results. However, they can't access the files if they're not part of the specified group.
-Restricting site access through group membership can minimize the risk of oversharing content. For insights into data sharing, see
-Data access governance reports
-.
-What do you need to restrict site access?
+Restricted site access control (also referred to as
+restricted access control
+or
+site access restriction
+) helps prevent oversharing by designating access of SharePoint sites and its content to users in a specific control group. Users who aren't in the specified control group can't access the site or its content, even if they had prior permissions or a shared link. You can apply this policy on Microsoft 365 group-connected, Teams-connected, and nongroup connected sites by using Microsoft 365 groups or Microsoft Entra security groups.
+Site access restriction policies take effect when a user attempts to open a site, access a file, or search for content in organization search experiences and Microsoft Copilot experiences.
+Note
+Shared channel sites and private channel sites are separate site coll
```

---

### 11. Microsoft Defender - AI Agent Inventory

**URL:** https://learn.microsoft.com/en-us/defender-xdr/security-for-ai/ai-agent-inventory
**Section:** Microsoft Defender
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:af9285eb7e40ac275d66ce63d94db3aedfce9ad0d1fac569b2be81d870d41649

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`

**What Changed:**
```diff
--- +++ @@ -22,41 +22,120 @@ Discover AI agents and assess security posture using Microsoft Defender
 Feedback
 Summarize this article for me
-Microsoft Defender lets you discover all of the Microsoft Agent 365 managed agents in your organization and view their configuration details using two experiences in the Microsoft Defender portal:
-Advanced Hunting
-A dedicated AI agent inventory experience
-This inventory includes cloud agents built with Microsoft Copilot Studio, Microsoft Foundry, and
-supported non-Microsoft cloud platforms
-, and
-local AI agents
-discovered on endpoints.
-This article explains how to discover AI agents, assess their security posture, and use the AI agent inventory in the Microsoft Defender portal.
+Microsoft Defender provides a centralized inventory of AI agents in your organization and assesses their security posture.
+The inventory includes:
+Agents built with Microsoft Copilot Studio, Microsoft Foundry, Microsoft 365, and
+supported non-Microsoft platforms
+.
+Local AI agents
+discovered on endpoint devices.
+Use the
+AI Agents
+page in the Microsoft Defender portal to review agent configuration, risk levels, risk indicators, recommendations, alerts, tools, identities, and related security context. You can also query agent inventory and configuration data by using Advanced Hunting.
 Prerequisites
-Enable security for AI agents, including the Microsoft 365 app connector. See
+Enable security for AI agents, including the Microsoft 365 connector. See
 Enable security for AI agents using Microsoft Defender
 .
 To discover local AI agents that run on endpoints, set up
 AI agent runtime protection in Microsoft Defender for Endpoint
-. Discovery requires Microsoft Defender for Endpoint and Microsoft Defender Antivirus in active mode. Local agents are onboarded separately from cloud agents.
-Discover AI agents and assess security posture using Advanced Hunting
+. Discovery requires Microsoft Defender for Endpoint and Microsoft Defender Antivi
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Security and Governance
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c44725e3549e8a7e84ab5af977afebc298511d5d35c88484b4791b673257c360

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*