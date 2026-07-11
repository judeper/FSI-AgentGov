---
applyTo: "docs/**,mkdocs.yml"
---

# Build Validation Requirements

After making documentation or site-configuration changes, run validation from the repository root before considering work complete.

## Mandatory Validation (in this exact order)

```bash
mkdocs build --strict
python scripts/verify_build_output.py site
python scripts/verify_meta_tags.py site/
python scripts/verify_doc_links.py site --json _broken-links.json
```

`site` consumers must never run before `mkdocs build --strict`.

## Current Documentation/Drift Gates (run when affected files changed)

```bash
python scripts/verify_controls.py
python scripts/verify_xref_graph.py
python scripts/check_manifest_doc_drift.py --check
python scripts/check_explorer_data_drift.py --check
python scripts/check_change_radar_data_drift.py --check
python scripts/check_faq_jsonld_drift.py --check
python scripts/generate_coverage_matrix.py --check
python scripts/verify_language_rules.py
python scripts/verify_commercial_scope.py
python scripts/verify_learn_urls_count.py --check
python scripts/verify_version_stamps.py --check
python scripts/verify_prose_counts.py --check
python scripts/verify_solutions_docs.py --check
python scripts/verify_regulatory_naming.py --check
```

## Conditional Supplemental Checks

### After Template Content Changes

```bash
python scripts/verify_templates.py
```

### After Excel Download Template Changes

```bash
python scripts/verify_excel_templates.py
```

### After Pillar Control Changes (researcher package maintenance)

```bash
python scripts/compile_researcher_package.py
```

## What "Pass" Means

- `mkdocs build --strict` completes with zero errors and zero warnings
- Built-site completeness, metadata, and internal-link checks pass against the generated `site/`
- Applicable documentation/drift gates pass for the touched surfaces
- Any required supplemental checks pass when their triggering files changed
