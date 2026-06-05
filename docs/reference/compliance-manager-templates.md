# Microsoft Purview Compliance Manager Templates Reference

**Purpose:** This reference summarises the Microsoft Purview Compliance Manager **assessment template catalog** as it pertains to US financial services governance of Microsoft 365 AI agents. Compliance Manager is a Microsoft Purview surface that ships a library of 360+ regulatory and standards templates that customers can use to map their own controls to a specific framework, run improvement actions, and produce examiner-ready evidence.

**Scope reminder.** Compliance Manager (CM) is a **template / control-mapping surface**. It is distinct from the Microsoft **Service Trust Portal** (STP), which is the vendor attestation / audit-report repository — see the [Service Trust Portal Attestation Evidence Guide](service-trust-portal-attestation-guide.md) for how Microsoft's own attestations (SOC 2 Type 2, ISO 27001/27017/27018/27701/42001, FedRAMP, etc.) are surfaced for examiner / vendor risk-management evidence.

**Relationship to the framework.** Compliance Manager templates are an **input** to the framework's regulatory mapping (see [`regulatory-mappings.md`](regulatory-mappings.md)) and an **output destination** for evidence collected via the controls in this catalog. The framework does not depend on Compliance Manager — it is one of several optional implementation surfaces (Sentinel ([Control 3.9](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md)), Purview Audit ([Control 1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md)), and the [Automated Assessment Engine](assessment-coverage.md) are alternative or complementary paths).

---

## Catalog Snapshot

Microsoft maintains the canonical and current list at [Microsoft Learn — Compliance Manager templates list](https://learn.microsoft.com/en-us/purview/compliance-manager-templates-list). As of the framework's last verification, the catalog includes 360+ templates across the following families:

| Family | Representative templates relevant to US FSI |
|--------|----------------------------------------------|
| **US federal financial regulation** | FFIEC IT Examination Handbook, GLBA (Gramm-Leach-Bliley Act), Sarbanes-Oxley (SOX), Federal Reserve Supervisory Letter Fed SR 26-2 (formerly SR 11-7) (Model Risk), OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12) (Technology Risk Management), Dodd-Frank elements |
| **US sector / SRO** | FINRA recordkeeping and supervision frameworks, SEC Rule 17a-3/17a-4 recordkeeping, CFTC Part 1.31 |
| **US state financial regulation** | NYDFS 23 NYCRR Part 500 (Cybersecurity), CCPA / CPRA (California Privacy), New York Privacy frameworks |
| **US security & privacy frameworks** | NIST 800-53 Rev 5, NIST 800-171, NIST CSF 2.0, NIST AI Risk Management Framework, FedRAMP Moderate/High, CMMC Level 2 |
| **International standards** | ISO/IEC 27001, ISO/IEC 27017, ISO/IEC 27018, ISO/IEC 27701, ISO/IEC 42001 (AI Management Systems), ISO/IEC 27017 cloud-services profile |
| **Healthcare / privacy** | HIPAA / HITECH, GDPR (EU), PIPEDA (Canada), LGPD (Brazil) |
| **Payments / industry** | PCI DSS v4.0, SWIFT Customer Security Programme |
| **AI-specific** | EU AI Act, NIST AI RMF 1.0, ISO/IEC 42001:2023 |
| **Audit / attestation overlays** | SOC 2 Trust Services Criteria, SOC 1 (SSAE-18), AICPA Service Organization Controls overlays |

