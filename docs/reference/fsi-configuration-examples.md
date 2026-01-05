# FSI Configuration Examples

Concrete implementation examples for financial services organizations deploying Microsoft 365 AI agents.

---

## Industry Scenarios

This document provides specific configuration examples for:

- **Retail Banks** - Consumer banking, deposits, lending
- **Broker-Dealers** - Securities trading, investment advice
- **Insurance Companies** - Policy management, claims processing
- **Asset Managers** - Investment management, fund administration
- **Credit Unions** - Member services, lending

---

## Example 1: Retail Bank - Customer Service Agent

### Scenario
A regional retail bank deploys a customer service agent to handle account inquiries, balance checks, and transaction history requests for online banking customers.

### Classification
- **Zone:** Zone 3 (Enterprise Managed - Customer-facing)
- **Risk Level:** High
- **Data Types:** Customer PII, Account Numbers, Transaction History
- **Regulations:** GLBA, FINRA, SOX, State Banking Regulations

### Control Configuration

#### Control 1.4: Advanced Connector Policies

**Approved Connectors (Allowlist):**
| Connector | Justification | Data Classification |
|-----------|---------------|---------------------|
| Microsoft Dataverse | Customer account data storage | Confidential |
| Core Banking API (Custom) | Read-only access to account balances | Highly Confidential |
| SharePoint | Knowledge base articles | Internal |
| Microsoft Teams | Escalation to human advisors | Internal |

**Blocked Connectors:**

- All social media platforms (Twitter, Facebook, LinkedIn)
- Public cloud storage (Dropbox, Box, Google Drive)
- Consumer email services (Gmail, Yahoo Mail)
- Web scraping connectors
- Any connector transmitting data outside tenant

#### Control 1.5: DLP and Sensitivity Labels

**DLP Policy Configuration:**
```
Policy Name: FSI-CustomerService-DLP
Locations: Copilot Studio, SharePoint, OneDrive, Exchange
Conditions:
  - Detect: SSN, Bank Account Number, Credit Card Number, Driver's License
  - Confidence: High (85%+)
Actions:
  - Block external sharing
  - Encrypt content
  - Notify Compliance Officer
  - Log to audit
Exceptions: None for Zone 3
```

**Sensitivity Labels:**
| Label | Apply To | Protection |
|-------|----------|------------|
| Highly Confidential - Customer PII | All customer data | Encrypt, No download, Watermark |
| Confidential - Internal | Internal knowledge articles | Encrypt, Track access |
| General | Public-facing FAQs | No encryption |

#### Control 1.7: Audit Logging

**Audit Configuration:**

- Retention: 10 years (SEC 17a-4 compliance)
- Export: Weekly to Azure Blob (WORM storage)
- Real-time alerts: All agent interactions with customer data
- Review cadence: Daily by Compliance team

#### Control 1.11: Conditional Access

**Policy Configuration:**
```
Policy Name: FSI-CustomerAgent-CA
Users: All customer service representatives
Cloud Apps: Copilot Studio, Power Platform
Conditions:
  - Locations: Corporate network + approved remote locations only
  - Devices: Compliant devices only (Intune managed)
  - Risk: Block High and Medium risk sign-ins
Grant:
  - Require MFA (FIDO2 or Windows Hello)
  - Require compliant device
  - Require approved client app
Session:
  - Sign-in frequency: 4 hours
  - Persistent browser session: Disabled
```

#### Control 2.1: Managed Environments

**Environment Configuration:**
| Setting | Value |
|---------|-------|
| Environment Name | FSI-Production-CustomerService |
| Environment Type | Production |
| Managed Environment | Enabled |
| Weekly Digest | Enabled |
| Limit Sharing | Exclude Sharing to Security Groups |
| Solution Checker | Enforced |
| Maker Welcome | Enabled |

---

## Example 2: Broker-Dealer - Research Assistant Agent

### Scenario
An investment firm deploys a research assistant agent to help analysts search internal research reports, summarize market data, and draft preliminary investment recommendations.

### Classification
- **Zone:** Zone 3 (Enterprise Managed)
- **Risk Level:** High
- **Data Types:** Investment Research, Trade Recommendations, Client Holdings
- **Regulations:** FINRA 3110, SEC Reg BI, FINRA 4511, SOX

### Control Configuration

#### Control 2.6: Model Risk Management

**SR 11-7 Compliance Framework:**

| Requirement | Implementation |
|-------------|----------------|
| Model Inventory | Agent registered in Model Risk inventory with unique ID |
| Risk Rating | High - directly impacts investment decisions |
| Validation | Independent validation by Model Validation team quarterly |
| Monitoring | Daily performance metrics vs. baseline |
| Limits | Agent recommendations require human review before action |

**Testing Schedule:**

- Pre-deployment: Full functionality and bias testing
- Monthly: Performance monitoring and drift detection
- Quarterly: Independent validation and accuracy assessment
- Annual: Full model validation with external review

