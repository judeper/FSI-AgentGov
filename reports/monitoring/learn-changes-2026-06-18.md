# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-18
**Run Time:** 2026-06-18T10:22:28.733754+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 4 |
| HIGH Changes | 12 |
| MEDIUM Changes | 10 |
| Redirects | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | CRITICAL | 2.4 | Update portal-walkthrough |
| 2 | ...ilot-security-enhanced-admin-controls | HIGH | 2.8, 2.3, 1.18 | Review and update |
| 3 | analytics-overview | MEDIUM | 3.2, 3.10, 2.5, 2.9, 2.6 | Update portal-walkthrough |
| 4 | analytics-improve-agent-effectiveness | MEDIUM | None | Update portal-walkthrough |
| 5 | planned-features | MEDIUM | 3.8, 2.25, 2.17, 1.4 | Review optional |
| 6 | whats-new | MEDIUM | None | Review optional |
| 7 | microsoft-365-copilot-usage | HIGH | 3.8 | Review and update |
| 8 | agent-prerequisites | HIGH | 2.25 | Review and update |
| 9 | agent-365-overview | HIGH | 3.8, 2.25 | Review and update |
| 10 | dlp-policy-reference | HIGH | None | Review and update |
| 11 | ai-microsoft-purview | MEDIUM | 2.6, 4.8, 4.7, 1.6, 1.16, 1.5 | Review and update |
| 12 | ...management-settings-policy-indicators | HIGH | 1.12 | Update portal-walkthrough |
| 13 | ...ensitive-information-type-learn-about | HIGH | 1.13 | Review and update |
| 14 | create-retention-policies | HIGH | 4.3, 1.9 | Review and update |
| 15 | endpoint-dlp-getting-started | HIGH | 1.17 | Review and update |
| 16 | data-classification-activity-explorer | HIGH | 1.6, 1.14 | Review and update |
| 17 | permissions-reference | CRITICAL | 2.23 | Monitor |
| 18 | ...n.microsoft.com/en-us/entra/agent-id/ | MEDIUM | 3.11, 3.6, 2.26, 2.6, 1.11, 1.18 | Review and update |
| 19 | agent-id-governance-overview | MEDIUM | 3.6, 2.26, 1.11 | Review optional |
| 20 | create-retention-policies | HIGH | None | Review and update |
| 21 | whats-new | CRITICAL | None | Monitor |
| 22 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -146,15 +146,10 @@ The selected environment must be a
 Managed Environment
 . This environment is a premium license tier.
-Capacity charges are based on the storage consumption of the environment's paired secondary region for database, file, and log storage types.
-Capacity consumption is reflected in the familiar licensing experience within the Power Platform admin center. Learn more in
-View usage and billing information
-.
+Prepaid storage consumed for the secondary region is the cost incurred.
 For example, suppose you have 10 GB of capacity consumption in the primary location. When you turn on self-service disaster recovery, you create a copy of the data in the remote secondary region and this copy consumes another 10 GB. You can pay for this 10 GB in the secondary region through storage entitlements. If you exceed your available free storage or available entitlements, a pay-as-you-go plan actively starts billing.
 How does billing work for self-service disaster recovery?
-If you configure your environment to draw capacity from your tenant's Dataverse capacity entitlement, the system consumes the entitled capacity first. You still need a pay-as-you-go billing plan to avoid capacity overages.
-The pay-as-you-go plan generates multiple warnings at various thresholds to ensure that you're well-informed and can take appropriate action to avoid pay-as-you-go charges.
-Admins can allocate capacity to the environment, after which the pay-as-you-go plan is billed.
+A pay-as-you-go billing plan has been removed as a mandatory requirement. The system checks for available free capacity in your tenant. All pooled Dataverse entitlements at the tenant-level can be counted towards secondary storage enablement. Various overage initiatives are being evaluated. Overage management is out side of self-service disaster recovery management scope.
 Can I switch regions during a regional outage?
 If there's a regional outage, the system supports failover only to the designa
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
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -31,7 +31,7 @@ and for
 autonomous agents
 .
-Analytics are available in all geographies. Analytics data is available for up to 180 days. Session details and transcript information are available for the last 28 days. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
+Analytics are available in all geographies. Analytics data is available for up to 360 days. Session details and transcript information are available for the last 28 days. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
 Note
 The
 Analytics

