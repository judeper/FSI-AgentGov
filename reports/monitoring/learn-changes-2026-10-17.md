# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-17
**Run Time:** 2026-10-17T10:16:48.555850+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 3 |
| MEDIUM Changes | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | managed-environment-overview | CRITICAL | 3.7, 1.8, 2.2, 2.7, 2.1, 2.15 | Update portal-walkthrough |
| 2 | default-environment-routing | CRITICAL | 2.15 | Review and update |
| 3 | create-developer-environment | CRITICAL | 2.15 | Monitor |
| 4 | backup-restore-environments | CRITICAL | 2.4 | Update portal-walkthrough |
| 5 | capacity-storage | HIGH | 3.5 | Review and update |
| 6 | fundamentals-what-is-copilot-studio | MEDIUM | 2.13 | Review optional |
| 7 | whats-new | HIGH | None | Review and update |
| 8 | pricing-billing-skus | CRITICAL | 3.5, 2.1 | Monitor |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Managed Environments

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:c162b49dc905209327310140517e637947acd24f3a9f8f86f9a999118ba26f1a

**Affected Controls:**
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 2.2: Control 2.2: Environment Groups and Tier Classification
  - File: `controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md`
- Control 2.7: Control 2.7: Vendor and Third-Party Risk Management
  - File: `controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md`
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.15/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.1/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -56,6 +56,9 @@ Managed environment isn't included as an entitlement in the Developer Plan when users run their assets. For more information about managed environments and the Developer Plan, see
 Power Apps Developer Plan Guide: Features and Benefits
 .
+Unmanaged developer environments are deprecated. To keep an existing developer environment, enable Managed Environments on it before December 15, 2026. Learn more in
+Deprecation of unmanaged developer environments and the Power Apps Developer Plan
+.
 Related content
 Enable managed environments
 Usage insights

```

---

### 2. Backup and Restore

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:7842aa27ba00bf93f0e5db6db6557600076d0b130a0c49f53f513ab170528c2a

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -37,10 +37,10 @@ Sandbox
 7 days
 7 days
-Developer
-7 days
-7 days
-Teams
+Developer***
+7 days
+7 days
+Teams***
 7 days
 7 days
 Default**
@@ -59,6 +59,11 @@ .
 ** You can't restore a system backup over the default environment. Instead, Power Platform admins can use the Power Platform admin center to restore a default environment system backup to a developer environment. Learn more in
 Backup and restoration of the default environment
+.
+*** Unmanaged developer environments and Dataverse for Teams environments are deprecated. Backups of these environments don't replace the actions required to keep your apps, flows, and data before the environments are disabled. Learn more in
+Deprecation of unmanaged developer environments and the Power Apps Developer Plan
+and
+Deprecation of Microsoft Dataverse for Teams environments
 .
 System backup and restore operations aren't supported for trial-type environments. To use the full set of features, including system backup and restore options, go to
 Convert either type of trial environment to a production environment

```

---

## HIGH: Control Review Recommended

### 1. Environment Routing

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:c9e535fdfa947a69c260024c2212b1b3a16f6adf133ab7358a19a72f5e8719b0

**Affected Controls:**
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -49,6 +49,9 @@ unaffected
 by this feature. Learn more about the developer environment and developer plan in
 Power Apps Developer Plan Guide: Features and Benefits
+.
+Unmanaged developer environments are deprecated, and they're suspended starting December 15, 2026. Environment routing creates managed developer environments, which aren't affected by this deprecation. Learn more in
+Deprecation of unmanaged developer environments and the Power Apps Developer Plan
 .
 The
 Environment assignment: Developer

```

---

### 2. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:1c3aa8a2beaadebe4961cdcaf17c18d957a5a778d9632917ccae503513c6e8c1

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

**What Changed:**
```diff
--- +++ @@ -573,7 +573,7 @@ Stage 3: Disabled
 The overage remains unresolved for 90 days from T0
 In addition to the restrictions applied in Stage 1, sign-in to affected sandbox environments is blocked for all users, including administrators. The environment and its data remain retained.
-Return the tenant to compliance, and then re-enable the environment. Customer can reach the Microsoft support to explore data export options.
+Return the tenant to compliance, and then re-enable the environment. If tenant remains in overage, customer can reach the Microsoft support for the sole purpose of directing data export options, if needed.
 The date the tenant first exceeds 100% effective consumption is the start of the lifecycle timeline. Resolving the effective deficit before the next stage prevents further progression. Sandbox environments with pay-as-you-go enabled do not progress through the storage overage lifecycle.
 Note
 Effective consumption represents the storage usage remaining after cross-capacity-type borrowing has been applied. Storage notifications, overage calculations, and storage validation actions are based on effective consumption rather than raw storage consumption.
@@ -890,14 +890,14 @@ Exiting administration mode can restore access temporarily, but it doesn't:
 Resolve the tenant storage overage.
 Add storage entitlement.
-Pause or reset the lifecycle timeline.
+Pause or reset the overage lifecycle timeline.
 Prevent the environment from progressing to the next stage if the tenant remains over capacity.
-Complete a tenant-level remediation to stop the lifecycle.
+Complete a tenant-level remediation to stop the overage lifecycle.
 Re-enable a disabled sandbox
 Before re-enabling a disabled sandbox, bring the tenant back within its effective storage entitlement by following one of these
 remediation options
 .
-After capacity validation confirms that the tenant is within entitlement, an administrator can re-enable each affected environment in the Power
```

---

### 3. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:e4bda8e46d696d3c62f396c1871d11cf784fdbd7cba39452aea8aacb604c33e4

**What Changed:**
```diff
--- +++ @@ -37,6 +37,12 @@ for data governance solutions.
 Roadmap
 for data security and risk and compliance solutions.
+October 2026
+Data Loss Prevention
+General availability
+: Endpoint data loss prevention (DLP) can now monitor sensitive data transferred over FTP and SFTP from managed Windows devices. It can enforce restrictive actions to help prevent data exfiltration. Configure FTP and SFTP transfer activities in your Endpoint DLP policies to get started. See
+Protect FTP and SFTP transfers with Microsoft Purview Endpoint DLP
+.
 September 2026
 Data Loss Prevention
 General availability

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Developer Environments
**URL:** https://learn.microsoft.com/en-us/power-platform/developer/create-developer-environment
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:9057c8ed2fea6884a0f42ba80ef10aebddd1406134116c1ee58d1ef4d5c78892

---

### 2. Copilot Studio Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ca06345b4ebf853c449de74c7c162432a987ad02ebb073379f445119560fba7f

---

### 3. Power Platform Licensing
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/pricing-billing-skus
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:823feb7a3f06b9c282e7749c54da5fdb21ff54c869fd288e843098dccc244a91

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*