#### Control 2.11: Bias Testing

**Fairness Assessment Configuration:**
```
Test Frequency: Quarterly
Metrics Tracked:
  - Recommendation accuracy by sector
  - Response quality by analyst seniority
  - Coverage of small-cap vs. large-cap securities
Thresholds:
  - Accuracy variance by sector: <5%
  - Coverage ratio: Within 10% of benchmark
Documentation:
  - Test methodology
  - Results by metric
  - Remediation actions if thresholds exceeded
Review: Compliance Committee quarterly
```

#### Control 2.12: Supervision (FINRA 3110)

**Supervisory Controls:**
| Requirement | Implementation |
|-------------|----------------|
| Written Procedures | Agent use documented in WSPs |
| Designated Supervisor | Chief Compliance Officer oversight |
| Review Frequency | Daily spot-checks, weekly comprehensive review |
| Escalation | Immediate escalation for recommendation errors |
| Documentation | All agent outputs retained per FINRA 4511 |

**Supervision Workflow:**

1. Agent generates draft recommendation
2. Analyst reviews and edits
3. Supervisor reviews before publication
4. Compliance spot-checks 10% of recommendations daily
5. All interactions logged for regulatory examination

#### Control 1.10: Communication Compliance

**Policy Configuration:**
```
Policy Name: Investment-Research-Compliance
Scope: All Copilot Studio agent interactions
Conditions:
  - Detect: Investment recommendations, Buy/Sell language
  - Detect: Price targets, Earnings estimates
  - Detect: Material non-public information patterns
Actions:
  - Route to Compliance queue for review
  - Retain all communications
  - Flag potential violations
Reviewers: Compliance Team
SLA: Review within 24 hours
```

---

## Example 3: Insurance Company - Claims Processing Agent

### Scenario
A property & casualty insurer deploys an agent to assist claims adjusters with initial claim intake, damage assessment documentation, and coverage verification.

### Classification
- **Zone:** Zone 3 (Enterprise Managed)
- **Risk Level:** High
- **Data Types:** Policyholder PII, Health Information (if applicable), Financial Records
- **Regulations:** State Insurance Regulations, GLBA, HIPAA (if health data)

### Control Configuration

#### Control 1.13: Sensitive Information Types

**Custom SITs for Insurance:**
| SIT Name | Pattern | Confidence |
|----------|---------|------------|
| Policy Number | [A-Z]{2}[0-9]{8} | High |
| Claim Number | CLM-[0-9]{10} | High |
| VIN | [A-HJ-NPR-Z0-9]{17} | High |
| Medical Record Number | MRN-[0-9]{8} | High |
| Insurance Score | Pattern + context | Medium |

**SIT Policy Application:**

- Apply DLP rules to all custom SITs
- Block external sharing of documents containing policy/claim numbers
- Require encryption for documents with medical information
- Audit all access to documents with sensitive SITs

#### Control 1.14: Data Minimization

**Agent Scope Configuration:**
| Data Source | Access Level | Justification |
|-------------|--------------|---------------|
| Claims Database | Read (specific claim only) | Process current claim |
| Policy Database | Read (policy linked to claim) | Verify coverage |
| Adjuster Notes | Read/Write | Document claim processing |
| Payment System | None | Payments processed by human only |
| Medical Records | Read (with authorization) | Medical claims only |

**Scope Enforcement:**

- API-level restrictions on data access
- No bulk data export capability
- Session-based access tokens (30-minute expiry)
- Quarterly scope audits by Information Security

#### Control 4.1: SharePoint IAG/RCD

**Restricted Content Discovery Configuration:**
```
Policy Name: Claims-Document-Protection
Protected Sites: 
  - Claims Documentation Library
  - Adjuster Workspaces
  - Medical Records Archive
Restrictions:
  - Copilot/Agent cannot discover content without explicit access
  - Restrict search results to claim-specific documents
  - Block cross-claim document access
Audit: Log all agent access attempts
```

---

## Example 4: Asset Manager - Portfolio Analysis Agent

### Scenario
An asset management firm deploys an agent to help portfolio managers analyze fund performance, generate attribution reports, and summarize market conditions.

### Classification
- **Zone:** Zone 2 (Team Collaboration) - Internal use only
- **Risk Level:** Medium
- **Data Types:** Portfolio Holdings, Performance Data, Market Data
- **Regulations:** SEC, Investment Advisers Act, DOL (for ERISA funds)

### Control Configuration

#### Control 2.2: Environment Groups

**Environment Group Structure:**
| Group Name | Tier | Environments | Policies |
|------------|------|--------------|----------|
| FSI-Development | Dev | Dev-PortfolioAnalytics | Relaxed DLP, All connectors |
| FSI-Test | Test | UAT-PortfolioAnalytics | Production-like DLP |
| FSI-Production | Prod | Prod-PortfolioAnalytics | Strict DLP, ACP enforced |

**Promotion Workflow:**

