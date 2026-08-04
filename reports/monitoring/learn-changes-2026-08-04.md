# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-04
**Run Time:** 2026-08-04T08:38:12.533758+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 9 |
| HIGH Changes | 6 |
| MEDIUM Changes | 11 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 2 | monitor-copilot-studio | MEDIUM | 3.2 | Review optional |
| 3 | manage-copilot-studio-messages-capacity | HIGH | 2.27 | Update portal-walkthrough |
| 4 | capacity-storage | HIGH | 3.5 | Review and update |
| 5 | fundamentals-what-is-copilot-studio | CRITICAL | 2.13 | Monitor |
| 6 | ...ication-fundamentals-publish-channels | MEDIUM | None | Review optional |
| 7 | admin-share-bots | HIGH | 3.10, 3.2, 2.9, 2.6, 2.5 | Update portal-walkthrough |
| 8 | analytics-overview | MEDIUM | 3.10, 3.2, 2.9, 2.6, 2.5 | Update portal-walkthrough |
| 9 | analytics-improve-agent-effectiveness | MEDIUM | None | Update portal-walkthrough |
| 10 | advanced-connectors | MEDIUM | None | Review optional |
| 11 | knowledge-copilot-studio | HIGH | 1.14, 2.16, 4.8 | Update portal-walkthrough |
| 12 | nlu-gpt-overview | MEDIUM | 2.12 | Review optional |
| 13 | add-tools-custom-agent | HIGH | 2.17 | Review and update |
| 14 | advanced-hand-off | MEDIUM | 2.12, 2.19 | Update portal-walkthrough |
| 15 | authoring-test-bot | HIGH | 2.5 | Update portal-walkthrough |
| 16 | whats-new | HIGH | 2.10, 2.25, 2.5 | Review and update |
| 17 | mcp-create-new-server | MEDIUM | None | Review and update |
| 18 | ...rosoft.com/en-us/microsoft-agent-365/ | MEDIUM | 3.13, 3.1, 3.6, 3.14, 3.2, 1.7, 2.12, 2.25, 2.6, 2.5 | Update portal-walkthrough |
| 19 | use-powerapps-checker | HIGH | None | Review and update |
| 20 | microsoft-purview-service-description | HIGH | None | Update portal-walkthrough |
| 21 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Copilot Studio Message Capacity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:30bf9859f5f1911323199cd2fad4a638356849c89ffb889e75f934cab26bd52e

**Affected Controls:**
- Control 2.27: Control 2.27: Consumption-Entitlement Governance
  - File: `controls/pillar-2-management/2.27-consumption-entitlement-governance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.27/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.27/powershell-setup.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.27/portal-walkthrough.md` (CRITICAL)

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
@@ -22,7 +22,9 @@ Manage Copilot Studio credits and capacity
 Feedback
 Summarize this article for me
-The Microsoft Copilot Studio capacity management experience in the Power Platform admin center allows administrators to manage Copilot Studio credit capacity, while monitoring overall capacity consumption. This experience provides an overview of the licensing models in use. This experience allows administrators to efficiently manage their available session capacity.
+Important
+Microsoft Copilot Studio is a multi-harness platform. The Power Platform admin center (PPAC) provides a unified capacity management experience across all Copilot Studio harnesses, including Copilot Chat, Standard, and GitHub Copilot. Administrators can view capacity and consumption data at the agent and environment level in PPAC.
+The Microsoft Copilot Studio capacity management experience in the Power Platform admin center enables administrators to manage Copilot Studio credit capacity and monitor overall capacity consumption. This experience provides an overview of the licensing models in use. Administrators can efficiently manage their available session capacity.
 View summary information
 Sign in to the
 Power Platform admin center
@@ -41,26 +43,28 @@ Summary
 tab.
 The licensing summary view shows usage of both prepaid and session-based capacity units.
