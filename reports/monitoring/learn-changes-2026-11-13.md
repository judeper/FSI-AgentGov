# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-13
**Run Time:** 2026-11-13T14:04:46.617580+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 6 |
| HIGH Changes | 5 |
| MEDIUM Changes | 8 |
| Redirects | 8 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | HIGH | 1.4 | Review and update |
| 2 | power-platform-inventory | MEDIUM | 2.7, 3.11 | Update portal-walkthrough |
| 3 | ...pilot-studio-copilot-credits-capacity | HIGH | 2.27 | Update portal-walkthrough |
| 4 | capacity-storage | HIGH | 3.5 | Review and update |
| 5 | fundamentals-what-is-copilot-studio | MEDIUM | 2.13 | Review optional |
| 6 | sensitivity-label-copilot-studio | MEDIUM | 1.26 | Update portal-walkthrough |
| 7 | ...ication-fundamentals-publish-channels | MEDIUM | 2.3, 1.28 | Update portal-walkthrough |
| 8 | add-tools-custom-agent | MEDIUM | 2.17 | Review optional |
| 9 | whats-new | CRITICAL | 2.10, 2.5, 2.25 | Review and update |
| 10 | sec-gov-intro | MEDIUM | 3.8 | Review optional |
| 11 | whats-new | HIGH | None | Review and update |
| 12 | plan-agent-model-lifecycle | MEDIUM | 2.6 | Update portal-walkthrough |
| 13 | overview | HIGH | 2.12, 2.6, 2.25, 3.13, 3.1 | Update portal-walkthrough |
| 14 | permissions-reference | HIGH | 2.23 | Review and update |
| 15 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Power Platform Inventory

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:bdeeda3131d59a8a0f98f6c437d98b63e45fa6ea479f5bd8a49c1827bf35f1e7

**Affected Controls:**
- Control 2.7: Control 2.7: Vendor and Third-Party Risk Management
  - File: `controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md`
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.7/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -41,7 +41,7 @@ Supported resource types
 The Power Platform inventory includes the following resource types:
 Agents
-: All agents you create in Copilot Studio on the Standard harness or GitHub Copilot harness, and all agents you create in Microsoft 365 Copilot Agent Builder.
+: All agents you create in Copilot Studio on the Standard harness or Microsoft Copilot harness, and all agents you create in Microsoft 365 Copilot Agent Builder.
 Apps
 : All canvas, model-driven, code, and vibe apps, all
 apps built in Copilot managed runtime
@@ -265,7 +265,7 @@ .
 Connector inventory makes common admin workflows query-driven: identifying every resource affected by a deprecated connector, tracking Premium connector adoption for license decisions, scoping DLP policies to actual usage patterns, and reviewing a resource's full connector footprint during troubleshooting.
 Supported resource types
-: canvas apps, model-driven apps, apps built in Copilot managed runtime, cloud flows, agent flows, workflow agent flows, Copilot Studio agents on the Standard harness or GitHub Copilot harness, and agents created in Microsoft 365 Copilot Agent Builder.
+: canvas apps, model-driven apps, apps built in Copilot managed runtime, cloud flows, agent flows, workflow agent flows, Copilot Studio agents on the Standard harness or Microsoft Copilot harness, and agents created in Microsoft 365 Copilot Agent Builder.
 For flows, the inventory additionally captures the trigger connector and trigger operation that initiate the flow.
 For the data shape and known limitations, see
 Connector inventory
@@ -306,7 +306,7 @@ Yes
 Yes
 No
-Agents with the GitHub Copilot harness
+Agents with the Microsoft Copilot harness
 No
 No
 No

```

---

### 2. Copilot Studio Copilot Credits Capacity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-copilot-credits-capacity
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:044bd4f0a6ef4b653e586e33c943d77548ae7d9f56790bdb7a303f99661a2806

**Affected Controls:**
- Control 2.27: Control 2.27: Consumption-Entitlement Governance
  - File: `controls/pillar-2-management/2.27-consumption-entitlement-governance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.27/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -172,7 +172,7 @@ Agent flow actions
 feature in the
 Copilot credit consumption details
