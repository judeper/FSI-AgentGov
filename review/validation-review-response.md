# FSI Agent Governance Framework - Validation Review Response

**Document Type:** Review Response and Recommendations
**Validation Date:** January 6, 2026
**Sources Reviewed:** `validation-findings.md`, `Copilot Studio Governance Review.docx`
**Validated Against:** Microsoft Learn Documentation (accessed January 6, 2026)

---

## Executive Summary

This document cross-references the feedback from two external reviews against current Microsoft Learn documentation to determine which findings are accurate, which are outdated or incorrect, and what changes should be incorporated into the FSI Agent Governance Framework.

**Key Findings:**

| Category | Count |
|----------|-------|
| Validated - Recommend Action | 12 |
| Not Validated / Incorrect | 4 |
| Missing Controls Worth Adding | 4 |

**Critical Discovery:** Several claims in the reviews reference outdated information or PowerShell cmdlets that no longer appear in current Microsoft documentation. Most notably, DLP enforcement for Copilot Studio is now **enabled by default** as of early 2025, rendering several "missing control" claims moot.

---

## Section 1: Validated Findings - Recommend Action

### 1.1 Agent Creation Cannot Be Disabled (CRITICAL)

**Source:** Both reviews
**Claim:** The framework implies agent creation can be disabled, but Microsoft confirms this is not possible.

**Microsoft Learn Validation:** CONFIRMED
> "You can't disable agent creation. Our guidance is to use data policies to disable anyone from chatting with that agent."
> *Source: [Security FAQs for Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-faq)*

**Recommendation:**
- Update framework language to clarify that agent *creation* cannot be prevented
- Document the "Sterile Containment Strategy" approach:
  1. Block all publishing channels via DLP (Direct Line, Teams, Facebook, Omnichannel, SharePoint, WhatsApp)
  2. Disable "Share with Everyone" via tenant settings
  3. Use environment routing to divert makers away from default environment
- Add explicit note that blocking publishing channels renders agents non-functional (cannot be deployed)

**Priority:** HIGH
**Affects:** Control 1.1, Overview documentation

---

### 1.2 Control 3.8 Naming: "Copilot Hub" Not "Copilot Command Center"

**Source:** Both reviews
**Claim:** "Copilot Command Center" is not an official Microsoft product name.

**Microsoft Learn Validation:** CONFIRMED
- The official name in Power Platform Admin Center is "**Copilot**" (navigation item) or "**Copilot area/hub**"
- No documentation uses "Copilot Command Center"
- *Source: [Track, manage, and scale Copilot adoption](https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub)*

**Recommendation:**
- Rename Control 3.8 from "Copilot Command Center" to "**Copilot Hub and Governance Dashboard**"
- Update all references throughout the framework
- Note: The content in our Control 3.8 is comprehensive and accurate; only the naming needs correction

**Priority:** MEDIUM
**Affects:** Control 3.8, navigation, cross-references

---

### 1.3 Environment Routing Default Fallback Behavior (CRITICAL)

**Source:** validation-findings.md (Finding 3.3)
**Claim:** Framework does not explain what happens when no routing rule matches.

**Microsoft Learn Validation:** CONFIRMED
> "When a maker accesses a portal, the system evaluates the rules in order and applies the first matching rule. If no rule matches, or if environment routing isn't turned on, the maker is routed to the default environment."
> *Source: [Environment routing](https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing)*

**Current State:** Our Control 2.15 does not explicitly document this fallback behavior.

**Recommendation:**
- Add explicit warning to Control 2.15:

> **Important:** When environment routing is enabled but no routing rule matches a user, the user is routed to the **default environment**. Environment routing alone does NOT prevent access to the default environment. Organizations must either:
> 1. Ensure routing rules cover all user populations, OR
> 2. Implement "Sterile Default Environment" controls (DLP blocking + sharing restrictions)

**Priority:** HIGH
**Affects:** Control 2.15

---

### 1.4 Managed Environment Features - Incomplete List

**Source:** validation-findings.md (Finding 3.1)
**Claim:** Framework lists only 5-7 features; Microsoft documentation lists 23+.

**Microsoft Learn Validation:** CONFIRMED
Microsoft documentation lists **23 distinct features** for Managed Environments:

1. Environment groups
2. Limit sharing
3. Weekly usage insights
4. Data policies
5. Pipelines in Power Platform
6. Maker welcome content
7. Solution checker
8. **IP Firewall**
9. **IP cookie binding**
10. **Customer Managed Key (CMK)**
11. **Lockbox**
12. **Extended backup**
13. Data policies for desktop flow
14. **Export data to Azure Application Insights**
15. Administer the catalog
16. Default environment routing
17. Create app description with Copilot
18. **Virtual Network support**
19. Conditional access on individual apps
20. Control which apps are allowed
21. **Configure auditing for environment**
22. **Create and manage masking rules**
23. System administration capabilities

