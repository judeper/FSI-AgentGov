# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-10
**Run Time:** 2026-11-10T14:28:44.218332+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 4 |
| HIGH Changes | 1 |
| MEDIUM Changes | 1 |
| Redirects | 9 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | whats-new | HIGH | None | Review and update |
| 2 | dlp-policy-reference | MEDIUM | 1.5 | Update portal-walkthrough |
| 3 | ...osoft365-copilot-location-learn-about | HIGH | 1.5, 1.13, 1.14, 1.6 | Update portal-walkthrough |
| 4 | insider-risk-management-activities | HIGH | 1.12 | Update portal-walkthrough |
| 5 | microsoft-purview-service-description | HIGH | None | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a6ed5f9b0582b2c515fb75c86f904dd0b781148609325a38839ce02fb894fd79

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.26/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -950,6 +950,7 @@ - Only available in the
 Custom
 policy template
+- Administrative unit scoping also applies to Cowork.
 Managed cloud apps
 No
 Account or Distribution group

```

---

### 2. DLP for M365 Copilot

**URL:** https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:8e3f2492bacb7654eca68803b1224f1ad9ffbcb4e471564685c81b0e086dc8fb

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.7/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.14/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/1.13/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.5/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.7/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -38,7 +38,7 @@ Microsoft 365 Enterprise Plans
 Microsoft 365 Service Descriptions
 Permissions
-Accounts with one of the following roles or role groups can create or edit a DLP policy for the Microsoft 365 Copilot and Copilot Chat location:
+Accounts with one of the following roles or role groups can create or edit a DLP policy for the Microsoft Copilot, Copilot Chat, and Copilot Cowork location:
 Microsoft Entra AI Admin
 - Role for managing all aspects of Microsoft 365 Copilot and AI-related enterprise services in Microsoft 365.
 Purview Data Security AI Admin
@@ -76,7 +76,7 @@ On the
 Locations
 page, set the
-Microsoft 365 Copilot and Copilot Chat
+Microsoft Copilot, Copilot Chat, and Copilot Cowork
 location to on.
 Add a rule with the
 Content contains
@@ -91,10 +91,10 @@ Save and turn on the policy.
 When a user prompt contains the configured SITs, Copilot and Cowork block external web search as a grounding source and continue to generate the response using allowed internal Microsoft 365 data sources.
 Block SITs in web search use case example
-Contoso wants employees to use Microsoft 365 Copilot for productivity, but doesn't want sensitive customer data sent to external web search providers when Copilot grounds responses on the web.
+Contoso wants employees to use Microsoft 365 Copilot or Cowork for productivity, but doesn't want sensitive customer data sent to external web search providers when Copilot grounds responses on the web.
 To meet this business need, Contoso configures a DLP policy as follows:
 Targets the
-Microsoft 365 Copilot and Copilot Chat
+Microsoft Copilot, Copilot Chat, and Copilot Cowork
 policy location.
 Adds a rule with the
 Content contains
@@ -108,9 +108,9 @@ .
 When a user submits a prompt containing those SITs, Copilot doesn't send the prompt to external web search providers. Copilot still returns a response grounded in internal Microsoft 365 data sources where the user has access.
 Block sensitive information types in 
```

---

### 3. Investigate Alerts

**URL:** https://learn.microsoft.com/en-us/purview/insider-risk-management-activities
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:d9f1a8f54a43c39d5292ab490e53eb7646b513ebfd028c2e479feedfa390759a

**Affected Controls:**
- Control 1.12: Control 1.12: Insider Risk Detection and Response
  - File: `controls/pillar-1-security/1.12-insider-risk-detection-and-response.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.12/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.12/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -33,6 +33,16 @@ and
 Standard alert
 dashboards.
+How alternate email addresses affect activity association
+Insider Risk Management uses alternate email addresses associated with a Microsoft Entra ID user object to associate activity with that user. These addresses include those in
+Other mail
+, which is also used to populate historical activity. This association helps provide a complete view of activity across alternate-email accounts associated with the Microsoft Entra ID user object.
+For example, an administrator account's Microsoft Entra ID user object might list the user's primary-account email address in
+Other mail
+. In this configuration, activity performed with the primary account can appear under the administrator account's Insider Risk Management profile. The profile under which activity appears doesn't necessarily identify the account that performed the activity.
+When investigating activity that appears under an unexpected profile, review the associated alternate email addresses in Microsoft Entra ID and the activity details to understand the account association.
+Note
+Changing or removing an alternate email address doesn't correct existing alerts or reassociate historical activity.
 Triaging alerts
 Investigate and act on alerts in Insider Risk Management by following these steps:
 Review the dashboards for alerts

```

---

### 4. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:b439c6d2cddc42ef6f281deacd99bd86cd77ea603713ef881b2872999e7fdc27

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.10/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.10/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/verification-testing.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -61,14 +61,14 @@ Office 365 E3/E1/A3/A1/G3/G1/F3
 Microsoft 365 Business Basic/Standard/Premium
 Audit (Standard)
-Yes
-Yes
-Yes
+Included
+Included
+Included
 Audit (Standard) for Microsoft Copilot interactions
 1
-Yes
-Yes
-Yes
+Included
+Included
+Included
 1
 Audit logs for Microsoft Copilot interactions are generated only when Microsoft Copilot is licensed and in use.
 Microsoft Purview Audit (Premium)
@@ -86,16 +86,16 @@ 3
 Audit (Premium)
 1
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 Audit (Premium) for Microsoft Copilot interactions
 2
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 1
 Audit (Premium) includes all Audit (Standard) capabilities.
 2
@@ -128,30 +128,30 @@ Microsoft 365 E5/A5/G5, Microsoft Purview Suite/EDU/GOV/FLW and Microsoft Defender + Purview Suite FLW, and Microsoft 365 E5/A5/F5/G5 Insider Risk Management
 Office 365 E5/A5/G5
 Communication Compliance
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 Microsoft Copilot for Microsoft 365 prompt and response analysis
-Yes
-Yes
-No
-No
+Included
+Included
+Not included
+Not included
 Microsoft Teams chats
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 Viva Engage conversations
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 Exchange Online emails
-Yes
-Yes
-Yes
-Yes
+Included
+Included
+Included
+Included
 For more information, seeâ¯
 Get started with communication compliance
 .
@@ -167,7 +167,7 @@
```

---

## HIGH: Control Review Recommended

### 1. Copilot Studio guidance hub — What's new

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:5a65897bbc53df54509ed884e73458e31b58099bca8cb7b9aea520138ab3af11

**What Changed:**
```diff
--- +++ @@ -26,6 +26,9 @@ November 2026
 New articles
 Design reliable agentic loops
+Other updates
+New reference architecture in the Power Platform and Copilot Studio Architecture Center:
+Build a multilingual IT self-service agent with Copilot Studio
 October 2026
 New reference architecture in the
 Power Platform and Copilot Studio Architecture Center

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. DLP Policy Reference
**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:a6ed5f9b0582b2c515fb75c86f904dd0b781148609325a38839ce02fb894fd79

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2025wave2/ |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio | https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/ | https://learn.microsoft.com/en-us/previous-versions/power-platform/release-plan/2026wave1/ |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*