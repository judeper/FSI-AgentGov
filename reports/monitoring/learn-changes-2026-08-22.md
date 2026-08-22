# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-22
**Run Time:** 2026-08-22T06:40:48.897060+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 2 |
| MEDIUM Changes | 2 |
| Redirects | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 2 | fundamentals-what-is-copilot-studio | CRITICAL | 2.13 | Monitor |
| 3 | add-tools-custom-agent | HIGH | 2.17 | Review and update |
| 4 | whats-new | CRITICAL | None | Monitor |
| 5 | ...ecurity-compliance-licensing-guidance | HIGH | 1.21, 1.13, 1.19 | Update portal-walkthrough |
| 6 | microsoft-purview-service-description | HIGH | None | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. M365 Licensing Guidance

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-365-security-compliance-licensing-guidance
**Section:** Licensing
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:6c63b1da0e9a4e2ba0b2d80c7179120abc91bc5535f625236fa320b156f2cfc0

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.21/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/1.19/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/1.13/portal-walkthrough.md` (CRITICAL)

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
@@ -88,7 +88,7 @@ Microsoft Purview Data Loss Prevention (DLP) for Teams
 Microsoft Purview Data Loss Prevention: Data Loss Prevention (DLP) for Exchange Online, SharePoint Online, and OneDrive for Business
 Microsoft Purview Data Loss Prevention Graph APIs for Teams Data Loss Prevention (DLP) and for Teams Export
-Microsoft Purview Data Loss Prevention (DLP) for Microsoft 365 Copilot
+Microsoft Purview Data Loss Prevention (DLP) for Microsoft Copilot
 Microsoft Purview eDiscovery
 Microsoft Purview Information Barriers
 Microsoft Purview Information Protection

```

---

### 2. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:690426464ccdc804db7da58ed7e0f3c96c84cdcca51cbc49f777ae1b5205efe2

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)

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
@@ -64,16 +64,16 @@ Yes
 Yes
 Yes
-Audit (Standard) for Microsoft 365 Copilot interactions
+Audit (Standard) for Microsoft Copilot interactions
 1
 Yes
 Yes
 Yes
 1
-Audit logs for Microsoft 365 Copilot interactions are generated only when Microsoft 365 Copilot is licensed and in use.
+Audit logs for Microsoft Copilot interactions are generated only when Microsoft Copilot is licensed and in use.
 Microsoft Purview Audit (Premium)
-Audit (Premium) (formerly named Microsoft 365 Advanced Audit) provides one-year retention of audit logs for user and admin activities and provides the ability to create custom audit log retention policies to manage audit log retention for other Microsoft 365 services. It also provides access to crucial events for investigations and high-bandwidth access to the Office 365 Management Activity API.
-Users benefit from Audit (Premium) because audit records related to user activity in Microsoft 365 services can be retained for up to one year. Additionally, high-value auditing events are logged, such as when items in a user's mailbox are accessed or read.
+Audit (Premium) (formerly named Microsoft 365 Advanced Audit) provides up to one-year retention of audit logs for user and admin activities and provides the ability to create custom audit log retention policies to manage audit log retention for other Microsoft 365 services. It also provides access to crucial events for investigations and high-bandwidth access to the Office 365 Management Activity API.
+Users benefit from Audit (Premium) because audit records related to user activity in Microsoft 365 services can be retained for up to one year. Additionally, intelligent insights for certain auditing events are logged, such as the sensitivity label for items accessed in a user's mailbox.
 By default, Audit (Premium) is enabled at the tenant level for all users that benefit from 
```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:b5b8195be86661ee36e6c86c4eb0e8aea9ef08da3eadccc75b8a75f4eb297de2

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

### 2. Agent Orchestration

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c0925eb7c0b0617065da6a8897eb8562acb3fe2790d9f9b5bb69950789cf1f83

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

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
@@ -22,6 +22,14 @@ Add tools to custom agents
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 Tools are building blocks that let your agent interact with external systems. Tools expand what your agent can do, letting your agent perform various actions in response to user requests or autonomous triggers. Each tool represents a specific capability that your agent can perform. For example, you can equip your agent with tools that perform tasks like:
 Send emails using the Office 365 Outlook connector
 Check the current weather conditions and forecasts
@@ -54,12 +62,15 @@ : Connect to an MCP server to access tools and resources.
 Computer use
 : Lets your agent interact with any system that has a graphical user interface, for websites and desktop apps, selecting buttons, choosing menus, and entering text into fields on the screen.
-There are two other mechanisms you can use to add tool-like behavior to your agent:
-Skills: Container for a set of related tools.
-Client tool: Send an event activity to the client so that the client carries out an action and returns a response.
-For more information on skills and client tools, see the links in the
-Related content
-section.
+Two other mechanisms you can use to add
+tool-like
+behavior to your agent are:
+Azure Bot Service skills
+: Container for a set of related tools made available through the Azure Bot Service.
+Client tools
+: Send an event activity to the client so that the client carries out an action and returns a response.
+Note
+Skills in the context of the agents powered by the standard harness aren't the same as the skills used in coding agents. You c
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Copilot Studio Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:a88cf63af4f9e734717764570e6c0832e8f53f19d6d5e4b389aa31c7b1383286

---

### 2. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:2f8411569ff5a020b4e999b72a70e18ede2637ee272a1f516b449d8234170bc1

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity | https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-copilot-credits-capacity |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*