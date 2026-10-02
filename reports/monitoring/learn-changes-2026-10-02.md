# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-02
**Run Time:** 2026-10-02T12:02:39.209421+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 4 |
| HIGH Changes | 4 |
| MEDIUM Changes | 4 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | capacity-storage | CRITICAL | 3.5 | Monitor |
| 2 | fundamentals-what-is-copilot-studio | HIGH | 2.13 | Review and update |
| 3 | security-and-governance | HIGH | 1.8, 1.3, 1.1, 1.5, 1.4, 1.28, 2.8 | Update portal-walkthrough |
| 4 | ...ication-fundamentals-publish-channels | HIGH | 1.28 | Review and update |
| 5 | analytics-improve-agent-effectiveness | HIGH | None | Update portal-walkthrough |
| 6 | add-tools-custom-agent | HIGH | 2.17 | Review and update |
| 7 | kit-agent-review-tool | MEDIUM | 2.3 | Review optional |
| 8 | plan-agent-model-lifecycle | MEDIUM | 2.6 | Update portal-walkthrough |
| 9 | microsoft-365-copilot-overview | MEDIUM | 3.8 | Review optional |
| 10 | .../en-us/microsoft-agent-365/developer/ | HIGH | 3.2, 3.14, 3.6, 1.7, 2.5 | Review and update |
| 11 | overview | HIGH | 1.8, 1.27 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:855d7c9d95550f1c30376769dace7bc038c9f490a89e5b288420147743c97608

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
--- +++ @@ -124,7 +124,7 @@ Disable agent publishing: Your admin can use the Power Platform admin center to turn off the ability to publish agents that use generative AI features for your tenant.
 Disable data movement across geographic locations
 for Copilot Studio generative AI features outside the United States.
-Use the Microsoft 365 admin center to govern the conversational and AI actions and agents that show in Microsoft 365 Copilot
+Use the Microsoft 365 admin center to govern the conversational and AI actions and agents that show in Microsoft Copilot
 .
 Finally, Copilot Studio supports securely accessing customer data using
 Customer Lockbox

```

---

### 2. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:a98c25bca62df87403087ee9cf3ee03162ebcbbd46529e3f505c9e17af5089ae

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -231,12 +231,12 @@ Reactions
 section shows user feedback gathered from reactions to agent responses. The chart counts the number of times users selected either the thumbs up (positive) or thumbs down (negative) buttons available on each response they received from your agent.
 Note
-Agents published to the Microsoft 365 Copilot channel require admin consent in the Microsoft 365 admin center to share user feedback, including reactions and comments. You can view this feedback on the
+Agents published to the Microsoft Copilot channel require admin consent in the Microsoft 365 admin center to share user feedback, including reactions and comments. You can view this feedback on the
 Monitor
 page. Learn more in
 Agent settings in the Microsoft 365 admin center
 .
-Reactions from the Microsoft 365 Copilot channel aren't aggregated or counted in the
+Reactions from the Microsoft Copilot channel aren't aggregated or counted in the
 Reactions
 column in the
 Themes
@@ -248,7 +248,7 @@ security role.
 The Reactions feature is
 On
-by default for all channels except the Microsoft 365 Copilot channel. You can turn off this feature, if desired. You can also add or edit a disclaimer for users about how their feedback is used:
+by default for all channels except the Microsoft Copilot channel. You can turn off this feature, if desired. You can also add or edit a disclaimer for users about how their feedback is used:
 Open the agent, then go to
 Settings
 , and find the

```

---

### 3. Manage the AI model lifecycle for Copilot Studio agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:404e97b096448a1f7a95f05257752c5a94c2f94791bcfa769ce22413c21074e0

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.6/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.6/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -233,7 +233,7 @@ and repeat the request until all records are retrieved.
 Group the collected records by
 properties_model
-to see where each model is used across the tenant. The following example shows the agent count by model for a tenant, excluding agents that use the Copilot Studio default model or run in the Microsoft 365 Copilot experience:
+to see where each model is used across the tenant. The following example shows the agent count by model for a tenant, excluding agents that use the Copilot Studio default model or run in the Microsoft Copilot experience:
 Model Count
 ----- -----
 Claude Sonnet 4.6 24

