# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-23
**Run Time:** 2026-06-23T09:41:43.778971+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 12 |
| HIGH Changes | 14 |
| MEDIUM Changes | 11 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | managed-environment-overview | HIGH | 3.7, 2.15, 2.1, 2.2, 2.7, 1.8 | Update portal-walkthrough |
| 2 | managed-environment-enable | HIGH | 2.1, 1.4 | Review and update |
| 3 | managed-environment-sharing-limits | MEDIUM | 2.1, 2.2, 1.1 | Update portal-walkthrough |
| 4 | managed-environment-solution-checker | MEDIUM | 2.1, 2.2 | Review optional |
| 5 | managed-environment-usage-insights | HIGH | 3.2, 2.1 | Review and update |
| 6 | environment-groups | HIGH | 2.15, 2.2, 1.4, 1.28 | Update portal-walkthrough |
| 7 | default-environment-routing | HIGH | 2.15 | Review and update |
| 8 | advanced-connector-policies | MEDIUM | 1.4 | Update portal-walkthrough |
| 9 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 10 | security-overview | MEDIUM | 3.7, 1.8, 1.26 | Review and update |
| 11 | ip-firewall | HIGH | 1.20 | Update portal-walkthrough |
| 12 | customer-managed-key | HIGH | 1.15 | Update portal-walkthrough |
| 13 | monitoring-overview | MEDIUM | None | Review optional |
| 14 | alerts | HIGH | None | Review and update |
| 15 | copilot-hub | MEDIUM | 3.1, 3.8 | Review and update |
| 16 | welcome-content | MEDIUM | None | Review optional |
| 17 | identity-access-management | CRITICAL | None | Monitor |
| 18 | business-continuity-disaster-recovery | HIGH | 2.4 | Update portal-walkthrough |
| 19 | backup-restore-environments | HIGH | 2.4 | Update portal-walkthrough |
| 20 | capacity-storage | MEDIUM | 3.5 | Review optional |
| 21 | environment-strategy | HIGH | 2.4 | Review and update |
| 22 | power-bi-monitor | MEDIUM | 2.6 | Review optional |
| 23 | pipelines | HIGH | 2.5, 2.3, 1.28 | Update portal-walkthrough |
| 24 | ...-pipeline-rule-for-environment-groups | MEDIUM | None | Review optional |
| 25 | admin-deployment-hub | HIGH | 2.1, 2.3 | Update portal-walkthrough |
| 26 | whats-new | HIGH | None | Review and update |
| 27 | communication-compliance-policies | HIGH | 1.10 | Update portal-walkthrough |
| 28 | ...tion-compliance-investigate-remediate | HIGH | 1.10 | Update portal-walkthrough |
| 29 | ...tion-labels-data-lifecycle-management | HIGH | 4.3, 1.9 | Review and update |
| 30 | endpoint-dlp-learn-about | HIGH | 1.17 | Review and update |
| 31 | create-analytics-rules | HIGH | None | Review and update |
| 32 | apply-irm-to-a-list-or-library | HIGH | 1.16 | Review and update |
| 33 | whats-new | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Managed Environments

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:ebcf18478f5c869a6c75d308bc32010400e314e0351854ee88097b743a060fa7

**Affected Controls:**
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 2.2: Control 2.2: Environment Groups and Tier Classification
  - File: `controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md`
- Control 2.7: Control 2.7: Vendor and Third-Party Risk Management
  - File: `controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.1/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.15/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -19,13 +19,13 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Managed Environments overview
+Managed environments overview
 Feedback
 Summarize this article for me
-Managed Environments is a suite of premium capabilities that allows admins to manage Power Platform at scale with more control, less effort, and more insights. Admins can use Managed Environments with any type of environment. Certain features can be configured upon enabling a Managed Environment. Once an environment is managed, it unlocks more features across the Power Platform.
-Learn how to use Managed Environments
+Managed environments are a suite of premium capabilities that allow admins to manage Power Platform at scale with more control, less effort, and more insights. Admins can use managed environments with any type of environment. Certain features can be configured upon enabling a managed environment. Once an environment is managed, it unlocks more features across the Power Platform.
+Learn how to use managed environments
 .
-A Managed Environment encompasses, but isn't limited to, the following features:
+A managed environment encompasses, but isn't limited to, the following features:
 Environment groups
 Limit sharing
 Weekly usage insights
@@ -48,16 +48,16 @@ Control which apps are allowed in your environment
 Create and manage masking rules
 Note
-Managed Environments is included as an entitlement with standalone Power Apps, Power Automate, Microsoft Copilot Studio, Power Pages, and Dynamics 365 licenses. Trial licenses can be used to license users in Managed Environments, with the restrictions specific to these types of licenses. To learn more about Managed Environment licensing, see
+Managed environments are included as an entitlement with standalone Power Apps, Power Automate, Microsoft Copilot Studio, Power Pages, and Dynamics 365 licenses. Trial licenses can be used to license users in managed environments, with the restrictions specific t
```

---

### 2. Managed Environment Sharing Limits

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-sharing-limits
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:5b36505acbf7a353b885bf4e3bf3c5af8f99a6be2899ca5fce73b5d1f163d0b1

