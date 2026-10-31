# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-31
**Run Time:** 2026-10-31T11:49:48.000541+00:00
**Total URLs Checked:** 228

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
| 1 | restricted-content-discovery | HIGH | 4.7, 4.1, 4.6, 1.3, 1.14 | Review and update |
| 2 | advanced-management | HIGH | 4.1, 4.5, 4.6, 4.2, 1.3 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:a49f8c2049869398f1c66fbb7718dafc062a3370b5030fd0546479eccb61a771

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
--- +++ @@ -142,9 +142,9 @@ How long does it take for updates to Restricted Content Discovery to take effect?
 Restricted Content Discovery is a site-level property. Index update latency is highly dependent on the number of items in the site and the number of sites getting updated at the same time. For sites with more than 500,000 items, an update to Restricted Content Discovery could take more than a week to fully process and reflect in search and Copilot experiences.
 How does Restricted Content Discovery fit into a Copilot readiness strategy?
-Restricted Content Discovery helps organizations temporarily limit discovery of selected sites while permissions, ownership, and governance controls are reviewed. It's one component of a broader SharePoint governance and Copilot readiness strategy. See the following resources:
+Restricted Content Discovery helps organizations temporarily limit discovery of selected sites while permissions, ownership, and governance controls are reviewed. It's one component of a broader SharePoint governance and Copilot readiness strategy. See
 Secure and govern Microsoft Copilot: Foundational deployment guidance
-Get ready for Microsoft Copilot and agents with SharePoint Advanced Management
+.
 Next steps
 Review
 Data access governance reports for SharePoint and OneDrive sites

```

---

### 2. Advanced Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:81f7cbfce4cc6d3410a288a7746565bc57d2ff3314c3a4377b9f636bffb366c0

**Affected Controls:**
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -28,9 +28,6 @@ Manage the content lifecycle
 ; and
 Prevent oversharing
-.
-SAM capabilities are helpful as organizations
-prepare for Microsoft Copilot and agents
 .
 Video: SharePoint Advanced Management overview
 Watch the following video to get an overview of SharePoint Advanced Management:
@@ -107,7 +104,6 @@ .
 Related articles
 SharePoint Admin Agent
-Get ready for Microsoft Copilot and Agents with SharePoint Advanced Management
 Configure a secure and governed foundation for Microsoft Copilot
 SharePoint Advanced Management features in Microsoft Copilot licenses
 Feedback

```

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |
| https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps?view=o365-worldwide | https://learn.microsoft.com/en-us/microsoft-agent-365/admin/manage-copilot-agents-integrated-apps?view=o365-worldwide |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*