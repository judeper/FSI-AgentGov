# Roadmap: Agent Security Configuration Governance (v17)

## Overview

Automate per-agent authentication enforcement, publishing restriction validation, and zone-based access configuration governance — closing the manual attestation gap across Controls 1.1, 3.7, and 3.8. Converts 6 manual-only SSPM checks to automated validation, creates the phantom `restrict-agent-publishing.ps1` governance script, and adds zone-policy compliance verification for agent access settings.

**Source:** Three high-priority pending todos from v16 research addressing automation gaps where agent-level security checks are manual-only.

**Execution model:** 4 phases. Phases 1–3 are independent (parallel-eligible). Phase 4 depends on 1–3. Within each phase, plans target non-overlapping file sets for parallel execution.

## Phases

- [x] **Phase 1: Agent Authentication Enforcement** — PowerShell script validating 6 SSPM items per agent, zone-based logic, drift detection, SHA-256 evidence export
- [x] **Phase 2: Publishing Restriction Governance** — `restrict-agent-publishing.ps1` validating 6 publishing criteria, SHA-256 evidence, hardening baseline integration
- [ ] **Phase 3: Zone Access Validation** — M365 Admin Center agent access settings verification per zone, admin exclusion group validation, drift detection
- [ ] **Phase 4: Framework Integration & Validation** — Controls 1.1/3.7/3.8 updates, solutions-index entry, hardening baseline reclassification, full build validation

## Phase Details

### Phase 1: Agent Authentication Enforcement
**Goal:** Build PowerShell script that reads per-agent authentication configuration via BAP/PPAC REST endpoints and validates 6 SSPM items with zone-based logic and drift detection
**Depends on:** Nothing (independent)
**Requirements:** AUTH-01, AUTH-02, AUTH-03
**Success Criteria:**
  1. `Test-AgentAuthConfiguration.ps1` connects to Power Platform, enumerates agents per environment, retrieves auth mode/enforcement/sharing settings
  2. Validates SSPM-1.1-01 through SSPM-1.1-06 with zone-based logic — Zone 1 permissive (warn only), Zone 2/3 enforce "Always" auth timing, "No Authentication" flagged in all zones, sharing scope "Anyone" flagged in Zone 2/3
  3. Drift detection compares against previous scan baseline with SHA-256 evidence hashing
  4. JSON output structured for Dataverse ingestion with per-check pass/fail, evidence hashes, and timestamps
  5. Follows established conventions: `#Requires -Version 7.0`, `ErrorAction Stop`, `-OutputFormat`/`-OutputPath` parameters
**Plans:** 2 (A = script core + BAP API integration + 6 SSPM checks, B = drift detection + evidence export + JSON output)

### Phase 2: Publishing Restriction Governance
**Goal:** Create the `restrict-agent-publishing.ps1` governance script (currently phantom — listed in README but file does not exist) validating 6 publishing restriction criteria with SHA-256 evidence export
**Depends on:** Nothing (independent)
**Requirements:** PUB-01, PUB-02, PUB-03
**Success Criteria:**
  1. `restrict-agent-publishing.ps1` validates 6 publishing criteria: Environment Maker role removal, authorized security groups, Share with Everyone disabled, DLP connector blocking, Managed Environment sharing limits, approval workflow active (Zone 2/3)
  2. SHA-256 evidence export and structured JSON output with per-check pass/fail, evidence hashes, timestamp; compatible with Dataverse ingestion patterns
  3. Hardening baseline items 1–6 in `Invoke-HardeningBaselineCheck.ps1` reclassified from "Manual Attestation" to "Automated" or "Semi-Automated"; baseline script calls or references the new validation
  4. Follows established conventions: `#Requires -Version 7.0`, `ErrorAction Stop`, standard parameters
**Plans:** 2 (A = script core + 6 publishing criteria validation, B = hardening baseline integration + evidence export)

### Phase 3: Zone Access Validation
**Goal:** Automate M365 Admin Center agent access settings verification per zone policy and admin exclusion group validation
**Depends on:** Nothing (independent)
**Requirements:** ZAV-01, ZAV-02, ZAV-03
**Success Criteria:**
  1. `Test-ZoneAgentAccess.ps1` reads agent access control configuration, compares to zone policy (Zone 1: all agents, Zone 2: Org + MS verified, Zone 3: Org only with approval)
  2. Validates `CopilotForM365AdminExclude` Entra group exists and is populated; validates staged deployment group configuration per zone
  3. Drift detection with structured comparison output suitable for daily scheduling; results compatible with existing alerting patterns (adaptive cards)
  4. Follows established conventions: `#Requires -Version 7.0`, `ErrorAction Stop`, `-OutputFormat`/`-OutputPath` parameters
**Plans:** 2 (A = script core + zone policy validation + admin exclusion groups, B = drift detection + Teams notification support)