**Affected Controls:**
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 2.2: Control 2.2: Environment Groups and Tier Classification
  - File: `controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.1/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -22,7 +22,7 @@ Limit sharing
 Feedback
 Summarize this article for me
-In Managed Environments, admins can limit how broadly users can share canvas apps, flows, and agents.
+In managed environments, admins can limit how broadly users can share canvas apps, flows, and agents.
 To configure these rules:
 Sign in to the
 Power Platform admin center
@@ -110,42 +110,42 @@ # Retrieve the environment
 $environment = Get-AdminPowerAppEnvironment -EnvironmentName <EnvironmentId>
 
-# Update the Managed Environment settings
+# Update the managed environment settings
 $governanceConfiguration = $environment.Internal.properties.governanceConfiguration
 $governanceConfiguration.settings.extendedSettings | Add-Member -MemberType NoteProperty -Name 'limitSharingMode' -Value "excludeSharingToSecurityGroups" -Force
 $governanceConfiguration.settings.extendedSettings | Add-Member -MemberType NoteProperty -Name 'maxLimitUserSharing' -Value "20" -Force
 
-# Save the updated Managed Environment settings
+# Save the updated managed environment settings
 Set-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName <EnvironmentId> -UpdatedGovernanceConfiguration $governanceConfiguration
 Here's a PowerShell script that turns off sharing for solution-aware cloud flows.
 # Retrieve the environment
 $environment = Get-AdminPowerAppEnvironment -EnvironmentName <EnvironmentId>
 
-# Update the Managed Environment settings
+# Update the managed environment settings
 $governanceConfiguration = $environment.Internal.properties.governanceConfiguration
 $governanceConfiguration.settings.extendedSettings | Add-Member -MemberType NoteProperty -Name 'solutionCloudFlows-limitSharingMode' -Value "disableSharing" -Force
 
-# Save the updated Managed Environment settings
+# Save the updated managed environment settings
 Set-AdminPowerAppEnvironmentGovernanceConfiguration -EnvironmentName <EnvironmentId> -UpdatedGovernanceConfiguration $governanceConfiguration
 Here's a PowerShell script t
```

---

### 3. Environment Groups

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/environment-groups
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:fa9f865382a90db82dc3661a34308c1997795ec16123f6e6d0d05cf41382d394

**Affected Controls:**
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`
- Control 2.2: Control 2.2: Environment Groups and Tier Classification
  - File: `controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.2/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.2/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -25,7 +25,7 @@ Managing the Power Platform on a large scale across numerous environments, ranging from hundreds to tens of thousands, poses a significant challenge for both startup and enterprise IT teams. To address these complexities, environment groups offer a premium governance solution designed to streamline management tasks by organizing environments into logical collections and enforcing uniform policies and configurations.
 Think of an environment group as a "folder" for your environments. Administrators can cluster a flat list of environments into structured groups based on criteria such as business unit, project, geographic region, or purpose. By creating these logical collections, IT teams gain the ability to manage multiple environments simultaneously and efficiently implement security, governance, and compliance policies on a large scale through centrally managed rules. This centralized approach eliminates the need to configure each environment one-by-one, ensures consistency, significantly reduces administrative overhead, and prevents issues such as configuration drift and chaotic management practices common in extensive deployments.
 Note
-Environment groups can only contain Managed Environments.
+Environment groups can only contain managed environments.
 Each environment can belong to only one group, and groups can't overlap or be nested.
 Environments in a group can span different regions and types as long as each is managed.
 Environments can be transferred between groups by removing them from one and adding them to another.
@@ -101,7 +101,7 @@ Power Platform for Admins V2 (Preview) connector
 offers an alternative solution. It allows the creation and deletion of environment groups and the ability to add or remove environments from these environment groups, facilitating opportunities for automation.
 Configure the rules for your environment group
-After you create the environment group, Power Platform tenant administrators can immediatel
```

---

### 4. Advanced Connector Policies

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:15a99109dfeaf7fd4ad3e2cb78e29262df280c843c054c8a5797b13a25c04bb8

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.4/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -244,8 +244,8 @@ : ACP doesn't support virtual connectors and won't support them in the future. For migration paths, see
 Virtual connector transition
 .
-Managed Environments and nonblockable connectors
-: In single environment mode, ACP works on both Managed Environments and non-Managed Environments so that all customers using classic data policies can migrate to ACP without extra cost. However, on non-Managed Environments, the nonblockable connectors remain nonblockable. On Managed Environments (single or environment group), you can block any connector or any action, including those that are nonblockable in classic data policies.
+Managed environments and nonblockable connectors
+: In single environment mode, ACP works on both managed environments and non-managed environments so that all customers using classic data policies can migrate to ACP without extra cost. However, on non-managed environments, the nonblockable connectors remain nonblockable. On managed environments (single or environment group), you can block any connector or any action, including those that are nonblockable in classic data policies.
 Feedback
 Was this page helpful?
 Yes

```

---

### 5. IP Firewall

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/ip-firewall
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:770ea36504e1c0cbed987c0c7cfdf190479af66c7aa64433786aad1997954d96

**Affected Controls:**
- Control 1.20: Control 1.20: Network Isolation and Private Connectivity
  - File: `controls/pillar-1-security/1.20-network-isolation-private-connectivity.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.1/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.1/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -36,7 +36,7 @@ .
 Prerequisites
 The IP firewall is a feature of
-Managed Environments
+managed environments
 .
 You must have a Power Platform admin role to enable or disable the IP firewall.
 Enable the IP firewall
@@ -258,8 +258,8 @@ Navigate to the Power Platform Admin Center (PPAC) and configure the IP Firewall settings.
 Ensure that the option "Allow access for all application users" is unchecked to enforce filtering.
 Licensing requirements for IP firewall
-The IP firewall is only enforced on environments that are activated for Managed Environments. Managed Environments are included as an entitlement in standalone Power Apps, Power Automate, Microsoft Copilot Studio, Power Pages, and Dynamics 365 licenses that give premium usage rights. Learn more about
-Managed Environment licensing
+The IP firewall is only enforced on environments that are activated for managed environments. Managed environments are included as an entitlement in standalone Power Apps, Power Automate, Microsoft Copilot Studio, Power Pages, and Dynamics 365 licenses that give premium usage rights. Learn more about
+managed environment licensing
 with the
 Licensing overview for Microsoft Power Platform
 .
@@ -278,14 +278,14 @@ Does this feature work in real time?
 IP firewall protection works in real time. Since the feature works at the network layer, it evaluates the request after the authentication request is completed.
 Is this feature enabled by default in all environments?
-The IP firewall isn't enabled by default. The Power Platform administrator needs to enable it for Managed Environments.
+The IP firewall isn't enabled by default. The Power Platform administrator needs to enable it for managed environments.
 What is audit-only mode?
 In audit-only mode, the IP firewall identifies the IP addresses that are making calls to the environment and allows them all, whether they're in an allowed range or not. It's helpful when you're configuring restrictions on a Power Platform envi
```

