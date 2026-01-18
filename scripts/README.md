# FSI Agent Governance Framework - Scripts

Scripts for validating, maintaining, and automating governance controls.

## Directory Structure

```
scripts/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
│
├── validation/                  # Framework validation scripts
│   ├── verify_controls.py       # Validate control structure
│   ├── verify_templates.py      # Validate template formats
│   ├── validate_docs_anchors.py # Check internal links
│   └── audit_controls_zone_hygiene.py # Zone guidance consistency
│
├── maintenance/                 # Framework maintenance scripts
│   ├── normalize_controls.py    # Standardize control formatting
│   ├── apply_primary_owner_roles.py # Update role assignments
│   └── refactor_controls_to_canonical_sections.py # Section reorg
│
├── governance/                  # Governance automation (planned)
│   └── README.md                # Placeholder
│
├── reporting/                   # Reporting automation (planned)
│   └── README.md                # Placeholder
│
└── hooks/                       # Claude Code hooks
    ├── researcher-package-reminder.py # Remind to update researcher package
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
- No external dependencies for core validation scripts

## Usage

### Validation Scripts

**Verify all controls follow required structure:**
```bash
python scripts/verify_controls.py
```

**Validate template formatting:**
```bash
python scripts/verify_templates.py
```

**Check internal document links:**
```bash
python scripts/validate_docs_anchors.py
```

**Audit zone guidance consistency:**
```bash
python scripts/audit_controls_zone_hygiene.py
```

### Maintenance Scripts

**Normalize control formatting:**
```bash
python scripts/normalize_controls.py
```

**Apply role updates:**
```bash
python scripts/apply_primary_owner_roles.py
```

### Governance Automation (Planned)

Future scripts for:
- `configure-managed-environment.ps1` — Enable Managed Environments
- `setup-sod-groups.ps1` — Create segregation of duties groups
- `enable-dlp-policies.ps1` — Configure DLP policies

### Reporting Automation (Planned)

Future scripts for:
- `generate-compliance-report.ps1` — Generate compliance reports
- `export-agent-metadata.ps1` — Export agent inventory

## Safety Notes

!!! warning "Production Use"
    - **Always test in non-production first** — Scripts may modify tenant configuration
    - **Review before running** — Read script source to understand actions
    - **Backup configurations** — Export settings before making changes
    - **Use least privilege** — Run with minimum required permissions

## Script Standards

All scripts should follow these standards:

1. **Documentation** — Include synopsis, description, parameters, examples
2. **Error handling** — Graceful failure with informative messages
3. **Logging** — Write to console and optionally to file
4. **No hard-coded values** — Use parameters for configuration
5. **Last Verified date** — Include date script was last tested

## Contributing

When adding new scripts:

1. Place in appropriate category folder
2. Add script documentation header
3. Update this README
4. Test in non-production environment
5. Add to `requirements.txt` if new dependencies needed

## Related Documentation

- [Framework Overview](../docs/framework/index.md)
- [Control Catalog](../docs/controls/index.md)
- [Playbooks](../docs/playbooks/index.md)

---

*FSI Agent Governance Framework v1.1 - January 2026*
