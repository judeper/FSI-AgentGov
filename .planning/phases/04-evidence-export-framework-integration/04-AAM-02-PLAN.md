---
phase: 04-evidence-export-framework-integration
plan: AAM-02
title: "Control 3.8 tip admonition and solutions-index.md catalog entry"
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md
  - docs/reference/solutions-index.md
autonomous: true

must_haves:
  truths:
    - "Control 3.8 contains an 'Automated Validation: Agent Access Governance Monitor' tip admonition"
    - "Tip admonition includes capabilities list and deployable solution link"
    - "solutions-index.md lists Agent Access Governance Monitor in the Available Solutions table"
    - "solutions-index.md contains a full Solution Details section for Agent Access Governance Monitor"
    - "Version History table in solutions-index.md includes Agent Access Governance Monitor"
    - "mkdocs build --strict passes with zero errors"
  artifacts:
    - path: "docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md"
      provides: "Automated Validation tip admonition"
      contains: 'tip "Automated Validation: Agent Access Governance Monitor"'
    - path: "docs/reference/solutions-index.md"
      provides: "Solution catalog entry"
      contains: "Agent Access Governance Monitor"
  key_links:
    - from: "Control 3.8 tip admonition"
      to: "solutions-index.md"
      via: "reference to solution catalog"
      pattern: "agent-access-monitor"
    - from: "solutions-index.md table entry"
      to: "Solution Details section"
      via: "anchor link"
      pattern: "#agent-access-governance-monitor"
---

# Plan 04-AAM-02: Control 3.8 Tip Admonition and Solutions-Index Catalog Entry

## Goal

Add the Agent Access Governance Monitor to the FSI-AgentGov framework documentation — Control 3.8 tip admonition and solutions-index.md catalog entry. This makes the solution discoverable through the governance documentation.

## Tasks

### Task 1: Add Automated Validation tip admonition to Control 3.8

**File:** `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md`

Add a new tip admonition between the **Related Controls** section (ends around line 292) and the **Implementation Playbooks** section (starts around line 296). Control 3.8 currently has NO existing solution tip admonitions, so this will be the first.

Insert this content after the Related Controls table and before the `---` separator preceding Implementation Playbooks:

```markdown

!!! tip "Automated Validation: Agent Access Governance Monitor"
    For automated detection of overly permissive agent access configurations across Power Platform environments, see the **Agent Access Governance Monitor** solution.

    **Capabilities:**

    - Zone-based agent access compliance validation (Zone 1/2/3 requirements)
    - Daily scheduled drift detection with baseline comparison
    - Teams adaptive card alerts with severity classification
    - Dataverse-persisted validation history for audit trail
    - SHA-256 integrity-hashed evidence export for examination support

    **Deployable Solution:** [agent-access-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-access-monitor) provides PowerShell validation scripts, Power Automate flow definitions, and Dataverse schema for persistent governance state.

```

**Language check:** Uses "For automated detection" (not "ensures" or "guarantees"). Compliant.

**Acceptance Criteria:**
- [ ] Tip admonition exists between Related Controls and Implementation Playbooks
- [ ] Contains 5 capability bullets
- [ ] Contains Deployable Solution link to GitHub repo
- [ ] No FSI language violations
- [ ] mkdocs build --strict passes

### Task 2: Add Agent Access Governance Monitor to solutions-index.md

**File:** `docs/reference/solutions-index.md`

Three additions:

**1. Add table row to "Available Solutions" table (around line 17-31):**

Insert after the Session Security Configurator row (or at the end of the table). New row:
```
| [Agent Access Governance Monitor](#agent-access-governance-monitor) | v1.0.0 | Work In Progress | Automated detection of overly permissive agent access configurations per governance zone | 3.8 |
```

**2. Add Solution Details section:**

Insert `### Agent Access Governance Monitor` section AFTER the Session Security Configurator section and BEFORE the `## Getting Started` section:

```markdown
### Agent Access Governance Monitor

Automated detection of overly permissive agent access configurations across Power Platform environments. Validates agent sharing, authoring, and publishing settings against governance zone requirements with daily drift detection and compliance evidence export.

**Components:**

- PowerShell scripts for zone-based agent access validation
- Daily scheduled drift detection via Power Automate
- Teams adaptive card alerts with severity classification (Critical/High/Warning/Info)
- Dataverse tables for access baselines, validation history, and violations
- Evidence export with SHA-256 integrity hashing

**Regulatory Alignment:**

- FINRA 4511 (Books and Records — Agent Access Controls)
- SOX 404 (Internal Controls — Configuration Governance)
- SEC 17a-3/4 (Recordkeeping — Access Configuration)
- GLBA 501(b) (Safeguards — Agent Sharing Controls)

**Related Control:** [3.8 - Copilot Hub and Governance Dashboard](../controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)

**Repository Link:** [agent-access-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/agent-access-monitor)

---
```

**3. Add row to Version History table (around line 397-413):**

Add row in alphabetical order (after "Audit Configuration Validator"):
```
| Agent Access Governance Monitor | v1.0.0 | February 2026 |
```

**Acceptance Criteria:**
- [ ] Available Solutions table includes AAM row
- [ ] Solution Details section exists with Components, Regulatory Alignment, Related Control, Repository Link
- [ ] Version History table includes AAM entry
- [ ] Anchor link `#agent-access-governance-monitor` matches section heading
- [ ] mkdocs build --strict passes

## Verification

1. `mkdocs build --strict` passes with zero errors
2. Control 3.8 contains tip admonition with "Agent Access Governance Monitor"
3. solutions-index.md contains AAM in three locations (table, details, version history)
4. No "ensures compliance" or "guarantees" language

## Success Criteria

- Control 3.8 has tip admonition titled "Automated Validation: Agent Access Governance Monitor"
- Tip contains 5 capability bullets and deployable solution link
- solutions-index.md Available Solutions table includes AAM row
- solutions-index.md Solution Details section includes all required subsections
- solutions-index.md Version History includes AAM entry
- mkdocs build --strict passes

## Output

After completion, create `.planning/phases/04-evidence-export-framework-integration/04-AAM-02-SUMMARY.md`

Git operations: Commit to FSI-AgentGov repository.
