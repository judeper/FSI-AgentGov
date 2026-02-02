# Microsoft Learn Documentation Changes - 2026-02-01

**Run Time:** 2026-02-01T06:52:45.727798+00:00
**Total URLs Checked:** 209
**Meaningful Changes:** 31
**Minor Changes:** 4
**Redirects:** 54
**Errors:** 1

---

## Summary of Required Actions

| Priority | Count | Action Required |
|----------|-------|-----------------|
| HIGH | 31 | Control/playbook may need review |
| MEDIUM | 4 | Minor content change - review optional |

---

## HIGH: Control Review Recommended

### 1. Share and Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Section:** Copilot Studio
**Classification:** Meaningful (Configuration instructions)

**What Changed:**
```diff
--- +++ @@ -46,14 +46,18 @@ Collaborators
 , who have authoring permissions for a shared agent, can always chat with it. However, you can also grant users permission to chat with an agent in Copilot Studio without granting them authoring permissions.
 To grant users permission to only chat with the agent, you can either:
+Share your agent with individual users.
 Share your agent with a security group.
 Share your agent with everyone in your organization.
 Note
 When sharing an agent for
 chat
-you can't share it with:
-Microsoft 365 groups.
-Individual users directly. To manage individual user access, add or remove users from the security group.
+, you can't share it with:
+Microsoft 365 groups with
+SecurityEnabled
+set as false. To change this setting, learn more in
+Share an app with Microsoft 365 groups
+.
 To author agents in Copilot Studio, makers need at least the
 Environment Maker
 role. The
@@ -62,7 +66,7 @@ Bot Contributor
 and
 Environment Maker
-roles. Users in these roles can only access agents they created or that have been shared with them. Additionally, makers must have the
+roles. Users in these roles can only access agents they created or the agents shared with them. Additionally, makers must have the
 prvAssignRole
 privilege, included in the
 System Administrator
@@ -81,20 +85,24 @@ ) and then select
 Share
 .
-Enter the name of every security group that you would like to share the agent with.
+Enter the name of every security group that you want to share the agent with.
 Review the permissions for each security group.
-If you want to let the users know you shared the agent with them, select
+If you want to let the users know you shared the agent with them, select the three dots at the top of the sharing screen (
+â¦
+), then
+Use Classic Sharing
+. You can then select
 Send an email invitation to new users
-.
+at the bottom of the screen.
 Note
 Users can only receive an email invitation if their security group has email enabled. Alternatively
```

### 2. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** Meaningful (UI element names)

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC 2011-12/SR 11-7) (`controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md`)
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization (`controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`)
- Control 3.10: Control 3.10: Hallucination Feedback Loop (`controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`)
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring (`controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`)

**What Changed:**
```diff
--- +++ @@ -29,17 +29,17 @@ Use analytics to understand how well your agent is performing and to identify areas for improvement.
 The
 Analytics
-tab in Copilot Studio shows you comprehensive data for your agent, from an overview of key metrics to in-depth usage analytics for your agent's components. You can drill down into each piece of data to get more details.
+page in Copilot Studio shows you comprehensive data for your agent, from an overview of key metrics to in-depth usage analytics for your agent's components. You can drill down into each piece of data to get more details.
 The analytics experience is tailored for
 conversational agents
 and for
 autonomous agents
 .
-Analytics are available in all geographies. Time and date stamps in analytics are in Coordinated Universal Time (UTC). This includes day start and end times, session times, and any other time markers in your agent's data.
+Analytics are available in all geographies. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
 Note
 Analytics aren't available on the
 Analytics
-page for activity completed when you test your agent in Copilot Studio using the
+page for activity completed when you test your agent in Copilot Studio by using the
 test panel
 .
 To access analytics:
@@ -74,16 +74,18 @@ Analytics for conversational agents
 in Copilot Studio track user engagement with your agent and try to capture how well your agent handles user tasks.
 Conversational analytics uses the following concepts and terms:
-Conversations
-are an ongoing interaction between a specific user, or group of users, on a
+Conversations are an ongoing interaction between a specific user, or group of users, on a
 channel
 and your agent.
 Conversations can pause and resume later, or be
 transferred to a customer service representative
-. The conversation might be one-way, either from 
```

### 3. Connectors

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors
**Section:** Copilot Studio
**Classification:** Meaningful (Configuration instructions)

**What Changed:**
```diff
--- +++ @@ -27,13 +27,11 @@ Feedback
 Summarize this article for me
 Connectors from Microsoft Power Platform
-are proxies or "wrappers" around APIs that allow Copilot Studio, Power Automate, Power Apps, and Azure Logic Apps to talk to other apps and services. Connectors let you connect your accounts and use prebuilt tools and triggers to build your apps and workflows.
-With connectors, you can access various services (both within the Microsoft ecosystem and outside it) to perform a wide array of tasks automatically.
-There are
-many connectors
-available. Connectors include connections between and to Microsoft services like Office 365, SharePoint, and Dynamics 365, as well as connections to non-Microsoft services like Twitter, Google services, Salesforce, and more. Connectors are categorized as:
+act as proxies or "wrappers" around APIs. They enable Copilot Studio, Power Automate, Power Apps, and Azure Logic Apps to communicate with other apps and services. By using connectors, you can connect your accounts and use prebuilt tools and triggers to build your apps and workflows.
+By using connectors, you can access various services (both within the Microsoft ecosystem and outside it) to perform a wide array of tasks automatically.
+Many connectors are available. Connectors include connections between and to Microsoft services like Office 365, SharePoint, and Dynamics 365, as well as connections to non-Microsoft services like Twitter, Google services, Salesforce, and more. Connectors are categorized as:
 Prebuilt connectors
-, which are built-in connections to popular services available to use in Copilot Studio agents. These include:
+, which are built-in connections to popular services available to use in Copilot Studio agents. These connectors include:
 Standard connectors
 , such as SharePoint, which are included with all Copilot Studio plans.
 Premium connectors
@@ -41,9 +39,9 @@ Copilot Studio plans
 .
 Custom connectors
-, which let you connect to any publicly av
```

### 4. Agent Orchestration

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-plugin-actions
**Section:** Copilot Studio
**Classification:** Meaningful (Configuration instructions)

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits (`controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`)

**What Changed:**
```diff
--- +++ @@ -26,17 +26,19 @@ Add tools to custom agents
 Feedback
 Summarize this article for me
-Tools are the building blocks that enable your agent to interact with external systems. Tools expand the functionality of your agent, allowing it to perform various actions in response to user requests or autonomous triggers. Each tool represents a specific capability that your agent can perform. For example, you can equip your agent with tools that do things like:
+Tools are building blocks that let your agent interact with external systems. Tools expand what your agent can do, letting your agent perform various actions in response to user requests or autonomous triggers. Each tool represents a specific capability that your agent can perform. For example, you can equip your agent with tools that perform tasks like:
 Send emails using the Office 365 Outlook connector
 Check the current weather conditions and forecasts
 Read and write data from Dataverse
 Read and post messages to Teams
-Mechanisms for adding tools
+Mechanisms for adding tools to agents
 You can extend the capabilities of your custom agent by adding one or more
 tools
 . Your agent can use tools to respond to users automatically, using
 generative orchestration
-. You can also call tools explicitly from within a topic.
+. You can also call tools explicitly from within a
+topic
+.
 With
 generative orchestration
 (active by default), your agent can automatically select the most appropriate tool or topic, or search across knowledge, to respond to a user. This orchestration mode creates a more dynamic and intelligent conversation experience.
@@ -197,14 +199,14 @@ User intent derived from their message
 Available inputs and outputs
 Previous tool usage in the conversation
-Wen using generative mode, by default, tools return their information back to the agent. With the tool response, the agent can generate a contextual response to the user's query. Alternatively, you can instruct your tool to always respond i
```

