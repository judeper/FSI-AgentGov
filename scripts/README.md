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
├── governance/                         # Governance automation (17 scripts/files)
│   ├── README.md                       # Governance scripts overview
│   ├── Invoke-HardeningBaselineCheck.ps1  # Hardening baseline validation
│   ├── restrict-agent-publishing.ps1   # Publishing restriction validation
│   ├── Test-AgentAuthConfiguration.ps1 # Auth configuration validation
│   ├── Test-ZoneAgentAccess.ps1        # Zone access policy validation
│   ├── FsiMimeControl.psm1            # MIME type management module
│   ├── Set-InactivityTimeout.ps1       # Inactivity timeout remediation
│   ├── Deploy-DetectionFlow.ps1        # UASD detection flow deployment
│   ├── Deploy-RemediationFlow.ps1      # UASD remediation flow deployment
│   ├── Export-ViolationReport.ps1      # Sharing violation report export
│   ├── Import-ApprovedSecurityGroups.ps1 # Security group import
│   ├── Invoke-SharingAudit.ps1         # On-demand sharing audit
│   ├── ... (+ tests, data files)       # See governance/README.md for full list
│   └── mime-templates/                 # MIME type zone templates
│
├── config/                             # Monitoring configuration
│   ├── monitoring-config.yaml          # Learn & regulatory monitor settings
│   └── README.md                       # Configuration guide
│
├── reporting/                          # Reporting automation (planned)
│   └── README.md                       # Planned scripts overview
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
Standardizes control file formatting across the current 78-control catalog.

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

### Governance Automation

The `governance/` directory contains 17 PowerShell scripts and data files for automating governance control implementation. See [`governance/README.md`](governance/README.md) for full details, prerequisites, and usage instructions.

Key scripts include:
- `Invoke-HardeningBaselineCheck.ps1` - Validate 18 hardening baseline items
- `restrict-agent-publishing.ps1` - Validate 6 publishing restriction criteria
- `Test-AgentAuthConfiguration.ps1` - Validate per-agent authentication configuration
- `Test-ZoneAgentAccess.ps1` - Validate zone-based agent access policies
- `FsiMimeControl.psm1` - Zone-based MIME type configuration management
- `Set-InactivityTimeout.ps1` - Remediate inactivity timeout via BAP Admin API
- `Deploy-DetectionFlow.ps1` / `Deploy-RemediationFlow.ps1` - UASD flow deployment
- `Invoke-SharingAudit.ps1` - On-demand agent sharing audit scan

**Planned additions:**
- `configure-managed-environment.ps1` - Enable Managed Environments
- `setup-sod-groups.ps1` - Create segregation of duties groups
- `enable-dlp-policies.ps1` - Configure DLP policies

### Monitoring Configuration

The `config/` directory contains monitoring configuration for the Learn Monitor and Regulatory Monitor. See [`config/README.md`](config/README.md) for pattern syntax, classification tiers, and operational settings.

### Reporting Automation (Planned)

The `reporting/` directory contains planned scripts for compliance reporting and governance data export. See [`reporting/README.md`](reporting/README.md) for full details.

Future scripts for:
- `generate-compliance-report.ps1` - Generate compliance dashboard report
- `export-agent-metadata.ps1` - Export agent inventory with metadata
- `reconcile-agent-inventory.ps1` - Reconcile agent inventory against PPAC
- `create-compliance-dashboard.ps1` - Generate Power BI dashboard data

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
| `validate_before_push.py` | Pre-push validation suite | Mar 2026 |
| `verify_controls.py` | Control structure validation | Mar 2026 |
| `verify_templates.py` | Template format validation | Mar 2026 |
| `verify_excel_templates.py` | Excel template verification | Mar 2026 |
| `validate_docs_anchors.py` | Internal link checking | Mar 2026 |
| `audit_control_metadata.py` | Control metadata audit | Mar 2026 |

### Maintenance Scripts (5 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `normalize_controls.py` | Control formatting standardization | Mar 2026 |
| `compile_researcher_package.py` | Researcher package generation | Mar 2026 |
| `update_excel_templates.py` | Excel template updates | Mar 2026 |
| `extract_whitepaper_text.py` | Whitepaper text extraction | Mar 2026 |
| `check_temp.py` | Temp file verification utility | Mar 2026 |

### Governance Scripts (17 scripts/files)
| Script | Purpose | Related Control |
|--------|---------|-----------------|
| `governance/Invoke-HardeningBaselineCheck.ps1` | Hardening baseline validation (18 items) | 1.7, 2.1, 3.7 |
| `governance/restrict-agent-publishing.ps1` | Publishing restriction validation (6 criteria) | 1.1, 2.1, 3.7 |
| `governance/Test-AgentAuthConfiguration.ps1` | Per-agent auth config validation | 1.1 |
| `governance/Test-ZoneAgentAccess.ps1` | Zone access policy validation | 3.8 |
| `governance/FsiMimeControl.psm1` | MIME type management module | 1.25 |
| `governance/FsiMimeControl.Tests.ps1` | Pester 5 tests for MIME module (40 tests) | 1.25 |
| `governance/register-plugin.ps1` | Dataverse plugin registration | 1.25 |
| `governance/test-plugin.ps1` | Plugin integration tests | 1.25 |
| `governance/validate-exceptions.ps1` | MIME exception register validation | 1.25 |
| `governance/mime-type-exceptions.csv` | MIME type exception register | 1.25 |
| `governance/Set-InactivityTimeout.ps1` | Inactivity timeout remediation | 2.22 |
| `governance/Set-InactivityTimeout.Tests.ps1` | Pester 5 tests for timeout (44 tests) | 2.22 |
| `governance/Deploy-DetectionFlow.ps1` | UASD detection flow deployment | 1.1 |
| `governance/Deploy-RemediationFlow.ps1` | UASD remediation flow deployment | 1.1 |
| `governance/Export-ViolationReport.ps1` | Sharing violation report export | 1.1 |
| `governance/Import-ApprovedSecurityGroups.ps1` | Security group import | 1.1 |
| `governance/Invoke-SharingAudit.ps1` | On-demand sharing audit | 1.1, 3.8 |

### Hooks (2 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `hooks/researcher-package-reminder.py` | Claude Code post-edit reminder | Mar 2026 |
| `hooks/boundary-check.py` | Claude Code command boundary check | Mar 2026 |

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

*FSI Agent Governance Framework v1.2 - March 2026*
