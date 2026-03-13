# Microsoft Learn Documentation Changes

**Run Date:** 2026-03-13
**Run Time:** 2026-03-13T06:56:56.922229+00:00
**Total URLs Checked:** 208

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 6 |
| MEDIUM Changes | 3 |
| NOISE Changes | 1 |
| Redirects | 21 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | MEDIUM | 1.4 | Review optional |
| 2 | alerts | HIGH | None | Review and update |
| 3 | ...ication-fundamentals-publish-channels | HIGH | None | Review and update |
| 4 | analytics-improve-agent-effectiveness | HIGH | None | Review and update |
| 5 | insider-risk-management-policies | HIGH | 1.12 | Review and update |
| 6 | ...management-settings-policy-indicators | HIGH | 1.12 | Review and update |
| 7 | information-barriers | MEDIUM | 1.22 | Review optional |
| 8 | new-dlpcompliancepolicy | NOISE | 1.5 | Monitor |
| 9 | whats-new | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -30,15 +30,17 @@ [This article is prerelease documentation and is subject to change.]
 Tenant and environment admins in Power Platform use
 alerts
-to track the operational health of their resources. Admins set up custom thresholds and get notifications when metrics for their resources pass specific thresholds. Create alerts on any metrics in the Monitor area of the Power Platform admin center.
+to track the operational health of their resources. Admins set up custom thresholds and get notifications when metrics for their resources pass specific thresholds. Create alerts on any metrics in the
+Monitor
+area of the Power Platform admin center.
 Keep the following principles in mind:
 Alerts are evaluated after new metrics are produced. Currently, all metrics are 24-hour aggregates, which means an alert rule in the
 Monitor
 area is evaluated every 24 hours after the newest 24-hour aggregates are produced. An alert rule does an on-demand evaluation upon its creation.
-Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. Alert rules can be placed on an environment and a specific resource.
+Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. You can place alert rules on an environment and a specific resource.
 A
 triggered alert
-is when one or more of the resources that are being monitored by an alert rule pass specific thresholds defined by the admin who configured the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for how to improve the resources if it's in a managed environment.
+occurs when one or more of the resources that an alert rule monitors pass specific thresholds that the admin defines when configuring the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for 
```

---

### 2. Agent Publishing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)

**What Changed:**
```diff
--- +++ @@ -169,6 +169,16 @@ Twitter
 ).
 Suggested actions are presented as a text-only list; users must retype an option to respond.
+Troubleshoot publishing errors
+If you run into issues when publishing your agent, use the following troubleshooting steps to resolve common publishing errors:
+Verify all configurations are correct.
+Make sure that the agent settings, authentication options, and channel configurations are set up properly before publishing.
+Check for any missing dependencies.
+Ensure that all required components, such as topics, flows, connectors, and data sources, are available and properly configured.
+Review error logs for specific error codes and messages.
+Go to the
+Publish
+page and check the publish status for any error details. Use the error codes and messages to identify and address the root cause.
 Next steps (Web app)
 Article
 Description

```

---

### 3. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)

**What Changed:**
```diff
--- +++ @@ -276,21 +276,11 @@ Poor
 quality label. The tooltip also indicates the number of answers sampled to arrive at the calculated percent value.
 In the legend below the chart, hover over any of the quality label reasons to highlight that reason in the chart.
-You can provide feedback to Microsoft about this section with the
-Thumbs up
-and
-Thumbs down
-icons
-. Use the
-Submit feedback to Microsoft
-panel to add a comment and share related files. By providing descriptive feedback like this, we can work together to continuously improve our product.
-On the
-Submit feedback to Microsoft
-panel, describe in natural language your likes or dislikes, depending on which icon you selected to open the panel.
-Choose whether to share prompt, generated response, relevant content samples, and additional log files.
 Select
-Submit
-.
+See questions
+to
+see an unfiltered list of all questions
+within the configured time period.
 Select
 See details
 to open a side panel with question answer rates, knowledge source usage, and error rates over your selected time period. You can use these charts to identify which knowledge sources work well to help users, and which to target for improvements.
@@ -318,6 +308,117 @@ thumbs down
 reactions.
 A stacked bar chart showing the breakdown of the quality of response relative weightings for questions referencing this knowledge source. Hover over any segment of the bar chart to see the value of that segment's relative weighting and the number of questions sampled to arrive at that value.
