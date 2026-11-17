# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-17
**Run Time:** 2026-11-17T15:38:16.909281+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 5 |
| HIGH Changes | 10 |
| MEDIUM Changes | 7 |
| Redirects | 6 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ...m/en-us/connectors/custom-connectors/ | HIGH | 2.7 | Review and update |
| 2 | capacity-storage | HIGH | 3.5 | Review and update |
| 3 | security-and-governance | HIGH | 2.8, 1.5, 1.4, 1.8, 1.28, 1.1, 1.3 | Update portal-walkthrough |
| 4 | ...ication-fundamentals-publish-channels | MEDIUM | 2.3, 1.28 | Update portal-walkthrough |
| 5 | add-tools-custom-agent | CRITICAL | 2.17 | Monitor |
| 6 | mcp-create-new-server | HIGH | 1.4 | Review and update |
| 7 | whats-new | HIGH | None | Review and update |
| 8 | concept-conditional-access-cloud-apps | HIGH | None | Review and update |
| 9 | overview-authentication | HIGH | 1.11 | Review and update |
| 10 | pim-configure | HIGH | 2.8, 1.18 | Update portal-walkthrough |
| 11 | ...n.microsoft.com/en-us/entra/agent-id/ | MEDIUM | 3.11, 3.6, 2.12, 2.6, 2.26, 1.7, 1.18, 1.11 | Update portal-walkthrough |
| 12 | what-is-microsoft-entra-agent-id | MEDIUM | 1.18, 1.11 | Review optional |
| 13 | agent-id-governance-overview | HIGH | 3.6, 2.26, 1.11 | Update portal-walkthrough |
| 14 | overview | HIGH | 3.9 | Review and update |
| 15 | connect-data-sources | HIGH | 3.9 | Review and update |
| 16 | create-analytics-rules | HIGH | None | Review and update |
| 17 | monitor-your-data | MEDIUM | 3.9 | Review optional |
| 18 | overview | HIGH | None | Review and update |
| 19 | information-barriers-teams | CRITICAL | None | Monitor |
| 20 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:752e7355a3dd0fd1a0c4e9a73d03ba6ef00f806bd152080bfc74088d8e12c9fc

**Affected Controls:**
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -101,8 +101,8 @@ Microsoft Product Terms
 and the
 Data Protection Addendum
-, govern the Copilot Studio service. For the location of data processing, refer to the
-geographical availability documentation
+, govern the Copilot Studio service. For the location of data processing, refer to
+Dynamics 365, Power Platform, and Copilot Studio product availability
 .
 Compliance with standards and practices
 The

```

---

### 2. Agent Publishing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ee515ba5d444da20495b51f3e8be69438ff6cba719b16caca3b3ba0972fab10a

**Affected Controls:**
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.3/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -29,10 +29,14 @@ Important
 This article includes information about
 Azure Bot Service skills
-, a code-based way to extend the capabilities of an agent in the standard harness. These skills shouldn't be confused with
-agentic skills
-in the GitHub Copilot harness. Learn more about how to use agentic skills in
+, a code-based way to extend the capabilities of an agent in the standard harness. Azure Bot Service skills are different from:
+Agent skills
+, instruction-based skills that you add to agents powered by the GitHub Copilot or Customer Conversation harness. Learn more in
 Skills overview for agents
+.
+Plugin skills
+, a capability that a Microsoft 365 Copilot plugin can include. Learn more in
+Skills as plugin capabilities
 .
 By using Copilot Studio, you can publish agents that engage with your customers on multiple platforms or channels. For example, live websites, mobile apps, Microsoft Copilot, and messaging platforms like Teams and Facebook.
 Each time you update your agent, you can publish it again from within Copilot Studio. Publishing your agent applies to all the channels associated with your agent.

```

---

### 3. Privileged Identity Management

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:6a377f6dad0918fe545cc6529bbb353b00d7de77b7a39c8893529cad9d7df537

