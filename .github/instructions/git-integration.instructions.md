---
applyTo: "docs/**"
---

# Git Integration Conventions

## Commit Philosophy

**Commit outcomes, not process.** Commit messages should describe what was achieved, not the steps taken.

```bash
# GOOD - describes the outcome
git commit -m "feat(1.23): add session security configurator deployment scripts"

# BAD - describes the process
git commit -m "wrote some scripts and tested them"
```

## Commit Message Format

```
type(scope): brief description

[Optional body with details]
```

**Types:**
- `feat` — New feature or capability
- `fix` — Bug fix
- `docs` — Documentation only
- `refactor` — Code restructuring without behavior change
- `chore` — Build, tooling, or maintenance

**Scopes (examples):**
- Control IDs: `1.23`, `2.1`, `4.7`
- Phase references: `phase-3`, `03-02`
- Solution names: `elm`, `ssc`, `acv`
- General: `nav`, `build`, `ci`

## Cross-Repository Commits

FSI-AgentGov and FSI-AgentGov-Solutions have separate git histories.

When changes span both repos:
1. Commit FSI-AgentGov-Solutions changes first (implementations)
2. Commit FSI-AgentGov changes second (documentation)
3. Reference the related commit in the message

```bash
# In FSI-AgentGov-Solutions
git commit -m "feat(ssc): add baseline capture script"

# In FSI-AgentGov
git commit -m "docs(1.23): add baseline capture playbook (solutions: abc1234)"
```

## CHANGELOG Format

Major changes should be recorded in `CHANGELOG.md`:

```markdown
## [1.2.53] - YYYY-MM-DD

### Added
- Description of new feature

### Changed
- Description of modification

### Fixed
- Description of bug fix
```

## Version Numbering

- Patch: `1.2.X` — Documentation updates, minor fixes
- Minor: `1.X.0` — New controls, solutions, or significant features
- Major: `X.0.0` — Breaking changes to framework structure

## Logical Commit Grouping

Create one commit per logical unit of work. Group files that deliver the same outcome, split unrelated changes into separate commits, and keep each commit reviewable and independently reversible.
