# Phase 1: Telemetry Infrastructure & Solution Foundation - Context

**Gathered:** 2026-02-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Deploy FSI-compliant telemetry pipeline (Application Insights, Log Analytics, ADLS Gen2 export) and create solution documentation (README, architecture, prerequisites, governance mapping) in the FSI-AgentGov-Solutions repository. Python automation scripts for full provisioning and teardown.

</domain>

<decisions>
## Implementation Decisions

### Documentation depth & structure
- README leads with architecture overview, then setup instructions (not quick-start-first)
- architecture.md uses a single high-level Mermaid data flow diagram (3-5 boxes: Copilot Studio → App Insights → Log Analytics → ADLS Gen2)
- prerequisites.md uses checklist table format: Resource | Required Role | License Tier
- Framework control references appear inline in architecture/README docs (e.g., "supports Control 1.3, 3.2") — not deferred to a separate mapping doc
- governance-mapping.md is the comprehensive mapping; inline refs provide contextual pointers

### Deployment experience
- Python scripts using Azure SDK for Python (azure-mgmt-*) for full resource provisioning — not Azure CLI wrappers
- Scripts handle full provisioning: create Application Insights workspace, Log Analytics workspace, ADLS Gen2 storage account, diagnostic settings, RBAC assignments
- Matching teardown/destroy script for lab cycling
- Config file (JSON/YAML) for environment-specific values (resource group, location, retention days) with CLI argument overrides
- Rationale: user tests in lab environment, needs easy setup and teardown

### Governance mapping approach
- Artifact → Controls direction: start from each observability component and list which controls it supports
- Tiered evidence indicators: Primary evidence / Supporting evidence / Partial coverage
- Direct regulatory citations alongside control references (e.g., "App Insights → Control 1.3 (SEC 17a-4)")
- Include placeholder sections for future-phase artifacts (KQL queries, workbooks, alerts) marked "Coming in Phase X"

### Compliance data handling
- PII sanitization: decision framework + table of known Copilot Studio telemetry fields with recommended handling (mask/hash/drop)
- SEC 17a-4 ADLS Gen2 export includes verification steps to confirm immutability (WORM policy) — verification in Phase 1, not deferred to Phase 5
- WORM policy configuration is manual with documentation guidance — NOT automated in provisioning script (too risky for accidental production deployment)
- Cost management: Python script sets sensible sampling defaults (e.g., 50% adaptive sampling) + separate tuning guide for production workloads

### Claude's Discretion
- Exact Mermaid diagram layout and styling
- Config file format choice (JSON vs YAML)
- Python script structure (single file vs module)
- Error handling patterns in provisioning scripts
- Prerequisites table column order and formatting
- Cost alert threshold defaults

</decisions>

<specifics>
## Specific Ideas

- "I would like to use automation using Python for any configuration we would be doing. This is because I will be testing this out in lab environment and then deleting them. So I would need to have an easy way to setup most of the configuration using automation and the rest which cannot be automated will be done manually."
- Azure SDK for Python (azure-mgmt-*) — not CLI wrappers
- WORM policy stays manual — explicit decision to avoid accidental immutable lockdown via script

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-telemetry-infrastructure-solution-foundation*
*Context gathered: 2026-02-05*
