# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-02
**Run Time:** 2026-09-02T10:49:21.637946+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 1 |
| MEDIUM Changes | 1 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | microsoft-365-copilot-overview | HIGH | 3.8 | Review and update |
| 2 | insider-risk-management-activities | CRITICAL | 1.12 | Update portal-walkthrough |
| 3 | application | CRITICAL | 1.2 | Monitor |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-activities
**Section:** Microsoft Purview
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:98b21eb675cf8ef4d7acac492e39475426a7e9821ccb965870ffbcfbcdd8ab8d

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

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
@@ -37,7 +37,7 @@ Investigate and act on alerts in Insider Risk Management by following these steps:
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
+The new unified alert experience combines the Triage Agent and classic alert dashboards into a single alerts list page. This unified view lets you manage both classic and agent-triaged alerts from
```

---

## HIGH: Control Review Recommended

### 1. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:b6e60a28144b5039b104f081f8aadd26bdb429925cae173a02cf06b31ffacaea

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

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
@@ -19,220 +19,379 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Microsoft 365 Copilot overview
+Microsoft Copilot overview
 Feedback
 Summarize this article for me
 Note
-Microsoft onboarded Anthropic as a Microsoft subprocessor. As a subprocessor, Anthropic operates with
+Microsoft Copilot is available in many regions worldwide. However, it might not be accessible in certain markets. Some organizations might gain access through an account support escalation process, but access is subject to approval. For more information, see
+International availability
+.
+Microsoft Copilot Chat and Microsoft Copilot responses and experiences differ by data grounding, integration depth, and licensing:
+However, all experiences are powered by:
+Large language models (LLMs)
+for natural language understanding and generation
+Grounding in web
+and/or
+organizational data
+(
+Microsoft Graph
+and
+Work IQ
+)
+Access scoped by user permissions (security and compliance enforced)
+Note
+Anthropic subprocessors are available only in applicable Microsoft 365 licensed experiences and aren't available to all users by default. Anthropic operates with
 Microsoft Enterprise data protections
 . For more information, see
-Anthropic as a subprocessor for Microsoft Online Services
-.
-Microsoft 365 Copilot is an AI-powered tool that helps with your work tasks
-.
-Users enter a prompt in Copilot and Copilot responds with AI-generated information. The responses are in real-time and can include internet-based content and work content that users have permission to access.
-Users get content relevant to their work tasks, and in the context of the Microsoft 365 app they're using.
-The following video provides an overview of Microsoft 365 Copilot. It's 1 minute and 49 seconds long.
-Using Microsoft 365 Copilot
-Say, for example, you're an operations
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Application Resources
**URL:** https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0
**Classification:** CRITICAL (Breaking changes)
**Content-Hash:** sha256:b46d4d77fe4cb9433c9e25765f7d4e1ad4215b822caf6949b12b8d2d37d0e21c

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