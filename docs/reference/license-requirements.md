# License Requirements by Control

License mapping guidance for the current FSI Agent Governance Framework control catalog.

---

## License Summary

| License | Controls Requiring | Primary Use |
|---------|-------------------|-------------|
| **Power Platform Premium** | 1.1, 1.4, 1.8, 1.14, 1.20, 2.1, 2.2, 2.3, 2.5, 2.8, 2.9, 2.15, 3.2, 3.5, 3.6, 3.7, 3.8 | Managed Environments, ACP |
| **Microsoft 365 E5** | 1.5, 1.6, 1.7, 1.9, 1.10, 1.12, 1.13, 1.17, 1.19, 1.21, 1.22 | Purview full suite |
| **Microsoft Purview Suite** (formerly M365 E5 Compliance) | 1.5, 1.6, 1.7, 1.9, 1.10, 1.12, 1.13, 1.17, 1.19, 1.22 | Purview add-on to E3 |
| **Microsoft 365 E3** | 1.3, 1.11, 1.15, 1.16, 2.10 | Basic security features |
| **Microsoft Entra ID P1** | 1.11, 1.18, 2.8 | Conditional Access |
| **Microsoft Entra ID P2** | 1.11, 1.12, 1.23, 4.2 | PIM, Access Reviews |
| **SharePoint Advanced Management** | 4.1, 4.2, 4.3, 4.4, 4.5, 4.6 | SharePoint governance |
| **Copilot Studio** | All | Agent development |
| **Microsoft 365 Copilot Business** | N/A | SMB Copilot access |

---

## Microsoft 365 Copilot Business

!!! info "SMB-Focused Copilot License (GA December 2025)"
    Microsoft 365 Copilot Business is designed for smaller organizations (up to 300 users) and became generally available December 1, 2025.

| Aspect | Details |
|--------|---------|
| **Price** | $21/user/month |
| **User Limit** | Up to 300 users per tenant |
| **GA Date** | December 1, 2025 |
| **Prerequisites** | Microsoft 365 Business Basic, Standard, or Premium |

**Key Differences from Enterprise Copilot:**

| Capability | Copilot Business | Microsoft 365 Copilot |
|------------|------------------|----------------------|
| **User limit** | 300 maximum | Unlimited |
| **Base license** | M365 Business SKUs | M365 E3/E5 |
| **Copilot Studio** | Included (limited) | Full Copilot Studio |
| **Advanced compliance** | Basic | Full Purview integration |

**FSI Applicability:** Smaller broker-dealers, RIAs, or credit unions with under 300 users may find this SKU more cost-effective than enterprise licensing. However, organizations with significant regulatory compliance requirements (FINRA 4511 long-term retention, comprehensive audit) should evaluate whether Microsoft Purview Suite features are necessary before selecting the Business SKU.

---

## E5 License Distinction: E5 vs Microsoft Purview Suite vs E5 Security

!!! warning "These Are Three Distinct Products"
    Microsoft 365 E5, Microsoft Purview Suite, and E5 Security are separate products with different feature sets. Documentation must be precise about which is required. Microsoft Purview Suite was formerly named "Microsoft 365 E5 Compliance" (renamed September 2025); older documentation and admin portals may still use the previous name.

| License | What It Includes | Typical Use Case |
|---------|------------------|------------------|
| **Microsoft 365 E5** | Full suite: E3 + Purview Suite + E5 Security + additional services | Enterprise with comprehensive needs |
| **Microsoft Purview Suite** (formerly E5 Compliance) | Microsoft Purview suite (DLP, IRM, eDiscovery, Insider Risk, etc.) | Organizations with E3 needing compliance |
| **Microsoft 365 E5 Security** | Microsoft Defender suite (Defender for Office 365 P2, Defender for Endpoint P2, etc.) | Organizations with E3 needing security |

**Key Distinctions:**

