# Microsoft Learn Documentation Changes

**Run Date:** 2026-04-15
**Run Time:** 2026-04-15T07:49:50.874340+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 16 |
| MEDIUM Changes | 5 |
| Redirects | 14 |
| Errors | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | advanced-connector-policies | CRITICAL | 1.4 | Monitor |
| 2 | wp-data-loss-prevention | HIGH | 1.28, 1.14, 3.7, 2.24, 2.7 | Review and update |
| 3 | dlp-connector-classification | CRITICAL | 1.14 | Monitor |
| 4 | ...en-us/connectors/connector-reference/ | CRITICAL | 1.4 | Monitor |
| 5 | security-overview | HIGH | 1.26, 1.8, 1.25 | Review and update |
| 6 | analytics-improve-agent-effectiveness | HIGH | None | Review and update |
| 7 | planned-features | MEDIUM | 1.4, 1.5, 3.8, 2.25, 2.17 | Review optional |
| 8 | dlp-policy-reference | HIGH | None | Review and update |
| 9 | audit-solutions-overview | HIGH | 1.28, 1.27, 1.7, 1.6, 4.5 | Review and update |
| 10 | audit-copilot | HIGH | None | Review and update |
| 11 | audit-log-retention-policies | HIGH | 1.7, 3.14 | Review and update |
| 12 | audit-search | HIGH | None | Review and update |
| 13 | import-hr-data | HIGH | 1.12 | Review and update |
| 14 | information-barriers | HIGH | 1.22 | Review and update |
| 15 | concept-conditional-access-cloud-apps | HIGH | 1.23 | Review and update |
| 16 | how-to-authentication-passkeys-fido2 | HIGH | None | Review and update |
| 17 | information-barriers-sharepoint | HIGH | None | Review and update |
| 18 | private-link-service | HIGH | 1.20 | Review and update |
| 19 | information-barriers-teams | HIGH | None | Review and update |
| 20 | whats-new | HIGH | None | Review and update |
| 21 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

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

### 5. Audit Logging

**URL:** https://learn.microsoft.com/en-us/purview/audit-solutions-overview
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -190,10 +190,17 @@ Before you get started, review the
 subscription requirements
 for Audit (Standard) and Audit (Premium).
-Training
-Training your security operations team, IT administrators, and compliance investigators in the fundamentals for Audit (Standard) and Audit (Premium) can help your organization get started more quickly using auditing to help with your investigations. Microsoft Purview provides the following resource to help these users in your organization get started with auditing:
+Next steps
+Tip
+Training your security operations team, IT administrators, and compliance investigators in Audit (Standard) and Audit (Premium) can help your organization get started more quickly. For more information, see
 Describe the eDiscovery and audit capabilities of Microsoft Purview
 .
+Get started with auditing solutions
+: Walk through the setup steps to enable Audit (Standard) or Audit (Premium) in your organization.
+Search the audit log
+: Run your first audit log search to find user and admin activities.
+Manage audit log retention policies
+: Create custom retention policies to keep audit records beyond the default period.
 Feedback
 Was this page helpful?
 Yes

```

---

### 6. Audit Copilot Activities

**URL:** https://learn.microsoft.com/en-us/purview/audit-copilot
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -558,6 +558,13 @@ value or set of values, first search and export all relevant Copilot audit logs by filtering by operation name. From the exported search results, apply a filter on the
 AppIdentity
 property offline.
+Next steps
+Search the audit log
+: Run targeted searches for Copilot and AI application activities in the audit log.
+Manage audit log retention policies
+: Create retention policies to preserve Copilot audit records for your required period.
+Export, configure, and view audit log records
+: Export Copilot activity records for detailed analysis or compliance reporting.
 Feedback
 Was this page helpful?
 Yes

```

---

### 7. Audit Log Retention

**URL:** https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 3.14: Control 3.14: Agent 365 Observability SDK and Custom Agent Telemetry
  - File: `controls/pillar-3-reporting/3.14-agent-365-observability-sdk.md`

