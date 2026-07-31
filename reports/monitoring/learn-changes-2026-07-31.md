# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-31
**Run Time:** 2026-07-31T08:50:37.210757+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 2 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 2 | admin-share-bots | HIGH | 3.10, 3.2, 2.9, 2.6, 2.5 | Update portal-walkthrough |
| 3 | restricted-access-control | HIGH | 1.3, 4.1 | Review and update |
| 4 | data-access-governance-reports | HIGH | 1.14, 1.3, 4.4, 4.1, 4.5, 4.6, 4.2 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Share and Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:635e73046b5de485fafa893ae9c25a4460f36fb94c23e21586cd4750e9d58e4d

**Affected Controls:**
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)

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
@@ -40,7 +40,7 @@ is turned on, to manage who can chat with the agent in your organization.
 Share an agent for chat
 Web app
-Teams
+Teams app
 Collaborators
 with authoring permissions for a shared agent can always chat with it. However, you can also grant users permission to chat with an agent in Copilot Studio without granting them authoring permissions.
 To grant users permission to only chat with the agent, you can:
@@ -171,7 +171,7 @@ to share the agent with everyone in the organization.
 Share an agent for collaborative authoring
 Web app
-Teams
+Teams app
 When you share an agent with others for
 collaborative authoring,
 you give them permission to view, edit, configure, share, and publish the agent. They can't delete the agent. You can only share agents for collaborative authoring with individual users in your organization. These users can be in different Power Platform environments, as long as they belong to your organization.
@@ -307,6 +307,39 @@ The Bot Transcript Viewer security role is assigned at the environment level in the Power Platform admin center. Learn more about
 enabling this security role
 in your single or group environment.
+Share an agent's evaluations
+Use the
+Agent Viewer
+role in Copilot Studio to give evaluators access to an agent's evaluations without letting them change the agent.
+What is the agent viewer role?
+The agent viewer role is a sharing role that grants access to the
+Evaluation
+page for a specific agent. Users with this role can view and run evaluations without access to the agent itself.
+Why use this role?
+The agent viewer role lets agent owners include subject matter experts, quality reviewers, and other stakeholders in testing without giving them permission to the agent. Evaluators review agent performance and run repeatable tests, while agent owners keep control of the agent's content and confi
```

---

### 2. Data Access Governance Reports

**URL:** https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports
**Section:** SharePoint Administration
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:a2626ee740f209b318c8c563e37daa1f117527dafcbac0c55fdfd6c9671ba971

**Affected Controls:**
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.2/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

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
@@ -27,7 +27,7 @@ See
 Prerequisites for SharePoint Advanced Management
 .
-The reports are currently unavailable for Gallatin, even if you have the required licenses.
+The reports are currently unavailable for Microsoft 365 operated by 21Vianet, even if you have the required licenses.
 How to access the Data access governance reports in the SharePoint admin center
 Sign in to the
 SharePoint admin center
@@ -94,8 +94,15 @@ Learn how to create and use the
 site permissions for users report
 .
+What is the sites and files shared via special SharePoint groups report?
+The sites and files shared via special SharePoint groups report is a snapshot report that identifies all sites, folders, and files across SharePoint and OneDrive that are effectively public because of the special SharePoint groups 'Everyone except external users' (EEEU) or 'Everyone'. While the
+site permissions for your organization report
+tells you which sites are overshared, this report tells you exactly which items are overshared and how access was granted, so you can accelerate cleanup through scripting instead of depending on site owners.
+Learn how to run and use the
+sites and files shared via special SharePoint groups report
+.
 What is the sensitivity labels for files report?
-The sensitivity labels for files report is the other snapshot report that helps you control access to sensitive content across your organization. This report identifies sites containing
+The sensitivity labels for files report is another snapshot report that helps you control access to sensitive content across your organization. This report identifies sites containing
 files with sensitivity labels applied
 , allowing you to verify that appropriate security policies are applied.
 Learn how to use the

```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:306cbf09c2d7cf0e947c183eacad19e61fb81b50044a9f5d4aeb17adcf5911ea

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
@@ -548,6 +552,8 @@ By: Cireson
 Cisco Webex Meetings
 By: Cisco
+Cisco Workspaces
+By: Cisco Systems.
 Citymapper (Independent Publisher)
 By: Troy Taylor
 CivicPlus Transform
@@ -626,6 +632,8 @@ By: Roy Paar
 Commercient
 By: Commercient LLC
+CommunitycliQ Agent
+By: Mentorcliq, Inc.
 Companies House (Independent Publisher)
 By: Matt Collins
 Company Connect
@@ -665,7 +673,7 @@ ConvertKit (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 Copilot for Finance
-By: Microsoft
+By:
 Copilot for Sales
 By: Microsoft Corporation

```

---

### 2. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:2495d89069a2f47f78103a4f22e387fe2a1c76e91afca705368e5c9d58a1c327

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`

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
@@ -22,12 +22,15 @@ Restrict SharePoint site access with Microsoft 365 groups and Microsoft Entra security groups
 Feedback
 Summarize this article for me
-Restricted site access control helps prevent oversharing by designating access of SharePoint sites and its content to users in a specific group. Users not in the specified group can't access the site or its content, even if they had prior permissions or a shared link. You can apply this policy on Microsoft 365 group-connected, Teams-connected, and nongroup connected sites by using Microsoft 365 groups or Microsoft Entra security groups.
-Site access restriction policies take effect when a user attempts to open a site or access a file. Users with direct permissions to the file can still view files in search results. However, they can't access the files if they're not part of the specified group.
-Restricting site access through group membership can minimize the risk of oversharing content. For insights into data sharing, see
-Data access governance reports
-.
-What do you need to restrict site access?
+Restricted site access control (also referred to as
+restricted access control
+or
+site access restriction
+) helps prevent oversharing by designating access of SharePoint sites and its content to users in the specific control group. Users not in the specified group can't access the site or its content, even if they had prior permissions or a shared link. You can apply this policy on Microsoft 365 group-connected, Teams-connected, nongroup connected sites, and OneDrive by using Microsoft 365 groups or Microsoft Entra security groups.
+Site access restriction policy take effect when a user attempts to open a site or access a file. Copilot and organization wide search results also honor the policy. Users with direct permissions to the file but not in the specified control group will not be able to vi
```

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