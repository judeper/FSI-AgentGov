# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-19
**Run Time:** 2026-08-19T06:44:19.650230+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 20 |
| MEDIUM Changes | 2 |
| Redirects | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | manage-copilot-studio-messages-capacity | HIGH | 2.27 | Update portal-walkthrough |
| 2 | planned-features | CRITICAL | 3.8, 2.25, 2.17, 1.4 | Review and update |
| 3 | microsoft-365-copilot-overview | HIGH | 3.8 | Review and update |
| 4 | microsoft-365-copilot-privacy | HIGH | 4.6, 4.7, 2.23 | Update portal-walkthrough |
| 5 | microsoft-365-copilot-enable-users | HIGH | None | Review and update |
| 6 | manage-copilot-agents-integrated-apps | HIGH | 3.11, 3.6, 3.1, 3.8, 2.25 | Review and update |
| 7 | microsoft-365-copilot-usage | CRITICAL | 3.8 | Review and update |
| 8 | overview | HIGH | 3.8 | Review and update |
| 9 | security-governance | HIGH | None | Review and update |
| 10 | management-controls | HIGH | 3.8 | Review and update |
| 11 | agent-essentials-overview | HIGH | 2.25 | Review and update |
| 12 | agent-prerequisites | HIGH | 2.25 | Review and update |
| 13 | m365-agents-visual-map | HIGH | 1.1 | Review and update |
| 14 | m365-agents-checklist | HIGH | 3.5, 3.1, 1.6, 1.5, 1.1, 1.11 | Review and update |
| 15 | m365-agents-blueprint | HIGH | 2.3, 2.1, 1.11 | Review and update |
| 16 | agent-365-overview | HIGH | 3.8, 2.25 | Review and update |
| 17 | restricted-access-control | HIGH | 4.1, 1.3 | Review and update |
| 18 | restricted-content-discovery | HIGH | 4.6, 4.7, 4.1, 1.14, 1.3 | Review and update |
| 19 | restricted-sharepoint-search | HIGH | 4.6, 4.7, 4.1, 1.14, 1.3 | Review and update |
| 20 | advanced-management | MEDIUM | 4.6, 4.5, 4.2, 4.1, 1.3 | Review and update |
| 21 | site-lifecycle-management | CRITICAL | 4.3, 4.2 | Review and update |
| 22 | request-site-attestations | CRITICAL | 4.2 | Monitor |
| 23 | insights-on-sharepoint-agents | HIGH | 4.5 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Copilot Studio Message Capacity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:272c7848afebe4b586646dc28e4fd4cb12c897dc7bbb60aa0765787cd00add0b

**Affected Controls:**
- Control 2.27: Control 2.27: Consumption-Entitlement Governance
  - File: `controls/pillar-2-management/2.27-consumption-entitlement-governance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.27/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.27/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.27/verification-testing.md` (HIGH)

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
@@ -19,10 +19,12 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Manage Copilot Studio credits and capacity
+Manage Copilot Credits and capacity for Copilot Studio
 Feedback
 Summarize this article for me
-The Microsoft Copilot Studio capacity management experience in the Power Platform admin center allows administrators to manage Copilot Studio credit capacity, while monitoring overall capacity consumption. This experience provides an overview of the licensing models in use. This experience allows administrators to efficiently manage their available session capacity.
+Important
+Microsoft Copilot Studio is a multi-harness platform. The Power Platform admin center (PPAC) provides a unified capacity management experience across all Copilot Studio harnesses, including Copilot Chat, Standard, and GitHub Copilot. Administrators can view capacity and consumption data at the agent and environment level in PPAC.
+The Microsoft Copilot Studio capacity management experience in the Power Platform admin center enables administrators to manage Copilot Studio credit capacity and monitor overall capacity consumption. This experience provides an overview of the licensing models in use. Administrators can efficiently manage their available session capacity.
 View summary information
 Sign in to the
 Power Platform admin center
@@ -41,26 +43,28 @@ Summary
 tab.
 The licensing summary view shows usage of both prepaid and session-based capacity units.