---

### 6. Encryption

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:554d0992f17a2ddebce97cd4a3d28bf18f012330bd0e19c5cedc58d51f7dd621

**Affected Controls:**
- Control 1.15: Control 1.15: Encryption: Data in Transit and at Rest
  - File: `controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.1/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.1/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -90,8 +90,8 @@ Warning
 When environments are locked, they can't be accessed by anyone, including Microsoft support. Environments that are locked become disabled and data loss can occur.
 Licensing requirements for customer-managed key
-Customer-managed key policy is only enforced on environments that are activated for Managed Environments. Managed Environments are included as an entitlement in standalone Power Apps, Power Automate, Microsoft Copilot Studio, Power Pages, and Dynamics 365 licenses that give premium usage rights. Learn more about
-Managed Environment licensing
+Customer-managed key policy is only enforced on environments that are activated for managed environments. Managed environments are included as an entitlement in standalone Power Apps, Power Automate, Microsoft Copilot Studio, Power Pages, and Dynamics 365 licenses that give premium usage rights. Learn more about
+managed environment licensing
 , with the
 Licensing overview for Microsoft Power Platform
 .
@@ -341,9 +341,9 @@ Grant enterprise policy permissions to access key vault
 Grant Power Platform and Dynamics 365 administrators permission to read the enterprise policy. More information:
 Grant the Power Platform admin privilege to read enterprise policy
-Power Platform admin center admin selects the environment to encrypt and enable Managed environment. More information:
-Enable Managed environment to be added to the enterprise policy
-Power Platform admin center admin adds the Managed environment to the enterprise policy. More information:
+Power Platform admin center admin selects the environment to encrypt and enable managed environment. More information:
+Enable managed environment to be added to the enterprise policy
+Power Platform admin center admin adds the managed environment to the enterprise policy. More information:
 Add an environment to the enterprise policy to encrypt data
 Enable the Power Platform enterprise policies service for your Azure subscription
 Register
```

---

### 7. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:e47d80384a1688dc4187ac84013bd83b3a969bd782e5e9915ecb41b3608cf64a

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -22,6 +22,8 @@ Business continuity and disaster recovery
 Feedback
 Summarize this article for me
+Note
+As of June 22, 2026, Self-Service Disaster Recovery (SSDR) is also available for Finance & Operations (F&O) applications. SSDR enables organizations to maintain an asynchronous secondary copy of their production environment in a paired Azure region and perform self-service failover, failback, and disaster recovery testing.
 Businesses expect their applications and customer data to be protected and resilient during unavoidable outages and disruptions. It's important to document a business continuity plan that minimizes the effects of outages. To recover and resume operations, make sure the plan lists stakeholders, processes, and specific steps.
 Microsoft provides business continuity and disaster recovery capabilities to all
 production type environments
@@ -146,7 +148,7 @@ , these cross-region copies became redundant. Recovering from these copies was a complex and manual process that affected recovery times.
 What are the costs associated with using self-service disaster recovery?
 The selected environment must be a
-Managed Environment
+managed environment
 . This environment is a premium license tier.
 Prepaid storage consumed for the secondary region is the cost incurred.
 For example, suppose you have 10 GB of capacity consumption in the primary location. When you turn on self-service disaster recovery, you create a copy of the data in the remote secondary region and this copy consumes another 10 GB. You can pay for this 10 GB in the secondary region through storage entitlements. If you exceed your available free storage or available entitlements, a pay-as-you-go plan actively starts billing.
@@ -236,7 +238,6 @@ Data lake failover has known issues. Self-service disaster recovery isn't supported yet.
 Connectors might have recovery problems when dependent on external systems, like SharePoint, SQL server, or third-party applications.
 For Dynamics 36
```

---

### 8. Backup and Restore

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:f2f2bd39b25996bdc1698dc59a7f635e28cfbee25909af45b3d58f73d72ce300

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -24,9 +24,9 @@ Summarize this article for me
 It's important to protect your data on Microsoft Power Platform and in Dataverse and to provide continuous availability of service through system or manual backups.
 System backups are automatically created for environments that have a database. By default, backups of all production and nonproduction environments are retained for seven days. However, for production
-Managed Environments
+managed environments
 , the retention period can be extended up to 28 days through the Power Platform admin center or PowerShell.
-Manual backups are backups that the user initiates. It's recommended that you create manual backups before performing major customizations, applying a version update, or making significant changes to the environment. You can create these backups for production and sandbox environments, but not for the default environment. By default, manual backups are kept for seven days. For production Managed Environments, the retention period can be extended up to 28 days.
+Manual backups are backups that the user initiates. It's recommended that you create manual backups before performing major customizations, applying a version update, or making significant changes to the environment. You can create these backups for production and sandbox environments, but not for the default environment. By default, manual backups are kept for seven days. For production managed environments, the retention period can be extended up to 28 days.
 Supported retention period
 Environment types
 System backup
@@ -53,9 +53,9 @@ Not backed up
 Not supported
 * For production
-Managed Environments
+managed environments
 , you can extend the retention period beyond seven days, to a maximum of 28 days, through the Power Platform admin center or PowerShell. Learn more in
-Change the backup retention period for production Managed Environments
+Change the backup retention period for production managed environments
 .
 ** We don't support
```

---

### 9. Pipelines Overview

**URL:** https://learn.microsoft.com/en-us/power-platform/alm/pipelines
**Section:** Power Platform ALM
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:23425e1124835c5a8cb72c924ccb70aa2c52e83c36050aa30e4d05bfad63b557

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -86,10 +86,10 @@ Deploy
 from within their development environment), and the same solution artifact will be deployed. Similarly, the system doesn't re-export a solution for deployments to subsequent stages in a pipeline. The same solution artifact must pass through pipeline stages in sequential order. The system also prevents any tampering or modification to the exported solution artifact. This ensures customization can't bypass QA environments or your approval processes.
 Are standalone licenses required to use pipelines?