**Affected Controls:**
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/3.3/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -24,6 +24,9 @@ Summarize this article for me
 Overview
 Privileged Identity Management (PIM) is a service in Microsoft Entra ID that enables you to manage, control, and monitor access to important resources in your organization. These resources include resources in Microsoft Entra ID, Azure, and other Microsoft Online Services such as Microsoft 365 or Microsoft Intune. The following video explains important PIM concepts and features.
+PIM also supports eligible and active assignments for application-defined roles through
+PIM for app roles (preview)
+. Users can activate eligible app roles when they need them and deactivate them when they finish.
 Reasons to use
 Organizations want to minimize the number of people who have access to secure information or resources, because that reduces the chance of
 a malicious actor getting access
@@ -33,6 +36,8 @@ Using Privileged Identity Management requires licenses. For more information on licensing, see
 Microsoft Entra ID Governance licensing fundamentals
 .
+PIM for app roles (preview) requires Microsoft Entra ID Governance licenses. Microsoft Entra ID P2 alone isn't sufficient.
+License coverage is required for users with eligible or time-bound app role assignments and for request approvers.
 What does it do?
 Privileged Identity Management provides time-based and approval-based role activation to mitigate the risks of excessive, unnecessary, or misused access permissions on resources that you care about. Here are some of the key features of Privileged Identity Management:
 Provide
@@ -64,6 +69,9 @@ and
 Privileged Role Administrator
 role assignments
+The available capabilities depend on the PIM provider. For the app roles preview's workflows, see
+PIM for app roles (preview)
+.
 What can I do with it?
 Once you set up Privileged Identity Management, you'll see
 Tasks
@@ -76,9 +84,15 @@ , managing
 Azure resource
 roles, or PIM for Groups. When you choose what you want to manage, you see the appropriate set of 
```

---

### 4. Agent ID Overview

**URL:** https://learn.microsoft.com/en-us/entra/agent-id/
**Section:** Microsoft Entra Agent ID
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:37c04f685d654548a8dcbb9551e4f7e75c77822c0b13d22caf6338c76d65ac25

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.11/powershell-setup.md` (HIGH)
- ⚠️ `playbooks/control-implementations/3.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.7/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.26/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.26/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.26/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.26/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.2/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -44,8 +44,8 @@ Use an AI coding agent to automate the full Agent ID onboarding workflow.
 OAuth protocols for agents
 Understand how agents authenticate using OAuth 2.0 flows optimized for AI workloads.
-Configure third-party agents
-Integrate agents from platforms like AWS Bedrock and n8n with Agent ID.
+Choose an integration path
+Choose how to integrate an agent with Agent ID based on its platform and hosting model.
 Call Microsoft Graph API
 Access Microsoft 365 data and services from your agents.
 Microsoft Agent 365

```

---

### 5. Governing Agent Identities

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:75ac614bb78d05096c813dd706e2d6ea62ecae394274686fe31b60d75f9bc55e

**Affected Controls:**
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.26/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -19,11 +19,14 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Governing Agent Identities
+Governing Agent identities and access
 Feedback
 Summarize this article for me
-Microsoft Entra allows you to ensure that the right people have the right access to the right apps and services at the right time. With the addition of the Microsoft agent identity platform, managing the access rights of agents in the same way is just as important in the governance lifecycle of your organization's identities. The Microsoft agent identity platform introduces the concept of Agent Identities (IDs). Agent identities are accounts within Microsoft Entra ID that provide unique identification and authentication capabilities for AI agents.
-This allows agent identities to be governed with Microsoft Entra features in the same style as you would govern human identities. With Agent identities, you can govern and manage the identity and access lifecycle of agents, ensuring the agents have a responsible person providing oversight throughout the agent lifecycle and agent's access does not persist longer than it is needed. This article provides an overview of how Microsoft Entra can be utilized to govern agent identities.
+Microsoft Entra allows you to ensure that the right people have the right access to the right apps and services at the right time. Microsoft Entra ID Governance features enable governing the identity and access lifecycle for employees and business guests. With the addition of the Microsoft agent identity platform, managing the access rights of agents in the same way is just as important in the governance lifecycle of your organization's identities. The Microsoft agent identity platform introduces the concept of Agent Identities (IDs). Agent identities are accounts within Microsoft Entra ID that provide unique identification, authentication and authorization capabilities for AI agents.
+This allows agent identities to be governed wit
```

---

## HIGH: Control Review Recommended

### 1. Custom Connectors

**URL:** https://learn.microsoft.com/en-us/connectors/custom-connectors/
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c60e14173f962f86250c7e8298e9526469768bfbe4dfeee0a899977aa1b1a73c

**Affected Controls:**
- Control 2.7: Control 2.7: Vendor and Third-Party Risk Management
  - File: `controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md`

**What Changed:**
```diff
--- +++ @@ -27,15 +27,16 @@ Microsoft Power Automate
 ,
 Microsoft Power Apps
