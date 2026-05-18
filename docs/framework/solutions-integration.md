# Solutions Integration

How FSI-AgentGov-Solutions automation aligns with the governance framework.

---

## Overview

The FSI Agent Governance Framework defines **what** controls organizations should implement. The FSI-AgentGov-Solutions repository provides **how**—ready-to-deploy automation that operationalizes key controls. The current companion catalog includes **36 solutions (35 live + 1 preview)** aligned to the framework's 78-control baseline, while this page focuses on representative integrations. Use the [Solutions Index](../reference/solutions-index.md) for the authoritative per-solution version and live/preview status details.

```mermaid
flowchart TB
    subgraph Framework["FSI-AgentGov (Framework)"]
        direction TB
        P1[Pillar 1: Security<br/>29 Controls]
        P2[Pillar 2: Management<br/>26 Controls]
        P3[Pillar 3: Reporting<br/>14 Controls]
        P4[Pillar 4: SharePoint<br/>9 Controls]
    end

    subgraph Solutions["FSI-AgentGov-Solutions (Representative Solutions)"]
        direction TB
        ELM[Environment Lifecycle<br/>Management]
        MCM[Message Center<br/>Monitor]
        PGC[Pipeline Governance<br/>Cleanup]
        DEC[Deny Event<br/>Correlation]
        FSW[FINRA Supervision<br/>Workflow]
        CAA[Conditional Access<br/>Automation]
        CD[Compliance<br/>Dashboard]
        SDD[Segregation<br/>Detector]
        SDM[Scope Drift<br/>Monitor]
        RSV[RAG Source<br/>Validator]
        COI[COI<br/>Testing]
        HT[Hallucination<br/>Tracker]
        DR[DR Testing<br/>Framework]
        SSC[Session Security<br/>Configurator]
        FUS[File Upload<br/>Security]
        ACM[Audit Compliance<br/>Manager]
        AAM[Agent Access<br/>Monitor]
        CMM[Content Moderation<br/>Monitor]
        CSI[Cross-Solution<br/>Integration]
    end

    P2 --> ELM
    P2 --> MCM
    P2 --> PGC
    P1 --> DEC
    P3 --> DEC
    P2 --> FSW
    P1 --> CAA
    P3 --> CD
    P2 --> SDD
    P1 --> SDM
    P2 --> RSV
    P2 --> COI
    P3 --> HT
    P2 --> DR
    P1 --> SSC
    P1 --> FUS
    P1 --> ACM
    P3 --> AAM
    P1 --> CMM
    P1 --> CSI
    P3 --> CSI
    CSI --> CD
    CSI --> ELM
```

> :inbox_tray: **Download diagram:** [SVG](../images/diagrams/solutions-integration-overview.svg)

---

## Solution-to-Control Mapping

!!! note "Representative examples"
    This section intentionally highlights representative solution-to-control examples rather than re-publishing the full companion inventory. The canonical live/preview status, version, and full control coverage for each solution live in `assessment/data/solutions-lock.json` and the [Solutions Index](../reference/solutions-index.md). CI validates that any control IDs listed here are a subset of the linked solution's canonical `controls` array.

### Environment Lifecycle Management

Automates environment provisioning with zone classification.

| Control | How Solution Helps |
|---------|-------------------|
| **2.1 Managed Environments** | Automatically enables managed environment settings during provisioning |
| **2.2 Environment Groups** | Assigns environments to zone-appropriate environment groups |
| **2.8 Access Control and Segregation of Duties** | Supports governed environment ownership and maker-checker separation in production paths |

**Applicable Zones:** Zone 2, Zone 3

**Repository Link:** [environment-lifecycle-management](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/environment-lifecycle-management)

**Playbook:** [Environment Lifecycle Management](../playbooks/advanced-implementations/environment-lifecycle-management/index.md)

---

### Message Center Monitor

Operationalizes platform change tracking for governance workflows.

| Control | How Solution Helps |
|---------|-------------------|
| **2.3 Change Management** | Delivers structured notifications for platform changes requiring assessment |

**Applicable Zones:** All zones (organization-wide)

**Repository Link:** [message-center-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/message-center-monitor)

**Playbook:** [Platform Change Governance](../playbooks/advanced-implementations/platform-change-governance/index.md)

---

