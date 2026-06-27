# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-26
**Run Time:** 2026-06-26T09:29:50.695126+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 4 |
| MEDIUM Changes | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | planned-features | MEDIUM | 3.8, 2.25, 2.17, 1.4 | Review and update |
| 2 | insider-risk-management-policies | HIGH | 1.12 | Update portal-walkthrough |
| 3 | ...management-settings-policy-indicators | HIGH | 1.12 | Update portal-walkthrough |
| 4 | concept-authentication-strengths | MEDIUM | None | Review and update |
| 5 | permissions-reference | CRITICAL | 2.23 | Monitor |
| 6 | site-lifecycle-management | CRITICAL | 4.2, 4.3 | Review and update |
| 7 | request-site-attestations | HIGH | 4.2 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Create Insider Risk Policies

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:575feddecb2f898d1cd36bc081aa3928299e20446a4da123f6bebd4b2e72a4d3

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -241,7 +241,9 @@ Policy triggers aren't working, or policy trigger requirements aren't properly configured
 . Policy functionality might depend on other services or configuration requirements to effectively detect triggering events to activate risk score assignment to users in the policy. These dependencies might include issues with connector configuration, Microsoft Defender for Endpoint alert sharing, or data loss prevention policy configuration settings.
 Volume limits are nearing or over limits
-. Insider Risk Management policies use numerous Microsoft 365 services and endpoints to aggregate risk activity signals. Depending on the number of users in your policies, volume limits might delay identification and reporting of risk activities. Learn more about these limits in the Policy template limits section of this article.
+. Insider Risk Management policies use numerous Microsoft 365 services and endpoints to aggregate risk activity signals. Depending on the number of users in your policies, volume limits might delay identification and reporting of risk activities. Learn more about these limits in the
+Policy template limits
+section.
 To quickly view the health status for a policy, go to the
 Policy
 tab and check the
@@ -359,7 +361,9 @@ Check that your HR connector is configured correctly and sending data, or come back and check the policy status.
 You're approaching the maximum limit of users being actively scored for this policy template
 All policy templates
-Each policy template has a maximum number of included users. See the template limit section details.
+Each policy template has a maximum number of included users. See the
+Policy template limits
+section for details.
 Review the users in the Users tab and remove any users who don't need to be scored anymore.
 Your organization doesn't have a Microsoft Defender for Endpoint subscription
 - Security policy violations
@@ -373,7 +377,7 @@ Insider Risk Management
 solution in the Microsoft Purview
```

---

### 2. Insider Risk Indicators

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators
**Section:** Microsoft Purview
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:b46293ae3738d35d601180a99c2d48b0c58bb57d26de53b6ec702607a6fe2098

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -52,6 +52,7 @@ Data leaks by priority users
 templates, you get more flexibility and customization for your policies and when users are in-scope for a policy. You can also define risk management activity thresholds for these triggering indicators for more fine-grained control in a policy.
 Define the insider risk policy indicators that are enabled in all insider risk policies
+To enable policy indicators for all insider risk policies, complete the following steps:
 Select
 Settings
 , then select
@@ -68,7 +69,8 @@ Users dashboard
 and open the
 User activity
-tab in the details pane.## Two types of policy indicators: built-in indicators and custom indicators
+tab in the details pane.
+Two types of policy indicators: built-in indicators and custom indicators
 Indicators and pay-as-you-go billing
 Some indicators included in Insider Risk Management require that you enable the
 pay-as-you-go billing model
@@ -81,7 +83,7 @@ : Use custom indicators together with the
 Insider Risk Indicators (preview) connector
 to bring non-Microsoft detections to Insider Risk Management. For example, you might want to extend your detections to include Salesforce and Dropbox and use them alongside the built-in detections provided by the Insider Risk Management solution, which is focused on Microsoft workloads (SharePoint Online and Exchange Online, for example).
-Learn more about creating a custom indicator
+Create a custom indicator
 Built-in indicators
 Insider Risk Management includes the following built-in indicators.
 Office indicators
@@ -94,9 +96,9 @@ These indicators include policy indicators for Google Drive, Box, and Dropbox that you can use to detect techniques used to determine the environment, gather and steal data, and disrupt the availability or compromise the integrity of a system. To select from
 cloud storage indicators
 , you must
-first connect to the relevant cloud storage apps in Microsoft Defender
-.
-After configuring these indicators, you can turn off 
```

---

## HIGH: Control Review Recommended

### 1. Planned Features (2026 Wave 1) [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c6c09662477d84474fbfd52afdbe48bce3c4d4aaffbf9b679e97faa5532b7f52

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -120,7 +120,7 @@ See a unified view of errors, warnings, and governance notifications
 Admins, makers, marketers, or analysts, automatically
 May 15, 2026
