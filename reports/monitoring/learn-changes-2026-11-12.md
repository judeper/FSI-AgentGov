# Microsoft Learn Documentation Changes

**Run Date:** 2026-11-12
**Run Time:** 2026-11-12T14:46:12.938999+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 3 |
| Redirects | 8 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | monitor-copilot-studio | HIGH | 3.2 | Review and update |
| 2 | alerts | HIGH | None | Review and update |
| 3 | business-continuity-disaster-recovery | HIGH | 2.4 | Update portal-walkthrough |
| 4 | whats-new | CRITICAL | 2.10, 2.5, 2.25 | Review and update |
| 5 | agent-id-governance-overview | HIGH | 2.26, 1.11, 3.6 | Update portal-walkthrough |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:b25bfb292eb92235ac0e14abf6478ef639afbdf6fd34d3565f561310053937e6

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -133,7 +133,7 @@ Because customers retain control of when and whether to trigger a cross-region failover, Microsoft doesn't publish a cross-region RTO commitment. Customers can monitor real-time replication lag directly in the Power Platform admin center to inform their own recovery decisions. It's important to note that when Power Platform solutions connect to external systemsâsuch as SQL Server, REST APIs, or other third-party servicesâthe RPO of those integrations are governed by the availability and recovery capabilities of the respective target systems, and fall outside the scope of Power Platform's resiliency commitments.
 Frequently asked questions (FAQs)
 Why use self-service disaster recovery?
-Super storms, natural calamities, and unforeseen political uncertainties that can bring down an entire region are becoming more common. To minimize the impact of a disaster that brings down an entire region, maintain an asynchronous copy in a remote region. You might also want to maintain a copy in a remote region for compliance audits.
+Superstorms, natural calamities, and unforeseen political uncertainties that can bring down an entire region are becoming more common. To minimize the impact of a disaster that brings down an entire region, maintain an asynchronous copy in a remote region. You might also want to maintain a copy in a remote region for compliance audits.
 Self-service disaster recovery gives you control to fail over to a secondary region with the push of a button and fail back with the push of a button when the primary region is restored to ensure business continuity. You can also simulate the primary region being down to run a real failover and fail back to the secondary region to test a real compliance drill. Run drills with a copy of the production environment to avoid any downtime.
 Why do I need self-service disaster recovery if I already have a secondary copy maintained in a remote, secondary region?
 For the public cloud, the syst
```

---

### 2. Governing Agent Identities

**URL:** https://learn.microsoft.com/en-us/entra/id-governance/agent-id-governance-overview
**Section:** Microsoft Entra Agent ID
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:570c94e24ca32c42686a545b7db1f2c12aa589710b2579e683e1569538dba7b0

**Affected Controls:**
- Control 2.26: Control 2.26: Entra Agent ID — Identity Governance for Agents
  - File: `controls/pillar-2-management/2.26-entra-agent-id-identity-governance.md`
- Control 1.11: Control 1.11: Conditional Access and Phishing-Resistant MFA
  - File: `controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md`
- Control 3.6: Control 3.6: Orphaned Agent Detection and Remediation
  - File: `controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.2/sponsorship-lifecycle-workflows.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.26/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -22,8 +22,8 @@ Governing Agent Identities
 Feedback
 Summarize this article for me
-Microsoft Entra allows you to ensure that the right people have the right access to the right apps and services at the right time. With the addition of the Microsoft agent identity platform, managing the access rights of agents in the same way is just as important in the governance lifecycle of your organization's identities. The Microsoft agent identity platform introduces the concept of Agent Identities (IDs). Agent identities are accounts within Microsoft Entra ID that provide unique identification and authentication capabilities for AI agents.
-This allows agent identities to be governed with Microsoft Entra features in the same style as you would govern human identities. With Agent identities, you can govern and manage the identity and access lifecycle of agents, ensuring the agents have a responsible person providing oversight throughout the agent lifecycle and agent's access does not persist longer than it is needed. This article provides an overview of how Microsoft Entra can be utilized to govern agent identities.
+Microsoft Entra allows you to ensure that the right people have the right access to the right apps and services at the right time. With the addition of the Microsoft agent identity platform, managing the access rights of agents in the same way is just as important in the governance lifecycle of your organization's identities. The Microsoft agent identity platform introduces the concept of Agent Identities (IDs). Agent identities are accounts within Microsoft Entra ID that provide unique identification, authentication and authorization capabilities for AI agents.
+This allows agent identities to be governed with Microsoft Entra features in the same style as you would govern human identities. With Agent identities, you can govern and manage the identity and access lifecycle of agents, ensuring the agents have a responsible person providing oversight throu
```

---

## HIGH: Control Review Recommended

### 1. Monitor Microsoft Copilot Studio

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/monitor-copilot-studio
**Section:** Power Platform Administration
**Classification:** HIGH (UI element names)
**Content-Hash:** sha256:bde14378f7ca053e0682c56d4db57407c3c4807d2bd77e374e451474b6316dde

**Affected Controls:**
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`

