---
phase: 01-powershell-core
plan: 01
subsystem: session-controls
tags: [powershell, graph-api, conditional-access, authentication-contexts, session-security]

# Dependency graph
requires:
  - phase: 01-powershell-core
    provides: Research completed for Graph SDK patterns and session controls
provides:
  - Solution scaffold with 3 private helper functions
  - 5 authentication context definitions (c1-c5)
  - 3 zone-specific CA policy templates with session controls
  - 3 zone baseline definitions for validation
affects: [01-02, 01-03, 01-04]

# Tech tracking
tech-stack:
  added: [Microsoft.Graph.Identity.SignIns v2.35.1, Microsoft.Graph.Authentication v2.35.1]
  patterns: [orchestrator-private-helpers, idempotent-deployment, structured-validation-results]

key-files:
  created:
    - session-security-configurator/scripts/private/Connect-GraphSession.ps1
    - session-security-configurator/scripts/private/Test-BreakGlassExclusion.ps1
    - session-security-configurator/scripts/private/Compare-SessionBaseline.ps1
    - session-security-configurator/templates/auth-contexts/auth-contexts-c1-c5.json
    - session-security-configurator/templates/step-up/zone1-step-up-policy.json
    - session-security-configurator/templates/step-up/zone2-step-up-policy.json
    - session-security-configurator/templates/step-up/zone3-step-up-policy.json
    - session-security-configurator/templates/session-baselines/zone1-baseline.json
    - session-security-configurator/templates/session-baselines/zone2-baseline.json
    - session-security-configurator/templates/session-baselines/zone3-baseline.json
    - session-security-configurator/CHANGELOG.md
  modified: []

key-decisions:
  - "Follow ACV/CAA pattern: Connect-GraphSession handles auth with tenant reuse check"
  - "Test-BreakGlassExclusion validates both direct user and group membership exclusions"
  - "Compare-SessionBaseline normalizes signInFrequency to minutes for consistent comparison"
  - "All step-up policies default to report-only mode (enabledForReportingButNotEnforced)"
  - "Zone 1: 8h / standard MFA, Zone 2: 4h / passwordless, Zone 3: 1h / phishing-resistant + compliant device"

patterns-established:
  - "Private helpers pattern: Shared logic in scripts/private/, dot-sourced by orchestrators"
  - "Placeholder ID pattern: Templates use <zone-N-users-group-id> for tenant-specific values"
  - "Break-glass safety check: Mandatory validation before every CA policy deployment"
  - "Baseline normalization: Session controls compared in normalized units (minutes not hours)"

# Metrics
duration: 4min
completed: 2026-02-07
---

# Phase 1 Plan 1: Solution Scaffold Summary

**Session Security Configurator solution scaffold with 3 private helpers and 7 JSON templates for zone-specific session controls**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-07T00:52:15Z
- **Completed:** 2026-02-07T00:56:57Z
- **Tasks:** 2
- **Files modified:** 11

## Accomplishments
- Private helper scripts follow established ACV/CAA patterns for auth, validation, and baseline comparison
- Authentication context definitions (c1-c5) for FSI-AgentGov zones plus PIM and emergency access
- Step-up policy templates with zone-appropriate session controls (8h/4h/1h sign-in frequency)
- Session baseline definitions enable automated compliance validation
- All policies default to report-only state for safe deployment

## Task Commits

Each task was committed atomically:

1. **Task 1: Create solution directory scaffold, private helpers, and CHANGELOG** - `d5423d5` (chore)
2. **Task 2: Create all JSON templates (auth contexts, step-up policies, session baselines)** - `a93d49b` (feat)

## Files Created/Modified

**Private Helpers:**
- `session-security-configurator/scripts/private/Connect-GraphSession.ps1` - Graph authentication with tenant context reuse
- `session-security-configurator/scripts/private/Test-BreakGlassExclusion.ps1` - Break-glass account exclusion validation (direct + group membership)
- `session-security-configurator/scripts/private/Compare-SessionBaseline.ps1` - Zone baseline comparison with signInFrequency normalization

**Templates:**
- `session-security-configurator/templates/auth-contexts/auth-contexts-c1-c5.json` - 5 authentication contexts for zones
- `session-security-configurator/templates/step-up/zone1-step-up-policy.json` - Zone 1: 8h sign-in, standard MFA
- `session-security-configurator/templates/step-up/zone2-step-up-policy.json` - Zone 2: 4h sign-in, passwordless MFA
- `session-security-configurator/templates/step-up/zone3-step-up-policy.json` - Zone 3: 1h sign-in, phishing-resistant MFA, compliant device
- `session-security-configurator/templates/session-baselines/zone1-baseline.json` - 480min baseline validation
- `session-security-configurator/templates/session-baselines/zone2-baseline.json` - 240min baseline validation
- `session-security-configurator/templates/session-baselines/zone3-baseline.json` - 60min baseline validation

**Metadata:**
- `session-security-configurator/CHANGELOG.md` - Version tracking initialized

## Decisions Made

1. **Pattern alignment:** All helper scripts follow existing ACV/CAA solution patterns for consistency
   - Parameter splatting for auth credentials
   - Color-coded output (Cyan banners, Green/Yellow/Red status)
   - Structured result objects with Status/Confidence/Reason

2. **Break-glass validation:** Test-BreakGlassExclusion checks both direct excludeUsers and excludeGroups membership
   - Prevents tenant lockout by ensuring all break-glass accounts are excluded before deployment
   - DryRun parameter supports template validation without Graph API calls

3. **Baseline normalization:** Compare-SessionBaseline normalizes signInFrequency to minutes
   - Handles hours (8h = 480min), minutes, and days
   - Enables consistent comparison regardless of unit used in policy

4. **Report-only default:** All step-up policy templates use `state: "enabledForReportingButNotEnforced"`
   - Aligns with Microsoft best practice for safe CA policy deployment
   - Prevents production impact before 72-hour bake period

5. **Zone-appropriate session controls:**
   - Zone 1: 8h sign-in, standard MFA (any method), no compliant device
   - Zone 2: 4h sign-in, passwordless MFA, no compliant device
   - Zone 3: 1h sign-in, phishing-resistant MFA, compliant device required

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - scaffold creation and template generation completed without issues.

## User Setup Required

None - no external service configuration required. Templates use placeholder IDs for tenant-specific values.

## Next Phase Readiness

**Ready for Phase 1 Plan 2 (Deploy-AuthContexts.ps1):**
- Private helpers available for dot-sourcing
- auth-contexts-c1-c5.json template ready for deployment
- Test-BreakGlassExclusion ready for safety validation

**Ready for Phase 1 Plan 3 (Deploy-StepUpPolicies.ps1):**
- Step-up policy templates for all 3 zones
- Connect-GraphSession handles authentication
- Test-BreakGlassExclusion validates safety before deployment

**Ready for Phase 1 Plan 4 (Test-SessionCompliance.ps1):**
- Compare-SessionBaseline normalizes and compares policy vs baseline
- Session baseline templates define expected zone configurations

**No blockers or concerns.**

## Self-Check: PASSED

All created files verified to exist.
All commits verified in git history.

---
*Phase: 01-powershell-core*
*Completed: 2026-02-07*