-grid. Agents powered by the GitHub Copilot harness can also be referred to as Process Agents in the Power Platform admin center licensing report. When the environment has no Copilot Credits available, new agent flow runs are blocked while the parent agent continues to function for non-flow interactions. Flow authors also see a design-time warning in the Copilot Studio designer. To resolve enforcement, reallocate capacity, purchase more credits, or
+grid. Agents powered by the Microsoft Copilot harness can also be referred to as Process Agents in the Power Platform admin center licensing report. When the environment has no Copilot Credits available, new agent flow runs are blocked while the parent agent continues to function for non-flow interactions. Flow authors also see a design-time warning in the Copilot Studio designer. To resolve enforcement, reallocate capacity, purchase more credits, or
 enable pay-as-you-go billing
 . For more information, see
 Agent flow enforcement
@@ -332,8 +332,8 @@ How tokens are counted for reasoning models
 . For the rate of each feature, see
 Billing rates and management
-. For agents powered by the GitHub Copilot harness, see
-Overview of billing for agents powered by the GitHub Copilot harness
+. For agents powered by the Microsoft Copilot harness, see
+Overview of billing for agents powered by the Microsoft Copilot harness
 .
 Why should I use a pay-as-you-go plan?
 Pay-as-you-go plans provide these benefits:

```

---

### 3. Sensitivity Labels in Copilot Studio

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b587d9599a063cf46f9fcec4d503d44e3169568f8445bd835271d56d3094e27c

**Affected Controls:**
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.26/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.26/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.26/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -27,7 +27,7 @@ Azure Bot Service skills
 , a code-based way to extend the capabilities of an agent in the standard harness. These skills shouldn't be confused with
 agentic skills
-in the GitHub Copilot harness. Learn more about how to use agentic skills in
+in the Microsoft Copilot harness. Learn more about how to use agentic skills in
 Skills overview for agents
 .
 By using Copilot Studio, you can quickly create and deploy high-value agents for your users that connect to many data sources and services. Some of these sources and services might be external, non-Microsoft services. They might even include social networks, alongside connections to your organizational data.

```

---

### 4. Agent Publishing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:739f41c1fbb978936696955c071f9ad7354068d3637270e12d5c40f0f1278c06

**Affected Controls:**
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.3/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -31,7 +31,7 @@ Azure Bot Service skills
 , a code-based way to extend the capabilities of an agent in the standard harness. These skills shouldn't be confused with
 agentic skills
-in the GitHub Copilot harness. Learn more about how to use agentic skills in
+in the Microsoft Copilot harness. Learn more about how to use agentic skills in
 Skills overview for agents
 .
 By using Copilot Studio, you can publish agents that engage with your customers on multiple platforms or channels. For example, live websites, mobile apps, Microsoft Copilot, and messaging platforms like Teams and Facebook.

```

---

### 5. Manage the AI model lifecycle for Copilot Studio agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:043d856b70905f20b2b6d56c85b5c4d009bb0264c0187d488b97f409512b892b

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.6/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.6/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.6/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -273,7 +273,7 @@ The configured model and its release tag.
 Whether the agent uses the default model or a specific selected model.
 Cross-geo processing requirement and regional constraints.
-Whether the agent is powered by the standard harness or the GitHub Copilot harness, which determines the evaluation test methods available to it. Learn more about
+Whether the agent is powered by the standard harness or the Microsoft Copilot harness, which determines the evaluation test methods available to it. Learn more about
 Copilot Studio harnesses
 .
 The regression test set location and the date of the last baseline run.

```

---

### 6. Agent 365 Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:78d041da78974340f69f9d6ec423fdd364d0a7cf39cef39a6705142c1eacef39

**Affected Controls:**
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -22,31 +22,56 @@ Overview of Microsoft Agent 365
 Feedback
 Summarize this article for me
-AI-powered agents are rapidly becoming ubiquitous across enterprises, driving a broad and accelerating transformation. Microsoft Agent 365 provides the ability to
-observe
+AI agents are quickly becoming part of everyday work. Microsoft Agent 365 is the observability platform for AI. It gives you one view of the agents in your organization, including agents from Microsoft and from other companies. Your IT, security, and business teams see the same information, each in the tools they already use.
+Agent 365 is built on four pillars:
+management
 ,
-govern
+governance
+,
+security
 , and
