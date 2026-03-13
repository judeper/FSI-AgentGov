# CSA Positioning Guide

> Guidance for Cloud Solution Architects on positioning FSI-AgentGov in customer engagements.

---

## What FSI-AgentGov Is

- **Open-source governance framework** for Microsoft 365 AI agents (Copilot Studio, M365 Copilot)
- Designed for **regulated financial services** — banks, broker-dealers, insurance, credit unions
- **71 controls** across 4 pillars mapped to FINRA, SEC, OCC, GLBA, FDIC, NCUA, and Federal Reserve regulations
- **284 implementation playbooks** with click-by-click portal walkthroughs, PowerShell scripts, verification steps, and troubleshooting
- **27 companion Power Platform solutions** for automated governance enforcement
- **Governance Readiness Assessment** tool for quantitative gap analysis

## What FSI-AgentGov Is NOT

!!! warning "Be precise about what FSI-AgentGov is not"

- **Not a Microsoft product or service** — independent open-source project
- **Not a replacement** for Microsoft Purview, Defender, or other security products
- **Not regulatory advice or legal guidance** — controls reference regulations but do not constitute legal opinion
- **Not a certification or compliance guarantee** — assists with implementation, not attestation
- **Not a managed service** — customers implement and maintain it themselves

---

## Do's and Don'ts

### ✅ Do's

- **Position as a "governance accelerator"** that helps implement Microsoft's own admin controls
- **Emphasize existing Microsoft capabilities** — PPAC, Purview, Defender, Entra ID are the foundation
- **Reference specific regulations** when discussing controls (e.g., "Control 1.7 maps to FINRA 4511 and SEC 17a-4 record retention requirements")
- **Use the Governance Readiness Assessment tool** for gap analysis in customer workshops
- **Point to the 3-zone model** (Personal / Team / Enterprise) for progressive governance adoption
- **Recommend starting with Phase 0 controls** (1.1, 1.5, 2.1, 3.1) for immediate value
- **Highlight companion solutions** for automation — reduce manual implementation effort

### ❌ Don'ts

- **Don't claim FSI-AgentGov ensures regulatory compliance** — it helps implement controls; compliance is the customer's responsibility
- **Don't position as Microsoft-endorsed or Microsoft-supported** — it's a community project
- **Don't guarantee specific audit outcomes** — audit success depends on many factors beyond this framework
- **Don't claim controls cover all regulatory requirements** — comprehensive but not exhaustive
- **Don't recommend skipping the customer's legal/compliance team review** — they must validate applicability
- **Don't promise specific implementation timelines** — every organization's complexity differs
- **Don't present automation solutions as production-ready** without customer testing and validation

---

## Supported Claims

| Claim | Status | Evidence |
|-------|--------|----------|
| "71 controls mapped to FSI regulations" | ✅ Supported | Control catalog with regulatory cross-references |
| "284 implementation playbooks" | ✅ Supported | Playbook directory with portal walkthroughs, PowerShell, verification, troubleshooting |
| "27 companion automation solutions" | ✅ Supported | FSI-AgentGov-Solutions repository |
| "Covers FINRA, SEC, OCC, GLBA requirements" | ✅ Supported | [Regulatory mappings](regulatory-mappings.md) reference |
| "Ensures compliance" | ❌ Not supported | Framework assists with implementation; compliance determination is customer's responsibility |
| "Microsoft-endorsed" | ❌ Not supported | Independent open-source project |
| "Production-ready solutions" | ⚠️ Qualified | Solutions require customer validation and testing in their environment |

!!! tip "When a customer asks for a compliance guarantee"
    Redirect to the [Evidence Standards](evidence-standards.md) reference. The framework provides
    evidence collection guidance, but the customer's compliance team makes the determination.

---

## Common Customer Objections

### "We already use Microsoft Purview / Defender"

