# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-08
**Run Time:** 2026-10-08T12:58:10.051207+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 2 |
| MEDIUM Changes | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | capacity-storage | HIGH | 3.5 | Review and update |
| 2 | security-and-governance | MEDIUM | 1.8, 1.3, 1.1, 1.5, 1.4, 1.28, 2.8 | Update portal-walkthrough |
| 3 | microsoft-365-copilot-overview | MEDIUM | 3.8 | Review optional |
| 4 | message-center | HIGH | 2.10 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f040e3a56bb69012e979cbfad0c293adc3b50b23fef71987f1af19db90408a6f

**Affected Controls:**
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -115,6 +115,10 @@ Copilot Studio compliance offerings
 .
 Data loss prevention and governance
+Note
+Copilot Studio provides content moderation for predefined harmful-content categories, but Microsoft 365 Copilot governance and safety controls don't provide a tenant-configurable policy that blocks conversations based on arbitrary administrator-defined subjects or ethical categories. Learn more in
+Troubleshoot error messages
+.
 Copilot Studio supports an extensive set of
 data loss prevention features
 to help you manage the security of your data, along with

```

---

## HIGH: Control Review Recommended

### 1. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:cd459e23ec77bf6c833c001105bf89de2edfd3583f6998cc657c8ecba4a15a42

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

**What Changed:**
```diff
--- +++ @@ -563,17 +563,17 @@ Informational or warning notifications appear.
 Review growth and begin remediation.
 Stage 1: Restricted
-The tenant first exceeds 100% effective consumption
+The tenant first exceeds 100% effective consumption (time zero, or T0).
 Critical notifications appear. Environment create, copy, restore, and recover operations are blocked.
 Free storage, archive eligible data, add capacity, configure pay-as-you-go billing, or request a capacity extension.
 Stage 2: Administration mode
-The overage remains unresolved for 30 days
+The overage remains unresolved for 30 days from T0
 In addition to the restrictions applied in Stage 1, access to affected sandbox environments is limited to administrators.
 Administrators can temporarily take affected sandbox environments out of Administration mode to perform remediation activities. However, the storage overage lifecycle and timer continue to progress until the overage is resolved.
 Stage 3: Disabled
-The overage remains unresolved for 60 days
+The overage remains unresolved for 90 days from T0
 In addition to the restrictions applied in Stage 1, sign-in to affected sandbox environments is blocked for all users, including administrators. The environment and its data remain retained.
-Return the tenant to compliance, and then re-enable the environment.
+Return the tenant to compliance, and then re-enable the environment. Customer can reach the Microsoft support to explore data export options.
 The date the tenant first exceeds 100% effective consumption is the start of the lifecycle timeline. Resolving the effective deficit before the next stage prevents further progression. Sandbox environments with pay-as-you-go enabled do not progress through the storage overage lifecycle.
 Note
 Effective consumption represents the storage usage remaining after cross-capacity-type borrowing has been applied. Storage notifications, overage calculations, and storage validation actions are based on effective consumpt
```

---

### 2. Message Center

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide
**Section:** Microsoft 365 Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:db21b004d1939a0a4517042fbca5fdbbc1f244268ebea7eaf42d8e158817c503

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**What Changed:**
```diff
--- +++ @@ -44,9 +44,9 @@ For frequently asked questions about Message center, see
 Message center FAQ
 .
-Feature release status for your organization in Message Center
-Note
-The release status is only available for limited Microsoft Teams feature announcements.
+Feature release status for your organization in Message center
+Note
+The release status is only available for limited feature announcements.
 For each new and updated feature announcement in Message center, the
 Status for your org
 field provides a release status to help you track when a feature is available in your tenant.
@@ -60,7 +60,7 @@ Updates to feature release status are provided on the original Message center post. Filtering capability on
 Status for your org
 allows easier visibility on the updated release status.
-The release status is only available for new and updated features that are also announced on Microsoft 365 Public Roadmap and that have general availability status (production ready). If you don't see release status on a message, it means the release status isn't available for that feature.
+The release status is only available for new and updated features that are also announced on AI at Work Roadmap and that have general availability status (production ready). If you don't see release status on a message, it means the release status isn't available for that feature.
 Relevance recommendation
 For each new Message center post, we provide a recommendation for how relevant the change is for your organization. This recommendation is based on multiple factors such as:
 Apps and service usage.
@@ -81,62 +81,7 @@ Microsoft needs your feedback to improve the accuracy and relevance for Message center posts. Use the
 Extended Feedback
 option on Message center posts to send us your opinions.
-Filter messages
-Message center presents a view of all active messages in a table format. By default, it shows the most recent message at the top of the list.
-Use the
-Service
-,
-Tag
-, and
-Message 
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Security and Governance
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f040e3a56bb69012e979cbfad0c293adc3b50b23fef71987f1af19db90408a6f

---

### 2. M365 Copilot Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:93988ca5e31c7c3ed5da8c6471c7ce9150a4da12a251e7fcce0ea87b28519eec

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*