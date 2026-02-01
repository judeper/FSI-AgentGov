# Solutions Coverage Gap Analysis

Analysis of FSI-AgentGov-Solutions coverage against the 62-control framework, identifying high-risk gaps and implementation prioritization guidance.

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Controls | 62 |
| Controls with Deployable Solutions | 10 |
| Controls Without Solutions | 52 |
| Overall Solution Coverage | 16.1% |

!!! info "Important Context"
    Many "gaps" are addressed by **native Microsoft 365 and Power Platform features** that require portal configuration, not custom solutions. This analysis focuses specifically on deployable automation from the [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) repository. A control without a deployable solution is not necessarily unimplemented—it may be fully addressed through portal configuration following the control's playbooks.

---

## Current Solution Coverage

### Covered Controls (10 of 62)

| Control ID | Control Name | Solution |
|------------|--------------|----------|
| 1.5 | DLP and Sensitivity Labels | [Deny Event Correlation Report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) |
| 1.7 | Comprehensive Audit Logging | [Deny Event Correlation Report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) |
| 1.11 | Conditional Access and MFA | [Conditional Access Automation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation) |
| 2.1 | Managed Environments | [Environment Lifecycle Management](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management) |
| 2.2 | Environment Groups | [Environment Lifecycle Management](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management) |
| 2.3 | Change Management | [Message Center Monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor), [Pipeline Governance Cleanup](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup) |
| 2.10 | Patch Management | [Message Center Monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor) |
| 2.12 | Supervision and Oversight | [FINRA Supervision Workflow](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow) |
| 2.15 | Environment Routing | [Environment Lifecycle Management](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management) |
| 3.4 | Incident Reporting | [Deny Event Correlation Report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report) |

### Coverage by Pillar

| Pillar | Total Controls | Covered | Gaps | Coverage |
|--------|----------------|---------|------|----------|
| **Pillar 1 - Security** | 24 | 3 | 21 | 12.5% |
| **Pillar 2 - Management** | 21 | 6 | 15 | 28.6% |
| **Pillar 3 - Reporting** | 10 | 1 | 9 | 10.0% |
| **Pillar 4 - SharePoint** | 7 | 0 | 7 | 0.0% |
| **Total** | 62 | 10 | 52 | 16.1% |

---

## Gap Classification

Not all gaps require custom solutions. Understanding the gap type helps prioritize development efforts.

### Category 1: Native Microsoft Features (Portal Configuration)

These controls are fully addressed through Microsoft admin portal configuration. No custom solution is needed—follow the control's playbooks for implementation.

| Control | Control Name | Native Feature |
|---------|--------------|----------------|
| 1.1 | Restrict Agent Publishing | Power Platform Admin Center settings |
| 1.2 | Agent Registry | Integrated Apps management in M365 Admin |
| 1.4 | Advanced Connector Policies | PPAC connector classification |
| 1.6 | DSPM for AI | Purview compliance portal |
| 1.8 | Runtime Protection | Defender for Cloud Apps |
| 1.9 | Data Retention | Purview retention policies |
| 1.10 | Communication Compliance | Purview Communication Compliance |
| ~~1.11~~ | ~~Conditional Access~~ | ~~Entra ID Conditional Access policies~~ **Now has [Conditional Access Automation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)** |
| 1.12 | Insider Risk Detection | Purview Insider Risk Management |
| 1.13 | Sensitive Information Types | Purview SIT configuration |
| 1.15 | Encryption | Microsoft-managed encryption (default) |
| 1.16 | Information Rights Management | Purview sensitivity labels with IRM |
| 1.17 | Endpoint DLP | Purview Endpoint DLP |
| 1.18 | Application-Level RBAC | Entra ID app roles |
| 1.19 | eDiscovery | Purview eDiscovery |
| 1.22 | Information Barriers | Purview Information Barriers |
| 1.24 | Defender AI-SPM | Defender for Cloud |
| 3.1 | Agent Inventory | PPAC + CoE Starter Kit |
| 3.2 | Usage Analytics | PPAC Analytics |
| 3.7 | PPAC Security Posture | PPAC native dashboard |
| 3.8 | Copilot Hub | M365 Admin Center Copilot Hub |
| 4.1-4.7 | SharePoint Controls | SharePoint Advanced Management |

### Category 2: Custom Solution Recommended

These controls would benefit from custom automation beyond native features. Prioritize based on Zone 3/Tier 1 risk.

