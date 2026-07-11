---
name: "repo-health-check"
description: "Run full health check suite (all 3 phases in one shot) — or use individual prompts: scripts → analysis → references"
tools: ["read", "search", "execute", "agent"]
---

<objective>
Run a 3-phase repository health check: automated scripts, structural/content analysis, and external reference validation. This orchestrator runs all three phases sequentially in a single session. For targeted checks, use the individual prompts instead: `/repo-health-check-scripts`, `/repo-health-check-analysis`, `/repo-health-check-references`.
</objective>

<instructions>

## Output Rules (READ FIRST — critical for context efficiency)

**Be maximally concise to preserve context window:**
- One line per finding: `🔴|🟡|🔵 file:line — description`
- No preamble, no "all clear" messages, no explanations for obvious issues
- Skip any check that finds zero issues — do not mention it
- NEVER echo file contents — just cite path and line number
- Do not exceed 200 lines of total output across all phases

**Severity markers:**
- 🔴 **CRITICAL** — Breaks build, missing files, broken links
- 🟡 **HIGH** — Content quality, stale versions, incorrect terminology
- 🔵 **LOW** — Minor formatting, cosmetic consistency

## Dynamic Values — Derive, Do Not Hardcode

- **CURRENT_VERSION:** Read from the latest entry in `CHANGELOG.md`
- **CONTROL_LIST:** Read from `docs/controls/CONTROL-INDEX.md` (do not assume a fixed count)
- **SOLUTIONS_REPO:** Look for sibling directory `FSI-AgentGov-Solutions` (if not found, skip cross-repo checks)

---

## Phase 1: Script Validation (fastest — run first)

Run workflow-aligned validation from the repo root. Treat these files as command sources:

- `.github/workflows/docs-validation.yml`
- `.github/workflows/python-quality.yml`
- `.github/workflows/commercial-scope.yml`

Build a dynamic command plan (no fixed script list), then execute applicable gates in this order:

1. Determine changed paths from `git diff --name-only`.
2. Build site first: `mkdocs build --strict`
3. Run built-site gates with current args:
   - `python scripts/verify_build_output.py site`
   - `python scripts/verify_meta_tags.py site/`
   - `python scripts/verify_doc_links.py site --json _broken-links.json`
4. Run current documentation/drift gates when applicable:
   - `python scripts/verify_controls.py`
   - `python scripts/verify_xref_graph.py`
   - `python scripts/check_manifest_doc_drift.py --check`
   - `python scripts/check_explorer_data_drift.py --check`
   - `python scripts/check_change_radar_data_drift.py --check`
   - `python scripts/check_faq_jsonld_drift.py --check`
   - `python scripts/generate_coverage_matrix.py --check`
   - `python scripts/verify_language_rules.py`
   - `python scripts/verify_commercial_scope.py`
   - `python scripts/verify_learn_urls_count.py --check`
   - `python scripts/verify_version_stamps.py --check`
   - `python scripts/verify_prose_counts.py --check`
   - `python scripts/verify_solutions_docs.py --check`
   - `python scripts/verify_regulatory_naming.py --check`
5. Run code/test gates only when relevant files changed:
   - `ruff check assessment scripts`
   - `pytest assessment/tests -v`
   - `pytest scripts -v -p no:cacheprovider --ignore=scripts/private --ignore=scripts/governance -k "test_"`
6. Keep these conditional and mark as **supplemental (non-authoritative CI gates)**:
   - `python scripts/verify_templates.py`
   - `python scripts/verify_excel_templates.py`
   - `python scripts/compile_researcher_package.py`
   - `python scripts/validate_docs_anchors.py`
7. *(If Solutions repo available)* Conditionally parse `.json` under `SOLUTIONS_REPO/*/src/` with `json.loads()` and report parse failures.

**These workflow-derived gates are authoritative.** Do NOT duplicate their domains in Phase 2 (language rules, control structure, built-site link/anchor validation, drift checks).

