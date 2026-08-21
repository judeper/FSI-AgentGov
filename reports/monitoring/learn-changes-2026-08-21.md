# Microsoft Learn Documentation Changes

**Run Date:** 2026-08-21
**Run Time:** 2026-08-21T06:48:56.912980+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 2 |
| Redirects | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | CRITICAL | 2.4 | Update portal-walkthrough |
| 2 | whats-new | CRITICAL | 2.25, 2.10, 2.5 | Review and update |
| 3 | endpoint-dlp-getting-started | HIGH | 1.17 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:dffc3ff9194ee448acb60cff9a23e15b17846ed49d1e2334da9d2f5be38bf154

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

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
@@ -22,7 +22,9 @@ Business continuity and disaster recovery
 Feedback
 Summarize this article for me
-Businesses expect their applications and customer data to be protected and resilient during unavoidable outages and disruptions. It's important to document a business continuity plan that minimizes the effects of outages. To recover and resume operations, make sure the plan lists stakeholders, processes, and specific steps.
+Note
+As of June 22, 2026, Self-Service Disaster Recovery (SSDR) is also available for Finance & Operations (F&O) applications. SSDR enables organizations to maintain an asynchronous secondary copy of their production environment in a paired Azure region and perform self-service failover, failback, and disaster recovery testing.
+Businesses expect their applications and customer data to be protected and resilient during unavoidable outages and disruptions. It's important to document a business continuity plan that minimizes the effects of outages. To recover and resume operations, ensure the plan lists stakeholders, processes, and specific steps.
 Microsoft provides business continuity and disaster recovery capabilities to all
 production type environments
 in Dynamics 365 and Power Platform software as a service (SaaS) applications. This article describes how Microsoft keeps your production data resilient during outages.
@@ -47,18 +49,15 @@ : Automated failover within the primary region means you don't need to contact Microsoft support for most disaster recovery scenarios.
 A limited number of customers in certain regions are transitioning to the improved architecture. Whether the region transitioned or is transitioning, the service always keeps a backup of environment data in more than one data center.
 Availability zones are far enough apart to reduce the chance of an outage affecting more than one zone, but close enough to m
```

---

## HIGH: Control Review Recommended

### 1. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:92e9f33e3316a3cfa5c625a143c1db7a23002eb904c62f1c585a17887a9bdfb3

**Affected Controls:**
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)

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
@@ -23,10 +23,6 @@ Feedback
 Summarize this article for me
 This article provides resources to learn about new features in Copilot Studio.
-Release plans
-For information about new features being released over the next few months that you can use for planning, see
-Release Planner
-.
 Released versions
 For information about the new features, fixes, and improvements released in the past few weeks, see
 Released versions of Microsoft Copilot Studio
@@ -35,13 +31,69 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+July 2026
+Starting in July 2026, Copilot Studio automatically creates a
+Microsoft Entra Agent ID
+for every new agent, and you can no longer opt out at the environment level.
+(Preview) Add a
+workflow
+or
+MCP server
+as a tool for agents powered by the GitHub Copilot harness to extend your agent with multistep automated processes or external services.
+(Preview) Submit your
+MCP server for Microsoft certification
+to give customers and administrators confidence that it meets Microsoft's expectations for reliability, security, compliance, and responsible operation.
+Deploy the same
+real-time agent
+across voice and digital messaging channels (digital messaging in preview) for consistent, natural, context-aware conversations. Use the
+GPT-5-Chat (Preview)
+model for greater voice customization and deployment flexibility, and
+monitor real-time agents
+with Application Insights.
+(Preview) Export
+environment-level agent telemetry
+to Azure Application Insights through the Power Platform admin center.
+(Preview) Let users
+attach files
+to a conversation and view
+files your agent creates
+during a conversation, for agents powered by the GitHub Copilot harness.
+June 2026

```

---

### 2. Onboard Devices

**URL:** https://learn.microsoft.com/en-us/purview/endpoint-dlp-getting-started
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:7402c66526e91fc5cdd53dcac9972f3746b869bc67997807dcd1602ccce3ef17

**Affected Controls:**
- Control 1.17: Control 1.17: Endpoint Data Loss Prevention (Endpoint DLP)
  - File: `controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md`

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
@@ -46,7 +46,7 @@ , ensure those users or devices or both are explicitly excluded from the policy. Failure to do so may lead to unintended policy enforcement behavior.
 Configure proxy on the Windows 10 or Windows 11 device
 If you're onboarding Windows 10 or Windows 11 devices, check to make sure that the device can communicate with the cloud DLP service. For more information, see,
-Configure device proxy and internet connection settings for Information Protection
+Configure device proxy and internet connection settings for Microsoft Purview Endpoint DLP
 .
 Windows 10 and Windows 11 Onboarding procedures
 For a general introduction to onboarding Windows devices, see:
@@ -126,6 +126,10 @@ For a general introduction to onboarding macOS devices, see:
 Onboard macOS devices into Microsoft Purview
 For specific guidance to onboarding macOS devices, see:
+Important
+There are important permission changes for Microsoft Purview Endpoint DLP in macOS 27. If you're onboarding or upgrading devices that run macOS 27, review the updated guidance before deployment. For more information, see
+Microsoft Purview Endpoint DLP on macOS 27 (Preview)
+.
 Article
 Description
 Intune

```

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