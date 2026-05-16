# Microsoft Learn Documentation Changes

**Run Date:** 2026-05-10
**Run Time:** 2026-05-10T08:09:53.232467+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 8 |
| HIGH Changes | 27 |
| MEDIUM Changes | 8 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 2 | business-continuity-disaster-recovery | HIGH | 2.4 | Review and update |
| 3 | backup-restore-environments | HIGH | 2.4 | Update portal-walkthrough |
| 4 | environment-strategy | HIGH | 2.4 | Review and update |
| 5 | power-bi-monitor | CRITICAL | 2.6 | Monitor |
| 6 | fundamentals-what-is-copilot-studio | CRITICAL | 2.13 | Monitor |
| 7 | analytics-overview | MEDIUM | 3.2, 3.10, 2.5, 2.6, 2.9 | Update portal-walkthrough |
| 8 | analytics-improve-agent-effectiveness | HIGH | None | Update portal-walkthrough |
| 9 | whats-new | MEDIUM | 2.10 | Review and update |
| 10 | microsoft-365-copilot-overview | HIGH | 3.8 | Review and update |
| 11 | microsoft-365-copilot-privacy | HIGH | 4.7, 4.6, 2.23 | Review and update |
| 12 | manage-copilot-agents-integrated-apps | HIGH | 3.1, 3.11, 3.6, 3.8, 2.25 | Review and update |
| 13 | microsoft-365-copilot-usage | HIGH | 3.8 | Review and update |
| 14 | agent-prerequisites | HIGH | 2.25 | Review and update |
| 15 | m365-agents-visual-map | HIGH | 1.1 | Review and update |
| 16 | m365-agents-blueprint | HIGH | 1.11, 2.1, 2.3 | Review and update |
| 17 | agent-365-overview | HIGH | 3.13, 3.8, 2.25 | Review and update |
| 18 | dlp-policy-reference | HIGH | None | Review and update |
| 19 | sensitivity-labels-teams-groups-sites | CRITICAL | 1.5, 1.3 | Update portal-walkthrough |
| 20 | ...management-settings-policy-indicators | HIGH | 1.12 | Update portal-walkthrough |
| 21 | insider-risk-management-activities | HIGH | 1.12 | Update portal-walkthrough |
| 22 | encryption-sensitivity-labels | HIGH | 1.16 | Review and update |
| 23 | encryption | HIGH | 1.16 | Review and update |
| 24 | overview-authentication | CRITICAL | 1.11 | Monitor |
| 25 | how-to-authentication-passkeys-fido2 | HIGH | None | Review and update |
| 26 | what-is-microsoft-entra-agent-id | HIGH | 1.11, 1.18 | Review and update |
| 27 | agent-id-governance-overview | MEDIUM | 1.11, 3.6, 2.26 | Review optional |
| 28 | external-sharing-overview | CRITICAL | 4.4 | Review and update |
| 29 | turn-external-sharing-on-or-off | HIGH | 1.3, 4.4 | Review and update |
| 30 | restricted-access-control | HIGH | 1.3, 4.1 | Review and update |
| 31 | data-access-governance-reports | HIGH | 1.14, 1.3, 4.4, 4.1, 4.5, 4.2, 4.6 | Update portal-walkthrough |
| 32 | site-lifecycle-management | HIGH | 4.3, 4.2 | Review and update |
| 33 | request-site-attestations | HIGH | 4.2 | Review and update |
| 34 | manage-addins-in-the-admin-center | MEDIUM | 1.2 | Review optional |
| 35 | message-center | HIGH | 2.10 | Review and update |
| 36 | private-link-service | HIGH | 1.20 | Review and update |
| 37 | apply-irm-to-a-list-or-library | HIGH | 1.16 | Review and update |
| 38 | ai-agent-inventory | HIGH | 1.8, 3.7 | Update portal-walkthrough |
| 39 | whats-new | CRITICAL | None | Monitor |
| 40 | microsoft-purview-service-description | HIGH | None | Review and update |
| 41 | requirements-licensing-subscriptions | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Backup and Restore

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments
**Section:** Power Platform Administration
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -23,16 +23,15 @@ Feedback
 Summarize this article for me
 It's important to protect your data on Microsoft Power Platform and in Dataverse and to provide continuous availability of service through system or manual backups.
-System backups are automatically created for environments that have a database. System backups of production environments that have a database and Dynamics 365 applications are retained for up to 28 days. By default, backups of production environments without Dynamics 365 applications and other nonproduction environments are retained for seven days. However, for managed production environments without Dynamics 365 applications, the retention period can be extended up to 28 days using PowerShell.
-Manual backups are backups that the user initiates. It's recommended for creating manual backups before performing major customizations, applying a version update, or making significant changes to the environment. You can create these backups for production and sandbox environments, but not for the default environment. Manual backups of production environments that have Dynamics 365 applications are kept for up to 28 days. Backups of environments that don't have Dynamics 365 applications are kept for seven days.
+System backups are automatically created for environments that have a database. By default, backups of all production and nonproduction environments are retained for seven days. However, for production
+Managed Environments
+, the retention period can be extended up to 28 days through the Power Platform admin center or PowerShell.
+Manual backups are backups that the user initiates. It's recommended that you create manual backups before performing major customizations, applying a version update, or making significant changes to the environment. You can create these backups for production and sandbox environments, but not for the default environment. By default, manual backups are kept for seven days. For production Managed Environment
```

---

### 2. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC 2011-12/SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -31,7 +31,7 @@ and for
 autonomous agents
 .
-Analytics are available in all geographies. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
+Analytics are available in all geographies. Analytics data is available for up to 180 days. Session details and transcript information is available for the last 28 days. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
 Note
 The
 Analytics

```

---

### 3. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -44,7 +44,8 @@ Savings
 area, see
 Analyze time and cost savings for agents
-There are six core areas to focus on when reviewing and improving conversational agent effectiveness:
+There are seven core areas to focus on when reviewing and improving conversational agent effectiveness:
+The Analytics page has seven core areas for reviewing and improving conversational agents effectiveness:
 Themes
 :
 Themes
@@ -59,6 +60,8 @@ : Learning how often tools are used and how often they succeed can help you understand if those tools are useful and successful for users.
 Effectiveness
 : Reviewing user feedback helps you identify new user scenarios and issues, and making improvements based directly on what your users are asking for.
+Knowledge source use
+: Learning how often individual knowledge sources are used and how often they return errors helps you improve the quality and coverage of your agent's answers.
 You can view analytics for events that occurred in the last 90 days.
 Conversation outcomes
 The
@@ -263,36 +266,13 @@ Poor
 quality label. The tooltip also indicates the number of answers sampled to arrive at the calculated percent value.
 In the legend below the chart, hover over any of the quality label reasons to highlight that reason in the chart.
-Select
+Select a segment of the bar chart will open a page of
+user questions
+filtered on that response quality. Select
 See questions
 to
 see an unfiltered list of all questions
 within the configured time period.