### 5. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** Meaningful (Feature availability)

**Affected Playbooks:**
- `playbooks/control-implementations/2.7/troubleshooting.md` 

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates (`controls/pillar-2-management/2.10-patch-management-and-system-updates.md`)

**What Changed:**
```diff
--- +++ @@ -65,9 +65,7 @@ to break down complex tasks across specialized agents, improving accuracy and speeding up endâtoâend automation. Enhance your agents by linking them to other agentsâeither within your environment or external sources like
 Microsoft Fabric
 data agentsâfor modular, task-specific functionality.
-(Preview)
-Add tool groups to agents
-for faster setup. Quickly equip your agents with curated sets of tools from Outlook and SharePoint connectors in one step. This streamlines setup, reduces errors, and ensures consistent, reliable orchestration.
+(Preview) Add tool groups to agents for faster setup. Quickly equip your agents with curated sets of tools from Outlook and SharePoint connectors in one step. This streamlines setup, reduces errors, and ensures consistent, reliable orchestration.
 Copy agents from
 Microsoft 365 Copilot to Copilot Studio
 . Easily move agents you created in Microsoft 365 Copilot into Copilot Studio to unlock advanced capabilities like multi-step workflows, custom integrations, and broader deployment options.

```

### 6. Visual Governance Guide

**URL:** https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-visual-map
**Section:** Agent Essentials & Agent 365 SDK (Preview)
**Classification:** Meaningful (UI element names)

**Affected Controls:**
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization (`controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`)
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard (`controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`)

**What Changed:**
```diff
--- +++ @@ -0,0 +1,83 @@+Table of contents
+Exit editor mode
+Ask Learn
+Ask Learn
+Focus mode
+Table of contents
+Read in English
+Add
+Add to plan
+Edit
+Share via
+Facebook
+x.com
+LinkedIn
+Email
+Print
+Note
+Access to this page requires authorization. You can try
+signing in
+or
+changing directories
+.
+Access to this page requires authorization. You can try
+changing directories
+.
+Microsoft 365 Copilot agents visual guide
+Feedback
+Summarize this article for me
+To help understand the structure and flow of the
+Microsoft 365 Copilot Agent Management Essentials checklist
+, you can view the visual guide. This mind map provides a graphical representation of the key concepts and actions outlined in the checklist, making it easier to understand relationships between sections and navigate the framework at a glance.
+Each branch of the mind map corresponds to a major heading in the checklist, with subbranches breaking down detailed steps, considerations, and best practices. By presenting the content visually, the mind map serves as a quick reference tool for planning, implementing, and validating Copilot agents within your organization.
+An image of the relevant portion of the mind map is included in each section of this article. However, to view the entire mind map and access the related links, download the Microsoft 365 Copilot agents visual guide PDF.
+Download
+:
+Microsoft 365 Copilot agents visual guide PDF
+Manage Microsoft 365 Copilot agent access and availability policies
+Agent policies refer to the tenant settings you can make as an administrator in the Copilot Control System within Microsoft 365 admin center. Choose how you manage access to agents, as well as share and publish agents. For more information, see
+Microsoft 365 agents deployment checklist
+.
+Choose the right Copilot Studio experience
+Members of your organization can create agents using different methods that allow different capabilities. For more information, see
+Microsoft 365 agent
```

### 7. Deployment Checklist

**URL:** https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-checklist
**Section:** Agent Essentials & Agent 365 SDK (Preview)
**Classification:** Meaningful (UI element names)

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels (`controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`)
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization (`controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`)
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI (`controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`)
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA (`controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`)
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking (`controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`)
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management (`controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`)
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard (`controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`)

**What Changed:**
```diff
--- +++ @@ -0,0 +1,305 @@+Table of contents
+Exit editor mode
+Ask Learn
+Ask Learn
+Focus mode
+Table of contents
+Read in English
+Add
+Add to plan
+Edit
+Share via
+Facebook
+x.com
+LinkedIn
+Email
+Print
+Note
+Access to this page requires authorization. You can try
+signing in
+or
+changing directories
+.
+Access to this page requires authorization. You can try
+changing directories
+.
+Microsoft 365 agents deployment checklist
+Feedback
+Summarize this article for me
+This checklist is intended to assist admins with the successful deployment of Copilot agent governance. This checklisdt provides a comprehensive guide to help you understand, set up, manage, and deploy agents.
+Required administrators for the engagement
+:
+Microsoft 365 admin
+- Setup Copilot agent and connectors settings.
+Microsoft Power Platform admin
+- Setup Copilot Studio policies and settings.
+Microsoft 365 Search admin
+- Setup Microsoft 365 Graph connector configurations.
+Microsoft Azure admin
+- Setup Azure subscription configurations.
+Deployment phases
+:
+Downloadable resources
+:
+Microsoft 365 Copilot agents blueprint
+Microsoft 365 Copilot agents visual guide
+Manage Microsoft 365 Copilot agent access and availability policies
+Agent policies refer to the tenant settings you can make as an administrator in the Copilot Control System within Microsoft 365 admin center. Agent policies relate to the available settings for all agents in your tenant.
+Step
+Task
+Description
+Administrator
+1
+Manage access to Microsoft 365 Copilot agents
+Control how your users interact with agents:
+Choose who can access agents
+Choose which type of agents users are allowed to install
+Copilot administrator, SharePoint administrator, Copilot Studio administrator
+2
+Share and publish Microsoft 365 Copilot agents
+Agent sharing methods:
+Sideload agents for personal use
+Shared agent with others
+Publish custom agents to your organization
+Submit agents to the marketplace
+Copilot administrator, Sha
```

### 8. Deployment Blueprint

**URL:** https://learn.microsoft.com/en-us/copilot/microsoft-365/agent-essentials/m365-agents-blueprint
**Section:** Agent Essentials & Agent 365 SDK (Preview)
**Classification:** Meaningful (UI element names)

**Affected Controls:**
- Control 2.3: Control 2.3: Change Management and Release Planning (`controls/pillar-2-management/2.3-change-management-and-release-planning.md`)
- Control 2.1: Control 2.1: Managed Environments (`controls/pillar-2-management/2.1-managed-environments.md`)
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA (`controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`)

