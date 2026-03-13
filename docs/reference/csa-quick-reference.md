# CSA Quick Reference

> One-page orientation for Cloud Solution Architects engaging with FSI customers on AI agent governance.

---

## Top 3 Customer Questions

!!! tip "Lead with these — they come up in every engagement"

**1. "How do we control who can build and publish AI agents?"**

→ [Control 1.1 — Restrict Agent Publishing by Authorization](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md). Managed Environments + environment-level maker permissions. Prerequisite: [Control 2.1](../controls/pillar-2-management/2.1-managed-environments.md).

**2. "What compliance evidence do we need for regulators?"**

→ [Control 1.7 — Audit Logging](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md), [Control 3.3 — Compliance Reporting](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md), and [Evidence Standards](evidence-standards.md). Covers FINRA, SEC, OCC, and state regulatory obligations.

**3. "How do we prevent agents from accessing sensitive data?"**

→ [Control 1.4 — DLP/Connector Policies](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md), [Control 1.5 — Sensitivity Labels](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md), and [Control 4.1 — SharePoint IAG](../controls/pillar-4-sharepoint/4.1-sharepoint-information-access-governance-iag-restricted-content-discovery.md). Layered defense: connector restrictions + label-based DLP + grounding-scope governance.

---

## Top 10 Controls for CSA Conversations

| # | Control | Title | Why It Matters | Pillar |
|---|---------|-------|----------------|--------|
| 1 | [1.1](../controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md) | Restrict Agent Publishing | Most-asked control — who can create and share agents | Security |
| 2 | [2.1](../controls/pillar-2-management/2.1-managed-environments.md) | Managed Environments | Prerequisite for 15+ controls; enables zone model | Management |
| 3 | [1.5](../controls/pillar-1-security/1.5-data-loss-prevention-dlp-and-sensitivity-labels.md) | DLP & Sensitivity Labels | Core data protection — blocks exfiltration via agents | Security |
| 4 | [1.4](../controls/pillar-1-security/1.4-advanced-connector-policies-acp.md) | Advanced Connector Policies | Controls which APIs/connectors agents can invoke | Security |
| 5 | [1.7](../controls/pillar-1-security/1.7-comprehensive-audit-logging-and-compliance.md) | Audit Logging & Compliance | FINRA/SEC evidence requirements; retention up to 10 yr | Security |
| 6 | [3.1](../controls/pillar-3-reporting/3.1-agent-inventory-and-metadata-management.md) | Agent Inventory | Foundational — you can't govern what you can't see | Reporting |
| 7 | [2.12](../controls/pillar-2-management/2.12-supervision-and-oversight-finra-rule-3110.md) | FINRA 3110 Supervision | Broker-dealer requirement; supervisory review of agent output | Management |
| 8 | [1.11](../controls/pillar-1-security/1.11-conditional-access-and-phishing-resistant-mfa.md) | Conditional Access & MFA | Zero-trust baseline; phishing-resistant MFA for Zone 3 | Security |
| 9 | [1.23](../controls/pillar-1-security/1.23-step-up-authentication-for-agent-operations.md) | Step-Up Authentication | Re-authentication for high-risk agent operations | Security |
| 10 | [3.3](../controls/pillar-3-reporting/3.3-compliance-and-regulatory-reporting.md) | Compliance Reporting | Automated evidence collection for examiners | Reporting |

---

## Repository Map

```
FSI-AgentGov
│
├── Framework (strategy)          ← WHY: governance model, operating model, regulatory alignment
│   ├── Executive Summary            Start here for leadership conversations
│   ├── Governance Fundamentals      Zones, tiers, lifecycle model
│   ├── Regulatory Framework         FINRA, SEC, OCC, NIST mapping
│   ├── Adoption Roadmap             Phased rollout plan
│   └── Solutions Integration        27 companion automation solutions
│
├── Controls (specifications)     ← WHAT: 71 controls across 4 pillars
│   ├── Pillar 1 – Security & Data Protection       (28 controls)
│   ├── Pillar 2 – Lifecycle Management & Oversight  (24 controls)
│   ├── Pillar 3 – Reporting & Inventory             (12 controls)
│   └── Pillar 4 – SharePoint & Content Governance    (7 controls)
│
├── Playbooks (procedures)        ← HOW: 284 step-by-step implementation guides
│   └── Each control has 3-6 playbooks with portal screenshots and PowerShell
│
├── Assessment                    ← MEASURE: interactive governance readiness tool
│   └── Produces scorecard, gap analysis, and remediation roadmap
│
└── Reference                     ← LOOKUP: glossary, regulatory mappings, portal paths
    └── Evidence standards, RACI matrix, licensing requirements
```