-secure
-the growing number of agents within organizations.
-Observe
-Microsoft Agent 365 gives organizations real-time visibility into their agentic environment, helping admins understand how agents are used, identify performance or risk signals early, and take action before issues impact the business. Admins can now view all their agents in a single, centralized registry providing a unified view of agent adoption, activity, and agent health. These insights help leaders and AI admins stay in control, operate efficiently, and maximize the value of their agent investments from a centralized AI admin experience. Role-specific oversight extends this visibility to security and business leaders, ensuring the right stakeholders have the tailored insights they need to manage risk and measure agent value within their domains. Learn more:
+business value
+.
+Management
+Management helps you see and run all your agents from one place.
+The agent registry in the Microsoft 365 admin center lists the agents in your organization. It includes agents from Microsoft, from partners, and from your own teams. For each agent, you can see who owns it, how much people use it, and whether it has any risks.
+You can also bring in agents that you built on other platforms. Agent Map shows your agents on a visua
```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:ef1174bed73eff351a56d2d2e110872f3069ff19ad387fb532be9e14402b2504

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

### 2. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:6ee133f1815aa4ea2c7ab2d3e214049768d41541df7e3e463e780be703800a2c

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

**What Changed:**
```diff
--- +++ @@ -19,9 +19,37 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Dataverse capacity-based storage details
 Feedback
 Summarize this article for me
+---1
+title: Dataverse capacity-based storage details
+description: Learn about the Microsoft Dataverse capacity-based storage model.
+ms.date: [DATE]
+ms.topic: concept-article
+author: amiyapatr
+ms.subservice: admin
+ms.author: ampatra
+ms.reviewer: ellenwehrle
+search.audienceType:
+admin
+contributors:
+rijoshi1
+olegovanesyan
+ianceicys-msft
+amiyapatr-zz
+pnghub
+marianaraujo
+EllenWehrle
+ms.contributors:
+ceian
+ampatra
+maraujo
+swatim
+ms.custom:
+NewPPAC
+sfi-ga-nochange
+ai-usage: ai-assisted
+Dataverse capacity-based storage details
 If you purchased storage after April 2019, or if you have a mix of storage purchases made before and after April 2019, you see your storage capacity entitlement and usage by database, file, and log as it appears in the Microsoft Power Platform admin center today.
 Data volume continues to grow exponentially as businesses advance their digital transformation journey and bring data together across their organizations. Modern business applications need to support new business scenarios, manage new data types, and help organizations with the increasing complexity of compliance mandates. To support the growing needs of today's organizations, data storage solutions need to evolve continuously and provide the right solution to support expanding business needs.
 Note
@@ -564,16 +592,16 @@ Review growth and begin remediation.
 Stage 1: Restricted
 The tenant first exceeds 100% effective consumption (time zero, or T0).
-Critical notifications appear. Environment create, copy, restore, and recover operations are blocked.
+Critical notifications appear. Environment create, copy, restore, convert, recover and add Dataverse to an environment operations are blocked.
 Free storage, archive eligible data, add capacity, configure pay-as-you-go billing,
```

---

### 3. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:1680f18f369c254fed1fd912be8dd1388419b664d77f057afce030844621e382

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -31,6 +31,58 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+October 2026
+(Preview) Build agents powered by the new
+Customer Conversation harness
+to handle customer-facing conversations over speech and chat, with specialized sub-agents that can escalate unresolved issues to a human representative, similar to a contact center. Start
+building from Copilot Studio or the Microsoft Contact Center Intelligence portal
+âboth use the same authoring experience, but only the portal lets you connect the agent to a live contact center. Agents on this harness use Copilot Credits for usage-based billing.
+Control which
+knowledge sources
+makers can add to their agents from the Power Platform admin center. Restrict access to local file uploads, SharePoint and OneDrive, or public websitesâindependently or togetherâto match your organization's data governance policies.
+(General availability) Use
+Work IQ
+, now added by default to every new agent powered by the Microsoft Copilot harness, to ground your agent's responses in real-time context from your organization's files, emails, meetings, and chats. Write operations are enabled by default, subject to your organization's permissions and policies.
+Keep your agent on its current AI model for up to 30 days after Copilot Studio
+upgrades it to a new default
+, giving you time to test and migrate before support for the retired model ends.
+Connect MCP-compatible tools, like Visual Studio Code and GitHub Copilot CLI, to
+Copilot Studio MCP
+so you can create, test, deploy, and monitor your agents and workflows without leaving the tool you already use.
+(Preview) Ask Copilot Studio to
+upgrade an agent
+from the standard harness to the Microsoft Copilot harness. The upgrade carries over instructions, tools, and prompts, rebuilds topics as skills or
```

---

