# Regulatory Mappings

Mapping of framework controls to regulatory requirements.

---

## FINRA Rule 4511 - Books and Records

### Overview
Requires firms to maintain records of all agent activities and communications.

### Retention Period Matrix

| Record Type | Retention | Regulation | Access Requirement |
|-------------|-----------|------------|--------------------|
| **Communications** (agent logs, chat, email) | 3 years | SEC 17a-4(b)(4) | First 2 years easily accessible place |
| **Accounting/Financial Records** | 6 years | SEC 17a-4(a) | First 2 years easily accessible place |
| **Customer Account Records** | 6 years after account close | SEC 17a-4(c) | First 2 years easily accessible place |
| **Agent Governance Records** (approvals, validations, incidents, bias testing) | 6 years | SEC 17a-4(a) / SR 26-2 (formerly SR 11-7) | First 2 years easily accessible place |
| **Derivatives/Commodities Records** (CFTC-registered entities) | 5 years minimum | CFTC Rule 1.31 | First 2 years readily accessible |
| **FINRA-Specific Records** (no SEC period applies) | 6 years | FINRA 4511(b) | First 2 years easily accessible place |
| **AI Marketing Substantiation** (investment advisers) | 7 years | FINRA 4511 / Control 2.21 | First 2 years easily accessible place |

!!! note "Terminology Note"
    "Readily accessible" (CFTC) and "easily accessible place" (SEC/FINRA) both mean the same compliance standard: records must be available for immediate access and review.

!!! warning "Agent Logs as Communications"
    Agent conversation logs typically fall under the 3-year communications retention (SEC 17a-4(b)(4)), not the 6-year financial records period. If agent interactions generate or modify financial records, those outputs follow the 6-year period.