-Purchasing a Copilot Studio license includes a specified number of billed Copilot credits pooled across the tenant, which must be assigned to an environment to allow Copilot Studio features for agents in that environment.
-Capacity management features allow administrators to allocate prepurchased capacity across environments, within the tenant, based on anticipated usage of Copilot a
```

---

### 2. Data, Privacy, and Security

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:dfe9978e4f43c306d4eacbfffd653694bb420b86967eb435426b2c208b30e301

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Copy Markdown
 Print
 Note
@@ -18,87 +18,92 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Data, Privacy, and Security for Microsoft 365 Copilot
+Data, Privacy, and Security for Microsoft Copilot
 Feedback
 Summarize this article for me
-Microsoft 365 Copilot is a sophisticated processing and orchestration engine that provides AI-powered productivity capabilities by coordinating the following components:
+Note
+Microsoft 365 Copilot is now named Microsoft Copilot, and Microsoft 365 Copilot Chat is now named Microsoft Copilot Chat. Some experiences, licenses, and capabilities might continue to reference Microsoft 365 Copilot and Microsoft 365 Copilot Chat during the transition period. There are no changes to security, compliance, and privacy for organizations.
+Microsoft Copilot is a sophisticated processing and orchestration engine that provides AI-powered productivity capabilities by coordinating the following components:
 Large language models (LLMs)
 Content in Microsoft Graph, such as emails, chats, and documents that you have permission to access.
 The Microsoft 365 productivity apps that you use every day, such as Word and PowerPoint.
 For an overview of how these three components work together, see
-Microsoft 365 Copilot overview
-. For links to other content related to Microsoft 365 Copilot, see
-Microsoft 365 Copilot documentation
+Microsoft Copilot overview
+. For links to other content related to Microsoft Copilot, see
+Microsoft Copilot documentation
 .
 Important
-Microsoft 365 Copilot, including
-Microsoft 365 Copilot Search
+Microsoft Copilot, including
+Microsoft Copilot Search
 , is compliant with our existing privacy, security, and compliance commitments to Microsoft 365 commercial customers, including the General Data Protection Regulation (GDPR) and European Union (EU) Data Boundary.
-Prompts, responses, and data acces
```

---

## HIGH: Control Review Recommended

### 1. Planned Features (2026 Wave 1) [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:759e460fa8cb599536857869311affa87a0f3ed2ef675445c1b0f2b0aa5ffe37

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -1,156 +1,502 @@-Table of contents
-Exit editor mode
-Ask Learn
-Ask Learn
-Reading mode
-Table of contents
-Read in English
-Add
-Add to plan
-Edit
-Copy Markdown
-Print
-Note
-Access to this page requires authorization. You can try
-signing in
-or
-changing directories
-.
-Access to this page requires authorization. You can try
-changing directories
-.
-What's new and planned for Microsoft Copilot Studio
-Feedback
-Summarize this article for me
-This topic lists features that are planned to release from April 2026 through September 2026. Because this topic lists features that may not have released yet,
-delivery timelines may change and projected functionality may not be released
-. For more information, go to
-Microsoft policy
-.
-For a list of the previous wave's release plans, go to
-2025 release wave 2 plan
-.
-In the
-General availability
-column, the feature will be delivered within the month listed. The delivery date can be any day within that month. Released features show the full date, including the date of release.
-This check mark (
-) shows which features have been released for public preview and general availability.
-Copilot and AI innovation
-Use industry leading generative AI capabilities in Microsoft Copilot Studio to do the work so you and your team don't have to.
-Feature
-Enabled for
-Public preview
-General availability
-Automate web and desktop apps with computer use
-Admins, makers, marketers, or analysts, automatically
-May 27, 2025
-May 7, 2026
-Give read-only analytics access to users
-Admins, makers, marketers, or analysts, automatically
--
-Apr 28, 2026
-Use code interpreter on SharePoint sources in agent conversations
-Admins, makers, marketers, or analysts, automatically
-Mar 16, 2026
-May 2026
-Define custom metrics for analytics
-Admins, makers, marketers, or analysts, automatically
-Apr 15, 2026
-Jul 2026
-Analyze quality of responses that use generative AI
-Admins, makers, marketers, or analysts, automatically
-Jun 17, 
```

---

### 2. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:feffa90ba4a6e5581fe5835a872102d61e18461455f412d384e4dec6704c0f64

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
@@ -19,39 +19,40 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Microsoft 365 Copilot overview
+Microsoft Copilot overview
 Feedback
 Summarize this article for me
 Note
-Microsoft onboarded Anthropic as a Microsoft subprocessor. As a subprocessor, Anthropic operates with
-Microsoft Enterprise data protections
-. For more information, see
+Microsoft has onboarded OpenAI as a Microsoft subprocessor. For more information, see
+OpenAI as a subprocessor in Microsoft Online Services
+.
+Microsoft has onboarded Anthropic as a Microsoft subprocessor. For more information, see
 Anthropic as a subprocessor for Microsoft Online Services
 .
-Microsoft 365 Copilot is an AI-powered tool that helps with your work tasks
+Microsoft Copilot is an AI-powered tool that helps with your work tasks
 .
 Users enter a prompt in Copilot and Copilot responds with AI-generated information. The responses are in real-time and can include internet-based content and work content that users have permission to access.
 Users get content relevant to their work tasks, and in the context of the Microsoft 365 app they're using.
-The following video provides an overview of Microsoft 365 Copilot. It's 1 minute and 49 seconds long.
-Using Microsoft 365 Copilot
+The following video provides an overview of Microsoft Copilot. It's 1 minute and 49 seconds long.
+Using Microsoft Copilot
 Say, for example, you're an operations manager and are working with human resources to update job descriptions. By providing Copilot the basic job requirements, you can ask Copilot to create a job description. You can also have Copilot add various job requirements and qualifications that should be included in the description. In the same prompting session, you can expand the generated job description to create different levels, like Level 1, Level 2, and Level 3.
 You can 
```

---