**What Changed:**
```diff
--- +++ @@ -47,6 +47,7 @@ property (which is the service in which the activity occurred). Audit records for all other activities are retained for 180 days by default or you can change the retention to a different duration using a custom retention policy.
 Note
 The default audit log retention policy only applies to audit records for activity performed by users who are assigned an Office 365 or Microsoft 365 E5 license or have a Microsoft Purview Suite (formerly known as Microsoft 365 E5 Compliance) or E5 eDiscovery and Audit add-on license. If you have non-E5 users or guest users in your organization, their corresponding audit records are retained for 180 days.
+The default retention period for audit records varies by license type and when the records were generated.
 Important
 The default retention period for Audit (Standard) changed from 90 days to 180 days. Audit (Standard) logs generated before October 17, 2023 are retained for 90 days. Audit (Standard) logs generated on or after October 17, 2023 follow the new default retention of 180 days.
 Before you create an audit log retention policy
@@ -92,7 +93,7 @@ : The audit record type the policy applies to. If you leave this property blank, the policy applies to all record types. You can select a single record type or multiple record types:
 If you select a single record type, the
 Activities
-field is dynamically displayed. Use the drop-down list to select activities from the selected record type to apply the policy to. If you don't choose specific activities, the policy applies to all activities of the selected record type.
+field is dynamically displayed. Use the drop-down list to select activities from the selected record type to apply the policy to. If you don't select specific activities, the policy applies to all activities of the selected record type.
 If you select multiple record types, you don't have the ability to select activities. The policy applies to all activities of the selected record types.
 Dur
```

---

### 8. Search the Audit Log

**URL:** https://learn.microsoft.com/en-us/purview/audit-search
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**What Changed:**
```diff
--- +++ @@ -82,7 +82,7 @@ The default retention period for Audit (Standard) changed from 90 days to 180 days. Audit (Standard) logs generated before October 17, 2023 are retained for 90 days. Audit (Standard) logs generated on or after October 17, 2023 follow the new default retention of 180 days.
 Note
 Even when mailbox auditing on by default is turned on, you might notice that mailbox audit events for some users aren't found in audit log searches in the Microsoft Purview portal or via the Office 365 Management Activity API. For more information, see
-More information about mailbox audit logging
+Mailbox audit logging
 .
 To turn off audit log search for your organization, run the following command in Exchange Online PowerShell:
 Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $false
@@ -176,7 +176,7 @@ .
 Enter
 SPOIBIsEnabled,SPOIBIsDisabled
-in operation search field. We recommend copying and pasting the operation names directly from the article to the operation search field to ensure that they're entered correctly and without typos.
+in operation search field. Copy and paste the operation names directly from the article to the operation search field to ensure that they're entered correctly and without typos.
 Record types
 : Select the drop-down list to display the record types for audited activities that you can search for. You can select one or more record types to search for. To search for a record type in the list, use the search box over the list.
 Specific
@@ -193,7 +193,7 @@ Search name
 : Enter in a custom name for your search job. This name is used to identify your search job in the search job history. If you don't enter a name, the search job is automatically named using a combination of the date and time defined for the search and other defined search criteria values.
 Users
-: Select this field and choose the names one or more users to display search results for. The audit log entries for the selected activity performed by the users you se
```

---

### 9. HR Data Connector

**URL:** https://learn.microsoft.com/en-us/purview/import-hr-data
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**What Changed:**
```diff
--- +++ @@ -224,7 +224,7 @@ Note
 *
 This column is mandatory. If a mandatory column is missing, the CSV file isn't validated and other data in the file isn't imported.
-We recommend that you create an HR connector that only imports employee profile data. For this connector, frequently refresh the employee profile data, preferably every 15 to 20 days. Employee profile records are deleted if you don't update them in the past 30 days.
+Create an HR connector that only imports employee profile data. For this connector, frequently refresh the employee profile data, preferably every 15 to 20 days. Employee profile records are deleted if you don't update them in the past 30 days.
 Determining how many CSV files to use for HR data
 In Step 3, you can choose to create separate connectors for each HR data type or a single connector for all data types. You can use separate CSV files that contain data for one HR scenario (like the examples of the CSV files described in the previous sections). Alternatively, you can use a single CSV file that contains data for two or more HR scenarios. Here are some guidelines to help you determine how many CSV files to use for HR data.
 If the insider risk management policy that you want to implement requires multiple HR data types, consider using a single CSV file that contains all the required data types.
@@ -293,7 +293,7 @@ , then select
 Add connector
 .
-From the list, choose
+From the list, select
 HR (preview)
 .
 On the
@@ -576,7 +576,7 @@ .
 If needed, you can update the flow to create triggers based on file availability and modification events on SharePoint and other data sources supported by Power Automate Flows.
 Existing HR connectors
-On December 13, 2021, we released the employee profile data scenario for HR connectors. If you created an HR connector before this date, we migrate the existing instances or your organization's HR connectors so your HR data continues to be imported to the Microsoft cloud. You don't have to do anythi
```

