# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-18
**Run Time:** 2026-08-18T06:43:51.536761+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 3 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | capacity-storage | HIGH | 3.5 | Review and update |
| 2 | ...ication-fundamentals-publish-channels | HIGH | None | Review and update |
| 3 | overview | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Capacity Storage

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/capacity-storage
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:5d1b10d34e0dccaed5968dbe6dac394153d78fb40728f0c9b39c66c23b71f456

**Affected Controls:**
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`

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
@@ -47,7 +47,9 @@ legacy model licenses
 nor the new model licenses, a new model report is displayed.
 Verifying your Microsoft Dataverse capacity-based storage model
-To view the Capacity add-ons summary page, you need one of the following roles:
+To view the
+Capacity add-ons
+summary page, you need one of the following roles:
 Tenant administrator
 Power Platform administrator
 Dynamics 365 administrator
@@ -63,9 +65,13 @@ On the navigation pane, select
 Licensing
 .
-On the Licensing pane, select
+On the
+Licensing
+pane, select
 Capacity add-ons
-to go to the Capacity add-ons summary page where you can see your tenant's storage, add-ons, and Microsoft Power Platform requests.
+to go to the
+Capacity add-ons
+summary page where you can see your tenant's storage, add-ons, and Microsoft Power Platform requests.
 Learn more in
 Dataverse capacity-based storage overview
 .
@@ -80,7 +86,9 @@ Add-ons
 , and
 Trial
-are available on the Capacity add-ons page.
+are available on the
+Capacity add-ons
+page.
 Summary tab
 On the Capacity page,
 Summary
@@ -154,7 +162,7 @@ Download
 Select
 Download
-above the list of environments to download an Excel .csv file with high-level storage information for each environment that the signed-in admin has permission to see in the Power Platform admin center.
+above the list of environments to download an Excel .csv file with high-level storage information for each environment that the signed-in admin can see in the Power Platform admin center.
 Search
 Use
 Search
@@ -211,7 +219,7 @@ Download
 Select
 Download
-above the list of environments to download an Excel .csv file with high-level storage information for each environment that the signed-in admin has permission to see in the Power Platform admin center.
+above the list of environments to download an Excel .csv file with high-level storage information for each 
```

---

### 2. Agent Publishing

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:0fcb0d5569907fae54c591df60354ed3457bd82bb93d184429d5cf3d73ba7337

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
@@ -22,6 +22,14 @@ Key concepts - Publish and deploy your agent
 Feedback
 Summarize this article for me
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
 By using Copilot Studio, you can publish agents that engage with your customers on multiple platforms or channels. For example, live websites, mobile apps, Microsoft 365 Copilot, and messaging platforms like Teams and Facebook.
 Each time you update your agent, you can publish it again from within Copilot Studio. Publishing your agent applies to all the channels associated with your agent.
 You need to publish your agent before your customers can engage with it. You can publish your agent on multiple platforms, or
@@ -95,6 +103,12 @@ Only share the demo website URL with members of your team and other stakeholders to try out the agent. The demo website isn't intended for production use. You shouldn't share this URL with customers.
 Configure channels
 After you publish your agent at least once, add channels so your customers can reach it.
+Note
+Some channels might be unavailable or disabled in your environment. Administrators can control which channels are available for Copilot Studio agents by using
+Agent access channels
+in the Power Platform admin center. Learn more in
+Configure channel publishing and connected agent access (preview)
+.
 To configure channels for your agent:
 On the top menu bar, select
 Channels
@@ -188,26 +202,20 @@ Use Microsoft Bot Framework skills in Copilot Studio
 .
 Next steps
-Web app
-Teams
 Article
 Description
 Publish an agent to a live or demo website
 Publish your agent on your live website, or use a demo website to share internally.
 Connect and configure 
```

---

### 3. Azure DevOps Test Plans

**URL:** https://learn.microsoft.com/en-us/azure/devops/test/overview?view=azure-devops
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:f0797b5c36bd1f0cf3d6de5b2d7ef33e79cc4be3c89c68aa97d23d4d8cadc260

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
@@ -76,9 +76,9 @@ run manual tests
 through an easy-to-use, browser-based interface that users can access from all major browsers on any platform.
 Rich diagnostic data collection
-: Using the web-based Test Runner and Test Runner client you can
-collect rich diagnostic data
-during your manual tests. This data includes screenshots, an image action log, screen recordings, code coverage, IntelliTrace traces, and test impact data for your apps under test. This data is automatically included in all the bugs you create during test, making it easy for developers to reproduce the issues.
+: Use the web-based Test Runner to
+collect diagnostic data
+during manual tests, including screenshots, image action logs, and screen recordings. Azure Test Plans automatically includes the captured data in bugs you create during the test, which helps developers reproduce issues.
 End to End traceability
 : Azure DevOps provides end-to-end traceability of your requirements, builds, tests, and bugs with
 linking work items to other objects
@@ -186,11 +186,11 @@ Test execution and test tools
 With the following tools, developers, testers, and stakeholders can initiate tests and capture rich data as they execute tests and automatically log code defects linked to the tests. Test your application by executing tests across desktop or web apps.
 Test Runner
-: A browser-based tool for testing web applications and a desktop client version for testing desktop applications that you launch from the
-Test plans
-hub to run manual tests. Test Runner supports rich data collection while performing tests, such as image action log, video recording, code coverage, etc. It also allows users to create bugs and mark the status of tests.
+: A browser-based tool that you launch from the
+Test plans
+hub to run manual tests for web and desktop applications. Test Runner supports screenshots, im
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