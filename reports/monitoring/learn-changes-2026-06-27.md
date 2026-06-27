# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-27
**Run Time:** 2026-06-27T08:37:50.164031+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 4 |
| HIGH Changes | 9 |
| MEDIUM Changes | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | HIGH | 2.4 | Update portal-walkthrough |
| 2 | analytics-improve-agent-effectiveness | MEDIUM | None | Update portal-walkthrough |
| 3 | human-in-the-loop | HIGH | 2.17, 2.12 | Review and update |
| 4 | dlp-create-deploy-policy | HIGH | 1.5 | Update portal-walkthrough |
| 5 | dlp-policy-reference | HIGH | 1.5 | Review and update |
| 6 | insider-risk-management-activities | HIGH | 1.12 | Update portal-walkthrough |
| 7 | ...e-a-custom-sensitive-information-type | HIGH | 1.13 | Review and update |
| 8 | sit-create-a-keyword-dictionary | HIGH | 1.13 | Review and update |
| 9 | endpoint-dlp-getting-started | HIGH | 1.17 | Review and update |
| 10 | dlp-configure-endpoint-settings | HIGH | 1.17 | Review and update |
| 11 | restricted-content-discovery | HIGH | 4.7, 4.1, 4.6, 1.3, 1.14 | Review and update |
| 12 | track-and-revoke-admin | HIGH | None | Review and update |
| 13 | microsoft-purview-service-description | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:3433cf21c161b9ec033ebb941badb43e6d7687f3942f65da62cf4f63ab6fa5b8

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
@@ -203,6 +205,8 @@ For instructions on retrieving the current IP ranges, see
 What are the outbound IP ranges for my Finance and Operations environment?
 .
+Can I enable SSDR on a sandbox environment in Dynamics 365 Finance & Operations?
+No. Self-Service Dis
```

---

### 2. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:d9264fc1863e88d5b74a7eaceafcfa1c4b31a2791365c73b5ae6dbed78b4bef5

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -60,7 +60,11 @@ Custom metrics
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

### 3. Create DLP Policies

**URL:** https://learn.microsoft.com/en-us/purview/dlp-create-deploy-policy
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:9e8a859bb89f1655cf1a0f183fead66ebf8acee5da378777b7179f49ba9356b8

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -23,9 +23,9 @@ Feedback
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
+The following scenarios show how to create DLP policies for inline web traffic.
 Help prevent sharing via Microsoft Edge for Business to unmanaged AI apps from managed devices
 Help Prevent
```

---

### 4. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-activities
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:5cc026b9eb931a07700577c273fcae0e18b3e9ff3553c14e60d32504d0b9ee82

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -37,7 +37,7 @@ Investigate and act on alerts in Insider Risk Management by following these steps:
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
@@ -107,7 +109,7 @@ You can also use the
 standalone version of Microsoft Security Copilot to investigate Insider Risk Management, Microsoft Purview Data Loss Prevention (DLP), and Microsoft Defender XDR alerts
 .
-Spotlight (preview)
+Use Spotlight to prioritize alerts (preview)
 The alert
 Spotlight
 on the
@@ -161,8 +163,10 @@ For an overview of how alerts provide details, context, and related content for risky activity and how to make your investigation process more effective, see the
 Insider Risk Management Alerts Triage Experience video
 .
-Agent su
```

---

## HIGH: Control Review Recommended

### 1. Human-in-the-Loop Workflows

**URL:** https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:d8a8b43d52a9f25eb563ecb39bbb2b16f87c203cd3420728d2d71a5841bec749

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

**What Changed:**
```diff
--- +++ @@ -248,7 +248,13 @@ .
 When a checkpoint is created, pending requests are also saved as part of the checkpoint state. When you restore from a checkpoint, any pending requests will be re-emitted as
 RequestInfoEvent
-objects, allowing you to capture and respond to them. You cannot provide responses directly during the resume operation - instead, you must listen for the re-emitted events and respond using the standard response mechanism.
+objects, allowing you to capture and respond to them. You can also resume from a checkpoint and provide responses in the same call by passing both
+checkpoint_id
+and
+responses
+to
+workflow.run(...)
+.
 Next Steps
 Learn about sequential orchestration with HITL
 .

```

---

### 2. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:2d354edffebf195a94a4bc9d446fdfb46d771b442e69fc0857a4312059b55741

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**What Changed:**
```diff
--- +++ @@ -917,7 +917,7 @@ -
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

### 3. Custom SITs

**URL:** https://learn.microsoft.com/en-us/purview/sit-create-a-custom-sensitive-information-type
**Section:** Microsoft Purview
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:5919db88989c88c659a897672d64eb15e4cc9f6ebcb9f27199142c5ab14890a5

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -96,11 +96,36 @@ Sensitive Information Type regular expression validators
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

### 4. Keyword Dictionaries

**URL:** https://learn.microsoft.com/en-us/purview/sit-create-a-keyword-dictionary
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:93a008a9b303406b867fc14560afdbeb8d509940710c8c4f236a4fb7f59338b4

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**What Changed:**
```diff
--- +++ @@ -25,13 +25,13 @@ Microsoft Purview can identify, monitor, and protect your sensitive items. Identifying sensitive items sometimes requires looking for keywords, particularly when identifying generic content (such as healthcare-related communication), or inappropriate or explicit language. Although you can create keyword lists when you
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
-Most commonly you compile your keywords for your dictionary in a file, such as a .csv or .txt list. You upload the dictionary file into a SIT during creation or editing or import them via a PowerShell cmdlet. Alternately, you can start from an existing or from an
```

---

