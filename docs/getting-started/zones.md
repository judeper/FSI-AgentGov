# Governance Zones: Complete Overview

## Three-Zone Governance Model

The framework uses three governance zones to balance innovation with compliance. Agents progress from development (Zone 1) through team collaboration (Zone 2) to enterprise production (Zone 3).

---

## Zone 1: Personal Productivity

### Profile
- **Risk Level:** Low
- **Scope:** Individual developers
- **Typical Users:** Single user or small team
- **Data Access:** Microsoft Graph only
- **Regulatory Scrutiny:** Minimal

### Characteristics
- Development and learning environment
- Isolated from organizational controls
- Quick prototyping and experimentation
- No production customer data
- Self-service deployment

### Governance Model
- **Approval:** Self-service (no approval needed)
- **Publishing:** Self-published by creator
- **Data:** Personal data only
- **Retention:** 30 days (default)
- **Audit:** Basic logging only
- **Access Reviews:** Annual (if any)

### Typical Agents
- Personal productivity bot
- Learning/development agent
- Proof-of-concept demonstration
- Personal research assistant

### Technology Stack
- Managed Environments: Not required
- DLP: Baseline only
- Audit: 30-day retention acceptable
- Connectors: Restricted connectors allowed
- MFA: Basic (standard M365 login)

### Regulatory Status
**Zone 1 is NOT subject to FINRA, SEC, or GLBA examination.**

- No books and records requirements
- No formal supervision required
- No model risk management needed
- Sandbox environment for innovation

### Compliance Requirements
- Document agent purpose
- Maintain creator documentation
- Basic audit logging
- No external data sharing

---

## Zone 2: Team Collaboration

### Profile
- **Risk Level:** Medium
- **Scope:** Teams or departments
- **Typical Users:** Team members within department
- **Data Access:** Internal departmental data
- **Regulatory Scrutiny:** Moderate

### Characteristics
- Shared across team/department
- Internal data access
- Collaboration and workflow support
- Medium business impact if fails
- Cross-team dependencies possible

### Governance Model
- **Approval:** Manager/Department Head approval required
- **Publishing:** Central publishing workflow
- **Data:** Departmental data only
- **Retention:** 1 year minimum
- **Audit:** Weekly exports recommended
- **Access Reviews:** Quarterly

### Typical Agents
- HR benefits assistant
- IT help desk support
- Document processing for team
- Compliance training delivery
- Internal knowledge bot

### Technology Stack
- Managed Environments: Recommended
- DLP: Strict policies
- Audit: 1-year retention
- Connectors: Approved connectors only
- MFA: Enforced
- Environment Groups: Recommended

### Regulatory Status
**Zone 2 is subject to MODERATE regulatory oversight:**

- FINRA examiners may request agent list and approval documentation
- SEC reviewers may inquire about data handling
- Supervisory controls per FINRA Rule 3110 required
- Annual testing recommended

### Compliance Requirements
- Formal approval workflow
- Documented business justification
- Data source documentation
- Access controls and permissions
- Monthly compliance reviews
- Training for users

### Implementation Considerations
- Department head signs off on deployment
- Compliance reviews recorded
- Access permissions documented
- Data sources approved
- Incident response procedures

---

## Zone 3: Enterprise Managed

### Profile
- **Risk Level:** High
- **Scope:** Organization-wide or customer-facing
- **Typical Users:** Multiple departments, external customers
- **Data Access:** Sensitive, regulated data
- **Regulatory Scrutiny:** High / Critical

### Characteristics
- Production environment
- Customer-facing or high-value business
- Sensitive or regulated data
- Critical business impact if fails
- Full compliance requirements

### Governance Model
- **Approval:** Governance Committee + Legal review
- **Publishing:** Change control process
- **Data:** All regulated and sensitive data
- **Retention:** 10 years minimum (per SEC 17a-3/4)
- **Audit:** Real-time monitoring
- **Access Reviews:** Monthly with attestation

### Typical Agents
- Client service chatbot
- Compliance monitoring
- Trading/transaction processing
- Document processing for regulated data
- Risk assessment/credit scoring
- Financial reporting assistant

### Technology Stack
- Managed Environments: Mandatory
- DLP: Strictest policies
- Audit: 10-year retention with WORM
- Connectors: Allowlisted only
- MFA: Phishing-resistant (FIDO2/Windows Hello)
- Runtime Protection: Mandatory
- DSPM for AI: Recommended

### Regulatory Considerations
**Zone 3 agents handling regulated data may be subject to comprehensive oversight depending on firm type and use case:**

- FINRA examination (broker-dealers)
- SEC Division of Examinations review (registered entities)
- OCC/Federal Reserve model risk review (national banks, FSAs)
- CFPB oversight (consumer financial services)
- SOX controls testing (public companies)
- Internal audit review (all organizations)

### Compliance Requirements
**MANDATORY Controls:**

1. **Governance Committee Approval**
   - AI Governance Lead
   - Compliance Officer
   - CISO
   - Legal/General Counsel
   - Business Owner

2. **Model Risk Management**
   - Validation testing
   - Bias testing and fairness assessment
   - Performance monitoring vs. baseline
   - Annual third-party validation (recommended)

