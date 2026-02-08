---
applyTo: ".planning/**"
---

# Checkpoint and Save Conventions

## When to Create Checkpoints

Create a checkpoint (git commit) after:
- Completing a plan task
- Making a significant decision
- Reaching a stable intermediate state
- Before attempting a risky operation

## Checkpoint Format

```bash
git add <specific-files>
git commit -m "checkpoint: <brief description of stable state>"
```

## Save Points in Plans

Plans may include explicit save points marked with:
```markdown
**CHECKPOINT:** Commit current state before proceeding
```

When you encounter a checkpoint marker:
1. Stage all files modified since last commit
2. Commit with descriptive message
3. Verify the commit succeeded
4. Continue to next task

## Recovery

If an operation fails after a checkpoint:
1. Check `git log` for the last checkpoint commit
2. Assess whether to fix forward or reset to checkpoint
3. Prefer fixing forward when possible
4. Only reset if the current state is unrecoverable

## Self-Check

After completing a plan, verify all expected files exist and all commits are present. Record results in the SUMMARY.md:

```markdown
## Self-Check
- [ ] All files in manifest exist
- [ ] All commits present
- [ ] Build passes (`mkdocs build --strict`)
```
