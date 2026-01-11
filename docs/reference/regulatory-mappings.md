# Regulatory Mappings

Complete mapping of framework controls to regulatory requirements.

---

## FINRA Rule 4511 - Books and Records

### Overview
Requires firms to maintain records of all agent activities and communications.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.7](pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | 6-year retention + 1 year accessible |
| [1.9](pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention and Deletion | Retention policies per FINRA timeline |
| [2.9](pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | Agent Performance Monitoring | Track all agent activity |
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and Oversight | Compliance Officer oversight |
| [3.1](pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Central registry of all agents |
| [3.3](pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance and Regulatory Reporting | Regular compliance reports |
| [3.4](pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Incident Reporting | Document all incidents |

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
The framework provides mapped coverage via the applicable controls listed above. Implementation and validation are required for compliance.

---

## FINRA Rule 3110 - Supervision

### Overview
Requires written policies and procedures for supervision of agents and AI technologies.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and Oversight | Define supervisory procedures |
| [2.3](pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Change control and approval |
| [2.5](pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | QA before production |
| [2.6](pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | SR 11-7 alignment |
| [2.11](pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | Fairness assessment |
| [3.3](pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Supervision documentation |

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
| [2.6](pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | Formal framework per SR 11-7 |
| [2.11](pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | Quarterly fairness assessment |
| [1.8](pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime Protection | Ongoing monitoring and alerting |
| [1.6](pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | Data handling governance |
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Governance procedures |
| [3.2](pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | Performance monitoring |

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
| [1.7](pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | 6-year + 3-year accessible retention |
| [1.9](pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention | Retention policies enforced |
| [2.13](pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation and Record Keeping | All records documented |
| [3.1](pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Registry of agents as records |
| [3.3](pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Evidence retention |

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
The framework provides mapped coverage via the applicable controls listed above. Some requirements may require additional organization-specific controls and procedures. Implementation required.

---

## SEC Rule 10b-5 / Reg BI - Fair Dealing and Disclosure

### Overview
Requires fair dealing in transactions and investment advice, including disclosure of conflicts and algorithmic use.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.6](pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | Agent accuracy and reliability |
| [2.11](pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | Fair treatment across demographics |
| [1.14](pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Data Minimization | Use only necessary data |
| [1.6](pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | Data governance and privacy |

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
| [2.5](pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | Control testing documented |
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Control procedures documented |
| [2.13](pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation | Evidence for control effectiveness |
| [2.10](pillar-2-management/2.10-patch-management-and-system-updates.md) | Patch Management | Security control maintenance |
| [3.3](pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Control effectiveness reports |
| [2.8](pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Access Control | Segregation of duties enforced |

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
Framework provides 81% control coverage (40/48 controls). SOX-specific testing required. Implementation required.

---

## GLBA Safeguards Rule (501-505)

### Overview
Requires financial institutions to maintain appropriate safeguards for customer information.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.11](pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access and MFA | Strong authentication |
| [1.15](pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Encryption | Data protection in transit and at rest |
| [1.5](pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and Sensitivity Labels | Data loss prevention |
| [1.16](pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | Information Rights Management | Document-level protection |
| [1.18](pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | RBAC | Access control |
| [1.3](pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | SharePoint Governance | Permission management |

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
Framework provides 93% control coverage (45/48 controls). Implementation validation required.

---

## OCC Bulletin 2011-12 / SR 11-7 - Model Risk Management

### Overview
Applies to national banks and federal savings associations. Requires governance framework for models used in business decisions.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.6](pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | Formal SR 11-7 framework |
| [2.11](pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | Fairness and discrimination testing |
| [2.5](pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | Independent validation |
| [3.2](pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Performance Monitoring | Ongoing performance tracking |
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Governance committee oversight |

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
Framework provides 58% control coverage (30/48 controls). OCC-specific model validation required for full compliance.

---

## Federal Reserve Guidance - Fair Lending (ECOA)

### Overview
Applies to bank holding companies and entities with lending functions. Requires fair lending practices in credit decisions.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.11](pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | ECOA discrimination testing |
| [2.6](pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | Credit model governance |
| [1.14](pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Data Minimization | Fair treatment in data usage |
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Compliance oversight |

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

## CFPB Guidance - Algorithmic Accountability and UDAAP

### Overview
Applies to consumer financial service providers. Focuses on algorithmic accountability, bias, consumer protection, and avoidance of unfair, deceptive, or abusive acts or practices (UDAAP).

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.11](pillar-2-management/2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md) | Bias Testing | Algorithmic bias assessment |
| [1.6](pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | Consumer data protection |
| [1.8](pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime Protection | Anomaly detection |
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Algorithmic governance |

### UDAAP Considerations for AI Agents

Consumer-facing AI agents must avoid Unfair, Deceptive, or Abusive Acts or Practices (UDAAP):

1. **Unfair Acts or Practices**
   - Agent outputs must not cause substantial injury to consumers
   - Injury must not be reasonably avoidable by consumers
   - Injury must not be outweighed by benefits

2. **Deceptive Acts or Practices**
   - Agent communications must not mislead consumers
   - Material information must be disclosed
   - AI-generated content must be accurate

3. **Abusive Acts or Practices**
   - Agent must not take unreasonable advantage of consumer lack of understanding
   - Must not exploit consumer inability to protect their interests
   - Must not interfere with consumer ability to understand terms

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
- UDAAP compliance review for all consumer-facing agent outputs

### Framework Coverage
Framework addresses consumer protection topics (4/48 controls). CFPB-specific implementation required.

---

## FDIC-Supervised Institutions

### Overview
Applies to state non-member banks, state savings associations, and insured depository institutions supervised by the Federal Deposit Insurance Corporation.

### Regulatory Alignment

FDIC-supervised institutions follow the same interagency guidance as OCC and Federal Reserve institutions:

| Guidance | FDIC Applicability | Framework Alignment |
|----------|-------------------|---------------------|
| Interagency Model Risk Guidance (SR 11-7) | Adopted by FDIC | Control 2.6, 2.11 |
| Interagency Third-Party Guidance (2023) | Joint OCC/Fed/FDIC | Control 2.7 |
| FFIEC IT Examination Handbook | Primary reference | Pillars 1-4 |
| GLBA Safeguards Rule | Required | Pillar 1 Security |

### Applicable Controls

All framework controls apply to FDIC-supervised institutions. Key controls include:

| Control | Requirement | FDIC Relevance |
|---------|-------------|----------------|
| [1.7](pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Audit Logging | FFIEC IT Handbook - Audit and Monitoring |
| [1.11](pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access/MFA | FFIEC Authentication Guidance |
| [1.15](pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Encryption | FFIEC Information Security |
| [2.6](pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | Model Risk Management | Interagency SR 11-7 guidance |
| [2.7](pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Third-Party Risk | Interagency Third-Party Guidance (2023) |
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Examination expectations |

### FFIEC IT Examination Alignment

The framework aligns with FFIEC IT Examination Handbook domains:

| FFIEC Domain | Framework Pillar | Key Controls |
|--------------|-----------------|--------------|
| Information Security | Pillar 1 | 1.5, 1.11, 1.15, 1.18 |
| Audit | Pillar 1, 3 | 1.7, 3.1, 3.3 |
| Business Continuity | Pillar 2 | [2.4](pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) |
| Operations | Pillar 2 | 2.1, 2.3, 2.10 |
| Outsourcing Technology | Pillar 2 | [2.7](pillar-2-management/2.7-vendor-and-third-party-risk-management.md) |

### Governance Framework Alignment

**FDIC-Supervised Institutions:**

- Apply the same zone-based governance as OCC/Fed institutions
- Follow interagency model risk guidance (SR 11-7) for AI agents
- Reference FFIEC IT Examination Handbook for examination preparation
- Maintain evidence for examination readiness

### Framework Coverage
Framework provides equivalent coverage to OCC/Fed institutions. All 48 controls applicable.

---

## NCUA-Supervised Credit Unions

### Overview
Applies to federally insured credit unions supervised by the National Credit Union Administration.

### Regulatory Alignment

NCUA follows similar principles to banking regulators for technology risk management:

| Regulation | Description | Framework Alignment |
|------------|-------------|---------------------|
| NCUA Part 748 | Security Program Requirements | Pillar 1 Security Controls |
| NCUA Cybersecurity Guidance | Risk assessment and controls | Pillars 1-3 |
| FFIEC IT Examination Handbook | Shared examination standards | All Pillars |

### Applicable Controls

| Control | Requirement | NCUA Relevance |
|---------|-------------|----------------|
| [1.5](pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and Sensitivity Labels | Member data protection |
| [1.7](pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Audit Logging | Examination documentation |
| [1.11](pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access/MFA | Authentication controls |
| [1.15](pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Encryption | Member information security |
| [2.3](pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Control environment |
| [2.7](pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Third-Party Risk | Vendor oversight |
| [2.12](pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Board and management oversight |

### NCUA Part 748 Alignment

Part 748 requires credit unions to maintain a security program. Framework controls support:

1. **Administrative Controls** (Part 748.1)
   - Governance roles (RACI Matrix)
   - Training requirements (Control 2.14)
   - Incident response (Control 3.4)

2. **Technical Controls** (Part 748.1)
   - Access controls (Control 1.18)
   - Encryption (Control 1.15)
   - Audit trails (Control 1.7)

3. **Response Programs** (Part 748.1)
   - Incident detection and response (Control 3.4)
   - Member notification procedures

### Governance Framework Alignment

**Credit Union Implementation:**

- Credit unions may adapt the framework based on asset size and complexity
- Smaller credit unions may combine roles (see RACI Matrix guidance)
- Zone classification remains applicable
- Compliance Officer oversight for Zone 2+ agents

### Framework Coverage
Framework controls applicable to credit unions. Adapt based on asset size and AI agent complexity.

---

## State-Level Regulations (For Awareness)

### Overview
State-level regulations may apply depending on where the institution is chartered, operates, or serves customers. The following are provided for awareness; institutions should consult legal counsel for applicability.

### NYDFS Part 500 (23 NYCRR 500)

**Applicability:** Entities licensed by NYDFS (banks, insurers, money transmitters) with New York operations.

The framework's controls align with NYDFS Part 500 cybersecurity requirements:

| Part 500 Section | Requirement | Framework Control(s) |
|------------------|-------------|---------------------|
| §500.02 | Cybersecurity Program | Pillar 1 (Security), Pillar 2 (Management) |
| §500.03 | Cybersecurity Policy | Governance documentation |
| §500.05 | Penetration Testing | 2.5 Testing and Validation |
| §500.06 | Audit Trail | 1.7 Comprehensive Audit Logging |
| §500.07 | Access Privileges | 1.18 RBAC, 2.8 Segregation of Duties |
| §500.08 | Application Security | 2.5 Testing, 1.8 Runtime Protection |
| §500.10 | Cybersecurity Personnel | RACI Matrix role definitions |
| §500.11 | Third-Party Risk | 2.7 Vendor and Third-Party Risk |
| §500.12 | MFA | 1.11 Conditional Access and MFA |
| §500.14 | Training | 2.14 Training and Awareness |
| §500.15 | Encryption | 1.15 Encryption |
| §500.16 | Incident Response | 3.4 Incident Reporting |
| §500.17 | Notices to Superintendent | 3.4 Incident Reporting (escalation) |

**Note:** NYDFS Part 500 underwent significant amendments effective November 2023. Institutions should verify current requirements with legal counsel.

### CCPA/CPRA (California)

**Applicability:** Institutions with California customers may be subject to CCPA/CPRA for certain data processing activities.

**GLBA Preemption:** Financial institutions subject to GLBA may have limited CCPA/CPRA obligations for GLBA-covered data. However:

- Non-GLBA data may still be subject to CCPA/CPRA
- Employee data may be subject to CPRA
- Consult legal counsel for your specific situation

The framework's data governance controls (1.5, 1.6, 1.9, 1.14) support privacy compliance but do not specifically address CCPA/CPRA requirements.

### Other State Regulations

Additional state-level requirements may apply:

- **State Insurance Regulators** - See Insurance Regulators section
- **State Banking Regulators** - State-chartered institutions should consult their state regulator
- **State Privacy Laws** - Other states have enacted privacy laws (Virginia, Colorado, Connecticut, etc.)

---

## Insurance Regulators (For Awareness)

### Overview
Insurance companies are primarily regulated at the state level. The NAIC (National Association of Insurance Commissioners) develops model laws that states may adopt.

### NAIC Insurance Data Security Model Law

Many states have adopted versions of the NAIC Insurance Data Security Model Law, which requires:

| Requirement | Model Law Section | Framework Alignment |
|-------------|-------------------|---------------------|
| Information Security Program | Section 4 | Pillar 1, Pillar 2 |
| Risk Assessment | Section 4(C) | Zone classification, risk assessment |
| Security Controls | Section 4(D) | Pillar 1 Security Controls |
| Third-Party Oversight | Section 4(F) | Control 2.7 |
| Incident Response | Section 5 | Control 3.4 |
| Investigation and Notification | Section 6 | Control 3.4 |

### Framework Applicability to Insurers

The framework controls are generally applicable to insurance companies:

| Framework Area | Insurance Relevance |
|----------------|---------------------|
| **Pillar 1 (Security)** | Information security program requirements |
| **Pillar 2 (Management)** | Governance and oversight requirements |
| **Pillar 3 (Reporting)** | Incident response and reporting |
| **Pillar 4 (SharePoint)** | Document and data governance |

### Governance Framework Alignment

**Insurance Company Implementation:**

- Apply zone-based classification to AI agents
- Follow state insurance regulator requirements
- Reference NAIC model laws as baseline
- Consult state insurance department for specific requirements
- Annual certification may be required in some states

### Recommendation
Insurers should consult their primary state insurance regulator and legal counsel to confirm specific requirements. The framework provides a solid foundation but may require state-specific adaptations.

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
| CFPB / UDAAP | 4/48 | 8% | Consumer protection focus |
| FDIC (Interagency) | 48/48 | 100% | Full applicability; align to interagency guidance |
| NCUA Part 748 | 45/48 | 93% | Security program alignment |
| NYDFS Part 500 | 40/48 | 83% | State-level awareness |
| NAIC Model Law | 35/48 | 73% | Insurance awareness |

> **Note:** Coverage percentages indicate which framework controls address aspects of each regulation. Actual compliance requires implementation, validation, and ongoing maintenance. Consult legal counsel for regulatory interpretation. See [Disclaimer](../disclaimer.md).

---

## How to Use This Document

1. **Find your primary regulation** in the list above
2. **Review applicable controls** for your regulation
3. **Check governance zone** alignment (Zone 2 vs Zone 3 requirements)
4. **Reference individual control files** for detailed implementation
5. **Document compliance evidence** for audit purposes

---

*FSI Agent Governance Framework v1.0 - January 2026*
