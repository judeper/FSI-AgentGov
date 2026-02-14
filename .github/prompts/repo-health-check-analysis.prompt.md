---
name: "repo-health-check-analysis"
description: "[2/3] Structural integrity and content quality analysis — run before releases"
tools: ["read", "search"]
---

<objective>
Analyze repository structural integrity and content quality through cross-file reasoning that automated scripts cannot perform. Do NOT re-check anything covered by validation scripts (language rules, control section structure, footer format, anchor links). Report issues only, one line per finding.
</objective>

<instructions>

## Output Rules (READ FIRST)

**Preserve context window — be maximally concise:**
- One line per finding: `🔴|🟡|🔵 file:line — description`
- No preamble, no "all clear" messages, no explanations for obvious issues
- Skip any check that finds zero issues — do not mention it
- NEVER echo file contents — just cite path and line number
- Do not exceed 150 lines of output total

**Severity:**
- 🔴 **CRITICAL** — Missing files, broken links, build-breaking issues
- 🟡 **HIGH** — Content quality, stale versions, incorrect terminology
- 🔵 **LOW** — Minor formatting, cosmetic consistency

## What NOT to Check

These are already covered by `repo-health-check-scripts`. Do not duplicate:
- Prohibited language phrases → `verify_language_rules.py`
- Control 10-section structure and footer format → `verify_controls.py`
- Broken anchor links → `validate_docs_anchors.py`
- Template validity → `verify_templates.py`
- Excel template integrity → `verify_excel_templates.py`

## Dynamic Values — Derive, Do Not Hardcode

- **CURRENT_VERSION:** Read from the latest entry in `CHANGELOG.md`
- **CONTROL_LIST:** Read from `docs/controls/CONTROL-INDEX.md` (do not assume a fixed count)
- **SOLUTIONS_REPO:** Look for sibling directory `FSI-AgentGov-Solutions`

---

## Structural Integrity Checks

1. **mkdocs.yml nav integrity:** Verify every file path in `mkdocs.yml` nav actually exists on disk. List broken entries.

2. **Orphaned docs:** Find `.md` files under `docs/` not referenced in `mkdocs.yml` nav. Exclude `docs/templates/`, `docs/images/`, and `index.md` directory index files.

3. **Control cross-references:** In each control's "Related Controls" table, verify linked file paths exist. List broken links only.

4. **Playbook completeness:** For every control in `CONTROL-INDEX.md`, verify 4 playbooks exist: `docs/playbooks/control-implementations/{id}/portal-walkthrough.md`, `powershell-setup.md`, `verification-testing.md`, `troubleshooting.md`. List missing only.

5. **Playbook stub detection:** Verify each playbook contains at least 100 characters and at least one numbered or bulleted step. Flag stubs.

6. **Nav ordering:** Within each pillar section in `mkdocs.yml`, verify controls appear in numerical order. Flag out-of-order entries.

## Content Quality Checks

7. **Placeholder/TODO markers:** Search `docs/**/*.md` for: TODO, FIXME, PLACEHOLDER, TBD, [TBD], [TODO], "your-org", "contoso", `<your-`, `[your-`. List each with file:line.

8. **Version staleness:** Read `CURRENT_VERSION` from `CHANGELOG.md`. Check `docs/reference/*.md` for version numbers older than `CURRENT_VERSION` in their footers. Flag stale files.

9. **CHANGELOG-mkdocs version alignment:** Verify the latest version in `CHANGELOG.md` matches any version reference in `mkdocs.yml` (copyright line or elsewhere).

## Solutions Repo Checks (skip if not available)

**If FSI-AgentGov-Solutions is not found as a sibling directory, skip checks 10-18 and note: "Solutions repo not available — cross-repo checks skipped."**

10. **Solution folder completeness:** Every solution folder must contain `README.md`, `CHANGELOG.md`, and either `src/` or `docs/` with implementation artifacts. List any missing.

11. **CONTROL-INDEX solution coverage:** For every solution in `solutions-index.md`, verify its related controls are linked in `CONTROL-INDEX.md`'s Implementation column. List gaps.

12. **Solutions-index alignment:** Every solution with status "Completed" or "Validated" in `solutions-index.md` must have a matching folder in the Solutions repo. List mismatches.

13. **Solution README completeness:** Each solution `README.md` should contain: a version identifier, a related controls section, a component listing, prerequisites, and deployment instructions. List READMEs missing any.

14. **Component manifest accuracy:** For each solution README listing component files, verify each listed file exists in `src/`. Flag phantom files (listed but missing) and unlisted files (exist but undocumented).

15. **Cross-repo URL validation:** Search solution `.md` and `.json` files for URLs referencing FSI-AgentGov (github.io or github.com paths). Verify targets exist. List broken URLs.

16. **Adaptive card placeholders:** In `adaptive-card-*.json` action URLs, flag placeholder patterns ("your-org", "contoso", "[org]"). Note: placeholders are expected in templates — only flag if undocumented or clearly accidental.

17. **Solution naming consistency:** Verify solution folder names are kebab-case and match anchors in `solutions-index.md`. List mismatches.

18. **Advanced implementation playbook links:** Verify every "Framework Playbook" link in `solutions-index.md` points to an existing file. List broken links.

---

## Output Format

```
# Structural & Content Analysis Report
**Date:** {date}
**Version:** {CURRENT_VERSION}
**Issues:** {total} (🔴 {n} / 🟡 {n} / 🔵 {n})

## Findings
[One line per finding, grouped by check number]

## Summary
| Category | 🔴 | 🟡 | 🔵 |
|----------|-----|-----|-----|
| Structural Integrity (1-6) | n | n | n |
| Content Quality (7-9) | n | n | n |
| Solutions Repo (10-18) | n | n | n |
```

</instructions>
