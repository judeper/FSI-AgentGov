# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-20
**Run Time:** 2026-06-20T09:17:38.669143+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 5 |
| MEDIUM Changes | 2 |
| Redirects | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | HIGH | 2.4 | Update portal-walkthrough |
| 2 | dlp-policy-reference | HIGH | None | Review and update |
| 3 | permissions-reference | HIGH | 2.23 | Review and update |
| 4 | ...n.microsoft.com/en-us/entra/agent-id/ | HIGH | 3.11, 3.6, 2.26, 2.6, 1.11, 1.18 | Review and update |
| 5 | what-is-microsoft-entra-agent-id | MEDIUM | 1.11, 1.18 | Review optional |
| 6 | agent-id-governance-overview | MEDIUM | 3.6, 2.26, 1.11 | Review optional |
| 7 | restricted-content-discovery | HIGH | 4.7, 4.1, 4.6, 1.3, 1.14 | Review and update |
| 8 | whats-new | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -128,7 +128,9 @@ Cancel
 if your only purpose is to check the potential loss of data if there's a failover operation. Remember, the last sync time always changes because data is replicated continuously.
 Recovery point and recovery time objectives with business continuity and disaster recovery
-Power Platform and Dataverse are designed with high availability built into every region. Within a region, the platform targets approximately near zero RPO (recovery point objective) and a recovery time of under five minutes across availability zones and data centers within a region. For cross-region resiliency, Microsoft provides self-service disaster recovery, which gives customers full visibility and control over the failover process. In this model, typical replication lag is under 15 minutes (often under five minutes), and the platform is designed to complete failover within minutes once initiated.
+Power Platform and Dataverse are designed with high availability built into every region. Within a region, the platform targets approximately near zero RPO (recovery point objective) and a recovery time of under five minutes across availability zones and data centers within a region. For cross-region resiliency, Microsoft provides self-service disaster recovery, which gives customers full visibility and control over the failover process. In this model, typical replication lag is under 15 minutes (often under five minutes), and the platform is designed to complete failover within minutes once initiated. Dynamics 365 uses the same Azure SQL Database business continuity capabilities described in the
+Business continuity in Azure SQL Database
+public documentation.
 Because customers retain control of when and whether to trigger a cross-region failover, Microsoft doesn't publish a cross-region RTO commitment. Customers can monitor real-time replication lag directly in the Power Platform admin center to inform their own recovery decisions. It's important to note that whe
```

---

## HIGH: Control Review Recommended

### 1. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -1707,10 +1707,10 @@ Document name contains words or phrases
 Document size equals or is greater than
 Document created by
-Document creation date is on or after (preview)
-Document creation date is on or before (preview)
-Document modification date is on or after (preview)
-Document modification date is on or before (preview)
+Document creation date is on or after
+Document creation date is on or before
+Document modification date is on or after
+Document modification date is on or before
 Conditions OneDrive accounts support
 Content contains
 Content is shared from Microsoft 365
@@ -1723,10 +1723,10 @@ Document size equals or is greater than
 Document created by
 Document is shared
-Document creation date is on or after (preview)
-Document creation date is on or before (preview)
-Document modification date is on or after (preview)
-Document modification date is on or before (preview)
+Document creation date is on or after
+Document creation date is on or before
+Document modification date is on or after
+Document modification date is on or before
 Conditions Teams chat and channel messages support
 Content contains
 Insider risk level for Adaptive Protection is

```

---

### 2. Admin Roles

