# Governance Automation Scripts

Scripts for automating governance control implementation.

## Scripts

| Script | Purpose | Related Control |
|--------|---------|-----------------|
| `Invoke-HardeningBaselineCheck.ps1` | Validate 18 hardening baseline items (6 agent publishing via cross-reference + 12 direct: audit logging, environment provisioning, environment security settings) | Controls 1.7, 2.1, 3.7 |
| `configure-managed-environment.ps1` | Enable Managed Environments | Control 2.1 |
| `setup-sod-groups.ps1` | Create segregation of duties groups | Control 2.8 |
| `enable-dlp-policies.ps1` | Configure DLP policies | Control 1.5 |
| `restrict-agent-publishing.ps1` | Validate 6 publishing restriction criteria (env maker role, security groups, sharing, DLP, managed env limits, approval workflow) | Controls 1.1, 2.1, 3.7 |
| `Test-AgentAuthConfiguration.ps1` | Validate per-agent authentication configuration against 6 SSPM items with zone-based logic | Control 1.1 |

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

## Integration Notes

`Invoke-HardeningBaselineCheck.ps1` cross-references `restrict-agent-publishing.ps1` for hardening baseline items 1-6 (agent publishing restrictions). When `restrict-agent-publishing.ps1` is present in the same directory, items 1-6 are reported as "Pass" with automation level noted. When absent, items 1-6 are reported as "Skip" requiring manual attestation.
