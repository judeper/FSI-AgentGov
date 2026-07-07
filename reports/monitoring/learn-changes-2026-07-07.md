# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-07
**Run Time:** 2026-07-07T09:43:57.476781+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 6 |
| HIGH Changes | 13 |
| MEDIUM Changes | 7 |
| Redirects | 5 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | CRITICAL | 2.4 | Update portal-walkthrough |
| 2 | ...ower-platform/release-plan/2025wave2/ | HIGH | 1.27 | Review and update |
| 3 | ...ower-platform/release-plan/2026wave1/ | HIGH | 3.8, 2.25, 2.8, 2.17, 2.10, 2.3, 1.4, 1.18 | Review and update |
| 4 | knowledge-copilot-studio | MEDIUM | 2.16, 4.8, 1.14 | Update portal-walkthrough |
| 5 | authoring-test-bot | HIGH | 2.5 | Update portal-walkthrough |
| 6 | whats-new | HIGH | 2.25, 2.5, 2.10 | Review and update |
| 7 | planned-features | CRITICAL | 3.8, 2.25, 2.17, 1.4 | Review and update |
| 8 | ...ring-detecting-credential-oversharing | CRITICAL | 3.8, 2.8, 2.3, 1.18 | Monitor |
| 9 | ...suggestions-based-work-copilot-studio | CRITICAL | None | Monitor |
| 10 | whats-new | HIGH | None | Review and update |
| 11 | overview | HIGH | 3.13, 3.1, 2.25, 2.12, 2.6 | Update portal-walkthrough |
| 12 | insider-risk-management-activities | CRITICAL | 1.12 | Update portal-walkthrough |
| 13 | compliance-manager-assessments | HIGH | 3.3, 2.13 | Review and update |
| 14 | permissions-reference | CRITICAL | 2.23 | Monitor |
| 15 | turn-external-sharing-on-or-off | HIGH | 4.4, 1.3 | Review and update |
| 16 | restricted-access-control | MEDIUM | 4.1, 1.3 | Review optional |
| 17 | restricted-content-discovery | HIGH | 4.7, 4.1, 4.6, 1.3, 1.14 | Review and update |
| 18 | restricted-sharepoint-search | HIGH | 4.7, 4.1, 4.6, 1.3, 1.14 | Review and update |
| 19 | advanced-management | MEDIUM | 4.5, 4.2, 4.1, 4.6, 1.3 | Review and update |
| 20 | site-lifecycle-management | CRITICAL | 4.2, 4.3 | Review and update |
| 21 | request-site-attestations | HIGH | 4.2 | Review and update |
| 22 | ...cident-handling-with-automation-rules | HIGH | 3.9 | Review and update |
| 23 | ai-agent-inventory | HIGH | 3.7, 1.8 | Update portal-walkthrough |
| 24 | whats-new | CRITICAL | None | Monitor |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:051d17c7d8b7cc2fe6c6cf48ca1f8a669b0fd7a09daadd271373fb70a0791fec

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -22,6 +22,8 @@ Business continuity and disaster recovery
 Feedback
 Summarize this article for me
+Note
+As of June 22, 2026, Self-Service Disaster Recovery (SSDR) is also available for Finance & Operations (F&O) applications. SSDR enables organizations to maintain an asynchronous secondary copy of their production environment in a paired Azure region and perform self-service failover, failback, and disaster recovery testing.
 Businesses expect their applications and customer data to be protected and resilient during unavoidable outages and disruptions. It's important to document a business continuity plan that minimizes the effects of outages. To recover and resume operations, make sure the plan lists stakeholders, processes, and specific steps.
 Microsoft provides business continuity and disaster recovery capabilities to all
 production type environments
@@ -101,7 +103,7 @@ Disaster recovery drill
 Emergency response for a major regional outage
 Disaster recovery drills