-, and
+,
 Microsoft Copilot Studio
-offer over
+, and Microsoft Copilot (through
+Microsoft Copilot plugins
+) offer over
 1,000 connectors
-to connect to Microsoft and verified services, but you might want to communicate with services that aren't available as prebuilt connectors. Custom connectors address this scenario by allowing you to create (and even share) a connector with its own triggers and actions.
+to connect to Microsoft and verified services. However, you might want to communicate with services that aren't available as prebuilt connectors. Custom connectors address this scenario by allowing you to create (and even share) a connector with its own triggers and actions.
 Lifecycle
 1. Build your API
-A custom connector is a wrapper around a REST API that allows Logic Apps,
-Power Automate, Power Apps, or Copilot Studio to communicate with that REST or SOAP API. These APIs can be:
+A custom connector is a wrapper around a REST API that lets Logic Apps, Power Automate flows, Power Apps, Copilot Studio agents and workflows, or Microsoft Copilot plugins communicate with that REST or SOAP API. These APIs can be:
 Public (visible on the public internet) such as
 Spotify
 ,
@@ -84,7 +85,7 @@ this solution
 . You can extend the flow further to send the HTML table as an email to yourself. or you can extend it to send emails to the connector creators directly and provide them with the names of the connector that needs to be updated.
 3. Describe the API and define the custom connector
-Once you have an API with authenticated access, the next thing to do is to describe your API so that Logic Apps, Power Automate, Power Apps, or Copilot Studio can communicate with your API. The following approaches are supported:
+After you create an API with authenticated access, describe your API so that Logic Apps, Power Automate, Power Apps, Copilot Studio, or Microsoft Copilot can communicate with your
```

---

### 2. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:4c11a7a1b4b0e51a6602a2e6a075373a66806552d05858125589195c3f1a73bb

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

**What Changed:**
```diff
--- +++ @@ -564,16 +564,16 @@ Review growth and begin remediation.
 Stage 1: Restricted
 The tenant first exceeds 100% effective consumption (time zero, or T0).
-Critical notifications appear. Environment create, copy, restore, and recover operations are blocked.
+Critical notifications appear. Environment create, copy, restore, convert, recover and add Dataverse to an environment operations are blocked.
 Free storage, archive eligible data, add capacity, configure pay-as-you-go billing, or request a capacity extension.
 Stage 2: Administration mode
 The overage remains unresolved for 30 days from T0
 In addition to the restrictions applied in Stage 1, access to affected sandbox environments is limited to administrators.
-Administrators can temporarily take affected sandbox environments out of Administration mode to perform remediation activities. However, the storage overage lifecycle and timer continue to progress until the overage is resolved.
+Free storage, archive eligible data, add capacity, configure pay-as-you-go billing, or request a capacity extension. Administrators can temporarily take affected sandbox environments out of Administration mode to perform remediation activities. However, the storage overage lifecycle and timer continue to progress until the overage is resolved.
 Stage 3: Disabled
 The overage remains unresolved for 90 days from T0
 In addition to the restrictions applied in Stage 1, sign-in to affected sandbox environments is blocked for all users, including administrators. The environment and its data are limited to data export and recovery options through support tickets.