### 4. Copilot Studio guidance hub — What's new

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:838dc73f10cdcd8e4552925bb4d37232e8a9d64f721df2a198915f52d54e2de9

**What Changed:**
```diff
--- +++ @@ -26,6 +26,9 @@ November 2026
 New articles
 Design reliable agentic loops
+Other updates
+New reference architecture in the Power Platform and Copilot Studio Architecture Center:
+Build a multilingual IT self-service agent with Copilot Studio
 October 2026
 New reference architecture in the
 Power Platform and Copilot Studio Architecture Center
@@ -35,7 +38,7 @@ September 2026
 New articles
 Compare Copilot Studio agent harnesses
-Govern Copilot Credit consumption for agents powered by the GitHub Copilot
+Govern Copilot Credit consumption for agents powered by the Microsoft Copilot harness
 Updated articles
 Plan Copilot Studio agent deployments for throughput and rate limits
 : Added guidance for running a

```

---

### 5. Admin Roles

**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:aabb6f9eda08833855c058505ae3b5902f92802abaccaa832d9d67cf6021d397

**Affected Controls:**
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**What Changed:**
```diff
--- +++ @@ -345,6 +345,15 @@ Reports Reader
 Can read sign-in and audit reports.
 4a5d8f65-41da-4de4-8968-e035b65339cf
+Resource Policy Administrator
+Can manage resource policy definitions, assignments, tenant-wide configuration, and evaluation.
+c0c46a03-c257-4f91-ab71-3c7e59c89d97
+Resource Policy Evaluator
+Can evaluate a supplied resource policy without reading or changing policy definitions or assignments.
+1dae4b79-8aea-40ab-9ad0-30d3ab1fa9c1
+Resource Policy Reader
+Can read resource policy definitions, assignments, and tenant-wide configuration, and evaluate policies without making changes.
+311877b7-9a2e-4337-81c2-068a250eaa22
 Search Administrator
 Can create and manage all aspects of Microsoft Search settings.
 0964bb5e-9bdb-4d7b-ac29-58e794862a40
@@ -4530,6 +4539,56 @@ Read Office 365 usage reports
 microsoft.office365.webPortal/allEntities/standard/read
 Read basic properties on all resources in the Microsoft 365 admin center
+Resource Policy Administrator
+Users with this role can create, read, update, and delete resource policy definitions and assignments in Microsoft Graph. They can also read and update tenant-wide resource policy configuration and evaluate policies.
+Actions
+Description
+microsoft.directory/resourcePolicy/assignments/basic/update
+Update resource policy assignments basic properties.
+microsoft.directory/resourcePolicy/assignments/create
+Create resource policy assignments.
+microsoft.directory/resourcePolicy/assignments/delete
+Delete resource policy assignments.
+microsoft.directory/resourcePolicy/assignments/standard/read
+Read resource policy assignments standard properties.
+microsoft.directory/resourcePolicy/configuration/basic/update
+Update basic properties of the tenant-wide resource policy configuration, such as the privileged-read app ID.
+microsoft.directory/resourcePolicy/configuration/standard/read
+Read standard properties of the tenant-wide resource policy configuration, such as the privileged-read app ID.
+microsof
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Power Platform Inventory
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:bdeeda3131d59a8a0f98f6c437d98b63e45fa6ea479f5bd8a49c1827bf35f1e7

---

### 2. Copilot Studio Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:31e7e67fb42c13343dfa8ee31851931cbe8357ad0835d3fd7d1d852a252061f1

---

### 3. Sensitivity Labels in Copilot Studio
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b587d9599a063cf46f9fcec4d503d44e3169568f8445bd835271d56d3094e27c

---

### 4. Agent Publishing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:739f41c1fbb978936696955c071f9ad7354068d3637270e12d5c40f0f1278c06

---

### 5. Add Tools to Agents
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6eef4493e060deed21d36f3659060d63d0489fe5a1321453f234ea5611390c9b

---

### 6. Governance Guidance
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/sec-gov-intro
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:442296b666127ed224e112299bd8e6efca71ac87137bdfb0363347cf4042c5f3

---

### 7. Manage the AI model lifecycle for Copilot Studio agents
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:043d856b70905f20b2b6d56c85b5c4d009bb0264c0187d488b97f409512b892b

---

### 8. Copilot Studio Licensing (Get Access)
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:7a42fb36c4ecd63a560260d830d7ee1fec6f72b1e54c45d382ace23ec9ae1b69

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio | https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*