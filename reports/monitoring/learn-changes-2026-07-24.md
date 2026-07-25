# Microsoft Learn Documentation Changes

**Run Date:** 2026-07-24
**Run Time:** 2026-07-24T08:28:49.231627+00:00
**Total URLs Checked:** 227

---

## Executive Summary

| Category | Count |
|----------|-------|
| CRITICAL Changes | 2 |
| HIGH Changes | 3 |
| MEDIUM Changes | 1 |
| Redirects | 2 |

---

## Change Summary (Quick Scan)

| # | URL | Classification | Affected Controls | Action Required |
|---|-----|----------------|-------------------|-----------------|
| 1 | business-continuity-disaster-recovery | CRITICAL | 2.4 | Update portal-walkthrough |
| 2 | ...ilot-security-enhanced-admin-controls | MEDIUM | 1.18, 2.3, 2.8 | Review optional |
| 3 | retention | HIGH | 1.19, 1.9, 3.5, 4.3, 2.13 | Update portal-walkthrough |
| 4 | data-classification-activity-explorer | HIGH | 1.6, 1.14 | Review and update |
| 5 | restricted-content-discovery | HIGH | 1.3, 1.14, 4.6, 4.7, 4.1 | Review and update |
| 6 | private-link-overview | HIGH | 1.20 | Review and update |

---

## CRITICAL: Playbook Updates Required

These changes affect step-by-step procedures and must be addressed.

### 1. Business Continuity

**URL:** https://learn.microsoft.com/en-us/power-platform/admin/business-continuity-disaster-recovery
**Section:** Power Platform Administration
**Classification:** CRITICAL (Deprecation notice)
**Content-Hash:** sha256:69b9558b69e9544cf67d77adc5c95c541851110072f0be156be8331b01a8640f

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
@@ -22,6 +22,8 @@ Business continuity and disaster recovery
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
-Your company might have dis
```

---

### 2. Data Retention

**URL:** https://learn.microsoft.com/en-us/purview/retention
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:fa2f291c7a2d96cec8e0a405cc208317a5b42a7695ff061b041a57a0f34b3023

**Affected Controls:**
- Control 1.19: Control 1.19: eDiscovery for Agent Interactions
  - File: `controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md`
- Control 1.9: Control 1.9: Data Retention and Deletion Policies
  - File: `controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md`
- Control 3.5: Control 3.5: Cost Allocation and Budget Tracking
  - File: `controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md`
- Control 4.3: Control 4.3: Site and Document Retention Management
  - File: `controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md`
- Control 2.13: Control 2.13: Documentation and Record Keeping
  - File: `controls/pillar-2-management/2.13-documentation-and-record-keeping.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/4.3/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/2.13/troubleshooting.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.9/powershell-setup.md` (HIGH)
- ℹ️ `playbooks/control-implementations/1.9/troubleshooting.md` (HIGH)
- ⚠️ `playbooks/control-implementations/1.21/portal-walkthrough.md` (CRITICAL)
- ℹ️ `playbooks/getting-started/phase-1-minimal-viable-controls.md` (HIGH)

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
@@ -438,6 +438,16 @@ condition, and then enter the complete retention label name or part of the label name and use a wildcard. For more information, see
 Keyword queries and search conditions for Content Search
 .
+When the retention period starts
+The start of the retention period depends on how you configure the retention policy or retention label:
+When the content was created.
+The default start of the retention period.
+When the content was last modified.
+Supported only for files in the SharePoint, OneDrive, and Microsoft 365 Groups locations.
+When the content was labeled.
+Available with retention labels, for documents in SharePoint and OneDrive, and for email items.
+When an event occurs.
+Available with retention labels that are configured for event-based retention, such as when employees leave the organization or contracts expire.
 Compare capabilities for retention policies and retention labels
 Use the following table to help you identify whether to use a retention policy or retention label, based on capabilities.
 Capability

```

---

## HIGH: Control Review Recommended

### 1. Activity Explorer

**URL:** https://learn.microsoft.com/en-us/purview/data-classification-activity-explorer
**Section:** Microsoft Purview
**Classification:** HIGH (Compliance features)
**Content-Hash:** sha256:52c999024e52ceb8dc91a0e037e1831f89229bfc99c51cfc1f98ecf75dcb1b67

**Affected Controls:**
- Control 1.6: Control 1.6: Microsoft Purview DSPM for AI
  - File: `controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`

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
@@ -25,6 +25,19 @@ Activity explorer
 lets you monitor what's being done with your labeled content. Activity explorer provides a historical view of activities on your labeled content. The activity information comes from the Microsoft 365 unified audit logs. It's transformed and then made available in the activity explorer UI. Activity explorer reports on up to 30 days worth of data.
 Activity explorer gives you multiple ways to sort and view the data.
