# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-01
**Run Time:** 2026-10-01T12:37:27.388915+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| MEDIUM Changes | 4 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | capacity-storage | CRITICAL | 3.5 | Monitor |
| 2 | pipelines | MEDIUM | 1.28, 2.5, 2.3 | Update portal-walkthrough |
| 3 | admin-deployment-hub | HIGH | 2.1, 2.3 | Update portal-walkthrough |
| 4 | whats-new | MEDIUM | None | Review optional |
| 5 | microsoft-365-copilot-overview | MEDIUM | 3.8 | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Pipelines Overview

**URL:** https://learn.microsoft.com/en-us/power-platform/alm/pipelines
**Section:** Power Platform ALM
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:debad1440e29a86bbb9bd9f42fc11fc121a60daf86fac98d11d90207e7a26c6e

**Affected Controls:**
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -114,14 +114,9 @@ Settings
 . Turn on the automatic managed environment setting for each pipeline host.
 Important
-Starting February 2026, Microsoft will start enabling managed environments for any pipeline target environments that aren't already enabled. Customers will be notified via Microsoft 365 Message center.
-We recommend you review and enable managed environments for all pipeline targets now. You can do this manually now or set it to occur automatically:
-Manually:
-Go to enable
-managed environments
-.
-Automatically:
-Configure the setting for new pipelines as described above.
+Starting in October 2026, the admin deployment page notifies admins when pipelines deploy to unmanaged target environments. Admins have 30 days to approve enabling managed environments before future deployments to the target are blocked. You can request one additional 30-day extension for each environment. For more information, see
+Managed environments enforcement for pipelines
+.
 Can I configure approvals for deployments?
 Yes. See
 delegated deployments

```

---

### 2. Admin Deployment Hub

**URL:** https://learn.microsoft.com/en-us/power-platform/alm/admin-deployment-hub
**Section:** Power Platform ALM
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:84673dce65a415b096e803ada2cf65d59faa80c6742b695ae68977cbe8ddfe24

**Affected Controls:**
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.3/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -120,43 +120,29 @@ FAQ
 Are managed environments required for deployment pipelines, and what does this mean for my organization?
 Yes. All target environments used in Power Platform deployment pipelines have always been required to be managed environments for compliant usage. This requirement helps your organization benefit from enhanced governance, improved security, and streamlined license management.
-How can I ensure pipelines targets are managed environments automatically?
-Tenant admins (Power Platform and Dynamics 365 admins) can enable a setting that automatically converts pipelines target environments to managed environments, ensuring compliance with Microsoft standards. Managed environments are then enabled on the target during the next deployment.
-To enable the setting, go to the Power Platform admin center
-Deployments
+What happens when pipelines deploy to unmanaged target environments starting in October 2026?
+Starting in October 2026, the admin deployment page notifies admins when pipelines deploy to an unmanaged target environment. Admins must approve enabling managed environments for the target within 30 days of the notification to prevent future pipelines deployments from being blocked.
+Admins can enable managed environments for deployment targets individually or turn on
+automatic enablement
+. If more time is needed, admins can request one additional 30-day extension for each environment. After the grace period or extension expires, the system blocks pipelines deployments to the unmanaged target environment.
+What can makers without tenant-administrator permissions do?
+Makers can view affected targets, continue deploying during the allowed period, and acknowledge the one-time extension, but they can't enable managed environments. Ask your tenant administrator to enable managed environments before the countdown expires; enabling it removes the deployment block.
+Can automatic enablement prevent this deployment block?
+Yes. Power Pla
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Capacity Storage
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:37b9b8de8c703350ee45162a009a7ad6a863fc417f1b336fc61b6e0ae5b8ca89

---

### 2. Pipelines Overview
**URL:** https://learn.microsoft.com/en-us/power-platform/alm/pipelines
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:debad1440e29a86bbb9bd9f42fc11fc121a60daf86fac98d11d90207e7a26c6e

---

### 3. Copilot Studio guidance hub — What's new
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:9c4fe4542257e1c76cb6587b96b01a429596b1cf62916d06b0b1bd3478513c5e

---

### 4. M365 Copilot Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b991bea1c91ebb637767f5bbb2f160715f9c44969af84210f53d9e4d238afd90

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*