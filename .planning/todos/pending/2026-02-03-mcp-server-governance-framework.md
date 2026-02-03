---
created: 2026-02-03T00:00
title: Create MCP server for FSI governance framework
area: tooling
files:
  - docs/controls/:all 62 controls
  - docs/playbooks/:248 control playbooks + 27 advanced
  - docs/reference/regulatory-mappings.md
  - docs/reference/solutions-index.md
  - docs/framework/solutions-integration.md
---

## Problem

The FSI Agent Governance Framework (62 controls, 248+ playbooks, 13 solutions) is currently consumed only through static MkDocs web pages. As FSI organizations increasingly use AI assistants for compliance and governance work, there is no machine-readable interface for AI agents to query controls, regulatory mappings, playbooks, or solution status programmatically.

An MCP (Model Context Protocol) server would expose the framework as structured resources and tools, enabling AI assistants (Copilot, Claude, etc.) to answer governance questions with authoritative, versioned data rather than requiring human navigation or web scraping.

## Solution

Build an MCP server that exposes:

**Resources (read-only data):**
- Individual controls (all 10 sections per control)
- Playbooks (portal, PowerShell, verification, troubleshooting)
- Regulatory mappings (FINRA, SEC, SOX, GLBA, OCC, Fed, CFTC)
- Zone classifications and tier requirements
- Solutions catalog with framework control mappings

**Tools (queryable interfaces):**
- `get_control(id)` — Return full control specification
- `find_controls_by_regulation(reg)` — Controls mapped to a regulation
- `find_controls_by_zone(zone)` — Controls applicable to a governance zone
- `get_playbook(control_id, type)` — Return specific playbook
- `get_solution(name)` — Solution details and mapped controls
- `check_coverage(regulation)` — Coverage analysis for a regulation

**Key design decisions (TBD):**
- TypeScript vs Python implementation
- Hosting model (local CLI, containerized, cloud)
- Content parsing strategy (markdown AST vs structured extraction)
- Version tracking (align with framework version e.g., 1.2.37)
- Whether to include Solutions repo artifacts or just documentation

**Timing:** Should follow content audit phases (2-7) so the MCP server exposes verified, accurate content. Candidate for Phase 9 or post-Phase 8 work.

**Rationale:** Complements (not replaces) the MkDocs site. Same source of truth, two consumption channels — human-readable web pages and machine-readable MCP interface. Early differentiator for governance frameworks.