-Your company might have disaster recovery drills documented as a requirement in your internal business continuity plans. Some industries and companies might be required by government regulations to perform audits on their business continuity disaster recovery capabilities. In these cases, you can run a disaster recovery drill on an environment. A disaster recovery drill lets you do self-service disaster recovery without losing any data. The duration of the failover action can be slightly longer while all remaining data is replicated to the secondary region.
+Your company might document disaster recovery drills as a requirement in its internal business continuity plans. Some industries and companies are subject to government regulations that require audits on their business continuity and disaster recovery capabilities. In these cases, run a disaster recovery drill on an environment. A disaster recovery drill lets you do self-service disaster recovery without losing any data. The duratio
```

---

### 2. Knowledge Sources

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:325112c147a59f97007ede56d84adae2eb6334a379fd6f7a9d478b7d3a9f3138

**Affected Controls:**
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -29,23 +29,6 @@ generative answers node
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
+. For individual generative answers nodes, see
+Authentication
+.
+In addition, you might need to account for
+URL con
```

---

### 3. Test Your Agent

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:90ba14bc75c8a750c552c6efa27d08db2f3b35f0373719a47095c74d375ac89a

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -28,7 +28,7 @@ . Close the activity map if you want to follow through the conversation path step by step with tracking between topics turned on.
 In addition to testing your agent in the
 Test your agent
-panel, you can create test sets of multiple queries for automated testing. For more information, see
+panel, you can create test sets of multiple queries for automated testing. Learn more in
 Create test cases to evaluate your agent (preview)
 .
 Use the test chat
@@ -38,13 +38,14 @@ Use the
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
@@ -64,7 +65,7 @@ to avoid having to collapse the activity map at every conversation turn.
 Continue the conversation until you're satisfied that it flows as intended.
 Tip
-You can update a topic at any time while interacting with the test agent. Save your topic to apply changes and continue the conversation with your agent.
+You can update a topic at any time while interacting with the agent. Save your topic to apply changes and continue the conversation with your agent.
 Your conversation isn't automatically cleared when you save a topic. If you want your agent to forget the test conversation and start over, select the
 Reset
 icon
@@ -79,8 +80,7 @@ on the top menu bar.
 Unless you want to continue an earlier conversation, select the
 Reset
-icon
-at the top of the
+icon at the top of the
 Test bot
 panel to clear the previous conversation. Clearing previous conversations makes it easier to see 
```

---

### 4. Agent 365 Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:6864d51fa8e656954191b64dcc6b7c7bc7e0665a386b076f4001a7b3e531d175

**Affected Controls:**
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -42,7 +42,7 @@ Agent management overview
 .
 Secure
-Microsoft Agent 365 delivers endâtoâend protection for every agent by extending Microsoftâs enterpriseâgrade identity, data, and threatâdefense capabilities across your AI ecosystem. Microsoft Entra enforces consistent, riskâbased access controls for users and agents acting on their behalf, while MicrosoftPurview provides deep visibility into data risks with information protection, DLP, and risk safeguards. Microsoft Defender adds continuous threat detection and realâtime protection to block unsafe behaviors and malicious activity. Together, these capabilities ensure agents only access authorized resources, prevent data leakage, and defend against evolving threats. Learn more:
+Microsoft Agent 365 delivers endâtoâend protection for every agent by extending Microsoftâs enterpriseâgrade identity, data, and threatâdefense capabilities across your AI ecosystem. Microsoft Entra enforces consistent, riskâbased access controls for users and agents acting on their behalf, while Microsoft Purview provides deep visibility into data risks with information protection, DLP, and risk safeguards. Microsoft Defender adds continuous threat detection and realâtime protection to block unsafe behaviors and malicious activity. Together, these capabilities ensure agents only access authorized resources, prevent data leakage, and defend against evolving threats. Learn more:
 Use Microsoft Purview to manage data security and compliance
 ,
 Protect your agents in real-time during runtime

```

---

### 5. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-activities
**Section:** Microsoft Purview
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:7a8879a5bf1da2826190051780653df692361e7ec4529cf97371276e70763bf6

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -37,7 +37,7 @@ Investigate and act on alerts in Insider Risk Management by following these steps:
 Review the dashboards for alerts
 . On the Standard dashboard,
-filter
+filter alerts
 by alert
 Status
 to locate
@@ -49,7 +49,7 @@ filter to view alerts with the highest prioritization.
 Start with the alerts with the highest severity
 .
-Filter
+Filter alerts
 by alert
 Severity
 if needed to help locate these types of alerts.
