# Microsoft Learn Documentation Changes

**Run Date:** 2026-05-02
**Run Time:** 2026-05-02T07:46:55.519239+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 6 |
| HIGH Changes | 13 |
| MEDIUM Changes | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | advanced-hand-off | HIGH | 2.12, 2.19 | Update portal-walkthrough |
| 2 | planned-features | HIGH | 1.4, 3.8, 2.25, 2.17 | Review and update |
| 3 | ...rosoft.com/en-us/microsoft-agent-365/ | MEDIUM | 1.7, 3.2, 3.1, 3.14, 3.6, 3.13, 2.12, 2.25, 2.5, 2.6 | Update portal-walkthrough |
| 4 | overview | HIGH | 3.1, 3.13, 2.12, 2.25, 2.6 | Update portal-walkthrough |
| 5 | .../en-us/microsoft-agent-365/developer/ | HIGH | 1.7, 3.2, 3.14, 3.6, 2.5 | Review and update |
| 6 | agent-365-security | HIGH | 3.7, 2.25 | Review and update |
| 7 | dlp-policy-reference | HIGH | None | Review and update |
| 8 | audit-solutions-overview | HIGH | 1.28, 1.27, 1.7, 4.5, 2.13 | Update portal-walkthrough |
| 9 | audit-search | HIGH | None | Review and update |
| 10 | ai-microsoft-purview | HIGH | 1.5, 1.6, 1.16, 4.7, 4.8, 2.6 | Review and update |
| 11 | dspm-for-ai-considerations | HIGH | 1.6 | Review and update |
| 12 | import-hr-data | MEDIUM | 1.12 | Update portal-walkthrough |
| 13 | dlp-configure-endpoint-settings | HIGH | 1.17 | Review and update |
| 14 | permissions-reference | HIGH | 2.23 | Review and update |
| 15 | ...n.microsoft.com/en-us/entra/agent-id/ | HIGH | 1.11, 1.18, 3.11, 2.26, 2.6 | Review and update |
| 16 | agent-id-governance-overview | HIGH | 1.11, 3.6, 2.26 | Review and update |
| 17 | track-and-revoke-admin | HIGH | None | Review and update |
| 18 | get-started-approvals | CRITICAL | 3.10, 3.12, 2.21, 2.16 | Update portal-walkthrough |
| 19 | information-barriers-teams | MEDIUM | None | Review optional |
| 20 | whats-new | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Human Agent Handoff

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)

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
--- +++ @@ -22,8 +22,8 @@ Hand off to a live agent
 Feedback
 Summarize this article for me
-With Copilot Studio, you can configure your agent to hand off conversations to live agents seamlessly and contextually.
-When your agent hands off a conversation, it can share the full history of the conversation, and all relevant variables. With this context, a live agent that uses a connected engagement hub can be notified that a conversation requires a live agent, see the context of the prior conversation, and resume the conversation.
+By using Copilot Studio, you can configure your agent to hand off conversations to live agents seamlessly and contextually.
+When your agent hands off a conversation, it can share the full history of the conversation, and all relevant variables. A live agent that uses a connected engagement hub sees an alert, reviews the conversation history, and continues the conversation.
 For more information about how to configure handoff with
 Omnichannel for Customer Service
 , see
@@ -48,8 +48,8 @@ that, by default, provides a simple message to a user if they ask for a human agent.
 You can edit the topic to include a simple URL to a support website or ticketing system, or to include instructions for emailing or contacting support.
 Prerequisites
-A agent built with Microsoft Copilot Studio
-An engagement hub that is being used by live agents, such as
+An agent built with Microsoft Copilot Studio
+An engagement hub that live agents use, such as
 Omnichannel for Customer Service
 , and you need to configure the connection, as described in
 Configure handoff to Omnichannel for Customer Service
@@ -80,7 +80,7 @@ .
 Trigger handoff to a live agent
 Customers engaging with your agent can ask for a live agent at any point in the conversation. This escalation can happen in two ways, with an implicit trigger or an explicit trigger.
