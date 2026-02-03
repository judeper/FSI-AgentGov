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
| **AI Administrator** | Manage M365 Copilot settings, AI services, and connector delegation | Microsoft 365 AI Administrator |

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

| Permission | AI Administrator | Entra Global Admin | Entra Security Admin |
|------------|------------------|---------------------|----------------------|
| Manage Copilot settings | ✓ | ✓ | ✗ |
| Manage Copilot connectors | ✓ | ✓ | ✗ |
| Register Entra apps (delegated) | ✓* | ✓ | ✗ |
| Consent to ExternalItem/ExternalConnection APIs | ✓ | ✓ | ✗ |
| Consent to all Graph APIs | ✗ | ✓ | ✗ |
| View Copilot usage reports | ✓ | ✓ | ✗ |
| Create support tickets | ✓ | ✓ | ✓ |
| Configure Defender XDR | ✗ | ✓ | ✓ |
| Manage Defender policies | ✗ | ✓ | ✓ |
| View Defender alerts | ✗ | ✓ | ✓ |
| Configure DLP policies | ✗ | ✓ | ✗ |

*Requires delegation via Entra admin consent or custom role for app registration and limited API consent scope.

!!! tip "FSI Least-Privilege Role Assignment"
    - **For agent governance and Copilot management:** Prefer AI Administrator over Global Admin to enforce least-privilege access
    - **For Copilot connector management:** AI Administrator is sufficient for most connector delegation tasks
    - **For Defender XDR operations:** Use Entra Security Admin (not Global Admin) for security operations teams
    - **When Global Admin is required:** Initial tenant setup, broad Graph API consent beyond ExternalItem/ExternalConnection scope, or cross-service configuration
    - **For FINRA-regulated firms:** Document role assignments in your supervisory procedures per FINRA Rule 3110

---

## Governance Roles (Non-Admin)

These roles appear in some controls under **Support & Questions** or governance workflows.

- **AI Governance Lead**
- **Compliance Officer**
- **Security Team** (organizational function, not a directory role)

---

*FSI Agent Governance Framework v1.2 - January 2026*
