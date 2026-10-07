# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-07
**Run Time:** 2026-10-07T12:49:35.827585+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | default-environment-routing | HIGH | 2.15 | Review and update |
| 2 | backup-restore-environments | HIGH | 2.4 | Update portal-walkthrough |
| 3 | analytics-improve-agent-effectiveness | HIGH | None | Update portal-walkthrough |
| 4 | permissions-reference | HIGH | 2.23 | Review and update |
| 5 | agent-id-governance-overview | HIGH | 3.6, 1.11, 2.26 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Backup and Restore

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:968549577a0ca035de3fbab4dde5af80e73ac11f343b4edaceb799eb16743caa

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -460,6 +460,10 @@ Learn more about the recovery environment in
 Recover environment
 .
+What are production environments without Dynamics 365 apps?
+Production environments without Dynamics 365 apps are environments where none of the Dynamics 365 apps are installed. The backup retention period for production environments with Dynamics 365 apps can differ from those without Dynamics 365 apps. Learn more in
+Change the backup retention period for production managed environments
+.
 Troubleshooting
 The environment operation runs for a long time. What action can I take?
 The length of restore and copy operations varies depending on the size of the data involved, so it's common for these operations to take a long time. If the source environment has large amounts of data (such as database, file, log, audit, lake, or search data), the operation can take up to 48 hours to complete. These operations complete on their own without intervention from Microsoft Support. Wait 48 hours after the operation starts before you create a support ticket.

```

---

### 2. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c19586f2213b807a12ba2034ccfc39f7346ed1c5ae9179d9ddf3fc9322091e90

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -223,9 +223,6 @@ for confirmed success or
 conversationOutcome: ResolvedImplied
 for implied success.
-See the guidance documentation on
-measuring engagement
-for suggestions and best practices on how to measure and improve engagement.
 Reactions
 The
 Reactions

```

---

## HIGH: Control Review Recommended

### 1. Environment Routing

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c059cbc0de06951a07fe93c60b8c2a43f8727516e73b66624a5fddd93f0aea64

**Affected Controls:**
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -50,6 +50,9 @@ by this feature. Learn more about the developer environment and developer plan in
 Power Apps Developer Plan Guide: Features and Benefits
 .
+The
+Environment assignment: Developer
+setting is applicable for manual creation of developer environments and environment routing is unaffected by this setting.
 Multi-rule environment routing
 Multi-rule environment routing is an advanced governance feature in Power Platform that tenant administrators use to define multiple routing rules. These rules control how makers are directed to development environments across various portals, such as Power Apps, Power Automate, and Copilot Studio.
 This capability builds on the original environment routing feature, which routed makers to a single environment group. The multirule enhancement introduces flexibility by allowing routing to multiple environment groups based on rule logic. This feature is especially useful for organizations where governance, security, and scalability are critical. It allows:
@@ -121,50 +124,6 @@ Select
 Save
 .
-Turn on environment routing using PowerShell
-Sign in to your tenant account.
-Add-PowerAppsAccount -Endpoint "prod" -TenantID <Tenant_ID>
-Retrieve and store your tenant settings in
-TenantSettings
-.
-$tenantSettings = Get-TenantSettings
-Set the
-enableDefaultEnvironmentRouting
-flag to
-True
-.
-$tenantSettings.powerPlatform.governance.enableDefaultEnvironmentRouting = $True
-Set-TenantSettings -RequestBody $tenantSettings
-Set the
-environmentRoutingAllMakers
-flag to
-True
-to allow routing for all makers or
-False
-to limit routing to new makers.
-$tenantSettings = Get-TenantSettings
-$tenantSettings.powerPlatform.governance | Add-Member -MemberType NoteProperty -Name 'environmentRoutingAllMakers' -Value $True -Force
-(Optional) Set the
-environmentRoutingTargetEnvironmentGroupId
-to the desired Environment Group ID.
-$tenantSettings.powerPlatform.governance | Add-Member -MemberType NoteProperty -Name 'environmentRo
```

---

### 2. Admin Roles

**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Section:** Microsoft Entra ID
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:7dcdb1267dac4a2969b6658d9ab5cc204dba05547719208ea07e7d700f59ca44

**Affected Controls:**
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`

**What Changed:**
```diff
--- +++ @@ -5356,10 +5356,29 @@ microsoft.directory/tenantManagement/tenants/create
 Create new tenants in Microsoft Entra ID
 Tenant Governance Administrator
-Assign the Tenant Governance Administrator role to users who need to do the following tasks:
-Manage all capabilities in the Microsoft Entra Tenant Governance service
-Actions
-Description
+Assign the Tenant Governance Administrator role to users who manage capabilities in the Microsoft Entra Tenant Governance service.
+The table below lists the role's existing actions and additional application-management operations.
+Operations marked
+application-scoped
+are available only through the approved Tenant Governance application. Assigning this role does not grant equivalent unrestricted application-management permissions through other applications. This restriction does not change the scope of the role's other permissions.
+Important
+This is a privileged role. Its application-management capabilities can grant access to tenant resources. Assign it only to trusted administrators.
+Actions and operations
+Description
+Create service principals (application-scoped)
+Create service principals for first-party and third-party applications.
+Update service principal endpoints (application-scoped)
+Update endpoints on service principals.
+Delete service principals (application-scoped)
+Delete service principals.
+Permanently delete service principals (application-scoped)
+Permanently delete service principals, including those for social identity providers.
+Restore service principals (application-scoped)
+Restore deleted service principals, including those for social identity providers.
+Manage delegated permission grants (application-scoped)
+List, create, update, and delete delegated permission grants.
+Manage application role assignments (application-scoped)
+Manage application role assignments, including assignments for Microsoft Graph and Azure AD Graph.
 microsoft.directory/crossTenantAccessPolicy/basic/update
 U
```

---

### 3. Governing Agent Identities

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:db2b14277d17a53e15e4655a0c934f3ea01dd73b1187bb57bbcea3b5d28af6d7

**Affected Controls:**
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`

**What Changed:**
```diff
--- +++ @@ -78,8 +78,8 @@ inherited from their parent agent identity blueprint
 . In addition, agent identities can have resource access assigned to them directly via access packages. Agents can request an access package for own agent IDs, or have their owner or sponsor request one on their behalf. With access packages, you're able to assign agent identities access to the following resources:
 Security Group memberships
-Application OAuth API permissions
-, including Graph application permissions
+OAuth API permissions
+, delegated and application permissions for Microsoft Graph and applications
 Microsoft Entra roles
 To use access packages for agent identities, configure an access package with the required policy settings. When creating an access package assignment policy, in the
 Who can get access

```

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*