### 3. Manage Copilot

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-enable-users
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:dc1a6a692f45aa52ba50bf8ebfe841fcf49bb2362b95b5b7ecc78297c0df5b90

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
@@ -19,28 +19,28 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Welcome users, create organizational messages, and enable feedback for Microsoft 365 Copilot
+Welcome users, create organizational messages, and enable feedback for Microsoft Copilot
 Feedback
 Summarize this article for me
-Microsoft 365 Copilot
+Microsoft Copilot
 is an AI-powered productivity tool that helps users with everyday tasks.
 As part of your
-Microsoft 365 Copilot adoption
-, a welcome email to your Microsoft 365 Copilot users is sent on license assignment that announces Microsoft 365 Copilot and its features. You can also enable feedback for Microsoft 365 Copilot users.
+Microsoft Copilot adoption
+, send a welcome email to your Microsoft Copilot users on license assignment that announces Microsoft Copilot and its features. You can also enable feedback for Microsoft Copilot users.
 Additionally, admins can use Organizational Messaging in the Microsoft Admin Center to deliver tailored in-product messages to your users directly through Teams.
-This article provides information about how to send users a welcome email, enable feedback, send organizational messages, and review the Microsoft 365 Copilot usage activity report.
+This article provides information about how to send users a welcome email, enable feedback, send organizational messages, and review the Microsoft Copilot usage activity report.
 This article applies to:
-Microsoft 365 Copilot
+Microsoft Copilot
 Send welcome email
-After you assign a Microsoft 365 Copilot license to a user, they will automatically be sent a notification email that can look like the following email.
+After you assign a Microsoft Copilot license to a user, the system automatically sends a notification email that can look like the following email.
 The welcome email also includes a link to
 Microsoft Cop
```

---

### 4. Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:bd26397bf389b6c1d901c68b6f32f33ca5d5671e2f688faf9353d6ec312322bb

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

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
@@ -24,15 +24,15 @@ Summarize this article for me
 Important
 This article is intended for IT administrators.
-The capability is enabled by default in all Microsoft 365 Copilot licensed tenants.
-Microsoft 365 Copilot combines the power of large language models with your data and apps in Microsoft 365. It captures natural language commands to produce content and analyze data. It enables access to and use of other apps, such as Jira,
+The capability is enabled by default in all Microsoft Copilot licensed tenants.
+Microsoft Copilot combines the power of large language models with your data and apps in Microsoft 365. It captures natural language commands to produce content and analyze data. It enables access to and use of other apps, such as Jira,
 Dynamics 365
 , or Bing Web Search.
 You can manage agents for Copilot by using the
 Microsoft 365 admin center
 . You can enable, disable, assign, block, or remove agents for your organization, and manage Copilot capabilities.
 Note
-Researcher and Analyst are first-party Microsoft experiences built on the same foundation as Microsoft 365 Copilot, operating entirely within the Microsoft 365 commercial data processing boundary. These tools inherit all existing security, privacy, and compliance commitments that apply across the suite of Microsoft 365 products. These tools are available in Microsoft 365 Copilot Chat under
+Researcher and Analyst are first-party Microsoft experiences built on the same foundation as Microsoft Copilot, operating entirely within the Microsoft 365 commercial data processing boundary. These tools inherit all existing security, privacy, and compliance commitments that apply across the suite of Microsoft 365 products. These tools are available in Microsoft Copilot Chat under
 Tools
 and can be invoked by the user anytime. While Researcher and Analyst coexist with agents and abide by 
```

---

### 5. Copilot Usage Reports

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:0217bee0f0795c6c79169f74ea59691e5e92670919cbf34135070515326ac3db

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)

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
@@ -19,14 +19,14 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Microsoft 365 Copilot usage report
+Microsoft Copilot usage report
 Feedback
 Summarize this article for me
-The Microsoft 365 Copilot usage report provides a summary of how users adopt, retain, and engage with Microsoft 365 Copilot and its associated enabled apps, including agent usage. For Copilot activity on a given day, the report typically becomes available within 72 hours of the end of that day (in UTC).
+The Microsoft Copilot usage report provides a summary of how users adopt, retain, and engage with Microsoft Copilot and its associated enabled apps. For Copilot activity on a given day, the report typically becomes available within 48 hours of the end of that day (in UTC).
 For general information about usage reports in the Microsoft 365 admin center, and to see a list of all available reports, see
 Microsoft 365 admin center usage reports overview
 .
-View the Microsoft 365 Copilot usage report in the Microsoft 365 admin center
+View the Microsoft Copilot usage report in the Microsoft 365 admin center
 For information about the roles needed to view usage reports, see "Before you begin" in
 Microsoft 365 admin center usage reports overview
 Go to the
@@ -49,20 +49,20 @@ page, under
 Reports
 , select
-Microsoft 365 Copilot
+Microsoft Copilot
 , and then select
 Copilot
 .
 On the report page, select the
 Usage
 tab to view adoption and usage metrics.
