# Administrator Role Catalog

Canonical, framework-friendly role names used throughout this framework (controls, templates, and downloads).

---

## How to Use This Catalog

- **Primary Owner Admin Role**: each control should name **one** primary owner role (who is accountable for implementing/configuring that control).
- **Supporting Roles** (optional): add only when needed for access, evidence collection, or shared responsibility.
- **Naming rule**: use the **canonical short name** from this page in control prerequisites.

> This catalog is intentionally **framework-friendly** (short names). It is not a complete list of all Microsoft built-in role display names.

---

## Canonical Roles (Short Names)

### Entra (Identity)

| Canonical Role | Typical Responsibilities | Accepted Aliases (Normalize From) |
|---|---|---|
| **Entra Global Admin** | Tenant-wide configuration and access | Global Administrator, Global Admin |
| **Entra Privileged Role Admin** | Role assignment and privileged access | Privileged Role Administrator |
| **Entra App Admin** | App registrations and enterprise apps | Application Administrator |
| **Entra User Admin** | User and group administration | User Administrator |
| **Entra Identity Governance Admin** | Access reviews, entitlement management | Identity Governance Administrator |
| **Entra Security Admin** | Security configuration, policy, and Defender XDR access | Security Administrator, Defender XDR Admin (informal) |
| **Entra Global Reader** | Read-only tenant visibility | Global Reader |
| **Entra Security Reader** | Read-only security visibility | Security Reader |
| **AI Administrator** | Manage M365 Copilot settings, AI services, connector delegation, Copilot feature access controls, and agent governance settings | Microsoft 365 AI Administrator |
| **Entra Agent ID Admin** | Manage agent identity registrations and lifecycle | Agent ID Administrator |
| **Entra Agent ID Developer** | Register and configure agent identities | Agent ID Developer |

!!! note "Agent 365 Role Limitations (February 2026)"
    Agent 365 administrative access is currently limited to Entra Global Admin and AI Administrator roles only. No fine-grained or read-only administrative roles are planned for GA. Microsoft is collecting feedback on role granularity requirements. Organizations should plan Agent 365 governance workflows around these two roles and use Entra Privileged Identity Management (PIM) for just-in-time elevation where possible.