```

---

### 3. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -56,7 +56,7 @@ The
 Use
 section helps you improve operational performance by showing how well your agent answers questions, how reliably tools and knowledge sources support those answers, and where targeted updates can increase coverage and consistency.
-You can view analytics for events that occurred in the last 90 days.
+You can view analytics for events that occurred in the last 360 days.
 Custom metrics
 The
 Custom metrics

```

---

### 4. Insider Risk Indicators

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -177,6 +177,10 @@ in your organization.
 Other AI applications
 : AI applications that users in your organization discover from their browser activity.
+Important
+To use this indicator, enable
+pay-as-you-go billing
+in your organization.
 Azure AI Content Safety indicators
 : Support for
 Communication Compliance indicators

```

---

## HIGH: Control Review Recommended

### 1. Enhanced Admin Controls [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**What Changed:**
```diff
--- +++ @@ -32,14 +32,14 @@ Public preview
 General availability
 Admins, makers, marketers, or analysts, automatically
-May 2026
+May 31, 2026
 Jun 2026
 Business value
-By using the new governance controls, you can guide Copilot development in your tenants, enforce governance policies that match your organizational requirements, and unlock Copilot innovation opportunities.
+By using new governance controls, you can guide Copilot and agent development in your tenants, enforce governance policies that match your organizational requirements, and unlock new innovation opportunities.
 Feature details
-This feature introduces advanced governance controls that allow administrators to configure security and compliance settings at the environment or environment group level within the Power Platform admin center.
-Technically, these controls work by configuring new settings for agent sharing, turning off anonymous access endpoints, and enforcing the use of approved authentication providers through integrated identity management. The system applies these configurations through environment-level policies that are validated during agent deployment and runtime, ensuring consistent enforcement across all environments.
-From a business perspective, these controls significantly reduce the risk of data exfiltration and unauthorized access, aligning with organizational security and compliance standards. By centralizing governance, organizations can maintain regulatory compliance and prevent costly data breaches. These controls also ensure that agent development adheres to internal and external audit requirements, which ultimately protects brand reputation and reduces operational risk.
+This feature introduces advanced governance controls that enable administrators to centrally define authentication and access policies for agents at the environment or environment group level within the Power Platform admin center. These controls are designed to standardize how agents handle identity 
```

---

### 2. Copilot Usage Reports

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -26,7 +26,7 @@ For general information about usage reports in the Microsoft 365 admin center, and to see a list of all available reports, see
 Microsoft 365 admin center usage reports overview
 .
-View the Microsoft 365 Copilot usage report
+View the Microsoft 365 Copilot usage report in the Microsoft 365 admin center
 For information about the roles needed to view usage reports, see "Before you begin" in
 Microsoft 365 admin center usage reports overview
 Go to the
@@ -253,7 +253,7 @@ Adoption
 section, you might see a recommendation card:
 To learn more about using organizational messages for Microsoft 365 Copilot, see
-Microsoft 365 features adoption using organizational messages
+Drive adoption with Microsoft 365 Copilot Usage report's Organizational Messages feature
 .
 You can export the report data into an Excel .csv file by selecting the ellipses and then
 Export

```

---

### 3. Agent Prerequisites

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-prerequisites
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -26,15 +26,19 @@ Note
 Before your organization assigns or deploys an agent, first consider your organization's objectives, technical requirements, costs, Responsible AI (RAI) considerations, and compliance factors. For more information, see Microsoft 365 Copilot extensibility planning guide.
 Licensing requirements
-Microsoft 365 Copilot Chat is available at no additional cost for all Microsoft Entra account users with a Microsoft 365 or Office 365 subscription. Members of your organization can use agents that are available at no additional cost from the Agent Store. You, as the administrator of your organization, would also need to enable these agents. If your organization requires agents that incorporate your organization's data, you can provide access to
+Microsoft 365 Copilot Chat
+is available at no additional cost for all Microsoft Entra account users with a Microsoft 365 or Office 365 subscription. Members of your organization can use agents that are available at no additional cost from the Agent Store. You, as the administrator of your organization, would also need to enable these agents. If your organization requires agents that incorporate your organization's data, you can provide access to
 agents
 that are billed based on metered consumption.
-Microsoft 365 Copilot, which includes Microsoft 365 Copilot Chat, requires a Microsoft 365
+Microsoft 365 Copilot
+, which includes Microsoft 365 Copilot Chat, requires a Microsoft 365
 Business
 or
 Enterprise
 plan. It includes AI-powered chat grounded in both web-based and work-based data, as well as the capabilities of Microsoft 365 Copilot Chat. In addition, Microsoft 365 Copilot unlocks embedded Copilot features in Word, Excel, Outlook, and Teams. Additionally, your organization can use
 custom agents