-Select
-See details
-to open a side panel with question answer rates, knowledge source usage, and error rates over your selected time period. You can use these charts to identify which knowledge sources work well to help users, and which to target for improvements.
-If your agent has child agents, on the side panel, select
-All
-to display metrics for both the main agent and child agents,
-Main agent
-for metrics about the main agent only, or
-Child agent
-for metrics about child agents only.
-
```

---

### 4. Sensitivity Labels for Sites

**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels-teams-groups-sites
**Section:** Microsoft Purview
**Classification:** CRITICAL (Deprecation notice)

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -417,43 +417,6 @@ Project
 Power BI
 My Apps portal
-Classic Microsoft Entra group classification
-After you enable sensitivity labels for containers, the group classifications from Microsoft Entra ID are no longer supported by Microsoft 365 and won't display on sites that support sensitivity labels. However, you can convert your old classifications to sensitivity labels.
-As an example of how you might have used the old group classification for SharePoint, see
-SharePoint "modern" sites classification
-.
-These classifications were configured by using Microsoft Graph PowerShell or the PnP Core library and defining values for the
-ClassificationList
-setting.
-($setting["ClassificationList"])
-To convert your old classifications to sensitivity labels, do one of the following:
-Use existing labels: Specify the label settings you want for sites and groups by editing existing sensitivity labels that are already published.
-Create new labels: Specify the label settings you want for sites and groups by creating and publishing new sensitivity labels that have the same names as your existing classifications.
-Then:
-Use PowerShell to apply the sensitivity labels to existing Microsoft 365 groups and SharePoint sites by using name mapping. See the next section for instructions.
-Remove the old classifications from the existing groups and sites.
-Although you can't prevent users from creating new groups in apps and services that don't yet support sensitivity labels, you can run a recurring PowerShell script to look for new groups that users have created with the old classifications, and convert these to use sensitivity labels.
-To help you manage the coexistence of sensitivity labels and Microsoft Entra classifications for sites and groups, see
-Microsoft Entra classification and sensitivity labels for Microsoft 365 groups
-.
-Use PowerShell to convert classifications for Microsoft 365 groups to sensitivity labels
-First,
-connect to Security & Compliance PowerShel
```

---

### 5. Insider Risk Indicators

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -309,6 +309,31 @@ data loss prevention (DLP)
 policies. By selecting DLP policies as indicators in Insider Risk Management policies, you can automatically detect if a user has existing alerts in connected DLP policies. DLP policies help protect sensitive information and reduce the risks of oversharing data with inappropriate users or organizations.
 When an Insider Risk Management alert is generated for a user, you can quickly determine if the user has any high risk alerts associated with DLP policies in your organization without having to navigate to DLP solution in the Microsoft Purview portal. You can review and evaluate the Insider Risk Management activity and associated DLP alerts within Insider Risk Management in a unified view.
+Supported DLP workloads
+The High Severity DLP Alert indicator currently supports alerts generated by DLP policies scoped to the following workloads:
+Supported workload
+Description
+Exchange Online
+DLP policy matches on email messages
+SharePoint Online
+DLP policy matches on documents stored in SharePoint sites
+OneDrive for Business
+DLP policy matches on documents stored in OneDrive accounts
+Important
+The following DLP workloads are
+not
+currently supported by the High Severity DLP Alert indicator. Alerts generated by DLP policies that apply exclusively to these workloads won't trigger the indicator and won't appear in Insider Risk Management alerts, cases, or activity views:
+Endpoint DLP
+: DLP policy matches on Windows and macOS devices
+Microsoft Teams
+: DLP policy matches in Teams chat and channel messages
+Microsoft 365 Copilot
+: DLP policy matches in Copilot interactions
+On-premises repositories
+: DLP policy matches on on-premises file shares and SharePoint Server
+Power BI
+: DLP policy matches in Power BI datasets
+This is by design. Only DLP alerts written to the Microsoft 365 audit log by the supported workloads listed above are evaluated by Insider Risk Management. If your DLP policy spans multiple 
```

---

### 6. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-activities
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -19,7 +19,7 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Investigate Insider Risk Management activities
+Investigate Microsoft Purview Insider Risk Management activities
 Feedback
 Summarize this article for me
 Important
@@ -635,6 +635,13 @@ Needs review
 status on the dashboard and quickly dismiss these alerts as benign. You can select up to 400 alerts to dismiss at one time.
 Dismiss an insider risk alert
+To dismiss alerts, you must be a member of the
+Insider Risk Management
+,
+Insider Risk Management Analysts
+, or
+Insider Risk Management Investigators
+role group.
 Sign in to the
 Microsoft Purview portal
 with credentials for an admin account in your Microsoft 365 organization.
@@ -740,7 +747,11 @@ Suggested contacts
 list, select the appropriate admin.
 Create a case for an alert
-Create a case for an alert to investigate potentially risky activity.
+Create a case for an alert to investigate potentially risky activity. You must be a member of the
+Insider Risk Management
+or
+Insider Risk Management Investigators
+role group to create a case.
 Sign in to the
 Microsoft Purview portal
 with credentials for an admin account in your Microsoft 365 organization.

```

---

### 7. Data Access Governance Reports

**URL:** https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports
**Section:** SharePoint Administration
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.2/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -22,7 +22,7 @@ Data access governance reports for SharePoint and OneDrive sites
 Feedback
 Summarize this article for me
-As sprawl and oversharing of SharePoint sites increase with exponential data growth, organizations need help with governing their data. Data access governance reports can help you govern access to SharePoint data. The reports let you discover sites that contain potentially overshared or sensitive content. You can use these reports to assess and apply the appropriate security and compliance policies.
+As sprawl and oversharing of SharePoint sites increase with exponential data growth, organizations need help with governing their data. Data access governance reports can help you govern access to SharePoint data. The reports let you discover sites that contain potentially overshared or sensitive content. You can use these reports to assess and apply the appropriate security and compliance policies.
 What you need to create a data access governance report
 License requirements
 Your organization needs to have the right
@@ -47,7 +47,7 @@ For organizations without a Copilot license, you can use SharePoint Advanced Management features
 by purchasing a standalone SharePoint Advanced Management license
 .
-Data governance access reports are available in nongovernment cloud environments, as well as GCC, GCC-High, and DoD government cloud environments. The reports are currently unavailable for Gallatin, even if you have the required licenses.
+The reports are currently unavailable for Gallatin, even if you have the required licenses.
 How to access the Data access governance reports in the SharePoint admin center
 Sign in to the
 SharePoint admin center
@@ -68,18 +68,18 @@ Sharing links
 Shared with 'Everyone except external users'
 Note
