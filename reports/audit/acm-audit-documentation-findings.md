# ACM Deep Audit — Documentation Findings

**Audit Date:** 2026-02-16
**Solution:** Audit Compliance Manager (ACM) v1.0.0
**Scope:** 16 solution docs/templates (FSI-AgentGov-Solutions) + 9 framework docs (FSI-AgentGov)

---

## Root Cause: Incomplete Post-Merger Cleanup

The ACV and ALCA solutions were physically consolidated into `audit-compliance-manager/` but documentation was largely carried over verbatim. This accounts for ~60% of documentation findings.

---

## P0 — Critical

### DOC-1: DELIVERY-CHECKLIST.md is entirely stale

- **File:** `audit-compliance-manager/DELIVERY-CHECKLIST.md`
- **Issue:** Still titled "ALCA Solution - Customer Delivery Checklist". Excludes all ACV deliverables (14+ scripts). Uses old folder name `audit-logging-compliance-automation` in ZIP command. All file paths use `src/` prefix (actual: `scripts/` and `templates/`). Footer says "Solution: Audit Logging Compliance Automation (ALCA)".
- **Fix:** Complete rewrite as "ACM — Customer Delivery Checklist" covering all ACV + ALCA components.

### DOC-2: README.md references non-existent Python scripts

- **File:** `audit-compliance-manager/README.md` — Quick Start Step 4
- **Issue:** References `python scripts/discover_environments.py` and `python scripts/validate_environments.py` — neither exists. Actual equivalents are PowerShell scripts.
- **Fix:** Replace with `Invoke-EnvironmentDiscovery.ps1` and `Invoke-EnvironmentAuditValidation.ps1`.

---

## P1 — High

### Stale Path References (`src/` → `scripts/`/`templates/`)

| # | File | Occurrences | Fix |
|---|------|-------------|-----|
| DOC-3 | SOLUTION-DOCUMENTATION.md | ~7 locations | Global replace `src/` → `scripts/`/`templates/` |
| DOC-4 | docs/FLOW_SETUP.md | Sections 2.1, 2.3, 2.4 | Replace `src/` → `templates/` |
| DOC-5 | docs/deployment-guide.md | Phase 5 Steps 5.1-5.2 | Replace `src/` → `scripts/` |

### Stale Solution Names

| # | File | Issue | Fix |
|---|------|-------|-----|
| DOC-6 | SOLUTION-DOCUMENTATION.md | Titled "ALCA" — covers only ALCA half of ACM | Expand to cover full ACM or rename as component doc |
| DOC-7 | docs/FLOW_SETUP.md | Title/footer say "Audit Configuration Validator" | Update to "Audit Compliance Manager" |
| DOC-8 | docs/FLOW_SETUP.md | Links to 4 non-existent docs (AUTHENTICATION.md, DATAVERSE_DEPLOYMENT.md, RUNBOOK_REFERENCE.md, TROUBLESHOOTING.md) | Create or redirect to existing docs |

### Completeness Issues

| # | File | Issue | Fix |
|---|------|-------|-----|
| DOC-9 | README.md | Components table missing 8 scripts (all private/ files + 2 Test-*.ps1) | Add missing entries |
| DOC-10 | Cross-reference | solutions-index says "29 test cases"; ALCA changelog says "15+ test scenarios" — unreconciled | Verify actual count, standardize |
| DOC-11 | Cross-reference | SOLUTION-DOCUMENTATION covers only ALCA; solutions-index describes unified ACM — trilateral inconsistency | See DOC-6 |

### FSI Language

| # | File | Issue | Fix |
|---|------|-------|-----|
| DOC-12 | DELIVERY-CHECKLIST.md | "Ensure continuous audit coverage" — "Ensure" implies guarantee | Change to "Support continuous audit coverage" |

### Stale References in Audit Reports

