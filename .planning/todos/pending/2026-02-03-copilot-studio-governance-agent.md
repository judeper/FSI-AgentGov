---
created: 2026-02-03T00:00
title: Build Copilot Studio agent for FSI governance Q&A
area: tooling
files:
  - docs/:entire documentation site (GitHub Pages knowledge source)
  - docs/controls/:62 controls as primary knowledge base
  - docs/playbooks/:248+ playbooks for implementation guidance
  - docs/reference/regulatory-mappings.md
  - CONTRIBUTING.md:language guidelines for agent system prompt
---

## Problem

The FSI Agent Governance Framework documentation (62 controls, 248+ playbooks, regulatory mappings) is currently only accessible through manual navigation of the MkDocs GitHub Pages site. FSI administrators and compliance officers must browse or search through extensive documentation to find answers to specific governance questions.

A Copilot Studio agent using the GitHub Pages site as a knowledge source would let users ask natural language questions ("What controls apply to FINRA 3110?", "How do I configure DLP for agent outputs?", "What are the requirements for Enterprise Managed zone?") and get grounded, accurate answers directly.

This also serves as a powerful dogfooding demonstration — the governance framework for M365 AI agents is itself delivered through an M365 AI agent.

## Solution

**Approach:** Build a Copilot Studio agent with:

1. **Knowledge source:** GitHub Pages URL (`https://judeper.github.io/FSI-AgentGov/`) configured as website knowledge in Copilot Studio
2. **System prompt:** Include regulatory language guardrails from CONTRIBUTING.md (never say "ensures compliance", use "supports compliance with" etc.), disclaimer that this is guidance not legal advice
3. **Topics/capabilities:**
   - Control lookup by ID, pillar, or regulation
   - Playbook retrieval (portal, PowerShell, verification, troubleshooting)
   - Regulatory mapping queries
   - Zone classification guidance
   - Solution recommendations for specific controls
4. **Guardrails:** Scope boundaries to prevent hallucination on regulatory claims, clear attribution to source documentation

**Key design decisions (TBD):**
- Whether to use website knowledge source alone or supplement with uploaded structured data (e.g., control index as a file)
- Authentication model (public vs. organizational)
- Whether to include Solutions repo content or just framework documentation
- How to handle version tracking (agent should know which framework version it reflects)
- Conversation handoff for questions beyond the framework's scope

**Relationship to MCP server todo:** Complementary, not overlapping. MCP server = developer/tool integration. Copilot Studio agent = end-user Q&A. Both depend on the same verified source content.

**Timing:** Should follow content audit phases (2-7) so the agent grounds on verified, accurate documentation. Candidate for Phase 9/10 or post-milestone work alongside MCP server.
