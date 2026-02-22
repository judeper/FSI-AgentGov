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
│   ├── verify_language_rules.py        # Check regulatory language compliance
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
├── Monitoring Scripts (root level)
│   ├── learn_monitor.py               # Microsoft Learn documentation change monitor
│   ├── regulatory_monitor.py          # Regulatory source change monitor
│   └── monitoring_shared.py           # Shared monitoring utilities
│
├── Solution Deployment Scripts (root level)
│   ├── deploy.py                      # Solution deployment orchestrator
│   ├── create_asard_dataverse_schema.py   # ASARD Dataverse schema creation
│   ├── create_connection_references.py    # Connection reference setup
│   ├── create_dataverse_schema.py         # Dataverse schema creation
│   ├── create_environment_variables.py    # Environment variable setup
│   ├── create_timeout_connection_references.py  # Timeout solution connections
│   ├── create_timeout_dataverse_schema.py       # Timeout Dataverse schema
│   ├── create_timeout_environment_variables.py  # Timeout environment variables
│   ├── create_timeout_errorlog_schema.py        # Timeout error log schema
│   ├── create_uasd_connection_references.py     # UASD connections
│   ├── create_uasd_dataverse_schema.py          # UASD Dataverse schema
│   └── create_uasd_environment_variables.py     # UASD environment variables
│
├── Agent & Policy Scripts (root level)
│   ├── detect_agent_sharing_violations.py    # Detect sharing violations
│   ├── remediate_agent_sharing.py            # Remediate sharing violations
│   ├── asard_zone_rules.py                   # ASARD zone rule definitions
│   ├── bap_admin_client.py                   # BAP admin API client
│   ├── caa_client.py                         # Conditional Access Automation client
│   ├── generate_excel_templates.py           # Generate Excel templates
│   ├── Start-CAAValidationRunbook.ps1        # CAA validation runbook
│   ├── Test-PolicyCompliance.ps1             # Policy compliance testing
│   └── conditional-access-automation.psd1    # CAA module manifest
│
├── Test Scripts (root level)
│   ├── test_asard_zone_rules.py              # ASARD zone rules tests
│   ├── test_bap_admin_client.py              # BAP admin client tests
│   ├── test_detect_agent_sharing_violations.py   # Sharing violation tests
│   └── test_remediate_agent_sharing.py       # Sharing remediation tests
│
├── config/                             # Monitoring configuration
│   ├── README.md                       # Configuration guide
│   └── monitoring-config.yaml          # Monitor classification settings
│
├── governance/                         # Governance automation (19 items)
│   ├── README.md                       # Governance scripts overview
│   ├── Invoke-HardeningBaselineCheck.ps1   # Hardening baseline validation
│   ├── Deploy-DetectionFlow.ps1        # Detection flow deployment
│   ├── Deploy-RemediationFlow.ps1      # Remediation flow deployment
│   ├── Export-ViolationReport.ps1      # Violation report export
│   ├── Import-ApprovedSecurityGroups.ps1   # Security group import
│   ├── Invoke-SharingAudit.ps1         # Sharing audit execution
│   ├── Set-InactivityTimeout.ps1       # Inactivity timeout configuration
│   ├── Test-AgentAuthConfiguration.ps1 # Agent auth config testing
│   ├── Test-ZoneAgentAccess.ps1        # Zone agent access testing
│   ├── register-plugin.ps1            # Plugin registration
│   ├── restrict-agent-publishing.ps1   # Agent publishing restrictions
│   ├── test-plugin.ps1                # Plugin testing
│   ├── validate-exceptions.ps1        # Exception validation
│   ├── FsiMimeControl.psm1            # MIME control module
│   ├── FsiMimeControl.Tests.ps1       # MIME control tests
│   ├── Set-InactivityTimeout.Tests.ps1 # Inactivity timeout tests
│   ├── mime-type-exceptions.csv       # MIME type exception list
│   └── mime-templates/                # Zone MIME templates (zone1-3.json)
│
├── private/                            # Internal utility modules
│   ├── CAAClient.psm1                 # CAA client module
│   ├── Compare-PolicyBaseline.ps1     # Policy baseline comparison
│   ├── Connect-GraphSession.ps1       # Graph API session management
│   ├── Get-PolicyBaseline.ps1         # Policy baseline retrieval
│   ├── Get-ZoneClassification.ps1     # Zone classification lookup
│   └── Test-ParameterValidation.ps1   # Parameter validation testing
│
├── reporting/                          # Reporting automation (planned)
│   └── README.md                       # Placeholder
│
└── hooks/                              # Claude Code hooks
    ├── researcher-package-reminder.py  # Remind to update researcher package
    └── boundary-check.py              # Prevent commands outside project
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

