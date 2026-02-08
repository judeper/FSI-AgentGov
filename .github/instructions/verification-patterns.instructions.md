---
applyTo: ".planning/**"
---

# Verification Patterns

Verification confirms that what was built actually achieves the phase goal. It uses goal-backward analysis, not checklist-forward checking.

## Goal-Backward Analysis

1. **Start from the phase goal** (from ROADMAP.md success criteria)
2. **Ask:** "Does the codebase now deliver this?"
3. **Trace backward** from goal to implementation artifacts
4. **Flag gaps** where the goal is not fully met

This is the opposite of "did we complete all the tasks?" — it asks "does the result achieve the intent?"

## Verification Checklist

For every phase verification:

### 1. Goal Achievement
- [ ] Phase goal statement is fully satisfied
- [ ] Success criteria from ROADMAP.md are met
- [ ] No scope creep beyond phase boundaries

### 2. Artifact Completeness
- [ ] All files listed in plan manifests exist
- [ ] All commits listed in summaries are present
- [ ] No orphaned or incomplete files

### 3. Build Validation (FSI-AgentGov Specific)
- [ ] `mkdocs build --strict` passes with zero errors
- [ ] `python scripts/verify_controls.py` passes (if controls were modified)
- [ ] No broken internal links

### 4. Cross-Reference Integrity
- [ ] Related controls correctly reference new content
- [ ] Navigation in `mkdocs.yml` includes new pages
- [ ] CONTROL-INDEX.md is up to date (if controls changed)

### 5. Language Compliance
- [ ] No prohibited phrases ("ensures compliance", "guarantees", etc.)
- [ ] Canonical role names used throughout
- [ ] Regulatory references are specific and accurate

## Verification Output

Write results to `{NN}-VERIFICATION.md`:

```markdown
# Phase {NN} Verification

**Phase:** {name}
**Goal:** {goal from ROADMAP.md}
**Verified:** YYYY-MM-DD
**Result:** PASS / PARTIAL / FAIL

## Goal Achievement
[Analysis of whether the goal was met]

## Gaps Identified
[Any gaps between goal and implementation]

## Build Validation
[Results of mkdocs build and verify_controls]

## Recommendation
[Ship / Fix before ship / Rework needed]
```
