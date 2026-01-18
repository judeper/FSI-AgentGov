# Control 2.7: Vendor and Third-Party Risk Management - Verification & Testing

> This playbook provides verification and testing guidance for [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md).

---

## Verification Checklist

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Review connector inventory document | Complete list of all third-party connectors |
| 2 | Check vendor security assessments | Current assessments for all Tier 1/2 vendors |
| 3 | Verify contracts have security clauses | Required clauses present in all vendor contracts |
| 4 | Confirm vendor access is monitored | Audit logs showing connector activity |
| 5 | Test DLP policy enforcement | Blocked connectors cannot be used |
| 6 | Review board reporting | Quarterly vendor risk reports delivered |
| 7 | Verify incident response procedures | Documented and tested for vendor issues |

---

## Vendor Assessment Requirements by Zone

| Assessment Area | Zone 1 | Zone 2 | Zone 3 |
|-----------------|--------|--------|--------|
| **Vendor Vetting** | Self-certification | Basic questionnaire | Comprehensive assessment |
| **Security Documentation** | Optional | SOC 2 recommended | SOC 2 Type II required |
| **Contract Review** | Standard terms | Legal review | Security addendum required |
| **Monitoring Frequency** | Annual | Quarterly | Continuous |
| **Audit Rights** | Not required | Recommended | Required |
| **Exit Planning** | Optional | Documented | Tested annually |
| **Board Reporting** | None | Summary | Detailed risk report |

---

## AI Vendor Assessment Questionnaire Sections

### Section A: Model Information

- What AI/ML models power the service?
- How are model updates handled?
- What is the model change notification process?
- Is model documentation (model card) available?

### Section B: Training Data

- What data was used to train the model?
- How is training data governance managed?
- Does the vendor train on customer inputs?
- Are bias testing results available?

### Section C: Output Quality and Safety

- What output quality controls are in place?
- What safety guardrails exist?
- How is output accuracy measured?
- What is the incident response process for AI failures?

### Section D: Transparency and Explainability

- Can outputs be explained?
- What audit capabilities exist?
- Is explainability documentation available?

### Section E: Compliance and Regulatory

- AI-specific certifications held?
- Regulatory examination support?
- AI governance framework?

### Section F: Model Risk Management Integration

- OCC 2011-12/SR 11-7 support?
- Model inventory information provided?

---

## AI Vendor Risk Scoring

| Factor | Weight | Scoring Criteria |
|--------|--------|------------------|
| **Model transparency** | 20% | Full disclosure (low risk) to black box (high risk) |
| **Training data governance** | 15% | Documented and audited (low) to undisclosed (high) |
| **Output quality controls** | 20% | Comprehensive controls (low) to minimal (high) |
| **Customer data protection** | 15% | No training on customer data (low) to unrestricted (high) |
| **Regulatory readiness** | 15% | AI-specific certifications (low) to no attestations (high) |
| **Incident response** | 15% | Defined AI incident process (low) to undefined (high) |

---

## Dynamic Tool Governance Checklist

- [ ] Default-deny policy for runtime tool discovery
- [ ] Plugin allowlist maintained and enforced
- [ ] Community plugins require full security review
- [ ] Automatic updates disabled for third-party tools
- [ ] Transitive data exposure mapped for tool chains
- [ ] Agent-to-agent composition risks assessed
- [ ] Marketplace installations blocked by default
- [ ] Tool chain audit logging enabled
- [ ] Quarterly review of approved tool inventory

---

## Transitive Data Exposure Mapping Template

```
TRANSITIVE DATA EXPOSURE MAPPING
================================
Agent: [Agent Name]

Primary Tool: [Connector Name] ([Publisher])
  └── Data Retrieved: [Data type]

Secondary Tool: [Service Name] ([Third-Party])
  └── Data Sent: [Data type]
  └── Third Party: [Vendor name]
  └── Data Residency: [Location]

Tertiary Tool: [Service Name] ([Third-Party])
  └── Data Sent: [Data type]
  └── Third Party: [Vendor name]
  └── Data Residency: [Location]

RISK ASSESSMENT:
├── Customer data flows to [X] third parties
├── Data residency: [Known/Unknown]
├── Transitive exposure disclosed: [Yes/No]
└── RECOMMENDATION: [Action]
```

---

## Contract Requirements Checklist

### Standard Clauses

- [ ] Data protection and encryption requirements
- [ ] Incident notification (24 hours for critical)
- [ ] Audit rights (annual minimum)
- [ ] Subprocessor approval requirements
- [ ] Data return/destruction on termination

### AI-Specific Clauses

- [ ] Model change notification
- [ ] Training data requirements
- [ ] Output monitoring rights
- [ ] Human oversight provisions
- [ ] Explainability requirements

---

## Related Playbooks

- [Portal Walkthrough](./portal-walkthrough.md) - Step-by-step portal configuration
- [PowerShell Setup](./powershell-setup.md) - Automation scripts
- [Troubleshooting](./troubleshooting.md) - Common issues and solutions

---

*Updated: January 2026 | Version: v1.1*