---

### 10. Information Barriers

**URL:** https://learn.microsoft.com/en-us/purview/information-barriers
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.22: Control 1.22: Information Barriers for AI Agents
  - File: `controls/pillar-1-security/1.22-information-barriers.md`

**What Changed:**
```diff
--- +++ @@ -137,13 +137,11 @@ in Exchange Online.
 Ready to get started?
 Get started with Information Barriers
-Manage IB policies
+: Define segments and create your first IB policies.
+Information Barriers attributes
+: Review the Microsoft Entra attributes available for defining user segments.
 Use multi-segment support in Information Barriers
-See the attributes that can be used for IB policies
-Information Barriers in Microsoft Teams
-Information Barriers in SharePoint
-Information Barriers in OneDrive
-SharePoint & OneDrive insights report
+: Assign users to multiple segments for complex organizational scenarios.
 Feedback
 Was this page helpful?
 Yes

```

---

### 11. Authentication Contexts

**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-cloud-apps#authentication-context
**Section:** Microsoft Entra ID
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.23: Control 1.23: Step-Up Authentication for AI Agent Operations
  - File: `controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md`

**What Changed:**
```diff
--- +++ @@ -267,6 +267,9 @@ New Conditional Access behavior when an ALL resources policy has a resource exclusion
 The scopes listed in the previous section are now evaluated as directory access and mapped to Azure AD Graph (resource: Windows Azure Active Directory, ID: 00000002-0000-0000-c000-000000000000) for Conditional Access evaluation purposes.
 Conditional Access policies that target All resources with one or more resource exclusions, or policies that explicitly target Azure AD Graph, are enforced in user sign-in flows where the client application requests only these scopes. There is no change in behavior when an application requests any additional scope beyond those listed above.
+For guidance on assessing impact, identifying affected applications, and retaining legacy behavior, see
+Improved enforcement for policies with resource exclusions
+.
 Note
 The
 Azure AD Graph retirement

```

---

### 12. FIDO2 Security Keys

**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-authentication-passkeys-fido2
**Section:** Microsoft Entra ID
**Classification:** HIGH (Policy language)

**What Changed:**
```diff
--- +++ @@ -36,7 +36,10 @@ Support for FIDO2 authentication with Microsoft Entra ID
 .
 Note
-Microsoft Entra ID currently supports synced passkeys and device-bound passkeys stored on FIDO2 security keys and in Microsoft Authenticator. Passkeys (FIDO2) are available in all Microsoft Entra ID editions, including Microsoft Entra ID Free. No extra licenses are required. For more information, see
+Microsoft Entra ID currently supports:
+synced passkeys
+device-bound passkeys stored on FIDO2 security keys and in Microsoft Authenticator
+Passkeys (FIDO2) are available in all Microsoft Entra ID editions, including Microsoft Entra ID Free. No extra licenses are required. For more information, see
 Passkeys (FIDO2) authentication method in Microsoft Entra ID
 .
 Get started

```

---

### 13. Information Barriers

**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-sharepoint
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -141,7 +141,7 @@ Allow apps running in app-only mode to access IB sites
 Many organizations use applications running in an app-only context in their organization. To allow these apps running in app-only mode to access IB protected sites, SharePoint admins can enable the opt-in capability.
 Important
