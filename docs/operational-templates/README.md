# Operational Templates & Specifications

**Status:** Added January 2026 to support FSI-AgentGov v1.0 framework implementation

This section provides practical, production-ready templates and technical specifications that operationalize the existing 48 controls across the four pillars.

---

## What Are Operational Templates?

The framework's 48 controls define *what* governance actions are required and *why* they're important for regulatory compliance. Operational templates translate those controls into concrete, executable processes and templates that teams can implement immediately.

**Framework Pillar** → **Control** → **Operational Template**

*Example:*
- **Pillar 2 (Management)** → **Control 2.12 (Supervision and Oversight)** → **Escalation Decision Matrix** (this section)

---

## Template Categories

### Templates (Implementation Checklists & Matrices)

Ready-to-use templates that provide structure for governance processes.

| Template | Related Control(s) | Purpose |
|----------|-------------------|---------|
| [Action Authorization Matrix](templates/action-authorization-matrix.md) | 2.8, 2.12, 1.4 | Define agent capabilities, hard limits, and allowed/prohibited actions |
| [Agent Inventory Entry](templates/agent-inventory-entry.md) | 3.1, 1.2 | Standardized metadata for tracking deployed agents |
| [Colorado AI Impact Assessment](templates/colorado-ai-impact-assessment.md) | 2.6 | High-risk AI system assessment (optional - for Colorado operations) |
| [Decision Log Schema](templates/decision-log-schema.md) | 1.7, 3.4 | Structured logging of agent decision reasoning and inputs |
| [DSPM for AI Policy Pack](templates/dspm-for-ai-policy-pack.md) | 1.6, 1.5 | Data Security Posture Management prerequisites for AI agents |
| [Escalation Matrix](templates/escalation-matrix.md) | 2.12, 2.3 | Define escalation triggers, SLAs, and authority paths |
| [Per-Agent Data Policy](templates/per-agent-data-policy.md) | 1.5, 1.6, 1.14 | Agent-specific allowed/prohibited data handling rules |
| [Purview Audit Query Pack](templates/purview-audit-query-pack.md) | 3.9, 1.7 | KQL queries for M365 Purview audit log analysis |
| [Supply Chain Risk Register Entry](templates/supply-chain-risk-register-entry.md) | 2.7 | AI-specific third-party vendor risk assessment |

### Specifications (Technical Blueprints)

Detailed technical specifications for governance infrastructure and continuous monitoring.

| Specification | Related Control(s) | Purpose |
|---------------|-------------------|---------|
| [Confidence & Routing Workflow](specs/confidence-and-routing.md) | 2.9, 3.4 | Route low-confidence agent outputs for human review |
| [Evidence Pack Assembly](specs/evidence-pack-assembly.md) | 1.7, 3.1, 3.4 | Audit-ready evidence collection for regulatory exams |
| [Real-time Compliance Dashboard](specs/real-time-compliance-dashboard.md) | 3.8, 3.9, 3.2 | Governance metrics and exception monitoring dashboard |
| [Scope Creep Detection](specs/scope-creep-detection.md) | 1.14, 1.7, 3.2 | Behavioral drift monitoring for agents |
| [Zone 1 Minimum Explainability](specs/zone1-min-explainability.md) | 1.7, 3.1 | Baseline logging for low-risk "informational" agents |

### Modules (Specialized Frameworks)

Comprehensive frameworks for specialized governance areas.

| Module | Related Control(s) | Purpose | Applicability |
|--------|-------------------|---------|---------------|
| [Colorado AI Act Readiness](modules/colorado-ai-act-readiness.md) | 2.6, 3.3 | Impact assessments and compliance tracking for SB24-205 | **Optional** - for CO operations only |

---

## How to Use This Section

### For Governance Teams Implementing Controls

1. **Read the relevant control** in the framework (e.g., Control 2.12 Supervision and Oversight)
2. **Find the related template/spec** in this section (e.g., Escalation Matrix)
3. **Adapt the template** to your organization's specific use cases
4. **Document your implementation** using the framework structure
5. **Reference this template** in your compliance documentation

### For Auditors & Examiners