### Phase 4: Framework Integration & Validation
**Goal:** Update framework controls, solutions catalog, and hardening baseline to reference new automation scripts; full build validation
**Depends on:** Phases 1–3 (all scripts must exist before documentation references them)
**Requirements:** FRM-01, FRM-02, FRM-03
**Success Criteria:**
  1. Controls 1.1, 3.7, 3.8 updated with tip admonitions linking to new governance scripts; verification criteria updated to reflect automation availability
  2. `solutions-index.md` includes Agent Security Configuration Governance entry with status, components, regulatory alignment, control mappings
  3. Hardening baseline items 1–6 status updated from "Manual Attestation" to "Automated"/"Semi-Automated"
  4. `scripts/governance/README.md` updated to reflect actual script inventory (no phantom references)
  5. `mkdocs build --strict` passes, `verify_controls.py` 62/62, `verify_language_rules.py` 0 violations
**Plans:** 2 (A = control updates + solutions-index + governance README, B = hardening baseline status + build validation)

## Progress

| Phase | Plans Complete | Status |
|-------|---------------|--------|
| 1. Agent Authentication Enforcement | 2/2 | Complete |
| 2. Publishing Restriction Governance | 2/2 | Complete |
| 3. Zone Access Validation | 0/2 | Not Started |
| 4. Framework Integration & Validation | 0/2 | Not Started |

## Parallel Execution Guide

Phases 1–3 are **independent** — no shared file targets, parallel-eligible. Phase 4 depends on 1–3.

```
Phase 1 (AUTH) ──┐
Phase 2 (PUB) ──┼── Phase 4 (FRM)
Phase 3 (ZAV) ──┘
```

Within each phase, plans target non-overlapping file sets:

| Phase | Plan A Files | Plan B Files | Parallel? |
|-------|-------------|-------------|-----------|
| 1 | `scripts/governance/Test-AgentAuthConfiguration.ps1` (core) | Drift detection module, evidence export | Yes |
| 2 | `scripts/governance/restrict-agent-publishing.ps1` (core) | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` (modify), evidence export | Yes |
| 3 | `scripts/governance/Test-ZoneAgentAccess.ps1` (core) | Drift detection, Teams notification support | Yes |
| 4 | `docs/controls/pillar-*`, `docs/reference/solutions-index.md`, `scripts/governance/README.md` | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` (status update), validation (read-only) | Yes |

## File Manifest

### Created (new files)

| Phase | File | Purpose |
|-------|------|---------|
| 1 | `scripts/governance/Test-AgentAuthConfiguration.ps1` | Per-agent auth config validation (6 SSPM items) |
| 2 | `scripts/governance/restrict-agent-publishing.ps1` | Publishing restriction governance (6 criteria) |
| 3 | `scripts/governance/Test-ZoneAgentAccess.ps1` | Zone-based agent access settings verification |

### Modified (existing files)

| Phase | File | Change |
|-------|------|--------|
| 2 | `scripts/governance/Invoke-HardeningBaselineCheck.ps1` | Items 1–6 reclassified, references to new script |
| 4 | `docs/controls/pillar-1-security/1.1-restrict-agent-publishing-by-authorization.md` | Add tip admonition for auth + publishing automation |
| 4 | `docs/controls/pillar-3-reporting/3.7-ppac-security-posture.md` | Add tip admonition for publishing restriction script |
| 4 | `docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md` | Add tip admonition for zone access validation |
| 4 | `docs/reference/solutions-index.md` | Add Agent Security Config Governance entry |
| 4 | `scripts/governance/README.md` | Update script inventory (remove phantom, add actuals) |

## Coverage

| Requirement | Phase | Plan | Description |
|-------------|-------|------|-------------|
| AUTH-01 | 1 | 01-01 | Per-agent auth config read via BAP/PPAC REST |
| AUTH-02 | 1 | 01-01 | 6 SSPM items validated with zone-based logic |
| AUTH-03 | 1 | 01-02 | Drift detection with SHA-256 evidence export |
| PUB-01 | 2 | 02-01 | restrict-agent-publishing.ps1 with 6 criteria |
| PUB-02 | 2 | 02-02 | SHA-256 evidence export and JSON output |
| PUB-03 | 2 | 02-02 | Hardening baseline items 1–6 integration |
| ZAV-01 | 3 | 03-01 | Agent access settings verification per zone |
| ZAV-02 | 3 | 03-01 | Admin exclusion group + deployment group validation |
| ZAV-03 | 3 | 03-02 | Drift detection with Teams notification support |
| FRM-01 | 4 | 04-01 | Controls 1.1, 3.7, 3.8 automation references |
| FRM-02 | 4 | 04-01 | Solutions-index + hardening baseline + governance README |
| FRM-03 | 4 | 04-02 | Full build validation (mkdocs + verify scripts) |
| FRM-01 | 5 | 05-01 | Solutions-index entry |
| FRM-02 | 5 | 05-01 | Control updates + architecture docs |
| FRM-03 | 5 | 05-02 | mkdocs nav + AAM reconciliation |
| VAL-01 | 5 | 05-02 | Build and language validation |

**Total: 16/16 requirements mapped. No orphans.**

---
*Roadmap created: 2026-02-12*
*Depth: comprehensive*
*Phases: 5 (infrastructure → detection → remediation/exceptions → deployment/ops → framework integration)*
