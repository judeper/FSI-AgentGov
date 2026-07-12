# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-12
**Run Time:** 2026-07-12T08:19:37.414629+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 48 |
| HIGH Changes | 61 |
| MEDIUM Changes | 150 |
| Redirects | 2 |

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
| 7 | environment-groups-rules | MEDIUM | 2.2 | Update portal-walkthrough |
| 8 | default-environment-routing | HIGH | 2.15 | Review and update |
| 9 | create-developer-environment | MEDIUM | 2.15 | Review optional |
| 10 | advanced-connector-policies | MEDIUM | 1.4 | Update portal-walkthrough |
| 11 | wp-data-loss-prevention | MEDIUM | 3.7, 2.24, 2.7, 1.14, 1.28, 1.5 | Update portal-walkthrough |
| 12 | dlp-connector-classification | MEDIUM | 4.6, 1.14 | Update portal-walkthrough |
| 13 | connections-list | MEDIUM | None | Review optional |
| 14 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Review and update |
| 15 | ...m/en-us/connectors/custom-connectors/ | MEDIUM | 2.7 | Review optional |
| 16 | security-overview | MEDIUM | 3.7, 1.8, 1.26 | Review and update |
| 17 | security-roles-privileges | MEDIUM | 2.8, 1.1, 1.18 | Review optional |
| 18 | create-edit-security-role | MEDIUM | 1.18 | Review optional |
| 19 | database-security | MEDIUM | 1.1 | Review optional |
| 20 | field-level-security | MEDIUM | 1.18 | Review optional |
| 21 | manage-high-privileged-admin-roles | MEDIUM | 2.8 | Review optional |
| 22 | ip-firewall | HIGH | 1.20 | Update portal-walkthrough |
| 23 | customer-managed-key | HIGH | 1.15 | Update portal-walkthrough |
| 24 | analytics-common-data-service | MEDIUM | 2.9 | Review optional |
| 25 | self-service-analytics | MEDIUM | 2.9 | Review optional |
| 26 | power-platform-inventory | HIGH | 3.11 | Review and update |
| 27 | monitor-copilot-studio | MEDIUM | 3.2 | Review optional |
| 28 | monitoring-overview | MEDIUM | None | Review optional |
| 29 | alerts | HIGH | None | Review and update |
| 30 | activity-logs-power-platform-admin | MEDIUM | None | Review optional |
| 31 | copilot-hub | MEDIUM | 3.1, 3.8 | Review and update |
| 32 | identity-access-management | CRITICAL | None | Monitor |
| 33 | manage-copilot-studio-messages-capacity | MEDIUM | 2.27 | Update portal-walkthrough |
| 34 | business-continuity-disaster-recovery | CRITICAL | 2.4 | Update portal-walkthrough |
| 35 | backup-restore-environments | CRITICAL | 2.4 | Update portal-walkthrough |
| 36 | capacity-storage | MEDIUM | 3.5 | Review optional |
| 37 | powerapps-powershell | MEDIUM | None | Review optional |
| 38 | powershell-getting-started | MEDIUM | 3.1 | Review optional |
| 39 | dlp-strategy | MEDIUM | 1.4 | Review optional |
| 40 | environment-strategy | HIGH | 2.4 | Review and update |
| 41 | power-bi-monitor | MEDIUM | 2.6 | Review optional |
| 42 | ...ower-platform/release-plan/2025wave2/ | HIGH | 1.27 | Review and update |
| 43 | ...ower-platform/release-plan/2026wave1/ | HIGH | 3.8, 2.25, 2.8, 2.17, 2.10, 2.3, 1.4, 1.18 | Review and update |
| 44 | ...ilot-security-enhanced-admin-controls | MEDIUM | 2.8, 2.3, 1.18 | Review optional |
| 45 | pipelines | HIGH | 2.5, 2.3, 1.28 | Update portal-walkthrough |
| 46 | set-up-pipelines | MEDIUM | 2.3 | Review optional |
| 47 | run-pipeline | MEDIUM | 2.3 | Review optional |
| 48 | ...-pipeline-rule-for-environment-groups | MEDIUM | None | Review optional |
| 49 | solution-concepts-alm | MEDIUM | 2.4, 2.3 | Review optional |
| 50 | admin-deployment-hub | HIGH | 2.1, 2.3 | Update portal-walkthrough |
| 51 | fundamentals-what-is-copilot-studio | MEDIUM | 2.13 | Review optional |
| 52 | security-and-governance | MEDIUM | 2.8, 1.8, 1.1, 1.4, 1.3, 1.28, 1.5 | Update portal-walkthrough |
| 53 | sensitivity-label-copilot-studio | MEDIUM | 1.26 | Update portal-walkthrough |
| 54 | ...ication-fundamentals-publish-channels | MEDIUM | None | Review optional |
| 55 | admin-share-bots | HIGH | 3.2, 3.10, 2.5, 2.9, 2.6 | Update portal-walkthrough |
| 56 | analytics-overview | MEDIUM | 3.2, 3.10, 2.5, 2.9, 2.6 | Update portal-walkthrough |
| 57 | analytics-improve-agent-effectiveness | MEDIUM | None | Update portal-walkthrough |
| 58 | advanced-connectors | MEDIUM | None | Review optional |
| 59 | knowledge-copilot-studio | MEDIUM | 2.16, 4.8, 1.14 | Update portal-walkthrough |
| 60 | nlu-gpt-overview | MEDIUM | 2.12 | Review optional |
| 61 | add-tools-custom-agent | MEDIUM | 2.17 | Review optional |
| 62 | external-security-provider | MEDIUM | 1.8 | Update portal-walkthrough |
| 63 | advanced-hand-off | MEDIUM | 2.19, 2.12 | Update portal-walkthrough |
| 64 | authoring-test-bot | HIGH | 2.5 | Update portal-walkthrough |
| 65 | admin-network-isolation-vnet | MEDIUM | None | Review optional |
| 66 | whats-new | HIGH | 2.25, 2.5, 2.10 | Review and update |
| 67 | sec-gov-intro | MEDIUM | 3.8 | Review optional |
| 68 | ...rosoft.com/en-us/agents/architecture/ | MEDIUM | 2.17, 2.12, 2.3 | Review optional |
| 69 | mcp-create-new-server | MEDIUM | None | Review and update |
| 70 | ...-governance-agentic-center-enablement | MEDIUM | None | Review optional |
| 71 | whats-new | HIGH | None | Review and update |
| 72 | microsoft-365-copilot-overview | MEDIUM | 3.8 | Review optional |
| 73 | microsoft-365-copilot-privacy | HIGH | 2.23, 4.7, 4.6 | Update portal-walkthrough |
| 74 | microsoft-365-copilot-enable-users | MEDIUM | None | Review optional |
| 75 | manage-copilot-agents-integrated-apps | MEDIUM | 3.11, 3.1, 3.6, 3.8, 2.25 | Review optional |
| 76 | microsoft-365-copilot-usage | MEDIUM | 3.8 | Review and update |
| 77 | overview | MEDIUM | 3.8 | Review optional |
| 78 | security-governance | MEDIUM | None | Review optional |
| 79 | management-controls | MEDIUM | 3.8 | Review optional |
| 80 | agent-essentials-overview | MEDIUM | 2.25 | Review optional |
| 81 | agent-prerequisites | MEDIUM | 2.25 | Review optional |
| 82 | m365-agents-visual-map | MEDIUM | 1.1 | Review optional |
| 83 | m365-agents-checklist | MEDIUM | 3.5, 3.1, 1.1, 1.6, 1.11, 1.5 | Review optional |
| 84 | overview | HIGH | 3.13, 3.1, 2.25, 2.12, 2.6 | Update portal-walkthrough |
| 85 | .../en-us/microsoft-agent-365/developer/ | MEDIUM | 3.14, 3.2, 3.6, 2.5, 1.7 | Review and update |
| 86 | agent-365-overview | MEDIUM | 3.8, 2.25 | Review and update |
| 87 | agent-365-security | MEDIUM | 3.7, 2.25 | Review optional |
| 88 | human-in-the-loop | HIGH | 2.17, 2.12 | Review and update |
| 89 | dlp-learn-about-dlp | MEDIUM | 1.25, 1.3, 1.26, 1.5 | Update portal-walkthrough |
| 90 | dlp-create-deploy-policy | HIGH | 1.5 | Update portal-walkthrough |
| 91 | dlp-policy-reference | HIGH | 1.5 | Review and update |
| 92 | sensitivity-labels | MEDIUM | 1.3, 1.26, 1.5 | Update portal-walkthrough |
| 93 | sensitivity-labels-teams-groups-sites | MEDIUM | 1.3, 1.5 | Update portal-walkthrough |
| 94 | audit-solutions-overview | HIGH | 2.13, 4.5, 1.7, 1.28, 1.27 | Review and update |
| 95 | audit-copilot | MEDIUM | 1.21, 1.6, 1.7, 1.14, 1.19 | Review and update |
| 96 | audit-log-retention-policies | HIGH | 3.14, 4.5, 1.7 | Update portal-walkthrough |
| 97 | audit-search | HIGH | 3.2, 3.12, 1.7 | Update portal-walkthrough |
| 98 | ai-microsoft-purview | MEDIUM | 2.6, 4.8, 4.7, 1.6, 1.16, 1.5 | Review and update |
| 99 | dspm-for-ai-considerations | MEDIUM | 1.6 | Review optional |
| 100 | communication-compliance | MEDIUM | 1.21, 1.10 | Update portal-walkthrough |
| 101 | communication-compliance-policies | HIGH | 1.10 | Update portal-walkthrough |
| 102 | ...tion-compliance-investigate-remediate | HIGH | 1.10 | Update portal-walkthrough |
| 103 | insider-risk-management | MEDIUM | 1.6, 1.12, 1.5 | Update portal-walkthrough |
| 104 | insider-risk-management-policies | HIGH | 1.12 | Update portal-walkthrough |
| 105 | ...management-settings-policy-indicators | HIGH | 1.12 | Update portal-walkthrough |
| 106 | insider-risk-management-activities | CRITICAL | 1.12 | Update portal-walkthrough |
| 107 | import-hr-data | MEDIUM | 1.12 | Update portal-walkthrough |
| 108 | ...ensitive-information-type-learn-about | MEDIUM | 1.13 | Review and update |
| 109 | ...e-a-custom-sensitive-information-type | HIGH | 1.13 | Review and update |
| 110 | sit-create-a-keyword-dictionary | HIGH | 1.13 | Review and update |
| 111 | ...arn-about-exact-data-match-based-sits | MEDIUM | 1.13 | Review and update |
| 112 | trainable-classifiers-learn-about | MEDIUM | 1.13 | Review and update |
| 113 | retention | MEDIUM | 3.5, 2.13, 4.3, 1.19, 1.9 | Update portal-walkthrough |
| 114 | create-retention-policies | MEDIUM | 4.3, 1.9 | Review and update |
| 115 | ...tion-labels-data-lifecycle-management | HIGH | 4.3, 1.9 | Review and update |
| 116 | retention-policies-sharepoint | MEDIUM | 4.3 | Review and update |
| 117 | disposition | MEDIUM | 1.9 | Review and update |
| 118 | retention-regulatory-requirements | MEDIUM | 4.3, 1.9 | Review and update |
| 119 | records-management | MEDIUM | 3.3, 2.13, 1.9 | Review and update |
| 120 | data-lifecycle-management | MEDIUM | None | Review optional |
| 121 | ediscovery | MEDIUM | 1.19, 1.9 | Review optional |
| 122 | ediscovery-create-and-manage-cases | MEDIUM | 1.19 | Review optional |
| 123 | ...keyword-queries-and-search-conditions | MEDIUM | 1.19 | Review optional |
| 124 | ediscovery-create-holds | MEDIUM | 1.19, 1.9 | Review optional |
| 125 | endpoint-dlp-learn-about | HIGH | 1.17 | Review and update |
| 126 | endpoint-dlp-getting-started | HIGH | 1.17 | Review and update |
| 127 | dlp-configure-endpoint-settings | HIGH | 1.17 | Review and update |
| 128 | information-barriers | MEDIUM | 1.22 | Update portal-walkthrough |
| 129 | encryption-sensitivity-labels | MEDIUM | 1.16 | Review optional |
| 130 | encryption | MEDIUM | 1.16 | Review optional |
| 131 | data-classification-activity-explorer | MEDIUM | 1.6, 1.14 | Review optional |
| 132 | compliance-manager | MEDIUM | 3.3, 2.13 | Review optional |
| 133 | compliance-manager-assessments | HIGH | 3.3, 2.13 | Review and update |
| 134 | overview | MEDIUM | 1.11 | Review and update |
| 135 | concept-conditional-access-policies | MEDIUM | None | Review and update |
| 136 | concept-conditional-access-cloud-apps | MEDIUM | None | Review optional |
| 137 | ...o-conditional-access-session-lifetime | MEDIUM | None | Review optional |
| 138 | concept-authentication-strengths | MEDIUM | None | Review and update |
| 139 | overview-authentication | MEDIUM | 1.11 | Review optional |
| 140 | how-to-authentication-passkeys-fido2 | MEDIUM | None | Review optional |
| 141 | custom-overview | MEDIUM | None | Review optional |
| 142 | permissions-reference | CRITICAL | 2.23 | Monitor |
| 143 | access-reviews-overview | MEDIUM | 1.14 | Update portal-walkthrough |
| 144 | create-access-review | MEDIUM | 2.8, 4.2, 1.3 | Review optional |
| 145 | pim-configure | MEDIUM | 2.8, 1.18 | Update portal-walkthrough |
| 146 | what-is-microsoft-entra-agent-id | MEDIUM | 1.11, 1.18 | Review optional |
| 147 | agent-id-governance-overview | HIGH | 3.6, 2.26, 1.11 | Review and update |
| 148 | sharepoint-admin-role | MEDIUM | None | Review optional |
| 149 | modern-experience-sharing-permissions | MEDIUM | 4.8, 1.14 | Review and update |
| 150 | external-sharing-overview | MEDIUM | 4.4 | Review and update |
| 151 | turn-external-sharing-on-or-off | HIGH | 4.4, 1.3 | Review and update |
| 152 | restricted-access-control | HIGH | 4.1, 1.3 | Review and update |
| 153 | restricted-content-discovery | HIGH | 4.7, 4.1, 4.6, 1.3, 1.14 | Review and update |
| 154 | restricted-sharepoint-search | HIGH | 4.7, 4.1, 4.6, 1.3, 1.14 | Review and update |
| 155 | advanced-management | MEDIUM | 4.5, 4.2, 4.1, 4.6, 1.3 | Review and update |
| 156 | data-access-governance-reports | HIGH | 4.5, 4.2, 4.1, 4.4, 4.6, 1.3, 1.14 | Update portal-walkthrough |
| 157 | site-lifecycle-management | CRITICAL | 4.2, 4.3 | Review and update |
| 158 | request-site-attestations | HIGH | 4.2 | Review and update |
| 159 | information-barriers-sharepoint | MEDIUM | None | Review optional |
| 160 | insights-on-sharepoint-agents | MEDIUM | 4.5 | Review and update |
| 161 | control-lists | MEDIUM | None | Review optional |
| 162 | create-training-site | MEDIUM | None | Review optional |
| 163 | ...ntent-approval-and-check-out-planning | MEDIUM | 2.16 | Review optional |
| 164 | create-retention-policies | MEDIUM | None | Review optional |
| 165 | manage-addins-in-the-admin-center | MEDIUM | 1.2 | Review optional |
| 166 | view-service-health | MEDIUM | 3.4 | Review optional |
| 167 | message-center | MEDIUM | 2.10 | Review optional |
| 168 | overview | MEDIUM | 3.9 | Review optional |
| 169 | connect-data-sources | MEDIUM | 3.9 | Review optional |
| 170 | create-analytics-rules | HIGH | None | Review and update |
| 171 | threat-detection | MEDIUM | None | Review optional |
| 172 | monitor-your-data | HIGH | 3.9 | Review and update |
| 173 | ...cident-handling-with-automation-rules | HIGH | 3.9 | Review and update |
| 174 | investigate-cases | HIGH | None | Review and update |
| 175 | overview | MEDIUM | None | Review and update |
| 176 | private-link-service | MEDIUM | 1.20 | Review optional |
| 177 | private-link-overview | MEDIUM | 1.20 | Review optional |
| 178 | immutable-storage-overview | MEDIUM | 2.13, 1.7 | Update portal-walkthrough |
| 179 | alerts-overview | HIGH | 2.9 | Review and update |
| 180 | overview | MEDIUM | 2.10 | Review optional |
| 181 | information-protection | MEDIUM | 1.16 | Review optional |
| 182 | track-and-revoke-admin | HIGH | None | Review and update |
| 183 | apply-irm-to-a-list-or-library | HIGH | 1.16 | Review and update |
| 184 | concept-responsible-ai | MEDIUM | 2.21 | Review optional |
| 185 | overview | MEDIUM | 1.8, 1.27 | Update portal-walkthrough |
| 186 | overview-cost-management | MEDIUM | 3.5 | Review optional |
| 187 | tutorial-acm-create-budgets | MEDIUM | 3.5 | Review optional |
| 188 | overview | MEDIUM | None | Review optional |
| 189 | device-control-overview | MEDIUM | 1.17 | Review optional |
| 190 | get-started-approvals | MEDIUM | 3.12, 3.10, 2.16, 2.21 | Update portal-walkthrough |
| 191 | run-scheduled-tasks | MEDIUM | 3.6, 3.3 | Review optional |
| 192 | use-powerapps-checker | MEDIUM | None | Review optional |
| 193 | plan-designer | MEDIUM | None | Review optional |
| 194 | information-barriers-teams | MEDIUM | None | Review optional |
| 195 | application | MEDIUM | 1.2 | Review optional |
| 196 | accessreviewsv2-overview | MEDIUM | 4.2 | Review optional |
| 197 | fabric-adoption-roadmap-governance | MEDIUM | None | Review optional |
| 198 | overview-viva-learning | MEDIUM | 2.14 | Review optional |
| 199 | incident-response-planning | MEDIUM | None | Review optional |
| 200 | new-dlpcompliancepolicy | MEDIUM | 1.5 | Review optional |
| 201 | ...365-management-activity-api-reference | MEDIUM | 1.7 | Review and update |
| 202 | whats-new | CRITICAL | None | Monitor |
| 203 | pricing-billing-skus | MEDIUM | 3.5, 2.1 | Review optional |
| 204 | microsoft-365-overview | MEDIUM | None | Review optional |
| 205 | ...ecurity-compliance-licensing-guidance | MEDIUM | 1.21, 1.13, 1.19 | Update portal-walkthrough |
| 206 | microsoft-purview-service-description | HIGH | None | Review and update |
| 207 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Managed Environments

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:f26a1f9cef530b0543a6f672e1e8a71cc2b06debfd69178e889addeb949e52be

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
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -19,13 +19,13 @@ Access to this page requires authorization. You can try
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
+Managed environments are included as an entitlement with standalone Power Apps, Power Automate, Microsoft Copilot Studio, Power Pages, and Dynamics 365 
```

---

### 2. Managed Environment Sharing Limits

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-sharing-limits
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:37cb138e983d31e6cea9986625eb8033b11e2a3a74a08ec6847902d4f327d099

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
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -22,7 +22,7 @@ Limit sharing
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
 Set-AdminPowerAppEnvironmentGovernanceConfiguration -Environ
```