-Interpret the Microsoft 365 Copilot usage report
-At the top, you can filter by different timeframes. You can view the Microsoft 365 Copilot report over the last 7, 30, 90, or 180 days.
-You can view several numbers for Microsoft 365 Copilot usage, which highlight the enablement number and the adoption of the enablement:
+Interpret the Microsoft Copilot usage report
+At the top, you can filter b
```

---

### 6. Copilot Control System Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:3b724093391de342dd0a4ebcc294414c43b803115dc826a736cef663ce32e820

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
@@ -22,9 +22,9 @@ Copilot Control System overview
 Feedback
 Summarize this article for me
-The Copilot Control System is a framework of integrated controls and capabilities for Microsoft 365 Copilot and agents. Use it to help secure data that Copilot and agents create or reference, manage Copilot and agent experiences, and measure and analyze adoption and impact across your organization.
+The Copilot Control System is a framework of integrated controls and capabilities for Microsoft Copilot and agents. Use it to help secure data that Copilot and agents create or reference, manage Copilot and agent experiences, and measure and analyze adoption and impact across your organization.
 It provides a governance structure for the use of:
-Microsoft 365 Copilot
+Microsoft Copilot
 Copilot Chat
 Microsoft 365 prebuilt agents
 Agents your organization creates in Microsoft Copilot Studio and publish to Microsoft 365 channels
@@ -45,7 +45,7 @@ Security and governance
 .
 Management controls
-Copilot Control System management controls help you decide how to deploy your Microsoft 365 Copilot licenses and agents to fit your organization's unique needs. You can find Copilot and agent management controls mainly in the Microsoft 365 admin center, Power Platform admin center, and Copilot Studio.
+Copilot Control System management controls help you decide how to deploy your Microsoft Copilot licenses and agents to fit your organization's unique needs. You can find Copilot and agent management controls mainly in the Microsoft 365 admin center, Power Platform admin center, and Copilot Studio.
 The management controls pillar of the Copilot Control System focuses on the following key capabilities:
 Licensing and metering
 Agent lifecycle
@@ -66,7 +66,7 @@ Microsoft Support
 offers many resources to help you get your entire organization on board and help users adopt these p
```

---

### 7. Copilot Control System - Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/security-governance
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:951b45f6baf149898aae76da26acd76e1edd4534b1257daf5ba6043e17e04b77

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
@@ -22,9 +22,9 @@ Copilot Control System security and governance
 Feedback
 Summarize this article for me
-When you implement Microsoft 365 Copilot and agents, you might face new and amplified risks related to security, compliance, privacy, and governance. This security and governance framework helps you mitigate these issues in the following components:
-Microsoft 365 Copilot
-Microsoft 365 Copilot Chat
+When you implement Microsoft Copilot and agents, you might face new and amplified risks related to security, compliance, privacy, and governance. This security and governance framework helps you mitigate these issues in the following components:
+Microsoft Copilot
+Microsoft Copilot Chat
 Microsoft 365 prebuilt agents
 Agents created in Microsoft Copilot Studio and published to Microsoft 365 channels
 This article refers to
@@ -132,7 +132,7 @@ Optimized AI security controls
 In Microsoft Purview with an A5/E5/G5 license, you get the following optimized AI security controls:
 To prevent Copilot and agents from processing certain sensitive files and from using them in responses, use
-Microsoft Purview Data Loss Prevention for Microsoft 365 Copilot and agents
+Microsoft Purview Data Loss Prevention for Microsoft Copilot and agents
 .
 To get alerted to risky AI use, such as an attempted prompt injection attack or use of sensitive data, use
 Microsoft Purview Insider Risk Management
@@ -144,7 +144,7 @@ Microsoft Purview Data Security Posture Management for AI
 .
 Compliance and privacy
-The third aspect of security and governance in the Copilot Control System is to ensure that you can monitor, audit, and manage how Copilot and agent interactions comply with regulatory and internal standards. Use Microsoft Purview to provide comprehensive oversight of Copilot activities. With these controls, you can protect sensitive information, maintain privacy, and d
```

---

### 8. Copilot Control System - Management Controls

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/management-controls
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:af0ce968dc93d9bfbfa786eccedacb895e24834b6b16464210c3479ffefa6dfb

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
@@ -22,7 +22,7 @@ Copilot Control System management controls
 Feedback
 Summarize this article for me
-Copilot Control System management controls help you decide how to deploy and customize your Microsoft 365 Copilot licenses and agents to fit your organization's unique needs. You can find Copilot and agent management controls mainly in the
+Copilot Control System management controls help you decide how to deploy and customize your Microsoft Copilot licenses and agents to fit your organization's unique needs. You can find Copilot and agent management controls mainly in the
 Microsoft 365 admin center
 ,
 Power Platform admin center
@@ -42,14 +42,14 @@ Agent lifecycle
 Customization
 Licensing and metering
-To manage the costs associated with deploying Copilot, your organization needs control over the deployment and usage of Microsoft 365 Copilot services. This capability includes controls for the use of per-user, per-month licenses and pay-as-you-go services. These pay-as-you-go services include license management, policies, and usage limits. You can also monitor message capacity for both prepaid and pay-as-you-go consumption.
+To manage the costs associated with deploying Copilot, your organization needs control over the deployment and usage of Microsoft Copilot services. This capability includes controls for the use of per-user, per-month licenses and pay-as-you-go services. These pay-as-you-go services include license management, policies, and usage limits. You can also monitor message capacity for both prepaid and pay-as-you-go consumption.
 Copilot and Copilot chat in the Microsoft 365 admin center
 Use the
 Microsoft 365 admin center
-to manage Microsoft 365 Copilot and Copilot Chat licensing. You can also configure pay-as-you-go billing so that you only pay when users use it.
+to manage Microsoft Copilot and Copilot Chat licensing. You can al
```