@@ -70,14 +70,16 @@ is available for the content within the alert, you can review relevant files from SharePoint, Exchange, and OneDrive for Business in Activity explorer to identify false positives, confirm that sensitive data is present, and quickly decide whether the alert warrants escalation.
 Act on the alert
 . You can either confirm and
-create a case
-for the alert or dismiss and resolve the alert.
+create a case for an alert
+or dismiss and resolve the alert.
 You can triage alerts by going to the
 Alert details
 page for an alert in either dashboard. On the
 Alert details
 page, you can review information about the alert. You can confirm the alert and create a new case, confirm the alert and add to an existing case, or dismiss the alert.
-This page also includes the current status for the alert and the alert risk severity level, listed as
+The
+Alert details
+page also includes the current status for the alert and the alert risk severity level, listed as
 High
 ,
 Medium
@@ -107,7 +109,75 @@ You can also use the
 standalone version of Microsoft Security Copilot to investigate Insider Risk Management, Microsoft Purview Data Loss Prevention (DLP), and Microsoft Defender XDR alerts
 .
-Spotlight (preview)
+Alerts (preview)
+The new unified alert experience combines the Triage Agent and classic alert dashboards into a single alerts list page. This unified view lets you manage both classic and agent-triaged alerts from one location, making it easier to investigate and act on alerts without toggling between dashboards.
+The unif
```

---

### 6. Defender for Cloud Apps - AI Inventory

**URL:** https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory
**Section:** Microsoft Defender
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:37f62632bf5a22ed901e664b648d3806998dd066c45d2e770380b6b154256082

**Affected Controls:**
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/3.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.7/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -19,57 +19,136 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Discover and protect AI agents with Microsoft Defender (Preview)
+Discover AI agents and assess security posture using Microsoft Defender
 Feedback
 Summarize this article for me
-Microsoft Defender detects all Copilot Studio custom AI agents in your tenant and provides tools to identify misconfigured or potentially risky agents, and collects data from Copilot Studio for use in
-advanced hunting
+Microsoft Defender lets you discover all of the Microsoft Agent 365 managed agents in your organization and view their configuration details using two experiences in the Microsoft Defender portal:
+Advanced Hunting
+A dedicated AI agent inventory experience
+This inventory includes cloud agents built with Microsoft Copilot Studio, Microsoft Foundry, and
+supported non-Microsoft cloud platforms
+, and
+local AI agents
+discovered on endpoints.
+This article explains how to discover AI agents, assess their security posture, and use the AI agent inventory in the Microsoft Defender portal.
+Prerequisites
+Enable security for AI agents, including the Microsoft 365 app connector. See
+Enable security for AI agents using Microsoft Defender
 .
-Prerequisites
-To enable AI agent inventory and detection, you must:
-Have a Microsoft Agent 365 license
-Until July 1, 2026, you can access the Copilot Studio AI agent inventory and detection without a Microsoft Agent 365 license if you:
-Have a Microsoft Defender for Cloud Apps license
-Opt in to the
-Microsoft Defender for Cloud apps and Defender XDR preview features
-Enable discovery of Copilot Studio AI agents
-After you enable Security for AI, Microsoft Defender automatically discovers all Copilot Studio custom AI agents in your tenant. After discovery, you can view your agents in the
-AI agent inventory
-and use
-advanced hunting
-to investigate potential threats and misconfigurations.
+To discover local AI agents that run on
```

---

## HIGH: Control Review Recommended

### 1. Release Plans

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:5f35d9ed6badd0c219b8a9b754dc0e286d174d9a2b8609e871d346bb8ecb1b9b

**Affected Controls:**
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -40,13 +40,8 @@ and a downloadable
 PDF
 .
-The role-based Copilot offerings features coming in the 2025 release wave 2 have been summarized in a separate
-release plan
-as well as a downloadable
-PDF
-.
 2025 release wave 2 overview
-Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. Microsoft Power Platform today is comprised of: Power Apps, Power Pages, Power Automate, Microsoft Copilot Studio, Microsoft Dataverse and Microsoft Power Platform governance and administration. The 2025 release wave 2 contains hundreds of new features across Power Platform applications, including Power Apps, Power Pages, Power Automate, and Microsoft Copilot Studio, as well as Microsoft Dataverse and Power Platform capabilities for governance and administration.
+Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. Microsoft Power Platform today is comprised of: Power Apps, Power Pages, Power Automate, Microsoft Copilot Studio, Microsoft Dataverse and Microsoft Power Platform governance and administration. The 2025 release wave 2 contains hundreds of new features across Power Platform applications, including Power Apps, Power Pages, and Power Automate, as well as Microsoft Dataverse and Power Platform capabilities for governance and administration.
 Power Apps
 Power Apps
 enables human and agent collaboration. They include an agent feed to supervise the work of agents and extensible built-in agents for common tasks like entering, exploring, visualizing, and summarizing data. Bring business problems to Plan Designer and a team of agents will help you build enterprise solutions that include apps, agents, Power BI reports and more. Vibe-code with the App Agent to create data-connected experiences. Just describe what you need or provide an image, and it will be done!
@@ -56,9 +51,6 @@ Power Automate
 Power Autom
```

---

### 2. Release Plans (2026 Wave 1)

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:1f9f2875fe92808115615704acdac960f131252adb0428ab0a1ef52ebf56e15f

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -40,13 +40,8 @@ and a downloadable
 PDF
 .
-The role-based Copilot offerings features coming in the 2026 release wave 1 have been summarized in a separate
-release plan
-as well as a downloadable
-PDF
-.
 2026 release wave 1 overview
-Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. The 2026 release wave 1 contains hundreds of new features across Power Platform applications, including Power Apps, Power Pages, Power Automate, and Microsoft Copilot Studio, as well as Microsoft Dataverse and Power Platform capabilities for governance and administration.
+Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. The 2026 release wave 1 contains hundreds of new features across Power Platform applications, including Power Apps, Power Pages, and Power Automate, as well as Microsoft Dataverse and Power Platform capabilities for governance and administration.
 Power Apps
 Power Apps
 continues to modernize app experiences with a refreshed model-driven UI, improved mobile and offline capabilities, faster search, and expanded AI features. This release brings standardized modern theming to everyone, real-time Dataverse access for offline-first Canvas apps, enhanced search in grids and lookups, and broader availability and extensibility of generative pages to help teams build and scale intelligent apps faster.
@@ -56,9 +51,6 @@ Power Automate
 Power Automate
 is Microsoft's comprehensive automation platform for cloud flows, desktop flows, and process mining. This release introduces AI agent authoring, optimization, and self-healing capabilities for desktop flows, Copilot Studio-powered actions in cloud flows, enhanced maker and collaboration tools across both, general availability of object-centric process mining, and consolidated governance reporting.
-Microsoft Copilot Studio
-Microsoft Copilot Studio
-c
```

---

### 3. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:0976aa5e8700470f9f8f9217aba749f68699ee969e58726513a15e286ff16fe1

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -35,13 +35,26 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
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
 May 2026
 (General availability)
 Computer use
 is now generally available, letting your agents automate web and desktop apps by controlling browsers and desktop applications on behalf of users.
 Add a
 prompt node
-to an agent flow or workflow to make a single AI call with dynamic content and model selection, useful for scenarios like translation and structured data extraction.
+to an agent flow to make a single AI call with dynamic content and model selection, useful for scenarios like translation and structured data extraction.
 Add a
 Microsoft 365 Copilot node
 to a workflow to send prompts to Microsoft 365 Copilot or a specific agent, enabling automation scenarios like research and audit drafting.
@@ -200,7 +213,7 @@ Microsoft Entra agent identities
 for agents. When turned on, automatically appl
