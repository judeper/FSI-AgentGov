# Codebase Analysis: Quality Assurance

**Generated:** 2026-02-11
**Scope:** Full repository quality analysis

## Summary

The repository has a solid multi-layered quality validation pipeline comprising five Python scripts, a CI build gate, and documented language/template rules. All 62 controls pass structural validation and anchor checks, and mkdocs build --strict succeeds. However, no script enforces FSI language rules programmatically, and verify_controls.py is not run in CI.

## Current Build Status

| Check | Status | Notes |
|-------|--------|-------|
| mkdocs build --strict | PASS | 5 informational warnings about links to excluded files |
| verify_controls.py | PASS | 62/62 controls pass structure + footer validation |
| Anchor validation | PASS | No broken fragment links |
| Control index consistency | PASS | 62 controls in index, 62 files in pillars |
| Legacy marker check | PASS | No stale Last Updated or Version: 2.0 markers |

## Validation Scripts

| Script | What It Checks |
|--------|---------------|
| verify_controls.py | 10-section structure, title format, metadata fields, footer (version/date), anchor validation |
| verify_templates.py | Excel checklist existence (6 files), template 10-section structure, downloads index |
| verify_excel_templates.py | Control counts per template, stale content detection (v1.0, old counts, legacy paths) |
| validate_docs_anchors.py | Internal #fragment links across all docs |
| validate_before_push.py | Runs mkdocs build --strict + verify_controls.py + optional external link check |

## Template Drift

- Template uses `## Implementation Guides` but all 62 controls use `## Implementation Playbooks`
- verify_templates.py checks for Version: v1.1 and Updated: January 2026 (both stale)
- Template file needs sync with actual control conventions

## Language Rule Enforcement

- Prohibited: "ensures compliance", "guarantees", "will prevent", "eliminates risk"
- Required: "supports compliance with", "helps meet", "required for"
- **Enforcement: NONE automated** - relies on authoring discipline only
- Current compliance: zero prohibited phrases found in controls (clean)

## Gaps in Quality Coverage

| Gap | Severity |
|-----|----------|
| No automated language rule enforcement | HIGH |
| verify_controls.py not in CI pipeline | MEDIUM |
| Template file drift (Implementation Guides vs Playbooks) | MEDIUM |
| No playbook existence validation (248 files) | MEDIUM |
| No automated role name validation | MEDIUM |
| No cross-reference bidirectional consistency check | LOW |
| Excel dashboard expected count 61 not 62 | LOW |
| External link validation is sample-only | LOW |
| exclude_docs link warnings (5 docs) | LOW |

## Recommendations

1. Create scripts/verify_language_rules.py - grep for prohibited phrases, fail if found
2. Add verify_controls.py to CI publish_docs.yml workflow
3. Sync control-setup-template.md with actual controls (Implementation Playbooks, current version)
4. Add playbook existence validation (verify all 4 files per control exist)
5. Add role name validation against role-catalog.md canonical names
6. Fix exclude_docs link warnings (add to nav or update linking docs)
7. Correct Excel dashboard expected count (61 -> 62)
