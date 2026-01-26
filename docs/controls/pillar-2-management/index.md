# Pillar 2: Management Controls

Ensure operational excellence, risk management, and reliable agent lifecycle management.

## Overview

Pillar 2 governs the operational processes required to manage AI agents throughout their lifecycle—from initial development through testing, deployment, monitoring, and eventual retirement. These 21 controls establish the governance framework for change management, model risk, vendor oversight, multi-agent orchestration, customer disclosure, and ongoing supervision required by financial regulators.

**Primary Regulatory Alignment:** OCC 2011-12 / Fed SR 11-7 (model risk), FINRA 3110 (supervision), FINRA 25-07 (AI fairness), SOX 302/404 (internal controls)

**Control Categories:**

| Category | Controls | Focus |
|----------|----------|-------|
| Environment Governance | 2.1-2.2, 2.15 | Managed environments, groups, routing |
| Lifecycle Management | 2.3-2.5, 2.10 | Change control, BCDR, testing, patching |
| Risk Management | 2.6-2.8, 2.16-2.18 | Model risk, vendor risk, RAG validation, orchestration, conflict testing |
| Oversight & Compliance | 2.9, 2.11-2.14 | Performance monitoring, bias testing, supervision, training |
| Customer Transparency | 2.19 | AI disclosure and human escalation |

!!! note
    Controls 2.6 and 2.11 address model risk management guidance (OCC 2011-12 / SR 11-7) but cover
    qualitative controls only. Organizations using AI agents for credit decisions or trading should
    supplement with comprehensive quantitative model validation programs.

## Controls
- [2.1 Managed Environments](2.1-managed-environments.md)
- [2.2 Environment Groups and Tier Classification](2.2-environment-groups-and-tier-classification.md)
- [2.3 Change Management and Release Planning](2.3-change-management-and-release-planning.md)
- [2.4 Business Continuity and Disaster Recovery](2.4-business-continuity-and-disaster-recovery.md)
- [2.5 Testing, Validation, and Quality Assurance](2.5-testing-validation-and-quality-assurance.md)
- [2.6 Model Risk Management (OCC 2011-12 / SR 11-7)](2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md)
- [2.7 Vendor and Third-Party Risk Management](2.7-vendor-and-third-party-risk-management.md)
- [2.8 Access Control and Segregation of Duties](2.8-access-control-and-segregation-of-duties.md)
- [2.9 Agent Performance Monitoring and Optimization](2.9-agent-performance-monitoring-and-optimization.md)
- [2.10 Patch Management and System Updates](2.10-patch-management-and-system-updates.md)
- [2.11 Bias Testing and Fairness Assessment](2.11-bias-testing-and-fairness-assessment-finra-notice-25-07-sr-11-7-alignment.md)
- [2.12 Supervision and Oversight (FINRA Rule 3110)](2.12-supervision-and-oversight-finra-rule-3110.md)
- [2.13 Documentation and Record Keeping](2.13-documentation-and-record-keeping.md)
- [2.14 Training and Awareness Program](2.14-training-and-awareness-program.md)
- [2.15 Environment Routing and Auto-Provisioning](2.15-environment-routing.md)
- [2.16 RAG Source Integrity Validation](2.16-rag-source-integrity-validation.md)
- [2.17 Multi-Agent Orchestration Limits](2.17-multi-agent-orchestration-limits.md)
- [2.18 Automated Conflict of Interest Testing](2.18-automated-conflict-of-interest-testing.md)
- [2.19 Customer AI Disclosure and Transparency](2.19-customer-ai-disclosure-and-transparency.md)
- [2.20 Adversarial Testing and Red Team Framework](2.20-adversarial-testing-and-red-team-framework.md)
- [2.21 AI Marketing Claims and Substantiation](2.21-ai-marketing-claims-and-substantiation.md)

---

*FSI Agent Governance Framework v1.2 - January 2026*
