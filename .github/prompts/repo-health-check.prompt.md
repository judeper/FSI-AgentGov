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

Run all validation scripts from the repo root. Report a pass/fail table. Show output ONLY for failures.

1. `mkdocs build --strict`
2. `python scripts/verify_controls.py`
3. `python scripts/verify_templates.py`
4. `python scripts/verify_excel_templates.py`
5. `python scripts/verify_language_rules.py`
6. `python scripts/validate_docs_anchors.py`
7. *(If Solutions repo available)* Parse every `.json` under `SOLUTIONS_REPO/*/src/` with `json.loads()` — report failures only

**These scripts are authoritative.** Do NOT re-check their domains in Phase 2 (prohibited language, control section structure, footer format, anchor links).

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
| Script | Result |
|--------|--------|
| mkdocs build --strict | PASS/FAIL |
| ... | ... |
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