-IT administrators with Microsoft 365 E5 licensing can access Data access governance reporting, but are unable to view or utilize the other
+IT administrators with Microsoft 365 E5 licensing can access Data acces
```

---

### 8. Defender for Cloud Apps - AI Inventory

**URL:** https://learn.microsoft.com/en-us/defender-cloud-apps/ai-agent-inventory
**Section:** Microsoft Defender
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/3.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -19,7 +19,7 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Discover and protect your Copilot Studio AI Agents (Preview)
+Discover and protect AI agents with Microsoft Defender (Preview)
 Feedback
 Summarize this article for me
 Microsoft Defender detects all Copilot Studio custom AI agents in your tenant and provides tools to identify misconfigured or potentially risky agents, and collects data from Copilot Studio for use in
@@ -27,14 +27,11 @@ .
 Prerequisites
 To enable AI agent inventory and detection, you must:
-Have one of the following:
-A Microsoft Agent 365 license.
-Both a Microsoft Defender for Cloud Apps license and a Microsoft Copilot Studio license.
+Have a Microsoft Agent 365 license
+Until July 1, 2026, you can access the Copilot Studio AI agent inventory and detection without a Microsoft Agent 365 license if you:
+Have a Microsoft Defender for Cloud Apps license
 Opt in to the
-Microsoft Defender preview features
-of:
-Microsoft Defender for Cloud
-Microsoft Defender XDR
+Microsoft Defender for Cloud apps and Defender XDR preview features
 Enable discovery of Copilot Studio AI agents
 After you enable Security for AI, Microsoft Defender automatically discovers all Copilot Studio custom AI agents in your tenant. After discovery, you can view your agents in the
 AI agent inventory

```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -110,6 +110,8 @@ By: Adobe
 Adobe PDF Services
 By: Adobe Acrobat Services
+ADP Employee Self-Service
+By: ADP, Inc.
 Advanced Data Operations
 By: State Solutions
 Advanced Scraper (Independent Publisher)
@@ -194,7 +196,7 @@ By: Troy Taylor
 ANY.RUN Threat Intelligence
 By: ANYRUN FZCO
-Apache Impala
+Apache Impala [DEPRECATED]
 By: Microsoft
 APITemplate (Independent Publisher)
 By: Troy Taylor
