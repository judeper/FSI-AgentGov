# Microsoft Learn Documentation Changes

**Run Date:** 2026-06-05
**Run Time:** 2026-06-05T09:53:49.503923+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 2 |
| MEDIUM Changes | 5 |
| Redirects | 1 |
| Errors | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | analytics-overview | MEDIUM | 2.6, 2.5, 2.9, 3.2, 3.10 | Update portal-walkthrough |
| 2 | whats-new | HIGH | 2.5, 2.10, 2.25 | Review and update |
| 3 | planned-features | MEDIUM | 1.4, 2.17, 2.25, 3.8 | Review optional |
| 4 | ...ring-detecting-credential-oversharing | HIGH | 1.18, 2.3, 2.8, 3.8 | Review and update |
| 5 | whats-new | MEDIUM | None | Review optional |
| 6 | dlp-policy-reference | MEDIUM | None | Review optional |
| 7 | sit-create-a-keyword-dictionary | MEDIUM | 1.13 | Review optional |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Analytics

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)

**Affected Controls:**
- Control 2.6: Control 2.6: Model Risk Management (OCC Bulletin 2026-13 / SR 26-2 — formerly OCC 2011-12 / SR 11-7)
  - File: `controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.9: Control 2.9: Agent Performance Monitoring and Optimization
  - File: `controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md`
- Control 3.2: Control 3.2: Usage Analytics and Activity Monitoring
  - File: `controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md`
- Control 3.10: Control 3.10: Hallucination Feedback Loop
  - File: `controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.5/portal-walkthrough.md` (CRITICAL)
- ⚠️ `playbooks/control-implementations/2.6/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -228,6 +228,8 @@ satisfaction score
 changes over time. Use this trend to identify periods where user sentiment declined or improved.
 To change the time range, select the time range dropdown at the top of the topic analytics panel.
+Related information
+Measure the return on investment (ROI) and business value of AI agents
 Feedback
 Was this page helpful?
 Yes

```

---

## HIGH: Control Review Recommended

### 1. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -35,6 +35,37 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+May 2026
+(General availability)
+Computer use
+is now generally available, letting your agents automate web and desktop apps by controlling browsers and desktop applications on behalf of users.
+Add a
+prompt node
+to an agent flow or workflow to make a single AI call with dynamic content and model selection, useful for scenarios like translation and structured data extraction.
+Add a
+Microsoft 365 Copilot node
+to a workflow to send prompts to Microsoft 365 Copilot or a specific agent, enabling automation scenarios like research and audit drafting.
+Configure
+consent-based recording
+on voice-enabled agents to ask callers for consent before recording, with configurable compliance behavior and retention settings.
+Use the
+agent inventory schema
+to discover and audit all Copilot Studio agents in your organization from the admin center, API, or Azure Resource Graph.
+(Preview) Review
+agent readiness and issue status
+from a consolidated status page that surfaces publishing errors, runtime issues, and configuration blocks with severity levels.
+Use
+asynchronous responses
+for agent flows to let long-running processes exceed the two-minute limit and return results to the agent when they complete.
+(Preview) Automatically create
+Microsoft Entra agent identities
+for each of your agents to scope connector permissions, Conditional Access policies, and DLP governance to individual agents.
+(Preview) Add
+computer use standalone tools
+to agents and agent flows for modular, reusable UI automation with built-in governance, model selection, and observability.
+(Preview) Choose
+Mistral Medium 3.5
+as the primary AI model for your agent, now available as an experimental option alongside Anthropic, xAI, and other supported providers
```

---

### 2. Safe Sharing / Credential Oversharing [Preview]

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/enforce-safe-sharing-detecting-credential-oversharing
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.18: Control 1.18: Application-Level Authorization and Role-Based Access Control (RBAC)
  - File: `controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -37,12 +37,8 @@ Business value
 This feature helps organizations reduce security risk by preventing agents and flows from being shared when they rely on unsafe identities, such as maker credentials. By detecting identity oversharing early and enforcing safeâsharing policies at publish and share time, customers can avoid identity leakage, privilege escalation, and unintended access - while still allowing makers to build and iterate safely within approved guardrails.
 Feature details
-When creating agents, Makers may inadvertently use credentials that rely on maker or system credentials not intended for reuse. When they publish the agent, users of the agent may have access to assets they're not intended to access.
-To help enforce the use of safe publishing and sharing policies, the oversharing detection and policy enforcement platform in Copilot Studio:
-Identifies agents that use connections marked as not safe for sharing.
-Surfaces clear guidance through inventory and advisor signals.
-Enables admins to block publishing or sharing of unsafe assets before exposure occurs.
-This enforcement is applied across design, publish, and share stages for makers, helping organizations avoid identity leakage and privilege escalation while maintaining maker productivity.
+When creating agents, makers may inadvertently use credentials that rely on maker or system credentials not intended for reuse. When they publish the agent, users of the agent may have access to assets they're not intended to access.
+This enforcement is applied across the design, publish, and share stages for makers, helping organizations avoid identity leakage and privilege escalation while maintaining maker productivity.
 Geographic areas
 Visit the
 Explore Feature Geography

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Analytics
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview
**Classification:** MEDIUM (General content update)

---

### 2. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)

---

### 3. Copilot Studio Kit — Compliance Hub
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Classification:** MEDIUM (General content update)

---

### 4. DLP Policy Reference
**URL:** https://learn.microsoft.com/en-us/purview/dlp-policy-reference
**Classification:** MEDIUM (General content update)

---

### 5. Keyword Dictionaries
**URL:** https://learn.microsoft.com/en-us/purview/sit-create-a-keyword-dictionary
**Classification:** MEDIUM (General content update)

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/architecture/ | https://learn.microsoft.com/en-us/agents/architecture/ |

---

## Errors

- **Encryption** (HTTP 404): https://learn.microsoft.com/en-us/power-platform/admin/manage-encryption-key

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*