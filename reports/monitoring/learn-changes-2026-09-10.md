# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-10
**Run Time:** 2026-09-10T10:50:05.893817+00:00
**Total URLs Checked:** 231

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 6 |
| MEDIUM Changes | 1 |
| Redirects | 5 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | advanced-connector-policies | CRITICAL | 1.4 | Update portal-walkthrough |
| 2 | microsoft-365-copilot-overview | HIGH | 3.8 | Review and update |
| 3 | overview | HIGH | 3.8 | Review and update |
| 4 | security-governance | HIGH | None | Review and update |
| 5 | management-controls | HIGH | 3.8 | Review and update |
| 6 | m365-agents-visual-map | HIGH | 1.1 | Review and update |
| 7 | m365-agents-checklist | HIGH | 1.1, 1.11, 1.6, 1.5, 3.1, 3.5 | Review and update |
| 8 | concept-responsible-ai | MEDIUM | 2.21 | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Advanced Connector Policies

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:adea069eafeb293ccb3578468517b91b63275f3cf6e76ca9dcc2974f76c08f17

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.4/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)

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
@@ -22,9 +22,9 @@ Advanced connector policies
 Feedback
 Summarize this article for me
-Advanced connector policies (ACP) represent the next generation of securing connector usage within Power Platform. ACP provides a modern, flexible approach to managing
+Advanced connector policies (ACP) provide the next generation of securing connector usage within Power Platform. ACP offers a modern, flexible approach to managing
 certified connectors
-, replacing the Business/Non-Business/Blocked classification model in classic
+. It replaces the Business, Non-Business, and Blocked classification model in classic
 data policies
 with a strict allowlist that blocks all connectors by default.
 Key principles of advanced connector policies:
@@ -47,6 +47,19 @@ . Custom connectors and HTTP connectors aren't yet supported. They're planned as a separate rule type in the future. For governing custom connectors and HTTP connectors today, continue using classic
 data policies
 .
+Enforcement modes
+When you enable ACP, you choose how it works alongside your existing classic
+data policies
+. Two modes are available:
+Mixed mode (default)
+: ACP runs alongside classic data policies, and the most restrictive settings from both are enforced. This mode is the starting state when you first enable ACP and is recommended while you migrate. For details, see
+Data policy mixed mode
+.
+ACP-only mode
+: ACP becomes the sole policy evaluator. Classic data policies are ignored but not deleted for the affected scope. Choose this mode after you fully migrate connector governance to ACP. For details, see
+ACP-only mode
+.
+Set the mode independently on an environment group or a single environment.
 Supported connector types
 Advanced connector policies are built on the certified connector catalog. ACP doesn't support all connector types from classic data policies.
 Connector type
@@ -8
```

---

## HIGH: Control Review Recommended

### 1. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:164338d50a11d11764ca79ddfee5cd886fd330772f9286aa3387bd2821d78c90

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
-Anthropic as a subprocessor for Microsoft Online Services
-.
-Microsoft 365 Copilot is an AI-powered tool that helps with your work tasks
-.
-Users enter a prompt in Copilot and Copilot responds with AI-generated information. The responses are in real-time and can include internet-based content and work content that users have permission to access.
-Users get content relevant to their work tasks, and in the context of the Microsoft 365 app they're using.
-The following video provides an overview of Microsoft 365 Copilot. It's 1 minute and 49 seconds long.
-Using Microsoft 365 Copilot
-Say, for example, you're an operations
```

---

### 2. Copilot Control System Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:0e68034be47dec5063cbf09c6e3f3a21386c5a4576ceb746ca052ce7fa092dfa

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
@@ -19,16 +19,16 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Copilot Control System overview
+Copilot controls overview
 Feedback
 Summarize this article for me
-The Copilot Control System is a framework of integrated controls and capabilities for Microsoft 365 Copilot and agents. Use it to help secure data that Copilot and agents create or reference, manage Copilot and agent experiences, and measure and analyze adoption and impact across your organization.
-It provides a governance structure for the use of:
-Microsoft 365 Copilot
+Copilot controls provide an integrated framework for Microsoft Copilot and agents. Use them to help secure data that Copilot and agents create or reference, manage Copilot and agent experiences, and measure and analyze adoption and impact across your organization.
+They provide a governance structure for the use of:
+Microsoft Copilot
 Copilot Chat
 Microsoft 365 prebuilt agents
 Agents your organization creates in Microsoft Copilot Studio and publish to Microsoft 365 channels
-The Copilot Control System consists of three main pillars:
+Copilot controls consist of three main pillars:
 Security and governance
 Management controls
 Measurement and reporting
@@ -37,7 +37,7 @@ Key capabilities
 Security and governance
 When you implement Copilot and agents, you might face new and amplified risks related to data security, compliance, and governance. This security and governance framework helps you mitigate these issues.
-The security and governance pillar of the Copilot Control System focuses on the following key capabilities:
+The security and governance pillar of Copilot controls focuses on the following key capabilities:
 Data security
 AI security
 Compliance and privacy
@@ -45,8 +45,8 @@ Security and governance
 .
 Management controls