-Developer environments aren't required to be Managed Environments. They can be used for development and testing with the developer plan.
-The pipelines host should be a production environment, but the pipelines host doesn't have to be a Managed Environment.
-All other environments used in pipelines must be enabled as Managed Environments.
-Licenses granting premium use rights are required for all Managed Environments.
+Developer environments aren't required to be managed environments. They can be used for development and testing with the developer plan.
+The pipelines host should be a production environment, but the pipelines host doesn't have to be a managed environment.
+All other environments used in pipelines must be enabled as managed environments.
+Licenses granting premium use rights are required for all managed environments.
 A common setup example:
 Environment purpose
 Environment type
@@ -106,19 +106,19 @@ Production
 Production
 Yes
-Can I ensure pipeline targets are Managed Environments?
-Yes. Tenant admins can automatically convert pipeline target environments to Managed Environments, ensuring compliance with Microsoft standards.
-To enable an environment as a Managed Environment, go to the Power Platform admin center
+Can I ensure pipeline targets are managed environments?
+Yes. Tenant admins can automatically convert pipeline target environments to managed environments, ensuring compliance with Microsoft standards.
+To 
```

---

### 10. Admin Deployment Hub

**URL:** https://learn.microsoft.com/en-us/power-platform/alm/admin-deployment-hub
**Section:** Power Platform ALM
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:55ef6b2bf531a588ca9865ecbbecb461fb273913bc8d4534ecb7f446a8f7387c

**Affected Controls:**
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.3/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -78,18 +78,18 @@ deployed to the target environment.
 Important
 All target environments used in a pipeline must be enabled as
-Managed Environments
+managed environments
 .
 Tenant admins can enable automatic conversion of pipelines environments to
-Managed Environments
+managed environments
 .
 Manage deployment settings
 Admins can manage these
 Settings
 within the selected pipelines host (settings are managed separately for each host):
 Enable automatic conversion of pipelines environments to
-Managed Environments
-. This ensures pipelines environments meet Microsoft compliance standards automatically. When makers deploy to this environment, it gets automatically converted to a Managed Environment.
+managed environments
+. This ensures pipelines environments meet Microsoft compliance standards automatically. When makers deploy to this environment, it gets automatically converted to a managed environment.
 Solution deployments across regions
 : Admins can opt in to allow deployments between environments in different geographic locations. For example, when the host and production environments are in North America but the development environment is in India.
 Important
@@ -118,22 +118,22 @@ Deploy
 . A confirmation message appears when you confirm the retry.
 FAQ
-Are Managed Environments required for deployment pipelines, and what does this mean for my organization?
-Yes. All target environments used in Power Platform deployment pipelines have always been required to be Managed Environments for compliant usage. This requirement helps your organization benefit from enhanced governance, improved security, and streamlined license management.
-How can I ensure pipelines targets are Managed Environments automatically?
-Tenant admins (Power Platform and Dynamics 365 admins) can enable a setting that automatically converts pipelines target environments to Managed Environments, ensuring compliance with Microsoft standards. Managed Environments are then enabled
```

---

### 11. Create Policies

**URL:** https://learn.microsoft.com/en-us/purview/communication-compliance-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:5751710a6855e1be9c9ac718196bbaa0253af15a940b1402d1def9bd5a0bebaa

**Affected Controls:**
- Control 1.10: Control 1.10: Communication Compliance Monitoring
  - File: `controls/pillar-1-security/1.10-communication-compliance-monitoring.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.10/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -25,7 +25,7 @@ Important
 Microsoft Purview Communication Compliance
 provides the tools to help organizations detect regulatory compliance (for example, SEC or FINRA) and business conduct violations such as sensitive or confidential information, harassing or threatening language, and sharing of adult content. Communication Compliance is built with privacy by design. Usernames are pseudonymized by default, role-based access controls are built in, investigators are opted in by an admin, and audit logs are in place to help ensure user-level privacy.
-Policies
+Create and manage policies
 Create Communication Compliance policies for Microsoft 365 organizations in the Microsoft Purview portal. Communication Compliance policies define which communications and users are subject to review in your organization, set custom conditions the communications must meet, and specify who should do reviews.
 Users assigned the
 Communication Compliance Admins
@@ -36,7 +36,7 @@ You can't rename policies, but you can delete them when no longer needed.
 Important
 PowerShell isn't supported for creating and managing Communication Compliance policies. To create and manage these policies, use the policy management controls in the Communication Compliance solution.
-Policy templates
+Choose a policy template
 Policy templates are predefined policy settings that you can use to quickly create policies to address common compliance scenarios. Each of these templates has differences in conditions and scope. All templates use the same types of detection signals. You can choose from the following policy templates:
 Area
 Policy Template
@@ -88,12 +88,12 @@ User-reported messages
 policy is implemented for your organization when you purchase a license that includes Microsoft Purview Communication Compliance. However, this feature can take up to 30 days to become available after license purchase.
 As part of a layered defense to detect and remediate inappropriate messages in your organiza
```

---

### 12. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/communication-compliance-investigate-remediate
**Section:** Microsoft Purview
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:b3424223f07c1d2aec218ceb8850913fea028196d374321487ce40fcac8174d6

