# Microsoft Learn Documentation Changes

**Run Date:** 2026-10-16
**Run Time:** 2026-10-16T10:54:18.447667+00:00
**Total URLs Checked:** 228

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 3 |
| HIGH Changes | 2 |
| MEDIUM Changes | 3 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | environment-groups-rules | HIGH | 2.2 | Update portal-walkthrough |
| 2 | wp-data-loss-prevention | HIGH | 3.7, 1.14, 1.5, 1.28, 2.24, 2.7 | Update portal-walkthrough |
| 3 | ...pilot-studio-copilot-credits-capacity | HIGH | 2.27 | Update portal-walkthrough |
| 4 | ...ower-platform/release-plan/2025wave2/ | CRITICAL | 1.27 | Review and update |
| 5 | ...ower-platform/release-plan/2026wave1/ | CRITICAL | 3.8, 1.18, 2.8, 2.3, 2.10 | Monitor |
| 6 | ...ilot-security-enhanced-admin-controls | CRITICAL | 1.18, 2.8, 2.3 | Monitor |
| 7 | ...-governance-agentic-center-enablement | CRITICAL | None | Monitor |
| 8 | whats-new | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Environment Group Rules

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules
**Section:** Power Platform Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:bf0f92f91bbc0644c4730e973ac76b648af6e98b8f6687b49213ca96faee9016

**Affected Controls:**
- Control 2.2: Control 2.2: Environment Groups and Tier Classification
  - File: `controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.2/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/2.2/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -32,52 +32,58 @@ 1
 Accessing transcripts from conversations in Copilot Studio agents
 2
-Advanced connector policy (preview)
+Advanced connector policy
 3
+Advanced connector policies only (preview)
+4
 AI prompts
-4
+5
 AI-generated descriptions (preview)
-5
+6
 AI-powered Copilot features
-6
+7
 Back-up retention
-7
+8
 Cost controls - Draw from tenant credit pool
-8
+9
 Default deployment pipeline (preview)
-9
+10
 Generative AI settings
-10
+11
 External models
-11
+12
+Knowledge sources for agents
+13
 Maker guidelines (preview)
-12
+14
 Maker welcome content
-13
+15
 Power Apps component framework for canvas apps
-14
+16
 Preview and experimental AI models
-15
+17
 Release channel
-16
+18
 Sharing agents with Editor permissions
-17
+19
 Sharing agents with Viewer permissions
-18
+20
 Sharing controls for canvas apps
-19
+21
 Sharing controls for solution-aware cloud flows
-20
+22
 Sharing data between Copilot Studio and Viva Insights
-21
+23
+Skills in Copilot Studio
+24
 Solution checker enforcement
-22
+25
 Unmanaged customizations
-23
+26
 Usage insights
-24
+27
 Power Apps code apps
-25
+28
 Content security policy
 Note
 The rules that have "(preview)" in their name are in public preview, while rules without it are considered generally available.

```

---

### 2. DLP Policies (Power Platform)

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:c88cdf219cf2d53105cea1d47c1a92e97d76bb0d12ee9e0d28f30d66d4ac7020

**Affected Controls:**
- Control 3.7: Control 3.7: PPAC Security Posture Assessment
  - File: `controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 2.24: Control 2.24: Agent Feature Enablement and Restriction Governance
  - File: `controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md`
- Control 2.7: Control 2.7: Vendor and Third-Party Risk Management
  - File: `controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.25/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.5/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.5/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/advanced-implementations/mcp-server-governance/index.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -45,7 +45,7 @@ Virtual connectors are connectors that appear in data policies for administrators to control, but they're not based on a RESTful API. The proliferation of virtual connectors comes from data policies being one of the most popular governance controls in Power Platform. More of these types of "on/off" capabilities are expected to surface as rules within
 Environment groups
 .
-Microsoft provides several virtual connectors for governing Microsoft Copilot Studio. These connectors facilitate the ability to turn off various features of Copilots and chatbots.
+Microsoft provides several virtual connectors for governing Microsoft Copilot Studio. These connectors facilitate the ability to turn off various features of agents.
 Learn about virtual connectors and their role in
 data loss prevention in Microsoft Copilot Studio
 .
@@ -53,9 +53,11 @@ Advanced connector policies
 (ACP)
 don't support
-virtual connectors and won't add support in the future. ACP's singular focus is to be the most robust governance feature for real certified connectors. The following transition paths apply to virtual connectors:
+virtual connectors and there are no plans to add support in the future. ACP's singular focus is to be the most robust governance feature for real certified connectors. The following transition paths apply to virtual connectors:
 Copilot Studio virtual connectors
