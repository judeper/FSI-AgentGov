# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-28
**Run Time:** 2026-07-28T08:35:23.539362+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 2 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | microsoft-365-copilot-enable-users | HIGH | None | Review and update |
| 2 | restricted-content-discovery | HIGH | 1.14, 1.3, 4.7, 4.1, 4.6 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Manage Copilot

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-enable-users
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:f830a0f4f477db1ec374b67aee92dea7815065e7b650a41825b316f112a368b1

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
@@ -26,21 +26,21 @@ is an AI-powered productivity tool that helps users with everyday tasks.
 As part of your
 Microsoft 365 Copilot adoption
-, a welcome email to your Microsoft 365 Copilot users is sent on license assignment that announces Microsoft 365 Copilot and its features. You can also enable feedback for Microsoft 365 Copilot users.
+, send a welcome email to your Microsoft 365 Copilot users on license assignment that announces Microsoft 365 Copilot and its features. You can also enable feedback for Microsoft 365 Copilot users.
 Additionally, admins can use Organizational Messaging in the Microsoft Admin Center to deliver tailored in-product messages to your users directly through Teams.
 This article provides information about how to send users a welcome email, enable feedback, send organizational messages, and review the Microsoft 365 Copilot usage activity report.
 This article applies to:
 Microsoft 365 Copilot
 Send welcome email
-After you assign a Microsoft 365 Copilot license to a user, they will automatically be sent a notification email that can look like the following email.
+After you assign a Microsoft 365 Copilot license to a user, the system automatically sends a notification email that can look like the following email.
 The welcome email also includes a link to
 Microsoft Copilot help and learning
 .
-We also recommend sending an in-product notification to your users through Organizational Messaging.
-Organizational Messages
-Admins can also send a customizable in-product message through Teams with Organizational Messaging in the Microsoft Admin Center. After you
+Send an in-product notification to your users through Organizational Messaging.
+Organizational messages
+Admins can send a customizable in-product message through Teams with organizational messaging in the Microsoft Admin Center. After you
 set up Microsoft 365 C
```

---

### 2. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:8df445512fee33c97b7668e0a5d5610d9932430fbbae06996fc9f9b15dd809d6

**Affected Controls:**
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`

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
@@ -22,108 +22,132 @@ Restrict discovery of SharePoint sites and content
 Feedback
 Summarize this article for me
-For organizations onboarding to Microsoft 365 Copilot, maintaining strong data governance controls for SharePoint content is critical to deploying Copilot in a safe manner. Sites identified with the highest risk of oversharing can use Restricted Content Discovery to protect content while taking time to ensure that permissions are accurate and well-managed.
-With Restricted Content Discovery, organizations can limit the ability of end users to search for files from specific SharePoint sites. Enabling Restricted Content Discovery for each site prevents the sites from surfacing in organization-wide search and Microsoft 365 Copilot Business Chat, unless a user had a recent interaction.
-Restricted Content Discovery is a site-level setting that needs to be propagated to the search index, a large number of transactions could lead to a long queue in the ingestion pipeline and higher update latency times.
-While child content is hidden by default, users in your organization can still discover files they own or recently interacted with. End users can still find relevant content they need for their day-to-day tasks, even if Restricted Content Discovery is applied to the parent site.
-Restricted Content Discovery doesn't affect searches originating from a site context or other intelligent features such as Microsoft 365 Feed and Recommendations.
+Organizations preparing for Microsoft 365 Copilot often need time to review SharePoint sites, validate permissions, and implement governance controls before making content broadly discoverable. Restricted Content Discovery (RCD) helps you limit discovery of content from specific SharePoint sites, including recently interacted files, in organization-wide search results and Microsoft 365 Copilot responses wh
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