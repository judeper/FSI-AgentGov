# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-28
**Run Time:** 2026-08-28T18:18:05.706261+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 6 |
| HIGH Changes | 8 |
| MEDIUM Changes | 5 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...m/en-us/connectors/custom-connectors/ | HIGH | 2.7 | Review and update |
| 2 | fundamentals-what-is-copilot-studio | CRITICAL | 2.13 | Monitor |
| 3 | ...ication-fundamentals-publish-channels | HIGH | None | Review and update |
| 4 | admin-share-bots | HIGH | 3.2, 3.10, 2.9, 2.5, 2.6 | Update portal-walkthrough |
| 5 | analytics-overview | HIGH | 3.2, 3.10, 2.9, 2.5, 2.6 | Update portal-walkthrough |
| 6 | analytics-improve-agent-effectiveness | HIGH | None | Update portal-walkthrough |
| 7 | advanced-connectors | HIGH | None | Review and update |
| 8 | nlu-gpt-overview | MEDIUM | 2.12 | Review optional |
| 9 | add-tools-custom-agent | HIGH | 2.17 | Review and update |
| 10 | advanced-hand-off | MEDIUM | 2.19, 2.12 | Update portal-walkthrough |
| 11 | authoring-test-bot | HIGH | 2.5 | Update portal-walkthrough |
| 12 | mcp-create-new-server | HIGH | None | Review and update |
| 13 | whats-new | HIGH | None | Review and update |
| 14 | microsoft-365-copilot-overview | HIGH | 3.8 | Review and update |
| 15 | dlp-learn-about-dlp | HIGH | 1.5, 1.25, 1.3, 1.26 | Update portal-walkthrough |
| 16 | dlp-policy-reference | HIGH | 1.5 | Review and update |
| 17 | whats-new | CRITICAL | None | Monitor |
| 18 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Share and Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:b725505e4525b95edcc402a886adf45109e44f26078c52e6867ca9ac31b8fb21

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

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
@@ -22,6 +22,10 @@ Share agents with other users
 Feedback
 Summarize this article for me
+Note
+This article describes features used in agents or agent flows powered by the
+standard harness
+.
 You can share your agents with others in either of the following ways:
 Grant security groups, or your whole organization, permission to chat with the agent.
 Invite users to collaborate on your agent project. Collaborators always have permission to chat with the agent.
@@ -40,7 +44,7 @@ is turned on, to manage who can chat with the agent in your organization.
 Share an agent for chat
 Web app
-Teams
+Teams app
 Collaborators
 with authoring permissions for a shared agent can always chat with it. However, you can also grant users permission to chat with an agent in Copilot Studio without granting them authoring permissions.
 To grant users permission to only chat with the agent, you can:
@@ -171,7 +175,7 @@ to share the agent with everyone in the organization.
 Share an agent for collaborative authoring
 Web app
-Teams
+Teams app
 When you share an agent with others for
 collaborative authoring,
 you give them permission to view, edit, configure, share, and publish the agent. They can't delete the agent. You can only share agents for collaborative authoring with individual users in your organization. These users can be in different Power Platform environments, as long as they belong to your organization.
@@ -307,6 +311,39 @@ The Bot Transcript Viewer security role is assigned at the environment level in the Power Platform admin center. Learn more about
 enabling this security role
 in your single or group environment.
+Share an agent's evaluations
+Use the
+Agent Viewer
+role in Copilot Studio to give evaluators access to an agent's evaluations without letting them change the agent.
+What is the agent viewer role?
+The agent viewer role is a sharing role th
```

---

### 2. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:de5397a388a6d27513af8abee1b79ea0746eb2791c21f1ae081a27b27c4085ab

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)

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
@@ -19,28 +19,32 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Analytics overview
+Monitor overview
 Feedback
 Summarize this article for me
+Note
+This article describes features used in agents or agent flows powered by the
+standard harness
+.
 Use analytics to understand how well your agent is performing and to identify areas for improvement.
 The
-Analytics
+Monitor
 page in Copilot Studio shows you comprehensive data for your agent, from an overview of key metrics to in-depth usage analytics for your agent's components. You can drill down into each piece of data to get more details.
-The analytics experience is tailored for
+The Monitor experience is tailored for
 conversational agents
 and for
 autonomous agents
 .
-Analytics are available in all geographies. Analytics data is available for up to 360 days. Session details and transcript information are available for the last 28 days. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
-Note
-The
-Analytics
+Monitoring is available in all geographies. Monitor data is available for up to 360 days. Session details and transcript information are available for the last 28 days. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
+Note
+The
+Monitor
 page doesn't show analytics for activity you complete when you test your agent in Copilot Studio by using the
 test panel
 .
 Grant limited view-only access to analytics
 If you're the agent owner and want to grant access only to the
-Analytics
+Monitor
 page of your agent, you can do so by sharing the agent with the
 Analytics Vi
```