| Control | Control Name | Gap Type | Priority |
|---------|--------------|----------|----------|
| 1.3 | SharePoint Content Governance | Automated permission scanning | Medium |
| 1.14 | Data Minimization | Scope drift detection automation | High |
| 1.20 | Network Isolation | Connectivity validation automation | Medium |
| 1.21 | Adversarial Input Logging | Centralized attack pattern analysis | High |
| 1.23 | Step-Up Authentication | Auth challenge orchestration | Medium |
| 2.4 | Business Continuity | Automated DR testing | Medium |
| 2.5 | Testing and Validation | Test orchestration framework | High |
| 2.8 | Segregation of Duties | Role conflict detection | High |
| 2.9 | Performance Monitoring | Custom KPI dashboards | Medium |
| 2.16 | RAG Source Integrity | Source validation automation | High |
| 2.17 | Multi-Agent Orchestration | Orchestration limit enforcement | Medium |
| 2.18 | Conflict of Interest Testing | Automated COI detection | High |
| 3.3 | Compliance Reporting | Aggregated compliance dashboard | High |
| 3.5 | Cost Allocation | Chargeback automation | Medium |
| 3.6 | Orphaned Agent Detection | Automated remediation workflows | Medium |
| 3.9 | Sentinel Integration | Custom data connectors | High |
| 3.10 | Hallucination Feedback | Feedback aggregation pipeline | Medium |

### Category 3: Process/Documentation Controls

These controls are inherently process-based and cannot be fully automated. They require documented procedures, training, and human judgment.

| Control | Control Name | Why Not Automatable |
|---------|--------------|---------------------|
| 2.6 | Model Risk Management | OCC 2011-12 requires human model validation and governance committee oversight |
| 2.7 | Vendor Risk Management | Third-party assessments require human judgment and negotiation |
| 2.11 | Bias Testing | Fairness assessment requires domain expertise and ethical judgment |
| 2.12 | Supervision and Oversight | ~~FINRA 3110 requires designated supervisory principals~~ **Now has [FINRA Supervision Workflow](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow)** - Automates routing and tracking while human review remains required |
| 2.13 | Documentation | Record-keeping is a process discipline |
| 2.14 | Training Program | Human learning and awareness |
| 2.19 | AI Disclosure | Customer communication decisions |
| 2.20 | Adversarial Testing | Red team exercises require human creativity |
| 2.21 | AI Marketing Claims | Legal/compliance review of marketing materials |

---

## High-Risk Gaps (Zone 3 / Tier 1)

These 32 controls apply to Zone 3 (Enterprise Managed) agents and Tier 1 (Critical) classifications. Gaps in these controls present elevated regulatory and operational risk.

### Zone 3 Controls Without Solutions

| Control | Control Name | Gap Category | Regulatory Impact |
|---------|--------------|--------------|-------------------|
| 1.3 | SharePoint Content Governance | Custom Recommended | Data exposure risk |
| 1.4 | Advanced Connector Policies | Native Feature | - |
| 1.6 | DSPM for AI | Native Feature | - |
| 1.8 | Runtime Protection | Native Feature | - |
| 1.9 | Data Retention | Native Feature | SEC 17a-4, FINRA 4511 |
| 1.10 | Communication Compliance | Native Feature | FINRA 3110 |
| ~~1.11~~ | ~~Conditional Access~~ | ~~Native Feature~~ | **Now has [Conditional Access Automation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)** |
| 1.12 | Insider Risk Detection | Native Feature | - |
| 1.14 | Data Minimization | Custom Recommended | Data exposure risk |
| 1.19 | eDiscovery | Native Feature | SEC 17a-4, FINRA 4511 |
| 1.20 | Network Isolation | Custom Recommended | Security posture |
| 1.21 | Adversarial Input Logging | Custom Recommended | Threat detection |
| 1.22 | Information Barriers | Native Feature | FINRA Rule 5110 |
| 1.23 | Step-Up Authentication | Custom Recommended | Access control |
| 1.24 | Defender AI-SPM | Native Feature | - |
| 2.4 | Business Continuity | Custom Recommended | Operational resilience |
| 2.5 | Testing and Validation | Custom Recommended | FINRA Notice 15-09 |
| 2.6 | Model Risk Management | Process Control | OCC 2011-12, SR 11-7 |
| 2.7 | Vendor Risk Management | Process Control | OCC 2013-29 |
| 2.8 | Segregation of Duties | Custom Recommended | SOX 404 |
| 2.9 | Performance Monitoring | Custom Recommended | SLA compliance |
| 2.11 | Bias Testing | Process Control | ECOA, CFPB |
| 2.13 | Documentation | Process Control | SEC 17a-3 |
| 2.16 | RAG Source Integrity | Custom Recommended | Data accuracy |
| 2.17 | Multi-Agent Orchestration | Custom Recommended | Complexity risk |
| 2.18 | Conflict of Interest Testing | Custom Recommended | FINRA Rule 2111 |
| 2.19 | AI Disclosure | Process Control | CFPB guidance |
| 2.20 | Adversarial Testing | Process Control | Security posture |
| 3.3 | Compliance Reporting | Custom Recommended | Audit readiness |
| 3.9 | Sentinel Integration | Custom Recommended | SIEM coverage |
| 3.10 | Hallucination Feedback | Custom Recommended | Output quality |