---

### 3. Environment Groups

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/environment-groups
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:b9c71638b8d680a0550257bea492b2d4ff68e663edab0fb513aa9df78dac7ad3

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
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -25,7 +25,7 @@ Managing the Power Platform on a large scale across numerous environments, ranging from hundreds to tens of thousands, poses a significant challenge for both startup and enterprise IT teams. To address these complexities, environment groups offer a premium governance solution designed to streamline management tasks by organizing environments into logical collections and enforcing uniform policies and configurations.
 Think of an environment group as a "folder" for your environments. Administrators can cluster a flat list of environments into structured groups based on criteria such as business unit, project, geographic region, or purpose. By creating these logical collections, IT teams gain the ability to manage multiple environments simultaneously and efficiently implement security, governance, and compliance policies on a large scale through centrally managed rules. This centralized approach eliminates the need to configure each environment one-by-one, ensures consistency, significantly reduces administrative overhead, and prevents issues such as configuration drift and chaotic management practices common in extensive deployments.
 Note
-Environment groups can only contain Managed Environments.
+Environment groups can only contain managed environments.
 Each environment can belong to only one group, and groups can't overlap or be nested.
 Environments in a group can span different regions and types as long as each is managed.
 Environments can be transferred between groups by removing them from one and adding them to another.
@@ -101,7 +101,7 @@ Power Platform for Admins V2 (Preview) connector
 offers an alternative solution. It allows the creation and deletion of environment groups and the ability to add or remove environments from these environment groups, facilitating opportunities for automation.
 Configure the rules for your
```

---

### 4. Environment Group Rules

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f5bbbd8c4cda402ff00f151e73e829363fee475e3e5584a4479ff4c23dad7a14

**Affected Controls:**
- Control 2.2: Control 2.2: Environment Groups and Tier Classification
  - File: `controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.2/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.2/troubleshooting.md` (HIGH)

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

```

---

### 5. Advanced Connector Policies

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e007bc61a0457ef21c92602e09e2915312c99518bf3bba29e5fafef98eedb7d6

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.4/troubleshooting.md` (HIGH)

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
@@ -244,8 +244,8 @@ : ACP doesn't support virtual connectors and won't support them in the future. For migration paths, see
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

### 6. DLP Policies (Power Platform)

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e13870a3c31f5cf53252c4b3d4f0b53b21ebdddddf1da9c87dcfdb7ca03284be

**Affected Controls:**
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 2.24: Control 2.24: Agent Feature Enablement and Restriction Governance
  - File: `controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md`
- Control 2.7: Control 2.7: Vendor and Third-Party Risk Management
  - File: `controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.25/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)
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

```

---

### 7. Connector Classification

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/dlp-connector-classification
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fba6bcd6d385591b302b192b3274cd6bdc88020dbe89b930d59da544e5c91c1a

**Affected Controls:**
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.14/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

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

```

---

### 8. IP Firewall

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/ip-firewall
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:cdc9c4ace7792c65920c5bf2abc9f0e649e3d2f6bf50e7057e99ba7073b3bbad

**Affected Controls:**
- Control 1.20: Control 1.20: Network Isolation and Private Connectivity
  - File: `controls/pillar-1-security/1.20-network-isolation-private-connectivity.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.1/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.1/verification-testing.md` (HIGH)

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
@@ -36,7 +36,7 @@ .
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
 In audit-only mode, the IP firewall identifies the IP addresses that are making calls to the environment and allows them all, whether
```

---

### 9. Encryption

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/customer-managed-key
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:2aea8db44bf0e16061712067b70e236a8b492e505eaa27415137b2c1030109a6

**Affected Controls:**
- Control 1.15: Control 1.15: Encryption: Data in Transit and at Rest
  - File: `controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.1/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.1/verification-testing.md` (HIGH)

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
@@ -90,8 +90,8 @@ Warning
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
 Add an environment to the enterprise poli
```

---

### 10. Copilot Studio Message Capacity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e591a8626eca0e48d52b387250bdb2ef0487c8d66c4ab11fee28f2e5283d5177

**Affected Controls:**
- Control 2.27: Control 2.27: Consumption-Entitlement Governance
  - File: `controls/pillar-2-management/2.27-consumption-entitlement-governance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.27/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.27/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.27/powershell-setup.md` (HIGH)

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

```

---

### 11. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:62bc12575d8914756c8ed383bcdd4a41b475fb292b04820dc87da39065408e3d

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

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
@@ -22,6 +22,8 @@ Business continuity and disaster recovery
 Feedback
 Summarize this article for me
+Note
+As of June 22, 2026, Self-Service Disaster Recovery (SSDR) is also available for Finance & Operations (F&O) applications. SSDR enables organizations to maintain an asynchronous secondary copy of their production environment in a paired Azure region and perform self-service failover, failback, and disaster recovery testing.
 Businesses expect their applications and customer data to be protected and resilient during unavoidable outages and disruptions. It's important to document a business continuity plan that minimizes the effects of outages. To recover and resume operations, make sure the plan lists stakeholders, processes, and specific steps.
 Microsoft provides business continuity and disaster recovery capabilities to all
 production type environments
@@ -101,7 +103,7 @@ Disaster recovery drill
 Emergency response for a major regional outage
 Disaster recovery drills
-Your company might have disaster recovery drills documented as a requirement in your internal business continuity plans. Some industries and companies might be required by government regulations to perform audits on their business continuity disaster recovery capabilities. In these cases, you can run a disaster recovery drill on an environment. A disaster recovery drill lets you do self-service disaster recovery without losing any data. The duration of the failover action can be slightly longer while all remaining data is replicated to the secondary region.
+Your company might document disaster recovery drills as a requirement in its internal business continuity plans. Some industries and companies are subject to government regulations that require audits on their business continuity and disaster recovery capabilities. In these cases, run a disaster recovery drill on an environ
```

---

### 12. Backup and Restore

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/backup-restore-environments
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:d6e04b46ad46f56307d232e0663f2694a149ad03fadf1f8a1953f29f117d7b48

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

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
@@ -22,11 +22,11 @@ Back up and restore environments
 Feedback
 Summarize this article for me
-It's important to protect your data on Microsoft Power Platform and in Dataverse and to provide continuous availability of service through system or manual backups.
-System backups are automatically created for environments that have a database. By default, backups of all production and nonproduction environments are retained for seven days. However, for production
-Managed Environments
-, the retention period can be extended up to 28 days through the Power Platform admin center or PowerShell.
-Manual backups are backups that the user initiates. It's recommended that you create manual backups before performing major customizations, applying a version update, or making significant changes to the environment. You can create these backups for production and sandbox environments, but not for the default environment. By default, manual backups are kept for seven days. For production Managed Environments, the retention period can be extended up to 28 days.
+Protect your data on Microsoft Power Platform and in Dataverse by providing continuous availability of service through system or manual backups.
+The system automatically creates backups for environments that have a database. By default, the system retains backups of all production and nonproduction environments for seven days. However, for production
+managed environments
+, you can extend the retention period up to 28 days through the Power Platform admin center or PowerShell.
+Manual backups are backups that you initiate. Create manual backups before major customizations, applying a version update, or making significant changes to the environment. You can create these backups for production and sandbox environments, but not for the default environment. By default, manual backups are kept for seven days. Fo
```

---

### 13. Pipelines Overview

**URL:** https://learn.microsoft.com/en-us/power-platform/alm/pipelines
**Section:** Power Platform ALM
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:e3c99bd213621737a671a674febd531e41674c5a68f26d251cb3de22e2e268ed

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
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -86,10 +86,10 @@ Deploy
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
+Yes. Tenant admins can automatically c
```

---

### 14. Admin Deployment Hub

**URL:** https://learn.microsoft.com/en-us/power-platform/alm/admin-deployment-hub
**Section:** Power Platform ALM
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:033d466a8d6f33a4ee9bfe4460d1f6283014bb55329d1c8a3b6d44023eb3f324

**Affected Controls:**
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.3/portal-walkthrough.md` (CRITICAL)

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
@@ -78,18 +78,18 @@ deployed to the target environment.
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
-Tenant admins (Power Platform and Dynamics 365 admins) can enable a setting that automatically converts pipelines target environmen
```

---

### 15. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2ec331e65ac84583004e2bb380873aba35d2985102f60cb7e86ae39d63a61876

**Affected Controls:**
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)

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

```

---

### 16. Sensitivity Labels in Copilot Studio

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b2f39a2ba409bfc1c7af456069eb64d5192e0306beaca4062f0aebdb48b6d9ed

**Affected Controls:**
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.26/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.26/troubleshooting.md` (HIGH)

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

```

---

### 17. Share and Manage Agents

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-share-bots
**Section:** Copilot Studio
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:43536e73d0681c5fde1249be22cf7a77e352b731ed1e532c9e4dffe44a32081c

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)

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
@@ -40,7 +40,7 @@ is turned on, to manage who can chat with the agent in your organization.
 Share an agent for chat
 Web app
-Teams
+Teams app
 Collaborators
 with authoring permissions for a shared agent can always chat with it. However, you can also grant users permission to chat with an agent in Copilot Studio without granting them authoring permissions.
 To grant users permission to only chat with the agent, you can:
@@ -171,7 +171,7 @@ to share the agent with everyone in the organization.
 Share an agent for collaborative authoring
 Web app
-Teams
+Teams app
 When you share an agent with others for
 collaborative authoring,
 you give them permission to view, edit, configure, share, and publish the agent. They can't delete the agent. You can only share agents for collaborative authoring with individual users in your organization. These users can be in different Power Platform environments, as long as they belong to your organization.
@@ -331,7 +331,7 @@ If you save your changes as a new topic, you can then review your coworker's changes, merge the two topics, and delete the copy when you're done.
 Stop sharing an agent
 Web app
-Teams
+Teams app
 You can stop sharing an agent with individual users, a security group, or everyone in your organization.
 Stop sharing with security groups
 On the top menu bar, select the three dots (
@@ -431,6 +431,14 @@ If you're a
 System Administrator
 , you can assign and manage environment security roles when sharing an agent.
+Users must have the
+ChatBotReaders
+privilege to chat with agents in an environment. The
+Environment Maker
+security role includes this privilege, which is why it's assigned when you share an agent with users who don't have sufficient permissions.
+Administrators can also create custom security roles with the
+ChatBotReaders
+privilege and assign them to users before sharing agents.
 T
```

---

### 18. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:67ddb3c6c52201074c0662ce176c561ef4cc81952bfab91d94363b5338ede7a6

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)

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

```

---

### 19. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:49116bbd42d20db85edb38be0a236011d85e31ef4796c59b1f546d77dac44da6

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

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
@@ -60,7 +60,11 @@ Custom metrics
 The
 Custom metrics
-section lets you define up to three business-specific metrics in natural language and track how often each outcome appears across sampled sessions. Use these metrics to complement your standard analytics insights with indicators that reflect your agent's goals and business use. To learn how to create, test, and refine custom metrics, see
+section lets you define up to three business-specific metrics in natural language and track how often each outcome appears across sampled sessions. Use these metrics to complement your standard analytics insights with indicators that reflect your agent's goals and business use.
+For users with the Bot Transcript Viewer privilege, you can
+drill down to a list of customer sessions
+filtered based on the selected segment of the donut graph. From the session list you can see the reasoning behind the metric and access the underlying the transcript by selecting individual sessions.
+To learn how to create, test, and refine custom metrics, see
 Analyze your agent with custom metrics
 .
 Effectiveness

```

---

### 20. Knowledge Sources

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:07f5e0a19485946ccc9bff6105ab1616d7a3180b63d264ff4003edbbaae22e4e

**Affected Controls:**
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)

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
@@ -29,23 +29,6 @@ generative answers node
 in an agent topic.
 You can incorporate knowledge sources into agents during their initial creation, add them after the agent is created, or add them to a generative answers topic node.
-Add and manage knowledge for generative answers
-Generative answers allow your agent to find and present information from multiple sources, internal or external, without having to create specific topics. Use generative answers as primary information sources or as a fallback source when authored topics can't answer a user's query. As a result, you can quickly create and deploy a functional agent. Makers don't need to manually author multiple topics, which might not address all customer questions.
-By default, when you create an agent, Copilot Studio automatically creates the
-Conversational boosting
-system topic. This topic contains a generative answers node, which you can use to begin utilizing knowledge sources immediately. All knowledge sources that you add at the agent level are added to generative answers node in the
-Conversational boosting
-system topic.
-For prerequisites and information on limitations, see
-Generative answers
-.
-For information on analytic metrics on a per knowledge source basis, see:
-Generated answer rate and quality
-for conversational agents.
-Knowledge source use
-for autonomous agents.
-Drill down on a theme
-for knowledge source metrics in the context of themes.
 Supported knowledge sources
 Name
 Source
@@ -101,6 +84,15 @@ Limits and limitations
 .
 Currently, citations returned from a knowledge source can't be used as inputs to other tools or actions.
+Source authentication
+If you're using SharePoint, Dataverse, or enterprise data with Microsoft Copilot connectors, you need to incorporate authentication. For more information, see
+Configure user authentication in Copilot Studio
+. For i
```

---

### 21. External Threat Detection

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-provider
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:408c3a5a9d34c3fe3f0e2649ad67da4a7a35a82840223811299e64ff35831f9f

**Affected Controls:**
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)

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

```

---

### 22. Human Agent Handoff

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0bc03a22f793dc359891b1d75d2ed29a46565542d8833b565b40733c88c2b80c

**Affected Controls:**
- Control 2.19: Control 2.19: Customer AI Disclosure and Transparency
  - File: `controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.19/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.19/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.12/verification-testing.md` (HIGH)

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

```

---

### 23. Test Your Agent

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:c633e51df27de3a06cd87d3b0d5cb0f5471fb571c4400b851fcc33a365323f3b

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

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
@@ -28,23 +28,24 @@ . Close the activity map if you want to follow through the conversation path step by step with tracking between topics turned on.
 In addition to testing your agent in the
 Test your agent
-panel, you can create test sets of multiple queries for automated testing. For more information, see
+panel, you can create test sets of multiple queries for automated testing. Learn more in
 Create test cases to evaluate your agent (preview)
 .
 Use the test chat
 Web app
-Classic
-Teams
+Teams plan
+Teams app
 Use the
 Test your agent
 panel to walk through your agent conversations as a user. It's a good way to make sure your topics are working and that conversations flow as you expect.
-In addition to testing your agent in
+In addition to testing your agent in the
 Test your agent
 panel, you can create test sets of multiple queries for
 automated testing
-. To start an automated test, select the evaluate
-button.
-Preview a conversation
+. To start an automated test, select the
+Evaluate
+icon.
+To preview a conversation:
 If the
 Test your agent
 panel is hidden, open it by selecting
@@ -64,7 +65,7 @@ to avoid having to collapse the activity map at every conversation turn.
 Continue the conversation until you're satisfied that it flows as intended.
 Tip
-You can update a topic at any time while interacting with the test agent. Save your topic to apply changes and continue the conversation with your agent.
+You can update a topic at any time while interacting with the agent. Save your topic to apply changes and continue the conversation with your agent.
 Your conversation isn't automatically cleared when you save a topic. If you want your agent to forget the test conversation and start over, select the
 Reset
 icon
@@ -79,8 +80,7 @@ on the top menu bar.
 Unless you want to continue an earlier conversation, select the
 Reset
-icon
-at the t
```

---

### 24. Data, Privacy, and Security

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-privacy
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:71e99a22b7a8a8e810f048bf45edd96e298d508988fc75308136cf29da22a0f9