@@ -267,6 +269,8 @@ Aviationstack (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 AWeber
+By: Microsoft
+Azure - Foundry IQ
 By: Microsoft
 Azure AD Identity and Access
 By: Microsoft, Daniel Laskewitz
@@ -614,6 +618,8 @@ By: Troy Taylor
 Cohesity Gaia
 By: Cohesity, Inc.
+Cohesity Gaia MCP
+By: Cohesity, Inc.
 Coinbase (Independent Publisher)
 By: Roy Paar
 Commercient
@@ -844,6 +850,8 @@ By: DocuSign, Inc.
 Docusign Demo
 By: DocuSign, Inc.
+Docusign MCP Demo
+By: DocuSign, Inc.
 DocuWare
 By: DocuWare
 Dokobit Portal
@@ -1000,8 +1008,6 @@ By: Encodian
 Encodian [DEPRECATED]
 By: Encodian
-Encodian Filer
-By: Encodian
 Engagement Cloud
 By: dotdigital
 Enlyft Insights
@@ -1246,6 +1252,8 @@ By: Reenhanced LLC
 Gravity Forms Professional
 By: Reenhanced, LLC
+Gravity SMS
+By: Clark County Tech
 Groopit
 By: Groopit
 GroupMgr
@@ -1393,9 +1401,9 @@ iLovePDF
 By: i Love PDF
 iLovePDFv2
-By: i Love PDF
+By: iLovePDF
 iLoveSign
-By: i Love PDF
+By: iLoveSign
 iLoveSign [DEPRECATED]
 By: i Love PDF
 iManage AI
@@ -1788,6 +1796,8 @@ By: Troy Taylor
 Mitto
 By: Mitto AG
+Mizorix Filer
+By: Mizorix Ltd
 Mobile Text Alerts MCP Server
 By: Mobile Text Alerts
 Mobili Stotele
@@ -2915,7 +2925,7 @@ Vimeo
 By: Microsoft
 Virtual Data Platform
-By: Virtual_Data_Platform_GmbH
+By: Virtual Data Platform GmbH
 Virus Total
 By: Microsoft
 Viva Engage
@@ -2982,9 +2992,9 @@ By: Microsoft
 Workable (Independent Publisher)
 By: David Kjell
+Workday

```

---

### 2. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**What Changed:**
```diff
--- +++ @@ -164,6 +164,9 @@ Pay-as-you-go links the selected environment to the Azure subscription by using a billing policy. Once you link an environment to an Azure subscription, the usage of apps and any Dataverse or Power Platform usage that goes above the included storage amounts are billed against the Azure subscription by using Azure meters. For more information, go to
 Pay-as-you-go meters
 . If you acquire more storage entitlements, the pay-as-you-go plan stops running the meters and consuming from available free storage and entitlements take precedence.
+What are the recovery point and recovery time objectives with business continuity and disaster recovery?
+Power Platform and Dataverse are designed with high availability built into every region. Within a region, the platform targets approximately near zero recovery point objective (RPO) and a recovery time of under five minutes across availability zones and data centers within a region. For cross-region resiliency, Microsoft provides self-service disaster recovery, which gives customers full visibility and control over the failover process.
+In this model, typical replication lag is under 15 minutes (often under five minutes), and the platform is designed to complete failover within minutes once initiated. Because customers retain control of when and whether to trigger a cross-region failover, Microsoft doesn't publish a cross-region RTO commitment. However, customers can monitor real-time replication lag directly in the Power Platform admin center to inform their own recovery decisions. It's also important to note that when Power Platform solutions connect to external systems, such as SQL Server, REST APIs, or other third-party services, the RPO of those integrations are governed by the availability and recovery capabilities of the respective target systems, and fall outside the scope of Power Platform's resiliency commitments.
 How does billing work for self-service disaster recovery?
 If you configure 
```

---

### 3. Environment Strategy

**URL:** https://learn.microsoft.com/en-us/power-platform/guidance/adoption/environment-strategy
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**What Changed:**
```diff
--- +++ @@ -69,7 +69,9 @@ Default
 The environment that comes with every tenant. Many Microsoft 365 experiences use this environment for customizations and automations. This environment isn't intended for long-term or permanent work beyond the Microsoft 365 personal, productivity scenarios.
 Production
-This environment is intended to be used for permanent work in an organization. Production environments support extended, back-up retention, from seven days to up to 28 days.
+This environment is intended to be used for permanent work in an organization. Production
+Managed Environments
+support extended back-up retention from seven days to up to 28 days.
 Sandbox
 These nonproduction environments support environment actions like copy and reset. Sandboxes are best used for testing and ALM build environments.
 Developer

```

---

### 4. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -150,7 +150,7 @@ Microsoft 365 Copilot to Copilot Studio
 . Easily move agents you created in Microsoft 365 Copilot into Copilot Studio to unlock advanced capabilities like multistep workflows, custom integrations, and broader deployment options.
 (Preview) Add human input to agent workflows with the
-request for information
+request information
 action. Pause an agent flow to collect details from designated reviewers via Outlook, then resume execution using their responses as dynamic parameters. This action ensures workflows can handle missing data or context without relying on hard-coded values.
 Update Power Platform API calls to use the
 new 'copilotstudio' namespace

```

---

### 5. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -132,50 +132,50 @@ Feature
 Word
 Draft
-âGenerate text with and without formatting in new or existing documents. Word files can also be used for grounding data.
+-Generate text with and without formatting in new or existing documents. Word files can also be used for grounding data.
 Chat
-âCreate content, summarize, ask questions about your document, and do light commanding.
+-Create content, summarize, ask questions about your document, and do light commanding.
 PowerPoint
 Draft
-âCreate a new presentation from a prompt or Word file using enterprise templates. PowerPoint files can also be used for grounding data.
+-Create a new presentation from a prompt or Word file using enterprise templates. PowerPoint files can also be used for grounding data.
 Chat
-âSummary and Q&A
+-Summary and Q&A
 Light commanding
-âAdd slides, pictures, or make deck-wide formatting changes.
+-Add slides, pictures, or make deck-wide formatting changes.
 Excel
 Draft
-âGet suggestions for formulas, chart types, and insights about data in your spreadsheet.
+-Get suggestions for formulas, chart types, and insights about data in your spreadsheet.
 Loop
 Collaborative content creation
-âCreate content that can be collaboratively improved through direct editing.
+-Create content that can be collaboratively improved through direct editing.
 Outlook
 Coaching tips
-âGet coaching tips and suggestions on clarity, sentiment, and tone, and an overall message assessment and suggestions for improvement.
+-Get coaching tips and suggestions on clarity, sentiment, and tone, and an overall message assessment and suggestions for improvement.
 Summarize
-âSummarize an email thread to quickly understand the discussion.
-Draft
-âPull from other emails or content across Microsoft 365 that the user already has access to.
+-Summarize an email thread to quickly understand the discussion.
+Draft
+-Pull from other emails or content across Microsoft 365 that the user already has access
```

---

### 6. Data, Privacy, and Security

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**What Changed:**
```diff
--- +++ @@ -62,20 +62,20 @@ Microsoft 365 Copilot community
 on the Microsoft Tech Community.
 How does Microsoft 365 Copilot use your proprietary organizational data?
-Microsoft 365 Copilot provides value by connecting LLMs to your organizational data. Microsoft 365 Copilot accesses content and context through Microsoft Graph. It can generate responses anchored in your organizational data, such as user documents, emails, calendar, chats, meetings, and contacts. Microsoft 365 Copilot combines this content with the userâs working context, such as the meeting a user is in now, the email exchanges the user had on a topic, or the chat conversations the user had last week. Microsoft 365 Copilot uses this combination of content and context to help provide accurate, relevant, and contextual responses.
+Microsoft 365 Copilot provides value by connecting LLMs to your organizational data. Microsoft 365 Copilot accesses content and context through Microsoft Graph. It can generate responses anchored in your organizational data, such as user documents, emails, calendar, chats, meetings, and contacts. Microsoft 365 Copilot combines this content with the user's working context, such as the meeting a user is in now, the email exchanges the user had on a topic, or the chat conversations the user had last week. Microsoft 365 Copilot uses this combination of content and context to help provide accurate, relevant, and contextual responses.
 Important
 Prompts, responses, and data accessed through Microsoft Graph aren't used to train foundation LLMs, including those used by Microsoft 365 Copilot.
 Microsoft 365 Copilot only surfaces organizational data to which individual users have at least view permissions. It's important that you're using the permission models available in Microsoft 365 services, such as SharePoint, to help ensure the right users or groups have the right access to the right content within your organization. This includes permissions you give to users outside your o
```

---

### 7. Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -53,11 +53,11 @@ Agent types you can manage
 You can manage several types of agents in Microsoft 365 Copilot, each serving different purposes:
 Published by your organization
-:â¯Built with predefined instructions and actions. These agents follow structured logic and are best for predictable, rule-based tasks. Before agents become available to users, these agents go through an admin approval and publishing process to ensure compliance and readiness.
+: Built with predefined instructions and actions. These agents follow structured logic and are best for predictable, rule-based tasks. Before agents become available to users, these agents go through an admin approval and publishing process to ensure compliance and readiness.
 Note
 Publishing agents to the organization is supported in Microsoft 365 Government Community Cloud High (GCCH) and Government Community Cloud Moderate (GCCM) environments.
 Shared by creator
-:â¯Shared agents are custom versions of Microsoft 365 Copilot that combine instructions, knowledge, and skills to perform specific tasks or scenarios. Creators can create and share these agents through multiple channels, such as Microsoft 365 Copilot Studio, Microsoft 365 Copilot Agent Builder, and more. Shared agents enhance the functionality of Copilot by adding search capabilities, custom actions, connectors, and APIs. For more information, see
+: Shared agents are custom versions of Microsoft 365 Copilot that combine instructions, knowledge, and skills to perform specific tasks or scenarios. Creators can create and share these agents through multiple channels, such as Microsoft 365 Copilot Studio, Microsoft 365 Copilot Agent Builder, and more. Shared agents enhance the functionality of Copilot by adding search capabilities, custom actions, connectors, and APIs. For more information, see
 Share agents with other users
 .
 As an admin, you can view shared agents on the
@@ -65,11 +65,11 @@ page in the Microsoft 365 admin center. You can see a 
```

---

### 8. Copilot Usage Reports

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -33,7 +33,7 @@ Go to the
 Microsoft 365 admin center
 .
-In the navigation menu, selectâ¯
+In the navigation menu, select
 Reports
 . If you don't see
 Reports
@@ -73,7 +73,7 @@ Microsoft Copilot Dashboard
 , where you can deliver insights to your IT leaders to explore Copilot readiness, adoption, and impact in Viva Insights.
 Active agent users
-shows the total number of unique Microsoft 365 Copilot users in your org who used agents built by your org (including admin-approved agents and agents created via agent builderâ¯and shared with users in your org).
+shows the total number of unique Microsoft 365 Copilot users in your org who used agents built by your org (including admin-approved agents and agents created via agent builder and shared with users in your org).
 Note
 Agent usage is available starting November 1, 2024, and is currently limited to agents built by your org. Usage of agents built by Microsoft and Microsoft Partners will be introduced in the coming months.
 Total prompts submitted
@@ -229,7 +229,7 @@ Welcome to Copilot in OneNote - Microsoft Support
 .
 Loop
-All Copilot in Loop features are automatically included in the Microsoft 365 Copilot usage report. Usage of any Copilot in Loop feature counts towards the Active users metric and is indicated in the per-user Last activity date (UTC). User views of Loop documents generated by the Facilitator feature in Teams meetings are included in active usage for the Loop app and all up Microsoft 365 Copilot usage, effective December 11, 2025.
+All Copilot in Loop features are automatically included in the Microsoft 365 Copilot usage report. Usage of any Copilot in Loop feature counts towards the Active users metric and is indicated in the per-user Last activity date (UTC). User views of Loop documents generated by the Facilitator feature in Teams meetings are included in active usage for the Loop app and all up Microsoft 365 Copilot usage, effective December 11, 2025.
 To learn more about Copil
```

---

### 9. Agent Prerequisites

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-prerequisites
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -22,11 +22,11 @@ Prerequisites for managing agents in Microsoft 365
 Feedback
 Summarize this article for me
-Organizations typically deploy a combination of Microsoft 365 Copilot Chat and Microsoft 365 Copilot. Before you get started, it's important to understand the differences between these two offerings and the licensing involved when deploying and using agents. Agents allow you and your end users to extend Copilotâs knowledge, automate complex workflows, and deliver tailored user experiences.
+Organizations typically deploy a combination of Microsoft 365 Copilot Chat and Microsoft 365 Copilot. Before you get started, it's important to understand the differences between these two offerings and the licensing involved when deploying and using agents. Agents allow you and your end users to extend Copilot's knowledge, automate complex workflows, and deliver tailored user experiences.
 Note
-Before your organization assigns or deploys an agent, first consider your organizationâs objectives, technical requirements, costs, Responsible AI (RAI) considerations, and compliance factors. For more information, see Microsoft 365 Copilot extensibility planning guide.
+Before your organization assigns or deploys an agent, first consider your organization's objectives, technical requirements, costs, Responsible AI (RAI) considerations, and compliance factors. For more information, see Microsoft 365 Copilot extensibility planning guide.
 Licensing requirements
-Microsoft 365 Copilot Chat is available at no additional cost for all Microsoft Entra account users with a Microsoft 365 or Office 365 subscription. Members of your organization can use agents that are available at no additional cost from the Agent Store. You, as the administrator of your organization, would also need to enable these agents. If your organization requires agents that incorporate your organizationâs data, you can provide access to
+Microsoft 365 Copilot Chat is available at no additional cos
```

---

### 10. Visual Governance Guide

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-visual-map
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`

**What Changed:**
```diff
--- +++ @@ -51,7 +51,7 @@ Microsoft 365 agents deployment checklist
 .
 Manage Microsoft 365 Copilot agent inventory and lifecycle
-You can manage your organizationâs available agents in the Copilot Control System (CCS) within Microsoft 365 admin center. For more information, see
+You can manage your organization's available agents in the Copilot Control System (CCS) within Microsoft 365 admin center. For more information, see
 Microsoft 365 agents deployment checklist
 .
 Manage Data Access - Data security, compliance, and governance

```

---

### 11. Deployment Blueprint

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-blueprint
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`

**What Changed:**
```diff
--- +++ @@ -24,7 +24,7 @@ Summarize this article for me
 This deployment blueprint helps you enable agents in
 Microsoft 365 Copilot
-at scale, while ensuring data security and governance, managing access and costs, and measuring adoption and impact.
+at scale, while ensuring data security and governance, managing access and costs, and measuring adoption and impact.
 Note
 This blueprint is scoped primarily to agents created in the
 Agent Builder
@@ -33,17 +33,17 @@ Security and governance concerns
 - Your organization can address oversharing, data protection, and compliance risks by implementing robust security and governance controls to safely enable agents in Microsoft 365 Copilot.
 Deployment complexity
-- Agents in Microsoft 365 Copilot introduce new admin tools and processes. This guidance can help address user enablement and cost management complexity.
-Visibility and impact gaps
-- By reviewing and acting on agent data, you can better measure success. Agent data can also provide usage to manage costs and help assess business value.
+- Agents in Microsoft 365 Copilot introduce new admin tools and processes. This guidance can help address user enablement and cost management complexity.
+Visibility and impact gaps
+- By reviewing and acting on agent data, you can better measure success. Agent data can also provide usage to manage costs and help assess business value.
 By addressing these challenges, you can better drive innovation while maintaining security, control, and visibility. This blueprint can help, by providing shorter, actionable, and prescriptive guidance.
 In this deployment blueprint, we provide a recommended approach to address concerns throughout a Microsoft 365 Copilot agent deployment. The blueprint breaks the deployment into three phases:
 Prepare
-â Set the foundation before enabling agents.
+- Set the foundation before enabling agents.
 Deploy
-â Enable agents in a controlled manner.
+- Enable agents in a controlled manner.
 Manage
-â 
```

---

### 12. Agent 365 Overview Page (M365 Admin)

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.25/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -26,7 +26,7 @@ Agent governance involves using policies, settings, and admin actions to control how agents at your organization are accessed, published, deployed, and managed across your organization. When you apply an agent governance approach to managing agents, you ensure agents and the data they use remain secure and compliant.
 By using governance across your agent lifecycle, you help ensure agent adoption is consistent and safe. Governance ensures agents onboard intentionally, operate within guardrails, and are managed consistently from build through retirement.
 Organizations face significant challenges related to agent governance, including the following:
-How to apply consistent governance policies across all agents, regardless of how or where theyâre built.
+How to apply consistent governance policies across all agents, regardless of how or where they're built.
 How to balance developer freedom and experimentation with centralized oversight.
 How to identify and retire low value or ownerless agents before they create risk or cost.
 By managing agents within Microsoft 365 admin center, organizations can establish these guardrails for agents and people, onboard agents with IT oversight, and govern agent access to resources and data, thereby meeting the challenges that organization face. In addition, organizations track their governance approach with built-in compliance and data retention details.
@@ -170,7 +170,9 @@ - Total hours worked by agents during the last 30 days, calculated from when a user request begins to when it is completed, and aggregated across all agent activities, such as executing tool calls and preparing responses.
 This metric begins when your organization activates Agent 365 licenses, so it will reflect fewer than 30 days of data immediately after activation. As activity accumulates, the metric will progressively reflect a fuller 30-day view.
 Registry sync
-- The external connected platforms that were scanned. You can conne
```

---

### 13. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -19,31 +19,9 @@ Access to this page requires authorization. You can try
 changing directories
 .
+Data Loss Prevention policy reference
 Feedback
 Summarize this article for me
-title: "Data Loss Prevention policy reference"
-f1.keywords: CSH
-ms.author: chrfox
-author: chrfox
-manager: laurawi
-ms.date: [DATE]
-audience: Admin
-ms.topic: reference
-ms.service: purview
-ms.subservice: purview-data-loss-prevention
-search.appverid:
-SPO160
-MET150
-ms.assetid: 6501b5ef-6bf7-43df-b60d-f65781847d6c
-ms.collection:
-highpri
-purview-compliance
-SPO_Content
-recommendations: false
-description: "DLP policy component and configuration reference. This article provides a detailed anatomy of a DLP policy."
-ms.custom: seo-marvel-apr2021
-ai-usage: ai-assisted
-Data Loss Prevention policy reference
 Microsoft Purview Data Loss Prevention (DLP) policies have many components to configure. To create an effective policy, you need to understand what the purpose of each component is and how its configuration alters the behavior of the policy. This article provides a detailed anatomy of a DLP policy.
 Tip
 Get started with Microsoft Security Copilot to explore new ways to work smarter and faster using the power of AI. Learn more about

```

---

### 14. Information Rights Management

**URL:** https://learn.microsoft.com/en-us/purview/encryption-sensitivity-labels
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

**What Changed:**
```diff
--- +++ @@ -48,8 +48,8 @@ Understand how the encryption works
 Unless you're using
 S/MIME for Outlook
-, encryption that's applied by sensitivity labels to documents, emails, and meeting invites all use the Azure Rights Management service (Azure RMS) from Microsoft Purview Information Protection. This protection solution uses encryption, identity, and authorization policies. To learn more, see
-What is Azure Rights Management?
+, encryption that's applied by sensitivity labels to documents, emails, and meeting invites all use the Azure Rights Management service from Microsoft Purview Information Protection. This protection solution uses encryption, identity, and authorization policies. To learn more, see
+Learn about the Azure Rights Management encryption service
 .
 When you use this encryption solution, the
 super user
@@ -76,8 +76,8 @@ There are some Microsoft Entra configurations that can prevent authorized access to encrypted content. For example, cross-tenant access settings and Conditional Access policies. For more information, see
 Microsoft Entra configuration for encrypted content
 .
-Configure Exchange for Azure Rights Management
-Exchange doesn't have to be configured for Azure Rights Management before users can apply labels in Outlook to encrypt their emails. However, until Exchange is configured for Azure Rights Management, you don't get the full functionality of encryption with rights management.
+Configure Exchange for the Azure Rights Management service
+Exchange doesn't have to be configured for the Azure Rights Management service before users can apply labels in Outlook to encrypt their emails. However, until Exchange is configured for the Azure Rights Management service, you don't get the full functionality of encryption with rights management.
 For example, users can't view encrypted emails or encrypted meeting invites on mobile phones or with Outlook on the web, encrypted emails can't be indexed for search, and you can't configure Exchange Onl
```

---

### 15. Encryption

**URL:** https://learn.microsoft.com/en-us/purview/encryption
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

**What Changed:**
```diff
--- +++ @@ -56,7 +56,7 @@ Data Encryption in OneDrive and SharePoint
 Skype for Business Online: Security and Archiving
 Email in transit between recipients. This email includes email hosted by Exchange Online.
-Microsoft Purview Message Encryption with Azure Rights Management, S/MIME, and TLS for email in transit
+Microsoft Purview Message Encryption with the Azure Rights Management service, S/MIME, and TLS for email in transit
 Message Encryption
 Email encryption in Microsoft 365
 How Exchange Online uses TLS to secure email connections in Microsoft 365
@@ -70,8 +70,7 @@ What if I need more control over encryption to meet security and compliance requirements?
 Microsoft 365 provides Microsoft-managed solutions for volume encryption, file encryption, and mailbox encryption in Microsoft 365. In addition, Microsoft provides encryption solutions that you can manage and control. These encryption solutions are built on Azure.
 To learn more, see the following resources:
-What is Azure Rights Management?
-Activate Rights Management in the admin center
+Learn about the Azure Rights Management encryption service
 Set up Information Rights Management (IRM) in SharePoint admin center
 Overview of Customer Key
 Double Key Encryption

```

---

### 16. FIDO2 Security Keys

**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-authentication-passkeys-fido2
**Section:** Microsoft Entra ID
**Classification:** HIGH (Policy language)

**What Changed:**
```diff
--- +++ @@ -264,9 +264,6 @@ Note
 Treat synced passkeys as phishing-resistant credentials but with the same security posture as other unattested authenticators.
 Synced passkey requirements
-To enable synced passkeys, your organization must have
-passkey profiles
-enabled.
 An account with at least
 Authentication Policy Administrator
 permissions.
@@ -292,6 +289,7 @@ Check for an app. iOS 17+
 Check for an app. Android 14+
 Enable synced passkeys
+If you haven't opted in to passkey profiles yet and you have attestation enforcement off, synced passkeys are already enabled. Otherwise, you can follow these steps to enable synced passkeys:
 Sign in to the Microsoft Entra admin center as at least an
 Authentication Policy Administrator
 .

```

---

### 17. Agent Identities for AI Agents

**URL:** https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**What Changed:**
```diff
--- +++ @@ -30,6 +30,9 @@ enables developers to create and manage
 agent identities
 , which are specialized identity constructs built for AI agents. Agent identity blueprints serve as templates for creating individual agent identities with parent-child relationships, enabling consistent security policies across large numbers of agents. The platform supports standard protocols such as OAuth 2.0, MCP, and A2A for authentication and agent-to-agent communication.
+Microsoft Entra Agent ID works with agents built on Microsoft and non-Microsoft platforms. Organizations can
+integrate third-party agents
+from platforms such as AWS Bedrock and n8n by using the Microsoft Entra Auth SDK (sidecar) or workload identity federation, giving every agent a governed identity regardless of where it was built.
 Security and governance for agents
 Microsoft Entra Agent ID extends existing Microsoft Entra security and governance capabilities to agent identities. Agents receive the same identity-driven protections as users and workloads, including adaptive access policies, real-time risk detection, lifecycle management, and network-level controls. All agent authentication and activity is logged for compliance and audit.
 For details on how these capabilities work for agents, see:
@@ -55,7 +58,7 @@ ID Protection for agents
 : Microsoft Entra ID P2, Microsoft 365 E5, or Microsoft Entra Suite.
 ID Governance for agents
-: Microsoft Entra ID P2, Microsoft 365 E5, or Microsoft Entra Suite.
+: Microsoft Entra ID P1 or Microsoft 365 E3.
 Network controls for agents
 : Microsoft Entra Internet Access, included in Microsoft Entra Suite or licensed separately. For more information, see
 What is Global Secure Access

```

---

### 18. External Sharing

**URL:** https://learn.microsoft.com/en-us/sharepoint/external-sharing-overview
**Section:** SharePoint Administration
**Classification:** CRITICAL (Deprecation notice)

**Affected Controls:**
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -23,14 +23,14 @@ Feedback
 Summarize this article for me
 Note
-As of June 2024, invitations sent via the legacy SharePoint Invitation Manager no longer grant access. Users must reshare documents to generate valid invitations.
+As of June 2024, invitations sent through the legacy SharePoint Invitation Manager no longer grant access. Users must reshare documents to generate valid invitations.
 External sharing in SharePoint and OneDrive allows users to share content with people outside your organization, such as partners, vendors, clients, or customers. You can also use external sharing to share between licensed users on multiple Microsoft 365 subscriptions. External sharing in SharePoint is part of
 secure collaboration with Microsoft 365
-. Also read
+. Also see
 Overview of external collaboration options in Microsoft 365
 .
 Important
-Trial tenants can utilize SharePoint's robust collaboration features, but the scope of external sharing will be restricted compared to licensed tenants. This is designed to prevent potential abuse and ensure a safe experience for all users.
+Trial tenants can use SharePoint's robust collaboration features, but the scope of external sharing is restricted compared to licensed tenants. This restriction helps prevent potential abuse and ensures a safe experience for all users.
 Include external sharing as part of your overall permissions planning for SharePoint and OneDrive. This article describes what happens when users share, depending on what they're sharing and with whom.
 If you want to get straight to setting up sharing, choose the scenario you want to enable:
 Collaborate with guests on a document
@@ -42,16 +42,16 @@ Share SharePoint files or folders in Microsoft 365
 .)
 Note
