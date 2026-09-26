# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-26
**Run Time:** 2026-09-26T10:57:52.834194+00:00
**Total URLs Checked:** 231

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 3 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | default-environment-routing | HIGH | 2.15 | Review and update |
| 2 | backup-restore-environments | HIGH | 2.4 | Update portal-walkthrough |
| 3 | overview | HIGH | None | Review and update |
| 4 | run-scheduled-tasks | HIGH | 3.3, 3.6 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Backup and Restore

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments
**Section:** Power Platform Administration
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:d970f833e369860f7719548f79041e7dc35a469a6ecc1794e3417d1729ff32fb

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -461,8 +461,12 @@ Recover environment
 .
 Troubleshooting
+The environment operation runs for a long time. What action can I take?
+The length of restore and copy operations varies depending on the size of the data involved, so it's common for these operations to take a long time. If the source environment has large amounts of data (such as database, file, log, audit, lake, or search data), the operation can take up to 48 hours to complete. These operations complete on their own without intervention from Microsoft Support. Wait 48 hours after the operation starts before you create a support ticket.
 The restore operation failed. What action can I take?
 The restore process, especially for environments with large amounts of data, is a complex backend operation. If the restore operation fails, the target environment is disabled. To retry the restore process, the failed environment must be the target environment for the operation. Wait 30 minutes and retry the operation. The other actions you can take for the disabled, target environment are reset, delete, or copy to as a target environment.
+I created a manual backup but can't restore from it yet
+If you're restoring from a manual backup, the backup can take up to 10 minutes to be ready for restoration. Wait at least 10 minutes after you create a manual backup before you attempt to restore your data from it.
 You don't see the environment that you want to restore to
 The source environment can be a production, sandbox, developer, Teams, or default environment.
 The target environment can be a sandbox, developer, or Teams environment. If the source is a default environment, the target must be a developer environment.

```

---

## HIGH: Control Review Recommended

### 1. Environment Routing

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:fe9a9f175196d4d95271b761ec816bf3641b85d094bace89bd1b74027afe2a99

**Affected Controls:**
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -22,20 +22,20 @@ Environment routing
 Feedback
 Summarize this article for me
-Environment routing is a premium governance feature. This feature allows Power Platform admins to automatically direct new or existing makers into their own personal developer environments when they visit
+Environment routing is a premium governance feature. Power Platform admins can use this feature to automatically direct new or existing makers into their own personal developer environments when they visit
 Copilot Studio
 ,
 Power Apps
 ,
 Power Automate
-, or Power Automate for desktop. Environment routing offers makers a personal, safe space to build with Microsoft Dataverse without the fear of others accessing their apps or data.
+, or Power Automate for desktop. Environment routing offers makers a personal, safe space to build with Microsoft Dataverse without the fear of others accessing their apps or data. It also helps admins ensure that makers can build and customize their applications without affecting shared or default environments.
 In this video, check out what's new with environment routing in the Power Platform admin center.
-When the
-Environment routing
-setting is enabled in
+When you turn on the
+Environment routing
+setting in
 Power Platform admin center
 , the maker lands in their own personal developer environment instead of the default environment. Personal developer environments are the makers' own spaces, like OneDrive, for personal productivity where they can start building apps and solutions in their own workspace. Makers don't need to know which environment to work in, since the personal developer environment appears automatically.
-When the feature is turned on, the selected maker type (that is, new or existing makers), are directed into their own, personal developer environment. If the maker has access to one or more existing developer environments that aren't owned by them, they're routed to a new developer environment.
+When you turn on the fea
```

---

### 2. Azure Key Vault

**URL:** https://learn.microsoft.com/en-us/azure/key-vault/general/overview
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:0a268f700c1a23a5ab88ad141ec19c9a0e6c45792c56c98c4352b30eafa566e6

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -51,7 +51,7 @@ Access to a key vault requires proper authentication and authorization before a caller (user or application) can get access. Authentication establishes the identity of the caller, while authorization determines the operations that they're allowed to perform.
 Authentication is done via Microsoft Entra ID. Authorization may be done via Azure role-based access control (Azure RBAC) or Key Vault access policy. Azure RBAC can be used for both management of the vaults and to access data stored in a vault, while key vault access policy can only be used when attempting to access data stored in a vault.
 Azure Key Vault provides multiple layers of security to protect your data. All key vaults are encrypted at rest using keys stored in hardware security modules (HSMs), and Azure safeguards your keys, secrets, and certificates using industry-standard algorithms, key lengths, and cryptographic protection.
-For organizations requiring the highest level of security, the Premium tier offers HSM-protected keys (RSA-HSM, EC-HSM, or OCT-HSM) that never leave the HSM boundary. These Premium tier HSMs utilize Marvell LiquidSecurity hardware with FIPS 140-3 Level 3 validation, ensuring the most stringent cryptographic protection available.
+For organizations requiring the highest level of security, the Premium tier offers HSM-protected keysâRSA-HSM, EC-HSM, and OCT-HSM (symmetric/AES, preview)âthat never leave the HSM boundary. These Premium tier HSMs utilize Marvell LiquidSecurity hardware with FIPS 140-3 Level 3 validation, ensuring the most stringent cryptographic protection available.
 Both Standard and Premium tiers use
 Federal Information Processing Standard 140 validated software cryptographic modules and HSMs
 to meet rigorous security and compliance standards.

```

---

### 3. Scheduled Flows

**URL:** https://learn.microsoft.com/en-us/power-automate/run-scheduled-tasks
**Section:** Power Automate
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:4bbfca71ff9cc389a43f168b9af0cb384ef0d45cda861118ddf64e0aaa0fbcba

**Affected Controls:**
- Control 3.3: Control 3.3: Compliance and Regulatory Reporting
  - File: `controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`

**What Changed:**
```diff
--- +++ @@ -41,20 +41,21 @@ On the navigation pane to the left, make sure that
 Home
 is selected.
-In the
-Create your automation with Copilot
-field, type the following prompt:
-Create a flow that runs Monday every week starting [DATE] which sends an email to contoso@gmail.com that their MPR doc is due.**
-Select
-Generate
-.
+Select
+Create with Copilot
+.
+In the text field, type the following prompt:
+Create a flow that runs Monday every week starting next week, which sends an email to contoso@gmail.com that their MPR doc is due.**
+Select the submit (paper airplane) icon button to continue.
 Copilot generates a flow based on your prompt. You can review the generated flow and make any necessary adjustments. If you're satisfied with the suggested flow, select
 Keep it and continue
 .
-Review the connected apps and services. A green checkmark means the connection is ready to go.
+Review the connected apps and services on the
+Step 2 of 2: Make sure everything's ready
+screen. A green checkmark means the connection is ready to go.
 If you don't have a green checkmark, select the connection to set it up.
 Select
-Create flow
+Save
 .
 Use Copilot to configure actions
 In the designer, select
@@ -62,7 +63,7 @@ .
 In the Copilot panel, ask Copilot to make changes to your scheduled flow. For example, you can enter the following prompt:
 Change the interval from every week to 2 weeks.
-After Copilot generates a response, it confirms that it made the update successfully. If you change your mind, you can select
+After Copilot generates a response, it confirms that it made the update successfully. If you change your mind, select
 Undo
 to revert the changes.
 If you're not using Copilot to configure your actions, go to
@@ -73,17 +74,43 @@ .
 Select
 My flows
->
-New flow
->
-Scheduled cloud flow
-.
-In the fields next to
-Starting
-, specify the date and time when your flow should start.
-In the fields next to
-Repeat every
-, specify the flow's recurrence.
+and then sele
```

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