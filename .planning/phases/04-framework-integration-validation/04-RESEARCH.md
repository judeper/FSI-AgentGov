# Phase 4 Research: Framework Integration & Validation

## Overview

Phase 4 integrates the Agent Usage & Performance Workbook into the FSI-AgentGov framework by updating 3 controls with tip admonitions, adding a solutions-index.md catalog entry, and validating all changes pass build and language rules.

## Target Files Analysis

### Controls Requiring Updates

| Control | Filename | Key Sections | Existing Admonitions |
|---------|----------|-------------|---------------------|
| 3.2 | `3.2-usage-analytics-and-activity-monitoring.md` | Section 8 (Implementation Playbooks), Section 10 (Additional Resources) | `!!! note`, `!!! info`, `!!! warning` — no `!!! tip` |
| 3.9 | `3.9-microsoft-sentinel-integration.md` | Section 8 (Implementation Playbooks), Section 10 (Additional Resources) | `!!! info`, `!!! tip` (pathway selection — different topic), `!!! warning` |
| 2.9 | `2.9-agent-performance-monitoring-and-optimization.md` | Section 8 (Implementation Playbooks), Section 10 (Additional Resources) | `!!! warning`, `!!! note`, `!!! info` — no `!!! tip` |

### Admonition Placement Strategy

The `!!! tip` admonition should be placed **after Section 8 (Implementation Playbooks)** for each control, linking to the workbook playbook as a complementary solution. This positions the workbook reference where administrators are already looking for implementation guidance.

**Admonition pattern:**
```markdown
!!! tip "Agent Usage & Performance Workbook"
    For organizations with ALM separation-of-duties requirements, the [Agent Usage & Performance Workbook](../../playbooks/advanced-implementations/agent-usage-workbook/index.md) provides Azure Monitor-based analytics without requiring direct Copilot Studio Analytics tab access. See the [Deployment Guide](../../playbooks/advanced-implementations/agent-usage-workbook/deployment-guide.md) for setup instructions.
```

### Solutions Index Pattern

The workbook is a **framework-integrated tool** (JSON template lives at `src/agent-usage-workbook.json`), not an FSI-AgentGov-Solutions repo solution. Use the same pattern as "Configuration Hardening Baseline" which uses `!!! info "Framework-Integrated Tool"`.

**Entry needs:**
1. Row in overview table (line ~38 area)
2. Detail section with components, regulatory alignment, related controls, playbook link
3. Row in version history table (line ~580 area)

### Workbook Playbook Paths

| File | Path |
|------|------|
| index.md | `docs/playbooks/advanced-implementations/agent-usage-workbook/index.md` |
| telemetry-schema.md | `docs/playbooks/advanced-implementations/agent-usage-workbook/telemetry-schema.md` |
| deployment-guide.md | `docs/playbooks/advanced-implementations/agent-usage-workbook/deployment-guide.md` |
| customization-guide.md | `docs/playbooks/advanced-implementations/agent-usage-workbook/customization-guide.md` |

Already in mkdocs.yml nav under Advanced Implementations (lines 569–573).

### Footer Requirements

Controls use: `*Updated: February 2026 | Version: v1.2 | UI Verification Status: Current*`

`verify_controls.py` accepts `Updated: January 2026` or `Updated: February 2026` and `Version: v1.2` or `Version: v1.3`.

## Risks

| Risk | Mitigation |
|------|-----------|
| Language rule violations in new admonition text | Avoid "ensures compliance", "guarantees", "will prevent", "eliminates risk" |
| Broken relative links in tip admonitions | Use verified relative paths from control → playbook |
| solutions-index.md anchor collision | Generate unique anchor `agent-usage--performance-workbook` |
| Footer date/version rejection by verify_controls.py | Use `Updated: February 2026` and `Version: v1.2` |

## Recommended Approach

- **Plan 04-01 (Wave 1):** Update 3 controls + add solutions-index.md entry (content creation)
- **Plan 04-02 (Wave 2):** Run validation suite (depends on 04-01 completing all edits first)

---
*Research completed: 2026-02-11*