+When activities appear
+Activity explorer isn't a real-time view. Because its data comes from the Microsoft 365 unified audit log, activities appear on the same schedule as audit records â not the moment they occur.
+For core services (Exchange, SharePoint, OneDrive, and Teams), allow 60 to 90 minutes after an activity for it to appear in activity explorer. Other services can take longer, and Microsoft doesn't guarantee a specific time for an activity to become available. For more information, see
+Search the audit log
+.
+After you enable or change a policy, allow time for the policy to reach the workload
+and
+for the resulting activities to flow in. An empty view right after you turn on a policy usually means the data pipeline hasn't caught up yet, not that the policy failed.
+Devices report endpoint activities only while they're online. An offline device backfills its activities after it reconnects.
+Note
+If a recent activity isn't showing yet, confirm that it falls within the 30 days of data that activity explorer reports on, and allow the audit-log availability time described earlier before you treat a missing activity as a defect. To confirm an activity independently, search for it in
+Audit
+.
 Filters
 Filters are the building blocks of activity explorer. Each filter focuses on a different dimension of the collected data. You can use about 50 different individual filters, including:
 Date 
```

---

### 2. Restricted Content Discovery

**URL:** https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery
**Section:** SharePoint Administration
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:07c3c50bb7abffb53e88a7d9a1a1e349ca70dc7ed7e5e8aa6cb01b18481399e3

**Affected Controls:**
- Control 1.3: Control 1.3: SharePoint Content Governance and Permissions
  - File: `controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md`
- Control 1.14: Control 1.14: Data Minimization and Agent Scope Control
  - File: `controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md`
- Control 4.6: Control 4.6: Grounding Scope Governance
  - File: `controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md`
- Control 4.7: Control 4.7: Microsoft 365 Copilot Data Governance
  - File: `controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md`
- Control 4.1: Control 4.1: SharePoint Information Access Governance (IAG) / Restricted Content Discovery
  - File: `controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md`

**Affected Playbooks:**
- ℹ️ `playbooks/control-implementations/1.14/verification-testing.md` (HIGH)

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
@@ -22,108 +22,131 @@ Restrict discovery of SharePoint sites and content
 Feedback
 Summarize this article for me
-For organizations onboarding to Microsoft 365 Copilot, maintaining strong data governance controls for SharePoint content is critical to deploying Copilot in a safe manner. Sites identified with the highest risk of oversharing can use Restricted Content Discovery to protect content while taking time to ensure that permissions are accurate and well-managed.
-With Restricted Content Discovery, organizations can limit the ability of end users to search for files from specific SharePoint sites. Enabling Restricted Content Discovery for each site prevents the sites from surfacing in organization-wide search and Microsoft 365 Copilot Business Chat, unless a user had a recent interaction.
-Restricted Content Discovery is a site-level setting that needs to be propagated to the search index, a large number of transactions could lead to a long queue in the ingestion pipeline and higher update latency times.
-While child content is hidden by default, users in your organization can still discover files they own or recently interacted with. End users can still find relevant content they need for their day-to-day tasks, even if Restricted Content Discovery is applied to the parent site.
-Restricted Content Discovery doesn't affect searches originating from a site context or other intelligent features such as Microsoft 365 Feed and Recommendations.
+Organizations preparing for Microsoft 365 Copilot often need time to review SharePoint sites, validate permissions, and implement governance controls before making content broadly discoverable. Restricted Content Discovery (RCD) helps you limit discovery of content from specific SharePoint sites while those reviews are taking place.
+When you enable Restricted Content Discovery for a site, content from tha
```

---

### 3. Azure Private Link

**URL:** https://learn.microsoft.com/en-us/azure/private-link/private-link-overview
**Section:** Azure Services
**Classification:** HIGH (Feature availability)
**Content-Hash:** sha256:d67370fbffec5e1e691fe128539b284d722ac76f6454a9443e5df4203f00a2f2

**Affected Controls:**
- Control 1.20: Control 1.20: Network Isolation and Private Connectivity
  - File: `controls/pillar-1-security/1.20-network-isolation-private-connectivity.md`

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
@@ -39,6 +39,10 @@ Note
 The feature Private Link Service Direct Connect, which allows you to connect to any privately routable destination IP address, is now in public preview. For more information and known limitations, see
 Private Link Service Direct Connect
+Important
+Azure Private Link support over IPv6 is now in public preview in limited regions. For more information, see
+Azure Private Link over IPv6 (Preview)
+.
 Note
 Azure Private Link is one of the services that make up the Network Foundations category in Azure. Other services in this category include
 Azure DNS
@@ -49,7 +53,9 @@ .
 For scenarios that involve public internet PaaS traffic, configure
 network security perimeter
-to set up a secure logical boundary. Network security perimeter restricts communication to services within its perimeter, and it allows nonperimeter public traffic through inbound and outbound access rules.
+to set up a secure logical boundary. Network security perimeter restricts communication to services within its perimeter, and it allows nonperimeter public traffic through inbound and outbound access rules. For scalable IaaS-to-PaaS connectivity with centralized access control, see
+standard service endpoint
+.
 Important
 Network security perimeter is now generally available in all Azure public cloud regions and in Azure Government regions (US Gov Virginia, US Gov Texas, US Gov Arizona, US DoD East and US DoD Central). For information on supported services, see
 Onboarded private link resources

```

---

## MEDIUM: Minor Changes (Review Optional)

### 1. Enhanced Admin Controls [Preview]
**URL:** https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/power-platform-governance-administration/manage-copilot-security-enhanced-admin-controls
**Classification:** MEDIUM (General content update)
**Content-Hash:** sha256:b2c1a390648ce62181a14140cfe4e6a81778f6f107429c3840431c876db9e07b

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