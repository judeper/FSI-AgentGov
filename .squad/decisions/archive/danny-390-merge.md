# Decision: Merge PR #390 — escalation re-verify batch (#365 #370 #372 #373)

**Date:** 2026-06-04T16:18-04:00
**Lead:** Danny
**Requested by:** judep (maintainer) — "merge and close out all pending ones"

## Outcome: MERGED ✅

- **PR:** judeper/FSI-AgentGov#390 (`fix/escalation-reverify-batch-365-370-372-373`)
- **Merge method:** squash
- **Merge SHA:** `fc94872db` (full: `fc94872dbe43ddb5c1910e1407ec46d955398224`)
- **Merged at:** 2026-06-04T20:17:57Z
- **Head commit pre-merge:** `1b832465740bba5cde676464bfbd91810d43f4e9`

## Required checks (all green at merge time)

CodeQL ✅, mkdocs-strict ✅, e2e-smoke ✅, e2e-full (skipped, allowed) ✅,
regulatory naming (OCC/SR canonical) ✅, verify_version_stamps ✅, gitleaks ✅,
markdown-link-check ✅, manifest/index/nav drift ✅, prose-counts drift ✅,
Microsoft Learn URL count drift ✅, FSI language rules ✅,
pytest (assessment + scripts) ✅, ruff ✅, control-consistency ✅,
Analyze (javascript) ✅, Analyze (python) ✅, dependency-review ✅

**Non-required failure (ignored):** `Microsoft Learn URL health` — flake, not a required gate.

## Auto-closed issues (via `Closes` trailers)

- #365 → closed ✅
- #370 → closed ✅
- #372 → closed ✅
- #373 → closed ✅

No manual REST PATCH needed.

## Post-merge verification

- `git fetch origin main` → HEAD = `fc94872db` ✅
- Merge commit visible on `origin/main` (top of log)
- GitHub account restored to `judep_microsoft` (EMU) so Copilot CLI license stays active ✅

## Notes

- Account verified as `judeper` immediately before the merge write (no mid-session flip).
- `gh pr merge` succeeded directly; no EMU-Unauthorized fallback to REST PUT needed.