-are evolving into their own dedicated governance rules, separate from both data policies and ACP.
+are evolving into their own dedicated governance rules, separate from both data policies and ACP. See
+Configure skills in the Power Platform admin center
+.
 Desktop Flow virtual connectors
 are transitioning to certified connectors, at which point ACP manages them.
 Model Context Protocol (MCP) connectors

```

---

### 3. Copilot Studio Copilot Credits Capacity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/manage-copilot-studio-copilot-credits-capacity
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:dbf2ae5eb155c479fa75171ee38d6bbafe07f0c208fbda693695bcfa5468b858

**Affected Controls:**
- Control 2.27: Control 2.27: Consumption-Entitlement Governance
  - File: `controls/pillar-2-management/2.27-consumption-entitlement-governance.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.27/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -23,7 +23,7 @@ Feedback
 Summarize this article for me
 Important
-Microsoft Copilot Studio is a multi-harness platform. The Power Platform admin center (PPAC) provides a unified capacity management experience across all Copilot Studio harnesses, including Copilot Chat, Standard, and GitHub Copilot. Administrators can view capacity and consumption data at the agent and environment level in PPAC.
+Microsoft Copilot Studio is a multi-harness platform. The Power Platform admin center (PPAC) provides a unified capacity management experience across all Copilot Studio harnesses, including Copilot Chat, Standard, and GitHub Copilot. Administrators can view capacity and consumption data at the environment and agent level, and can download consumption reports by environment, agent, or user.
 The Microsoft Copilot Studio capacity management experience in the Power Platform admin center enables administrators to manage Copilot Studio credit capacity and monitor overall capacity consumption. This experience provides an overview of the licensing models in use. Administrators can efficiently manage their available session capacity.
 View summary information
 Sign in to the
@@ -95,6 +95,36 @@ Select the download type you need: environment, agent, or user.
 Download the report.
 Start with the environment report to identify where consumption occurs. Then use the agent or user report to narrow the investigation.
+What the reports show
+The reports show consumption by environment and agent. For agents powered by the standard harness, the user report also shows consumption by user. The detailed report adds the
+Product / AI feature
+,
+Channel
+,
+LLM model
+, and
+Knowledge sources / Tool used
+columns.
+In the user report, usage from sessions where the user didn't sign in, for example on an agent that doesn't require authentication, can appear under the user ID
+00000000-0000-0000-0000-000000000000
+with no user name.
+The reports don't show:
+Usage for a single conversat
```

---

## HIGH: Control Review Recommended

### 1. Release Plans (2025 Wave 2)

**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:57494d27fb604a45ba0ee792dacc7eae4285d23f39cc4971c7d2066af0f893b9

**Affected Controls:**
- Control 1.27: Control 1.27: AI Agent Content Moderation Enforcement
  - File: `controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.27/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -23,12 +23,12 @@ Feedback
 Summarize this article for me
 Important
-Release Plans will no longer be published starting in September 2026.
-New Dynamics 365, Power Platform, and Dataverse capabilities will be published to the
-AI at Work roadmap
-beginning in September 2026. Existing release plans will remain available for historical reference until further notice. Learn more about the roadmap and disclosure changes at
-One always-on roadmap: Dynamics 365, Power Platform and Dataverse join the AI at Work roadmap
-.
+As of October 2026, this content is archived and no longer maintained.
+Information on this page may not reflect the latest product plans, features, or guidance. For current roadmap information across Dynamics 365, Power Platform, Dataverse, Microsoft 365, and Copilot, visit the
+roadmap
+. Continue to use
+Microsoft Learn
+for authoritative product guidance and documentation.
 The Microsoft Power Platform release plan for the 2025 release wave 2 announces the latest updates to customers as features are prepared for release. You can browse the release plan here
 online
 (updated throughout the month), view it in the

```

---

### 2. Copilot Studio guidance hub — What's new

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:1d2009d7b7391652008632b93ccd0243bd5ad52ca6859d5ec57eb89f4d91cc60

**What Changed:**
```diff
--- +++ @@ -23,6 +23,12 @@ Feedback
 Summarize this article for me
 Get the latest information about what's new and what changed in the Copilot Studio guidance hub.
+October 2026
+New reference architecture in the
+Power Platform and Copilot Studio Architecture Center
+on
+using Copilot Studio to modernize employee HR support with a multi-agent solution
+.
 September 2026
 New articles
 Compare Copilot Studio agent harnesses

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Release Plans (2026 Wave 1)
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:25e688c4d1a8f15d9a6e44c666b97558a0571d1647f3a4adbc6f3ef62269529f

---

### 2. Enhanced Admin Controls [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:557ec9afc8c7a601b42bf4c5cb6f2c68b9d2421de4f8c10e641093aa93b2c722

---

### 3. Agentic Center of Enablement [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/automate-governance-agentic-center-enablement
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:6c45c841ab271ebf6815d0cec7656de95c3812d4c99469dc3653eb104fd26d57

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*