### Pipeline Governance Cleanup

Transitions from personal to centralized deployment pipelines.

| Control | How Solution Helps |
|---------|-------------------|
| **2.3 Change Management** | Enforces centralized ALM governance by removing ungoverned personal pipelines |

**Applicable Zones:** Zone 2, Zone 3 (production-path environments)

**Repository Link:** [pipeline-governance-cleanup](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/pipeline-governance-cleanup)

**Related Control:** [2.3 - Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md)

---

### Deny Event Correlation Report

Aggregates block events for unified compliance visibility.

| Control | How Solution Helps |
|---------|-------------------|
| **1.5 DLP and Sensitivity Labels** | Correlates DLP policy violation events |
| **1.7 Comprehensive Audit Logging** | Extracts Purview audit events for agent activities |
| **3.4 Incident Reporting** | Provides unified deny event view for incident investigation |

**Applicable Zones:** Zone 2, Zone 3

**Repository Link:** [deny-event-correlation-report](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/deny-event-correlation-report)

**Playbook:** [Deny Event Correlation Report](../playbooks/advanced-implementations/deny-event-correlation-report/index.md)

---

### FINRA Supervision Workflow

Automates supervision queue for AI agent outputs supporting FINRA Rule 3110.

| Control | How Solution Helps |
|---------|-------------------|
| **2.12 Supervision and Oversight** | Routes flagged content to supervisory principals with SLA tracking |
| **1.10 Communication Compliance** | Ingests policy violations from Communication Compliance |
| **1.7 Comprehensive Audit Logging** | Maintains immutable audit trail with SHA-256 integrity hashing |

**Applicable Zones:** Zone 2, Zone 3


**Repository Link:** [finra-supervision-workflow](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/finra-supervision-workflow)

**Prerequisites:**
- Microsoft Purview Communication Compliance configured
- Supervisory principal role assignments in place
- Dataverse database with appropriate capacity

---

### Conditional Access Automation

Automates CA policy deployment and compliance monitoring for AI workloads.

| Control | How Solution Helps |
|---------|-------------------|
| **1.11 Conditional Access and MFA** | Deploys 8 zone-aligned CA policies with break-glass exclusions |
| **1.23 Step-Up Authentication** | Enforces step-up authentication for sensitive agent operations |
| **1.18 Service Principal Governance** | Validates service principal access controls meet zone requirements |

**Applicable Zones:** All zones (zone-specific policy requirements)


**Repository Link:** [conditional-access-automation](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/conditional-access-automation)

**Prerequisites:**
- Microsoft Entra ID P1 licenses
- Break-glass account configuration
- Zone classification completed

---

### Compliance Dashboard

Unified compliance visibility across the framework control catalog.

| Control | How Solution Helps |
|---------|-------------------|
| **3.3 Compliance and Regulatory Reporting** | Aggregates control scores with zone-based filtering and trend analysis |
| **3.1 Agent Inventory and Metadata Management** | Provides executive visibility into governance posture |
| **3.2 Usage Analytics and Activity Monitoring** | Integrates security control scores with operational metrics |

**Applicable Zones:** All zones (organization-wide reporting)


**Repository Link:** [compliance-dashboard](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/compliance-dashboard)

**Prerequisites:**
- Power BI Pro licenses for dashboard consumers
- Dataverse database with appropriate capacity
- Control assessment process established

---

### Segregation Detector

Identifies and helps prevent SoD violations in agent development workflows.

| Control | How Solution Helps |
|---------|-------------------|
| **2.8 Access Control and Segregation of Duties** | Scans for incompatible role assignments across development and deployment |
| **2.1 Managed Environments** | Validates Maker/Checker separation in environment configurations |
| **2.3 Change Management** | Enforces deployment approval separation from developer roles |

**Applicable Zones:** Zone 2, Zone 3


**Repository Link:** [segregation-detector](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/segregation-detector)

**Prerequisites:**
- Environment role assignments documented
- SoD policy requirements defined
- Exception approval workflow established

---

### Scope Drift Monitor

Detects agent data access beyond declared operational scope.

| Control | How Solution Helps |
|---------|-------------------|
| **1.14 Data Minimization and Agent Scope Control** | Compares actual data access against declared scope baselines |
| **1.4 Connector Governance** | Monitors connector usage for scope expansion patterns |
| **1.5 DLP and Sensitivity Labels** | Correlates DLP events with scope violation alerts |