---

## Critical Regulatory Gaps

One control has significant regulatory implications with no native Microsoft feature fully addressing it.

### FINRA Rule 3110 - Supervision (Control 2.12) - ADDRESSED

!!! success "Solution Available"
    The [FINRA Supervision Workflow](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow) solution provides automated routing and tracking for supervisory review while maintaining human oversight as required by regulation.

**Regulation:** FINRA Rule 3110 requires member firms to establish and maintain a system to supervise the activities of each associated person that is reasonably designed to achieve compliance.

**Solution:** The [FINRA Supervision Workflow](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow) solution automates:

- Queue management for flagged AI agent outputs
- Routing to designated supervisory principals based on zone/tier
- SLA monitoring with automatic escalation
- Evidence collection with SHA-256 integrity hashing
- Integration with Communication Compliance for content detection

**Remaining Human Requirements:**

1. Designate supervisory principals with AI agent oversight responsibilities
2. Document supervision procedures in Written Supervisory Procedures (WSP)
3. Perform actual content review and approval decisions
4. Configure zone/tier-specific review percentages and SLAs

**See:** [Control 2.12 Playbooks](../playbooks/control-implementations/2.12/portal-walkthrough.md)

### OCC 2011-12 / SR 11-7 - Model Risk Management (Control 2.6)

**Regulation:** OCC Bulletin 2011-12 and Fed SR 11-7 require banks to establish a model risk management framework including model validation, ongoing monitoring, and governance.

**Gap:** Microsoft provides infrastructure for deploying AI agents, not a pre-built model risk management solution. MRM requires human judgment and governance structures.

**Mitigation:**

1. Document AI agents in your model inventory
2. Classify agents by materiality (Tier 1/2/3)
3. Establish model validation procedures appropriate to agent complexity
4. Define model owner and validator roles with appropriate independence
5. Implement ongoing performance monitoring (Control 2.9)
6. Maintain model documentation per SR 11-7 requirements

**See:** [Control 2.6 Playbooks](../playbooks/control-implementations/2.6/portal-walkthrough.md)

---

## Implementation Roadmap Priority

Recommended prioritization for addressing solution gaps, organized by quarter. Effort estimates assume a dedicated implementation team with Power Platform and Azure experience.

### Phase 1: Q1 2026 (Foundation)

Focus on controls with highest regulatory impact and broadest applicability.

| Priority | Control | Action | Approach | Effort |
|----------|---------|--------|----------|--------|
| 1 | 2.12 | ~~Configure supervision workflow~~ **DONE** - Deploy [FINRA Supervision Workflow](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow) | Solution Available | - |
| 2 | 2.6 | Establish MRM governance for AI agents; create model inventory | Process + Documentation | 3 weeks |
| 3 | 1.22 | Configure Information Barriers for research/trading separation | Portal Configuration | 1 week |
| 4 | 1.11 | ~~Deploy Conditional Access policies for AI app access~~ **DONE** - Deploy [Conditional Access Automation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation) | Solution Available | - |
| 5 | 3.3 | Build compliance reporting dashboard using existing audit data | Custom Development | 4 weeks |

### Phase 2: Q2 2026 (Hardening)

Extend coverage to operational excellence controls.

| Priority | Control | Action | Approach | Effort |
|----------|---------|--------|----------|--------|
| 1 | 2.5 | Implement automated testing framework for Zone 3 agents | Custom Development | 6 weeks |
| 2 | 2.8 | Build role conflict detection for Maker/Checker enforcement | Custom Development | 3 weeks |
| 3 | 1.14 | Deploy scope drift detection automation | Custom Development | 4 weeks |
| 4 | 3.9 | Configure Sentinel MCP Server for agent telemetry | Portal + Integration | 2 weeks |
| 5 | 2.16 | Implement RAG source validation checks | Custom Development | 4 weeks |

### Phase 3: Q3 2026 (Optimization)

Address remaining gaps and enhance automation maturity.

