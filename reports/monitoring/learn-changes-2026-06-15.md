# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-15
**Run Time:** 2026-06-15T12:17:32.212810+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 6 |
| MEDIUM Changes | 4 |
| Redirects | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | CRITICAL | 2.4 | Update portal-walkthrough |
| 2 | ...ilot-security-enhanced-admin-controls | MEDIUM | 2.8, 2.3, 1.18 | Review optional |
| 3 | whats-new | MEDIUM | None | Review optional |
| 4 | agent-365-overview | HIGH | 3.8, 2.25 | Review and update |
| 5 | dlp-policy-reference | HIGH | None | Review and update |
| 6 | ...ensitive-information-type-learn-about | HIGH | 1.13 | Review and update |
| 7 | create-retention-policies | HIGH | 4.3, 1.9 | Review and update |
| 8 | endpoint-dlp-getting-started | HIGH | 1.17 | Review and update |
| 9 | permissions-reference | CRITICAL | 2.23 | Monitor |
| 10 | create-retention-policies | HIGH | None | Review and update |
| 11 | whats-new | CRITICAL | None | Monitor |

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

## HIGH: Control Review Recommended

### 1. Agent 365 Overview Page (M365 Admin)

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

### 2. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -1921,6 +1921,8 @@ Conditions Microsoft 365 Copilot supports
 This feature is in preview.
 Content contains (sensitivity labels)
+Content contains (sensitive information types)
+Email is received from (External users) (preview)
 Condition groups
 Sometimes you need a rule to identify only one thing, such as all content that contains a U.S. Social Security Number, which is defined by a single SIT. However, in many scenarios where the types of items you're trying to identify are more complex and therefore harder to define, more flexibility in defining conditions is required.
 For example, to identify content subject to the U.S. Health Insurance Act (HIPAA), you need to look for:
@@ -2761,7 +2763,7 @@ Content is shared from Microsoft 365
 - with people outside my organization
 Not configured
-User notification emails, policy tips, DLP alerts, and incident reports are sent only when a file is shared with a guest and a guest access the file.
+User notification emails, policy tips, DLP alerts, and incident reports are sent when a file is shared with a guest or when a guest accesses the file.
 Content is shared from Microsoft 365
 - only with people inside my organization
 Not configured
@@ -2800,7 +2802,7 @@ Block everyone
 - When the first user outside the organization access the document, the event causes the document to be blocked.
 - It's expected that for a short time, the document is accessible by guests who have the link to the file.
-- User notification emails, policy tips, DLP alerts, and incident reports are sent when a file is shared with an guest and an guest accesses that file.
+- User notification emails, policy tips, DLP alerts, and incident reports are sent when a file is shared with a guest or when a guest accesses that file.
 Content is shared from Microsoft 365
 - with people outside my organization
 -

```

---

### 3. Sensitive Information Types

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

### 4. Retention Policies

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

### 5. Onboard Devices

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

### 6. Retention for SharePoint

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

### 1. Enhanced Admin Controls [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls
**Classification:** MEDIUM (General content update)

---

### 2. Copilot Studio Kit — Compliance Hub
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Classification:** MEDIUM (General content update)

---

### 3. Admin Roles
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Classification:** CRITICAL (Deprecation notice)

---

### 4. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)

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