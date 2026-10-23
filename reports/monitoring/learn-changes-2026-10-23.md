# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-23
**Run Time:** 2026-10-23T11:09:53.599393+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | fundamentals-what-is-copilot-studio | HIGH | 2.13 | Review and update |
| 2 | analytics-overview | HIGH | 3.10, 3.2, 2.5, 2.9, 2.6 | Update portal-walkthrough |
| 3 | analytics-improve-agent-effectiveness | CRITICAL | None | Update portal-walkthrough |
| 4 | whats-new | CRITICAL | 2.25, 2.5, 2.10 | Review and update |
| 5 | .../en-us/microsoft-agent-365/developer/ | CRITICAL | 3.6, 3.14, 3.2, 1.7, 2.5 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:8917cef5c18a48d77c3f50420c4f16031b2f65549fd7d3547f07453c02a7ce79

**Affected Controls:**
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -19,7 +19,7 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Monitor overview
+Monitor agent performance in Copilot Studio
 Feedback
 Summarize this article for me
 Note
@@ -29,7 +29,7 @@ Use analytics to understand how well your agent is performing and to identify areas for improvement.
 The
 Monitor
-page in Copilot Studio shows you comprehensive data for your agent, from an overview of key metrics to in-depth usage analytics for your agent's components. You can drill down into each piece of data to get more details.
+page in Copilot Studio summarizes key metrics and provides usage analytics for your agent's components. Open individual metrics to explore the underlying data.
 The Monitor experience is tailored for
 conversational agents
 and for
@@ -43,15 +43,15 @@ test panel
 .
 Grant limited view-only access to analytics
-If you're the agent owner and want to grant access only to the
-Monitor
-page of your agent, you can do so by sharing the agent with the
+If you're the agent owner, share the agent with the
 Analytics Viewer
-sharing role enabled. If you want the person you're sharing the agent with to have access to information from the conversation transcript, they must also have the
+sharing role to grant access only to its
+Monitor
+page. To access conversation transcript information, the person must also have the
 Bot Transcript Viewer
 security role.
-Learn more about
-sharing an agent's analytics
+Learn more in
+Share an agent's analytics
 .
 Important
 As an agent owner, you can only share the Analytics viewer role with individuals and not with groups of users.
@@ -68,32 +68,44 @@ area uses Copilot to generate an AI summary of key analytics insights about your agent. Select
 View More
 to see the full summarized list of insights.
-It helps you quickly understand common themes and metrics and identify areas for improvement for your agent by summarizing them in a bulleted list for the selected reporting perio
```

---

### 2. Monitor Conversational Agents (Effectiveness)

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:ff0688066e1ebe13631859c3fffe430e27496fca429a1b5913d287cb082d042d

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -19,35 +19,29 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Monitor conversational agents
+Monitor conversational agent effectiveness
 Feedback
 Summarize this article for me
 Note
 This article describes features used in agents or agent flows powered by the
 standard harness
 .
-The
+Use the
 Monitor
-page in Copilot Studio provides an aggregated insight into the overall effectiveness of your agent across
+page in Copilot Studio to review your conversational agent's effectiveness across
 analytics sessions
-. The page is divided into core areas that focus on different performance contexts. The page also displays an
+. Identify where conversations succeed or break down, review user feedback, and find opportunities to improve answers and tool use.
+Review the following areas:
+The
+Summary
+,
 Overview
-area that provides high-level, key performance indicator (KPI) metrics for your agent, a
+, and
 Savings
-area that displays time and cost savings attributable to your agent or your agent's tools, and a
-Summary
-area that provides key analytic insights into your agent's performance.
-There are four core sections to focus on when reviewing and improving conversational agent effectiveness.
-The
-Summary
-,
-Overview
-, and
-Savings
-section shows key insights about your agents along with billing and cost savings statistics.
-The
-Custom metrics
-section lets you define business-specific metrics for your agents use cases.
+areas show key insights, key performance indicators (KPIs), and estimated time and cost savings.
+The
+Custom metrics (preview)
+section lets you define business-specific metrics for your agent's use cases.
 The
 Effectiveness
 section helps you evaluate the quality of user experiences by showing where conversations succeed, where they break down, and how users feel about outcomes.
@@ -55,15 +49,24 @@ Use
 section helps you improve operational performance by showing how well your agent answers question
```

---

## HIGH: Control Review Recommended

### 1. Copilot Studio Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:57493a625032a9a92ab0613e61a6c55a9968d404dea6b5a6043310e2f9545ed4

**Affected Controls:**
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`

**What Changed:**
```diff
--- +++ @@ -54,9 +54,6 @@ GitHub Copilot harness
 for reasoning-heavy, multi-step work and complex business processes.
 The
-Copilot chat harness
-for extending Microsoft Copilot Chat with your organization's knowledge.
-The
 Customer Conversation harness
 for agents that answer questions and resolve issues for customers over voice and chat.
 The
@@ -72,9 +69,6 @@ On the
 GitHub Copilot harness
 , what you build reasons from the instructions and knowledge you provide. It interprets the request, chooses the right tools, and works through the steps needed to complete the task, so you don't have to script every path. You can build agents and workflows powered by the GitHub Copilot harness.
