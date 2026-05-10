# Agent Lifecycle

Complete guide to agent lifecycle governance from creation through decommissioning.

---

## Overview

This guide covers the complete agent lifecycle with zone-specific governance requirements at each stage. Effective lifecycle management helps agents remain compliant, secure, and aligned with business objectives throughout their operational life.

---

## Lifecycle Phases

| Phase | Description | Key Activities |
|-------|-------------|----------------|
| **Creation** | Initial agent setup | Zone classification, environment selection |
| **Development** | Building and configuring | Topics, knowledge sources, connectors |
| **Testing** | Validation before promotion | Functional testing, security review |
| **Deployment** | Production release | Channel publication, user access |
| **Monitoring** | Ongoing observation | Performance, usage, compliance |
| **Maintenance** | Updates and changes | Enhancements, fixes, retraining |
| **Decommission** | Secure retirement | Data retention, access removal |

---

## Phase 1: Creation

### Zone Selection

Before creating an agent, determine the appropriate governance zone:

| Factor | Zone 1 | Zone 2 | Zone 3 |
|--------|--------|--------|--------|
| **Data sensitivity** | Public/internal only | Departmental data | Customer PII, financial |
| **User scope** | Individual | Team/department | Enterprise-wide |
| **External access** | No | No | Yes (with approval) |
| **Approval required** | Self-service | Manager | Governance committee |

See [Zones and Tiers](zones-and-tiers.md) for detailed zone selection criteria.

### Environment Routing

Makers are automatically routed to appropriate environments based on security group membership:

1. **Zone 1**: Personal developer environment (auto-provisioned)
2. **Zone 2**: Team/departmental environment
3. **Zone 3**: Enterprise managed environment

### Initial Governance Classification

| Requirement | Zone 1 | Zone 2 | Zone 3 |
|-------------|--------|--------|--------|
| Business justification | Optional | Required | Detailed |
| Sponsor approval | None | Manager | Executive |
| Risk assessment | None | Basic | Comprehensive |
| Documentation | Minimal | Standard | Full |

---

## Phase 2: Development

### Developer Environment Usage

| Environment Type | Purpose | Governance Level |
|------------------|---------|------------------|
| **Personal developer** | Individual experimentation | Minimal (Zone 1) |
| **Shared development** | Team collaboration | Standard (Zone 2) |
| **Controlled development** | Enterprise solutions | Full (Zone 3) |

### Version Control with Solutions

For Zone 2-3 agents, use Power Platform solutions for version control:

1. Create a solution containing the agent
2. Export solution for backup/deployment
3. Use ALM pipelines for promotion

### Co-Authoring Controls

| Zone | Co-Authoring | Configuration |
|------|--------------|---------------|
| Zone 1 | Disabled | Single owner only |
| Zone 2 | Limited | Team members via security group |
| Zone 3 | Controlled | Governance-approved editors only |

### Development Checklist

- [ ] Agent created in appropriate environment
- [ ] Solution created (Zone 2-3)
- [ ] Knowledge sources configured
- [ ] Connectors reviewed for DLP compliance
- [ ] Authentication configured appropriately
- [ ] Initial testing completed

---

## Phase 3: Testing

### Test Environment Requirements

| Zone | Test Environment | Requirements |
|------|------------------|--------------|
| Zone 1 | Same as development | Basic functional testing |
| Zone 2 | Dedicated test environment | Formal test plan |
| Zone 3 | Production-like environment | Full validation suite |

### Validation Checklists by Zone

#### Zone 1 Testing

- [ ] Agent responds correctly to expected queries
- [ ] No sensitive data exposed
- [ ] Performance acceptable

#### Zone 2 Testing

- [ ] All Zone 1 checks
- [ ] Connectors function correctly
- [ ] Team members can access appropriately
- [ ] Manager approval obtained

#### Zone 3 Testing

- [ ] All Zone 2 checks
- [ ] Security testing completed
- [ ] Compliance review passed
- [ ] Performance benchmarks met
- [ ] Fallback scenarios tested
- [ ] User acceptance testing completed
- [ ] Governance committee approval

### Security Testing Requirements

| Test Type | Zone 1 | Zone 2 | Zone 3 |
|-----------|--------|--------|--------|
| DLP policy validation | Automatic | Required | Required |
| Authentication testing | N/A | Required | Required |
| Data access review | Optional | Required | Required |
| Penetration testing | N/A | Optional | Required |
| Bias assessment | N/A | Optional | Required |

