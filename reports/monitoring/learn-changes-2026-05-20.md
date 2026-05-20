# Microsoft Learn Documentation Changes

**Run Date:** 2026-05-20
**Run Time:** 2026-05-20T09:36:49.633569+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| HIGH Changes | 4 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | agent-365-overview | HIGH | 3.8, 2.25 | Review and update |
| 2 | trainable-classifiers-learn-about | HIGH | 1.13 | Review and update |
| 3 | private-link-overview | HIGH | 1.20 | Review and update |
| 4 | whats-new | HIGH | None | Review and update |

---

## HIGH: Control Review Recommended

### 1. Agent 365 Overview Page (M365 Admin)

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide
**Section:** Microsoft Agent 365 & Agent Essentials
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.25/powershell-setup.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -69,7 +69,7 @@ Agent overview
 pane is displayed.
 Important
-Certain features are available within Microsoft 365 admin center based on services licensed in your subscription. Based on your subscription, you may see Agent 365 branding and additional agent related features and details. To view your licensed subscriptions in the
+Certain features are available within Microsoft 365 admin center based on services licensed in your subscription. To view your licensed subscriptions in the
 Microsoft 365 admin center
 , select
 Billing
@@ -77,6 +77,8 @@ Licenses
 >
 Subscriptions
+. For more information, see
+Plans and licensing
 .
 Agent overview summary
 Administrators use the Agent overview to identify and act on critical governance tasks required to maintain compliance, mitigate risk, and ensure agents are properly managed across the organization. These actions are surfaced through actionable insights in the dashboard and provide direct pathways to resolve governance gaps.
@@ -150,6 +152,7 @@ Data & tools by agent type
 .
 Agent card details
+The agents overview provides a dashboard view with cards containing specific information and status related to agents.
 Hero metrics for agent impact
 Hero metrics provide a high-level summary of the most critical indicators of agent scale and engagement.
 Agent registry

```

---

### 2. Trainable Classifiers

**URL:** https://learn.microsoft.com/en-us/purview/trainable-classifiers-learn-about
**Section:** Microsoft Purview
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 1.13: Control 1.13: Sensitive Information Types (SITs) and Pattern Recognition
  - File: `controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.13/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -23,7 +23,7 @@ Feedback
 Summarize this article for me
 Trainable Classifiers
-This categorization method is well suited to content that can't be easily identified using either the manual or automated pattern-matching methods. This method of categorization is designed to use a classifier to identify an item based on what the item is, not by elements that are in the item (pattern matching). A classifier learns how to identify a type of content by looking at hundreds of examples of the content you want to detect.
+This categorization method is well suited to content that can't be easily identified using either the manual or automated pattern-matching methods. A classifier learns how to identify a type of content by looking at hundreds of examples of the content you want to detect.
 Note
 In Preview:
 You can view the trainable classifiers in content explorer by expanding
@@ -59,7 +59,7 @@ Language limitation:
 Support for custom classifiers is limited to English.
 When the Microsoft provided pretrained classifiers don't meet your needs, you can create and train your own classifiers. There's more work involved with creating your own, but they're better tailored to your organization's needs.
-To create a custom trainable classifier, you start by feeding it one set of examples that are definitely in the category, and another set of examples that are definitely not. Microsoft Purview processes those examples and the classifier then makes predictions as to whether any given item falls into the category you're building. You then confirm the results, sorting out the true positives, true negatives, false positives, and false negatives to help increase the accuracy of its predictions.
+To create a custom trainable classifier, you start by feeding it one set of examples that are definitely in the category, and another set of examples that are definitely not in the category. Microsoft Purview processes those examples and the classifier then makes predictions as to whe
```

---

### 3. Azure Private Link

**URL:** https://learn.microsoft.com/en-us/azure/private-link/private-link-overview
**Section:** Azure Services
**Classification:** HIGH (Feature availability)

**Affected Controls:**
- Control 1.20: Control 1.20: Network Isolation and Private Connectivity
  - File: `controls/pillar-1-security/1.20-network-isolation-private-connectivity.md`

**What Changed:**
```diff
--- +++ @@ -51,9 +51,9 @@ network security perimeter
 to set up a secure logical boundary. Network security perimeter restricts communication to services within its perimeter, and it allows nonperimeter public traffic through inbound and outbound access rules.
 Important
-Network security perimeter is now generally available in all Azure public cloud regions. For information on supported services, see
+Network security perimeter is now generally available in all Azure public cloud regions and in Azure Government regions (US Gov Virginia, US Gov Texas, US Gov Arizona, US DoD East and US DoD Central). For information on supported services, see
 Onboarded private link resources
-for supported PaaS services."
+for supported PaaS services.
 Key benefits
 Azure Private Link provides the following benefits:
 Privately access services on the Azure platform

```

---

### 4. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -114,6 +114,10 @@ ,
 Apply meeting label to artifacts
 , automatically applies the meeting's sensitivity label to recordings and their transcripts (.mp4 files), and to meeting notes (.loop files).
+In preview
+: You can now see the sync status of your sensitivity label publishing policies on the
+Label policies
+page, giving you visibility into when label policy updates are fully synced across Microsoft 365.
 April 2026
 Collection Policies
 Preview

```

---

## Errors

No errors detected.

---

*Generated by `scripts/learn_monitor.py` (unified monitoring framework)*