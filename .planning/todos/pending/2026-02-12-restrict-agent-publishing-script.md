# Todo: Create restrict-agent-publishing.ps1 Governance Script

**Created:** 2026-02-12
**Source:** v16 research — phantom script reference in scripts/governance/README.md
**Priority:** high

## Description

The `scripts/governance/README.md` lists `restrict-agent-publishing.ps1` as a planned governance script for Control 1.1, but the file was never created. This is a gap between documentation and actual artifacts.

### Gaps

| Area | Current State |
|---|---|
| `restrict-agent-publishing.ps1` | Listed in README.md but file does not exist |
| Publishing restriction validation | Only 3 of 11 Control 1.1 checks automated (env role, auth group, share with everyone) |
| DLP channel blocking verification | Documented in Control 1.1 but no script validates it |
| Security group enforcement | Playbook has manual steps, no governance-level recurring check |
| Managed Environment sharing limits | Documented but not validated by automation |

### What Already Exists

- `scripts/governance/Invoke-HardeningBaselineCheck.ps1` — 630 lines, validates 12 items (items 7-9 audit logging, 14-17 environment provisioning, 28-32 environment security). Does NOT cover items 1-6 (agent-level auth checks for Control 1.1).
- `docs/playbooks/control-implementations/1.1/powershell-setup.md` — 3 PowerShell operations (Remove-AdminPowerAppEnvironmentRoleAssignment, Set-AdminPowerAppEnvironmentRoleAssignment, Set-TenantSettings)

### What Needs to Be Built

A governance script that validates:
1. Environment Maker role removed from "All Users" group per environment
2. Authorized security groups (`FSI-Agent-Makers-*`) assigned to correct environments
3. "Share with Everyone" tenant setting disabled
4. DLP policy blocks agent publishing connector in default environment
5. Managed Environment sharing limits configured per zone
6. Agent publishing approval workflow active for Zone 2/3

Should follow existing patterns:
- `#Requires` statements for module dependencies
- Comprehensive error handling (v2 security remediation patterns)
- SHA-256 evidence export for compliance
- JSON output for downstream Dataverse ingestion

### Regulatory Driver

- FINRA 4511 (evidence of publishing restrictions)
- SEC 17a-4 (immutable records of control enforcement)
- SOX 302/404 (management attestation, IT controls)
- GLBA 501(b) (access control safeguards)

### Related Controls

- Control 1.1 — Restrict Agent Publishing by Authorization
- Control 2.1 — Managed Environments
- Control 3.7 — PPAC Security Posture
