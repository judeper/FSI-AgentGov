# Microsoft Learn Documentation Changes

**Run Date:** 2026-03-14
**Run Time:** 2026-03-14T06:51:10.083468+00:00
**Total URLs Checked:** 208

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 11 |
| MEDIUM Changes | 5 |
| NOISE Changes | 1 |
| Redirects | 21 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | HIGH | 1.4 | Review and update |
| 2 | alerts | HIGH | None | Review and update |
| 3 | security-and-governance | MEDIUM | 1.8, 1.28, 1.1 | Review optional |
| 4 | ...ication-fundamentals-publish-channels | HIGH | None | Review and update |
| 5 | analytics-improve-agent-effectiveness | HIGH | None | Review and update |
| 6 | nlu-gpt-overview | HIGH | 2.12 | Review and update |
| 7 | insider-risk-management-policies | HIGH | 1.12 | Review and update |
| 8 | ...management-settings-policy-indicators | HIGH | 1.12 | Review and update |
| 9 | import-hr-data | HIGH | 1.12 | Review and update |
| 10 | endpoint-dlp-learn-about | MEDIUM | 1.17 | Review optional |
| 11 | information-barriers | MEDIUM | 1.22 | Review optional |
| 12 | access-reviews-overview | HIGH | 1.3 | Review and update |
| 13 | create-access-review | HIGH | 4.2, 2.8 | Review and update |
| 14 | application | MEDIUM | 1.2 | Review optional |
| 15 | new-dlpcompliancepolicy | NOISE | 1.5 | Monitor |
| 16 | whats-new | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**What Changed:**
```diff
--- +++ @@ -112,11 +112,13 @@ Adobe Experience Manager
 By: Adobe
 Adobe PDF Services
-By: Adobe Inc.
+By: Adobe Acrobat Services
 Advanced Data Operations
 By: State Solutions
 Advanced Scraper (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
+Aexum
+By: Nodefusion d.o.o
 Affirmations (Independent Publisher)
 By: Troy Taylor
 Africa's Talking Airtime
@@ -737,6 +739,8 @@ By: Troy Taylor
 Databricks
 By: Databricks Inc.
+DataFlows SMS
+By: DATAFLOWS SMS
 DataMotion
 By: DataMotion, Inc.
 Datamuse (Independent Publisher)
@@ -973,6 +977,8 @@ By: Encodian
 Encodian - PowerPoint
 By: Encodian
+Encodian - Sign
+By: Encodian
 Encodian - Utilities
 By: Encodian
 Encodian - Word
@@ -980,8 +986,6 @@ Encodian [DEPRECATED]
 By: Encodian
 Encodian Filer
-By: Encodian
-Encodian Trigr
 By: Encodian
 Engagement Cloud
 By: dotdigital
@@ -1045,6 +1049,8 @@ By: EXPOCAD
 Ezekia-MCP
 By: Ezekia
+Fabric MCP
+By: Microsoft
 Face API
 By: Microsoft
 FactSet
@@ -1264,7 +1270,7 @@ HitHorizons
 By: FinStat, s. r. o.
 Hive CPQ Product Configurator
-By: NimbleOps NV
+By: Hive CPQ
 Holopin
 By: Troy Taylor
 Holopin (Independent Publisher)
@@ -1669,8 +1675,6 @@ By: Build My Team LLC
 Michael Scott Quotes (Independent Publisher) [DEPRECATED]
 By: Troy Taylor
-Microsoft 365 Admin Center MCP
-By: Microsoft
 Microsoft 365 compliance
 By: Microsoft
 Microsoft 365 message center
@@ -2931,18 +2935,6 @@ By: Microsoft
 WordPress
 By: Microsoft
-Work IQ Calendar MCP
-By: Microsoft
-Work IQ Copilot MCP
-By: Microsoft
-Work IQ Mail MCP
-By: Microsoft
-Work IQ Teams MCP
-By: Microsoft
-Work IQ User MCP
-By: Microsoft
-Work IQ Word MCP
-By: Microsoft
 Workable (Independent Publisher)
 By: David Kjell
 Workday HCM
@@ -3037,6 +3029,8 @@ By: Troy Taylor
 Zenlogin (Independent Publisher)
 By: Troy Taylor
+ZeroTrain AI Core
+By: Leonard Gambrell - DBA Gambrell Software
 Zippopotamus (Independent Publisher)
 By: Tomasz Poszytek
 ZIPPYDOC

```

