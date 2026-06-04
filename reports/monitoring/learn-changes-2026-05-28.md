# Microsoft Learn Documentation Changes

**Run Date:** 2026-05-28
**Run Time:** 2026-05-28T10:05:02.954857+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 7 |
| MEDIUM Changes | 3 |
| Redirects | 1 |
| Errors | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | copilot-hub | HIGH | 3.1, 3.8 | Review and update |
| 2 | planned-features | MEDIUM | 1.4, 3.8, 2.17, 2.25 | Review optional |
| 3 | agent-365-overview | HIGH | 3.8, 2.25 | Review and update |
| 4 | dlp-policy-reference | HIGH | None | Review and update |
| 5 | audit-copilot | HIGH | 1.7, 1.19, 1.21, 1.14, 1.6 | Review and update |
| 6 | ai-microsoft-purview | MEDIUM | 4.8, 4.7, 1.5, 1.16, 1.6, 2.6 | Review and update |
| 7 | import-hr-data | HIGH | 1.12 | Update portal-walkthrough |
| 8 | concept-conditional-access-cloud-apps | HIGH | None | Review and update |
| 9 | permissions-reference | MEDIUM | 2.23 | Review optional |
| 10 | whats-new | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. HR Data Connector

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

### 1. Copilot Hub

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

### 2. Agent 365 Overview Page (M365 Admin)

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

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

### 3. DLP Policy Reference

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

### 4. Audit Copilot Activities

**URL:** https://learn.microsoft.com/en-us/purview/audit-copilot
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/troubleshooting.md` (HIGH)

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

### 5. DSPM for AI

**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
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

### 6. Authentication Contexts

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

### 7. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -89,7 +89,25 @@ : Removed DeepL and Zapier from the
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
 Data Security Posture Management
+New
+: Support for Anthropic Claude (Enterprise), when you add and configure the
+Anthropic Claude data connector
+, which is now in preview. Claude then displays as another AI application alongside Copilot, Copilot Studio, ChatGPT Enterprise, and other AI apps. Use
+activity explorer
+to see individual Claude interactions, such as who used Claude, when they used it, and what kinds of content were involved, just as you do for other AI apps. For more information about Purview support for Claude, see
+Use Microsoft Purview to manage data security & compliance for Anthropic Claude (Enterprise)
+.
 General availability (GA)
 : The new version of
 Data Security Posture Management
@@ -130,6 +148,10 @@ : You can now see the sync status of your sensitivity label publishing policies on the
 Label policies
 page, giving you visibility into when label policy updates are fully synced across Microsoft 365.
+Updated
+: The documentation section
+How to disable sensitivity labels for SharePoint and OneDrive (opt-out)
+now includes labeling behavior if you disable sensitivity labels for SharePoint and Onedrive after they've been enabled.
 April 2026
 Collection Policies
 Preview
@@ -203,6 +225,10 @@ Data loss prevention policy tip reference for Outlook for Android, iOS, and macOS
 . A new reference article covering DLP policy tips, supported conditions, oversharing dialogs, and override capabilities for Outlook on An
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)

---

### 2. DSPM for AI
**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Classification:** MEDIUM (General content update)

---

### 3. Admin Roles
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
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