---

## Phase 4: Deployment

### Zone Promotion Process

Agents progress through zones based on governance requirements:

1. Zone 1 agent shared beyond creator triggers Zone 2 evaluation
2. Zone 2 agent deployed to production triggers Zone 3 evaluation
3. Promotion requires meeting all criteria for target zone

### ALM Pipeline Usage

For Zone 2-3 promotions, use Power Platform pipelines:

1. **Configure pipeline** in Power Apps (Solutions > Pipelines)
2. **Add stages** (Development, Test, Production)
3. **Deploy solution** with agent through pipeline
4. **Validate deployment** in target environment

!!! warning
    Target environments in pipelines must be enabled as Managed Environments. Configure this in
    PPAC > Deployment > Settings.

### Approval Workflows

| Promotion | Approvers | Documentation |
|-----------|-----------|---------------|
| Zone 1 to Zone 2 | Manager, Environment owner | Business justification |
| Zone 2 to Zone 3 | Governance committee, Compliance, Security | Full assessment package |
| Within Zone | Environment owner | Change request |

### Channel Publication

| Channel | Zone 1 | Zone 2 | Zone 3 |
|---------|--------|--------|--------|
| Microsoft 365 Chat | Allowed | Allowed | Allowed |
| Teams | Blocked | Allowed | Allowed |
| SharePoint | Blocked | Allowed | Allowed |
| External website | Blocked | Blocked | Allowed (approved) |
| Direct Line | Blocked | Blocked | Allowed (approved) |

---

## Phase 5: Monitoring

### Performance Monitoring

| Metric | Zone 1 Target | Zone 2 Target | Zone 3 Target |
|--------|---------------|---------------|---------------|
| Success rate | >80% | >90% | >95% |
| Response time | <10s | <5s | <3s |
| Availability | 95% | 99% | 99.9% |

### Usage Tracking

| Tracking | Zone 1 | Zone 2 | Zone 3 |
|----------|--------|--------|--------|
| Session counts | Monthly | Weekly | Daily |
| User analytics | Optional | Required | Required |
| Conversation logs | N/A | Sampled | Full |
| Cost tracking | Aggregate | Department | Per-agent |

### Compliance Verification

| Verification | Frequency | Zone 1 | Zone 2 | Zone 3 |
|--------------|-----------|--------|--------|--------|
| DLP compliance | Automatic | Yes | Yes | Yes |
| Access review | Quarterly | No | Yes | Yes |
| Security scan | Monthly | No | Yes | Yes |
| Full audit | Annual | No | No | Yes |

### Alert Configuration

Configure alerts for:

- Success rate drops below threshold
- Unusual usage patterns
- Security events
- Capacity approaching limits

---

## Phase 6: Maintenance

### Change Management Process

| Change Type | Zone 1 | Zone 2 | Zone 3 |
|-------------|--------|--------|--------|
| Minor updates | Self-service | Notify manager | Change request |
| Major changes | Self-service | Manager approval | CAB approval |
| Knowledge updates | Self-service | Review required | Formal process |
| Connector changes | Self-service | Security review | Full assessment |

### Version Updates

1. **Create new solution version** in development
2. **Test changes** in test environment
3. **Deploy via pipeline** to production
4. **Validate deployment** and rollback if needed

### Owner Transitions

When agent ownership changes:

| Task | Zone 1 | Zone 2 | Zone 3 |
|------|--------|--------|--------|
| Transfer ownership | Self-service | Document transfer | Formal handover |
| Update documentation | Optional | Required | Required |
| Notify stakeholders | N/A | Team | All users |
| Compliance review | N/A | Optional | Required |

### Periodic Reviews

| Review Type | Zone 1 | Zone 2 | Zone 3 |
|-------------|--------|--------|--------|
| Business value | Annual | Quarterly | Monthly |
| Security posture | N/A | Semi-annual | Quarterly |
| Compliance | N/A | Annual | Quarterly |
| Performance | As needed | Monthly | Weekly |

---

## Phase 7: Decommissioning

### Agent Retirement Process

1. **Retirement Decision** — Document business justification
2. **Notify Stakeholders** — Inform users, compliance, security
3. **Disable Agent** — Remove from channels, disable publishing
4. **Export Data** — Capture conversation history if required
5. **Retain per Policy** — Apply retention requirements
6. **Delete Agent** — Remove from environment
7. **Update Inventory** — Remove from agent registry
8. **Close Documentation** — Archive all governance records

