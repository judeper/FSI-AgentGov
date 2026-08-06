# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-29
**Run Time:** 2026-07-29T08:42:28.707599+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 4 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | environment-groups | HIGH | 1.4, 1.28, 2.2, 2.15 | Update portal-walkthrough |
| 2 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 3 | analytics-common-data-service | HIGH | 2.9 | Review and update |
| 4 | capacity-storage | HIGH | 3.5 | Review and update |
| 5 | add-tools-custom-agent | HIGH | 2.17 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Environment Groups

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/environment-groups
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:9754011ed502bae00c9951d59da3bb3ca62c81339a10d4ef087537bf8dd244d3

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 2.2: Control 2.2: Environment Groups and Tier Classification
  - File: `controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md`
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.2/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.2/troubleshooting.md` (HIGH)

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
@@ -25,7 +25,7 @@ Managing the Power Platform on a large scale across numerous environments, ranging from hundreds to tens of thousands, poses a significant challenge for both startup and enterprise IT teams. To address these complexities, environment groups offer a premium governance solution designed to streamline management tasks by organizing environments into logical collections and enforcing uniform policies and configurations.
 Think of an environment group as a "folder" for your environments. Administrators can cluster a flat list of environments into structured groups based on criteria such as business unit, project, geographic region, or purpose. By creating these logical collections, IT teams gain the ability to manage multiple environments simultaneously and efficiently implement security, governance, and compliance policies on a large scale through centrally managed rules. This centralized approach eliminates the need to configure each environment one-by-one, ensures consistency, significantly reduces administrative overhead, and prevents issues such as configuration drift and chaotic management practices common in extensive deployments.
 Note
-Environment groups can only contain Managed Environments.
+Environment groups can only contain managed environments.
 Each environment can belong to only one group, and groups can't overlap or be nested.
 Environments in a group can span different regions and types as long as each is managed.
 Environments can be transferred between groups by removing them from one and adding them to another.
@@ -101,7 +101,7 @@ Power Platform for Admins V2 (Preview) connector
 offers an alternative solution. It allows the creation and deletion of environment groups and the ability to add or remove environments from these environment groups, facilitating opportunities for automation.
 Configure the rules for your
```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:3e52adb9ebfb951acc6f2444443c476b4cfd97f83ba378775a134dd117f3083b

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

### 2. Analytics

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/analytics-common-data-service
**Section:** Power Platform Administration
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:724147ab00dbbd888671c98e2cb3543716ed6618de95342643d2885a0f0430af

**Affected Controls:**
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`

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
@@ -329,7 +329,7 @@ Total API Calls
 This chart shows total number of API calls made in the environment with a Dataverse database over a specified time.
 Most Used API
-This chart shows top-10 most executed API calls in the environment with a Dataverse database database. Adding the individual counts provide the total of the top-10 API calls. This is not be the same as the all-up Total API Calls metric.
+This chart shows top-10 most executed API calls in the environment with a Dataverse database. Adding the individual counts provide the total of the top-10 API calls. This is not be the same as the all-up Total API Calls metric.
 API Calls
 This chart shows the number of API calls made over time in the environment with a Dataverse database over a specified time. Adding up the individual counts equals the Total API Calls count.
 API peak call rate

```

---

### 3. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:8251dfe9e3bbcfb9912e900db1a99b3404fa4e2f0763822058b373c86ae7e956

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

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
@@ -311,7 +311,7 @@ Overage status if capacity is allocated to the environment
 Whether capacity is preallocated to the environment
 Environment type
-Managed Environment status
+Managed environment status
 Pay-as-you-go plan linkage status
 Ability to draw capacity from available tenant pool
 Database, file, and log consumption
@@ -342,6 +342,55 @@ in the
 Usage per storage type
 tile. Select the table name for the consumption trend, with the option to track daily usage trends, for up to the past three months.
+Dataverse storage advisor (preview)
+Preview features aren't meant for production use and may have restricted functionality. These features are available before an official release so that customers can get early access and provide feedback.
+Dataverse storage advisor analyzes table-level storage consumption and recommends data that you can clean up to reduce storage usage. The advisor surfaces these recommendations directly in the
+Licensing
+>
+Dataverse
+capacity view, so you can act on them without leaving the Power Platform admin center.
+Note
+Dataverse storage advisor is being rolled out gradually and might not be available in your environment yet. When it's available, recommendations appear only for environments that have storage that can be cleaned up.
+When recommendations are available, the advisor adds the following experiences:
+Storage recommendation banner
+: A banner appears above the capacity details that estimates how much space the advisor can help you reclaimâfor example,
+Storage advisor has action plans to clean up space and manage the environment
+. Select the banner to open the
+Dataverse storage advisor
+panel.
+Clean up column
+: The
+Consumption per table
+grid includes a
+Clean up
+column that shows the estimated space the advisor recommends cleaning up for each table. The environment list in the
+Manage capacit
```

---

### 4. Agent Orchestration

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:eab3106c426ac6e5c1b5d2816515bd89ccb451fb1d4c8b24d021a7a6ce68ea54

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
@@ -54,12 +54,15 @@ : Connect to an MCP server to access tools and resources.
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
+Skills in the context of the classic agent experience aren't the same as the skills used in coding agents. You can only add coding agent skills to agents in the new agent experience.
 Create and add a new tool at agent level
 Creating new tools directly within Copilot Studio streamlines the development process and ensures proper integration with your agent. Tools added to an agent are available for automatic orchestration throughout your agent's conversations.
 Open your agent by choosing
@@ -288,15 +291,6 @@ When using multi-agent orchestration with
 child agents
 , child agents have their own orchestration and can manage their own set of up to 128 tools.
-Related content
-Use connectors
-Use prompts
-Use agent flows with your agent
-Model context protocol (MCP)
-Add tools from a REST API
-Use skills
-Client tools
-Computer use (preview)
 Feedback
 Was this page helpful?
 Yes

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