!!! note "Defender XDR Administrator"
    "Defender XDR Administrator" is informal terminology used in community and operational contexts. There is no distinct Microsoft Entra built-in role named "Defender XDR Administrator." The official role for managing Microsoft Defender XDR is **Entra Security Admin** (Security Administrator). This framework uses "Entra Security Admin" as the canonical name and accepts "Defender XDR Admin" as a normalization alias. See [Microsoft Learn: Manage access to Defender XDR](https://learn.microsoft.com/en-us/defender-xdr/m365d-permissions) for authoritative role documentation.

### Purview (Compliance)

| Canonical Role | Typical Responsibilities | Accepted Aliases (Normalize From) |
|---|---|---|
| **Purview Compliance Admin** | Core compliance configuration | Compliance Administrator, Purview Compliance Administrator |
| **Purview Compliance Reader** | Read-only compliance visibility | Compliance Reader |
| **Purview Compliance Data Admin** | Compliance data access/exports | Compliance Data Administrator |
| **Purview Info Protection Admin** | Labels, policies, and information protection | Information Protection Admin |
| **Purview Records Manager** | Retention/records governance | Records Management Administrator, Records Manager |
| **Purview Audit Admin** | Audit configuration | Audit Administrator |
| **Purview Audit Reader** | Audit search/read-only | Audit Log Reader |
| **Compliance Manager Admin** | Compliance Manager setup and templates | Compliance Manager Administrator |
| **Purview Communication Compliance Roles** | Communication compliance workflows | Communication Compliance Admin/Analyst/Investigator/Viewer |
| **Purview Insider Risk Roles** | Insider risk program workflows | Insider Risk Management Admin/Analyst/Investigator/Auditor |
| **Purview eDiscovery Roles** | eDiscovery workflows | eDiscovery Administrator/Manager/Case Member |
| **Purview Data Security AI Viewer** | View-only access to DSPM for AI dashboards and reports | Data Security AI Viewer |
| **Purview Data Security AI Content Viewer** | View sensitive content flagged by DSPM for AI policies | Data Security AI Content Viewer |

### Power Platform (PPAC / Copilot Studio)

| Canonical Role | Typical Responsibilities | Accepted Aliases (Normalize From) |
|---|---|---|
| **Power Platform Admin** | Tenant-level Power Platform governance | Power Platform Administrator, Power Platform Admin |
| **Environment Admin** | Environment-level administration | Environment Administrator, Environment Admin |
| **Power Automate Admin** | Power Automate governance | Power Automate Administrator |
| **Pipeline Admin** | Deployment pipeline administration | Pipeline Administrator |

### Scenario-Based Roles (Use Only When Needed)

| Canonical Role | When to Use | Accepted Aliases (Normalize From) |
|---|---|---|
| **Dataverse System Admin** | When a control requires Dataverse security role elevation | System Administrator, Power Platform System Administrator |
| **SharePoint Admin** | SharePoint tenant settings and governance | SharePoint Administrator, SharePoint Admin |
| **SharePoint Site Collection Admin** | Site collection admin operations | Site Collection Administrator |
| **SharePoint Site Owner** | Site-level ownership tasks | SharePoint Site Owner, Site Owner |

---

## AI Governance Permission Matrix

| Permission | AI Administrator | Entra Global Admin | Entra Security Admin | Power Platform Admin |
|------------|------------------|---------------------|----------------------|----------------------|
| Manage Copilot settings | ✓ | ✓ | ✗ | ✗ |
| Manage Copilot connectors | ✓ | ✓ | ✗ | ✗ |
| Register Entra apps (delegated) | ✓* | ✓ | ✗ | ✗ |
| Consent to ExternalItem/ExternalConnection APIs | ✓ | ✓ | ✗ | ✗ |
| Consent to all Graph APIs | ✗ | ✓ | ✗ | ✗ |
| View Copilot usage reports | ✓ | ✓ | ✗ | ✗ |
| Manage AI feature access controls | ✓ | ✓ | ✗ | ✗ |
| Configure Admin Exclusion Groups | ✓ | ✓ | ✗ | ✗ |
| Create support tickets | ✓ | ✓ | ✓ | ✓ |
| Configure Defender XDR | ✗ | ✓ | ✓ | ✗ |
| Manage Defender policies | ✗ | ✓ | ✓ | ✗ |
| View Defender XDR security reports | ✗ | ✓ | ✓ | ✗ |
| Manage Conditional Access for agents | ✗ | ✓ | ✓ | ✗ |
| Configure DLP policies | ✗ | ✓ | ✗ | ✗ |
| Manage Power Platform environments | ✗ | ✓ | ✗ | ✓ |
| Configure Power Platform DLP | ✗ | ✓ | ✗ | ✓ |

*Requires delegation via Entra admin consent or custom role for app registration and limited API consent scope.

!!! tip "FSI Least-Privilege Role Assignment"
    - **For agent governance and Copilot management:** Prefer AI Administrator over Global Admin to enforce least-privilege access
    - **For Copilot connector management:** AI Administrator is sufficient for most connector delegation tasks
    - **For Defender XDR operations:** Use Entra Security Admin (not Global Admin) for security operations teams
    - **When Global Admin is required:** Initial tenant setup, broad Graph API consent beyond ExternalItem/ExternalConnection scope, or cross-service configuration
    - **For FINRA-regulated firms:** Document role assignments in your supervisory procedures per FINRA Rule 3110

## Role Selection Guidance

For FSI organizations implementing agent governance, selecting the right administrative role is critical for separation of duties and least-privilege compliance.

| Scenario | Recommended Role | Why Not Global Admin | Regulatory Alignment |
|----------|------------------|----------------------|---------------------|
| Manage Copilot settings and feature access | AI Administrator | Scoped to AI services only; prevents unnecessary tenant-wide access | FINRA 3110: least-privilege supervisory access |
| Manage Copilot connectors and delegation | AI Administrator | Sufficient permissions for connector management without broad admin scope | SOX 404: segregation of duties |
| Configure Defender XDR policies for AI workloads | Entra Security Admin | Security-scoped; no need for full tenant administration | OCC 2011-12: security operations separation |
| Configure DLP policies for AI applications | Purview Compliance Admin | Dedicated compliance role; Global Admin is overprivileged | GLBA 501(b): data protection oversight |
| Manage Power Platform environments | Power Platform Admin | Platform-scoped; AI Admin cannot manage environments | SOX 404: platform vs. AI governance separation |
| Initial tenant setup and broad API consent | Entra Global Admin | Required for initial configuration only; delegate afterward | Industry best practice: time-boxed elevation |

!!! tip "FSI Role Assignment Best Practice"
    For FINRA-regulated firms: Document all administrative role assignments in your Written Supervisory Procedures (WSPs). Use Entra Privileged Identity Management (PIM) to require just-in-time elevation for Global Admin access. Prefer AI Administrator for day-to-day Copilot governance and Entra Security Admin for Defender XDR security operations.

---

## Governance Roles (Non-Admin)

These roles appear in some controls under **Support & Questions** or governance workflows.

- **AI Governance Lead**
- **Compliance Officer**
- **Security Team** (organizational function, not a directory role)

---

*FSI Agent Governance Framework v1.2 - February 2026*
