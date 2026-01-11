# License Requirements by Control

Complete license mapping for all 48 FSI Agent Governance Framework controls.

---

## License Summary

| License | Controls Requiring | Primary Use |
|---------|-------------------|-------------|
| **Power Platform Premium** | 1.1, 1.4, 1.8, 1.14, 2.1, 2.2, 2.3, 2.8, 2.9, 3.2, 3.5, 3.6 | Managed Environments, ACP |
| **Microsoft 365 E5** | 1.5, 1.6, 1.7, 1.9, 1.10, 1.12, 1.13, 1.17 | Purview full suite |
| **Microsoft 365 E5 Compliance** | 1.5, 1.6, 1.7, 1.9, 1.10, 1.12, 1.13, 1.17 | Purview add-on to E3 |
| **Microsoft 365 E3** | 1.3, 1.11, 1.15, 1.16, 2.10 | Basic security features |
| **Microsoft Entra ID P1** | 1.11, 1.18, 2.8 | Conditional Access |
| **Microsoft Entra ID P2** | 1.11, 1.12, 4.2 | PIM, Access Reviews |
| **SharePoint Advanced Management** | 4.1, 4.2, 4.3, 4.4, 4.5 | SharePoint governance |
| **Copilot Studio** | All | Agent development |

---

## Pillar 1: Security Controls

| Control | Control Name | Required License | Notes |
|---------|--------------|------------------|-------|
| **1.1** | Restrict Agent Publishing | Power Platform Premium | Managed Environments required |
| **1.2** | Agent Registry | Microsoft 365 E3+ | Integrated Apps in M365 Admin |
| **1.3** | SharePoint Content Governance | Microsoft 365 E3+ | SharePoint included; SAM for advanced |
| **1.4** | Advanced Connector Policies | Power Platform Premium | Managed Environments + Environment Groups |
| **1.5** | DLP and Sensitivity Labels | Microsoft 365 E5 or E5 Compliance | Purview DLP + Information Protection |
| **1.6** | DSPM for AI | Microsoft 365 E5 or E5 Compliance | Microsoft Purview DSPM for AI |
| **1.7** | Audit Logging | Microsoft 365 E5 (Premium) or E3 (Standard) | E5 for 10-year retention |
| **1.8** | Runtime Protection | Power Platform Premium | Managed Environments feature |
| **1.9** | Data Retention | Microsoft 365 E5 or E5 Compliance | Data Lifecycle Management |
| **1.10** | Communication Compliance | Microsoft 365 E5 or E5 Compliance | Purview Communication Compliance |
| **1.11** | Conditional Access & MFA | Microsoft Entra ID P1 (basic) or P2 (advanced) | P2 for risk-based policies |
| **1.12** | Insider Risk | Microsoft 365 E5 or E5 Insider Risk | Purview Insider Risk Management |
| **1.13** | Sensitive Information Types | Microsoft 365 E5 or E5 Compliance | Custom SITs require E5 |
| **1.14** | Data Minimization | Power Platform Premium | Environment-level controls |
| **1.15** | Encryption | Microsoft 365 E3+ | Default encryption included |
| **1.16** | IRM for Documents | Microsoft 365 E3+ | Azure Information Protection |
| **1.17** | Endpoint DLP | Microsoft 365 E5 or E5 Compliance | Endpoint DLP |
| **1.18** | RBAC | Microsoft Entra ID P1+ | Role management |

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

---

## Pillar 4: SharePoint Controls

| Control | Control Name | Required License | Notes |
|---------|--------------|------------------|-------|
| **4.1** | IAG / Restricted Content Discovery | SharePoint Advanced Management | Required for IAG |
| **4.2** | Site Access Reviews | Microsoft Entra ID P2 + SAM | Access Reviews + SAM |
| **4.3** | Retention Management | Microsoft 365 E5 or E5 Compliance | Data Lifecycle Management |
| **4.4** | Guest Access Controls | Microsoft 365 E3+ | Basic; E5 for advanced |
| **4.5** | Security Monitoring | SharePoint Advanced Management + E5 | SAM + Purview Audit |

---

## License Bundles for FSI

### Minimum (Zone 1 Only)
- Microsoft 365 E3
- Power Platform per-user (standard)

### Recommended (Zone 2)
- Microsoft 365 E5 or E3 + E5 Compliance
- Power Platform Premium (per-environment)
- Microsoft Entra ID P1

### Regulated (Zone 3)
- Microsoft 365 E5
- Power Platform Premium (per-environment for all production)
- Microsoft Entra ID P2
- SharePoint Advanced Management
- Copilot Studio (per-user or capacity-based)

---

## Cost Optimization Tips

1. **Start with E3 + Add-ons**: Many FSI organizations start with E3 and add E5 Compliance and E5 Security as add-ons rather than full E5.

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

*Last Updated: January 2026*