-External sharing is turned on by default for your entire SharePoint and OneDrive environment. You may want to
+External sharing is turned on by default for your entire SharePoint and OneDrive environment. You might want to
 turn it off globally

```

---

### 19. Manage Sharing Settings

**URL:** https://learn.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -22,13 +22,13 @@ Manage sharing settings for SharePoint and OneDrive in Microsoft 365
 Feedback
 Summarize this article for me
-As a SharePoint Administrator in Microsoft 365, you can change the organization-level sharing settings for SharePoint and OneDrive. These settings control sharing at the organization level, and you can then configure more restrictive settings for specific sites if needed.
-For end-to-end guidance around how to configure guest sharing in Microsoft 365, see:
+As a SharePoint Administrator in Microsoft 365, you can change the organization-level sharing settings for SharePoint and OneDrive. These settings control sharing at the organization level. You can configure more restrictive settings for specific sites if needed.
+For end-to-end guidance on how to configure guest sharing in Microsoft 365, see:
 Set up secure collaboration with Microsoft 365
 Collaborate with guests on a document
 Collaborate with guests in a site
 Collaborate with guests in a team
-To change the sharing settings for a site after you've set the organization-level sharing settings, see
+To change the sharing settings for a site after you set the organization-level sharing settings, see
 Change sharing settings for a site
 . To learn how to change the external sharing setting for a specific user's OneDrive, see
 Change the external sharing setting for a user's OneDrive
@@ -40,12 +40,12 @@ Set up SharePoint in Microsoft 365 guide
 in the Microsoft 365 admin center.
 How do SharePoint and OneDrive integrate with Microsoft Entra B2B?
-There are two external sharing models used in SharePoint and OneDrive:
+SharePoint and OneDrive use two external sharing models:
 SharePoint external authentication
 SharePoint and OneDrive integration with Microsoft Entra B2B
-When using Microsoft Entra B2B integration, Microsoft Entra external collaboration settings, such as
+When you use Microsoft Entra B2B integration, Microsoft Entra external collaboration settings, such as
 guest
```

