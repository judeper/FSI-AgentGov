# Service Trust Portal Attestation Evidence Guide

**Purpose:** This guide explains how to use the Microsoft **Service Trust Portal (STP)** to pull Microsoft's own attestation and audit-report evidence (SOC 2 Type 2, ISO 27001/27017/27018/27701/42001, FedRAMP, etc.) for examiner submissions and vendor risk-management evidence packages.

**Scope reminder.** STP is the Microsoft attestation / audit-report repository — a **vendor evidence surface** that customers download from. It is **distinct from Microsoft Purview Compliance Manager**, which is a **template / control-mapping surface** customers use to map their own controls to a regulatory framework. The two surfaces are complementary:

| Surface | Direction of evidence | Purpose | Reference |
|---------|------------------------|---------|-----------|
| **Service Trust Portal (STP)** | Microsoft → Customer (download) | Microsoft's own third-party attestations and audit reports | This guide |
| **Microsoft Purview Compliance Manager** | Customer-authored control mappings | Map customer's controls to a regulatory framework template | [Compliance Manager Templates Reference](compliance-manager-templates.md) |

Conflating the two leaves an evidence gap — examiners typically want both Microsoft's attestation pack (from STP) and the firm's own control evidence (assembled via Compliance Manager + the framework's [Automated Assessment Engine](assessment-coverage.md)).

---

## Accessing the Service Trust Portal

| Cloud | URL | Sign-in |
|-------|-----|---------|
| Commercial (Global) | [`https://servicetrust.microsoft.com`](https://servicetrust.microsoft.com) | Work or school account; no special role required to browse the public report library, but downloads require sign-in |

**No tenant-side configuration required.** Any signed-in customer can access STP. There is no Compliance Manager dependency, no Purview entitlement, and no Power Platform requirement.

---

## Categories of Microsoft Attestations Available

| Category | Representative reports | Refresh cadence | Typical FSI use |
|----------|------------------------|-----------------|------------------|
| **SOC 1 Type 2** | Microsoft 365, Azure, Dynamics 365 | Annual (12-month observation period) | SOX 404 ICFR sub-service-organization evidence |
| **SOC 2 Type 2** | Microsoft 365, Azure, Dynamics 365, Power Platform | Annual (sometimes semi-annual delta reports) | FINRA / SEC examination, vendor due diligence under Interagency Guidance / OCC 2013-29 |
| **SOC 3** | Public-disclosure version of SOC 2 | Annual | Public posting; satisfies general due-diligence questionnaires |
| **ISO/IEC 27001** | Information Security Management System certification | 3-year certification cycle with annual surveillance audits | ISO 27001 vendor-equivalence questionnaires |
| **ISO/IEC 27017** | Cloud-services security profile | 3-year cycle | Cloud-specific control evidence |
| **ISO/IEC 27018** | Cloud-services PII protection | 3-year cycle | GLBA / GDPR / CCPA personal-data-processing evidence |
| **ISO/IEC 27701** | Privacy Information Management System | 3-year cycle | Privacy-program evidence |
| **ISO/IEC 42001:2023** | AI Management System (the AI MS standard) | New standard; check STP for Microsoft's first attestation cycle | EU AI Act / NIST AI RMF vendor evidence |
| **HITRUST CSF** | Selected Microsoft 365 services | 2-year cycle | Healthcare-adjacent FSI lines (insurance, integrated wealth-and-health) |
| **PCI DSS Attestation of Compliance (AoC)** | Azure | Annual | Card-data processing where Azure is in scope |
| **CSA STAR Level 2** | Cloud Security Alliance attestation | Annual | Cloud-specific vendor due diligence |
| **NIST CSF / 800-53 Mappings** | Microsoft-published mappings showing how Microsoft 365 / Azure controls map to NIST families | Per Microsoft cadence | Combine with Compliance Manager NIST templates |
| **EU Model Clauses / DPA** | Microsoft Online Services Data Protection Addendum, Standard Contractual Clauses | Updated as regulation evolves | GDPR Article 28 processor evidence |
| **Country / region-specific** | Australia IRAP, Singapore MTCS, Japan ISMAP, Spain ENS, etc. | Per scheme cadence | Cross-border subsidiaries |

> **Verify per service.** Microsoft's attestation scope varies by service. Always open the actual report and check the **scope** section before relying on it for a specific Microsoft service.

---

## How to Download Reports for an Evidence Pack

1. Navigate to [`https://servicetrust.microsoft.com`](https://servicetrust.microsoft.com) and sign in.
2. Open **Reports & White Papers** (or use the search bar).
3. Filter by:
    - **Industry** (e.g., Financial Services)
    - **Region** (e.g., United States)
    - **Cloud Service** (Microsoft 365, Azure, Dynamics 365, Power Platform)
    - **Compliance Framework** (SOC, ISO, FedRAMP, etc.)
4. For each required report, download the PDF (and any accompanying mappings/SOC bridge letters).
5. Capture the **report effective date**, **report period covered**, and **next-expected-refresh date** in the firm's vendor evidence register. Reports older than the report-period end date should be supplemented with a SOC bridge letter (also available on STP) until the next annual report is published.
6. Validate hash integrity if your evidence-retention policy requires it (compute SHA-256 of the downloaded PDF and store alongside in the evidence register).
7. File the report into the firm's vendor risk-management package per [Control 2.7 — Vendor and Third-Party Risk Management](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md).

> **Bridge letters.** Between annual SOC report cycles, Microsoft publishes a "bridge letter" (a.k.a. gap letter) that confirms no material change to the control environment since the last SOC report. Always pair the most recent SOC report with the latest bridge letter when the report's period-end is more than 90 days old.

---

## Refresh Cadence Summary

| Report family | Typical refresh | When to re-pull |
|---------------|-----------------|------------------|
| SOC 1 / SOC 2 Type 2 | Annual; Microsoft sometimes publishes semi-annual delta reports | Annually + after any Microsoft service-update advisory affecting in-scope services |
| ISO 27001 / 27017 / 27018 / 27701 | 3-year cycle, annual surveillance | Annually (capture surveillance results) |
| ISO/IEC 42001 | New (2023 standard); first Microsoft cycle in progress | Verify status quarterly until cycle stabilises |
| FedRAMP | Annual continuous-monitoring summary; 3-year recertification | Annually for federal-regulator evidence |
| PCI DSS AoC | Annual | Annually for card-data scenarios |
| Microsoft DPA / Model Clauses | As regulation evolves | Quarterly check |
| Country-specific (IRAP, MTCS, ISMAP, ENS) | Per scheme | Per scheme cadence |

---

## FSI-Specific: Which Attestations Are Accepted by Which Regulators

The acceptance below reflects common examiner expectations; the firm should always confirm with examination staff before substituting a Microsoft attestation for a customer-conducted control test.

| US regulator / regime | Commonly accepted Microsoft attestations | Notes |
|------------------------|------------------------------------------|-------|
| **OCC, Federal Reserve, FDIC** (national / state-member banks) | SOC 1 Type 2, SOC 2 Type 2, FedRAMP Moderate/High, ISO 27001 | Interagency Guidance on Third-Party Relationships (June 2023) and OCC Bulletin 2013-29 require the bank to "conduct ongoing monitoring" — Microsoft attestations are an input, not a substitute |
| **NCUA** (federal credit unions) | SOC 1 Type 2, SOC 2 Type 2, FedRAMP | Often paired with credit-union-specific vendor questionnaires |
| **SEC, FINRA** (broker-dealers, IAs) | SOC 2 Type 2, ISO 27001, FedRAMP (where federally regulated affiliates exist) | FINRA Rule 3110 supervisory framework; SEC Reg S-P (Privacy of Consumer Financial Information) |
| **CFTC, NFA** (futures commission merchants, CTAs) | SOC 2 Type 2, ISO 27001 | CFTC Part 1.31 records-management requirements; NFA Self-Examination Questionnaire |
| **NYDFS** (23 NYCRR 500) | SOC 2 Type 2, ISO 27001 / 27017 / 27018, FedRAMP | NYDFS expects the firm to perform its own Third-Party Service Provider risk assessment per 500.11 — Microsoft attestations are an input |
| **CFPB** (consumer financial protection — Reg Z, Reg E, etc.) | SOC 2 Type 2, ISO 27001 / 27018 / 27701 | Privacy attestations especially relevant for ECOA / fair-lending agent scenarios |
| **State insurance regulators** (NAIC Insurance Data Security Model Law adopters) | SOC 2 Type 2, ISO 27001 | State-by-state variability; verify per insurance commissioner |

> **Examiner-pack pattern.** A typical examiner submission for a Microsoft 365 AI agent program includes: **(1)** Microsoft SOC 2 Type 2 (current report + bridge letter), **(2)** Microsoft FedRAMP attestation if a regulated affiliate is in scope, **(3)** Microsoft ISO 27001 + 27017 + 27018, **(4)** the firm's own Compliance Manager assessment for the relevant US framework (FFIEC, GLBA, SOX, NYDFS), **(5)** the firm's [Automated Assessment Engine](assessment-coverage.md) output mapped to the framework controls, and **(6)** Microsoft's DPA + Standard Contractual Clauses where any non-US data is in scope.

---

## Cross-References

This guide complements:

- [Compliance Manager Templates Reference](compliance-manager-templates.md) — customer's own control-mapping surface
- [Control 2.7 — Vendor and Third-Party Risk Management](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) — Section 10 of 2.7 references STP at a high level; this guide is the detailed companion
- [Control 2.1 — Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md) — Customer Lockbox & Data Residency Posture sub-section references STP as part of the Lockbox-coverage-gap evidence pattern
- [Control 2.6 — Model Risk Management](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) — vendor-model risk evidence pattern
- [Regulatory Mappings](regulatory-mappings.md) — full US FSI regulation crosswalk
- [Solutions Coverage Gaps](solutions-coverage-gaps.md) — known limits of the framework's automated coverage

---

## Microsoft Learn Sources

- [Microsoft Service Trust Portal — main entry](https://servicetrust.microsoft.com)
- [Microsoft Learn: Get started with the Microsoft Service Trust Portal](https://learn.microsoft.com/en-us/microsoft-365/compliance/get-started-with-service-trust-portal)
- [Microsoft Learn: Microsoft compliance offerings (canonical attestation list)](https://learn.microsoft.com/en-us/compliance/regulatory/offering-home)
- [Microsoft Learn: Microsoft Online Services Data Protection Addendum](https://learn.microsoft.com/en-us/compliance/regulatory/gdpr-dpia-office365)
- [Microsoft Learn: SOC 2 Type 2 (Microsoft compliance)](https://learn.microsoft.com/en-us/compliance/regulatory/offering-soc-2)
- [Microsoft Learn: ISO/IEC 27001 (Microsoft compliance)](https://learn.microsoft.com/en-us/compliance/regulatory/offering-iso-27001)
- [Microsoft Learn: FedRAMP (Microsoft compliance)](https://learn.microsoft.com/en-us/compliance/regulatory/offering-fedramp)
- [Microsoft Learn: ISO/IEC 42001 (AI Management System)](https://learn.microsoft.com/en-us/compliance/regulatory/offering-iso-42001)
- [Interagency Guidance on Third-Party Relationships: Risk Management (Federal Reserve SR 23-04)](https://www.federalreserve.gov/supervisionreg/srletters/SR2304.htm)
- [OCC Bulletin 2013-29: Third-Party Relationships — Risk Management Guidance](https://www.occ.treas.gov/news-issuances/bulletins/2013/bulletin-2013-29.html)

---

*Updated: May 2026 | Version: v1.6.2 | Verification Status: Current*
