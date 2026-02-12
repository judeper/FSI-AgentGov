# Phase 3 Research: Zone Access Validation

## Context

Phase 3 automates M365 Admin Center agent access settings verification per zone policy, admin exclusion group validation, and drift detection with Teams notification support.

## Key APIs and Endpoints

### Agent Access Control Settings
- **Portal:** M365 Admin > Copilot > Settings > Actions
- **API:** Microsoft Graph — `GET https://graph.microsoft.com/beta/admin/microsoft365/copilot/settings` (beta endpoint)
- **Fallback:** PowerShell `Get-MgBetaAdminMicrosoft365CopilotSetting` or direct Graph REST
- **Settings of interest:** Agent access policy (all agents, org + MS verified, org only)

### Admin Exclusion Group
- **Portal:** M365 Admin > Copilot > Settings > User access
- **Group name:** `CopilotForM365AdminExclude` (exact name required)
- **API:** Microsoft Graph — `GET https://graph.microsoft.com/v1.0/groups?$filter=displayName eq 'CopilotForM365AdminExclude'`
- **Members:** `GET https://graph.microsoft.com/v1.0/groups/{id}/members`
- **Nested groups supported**

### Deployment Groups
- **Portal:** M365 Admin > Copilot > Settings > Deployment
- **API:** Microsoft Graph — deployment group configuration via beta endpoints
- **Validation:** Group exists, members assigned, phased rollout active

### Web Search Control
- **Portal:** M365 Admin > Copilot > Settings > Data access
- **Setting:** Web search enabled/disabled for organization
- **Zone policy:** Zone 1 enabled, Zone 2 disabled for MNPI teams, Zone 3 disabled org-wide

## Zone Policy Requirements (from Control 3.8)

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---------|-------------------|---------------|---------------------|
| Agent Access | All agents allowed | Organizational + Microsoft verified | Organizational only, approved list |
| Admin Exclusion | Not required | Compliance-sensitive roles | Traders, restricted persons, investigated employees |
| Deployment Groups | Optional | Recommended phased | Mandatory phased with approval |
| Web Search | Enabled | Disabled for MNPI | Disabled org-wide |

## Established Script Conventions

From Test-AgentAuthConfiguration.ps1 and restrict-agent-publishing.ps1:
- `#Requires -Version 7.0`
- `[CmdletBinding(SupportsShouldProcess)]`
- `$ErrorActionPreference = 'Stop'`
- Standard params: `$OutputFormat`, `$OutputPath`, `$ZoneMapping`, `$IncludeEvidence`
- Helper functions: `Get-EnvironmentZone`, result builder, `Get-EvidenceHash`
- SHA-256 evidence hashing
- Drift detection via baseline comparison (Import/Compare pattern)
- JSON output structured for Dataverse ingestion
- Cyan box-drawing banners

## Adaptive Card Pattern

From `src/adaptive-card-uasd-alert.json`:
- Schema version 1.4
- Header with severity badge
- Summary metrics section
- Detail table with findings
- Action buttons for portal links
- Template variables: `${SeverityStyle}`, `${OverallStatus}`, `${ScannedAt}`, etc.
