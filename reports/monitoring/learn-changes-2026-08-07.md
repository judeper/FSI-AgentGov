# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-07
**Run Time:** 2026-08-07T07:17:12.109886+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 3 |
| MEDIUM Changes | 1 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | create-developer-environment | HIGH | 2.15 | Review and update |
| 2 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 3 | power-platform-inventory | CRITICAL | 3.11 | Monitor |
| 4 | what-is-microsoft-entra-agent-id | HIGH | 1.18, 1.11 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Developer Environments

**URL:** https://learn.microsoft.com/en-us/power-platform/developer/create-developer-environment
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:1ea18875466ac59b5d118539da5ee6b3653b7b0da77a7e6763412e088a805b60

**Affected Controls:**
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -22,28 +22,29 @@ Create a developer environment with the Power Apps Developer Plan
 Feedback
 Summarize this article for me
-To fully use the
+To get the most out of the
 Power Apps Developer Plan
-as a developer, you need an Azure account and a work account. This article guides you through the process for creating a Power Platform environment and a test tenant if needed.
-Where do I start?
+as a developer, you need an Azure account and a work account. This article guides you through the process of creating a Power Platform environment and a test tenant if needed.
+Choose an account for your developer environment
 If you have a
 work account
-, and want to use it to learn Power Platform, go to the
+and want to use it to learn Power Platform, go to the
 next section
 .
-If you don't have a work account or prefer a Sandbox tenant to learn Power Platform, read information in the
+If you don't have a work account or prefer a Sandbox tenant to learn Power Platform, read the information in the
 create a test tenant
 section later in this article before signing up for the developer environment.
 Sign up for the Power Apps Developer Plan
-The Power Apps Developer Plan gives you a free development environment to build and test with Power Apps, Power Automate, and Microsoft Dataverse.
+The Power Apps Developer Plan provides a free development environment where you can build and test apps by using Power Apps, Power Automate, and Microsoft Dataverse.
 It's simple to sign up for the Power Apps Developer Plan:
+To sign up for the Power Apps Developer Plan, follow these steps:
 Ensure that you have a work account. If you don't,
 create a test tenant
 first.
 Sign up on the
 Power Apps Developer Plan website
 .
-After signing up for the Developer Plan, you'll be redirected to
+After you sign up for the Developer Plan, you're redirected to
 Power Apps
 . The envi
```

---

### 2. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:c1e63a2f0d7e58fd6d88c989f1c033de59d9f4b18a098cf88d5fdc3627a43de3

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -126,6 +126,8 @@ By: Africa's Talking
 AfterShip (Independent Publisher)
 By: Taiki Yoshida
+Agent SDK
+By: Microsoft
 AgilePoint NX
 By: AgilePoint Inc
 Agilite
@@ -177,11 +179,11 @@ Amazon Redshift [DEPRECATED]
 By: Microsoft
 Amazon S3
-By: Microsoft
+By:
 Amazon S3 Bucket (Independent Publisher)
 By: Michael Megel
 Amazon SQS
-By: Microsoft
+By:
 Ambee (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 AMEE Open Business (Independent Publisher)
@@ -270,8 +272,6 @@ By: Microsoft
 Azure - Foundry IQ
 By: Microsoft
-Azure AD Identity and Access
-By: Microsoft, Daniel Laskewitz
 Azure AI Content Understanding
 By: Microsoft
 Azure AI Document Intelligence (form recognizer)
@@ -283,7 +283,7 @@ Azure AI Search
 By: Microsoft
 Azure App Service
-By: Microsoft
+By:
 Azure Application Insights [DEPRECATED]
 By: Microsoft
 Azure Automation
@@ -340,8 +340,12 @@ By: Microsoft
 Azure Log Analytics Data Collector
 By: Microsoft
+Azure Maps
+By: Microsoft
 Azure Monitor Logs
 By: Microsoft
+Azure Monitor Logs Ingestion
+By: Microsoft
 Azure OpenAI
 By: Microsoft
 Azure Queues
@@ -357,7 +361,7 @@ Azure Text to speech
 By: Microsoft
 Azure VM
-By: Microsoft
+By:
 Badgr (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 Basecamp 2
@@ -480,6 +484,8 @@ By: Skyscape
 Byword (Independent Publisher)
 By: Troy Taylor
+C TWO
+By: C TWO
 Calculate Working Day
 By: Tweed Technology Ltd
 Calendar Pro
@@ -548,6 +554,8 @@ By: Cireson
 Cisco Webex Meetings
 By: Cisco
+Cisco Workspaces
+By: Cisco Systems.
 Citymapper (Independent Publisher)
 By: Troy Taylor
 CivicPlus Transform
@@ -626,6 +634,8 @@ By: Roy Paar
 Commercient
 By: Commercient LLC
+CommunitycliQ Agent
+By: Mentorcliq, Inc.
 Companies House (Independent Publisher)
 By: Matt Collins

```

---

### 3. Agent Identities for AI Agents

**URL:** https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:377ae975ee093c21b90549c12a060e591db8c7728a9bb3b10668177445bd8b9d

**Affected Controls:**
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -50,24 +50,8 @@ license for each user. For pricing details, see
 Microsoft Agent 365 plans and pricing
 .
-Extending Microsoft Entra security features to agents requires
-Microsoft 365 E7
-(includes Agent 365 and Microsoft Entra Suite) or
-Microsoft 365 E5
-paired with a
-Microsoft Agent 365
-license. Customers without E5 or E7 can use the following standalone licensing options with a
-Microsoft Agent 365
-license:
-Conditional Access for agents
-: Microsoft Entra ID P1
-ID Protection for agents
-: Microsoft Entra ID P2
-ID Governance for agents
-: Microsoft Entra ID P1
-Network controls for agents
-: Microsoft Entra Internet Access, included in Microsoft Entra Suite or licensed separately. For more information, see
-What is Global Secure Access
+Extending Microsoft Entra security features to agents requires Microsoft Agent 365. Agent 365 is included with Microsoft 365 E7 and is available as an add-on to Microsoft E5/A5/Business Premium (or Microsoft Defender Suite + Microsoft Purview Suite). See our latest
+Agent 365 product terms for more details
 .
 Related content
 Microsoft Entra security for AI overview

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Power Platform Inventory
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:4b90544b7dbcc6703f099b132e2e78fa21c1228af80396e19e981b178a002ce3

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*