---

### 20. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`

**What Changed:**
```diff
--- +++ @@ -22,9 +22,9 @@ Restrict SharePoint site access with Microsoft 365 groups and Microsoft Entra security groups
 Feedback
 Summarize this article for me
-Restricted site access control lets you prevent oversharing by designating access of SharePoint sites and its content to users in a specific group. Users not in the specified group can't access the site or its content, even if they had prior permissions or a shared link. This policy can be applied on Microsoft 365 group-connected, Teams-connected, and nongroup connected sites using Microsoft 365 groups or Microsoft Entra security groups.
-Site access restriction policies are applied when a user attempts to open a site or access a file. Users with direct permissions to the file can still view files in search results. However, they can't access the files if they're not part of the specified group.
-Restricting site access via group membership can minimize the risk of oversharing content. For insights into data sharing, see
+Restricted site access control helps prevent oversharing by designating access of SharePoint sites and its content to users in a specific group. Users not in the specified group can't access the site or its content, even if they had prior permissions or a shared link. You can apply this policy on Microsoft 365 group-connected, Teams-connected, and nongroup connected sites by using Microsoft 365 groups or Microsoft Entra security groups.
+Site access restriction policies take effect when a user attempts to open a site or access a file. Users with direct permissions to the file can still view files in search results. However, they can't access the files if they're not part of the specified group.
+Restricting site access through group membership can minimize the risk of oversharing content. For insights into data sharing, see
 Data access governance reports
 .
 What do you need to restrict site access?
@@ -71,20 +71,20 @@ Set-SPOTenant -EnableRestrictedAccessControl $true
 It might take up t
```