-Upon triggering the handoff topic, the agent starts the handoff to the configured engagement hub, and sends over all conversati
```

---

### 2. Agent 365 Documentation Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC 2011-12/SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -1,6 +1,6 @@ Microsoft Agent 365 documentation
 Agent 365 is the control plane for IT and security leaders to observe, secure, and govern agents across the organization.
-Get early access to Agent 365 for IT admins
+Get Microsoft Agent 365 for IT admins
 Get started with Microsoft Agent 365
 Microsoft Agent 365 allows you to manage all your organizationâs agents at scale, regardless of where these agents are built or acquired.
 What is Agent 365?

```

---

### 3. Agent 365 Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC 2011-12/SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -22,12 +22,6 @@ Overview of Microsoft Agent 365
 Feedback
 Summarize this article for me
-Important
-You need to be part of the
-Frontier preview program
-to get
-early access
-to Microsoft Agent 365. Frontier connects you directly with Microsoftâs latest AI innovations. Frontier previews are subject to the existing preview terms of your customer agreements. As these features are still in development, their availability and capabilities may change over time.
 AI-powered agents are rapidly becoming ubiquitous across enterprises, driving a broad and accelerating transformation. Microsoft Agent 365 provides the ability to
 observe
 ,
@@ -36,119 +30,39 @@ secure
 the growing number of agents within organizations.
 Observe
-Microsoft Agent 365 gives organizations real-time visibility into their agentic environment, helping admins understand how agents are used, identify performance or risk signals early, and take action before issues impact the business. Admins can now view all their agents in a single, centralized registry providing a unified view of agent adoption, activity, and agent health. These insights help leaders and AI admins stay in control, operate efficiently, and maximize the value of their agent investments from a centralized AI admin experience. Learn more:
-Observability
+Microsoft Agent 365 gives organizations real-time visibility into their agentic environment, helping admins understand how agents are used, identify performance or risk signals early, and take action before issues impact the business. Admins can now view all their agents in a single, centralized registry providing a unified view of agent adoption, activity, and agent health. These insights help leaders and AI admins stay in control, operate efficiently, and maximize the value of their agent investments from a centralized AI admin experience. Role-specific oversight extends this visibility to security and business leaders, ensuring the right stakeholders have the tailored in
```

---

### 4. Audit Logging

**URL:** https://learn.microsoft.com/en-us/purview/audit-solutions-overview
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -109,7 +109,7 @@ property (which indicates the service in which the activity occurred) for one year. Retaining audit records for longer periods can help with ongoing forensic or compliance investigations. For more information, see the "Default audit log retention policy" section in
 Manage audit log retention policies
 .
-In addition to the one-year retention capabilities of Audit (Premium), we also released the capability to retain audit logs for 10 years. The 10-year retention of audit logs helps support long running investigations and respond to regulatory, legal, and internal obligations.
+In addition to the one-year retention capabilities of Audit (Premium), Microsoft also released the capability to retain audit logs for 10 years. The 10-year retention of audit logs helps support long running investigations and respond to regulatory, legal, and internal obligations.
 Note
 Retaining audit logs for 10 years requires an additional per-user add-on license. After you assign this license to a user and set an appropriate 10-year audit log retention policy for that user, audit logs covered by that policy start to be retained for the 10-year period. This policy isn't retroactive and can't retain audit logs that were generated before the 10-year audit log retention policy was created.
 Audit log retention policies

```

---

### 5. HR Data Connector

**URL:** https://learn.microsoft.com/en-us/purview/import-hr-data
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -228,7 +228,7 @@ HRScenario
 column to a CSV file (see the next section), you can configure a single HR connector that can process different CSV files.
 For each CSV file, you can ingest up to 500 records at once. To ingest a larger number of records, upload multiple CSV files, each with fewer than 500 records.
-Configuring a single CSV file for multiple HR data types
+Configure a single CSV file for multiple HR data types
 You can add multiple HR data types to a single CSV file. This configuration is useful if the insider risk management solution you're implementing requires multiple HR data types or if the data types are located in a single HR system in your organization. Having fewer CSV files always allows you to have fewer HR connectors to create and manage.
 Here are requirements for configuring a CSV file with multiple data types:
 Add the required columns (and optional columns if you use them) for each data type and the corresponding column name in the header row. If a data type doesn't correspond to a column, leave the value blank.
