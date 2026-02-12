# v16 Research: Architecture Patterns — Unrestricted Agent Sharing Detector

**Dimension:** Architecture
**Created:** 2026-02-12

## Solution Pattern: Tier 2 (PowerShell + Dataverse + Power Automate)

UASD follows the established Tier 2 pattern used by ACV, SSC, AAM, CMM, FUS, and CAA.

### Component Map

```
BAP API ──► Detector Flow ──► Dataverse Tables ──► Remediation Flow ──► BAP API (PATCH)
                                    │                      │
                                    │                      ▼
                                    │               Approval Request
                                    │                      │
                                    ▼                      ▼
                              Teams Alert           Exception Manager App
                                    │                      │
                                    ▼                      ▼
                           Export Script        Exception Approval Flow
```

## Dataverse Table Design

### Table Pattern (5 tables — extended from standard 3-table pattern)

| Table | Pattern Role | Ownership | Immutability |
|-------|-------------|-----------|-------------|
| `fsi_AgentSharingSetting` | Baseline/State | Organization-owned | Mutable (current state) |
| `fsi_SharingViolation` | Violation/Event | Organization-owned | Append-only (audit trail) |
| `fsi_SharingException` | Exception/Override | Organization-owned | Mutable (status transitions) |
| `fsi_ApprovedSecurityGroup` | Configuration | Organization-owned | Mutable (admin-managed) |
| `fsi_SharingPolicy` | Configuration | Organization-owned | Mutable (threshold tuning) |

### Agent Identity (Inline — no agentvault dependency)

Since Control 3.1 agent inventory is CSV/SharePoint-based (not Dataverse), agent identity is stored inline:

- `fsi_agent_id` (Text) — BAP agent/bot ID
- `fsi_agent_name` (Text) — display name from BAP
- `fsi_environment_id` (Text) — Power Platform environment ID

This appears on `fsi_AgentSharingSetting`, `fsi_SharingViolation`, and `fsi_SharingException`.

### Option Set Reuse

| Option Set | Source | Used In |
|-----------|--------|---------|
| `fsi_acv_zone` | ACV (shared global) | `fsi_ApprovedSecurityGroup.fsi_zone`, `fsi_SharingPolicy.fsi_governancezone` |
| `fsi_acv_severity` | ACV (shared global) | `fsi_SharingViolation.fsi_severity` — mapped: Critical→Failed(4), High→Error(5), Medium→Warning(2), Low→GracePeriod(3) |
| `fsi_UASD_sharingscope` | UASD (solution-specific) | Individual, SecurityGroup, Organization, Public |
| `fsi_UASD_violationtype` | UASD (solution-specific) | 5 violation types per spec |
| `fsi_UASD_violationstatus` | UASD (solution-specific) | Open, Remediated, Exception_Granted, False_Positive |
| `fsi_UASD_exceptionstatus` | UASD (solution-specific) | Pending, Approved, Denied, Expired |
| `fsi_UASD_authmode` | UASD (solution-specific) | ManualAuthentication, NoAuthentication |

## Power Automate Flow Patterns

### Detector Flow (`fsi-UASD-Detector-ScanAgents`)
- **Trigger:** Scheduled recurrence
- **Pattern:** HTTP action → BAP API → Apply to Each → Dataverse upsert → Condition evaluations → Violation insert
- **Error handling:** Scope_Try/Scope_Catch wrapping all API calls

### Remediation Flow (`fsi-UASD-Remediation-ApplySharingPolicy`)
- **Trigger:** Dataverse row created/updated on `fsi_SharingViolation` where status = Open
- **Pattern:** Exception check → Mode determination → Approval (default) or Auto → BAP PATCH → Status update
- **Non-negotiable:** Default mode is Approval for ALL zones. Auto only for PUBLIC_INTERNET_LINK when explicitly enabled.

### Exception Approval Flow (`fsi-UASD-ExceptionApproval-Workflow`)
- **Trigger:** Dataverse row created on `fsi_SharingException` where status = Pending
- **Pattern:** Sequential approval (Security → Data Owner) → Status update → Expiration scheduling

## Cross-Repository Integration

| Repository | Contains | Path/Folder |
|-----------|----------|-------------|
| FSI-AgentGov | Framework docs, deployment guide, architecture docs | `docs/playbooks/advanced-implementations/unrestricted-agent-sharing-detector/` |
| FSI-AgentGov-Solutions | Scripts, flow JSONs, app definition, schema scripts | `unrestricted-agent-sharing-detector/` |

## Deployment Pattern

Follows `deploy.py` selective flags pattern from CAA and other solutions:
- `Deploy-DetectionFlow.ps1` — idempotent flow import
- `Deploy-RemediationFlow.ps1` — idempotent flow import
- `Import-ApprovedSecurityGroups.ps1` — seed approved groups
- Lab-grade: interactive auth, manual Dataverse table provisioning via schema script

## Confidence: High

Pattern is well-established across 12 shipped solutions. UASD extends to 5 tables (vs standard 3) to accommodate exception management and policy configuration — justified by spec requirements.
