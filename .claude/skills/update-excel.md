---
name: update-excel
description: Use when maintaining Excel checklist templates after adding new controls or updating version references
allowed-tools: Read, Bash, Glob
user-invocable: true
---

# Skill: Update Excel Templates

Use this skill when maintaining Excel checklist templates after adding new controls.

## Template Files

Located in: `docs/downloads/`

| File | Role | Controls | Notes |
|------|------|----------|-------|
| `governance-maturity-dashboard.xlsx` | AI Governance Lead | 61 (all) | "All Controls" + "Summary Dashboard" sheets |
| `purview-administrator-checklist.xlsx` | Purview Compliance Admin | 7 | DLP, DSPM, Audit, eDiscovery |
| `sharepoint-administrator-checklist.xlsx` | SharePoint Admin | 7 | IAG, Access Reviews, Retention |
| `power-platform-administrator-checklist.xlsx` | Power Platform Admin | 7 | Environments, Groups, Routing |
| `compliance-officer-checklist.xlsx` | Compliance Officer | 11 | Regulatory controls |
| `entra-administrator-checklist.xlsx` | Entra Global Admin | 4 | Conditional Access, RBAC |

## Control-to-Checklist Mapping

| Control Category | Target Checklist |
|------------------|------------------|
| Pillar 1 Purview controls | `purview-administrator-checklist.xlsx` |
| Pillar 2 Power Platform controls | `power-platform-administrator-checklist.xlsx` |
| Pillar 4 SharePoint controls | `sharepoint-administrator-checklist.xlsx` |
| Regulatory/compliance controls | `compliance-officer-checklist.xlsx` |
| Entra-managed controls | `entra-administrator-checklist.xlsx` |
| **ALL controls** | `governance-maturity-dashboard.xlsx` |

See `docs/downloads/index.md` for full mapping.

## Python Dependencies

```bash
pip install openpyxl
```

## Automated Scripts

**Verify templates:**
```bash
python scripts/verify_excel_templates.py
```

**Update templates (version refs, missing controls):**
```bash
python scripts/update_excel_templates.py
```

## Manual Update Workflow

### Step 1: Identify Target File(s)
Based on control category (see mapping above).

### Step 2: Open with openpyxl

```python
from openpyxl import load_workbook

wb = load_workbook('docs/downloads/governance-maturity-dashboard.xlsx')
ws = wb.active  # or wb['Sheet Name']
```

### Step 3: Handle Merged Cells (Dashboard Only)

The `governance-maturity-dashboard.xlsx` has merged cells for pillar headers.

```python
# Unmerge before editing
for merged in list(ws.merged_cells.ranges):
    ws.unmerge_cells(str(merged))

# ... make edits ...

# Re-merge after (pillar header rows)
ws.merge_cells('A5:E5')  # Pillar 1 header
```

### Step 4: Insert New Control Row

```python
# Find insertion point (maintain numerical order within pillar)
# All checklists use column format: Control ID | Control Name | Status | Notes | Due Date

row = find_insertion_row(ws, control_id)
ws.insert_rows(row)
ws.cell(row=row, column=1, value='1.24')
ws.cell(row=row, column=2, value='New Control Name')
ws.cell(row=row, column=3, value='Not Started')
```

### Step 5: Update Summary Dashboard (Dashboard Only)

Update control counts on "Summary Dashboard" sheet.

### Step 6: Save

```python
wb.save('docs/downloads/governance-maturity-dashboard.xlsx')
```

## Version Updates

When updating framework version, update version footer in all 6 files:
- Cell location varies by file (typically bottom-right area)
- Search for "v1.1" pattern

## Validation

After updates:
```bash
python scripts/verify_excel_templates.py
```

Expected output: "All 6 files pass"

## Related Skills

- `/add-control` - Creates new controls (triggers Excel update need)