**What Changed:**
```diff
--- +++ @@ -0,0 +1,79 @@+Table of contents
+Exit editor mode
+Ask Learn
+Ask Learn
+Focus mode
+Table of contents
+Read in English
+Add
+Add to plan
+Edit
+Share via
+Facebook
+x.com
+LinkedIn
+Email
+Print
+Note
+Access to this page requires authorization. You can try
+signing in
+or
+changing directories
+.
+Access to this page requires authorization. You can try
+changing directories
+.
+Microsoft 365 Copilot agents deployment blueprint
+Feedback
+Summarize this article for me
+This deployment blueprint helps you enable agents in
+Microsoft 365 Copilot
+at scale, while ensuring data security and governance, managing access and costs, and measuring adoption and impact.
+Note
+This blueprint is scoped primarily to agents created in the
+Agent Builder
+experience using the Microsoft 365 Copilot app.
+The primary challenges when enabling Microsoft 365 Copilot agents include the following:
+Security and governance concerns
+- Your organization can address oversharing, data protection, and compliance risks by implementing robust security and governance controls to safely enable agents in Microsoft 365 Copilot.
+Deployment complexity
+- Agents in Microsoft 365 Copilot introduce new admin tools and processes. This guidance can help address user enablement and cost management complexity.
+Visibility and impact gaps
+- By reviewing and acting on agent data, you can better measure success. Agent data can also provide usage to manage costs and help assess business value.
+By addressing these challenges, you can better drive innovation while maintaining security, control, and visibility. This blueprint can help, by providing shorter, actionable, and prescriptive guidance.
+In this deployment blueprint, we provide a recommended approach to address concerns throughout a Microsoft 365 Copilot agent deployment. The blueprint breaks the deployment into three phases:
+Prepare
+â Set the foundation before enabling agents.
+Deploy
+â Enable agents in a controlled manner.
+Manage

```

### 9. Agent 365 SDK Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/developer/
**Section:** Agent Essentials & Agent 365 SDK (Preview)
**Classification:** Meaningful (UI element names)

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance (`controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`)
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance (`controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`)
- Control 1.2: Control 1.2: Agent Registry and Integrated Apps Management (`controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md`)
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation (`controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`)
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring (`controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`)

**What Changed:**
```diff
--- +++ @@ -0,0 +1,102 @@+Table of contents
+Exit editor mode
+Ask Learn
+Ask Learn
+Focus mode
+Table of contents
+Read in English
+Add
+Add to plan
+Edit
+Share via
+Facebook
+x.com
+LinkedIn
+Email
+Print
+Note
+Access to this page requires authorization. You can try
+signing in
+or
+changing directories
+.
+Access to this page requires authorization. You can try
+changing directories
+.
+Microsoft Agent 365 SDK and CLI
+Feedback
+Summarize this article for me
+Important
+You need to be part of the
+Frontier preview program
+to get
+early access
+to Microsoft Agent 365. Frontier connects you directly with Microsoftâs latest AI innovations. Frontier previews are subject to the existing preview terms of your customer agreements. As these features are still in development, their availability and capabilities may change over time.
+Agent 365 SDK
+Use the
+Agent 365 SDK
+to extend agents built using any agent SDK or platform, with enterpriseâgrade identity, observability, notifications, security, and governed access to Microsoft 365 data.
+Agents have unique identities. People invoke them using common gestures (such as
+@mentions)
+in apps that enterprise users typically operate in (such as Teams, Word, Outlook, and more). They demonstrate observable behaviors that build trust, take auditable actions, and do so via secure access to tools and data.
+With the Agent 365 SDK, agents can:
+Use Entra-backed Agent Identity with their own user resources like mailbox for secure authentication and controlled access to tools and data.
+Receive and respond to notifications from Teams, Outlook, Word comments, and emailsâjust like a human participant in Microsoft 365 apps.
+Gain full observability via
+Open Telemetry
+, enabling audited, traceable agent interactions, inference events, and tool usage.
+Invoke governed Model Context Protocol (MCP) servers to access Microsoft 365 workloads (for example, Mail, Calendar, SharePoint, Teams) under admin control.
+Function within an 
```

### 10. Blueprint Registration

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/developer/registration
**Section:** Agent Essentials & Agent 365 SDK (Preview)
**Classification:** Meaningful (UI element names)

**Affected Controls:**
- Control 1.2: Control 1.2: Agent Registry and Integrated Apps Management (`controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md`)

**What Changed:**
```diff
--- +++ @@ -0,0 +1,470 @@+Table of contents
+Exit editor mode
+Ask Learn
+Ask Learn
+Focus mode
+Table of contents
+Read in English
+Add
+Add to plan
+Edit
+Share via
+Facebook
+x.com
+LinkedIn
+Email
+Print
+Note
+Access to this page requires authorization. You can try
+signing in
+or
+changing directories
+.
+Access to this page requires authorization. You can try
+changing directories
+.
+Setup Agent blueprint
+Feedback
+Summarize this article for me
+Important
+You need to be part of the
+Frontier preview program
+to get
+early access
+to Microsoft Agent 365. Frontier connects you directly with Microsoftâs latest AI innovations. Frontier previews are subject to the existing preview terms of your customer agreements. As these features are still in development, their availability and capabilities may change over time.
+The agent blueprint defines your agent's identity, permissions, and infrastructure requirements. Create every agent instance from this agent blueprint.
+For more information about Agent 365 Identity, see
+Agent 365 Identity
+.
+Prerequisites
+Before you begin, ensure you have the following prerequisites:
+Agent 365 CLI
+- See
+Agent 365 CLI installation
+.
+Required permissions:
+Valid tenant user with one of the following roles:
+Global Administrator
+Agent ID Administrator
+Agent ID Developer
+Access to an Azure subscription with permissions to create resources
+Valid
+a365.config.json
+file in your working directory, set up via this step:
+Setting up Agent 365 config
+.
+Create agent blueprint
+Use the
+a365 setup
+command to create Azure resources and register your
+agent blueprint
+. The blueprint defines your agent's identity, permissions, and infrastructure requirements. This step establishes the foundation for deploying and running your agent in Azure.
+Run setup
+Run the setup command:
+a365 setup -h
+The command has various options. You can complete the entire setup in a single command by using
+a365 setup all
+or choose more granular op
```

### 11. Sensitivity Labels

**URL:** https://learn.microsoft.com/en-us/microsoft-365/compliance/sensitivity-labels
**Section:** Microsoft Purview
**Classification:** Meaningful (Configuration instructions)

