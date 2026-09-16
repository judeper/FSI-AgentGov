# Microsoft Learn Documentation Changes

**Run Date:** 2026-09-16
**Run Time:** 2026-09-16T10:59:31.119419+00:00
**Total URLs Checked:** 231

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 3 |
| MEDIUM Changes | 1 |
| Redirects | 5 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | alerts | HIGH | None | Review and update |
| 2 | planned-features | CRITICAL | 1.4, 3.8, 2.25, 2.17 | Review and update |
| 3 | restricted-content-discovery | HIGH | 1.3, 1.14, 4.1, 4.6, 4.7 | Review and update |
| 4 | whats-new | CRITICAL | None | Monitor |

---

## HIGH: Control Review Recommended

### 1. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:949fc4d3088c00dc293886a6135089ff0d5214232cd27c1f5c783e0a9f22099f

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
@@ -34,14 +34,14 @@ Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. You can place alert rules on an environment and a specific resource.
 A
 triggered alert
-occurs when one or more of the resources that an alert rule monitors pass specific thresholds that the admin defines when configuring the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for how to improve the resources if it's in a Managed Environment.
+occurs when one or more of the resources that an alert rule monitors pass specific thresholds that the admin defines when configuring the alert rule. You can select the triggered alert to learn what resources triggered the alert rule, and get recommendations for how to improve the resources if it's in a managed environment.
 When to use alerts
 Teams and admins use alerts to find resources that are used more than expected. For example, an admin creates an alert to know if apps in the default environment exceed 50 launches a day.
 Teams use alerts to find resources with degraded health, and work with their makers to fix issues.
 For operations, admins create alerts to know if apps in their production environment are slow to open for users.
 Prerequisites
 You must be a tenant administrator or an environment administrator to access alerts.
-You can only place alerts on a Managed Environment.
+You can only place alerts on a managed environment.
 You must be using the
 new and improved Power Platform admin center
 .
@@ -160,7 +160,7 @@ Find your resource, and select it to open a resource pane, which has more detailed metric information.
 In the upper-right corner of the pane, you see a link labeled
 + New alert rule
-if the resource is in a Managed Environment.
+if the resource is in a managed environ
```

---

### 2. Planned Features (2026 Wave 1) [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:516fa60b9833c6a5268ae6e81b55798684dcef30892bec31786334e0a5e998c5

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -1,156 +1,539 @@-Table of contents
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

### 3. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:8dc5389ff8f101de23b0271c62a24744afc2985a75255e5e5e455f8be06260d6

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`

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
@@ -22,108 +22,138 @@ Restrict discovery of SharePoint sites and content
 Feedback
 Summarize this article for me
-For organizations onboarding to Microsoft 365 Copilot, maintaining strong data governance controls for SharePoint content is critical to deploying Copilot in a safe manner. Sites identified with the highest risk of oversharing can use Restricted Content Discovery to protect content while taking time to ensure that permissions are accurate and well-managed.
-With Restricted Content Discovery, organizations can limit the ability of end users to search for files from specific SharePoint sites. Enabling Restricted Content Discovery for each site prevents the sites from surfacing in organization-wide search and Microsoft 365 Copilot Business Chat, unless a user had a recent interaction.
-Restricted Content Discovery is a site-level setting that needs to be propagated to the search index, a large number of transactions could lead to a long queue in the ingestion pipeline and higher update latency times.
-While child content is hidden by default, users in your organization can still discover files they own or recently interacted with. End users can still find relevant content they need for their day-to-day tasks, even if Restricted Content Discovery is applied to the parent site.
-Restricted Content Discovery doesn't affect searches originating from a site context or other intelligent features such as Microsoft 365 Feed and Recommendations.
+Organizations preparing for Microsoft Copilot often need time to review SharePoint sites, validate permissions, and implement governance controls before making content broadly discoverable. Restricted Content Discovery helps you limit discovery of content from specific SharePoint sites, including recently interacted files, in organization-wide search results and Microsoft Copilot responses while those revi
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Purview What's New
**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:f6e4f383e23d741218bb31d3abf5b7f80b60d7b95f41ddd1ceae8432ebe91c1c

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