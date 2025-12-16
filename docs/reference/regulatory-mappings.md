# Regulatory Mappings

Complete mapping of framework controls to regulatory requirements.

---

## FINRA Rule 4511 - Books and Records

### Overview
Requires firms to maintain records of all agent activities and communications.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| 1.7 | Comprehensive Audit Logging | 6-year retention + 1 year accessible |
| 1.9 | Data Retention and Deletion | Retention policies per FINRA timeline |
| 2.9 | Agent Performance Monitoring | Track all agent activity |
| 2.12 | Supervision and Oversight | Compliance Officer oversight |
| 3.1 | Agent Inventory | Central registry of all agents |
| 3.3 | Compliance and Regulatory Reporting | Regular compliance reports |
| 3.4 | Incident Reporting | Document all incidents |

### Governance Framework Alignment

**Zone 2 Requirements:**
- Maintain 1-year audit logs
- Document approval process
- Monthly compliance reviews
- Supervisory controls per Rule 3110

**Zone 3 Requirements:**
- Maintain 6-year + 1 year accessible audit logs
- Comprehensive real-time monitoring
- Immediate incident escalation
- Weekly executive reporting

### Framework Coverage
Framework provides 100% control coverage (43/48 controls). Implementation and validation required for compliance.

---

## FINRA Rule 3110 - Supervision

### Overview
Requires written policies and procedures for supervision of agents and AI technologies.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| 2.12 | Supervision and Oversight | Define supervisory procedures |
| 2.3 | Change Management | Change control and approval |
| 2.5 | Testing and Validation | QA before production |
| 2.6 | Model Risk Management | SR 11-7 alignment |
| 2.11 | Bias Testing | Fairness assessment |
| 3.3 | Compliance Reporting | Supervision documentation |

### Key Requirements

1. **Written Procedures**
   - Documented approval workflow
   - Agent classification procedures
   - Escalation procedures
   - Incident response procedures

2. **Supervisory Controls**
   - Compliance Officer oversight for Zone 2+
   - Real-time monitoring for Zone 3
   - Quarterly compliance reviews
   - Annual testing of controls

3. **Qualified Supervisor**
   - Compliance Officer oversight mandatory
   - AI Governance Lead coordination
   - Escalation to COO/Board if needed

### Governance Framework Alignment

**Zone 1:** No supervision required

**Zone 2:** 
- Basic supervisory procedures
- Quarterly compliance reviews
- Annual testing

**Zone 3:**
- Comprehensive supervision
- Real-time monitoring
- Mandatory incident escalation
- Monthly compliance certification

### Framework Coverage
Framework provides supervision procedure guidance (6/48 controls). Implementation required.

---

## FINRA Regulatory Notice 25-07 - AI Governance

### Overview
Discusses model risk management considerations for AI and algorithmic systems. Topics include validation, monitoring, bias, and governance.

### Applicable Controls

| Control | Topic | Mapping |
|---------|-------|---------|
| 2.6 | Model Risk Management | Formal framework per SR 11-7 |
| 2.11 | Bias Testing | Quarterly fairness assessment |
| 1.8 | Runtime Protection | Ongoing monitoring and alerting |
| 1.6 | DSPM for AI | Data handling governance |
| 2.12 | Supervision | Governance procedures |
| 3.2 | Usage Analytics | Performance monitoring |

### Key Topics

1. **Model Validation**
   - Independent testing required
   - Performance baseline established
   - Bias testing documented
   - Results retained for audit

2. **Ongoing Monitoring**
   - Performance vs. baseline tracked
   - Anomalies detected and investigated
   - Monthly monitoring reports
   - Executive escalation procedures

3. **Model Governance**
   - Governance committee oversight
   - Change control procedures
   - Incident response procedures
   - Annual validation recommended

### Governance Framework Alignment

The framework treats agents as models requiring comprehensive governance per SR 11-7 principles.

### Framework Coverage
Framework addresses Notice 25-07 topics (6/48 controls). Implementation and validation required.

---

## SEC Rule 17a-3/4 - Recordkeeping

### Overview
Requires SEC-registered firms to maintain records of all transactions and communications for 6 years + 3 years accessible.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| 1.7 | Comprehensive Audit Logging | 6-year + 3-year accessible retention |
| 1.9 | Data Retention | Retention policies enforced |
| 2.13 | Documentation and Record Keeping | All records documented |
| 3.1 | Agent Inventory | Registry of agents as records |
| 3.3 | Compliance Reporting | Evidence retention |

### Record Categories

**Agent Communications:**
- All user interactions with agents
- All agent outputs and decisions
- All approvals and rejections
- Retention: 6 years + 3 years accessible

**Transaction Records:**
- If agent processes transactions
- If agent provides investment advice
- If agent executes trades
- Retention: 6 years + 3 years accessible

**Governance Records:**
- Agent approvals
- Change logs
- Incident reports
- Model validation results
- Retention: 6 years minimum

### Governance Framework Alignment

**Zone 2:**
- 1-year retention minimum
- Audit logs searchable
- Weekly export recommended