!!! warning "Dataverse Audit Event Changes — May 2026"
    Starting May 2026, Dataverse will no longer include before-and-after field change values in audit events sent to Microsoft Purview. Organizations relying on Purview audit events for Dataverse field-level change records to support FINRA 4511 recordkeeping requirements should transition to Dataverse API-based retrieval before May 2026. See [Control 1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for implementation guidance.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | Retention per record type (3 years for communications, 6 years for financial records) |
| [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention and Deletion | Retention policies per record type matrix |
| [1.20](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | Network Isolation | Secure network architecture for records systems |
| [1.21](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Adversarial Input Logging | Record security incidents and attacks |
| [1.25](../controls/pillar-1-security/1.25-mime-type-restrictions.md) | MIME Type Restrictions | Supervise file-based agent interactions and maintain record integrity |
| [1.26](../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | File Upload Restrictions | Granular control over file-based interactions subject to retention and review |
| [2.9](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | Agent Performance Monitoring | Track all agent activity |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and Oversight | Compliance Officer oversight |
| [2.22](../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md) | Inactivity Timeout Enforcement | Session timeout supports supervisory controls and record integrity |
| [2.24](../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | Feature Enablement Governance | Restrict features lacking adequate audit trails for recordkeeping |
| [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Central registry of all agents |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance and Regulatory Reporting | Regular compliance reports |
| [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Incident Reporting | Document all incidents |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback Loop | Record and track accuracy issues |
| [3.11](../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | Centralized Inventory Enforcement | Complete inventory for audit trails and supervisory records |
| [4.6](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Grounding Scope Governance | Govern knowledge source records |
| [4.7](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | M365 Copilot Data Governance | M365 Copilot usage records |

### Governance Framework Alignment

**Zone 2 Requirements:**

- Maintain 1-year audit logs
- Document approval process
- Monthly compliance reviews
- Supervisory controls per Rule 3110

**Zone 3 Requirements:**

- Maintain audit logs per retention matrix (3 years for communications, 6 years for financial records; first 2 years readily accessible)
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
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision and Oversight | Define supervisory procedures |
| [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Change control and approval |
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | QA before production |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management | SR 26-2 (formerly SR 11-7) alignment |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Bias Testing | Fairness assessment |
| [2.15](../controls/pillar-2-management/2.15-environment-routing.md) | Environment Routing | Enforce routing rules based on role/group membership for supervision |
| [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-Agent Orchestration Limits | Supervise agent interactions |
| [2.18](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Conflict of Interest Testing | Test for recommendation biases |
| [2.23](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | User Consent and AI Disclosure | Disclosure supports supervisory obligations for AI interactions |
| [2.24](../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | Feature Enablement Governance | Supervisory procedures for agent feature enablement |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Supervision documentation |
| [3.12](../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md) | Exception Management | Documented exceptions to supervisory procedures with principal approval |

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
Framework provides supervision procedure guidance through 8 mapped controls. Implementation required.

---

## FINRA AI Supervision and Governance

!!! warning "FINRA Notice 25-07 Clarification"
    FINRA Regulatory Notice 25-07 (April 2025) addresses **workplace modernization rules**, not AI governance. It discusses AI only in the limited context of recordkeeping for AI-generated communications. For AI supervision requirements, refer to **FINRA Regulatory Notice 24-09** (Gen AI guidance), **FINRA Rule 3110** (Supervision), **FINRA Rule 2111** (Suitability), and **FINRA's Annual Regulatory Oversight Report** for current AI examination priorities.

!!! info "FINRA Regulatory Notice 24-09 (June 2024)"
    FINRA Notice 24-09 provides official guidance on generative AI and large language model (LLM) obligations:

    - **Technology-neutral principle:** Existing FINRA rules apply equally to AI-generated content
    - **Rule 3110 supervision:** Firms must establish supervisory procedures for AI tools
    - **Rule 2210 communications:** AI-generated customer communications must meet content standards
    - **Firm responsibility:** Per FINRA FAQ D.8, "Firms are responsible for their communications, regardless of whether they are generated by a human or AI technology"

    See: [FINRA Regulatory Notice 24-09](https://www.finra.org/rules-guidance/notices/24-09)

!!! tip "FINRA 2026 Annual Regulatory Oversight Report (December 2025)"
    The 2026 Report contains FINRA's most detailed AI agent supervision guidance, with a dedicated GenAI section:

    | Topic | Requirement | Framework Control |
    |-------|-------------|-------------------|
    | **AI as Supervisory Function** | Document WSPs for AI supervision substitution | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
    | **Audit Trail Completeness** | Retain prompts, model state, reasoning—not just outputs | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) |
    | **Decision Reconstruction** | Demonstrate how agents reached conclusions | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) |
    | **Agent Autonomy Limits** | Dedicated supervisory procedures for AI agents | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |

    See: [FINRA 2026 Annual Regulatory Oversight Report](https://www.finra.org/rules-guidance/guidance/reports/2026-finra-annual-regulatory-oversight-report)

### Overview

FINRA's supervisory requirements for AI systems derive primarily from existing rules rather than AI-specific guidance:

- **FINRA Regulatory Notice 24-09 (June 2024):** Official guidance on Gen AI and LLM obligations for broker-dealers
- **FINRA Rule 3110 (Supervision):** Requires supervision of associated persons' activities, including use of AI tools for customer communications and recommendations
- **FINRA Rule 3120 (Supervisory Control System):** Requires testing and verification of supervisory procedures, including those for AI systems
- **FINRA Rule 2111 (Suitability):** Requires reasonable basis for recommendations, including those assisted by AI
- **FINRA Rule 2210 (Communications):** AI-generated customer communications must meet content standards; firms are responsible regardless of AI involvement
- **FINRA Rule 4511 (Books and Records):** Requires retention of AI-generated communications and agent interaction logs

### FINRA Rule 2210 Communication Classifications

| Communication Type | Definition | Supervision Requirement | AI Agent Impact |
|-------------------|------------|------------------------|-----------------|
| **Correspondence** | To ≤25 retail investors in 30 days | Post-use review acceptable | Zone 2 agents may qualify |
| **Retail Communication** | To >25 retail investors in 30 days | Pre-use principal approval required | Zone 3 agents typically require |
| **Institutional** | Institutional investors only | Internal procedures | Reduced supervision |

!!! warning "Zone 3 Agent Classification"
    If agent output could reach >25 retail investors in any 30-day period, configure HITL pre-approval per Retail Communication requirements.

### FINRA Notice 15-09 — Algorithmic Trading Precedent

FINRA Regulatory Notice 15-09 (March 2015) addresses supervision of algorithmic trading strategies and provides a useful precedent for AI agent testing:

| Principle | Application to AI Agents | Framework Control |
|-----------|-------------------------|-------------------|
| **Pre-deployment testing** | Test agents in controlled environments before production | [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) |
| **Ongoing monitoring** | Continuously monitor agent performance | [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) |
| **Kill switch capability** | Ability to halt agent operation quickly | [2.4](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) |
| **Change testing** | Re-test after any modification | [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) |

See: [FINRA Regulatory Notice 15-09](https://www.finra.org/rules-guidance/notices/15-09)

### Applicable Controls

| Control | Topic | Mapping |
|---------|-------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | Records retention for AI communications |
| [1.27](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | Content Moderation | Filter harmful outputs per supervisory obligations |
| [1.28](../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | Publishing Restrictions | Approval and review before customer-facing agent deployment |
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | Agent accuracy and reliability testing |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management | Formal framework per SR 26-2 (formerly SR 11-7) |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Bias Testing | Fairness assessment per SR 26-2 (formerly SR 11-7) |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Written supervisory procedures |
| [2.18](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Conflict of Interest Testing | Test for recommendation biases |
| [2.23](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | User Consent and AI Disclosure | AI disclosure supports supervisory obligations per FINRA 2210 |
| [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | Performance monitoring |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback Loop | Monitor output accuracy |

### Key Requirements

1. **Written Supervisory Procedures (Rule 3110)**
   - Document AI tool approval process
   - Define supervisory review procedures
   - Establish escalation paths for AI-related issues
   - Train supervisors on AI capabilities and limitations

2. **Suitability Requirements (Rule 2111)**
   - Validate AI recommendations meet suitability standards
   - Document basis for AI-assisted recommendations
   - Ensure human review for material decisions

3. **Recordkeeping (Rule 4511)**
   - Retain AI-generated customer communications
   - Log agent interactions and outputs
   - Maintain audit trail for AI-assisted decisions

### Governance Framework Alignment

The framework applies FINRA's existing supervision principles to AI agents, treating them as tools requiring documented procedures, ongoing monitoring, and supervisory oversight.

### Framework Coverage
Framework addresses FINRA supervision requirements through 8 mapped controls. Implementation and validation required.

---

## SEC Rule 17a-3/4 - Recordkeeping

### Overview
Requires SEC-registered firms to maintain records for varying periods: 3 years for communications per 17a-4(b)(4), 6 years for accounting/financial records per 17a-4(a), with the first 2 years in an easily accessible place.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | 6-year retention, first 2 years in easily accessible place |
| [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention | Retention policies enforced |
| [1.20](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | Network Isolation | Secure storage network architecture |
| [1.21](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Adversarial Input Logging | Security event records |
| [1.25](../controls/pillar-1-security/1.25-mime-type-restrictions.md) | MIME Type Restrictions | Reduce risk of unauditable formats entering record stream |
| [1.26](../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | File Upload Restrictions | Control file-based content entering record stream |
| [1.27](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | Content Moderation | Prevent responses triggering disclosure violations |
| [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation and Record Keeping | All records documented |
| [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Registry of agents as records |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Evidence retention |
| [4.6](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Grounding Scope Governance | Knowledge source records |
| [4.7](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | M365 Copilot Data Governance | M365 Copilot usage logging |
| 4.8 | Item-Level Permission Scanning for Agent Knowledge Sources | Agent knowledge source access documentation and control |

!!! warning "Dataverse Audit Event Changes — May 2026"
    Starting May 2026, Dataverse will no longer include before-and-after field change values in audit events sent to Microsoft Purview. Organizations relying on Purview audit events for Dataverse field-level change records to support SEC 17a-4 record retention requirements should transition to Dataverse API-based retrieval before May 2026. This may affect the completeness of audit records for agent interactions involving Dataverse entities. See [Control 1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) for implementation guidance.

### Record Categories

**Agent Communications:**

- All user interactions with agents
- All agent outputs and decisions
- All approvals and rejections
- Retention: 3 years per SEC 17a-4(b)(4) (communications), first 2 years in easily accessible place
- Exception: If agent outputs constitute accounting/financial records, apply 6-year retention per SEC 17a-4(a)

**Transaction Records:**

- If agent processes transactions
- If agent provides investment advice
- If agent executes trades
- Retention: 6 years, first 2 years in easily accessible place

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

- 6-year retention, first 2 years in easily accessible place
- WORM or audit-trail alternative (per SEC October 2022 amendments)
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
| [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | Data governance and privacy |
| [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Data Minimization | Use only necessary data |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management | Agent accuracy and reliability |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Bias Testing | Fair treatment across demographics |
| [2.18](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Conflict of Interest Testing | Best interest standard compliance |
| [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Customer AI Disclosure | AI transparency and disclosure |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback Loop | Ensure advice accuracy |

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
Framework incorporates SEC AI disclosure guidance through 6 mapped controls. Legal review recommended. Implementation required.

---

## SEC Marketing Rule (206(4)-1) - AI Marketing Claims

### Overview
The SEC Marketing Rule governs advertising by investment advisers, including claims about AI capabilities. SEC enforcement actions in 2024 (Delphia Inc., Global Predictions Inc.) established precedent for "AI washing" enforcement.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.21](../controls/pillar-2-management/2.21-ai-marketing-claims-and-substantiation.md) | AI Marketing Claims and Substantiation | Primary control for marketing rule compliance |
| [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Customer AI Disclosure | Transparency complements marketing accuracy |
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | Performance claims require substantiation |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management | Validates AI capabilities being marketed |
| [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation | Maintains substantiation evidence |

### Key Requirements

1. **Substantiation Required**
   - All AI capability claims must have reasonable basis
   - Performance claims require documented testing methodology
   - Comparative claims require controlled studies

2. **No Material Misstatements**
   - Cannot overstate AI capabilities
   - Must disclose AI limitations
   - Cannot imply human-level judgment where AI is used

3. **Pre-Publication Review**
   - Compliance review before external publication
   - Legal review for Zone 3 customer-facing claims
   - Document approval workflow

4. **Ongoing Monitoring**
   - Quarterly review of published claims
   - Update or retire claims when AI capabilities change
   - Monitor for regulatory guidance changes

### Governance Framework Alignment

**Zone 3 Customer-Facing AI Marketing:**

- Mandatory pre-publication compliance review
- Legal review for all external AI claims
- Substantiation file maintained with evidence
- Quarterly claims accuracy review
- 7-year retention per FINRA 4511

### Framework Coverage
Framework provides dedicated AI marketing claims control (Control 2.21). Implementation required for investment advisers.

---

## SOX Section 302/404 - Internal Controls

### Overview
Requires CEO/CFO certification of internal control effectiveness and management assessment.

### Applicable Controls

**Pillar 1 - Security Controls (19 controls):**

| Control | Requirement | SOX Mapping |
|---------|-------------|-------------|
| [1.1](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Restrict Agent Publishing | Authorization controls over system changes |
| [1.2](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Agent Registry | Inventory of IT systems |
| [1.3](../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | SharePoint Governance | Access controls over financial data |
| [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and Sensitivity Labels | Data protection controls |
| [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | Data governance and classification |
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | Audit trail for transactions |
| [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime Protection | Security monitoring controls |
| [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention | Record retention policies |
| [1.10](../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Communication Compliance | Monitoring controls |
| [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access and MFA | Authentication controls |
| [1.12](../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) | Insider Risk Detection | Fraud detection controls |
| [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Data Minimization | Scope limitation controls |
| [1.15](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Encryption | Data protection controls |
| [1.16](../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | IRM | Document protection controls |
| [1.17](../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | Endpoint DLP | Endpoint data protection |
| [1.18](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | RBAC | Access control matrix |
| [1.19](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | eDiscovery | Audit and investigation capability |
| [1.20](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | Network Isolation | IT infrastructure security |
| [1.22](../controls/pillar-1-security/1.22-information-barriers.md) | Information Barriers | Segregation of information |
| [1.28](../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | Publishing Restrictions | Change management and deployment controls |

| Control | Requirement | SOX Mapping |
|---------|-------------|-------------|
| [2.1](../controls/pillar-2-management/2.1-managed-environments.md) | Managed Environments | Environment controls |
| [2.2](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | Environment Groups | Classification controls |
| [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Change control procedures |
| [2.4](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) | BC/DR | Continuity controls |
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | Control testing documented |
| [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Vendor Risk Management | Third-party controls |
| [2.8](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Access Control and SoD | Segregation of duties enforced |
| [2.9](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | Performance Monitoring | Operational controls |
| [2.10](../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | Patch Management | Security control maintenance |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Management oversight |
| [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation | Evidence for control effectiveness |
| [2.14](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | Training | Control awareness |
| [2.15](../controls/pillar-2-management/2.15-environment-routing.md) | Environment Routing | Audit trail of routing decisions for internal controls |
| [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-Agent Orchestration | Control over complex systems |
| [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Adversarial Testing | Security testing |
| [2.22](../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md) | Inactivity Timeout | Internal controls over financial reporting systems |
| [2.24](../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | Feature Enablement Governance | Control environment for AI capability authorization |

**Pillar 3 - Reporting Controls (7 controls):**

| Control | Requirement | SOX Mapping |
|---------|-------------|-------------|
| [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | System inventory |
| [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | Activity monitoring |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Control effectiveness reports |
| [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Incident Reporting | Incident response |
| [3.5](../controls/pillar-3-reporting/3.5-cost-allocation-and-budget-tracking.md) | Cost Allocation | Financial controls |
| [3.7](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | Security Posture | Control assessment |
| [3.9](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Sentinel Integration | Security monitoring |
| [3.11](../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | Centralized Inventory Enforcement | IT general controls over application inventory |
| [3.12](../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md) | Exception Management | Documented exception processes with management approval |

**Pillar 4 - SharePoint Controls (4 controls):**

| Control | Requirement | SOX Mapping |
|---------|-------------|-------------|
| [4.2](../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | Site Access Reviews | Access certification |
| [4.3](../controls/pillar-4-sharepoint/4.3-site-and-document-retention-management.md) | Retention Management | Record retention |
| [4.5](../controls/pillar-4-sharepoint/4.5-sharepoint-security-and-compliance-monitoring.md) | Security Monitoring | Monitoring controls |
| [4.7](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | M365 Copilot Data Governance | Output review processes |

**Mapped controls: 44**

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
Framework provides 44 mapped controls relevant to SOX requirements. SOX-specific testing required. Implementation required.

---

## GLBA Safeguards Rule (501-505)

### Overview
Requires financial institutions to maintain appropriate safeguards for customer information.

!!! warning "FTC Safeguards Rule Amendments (2021/2023)"
    The FTC significantly strengthened the GLBA Safeguards Rule through amendments effective June 9, 2023 (16 CFR Part 314). Financial institutions must implement **10 specific elements** in their information security programs. AI agents handling customer NPI must be governed within this framework.

### Required Safeguards Rule Elements (16 CFR 314.4)

| # | Required Element | AI Agent Application | FSI-AgentGov Control |
|---|-----------------|---------------------|---------------------|
| 1 | **Qualified Individual** to oversee program | AI Governance Lead accountable for agent security | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
| 2 | **Risk Assessment** - written, updated | Include AI agents in annual risk assessment | [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) |
| 3 | **Safeguards** - implement and test controls | DLP, access controls, encryption for agent data | Pillar 1 controls (1.1-1.24) |
| 4 | **Service Provider Oversight** | Due diligence for Microsoft, AI model providers | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) |
| 5 | **Evaluate and Adjust** - continuous monitoring | Monitor agent performance and security posture | [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [3.7](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) |
| 6 | **Staff Training** | Train staff on AI agent security and governance | [2.14](../controls/pillar-2-management/2.14-training-and-awareness-program.md) |
| 7 | **Qualified Individual Reports** to board/senior management | Include AI agent governance in board reporting | [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) |
| 8 | **Encryption** of customer information | TLS for transit, encryption at rest | [1.15](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) |
| 9 | **Multi-Factor Authentication** | MFA for agent developers and administrators | [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) |
| 10 | **Incident Response Plan** | Include AI agent incidents in IR plan | [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md), [2.4](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) |

### Breach Notification Requirement

!!! danger "30-Day Notification Deadline"
    The amended Safeguards Rule requires notification to the FTC **within 30 days** of discovering a breach affecting 500+ customers. AI agent security incidents that result in unauthorized access to customer NPI trigger this requirement.

    **Notification Requirements:**

    - Report via FTC's online portal (BreachNotification.ftc.gov)
    - Include description of the event, types of information involved, estimated number of affected customers
    - AI-specific incidents: Document whether the breach resulted from agent misconfiguration, prompt injection, data exfiltration, or other AI-specific vectors

    **Source:** [FTC Safeguards Rule](https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know)

### Applicable Controls

**Pillar 1 - Security Controls (22 controls):**

| Control | Requirement | GLBA Mapping |
|---------|-------------|--------------|
| [1.1](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Restrict Agent Publishing | Administrative safeguard - authorization |
| [1.2](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) | Agent Registry | Administrative safeguard - inventory |
| [1.3](../controls/pillar-1-security/1.3-sharepoint-content-governance-and-permissions.md) | SharePoint Governance | Technical safeguard - permission management |
| [1.4](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Advanced Connector Policies | Technical safeguard - data flow control |
| [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and Sensitivity Labels | Technical safeguard - data loss prevention |
| [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | Technical safeguard - data governance |
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | Technical safeguard - audit trail |
| [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime Protection | Technical safeguard - threat detection |
| [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention | Administrative safeguard - records |
| [1.10](../controls/pillar-1-security/1.10-communication-compliance-monitoring.md) | Communication Compliance | Technical safeguard - monitoring |
| [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access and MFA | Technical safeguard - authentication |
| [1.12](../controls/pillar-1-security/1.12-insider-risk-detection-and-response.md) | Insider Risk Detection | Technical safeguard - threat detection |
| [1.13](../controls/pillar-1-security/1.13-sensitive-information-types-sits-and-pattern-recognition.md) | Sensitive Information Types | Technical safeguard - data classification |
| [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Data Minimization | Technical safeguard - scope control |
| [1.15](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Encryption | Technical safeguard - data protection |
| [1.16](../controls/pillar-1-security/1.16-information-rights-management-irm-for-documents.md) | Information Rights Management | Technical safeguard - document protection |
| [1.17](../controls/pillar-1-security/1.17-endpoint-data-loss-prevention-endpoint-dlp.md) | Endpoint DLP | Technical safeguard - endpoint protection |
| [1.18](../controls/pillar-1-security/1.18-application-level-authorization-and-role-based-access-control-rbac.md) | RBAC | Technical safeguard - access control |
| [1.19](../controls/pillar-1-security/1.19-ediscovery-for-agent-interactions.md) | eDiscovery | Administrative safeguard - investigation |
| [1.20](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | Network Isolation | Technical safeguard - network security |
| [1.21](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Adversarial Input Logging | Technical safeguard - threat logging |
| [1.22](../controls/pillar-1-security/1.22-information-barriers.md) | Information Barriers | Technical safeguard - information segregation |
| [1.24](../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | Defender AI-SPM | Technical safeguard - AI threat assessment |
| [1.25](../controls/pillar-1-security/1.25-mime-type-restrictions.md) | MIME Type Restrictions | Technical safeguard - attack surface reduction |
| [1.26](../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | File Upload Restrictions | Technical safeguard - data ingestion control |
| [1.27](../controls/pillar-1-security/1.27-ai-agent-content-moderation-enforcement.md) | Content Moderation | Technical safeguard - output privacy protection |

| Control | Requirement | GLBA Mapping |
|---------|-------------|--------------|
| [2.1](../controls/pillar-2-management/2.1-managed-environments.md) | Managed Environments | Administrative safeguard - governance |
| [2.2](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | Environment Groups | Administrative safeguard - classification |
| [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Administrative safeguard - change control |
| [2.4](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) | BC/DR | Administrative safeguard - continuity |
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | Administrative safeguard - validation |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management | Administrative safeguard - risk management |
| [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Vendor Risk Management | Administrative safeguard - third-party oversight |
| [2.8](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Access Control and SoD | Technical safeguard - access management |
| [2.9](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | Performance Monitoring | Technical safeguard - monitoring |
| [2.10](../controls/pillar-2-management/2.10-patch-management-and-system-updates.md) | Patch Management | Technical safeguard - security updates |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Administrative safeguard - oversight |
| [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation | Administrative safeguard - records |
| [2.14](../controls/pillar-2-management/2.14-training-and-awareness-program.md) | Training | Administrative safeguard - training program |
| [2.15](../controls/pillar-2-management/2.15-environment-routing.md) | Environment Routing | Administrative safeguard - data policy enforcement |
| [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | RAG Source Integrity | Technical safeguard - data integrity |
| [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-Agent Orchestration | Technical safeguard - system controls |
| [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Customer AI Disclosure | Administrative safeguard - customer notice |
| [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Adversarial Testing | Technical safeguard - security testing |
| [2.22](../controls/pillar-2-management/2.22-inactivity-timeout-enforcement.md) | Inactivity Timeout | Technical safeguard - session security |
| [2.23](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | User Consent and AI Disclosure | Administrative safeguard - transparency obligation |
| [2.24](../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | Feature Enablement Governance | Technical safeguard - feature restriction |

**Pillar 3 - Reporting Controls (7 controls):**

| Control | Requirement | GLBA Mapping |
|---------|-------------|--------------|
| [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Administrative safeguard - asset inventory |
| [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | Technical safeguard - monitoring |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Administrative safeguard - reporting |
| [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Incident Reporting | Administrative safeguard - incident response |
| [3.7](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | Security Posture | Technical safeguard - assessment |
| [3.9](../controls/pillar-3-reporting/3.9-microsoft-sentinel-integration.md) | Sentinel Integration | Technical safeguard - security monitoring |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback | Technical safeguard - quality monitoring |

**Pillar 4 - SharePoint Controls (5 controls):**

| Control | Requirement | GLBA Mapping |
|---------|-------------|--------------|
| [4.1](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | Information Access Governance | Technical safeguard - access control |
| [4.2](../controls/pillar-4-sharepoint/4.2-site-access-reviews-and-certification.md) | Site Access Reviews | Administrative safeguard - access review |
| [4.4](../controls/pillar-4-sharepoint/4.4-guest-and-external-user-access-controls.md) | Guest Access Controls | Technical safeguard - third-party access |
| [4.6](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Grounding Scope Governance | Technical safeguard - data source governance |
| [4.7](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | M365 Copilot Data Governance | Technical safeguard - M365 access controls |
| 4.8 | Item-Level Permission Scanning for Agent Knowledge Sources | Item-level access control validation for agent knowledge sources |

**Mapped controls: 52**

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
Framework provides 52 mapped controls relevant to GLBA safeguards. Implementation validation required.

---

## OCC Bulletin 2011-12 / SR 26-2 (formerly SR 11-7) - Model Risk Management

### Overview
Applies to national banks and federal savings associations. Requires governance framework for models used in business decisions.

### Applicable Controls

**Pillar 1 - Security Controls (7 controls):**

| Control | Requirement | SR 26-2 (formerly SR 11-7) Mapping |
|---------|-------------|-----------------|
| [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | Model data governance |
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | Model audit trail |
| [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime Protection | Model monitoring |
| [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Data Minimization | Model input controls |
| [1.21](../controls/pillar-1-security/1.21-adversarial-input-logging.md) | Adversarial Input Logging | Model attack detection |
| [1.22](../controls/pillar-1-security/1.22-information-barriers.md) | Information Barriers | Model information segregation |
| [1.23](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | Step-Up Authentication | Model access controls |
| [1.24](../controls/pillar-1-security/1.24-defender-ai-security-posture-management.md) | Defender AI-SPM | AI attack surface and vulnerability management |
| [1.25](../controls/pillar-1-security/1.25-mime-type-restrictions.md) | MIME Type Restrictions | Operational risk management for file inputs |
| [1.26](../controls/pillar-1-security/1.26-agent-file-upload-and-file-analysis-restrictions.md) | File Upload Restrictions | Operational risk management for file processing |
| [1.28](../controls/pillar-1-security/1.28-policy-based-agent-publishing-restrictions.md) | Publishing Restrictions | Third-party risk management and deployment validation |

| Control | Requirement | SR 26-2 (formerly SR 11-7) Mapping |
|---------|-------------|-----------------|
| [2.1](../controls/pillar-2-management/2.1-managed-environments.md) | Managed Environments | Model environment controls |
| [2.2](../controls/pillar-2-management/2.2-environment-groups-and-tier-classification.md) | Environment Groups | Model tier classification |
| [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Model change control |
| [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) | Testing and Validation | Independent model validation |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management | Primary SR 26-2 (formerly SR 11-7) framework |
| [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Vendor Risk Management | Third-party model governance |
| [2.8](../controls/pillar-2-management/2.8-access-control-and-segregation-of-duties.md) | Access Control and SoD | Model development controls |
| [2.9](../controls/pillar-2-management/2.9-agent-performance-monitoring-and-optimization.md) | Performance Monitoring | Model performance tracking |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Bias Testing | Fairness and discrimination testing |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Model governance oversight |
| [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation | Model documentation |
| [2.15](../controls/pillar-2-management/2.15-environment-routing.md) | Environment Routing | Model environment governance |
| [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) | RAG Source Integrity | Model data source validation |
| [2.17](../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-Agent Orchestration | Complex model governance |
| [2.18](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Conflict of Interest Testing | Model bias detection |
| [2.20](../controls/pillar-2-management/2.20-adversarial-testing-and-red-team-framework.md) | Adversarial Testing | Model robustness testing |
| [2.24](../controls/pillar-2-management/2.24-agent-feature-enablement-and-restriction-governance.md) | Feature Enablement Governance | Model risk management for AI capability controls |

| Control | Requirement | SR 26-2 (formerly SR 11-7) Mapping |
|---------|-------------|-----------------|
| [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Model inventory |
| [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md) | Usage Analytics | Model performance monitoring |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Model risk reporting |
| [3.4](../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | Incident Reporting | Model incident management |
| [3.6](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md) | Orphaned Agent Detection | Model lifecycle management |
| [3.7](../controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md) | Security Posture | Model security assessment |
| [3.8](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md) | Copilot Hub | Model governance dashboard |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback Loop | Model output accuracy monitoring |
| [3.11](../controls/pillar-3-reporting/3.11-centralized-agent-inventory-enforcement.md) | Centralized Inventory Enforcement | Model inventory and ongoing monitoring |
| [3.12](../controls/pillar-3-reporting/3.12-agent-governance-exception-and-override-management.md) | Exception Management | Model governance exception and override tracking |

| Control | Requirement | SR 26-2 (formerly SR 11-7) Mapping |
|---------|-------------|-----------------|
| [4.1](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md) | Information Access Governance | Model data access controls |
| [4.6](../controls/pillar-4-sharepoint/4.6-grounding-scope-governance.md) | Grounding Scope Governance | Model data source governance |
| [4.7](../controls/pillar-4-sharepoint/4.7-microsoft-365-copilot-data-governance.md) | M365 Copilot Data Governance | Model output governance |
| 4.8 | Item-Level Permission Scanning for Agent Knowledge Sources | Data governance for AI model knowledge sources |

**Mapped controls: 34**

### Model Risk Framework (SR 26-2 (formerly SR 11-7))

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
- Requires SR 26-2 (formerly SR 11-7) governance framework
- Annual third-party validation recommended
- Quarterly monitoring mandatory

### Applicability

**OCC Regulated Entities (National Banks, FSAs):**

- All Zone 3 agents using ML = Model
- SR 26-2 (formerly SR 11-7) framework required
- Annual validation mandatory

**Non-OCC Entities:**

- SR 26-2 (formerly SR 11-7) represents best practice
- Apply for Zone 3 high-risk agents
- Recommended even if not OCC-regulated

### Framework Coverage
Framework provides 34 mapped controls relevant to OCC and SR 26-2 (formerly SR 11-7) topics. OCC-specific model validation required for full compliance.

---

## Federal Reserve Guidance - Fair Lending (ECOA)

### Overview
Applies to bank holding companies and entities with lending functions. Requires fair lending practices in credit decisions.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Bias Testing | ECOA discrimination testing |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management | Credit model governance |
| [1.14](../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) | Data Minimization | Fair treatment in data usage |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Compliance oversight |

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
Framework provides 2 mapped bias-testing controls applicable to ECOA and fair lending topics. ECOA-specific testing and validation required.

---

## CFTC Rule 1.31 - Recordkeeping Requirements

### Overview
Applies to futures commission merchants (FCMs), introducing brokers, commodity trading advisors, and commodity pool operators. Requires maintenance of books and records in accordance with CFTC regulations.

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Comprehensive Audit Logging | 5-year retention (CFTC requires records for life of enterprise + 5 years) |
| [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime Protection | Security monitoring for trading systems |
| [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and Sensitivity Labels | Protection of trading data |
| [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) | Data Retention | Retention policies per CFTC requirements |
| [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Change control for trading systems |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management | Governance for algorithmic trading agents |
| [2.13](../controls/pillar-2-management/2.13-documentation-and-record-keeping.md) | Documentation and Record Keeping | Complete transaction documentation |
| [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Registry of trading-related agents |
| [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Regulatory reporting capabilities |

### Key Recordkeeping Requirements

1. **Electronic Records**
   - Records must be maintained in electronic format capable of being retrieved and produced
   - Principles-based standard requiring systems ensuring "authenticity and reliability" of records (17 CFR § 1.31(c))
   - Records must be searchable and accessible for CFTC examination

2. **Retention Period**
   - Minimum 5 years from creation
   - First 2 years: readily accessible location
   - Full retention: life of enterprise plus 5 years for certain records

3. **AI Agent Records**
   - All agent-assisted transactions must be recorded
   - Agent decision logs for trading recommendations
   - Audit trail of agent inputs and outputs
   - Model validation documentation

### Governance Framework Alignment

**Derivatives/Commodities Trading Agents (Zone 3):**

- Mandatory comprehensive audit logging
- 5+ year retention with immediate accessibility
- Systems ensuring authenticity and reliability per 17 CFR § 1.31(c)
- Complete transaction reconstruction capability
- Model risk management per SR 26-2 (formerly SR 11-7) principles

### Framework Coverage
Framework provides audit and recordkeeping controls. Organizations with CFTC-regulated entities should map these controls to specific Rule 1.31 requirements. Implementation and validation required.

!!! warning "Dual-Registrant Compliance"
    Organizations registered with both SEC and CFTC must comply with both standards:

    - **SEC Rule 17a-4(f):** WORM storage or audit-trail alternative required for securities records
    - **CFTC Rule 1.31:** Principles-based "authenticity and reliability" standard for commodities records (WORM eliminated May 2017)

    CFTC eliminated the WORM requirement in 2017; SEC maintains it. Dual-registrants need separate compliance approaches for each regulatory regime.

---

## CFPB Guidance - Algorithmic Accountability and UDAAP

### Overview
Applies to consumer financial service providers. Focuses on algorithmic accountability, bias, consumer protection, and avoidance of unfair, deceptive, or abusive acts or practices (UDAAP).

### Applicable Controls

| Control | Requirement | Mapping |
|---------|-------------|---------|
| [1.6](../controls/pillar-1-security/1.6-microsoft-purview-dspm-for-ai.md) | DSPM for AI | Consumer data protection |
| [1.8](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) | Runtime Protection | Anomaly detection |
| [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) | Bias Testing | Algorithmic bias assessment |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Algorithmic governance |
| [2.18](../controls/pillar-2-management/2.18-automated-conflict-of-interest-testing.md) | Conflict of Interest Testing | Prevent unfair recommendations |
| [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) | Customer AI Disclosure | Prevent deceptive omissions |
| [2.23](../controls/pillar-2-management/2.23-user-consent-and-ai-disclosure-enforcement.md) | User Consent and AI Disclosure | Algorithmic transparency and fair lending disclosure |
| [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) | Hallucination Feedback Loop | Prevent deceptive outputs |

### ECOA vs. UDAAP for Credit Decisions

For AI systems making **credit decisions**, the regulatory framework involves two distinct authorities:

| Authority | Primary Use | Key Requirement |
|-----------|-------------|-----------------|
| **ECOA (Regulation B)** | Credit decisions | Adverse action notification specificity (Circulars 2022-03, 2023-03) |
| **UDAAP** | All consumer products | Prohibition on unfair, deceptive, or abusive practices |

CFPB Circulars 2022-03 (May 2022) and 2023-03 (September 2023) address ECOA requirements for AI-driven credit decisions, requiring creditors to disclose specific principal reasons for adverse action even when using complex algorithms.

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
Framework addresses consumer protection topics through 6 mapped controls. CFPB-specific implementation required.

---

## SEC Regulation S-ID (Red Flags Rule)

### Overview
Identity theft prevention programs for covered accounts under 16 CFR Part 314.

### Framework Coverage
SEC Regulation S-ID is not directly addressed by this framework. Organizations deploying agents that handle customer identity verification should implement red flags detection procedures per 16 CFR Part 314.

**Related Controls:**
- [1.8 - Runtime Protection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md) - Synthetic identity detection
- [2.7 - Vendor Risk Management](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) - Identity verification service providers

---

## FDIC-Supervised Institutions

### Overview
Applies to state non-member banks, state savings associations, and insured depository institutions supervised by the Federal Deposit Insurance Corporation.

### Regulatory Alignment

FDIC-supervised institutions follow the same interagency guidance as OCC and Federal Reserve institutions:

| Guidance | FDIC Applicability | Framework Alignment |
|----------|-------------------|---------------------|
| Interagency Model Risk Guidance (SR 26-2 (formerly SR 11-7)) | Adopted by FDIC | Control 2.6, 2.11 |
| Interagency Third-Party Guidance (2023) | Joint OCC/Fed/FDIC | Control 2.7 |
| FFIEC IT Examination Handbook | Primary reference | Pillars 1-4 |
| GLBA Safeguards Rule | Required | Pillar 1 Security |

### Applicable Controls

All framework controls apply to FDIC-supervised institutions. Key controls include:

| Control | Requirement | FDIC Relevance |
|---------|-------------|----------------|
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Audit Logging | FFIEC IT Handbook - Audit and Monitoring |
| [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access/MFA | FFIEC Authentication Guidance |
| [1.15](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Encryption | FFIEC Information Security |
| [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) | Model Risk Management | Interagency SR 26-2 (formerly SR 11-7) guidance |
| [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Third-Party Risk | Interagency Third-Party Guidance (2023) |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Examination expectations |

### FFIEC IT Examination Alignment

The framework aligns with FFIEC IT Examination Handbook domains:

| FFIEC Domain | Framework Pillar | Key Controls |
|--------------|-----------------|--------------|
| Information Security | Pillar 1 | 1.5, 1.11, 1.15, 1.18 |
| Audit | Pillar 1, 3 | 1.7, 3.1, 3.3 |
| Business Continuity | Pillar 2 | [2.4](../controls/pillar-2-management/2.4-business-continuity-and-disaster-recovery.md) |
| Operations | Pillar 2 | 2.1, 2.3, 2.10 |
| Outsourcing Technology | Pillar 2 | [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) |

### Governance Framework Alignment

**FDIC-Supervised Institutions:**

- Apply the same zone-based governance as OCC/Fed institutions
- Follow interagency model risk guidance (SR 26-2 (formerly SR 11-7)) for AI agents
- Reference FFIEC IT Examination Handbook for examination preparation
- Maintain evidence for examination readiness

### Framework Coverage
Framework provides equivalent coverage to OCC/Fed institutions. All current framework controls are applicable.

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
| [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP and Sensitivity Labels | Member data protection |
| [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Audit Logging | Examination documentation |
| [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access/MFA | Authentication controls |
| [1.15](../controls/pillar-1-security/1.15-encryption-data-in-transit-and-at-rest.md) | Encryption | Member information security |
| [1.20](../controls/pillar-1-security/1.20-network-isolation-private-connectivity.md) | Network Isolation | Network security controls |
| [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md) | Change Management | Control environment |
| [2.7](../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md) | Third-Party Risk | Vendor oversight |
| [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervision | Board and management oversight |

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
All current framework controls are applicable to credit unions. Adapt based on asset size and AI agent complexity.

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
| §500.06 | Audit Trail | 1.7 Comprehensive Audit Logging, 1.21 Adversarial Input Logging |
| §500.07 | Access Privileges | 1.18 RBAC, 1.20 Network Isolation, 2.8 Segregation of Duties |
| §500.08 | Application Security | 2.5 Testing, 1.8 Runtime Protection |
| §500.10 | Cybersecurity Personnel | RACI Matrix role definitions |
| §500.11 | Third-Party Risk | 2.7 Vendor and Third-Party Risk |
| §500.12 | MFA | 1.11 Conditional Access and MFA |
| §500.14 | Training | 2.14 Training and Awareness |
| §500.15 | Encryption | 1.15 Encryption |
| §500.16 | Incident Response | 3.4 Incident Reporting |
| §500.17 | Notices to Superintendent | 3.4 Incident Reporting (escalation) |

**Note:** NYDFS Part 500 underwent significant amendments effective November 2023. Institutions should verify current requirements with legal counsel.

**2024 Updates:**

- **Dual-Signature Certification (April 15, 2024):** Annual certification must now be signed by BOTH the highest-ranking executive AND the CISO
- **AI Cybersecurity Guidance (October 16, 2024):** NYDFS issued an industry letter clarifying that existing Part 500 requirements apply to AI-related cybersecurity risks, including covered entity's use of AI, vendor AI dependencies, and AI-enabled threats (deepfakes, enhanced phishing)
- **24-Hour Extortion Reporting:** Covered entities must notify NYDFS within 24 hours of making any extortion/ransomware payment (in addition to 72-hour incident reporting)

### CCPA/CPRA (California)

**Applicability:** Institutions with California customers may be subject to CCPA/CPRA for certain data processing activities.

**GLBA Preemption:** Financial institutions subject to GLBA may have limited CCPA/CPRA obligations for GLBA-covered data. However:

- Non-GLBA data may still be subject to CCPA/CPRA
- Employee data may be subject to CPRA
- Consult legal counsel for your specific situation

The framework's data governance controls (1.5, 1.6, 1.9, 1.14) support privacy compliance but do not specifically address CCPA/CPRA requirements.

### State AI Governance Laws

Several states have enacted or are developing AI-specific legislation that may apply to financial services AI agents. Organizations should monitor these developments and assess applicability to their AI agent deployments.

#### Colorado AI Act (SB 24-205)

**Applicability:** Organizations deploying "high-risk AI systems" that make consequential decisions affecting consumers in Colorado. Effective June 30, 2026 (extended from February 1, 2026 via SB 25B-004).

| Requirement | Description | Framework Alignment |
|-------------|-------------|---------------------|
| Algorithmic Discrimination Prevention | Prevent discriminatory outcomes | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) |
| Annual Bias Audits | Regular fairness assessments | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md), [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) |
| Consumer Opt-Out Rights | Right to opt out of AI processing | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |
| Risk Management Policy | Document AI risk management | [2.6](../controls/pillar-2-management/2.6-model-risk-management-sr-26-2.md) |
| Impact Assessments | Conduct and document impact assessments | See [Colorado AI Impact Assessment Template](../playbooks/regulatory-modules/colorado-ai-impact-assessment.md) |

**High-Risk AI Systems under Colorado AI Act:**

- Systems making consequential decisions in education, employment, financial services, government services, healthcare, housing, insurance, or legal services
- Financial services organizations should assess whether customer-facing agents qualify as high-risk

!!! info "Updated February 2026"
    Effective date extended to June 30, 2026 via SB 25B-004. Prudential regulator exemption is limited in scope and does not provide blanket immunity from all Colorado AI Act requirements. Consult legal counsel for applicability to federally regulated financial institutions.

> **Note:** Proposed small business exemptions (HB 25B-1009, August 2025) were not enacted. The law applies to all developers and deployers meeting definitional thresholds, with no small business carve-outs. No implementing regulations have been issued by the Attorney General as of February 2026.

#### Texas TRAIGA (HB 149)

**Applicability:** Texas Responsible AI Governance Act applies to state agencies (comprehensive governance requirements) and private sector including FSI (intent-based prohibitions + biometric consent). Effective January 1, 2026.

**Private Sector Requirements:**

| Requirement | Description | Framework Alignment |
|-------------|-------------|---------------------|
| Intent-Based Prohibitions | Prohibited from using AI to intentionally manipulate, discriminate, or violate constitutional rights | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) |
| Biometric Consent | Informed consent required for biometric data collection and processing | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |

!!! info "Updated February 2026"
    TRAIGA is substantially narrower than Colorado's AI Act. TRAIGA imposes substantive governance requirements (disclosure, social scoring prohibition, risk assessments) on **state agencies only**. Private sector obligations are limited to intent-based prohibitions on manipulation, discrimination, and constitutional rights violations, plus biometric consent. Unlike Colorado, TRAIGA does not require private sector impact assessments or annual bias audits.

> **Consult Legal Counsel:** FSI organizations should consult legal counsel for applicability of TRAIGA's biometric provisions to voiceprint authentication and other AI-enabled identity verification systems.

#### NYC Local Law 144 - Automated Employment Decision Tools

**Applicability:** Employers using automated decision tools for employment decisions in New York City. Effective January 1, 2023 (enforcement began July 5, 2023).

**FSI Note:** Applies to FSI HR departments, not customer-facing AI agents.

| Requirement | Description | Framework Alignment |
|-------------|-------------|---------------------|
| Bias Audits | Annual third-party bias audits | [2.11](../controls/pillar-2-management/2.11-bias-testing-and-fairness-assessment.md) |
| Public Disclosure | Publish audit results summary | [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) |
| Notice to Candidates | Notify affected individuals of AI use | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |
| Alternative Procedures | Offer non-AI alternatives | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |

!!! info "Updated February 2026"
    Enforcement active since July 5, 2023 (2.5+ years). NYC DCWP actively enforcing. Employers must retain audit documentation for 3 years.

#### Illinois HB 3773 - AI Video Interview Act

**Applicability:** Employers using AI to analyze video interviews in Illinois. Effective January 1, 2026.

**FSI Note:** Applies to FSI HR departments conducting video interviews with Illinois candidates. Does NOT apply to customer-facing AI agents.

| Requirement | Description | Framework Alignment |
|-------------|-------------|---------------------|
| Notice to Applicants | Notify applicants before interview that AI will be used | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |
| AI Explanation | Explain how AI works and what characteristics are evaluated | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |
| Consent | Obtain applicant consent before AI analysis | [2.19](../controls/pillar-2-management/2.19-customer-ai-disclosure-and-transparency.md) |
| Video Sharing Limits | Limit sharing to persons evaluating candidate fitness | [1.2](../controls/pillar-1-security/1.2-agent-registry-and-integrated-apps-management.md) |
| Deletion Rights | Delete videos within 30 days of applicant request | [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |

> **Note:** Unlike NYC Local Law 144, Illinois HB 3773 does NOT require bias audits or public disclosure of audit results. Illinois law focuses on transparency and consent for AI video interview analysis only.

### Governance Framework Alignment for State AI Laws

**Customer-Facing Financial AI Agents:**

Organizations should consider the following when deploying AI agents that interact with customers in states with AI legislation:

1. **Bias Testing:** Implement regular fairness assessments per Control 2.11
2. **Transparency:** Disclose AI use and decision factors per Control 2.19
3. **Human Escalation:** Provide clear paths to human review per Control 2.12
4. **Documentation:** Maintain impact assessments and audit documentation per Control 2.6
5. **Incident Response:** Report AI-related incidents per Control 3.4

#### California AI Laws

**Current Status:** As of February 2026, California has not enacted comprehensive AI-specific legislation beyond CCPA/CPRA consumer privacy requirements.

**SB 1047 (Safe and Secure Innovation for Frontier Artificial Intelligence Models Act):** Vetoed by Governor Gavin Newsom on September 29, 2024. This law is NOT in effect.

**CCPA/CPRA:** Financial institutions should note GLBA preemption for financial data. See CCPA/CPRA section above for details.

!!! info "Updated February 2026"
    California continues to consider AI safety, transparency, and accountability bills. Organizations should monitor California's active AI legislative agenda. Consult legal counsel for applicability.

**Monitoring Requirement:**

The state AI regulatory landscape is evolving rapidly. Organizations should:

- Monitor legislative developments in states where they operate
- Assess new laws for applicability to AI agent deployments
- Update governance procedures as requirements change
- Consult legal counsel for state-specific compliance strategies

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
| FINRA 4511 | 62/72 | 86% | Full coverage - implementation required |
| FINRA 3110 | 8/72 | 11% | Partial - supervision focus |
| FINRA 3110/2111 (AI) | 11/72 | 15% | Partial - supervision/suitability focus |
| SEC 17a-3/4 | 50/72 | 69% | Substantial coverage |
| SEC Rule 10b-5 / Reg BI | 7/72 | 10% | Limited - fairness + disclosure focus |
| SEC Marketing Rule (206(4)-1) | 5/72 | 7% | AI marketing claims - Control 2.21 |
| SOX 302/404 | 44/72 | 61% | Substantial coverage |
| GLBA 501-505 | 52/72 | 72% | Substantial coverage |
| OCC 2011-12 | 34/72 | 47% | Partial - model risk focus |
| Fed SR 26-2 (formerly SR 11-7) | 34/72 | 47% | Partial - model risk focus |
| Fed ECOA | 3/72 | 4% | Minimal - bias testing only |
| CFPB / UDAAP | 7/72 | 10% | Consumer protection + disclosure focus |
| CFTC Rule 1.31 | 9/72 | 13% | Recordkeeping for derivatives/commodities |
| FDIC (Interagency) | 63/72 | 88% | Full applicability; align to interagency guidance |
| NCUA Part 748 | 51/72 | 71% | Security program alignment |
| NYDFS Part 500 | 45/72 | 63% | State-level awareness |
| NAIC Model Law | 41/72 | 57% | Insurance awareness |
| State AI Laws | 6/72 | 8% | Emerging - transparency, bias, human review |

> **Note:** Coverage percentages indicate which framework controls address aspects of each regulation. Actual compliance requires implementation, validation, and ongoing maintenance. Consult legal counsel for regulatory interpretation. See [Disclaimer](../disclaimer.md).

---

## How to Use This Document

1. **Find your primary regulation** in the list above
2. **Review applicable controls** for your regulation
3. **Check governance zone** alignment (Zone 2 vs Zone 3 requirements)
4. **Reference individual control files** for detailed implementation
5. **Document compliance evidence** for audit purposes

---

## FINOS AI Governance Framework (AIGF v2.0)

### Overview

The [FINOS AI Governance Framework v2.0](https://air-governance-framework.finos.org) (released November 11, 2025) is an open-source governance framework developed by the Fintech Open Source Foundation specifically for AI systems in financial services. Version 2.0 introduces **46 agentic AI-specific risks** with enhanced mitigation guidance.

!!! info "AIGF v2.0 Update (November 2025)"
    Version 2.0 expanded the framework from traditional AI governance to include comprehensive agentic AI risk categories:

    - **Action Autonomy Risks** (12 risks) - Uncontrolled agent actions, scope creep, unauthorized transactions
    - **Tool Integration Risks** (8 risks) - API vulnerabilities, tool chain exploitation, connector abuse
    - **Multi-Agent Risks** (9 risks) - Orchestration failures, agent collusion, coordination gaps
    - **Data Access Risks** (10 risks) - Overprivileged access, data exfiltration, cross-boundary violations
    - **Governance Gaps** (7 risks) - Audit trail incompleteness, supervision blindspots, compliance drift

### Key Risk: Agent Action Authorization Bypass

FINOS identifies that agentic AI systems may:

- Bypass intended authorization controls
- Perform actions beyond designated scope
- Execute unauthorized financial transactions
- Access restricted data
- Violate business logic constraints
- Exploit API vulnerabilities
- Escalate privileges through tool chains
- Circumvent approval workflows

### FSI-AgentGov Alignment

| FINOS AIGF v2.0 Risk Category | FSI-AgentGov Controls | Coverage |
|-------------------------------|----------------------|----------|
| Authorization Bypass | 1.14 (Scope Control), 1.18 (RBAC), [AAM Template](../playbooks/governance-operations/action-authorization-matrix.md) | Full |
| Privilege Escalation | 1.4 (ACP), 2.17 (Orchestration Limits) | Full |
| Data Access Violations | 1.5 (DLP), 4.1-4.9 (SharePoint Controls) | Full |
| Audit Trail Gaps | 1.7 (Audit Logging), 3.2 (Usage Analytics) | Full |
| Workflow Circumvention | [HITL Triggers](../playbooks/advanced-implementations/human-in-the-loop-triggers.md), 2.12 (Supervision) | Full |
| Multi-Agent Coordination | 2.17 (Orchestration Limits), 2.12 (Supervision) | Full |
| Tool Chain Exploitation | 1.4 (ACP), 1.8 (Runtime Protection) | Full |

### Framework Coverage

The FSI-AgentGov framework addresses FINOS AIGF v2.0 risks through defense-in-depth controls across all four pillars. The Agent Action Authorization Matrix (AAM) template specifically addresses authorization bypass risks.

**Reference:** [FINOS AI & Readiness Governance Framework v2.0](https://air-governance-framework.finos.org)

---

*FSI Agent Governance Framework v1.2 - February 2026*