@@ -252,7 +252,7 @@ Performance improvement plan,pillarp@contoso.com,,,2019-04-23T15:18:02.4675041+05:30,Multiple conflicts with the team,,
 Note
 You can use any name for the column that identifies HR data type because you map the name of the column in your CSV file as the column that identifies the HR data type when you set up the connector in Step 3. You also map the values used for the data type column when you set up the connector.
-Adding the HRScenario column to a CSV file that contains a single data type
+Add the HRScenario column to a CSV file that contains a single data type
 Based on your organization's HR systems and how you export HR data to a CSV file, you might need to create multiple CSV files that each contain a single HR data type. In this case, you can still create a single HR connector to import data from different CSV files. To do this, add an HRScenario column to the CSV file and specify the HR da
```

---

### 6. Approval Workflows

**URL:** https://learn.microsoft.com/en-us/power-automate/get-started-approvals
**Section:** Power Automate
**Classification:** CRITICAL (Deprecation notice)

**Affected Controls:**
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 3.12: Control 3.12: Agent Governance Exception and Override Management
  - File: `controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md`
- Control 2.21: Control 2.21: AI Marketing Claims and Substantiation
  - File: `controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md`
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/3.3/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -74,16 +74,16 @@ Sequential approval
 Approvals are requested one at a time, in a specific order. Each approver must respond before the request moves to the next approver in the sequence. The actions that follow the
 Start and wait for an approval
-action run after all the approvers in the sequence have responded.
+action run after all the approvers in the sequence respond.
 Prerequisites
-If it's the first time you're using approvals in your organization, ensure that you've met the following prerequisites:
+If it's the first time you're using approvals in your organization, ensure that you meet the following prerequisites:
 A Microsoft Dataverse database
 .
 A valid license to create flows
 .
 Permissions to create a Dataverse database
 When you create approval flows, they're saved in Dataverse. Initially, when you use the approvals connector in a cloud flow that's located in a non-default environment, the system automatically provisions a database. To be successful, the user who runs the first approval flow must have an administrator role in the environment.
-It can take a few minutes for the database provisioning to be completed, and you'll notice this delay the first time that you run the flow. Other users who create approval flows don't need any elevated permissions in the environment.
+It can take a few minutes for the database provisioning to be completed. You notice this delay the first time that you run the flow. Other users who create approval flows don't need any elevated permissions in the environment.
 Note
 If you're using the default environment, you don't need to provision the Dataverse database. If you create approval flows, the Dataverse database is created for you automatically in the default environment.
 License to create flows
@@ -115,12 +115,16 @@ to ask specific questions and get answers.
 Assign approvals to any user in your tenant
 You can assign approvals to usersâincluding guest users and Microsoft 365 groupsâin your curren
```

---

## HIGH: Control Review Recommended

### 1. Planned Features (2026 Wave 1) [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

**What Changed:**
```diff
--- +++ @@ -55,7 +55,7 @@ Jul 2026
 Use code interpreter on SharePoint sources in agent conversations
 Admins, makers, marketers, or analysts, automatically
-Mar 2026
+Mar 16, 2026
 May 2026
 Define custom metrics for analytics
 Admins, makers, marketers, or analysts, automatically
@@ -133,16 +133,6 @@ Admins, makers, marketers, or analysts, automatically
 May 2026
 Oct 2026
-Service, runtime, and governance
-Microsoft Copilot Studio continues to meet strict compliance and governance requirements.
-Feature
-Enabled for
-Public preview
-General availability
-Enable express mode for flows invoked by an agent or app
-Admins, makers, marketers, or analysts, automatically
-Nov 17, 2025
-May 2026
 Description of
 Enabled for
 column values:

```

---