```

---

### 4. Planned Features (2026 Wave 1) [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:352097313ad1542226495ef8ee42bf08fb6306e7177e873b9364a3dd72590c94

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -1,156 +1,507 @@-Table of contents
-Exit editor mode
-Ask Learn
-Ask Learn
-Reading mode
-Table of contents
-Read in English
-Add
-Add to plan
-Edit
-Copy Markdown
-Print
-Note
-Access to this page requires authorization. You can try
-signing in
-or
-changing directories
-.
-Access to this page requires authorization. You can try
-changing directories
-.
-What's new and planned for Microsoft Copilot Studio
-Feedback
-Summarize this article for me
-This topic lists features that are planned to release from April 2026 through September 2026. Because this topic lists features that may not have released yet,
-delivery timelines may change and projected functionality may not be released
-. For more information, go to
-Microsoft policy
-.
-For a list of the previous wave's release plans, go to
-2025 release wave 2 plan
-.
-In the
-General availability
-column, the feature will be delivered within the month listed. The delivery date can be any day within that month. Released features show the full date, including the date of release.
-This check mark (
-) shows which features have been released for public preview and general availability.
-Copilot and AI innovation
-Use industry leading generative AI capabilities in Microsoft Copilot Studio to do the work so you and your team don't have to.
-Feature
-Enabled for
-Public preview
-General availability
-Automate web and desktop apps with computer use
-Admins, makers, marketers, or analysts, automatically
-May 27, 2025
-May 7, 2026
-Give read-only analytics access to users
-Admins, makers, marketers, or analysts, automatically
--
-Apr 28, 2026
-Use code interpreter on SharePoint sources in agent conversations
-Admins, makers, marketers, or analysts, automatically
-Mar 16, 2026
-May 2026
-Define custom metrics for analytics
-Admins, makers, marketers, or analysts, automatically
-Apr 15, 2026
-Jul 2026
-Analyze quality of responses that use generative AI
-Admins, makers, marketers, or analysts, automatically
-Jun 17, 
```

---

### 5. Copilot Studio Kit — Compliance Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:bb0853f3cb9627ce2b7c1f44eb3e678bf626bb42d695647cb0cabbff0a772718

**What Changed:**
```diff
--- +++ @@ -27,6 +27,12 @@ New articles
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

### 6. Assessments

**URL:** https://learn.microsoft.com/en-us/purview/compliance-manager-assessments
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:6a5a8df40ee1f7e428ccd547fad39156f2cdfdfd80ba72490d073790311a4f49

**Affected Controls:**
- Control 3.3: Control 3.3: Compliance and Regulatory Reporting
  - File: `controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md`
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`

**What Changed:**
```diff
--- +++ @@ -68,7 +68,7 @@ : The services covered by the assessment, such as Microsoft 365, Microsoft Azure, or other cloud services.
 Regulation
 : The regulatory template serving as the basis for the assessment.
-To filter your view of assessments:
+To filter your view of assessments, follow these steps:
 Select
 Filter
 at the top-left corner of your assessments list.
@@ -84,8 +84,8 @@ Data protection baseline default assessment
 To get you started, Microsoft provides a default
 Data Protection Baseline
-assessment that's included at all subscription levels. This baseline assessment has a set of controls for key regulations and standards for data protection and general data governance. This baseline draws elements primarily from NIST CSF (National Institute of Standards and Technology Cybersecurity Framework) and ISO (International Organization for Standardization), as well as from FedRAMP (Federal Risk and Authorization Management Program) and GDPR (General Data Protection Regulation of the European Union).
-This assessment is used to calculate your initial compliance score the first time you come to Compliance Manager, before you configure any other assessments. Compliance Manager collects initial signals from your Microsoft 365 solutions. You see at a glance how your organization is performing relative to key data protection standards and regulations, and see suggested improvement actions to take. Compliance Manager becomes more helpful as you build and manage your own assessments to meet your organization's particular needs.
+assessment that's included at all subscription levels. This baseline assessment has a set of controls for key regulations and standards for data protection and general data governance. The Data Protection Baseline assessment draws elements primarily from NIST CSF (National Institute of Standards and Technology Cybersecurity Framework) and ISO (International Organization for Standardization), as well as from FedRAMP (Federal Risk and Autho
```

---

### 7. Manage Sharing Settings

**URL:** https://learn.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off
**Section:** SharePoint Administration
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:bfc58c3ce592d032ed09cea8e8a7cff368f9a605d473cd9f7086496195df18da

**Affected Controls:**
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -52,7 +52,7 @@ Sites
 SharePoint external authentication
 (Microsoft Entra B2B integration not enabled)
-No guest account created*
+No guest account created (see the note following this table)
 Microsoft Entra settings don't apply
 N/A
 (Microsoft Entra B2B always used)
@@ -61,41 +61,43 @@ Microsoft Entra settings apply
 Guest account always created
 Microsoft Entra settings apply
