# Evidence Standards for Control Implementation

## Overview

This document establishes standards for collecting, documenting, and retaining evidence of control implementation across the FSI Agent Governance Framework. Consistent evidence practices support regulatory examinations, internal audits, and ongoing governance validation.

---

## Purpose

Evidence standards help organizations:

- **Demonstrate compliance** to regulators during examinations
- **Support internal audits** with consistent documentation
- **Enable point-in-time reconstruction** of control configurations
- **Facilitate knowledge transfer** across governance teams
- **Reduce examination preparation time** through organized evidence packages

---

## Evidence Types

### Primary Evidence Categories

| Evidence Type | Description | Use Case | Format |
|---------------|-------------|----------|--------|
| **Screenshots** | Portal configuration captures | UI-based configuration verification | PNG/PDF with metadata |
| **Exports** | Configuration exports from admin portals | Machine-readable configuration state | JSON/CSV/XML |
| **Logs** | Audit logs and activity records | Activity verification and investigation | Log files/KQL exports |
| **Reports** | System-generated compliance reports | Aggregate compliance status | PDF/Excel |
| **Attestations** | Signed acknowledgments of control state | Human verification of automated controls | Signed PDF/digital signature |
| **Test Results** | Validation and testing outputs | Verification that controls function | Structured test reports |
| **Policies** | Documented policies and procedures | Governance framework documentation | Approved documents |

### Evidence Quality Requirements

| Requirement | Standard | Rationale |
|-------------|----------|-----------|
| **Timestamp** | All evidence must include capture timestamp | Point-in-time verification |
| **Source** | Document the source portal/system | Authenticity verification |
| **Operator** | Record who captured the evidence | Chain of custody |
| **Context** | Include relevant context (control ID, environment) | Traceability |
| **Integrity** | Store in tamper-evident location | Authenticity assurance |

---

## Evidence by Control Category

### Pillar 1: Security Controls

| Control Area | Primary Evidence | Secondary Evidence | Capture Frequency |
|--------------|-----------------|-------------------|-------------------|
| **Agent Publishing (1.1)** | PPAC screenshots showing publishing restrictions | DLP policy export | Quarterly |
| **Agent Registry (1.2)** | Agent inventory export | Integrated apps screenshots | Monthly |
| **Connector Policies (1.4)** | DLP policy export | Blocked connector test results | Quarterly |
| **DLP/Sensitivity Labels (1.5)** | Label policy export | Sample labeled document screenshots | Quarterly |
| **DSPM for AI (1.6)** | DSPM policy export | Risk assessment report | Quarterly |
| **Audit Logging (1.7)** | Audit policy configuration | Sample audit log export | Quarterly |
| **Runtime Protection (1.8)** | Security policy screenshots | Blocked prompt sample | Monthly |
| **Retention Policies (1.9)** | Retention policy export | Legal hold evidence | Quarterly |
| **Conditional Access (1.11)** | CA policy export | Sign-in log sample | Quarterly |

### Pillar 2: Management Controls

| Control Area | Primary Evidence | Secondary Evidence | Capture Frequency |
|--------------|-----------------|-------------------|-------------------|
| **Managed Environments (2.1)** | Environment list export | ME settings screenshot | Quarterly |
| **Environment Groups (2.2)** | Group configuration export | Environment assignment screenshots | Quarterly |
| **Change Management (2.3)** | Change request sample | Deployment logs | Per change |
| **Model Risk Management (2.6)** | Agent Card export | Validation report | Per validation cycle |
| **Vendor Risk (2.7)** | Vendor assessment questionnaire | Contract excerpts | Per vendor review |
| **Supervision (2.12)** | Supervision log sample | Dashboard screenshot | Monthly |
| **Bias Testing (2.11)** | Bias test results | Test methodology documentation | Per test cycle |
| **Training Program (2.14)** | Training completion report | Course materials | Quarterly |

### Pillar 3: Reporting Controls

| Control Area | Primary Evidence | Secondary Evidence | Capture Frequency |
|--------------|-----------------|-------------------|-------------------|
| **Agent Inventory (3.1)** | Full inventory export | Metadata completeness report | Monthly |
| **Usage Analytics (3.2)** | Usage report export | Trend analysis | Monthly |
| **Compliance Reporting (3.3)** | Compliance dashboard export | Exception report | Quarterly |
| **Incident Reporting (3.4)** | Incident log export | RCA documentation sample | Per incident |
| **Cost Tracking (3.5)** | Cost allocation report | Budget variance analysis | Monthly |
| **Copilot Hub (3.8)** | Hub dashboard screenshot | Configuration export | Quarterly |

### Pillar 4: SharePoint Controls