### 2. Agent 365 SDK and CLI

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/developer/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**What Changed:**
```diff
--- +++ @@ -22,16 +22,34 @@ Microsoft Agent 365 SDK and CLI
 Feedback
 Summarize this article for me
-Important
-You need to be part of the
-Frontier preview program
-to get
-early access
-to Microsoft Agent 365. Frontier connects you directly with Microsoftâs latest AI innovations. Frontier previews are subject to the existing preview terms of your customer agreements. As these features are still in development, their availability and capabilities may change over time.
+New to Agent 365?
+If you're just getting started, choose the path that fits you best:
+I want to...
+Start here
+Get up and running quickly with AI assistance
+AI-guided setup
+â An AI coding agent (GitHub Copilot, Claude Code, or OpenAI Codex) walks you through installation, configuration, deployment, and publishing from a single instruction file.
+Follow a hands-on example step by step
+Quickstarts
+â pick a sample in your language (Node.js, Python, or .NET) and build a working agent.
+Understand the full workflow before diving in
+Get started with Agent 365 development
+â agent types, phases, setup, and publishing in one guide.
+Understand which type of agent to build
+Types of agents
+â explains the agent types and their identity models.
+Enable Google Vertex AI or Amazon Bedrock agents
+Registration for these agents requires no development work â agents are pulled automatically via the Google and Amazon APIs. No SDK integration, no blueprint, and no code changes are required. Once registered, you can use the Agent 365 SDK to add observability, Work IQ tool access, and other capabilities incrementally. See
+Registering Google Vertex AI and Amazon Bedrock agents
+to get started.
 Agent 365 SDK
 Use the
 Agent 365 SDK
 to extend agents built using any agent SDK or platform, with enterpriseâgrade identity, observability, notifications, security, and governed access to Microsoft 365 data.
+Tip
+Looking for pre-built agents? See
+ecosystem partner agents available in Agent 365
+for age
```

---

### 3. Agent 365 Security Overview

**URL:** https://learn.microsoft.com/en-us/security/security-for-ai/agent-365-security
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -22,65 +22,71 @@ Secure AI agents at scale using Microsoft Agent 365
 Feedback
 Summarize this article for me
-As organizations adopt AI agents to automate workflows and boost productivity, securing these agents has become a critical concern. Unlike traditional applications, AI agents operate autonomously, interact with sensitive data, and execute tasks across multiple systems - making them high-value targets for intentional attacks and also vulnerable to unintentional compromise caused by misconfigurations or excessive permissions.
-Microsoft Agent 365 provides a unified control plane that lets you oversee the security of all AI agents in your organization. It integrates with Microsoftâs security suite - now extended to secure AI agents - to secure agents built in Microsoft Copilot Studio, Microsoft Foundry (formerly called Azure AI Foundry), and third-party solutions.
-This article outlines the core security capabilities that Microsoft Agent 365 provides based on Microsoftâs extended security infrastructure for AI agents.
-For more information about Microsoft Agent 365, see
-Microsoft Agent 365 documentation
-.
-A unified control plane for managing agent security
-Agent 365 integrates with Microsoft 365 Admin Center, giving IT teams a familiar interface to configure policies, apply Conditional Access, and monitor compliance across the agent fleet.
-This control plane provides centralized visibility and lets you drill down into Microsoft's suite of security tools - the same tools you use to manage, secure, and govern users - to manage posture, configure policies, investigate issues, and remediate risks for agents.
-Microsoft security infrastructure extended to AI agents
-Agent 365 extends your existing security and governance practices to AI agents, so teams can use familiar tools and processes without disruption.
-By integrating with Microsoftâs security suite - enhanced with agent-specific controls and capabilities - Agent 365 lets you manage AI 
```

---

### 4. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -19,9 +19,31 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Data Loss Prevention policy reference
 Feedback
 Summarize this article for me
+title: "Data Loss Prevention policy reference"
+f1.keywords: CSH
+ms.author: chrfox
+author: chrfox
+manager: laurawi
+ms.date: [DATE]
+audience: Admin
+ms.topic: reference
+ms.service: purview
+ms.subservice: purview-data-loss-prevention
+search.appverid:
+SPO160
+MET150
+ms.assetid: 6501b5ef-6bf7-43df-b60d-f65781847d6c
+ms.collection:
+highpri
+purview-compliance
+SPO_Content
+recommendations: false
+description: "DLP policy component and configuration reference. This article provides a detailed anatomy of a DLP policy."
+ms.custom: seo-marvel-apr2021
+ai-usage: ai-assisted
+Data Loss Prevention policy reference
 Microsoft Purview Data Loss Prevention (DLP) policies have many components to configure. To create an effective policy, you need to understand what the purpose of each component is and how its configuration alters the behavior of the policy. This article provides a detailed anatomy of a DLP policy.
 Tip
 Get started with Microsoft Security Copilot to explore new ways to work smarter and faster using the power of AI. Learn more about
@@ -1870,7 +1892,7 @@ .ppt, .pptx, .pos, .pps, .pptm, .potx, .potm, .ppam, .ppsx
 The user accessed a sensitive website from Microsoft Edge:
 For more information, see
-Scenario 6 Monitor or restrict user activities on sensitive service domains (preview)
+Help prevent risky user activity by monitoring or restricting access to sensitive service domains
 .
 Insider risk level for Adaptive Protection is:
 Detects the insider risk level.
@@ -2336,7 +2358,7 @@ Detects when protected files are blocked or allowed to be uploaded to cloud service domains. See,
 Browser and domain restrictions to sensitive data
 and
-Scenario 6 Monitor or restrict user activities on sensitive service domains)
+Help prevent risky user activity by monitoring or restrict
```

