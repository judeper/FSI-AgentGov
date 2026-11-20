# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-20
**Run Time:** 2026-11-20T14:59:52.553834+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 4 |
| HIGH Changes | 2 |
| MEDIUM Changes | 3 |
| Redirects | 11 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | capacity-storage | HIGH | 3.5 | Review and update |
| 2 | authoring-test-bot | HIGH | 2.5 | Update portal-walkthrough |
| 3 | dlp-policy-reference | MEDIUM | 1.5 | Update portal-walkthrough |
| 4 | advanced-management | MEDIUM | 4.5, 4.6, 4.1, 4.2, 1.3 | Review and update |
| 5 | data-access-governance-reports | MEDIUM | 4.5, 4.6, 4.4, 4.1, 4.2, 1.3, 1.14 | Update portal-walkthrough |
| 6 | microsoft-purview-service-description | HIGH | None | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Test Your Agent

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:f16aeb9faf716960e1f45be78306ae02c2dc15a38f3b59cb2e68f227948d6685

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -71,9 +71,8 @@ Tip
 You can update a topic at any time while interacting with the agent. Save your topic to apply changes and continue the conversation with your agent.
 Your conversation isn't automatically cleared when you save a topic. If you want your agent to forget the test conversation and start over, select the
-Reset
-icon
-at the top of the test panel.
+Start new test session
+icon at the top of the panel.
 You can use queries you send in the test chat to
 create automated test sets
 for evaluating your agent.
@@ -141,7 +140,7 @@ Teams plan / Teams app
 At the top of theâ¯
 Test your agent
