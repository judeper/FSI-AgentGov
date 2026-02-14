---
name: "repo-health-check-scripts"
description: "[1/3] Run automated validation scripts — fast pre-flight check (run after every change session)"
tools: ["execute"]
---

<objective>
Run all existing validation scripts and report pass/fail. This is the fastest health check — run it after every change session. Keep output to a compact summary table.
</objective>

<instructions>

## Output Rules

- Report ONLY a pass/fail table + failure details
- Do NOT show successful command output
- Do NOT explain what each script does
- Keep total output under 30 lines

## Scripts to Run

Run each script from the repository root. Report PASS (zero errors/warnings) or FAIL:

1. `mkdocs build --strict`
2. `python scripts/verify_controls.py`
3. `python scripts/verify_templates.py`
4. `python scripts/verify_excel_templates.py`
5. `python scripts/verify_language_rules.py`
6. `python scripts/validate_docs_anchors.py`

**Solutions repo (if sibling directory FSI-AgentGov-Solutions exists):**

7. Parse every `.json` file under `FSI-AgentGov-Solutions/*/src/` with Python `json.loads()` — report only files that fail to parse

## Output Format

```
# Script Validation Report
**Date:** {date}

| # | Script | Result |
|---|--------|--------|
| 1 | mkdocs build --strict | PASS/FAIL |
| 2 | verify_controls.py | PASS/FAIL |
| 3 | verify_templates.py | PASS/FAIL |
| 4 | verify_excel_templates.py | PASS/FAIL |
| 5 | verify_language_rules.py | PASS/FAIL |
| 6 | validate_docs_anchors.py | PASS/FAIL |
| 7 | Solutions JSON validity | PASS/FAIL/SKIP |

## Failures
[Show error output ONLY for scripts that failed. If all pass, write "All scripts passed."]
```

</instructions>
