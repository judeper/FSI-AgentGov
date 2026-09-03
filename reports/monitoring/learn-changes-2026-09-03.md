# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-03
**Run Time:** 2026-09-03T10:49:30.215240+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 1 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | dlp-learn-about-dlp | HIGH | 1.5, 1.25, 1.3, 1.26 | Update portal-walkthrough |
| 2 | dlp-policy-reference | HIGH | 1.5 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Data Loss Prevention

**URL:** https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:c15ceed23aaa680617fa762c6729e2424a6de4135598c6cff317d882306f949c

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.25: Control 1.25: MIME Type Restrictions for File Uploads
  - File: `controls/pillar-1-security/1.25-mime-type-restrictions.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/3.1/verification-testing.md` (HIGH)
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
@@ -46,14 +46,15 @@ Use Network Data Security to help prevent sharing sensitive information with unmanaged AI (preview)
 Enterprise applications and devices
 DLP monitors and protects against oversharing in enterprise apps and on devices. It targets Microsoft 365 locations, like Exchange and SharePoint, and locations you add, like on-premises file shares, endpoint devices, and non-Microsoft cloud apps. These locations and sources include:
-Microsoft 365 services, like Exchange, SharePoint, OneDrive accounts, and Teams chat and channel messages
-Office applications, such as Word, Excel, and PowerPoint
-Devices running Windows 10, Windows 11, and the three most recent versions of macOS
-Non-Microsoft cloud apps
-On-premises file shares and on-premises SharePoint
-Microsoft Fabric and Power BI workspaces
-Microsoft 365 Copilot and Copilot chat (preview)
-Managed cloud apps
+Microsoft 365 services, like Exchange, SharePoint, OneDrive accounts, and Teams chat and channel messages.
+Office applications, such as Word, Excel, and PowerPoint.
+Devices running Windows 10, Windows 11, and the three most recent versions of macOS.
+Non-Microsoft cloud apps.
+Non-Microsoft connected apps (currently in preview), including Box, Dropbox, Google Workspace, and Salesforce.
+On-premises file shares and on-premises SharePoint.
+Microsoft Fabric and Power BI workspaces.
+Microsoft 365 Copilot and Copilot chat (preview).
+Managed cloud apps.
 Create DLP policies for
 Enterprise applications & devices
 to cover these locations.
@@ -305,7 +306,7 @@ Alerts in DLP policies
 : Describes alerts in the context of a DLP policy.
 Get started with data loss prevention alerts
-: Covers the necessary liscensing, permissions, and prerequisites for DLP alerts and alert reference details.
+: Covers the necessary licensing, permissions, and prerequisites for DLP alerts and alert referenc
```

---

## HIGH: Control Review Recommended

### 1. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:e4a2cc85ced745b8f2ffa089acfde13326c11d87eab884bb3868fbb0a833729f

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
@@ -925,17 +925,23 @@ -
 Learn about the data loss prevention on-premises repositories
 -
-Get started with the data loss prevention on-premises repositories
+Get started with data loss prevention for on-premises repositories
 Fabric and Power BI
 No
 Workspaces
 data-in-use
 No
-Third-party apps
-None
-No
-No
-No
+Non-Microsoft connected apps (preview)
+No
+Cloud app instance
+data-at-rest
+-
+Use DLP and sensitivity label policies for non-Microsoft connected apps
+- Only available in the
+Custom
+policy template
+- Set up a
+Microsoft Defender for Cloud Apps connector
 Microsoft 365 Copilot (preview)
 No
 Account or Distribution group
@@ -1795,9 +1801,7 @@ patent
 , etc.
 Document name matches patterns:
-Detects documents where the file name matches specific patterns. The evaluation considers the entire path of the document, not just the documentâs name. The pattern is checked as a string match, meaning it can match any part of the document path. To define the patterns, use wild cards. For information on regex patterns, see the Regular Expression documentation
-here
-.
+Detects documents where the file name matches specific patterns. The evaluation considers the entire path of the document, not just the documentâs name. The pattern is checked as a string match, meaning it can match any part of the document path. To define the patterns, use wild cards.
 Note
 Due to potential performance issues, this condition will gradually be phased out from Purview Endpoint DLP. We recommend using the 'Document name contains words or phrases' c
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