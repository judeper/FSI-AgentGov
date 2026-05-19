# Microsoft Learn Documentation Changes

**Run Date:** 2026-05-19
**Run Time:** 2026-05-19T09:48:08.310492+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 3 |
| HIGH Changes | 1 |
| MEDIUM Changes | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | HIGH | 2.4 | Update portal-walkthrough |
| 2 | microsoft-365-copilot-privacy | MEDIUM | 4.7, 4.6, 2.23 | Update portal-walkthrough |
| 3 | manage-copilot-agents-integrated-apps | HIGH | 3.1, 3.8, 3.6, 3.11, 2.25 | Review and update |
| 4 | audit-solutions-overview | HIGH | 4.5, 1.7, 1.28, 1.27, 2.13 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -64,17 +64,17 @@ . For more information about managed environments, go to
 Managed Environments
 .
-Allow Virtual Network pairing for self-service disaster recovery in Dynamics 365
-If you deploy your Dynamics 365 environment within a Virtual Network and plan to use self-service disaster recovery, you need to configure a
-Virtual Network pair
-. This pairing ensures that your primary and secondary environments can communicate securely during failover and failback operations. Without a Virtual Network pair, disaster recovery operations fail because network connectivity between regions can't be established.
+Allow virtual network pairing for self-service disaster recovery in Dynamics 365
+If you deploy your Dynamics 365 environment within a virtual network and plan to use self-service disaster recovery, you need to configure a
+virtual network pair
+. This pairing ensures that your primary and secondary environments can communicate securely during failover and failback operations. Without a virtual network pair, disaster recovery operations fail because network connectivity between regions can't be established.
 For setup instructions, go to
 Set up virtual network support for Power Platform
 .
 Turn on self-service disaster recovery
 This action sets up resources and starts replicating data between the primary and secondary locations. The process can take up to 48 hours to finish. Admins get a notification when the process finishes.
 Turning on disaster recovery in an environment doesn't affect the environment or its data.
-To turn on disaster recovery, follow these steps.
+To turn on disaster recovery, follow these steps:
 Sign in to the
 Power Platform admin center
 as a system administrator.
@@ -111,7 +111,7 @@ Emergency response for a major regional outage
 Disaster recovery drills
 Your company might have disaster recovery drills documented as a requirement in your internal business continuity plans. Some industries and companies might be required by 
```

---

### 2. Data, Privacy, and Security

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
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -175,6 +175,8 @@ . Our approach in the AI-driven landscape aims to empower organizations to innovate confidently with solutions built with transparency, privacy, and security in mind.
 Additional information
 Microsoft 365 Copilot and privacy controls for connected experiences
+Important
+Your personal data collected from the use of connected experiences in Microsoft 365 isnât used to train large language models (LLMs), including those used by Microsoft 365 Copilot.
 Some privacy controls for connected experiences in Microsoft 365 Apps can affect the availability of Microsoft 365 Copilot features. This includes the privacy controls for connected experiences that analyze your content and the privacy control for optional connected experiences. For more information about these privacy controls, see
 Overview of privacy controls for Microsoft 365 Apps for enterprise
 .

```

---

### 3. Audit Logging

**URL:** https://learn.microsoft.com/en-us/purview/audit-solutions-overview
**Section:** Microsoft Purview
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -46,7 +46,7 @@ 1
 Audit (Premium) includes higher bandwidth access to the Office 365 Management Activity API, which provides faster access to audit data.
 2
-In addition to the required licensing for Audit (Premium) (described in the next section), a user must be assigned a 10-Year Audit Log Retention add-on license to retain their audit records for 10 years.
+In addition to the required licensing for Audit (Premium) (described in the next section), a user must be assigned a 10-Year Audit Log Retention add-on license to retain their audit records for 10 years. Audit records generated by non-user entities (such as service principal actions, system events, and application activities) are retained for a fixed period of one year. This retention period isn't configurable and custom audit log retention policies don't apply to these records.
 Audit (Standard)
 Microsoft Purview Audit (Standard) enables you to log and search for audited activities to support your forensic, IT, compliance, and legal investigations.
 Enabled by default

```

---

## HIGH: Control Review Recommended

### 1. Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**What Changed:**
```diff
--- +++ @@ -43,17 +43,24 @@ Microsoft Agent 365 documentation
 .
 Overview
-Agents enhance the functionality of Copilot by adding search capabilities, custom actions, connectors, and APIs. Agents are custom versions of Microsoft 365 Copilot that combine instructions, knowledge, and skills to perform specific tasks or scenarios. For more information, see
-Get started with agents for Microsoft 365 Copilot
+Agents enhance the functionality of Copilot by adding search capabilities, custom actions, connectors, and APIs. Agents are custom versions of Microsoft 365 Copilot that combine instructions, knowledge, and skills to perform specific tasks or scenarios. For more information about using agents with Copilot, see
+Get started with agents in the Microsoft 365 Copilot app
 .
-However, before users can access these agents, the agents must undergo a streamlined process of submission and approval. To learn more, see
-Publish agents
-.
-The hub Copilot experience shows the list of agents that are available and deployed for the user. Users can toggle it on or off to restrict access of Copilot to any specific agents during the interaction. Users can also add or remove agents in their Copilot experience by right-clicking on the agents and selecting the appropriate option. Users can only access the agents that the admin allows and that they install or are assigned to.
+The members of your organization can find and add agents from the
+Agent Store
+within the Microsoft 365 Copilot app. However, before users can access these agents, each agent must undergo a streamlined process of submission and approval. Agents are managed in the
+Agent Registry
+of Microsoft 365 admin center. As part of agent management, you can review
+agent requests
+and determine whether to publish the agent to the store or reject the agent submission. For more information, see
+Agent management in Microsoft 365 admin center
+. Members of your organization can only access the agents that you have allowed.
 Ag
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Data, Privacy, and Security
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Classification:** MEDIUM (General content update)

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*