---

### 21. Site Lifecycle Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/site-lifecycle-management
**Section:** SharePoint Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -22,11 +22,10 @@ Manage inactive sites by using inactive site policies
 Feedback
 Summarize this article for me
-The site lifecycle management features from
+Site lifecycle management capabilities in
 Microsoft SharePoint Advanced Management
-help you improve site governance by automating policy configuration in the
-SharePoint admin center
-. Inactive site policies, part of SharePoint's site lifecycle management features, help you automate this process. You can set up an inactive site policy to automatically detect inactive sites and notify site owners by email. Owners can then confirm if the site is still active.
+help you improve site governance by automating the process of detecting inactive sites and notifying site owners by email. Site owners can then review and confirm whether their sites are still active.
+You can configure an inactive sites policy in the SharePoint admin center. This article describes how to set up an inactive site policy with notifications and enforcement actions.
 What do you need to create an inactive site policy?
 License requirements
 Your organization needs to have the right

```

---

### 22. Site Attestation

**URL:** https://learn.microsoft.com/en-us/sharepoint/request-site-attestations
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**What Changed:**
```diff
--- +++ @@ -22,13 +22,10 @@ Request recurring site attestations for SharePoint sites
 Feedback
 Summarize this article for me
-The site lifecycle management features in
+Site lifecycle management policies in
 Microsoft SharePoint Advanced Management
-help your organization improve site governance by automating policy configuration in the
-SharePoint admin center
-. Site attestation policies, part of SharePoint's site lifecycle management features, help you manage periodic attestation of sites at scale.
-Site attestation involves regular reviews by site owners or site admins to check and confirm the accuracy of site information, including the site's necessity, its owners, members, permissions, and sharing settings. For sites that remain unattested, you can choose to automate enforcement actions to prevent risks of content overexposure. This approach ensures ongoing site compliance and actively reduces risks such as information oversharing.
-This article describes how to create and configure a site attestation policy.
+help your organization improve site governance. Site attestation involves regular reviews by site owners or site administrators to check and confirm the accuracy of site information, including the site's necessity, its owners, members, permissions, and sharing settings. For sites that remain unattested, you can choose to automate enforcement actions to prevent risks of content overexposure. This approach ensures ongoing site compliance and actively reduces risks such as information oversharing.
+Site attestation policies help you manage periodic attestation of sites at scale. You can configure a site attestation policy in the SharePoint admin center. This article describes how to create and configure a site attestation policy in either active or simulation mode.
 Requirements for a site attestation policy
 License requirements
 Your organization needs to have the right
@@ -93,21 +90,21 @@ Selecting sites at scale
 On the
 Configure policy
-step, you can
```

---

### 23. Message Center

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide
**Section:** Microsoft 365 Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**What Changed:**
```diff
--- +++ @@ -136,7 +136,7 @@ Tags
 drop-down.
 Major updates are communicated at least 30 days in advance when an action is required and might include:
-User impacting changes to daily productivity such as changing a userâs inbox, meetings, delegations, sharing and access that might result in help desk calls, or organizational conformance concerns.
+User impacting changes to daily productivity such as changing a user's inbox, meetings, delegations, sharing and access that might result in help desk calls, or organizational conformance concerns.
 Changes to the themes, web parts, deployed Copilot agents, and other components that might impact customer customizations.
 Increases or decreases to visible capacity such as storage, number of rules, Copilot agents and prompts, items, or durations.
 Rebranding that might cause end-user confusion or result in help desk changes, collateral changes, or URL changes if the new URL isn't *.cloud.microsoft
@@ -254,7 +254,7 @@ Updated message
 : When a message is updated.
 Platform
-The platform thatâs affected by the Message center post.
+The platform that's affected by the Message center post.
 Category
 This column isn't shown by default, but can be specified in the
 Choose columns

```

---

### 24. Key Vault Private Endpoints

**URL:** https://learn.microsoft.com/en-us/azure/key-vault/general/private-link-service
**Section:** Azure Services
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 1.20: Control 1.20: Network Isolation and Private Connectivity
  - File: `controls/pillar-1-security/1.20-network-isolation-private-connectivity.md`

**What Changed:**
```diff
--- +++ @@ -176,6 +176,26 @@ Address: 10.1.0.5 (private IP address)
 Aliases: <vault-name>.vault.azure.net
  <vault-name>.privatelink.vaultcore.azure.net
