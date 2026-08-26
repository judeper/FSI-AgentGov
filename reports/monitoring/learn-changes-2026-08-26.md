# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-26
**Run Time:** 2026-08-26T06:51:04.363080+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 3 |
| MEDIUM Changes | 1 |
| Redirects | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | power-platform-inventory | CRITICAL | 3.11 | Monitor |
| 2 | analytics-overview | HIGH | 3.2, 3.10, 2.9, 2.5, 2.6 | Update portal-walkthrough |
| 3 | analytics-improve-agent-effectiveness | HIGH | None | Update portal-walkthrough |
| 4 | planned-features | CRITICAL | 3.8, 2.25, 2.17, 1.4 | Review and update |
| 5 | human-in-the-loop | HIGH | 2.12, 2.17 | Review and update |
| 6 | message-center | HIGH | 2.10 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:7a5c7f77dca89695114dcb06748ebcf99b76fc7dce6f5a1347764fb9e0b08932

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)

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
@@ -19,28 +19,36 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Analytics overview
+Monitor overview
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
 Use analytics to understand how well your agent is performing and to identify areas for improvement.
 The
-Analytics
+Monitor
 page in Copilot Studio shows you comprehensive data for your agent, from an overview of key metrics to in-depth usage analytics for your agent's components. You can drill down into each piece of data to get more details.
-The analytics experience is tailored for
+The Monitor experience is tailored for
 conversational agents
 and for
 autonomous agents
 .
-Analytics are available in all geographies. Analytics data is available for up to 360 days. Session details and transcript information are available for the last 28 days. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
-Note
-The
-Analytics
+Monitoring is available in all geographies. Monitor data is available for up to 360 days. Session details and transcript information are available for the last 28 days. Time-and-date stamps in analytics are in Coordinated Universal Time (UTC). The time-and-date stamps include day start and end times, session times, and any other time markers in your agent's data.
+Note
+The
+Monitor
 page doesn't show analytics for activity you complete when you test your agent in Copilot Studio by using the
 test panel
 .
 Grant limited view-only access to analytics
 If you're
```

---

### 2. Customer Satisfaction

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-improve-agent-effectiveness
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:bf318c56c7c3ef43787d049387e2a4838c16a58afbf38024876808fb964bffa5

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)

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
@@ -19,18 +19,26 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Analyze conversational agents
+Monitor conversational agents
 Feedback
 Summarize this article for me
-The
-Analytics
+Note
+Features in this article are powered by the
+standard harness
+, which uses the billing options described in
+Licensing for agents powered by the standard harness
+. Learn how to access standard features in
+Access standard agents and agent flows
+.
+The
+Monitor
 page in Copilot Studio provides an aggregated insight into the overall effectiveness of your agent across
 analytics sessions
 . The page is divided into core areas that focus on different performance contexts. The page also displays an
 Overview
 area that provides high-level, key performance indicator (KPI) metrics for your agent, a
 Savings
-area that analyzes time and cost savings attributable to your agent or your agent's tools, and a
+area that displays time and cost savings attributable to your agent or your agent's tools, and a
 Summary
 area that provides key analytic insights into your agent's performance.
 There are four core sections to focus on when reviewing and improving conversational agent effectiveness.
@@ -40,7 +48,7 @@ Overview
 , and
 Savings
-section shows key analytics insights about your agents along with billing and cost savings statistics; see
+section shows key insights about your agents along with billing and cost savings statistics; see
 Summary
 ,
 Overview
@@ -60,8 +68,12 @@ Custom metrics
 The
 Custom metrics
-section lets you define up to three business-specific metrics in natural language and track how often each outcome appears across sampled sessions. Use these metrics to complement your standard analytics insights with indicators that reflect your agent's goals and business use. To learn how to create, test, and refine custom metr
```

---

## HIGH: Control Review Recommended

### 1. Planned Features (2026 Wave 1) [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:1ee629d14e5c1f641ed6d226fb593782dce18638f9a1afc764ec24ac75c883e5

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
--- +++ @@ -1,156 +1,510 @@-Table of contents
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

### 2. Human-in-the-Loop Workflows