-*A guest account might already exist from another sharing workflow, such as sharing a team, in which case it's used for sharing.
+Note
+A guest account might already exist from another sharing workflow, such as sharing a team, in which case it's used for sharing.
 For information on how to enable or disable Microsoft Entra B2B integration, see
 SharePoint and OneDrive integration with Microsoft Entra B2B
 .
-Video demonstration
-This video shows how the settings on the
+Change organization-level external sharing setting
+In the SharePoint admin center, expand
+Policies
+, and then select
 Sharing
-page in the SharePoint admin center
-affect the sharing options available to users.
-How do I change the organization-level external sharing setting?
-Go to
-Sharing
-in the SharePoint admin center
-, and sign in with an account that has
-admin permissions
-for your organization.
+.
 Under
 External sharing
-, specify your sharing level for SharePoint and OneDrive. The default level for both is
-Anyone
-.
-Note
-The SharePoint setting applies to all site types, including those connected to Microsoft 365 groups and teams. Groups and Teams guest sharing settings also affect connected SharePoint sites.
+, set your sharing level for SharePoint and OneDrive. Keep these points in mind:
+The SharePoint setting applies to all site types, including sites connected to Microsoft 365 groups and teams. Groups and Teams guest sharing settings also affect connected SharePoint sites.
 The OneDrive setting can be more restrictive than the SharePoint setting, but not more permissive.
-This setting is f
```

---

### 8. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:e60e31ed7f9679638df0c93749e9678a765cc390e57e997f4ff711405fc692e5

**Affected Controls:**
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -22,108 +22,142 @@ Restrict discovery of SharePoint sites and content
 Feedback
 Summarize this article for me
-For organizations onboarding to Microsoft 365 Copilot, maintaining strong data governance controls for SharePoint content is critical to deploying Copilot in a safe manner. Sites identified with the highest risk of oversharing can use Restricted Content Discovery to protect content while taking time to ensure that permissions are accurate and well-managed.
-With Restricted Content Discovery, organizations can limit the ability of end users to search for files from specific SharePoint sites. Enabling Restricted Content Discovery for each site prevents the sites from surfacing in organization-wide search and Microsoft 365 Copilot Business Chat, unless a user had a recent interaction.
-Restricted Content Discovery is a site-level setting that needs to be propagated to the search index, a large number of transactions could lead to a long queue in the ingestion pipeline and higher update latency times.
-While child content is hidden by default, users in your organization can still discover files they own or recently interacted with. End users can still find relevant content they need for their day-to-day tasks, even if Restricted Content Discovery is applied to the parent site.
-Restricted Content Discovery doesn't affect searches originating from a site context or other intelligent features such as Microsoft 365 Feed and Recommendations.
+Organizations preparing for Microsoft 365 Copilot often need time to review SharePoint sites, validate permissions, and implement governance controls before making content broadly discoverable. Restricted Content Discovery (RCD) helps you limit discovery of content from specific SharePoint sites while those reviews are taking place.
+When you enable Restricted Content Discovery for a site, content from that site doesn't appear in organization-wide search and Microsoft 365 Copilot experiences unless a user recently 
```

---

### 9. Restricted SharePoint Search

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search
**Section:** SharePoint Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:792e4aaed7734ff68383ad5cd935c61461754266901505587d073a2fd3745e77

**Affected Controls:**
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -23,21 +23,24 @@ Feedback
 Summarize this article for me
 Important
-Restricted SharePoint Search is designed for customers of Microsoft 365 Copilot chat and agentic experiences. It's designed as a short-term solution to allow time for your organization's administrators to thoroughly review and audit site and file permissions, but it's not intended or scalable for long-term use. Comprehensive data security solutions are available, including
+Restricted SharePoint Search is retiring. Starting July 31, 2026, new enablement is blocked. Use comprehensive data controls such as
+Restricted Content Discovery
+(RCD) for content discoverability.
+Restricted SharePoint Search is designed for customers of Microsoft 365 Copilot chat and agentic experiences. It's a short-term solution that gives your organization's administrators time to review and audit site and file permissions. It's not intended or scalable for long-term use. Comprehensive data security solutions are available, including
 SharePoint Advanced Management
 and
 Microsoft Purview
 .
 What is Restricted SharePoint Search?
-Restricted SharePoint Search is a setting that enables you as a
+Restricted SharePoint Search is a setting that you, as a
 SharePoint Administrator
 or
 other Microsoft 365 administrator
