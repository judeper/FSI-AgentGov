# Control 2.6: Model Risk Management - Portal Walkthrough

> This playbook provides portal-based configuration guidance for [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).

---

## Overview

This walkthrough guides you through implementing Model Risk Management (MRM) governance for AI agents, including model classification, inventory management, validation configuration, and performance monitoring.

---

## Part 1: Agent-as-Model Classification

### Model Definition per OCC 2011-12

> A model is a quantitative method, system, or approach that applies statistical, economic, financial, or mathematical theories, techniques, and assumptions to process input data into quantitative estimates.

### Agent Classification Criteria

| Criteria | Model Treatment | Example |
|----------|-----------------|---------|
| Makes decisions affecting customers | Yes - Tier 1 | Credit recommendation agent |
| Provides financial calculations | Yes - Tier 1/2 | Investment calculator agent |
| Influences risk assessments | Yes - Tier 1 | Risk scoring agent |
| Customer-facing recommendations | Yes - Tier 2 | Product recommendation agent |
| Information retrieval only | No | FAQ/knowledge base agent |
| Internal productivity | No | IT help desk agent |

### Classification Form

```
Agent Model Classification Form

Agent Name: [Name]
Agent ID: [ID]
Business Owner: [Owner]

Classification Decision:
[ ] Model (requires MRM governance)
[ ] Non-Model (standard agent governance)

Justification:
[Explain why agent does/doesn't qualify as model]

Model Tier (if applicable):
[ ] Tier 1 - High Risk (material business impact)
[ ] Tier 2 - Medium Risk (significant but limited impact)
[ ] Tier 3 - Low Risk (minimal business impact)

Approved by: _________________ Date: _________
Model Risk Manager
```

---

## Part 2: Model Selection Governance

**Portal Path:** Copilot Studio > [Agent] > Settings > AI capabilities > Model

### Model Options

| Model | Availability | Capability Level | FSI Recommendation |
|-------|-------------|------------------|-------------------|
| **GPT-5** | GA (Nov 2025) | Production-ready, default | Approved for all zones |
| **GPT-5.2** | Preview | Experimental capabilities | Zone 1 only; Zone 2/3 disabled |
| **GPT-4o** | GA | Previous generation | Approved for all zones |
| **Custom models** | Varies | Organization-specific | Requires MRM validation |

### Configuration Steps

1. Navigate to **Copilot Studio** > Select agent
2. Click **Settings** > **AI capabilities**
3. Review **Model** selection
4. Document model choice in agent inventory

### Zone-Specific Model Governance

| Zone | Allowed Models | Experimental Models | Documentation |
|------|---------------|---------------------|---------------|
| **Zone 1** | GPT-5, GPT-4o | Allowed for evaluation | Minimal |
| **Zone 2** | GPT-5, GPT-4o | Disabled | Standard MRM |
| **Zone 3** | GPT-5, GPT-4o (approved only) | **Disabled** | Full MRM with validation |

---

## Part 3: Model Inventory Setup

### Create Inventory Registry

**Option 1: Dataverse Table**
- Power Platform Admin Center > Create new Dataverse table

**Option 2: SharePoint List**
- SharePoint > Create list with inventory columns
- Enable version history for audit trail

### Required Inventory Fields

| Field | Description |
|-------|-------------|
| Model ID | Unique identifier |
| Model Name | Agent/model name |
| Model Tier | 1, 2, or 3 |
| Business Purpose | What the model does |
| Model Owner | Business owner |
| Model Developer | Technical owner |
| Primary Users | Who uses the model |
| Data Inputs | Data sources used |
| Model Outputs | Decisions/recommendations |
| Implementation Date | Go-live date |
| Last Validation | Date of last review |
| Next Validation Due | Scheduled review date |
| Performance Status | Green/Yellow/Red |

---

## Part 4: Agent Card Template

### Purpose

Agent Cards provide standardized documentation for each AI agent, capturing capabilities, limitations, training sources, and governance status.