+and
+Licensing for agent management
 .
 Each Copilot option offers different capabilities. For a list of these capabilities, see
 Agent capabilities for Microsoft 365 users

```

---

### 4. Agent 365 Overview Page (M365 Admin)

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.25/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -53,15 +53,33 @@ The Microsoft Frontier program gives organizations early access to innovative and emerging AI capabilities in Microsoft 365 before those features reach general availability (GA). Frontier previews are subject to the existing preview terms of your customer agreements. For more information, see
 Get started with the Microsoft Frontier program
 .
-Prerequisites
+Prerequisites for agent management
 Before you can manage agents in the Microsoft 365 admin center, confirm the following requirements are met:
-Your organization has the required Microsoft 365 subscription and licenses for either Microsoft 365 Copilot or Microsoft Agent 365 capabilities.
-Users who create, publish, or use agents have the appropriate licenses assigned.
-Youâre assigned an administrator role that includes permissions to manage settings for either Microsoft 365 Copilot or Microsoft Agent 365 in the Microsoft 365 admin center.
+Your organization has the required subscription and licenses for either Microsoft 365, Microsoft 365 Copilot, or Microsoft Agent 365.
+Users at your organization that create, publish, or use agents have the appropriate licenses assigned.
+Youâre assigned an administrator role that includes permissions to manage settings for Microsoft 365, Microsoft 365 Copilot, or Microsoft Agent 365 in the Microsoft 365 admin center.
 For more information, see the following resources:
+Licensing for agent management
+Agent management roles and permissions
+Licensing for agent management
+The following licensing options include agents that can be managed in Microsoft 365 admin center:
+Microsoft 365 plans
+Microsoft 365 (All Suites) includes Copilot Chat. Copilot Chat provides web data agents.
+Microsoft 365 (E7) includes Microsoft 365 E5, Microsoft 365 Copilot, Microsoft Agent 365, and Microsoft Entra Suite.
+Microsoft 365 Copilot
+This license can be added to your Microsoft 365 license (E3, E5). It's included with your Microsoft 365 license (E7). This optio
```

---

### 5. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -958,6 +958,18 @@ - Only available in the
 Custom
 policy template
+Note
+In the
+Devices
+location, the
+Devices and device groups
+setting supports only
+Audit or restrict activities on devices
+. You can't use it with
+Audit or restrict activities when users access sensitive sites in the Microsoft Edge browser on Windows devices
+under
+Rule Actions
+.
 Exchange location scoping
 If you choose to include specific distribution groups in Exchange, the DLP policy is scoped to the emails sent by members of that group or sent to members of that group. Similarly, excluding a distribution group excludes all the emails sent by the members of that distribution group or from policy evaluation.
 Group Type
@@ -1921,6 +1933,8 @@ Conditions Microsoft 365 Copilot supports
 This feature is in preview.
 Content contains (sensitivity labels)
+Content contains (sensitive information types)
+Email is received from (External users) (preview)
 Condition groups
 Sometimes you need a rule to identify only one thing, such as all content that contains a U.S. Social Security Number, which is defined by a single SIT. However, in many scenarios where the types of items you're trying to identify are more complex and therefore harder to define, more flexibility in defining conditions is required.
 For example, to identify content subject to the U.S. Health Insurance Act (HIPAA), you need to look for:
@@ -2761,7 +2775,7 @@ Content is shared from Microsoft 365
 - with people outside my organization
 Not configured
-User notification emails, policy tips, DLP alerts, and incident reports are sent only when a file is shared with a guest and a guest access the file.
+User notification emails, policy tips, DLP alerts, and incident reports are sent when a file is shared with a guest or when a guest accesses the file.
 Content is shared from Microsoft 365
 - only with people inside my organization
 Not configured
@@ -2800,7 +2814,7 @@ Block everyone
 - When the first user outside the organi
