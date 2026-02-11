# Governance Automation Scripts

Scripts for automating governance control implementation.

## Scripts

| Script | Purpose | Related Control |
|--------|---------|-----------------|
| `Invoke-HardeningBaselineCheck.ps1` | Validate hardening baseline items (audit logging, environment provisioning) | Controls 1.7, 2.1 |
| `configure-managed-environment.ps1` | Enable Managed Environments | Control 2.1 |
| `setup-sod-groups.ps1` | Create segregation of duties groups | Control 2.8 |
| `enable-dlp-policies.ps1` | Configure DLP policies | Control 1.5 |
| `restrict-agent-publishing.ps1` | Restrict agent publishing | Control 1.1 |

## Prerequisites

- PowerShell 7.0+
- Microsoft Power Platform PowerShell modules
- Microsoft Graph PowerShell modules
- Appropriate admin permissions

## Usage

Scripts in this directory require elevated permissions and should be:

1. Reviewed before execution
2. Tested in non-production environment
3. Run with appropriate admin credentials
4. Logged for audit purposes