-Return the tenant to compliance, and then re-enable the environment. If tenant remains in overage, customer can reach the Microsoft support for the sole purpose of directing data export options, if needed.
+Free storage, archive eligible data, add capacity, configure pay-as-you-go billing, or request a capacity extension. Return the tenant to compliance, and then re-ena
```

---

### 3. Create Custom MCP Server

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:24cfd129044d45d175f2f7fb367013c3202122e919cf8e179750a16a5d64febf

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -26,6 +26,9 @@ This article describes features used in agents or agent flows powered by the
 standard harness
 .
+Before you build a new MCP server, check whether an existing server already provides the tools and resources you need. Learn more in
+Built-in MCP server connectors
+.
 Use
 MCP software development kits (SDKs)
 to set up an MCP server in one of the supported languages.
@@ -33,7 +36,7 @@ Add an existing Model Context Protocol (MCP) server to your agent
 for information on how to add the server to your agent.
 Authentication support
-When you create an MCP server, you can choose to implement authentication or not. If you choose to implement authentication, use one of the following methods:
+When you create an MCP server, you can choose to implement authentication or not. If you choose to implement authentication, use one of the following methods that Copilot Studio supports:
 API key
 : A simple way to secure your server by making your application include a key with requests.
 OAuth 2.0
@@ -47,6 +50,7 @@ Next steps
 Connect your agent to an existing Model Context Protocol (MCP) server
 Add tools and resources from a Model Context Protocol (MCP) server to your agent
+Microsoft MCP server certification (preview)
 Feedback
 Was this page helpful?
 Yes

```

---

### 4. Copilot Studio guidance hub — What's new

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:8e4985d5f317986c54a355afbdf2049099658911d1f6d434983e4182a4905710

**What Changed:**
```diff
--- +++ @@ -25,7 +25,14 @@ Get the latest information about what's new and what changed in the Copilot Studio guidance hub.
 November 2026
 New articles
+Assess model changes with Copilot Agent Kit (preview)
 Design reliable agentic loops
+Updated articles
+Run and validate an AI model migration for Copilot Studio agents
+: Added guidance for using Copilot Agent Kit's model assessment functionality to compare models, identify regressions, and validate migration decisions before production rollout.
+Other updates
+New reference architecture in the Power Platform and Copilot Studio Architecture Center:
+Build a multilingual IT self-service agent with Copilot Studio
 October 2026
 New reference architecture in the
 Power Platform and Copilot Studio Architecture Center
@@ -35,7 +42,7 @@ September 2026
 New articles
 Compare Copilot Studio agent harnesses
-Govern Copilot Credit consumption for agents powered by the GitHub Copilot
+Govern Copilot Credit consumption for agents powered by the Microsoft Copilot harness
 Updated articles
 Plan Copilot Studio agent deployments for throughput and rate limits
 : Added guidance for running a

```

---

### 5. Authentication Contexts

**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-cloud-apps#authentication-context
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:169884c12452eb4b9f549405a4a94339ff056650356153b153c92efb79baa1b8

**What Changed:**
```diff
--- +++ @@ -177,6 +177,28 @@ Microsoft recommends creating a baseline multifactor authentication policy targeting all users and all resources (without any resource exclusions), like the one explained in
 Require multifactor authentication for all users
 .
+Exclude onboarding and recovery from All resources policies (preview)
+Policies targeting
+All resources
+also apply to onboarding and account recovery events unless you enable the global user-action exclusion. These policies can require credentials or other controls that users can't satisfy before they establish or restore their authentication methods.
+Under
+Entra ID
+>
+Conditional Access
+>
+Settings (Preview)
+,
+Global exclusions
+exposes the
+Account onboarding and recovery (Preview)
+setting. When enabled, it excludes the
+Account onboarding and recovery
+user action from policies targeting
+All resources
+. Policies that directly target the user action still apply.
+This is a global user-action exclusion, not a resource exclusion configured in an individual policy. It doesn't exclude users from ordinary application access policies. Review the tenant-wide impact and protect the bootstrap journey with a policy targeting the user action. For steps and validation guidance, see
+Enable the global onboarding and recovery exclusion
+.
 Legacy Conditional Access behavior when an ALL resources policy has a resource exclusion
 Warning
 The following Conditional Access behavior is changing
@@ -388,7 +410,7 @@ All agent resources (Preview)
 Applying a Conditional Access policy to All agent resources enforces the policy for all token requests to agent identity blueprint principals and agent identities.
 User actions
-User actions are tasks that a user performs. Conditional Access supports two user actions:
+User actions are tasks that a user performs. Conditional Access supports the following user actions:
 Register security information
 : This user action lets Conditional Access policies enforce rules when users try
```