**Zone 3:**
- 6-year + 3-year accessible
- Immutable storage mandatory
- Real-time audit trail
- Weekly compliance verification

### Framework Coverage
Framework provides 88% control coverage (38/48 controls). Remaining gaps require supplemental controls. Implementation required.

---

## SEC Rule 10b-5 / Reg BI - Fair Dealing and Disclosure

### Overview
Requires fair dealing in transactions and investment advice, including disclosure of conflicts and algorithmic use.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| 2.6 | Model Risk Management | Agent accuracy and reliability |
| 2.11 | Bias Testing | Fair treatment across demographics |
| 1.14 | Data Minimization | Use only necessary data |
| 1.6 | DSPM for AI | Data governance and privacy |

### Key Requirements

1. **Algorithmic Disclosure**
   - Inform customers if using AI agent
   - Explain agent decision factors
   - Disclose material conflicts
   - Provide override/escalation procedure

2. **Fair Dealing**
   - Agent must treat all customers fairly
   - No discrimination (ECOA compliance)
   - Bias testing documented
   - Model monitoring for fair outcomes

3. **Best Execution**
   - Agent must seek best outcomes
   - Performance monitoring required
   - Escalation to human advisor available
   - Regular review of effectiveness

### Governance Framework Alignment

**Zone 3 Customer-Facing Agents:**
- Mandatory bias testing (quarterly)
- Fair treatment confirmed
- Escalation procedures documented
- Customer disclosure completed

### Framework Coverage
Framework incorporates SEC AI disclosure guidance (4/48 controls). Legal review recommended. Implementation required.

---

## SOX Section 302/404 - Internal Controls

### Overview
Requires CEO/CFO certification of internal control effectiveness and management assessment.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| 2.5 | Testing and Validation | Control testing documented |
| 2.12 | Supervision | Control procedures documented |
| 2.13 | Documentation | Evidence for control effectiveness |
| 2.10 | Patch Management | Security control maintenance |
| 3.3 | Compliance Reporting | Control effectiveness reports |
| 2.8 | Access Control | Segregation of duties enforced |

### Management Assessment Requirements

1. **Control Design**
   - Controls documented and approved
   - Risk areas identified
   - Control procedures defined
   - Responsibility assigned

2. **Control Testing**
   - Annual testing of all controls
   - Test results documented
   - Deficiencies identified and remediated
   - Testing evidence retained

3. **Compliance Reporting**
   - Management certifies control effectiveness
   - Auditor validation of testing
   - Any deficiencies disclosed
   - Remediation plans documented

### Governance Framework Alignment

**Zone 2 Agents:**
- Annual control testing
- Results documented
- Basic compliance reporting

**Zone 3 Agents:**
- Annual control testing + quarterly assessments
- Comprehensive documentation
- Monthly compliance certification
- Executive sign-off on effectiveness

### Framework Coverage
Framework provides 81% control coverage (35/48 controls). SOX-specific testing required. Implementation required.

---

## GLBA Safeguards Rule (501-505)

### Overview
Requires financial institutions to maintain appropriate safeguards for customer information.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| 1.11 | Conditional Access and MFA | Strong authentication |
| 1.15 | Encryption | Data protection in transit and at rest |
| 1.5 | DLP and Sensitivity Labels | Data loss prevention |
| 1.16 | Information Rights Management | Document-level protection |
| 1.18 | RBAC | Access control |
| 1.3 | SharePoint Governance | Permission management |

### Key Safeguard Areas

1. **Administrative Safeguards**
   - Information security program (documented)
   - Qualified individual oversight (CISO)
   - Training program (annual mandatory)
   - Incident response procedures

2. **Technical Safeguards**
   - Access controls (RBAC, MFA)
   - Encryption (in transit and at rest)
   - Audit logging (6+ years)
   - Monitoring and detection

3. **Physical Safeguards**
   - Physical access controls
   - Device management
   - Secure disposal procedures

### Governance Framework Alignment

**Zone 2 Agents Accessing Customer Data:**
- MFA required
- Encryption in transit
- DLP policies
- Annual training

**Zone 3 Agents:**
- Phishing-resistant MFA
- Encryption in transit and at rest
- Strictest DLP
- Customer-managed keys (recommended)
- Quarterly training + annual assessment

### Framework Coverage
Framework provides 93% control coverage (40/48 controls). Implementation validation required.

---

## OCC Bulletin 2011-12 / SR 11-7 - Model Risk Management

### Overview
Applies to national banks and federal savings associations. Requires governance framework for models used in business decisions.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| 2.6 | Model Risk Management | Formal SR 11-7 framework |
| 2.11 | Bias Testing | Fairness and discrimination testing |
| 2.5 | Testing and Validation | Independent validation |
| 3.2 | Performance Monitoring | Ongoing performance tracking |
| 2.12 | Supervision | Governance committee oversight |

### Model Risk Framework (SR 11-7)

1. **Model Development**
   - Clear model purpose defined
   - Appropriate data sources
   - Documented assumptions
   - Validation testing completed

2. **Model Validation**
   - Independent validation required
   - Testing covers all use cases
   - Performance benchmarks established
   - Bias testing (fairness assessment)

