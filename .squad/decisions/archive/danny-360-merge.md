# Decision: Merge PR #389 / close #360

**Date:** 2026-06-04
**Owner:** Danny (merge-master)
**Requested by:** judep

## Outcome
- PR #389 squash-merged into main.
- Merge SHA: `36e2b7f96d5a08264ca3bc89305a90d9169ce105`
- Issue #360 auto-closed at 2026-06-04T20:08:23Z.

## Pre-merge gate
- All 11 branch-protection required checks: success.
- Non-required `Microsoft Learn URL health`: failure (pre-existing, out of scope).
- mergeStateStatus: UNSTABLE (driven by the non-required failure; ignored per policy).

## Account discipline
- Switched judep_microsoft → judeper for write.
- Re-verified `gh api user` = judeper immediately before merge.
- Restored judep_microsoft as active post-merge to preserve Copilot CLI license.