!!! info "Three-layer model"
    **Framework** answers *why* → **Controls** answer *what* → **Playbooks** answer *how*. Start customers at the framework level, then drill into controls relevant to their regulatory profile.

### Pillar Summary

| Pillar | Controls | Scope |
|--------|----------|-------|
| **1 — Security & Data Protection** | 28 | DLP, labels, encryption, MFA, eDiscovery, runtime protection |
| **2 — Lifecycle Management & Oversight** | 24 | Managed environments, change management, FINRA supervision, DR |
| **3 — Reporting & Inventory** | 12 | Agent inventory, usage analytics, compliance reports, Sentinel |
| **4 — SharePoint & Content** | 7 | IAG, site access reviews, retention, guest controls, grounding scope |

---

## Governance Zones at a Glance

The framework uses a three-zone model to scale controls with risk:

| Zone | Scope | Sharing | Key Controls | Typical Agents |
|------|-------|---------|--------------|----------------|
| **Zone 1** | Personal | Creator only | 1.1, 1.5, 2.1 | Personal productivity, prototyping |
| **Zone 2** | Team | Shared with colleagues | Zone 1 + 1.4, 3.1, 4.1 | Team assistants, department tools |
| **Zone 3** | Enterprise | Org-wide / external | Zone 2 + 1.7, 1.11, 2.8, 2.12, 3.3 | Customer-facing, regulated workflows |

Controls compound as agents move up zones. Zone 3 requires all Phase 0 and Phase 1 controls.

See: [Governance Fundamentals](../framework/governance-fundamentals.md) · [Zones and Tiers](../framework/zones-and-tiers.md)

---

## Quick Links

| Resource | Description | Path |
|----------|-------------|------|
| Governance Readiness Assessment | Interactive tool — produces scorecard and gap analysis | [assessment/index.md](../assessment/index.md) |
| Control Catalog | All 71 controls with priority and ownership | [controls/index.md](../controls/index.md) |
| Executive Summary | 2-page leadership overview | [framework/executive-summary.md](../framework/executive-summary.md) |
| Solutions Integration | How 27 solutions map to controls | [framework/solutions-integration.md](../framework/solutions-integration.md) |
| Adoption Roadmap | Phased rollout with success criteria | [framework/adoption-roadmap.md](../framework/adoption-roadmap.md) |
| Regulatory Mappings | FINRA, SEC, OCC, NIST crosswalks | [regulatory-mappings.md](regulatory-mappings.md) |
| Portal Paths Quick Reference | Admin center URLs for every control | [portal-paths-quick-reference.md](portal-paths-quick-reference.md) |
| Evidence Standards | What auditors expect per control | [evidence-standards.md](evidence-standards.md) |
| License Requirements | SKU prerequisites by control | [license-requirements.md](license-requirements.md) |
| Glossary | Term definitions | [glossary.md](glossary.md) |
| Companion Solutions | 27 automation repos on GitHub | [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) |

---

## Key Regulatory Drivers

!!! info "Know your customer's regulators"
    The framework maps controls to specific regulatory obligations. Lead with the regulations that apply to your customer's institution type.

| Institution Type | Primary Regulators | Critical Controls |
|-----------------|-------------------|-------------------|
| Broker-Dealer | FINRA, SEC | 2.12 (3110 Supervision), 1.7 (Audit), 1.9 (Retention), 3.3 |
| Bank / Thrift | OCC, FDIC, Fed | 2.6 (Model Risk / SR 11-7), 2.8 (SoD), 1.7 (Audit) |
| Insurance | State DOIs, NAIC | 1.5 (DLP), 2.14 (Training), 3.1 (Inventory) |
| RIA / Advisor | SEC | 1.7 (Audit), 2.13 (Record-Keeping), 3.3 (Reporting) |

Full regulatory crosswalk: [Regulatory Mappings](regulatory-mappings.md) · [NIST AI RMF Crosswalk](nist-ai-rmf-crosswalk.md)

---

## Implementation Phases