### Decommission Checklist

- [ ] Business justification for retirement documented
- [ ] Stakeholders notified (users, compliance, security)
- [ ] Agent disabled (not deleted initially)
- [ ] User access removed
- [ ] Conversation history exported (if required)
- [ ] Data retention requirements met
- [ ] Agent deleted from environment
- [ ] Inventory updated
- [ ] Documentation archived

### Data Retention Requirements

| Data Type | Retention Period | Zone Requirement |
|-----------|------------------|------------------|
| Conversation logs | Per retention policy | Zone 2-3 |
| Configuration | 7–10 years (FSI) | Zone 3 |
| Audit trail | 7–10 years (FSI) | Zone 2-3 |
| User data | Per privacy policy | All zones |

### Audit Trail Preservation

For Zone 3 agents:

1. Export complete audit log
2. Document reason for retirement
3. Preserve approval chain
4. Archive in compliance system
5. Retain per regulatory requirements

---

## Zone-Specific Lifecycle Summary

### Zone 1: Personal Productivity

| Phase | Governance |
|-------|------------|
| Creation | Auto-provisioned developer environment |
| Development | Self-service, minimal oversight |
| Testing | Basic functional testing |
| Deployment | Creator-only access, M365 Chat channel |
| Monitoring | Basic metrics, aggregate reporting |
| Maintenance | Self-service updates |
| Decommission | Creator-initiated, minimal retention |

### Zone 2: Team Collaboration

| Phase | Governance |
|-------|------------|
| Creation | Manager approval, team environment |
| Development | Team collaboration, version control |
| Testing | Formal test plan, security review |
| Deployment | Team access, internal channels |
| Monitoring | Weekly metrics, compliance checks |
| Maintenance | Documented changes, manager approval |
| Decommission | Stakeholder notification, data export |

### Zone 3: Enterprise Managed

| Phase | Governance |
|-------|------------|
| Creation | Committee approval, risk assessment |
| Development | Controlled environment, full documentation |
| Testing | Complete validation, security testing |
| Deployment | Phased rollout, all channels (approved) |
| Monitoring | Daily metrics, continuous compliance |
| Maintenance | CAB approval, formal change process |
| Decommission | Full audit trail, 10-year retention |

---

## Regulatory Considerations

### FSI Regulatory Requirements by Lifecycle Phase

| Phase | FINRA | SEC | SOX | GLBA |
|-------|-------|-----|-----|------|
| Creation | Supervision (3110) | - | IT Controls | - |
| Development | Documentation (4511) | 17a-3/4 | 302 | 501(b) |
| Testing | Validation | 17a-4 | 404 | - |
| Deployment | Approval records | - | 302 | 501(b) |
| Monitoring | Supervision (3110) | 17a-3/4 | 404 | 501(b) |
| Maintenance | Change records (4511) | 17a-4 | 404 | - |
| Decommission | Retention (4511) | 17a-4 | 802 | 501(b) |

### Examination Readiness

Maintain documentation at each phase for regulatory examinations:

- Agent creation requests and approvals
- Development records and version history
- Test results and validation evidence
- Deployment approvals and access lists
- Monitoring reports and incident records
- Change history and maintenance logs
- Decommission decisions and data retention proof

---

## Microsoft CAPE 7-Stage Lifecycle Alignment

Microsoft's CAPE materials describe a 7-stage agent lifecycle (Intake → Triage → Build → Deploy → Monitor → Improve → Retire) that organizations use to manage agent portfolios at scale. FSI-AgentGov's lifecycle treatment (described above in this document) aligns with Microsoft's 7-stage model — they describe the same operational reality using different vocabularies. The two frameworks are compatible and complementary. This section maps the Microsoft CAPE stages to FSI-AgentGov's existing lifecycle phases, identifies the Center of Excellence function that owns each stage, and names the key controls that help meet regulatory requirements at each gate.

### CAPE × FSI Lifecycle Mapping

