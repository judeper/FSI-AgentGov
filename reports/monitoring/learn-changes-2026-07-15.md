# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-15
**Run Time:** 2026-07-15T08:12:23.156510+00:00
**Total URLs Checked:** 227

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
| 1 | planned-features | CRITICAL | 3.8, 2.25, 2.17, 1.4 | Review and update |
| 2 | audit-search | HIGH | 3.2, 3.12, 1.7 | Update portal-walkthrough |
| 3 | endpoint-dlp-learn-about | HIGH | 1.17 | Review and update |
| 4 | dlp-configure-endpoint-settings | HIGH | 1.17 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Search the Audit Log

**URL:** https://learn.microsoft.com/en-us/purview/audit-search
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:5694ada19a69f4ac34ef15efe57006e0d1b5cf385bbae97b574003bda9855cec

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
--- +++ @@ -28,7 +28,7 @@ Each admin Audit account user can have up to 10 search jobs running at the same time, with a limit of one unfiltered search job.
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
-cmdlet to a CSV file, see the "Tips for exporting and viewing the audit log" section in
-Export, configure, and view audit log records
+cmdlet to a CSV file, see
+Tips for exporting an
```

---

## HIGH: Control Review Recommended

### 1. Planned Features (2026 Wave 1) [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:2c6ed37d9613abf1d1840d763365626c1beea6fd6a725138889dc17a6425b962

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -1,156 +1,523 @@-Table of contents
-Exit editor mode
-Ask Learn
-Ask Learn
-Reading mode
-Table of contents
-Read in English
-Add
-Add to plan
-Edit
-Copy Markdown
-Print
-Note
-Access to this page requires authorization. You can try
-signing in
-or
-changing directories
-.
-Access to this page requires authorization. You can try
-changing directories
-.
-What's new and planned for Microsoft Copilot Studio
-Feedback
-Summarize this article for me
-This topic lists features that are planned to release from April 2026 through September 2026. Because this topic lists features that may not have released yet,
-delivery timelines may change and projected functionality may not be released
-. For more information, go to
-Microsoft policy
-.
-For a list of the previous wave's release plans, go to
-2025 release wave 2 plan
-.
-In the
-General availability
-column, the feature will be delivered within the month listed. The delivery date can be any day within that month. Released features show the full date, including the date of release.
-This check mark (
-) shows which features have been released for public preview and general availability.
-Copilot and AI innovation
-Use industry leading generative AI capabilities in Microsoft Copilot Studio to do the work so you and your team don't have to.
-Feature
-Enabled for
-Public preview
-General availability
-Automate web and desktop apps with computer use
-Admins, makers, marketers, or analysts, automatically
-May 27, 2025
-May 7, 2026
-Give read-only analytics access to users
-Admins, makers, marketers, or analysts, automatically
--
-Apr 28, 2026
-Use code interpreter on SharePoint sources in agent conversations
-Admins, makers, marketers, or analysts, automatically
-Mar 16, 2026
-May 2026
-Define custom metrics for analytics
-Admins, makers, marketers, or analysts, automatically
-Apr 15, 2026
-Jul 2026
-Analyze quality of responses that use generative AI
-Admins, makers, marketers, or analysts, automatically
-Jun 17, 
```

---

### 2. Endpoint DLP

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:8f4e0ad012f79ad5d3d42a7895d99753c079efddfd50693a9713e96297835d0a

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

**What Changed:**
```diff
--- +++ @@ -42,13 +42,7 @@ Note
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
@@ -131,6 +125,11 @@ n/a
 Supported
 Supported
+Following parameters are only supported on Windows:
+- Print to file
+- Universal print deployed on a printer
+- Corporate printer
+- Print to local
 Removable USB device groups
 n/a
 Supported
@@ -168,7 +167,7 @@ Other settings
 Setting
 Windows 10/11, Windows 10, 1809 and later, Windows 11
-Windows Server 2019, Windows Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows Server 2019 and later versions for Endpoints (X64)
 macOS (three latest released versions)
 Archive file
 Supported
@@ -188,7 +187,7 @@ Endpoint DLP enables you to audit and manage the following types of activities users take on sensitive items that are physically stored Windows 10, Windows 11, or macOS devices.
 Activity
 Description
-Windows 10 (21H2, 22H2), Windows 11 (21H2, 22H2), Windows Server 2019, Server 2022 (21H2 onwards) for Endpoints (X64)
+Windows 
```

---

### 3. Configure Settings

**URL:** https://learn.microsoft.com/en-us/purview/dlp-configure-endpoint-settings
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:8464e14eb38ae532bd15ee51ca882038f92597f75f99d5602af52d3cd751800f

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