---

### 9. Agent Management Essentials Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-essentials-overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:84798b8e8bc6d0d1df272e0bda3f09cbd13e206f3fb134a791839025cd2d81ee

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

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
@@ -27,7 +27,7 @@ Prerequisites
 - Understand licensing requirements, admin permissions, and access controls.
 Blueprint
-- Understand how to enable Microsoft 365 Copilot at scale.
+- Understand how to enable Microsoft Copilot at scale.
 Checklist
 - Understand how to successfully implement and deploy agent governance.
 Visual Guide
@@ -43,17 +43,17 @@ Microsoft Agent 365 documentation
 .
 Understand agent security, privacy, and compliance
-Microsoft applies a multi-layered, defense-in-depth strategy to secure Microsoft 365 Copilot at every level, grounded in enterprise security, privacy, and compliance standards. Each aspect of this foundation forms a safer digital ecosystem for you and your organization to confidently adopt AI features and tools.
+Microsoft applies a multi-layered, defense-in-depth strategy to secure Microsoft Copilot at every level, grounded in enterprise security, privacy, and compliance standards. Each aspect of this foundation forms a safer digital ecosystem for you and your organization to confidently adopt AI features and tools.
 Agents use this foundation as part of Copilot's AI
 infrastructure
 ,
 model
 , and
 orchestrator
-, which means agents adhere to the security, privacy, and compliance that is provided by Microsoft 365 Copilot.
+, which means agents adhere to the security, privacy, and compliance that is provided by Microsoft Copilot.
 Note
 Your organization's data is maintained within the Microsoft 365 service boundary within your tenant. For more information, see
-Microsoft 365 Copilot architecture and how it works
+Microsoft Copilot architecture and how it works
 .
 Copilot and agents only access data that
 individual users are authorized to access
@@ -62,16 +62,16 @@ .
 When you integrate your business workflows as agents for Copilot, your internal data stays within your agent. That data doesn't flow out of
 Mi
```

---

### 10. Agent Prerequisites

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-prerequisites
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:880e8e1b85668edbb1f5f9c1c37115404033dc73eda93f3383a21f3beccdfc56

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

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
@@ -22,20 +22,20 @@ Prerequisites for managing agents in Microsoft 365
 Feedback
 Summarize this article for me
-Organizations typically deploy a combination of Microsoft 365 Copilot Chat and Microsoft 365 Copilot. Before you get started, it's important to understand the differences between these two offerings and the licensing involved when deploying and using agents. Agents allow you and your end users to extend Copilot's knowledge, automate complex workflows, and deliver tailored user experiences.
+Organizations typically deploy a combination of Microsoft Copilot Chat and Microsoft Copilot. Before you get started, it's important to understand the differences between these two offerings and the licensing involved when deploying and using agents. Agents allow you and your end users to extend Copilot's knowledge, automate complex workflows, and deliver tailored user experiences.
 Note
-Before your organization assigns or deploys an agent, first consider your organization's objectives, technical requirements, costs, Responsible AI (RAI) considerations, and compliance factors. For more information, see Microsoft 365 Copilot extensibility planning guide.
+Before your organization assigns or deploys an agent, first consider your organization's objectives, technical requirements, costs, Responsible AI (RAI) considerations, and compliance factors. For more information, see Microsoft Copilot extensibility planning guide.
 Licensing requirements
-Microsoft 365 Copilot Chat
+Microsoft Copilot Chat
 is available at no additional cost for all Microsoft Entra account users with a Microsoft 365 or Office 365 subscription. Members of your organization can use agents that are available at no additional cost from the Agent Store. You, as the administrator of your organization, would also need to enable these agents. If your organization requires agents that incorpo
```

---

### 11. Visual Governance Guide

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-visual-map
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:790df591632661eaf8f88e2b5bbaf6ddbba45233e5e35abe5d2314a1a2785c28