-Information Barriers policies might impact the applications accessing sites in app-only mode. We recommend that you enable the policy and then test the experience for the apps used in your organization.
+Information Barriers policies might impact the applications accessing sites in app-only mode. Enable the policy and then test the experience for the apps used in your organization.
 To enable applications running in app-only mode to access IB sites, run the following command:
 Set-SPOTenant -AppBypassInformationBarriers $true
 If you enable Teams Meeting Recording or EDU Assignment application in your organization, run the following command to allow these applications to interact with IB protected sites:
@@ -179,7 +179,7 @@ .
 Connect to SharePoint Online as a Global Administrator or
 SharePoint Administrator
-in Microsoft 365. To learn how, see
+in Microsoft 365. For more information, see
 Getting started with SharePoint Online Management Shell
 .
 Run the following command to enable Information Barriers in SharePoint and OneDrive:
@@ -257,7 +257,7 @@ .
 Connect to SharePoint Online as a
 Global Administrator or SharePoint Administrator
-in Microsoft 365. To learn how, see
+in Microsoft 365. For more information, see
 Getting started with SharePoint Online Management Shell
 .
 Run the following command:
@@ -458,12 +458,15 @@ Open
 mode sites, run the following command:
 Set-SPOTenant -ShowPeoplePickerGroupSuggestionsForIB $true
-Resources
-Learn about Information Barriers
-Get started with Information Barriers
-Manage Information Barriers policies
-Information Barriers in Microsoft Teams
-Information Barriers in OneDrive
+Next steps
+Use Information Barriers
```

---

### 14. Key Vault Private Endpoints

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

### 15. Information Barriers in Teams

**URL:** https://learn.microsoft.com/en-us/purview/information-barriers-teams
**Section:** Microsoft Teams
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -105,7 +105,7 @@ Guests in Teams
 : IB policies apply to guests in Teams, too. If guests need to be discoverable in your organization's global address list, see
 Manage guest access in Microsoft 365 Groups
-. Once guests are discoverable, you can
+. After guests are discoverable, you can
 define IB policies
 .
 How policy changes impact existing chats
@@ -219,18 +219,18 @@ Teams Town hall
 for a smoother experience.
 Users can't join channel meetings
-: If you enable IB policies, users can't join channel meetings if they're not a member of the team. The root cause is that IB checks rely on whether users can be added to a meeting chat roster, and only when they can be added to the roster are they allowed to join the meeting. The chat thread in a channel meeting is available to Team/Channel members only, and non-members can't see or access the chat thread. If you enable IB for the organization and a non-team member attempts to join a channel meeting, that user isn't allowed to join the meeting. However, if you don't enable IB for the organization and a nonteam member attempts to join a channel meeting, the user is allowed to join the meeting but they won't see the chat option in the meeting.
+: If you enable IB policies, users can't join channel meetings if they're not a member of the team. The root cause is that IB checks rely on whether users can be added to a meeting chat roster, and only when they can be added to the roster are they allowed to join the meeting. The chat thread in a channel meeting is available to Team/Channel members only, and non-members can't see or access the chat thread. If you enable IB for the organization and a non-team member attempts to join a channel meeting, that user isn't allowed to join the meeting. However, if you don't enable IB for the organization and a nonteam member attempts to join a channel meeting, the user is allowed to join the meeting but they don't see the chat option in the meeting.
 IB policies don't work fo
```

---

### 16. Purview What's New

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
@@ -68,11 +73,39 @@ : Preview content while
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
+eDiscovery
+Updated
+: The
+maximum number of review sets per case
+has increased from 20 to 100 for eDiscovery with premium feature support.
+New
+: The
+Advanced review set explorer (preview)
+includes a new
+left navigation pane
+to browse the review set schema, insert KQL operators, and run sample queries, and a new
+Getting started tab
+with basic and advanced query templates to help you build queries faster.
 Sensitivity labels
 General availability (GA)
 :
 Auto-labeling policies
 introduce a new flow where you must decide whether to automatically apply a sensitivity label, or remove a label when the configured conditions apply for files in SharePoint and OneDrive. When you chose to automatically apply a sensitivity label, you can now optionally choose to always overriding an existing label that has a lower priority label, even if it was m
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
**Classification:** CRITICAL (Deprecation notice)

---

### 4. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)

---

### 5. Copilot Studio Licensing
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
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