**Applicable Zones:** Zone 2, Zone 3


**Repository Link:** [scope-drift-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/scope-drift-monitor)

**Prerequisites:**
- Agent scope baselines defined
- Unified Audit Log enabled
- Defender for Cloud Apps configured

---

### RAG Source Validator

Validates integrity of RAG knowledge sources with change detection.

| Control | How Solution Helps |
|---------|-------------------|
| **2.16 RAG Source Integrity Validation** | SHA-256 hash validation detects unauthorized content modifications |
| **1.7 Comprehensive Audit Logging** | Tracks knowledge source changes with immutable audit trail |
| **2.13 Documentation and Record Keeping** | Monitors knowledge source freshness for RAG model accuracy |

**Applicable Zones:** Zone 2, Zone 3


**Repository Link:** [rag-source-validator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/rag-source-validator)

**Prerequisites:**
- RAG knowledge sources cataloged
- Baseline hash values generated
- SharePoint/Dataverse/Blob access configured

---

### COI Testing

Automated testing for conflicts of interest in agent recommendations.

| Control | How Solution Helps |
|---------|-------------------|
| **2.18 Automated Conflict of Interest Testing** | Runs 10 predefined scenarios for proprietary bias and suitability violations |
| **2.11 Bias Testing and Fairness Assessment** | Integrates COI testing into agent validation lifecycle |
| **2.5 Testing, Validation, and Quality Assurance** | Provides evidence for COI risk mitigation |

**Applicable Zones:** Zone 2, Zone 3


**Repository Link:** [coi-testing](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/coi-testing)

**Prerequisites:**
- Test scenarios aligned with product catalog
- Integration with FINRA Supervision Workflow
- Agent response baselines established

---

### Hallucination Tracker

Feedback aggregation for hallucination pattern analysis.

| Control | How Solution Helps |
|---------|-------------------|
| **3.10 Hallucination Feedback Loop** | Collects multi-source feedback and clusters hallucination patterns |
| **2.9 Continuous Monitoring** | Tracks hallucination trends for model performance degradation |
| **2.12 Supervision and Oversight** | Routes high-severity hallucinations to supervisory review |

**Applicable Zones:** Zone 2, Zone 3


**Repository Link:** [hallucination-tracker](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/hallucination-tracker)

**Prerequisites:**
- Feedback collection channels configured
- Hallucination taxonomy aligned with firm policies
- Integration with FINRA Supervision Workflow

---

### DR Testing Framework

Automated disaster recovery testing for AI agent infrastructure.

| Control | How Solution Helps |
|---------|-------------------|
| **2.4 Business Continuity and Disaster Recovery** | Validates agent restore procedures against RTO/RPO targets |
| **2.1 Managed Environments** | Tests environment failover for production agent infrastructure |
| **1.9 Data Retention and Deletion Policies** | Verifies backup integrity for agent configurations and data |

**Applicable Zones:** Zone 3 (Enterprise Managed)


**Repository Link:** [dr-testing-framework](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/dr-testing-framework)

**Prerequisites:**
- RTO/RPO targets defined
- DR environment provisioned
- Backup and restore procedures documented

---

### Session Security Configurator

Validates session security settings per governance zone with drift detection and compliance evidence export.

| Control | How Solution Helps |
|---------|-------------------|
| **1.23 Step-Up Authentication** | Validates session timeout and authentication challenge configurations per zone |
| **1.11 Conditional Access and MFA** | Monitors MFA enforcement alignment with zone requirements |

**Applicable Zones:** Zone 2, Zone 3


**Repository Link:** [session-security-configurator](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/session-security-configurator)

---

### File Upload Security

Validates per-agent file upload settings against zone governance policies with drift detection.

| Control | How Solution Helps |
|---------|-------------------|
| **1.14 Data Minimization** | Validates file upload restrictions align with agent scope declarations |
| **1.8 Runtime Protection** | Monitors file upload configurations for security compliance |
| **1.4 Advanced Connector Policies** | Validates connector-level file upload restrictions |

**Applicable Zones:** Zone 2, Zone 3


**Repository Link:** [file-upload-security](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/file-upload-security)

