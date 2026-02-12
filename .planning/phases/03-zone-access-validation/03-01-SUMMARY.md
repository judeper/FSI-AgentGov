# Summary: Plan 03-01 — Script Core + Zone Policy Validation + Admin Exclusion Groups

## Status: Complete

## Deliverables

| Deliverable | Status | File |
|-------------|--------|------|
| Test-ZoneAgentAccess.ps1 | Complete | `scripts/governance/Test-ZoneAgentAccess.ps1` |

## Tasks Completed

1. **Script Scaffolding and Parameters** — Created with comment-based help, #Requires -Version 7.0, standard parameters (OutputFormat, OutputPath, ZoneMapping, IncludeEvidence, BaselinePath, ExpectedExclusionGroupName), CmdletBinding(SupportsShouldProcess), cyan banner
2. **Helper Functions** — Get-GraphApiToken, Invoke-GraphApi (with AdditionalHeaders support), Get-ZoneForContext, New-AccessCheckResult, Get-EvidenceHash, Import-AccessBaseline, Compare-AccessBaseline
3. **Check 1: Agent Access Policy (ZAV-01)** — Reads M365 Copilot settings via Graph beta API, normalizes policy values (AllAgents/OrgAndMicrosoftVerified/OrgOnly), zone-based validation per Control 3.8 table
4. **Check 2: Admin Exclusion Group (ZAV-02)** — Queries Entra ID for CopilotForM365AdminExclude, validates group type (security), checks member count with ConsistencyLevel=eventual, zone-appropriate enforcement
5. **Check 3: Deployment Group Configuration (ZAV-03)** — Reads deployment group settings via Graph beta, semi-automated with graceful degradation, zone-based enforcement (optional→recommended→mandatory)
6. **Check 4: Web Search Control (ZAV-04)** — Reads web search setting from Copilot configuration, zone-based validation (enabled OK Zone 1, warning Zone 2, fail Zone 3)
7. **Results Aggregation and Output** — Metadata/Summary/Checks/Drifts/Gaps structure, SHA-256 evidence hash, Table/JSON/Object output, baseline auto-save

## Decisions Made

- **Drift detection pre-integrated:** Import-AccessBaseline and Compare-AccessBaseline were implemented in Plan 01 rather than deferring to Plan 02, since the script architecture benefited from having drift detection wired into the main flow from the start
- **Graph API over BAP API:** Used Microsoft Graph API rather than BAP since M365 Admin Center settings are managed through Graph (different from Power Platform BAP endpoints used in other scripts)
- **No #Requires for modules:** Unlike the PPAC scripts that require Microsoft.PowerApps.Administration.PowerShell, this script only requires Az.Accounts for token acquisition (Get-AzAccessToken) — no Microsoft.Graph module dependency
- **Semi-automated checks:** Deployment groups (Check 3) and some Copilot settings may not be fully exposed via API in all tenants — implemented graceful Skip fallback with manual verification guidance

## Commits

1. `feat(governance): create Test-ZoneAgentAccess.ps1 — zone agent access validation` — 1145 lines, 4 check groups, drift detection, evidence hashing

## File Manifest

| Action | File |
|--------|------|
| Created | `scripts/governance/Test-ZoneAgentAccess.ps1` |

## Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| ZAV-01 | Delivered | Checks 1 (agent access policy) and 4 (web search) validate settings per zone |
| ZAV-02 | Delivered | Check 2 (exclusion group) and Check 3 (deployment groups) validate configuration |
