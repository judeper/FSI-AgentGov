# ACM Deep Audit — Remediation Backlog

**Audit Date:** 2026-02-16
**Total Findings:** 166 (15 P0, 76 P1, 75 P2)
**Solution:** Audit Compliance Manager (ACM) v1.0.0

---

## P0 — Critical (15 findings — Fix Immediately)

| # | Category | File | Description | Owner | Difficulty |
|---|----------|------|-------------|-------|------------|
| 1 | PS Version | AuditComplianceHelpers.psm1 | `#Requires -Version 7.2` but callers declare 5.1 — module won't load | Engineering | Easy |
| 2 | PS Version | Connect-PowerPlatform.ps1 | `#Requires -Version 7.0` incompatible with PS 5.1 target | Engineering | Easy |
| 3 | PS Version | Check-AuditLoggingCompliance.ps1 | `Get-Date -AsUTC` (PS 7.1+) in script declaring 5.1 | Engineering | Easy |
| 4 | PS Version | Test-*.ps1 (all 5) | All require PS 7.0+ — systemic conflict (counted as 1 item, 5 files) | Engineering | Easy |
| 5 | Pagination | acv_client.py `query()` | No `@odata.nextLink` handling — >5000 records silently dropped | Engineering | Medium |
| 6 | Pagination | alca_client.py `query()` | Same pagination gap | Engineering | Medium |
| 7 | Retry | alca_client.py | PUT in retry methods + POST retries create duplicates | Engineering | Easy |
| 8 | Docs | DELIVERY-CHECKLIST.md | Entirely stale ALCA branding, wrong paths, excludes ACV deliverables | Docs | High |
| 9 | Docs | README.md Quick Start | References 2 non-existent Python scripts | Docs | Easy |
| 10 | Metadata | AuditComplianceHelpers.psd1 | ProjectUri/LicenseUri point to wrong GitHub org | Engineering | Easy |
| 11 | Security | Connect-PowerPlatform.ps1 | SecureString double-converted to plaintext for MSAL | Engineering | Medium |

**Acceptance Criteria:** All `#Requires` aligned to 7.2; pagination added; retry methods corrected; DELIVERY-CHECKLIST rewritten; README Quick Start fixed; PSD1 URIs updated; SecureString handling fixed.

---

## P1 — High (76 findings — Fix Before Next Release)

### Scripts (grouped by theme)

| Theme | Count | Key Files | Action |
|-------|-------|-----------|--------|
| Export-ModuleMember in .ps1 | 7 | All private/ scripts + Invoke-EnvironmentDiscovery | Remove all instances |
| Missing Pester tests | 5 | Test-*.ps1 (5 validators with zero coverage) | Create .Tests.ps1 for each |
| Duplicate param() blocks | 3 | Test-EnvironmentAudit, Test-EnvironmentRetention, Connect-PowerPlatform | Remove script-level params |
| Non-existent cmdlet | 1 | Check-AuditLoggingCompliance — `Get-AdminConfig` | Use BAP API or Get-AdminPowerAppEnvironment |
| Unfiltered audit search | 1 | Check-AuditLoggingCompliance — tenant-wide Search-UnifiedAuditLog | Add env filter |
| Missing pagination | 3 | Invoke-EnvironmentDiscovery (2), Invoke-EnvironmentAuditValidation (1) | Add @odata.nextLink |
| Race conditions | 2 | AuditComplianceHelpers upsert, Invoke-EnvironmentAuditValidation registry | Use Dataverse alternate key upsert |
| Auth gaps | 2 | Connect-AuditServices (no MI), Start-TenantValidationRunbook (no secret) | Add missing auth paths |
| Evidence integrity | 3 | UTF-8 BOM chain: Export encoding + Test version mismatch + hash parsing | Standardize to utf8NoBOM, align PS versions |
| Wrong entity | 1 | Enable-AuditLogging — `systemuser` in Copilot Studio list | Replace with correct entity |
| Property mismatch | 1 | Discovery outputs DisplayName, orchestrator reads EnvironmentName | Standardize |
| Code duplication | 1 | acv_client.py + alca_client.py nearly identical | Merge with inheritance |
| Vulnerable dep | 1 | requirements.txt — requests CVE-2024-47081 | Pin >=2.32.4 |
| OptionSet numbering | 1 | create_dataverse_schema.py — values 1-5 instead of 100000000+ | Renumber |
| Canary cleanup | 1 | New-CanaryEvent — $null throws on Set-Mailbox | Use empty string |
| Various | 7+ | Module state, test coverage, parameter issues | See technical findings |