**Affected Controls:**
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`

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
@@ -23,14 +23,14 @@ Feedback
 Summarize this article for me
 To help understand the structure and flow of the
-Microsoft 365 Copilot Agent Management Essentials checklist
+Microsoft Copilot Agent Management Essentials checklist
 , you can view the visual guide. This mind map provides a graphical representation of the key concepts and actions outlined in the checklist, making it easier to understand relationships between sections and navigate the framework at a glance.
 Each branch of the mind map corresponds to a major heading in the checklist, with subbranches breaking down detailed steps, considerations, and best practices. By presenting the content visually, the mind map serves as a quick reference tool for planning, implementing, and validating Copilot agents within your organization.
 An image of the relevant portion of the mind map is included in each section of this article. However, to view the entire mind map and access the related links, download the Agents visual guide for Microsoft 365 PDF.
 Download
 :
 Agents visual guide for Microsoft 365 PDF
-Manage Microsoft 365 Copilot agent access and availability policies
+Manage Microsoft Copilot agent access and availability policies
 Agent policies refer to the tenant settings you can make as an administrator in the Copilot Control System within Microsoft 365 admin center. Choose how you manage access to agents, as well as share and publish agents. For more information, see
 Microsoft 365 agents deployment checklist
 .
@@ -50,7 +50,7 @@ When you need to provide powerful AI assistants that retrieve real-time insights and act on behalf of users, as well as create specialized workflows, you can use Copilot Studio to create custom agents. For more information, see
 Microsoft 365 agents deployment checklist
 .
-Manage Microsoft 365 Copilot agent inventory and lifecycle
+Manage Microsoft Copilot age
```

---

### 12. Deployment Checklist

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-checklist
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:7c8da0d49f5dad19eed28d395acc2565e194deda8a1693d2199dfbb6322cf9ab

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
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
@@ -39,7 +39,7 @@ :
 Agents blueprint for Microsoft 365
 Agents visual guide for Microsoft 365
-Manage Microsoft 365 Copilot agent access and availability policies
+Manage Microsoft Copilot agent access and availability policies
 Agent policies refer to the tenant settings you can make as an administrator in the Copilot Control System within Microsoft 365 admin center. Agent policies relate to the available settings for all agents in your tenant.
 Step
 Task
@@ -145,7 +145,7 @@ Description
 Administrator
 1
-Understand how to extend Microsoft 365 Copilot with agents
+Understand how to extend Microsoft Copilot with agents
 Learn how to create and configure a custom agent using Copilot Studio.
 Copilot administrator, Microsoft 365 administrator
 2
@@ -170,9 +170,9 @@ Copilot administrator, Microsoft 365 administrator
 7
 Publish an agent
-You can publish agents to engage with your customers on multiple platforms or channels, such as live websites, mobile apps, Microsoft 365 Copilot or messaging platforms like Teams and Facebook.
-Copilot administrator, Microsoft 365 administrator
-Manage Microsoft 365 Copilot agent inventory and lifecycle
+You can publish agents to engage with your customers on multiple platforms or channels, such as live websites, mobile apps, Microsoft Copilot or messaging platforms like Teams and Facebook.
+Copilot administrator, Microsoft 365 administrator
+Manage Microsoft Copilot agent inventory and lifecycle
 You can manage your organization's available agents in the Copilot Control System (CCS) within Microsoft 365 admin center.
 Step
 Task
@@ -201,7 +201,7 @@ AI administrator, Global administrator, Global reader (view-only, no edit)
 4
 Manage Copilot connectors
-Microsoft 365 Copilot connectors provide a platform for you to ingest your unstructured, line-of-business data into Microsoft Graph, so that Microsoft 365 Copilot ca
```

---

### 13. Deployment Blueprint

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-blueprint
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:3a03e6d2ee3fa20e60b403c1f2fa8dbb9dae09419c881ed29a4ed367b08b0dcc

**Affected Controls:**
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
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
@@ -23,21 +23,21 @@ Feedback
 Summarize this article for me
 This deployment blueprint helps you enable agents in
-Microsoft 365 Copilot
+Microsoft Copilot
 at scale, while ensuring data security and governance, managing access and costs, and measuring adoption and impact.
 Note
 This blueprint is scoped primarily to agents created in the
 Agent Builder
-experience using the Microsoft 365 Copilot app.
+experience using the Microsoft Copilot app.
 The primary challenges when enabling agents in Microsoft 365 include the following:
 Security and governance concerns
-- Your organization can address oversharing, data protection, and compliance risks by implementing robust security and governance controls to safely enable agents in Microsoft 365 Copilot.
+- Your organization can address oversharing, data protection, and compliance risks by implementing robust security and governance controls to safely enable agents in Microsoft Copilot.
 Deployment complexity
-- Agents in Microsoft 365 Copilot introduce new admin tools and processes. This guidance can help address user enablement and cost management complexity.
+- Agents in Microsoft Copilot introduce new admin tools and processes. This guidance can help address user enablement and cost management complexity.
 Visibility and impact gaps
 - By reviewing and acting on agent data, you can better measure success. Agent data can also provide usage to manage costs and help assess business value.
 By addressing these challenges, you can better drive innovation while maintaining security, control, and visibility. This blueprint can help, by providing shorter, actionable, and prescriptive guidance.
-In this deployment blueprint, we provide a recommended approach to address concerns throughout a Microsoft 365 Copilot agent deployment. The blueprint breaks the deployment into three phases:
+In this deployment bluepr
```

---

