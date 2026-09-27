---
name: "git-workflow"
description: "FSI-AgentGov protected-main PR, worktree, dual-account, and clean-state handoff workflow"
domain: "version-control"
confidence: "high"
source: "repository-policy"
---

## Repository model

`main` is the protected integration branch. `gh-pages` is the publication branch.
All repository changes use a task branch and pull request targeting `main`.

The installed copy and `.squad/templates/skills/git-workflow/SKILL.md`
regeneration source must remain byte-identical.

## Account boundary

- Keep `judep_microsoft` active while using Copilot CLI.
- For GitHub writes, switch to `judeper` and verify with `gh api user -q '.login'`.
- Batch writes, read back the result, then restore `judep_microsoft`.
- If a `gh` GraphQL write fails after `judeper` is verified, use the documented
  REST fallback in `AGENTS.md`.

## Single-task workflow

1. **Baseline in the primary checkout**
   ```powershell
   git switch main
   git fetch origin --prune
   git status --short --branch
   git pull --ff-only
   ```
   Start only from a clean, synchronized `main`.

2. **Create a task branch in the primary checkout**
   ```powershell
   git switch -c <type>/<kebab-case-slug> origin/main
   ```
   Use an outcome-oriented prefix such as `fix/`, `docs/`, `chore/`, or `feat/`.

3. **Implement and validate**
   - Follow path-scoped `.github/instructions/*.instructions.md`.
   - Run the smallest checks that cover the change, then the required repository
     gates for the touched surfaces.
   - Keep commits reviewable and independently reversible.

4. **Commit and open a PR**
   ```powershell
   git push -u origin <branch>
   gh pr create --base main --head <branch> --title "<type>(<scope>): <outcome>"
   ```
   Include the repository-required Copilot co-author trailer in commits.

5. **Protected merge**
   - Verify the PR head, file set, and complete check list.
   - Update a behind branch before merge; do not bypass strict-base protection.
   - Merge only after required checks pass and the intended outcome is reviewed.

6. **Read back from the primary checkout**
   ```powershell
   git -C <primary-checkout> pull --ff-only
   gh pr view <number> --json state,mergedAt,mergeCommit
   ```

7. **Clean-state handoff**
   - Remove the merged worktree, local task branch, and remote task branch.
   - Run `git worktree prune` and `git fetch origin --prune`.
   - Verify the completion criteria below.

## Parallel worktrees

When parallel work is required, keep `main` in the primary checkout and create
one worktree per concurrently modified branch:

```powershell
git worktree add -b <branch> <worktree-path> origin/main
```

Each modifying agent owns one worktree. Do not switch branches inside another
agent's worktree or edit the same file region concurrently.

After the PR merges:

```powershell
git worktree list
git worktree remove <resolved-worktree-path>
git branch -d <branch>
git push origin --delete <branch>
git worktree prune
```

If Worktrunk is available, the equivalent `git-wt` commands in `AGENTS.md` are
preferred because project hooks copy approved ignored dependencies and run
pre-merge validation.

## Ignored-file boundary

Treat ignored paths by classification, never by blanket deletion.

Preserve unless the user explicitly chooses a deeper cleanup:

- `.mcp.json`
- `.venv/`
- `node_modules/`
- `maintainers-local/`
- `assessment/output/`

Disposable examples include `.pytest_cache/`, `__pycache__/`, generated `site/`,
and explicitly named temporary reports after their consumers finish.

Preview ignored cleanup with `git clean -ndX`. Do not run broad ignored-file
deletion; remove only resolved paths.

## Completion criteria

A repository task is clean only when:

- its PR is resolved;
- its task worktree, local branch, and remote branch are removed;
- the primary worktree is clean and synchronized with `origin/main`;
- `judep_microsoft` is restored.

For repository-wide queue, branch, and ignored-artifact cleanup, invoke
`.github/prompts/repo-clean-state.prompt.md`.