---

### 2. Monitor Alerts

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

### 3. Agent Publishing

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

### 4. Customer Satisfaction

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

### 5. Generative AI

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-gpt-overview
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

**What Changed:**
```diff
--- +++ @@ -32,59 +32,67 @@ Generative AI
 in the Artificial Intelligence (AI) playbook.
 In Copilot Studio, you can use the following generative AI features to retrieve and create content, either individually or all together.
-Create an agent
-. With no manual authoring of topics required, an
+Create an agent.
+With no manual authoring of topics required, an
 empty
-agent can generate answers based on knowledge sources you specify such as websites and files. See
-Generative answers
-and the
-Quickstart
+agent can generate answers based on knowledge sources you specify such as websites and files. Learn more in
+Quickstart: Create and deploy an agent
 .
-Harness AI general knowledge
-. When this option is enabled, the agent can answer general questions unrelated to your specific knowledge sources or topics. See
-AI general knowledge
+Harness AI general knowledge.
+When
+Use general knowledge
+is turned on, the agent can answer general questions unrelated to your specific knowledge sources or topics. Learn more in
+Allow the agent to use general knowledge
 .
-Author topics using natural language
-. Describe what you want your topic to do, and Copilot Studio creates it for you. Your agent includes conversational responses and multiple types of nodes. Use the suggested default topic or as a starting point for further development. See
+Author topics using natural language.
+Describe what you want your topic to do, and Copilot Studio creates it for you. Your agent includes conversational responses and multiple types of nodes. Use the suggested default topic as a starting point for further development. Learn more in
 Create and edit topics with Copilot
 .
-Author prompts using natural language
-. Describe the prompt you want to create, and Copilot Studio generates it for you. You can use the suggested default prompt or as a starting point for further development. See
-Create and edit prompts with Copilot
+Author prompts using natural language.
+Describe the prompt you want
```

---

### 6. Create Insider Risk Policies

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

### 7. Insider Risk Indicators

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

### 8. HR Data Connector

**URL:** https://learn.microsoft.com/en-us/purview/import-hr-data
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**What Changed:**
```diff
--- +++ @@ -37,12 +37,13 @@ Assign the Data Connector Admin role to the user who creates the HR connector in Step 3. This role is required to add connectors on the
 Data connectors
 page in the Microsoft Purview portal. Multiple role groups include this role by default. For a list of these role groups, see
-Roles in Microsoft Defender for Office 365 and Microsoft Purview compliance
-. Alternatively, an admin in your organization can create a custom role group, assign the Data Connector Admin role, and add the appropriate users as members. For instructions, see:
+Roles in Microsoft Defender for Office 365 and Microsoft Purview
+. Alternatively, an admin in your organization can create a custom role group, assign the Data Connector Admin role, and then add the appropriate users as members. For instructions, see:-
 Permissions in the Microsoft Purview portal
+-
 Roles and role groups in Microsoft Defender for Office 365 and Microsoft Purview compliance
-Understand that the sample script you run in Step 4 uploads your HR data to the Microsoft cloud so that the insider risk management solution can use it. This sample script isn't supported under any Microsoft standard support program or service. It's provided AS IS without warranty of any kind. Microsoft further disclaims all implied warranties including, without limitation, any implied warranties of merchantability or of fitness for a particular purpose. You assume all risk arising from the use or performance of the sample script and documentation. In no event shall Microsoft, its authors, or anyone else involved in the creation, production, or delivery of the scripts be liable for any damages whatsoever (including, without limitation, damages for loss of business profits, business interruption, loss of business information, or other pecuniary loss) arising out of the use of or inability to use the sample scripts or documentation, even if Microsoft has been advised of the possibility of such damages.
-Know that this con
```