| Capability | E5 | Purview Suite | E5 Security |
|------------|:--:|:-------------:|:-----------:|
| Microsoft Purview DLP | ✅ | ✅ | ❌ |
| Microsoft Purview DSPM for AI | ✅ | ✅ | ❌ |
| Microsoft Purview Insider Risk | ✅ | ✅ | ❌ |
| Microsoft Purview eDiscovery | ✅ | ✅ | ❌ |
| Microsoft Defender for Office 365 P2 | ✅ | ❌ | ✅ |
| Microsoft Defender for Endpoint P2 | ✅ | ❌ | ✅ |
| Microsoft Defender for Cloud Apps | ✅ | ❌ | ✅ |
| Microsoft Sentinel (50 MB/user/month) | ✅ | ❌ | ✅ |

**Documentation Guidance:** When referencing E5 requirements, specify whether Microsoft Purview Suite is sufficient (Purview features) or full E5/E5 Security is required (Defender features).

## Copilot Control System License Language

!!! note "Foundational vs Optimized"
    Microsoft Learn now describes Copilot Control System licensing in **Foundational** and **Optimized** tiers. Foundational controls map to Microsoft 365 admin center, SharePoint Advanced Management, and Microsoft Purview capabilities available with A3/E3/G3 licensing. Optimized controls map to Microsoft Purview and Microsoft Defender for Cloud Apps capabilities available with A5/E5/G5 licensing.

    For FSI implementations, Zone 2 deployments often start with Foundational controls, while Zone 3 deployments typically need Optimized data security, insider risk, and reporting capabilities.

---

## Pillar 1: Security Controls

| Control | Control Name | Required License | Notes |
|---------|--------------|------------------|-------|
| **1.1** | Restrict Agent Publishing | Power Platform Premium | Managed Environments required |
| **1.2** | Agent Registry | Microsoft 365 E3+ | Integrated Apps in M365 Admin |
| **1.3** | SharePoint Content Governance | Microsoft 365 E3+ | SharePoint included; SAM for advanced |
| **1.4** | Advanced Connector Policies | Power Platform Premium | Managed Environments + Environment Groups |
| **1.5** | DLP and Sensitivity Labels | Microsoft 365 E5 or Microsoft Purview Suite | Purview DLP + Information Protection. **Note:** DLP for Copilot *prompts* is available to all M365 Copilot/Copilot Chat users at no additional cost (any SKU); DLP to restrict Copilot from *processing files/emails* requires E5/Purview Suite |
| **1.6** | DSPM for AI | Microsoft 365 E5 or Microsoft Purview Suite | Microsoft Purview DSPM for AI |
| **1.7** | Audit Logging | Microsoft 365 E5 (Premium) or E3 (Standard) | E5 for 10-year retention |
| **1.8** | Runtime Protection | Power Platform Premium | Managed Environments feature |
| **1.9** | Data Retention | Microsoft 365 E5 or Microsoft Purview Suite | Data Lifecycle Management |
| **1.10** | Communication Compliance | Microsoft 365 E5 or Microsoft Purview Suite | Purview Communication Compliance |
| **1.11** | Conditional Access & MFA | Microsoft Entra ID P1 (basic) or P2 (advanced) | P2 for risk-based policies |
| **1.12** | Insider Risk | Microsoft 365 E5 or E5 Insider Risk | Purview Insider Risk Management |
| **1.13** | Sensitive Information Types | Microsoft 365 E5 or Microsoft Purview Suite | Custom SITs require E5 |
| **1.14** | Data Minimization | Power Platform Premium | Environment-level controls |
| **1.15** | Encryption | Microsoft 365 E3+ | Default encryption included |
| **1.16** | IRM for Documents | Microsoft 365 E3+ | Azure Information Protection |
| **1.17** | Endpoint DLP | Microsoft 365 E5 or Microsoft Purview Suite | Endpoint DLP |
| **1.18** | RBAC | Microsoft Entra ID P1+ | Role management |
| **1.19** | eDiscovery for Agent Interactions | Microsoft 365 E5 or Microsoft Purview Suite | eDiscovery (Premium) for AI content search |
| **1.20** | Network Isolation and Private Connectivity | Azure subscription + Power Platform Premium | VNet integration, Private Endpoints |
| **1.21** | Adversarial Input Logging | Microsoft 365 E5 or E5 Security | Defender for Cloud Apps + Purview Audit |
| **1.22** | Information Barriers | Microsoft 365 E5 or Microsoft Purview Suite | Purview Information Barriers |
| **1.23** | Step-Up Authentication | Microsoft Entra ID P2 | Authentication context + Conditional Access |
| **1.24** | Defender AI-SPM | Microsoft Defender for Cloud (CSPM) | Defender CSPM plan required |
| **1.25** | MIME Type Restrictions | Power Platform Premium | Managed Environments; optional Purview DLP |
| **1.26** | Agent File Upload and File Analysis Restrictions | Power Platform Premium | Copilot Studio v8+; Purview DLP for Zone 2+ |
| **1.27** | AI Agent Content Moderation Enforcement | Power Platform Premium | Native Copilot Studio content moderation |
| **1.28** | Policy-Based Agent Publishing Restrictions | Power Platform Premium | Tenant DLP policies; PPAC security scans |

