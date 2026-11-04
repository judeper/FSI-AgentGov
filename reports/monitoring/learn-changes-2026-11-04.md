# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-04
**Run Time:** 2026-11-04T13:54:36.058662+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 3 |
| HIGH Changes | 3 |
| MEDIUM Changes | 7 |
| Redirects | 9 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | copilot-overview | MEDIUM | 3.8 | Review and update |
| 2 | microsoft-365-copilot-privacy | MEDIUM | 4.7, 4.6, 2.23 | Update portal-walkthrough |
| 3 | enable-users | MEDIUM | None | Review optional |
| 4 | copilot-controls-overview | MEDIUM | 3.8 | Review optional |
| 5 | copilot-controls-security-governance | MEDIUM | None | Review optional |
| 6 | copilot-controls-management | MEDIUM | 3.8 | Review optional |
| 7 | ...osoft365-copilot-location-learn-about | HIGH | 1.6, 1.5, 1.14, 1.13 | Update portal-walkthrough |
| 8 | sensitivity-labels | MEDIUM | 1.3, 1.5, 1.26 | Update portal-walkthrough |
| 9 | ai-agent-inventory | HIGH | 1.21 | Review and update |
| 10 | incident-response-planning | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Data, Privacy, and Security

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Section:** Microsoft 365 Copilot
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:888e6f068d72cd14386f1df0ea9cfb4391589342b413a7906ca0e7932faba6d0

**Affected Controls:**
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -243,14 +243,4 @@ Microsoft Copilot requirements
 Get started with Microsoft Copilot
 Microsoft Copilot adoption site
-Feedback
-Was this page helpful?
-Yes
-No
-No
-Need help with this topic?
-Want to try using Ask Learn to clarify or guide you through this topic?
-Ask Learn
-Ask Learn
-Suggest a fix?
 Additional resources
```

---

### 2. DLP for M365 Copilot

**URL:** https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:24fe3a82cc9d96184bd19adc12f29d212572ef8219d446cb362fb256626076c9

**Affected Controls:**
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.7/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.14/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.5/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.13/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.13/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -150,7 +150,7 @@ Internal
 Public
 Personal
-They deploy Microsoft 365 Copilot and Copilot Chat to help users find and use Contoso enterprise information in their organization. They want to minimize the risk of General Data Protection Regulation (GDPR) data being included in Microsoft 365 Copilot and Copilot Chat summaries and also exclude private information from summaries. They create a DLP policy that uses the
+They deploy Microsoft 365 Copilot and Copilot Chat to help users find and use Contoso enterprise information in their organization. They want to exclude personal data and highly confidential information from Microsoft 365 Copilot and Copilot Chat summaries. They create a DLP policy that uses the
 Microsoft 365 Copilot and Copilot Chat
 policy location with the
 Content contains

```

---

### 3. Sensitivity Labels

**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c0c87508de563356205ac4b22de5a6c0466d336842ad7b28afc9a6058e417894

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.14/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.26/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.8/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -257,9 +257,15 @@ All users in the same organization can see the name of a sensitivity label applied to content, even if that label isn't published to them. They don't see sensitivity labels from other organizations.
 When you configure a publishing label policy, you can:
 Choose which users and groups see the labels.
