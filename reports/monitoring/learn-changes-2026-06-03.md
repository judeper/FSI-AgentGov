# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-03
**Run Time:** 2026-06-03T11:02:05.238013+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 11 |
| HIGH Changes | 15 |
| MEDIUM Changes | 10 |
| Redirects | 1 |
| Errors | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | advanced-connector-policies | HIGH | 1.4 | Update portal-walkthrough |
| 2 | ...en-us/connectors/connector-reference/ | MEDIUM | 1.4 | Review and update |
| 3 | database-security | HIGH | 1.1 | Review and update |
| 4 | power-platform-inventory | CRITICAL | 3.11 | Monitor |
| 5 | copilot-hub | HIGH | 3.1, 3.8 | Review and update |
| 6 | business-continuity-disaster-recovery | HIGH | 2.4 | Update portal-walkthrough |
| 7 | regions-overview | MEDIUM | 2.4 | Update portal-walkthrough |
| 8 | capacity-storage | CRITICAL | 3.5 | Monitor |
| 9 | analytics-overview | HIGH | 2.6, 2.5, 2.9, 3.2, 3.10 | Update portal-walkthrough |
| 10 | analytics-improve-agent-effectiveness | CRITICAL | None | Update portal-walkthrough |
| 11 | nlu-gpt-overview | HIGH | 2.12 | Review and update |
| 12 | external-security-provider | HIGH | 1.8 | Update portal-walkthrough |
| 13 | planned-features | MEDIUM | 1.4, 2.17, 2.25, 3.8 | Review optional |
| 14 | microsoft-365-copilot-privacy | MEDIUM | 4.7, 4.6, 2.23 | Update portal-walkthrough |
| 15 | ...rosoft.com/en-us/microsoft-agent-365/ | HIGH | 1.7, 2.6, 2.5, 2.12, 2.25, 3.14, 3.1, 3.2, 3.6, 3.13 | Update portal-walkthrough |
| 16 | overview | MEDIUM | 2.6, 2.12, 2.25, 3.1, 3.13 | Update portal-walkthrough |
| 17 | agent-365-overview | HIGH | 2.25, 3.8 | Review and update |
| 18 | dlp-policy-reference | HIGH | None | Review and update |
| 19 | audit-copilot | HIGH | 1.6, 1.21, 1.19, 1.14, 1.7 | Review and update |
| 20 | ai-microsoft-purview | MEDIUM | 4.7, 4.8, 1.6, 1.5, 1.16, 2.6 | Review and update |
| 21 | communication-compliance-policies | CRITICAL | 1.10 | Update portal-walkthrough |
| 22 | import-hr-data | HIGH | 1.12 | Update portal-walkthrough |
| 23 | trainable-classifiers-learn-about | HIGH | 1.13 | Review and update |
| 24 | dlp-configure-endpoint-settings | HIGH | 1.17 | Review and update |
| 25 | concept-conditional-access-cloud-apps | HIGH | None | Review and update |
| 26 | custom-overview | HIGH | None | Review and update |
| 27 | permissions-reference | MEDIUM | 2.23 | Review optional |
| 28 | alerts-overview | HIGH | 2.9 | Review and update |
| 29 | information-barriers-teams | HIGH | None | Review and update |
| 30 | whats-new | HIGH | None | Review and update |
| 31 | microsoft-365-overview | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Advanced Connector Policies

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.4/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -19,11 +19,9 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Advanced connector policies (preview)
+Advanced connector policies
 Feedback
 Summarize this article for me
-[This article is prerelease documentation and is subject to change.]
-Overview
 Advanced connector policies (ACP) represent the next generation of securing connector usage within Power Platform. ACP provides a modern, flexible approach to managing
 certified connectors
 , replacing the Business/Non-Business/Blocked classification model in classic
@@ -49,11 +47,6 @@ . Custom connectors and HTTP connectors aren't yet supported. They're planned as a separate rule type in the future. For governing custom connectors and HTTP connectors today, continue using classic
 data policies
 .
-Important
-This is a preview feature.
-Preview features arenât meant for production use and might have restricted functionality. These features are subject to
-supplemental terms of use
-, and are available before an official release so that customers can get early access and provide feedback.
 Supported connector types
 Advanced connector policies are built on the certified connector catalog. ACP doesn't support all connector types from classic data policies.
 Connector type
@@ -112,9 +105,9 @@ Rules
 tab.
 Select
-Advanced connector policies (preview)
+Advanced connector policies
 . The
-Advanced connector policies (preview)
+Advanced connector policies
 pane is displayed.
 Define the policy. Keep the following points in mind:
 By default, the nonblockable connectors are preloaded as
@@ -150,7 +143,7 @@ Data and privacy
 .
 Select
-Advanced connector policies (preview)
+Advanced connector policies
 .
 Define the policy by using the same connector allow and block controls as the environment group experience.
 Select
@@ -253,10 +246,6 @@ .
 Managed Environments and nonblockable connectors
 : In single environment mode, ACP works on both Managed Environments and non-Managed En