*Source: [Managed Environments overview](https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview)*

**Our Current State:** Control 2.1 Key Capabilities table lists only 5 features.

**Recommendation:**
- Expand Control 2.1 to reference the complete feature set
- Add a "Full Capabilities Reference" section linking to MS Learn
- Highlight FSI-relevant advanced features: IP Firewall, VNet support, CMK, Lockbox, data masking

**Priority:** MEDIUM
**Affects:** Control 2.1

---

### 1.5 Environment Group Rules - Updated Count

**Source:** validation-findings.md (Finding 3.2)
**Claim:** Framework does not list all available environment group rules.

**Microsoft Learn Validation:** CONFIRMED
Current count: **21 rules** (6 in preview, 15 generally available)

Notable Copilot Studio-specific rules:
- Accessing transcripts from conversations in Copilot Studio agents
- Sharing agents with Editor permissions
- Sharing agents with Viewer permissions
- Sharing data between Copilot Studio and Viva Insights

*Source: [Environment group rules](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules)*

**Recommendation:**
- Update Control 2.2 to reference the complete rule list
- Highlight FSI-relevant rules (transcript access, sharing controls)

**Priority:** LOW
**Affects:** Control 2.2

---

### 1.6 Automatic Security Scan Feature

**Source:** validation-findings.md (Finding 2.3)
**Claim:** Framework should reference the automatic security scan feature.

**Microsoft Learn Validation:** CONFIRMED
Copilot Studio automatically scans agents before publishing and warns makers when:
- Authentication mode is changed to "No authentication"
- Connector credentials changed from user auth to maker auth
- Agent is shared with everyone in the organization

*Source: [Security scan](https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-scan)*

**Recommendation:**
- Add reference to automatic security scan in Control 1.7 (Audit Logging) or create new sub-section
- Document that this is a built-in governance safety net
- Note that organizations can monitor for bypassed warnings

**Priority:** MEDIUM
**Affects:** Control 1.7 or new section

---

### 1.7 RSS vs RCD Distinction for SharePoint

**Source:** Copilot Studio Governance Review.docx (Section 5.1)
**Claim:** Framework should distinguish between Restricted Content Discovery (RCD) and Restricted SharePoint Search (RSS).

**Microsoft Learn Validation:** CONFIRMED

| Feature | Type | Behavior |
|---------|------|----------|
| **Restricted Content Discovery (RCD)** | Block list | Excludes specific sites from Copilot |
| **Restricted SharePoint Search (RSS)** | Allow list | Limits Copilot to curated site list (max 100 sites) |

RSS is specifically designed for Copilot customers to:
- Review permissions before exposing sites to Copilot
- Reduce oversharing risks
- Maintain momentum with Copilot deployment

*Source: [Restricted SharePoint Search](https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search)*

**Recommendation:**
- Update Control 4.1 to clearly distinguish RCD (our current focus) from RSS
- Add guidance that RSS (allow-list) is often the superior "Zero Trust" starting point for FSI
- Consider separate section or sub-control for RSS

**Priority:** MEDIUM
**Affects:** Control 4.1

---

### 1.8 Restricted Access Control (RAC) for Ethical Walls

**Source:** Copilot Studio Governance Review.docx (Section 5.3)
**Claim:** RAC is missing as a control for implementing ethical walls.

**Microsoft Learn Validation:** CONFIRMED

RAC (Restricted Access Control) is a SharePoint feature that:
- Limits site access to specific security groups regardless of individual sharing
- Acts as a blanket denial that supersedes previous access grants
- Supports up to 10 security/M365 groups per site
- Ideal for enforcing "Chinese Walls" / information barriers

