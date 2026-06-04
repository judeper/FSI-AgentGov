# Danny — Decision: #360 Remediation Applied (PR #389)

**Date:** 2026-06-04
**Author:** Danny (Lead, FSI-AgentGov review squad)
**Status:** Awaiting maintainer merge (judep)

## Decision

Applied Saul's verifier-confirmed corrected JSON (file: `.squad/decisions/inbox/saul-360-graph-reverify.md`) to both Conditional Access policy examples in `docs/framework/agent-identity-architecture.md` verbatim. Replaced the strong "illustrative example — not Graph-API-ready" warning admonition with a lighter "Beta Graph API — subject to change" note linking to the Conditional Access for agents Learn page.

## Corrections (per Saul's verdict)

1. `agentIdRiskLevels`: single flag-enum STRING (`"high"`, multi-select `"medium,high"`) — not an array, not a nested `agentRisk` object.
2. Agent-identity targeting: `conditionalAccessClientApplications.includeAgentIdServicePrincipals` / `excludeAgentIdServicePrincipals` / `agentIdServicePrincipalFilter` (with `"All"` sentinel). `users.includeAgents`/`excludeAgents` deleted (do not exist).
3. `excludeApplications.attributeFilter` deleted; sibling `applicationFilter` (with `mode: include`/`exclude`) used on `applications`.

Both examples now start in `enabledForReportingButNotEnforced` per MS Learn pattern.

## Reviewer lockout

Linus was locked out of this artifact per maintainer instruction (his F-20260603-003 mapping was refuted by the verifier). Lead authored the fix directly. No re-route to Linus occurred.

## Validation (local)

- `mkdocs build --strict`: passed (0 errors, 0 warnings)
- `python scripts/verify_controls.py`: passed
- `python scripts/verify_language_rules.py`: passed

## PR

- Number: #389
- URL: https://github.com/judeper/FSI-AgentGov/pull/389
- Branch: `fix/360-conditional-access-verified-json`
- Title: `fix(framework/agent-identity-architecture): replace fabricated CA JSON with Graph-beta-verified payloads (#360)`
- Body cites Saul's verdict + all 6 MS Learn source URLs, notes beta caveat, `Closes #360`, includes Copilot Co-authored-by trailer.
- **Not self-merged.** Left open for maintainer (judep) to merge.
