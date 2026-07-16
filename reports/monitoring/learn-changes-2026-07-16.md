# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-16
**Run Time:** 2026-07-16T08:15:38.539529+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 4 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | advanced-connector-policies | HIGH | 1.4 | Update portal-walkthrough |
| 2 | business-continuity-disaster-recovery | CRITICAL | 2.4 | Update portal-walkthrough |
| 3 | whats-new | HIGH | 2.10, 2.5, 2.25 | Review and update |
| 4 | microsoft-365-copilot-usage | HIGH | 3.8 | Review and update |
| 5 | restricted-access-control | HIGH | 1.3, 4.1 | Review and update |
| 6 | microsoft-purview-service-description | HIGH | None | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Advanced Connector Policies

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/advanced-connector-policies
**Section:** Power Platform Administration
**Classification:** HIGH (Portal references)
**Content-Hash:** sha256:3361a534c1db8dd806a5c4f9428725e011cf2d45cf1aac9bb32f205fb2695031

**Affected Controls:**
- Control 1.4: Control 1.4: Advanced Connector Policies (ACP)
  - File: `controls/pillar-1-security/1.4-advanced-connector-policies-acp.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/1.4/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/control-implementations/1.4/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -22,9 +22,9 @@ Advanced connector policies
 Feedback
 Summarize this article for me
-Advanced connector policies (ACP) represent the next generation of securing connector usage within Power Platform. ACP provides a modern, flexible approach to managing
+Advanced connector policies (ACP) provide the next generation of securing connector usage within Power Platform. ACP offers a modern, flexible approach to managing
 certified connectors
-, replacing the Business/Non-Business/Blocked classification model in classic
+. It replaces the Business, Non-Business, and Blocked classification model in classic
 data policies
 with a strict allowlist that blocks all connectors by default.
 Key principles of advanced connector policies:
@@ -47,6 +47,19 @@ . Custom connectors and HTTP connectors aren't yet supported. They're planned as a separate rule type in the future. For governing custom connectors and HTTP connectors today, continue using classic
 data policies
 .
+Enforcement modes
+When you enable ACP, you choose how it works alongside your existing classic
+data policies
+. Two modes are available:
+Mixed mode (default)
+: ACP runs alongside classic data policies, and the most restrictive settings from both are enforced. This mode is the starting state when you first enable ACP and is recommended while you migrate. For details, see
+Data policy mixed mode
+.
+ACP-only mode
+: ACP becomes the sole policy evaluator. Classic data policies are ignored but not deleted for the affected scope. Choose this mode after you fully migrate connector governance to ACP. For details, see
+ACP-only mode
+.
+Set the mode independently on an environment group or a single environment.
 Supported connector types
 Advanced connector policies are built on the certified connector catalog. ACP doesn't support all connector types from classic data policies.
 Connector type
@@ -85,6 +98,12 @@ : Desktop Flow connectors are transitioning to certified connectors. Once certified, you manage t
```

---

### 2. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:45f597e348724fc58a07d5e5ecc96589bcd0d98d81ab01d169787cd248cc50b4

**Affected Controls:**
- Control 2.4: Control 2.4: Business Continuity and Disaster Recovery
  - File: `controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md`

**Affected Playbooks:**
- ⚠️ `playbooks/control-implementations/2.4/portal-walkthrough.md` (CRITICAL)

**What Changed:**
```diff
--- +++ @@ -22,6 +22,8 @@ Business continuity and disaster recovery
 Feedback
 Summarize this article for me
+Note
+As of June 22, 2026, Self-Service Disaster Recovery (SSDR) is also available for Finance & Operations (F&O) applications. SSDR enables organizations to maintain an asynchronous secondary copy of their production environment in a paired Azure region and perform self-service failover, failback, and disaster recovery testing.
 Businesses expect their applications and customer data to be protected and resilient during unavoidable outages and disruptions. It's important to document a business continuity plan that minimizes the effects of outages. To recover and resume operations, make sure the plan lists stakeholders, processes, and specific steps.
 Microsoft provides business continuity and disaster recovery capabilities to all
 production type environments
@@ -52,9 +54,6 @@ Most geographies have region pairs separated by at least 300 miles when possible, to help protect your data in large-scale disasters.
 Self-service disaster recovery is a Power Platform infrastructure capability that lets you replicate your environment across long distances and start environment failover between regions yourself.
 You usually have multiple environments of different types in your tenant. This capability is available only for production environments.
-To turn on self-service disaster recovery, make sure your environment is managed and linked to a
-pay-as-you-go billing plan
-.
 Allow virtual network pairing for self-service disaster recovery in Dynamics 365
 If you deploy your Dynamics 365 environment within a virtual network and plan to use self-service disaster recovery, you need to configure a
 virtual network pair
@@ -101,7 +100,7 @@ Disaster recovery drill
 Emergency response for a major regional outage
 Disaster recovery drills
-Your company might have disaster recovery drills documented as a requirement in your internal business continuity plans. Some industries a
```