```

---

### 2. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -184,8 +184,10 @@ Yes, self-service disaster recovery is supported for Power Apps and Power Pages.
 Is Power Automate supported with self-service disaster recovery?
 As of October 2025:
-Power Automate desktop flows are fully supported for failover and failback with self-service disaster recovery.
-Power Automate cloud flows are now available in preview. Don't use features in preview with production workloads.
+Power Automate desktop flows and cloud flows are supported for failover and failback with self-service disaster recovery.
+As Microsoft works on performance optimizations, you must
+sign-up for this feature
+.
 How can I find out where my data is being replicated? Can I change my secondary destination region?
 Microsoft reserves the right to disclose the exact details of where your data resides for security reasons. If your data needs to be moved or replicated, Microsoft considers various high availability and resiliency scenarios. You can be assured that your data at rest respects geographical boundaries and abides by legislated residency laws. Even if self-service disaster recovery isn't turned on, Microsoft reserves the right to replicate, move, and relocate the data within a region for high availability and operational needs. The location of customer data within a geography (for example,
 APAC

```

---

### 3. Regions Overview

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/regions-overview
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -19,14 +19,18 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Regions overview
+Choose the region when setting up an environment
 Feedback
 Summarize this article for me
 For multinational companies with employees and customers distributed around the world, you can create and manage environments specific to your global regions. You can create an environment in a different region than where your tenant resides. Local environments can provide quicker data access for users in that region. Be sure to read
 A multi-environment deployment
-to understand the features of multiple environments.
+to understand the features of multiple environments and learn about
+macro regions
+.
 How do I find out where my app is deployed?
-Your app is deployed in the region that hosts the environment. For example, if your environment is created in the Europe region, then your app is deployed in Europe data centers.
+Your app is deployed in the region that hosts the environment. Learn more about
+macro regions
+. For example, if your environment is created in the European Union (EU) and European Free Trade Association (EFTA), then your app is deployed in European data centers. Your data resides within EU and EFTA member states which are European Union Data Boundary (EUDB) regions.
 Using Power Platform admin center
 If you're an administrator, you can determine the region of each environment in the Power Platform admin center.
 Sign in to the

```

---

### 4. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -31,7 +31,7 @@ and for
 autonomous agents
 .
-Analytics are available in all geographies. Analytics data is available for up to 180 days. Session details and transcript information is available for the last 28 days. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
+Analytics are available in all geographies. Analytics data is available for up to 180 days. Session details and transcript information are available for the last 28 days. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
 Note
 The
 Analytics
@@ -39,11 +39,11 @@ test panel
 .
 Grant limited view-only access to analytics
-If you are the agent owner and want to grant access only to the
+If you're the agent owner and want to grant access only to the
 Analytics
 page of your agent, you can do so by sharing the agent with the
 Analytics Viewer
-sharing role enabled. If you want the person you are sharing this agent with to have access to information from the conversation transcript, they must also have the
+sharing role enabled. If you want the person you're sharing the agent with to have access to information from the conversation transcript, they must also have the
 Bot Transcript Viewer
 security role.
 Learn more about
@@ -67,7 +67,7 @@ It helps you quickly understand common themes and metrics and identify areas for improvement for your agent by summarizing them in a bulleted list for the selected reporting period. This can include engagement metrics, customer sentiment and feedback, and trends since the last reporting period.
 The
 customer comments summary
-(preview) helps you understand high-level customer sentiment about the agent, such as feedback and comments. Insights are prioritized based on both t
```

---

### 5. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -19,7 +19,7 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Analyze conversational agent effectiveness
+Analyze conversational agents
 Feedback
 Summarize this article for me
 The
@@ -33,36 +33,53 @@ area that analyzes time and cost savings attributable to your agent or your agent's tools, and a
 Summary
 area that provides key analytic insights into your agent's performance.
-For more information about:
+There are four core sections to focus on when reviewing and improving conversational agent effectiveness.
 The
 Summary
-and
+,
 Overview
-areas, see
-Analytics overview
-The
+, and
 Savings