-to maintain a list of SharePoint sites (an "allowed list") for which you have checked permissions and applied data governance. The allowed list defines which SharePoint sites can be used in organization-wide search queries, and, as a temporary measure, Copilot chat and agentic experiences.
-By default, the Restricted SharePoint Search setting is turned off and the allowed list is empty. If Restricted SharePoint Search is enabled, users can interact with files and content they own or have previously accessed in Copilot.
+, use to maintain a list of SharePoint sites (an "allow list") for which you check permissions and apply data governance. The allow list defines which SharePoint sites can be used in 
```

---

### 10. Advanced Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8d844f37f1820369dfe2704740bad68bf47e8ec2a603ebcee9a8ab35d17e658b

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -32,6 +32,8 @@ SAM capabilities are helpful as organizations
 prepare for Microsoft 365 Copilot and agents
 .
+Video: SharePoint Advanced Management overview
+Watch the following video to get an overview of SharePoint Advanced Management:
 Administrators primarily manage SAM through the SharePoint admin center. It's designed for SharePoint and Microsoft 365 administrators who are responsible for governance, risk reduction, and audit readiness. You can also use the
 SharePoint Admin Agent
 to make your SharePoint administration more productive and efficient.

```

---

### 11. Site Lifecycle Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/site-lifecycle-management
**Section:** SharePoint Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:6d9c78fed679c44d20a88a1d4f4fa09e266b4e5c5729b1ff5034d4e72395e189

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -19,399 +19,105 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Manage inactive sites by using inactive site policies
+SharePoint site lifecycle management
 Feedback
 Summarize this article for me
-Site lifecycle management capabilities in
+Site lifecycle management policies in
 Microsoft SharePoint Advanced Management
-help you improve site governance by automating the process of detecting inactive sites and notifying site owners by email. Site owners can then review and confirm whether their sites are still active.
-You can configure an inactive sites policy in the SharePoint admin center. This article describes how to set up an inactive site policy with notifications and enforcement actions.
-Prerequisites for an inactive site policy
-See
-SharePoint Advanced Management prerequisites
+help you maintain site governance at scale. These policies automate common governance tasks, so sites stay active, properly owned, and regularly reviewed throughout their lifecycle.
+Video: Overview of SharePoint Advanced Management
+The following video provides an overview of SharePoint site lifecycle management:
+Site lifecycle management policies don't delete SharePoint sites directly. Instead, the policies notify site owners and administrators, and take actions based on how you configure the policies.
+As your organization creates more SharePoint sites, Microsoft Teams-connected sites, and Microsoft 365 group-connected sites, it becomes increasingly difficult for your administrators to manually identify inactive sites, ownerless sites, or sites that no longer meet business requirements. Site lifecycle management policies help you automate these governance processes by monitoring sites, notifying responsible users, collecting responses, and taking enforcement actions when necessary.
+Benefits of site lifecycle management
+Site lifecycle management policies help you:
+Reduce the number of inactive or abandoned sites.
+Identify and ad
```

---

### 12. Site Attestation

**URL:** https://learn.microsoft.com/en-us/sharepoint/request-site-attestations
**Section:** SharePoint Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:ed5b2218870cb928c36b6689e4f801c9414f9ef5cb5a1d1199c9ce77e06ea27e

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**What Changed:**
```diff
--- +++ @@ -22,17 +22,21 @@ Request recurring site attestations for SharePoint sites
 Feedback
 Summarize this article for me
-Site lifecycle management policies in
-Microsoft SharePoint Advanced Management
-help your organization improve site governance. Site attestation involves regular reviews by site owners or site administrators to check and confirm the accuracy of site information, including the site's necessity, its owners, members, permissions, and sharing settings. For sites that remain unattested, you can choose to automate enforcement actions to prevent risks of content overexposure. This approach ensures ongoing site compliance and actively reduces risks such as information oversharing.
-Site attestation policies help you manage periodic attestation of sites at scale. You can configure a site attestation policy in the SharePoint admin center. This article describes how to create and configure a site attestation policy in either active or simulation mode.
+Site attestation policies help you periodically verify that SharePoint sites continue to meet your organization's governance requirements. These policies request reviews from site owners or site administrators, who confirm whether a site is still needed and whether its ownership, membership, permissions, and sharing settings remain appropriate.
+You can configure site attestation policies to send recurring review requests and apply enforcement actions when required reviews aren't completed.
+For an overview of site lifecycle management policies, see
+SharePoint site lifecycle management
+.
+This article describes how to create a site attestation policy with notifications and enforcement actions.
 Requirements for a site attestation policy
 See
 SharePoint Advanced Management prerequisites
 .