### 14. Agent 365 Overview Page (M365 Admin)

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:b51a8579ce2aebf03ba67f199ff49ed877497b81a4cf15be6bb5386175b5c3cd

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.25/powershell-setup.md` (HIGH)

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
@@ -55,9 +55,9 @@ .
 Prerequisites for agent management
 Before you can manage agents in the Microsoft 365 admin center, confirm the following requirements are met:
-Your organization has the required subscription and licenses for either Microsoft 365, Microsoft 365 Copilot, or Microsoft Agent 365.
+Your organization has the required subscription and licenses for either Microsoft 365, Microsoft Copilot, or Microsoft Agent 365.
 Users at your organization that create, publish, or use agents have the appropriate licenses assigned.
-Youâre assigned an administrator role that includes permissions to manage settings for Microsoft 365, Microsoft 365 Copilot, or Microsoft Agent 365 in the Microsoft 365 admin center.
+Youâre assigned an administrator role that includes permissions to manage settings for Microsoft 365, Microsoft Copilot, or Microsoft Agent 365 in the Microsoft 365 admin center.
 For more information, see the following resources:
 Licensing for agent management
 Agent management roles and permissions
@@ -65,14 +65,14 @@ The following licensing options include agents that can be managed in Microsoft 365 admin center:
 Microsoft 365 plans
 Microsoft 365 (All Suites) includes Copilot Chat. Copilot Chat provides web data agents.
-Microsoft 365 (E7) includes Microsoft 365 E5, Microsoft 365 Copilot, Microsoft Agent 365, and Microsoft Entra Suite.
-Microsoft 365 Copilot
+Microsoft 365 (E7) includes Microsoft 365 E5, Microsoft Copilot, Microsoft Agent 365, and Microsoft Entra Suite.
+Microsoft Copilot
 This license can be added to your Microsoft 365 license (E3, E5). It's included with your Microsoft 365 license (E7). This option provides both web and work data agents.
 Microsoft Agent 365
 Microsoft Agent 365 is also included in Microsoft 365 (E7).
 Note
-To compare Copilot Chat and Microsoft 365 Copilot, see
-License options for Microsoft 365 C
```

---

### 15. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:cefc88dc52326086e76efe3a04c9f0b5bc6f5f5fa7ebb28a84934b31e7b6fd15

**Affected Controls:**
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

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

### 16. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:97871ba386e516a712dfcf4b5f101a544f007d3c8bd625295eb84ff5ad10a7db

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

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
@@ -22,108 +22,132 @@ Restrict discovery of SharePoint sites and content
 Feedback
 Summarize this article for me
-For organizations onboarding to Microsoft 365 Copilot, maintaining strong data governance controls for SharePoint content is critical to deploying Copilot in a safe manner. Sites identified with the highest risk of oversharing can use Restricted Content Discovery to protect content while taking time to ensure that permissions are accurate and well-managed.
-With Restricted Content Discovery, organizations can limit the ability of end users to search for files from specific SharePoint sites. Enabling Restricted Content Discovery for each site prevents the sites from surfacing in organization-wide search and Microsoft 365 Copilot Business Chat, unless a user had a recent interaction.
-Restricted Content Discovery is a site-level setting that needs to be propagated to the search index, a large number of transactions could lead to a long queue in the ingestion pipeline and higher update latency times.
-While child content is hidden by default, users in your organization can still discover files they own or recently interacted with. End users can still find relevant content they need for their day-to-day tasks, even if Restricted Content Discovery is applied to the parent site.
-Restricted Content Discovery doesn't affect searches originating from a site context or other intelligent features such as Microsoft 365 Feed and Recommendations.
+Organizations preparing for Microsoft Copilot often need time to review SharePoint sites, validate permissions, and implement governance controls before making content broadly discoverable. Restricted Content Discovery (RCD) helps you limit discovery of content from specific SharePoint sites, including recently interacted files, in organization-wide search results and Microsoft Copilot responses while thos
```

---

### 17. Restricted SharePoint Search

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search
**Section:** SharePoint Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:b30ea00eea1e64352a4b2690963e6347bc660efae0be1b84a72d22c0778106b4

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

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
@@ -23,21 +23,24 @@ Feedback
 Summarize this article for me
 Important
-Restricted SharePoint Search is designed for customers of Microsoft 365 Copilot chat and agentic experiences. It's designed as a short-term solution to allow time for your organization's administrators to thoroughly review and audit site and file permissions, but it's not intended or scalable for long-term use. Comprehensive data security solutions are available, including
+Restricted SharePoint Search is retiring. Starting July 31, 2026, new enablement is blocked. Use comprehensive data controls such as
+Restricted Content Discovery
+(RCD) for content discoverability.
+Restricted SharePoint Search is designed for customers of Microsoft Copilot Chat and agentic experiences. It's a short-term solution that gives your organization's administrators time to review and audit site and file permissions. It's not intended or scalable for long-term use. Comprehensive data security solutions are available, including
 SharePoint Advanced Management
 and
 Microsoft Purview
 .
 What is Restricted SharePoint Search?
-Restricted SharePoint Search is a setting that enables you as a
+Restricted SharePoint Search is a setting that you, as a
 SharePoint Administrator
 or
 other Microsoft 365 administrator
-to maintain a list of SharePoint sites (an "allowed list") for which you have checked permissions and applied data governance. The allowed list defines which SharePoint sites can be used in organization-wide search queries, and, as a temporary measure, Copilot chat and agentic experiences.
-By default, the Restricted SharePoint Search setting is turned off and the allowed list is empty. If Restricted SharePoint Search is enabled, users can interact with files and content they own or have previously accessed in Copilot.
+, use to maintain a list of SharePoint sites (an "allow list") for which you
```

