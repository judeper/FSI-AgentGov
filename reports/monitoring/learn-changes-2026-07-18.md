# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-18
**Run Time:** 2026-07-18T07:52:21.706397+00:00
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
| 1 | alerts | HIGH | None | Review and update |
| 2 | human-in-the-loop | HIGH | 2.17, 2.12 | Review and update |
| 3 | audit-copilot | HIGH | 1.21, 1.19, 1.6, 1.7, 1.14 | Review and update |

---

## HIGH: Control Review Recommended

### 1. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:8d64e8e5ae418747ffcf797bf487f29eafbd8e226583b1ec300d346d9fc4dfad

**What Changed:**
```diff
--- +++ @@ -34,14 +34,14 @@ Alert rules are alerts that admins create to monitor their resources. You can edit, delete, and turn an alert rule on or off. You can place alert rules on an environment and a specific resource.
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
+if the resource is in a managed environment.
 Select the
 + New alert rule
 link to create an alert. The admin center autofills the information for
@@
```

---

### 2. Human-in-the-Loop Workflows

**URL:** https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:eea1a6b6b36da68e6c75b178c65c88e9305b3c73461e013a5829ac320218ad47

**Affected Controls:**
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`

**What Changed:**
```diff
--- +++ @@ -144,6 +144,30 @@ and
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
 An
 RequestPort
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
 Human-in-the-Loop with Agent Orchestrations
 The
 RequestPort
@@ -231,11 +289,18 @@ RequestPort
 pattern, but the event payload contains a
 ToolApprovalRequestContent

```

---

### 3. Audit Copilot Activities

**URL:** https://learn.microsoft.com/en-us/purview/audit-copilot
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:236f234d44550df83fdf0a2488c6cb5eb8263a0c0b97ffcc7cca584c2c2a4592

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.7: Control 1.7: Comprehensive Audit Logging and Compliance
  - File: `controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.8/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/advanced-implementations/deny-event-correlation-report/deployment-guide.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -49,8 +49,8 @@ The system generates audit logs when an administrator performs activities related to Copilot settings, plugins, promptbooks, or workspaces. For more information, see
 Microsoft 365 Copilot activities
 .
-User activities with Copilot and AI applications
-The system automatically generates audit logs when a user interacts with Copilot or an AI Application. These audit records contain details about which user interacted with Copilot, when the interaction took place, and where it occurred. Audit records also include references to files, sites, or other resources Copilot and AI applications accessed to generate responses to user prompts.
+User activities with Copilot, Cowork, and AI applications
+The system automatically generates audit logs when a user interacts with Copilot, Cowork, or an AI application. These audit records contain details about which user interacted with Copilot, when the interaction took place, and where it occurred. Audit records also include references to files, sites, or other resources Copilot, Cowork, and AI applications accessed to generate responses to user prompts.
 Common properties in Copilot audit logs
 The following table outlines some of the common properties included in audit logs.
 Attribute
@@ -229,6 +229,28 @@ -
 Type
 contains values like docx, pptx, xlsx, TeamsMeeting, TeamsChannel, TeamsChat, and others.
+DLPEvaluationDeferred
+An integer bitmask that indicates DLP evaluation of one or more content processing stages couldn't be completed, so it's deferred for later reevaluation.
+The value is a bitmask where each bit represents a specific evaluation scenario that was deferred. Multiple deferred scenarios can be represented by combining bit values using a bitwise OR operation.
+-
+1 â Prompt
+: DLP evaluation of the user prompt was deferred.
+-
+2 â Response
+: DLP evaluation of the generated response was deferred.
+-
+4 â Grounding
+: DLP evaluation of grounding content was deferred.
+-
+8 â WebGr
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