**What Changed:**
```diff
--- +++ @@ -29,10 +29,10 @@ Microsoft 365 licensing guidance for security & compliance
 .
 Note
-If you're looking for information about sensitivity labels that you see and can select in your Office apps, see
-Apply sensitivity labels to your files and email in Office
-.
-The information on this page is for IT administrators who can create and configure those labels.
+If you're looking for information about sensitivity labels that you see and can select in your Office apps, check their documentation. For example,
+Apply sensitivity labels to your files
+.
+The information on this page is for IT administrators who can create and configure those labels by using the Microsoft Purview management solution.
 To get their work done, people in your organization collaborate with others both inside and outside the organization. This means that content no longer stays behind a firewallâit can roam everywhere, across devices, apps, and services. And when it roams, you want it to do so in a secure, protected way that meets your organization's business and compliance policies.
 Sensitivity labels from Microsoft Purview Information Protection let you classify and protect your organization's data, while making sure that user productivity and their ability to collaborate isn't hindered.
 The following example from Excel shows how users might see an applied sensitivity label from the window bar, and how they can easily change the label by using the
@@ -54,11 +54,11 @@ Extend SharePoint protection when files are downloaded
 when you configure a default sensitivity label for SharePoint document libraries and select the option to extend protection for unencrypted files. Then, when these files are downloaded, the current SharePoint permissions travel with the labeled file.
 Protect content in Office apps across different platforms and devices.
-Supported by Word, Excel, PowerPoint, and Outlook on the Office desktop apps and Office for the web. Supported on Windows, macOS, iOS, and Andr
```

### 12. Sensitivity Labels Overview

**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels
**Section:** Microsoft Purview
**Classification:** Meaningful (Configuration instructions)

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels (`controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`)
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions (`controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`)

**What Changed:**
```diff
--- +++ @@ -29,10 +29,10 @@ Microsoft 365 licensing guidance for security & compliance
 .
 Note
-If you're looking for information about sensitivity labels that you see and can select in your Office apps, see
-Apply sensitivity labels to your files and email in Office
-.
-The information on this page is for IT administrators who can create and configure those labels.
+If you're looking for information about sensitivity labels that you see and can select in your Office apps, check their documentation. For example,
+Apply sensitivity labels to your files
+.
+The information on this page is for IT administrators who can create and configure those labels by using the Microsoft Purview management solution.
 To get their work done, people in your organization collaborate with others both inside and outside the organization. This means that content no longer stays behind a firewallâit can roam everywhere, across devices, apps, and services. And when it roams, you want it to do so in a secure, protected way that meets your organization's business and compliance policies.
 Sensitivity labels from Microsoft Purview Information Protection let you classify and protect your organization's data, while making sure that user productivity and their ability to collaborate isn't hindered.
 The following example from Excel shows how users might see an applied sensitivity label from the window bar, and how they can easily change the label by using the
@@ -54,11 +54,11 @@ Extend SharePoint protection when files are downloaded
 when you configure a default sensitivity label for SharePoint document libraries and select the option to extend protection for unencrypted files. Then, when these files are downloaded, the current SharePoint permissions travel with the labeled file.
 Protect content in Office apps across different platforms and devices.
-Supported by Word, Excel, PowerPoint, and Outlook on the Office desktop apps and Office for the web. Supported on Windows, macOS, iOS, and Andr
```

### 13. eDiscovery

**URL:** https://learn.microsoft.com/en-us/purview/ediscovery
**Section:** Microsoft Purview
**Classification:** Meaningful (Deprecation notice)

**Affected Controls:**
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions (`controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`)
- Control 1.9: Control 1.9: Data Retention and Deletion Policies (`controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`)

**What Changed:**
```diff
--- +++ @@ -26,17 +26,15 @@ Microsoft Purview eDiscovery legacy solutions
 Feedback
 Summarize this article for me
-Important
-The classic eDiscovery experiences were
-retired on August 31, 2025
-. This retirement includes classic
+Caution
+Microsoft retired all classic eDiscovery experiences on August 31, 2025. This retirement includes classic
 Content Search
 , classic
 eDiscovery (Standard)
 , and classic
 eDiscovery (Premium)
-. These options aren't available as an experience option in the Microsoft Purview portal.
-Unless you're working directly with Microsoft when using these legacy features for specific short-term transition scenarios, use the guidance for the
+.
+The guidance in this article only applies to organizations hosted in Microsoft 365 operated by 21Vianet (China). If your organization isn't hosted by 21Vianet, use the guidance for the
 new eDiscovery experience
 in the
 Microsoft Purview portal

```

### 14. Create Cases

**URL:** https://learn.microsoft.com/en-us/purview/ediscovery-create-and-manage-cases
**Section:** Microsoft Purview
**Classification:** Meaningful (Deprecation notice)

**Affected Controls:**
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions (`controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`)

**What Changed:**
```diff
--- +++ @@ -26,17 +26,15 @@ Create and manage an eDiscovery (Premium) case
 Feedback
 Summarize this article for me
-Important
-The classic eDiscovery experiences were
-retired on August 31, 2025
-. This retirement includes classic
+Caution
+Microsoft retired all classic eDiscovery experiences on August 31, 2025. This retirement includes classic
 Content Search
 , classic
 eDiscovery (Standard)
 , and classic
 eDiscovery (Premium)
-. These options aren't available as an experience option in the Microsoft Purview portal.
-Unless you're working directly with Microsoft when using these legacy features for specific short-term transition scenarios, use the guidance for the
+.
+The guidance in this article only applies to organizations hosted in Microsoft 365 operated by 21Vianet (China). If your organization isn't hosted by 21Vianet, use the guidance for the
 new eDiscovery experience
 in the
 Microsoft Purview portal

```

### 15. KeyQL Reference

**URL:** https://learn.microsoft.com/en-us/purview/ediscovery-keyword-queries-and-search-conditions
**Section:** Microsoft Purview
**Classification:** Meaningful (Deprecation notice)

**Affected Controls:**
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions (`controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`)

**What Changed:**
```diff
--- +++ @@ -26,17 +26,15 @@ Keyword queries and search conditions for eDiscovery
 Feedback
 Summarize this article for me
-Important
-The classic eDiscovery experiences were
-retired on August 31, 2025
-. This retirement includes classic
+Caution
+Microsoft retired all classic eDiscovery experiences on August 31, 2025. This retirement includes classic
 Content Search
 , classic
 eDiscovery (Standard)
 , and classic
 eDiscovery (Premium)
-. These options aren't available as an experience option in the Microsoft Purview portal.
-Unless you're working directly with Microsoft when using these legacy features for specific short-term transition scenarios, use the guidance for the
+.
+The guidance in this article only applies to organizations hosted in Microsoft 365 operated by 21Vianet (China). If your organization isn't hosted by 21Vianet, use the guidance for the
 new eDiscovery experience
 in the
 Microsoft Purview portal

```

### 16. eDiscovery Holds

**URL:** https://learn.microsoft.com/en-us/purview/ediscovery-create-holds
**Section:** Microsoft Purview
**Classification:** Meaningful (Deprecation notice)

**Affected Controls:**
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions (`controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`)
- Control 1.9: Control 1.9: Data Retention and Deletion Policies (`controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`)

