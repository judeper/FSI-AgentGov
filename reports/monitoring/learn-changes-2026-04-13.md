# Microsoft Learn Documentation Changes

**Run Date:** 2026-04-13
**Run Time:** 2026-04-13T08:07:02.146404+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 6 |
| MEDIUM Changes | 4 |
| Redirects | 14 |
| Errors | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | advanced-connector-policies | CRITICAL | 1.4 | Monitor |
| 2 | wp-data-loss-prevention | HIGH | 1.28, 1.14, 3.7, 2.24, 2.7 | Review and update |
| 3 | dlp-connector-classification | CRITICAL | 1.14 | Monitor |
| 4 | ...en-us/connectors/connector-reference/ | MEDIUM | 1.4 | Review optional |
| 5 | security-overview | HIGH | 1.26, 1.8, 1.25 | Review and update |
| 6 | analytics-improve-agent-effectiveness | HIGH | None | Review and update |
| 7 | planned-features | MEDIUM | 1.4, 1.5, 3.8, 2.25, 2.17 | Review optional |
| 8 | dlp-policy-reference | HIGH | None | Review and update |
| 9 | private-link-service | HIGH | 1.20 | Review and update |
| 10 | whats-new | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. DLP Policies (Power Platform)

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 2.24: Control 2.24: Agent Feature Enablement and Restriction Governance
  - File: `controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md`
- Control 2.7: Control 2.7: Vendor and Third-Party Risk Management
  - File: `controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.28/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.25/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -28,66 +28,77 @@ Feedback
 Summarize this article for me
 Data policies are a critical aspect of maintaining data security and compliance within the Microsoft Power Platform ecosystem.
-You can create data policies that can act as guardrails to help reduce the risk of users from unintentionally exposing organizational data. A core component of Power Apps, Power Automate, and Microsoft Copilot Studio is the use of connectors to enumerate, populate, push, and pull data. Data policies in Power Platform admin center allow administrators to control access to these connectors in various ways to help reduce risk in your organization.
+Create data policies that act as guardrails to help reduce the risk of users unintentionally exposing organizational data. A core component of Power Apps, Power Automate, and Microsoft Copilot Studio is the use of connectors to enumerate, populate, push, and pull data. Power Platform admin center data policies allow administrators to control access to these connectors in various ways to help reduce risk in your organization.
 This overview describes some high-level concepts related to connectors and several important considerations to take into account when setting up your policies or making policy changes.
 Connectors
-Connectors, at their most basic level, are strongly typed representations of restful, application programming interfaces, also known as APIs. For example, the Power Platform API provides several operations related to functionality in Power Platform admin center.
-When wrapping the Power Platform API in to a connector, it becomes easier for makers and citizen developers to utilize the API in their low-code apps, workflows, and chatbots. For example, the Power Platform for Admins V2 connector is the representation of the Power Platform API and we see the 'Get Recommendations' action is simply drag and dropped on to the flow:
-There are several types of connectors mentioned in this article, and each has capabilities wi
```

---

### 2. Security

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/security/security-overview
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.25: Control 1.25: MIME Type Restrictions for File Uploads
  - File: `controls/pillar-1-security/1.25-mime-type-restrictions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.26/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -94,6 +94,11 @@ Preview features arenât meant for production use and might have restricted functionality. These features are subject to
 supplemental terms of use
 , and are available before an official release so that customers can get early access and provide feedback.
+Important
+Microsoft is actively working on updates to the
+Security
+area of Power Platform admin center. As part of this effort, we don't plan to invest in changes to the current preview implementation of logic or the security score calcualtion.
+Given that this functionality is in preview, behaviors may change as we continue to make changes. We recommend using the security score for evaluation purposes only at this time.
 The security score is calculated based on the security features that are turned on in your environment. It provides a measurement of your organizational security position for Microsoft Power Platform and Dynamics 365 workloads.
 Qualitative scale
 : The security score is shown on a qualitative scale that uses three assessment labels:

```

---

### 3. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -62,7 +62,7 @@ : Understanding when agent struggles to provide answers to user questions and how it uses knowledge sources can help you find ways to improve your agent's answer rate and quality.
 Tool use
 : Learning how often tools are used and how often they succeed can help you understand if those tools are useful and successful for users.
-Satisfaction
+Effectiveness
 : Reviewing user feedback helps you identify new user scenarios and issues, and making improvements based directly on what your users are asking for.
 You can view analytics for events that occurred in the last 90 days.
 Conversation outcomes