---

### 5. Search the Audit Log

**URL:** https://learn.microsoft.com/en-us/purview/audit-search
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.23/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -98,7 +98,7 @@ cmdlet to a CSV file, see the "Tips for exporting and viewing the audit log" section in
 Export, configure, and view audit log records
 .
-To programmatically download data from the audit log, we recommend that you use the Office 365 Management Activity API instead of using a PowerShell script. The Office 365 Management Activity API is a REST web service that you can use to develop operations, security, and compliance monitoring solutions for your organization. For more information, see
+To programmatically download data from the audit log, use the Office 365 Management Activity API instead of a PowerShell script. The Office 365 Management Activity API is a REST web service that you can use to develop operations, security, and compliance monitoring solutions for your organization. For more information, see
 Office 365 Management Activity API reference
 .
 Microsoft Entra ID is the directory service for Microsoft 365. The unified audit log contains user, group, application, domain, and directory activities performed in the

```

---

### 6. DSPM for AI

**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC 2011-12/SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -45,12 +45,6 @@ Google Gemini
 Microsoft Copilot (consumer version)
 DeepSeek
-Note
-Now rolling out with the
-Frontier preview program
-data security and compliance protections from Microsoft Purview also support
-Microsoft Agent 365
-. Currently, agent instances are identified and managed like other users.
 For a breakdown of Microsoft Purview security and compliance supported capabilities for AI interactions by app, see the additional pages identified in the following table. Where these AI apps support agents, they inherit the same security and compliance capabilities as their parent AI app. However, for a quick summary, see
 Use Microsoft Purview to manage data security & compliance for AI agents
 .
@@ -73,11 +67,11 @@ If you're new to Microsoft Purview, you might also find an overview of the product helpful:
 Learn about Microsoft Purview
 .
-DSPM for AI (classic) and DSPM (preview)
+DSPM and DSPM for AI (classic)
 Use
+Data Security Posture Management
+or
 Data Security Posture Management for AI (classic)
-or
-Data Security Posture Management (preview)
 as your front door to discover, secure, and apply compliance controls for AI usage across your enterprise. Both DSPM versions use existing controls from Microsoft Purview information protection and compliance management with easy-to-use graphical tools and reports to quickly gain insights into AI use within your organization. With personalized recommendations, and one-click policies help you protect your data and comply with regulatory requirements.
 Microsoft Purview strengthens information protection for AI apps
 Because of the power and speed AI can proactively surface content, generative AI amplifies the problem and risk of oversharing or leaking data. Learn how information protection capabilities from Microsoft Purview can help to strengthen your existing data security solutions.
@@ -187,7 +181,7 @@ After the search is refined, you can export the results or add to a
 review set
 . You can review
```

---

### 7. DSPM Considerations

**URL:** https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`

**What Changed:**
```diff
--- +++ @@ -26,10 +26,10 @@ Note
 This article is for the
 classic
-version of Data Security Posture Management that's being replaced with a new version that expands coverage to more data sources, introduces guided workflows for proactive risk management, and streamlines data security operations so you can more confidently adopt AI across your digital estate.
+version of Data Security Posture Management for AI that's now replaced with a new version that incorporates support for AI apps and agents, new features and broader reach, with simplified management.
 These improvements won't be added to this classic version so we invite you to try the new
 Data Security Posture Management