**What Changed:**
```diff
--- +++ @@ -26,17 +26,15 @@ Create eDiscovery holds in an eDiscovery case
 Feedback
 Summarize this article for me
-Important
-The classic eDiscovery experiences were
-retired on August 31, 2025
-. This retirement includes classic
+Caution
+Microsoft retired all classic eDiscovery experiences on August 31, 2025. This retirement includes classic
 Content Search
 , classic
 eDiscovery (Standard)
 , and classic
 eDiscovery (Premium)
-. These options aren't available as an experience option in the Microsoft Purview portal.
-Unless you're working directly with Microsoft when using these legacy features for specific short-term transition scenarios, use the guidance for the
+.
+The guidance in this article only applies to organizations hosted in Microsoft 365 operated by 21Vianet (China). If your organization isn't hosted by 21Vianet, use the guidance for the
 new eDiscovery experience
 in the
 Microsoft Purview portal

```

### 17. Authentication Contexts

**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-cloud-apps#authentication-context
**Section:** Microsoft Entra ID
**Classification:** Meaningful (Portal references)

**Affected Controls:**
- Control 1.23: Control 1.23: Step-Up Authentication for AI Agent Operations (`controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md`)

**What Changed:**
```diff
--- +++ @@ -49,19 +49,19 @@ Admins can assign a Conditional Access policy to Microsoft cloud apps if the service principal appears in their tenant, except for Microsoft Graph. Microsoft Graph functions as an umbrella resource. Use
 Audience Reporting
 to see the underlying services and target those services in your policies. Some apps like
-Office 365
+Microsoft 365/Office 365
 and
 Windows Azure Service Management API
 include multiple related child apps or services. When new Microsoft cloud applications are created, they appear in the app picker list as soon as the service principal is created in the tenant.
 Office 365
-Microsoft 365 offers cloud-based productivity and collaboration services like Exchange, SharePoint, and Microsoft Teams. Microsoft 365 cloud services are deeply integrated to ensure smooth and collaborative experiences. This integration might cause confusion when creating policies because some apps, like Microsoft Teams, depend on others, like SharePoint or Exchange.
-The Office 365 app grouping makes it possible to target these services all at once. We recommend using the Office 365 grouping, instead of targeting individual cloud apps to avoid issues with
+Microsoft 365 offers cloud-based productivity and collaboration services like Exchange, SharePoint, and Microsoft Teams. In Conditional Access, the Microsoft 365 suite of applications appears under 'Office 365'. Microsoft 365 cloud services are deeply integrated to ensure smooth and collaborative experiences. This integration might cause confusion when creating policies because some apps, like Microsoft Teams, depend on others, like SharePoint or Exchange.
+The Office 365 app grouping in Conditional Access makes it possible to target these services all at once. We recommend using the Microsoft 365 grouping, instead of targeting individual cloud apps to avoid issues with
 service dependencies
 .
-Targeting this group of applications helps to avoid issues that might arise because of inconsistent 
```

### 18. Admin Roles

**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Section:** Microsoft Entra ID
**Classification:** Meaningful (Portal references)

**What Changed:**
```diff
--- +++ @@ -753,7 +753,7 @@ Users in this role can create and manage all aspects of attack simulation creation, launch/scheduling of a simulation, and the review of simulation results. Members of this role have this access for all simulations in the tenant.
 For more information, see these articles:
 Microsoft Defender for Office 365 permissions in the Microsoft Defender portal
-Permissions in the Microsoft Purview compliance portal
+Permissions in the Microsoft Purview portal
 Actions
 Description
 microsoft.office365.protectionCenter/attackSimulator/payload/allProperties/allTasks
@@ -1397,12 +1397,12 @@ microsoft.office365.serviceHealth/allEntities/allTasks
 Read and configure Service Health in the Microsoft 365 admin center
 Compliance Administrator
-Users with this role have permissions to manage compliance-related features in the Microsoft Purview compliance portal, Microsoft 365 admin center, Azure, and Microsoft 365 Defender portal. Assignees can also manage all features within the Exchange admin center and create support tickets for Azure and Microsoft 365. For more information, see
+Users with this role have permissions to manage compliance-related features in the Microsoft Purview portal, Microsoft 365 admin center, Azure, and Microsoft 365 Defender portal. Assignees can also manage all features within the Exchange admin center and create support tickets for Azure and Microsoft 365. For more information, see
 Roles and role groups in Microsoft Defender for Office 365 and Microsoft Purview compliance
 .
 In
 Can do
-Microsoft Purview compliance portal
+Microsoft Purview portal
 Protect and manage your organization's data across Microsoft 365 services
 Manage compliance alerts
 Microsoft Purview Compliance Manager
@@ -1437,12 +1437,12 @@ microsoft.office365.webPortal/allEntities/standard/read
 Read basic properties on all resources in the Microsoft 365 admin center
 Compliance Data Administrator
-Users with this role have permissions to track data in the Mic
```

### 19. Restricted SharePoint Search

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search
**Section:** SharePoint Administration
**Classification:** Meaningful (Feature availability)

**Affected Controls:**
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery (`controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`)

**What Changed:**
```diff
--- +++ @@ -47,7 +47,7 @@ Prevent sites from showing up in organization-wide search results and Copilot experiences until your admins or site owners can check the permissions on the site content;
 Honor existing site permissions, and let site owners manage individual site permissions.
 If Restricted SharePoint Search is enabled, the customer's experience is impacted in the following ways:
-Search results are limited to sites on the allowed list, usersâ frequently visited sites, sites that users already have permissions to, and usersâ recently accessed files. Turning on this feature impacts the overall search experience, even for non-Copilot users.
+Search results are limited to sites on the allowed list, users' frequently visited sites, sites that users already have permissions to, and users' recently accessed files. Turning on this feature impacts the overall search experience, even for non-Copilot users.
 Copilot has less information available to reference, which may impact its ability to provide accurate and comprehensive responses.
 Remember, whether you have enabled Restricted SharePoint Search, users in your organization are always able to interact with files and content they own or that they have previously accessed in Copilot .
 How does Restricted SharePoint Search work?
@@ -65,8 +65,8 @@ Restricted SharePoint Search is off by default. If you decide to enable it, Copilot and non-Copilot users are able to find and use content from:
 An allowed list of curated SharePoint sites set up by admins (with
 up to 100 SharePoint sites
-), honoring sitesâ existing permissions.
-Usersâ OneDrive files, chats, emails, calendars they have access to.
+), honoring sites' existing permissions.
+Users' OneDrive files, chats, emails, calendars they have access to.
 Files from their frequently visited SharePoint sites.
 Files that were shared directly with the users.
 Files that the users viewed, edited, or created.
@@ -76,9 +76,9 @@ The following diagram shows an examp
```

### 20. Advanced Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Section:** SharePoint Administration
**Classification:** Meaningful (Feature availability)

**Affected Playbooks:**
- `playbooks/control-implementations/4.6/troubleshooting.md` 
- `playbooks/control-implementations/4.5/troubleshooting.md` 

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification (`controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`)
- Control 4.6: Control 4.6: Grounding Scope Governance (`controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`)
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring (`controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`)
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery (`controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`)
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions (`controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`)