@@ -419,6 +419,78 @@ If the Response quality is
 Good
 or if the question wasn't sampled, the Reason parameter isn't assigned any value.
+Drill down to sessions
+Drill down to sessions to view specific sessions that contributed to a metric. This deeper view helps you understand the
+why
+and
+how
+behind top-level agent metrics and enables you to identify and investigate potential issues.
+Use the sessions list to analyze agent performance and investigate issues that lead to a session outcome (
+resolved
+,
+escalated
+,
+abandoned
+, or
+unengaged
+). For example, filter by channel and focus on low CSAT sessions to gain insight into why customers in those channels might be having a poor experience.
+To drill down to the session list window:
+From the
+Conversation outcomes
+panel, select
+See sessions
+to view all sessions for the analytic period.
+From the
+Conversation outcomes
+panel, select
+See details
+. This opens a side pane of further metrics on conversation session outcomes. Select on any highlighted metric plot to view a filter list of sessions.
+The session list is filtered based on the data point you drilled down on. This is reflected in the default filter settings above the session list. For instance, within the
+Conversation outcomes
+side pane, choosing the
+Resolved confirmed
+bar segment of the
+Resolved outcomes reasons
+bar tile
```

---

### 4. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -1742,6 +1742,11 @@ File size is greater than
 File type is
 Insider risk level for Adaptive Protection is
+URL contains text (preview)
+(Preview)
+The
+URL contains text
+condition detects when the URL of the unmanaged cloud app contains specified text strings. You can use it as a condition to scope DLP rules to specific URLs, or as an exception to exclude specific URLs from policy enforcement. For example, you can create a rule that blocks uploading sensitive data to any GitHub URL that doesn't contain your organization's name while allowing uploads to your organization's GitHub repositories. This condition is supported for browser and network detection and doesn't require devices to be onboarded to endpoint DLP.
 Important
 Encrypted files can't be inspected for sensitive info types or trainable classifiers.
 Conditions supported for Endpoints
@@ -2592,7 +2597,24 @@ Managed cloud apps
 - Not supported
 Unmanaged cloud apps
-- Not supported
+- (Preview) Supported for email notifications. See
+Inline email notifications for browser and network
+.
+Email notifications for browser and network (preview)
+When a DLP rule is configured for unmanaged cloud apps (browser and network), you can enable email notifications to notify end users via email when their activity is blocked. This is different from the inline pop-up notifications that appear directly in the browser, such as in Microsoft Edge for Business. Email notifications are particularly useful for integrations that don't support pop-up notifications, such as the Android Global Secure Access integration.
+You can configure email notifications for:
+The person who performed the blocked activity.
+Additional recipients, such as admins or compliance officers.
+Email notification batching
+Email notifications are batched to prevent a flood of communications:
+The
+first
+policy match sends an email notification immediately (within seconds of the activity).
+Any additional policy matches within a rolling
+10
```

---

### 5. Key Vault Private Endpoints

**URL:** https://learn.microsoft.com/en-us/azure/key-vault/general/private-link-service
**Section:** Azure Services
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 1.20: Control 1.20: Network Isolation and Private Connectivity
  - File: `controls/pillar-1-security/1.20-network-isolation-private-connectivity.md`

**What Changed:**
```diff
--- +++ @@ -108,53 +108,53 @@ If there are any private endpoint connections you want to reject, whether it's a pending request or existing connection, select the connection and select the "Reject" button.
 Establish a private link connection to Key Vault using CLI (Initial Setup)
 az login # Login to Azure CLI
-az account set --subscription {SUBSCRIPTION ID} # Select your Azure Subscription
-az group create -n {RESOURCE GROUP} -l {REGION} # Create a new Resource Group
+az account set --subscription <subscription-id> # Select your Azure Subscription
+az group create -n <resource-group> -l <location> # Create a new Resource Group
 az provider register -n Microsoft.KeyVault # Register KeyVault as a provider
-az keyvault create -n {VAULT NAME} -g {RG} -l {REGION} --enable-rbac-authorization true --enable-purge-protection true # Create a Key Vault
-az keyvault update -n {VAULT NAME} -g {RG} --default-action deny # Turn on Key Vault Firewall
-az network vnet create -g {RG} -n {vNet NAME} -location {REGION} # Create a Virtual Network
+az keyvault create -n <vault-name> -g <resource-group> -l <location> --enable-rbac-authorization true --enable-purge-protection true # Create a Key Vault
+az keyvault update -n <vault-name> -g <resource-group> --default-action deny # Turn on Key Vault Firewall
+az network vnet create -g <resource-group> -n <vnet-name> -location <location> # Create a Virtual Network
 
  # Create a Subnet
-az network vnet subnet create -g {RG} --vnet-name {vNet NAME} --name {subnet NAME} --address-prefixes {addressPrefix}
+az network vnet subnet create -g <resource-group> --vnet-name <vnet-name> --name <subnet-name> --address-prefixes <address-prefix>
 
  # Disable Virtual Network Policies
-az network vnet subnet update --name {subnet NAME} --resource-group {RG} --vnet-name {vNet NAME} --disable-private-endpoint-network-policies true
+az network vnet subnet update --name <subnet-name> --resource-group <resource-group> --vnet-name <vnet-name> --disable-private-e
```

