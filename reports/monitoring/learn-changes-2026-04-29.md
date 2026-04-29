# Microsoft Learn Documentation Changes

**Run Date:** 2026-04-29
**Run Time:** 2026-04-29T08:21:51.436499+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 2 |
| MEDIUM Changes | 2 |
| Redirects | 14 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | MEDIUM | 1.4 | Review and update |
| 2 | admin-share-bots | HIGH | None | Review and update |
| 3 | analytics-overview | HIGH | 3.2, 3.10, 2.5, 2.6, 2.9 | Update portal-walkthrough |
| 4 | whats-new | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC 2011-12/SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -38,7 +38,22 @@ page doesn't show analytics for activity you complete when you test your agent in Copilot Studio by using the
 test panel
 .
-To access analytics:
+Grant limited view-only access to analytics
+If you are the agent owner and want to grant access only to the
+Analytics
+page of your agent, you can do so by sharing the agent with the
+Analytics Viewer
+sharing role enabled. If you want the person you are sharing this agent with to have access to information from the conversation transcript, they must also have the
+Bot Transcript Viewer
+security role.
+Learn more about
+sharing an agent's analytics
+.
+Important
+As an agent owner, you can only share the Analytics viewer role with individuals and not with groups of users.
+To access the
+Analytics
+page of your agent:
 Open your agent in Copilot Studio.
 Select
 Analytics

```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -2516,6 +2516,8 @@ By: NETWORG
 SigningHub
 By: Ascertia Limited.
+SigningHub Webhooks
+By: Ascertia Limited.
 SIGNL4 - Mobile Alerting
 By: Derdack
 SignNow

```

---

### 2. Share and Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)

**What Changed:**
```diff
--- +++ @@ -243,6 +243,70 @@ Analytics
 pages.
 If you rename, restore, or delete a team, it can take up to two hours for the changes to be reflected in the Copilot Studio app.
+Share an agent's analytics
+Use the
+Analytics Viewer
+role in Copilot Studio to provide analysts and stakeholders with read-only access to an agent's analytics, without allowing changes to the agent.
+Important
+As an agent owner, you can only share the Analytics viewer role with individuals and not with groups of users.
+What is the Analytics Viewer role?
+The Analytics Viewer role is a sharing role that grants access to the
+Analytics
+page for a specific agent.
+Users who are assigned this role:
+Can view the agent's
+Analytics
+page and its metrics.
+Open the agent directly on the
+Analytics
+page.
+Can't edit or share the agent.
+Can't access topics, actions, settings, testing tools, or publishing.
+Why use this role?
+The Analytics Viewer role helps resolve a common challenge for agent makers: giving analysts and stakeholders access to analytics insights without granting editing permissions. With this role, you can:
+Share performance insights with analysts and business stakeholders.
+Avoid exporting and manually distributing analytics data.
+Maintain governance over production agents.
+Enable faster, data-driven decision-making with direct access to metrics.
+Share an agent and assign the Analytics Viewer role
+Important
+You must be an agent owner to share an agent and assign the Analytics Viewer role.
+To grant Analytics Viewer access:
+Open the agent in Copilot Studio.
+Select the three dots (
+â¦
+) next to
+Test
+, and then select
+Share
+.
+In the
+Share agent
+pane, add the user you want to share your agent with, or select an existing user.
+Select
+Analytics viewer
+.
+Select
+Share
+.
+A significant part of the insight from the
+Analytics
+page comes from the ability to drill down into the data behind each metric. For example, on the
+Analytics
+page, you can select a respo
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Connector Reference
**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Classification:** MEDIUM (General content update)

---

### 2. Copilot Studio Kit — Compliance Hub
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Classification:** MEDIUM (General content update)

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

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*