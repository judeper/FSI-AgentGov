# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-06
**Run Time:** 2026-06-06T08:35:09.460880+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 3 |
| Redirects | 1 |
| Errors | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | HIGH | 2.4 | Update portal-walkthrough |
| 2 | endpoint-dlp-learn-about | HIGH | 1.17 | Review and update |
| 3 | whats-new | HIGH | None | Review and update |
| 4 | microsoft-purview-service-description | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -134,7 +134,7 @@ Perform disaster recovery drills or an emergency response before a real disaster strikes, so you can document all steps required for any integration points that are external to Power Platform. Your company is then more prepared for recovery if there's a real disaster.
 Frequently asked questions (FAQs)
 Why use self-service disaster recovery?
-Super storms, natural calamities, and unforeseen political uncertainties that have the potential to bring an entire region down are becoming more common. To minimize the impact of a disaster that brings an entire region down, maintain an asynchronous copy in a remote region. You might also want to maintain a copy in a remote region for compliance audits.
+Super storms, natural calamities, and unforeseen political uncertainties that can bring down an entire region are becoming more common. To minimize the impact of a disaster that brings down an entire region, maintain an asynchronous copy in a remote region. You might also want to maintain a copy in a remote region for compliance audits.
 Self-service disaster recovery gives you control to fail over to a secondary region with the push of a button and fail back with the push of a button when the primary region is restored to ensure business continuity. You can also simulate the primary region being down to run a real failover and fail back to the secondary region to test a real compliance drill. Run drills with a copy of the production environment to avoid any downtime.
 Why do I need self-service disaster recovery if I already have a secondary copy maintained in a remote, secondary region?
 For the public cloud, the system doesn't maintain secondary copies in a remote, secondary region unless you turn on self-service disaster recovery.
@@ -150,7 +150,7 @@ Capacity consumption is reflected in the familiar licensing experience within the Power Platform admin center. Learn more in
 View usage and billing information
 .
-For example, suppose a user has 
```

---

## HIGH: Control Review Recommended

### 1. Endpoint DLP

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -143,10 +143,27 @@ n/a
 Supported
 Not supported
-Scoping DLP policies (preview)
-In preview, DLP policies for endpoints are scoped by users, and devices. For an endpoint policy to be applied, both the user and the device must be in the policy scope. This means that if a user is in the policy scope, but the device isn't, the policy won't be applied. Similarly, if a device is in the policy scope, but the user isn't, the policy won't be applied.
-For more information on scoping endpoint DLP policies, see
+Scoping DLP policies for endpoints
+Microsoft Purview Data Loss Prevention (DLP) policies can be applied to multiple locations, including endpoint devices. When a DLP policy includes the
+Devices
+location, the policy can be scoped by both users and devices. For a DLP policy to be enforced on an endpoint, both the user and the device must be included in the policy scope.
+Device in scope
+User in scope
+Policy applied
+Yes
+Yes
+Yes
+No
+Yes
+No
+No
+Yes
+No
+This enables more precise data protection controls based on who is accesing data and from which device. For more information, see
 Device scoping
+.
+For implementation details see
+Create policy using device scoping
 .
 Other settings
 Setting

```

---

### 2. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -43,6 +43,15 @@ :
 Access Endpoint DLP device attribute data using Advanced Hunting
 . Query Endpoint DLP device configuration and policy sync attributes at scale through the DeviceInfo table's DlpInfo column in Advanced hunting in the Microsoft Defender portal, instead of relying on point-in-time exports from the Microsoft Purview portal.
+New
+:
+Create a DLP policy that uses device scoping
+. Scope an Endpoint DLP policy to specific device groups â for example, enforce policy only when Finance users access data from Windows devices, and not when the same users work from macOS â using dynamic device groups defined in Microsoft Entra ID.
+Device Onboarding
+New
+:
+Monitor device health with the device health reports dashboard
+. Use the device health reports dashboard to monitor device onboarding status, policy update readiness, and feature readiness for Endpoint DLP.
 May 2026
 Agent 365
 General availability (GA)

```

---

### 3. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -512,6 +512,7 @@ eDiscovery (Premium)
 provides an end-to-end workflow to preserve, collect, analyze, review, and export content that's responsive to your organization's internal and external investigations. It also lets legal teams manage the entire legal hold notification workflow to communicate with custodians involved in a case.
 In Microsoft Purview eDiscovery, a custodian refers to the individual whose content is subject to search, hold, or review as part of a legal, regulatory, or investigative process. A custodian is typically an employee or user whose data (e.g., email, documents, Teams messages) may be relevant to the matter under investigation. This is distinct from the IT administrators or compliance officers who perform searches or manage eDiscovery cases. Licensing requirements apply both to custodians (whose data is preserved or reviewed) and to users performing eDiscovery activities, as defined in the Microsoft Purview licensing terms.
+Compliance boundaries are an eDiscovery configuration capability for limiting which content locations and cases eDiscovery managers can access, and don't have separate licensing requirements beyond applicable eDiscovery licensing.
 Placing a shared mailbox on hold using Microsoft Purview eDiscovery (Standard or Premium) is subject to the same licensing requirements as placing a hold directly in Exchange Onlineâ
 Exchange Online Plan 2
 or

```

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