-area, see
-Analyze time and cost savings for agents
-There are seven core areas to focus on when reviewing and improving conversational agent effectiveness:
-The Analytics page has seven core areas for reviewing and improving conversational agents effectiveness:
-Themes
-:
-Themes
-help you gain analytics insights by clustering user questions into AI-suggested categories.
+section shows key analytics insights about your agents along with billing and cost savings statistics; see
+Summary
+,
+Overview
+, and
+Savings
+to learn more about each subsections.
+The
+Custom metrics
+section lets you define business-specific metrics for your agents use cases.
+The
+Effectiveness
+section helps you evaluate the quality of user experiences by showing where conversations succeed, where they break down, and how users feel about outcomes.
+The
+Use
+section helps you improve operational performance by showing how well your agent answers questions, how reliably tools and knowledge sources support those answers, and where targeted updates can increase coverage and consistency.
+You can view analytics for events that occurred in the last 90 days.
+Custom metrics
+The
+Custom metrics
+section lets you define up to three business-specific metrics in natural language and track how often each outcome appears across sampled sessions. Use these metrics
```

---

### 6. External Threat Detection

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-provider
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -262,15 +262,22 @@ , but you can also chose the
 Block the query
 option to further reduce risk.
+Note
+Once you configure threat detection, the threat detection system triggers before any tool invocation by an agent. If the agent doesn't receive a decision from the system (either allow or block) within one second, by default, it proceeds to
+allow
+the tool to execute as planned. To change the default behavior, configure
+Set error behavior
+.
 Select
 Save
 .
 Important
-The save will fail if your Microsoft Entra app is not properly configured in Microsoft Entra or not properly authorized with your provider of choice.
+The save fails if your Microsoft Entra app is not properly configured in Microsoft Entra or not properly authorized with your provider of choice.
 Note
-Once configured, the threat detection system triggers before any tool invocation by an agent. If the agent doesn't receive a decision from the system (either allow or block) within one second, it proceeds to
-allow
-the tool to execute as planned.
+There is no global or tenant-wide setting to automatically enable the external security provider across all Copilot Studio environments. External threat detection must be turned on manually for each environment via the Copilot Studio admin portal. Here are some important considerations:
+The external security provider is configured per environment.
+Thereâs no PowerShell, API, or admin center setting to enforce or propagate this configuration globally for other existing or future environments.
+You need to turn on the threat detection for a new environments after you create the environment.
 Troubleshooting
 Here's some information on issues that might occur and how to handle them.
 Power Platform admin center threat detection configuration issues
@@ -298,14 +305,14 @@ Here are some other common issues that might occur with your Microsoft Entra app and authentication.
 Microsoft Entra application doesn't exist
 Example
-: Failed to acquire to
```

---

### 7. Data, Privacy, and Security

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Section:** Microsoft 365 Copilot
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -78,8 +78,11 @@ When you're using web search, Microsoft 365 Copilot parses the user's prompt and identifies terms where web search would improve the quality of the response. Based on these terms, Copilot generates a search query that it sends to the Bing Search service. For more information,
 Data, privacy, and security for web queries in Microsoft 365 Copilot and Microsoft 365 Copilot Chat
 .
-Starting January 7, 2026, Anthropic is a subprocessor for Microsoft 365 Copilot. For more information, see
+Anthropic is a subprocessor for Microsoft 365 Copilot. For more information, see
 Anthropic as a subprocessor for Microsoft Online Services
+.
+We may deploy other AI models for Microsoft 365 Copilot to use that are hosted and operated by Microsoft. These models are governed by the same contractual and data protection commitments already in place, including that no data leaves Microsoft. For more information about models that may be used by Copilot, see
+Understanding AI functionality and models in Microsoft Online Services
 .
 While abuse monitoring, which includes human review of content, is available in Azure OpenAI, Microsoft 365 Copilot services have opted out of it. For information about content filtering, see the
 How does Copilot block harmful content?

```

---

### 8. Agent 365 Documentation Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -1,18 +1,18 @@ Microsoft Agent 365 documentation
 Agent 365 is the control plane for IT and security leaders to observe, secure, and govern agents across the organization.
 Get Microsoft Agent 365 for IT admins
-Get started with Microsoft Agent 365
-Microsoft Agent 365 allows you to manage all your organizationâs agents at scale, regardless of where these agents are built or acquired.
-What is Agent 365?
-Agent 365 is the control plane for AI agents. Empower your organization to confidently deploy, govern, and manage all your agents at scale, regardless of where these agents are built or acquired.
+Explore Microsoft Agent 365
+Microsoft Agent 365 allows you to manage all your organizationâs agents at scale, regardless of where they originate.
+Why does an enterprise need Agent 365?
+Transform fragmented, high-risk experimentation into trusted, enterprise-wide AI operations with a unified control plane that makes agents visible, governed, and secure.
 Learn more
-How can I provision my organizationâs agents with Microsoft Agent 365?
-As an IT admin, set up and manage all AI agents with Agent 365.
+Govern without slowing innovation
+Establish lightweight guardrails for observability and acccountability to gain control and trust while still allowing teams to move quickly.
 Learn more
 How can I extend my agent to be Microsoft Agent 365 compatible?
-Any agent can adopt Agent 365, regardless of where the agent is built or acquired. Learn how to get started as an agent developer.
+Use Microsoft Agent 365 SDK to extend agents built using any agent SDK or platform, with enterpriseâgrade identity, observability, notifications, security, and governed access to Microsoft 365 data.
 Learn more
-Explore Microsoft Agent 365
+Get started with Microsoft Agent 365
 Observe, secure, and govern every agent across your organization with Microsoft Agent 365.
 Observe
 Gain visibility into agents in your environment, understand how theyâre used, and act quickly on pe
```

---

### 9. Agent 365 Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -64,7 +64,7 @@ Microsoft Agent 365 Licensing FAQs
 .
 Next step
-Onboard to Microsoft Agent 365
+Why does an enterprise need Agent 365?
 Feedback
 Was this page helpful?
 Yes

