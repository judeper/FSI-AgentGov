# Microsoft Learn Documentation Changes

**Run Date:** 2026-05-22
**Run Time:** 2026-05-22T09:28:25.560432+00:00
**Total URLs Checked:** 229

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 1 |
| HIGH Changes | 8 |
| MEDIUM Changes | 3 |
| Redirects | 1 |
| Errors | 1 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | ip-firewall | HIGH | 1.20 | Update portal-walkthrough |
| 2 | ...copilot-studio/guidance/architecture/ | HIGH | 2.12, 2.17, 2.3 | Review and update |
| 3 | planned-features | MEDIUM | 1.4, 3.8, 2.17, 2.25 | Review optional |
| 4 | ...suggestions-based-work-copilot-studio | MEDIUM | None | Review optional |
| 5 | whats-new | MEDIUM | None | Review optional |
| 6 | microsoft-365-copilot-usage | HIGH | 3.8 | Review and update |
| 7 | agent-365-overview | HIGH | 3.8, 2.25 | Review and update |
| 8 | trainable-classifiers-learn-about | HIGH | 1.13 | Review and update |
| 9 | retention-policies-sharepoint | HIGH | 4.3 | Review and update |
| 10 | advanced-management | HIGH | 4.2, 4.1, 4.5, 4.6, 1.3 | Review and update |
| 11 | private-link-overview | HIGH | 1.20 | Review and update |
| 12 | whats-new | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. IP Firewall

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/ip-firewall
**Section:** Power Platform Administration
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 1.20: Control 1.20: Network Isolation and Private Connectivity
  - File: `controls/pillar-1-security/1.20-network-isolation-private-connectivity.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.1/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/2.1/verification-testing.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -312,12 +312,8 @@ I have configured the reverse proxy address correctly, but the IP firewall isn't working. What should I do?
 Make sure your reverse proxy is configured to send the client IP address in the forwarded header.
 IP firewall audit functionality isn't working in my environment. What should I do?
-IP firewall audit logs aren't supported in tenants enabled for bring-your-own-key
-(BYOK)
-encryption keys. If your tenant is enabled for bring-your-own-key, then all environments in a BYOK-enabled tenant are locked down to SQL only, therefore audit logs can only be stored in SQL. We recommend that you migrate to
+IP firewall audit logs aren't supported in tenants enabled for bring-your-own-key (BYOK) encryption keys. We recommend that you migrate to a
 customer-managed key
-. To migrate from BYOK to customer-managed key (CMKv2), follow the steps in
-Migrate bring-your-own-key (BYOK) environments to customer-managed key
 .
 Does IP firewall support IPv6 IP ranges?
 Yes, IP firewall supports IPv6 IP ranges.

```

---

## HIGH: Control Review Recommended

### 1. Architecting Agent Solutions

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/architecture/
**Section:** Copilot Studio
**Classification:** HIGH (UI element names)

**Affected Controls:**
- Control 2.12: Control 2.12: Supervision and Oversight (FINRA Rule 3110)
  - File: `controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md`
- Control 2.17: Control 2.17: Multi-Agent Orchestration Limits
  - File: `controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md`
- Control 2.3: Control 2.3: Change Management and Release Planning
  - File: `controls/pillar-2-management/2.3-change-management-and-release-planning.md`

**What Changed:**
```diff
--- +++ @@ -1,36 +1,94 @@+Table of contents
+Exit editor mode
+Ask Learn
+Ask Learn
+Reading mode
 Table of contents
 Read in English
+Add
+Add to plan
 Edit
+Copy Markdown
+Print
+Note
+Access to this page requires authorization. You can try
+signing in
+or
+changing directories
+.
+Access to this page requires authorization. You can try
+changing directories
+.
 Architecting agent solutions: Principles and patterns
-Guidance for architecting agents using established patterns and best practices.
+Feedback
+Summarize this article for me
+Agents are AI systems designed to assist users by interpreting data, making decisions, and automating tasks to enhance productivity and efficiency. AI agents can be:
+Conversational: Interacting with users via chat interfaces
+Autonomous: Running independently without continuous human direction
+Agents understand user requests and can combine language understanding with business logic.
+This
+Architecting agent solutions
+content provides guidance on essential principles and patterns for building secure, reliable agents, with the focus on Microsoft 365 Copilot. The framework provides standardized approaches for agent development, ensuring maximum return on investment while maintaining enterprise-grade security and compliance.
+This framework:
+Demonstrates leadership
+by establishing industry standards for agent architecture, reinforcing Microsoft's leadership in responsible AI.
+Provides recommended guidance
+for developing agents for Copilot, reducing confusion.
+Ensures quality and trust
+by prioritizing reliability, traceability, and responsible AI for secure, auditable solutions.
+Enables scale
+by empowering developers to build solutions that align to industry and Microsoft prescribed best practices, without the need for technical support from Microsoft.
+Aligns standards
+by standardizing terminology and evaluation criteria for Copilot and agent solutions organization-wide.
+Prerequisites
+To effectively use this framework, y
```

