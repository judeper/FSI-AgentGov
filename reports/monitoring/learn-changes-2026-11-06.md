# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-06
**Run Time:** 2026-11-06T13:52:04.974313+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 3 |
| HIGH Changes | 4 |
| MEDIUM Changes | 2 |
| Redirects | 10 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | monitor-copilot-studio | HIGH | 3.2 | Review and update |
| 2 | monitoring-overview | HIGH | None | Review and update |
| 3 | alerts | MEDIUM | None | Review optional |
| 4 | security-and-governance | HIGH | 2.8, 1.4, 1.5, 1.28, 1.1, 1.3, 1.8 | Update portal-walkthrough |
| 5 | sensitivity-label-copilot-studio | CRITICAL | 1.26 | Update portal-walkthrough |
| 6 | copilot-overview | HIGH | 3.8 | Review and update |
| 7 | create-retention-policies | CRITICAL | 1.9, 4.3 | Review and update |
| 8 | overview | MEDIUM | 1.27, 1.8 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:b42e9812626598fa044ab029f1891708daaceccb57c7f703a724e753a3257553

**Affected Controls:**
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -59,16 +59,13 @@ Application lifecycle management (ALM) guidance
 Makers audit logs in Microsoft Purview for admins
 Admins have full visibility into maker audit logs in Microsoft Purview. Agent 365 complements this with centralized agent inventory and lifecycle context that can be correlated with audit records.
-View audit logs
+Use Microsoft Purview to manage data security and compliance for Microsoft Copilot Studio
 Audit logs in Microsoft Sentinel for admins
 Admins can monitor and receive alerts on agent activities through Microsoft Sentinel. Agent 365 complements Sentinel monitoring with unified agent governance telemetry and ownership context.
-View audit logs
+Relate Alerts to Incidents in Microsoft Sentinel in the Azure Portal
 Run tools with user credentials
 Agent makers can configure tools to use the user's credentials by default.
 Use tools with custom agents
-Sensitivity label for Knowledge with SharePoint
-Agent makers and users can see the highest sensitivity label applied to sources used in the agent's response and individual reference labels in the chat.
-View sensitivity labels for SharePoint data sources
 User authentication with certificates
 Admins and makers can configure agents to use Entra ID manual authentication with certificate provider.
 Configure user authentication
@@ -142,7 +139,7 @@ Microsoft Agent 365
 âa separate governance control plane for Copilot Studio agents that provides identity management and centralized observability. These events aren't covered by the configured Lockbox.
 Learn more in
-View audit logs
+Configure data policies for agents
 .
 Feedback
 Was this page helpful?

```

---

### 2. Sensitivity Labels in Copilot Studio

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:c9e0a4a1fefd93649445739889b5204be59735eb70b193a140bac45cf29b11be

**Affected Controls:**
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.26/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.26/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.26/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -19,55 +19,409 @@ Access to this page requires authorization. You can try
 changing directories
 .
-View sensitivity labels in agent responses (preview)
+Configure data policies for agents
 Feedback
 Summarize this article for me
-[This article is prerelease documentation and is subject to change.]
-Your organization's makers work with people inside and outside the organization. This means your data can go anywhere, on any device, app, or service. You want to keep your data secure and compliant with your organization's policies.
-With Microsoft Purview, you can use sensitivity labels to classify and protect your data, without affecting user productivity and collaboration. Specific to your organization and business needs, your admins can create categories for different levels of sensitive content in your organization.
-For example, you can create and apply labels for Personal, Public, General, Confidential, and Highly Confidential content. For more information, see
-Learn about sensitivity labels
-in the Purview documentation.
-In the standard harness, Copilot Studio supports sensitivity labels for the following
-knowledge sources
-and
-sources used in the generative answers classic mode
-:
-SharePoint
-OneDrive for Business
-SQL
-Dataverse
-Cosmos
-Azure Blob Storage
-Word
-Excel
-Outlook
-Office groups
-Office users
 Important
-This article contains Microsoft Copilot Studio preview documentation and is subject to change.
-Preview features aren't meant for production use and may have restricted functionality. These features are available before an official release so that you can get early access and
-provide feedback
-.
-If you're building a production-ready agent, see
-Microsoft Copilot Studio Overview
-.
-Microsoft Purview strengthens information protection for Copilot Studio
-An agent uses existing controls to ensure that data stored in your tenant is never returned to the user, or used by generative AI, if the user doesn't normally have access to tha
```