**Affected Controls:**
- Control 1.10: Control 1.10: Communication Compliance Monitoring
  - File: `controls/pillar-1-security/1.10-communication-compliance-monitoring.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -49,8 +49,8 @@ May 19
 to change the time period if you don't want to use the default setting of
 1 year
-.
-Learn more about the Policy Match Preservation setting
+. For details, see
+Policy Match Preservation setting
 .
 To investigate issues detected by your policies, review policy matches and alerts. The Communication Compliance area provides several features to help you quickly investigate policy matches and alerts:
 Policies page
@@ -104,8 +104,8 @@ Pending
 tab, summarize a lengthy message by using Microsoft Copilot in Microsoft Purview, or review the history of closed policy matches on the
 Resolved
-tab.
-Learn more about remediation actions
+tab. For details, see
+Review and remediate policy matches and alerts
 .
 Alerts page
 Go to
@@ -120,7 +120,7 @@ Reports
 to display Communication Compliance report widgets. Each widget provides an overview of Communication Compliance activities and statuses, including access to deeper insights about policy matches and remediation actions.
 Tip
-Learn how to analyze interactions entered into generative AI applications
+Analyze interactions entered into generative AI applications
 .
 Tips for quickly reviewing policy matches on the Pending or Resolved tab
 When you select a message to review on the
@@ -155,7 +155,9 @@ You can also specify a preservation period when you create or edit a policy. The preservation period you select within a policy takes precedence over the global
 Policy Match Preservation
 setting.
-When the setting goes into effect on April 1, 2025:
+When the global
+Policy Match Preservation
+setting goes into effect on April 1, 2025:
 The value in the
 Policy Match Preservation
 setting applies to all existing policy matches. The system automatically deletes policy matches that are older than the selected time period. For example, if the
@@ -178,6 +180,7 @@ Change the time period for the global
 Policy Match Preservation
 setting
+To change the global policy match preservation period, complet
```

---

## HIGH: Control Review Recommended

### 1. Enable Managed Environments

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-enable
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:84283f9ed0eaa8d2e1b49471c7b9cf0cc2fc5de5b7c42971e0402763af084692

**Affected Controls:**
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -19,20 +19,20 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Enable Managed Environments
+Enable managed environments
 Feedback
 Summarize this article for me
-Admins enable, disable, and edit Managed Environments in the Power Platform admin center. Admins can also use PowerShell to disable Managed Environments. This article explains the permissions you need to manage environments and the steps to get started in the Microsoft Power Platform admin center or with PowerShell.
+Admins enable, disable, and edit managed environments in the Power Platform admin center. Admins can also use PowerShell to disable managed environments. This article explains the permissions you need to manage environments and the steps to get started in the Microsoft Power Platform admin center or with PowerShell.
 Permissions
-To enable or edit Managed Environments, you need the Power Platform Administrator or Dynamics 365 Administrator role in Microsoft Entra ID. You can learn more about these roles in
+To enable or edit managed environments, you need the Power Platform Administrator or Dynamics 365 Administrator role in Microsoft Entra ID. You can learn more about these roles in
 Use service admin roles to manage your tenant
 .
-Any user with permission to view environment details can see the Managed Environments property for an environment.
-Users with the Delegated Admin role or the Environment Admin security role can't change the Managed Environments property in an environment.
+Any user with permission to view environment details can see the managed environments property for an environment.
+Users with the Delegated Admin role or the Environment Admin security role can't change the managed environments property in an environment.
 Important
-The Managed Environments property must be the same in the source and destination before you can start to copy and restore environment lifecycle operations.
-Dataverse is required to use Managed Environ
```

---

### 2. Usage Insights

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-usage-insights
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:13800331e8232d4d723bcb4b50adf3af05c651b750f2a66fa1df59869bc09ac4

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`

**What Changed:**
```diff
--- +++ @@ -60,7 +60,7 @@ Include insights for this environment in the weekly email digest
 in the
 Usage insights
-section of the Managed Environment settings. If you exclude all your managed environments, Power Platform won't send a weekly digest.
+section of the managed environment settings. If you exclude all your managed environments, Power Platform won't send a weekly digest.
 Note
 Clear the check box to exclude a managed environment. If you exclude all your managed environments, Power Platform won't send a weekly digest.
 Who can receive the weekly digest?
@@ -86,7 +86,7 @@ Additional recipients
 box in the
 Usage insights
-section of the Managed Environments settings.
+section of the managed environments settings.
 $tenantSettings = Get-TenantSettings 
 ($tenantSettings.powerPlatform.governance) | Add-Member -MemberType NoteProperty -Name additionalAdminDigestEmailRecipients -Value 'fakeEmail@contoso.com;otherFakeEmail@contoso.com' 
 Set-TenantSettings -RequestBody $tenantSettings
@@ -101,8 +101,8 @@ $False
 .
 See also
-Managed Environments overview
-Enable Managed Environments
+Managed environments overview
+Enable managed environments
 Limit sharing
 Data policies
 Licensing

```

---

### 3. Environment Routing

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:334578ff92b8e163bec832ae880428885b1a24bf12f90c9d437acc4d16dbab09

**Affected Controls:**
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -37,11 +37,11 @@ , the maker lands in their own personal developer environment instead of the default environment. Personal developer environments are the makers' own spaces, like OneDrive, for personal productivity where they can start building apps and solutions in their own workspace. Makers don't need to know which environment to work in, since the personal developer environment appears automatically.
 When the feature is turned on, the selected maker type (that is, new or existing makers), are directed into their own, personal developer environment. If the maker has access to one or more existing developer environments that aren't owned by them, they're routed to a new developer environment.
 Dataverse is available in developer environments, and these environments are
-Managed Environments
+managed environments
 with the admin settings preconfigured according to the assigned environment group rules. Admins no longer need to worry that their makers are working in the default environment, where their work can conflict with others.
 Important
 By default, all developer environments created through environment routing are managed.
-Managed Environments isn't included as an entitlement in the Developer Plan when users run their assets. For more information about Managed Environments and the Developer Plan, see
+Managed environments aren't included as an entitlement in the Developer Plan when users run their assets. For more information about managed environments and the Developer Plan, see
 Power Apps Developer Plan Guide: Features and Benefits
 .
 Non-managed
@@ -56,11 +56,11 @@ Fine-grained control over where makers build.
 Consistent policy enforcement across environments.
 Reduced risk of conflicts in shared or default environments.