3. **Data Security**
   - DLP with strictest policies
   - Sensitivity labels mandatory
   - Encryption in transit and at rest
   - Customer-managed keys (recommended)

4. **Audit and Logging**
   - 10-year retention with immutable storage
   - Real-time monitoring and alerting
   - Daily compliance reviews
   - Weekly executive reporting

5. **Change Management**
   - 48-hour change review window
   - Formal change advisory board (CAB)
   - Automated rollback capability
   - Testing in lower tier before promotion

6. **Incident Response**
   - SLA for incident investigation (<4 hours)
   - Root cause analysis required
   - Executive escalation procedures
   - Board notification procedures

### Implementation Considerations
- Formal governance committee established
- Comprehensive risk assessment completed
- Model validation documented
- Security testing completed
- Legal review and sign-off obtained
- Training and awareness program implemented
- Incident response playbooks documented

---

## Zone Progression Model

Agents typically progress through zones as they mature:

```
Zone 1: Personal Development
    ↓ (Proven value, team validation)
Zone 2: Team Collaboration
    ↓ (Org-wide need, full testing, legal review)
Zone 3: Enterprise Production
```

### Promotion Criteria

**Zone 1 → Zone 2:**
- Proof of concept validated
- Manager approval obtained
- Data source identified and approved
- User training completed
- Incident response procedures documented

**Zone 2 → Zone 3:**
- Production readiness testing completed
- Security assessment passed
- Model risk validation completed
- Bias testing results documented
- Governance committee approval obtained
- Legal and compliance sign-off received

### Demotion/Remediation

If an agent violates governance requirements:

- **Zone 3 → Zone 2:** Policy violations, performance issues
- **Zone 2 → Zone 1:** Compliance failures, security incidents
- **Suspension:** Critical security issues (any zone)

Demotion typically requires:
- Root cause analysis
- Remediation plan
- Re-approval before re-promotion

---

## Regulation-Zone Mapping

### FINRA Examination Focus by Zone

| Zone | FINRA Focus | Key Controls | Examination Depth |
|------|-------------|--------------|-------------------|
| Zone 1 | None | N/A | None |
| Zone 2 | Supervisory controls | Rule 3110 | Moderate |
| Zone 3 | Complete oversight | Rules 3110, 4511, Notice 25-07 | Comprehensive |

### SEC Examination Focus by Zone

| Zone | SEC Focus | Key Controls | Examination Depth |
|------|-----------|--------------|-------------------|
| Zone 1 | None | N/A | None |
| Zone 2 | Data handling | Reg S-P | Limited |
| Zone 3 | Complete compliance | Rules 17a-3/4, AI disclosure | Comprehensive |

### SOX Internal Controls by Zone

| Zone | SOX Scope | Documentation | Testing |
|------|-----------|---------------|---------|
| Zone 1 | None | N/A | None |
| Zone 2 | Limited | Process docs | Annual |
| Zone 3 | Full | All controls | Annual + Continuous |

---

## Zone Decision Matrix

### Questions to Determine Zone

| Question | Zone 1 | Zone 2 | Zone 3 |
|----------|--------|--------|--------|
| Who uses the agent? | Individual only | Team/Department | Organization-wide |
| What data accessed? | Microsoft Graph only | Internal data | Regulated/sensitive data |
| Customer-facing? | No | No (internal only) | Yes or customer data |
| Regulatory scrutiny? | Minimal | Moderate | High |
| Business impact if fails? | Low - inconvenience | Medium - workflow disruption | High - financial/reputational |
| Approval required? | Self-service | Manager/Dept Head | Governance Committee |
| Audit retention? | 30 days | 1 year | 10 years |

---

## Implementation Guidance by Zone

### Zone 1 Setup (1-2 days)
1. Enable personal environments
2. Configure basic DLP
3. Document agent purpose
4. Train user on best practices

### Zone 2 Setup (1-2 weeks)
1. Establish approval workflow
2. Configure Managed Environments
3. Implement DLP policies
4. Set up audit logging (1-year)
5. Document compliance procedures
6. Train team members

### Zone 3 Setup (3-6 weeks)
1. Establish governance committee
2. Perform model risk assessment
3. Conduct bias and fairness testing
4. Implement comprehensive DLP
5. Configure 10-year audit retention
6. Deploy runtime protection
7. Establish incident response
8. Obtain legal and compliance sign-off
9. Train governance team and operators

---

## Common Zone Questions

**Q: Can an agent be in multiple zones?**
A: No. Each agent exists in one zone. It may progress to a higher zone as it matures.

**Q: What if an agent crosses zone boundaries?**
A: If a Zone 1 agent needs to access team data, it should be promoted to Zone 2 with appropriate approvals.

**Q: How do we prevent zone bypassing?**
A: Use environment groups, Managed Environments, and DLP policies to enforce zone boundaries technically.

**Q: Can we have Zone 1 agents access Zone 3 data?**
A: No. Zone 1 is restricted to Microsoft Graph. Access to regulated data requires Zone 3.

---

## Quarterly Zone Reviews

Each zone should have recurring compliance reviews:

- **Zone 1:** Annual review (if tracked)
- **Zone 2:** Quarterly compliance review
- **Zone 3:** Monthly review with attestation

---

*FSI Agent Governance Framework Beta - December 2025*
