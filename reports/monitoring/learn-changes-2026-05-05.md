# Microsoft Learn Documentation Changes

**Run Date:** 2026-05-05
**Run Time:** 2026-05-05T08:12:26.949374+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 6 |
| MEDIUM Changes | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | HIGH | 2.4 | Review and update |
| 2 | fundamentals-what-is-copilot-studio | CRITICAL | 2.13 | Monitor |
| 3 | dlp-policy-reference | HIGH | None | Review and update |
| 4 | encryption-sensitivity-labels | HIGH | 1.16 | Review and update |
| 5 | encryption | HIGH | 1.16 | Review and update |
| 6 | apply-irm-to-a-list-or-library | HIGH | 1.16 | Review and update |
| 7 | requirements-licensing-subscriptions | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**What Changed:**
```diff
--- +++ @@ -175,9 +175,10 @@ Self-service disaster recovery depends on Azure region pairs. Regions that don't have a regional Azure pair aren't supported. For more information, go to
 Azure supported regions
 .
-As of November 2025, Austria East, Belgium Central, Chile Central, Indonesia Central, Israel Central, Italy North, Malaysia West, Mexico Central, New Zealand North, and Poland Central are single regions and aren't supported. Once a region gets a regional pair, it's on our roadmap for Power Platform geo build-out and for supporting self-service disaster.
-Note
-UAE, Brazil, and South Africa have regional pairs in constrained regions and are on the roadmap for Power Platform geo buildout followed by self-service disaster recovery support. Geo build-out prioritization is influenced by impact, opportunity, and resource constraints.
+As of November 2025, Austria East, Belgium Central, Chile Central, Indonesia Central, Israel Central, Italy North, Malaysia West, Mexico Central, New Zealand North, and Poland Central are single regions and aren't supported for self-service disaster recovery.
+Note
+Brazil and South Africa don't have self-service disaster recovery because their regional pairs are in heavily constrained regions. Adding supported regions is influenced by impact, opportunity, and resource constraints.
+United Arab Emirates has self-service disaster recovery but continues to be capacity-constrained, which has impacted its general availability.
 What should I know about the capacity experience?
 When you allow self-service disaster recovery, you see more storage consumption displayed in the Dataverse capacity graph, clearly indicating the extra capacity used by the cross-region backup.
 When you don't allow self-service disaster recovery, the capacity graph shows standard usage without the extra storage for replication.

```

---

### 2. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -19,31 +19,9 @@ Access to this page requires authorization. You can try
 changing directories
 .
+Data Loss Prevention policy reference
 Feedback
 Summarize this article for me
-title: "Data Loss Prevention policy reference"
-f1.keywords: CSH
-ms.author: chrfox
-author: chrfox
-manager: laurawi
-ms.date: [DATE]
-audience: Admin
-ms.topic: reference
-ms.service: purview
-ms.subservice: purview-data-loss-prevention
-search.appverid:
-SPO160
-MET150
-ms.assetid: 6501b5ef-6bf7-43df-b60d-f65781847d6c
-ms.collection:
-highpri
-purview-compliance
-SPO_Content
-recommendations: false
-description: "DLP policy component and configuration reference. This article provides a detailed anatomy of a DLP policy."
-ms.custom: seo-marvel-apr2021
-ai-usage: ai-assisted
-Data Loss Prevention policy reference
 Microsoft Purview Data Loss Prevention (DLP) policies have many components to configure. To create an effective policy, you need to understand what the purpose of each component is and how its configuration alters the behavior of the policy. This article provides a detailed anatomy of a DLP policy.
 Tip
 Get started with Microsoft Security Copilot to explore new ways to work smarter and faster using the power of AI. Learn more about

```

---

### 3. Information Rights Management

**URL:** https://learn.microsoft.com/en-us/purview/encryption-sensitivity-labels
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

**What Changed:**
```diff
--- +++ @@ -48,8 +48,8 @@ Understand how the encryption works
 Unless you're using
 S/MIME for Outlook
-, encryption that's applied by sensitivity labels to documents, emails, and meeting invites all use the Azure Rights Management service (Azure RMS) from Microsoft Purview Information Protection. This protection solution uses encryption, identity, and authorization policies. To learn more, see
-What is Azure Rights Management?
+, encryption that's applied by sensitivity labels to documents, emails, and meeting invites all use the Azure Rights Management service from Microsoft Purview Information Protection. This protection solution uses encryption, identity, and authorization policies. To learn more, see
+Learn about the Azure Rights Management encryption service
 .
 When you use this encryption solution, the
 super user
@@ -76,8 +76,8 @@ There are some Microsoft Entra configurations that can prevent authorized access to encrypted content. For example, cross-tenant access settings and Conditional Access policies. For more information, see
 Microsoft Entra configuration for encrypted content
 .
-Configure Exchange for Azure Rights Management
-Exchange doesn't have to be configured for Azure Rights Management before users can apply labels in Outlook to encrypt their emails. However, until Exchange is configured for Azure Rights Management, you don't get the full functionality of encryption with rights management.
+Configure Exchange for the Azure Rights Management service
+Exchange doesn't have to be configured for the Azure Rights Management service before users can apply labels in Outlook to encrypt their emails. However, until Exchange is configured for the Azure Rights Management service, you don't get the full functionality of encryption with rights management.
 For example, users can't view encrypted emails or encrypted meeting invites on mobile phones or with Outlook on the web, encrypted emails can't be indexed for search, and you can't configure Exchange Onl