**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Section:** Microsoft Entra ID
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**What Changed:**
```diff
--- +++ @@ -323,6 +323,15 @@ Privileged Role Administrator
 Can manage role assignments in Microsoft Entra ID, and all aspects of Privileged Identity Management.
 e8611ab8-c189-46e8-94e1-60213ab1f814
+Purview Workload Content Administrator
+Manage or purge data from Microsoft 365 when accessing from the Microsoft Purview portal.
+3f04f91a-4ad7-4bd3-bcfa-49882ea1a88a
+Purview Workload Content Reader
+Read data from Microsoft 365 when accessing from the Microsoft Purview portal.
+e07494ad-1654-4dd2-922e-6f81a71bf00f
+Purview Workload Content Writer
+Read and edit data from Microsoft 365 when accessing from the Microsoft Purview portal.
+02d5655b-c1cf-4e5f-98da-5fb919085bf6
 Reports Reader
 Can read sign-in and audit reports.
 4a5d8f65-41da-4de4-8968-e035b65339cf
@@ -4324,6 +4333,30 @@ Update permissions of service principals
 microsoft.office365.webPortal/allEntities/standard/read
 Read basic properties on all resources in the Microsoft 365 admin center
+Purview Workload Content Administrator
+Assign the Purview Workload Content Administrator role to users who need to do the following tasks:
+Manage or purge Microsoft 365 data (such as SharePoint, Teams, OneDrive, or Exchange) when accessing from the Microsoft Purview portal
+Important
+Assign this role through the Microsoft Purview portal. If you try to assign this role using the Microsoft Entra admin center, it might be overwritten.
+Microsoft Purview uses role groups to limit tasks that users can perform in the Microsoft Purview portal. To learn more about how the Purview Workload Content Administrator role maps to the roles on the Microsoft Purview portal, see
+Purview Role Assignment Migrator
+.
+Purview Workload Content Reader
+Assign the Purview Workload Content Reader role to users who need to do the following tasks:
+Read data from Microsoft 365 (such as SharePoint, Teams, OneDrive, or Exchange) when processing long-running operations submitted from the Microsoft Purview portal.
+Important
+Assign this role t
```

---

### 3. Agent ID Overview

**URL:** https://learn.microsoft.com/en-us/entra/agent-id/
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.11/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -1,46 +1,57 @@-Microsoft Entra Agent ID
-Protect agent identities and secure their access to applications and resources. Part of Microsoft Agent 365, Microsoft Entra Agent ID and the Microsoft agent identity platform provide the foundation for secure and compliant AI agent deployments in the enterprise.
-Learn about Microsoft Entra Agent ID
-Get started with Microsoft Entra Agent ID
-Learn about how Microsoft Entra Agent ID and Agent 365 work together so you can observe, govern, and secure agents across your organization.
-Manage agents
-Learn how to manage all aspects of agents in your ecosystem, such as assigning sponsors and requesting access packages.
+Microsoft Entra Agent ID documentation
+Secure access for AI agents with enterprise-grade access management, protection, and governance. Integrate AI agents with enterprise workflows, apply Zero Trust principles, and govern agent access at scale using the identity and network access capabilities of Microsoft Entra.
+Overview
+What is Microsoft Entra Agent ID?
+Architecture
+Plan your agent identity architecture
+Concept
+Security for AI overview
+What's new
+What's new in Agent ID
+Manage, govern, and protect
+Microsoft Entra Agent ID helps you manage, govern, and protect AI agent identities across your organization.
 Manage agent identities
+Create an agent blueprint
+Create agent identities
+Manage owners and sponsors
 Govern agent lifecycles
-Ensure the lifecycle of your agents is governed with access reviews, entitlement management, and sponsor accountability.
-Get started
+ID Governance for agents
+Access packages for agents
+Maintain agent sponsors and lifecycle
 Protect agent access to resources
-Apply the same Zero Trust principles and access controls to your agents as you do for your users and workloads.
-Security for AI overview
-Build on the Microsoft agent identity platform
-Build agents with enterprise-ready identities using the Microsoft agent identity platform.
+Conditional Access for age
```

---

### 4. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -122,6 +122,8 @@ Restricted Content Discovery is designed to limit the ability of end users to search for content from specific SharePoint sites. For a more comprehensive guidance on preparing your data for Copilot, check out this
 blueprint
 .
+How does Restricted Content Discovery affect the end user experience in SharePoint?
+Restricted Content Discovery will restrict usage of AI-powered features in SharePoint. Users will not see entry points such as the Copilot button, AI actions menus (including creating agents), or Create pages with AI.
 Feedback
 Was this page helpful?
 Yes

```

---

### 5. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -92,6 +92,23 @@ and
 .page
 files are converted to HTML, making the content indexed and keyword searchable in the review set and easier to process in post-export workflows.
+Information Protection client
+In preview
+:
+View and label files
+with the Information Protection client using macOS.
+Sensitive information types
+New
+: Added definitions for the following sensitive information types:
+China physical addresses
+Colombia national ID
+Colombia tax identification number
+Greenland physical addresses
+Russia physical addresses
+Russia taxpayer identification number
+Singapore physical addresses
+South Africa physical addresses
+Ukraine physical addresses
 May 2026
 Agent 365
 General availability (GA)

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Agent Identities for AI Agents
**URL:** https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id
**Classification:** MEDIUM (General content update)

---

### 2. Governing Agent Identities
**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Classification:** MEDIUM (General content update)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/architecture/ | https://learn.microsoft.com/en-us/agents/architecture/ |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*