---

### Audit Compliance Manager

Validates tenant and environment audit configurations, detects compliance gaps, and provides approval-gated remediation with Managed Identity authentication.

| Control | How Solution Helps |
|---------|-------------------|
| **1.7 Comprehensive Audit Logging** | Validates audit log configuration completeness, detects gaps, and remediates non-compliant environments with approval workflows |

**Applicable Zones:** All zones


**Repository Link:** [audit-compliance-manager](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/audit-compliance-manager)

---

### Agent Access Monitor

Detects overly permissive agent access configurations per governance zone.

| Control | How Solution Helps |
|---------|-------------------|
| **3.8 Copilot Hub** | Monitors agent access settings and identifies governance gaps |

**Applicable Zones:** All zones


**Repository Link:** [agent-access-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-access-monitor)

---

### Content Moderation Monitor

Validates per-agent content moderation levels against zone-specific governance requirements.

| Control | How Solution Helps |
|---------|-------------------|
| **1.27 Content Moderation Enforcement** | Validates per-agent content moderation levels against zone-specific governance requirements |
| **1.8 Runtime Protection** | Validates content moderation settings meet zone protection requirements |

**Applicable Zones:** Zone 2, Zone 3


**Repository Link:** [content-moderation-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/content-moderation-monitor)

---

## Cross-Solution Integration Layer

The **Cross-Solution Integration** layer wires five Tier 2 governance solutions into the Compliance Dashboard, adds ELM provisioning hooks, and delivers unified evidence export. This enables automated compliance scoring and consolidated audit evidence across all deployed solutions.

### Integration Architecture

```mermaid
flowchart TB
    subgraph Tier2["Tier 2 Solutions"]
        ACM[Audit Compliance<br/>Manager<br/>→ Control 1.7]
        SSC[Session Security<br/>Configurator<br/>→ Controls 1.23, 1.11]
        AAM[Agent Access<br/>Monitor<br/>→ Control 3.8]
        CMM[Content Moderation<br/>Monitor<br/>→ Controls 1.27, 1.8]
        FUS[File Upload<br/>Security<br/>→ Control 1.14]
    end

    subgraph Integration["Cross-Solution Integration"]
        SYNC[Sync-Solution<br/>Assessments.ps1]
        FLOW[CD Solution Feed<br/>Collector Flow]
        CONFIG[IntegrationConfig<br/>Module]
        EXPORT[Unified Evidence<br/>Export]
    end

    subgraph Targets["Target Solutions"]
        CD[Compliance<br/>Dashboard]
        ELM[Environment<br/>Lifecycle Mgmt]
    end

    ACM --> SYNC
    SSC --> SYNC
    AAM --> SYNC
    CMM --> SYNC
    FUS --> SYNC

    ACM --> FLOW
    SSC --> FLOW
    AAM --> FLOW
    CMM --> FLOW
    FUS --> FLOW

    SYNC --> CD
    FLOW --> CD
    CONFIG --> SYNC
    CONFIG --> FLOW
    CONFIG --> EXPORT

    ELM -->|ProvisioningCompleted| ACM

    ACM --> EXPORT
    SSC --> EXPORT
    AAM --> EXPORT
    CMM --> EXPORT
    FUS --> EXPORT
```

> :inbox_tray: **Download diagram:** [PNG](../images/diagrams/solutions-integration-integration-architecture.png) | [SVG](../images/diagrams/solutions-integration-integration-architecture.svg)

### Integration Components

| Component | Type | Purpose |
|-----------|------|---------|
| **IntegrationConfig.psm1** | PowerShell Module | Shared configuration — solution-to-control mappings, status translation, canonical zone/severity values |
| **Sync-SolutionAssessments.ps1** | PowerShell Script | Batch pipeline — queries Tier 2 validation tables, translates status, upserts CD assessment records |
| **cd-solution-feed-collector.json** | Power Automate Flow | Scheduled daily flow — alternative to PowerShell for organizations preferring low-code |
| **elm-solution-initializer.json** | Power Automate Flow | Event-driven — triggers on ELM ProvisioningCompleted to auto-register environments in ACM |
| **Register-ProvisionedEnvironment.ps1** | PowerShell Script | Manual/scripted ACM registration — PowerShell alternative to the ELM flow |
| **Export-UnifiedComplianceEvidence.ps1** | PowerShell Script | Exports governance data from all 5 solutions into auditor-ready package with SHA-256 hash chain |
| **Test-UnifiedEvidenceIntegrity.ps1** | PowerShell Script | Verifies evidence package integrity by recalculating and comparing all hashes |

