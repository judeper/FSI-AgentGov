# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-27
**Run Time:** 2026-08-27T17:24:41.616607+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 3 |
| MEDIUM Changes | 3 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...ower-platform/release-plan/2025wave2/ | CRITICAL | 1.27 | Review and update |
| 2 | ...ower-platform/release-plan/2026wave1/ | CRITICAL | 3.8, 2.25, 2.3, 2.10, 2.8, 2.17, 1.4, 1.18 | Review and update |
| 3 | ...ilot-security-enhanced-admin-controls | CRITICAL | 2.3, 2.8, 1.18 | Monitor |
| 4 | knowledge-copilot-studio | HIGH | 4.8, 2.16, 1.14 | Update portal-walkthrough |
| 5 | ...-governance-agentic-center-enablement | CRITICAL | None | Monitor |
| 6 | audit-copilot | HIGH | 1.21, 1.14, 1.7, 1.6, 1.19 | Review and update |
| 7 | site-permissions | MEDIUM | 1.3 | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Knowledge Sources

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:3aa82c564f9da724060e4be13972cf55cb705292c711e56a4711a3b7a7231133

**Affected Controls:**
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)

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
@@ -22,30 +22,14 @@ Knowledge sources summary
 Feedback
 Summarize this article for me
-In Copilot Studio, knowledge sources work together with generative answers. When you add knowledge sources, agents can use enterprise data from Power Platform, Dynamics 365 data, websites, and external systems. Knowledge sources allow your agents to provide relevant information and insights for your customers.
+Knowledge sources ground your agent's responses in enterprise data. When you add knowledge sources, agents can use enterprise data from Power Platform, Dynamics 365 data, websites, and external systems. By using knowledge sources, your agents can provide relevant information and insights for your customers.
+You can incorporate knowledge sources into agents during their initial creation, or add them after the agent is created.
 Published agents that contain knowledge use the configured knowledge sources to ground the published agent. You can incorporate knowledge at the agent level, in the
 Knowledge
 page, or at the topic level, with a
 generative answers node
 in an agent topic.
-You can incorporate knowledge sources into agents during their initial creation, add them after the agent is created, or add them to a generative answers topic node.
-Add and manage knowledge for generative answers
-Generative answers allow your agent to find and present information from multiple sources, internal or external, without having to create specific topics. Use generative answers as primary information sources or as a fallback source when authored topics can't answer a user's query. As a result, you can quickly create and deploy a functional agent. Makers don't need to manually author multiple topics, which might not address all customer questions.
-By default, when you create an agent, Copilot Studio automatically creates the
-Conversational boosting
-system topic. T
```

---

## HIGH: Control Review Recommended

### 1. Release Plans

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:5c0f2608a808feaa2a6550e975bed9c8fc21bb241cab9c6193c6ab2461871991

**Affected Controls:**
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)

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
@@ -22,6 +22,13 @@ Microsoft Power Platform 2025 release wave 2 plan
 Feedback
 Summarize this article for me
+Important
+Release Plans will no longer be published starting in September 2026.
+New Dynamics 365, Power Platform, and Dataverse capabilities will be published to the
+AI at Work roadmap
+beginning in September 2026. Existing release plans will remain available for historical reference until further notice. Learn more about the roadmap and disclosure changes at
+One always-on roadmap: Dynamics 365, Power Platform and Dataverse join the AI at Work roadmap
+.
 The Microsoft Power Platform release plan for the 2025 release wave 2 announces the latest updates to customers as features are prepared for release. You can browse the release plan here
 online
 (updated throughout the month), view it in the
@@ -40,13 +47,8 @@ and a downloadable
 PDF
 .
-The role-based Copilot offerings features coming in the 2025 release wave 2 have been summarized in a separate
-release plan
-as well as a downloadable
-PDF
-.
 2025 release wave 2 overview
-Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. Microsoft Power Platform today is comprised of: Power Apps, Power Pages, Power Automate, Microsoft Copilot Studio, Microsoft Dataverse and Microsoft Power Platform governance and administration. The 2025 release wave 2 contains hundreds of new features across Power Platform applications, including Power Apps, Power Pages, Power Automate, and Microsoft Copilot Studio, as well as Microsoft Dataverse and Power Platform capabilities for governance and administration.
+Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. Microsoft Power Platform today is comprised of: Power Apps, Power Pages, Power Autom
```