---

## HIGH: Control Review Recommended

### 1. What's New

**URL:** https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new
**Section:** Copilot Studio
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:b49d854bc9c1ad64d98740f9c815523719cd4c1ff646a8d0eaa90b9bcd86c38f

**Affected Controls:**
- Control 2.10: Control 2.10: Patch Management and System Updates
  - File: `controls/pillar-2-management/2.10-patch-management-and-system-updates.md`
- Control 2.5: Control 2.5: Testing, Validation, and Quality Assurance
  - File: `controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md`
- Control 2.25: Control 2.25: Microsoft Agent 365 — Admin Center Governance Console
  - File: `controls/pillar-2-management/2.25-agent-365-admin-center-governance-console.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/2.7/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.10/troubleshooting.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -35,13 +35,44 @@ Releases roll out over several days. New or updated functionality might not appear immediately.
 Notable changes
 The following sections list features released in the past months, with links to related information.
+June 2026
+(Production-ready preview) Use the
+new agent experience
+in Copilot Studio to build agents. The new experience uses an enhanced orchestration runtime for improved response quality and reasoning, available alongside the classic experience.
+Use
+Microsoft IQ
+in the new agent experience to connect your agent to organizational data, giving it access to emails, calendar events, files, Teams messages, and people information.
+Build and reuse
+skills
+in the new agent experience to extend your agent's capabilities with modular, self-contained sets of instructions. Create a skill once, add it to multiple agents, and export it as a Markdown file or package to share with others.
+Turn on
+memory
+in the new agent experience to give your agent persistent context across interactions. It captures user preferences and patterns, stores them per user, and applies them to deliver more relevant and personalized responses over time.
+(General availability) Use the
+Windows 365 for Agents MCP server
+to give your agents full operational control of a Windows 365 cloud PC, including desktop interaction, browser automation, and semantic UI inspection.
+Use
+condition groups
+to manage multiple conditions in a single Message, Question, or prompt node, reducing branching and making topic flows easier to review and maintain.
+(Preview) Integrate
+voice agents with Teams Phone Agent
+to handle specialized call workflows like billing, prescription refills, and order status, with a seamless handoff between Teams Phone Agent and your custom voice agent.
+(Preview) Connect
+other agents
+to your agent in the new agent experience so it can delegate requests to specialized agents, letting you build modular solutions with a single front-door agen
```

---

### 2. Copilot Usage Reports

**URL:** https://learn.microsoft.com/en-us/microsoft-365/admin/activity-reports/microsoft-365-copilot-usage?view=o365-worldwide
**Section:** Microsoft 365 Copilot
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:85378d121513eb324a29bdc6d24bd95e91722d138600835b25fa211eaa1383a2

**Affected Controls:**
- Control 3.8: Control 3.8: Copilot Hub and Governance Dashboard
  - File: `controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

**Affected Playbooks:**
- ℹ️ `playbooks/advanced-implementations/microsoft-audit-reporting-tools.md` (HIGH)

**What Changed:**
```diff
--- +++ @@ -22,7 +22,7 @@ Microsoft 365 Copilot usage report
 Feedback
 Summarize this article for me
-The Microsoft 365 Copilot usage report provides a summary of how users adopt, retain, and engage with Microsoft 365 Copilot and its associated enabled apps, including agent usage. For Copilot activity on a given day, the report typically becomes available within 72 hours of the end of that day (in UTC).
+The Microsoft 365 Copilot usage report provides a summary of how users adopt, retain, and engage with Microsoft 365 Copilot and its associated enabled apps. For Copilot activity on a given day, the report typically becomes available within 48 hours of the end of that day (in UTC).
 For general information about usage reports in the Microsoft 365 admin center, and to see a list of all available reports, see
 Microsoft 365 admin center usage reports overview
 .
@@ -57,7 +57,7 @@ Usage
 tab to view adoption and usage metrics.
 Interpret the Microsoft 365 Copilot usage report
