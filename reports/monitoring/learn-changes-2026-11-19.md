# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-19
**Run Time:** 2026-11-19T15:22:47.771394+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 1 |
| MEDIUM Changes | 2 |
| Redirects | 11 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | HIGH | 1.4 | Review and update |
| 2 | ...pilot-studio-copilot-credits-capacity | HIGH | 2.27 | Update portal-walkthrough |
| 3 | tutorial-acm-create-budgets | MEDIUM | 3.5 | Review optional |
| 4 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Copilot Studio Copilot Credits Capacity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-copilot-credits-capacity
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:7f251b158f4e9cb1cca7aa76999058ab75a3be2b18ab771f1ad204793f3db395

**Affected Controls:**
- Control 2.27: Control 2.27: Consumption-Entitlement Governance
  - File: `controls/pillar-2-management/2.27-consumption-entitlement-governance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.27/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -172,7 +172,7 @@ Agent flow actions
 feature in the
 Copilot credit consumption details
-grid. Agents powered by the GitHub Copilot harness can also be referred to as Process Agents in the Power Platform admin center licensing report. When the environment has no Copilot Credits available, new agent flow runs are blocked while the parent agent continues to function for non-flow interactions. Flow authors also see a design-time warning in the Copilot Studio designer. To resolve enforcement, reallocate capacity, purchase more credits, or
+grid. Agents powered by the Microsoft Copilot harness can also be referred to as Process Agents in the Power Platform admin center licensing report. When the environment has no Copilot Credits available, new agent flow runs are blocked while the parent agent continues to function for non-flow interactions. Flow authors also see a design-time warning in the Copilot Studio designer. To resolve enforcement, reallocate capacity, purchase more credits, or
 enable pay-as-you-go billing
 . For more information, see
 Agent flow enforcement
@@ -227,8 +227,15 @@ To learn which tokens are billed, see
 How tokens are counted for reasoning models
 .
+Programmatic access to usage reports (preview)
+[This article is prerelease documentation and is subject to change.]
+Administrators can use the Power Platform API to retrieve Copilot Studio usage data programmatically instead of manually downloading reports. Use this data in custom dashboards and reporting pipelines to monitor usage, support budgeting, and investigate usage trends.
+The API provides access to various reports with daily or summary results, with granularity for user, resource, environment, product, and feature.
+Report retrieval requires delegated administrator authentication and follows an asynchronous workflow: submit a request, poll for completion, and download the gzip-compressed file. For detailed steps, see
+Tutorial: Download Copilot Credit usage reports programmatica
```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:fe96ca42384f0f8b7b66846229f238d9b07c7e3876f77a457c69bb024dbb92e6

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -98,6 +98,8 @@ By: Acumatica
 Address Labs (Independent Publisher)
 By: Richard Wilson
+Adobe Acrobat Knowledge Base
+By: ADOBE INC.
 Adobe Acrobat Sign
 By: ADOBE INC.
 Adobe Acrobat Sign Sandbox
@@ -110,12 +112,16 @@ By: Adobe Acrobat Services
 ADP Employee Self-Service
 By: ADP, Inc.
+ADPÂ® MCP
+By: ADP, Inc.
 Advanced Data Operations
 By: State Solutions
 Advanced Scraper (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 Aexum
 By: Nodefusion d.o.o
+Affinity MCP
+By: Project Affinity, Inc.
 Affirmations (Independent Publisher)
 By: Troy Taylor
 Africa's Talking Airtime
@@ -140,6 +146,8 @@ By: ahead AG
 AI or Not (Independent Publisher)
 By: FÃ¶rdÅs AndrÃ¡s
+AI TeamsMaestro
+By: MailMaestro
 AIForged
 By: Larc AI (PTY) Ltd
 AIHW MyHospitals (Independent Publisher)
@@ -156,6 +164,8 @@ By: airSlate Inc.
 Airtable (Independent Publisher) [DEPRECATED]
 By: Woong Choi
+Akeyless Secrets Manager
+By: Akeyless
 Alemba ITSM
 By: Alemba Ltd
 Alert Relay
@@ -190,6 +200,18 @@ By: Troy Taylor, Hitachi Solutions
 AMEE Open Business (Independent Publisher)
 By: Paul Culmsee
+ancoreMate Apps
+By: ancoreSoft
+ancoreMate Automations
+By: ancoreSoft
+ancoreMate Catalog
+By: ancoreSoft
+ancoreMate Content
+By: ancoreSoft
+ancoreMate Reloads
+By: ancoreSoft
+ancoreMate Spaces and Access
+By: ancoreSoft
 Annature (Independent Publisher)
 By: Dr Adrian Colquhoun (Strategik)
 Ant Text Automation
@@ -200,10 +222,14 @@ By: ANYRUN FZCO
 Apache Impala [DEPRECATED]
 By: Microsoft
+Apify
+By: Apify
 APITemplate (Independent Publisher)
 By: Troy Taylor
 APlace.io (Independent Publisher)
 By: Troy Taylor
+Apollo
+By: ZenLeads Inc. dba Apollo.io
 App Power Forms
 By: App Power Solutions LLC
 App Store Connect - App Store (Independent Publisher)
@@ -232,6 +258,8 @@ By: Esri, Inc.
 ArcGIS PaaS
 By: Esri, Inc.
+Aria by Convosight
+By: Convosight
 AS2
 By: Microsoft
 Asana
@@ -258,6 +286,8 @@ By: H3 Solutions Inc.
 AtBot Logic
 By: H3 Solutions Inc.
+Audioscrape
+By: Audioscra
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Azure Budgets
**URL:** https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ffa7ccd513554dcf0fb033b7356cac5ca62d7418561479b3dce3cfd7236045d7

---

### 2. Copilot Studio Licensing (Get Access)
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:496116915a4146a3854f7a03c1ca227ecd4ed943582e6d62ae3a59e42c55d8b4

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