```

---

### 10. Create Policies

**URL:** https://learn.microsoft.com/en-us/purview/communication-compliance-policies
**Section:** Microsoft Purview
**Classification:** CRITICAL (Deprecation notice)

**Affected Controls:**
- Control 1.10: Control 1.10: Communication Compliance Monitoring
  - File: `controls/pillar-1-security/1.10-communication-compliance-monitoring.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.10/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -26,13 +26,16 @@ Microsoft Purview Communication Compliance
 provides the tools to help organizations detect regulatory compliance (for example, SEC or FINRA) and business conduct violations such as sensitive or confidential information, harassing or threatening language, and sharing of adult content. Communication Compliance is built with privacy by design. Usernames are pseudonymized by default, role-based access controls are built in, investigators are opted in by an admin, and audit logs are in place to help ensure user-level privacy.
 Policies
+Create Communication Compliance policies for Microsoft 365 organizations in the Microsoft Purview portal. Communication Compliance policies define which communications and users are subject to review in your organization, set custom conditions the communications must meet, and specify who should do reviews.
+Users assigned the
+Communication Compliance Admins
+role can set up policies and access the
+Communication Compliance
+page and global settings in Microsoft Purview.
+You can export the modification history to a .csv file that includes the status of alerts pending review, escalated items, and resolved items.
+You can't rename policies, but you can delete them when no longer needed.
 Important
 PowerShell isn't supported for creating and managing Communication Compliance policies. To create and manage these policies, use the policy management controls in the Communication Compliance solution.
-Create Communication Compliance policies for Microsoft 365 organizations in the Microsoft Purview portal. Communication Compliance policies define which communications and users are subject to review in your organization, set custom conditions the communications must meet, and specify who should do reviews. Users assigned the
-Communication Compliance Admins
-role can set up policies. Anyone with this role can access the
-Communication Compliance
-page and global settings in Microsoft Purview. If needed, you can expo
```

---

### 11. HR Data Connector

**URL:** https://learn.microsoft.com/en-us/purview/import-hr-data
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -33,10 +33,11 @@ Data connectors
 page in the Microsoft Purview portal. Multiple role groups include this role by default. For a list of these role groups, see
 Roles in Microsoft Defender for Office 365 and Microsoft Purview
-. Alternatively, an admin in your organization can create a custom role group, assign the Data Connector Admin role, and then add the appropriate users as members. For instructions, see:-
+. Alternatively, an admin in your organization can create a custom role group, assign the Data Connector Admin role, and then add the appropriate users as members. For instructions, see
 Permissions in the Microsoft Purview portal
--
-Roles and role groups in Microsoft Defender for Office 365 and Microsoft Purview compliance
+and
+Roles and role groups in Microsoft Defender for Office 365 and Microsoft Purview
+.
 Understand that the sample script you run in Step 4 uploads your HR data to the Microsoft cloud so that the insider risk management solution can use it. This sample script isn't supported under any Microsoft standard support program or service. The sample script is provided AS IS without warranty of any kind. Microsoft further disclaims all implied warranties including, without limitation, any implied warranties of merchantability or of fitness for a particular purpose. You assume all risk arising from the use or performance of the sample script and documentation. In no event shall Microsoft, its authors, or anyone else involved in the creation, production, or delivery of the scripts be liable for any damages whatsoever (including, without limitation, damages for loss of business profits, business interruption, loss of business information, or other pecuniary loss) arising out of the use of or inability to use the sample scripts or documentation, even if Microsoft has been advised of the possibility of such damages.
 This data connector is available in GCC environments in the Microsoft 365 US Government cloud. Third-party applications an
```

---

## HIGH: Control Review Recommended

### 1. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -2372,6 +2372,8 @@ By: Troy Taylor
 Resend (Independent Publisher)
 By: Troy Taylor
+Responsive MCP
+By: RFPIO Inc (dba Responsive)
 REST Countries (Independent Publisher)
 By: Siddharth Vaghasia
 Retarus SMS
@@ -2670,7 +2672,7 @@ By: Troy Taylor
 SureXeroLite (Independent Publisher)
 By: The 848 Group
-Survalyzer EU
+Survalyzer Eu
 By: Survalyzer AG
 Survalyzer Swiss
 By: Survalyzer AG

```

---

### 2. Database Security

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/database-security
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`