**Verify regulatory language compliance:**
```bash
python scripts/verify_language_rules.py
```
Checks documentation for prohibited regulatory language (e.g., "ensures compliance", "guarantees").

### Maintenance Scripts

**Normalize control formatting:**
```bash
python scripts/normalize_controls.py
```
Standardizes control file formatting across all 71 controls.

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

The `governance/` directory contains 16 PowerShell scripts for hardening baseline checks, sharing audits, MIME type controls, agent authentication testing, and more. See [`governance/README.md`](governance/README.md) for the full inventory and usage instructions.

### Monitoring Scripts

**Learn Monitor** — detects changes in Microsoft Learn documentation that may require playbook updates:
```bash
python scripts/learn_monitor.py
```

**Regulatory Monitor** — detects new rules and notices from SEC, CFTC, OCC, Federal Reserve, and FINRA:
```bash
python scripts/regulatory_monitor.py
```

Configuration is managed via `scripts/config/monitoring-config.yaml`. See [`config/README.md`](config/README.md) for the configuration guide.

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

### Validation Scripts (7 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `validate_before_push.py` | Pre-push validation suite | v1.1 |
| `verify_controls.py` | Control structure validation | v1.1 |
| `verify_templates.py` | Template format validation | v1.1 |
| `verify_excel_templates.py` | Excel template verification | Jan 2026 |
| `verify_language_rules.py` | Regulatory language compliance checking | v1.2 |
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

### Monitoring Scripts (3 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `learn_monitor.py` | Microsoft Learn documentation change detection | v1.2 |
| `regulatory_monitor.py` | Regulatory source change detection | v1.2 |
| `monitoring_shared.py` | Shared monitoring utilities and config loader | v1.2 |

### Solution Deployment Scripts (12 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `deploy.py` | Solution deployment orchestrator | v1.2 |
| `create_asard_dataverse_schema.py` | ASARD Dataverse schema creation | v1.2 |
| `create_connection_references.py` | Connection reference setup | v1.2 |
| `create_dataverse_schema.py` | Dataverse schema creation | v1.2 |
| `create_environment_variables.py` | Environment variable setup | v1.2 |
| `create_timeout_connection_references.py` | Timeout solution connection references | v1.2 |
| `create_timeout_dataverse_schema.py` | Timeout Dataverse schema | v1.2 |
| `create_timeout_environment_variables.py` | Timeout environment variables | v1.2 |
| `create_timeout_errorlog_schema.py` | Timeout error log schema | v1.2 |
| `create_uasd_connection_references.py` | UASD connection references | v1.2 |
| `create_uasd_dataverse_schema.py` | UASD Dataverse schema | v1.2 |
| `create_uasd_environment_variables.py` | UASD environment variables | v1.2 |

### Agent & Policy Scripts (9 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `detect_agent_sharing_violations.py` | Detect sharing violations | v1.2 |
| `remediate_agent_sharing.py` | Remediate sharing violations | v1.2 |
| `asard_zone_rules.py` | ASARD zone rule definitions | v1.2 |
| `bap_admin_client.py` | BAP admin API client | v1.2 |
| `caa_client.py` | Conditional Access Automation client | v1.2 |
| `generate_excel_templates.py` | Generate Excel templates | v1.2 |
| `Start-CAAValidationRunbook.ps1` | CAA validation runbook | v1.2 |
| `Test-PolicyCompliance.ps1` | Policy compliance testing | v1.2 |
| `conditional-access-automation.psd1` | CAA module manifest | v1.2 |

### Test Scripts (4 scripts)
| Script | Purpose | Last Updated |
|--------|---------|--------------|
| `test_asard_zone_rules.py` | ASARD zone rules tests | v1.2 |
| `test_bap_admin_client.py` | BAP admin client tests | v1.2 |
| `test_detect_agent_sharing_violations.py` | Sharing violation detection tests | v1.2 |
| `test_remediate_agent_sharing.py` | Sharing remediation tests | v1.2 |

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

*FSI Agent Governance Framework v1.2 - February 2026*