```

---

### 6. DSPM for AI

**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -55,12 +55,13 @@ Microsoft 365 Copilot & Microsoft 365 Copilot Chat
 Entra-registered AI apps
 Other AI apps
+Microsoft 365 Copilot Cowork
+Microsoft Foundry
 Microsoft Security Copilot
-Microsoft Foundry
+ChatGPT Enterprise
 Copilot in Fabric
-ChatGPT Enterprise
+Anthropic Claude (Enterprise)
 Microsoft Copilot Studio
-Anthropic Claude (Enterprise)
 Microsoft Facilitator
 Channel Agent in Teams
 For a list of supported Microsoft Purview security and compliance supported capabilities for Microsoft Agent 365, see

```

---

### 7. Sensitive Information Types

**URL:** https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -67,6 +67,10 @@ . Use them as broad criteria in your DLP policies for detecting sensitive items. See,
 Examples of named entity SITs
 .
+Tip
+You must enable
+Advanced classification scanning and protection
+if you want to use a bundled SIT in an endpoint DLP policy. This requirement is specific to the combination of bundled SITS andendpoint DLP policies.
 Custom sensitive information types
 If the preconfigured sensitive information types don't meet your needs, you can create your own custom sensitive information types that you fully define or you can copy one of the built-in ones and modify it. For more information, see
 Create a custom sensitive information type in the Microsoft Purview portal

```

---

### 8. Retention Policies

**URL:** https://learn.microsoft.com/en-us/purview/create-retention-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.9/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -100,7 +100,7 @@ . When you configure retention settings for the
 Teams channel message
 location, if a team has any shared channels, they inherit retention settings from their parent team.
-From late April 20206, retention policies also support newly created Teams call logs when you create the retention policies with PowerShell. For more information, see
+From late April 2026, retention policies also support newly created Teams call logs when you create the retention policies with PowerShell. For more information, see
 Retention policy for Teams call logs
 .
 Sign in to the Microsoft Purview portal
@@ -205,9 +205,7 @@ Retention policy for Teams call logs
 Teams call logs represent the collection of call-related data generated by Teams, including call data records (CDRs) and other call metadata. CDRs are also sometimes referred to as call detail records, or just call records.
 Prior to supporting the retention of Teams call logs in late April 2026, CDRs for Teams chat and Teams channels were included in retention policies for the Teams chat location. Going forward, new CDRs are supported only when you create a retention policy for Teams call logs. CDRs included in previous Teams chat retention policies continue to be managed by those same policies.
-This separate retention policy for call logs can be created only by using PowerShell, and has the following considerations:
-The policy is tenant-wide and can't be scoped to individual users.
-The policy doesn't support adaptive scopes or administrative units.
+This separate retention policy for call logs can be created and modified only by using PowerShell. It has the following considerations:
 The policy includes call logs for both Teams chat and Teams channels.
 The policy applies only to new call logs that are created after the policy is configured and active.
 After you create the retention policy for Teams call logs, it's displayed in
@@ -215,14 +213,13 @@ >
 Policies
 in the Microsoft Purview portal, wh
```

---

### 9. Onboard Devices

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-getting-started
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -40,6 +40,10 @@ For information on licensing, see
 Microsoft 365 Enterprise Plans
 Microsoft 365 Service Descriptions
+Important
+Endpoint DLP policy targeting can be configured using a combination of users and devices. If a policy is scoped to devices where the signed-in users do not meet the
+required criteria
+, ensure those users or devices or both are explicitly excluded from the policy. Failure to do so may lead to unintended policy enforcement behavior.
 Configure proxy on the Windows 10 or Windows 11 device
 If you're onboarding Windows 10 or Windows 11 devices, check to make sure that the device can communicate with the cloud DLP service. For more information, see,
 Configure device proxy and internet connection settings for Information Protection

```

---

### 10. Activity Explorer

**URL:** https://learn.microsoft.com/en-us/purview/data-classification-activity-explorer
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**What Changed:**
```diff
--- +++ @@ -118,6 +118,40 @@ Labeling events available in Activity explorer
 .
 Additionally, Activity Explorer gathers DLP policy match events from Microsoft 365 workloads such as Exchange, SharePoint, OneDrive, Teams chat and channels, and on-premises SharePoint folders, libraries, and file shares. When you enable Endpoint data loss prevention (DLP), Activity Explorer also includes device-level activities from onboarded Windows 10, Windows 11, and the three most recent major macOS versions.