---

## Pillar 2: Management Controls

| Control | Control Name | Required License | Notes |
|---------|--------------|------------------|-------|
| **2.1** | Managed Environments | Power Platform Premium | Per-environment license |
| **2.2** | Environment Groups | Power Platform Premium | Requires Managed Environments |
| **2.3** | Change Management | Power Platform Premium | ALM features |
| **2.4** | Business Continuity | Microsoft 365 E3+ | Documentation-focused |
| **2.5** | Testing & Validation | Power Platform Premium | Test environments |
| **2.6** | Model Risk Management | N/A (process) | Process/documentation control |
| **2.7** | Vendor Risk Management | N/A (process) | Process/documentation control |
| **2.8** | Access Control & SoD | Microsoft Entra ID P1+ | Security roles |
| **2.9** | Performance Monitoring | Power Platform Premium | Analytics features |
| **2.10** | Patch Management | Microsoft 365 E3+ | Automatic with SaaS |
| **2.11** | Bias Testing | N/A (process) | Process/documentation control |
| **2.12** | Supervision & Oversight | Microsoft 365 E5 (for monitoring) | Communication Compliance optional |
| **2.13** | Documentation & Records | Microsoft 365 E3+ | SharePoint/OneDrive storage |
| **2.14** | Training & Awareness | Microsoft 365 E3+ | Viva Learning optional |
| **2.15** | Environment Routing | Power Platform Premium | Managed Environments auto-provisioning |
| **2.16** | RAG Source Integrity | N/A (process) | Process/documentation control |
| **2.17** | Multi-Agent Orchestration Limits | Copilot Studio | Orchestration requires Copilot Studio |
| **2.18** | Automated Conflict of Interest | N/A (process) | Process/documentation control |
| **2.19** | Customer AI Disclosure | N/A (process) | Transparency/labeling requirement |
| **2.20** | Adversarial Testing / Red Team | N/A (process) | Process; optional Azure AI safety tools |
| **2.21** | AI Marketing Claims | N/A (process) | Process/documentation control |
| **2.22** | Inactivity Timeout Enforcement | Power Platform Premium | BAP Admin API for timeout configuration |
| **2.23** | User Consent and AI Disclosure Enforcement | Microsoft 365 E3+ | M365 Admin Center AI Disclaimer toggle |
| **2.24** | Agent Feature Enablement and Restriction Governance | Power Platform Premium | PPAC Copilot governance page |
| **2.25** | Agent 365 Governance Console | GA May 1, 2026 — Agent 365 or Microsoft 365 E7 per-user licensing | AI Admin/Global Admin/Global Reader roles |

---

## Pillar 3: Reporting Controls

