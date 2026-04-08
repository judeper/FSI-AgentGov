# Microsoft Learn Documentation Changes

**Run Date:** 2026-04-08
**Run Time:** 2026-04-08T07:23:38.439895+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 4 |
| MEDIUM Changes | 3 |
| Redirects | 14 |
| Errors | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | environment-groups-rules | MEDIUM | 2.2 | Review optional |
| 2 | insider-risk-management-activities | HIGH | 1.12 | Review and update |
| 3 | endpoint-dlp-learn-about | HIGH | 1.17 | Review and update |
| 4 | concept-conditional-access-cloud-apps | MEDIUM | 1.23 | Review optional |
| 5 | how-to-authentication-passkeys-fido2 | MEDIUM | None | Review optional |
| 6 | whats-new | HIGH | None | Review and update |
| 7 | microsoft-purview-service-description | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-activities
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**What Changed:**
```diff
--- +++ @@ -65,10 +65,14 @@ to review intelligently distilled user activity and risk pattern narratives.
 Use the
 Activity explorer tab
-to review a timeline of the associated potentially risky behavior and to identify all risk activities for the alert.
+to review a timeline of the associated potentially risky behavior, and to identify all risk activities for the alert.
 Use the
 Data risk graph
 to review connections and details about users and files for the alert.
+Tip
+If
+Content preview (preview)
+is available for the content within the alert, you can review relevant files from SharePoint, Exchange, and OneDrive for Business in Activity explorer to identify false positives, confirm that sensitive data is present, and quickly decide whether the alert warrants escalation.
 Act on the alert
 . You can either confirm and
 create a case
@@ -399,6 +403,23 @@ The
 Activity explorer
 tab is available for alerts in both dashboard views. It provides risk investigators and analysts with a comprehensive analytics tool that provides detailed information about alerts. With the Activity explorer, reviewers can quickly review a timeline of detected potentially risky activity and identify and filter all risk activities associated with alerts.
+Content preview (preview)
+For supported activities, investigators can preview related content directly within Activity explorer to quickly validate risk without creating a case. Content preview (preview) enables early triage by helping investigators determine whether an activity contains sensitive data, represents a false positive, or requires escalation to a full investigation. Content preview is supported for activities that involve accessing or transmitting content.
+Supported Content preview (preview) activities
+Content preview is supported for activities that involve accessing or transmitting content, including:
+SharePoint
+: File accessed, file download, full file sync download
+Exchange
+: Email sent (hygiene events), Data loss
```

---

### 2. Endpoint DLP

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Policy language)

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -568,39 +568,10 @@ Just-in-time protection blocks egress activities on these monitored files until policy evaluation completes successfully:
 Items that have never been evaluated.
 Items on which the evaluation has gone stale. These are previously evaluated items that haven't been reevaluated by the current, updated cloud versions of the policies.
