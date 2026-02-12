# Summary: Plan 04-01 — Control Updates + Solutions Catalog + Governance README

## Status: Complete

## Commits

| Commit | Description |
|--------|-------------|
| `10383e0` | docs(controls): add v17 governance script tip admonitions to 1.1, 3.7, 3.8 and solutions catalog entry |

## Tasks Completed

1. **Control 1.1** — Added 2 tip admonitions: `Test-AgentAuthConfiguration.ps1` (per-agent auth enforcement, 6 SSPM items) and `restrict-agent-publishing.ps1` (6 publishing restriction criteria)
2. **Control 3.7** — Added tip admonition for `restrict-agent-publishing.ps1` (publishing restriction validation with SHA-256 evidence)
3. **Control 3.8** — Added tip admonition for `Test-ZoneAgentAccess.ps1` (zone access validation, admin exclusion groups, deployment groups, adaptive card alerting)
4. **solutions-index.md** — Added overview table row, full detail section (components, regulatory alignment, related controls, script locations), and version history row for Agent Security Configuration Governance
5. **scripts/governance/README.md** — Removed 3 phantom scripts (configure-managed-environment.ps1, setup-sod-groups.ps1, enable-dlp-policies.ps1), added 5 UASD scripts that were missing from inventory (Deploy-DetectionFlow, Deploy-RemediationFlow, Export-ViolationReport, Import-ApprovedSecurityGroups, Invoke-SharingAudit)

## File Manifest

| File | Action |
|------|--------|
| `docs/controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md` | Modified |
| `docs/controls/pillar-3-reporting/3.7-ppac-security-posture-assessment.md` | Modified |
| `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md` | Modified |
| `docs/reference/solutions-index.md` | Modified |
| `scripts/governance/README.md` | Modified |

## Decisions Made

- Removed 3 phantom script entries from governance README (scripts that were listed but never created) — these were aspirational entries from earlier milestones
- Added 5 UASD scripts to README that existed on disk but weren't listed (all from v16 Unrestricted Agent Sharing Detector milestone)
- Placed governance script tips after existing advanced implementation tips in each control to maintain consistent ordering