-All routed environments are Managed Environments, meaning they inherit standardized policies like data retention, AI features, and application lifecycle management (ALM) settings defined by the admin through environment g
```

---

### 4. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:ff56884a550cca3c04e0b53f88c459e300e3140c5ec4d42d3e2160f3e3b294dd

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -716,8 +716,6 @@ By: Agendium Ltd
 CyberProof
 By: CyberProof Inc.
-D&B Optimizer [DEPRECATED]
-By: Dun & Bradstreet
 d.velop
 By: d.velop AG
 D365 Contact Center Admin MCP
@@ -886,6 +884,8 @@ By: Draup
 Dropbox
 By: Microsoft
+Dun and Bradstreet MCP Server
+By: Dun & Bradstreet, Inc.
 Duration Calculator (Independent Publisher)
 By: Troy Taylor
 DVLA Vehicle Enquiry Service (Independent Publisher)
@@ -1012,6 +1012,8 @@ By: Encodian
 Encodian - Word
 By: Encodian
+Encodian [DEPRECATED]
+By: Encodian
 Engagement Cloud
 By: dotdigital
 Enlyft Insights
@@ -1156,6 +1158,8 @@ By: Formstack LLC
 Formstack Forms
 By: Formstack LLC
+Foxit eSign
+By: Foxit Software Inc.
 FraudLabs Pro (Independent Publisher)
 By: Troy Taylor
 FreeAgent (Independent Publisher)
@@ -1412,8 +1416,6 @@ By: iLovePDF
 iLoveSign
 By: iLoveSign
-iLoveSign [DEPRECATED]
-By: i Love PDF
 iManage AI
 By: iManage Power Platform Connector
 iManage Data Marts
@@ -1512,6 +1514,8 @@ By: ITautomate LTD
 ITGlue (Independent Publisher)
 By: Nirmal Kumar
+Jamie AI
+By: Jamie AI
 Jasper (Independent Publisher)
 By: Troy Taylor
 JBHunt
@@ -2138,6 +2142,8 @@ By: Peakboard GmbH
 Peltarion AI
 By: Peltarion
+Penneo Sign Sandbox
+By: Penneo Integration
 Perfect Wiki
 By: OOO RD17
 Perplexity AI (Independent Publisher)
@@ -2536,6 +2542,8 @@ By: Showcase Software Ltd
 Showpad eOS
 By: Showpad
+Showpad MCP
+By: Showpad
 SHRTCODE (Independent Publisher)
 By: Chandra Sekhar Malla
 Sigma Conso CR
@@ -2590,6 +2598,8 @@ By: Tensis Group
 Smartsheet
 By: Microsoft
+Smartsheet EU
+By: Smartsheet Inc
 Smartsheet US
 By: Smartsheet Inc
 SmileBack
@@ -2740,6 +2750,8 @@ By: TeleSign Corporation
 Templafy
 By: Templafy
+TemplioniX
+By: TemplioniX
 Tendocs Documents
 By: Deepdale BV
 Teradata
@@ -3112,6 +3124,8 @@ By: Troy Taylor
 ZeroTrain AI Core
 By: Leonard Gambrell - DBA Gambrell Software
+Zint
+By: Zint
 Zippopotamus (Independent Publisher)
 By: Tomasz Poszytek

```

---

### 5. Security

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:680806eee53b6cb9eb1bdf5c41ffa42e2133a2f433866b5deb509c3795a08087

**Affected Controls:**
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.26/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -81,7 +81,7 @@ Overview
 page.
 Only tenant administrators can convert an environment to a managed type.
-On every security page, features that apply to Managed Environments are marked with the following meter symbol:
+On every security page, features that apply to managed environments are marked with the following meter symbol:
 Security score (preview)
 [This section is prerelease documentation and is subject to change.]
 Important
@@ -117,7 +117,7 @@ Ã·
 Total possible score
 ) Ã 100
-For example, your tenant has 10 environments, five Managed Environments and five non-Managed Environments. The following features are configured:
+For example, your tenant has 10 environments, five managed environments and five non-managed environments. The following features are configured:
 IP firewall
 : Turned on in two of the 10 environments (2 points).
 Tenant isolation
@@ -127,8 +127,8 @@ In this case, your total score is 2 + 10 + 5 = 17, and the total possible score is 30. Therefore, your security score is (17 Ã· 30) Ã 100 = 56.66%.
 Important
 The security score is updated every 24 hours. Therefore, any action that is taken might take up to 24 hours to reflect the updated score.
-The score calculation considers all environments, both Managed Environments and non-Managed Environments.
-If there are no Managed Environments that you can take action on in the recommendation pane, no environments are listed.
+The score calculation considers all environments, both managed environments and non-managed environments.
+If there are no managed environments that you can take action on in the recommendation pane, no environments are listed.
 Turn on environment management to unlock full security benefits
 Note
 This feature is in the process of rolling out and might not be available in your region yet.
@@ -158,7 +158,7 @@ The system generates various recommendations, based on common best practices that improve the security score of your tenant. Recommendations refer to acti
```

---

### 6. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:31fb8108b1bade30f61552014a850dff8676e026c360c72d4ce81da4f1a95f59

**What Changed:**
```diff
--- +++ @@ -34,14 +34,14 @@ Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. You can place alert rules on an environment and a specific resource.
 A
 triggered alert
-occurs when one or more of the resources that an alert rule monitors pass specific thresholds that the admin defines when configuring the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for how to improve the resources if it's in a Managed Environment.
+occurs when one or more of the resources that an alert rule monitors pass specific thresholds that the admin defines when configuring the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for how to improve the resources if it's in a managed environment.
 When to use alerts
 Teams and admins use alerts to find resources that are used more than expected. For example, an admin creates an alert to know if apps in the default environment exceed 50 launches a day.
 Teams use alerts to find resources with degraded health, and work with their makers to fix issues.
 For operations, admins create alerts to know if apps in their production environment are slow to open for users.
 Prerequisites
 You must be a tenant administrator or an environment administrator to access alerts.
-You can only place alerts on a Managed Environment.
+You can only place alerts on a managed environment.
 You must be using the
 new and improved Power Platform admin center
 .
@@ -160,7 +160,7 @@ Find your resource, and select it to open a resource pane, which has more detailed metric information.
 In the upper-right corner of the pane, you see a link labeled
 + New alert rule
-if the resource is in a Managed Environment.
+if the resource is in a managed environment.
 Select the
 + New alert rule
 link to create an alert. The admin center autofills the information for
