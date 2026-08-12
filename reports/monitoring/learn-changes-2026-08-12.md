# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-12
**Run Time:** 2026-08-12T07:25:41.063913+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 3 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | analytics-improve-agent-effectiveness | HIGH | None | Update portal-walkthrough |
| 2 | whats-new | HIGH | 2.10, 2.25, 2.5 | Review and update |
| 3 | whats-new | HIGH | None | Review and update |
| 4 | create-analytics-rules | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:e43734a10971b30289f14617aaa5027f04dde7324e44555af76d6b8d2d942e40

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
@@ -223,13 +235,24 @@ Reactions
 section shows user feedback gathered from reactions to agent responses. The chart counts the number of times users selected either the thumbs up (positive) or thumbs down (negative) buttons available on each response they received from your agent.
 Note
-Agents published to th
```

---

## HIGH: Control Review Recommended

### 1. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:1fc65a266c5508192c557dc637cd91ff1309de1dddc6f99a10a30b8767263816

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

### 2. Copilot Studio Kit — Compliance Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:fbffa2a6898ab9dbcee41fb9f265d2787c5fb07c425a2bfc10c5b4b4598f2f64

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
@@ -23,10 +23,38 @@ Feedback
 Summarize this article for me
 Get the latest information about what's new and what changed in the Copilot Studio guidance hub.
+August 2026
+New articles
+Manage the AI model lifecycle for Copilot Studio agents
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
@@ -52,7 +80,7 @@ Dunaway, a Texas-based, multidiscipline design, planning, and engineering firm, streamlines city code research with Copilot Studio
 and on how the
 Singapore Civil Defence Force implements digital solutions using Power Platform and Copilot Studio
-Rubrics refinement in Copilot Studio Kit
+Rubrics refinement in Copilot Agent Kit
 Copilot Studio and agent samples
 Connect to custom knowledge sources
 Localize Adaptive Card content
@@ -122,7 +150,7 @@ December 2025
 New articles
 Best practices for planning and creating performance tests for conversational agents
-Define and enforce agent compliance with Copilot Studio Kit Compliance Hub
+Define and enforce agent compliance with Copilot Agent Kit Compliance Hub
 Updated articles
 Configure high-quality instructions for generative orchestration

```

---

### 3. Custom Analytics Rules

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/create-analytics-rules
**Section:** Azure Services
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:d61cc704da7f8734bb4428228366ad4db10dfcc5b701b7e99fedde8fceb970aa

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
@@ -38,9 +38,9 @@ to find and install the recommended rules specific to that recommendation. For more information, see
 SOC optimization usage flow
 .
-This article describes the process of creating an analytics rule from scratch, including using the
+This article explains how to create a Microsoft Sentinel analytics rule from scratch by using the
 Analytics rule wizard
-. It includes screenshots and directions to access the wizard in both the Azure portal and the Defender portal.
+. It includes screenshots and directions for both the Azure portal and the Defender portal.
 Important
 After
 March 31, 2027
@@ -55,7 +55,7 @@ Prerequisites
 You must have the Microsoft Sentinel Contributor role, or any other role or set of permissions that includes write permissions on your Log Analytics workspace and its resource group.
 You should have at least a basic familiarity with data science and analysis and the Kusto Query Language.
-You should familiarize yourself with the analytics rule wizard and all the configuration options that are available. For more information, see
+You should familiarize yourself with the analytics rule wizard and all the configuration options that are available. For more information about how scheduled rules work and their configuration options, see
 Scheduled analytics rules in Microsoft Sentinel
 .
 Design and build your query
@@ -66,7 +66,9 @@ Important
 Make sure that your query returns the
 TimeGenerated
-column, as scheduled analytics rules use it as the reference for the lookback period. This means that the rule only evaluates records where the
+column, as scheduled analytics rules use it as the reference for the lookback period. Because
+TimeGenerated
+serves as the lookback reference, the rule only evaluates records where the
 TimeGenerated
 value falls within the specified lookback window.
 Build and test your queries in t
```

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