!!! tip "Run the [Governance Readiness Assessment](../assessment/index.md) first to scope Phase 0 priorities"

| Phase | Window | Focus | Key Controls |
|-------|--------|-------|--------------|
| **Phase 0 — Foundation** | 0–60 days | Governance structure, core controls, Zones 1–2 | 1.1, 1.5, 2.1, 3.1, 4.1 |
| **Phase 1 — Production Ready** | 2–6 months | Audit, retention, segregation, supervision, Zone 3 | 1.7, 1.9, 1.11, 2.8, 2.12, 3.3 |
| **Phase 2 — Advanced** | 6–12 months | Content moderation, insider risk, eDiscovery, Sentinel | 1.6, 1.8, 1.19, 2.20, 3.9, 3.10 |
| **Phase 3 — Optimization** | Ongoing | Hallucination feedback, multi-agent orchestration, tuning | 2.17, 3.10, 2.16 |

### Phase 0 — What to prioritize in first customer engagement

1. **Enable Managed Environments** (2.1) — unlocks sharing controls, DLP enforcement, and maker restrictions
2. **Restrict agent publishing** (1.1) — most urgent customer concern; requires Managed Environments
3. **Apply DLP and sensitivity labels** (1.5) — prevents data leakage via connectors and grounding sources
4. **Stand up agent inventory** (3.1) — visibility prerequisite for all reporting controls
5. **Scope SharePoint IAG** (4.1) — restricts which content agents can access for grounding

### Phase 1 — Production readiness gates

- Audit logging with retention configured (1.7, 1.9)
- Segregation of duties between makers and approvers (2.8)
- FINRA 3110 supervision workflow for broker-dealers (2.12)
- Conditional access with phishing-resistant MFA for Zone 3 (1.11)
- Compliance reporting process operational (3.3)

### Critical-path dependencies

```
2.1 Managed Environments ──→ 1.1 Restrict Publishing ──→ 3.1 Agent Inventory
                         └──→ 1.7 Audit Logging ──→ 3.3 Compliance Reporting
```

Control 2.1 is the single most important prerequisite. Without Managed Environments, most governance controls cannot be enforced.

Full details: [Adoption Roadmap](../framework/adoption-roadmap.md)

---

## Automation Coverage

**27 companion solutions** in [FSI-AgentGov-Solutions](https://github.com/judeper/FSI-AgentGov-Solutions) cover **34+ controls** with ready-to-deploy Power Platform and Azure automation.

!!! info "Gap analysis"
    Run the [Governance Readiness Assessment](../assessment/index.md) to identify which controls lack automation and need manual procedures. See [Solutions Coverage Gaps](solutions-coverage-gaps.md) for the full gap inventory.

| Solution | Controls Covered | Use Case |
|----------|-----------------|----------|
| Environment Lifecycle Management | 2.1, 2.2, 2.15 | Automated environment provisioning with zone classification |
| Compliance Dashboard | 3.3, 3.7 | Consolidated compliance posture view for governance leads |
| FINRA Supervision Workflow | 2.12 | Supervisory review queue for agent-generated outputs |
| Deny Event Correlation Report | 1.7, 1.4 | Aggregated block events from Purview, DLP, App Insights |
| Audit Compliance Manager | 1.7, 1.9 | Audit log collection with configurable retention |
| Segregation Detector | 2.8 | Detects maker/approver role conflicts |
| Conditional Access Automation | 1.11 | Deploys CA policies for agent-related scenarios |
| Content Moderation Monitor | 1.27 | Monitors agent content filtering effectiveness |
| Hallucination Tracker | 3.10 | Captures and trends hallucination feedback |
| Agent Access Monitor | 1.2 | Tracks agent registration and integrated app changes |

Full mapping: [Solutions Integration](../framework/solutions-integration.md)

---

## See Also

- [CSA Positioning Guide](csa-positioning-guide.md) — Do's and don'ts for customer conversations
- [Start Here](../start-here.md) — Customer-facing orientation (share with customers directly)
- [FAQ](faq.md) — Frequently asked questions
- [RACI Matrix](raci-matrix.md) — Role assignments across all 71 controls
- [License Requirements](license-requirements.md) — SKU prerequisites by control
- [Regulatory Mappings](regulatory-mappings.md) — FINRA, SEC, OCC, NIST crosswalks
