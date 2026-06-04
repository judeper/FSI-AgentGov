
## 2026-06-04 — #360 CA JSON remediation (PR #389)

- Applied Saul's verifier-confirmed corrected JSON to Policy Examples 1 & 2 in `docs/framework/agent-identity-architecture.md`; downgraded heavy warning admonition to a lighter "Beta Graph API — subject to change" note.
- Three schema fixes: `agentIdRiskLevels` (flag-enum STRING, not array/nested object); agent-identity targeting on `conditionalAccessClientApplications` not `users`; `applicationFilter` (sibling, with mode) not `excludeApplications.attributeFilter`.
- Validations: `mkdocs build --strict` ✅ (0/0), `verify_controls.py` ✅, `verify_language_rules.py` ✅.
- Account discipline: switched judep_microsoft → judeper for push/PR via REST POST /pulls (gh pr create not attempted; REST has been more reliable here), restored EMU after.
- Linus locked out per charter; lead authored fix directly.
- PR left open for maintainer (judep) to merge.

## 2026-06-04 — PR #389 merged, #360 closed
- Squashed PR #389 (Conditional Access verified JSON) into main.
- Merge SHA: 36e2b7f96d5a08264ca3bc89305a90d9169ce105
- Issue #360 auto-closed via 'Closes #360' trailer at 20:08:23Z.
- All 11 required checks green pre-merge. Non-required 'Microsoft Learn URL health' failed (out of scope, ignored).
- Account flow: switched judep_microsoft → judeper, verified, merged, restored judep_microsoft.

## 2026-06-04T16:18 — Merged PR #390 (escalation re-verify batch)

- Squash-merge SHA: fc94872db
- Required checks: all green (mkdocs-strict, e2e-smoke, CodeQL, ruff, pytest, gitleaks, dependency-review, control-consistency, manifest drift, FSI language, regulatory naming, prose-counts, Learn URL count drift, markdown-link-check, version stamps, Analyze py/js)
- Non-required `Microsoft Learn URL health` failed — ignored per charter
- Auto-closed: #365, #370, #372, #373 (via Closes trailers)
- main HEAD verified: fc94872db on origin/main
- Account restored to judep_microsoft (EMU) for Copilot CLI license