**What Changed:**
```diff
--- +++ @@ -39,7 +39,7 @@ .
 The
 Copilot Studio
-page displays the metrics for conversational and autonomous agents created in Copilot Studio. Agents that use GitHub Copilot use AI to map sessions with outcomes more accurately. As a result, the metrics generated for these agents can appear in Monitor up to 48 hours after usage.
+page displays the metrics for conversational and autonomous agents created in Copilot Studio. For agents that use GitHub Copilot, Copilot Studio uses AI to review each completed session and assign it a single outcome, such as resolved, escalated, or abandoned. Monitor then uses that outcome to decide whether the session counts as a success or a failure. The AI analysis runs after the session ends, so metrics for these agents can appear in Monitor up to 48 hours after usage.
 Copilot Studio metrics and recommendations
 Metric definitions
 Type
@@ -54,6 +54,73 @@ Recent agent sessions
 The number of distinct user sessions in an agent in one day. A session begins when a user opens the agent and ends after a period of inactivity or when the agent is closed.
 Generally available
+Session outcome mapping
+The following table shows how Monitor counts each session outcome for agents that use GitHub Copilot.
+Session outcome
+What it means
+Agent session success rate
+Recent agent sessions
+Resolved â confirmed
+The user confirmed that their need was met.
+â+ Success
+Counted
+Resolved â implied
+The user's need appears to be met, even though the user didn't explicitly confirm it.
+â+ Success
+Counted
+Escalated â system intended
+The agent handed off the session because of an escalation rule the maker configured. The agent did what it was designed to do.
+â+ Success
+Counted
+Escalated â user requested
+The user asked to talk to a person.
+â Failure
+Counted
+Escalated â system unintended
+The session was escalated because the agent, or a tool or flow it called, failed.
+â Failure
+Counted
+Unresolved â agent failure
+The agen
```

---

### 2. Monitor Alerts

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/monitoring/alerts
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:1ff9f1c463b85b758dd5f255fb0112658184cc3566d080bdf925270e9376ed26

**What Changed:**
```diff
--- +++ @@ -209,10 +209,6 @@ metric for that app. Use the
 Review period
 list above the chart to switch between views.
-Note
-Currently, the
-Data review period
-is in preview and is only available for code apps.
 Select
 Save
 .
@@ -603,6 +599,8 @@ or an
 Environment administrator
 to create and manage alerts.
+How many alert rules can I create?
+You can create up to 10 alert rules with a 1-hour data review period and up to 50 alert rules with a 24-hour data review period for a total of up to 60 alert rules. Hourly alert rules that are turned off still count towards the limit of 10, so delete hourly alert rules that you aren't using. Alert rules with a 24-hour data review period that are turned off don't count towards the alert rule limit.
 What environments are supported?
 All environment types, such as production, sandbox, trial, and developer environment types are supported, but they must be a managed environment. You select the environment in the
 ID
@@ -673,6 +671,16 @@ as the metric, it only monitors the TTI or TTFL of the
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
+Can hourly alerts be opted into the 'When an alert fires' trigger on the Power Platform for Admi
```

---

### 3. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:591f5f6eb2270da2283a1436f2dc88119824267a4ad1763e0ed8a20da5ad8355

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -31,6 +31,58 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+October 2026
+(Preview) Build agents powered by the new
+Customer Conversation harness
+to handle customer-facing conversations over speech and chat, with specialized sub-agents that can escalate unresolved issues to a human representative, similar to a contact center. Start
+building from Copilot Studio or the Microsoft Contact Center Intelligence portal
+âboth use the same authoring experience, but only the portal lets you connect the agent to a live contact center. Agents on this harness use Copilot Credits for usage-based billing.
+Control which
+knowledge sources
+makers can add to their agents from the Power Platform admin center. Restrict access to local file uploads, SharePoint and OneDrive, or public websitesâindependently or togetherâto match your organization's data governance policies.
+(General availability) Use
+Work IQ
+, now added by default to every new agent powered by the GitHub Copilot harness, to ground your agent's responses in real-time context from your organization's files, emails, meetings, and chats. Write operations are enabled by default, subject to your organization's permissions and policies.
+Keep your agent on its current AI model for up to 30 days after Copilot Studio
+upgrades it to a new default
+, giving you time to test and migrate before support for the retired model ends.
+Connect MCP-compatible tools, like Visual Studio Code and GitHub Copilot CLI, to
+Copilot Studio MCP
+so you can create, test, deploy, and monitor your agents and workflows without leaving the tool you already use.
+(Preview) Ask Copilot Studio to
+upgrade an agent
+from the standard harness to the GitHub Copilot harness. The upgrade carries over instructions, tools, and prompts, rebuilds topics as skills or workf
```

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
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