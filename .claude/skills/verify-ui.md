# Skill: Verify UI Screenshots

Use this skill to check if control documentation matches actual Microsoft portal UI.

## Workflow

### Step 1: Read the Control Document
```
docs/controls/pillar-{n}-{name}/{control-id}-{name}.md
```

### Step 2: Read Expected Screenshots
```
docs/images/{control-id}/EXPECTED.md
```

Each EXPECTED.md file describes:
- Screenshot filename
- Portal path to navigate
- What the screenshot should show
- Key UI elements to verify

### Step 3: Review VERIFY.md Workflow
Read: `docs/images/VERIFY.md`

This file contains the overall verification process.

### Step 4: Compare Documentation Against Portal

For each portal instruction in the control doc:
1. Verify the navigation path is still accurate
2. Verify menu names match current UI
3. Verify setting names match current UI
4. Verify any screenshots match current appearance

### Step 5: Report Status

Use these status indicators:

| Status | Meaning |
|--------|---------|
| **Matches** | Instructions align with current portal UI |
| **Discrepancies found** | Instructions don't match current UI |
| **Outdated** | UI has significantly changed since last verification |

### Step 6: Update Control (if needed)

If discrepancies found:
1. Update the control file with corrected paths/names
2. Update EXPECTED.md with new screenshot requirements
3. Update footer "Last UI Verified" date
4. Run `mkdocs build --strict`

## EXPECTED.md Format

Each control folder should contain an EXPECTED.md file:

```markdown
# Control X.Y - Expected Screenshots

## Screenshot 1: [description]
**Filename:** x.y-screenshot-1.png
**Portal:** [Portal name]
**Path:** [Menu > Submenu > Setting]
**Shows:** [What this screenshot demonstrates]

## Screenshot 2: [description]
...
```

## Image Directory Structure

```
docs/images/
├── README.md           # Overview of image directory
├── VERIFY.md           # Verification workflow
├── 1.1/
│   └── EXPECTED.md
├── 1.2/
│   └── EXPECTED.md
...
├── 4.7/
│   └── EXPECTED.md
```

## Control Folders That Exist

60 possible folders (one per control):
- 1.1 through 1.23 (Pillar 1 - Security)
- 2.1 through 2.21 (Pillar 2 - Management)
- 3.1 through 3.10 (Pillar 3 - Reporting)
- 4.1 through 4.7 (Pillar 4 - SharePoint)

## Known Missing Folders (Low Priority)

These are screenshot spec gaps, not control gaps:
- 1.22, 1.23, 2.19, 2.20, 4.7 (missing folders)
- 2.17, 2.18, 3.10 (missing EXPECTED.md files)

## Portal Verification Sources

| Portal | URL |
|--------|-----|
| Power Platform Admin Center | admin.powerplatform.microsoft.com |
| Microsoft Purview Portal | purview.microsoft.com |
| Microsoft Entra Admin Center | entra.microsoft.com |
| Microsoft 365 Admin Center | admin.microsoft.com |
| SharePoint Admin Center | admin.microsoft.com/sharepoint |

## Related Skills

- `/update-control` - Update control after verification
