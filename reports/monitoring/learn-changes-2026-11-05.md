# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-05
**Run Time:** 2026-11-05T14:10:10.591813+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 5 |
| MEDIUM Changes | 4 |
| Redirects | 9 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | MEDIUM | 1.4 | Review and update |
| 2 | power-platform-inventory | HIGH | 3.11 | Review and update |
| 3 | alerts | HIGH | None | Review and update |
| 4 | analytics-improve-agent-effectiveness | HIGH | None | Update portal-walkthrough |
| 5 | whats-new | MEDIUM | 2.5, 2.10, 2.25 | Review and update |
| 6 | copilot-overview | MEDIUM | 3.8 | Review and update |
| 7 | microsoft-365-copilot-privacy | MEDIUM | 4.6, 4.7, 2.23 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Monitor Conversational Agents (Effectiveness)

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:91a5fe89095952dda373a4a6d29bf5f58c8c6ce194663e1a913c7d2ca281fd95

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -53,7 +53,7 @@ [This section is prerelease documentation and is subject to change.]
 The
 Custom metrics
-section lets you define up to three business-specific metrics in natural language and track how often each outcome appears across sampled sessions. Use these metrics to complement your standard analytics insights with indicators that reflect your agent's goals and business use.
+section lets you define up to three business-specific metrics in natural language. Copilot Studio generates classification categories or numeric scoring criteria from your description. Preview uses sample sessions to help you test the metric. After you save it, Copilot Studio calculates the metric for all applicable sessions from the preceding seven days and then calculates it daily for new sessions.
 Important
 This article contains Microsoft Copilot Studio preview documentation and is subject to change.
 Preview features aren't meant for production use and may have restricted functionality. These features are available before an official release so that you can get early access and
@@ -62,9 +62,11 @@ If you're building a production-ready agent, see
 Microsoft Copilot Studio Overview
 .
-Users with the Bot Transcript Viewer privilege can
+If you have the
+Bot Transcript Viewer
+security role, you can select a category or result to
 drill down to a list of customer sessions
-filtered based on the selected segment of the donut chart. Select an individual session to see the reasoning behind the metric and access its transcript.
+. From the session list, you can review the reasoning behind the metric result and open the transcript for an individual session.
 Learn more about creating, testing, and refining metrics in
 Monitor your agent with custom metrics (preview)
 .

```

---

### 2. Data, Privacy, and Security

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Section:** Microsoft 365 Copilot
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e508a58096b8cc866d03b5bece6867b93141d118b7fbcda5a2723b3e48e6ce71

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -43,7 +43,7 @@ blocking prompt injections (jailbreak attacks)
 .
 For information about models provided by Anthropic as a subprocessor within Microsoft Copilot experiences, see
-Anthropic models in Microsoft Online Services
+Claude models from Anthropic in Microsoft Online Services
 .
 For information about models provided by OpenAI as a subprocessor within Microsoft Copilot experiences, see
 OpenAI as a subprocessor in Microsoft Online Services
@@ -80,7 +80,7 @@ Data, privacy, and security for web queries in Microsoft Copilot and Microsoft Copilot Chat
 .
 Microsoft offers third-party AI models in Microsoft Copilot, such as Anthropic and OpenAI models. As an admin, you can decide whether to use these models to power your experiences, and additional terms may apply. Review the following documentation to learn more:
-Anthropic models in Microsoft Online Services
+Claude models from Anthropic in Microsoft Online Services
 and
 OpenAI as a subprocessor in Microsoft Online Services
 .
@@ -122,7 +122,7 @@ . EU traffic stays within the EU Data Boundary while worldwide traffic can be sent to the EU and other countries or regions for LLM processing.
 Note
 Models provided by Anthropic as a subprocessor are currently excluded from the EU Data Boundary. For more information, see
-Anthropic models in Microsoft Online Services
+Claude models from Anthropic in Microsoft Online Services
 .
 Microsoft Copilot and data residency
 Microsoft Copilot is upholding data residency commitments as outlined in the Microsoft Product Terms and Data Protection Addendum. Microsoft Copilot was added as a covered workload in the data residency commitments in Microsoft Product Terms on March 1, 2024.

```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8d56f8187ee73db247c795f51f99b354a012772a5b3c90466b22c9044415f8f2

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -126,6 +126,8 @@ By: Africa's Talking
 AfterShip (Independent Publisher)
 By: Taiki Yoshida
