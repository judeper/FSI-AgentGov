# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-15
**Run Time:** 2026-10-15T10:59:22.339593+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 3 |
| HIGH Changes | 1 |
| MEDIUM Changes | 7 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | security-and-governance | MEDIUM | 1.8, 1.3, 1.1, 1.5, 1.4, 1.28, 2.8 | Update portal-walkthrough |
| 2 | ...ication-fundamentals-publish-channels | MEDIUM | 1.28 | Review optional |
| 3 | analytics-improve-agent-effectiveness | HIGH | None | Update portal-walkthrough |
| 4 | add-tools-custom-agent | MEDIUM | 2.17 | Review optional |
| 5 | plan-agent-model-lifecycle | MEDIUM | 2.6 | Update portal-walkthrough |
| 6 | microsoft-365-copilot-overview | HIGH | 3.8 | Review and update |
| 7 | dlp-policy-reference | MEDIUM | 1.5 | Review optional |
| 8 | endpoint-dlp-learn-about | MEDIUM | 1.17 | Review optional |
| 9 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f6bab0694e901c73590a376465b1c5625867190e11486451f20b84a8f5a85ec1

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
--- +++ @@ -41,7 +41,7 @@ Admins can use data policies in the Power Platform admin center to govern the use and availability of Copilot Studio features and agent capabilities, including:
 Maker and user authentication
 Knowledge sources
-Actions, connectors, and skills
+Actions, connectors, and Azure Bot Service skills
 HTTP requests
 Publication to channels
 Azure Monitor Application Insights

```

---

### 2. Monitor Conversational Agents (Effectiveness)

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:0449304025871c8085a87bfd4f22ac1e5493bfeee1ab8efd718e5457b2f4356f

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -44,13 +44,7 @@ Overview
 , and
 Savings
-section shows key insights about your agents along with billing and cost savings statistics; see
-Summary
-,
-Overview
-, and
-Savings
-to learn more about each subsections.
+section shows key insights about your agents along with billing and cost savings statistics.
 The
 Custom metrics
 section lets you define business-specific metrics for your agents use cases.
@@ -68,7 +62,7 @@ For users with the Bot Transcript Viewer privilege, you can
 drill down to a list of customer sessions
 filtered based on the selected segment of the donut graph. From the session list you can see the reasoning behind the metric and access the underlying the transcript by selecting individual sessions.
-To learn how to create, test, and refine custom metrics, see
+Learn how to create, test, and refine custom metrics in
 Monitor your agent with custom metrics
 .
 Effectiveness
@@ -85,9 +79,9 @@ (preview): An AI-based sentiment analysis for the entire session.
 Agents
 : See call volume metrics, success rates, and current status for child and connected agents.
-Feedback data is stored in the conversation transcript table in Dataverse. For a list of channels that support this feature, see
-Feature details
-.
+Feedback data is stored in the
+conversation transcript table
+in Dataverse.
 Conversation outcomes
 The
 Conversation outcomes
@@ -101,7 +95,7 @@ , and
 Unengaged
 are represented by their respective colors for each data point. The y-axis indicates the number of sessions.
-To see metrics about individual outcomes specific to one data point (a specific day), hover over an area representing the color of an outcome of interest (for example, teal for Abandoned) on the day you're interested in.
+To view metrics about individual outcomes specific to one data point (a specific day), hover over an area representing the color of an outcome of interest (for example, teal for Abandoned) on the day you're interested in.
 To download conversation
```

---

### 3. Manage the AI model lifecycle for Copilot Studio agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c7d3b6c0029327e8129668273daee2333c6be5ccd415fdd5084171bbfac96d4f

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.6/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.6/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -117,7 +117,7 @@ and
 Power Platform admin notifications
 Tenant-targeted change and retirement announcements.
-Copilot Studio release plans
+Roadmap
 and
 What's new in Copilot Studio
 The forward-looking model and capability roadmap.

```

---

## HIGH: Control Review Recommended

### 1. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:73b8939986539425db3a78502b349498e45a744a3a9e1d0783159bdb22931943

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -49,9 +49,19 @@ Copilot Chat (Basic) license
 Microsoft 365 Copilot (Basic) license
 Microsoft 365 Copilot (Premium) license
+Usage-based billing capabilities
 Securely interact with Copilot Chat using web data only
 Securely interact with Copilot Chat using web data only
 Securely interact with Copilot using web data and work data (
+Microsoft Graph
+and
+Work IQ
+)
+Securely interact with Copilot,
+Copilot Cowork
+and
+Copilot Code
+using web and work data (
 Microsoft Graph
 and
 Work IQ
@@ -77,8 +87,17 @@ the Microsoft 365 Copilot add-on license with
 priority access
 to the full experience of Copilot in Word, Excel, PowerPoint, and OneNote.
-You have access to
-Microsoft Copilot Cowork
+For more information, see
+Microsoft 365 Copilot (Premium) license and experience
+.
+You
+have
+the Microsoft 365 Copilot add-on license with
+priority access
+to the full experience of Copilot in Word, Excel, PowerPoint, and OneNote, and access to
+Copilot Cowork
+and
+Copilot Code
 via
 usage-based billing
 .
@@ -94,9 +113,15 @@ and
 Work IQ
 ).
+Includes access to Cowork, Code, and agents that use web and work data (
+Microsoft Graph
+and
+Work IQ
+). Usage is billed based on consumption.
 Basic usage management controls and reporting for admins.
 Basic usage management controls and reporting for admins.
 Added advanced management controls and analytics for admins.
+Added usage monitoring, reporting, and cost management controls for admins.
 Note
 In-product labels are displayed in Microsoft 365 apps like Word, Excel, PowerPoint, and OneNote, and in the Microsoft Copilot app, to help users identify their Copilot experience.
 Copilot features in Microsoft 365 apps
@@ -117,6 +142,7 @@ Microsoft Copilot Chat (Basic) license and experience
 Microsoft 365 Copilot (Basic) license and experience
 Microsoft 365 Copilot (Premium) license and experience
+Usage-based billing capabilities
 Copilot Chat (Basic)
 is the standalone baseline experience included with eligible Micr
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Security and Governance
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f6bab0694e901c73590a376465b1c5625867190e11486451f20b84a8f5a85ec1

---

### 2. Agent Publishing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6bc6b7cf00c92be6d6c7d1df7e3620d07ffcdf2c9c088b81b59238cdc4515187

---

### 3. Add Tools to Agents
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:735ca689c2f02a6e8f99e7d1494a138284c9f3797979dcb3fb65afc2436cfe92

---

### 4. Manage the AI model lifecycle for Copilot Studio agents
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c7d3b6c0029327e8129668273daee2333c6be5ccd415fdd5084171bbfac96d4f

---

### 5. DLP Policy Reference
**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:cc8aa55f25fa6d4b7e38db957339ab4f0b39a6a24eaef902115beddca89ed599

---

### 6. Endpoint DLP
**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:06b5c1e8959d41433ce59008dea1df9c57ef681939d40a0adfc13cdf369aa2e7

---

### 7. Copilot Studio Licensing (Get Access)
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:066a2ec2a8cc13d8055d601594a3be43660db0121b59849d790cc0cf17360bab

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*