---

### 9. Access Reviews

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview
**Section:** Microsoft Entra ID
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**What Changed:**
```diff
--- +++ @@ -34,7 +34,7 @@ As new employees join, how do you ensure they have the access they need to be productive?
 As people move teams or leave the company, how do you make sure that their old access is removed?
 Excessive access rights can lead to compromises.
-Excessive access right can also lead audit findings as they indicate a lack of control over access.
+Excessive access rights can also lead to audit findings as they indicate a lack of control over access.
 You have to proactively engage with resource owners to ensure they regularly review who has access to their resources.
 When should you use access reviews?
 Too many users in privileged roles:
@@ -46,9 +46,9 @@ Microsoft Entra Privileged Identity Management (PIM)
 experience.
 When automation is not possible:
-You can create rules for dynamic membership groups, security groups, or Microsoft 365 Groups, but what if the HR data isn't in Microsoft Entra ID or if users still need access after leaving the group to train their replacement? You can then create a review on that group to ensure those who still need access keeps access.
+You can create rules for dynamic membership groups, security groups, or Microsoft 365 Groups, but what if the HR data isn't in Microsoft Entra ID or if users still need access after leaving the group to train their replacements? You can then create a review on that group to ensure those who still need access keeps access.
 When a group is used for a new purpose:
-If you have a group that is going to be synced to Microsoft Entra ID, or if you plan to enable the application Salesforce for everyone in the Sales team group, it would be useful to ask the group owner to review the dynamic membership group before it's used in a different risk content.
+If you have a group that is going to be synced to Microsoft Entra ID, or if you plan to enable the application Salesforce for everyone in the Sales team group, it would be useful to ask the group owner to review the dynamic membership gro
```

---

### 10. Create Access Review

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/create-access-review
**Section:** Microsoft Entra ID
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`

**What Changed:**
```diff
--- +++ @@ -110,7 +110,7 @@ Inactive users (on tenant level)
 . If you check the box, the scope of the review focuses on inactive users only, those who haven't signed in either interactively or non-interactively to the tenant. Then, specify
 Days inactive
-with many days inactive up to 730 days (two years). Users in the group inactive for the specified number of days are the only users in the review.
+with the number of days inactive up to 730 days (two years). Users in the group inactive for the specified number of days are the only users in the review.
 Note
 Recently created users aren't affected when configuring the inactivity time. The Access Review checks if a user has been created in the time frame configured and disregard users who havenât existed for at least that amount of time. For example, if you set the inactivity time as 90 days and a guest user was created or invited less than 90 days ago, the guest user won't be in scope of the Access Review. This ensures that a user can sign in at least once before being removed.
 Select
@@ -119,6 +119,7 @@ Next: Reviews
 You can create a single-stage or multi-stage review. For a single stage review, continue here. To create a multi-stage access review, follow the steps in
 Create a multi-stage access review
+.
 In the
 Specify reviewers
 section, in the
@@ -158,7 +159,6 @@ .
 Note
 When creating an access review, you're able to specify the start date, but the start time could vary a few hours based on system processing. For example, if you create an access review at 03:00 UTC on 09/09 that is set to run on 09/12, then the review is scheduled to run at 03:00 UTC on the start date, but could be delayed due to system processing.
-You're able to specify the start date, but the start time can vary a few hours based on system processing.
 Next: Settings
 In the
 Upon completion settings
@@ -178,7 +178,7 @@ Take recommendations
 : Takes the system's recommendation to deny or approve the user's continued access.
 Warning
```

---

### 11. Purview What's New

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

### 1. Security and Governance
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Classification:** MEDIUM (General content update)

---

### 2. Endpoint DLP
**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Classification:** MEDIUM (General content update)

---

### 3. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers
**Classification:** MEDIUM (General content update)

---

### 4. Application Resources
**URL:** https://learn.microsoft.com/en-us/graph/api/resources/application
**Classification:** MEDIUM (General content update)

---

### 5. DLP Cmdlets
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