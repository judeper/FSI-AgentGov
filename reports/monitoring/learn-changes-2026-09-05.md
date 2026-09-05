# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-05
**Run Time:** 2026-09-05T10:06:29.949112+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 2 |
| MEDIUM Changes | 1 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | default-environment-routing | HIGH | 2.15 | Review and update |
| 2 | powerapps-powershell | MEDIUM | None | Review optional |
| 3 | ...tion-labels-data-lifecycle-management | HIGH | 1.9, 4.3 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Environment Routing

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:c3cdf366bb27cd447333d3850f9da270a7d1dc4a630890f2f16077d6c2ff7de3

**Affected Controls:**
- Control 2.15: Control 2.15: Environment Routing and Auto-Provisioning
  - File: `controls/pillar-2-management/2.15-environment-routing.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/configuration-hardening-baseline/index.md` (HIGH)
- ℹ️ `playbooks/getting-started/phase-0-governance-setup.md` (HIGH)

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
@@ -37,11 +37,11 @@ , the maker lands in their own personal developer environment instead of the default environment. Personal developer environments are the makers' own spaces, like OneDrive, for personal productivity where they can start building apps and solutions in their own workspace. Makers don't need to know which environment to work in, since the personal developer environment appears automatically.
 When the feature is turned on, the selected maker type (that is, new or existing makers), are directed into their own, personal developer environment. If the maker has access to one or more existing developer environments that aren't owned by them, they're routed to a new developer environment.
 Dataverse is available in developer environments, and these environments are
-Managed Environments
+managed environments
 with the admin settings preconfigured according to the assigned environment group rules. Admins no longer need to worry that their makers are working in the default environment, where their work can conflict with others.
 Important
 By default, all developer environments created through environment routing are managed.
-Managed Environments isn't included as an entitlement in the Developer Plan when users run their assets. For more information about Managed Environments and the Developer Plan, see
+Managed environments aren't included as an entitlement in the Developer Plan when users run their assets. For more information about managed environments and the Developer Plan, see
 Power Apps Developer Plan Guide: Features and Benefits
 .
 Non-managed
@@ -56,11 +56,11 @@ Fine-grained control over where makers build.
 Consistent policy enforcement across environments.
 Reduced risk of conflicts in shared or default environments.
-All routed environments are Managed Environments, meaning they inherit standardized policies like data retenti
```

---

### 2. Retention Labels

**URL:** https://learn.microsoft.com/en-us/purview/create-retention-labels-data-lifecycle-management
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:4d5d32cde8d84548a41afa45ecb03c23ea510eca5a1340501b5b239d3ee4c62b

**Affected Controls:**
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`

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
@@ -60,6 +60,9 @@ Select
 Create a label
 and follow the prompts to create the retention label. Be careful what name you choose, because this can't be changed after the label is saved.
+Note
+Retention label names can't contain characters that match this regular expression:
+[""#\$%\*\\\&\?\,\;\:\<\>\|\!\'\(\)\[\]\{\}\^`~]+
 For more information about the retention settings, see
 Settings for retaining and deleting content
 .

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. PowerShell
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8912872914c0a81c8ad88a8bb02c6aa33bdfcca0d5e55305dd40ae12ef04e895

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