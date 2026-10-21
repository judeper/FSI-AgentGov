# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-21
**Run Time:** 2026-10-21T11:19:42.972894+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 2 |
| Redirects | 2 |
| Errors | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | microsoft-365-copilot-overview | HIGH | 3.8 | Review and update |
| 2 | agent-365-overview | HIGH | 3.8, 2.25 | Review and update |

---

## HIGH: Control Review Recommended

### 1. M365 Copilot Overview

**URL:** https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:be77c24f45135c9878f2162b9e94823a8b90c2bd54c1d9d2806f49ca9bc24c7f

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -316,7 +316,8 @@ Frontier preview program
 .
 Note
-To ensure your users access Copilot Chat for work and education, instruct them to sign in with their Microsoft Entra account before accessing Copilot via the Microsoft Copilot app, copilot.cloud.microsoft, Copilot Chat in Edge, or productivity apps. Entry points for users signed in with a personal account (MSA):
+To ensure your users access Copilot Chat for work and education, instruct them to sign in with their Microsoft Entra account before accessing Copilot via the Microsoft Copilot app, copilot.cloud.microsoft, Copilot Chat in Edge, or productivity apps. These include a different background color for each account type, "Work" label under the user profile in the navigation pane, and the green data protection shield in their Microsoft Entra ID experience.
+Entry points for users signed in with a personal account (MSA):
 Microsoft Copilot app (web, desktop, mobile)
 Copilot Chat in Edge
 Copilot Chat in Outlook and Teams

```

---

### 2. Agent 365 Overview Page (M365 Admin)

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Policy language)
**Content-Hash:** sha256:770cc5dfe07296ce75b28ad8d4311b47b0b6db747ea0d777ec9403e2d82cc3d9

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.25/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -182,6 +182,7 @@ The agents overview provides a dashboard view with cards containing specific information and status related to agents.
 Hero metrics for agent impact
 Hero metrics provide a high-level summary of the most critical indicators of agent scale and engagement.
+Agent 365 licenses are required for data collection only for third-party agents, not for first-party agents.
 Agent registry
 - The total count of all agents available in your organization's catalog, including Microsoft-built, partner-built, and custom "line-of-business" agents. In both registry and usage, we refer to these types of agents as "Built by your organization". This Agent registry reflects the breadth of agents deployed across your tenant. In the
 Agent overview
@@ -192,13 +193,13 @@ to view your inventory in detail.
 Active users
 - The number of unique users who interacted with at least one agent up to the last 30 days by sending a prompt to an agent and receiving a response from that agent. These conversational interactions can occur in Microsoft experiences, such as Teams and Microsoft Copilot, as well as non-Microsoft channels. For Microsoft Copilot Studio agents, an active user is counted when a user sends a prompt to the agent. In most cases, prompts and responses have a one-to-one relationship. However, there are limited scenarios where a user may send a prompt but not receive a response. This difference is expected to have a minimal impact in practice. This definition will evolve in the future as we continue to improve how usage is measured.
-This metric begins when your organization activates Agent 365 licenses. It may reflect fewer than 30 days of data immediately after activation. As activity accumulates, the metric will progressively reflect a fuller 30-day view.
-Data collection starts at license activation. For related information, see
+For third-party agents, this metric begins when your organization activates Agent 365 licenses. It might reflect fewer than 30
```

---

## URL Redirects Detected

Consider updating microsoft-learn-urls.md:

| Original URL | Redirects To |
|--------------|--------------|
| https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-overview | https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-overview |
| https://learn.microsoft.com/en-us/microsoft-365/copilot/microsoft-365-copilot-enable-users | https://learn.microsoft.com/en-us/microsoft-365/copilot/enable-users |

---

## Errors

- **Copilot Control System Overview** (HTTP 404): https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/overview
- **Copilot Control System - Security and Governance** (HTTP 404): https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/security-governance
- **Copilot Control System - Management Controls** (HTTP 404): https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-controls/management-controls

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*