---

### 3. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:ed92879d2f725960823cbddfd33dd3af11049d7c8f23b384bb1f1b6c66a5eed7

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

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
@@ -19,18 +19,22 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Analyze conversational agents
+Monitor conversational agents
 Feedback
 Summarize this article for me
-The
-Analytics
+Note
+This article describes features used in agents or agent flows powered by the
+standard harness
+.
+The
+Monitor
 page in Copilot Studio provides an aggregated insight into the overall effectiveness of your agent across
 analytics sessions
 . The page is divided into core areas that focus on different performance contexts. The page also displays an
 Overview
 area that provides high-level, key performance indicator (KPI) metrics for your agent, a
 Savings
-area that analyzes time and cost savings attributable to your agent or your agent's tools, and a
+area that displays time and cost savings attributable to your agent or your agent's tools, and a
 Summary
 area that provides key analytic insights into your agent's performance.
 There are four core sections to focus on when reviewing and improving conversational agent effectiveness.
@@ -40,7 +44,7 @@ Overview
 , and
 Savings
-section shows key analytics insights about your agents along with billing and cost savings statistics; see
+section shows key insights about your agents along with billing and cost savings statistics; see
 Summary
 ,
 Overview
@@ -60,8 +64,12 @@ Custom metrics
 The
 Custom metrics
-section lets you define up to three business-specific metrics in natural language and track how often each outcome appears across sampled sessions. Use these metrics to complement your standard analytics insights with indicators that reflect your agent's goals and business use. To learn how to create, test, and refine custom metrics, see
-Analyze your agent with custom metrics
+section lets you define up to three business-specific metrics in natural language and track how often 
```

---

### 4. Human Agent Handoff

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c115e1391dc209aeaeb6077eb452bcabd624b37bd2c0e665ada38cd737209412

**Affected Controls:**
- Control 2.19: Control 2.19: Customer AI Disclosure and Transparency
  - File: `controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.19/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.19/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)

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
@@ -22,6 +22,10 @@ Hand off to a live agent
 Feedback
 Summarize this article for me
+Note
+This article describes features used in agents or agent flows powered by the
+standard harness
+.
 By using Copilot Studio, you can configure your agent to hand off conversations to live agents seamlessly and contextually.
 When your agent hands off a conversation, it can share the full history of the conversation, and all relevant variables. A live agent that uses a connected engagement hub sees an alert, reviews the conversation history, and continues the conversation.
 For more information about how to configure handoff with

```

---

### 5. Test Your Agent

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:4bbbbecb25684240876a275f7a560c017dc6ec729dc8c15c92af3b98c1447d8f

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

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
@@ -22,29 +22,34 @@ Test your agent
 Feedback
 Summarize this article for me
+Note
+This article describes features used in agents or agent flows powered by the
+standard harness
+.
 As you design your agent in Copilot Studio, use the test panel to see how the agent leads a customer through the conversation. It's a good way to make sure your topics work and that conversations flow as you expect.
 When you test an agent that uses generative orchestration, you can follow the orchestrator's plan in real time on the
 activity map
 . Close the activity map if you want to follow through the conversation path step by step with tracking between topics turned on.
 In addition to testing your agent in the
 Test your agent
-panel, you can create test sets of multiple queries for automated testing. For more information, see
+panel, you can create test sets of multiple queries for automated testing. Learn more in
 Create test cases to evaluate your agent (preview)
 .
 Use the test chat
 Web app
-Classic
-Teams
+Teams plan
+Teams app
 Use the
 Test your agent
 panel to walk through your agent conversations as a user. It's a good way to make sure your topics are working and that conversations flow as you expect.
-In addition to testing your agent in
+In addition to testing your agent in the
 Test your agent
 panel, you can create test sets of multiple queries for
 automated testing
-. To start an automated test, select the evaluate
-button.
-Preview a conversation
+. To start an automated test, select the
+Evaluate
+icon.
+To preview a conversation:
 If the
 Test your agent
 panel is hidden, open it by selecting
@@ -64,7 +69,7 @@ to avoid having to collapse the activity map at every conversation turn.
 Continue the conversation until you're satisfied that it flows as intended.
 Tip
-You can update a topic at any time while interacting with the test agent. Save you
```