### Data Flow Summary

| Source | Target | Mechanism | Frequency |
|--------|--------|-----------|-----------|
| 5 Tier 2 solutions | Compliance Dashboard | Sync script or PA flow | Daily |
| ELM provisioning log | ACM environment registry | PA flow or PS script | Event-driven |
| 5 Tier 2 solutions | Evidence export | PS script | On-demand |

### Status Translation

Each Tier 2 solution stores compliance status in different formats. The integration layer normalizes all to the Compliance Dashboard's four-value scale:

| CD Status | Value | Meaning |
|-----------|-------|---------|
| Compliant | 1 | All validations pass |
| Partially Compliant | 2 | Some validations pass |
| Non-Compliant | 3 | Critical failures detected |
| Not Assessed | 4 | No recent validation data |

**Repository Link:** [cross-solution-integration](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/cross-solution-integration)

---

## Zone Applicability Matrix

| Solution | Zone 1 | Zone 2 | Zone 3 | Notes |
|----------|:------:|:------:|:------:|-------|
| Environment Lifecycle Management | — | ✓ | ✓ | Zone 1 uses default environment |
| Message Center Monitor | ✓ | ✓ | ✓ | Organization-wide change tracking |
| Pipeline Governance Cleanup | — | ✓ | ✓ | Only applies to production paths |
| Deny Event Correlation | — | ✓ | ✓ | Zone 2/3 have audit requirements |
| FINRA Supervision Workflow | — | ✓ | ✓ | Required for customer-facing agents |
| Conditional Access Automation | ✓ | ✓ | ✓ | Zone-specific policy requirements |
| Compliance Dashboard | ✓ | ✓ | ✓ | Organization-wide reporting |
| Segregation Detector | — | ✓ | ✓ | SoD required for production paths |
| Scope Drift Monitor | — | ✓ | ✓ | Data minimization for regulated data |
| Session Security Configurator | — | ✓ | ✓ | Zone-specific session settings |
| File Upload Security | — | ✓ | ✓ | Per-agent upload validation |
| Audit Compliance Manager | ✓ | ✓ | ✓ | Tenant-wide audit configuration |
| Agent Access Monitor | ✓ | ✓ | ✓ | Organization-wide access governance |
| Content Moderation Monitor | — | ✓ | ✓ | Moderation for regulated agents |
| RAG Source Validator | — | ✓ | ✓ | Knowledge integrity for compliance |
| COI Testing | — | ✓ | ✓ | Customer-facing recommendations only |
| Hallucination Tracker | — | ✓ | ✓ | Customer-facing agents require tracking |
| DR Testing | — | — | ✓ | Production disaster recovery only |
| Cross-Solution Integration | ✓ | ✓ | ✓ | Organization-wide — feeds CD, evidence export |

---

## Pillar Coverage

| Pillar | Solutions Covering | Coverage Notes |
|--------|-------------------|----------------|
| **Pillar 1: Security** | Deny Event Correlation, Conditional Access Automation, Scope Drift Monitor, Session Security Configurator, File Upload Security, Audit Compliance Manager, Content Moderation Monitor | DLP correlation, access controls, data minimization, session security, audit validation and remediation |
| **Pillar 2: Management** | ELM, MCM, PGC, FINRA Supervision, Segregation Detector, RAG Validator, COI Testing, DR Testing | Environment lifecycle, change management, supervision, testing |
| **Pillar 3: Reporting** | Deny Event Correlation, Compliance Dashboard, Hallucination Tracker, Agent Access Monitor | Incident visibility, compliance reporting, feedback loops, access governance |
| **Pillar 4: SharePoint** | — | SharePoint controls use native admin tools |

---

## Deployment Sequence

For organizations implementing a representative subset of the live catalog, this staged order can help sequence dependencies:

**Phase 1: Foundation**
1. **Message Center Monitor** — Establishes platform change visibility
2. **Environment Lifecycle Management** — Provides governed provisioning
3. **Pipeline Governance Cleanup** — Transitions to centralized ALM

