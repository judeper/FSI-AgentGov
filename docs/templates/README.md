# Templates Directory

This folder contains templates for creating consistent documentation.

## Available Templates

| Template | Purpose |
|----------|---------|
| `control-setup-template.md` | Standard structure for all 60 governance controls |

## Using the Control Template

### When to Use

Use `control-setup-template.md` when:
- Creating a new control (1.x, 2.x, 3.x, or 4.x)
- Restructuring an existing control to match the standard format
- Adding sections that are missing from older controls

### Required Sections (10 Total)

1. **Objective** - Concise statement of the control's purpose
2. **Why This Matters for FSI** - Regulatory bullet points
3. **Control Description** - Detailed technical explanation
4. **Key Configuration Points** - Bulleted configuration items
5. **Zone-Specific Requirements** - Zone 1/2/3 table
6. **Roles & Responsibilities** - Admin roles table
7. **Related Controls** - Cross-reference table
8. **Implementation Guides** - Links to 4 playbooks
9. **Verification Criteria** - Verification checklist
10. **Additional Resources** - Microsoft Learn links

### Naming Convention

```
{control-id}-{kebab-case-name}.md

Examples:
1.20-new-security-control.md
2.16-additional-management-control.md
```

### After Creating a Control

1. Add to `mkdocs.yml` navigation
2. Update `docs/controls/CONTROL-INDEX.md` with the new control entry
3. Create screenshot specs in `docs/images/{control-id}/EXPECTED.md`
4. Validate: `mkdocs build --strict`

## Style Guidelines

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for:
- Language guidelines (avoid "ensures compliance")
- Regulatory mapping requirements
- Testing procedures
