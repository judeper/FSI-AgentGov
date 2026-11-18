# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-18
**Run Time:** 2026-11-18T15:15:38.997578+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 5 |
| HIGH Changes | 6 |
| MEDIUM Changes | 6 |
| Redirects | 11 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | HIGH | 1.4 | Review and update |
| 2 | environment-strategy | MEDIUM | 2.4 | Review optional |
| 3 | admin-share-bots | HIGH | 2.5, 2.9, 2.6, 3.10, 3.2 | Update portal-walkthrough |
| 4 | analytics-overview | HIGH | 2.5, 2.9, 2.6, 3.10, 3.2 | Update portal-walkthrough |
| 5 | knowledge-copilot-studio | MEDIUM | 2.16, 1.14, 4.8 | Update portal-walkthrough |
| 6 | agent-essentials-overview | HIGH | 2.25 | Review and update |
| 7 | agent-prerequisites | HIGH | 2.25 | Review and update |
| 8 | m365-agents-visual-map | HIGH | 1.1 | Review and update |
| 9 | m365-agents-checklist | HIGH | 1.5, 1.11, 1.1, 1.6, 3.5, 3.1 | Review and update |
| 10 | m365-agents-blueprint | HIGH | 2.3, 2.1, 1.11 | Review and update |
| 11 | information-barriers | MEDIUM | 1.22 | Update portal-walkthrough |
| 12 | pim-configure | HIGH | 2.8, 1.18 | Update portal-walkthrough |
| 13 | message-center | MEDIUM | 2.10 | Review optional |
| 14 | overview-cost-management | MEDIUM | 3.5 | Review optional |
| 15 | plan-designer | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Share and Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:b65a21e925820df6c637ea44a98772b91d6664a6b01073dd2b34bdaa70edcc4b

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -189,6 +189,19 @@ System Administrator
 Dataverse security role so that Copilot Studio can assign the required role to that person on your behalf. If you and your potential coauthor don't have the required security roles, ask your system administrator for assistance.
 If a user isn't already a member of the environment for the shared agent, it can take up to 10 minutes before the agent becomes available in Copilot Studio for this user.
