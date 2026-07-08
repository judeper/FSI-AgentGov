---
description: "Orient yourself to the FSI Agent Governance Framework in about 30 minutes."
search:
  boost: 2
---
# Quick Start Guide

Orient yourself to the FSI Agent Governance Framework in about 30 minutes. By the end you will have classified an agent into a zone, identified your applicable regulations, and taken a first concrete action.

!!! tip "Prefer to act first?"
    [Run the Readiness Assessment](../assessment/index.md) — about 15 minutes. It evaluates your organization's current state across all 79 controls and generates a personalized remediation roadmap.

---

## Step 1: Understand the Framework Structure (3 min)

The framework has **4 pillars** and **3 zones**:

**4 Pillars (types of governance):**

1. Security (29 controls) — Protect data and access
2. Management (27 controls) — Govern the agent lifecycle
3. Reporting (14 controls) — Monitor and report on activity
4. SharePoint (9 controls) — Govern SharePoint-integrated agents

**3 Zones (governance depth by risk level):**

1. Zone 1 — Personal Productivity (low risk, ~1 day for foundational controls)
2. Zone 2 — Team Collaboration (medium risk, ~1 week for baseline)
3. Zone 3 — Enterprise Managed (high risk, 6–8 weeks for comprehensive coverage)

For a full explanation of how zones work, see [Zones and Tiers](../framework/zones-and-tiers.md).

!!! info "Platform and license overlay"
    The framework's three-zone model — Personal Productivity, Team Collaboration, and Enterprise Managed — classifies agent risk, governance friction, and approval depth. License tier is an orthogonal axis: Microsoft 365 Copilot, Microsoft Agent 365, Microsoft 365 E5, and Power Platform entitlements determine which platform features are available to govern. Apply both axes to every agent: choose the zone first, then verify the tenant license enables the controls and evidence surfaces needed for that zone. See [License Requirements](../reference/license-requirements.md) and the [Agent 365 Capabilities Summary](../reference/agent-365-capabilities-summary.md) before writing implementation dependencies into policy.

---

## Step 2: Classify Your First Agent (5 min)

Ask these questions:

**Q: Who uses this agent?**

- Just me? → Zone 1
- My team or department? → Zone 2
- Organization-wide or customer-facing? → Zone 3

**Q: What data does it access?**

- Only my personal data? → Zone 1
- Departmental data? → Zone 2
- Regulated or customer data? → Zone 3

**Result:** You've classified your first agent into a governance zone. Start with the controls for that zone.

---

## Step 3: Identify Your Applicable Regulations (2 min)

Check which regulators apply to your organization:

- FINRA? (broker-dealers)
- SEC? (investment advisers, public companies)
- SOX? (public companies)
- GLBA? (all financial institutions)
- OCC? (national banks)
- Federal Reserve? (bank holding companies, state member banks)
- CFTC? (futures commission merchants, swap dealers, commodity pools — Rule 1.31 recordkeeping)
- FDIC? (state non-member banks, savings associations)
- NCUA? (credit unions)
- State insurance regulator? (insurers)
- NYDFS Part 500? (NY-licensed institutions)

Consult your Compliance Officer to confirm which apply. Note: FDIC, NCUA, state insurance, and NYDFS Part 500 regulatees should apply the framework's analogous controls, but these regulations are not explicitly mapped in the Control Catalog. Then see the [Regulatory Framework](../framework/regulatory-framework.md) for the control-to-regulation mapping.

---

## Common Scenarios

### Scenario 1: Zone 1 Agent (Personal Productivity)

**Time Required:** 1 day

**Steps:**

1. Create agent in personal environment
2. Document agent purpose
3. Verify audit logging (platform default: 180 days Audit Standard / 1 year Audit Premium-E5; do not reduce below default)
4. No approval needed

**Controls Required:**

- Basic documentation
- Minimal governance

**Compliance:** Minimal — regulatory obligations may still apply depending on organizational policies and the nature of interactions. See [Zones and Tiers](../framework/zones-and-tiers.md) for details.

---

### Scenario 2: Zone 2 Team Agent (Department)

**Time Required:** 1 week

**Steps:**

1. Get manager approval
2. Classify agent to Zone 2
3. Identify data sources
4. Configure DLP and audit
5. Document approval
6. Train team members

**Controls Required (minimum):**

- 1.2 Agent Registry
- 1.5 DLP and Labels
- 1.7 Audit Logging (1 year)
- 1.11 Conditional Access
- 2.3 Change Management
- 2.12 Supervision

**Compliance:** FINRA 3110 supervision

---

### Scenario 3: Zone 3 Production Agent (Customer-Facing)

**Time Required:** 3-6 weeks

**Steps:**

1. Establish governance committee
2. Risk assessment and business case
3. Security testing
4. Bias testing (if applicable)
5. Model risk assessment
6. Legal and compliance review
7. Change control process
8. Incident response procedures
9. Governance committee approval
10. Production deployment

**Controls Required (comprehensive):**

- All 79 controls apply
- Enhanced versions per regulation

**Compliance:**

- FINRA comprehensive
- SEC Rule 17a-3/4
- SOX 302/404
- GLBA 501(b)
- OCC Bulletin 2026-13 (formerly OCC 2011-12) / Fed SR 26-2 (formerly Fed SR 11-7) (if applicable — note: both documents explicitly exclude generative AI and agentic AI from scope; apply analogous MRM principles as best practice and consult compliance counsel)

---

## Where to Go Next

| What you need | Where to go |
|---------------|-------------|
| Week-by-week deployment plan | [Implementation Checklist](checklist.md) |
| Scenario-based routing guide | [Start Here](../start-here.md) |
| Formal gap assessment | [Readiness Assessment](../assessment/index.md) |
| Browse all 79 controls | [Control Index](../controls/index.md) |
| Step-by-step implementation playbooks | [Playbooks](../playbooks/index.md) |
| Term definitions | [Glossary](../reference/glossary.md) |

---

## Still Have Questions?

- Check **[FAQ](../reference/faq.md)** for common questions
- Review **[Glossary](../reference/glossary.md)** for terms
- Contact your **Compliance Officer** for regulatory questions
- Ask your **Power Platform Admin** for technical setup

---

*FSI Agent Governance Framework v1.6.2 — May 2026*