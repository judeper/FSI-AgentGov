---
applyTo: "docs/controls/**/*.md"
---

# FSI Control Template Requirements

All control files must follow the 10-section template structure defined in `docs/templates/control-setup-template.md`.

## Required Header Metadata

```markdown
# Control [X.X]: [Control Name]

**Control ID:** [X.X]
**Pillar:** [Security / Management / Reporting / SharePoint]
**Regulatory Reference:** [FINRA 4511, SEC 17a-4, etc.]
**Last UI Verified:** [Month Year]
**Governance Levels:** Baseline / Recommended / Regulated
```

## Required Sections (All 10 Mandatory)

1. **Objective** — Concise purpose statement
2. **Why This Matters for FSI** — Regulatory justifications with specific regulation references
3. **Control Description** — Detailed technical explanation
4. **Key Configuration Points** — Specific settings to configure
5. **Zone-Specific Requirements** — Table with Zone 1/2/3 requirements and rationale
6. **Roles & Responsibilities** — Table mapping admin roles to responsibilities
7. **Related Controls** — Table with cross-references to related controls
8. **Implementation Guides** — Links to 4 playbooks (portal-walkthrough, powershell-setup, verification-testing, troubleshooting)
9. **Verification Criteria** — Numbered checklist for validating effectiveness
10. **Additional Resources** — Microsoft Learn links

## Required Footer Metadata

```markdown
*Updated: [Month Year] | Version: v[X.X] | UI Verification Status: [Current/Needs Review]*
```

## Role Naming Conventions

Use canonical short names from `docs/reference/role-catalog.md`:

| Use This | NOT This |
|----------|----------|
| Entra Global Admin | Global Administrator |
| Purview Compliance Admin | Compliance Administrator |
| Power Platform Admin | Power Apps Admin |
| Exchange Online Admin | Exchange Administrator |

## Cross-Reference Format

Related controls link format:
```markdown
| [X.X - Control Name](../pillar-N-name/X.X-control-name.md) | Relationship description |
```

## Playbook Link Format

```markdown
- [Portal Walkthrough](../../playbooks/control-implementations/[X.X]/portal-walkthrough.md)
- [PowerShell Setup](../../playbooks/control-implementations/[X.X]/powershell-setup.md)
- [Verification & Testing](../../playbooks/control-implementations/[X.X]/verification-testing.md)
- [Troubleshooting](../../playbooks/control-implementations/[X.X]/troubleshooting.md)
```

## Pillar Organization

| Pillar | Controls | Directory |
|--------|----------|-----------|
| Pillar 1 — Security | 1.1–1.29 | `docs/controls/pillar-1-security/` |
| Pillar 2 — Management | 2.1–2.26 | `docs/controls/pillar-2-management/` |
| Pillar 3 — Reporting | 3.1–3.14 | `docs/controls/pillar-3-reporting/` |
| Pillar 4 — SharePoint | 4.1–4.9 | `docs/controls/pillar-4-sharepoint/` |