---

### 2. Copilot Usage Reports

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**What Changed:**
```diff
--- +++ @@ -19,17 +19,16 @@ Access to this page requires authorization. You can try
 changing directories
 .
-Microsoft 365 Copilot usage report - Microsoft 365 admin center
+Microsoft 365 Copilot usage report
 Feedback
 Summarize this article for me
 The Microsoft 365 Copilot usage report provides a summary of how users adopt, retain, and engage with Microsoft 365 Copilot and its associated enabled apps, including agent usage. For Copilot activity on a given day, the report typically becomes available within 72 hours of the end of that day (in UTC).
-For general information about Microsoft 365 Usage reports and to see a list of all available reports, see
+For general information about usage reports in the Microsoft 365 admin center, and to see a list of all available reports, see
 Microsoft 365 admin center usage reports overview
 .
 View the Microsoft 365 Copilot usage report
-For information about the roles needed to view usage reports, see
+For information about the roles needed to view usage reports, see "Before you begin" in
 Microsoft 365 admin center usage reports overview
-.
 Go to the
 Microsoft 365 admin center
 .
@@ -58,7 +57,6 @@ Usage
 tab to view adoption and usage metrics.
 Interpret the Microsoft 365 Copilot usage report
-Use the Microsoft 365 Copilot usage report to see the usage of Microsoft 365 Copilot in your organization.
 At the top, you can filter by different timeframes. You can view the Microsoft 365 Copilot report over the last 7, 30, 90, or 180 days.
 You can view several numbers for Microsoft 365 Copilot usage, which highlight the enablement number and the adoption of the enablement:
 Enabled Users
@@ -148,7 +146,7 @@ , type a prompt in Copilot box, and submit. (User experience is slightly different among web, Windows, Mac, or mobile.)
 Draft an email message with Copilot in Outlook - Microsoft Support
 Coach
-Select Copilot icon in the email message, choose
+Select the Copilot icon in the email message, and then select
 Coaching by Copi
```

---

### 3. Agent 365 Overview Page (M365 Admin)

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
@@ -164,7 +167,7 @@ - The number of unique users who interacted with at least one agent up to the last 30 days by sending a prompt to an agent and receiving a response from that agent. These conversational interactions can occur in Microsoft experiences, such as Teams and Microsoft Copilot, as well as non-Microsoft channels. For Microsoft Copilot Studio agents, an active user is counted when a user sends a prompt to the agent. In most cases, prompts and responses have a one-to-one relationship. However, there are limited scenarios where a user may send a prompt but not receive a response. This difference is expected to have a minimal impact in practice. 
```

---

### 4. Trainable Classifiers

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

### 5. Retention for SharePoint

**URL:** https://learn.microsoft.com/en-us/purview/retention-policies-sharepoint
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)

**Affected Controls:**
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -137,7 +137,7 @@ The retention label marks items as a
 regulatory record
 , which always prevents the item from being edited or deleted.
-After retention settings are assigned to content in a OneDrive account, SharePoint site, or SharePoint Embedded container for a Loop workspace, the paths the content takes depend on whether the retention settings are to retain and delete, to retain only, or delete only. In the explanations that follow, modified content is moved to the Preservation Hold library for retention policies, and retention labels that mark items as records (and the content is unlocked). Items that are modified with retention labels that don't mark items as records don't create copies in the Preservation Hold library, but do when items are deleted.
+After retention settings are assigned to content in a OneDrive account, SharePoint site, or SharePoint Embedded container for a Loop workspace, a timer job periodically evaluates the items and the paths the content takes depend on whether the retention settings are to retain and delete, to retain only, or delete only. The timer job can take up to seven days to run. In the explanations that follow, modified content is moved to the Preservation Hold library for retention policies, and retention labels that mark items as records (and the content is unlocked). Items that are modified with retention labels that don't mark items as records don't create copies in the Preservation Hold library, but do when items are deleted.
 When the retention settings are to retain and delete:
 If the content is modified or deleted
 during the retention period, a copy of the original content as it existed when the retention settings were assigned is created in the Preservation Hold library. There, the timer job identifies items whose retention period has expired. Those items are moved to the second-stage Recycle Bin, where they're permanently deleted at the end of 93 days. The second-stage Recycle Bin isn't visible to end u
```