---

### 6. Data Loss Prevention

**URL:** https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:a7a9df9d4cf8fc860c5e4e602d255389387238e58dea2536c976322ae68382df

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.25: Control 1.25: MIME Type Restrictions for File Uploads
  - File: `controls/pillar-1-security/1.25-mime-type-restrictions.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)

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
@@ -46,14 +46,15 @@ Use Network Data Security to help prevent sharing sensitive information with unmanaged AI (preview)
 Enterprise applications and devices
 DLP monitors and protects against oversharing in enterprise apps and on devices. It targets Microsoft 365 locations, like Exchange and SharePoint, and locations you add, like on-premises file shares, endpoint devices, and non-Microsoft cloud apps. These locations and sources include:
-Microsoft 365 services, like Exchange, SharePoint, OneDrive accounts, and Teams chat and channel messages
-Office applications, such as Word, Excel, and PowerPoint
-Devices running Windows 10, Windows 11, and the three most recent versions of macOS
-Non-Microsoft cloud apps
-On-premises file shares and on-premises SharePoint
-Microsoft Fabric and Power BI workspaces
-Microsoft 365 Copilot and Copilot chat (preview)
-Managed cloud apps
+Microsoft 365 services, like Exchange, SharePoint, OneDrive accounts, and Teams chat and channel messages.
+Office applications, such as Word, Excel, and PowerPoint.
+Devices running Windows 10, Windows 11, and the three most recent versions of macOS.
+Non-Microsoft cloud apps.
+Non-Microsoft connected apps (currently in preview), including Box, Dropbox, Google Workspace, and Salesforce.
+On-premises file shares and on-premises SharePoint.
+Microsoft Fabric and Power BI workspaces.
+Microsoft 365 Copilot and Copilot chat (preview).
+Managed cloud apps.
 Create DLP policies for
 Enterprise applications & devices
 to cover these locations.

```

---

## HIGH: Control Review Recommended

### 1. Custom Connectors

**URL:** https://learn.microsoft.com/en-us/connectors/custom-connectors/
**Section:** Power Platform Administration
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:4a825442d4245a7c6ae1a96b427199574f55b52b8a1d3d3e7f735e90dc10c0c8

**Affected Controls:**
- Control 2.7: Control 2.7: Vendor and Third-Party Risk Management
  - File: `controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md`

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
@@ -64,7 +64,7 @@ Secure your API and connector with Microsoft Entra ID
 .
 2.1. OAuth 2.0
-Newly created custom connectors that use OAuth 2.0 to authenticate automatically have a per connector redirect URI. Existing OAuth 2.0 connectors must be updated to use a per-connector redirect URI before February 17, 2024.
+Custom connectors that use OAuth 2.0 to authenticate use a per-connector redirect URI. If you have older custom connectors created before February 2024 that were using the global redirect URI, those connectors were updated or stopped working for new connections after the per-connector redirect URI was enforced.
 If you created your custom connectors with the web interface, edit your custom connectors, go to the
 Security
 tab and check the box,
@@ -78,7 +78,6 @@ Once custom connectors are updated to use the per-connector redirect URI either through the setting in the
 Security
 tab or the CLI tool, remove the global redirect URI from your OAuth 2.0 apps. You should add the newly generated unique redirect URL to your OAuth 2.0 apps.
