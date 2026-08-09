# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-09
**Run Time:** 2026-08-09T06:57:42.784648+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 2 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | monitor-your-data | HIGH | 3.9 | Review and update |
| 2 | investigate-cases | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Workbooks

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data
**Section:** Azure Services
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:11db1912339b7f4cfde421f0b14338ed0aab1db7eab36978db2f55aa73a037e8

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
+, and then select the location where you want to save the workbook. Saving the workbook creates an Azure resource in the selected location based on the relevant template. Only the workbook's JSON file is saved in this location, and no data.
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
@@ -122,7 +123,7 @@ , and then choose one or more workspaces.
 We recommend that your query uses an
 Advanced Security Information Model (ASIM) parser
-and not a built-in table. The query will then support any current or future relevant data source rather than a single data source.
+and not a built-in table. A query that uses an ASIM parser supports any current or future relevant data source rather than a single data source.
 When you're done with your edits, select
 Done editing
 and then
@@ -130,7 +131,7 @@ . In the side pane, enter a meaningful name for your workbook, and select the subscription and resource group for your workspace.
 When working in the Azure portal, switch between workbooks in your workspace
```

---

### 2. Investigate Incidents

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/investigate-cases
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:52be625843b267799b572f2ca72321b27cf938f189f2eb6d832aeba6ba4b9830

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