**What Changed:**
```diff
--- +++ @@ -27,6 +27,43 @@ environments that have no Dataverse database
 and
 environments that have a Dataverse database
+.
+Understand role types
+Microsoft Power Platform uses different types of roles at different scopes. Understanding the distinction helps you identify which role to assign for a given scenario.
+Role type
+Examples
+Scope
+Typical use
+Tenant-level admin roles
+Power Platform administrator, Dynamics 365 administrator, Global Administrator
+Entire tenant (all environments)
+Manage environments, policies, and platform settings across the organization. Assigned in the Microsoft 365 admin center.
+Environment-level roles
+Environment Admin, Environment Maker
+Single environment (without Dataverse)
+Create and manage resources such as apps, flows, and connections in an environment that doesn't have a Dataverse database.
+Dataverse security roles
+System Administrator, System Customizer, Basic User
+Single environment (with Dataverse)
+Control access to Dataverse tables, apps, and data within an environment that has a Dataverse database.
+App-specific roles
+Dynamics 365 Sales roles, Customer Service roles
+Single environment (with Dataverse)
+Provide access to features in specific Dynamics 365 or Power Platform apps.
+Important
+Tenant-level admin roles such as
+Power Platform administrator
+and
+Dynamics 365 administrator
+are assigned in the Microsoft 365 admin center and grant administrative access across environments. However, these roles don't automatically grant Dataverse data access. To work with data in a Dataverse environment, a tenant admin must also be assigned the
+System Administrator
+Dataverse security role in that specific environment. Learn more in
+Use service admin roles to manage your tenant
+.
+Use this article to understand built-in roles and how they apply to different environment types. To assign roles, see
+Configure user security in an environment
+. If users encounter access errors, see
+Troubleshoot user access problems
 .
```

---

### 3. Copilot Hub

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -54,13 +54,7 @@ area for in-product configuration.
 Note
 Tenant users with environment access can view Copilot settings.
-Control who can use AI features in model-driven apps (preview)
-[This section is prerelease documentation and is subject to change.]
-Important
-This is a preview feature.
-Preview features arenât meant for production use and might have restricted functionality. These features are subject to
-supplemental terms of use
-, and are available before an official release so that customers can get early access and provide feedback.
+Control who can use AI features in model-driven apps
 Admins can define who within an environment can use Copilot capabilities in model-driven appsâeither by explicitly allowing specific users or allowing all users except a defined exclusion list. This capability is currently in preview and is only for environments activated for
 Managed Environments
 , with a subset of Copilot features adhering to it. Review the following table to learn which capabilities adhere to this configuration.

```

---

### 4. Quickstart: Create and deploy an agent

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-gpt-overview
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

**What Changed:**
```diff
--- +++ @@ -67,7 +67,7 @@ Azure OpenAI
 .
 Generative answers
-With generative answers, your agent can find and present information from multiple sources, both internal and external. You don't need to manually create multiple topics that might not address all customer questions. Use generative answers as primary information sources or as a fallback when authored topics can't answer a user's query. By using generative answers, you can quickly create and deploy a functional agent.
+By using generative answers, your agent can find and present information from multiple sources, both internal and external. You don't need to manually create multiple topics that might not address all customer questions. Use generative answers as primary information sources or as a fallback when authored topics can't answer a user's query. By using generative answers, you can quickly create and deploy a functional agent.
 What changed?
 When a traditional chatbot can't determine a user's intent, it asks the user to rephrase their question. If after two prompts, the chatbot still can't determine the user's intent, it escalates to a live agent by using the
 Escalate
@@ -84,6 +84,13 @@ You create individual topics for frequently asked questions. These topics might develop from
 analytics from previous agents
 or existing support issues.
+Generative answers behavior
+Answers aren't deterministic. Repeating a question almost guarantees different answers because the question-answering process includes previous chat context. Consider the following interaction between two persons, a tourist and a local:
+The tourist asks the local: "Could you give me directions to the train station?"
+The local answers with directions.
+The tourist immediately follows up with "Give me directions to the train station."
+The local probably wouldn't repeat verbatim the directions they already gave the tourist. The local might give the tourist more precise directions or ask where they're starting from. Every time the t
```

---

### 5. Agent 365 Overview Page (M365 Admin)

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.25/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -53,6 +53,15 @@ The Microsoft Frontier program gives organizations early access to innovative and emerging AI capabilities in Microsoft 365 before those features reach general availability (GA). Frontier previews are subject to the existing preview terms of your customer agreements. For more information, see
 Get started with the Microsoft Frontier program
 .
+Prerequisites
+Before you can manage agents in the Microsoft 365 admin center, confirm the following requirements are met:
+Your organization has the required Microsoft 365 subscription and licenses for either Microsoft 365 Copilot or Microsoft Agent 365 capabilities.
+Users who create, publish, or use agents have the appropriate licenses assigned.
+Youâre assigned an administrator role that includes permissions to manage settings for either Microsoft 365 Copilot or Microsoft Agent 365 in the Microsoft 365 admin center.
+For more information, see the following resources:
+Plans and licensing for Microsoft Agent 365
+License options for Microsoft 365 Copilot
+Agent management roles and permissions
 View the Agent overview
 You can access and view the
 Agent overview

```

---

### 6. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -2178,8 +2178,48 @@ .
 Supported actions: SharePoint
 Restrict access or encrypt the content in Microsoft 365 locations