-We'll enforce this update for existing OAuth 2.0 custom connectors starting on February 17, 2024. Any custom connector not updated to use a per-connector redirect URI stops working for new connections and shows an error message to the user.
 To find out which custom connectors need an update to migrate to per-connector redirect URL, you can create a flow that uses the
 Get Custom Connectors as Admin
 action of Power Apps for Admin connector and parse its result. The flow attached later in this article fetches all the custom connectors using the same. It then applies a filter condition on the connection parameter's property to filter out non-Oauth custom connector, followed by another filter to select only connectors that don't use the per connector unique redirect URL. Finally, it puts the selected custom conn
```

---

### 2. Agent Publishing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:b84082a9eb7a853eafa957c9bb8779e642e2a1cfa5d7f49084aeace9d5853e1f

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
@@ -22,6 +22,10 @@ Key concepts - Publish and deploy your agent
 Feedback
 Summarize this article for me
+Note
+This article describes features used in agents or agent flows powered by the
+standard harness
+.
 By using Copilot Studio, you can publish agents that engage with your customers on multiple platforms or channels. For example, live websites, mobile apps, Microsoft 365 Copilot, and messaging platforms like Teams and Facebook.
 Each time you update your agent, you can publish it again from within Copilot Studio. Publishing your agent applies to all the channels associated with your agent.
 You need to publish your agent before your customers can engage with it. You can publish your agent on multiple platforms, or
@@ -95,6 +99,12 @@ Only share the demo website URL with members of your team and other stakeholders to try out the agent. The demo website isn't intended for production use. You shouldn't share this URL with customers.
 Configure channels
 After you publish your agent at least once, add channels so your customers can reach it.
+Note
+Some channels might be unavailable or disabled in your environment. Administrators can control which channels are available for Copilot Studio agents by using
+Agent access channels
+in the Power Platform admin center. Learn more in
+Configure channel publishing and connected agent access (preview)
+.
 To configure channels for your agent:
 On the top menu bar, select
 Channels
@@ -188,26 +198,20 @@ Use Microsoft Bot Framework skills in Copilot Studio
 .
 Next steps
-Web app
-Teams
 Article
 Description
 Publish an agent to a live or demo website
 Publish your agent on your live website, or use a demo website to share internally.
 Connect and configure an agent for Teams and Microsoft 365 Copilot
 Use Teams and Microsoft 365 Copilot to distribute your agent.
+Create a privacy statement and terms of use 
```

---

### 3. Connectors

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:b2c09596a7bbd28a269b70185343ca2d5e82af13b4aa73896bdd830d207a8104

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
@@ -19,9 +19,13 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Use Power Platform connectors as tools
+Use Power Platform connectors as tools in Copilot Studio agents
 Feedback
 Summarize this article for me
+Note
+This article describes features used in agents or agent flows powered by the
+standard harness
+.
 Connectors from Microsoft Power Platform
 act as proxies or "wrappers" around APIs. They enable Copilot Studio, Power Automate, Power Apps, and Azure Logic Apps to communicate with other apps and services. By using connectors, you can connect your accounts and use prebuilt tools and triggers to build your apps and workflows.
 By using connectors, you can access various services (both within the Microsoft ecosystem and outside it) to perform a wide array of tasks automatically.
@@ -44,7 +48,7 @@ Within a
 topic
 .
-Connectors can also be used in Copilot Studio as:
+You can also use connectors in Copilot Studio as:
 Actions in
 agent flows
 Knowledge sources. For more information, see
@@ -65,7 +69,7 @@ .
 Select
 Connector
-. The different services with connectors available are displayed.
+. You see the different services with connectors available.
 Select the service you want to connect to, or search for the service by name in the search box. You see a list of tools available for the service connector.
 Select the tool you want to add. The
 Add tool

```

---

### 4. Agent Orchestration

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:2bd6b149f49e223f35defa4618e77b778ea566097795cca1a3104720f16566a0

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
@@ -22,6 +22,10 @@ Add tools to custom agents
 Feedback
 Summarize this article for me
+Note
+This article describes features used in agents or agent flows powered by the
+standard harness
+.
 Tools are building blocks that let your agent interact with external systems. Tools expand what your agent can do, letting your agent perform various actions in response to user requests or autonomous triggers. Each tool represents a specific capability that your agent can perform. For example, you can equip your agent with tools that perform tasks like:
 Send emails using the Office 365 Outlook connector
 Check the current weather conditions and forecasts
@@ -54,12 +58,15 @@ : Connect to an MCP server to access tools and resources.
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
+Skills in the context of the agents powered by the standard harness aren't the same as the skills used in coding agents. You can only add coding agent skills to agents powered by the GitHub Copilot harness.
 Create and add a new tool at agent level
 Creating new tools directly 
```

