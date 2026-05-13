# Control 2.7: Vendor and Third-Party Risk Management — Verification & Testing

> Companion to [Control 2.7](../../../controls/pillar-2-management/2.7-vendor-and-third-party-risk-management.md). Verification confirms vendor risk management is operating as designed and produces the evidence financial-services examiners and internal audit will request.

---

## Verification Checklist

| # | Test | Expected Evidence | Pass Criteria |
|---|------|-------------------|---------------|
| 1 | Connector inventory currency | Inventory CSV with timestamp ≤ 7 days for Zone 2/3, ≤ 30 days for Zone 1 | All Zone 2/3 environments represented; reviewer initials present |
| 2 | Risk-tier completeness | Tier T1–T5 populated for every row; T3/T4/T5 connectors have a documented business owner | Zero blanks in Tier or Owner columns for Zone 2/3 |
| 3 | DLP enforcement of Blocked tier | Test agent attempts to add a Blocked connector | Add operation fails with policy-block message; Purview audit event recorded |
| 4 | Custom connector restriction | Power Platform admin center shows custom connector creation restricted in Zone 2/3 to designated environments | Producer environments are explicit; no Zone 1 production environments allow custom |
| 5 | SOC 2 / equivalent on file | Vendor file shows SOC 2 Type II within validity window OR accepted alternative + risk-acceptance memo | Coverage = 100% of Tier T2–T5 vendors |
| 6 | AI-specific contract clauses | Procurement export shows clause flags for model change notice, no-training-on-customer-data, AI incident notice, audit rights | Coverage = 100% of Tier T5 vendors |
| 7 | Transitive data-flow map | Architecture artifact lists every downstream subprocessor reached by Zone 3 multi-tool agents | One map per Zone 3 multi-tool agent; reviewed within last 12 months |
| 8 | Quarterly governance reporting | Meeting minutes / committee deck referencing the report | At least one report per quarter in last 12 months |
| 9 | Vendor incident drill | Tabletop exercise log for at least one Zone 3 critical vendor | Conducted within last 12 months; gaps captured and remediated |
| 10 | Records retention | Evidence repository governed by Purview retention aligned to FINRA 4511 / SEC 17a-4 schedule | Retention label applied; deletion holds in effect during open exams |

---

## Vendor Assessment Requirements by Zone

| Assessment Area | Zone 1 | Zone 2 | Zone 3 |
|-----------------|--------|--------|--------|
| Vendor vetting | Self-attestation; Microsoft / verified-publisher only | Documented questionnaire | Risk-tiered due diligence aligned to Interagency 2023 Guidance |
| Security documentation | None required (Microsoft baseline relied on) | SOC 2 Type II recommended | SOC 2 Type II required (SOC 1 where SOX-relevant) |
| Contract review | Standard terms | Legal review with security addendum | Negotiated security and AI addendum; audit rights |
| Monitoring frequency | Annual | Quarterly | Continuous (telemetry + advisory feeds) |
| Audit rights | Not required | Recommended | Required (or accepted SOC 2 in lieu) |
| Exit / contingency planning | Optional | Documented | Documented and tabletop-tested annually |
| Reporting cadence | None | Summary to AI governance | Detailed report to AI governance + risk/board committee |

---

## AI-Specific Vendor Assessment Questionnaire

### Section A — Model Information
- Which AI/ML models power the service? List provider, model family, and current version.
- How are model updates handled? What is the customer notification process and lead time?
- Is a model card or equivalent documentation available on request?
- Does the vendor maintain a documented evaluation suite (accuracy, safety, bias)?

### Section B — Training Data Governance
- Is customer data used to train, fine-tune, or improve any vendor model? If yes, under what consent mechanism?
- Are training data sources documented? Is provenance traceable?
- Are bias or fairness evaluation results available?
- How are data subject rights (GLBA, state privacy law) supported?

### Section C — Output Quality and Safety
- What output safety guardrails exist (content filters, jailbreak resistance)?
- How is hallucination rate measured and reported?
- What is the incident response process for AI-specific failures (e.g., harmful or non-compliant output)?
- Is human-in-the-loop available for high-risk operations?

### Section D — Transparency and Explainability
- Are outputs explainable or auditable to the prompt and tool calls that produced them?
- Is end-to-end logging available to the customer for AI interactions?
- Does the vendor support content provenance signals (e.g., C2PA) for generated content?

### Section E — Compliance and Regulatory Alignment
- Which AI-specific certifications or attestations does the vendor hold (e.g., ISO/IEC 42001)?
- Does the vendor support customer regulatory examinations (FINRA, SEC, OCC, Federal Reserve)?
- Is a documented AI governance framework (NIST AI RMF or equivalent) in place?