| Control Area | Primary Evidence | Secondary Evidence | Capture Frequency |
|--------------|-----------------|-------------------|-------------------|
| **IAG/RCD (4.1)** | RCD configuration export | Site exclusion list | Quarterly |
| **Access Reviews (4.2)** | Access review completion report | Review decision sample | Per review cycle |
| **Retention Management (4.3)** | Retention policy assignment | Legal hold list | Quarterly |
| **External Access (4.4)** | Sharing settings export | Guest user inventory | Quarterly |
| **M365 Copilot Governance (4.7)** | Copilot settings screenshot | Plugin inventory | Quarterly |

---

## Evidence Capture Procedures

### Screenshot Standards

```markdown
# Screenshot Evidence Capture Standard

## File Naming Convention
[ControlID]-[EvidenceType]-[Environment]-[YYYYMMDD]-[Sequence].png

Example: 1.5-DLPPolicy-Prod-20260115-001.png

## Required Elements in Screenshot
1. Browser URL bar (showing portal URL)
2. Logged-in user indicator
3. Timestamp (if displayed in portal)
4. Complete configuration visible (scroll if needed)

## Annotation Requirements
- Highlight key configuration elements
- Add callout boxes for critical settings
- Include legend if using color coding

## Metadata File (companion .json)
{
  "controlId": "1.5",
  "evidenceType": "screenshot",
  "captureDate": "2026-01-15T10:30:00Z",
  "capturedBy": "john.smith@company.com",
  "environment": "production",
  "portal": "purview.microsoft.com",
  "description": "DLP policy configuration for AI agent data protection"
}
```

### Export Standards

```markdown
# Configuration Export Standard

## File Naming Convention
[ControlID]-[ExportType]-[Environment]-[YYYYMMDD].json

Example: 2.1-ManagedEnvironments-Prod-20260115.json

## Export Validation
Before storing export evidence:
1. Verify export is complete (not truncated)
2. Validate JSON/XML is well-formed
3. Confirm sensitive data is appropriately redacted
4. Check export includes metadata (timestamps, versions)

## Redaction Requirements
Redact before storing:
- User passwords or secrets
- API keys or tokens
- Personal identifiable information (if not required)
- Specific customer names (if not relevant)

Do NOT redact:
- Configuration settings
- Policy names and descriptions
- User identities (for accountability)
- Timestamps and version information
```

### Log Evidence Standards

```markdown
# Audit Log Evidence Standard

## Query Documentation
For each log evidence capture, document:
1. KQL/query used to extract logs
2. Time range covered
3. Filters applied
4. Expected vs. actual record count

## Log Export Format
{
  "query": "[KQL query used]",
  "timeRange": {
    "start": "2026-01-01T00:00:00Z",
    "end": "2026-01-15T23:59:59Z"
  },
  "recordCount": 1234,
  "exportedBy": "analyst@company.com",
  "exportDate": "2026-01-16T09:00:00Z",
  "purpose": "Quarterly audit logging verification for Control 1.7"
}

## Sampling Guidelines
For large log volumes, document sampling methodology:
- Random sample: X% of records
- Time-based sample: First week of quarter
- Event-based sample: All error events + 10% success
```

---

## Evidence Retention Requirements

### Retention by Zone

| Zone | Minimum Retention | Storage Type | Access Control |
|------|------------------|--------------|----------------|
| **Zone 1** | 1 year | Standard SharePoint | Team access |
| **Zone 2** | 3 years | Compliance SharePoint | Governance team |
| **Zone 3** | 7 years | Immutable storage (WORM) | Compliance + Legal |

### Retention by Evidence Type

| Evidence Type | Minimum Retention | Rationale |
|---------------|------------------|-----------|
| **Configuration snapshots** | 7 years | SEC 17a-4, FINRA 4511 |
| **Audit logs** | 7 years | Regulatory recordkeeping |
| **Validation reports** | 7 years | Model risk management |
| **Incident documentation** | 7 years | Litigation support |
| **Training records** | Duration of employment + 3 years | FINRA requirements |
| **Vendor assessments** | Duration of relationship + 6 years | Third-party risk management |
| **Change records** | 7 years | SOX 404 |

### Regulatory Alignment

| Regulation | Retention Requirement | Evidence Application |
|------------|----------------------|---------------------|
| **SEC 17a-4** | 6 years | Agent interaction records, configuration |
| **FINRA 4511** | 6 years | Supervision records, compliance evidence |
| **SOX 404** | 7 years | Control testing, change documentation |
| **OCC 2011-12** | Duration of model use + 3 years | Model validation, performance monitoring |
| **GLBA 501(b)** | Duration of customer relationship + 6 years | Security control evidence |

---

## Evidence Organization

### Folder Structure

