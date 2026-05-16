# Microsoft Learn Documentation Changes

**Run Date:** 2026-05-16
**Run Time:** 2026-05-16T08:06:15.395729+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 3 |
| HIGH Changes | 19 |
| MEDIUM Changes | 7 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | MEDIUM | 1.4 | Review and update |
| 2 | capacity-storage | HIGH | 3.5 | Review and update |
| 3 | whats-new | HIGH | 2.10 | Review and update |
| 4 | planned-features | MEDIUM | 1.4, 3.8, 2.17, 2.25 | Review optional |
| 5 | ...-governance-agentic-center-enablement | MEDIUM | None | Review optional |
| 6 | agent-essentials-overview | HIGH | 2.25 | Review and update |
| 7 | ...rosoft.com/en-us/microsoft-agent-365/ | HIGH | 1.7, 3.1, 3.13, 3.14, 3.6, 3.2, 2.6, 2.12, 2.5, 2.25 | Update portal-walkthrough |
| 8 | overview | HIGH | 3.1, 3.13, 2.6, 2.12, 2.25 | Update portal-walkthrough |
| 9 | audit-search | HIGH | None | Review and update |
| 10 | ai-microsoft-purview | HIGH | 4.8, 4.7, 1.5, 1.16, 1.6, 2.6 | Review and update |
| 11 | endpoint-dlp-learn-about | HIGH | 1.17 | Review and update |
| 12 | dlp-configure-endpoint-settings | HIGH | 1.17 | Review and update |
| 13 | encryption | HIGH | 1.16 | Review and update |
| 14 | how-to-authentication-passkeys-fido2 | HIGH | None | Review and update |
| 15 | what-is-microsoft-entra-agent-id | MEDIUM | 1.11, 1.18 | Review optional |
| 16 | agent-id-governance-overview | MEDIUM | 1.11, 3.6, 2.26 | Review optional |
| 17 | restricted-access-control | HIGH | 4.1, 1.3 | Review and update |
| 18 | restricted-content-discovery | HIGH | 4.1, 4.7, 4.6, 1.3, 1.14 | Review and update |
| 19 | advanced-management | HIGH | 4.2, 4.1, 4.5, 4.6, 1.3 | Review and update |
| 20 | data-access-governance-reports | HIGH | 4.2, 4.1, 4.5, 4.4, 4.6, 1.3, 1.14 | Update portal-walkthrough |
| 21 | site-lifecycle-management | HIGH | 4.3, 4.2 | Review and update |
| 22 | request-site-attestations | HIGH | 4.2 | Review and update |
| 23 | insights-on-sharepoint-agents | HIGH | 4.5 | Review and update |
| 24 | track-and-revoke-admin | HIGH | None | Review and update |
| 25 | apply-irm-to-a-list-or-library | HIGH | 1.16 | Review and update |
| 26 | new-dlpcompliancepolicy | MEDIUM | 1.5 | Review optional |
| 27 | whats-new | CRITICAL | None | Monitor |
| 28 | requirements-licensing-subscriptions | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Agent 365 Documentation Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -12,8 +12,8 @@ How can I extend my agent to be Microsoft Agent 365 compatible?
 Any agent can adopt Agent 365, regardless of where the agent is built or acquired. Learn how to get started as an agent developer.
 Learn more
-Get started with Microsoft Agent 365
-Learn more about Microsoft Agent 365.
+Explore Microsoft Agent 365
+Observe, secure, and govern every agent across your organization with Microsoft Agent 365.
 Observe
 Gain visibility into agents in your environment, understand how theyâre used, and act quickly on performance, behavior, and risk signals before they impact the business.
 Learn more
@@ -23,5 +23,6 @@ Secure
 Secure agent identities, control access to resources, prevent data oversharing and leaks, and defend against threats and vulnerabilities with enterprise-grade security solutions.
 Learn more