-, currently in preview.
+.
 For the most part, Data Security Posture Management for AI is easy to use and self-explanatory, guiding you through prerequisites and preconfigured reports and policies. Use this section to complement that information and provide additional details that you might need.
 Prerequisites for Data Security Posture Management for AI
 To use Data Security Posture Management for AI from the Microsoft Purview portal, you must have the following prerequisites:

```

---

### 8. Configure Settings

**URL:** https://learn.microsoft.com/en-us/purview/dlp-configure-endpoint-settings
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -22,14 +22,14 @@ Configure endpoint data loss prevention settings
 Feedback
 Summarize this article for me
-Many aspects of endpoint data loss prevention (DLP) behavior are controlled by centrally configured settings that are applied to all DLP policies for devices. Use these settings to control the following behaviors:
+Centrally configured settings control many aspects of endpoint data loss prevention (DLP) behavior. These settings apply to all DLP policies for devices. Use these settings to control the following behaviors:
 Cloud egress restrictions
 Various types of restrictive actions on user activities per application
 File path exclusions for Windows and macOS devices
 Browser and domain restrictions
 Appearance of business justifications for overriding policies in policy tips
 Whether actions performed on Office, PDF, and CSV files are automatically audited
-To access these settings, from the Microsoft Purview portal, navigate to
+To access these settings, from the Microsoft Purview portal, go to
 Data loss prevention
 >
 Overview
@@ -47,7 +47,7 @@ Microsoft Purview Information Protection Support in Acrobat
 .
 Advanced classification scanning and protection
-Advanced classification scanning and protection allow the Microsoft Purview cloud-based data classification service to scan items, classify them, and return the results to the local machine. Therefore, you can take advantage of classification techniques such as
+When you turn on advanced classification scanning and protection, the Microsoft Purview cloud-based data classification service can scan items, classify them, and return the results to the local machine. Therefore, you can take advantage of classification techniques such as
 exact data match
 classification,
 trainable classifiers
@@ -60,42 +60,42 @@ The
 Paste to browser
 action doesn't support advanced classification.
-When advanced classification is turned on, content is sent from the local device to the cloud services for scanning
```

---

### 9. Admin Roles

**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**What Changed:**
```diff
--- +++ @@ -36,7 +36,7 @@ Manage all aspects of agents in a tenant including identity lifecycle operations for agent blueprints, agent service principals, agent identities, and agentic users.
 db506228-d27e-4b7d-95e5-295956d6615f
 Agent ID Developer
-Create an agent blueprint and its service principal in a tenant. User will be added as an owner of the agent blueprint and its service principal.
+Create an agent identity blueprint and its agent identity blueprint principal in a tenant. User will be added as an owner of the created agent identity blueprint and its agent identity blueprint principal.
 adb2368d-a9be-41b5-8667-d96778e081b0
 Agent Registry Administrator
 Manage all aspects of the Agent Registry service in Microsoft Entra ID
@@ -44,6 +44,9 @@ AI Administrator
 Manage all aspects of Microsoft 365 Copilot and AI-related enterprise services in Microsoft 365.
 d2562ede-74db-457e-a7b6-544e236ebb61
+AI Reader
+Read all aspects of Microsoft 365 Copilot and AI-related enterprise services in Microsoft 365.
+1fe13547-53f6-408d-ac04-7f8eed167b38
 Application Administrator
 Can create and manage all aspects of app registrations and enterprise apps.
 9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3
@@ -93,7 +96,7 @@ Can create and manage the authentication methods policy, tenant-wide MFA settings, password protection policy, and verifiable credentials.
 0526716b-113d-4c15-b2c8-68e3c22b9f80
 Azure DevOps Administrator
-Can manage Azure DevOps policies and settings.
+Manage Azure DevOps policies and settings.
 e3973bdf-4987-49ae-837a-ba8e231c7286
 Azure Information Protection Administrator
 Can manage all aspects of the Azure Information Protection product.
@@ -108,7 +111,7 @@ Can perform common billing related tasks like updating payment information.
 b0f54661-2d74-4c50-afa3-1ec803f12efe
 Cloud App Security Administrator
-Can manage all aspects of the Defender for Cloud Apps product.
+Manage all aspects of the Defender for Cloud Apps product.
 892c5842-a9a6-463a-8041-72aa08ca3cf6
 C
```

