# Governance Automation Scripts

Scripts for automating governance control implementation.

## Scripts

| Script | Purpose | Related Control |
|--------|---------|-----------------|
| `Invoke-HardeningBaselineCheck.ps1` | Validate 18 hardening baseline items (6 agent publishing via cross-reference + 12 direct: audit logging, environment provisioning, environment security settings) | Controls 1.7, 2.1, 3.7 |
| `restrict-agent-publishing.ps1` | Validate 6 publishing restriction criteria (env maker role, security groups, sharing, DLP, managed env limits, approval workflow) | Controls 1.1, 2.1, 3.7 |
| `Test-AgentAuthConfiguration.ps1` | Validate per-agent authentication configuration against 6 SSPM items with zone-based logic | Control 1.1 |
| `Test-ZoneAgentAccess.ps1` | Validate M365 agent access settings against zone-based governance policies (agent access policy, admin exclusion groups, deployment groups, web search) | Control 3.8 |
| `Deploy-DetectionFlow.ps1` | Deploy UASD detection flow to Power Automate | Control 1.1 |
| `Deploy-RemediationFlow.ps1` | Deploy UASD remediation flow to Power Automate | Control 1.1 |
| `Export-ViolationReport.ps1` | Export sharing violation report with SHA-256 evidence | Control 1.1 |
| `Import-ApprovedSecurityGroups.ps1` | Import approved security groups for sharing validation | Control 1.1 |
| `Invoke-SharingAudit.ps1` | On-demand agent sharing audit scan | Control 1.1, 3.8 |
| `Set-InactivityTimeout.ps1` | Remediate inactivity timeout via BAP Admin API PATCH (GET-PATCH-GET pattern with WhatIf, evidence packaging) | Control 2.22 |
| `Set-InactivityTimeout.Tests.ps1` | Pester 5 validation test suite (27 tests) for Set-InactivityTimeout | Control 2.22 |

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

`Test-ZoneAgentAccess.ps1` has a companion adaptive card template at `src/adaptive-card-zone-access-alert.json` for Teams webhook notifications when zone access policy drift is detected. The template follows the same pattern as `src/adaptive-card-uasd-alert.json` with scalar and per-finding template variables for Power Automate flow integration.