+Block everyone
+Block only people from outside your organization
+Block access for specific external domains or users (in public preview)
+The
+Block access for specific external domains or users
+sub-option lets you block external access by domain (for example,
+partner.com
+) or by user SMTP (for example,
+user@example.com
+). You can also specify allow lists by using
+Domain IS NOT
+or
+User IS NOT
+. Internal users and domains can't be blocked with this sub-option; continue to use
+Block everyone
+for internal users.
+Note
+When you use
+Block access for specific external domains or users
+: if a user or domain appears in both allow and block lists, the block takes effect (most restrictive wins). If a file matches both an allow rule and a block rule, evaluation is across all matching rules â allowed users and domains are permitted, blocked users and domains are denied, and users in neither list are blocked by default.
 Supported actions: OneDrive
 Restrict access or encrypt the content in Microsoft 365 locations
+Block everyone
+Block only people from outside your organization
+Block access for specific external domains or users (in public preview)
+The
+Block access for specific external domains or users
+sub-option lets you block external access by domain (for example,
+partner.com
+) or by user SMTP (for example,
+user@example.com
+). You can also specify allow lists by using
+Domain IS NOT
+or
+User IS NOT
+. Internal users and domains can't be blocked with this sub-option; continue to use
+Block everyone
+for internal users.
+Note
+When you use
+Block access for specific external domains or users
+: if a user or domain appears in both allow and block lists, the block takes effect (most restrictive wins). If a file matches both an allow rule and a block rule, evaluation is per rule â allowed users and domains are permitted, 
```

---

### 7. Audit Copilot Activities

**URL:** https://learn.microsoft.com/en-us/purview/audit-copilot
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -44,7 +44,7 @@ Copilot in Microsoft Fabric
 , and custom applications built using
 Microsoft Copilot Studio
-and Azure AI Studio are included in Audit Standard.
+and Microsoft Foundry are included in Audit Standard.
 Admin activities with Copilot and AI applications
 The system generates audit logs when an administrator performs activities related to Copilot settings, plugins, promptbooks, or workspaces. For more information, see
 Microsoft 365 Copilot activities

```

---

### 8. DSPM for AI

**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -36,9 +36,10 @@ Copilot Studio
 Enterprise AI apps
 for non-Copilot AI apps and agents connected to your organization through Entra registration, data connectors, Microsoft Foundry, and other methods, and include:
+Microsoft Foundry
 Entra-registered AI apps
+Anthropic Claude (Enterprise)
 ChatGPT Enterprise
-Microsoft Foundry
 Other AI apps
 that are detected through browser activity and categorized as "Generative AI" in the Defender for Cloud Apps catalog. This category can include AI apps and agents from the other two categories but also uniquely includes AI apps and agents from third-party LLMs, such as:
 ChatGPT
@@ -59,6 +60,7 @@ Copilot in Fabric
 ChatGPT Enterprise
 Microsoft Copilot Studio
+Anthropic Claude (Enterprise)
 Microsoft Facilitator
 Channel Agent in Teams
 For a list of supported Microsoft Purview security and compliance supported capabilities for Microsoft Agent 365, see

```

---

### 9. Trainable Classifiers

**URL:** https://learn.microsoft.com/en-us/purview/trainable-classifiers-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -28,7 +28,7 @@ In Preview:
 You can view the trainable classifiers in content explorer by expanding
 Trainable Classifiers
-in the filters panel. The trainable classifiers automatically display the number of incidents found in SharePoint, Teams, and OneDrive, without requiring any labeling.
+in the filters panel. The trainable classifiers automatically display the number of incidents found in SharePoint and Teams, without requiring any labeling.
 If you don't want to use this feature, you must file a request with Microsoft Support. This request disables the display of your sensitive data that isn't used in any labeling policies within Content Explorer. You can disable scanning of your data as well. If scanning is turned off, sensitivity labeling and DLP policies with those classifiers don't work.
 Where you can use classifiers
 Use classifiers as a condition for:
@@ -60,7 +60,7 @@ Support for custom classifiers is limited to English.
 When the Microsoft provided pretrained classifiers don't meet your needs, you can create and train your own classifiers. There's more work involved with creating your own, but they're better tailored to your organization's needs.
 To create a custom trainable classifier, you start by feeding it one set of examples that are definitely in the category, and another set of examples that are definitely not in the category. Microsoft Purview processes those examples and the classifier then makes predictions as to whether any given item falls into the category you're building. You then confirm the results, sorting out the true positives, true negatives, false positives, and false negatives to help increase the accuracy of its predictions.
-When you publish the classifier, it sorts through items in locations like SharePoint, Exchange, and OneDrive, and classifies the content.
+When you publish the classifier, it sorts through items in locations like SharePoint and Exchange, and classifies the content.
 For example, you can create tr
```

---

### 10. Configure Settings

**URL:** https://learn.microsoft.com/en-us/purview/dlp-configure-endpoint-settings
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -147,17 +147,7 @@ %SystemDrive%\Users\*\Documents\*(2)\Sub\
 Windows file paths excluded by default
 %SystemDrive%\\Users\\*(1)\\AppData\\Roaming