+Agent 365 MCP Server
+By: Microsoft
 Agent SDK
 By: Microsoft
 AgilePoint NX
@@ -942,8 +944,6 @@ By: Microsoft
 Dynamics 365 ERP Analytics MCP
 By: Microsoft
-Dynamics 365 Fraud Protection
-By: Microsoft
 Dynamics 365 MCP Server
 By: Microsoft
 Dynamics 365 Sales Insights
@@ -2020,8 +2020,6 @@ By: Microsoft
 Office 365 Groups Mail
 By: Microsoft
-Office 365 Outlook
-By: Microsoft
 Office 365 Users
 By: Microsoft
 Office 365 Video [DEPRECATED]
@@ -3046,6 +3044,8 @@ By: Microsoft
 Viva Engage
 By: Microsoft
+Viva Insights Agent
+By: Microsoft
 Vocean
 By: Vocean AB
 Voice Monkey (Independent Pubshisher)

```

---

### 2. Power Platform Inventory

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:1fd52355e91d980a8366a8d9a0fb2eef355cd02deb48d43098a135753f615d56

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`

**What Changed:**
```diff
--- +++ @@ -24,7 +24,7 @@ Summarize this article for me
 Power Platform inventory gives tenant administrators a unified view of all agents, apps, and flows built on Power Platform across their organization. Administrators can discover, search, filter, and sort these resources to streamline common administrative tasks.
 By using Power Platform inventory, you can easily complete the following tasks:
-Map connector usage (preview)
+Map connector usage
 : Find which apps, flows, and agents use a given connector or operation. Use this information to scope DLP, audit Premium connector adoption, and plan ahead of deprecations, security issues, or licensing changes.
 Spot your champions
 : Quickly identify who's creating the most resources so you can recognize, nurture, and empower your top innovators.
@@ -41,14 +41,14 @@ Supported resource types
 The Power Platform inventory includes the following resource types:
 Agents
-: All agents you create in Copilot Studio, and all agents you create in Microsoft 365 Copilot Agent Builder.
+: All agents you create in Copilot Studio on the Standard harness or GitHub Copilot harness, and all agents you create in Microsoft 365 Copilot Agent Builder.
 Apps
-: All canvas, model-driven, code, vibe, and
-managed apps
+: All canvas, model-driven, code, and vibe apps, all
+apps built in Copilot managed runtime
 , and all apps you create in Microsoft 365 Copilot's App Builder agent.
 Flows
 : All agent flows you create in Copilot Studio, all cloud flows you create in Power Automate, and all workflows you create in Microsoft 365 Copilot's Workflows agent.
-Connectors (preview)
+Connectors
 : All connectors available in your tenant, including the operations each connector exposes and its publisher and tier.
 Environments
 : All environments in your tenant.
@@ -68,7 +68,7 @@ : Tailor your view by selecting which columns to display.
 Download
 : Export your entire inventory to a CSV file for further analysis.
-Connector visibility (preview)
+Conne
```

---

### 3. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:160bba316e45ce01cf431af122e2933f2ed49bc4604e45269cd422c8f1ed7c83