+Public DNS visibility of a private key vault
+A key vault that uses a private endpoint with public access disabled is still resolvable in public DNS. The FQDN
+<vault-name>.vault.azure.net
+returns a CNAME into
+privatelink.vaultcore.azure.net
+, which in public DNS points to the regional Key Vault service ingress. This behavior is intentional and is how every Azure PaaS service that supports Private Link is designed: the public CNAME exists so that clients without a private DNS override (for example, on-premises hosts that aren't yet configured for the private zone) can still resolve the name during a phased migration.
+Public DNS resolution isn't the same as access:
+A successful lookup confirms only that a vault with that exact name exists in the global Key Vault namespace. It doesn't confirm a private endpoint is attached, expose the private endpoint IP, or expose any vault configuration, network rules, or data.
+The IPs returned by public DNS belong to the shared multitenant Key Vault frontend, not to your vault. With
+Public network access
+set to
+Disabled
+and no firewall allow-list, the service rejects every request at that ingress.
+The data-plane controls protect the vault: public access disabled, private endpoint, RBAC, soft delete, purge protection,
+Microsoft Defender for Key Vault
+, and diagnostic logging. DNS suppression isn't a control.
+If predictable resource names are themselves part of your threat model, choose vault names that don't encode environment, customer, or workload identifiers, so external observers can't guess the FQDN to query.
+For the underlying DNS architecture, see
+Azure Private Endpoint DNS configuration
+.
 Troubleshooting Guide
 Check to make sure the private endpoint is in the approved state.
 You can check and fix this in Azure portal. Open the Key Vault resource, and se
```

---

### 25. Apply IRM to SharePoint

**URL:** https://learn.microsoft.com/en-us/purview/apply-irm-to-a-list-or-library
**Section:** Azure Services
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

**What Changed:**
```diff
--- +++ @@ -24,7 +24,7 @@ Summarize this article for me
 You can use Information Rights Management (IRM) to help control and protect files that are downloaded from lists or libraries. This feature is only supported in the Microsoft global cloud. IRM isn't supported for SharePoint lists and libraries in national cloud deployments.
 Administrator preparations before applying IRM
-The Azure Rights Management service (Azure RMS) from Microsoft Purview Information Protection, and the on-premises equivalent, Active Directory Rights Management Services (AD RMS), support Information Rights Management for sites. No other installations are required.
+The Azure Rights Management service from Microsoft Purview Information Protection, and the on-premises equivalent, Active Directory Rights Management Services (AD RMS), support Information Rights Management for sites. No other installations are required.
 Before you apply IRM to a list or library, you need to enable IRM for your site. You need administrator permissions for the site to enable IRM. In addition, to apply IRM to a list or library, you must have administrator permissions for that list or library.
 If you're using SharePoint, your users might experience timeouts when downloading larger IRM-protected files. To avoid timeouts, use your Office apps to apply IRM protection, and store larger files in a SharePoint library that doesn't use IRM.
 Note
@@ -87,7 +87,7 @@ Select the
 Stop restricting access to the library at
 check box, and then select the date that you want.
-Control the interval that Azure RMS credentials are cached for the program that is licensed to open the document.
+Control the interval that the Azure Rights Management service credentials are cached for the program that is licensed to open the document.
 Select the
 Users must verify their credentials using this interval (days)
 check box, then enter the interval for caching credentials in number of days.

```

---

### 26. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -577,6 +577,8 @@ eDiscovery administrators can select specific users as data custodians for a case by using the built-in custodian management tool in eDiscovery (Premium) as described inâ¯
 Add custodians to an eDiscovery (Premium) case
 .
+Microsoft Purview for agentic workloads
+Microsoft Purview security and compliance capabilities for agents on Microsoft Foundry and Entra-connected AI apps will be supported by Microsoft 365 E7 and Agent365 SKUs.
 Microsoft Purview Information Barriers
 Information Barriers are policies that an admin can configure to prevent individuals or groups from communicating with each other. This is useful if, for example, one department is handling information that shouldn't be shared with other departments, or a group needs to be prevented from communicating with outside contacts. Information barrier policies also prevent lookups and discovery. This means that if you attempt to communicate with someone you shouldn't be communicating with, you won't find that user in the people picker.
 Users benefit from the advanced compliance capabilities of information barriers when they're restricted from communicating with others. Information barriers policies can be defined to prevent a certain segment of users from communicating with each or allow specific segments to communicate only with certain other segments. For more information on defining information barrier policies, seeâ¯

```

---

### 27. Copilot Studio Licensing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Section:** Licensing
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -73,29 +73,33 @@ You can get a standalone Copilot Studio subscription from the Microsoft 365 admin center. For more information, see
 Assign licenses and manage access to Copilot Studio
 .
-Copilot Studio for Microsoft Teams plans
-Copilot Studio for Teams enables customers to build conversational interfaces within Teams. The agents can use data stored in Microsoft Dataverse for Teams or many other sources, using the supplied standard connectors.
-Capabilities available in the Copilot Studio app in Teams are available as part of select Microsoft 365 subscriptions with Microsoft Power Platform and Teams capabilities. This plan excludes plans for US government environments (GCC, GCC High, and DoD), EDU A1, and SUB SKUs.
-This table compares key capabilities in the Copilot Studio for Teams plan, which is available in select Microsoft 365 subscriptions, against the standalone Copilot Studio subscription. For a full, comparative list, see the
+Copilot Studio for Microsoft Teams plan
+The Copilot Studio for Teams plan, part of select Microsoft 365 subscriptions, lets you build agents that use classic orchestration and publish them to Teams. These agents can use data stored in Microsoft Dataverse for Teams or many other sources, by using
+Power Automate flows
+.
+A subset of the capabilities available in Copilot Studio are available as part of select Microsoft 365 subscriptions with Microsoft Power Platform and Teams capabilities. This plan excludes plans for US government environments (GCC, GCC High, and DoD), EDU A1, and SUB SKUs.
+The following table compares key capabilities in the Copilot Studio for Teams plan, available in select Microsoft 365 subscriptions, against the standalone Copilot Studio subscription. For a full, comparative list, see the
 Microsoft Power Platform Licensing Guide
 .
-Also see the
+Also see
 Quotas and limits
-article for other capacity considerations.
+for other capacity considerations.
 Capability
-Select Microsoft 365 subscriptio
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. CoE Power BI Monitor
**URL:** https://learn.microsoft.com/en-us/power-platform/guidance/coe/power-bi-monitor
**Classification:** CRITICAL (Deprecation notice)

---

### 2. Copilot Studio Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Classification:** CRITICAL (Deprecation notice)

---

### 3. Analytics
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Classification:** MEDIUM (General content update)

---

### 4. What's New
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Classification:** MEDIUM (General content update)

---

### 5. Authentication Methods
**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/overview-authentication
**Classification:** CRITICAL (Deprecation notice)

---

### 6. Governing Agent Identities
**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Classification:** MEDIUM (General content update)

---

### 7. Integrated Apps
**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center?view=o365-worldwide
**Classification:** MEDIUM (General content update)

---

### 8. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*