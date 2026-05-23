# Rusty — FSI-AgentGov Override

> Thin override for FSI-AgentGov. Full charter in `judeper/OceanSquad/.squad/agents/rusty/charter.md`.

## Repo-Specific Instructions
- Read `.squad/skills/repo-context.md` for repo structure
- This repo uses Python (ruff, pytest) and PowerShell (PSScriptAnalyzer)
- All Python code must pass `ruff check` and `pytest`
- All PowerShell must pass PSScriptAnalyzer with `PSScriptAnalyzerSettings.psd1`

## What I Can Edit
- `scripts/` — Python validation scripts, hooks
- `assessment/` — Assessment engine (Python collectors, scoring)
- `.github/workflows/` — CI/CD pipelines
- `pyproject.toml` — Python config
- `package.json` — Node.js config (for Playwright/Vitest)
- `.config/wt.toml` — Worktrunk config

## What I Must NOT Edit
- `docs/controls/**/*.md` — content (linus's domain)
- `docs/playbooks/**/*.md` — playbooks (linus's domain)
- `mkdocs.yml` — site config (review-tier, needs human approval)

## Validation After Changes
```bash
ruff check .
pytest
python scripts/verify_controls.py
python scripts/verify_version_stamps.py
```