@@
```

---

### 7. Copilot Hub

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2c8d3677a6236d395618e51f1741ee97dd993b3db2fb2276e7898e06a640e2cd

**Affected Controls:**
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -56,7 +56,7 @@ Tenant users with environment access can view Copilot settings.
 Control who can use AI features in model-driven apps
 Admins can define who within an environment can use Copilot capabilities in model-driven appsâeither by explicitly allowing specific users or allowing all users except a defined exclusion list. This capability is currently in preview and is only for environments activated for
-Managed Environments
+managed environments
 , with a subset of Copilot features adhering to it. Review the following table to learn which capabilities adhere to this configuration.
 Product
 Feature

```

---

### 8. Environment Strategy

**URL:** https://learn.microsoft.com/en-us/power-platform/guidance/adoption/environment-strategy
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:d607c43a590f18f83d1b1b6b45a27966149ad1e3ab1c6f326e064e73c8e2a362

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**What Changed:**
```diff
--- +++ @@ -34,7 +34,7 @@ . These resources often use only the basic capabilities included with Microsoft 365 and don't use the full capabilities of Power Platform. As this initial adoption accelerates, Microsoft provides organizations with an on-ramp to an environment strategy for enterprise scale adoption of the full Power Platform capabilities. These premium governance capabilities become available when users have a premium Power Platform (Power Apps, Power Automate, Microsoft Copilot Studio, and Dynamics 365) license. The
 Power Platform adoption maturity model
 provides more insights to help organizations define their roadmap to achieve enterprise scale adoption beyond their environment strategy. This approach can help organizations mature from basic personal productivity to enterprise-scale adoption of Power Platform.
-Power Platform administrative, governance, and security features allow organizations to adopt and manage Power Platform for enterprise productivity and enterprise app usage at scale. Using Managed Environments activates a set of premium capabilities that enable greater visibility and control and reduce the manual effort to administer and secure environments. Using these capabilities, you can ensure consistent application of your governance and security policies. Admins can transition into an enterprise-scale, environment strategy using these capabilities. Spending less time and effort on the administration helps reduce the overall total cost of ownership (TCO) of the platform as your organization scales usage.
+Power Platform administrative, governance, and security features allow organizations to adopt and manage Power Platform for enterprise productivity and enterprise app usage at scale. Using managed environments activates a set of premium capabilities that enable greater visibility and control and reduce the manual effort to administer and secure environments. Using these capabilities, you can ensure consistent application of your governanc
```

---

### 9. Copilot Studio Kit — Compliance Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:e02679dd86c20d49730b5f4f6b8a15f32234420084cb44d2e1c42e4a00c239b2

**What Changed:**
```diff
--- +++ @@ -27,6 +27,10 @@ New articles
 Measure the return on investment (ROI) and business value of AI agents
 Plan Copilot Studio agent deployments for throughput and rate limits
+Other updates
+New real-world case study on how
+Grupo Bimbo standardizes global audit processes with Copilot Studio
+.
 May 2026
 Architecting agent solutions
 moved to the

```

---

### 10. Retention Labels

**URL:** https://learn.microsoft.com/en-us/purview/create-retention-labels-data-lifecycle-management
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:6dd3a06b0a93915d14aeb0d594815c675075a3e09cac5b50c52f4fd6b8cc3db6

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`

**What Changed:**
```diff
--- +++ @@ -60,6 +60,8 @@ Select
 Create a label
 and follow the prompts to create the retention label. Be careful what name you choose, because this can't be changed after the label is saved.
+Note
+Double quotation marks ("") aren't supported in retention label names. For example, ""Permanent Label"" isn't supported.
 For more information about the retention settings, see
 Settings for retaining and deleting content
 .

```

---

### 11. Endpoint DLP

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:67f0668bb80b33ec3320d4d558d74a9f3e70c3e071b68c9a48448de1e63cca00

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -582,9 +582,6 @@ Just-in-time protection blocks egress activities on these monitored files until policy evaluation completes successfully:
 Items that have never been evaluated.
 Items on which the evaluation has gone stale. These are previously evaluated items that haven't been reevaluated by the current, updated cloud versions of the policies.
-Unsaved files (preview) â brand-new files that have never been saved, or existing files with unsaved modifications, including the window before autosave completes. For more information, see
-Unsaved file protection
-.
 For more information on how just-in-time protection works,see
 Learn about just-in-time protection
 , and
@@ -600,6 +597,7 @@ Getting started with Microsoft Endpoint data loss prevention
 Using Microsoft Endpoint data loss prevention
 Learn about data loss prevention
+Investigate endpoint DLP evidence in Data Security Investigations (preview)
 Create and Deploy data loss prevention policies
 Get started with Activity explorer
 Microsoft Defender for Endpoint

```

---

### 12. Custom Analytics Rules

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/create-analytics-rules
**Section:** Azure Services
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:fe9c017ba6644694a86fef736cf81aeb4c3f5a07b5742439b6364883e0086226

**What Changed:**
```diff
--- +++ @@ -38,7 +38,7 @@ to find and install the recommended rules specific to that recommendation. For more information, see
 SOC optimization usage flow
 .
-This article describes the process of creating an analytics rule from scratch, including using the
+This section describes the process of creating an analytics rule from scratch, including using the
 Analytics rule wizard
 . It includes screenshots and directions to access the wizard in both the Azure portal and the Defender portal.
 Important
@@ -66,7 +66,9 @@ Important
 Make sure that your query returns the
 TimeGenerated
-column, as scheduled analytics rules use it as the reference for the lookback period. This means that the rule only evaluates records where the
+column, as scheduled analytics rules use it as the reference for the lookback period. Because
+TimeGenerated
+serves as the lookback reference, the rule only evaluates records where the
 TimeGenerated
 value falls within the specified lookback window.
 Build and test your queries in the
@@ -78,7 +80,7 @@ Kusto Query Language in Microsoft Sentinel
 Best practices for Kusto Query Language queries
 Create your analytics rule
-This section describes how to create a rule by using the Azure or Defender portals.
+The following procedure explains how to create a scheduled analytics rule by using the Azure portal or the Defender portal.
 Get started creating a scheduled query rule
 To get started, go to the
 Analytics
@@ -149,7 +151,7 @@ Defender portal
 Azure portal
 Define the rule logic
-The next step is to set the rule logic, which includes adding the Kusto query that you created.
+Set the rule logic, including adding the Kusto query that you created.
 Enter the rule query and alert enhancement configuration.
 Setting
 Description
@@ -162,7 +164,7 @@ Entity mapping
 and define up to 10 entity types recognized by Microsoft Sentinel onto fields in your query results. This mapping integrates the identified entities into the
 Entities
-field in your alert
```

