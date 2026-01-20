# Skill: Update Control

Use this skill when modifying an existing control's content (e.g., update instructions, fix typos, add regulation references).

## Workflow

### Step 1: Read the Control
```
docs/controls/pillar-{1-4}-{name}/{id}-{kebab-case}.md
```

Example paths:
- `docs/controls/pillar-1-security/1.1-data-loss-prevention-dlp-policies.md`
- `docs/controls/pillar-2-management/2.7-supply-chain-risk-assessment.md`

### Step 2: Read the Template
Always reference: `docs/templates/control-setup-template.md`

### Step 3: Make Changes
Preserve ALL 10 sections (never skip or remove a section):
1. Header metadata (Control ID, Pillar, Regulatory Reference, Last UI Verified, Governance Levels)
2. Section 1: Objective
3. Section 2: Why This Matters for FSI
4. Section 3: Control Description
5. Section 4: Key Configuration Points
6. Section 5: Zone-Specific Requirements
7. Section 6: Roles & Responsibilities
8. Section 7: Related Controls
9. Section 8: Implementation Guides
10. Section 9: Verification Criteria
11. Section 10: Additional Resources
12. Footer metadata

### Step 4: Update Footer Date
Change "Updated: Month-Year" to current date (e.g., "Updated: January 2026")

### Step 5: Update Screenshot Specs (if portal paths changed)
Edit: `docs/images/{control-id}/EXPECTED.md`

### Step 6: Update Related Playbooks
Check for impacted guides in:
```
docs/playbooks/control-implementations/{control-id}/
├── portal-walkthrough.md
├── powershell-setup.md
├── verification-testing.md
└── troubleshooting.md
```

### Step 7: Validate
```bash
mkdocs build --strict
```
Must pass with zero errors.

## Critical Language Rules (NEVER violate)

**NEVER use these phrases:**
- "ensures compliance" (implies guarantee)
- "guarantees" (legal risk)
- "will prevent" (overclaim)
- "eliminates risk" (unrealistic)

**ALWAYS use these alternatives:**
- "supports compliance with"
- "helps meet"
- "required for"
- "recommended to"
- "aids in"

### Example
```markdown
# WRONG
This control ensures you meet SEC 17a-4 requirements

# RIGHT
This control helps support SEC 17a-4 requirements. Implementation requires...
```

## Role Naming Convention

Use canonical short role names from `docs/reference/role-catalog.md`:
- "Entra Global Admin" (NOT "Global Administrator")
- "Purview Compliance Admin" (NOT "Compliance Administrator")
- "Power Platform Admin" (NOT "Power Apps Admin")
- "Exchange Online Admin" (NOT "Exchange Administrator")

## Related Skill

- `/add-control` - Creating new controls
- `/verify-ui` - Screenshot verification
