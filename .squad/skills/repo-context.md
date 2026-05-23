# FSI-AgentGov — Repo Context for OceanSquad Agents

## Overview
- **Repo:** `judeper/FSI-AgentGov` (public, GitHub Pages)
- **Site:** https://judeper.github.io/FSI-AgentGov/
- **Framework:** FSI Agent Governance Framework — 78 controls across 4 pillars
- **Current version:** Check `VERSION` file for latest

## Pillars
1. **Security** (controls 1.1–1.30) — DLP, encryption, access control, content moderation
2. **Operational Governance** (controls 2.1–2.26) — environments, change management, testing, compliance
3. **Monitoring & Reporting** (controls 3.1–3.14) — inventory, analytics, incident response, cost tracking
4. **SharePoint Governance** (controls 4.1–4.9) — IAG, access reviews, retention, grounding scope

## Control Document Structure (10 sections)
Every control doc under `docs/controls/` follows a strict 10-section template:
1. Control Statement
2. Why It Matters in FSI
3. Key Risks Addressed
4. Implementation Approaches
5. Microsoft Technology Mapping
6. Regulatory Alignment
7. Implementation Considerations
8. Related Controls
9. Summary
10. Version footer with Last Verified date

## Key Validation Commands
```bash
mkdocs build --strict          # Required CI check (mkdocs-strict)
python scripts/verify_controls.py   # Control structure validation
python scripts/verify_version_stamps.py  # Version drift detection
python scripts/verify_prose_counts.py    # Prose count accuracy
```

## Language Rules (MANDATORY)
See `.github/instructions/fsi-language-rules.instructions.md`. Key rules:
- Never say "ensure" — use "verify", "confirm", "validate"
- Never say "utilize" — use "use"
- Never say "in order to" — use "to"
- Never use "simply" or "just" — remove entirely
- Use present tense, active voice
- Cite specific Microsoft service names, not generic terms

## Playbooks
Each control has 4 playbooks under `docs/playbooks/control-implementations/{id}/`:
- `portal-walkthrough.md` — UI-based steps
- `powershell-setup.md` — Script-based setup
- `verification-testing.md` — Evidence collection
- `troubleshooting.md` — Common issues

## CI Required Checks
PRs must pass: `e2e-smoke` and `mkdocs-strict`

## Worktrees
Use `git worktree` for parallel work. Config in `.config/wt.toml`.
Pre-merge hook runs `mkdocs build --strict` + `verify_controls.py`.
