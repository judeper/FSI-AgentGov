# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-21
**Run Time:** 2026-07-21T08:30:50.928764+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 2 |
| MEDIUM Changes | 1 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | security-and-governance | MEDIUM | 1.1, 1.4, 1.3, 1.8, 1.28, 1.5, 2.8 | Update portal-walkthrough |
| 2 | restricted-access-control | HIGH | 1.3, 4.1 | Review and update |
| 3 | ai-agent-inventory | HIGH | 1.21 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Security and Governance

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Section:** Copilot Studio
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:95af8e4aa2f94eeb8ca33a0c473ed830908a06ef06b02380292405436d135923

**Affected Controls:**
- Control 1.1: Control 1.1: Restrict Agent Publishing by Authorization
  - File: `controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md`
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.8: Control 1.8: Runtime Protection and External Threat Detection
  - File: `controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`
- Control 1.28: Control 1.28: Policy-Based Agent Publishing Restrictions
  - File: `controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md`
- Control 1.5: Control 1.5: Data Loss Prevention (DLP) and Sensitivity Labels
  - File: `controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md`
- Control 2.8: Control 2.8: Access Control and Segregation of Duties
  - File: `controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.8/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -80,11 +80,11 @@ Microsoft Security Development Lifecycle Practices
 .
 Data processing and license agreements
-The Copilot Studio service is governed by your commercial license agreements, including the
+Your commercial license agreements, including the
 Microsoft Product Terms
 and the
 Data Protection Addendum
-. For the location of data processing, refer to the
+, govern the Copilot Studio service. For the location of data processing, refer to the
 geographical availability documentation
 .
 Compliance with standards and practices

```

---

## HIGH: Control Review Recommended

### 1. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:2bb494e7815fdbf399ced0793afb68594f6d7e3eeeaedadc8ad432a452a27060

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`

**What Changed:**
```diff
--- +++ @@ -22,12 +22,15 @@ Restrict SharePoint site access with Microsoft 365 groups and Microsoft Entra security groups
 Feedback
 Summarize this article for me
-Restricted site access control helps prevent oversharing by designating access of SharePoint sites and its content to users in a specific group. Users not in the specified group can't access the site or its content, even if they had prior permissions or a shared link. You can apply this policy on Microsoft 365 group-connected, Teams-connected, and nongroup connected sites by using Microsoft 365 groups or Microsoft Entra security groups.
-Site access restriction policies take effect when a user attempts to open a site or access a file. Users with direct permissions to the file can still view files in search results. However, they can't access the files if they're not part of the specified group.
-Restricting site access through group membership can minimize the risk of oversharing content. For insights into data sharing, see
-Data access governance reports
-.
-What do you need to restrict site access?
+Restricted site access control (also referred to as
+restricted access control
+or
+site access restriction
+) helps prevent oversharing by designating access of SharePoint sites and its content to users in a specific control group. Users who aren't in the specified control group can't access the site or its content, even if they had prior permissions or a shared link. You can apply this policy on Microsoft 365 group-connected, Teams-connected, and nongroup connected sites by using Microsoft 365 groups or Microsoft Entra security groups.
+Site access restriction policies take effect when a user attempts to open a site, access a file, or search for content in organization search experiences and Microsoft Copilot experiences.
+Note
+Shared channel sites and private channel sites are separate site collections from the Microsoft 365 group-connected site used by standard channels. Restricted site access policies 
```

---

### 2. Microsoft Defender - AI Agent Inventory

**URL:** https://learn.microsoft.com/en-us/defender-xdr/security-for-ai/ai-agent-inventory
**Section:** Microsoft Defender
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:4ea0f6167db3547b56c283330e67c5c01f083be3933a5c600247675bb5b6afd6

**Affected Controls:**
- Control 1.21: Control 1.21: Adversarial Input Logging
  - File: `controls/pillar-1-security/1.21-adversarial-input-logging.md`

**What Changed:**
```diff
--- +++ @@ -6,7 +6,7 @@ Table of contents
 Read in English
 Add
-Add to Plans
+Add to plan
 Edit
 Copy Markdown
 Print
@@ -22,41 +22,120 @@ Discover AI agents and assess security posture using Microsoft Defender
 Feedback
 Summarize this article for me
-Microsoft Defender lets you discover all of the Microsoft Agent 365 managed agents in your organization and view their configuration details using two experiences in the Microsoft Defender portal:
-Advanced Hunting
-A dedicated AI agent inventory experience
-This inventory includes cloud agents built with Microsoft Copilot Studio, Microsoft Foundry, and
-supported non-Microsoft cloud platforms
-, and
-local AI agents
-discovered on endpoints.
-This article explains how to discover AI agents, assess their security posture, and use the AI agent inventory in the Microsoft Defender portal.
+Microsoft Defender provides a centralized inventory of AI agents in your organization and assesses their security posture.
+The inventory includes:
+Agents built with Microsoft Copilot Studio, Microsoft Foundry, Microsoft 365, and
+supported non-Microsoft platforms
+.
+Local AI agents
+discovered on endpoint devices.
+Use the
+AI Agents
+page in the Microsoft Defender portal to review agent configuration, risk levels, risk indicators, recommendations, alerts, tools, identities, and related security context. You can also query agent inventory and configuration data by using Advanced Hunting.
 Prerequisites
-Enable security for AI agents, including the Microsoft 365 app connector. See
+Enable security for AI agents, including the Microsoft 365 connector. See
 Enable security for AI agents using Microsoft Defender
 .
 To discover local AI agents that run on endpoints, set up
 AI agent runtime protection in Microsoft Defender for Endpoint
-. Discovery requires Microsoft Defender for Endpoint and Microsoft Defender Antivirus in active mode. Local agents are onboarded separately from cloud agents.
-Discover AI agents and assess security pos
```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Security and Governance
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:95af8e4aa2f94eeb8ca33a0c473ed830908a06ef06b02380292405436d135923

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