# Codebase Analysis: Concerns

**Generated:** 2026-02-11
**Scope:** Full repository concerns and technical debt analysis

## Summary

The repository is in a healthy post-remediation state - v11 addressed 107 findings and both mkdocs build --strict and verify_controls.py pass. However, residual consistency issues remain: "Azure AD" and "Tier" terminology drift persists in ~20+ locations, solution status metadata is stale in solutions-integration.md vs solutions-index.md, and 5 documents link to files excluded from the published site (producing dead links for users).

## Active Issues

**User-facing broken links (5 docs link to excluded files):**
- Control 1.7 -> reference/regulatory-mappings.md (excluded)
- quick-start.md -> controls/CONTROL-INDEX.md (excluded)
- faq.md -> controls/CONTROL-INDEX.md (excluded)
- nist-ai-rmf-crosswalk.md -> regulatory-mappings.md (excluded)
- solutions-coverage-gaps.md -> controls/CONTROL-INDEX.md (excluded)

## Technical Debt

| Item | Severity |
|------|----------|
| Pseudocode cmdlets in promotion gates playbooks (6+ instances) | Medium |
| Links to exclude_docs files produce dead links | Medium |
| REQUIREMENTS.md checkboxes all unchecked despite delivery | Low |
| Stale output files in repo root (verify_output.txt, build_*.txt) | Low |
| Control 1.6 PowerShell "Placeholder for future API" comment | Low |

## Consistency Issues

| Pattern | Remaining Instances |
|---------|-------------------|
| "Azure AD" vs "Microsoft Entra ID" | 10+ files (portal-paths, script-validation, 2.15, 2.14, 1.8, 1.18) |
| "Tier 1/2/3" vs "Zone 1/2/3" | 10+ files (solutions-index, solutions-coverage-gaps, 1.8, 4.1, 3.2) |
| "Level" terminology | 3 instances (governance-fundamentals, 2.17) |
| Solution status drift | solutions-integration.md vs solutions-index.md (CAA, Scope Drift Monitor, DEC) |

## Stale Content

- solutions-integration.md: CAA listed as WIP/v1.0.0 vs Completed/v1.1.0 in solutions-index.md
- Root output files: verify_output.txt, build_output.txt, build_out2.txt, build_err.txt, etc.
- Preview feature dates (3.8, 3.1, 1.5) need periodic validation

## Documentation Gaps

- 10 controls missing docs/images/{id}/ directories (1.22-1.24, 2.17-2.21, 3.10, 4.7)
- No external link validation for 456+ Microsoft Learn URLs
- regulatory-mappings.md excluded from nav but linked from 2 docs
- CONTROL-INDEX.md excluded from nav but linked from 3 docs

## Risk Areas

| Area | Risk | Likelihood |
|------|------|------------|
| Excluded-file links (user gets 404) | User-facing broken links | HIGH |
| Preview feature changes break portal paths | Outdated instructions | HIGH |
| Solution status confusion (2 pages disagree) | Reader confusion | MEDIUM |
| Pseudocode cmdlets executed as real scripts | Admin errors | MEDIUM |
| Azure AD terminology in portal paths | Outdated navigation | MEDIUM |

## Prioritized Recommendations

**P1 - User-Facing (High Impact, Low Effort):**
1. Fix 5 docs linking to excluded files (add to nav or update links)

**P2 - Consistency (Medium Impact, Medium Effort):**
2. Complete Azure AD -> Microsoft Entra ID rename (10+ remaining instances)
3. Complete Tier -> Zone normalization (10+ remaining instances)
4. Sync solutions-integration.md statuses with solutions-index.md

**P3 - Housekeeping (Low Impact, Low Effort):**
5. Add root output files to .gitignore or delete them
6. Create missing docs/images/{id}/EXPECTED.md for 10 controls
7. Update REQUIREMENTS.md checkboxes to checked

**P4 - Ongoing Maintenance:**
8. Quarterly review of preview feature status boxes
9. Implement automated external link checking for Learn URLs
10. Review pseudocode cmdlets when Microsoft ships agent management APIs
