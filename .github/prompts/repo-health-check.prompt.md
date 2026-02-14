---
name: "repo-health-check"
description: "Run comprehensive health check across FSI-AgentGov and FSI-AgentGov-Solutions"
tools: ["read", "search", "execute", "agent"]
---

<objective>
Run a 5-part repository health check validating structural integrity, content quality, solution completeness, build validation, and reference accuracy across both FSI-AgentGov and FSI-AgentGov-Solutions repositories. Report issues only — skip checks that pass.
</objective>

<instructions>

## Overview

This prompt runs a comprehensive pre-release validation suite. Execute all 5 checks sequentially and produce a consolidated issue report at the end.

**Both repos must be available locally:**
- FSI-AgentGov (documentation repo)
- FSI-AgentGov-Solutions (solutions repo — sibling directory)

---

## Check 1: Structural Integrity & Cross-Reference Validation

Verify the structural completeness of both repositories:

1. **Solution folder completeness (Solutions repo):** Every solution folder MUST contain README.md and CHANGELOG.md plus a src/ directory. List any solution missing files.

2. **CONTROL-INDEX.md solution coverage:** For every solution in solutions-index.md, check if its related controls are linked in CONTROL-INDEX.md's Implementation column. List solutions with no CONTROL-INDEX entry.

3. **mkdocs.yml nav integrity:** Verify every file path in mkdocs.yml nav: section actually exists on disk. List any broken nav entries.

4. **Orphaned docs:** Find any .md files under docs/ that are NOT referenced in mkdocs.yml nav. Exclude docs/templates/ and docs/images/.

5. **Control cross-references:** For each control file, verify that files referenced in "Related Controls" tables actually exist at the linked paths. List broken cross-references.

6. **Playbook completeness:** Verify all 71 controls have their 4 required playbooks in docs/playbooks/control-implementations/{id}/: portal-walkthrough.md, powershell-setup.md, verification-testing.md, troubleshooting.md. List any missing.

7. **Solutions-index to Solutions-repo alignment:** Every solution in solutions-index.md with status "Completed" or "Validated" must have a matching folder in FSI-AgentGov-Solutions. List mismatches.

8. **Advanced implementation playbook links:** Every solution that has a "Framework Playbook" link in solutions-index.md — verify that playbook file exists in FSI-AgentGov. List broken links.

---

## Check 2: Content Quality & Language Compliance

Audit all documentation content for compliance violations and staleness:

1. **Prohibited language scan:** Search ALL .md files in docs/ for these exact prohibited phrases (case-insensitive): "ensures compliance", "guarantees", "will prevent", "eliminates risk", "eliminates the need for". List every occurrence with file path and line number.

2. **Placeholder/TODO markers:** Search all .md files in docs/ for: TODO, FIXME, PLACEHOLDER, TBD, [TBD], [TODO], "your-org", "contoso", "<your-", "[your-". List every occurrence with file path and line.

3. **Version consistency:** Check footer metadata in all control files (docs/controls/**/*.md). Every control should have a footer matching: *Updated: {Month} {Year} | Version: v{X.X} | UI Verification Status: {Current/Needs Review}*. List controls with missing/malformed footers or versions older than v1.2.

4. **Stale version references in docs/reference/:** Check all files in docs/reference/ for version numbers. Flag any file with a version older than v1.2.43 in its footer or header.

5. **Empty or stub sections:** In all control files, check if any of the 10 required sections contain fewer than 20 characters of content. List any suspiciously short sections.

6. **Role naming consistency:** Search control files for non-canonical role names: "Global Administrator" (should be "Entra Global Admin"), "Compliance Administrator" (should be "Purview Compliance Admin"), "Power Apps Admin" (should be "Power Platform Admin"), "Exchange Administrator" (should be "Exchange Online Admin"). List violations.

---

## Check 3: Solutions Repo Technical Validation

Validate all solution artifacts in FSI-AgentGov-Solutions:

