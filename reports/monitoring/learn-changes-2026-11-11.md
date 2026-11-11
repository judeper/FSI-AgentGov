# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-11
**Run Time:** 2026-11-11T13:43:02.745067+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 1 |
| Redirects | 9 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | alerts | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:7820eda2b762217592143736ae18b9513534066b061a3f5700fa763a5baf0f2c

**What Changed:**
```diff
--- +++ @@ -603,6 +603,8 @@ or an
 Environment administrator
 to create and manage alerts.
+How many alert rules can I create?
+You can create up to 10 alert rules with a 1-hour data review period and up to 50 alert rules with a 24-hour data review period for a total of up to 60 alert rules. Hourly alert rules that are turned off still count towards the limit of 10, so delete hourly alert rules that you aren't using. Alert rules with a 24-hour data review period that are turned off don't count towards the alert rule limit.
 What environments are supported?
 All environment types, such as production, sandbox, trial, and developer environment types are supported, but they must be a managed environment. You select the environment in the
 ID
@@ -673,6 +675,16 @@ as the metric, it only monitors the TTI or TTFL of the
 start screen
 for that app. You cannot select a specific screen of an app when configuring an alert.
+I created an hourly alert rule, why can't I see any data or alert triggering right after?
+The first check runs after the first full hour, once there's at least one data point.
+Why are there gaps in the hourly chart?
+An hour with no activity has no data point.
+Will I get an email every hour while the problem lasts?
+You get an email as soon as a low-latency alert fires, then a reminder every 4 hours while the issue continues. Reminders stop when the issue resolves or after 7 days, whichever comes first. If the issue comes back after it resolves, you get a new email.
+Can I see more than 24 hours, or export hourly data?
+No, the hourly chart covers the last 24 hours only and Monitor's data export feature only covers daily metric aggregates.
+Can hourly alerts be opted into the 'When an alert fires' trigger on the Power Platform for Admins V2 Connector?
+At the moment, no, only alerts that have a 24-hour data review period can be opted in. We expect to support this functionality for hourly alerts by January 2027.
 Any tips or best practices?
 Yes! Follow t
```

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