### Section F — Model Risk and Recordkeeping Integration
- Does the vendor support OCC 2011-12 / Fed SR 11-7 model risk management workflows (model inventory, validation evidence)?
- Can AI-generated content be archived in a SEC 17a-4(f) / FINRA 4511-compliant manner?
- Can records be distinguished as AI-generated vs human-generated?

---

## AI Vendor Risk Scoring Rubric

| Factor | Weight | Low (1) | High (5) |
|--------|-------:|---------|----------|
| Model transparency | 20% | Full disclosure (model card, version, eval) | Black box, undocumented |
| Training data governance | 15% | Documented, audited, no customer training | Undisclosed, customer data used |
| Output quality controls | 20% | Comprehensive guardrails, measured | Minimal, unmeasured |
| Customer data protection | 15% | No training, regional residency, encryption | Unrestricted use, unclear residency |
| Regulatory readiness | 15% | ISO 42001 / NIST AI RMF aligned, exam-ready | No attestations, no exam support |
| Incident response | 15% | Defined AI-incident process, tested | Undefined / ad-hoc |

Weighted score ≥ 4.0 → Tier T5 (high); 2.5–3.9 → enhanced monitoring; ≤ 2.4 → standard.

---

## Dynamic Tool / Plugin / MCP Governance Checklist

- [ ] Default-deny posture for runtime tool discovery in Zone 2/3 agents
- [ ] Plugin and MCP allowlist maintained per agent
- [ ] Independent-publisher and community plugins blocked unless reviewed
- [ ] Auto-update disabled for non-Microsoft tools
- [ ] Transitive data-flow map exists for every Zone 3 multi-tool agent
- [ ] Marketplace installations blocked at the tenant level
- [ ] Tool-call logging enabled (request, response metadata, identity)
- [ ] Quarterly review of approved tool inventory completed and signed off
- [ ] MCP tool servers traverse only approved network egress paths

---

## Transitive Data Exposure Map (Template)

```text
TRANSITIVE DATA EXPOSURE MAP
============================
Agent:        [Agent name]                     Zone: [1/2/3]
Owner:        [Business owner]                 Reviewed: [YYYY-MM-DD]

Tool 1: [Connector / plugin / MCP]
  Publisher: [Microsoft / Verified / Independent / Custom / MCP server]
  Data sent: [Class — e.g., customer NPI, MNPI, supervisory log]
  Vendor:    [Name]
  Subprocessors: [List]
  Residency: [Region]
  Recordkeeping coverage: [Yes / No / Partial — reference]

Tool 2: ...

Tool N: ...

Aggregate risk:
  Number of distinct vendors reached: [N]
  Number of distinct subprocessors reached: [N]
  Customer data leaves [primary region]?: [Yes / No]
  Recordkeeping gaps identified: [List]
  Compensating controls: [List]
  Recommendation: [Allow / Restrict / Block / Re-architect]
```

---

## Contract Requirements Checklist

### Standard clauses
- [ ] Encryption (in transit and at rest)
- [ ] Incident notification SLA (24 hours for critical)
- [ ] Audit rights (annual minimum) or SOC 2 acceptance
- [ ] Subprocessor approval and notification
- [ ] Data return / destruction at termination
- [ ] Indemnification aligned to data class handled

### AI-specific clauses
- [ ] Material model change notice (≥ 30 days)
- [ ] Training data restrictions (no training on customer data without consent)
- [ ] AI incident notification (24 hours for integrity / safety incidents)
- [ ] Output monitoring and audit support
- [ ] Human oversight provisions where decisions affect customers
- [ ] Explainability commitments

### FSI-specific clauses
- [ ] Books-and-records vendor: SEC 17a-4(f) / FINRA 4511 attestation
- [ ] Communication archiving vendor: AI-generated content tagging
- [ ] Identity verification vendor: synthetic identity / deepfake detection capability
- [ ] LLM provider: data residency aligned to firm's books-and-records jurisdiction

---

## Evidence Package for Examination

For each examination cycle, assemble:

1. Latest connector inventory snapshot (CSV + SHA-256 manifest)
2. DLP policy export and effective-policy report
3. Custom connector inventory and creation-restriction screenshot
4. Per-vendor due diligence pack (Tier T2–T5)
5. Quarterly vendor risk reports for the prior 12 months
6. Transitive data-flow maps for Zone 3 multi-tool agents
7. Exit-plan tabletop minutes for Zone 3 critical vendors
8. Records-retention configuration showing FINRA 4511 / SEC 17a-4 alignment

---

## Related Playbooks

- [Portal Walkthrough](portal-walkthrough.md)
- [PowerShell Setup](powershell-setup.md)
- [Troubleshooting](troubleshooting.md)

---

*Updated: April 2026 | Version: v1.6.2 | UI Verification Status: Current*