-Purchasing a Copilot Studio license includes a specified number of billed Copilot credits pooled across the tenant, which must be assigned to an environment to allow Copilot Studio features for agents in that environment.
-Capacity management features allow administrators to allocate prepurchased capacity across environments, within the tenant, based on anticipated usage of Copilot agents in each environment. The
+When you purchase a Copilot Studio license, you get a specified number of billed Copilot credits pooled acro
```

---

### 2. Share and Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:a1ce97bf6bbb03b1ce656c0e9658e0bf10479c90524e5a34f20970f9db7cde67

**Affected Controls:**
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)

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
@@ -22,6 +22,14 @@ Share agents with other users
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 You can share your agents with others in either of the following ways:
 Grant security groups, or your whole organization, permission to chat with the agent.
 Invite users to collaborate on your agent project. Collaborators always have permission to chat with the agent.
@@ -40,7 +48,7 @@ is turned on, to manage who can chat with the agent in your organization.
 Share an agent for chat
 Web app
-Teams
+Teams app
 Collaborators
 with authoring permissions for a shared agent can always chat with it. However, you can also grant users permission to chat with an agent in Copilot Studio without granting them authoring permissions.
 To grant users permission to only chat with the agent, you can:
@@ -171,7 +179,7 @@ to share the agent with everyone in the organization.
 Share an agent for collaborative authoring
 Web app
-Teams
+Teams app
 When you share an agent with others for
 collaborative authoring,
 you give them permission to view, edit, configure, share, and publish the agent. They can't delete the agent. You can only share agents for collaborative authoring with individual users in your organization. These users can be in different Power Platform environments, as long as they belong to your organization.
@@ -307,6 +315,39 @@ The Bot Transcript Viewer security role is assigned at the environment level in the Power Platform admin center. Learn more about
 enabling this security role
 in your single or group environment.
+Share an agent's evaluations
+Use the
+Agent Viewer
+role in Copilot Studio to give evalua
```

---

### 3. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:3a6c68684f1e36b04ba0928200c846dc8533f849e41fec9acef20158c29aeea6

**Affected Controls:**
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)

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
@@ -22,6 +22,14 @@ Analytics overview
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 Use analytics to understand how well your agent is performing and to identify areas for improvement.
 The
 Analytics

```

---

### 4. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8013dd109dbc00073d730c885b83f4fedf4bcf244ec584589fda7de50440c4ce

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

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
@@ -22,6 +22,14 @@ Analyze conversational agents
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 The
 Analytics
 page in Copilot Studio provides an aggregated insight into the overall effectiveness of your agent across
@@ -60,7 +68,11 @@ Custom metrics
 The
 Custom metrics
-section lets you define up to three business-specific metrics in natural language and track how often each outcome appears across sampled sessions. Use these metrics to complement your standard analytics insights with indicators that reflect your agent's goals and business use. To learn how to create, test, and refine custom metrics, see
+section lets you define up to three business-specific metrics in natural language and track how often each outcome appears across sampled sessions. Use these metrics to complement your standard analytics insights with indicators that reflect your agent's goals and business use.
+For users with the Bot Transcript Viewer privilege, you can
+drill down to a list of customer sessions
+filtered based on the selected segment of the donut graph. From the session list you can see the reasoning behind the metric and access the underlying the transcript by selecting individual sessions.
+To learn how to create, test, and refine custom metrics, see
 Analyze your agent with custom metrics
 .
 Effectiveness

```

---

### 5. Knowledge Sources

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:20f3acd719896760b803b6827ad24815b2caf1dc2db06f768d17dc30a86b8d0a

**Affected Controls:**
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)

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
@@ -22,6 +22,14 @@ Knowledge sources summary
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 In Copilot Studio, knowledge sources work together with generative answers. When you add knowledge sources, agents can use enterprise data from Power Platform, Dynamics 365 data, websites, and external systems. Knowledge sources allow your agents to provide relevant information and insights for your customers.
 Published agents that contain knowledge use the configured knowledge sources to ground the published agent. You can incorporate knowledge at the agent level, in the
 Knowledge