-%SystemDrive%\\Users\\*(1)\\AppData\\Local\\Temp
-%SystemDrive%\\Users\\*(1)\\AppData\\Local\\Microsoft\\Windows\\INetCache
-Note
-Unsaved file protection (preview)
-can detect and block egress activities on unsaved files even when those files are located in excluded paths, such as
-%temp%
-or
-%appdata%
-. File path exclusions apply to DLP classification and policy enforcement on
-saved
-files only.
+%SystemDrive%\\Users\\*(1)\\AppData\\Local
 File path exclusions for Mac
 You can also add your own exclusions for macOS devices.
 File path definitions are case insensitive, so
@@ -382,10 +372,10 @@ setting.
 Add the desired restricted app group.
 Select
-Apply restriction to all/specific activity
+Apply restriction to all activity
 , and select
 Allow
-.
+. Audit and Off will not work.
 For all other apps, set the
 Access by apps that arenât on the 'unallowed apps' list
 setting to

```

---

### 11. Authentication Contexts

**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-cloud-apps#authentication-context
**Section:** Microsoft Entra ID
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -182,7 +182,9 @@ The following Conditional Access behavior is changing
 . Those low privileged scopes that were previously excluded from policy enforcement will
 no longer be excluded
-. This change means that users who were previously able to access the application without any Conditional Access enforcement might now receive Conditional Access challenges. The change is rolling out in phases starting in March, 2026.
+. This change means that users who were previously able to access the application without any Conditional Access enforcement might now receive Conditional Access challenges. The change is rolling out in phases starting in March, 2026. For more information see
+Enforcement for baseline scopes
+.
 If any app is excluded from the policy, to avoid inadvertently blocking user access, certain low privilege scopes were
 previously
 excluded from policy enforcement. These scopes allowed calls to the underlying Graph APIs, like
@@ -269,264 +271,6 @@ The
 Azure AD Graph retirement
 does not affect the Azure AD Graph (Windows Azure Active Directory) resource registered in your tenant.
-User experience
-In user sign-in flows where client applications request only the scopes listed above, users might now receive Conditional Access challenges (such as MFA or device compliance). The exact challenge depends on the access controls configured in your policies that target All resources (with or without resource exclusions) or policies that explicitly target Azure AD Graph.
-In the following example, the tenant has a Conditional Access policy with the following details:
-Targeting All users and All resources
-Resource exclusions for a confidential client application and Exchange Online
-MFA is configured as the grant control
-Example scenarios
-Example scenario
-User impact (before â after)
-Conditional Access evaluation
-A user signs into Visual Studio Code desktop client, which requests openid and profile scopes.
-Before
-: User not prompted for MFA
-After
-
```

---

### 12. Role-Based Access Control

**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/custom-overview
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -103,6 +103,87 @@ With Microsoft Entra ID P2, you can use Microsoft Entra Privileged Identity Management (Microsoft Entra PIM) to provide just-in-time access to roles. This feature allows you to grant time-limited access to a role to users who require it, rather than granting permanent access. It also provides detailed reporting and auditing capabilities. For more information, see
 Assign Microsoft Entra roles in Privileged Identity Management
 .
+Understand who has access to what
+Listing role assignments is one part of answering the broader question: "who has access to what in my organization?" Microsoft Entra ID provides several tools that, when used together, give you visibility into access across your tenant.
+Role assignments.
+Use the procedures in
+List Microsoft Entra role assignments
+to list who holds Microsoft Entra roles at the tenant, application, or administrative unit scope. You can
+download role assignments
+as a CSV for offline analysis, or query them programmatically with the
+List unifiedRoleAssignments
+Microsoft Graph API.
+App role assignments and consent grants.
+Use
+Assign users and groups to an application
+to see which users and groups can access a given enterprise application. Use
+Review permissions granted to applications
+to inspect the delegated and application permissions that users or administrators have consented to.
+Custom security attributes.
+Use
+custom security attributes
+to tag users and service principals with business-specific attributes that you define for your tenant. You can then filter and query the directory by attribute to build a business-attribute view of access that complements role-based queries.
+Access reviews.
+Use
+access reviews
+to periodically verify that users still need their current group memberships and assignments to enterprise applications. Use
+Privileged Identity Management (PIM) access reviews
+to review users and service principals assigned to Microsoft Entra or Azure resource roles
```

---

### 13. Azure Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview
**Section:** Azure Services
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`

**What Changed:**
```diff
--- +++ @@ -77,7 +77,7 @@ Metric alerts evaluate resource metrics at regular intervals. Metrics can be platform metrics, custom metrics, logs from Azure Monitor converted to metrics, or Application Insights metrics. Metric alerts can also apply multiple conditions and use dynamic thresholds.
 Log search alerts
 Log search alerts allow users to use a Log Analytics query to evaluate resource logs at a predefined frequency. Log search can use dynamic thresholds (preview).
-Simple log search alerts - preview
+Simple log search alerts
 Simple Log alerts allow users to use a Log Analytics query to evaluate each row individually.
 Activity log alerts
 Activity log alerts are triggered when a new activity log event occurs that matches defined conditions. Resource Health alerts and Service Health alerts are activity log alerts that report on your service and resource health.
@@ -163,7 +163,7 @@ . When you split on the resourceId column, you will get one alert per resource that meets the condition.
 Log search alert rules that use splitting by dimensions are charged based on the number of time series created by the dimensions resulting from your query. If the data is already collected to a Log Analytics workspace, there is no additional cost.
 If you use metric data at scale in the Log Analytics workspace, pricing will change based on the data ingestion.
-Simple log search alerts - Preview
+Simple log search alerts
 Simple log search alerts are designed to provide a simpler and faster alternative to traditional log search alerts. Unlike traditional log search alerts that aggregate rows over a defined period, simple log alerts evaluate each row individually. Search based alerts support the analytics and basic logs.
 Simple log search alerts use the Kusto Query Language (KQL) but the feature is designed to simplify the query process, making it easier for you to create alerts without extensive KQL knowledge.
 Simple search alerts provide faster alerting compared to traditional l
```