### Agent Card Requirements by Tier

| Requirement | Tier 3 (Low) | Tier 2 (Medium) | Tier 1 (High) |
|-------------|-------------|-----------------|---------------|
| Agent Card Required | Recommended | Required | Required |
| Full Limitations Section | Optional | Required | Required |
| Bias Testing Results | Optional | Required | Required |
| Performance Benchmarks | Basic | Standard | Comprehensive |
| Change History | Summary | Detailed | Full audit trail |
| Review Frequency | Annual | Semi-annual | Quarterly |
| External Validation | No | Recommended | Required |

---

## Part 5: Validation Framework

### Validation Tiers

| Model Tier | Validation Requirements | Frequency |
|------------|------------------------|-----------|
| Tier 1 | Independent third-party | Annual |
| Tier 2 | Independent internal team | Annual |
| Tier 3 | Self-assessment + review | Biennial |

### Validation Scope

**Conceptual Soundness:**
- [ ] Model design is appropriate for intended use
- [ ] Methodology is theoretically sound
- [ ] Assumptions are reasonable and documented
- [ ] Limitations are clearly stated

**Data Quality:**
- [ ] Data sources are appropriate
- [ ] Data quality is acceptable
- [ ] Data preprocessing is appropriate
- [ ] Data is representative of use cases

**Output Analysis:**
- [ ] Outputs are accurate and reliable
- [ ] Performance meets expectations
- [ ] Outputs are consistent over time
- [ ] Edge cases handled appropriately

**Implementation Verification:**
- [ ] Model implemented as designed
- [ ] Controls are effective
- [ ] Documentation is complete
- [ ] Users are properly trained

---

## Part 6: Performance Monitoring

**Portal Path:** Power Platform Admin Center > Analytics > Copilot Studio

### Performance Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Response Accuracy | Correct responses / Total | >95% |
| User Satisfaction | CSAT score | >4.0/5.0 |
| Fallback Rate | Escalations to human | <10% |
| Response Time | Average response latency | <2 seconds |
| Error Rate | Failed conversations | <2% |
| Bias Indicators | Demographic disparity | <5% variance |

### Status Thresholds

- **Green:** All metrics within thresholds
- **Yellow:** 1-2 metrics slightly below threshold
- **Red:** Multiple metrics below threshold or critical failures

---

## Part 7: Change Control

### Change Classification

| Change Type | Description | Governance |
|-------------|-------------|------------|
| Material Change | Affects model outputs significantly | Full revalidation |
| Non-Material Change | Minor updates, bug fixes | Abbreviated review |
| Emergency Change | Critical fix | Expedited process |
| Prompt Change | System/topic prompt updates | See prompt review checklist |

### Prompt Change Categories

| Change Type | Description | Review Level |
|-------------|-------------|--------------|
| **System Prompt** | Core agent instructions | Full review + testing |
| **Topic Prompt** | Topic-specific logic | Standard review |
| **Fallback Prompt** | Unknown input handling | Standard review |
| **Grounding Instructions** | Knowledge source usage | Full review + testing |

---

## Part 8: Multi-Agent Governance

### Zone Restrictions

| Zone | Multi-Agent Allowance |
|------|----------------------|
| **Zone 1** | No agent-to-agent delegation allowed |
| **Zone 2** | Delegation within same zone only; max depth 2 |
| **Zone 3** | Cross-zone delegation with explicit approval; max depth 3 |

### Multi-Agent Risk Considerations

- Treat orchestrated systems as single model for validation
- Document complete delegation chain
- If any agent in chain is Tier 1, treat entire chain as Tier 1
- Validate end-to-end behavior, not just individual agents

---

---

[Back to Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md) | [PowerShell Setup](powershell-setup.md) | [Verification Testing](verification-testing.md) | [Troubleshooting](troubleshooting.md)

---

*Updated: January 2026 | Version: v1.2*