---

### 3. AI Content Safety

**URL:** https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
**Section:** Azure Services
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:575287d3d92cfd313994b303330a897efda968db8cc09d5ddf28df209555bf73

**Affected Controls:**
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -39,10 +39,25 @@ Groundedness detection in Azure AI Content Safety and Azure OpenAI
 .
 See the linked feature pages for migration guidance and recommended alternatives.
-Azure AI Content Safety is an AI service that detects harmful user-generated and AI-generated content in applications and services. Azure AI Content Safety includes text and image APIs that allow you to detect material that's harmful. The interactive Content Safety Studio allows you to view, explore, and try out sample code for detecting harmful content across different modalities.
-Content filtering software can help your app comply with regulations or maintain the intended environment for your users.
+Microsoft provides safety and security guardrails for core models and agents, powered by Azure AI Content Safety. This AI service detects harmful user- and AI-generated content in models, agents, and services. Guardrails are made up of controls that specify the risk to detect, where to scan for it, and how the model or agent should respond when it is found.
+Choose how to build with Azure AI Content Safety
+You can access guardrails in Microsoft Foundry for both Foundry Models sold by Azure and Foundry Models from partners and community, or as a standalone offering through Azure AI Content Safety Studio and APIs. The same AI service supports each access point, the difference is how and where you choose to use it.
+Use guardrails in Microsoft Foundry when
+Your models and agents are hosted in Foundry.
+You want to use built-in services during model and agent calls.
+You want free moderation on the first 1000 text characters.
+See
+details
+on how to use guardrails in Microsoft Foundry.
+Use guardrails in Azure AI Content Safety Studio and APIs when
+Your models and agents are outside Foundry - or span multiple platforms - and you want a consistent guardrail experience.
+You want guardrails beyond model and agent calls.
+You want moderation on all characters, following Azure AI Content Safe
```

---

## HIGH: Control Review Recommended

### 1. Monitor Microsoft Copilot Studio

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitor-copilot-studio
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:9dfa8736dd5cb1bdab0ccb6dfad7b1ffa571ceeafb673e0ba9c3a2bf74e7f375

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`

**What Changed:**
```diff
--- +++ @@ -49,11 +49,11 @@ Agents
 Agent session success rate
 A percentage that describes how often an autonomous agent is able to successfully execute its task, or how often a conversational agent's session was successfully resolved.
-Preview
+Generally available
 Agents
 Recent agent sessions
 The number of distinct user sessions in an agent in one day. A session begins when a user opens the agent and ends after a period of inactivity or when the agent is closed.
-Preview
+Generally available
 Feedback
 Was this page helpful?
 Yes

```

---

### 2. Monitoring Hub

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitoring-overview
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:a68cbfdde20b7ba091c2000eb4c6060c0ef6f3d94342baf4e8d90426dcdd1ad1

**What Changed:**
```diff
--- +++ @@ -112,6 +112,10 @@ Model-driven apps
 Generally available
 Generally available
+Power Apps
+Code apps
+Generally available
+Generally available
 Power Automate
 Cloud flows
 Generally available
@@ -126,7 +130,7 @@ for a similar experience.
 Power Automate
 Work queue
-Public preview
+Not yet available
 Not available. Use the
 Automation center
 for a similar experience.
@@ -136,7 +140,7 @@ Not yet available
 Copilot Studio
 Copilot Studio agents
-Public preview
+Generally available
 Use the
 Analytics tab
 for a similar experience.

```

