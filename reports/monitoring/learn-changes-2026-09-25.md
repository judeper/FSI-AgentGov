# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-25
**Run Time:** 2026-09-25T11:21:58.270592+00:00
**Total URLs Checked:** 231

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 3 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | fundamentals-what-is-copilot-studio | HIGH | 2.13 | Review and update |
| 2 | ...ication-fundamentals-publish-channels | HIGH | None | Review and update |
| 3 | add-tools-custom-agent | HIGH | 2.17 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Copilot Studio Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c88f62f18538a0eb69943864206a659357b62d2af2ff1ebe3a9e72dd3e246d89

**Affected Controls:**
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`

**What Changed:**
```diff
--- +++ @@ -23,6 +23,10 @@ Feedback
 Summarize this article for me
 Microsoft Copilot Studio is a graphical, low-code studio for building and managing AI-powered agents and workflows. Build agents and workflows, connect them to your organization's data and systems, and publish them to the channels where your users already work.
+Note
+The app creation experience in Copilot Studio is in preview. Learn more in
+Apps overview
+.
 Copilot Studio brings agent and workflow creation and management into a single studio, so you can design a complete business solutionâand let those pieces work togetherâwithout switching tools. Because it's low-code, you can build capable solutions without an extensive technical background, while still giving professional makers the depth they need. Connect to other data sources through prebuilt or custom connectors to create and coordinate sophisticated logic across your solution.
 What you can build
 Copilot Studio supports several building blocks. Use them on their own, or combine them to automate an end-to-end business process. They can also collaborateâfor example, a workflow can call an agent to complete a step.
@@ -122,6 +126,7 @@ Harnesses in Copilot Studio
 Workflows overview
 Agent flows overview
+Apps overview (preview)
 Copilot Studio licensing
 Publish and deploy your agent
 Feedback

```

---

### 2. Agent Publishing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:0bcbbac56a54dff8f0b8c352273a862b56e80bc2582158635680c4b217579e55

**What Changed:**
```diff
--- +++ @@ -129,6 +129,21 @@ GroupMe
 Direct Line Speech
 Email
+Note
+If your organization has
+blocked a channel due to data policies
+or due to the type of
+authentication configuration
+, you won't be able to select it. Learn more in
+Channels blocked by your organization's policies
+.
+Channels blocked by your organization's policies
+Your organization's governance policies or your agent's configuration might block some channels.
+An unavailable channel appears disabled on the
+Channels
+page. Select the information
+icon next to the channel to see why the channel isn't available.
+Depending on the restriction, you might need to use a different channel, change the applicable configuration, or contact your administrator.
 Channel experience reference table
 Different channels offer different user experiences. The following table shows a high-level overview of the experiences for each channel. Consider the channel experiences when you optimize your agent content for specific channels.
 Experience

```

---

### 3. Agent Orchestration

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:fab6368fddec0beeb4734d9e1d89f7f7d9d9cf4d374e0a76e1325b4c8a0d81e3

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

**What Changed:**
```diff
--- +++ @@ -80,7 +80,7 @@ .
 In the
 Add tool
-pane, select
+panel, select
 New tool
 .
 Select the type of tool you want to add from the list that appears:
@@ -90,6 +90,10 @@ Custom connector
 Model Context Protocol
 REST API
+Note
+If your organization blocked a tool due to data policies, you can't select it. Learn more in
+Tools blocked by your organization's policies
+.
 Perform the configuration steps specific to the type of tool you selected. For example, if you select
 Prompt
 , you must perform the following steps:
@@ -110,6 +114,16 @@ You can see the new tool on the
 Tools
 page for the agent.
+Tools blocked by your organization's policies
+Your organization can use governance policies to restrict which tools and connectors are available in Copilot Studio.
+When a data policy blocks a tool, the tool appears disabled in the
+Add tool
+panel and you can't select it. Select the information
+icon next to the disabled tool to see why the tool isn't available.
+The message identifies the policy restriction that prevents the tool from being used. If you need access to a blocked tool, contact your administrator.
+Learn more in
+Configure data policies for agents
+.
 View and make changes to your tool configuration
 You can view and edit the configuration of your tool at any time: go to the
 Tools

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