```

---

### 4. Encryption

**URL:** https://learn.microsoft.com/en-us/purview/encryption
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

**What Changed:**
```diff
--- +++ @@ -56,7 +56,7 @@ Data Encryption in OneDrive and SharePoint
 Skype for Business Online: Security and Archiving
 Email in transit between recipients. This email includes email hosted by Exchange Online.
-Microsoft Purview Message Encryption with Azure Rights Management, S/MIME, and TLS for email in transit
+Microsoft Purview Message Encryption with the Azure Rights Management service, S/MIME, and TLS for email in transit
 Message Encryption
 Email encryption in Microsoft 365
 How Exchange Online uses TLS to secure email connections in Microsoft 365
@@ -70,8 +70,7 @@ What if I need more control over encryption to meet security and compliance requirements?
 Microsoft 365 provides Microsoft-managed solutions for volume encryption, file encryption, and mailbox encryption in Microsoft 365. In addition, Microsoft provides encryption solutions that you can manage and control. These encryption solutions are built on Azure.
 To learn more, see the following resources:
-What is Azure Rights Management?
-Activate Rights Management in the admin center
+Learn about the Azure Rights Management encryption service
 Set up Information Rights Management (IRM) in SharePoint admin center
 Overview of Customer Key
 Double Key Encryption

```

---

### 5. Apply IRM to SharePoint

**URL:** https://learn.microsoft.com/en-us/purview/apply-irm-to-a-list-or-library
**Section:** Azure Services
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.16: Control 1.16: Information Rights Management (IRM) for Documents
  - File: `controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md`

**What Changed:**
```diff
--- +++ @@ -24,7 +24,7 @@ Summarize this article for me
 You can use Information Rights Management (IRM) to help control and protect files that are downloaded from lists or libraries. This feature is only supported in the Microsoft global cloud. IRM isn't supported for SharePoint lists and libraries in national cloud deployments.
 Administrator preparations before applying IRM
-The Azure Rights Management service (Azure RMS) from Microsoft Purview Information Protection, and the on-premises equivalent, Active Directory Rights Management Services (AD RMS), support Information Rights Management for sites. No other installations are required.
+The Azure Rights Management service from Microsoft Purview Information Protection, and the on-premises equivalent, Active Directory Rights Management Services (AD RMS), support Information Rights Management for sites. No other installations are required.
 Before you apply IRM to a list or library, you need to enable IRM for your site. You need administrator permissions for the site to enable IRM. In addition, to apply IRM to a list or library, you must have administrator permissions for that list or library.
 If you're using SharePoint, your users might experience timeouts when downloading larger IRM-protected files. To avoid timeouts, use your Office apps to apply IRM protection, and store larger files in a SharePoint library that doesn't use IRM.
 Note
@@ -87,7 +87,7 @@ Select the
 Stop restricting access to the library at
 check box, and then select the date that you want.
-Control the interval that Azure RMS credentials are cached for the program that is licensed to open the document.
+Control the interval that the Azure Rights Management service credentials are cached for the program that is licensed to open the document.
 Select the
 Users must verify their credentials using this interval (days)
 check box, then enter the interval for caching credentials in number of days.

```

---

### 6. Copilot Studio Licensing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Section:** Licensing
**Classification:** HIGH (Portal references)

**What Changed:**
```diff
--- +++ @@ -73,29 +73,33 @@ You can get a standalone Copilot Studio subscription from the Microsoft 365 admin center. For more information, see
 Assign licenses and manage access to Copilot Studio
 .
-Copilot Studio for Microsoft Teams plans
-Copilot Studio for Teams enables customers to build conversational interfaces within Teams. The agents can use data stored in Microsoft Dataverse for Teams or many other sources, using the supplied standard connectors.
-Capabilities available in the Copilot Studio app in Teams are available as part of select Microsoft 365 subscriptions with Microsoft Power Platform and Teams capabilities. This plan excludes plans for US government environments (GCC, GCC High, and DoD), EDU A1, and SUB SKUs.
-This table compares key capabilities in the Copilot Studio for Teams plan, which is available in select Microsoft 365 subscriptions, against the standalone Copilot Studio subscription. For a full, comparative list, see the
+Copilot Studio for Microsoft Teams plan
+The Copilot Studio for Teams plan, part of select Microsoft 365 subscriptions, lets you build agents that use classic orchestration and publish them to Teams. These agents can use data stored in Microsoft Dataverse for Teams or many other sources, by using
+Power Automate flows
+.
+A subset of the capabilities available in Copilot Studio are available as part of select Microsoft 365 subscriptions with Microsoft Power Platform and Teams capabilities. This plan excludes plans for US government environments (GCC, GCC High, and DoD), EDU A1, and SUB SKUs.
+The following table compares key capabilities in the Copilot Studio for Teams plan, available in select Microsoft 365 subscriptions, against the standalone Copilot Studio subscription. For a full, comparative list, see the
 Microsoft Power Platform Licensing Guide
 .
-Also see the
+Also see
 Quotas and limits
-article for other capacity considerations.
+for other capacity considerations.
 Capability
-Select Microsoft 365 subscriptio
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Copilot Studio Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Classification:** CRITICAL (Deprecation notice)

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*