-Learn about Microsoft Agent 365
-Agent 365 extends the existing infrastructure that you use for managing people to agents. It equips your agents with the same apps and protections, tailored to agent needs, saving IT time and effort on integrating agents into business processes.+Learn more about Microsoft Agent 365
+Agent 365 extends the existing infrastructure that you use for managing people to agents. It equips your agents with the same apps and protections, tailored to agent needs, saving IT time and effort on integrating agents into business processes.
+Get started
```

---

### 2. Agent 365 Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -53,7 +53,9 @@ . At launch, a set of
 pre-integrated ecosystem partner agents
 are available to deploy directly from the Microsoft 365 admin center.
-Microsoft Agent 365 does not require specific product prerequisites to enable; however, it is recommended that customers have Entra P1, Entra P2, or Entra Suite in addition to Purview Data Loss Prevention to make full use of the benefits.
+Microsoft Agent 365 does not require specific product prerequisites to enable; however, it is recommended that customers have Entra P1, Entra P2, or Entra Suite in addition to Purview Data Loss Prevention to make full use of the benefits. At least one user must be licensed with a
+qualifying Microsoft Agent 365 license
+to enable Agent 365.
 Plans and licensing
 For plans and pricing information, see
 Microsoft Agent 365: The Control Plane for Agents

```

---

### 3. Data Access Governance Reports

**URL:** https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/4.2/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -24,28 +24,8 @@ Summarize this article for me
 As sprawl and oversharing of SharePoint sites increase with exponential data growth, organizations need help with governing their data. Data access governance reports can help you govern access to SharePoint data. The reports let you discover sites that contain potentially overshared or sensitive content. You can use these reports to assess and apply the appropriate security and compliance policies.
 What you need to create a data access governance report