```

---

### 4. AI Content Safety

**URL:** https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:5ccf554355193ba75a54e9cf4b1ec95c52580cf116e3224c52351a5689e8d5af

**Affected Controls:**
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -156,40 +156,9 @@ What's new
 page for upcoming deprecations.
 Input requirements
-See the following list for the input requirements for each feature.
-Analyze text API
-:
-Default maximum length: 10K characters (split longer texts as needed).
-Analyze image API
-:
-Maximum image file size: 4 MB
-Dimensions between 50 x 50 and 7200 x 7,200 pixels.
-Images can be in JPEG, PNG, GIF, BMP, TIFF, or WEBP formats.
-Analyze multimodal API (preview)
-:
-Default maximum text length: 1K characters.
-Maximum image file size: 4 MB
-Dimensions between 50 x 50 and 7200 x 7,200 pixels.
-Images can be in JPEG, PNG, GIF, BMP, TIFF, or WEBP formats.
-Prompt Shields API
-:
-Maximum prompt length: 10K characters.
-Up to five documents with a total of 10K characters.
-Groundedness detection API (preview)
-:
-Maximum length for grounding sources: 55,000 characters (per API call).
-Maximum text and query length: 7,500 characters.
-Minimum query length: 3 words.
-Protected material detection APIs
-:
-Default maximum length: 10K characters.
-Default minimum length: 110 characters (for scanning LLM completions, not user prompts).
-Custom categories (standard) API (preview)
-:
-Maximum inference input length: 1K characters.
-Task adherence (preview)
-:
-Maximum input length: 100K characters.
+For more information, see
+Input requirements
+.
 Language support
 The Azure AI Content Safety models for protected material, groundedness detection, and custom categories (standard) work with English only.
 Other Azure AI Content Safety models have been specifically trained and tested on the following languages: Chinese, English, French, German, Spanish, Italian, Japanese, Portuguese. However, these features can work in many other languages, but the quality might vary. In all cases, you should do your own testing to ensure that it works for your application.

```

---

## HIGH: Control Review Recommended

### 1. Copilot Studio Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:368f766f1564cce0c04b25f7b9f81cf7aab3f92f831dd495fae055d5d6489d1e

**Affected Controls:**
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`

**What Changed:**
```diff
--- +++ @@ -31,7 +31,7 @@ What you can build
 Copilot Studio supports several building blocks. Use them on their own, or combine them to automate an end-to-end business process. They can also collaborateâfor example, a workflow can call an agent to complete a step.
 Agents
-An agent is an AI assistant that handles conversations and completes tasks. It follows the instructions you give it, draws on the knowledge sources you connect, and uses tools to take actionâreasoning through a request and deciding the best next step based on its instructions and context. Agents can work with employees and customers in multiple languages across Microsoft Teams, Microsoft 365 Copilot, websites, mobile apps, and other channels.
+An agent is an AI assistant that handles conversations and completes tasks. It follows the instructions you give it, draws on the knowledge sources you connect, and uses tools to take actionâreasoning through a request and deciding the best next step based on its instructions and context. Agents can work with employees and customers in multiple languages across Microsoft Teams, Microsoft Copilot, websites, mobile apps, and other channels.
 You can create an agent by describing it in plain language, then test it before you publish. Some agents can be given their own account so they can work proactively on tasks and take part in shared business processes, such as onboarding a new employee or coordinating a recurring meeting.
 Learn more in
 Agents overview
@@ -60,7 +60,7 @@ for rule-based agents and structured, repeatable conversations.
 The
 Copilot chat harness
-for extending Microsoft 365 Copilot Chat with your organization's knowledge.
+for extending Microsoft Copilot Chat with your organization's knowledge.
 Learn more in
 Agent harnesses overview
 .
@@ -82,7 +82,7 @@ .
 The
 Copilot chat harness
-connects your enterprise knowledge to Microsoft 365 Copilot Chat. Employees get answers grounded in your content without leaving their everyday Microsoft
```

---

### 2. Agent Publishing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:97552dff71bde572bb76140c951aa591463c00ac07949a67aa331b72867e977f

**Affected Controls:**
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`

**What Changed:**
```diff
--- +++ @@ -26,7 +26,7 @@ This article describes features used in agents or agent flows powered by the
 standard harness
 .
-By using Copilot Studio, you can publish agents that engage with your customers on multiple platforms or channels. For example, live websites, mobile apps, Microsoft 365 Copilot, and messaging platforms like Teams and Facebook.
+By using Copilot Studio, you can publish agents that engage with your customers on multiple platforms or channels. For example, live websites, mobile apps, Microsoft Copilot, and messaging platforms like Teams and Facebook.
 Each time you update your agent, you can publish it again from within Copilot Studio. Publishing your agent applies to all the channels associated with your agent.
 You need to publish your agent before your customers can engage with it. You can publish your agent on multiple platforms, or
 channels
@@ -35,7 +35,7 @@ When you publish an agent, this agent updates on all connected channels. If you make changes to your agent but don't publish after doing so, your customers won't be engaging with the latest content.
 Agents have the
 Authenticate with Microsoft
-option turned on by default. With this option, agents automatically use Microsoft Entra ID authentication for Teams, Power Apps, and Microsoft 365 Copilot without requiring any manual setup.
+option turned on by default. With this option, agents automatically use Microsoft Entra ID authentication for Teams, Power Apps, and Microsoft Copilot without requiring any manual setup.
 If you want to allow anyone to chat with an agent, select
 No authentication
 .
@@ -71,7 +71,7 @@ in the current session. This command resets the conversation and starts a new session with the latest content you published. Otherwise, it might take one hour after you publish an update for the agent for its latest version to take effect. After this delay, users get the new version the next time they send a message to your agent.
 Test your agent
 Test your agent after you p
```