**Affected Controls:**
- Control 2.23: Control 2.23: User Consent and AI Disclosure Enforcement
  - File: `controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.6/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Copy Markdown
 Print
 Note
@@ -42,10 +42,11 @@ , and
 blocking prompt injections (jailbreak attacks)
 .
-Anthropic models within Microsoft 365 Copilot experiences are provided under the Microsoft Product Terms and Data Protection Addendum.
-Learn more about Anthropic's safeguards.
-Anthropic models are out of scope for the EU Data Boundary and when available, in-country LLM processing commitments. For more information, see
-Anthropic as a subprocessor for Microsoft Online Services
+For information about models provided by Anthropic as a subprocessor within Microsoft 365 Copilot experiences, see
+Anthropic models in Microsoft Online Services
+.
+For information about models provided by OpenAI as a subprocessor within Microsoft 365 Copilot experiences, see
+OpenAI as a subprocessor in Microsoft Online Services
 .
 The information in this article is intended to help provide answers to the following questions:
 How does Microsoft 365 Copilot use your proprietary organizational data?
@@ -68,7 +69,7 @@ Microsoft 365 Copilot only surfaces organizational data to which individual users have at least view permissions. It's important that you're using the permission models available in Microsoft 365 services, such as SharePoint, to help ensure the right users or groups have the right access to the right content within your organization. This includes permissions you give to users outside your organization through inter-tenant collaboration solutions, such as
 shared channels in Microsoft Teams
 .
-When you enter prompts using Microsoft 365 Copilot, the information contained within your prompts, the data they retrieve, and the generated responses remain within the Microsoft 365 service boundary, in keeping with our current privacy, security, and compliance commitments. Microsoft 365 Copilot uses Azure OpenAI services for processing, not OpenAI's publicly available services. Azure OpenAI 
```

---

### 25. Agent 365 Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/overview
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:df26d483ad56818a7b4efd89008755b05652ff9643c67c1002b0d06d1b4045de

**Affected Controls:**
- Control 3.13: Control 3.13: Agent 365 Admin Center Analytics and Reporting
  - File: `controls/pillar-3-reporting/3.13-agent-365-admin-center-analytics.md`
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.25/portal-walkthrough.md` (CRITICAL)

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
@@ -42,7 +42,7 @@ Agent management overview
 .
 Secure
-Microsoft Agent 365 delivers endâtoâend protection for every agent by extending Microsoftâs enterpriseâgrade identity, data, and threatâdefense capabilities across your AI ecosystem. Microsoft Entra enforces consistent, riskâbased access controls for users and agents acting on their behalf, while MicrosoftPurview provides deep visibility into data risks with information protection, DLP, and risk safeguards. Microsoft Defender adds continuous threat detection and realâtime protection to block unsafe behaviors and malicious activity. Together, these capabilities ensure agents only access authorized resources, prevent data leakage, and defend against evolving threats. Learn more:
+Microsoft Agent 365 delivers endâtoâend protection for every agent by extending Microsoftâs enterpriseâgrade identity, data, and threatâdefense capabilities across your AI ecosystem. Microsoft Entra enforces consistent, riskâbased access controls for users and agents acting on their behalf, while Microsoft Purview provides deep visibility into data risks with information protection, DLP, and risk safeguards. Microsoft Defender adds continuous threat detection and realâtime protection to block unsafe behaviors and malicious activity. Together, these capabilities ensure agents only access authorized resources, prevent data leakage, and defend against evolving threats. Learn more:
 Use Microsoft Purview to manage data security and compliance
 ,
 Protect your agents in real-time during runtime

```

---

### 26. Data Loss Prevention

**URL:** https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c7cbbb2a977ce39604bb9fcfe549d03a10facc131eeb42f01ea1345b3180f8a4

**Affected Controls:**
- Control 1.25: Control 1.25: MIME Type Restrictions for File Uploads
  - File: `controls/pillar-1-security/1.25-mime-type-restrictions.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)

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

```

---

### 27. Create DLP Policies

**URL:** https://learn.microsoft.com/en-us/purview/dlp-create-deploy-policy
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:bd55515d937bfe4a49c561f59f8a681881658f0132355882e627f74ee63cbfc8

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

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
@@ -23,9 +23,9 @@ Feedback
 Summarize this article for me
 Microsoft Purview Data Loss Prevention (DLP) policies include many configuration options. Each option changes the policy's behavior. The articles in this series cover some of the most common DLP policy scenarios. They walk you through configuring those options to give you hands-on experience with the DLP policy creation process. When you familiarize yourself with these scenarios, you gain the foundational skills that you need to use the DLP policy creation UX to create your own policies.
-How you deploy a policy is as important policy design. You have
-multiple options to control policy deployment
-. This article shows you how to use these options so that the policy achieves your intent while avoiding costly business disruptions.
+How you deploy a policy is as important policy design. You have multiple options to control policy deployment, including policy state, actions, and scope, as described in the
+Deploy and manage DLP policies
+section of this article. This article shows you how to use these options so that the policy achieves your intent while avoiding costly business disruptions.
 In preview
 You can change the display name of DLP policies and rules. Once you rename a policy or a rule, any existing records retain their previous name in activity explorer evetns, in alerts and in audit records. New records will reflect the new name in activity explorer events, in alerts and in audit records. These names will remain until the items age out of the system.
 Orient yourself to DLP
@@ -95,20 +95,22 @@ Disable Microsoft Purview data loss prevention scanning for some supported files and apply controls
 Help prevent sharing Power BI reports with credit card numbers
 Policy creation scenarios for Inline web traffic
+The following scenarios show how to create DLP policies for inline web traffic
```

---

### 28. Sensitivity Labels

**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:240a866b8202dbbbd974cd8a6e613e3c260d06fb1484eae8fc09d4fb05d2b985

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.26/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.8/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)

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

```

---

### 29. Sensitivity Labels for Sites

**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels-teams-groups-sites
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f136bc0ffd732fefd6fabad2e16773e7d8359f58388e9fae0437dee1babb53c4

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)

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

```

---

### 30. Audit Log Retention

**URL:** https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:2d39c3d63ce4e252921ffdcee7f80979f22dd61acea20cd8f27e88d596cd23cd

**Affected Controls:**
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)

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
@@ -52,7 +52,7 @@ Your organization can have up to 50 audit log retention policies.
 To retain an audit log for longer than 180 days (and up to 1 year), the user who generates the audit log (by performing an audited activity) must have an Office 365 E5 or Microsoft 365 E5 license or a Microsoft Purview Suite (formerly known as Microsoft 365 E5 Compliance) or E5 eDiscovery and Audit add-on license. To retain audit logs for 10 years, the user who generates the audit log must also have a 10-year audit log retention add-on license in addition to an E5 license.
 Note
-If the user generating the audit log doesn't meet these licensing requirements, data is retained according to the highest priority retention policy. This retention might be either the default retention policy for the user's license or the highest priority policy that matches the user and its record type.
+If the user generating the audit log doesn't have the licenses required for the selected retention duration, data is retained according to the highest priority retention policy. This retention might be either the default retention policy for the user's license or the highest priority policy that matches the user and its record type.
 All custom audit log retention policies (created by your organization) take priority over the default retention policy. For example, if you create an audit log retention policy for Exchange mailbox activity that has a retention period that's shorter than one year, audit records for Exchange mailbox activities are retained for the shorter duration specified by the custom policy.
 The audit item lifetime for data is determined when you add it to the auditing pipeline and is based on the licensing defaults or applicable retention policies. Any changes to licensing or applicable retention policies change the expiration time of the audit data after updating. These 
```

---

### 31. Search the Audit Log

**URL:** https://learn.microsoft.com/en-us/purview/audit-search
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:7fd8270e1825896b8c0ef7256c88ab3c68d3d43516a76dc22b6e56e7aebd47ff

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.12: Control 3.12: Agent Governance Exception and Override Management
  - File: `controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.23/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

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
@@ -28,7 +28,7 @@ Each admin Audit account user can have up to 10 search jobs running at the same time, with a limit of one unfiltered search job.
 Before you search the audit log
 Review the following items before you start searching the audit log.
-Audit log search is turned on by default for Microsoft 365 and Office 365 enterprise organizations. To verify that audit log search is turned on, run the following command in
+Audit log search is turned on by default for Microsoft 365 and Office 365 enterprise organizations. Verify the current unified audit log ingestion setting for your organization by running the following command in
 Exchange Online PowerShell
 :
 Get-AdminAuditLogConfig | Format-List UnifiedAuditLogIngestionEnabled
@@ -79,9 +79,9 @@ Even when mailbox auditing on by default is turned on, you might notice that mailbox audit events for some users aren't found in audit log searches in the Microsoft Purview portal or via the Office 365 Management Activity API. For more information, see
 Mailbox audit logging
 .
-To turn off audit log search for your organization, run the following command in Exchange Online PowerShell:
+To turn off audit log search for your organization, use the following command to disable unified audit log ingestion in Exchange Online PowerShell:
 Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $false
-To turn on audit search again, run the following command in Exchange Online PowerShell:
+To turn unified audit log ingestion back on for your organization, run the following command in Exchange Online PowerShell:
 Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true
 For more information, see
 Turn off audit log search
@@ -95,8 +95,8 @@ .
 For information about exporting the search results returned by the
 Search-UnifiedAuditLog
-cmdlet to a CSV file, see the "Tips for exporting and viewing the audit l
```

---

### 32. Communication Compliance

**URL:** https://learn.microsoft.com/en-us/purview/communication-compliance
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a71f2e08c3a750e25447880ba3930d6bad00a282b8633600ddffcf8c65e642b4

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`
- Control 1.10: Control 1.10: Communication Compliance Monitoring
  - File: `controls/pillar-1-security/1.10-communication-compliance-monitoring.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.21/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.10/powershell-setup.md` (HIGH)

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

```

---

### 33. Create Policies

**URL:** https://learn.microsoft.com/en-us/purview/communication-compliance-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:8b0736a0af40f81fa1c8f314369356427b3419bad76971f735ca330d2640b012

**Affected Controls:**
- Control 1.10: Control 1.10: Communication Compliance Monitoring
  - File: `controls/pillar-1-security/1.10-communication-compliance-monitoring.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.10/powershell-setup.md` (HIGH)

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
@@ -25,7 +25,7 @@ Important
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
 policy is implemented for your organization when you purchase a license that includes Microsoft Purview Communication Compliance. However, this feature can take up to 30 days to become available after 
```

---

### 34. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/communication-compliance-investigate-remediate
**Section:** Microsoft Purview
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:678c43a6c96ca8bee53c08e1818304224a321c286154029c329ee1612d9382a5

**Affected Controls:**
- Control 1.10: Control 1.10: Communication Compliance Monitoring
  - File: `controls/pillar-1-security/1.10-communication-compliance-monitoring.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)

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
@@ -49,8 +49,8 @@ May 19
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
@@ -178,6 +180,7 @@ Change the time period for
```

---

### 35. Insider Risk Management

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c9852af5fa11d541277854e85b4db62edd84ddf45070d5a72134ac1eb5131d3a

**Affected Controls:**
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

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

```

---

### 36. Create Insider Risk Policies

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:fed5efaf76ebce50327cdb95ef1de729bf5e653d256b0dd21ef1efb0063d6219

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

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
@@ -241,7 +241,9 @@ Policy triggers aren't working, or policy trigger requirements aren't properly configured
 . Policy functionality might depend on other services or configuration requirements to effectively detect triggering events to activate risk score assignment to users in the policy. These dependencies might include issues with connector configuration, Microsoft Defender for Endpoint alert sharing, or data loss prevention policy configuration settings.
 Volume limits are nearing or over limits
-. Insider Risk Management policies use numerous Microsoft 365 services and endpoints to aggregate risk activity signals. Depending on the number of users in your policies, volume limits might delay identification and reporting of risk activities. Learn more about these limits in the Policy template limits section of this article.
+. Insider Risk Management policies use numerous Microsoft 365 services and endpoints to aggregate risk activity signals. Depending on the number of users in your policies, volume limits might delay identification and reporting of risk activities. Learn more about these limits in the
+Policy template limits
+section.
 To quickly view the health status for a policy, go to the
 Policy
 tab and check the
@@ -359,7 +361,9 @@ Check that your HR connector is configured correctly and sending data, or come back and check the policy status.
 You're approaching the maximum limit of users being actively scored for this policy template
 All policy templates
-Each policy template has a maximum number of included users. See the template limit section details.
+Each policy template has a maximum number of included users. See the
+Policy template limits
+section for details.
 Review the users in the Users tab and remove any users who don't need to be scored anymore.
 Your organization doesn't have a Microsoft Defender for Endpoint subscripti
```

---

### 37. Insider Risk Indicators

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-settings-policy-indicators
**Section:** Microsoft Purview
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:c2aa0eb858c9d64c12173e89b8f290f8fd9baf30a21ad96549ad3f8751fa93cb

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

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
@@ -52,6 +52,7 @@ Data leaks by priority users
 templates, you get more flexibility and customization for your policies and when users are in-scope for a policy. You can also define risk management activity thresholds for these triggering indicators for more fine-grained control in a policy.
 Define the insider risk policy indicators that are enabled in all insider risk policies
+To enable policy indicators for all insider risk policies, complete the following steps:
 Select
 Settings
 , then select
@@ -68,7 +69,8 @@ Users dashboard
 and open the
 User activity
-tab in the details pane.## Two types of policy indicators: built-in indicators and custom indicators
+tab in the details pane.
+Two types of policy indicators: built-in indicators and custom indicators
 Indicators and pay-as-you-go billing
 Some indicators included in Insider Risk Management require that you enable the
 pay-as-you-go billing model
@@ -81,7 +83,7 @@ : Use custom indicators together with the
 Insider Risk Indicators (preview) connector
 to bring non-Microsoft detections to Insider Risk Management. For example, you might want to extend your detections to include Salesforce and Dropbox and use them alongside the built-in detections provided by the Insider Risk Management solution, which is focused on Microsoft workloads (SharePoint Online and Exchange Online, for example).
-Learn more about creating a custom indicator
+Create a custom indicator
 Built-in indicators
 Insider Risk Management includes the following built-in indicators.
 Office indicators
@@ -94,9 +96,9 @@ These indicators include policy indicators for Google Drive, Box, and Dropbox that you can use to detect techniques used to determine the environment, gather and steal data, and disrupt the availability or compromise the integrity of a system. To select from
 cloud storage indicators
 , you must
-first connect to 
```

---

### 38. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-activities
**Section:** Microsoft Purview
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:3a2535ed2df38e7d52bae8ae4a0d80b96ca125117e0db7c04291481ffdc23295

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

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
@@ -37,7 +37,7 @@ Investigate and act on alerts in Insider Risk Management by following these steps:
 Review the dashboards for alerts
 . On the Standard dashboard,
-filter
+filter alerts
 by alert
 Status
 to locate
@@ -49,7 +49,7 @@ filter to view alerts with the highest prioritization.
 Start with the alerts with the highest severity
 .
-Filter
+Filter alerts
 by alert
 Severity
 if needed to help locate these types of alerts.
@@ -70,14 +70,16 @@ is available for the content within the alert, you can review relevant files from SharePoint, Exchange, and OneDrive for Business in Activity explorer to identify false positives, confirm that sensitive data is present, and quickly decide whether the alert warrants escalation.
 Act on the alert
 . You can either confirm and
-create a case
-for the alert or dismiss and resolve the alert.
+create a case for an alert
+or dismiss and resolve the alert.
 You can triage alerts by going to the
 Alert details
 page for an alert in either dashboard. On the
 Alert details
 page, you can review information about the alert. You can confirm the alert and create a new case, confirm the alert and add to an existing case, or dismiss the alert.
-This page also includes the current status for the alert and the alert risk severity level, listed as
+The
+Alert details
+page also includes the current status for the alert and the alert risk severity level, listed as
 High
 ,
 Medium
@@ -107,7 +109,75 @@ You can also use the
 standalone version of Microsoft Security Copilot to investigate Insider Risk Management, Microsoft Purview Data Loss Prevention (DLP), and Microsoft Defender XDR alerts
 .
-Spotlight (preview)
+Alerts (preview)
+The new unified alert experience combines the Triage Agent and classic alert dashboards into a single alerts list page. This unified view lets you manage both classic and agent-triaged alerts from
```

---

### 39. HR Data Connector

**URL:** https://learn.microsoft.com/en-us/purview/import-hr-data
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8db12e9dfebabc5f094c8ae99411f955903f3dc3db12af54a7d82fc17072edc8

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

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

```

---

### 40. Data Retention

**URL:** https://learn.microsoft.com/en-us/purview/retention
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:aaefb527bce6c1df62cc41941418696e90a03af63fadf44232cf91d4c84bd4a6

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.21/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.13/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.9/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.9/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-1-minimal-viable-controls.md` (HIGH)

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

```

---

### 41. Information Barriers

**URL:** https://learn.microsoft.com/en-us/purview/information-barriers
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:147212adc4393f13e6dad360984772926ab3696b56a973316ad352f08e53c470

**Affected Controls:**
- Control 1.22: Control 1.22: Information Barriers for AI Agents
  - File: `controls/pillar-1-security/1.22-information-barriers.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.22/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.22/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-2-hardening.md` (HIGH)

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

```

---

### 42. Access Reviews

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview
**Section:** Microsoft Entra ID
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a440d9298cfbd378bb91c908979fe4d57d6e31ee880eaf99fbb314e541643b98

**Affected Controls:**
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.12/portal-walkthrough.md` (CRITICAL)

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

```

---

### 43. Privileged Identity Management

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure
**Section:** Microsoft Entra ID
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:631968768c37ee95de28691a4540d3d2349a924c28ec0f7cb3434be15b4fd671

**Affected Controls:**
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/3.3/portal-walkthrough.md` (CRITICAL)

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

```

---

### 44. Data Access Governance Reports

**URL:** https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports
**Section:** SharePoint Administration
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:56ec7f06167f5a83efbdadf9a5dce0e5a6bec0f729a02a6382577bb3111f5600

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.2/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/sharepoint-copilot-preflight/index.md` (HIGH)

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
@@ -27,7 +27,7 @@ See
 Prerequisites for SharePoint Advanced Management
 .
-The reports are currently unavailable for Gallatin, even if you have the required licenses.
+The reports are currently unavailable for Microsoft 365 operated by 21Vianet, even if you have the required licenses.
 How to access the Data access governance reports in the SharePoint admin center
 Sign in to the
 SharePoint admin center

```

---

### 45. Immutable Blob Storage

**URL:** https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview
**Section:** Azure Services
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:eebc3f88c42731c123eb6c091fb81d23273f0e43c8ec997a169a418ef01a6819

**Affected Controls:**
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.7/powershell-setup.md` (HIGH)

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