---

## Phase 2: Structural & Content Analysis (checks scripts can't do)

### Structural Integrity

1. **mkdocs.yml nav integrity:** Verify every file path in `mkdocs.yml` nav exists on disk. List broken entries.
2. **Orphaned docs:** Find `.md` files under `docs/` not in `mkdocs.yml` nav. Exclude `docs/templates/`, `docs/images/`, and `index.md` directory indices.
3. **Control cross-references:** In each control's "Related Controls" table, verify linked paths exist.
4. **Playbook completeness:** For every control in `CONTROL-INDEX.md`, verify 4 playbooks exist: `portal-walkthrough.md`, `powershell-setup.md`, `verification-testing.md`, `troubleshooting.md`.
5. **Playbook stub detection:** Flag playbooks with fewer than 100 characters or no numbered/bulleted steps.
6. **Nav ordering:** Verify controls appear in numerical order within each pillar section in `mkdocs.yml`.

### Content Quality

7. **Placeholder/TODO markers:** Search `docs/**/*.md` for: TODO, FIXME, PLACEHOLDER, TBD, [TBD], [TODO], "your-org", "contoso", `<your-`, `[your-`.
8. **Version staleness:** Flag `docs/reference/*.md` files with version numbers older than `CURRENT_VERSION`.
9. **CHANGELOG-mkdocs version alignment:** Verify the latest `CHANGELOG.md` version matches any version reference in `mkdocs.yml`.

### Solutions Repo (skip if unavailable)

10. **Solution folder completeness:** Must contain `README.md`, `CHANGELOG.md`, and either `src/` or `docs/` directory.
11. **CONTROL-INDEX solution coverage:** Verify solutions in `solutions-index.md` are linked in `CONTROL-INDEX.md`.
12. **Solutions-index alignment:** "Completed"/"Validated" solutions must have matching folders.
13. **Solution README completeness:** Must have version, related controls, component listing, prerequisites, deployment instructions.
14. **Component manifest accuracy:** Verify listed files exist; flag unlisted files.
15. **Cross-repo URL validation:** Verify FSI-AgentGov URLs in solution files point to existing targets.
16. **Adaptive card placeholders:** Flag undocumented placeholder patterns in action URLs.
17. **Solution naming consistency:** Kebab-case folder names matching `solutions-index.md` anchors.
18. **Advanced implementation playbook links:** Verify "Framework Playbook" links exist.

---

## Phase 3: External References (requires web access)

**If web access is unavailable, skip Phase 3 and note: "Phase 3 skipped — no web access."**

1. **Microsoft Learn URLs:** Fetch unique `learn.microsoft.com` URLs from `docs/**/*.md`. Report only 404s and permanent redirects.
2. **Deprecated terminology:** Flag "Azure AD", "Office 365", "Power Apps portal", "CDS" outside code blocks.
3. **Regulatory citation specificity:** Flag vague regulatory references without specific rule/section numbers.

---

## Final Report Format

```
# Repository Health Check Report
**Date:** {date}
**Version:** {CURRENT_VERSION}
**Issues:** {total} (🔴 {n} critical, 🟡 {n} high, 🔵 {n} low)

## Phase 1: Script Validation
| Source Workflow | Gate | Command | Condition | Result |
|-----------------|------|---------|-----------|--------|
| docs-validation.yml | mkdocs-strict | mkdocs build --strict | always | PASS/FAIL |
| ... | ... | ... | ... | ... |
[Failure details only]

## Phase 2: Structural & Content
[One line per finding]

## Phase 3: External References
[One line per finding, or "Skipped"]

## Summary
| Phase | 🔴 | 🟡 | 🔵 |
|-------|-----|-----|-----|
| 1. Scripts | n | n | n |
| 2. Analysis | n | n | n |
| 3. References | n | n | n |
```

</instructions>