---

### 10. Agent ID Overview

**URL:** https://learn.microsoft.com/en-us/entra/agent-id/
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC 2011-12/SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.11/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -5,23 +5,37 @@ Learn about how Microsoft Entra Agent ID and Agent 365 work together so you can observe, govern, and secure agents across your organization.
 Manage agents
 Learn how to manage all aspects of agents in your ecosystem, such as assigning sponsors and requesting access packages.
-How it works
+Manage agent identities
 Govern agent lifecycles
-Ensure the lifecycle of your agents are governed with access reviews, entitlement management, and sponsor accountability.
+Ensure the lifecycle of your agents is governed with access reviews, entitlement management, and sponsor accountability.
 Get started
 Protect agent access to resources
 Apply the same Zero Trust principles and access controls to your agents as you do for your users and workloads.
-Protect agents
+Security for AI overview
 Build on the Microsoft agent identity platform
 Build agents with enterprise-ready identities using the Microsoft agent identity platform.
 Agent identity blueprints
 Define reusable templates for agent identities with preconfigured permissions, policies, and settings.
+AI-guided setup
+Use an AI coding agent to automate the full Agent ID onboarding workflow, from blueprint creation to agent provisioning.
 Microsoft Entra SDK for agents
 Integrate agent authentication and authorization with familiar SDKs and developer tools.
 OAuth protocols for agents
 Understand how agents authenticate and obtain tokens using OAuth 2.0 flows optimized for AI workloads.
+Create an agent blueprint
+Follow step-by-step instructions to create your first agent identity blueprint and provision agent identities.
 Security for AI
-Explore how Microsoft Entra Agent ID integrates with Security for AI to protect your agents
+Explore how Microsoft Entra Agent ID integrates with Security for AI to protect your agents.
+Plan and operate
+Plan your agent identity architecture, follow best practices, and monitor agent activity.
+Plan your agent identity architecture
+Design your agent identity st
```

---

### 11. Governing Agent Identities

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`

**What Changed:**
```diff
--- +++ @@ -19,7 +19,7 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Governing Agent Identities (Preview)
+Governing Agent Identities
 Feedback
 Summarize this article for me
 Microsoft Entra allows you to ensure that the right people have the right access to the right apps and services at the right time. With the addition of the Microsoft agent identity platform, managing the access rights of agents in the same way is just as important in the governance lifecycle of your organization's identities. The Microsoft agent identity platform introduces the concept of Agent Identities (IDs). Agent identities are accounts within Microsoft Entra ID that provide unique identification and authentication capabilities for AI agents.
@@ -27,26 +27,24 @@ License requirements
 Microsoft Entra Agent ID is part of
 Microsoft Agent 365
-. Both are available through the
-Frontier program
-in Microsoft 365. To access these features you must have a license for Microsoft 365 Copilot and have enabled Frontier for your users.
-Follow the
-Frontier getting started guide
-or use the following steps to check if Frontier is enabled:
-Sign in to the
-Microsoft 365 admin center
-as a
-Billing Administrator
+. To use Agent ID features, users need a
+Microsoft Agent 365
+or
+Microsoft 365 E7
+license. All agents acting on behalf of a licensed user are covered under that user's license. Agents don't require their own license. For pricing details, see
+Microsoft Agent 365 licensing FAQ
 .
-Browse to
-Copilot
->
-Settings
->
-User access
->
-Copilot Frontier
-and make sure it's enabled for users. If you don't see these options, contact your administrator to check your Microsoft 365 Copilot licensing.
+Some Microsoft Entra security features for agents require additional licensing:
+Conditional Access for agents
+: Microsoft Entra ID P1 or Microsoft 365 E3.
+ID Protection for agents
+: Microsoft Entra ID P2, Microsoft 365 E5, or Microsoft Entra Suite.
+ID Governanc
```