*Source: [Restricted Access Control](https://learn.microsoft.com/en-us/sharepoint/restricted-access-control)*

**Recommendation:**
- Add RAC guidance to Control 4.1 or create Control 4.6
- Document FSI use cases: M&A separation, Investment Banking/Research walls
- Include PowerShell implementation examples

**Priority:** MEDIUM
**Affects:** Pillar 4 (new or existing control)

---

### 1.9 Two Agent Inventories - Clarification Needed

**Source:** Copilot Studio Governance Review.docx (Section 4.2)
**Claim:** There are two distinct agent inventories that must be monitored.

**Microsoft Learn Validation:** CONFIRMED

| Inventory | Location | Tracks |
|-----------|----------|--------|
| Agent Registry | M365 Admin Center → Agents | Declarative agents, M365 Copilot plugins |
| Agent Inventory | Power Platform Admin Center | Copilot Studio custom agents |

**Recommendation:**
- Update Control 3.1 to clarify both inventory sources
- Add guidance to reconcile both sources for complete visibility
- Note that Microsoft is working toward unified "Agent 365" view

**Priority:** MEDIUM
**Affects:** Control 3.1

---

### 1.10 Channel Connectors for Blocking Publishing

**Source:** validation-findings.md (Finding 2.1)
**Claim:** Four specific channel connectors must be blocked to disable publishing.

**Microsoft Learn Validation:** PARTIALLY CONFIRMED

Microsoft documentation lists **6 supported channels** (not 4):
1. Microsoft Teams + M365
2. Direct Line
3. Facebook
4. Omnichannel
5. SharePoint
6. WhatsApp

> "If makers don't configure their agents for the allowed channel except Direct Line (on by default), or if the administrators don't allow any channel, the agents can't be published."

*Source: [Configure data policies for agents - DLP Example 6](https://learn.microsoft.com/en-us/microsoft-copilot-studio/dlp-example-6)*

**Recommendation:**
- Update any references to specify all 6 channels (not 4)
- Note that Direct Line is enabled by default
- Document that blocking all channels effectively prevents agent deployment

**Priority:** MEDIUM
**Affects:** Control 1.1, Control 1.5

---

### 1.11 Default Environment "Sterile Containment" Strategy

**Source:** Copilot Studio Governance Review.docx (Section 1.1)
**Claim:** Framework should document the "Sterile Default" strategy since creation cannot be disabled.

**Microsoft Learn Validation:** CONFIRMED (based on multiple sources)

Since agent creation cannot be disabled in the default environment:
1. Block all publishing channels via DLP
2. Disable "Share with Everyone"
3. Use environment routing to redirect makers
4. Consider Power Pages bot creation prevention

*Sources: Multiple (security-faq, admin-data-loss-prevention, default-environment-routing)*

**Recommendation:**
- Add new section or control for "Default Environment Governance"
- Document the multi-layer defense approach
- Include PowerShell commands for implementation

**Priority:** HIGH
**Affects:** New content, possibly Control 2.15 or new control

---

### 1.12 DLP Enforcement Now Enabled by Default

**Source:** validation-findings.md (Missing Control 5.4)
**Claim:** Copilot Studio DLP enforcement is NOT enabled by default.

**Microsoft Learn Validation:** OUTDATED CLAIM

> "In early 2025, data policy enforcement for all tenants is set to **Enabled by default**, as announced in message center alert MC973179."

*Source: [Configure data policies for agents](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention)*

**Recommendation:**
- Do NOT add `Set-PowerVirtualAgentsDlpEnforcement` cmdlet (not in current docs)
- Update framework to note that DLP enforcement is now default
- Remove any outdated references to "opt-in" DLP enforcement

**Priority:** LOW (informational update)
**Affects:** Control 1.5, any DLP-related content

---

## Section 2: Not Validated / Incorrect Claims

### 2.1 `Set-PowerVirtualAgentsDlpEnforcement` Cmdlet

**Source:** validation-findings.md
**Claim:** Use this cmdlet to enable Copilot Studio DLP enforcement.

**Microsoft Learn Status:** NOT FOUND IN CURRENT DOCUMENTATION

The referenced cmdlet does not appear in current Microsoft Learn documentation. The closest equivalent is `Set-PowerAppDlpErrorSettings` for configuring error messages.

**Action:** IGNORE - Do not add to framework

---

### 2.2 DLP Enforcement Not Enabled by Default

**Source:** validation-findings.md (Missing Control 5.4)
**Claim:** DLP enforcement must be manually activated.

**Microsoft Learn Status:** OUTDATED

As of early 2025, DLP enforcement IS enabled by default for all tenants.

**Action:** IGNORE - No longer applicable

---

### 2.3 "4 Specific Channel Connectors"

**Source:** validation-findings.md (Finding 2.1)
**Claim:** Exactly 4 channel connectors must be blocked.

**Microsoft Learn Status:** INCORRECT

Microsoft lists 6 channels, not 4. The specific "4 connector" claim appears to be incomplete.

**Action:** CLARIFY - Use correct count (6 channels) in any documentation updates

---

### 2.4 DSPM for AI Previously Called "AI Hub"

**Source:** Copilot Studio Governance Review.docx (Section 2.2)
**Claim:** The feature was previously known as "AI Hub" and was rebranded.

**Microsoft Learn Status:** NOT CONFIRMED

Current documentation refers to "classic" version being replaced with new guided workflows, but does not confirm "AI Hub" as a previous name.

**Action:** SKIP - Cannot validate; do not include this claim

---

## Section 3: Missing Controls Worth Adding

Based on validated findings, consider adding the following to the framework:

### 3.1 Restricted SharePoint Search (RSS) Control

**Description:** Allow-list approach to limit Copilot's SharePoint content scope
**Source:** [restricted-sharepoint-search](https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search)
**FSI Relevance:** Zero-trust starting point for high-risk deployments
**Priority:** HIGH

---

### 3.2 Restricted Access Control (RAC) for Ethical Walls

**Description:** Security group-based site access regardless of sharing
**Source:** [restricted-access-control](https://learn.microsoft.com/en-us/sharepoint/restricted-access-control)
**FSI Relevance:** Information barriers for M&A, Investment Banking/Research separation
**Priority:** MEDIUM

---

### 3.3 Default Environment Governance Strategy

**Description:** Multi-layer approach to contain default environment risk
**Source:** Multiple Microsoft Learn articles
**FSI Relevance:** Prevents shadow AI in ungoverned environment
**Priority:** HIGH

---

### 3.4 Automatic Security Scan Documentation

**Description:** Built-in pre-publish security warnings
**Source:** [security-scan](https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-scan)
**FSI Relevance:** Defense-in-depth for maker mistakes
**Priority:** MEDIUM

---

## Section 4: Recommended Framework Changes Summary

### High Priority (Implement Immediately)

| Change | Location | Description |
|--------|----------|-------------|
| Agent creation cannot be disabled | Overview, Control 1.1 | Clarify technical limitation and containment approach |
| Environment routing fallback | Control 2.15 | Add explicit warning about default environment fallback |
| Default environment strategy | New section | Document sterile containment approach |

### Medium Priority (Add Within 30 Days)

| Change | Location | Description |
|--------|----------|-------------|
| Rename Control 3.8 | Control 3.8, nav | Change "Copilot Command Center" to "Copilot Hub" |
| Expand Managed Environment features | Control 2.1 | Reference full 23-feature list |
| Add RSS guidance | Control 4.1 | Distinguish RCD (block-list) from RSS (allow-list) |
| Add RAC for ethical walls | Pillar 4 | Information barrier implementation |
| Clarify two agent inventories | Control 3.1 | M365 Admin vs PPAC inventories |
| Update channel count | Control 1.1, 1.5 | 6 channels (not 4) for blocking |
| Add security scan reference | Control 1.7 | Document automatic pre-publish scan |

### Low Priority (Enhancement)

| Change | Location | Description |
|--------|----------|-------------|
| Environment group rules count | Control 2.2 | Update to 21 rules |
| DLP default status | Control 1.5 | Note enforcement is now default |

---

## Section 5: Sources Consulted

| Topic | Microsoft Learn URL | Access Date |
|-------|---------------------|-------------|
| Copilot Studio DLP | https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention | Jan 6, 2026 |
| Security FAQs | https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-faq | Jan 6, 2026 |
| Managed Environments | https://learn.microsoft.com/en-us/power-platform/admin/managed-environment-overview | Jan 6, 2026 |
| Environment Routing | https://learn.microsoft.com/en-us/power-platform/admin/default-environment-routing | Jan 6, 2026 |
| Copilot Hub | https://learn.microsoft.com/en-us/power-platform/admin/copilot/copilot-hub | Jan 6, 2026 |
| Environment Group Rules | https://learn.microsoft.com/en-us/power-platform/admin/environment-groups-rules | Jan 6, 2026 |
| Security Scan | https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-scan | Jan 6, 2026 |
| DLP Example 6 (Channels) | https://learn.microsoft.com/en-us/microsoft-copilot-studio/dlp-example-6 | Jan 6, 2026 |
| DSPM for AI | https://learn.microsoft.com/en-us/purview/dspm-for-ai | Jan 6, 2026 |
| Restricted SharePoint Search | https://learn.microsoft.com/en-us/sharepoint/restricted-sharepoint-search | Jan 6, 2026 |
| Restricted Access Control | https://learn.microsoft.com/en-us/sharepoint/restricted-access-control | Jan 6, 2026 |
| Tenant-Level Analytics | https://learn.microsoft.com/en-us/power-platform/admin/tenant-level-analytics | Jan 6, 2026 |

---

## Conclusion

The external reviews provide valuable feedback, but several claims are outdated or incorrect based on current Microsoft documentation. The most critical validated findings relate to:

1. **Technical limitations** - Agent creation cannot be disabled; containment is the approach
2. **Terminology** - "Copilot Hub" not "Copilot Command Center"
3. **Default environment risk** - Routing alone doesn't prevent default environment access
4. **SharePoint controls** - RSS (allow-list) and RAC (ethical walls) should be documented

The `Set-PowerVirtualAgentsDlpEnforcement` cmdlet and several "missing control" claims are outdated and should NOT be incorporated into the framework.

---

**Prepared by:** Claude (Validation Review)
**Review Status:** Ready for stakeholder review
**Next Action:** Stakeholder approval before implementation