@@ -29,23 +37,6 @@ generative answers node
 in an agent topic.
 You can incorporate knowledge sources into agents during their initial creation, add them after the agent is created, or add them to a generative answers topic node.
-Add and manage knowledge for generative answers
-Generative answers allow your agent to find and present information from multiple sources, internal or external, without having to create specific topics. Use generative answers as primary information sources or as a fallback source when authored topics can't answer a user's query. As a result, you can quickly create and deploy a functional agent. Makers don't need to manually author multiple topics, which might not address all customer questions.
-By default, when you create an agent, Copilot Studio automatically creates the
-Conversational boosting
-system topic. This topic contains a generative answers node, which you can use to begin utilizing knowledge sources immediately. All knowledge sources that you add at the agent level are added to generative ans
```

---

### 6. Human Agent Handoff

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:476411cee51476906ed80fe44ec774ae8db74dd8094f13de4e927b1adc8b2798

**Affected Controls:**
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.19: Control 2.19: Customer AI Disclosure and Transparency
  - File: `controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.19/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.19/troubleshooting.md` (HIGH)

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
@@ -22,6 +22,14 @@ Hand off to a live agent
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 By using Copilot Studio, you can configure your agent to hand off conversations to live agents seamlessly and contextually.
 When your agent hands off a conversation, it can share the full history of the conversation, and all relevant variables. A live agent that uses a connected engagement hub sees an alert, reviews the conversation history, and continues the conversation.
 For more information about how to configure handoff with

```

---

### 7. Test Your Agent

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:651c8190e4549f22dcfc01a4bd870c5427997f52ee2c5c53e89f143b4a1bd24d

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

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
@@ -22,29 +22,38 @@ Test your agent
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 As you design your agent in Copilot Studio, use the test panel to see how the agent leads a customer through the conversation. It's a good way to make sure your topics work and that conversations flow as you expect.
 When you test an agent that uses generative orchestration, you can follow the orchestrator's plan in real time on the
 activity map
 . Close the activity map if you want to follow through the conversation path step by step with tracking between topics turned on.
 In addition to testing your agent in the
 Test your agent
-panel, you can create test sets of multiple queries for automated testing. For more information, see
+panel, you can create test sets of multiple queries for automated testing. Learn more in
 Create test cases to evaluate your agent (preview)
 .
 Use the test chat
 Web app
-Classic
-Teams
+Teams plan
+Teams app
 Use the
 Test your agent
 panel to walk through your agent conversations as a user. It's a good way to make sure your topics are working and that conversations flow as you expect.
-In addition to testing your agent in
+In addition to testing your agent in the
 Test your agent
 panel, you can create test sets of multiple queries for
 automated testing
-. To start an automated test, select the evaluate
-button.
-Preview a conversation
+. To start an automated test, select the
+Evaluate
+icon.
+To preview a conversation:
 If the
 Test your agent
 panel is hidden, open it by selecting
@@ -64,7 +73,7 @@ to avoid having to collapse the activity map at every conversation turn.
 Continue the
```

---

### 8. Agent 365 Documentation Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:db012f4e5b567260111465b28b62f9c9ed1178e6bcd7c9f726360dac2c52b812

**Affected Controls:**
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/opentelemetry-setup.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -25,4 +25,4 @@ Learn more
 Learn more about Microsoft Agent 365
 Agent 365 extends the existing infrastructure that you use for managing people to agents. It equips your agents with the same apps and protections, tailored to agent needs, saving IT time and effort on integrating agents into business processes.
-Get started+Prepare and learn
```

---

### 9. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:3116c58a9e5ee5ed829f1968e9f1b013d772c48a3a4959677e02c05b3b49ade9

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
**Content-Hash:** sha256:5e7c848637c257a56892e786fdc20b0601557d92e73abefa8b50957f561054d2

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