| Control | Control Name | Required License | Notes |
|---------|--------------|------------------|-------|
| **3.1** | Agent Inventory | Microsoft 365 E3+ | M365 Admin Center |
| **3.2** | Usage Analytics | Power Platform Premium | CoE Toolkit recommended |
| **3.3** | Compliance Reporting | Microsoft 365 E5 | Purview reports |
| **3.4** | Incident Reporting | Microsoft 365 E3+ | Process/documentation |
| **3.5** | Cost Allocation | Power Platform Premium | License tracking |
| **3.6** | Orphaned Agent Detection | Power Platform Premium | Managed Environments feature |
| **3.7** | PPAC Security Posture | Power Platform Premium | Managed Environments security dashboard |
| **3.8** | Copilot Hub | Power Platform Premium + Microsoft 365 Copilot | PPAC Copilot Hub plus M365 admin center agent reporting; Agent overview metrics available with Agent 365 or M365 E7 licensing at GA |
| **3.9** | Microsoft Sentinel Integration | Microsoft Sentinel + E5 Security | Azure Sentinel workspace required |
| **3.10** | Hallucination Feedback Loop | Microsoft 365 E3+ | Process-focused; Purview optional |
| **3.11** | Centralized Agent Inventory Enforcement | Power Platform Premium | PPAC Agent Inventory feature |
| **3.12** | Agent Governance Exception and Override Management | Microsoft 365 E3+ | Dataverse/SharePoint exception register |

---

## Pillar 4: SharePoint Controls

| Control | Control Name | Required License | Notes |
|---------|--------------|------------------|-------|
| **4.1** | IAG / Restricted Content Discovery | SharePoint Advanced Management + at least one Microsoft 365 Copilot license | SAM required for IAG; RCD requires at least one Copilot license assigned in tenant (March 2026 prerequisite) |
| **4.2** | Site Access Reviews | Microsoft Entra ID P2 + SAM | Access Reviews + SAM |
| **4.3** | Retention Management | Microsoft 365 E5 or Microsoft Purview Suite | Data Lifecycle Management |
| **4.4** | Guest Access Controls | Microsoft 365 E3+ | Basic; E5 for advanced |
| **4.5** | Security Monitoring | SharePoint Advanced Management + E5 | SAM + Purview Audit |
| **4.6** | Grounding Scope Governance | SharePoint Advanced Management | Restricted SharePoint Search |
| **4.7** | M365 Copilot Data Governance | Microsoft 365 E5 or Microsoft Purview Suite | Purview data governance for Copilot |

---

## License Bundles for FSI

### Minimum (Zone 1 Only)
- Microsoft 365 E3
- Power Platform per-user (standard)

### Recommended (Zone 2)
- Microsoft 365 E5 or E3 + Microsoft Purview Suite
- Power Platform Premium (per-environment)
- Microsoft Entra ID P1

### Regulated (Zone 3)
- Microsoft 365 E5
- Power Platform Premium (per-environment for all production)
- Microsoft Entra ID P2
- SharePoint Advanced Management
- Copilot Studio (per-user or capacity-based)

---

## Premium Connector Licensing by Product

!!! info "Copilot Studio Includes All Premium Connectors"
    Premium connector licensing varies by product. This distinction is critical for cost planning.

| Product | Premium Connectors | Dataverse Access | Notes |
|---------|-------------------|------------------|-------|
| **Copilot Studio** | ✅ Included | ✅ Included (15 GB default) | No additional connector licensing required |
| **Power Apps** | Requires Premium license | Requires Premium license | Per-user or per-app licensing |
| **Power Automate** | Requires Premium license | Requires Premium license | Per-user or per-flow licensing |

**Common Misconception:** Teams building Copilot Studio agents do NOT need separate premium connector licenses. All premium connectors and Dataverse access (15 GB default capacity) are included with the Copilot Studio license at no additional cost.

**Power Apps/Power Automate Context:** Premium connector and Dataverse access require Power Apps Premium, Power Apps per app, Power Automate Premium, or Power Automate per flow licenses for all accessing users.

---

## Cost Optimization Tips

1. **Start with E3 + Add-ons**: Many FSI organizations start with E3 and add Microsoft Purview Suite and E5 Security as add-ons rather than full E5.

2. **Managed Environments per Environment**: Only production and UAT typically need Managed Environments; dev/test can use standard.

3. **SharePoint Advanced Management**: Only required if using IAG/RCD features for Zone 3 SharePoint governance.

4. **Entra ID P2 vs P1**: P2 is only required for Privileged Identity Management and Access Reviews; P1 covers Conditional Access.

