---
created: 2026-02-07T12:00
title: Investigate multi-source governance agent architecture
area: tooling
files:
  - docs/controls/:62 controls as primary knowledge base
  - docs/playbooks/:248 control playbooks + 27 advanced implementations
  - docs/reference/regulatory-mappings.md
  - docs/reference/solutions-index.md
  - docs/framework/solutions-integration.md
  - CONTRIBUTING.md:language guidelines for agent system prompt
---

## Problem

The FSI Agent Governance Framework (62 controls, 248+ playbooks, 13 solutions, 7+ regulations) is consumed only through static MkDocs web pages. M365 administrators and compliance officers in financial services need a conversational interface to:

- Understand how to verify configuration for specific controls
- Get step-by-step guidance on configuring controls based on their requirements
- Receive answers grounded in authoritative sources with proper citations
- Cross-reference regulatory requirements (FINRA, SEC) with implementation guidance

Currently there is no machine-readable interface for AI agents to query this data, and no unified approach to combine the framework content with official Microsoft documentation and regulatory source material.

## Solution

**Investigation needed** — Determine whether a multi-source citation agent architecture provides sufficient value to justify implementation. If the approach doesn't deliver meaningfully better outcomes than existing documentation, we will NOT implement.

### Concept: Three-Source Citation Architecture

Provide grounded answers with citations from three authoritative sources:

1. **Government/Regulatory Sites** — FINRA.org, SEC.gov for regulation text, rule citations, enforcement guidance (FINRA 4511/3110/25-07, SEC 17a-3/4, etc.)
2. **FSI-AgentGov Repositories** — Framework documentation + Solutions repo for control specifications, playbooks, and deployable artifacts
3. **Microsoft Learn MCP Server** — Official Microsoft documentation for product capabilities, API references, configuration steps

### Approaches to Investigate

**Option A: MCP Server for Framework + External MCP Servers**
- Build custom MCP server exposing FSI-AgentGov content as structured resources/tools
- Point to GitHub repos for live reasoning over controls, playbooks, solutions
- Integrate Learn MCP server for Microsoft docs fallback
- Add regulatory site access (FINRA/SEC) for citation grounding
- Pros: Machine-readable, composable, works with multiple AI clients
- Cons: Build and maintenance cost, requires MCP ecosystem maturity

**Option B: Copilot Studio Agent with Knowledge Sources**
- Use GitHub Pages site as website knowledge source in Copilot Studio
- Supplement with uploaded structured data (control index, regulatory mappings)
- System prompt includes regulatory language guardrails from CONTRIBUTING.md
- Pros: Native M365 integration, lower build cost, dogfooding demo
- Cons: Limited citation granularity, no programmatic access, single-client

**Option C: Hybrid — MCP Server + Copilot Studio Agent**
- MCP server for developer/tool integration (machine-readable)
- Copilot Studio agent for end-user Q&A (human-friendly)
- Both consume the same verified source content
- Pros: Covers both audiences
- Cons: Two things to build and maintain

### Key Questions to Answer

1. **Is it overkill?** Does the citation architecture provide meaningfully better answers than pointing users to the existing MkDocs site?
2. **GitHub repos as knowledge source** — Is pointing an agent directly at the repos effective for reasoning, or is a structured extraction layer needed?
3. **Learn MCP server value** — Does supplementing with Learn docs improve answer quality enough to justify the integration?
4. **Regulatory site access** — Can we reliably extract and cite FINRA/SEC content, and does this improve trust in answers?
5. **Build vs. buy** — Are there existing tools or services that already solve parts of this?
6. **Maintenance burden** — Who keeps the agent/MCP server in sync with framework updates?

### Target Users

- M365 administrators implementing governance controls
- Compliance officers verifying configuration against regulatory requirements
- Security teams assessing agent governance posture

### Success Criteria for Investigation

- Clear recommendation: build / don't build / defer
- If build: recommended approach (A, B, or C) with justification
- Estimated effort and maintenance cost
- Prototype or proof-of-concept demonstrating citation quality

### Supersedes

This todo consolidates two earlier todos:
- `2026-02-03-mcp-server-governance-framework.md` (MCP server concept)
- `2026-02-03-copilot-studio-governance-agent.md` (Copilot Studio agent concept)