```
evidence/
├── quarterly/
│   └── YYYY-QX/
│       ├── pillar-1-security/
│       │   ├── 1.1-agent-publishing/
│       │   ├── 1.5-dlp-sensitivity/
│       │   └── ...
│       ├── pillar-2-management/
│       ├── pillar-3-reporting/
│       ├── pillar-4-sharepoint/
│       └── summary-report.pdf
├── incidents/
│   └── INC-YYYY-XXXX/
│       ├── timeline.md
│       ├── evidence/
│       └── rca-report.pdf
├── validations/
│   └── agent-validation-YYYY-MM/
│       ├── agent-cards/
│       ├── test-results/
│       └── validation-report.pdf
└── regulatory-exams/
    └── EXAM-YYYY-XXXX/
        ├── request-list.xlsx
        ├── evidence-package/
        └── response-tracker.xlsx
```

### Evidence Package Assembly

For regulatory examinations or audits, assemble evidence packages:

```markdown
# Evidence Package Assembly Checklist

## Package Information
- **Purpose:** [Examination/Audit/Internal Review]
- **Requestor:** [Name/Organization]
- **Due Date:** [Date]
- **Assembler:** [Name]
- **Review Date:** [Date]

## Pre-Assembly Verification
- [ ] Request list reviewed and understood
- [ ] Evidence scope identified (controls, timeframe)
- [ ] Evidence availability confirmed
- [ ] Sensitive data review completed

## Evidence Gathering
For each requested item:
- [ ] Evidence located in repository
- [ ] Evidence validity confirmed (within timeframe)
- [ ] Evidence quality verified (complete, readable)
- [ ] Redaction applied if required
- [ ] Metadata file included

## Package Validation
- [ ] All requested items included
- [ ] Index/table of contents created
- [ ] Cross-reference to request items documented
- [ ] Quality review completed
- [ ] Legal/Compliance review (if required)

## Package Delivery
- [ ] Secure delivery method used
- [ ] Delivery confirmed
- [ ] Delivery logged in tracking system

## Post-Delivery
- [ ] Follow-up questions addressed
- [ ] Supplemental evidence provided (if requested)
- [ ] Lessons learned documented
```

---

## Evidence Templates

### Control Implementation Evidence Template

```markdown
# Control Implementation Evidence

## Control Information
- **Control ID:** [X.X]
- **Control Name:** [Name]
- **Implementation Date:** [Date]
- **Evidence Capture Date:** [Date]
- **Captured By:** [Name]

## Environment
- **Environment Name:** [Name]
- **Environment Type:** [Production/Test/Development]
- **Zone:** [1/2/3]

## Configuration Evidence
- **Primary Evidence:** [Filename and location]
- **Secondary Evidence:** [Filename and location]
- **Screenshot(s):** [Filename(s)]

## Configuration Summary
[Narrative description of configured state]

## Verification
- **Testing Performed:** [Yes/No]
- **Test Results:** [Pass/Fail/N/A]
- **Test Evidence:** [Filename and location]

## Attestation
I attest that this evidence accurately represents the configuration state of Control [X.X] as of [Date].

**Name:** _________________ **Date:** _________
**Role:** _________________
```

### Quarterly Evidence Review Template

```markdown
# Quarterly Evidence Review

## Review Period: Q[X] [YYYY]
## Reviewer: [Name]
## Review Date: [Date]

## Evidence Completeness
| Pillar | Controls | Evidence Complete | Evidence Missing | Action Required |
|--------|----------|-------------------|------------------|-----------------|
| Pillar 1 | [#] | [#] | [List] | [Actions] |
| Pillar 2 | [#] | [#] | [List] | [Actions] |
| Pillar 3 | [#] | [#] | [List] | [Actions] |
| Pillar 4 | [#] | [#] | [List] | [Actions] |

## Evidence Quality Issues
| Control | Issue | Remediation | Due Date |
|---------|-------|-------------|----------|
| [X.X] | [Description] | [Action] | [Date] |

## Expiring Evidence
| Control | Evidence Type | Expiration | Renewal Action |
|---------|--------------|------------|----------------|
| [X.X] | [Type] | [Date] | [Action] |

## Recommendations
[Recommendations for improving evidence practices]

## Sign-Off
Reviewer: _________________ Date: _________
Compliance: _________________ Date: _________
```

---

## Related Documents

| Document | Relationship |
|----------|-------------|
| [Control 1.7 - Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Primary source of log evidence |
| [Control 2.13 - Documentation and Record Keeping](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation standards |
| [Control 3.3 - Compliance Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance evidence aggregation |
| [Evidence Pack Assembly](../playbooks/compliance-and-audit/evidence-pack-assembly.md) | Detailed assembly procedures |

---

## Support & Questions

For questions about evidence standards:

- **AI Governance Lead:** Evidence strategy and requirements
- **Compliance Officer:** Regulatory evidence requirements
- **Legal:** Litigation hold and preservation
- **Internal Audit:** Audit evidence expectations

---

**Updated:** Jan 2026
**Version:** v1.2 (Jan 2026)
