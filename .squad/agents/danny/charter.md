# Danny — FSI-AgentGov Override

> Thin override for FSI-AgentGov. Full charter in `judeper/OceanSquad/.squad/agents/danny/charter.md`.

## Repo-Specific Routing Context
- This repo has 78 controls across 4 pillars with strict language rules
- Typo/link fixes → linus (LOW tier, auto-merge eligible)
- Control content edits → linus (REVIEW tier)
- Validation script changes → rusty
- `mkdocs build --strict` failures or QA tasks → saul
- Framework-level changes (new controls, pillar restructuring) → escalate to human

## Triage Hints
- Issues mentioning specific control IDs (e.g., "1.7", "2.14") are content work → linus
- Issues mentioning CI, workflows, scripts → rusty
- Issues mentioning broken links, build failures, verification → saul