---

### 14. Information Barriers in Teams

**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-teams
**Section:** Microsoft Teams
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -215,8 +215,8 @@ for a smoother experience.
 Users can't join channel meetings
 : If you enable IB policies, users can't join channel meetings if they're not a member of the team. The root cause is that IB checks rely on whether users can be added to a meeting chat roster, and only when they can be added to the roster are they allowed to join the meeting. The chat thread in a channel meeting is available to Team/Channel members only, and non-members can't see or access the chat thread. If you enable IB for the organization and a non-team member attempts to join a channel meeting, that user isn't allowed to join the meeting. However, if you don't enable IB for the organization and a nonteam member attempts to join a channel meeting, the user is allowed to join the meeting but they don't see the chat option in the meeting.
-IB policies don't work for federated users
-: If you allow federation with external organizations, the users of those organizations aren't restricted by IB policies. If users of your organization join a chat or meeting organized by external federated users, then IB policies also don't restrict communication between users of your organization.
+IB policies are supported in federated communication
+: If you allow federation with external organizations, the users of those organizations aren't restricted by IB policies. If users of your organization join a group chat, meeting chat, or a call organized by external federated users, IB policies continue to restrict communication between users of your organization.
 Next steps
 Use Information Barriers with SharePoint
 : Enable IB on SharePoint sites connected to Teams.

```

---

### 15. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -37,6 +37,12 @@ for data governance solutions.
 Roadmap
 for data security and risk and compliance solutions.
+June 2026
+Data Loss Prevention
+New
+:
+Access Endpoint DLP device attribute data using Advanced Hunting
+. Query Endpoint DLP device configuration and policy sync attributes at scale through the DeviceInfo table's DlpInfo column in Advanced hunting in the Microsoft Defender portal, instead of relying on point-in-time exports from the Microsoft Purview portal.
 May 2026
 Agent 365
 General availability (GA)
@@ -44,18 +50,6 @@ Data security and compliance protections for Microsoft Agent 365
 .
 Data Governance
-In preview
-:
-Search for governed assets
-in Unified Catalog. Instead of searching across all assets, you can conduct a focused search of data assets that are activiely governed. Governed assets search supports semantic search, partial keyword matching, exact phrase matching with double quotes, and hover highlights that show why a result was returned.
-Updated
-:
-Data products search
-now supports partial keyword matching, exact phrase matching with double quotes, and hover highlights that show which attributes matched your search query.
-Updated
-: Release of additional
-APIs for data assets and columns
-.
 General availability (GA)
 :
 Standalone data asset data quality scan
@@ -89,6 +83,29 @@ : Removed DeepL and Zapier from the
 list of unmanaged AI apps supported by browser policies in Edge for Business
 .
+In preview
+: New
+Block access for specific external domains or users
+sub-option for the
+Restrict access or encrypt the content in Microsoft 365 locations
+action lets DLP policies for SharePoint and OneDrive block access to sensitive files for specific external domains or user SMTPs. See
+Actions
+and
+Help prevent sharing sensitive items via SharePoint and OneDrive with external users
+.
+Data Security Investigations
+New
+:
+OCR support
+in Data Security Investigations. Image files are automatically processed with optical ch
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Connector Reference
**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Classification:** MEDIUM (General content update)

---

### 2. Power Platform Inventory
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Classification:** CRITICAL (Deprecation notice)

---

### 3. Regions Overview
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/regions-overview
**Classification:** MEDIUM (General content update)

---

### 4. Capacity Storage
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Classification:** CRITICAL (Deprecation notice)

---

### 5. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)

---

### 6. Data, Privacy, and Security
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Classification:** MEDIUM (General content update)

---

### 7. Agent 365 Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/overview
**Classification:** MEDIUM (General content update)

---

### 8. DSPM for AI
**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Classification:** MEDIUM (General content update)

---

### 9. Admin Roles
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Classification:** MEDIUM (General content update)

---

### 10. Microsoft 365 Licensing
**URL:** https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview?view=o365-worldwide
**Classification:** MEDIUM (General content update)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/architecture/ | https://learn.microsoft.com/en-us/agents/architecture/ |

---

## Errors

- **Encryption** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/admin/manage-encryption-key

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*