# Reporting Automation Scripts

Scripts for generating compliance reports and exporting governance data.

## Planned Scripts

| Script | Purpose | Related Control |
|--------|---------|-----------------|
| `generate-compliance-report.ps1` | Generate compliance dashboard report | Control 3.3 |
| `export-agent-metadata.ps1` | Export agent inventory with metadata | Control 3.1 |
| `reconcile-agent-inventory.ps1` | Reconcile agent inventory against PPAC | Control 3.6 |
| `create-compliance-dashboard.ps1` | Generate Power BI dashboard data | Control 3.8 |

## Prerequisites

- PowerShell 7.0+
- Microsoft Power Platform PowerShell modules
- Microsoft Graph PowerShell modules
- Read permissions on Power Platform Admin Center

## Output Formats

Scripts generate output in:
- CSV (for Excel import)
- JSON (for programmatic use)
- Markdown (for documentation)

---

*Coming in a future release*
