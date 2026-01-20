---
name: add-control
description: Use when adding a brand new control to one of the four pillars in the governance framework
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
user-invocable: true
---

# Skill: Add Control

Use this skill when adding a brand new control to one of the four pillars.

## Workflow

### Step 1: Copy Template
Source: `docs/templates/control-setup-template.md`

### Step 2: Create Control File
Target path: `docs/controls/pillar-{n}-{name}/{id}-{kebab-case-name}.md`

Examples:
- `docs/controls/pillar-1-security/1.24-new-security-control.md`
- `docs/controls/pillar-2-management/2.22-new-management-control.md`

### Step 3: Fill ALL 10 Sections

**Header Metadata:**
```markdown
**Control ID:** X.Y
**Pillar:** Pillar N - Name
**Regulatory Reference:** [Primary regulation]
**Last UI Verified:** [Month Year]
**Governance Levels:** Zone 1: [Level] | Zone 2: [Level] | Zone 3: [Level]
```

**Section 1: Objective**
Concise purpose statement (2-3 sentences)

**Section 2: Why This Matters for FSI**
Regulatory bullet points (FINRA, SEC, SOX, GLBA, OCC, Fed SR 11-7)

**Section 3: Control Description**
Detailed technical explanation

**Section 4: Key Configuration Points**
Bulleted configuration items

**Section 5: Zone-Specific Requirements**
| Zone | Description | Governance Level | Example Configuration |
|------|-------------|------------------|----------------------|
| Zone 1 | ... | ... | ... |
| Zone 2 | ... | ... | ... |
| Zone 3 | ... | ... | ... |

**Section 6: Roles & Responsibilities**
| Role | Responsibilities |
|------|------------------|
| [Role Name] | ... |

**Section 7: Related Controls**
| Control | Relationship |
|---------|--------------|
| [X.Y - Name](path.md) | ... |

**Section 8: Implementation Guides**
Links to 4 playbooks (create these next)

**Section 9: Verification Criteria**
Verification checklist

**Section 10: Additional Resources**
Microsoft Learn links

**Footer:**
```markdown
---
*Updated: [Month Year] | Version: v1.1 | UI Verification Status: [Pending/Verified]*
```

### Step 4: Update CONTROL-INDEX.md
Add entry to: `docs/controls/CONTROL-INDEX.md`

Maintain numerical order within pillar.

### Step 5: Update mkdocs.yml
Add navigation entry under correct pillar:
```yaml
- Controls:
  - Pillar N - Name:
    - X.Y - Control Name: controls/pillar-n-name/x.y-control-name.md
```

### Step 6: Create Screenshot Spec
Create: `docs/images/{control-id}/EXPECTED.md`

Include required screenshot descriptions for portal verification.

### Step 7: Create 4 Playbook Files
```
docs/playbooks/control-implementations/{control-id}/
├── portal-walkthrough.md    # Step-by-step portal configuration
├── powershell-setup.md      # PowerShell automation scripts
├── verification-testing.md  # Test cases, evidence collection
└── troubleshooting.md       # Common issues, resolutions
```

### Step 8: Update Playbook Navigation in mkdocs.yml
Add nested playbook links under Playbooks section.

### Step 9: Update Excel Templates
Run: `python scripts/update_excel_templates.py` (if needed)

Or use `/update-excel` skill for manual updates.

### Step 10: Validate
```bash
mkdocs build --strict
python scripts/verify_controls.py
```

## Language Rules

Same as `/update-control`:
- NEVER: "ensures compliance", "guarantees", "will prevent"
- ALWAYS: "supports compliance with", "helps meet", "required for"

## Control Numbering

| Pillar | Current Max | Next Available |
|--------|-------------|----------------|
| Pillar 1 - Security | 1.23 | 1.24 |
| Pillar 2 - Management | 2.21 | 2.22 |
| Pillar 3 - Reporting | 3.10 | 3.11 |
| Pillar 4 - SharePoint | 4.7 | 4.8 |

## Related Skills

- `/update-control` - Modifying existing controls
- `/update-excel` - Excel template maintenance
