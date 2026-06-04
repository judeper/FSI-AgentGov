
## 2026-06-04 — #364 FINRA RN 25-07 reframing (PR #393)

- Implemented Option 1 (maintainer-selected): reframed FINRA RN 25-07 from "target regulation" / "not AI governance" to "monitored RFC touching AI-generated communications recordkeeping (Section E.3)."
- Scorched-earth enumeration: 2 class (a) mischaracterizations fixed, 13 class (b) contradictions fixed, ~70+ class (c) neutral citations left as-is.
- 15 files changed. All validations green (mkdocs strict, verify_controls, verify_language_rules).
- Decision file: `.squad/decisions/inbox/danny-364-reconciliation.md`

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

## 2026-06-04T16:30 — PR #391 merge ABORTED
- Switched to judeper, verified account.
- gh pr diff 391 --name-only returned 15 paths: 11 under .squad/ AND 4 under docs/controls/ (1.15, 3.7, 3.9, 3.13).
- Per task guard ('every changed path MUST start with .squad/'), STOPPED before merge — branch reuse leaked already-merged doc changes back into the PR.
- No merge performed. Branch not deleted. Restored EMU account (judep_microsoft).
- Recommend: Scribe rebase #391 onto origin/main to drop the stale doc commits, then re-request merge.

## 2026-06-04 — Merged PR #392 (Class B) and #391 (squad memory)

- **PR #392** squash-merged at `84228b6f425665b0cdf4d7ba801b5ed63a2c2621` (branch deleted). Auto-closed #363, #371. #381 intentionally left open (partial).
- **PR #391** required rebase onto main (branch was BEHIND; protection requires up-to-date). Clean rebase, no conflicts. Re-pushed via tokenized URL with explicit `--force-with-lease` value. Squash-merged at `4116323d74633f26b8d08876b9446e067600cfda` (branch deleted).
- All required CI gates green on both merges (Microsoft Learn URL health failure ignored — non-required).
- Account restored to `judep_microsoft` (EMU) for Copilot CLI license.