---

### 2. Release Plans (2026 Wave 1)

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:65a75bbfcae26236900d3288f3adc2939c110e3d1a6be6bdb1043165cba8be19

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

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
@@ -22,6 +22,13 @@ Microsoft Power Platform 2026 release wave 1 plan
 Feedback
 Summarize this article for me
+Important
+Release Plans will no longer be published starting in September 2026.
+New Dynamics 365, Power Platform, and Dataverse capabilities will be published to the
+AI at Work roadmap
+beginning in September 2026. Existing release plans will remain available for historical reference until further notice. Learn more about the roadmap and disclosure changes at
+One always-on roadmap: Dynamics 365, Power Platform and Dataverse join the AI at Work roadmap
+.
 The Microsoft Power Platform release plan for the 2026 release wave 1 announces the latest updates to customers as features are prepared for release. You can browse the release plan here
 online
 (updated weekly), view it in the
@@ -40,13 +47,8 @@ and a downloadable
 PDF
 .
-The role-based Copilot offerings features coming in the 2026 release wave 1 have been summarized in a separate
-release plan
-as well as a downloadable
-PDF
-.
 2026 release wave 1 overview
-Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. The 2026 release wave 1 contains hundreds of new features across Power Platform applications, including Power Apps, Power Pages, Power Automate, and Microsoft Copilot Studio, as well as Microsoft Dataverse and Power Platform capabilities for governance and administration.
+Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. The 2026 release wave 1 contains hundreds of new features across Power Platform applications, including Power Apps, Power Pages, and Power Automate, as well as Microsoft Dataverse and Power Platform capabilities for governance and administration.
 Power Apps
 Power Apps
 continues to moderniz
```

---

### 3. Audit Copilot Activities

**URL:** https://learn.microsoft.com/en-us/purview/audit-copilot
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:76c147b53ab694d8e195f01cab102fc5e118bff262cf4f05bc821af286353aac

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/deny-event-correlation-report/deployment-guide.md` (HIGH)

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
@@ -49,15 +49,15 @@ The system generates audit logs when an administrator performs activities related to Copilot settings, plugins, promptbooks, or workspaces. For more information, see
 Microsoft 365 Copilot activities
 .
-User activities with Copilot and AI applications
-The system automatically generates audit logs when a user interacts with Copilot or an AI Application. These audit records contain details about which user interacted with Copilot, when the interaction took place, and where it occurred. Audit records also include references to files, sites, or other resources Copilot and AI applications accessed to generate responses to user prompts.
+User activities with Copilot, Cowork, and AI applications
+The system automatically generates audit logs when a user interacts with Copilot, Cowork, or an AI application. These audit records contain details about which user interacted with Copilot, when the interaction took place, and where it occurred. Audit records also include references to files, sites, or other resources Copilot, Cowork, and AI applications accessed to generate responses to user prompts.
 Common properties in Copilot audit logs
 The following table outlines some of the common properties included in audit logs.
 Attribute
 Definition
 Examples
 AccessedResources
-References to all resources (files, documents, emails, etc.) which Copilot accessed in response to the userâs request.
+References to all resources (files, documents, emails, etc.) which Copilot accessed in response to the user's request.
 -
 ID
 is the unique identifier for the resource. This could be a fileId on OneDrive, or a messageId in Teams, or email ID in Outlook, etc.
@@ -210,7 +210,7 @@ https://app.powerbi.com/admin-portal/capacities/00001111-aaaa-2222-bbbb-3333cccc4444
 .
 ClientRegion
-The userâs region when they performed the operation.
+The user's regio
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Enhanced Admin Controls [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:442e6640f227029d3e5f2b414dd858fde43a75b2ff45dc14ca3887312db4f290

---

### 2. Agentic Center of Enablement [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:1637c40c09428b58b032da7206538139fe0150afaa147a27da33a0143405b957

---

### 3. Site Permissions
**URL:** https://learn.microsoft.com/en-us/sharepoint/site-permissions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:622f62291cbac92288ae7caa3d48a9246f10385ecf0127cbc98fae5e9dda6614

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