---

### 6. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -43,6 +43,11 @@ Roadmap
 for data security and risk and compliance solutions.
 April 2026
+Collection Policies
+Preview
+: Collection policies support
+sensitivity labels as a condition
+for scoping detection to items with specific sensitivity labels applied. This condition is supported with browser and network cloud apps detection.
 Data Governance
 General availability (GA)
 : Now rolling out, the
@@ -68,6 +73,15 @@ : Preview content while
 triaging alerts
 to quickly identify false positives, confirm the presence of sensitive data, and decide whether the alert warrants escalation.
+Data Loss Prevention
+Preview
+: DLP policies for unmanaged cloud apps support a new
+URL contains text
+condition that detects when the URL of the cloud app contains specified text strings. You can use it as a condition to scope DLP rules to specific URLs, or as an exception to exclude specific URLs from policy enforcement.
+Preview
+:
+Email notifications for browser and network DLP
+rules notify end users via email when their activity is blocked. Notifications use a rolling 10-minute batching window to prevent excessive emails.
 Sensitivity labels
 General availability (GA)
 :
@@ -149,6 +163,12 @@ : Use the new
 Advanced review set explorer
 to query review set data with Kusto Query Language (KQL). Build advanced queries with complex filtering, pattern-based text extraction, and data visualization to analyze and find key information in your review sets.
+New
+: Configure
+sampling options
+when adding search results to a review set in eDiscovery. Choose confidence-based or percentage-based sampling to add a statistically representative subset of search results instead of all items. Completing the
+Generate statistics
+process is required to enable sampling.
 Insider Risk Management
 In preview
 : Disable content download to create cases without content to reduce triage time. To get started, see

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Advanced Connector Policies
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Classification:** CRITICAL (Deprecation notice)

---

### 2. Connector Classification
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/dlp-connector-classification
**Classification:** CRITICAL (Deprecation notice)

---

### 3. Connector Reference
**URL:** https://learn.microsoft.com/en-us/connectors/connector-reference/
**Classification:** MEDIUM (General content update)

---

### 4. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage | https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/entra/agent-id/identity-professional/microsoft-entra-agent-identities-for-ai-agents | https://learn.microsoft.com/en-us/entra/agent-id/what-is-microsoft-entra-agent-id |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-addins-in-the-admin-center?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health | https://learn.microsoft.com/en-us/microsoft-365/enterprise/view-service-health?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center | https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide |
| https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai | https://learn.microsoft.com/en-us/azure/machine-learning/concept-responsible-ai?view=azureml-api-2 |
| https://learn.microsoft.com/en-us/azure/devops/test/overview | https://learn.microsoft.com/en-us/azure/devops/test/overview?view=azure-devops |
| https://learn.microsoft.com/en-us/graph/api/resources/application | https://learn.microsoft.com/en-us/graph/api/resources/application?view=graph-rest-1.0 |
| https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview | https://learn.microsoft.com/en-us/graph/api/resources/accessreviewsv2-overview?view=graph-rest-1.0 |
| https://learn.microsoft.com/en-us/powershell/module/exchange/new-dlpcompliancepolicy | https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/new-dlpcompliancepolicy?view=exchange-ps |
| https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview | https://learn.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-overview?view=o365-worldwide |

---

## Errors

- **Enhanced Admin Controls for Agent Security [Preview]** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/enhanced-admin-controls-agent-security
- **Agentic Center of Enablement [Preview]** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/automate-governance-agentic-center-enablement
- **Agent Suggestions from M365 Copilot [Preview]** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/get-agent-suggestions-based-work

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*