-Before you can deploy just-in-time protection, you must first deploy Antimalware Client version 4.18.23080 or later.
-Note
-For machines with an outdated version of the Antimalware Client, we recommend disabling just-in-time protection by installing one of the following KBs:
-Windows 10 -
-KB5032278
-Windows 11 -
-KB5032288
-To enable Just-in-time protection in the Microsoft Purview Portal, select
-Settings
-in the left navigation pane, choose
-Just-in-time protection
-, and configure your desired settings.
-Choose which locations to monitor:
-Select
-Devices
-.
-Choose
-Edit
-.
-In the flyout pane, select the scope of accounts and distribution groups you want to apply just-in-time protection to. Keep in mind that, while policy evaluation is processing, Endpoint DLP blocks all egress activities for each user whose account is in the selected scope. Endpoint DLP audits the egress activities for all user accounts that are excluded (via the Exclude setting) or are otherwise not in scope.
-Just-in-time protection is supported on macOS devices running the three latest major versions.
-Fallback action in case of failure
-: This configuration specifies the enforcement mode that DLP should apply when the policy evaluation doesn't complete. No matter which value you select, the relevant telemetry shows in activity explorer.
-Tip
-Tips for maximizing user productivity:
-Configure and deploy your Endpoint DLP policies to your devices before enabling just-in-time protection to prevent unnecessarily blocking user activity during policy evaluation.
-Make sure to carefully configure your settings for egress activities. Just-in
```

---

### 3. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -54,6 +54,20 @@ : Updates to facilitate editing and managing glossary terms in Unified Catalog:
 Edit glossary terms in bulk
 Move multiple terms at once from one governance domain into another domain
+Data Loss Prevention
+Updated
+: Restructured the
+just-in-time (JIT) protection
+documentation. A new conceptual article,
+Learn about just-in-time protection
+, now covers JIT concepts, terms, supported activities, device compatibility, and includes a detailed JIT workflow diagram. The
+Get started with just-in-time protection
+article now focuses on deployment and configuration steps.
+Insider Risk Management
+In preview
+: Preview content while
+triaging alerts
+to quickly identify false positives, confirm the presence of sensitive data, and decide whether the alert warrants escalation.
 Sensitivity labels
 General availability (GA)
 :
@@ -503,72 +517,6 @@ : SharePoint document libraries can be configured for a sensitivity label to extend permissions to downloaded documents, and protect files from being copied or moved. For more information, see
 Configure SharePoint with a sensitivity label to extend permissions to downloaded documents
 . Microsoft 365 Copilot can access unopened files that are labeled with this configuration.
-October 2025
-Data Governance
-In preview
-:
-Unified Catalog API
-for general availability (GA) features in Unified Catalog.
-General availability (GA)
-:
-Data quality error record publishing to your cloud storage
-is now generally available in all supported Azure regions. Data engineers, data quality stewards, and analysts can review and correct data, as well as monitor continuous improvements by creating dashboards with
-Unified Catalog metadata
-and
-Data quality error records
-for their data governance and data quality teams. This feature helps Microsoft Purview Unified Catalog users not only measure and monitor data quality, but also improve it by enabling them to correct data quality error records and handle rule excepti
```

---

### 4. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -487,18 +487,31 @@ Graph requirements for accessing chat messages
 .
 Microsoft Purview Data Loss Prevention (DLP) for Microsoft 365 Copilot
-In Microsoft Purview, organizations can implement data loss prevention by defining and applying DLP policies. With a DLP policy, admins can identify, monitor, and automatically protect sensitive items across different locations. DLP for Microsoft 365 Copilot as a location allows organizations to identify sensitive content based on sensitivity labels and exclude them from Copilot processing.
+In Microsoft Purview, organizations can implement data loss prevention by defining and applying DLP policies. With a DLP policy, admins can identify, monitor, and automatically protect sensitive data across different locations. DLP for Microsoft 365 Copilot and Copilot Chat as a location allows organizations to identify and restrict the use of sensitive content in Copilot grounding and Copilot interactions based on sensitive information types and sensitivity labels.
 Using the
 Microsoft Purview portal
 , admins can configure DLP policies and scope Microsoft 365 Copilot as a location.
 Learn more about Microsoft 365 Copilot as a policy location
 .
 Feature
+Microsoft 365 Business Basic/Standard/Premium
+Microsoft 365 E3/A3/A1/G3/F3/F1
+Office 365 E3/E1/A3/A1/G3/G1/F3
 Microsoft 365 E5/A5, Microsoft Purview Suite/EDU/FLW and Microsoft Defender + Purview Suite FLW, Microsoft 365 E5/A5/F5 Information Protection and Governance
 Office 365 E5/A5
-Purview Data Loss Prevention (DLP) for Copilot
-Yes
-Yes
+Purview Data Loss Prevention (DLP) to restrict Copilot from processing files and emails
+No
+No
+No
+Yes
+Yes
+*Purview Data Loss Prevention (DLP) to safeguard prompts
+Yes*
+Yes*
+Yes*
+Yes*
+Yes*
+*Purview DLP for prompts is available to all users of M365 Copilot and Copilot Chat
 Microsoft Purview eDiscovery
 eDiscovery (Standard) enables you to create eDiscovery cases and assign eDiscovery managers to specific cases. eDiscovery ma
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Environment Group Rules
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules
**Classification:** MEDIUM (General content update)

---

### 2. Authentication Contexts
**URL:** https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-cloud-apps#authentication-context
**Classification:** MEDIUM (General content update)

---

### 3. FIDO2 Security Keys
**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/how-to-authentication-passkeys-fido2
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