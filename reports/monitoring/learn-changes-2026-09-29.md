# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-29
**Run Time:** 2026-09-29T12:18:48.860214+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 3 |
| MEDIUM Changes | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | environment-groups-rules | HIGH | 2.2 | Update portal-walkthrough |
| 2 | power-platform-inventory | HIGH | 3.11 | Review and update |
| 3 | welcome-content | MEDIUM | None | Review optional |
| 4 | add-tools-custom-agent | HIGH | 2.17 | Review and update |
| 5 | microsoft-365-copilot-overview | MEDIUM | 3.8 | Review optional |
| 6 | application | HIGH | 1.2 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Environment Group Rules

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c391a85e686eb6fff6c7aaf01be3f95bd31cb3942f5fe9edb8b9454bb680995e

**Affected Controls:**
- Control 2.2: Control 2.2: Environment Groups and Tier Classification
  - File: `controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.2/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.2/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -50,32 +50,34 @@ 10
 External models
 11
+Maker guidelines (preview)
+12
 Maker welcome content
-12
+13
 Power Apps component framework for canvas apps
-13
+14
 Preview and experimental AI models
-14
+15
 Release channel
-15
+16
 Sharing agents with Editor permissions
-16
+17
 Sharing agents with Viewer permissions
-17
+18
 Sharing controls for canvas apps
-18
+19
 Sharing controls for solution-aware cloud flows
-19
+20
 Sharing data between Copilot Studio and Viva Insights
-20
+21
 Solution checker enforcement
-21
+22
 Unmanaged customizations
-22
+23
 Usage insights
-23
+24
 Power Apps code apps
-24
+25
 Content security policy
 Note
 The rules that have "(preview)" in their name are in public preview, while rules without it are considered generally available.

```

---

## HIGH: Control Review Recommended

### 1. Power Platform Inventory

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:445040f7e921a7826fb56c4dd2b86b1e240e19ce59ab92d1e71f8d9cd7ba6fde

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`

**What Changed:**
```diff
--- +++ @@ -43,7 +43,9 @@ Agents
 : All agents you create in Copilot Studio, and all agents you create in Microsoft 365 Copilot Agent Builder.
 Apps
-: All apps you create in Power Apps (canvas, model-driven, code, and vibe) and in Microsoft 365 Copilot's App Builder agent.
+: All canvas, model-driven, code, vibe, and
+managed apps
+, and all apps you create in Microsoft 365 Copilot's App Builder agent.
 Flows
 : All agent flows you create in Copilot Studio, all cloud flows you create in Power Automate, and all workflows you create in Microsoft 365 Copilot's Workflows agent.
 Connectors (preview)
@@ -88,7 +90,7 @@ Agents
 from Microsoft 365 Copilot and Copilot Studio
 Agentic apps
-, including vibe apps, code apps, and App Builder apps
+, including vibe apps, code apps, managed apps, and App Builder apps
 Agent flows
 from Copilot Studio and workflow agent flows from Microsoft 365 Copilot
 Environments
@@ -115,7 +117,7 @@ Power Apps
 >
 App Inventory tab
-: Canvas, model-driven, code, vibe, and App Builder apps.
+: Canvas apps, model-driven apps, code apps, vibe apps, managed apps, and App Builder apps.
 Manage
 >
 Power Automate
@@ -126,6 +128,10 @@ You can access Power Platform inventory data programmatically, which supports advanced scenarios such as automation, reporting, and integration with external tools. For a complete list of resource types and their fields, see
 Power Platform inventory schema reference
 .
+Important
+The
+Query Power Platform resources
+action in the Power Platform API and the Power Platform for Admins V2 connector currently support only delegated user authentication. The action doesn't support service principal or managed identity authentication and returns HTTP 403 Forbidden for those identities. Use a delegated user token or user-authenticated connection instead.
 Power Platform for Admins V2 connector
 You can query Power Platform inventory data directly from Power Automate by using the
 Power Platform for Admins V2 connector
@@ -138,
```

---

### 2. Agent Orchestration

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:383eeed04b1cfd710f009b9a3eaee0576eeabc4f8e62c3c40bda90968b52afa4

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

**What Changed:**
```diff
--- +++ @@ -26,8 +26,8 @@ This article describes features used in agents or agent flows powered by the
 standard harness
 .
-Tools are building blocks that let your agent interact with external systems. Tools expand what your agent can do, letting your agent perform various actions in response to user requests or autonomous triggers. Each tool represents a specific capability that your agent can perform. For example, you can equip your agent with tools that perform tasks like:
-Send emails using the Office 365 Outlook connector
+Tools are building blocks that let your agent interact with external systems. Tools expand what your agent can do, and your agent can perform various actions in response to user requests or autonomous triggers. Each tool represents a specific capability that your agent can perform. For example, you can equip your agent with tools that perform tasks like:
+Send emails by using the Office 365 Outlook connector
 Check the current weather conditions and forecasts
 Read and write data from Dataverse
 Read and post messages to Teams
@@ -39,15 +39,15 @@ . You can also call tools explicitly from within a
 topic
 .
-With
+By using
 generative orchestration
 (active by default), your agent can automatically select the most appropriate tool or topic, or search across knowledge, to respond to a user. This orchestration mode creates a more dynamic and intelligent conversation experience.
 In classic mode (generative orchestration turned off), an agent can only use topics to respond to the user. However, you can still design your agent to call tools explicitly from within topics.
-There are several mechanisms available to you to add tools to your agent:
+You can use the following mechanisms to add tools to your agent:
 Connector
-: Connect to proprietary APIs and services using Power Platform Connectors to pull in data or carry out actions.
+: Connect to proprietary APIs and services by using Power Platform Connectors to pull in data or carry out actions.
```

---

### 3. Application Resources

**URL:** https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0
**Section:** Microsoft Graph API
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:f9d5f42fcb8a3815a651e0faa001e2ba16d416d5c0cdd49dc5f3eb8aec03978e

**Affected Controls:**
- Control 1.2: Control 1.2: Agent Registry and Integrated Apps Management
  - File: `controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md`

**What Changed:**
```diff
--- +++ @@ -175,6 +175,11 @@ The collection of roles defined for the application. With
 app role assignments
 , these roles can be assigned to users, groups, or service principals associated with other applications. Not nullable.
+App roles and exposed delegated permission scopes (
+api.oauth2PermissionScopes
+) share a default limit of 700 permission definitions per application. Enabled and disabled definitions both count. This limit is separate from the aggregate 1,200-entry application manifest limit and from app role assignment limits. For counting rules, behavior for existing objects above the limit, and design guidance, see
+App role limits
+.
 authenticationBehaviors
 authenticationBehaviors
 The set of breaking change behaviors related to token issuance that are configured for the application. Authentication behaviors are unset by default (

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Maker Onboarding (Welcome Content)
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/welcome-content
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8f2c79e045daa94f859e9daced9820de82f26c8b72abc6541597e1240e2389d6

---

### 2. M365 Copilot Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:78bf784b00d8e45ab87dea3f6a64ee22664af35f5bb8443d96af80fc65709006

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*