### Documentation (grouped by theme)

| Theme | Count | Key Files | Action |
|-------|-------|-----------|--------|
| Stale `src/` paths | 3 | SOLUTION-DOCUMENTATION, FLOW_SETUP, deployment-guide | Replace with scripts/templates |
| Stale solution names | 2 | SOLUTION-DOCUMENTATION (ALCA only), FLOW_SETUP (ACV only) | Update to ACM |
| Broken doc links | 1 | FLOW_SETUP — 4 non-existent referenced docs | Create or redirect |
| Missing components | 1 | README — 8 scripts missing from Components table | Add entries |
| Stale audit reports | 6 | reports/audit/ 00, 01, 02, 04, 06, 07 — use ALCA/ACV as current names | Update to ACM |
| FSI language | 1 | DELIVERY-CHECKLIST — "Ensure" overclaim | Change to "Support" |
| Trilateral mismatch | 2 | solutions-index vs SOLUTION-DOCUMENTATION vs README test counts | Reconcile |
| solutions-integration | 1 | Mermaid diagram says 24 solutions, should be 27 | Update |

---

## P2 — Medium (75 findings — Improve When Convenient)

Major themes:
- **Stale doc titles** (5 files): evidence-export-guide, scheduling-guide, testing-scenarios, deployment-guide, DELIVERY-CHECKLIST package name
- **Role naming** (2 files): FLOW_SETUP, deployment-guide — non-canonical names
- **Code quality** (12 items): Array growth O(n²), fragile regex, hardcoded values, inconsistent casing, missing edge case tests
- **Framework docs** (4 items): Regulatory subsection refs, redundant header field, solutions-integration listing gaps
- **Python** (7 items): Environment variable type mapping, non-atomic two-step create, None-return pattern, missing CLI entry point, unused requirements, dry-run inconsistency, dynamic argparse `required`

---

## Prioritized Action Plan

### Wave 1 — Immediate (addresses all P0s)

1. Align all PS scripts to `#Requires -Version 7.2`
2. Add Dataverse pagination to Python client `query()` methods
3. Remove POST/PUT from retry `allowed_methods`
4. Rewrite DELIVERY-CHECKLIST.md for ACM
5. Fix README Quick Start script references
6. Update PSD1 URIs
7. Fix SecureString handling in Connect-PowerPlatform

### Wave 2 — Next Release (high-impact P1s)

1. Remove all `Export-ModuleMember` from .ps1 files (7 files)
2. Fix `Get-AdminConfig` non-existent cmdlet
3. Add Dataverse pagination to 3 PS scripts
4. Add MI support to Connect-AuditServices
5. Fix evidence integrity chain (UTF-8 BOM)
6. Fix property name mismatch (DisplayName → EnvironmentName)
7. Update all stale `src/` paths in docs
8. Pin `requests>=2.32.4`
9. Update stale ALCA/ACV references in audit reports

### Wave 3 — Planned (remaining P1s + priority P2s)

1. Create Pester tests for 5 validator scripts
2. Replace `systemuser` with correct Copilot Studio entity
3. Merge Python clients into single class
4. Fix upsert race conditions (use alternate key)
5. Update stale solution names in doc titles
6. Reconcile test count across docs
7. Fix role naming inconsistencies

---

*Report: acm-audit-remediation-backlog.md | Generated: 2026-02-16*