-How does a site attestation policy work?
-When a site attestation policy runs (usually on a monthly basis), it generates a report that lists sites requiring attestation according to policy criteria. Site owners and
```

---

### 13. Automation Rules

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/automate-incident-handling-with-automation-rules
**Section:** Azure Services
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:367a5bc9a0ccf71bbd019c496e4a169a057b4684deeded30e01393cd3b8f35c0

**Affected Controls:**
- Control 3.9: Control 3.9: Microsoft Sentinel Integration
  - File: `controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md`

**What Changed:**
```diff
--- +++ @@ -97,6 +97,13 @@ or
 NRT
 analytics rule.
+If your workspace is onboarded to the Microsoft Defender portal, you can also use the
+Case created
+and
+Case updated
+triggers from
+Simple Flows
+(preview) to automate case workflows.
 Incident-based or alert-based automation?
 With automation rules centrally handling the response to both incidents and alerts, how should you choose which to automate, and in which circumstances?
 For most use cases,
@@ -137,7 +144,10 @@ Microsoft security
 analytics rules
 .
-Alert-triggered automation for alerts created by Microsoft Defender XDR is not available in the Defender portal. For more information, see
+In the Defender portal:
+Alert-triggered automation for alerts created by Microsoft Defender XDR isn't available. To automate responses to alerts across Microsoft Sentinel, Microsoft Defender, and XDR platforms, use the
+Enhanced Alert Trigger
+. For more information, see
 Automation in the Defender portal
 .
 Conditions
@@ -316,6 +326,17 @@ Changing the severity of an incident: You can reevaluate and reprioritize based on the presence, absence, values, or attributes of entities involved in the incident.
 Assigning an incident to an owner: This helps you direct types of incidents to the personnel best suited to deal with them, or to the most available personnel.
 Adding a tag to an incident: This is useful for classifying incidents by subject, by attacker, or by any other common denominator.
+If your workspace is onboarded to the Microsoft Defender portal,
+Simple Flows
+(preview) adds more pre-built actions you can use directly from the automation rule wizard, without writing a playbook. Available actions include
+Send Case Created/Updated/SLA Exceeded Email
+,
+Update Case
+,
+Add Task
+, and
+Update Alert
+.
 Also, you can define an action to
 run a playbook
 , in order to take more complex response actions, including any that involve external systems. The playbooks available to be used in an automation rule depend o
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Knowledge Sources
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:325112c147a59f97007ede56d84adae2eb6334a379fd6f7a9d478b7d3a9f3138

---

### 2. Safe Sharing / Credential Oversharing [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/enforce-safe-sharing-detecting-credential-oversharing
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:352097313ad1542226495ef8ee42bf08fb6306e7177e873b9364a3dd72590c94

---

### 3. Agent Suggestions from M365 Copilot [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/get-365-copilot-agent-suggestions-based-work-copilot-studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:352097313ad1542226495ef8ee42bf08fb6306e7177e873b9364a3dd72590c94

---

### 4. Admin Roles
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:f05e85e8992f15c4fa560dcaf0d4526bd043cf512e647a657b54da2c2a376896

---

### 5. Restricted Access Control
**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:94cc652aca870b63e137b79444dbd2cf82a676524bebf05cd03fba0fce7edcd9

---

### 6. Advanced Management
**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8d844f37f1820369dfe2704740bad68bf47e8ec2a603ebcee9a8ab35d17e658b

---

### 7. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:484e57680647218fd0c7b2d700ea8dc0031155560cd610c7994afd734207ddb9

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/enforce-safe-sharing-detecting-credential-oversharing | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/get-365-copilot-agent-suggestions-based-work-copilot-studio | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory | https://learn.microsoft.com/en-us/defender-xdr/security-for-ai/ai-agent-inventory |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*