-License requirements
-Your organization needs to have the right
-licenses
-and meet certain administrative permissions or roles to use the feature described in this article.
-First, your organization must have one of the following base licenses:
-Office 365 E3, E5, or A5
-Microsoft 365 E1, E3, E5, or A5
-Additionally, you need at least one of these licenses:
-Microsoft 365 Copilot license:
-At least one user in your organization must be assigned a Copilot license (this user doesn't need to be a SharePoint administrator).
-Microsoft SharePoint Advanced Management license:
-Available as a standalone purchase.
-Administrator requirements
-You must be a
-SharePoint administrator
-or have equivalent permissions.
-Additional information
-If your organization has a Copilot license and at least one person in your organization is assigned a Copilot license, SharePoint administrators automatically gain access to the
-SharePoint Advanced Management features needed for Copilot deployment
-.
-For organizations without a Copilot license, you can use SharePoint Advanced Management features
-by purchasing a standalone SharePoint Advanced Management license
+See
+Prerequisites for SharePoint Advanced Management
 .
 The reports are currently unavailable for Gallatin, even if you have the required licenses.
 How to access the Data access governance reports in the SharePoint admin center

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
--- +++ @@ -2344,6 +2344,8 @@ By: Rencore GmbH
 Repfabric
 By: Repfbaric
+Repfabric Data Loader
+By: Repfabric LLC
 Repfabric Job Loader
 By: Repfabric LLC
 Repfabric Lead Loader

```

---

### 2. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

**What Changed:**
```diff
--- +++ @@ -416,7 +416,7 @@ Note
 The storage-driven capacity model calculation of these thresholds also considers the overflow usage allowed in the storage-driven model. For example, extra database capacity can be used to cover log and file overuse and extra log capacity can be used to cover file overuse. Therefore, overflow usage is taken into consideration to reduce the number of emails a tenant admin receives.
 Tenant admins, Power Platform admins, and Dynamics 365 admins receive these notifications on a weekly basis. At this time, there's no option for a customer to opt out of these notifications or delegate these notifications to someone else. All admin types listed earlier automatically receive these notifications.
-Additionally, there's a notification banner in the Power Platform admin center when a tenant exceeds storage capacity.
+Additionally, a notification banner appears in the Power Platform admin center, Power Apps, Power Automate, Power Pages, and model-driven apps when any of the three storage capacities (database, file, or log) fall below 15 percent remaining or exceed the allocated capacity.
 The
 Universal License Terms for Online Services
 apply to your organization's use of the online service, including consumption that exceeds the online service's documented entitlements or usage limits.

```

---

### 3. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -35,6 +35,41 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+April 2026
+Configure
+hold and resume
+for voice-enabled agents to pause mid-conversation and resume where you left off, giving users a more natural calling experience.
+(Preview) Build and deploy
+real-time voice agents
+for Copilot Studio and Dynamics 365 Contact Center, with support for NLU, multilingual conversations, knowledge integration, security settings, and voice tuning settings like speech sensitivity and silence detection. Configure and
+test your real-time voice agent
+directly in Copilot Studio, then
+publish it
+to your telephony channel.
+Trigger agent evaluations automatically using the
+Copilot Studio connector
+with Power Automate, reducing manual effort in your testing workflow.
+(Preview) Run
+automated agent evaluations from a REST API
+using the Power Platform API to integrate evaluation into CI/CD and custom automation pipelines.
+Use the
+agent usage estimator
+to forecast Copilot credit consumption across Copilot Studio and Dynamics 365 agents before deploying at scale.
+(Preview) Analyze your agent with
+custom metrics
+by defining your own analytics categories and visualizing results alongside built-in analytics.
+(General availability) Connect agents to other agents using the
+agent-to-agent (A2A) protocol
+.
+(Preview) Add a
+display name suffix
+to identify agents across environments in Teams and Microsoft 365 Copilot using environment variables.
+(Preview) Use
+GPT-5.5 Reasoning (Deep)
+as an experimental model for agents requiring deep analytical reasoning.
+Share
+analytics access
+with colleagues using the new Analytics Viewer role, without granting broader maker permissions.
 March 2026
 (Preview) Use
 Work IQ

```

---

### 4. Agent Management Essentials Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-essentials-overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -106,7 +106,7 @@ Microsoft 365 Copilot works with different Microsoft services to help you protect your organization's data. When you're ready to deploy agents within your organization, you should consider Microsoft's recommended approach to address oversharing concerns. This approach provides the pilot, deploy, and operate phases to consider when deploying Copilot and agents. Each phase consists of activities, outcomes, and expected effort needed. For more information, see
 Secure & governed data foundation for Microsoft 365 Copilot: A deployment blueprint
 .
-In addition, Microsoft provides SharePoint Advance Management and Microsoft Purview to address oversharing. SharePoint Advance Management provides SharePoint site management and content governance capabilities. Microsoft Purview provides security, compliance, and governance across data and files.
+In addition, Microsoft provides SharePoint Advanced Management and Microsoft Purview to address oversharing. SharePoint Advanced Management provides SharePoint site management and content governance capabilities. Microsoft Purview provides security, compliance, and governance across data and files.
 Note
 Microsoft 365 Copilot uses the access rights of the end user to determine the data that can be presented to the end user.
 To better understand aspects of data protection related to Microsoft 365 Copilot, such as sensitivity labels, encryption, oversharing, and data auditing, see the following resources:

```

---

### 5. Search the Audit Log

**URL:** https://learn.microsoft.com/en-us/purview/audit-search
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.23/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -249,7 +249,7 @@ : Additional details about the activity.
 You can sort the search job items by using the column headers or create a custom filter by using the filter pane. Use the filter to filter the search job items for specific values for any of the dashboard column criteria. To export all search job items to a .csv file, select
 Export
-on the command bar. Export supports results up to 50 KB for Audit (Standard) and up to 500 KB (500,000 rows) for Audit (Premium).
+on the command bar. Export supports results up to 50,000 rows for Audit (Standard) and up to 1,000,000 rows for Audit (Premium).
 Select a specific activity to see more details about the activity in a fly-out window. The fly-out window displays the additional information about the activity.
 Scoping access to audit logs using administrative units
 Access to search the audit log is based on the

```

---

### 6. DSPM for AI

**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Section:** Microsoft Purview
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -146,9 +146,9 @@ . Events include how and when users interact with the AI app, and can include in which Microsoft 365 service the activity took place, and references to the files stored in Microsoft 365 that were accessed during the interaction. If these files have a sensitivity label applied, that's also captured.
 These events flow into
 activity explorer
-in DSPM for AI and the
+in the
 AI activities
-tab in activity explorer from the preview version of DSPM, where the data from prompts and responses can be displayed. You can also use the
+tab in the current version of DSPM and in DSPM for AI, where the data from prompts and responses can be displayed. You can also use the
 Audit
 solution from the
 Microsoft Purview portal

```

---

### 7. Endpoint DLP

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -565,7 +565,10 @@ Just-in-time protection blocks egress activities on these monitored files until policy evaluation completes successfully:
 Items that have never been evaluated.
 Items on which the evaluation has gone stale. These are previously evaluated items that haven't been reevaluated by the current, updated cloud versions of the policies.
-For more information on how just-in-time protection works, see
+Unsaved files (preview) â brand-new files that have never been saved, or existing files with unsaved modifications, including the window before autosave completes. For more information, see
+Unsaved file protection
+.
+For more information on how just-in-time protection works,see
 Learn about just-in-time protection
 , and
 Get started with Microsoft Purview Data Loss Prevention just-in-time protection

```

---

### 8. Configure Settings

**URL:** https://learn.microsoft.com/en-us/purview/dlp-configure-endpoint-settings
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -47,7 +47,7 @@ Microsoft Purview Information Protection Support in Acrobat
 .
 Advanced classification scanning and protection
-When you turn on advanced classification scanning and protection, the Microsoft Purview cloud-based data classification service can scan items, classify them, and return the results to the local machine. Therefore, you can take advantage of classification techniques such as
+When you turn on advanced classification scanning and protection, the Microsoft Purview cloud-based data classification service scans items, classifies them, and returns the results to the local machine. Therefore, you can take advantage of classification techniques such as
 exact data match
 classification,
 trainable classifiers
@@ -60,7 +60,7 @@ The
 Paste to browser
 action doesn't support advanced classification.
-When you turn on advanced classification, the local device sends content to the cloud services for scanning and classification. If bandwidth usage is a concern, you can set a limit on how much bandwidth can be used in a rolling 24-hour period. You configure the limit in
+When you turn on advanced classification, the local device sends content to the cloud services for scanning and classification. If you're concerned about bandwidth usage, set a limit on how much bandwidth can be used in a rolling 24-hour period. You configure the limit in
 Endpoint DLP settings
 and it applies per device. If you set a bandwidth usage limit and that usage limit is exceeded, DLP stops sending the user content to the cloud. At that point, data classification continues locally on the device but classification by using exact data match, named entities, trainable classifiers, and credential classifiers isn't available. When the cumulative bandwidth usage drops below the rolling 24-hour limit, communication with the cloud services resumes.
 If bandwidth usage isn't a concern, select
@@ -112,19 +112,19 @@ Use the following logic to construct your exclusion paths for Wi
```

---

### 9. Encryption

**URL:** https://learn.microsoft.com/en-us/purview/encryption
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

**What Changed:**
```diff
--- +++ @@ -22,6 +22,7 @@ Encryption
 Feedback
 Summarize this article for me
+Microsoft Purview service description
 Encryption is an important part of your file protection and information protection strategy. This article provides an overview of encryption for Microsoft 365. Get help with encryption tasks like how to set up encryption for your organization and how to password-protect Microsoft 365 documents.
 For information about certificates and technologies like TLS, see
 Technical reference details about encryption in Microsoft 365

```

---

### 10. FIDO2 Security Keys

**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-authentication-passkeys-fido2
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -125,11 +125,9 @@ Devices must support passkey (FIDO2) authentication. For Windows devices that are joined to Microsoft Entra ID, the best experience is on Windows 10 version 1903 or higher. Hybrid-joined devices must run Windows 10 version 2004 or higher.
 If a passkey profile for both device-bound and synced passkeys targets Microsoft Authenticator, users need to run Microsoft Authenticator iOS version 6.8.37 or Android version 6.2507.4749.
 Policy size limit:
-The Authentication methods policy supports a size limit of 20 KB. You can't save more passkey profiles after the size limit is reached. To check the size, use the
-Get authenticationMethodsPolicy Microsoft Graph API
-to retrieve the JSON for the Authentication methods policy. Save the output as a .txt file, then right-click and select
-Properties
-to view the file size.
+The
+Passkey (FIDO2)
+policy supports a size limit of 20 KB. You can't save more passkey profiles after the size limit is reached.
 Reference sizes:
 Base passkey policy without changes: 1.44 KB
 Target with 1 applied passkey profile: 0.23 KB
@@ -401,6 +399,25 @@ Security info
 , delete the old passkey (FIDO2), and add a new one.
 Related content
+After you enable passkey profiles, share end-user registration and sign-in guidance for each passkey type:
+Synced passkeys
+â
+Register a passkey (FIDO2)
+|
+Sign in with a passkey (FIDO2)
+Passkeys in Microsoft Authenticator
+â
+Enable passkeys in Authenticator
+|
+Register a passkey in Authenticator
+|
+Sign in with passkeys in Authenticator
+Microsoft Entra passkeys on Windows (preview)
+â
+Enable passkeys on Windows
+FIDO2 security keys
+â
+Register a passkey with a security key
 Passkeys (FIDO2) authentication method in Microsoft Entra ID
 Support for FIDO2 authentication with Microsoft Entra ID
 How to enable passkeys in Microsoft Authenticator

```

---

### 11. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**What Changed:**
```diff
--- +++ @@ -28,28 +28,8 @@ Data access governance reports
 .
 What do you need to restrict site access?
-License requirements
-Your organization needs to have the right
-licenses
-and meet certain administrative permissions or roles to use the feature described in this article.
-First, your organization must have one of the following base licenses:
-Office 365 E3, E5, or A5
-Microsoft 365 E1, E3, E5, or A5
-Additionally, you need at least one of these licenses:
-Microsoft 365 Copilot license:
-At least one user in your organization must be assigned a Copilot license (this user doesn't need to be a SharePoint administrator).
-Microsoft SharePoint Advanced Management license:
-Available as a standalone purchase.
-Administrator requirements
-You must be a
-SharePoint administrator
-or have equivalent permissions.
-Additional information
-If your organization has a Copilot license and at least one person in your organization is assigned a Copilot license, SharePoint administrators automatically gain access to the
-SharePoint Advanced Management features needed for Copilot deployment
-.
-For organizations without a Copilot license, you can use SharePoint Advanced Management features
-by purchasing a standalone SharePoint Advanced Management license
+See
+Prerequisites for SharePoint Advanced Management
 .
 Enable site-level access restriction for your organization
 You must enable site-level access restriction for your organization before you can configure it for individual sites. You can also delegate site access restriction control to all the site admins of your organization.

```

---

### 12. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -40,30 +40,10 @@ Active sites
 tab to first compile a selective list of targeted sites.
 What you need to restrict a specific SharePoint access?
-License requirements
-Your organization needs to have the right
-licenses
-and meet certain administrative permissions or roles to use the feature described in this article.
-First, your organization must have one of the following base licenses:
-Office 365 E3, E5, or A5
-Microsoft 365 E1, E3, E5, or A5
-Additionally, you need at least one of these licenses:
-Microsoft 365 Copilot license:
-At least one user in your organization must be assigned a Copilot license (this user doesn't need to be a SharePoint administrator).
-Microsoft SharePoint Advanced Management license:
-Available as a standalone purchase.
-Administrator requirements
-You must be a
-SharePoint administrator
-or have equivalent permissions.
-Additional information
-If your organization has a Copilot license and at least one person in your organization is assigned a Copilot license, SharePoint administrators automatically gain access to the
-SharePoint Advanced Management features needed for Copilot deployment
+See
+SharePoint Advanced Management prerequisites
 .
-For organizations without a Copilot license, you can use SharePoint Advanced Management features
-by purchasing a standalone SharePoint Advanced Management license
-.
-In addition to preceding information, you also need the latest version of
+Also download the latest version of
 Microsoft SharePoint Online Management Shell
 .
 Configure Restricted Content Discovery

```

---

### 13. Advanced Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -88,7 +88,7 @@ Initiate site access reviews
 : Initiate site access reviews to delegate the process of reviewing DAG reports to site owners of overshared sites.
 Manage permissions and access
-SAM provides layered controls to detect oversharing, delegate remediation, and enforce leastâprivilege access across SharePoint and OneDrive.
+SAM provides layered controls to manage permissions and access, and enforce leastâprivilege access across SharePoint and OneDrive.
 Use Conditional Access policies
 : Use authentication contexts to connect a Microsoft Entra Conditional Access policy to a SharePoint site.
 Use site policy comparison reports
@@ -104,28 +104,8 @@ Restrict OneDrive and SharePoint site creation
 : Using PowerShell, you can designate who can create OneDrive or SharePoint sites by using security groups in Microsoft Entra ID.
 SAM prerequisites
-License requirements
-Your organization needs to have the right
-licenses
-and meet certain administrative permissions or roles to use the feature described in this article.
-First, your organization must have one of the following base licenses:
-Office 365 E3, E5, or A5
-Microsoft 365 E1, E3, E5, or A5
-Additionally, you need at least one of these licenses:
-Microsoft 365 Copilot license:
-At least one user in your organization must be assigned a Copilot license (this user doesn't need to be a SharePoint administrator).
-Microsoft SharePoint Advanced Management license:
-Available as a standalone purchase.
-Administrator requirements
-You must be a
-SharePoint administrator
-or have equivalent permissions.
-Additional information
-If your organization has a Copilot license and at least one person in your organization is assigned a Copilot license, SharePoint administrators automatically gain access to the
-SharePoint Advanced Management features needed for Copilot deployment
-.
-For organizations without a Copilot license, you can use SharePoint Advanced Management features
-by purchasing a standalone Sh
```

---

### 14. Site Lifecycle Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/site-lifecycle-management
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -26,31 +26,10 @@ Microsoft SharePoint Advanced Management
 help you improve site governance by automating the process of detecting inactive sites and notifying site owners by email. Site owners can then review and confirm whether their sites are still active.
 You can configure an inactive sites policy in the SharePoint admin center. This article describes how to set up an inactive site policy with notifications and enforcement actions.
-What do you need to create an inactive site policy?
-License requirements
-Your organization needs to have the right
-licenses
-and meet certain administrative permissions or roles to use the feature described in this article.
-First, your organization must have one of the following base licenses:
-Office 365 E3, E5, or A5
-Microsoft 365 E1, E3, E5, or A5
-Additionally, you need at least one of these licenses:
-Microsoft 365 Copilot license:
-At least one user in your organization must be assigned a Copilot license (this user doesn't need to be a SharePoint administrator).
-Microsoft SharePoint Advanced Management license:
-Available as a standalone purchase.
-Administrator requirements
-You must be a
-SharePoint administrator
-or have equivalent permissions.
-Additional information
-If your organization has a Copilot license and at least one person in your organization is assigned a Copilot license, SharePoint administrators automatically gain access to the
-SharePoint Advanced Management features needed for Copilot deployment
-.
-For organizations without a Copilot license, you can use SharePoint Advanced Management features
-by purchasing a standalone SharePoint Advanced Management license
-.
-How do inactive site policies work?
+Prerequisites for an inactive site policy
+See
+SharePoint Advanced Management prerequisites
+.
 Scope of inactive site policies
 You can configure parameters for an inactive site policy, such as inactive time period, template type, site creation source, sensitivity labels, and exclusion of up
```

---

### 15. Site Attestation

**URL:** https://learn.microsoft.com/en-us/sharepoint/request-site-attestations
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**What Changed:**
```diff
--- +++ @@ -27,28 +27,8 @@ help your organization improve site governance. Site attestation involves regular reviews by site owners or site administrators to check and confirm the accuracy of site information, including the site's necessity, its owners, members, permissions, and sharing settings. For sites that remain unattested, you can choose to automate enforcement actions to prevent risks of content overexposure. This approach ensures ongoing site compliance and actively reduces risks such as information oversharing.
 Site attestation policies help you manage periodic attestation of sites at scale. You can configure a site attestation policy in the SharePoint admin center. This article describes how to create and configure a site attestation policy in either active or simulation mode.
 Requirements for a site attestation policy
-License requirements
-Your organization needs to have the right
-licenses
-and meet certain administrative permissions or roles to use the feature described in this article.
-First, your organization must have one of the following base licenses:
-Office 365 E3, E5, or A5
-Microsoft 365 E1, E3, E5, or A5
-Additionally, you need at least one of these licenses:
-Microsoft 365 Copilot license:
-At least one user in your organization must be assigned a Copilot license (this user doesn't need to be a SharePoint administrator).
-Microsoft SharePoint Advanced Management license:
-Available as a standalone purchase.
-Administrator requirements
-You must be a
-SharePoint administrator
-or have equivalent permissions.
-Additional information
-If your organization has a Copilot license and at least one person in your organization is assigned a Copilot license, SharePoint administrators automatically gain access to the
-SharePoint Advanced Management features needed for Copilot deployment
-.
-For organizations without a Copilot license, you can use SharePoint Advanced Management features
-by purchasing a standalone SharePoint Advanced Management lice
```

---

### 16. Agent Insights

**URL:** https://learn.microsoft.com/en-us/sharepoint/insights-on-sharepoint-agents
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -22,29 +22,15 @@ Insights report on agents in SharePoint
 Feedback
 Summarize this article for me
-Insights report on agents in SharePoint provides SharePoint Administrators with rich information on the recently created agents across all SharePoint sites and OneDrive sites within their organization. This report provides admins with the ability to learn about the sites with the highest number of agents created. Using this report, SharePoint admins can further govern and maintain the integrity of the content used by agents as grounding data.
-The insights report is based on the Microsoft audit data logged for the agents, created in SharePoint, through the FileCreated and FileRenamed events.
-You can generate and manage agent insights report in SharePoint Admin Center or with SharePoint Online Management Shell.
-What do you need to access agent insights report
-License requirements
-Your organization needs to have the right
-licenses
-and meet certain administrative permissions or roles to use the feature described in this article.
-First, your organization must have one of the following licenses:
-Office 365 E3, E5, or A5
-Microsoft 365 E1, E3, E5, or A5
-Additionally, you need to have a Microsoft 365 Copilot license.
-Note
-At least one user in your organization must be assigned a Copilot license (this user doesn't need to be a SharePoint administrator).
-If your organization has a Copilot license and at least one person in your organization is assigned a Copilot license, SharePoint administrators automatically gain access to the
-SharePoint Advanced Management features needed for Copilot deployment
+The insights report on agents in SharePoint provides SharePoint administrators with rich information on the recently created agents across all SharePoint sites and OneDrive sites within their organization. This report helps admins learn about the sites with the highest number of agents created. By using this report, SharePoint admins can further govern and mai
```

---

### 17. Track and Revoke Documents

**URL:** https://learn.microsoft.com/en-us/purview/track-and-revoke-admin
**Section:** Azure Services
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -22,6 +22,7 @@ Track and revoke document access
 Feedback
 Summarize this article for me
+Microsoft Purview service description
 Document tracking provides information for administrators about when a protected document was accessed. If necessary, both admins and users can revoke document access for tracked documents.
 A document must be registered for tracking before an admin can track access details, including successful access events and denied attempts, and revoke access if needed. See the next section for minimum versions of Office apps that support file registration the next time they're opened.
 Note

```

---

### 18. Apply IRM to SharePoint

**URL:** https://learn.microsoft.com/en-us/purview/apply-irm-to-a-list-or-library
**Section:** Azure Services
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

**What Changed:**
```diff
--- +++ @@ -22,6 +22,7 @@ Apply Information Rights Management (IRM) to a list or library
 Feedback
 Summarize this article for me
+Microsoft Purview service description
 You can use Information Rights Management (IRM) to help control and protect files that are downloaded from lists or libraries. This feature is only supported in the Microsoft global cloud. IRM isn't supported for SharePoint lists and libraries in national cloud deployments.
 Administrator preparations before applying IRM
 The Azure Rights Management service from Microsoft Purview Information Protection, and the on-premises equivalent, Active Directory Rights Management Services (AD RMS), support Information Rights Management for sites. No other installations are required.

```

---

### 19. Copilot Studio Licensing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Section:** Licensing
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -96,6 +96,9 @@ Power Platform connectors
 Not available
 Premium connector tools in Copilot Studio
+Power Platform environment types supported
+Dataverse for Teams
+Any
 Flows (automated, instant, scheduled)
 Use
 Power Automate cloud flows

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Connector Reference
**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Classification:** MEDIUM (General content update)

---

### 2. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)

---

### 3. Agentic Center of Enablement [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement
**Classification:** MEDIUM (General content update)

---

### 4. Agent Identities for AI Agents
**URL:** https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id
**Classification:** MEDIUM (General content update)

---

### 5. Governing Agent Identities
**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Classification:** MEDIUM (General content update)

---

### 6. DLP Cmdlets
**URL:** https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpcompliancepolicy?view=exchange-ps
**Classification:** MEDIUM (General content update)

---

### 7. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*