1. **JSON validity:** For every .json file under */src/, verify it is valid JSON (parseable without errors). List any files that fail to parse.

2. **README consistency:** For every solution README.md, verify it contains: a version number, a "Related Controls" table, a "Components" section listing files in src/, a "Prerequisites" section, and a "Deployment" or "License" section. List READMEs missing any of these.

3. **CHANGELOG completeness:** For every solution CHANGELOG.md, verify it has at least one version entry with a date. List any empty or malformed changelogs.

4. **Component manifest accuracy:** For every solution README.md that lists component files, verify each listed file actually exists in the src/ directory. List phantom files (listed but missing) or unlisted files (exist but not documented).

5. **Cross-repo URL validation:** Search all .md and .json files for URLs containing "github.io/FSI-AgentGov/" or "github.com/judeper/FSI-AgentGov". Extract the path portion and verify it matches an actual page/file in FSI-AgentGov. List broken documentation URLs.

6. **Adaptive card template variables:** For every adaptive-card-*.json file, check the "actions" section for URLs. Flag any URL containing placeholder patterns ("your-org", "contoso", "[org]", "<your-") — these are expected in template files but should be documented, not accidentally left from copy errors.

7. **Solution naming consistency:** Every solution folder name should be kebab-case and match the anchor used in FSI-AgentGov's solutions-index.md. List any mismatches.

---

## Check 4: Build & Script Validation

Run all existing validation scripts and report failures only:

1. `python -m mkdocs build --strict` — must produce zero errors and zero warnings
2. `python scripts/verify_controls.py` — all 71 controls must pass
3. `python scripts/verify_templates.py` — all templates must pass
4. `python scripts/verify_excel_templates.py` — all Excel templates must pass
5. `python scripts/verify_language_rules.py` — no prohibited phrases
6. `python scripts/validate_docs_anchors.py` — no broken anchor links
7. For every .json file under FSI-AgentGov-Solutions/*/src/, parse with Python json.loads() and report failures

Report PASS or FAIL for each. Show detailed output ONLY for failures.

---

## Check 5: Microsoft Learn Link & Terminology Validation

Validate external references and terminology currency:

1. **Microsoft Learn URL check:** Extract ALL unique URLs matching "learn.microsoft.com" from docs/**/*.md. Fetch each URL and check if it returns HTTP 200 or redirects. List any URLs that return 404 or redirect permanently to a different page.

2. **Deprecated Microsoft terminology:** Search docs/ for outdated terms:
   - "Azure Active Directory" or "Azure AD" (should be "Microsoft Entra ID" unless quoting existing UI labels)
   - "Office 365" (should be "Microsoft 365" unless quoting a specific product name)
   - "Power Apps portal" (should be "Power Pages")
   - "Common Data Service" or "CDS" (should be "Dataverse")
   List occurrences with file and line.

3. **Regulatory citation specificity:** Search all control files for regulatory references (FINRA, SEC, SOX, GLBA, OCC, CFTC). Verify they use specific rule/section numbers (e.g., "FINRA Rule 4511(a)" not just "FINRA"). List any vague regulatory references without specific rule numbers.

---

## Output Format

Produce a consolidated report:

```
# Repository Health Check Report
**Date:** {date}
**FSI-AgentGov version:** {version from CHANGELOG}
**Issues found:** {total count}

## Critical Issues (must fix before release)
{issues that break builds, have missing files, or have broken links}

## High Issues (should fix before release)
{content quality issues, stale versions, terminology problems}

## Low Issues (fix when convenient)
{minor formatting, placeholder text in templates, etc.}

## Summary
| Check | Status | Issues |
|-------|--------|--------|
| 1. Structural Integrity | PASS/FAIL | {count} |
| 2. Content Quality | PASS/FAIL | {count} |
| 3. Solutions Validation | PASS/FAIL | {count} |
| 4. Build Validation | PASS/FAIL | {count} |
| 5. Learn Links & Terminology | PASS/FAIL | {count} |
```

</instructions>