> **Source of truth:** Always re-verify the current template list and version tags at [Microsoft Learn — Compliance Manager templates list](https://learn.microsoft.com/en-us/purview/compliance-manager-templates-list). Microsoft adds and deprecates templates on its own cadence; this file is a navigational summary, not an authoritative catalog.

---

## Entitlement Requirements

Compliance Manager is part of Microsoft Purview. The free tier surfaces the **Microsoft Data Protection Baseline** template only. Premium templates require additional entitlements:

| Template family | Minimum entitlement |
|-----------------|---------------------|
| Microsoft Data Protection Baseline | Any Microsoft 365 / Office 365 commercial subscription (free) |
| Premium templates (FFIEC, GLBA, SOX, NIST 800-53, ISO 27001, SOC 2, PCI DSS, HIPAA, EU AI Act, ISO/IEC 42001, etc.) | **Microsoft 365 E5 / A5 / G5 Compliance**, **Microsoft 365 E5 / A5 / G5 Information Protection & Governance**, or **Microsoft 365 E5 / A5 / G5 Risk Management & Privacy** |
| Industry-specific overlays (some Microsoft 365 industry templates) | May require add-on packs or industry-specific licensing — verify per template |

> **Licensing caveat.** Microsoft licensing changes regularly. Always re-verify against the current [Microsoft 365 Comparison Table](https://www.microsoft.com/en-us/microsoft-365/enterprise/microsoft365-plans-and-pricing) and [Microsoft 365 Service Description for Compliance Manager](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-365-security-compliance-licensing-guidance) before quoting an entitlement to a customer.

---

## Mapping Common FSI Templates to Framework Controls

The table below maps the most-frequently-requested Compliance Manager templates to the FSI Agent Governance controls that contribute evidence to those templates' control mappings. The framework's [Regulatory Mappings reference](regulatory-mappings.md) carries the full crosswalk; the table here is a quick orientation for compliance officers selecting which controls to prioritise when standing up a Compliance Manager assessment.

| Compliance Manager template | Primary framework controls contributing evidence | Supporting framework controls |
|------------------------------|---------------------------------------------------|--------------------------------|
| **FFIEC IT Examination Handbook** | [1.7 Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [2.1 Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md), [2.6 Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.7 Vendor Risk](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | [1.5 DLP](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.15 Encryption](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md), [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) |
| **GLBA 501(b) Safeguards Rule** | [1.5 DLP](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.13 SITs](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md), [1.15 Encryption](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md), [2.1 Managed Environments — Customer Lockbox sub-section](../controls/pillar-2-management/2.1-managed-environments.md#customer-lockbox-data-residency-posture) | [1.7 Audit](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [2.7 Vendor Risk](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) |
| **Sarbanes-Oxley (SOX) §302 / §404** | [2.1 Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md), [2.3 Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [2.8 Segregation of Duties](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md), [2.12 Supervision (FINRA 3110)](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | [1.7 Audit](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) |
| **Federal Reserve SR 26-2 (formerly SR 11-7) (Model Risk)** | [2.6 Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.11 Bias / Fairness Testing](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.7 Vendor Risk](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) |
| **OCC Bulletin 2026-13 (formerly OCC Bulletin 2011-12)** | [2.6 Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.7 Vendor Risk](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) |
| **NYDFS 23 NYCRR 500** | [1.7 Audit](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.15 Encryption](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md), [2.1 Managed Environments — Customer Lockbox sub-section](../controls/pillar-2-management/2.1-managed-environments.md#customer-lockbox-data-residency-posture), [3.9 Sentinel](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | [1.5 DLP](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [2.7 Vendor Risk](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) |
| **NIST 800-53 Rev 5** | All Pillar 1 (Security) and Pillar 3 (Reporting) controls contribute; consult [`regulatory-mappings.md`](regulatory-mappings.md) for the full crosswalk | — |
| **NIST AI Risk Management Framework** | [2.6 Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.11 Bias / Fairness](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [1.21 Prompt Injection / RAI](../controls/pillar-1-security/1.21-adversarial-input-logging.md) — see [`nist-ai-rmf-crosswalk.md`](nist-ai-rmf-crosswalk.md) for the 67/72 subcategory mapping | All controls contribute via the crosswalk |
| **ISO/IEC 27001 + 27017 + 27018 + 27701** | [1.5 DLP](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.7 Audit](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.15 Encryption](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md), [2.1 Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md), [2.7 Vendor Risk](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | All other Pillar 1 / 2 controls |
| **ISO/IEC 42001:2023 (AI Management Systems)** | [2.6 Model Risk](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.11 Bias / Fairness](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | All Pillar 2 (Management) controls |
| **SOC 2 Trust Services Criteria** | [1.7 Audit](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.15 Encryption](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md), [2.1 Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md), [2.8 Segregation of Duties](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | All Pillar 1 / 2 controls — note Microsoft's own SOC 2 attestation is sourced from STP per the [Service Trust Portal Attestation Guide](service-trust-portal-attestation-guide.md) |
| **PCI DSS v4.0** | [1.5 DLP](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.13 SITs](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md), [1.15 Encryption](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md), [2.7 Vendor Risk](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | [1.7 Audit](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
| **HIPAA / HITECH** | [1.5 DLP](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), [1.13 SITs](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md), [1.15 Encryption](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Mostly out of scope for FSI agents; included where firm operates an integrated wealth/insurance/health business |
| **EU AI Act** | [2.6 Model Risk](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md), [2.11 Bias / Fairness](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.7 Vendor Risk](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md), [3.1 Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Applicable where firm operates EU subsidiary or services EU customers; combine with [`regulatory-mappings.md`](regulatory-mappings.md) EU section |

---

## Implementation Notes

- **Pre-built improvement actions.** Each Compliance Manager template ships with Microsoft-recommended improvement actions (technical and operational) pre-mapped to its control framework. Customers should treat these as a starting point, not a finished assessment — many recommended actions require organisation-specific evidence and approval workflows that the framework's [Implementation Playbooks](../playbooks/control-implementations/index.md) supply.
- **Customer actions vs Microsoft actions.** Compliance Manager distinguishes **customer-managed** improvement actions (the firm's responsibility) from **Microsoft-managed** actions (Microsoft's own controls, validated via the Service Trust Portal attestations referenced in the [Service Trust Portal Attestation Evidence Guide](service-trust-portal-attestation-guide.md)). FSI compliance officers should pull both classes when assembling examiner evidence packs.
- **Evidence retention.** Compliance Manager retains assessment evidence per the firm's Microsoft 365 retention policies. For examiner-grade retention (FINRA 4511 / SEC 17a-4 / CFTC 1.31), pair Compliance Manager evidence exports with the records-retention pattern in [Control 1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md).
- **Automation interplay.** The framework's [Automated Assessment Engine](assessment-coverage.md) and [Honest Coverage Matrix](assessment-coverage.md) operate independently from Compliance Manager. They emit JSON/Markdown evidence that maps to the same controls but does not write into Compliance Manager. Where the firm wants a single dashboard, the [Solutions Index](solutions-index.md) catalogues integration patterns.

---

## Related Reference

- [Service Trust Portal Attestation Evidence Guide](service-trust-portal-attestation-guide.md) — Microsoft's own SOC 2 Type 2, ISO 27001/27017/27018/27701/42001, FedRAMP, and other attestation reports
- [Regulatory Mappings](regulatory-mappings.md) — full crosswalk of US FSI regulations to framework controls
- [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md) — 67/72 subcategory mapping to controls
- [Microsoft CAPE Crosswalk](microsoft-cape-crosswalk.md) — alignment with Microsoft's Cloud Adoption Framework for AI
- [Assessment Engine Coverage](assessment-coverage.md) — honest report of which framework controls have automated evaluators

---

## Microsoft Learn Sources

- [Microsoft Purview Compliance Manager — overview](https://learn.microsoft.com/en-us/purview/compliance-manager)
- [Compliance Manager templates list](https://learn.microsoft.com/en-us/purview/compliance-manager-templates-list)
- [Compliance Manager regional availability](https://learn.microsoft.com/en-us/purview/compliance-manager-templates)
- [Compliance Manager templates — assessment template properties](https://learn.microsoft.com/en-us/purview/compliance-manager-templates)
- [Microsoft 365 security & compliance licensing guidance](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-365-security-compliance-licensing-guidance)
- [Compliance Manager improvement actions](https://learn.microsoft.com/en-us/purview/compliance-manager-improvement-actions)

---

*Updated: May 2026 | Version: v1.6.2 | Verification Status: Current*