---

### 18. Advanced Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:3888e0c69900c278353ca920abfc5c2fa687fdcbb7d799b0d1028e3a312be0e0

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

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
@@ -30,8 +30,10 @@ Prevent oversharing
 .
 SAM capabilities are helpful as organizations
-prepare for Microsoft 365 Copilot and agents
+prepare for Microsoft Copilot and agents
 .
+Video: SharePoint Advanced Management overview
+Watch the following video to get an overview of SharePoint Advanced Management:
 Administrators primarily manage SAM through the SharePoint admin center. It's designed for SharePoint and Microsoft 365 administrators who are responsible for governance, risk reduction, and audit readiness. You can also use the
 SharePoint Admin Agent
 to make your SharePoint administration more productive and efficient.
@@ -72,7 +74,7 @@ Get insights on agents in SharePoint
 : Use this report to identify recently created agents across SharePoint and OneDrive sites, and identify sites with the highest number of agents created.
 Use restricted content discovery (RCD)
-: Prevent high-risk SharePoint sites and files from surfacing in Microsoft 365 Copilot and Agentic experiences.
+: Prevent high-risk SharePoint sites and files from surfacing in Microsoft Copilot and Agentic experiences.
 Use data access governance (DAG) reports for SharePoint and OneDrive sites
 : Identify sites that might contain overshared or sensitive content. AI insights can be generated from DAG reports to highlight access risk patterns and recommend next steps. You can also initiate site access reviews from a DAG report. DAG reports include:
 Permission state reports for sites, OneDrive sites, and files
@@ -105,9 +107,9 @@ .
 Related articles
 SharePoint Admin Agent
-Get ready for Microsoft 365 Copilot and Agents with SharePoint Advanced Management
-Configure a secure and governed foundation for Microsoft 365 Copilot
-SharePoint Advanced Management features in Microsoft 365 Copilot licenses
+Get ready for Microsoft Copilot and Agents with SharePoint Advanced Management
+Conf
```

---

### 19. Site Lifecycle Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/site-lifecycle-management
**Section:** SharePoint Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:07fc9a0591180f9ec9a0bd51c5bf172634df65ce1d31d5c14cb6d653aa52a7d8

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

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
@@ -19,399 +19,124 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Manage inactive sites by using inactive site policies
+SharePoint site lifecycle management
 Feedback
 Summarize this article for me
-Site lifecycle management capabilities in
+Site lifecycle management policies in
 Microsoft SharePoint Advanced Management
-help you improve site governance by automating the process of detecting inactive sites and notifying site owners by email. Site owners can then review and confirm whether their sites are still active.
-You can configure an inactive sites policy in the SharePoint admin center. This article describes how to set up an inactive site policy with notifications and enforcement actions.
-Prerequisites for an inactive site policy
-See
-SharePoint Advanced Management prerequisites
+help you maintain site governance at scale. These policies automate common governance tasks, so sites stay active, properly owned, and regularly reviewed throughout their lifecycle.
+Video: Overview of SharePoint Advanced Management
+The following video provides an overview of SharePoint site lifecycle management:
+Site lifecycle management policies don't delete SharePoint sites directly. Instead, the policies notify site owners and administrators, and take actions based on how you configure the policies.
+As your organization creates more SharePoint sites, Microsoft Teams-connected sites, and Microsoft 365 group-connected sites, it becomes increasingly difficult for your administrators to manually identify inactive sites, ownerless sites, or sites that no longer meet business requirements. Site lifecycle management policies help you automate these governance processes by monitoring sites, notifying responsible users, collecting responses, and taking enforcement actions when necessary.
+Benefits of site lifecycle management
+S
```

---

### 20. Agent Insights

**URL:** https://learn.microsoft.com/en-us/sharepoint/insights-on-sharepoint-agents
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c03b57e711d9848347354e0327592de5e3b971f686951061ff9f263d72b31a9f

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

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
@@ -80,7 +80,7 @@ in Microsoft 365. For more information, see
 Getting started with SharePoint Online Management Shell
 .
-To generate and view these reports, ensure the organization has the SharePoint Advanced Management add-on SKU or Microsoft 365 Copilot license.
+To generate and view these reports, ensure the organization has the SharePoint Advanced Management add-on SKU or Microsoft Copilot license.
 With permissions of at least a SharePoint administrator, you can generate and view the insights report by using the following commands:
 To generate a report for the default one-day report duration, run the following command:
 Start-SPOCopilotAgentInsightsReport

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Advanced Management
**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:3888e0c69900c278353ca920abfc5c2fa687fdcbb7d799b0d1028e3a312be0e0

---

### 2. Site Attestation
**URL:** https://learn.microsoft.com/en-us/sharepoint/request-site-attestations
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:85bce0fa6a5908d9c2cbf25b2884ffab155cc89e47b7dde67c26988039f25b83

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