**What Changed:**
```diff
--- +++ @@ -48,7 +48,7 @@ with access to the
 SharePoint admin center
 . Some features can also be used by site owners.
-With the right licensing in place, you can take full advantage of SharePoint Advanced Managementâs three core capabilities: preventing content sprawl, managing the content lifecycle, and streamlining permissions and access management for SharePoint and OneDrive sites. The following sections provide a detailed look at each area, helping you understand how SAM empowers you to govern your organizationâs information effectively and securely.
+With the right licensing in place, you can take full advantage of SharePoint Advanced Management's three core capabilities: preventing content sprawl, managing the content lifecycle, and streamlining permissions and access management for SharePoint and OneDrive sites. The following sections provide a detailed look at each area, helping you understand how SAM empowers you to govern your organization's information effectively and securely.
 What is content sprawl and how can you prevent it?
 Content sprawl happens when digital files and information accumulate across your organization without effective oversight. This can make it harder to find what you need, increase storage costs, and create security or compliance risks. To help you prevent content sprawl, SharePoint Advanced Management offers three key features:
 Site ownership policy:
@@ -97,7 +97,7 @@ The
 Recent SharePoint admin actions
 policy lets you review and monitor the last 30 changes you've made to a SharePoint site's properties within the last 30 days in the SharePoint admin center. This feature only shows changes made by you and not other administrators.
-How can you manage permissions and access
+How can you manage permissions and access?
 Microsoft 365 collaboration and AI experiences depend on strong permission and access controls for SharePoint and OneDrive. SharePoint Advanced Management (SAM) provides a suite of features to help you govern 
```

### 21. Microsoft Sentinel

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/overview
**Section:** Azure Services
**Classification:** Meaningful (Portal references)

**Affected Controls:**
- Control 3.9: Control 3.9: Microsoft Sentinel Integration (`controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md`)

**What Changed:**
```diff
--- +++ @@ -123,9 +123,9 @@ Microsoft Sentinel is
 generally available in the Microsoft Defender portal
 , including for customers without Microsoft Defender XDR or an E5 license. This means that you can use Microsoft Sentinel in the Defender portal even if you aren't using other Microsoft Defender services.
-Starting in
-July 2026
-, Microsoft Sentinel will be supported in the Defender portal only, and any remaining customers using the Azure portal will be automatically redirected.
+After
+March 31, 2027
+, Microsoft Sentinel will no longer be supported in the Azure portal and will be available only in the Microsoft Defender portal.
 If you're currently using Microsoft Sentinel in the Azure portal, we recommend that you start planning your transition to the Defender portal now to ensure a smooth transition and take full advantage of the
 unified security operations experience offered by Microsoft Defender
 .
@@ -139,7 +139,7 @@ onboarding the first workspace in their tenant to Microsoft Sentinel
 .
 Starting
-July, 2025
+July 2025
 , such new customers who also have the permissions of a subscription
 Owner
 or a

```

### 22. Data Connectors

**URL:** https://learn.microsoft.com/azure/sentinel/connect-data-sources
**Section:** Azure Services
**Classification:** Meaningful (Portal references)

**What Changed:**
```diff
--- +++ @@ -44,9 +44,9 @@ Important
 Microsoft Sentinel is generally available in the Microsoft Defender portal
 , including for customers without Microsoft Defender XDR or an E5 license.
-Starting in
-July 2026
-, all customers using Microsoft Sentinel in the Azure portal will be
+After
+March 31, 2027
+, Microsoft Sentinel will no longer be supported in the Azure portal and will be available only in the Microsoft Defender portal. All customers using Microsoft Sentinel in the Azure portal will be
 redirected to the Defender portal and will use Microsoft Sentinel in the Defender portal only
 . Starting in
 July 2025

```

### 23. Custom Analytics Rules

**URL:** https://learn.microsoft.com/azure/sentinel/detect-threats-custom
**Section:** Azure Services
**Classification:** Meaningful (Portal references)

**What Changed:**
```diff
--- +++ @@ -48,9 +48,9 @@ Important
 Microsoft Sentinel is generally available in the Microsoft Defender portal
 , including for customers without Microsoft Defender XDR or an E5 license.
-Starting in
-July 2026
-, all customers using Microsoft Sentinel in the Azure portal will be
+After
+March 31, 2027
+, Microsoft Sentinel will no longer be supported in the Azure portal and will be available only in the Microsoft Defender portal. All customers using Microsoft Sentinel in the Azure portal will be
 redirected to the Defender portal and will use Microsoft Sentinel in the Defender portal only
 . Starting in
 July 2025

```

### 24. Built-in Analytics

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-built-in
**Section:** Azure Services
**Classification:** Meaningful (Portal references)

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging (`controls/pillar-1-security/1.21-adversarial-input-logging.md`)

**What Changed:**
```diff
--- +++ @@ -56,9 +56,9 @@ Important
 Microsoft Sentinel is generally available in the Microsoft Defender portal
 , including for customers without Microsoft Defender XDR or an E5 license.
-Starting in
-July 2026
-, all customers using Microsoft Sentinel in the Azure portal will be
+After
+March 31, 2027
+, Microsoft Sentinel will no longer be supported in the Azure portal and will be available only in the Microsoft Defender portal. All customers using Microsoft Sentinel in the Azure portal will be
 redirected to the Defender portal and will use Microsoft Sentinel in the Defender portal only
 . Starting in
 July 2025

```

### 25. Workbooks

**URL:** https://learn.microsoft.com/azure/sentinel/monitor-your-data
**Section:** Azure Services
**Classification:** Meaningful (Portal references)

**What Changed:**
```diff
--- +++ @@ -32,9 +32,9 @@ Important
 Microsoft Sentinel is generally available in the Microsoft Defender portal
 , including for customers without Microsoft Defender XDR or an E5 license.
-Starting in
-July 2026
-, all customers using Microsoft Sentinel in the Azure portal will be
+After
+March 31, 2027
+, Microsoft Sentinel will no longer be supported in the Azure portal and will be available only in the Microsoft Defender portal. All customers using Microsoft Sentinel in the Azure portal will be
 redirected to the Defender portal and will use Microsoft Sentinel in the Defender portal only
 . Starting in
 July 2025

```

### 26. Automation Rules

**URL:** https://learn.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules
**Section:** Azure Services
**Classification:** Meaningful (Portal references)

**What Changed:**
```diff
--- +++ @@ -30,9 +30,9 @@ Important
 Microsoft Sentinel is generally available in the Microsoft Defender portal
 , including for customers without Microsoft Defender XDR or an E5 license.
-Starting in
-July 2026
-, all customers using Microsoft Sentinel in the Azure portal will be
+After
+March 31, 2027
+, Microsoft Sentinel will no longer be supported in the Azure portal and will be available only in the Microsoft Defender portal. All customers using Microsoft Sentinel in the Azure portal will be
 redirected to the Defender portal and will use Microsoft Sentinel in the Defender portal only
 . Starting in
 July 2025

```

### 27. Key Vault Private Endpoints

**URL:** https://learn.microsoft.com/en-us/azure/key-vault/general/private-link-service
**Section:** Azure Services
**Classification:** Meaningful (Configuration instructions)