### 5. Onboard Devices

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-getting-started
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:a45663f0a707099feed8ba1dfb217d96388b2995457b1ca5e6abda747a28d617

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -46,7 +46,7 @@ , ensure those users or devices or both are explicitly excluded from the policy. Failure to do so may lead to unintended policy enforcement behavior.
 Configure proxy on the Windows 10 or Windows 11 device
 If you're onboarding Windows 10 or Windows 11 devices, check to make sure that the device can communicate with the cloud DLP service. For more information, see,
-Configure device proxy and internet connection settings for Information Protection
+Configure device proxy and internet connection settings for Microsoft Purview Endpoint DLP
 .
 Windows 10 and Windows 11 Onboarding procedures
 For a general introduction to onboarding Windows devices, see:

```

---

### 6. Configure Settings

**URL:** https://learn.microsoft.com/en-us/purview/dlp-configure-endpoint-settings
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:a9d5db1363243e0517ef7d892bea405357d2f6ec0b1bc0659b60b6d975fff970

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -47,7 +47,7 @@ Microsoft Purview Information Protection Support in Acrobat
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
-When you turn on this feature, users can work on files - including files other than Office and PDF files - that have sensitivity labels applying access control settings in an unencrypted state, on their devices. Endpoint DLP continues to monitor and enforce access control and label-based protections on these files even in an unencrypted state. It automatically encrypts them before they're transferred outside from a user's device. For more information about this feature, see
+When you turn on advanced label-based protection, users can work on files - including fil
```

---

### 7. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:749895a286a6df590f1bd8a33536f33cd92f68f958ff28ffb8a376932fb07d6a

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
--- +++ @@ -22,108 +22,166 @@ Restrict discovery of SharePoint sites and content
 Feedback
 Summarize this article for me
-For organizations onboarding to Microsoft 365 Copilot, maintaining strong data governance controls for SharePoint content is critical to deploying Copilot in a safe manner. Sites identified with the highest risk of oversharing can use Restricted Content Discovery to protect content while taking time to ensure that permissions are accurate and well-managed.
-With Restricted Content Discovery, organizations can limit the ability of end users to search for files from specific SharePoint sites. Enabling Restricted Content Discovery for each site prevents the sites from surfacing in organization-wide search and Microsoft 365 Copilot Business Chat, unless a user had a recent interaction.
-Restricted Content Discovery is a site-level setting that needs to be propagated to the search index, a large number of transactions could lead to a long queue in the ingestion pipeline and higher update latency times.
-While child content is hidden by default, users in your organization can still discover files they own or recently interacted with. End users can still find relevant content they need for their day-to-day tasks, even if Restricted Content Discovery is applied to the parent site.
-Restricted Content Discovery doesn't affect searches originating from a site context or other intelligent features such as Microsoft 365 Feed and Recommendations.
+Organizations preparing for Microsoft 365 Copilot often need time to review SharePoint sites, validate permissions, and implement governance controls before making content broadly discoverable. Restricted Content Discovery (RCD) helps you limit discovery of content from specific SharePoint sites while those reviews are taking place.
+When you enable Restricted Content Discovery for a site, content from that site doesn't appear in organization-wide search and Microsoft 365 Copilot experiences unless a user recently 
```

---

### 8. Track and Revoke Documents

**URL:** https://learn.microsoft.com/en-us/purview/track-and-revoke-admin
**Section:** Azure Services
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:bc5402c65142288416441f1cf6d638f86cb45c08aeac70a82a85fd8897774f9a

**What Changed:**
```diff
--- +++ @@ -24,7 +24,9 @@ Summarize this article for me
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
+cmdlet to search for a document using the filename or the email address of the user who applied protection.
 For example;
 
```

---

### 9. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:c9327a99468b1c1d5368abf75c9352ae0ae06cf2982897f12869a8963703e9eb

**What Changed:**
```diff
--- +++ @@ -511,7 +511,9 @@ eDiscovery (Standard) enables you to create eDiscovery cases and assign eDiscovery managers to specific cases. eDiscovery managers can only access the cases of which they're members. eDiscovery (Standard) also lets you associate searches and exports with a case and lets you place an eDiscovery hold on content locations relevant to the case.
 eDiscovery (Premium)
 provides an end-to-end workflow to preserve, collect, analyze, review, and export content that's responsive to your organization's internal and external investigations. It also lets legal teams manage the entire legal hold notification workflow to communicate with custodians involved in a case.
-In Microsoft Purview eDiscovery, a custodian refers to the individual whose content is subject to search, hold, or review as part of a legal, regulatory, or investigative process. A custodian is typically an employee or user whose data (e.g., email, documents, Teams messages) may be relevant to the matter under investigation. This is distinct from the IT administrators or compliance officers who perform searches or manage eDiscovery cases. Licensing requirements apply both to custodians (whose data is preserved or reviewed) and to users performing eDiscovery activities, as defined in the Microsoft Purview licensing terms.
+In Microsoft Purview eDiscovery, a custodian refers to the individual whose content is subject to search, hold, or review as part of a legal, regulatory, or investigative process. A custodian is typically an employee or user whose data (e.g., email, documents, Teams messages) may be relevant to the matter under investigation. This is distinct from the IT administrators or compliance officers who perform searches or manage eDiscovery cases. Licensing requirements for eDiscovery vary based on usage. When premium eDiscovery features are used to analyze a userâs data, the user whose data is analyzed must have the appropriate license or add-on. For current licensing requir
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Customer Satisfaction
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:d9264fc1863e88d5b74a7eaceafcfa1c4b31a2791365c73b5ae6dbed78b4bef5

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*