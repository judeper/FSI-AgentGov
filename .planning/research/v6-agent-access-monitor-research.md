# Research: Agent Access Governance Monitor (v6)

**Created:** 2026-02-09
**Milestone:** v6 — Agent Access Governance Monitor
**Status:** Complete

## Overview

The Agent Access Governance Monitor automates detection of unrestricted agent access configurations across Power Platform environments and Microsoft 365. It identifies violations where environment agent access settings do not align with governance zone requirements (e.g., Zone 3 allowing "All agents" instead of "Organizational only").

## Problem Statement

Control 3.8 (Copilot Hub and Governance Dashboard) establishes zone-specific agent access requirements:

| Setting | Zone 1 (Personal) | Zone 2 (Team) | Zone 3 (Enterprise) |
|---------|-------------------|---------------|---------------------|
| Allowed Agent Types | All agents allowed | Organizational + Microsoft verified | Organizational only, approved list |
| Agent Sharing | No restrictions | Managed limits | Editor sharing disabled |
| User Access | All licensed users | All licensed users | Specific user groups only |

**Current gap:** No automated verification that environments comply with their designated zone's access requirements.

## Technical Stack Analysis

### Power Platform APIs (Full Support)

| Capability | API | Status | Notes |
|------------|-----|--------|-------|
| Environment enumeration | `Get-AdminPowerAppEnvironment` | ✅ GA | Returns all environments with governance settings |
| Environment group query | `Get-AdminPowerAppEnvironmentGroup` | ✅ GA | Returns group rules and member environments |
| Governance settings | `governanceConfiguration.settings.extendedSettings` | ✅ GA | Contains bot-* settings for agent controls |
| Zone classification | ELM Dataverse lookup or naming convention | ✅ Custom | ELM solution provides zone metadata |

### Power Platform Agent Settings (Key Detection Points)

| Setting Key | Values | Zone Expectation |
|-------------|--------|------------------|
| `bot-limitSharingMode` | `noLimit`, `ExcludeSharingToSecurityGroups` | Zone 3: Exclude |
| `bot-authoringSharingDisabled` | `true`, `false` | Zone 3: true (ALM enforced) |
| `bot-publishedBotLimitSharingMode` | `noLimit`, `ExcludeSharingToSecurityGroups` | Zone 3: Exclude |

### M365 Admin Center (Portal-Only)

| Capability | API | Status | Notes |
|------------|-----|--------|-------|
| Allowed Agent Types | None | ❌ Portal Only | No Graph or PowerShell API |
| Agent Sharing Settings | None | ❌ Portal Only | Manual baseline required |
| Admin Exclusion Groups | Graph `Get-MgGroup` | ✅ GA | Query `CopilotForM365AdminExclude` group membership |

**Mitigation for Portal-Only Settings:**
1. Capture manual baseline of M365 Admin agent settings
2. Store baseline in Dataverse
3. Detect drift via daily comparison (screenshot + manual validation)
4. Alert on baseline age (flag if >30 days without verification)

### Required Permissions

| Resource | Permission | Type | Purpose |
|----------|------------|------|---------|
| Power Platform | Power Platform Admin | Role | Query all environments |
| Graph | Organization.Read.All | Application | Tenant configuration |
| Graph | Group.Read.All | Application | Admin exclusion groups |
| Graph | AuditLog.Read.All | Application | Setting change events |
| Dataverse | System Administrator | Role | Schema deployment |

### PowerShell Modules

| Module | Version | Purpose |
|--------|---------|---------|
| Microsoft.PowerApps.Administration.PowerShell | 2.0.180+ | Environment/group queries |
| Microsoft.Graph | 2.0+ | Entra ID group queries |

## Architecture Design

### Pattern: Tier 2 (ACV/SSC Proven)

Following the Audit Configuration Validator and Session Security Configurator pattern:

```
Phase 1: PowerShell Core
├── Private helpers (parameter validation, zone lookup, severity classification)
├── Get-EnvironmentAccessSettings.ps1 (query all env agent settings)
├── Compare-ZoneCompliance.ps1 (validate settings vs zone requirements)
└── Test-AgentAccessCompliance.ps1 (orchestrator with dry-run mode)

Phase 2: Dataverse Infrastructure
├── Tables: AccessBaseline, ValidationHistory, Violation
├── Environment variables: fsi_AAM_* (zone thresholds, scan frequency)
├── Connection references: fsi_cr_dataverse, fsi_cr_teams
└── deploy.py (idempotent deployment)

Phase 3: Automation and Alerting
├── Runbook wrapper: Start-AccessValidationRunbook.ps1
├── Baseline capture: Invoke-AccessBaselineCapture.ps1
├── Power Automate flow: access-validation-flow.json
└── Teams adaptive card template

Phase 4: Evidence Export and Framework Integration
├── Export-AgentAccessEvidence.ps1 (SHA-256 evidence)
├── Control 3.8 tip admonition integration
├── solutions-index.md catalog entry
└── Documentation suite (4 docs)
```

### Zone Classification Strategy

**Option A (Recommended): ELM Dataverse Lookup**
- Query ELM `fsi_environment` table for `fsi_zone_classification`
- Environments provisioned via ELM have zone metadata
- Fallback to naming convention if ELM not deployed

