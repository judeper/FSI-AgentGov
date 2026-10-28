# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-28
**Run Time:** 2026-10-28T12:17:35.392551+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| MEDIUM Changes | 2 |
| Redirects | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | fundamentals-what-is-copilot-studio | MEDIUM | 2.13 | Review optional |
| 2 | dlp-policy-reference | HIGH | 1.5 | Update portal-walkthrough |
| 3 | ...osoft365-copilot-location-learn-about | HIGH | 1.14, 1.5, 1.6, 1.13 | Update portal-walkthrough |
| 4 | requirements-licensing-subscriptions | MEDIUM | None | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. DLP Policy Reference

**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Section:** Microsoft Purview
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:6e56b797676115868c997d9123b236e394c9fd0cd8f7076d61d5663b95643cd6

**Affected Controls:**
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.26/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -942,8 +942,8 @@ policy template
 - Set up a
 Microsoft Defender for Cloud Apps connector
-Microsoft 365 Copilot (preview)
-No
+Microsoft Copilot and Chat (preview)
+Yes (rolling out)
 Account or Distribution group
 data-at-rest
 data-in-use

```

---

### 2. DLP for M365 Copilot

**URL:** https://learn.microsoft.com/en-us/purview/dlp-microsoft365-copilot-location-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:bb1307d3ce7dda292a6949709415b6c94127cb11b1481919a97eccbf8aded776

**Affected Controls:**
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.7/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.13/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.5/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/4.7/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/4.7/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/4.7/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/1.14/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -274,9 +274,46 @@ Updates to a DLP policy can take up to four hours to reflect in Microsoft 365 Copilot and Copilot Chat experience.
 Admin units
 The
-Microsoft 365 Copilot and Copilot Chat
-policy location doesn't support
+Microsoft Copilot and Chat
+policy location supports
+administrative units
+. You can scope a Copilot DLP policy to a region or department and delegate policy management to administrators assigned to those units, without granting tenant-wide policy management permissions.
+Note
+Administrative unit support for this location is rolling out. The option might not yet be available in your tenant.
+Tip
+Use administrative units when regional or departmental administrators need to manage Copilot DLP policies for their own users.
+Before you create a scoped policy,
+configure administrative units
+in Microsoft Entra ID and assign them to the appropriate Microsoft Purview role group members. Administrators still need the DLP permissions required to create and manage policies.
+To scope a Copilot DLP policy:
+In the
+Microsoft Purview portal
+, go to
+Data Loss Prevention
+>
+Policies
+and select
++ Create policy
+.
+Select the
+Custom
+template, then
+Custom policy
+, and enter a name and description.
+On the
 Admin units
+page, select the administrative units for the policy.
+Select the
+Microsoft Copilot and Chat
+location and choose the users and groups to include or exclude within the selected administrative units.
+Configure the rule conditions and actions, review the settings, and save the policy.
+An administrative unit restricted administrator can select only their assigned units and manage policies within that scope. An unrestricted administrator can scope policies to administrative units or keep
+Full directory
+to apply a policy across the organization. Existing tenant-wide policies continue to apply; using administrative units is optional.
+Important
+Copilot DLP policy scoping is based on the user who submits the prompt, not the 
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Copilot Studio Overview
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:8881b27fb4c21693af02fefdaba5d8a6d61059fe27de2845d5132b8b1b759867

---

### 2. Copilot Studio Licensing (Get Access)
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:d977b5bdb7dccf45466e36a1ef9943040fff1ff03e3c43507c5d2281c49bc50e

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/agent-365-overview?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*