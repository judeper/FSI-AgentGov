# FSI Agent Governance Framework - Scripts

Scripts for validating, maintaining, and automating governance controls.

## Directory Structure

```
scripts/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── validate_before_push.py             # Pre-push validation (run before every push)
│
├── Validation Scripts (root level)
│   ├── verify_controls.py              # Validate control structure and footers
│   ├── verify_templates.py             # Validate template formats
│   ├── verify_excel_templates.py       # Verify Excel template content and counts
│   ├── validate_docs_anchors.py        # Check internal links
│   └── audit_control_metadata.py       # Audit control file metadata
│
├── Maintenance Scripts (root level)
│   ├── normalize_controls.py           # Standardize control formatting
│   ├── compile_researcher_package.py   # Compile controls into researcher package
│   ├── update_excel_templates.py       # Update Excel templates to v1.1
│   ├── extract_whitepaper_text.py      # Extract text from whitepaper PDF
│   └── check_temp.py                   # Utility to check temp files
│
├── governance/                         # Governance automation (planned)
│   └── README.md                       # Placeholder
│
├── reporting/                          # Reporting automation (planned)
│   └── README.md                       # Placeholder
│
└── hooks/                              # Claude Code hooks
    ├── researcher-package-reminder.py  # Remind to update researcher package
    └── boundary-check.py               # Prevent commands outside project
```

## Prerequisites

### Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r scripts/requirements.txt
```

### Required Modules

- Python 3.9+
- `openpyxl` - For Excel template manipulation (install via requirements.txt)
- `pypdf` - For whitepaper text extraction (install via requirements.txt)

## Usage

### Pre-Push Validation (Recommended)

**Run all validations before pushing:**
```bash
python scripts/validate_before_push.py
```

This script runs:
1. `mkdocs build --strict` - Validates internal links and markdown syntax
2. `verify_controls.py` - Validates control file structure and footers
3. `markdown-link-check` - Validates external URLs (requires: `npm install -g markdown-link-check`)

Run this before every push to catch issues before CI fails.

### Validation Scripts

**Verify all controls follow required structure:**
```bash
python scripts/verify_controls.py
```
Validates control file structure, required sections, and footer metadata.

**Validate template formatting:**
```bash
python scripts/verify_templates.py
```
Ensures all template files follow proper formatting standards.

**Verify Excel template content:**
```bash
python scripts/verify_excel_templates.py
```
Checks Excel files in `docs/downloads/` for:
- Correct control counts per template
- Stale version references (v1.0)
- Outdated control counts (48 controls)
- Legacy path references

**Check internal document links:**
```bash
python scripts/validate_docs_anchors.py
```
Validates all internal markdown links and cross-references.

**Audit control metadata:**
```bash
python scripts/audit_control_metadata.py
```
Checks control files for required metadata fields and footer format.

### Maintenance Scripts

**Normalize control formatting:**
```bash
python scripts/normalize_controls.py
```
Standardizes control file formatting across all 61 controls.

**Compile researcher package:**
```bash
python scripts/compile_researcher_package.py
```
Creates consolidated markdown files in `maintainers-local/researcher-package/` for external research review. Generates:
- `00-FSI-AgentGov-Summary-and-Review-Guide.md`
- `01-Pillar-1-Security-Controls.md`
- `02-Pillar-2-Management-Controls.md`
- `03-Pillar-3-Reporting-Controls.md`
- `04-Pillar-4-SharePoint-Controls.md`

**Update Excel templates:**
```bash
python scripts/update_excel_templates.py --check    # Preview changes only
python scripts/update_excel_templates.py --update   # Apply changes
```
Updates all Excel files in `docs/downloads/` to v1.1 and adds missing controls.

**Extract whitepaper text:**
```bash
python scripts/extract_whitepaper_text.py
```
Extracts searchable text from the Agent Governance whitepaper PDF. Outputs to `maintainers-local/reference-pack/` (gitignored, maintainer-only).

**Check temp files:**
```bash
python scripts/check_temp.py
```
Utility to verify temp files match repository files (development/debugging use).

### Governance Automation (Planned)

Future scripts for:
- `configure-managed-environment.ps1` - Enable Managed Environments
- `setup-sod-groups.ps1` - Create segregation of duties groups
- `enable-dlp-policies.ps1` - Configure DLP policies

### Reporting Automation (Planned)

Future scripts for:
- `generate-compliance-report.ps1` - Generate compliance reports
- `export-agent-metadata.ps1` - Export agent inventory

## Safety Notes

!!! warning "Production Use"
    - **Always test in non-production first** - Scripts may modify tenant configuration
    - **Review before running** - Read script source to understand actions
    - **Backup configurations** - Export settings before making changes
    - **Use least privilege** - Run with minimum required permissions

## Script Standards

All scripts should follow these standards:

1. **Documentation** - Include synopsis, description, parameters, examples
2. **Error handling** - Graceful failure with informative messages
3. **Logging** - Write to console and optionally to file
4. **No hard-coded values** - Use parameters for configuration
5. **Last Verified date** - Include date script was last tested

## Script Inventory

### Validation Scripts (6 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `validate_before_push.py` | Pre-push validation suite | v1.1 |
| `verify_controls.py` | Control structure validation | v1.1 |
| `verify_templates.py` | Template format validation | v1.1 |
| `verify_excel_templates.py` | Excel template verification | Jan 2026 |
| `validate_docs_anchors.py` | Internal link checking | v1.1 |
| `audit_control_metadata.py` | Control metadata audit | v1.1 |

### Maintenance Scripts (5 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `normalize_controls.py` | Control formatting standardization | v1.1 |
| `compile_researcher_package.py` | Researcher package generation | v1.1 |
| `update_excel_templates.py` | Excel template updates | Jan 2026 |
| `extract_whitepaper_text.py` | Whitepaper text extraction | v1.1 |
| `check_temp.py` | Temp file verification utility | Dev only |

### Hooks (2 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `hooks/researcher-package-reminder.py` | Claude Code post-edit reminder | v1.1 |
| `hooks/boundary-check.py` | Claude Code command boundary check | v1.1 |

## Contributing

When adding new scripts:

1. Place in appropriate category (validation, maintenance, hooks)
2. Add script documentation header with synopsis and usage
3. Update this README with script details in inventory table
4. Test in non-production environment
5. Add to `requirements.txt` if new dependencies needed
6. Run `validate_before_push.py` before committing

## Related Documentation

- [Framework Overview](../docs/framework/index.md)
- [Control Catalog](../docs/controls/CONTROL-INDEX.md)
- [Playbooks](../docs/playbooks/index.md)
- [Claude Code Instructions](../.claude/CLAUDE.md)

---

*FSI Agent Governance Framework v1.1 - January 2026*