---

### 12. Track and Revoke Documents

**URL:** https://learn.microsoft.com/en-us/purview/track-and-revoke-admin
**Section:** Azure Services
**Classification:** HIGH (Policy language)

**What Changed:**
```diff
--- +++ @@ -23,7 +23,7 @@ Feedback
 Summarize this article for me
 Document tracking provides information for administrators about when a protected document was accessed. If necessary, both admins and users can revoke document access for tracked documents.
-A document must be registered for tracking before an admin can track access details, including successful access events and denied attempts, and revoke access if needed. See the next section for minimum versions of Office apps for built-in labeling that support file registration the next time they're opened.
+A document must be registered for tracking before an admin can track access details, including successful access events and denied attempts, and revoke access if needed. See the next section for minimum versions of Office apps that support file registration the next time they're opened.
 Note
 Track and revoke features are supported for Office file types only.
 Requirements
@@ -70,7 +70,7 @@ Get-AipServiceDocumentLog
 to search for a document using the filename or the email address of the user who applied protection.
 For example;
-Get-AipServiceDocumentLog -ContentName "test.docx" -Owner âalice@contoso.comâ -FromTime "[DATE] 00:00:00" -ToTime "[DATE] 23:59:59"
+Get-AipServiceDocumentLog -ContentName "test.docx" -Owner "alice@contoso.com" -FromTime "[DATE] 00:00:00" -ToTime "[DATE] 23:59:59"
 This command returns the
 ContentID
 for all matching, protected documents that are registered for tracking.
@@ -101,7 +101,7 @@ Get-AipServiceDocumentLog
 to search for a document using the filename or the email address of the user who applied protection.
 For example:
-Get-AipServiceDocumentLog -ContentName "test.docx" -Owner âalice@contoso.comâ -FromTime "[DATE] 00:00:00" -ToTime "[DATE] 23:59:59"
+Get-AipServiceDocumentLog -ContentName "test.docx" -Owner "alice@contoso.com" -FromTime "[DATE] 00:00:00" -ToTime "[DATE] 23:59:59"
 The data returned includes the ContentID value for your document.
 Tip
 Only docu
```

---

### 13. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -37,6 +37,29 @@ for data governance solutions.
 Roadmap
 for data security and risk and compliance solutions.
+May 2026
+Agent 365
+General availability (GA)
+:
+Data security and compliance protections for Microsoft Agent 365
+.
+Data Security Posture Management
+General availability (GA)
+: The new version of
+Data Security Posture Management
+is now generally available. Partner solutions for non-Microsoft data sources remain in preview, as does the Data Security Posture Agent. This current version provides guided workflows for proactive risk management and streamlines data security operations so you can more confidently adopt AI across your digital estate.
+New
+:
+Support for administrative units
+, to bring parity with the classic versions of DSPM and DSPM for AI.
+New
+: To optimize resources, processing is paused for Microsoft 365 data when tenants are inactive for more than 60 days, and automatically resume when you return to the solution. For more information, see
+Data updates paused for inactive tenants
+.
+New
+: The "Responsible AI FAQ for Data Security Posture Management" is replaced with the more detailed
+Application card for Data Security Posture Management
+to better help you understand this solution's AI capabilities, intended uses, limitations, evaluations, safety components, and best practices.
 April 2026
 Collection Policies
 Preview
@@ -44,16 +67,26 @@ sensitivity labels as a condition
 for scoping detection to items with specific sensitivity labels applied. This condition is supported with browser and network cloud apps detection.
 Data Governance
+In preview
+: Use a one-time
+glossary migration and asset enablement process
+to curate data assets and columns with glossary terms. This process allows you to centralize the management of glossary terms by migrating glossary terms created in the classic governance experience into Unified Catalog. When you complete the process, you can
+curate data assets and columns
+.
+In preview
+: 
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Agent 365 Documentation Hub
**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/
**Classification:** MEDIUM (General content update)

---

### 2. HR Data Connector
**URL:** https://learn.microsoft.com/en-us/purview/import-hr-data
**Classification:** MEDIUM (General content update)

---

### 3. Information Barriers in Teams
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-teams
**Classification:** MEDIUM (General content update)

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*