---

### 6. Authentication Methods

**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/overview-authentication
**Section:** Microsoft Entra ID
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:00141a3f35264f3730a91a10dca19602a5dcf64379cd74ec365a23d923311cd8

**Affected Controls:**
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**What Changed:**
```diff
--- +++ @@ -130,9 +130,17 @@ Certificate-based authentication (CBA)
 Verified ID identity verification
 Verified ID is an identity verification capability in Microsoft Entra ID â not a traditional authentication method. It can't be used to satisfy authentication requirements like sign-in, MFA, or SSPR. Instead, Verified ID provides cryptographic proof of a user's verified identity for scenarios where trust must be re-established, such as account recovery when all authentication methods are lost.
-Identity verification profiles control which users can participate in Verified ID flows, which provider performs verification, and how identity claims are validated. Admins configure profiles through the Account Recovery setup wizard in the Microsoft Entra admin center, and the Verified ID policy page provides visibility into profile assignments and global exclusions.
-For more information, see
+Identity verification profiles control which users can participate in Verified ID flows, which provider performs verification, and how identity claims are validated. Profiles support recovery, onboarding, and verification for access. Manage shared profiles under
+Verified ID
+>
+ID verification profiles
+in the Microsoft Entra admin center. The Account Recovery setup wizard remains the entry point for recovery-specific configuration, and the Verified ID policy page provides visibility into profile assignments and global exclusions.
+For profile setup and credential support, see
 Verified ID identity verification overview
+. For user-level records, see
+Manage user authentication methods
+and
+Passkeys (FIDO2)
 .
 High-assurance account recovery
 Account recovery is the process of helping users who have lost all their credentials and can no longer access their account. Traditionally, a user calls the help desk, answers questions to verify their identity, and the help desk resets their credentials. Microsoft Entra ID now supports government-issued ID verification with biometric matc
```

---

### 7. Microsoft Sentinel

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/overview
**Section:** Azure Services
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:07043bdd84c9f4e041ebd4a688a7a125332b8337b09de22691c9820e9fff7a04

**Affected Controls:**
- Control 3.9: Control 3.9: Microsoft Sentinel Integration
  - File: `controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md`

**What Changed:**
```diff
--- +++ @@ -42,6 +42,17 @@ Collect data across all users, devices, applications, and infrastructure, both on-premises and in multiple clouds.
 Defender portal
 Azure portal
+To view Microsoft Sentinel data connectors, select
+Setup & configuration
+>
+Data management
+>
+Data & connectors
+, select the
+Connectors
+tab, and select
+Classic connectors - Microsoft Sentinel
+from the connector selector.
 This table highlights the key capabilities in Microsoft Sentinel for data collection.
 Capability
 Description

```

---

### 8. Data Connectors

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/connect-data-sources
**Section:** Azure Services
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:deb260325c510dd66d1e09ead74ee455324e7e16d84550005ffe34cbfc61c395

**Affected Controls:**
- Control 3.9: Control 3.9: Microsoft Sentinel Integration
  - File: `controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md`