---

### 13. Apply IRM to SharePoint

**URL:** https://learn.microsoft.com/en-us/purview/apply-irm-to-a-list-or-library
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:77041f69953eceb7eed260532a4ba096757b662972c66104e8e92457630be5b5

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

**What Changed:**
```diff
--- +++ @@ -23,7 +23,7 @@ Feedback
 Summarize this article for me
 Microsoft Purview service description
-You can use Information Rights Management (IRM) to help control and protect files that are downloaded from lists or libraries. This feature is only supported in the Microsoft global cloud. IRM isn't supported for SharePoint lists and libraries in national cloud deployments.
+You can use Information Rights Management (IRM) to help control and protect files that are downloaded from lists or libraries. IRM for SharePoint lists and libraries is only supported in the Microsoft global cloud. IRM isn't supported for SharePoint lists and libraries in national cloud deployments.
 Administrator preparations before applying IRM
 The Azure Rights Management service from Microsoft Purview Information Protection, and the on-premises equivalent, Active Directory Rights Management Services (AD RMS), support Information Rights Management for sites. No other installations are required.
 Before you apply IRM to a list or library, you need to enable IRM for your site. You need administrator permissions for the site to enable IRM. In addition, to apply IRM to a list or library, you must have administrator permissions for that list or library.
@@ -31,6 +31,7 @@ Note
 If you're using SharePoint Server 2013, a server administrator must install protectors on all front-end Web servers for every file type that the users in your organization want to protect by using IRM.
 Apply IRM to a list or library
+Perform the following steps to configure IRM settings for a list or library:
 Go to the list or library for which you want to configure IRM.
 On the ribbon, select the
 Library
@@ -104,7 +105,7 @@ What is Information Rights Management?
 Information Rights Management (IRM) enables you to limit the actions that users can take on files that downloaded from lists or libraries. IRM encrypts the downloaded files and limits the set of users and programs that are allowed to decrypt these files. IRM
```

---

### 14. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:b97124711a73b6da232bb207aa66c2cbe01ba73fa0ef923e8e8a68cc5bd3dea3

**What Changed:**
```diff
--- +++ @@ -71,6 +71,12 @@ Monitor device health with the device health reports dashboard
 . Use the device health reports dashboard to monitor device onboarding status, policy update readiness, and feature readiness for Endpoint DLP.
 Data Security Investigations
+In preview
+:
+Endpoint DLP evidence collection
+is now available as a data source in Data Security Investigations. Investigators can query data captured by endpoint Data Loss Prevention (DLP) policies on onboarded devices and add the associated content to an investigation scope for AI-powered analysis. This integration enables aggregate analysis of endpoint exfiltration events instead of per-alert triage. For more information, see
+Search, review, and refine results in Data Security Investigations
+.
 General availability (GA)
 :
 Email and portal notifications
@@ -291,14 +297,6 @@ : The
 Get started with just-in-time protection
 article now focuses on deployment and configuration steps.
-In preview
-:
-Unsaved file protection
-extends just-in-time (JIT) protection to files that haven't been saved yet, including brand-new files and files with unsaved modifications. For more information, see
-Get started with just-in-time protection
-and
-Learn about unsaved file protection
-.
 New
 : A new conceptual article,
 Learn about just-in-time protection

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Managed Environment Sharing Limits
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-sharing-limits
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:5b36505acbf7a353b885bf4e3bf3c5af8f99a6be2899ca5fce73b5d1f163d0b1

---

### 2. Solution Checker Enforcement
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-solution-checker
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:843ee09412b341e156ad6681d6c6096d54e07b66f9dde2fd818a27419c9ffa45

---

### 3. Advanced Connector Policies
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:15a99109dfeaf7fd4ad3e2cb78e29262df280c843c054c8a5797b13a25c04bb8

---

### 4. Security
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:680806eee53b6cb9eb1bdf5c41ffa42e2133a2f433866b5deb509c3795a08087

---

### 5. Monitoring Hub
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitoring-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:5227131027b8dd11cb153e03f429aade280eb9bc1ab7618c506399907388f7f6

---

### 6. Copilot Hub
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2c8d3677a6236d395618e51f1741ee97dd993b3db2fb2276e7898e06a640e2cd

---

### 7. Maker Onboarding (Welcome Content)
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/welcome-content
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:689638a611c072d6d76fb7f79cd43ba43c8671dfc2d58e441899dcf8a9f103ae

---

### 8. Agent Access Points
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/security/identity-access-management#agent-access-points-preview
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:4b903f1ccf84823055d2550cde3fb1a716f58c7e7cd17c209b489e174071a2c9

---

### 9. Capacity Storage
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c667ec53cdf2ca36fcbf2e593ac8d52984df67a9940f0b3d20fa3407c525669a

---

### 10. CoE Power BI Monitor
**URL:** https://learn.microsoft.com/en-us/power-platform/guidance/coe/power-bi-monitor
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:1691ad821818f8af59fa04236e22686cd72106920e41966ba6f4122f0bd0a8d2

---

### 11. Default Deployment Pipeline
**URL:** https://learn.microsoft.com/en-us/power-platform/alm/default-deployment-pipeline-rule-for-environment-groups
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:41565c4221edc1c5a64f04304b0e388ddc93b01036b86c3e190885cb6229415d

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*