**What Changed:**
```diff
--- +++ @@ -211,11 +211,310 @@ Save
 .
 After you create your alert, the system runs an on-demand evaluation and scans all the applicable resources under its scope.
+Monitor critical resources with low-latency alerts (preview)
+Use low-latency alerts to evaluate supported resource metrics every hour instead of waiting for the daily evaluation. These alerts can help you detect issues sooner on mission-critical applications and other resources.
+For example, you can create a low-latency alert for a production canvas app to check whether its
+App open success rate
+falls below 95%. The rule evaluates each hour after new hourly metrics are produced and can fire when the condition is met, rather than waiting for the next daily evaluation.
+How low-latency alerts work
+By default, Monitor metrics refresh every 24 hours, and alerts evaluate those metrics after the new 24-hour aggregates are produced. When you create a low-latency alert with
+Data review period
+set to
+1 Hour
+, Monitor enables hourly aggregation for the selected metric on the selected resource. The rule evaluates after new hourly metrics are produced and can fire each hour if its condition is met.
+Hourly aggregation applies only to that resource and metric. It doesn't enable hourly aggregation for every metric on the resource. The product list page and the metric summary on the left side of the resource pane continue to show 24-hour aggregates.
+Hourly alert rules do not perform an on-demand evaluation when it's created since new hourly data isn't available.
+Note
+Low-latency alerts use an hourly refresh and evaluation schedule. They aren't real-time alerts.
+Requirements and limits
+Meet the existing
+alert prerequisites
+, including the admin permissions and managed environment requirements for custom alerts.
+Use
+Resource
+scope. Low-latency alerts aren't available for environment-scoped rules.
+Select a supported product and metric. Supported metrics have a symbol next to them in the
+Metric
+selec
```

---

### 4. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fda81896ed32a1ca1a2d0620422eaa3adec50dec0dabc5992f5cdb59537dcfb4

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -179,7 +179,7 @@ to forecast Copilot credit consumption across Copilot Studio and Dynamics 365 agents before deploying at scale.
 (Preview) Analyze your agent with
 custom metrics
-by defining your own analytics categories and visualizing results alongside built-in analytics.
+by describing a business-specific outcome in natural language. Copilot Studio generates classification or numeric scoring criteria and calculates the results alongside built-in analytics.
 (General availability) Connect agents to other agents using the
 agent-to-agent (A2A) protocol
 .

```

---

### 5. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:9534344750efc9a2ada68ff2b827621be80daec448f4b0183e43189fb2306fa5

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -43,7 +43,7 @@ Anthropic subprocessors are available only in applicable Microsoft 365 licensed experiences and aren't available to all users by default. Anthropic operates with
 Microsoft Enterprise data protections
 . For more information, see
-Anthropic models in Microsoft Online Services
+Claude models from Anthropic in Microsoft Online Services
 .
 Compare Microsoft 365 Copilot licenses
 Copilot Chat (Basic) license
@@ -416,7 +416,7 @@ Anthropic subprocessors are available only in applicable Microsoft 365 licensed experiences and aren't available to all users by default. Anthropic operates with
 Microsoft Enterprise data protections
 . For more information, see
-Anthropic models in Microsoft Online Services
+Claude models from Anthropic in Microsoft Online Services
 .
 Model
 Description

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Connector Reference
**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8d56f8187ee73db247c795f51f99b354a012772a5b3c90466b22c9044415f8f2

---

### 2. What's New
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fda81896ed32a1ca1a2d0620422eaa3adec50dec0dabc5992f5cdb59537dcfb4

---

### 3. M365 Copilot Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:9534344750efc9a2ada68ff2b827621be80daec448f4b0183e43189fb2306fa5

---

### 4. Data, Privacy, and Security
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e508a58096b8cc866d03b5bece6867b93141d118b7fbcda5a2723b3e48e6ce71

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview | https://learn.microsoft.com/en-us/copilot/plan/copilot-overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy | https://learn.microsoft.com/en-us/copilot/plan/microsoft-365-copilot-privacy |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/enable-users | https://learn.microsoft.com/en-us/copilot/adopt/enable-users |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-overview | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-security-governance | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-security-governance |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-management | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-management |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/security/operations/incident-response-planning | https://learn.microsoft.com/en-us/security/zero-trust/security-operations-incident-response-readiness |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*