**Option B: Naming Convention**
- Parse environment display name for zone indicator
- Pattern: `{org}-{zone}-{purpose}` (e.g., `contoso-z3-trading`)
- Less reliable but works without ELM

**Option C: Manual Assignment**
- Dataverse lookup table with environment GUID → zone mapping
- Requires admin to maintain mapping
- Most flexible but highest maintenance

### Violation Classification

| Violation | Zone 1 | Zone 2 | Zone 3 | Regulatory Impact |
|-----------|--------|--------|--------|-------------------|
| bot-limitSharingMode = noLimit | OK | Warning | CRITICAL | FINRA 4511: uncontrolled tool sharing |
| bot-authoringSharingDisabled = false | OK | OK | HIGH | SOX 404: ALM control bypass |
| All agents allowed | OK | HIGH | CRITICAL | FINRA 4511: unapproved tools |
| Missing zone classification | Warning | Warning | CRITICAL | Ungoverned environment |

### Dataverse Schema

**Table: fsi_accessbaseline**
| Column | Type | Purpose |
|--------|------|---------|
| fsi_environmentid | Lookup(fsi_environment) | ELM environment reference |
| fsi_environment_guid | String | Power Platform environment GUID |
| fsi_zone | OptionSet(fsi_acv_zone) | Zone 1/2/3 |
| fsi_bot_limit_sharing_mode | String | Captured setting |
| fsi_bot_authoring_disabled | Boolean | Captured setting |
| fsi_captured_at | DateTime | Baseline capture timestamp |
| fsi_captured_by | Lookup(SystemUser) | Who captured baseline |
| fsi_is_active | Boolean | Current baseline or historical |

**Table: fsi_accessviolation**
| Column | Type | Purpose |
|--------|------|---------|
| fsi_environment_guid | String | Violating environment |
| fsi_zone | OptionSet(fsi_acv_zone) | Environment zone |
| fsi_violation_type | String | Setting key that violated |
| fsi_expected_value | String | What zone requires |
| fsi_actual_value | String | What was found |
| fsi_severity | OptionSet(fsi_acv_severity) | Low/Medium/High/Critical |
| fsi_detected_at | DateTime | When violation found |
| fsi_resolved_at | DateTime | When remediated (nullable) |

## Risk Analysis

### API Availability Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| M365 agent settings remain portal-only | High | Medium | Manual baseline + drift detection workflow |
| Power Platform API changes | Low | Low | PowerShell module version pinning |
| Graph API throttling | Medium | Low | Batch queries, exponential backoff |
| ELM not deployed at customer | Medium | Medium | Fallback to naming convention |

### False Positive Risks

| Scenario | Risk | Mitigation |
|----------|------|------------|
| Zone 1 flagged for "All agents" | False positive | Zone-aware severity (Zone 1 = Info only) |
| New environment not yet classified | False positive | Grace period (48h) for new environments |
| Sandbox/trial environments | Noise | Exclude non-production environment types |

### Integration Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Option set reuse conflicts | Low | Low | Existence check before creation |
| ELM schema version mismatch | Low | Medium | Version check in deploy.py |
| Connection reference binding failures | Medium | Low | Clear documentation, --refs-only flag |

## Recommended Approach

### Phase Structure (4 Phases, ~12 Plans)

1. **Phase 1: PowerShell Core** (3 plans)
   - Standalone scripts that work without Dataverse
   - Operator can run manual validation immediately
   - Dry-run mode for safe preview

2. **Phase 2: Dataverse Infrastructure** (3 plans)
   - Persistent state for baselines and violations
   - Reuse ACV option sets (fsi_acv_zone, fsi_acv_severity)
   - Environment variables for zone thresholds

3. **Phase 3: Automation and Alerting** (3 plans)
   - Daily scheduled validation
   - Teams alerts for violations
   - Immutable validation history

4. **Phase 4: Evidence Export and Framework Integration** (3 plans)
   - SHA-256 compliance evidence
   - Control 3.8 tip admonition
   - Documentation suite

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Focus on Power Platform settings first | Full API support; M365 settings are portal-only |
| Reuse ACV option sets | Cross-solution consistency |
| Zone lookup via ELM with fallback | Leverages existing ELM investment |
| Detect-only for Zone 3 | No auto-remediation; SOX change control |
| Grace period for new environments | Avoid false positives during provisioning |
| Severity by zone + setting | Zone 3 violations are always higher severity |

## Related Controls

| Control | Relationship |
|---------|--------------|
| 3.8 | Primary — Agent Access Control settings |
| 1.1 | Publishing authorization (security groups) |
| 1.2 | Agent registry (inventory tracking) |
| 2.1 | Managed Environments (sharing limits) |

## References

- [Power Platform Admin PowerShell](https://learn.microsoft.com/en-us/power-platform/admin/powerapps-powershell)
- [Environment Groups](https://learn.microsoft.com/en-us/power-platform/admin/environment-groups)
- [Agent Sharing Rules](https://learn.microsoft.com/en-us/power-platform/admin/control-user-access#canvas-app-owner-sharing-settings)
- [Control 3.8: Copilot Hub and Governance Dashboard](../../docs/controls/pillar-3-reporting/3.8-copilot-hub-and-governance-dashboard.md)

---
*Research completed: 2026-02-09*
*Confidence: High for Power Platform scope, Medium for M365 scope (API limitations)*
