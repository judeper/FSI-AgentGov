# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-13
**Run Time:** 2026-08-13T07:35:24.661785+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 3 |
| MEDIUM Changes | 1 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | .../en-us/microsoft-agent-365/developer/ | MEDIUM | 3.2, 3.6, 3.14, 2.5, 1.7 | Review and update |
| 2 | monitor-your-data | HIGH | 3.9 | Review and update |
| 3 | investigate-cases | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Agent 365 SDK and CLI

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/developer/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6702d6246963a1f1682e286c65bedaaa94458db210fe00101a959cdca1517e1e

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/index.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/opentelemetry-setup.md` (HIGH)

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
@@ -27,8 +27,8 @@ I want to...
 Start here
 Get up and running quickly with AI assistance
-AI-guided setup
-â An AI coding agent (GitHub Copilot, Claude Code, or OpenAI Codex) walks you through installation, configuration, deployment, and publishing from a single instruction file.
+Agent 365 Skills
+â An AI coding assistant (GitHub Copilot CLI, Claude Code, or VS Code agent mode) walks you through installation, configuration, deployment, and publishing.
 Follow a hands-on example step by step
 Quickstarts
 â pick a sample in your language (Node.js, Python, or .NET) and build a working agent.
@@ -36,7 +36,7 @@ Get started with Agent 365 development
 â agent types, phases, setup, and publishing in one guide.
 Understand which type of agent to build
-Types of agents
+Agent identity
 â explains the agent types and their identity models.
 Enable Google Vertex AI or Amazon Bedrock agents
 Registration for these agents requires no development work â agents are pulled automatically via the Google and Amazon APIs. No SDK integration, no blueprint, and no code changes are required. Once registered, you can use the Agent 365 SDK to add observability, Work IQ tool access, and other capabilities incrementally. See

```

---

### 2. Workbooks

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data
**Section:** Azure Services
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:7b0612a434c97e5f0d1d21efc91c05b8f34b8bfc2ae692a99a8ab49746e8f2e6

**Affected Controls:**
- Control 3.9: Control 3.9: Microsoft Sentinel Integration
  - File: `controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md`

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
@@ -36,6 +36,7 @@ unified security operations experience offered by Microsoft Defender
 .
 Prerequisites
+Before you create or use workbooks, make sure you meet the following prerequisites:
 You must have at least
 Workbook reader
 or
@@ -66,7 +67,7 @@ Azure portal
 From the details pane, select
 Save
-, and then select the location where you want to save the workbook. This action creates an Azure resource in the selected location based on the relevant template. Only the workbook's JSON file is saved in this location, and no data.
+, then select the location where you want to save the workbook. Saving the workbook creates an Azure resource in the selected location based on the relevant template. Only the workbook's JSON file is saved in this location, and no data.
 From the details pane, select
 View saved workbook
 to open it for editing.
@@ -98,7 +99,7 @@ For more information, see:
 Create interactive reports with Azure Monitor Workbooks
 Tutorial: Visual data in Log Analytics
-Create new workbook
+Create a new workbook
 Create a workbook from scratch in Microsoft Sentinel.
 In Microsoft Sentinel, select
 Threat management > Workbooks
@@ -119,10 +120,10 @@ Resource type
 to
 Log Analytics
-, and then choose one or more workspaces.
+, then choose one or more workspaces.
 We recommend that your query uses an
 Advanced Security Information Model (ASIM) parser
-and not a built-in table. The query will then support any current or future relevant data source rather than a single data source.
+and not a built-in table. A query that uses an ASIM parser supports any current or future relevant data source rather than a single data source.
 When you're done with your edits, select
 Done editing
 and then
@@ -130,7 +131,7 @@ . In the side pane, enter a meaningful name for your workbook, and select the subscription and resource group for your workspace.
 When 
```

---

### 3. Investigate Incidents

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/investigate-cases
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:e73fd2d5c758d934cd7c0b20c32d313088dccfb09e4e9a2a5e6074f8b7e98c80

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
@@ -22,10 +22,10 @@ Investigate incidents with Microsoft Sentinel (legacy)
 Feedback
 Summarize this article for me
-This article helps you use Microsoft Sentinel's legacy incident investigation experience. If you're using the newer version of the interface, use the newer set of instructions to match. For more information, see
+This article helps you use Microsoft Sentinel's legacy incident investigation experience. If you're using the newer version of the interface, see
 Navigate and investigate incidents in Microsoft Sentinel
-.
-After connecting your data sources to Microsoft Sentinel, you want to be notified when something suspicious happens. To enable you to do this, Microsoft Sentinel lets you create advanced analytics rules that generate incidents that you can assign and investigate.
+for instructions that match that experience.
+After connecting your data sources to Microsoft Sentinel, you want to be notified when something suspicious happens. To enable you to receive these notifications, Microsoft Sentinel lets you create advanced analytics rules that generate incidents that you can assign and investigate.
 An incident can include multiple alerts. It's an aggregation of all the relevant evidence for a specific investigation. An incident is created based on analytics rules that you created in the
 Analytics
 page. The properties related to the alerts, such as severity and status, are set at the incident level. After you let Microsoft Sentinel know what kinds of threats you're looking for and how to find them, you can monitor detected threats by investigating incidents.
@@ -34,11 +34,13 @@ Azure Preview Supplemental Terms
 include additional legal terms that apply to Azure features that are in beta, preview, or otherwise not yet released into general availability.
 Prerequisites
+Before you investigate or assign incidents, make sure the follo
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Agent 365 SDK and CLI
**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/developer/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6702d6246963a1f1682e286c65bedaaa94458db210fe00101a959cdca1517e1e

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