-Jun 2026
+Jul 2026
 Invoke agents as workflow steps with the agent node
 Admins, makers, marketers, or analysts, automatically
 Apr 1, 2026

```

---

### 2. Phishing-Resistant MFA

**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths
**Section:** Microsoft Entra ID
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ea18b55ee7310a630ffe2a3ee8302b6cceb7703d9f692687b187700e163c8813

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.11/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -98,6 +98,7 @@ SMS sign-in
 Password
 Federated single-factor
+QR code
 1
 Something the user has
 refers to one of the following methods: text message, voice, push notification, software OATH token, or hardware OATH token.

```

---

### 3. Site Lifecycle Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/site-lifecycle-management
**Section:** SharePoint Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:6ead14d95e32f5c216c1dac8cf03ca26e9bd017da6cf40d9021833e7affdfcc0

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -19,399 +19,102 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Manage inactive sites by using inactive site policies
+SharePoint site lifecycle management
 Feedback
 Summarize this article for me
-Site lifecycle management capabilities in
+Site lifecycle management policies in
 Microsoft SharePoint Advanced Management
-help you improve site governance by automating the process of detecting inactive sites and notifying site owners by email. Site owners can then review and confirm whether their sites are still active.
-You can configure an inactive sites policy in the SharePoint admin center. This article describes how to set up an inactive site policy with notifications and enforcement actions.
-Prerequisites for an inactive site policy
-See
-SharePoint Advanced Management prerequisites
+help you maintain site governance at scale. These policies automate common governance tasks, so sites stay active, properly owned, and regularly reviewed throughout their lifecycle.
+As your organization creates more SharePoint sites, Microsoft Teams-connected sites, and Microsoft 365 group-connected sites, it becomes increasingly difficult for your administrators to manually identify inactive sites, ownerless sites, or sites that no longer meet business requirements. Site lifecycle management policies help you automate these governance processes by monitoring sites, notifying responsible users, collecting responses, and taking enforcement actions when necessary.
+Benefits of site lifecycle management
+Site lifecycle management policies help you:
+Reduce the number of inactive or abandoned sites.
+Identify and address sites that have insufficient ownership.
+Verify that sites continue to serve a valid business purpose.
+Improve compliance with organizational governance requirements.
+Automate notifications, reporting, and remediation workflows.
+Maintain a healthier and more manageable SharePoint environment.
+Types of site lifecycle m
```

---

### 4. Site Attestation

**URL:** https://learn.microsoft.com/en-us/sharepoint/request-site-attestations
**Section:** SharePoint Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:6d22ebdf32a0536c64c4db7f3b915714ceba446a80e7eadda6b41010e7837ae0

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**What Changed:**
```diff
--- +++ @@ -22,17 +22,21 @@ Request recurring site attestations for SharePoint sites
 Feedback
 Summarize this article for me
-Site lifecycle management policies in
-Microsoft SharePoint Advanced Management
-help your organization improve site governance. Site attestation involves regular reviews by site owners or site administrators to check and confirm the accuracy of site information, including the site's necessity, its owners, members, permissions, and sharing settings. For sites that remain unattested, you can choose to automate enforcement actions to prevent risks of content overexposure. This approach ensures ongoing site compliance and actively reduces risks such as information oversharing.
-Site attestation policies help you manage periodic attestation of sites at scale. You can configure a site attestation policy in the SharePoint admin center. This article describes how to create and configure a site attestation policy in either active or simulation mode.
+Site attestation policies help you periodically verify that SharePoint sites continue to meet your organization's governance requirements. These policies request reviews from site owners or site administrators, who confirm whether a site is still needed and whether its ownership, membership, permissions, and sharing settings remain appropriate.
+You can configure site attestation policies to send recurring review requests and apply enforcement actions when required reviews aren't completed.
+For an overview of site lifecycle management policies, see
+SharePoint site lifecycle management
+.
+This article describes how to create a site attestation policy with notifications and enforcement actions.
 Requirements for a site attestation policy
 See
 SharePoint Advanced Management prerequisites
 .
-How does a site attestation policy work?
-When a site attestation policy runs (usually on a monthly basis), it generates a report that lists sites requiring attestation according to policy criteria. Site owners and
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c6c09662477d84474fbfd52afdbe48bce3c4d4aaffbf9b679e97faa5532b7f52

---

### 2. Phishing-Resistant MFA
**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ea18b55ee7310a630ffe2a3ee8302b6cceb7703d9f692687b187700e163c8813

---

### 3. Admin Roles
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:d058dc647c7aa8597a8b1732011c1a81547a432ba740f6d2929c83b69879162e

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*