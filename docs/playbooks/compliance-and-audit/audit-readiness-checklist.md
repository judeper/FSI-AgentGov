# Audit Readiness Checklist

Pre-examination preparation checklist for regulatory examinations.

---

## Overview

Use this checklist to prepare for FINRA, SEC, OCC, or internal audit examinations of AI agent governance. Complete all applicable items before scheduled examinations.

---

## Pre-Examination Timeline

| Timeframe | Activities |
|-----------|------------|
| **30 days before** | Confirm scope, assign response team, inventory documentation |
| **14 days before** | Compile evidence packs, verify access to systems |
| **7 days before** | Final documentation review, brief stakeholders |
| **Day of** | Ensure key personnel available, prepare demonstration environments |

---

## Documentation Checklist

### Governance Framework Documentation

- [ ] Current governance framework version documented
- [ ] Governance committee charter on file
- [ ] Committee meeting minutes available (past 12 months)
- [ ] Roles and responsibilities documented (RACI matrix)
- [ ] Zone classification criteria documented

### Agent Inventory

- [ ] Complete agent inventory current (Control 3.1)
- [ ] All agents classified by zone
- [ ] Agent owners identified and current
- [ ] Business justification on file for each Zone 2-3 agent
- [ ] Approval records available for Zone 2-3 agents

### Policy Documentation

- [ ] DLP policies documented (Control 1.5)
- [ ] Environment group configurations documented
- [ ] Sharing and channel rules documented
- [ ] Change management procedures documented (Control 2.3)
- [ ] Incident response procedures documented

---

## Technical Evidence Checklist

### Audit Logs

- [ ] Audit log retention verified (Control 1.7)
  - [ ] Zone 2: 1-year retention confirmed
  - [ ] Zone 3: 10-year retention confirmed
- [ ] Sample audit log exports tested
- [ ] eDiscovery search capability verified (Control 1.19)
- [ ] Audit log export procedures documented

### Access Controls

- [ ] Admin role assignments documented (Control 1.18)
- [ ] Segregation of duties verified (Control 2.8)
- [ ] Conditional Access policies documented (Control 1.11)
- [ ] Access review records available (Control 4.2)

### Security Controls

- [ ] DLP policy effectiveness report available
- [ ] Runtime protection status documented (Control 1.8)
- [ ] Encryption configuration documented (Control 1.15)
- [ ] MFA configuration documented (Control 1.11)

---

## Operational Evidence Checklist

### Change Management

- [ ] Change request records available (past 12 months)
- [ ] Deployment pipeline logs available
- [ ] Rollback incidents documented
- [ ] Change approval records available

### Testing and Validation

- [ ] Test plans and results on file (Control 2.5)
- [ ] Bias testing results documented (Control 2.11)
- [ ] Security testing results documented
- [ ] Model validation records (Control 2.6)

### Monitoring and Reporting

- [ ] Usage analytics reports available (Control 3.2)
- [ ] Compliance reports generated (Control 3.3)
- [ ] PPAC security posture assessments (Control 3.7)
- [ ] Incident reports on file (Control 3.4)

---

## Personnel Preparation

### Key Personnel Availability

- [ ] AI Governance Lead available during examination
- [ ] Compliance Officer available
- [ ] Power Platform Admin available for technical questions
- [ ] CISO available for security questions
- [ ] Legal counsel on standby

### Personnel Briefing

- [ ] Examination scope communicated to response team
- [ ] Roles during examination assigned
- [ ] Single point of contact designated
- [ ] Escalation procedures reviewed

---

## System Access Preparation

### Demo Environment

- [ ] Representative agent available for demonstration
- [ ] Test accounts configured for examiner use (if needed)
- [ ] Demo data sanitized of actual customer information
- [ ] Network access arranged (guest Wi-Fi, etc.)

### Admin Portal Access

- [ ] PPAC access verified for demonstration
- [ ] Purview Compliance access verified
- [ ] Microsoft Entra admin access verified
- [ ] SharePoint admin access verified

---

## Common Examiner Requests

Prepare responses for these frequently requested items:

| Request | Source | Preparation |
|---------|--------|-------------|
| List of all AI agents | Control 3.1 | Export agent inventory |
| Agent approval records | Governance minutes | Compile approval documentation |
| Audit logs for specific period | Control 1.7 | Test Purview Audit export |
| Supervisory procedures | Control 2.12 | Prepare written procedures |
| Incident history | Control 3.4 | Compile incident reports |
| Training records | Control 2.14 | Export training completion data |
| DLP policy documentation | Control 1.5 | Document current policies |
| Model validation evidence | Control 2.6 | Compile validation reports |

---

## Post-Examination Follow-up

- [ ] Document all examiner requests and responses
- [ ] Track open items and deadlines
- [ ] Assign remediation owners
- [ ] Schedule follow-up meetings as needed
- [ ] Update governance procedures based on findings

---

## Related Playbooks

- [Evidence Pack Assembly](evidence-pack-assembly.md)
- [Examination Response Guide](examination-response-guide.md)

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.1*
