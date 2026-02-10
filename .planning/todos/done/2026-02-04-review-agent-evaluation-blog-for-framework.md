---
created: 2026-02-04T14:01
title: Review AI agent evaluation blog for framework applicability
area: docs
files:
  - docs/controls/pillar-2-management/control-2.18.md
  - docs/controls/pillar-3-reporting/control-3.1.md
  - docs/controls/pillar-2-management/control-2.8.md
  - docs/playbooks/control-implementations/2.18/verification-testing.md
---

## Problem

Microsoft published a blog on AI agent evaluation in Copilot Studio that describes a structured 8-step evaluation framework. Need to review whether any of these concepts should be incorporated into the FSI-AgentGov framework, particularly for controls related to testing, quality assurance, and operational monitoring.

**Source:** https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/how-to-evaluate-ai-agents/

### Blog Summary — Key Concepts:

**8-Step Evaluation Framework:**
1. Scenario Definition — articulate what behaviors are being validated
2. Real User Data — use authentic messy user queries, not idealized prompts
3. Evaluation Logic — multiple grader types (quality, classification, capability)
4. User Context — identity profiles to catch permission-related risks
5. Response Testing — run simulations based on prescribed scenarios
6. Aggregated Analysis — review high-level quality patterns across test cases
7. Detailed Investigation — drill into specific failures for root causes
8. Comparative Monitoring — track improvements over time through sequential evaluations

**Grader Types:**
- General quality assessment
- Classification grading using natural language prompts
- Capability verification for correct tool/topic invocation

**Enterprise/Governance Relevance:**
- Permission validation under different user access levels
- Risk mitigation through edge case and escalation failure identification
- Regression detection when agents are updated
- Evidence-based confidence replacing subjective impressions
- Making agent behavior "observable, repeatable, and explainable at scale"

### Potential framework touchpoints:
- **Control 2.18** (Agent Testing) — May benefit from referencing Copilot Studio's built-in evaluation capabilities
- **Control 2.8** (Change Management) — Regression detection aligns with change validation requirements
- **Control 3.1** (Operational Monitoring) — Comparative monitoring over time fits reporting pillar
- **Hallucination Tracker solution** — Evaluation graders could complement hallucination tracking
- **Verification playbooks** — 8-step methodology could enhance testing playbook guidance
- **DR Testing Framework solution** — Evaluation as part of resilience testing

## Solution

TBD — Read blog in detail against each potentially affected control and determine:
1. Whether Copilot Studio evaluation is a GA feature or preview (affects how we reference it)
2. Which controls would benefit from cross-references to this capability
3. Whether any playbooks should include evaluation steps
4. Whether solutions (hallucination-tracker, dr-testing-framework) should integrate with evaluation APIs
