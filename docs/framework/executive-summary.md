# Executive Summary

A board-level overview of AI agent governance for US financial services organizations.

---

## The AI Agent Opportunity and Risk

Microsoft 365 AI agents (Copilot Studio, Agent Builder) enable financial institutions to automate customer service, streamline operations, and enhance employee productivity. However, these capabilities introduce governance challenges that require structured oversight.

**Key Business Drivers:**

- Operational efficiency through automated workflows
- Enhanced customer experience with 24/7 availability
- Improved employee productivity with AI assistance
- Competitive positioning in digital transformation

**Key Risk Considerations:**

- Regulatory scrutiny of AI-generated outputs affecting customers
- Data protection for sensitive financial information
- Model risk from AI decision-making
- Reputational risk from AI failures or bias

---

## Top 10 AI Agent Risks for Financial Services

| Rank | Risk | Impact | Key Mitigating Controls |
|------|------|--------|------------------------|
| 1 | **Unauthorized Data Access** | Customer PII exposure, regulatory violation | DLP policies (1.5), Sensitivity labels (1.5), DSPM for AI (1.6) |
| 2 | **Inadequate Supervision** | FINRA 3110 violation, unsuitable recommendations | Supervision controls (2.12), Human-in-the-loop (playbooks) |
| 3 | **Records Retention Failure** | SEC 17a-4/FINRA 4511 violation | Audit logging (1.7), Retention policies (1.9) |
| 4 | **Model Bias/Fairness Issues** | Fair lending violations, reputational harm | Bias testing (2.11), Model risk management (2.6) |
| 5 | **Hallucination/Inaccuracy** | Customer harm, regulatory exposure | RAG validation (2.16), Feedback loops (3.10) |
| 6 | **Unauthorized Agent Publishing** | Shadow AI, uncontrolled risk | Publishing restrictions (1.1), Managed environments (2.1) |
| 7 | **Excessive Data Grounding** | Oversharing, data leakage | Grounding scope (4.6), SharePoint governance (4.1) |
| 8 | **Lack of Audit Trail** | Examination failure, inability to investigate | Comprehensive logging (1.7), eDiscovery (1.19) |
| 9 | **Insufficient Change Control** | Unauthorized modifications, instability | Change management (2.3), ALM pipelines |
| 10 | **Third-Party Model Risk** | Vendor dependency, unexpected behavior | Vendor management (2.7), Testing (2.5) |

---

## Regulatory Landscape Summary

### Primary US Financial Regulations

| Regulation | Issuer | AI Agent Relevance | Framework Coverage |
|------------|--------|-------------------|-------------------|
| **FINRA 4511** | FINRA | Books and records for agent interactions | Controls 1.7, 1.9, 3.1, 3.3 |
| **FINRA 3110** | FINRA | Supervision of AI-assisted activities | Controls 2.12, 2.17, 2.18 |
| **FINRA 25-07** | FINRA | AI model risk and governance guidance | Controls 2.6, 2.11, 3.10 |
| **SEC 17a-3/4** | SEC | Recordkeeping requirements | Controls 1.7, 1.9, 2.13 |
| **SOX 302/404** | Congress | Internal controls over financial reporting | Controls 1.7, 2.3, 3.3 |
| **GLBA 501(b)** | FTC | Safeguards for customer information | Controls 1.5, 1.11, 1.15 |
| **OCC 2011-12** | OCC | Model risk management | Controls 2.6, 2.11 |
| **Fed SR 11-7** | Federal Reserve | Model risk management | Controls 2.6, 2.11 |

### Regulatory Heatmap by Zone

| Regulation | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|------------|------------------|---------------|---------------------|
| FINRA 4511 | Not applicable | Moderate | Full compliance |
| FINRA 3110 | Not applicable | Basic supervision | Comprehensive |
| SEC 17a-3/4 | Not applicable | If applicable | Full compliance |
| SOX 302/404 | Not applicable | Limited | Full compliance |
| GLBA 501(b) | Not applicable | If PII accessed | Full compliance |
| OCC 2011-12 | Not applicable | Not applicable | Full compliance |

**Note:** Zone 1 agents are intended for unregulated personal productivity scenarios and are generally not the focus of regulatory examination, provided their use remains restricted to unregulated activities. Any spillover into customer or trading data would move such agents into Zone 2 or 3.

---

## Governance Model Summary

### Four Pillars

```
+-------------------+-------------------+-------------------+-------------------+
|     PILLAR 1      |     PILLAR 2      |     PILLAR 3      |     PILLAR 4      |
|     Security      |    Management     |    Reporting      |    SharePoint     |
|   (23 controls)   |   (21 controls)   |   (10 controls)   |   (7 controls)    |
+-------------------+-------------------+-------------------+-------------------+
| DLP, Audit,       | Lifecycle, MRM,   | Inventory,        | Access, Grounding |
| Encryption, MFA,  | Testing, Change,  | Usage, PPAC,      | Retention,        |
| eDiscovery        | HITL, Supervision | Sentinel, Alerts  | External Access   |
+-------------------+-------------------+-------------------+-------------------+
```

**61 Total Controls** across four pillars addressing security, management, reporting, and SharePoint-specific governance.

### Three Governance Zones

