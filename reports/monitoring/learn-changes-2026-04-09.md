# Microsoft Learn Documentation Changes

**Run Date:** 2026-04-09
**Run Time:** 2026-04-09T07:25:58.443950+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 3 |
| MEDIUM Changes | 2 |
| Redirects | 14 |
| Errors | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | advanced-connector-policies | CRITICAL | 1.4 | Monitor |
| 2 | wp-data-loss-prevention | HIGH | 2.7, 2.24, 1.14, 1.28, 3.7 | Review and update |
| 3 | dlp-connector-classification | CRITICAL | 1.14 | Monitor |
| 4 | analytics-improve-agent-effectiveness | HIGH | None | Review and update |
| 5 | whats-new | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. DLP Policies (Power Platform)

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 2.7: Control 2.7: Vendor and Third-Party Risk Management
  - File: `controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md`
- Control 2.24: Control 2.24: Agent Feature Enablement and Restriction Governance
  - File: `controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.25/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.28/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -28,66 +28,77 @@ Feedback
 Summarize this article for me
 Data policies are a critical aspect of maintaining data security and compliance within the Microsoft Power Platform ecosystem.
-You can create data policies that can act as guardrails to help reduce the risk of users from unintentionally exposing organizational data. A core component of Power Apps, Power Automate, and Microsoft Copilot Studio is the use of connectors to enumerate, populate, push, and pull data. Data policies in Power Platform admin center allow administrators to control access to these connectors in various ways to help reduce risk in your organization.
+Create data policies that act as guardrails to help reduce the risk of users unintentionally exposing organizational data. A core component of Power Apps, Power Automate, and Microsoft Copilot Studio is the use of connectors to enumerate, populate, push, and pull data. Power Platform admin center data policies allow administrators to control access to these connectors in various ways to help reduce risk in your organization.
 This overview describes some high-level concepts related to connectors and several important considerations to take into account when setting up your policies or making policy changes.
 Connectors
-Connectors, at their most basic level, are strongly typed representations of restful, application programming interfaces, also known as APIs. For example, the Power Platform API provides several operations related to functionality in Power Platform admin center.
-When wrapping the Power Platform API in to a connector, it becomes easier for makers and citizen developers to utilize the API in their low-code apps, workflows, and chatbots. For example, the Power Platform for Admins V2 connector is the representation of the Power Platform API and we see the 'Get Recommendations' action is simply drag and dropped on to the flow:
-There are several types of connectors mentioned in this article, and each has capabilities wi
```

---

### 2. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -419,6 +419,78 @@ If the Response quality is
 Good
 or if the question wasn't sampled, the Reason parameter isn't assigned any value.
+Drill down to sessions
+Drill down to sessions to view specific sessions that contributed to a metric. This deeper view helps you understand the
+why
+and
+how
+behind top-level agent metrics and enables you to identify and investigate potential issues.
+Use the sessions list to analyze agent performance and investigate issues that lead to a session outcome (
+resolved
+,
+escalated
+,
+abandoned
+, or
+unengaged
+). For example, filter by channel and focus on low CSAT sessions to gain insight into why customers in those channels might be having a poor experience.
+To drill down to the session list window:
+From the
+Conversation outcomes
+panel, select
+See sessions
+to view all sessions for the analytic period.
+From the
+Conversation outcomes
+panel, select
+See details
+. This opens a side pane of further metrics on conversation session outcomes. Select on any highlighted metric plot to view a filter list of sessions.
+The session list is filtered based on the data point you drilled down on. This is reflected in the default filter settings above the session list. For instance, within the
+Conversation outcomes
+side pane, choosing the
+Resolved confirmed
+bar segment of the
+Resolved outcomes reasons
+bar tile sets the session outcome and outcome reason to resolved and resolved confirmed, respectively.
+The list of sessions window can be filtered by the
+Time period
+,
+Session outcome
+,
+Outcome reason
+, and
+Channel
+.
+Note
+To view sessions, you must have the
+Bot Transcript Viewer
+security role.
+Sessionâs list is updated daily and shows up to 10,000 sessions per day. Only the last 28 days of sessions are stored and available to be viewed.
+The list of session window is sorted by the following parameters:
+Detailed session-level parameter
+Description
+Start time
+Timestamp of when the session was invoked.
+D
```

---

### 3. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Policy language)

**What Changed:**
```diff
--- +++ @@ -149,6 +149,12 @@ : Use the new
 Advanced review set explorer
 to query review set data with Kusto Query Language (KQL). Build advanced queries with complex filtering, pattern-based text extraction, and data visualization to analyze and find key information in your review sets.
+New
+: Configure
+sampling options
+when adding search results to a review set in eDiscovery. Choose confidence-based or percentage-based sampling to add a statistically representative subset of search results instead of all items. Completing the
+Generate statistics
+process is required to enable sampling.
 Insider Risk Management
 In preview
 : Disable content download to create cases without content to reduce triage time. To get started, see

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Advanced Connector Policies
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Classification:** CRITICAL (Deprecation notice)

---

### 2. Connector Classification
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/dlp-connector-classification
**Classification:** CRITICAL (Deprecation notice)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage | https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents | https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health | https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide |
| https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai | https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2 |
| https://learn.microsoft.com/en-us/azure/devops/test/overview | https://learn.microsoft.com/en-us/azure/devops/test/overview?view=azure-devops |
| https://learn.microsoft.com/en-us/graph/api/resources/application | https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0 |
| https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview | https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview?view=graph-rest-1.0 |
| https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy | https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpcompliancepolicy?view=exchange-ps |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview | https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview?view=o365-worldwide |

---

## Errors

- **Enhanced Admin Controls for Agent Security [Preview]** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/enhanced-admin-controls-agent-security
- **Agentic Center of Enablement [Preview]** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/automate-governance-agentic-center-enablement
- **Agent Suggestions from M365 Copilot [Preview]** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/get-agent-suggestions-based-work

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*