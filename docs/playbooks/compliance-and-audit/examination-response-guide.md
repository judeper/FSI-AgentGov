# Examination Response Guide

Procedures for responding to regulatory examiner requests during FINRA, SEC, or OCC examinations.

---

## Overview

This guide provides procedures for responding to examiner information requests efficiently and accurately while maintaining appropriate documentation of all interactions.

---

## Response Team Structure

### Core Team

| Role | Responsibility | Backup |
|------|----------------|--------|
| **Response Coordinator** | Single point of contact with examiners | Deputy Compliance Officer |
| **AI Governance Lead** | Technical responses, agent inventory | Senior Platform Admin |
| **Compliance Officer** | Regulatory interpretation, policy responses | Legal Counsel |
| **Power Platform Admin** | System demonstrations, audit log exports | SharePoint Admin |
| **Legal Counsel** | Review responses, privilege issues | Outside Counsel |

### Extended Team (As Needed)

- CISO — Security-related inquiries
- CRO — Model risk and bias inquiries
- Internal Audit — Control testing evidence
- Business Owners — Agent-specific questions

---

## Response Process

### Step 1: Receive Request

1. Log all requests in examination tracking system
2. Assign unique tracking number
3. Note deadline and priority
4. Identify responsible team member

### Step 2: Assess Request

| Assessment | Action |
|------------|--------|
| Routine request | Assign to appropriate owner |
| Sensitive request | Route to Compliance + Legal |
| Unclear scope | Seek clarification from examiner |
| Potentially privileged | Route to Legal immediately |

### Step 3: Gather Response

1. Compile requested documentation
2. Verify accuracy and completeness
3. Remove any privileged or irrelevant information
4. Format consistently (PDF preferred for documents)

### Step 4: Review Response

- [ ] Technical accuracy verified by subject matter expert
- [ ] Compliance Officer reviewed
- [ ] Legal review (if sensitive)
- [ ] Response Coordinator final review

### Step 5: Submit Response

1. Submit through designated channel
2. Log submission date and contents
3. Retain copy of all submitted materials
4. Note any follow-up commitments

---

## Response Standards

### Timeliness

| Priority | Target Response Time |
|----------|---------------------|
| Urgent | Same day |
| Standard | 2-3 business days |
| Complex | 5 business days (negotiate if needed) |

### Quality Standards

- **Accurate:** Verify all facts before submission
- **Complete:** Respond to all parts of the request
- **Organized:** Use clear headings and labels
- **Traceable:** Include document references and dates

### Communication Guidelines

**DO:**

- Be responsive and cooperative
- Provide accurate, complete information
- Ask for clarification if request is unclear
- Document all interactions
- Involve Legal when appropriate

**DON'T:**

- Speculate or guess
- Provide information beyond the request scope
- Make commitments without authority
- Discuss ongoing examination with others
- Destroy or alter any documents

---

## Common Request Types

### Agent Inventory Requests

**Request:** "Provide a list of all AI agents deployed in your organization."

**Response:**

1. Export agent inventory from Control 3.1 process
2. Include: Agent name, ID, zone, owner, deployment date, status
3. Format as Excel or CSV
4. Include inventory date and methodology

### Audit Log Requests

**Request:** "Provide audit logs for [Agent X] for [Date Range]."

**Response:**

1. Access Purview Audit (Control 1.7)
2. Filter by agent and date range
3. Export in requested format
4. Include record count and any limitations

### Policy Documentation Requests

**Request:** "Provide your written supervisory procedures for AI agents."

**Response:**

1. Gather Control 2.12 documentation
2. Include governance framework overview
3. Include zone-specific procedures
4. Include approval workflows

### Incident History Requests

**Request:** "Provide documentation of any AI agent incidents in the past 12 months."

**Response:**

1. Compile Control 3.4 incident reports
2. Include resolution documentation
3. Include root cause analysis
4. Redact customer PII if present

---

## Escalation Procedures

### When to Escalate

| Situation | Escalate To |
|-----------|-------------|
| Request scope unclear | Response Coordinator |
| Request seems overbroad | Legal Counsel |
| Potential privilege issue | Legal Counsel |
| Cannot meet deadline | Compliance Officer |
| Conflicting requests | Response Coordinator |
| Finding of concern | CEO/Board (per policy) |

### Escalation Path

1. **Level 1:** Response Coordinator
2. **Level 2:** Compliance Officer + Legal
3. **Level 3:** CEO/General Counsel
4. **Level 4:** Board (material findings only)

---

## Documentation Requirements

### Request Log Template

```
EXAMINATION REQUEST LOG
Examination ID: [ID]
Request Number: [#]
Date Received: [Date]
Examiner Name: [Name]
Agency: [FINRA/SEC/OCC/Other]

REQUEST DETAILS
Subject: [Brief description]
Full Text: [Copy of request]
Deadline: [Date]
Priority: [Urgent/Standard/Complex]

ASSIGNMENT
Owner: [Name]
Backup: [Name]
Legal Review Required: [Yes/No]

RESPONSE
Response Date: [Date]
Submitted By: [Name]
Documents Provided: [List]
Follow-up Required: [Yes/No]

NOTES
[Any relevant notes or commitments]
```

### Retention Requirements

- Request logs: 7 years minimum
- Submitted responses: 7 years minimum
- Working papers: 7 years minimum
- Examiner correspondence: 7 years minimum

---

## Post-Examination Activities

### Exit Conference

- [ ] Attend scheduled exit conference
- [ ] Document preliminary findings
- [ ] Note any immediate concerns
- [ ] Clarify any misunderstandings
- [ ] Request timeline for written findings

### Findings Response

1. Receive written examination report
2. Review findings with response team
3. Prepare management response
4. Submit response within deadline
5. Track remediation commitments

### Remediation Tracking

- [ ] Log all findings in tracking system
- [ ] Assign remediation owners
- [ ] Set deadlines
- [ ] Monitor progress
- [ ] Report to governance committee
- [ ] Document closure evidence

---

## Related Playbooks

- [Audit Readiness Checklist](audit-readiness-checklist.md)
- [Evidence Pack Assembly](evidence-pack-assembly.md)

---

*Last Updated: January 2026*
*FSI Agent Governance Framework v1.2*