| Zone | Risk Level | Data Access | Approval | Audit Retention |
|------|------------|-------------|----------|-----------------|
| **Zone 1: Personal** | Low | M365 Graph only | Self-service | 30 days |
| **Zone 2: Team** | Medium | Internal data | Manager | 1 year |
| **Zone 3: Enterprise** | High | Regulated data | Governance Committee | 10 years |

### Governance Maturity Levels

Each control supports three implementation levels:

- **Baseline:** Minimum viable governance for initial deployment
- **Recommended:** Best practices for most production scenarios
- **Regulated:** Comprehensive controls for Zone 3 and high-risk agents

---

## High-Level RACI

| Activity | AI Gov Lead | Compliance | CISO | Legal | Board |
|----------|-------------|------------|------|-------|-------|
| Framework ownership | **A** | C | C | I | I |
| Zone 3 agent approval | R | **A** | A | A | I |
| Security policy | C | C | **A** | I | I |
| Regulatory alignment | C | **A** | C | C | I |
| Incident escalation | R | R | R | C | **A** |
| Annual governance review | R | **A** | C | C | A |

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

See [Operating Model](operating-model.md) for complete RACI matrices.

---

## Key Governance Metrics

### Board-Level KPIs

| Metric | Target | Measurement Frequency |
|--------|--------|----------------------|
| Zone 3 agent compliance rate | 100% | Monthly |
| Critical control gaps | 0 | Quarterly |
| Regulatory examination findings | 0 critical | Annual |
| Mean time to remediation (critical) | <7 days | Per incident |
| Governance training completion | 100% | Annual |

### Operational Metrics

| Metric | Zone 2 Target | Zone 3 Target |
|--------|---------------|---------------|
| Agent inventory accuracy | 95% | 100% |
| Audit log completeness | 99% | 99.9% |
| Change approval compliance | 95% | 100% |
| Incident response SLA | 24 hours | 4 hours |

---

## Investment Requirements

### Technology Investment

| Component | Purpose | Licensing |
|-----------|---------|-----------|
| Microsoft 365 E5 | Core platform, compliance features | Required |
| Power Platform Premium | Managed environments, DLP | Required for Zone 2-3 |
| Microsoft Purview | Data governance, eDiscovery | Included in E5 |
| Microsoft Sentinel | Advanced security monitoring | Optional (Zone 3 recommended) |

### Organizational Investment

| Role | Responsibility | FTE Estimate |
|------|----------------|--------------|
| AI Governance Lead | Framework ownership, committee chair | 0.5-1.0 FTE |
| Power Platform Admin | Technical implementation | 0.25-0.5 FTE |
| Compliance Analyst | Monitoring, reporting | 0.25-0.5 FTE |

**Note:** FTE estimates scale with agent deployment volume and complexity.

---

## Implementation Roadmap Summary

### Phase 0: Foundation (0-60 days)

- Establish AI Governance Committee
- Deploy core controls: 1.1, 1.5, 2.1, 2.3, 3.1, 4.1
- Implement Zone 1 and Zone 2 environments
- Complete baseline training

### Phase 1: Production Readiness (2-6 months)

- Implement segregation of duties (2.8)
- Enable comprehensive reporting (3.1-3.5)
- Deploy Zone 3 governance structure
- Conduct first governance review

### Phase 2: Advanced Governance (6-12 months)

- Implement runtime protection (1.8)
- Deploy adversarial testing (2.20)
- Enable Sentinel integration (3.9)
- Achieve steady-state operations

See [Adoption Roadmap](adoption-roadmap.md) for detailed implementation guidance.

---

## Examination Readiness

### Key Artifacts for Examiners

| Artifact | Location | Retention |
|----------|----------|-----------|
| Agent inventory | Control 3.1 | Current + 7 years |
| Approval records | Governance committee minutes | 7 years |
| Audit logs | Purview Audit | Per zone requirements |
| Incident reports | Incident management system | 7 years |
| Training records | HR/LMS system | 7 years |
| Governance review minutes | SharePoint Compliance Library | 10 years |

### Examination Response Process

1. Receive information request from examiner
2. Compliance Officer coordinates response
3. AI Governance Lead provides technical artifacts
4. Legal reviews before submission
5. Document all interactions

See [Governance Cadence](governance-cadence.md) for examination preparation checklists.

---

## Questions for Board Discussion

1. **Risk Appetite:** What level of AI agent risk is acceptable for customer-facing use cases?
2. **Investment:** Are current technology and staffing investments adequate for AI governance?
3. **Metrics:** What governance metrics should be reported to the board quarterly?
4. **Incidents:** What incident thresholds require board notification?
5. **Strategy:** How does AI agent governance align with broader digital transformation strategy?

---

## Next Steps for Executives

1. **Review** this summary and [Zones and Tiers](zones-and-tiers.md)
2. **Approve** governance committee charter and membership
3. **Allocate** resources per [Adoption Roadmap](adoption-roadmap.md)
4. **Establish** board reporting cadence for AI governance metrics
5. **Schedule** annual governance review participation

---

## Disclaimer

This framework provides governance guidance and does not constitute legal, regulatory, or compliance advice. Organizations should validate all controls against their specific regulatory obligations and consult legal counsel for regulatory interpretation.

---

*FSI Agent Governance Framework v1.1 - January 2026*
