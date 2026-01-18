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

### Required Sections (12 Total)

1. **Overview** - Control ID, name, regulatory reference, setup time
2. **Prerequisites** - License, admin role, dependencies
3. **Governance Levels** - Baseline, Recommended, Regulated configurations
4. **Setup & Configuration** - Portal-based steps with PowerShell alternative
5. **Financial Sector Considerations** - Regulatory alignment table
6. **Zone-Specific Configuration** - Zone 1/2/3 guidance
7. **Verification & Testing** - Numbered steps with EXPECTED results
8. **Troubleshooting & Validation** - Common issues table
9. **Additional Resources** - Microsoft Learn links
10. **Related Controls** - Cross-references
11. **Support & Questions** - Contact roles
12. **Footer** - Last Updated, Version, UI Verification Status

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
