# Human-in-the-Loop (HITL) Trigger Definitions

**Status:** January 2026 - FSI-AgentGov v1.2
**Related Controls:** 2.12 (Supervision), 2.17 (Multi-Agent Orchestration), 2.6 (Model Risk)

---

## Purpose

This specification defines when AI agent actions require human review or approval before execution. HITL triggers ensure appropriate supervision for high-impact decisions and maintain regulatory compliance for financial services organizations.

### Industry Context

This specification aligns with the **Agentic Oversight Framework** published by Sardine for regulated financial services. The framework defines five components for autonomous AI governance:

| Component | Description | FSI-AgentGov Coverage |
|-----------|-------------|----------------------|
| **Access** | Constrained data and tool access | [AAM](../governance-operations/action-authorization-matrix.md) sections 3-6, DLP policies |
| **Agent Operation** | Defined tasks, tool invocation, reasoning | AAM sections 2-5, [Control 1.14](../../controls/pillar-1-security/1.14-data-minimization-and-agent-scope-control.md) |
| **Decision and Presentation** | Agent recommends, human approves | HITL triggers (this document) |
| **Comprehensive Audit Trail** | All data, actions, decisions logged | [Control 1.7](../../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), AAM section 9 |
| **Board Governance** | Integration within GRC framework | [Control 2.12](../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md), escalation matrix |

