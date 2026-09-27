---
name: "repo-clean-state"
description: "Classify and remove stale worktrees, branches, queues, and disposable residue while preserving approved local assets"
tools: ["read", "search", "execute"]
---

<objective>
Leave FSI-AgentGov in a minimal, verified steady state. Classify every candidate
before deletion, preserve approved ignored assets, resolve GitHub queues through
their normal workflows, and finish with a read-back that proves the invariant.
</objective>

<instructions>

## Safety boundary

**Classify before delete.** A path or ref is removable only after its owner,
reachability, PR/issue relationship, and unique work are known.

Preserve by default:

- `.mcp.json`
- `.venv/`
- `node_modules/`
- `maintainers-local/`
- `assessment/output/`

These paths may contain local configuration, dependencies, tenant evidence, or
customer assessment output. Inspect metadata only unless the task explicitly
requires content access.

Preview ignored candidates with `git clean -ndX`. Also inspect
`git status --short --untracked-files=all`: `.mcp.json` can be excluded locally
instead of through the repository `.gitignore`, so an ignored-only preview may
not display it on every machine. Remove named paths directly. Do not use broad
ignored-file cleanup.

## 1. Establish the baseline

From the primary checkout:

```powershell
git fetch origin --prune
git status --short --branch
git worktree list --porcelain
git branch --format='%(refname:short)'
git branch -r --format='%(refname:short)'
```

Also inventory:

- open PRs and issues;
- unread repository notifications;
- in-progress or action-required workflow runs;
- local and remote branch-to-PR relationships;
- ignored/untracked candidates.

If `main` is clean but behind, fast-forward it before classification.

**Complete when:** every candidate worktree, branch, queue item, and ignored path
has an explicit disposition.

## 2. Resolve GitHub work

- Merge valid changes only through protected PRs and required checks.
- Close obsolete or superseded requests with a traceable reason.
- Keep a branch while its PR is open.
- Before branch deletion, read the branch-deletion/reopen hazard in `AGENTS.md`;
  deleting an open PR branch can permanently prevent that PR from reopening.
- Cancel only runs proven redundant, superseded, or intentionally abandoned.
- Use `judeper` for writes, verify with `gh api user -q '.login'`, and read back
  each write.

**Complete when:** no unexplained PR, issue, notification, review request, or
action-required run remains.

## 3. Reconcile worktrees and branches

For every non-primary worktree and non-main branch:

1. Inspect status and unique commits.
2. Check PR/issue history and remote reachability.
3. Preserve required work through a merged PR.
4. Remove the worktree.
5. Delete its local branch.
6. Delete its remote branch only after the PR is merged or intentionally closed.

Then run:

```powershell
git worktree prune
git fetch origin --prune
```

Long-lived remote branches are `main` and `gh-pages`. Any additional branch must
have an active, explained owner.

**Complete when:** the branch/worktree inventory exactly matches the intended
steady state.

## 4. Remove disposable residue

Remove only classified generated artifacts, such as:

- `.pytest_cache/`;
- `__pycache__/`;
- generated `site/` after validation consumers finish;
- named temporary reports or broken-link JSON created by the current task.

Re-run `git clean -ndX` and confirm every remaining ignored path is intentionally
preserved.

**Complete when:** no disposable path remains and the preserve list is intact.

## 5. Validate and read back

Run applicable repository gates for any tracked changes. Then verify:

```powershell
git status --short --branch
git worktree list
git branch --format='%(refname:short)'
git branch -r --format='%(refname:short)'
```

Read back GitHub queues and workflow state. Restore `judep_microsoft`.

## Completion invariant

Report completion only when all are true:

- primary worktree is clean and synchronized with `origin/main`;
- one local branch, `main`;
- remote branches are `main` and `gh-pages`, unless an additional branch has an
  active, explained PR or workflow;
- no disposable task worktree remains;
- no unexplained PR, issue, notification, or action-required workflow remains;
- approved ignored assets remain and disposable residue is gone;
- every GitHub write was read back;
- `judep_microsoft` is active.

Output a concise ledger: deleted refs, removed residue, merged/closed requests,
preserved local assets, validation results, and any explicit exception.

</instructions>