```

---

### 46. AI Content Safety

**URL:** https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
**Section:** Azure Services
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ec279db1d342f5c2ff28d52e162f7927b3f1431869bb14430518d7ffc54f0aa2

**Affected Controls:**
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

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

```

---

### 47. Approval Workflows

**URL:** https://learn.microsoft.com/en-us/power-automate/get-started-approvals
**Section:** Power Automate
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:4c1d1c5b8cffc2680fe28745f82ad55d0047cf828db79a3385c6df0e87484ee6

**Affected Controls:**
- Control 3.12: Control 3.12: Agent Governance Exception and Override Management
  - File: `controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 2.16: Control 2.16: RAG Source Integrity Validation
  - File: `controls/pillar-2-management/2.16-rag-source-integrity-validation.md`
- Control 2.21: Control 2.21: AI Marketing Claims and Substantiation
  - File: `controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/3.3/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.12/portal-walkthrough.md` (CRITICAL)

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

```

---

### 48. M365 Licensing Guidance

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-365-security-compliance-licensing-guidance
**Section:** Licensing
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2ad16c68adb19cbe6cc3c8496ba63d0f37070152a24ec962d2aef721f249f950

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.21/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/1.13/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/1.19/portal-walkthrough.md` (CRITICAL)

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

```

---

## HIGH: Control Review Recommended

### 1. Enable Managed Environments

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-enable
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:7c85b3171563fee3408403d73946436835b6bbb80f487f37cc80ad7031003287

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
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -19,20 +19,20 @@ Access to this page requires authorization. You can try
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
-The Managed Environments property must be the same in the source and destination before yo
```

---

### 2. Usage Insights

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-usage-insights
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:cea22c8fc12fe5cfe1cfda3b5190108eb3a3e8658045fceb7cd6965c392a22da

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 2.1: Control 2.1: Managed Environments
  - File: `controls/pillar-2-management/2.1-managed-environments.md`

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
@@ -60,7 +60,7 @@ Include insights for this environment in the weekly email digest
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
**Content-Hash:** sha256:ed6df2ce6096865c64fef988e55b562ac6f5441d737bbdf37de4142ee952a0d5

**Affected Controls:**
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

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
@@ -37,11 +37,11 @@ , the maker lands in their own personal developer environment instead of the default environment. Personal developer environments are the makers' own spaces, like OneDrive, for personal productivity where they can start building apps and solutions in their own workspace. Makers don't need to know which environment to work in, since the personal developer environment appears automatically.
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
-All routed environments are Managed Environments, meaning they inherit standardized policies like data retenti
```

---

### 4. Connector Reference

**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:fd6200659a500a593a12bac8eadd145c7902daeedaf349419bf9976e48c34404

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

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
@@ -108,8 +108,6 @@ By: Adobe
 Adobe PDF Services
 By: Adobe Acrobat Services
-ADP Employee Self-Service
-By: ADP, Inc.
 Advanced Data Operations
 By: State Solutions
 Advanced Scraper (Independent Publisher)
@@ -126,6 +124,8 @@ By: Africa's Talking
 AfterShip (Independent Publisher)
 By: Taiki Yoshida
+Agent SDK
+By: Microsoft
 AgilePoint NX
 By: AgilePoint Inc
 Agilite
@@ -177,11 +177,11 @@ Amazon Redshift [DEPRECATED]
 By: Microsoft
 Amazon S3
-By: Microsoft
+By:
 Amazon S3 Bucket (Independent Publisher)
 By: Michael Megel
 Amazon SQS
