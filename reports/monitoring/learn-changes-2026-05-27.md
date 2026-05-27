# Microsoft Learn Documentation Changes

**Run Date:** 2026-05-27
**Run Time:** 2026-05-27T09:54:06.972059+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 3 |
| MEDIUM Changes | 1 |
| Redirects | 1 |
| Errors | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | copilot-hub | HIGH | 3.1, 3.8 | Review and update |
| 2 | agent-365-overview | HIGH | 3.8, 2.25 | Review and update |
| 3 | permissions-reference | MEDIUM | 2.23 | Review optional |
| 4 | whats-new | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Copilot Hub

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -54,13 +54,7 @@ area for in-product configuration.
 Note
 Tenant users with environment access can view Copilot settings.
-Control who can use AI features in model-driven apps (preview)
-[This section is prerelease documentation and is subject to change.]
-Important
-This is a preview feature.
-Preview features arenât meant for production use and might have restricted functionality. These features are subject to
-supplemental terms of use
-, and are available before an official release so that customers can get early access and provide feedback.
+Control who can use AI features in model-driven apps
 Admins can define who within an environment can use Copilot capabilities in model-driven appsâeither by explicitly allowing specific users or allowing all users except a defined exclusion list. This capability is currently in preview and is only for environments activated for
 Managed Environments
 , with a subset of Copilot features adhering to it. Review the following table to learn which capabilities adhere to this configuration.

```

---

### 2. Agent 365 Overview Page (M365 Admin)

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.25/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -53,6 +53,15 @@ The Microsoft Frontier program gives organizations early access to innovative and emerging AI capabilities in Microsoft 365 before those features reach general availability (GA). Frontier previews are subject to the existing preview terms of your customer agreements. For more information, see
 Get started with the Microsoft Frontier program
 .
+Prerequisites
+Before you can manage agents in the Microsoft 365 admin center, confirm the following requirements are met:
+Your organization has the required Microsoft 365 subscription and licenses for either Microsoft 365 Copilot or Microsoft Agent 365 capabilities.
+Users who create, publish, or use agents have the appropriate licenses assigned.
+Youâre assigned an administrator role that includes permissions to manage settings for either Microsoft 365 Copilot or Microsoft Agent 365 in the Microsoft 365 admin center.
+For more information, see the following resources:
+Plans and licensing for Microsoft Agent 365
+License options for Microsoft 365 Copilot
+Agent management roles and permissions
 View the Agent overview
 You can access and view the
 Agent overview

```

---

### 3. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -203,6 +203,10 @@ Data loss prevention policy tip reference for Outlook for Android, iOS, and macOS
 . A new reference article covering DLP policy tips, supported conditions, oversharing dialogs, and override capabilities for Outlook on Android, iOS, and macOS.
 Data Security Investigations
+In preview
+:
+Proactive AI insights from Data Security Posture Management (DSPM)
+automatically create and refresh a single investigation for your tenant every 24 hours. The DSPM exfiltration objective card displays risk counts across five fixed categories, giving security teams continuous visibility into recently exfiltrated sensitive data without manual investigation creation.
 New
 : A new Data Security Investigation Contributor role automatically provides
 Data Security Investigations access

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Admin Roles
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Classification:** MEDIUM (General content update)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/architecture/ | https://learn.microsoft.com/en-us/agents/architecture/ |

---

## Errors

- **Encryption** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/admin/manage-encryption-key

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*