---

### 6. Advanced Management

**URL:** https://learn.microsoft.com/en-us/sharepoint/advanced-management
**Section:** SharePoint Administration
**Classification:** HIGH (Portal references)

**Affected Controls:**
- Control 4.2: Control 4.2: Site Access Reviews and Certification
  - File: `controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`
- Control 4.5: Control 4.5: SharePoint Security and Compliance Monitoring
  - File: `controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.5/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -26,15 +26,13 @@ Manage content sprawl
 ;
 Manage the content lifecycle
-;
+; and
 Prevent oversharing
-; and
-Manage permissions and access
 .
 SAM capabilities are helpful as organizations
 prepare for Microsoft 365 Copilot and agents
 .
-SAM is managed primarily through the SharePoint admin center and is designed for SharePoint and Microsoft 365 administrators who are responsible for governance, risk reduction, and audit readiness. You can also use the
+Administrators primarily manage SAM through the SharePoint admin center. It's designed for SharePoint and Microsoft 365 administrators who are responsible for governance, risk reduction, and audit readiness. You can also use the
 SharePoint Admin Agent
 to make your SharePoint administration more productive and efficient.
 Manage content sprawl
@@ -56,7 +54,11 @@ Restrict site creation by apps
 : Specify the non-Microsoft applications that can create SharePoint sites in your organization.
 Prevent oversharing
-SAM capabilities help prevent oversharing by empowering your administrators with reports, insights, and policies that help protect your organization's sensitive information.
+SAM provides layered controls to manage permissions and access, and enforce least-privilege access across SharePoint and OneDrive. SAM capabilities help prevent oversharing by empowering your administrators with reports, insights, and policies that help protect your organization's sensitive information.
+Use Conditional Access policies
+: Use authentication contexts to connect a Microsoft Entra Conditional Access policy to a SharePoint site.
+Use restricted access control (RAC)
+: Restrict access to SharePoint or OneDrive sites to specific groups.
 Use the content management assessment
 : This hub provides a comprehensive set of tools for assessing and improving your organization's content management practices with actionable insights and recommendations.
 Set up a "block download" policy
@@ -67,8 +69,8 @@ : Use the
 Get AI i
```

---

### 7. Azure Private Link

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

### 8. Purview What's New

**URL:** https://learn.microsoft.com/en-us/purview/whats-new
**Section:** Release Plans and Roadmaps
**Classification:** HIGH (Feature availability)

**What Changed:**
```diff
--- +++ @@ -44,6 +44,18 @@ Data security and compliance protections for Microsoft Agent 365
 .
 Data Governance
+In preview
+:
+Search for governed assets
+in Unified Catalog. Instead of searching across all assets, you can conduct a focused search of data assets that are activiely governed. Governed assets search supports semantic search, partial keyword matching, exact phrase matching with double quotes, and hover highlights that show why a result was returned.
+Updated
+:
+Data products search
+now supports partial keyword matching, exact phrase matching with double quotes, and hover highlights that show which attributes matched your search query.
+Updated
+: Release of additional
+APIs for data assets and columns
+.
 General availability (GA)
 :
 Standalone data asset data quality scan
@@ -114,6 +126,10 @@ ,
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

## MEDIUM: Minor Changes (Review Optional)

### 1. Planned Features (2026 Wave 1) [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/planned-features
**Classification:** MEDIUM (General content update)

---

### 2. Agent Suggestions from M365 Copilot [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/get-365-copilot-agent-suggestions-based-work-copilot-studio
**Classification:** MEDIUM (General content update)

---

### 3. Copilot Studio Kit — Compliance Hub
**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/whats-new
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