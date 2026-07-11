---
name: "repo-health-check-scripts"
description: "[1/3] Run CI-aligned validation gates — fast pre-flight check (run after every change session)"
tools: ["execute"]
---

<objective>
Run a CI-aligned Phase 1 validation sweep. Derive commands from `.github/workflows/python-quality.yml`, `.github/workflows/docs-validation.yml`, and `.github/workflows/commercial-scope.yml`, then execute only applicable gates in the correct order.
</objective>

<instructions>

## Output Rules

- Report ONLY a dynamic pass/fail table + failure details
- Do NOT show successful command output
- Do NOT explain what each script does
- Keep total output under 40 lines

## Phase 1 Command Source and Ordering

1. Read command sources:
   - `.github/workflows/docs-validation.yml`
   - `.github/workflows/python-quality.yml`
   - `.github/workflows/commercial-scope.yml`
2. Determine changed paths from the current working diff (`git diff --name-only`) and use them to decide which conditional gates apply.
3. Build the execution plan from workflow-defined gates (do not use a fixed hardcoded script list).
4. Enforce site-dependent ordering:
   1. `mkdocs build --strict`
   2. `python scripts/verify_build_output.py site`
   3. `python scripts/verify_meta_tags.py site/`
   4. `python scripts/verify_doc_links.py site --json _broken-links.json` *(internal built-site paths; does not validate fragment anchors)*
5. Run authoritative anchor validation:
   - `python scripts/validate_docs_anchors.py`
6. Run current documentation/drift gates when applicable to changed paths:
   - `python scripts/verify_controls.py`
   - `python scripts/verify_xref_graph.py`
   - `python scripts/check_manifest_doc_drift.py --check`
   - `python scripts/check_explorer_data_drift.py --check`
   - `python scripts/check_change_radar_data_drift.py --check`
   - `python scripts/check_faq_jsonld_drift.py --check`
   - `python scripts/check_playwright_pin_drift.py --check`
   - `python scripts/generate_coverage_matrix.py --check`
   - `python scripts/generate_pattern_coverage.py --solutions-repo <path> --check` *(only when companion repo is available, or when clone behavior is explicitly requested)*
   - `python scripts/verify_language_rules.py`
   - `python scripts/verify_commercial_scope.py`
   - `python scripts/verify_learn_urls_count.py --check`
   - `python scripts/verify_learn_url_health.py` *(networked: run only when network access is available/allowed in CI)*
   - `python scripts/verify_version_stamps.py --check`
   - `python scripts/verify_prose_counts.py --check`
   - `python scripts/verify_solutions_docs.py --check`
   - `python scripts/verify_regulatory_naming.py --check`
7. Run code/test gates conditionally on relevant changes:
   - `ruff check assessment scripts`
   - `pytest assessment/tests -v`
   - `pytest scripts -v -p no:cacheprovider --ignore=scripts/private --ignore=scripts/governance -k "test_"`
8. Keep these supplemental checks conditional and explicitly label them as non-authoritative CI supplements:
   - `python scripts/verify_templates.py`
   - `python scripts/verify_excel_templates.py`
   - `python scripts/compile_researcher_package.py`
9. If sibling `FSI-AgentGov-Solutions` exists, conditionally parse `*/src/*.json` with `json.loads()` and report parse failures only.

## Dynamic Output Format

```
# Script Validation Report
**Date:** {date}

| Source Workflow | Gate | Command | Condition | Result |
|-----------------|------|---------|-----------|--------|
| docs-validation.yml | mkdocs-strict | mkdocs build --strict | always | PASS/FAIL |
| ... | ... | ... | ... | ... |

## Failures
[Error output only for FAIL rows. If none: "All applicable gates passed."]
```

Use `SKIP` with a short reason when a conditional gate does not apply.

</instructions>