FSI-AgentGov builds **on top of** these products. Controls reference Purview (sensitivity labels, DLP, compliance), Defender (AI security posture), and Entra ID (conditional access). The framework provides the **governance wrapper** — which controls to enable, in what order, with what configuration — specifically for AI agents in regulated environments.

### "We have our own governance framework"

FSI-AgentGov can **complement** existing frameworks. The [regulatory mappings](regulatory-mappings.md) show coverage gaps specific to AI agents. The assessment tool generates a scorecard that can be compared against existing controls. Many customers use it to fill **Power Platform-specific gaps** their current framework doesn't address.

### "This seems like a lot of controls for AI agents"

The [3-zone model](../framework/zones-and-tiers.md) enables **progressive adoption**. Zone 1 (Personal) requires minimal controls. Start with the **4 Phase 0 controls** and expand based on risk assessment. The framework is modular — implement what's relevant to your agent deployment scope.

### "Is this supported by Microsoft?"

It's an **open-source project**. Microsoft provides the underlying platform capabilities (PPAC, Purview, Defender). The framework documents how to configure those capabilities for FSI compliance. Standard Microsoft support covers the platform; the framework itself is community-maintained.

!!! note "Positioning tip"
    Frame it as: "The platform is fully supported by Microsoft. This framework is the *recipe book*
    for how to configure that platform for financial services governance."

### "How long does implementation take?"

It depends on scope. Phase 0 controls (4 controls) can be assessed in a **half-day workshop** and implemented within a week. Full framework adoption across all 71 controls is a **multi-month program**, but the phased approach means customers get value at each stage. The [adoption roadmap](../framework/adoption-roadmap.md) outlines the recommended progression.

### "What about agents we've already deployed?"

The framework applies to **both new and existing** agent deployments. The Readiness Assessment identifies gaps in current deployments. Several controls (like 1.7 Audit Logging and 3.1 Inventory Reporting) can be retroactively applied to provide governance visibility over agents already in production.

---

## Positioning by Customer Segment

Different FSI segments have different priorities. Lead with what matters most to each:

| Segment | Lead With | Key Controls | Regulatory Focus |
|---------|-----------|-------------|-----------------|
| **Large banks** | Enterprise zone governance, audit evidence | 1.7, 3.3, 2.1 | OCC, Federal Reserve, GLBA |
| **Broker-dealers** | Supervision and record retention | 1.7, 1.5, 3.3 | FINRA 3110, SEC 17a-4 |
| **Insurance** | Data protection, agent access control | 1.4, 1.5, 4.1 | State insurance regulations, GLBA |
| **Credit unions** | Cost-effective governance, quick wins | Phase 0 controls | NCUA, FDIC |
| **Wealth management** | Client data protection, supervision | 1.5, 1.7, 3.1 | SEC, FINRA |

---

## Conversation Starters

1. **"Let me show you where your current AI agent governance stands"**
   → Open the Readiness Assessment tool for a live gap analysis

2. **"Here are the 4 controls that give you immediate governance coverage"**
   → Show Phase 0 controls (1.1, 1.5, 2.1, 3.1) and their quick-win value

3. **"This is how the framework maps to your regulatory requirements"**
   → Open the [regulatory mappings](regulatory-mappings.md) for their specific regulators

4. **"We have automation solutions that can implement several controls for you"**
   → Show the [solutions integration](../framework/solutions-integration.md) and demo a relevant solution

---

## Engagement Workflow

A typical CSA engagement follows this progression:

```
1. Discovery        → Run the Readiness Assessment to baseline current state
2. Gap Analysis     → Map assessment results against regulatory requirements
3. Prioritization   → Identify Phase 0 controls + high-risk gaps
4. Implementation   → Walk through playbooks for selected controls
5. Automation       → Deploy companion solutions where applicable
6. Validation       → Verify controls using playbook verification steps
7. Handoff          → Customer's compliance team reviews and assumes ownership
```