+Giving a user
+Editor
+access to an agent doesn't give them access to AI Builder prompts used by the agent's tools. To give the editor access,
+share the prompt
+with them as a
+User
+or
+Co-owner
+. Alternatively, ask an environment administrator to grant them a Dataverse security role with
+Read
+permission on the
+AI Model
+table at an access level that covers the prompt's specific AI Model record.
 Open the agent you want to share in Copilot Studio.
 On the top menu bar, select the three dots (
 â¦

```

---

### 2. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:f0c85581c24c8676241623f73a33b98f754c65f53e91fa86cdf7924b1b56172c

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.6/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -235,6 +235,49 @@ satisfaction score
 changes over time. Use this trend to identify periods where user sentiment declined or improved.
 To change the time range, select the time range dropdown at the top of the topic Monitor panel.
+Metric refresh rates
+The metrics on the
+Monitor
+page update at different frequencies. The following table shows when updated data becomes available.
+Metric type
+Refresh rate
+Metrics
+General metrics
+Up to two hours
+Sessions
+,
+user questions
+,
+knowledge sources
+,
+tools
+,
+connected agents
+,
+reactions
+,
+session outcomes
+,
+savings
+,
+AI Summary
+AI metrics
+Daily
+Quality of response
+,
+sentiment analysis
+,
+theme classification
+,
+custom metrics
+Theme generation
+Weekly
+Generated themes
+Cost
+A few hours
+Cost consumption
+Note
+Theme classification and theme generation have different refresh rates. New questions are classified into themes daily, while the list of generated themes regenerates weekly.
 Related information
 Measure the return on investment (ROI) and business value of AI agents
 Feedback

```

---

### 3. Knowledge Sources

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:4250f00839478e7a8d6d6f0384e1a050a65e55de9ee9a578818aaa998802ed15

**Affected Controls:**
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -198,6 +198,7 @@ . The agent can then respond by using the model's general knowledge, so its answers aren't always grounded in your knowledge sources.
 How citations appear on different channels
 How citations are shown can vary by channel:
+Depending on the channel, citations might appear as plain, unformatted text instead of linked references.
 Microsoft Teams has stricter limits than other channels. A response shows at most 20 citations; any beyond that are dropped. Each citation's title is limited to about 80 characters and its snippet to about 480 characters, so longer titles or snippets are shortened.
 If you customize the generative answer response, citations aren't added automatically. For example, if you clear a
 Message

```

---

### 4. Information Barriers

**URL:** https://learn.microsoft.com/en-us/purview/information-barriers
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:d92c6618319ebbd702cfd2291caf43890ae2e8fd734dd634e7cc704f99da3dd0

**Affected Controls:**
- Control 1.22: Control 1.22: Information Barriers for AI Agents
  - File: `controls/pillar-1-security/1.22-information-barriers.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.22/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.22/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-2-hardening.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -142,6 +142,9 @@ . When you enable IB policies and enable hierarchical address book, all users not included in an IB segment see the
 hierarchical address book
 in Exchange Online.
+Information Barriers and Agent Builder experience
+Agent Builder provides an easy way to build Declarative agent in Microsoft 365. It offers an immediate, interactive AI development experience that suits quick and straightforward projects.
+Agent builder honors IB policies in the people picker experience. With IB support in Agent builder, when an IB user searches for other users in the people picker, they wonât see users theyâre restricted from communicating and collaborating with per IB policy. This restriction prevents users from conflicting segments to share an agent with each other. Users can continue to access agents that was previously shared with them. However, any new sharing experience via people picker will be allowed only with the users who can collaborate with each other per IB policy.
 Ready to get started?
 Get started with Information Barriers
 : Define segments and create your first IB policies.

```

---

### 5. Privileged Identity Management

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:9c3e83151606f89002797510ae07607c67fb775faea96c4dbd14f23a936bef95

**Affected Controls:**
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/3.3/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -24,6 +24,9 @@ Summarize this article for me
 Overview
 Privileged Identity Management (PIM) is a service in Microsoft Entra ID that enables you to manage, control, and monitor access to important resources in your organization. These resources include resources in Microsoft Entra ID, Azure, and other Microsoft Online Services such as Microsoft 365 or Microsoft Intune. The following video explains important PIM concepts and features.
+PIM also supports eligible and active assignments for application-defined roles through
+PIM for app roles (preview)
+. Users can activate eligible app roles when they need them and deactivate them when they finish.
 Reasons to use
 Organizations want to minimize the number of people who have access to secure information or resources, because that reduces the chance of
 a malicious actor getting access
@@ -33,6 +36,8 @@ Using Privileged Identity Management requires licenses. For more information on licensing, see
 Microsoft Entra ID Governance licensing fundamentals
 .
+PIM for app roles (preview) requires Microsoft Entra ID Governance licenses. Microsoft Entra ID P2 alone isn't sufficient.
+License coverage is required for users with eligible or time-bound app role assignments and for request approvers.
 What does it do?
 Privileged Identity Management provides time-based and approval-based role activation to mitigate the risks of excessive, unnecessary, or misused access permissions on resources that you care about. Here are some of the key features of Privileged Identity Management:
 Provide
@@ -64,6 +69,45 @@ and
 Privileged Role Administrator
 role assignments
+The available capabilities depend on the PIM provider. For the app roles preview's workflows, see
+PIM for app roles (preview)
+.
+Privileged access capabilities in preview
+PIM also includes preview capabilities for role activation, agent access, and privileged sessions. Licensing and setup requirements vary by feature; see the linked guides for prerequisites.
+
```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:f11c4bc816d4a61df63438df8b5d47eb499f5a3de6b88ddfe21519c25ad567dc

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -98,6 +98,8 @@ By: Acumatica
 Address Labs (Independent Publisher)
 By: Richard Wilson
+Adobe Acrobat Knowledge Base
+By: ADOBE INC.
 Adobe Acrobat Sign
 By: ADOBE INC.
 Adobe Acrobat Sign Sandbox
@@ -110,12 +112,16 @@ By: Adobe Acrobat Services
 ADP Employee Self-Service
 By: ADP, Inc.
+ADPÂ® MCP
+By: ADP, Inc.
 Advanced Data Operations
 By: State Solutions
 Advanced Scraper (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 Aexum
 By: Nodefusion d.o.o
+Affinity MCP
+By: Project Affinity, Inc.
 Affirmations (Independent Publisher)
 By: Troy Taylor
 Africa's Talking Airtime
@@ -140,6 +146,8 @@ By: ahead AG
 AI or Not (Independent Publisher)
 By: FÃ¶rdÅs AndrÃ¡s
+AI TeamsMaestro
+By: MailMaestro
 AIForged
 By: Larc AI (PTY) Ltd
 AIHW MyHospitals (Independent Publisher)
@@ -156,6 +164,8 @@ By: airSlate Inc.
 Airtable (Independent Publisher) [DEPRECATED]
 By: Woong Choi
+Akeyless Secrets Manager
+By: Akeyless
 Alemba ITSM
 By: Alemba Ltd
 Alert Relay
@@ -200,10 +210,14 @@ By: ANYRUN FZCO
 Apache Impala [DEPRECATED]
 By: Microsoft
+Apify
+By: Apify
 APITemplate (Independent Publisher)
 By: Troy Taylor
 APlace.io (Independent Publisher)
 By: Troy Taylor
+Apollo
+By: ZenLeads Inc. dba Apollo.io
 App Power Forms
 By: App Power Solutions LLC
 App Store Connect - App Store (Independent Publisher)
@@ -232,6 +246,8 @@ By: Esri, Inc.
 ArcGIS PaaS
 By: Esri, Inc.
+Aria by Convosight
+By: Convosight
 AS2
 By: Microsoft
 Asana
@@ -258,6 +274,8 @@ By: H3 Solutions Inc.
 AtBot Logic
 By: H3 Solutions Inc.
+Audioscrape
+By: Audioscrape Inc.
 Autenti E-Signature Workflow
 By: Autenti sp. z o.o.
 AuthBinder
@@ -384,6 +402,10 @@ By: Microsoft
 Benifex
 By: Benefex Ltd
+BerniePortal
+By: BerniePortal
+Bid Intelligence
+By: Anovatech
 Bigdata-com
 By: RAVENPACK INTERNATIONAL SL.
 BILL Converter by Power2Apps
@@ -464,6 +486,8 @@ By: Blueink
 Bluesky Social (Independent Publisher)
 By: krautrocker
+BoardMark
+By: I C Develop Co., Ltd
 BoldSign
 By: Syncfusion-Inc
 boom
```

---

### 2. Agent Management Essentials Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-essentials-overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:2eaf05576e7841aec40d60e59be432e1c1158f10ac1e52bc390687bca0342370

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -19,100 +19,96 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Agent Management Essentials for Microsoft 365
+Manage agents in the Microsoft 365 admin center
 Feedback
 Summarize this article for me
-The guidance provided within this set of content has been designed to help you view, manage, create, protect, and understand all aspects of agents in Microsoft 365.
-Key aspects of this content include the following topics:
-Prerequisites
-- Understand licensing requirements, admin permissions, and access controls.
-Blueprint
-- Understand how to enable Microsoft Copilot at scale.
-Checklist
-- Understand how to successfully implement and deploy agent governance.
-Visual Guide
-- Follow the guided management paths and links to better understand agents.
-Admin Guide
-- Understand where to start when working with agents in Microsoft 365.
-FAQ
-- Answers to common questions about agents in Microsoft 365.
+Important
+This article is intended for IT administrators.
+The capability is enabled by default in all Microsoft Copilot licensed tenants.
+Microsoft Copilot combines the power of large language models with your data and apps in Microsoft 365. It captures natural language commands to produce content and analyze data. It enables access to and use of other apps, such as Jira,
+Dynamics 365
+, or Bing Web Search.
+You can manage agents for Copilot by using the
+Microsoft 365 admin center
+. You can enable, disable, assign, block, or remove agents for your organization, and manage Copilot capabilities.
 Note
+Researcher and Analyst are first-party Microsoft experiences built on the same foundation as Microsoft Copilot, operating entirely within the Microsoft 365 commercial data processing boundary. These tools inherit all existing security, privacy, and compliance commitments that apply across the suite of Microsoft 365 products. These tools are available in Microsoft Copilot Chat under
+Tools
+and can be invoked by the user an
```

---

### 3. Agent Prerequisites

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-prerequisites
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:2eaf05576e7841aec40d60e59be432e1c1158f10ac1e52bc390687bca0342370

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -19,83 +19,95 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Prerequisites for managing agents in Microsoft 365
+Manage agents in the Microsoft 365 admin center
 Feedback
 Summarize this article for me
-Organizations typically deploy a combination of Microsoft Copilot Chat and Microsoft Copilot. Before you get started, it's important to understand the differences between these two offerings and the licensing involved when deploying and using agents. Agents allow you and your end users to extend Copilot's knowledge, automate complex workflows, and deliver tailored user experiences.
+Important
+This article is intended for IT administrators.
+The capability is enabled by default in all Microsoft Copilot licensed tenants.
+Microsoft Copilot combines the power of large language models with your data and apps in Microsoft 365. It captures natural language commands to produce content and analyze data. It enables access to and use of other apps, such as Jira,
+Dynamics 365
+, or Bing Web Search.
+You can manage agents for Copilot by using the
+Microsoft 365 admin center
+. You can enable, disable, assign, block, or remove agents for your organization, and manage Copilot capabilities.
 Note
-Before your organization assigns or deploys an agent, first consider your organization's objectives, technical requirements, costs, Responsible AI (RAI) considerations, and compliance factors. For more information, see Microsoft Copilot extensibility planning guide.
-Licensing requirements
-Microsoft Copilot Chat
-is available at no additional cost for all Microsoft Entra account users with a Microsoft 365 or Office 365 subscription. Members of your organization can use agents that are available at no additional cost from the Agent Store. You, as the administrator of your organization, would also need to enable these agents. If your organization requires agents that incorporate your organization's data, you can provide access to
-agents
-
```

---

### 4. Visual Governance Guide

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-visual-map
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:2eaf05576e7841aec40d60e59be432e1c1158f10ac1e52bc390687bca0342370

**Affected Controls:**
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`

**What Changed:**
```diff
--- +++ @@ -19,53 +19,96 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Agents governance visual guide for Microsoft 365
+Manage agents in the Microsoft 365 admin center
 Feedback
 Summarize this article for me
-To help understand the structure and flow of the
-Microsoft Copilot Agent Management Essentials checklist
-, you can view the visual guide. This mind map provides a graphical representation of the key concepts and actions outlined in the checklist, making it easier to understand relationships between sections and navigate the framework at a glance.
-Each branch of the mind map corresponds to a major heading in the checklist, with subbranches breaking down detailed steps, considerations, and best practices. By presenting the content visually, the mind map serves as a quick reference tool for planning, implementing, and validating Copilot agents within your organization.
-An image of the relevant portion of the mind map is included in each section of this article. However, to view the entire mind map and access the related links, download the Agents visual guide for Microsoft 365 PDF.
-Download
-:
-Agents visual guide for Microsoft 365 PDF
-Manage Microsoft Copilot agent access and availability policies
-Agent policies refer to the tenant settings you can make as an administrator in Copilot controls within Microsoft 365 admin center. Choose how you manage access to agents, as well as share and publish agents. For more information, see
-Microsoft 365 agents deployment checklist
+Important
+This article is intended for IT administrators.
+The capability is enabled by default in all Microsoft Copilot licensed tenants.
+Microsoft Copilot combines the power of large language models with your data and apps in Microsoft 365. It captures natural language commands to produce content and analyze data. It enables access to and use of other apps, such as Jira,
+Dynamics 365
+, or Bing Web Search.
+You can manage agents for Copilot by 
```

---

### 5. Deployment Checklist

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-checklist
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:2eaf05576e7841aec40d60e59be432e1c1158f10ac1e52bc390687bca0342370

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`

**What Changed:**
```diff
--- +++ @@ -19,275 +19,96 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Microsoft 365 agents deployment checklist
+Manage agents in the Microsoft 365 admin center
 Feedback
 Summarize this article for me
-This checklist is intended to assist admins with the successful deployment of Copilot agent governance. This checklist provides a comprehensive guide to help you understand, set up, manage, and deploy agents.
-Required administrators for the engagement
-:
-Microsoft 365 admin
-- Setup Copilot agent and connectors settings.
-Microsoft Power Platform admin
-- Setup Copilot Studio policies and settings.
-Microsoft 365 Search admin
-- Setup Microsoft 365 Graph connector configurations.
-Microsoft Azure admin
-- Setup Azure subscription configurations.
-Deployment phases
-:
-Downloadable resources
-:
-Agents blueprint for Microsoft 365
-Agents visual guide for Microsoft 365
-Manage Microsoft Copilot agent access and availability policies
-Agent policies refer to the tenant settings you can make as an administrator in Copilot controls within Microsoft 365 admin center. Agent policies relate to the available settings for all agents in your tenant.
-Step
-Task
-Description
-Administrator
-1
-Manage access to agents in Microsoft 365
-Control how your users interact with agents:
-Choose who can access agents
-Choose which type of agents users are allowed to install
-Copilot administrator, SharePoint administrator, Copilot Studio administrator
-2
-Share and publish agents in Microsoft 365
-Agent sharing methods:
-Sideload agents for personal use
-Shared agent with others
-Publish custom agents to your organization
-Submit agents to the marketplace
-Copilot administrator, SharePoint administrator, Copilot Studio administrator
-Choose the right Copilot Studio experience
-As an admin, you can configure and deploy out-of-the-box agents without having to create and publish a new agent. However, when your organization needs to customize Copilo
```

---

### 6. Deployment Blueprint

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-blueprint
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:2eaf05576e7841aec40d60e59be432e1c1158f10ac1e52bc390687bca0342370

**Affected Controls:**
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**What Changed:**
```diff
--- +++ @@ -19,49 +19,96 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Agents deployment blueprint for Microsoft 365
+Manage agents in the Microsoft 365 admin center
 Feedback
 Summarize this article for me
-This deployment blueprint helps you enable agents in
-Microsoft Copilot
-at scale, while ensuring data security and governance, managing access and costs, and measuring adoption and impact.
+Important
+This article is intended for IT administrators.
+The capability is enabled by default in all Microsoft Copilot licensed tenants.
+Microsoft Copilot combines the power of large language models with your data and apps in Microsoft 365. It captures natural language commands to produce content and analyze data. It enables access to and use of other apps, such as Jira,
+Dynamics 365
+, or Bing Web Search.
+You can manage agents for Copilot by using the
+Microsoft 365 admin center
+. You can enable, disable, assign, block, or remove agents for your organization, and manage Copilot capabilities.
 Note
-This blueprint is scoped primarily to agents created in the
-Agent Builder
-experience using the Microsoft Copilot app.
-The primary challenges when enabling agents in Microsoft 365 include the following:
-Security and governance concerns
-- Your organization can address oversharing, data protection, and compliance risks by implementing robust security and governance controls to safely enable agents in Microsoft Copilot.
-Deployment complexity
-- Agents in Microsoft Copilot introduce new admin tools and processes. This guidance can help address user enablement and cost management complexity.
-Visibility and impact gaps
-- By reviewing and acting on agent data, you can better measure success. Agent data can also provide usage to manage costs and help assess business value.
-By addressing these challenges, you can better drive innovation while maintaining security, control, and visibility. This blueprint can help, by providing shorter, 
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Environment Strategy
**URL:** https://learn.microsoft.com/en-us/power-platform/guidance/adoption/environment-strategy
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fe2e7685363c394aa516e02a11893629861412fa6e4c64b8ff3ac8ef6e72f33e

---

### 2. Knowledge Sources
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:4250f00839478e7a8d6d6f0384e1a050a65e55de9ee9a578818aaa998802ed15

---

### 3. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:d92c6618319ebbd702cfd2291caf43890ae2e8fd734dd634e7cc704f99da3dd0

---

### 4. Message Center
**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:65e5f31d4f246b36ac2d28c415ffb5d5d2185ffc622eaff1d099187eee7b8412

---

### 5. Cost Management
**URL:** https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:413e0e581b9fcffedb39ca5bd1a2d7baa56b546ec73ee2f36ab1794a6739fd3e

---

### 6. Testing Guidance
**URL:** https://learn.microsoft.com/en-us/power-apps/maker/plan-designer/plan-designer
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:44685be4871b5d74ec85d20c27ac8b9a390cfe37c7575837b75bf5693ac9c466

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-essentials-overview | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-prerequisites | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-visual-map | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-checklist | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-blueprint | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*