| # | File | Issue | Fix |
|---|------|-------|-----|
| DOC-13 | reports/audit/01-repo-map.md | Lines 73-74: old `audit-configuration-validator/` and `audit-logging-compliance-automation/` folder names | Merge into single `audit-compliance-manager/` entry |
| DOC-14 | reports/audit/02-inventory.md | Lines 77-78: old solution rows | Merge into single ACM row |
| DOC-15 | reports/audit/00-executive-summary.md | Lines 24, 38: uses "ALCA" as current name | ~~Replace with "ACM"~~ **RESOLVED** — already reads "ACM (formerly ALCA)" on line 24 and "ACM" on line 38 |
| DOC-16 | reports/audit/04-technical-findings.md | Lines 17, 27: uses "ALCA" as current name/heading | Replace with "ACM" |
| DOC-17 | reports/audit/06-remediation-backlog.md | Lines 33, 121: uses "ALCA" as current name | Replace with "ACM" |
| DOC-18 | reports/audit/07-post-remediation-review.md | Line 39: uses "ALCA" as current name | Replace with "ACM" |

---

## P2 — Medium

### Solution Doc Titles (Stale Names)

| # | File | Current Title | Fix |
|---|------|---------------|-----|
| DOC-19 | docs/evidence-export-guide.md | "Audit Configuration Validator" | Update to "Audit Compliance Manager" |
| DOC-20 | docs/scheduling-guide.md | "ALCA" | Update to "ACM (ALCA Component)" |
| DOC-21 | docs/testing-scenarios.md | "ALCA" | Update to "ACM (ALCA Component)" |
| DOC-22 | docs/deployment-guide.md | "ALCA" | Update to "ACM (ALCA Component)" |

### Role Naming

| # | File | Issue | Fix |
|---|------|-------|-----|
| DOC-23 | docs/FLOW_SETUP.md | "Exchange Online admin role" (lowercase, appended "role") | Use "Exchange Online Admin" |
| DOC-24 | docs/deployment-guide.md | Mixes "Exchange Online Admin" with "Exchange Administrator" | Standardize to "Exchange Online Admin" |

### Framework Doc Issues

| # | File | Issue | Fix |
|---|------|-------|-----|
| DOC-25 | solutions-integration.md | Mermaid diagram says "24 solutions" but solutions-index lists 27 | Update diagram title and add missing solutions |
| DOC-26 | solutions-integration.md | Repository structure listing shows 19 folders but 27 solutions exist | Update listing |
| DOC-27 | Control 1.7 | Header regulatory ref "FINRA 4511" lacks subsection | Consider "FINRA Rule 4511(a)" |
| DOC-28 | Control 1.7 | Redundant `Last Verified` field alongside `Last UI Verified` | Remove duplicate |
| DOC-29 | powershell-setup.md | Link to `purview-audit-query-pack.md` — verify file exists | Verify path |

---

## Clean Areas (No Issues Found)

- ✅ **Control 1.7:** Full 10-section template compliance, correct header/footer metadata
- ✅ **FSI Language (framework docs):** Zero prohibited phrases across all 9 files
- ✅ **Role Naming (framework docs):** All canonical names correct
- ✅ **Playbook Links:** All 4 playbook paths in Control 1.7 Section 8 are correct
- ✅ **CONTROL-INDEX:** Control 1.7 correctly listed with ACM solution reference
- ✅ **solutions-index ACM entry:** Correct version, status, control mapping, repo link
- ✅ **solutions-integration ACM section:** Correct control mapping, status, capabilities
- ✅ **Regulatory mappings:** Control 1.7 correctly mapped under all applicable regulations
- ✅ **JSON Templates:** All 5 templates well-formed, valid schema, correct connection references
- ✅ **Learn URLs:** All 6 Microsoft Learn URLs valid and returning current content
- ✅ **README FSI Language:** Excellent hedged language throughout

---

*Report: acm-audit-documentation-findings.md | Generated: 2026-02-16*