3. **Model Monitoring**
   - Performance vs. baseline tracked
   - Drift detection and alerting
   - Quarterly monitoring reports
   - Annual validation recommended

4. **Model Governance**
   - Clear roles and responsibilities
   - Documented approval process
   - Change control procedures
   - Incident response procedures

### Governance Framework Alignment

**Agent Classification as Model:**
- Agents using ML/statistical algorithms = Model
- Requires SR 11-7 governance framework
- Annual third-party validation recommended
- Quarterly monitoring mandatory

### Applicability

**OCC Regulated Entities (National Banks, FSAs):**
- All Zone 3 agents using ML = Model
- SR 11-7 framework required
- Annual validation mandatory

**Non-OCC Entities:**
- SR 11-7 represents best practice
- Apply for Zone 3 high-risk agents
- Recommended even if not OCC-regulated

### Framework Coverage
Framework provides 58% control coverage (25/48 controls). OCC-specific model validation required for full compliance.

---

## Federal Reserve Guidance - Fair Lending (ECOA)

### Overview
Applies to bank holding companies and entities with lending functions. Requires fair lending practices in credit decisions.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| 2.11 | Bias Testing | ECOA discrimination testing |
| 2.6 | Model Risk Management | Credit model governance |
| 1.14 | Data Minimization | Fair treatment in data usage |
| 2.12 | Supervision | Compliance oversight |

### Fair Lending Requirements

1. **Non-Discrimination**
   - Agent must not discriminate based on protected class
   - Protected classes: Race, color, religion, national origin, sex, marital status, age, disability status, receipt of public assistance

2. **Disparate Impact Testing**
   - Regular testing for unintentional discrimination
   - Quarterly monitoring for credit agents
   - Results documented and retained

3. **Corrective Action**
   - If bias detected, investigate and remediate
   - Document remediation steps
   - Retest after changes
   - Board notification if material

### Governance Framework Alignment

**Credit/Lending Agents (Zone 3):**
- Mandatory bias testing (quarterly)
- ECOA protected classes tested
- Results documented and retained
- Remediation if issues detected
- Annual third-party validation

### Framework Coverage
Framework provides bias testing controls (2/48 controls applicable). ECOA-specific testing and validation required.

---

## CFPB Guidance - Algorithmic Accountability

### Overview
Applies to consumer financial service providers. Focuses on algorithmic accountability, bias, and consumer protection.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| 2.11 | Bias Testing | Algorithmic bias assessment |
| 1.6 | DSPM for AI | Consumer data protection |
| 1.8 | Runtime Protection | Anomaly detection |
| 2.12 | Supervision | Algorithmic governance |

### Consumer Protection Focus

1. **Transparency**
   - Disclose algorithmic decision-making to consumers
   - Explain key factors in decisions
   - Provide escalation to human review

2. **Bias and Fairness**
   - Regular bias testing
   - Results documented and retained
   - Disparate impact monitoring
   - Corrective action procedures

3. **Accountability**
   - Clear governance and oversight
   - Incident response procedures
   - Regular audits and testing
   - Board reporting on algorithms

### Governance Framework Alignment

**Consumer-Facing Agents (Zone 3):**
- Mandatory bias testing (quarterly)
- Disclosure to consumers about AI use
- Human escalation available
- Regular audit of fairness outcomes

### Framework Coverage
Framework addresses consumer protection topics (3/48 controls). CFPB-specific implementation required.

---

## Control Coverage Summary by Regulation

| Regulation | Applicable Controls | Coverage | Implementation Status |
|-----------|---------------------|----------|----------------------|
| FINRA 4511 | 48/48 | 100% | Full coverage - implementation required |
| FINRA 3110 | 6/48 | 14% | Partial - supervision focus |
| FINRA Notice 25-07 | 6/48 | 14% | Partial - model risk focus |
| SEC 17a-3/4 | 43/48 | 88% | Substantial coverage |
| SEC Rule 10b-5 / Reg BI | 4/48 | 9% | Limited - fairness focus |
| SOX 302/404 | 40/48 | 81% | Substantial coverage |
| GLBA 501-505 | 45/48 | 93% | Substantial coverage |
| OCC 2011-12 | 30/48 | 58% | Partial - model risk focus |
| Fed SR 11-7 | 30/48 | 58% | Partial - model risk focus |
| Fed ECOA | 2/48 | 5% | Minimal - bias testing only |
| CFPB | 3/48 | 7% | Minimal - consumer focus |

> **Note:** Coverage percentages indicate which framework controls address aspects of each regulation. Actual compliance requires implementation, validation, and ongoing maintenance. Consult legal counsel for regulatory interpretation. See [DISCLAIMER.md](/DISCLAIMER.md).

---

## How to Use This Document

1. **Find your primary regulation** in the list above
2. **Review applicable controls** for your regulation
3. **Check governance zone** alignment (Zone 2 vs Zone 3 requirements)
4. **Reference individual control files** for detailed implementation
5. **Document compliance evidence** for audit purposes

---

*FSI Agent Governance Framework Beta - December 2025*