-Labels can be published to any specific user or email-enabled security group, distribution group, or Microsoft 365 group (which can have
+Labels can be published to include or exclude specific users and supported groups. Supported groups include security groups (email-enabled or non-email-enabled), distribution groups, and Microsoft 365 groups. Microsoft 365 groups can also have
 dynamic membership
-) in Microsoft Entra ID.
+.
+Important
+The effect of user and group scoping depends on whether the sensitivity label applies protection:
+Label without protection:
+The publishing policy scope determines which users can see and apply the label.
+Label with protection:
+The publishing policy still determines who can see and apply the label. Access to protected content is also subject to Azure Rights Management. Azure Rights Management doesn't support non-email-enabled security groups or exclusions for protection. Make sure the users and groups that need access are supported and authorized by the protection configuration.
 Specify a default label
 for unlabeled documents and Loop components and pages, emails and meeting invites, new containers (when you've
 enabled sensitivity labels for containers
@@ -269,10 +275,6 @@ Consider using a default label to set a base level of protection settings that you want applied to all your content. However, without user training and other controls, this setting can also result in inaccurate labeling. It's usually not a good idea to select a label that applies encryption as a default label to documents. For example, many organizations need to send and share documents with external users who might not have apps t
```

---

## HIGH: Control Review Recommended

### 1. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:01d82364d023bc43353ac818bbd778ca765f6de271c35c79277853cdcf31b7dd

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -492,14 +492,4 @@ For other Microsoft Copilot products, see the
 Microsoft Copilot learning hub
 .
-Feedback
-Was this page helpful?
-Yes
-No
-No
-Need help with this topic?
-Want to try using Ask Learn to clarify or guide you through this topic?
-Ask Learn
-Ask Learn
-Suggest a fix?
 Additional resources
```

---

### 2. Microsoft Defender - AI Agent Inventory

**URL:** https://learn.microsoft.com/en-us/defender-xdr/security-for-ai/ai-agent-inventory
**Section:** Microsoft Defender
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:5addd9032e8500b931dad7d99b2ad18ae7c1a58fd73a864357751cfd10217d50

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`

**What Changed:**
```diff
--- +++ @@ -33,12 +33,12 @@ AI Agents
 page in the Microsoft Defender portal to review agent configuration, risk levels, risk indicators, recommendations, alerts, tools, identities, and related security context. You can also query agent inventory and configuration data by using Advanced Hunting.
 Prerequisites
-Enable security for AI agents, including the Microsoft 365 connector. See
+For cloud agents, enable security for AI agents, including the Microsoft 365 connector. See
 Enable security for AI agents using Microsoft Defender
 .
-To discover local AI agents that run on endpoints, set up
-AI agent runtime protection in Microsoft Defender for Endpoint
-. Discovery requires Microsoft Defender for Endpoint and Microsoft Defender Antivirus in active mode. Local agents are onboarded separately.
+To discover local AI agents that run on endpoints, meet the
+local AI agent discovery prerequisites
+. Local agents are onboarded separately, and discovery doesn't require you to enable AI agent runtime protection.
 Review AI agent risk and security posture
 Microsoft Defender calculates an agent's risk level from its active risk indicators. Security recommendations identify available actions for improving the agent's posture but are calculated separately from the risk level.
 The available risk indicators, recommendations, tabs, and supporting evidence depend on the agent type and the security information available for that agent.
@@ -172,6 +172,21 @@ For information about Advanced Hunting, see
 Proactively hunt for threats with Advanced Hunting in Microsoft Defender
 .
+Feature availability for GCC customers
+Microsoft Defender security for AI capabilities differ between GCC and the commercial offering. The following table lists availability for AI agent discovery and security posture capabilities in GCC.
+Capability
+GCC
+Agent discovery and inventory
+Supported
+Agent risk assessment
+Not supported
+Security recommendations
+Not supported
+Attack surface graph
+Not support
```

---

### 3. Incident Response Planning

**URL:** https://learn.microsoft.com/en-us/security/operations/incident-response-planning
**Section:** Security Operations
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:f2afa7699767586f059de14461aedb61b882d66e40a16a6962b78bcccae33f06

**What Changed:**
```diff
--- +++ @@ -19,10 +19,12 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Incident response planning
+Prepare for incident response
 Feedback
 Summarize this article for me
-Use this table as a checklist to prepare your Security Operations Center (SOC) to respond to cybersecurity incidents.
+This article is part of the Security Operations (SecOps) discipline in the
+Microsoft Security Adoption Framework (SAF)
+. Use this table as a readiness checklist to prepare your Security Operations Center (SOC) to respond to cybersecurity incidents.
 Done
 Activity
 Description
@@ -126,10 +128,10 @@ What do we plan to do next (and when is it realistic to expect results)?
 Incident responders come with different techniques and approaches, including dead box analysis, big data analysis, and the ability to produce incremental results. Starting with clear expectations will facilitate clear communications.
 Incident response resources
-Overview
-for Microsoft security products and resources for new-to-role and experienced analysts
-Playbooks
-for detailed guidance on responding to common attack methods
+Plan incident response
+for strategy, process, and recovery guidance
+Incident response playbooks overview
+for scenario-specific execution guidance
 Microsoft Defender XDR
 incident response
 Microsoft Defender for Cloud (Azure)

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. M365 Copilot Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:01d82364d023bc43353ac818bbd778ca765f6de271c35c79277853cdcf31b7dd

---

### 2. Data, Privacy, and Security
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:888e6f068d72cd14386f1df0ea9cfb4391589342b413a7906ca0e7932faba6d0

---

### 3. Manage Copilot
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/enable-users
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0cdcb2c126a4b1c4aafd3fd5880fd2a575c22bd13a6e8d3a37371964fffa6129

---

### 4. Copilot Control System Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8572495849c7436583f7b3c694724331bed64031d8d34fef1d1b9e92469e0b5b

---

### 5. Copilot Control System - Security and Governance
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-security-governance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6af8048277abf28cd10b43214d4bff7864fc6335006b30f5640b884d0472a3a2

---

### 6. Copilot Control System - Management Controls
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:785652eeb8753770c362cb9695b04d3f6688e89f1bdbc9d7a9dc314a770fb94a

---

### 7. Sensitivity Labels
**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c0c87508de563356205ac4b22de5a6c0466d336842ad7b28afc9a6058e417894

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview | https://learn.microsoft.com/en-us/copilot/plan/copilot-overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy | https://learn.microsoft.com/en-us/copilot/plan/microsoft-365-copilot-privacy |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/enable-users | https://learn.microsoft.com/en-us/copilot/adopt/enable-users |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-overview | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-security-governance | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-security-governance |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/copilot-controls-management | https://learn.microsoft.com/en-us/copilot/implement/copilot-controls-management |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/security/operations/incident-response-planning | https://learn.microsoft.com/en-us/security/zero-trust/security-operations-incident-response-readiness |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*