**Affected Controls:**
- Control 1.20: Control 1.20: Network Isolation and Private Connectivity (`controls/pillar-1-security/1.20-network-isolation-private-connectivity.md`)

**What Changed:**
```diff
--- +++ @@ -107,7 +107,7 @@ az account set --subscription {SUBSCRIPTION ID} # Select your Azure Subscription
 az group create -n {RESOURCE GROUP} -l {REGION} # Create a new Resource Group
 az provider register -n Microsoft.KeyVault # Register KeyVault as a provider
-az keyvault create -n {VAULT NAME} -g {RG} -l {REGION} # Create a Key Vault
+az keyvault create -n {VAULT NAME} -g {RG} -l {REGION} --enable-rbac-authorization true # Create a Key Vault
 az keyvault update -n {VAULT NAME} -g {RG} --default-action deny # Turn on Key Vault Firewall
 az network vnet create -g {RG} -n {vNet NAME} -location {REGION} # Create a Virtual Network
 
@@ -196,7 +196,7 @@ Link Virtual Network to Private DNS Zone
 Check to make sure the Private DNS Zone isn't missing an A record for the key vault.
 Navigate to the Private DNS Zone page.
-Select Overview and check if there's an A record with the simple name of your key vault (i.e. fabrikam). Don't specify any suffix.
+Select Overview and check if there's an A record with the simple name of your key vault (for example, fabrikam). Don't specify any suffix.
 Make sure you check the spelling, and either create or fix the A record. You can use a TTL of 600 (10 mins).
 Make sure you specify the correct private IP address.
 Check to make sure the A record has the correct IP Address.
@@ -232,6 +232,9 @@ Azure Private Link
 Learn more about
 Azure Key Vault
+Diagnose private links configuration issues
+Configure network security for Azure Key Vault
+Secure your Azure Key Vault
 Feedback
 Was this page helpful?
 Yes

```

### 28. AI Content Safety

**URL:** https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
**Section:** Azure Services
**Classification:** Meaningful (Feature availability)

**Affected Controls:**
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection (`controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`)

**What Changed:**
```diff
--- +++ @@ -26,8 +26,14 @@ What is Azure AI Content Safety?
 Feedback
 Summarize this article for me
-Azure AI Content Safety is an AI service that detects harmful user-generated and AI-generated content in applications and services. Azure AI Content Safety includes text and image APIs that allow you to detect material that is harmful. The interactive Content Safety Studio allows you to view, explore, and try out sample code for detecting harmful content across different modalities.
+Azure AI Content Safety is an AI service that detects harmful user-generated and AI-generated content in applications and services. Azure AI Content Safety includes text and image APIs that allow you to detect material that's harmful. The interactive Content Safety Studio allows you to view, explore, and try out sample code for detecting harmful content across different modalities.
 Content filtering software can help your app comply with regulations or maintain the intended environment for your users.
+Prerequisites
+To use Azure AI Content Safety, you need:
+An Azure subscription -
+Create one for free
+A Content Safety resource created in a
+supported region
 This documentation contains the following article types:
 Concepts
 provide in-depth explanations of the service functionality and features.
@@ -35,6 +41,58 @@ are getting-started instructions to guide you through making requests to the service.
 How-to guides
 contain instructions for using the service in more specific or customized ways.
+Content moderation features
+Content Safety provides several APIs for different moderation needs:
+AI safety and prompt protection
+Feature
+Purpose
+Concepts guide
+Get started
+Prompt Shields
+Scans text for the risk of a User input attack on a Large Language Model.
+Prompt Shields concepts
+Quickstart
+Groundedness detection
+(preview)
+Detects whether the text responses of large language models (LLMs) are grounded in the source materials provided by the users.
+Groundedness detection conc
```

### 29. Device Control

**URL:** https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/device-control-overview
**Section:** Microsoft Defender
**Classification:** Meaningful (Portal references)

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP) (`controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`)

**What Changed:**
```diff
--- +++ @@ -116,7 +116,7 @@ Restrict USB devices and allow specific USB devices using ADMX templates in Intune
 .
 Control access to removable media using device control
-Device control for Defender for Endpoint provides finer grain access control to a subset of USB devices. Device control can only restrict access to Windows Portal Devices, Removable Media, CD/DVDs and Printers.
+Device control for Defender for Endpoint provides finer grain access control to a subset of USB devices. Device control can only restrict access to Windows Portable Devices, Removable Media, CD/DVDs and Printers.
 Note
 On Windows, the term
 removable media devices

```

### 30. M365 Licensing Guidance

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance
**Section:** Licensing
**Classification:** Meaningful (Compliance features)

**What Changed:**
```diff
--- +++ @@ -23,7 +23,7 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Microsoft 365 guidance for security & compliance
+Microsoft 365 Security
 Feedback
 Summarize this article for me
 For the purposes of this article, a tenant-level service is an online service that is activated in part or in full for all users in the tenant (standalone license and/or as part of a Microsoft 365 or Office 365 plan). Appropriate subscription licenses are required for customer use of online services. To see the options for licensing your users to benefit from Microsoft 365 compliance features, download theâ¯
@@ -34,529 +34,23 @@ Some tenant services aren't currently capable of limiting benefits to specific users. To review the terms and conditions governing the use of Microsoft products and Professional Services acquired through Microsoft Licensing programs, see theâ¯
 Product Terms
 .
-Microsoft Entra ID Governance
-Microsoft Entra ID Governance allows you to balance your organization's need for security and employee productivity with the right processes and visibility. It uses entitlement management, access reviews, privileged identity management, and terms-of-use policies to ensure that the right people have the right access to the right resources.
-How do users benefit from the service?
-Microsoft Entra ID Governance increases users' productivity by making it easier to request access to apps, groups, and Microsoft Teams in one access package. Users can also be configured as approvers, without involving administrators. For access reviews, users can review memberships of groups with smart recommendations to take action on regular intervals.
-Which licenses provide the rights for a user to benefit from the service?
-The Microsoft Entra ID Governance capabilities are currently available in Microsoft Entra ID Governance and Microsoft Entra ID Governance Step Up for Microsoft Entra ID P2. These two products provide the rights for as many users as 
```

### 31. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** Meaningful (Portal references)