**What Changed:**
```diff
--- +++ @@ -64,6 +64,17 @@ page lists the installed or in-use data connectors.
 Defender portal
 Azure portal
+To view installed or in-use Microsoft Sentinel data connectors, select
+Setup & configuration
+>
+Data management
+>
+Data & connectors
+, select the
+Connectors
+tab, and select
+Classic connectors - Microsoft Sentinel
+from the connector selector.
 To add more data connectors, install the solution associated with the data connector from the
 Content Hub
 . For more information, see the following articles:

```

---

### 9. Custom Analytics Rules

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/create-analytics-rules
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:43eca3f2a2acdd76fce679be6a66290df02769a0c3e455b4ff7d942eb9195d11

**What Changed:**
```diff
--- +++ @@ -88,9 +88,9 @@ For Microsoft Sentinel in the
 Defender portal
 , select
-Microsoft Sentinel
+Investigation & response
 >
-Configuration
+Detection
 >
 Analytics
 . For Microsoft Sentinel in the

```

---

### 10. Azure Key Vault

**URL:** https://learn.microsoft.com/en-us/azure/key-vault/general/overview
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:8f5ba3c1d971b2a5090198af860cde78160a1889630cee15803c67bd1957e285

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.5/verification-testing.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -51,7 +51,7 @@ Access to a key vault requires proper authentication and authorization before a caller (user or application) can get access. Authentication establishes the identity of the caller, while authorization determines the operations that they're allowed to perform.
 Authentication is done via Microsoft Entra ID. Authorization may be done via Azure role-based access control (Azure RBAC) or Key Vault access policy. Azure RBAC can be used for both management of the vaults and to access data stored in a vault, while key vault access policy can only be used when attempting to access data stored in a vault.
 Azure Key Vault provides multiple layers of security to protect your data. All key vaults are encrypted at rest using keys stored in hardware security modules (HSMs), and Azure safeguards your keys, secrets, and certificates using industry-standard algorithms, key lengths, and cryptographic protection.
-For organizations requiring the highest level of security, the Premium tier offers HSM-protected keysâRSA-HSM, EC-HSM, and OCT-HSM (symmetric/AES, preview)âthat never leave the HSM boundary. These Premium tier HSMs utilize Marvell LiquidSecurity hardware with FIPS 140-3 Level 3 validation, ensuring the most stringent cryptographic protection available.
+For organizations requiring the highest level of security, the Premium tier offers HSM-protected keysâRSA-HSM, EC-HSM, and OCT-HSM (symmetric/AES)âthat never leave the HSM boundary. These Premium tier HSMs utilize Marvell LiquidSecurity hardware with FIPS 140-3 Level 3 validation, ensuring the most stringent cryptographic protection available.
 Both Standard and Premium tiers use
 Federal Information Processing Standard 140 validated software cryptographic modules and HSMs
 to meet rigorous security and compliance standards.

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Agent Publishing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ee515ba5d444da20495b51f3e8be69438ff6cba719b16caca3b3ba0972fab10a

---

### 2. Add Tools to Agents
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:6315e8843340587073b3e8bf8129be640cc00f2cd32e1a6bd371efe7471c8c9e

---

### 3. Agent ID Overview
**URL:** https://learn.microsoft.com/en-us/entra/agent-id/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:37c04f685d654548a8dcbb9551e4f7e75c77822c0b13d22caf6338c76d65ac25

---

### 4. Agent Identities for AI Agents
**URL:** https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:cb6e3500945f9e9dbd32befa1b4a5fac1e8c926299146d9a235b45cf840189b0

---

### 5. Workbooks
**URL:** https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e71af3d94e569881ea9178183015ea9cc37f042c5b7933c4aedbbf0ba05e5ca9

---

### 6. Information Barriers in Teams
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-teams
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:30f73a0b152d7927f1f66dd0b20b803d8ee29e12d4e817b0e5f03cb58a92d960

---

### 7. Copilot Studio Licensing (Get Access)
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:977a724ad6ceb7cbf4431d3b1a9fbd18641b17e1c7fc9c3e7cd5cd770622a7b3

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*