+Drill down to a list of agent questions
+Drill down to view specific questions that contributed to a metric and the supporting context, such as how the agent responded, how users reacted, and which knowledge sources were involved. This view provides better insight into response quality and helps identify possible gaps in knowledge coverage.
+Important
+You need a Bot Transcript Viewer security role to view the list and its metrics. Only admins can gra
```

---

### 4. Create Insider Risk Policies

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**What Changed:**
```diff
--- +++ @@ -88,7 +88,7 @@ Data theft from Microsoft 365 apps by users leaving your organization
 : Detects potential data theft from Microsoft 365 cloud apps by users leaving your organization or whose account was deleted from Microsoft Entra ID.
 Data theft from non-Microsoft 365 apps by users leaving your organization
-: (preview) Detects potential data theft from non-Microsoft 365 cloud apps, including Microsoft Fabric, by users leaving your organization or whose account was deleted from Microsoft Entra ID.
+: Detects potential data theft from non-Microsoft 365 cloud apps, including Microsoft Fabric, by users leaving your organization or whose account was deleted from Microsoft Entra ID.
 Email exfiltration
 : Detects when users email sensitive assets outside your organization. For example, users emailing sensitive assets to their personal email address.â
 To get started, go to

```

---

### 5. Insider Risk Indicators

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**What Changed:**
```diff
--- +++ @@ -145,7 +145,7 @@ To use this indicator, enable
 pay-as-you-go billing
 in your organization.
-These indicators include policy indicators for Microsoft Fabric workloads such as Power BI and Lakehouse (preview). They help you detect techniques used to:
+These indicators include policy indicators for Microsoft Fabric workloads such as Power BI and Lakehouse. They help you detect techniques used to:
 Figure out the environment (for example, viewing Power BI reports and dashboards).
 Gather data of interest (for example, downloading Power BI reports).
 Obfuscate the data gathered or change protection (for example, downgrading or removing sensitivity labels of Power BI or Lakehouse assets).

```

---

### 6. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -64,6 +64,18 @@ : Disable content download to create cases without content to reduce triage time. To get started, see
 Enable or disable content download
 .
+General availability (GA)
+:
+Microsoft Fabric indicators
+now include Lakehouse indicators.
+General availability (GA)
+: A new quick policy template for
+detecting data theft from non-Microsoft 365 apps by users leaving your organization
+is now available.
+General availability (GA)
+:
+Pay-as-you-go usage reports
+provide transparency and enable more accurate budget planning and policy tuning.
 Sensitivity labels
 General availability (GA)
 : Manual labeling for OneNote, supported at the

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Connector Reference
**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Classification:** MEDIUM (General content update)

---

### 2. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers
**Classification:** MEDIUM (General content update)

---

### 3. DLP Cmdlets
**URL:** https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy
**Classification:** NOISE (Metadata or formatting only)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage | https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide |
| https://learn.microsoft.com/purview/compliance-manager | https://learn.microsoft.com/en-us/purview/compliance-manager |
| https://learn.microsoft.com/purview/compliance-manager-assessments | https://learn.microsoft.com/en-us/purview/compliance-manager-assessments |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health | https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide |
| https://learn.microsoft.com/azure/sentinel/connect-data-sources | https://learn.microsoft.com/en-us/azure/sentinel/connect-data-sources |
| https://learn.microsoft.com/azure/sentinel/monitor-your-data | https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data |
| https://learn.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules | https://learn.microsoft.com/en-us/azure/sentinel/automate-incident-handling-with-automation-rules |
| https://learn.microsoft.com/azure/sentinel/investigate-cases | https://learn.microsoft.com/en-us/azure/sentinel/investigate-cases |
| https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai | https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2 |
| https://learn.microsoft.com/azure/cost-management-billing/costs/overview-cost-management | https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management |
| https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets | https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets |
| https://learn.microsoft.com/en-us/azure/devops/test/overview | https://learn.microsoft.com/en-us/azure/devops/test/overview?view=azure-devops |
| https://learn.microsoft.com/en-us/power-apps/guidance/planning/testing-phase | https://learn.microsoft.com/en-us/power-apps/maker/plan-designer/plan-designer |
| https://learn.microsoft.com/en-us/graph/api/resources/application | https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0 |
| https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview | https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview?view=graph-rest-1.0 |
| https://learn.microsoft.com/security/operations/incident-response-planning | https://learn.microsoft.com/en-us/security/operations/incident-response-planning |
| https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy | https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpcompliancepolicy?view=exchange-ps |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview | https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview?view=o365-worldwide |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*