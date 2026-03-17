---
applyTo: "docs/**,mkdocs.yml"
---

# Build Validation Requirements

After making changes to documentation files or site configuration, run these validations before considering work complete.

## Mandatory Validation

```bash
mkdocs build --strict
```

This must produce **zero errors and zero warnings**. Common failures:
- Broken internal links (wrong path or filename)
- Missing nav entries in `mkdocs.yml`
- Unmatched bracket syntax in markdown
- References to non-existent files

## Conditional Validations

### After Control File Changes

```bash
python scripts/verify_controls.py
```

Validates all 72 controls have required 10-section structure.

### After Excel Template Changes

```bash
python scripts/verify_excel_templates.py
```

### After Pillar Control Changes

```bash
python scripts/compile_researcher_package.py
```

Regenerates the researcher package with updated control metadata.

## What "Pass" Means

- `mkdocs build --strict` produces zero errors/warnings
- `verify_controls.py` reports all 72 controls valid
- No broken internal links
- Navigation in `mkdocs.yml` matches actual file structure