---

### 5. Create Custom MCP Server

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:e76ba1a369766b71362489ab8022b97accc507eab60c59eab24a7541bdb54db4

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

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
@@ -22,24 +22,31 @@ Create a new Model Context Protocol (MCP) server
 Feedback
 Summarize this article for me
-You can use
+Note
+This article describes features used in agents or agent flows powered by the
+standard harness
+.
+Use
 MCP software development kits (SDKs)
 to set up an MCP server in one of the supported languages.
 If you already have an MCP server set up, see
 Add an existing Model Context Protocol (MCP) server to your agent
 for information on how to add the server to your agent.
 Authentication support
-When you create an MCP server, you can choose to implement authentication or not. If you choose to implement authentication, you can use one of the following methods:
+When you create an MCP server, you can choose to implement authentication or not. If you choose to implement authentication, use one of the following methods:
 API key
 : A simple way to secure your server by making your application include a key with requests.
 OAuth 2.0
 : A more robust authentication method that lets individual users grant access to their data without sharing their credentials with the agent.
 Choose the method that best fits your needs and follow the implementation guidelines for that method.
-You must register your application with an identity provider to obtain the necessary client credentials. The credentials are either an application key for API key authentication or a client ID and client secret for OAuth 2.0 authentication.
-You must provide the authentication credentials from your identity provider when you add the MCP server to your agent in Copilot Studio. To learn more, see
+Register your application with an identity provider to obtain the necessary client credentials. The credentials are either an application key for API key authentication or a client ID and client secret for OAuth 2.0 authentication.
+Provide the authentication credent
```

---

### 6. Copilot Studio Kit — Compliance Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:e1f2bc9db98932c7e0dcf1688691d2cf37e92ffba35f224486c9facd81c16e1e

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
@@ -23,10 +23,39 @@ Feedback
 Summarize this article for me
 Get the latest information about what's new and what changed in the Copilot Studio guidance hub.
+August 2026
+New articles
+Prevent duplicate messages with context-aware design in the standard harness
+Manage the AI model lifecycle for Copilot Studio agents
+July 2026
+New articles
+New Copilot Agent Kit capabilities, including
+Agent Debugger
+,
+Agent Library
+,
+Agent Insights Hub
+,
+Power Shield
+, and
+Agent Review Pipeline
+, with significant updates to
+Agent Review Tool
+to describe its expanded scope. This update marks the first phase of the rename from
+Copilot Studio Kit
+to
+Copilot Agent Kit
+.
 June 2026
 New articles
 Measure the return on investment (ROI) and business value of AI agents
 Plan Copilot Studio agent deployments for throughput and rate limits
+Other updates
+New real-world case studies, on how
+Grupo Bimbo standardizes global audit processes with Copilot Studio
+and on how
+Copilot Agent Kit helps organizations improve visibility, monitor performance, and refine their agents
+.
 May 2026
 Architecting agent solutions
 moved to the
@@ -52,7 +81,7 @@ Dunaway, a Texas-based, multidiscipline design, planning, and engineering firm, streamlines city code research with Copilot Studio
 and on how the
 Singapore Civil Defence Force implements digital solutions using Power Platform and Copilot Studio
-Rubrics refinement in Copilot Studio Kit
+Rubrics refinement in Copilot Agent Kit
 Copilot Studio and agent samples
 Connect to custom knowledge sources
 Localize Adaptive Card content
@@ -122,7 +151,7 @@ December 2025
 New articles
 Best practices for planning and creating performance tests for conversational agents
-Define and enforce agent compliance with Copilot Studio Kit Compliance Hub
+Define and enforce agent compliance with Copilot Agent Kit Compliance Hub
 Updat
```

---

### 7. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:f04760b6810a425b0b3e1c8849c4bf7118323668d004b47b5f74acd3c8dfdade

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

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
@@ -19,220 +19,379 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Microsoft 365 Copilot overview
+Microsoft Copilot overview
 Feedback
 Summarize this article for me
 Note