**Reference:** [Sardine Agentic Oversight Framework Whitepaper](https://go.sardine.ai/hubfs/Whitepapers/The%20Agentic%20Oversight%20Framework.pdf)

---

## AI Agent Autonomy Levels (FINRA 2026 Report)

The FINRA 2026 Annual Regulatory Oversight Report defines autonomy levels that determine appropriate HITL patterns:

| Autonomy Level | Description | Recommended HITL Pattern | Zone |
|---------------|-------------|-------------------------|------|
| **Assisted** | AI suggests, human decides | Sampled Review | Zone 1-2 |
| **Augmented** | AI recommends, human approves | Pre-Approval for material actions | Zone 2-3 |
| **Automated** | AI executes pre-approved actions | Escalation-on-Threshold | Zone 3 restricted |
| **Autonomous** | AI self-directs | **Not Recommended** | Avoid for Zone 3 |

!!! danger "Autonomous Agents and Financial Services"
    FINRA expects human oversight of AI-assisted customer interactions. Fully autonomous agents without pre-approval or escalation mechanisms are not appropriate for Zone 3 customer-facing deployments.

### Mapping Autonomy to HITL Triggers

```yaml
# Autonomy-based HITL Configuration
autonomy_hitl_mapping:
  assisted:
    pattern: "sampled_review"
    sample_rate: 0.05  # 5%
    real_time_approval: false

  augmented:
    pattern: "pre_approval"
    approval_required_for:
      - "recommendations"
      - "account_changes"
      - "financial_transactions"
    sample_rate: 0.10  # 10% for non-approval items

  automated:
    pattern: "escalation_on_threshold"
    thresholds:
      confidence_minimum: 0.85
      transaction_maximum: 1000
      escalation_mandatory: true
    post_audit_rate: 1.0  # 100% post-execution review

  autonomous:
    pattern: "not_recommended"
    warning: "Zone 3 customer-facing agents should not operate autonomously"
```

---

## HITL Pattern Definitions

Three primary patterns for human oversight in AI agent workflows:

| Pattern | Description | Timing | Use Case |
|---------|-------------|--------|----------|
| **Pre-Approval** | Human must approve before agent action executes | Before action | High-risk actions, Zone 3 agents, regulatory decisions |
| **Sampled Review** | Post-hoc spot checks on agent decisions | After action | Quality assurance, compliance monitoring, audit sampling |
| **Escalation-on-Threshold** | Automatic human handoff when thresholds exceeded | During action | Confidence scoring, risk limits, unusual activity |

### Pattern 1: Pre-Approval

Agent pauses and requests human approval before executing action.

- **Zone requirement:** Mandatory for Zone 3 high-risk actions
- **Regulatory driver:** FINRA 3110 supervision, Reg BI suitability
- **Implementation:** Approval workflow, queue management, SLA tracking

### Pattern 2: Sampled Review

Agent executes action; subset of actions flagged for post-hoc human review.

- **Zone requirement:** Recommended for Zone 2, optional for Zone 1
- **Regulatory driver:** FINRA 3110 reasonable supervision
- **Implementation:** Random sampling, risk-based sampling, periodic audits

### Pattern 3: Escalation-on-Threshold

Agent monitors confidence scores or risk indicators and escalates when thresholds are breached.

- **Zone requirement:** Required for Zone 2-3 customer interactions
- **Regulatory driver:** SR 11-7 model risk management
- **Implementation:** Confidence scoring, anomaly detection, risk scoring

---

## HITL Trigger Framework

### Trigger Categories

| Category | Description | Regulatory Driver |
|----------|-------------|-------------------|
| **Mandatory** | Always require human review | Regulatory requirement |
| **Configurable** | Organization sets threshold | Risk-based decision |
| **Conditional** | Context-dependent triggers | Business rules |
| **Exception** | Unusual situations | Anomaly detection |

---

## Mandatory HITL Triggers

These triggers ALWAYS require human review before agent action proceeds:

### Financial Threshold Triggers

| Trigger | Condition | Review SLA | Approver Role |
|---------|-----------|------------|---------------|
| **Large Transaction** | Transaction value > $25,000 | 30 minutes | Supervisor |
| **Account Modification** | Account ownership change | 1 hour | Operations Manager |
| **Credit Decision** | Any credit/lending recommendation | 15 minutes | Credit Officer |
| **Investment Recommendation** | Suitability-impacting advice | 15 minutes | Registered Representative |
| **Wire Transfer** | Any wire transfer initiation | 15 minutes | Treasury |

### Suitability Triggers

| Trigger | Condition | Review SLA | Approver Role |
|---------|-----------|------------|---------------|
| **Suitability Determination** | Agent makes suitability assessment | Immediate | Registered Representative |
| **Risk Profile Change** | Customer risk profile modification | 30 minutes | Supervisor |
| **Product Recommendation** | Investment product suggestion | 15 minutes | Compliance |
| **Retirement Account Action** | IRA/401k transaction | 30 minutes | Supervisor |

### Regulatory Triggers

| Trigger | Condition | Review SLA | Approver Role |
|---------|-----------|------------|---------------|
| **SAR Indicator** | Suspicious activity detected | Immediate | BSA/AML Officer |
| **KYC Verification** | Identity verification decision | 1 hour | Compliance |
| **Regulatory Disclosure** | Required disclosure delivery | 15 minutes | Compliance |
| **Customer Complaint** | Complaint identified | 1 hour | Compliance |

---

## Configurable HITL Triggers

Organizations configure these thresholds based on risk appetite:

### Confidence Score Triggers

```yaml
# Confidence-based HITL Configuration
confidence_triggers:
  low_confidence_threshold: 0.7
  very_low_confidence_threshold: 0.5

  responses:
    below_very_low:
      action: "block_and_escalate"
      message: "I'm not confident enough to answer this. Let me connect you with a specialist."
      route_to: "human_queue"
      sla_minutes: 15

    below_low:
      action: "human_review"
      message: "Let me verify this information before proceeding."
      route_to: "verification_queue"
      sla_minutes: 30

    above_low:
      action: "proceed"
      message: null
      route_to: null
```

### Complexity Triggers

| Complexity Indicator | Threshold | Action |
|---------------------|-----------|--------|
| Query word count | > 100 words | Route for review |
| Multi-topic query | > 3 distinct topics | Human assist |
| Follow-up depth | > 5 clarifying questions | Escalate |
| Session duration | > 30 minutes | Supervisor check |

### Sensitive Topic Triggers

```yaml
# Sensitive Topic HITL Configuration
sensitive_topics:
  always_escalate:
    - "legal_advice"
    - "tax_advice"
    - "estate_planning"
    - "regulatory_complaint"
    - "discrimination"
    - "fraud_allegation"

  require_confirmation:
    - "account_closure"
    - "beneficiary_change"
    - "address_change"
    - "fee_waiver"

  soft_escalate:
    - "competitor_comparison"
    - "rate_negotiation"
    - "product_complaint"
```

---

## Conditional HITL Triggers

Context-dependent triggers based on business rules:

### Customer Segment Triggers

| Customer Segment | Additional Triggers | Rationale |
|------------------|--------------------|-----------|
| **High Net Worth** | All recommendations | Enhanced service |
| **Senior Customer** | Product changes | Elder protection |
| **New Customer** | First 90 days of activity | Onboarding protection |
| **Complaint History** | Any service interaction | Relationship management |

### Agent Capability Triggers

| Agent Type | Trigger Condition | Review Type |
|------------|-------------------|-------------|
| **Advisory Agent** | Any recommendation | Real-time approval |
| **Transactional Agent** | Value thresholds exceeded | Transaction review |
| **Informational Agent** | Sensitive topic detected | Content review |
| **Orchestrating Agent** | Depth limit reached | Chain review |

### Time-Based Triggers

| Condition | Trigger | Rationale |
|-----------|---------|-----------|
| After hours (6pm-8am) | All transactions | Fraud prevention |
| Weekend | Account modifications | Reduced staffing |
| Holiday | Large transactions | Enhanced review |
| End of quarter | Advisory interactions | Sales pressure mitigation |

---

## HITL Response Types

### Response Actions

| Action | Description | Use Case |
|--------|-------------|----------|
| **Block** | Prevent agent action entirely | High-risk situations |
| **Pause** | Hold until human approves | Approval workflows |
| **Review** | Allow action, flag for review | Audit sampling |
| **Assist** | Bring human into conversation | Complex queries |
| **Escalate** | Transfer to specialist | Subject matter expertise |
| **Log** | Proceed, enhanced logging | Monitoring only |

### Response Flow Configuration

```yaml
# HITL Response Flow
hitl_response_flow:
  trigger_activated:
    - log_trigger_details
    - capture_conversation_context
    - determine_response_action

  block_action:
    - notify_user_politely
    - route_to_human_queue
    - set_priority_based_on_trigger
    - start_sla_timer
    - alert_if_sla_breach

  pause_action:
    - notify_user_of_wait
    - present_approval_request
    - capture_approver_decision
    - resume_or_terminate_based_on_decision
    - log_approval_with_justification

  assist_action:
    - add_human_to_conversation
    - provide_context_to_human
    - human_can_guide_or_takeover
    - log_assistance_interaction
```

---

## SLA Definitions

### Review SLA Tiers

| Tier | Target Time | Max Time | Escalation |
|------|-------------|----------|------------|
| **Immediate** | 5 minutes | 15 minutes | Auto-escalate to manager |
| **Urgent** | 15 minutes | 30 minutes | Alert supervisor |
| **Standard** | 30 minutes | 1 hour | Queue management |
| **Normal** | 1 hour | 4 hours | Standard review |

### SLA Breach Handling

```yaml
# SLA Breach Configuration
sla_breach_handling:
  warning_at: 80%  # of SLA time
  breach_at: 100%  # of SLA time

  warning_actions:
    - notify_assigned_reviewer
    - add_to_supervisor_dashboard

  breach_actions:
    - escalate_to_backup_reviewer
    - notify_supervisor
    - log_sla_breach
    - update_compliance_metrics

  repeated_breach:
    threshold: 3  # breaches per day
    actions:
      - alert_operations_manager
      - review_staffing_levels
      - consider_temporary_agent_restriction
```

---

## Implementation Guidance

### Queue Management

```yaml
# HITL Queue Configuration
hitl_queues:
  immediate_review:
    routing: "round_robin"
    backup_after: "5_minutes"
    max_queue_depth: 10
    overflow_action: "escalate_all"

  standard_review:
    routing: "skill_based"
    backup_after: "30_minutes"
    max_queue_depth: 50
    overflow_action: "extend_sla"

  audit_sample:
    routing: "random_assignment"
    sample_rate: "10%"
    priority: "low"
    max_queue_depth: 100
```

### Approver Availability

```yaml
# Approver Availability Configuration
approver_availability:
  business_hours:
    start: "08:00"
    end: "18:00"
    timezone: "America/New_York"

  after_hours:
    on_call_rotation: true
    escalation_path:
      - "on_call_supervisor"
      - "operations_manager"
      - "security_operations"

  fallback:
    action: "block_and_notify"
    message: "This request requires human approval. Please try again during business hours or contact support."
```

### Metrics and Reporting

| Metric | Calculation | Target |
|--------|-------------|--------|
| HITL Trigger Rate | Triggers / Total Interactions | <10% |
| Approval Rate | Approved / Total Reviewed | >90% |
| Average Review Time | Mean time to decision | <SLA |
| SLA Compliance | Reviews within SLA / Total | >95% |
| False Positive Rate | Unnecessary triggers / Total | <5% |

---

## Zone-Specific Configuration

### Zone 1 (Personal Productivity)

```yaml
zone_1_hitl:
  enabled_triggers:
    - "sensitive_topic_detection"  # Minimal
  disabled_triggers:
    - "confidence_score"  # Too noisy for personal use
    - "financial_threshold"  # Not applicable
  rationale: "Minimal friction for low-risk personal agents"
```

### Zone 2 (Team Collaboration)

```yaml
zone_2_hitl:
  enabled_triggers:
    - "confidence_score"
    - "sensitive_topic"
    - "customer_segment"
  thresholds:
    confidence: 0.6  # Moderate
    financial: 10000  # Team appropriate
  rationale: "Balanced controls for shared agents"
```

### Zone 3 (Enterprise Managed)

```yaml
zone_3_hitl:
  enabled_triggers:
    - "all_mandatory"
    - "all_configurable"
    - "conditional_by_segment"
  thresholds:
    confidence: 0.7  # Strict
    financial: 5000  # Conservative
  additional:
    - "audit_sample_all_interactions"
    - "supervisor_spot_check_enabled"
  rationale: "Comprehensive oversight for customer-facing agents"
```

---

## Integration Points

| Control | Integration |
|---------|-------------|
| [2.12 Supervision](../../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | Supervisory review procedures |
| [2.17 Orchestration](../../controls/pillar-2-management/2.17-multi-agent-orchestration-limits.md) | Multi-agent HITL checkpoints |
| [3.4 Incident Reporting](../../controls/pillar-3-reporting/3.4-incident-reporting-and-root-cause-analysis.md) | HITL rejections as incidents |
| [2.6 Model Risk](../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | MRM oversight requirements |

---

*FSI Agent Governance Framework v1.2 - January 2026*
