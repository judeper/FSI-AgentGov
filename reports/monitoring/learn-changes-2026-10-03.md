# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-03
**Run Time:** 2026-10-03T11:14:43.844022+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 1 |
| MEDIUM Changes | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 2 | ...pilot-studio-copilot-credits-capacity | HIGH | 2.27 | Update portal-walkthrough |
| 3 | custom-overview | MEDIUM | None | Review optional |
| 4 | whats-new | CRITICAL | None | Monitor |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Copilot Studio Copilot Credits Capacity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-copilot-credits-capacity
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:cd6642cb23ce59010f8858a30cadd6e3d2f92acbd750ac6376d0e50e2e5bf5fc

**Affected Controls:**
- Control 2.27: Control 2.27: Consumption-Entitlement Governance
  - File: `controls/pillar-2-management/2.27-consumption-entitlement-governance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.27/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -127,6 +127,16 @@ : This tile provides a product-focused summary of Copilot Credits consumed, showing the number of units deducted from prepaid capacity packs and/or pay-as-you-go units.
 Copilot Credit consumption details
 : The grid displays a list of Copilot agents consuming capacity, including the associated product, feature name, and the count of billed versus nonbillable credits.
+Note
+Copilot credits used to build
+Apps in Copilot Studio (preview)
+are temporarily grouped in the
+Top Agents by credit usage
+section. Under
+View all agents
+, credits used to build apps are categorized as App under
+Billable features
+.
 Tip
 To monitor credit consumption for agent flows, look for the
 Agent flow actions

```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:1b11b79a8ab9bf685f84c088d1a3a0c40b7e172277a40f8068315e53a993e919

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -157,7 +157,7 @@ Alemba ITSM
 By: Alemba Ltd
 Alert Relay
-By: independNET Products
+By: independNET Software
 Aletheia
 By: Aletheia
 AlisQI
@@ -424,6 +424,8 @@ By: Blackbaud, Inc.
 Blackbaud FENXT Query
 By: Blackbaud. Inc
+Blackbaud Merchant Services
+By: Blackbaud, Inc.
 Blackbaud Raisers Edge NXT
 By: Blackbaud, Inc.
 Blackbaud Raisers Edge NXT Constituents
@@ -442,9 +444,13 @@ By: Blackbaud, Inc.
 Blackbaud RENXT Gifts
 By: Blackbaud, Inc.
+Blackbaud RENXT Import
+By: Blackbaud, Inc.
 Blackbaud RENXT Query
 By: Blackbaud. Inc
 Blackbaud RENXT Reports
+By: Blackbaud, Inc.
+Blackbaud RENXT Volunteer
 By: Blackbaud, Inc.
 Blackbaud SKY Add-ins
 By: Blackbaud. Inc
@@ -544,6 +550,8 @@ By: Certinal Inc.
 Certopus
 By: DevSquirrel Technologies Private Limited
+Certyneo
+By: Certyneo
 CGTrader
 By: Microsoft
 Chainpoint [DEPRECATED]
@@ -586,8 +594,6 @@ By: C-RISE Ltd.
 Cloud Connect Studio
 By: Fuji Xerox
-Cloud PKI Management
-By: 509 Solutions Pty Ltd
 CloudConvert
 By: Lunaweb GmbH
 Cloudmersive Barcode
@@ -644,8 +650,6 @@ By: Mentorcliq, Inc.
 Companies House (Independent Publisher)
 By: Matt Collins
-Company Connect
-By: InSpark
 Composer by Tachytelic
 By: Accendo Solutions Ltd
 Computer Vision API
@@ -992,8 +996,6 @@ By: E-goi
 Eigen Events
 By: Eigen Ltd
-Elastic Forms
-By: Workai
 ElasticOCR [DEPRECATED]
 By: ElasticOCR
 Elead Product Reference Data
@@ -1048,8 +1050,6 @@ By: dotdigital
 Enlyft Insights
 By: Enlyft.
-Enlyft MCP
-By: Enlyft.
 Entegrations.io
 By: entegrations.io inc
 Entersoft
@@ -1298,8 +1298,6 @@ By: Clark County Tech
 Groopit
 By: Groopit
-GroupMgr
-By: GroupMgr
 GSA Analytics (Independent Publisher)
 By: Richard Wilson
 GSA Per Diem (Independent Publisher)
@@ -1670,6 +1668,8 @@ By: Microsoft
 LinkedIn V2
 By: Microsoft
+Linkly
+By: Linkly
 Lit Ipsum (Independent Publisher)
 By: Troy Taylor
 Litera Search
@@ -1692,8 +1692,6 @@ By: Troy Taylor, Hitachi Solutions
 LSEG

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Role-Based Access Control
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/custom-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8280743e5dff517d01db5ebda31b88a4aaff1d24b2d826b6e6b28860a2ac9e67

---

### 2. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:1db45be1071a81dc731d0c8833fa1c09999bca4c1a80aa90da594bb8f72870ef

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*