**URL:** https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:90fc417a8d26f3965adaf0ff836ba86b300d433e78b1d55fdd78875a15dc34a6

**Affected Controls:**
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`

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
@@ -144,8 +144,32 @@ and
 response
 parameters.
+Workflows support human-in-the-loop patterns through
+RequestPort
+, which pauses execution and waits for external input.
+approvalPort := workflow.RequestPort{
+ ID: "ApprovalPort",
+ Request: reflect.TypeFor[string](),
+ Response: reflect.TypeFor[bool](),
+}
+
+approval := approvalPort.Bind()
+finalize := workflow.NewExecutor("FinalizeExecutor", func(approved bool) string {
+ if approved {
+ return "Request approved by the human reviewer"
+ }
+ return "Request rejected by the human reviewer"
+}).Bind()
+
+wf, err := workflow.NewBuilder(approval).
+ AddEdge(approval, finalize).
+ WithOutputFrom(finalize).
+ Build()
+A
+RequestPort
+defines a typed request/response channel between the workflow and the outside world. When an executor reaches a request port, the workflow pauses and emits an external request event. The workflow resumes when an external response is provided.
 Handling Requests and Responses
-An
+A
 RequestPort
 emits a
 RequestInfoEvent
@@ -215,6 +239,40 @@ See this
 full sample
 for a complete runnable file.
+Listen for
+workflow.RequestInfoEvent
+, create a response from the request, and resume the run with that response:
+run, err := inproc.Default.Run(ctx, wf, "Approve deployment to production?")
+if err != nil {
+ return err
+}
+
+var request *workflow.ExternalRequest
+for evt := range run.NewEvents() {
+ if requestEvent, ok := evt.(workflow.RequestInfoEvent); ok {
+ request = requestEvent.Request
+ break
+ }
+}
+
+response, err := request.CreateResponse(true)
+if err != nil {
+ return err
+}
+
+if _, err := run.Resume(ctx, response); err != nil {
+ return err
+}
+
+for evt := range run.NewEvents() {
+ if output, ok := evt.(workflow.OutputEvent); ok {
+ fmt.Println(output.Output)
+ }
+}
+Tip
+See the
+human-in-the-loop sample
+for a complete runnable file.
 Human-in-the-Loop with Age
```

---

### 3. Message Center

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/message-center?view=o365-worldwide
**Section:** Microsoft 365 Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:e4657aeb287287ff7cd9faef2e4682c0280f4af362e812503d9e6e925efc4b75

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`

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
@@ -107,8 +107,10 @@ New feature
 ,
 Retirement
+,
+User impact
 , or
-User impact
+Deferred feature
 messages.
 Under
 Message state
@@ -264,9 +266,9 @@ Plan for change
 : Informs you of changes to Microsoft 365 that might require you to act to avoid disruptions in service. For example, we let you know about changes to system requirements or about features that are being removed. We try to provide at least 30 days' notice of any change that requires an admin to act to keep the service running normally.
 Stay informed
-: Tells you about new or updated features we're turning on in your organization. announced first in the
-Microsoft 365 Roadmap
-.
+: Tells you about new or updated features we're turning on in your organization. Announced first in the
+Microsoft AI at Work Roadmap
+, formerly known as the Microsoft 365 Roadmap.
 Also lets you know about planned maintenance in accordance with our Service Level Agreement. Planned maintenance might result in down time, where you or your users can't access Microsoft 365, a specific feature, or a service such as email or OneDrive.
 Message ID
 Microsoft tracks our Message center posts by message ID. You can refer to this ID if you want to give feedback or if you call Support about a particular message.

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Power Platform Inventory
**URL:** https://learn.microsoft.com/en-us/power-platform/admin/power-platform-inventory
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:f39bef5630ab3956fafdb52bfe8ac15e4a98c399b23175544bf352354fd755e8

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-messages-capacity | https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-copilot-credits-capacity |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |
| https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features | https://www.microsoft.com/en-us/microsoft-365/roadmap?msockid=3e2528ce9674620625c73e4c970263de&filters=%5B%22Microsoft+Copilot+Studio%22%5D#Roadmap |

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*