-By: Microsoft
+By:
 Ambee (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 AMEE Open Business (Independent Publisher)
@@ -270,8 +270,6 @@ By: Microsoft
 Azure - Foundry IQ
 By: Microsoft
-Azure AD Identity and Access
-By: Microsoft, Daniel Laskewitz
 Azure AI Content Understanding
 By: Microsoft
 Azure AI Document Intelligence (form recognizer)
@@ -283,7 +281,7 @@ Azure AI Search
 By: Microsoft
 Azure App Service
-By: Microsoft
+By:
 Azure Application Insights [DEPRECATED]
 By: Microsoft
 Azure Automation
@@ -340,6 +338,8 @@ By: Microsoft
 Azure Log Analytics Data Collector
 By: Microsoft
+Azure Maps
+By: Microsoft
 Azure Monitor Logs
 By: Microsoft
 Azure OpenAI
@@ -357,7 +357,7 @@ Azure Text to speech
 By: Microsoft
 Azure VM
-By: Microsoft
+By:
 Badgr (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions
 Basecamp 2
@@ -548,6 +548,8 @@ By: Cireson
 Cisco Webex Meetings
 By: Cisco
+Cisco Workspaces
+By: Cisco Systems.
 Citymapper (Independent Publisher)
 By: Troy Taylor
 CivicPlus Transform
@@ -626,6 +628,8 @@ By: Roy Paar
 Commercient
 By: Commercient LLC
+CommunitycliQ Agent
+By: Mentorcliq, Inc.
 Companies House (Independent Publisher)
 By: Matt Collins
 Company Connect
@@ -665,7 +669,7 @@ ConvertKit (Independent Publisher)
 By: Troy Taylor, Hitachi Solutions

```

---

### 5. Security

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:eb30b3829c9a321481e00ec3be2943e3b8cb4057c97c3010abdcd42bfe08a1e5

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
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -81,7 +81,7 @@ Overview
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
@@ -158,7 +158,7 @@ The system generates various recommendation
```

---

### 6. Power Platform Inventory

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:142fc366376635213106a1a7d4b9cd95e6cf035b4881f4700dbc499109aea988

**Affected Controls:**
- Control 3.11: Control 3.11: Centralized Agent Inventory Enforcement
  - File: `controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md`

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
@@ -39,7 +39,7 @@ needle in a haystack
 resource referenced in a support ticket to dramatically improve response times.
 Supported resource types
-The Power Platform inventory includes:
+The Power Platform inventory includes the following resource types:
 Agents:
 All agents created in Copilot Studio, and all agents created in Microsoft 365 Copilot Agent Builder.
 Apps:
@@ -51,6 +51,7 @@ Environment groups:
 All environment groups in your tenant.
 Key features
+The Power Platform inventory includes the following key features:
 Unified inventory
 : Centralized view of all resources.
 Fast updates
@@ -66,11 +67,36 @@ Connector visibility (preview)
 : See which connectors and operations each resource uses, directly in the inventory grid.
 Access requirements
-To view the Power Platform inventory, you must have one of the following tenant-wide administrative roles:
+To view the Power Platform inventory, you must hold one of the supported Microsoft Entra roles. What you can see in the Power Platform admin center depends on your role: most roles have full visibility into all resources, while the AI roles are scoped to AI-related resources only.
+Role
+What they can see
+Global administrator
+All inventory resources
 Power Platform administrator
-or
+All inventory resources
 Dynamics 365 administrator
-. If you don't have one of these roles, you can't access the inventory.
+All inventory resources
+Global reader
+All inventory resources
+AI administrator
+Agents, agentic apps, agent flows, environments, and environment groups only
+AI reader
+Agents, agentic apps, agent flows, environments, and environment groups only
+The AI administrator and AI reader roles are scoped to AI-related resources only. They can see:
+Agents
+from Microsoft 365 Copilot and Copilot Studio
+Agentic apps
+, including vibe apps, code apps, and App Builder apps
+Agent flows
+from C
```

---

### 7. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:4b33bef0120b1e552bc99a4d11b45c3ca57a1bf6109d23bd0b7bf2f475bd7171

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
@@ -34,14 +34,14 @@ Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. You can place alert rules on an environment and a specific resource.
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
+if the resource is in a managed environ
```

---

### 8. Copilot Hub

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub
**Section:** Power Platform Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6f20aac4f3ce2316a5eafa8e0d52a9bc6f6eee004e9db6ad38d3539a7c7000f3

**Affected Controls:**
- Control 3.1: Control 3.1: Agent Inventory and Metadata Management
  - File: `controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)

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
@@ -56,7 +56,7 @@ Tenant users with environment access can view Copilot settings.
 Control who can use AI features in model-driven apps
 Admins can define who within an environment can use Copilot capabilities in model-driven appsâeither by explicitly allowing specific users or allowing all users except a defined exclusion list. This capability is currently in preview and is only for environments activated for
-Managed Environments
+managed environments
 , with a subset of Copilot features adhering to it. Review the following table to learn which capabilities adhere to this configuration.
 Product
 Feature

```

---

### 9. Environment Strategy

**URL:** https://learn.microsoft.com/en-us/power-platform/guidance/adoption/environment-strategy
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:88b099113d253e19bb9899809f89c9062e90616ac0e7a1e65d4282f2e1601b79

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

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
@@ -34,7 +34,7 @@ . These resources often use only the basic capabilities included with Microsoft 365 and don't use the full capabilities of Power Platform. As this initial adoption accelerates, Microsoft provides organizations with an on-ramp to an environment strategy for enterprise scale adoption of the full Power Platform capabilities. These premium governance capabilities become available when users have a premium Power Platform (Power Apps, Power Automate, Microsoft Copilot Studio, and Dynamics 365) license. The
 Power Platform adoption maturity model
 provides more insights to help organizations define their roadmap to achieve enterprise scale adoption beyond their environment strategy. This approach can help organizations mature from basic personal productivity to enterprise-scale adoption of Power Platform.
-Power Platform administrative, governance, and security features allow organizations to adopt and manage Power Platform for enterprise productivity and enterprise app usage at scale. Using Managed Environments activates a set of premium capabilities that enable greater visibility and control and reduce the manual effort to administer and secure environments. Using these capabilities, you can ensure consistent application of your governance and security policies. Admins can transition into an enterprise-scale, environment strategy using these capabilities. Spending less time and effort on the administration helps reduce the overall total cost of ownership (TCO) of the platform as your organization scales usage.
+Power Platform administrative, governance, and security features allow organizations to adopt and manage Power Platform for enterprise productivity and enterprise app usage at scale. Using managed environments activates a set of premium capabilities that enable greater visibility and control and reduce the manual effort to admini
```

---

### 10. Release Plans

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:0b31635446652401c0c2b840109b3f559f374d8caba1a89f4488765d40485af7

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
@@ -40,13 +40,8 @@ and a downloadable
 PDF
 .
-The role-based Copilot offerings features coming in the 2025 release wave 2 have been summarized in a separate
-release plan
-as well as a downloadable
-PDF
-.
 2025 release wave 2 overview
-Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. Microsoft Power Platform today is comprised of: Power Apps, Power Pages, Power Automate, Microsoft Copilot Studio, Microsoft Dataverse and Microsoft Power Platform governance and administration. The 2025 release wave 2 contains hundreds of new features across Power Platform applications, including Power Apps, Power Pages, Power Automate, and Microsoft Copilot Studio, as well as Microsoft Dataverse and Power Platform capabilities for governance and administration.
+Microsoft Power Platform enables users and organizations to analyze, act on, and automate data to digitally transform their businesses. Microsoft Power Platform today is comprised of: Power Apps, Power Pages, Power Automate, Microsoft Copilot Studio, Microsoft Dataverse and Microsoft Power Platform governance and administration. The 2025 release wave 2 contains hundreds of new features across Power Platform applications, including Power Apps, Power Pages, and Power Automate, as well as Microsoft Dataverse and Power Platform capabilities for governance and administration.
 Power Apps
 Power Apps
 enables human and agent collaboration. They include an agent feed to supervise the work of agents and extensible built-in agents for common tasks like entering, exploring, visualizing, and summarizing data. Bring business problems to Plan Designer and a team of agents will help you build enterprise solutions that include apps, agents, Power BI reports and more. Vibe-code with the App Agent to create data-connected experiences. Just
```

---

### 11. Release Plans (2026 Wave 1)

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:00aaaba18d5b964f6ecece529974195f9fce77efba878c56ef4255f7fc4b96fb

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
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
@@ -40,13 +40,8 @@ and a downloadable
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
 continues to modernize app experiences with a refreshed model-driven UI, improved mobile and offline capabilities, faster search, and expanded AI features. This release brings standardized modern theming to everyone, real-time Dataverse access for offline-first Canvas apps, enhanced search in grids and lookups, and broader availability and extensibility of generative pages to help teams build and scale intelligent apps faster.
@@ -56,9 +51,6 @@ Power Automate
 Power Automate
 is Microsoft's comprehensive automation platform for cloud flows, desktop flows, and process mining. This release introduces AI agent authoring, optimization, and self-healing capabilities for desktop flows, Copilot Studio-powered actions in cloud flows, enhanced maker and collaboration tools across both, general availability of object-centri
```

---

### 12. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:76a8dd9795a82356674d930c16bd452fdff690778bed1076b4674e24a483bb5a

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

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
@@ -35,13 +35,26 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+June 2026
+(Production-ready preview) Use the
+new agent experience
+in Copilot Studio to build agents. The new experience uses an enhanced orchestration runtime for improved response quality and reasoning, available alongside the classic experience.
+Use
+Microsoft IQ
+in the new agent experience to connect your agent to organizational data, giving it access to emails, calendar events, files, Teams messages, and people information.
+Build and reuse
+skills
+in the new agent experience to extend your agent's capabilities with modular, self-contained sets of instructions. Create a skill once, add it to multiple agents, and export it as a Markdown file or package to share with others.
+Turn on
+memory
+in the new agent experience to give your agent persistent context across interactions. It captures user preferences and patterns, stores them per user, and applies them to deliver more relevant and personalized responses over time.
 May 2026
 (General availability)
 Computer use
 is now generally available, letting your agents automate web and desktop apps by controlling browsers and desktop applications on behalf of users.
 Add a
 prompt node
-to an agent flow or workflow to make a single AI call with dynamic content and model selection, useful for scenarios like translation and structured data extraction.
+to an agent flow to make a single AI call with dynamic content and model selection, useful for scenarios like translation and structured data extraction.
 Add a
 Microsoft 365 Copilot node
 to a workflow to send prompts to Microsoft 365 Copilot or a specific agent, enabling automation scenarios like research and audit
```

---

### 13. Create Custom MCP Server

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:80b86de980dc87f5e3433b0a3518b230ca01ac7d3cbfa3d0179e475643a25b6b

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

```

---

### 14. Copilot Studio Kit — Compliance Hub

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:bdef90cb8e0c95ef4aba436c0aaecb717cd1dd62c5209c30e0e599f25bce6e4f

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
@@ -27,6 +27,12 @@ New articles
 Measure the return on investment (ROI) and business value of AI agents
 Plan Copilot Studio agent deployments for throughput and rate limits
+Other updates
+New real-world case studies, on how
+Grupo Bimbo standardizes global audit processes with Copilot Studio
+and on how
+Copilot Agent Kit helps organizations improve visibility, monitor performance, and refine their agents
+.
 May 2026
 Architecting agent solutions
 moved to the

```

---

### 15. Copilot Usage Reports

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0bcd10b9779d7753b859773001f1d369d18af0d505601ba41c793fdc5ebf5a85

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)

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

```

---

### 16. Agent 365 SDK and CLI

**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/developer/
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c0d8868bca505a8ef1b3f0c236850afccbfa36d5808577bf7448098761bf30d5

**Affected Controls:**
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/opentelemetry-setup.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/index.md` (HIGH)

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

```

---

### 17. Agent 365 Overview Page (M365 Admin)

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8bf9d4caf0a16a09cce6d98bdaee378f9b96dcbd96dcf0a09d4eef817334d7cd

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.25/powershell-setup.md` (HIGH)

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

```

---

### 18. Human-in-the-Loop Workflows

**URL:** https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:9f4cccc5d8b421e4446d3a4e6871c26f77a7509f523af92560e2f9350101053e

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

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
@@ -144,6 +144,30 @@ and
 response
 parameters.
+Workflows support human-in-the-loop patterns through
+RequestPort
+, which pauses execution and waits for external input.
+approvalPort := workflow.RequestPort{
+ ID: "ApprovalPort",
+ Request: reflect.TypeFor[string](),
+ Response: reflect.TypeFor[bool](),
+}
+
+approval := approvalPort.Bind()
+finalize := workflow.NewExecutor("FinalizeExecutor", func(approved bool) string {
+ if approved {
+ return "Request approved by the human reviewer"
+ }
+ return "Request rejected by the human reviewer"
+}).Bind()
+
+wf, err := workflow.NewBuilder(approval).
+ AddEdge(approval, finalize).
+ WithOutputFrom(finalize).
+ Build()
+A
+RequestPort
+defines a typed request/response channel between the workflow and the outside world. When an executor reaches a request port, the workflow pauses and emits an external request event. The workflow resumes when an external response is provided.
 Handling Requests and Responses
 An
 RequestPort
@@ -215,6 +239,40 @@ See this
 full sample
 for a complete runnable file.
+Listen for
+workflow.RequestInfoEvent
+, create a response from the request, and resume the run with that response:
+run, err := inproc.Default.Run(ctx, wf, "Approve deployment to production?")
+if err != nil {
+ return err
+}
+
+var request *workflow.ExternalRequest
+for evt := range run.NewEvents() {
+ if requestEvent, ok := evt.(workflow.RequestInfoEvent); ok {
+ request = requestEvent.Request
+ break
+ }
+}
+
+response, err := request.CreateResponse(true)
+if err != nil {
+ return err
+}
+
+if _, err := run.Resume(ctx, response); err != nil {
+ return err
+}
+
+for evt := range run.NewEvents() {
+ if output, ok := evt.(workflow.OutputEvent); ok {
+ fmt.Println(output.Output)
+ }
+}
+Tip
+See the
+human-in-the-loop sample
+for a complete runnable file.
 Human-in-the-Loop with Agent Orchestrations
 The
 Reques
```

---

### 19. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:f791bb8b8aa510bfd7361565e91b01b3721697a979c0fda0e39277881fcfb4df

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

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
@@ -917,7 +917,7 @@ -
 Get started with Endpoint data loss prevention
 -
-Configure device proxy and internet connection settings for Information Protection
+Configure device proxy and internet connection settings for Microsoft Purview Endpoint DLP
 On-premises repositories (file shares and SharePoint)
 No
 Repository
@@ -925,7 +925,7 @@ -
 Learn about the data loss prevention on-premises repositories
 -
-Get started with the data loss prevention on-premises repositories
+Get started with data loss prevention for on-premises repositories
 Fabric and Power BI
 No
 Workspaces

```

---

### 20. Audit Logging

**URL:** https://learn.microsoft.com/en-us/purview/audit-solutions-overview
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:d4dcfb2812a9ec72a1dfcace223b83454ae7da597f7877e6f73eca60e75e3ea7

**Affected Controls:**
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)

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
@@ -92,7 +92,7 @@ Longer retention of audit records
 . Microsoft Entra ID, Exchange, OneDrive, and SharePoint audit records are retained for one year by default. Audit records for all other activities are retained for 180 days by default, or you can use audit log retention policies to configure longer retention periods.
 Audit (Premium) intelligent insights
-. Audit records for intelligent insights can help your organization conduct forensic and compliance investigations by providing visibility to events such as when mail items were accessed, or when mail items were replied to and forwarded, or when and what a user searched for in Exchange Online and SharePoint Online. These intelligent insights can help you investigate possible breaches and determine the scope of compromise.
+. Audit records for intelligent insights can help your organization conduct forensic and compliance investigations by providing visibility to insights such as the sensitivity label of mail items which were accessed, or when and what a user searched for in Exchange Online and SharePoint Online. These intelligent insights can help you investigate possible breaches and determine the scope of compromise more precisely.
 Higher bandwidth to the Office 365 Management Activity API
 . Audit (Premium) provides organizations with more bandwidth to access auditing logs through the Office 365 Management Activity API. Although all organizations (that have Audit (Standard) or Audit (Premium)) initially receive a baseline of 2,000 requests per minute, this limit dynamically increases depending on an organization's seat count and their licensing subscription. This change results in organizations with Audit (Premium) getting about twice the bandwidth as organizations with Audit (Standard).
 Long-term retention of audit logs

```

---

### 21. Audit Copilot Activities

**URL:** https://learn.microsoft.com/en-us/purview/audit-copilot
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:93d155d38a7f71845c945314abe23fdfd66385a9a07f1129095b0df8f5e1b700

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/troubleshooting.md` (HIGH)
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

```

---

### 22. DSPM for AI

**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e2bfad0a4236f04b93f6737dabc796ca0454599005aa3ec4f5e4647a911df14e

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

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

```

---

### 23. Sensitive Information Types

**URL:** https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-learn-about
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a2ac8a6df00473b1720bda2469be035bdb672c54ecf6f6ace30af1740d0bb9db

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

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

```

---

### 24. Custom SITs

**URL:** https://learn.microsoft.com/en-us/purview/sit-create-a-custom-sensitive-information-type
**Section:** Microsoft Purview
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:ff8b0a9d58b945940d7a6b88db35bba15bd99d2ed3f2c33b99b9713969b21d67

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

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
@@ -96,11 +96,36 @@ Sensitive Information Type regular expression validators
 .
 Important
-Don't use positional regex anchors, like
+Custom SIT regex patterns must follow these rules:
+Don't use positional anchors
+like
 ^
 and
 $
-in custom SITs as the SIT is unlikely to behave as intended when these anchors are part of the regular expression. If they are used, when the content is scanned there are no guarantees about where in the content will correspond to the starting and ending anchors.
+. When content is scanned, there are no guarantees about where in the content the starting and ending anchors correspond to.
+Use
+one primary capturing group
+(the only capturing group), for example:
+(?:prefix)(primary capturing group)(?:suffix)
+(use noncapturing groups for any additional grouping).
+Handle all match variants
+inside
+that single group using
+|
+(alternation). Multiple capturing groups separated by
+|
+at the top level are
+not supported
+and are blocked during validation.
+Invalid pattern
+(three top-level capturing groups):
+(?:[\s,;])([A-Z]{2}[0-9]{3})(?:[\s,;])|(?:[\s,;])([A-Z]{2}[A-Z]{4}[0-9])(?:[\s,;])|(?:[\s,;])([A-Z]{2}[0-9]{5})(?:[\s,;])
+Valid pattern
+(single capturing group with alternation):
+(?:[\s,;])([A-Z]{2}[0-9]{3}|[A-Z]{2}[A-Z]{4}[0-9]|[A-Z]{2}[0-9]{5})(?:[\s,;])
+For more information on limits, see
+Sensitive information type limits
+.
 Fill in a value for
 Character proximity
 .
@@ -108,7 +133,7 @@ Character proximity
 configuration.
 (Optional) Add any
-additional checks
+sensitive information type additional checks
 from the list of available checks.
 Choose
 Create
@@ -207,7 +232,7 @@ (Optional) If you have
 Supporting elements
 or any
-additional checks
+sensitive information type additional checks
 you want to run, add them. If needed, you can organize your
 Supporting elements
 into groups.

```

---

### 25. Keyword Dictionaries

**URL:** https://learn.microsoft.com/en-us/purview/sit-create-a-keyword-dictionary
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:207f60950a60bb3bb85191d36c5da5573571e9ad98247be9cb785f6ff5eeb5b9

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

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
@@ -25,13 +25,13 @@ Microsoft Purview can identify, monitor, and protect your sensitive items. Identifying sensitive items sometimes requires looking for keywords, particularly when identifying generic content (such as healthcare-related communication), or inappropriate or explicit language. Although you can create keyword lists when you
 create custom sensitive information types
 , keyword lists are limited in size and if you're
-creating them in PowerShell
+creating custom sensitive information types in PowerShell
 , require modifying XML to create or edit them.
 In contrast, keyword dictionaries provide simpler management of keywords and at a larger scale, supporting up to 1 MB of terms (post-compression) in the dictionary. Additionally, keyword dictionaries can support any language. The tenant limit is also 1 MB after compression. A post-compression limit of 1 MB means that all dictionaries combined across a tenant can have close to one million characters.
 Keyword dictionary limits
-You can create keyword dictionary, subject to a combined size limit of 1MB (post compression) per tenant. To find out how many keyword dictionaries you have in your tenant, follow the procedures in
-Connect to the Security & Compliance PowerShell
-to connect to your tenant and then run this PowerShell script:
+You can create keyword dictionary, subject to a combined size limit of 1MB (post compression) per tenant. To find out how many keyword dictionaries you have in your tenant,
+connect to Security & Compliance PowerShell
+and then run this PowerShell script:
 $rawFile = $env:TEMP + "\rule.xml"
 
 $kd = Get-DlpKeywordDictionary
@@ -66,9 +66,7 @@ 
 Remove-Item $rawFile
 Basic steps to creating a keyword dictionary
-Most commonly you compile your keywords for your dictionary in a file, such as a .csv or .txt list. You upload the dictionary file into a SIT during cre
```

---

### 26. Exact Data Match

**URL:** https://learn.microsoft.com/en-us/purview/sit-learn-about-exact-data-match-based-sits
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ee7dad5ed86dbe40d55c1ae7fc770c68b8f933eeee4d0397611388f9d008a74f

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

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

```

---

### 27. Trainable Classifiers

**URL:** https://learn.microsoft.com/en-us/purview/trainable-classifiers-learn-about
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fdecf428e41e22fb7c73a3c7bc760b99347da1fbe6276470c9c44682a0c2a109

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

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

```

---

### 28. Retention Policies

**URL:** https://learn.microsoft.com/en-us/purview/create-retention-policies
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ea457d8405267250b1824faee1abd838257eccd75ee02a0d6e175640d8b18d28

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.9/powershell-setup.md` (HIGH)

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

```

---

### 29. Retention Labels

**URL:** https://learn.microsoft.com/en-us/purview/create-retention-labels-data-lifecycle-management
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:b1263f020679542be59ddcd126127207465a8bc8b49338833e9cbd9fd1ccb114

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`

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
@@ -60,6 +60,8 @@ Select
 Create a label
 and follow the prompts to create the retention label. Be careful what name you choose, because this can't be changed after the label is saved.
+Note
+Double quotation marks ("") aren't supported in retention label names. For example, ""Permanent Label"" isn't supported.
 For more information about the retention settings, see
 Settings for retaining and deleting content
 .

```

---

### 30. Retention for SharePoint

**URL:** https://learn.microsoft.com/en-us/purview/retention-policies-sharepoint
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b8baf750cbde30ee9bbbeff2b1ee0dfe0879f9f5ef1a11ceb9e87ede752aa0d7

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

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

```

---

### 31. Disposition

**URL:** https://learn.microsoft.com/en-us/purview/disposition
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:54b9f79d5fc85f336611297e49aa8fb6f2a815d9c7b96a8c5f06e791ace09eab

**Affected Controls:**
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

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

```

---

### 32. SEC 17a-4 / Preservation Lock

**URL:** https://learn.microsoft.com/en-us/purview/retention-regulatory-requirements
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:767689dee9673a50f41d0d4f603f9aca28d12d9b60d844d954898bd4c31844e3

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.9/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

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

```

---

### 33. Records Management

**URL:** https://learn.microsoft.com/en-us/purview/records-management
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:05b1262f0f8017a925180bd7a3bf5c57accaecf7357905ea8a778be3cd607c12

**Affected Controls:**
- Control 3.3: Control 3.3: Compliance and Regulatory Reporting
  - File: `controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md`
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

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

```

---

### 34. Endpoint DLP

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:36c588027f3a6987f95cdfce270f94d118df03707a41d2472961b03f1cb5c3a8

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

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
@@ -42,13 +42,7 @@ Note
 Endpoint DLP cannot detect the sensitivity label from another tenant on a document.
 Endpoint DLP Windows 10/11 and macOS support
-Endpoint DLP allows you to onboard devices running the following versions of Windows Server:
-Windows Server 2019 (
-November 14, 2023âKB5032196 (OS Build 17763.5122) - Microsoft Support
-)
-Windows Server 2022 (
-November 14, 2023 Security update (KB5032198) - Microsoft Support
-)
+Endpoint DLP allows you to onboard devices running Windows Server 2019 and later versions.
 Note
 Installing the supported Windows Server KBs disables the
 Classification
@@ -59,7 +53,7 @@ Once properly configured, the same data loss protection policies can be automatically applied to both Windows PCs and Windows servers.
 Setting
 Subsetting
-Windows 10, 1809 and later, Windows 11, Windows Server 2019, Windows Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows 10, 1809 and later, Windows 11, Windows Server 2019 and later versions for Endpoints (X64)
 macOS (three latest released versions)
 Notes
 Advanced classification scanning and protection
@@ -168,7 +162,7 @@ Other settings
 Setting
 Windows 10/11, Windows 10, 1809 and later, Windows 11
-Windows Server 2019, Windows Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows Server 2019 and later versions for Endpoints (X64)
 macOS (three latest released versions)
 Archive file
 Supported
@@ -188,7 +182,7 @@ Endpoint DLP enables you to audit and manage the following types of activities users take on sensitive items that are physically stored Windows 10, Windows 11, or macOS devices.
 Activity
 Description
-Windows 10 (21H2, 22H2), Windows 11 (21H2, 22H2), Windows Server 2019, Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows 10 (21H2, 22H2), Windows 11 (21H2, 22H2), Windows Server 2019 and later versions for Endpoints (X64)
 Windows 11 (21H2, 22H2) for E
```

---

### 35. Onboard Devices

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-getting-started
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:a9edceb99d2f11658e45b8f7ff250318ccd61f51341e9c9de3e57662392a91c9

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

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
@@ -46,7 +46,7 @@ , ensure those users or devices or both are explicitly excluded from the policy. Failure to do so may lead to unintended policy enforcement behavior.
 Configure proxy on the Windows 10 or Windows 11 device
 If you're onboarding Windows 10 or Windows 11 devices, check to make sure that the device can communicate with the cloud DLP service. For more information, see,
-Configure device proxy and internet connection settings for Information Protection
+Configure device proxy and internet connection settings for Microsoft Purview Endpoint DLP
 .
 Windows 10 and Windows 11 Onboarding procedures
 For a general introduction to onboarding Windows devices, see:

```

---

### 36. Configure Settings

**URL:** https://learn.microsoft.com/en-us/purview/dlp-configure-endpoint-settings
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:937ba4d51522fd00e18f9dd546b358b6b3be898cbc2689d6d030b10d466e9776

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

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
@@ -47,7 +47,7 @@ Microsoft Purview Information Protection Support in Acrobat
 .
 Advanced classification scanning and protection
-When you turn on advanced classification scanning and protection, the Microsoft Purview cloud-based data classification service scans items, classifies them, and returns the results to the local machine. Therefore, you can take advantage of classification techniques such as
+When you turn on advanced classification scanning and protection, the Microsoft Purview cloud-based data classification service scans items, classifies them, and returns the results to the local machine. Because advanced classification runs in the cloud, you can take advantage of classification techniques such as
 exact data match
 classification,
 trainable classifiers
@@ -85,15 +85,15 @@ Tip
 To use advanced classification for Windows 10 devices, you must install KB5016688. To use advanced classification for Windows 11 devices, you must install KB5016691 on those Windows 11 devices. Additionally, you must enable advanced classification before
 Activity explorer
-displays contextual text for DLP rule-matched events. To learn more about contextual text, see
-Contextual summary
+displays contextual text for DLP rule-matched events. To learn more about contextual text, see the "Contextual summary" section in
+Learn about data loss prevention
 .
 Advanced label-based protection for all files on devices
-When you turn on this feature, users can work on files - including files other than Office and PDF files - that have sensitivity labels applying access control settings in an unencrypted state, on their devices. Endpoint DLP continues to monitor and enforce access control and label-based protections on these files even in an unencrypted state. It automatically encrypts them before they're transferred outside from a user's device. For more information abo
```

---

### 37. Assessments

**URL:** https://learn.microsoft.com/en-us/purview/compliance-manager-assessments
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:7c7fd5fb881af54780a91573c59979880cb15458120ed3146bf793177a3599d8

**Affected Controls:**
- Control 3.3: Control 3.3: Compliance and Regulatory Reporting
  - File: `controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md`
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`

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
@@ -68,7 +68,7 @@ : The services covered by the assessment, such as Microsoft 365, Microsoft Azure, or other cloud services.
 Regulation
 : The regulatory template serving as the basis for the assessment.
-To filter your view of assessments:
+To filter your view of assessments, follow these steps:
 Select
 Filter
 at the top-left corner of your assessments list.
@@ -84,8 +84,8 @@ Data protection baseline default assessment
 To get you started, Microsoft provides a default
 Data Protection Baseline
-assessment that's included at all subscription levels. This baseline assessment has a set of controls for key regulations and standards for data protection and general data governance. This baseline draws elements primarily from NIST CSF (National Institute of Standards and Technology Cybersecurity Framework) and ISO (International Organization for Standardization), as well as from FedRAMP (Federal Risk and Authorization Management Program) and GDPR (General Data Protection Regulation of the European Union).
-This assessment is used to calculate your initial compliance score the first time you come to Compliance Manager, before you configure any other assessments. Compliance Manager collects initial signals from your Microsoft 365 solutions. You see at a glance how your organization is performing relative to key data protection standards and regulations, and see suggested improvement actions to take. Compliance Manager becomes more helpful as you build and manage your own assessments to meet your organization's particular needs.
+assessment that's included at all subscription levels. This baseline assessment has a set of controls for key regulations and standards for data protection and general data governance. The Data Protection Baseline assessment draws elements primarily from NIST CSF (National Institute of Standards and Technology Cybersecurity Frame
```

---

### 38. Conditional Access

**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview
**Section:** Microsoft Entra ID
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c96f5a2efd719c88e6a21a69b8da6bead50f28a56953a4f0b61a117af52b3e7b

**Affected Controls:**
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.11/powershell-setup.md` (HIGH)

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

```

---

### 39. Conditional Access Policies

**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-policies
**Section:** Microsoft Entra ID
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0a07640ad9b81d18d3b4a25f11c92f2f7fc1c6e7756a91bc6a852946732b0953

**Affected Playbooks:**
- ℹ️ `playbooks/getting-started/phase-1-minimal-viable-controls.md` (HIGH)

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

```

---

### 40. Phishing-Resistant MFA

**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths
**Section:** Microsoft Entra ID
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8a73d89092442fa1063070fbe3cb9d366cf8d237141c4ee2daa22197458e1d99

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.11/powershell-setup.md` (HIGH)

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
@@ -98,6 +98,7 @@ SMS sign-in
 Password
 Federated single-factor
+QR code
 1
 Something the user has
 refers to one of the following methods: text message, voice, push notification, software OATH token, or hardware OATH token.

```

---

### 41. Governing Agent Identities

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:130814c87f58819cbad55ad60c68e501e20febef98d77df147f54a47dbc68c09

**Affected Controls:**
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`

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
@@ -25,31 +25,19 @@ Microsoft Entra allows you to ensure that the right people have the right access to the right apps and services at the right time. With the addition of the Microsoft agent identity platform, managing the access rights of agents in the same way is just as important in the governance lifecycle of your organization's identities. The Microsoft agent identity platform introduces the concept of Agent Identities (IDs). Agent identities are accounts within Microsoft Entra ID that provide unique identification and authentication capabilities for AI agents.
 This allows agent identities to be governed with Microsoft Entra features in the same style as you would govern human identities. With Agent identities, you can govern and manage the identity and access lifecycle of agents, ensuring the agents have a responsible person providing oversight throughout the agent lifecycle and agent's access does not persist longer than it is needed. This article provides an overview of how Microsoft Entra can be utilized to govern agent identities.
 License requirements
-Microsoft Entra Agent ID is a product within Microsoft Entra that provides the platform for creating and managing agent identities and agent identity blueprints. Agent ID is available for all Microsoft Entra customers.
+Using
+Microsoft Entra ID Governance
+for agent identities requires one of the following license plans:
+Microsoft 365 E7
+, which includes Agent 365 and Microsoft Entra Suite, to provide governance of user and agent identities.
 Microsoft Agent 365
-enables agents to operate across Microsoft 365 services and enterprise workflows, which requires a
+license paired with at least Microsoft Entra P1 or Microsoft 365 E3.
+For more information, see
+Microsoft Agent 365 plans and pricing
+. For the full list of agent-specific capabilities, refer to the
 Microsoft Agent 365
-licen
```

---

### 42. Sharing Permissions

**URL:** https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:4b793c009cc51f5560d5eaedae0b8f5745a0b090a69f612f002baf0862069dd8

**Affected Controls:**
- Control 4.8: Control 4.8: Item-Level Permission Scanning for Agent Knowledge Sources
  - File: `controls/pillar-4-sharepoint/4.8-item-level-permission-scanning-agent-knowledge-sources.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.8/troubleshooting.md` (HIGH)

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

```

---

### 43. External Sharing

**URL:** https://learn.microsoft.com/en-us/sharepoint/external-sharing-overview
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a14361049b16ad88208892576caefec6cae4c1baaf42c9bc5cc9191b41830389

**Affected Controls:**
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)

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

```

---

### 44. Manage Sharing Settings

**URL:** https://learn.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off
**Section:** SharePoint Administration
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:ba60c4b3af13055680a46a2b27776327a68d1b9231b063a5a424d6bd71aeaee2

**Affected Controls:**
- Control 4.4: Control 4.4: Guest and External User Access Controls
  - File: `controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.4/troubleshooting.md` (HIGH)

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
@@ -52,7 +52,7 @@ Sites
 SharePoint external authentication
 (Microsoft Entra B2B integration not enabled)
-No guest account created*
+No guest account created (see the note following this table)
 Microsoft Entra settings don't apply
 N/A
 (Microsoft Entra B2B always used)
@@ -61,41 +61,43 @@ Microsoft Entra settings apply
 Guest account always created
 Microsoft Entra settings apply
-*A guest account might already exist from another sharing workflow, such as sharing a team, in which case it's used for sharing.
+Note
+A guest account might already exist from another sharing workflow, such as sharing a team, in which case it's used for sharing.
 For information on how to enable or disable Microsoft Entra B2B integration, see
 SharePoint and OneDrive integration with Microsoft Entra B2B
 .
-Video demonstration
-This video shows how the settings on the
+Change organization-level external sharing setting
+In the SharePoint admin center, expand
+Policies
+, and then select
 Sharing
-page in the SharePoint admin center
-affect the sharing options available to users.
-How do I change the organization-level external sharing setting?
-Go to
-Sharing
-in the SharePoint admin center
-, and sign in with an account that has
-admin permissions
-for your organization.
+.
 Under
 External sharing
-, specify your sharing level for SharePoint and OneDrive. The default level for both is
-Anyone
-.
-Note
-The SharePoint setting applies to all site types, including those connected to Microsoft 365 groups and teams. Groups and Teams guest sharing settings also affect connected SharePoint sites.
+, set your sharing level for SharePoint and OneDrive. Keep these points in mind:
+The SharePoint setting applies to all site types, including sites connected to Microsoft 365 groups and teams. Groups and Teams guest sharing settings also affect connected SharePoint sites.
 The On
```

---

### 45. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:e7207a407319a0a76534693b914cbbf5edc5d193e97684a12c0d88553cc5d69a

**Affected Controls:**
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

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
@@ -86,15 +86,15 @@ Add or remove your security groups or Microsoft 365 groups and select
 Save
 .
+Apply site access restriction to a site
 To apply site access restriction to the site, you must add at least one group to the site access restriction policy.
 For a group connected site, the Microsoft 365 group connected to the site is the default Restricted Access Control group. You can choose to keep this group and add more Microsoft 365 or Microsoft Entra Security groups as Restricted Access Control group.
 Note
 There's a tag labeled as
 Default group
 marked against the Microsoft 365 group connected to the site as shown in the previous image.
-To manage site access restriction for a SharePoint site by using PowerShell, use the following commands:
-Action
-PowerShell command
+Manage site access restriction by using PowerShell
+To manage site access restriction for a SharePoint site by using PowerShell, use the PowerShell commands described in this section.
 Enable site access restriction
 Set-SPOSite -Identity <siteurl> -RestrictedAccessControl $true
 Add group
@@ -111,7 +111,7 @@ After you delegate the site access restriction control to site admins, they can configure the site access restriction setting at the
 Site Information
 panel.
-To restrict access to a SharePoint site:
+Restrict access to a SharePoint site
 Limit who can access a site by using Microsoft Entra security groups or Microsoft 365 groups.
 Add the groups that contain the users who should have access.
 Add up to 10 groups for each site.
@@ -141,17 +141,14 @@ As an IT administrator, you can view the following reports to gain more insight about SharePoint sites protected with restricted site access policy:
 Sites protected by restricted site access policy (RACProtectedSites)
 Details of access denials due to restricted site access policy (ActionsBlockedByPolicy)
-Reports are curre
```

---

### 46. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:f8ab6732d30fcabbd2cbeb303e4298d93f4709b6153a5fc59c2cd48e7cb19559

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
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -22,108 +22,142 @@ Restrict discovery of SharePoint sites and content
 Feedback
 Summarize this article for me
-For organizations onboarding to Microsoft 365 Copilot, maintaining strong data governance controls for SharePoint content is critical to deploying Copilot in a safe manner. Sites identified with the highest risk of oversharing can use Restricted Content Discovery to protect content while taking time to ensure that permissions are accurate and well-managed.
-With Restricted Content Discovery, organizations can limit the ability of end users to search for files from specific SharePoint sites. Enabling Restricted Content Discovery for each site prevents the sites from surfacing in organization-wide search and Microsoft 365 Copilot Business Chat, unless a user had a recent interaction.
-Restricted Content Discovery is a site-level setting that needs to be propagated to the search index, a large number of transactions could lead to a long queue in the ingestion pipeline and higher update latency times.
-While child content is hidden by default, users in your organization can still discover files they own or recently interacted with. End users can still find relevant content they need for their day-to-day tasks, even if Restricted Content Discovery is applied to the parent site.
-Restricted Content Discovery doesn't affect searches originating from a site context or other intelligent features such as Microsoft 365 Feed and Recommendations.
+Organizations preparing for Microsoft 365 Copilot often need time to review SharePoint sites, validate permissions, and implement governance controls before making content broadly discoverable. Restricted Content Discovery (RCD) helps you limit discovery of content from specific SharePoint sites while those reviews are taking place.
+When you enable Restricted Content Discovery for a site, content from tha
```

---

### 47. Restricted SharePoint Search

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search
**Section:** SharePoint Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:70150ee056fa4a1b98d017eef96af16857daaf2b3c83d19657d66b9b9a6b43cd

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
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to plan
+Add to Plans
 Edit
 Copy Markdown
 Print
@@ -23,21 +23,24 @@ Feedback
 Summarize this article for me
 Important
-Restricted SharePoint Search is designed for customers of Microsoft 365 Copilot chat and agentic experiences. It's designed as a short-term solution to allow time for your organization's administrators to thoroughly review and audit site and file permissions, but it's not intended or scalable for long-term use. Comprehensive data security solutions are available, including
+Restricted SharePoint Search is retiring. Starting July 31, 2026, new enablement is blocked. Use comprehensive data controls such as
+Restricted Content Discovery
+(RCD) for content discoverability.
+Restricted SharePoint Search is designed for customers of Microsoft 365 Copilot chat and agentic experiences. It's a short-term solution that gives your organization's administrators time to review and audit site and file permissions. It's not intended or scalable for long-term use. Comprehensive data security solutions are available, including
 SharePoint Advanced Management
 and
 Microsoft Purview
 .
 What is Restricted SharePoint Search?
-Restricted SharePoint Search is a setting that enables you as a
+Restricted SharePoint Search is a setting that you, as a
 SharePoint Administrator
 or
 other Microsoft 365 administrator
-to maintain a list of SharePoint sites (an "allowed list") for which you have checked permissions and applied data governance. The allowed list defines which SharePoint sites can be used in organization-wide search queries, and, as a temporary measure, Copilot chat and agentic experiences.
-By default, the Restricted SharePoint Search setting is turned off and the allowed list is empty. If Restricted SharePoint Search is enabled, users can interact with files and content they own or have previously accessed in Copilot.
+, use to maintain a list of SharePoint sites (an "allow list") for which
```

---

### 48. Advanced Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:26cfb3d2cd8bf1b4dafd455afcb0c9f5bf1a6bc3c2e2c992e4d0ea9927081eca

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

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
@@ -32,6 +32,8 @@ SAM capabilities are helpful as organizations
 prepare for Microsoft 365 Copilot and agents
 .
+Video: SharePoint Advanced Management overview
+Watch the following video to get an overview of SharePoint Advanced Management:
 Administrators primarily manage SAM through the SharePoint admin center. It's designed for SharePoint and Microsoft 365 administrators who are responsible for governance, risk reduction, and audit readiness. You can also use the
 SharePoint Admin Agent
 to make your SharePoint administration more productive and efficient.

```

---

### 49. Site Lifecycle Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/site-lifecycle-management
**Section:** SharePoint Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:8931c168253a1bc782acadb45544e76e5f6790fc701af512fd1b80d79bd8e938

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

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
@@ -19,399 +19,105 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Manage inactive sites by using inactive site policies
+SharePoint site lifecycle management
 Feedback
 Summarize this article for me
-Site lifecycle management capabilities in
+Site lifecycle management policies in
 Microsoft SharePoint Advanced Management
-help you improve site governance by automating the process of detecting inactive sites and notifying site owners by email. Site owners can then review and confirm whether their sites are still active.
-You can configure an inactive sites policy in the SharePoint admin center. This article describes how to set up an inactive site policy with notifications and enforcement actions.
-Prerequisites for an inactive site policy
-See
-SharePoint Advanced Management prerequisites
+help you maintain site governance at scale. These policies automate common governance tasks, so sites stay active, properly owned, and regularly reviewed throughout their lifecycle.
+Video: Overview of SharePoint Advanced Management
+The following video provides an overview of SharePoint site lifecycle management:
+Site lifecycle management policies don't delete SharePoint sites directly. Instead, the policies notify site owners and administrators, and take actions based on how you configure the policies.
+As your organization creates more SharePoint sites, Microsoft Teams-connected sites, and Microsoft 365 group-connected sites, it becomes increasingly difficult for your administrators to manually identify inactive sites, ownerless sites, or sites that no longer meet business requirements. Site lifecycle management policies help you automate these governance processes by monitoring sites, notifying responsible users, collecting responses, and taking enforcement actions when necessary.
+Benefits of site lifecycle management
+S
```

---

### 50. Site Attestation

**URL:** https://learn.microsoft.com/en-us/sharepoint/request-site-attestations
**Section:** SharePoint Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:194495b8c68af97a8c37b41822c81a46a7320ea29dec563cb239d677e3c4053f

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`

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
@@ -22,17 +22,21 @@ Request recurring site attestations for SharePoint sites
 Feedback
 Summarize this article for me
-Site lifecycle management policies in
-Microsoft SharePoint Advanced Management
-help your organization improve site governance. Site attestation involves regular reviews by site owners or site administrators to check and confirm the accuracy of site information, including the site's necessity, its owners, members, permissions, and sharing settings. For sites that remain unattested, you can choose to automate enforcement actions to prevent risks of content overexposure. This approach ensures ongoing site compliance and actively reduces risks such as information oversharing.
-Site attestation policies help you manage periodic attestation of sites at scale. You can configure a site attestation policy in the SharePoint admin center. This article describes how to create and configure a site attestation policy in either active or simulation mode.
+Site attestation policies help you periodically verify that SharePoint sites continue to meet your organization's governance requirements. These policies request reviews from site owners or site administrators, who confirm whether a site is still needed and whether its ownership, membership, permissions, and sharing settings remain appropriate.
+You can configure site attestation policies to send recurring review requests and apply enforcement actions when required reviews aren't completed.
+For an overview of site lifecycle management policies, see
+SharePoint site lifecycle management
+.
+This article describes how to create a site attestation policy with notifications and enforcement actions.
 Requirements for a site attestation policy
 See
 SharePoint Advanced Management prerequisites
 .
-How does a site attestation policy work?
-When a site attestation policy runs (usually on a monthly bas
```

---

### 51. Agent Insights

**URL:** https://learn.microsoft.com/en-us/sharepoint/insights-on-sharepoint-agents
**Section:** SharePoint Administration
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:04c0b2658748f4e862810812ec97ae5040d7daee7d392e294f71dcbfc549e9b2

**Affected Controls:**
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

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

```

---

### 52. Custom Analytics Rules

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/create-analytics-rules
**Section:** Azure Services
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:053c1489e472b9524b5e6ea20770ca24569fca560518458e391900b31f2f8380

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
@@ -38,7 +38,7 @@ to find and install the recommended rules specific to that recommendation. For more information, see
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
 and define up to 10 entity types recognized by Microsoft Sentinel onto fields
```

---

### 53. Workbooks

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/monitor-your-data
**Section:** Azure Services
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:abf4c4d8f59f2a5ea19e6820cc2679f725906dffb322da778f14b1e43b2ec220

**Affected Controls:**
- Control 3.9: Control 3.9: Microsoft Sentinel Integration
  - File: `controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md`

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
@@ -36,6 +36,7 @@ unified security operations experience offered by Microsoft Defender
 .
 Prerequisites
+Before you create or use workbooks, make sure you meet the following prerequisites:
 You must have at least
 Workbook reader
 or
@@ -98,7 +99,7 @@ For more information, see:
 Create interactive reports with Azure Monitor Workbooks
 Tutorial: Visual data in Log Analytics
-Create new workbook
+Create a new workbook
 Create a workbook from scratch in Microsoft Sentinel.
 In Microsoft Sentinel, select
 Threat management > Workbooks
@@ -168,13 +169,15 @@ You can delete both saved templates and customized workbooks from the
 My workbooks
 tab. Templates themselves can't be deleted.
+Warning
+Deleting a workbook permanently removes the workbook resource and any customizations you made to the template. This action can't be undone. The original template remains available.
 To delete a workbook, select the workbook in the
 My workbooks
 tab, and then select
 Delete
-. This action removes the workbook resource and any changes you made to the template. The original template remains available.
+.
 Workbook recommendations
-This section reviews basic recommendations we have for using workbooks with Microsoft Sentinel.
+The following recommendations help you use Microsoft Sentinel workbooks effectively.
 Add Microsoft Entra ID workbooks
 If you use Microsoft Entra ID with Microsoft Sentinel, we recommend that you install the Microsoft Entra solution for Microsoft Sentinel and use the following workbooks:
 Microsoft Entra sign-ins
@@ -198,13 +201,15 @@ or
 CommonSecurityLog
 table, on any other firewall.
+The query compares daily security event counts between the current week and the previous week, so you can quickly spot unusual changes in event volume.
 // week over week query
 SecurityEvent
 | where TimeGenerated > ago(14d)
 | summarize count() by bin(TimeGe
```

---

### 54. Automation Rules

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/automate-incident-handling-with-automation-rules
**Section:** Azure Services
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:fa09b7f0452d1498105482b0dd2986134a06e29cbd46256a3f9b6657ef79c32d

**Affected Controls:**
- Control 3.9: Control 3.9: Microsoft Sentinel Integration
  - File: `controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md`

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
@@ -97,6 +97,13 @@ or
 NRT
 analytics rule.
+If your workspace is onboarded to the Microsoft Defender portal, you can also use the
+Case created
+and
+Case updated
+triggers from
+Simple Flows
+(preview) to automate case workflows.
 Incident-based or alert-based automation?
 With automation rules centrally handling the response to both incidents and alerts, how should you choose which to automate, and in which circumstances?
 For most use cases,
@@ -137,7 +144,10 @@ Microsoft security
 analytics rules
 .
-Alert-triggered automation for alerts created by Microsoft Defender XDR is not available in the Defender portal. For more information, see
+In the Defender portal:
+Alert-triggered automation for alerts created by Microsoft Defender XDR isn't available. To automate responses to alerts across Microsoft Sentinel, Microsoft Defender, and XDR platforms, use the
+Enhanced Alert Trigger
+. For more information, see
 Automation in the Defender portal
 .
 Conditions
@@ -316,6 +326,17 @@ Changing the severity of an incident: You can reevaluate and reprioritize based on the presence, absence, values, or attributes of entities involved in the incident.
 Assigning an incident to an owner: This helps you direct types of incidents to the personnel best suited to deal with them, or to the most available personnel.
 Adding a tag to an incident: This is useful for classifying incidents by subject, by attacker, or by any other common denominator.
+If your workspace is onboarded to the Microsoft Defender portal,
+Simple Flows
+(preview) adds more pre-built actions you can use directly from the automation rule wizard, without writing a playbook. Available actions include
+Send Case Created/Updated/SLA Exceeded Email
+,
+Update Case
+,
+Add Task
+, and
+Update Alert
+.
 Also, you can define an action to
 run a playbook
 , in order to take more complex response actions,
```

---

### 55. Investigate Incidents

**URL:** https://learn.microsoft.com/en-us/azure/sentinel/investigate-cases
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c6e978471c2420b2c53b14958642d150cc3dd0137bf9c9c85b552aaf6fd1220f

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
@@ -22,9 +22,9 @@ Investigate incidents with Microsoft Sentinel (legacy)
 Feedback
 Summarize this article for me
-This article helps you use Microsoft Sentinel's legacy incident investigation experience. If you're using the newer version of the interface, use the newer set of instructions to match. For more information, see
+This article helps you use Microsoft Sentinel's legacy incident investigation experience. If you're using the newer version of the interface, see
 Navigate and investigate incidents in Microsoft Sentinel
-.
+for instructions that match that experience.
 After connecting your data sources to Microsoft Sentinel, you want to be notified when something suspicious happens. To enable you to do this, Microsoft Sentinel lets you create advanced analytics rules that generate incidents that you can assign and investigate.
 An incident can include multiple alerts. It's an aggregation of all the relevant evidence for a specific investigation. An incident is created based on analytics rules that you created in the
 Analytics
@@ -34,11 +34,13 @@ Azure Preview Supplemental Terms
 include additional legal terms that apply to Azure features that are in beta, preview, or otherwise not yet released into general availability.
 Prerequisites
+Before you investigate or assign incidents, make sure the following prerequisites are met:
 You'll only be able to investigate the incident if you used the entity mapping fields when you set up your analytics rule. The investigation graph requires that your original incident includes entities.
 If you have a guest user that needs to assign incidents, the user must be assigned the
 Directory Reader
 role in your Microsoft Entra tenant. Regular (nonguest) users have this role assigned by default.
 How to investigate incidents
+Perform the following steps to review and investigate incidents:
 Select
 Incidents
 .
```

---

### 56. Azure Key Vault

**URL:** https://learn.microsoft.com/en-us/azure/key-vault/general/overview
**Section:** Azure Services
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:bddfe861ee5b3f0d56aca4481e6cdcf86f4b3f2748e6c305a9ef819a3674fcb0

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

```

---

### 57. Azure Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/azure/azure-monitor/alerts/alerts-overview
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:68d1f722854ea44006f485ae990177db45d539c70f0f19489b0920f932837baa

**Affected Controls:**
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/agent-365-observability/alerting-configuration.md` (HIGH)

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
@@ -35,6 +35,11 @@ An
 alert
 is triggered if the conditions of the alert rule are met. The alert initiates the associated action group and updates the state of the alert. If you're monitoring more than one resource, the alert rule condition is evaluated separately for each of the resources, and alerts are fired for each resource separately.
+Where supported, a fired alert can also become the starting point for investigation workflows in Azure Monitor, including the
+Azure Copilot Observability Agent
+and
+Azure Monitor issues
+.
 Alerts are stored for 30 days and are deleted after the 30-day retention period. You can see all alert instances for all of your Azure resources on the
 Alerts page
 in the Azure portal.
@@ -164,9 +169,8 @@ Log search alert rules that use splitting by dimensions are charged based on the number of time series created by the dimensions resulting from your query. If the data is already collected to a Log Analytics workspace, there is no additional cost.
 If you use metric data at scale in the Log Analytics workspace, pricing will change based on the data ingestion.
 Simple log search alerts
-Simple log search alerts are designed to provide a simpler and faster alternative to traditional log search alerts. Unlike traditional log search alerts that aggregate rows over a defined period, simple log alerts evaluate each row individually. Search based alerts support the analytics and basic logs.
-Simple log search alerts use the Kusto Query Language (KQL) but the feature is designed to simplify the query process, making it easier for you to create alerts without extensive KQL knowledge.
-Simple search alerts provide faster alerting compared to traditional log search alerts By evaluating each row individually. Alerts are triggered almost in real-time, allowing for quicker incident response.
+Simple log search alerts
+evaluate each r
```

---

### 58. Track and Revoke Documents

**URL:** https://learn.microsoft.com/en-us/purview/track-and-revoke-admin
**Section:** Azure Services
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:75fe0e67e9164a55dbb592a2f0ae892987961e927b805ca99007badf1feb2d3f

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
@@ -24,7 +24,9 @@ Summarize this article for me
 Microsoft Purview service description
 Document tracking provides information for administrators about when a protected document was accessed. If necessary, both admins and users can revoke document access for tracked documents.
-A document must be registered for tracking before an admin can track access details, including successful access events and denied attempts, and revoke access if needed. See the next section for minimum versions of Office apps that support file registration the next time they're opened.
+A document must be registered for tracking before an admin can track access details, including successful access events and denied attempts, and revoke access if needed. For minimum versions of Office apps that support file registration the next time they're opened, see
+Requirements
+.
 Note
 Track and revoke features are supported for Office file types only.
 Requirements
@@ -41,6 +43,7 @@ Connect-AipService
 to connect to your tenant before you run any of the documented cmdlets.
 Limitations
+The following limitations apply to track and revoke features:
 Password-protected documents aren't supported by track and revoke features.
 If you attach multiple documents to an email, and then protect the email and send it, each of the attachments gets the same ContentID value. This ContentID value will be returned only with the first file that had been opened. Searching for the other attachments won't return the ContentID value required to get tracking data.
 Additionally, revoking access for one of the attachments also revokes access for the other attachments in the same protected email.
@@ -69,15 +72,15 @@ value for the document you want to track.
 Use the
 Get-AipServiceDocumentLog
-to search for a document using the filename or the email address of the user who applied protection.
+cmdlet to se
```

---

### 59. Apply IRM to SharePoint

**URL:** https://learn.microsoft.com/en-us/purview/apply-irm-to-a-list-or-library
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:6c2866688535a296bed60335ddb58d28963f995a3e44313890a54241427de4f3

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

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
@@ -23,7 +23,7 @@ Feedback
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
 Information Rights Management (IRM) enables you to limit the actions that users can take on files that downloaded from lists or libraries. IRM encr
```

---

### 60. Management Activity API

**URL:** https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
**Section:** Office 365 Management API
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6f6c592ed3219fdb6cbf94e5cbaa153bf90135ba3aab161c92eeb07b2e984267

**Affected Controls:**
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)

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

```

---

### 61. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:0cd4edc3630ccc67e4351a6083470fdb477328d9a92e6de16f3c72dc6c4e6b51

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
@@ -511,7 +511,9 @@ eDiscovery (Standard) enables you to create eDiscovery cases and assign eDiscovery managers to specific cases. eDiscovery managers can only access the cases of which they're members. eDiscovery (Standard) also lets you associate searches and exports with a case and lets you place an eDiscovery hold on content locations relevant to the case.
 eDiscovery (Premium)
 provides an end-to-end workflow to preserve, collect, analyze, review, and export content that's responsive to your organization's internal and external investigations. It also lets legal teams manage the entire legal hold notification workflow to communicate with custodians involved in a case.
-In Microsoft Purview eDiscovery, a custodian refers to the individual whose content is subject to search, hold, or review as part of a legal, regulatory, or investigative process. A custodian is typically an employee or user whose data (e.g., email, documents, Teams messages) may be relevant to the matter under investigation. This is distinct from the IT administrators or compliance officers who perform searches or manage eDiscovery cases. Licensing requirements apply both to custodians (whose data is preserved or reviewed) and to users performing eDiscovery activities, as defined in the Microsoft Purview licensing terms.
+In Microsoft Purview eDiscovery, a custodian refers to the individual whose content is subject to search, hold, or review as part of a legal, regulatory, or investigative process. A custodian is typically an employee or user whose data (e.g., email, documents, Teams messages) may be relevant to the matter under investigation. This is distinct from the IT administrators or compliance officers who perform searches or manage eDiscovery cases. Licensing requirements for eDiscovery vary based on usage. When premium eDiscovery features are used to analyze a userâs 
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Managed Environment Sharing Limits
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-sharing-limits
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:37cb138e983d31e6cea9986625eb8033b11e2a3a74a08ec6847902d4f327d099

---

### 2. Solution Checker Enforcement
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-solution-checker
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b7f4f3f2ece529beab8f0ae2d7b6ce7338456db1aaf0466b35193cad826b4b9e

---

### 3. Environment Group Rules
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f5bbbd8c4cda402ff00f151e73e829363fee475e3e5584a4479ff4c23dad7a14

---

### 4. Developer Environments
**URL:** https://learn.microsoft.com/en-us/power-platform/developer/create-developer-environment
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:257999fc4a62476d88e02c7c0e35f74fc4195ff09ba22c9f04da5552b7c4eb04

---

### 5. Advanced Connector Policies
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e007bc61a0457ef21c92602e09e2915312c99518bf3bba29e5fafef98eedb7d6

---

### 6. DLP Policies (Power Platform)
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e13870a3c31f5cf53252c4b3d4f0b53b21ebdddddf1da9c87dcfdb7ca03284be

---

### 7. Connector Classification
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/dlp-connector-classification
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fba6bcd6d385591b302b192b3274cd6bdc88020dbe89b930d59da544e5c91c1a

---

### 8. Third-Party Connectors
**URL:** https://learn.microsoft.com/en-us/power-apps/maker/canvas-apps/connections-list
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:56ea8255431c80ffff028c4464b6695a41db4e12719230d4c1332e0f5b512582

---

### 9. Custom Connectors
**URL:** https://learn.microsoft.com/en-us/connectors/custom-connectors/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ca4b3b44f31abccef31de93ca428da49157e51c6b3384081a62d58bab0326943

---

### 10. Security
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:eb30b3829c9a321481e00ec3be2943e3b8cb4057c97c3010abdcd42bfe08a1e5

---

### 11. Security Roles
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:159b37f0b910de9c5548e937f9dd59edf5f5671737891635eef6ee4bc379353c

---

### 12. Create Security Roles
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/create-edit-security-role
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:086284a80b8e631ab75a2a1ed85dda7a972cce6f4f454bbb88f2935f5f2d0e93

---

### 13. Database Security
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/database-security
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6121276dc029f6b5d37afd9963b2c8ca77ae34fdef5ec442742448dcdde94acc

---

### 14. Column-Level Security
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/field-level-security
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:d5070adab7a9d889c2cd04892e64f59f5ba6215d4f8fbc59f6a2d994599ec230

---

### 15. High-Privileged Admin Roles
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-high-privileged-admin-roles
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:98b296f8c9db5f3196418441b0074fa6c465cce4488535f8fc11d5ba97275bb2

---

### 16. Analytics
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/analytics-common-data-service
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:19723c0e02094b46fd3ffac6023e42e254cc3f28a1e8fcd2f5551563339cb277

---

### 17. Export Analytics to Azure
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/self-service-analytics
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8ae19b97d7e400a28d95191560745695561d5d678f8b5d77e2c24a5285ab2456

---

### 18. Monitor Microsoft Copilot Studio
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitor-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:89174dfb3d432ddbc59c21d8835bfb84ccec1b00de65c2558057e931af51fd40

---

### 19. Monitoring Hub
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitoring-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e24ea3018a46499e291d5092399937a91ed11ed78dfbcaa8d6dd3f4c90cc212b

---

### 20. Admin Activity Logging
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/activity-logging-auditing/activity-logs-power-platform-admin
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ecc624d272bc5ccf841ddfddc3d4ad9cf5cdb004485d32493461949b8047cdb9

---

### 21. Copilot Hub
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6f20aac4f3ce2316a5eafa8e0d52a9bc6f6eee004e9db6ad38d3539a7c7000f3

---

### 22. Agent Access Points
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/security/identity-access-management#agent-access-points-preview
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:4a84a25a19d7220dd51ce7b864f89f451eee4bf86a6d28d18ca4cc3f0cc5fb60

---

### 23. Copilot Studio Message Capacity
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e591a8626eca0e48d52b387250bdb2ef0487c8d66c4ab11fee28f2e5283d5177

---

### 24. Capacity Storage
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:50e02599a2adb0ff0535bc6f46d50bfa6a11dccc78d33aaf0748d87f66ca4696

---

### 25. PowerShell
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:55822597a89306c18ec6936d74635a8a5cb71c7bada3df9683acbe31c94bbc11

---

### 26. PowerShell Getting Started
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/powershell-getting-started
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ee48f2f63e6f06360eed70edeeb58e413b0308b574cdf1a3cdc735d1f385333d

---

### 27. Power Platform Governance
**URL:** https://learn.microsoft.com/en-us/power-platform/guidance/adoption/dlp-strategy
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:3fa52bd3885f19c776b7b19ccf2d3fc6760d987cdaaeec3155b049a44d0c2f89

---

### 28. CoE Power BI Monitor
**URL:** https://learn.microsoft.com/en-us/power-platform/guidance/coe/power-bi-monitor
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ce5f90d52dd7da3acb76f120fa9e97a7d19b95560a3b8c4187ba6cfe0784e80f

---

### 29. Enhanced Admin Controls [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:48ef4170c46d394854a9541a74e1b5d769c0dbd601541635c9097a903f2e5c5f

---

### 30. Set Up Pipelines
**URL:** https://learn.microsoft.com/en-us/power-platform/alm/set-up-pipelines
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:7c04f42aac0720fc467a803bb0fc7ad54e0877138092b30f1fbb76f3b108e327

---

### 31. Run Pipelines
**URL:** https://learn.microsoft.com/en-us/power-platform/alm/run-pipeline
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:3917e8a9d58b173aac5a0eefc281226e89474435928a86de40cefbf61ea1c062

---

### 32. Default Deployment Pipeline
**URL:** https://learn.microsoft.com/en-us/power-platform/alm/default-deployment-pipeline-rule-for-environment-groups
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a702ce16d330d8fc96be0ac26cbee81b0c5af94e95d32fddad9564d404e29969

---

### 33. Solution Concepts
**URL:** https://learn.microsoft.com/en-us/power-platform/alm/solution-concepts-alm
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:65186e6c0008ccc7bab140bdbb98aa49581c9a34796d3ce46b53115c9ba171bd

---

### 34. Copilot Studio Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:99d280f6ebe4ee658d46d5d96c69b139c1cf78246a7f2691a518049fcec64bee

---

### 35. Security and Governance
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2ec331e65ac84583004e2bb380873aba35d2985102f60cb7e86ae39d63a61876

---

### 36. Sensitivity Labels in Copilot Studio
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b2f39a2ba409bfc1c7af456069eb64d5192e0306beaca4062f0aebdb48b6d9ed

---

### 37. Agent Publishing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:361548ab68a7734a2a85b8e6106b239ca5a2383457982d130751f74f1096c14f

---

### 38. Analytics
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:67ddb3c6c52201074c0662ce176c561ef4cc81952bfab91d94363b5338ede7a6

---

### 39. Customer Satisfaction
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:49116bbd42d20db85edb38be0a236011d85e31ef4796c59b1f546d77dac44da6

---

### 40. Connectors
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:816357f85a329f93ebe69bc4b125504bdfed3ff40dfbc0f97001c2c544185a2a

---

### 41. Knowledge Sources
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:07f5e0a19485946ccc9bff6105ab1616d7a3180b63d264ff4003edbbaae22e4e

---

### 42. Quickstart: Create and deploy an agent
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-gpt-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ec7ce6eda0ddc68179f3db2c9069fa20675f5e7a4b0992cbf9e6253067647dc3

---

### 43. Agent Orchestration
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-tools-custom-agent
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:4e33173bf65b43c20bc5867f1c6fa542a91a47530d0ff554c791b709ec6eb65c

---

### 44. External Threat Detection
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/external-security-provider
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:408c3a5a9d34c3fe3f0e2649ad67da4a7a35a82840223811299e64ff35831f9f

---

### 45. Human Agent Handoff
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-hand-off
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0bc03a22f793dc359891b1d75d2ed29a46565542d8833b565b40733c88c2b80c

---

### 46. VNet Support
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-network-isolation-vnet
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:072b9843850f25a87d38312220b6c3525c90811119feb45b51523b3e2d0805cc

---

### 47. Governance Guidance
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/sec-gov-intro
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6adf155eafc5dcc9c74dc544f2fb331f2bfcd4e44f72a952e77acf7034c17ff7

---

### 48. Architecting Agent Solutions
**URL:** https://learn.microsoft.com/en-us/agents/architecture/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:cb5211f2a84030fd18ccb1e2077eebb302e691dbbf98192e4784f45be4bf5e3f

---

### 49. Create Custom MCP Server
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:80b86de980dc87f5e3433b0a3518b230ca01ac7d3cbfa3d0179e475643a25b6b

---

### 50. Agentic Center of Enablement [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:01c7c25b520572f2022a9f1e839bfa8a2c38de0424335660ea5d295220f1d9c8

---

### 51. M365 Copilot Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6a884a4f2d1cb03a83b2b69a911448fbd6f59197a790cc2437dcd3ddd4dbb4a8

---

### 52. Manage Copilot
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-enable-users
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b20d69b13373c7bec0592fd2bc3dddd754cf81710e091a7398d6f5152e5e5bfe

---

### 53. Manage Agents
**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ef0c6223a02b6ffdd5f4b81d9493d020a87c4c057196d843638d202fc7dd30c3

---

### 54. Copilot Usage Reports
**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0bcd10b9779d7753b859773001f1d369d18af0d505601ba41c793fdc5ebf5a85

---

### 55. Copilot Control System Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b2fe7be949c443d7009e305eafb22ceff8266b0dab554b94f24004f6dc780dfa

---

### 56. Copilot Control System - Security and Governance
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/security-governance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8481068e35a39ea8143077c6d87885908829e87ee41b878a957634798173799a

---

### 57. Copilot Control System - Management Controls
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/management-controls
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fbcb682bddc350c4b45104321785423f82fc83eb5dfe8a408f63ebb9091a7cec

---

### 58. Agent Management Essentials Hub
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-essentials-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2b928e5e9f139e3e26ce7fb28e41e386d4ed9d0d6f3ad4cf060c8a06cfefa0fd

---

### 59. Agent Prerequisites
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-prerequisites
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:82877d58c6b134469908dde27c00cf5b496f680c148f7e4047a63bff0179f334

---

### 60. Visual Governance Guide
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-visual-map
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b72446bc3f1cf1fd41cb46a55290bac76ecc3d805d461fc2f9c673cc6f980171

---

### 61. Deployment Checklist
**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/m365-agents-checklist
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8e231183f234713bbc9fb1c97ed3071f807f28ad919fd8f52a81a19710efe03d

---

### 62. Agent 365 SDK and CLI
**URL:** https://learn.microsoft.com/en-us/microsoft-agent-365/developer/
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c0d8868bca505a8ef1b3f0c236850afccbfa36d5808577bf7448098761bf30d5

---

### 63. Agent 365 Overview Page (M365 Admin)
**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8bf9d4caf0a16a09cce6d98bdaee378f9b96dcbd96dcf0a09d4eef817334d7cd

---

### 64. Agent 365 Security Overview
**URL:** https://learn.microsoft.com/en-us/security/security-for-ai/agent-365-security
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:5dd714066038018715c3980a11d5d6fd2b6aad713f52675073e9d58b38c53eee

---

### 65. Data Loss Prevention
**URL:** https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c7cbbb2a977ce39604bb9fcfe549d03a10facc131eeb42f01ea1345b3180f8a4

---

### 66. Sensitivity Labels
**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:240a866b8202dbbbd974cd8a6e613e3c260d06fb1484eae8fc09d4fb05d2b985

---

### 67. Sensitivity Labels for Sites
**URL:** https://learn.microsoft.com/en-us/purview/sensitivity-labels-teams-groups-sites
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f136bc0ffd732fefd6fabad2e16773e7d8359f58388e9fae0437dee1babb53c4

---

### 68. Audit Copilot Activities
**URL:** https://learn.microsoft.com/en-us/purview/audit-copilot
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:93d155d38a7f71845c945314abe23fdfd66385a9a07f1129095b0df8f5e1b700

---

### 69. DSPM for AI
**URL:** https://learn.microsoft.com/en-us/purview/ai-microsoft-purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e2bfad0a4236f04b93f6737dabc796ca0454599005aa3ec4f5e4647a911df14e

---

### 70. DSPM Considerations
**URL:** https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:5f069bb935e8548bb1b2cbc430b5f9d5a3ca4de727040db1bbc0b74715d8f78c

---

### 71. Communication Compliance
**URL:** https://learn.microsoft.com/en-us/purview/communication-compliance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a71f2e08c3a750e25447880ba3930d6bad00a282b8633600ddffcf8c65e642b4

---

### 72. Insider Risk Management
**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c9852af5fa11d541277854e85b4db62edd84ddf45070d5a72134ac1eb5131d3a

---

### 73. HR Data Connector
**URL:** https://learn.microsoft.com/en-us/purview/import-hr-data
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8db12e9dfebabc5f094c8ae99411f955903f3dc3db12af54a7d82fc17072edc8

---

### 74. Sensitive Information Types
**URL:** https://learn.microsoft.com/en-us/purview/sit-sensitive-information-type-learn-about
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a2ac8a6df00473b1720bda2469be035bdb672c54ecf6f6ace30af1740d0bb9db

---

### 75. Exact Data Match
**URL:** https://learn.microsoft.com/en-us/purview/sit-learn-about-exact-data-match-based-sits
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ee7dad5ed86dbe40d55c1ae7fc770c68b8f933eeee4d0397611388f9d008a74f

---

### 76. Trainable Classifiers
**URL:** https://learn.microsoft.com/en-us/purview/trainable-classifiers-learn-about
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fdecf428e41e22fb7c73a3c7bc760b99347da1fbe6276470c9c44682a0c2a109

---

### 77. Data Retention
**URL:** https://learn.microsoft.com/en-us/purview/retention
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:aaefb527bce6c1df62cc41941418696e90a03af63fadf44232cf91d4c84bd4a6

---

### 78. Retention Policies
**URL:** https://learn.microsoft.com/en-us/purview/create-retention-policies
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ea457d8405267250b1824faee1abd838257eccd75ee02a0d6e175640d8b18d28

---

### 79. Retention for SharePoint
**URL:** https://learn.microsoft.com/en-us/purview/retention-policies-sharepoint
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b8baf750cbde30ee9bbbeff2b1ee0dfe0879f9f5ef1a11ceb9e87ede752aa0d7

---

### 80. Disposition
**URL:** https://learn.microsoft.com/en-us/purview/disposition
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:54b9f79d5fc85f336611297e49aa8fb6f2a815d9c7b96a8c5f06e791ace09eab

---

### 81. SEC 17a-4 / Preservation Lock
**URL:** https://learn.microsoft.com/en-us/purview/retention-regulatory-requirements
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:767689dee9673a50f41d0d4f603f9aca28d12d9b60d844d954898bd4c31844e3

---

### 82. Records Management
**URL:** https://learn.microsoft.com/en-us/purview/records-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:05b1262f0f8017a925180bd7a3bf5c57accaecf7357905ea8a778be3cd607c12

---

### 83. Data Lifecycle Management
**URL:** https://learn.microsoft.com/en-us/purview/data-lifecycle-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:144606176d9b9d0f3bc5ebe0081f78c107869c6f6c14f83be71fdfc7dd9e785d

---

### 84. eDiscovery
**URL:** https://learn.microsoft.com/en-us/purview/ediscovery
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c9c7058545a3bda43c6c0686f99acd06ebcae99ad1dd07f95f4ecd332b31db01

---

### 85. Create Cases
**URL:** https://learn.microsoft.com/en-us/purview/ediscovery-create-and-manage-cases
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:7ce19106bca3d7aca62502859c89707ff4f4e03faedc198c1a05ac3f25c90e85

---

### 86. KeyQL Reference
**URL:** https://learn.microsoft.com/en-us/purview/ediscovery-keyword-queries-and-search-conditions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:61d772f7c0c5331b75e54986f4d1d690087a12aedecb4cdf5a90c443e01946e4

---

### 87. eDiscovery Holds
**URL:** https://learn.microsoft.com/en-us/purview/ediscovery-create-holds
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f0f701624f7724dc174c84d8582f03b4967860e9a278dbfef8fcef2149a26cbd

---

### 88. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:147212adc4393f13e6dad360984772926ab3696b56a973316ad352f08e53c470

---

### 89. Information Rights Management
**URL:** https://learn.microsoft.com/en-us/purview/encryption-sensitivity-labels
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ff55d8ba8acc1fe33c25b30c628ec8abb68560a9bd79ac08c2ccff1bff989032

---

### 90. Encryption
**URL:** https://learn.microsoft.com/en-us/purview/encryption
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b58645868f5b0897b3d9af1327796b66eb8baf42a332e749cfc2a1a02f3b367a

---

### 91. Activity Explorer
**URL:** https://learn.microsoft.com/en-us/purview/data-classification-activity-explorer
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e5db3c8e3ec432cab0a73e69f1ca98ddb28aa0aaaca0c01f25585157e8ae7d82

---

### 92. Compliance Manager
**URL:** https://learn.microsoft.com/en-us/purview/compliance-manager
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:dcadfc8baab12f1bf4b32800614209ea81083b5f9dcbddda90fd2ce3fa2e73f7

---

### 93. Conditional Access
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:c96f5a2efd719c88e6a21a69b8da6bead50f28a56953a4f0b61a117af52b3e7b

---

### 94. Conditional Access Policies
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-policies
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0a07640ad9b81d18d3b4a25f11c92f2f7fc1c6e7756a91bc6a852946732b0953

---

### 95. Authentication Contexts
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-cloud-apps#authentication-context
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0ab852477615756222d5bcebd2e2abd779dcdd32bf895bcd1a5e9ac65e797ec6

---

### 96. Session Controls
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-session-lifetime
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:803e017223fabbdda1bdc57bf240846f880c1d1f9f746e1f81b851c43edc8a77

---

### 97. Phishing-Resistant MFA
**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8a73d89092442fa1063070fbe3cb9d366cf8d237141c4ee2daa22197458e1d99

---

### 98. Authentication Methods
**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/overview-authentication
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:1ee6a66ebab2acb4151c75546758dbb22911e691d541dccd1c5a00e726ab4a1c

---

### 99. FIDO2 Security Keys
**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-authentication-passkeys-fido2
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:044989d624d0309f0f6012058143bb925508f3fa1e2458ab4e610f8e58357914

---

### 100. Role-Based Access Control
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/custom-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8ed2b8255241ce636bbc2e38bfd3ddecb312d948f1a806031bf2f2584ee62e6f

---

### 101. Admin Roles
**URL:** https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:bb0cd9b5ed8ca771e24b460c1d999bc1f94f79564d1fc6bc5215e64da9b07076

---

### 102. Access Reviews
**URL:** https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a440d9298cfbd378bb91c908979fe4d57d6e31ee880eaf99fbb314e541643b98

---

### 103. Create Access Review
**URL:** https://learn.microsoft.com/en-us/entra/id-governance/create-access-review
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8d2bfa09e4166a82946798368a6431ca60f05e6240d1cbfe7cde55fd900be724

---

### 104. Privileged Identity Management
**URL:** https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:631968768c37ee95de28691a4540d3d2349a924c28ec0f7cb3434be15b4fd671

---

### 105. Agent Identities for AI Agents
**URL:** https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0a0add0dab4dc911edadf00ab383526f598b901d330c0cc2943a48fd3b0c1cbc

---

### 106. SharePoint Admin Center
**URL:** https://learn.microsoft.com/en-us/sharepoint/sharepoint-admin-role
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:3ad0a504a24238f0b8ed484843658941acf3781b91d278c403540d520c03d937

---

### 107. Sharing Permissions
**URL:** https://learn.microsoft.com/en-us/sharepoint/modern-experience-sharing-permissions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:4b793c009cc51f5560d5eaedae0b8f5745a0b090a69f612f002baf0862069dd8

---

### 108. External Sharing
**URL:** https://learn.microsoft.com/en-us/sharepoint/external-sharing-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a14361049b16ad88208892576caefec6cae4c1baaf42c9bc5cc9191b41830389

---

### 109. Advanced Management
**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:26cfb3d2cd8bf1b4dafd455afcb0c9f5bf1a6bc3c2e2c992e4d0ea9927081eca

---

### 110. Information Barriers
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-sharepoint
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:34b0c84d839c07af903370763c429b4db1974b81974c345db64c7d648a545014

---

### 111. Agent Insights
**URL:** https://learn.microsoft.com/en-us/sharepoint/insights-on-sharepoint-agents
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:04c0b2658748f4e862810812ec97ae5040d7daee7d392e294f71dcbfc549e9b2

---

### 112. List Management
**URL:** https://learn.microsoft.com/en-us/sharepoint/control-lists
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:41d6d650d9b6f4f74bc63cf646ec3421a330f482e37667e8fe1adec2aefef8a3

---

### 113. Training Sites
**URL:** https://learn.microsoft.com/en-us/sharepoint/create-training-site
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:d02c13a997ba297b38b36dbc53e115bded46f0a5a021c387400b5d4f9f4e26b4

---

### 114. Versioning
**URL:** https://learn.microsoft.com/en-us/sharepoint/governance/versioning-content-approval-and-check-out-planning
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:3bd16f0c7f6bf8373266a887d1a817c3b6da3f4ae6065125f31dff969bd57acc

---

### 115. Retention for SharePoint
**URL:** https://learn.microsoft.com/en-us/purview/create-retention-policies#retaining-content-thats-in-sharepoint-sites
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ea457d8405267250b1824faee1abd838257eccd75ee02a0d6e175640d8b18d28

---

### 116. Integrated Apps
**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center?view=o365-worldwide
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:0651d2f41d526e173a8d34fe3f8f1580ad0f37a14c9eb712032265058d71b053

---

### 117. Service Health
**URL:** https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health?view=o365-worldwide
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:53189d12c108a5221f1e53a5ff948689130aa346da00dc325fe71b1f40d47f1e

---

### 118. Message Center
**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b32043d279e60fd262e2f3844f85ac1d07d48959517581df47841077b75489ed

---

### 119. Microsoft Sentinel
**URL:** https://learn.microsoft.com/en-us/azure/sentinel/overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b5e0d4b8912cc6c18591a5dc6672d01021fe65baab49b677bc9ac97dedeb3a35

---

### 120. Data Connectors
**URL:** https://learn.microsoft.com/en-us/azure/sentinel/connect-data-sources
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:322617c132e64b177201cfdaa811207d890f98e1e7ef81bea76cc14d0488127b

---

### 121. Built-in Analytics
**URL:** https://learn.microsoft.com/en-us/azure/sentinel/threat-detection
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e8af63a11d53052ebe1d283fb8e5cbaa2028c6e327b373d78d5a7ec7e2ebc393

---

### 122. Azure Key Vault
**URL:** https://learn.microsoft.com/en-us/azure/key-vault/general/overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:bddfe861ee5b3f0d56aca4481e6cdcf86f4b3f2748e6c305a9ef819a3674fcb0

---

### 123. Key Vault Private Endpoints
**URL:** https://learn.microsoft.com/en-us/azure/key-vault/general/private-link-service
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f65f0c2000ef5f0f173e868eb42b28b8fa8c7ea1d02b754fe80ade4a9e46080a

---

### 124. Azure Private Link
**URL:** https://learn.microsoft.com/en-us/azure/private-link/private-link-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b95776297464c5dc34bdb834a4a2c9b937130190af2a0150baea29f0d43eb8d2

---

### 125. Immutable Blob Storage
**URL:** https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:eebc3f88c42731c123eb6c091fb81d23273f0e43c8ec997a169a418ef01a6819

---

### 126. Azure Service Health
**URL:** https://learn.microsoft.com/en-us/azure/service-health/overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:110bf40552e4a6bee1843dcb2c901209f60afce8cedab0821718bb756ba8976a

---

### 127. Microsoft Purview Information Protection
**URL:** https://learn.microsoft.com/en-us/purview/information-protection
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:42b452d39b25979b0d4f922e05f90c25840c06968a5c825ede8366498b4d17b7

---

### 128. Responsible AI
**URL:** https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8e2849f843719e6b5f76e0a5c367d5b235d57cc6af217ab099ad9f461326ec30

---

### 129. AI Content Safety
**URL:** https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ec279db1d342f5c2ff28d52e162f7927b3f1431869bb14430518d7ffc54f0aa2

---

### 130. Cost Management
**URL:** https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/overview-cost-management
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:bb6527ac7ea876dbb6070ce2dea1816bf35aa5b60476a48f85bf1cb10162a69e

---

### 131. Azure Budgets
**URL:** https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f23b92dc7519a6e121b83f45cccae66169d6cc020573233abdeaa40d55c76246

---

### 132. Azure DevOps Test Plans
**URL:** https://learn.microsoft.com/en-us/azure/devops/test/overview?view=azure-devops
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:34efb8ff7908de6651b3469e4e99a28fdde6d09f98456d9f8e718c5b5d2edd98

---

### 133. Device Control
**URL:** https://learn.microsoft.com/en-us/defender-endpoint/device-control-overview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b1d7656e8ca9710d3c9eb1ea86bb11ad5f6dd16f893d429e884514909bed147d

---

### 134. Approval Workflows
**URL:** https://learn.microsoft.com/en-us/power-automate/get-started-approvals
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:4c1d1c5b8cffc2680fe28745f82ad55d0047cf828db79a3385c6df0e87484ee6

---

### 135. Scheduled Flows
**URL:** https://learn.microsoft.com/en-us/power-automate/run-scheduled-tasks
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e028cd9dce32b5f7b843bd866486c37b0e733889bd44245c007989eb39830726

---

### 136. Solution Checker
**URL:** https://learn.microsoft.com/en-us/power-apps/maker/data-platform/use-powerapps-checker
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:fbb969de14b82392837fd19dfb6398053f86a41298b0a8315c601053e061aa86

---

### 137. Testing Guidance
**URL:** https://learn.microsoft.com/en-us/power-apps/maker/plan-designer/plan-designer
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:092973b078f8639d4cb4a7561dcee7a6cc169f47f9d7834d641ec17a01b5f18b

---

### 138. Information Barriers in Teams
**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-teams
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a4d7982ecb4a6ff3b44309a64accb575463deb843a28a38757ed6e01285a0d45

---

### 139. Application Resources
**URL:** https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:310ad4050874c19a31afbb8520ea9ae3a258815f43e2b4a9a9a6f80bf8806ff9

---

### 140. Access Reviews API
**URL:** https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview?view=graph-rest-1.0
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:49320867abf0ef9ee118ef8ffe69b8ab56fd1038072743bd2092b79a71baf1d8

---

### 141. Governance Adoption
**URL:** https://learn.microsoft.com/en-us/power-bi/guidance/fabric-adoption-roadmap-governance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:93ccdb1b6686e92078908688d0d9e65e71425effc9cc7f3304592b049f160e00

---

### 142. Viva Learning Overview
**URL:** https://learn.microsoft.com/en-us/viva/learning/overview-viva-learning
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:9b9d0a5a2cd0b7f9abdfc2358de20b788f5c1a60e31945f673f39fbac3d81b25

---

### 143. Incident Response Planning
**URL:** https://learn.microsoft.com/en-us/security/operations/incident-response-planning
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ee8af3e6cd7e849d9e8f23b969dbe2fe5265d42f230065c8cb629b78e07e31a2

---

### 144. DLP Cmdlets
**URL:** https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpcompliancepolicy?view=exchange-ps
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:e2750a1b3d5c5460f5604a8f2ce1bee7a211d80e449a145da0b88c63c32c3a45

---

### 145. Management Activity API
**URL:** https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:6f6c592ed3219fdb6cbf94e5cbaa153bf90135ba3aab161c92eeb07b2e984267

---

### 146. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:d13e2d275b9ef91eb90f51766058f5fa7472852419bedf238d0596927ff2410e

---

### 147. Power Platform Licensing
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/pricing-billing-skus
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:213abf346a0eb5f0bd670375400408a8e744312a5688f758d6fd117fab3a10cd

---

### 148. Microsoft 365 Licensing
**URL:** https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview?view=o365-worldwide
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:ad756fd14c847de548c3e6ad0d98511118a5d49a35abc81cdc1752cd5d5d469f

---

### 149. M365 Licensing Guidance
**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-365-security-compliance-licensing-guidance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:2ad16c68adb19cbe6cc3c8496ba63d0f37070152a24ec962d2aef721f249f950

---

### 150. Copilot Studio Licensing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:f5a22621684884028869c16ede7e2e08a6109a2eaaa85ef2e4978a6aef9f452c

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