These templates provide concrete evidence of governance implementation:
- Completed escalation matrices show defined authorization and oversight procedures
- Filled decision logs demonstrate compliance with audit logging requirements
- Dashboard evidence packs show continuous monitoring capabilities

### For Regulatory Review

All templates support compliance with:
- **FINRA Notice 25-07** (GenAI governance)
- **SEC 2026 Exam Priorities** (AI representation and alignment)
- **OCC 2011-12 / SR 11-7** (Model risk management)
- **Colorado SB24-205** (High-risk AI systems) *(optional)*
- **Federal Reserve AI governance expectations**

---

## Integration with Existing Controls

Each template and spec is **designed as an enhancement to existing controls**, not a replacement.

**Example Integration:**

**Control 1.7 (Audit Logging):** Establishes audit logging infrastructure
- ↓ Operationalized by ↓
**Decision Log Schema:** Defines *what* to log (decision inputs, rules applied, outputs)
- ↓ Further specified by ↓
**Evidence Pack Assembly:** Shows *how* to collect and present logs for compliance exams

**Result:** Comprehensive audit capability from infrastructure → implementation → evidence

---

## Zone Guidance

Templates are mapped to governance zones based on agent risk:

| Zone | Templates/Specs | Mandatory? |
|------|-----------------|-----------|
| **Zone 1: Personal Productivity** | Zone 1 Explainability; Agent Inventory | Baseline |
| **Zone 2: Team Collaboration** | Confidence & Routing; Decision Logs | Recommended |
| **Zone 3: Enterprise Managed** | All templates; Real-time Dashboard; Supply Chain Risk | Regulated |

---

## Implementation Timeline

### Phase 1: Feb 28, 2026 (Critical Path)
- Action Authorization Matrix
- Decision Log Schema
- Escalation Matrix
- Confidence & Routing

### Phase 2: Apr 30, 2026
- Real-time Compliance Dashboard
- Per-Agent Data Policy
- Supply Chain Risk Register
- Evidence Pack Assembly

### Phase 3: Jun 30, 2026
- Colorado AI Act Readiness *(if applicable)*

---

## Technical Prerequisites

### For Dashboard & Detection Specs
- Microsoft 365 Purview audit logging enabled
- Power BI or Sentinel integration capability
- Purview API access for custom queries

### For Policy & Process Templates
- Governance committee or oversight body
- TPRM (Third-Party Risk Management) process
- Change management framework (Control 2.3)
- Incident reporting process (Control 3.4)

### For AI-Specific Policies
- Copilot Studio deployment environment
- Power Automate for workflow automation
- SharePoint/Teams governance (Pillar 4)

---

## Documentation Standards

All templates in this section follow FSI-AgentGov conventions:

- **Language:** Supports compliance with [regulation] (never "ensures" or "guarantees")
- **Audience:** M365 administrators in US financial services
- **Scope:** US-only, Microsoft 365 Copilot agents
- **Versioning:** Aligned with framework v1.0 (January 2026)
- **Regulatory:** FINRA, SEC, SOX, GLBA, OCC, Fed SR 11-7, Colorado SB24-205 *(optional)*

---

## Version History

### v1.0 (January 2026)
- Initial release of 9 templates and 5 specifications
- Colorado AI Act readiness module (optional)
- Full validation report included

---

## Support & Questions

For questions about specific templates or specifications:
1. **Read the template header** - Contains prerequisites and related controls
2. **Check related control docs** - The framework control explains the *why*
3. **Review VALIDATION-REPORT.md** - Assessment of technical feasibility and implementation approach
4. **Contact governance team** - Role-based contacts listed in related control files (Pillar controls, Section 11)

---

## Related Resources

- **[CONTROL-INDEX.md](../reference/CONTROL-INDEX.md)** - Master list of all 48 controls
- **[Regulatory Mappings](../reference/regulatory-mappings.md)** - How controls map to regulations
- **[Role Catalog](../reference/role-catalog.md)** - Canonical role names

> **Validation Report:** A technical and regulatory feasibility assessment is maintained in `maintainers-local/reviews/2026-01-jan-update-review/VALIDATION-REPORT.md` for internal reference

---

*FSI Agent Governance Framework v1.0 - January 2026*
*Operational Templates: January 2026*