| Priority | Control | Action | Approach | Effort |
|----------|---------|--------|----------|--------|
| 1 | 2.18 | Deploy automated conflict of interest testing | Custom Development | 4 weeks |
| 2 | 1.21 | Centralize adversarial input analysis | Custom Development | 3 weeks |
| 3 | 3.10 | Build hallucination feedback aggregation pipeline | Custom Development | 4 weeks |
| 4 | 2.4 | Implement automated DR testing workflows | Custom Development | 5 weeks |
| 5 | 3.5 | Deploy cost allocation and chargeback automation | Custom Development | 3 weeks |

### Phase 4: Q4 2026 (Maturity)

Achieve comprehensive automation coverage and operational excellence.

| Priority | Control | Action | Approach | Effort |
|----------|---------|--------|----------|--------|
| 1 | 1.3 | Automated SharePoint permission scanning | Custom Development | 4 weeks |
| 2 | 1.20 | Network isolation connectivity validation | Custom Development | 3 weeks |
| 3 | 2.17 | Multi-agent orchestration limit enforcement | Custom Development | 4 weeks |
| 4 | 3.6 | Orphaned agent automated remediation | Custom Development | 3 weeks |
| 5 | 1.23 | Step-up authentication challenge orchestration | Custom Development | 4 weeks |

---

## Solution Development Backlog

Priority solutions for FSI-AgentGov-Solutions repository development, addressing critical regulatory and operational gaps.

### P0 - Critical (Q1-Q2 2026)

| Solution | Target Control | Description | Status |
|----------|---------------|-------------|--------|
| ~~**finra-supervision-workflow**~~ | 2.12 | ~~Automated supervision queue for AI agent outputs~~ | **[RELEASED v1.0.0](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow)** |
| ~~**conditional-access-automation**~~ | 1.11 | ~~Entra ID Conditional Access policy templates and deployment automation for AI workloads~~ | **[RELEASED v1.0.0](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)** |
| **compliance-dashboard** | 3.3 | Aggregated compliance reporting across all 62 controls with zone-based filtering | Planned |

### P1 - High (Q2-Q3 2026)

| Solution | Target Control | Description | Regulatory Driver |
|----------|---------------|-------------|-------------------|
| **segregation-detector** | 2.8 | Role conflict detection for Maker/Checker enforcement in agent pipelines | SOX 404 |
| **scope-drift-monitor** | 1.14 | Automated detection of agent data access beyond declared scope | Data Minimization |
| **rag-source-validator** | 2.16 | Integrity validation for RAG knowledge sources with change detection | Data Accuracy |

### P2 - Medium (Q3-Q4 2026)

| Solution | Target Control | Description | Operational Driver |
|----------|---------------|-------------|-------------------|
| **coi-testing-automation** | 2.18 | Automated conflict of interest testing for agent recommendations | FINRA 2111 |
| **hallucination-tracker** | 3.10 | Feedback aggregation pipeline for hallucination detection patterns | Output Quality |
| **dr-testing-framework** | 2.4 | Automated disaster recovery testing for agent infrastructure | Resilience |

---

## Duplicate Coverage Analysis

Some controls are covered by multiple solutions, providing redundancy.

### Control 2.3 - Change Management

| Solution | Coverage Aspect |
|----------|-----------------|
| Message Center Monitor | Platform change notifications from Microsoft |
| Pipeline Governance Cleanup | Internal deployment pipeline governance |

**Recommendation:** Deploy both solutions. They address different aspects of change management—external platform changes vs. internal deployment governance.

### Controls 1.5 and 1.7

| Solution | Controls |
|----------|----------|
| Deny Event Correlation Report | 1.5 (DLP), 1.7 (Audit), 3.4 (Incident) |

**Note:** The Deny Event Correlation Report provides unified visibility across multiple controls by correlating events from Purview Audit, DLP, and Application Insights.

---

## Next Steps

1. **Assess current state** - For each gap, determine if native features are already configured
2. **Prioritize by zone** - Focus on Zone 3 gaps first for enterprise agents
3. **Leverage existing solutions** - Deploy available FSI-AgentGov-Solutions before building custom
4. **Document process controls** - For Category 3 controls, focus on procedures and training
5. **Track progress** - Use the implementation roadmap to measure gap closure

---

## Related Resources

- [Solutions Index](solutions-index.md) - Complete FSI-AgentGov-Solutions catalog
- [Solutions Integration](../framework/solutions-integration.md) - How solutions map to framework pillars
- [Solutions Architecture Guide](solutions-architecture-guide.md) - Enterprise scalability patterns
- [CONTROL-INDEX](../controls/CONTROL-INDEX.md) - Full control reference with implementation links
- [Adoption Roadmap](../framework/adoption-roadmap.md) - Phased implementation guidance

---

*FSI Agent Governance Framework v1.2.35 - February 2026*