### 2. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:8e2d03dbbe618fc7fff381ba3e6021f04791b29904fd5b0a34209049596aec95

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

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
@@ -311,7 +311,7 @@ Overage status if capacity is allocated to the environment
 Whether capacity is preallocated to the environment
 Environment type
-Managed Environment status
+Managed environment status
 Pay-as-you-go plan linkage status
 Ability to draw capacity from available tenant pool
 Database, file, and log consumption
@@ -342,6 +342,57 @@ in the
 Usage per storage type
 tile. Select the table name for the consumption trend, with the option to track daily usage trends, for up to the past three months.
+Dataverse storage advisor (preview)
+Preview features aren't meant for production use and may have restricted functionality. These features are available before an official release so that customers can get early access and provide feedback.
+Dataverse storage advisor analyzes table-level storage consumption and recommends data that you can clean up to reduce storage usage. The advisor surfaces these recommendations directly in the
+Licensing
+>
+Dataverse
+capacity view, so you can act on them without leaving the Power Platform admin center.
+Note
+Dataverse storage advisor is being rolled out gradually and might not be available in your environment yet. When it's available, recommendations appear only for environments that have storage that can be cleaned up.
+When recommendations are available, the advisor adds the following experiences:
+Storage recommendation banner
+: A banner appears above the capacity details that estimates how much space the advisor can help you reclaimâfor example,
+Storage advisor has action plans to clean up space and manage the environment
+. Select the banner to open the
+Dataverse storage advisor
+panel.
+Clean up column
+: The
+Consumption per table
+grid includes a
+Clean up
+column that shows the estimated space the advisor recommends cleaning up for each table. The environment list in the
+Manage capacit
```

---

### 3. Agent Orchestration

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:cac6211d8e6bdc3b5aad2d9590d4d2f124a565f4b3810e2bc43a21c5907ab049

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

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
@@ -22,6 +22,14 @@ Add tools to custom agents
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 Tools are building blocks that let your agent interact with external systems. Tools expand what your agent can do, letting your agent perform various actions in response to user requests or autonomous triggers. Each tool represents a specific capability that your agent can perform. For example, you can equip your agent with tools that perform tasks like:
 Send emails using the Office 365 Outlook connector
 Check the current weather conditions and forecasts
@@ -54,12 +62,15 @@ : Connect to an MCP server to access tools and resources.
 Computer use
 : Lets your agent interact with any system that has a graphical user interface, for websites and desktop apps, selecting buttons, choosing menus, and entering text into fields on the screen.
-There are two other mechanisms you can use to add tool-like behavior to your agent:
-Skills: Container for a set of related tools.
-Client tool: Send an event activity to the client so that the client carries out an action and returns a response.
-For more information on skills and client tools, see the links in the
-Related content
-section.
+Two other mechanisms you can use to add
+tool-like
+behavior to your agent are:
+Azure Bot Service skills
+: Container for a set of related tools made available through the Azure Bot Service.
+Client tools
+: Send an event activity to the client so that the client carries out an action and returns a response.
+Note
+Skills in the context of the classic agent experience aren't the same as the skills used in coding agents. You can only add co
```

---

### 4. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:06929a9f82e4e1771f3e56d581d8f05781aef6255e65fa84cd9de05c9da29a7d

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

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
@@ -35,13 +35,42 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+June 2026
+(Production-ready preview) Use the new experience in Copilot Studio to build agents. The GitHub Copilot harness uses an enhanced orchestration runtime for improved response quality and reasoning, available alongside the classic experience.
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

### 5. Create Custom MCP Server

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:657a264462edf78cf2a795537f4c6caf86b8fe6cd96a3abcb73c2592cbdfc338

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

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
@@ -22,6 +22,14 @@ Create a new Model Context Protocol (MCP) server
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 You can use
 MCP software development kits (SDKs)
 to set up an MCP server in one of the supported languages.