+Enhanced matched conditions for Exchange DLP events (preview)
+For Exchange Online DLP events, Activity Explorer surfaces enhanced matched condition details for non-sensitive information type (SIT) conditions in addition to SIT matches. Every non-SIT condition that contributed to a DLP policy match is displayed with three levels of detail:
+Condition name
+: The specific policy condition that was matched, for example,
+Sender domain is
+or
+Attachment's file extension is
+.
+Matched value
+: The actual value that triggered the condition match, for example,
+contoso.com
+or
+.docx
+.
+Source
+: The part of the message where the match was found, for example, the message header, envelope, or attachment.
+Enhanced matched condition details appear on the event detail flyout for Exchange DLP events in Activity Explorer and the
+DLP Alerts dashboard
+. The following condition categories are supported:
+Sender conditions
+: Sender is, Sender domain is, Sender address contains words, Sender address matches patterns, Sender is a member of, Sender IP address is, Sender AD attribute
+Recipient conditions
+: Recipient is, Recipient domain is, Recipient address contains words, Recipient address matches patterns, Recipient is a member of, Recipient AD attribute
+Attachment conditions
+: Attachment's file extension is, Document name contains words, Document name matches patterns, Document property is, Document size equals or is greater than, Document is password protected, Document could not 
```

---

### 11. Agent ID Overview

**URL:** https://learn.microsoft.com/en-us/entra/agent-id/
**Section:** Microsoft Entra Agent ID
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.11/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -18,7 +18,7 @@ Define reusable templates for agent identities with preconfigured permissions, policies, and settings.
 AI-guided setup
 Use an AI coding agent to automate the full Agent ID onboarding workflow, from blueprint creation to agent provisioning.
-Microsoft Entra SDK for agents
+Microsoft Entra ID Auth SDK (sidecar)
 Integrate agent authentication and authorization with familiar SDKs and developer tools.
 OAuth protocols for agents
 Understand how agents authenticate and obtain tokens using OAuth 2.0 flows optimized for AI workloads.

```

---

### 12. Retention for SharePoint

**URL:** https://learn.microsoft.com/en-us/purview/create-retention-policies#retaining-content-thats-in-sharepoint-sites
**Section:** SharePoint Administration
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -100,7 +100,7 @@ . When you configure retention settings for the
 Teams channel message
 location, if a team has any shared channels, they inherit retention settings from their parent team.
-From late April 20206, retention policies also support newly created Teams call logs when you create the retention policies with PowerShell. For more information, see
+From late April 2026, retention policies also support newly created Teams call logs when you create the retention policies with PowerShell. For more information, see
 Retention policy for Teams call logs
 .
 Sign in to the Microsoft Purview portal
@@ -205,9 +205,7 @@ Retention policy for Teams call logs
 Teams call logs represent the collection of call-related data generated by Teams, including call data records (CDRs) and other call metadata. CDRs are also sometimes referred to as call detail records, or just call records.
 Prior to supporting the retention of Teams call logs in late April 2026, CDRs for Teams chat and Teams channels were included in retention policies for the Teams chat location. Going forward, new CDRs are supported only when you create a retention policy for Teams call logs. CDRs included in previous Teams chat retention policies continue to be managed by those same policies.
-This separate retention policy for call logs can be created only by using PowerShell, and has the following considerations:
-The policy is tenant-wide and can't be scoped to individual users.
-The policy doesn't support adaptive scopes or administrative units.
+This separate retention policy for call logs can be created and modified only by using PowerShell. It has the following considerations:
 The policy includes call logs for both Teams chat and Teams channels.
 The policy applies only to new call logs that are created after the policy is configured and active.
 After you create the retention policy for Teams call logs, it's displayed in
@@ -215,14 +213,13 @@ >
 Policies
 in the Microsoft Purview portal, wh
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Analytics
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Classification:** MEDIUM (General content update)

---

### 2. Customer Satisfaction
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Classification:** MEDIUM (General content update)

---

### 3. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)

---

### 4. Copilot Studio Kit — Compliance Hub
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Classification:** MEDIUM (General content update)

---

### 5. DSPM for AI
**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Classification:** MEDIUM (General content update)

---

### 6. Admin Roles
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Classification:** CRITICAL (Deprecation notice)

---

### 7. Agent ID Overview
**URL:** https://learn.microsoft.com/en-us/entra/agent-id/
**Classification:** MEDIUM (General content update)

---

### 8. Governing Agent Identities
**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Classification:** MEDIUM (General content update)

---

### 9. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)

---

### 10. Copilot Studio Licensing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Classification:** MEDIUM (General content update)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/architecture/ | https://learn.microsoft.com/en-us/agents/architecture/ |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*