-â¯pane, select the three dots (
+â¯panel, select the three dots (
 â¦
 ), and thenâ¯select
 Save snapshot

```

---

### 2. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b7914cb6a32c24414befaab41abf983f09d6d1925e0df5e4eafccf979d4f3b86

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.26/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -950,6 +950,7 @@ - Only available in the
 Custom
 policy template
+- Administrative unit scoping also applies to Cowork.
 Managed cloud apps
 No
 Account or Distribution group
@@ -2408,7 +2409,7 @@ Content is not labeled
 Additional notes:
 Paste to Browser supports SITs, not Sensitivity Labels.
-Paste to Browser doesn't evaluate on text smaller than 30 characters.
+Paste to Browser doesn't evaluate on text smaller than 15 characters or 30 bytes.
 Advanced Classification isn't supported.
 Contextual Summary doesn't show for Paste to Browser events.
 Paste to Browser takes 2 seconds to evaluate before allowing the paste action.

```

---

### 3. Data Access Governance Reports

**URL:** https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:1da61bb4eefc6db93e0ae6ba926eb76ad04e0da753bd6687e9ac13b716343393

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/4.2/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -43,6 +43,7 @@ Snapshot reports
 Site permissions across your organization
 (Recommended)
+Site permissions for users or groups
 Sensitivity label applied to files
 Activity reports
 Sharing links
@@ -56,8 +57,8 @@ Currently, three types of snapshot reports are available:
 Site permissions report
 : Provides a comprehensive snapshot of the permission structure across all SharePoint and OneDrive sites. It helps you identify sites with the broadest user access, such as sites with thousands of users, external guests, or "Everyone except external users" permissions.
-Site permissions for users report
-: Lists all sites a specified user can access. Admins can use this report to determine whether the user can access the entire site or specific sections, granted directly to the user or indirectly through groups.
+Site permissions for users or groups report
+: Lists all sites a specified user or group can access and the extent of that access. Each report contains either users or groups, not both.
 Sensitivity label for files report
 : Identifies SharePoint sites containing files with specific sensitivity labels applied. You can use this report to verify that appropriate security policies are in place for your most sensitive content.
 What are activity reports?
@@ -89,10 +90,11 @@ Learn how to create and use the
 site permissions for your organization report
 .
-What is the site permissions for users report?
-The site permissions for users report is the next snapshot report that provides a comprehensive view into permissions of the specified users across all SharePoint and OneDrive sites. This report lists all sites a user can access and allows admins to determine whether they can access the entire site or specific sections, granted directly to the user or indirectly through groups. This approach helps you quickly assess your overall security posture and identify sites that need immediate attention.
+What is the site permissions for users or groups report?
+The si
```

---

### 4. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:c11ac6b469614885a80e99c926841b968cefc6f443db4aa96abd3e9d5d5c1b35

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.10/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.13/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -61,14 +61,14 @@ Office 365 E3/E1/A3/A1/G3/G1/F3
 Microsoft 365 Business Basic/Standard/Premium
 Audit (Standard)
-Yes
-Yes
-Yes
+Included
+Included
+Included
 Audit (Standard) for Microsoft Copilot interactions
 1
-Yes
-Yes
-Yes
+Included
+Included
+Included
 1
 Audit logs for Microsoft Copilot interactions are generated only when Microsoft Copilot is licensed and in use.
 Microsoft Purview Audit (Premium)
@@ -86,16 +86,16 @@ 3
 Audit (Premium)
 1
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 Audit (Premium) for Microsoft Copilot interactions
 2
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 1
 Audit (Premium) includes all Audit (Standard) capabilities.
 2
@@ -128,30 +128,30 @@ Microsoft 365 E5/A5/G5, Microsoft Purview Suite/EDU/GOV/FLW and Microsoft Defender + Purview Suite FLW, and Microsoft 365 E5/A5/F5/G5 Insider Risk Management
 Office 365 E5/A5/G5
 Communication Compliance
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 Microsoft Copilot for Microsoft 365 prompt and response analysis
-Yes
-Yes
-No
-No
+Included
+Included
+Not included
+Not included
 Microsoft Teams chats
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 Viva Engage conversations
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 Exchange Online emails
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 For more information, seeâ¯
 Get started with communication compliance
 .
@@ -167,7 +167,7 @@
```

---

## HIGH: Control Review Recommended

### 1. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:ca9c53f9270e8fc4df1c601e5e413d63d3d20c947dc20d14833596c68230fe25

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

**What Changed:**
```diff
--- +++ @@ -564,16 +564,16 @@ Review growth and begin remediation.
 Stage 1: Restricted
 The tenant first exceeds 100% effective consumption (time zero, or T0).
-Critical notifications appear. Environment create, copy, restore, and recover operations are blocked.
+Critical notifications appear. Environment create, copy, restore, convert, recover and add Dataverse to an environment operations are blocked.
 Free storage, archive eligible data, add capacity, configure pay-as-you-go billing, or request a capacity extension.
 Stage 2: Administration mode
 The overage remains unresolved for 30 days from T0
 In addition to the restrictions applied in Stage 1, access to affected sandbox environments is limited to administrators.
-Administrators can temporarily take affected sandbox environments out of Administration mode to perform remediation activities. However, the storage overage lifecycle and timer continue to progress until the overage is resolved.
+Free storage, archive eligible data, add capacity, configure pay-as-you-go billing, or request a capacity extension. Administrators can temporarily take affected sandbox environments out of Administration mode to perform remediation activities. However, the storage overage lifecycle and timer continue to progress until the overage is resolved.
 Stage 3: Disabled
 The overage remains unresolved for 90 days from T0
 In addition to the restrictions applied in Stage 1, sign-in to affected sandbox environments is blocked for all users, including administrators. The environment and its data are limited to data export and recovery options through support tickets.
-Return the tenant to compliance, and then re-enable the environment. If tenant remains in overage, customer can reach the Microsoft support for the sole purpose of directing data export options, if needed.
+Free storage, archive eligible data, add capacity, configure pay-as-you-go billing, or request a capacity extension. Return the tenant to compliance, and then re-ena
```

---

### 2. Advanced Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:96fd504aac2a357165fdf448c01ca3e67a6b1212e13b4e2270494990c7d01cb3

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -76,8 +76,8 @@ : Identify sites that might contain overshared or sensitive content. AI insights can be generated from DAG reports to highlight access risk patterns and recommend next steps. You can also initiate site access reviews from a DAG report. DAG reports include:
 Permission state reports for sites, OneDrive sites, and files
 : Use this report to get a snapshot of your organization's current permission structure across all SharePoint and OneDrive sites, helping you understand how broadly your data is exposed and identify potential oversharing risks.
-Site permissions for a given user report
-: Use this report to get a list of all the sites a user can access and how access is granted.
+Site permissions for users or groups report
+: Use this report to list all sites accessible to a user, Microsoft 365 group, or Microsoft Entra security group and review the extent of access.
 Sensitivity label snapshot report
 : Use this report to get a snapshot of sensitivity label distribution across all SharePoint and OneDrive sites.
 Sharing links activity reports

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. DLP Policy Reference
**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b7914cb6a32c24414befaab41abf983f09d6d1925e0df5e4eafccf979d4f3b86

---

### 2. Advanced Management
**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:96fd504aac2a357165fdf448c01ca3e67a6b1212e13b4e2270494990c7d01cb3

---

### 3. Data Access Governance Reports
**URL:** https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:1da61bb4eefc6db93e0ae6ba926eb76ad04e0da753bd6687e9ac13b716343393

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-essentials-overview | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-prerequisites | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-visual-map | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-checklist | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-blueprint | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*