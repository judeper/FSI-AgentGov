# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-29
**Run Time:** 2026-10-29T12:26:46.248247+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 4 |
| MEDIUM Changes | 2 |
| Redirects | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | admin-share-bots | MEDIUM | 3.10, 3.2, 2.6, 2.5, 2.9 | Update portal-walkthrough |
| 2 | ...n.microsoft.com/en-us/entra/agent-id/ | MEDIUM | 3.11, 3.6, 2.26, 2.6, 2.12, 1.18, 1.11, 1.7 | Update portal-walkthrough |
| 3 | agent-id-governance-overview | HIGH | 3.6, 2.26, 1.11 | Update portal-walkthrough |
| 4 | overview | HIGH | 1.8, 1.27 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Share and Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a67d97505a3bb1fce8c329b8ddd89295727fc1f271a4c6c1e15c6ae3383b7d73

**Affected Controls:**
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -56,9 +56,12 @@ chat
 , you can't share it with Microsoft 365 groups with
 SecurityEnabled
-set to false. To change this setting, see
+set to false. Learn how to change this setting in
 Share an app with Microsoft 365 groups
 in the Power Apps documentation.
+If the agent uses a connector or agent flow that requires users to create their own connection, the users should have the
+End user access
+permissions.
 Important
 Sharing Copilot Studio agents that have connections to external services such as Azure Databricks Genie can be challenging because connections are tied to the identity of each individual agent user. This behavior explains why an agent might work for you but not for other users.
 To address this behavior, use one of the following approaches:

```

---

### 2. Agent ID Overview

**URL:** https://learn.microsoft.com/en-us/entra/agent-id/
**Section:** Microsoft Entra Agent ID
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:bad17b0018df5ae65bb9b4562dd099a6830498483ef771ca4cb2b948cf5158de

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.7/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.11/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.2/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.26/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.26/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.26/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.26/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/3.6/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -18,6 +18,7 @@ ID Governance for agents
 Access packages for agents
 Maintain agent sponsors and lifecycle
+Default agent inactivity policy
 Protect agent access to resources
 Conditional Access for agents
 ID Protection for agents

```

---

### 3. Governing Agent Identities

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:bfd36f4afcb942c4dcb3c1ecd104f99737a55ae04fbc745ce462d3cb30aea1b0

**Affected Controls:**
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.26/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -62,7 +62,7 @@ Agents created in
 Microsoft Copilot Studio
 can be configured to automatically be assigned to an agent identity. When an agent identity is first created in a Power Platform environment after enabling this setting, a Microsoft Copilot Studio agent identity blueprint, and an agent identity blueprint principal, are automatically created. For more information, see
-Automatically create Entra agent identities for Copilot Studio agents (preview)
+Microsoft Entra Agent IDs for Copilot Studio agents
 .
 For agents in the
 Microsoft Teams

```

---

### 4. AI Content Safety

**URL:** https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:20bda1f3a1abbe3770d3a735c46af359b8838cbaa5a4eeccc18c1a80dfe51cf5

**Affected Controls:**
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -22,6 +22,23 @@ What is Azure AI Content Safety?
 Feedback
 Summarize this article for me
+Important
+The following Azure AI Content Safety public preview capabilities retire on
+April 30, 2027
+:
+Analyze Multimodal
+.
+Custom categories (rapid), including text and image
+.
+Connected Content Safety containers
+.
+Disconnected Content Safety containers
+.
+Embedded Content Safety SDK
+.
+Groundedness detection in Azure AI Content Safety and Azure OpenAI
+.
+See the linked feature pages for migration guidance and recommended alternatives.
 Azure AI Content Safety is an AI service that detects harmful user-generated and AI-generated content in applications and services. Azure AI Content Safety includes text and image APIs that allow you to detect material that's harmful. The interactive Content Safety Studio allows you to view, explore, and try out sample code for detecting harmful content across different modalities.
 Content filtering software can help your app comply with regulations or maintain the intended environment for your users.
 Prerequisites

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Share and Manage Agents
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a67d97505a3bb1fce8c329b8ddd89295727fc1f271a4c6c1e15c6ae3383b7d73

---

### 2. Agent ID Overview
**URL:** https://learn.microsoft.com/en-us/entra/agent-id/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:bad17b0018df5ae65bb9b4562dd099a6830498483ef771ca4cb2b948cf5158de

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-365-overview?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*