5. **Copilot Studio Licensing**: Consider capacity-based licensing for high-volume agent scenarios vs. per-user for limited makers.

---

## License Verification

To verify current license assignments:

### Microsoft 365 Admin Center
1. Sign in to https://admin.microsoft.com
2. Navigate to **Billing** > **Licenses**
3. Review available and assigned licenses

### Power Platform Admin Center
1. Sign in to https://admin.powerplatform.microsoft.com
2. Navigate to **Manage** > **Environments**
3. Select an environment to view license type

### Entra Admin Center
1. Sign in to https://entra.microsoft.com
2. Navigate to **Identity** > **Users** > Select user > **Licenses**
3. Review assigned licenses

---

## Additional Resources

- [Power Platform Licensing Guide](https://learn.microsoft.com/en-us/power-platform/admin/pricing-billing-skus)
- [Microsoft 365 Licensing Guidance](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance)
- [Microsoft Purview Licensing](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-purview-service-description)
- [SharePoint Advanced Management](https://learn.microsoft.com/en-us/sharepoint/advanced-management)
- [Copilot Studio Licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions)

---

## Microsoft Agent 365 and Agent Management Essentials

> **GA note:** Microsoft Agent 365 reaches general availability on May 1, 2026 as part of Microsoft 365 E7 and standalone Agent 365 per-user licensing. Validate current terms in Microsoft Learn before procurement or production dependency decisions.

### Official prerequisites

| Requirement | Official guidance | Source |
|-------------|-------------------|--------|
| Tenant licensing | Agent 365 or Microsoft 365 E7 per-user licensing required; assign licenses from Microsoft 365 admin center | Agent 365 overview |
| Day-to-day admin roles | AI Admin, Global Admin, or Global Reader (view-only) can manage agents in Microsoft 365 admin center | Agent prerequisites / Manage agents |
| Power Platform admin roles | Power Platform Administrator or Dynamics 365 Administrator may still be needed for Copilot Studio environment administration | Agent prerequisites |
| Sensitive role hardening | Use Entra Privileged Identity Management for AI Admin and other high-privilege roles | Agent prerequisites |

### Microsoft Agent 365 Licensing at GA

| Licensing point | Microsoft-published guidance |
|-----------------|------------------------------|
| GA model (May 1, 2026) | At GA (May 1, 2026), Agent 365 transitions to per-user licensing. Agents acting on behalf of a licensed user are covered under that user's Agent 365 or Microsoft 365 E7 license |
| Included entitlement | Agents acting on behalf of a licensed user are covered under that user's **Agent 365** or **Microsoft 365 E7** license |
| Framework implication | Per-user licensing replaces the earlier per-agent-instance Frontier preview model; plan procurement and entitlement tracking accordingly |

### Control-specific interpretation

| Control | Licensing interpretation |
|---------|--------------------------|
| **2.25 - Agent 365 Governance Console** | Requires Agent 365 or Microsoft 365 E7 per-user licensing at GA (May 1, 2026) |
| **3.8 - Copilot Hub and Governance Dashboard** | Power Platform Premium covers PPAC Copilot Hub; Agent overview metrics and governance cards available with Agent 365 or M365 E7 licensing at GA (May 1, 2026) |
| **2.23 - User Consent and AI Disclosure Enforcement** | Follow Agent Management Essentials prerequisites for AI Admin role assignment and PIM when delegating admin-center agent governance |

### Microsoft Agent 365 Resources

- [Agent Management Essentials overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-essentials-overview)
- [Agent prerequisites](https://learn.microsoft.com/en-us/microsoft-365/copilot/agent-essentials/agent-prerequisites)
- [Microsoft Agent 365 overview](https://learn.microsoft.com/en-us/microsoft-agent-365/overview)
- [Agent 365 overview page in Microsoft 365 admin center](https://learn.microsoft.com/en-us/microsoft-365/admin/manage/agent-365-overview?view=o365-worldwide)
- [Copilot Control System overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/copilot-control-system/overview)

---

*Last Updated: March 2026 | Framework Version: v1.2.52*
