# Remediation Tracking

Procedures for tracking and resolving governance findings and issues.

---

## Overview

This playbook provides a structured approach to tracking remediation of governance findings, audit issues, and control gaps from initial identification through closure.

---

## Remediation Workflow

### 1. Issue Identification

| Source | Examples |
|--------|----------|
| Health checks | Control testing failures |
| Incidents | Security events, policy violations |
| Audits | Internal or external audit findings |
| Examinations | Regulatory examination findings |
| Self-assessments | Gap analysis discoveries |

### 2. Issue Classification

#### Severity Levels

| Severity | Definition | SLA |
|----------|------------|-----|
| **Critical** | Active security breach, regulatory violation, production impact | 24 hours |
| **High** | Control failure with potential for significant impact | 7 days |
| **Medium** | Control weakness requiring attention | 30 days |
| **Low** | Minor improvement opportunity | 90 days |

#### Issue Categories

- Security — Access control, data protection, threat detection
- Compliance — Regulatory requirements, policy violations
- Operational — Process gaps, documentation issues
- Technical — System configuration, integration issues

### 3. Remediation Planning

For each issue:

1. Assign remediation owner
2. Define specific remediation actions
3. Set target completion date
4. Identify dependencies
5. Estimate resources required

### 4. Execution and Tracking

- Regular status updates (weekly for Critical/High)
- Escalation for blocked items
- Documentation of actions taken

### 5. Verification and Closure

- Evidence of remediation
- Testing to confirm resolution
- Sign-off from appropriate authority
- Update tracking system

---

## Remediation Record Template

```
REMEDIATION RECORD
Issue ID: [Unique ID]
Status: [Open/In Progress/Pending Verification/Closed]

ISSUE DETAILS
Title: [Brief description]
Source: [Health check/Incident/Audit/Examination/Self-assessment]
Identified Date: [Date]
Identified By: [Name]
Severity: [Critical/High/Medium/Low]
Category: [Security/Compliance/Operational/Technical]

DESCRIPTION
[Detailed description of the issue, including what was found and the potential impact]

AFFECTED CONTROLS
- Control [ID]: [Name]
- Control [ID]: [Name]

ROOT CAUSE
[Analysis of why this issue occurred]

REMEDIATION PLAN
Action 1: [Description]
  Owner: [Name]
  Due Date: [Date]
  Status: [Not Started/In Progress/Complete]

Action 2: [Description]
  Owner: [Name]
  Due Date: [Date]
  Status: [Not Started/In Progress/Complete]

DEPENDENCIES
[List any dependencies on other teams, systems, or issues]

PROGRESS NOTES
[Date]: [Update]
[Date]: [Update]

VERIFICATION
Verification Method: [How will we confirm this is fixed?]
Verified By: [Name]
Verification Date: [Date]
Evidence: [Description or link to evidence]

CLOSURE
Closed By: [Name]
Closure Date: [Date]
Closure Notes: [Any final notes]
```

---

## Tracking Dashboard

### Status Categories

| Status | Definition |
|--------|------------|
| **Open** | Issue identified, remediation not started |
| **In Progress** | Remediation actively underway |
| **Pending Verification** | Remediation complete, awaiting verification |
| **Closed** | Issue resolved and verified |
| **Deferred** | Remediation postponed (requires approval) |

### Dashboard Metrics

Track these metrics for governance reporting:

| Metric | Target |
|--------|--------|
| Critical issues open >24 hours | 0 |
| High issues open >7 days | 0 |
| Average days to remediation (by severity) | Within SLA |
| Issues reopened | <5% |
| Overdue issues | 0 |

---

## Escalation Procedures

### Escalation Triggers

| Condition | Escalate To |
|-----------|-------------|
| Critical issue identified | CISO + Compliance Officer immediately |
| Issue past SLA | AI Governance Lead |
| Remediation blocked | AI Governance Lead |
| Resource conflict | Department heads |
| Regulatory implications | Legal + Compliance |

### Escalation Path

1. **Level 1:** Remediation Owner
2. **Level 2:** AI Governance Lead
3. **Level 3:** Governance Committee
4. **Level 4:** Executive Leadership

---

## Reporting

### Weekly Status Report

For Critical and High issues:

- New issues identified
- Issues closed
- Issues at risk of missing SLA
- Blocked issues requiring escalation

### Monthly Summary Report

For all issues:

- Total open by severity
- Aging analysis
- Trend analysis
- Top remediation owners
- Overdue issues

### Quarterly Board Report

- Summary of significant findings
- Remediation completion rate
- Risk trend analysis
- Resource requirements

---

## Special Procedures

### Regulatory Examination Findings

1. Track separately from operational issues
2. Assign senior owner (typically Compliance Officer)
3. Coordinate response with Legal
4. Report progress to governance committee
5. Document all communications with examiners

### Recurring Issues

When the same issue recurs:

1. Conduct root cause analysis
2. Identify systemic causes
3. Develop preventive controls
4. Track recurrence rate
5. Report to governance committee

### Deferral Requests

To defer remediation:

1. Document business justification
2. Assess risk of delay
3. Define compensating controls
4. Obtain approval:
   - Medium/Low: AI Governance Lead
   - High: Compliance Officer
   - Critical: Governance Committee
5. Set review date for deferred item

---

## Integration with Other Processes

| Process | Integration |
|---------|-------------|
| Incident Management | Issues created from incidents flow into remediation |
| Change Management | Remediation requiring changes follows change process |
| Risk Assessment | Remediation informs risk reassessment |
| Audit | Audit findings tracked through remediation |
| Governance Review | Remediation status reported to committee |

---

## Related Playbooks

- [AI Incident Response Playbook](ai-incident-response-playbook.md)
- [AI Risk Assessment Template](ai-risk-assessment-template.md)
- [Health Check Procedures](../monitoring-and-validation/health-check-procedures.md)

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.1*
