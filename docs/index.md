---
hide:
  - navigation
  - toc
---

<div class="hero" markdown>

# AI Agent Governance for **Financial Services**

Govern Microsoft 365 AI agents with confidence — from policy to production.
71 controls, implementation playbooks, and regulatory mappings for
Copilot Studio, Agent Builder, and custom agent deployments.

[Get Started](getting-started/quick-start.md){ .md-button .md-button--primary }
[View Control Catalog](controls/index.md){ .md-button }

</div>

<div class="metrics-strip">
  <div class="metric">
    <span class="metric-number">71</span>
    <span class="metric-label">Controls</span>
  </div>
  <div class="metric">
    <span class="metric-number">4</span>
    <span class="metric-label">Governance Pillars</span>
  </div>
  <div class="metric">
    <span class="metric-number">5</span>
    <span class="metric-label">Regulatory Frameworks</span>
  </div>
  <div class="metric">
    <span class="metric-number">3</span>
    <span class="metric-label">Governance Zones</span>
  </div>
</div>
<p class="metrics-regulations">
  FINRA · SEC · SOX · GLBA · OCC/SR 11-7
</p>

## Quick Start by Role

<div class="grid cards" markdown>

-   :material-shield-check:{ .lg .middle } **Compliance Officer**

    ---

    Map controls to FINRA, SEC, SOX, and GLBA requirements.
    Build examination-ready evidence packs.

    [:material-arrow-right: Start Here](framework/executive-summary.md)

-   :material-cog:{ .lg .middle } **Power Platform Admin**

    ---

    Deploy controls, run playbooks, and configure
    governance across your M365 tenant.

    [:material-arrow-right: Start Here](controls/index.md)

-   :material-security:{ .lg .middle } **IT Security / InfoSec**

    ---

    Implement DLP, audit logging, encryption, MFA,
    and 28 security controls across your tenant.

    [:material-arrow-right: Start Here](controls/pillar-1-security/index.md)

-   :material-file-document-check:{ .lg .middle } **Examination Readiness**

    ---

    Prepare for FINRA/SEC examinations with
    evidence standards and audit checklists.

    [:material-arrow-right: Start Here](playbooks/compliance-and-audit/audit-readiness-checklist.md)

-   :material-account-tie:{ .lg .middle } **Business Owner**

    ---

    Understand zone requirements and the agent
    approval lifecycle for your team.

    [:material-arrow-right: Start Here](framework/zones-and-tiers.md)

</div>

## Framework Architecture

```mermaid
graph TB
    subgraph Zones ["Governance Zones"]
        direction LR
        Z1["Zone 1: Personal\nLow Risk · Self-Service"]
        Z2["Zone 2: Team\nMedium Risk · Manager Approval"]
        Z3["Zone 3: Enterprise\nHigh Risk · Committee Approval"]
    end

    subgraph Pillars ["71 Controls across 4 Pillars"]
        direction LR
        P1["Security\n28 Controls"]
        P2["Management\n24 Controls"]
        P3["Reporting\n12 Controls"]
        P4["SharePoint\n7 Controls"]
    end

    subgraph Regs ["Regulatory Coverage"]
        direction LR
        R1["FINRA\n4511/3110"]
        R2["SEC\n17a-3/4"]
        R3["SOX\n302/404"]
        R4["GLBA\n501b"]
        R5["OCC\n2011-12"]
    end

    Zones --> Pillars --> Regs
```

---

!!! warning "Disclaimer"
    This framework is provided for informational purposes only and does not constitute legal, regulatory, or compliance advice. Organizations should consult with their legal counsel and compliance teams. See [Disclaimer](disclaimer.md) for full details.