1. Development in Dev tier (no approval needed)
2. Testing in Test tier (Tech Lead approval)
3. Production deployment (Change Advisory Board approval)
4. All promotions logged and documented

#### Control 2.3: Change Management

**Change Control Process:**
| Change Type | Approval Required | Lead Time | Documentation |
|-------------|------------------|-----------|---------------|
| Hotfix | Tech Lead | 1 hour | Post-implementation |
| Standard | Manager | 24 hours | Pre-approval |
| Major | CAB | 5 business days | Full change request |
| Emergency | CTO + CCO | Immediate | Post-implementation within 24h |

**Documentation Requirements:**

- Business justification
- Technical design
- Test results from UAT
- Rollback plan
- Compliance review sign-off

#### Control 3.2: Usage Analytics

**Monitoring Dashboard Metrics:**
| Metric | Threshold | Alert |
|--------|-----------|-------|
| Daily Active Users | >10, <100 | Outside range |
| Avg Response Time | <3 seconds | >5 seconds |
| Error Rate | <2% | >5% |
| Sessions per Day | Baseline ±20% | Outside range |
| Top Queries | Track for accuracy | Manual review |

**Reporting Cadence:**

- Daily: Automated dashboard refresh
- Weekly: Usage summary to stakeholders
- Monthly: Performance review with IT leadership
- Quarterly: ROI analysis with business sponsors

---

## Example 5: Credit Union - Member Services Agent

### Scenario
A credit union deploys a member services agent to answer questions about accounts, loan products, and branch services for members via the credit union website.

### Classification
- **Zone:** Zone 3 (Enterprise Managed - Member-facing)
- **Risk Level:** High
- **Data Types:** Member PII, Account Information, Loan Data
- **Regulations:** NCUA, GLBA, State Credit Union Laws

### Control Configuration

#### Control 1.8: Runtime Protection

**Runtime Protection Settings:**
| Setting | Value | Rationale |
|---------|-------|-----------|
| Prompt Injection Detection | Enabled | Prevent manipulation |
| Jailbreak Prevention | Enabled | Block bypass attempts |
| Harmful Content Blocking | Enabled | Protect members |
| External URL Blocking | Enabled | Prevent phishing links |
| PII Redaction in Logs | Enabled | Minimize data exposure |

**Threat Response:**

- Detected threats: Block immediately
- Alert: Security Operations within 5 minutes
- Log: Full interaction context retained
- Escalation: Security incident if pattern detected

#### Control 4.4: Guest Access Controls

**External Sharing Configuration:**
```
SharePoint Sharing Settings:
  Organization Level: Only people in your organization
  Site Level (Member Docs): No external sharing
  Site Level (Public Info): Existing guests (if needed)
  
Guest Access:
  Require MFA: Yes
  Guest expiration: 30 days
  Guest access reviews: Monthly
  
Agent Access:
  No access to guest-shared content
  Block if document has external sharing enabled
```

#### Control 1.9: Data Retention

**Retention Configuration:**
| Content Type | Retention Period | Disposition |
|--------------|------------------|-------------|
| Agent Interactions | 7 years | Review then delete |
| Member Account Documents | 7 years after account closure | Legal hold then delete |
| Loan Documents | 7 years after payoff | Archive then delete |
| Audit Logs | 10 years | Immutable storage |

**Retention Workflow:**

1. Auto-apply retention labels based on content type
2. Quarterly disposition review
3. Legal hold process for litigation
4. Deletion certificates for auditors

---

## Configuration Checklists

### Pre-Deployment Checklist (All Zones)

- [ ] Agent purpose documented
- [ ] Data sources identified and classified
- [ ] Connectors approved through change management
- [ ] DLP policies configured and tested
- [ ] Sensitivity labels applied to data sources
- [ ] Access controls configured (least privilege)
- [ ] Audit logging enabled
- [ ] Testing completed in non-production environment

### Zone 3 Additional Requirements

- [ ] Governance Committee approval obtained
- [ ] Legal review completed
- [ ] Model risk assessment documented
- [ ] Bias testing performed and documented
- [ ] Supervisory procedures documented
- [ ] Incident response plan updated
- [ ] Retention policies configured (10 years)
- [ ] Change management approval obtained
- [ ] Third-party validation scheduled (if required)

---

## Common Configuration Patterns

### Pattern 1: Strict Allowlist (Zone 3 Default)
- Block all connectors by default
- Explicitly approve each connector with business justification
- Quarterly review of all approved connectors
- Immediate revocation if risk identified

### Pattern 2: Deny External (All Zones)
- Block all connectors that transmit data externally
- Allow internal Microsoft services only
- Custom connectors require security review
- Monitor for shadow IT / unapproved connectors

### Pattern 3: Data Classification Enforcement
- Require sensitivity labels on all data sources
- Block agent access to unlabeled content
- Apply DLP based on label sensitivity
- Audit all access to Confidential+ content

---

*Last Updated: December 2025*