---

### 3. Agent Orchestration

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:0cc5ac076010d000c57b42900d8848da33a2ee29b541ad4cffdbf4b053c98b19

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

**What Changed:**
```diff
--- +++ @@ -32,6 +32,10 @@ Read and write data from Dataverse
 Read and post messages to Teams
 Mechanisms for adding tools to agents
+Note
+If a tool you expect isn't available in the
+Add a tool
+pane, your organization's policies might restrict the tools available to you. Contact your administrator for help.
 You can extend the capabilities of your custom agent by adding one or more
 tools
 . Your agent can use tools to respond to users automatically, using
@@ -78,40 +82,47 @@ Select
 Add a tool
 .
-In the
-Add tool
-panel, select
-New tool
-.
-Select the type of tool you want to add from the list that appears:
+Select the type of tool you want to add from the list:
+Agent flow
 Prompt
-Agent flow
+Model Context Protocol
 Computer use
+To show the full list, select
+See all
+. More options appear:
+Rest API
 Custom connector
-Model Context Protocol
-REST API
+See all
+changes to
+See less
+.
 Note
 If your organization blocked a tool due to data policies, you can't select it. Learn more in
 Tools blocked by your organization's policies
 .
 Perform the configuration steps specific to the type of tool you selected. For example, if you select
 Prompt
-, you must perform the following steps:
-Define the prompt template and instructions
-Specify input parameters
-Configure knowledge sources
-Set response format and constraints
+, perform the following steps:
+Define the prompt instructions
+Select a model
+Specify input parameters (by selecting
++ Add content
+)
+You can also get help by typing in the
+Prompt assistant
+field.
+As an alternative, you can use a pre-defined template to create a prompt by selecting
+prompt template
+.
 Select
 Save
-or
-Publish
-, as applicable, to create the new tool.
+to create the new tool.
 Select
 Add and configure
-. The tool is added to your agent. The configuration page for your tool appears. You can
-view and make changes to your tool configuration
+. The tool is added to your agent. The configuration page for your tool appears.
```

---

### 4. Agent 365 SDK and CLI

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/developer/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:ae8aaad64c21936c5bfa38e9d13b02178816dd7ee2180a60a501ed86241bad94

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/index.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/opentelemetry-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -39,13 +39,13 @@ Agent identity
 â explains the agent types and their identity models.
 Enable Google Vertex AI or Amazon Bedrock agents
-Registration for these agents requires no development work â agents are pulled automatically via the Google and Amazon APIs. No SDK integration, no blueprint, and no code changes are required. Once registered, you can use the Agent 365 SDK to add observability, Work IQ tool access, and other capabilities incrementally. See
+Registration for these agents requires no development work â agents are pulled automatically via the Google and Amazon APIs. No SDK integration, no blueprint, and no code changes are required. Use Microsoft OpenTelemetry for observability. See
 Registering Google Vertex AI and Amazon Bedrock agents
 to get started.
 Agent 365 SDK
-Use the
-Agent 365 SDK
-to extend agents built using any agent SDK or platform, with enterpriseâgrade identity, observability, notifications, security, and governed access to Microsoft 365 data.
+Use the Agent 365 SDK to extend agents built using any agent SDK or platform with identity, notifications, security, and governed access to Microsoft 365 data. Use
+Microsoft OpenTelemetry
+for observability.
 Tip
 Looking for pre-built agents? See
 ecosystem partner agents available in Agent 365
@@ -61,7 +61,7 @@ , enabling audited, traceable agent interactions, inference events, and tool usage.
 Invoke governed Model Context Protocol (MCP) servers to access Microsoft 365 workloads (for example, Mail, Calendar, SharePoint, Teams) under admin control.
 Function within an ITâapproved blueprint system, ensuring each agent instance inherits compliance, governance, and security policies.
-Learn more about the Agent 365 SDK
+Review the Agent 365 SDK overview
 .
 Agent 365 CLI
 Agent 365 CLI
@@ -83,9 +83,7 @@ Microsoft Entra agent blueprint
 and is an IT-approved, pre-configured definition of an agent type, essentially the enterprise "template" from which compliant agents can b
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Capacity Storage
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:4e953d81a18f028874e4e6ad0f931bc2c58aced2c740dda08e0ecb62b17cba08

---

### 2. Copilot Agent Kit — Agent Review Tool
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/kit-agent-review-tool
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:108e9180c23b12712ae1c90ea86125323d5c8b0be10ccd731a3e24acfbc4f8f2

---

### 3. Manage the AI model lifecycle for Copilot Studio agents
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/plan-agent-model-lifecycle
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:404e97b096448a1f7a95f05257752c5a94c2f94791bcfa769ce22413c21074e0

---

### 4. M365 Copilot Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f21c977515eba2e661a852644d485774151fdfedd616e5f5a8d1d9a410a3eed6

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*