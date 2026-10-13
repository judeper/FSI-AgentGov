# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-13
**Run Time:** 2026-10-13T13:44:27.918130+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 4 |
| MEDIUM Changes | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | welcome-content | HIGH | None | Review and update |
| 2 | environment-strategy | HIGH | 2.4 | Review and update |
| 3 | manage-copilot-agents-integrated-apps | HIGH | 3.11, 3.8, 3.6, 3.1, 2.25 | Review and update |
| 4 | restricted-content-discovery | MEDIUM | 4.6, 4.1, 4.7, 1.14, 1.3 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Maker Onboarding (Welcome Content)

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/welcome-content
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:0f7ce5f002e522adca0d55e81afe030be762f0c1c24679eb67b73c6ea367aa11

**What Changed:**
```diff
--- +++ @@ -69,7 +69,9 @@ Include consent button and log maker activity
 , and then enter the URL in
 Terms and conditions
-. Makers must read and acknowledge the linked content before they can continue. Consent activity is logged and available for audit in Microsoft Purview.
+. Makers must read and acknowledge the linked content before they can continue. Consent activity,
+UserConsented
+, is logged and available for audit in Microsoft Purview along with the date and time of the consent.
 Select
 Preview in a new tab
 to see how the text you entered, or Markdown renders.

```

---

### 2. Environment Strategy

**URL:** https://learn.microsoft.com/en-us/power-platform/guidance/adoption/environment-strategy
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:38a8b1dd054d24f7b41fb3e2edcc682f165a3b0bc25cb2ade98a6f78e64d6589

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**What Changed:**
```diff
--- +++ @@ -155,7 +155,7 @@ .
 You can use environment routing by itself, but the recommended way is to use it with environment groups. When used this way, any environment that's created is associated with the group that you designate to contain all new developer environments, ensuring that it's immediately covered by your governance policies.
 Makers are automatically assigned a security role that makes them an environment admin of their developer environment. When the environment is a part of an environment group, the makerâas the environment adminâcan't change the environment settings because they're managed by the environment group rules. Only admins, who can modify the group rules, can make any changes.
-You can impose even more control in two ways. First, you can disallow manual creation of developer environments in your tenant settings. When this option is set, makers can't create environments themselves in the admin portal. They also won't get one automatically created by the routing policy. Second, you can specify a security group, in the routing policy, to limit who can automatically get an environment created.
+You can impose even more control by specifying a security group in the routing policy to limit who can automatically get an environment created.
 Initially, environment routing supports routing new and existing makers away from the default environment when they use
 make.powerapps.com
 . Over time, other Power Platform services will support the environment routing feature.

```

---

### 3. Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:2eaf05576e7841aec40d60e59be432e1c1158f10ac1e52bc390687bca0342370

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -89,6 +89,15 @@ is enabled for Copilot Studio. You can also manage flows using the
 Power Platform admin center
 .
+Note
+The same Copilot Studio agent (declarative or custom engine) can appear more than once in the admin center with different publisher states, such as
+Shared by creator
+and
+Published by your organization
+. Depending on the publishing lifecycle and the actions that creators and admins take, these duplicate-looking entries can represent separate lifecycle and publisher records for the same underlying agent. They're expected and by design, not an error.
+For lifecycle details and available admin actions, see
+How one agent can appear as multiple entries
+.
 Get started
 To get started managing agents within Microsoft 365 admin center, see
 Agent management in Microsoft 365 admin center

```

---

### 4. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8008bf21308d8c79cd51f278cd6b7c7adb30338d0463808e22c41fa0e1f1f278

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -51,7 +51,7 @@ Restricted Content Discovery is a site-level setting. When you turn on the setting, Microsoft 365 search systems propagate it so that content from the site doesn't appear in organization-wide discovery experiences.
 Even when Restricted Content Discovery is enabled:
 Site permissions stay the same.
-Users can still discover content they own or have recently interacted with.
+Users can continue to access content they already have permission to access.
 The feature doesn't remove content from the Microsoft 365 search index.
 Because the setting must propagate across indexing systems, updates can take time to become fully effective. The amount of time depends on site size, the number of files in each site, and the number of concurrent updates being processed.
 Prerequisites

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Restricted Content Discovery
**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8008bf21308d8c79cd51f278cd6b7c7adb30338d0463808e22c41fa0e1f1f278

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*