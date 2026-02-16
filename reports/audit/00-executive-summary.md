# FSI-AgentGov Audit — Executive Summary

**Date:** 2026-02-14
**Scope:** FSI-AgentGov (docs) + FSI-AgentGov-Solutions (25 solutions)
**Method:** Parallel sub-agent architecture — 7 batches, 4 agents each, read-based review

---

## Overall Assessment: ⚠️ SIGNIFICANT REMEDIATION REQUIRED

The documentation framework is **structurally sound** — all 71 controls follow the 10-section template, 284 playbooks exist, mkdocs builds cleanly, and no prohibited language was detected across 552 markdown files. However, the solutions repo contains **17 Critical defects** that would cause runtime failures, data loss, or security exposure in production FSI environments.

## Key Metrics

| Category | Items Reviewed | Findings |
|----------|---------------|----------|
| Learn Validations | 31 claims deeply verified | 15 Contradicted, 4 Not Found, 3 Partially Verified, 9 Verified |
| Technical Findings | 25 solution packages | 17 Critical, 3 High |
| Documentation Findings | 71 controls + 34 framework/ref docs | 17 Incorrect, 7 Missing, 6 Ambiguity, 5 Gap, 1 Language |
| Baseline Validation | 4 scripts | 3 Pass, 1 Fail (Excel LFS) |

## Top 5 Critical Issues (P0 — Fix Immediately)

1. **ACM (formerly ALCA): PowerShell 7 + PS 5.1-only module** — `#Requires -Version 7.2` combined with `Microsoft.PowerApps.Administration.PowerShell` (PS 5.1 only). Scripts cannot execute. *[Enable-AuditLogging.ps1]*

2. **SSC: Schema deployment crashes every run** — `create_schema()` returns `None`; caller dereferences `result["errors"]`. Zone option sets use 0-3 vs PowerShell's 100000001-3, causing all queries to return empty. *[create_dataverse_schema.py + PS scripts]*

3. **DR Testing: Production recovery is empty** — Recovery steps only execute inside `if ($DryRun)` blocks. Production mode performs zero recovery, then reports PASS. *[Invoke-DRTest.ps1]*

4. **Control 2.12: GA claim for Preview feature** — Claims "Entra Agent ID and CA for agents are GA" — still Preview per Microsoft Learn. FSI customers may deploy based on false GA status. *[2.12-agent-identity-and-lifecycle.md]*

5. **Control 3.11: Fabricated certification** — References non-existent "AB-900: Microsoft AI and Automation Fundamentals" certification code. *[3.11-centralized-agent-inventory-enforcement.md]*

## Systemic Issues (Cross-Cutting)

| Issue | Solutions Affected | Risk |
|-------|-------------------|------|
| No Dataverse pagination (>5000 record loss) | ELM, ACM, FUS, SSC, AAM, HT, RAG, Dashboard | Data integrity |
| `--client-secret` as CLI argument | 6+ solutions | Secret exposure |
| No Graph API retry/backoff | CAA, DECR, FUS, SSC | Throttling failures |
| Option set value mismatch (Python vs PS) | FUS, SSC | Zero query results |
| Stale control counts (62 or 64 vs 71) | Dashboard, exec-summary, governance-fundamentals, solutions-index | Misleading metrics |

## Remediation Priority

| Priority | Count | Description |
|----------|-------|-------------|
| **P0** | 12 | Runtime crashes, data loss, security exposure — fix before any customer deployment |
| **P1** | 18 | Incorrect Learn claims, stale data, broken features — fix within next release |
| **P2** | 57 | Role naming, formatting, minor doc quality — batch into maintenance sprint |

## Recommendation

**Do not ship solutions to FSI customers** until all P0 items are resolved. The documentation framework is production-quality but needs the 7 new controls (1.25-1.28, 2.22-2.24, 3.11-3.12) reflected in license-requirements.md and executive-summary.md control counts. The solutions repo requires significant engineering work on authentication flows, pagination, error handling, and option set alignment before it meets FSI operational standards.
