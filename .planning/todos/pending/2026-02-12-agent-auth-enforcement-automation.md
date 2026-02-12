# Todo: Agent-Level Authentication Enforcement Automation

**Created:** 2026-02-12
**Source:** v16 research — Control 1.1 gap analysis
**Priority:** high

## Description

Automate detection of per-agent authentication configuration violations. Control 1.1 defines 6 SSPM verification criteria (SSPM-1.1-01 through SSPM-1.1-06) for agent-level auth settings, but all are currently classified as "Manual Attestation" in the hardening baseline with no scripted automation.

### Gaps

| SSPM Check | What It Validates | Current State |
|---|---|---|
| SSPM-1.1-01 | Agent authentication mode is not "No Authentication" | Manual attestation only |
| SSPM-1.1-02 | Manual auth requires sign-in | Manual attestation only |
| SSPM-1.1-03 | Authentication enforcement timing set to "Always" | Manual attestation only |
| SSPM-1.1-04 | Sharing scope is not "Anyone" | Manual attestation only |
| SSPM-1.1-05 | AI feature publishing tenant toggle disabled (Zone 2/3) | Manual attestation only |
| SSPM-1.1-06 | Unapproved agent blocking enabled | Manual attestation only |

### What Already Exists

- Control 1.1 documents all 11 verification criteria, but only 3 are automated (Environment Maker role, authorized group, Share with Everyone)
- Hardening Baseline items 1-6 correspond to these SSPM checks — classified as manual
- `scripts/governance/README.md` lists `restrict-agent-publishing.ps1` as planned but the file does not exist

### What Needs to Be Built

- PowerShell automation using Copilot Studio Bot Metadata API / PPAC REST endpoints to read per-agent auth configuration
- Zone-based validation logic (Zone 1 permissive, Zone 2/3 enforce "Always" auth)
- Drift detection for agents that change auth settings after initial approval
- Integration with existing hardening baseline check pattern (`Invoke-HardeningBaselineCheck.ps1`)

### Regulatory Driver

- FINRA 4511 (record retention of agent configuration state)
- SEC 17a-3/4 (audit trail for authentication changes)
- GLBA 501(b) (access control safeguards)
- SOX 302 (management attestation of controls)

### Related Controls

- Control 1.1 — Restrict Agent Publishing by Authorization
- Control 3.7 — PPAC Security Posture (connected agent access)
- Control 2.8 — Access Control and Segregation of Duties