-The
-Copilot chat harness
-connects your enterprise knowledge to Microsoft Copilot Chat. Employees get answers grounded in your content without leaving their everyday Microsoft 365 experience.
 For agents on the
 Customer Conversation harness
 , a primary agent works with specialized sub-agents in a multi-agent architecture to provide predictable responses for defined topics while still supporting fluid, natural-language conversation over voice or chat. If the agent can't resolve a request, it can escalate the conversation to a human representative through a defined path.
@@ -114,10 +108,6 @@ and
 Licensing for agents powered by the standard harness
 .
-Extend Microsoft Copilot
-You can also use Copilot Studio to extend Microsoft Copilot with your own instructions, tools, and knowledge, customizing Microsoft Copilot for specific tasks and domain knowledge, or creating a standalone custom version of the Microsoft Copilot Chat experience. Learn more in
-Extend Microsoft Copilot with agents
-.
 Accessibility
 The agent authoring canvas is built for accessibility in accordance with
 Microsoft accessibility guidelines

```

---

### 2. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:9f80df125d752f6fa8a0641780f3e9a67c24c75b39c36a98a50b447e6dc8f893

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -315,50 +315,6 @@ Use
 component collections
 with new enhancements. Access collections directly from the sidebar, quickly export or import collections, and take advantage of support for primary agents and new connector types, including child agents and Model Context Protocol (MCP).
-October 2025
-Updates for models used in Copilot Studio:
-Between October 27 and 31, 2025, GPTâ4o will be retired in Copilot Studio for agents using generative orchestration, except for GCC customers who can continue using GPTâ4o. The new default model is
-GPTâ4.1
-, which delivers improved performance, reliability, and consistency across experiences. GPTâ4o remains available until November 26, 2025 if you turn on the "
-Continue using retired models
-" option.
-Choose from multiple
-AI models
-to tailor your agent's performance to your needs.
-(Preview) Test and deploy
-GPTâ5
-models to explore advanced capabilities and enhance your agent's performance.
-Learn about
-Copilot Agent Kit
-, a suite of tools developed by the Power Customer Advisory Team (Power CAT) to help test custom agents, validate AI-generated content, analyze conversation key performance indicators, and more.
-(Preview) Group related user questions into
-themes
-and drill down into analytics to uncover patterns and gain deeper insights.
-Track
-time and cost savings
-for both autonomous and conversational agents to measure ROI and optimize performance.
-Access a
-unified activity and transcript view
-, pin sessions, and submit feedback for faster, more effective troubleshooting.
-(Preview)
-Accelerate flow execution
-to minimize timeouts and deliver a faster, smoother user experience.
-Use the
-Model Context Protocol (MCP) server
-to access dynamic, real-time contentâsuch as files, database records, and API responsesâfor richer context and improved agent responses.
-(Preview) Evaluate your agents using customizable
-test sets
-âwhether uploaded, manually created, or AI-generated. Test sets c
```

---

### 3. Agent 365 SDK and CLI

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/developer/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:b05142183ed0b5a5ae32916ea87ba6d3e16483a2438c6c9d793d2ab10bd52f6c

**Affected Controls:**
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/index.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/opentelemetry-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -23,25 +23,46 @@ Feedback
 Summarize this article for me
 New to Agent 365?
-If you're just getting started, choose the path that fits you best:
-I want to...
+First,
+choose your integration option
+. If built-in integration or registry sync provides the capabilities you need, you don't need to add the SDK just to register your agent. For Google Vertex AI and Amazon Bedrock agents, see
+Register Google Vertex AI and Amazon Bedrock agents
+.
+If your agent needs code-level integration, choose a path based on your starting point and the result you want:
+Your starting point
 Start here
-Get up and running quickly with AI assistance
+First result
+Before you begin
+You have an agent and want AI-assisted onboarding.
+Quickstart: Connect an existing agent to Agent 365
+, using
 Agent 365 Skills
-â An AI coding assistant (GitHub Copilot CLI, Claude Code, or VS Code agent mode) walks you through installation, configuration, deployment, and publishing.
-Follow a hands-on example step by step
-Quickstarts
-â pick a sample in your language (Node.js, Python, or .NET) and build a working agent.
-Understand the full workflow before diving in
-Get started with Agent 365 development
-â agent types, phases, setup, and publishing in one guide.
-Understand which type of agent to build
+.
+Register the agent, add the capabilities you choose, and validate the integration.
+Review the
+supported stacks, coding assistants, tenant access, roles, and licensing requirements
+.
+You have an agent and want to run CLI commands yourself.
+Set up an agent blueprint
+.
+Create the blueprint that defines your agent's identity and permissions.
+Review the
+CLI, tenant role, and Azure subscription requirements
+, then use
 Agent identity
-â explains the agent types and their identity models.
-Enable Google Vertex AI or Amazon Bedrock agents
-Registration for these agents requires no development work â agents are pulled automatically via the Google and Amazon APIs. No SDK integr
```

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*