-Copilot Control System management controls hel
```

---

### 3. Copilot Control System - Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/security-governance
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:0897c5a63697614a27c5721be8bc454e9bd689d46563a7a32ec5c06fa27447b9

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
@@ -19,12 +19,12 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Copilot Control System security and governance
+Copilot controls security and governance
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
@@ -37,14 +37,13 @@ Optimized
 : controls in Microsoft Purview and Microsoft Defender for Cloud Apps with an A5/E5/G5 license.
 Note
-The
-Copilot Control System
-consists of three main pillars:
+Copilot controls
+consist of three main pillars:
 Security and governance
 (this article)
 Management controls
 Measurement and reporting
-The security and governance pillar of the Copilot Control System focuses on the following key capabilities:
+The security and governance pillar of Copilot controls focuses on the following key capabilities:
 Data security
 AI security
 Compliance and privacy
@@ -116,7 +115,7 @@ Adaptive protection for insider risk management
 .
 AI security
-You also need to safeguard AI-powered tools and their associated data against evolving threats. The Copilot Control System provides controls to monitor, detect, and respond to AI-related risks. For example, oversharing of sensitive informa
```

---

### 4. Copilot Control System - Management Controls

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/management-controls
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:100684bad807ffc0a08e0bcc2438c750c764d4d0188441233be3a3789f5b1a10

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
@@ -19,10 +19,10 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Copilot Control System management controls
+Copilot controls for management
 Feedback
 Summarize this article for me
-Copilot Control System management controls help you decide how to deploy and customize your Microsoft 365 Copilot licenses and agents to fit your organization's unique needs. You can find Copilot and agent management controls mainly in the
+Copilot controls help you decide how to deploy and customize your Microsoft Copilot licenses and agents to fit your organization's unique needs. You can find related management settings mainly in the
 Microsoft 365 admin center
 ,
 Power Platform admin center
@@ -30,26 +30,25 @@ Copilot Studio
 .
 Note
-The
-Copilot Control System
-consists of three main pillars:
+Copilot controls
+consist of three main pillars:
 Security and governance
 Management controls
 (this article)
 Measurement and reporting
-The management controls pillar of the Copilot Control System focuses on the following key capabilities:
+The management pillar of Copilot controls focuses on the following key capabilities:
 Licensing and metering
 Agent lifecycle
 Customization
 Licensing and metering
-To manage the costs associated with deploying Copilot, your organization needs control over the deployment and usage of Microsoft 365 Copilot services. This capability includes controls for the use of per-user, per-month licenses and pay-as-you-go services. These pay-as-you-go services include license management, policies, and usage limits. You can also monitor message capacity for both prepaid and pay-as-you-go consumption.
+To manage the costs associated with deploying Copilot, your organization needs control over the deployment and usage of Microsoft Copilot services. This capability includes controls for the use of per-user, per-mo
```

---

### 5. Visual Governance Guide

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-visual-map
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:25e4060d3ce72e758bd93e9e8d1e0dd2a8817793cb1e2d2ae400645a993d1c39

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
@@ -23,15 +23,15 @@ Feedback
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
-Agent policies refer to the tenant settings you can make as an administrator in the Copilot Control System within Microsoft 365 admin center. Choose how you manage access to agents, as well as share and publish agents. For more information, see
+Manage Microsoft Copilot agent access and availability policies
+Agent policies refer to the tenant settings you can make as an administrator in Copilot controls within Microsoft 365 admin center. Choose how you manage access to agents, as well as share and publish agents. For more information, see
 Microsoft 365 agents deployment checklist
 .
 Choose the right Copilot Studio experience
@@ -50,8 +50,8 @@ When you need to provide powerful AI assistants that retrieve real-time insights an
```

---

### 6. Deployment Checklist

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-checklist
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:aea62b34a4459443de7635e177f0f768f1c922bde0da5c0c7d73992b735dfb34

**Affected Controls:**
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
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
@@ -39,8 +39,8 @@ :
 Agents blueprint for Microsoft 365
 Agents visual guide for Microsoft 365
-Manage Microsoft 365 Copilot agent access and availability policies
-Agent policies refer to the tenant settings you can make as an administrator in the Copilot Control System within Microsoft 365 admin center. Agent policies relate to the available settings for all agents in your tenant.
+Manage Microsoft Copilot agent access and availability policies
+Agent policies refer to the tenant settings you can make as an administrator in Copilot controls within Microsoft 365 admin center. Agent policies relate to the available settings for all agents in your tenant.
 Step
 Task
 Description
@@ -145,7 +145,7 @@ Description
 Administrator
 1
-Understand how to extend Microsoft 365 Copilot with agents
+Understand how to extend Microsoft Copilot with agents
 Learn how to create and configure a custom agent using Copilot Studio.
 Copilot administrator, Microsoft 365 administrator
 2
@@ -170,10 +170,10 @@ Copilot administrator, Microsoft 365 administrator
 7
 Publish an agent
-You can publish agents to engage with your customers on multiple platforms or channels, such as live websites, mobile apps, Microsoft 365 Copilot or messaging platforms like Teams and Facebook.
-Copilot administrator, Microsoft 365 administrator
-Manage Microsoft 365 Copilot agent inventory and lifecycle
-You can manage your organization's available agents in the Copilot Control System (CCS) within Microsoft 365 admin center.
+You can publish agents to engage with your customers on multiple platforms or channels, such as live websites, mobile apps, Microsoft Copilot or messaging platforms like Teams and Facebook.
+Copilot administrator, Microsoft 365 administrator
+Manage Microsoft Copilot agent inventory and lifecycle
+You can manage your organization's available agents by using Copilot contro
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Responsible AI
**URL:** https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:537e4e142599ac50496fef6a56c218d6b924d8f94efdbfc3a28f342f1f549f20

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/overview | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/security-governance | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/security-governance |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/management-controls | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/management-controls |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*