```

---

### 6. Solution Checker

**URL:** https://learn.microsoft.com/en-us/power-apps/maker/data-platform/use-powerapps-checker
**Section:** Power Apps
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:f7d7f0a65e58ad1b8b1af09df2cfc27bd48fc3043171364b2e5c1709a86018c9

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
@@ -430,51 +430,6 @@ Use Xrm.App.sidePanes.createPane instead of Xrm.Panels.loadPanel.
 Medium
 Upgrade readiness
-Web Resources
-web-sdl-no-cookies
-HTTP cookies are an old client-side storage mechanism with inherent risks and limitations. Use Web Storage, IndexedDB, or other modern methods instead.
-Medium
-Security
-Web Resources
-web-sdl-no-document-domain
-Writes to document.domain property must be reviewed to avoid bypass of same-origin checks. Usage of top level domains such as azurewebsites.net is strictly prohibited.
-Medium
-Security
-Web Resources
-web-sdl-no-document-write
-Calls to document.write or document.writeln manipulate DOM directly without any sanitization and should be avoided. Use document.createElement() or similar methods instead.
-Medium
-Security
-Web Resources
-web-sdl-no-html-method
-Direct calls to method html() often (for example, in jQuery framework) manipulate DOM without any sanitization and should be avoided. Use document.createElement() or similar methods instead.
-Medium
-Security
-Web Resources
-web-sdl-no-inner-html
-Assignments to innerHTML or outerHTML properties manipulate DOM directly without any sanitization and should be avoided. Use document.createElement() or similar methods instead.
-Medium
-Security
-Web Resources
-web-sdl-no-insecure-url
-Insecure protocols such as HTTP or FTP should be replaced by their encrypted counterparts (HTTPS, FTPS) to avoid sending potentially sensitive data over untrusted networks in plaintext.
-Medium
-Security
-Web Resources
-web-sdl-no-msapp-exec-unsafe
-Calls to MSApp.execUnsafeLocalFunction() bypass script injection validation and should be avoided.
-Medium
-Security
-Web Resources
-web-sdl-no-postmessage-star-origin
-Always provide specific target origin, not * when sending data to other windows using postMessage to avoid data leakage outside of trust boundary.
-Mediu
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Monitor Microsoft Copilot Studio
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitor-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:9e8342f529e59001468bbd78383bdb476bc76070d444ddbc44cc680426b99a44

---

### 2. Copilot Studio Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:b66a73113395238d4c6cb312e8749ea6ff44084c40c00dce036b50d51e94d434

---

### 3. Agent Publishing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:28275a9fc67281d34caba48ad2aa06527208212e8fd209be0a52b4501a553ea5

---

### 4. Analytics
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:3a6c68684f1e36b04ba0928200c846dc8533f849e41fec9acef20158c29aeea6

---

### 5. Customer Satisfaction
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8013dd109dbc00073d730c885b83f4fedf4bcf244ec584589fda7de50440c4ce

---

### 6. Connectors
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:12f45f17990ab6b8a16565a96bfcffb083df2649f8ebce9ba8f0b4a4c711b1e0

---

### 7. Quickstart: Create and deploy an agent
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-gpt-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:15bb06e52cf96340ba2ad5c50fb4f459e588c9c588133085feacbd4cfaf95430

---

### 8. Human Agent Handoff
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:476411cee51476906ed80fe44ec774ae8db74dd8094f13de4e927b1adc8b2798

---

### 9. Create Custom MCP Server
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:657a264462edf78cf2a795537f4c6caf86b8fe6cd96a3abcb73c2592cbdfc338

---

### 10. Agent 365 Documentation Hub
**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:db012f4e5b567260111465b28b62f9c9ed1178e6bcd7c9f726360dac2c52b812

---

### 11. Copilot Studio Licensing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:182007aa569e2b88b0a54dd61fbc0fa89d5cd045cf2b4083e386962353d43f5d

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