-Microsoft onboarded Anthropic as a Microsoft subprocessor. As a subprocessor, Anthropic operates with
+Microsoft Copilot is available in many regions worldwide. However, it might not be accessible in certain markets. Some organizations might gain access through an account support escalation process, but access is subject to approval. For more information, see
+International availability
+.
+Microsoft Copilot Chat and Microsoft Copilot responses and experiences differ by data grounding, integration depth, and licensing:
+However, all experiences are powered by:
+Large language models (LLMs)
+for natural language understanding and generation
+Grounding in web
+and/or
+organizational data
+(
+Microsoft Graph
+and
+Work IQ
+)
+Access scoped by user permissions (security and compliance enforced)
+Note
+Anthropic subprocessors are available only in applicable Microsoft 365 licensed experiences and aren't available to all users by default. Anthropic operates with
 Microsoft Enterprise data protections
 . For more information, see
 Anthropic as a subprocessor for Microsoft Online Services
 .
-Microsoft 365 Copilot is an AI-powered tool that helps with your work tasks
-.
-Users enter a prompt in Copilot and Copilot responds with AI-generated information. The responses are in real-time and can include internet-based content and work content that users have permission to access.
-Users get content relevant to their work tasks, and in the context of the Microsoft 365 app they're using.
-The following video provides an overview of Microsoft 365 Copilot. It's 1 minute and 49 seconds long.
-Using Microsoft 365 Copilot
-Say, for example, you're an operations
```

---

### 8. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:3eda24d428bd49d9e271b8d2d27eec6fc4c9b362b58f0d577349c4048c6d6f5f

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

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
@@ -917,7 +917,7 @@ -
 Get started with Endpoint data loss prevention
 -
-Configure device proxy and internet connection settings for Information Protection
+Configure device proxy and internet connection settings for Microsoft Purview Endpoint DLP
 On-premises repositories (file shares and SharePoint)
 No
 Repository
@@ -925,17 +925,23 @@ -
 Learn about the data loss prevention on-premises repositories
 -
-Get started with the data loss prevention on-premises repositories
+Get started with data loss prevention for on-premises repositories
 Fabric and Power BI
 No
 Workspaces
 data-in-use
 No
-Third-party apps
-None
-No
-No
-No
+Non-Microsoft connected apps (preview)
+No
+Cloud app instance
+data-at-rest
+-
+Use DLP and sensitivity label policies for non-Microsoft connected apps
+- Only available in the
+Custom
+policy template
+- Set up a
+Microsoft Defender for Cloud Apps connector
 Microsoft 365 Copilot (preview)
 No
 Account or Distribution group
@@ -1795,9 +1801,7 @@ patent
 , etc.
 Document name matches patterns:
-Detects documents where the file name matches specific patterns. The evaluation considers the entire path of the document, not just the documentâs name. The pattern is checked as a string match, meaning it can match any part of the document path. To define the patterns, use wild cards. For information on regex patterns, see the Regular Expression documentation
-here
-.
+Detects documents where the file name matches specific patterns. The evaluation considers the entire path of the document, not just the documentâs name. The pattern is checked as a string match, meaning it can match any part of the document path. To define the patterns, use wild cards.
 Note
 Due to potential performance issues, this condition will gradually be phased out from Purview Endpoint DLP. We recommend using the 'Document name contains words or phrases' c
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Copilot Studio Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:0f026864b85c129e563fc9b99a77957d4dfb2dafc7c934ea4770f16f84165c34

---

### 2. Quickstart: Create and deploy an agent
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-gpt-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fd6545b137837940ec19fcdfab3f230b814d6f7de7bbaf7c7978af05ed825b77

---

### 3. Human Agent Handoff
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c115e1391dc209aeaeb6077eb452bcabd624b37bd2c0e665ada38cd737209412

---

### 4. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:2ea0d53f687691b02cb2acf732bdb90bf22a960d3bd4c68c48c174c9df79ad99

---

### 5. Copilot Studio Licensing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:222a23d8e4b5be182b94450ab9868af93088e8898cbaf9df4cf812ef753eb791

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