| Microsoft CAPE Stage | FSI-AgentGov Treatment | Primary CoE Function | Primary FSI Accountability Role | Key Controls |
|---------------------|------------------------|---------------------|--------------------------------|--------------|
| **Intake** | Creation phase (zone classification, business justification) | Govern | AI Governance Lead | [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) |
| **Triage** | Creation phase (risk assessment, approval routing) | Govern | AI Governance Lead + Chief Risk Officer | [2.6](../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md), [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) |
| **Build** | Development phase (configuration, knowledge sources, connectors) | Enable | Copilot Studio Agent Author + Power Platform Admin | [2.1](../controls/pillar-2-management/2.1-managed-environments.md), [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) |
| **Deploy** | Testing + Deployment phases (validation, release gate, channel publication) | Optimize | Power Platform Admin + AI Governance Lead | [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [2.5](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md) |
| **Monitor** | Monitoring phase (performance tracking, compliance verification) | Optimize | Service Owner + Power Platform Admin | [3.2](../controls/pillar-3-reporting/3.2-usage-analytics-and-activity-monitoring.md), [3.10](../controls/pillar-3-reporting/3.10-hallucination-feedback-loop.md) |
| **Improve** | Maintenance phase (updates, optimization, knowledge refresh) | Enable + Optimize | Agent Product Owner + Service Owner | [2.3](../controls/pillar-2-management/2.3-change-management-and-release-planning.md), [2.16](../controls/pillar-2-management/2.16-rag-source-integrity-validation.md) |
| **Retire** | Decommissioning phase (retirement decision, data retention, cleanup) | Govern | AI Governance Lead + Chief Compliance Officer | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [1.9](../controls/pillar-1-security/1.9-data-retention-and-deletion-policies.md) |

**Cross-references:** See [Agentic Center of Excellence](agentic-coe.md) for the full treatment of the four CoE functions (Govern, Enable, Optimize, Scale) and the lifecycle × function ownership matrix. See [Role Catalog](../reference/role-catalog.md) for canonical role names and accountability definitions. See [Microsoft CAPE Crosswalk](../reference/microsoft-cape-crosswalk.md) for pattern-by-pattern regulatory implications.

### Stage-by-Stage FSI Implementation Notes

#### Intake — Formal Request Capture

**What it means in CAPE vocabulary.** Intake is the portfolio activity where the Center of Excellence receives agent requests from business lines, names an owner, and begins the formal governance pathway. In CAPE framing, every agent that reaches production should have entered through a documented intake process, not emerged as a shadow deployment.

**What it looks like in FSI practice.** An FSI institution's intake process captures the agent request in a structured format (business justification, data sources, user population, channel requirements). Zone classification occurs at intake — the AI Governance Lead applies the zone selection criteria from [Zones and Tiers](zones-and-tiers.md) based on data sensitivity, user scope, and regulatory exposure. For Zone 3 agents, intake triggers the governance committee approval pathway. For Zone 1 and Zone 2 agents, intake documents the request but may not require committee-level approval.

**The most important governance gate at this stage.** Agent inventory registration in Control 3.1 is mandatory before an agent proceeds beyond intake. An agent that bypasses intake and appears in production without an inventory entry is a books-and-records gap under FINRA Rule 4511 and SEC Rules 17a-3/17a-4. The inventory entry names the agent owner, the zone classification, the business sponsor, and the initial risk tier — these fields become the foundation for all downstream supervision and monitoring obligations.

#### Triage — Value × Risk × Feasibility Scoring

**What it means in CAPE vocabulary.** Triage is the portfolio activity where the CoE evaluates whether the agent request should proceed, be deferred, or be rejected. CAPE recommends scoring on three dimensions: business value, technical feasibility, and risk exposure. The triage decision determines priority and resourcing.

**What it looks like in FSI practice.** FSI triage adds regulatory exposure as a fourth dimension. An agent request that scores high on business value but touches customer data or executes decisions autonomously receives heightened scrutiny. The Chief Risk Officer (or delegate) participates in triage for any agent that may be classified as a model under OCC Bulletin 2011-12 / Fed SR 26-2. FINRA-supervised firms apply Rule 3110 supervision requirements at triage to identify whether the agent will produce communications subject to supervision. For Zone 3 agents, triage produces the initial risk tier and identifies the mandatory controls that must be in place before deployment.

**The most important governance gate at this stage.** Initial regulatory exposure assessment is the triage gate that prevents an institution from building an agent that it cannot legally deploy. An agent that reaches the Build stage without a documented assessment of its FINRA, SEC, OCC, GLBA, or SOX exposure will face re-scoping or abandonment when Compliance reviews it at the Deploy gate. FSI institutions should document the triage decision and the regulatory exposure rationale in the agent's inventory entry or governance committee minutes — this documentation becomes the examiner artifact that shows the institution understood the risk profile before committing resources.

#### Build — Configuration and Knowledge Assembly

**What it means in CAPE vocabulary.** Build is the stage where makers configure the agent, wire connectors, curate knowledge sources, and implement the conversational design. CAPE emphasizes that Build should follow golden-path templates provided by the Enable function to reduce maker friction and increase control consistency.

**What it looks like in FSI practice.** FSI builders work in managed environments (Control 2.1) segmented by zone. Zone 1 builders work in personal developer environments with self-service access. Zone 2 and Zone 3 builders work in controlled environments with documented change management and co-authoring restrictions. Knowledge sources are subject to RAG source integrity validation (Control 2.16) — an FSI agent that surfaces policy guidance or regulatory citations must draw from validated, version-controlled sources with named SME ownership. Connectors are subject to DLP policy enforcement (Control 1.5) and Advanced Connector Policies (Control 1.4) that prevent builders from wiring unapproved data pathways.

**The most important governance gate at this stage.** Knowledge source validation before the agent answers its first user query. An agent that cites stale policy, deprecated procedures, or unvalidated external content creates both operational risk (wrong answers) and regulatory risk (unsupervised communications under FINRA Rule 3110, inaccurate disclosures under Reg BI). Control 2.16 requires knowledge sources to carry refresh dates, SME attestations, and version lineage — these fields support compliance with the CAPE "drift thesis" that agents slowly give increasingly wrong answers with full confidence when their knowledge sources are not maintained.

#### Deploy — Validation, Release Gate, and Channel Publication

**What it means in CAPE vocabulary.** Deploy is the gate where an agent moves from development to production. CAPE recommends risk-proportionate release gates — lightweight for low-risk deployments, heavyweight for business-critical or external-facing agents. Deploy includes validation (functional, security, bias), release approval, and channel publication.

**What it looks like in FSI practice.** FSI Deploy is a formal release gate for Zone 2 and Zone 3 agents. Zone 3 agents require governance committee approval (per [Operating Model](operating-model.md)) before production deployment. Testing and validation (Control 2.5) must demonstrate that the agent meets the zone-specific validation requirements documented in the Testing phase above. Change management (Control 2.3) produces a release record that names the approver, the deployment timestamp, and the change scope — this record supports compliance with SOX Section 404 IT general controls for financial reporting systems and OCC heightened standards for critical systems. Channel publication follows zone-specific channel policies (Zone 1 = M365 Chat only; Zone 2 = internal channels; Zone 3 = all channels with approval).

**The most important governance gate at this stage.** Release-gate enforcement with documented approval before production access is granted. An FSI institution that allows Zone 3 agents to reach production without governance committee approval has a control failure that an examiner will classify as a design deficiency under SOX 404 or a supervisory failure under FINRA Rule 3110. The release record should include the agent ID, the approver names, the deployment environment, and the mandatory controls verification checklist — these fields become the audit trail that demonstrates the institution applied risk-proportionate oversight before granting the agent production access.

#### Monitor — Performance Tracking and Compliance Verification

**What it means in CAPE vocabulary.** Monitor is the ongoing activity where the Optimize function tracks agent health, detects drift, and surfaces improvement opportunities. CAPE emphasizes that every agent in production without monitoring is accumulating risk — agents do not fail dramatically; they slowly drift, giving increasingly wrong answers with full confidence.

**What it looks like in FSI practice.** FSI monitoring combines operational metrics (latency, error rate, user satisfaction) with compliance metrics (DLP denies, hallucination feedback, usage analytics). Control 3.2 requires usage tracking at frequencies that vary by zone (Zone 1 = monthly; Zone 2 = weekly; Zone 3 = daily). Hallucination feedback (Control 3.10) provides the signal that an agent's knowledge base has drifted or that the agent is operating outside its documented decision-rights boundary. For FINRA-supervised firms, monitoring includes supervisory review of agent-produced communications under Rule 3110 — the frequency and depth of review depend on the agent's risk tier and the communication type. For OCC-supervised banks, monitoring includes ongoing model performance validation under OCC Bulletin 2011-12 Section V for any agent classified as a model.

**The most important governance gate at this stage.** Drift detection and re-validation triggers. The CAPE "drift thesis" — that agents slowly give wrong answers over time — maps directly to FINRA Rule 4511 and SEC Rules 17a-3/17a-4 books-and-records obligations. An agent that drifts into providing inaccurate policy guidance or incorrect regulatory citations is producing unreliable records. FSI institutions should document the monitoring cadence, the drift detection criteria, and the re-validation triggers in the agent's governance record. When drift is detected, the agent should be pulled from production until re-validated — this decision and the re-validation evidence become the examiner artifact that shows the institution maintained supervisory oversight throughout the agent's operational life.

#### Improve — Updates, Optimization, and Knowledge Refresh

**What it means in CAPE vocabulary.** Improve is the stage where the CoE acts on monitoring signals to enhance the agent — updating knowledge sources, refining prompts, expanding capabilities, or adjusting scope. CAPE frames agents as products, not projects — products require ongoing improvement cycles, not one-time delivery.

**What it looks like in FSI practice.** FSI improvement follows change management (Control 2.3) with approval gates that vary by zone and by change materiality. Minor knowledge updates (refreshing a policy FAQ with the current version) may follow a lightweight approval process in Zone 1 and Zone 2. Material changes (adding a new connector, changing the model, expanding the agent's decision-rights boundary) require governance committee approval for Zone 3 agents. For OCC-supervised banks, material changes to an agent classified as a model trigger re-validation under SR 26-2 — the institution must document what changed, why it changed, and the validation evidence that the change did not degrade the agent's performance or introduce unacceptable risk.

**The most important governance gate at this stage.** Knowledge source refresh and SME attestation. The Improve stage is where FSI institutions operationalize the "agents are products, not projects" framing. An agent that launched six months ago with validated knowledge sources requires refresh to remain valid. Control 2.16 supports this requirement by mandating knowledge source refresh dates and SME ownership. The refresh cadence depends on the knowledge domain (regulatory policy may require quarterly refresh; internal HR policy may require annual refresh). The SME attestation that accompanies each refresh becomes the examiner artifact that demonstrates the institution maintained knowledge quality over the agent's operational life.

#### Retire — Retirement Decision, Data Retention, and Cleanup

**What it means in CAPE vocabulary.** Retire is the formal stage where an agent is removed from production, its data is retained per policy, and its resources are cleaned up. CAPE emphasizes that retirement is not informal abandonment — it is a documented decision with a retention disposition.

**What it looks like in FSI practice.** FSI retirement carries regulatory retention obligations. SEC Rule 17a-4 and FINRA Rule 4511 require retention of books and records for specified periods (typically 6–7 years for most records, 10 years for some). An FSI agent that produced decisions, communications, or records during its operational life must have those outputs retained per the applicable regulation even after the agent is retired. Control 1.9 documents the retention requirements by data type and by regulation. Control 1.7 ensures that the agent's audit trail is retained along with its outputs. The retirement decision should document why the agent is being retired (low utilization, replaced by newer agent, business line sunset, regulatory exposure identified post-deployment) and should name the approver and the retention disposition.

**The most important governance gate at this stage — and the FSI anti-pattern.** FSI institutions that skip formal retirement create record retention gaps and examiner exposure. The anti-pattern is informal abandonment: the agent owner leaves the firm, the business line deprioritizes the use case, and the agent lingers in production with no monitoring, no ownership, and no retirement decision. The agent continues to generate audit logs and may continue to respond to queries with stale knowledge. This is a supervisory failure under FINRA Rule 3110 and a records retention gap under SEC 17a-4. FSI institutions should implement quarterly orphaned agent detection (Control 3.6) to surface retirement candidates before they become compliance gaps. The retirement decision and the records-retention attestation become the examiner artifacts that demonstrate the institution applied risk-proportionate oversight through the agent's full lifecycle, including its end.

---

## Related Controls

- [Control 2.1: Managed Environments](../controls/pillar-2-management/2.1-managed-environments.md)
- [Control 2.3: Change Management](../controls/pillar-2-management/2.3-change-management-and-release-planning.md)
- [Control 2.5: Testing and Validation](../controls/pillar-2-management/2.5-testing-validation-and-quality-assurance.md)
- [Control 2.15: Environment Routing](../controls/pillar-2-management/2.15-environment-routing.md)
- [Control 3.1: Agent Inventory](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md)
- [Control 3.6: Orphaned Agent Detection](../controls/pillar-3-reporting/3.6-orphaned-agent-detection-and-remediation.md)

---

*Updated: May-2026 | Version: v1.5.0 | UI Verification Status: Current*
