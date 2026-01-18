# Control 2.6: Model Risk Management - Verification & Testing

> This playbook provides verification and testing guidance for [Control 2.6](../../../controls/pillar-2-management/2.6-model-risk-management-alignment-with-occ-2011-12-sr-11-7.md).

---

## Verification Checklist

### Classification Verification

- [ ] All agents reviewed for model classification
- [ ] Model/non-model decisions documented
- [ ] Model tier assignments justified

### Documentation Verification

- [ ] Model development docs complete
- [ ] Validation reports current
- [ ] Change control documentation maintained

### Monitoring Verification

- [ ] Performance dashboards operational
- [ ] Alerts configured
- [ ] Regular reporting in place

### Governance Verification

- [ ] MRM committee oversight
- [ ] Validation schedule maintained
- [ ] Regulatory examination package ready

---

## Compliance Checklist

- [ ] Agent-as-model classification completed
- [ ] Model inventory maintained
- [ ] Validation program established
- [ ] Performance monitoring active
- [ ] Change control process documented
- [ ] Agent manifest versioning implemented
- [ ] Point-in-time reconstruction capability verified
- [ ] Rollback procedures documented and tested
- [ ] Regulatory examination package ready

---

## Validation Report Template

```markdown
# Model Validation Report
## [Model Name] - [Validation Date]

### Validation Scope
- Validation type: [Initial / Annual / Ad-hoc]
- Validator: [Name/Firm]
- Independence statement: [Confirm no development involvement]

### Summary of Findings
| Area | Finding | Severity | Recommendation |
|------|---------|----------|----------------|
| [Area] | [Finding] | [Severity] | [Recommendation] |

### Detailed Assessment
[Section for each validation area]

### Conclusion
- Overall validation status: [Approved / Conditional / Not Approved]
- Conditions (if any): [List conditions]
- Next validation date: [Date]

### Sign-off
Validator: _________________ Date: _________
Model Risk Manager: _________________ Date: _________
```

---

## Explainability Testing

### Citation and Source Attribution

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Source Identification | Agent cites specific documents/sources used | Review 50+ sample responses |
| Citation Accuracy | Cited sources contain the referenced information | Spot-check 10% of citations |
| Confidence Indication | Agent indicates certainty level when appropriate | Pattern analysis of responses |

### Counterfactual Testing Template

```markdown
# Counterfactual Test Results

## Agent: [Name]
## Test Date: [Date]

### Baseline Scenario
Input: [Baseline input]
Output: [Agent response]

### Counterfactual Tests
| Change | New Output | Expected? | Notes |
|--------|-----------|-----------|-------|
| [Change 1] | [Output] | [Yes/No] | [Notes] |
| [Change 2] | [Output] | [Yes/No] | [Notes] |

### Validation
- [ ] Output changes align with documented business rules
- [ ] Protected characteristics do not influence decisions
- [ ] Threshold behaviors are consistent
```

---

## Agent Card Requirements

### Tier 1 (High Risk)

- Agent Card required
- Full limitations section
- Bias testing results
- Comprehensive performance benchmarks
- Full audit trail change history
- Quarterly review frequency
- External validation required

### Tier 2 (Medium Risk)

- Agent Card required
- Full limitations section
- Bias testing results
- Standard performance benchmarks
- Detailed change history
- Semi-annual review frequency
- External validation recommended

### Tier 3 (Low Risk)

- Agent Card recommended
- Optional limitations section
- Optional bias testing
- Basic performance benchmarks
- Summary change history
- Annual review frequency
- No external validation required

---

## Manifest Version Control Review

```markdown
# Agent Manifest Version Control Review

## Agent Information
- **Agent Name/ID:** [Name]
- **Current Version:** [X.Y.Z]
- **Zone:** [1/2/3]
- **Review Date:** [Date]

## Version Control
- [ ] Manifest stored in approved version control system
- [ ] All changes tracked with commit messages
- [ ] Version numbers follow convention
- [ ] Change approvals documented

## Reconstruction Capability
- [ ] Can retrieve manifest for any date within retention period
- [ ] Reconstruction procedure documented and tested
- [ ] Reconstruction exercise completed within last 12 months

## Rollback Capability
- [ ] Rollback procedure documented
- [ ] Rollback tested within last 6 months
- [ ] Rollback authority matrix current

## Audit Trail
- [ ] Complete change history maintained
- [ ] Retention meets regulatory requirements
- [ ] Access to manifest history is logged

## Sign-Off
Reviewed by: _________________ Date: _________
AI Governance Lead: _________________ Date: _________
```

---

## Regulatory Examination Readiness

### Documentation Package

- Model inventory (complete list)
- Model development documentation
- Validation reports
- Performance monitoring reports
- Change control documentation
- Issue/finding tracking

### Examination Response Template

```
Model Risk Management Summary for Examination

Total Models in Inventory: [Number]
- Tier 1 (High Risk): [Number]
- Tier 2 (Medium Risk): [Number]
- Tier 3 (Low Risk): [Number]

AI/Agent Models: [Number]

Validation Status:
- Current (validated within required period): [Number]
- Overdue: [Number]

Performance Status:
- Green (meeting thresholds): [Number]
- Yellow (watch list): [Number]
- Red (remediation required): [Number]

Open Findings: [Number]
- High severity: [Number]
- Medium severity: [Number]
- Low severity: [Number]

Key Issues/Remediation:
[Summary of significant issues and status]
```

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.1*
