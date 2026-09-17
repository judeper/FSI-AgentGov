# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-17
**Run Time:** 2026-09-17T11:10:22.271723+00:00
**Total URLs Checked:** 231

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| MEDIUM Changes | 2 |
| Redirects | 5 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | dlp-learn-about-dlp | HIGH | 1.3, 1.25, 1.26, 1.5 | Update portal-walkthrough |
| 2 | overview-authentication | MEDIUM | 1.11 | Review optional |
| 3 | whats-new | CRITICAL | None | Monitor |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Data Loss Prevention

**URL:** https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:7b53a110446016a080cdcfac1cfa52b0fb7bcc561628de81734bdfb4785ee495

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.25: Control 1.25: MIME Type Restrictions for File Uploads
  - File: `controls/pillar-1-security/1.25-mime-type-restrictions.md`
- Control 1.26: Control 1.26: Agent File Upload and File Analysis Restrictions
  - File: `controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

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
@@ -34,26 +34,28 @@ and
 Inline web traffic
 data. DLP policies act on a variety of locations, methods of data transmission, and types of user activities.
-DLP uses deep content analysisânot a simple text scan. It analyzes content:
+DLP uses deep content analysis - not a simple text scan. It analyzes content:
 For primary data matches to keywords
 By the evaluation of regular expressions
 By internal function validation
 By secondary data matches that are in proximity to the primary data match
-DLP also uses machine learning algorithms and other methods to detect content that matches your DLP policies
-Inline by
+Using machine learning algorithms and other methods to detect content that matches your DLP policies
+Inline through
 Microsoft Edge for business
-for Windows devices that haven't been onboarded into Microsoft Purview (preview) and
-Use Network Data Security to help prevent sharing sensitive information with unmanaged AI (preview)
+for Windows devices that haven't been onboarded into Microsoft Purview
+Microsoft Purview network data security
+via SASE and non-Microsoft secure enterprise browser integrations.
 Enterprise applications and devices
 DLP monitors and protects against oversharing in enterprise apps and on devices. It targets Microsoft 365 locations, like Exchange and SharePoint, and locations you add, like on-premises file shares, endpoint devices, and non-Microsoft cloud apps. These locations and sources include:
-Microsoft 365 services, like Exchange, SharePoint, OneDrive accounts, and Teams chat and channel messages
-Office applications, such as Word, Excel, and PowerPoint
-Devices running Windows 10, Windows 11, and the three most recent versions of macOS
-Non-Microsoft cloud apps
-On-premises file shares and on-premises SharePoint
-Microsoft Fabric and Power BI workspaces
-Microsoft 365 Copilot and Copilot chat (preview)
-
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Authentication Methods
**URL:** https://learn.microsoft.com/en-us/entra/identity/authentication/overview-authentication
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:5bc810595379748477149878dd26f73bbf0a907e9773806c072f327753ad5127

---

### 2. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:b6b3e410ec4794283e0d7d9c6b08c6d0c8e29770097a3952ed2c962ff065530b

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/overview | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/security-governance | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/security-governance |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/management-controls | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/management-controls |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*