!!! tip "Time estimate"
    Phase 0 controls (1.1, 1.5, 2.1, 3.1) can typically be assessed and demonstrated in a
    **single half-day workshop**. Full framework review across all 4 pillars usually spans
    **2–4 engagements** depending on organizational complexity.

---

## The Four Pillars at a Glance

Use this summary when introducing the framework's structure:

| Pillar | Controls | Focus Area | Key Message |
|--------|----------|------------|-------------|
| **1 — Security** | 1.1 – 1.15 | Agent publishing, authentication, DLP, data protection | "Who can build agents and what can they access?" |
| **2 — Management** | 2.1 – 2.18 | Managed Environments, lifecycle, capacity, environment strategy | "How do we operationalize agent governance at scale?" |
| **3 — Reporting** | 3.1 – 3.20 | Inventory, analytics, compliance reporting, monitoring | "What evidence do we have for regulators?" |
| **4 — SharePoint** | 4.1 – 4.18 | IAG, restricted content discovery, grounding controls | "How do we control what agents can see and share?" |

!!! info "Pillar interdependencies"
    Pillar 2 (Management) is foundational — **Managed Environments (2.1)** is a prerequisite for
    15+ controls across all four pillars. Always start environment strategy conversations here.

---

## Competitive Positioning

When customers mention other governance approaches:

| Alternative | FSI-AgentGov Differentiator |
|-------------|---------------------------|
| **Manual governance via spreadsheets** | Structured controls with automation solutions; repeatable and auditable |
| **Generic AI governance frameworks** | Purpose-built for Microsoft 365 + Power Platform; FSI-specific regulatory mappings |
| **Big-4 consulting engagements** | Open-source and free; customers own the implementation without ongoing consulting fees |
| **Wait-and-see approach** | Regulators are actively examining AI agent use; Phase 0 controls provide low-effort baseline coverage now |
| **Build from scratch internally** | 284 playbooks with step-by-step guidance; months of research already done |

---

## Key Proof Points

When you need to back up claims with specifics:

- **Regulatory depth**: Each control includes a regulatory cross-reference section citing specific rule numbers (e.g., FINRA Rule 3110, SEC Rule 17a-4(f), OCC Bulletin 2023-17)
- **Implementation detail**: Playbooks include portal screenshots, exact navigation paths, PowerShell commands, and verification steps — not just policy recommendations
- **Automation coverage**: 27 solutions cover controls across all 4 pillars, from agent access monitoring to compliance dashboards
- **Assessment tooling**: The Governance Readiness Assessment generates a quantitative scorecard, not just a qualitative checklist

---

## Quick Reference Links

For deeper dives during or after customer conversations:

| Resource | Link | Use When |
|----------|------|----------|
| CSA Quick Reference | [csa-quick-reference.md](csa-quick-reference.md) | Top controls and repository map |
| Start Here | [start-here.md](../start-here.md) | Customer-facing orientation page |
| Regulatory Mappings | [regulatory-mappings.md](regulatory-mappings.md) | Control-to-regulation mapping |
| Solutions Integration | [solutions-integration.md](../framework/solutions-integration.md) | Companion automation overview |
| Solutions Index | [solutions-index.md](solutions-index.md) | Full list of 27 automation solutions |
| Zones & Tiers | [zones-and-tiers.md](../framework/zones-and-tiers.md) | 3-zone progressive governance model |
| Adoption Roadmap | [adoption-roadmap.md](../framework/adoption-roadmap.md) | Phased implementation guidance |
| Evidence Standards | [evidence-standards.md](evidence-standards.md) | Audit evidence collection |
| License Requirements | [license-requirements.md](license-requirements.md) | Licensing prerequisites per control |
| FAQ | [faq.md](faq.md) | Common questions and answers |

---

!!! abstract "Internal Use Only"
    This guide is for **CSA use only**. Share the [Start Here](../start-here.md) page with customers
    for their orientation. Do not distribute this positioning guide externally.
