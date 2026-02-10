---
phase: 04-evidence-export-framework-integration
plan: CMM-02
title: "Control 1.8 tip admonition and solutions-index.md catalog entry"
type: execute
wave: 1
depends_on: []
files_modified:
  - docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md
  - docs/reference/solutions-index.md
autonomous: true

must_haves:
  truths:
    - "Control 1.8 contains an 'Automated Validation: Content Moderation Governance Monitor' tip admonition"
    - "Tip admonition includes capabilities list and deployable solution link"
    - "solutions-index.md lists Content Moderation Governance Monitor in the Available Solutions table"
    - "solutions-index.md contains a full Solution Details section for Content Moderation Governance Monitor"
    - "Version History table in solutions-index.md includes Content Moderation Governance Monitor"
    - "mkdocs build --strict passes with zero errors"
  artifacts:
    - path: "docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md"
      provides: "Automated Validation tip admonition"
      contains: 'tip "Automated Validation: Content Moderation Governance Monitor"'
    - path: "docs/reference/solutions-index.md"
      provides: "Solution catalog entry"
      contains: "Content Moderation Governance Monitor"
  key_links:
    - from: "Control 1.8 tip admonition"
      to: "solutions-index.md"
      via: "reference to solution catalog"
      pattern: "content-moderation-monitor"
    - from: "solutions-index.md table entry"
      to: "Solution Details section"
      via: "anchor link"
      pattern: "#content-moderation-governance-monitor"
---

# Plan 04-CMM-02: Control 1.8 Tip Admonition and Solutions-Index Catalog Entry

## Goal

Add the Content Moderation Governance Monitor to the FSI-AgentGov framework documentation — Control 1.8 tip admonition and solutions-index.md catalog entry. This makes the CMM solution discoverable through the governance documentation and links it to the control it automates.

**Integration point:** Control 1.8 explicitly covers content moderation level configuration with zone-specific requirements (Zone 1: Medium minimum, Zone 2/3: High). The CMM solution automates exactly these checks, making Control 1.8 the natural framework home.

## Tasks

### Task 1: Add Automated Validation tip admonition to Control 1.8

**File:** `docs/controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md`

Add a new tip admonition between the **Related Controls** section and the **RAI Telemetry Capture** subsection. Control 1.8 currently has 10 admonitions (info/success/warning) but NO tip admonitions for deployable solutions, so this will be the first.

**Recommended insertion point:** After the Related Controls table (around line 290) and before the RAI Telemetry section heading. This places the tip near the "Content Moderation Level Configuration" subsection for maximum discoverability.

Insert this content:

```markdown

!!! tip "Automated Validation: Content Moderation Governance Monitor"
    For automated detection of non-compliant content moderation settings on Copilot Studio agents per governance zone, see the **Content Moderation Governance Monitor** solution.

    **Capabilities:**

    - Per-agent content moderation level validation (Low/Medium/High vs zone requirements)
    - Zone-based compliance checking (Zone 1: Medium minimum, Zone 2/3: High)
    - Drift detection with baseline comparison for configuration change tracking
    - Teams adaptive card alerts with severity classification and regulatory context
    - SHA-256 integrity-hashed evidence export for examination support

    **Deployable Solution:** [content-moderation-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/content-moderation-monitor) provides PowerShell validation scripts, Power Automate flow definitions, and Dataverse schema for persistent governance state.

```

**Language check:** Uses "For automated detection" (not "ensures" or "guarantees"). Compliant.

**Acceptance Criteria:**
- [ ] Tip admonition exists between Related Controls and RAI Telemetry Capture
- [ ] Contains 5 capability bullets matching CMM features
- [ ] Contains Deployable Solution link to GitHub repo
- [ ] No FSI language violations
- [ ] mkdocs build --strict passes

### Task 2: Add Content Moderation Governance Monitor to solutions-index.md

**File:** `docs/reference/solutions-index.md`

Three additions:

**1. Add table row to "Available Solutions" table:**

Insert row in the table. New row:
```
| [Content Moderation Governance Monitor](#content-moderation-governance-monitor) | v1.0.0 | Work In Progress | Automated per-agent content moderation level validation against zone-specific governance requirements | 1.8, 1.14 |
```

**2. Add Solution Details section:**

Insert `### Content Moderation Governance Monitor` section in the Solution Details area, maintaining alphabetical order among the solution name headings:

```markdown
### Content Moderation Governance Monitor

Automated detection of non-compliant content moderation settings for Copilot Studio agents across Power Platform environments. Validates per-agent moderation levels (Low/Medium/High) against governance zone requirements with daily drift detection and compliance evidence export.

**Components:**

- PowerShell scripts for per-agent content moderation validation
- Daily scheduled drift detection via Power Automate
- Teams adaptive card alerts with severity classification (Critical/High/Medium/Warning)
- Dataverse tables for moderation baselines, validation history, and violations
- Evidence export with SHA-256 integrity hashing

**Regulatory Alignment:**

- FINRA 3110 (Supervisory Controls — Content Moderation Governance)
- SOX 404 (Internal Controls — Configuration Governance)
- GLBA 501(b) (Safeguards — Content Safety Controls)
- SEC AI Priorities (Responsible AI governance)

**Related Control(s):** [1.8 - Runtime Protection and External Threat Detection](../controls/pillar-1-security/1.8-runtime-protection-and-external-threat-detection.md)

**Repository Link:** [content-moderation-monitor](https://github.com/judeper/FSI-AgentGov-Solutions/tree/main/content-moderation-monitor)

---
```

**3. Add row to Version History table:**

Add row in alphabetical order:
```
| Content Moderation Governance Monitor | v1.0.0 | February 2026 |
```

**Acceptance Criteria:**
- [ ] Available Solutions table includes CMM row
- [ ] Solution Details section exists with Components, Regulatory Alignment, Related Control, Repository Link
- [ ] Version History table includes CMM entry
- [ ] Anchor link `#content-moderation-governance-monitor` matches section heading
- [ ] mkdocs build --strict passes

## Verification

1. `mkdocs build --strict` passes with zero errors
2. Control 1.8 contains tip admonition with "Content Moderation Governance Monitor"
3. solutions-index.md contains CMM in three locations (table, details, version history)
4. No "ensures compliance" or "guarantees" language

## Success Criteria

- Control 1.8 has tip admonition titled "Automated Validation: Content Moderation Governance Monitor"
- Tip contains 5 capability bullets and deployable solution link
- solutions-index.md Available Solutions table includes CMM row
- solutions-index.md Solution Details section includes all required subsections
- solutions-index.md Version History includes CMM entry
- mkdocs build --strict passes

## Output

After completion, create `.planning/phases/04-evidence-export-framework-integration/04-CMM-02-SUMMARY.md`

Git operations: Commit to FSI-AgentGov repository.