**What Changed:**
```diff
--- +++ @@ -86,7 +86,7 @@ 1
 Microsoft 365 E5 eDiscovery & Audit + Copilot
 1
-Microsoft 365 E5/A5/G5, Microsoft Purview Suite/EDU/GOV/FLW, Microsoft Defender + Purview Suite FLW, Microsoft 365 E5/A5/F5/G5 eDiscovery and Audit, Office 365 E5/A5/G5
+Microsoft 365 E5/A5/G5, Microsoft Purview Suite/EDU/GOV/FLW, Microsoft Defender + Purview Suite FLW, Microsoft 365 E5/A5/F5/G5 eDiscovery, and Audit, Office 365 E5/A5/G5
 Audit (Premium)
 Yes
 No
@@ -116,7 +116,7 @@ Microsoft Purview Communications Compliance
 Microsoft Purview Communication Compliance is an insider risk solution that helps you detect, capture, and act on inappropriate messages that can lead to potential data security or compliance incidents within your organization. Communication compliance evaluates text and image-based messages in Microsoft and third-party apps (Teams, Copilot for Microsoft 365, Viva Engage, Outlook, WhatsApp, etc.) for potential business policy violations including inappropriate sharing of sensitive information, threatening or harassing language as well as potential regulatory violations (such as stock and capital manipulations).
 Communication compliance's mission is to foster safe and compliant communications across customers' enterprise communication channels. With role-based access controls, human investigators can take remediation actions such as removing a message from Teams or notifying senders of potentially inappropriate conduct.
-Communication compliance uses machine learning models and keyword matching to identify messages containing potential business conduct or regulatory policy violations that are then reviewed by an investigator. Communication compliance cultivates user privacy with pseudonymization and responsible use of the product by providing role-based access controls.
+Communication compliance uses machine learning models and keyword matching to identify messages containing potential business conduct or regulatory policy violations that an investigator then review
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Connector Reference
**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Classification:** Minor (General content update)

---

### 2. Knowledge Sources
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Classification:** Minor (General content update)

---

### 3. Endpoint DLP
**URL:** https://learn.microsoft.com/en-us/microsoft-365/compliance/endpoint-dlp-learn-about
**Classification:** Minor (General content update)

---

### 4. Endpoint DLP Overview
**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Classification:** Minor (General content update)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/admin/wp-connectors | https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections-list |
| https://learn.microsoft.com/en-us/power-platform/admin/admin-activity-logging | https://learn.microsoft.com/en-us/power-platform/admin/activity-logging-auditing/activity-logs-power-platform-admin |
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-csat | https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness |
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-plugin-actions | https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent |
| https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-overview | https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-overview |
| https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-privacy | https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy |
| https://learn.microsoft.com/en-us/microsoft-365-copilot/microsoft-365-copilot-enable-users | https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-enable-users |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage | https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/dlp-learn-about-dlp | https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/dlp-create-deploy-policy | https://learn.microsoft.com/en-us/purview/dlp-create-deploy-policy |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/sensitivity-labels | https://learn.microsoft.com/en-us/purview/sensitivity-labels |
| https://learn.microsoft.com/en-us/purview/audit-log-search | https://learn.microsoft.com/en-us/purview/audit-search |
| https://learn.microsoft.com/en-us/purview/ai-microsoft-purview-considerations | https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/sensitive-information-type-learn-about | https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-learn-about |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/create-a-custom-sensitive-information-type | https://learn.microsoft.com/en-us/purview/sit-create-a-custom-sensitive-information-type |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/create-a-keyword-dictionary | https://learn.microsoft.com/en-us/purview/sit-create-a-keyword-dictionary |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/create-custom-sensitive-information-types-with-exact-data-match-based-classification | https://learn.microsoft.com/en-us/purview/sit-learn-about-exact-data-match-based-sits |
| https://learn.microsoft.com/en-us/purview/classifier-learn-about | https://learn.microsoft.com/en-us/purview/trainable-classifiers-learn-about |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/retention | https://learn.microsoft.com/en-us/purview/retention |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/create-retention-policies | https://learn.microsoft.com/en-us/purview/create-retention-policies |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/endpoint-dlp-learn-about | https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/encryption-sensitivity-labels | https://learn.microsoft.com/en-us/purview/encryption-sensitivity-labels |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/encryption | https://learn.microsoft.com/en-us/purview/encryption |
| https://learn.microsoft.com/purview/compliance-manager | https://learn.microsoft.com/en-us/purview/compliance-manager |
| https://learn.microsoft.com/purview/compliance-manager-assessments | https://learn.microsoft.com/en-us/purview/compliance-manager-assessments |
| https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-methods | https://learn.microsoft.com/en-us/entra/identity/authentication/overview-authentication |
| https://learn.microsoft.com/en-us/entra/identity/authentication/howto-authentication-passwordless-security-key | https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-enable-passkey-fido2 |
| https://learn.microsoft.com/en-us/sharepoint/information-barriers | https://learn.microsoft.com/en-us/purview/information-barriers-sharepoint |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/create-retention-policies#retaining-content-thats-in-sharepoint-sites | https://learn.microsoft.com/en-us/purview/create-retention-policies#retaining-content-thats-in-sharepoint-sites |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health | https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide |
| https://learn.microsoft.com/azure/sentinel/connect-data-sources | https://learn.microsoft.com/en-us/azure/sentinel/connect-data-sources |
| https://learn.microsoft.com/azure/sentinel/detect-threats-custom | https://learn.microsoft.com/en-us/azure/sentinel/create-analytics-rules |
| https://learn.microsoft.com/en-us/azure/sentinel/detect-threats-built-in | https://learn.microsoft.com/en-us/azure/sentinel/threat-detection |
| https://learn.microsoft.com/azure/sentinel/monitor-your-data | https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data |
| https://learn.microsoft.com/azure/sentinel/automate-incident-handling-with-automation-rules | https://learn.microsoft.com/en-us/azure/sentinel/automate-incident-handling-with-automation-rules |
| https://learn.microsoft.com/azure/sentinel/investigate-cases | https://learn.microsoft.com/en-us/azure/sentinel/investigate-cases |
| https://learn.microsoft.com/en-us/azure/information-protection/rms-client/track-and-revoke-admin | https://learn.microsoft.com/en-us/purview/track-and-revoke-admin |
| https://learn.microsoft.com/en-us/microsoft-365/compliance/apply-irm-to-a-list-or-library | https://learn.microsoft.com/en-us/purview/apply-irm-to-a-list-or-library |
| https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai | https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2 |
| https://learn.microsoft.com/azure/cost-management-billing/costs/overview-cost-management | https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management |
| https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets | https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets |
| https://learn.microsoft.com/en-us/azure/devops/test/overview | https://learn.microsoft.com/en-us/azure/devops/test/overview?view=azure-devops |
| https://learn.microsoft.com/en-us/microsoft-365/security/defender-endpoint/device-control-overview | https://learn.microsoft.com/en-us/defender-endpoint/device-control-overview |
| https://learn.microsoft.com/en-us/microsoftteams/information-barriers-in-teams | https://learn.microsoft.com/en-us/purview/information-barriers-teams |
| https://learn.microsoft.com/en-us/graph/api/resources/application | https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0 |
| https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview | https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview?view=graph-rest-1.0 |
| https://learn.microsoft.com/power-bi/guidance/powerbi-adoption-roadmap-governance | https://learn.microsoft.com/en-us/power-bi/guidance/fabric-adoption-roadmap-governance |
| https://learn.microsoft.com/security/operations/incident-response-planning | https://learn.microsoft.com/en-us/security/operations/incident-response-planning |
| https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy | https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpcompliancepolicy?view=exchange-ps |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview | https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview?view=o365-worldwide |
| https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance | https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-365-security-compliance-licensing-guidance |

---

## Errors

- **Agent Inventory** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/admin/tenant-wide-agent-inventory

---

*Generated by `scripts/learn_monitor.py`*