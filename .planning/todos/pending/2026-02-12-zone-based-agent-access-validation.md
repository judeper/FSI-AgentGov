# Todo: Zone-Based Agent Access Validation Automation

**Created:** 2026-02-12
**Source:** v16 research — Control 3.8 gap analysis
**Priority:** high

## Description

Automate validation that M365 Admin Center agent access settings match zone policy definitions. Control 3.8 defines zone-specific agent access rules (Zone 1: all agents, Zone 2: Organizational + Microsoft verified, Zone 3: Organizational only with approval), but no automation verifies these settings are correctly applied.

### Gaps

| Area | What It Validates | Current State |
|---|---|---|
| Agent Access Control settings | Zone-specific allowed agent types match policy | No automation — portal walkthrough only |
| Admin Exclusion Groups | `CopilotForM365AdminExclude` group exists and is populated | No automation — manual Entra group setup |
| Deployment Group rollout | Staged deployment groups configured per zone | No automation — manual M365 Admin Center |
| Agent registry validation | Only approved agents listed in zone registries | No automation |

### What Already Exists

- Control 3.8 documents Agent Access Control (GA) with zone-based tables
- Agent Access Governance Monitor (v6) is listed as "Work In Progress" in solutions-index.md (status discrepancy: MILESTONES.md says "Shipped")
- Portal walkthrough Step 5 covers manual Agent Access Control configuration
- Verification criteria 13-16 in Control 3.8 cover agent access but are manual

### Status Discrepancy to Resolve

The Agent Access Governance Monitor is listed as:
- **"Shipped"** in `.planning/MILESTONES.md`, `.planning/STATE.md`, `.planning/PROJECT.md`
- **"Work In Progress"** in `docs/reference/solutions-index.md`

This discrepancy should be reconciled as part of v16 scoping.

### What Needs to Be Built

- PowerShell automation to read M365 Admin Center agent access configuration via Graph API or PPAC endpoints
- Zone-policy compliance engine comparing actual settings to documented zone requirements
- Drift detection for agent access setting changes
- Dataverse tables for validation history and zone-policy baselines
- Power Automate daily orchestration with Teams alerting

### Regulatory Driver

- FINRA 3110 (supervisory control over agent access)
- SOX 404 (IT general controls — access management)
- GLBA 501(b) (safeguards for customer information access)
- OCC 2011-12 (model risk management — access governance)

### Related Controls

- Control 3.8 — Copilot Hub and Governance Dashboard
- Control 1.1 — Restrict Agent Publishing by Authorization
- Control 2.1 — Managed Environments (app allow/block lists)