---

### 3. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:ef583d4679b6b2037ec5bde2acbf406d1c8c90252af9f95389bb294e1b8d2ff3

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -40,12 +40,22 @@ )
 Access scoped by user permissions (security and compliance enforced)
 Note
+The
+Home
+tab provides a unified starting point for Chat and Cowork in the Copilot app. Users can switch between Chat and Cowork from either the
+left navigation or the prompt box
+. Cowork and Code require a
+Microsoft 365 Copilot license
+and an
+assigned usage-based billing policy
+.
+Compare Microsoft 365 Copilot licenses
+Note
 Anthropic subprocessors are available only in applicable Microsoft 365 licensed experiences and aren't available to all users by default. Anthropic operates with
 Microsoft Enterprise data protections
 . For more information, see
 Claude models from Anthropic in Microsoft Online Services
 .
-Compare Microsoft 365 Copilot licenses
 Copilot Chat (Basic) license
 Microsoft 365 Copilot (Basic) license
 Microsoft 365 Copilot (Premium) license

```

---

### 4. Retention Policies

**URL:** https://learn.microsoft.com/en-us/purview/create-retention-policies
**Section:** Microsoft Purview
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:407b23ae04c30a641f2e3aefcdddcb47f2179a57566d4f8e7624388909e8eba4

**Affected Controls:**
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.9/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -413,9 +413,15 @@ Separate an existing 'Teams chats and Copilot interactions' policy
 Previously, retention policies used the location
 Teams chats and Copilot interactions
-that combined Teams chat and Copilot interactions. There are now separate retention locations for Teams chat and Copilot interactions.
-You can separate Teams chats from Copilot interactions from an existing retention policy.
-You can create new retention policies for just Teams chats, or for just Copilot interactions.
+that combined Teams chat and Copilot interactions. Beginning 15th January, 2027, Microsoft Purview will treat 'Teams chats and Copilot interactions" policy as
+Teams-only policies
+. After this change is applied to your organization:
+Microsoft 365 Copilot interactions will no longer be retained or deleted through these legacy Teams policies.
+This change applies to both previously retained Copilot interactions and new Copilot interactions.
+Retention behavior for Microsoft Teams content will remain unchanged.
+Create a new retention policy explicitly configured for Copilot by selecting
+"Microsoft Copilot Experiences"
+location to maintain the required retention coverage for Copilot interactions.
 Use the following PowerShell commands to separate an existing retention policy for
 Teams chats and Copilot interactions
 :
@@ -431,15 +437,11 @@ newer locations
 , such as Teams private channel messages and Viva Engage:
 Set-AppRetentionCompliancePolicy -Identity â<policy name>â -Applications "User:M365Copilot"
-For new retention policies, select the new locations, such as
-Teams chat
-or
-Microsoft Copilot Experiences
-.
-Note
-If you have existing retention policies for
-Teams chats and Copilot interactions
-, they continue to be supported, although they can't be edited when your tenant supports the separate locations. At this point, any new retention policies must use the new locations.
+Please note that doing a Get command on 'Teams chats and Copilot interactions' p
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Monitor Alerts
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a4f39133e88f5cd5d34b5469de2c2fe398270f694f6eff57fb256ba84698da22

---

### 2. AI Content Safety
**URL:** https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:575287d3d92cfd313994b303330a897efda968db8cc09d5ddf28df209555bf73

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio | https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview | https://learn.microsoft.com/en-us/copilot/plan/copilot-overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy | https://learn.microsoft.com/en-us/copilot/plan/microsoft-365-copilot-privacy |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/enable-users | https://learn.microsoft.com/en-us/copilot/adopt/enable-users |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-overview | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-security-governance | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-security-governance |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-management | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-management |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/security/operations/incident-response-planning | https://learn.microsoft.com/en-us/security/zero-trust/security-operations-incident-response-readiness |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*