**Phase 2: Compliance & Access Controls**
4. **Conditional Access Automation** — Deploys Zero Trust access policies
5. **Deny Event Correlation** — Aggregates security events
6. **Compliance Dashboard** — Establishes baseline compliance visibility
7. **Scope Drift Monitor** — Monitors data access patterns
8. **Session Security Configurator** — Validates session security per zone

**Phase 3: Regulatory & Operational**
9. **FINRA Supervision Workflow** — Routes customer-facing content for review
10. **Segregation Detector** — Validates role separation before production use
11. **RAG Source Validator** — Validates knowledge source integrity
12. **Cross-Solution Integration** — Wires Tier 2 solutions into Compliance Dashboard

**Phase 4: Quality & Resilience**
13. **COI Testing** — Tests for conflicts of interest
14. **Hallucination Tracker** — Collects feedback for model improvement
15. **DR Testing Framework** — Validates disaster recovery procedures

---

## Repository Structure

```
FSI-AgentGov-Solutions/
├── environment-lifecycle-management/
├── message-center-monitor/
├── pipeline-governance-cleanup/
├── deny-event-correlation-report/
├── finra-supervision-workflow/
├── conditional-access-automation/
├── compliance-dashboard/
├── segregation-detector/
├── scope-drift-monitor/
├── rag-source-validator/
├── session-security-configurator/
├── file-upload-security/
├── audit-compliance-manager/
├── agent-access-monitor/
├── content-moderation-monitor/
├── coi-testing/
├── hallucination-tracker/
├── dr-testing-framework/
├── cross-solution-integration/
│   ├── flows/                            # Power Automate flow templates
│   ├── scripts/powershell/               # PowerShell modules and scripts
│   ├── docs/                             # Integration documentation
│   └── evidence/                         # Evidence export staging
├── scripts/
│   └── hooks/
└── .claude/

(See the [Solutions Index](../reference/solutions-index.md) for the authoritative per-solution version and status table — the inventory above is illustrative of repository shape, not a versioning source.)
```

---

## CoE Starter Kit Alignment

Microsoft's Power Platform Center of Excellence (CoE) Starter Kit provides comprehensive governance patterns. FSI-AgentGov-Solutions complements the CoE Starter Kit for financial services-specific requirements.

### Comparison

| Capability | CoE Starter Kit | FSI-AgentGov-Solutions |
|------------|:---------------:|:----------------------:|
| Environment inventory | ✓ | — |
| Environment provisioning | Basic | Zone-based with approvals |
| Pipeline discovery | ✓ | ✓ (cleanup focused) |
| Message Center monitoring | ✓ | ✓ (simpler setup) |
| Deny event correlation | — | ✓ |
| Power BI governance reports | ✓ | Limited |

### Integration Recommendations

| Scenario | Recommendation |
|----------|----------------|
| **Existing CoE deployment** | Add ELM for zone-based provisioning, DEC for deny visibility |
| **Greenfield FSI deployment** | Deploy FSI solutions first, consider CoE for broader inventory |
| **Enterprise hybrid** | CoE for platform-wide governance, FSI solutions for AI agent-specific controls |

For detailed architecture guidance including scalability limits and alternative patterns, see the [Solutions Architecture Guide](../reference/solutions-architecture-guide.md).

---

## Related Documentation

- [Solutions Index](../reference/solutions-index.md) — Complete solution catalog with version history
- [Solutions Contract](../reference/solutions-contract.md) — Versioning and pinning contract between this repo and FSI-AgentGov-Solutions
- [Solutions Architecture Guide](../reference/solutions-architecture-guide.md) — Enterprise scalability and platform limits
- [Adoption Roadmap](adoption-roadmap.md) — Phased implementation guidance
- [FSI-AgentGov-Solutions Repository](https://github.com/judeper/FSI-AgentGov-Solutions) — Source code and deployment scripts

---

## Summary Statistics

The current companion catalog includes **36 solutions (35 live + 1 preview)** aligned to the framework's **78 controls across 4 pillars**. For the authoritative per-solution version, status, and control coverage details, see the [Solutions Index](../reference/solutions-index.md).

---

*FSI Agent Governance Framework v1.6.2 - May 2026*