-At the top, you can filter by different timeframes. You can view the Microsoft 365 Copilot report over the last 7, 30, 90, or 180 days.
+At the top, you can filter by different timeframes. You can view the Microsoft 365 Copilot report over the last 7, 28, 90, or 180 days.
 You can view several numbers for Microsoft 365 Copilot usage, which highlight the enablement number and the adoption of the enablement:
 Enabled Users
 shows the total number of unique users in your organization with Microsoft 365 Copilot licenses over the selected timeframe.
@@ -70,10 +70,6 @@ , the recommended action card highlights
 Microsoft Copilot Dashboard
 , where you can deliver insights to your IT leaders to explore Copilot readiness, adoption, and impact in Viva Insights.
-Active agent users
-shows the total number of unique Microsoft 365 Copilot users in your org who used agents built by your org (including admin-approved agents and agents created via agent builder and shared with users in your org).
-Note
-Agent us
```

---

### 3. Restricted Access Control

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-access-control
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:cc06f77eb3893222ae3968d45fec77f339dd34fef621b7d7bb2c750c09a55378

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`

**What Changed:**
```diff
--- +++ @@ -22,11 +22,8 @@ Restrict SharePoint site access with Microsoft 365 groups and Microsoft Entra security groups
 Feedback
 Summarize this article for me
-Restricted site access control helps prevent oversharing by designating access of SharePoint sites and its content to users in a specific group. Users not in the specified group can't access the site or its content, even if they had prior permissions or a shared link. You can apply this policy on Microsoft 365 group-connected, Teams-connected, and nongroup connected sites by using Microsoft 365 groups or Microsoft Entra security groups.
-Site access restriction policies take effect when a user attempts to open a site or access a file. Users with direct permissions to the file can still view files in search results. However, they can't access the files if they're not part of the specified group.
-Restricting site access through group membership can minimize the risk of oversharing content. For insights into data sharing, see
-Data access governance reports
-.
+Restricted site access control helps prevent oversharing by designating access of SharePoint sites and its content to users in a specific control group. Users not in the specified control group can't access the site or its content, even if they had prior permissions or a shared link. You can apply this policy on Microsoft 365 group-connected, Teams-connected, and nongroup connected sites by using Microsoft 365 groups or Microsoft Entra security groups.
+Site access restriction policies take effect when a user attempts to open a site, access a file, or search for content in organization search experiences and Microsoft Copilot experiences.
 What do you need to restrict site access?
 See
 Prerequisites for SharePoint Advanced Management
@@ -86,15 +83,15 @@ Add or remove your security groups or Microsoft 365 groups and select
 Save
 .
+Apply site access restriction to a site
 To apply site access restriction to the site, you must add at least one group t
```

---

### 4. Purview Licensing

**URL:** https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description
**Section:** Licensing
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:54fabe44cd0aa3063aec7ac4e38a25bfc511b99269b10ebb0db399781333bb6d

**What Changed:**
```diff
--- +++ @@ -72,8 +72,8 @@ 1
 Audit logs for Microsoft 365 Copilot interactions are generated only when Microsoft 365 Copilot is licensed and in use.
 Microsoft Purview Audit (Premium)
-Audit (Premium) (formerly named Microsoft 365 Advanced Audit) provides one-year retention of audit logs for user and admin activities and provides the ability to create custom audit log retention policies to manage audit log retention for other Microsoft 365 services. It also provides access to crucial events for investigations and high-bandwidth access to the Office 365 Management Activity API.
-Users benefit from Audit (Premium) because audit records related to user activity in Microsoft 365 services can be retained for up to one year. Additionally, high-value auditing events are logged, such as when items in a user's mailbox are accessed or read.
+Audit (Premium) (formerly named Microsoft 365 Advanced Audit) provides up to one-year retention of audit logs for user and admin activities and provides the ability to create custom audit log retention policies to manage audit log retention for other Microsoft 365 services. It also provides access to crucial events for investigations and high-bandwidth access to the Office 365 Management Activity API.
+Users benefit from Audit (Premium) because audit records related to user activity in Microsoft 365 services can be retained for up to one year. Additionally, intelligent insights for certain auditing events are logged, such as the sensitivity label for items accessed in a user's mailbox.
 By default, Audit (Premium) is enabled at the tenant level for all users that benefit from the service, and automatically provides one-year retention of audit logs for activities (performed by users with the appropriate license) in Microsoft Entra ID, Exchange, and SharePoint.
 Additionally, organizations can use audit log retention policies to manage the retention period for audit records generated by activity in other Microsoft 365 services.
 One-year re
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