# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-18
**Run Time:** 2026-09-18T10:43:44.740539+00:00
**Total URLs Checked:** 231

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 2 |
| Redirects | 5 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | whats-new | HIGH | None | Review and update |
| 2 | microsoft-365-copilot-overview | HIGH | 3.8 | Review and update |
| 3 | information-barriers | CRITICAL | 1.22 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Information Barriers

**URL:** https://learn.microsoft.com/en-us/purview/information-barriers
**Section:** Microsoft Purview
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:ddd93d2047ef7c03fa407812be029bbb8eacdbc482cca910e7bdc5352b3847c6

**Affected Controls:**
- Control 1.22: Control 1.22: Information Barriers for AI Agents
  - File: `controls/pillar-1-security/1.22-information-barriers.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.22/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.22/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/getting-started/phase-2-hardening.md` (HIGH)

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
@@ -50,6 +50,11 @@ two-way communication and collaboration restrictions. For example, a scenario where Marketing can communicate and collaborate with Day Traders, but Day Traders can't communicate and collaborate with Marketing
 isn't supported
 .
+Important
+Information barrier (IB) policies can't restrict communication and collaboration between groups and users in email messages including Exchange Online.
+If your organization needs to define and control email communications, consider using
+Exchange mail flow rules
+.
 Information Barriers and Microsoft Teams
 In Microsoft Teams, IB policies determine and prevent the following kinds of unauthorized communication and collaboration:
 Searching for a user
@@ -89,8 +94,10 @@ Policy behavior
 When IB policy administrators create a new policy or modify an existing policy, users can still access existing plans shared with them or already assigned tasks. For any subsequent plan sharing or task assignment, an IB policy check is triggered and collaboration is permitted or restricted as defined by the policy.
 Information Barriers and Exchange Online
-Information barrier (IB) policies can't restrict communication and collaboration between groups and users in email messages. Only Exchange Online deployments currently support IB policies. If your organization needs to define and control email communications, consider using
+Information barrier (IB) policies can't restrict communication and collaboration between groups and users in email messages. If your organization needs to define and control email communications, consider using
 Exchange mail flow rules
+.
+Enabling Information Barriers in environments without configured ABPs can result in the loss of Address List visibility between all users
 .
 The following table summarizes the key differences between IB modes for Exchange Online Address Book Policies (
```

---

## HIGH: Control Review Recommended

### 1. Copilot Studio guidance hub — What's new

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:648f742aff97e94ae6b3a05e8ebe4284cc34537ef0ba2f18010f1b04df230284

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
@@ -23,10 +23,57 @@ Feedback
 Summarize this article for me
 Get the latest information about what's new and what changed in the Copilot Studio guidance hub.
+September 2026
+New articles
+Govern Copilot Credit consumption for agents powered by the GitHub Copilot
+Updated articles
+Plan Copilot Studio agent deployments for throughput and rate limits
+: Added guidance for running a
+representative pilot
+, measuring peak usage, extrapolating results to full capacity, and providing evidence when requesting a throughput increase.
+Other updates
+New real-world case studies showing how
+Coca-Cola Andina uses Copilot Studio to improve HR support for frontline workers
+and how
+COSMO CONSULT uses Copilot Studio agents to improve sales operations and data quality
+New
+Reference architectures
+in the Power Platform and Copilot Studio Architecture Center:
+Migrate legacy meetings to Microsoft Teams with a conversational agent
+Automate procurement order acknowledgment matching with Copilot Studio and SAP
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
+Copilot Agent Kit helps organizations improve vi
```

---

### 2. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:daed19a604126a72f42be18e1733f688c8474939c3a36e783393e2f4ba7d295b

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